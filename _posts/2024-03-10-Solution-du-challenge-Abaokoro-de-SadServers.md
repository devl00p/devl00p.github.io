---
title: "Solution du challenge Abaokoro de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Abaokoro": Restore MySQL Databases Spooked by a Ghost

**Level:** Medium

**Type:** Fix

**Tags:** [mysql](https://sadservers.com/tag/mysql)  

**Description:** There are three databases that need to be restored. You need to create three databases called "first", "second" and "third" and restore the databases using the file `/home/admin/dbs_to_restore.zip`.  
If you encounter an issue while restoring the database, fix it.

Credit: [Sebastian Segovia](https://www.linkedin.com/in/sebastian-segovia-a7518a228/)

**Test:** All databases, once restored, have a table named "foo".

The "Check My Solution" button runs the script `/home/admin/agent/check.sh`, which you can see and execute.

**Time to Solve:** 20 minutes.

Ça commence mal puisque `unzip` n'est pas installé : 

```console
admin@i-0d7f356c863ad6235:~$ ls -al
total 1296
drwxr-xr-x 5 admin admin    4096 Feb 24 18:25 .
drwxr-xr-x 3 root  root     4096 Feb 17 22:46 ..
drwx------ 3 admin admin    4096 Feb 17 22:47 .ansible
-rw-r--r-- 1 admin admin     220 Mar 27  2022 .bash_logout
-rw-r--r-- 1 admin admin    3526 Mar 27  2022 .bashrc
-rw-r--r-- 1 admin admin     807 Mar 27  2022 .profile
drwx------ 2 admin admin    4096 Feb 24 18:26 .ssh
drwxrwxrwx 2 admin admin    4096 Feb 24 18:25 agent
-rw-r--r-- 1 root  root  1292285 Feb 24 18:25 dbs_to_restore.zip
admin@i-0d7f356c863ad6235:~$ unzip -l dbs_to_restore.zip 
bash: unzip: command not found
admin@i-0d7f356c863ad6235:~$ file dbs_to_restore.zip
dbs_to_restore.zip: Zip archive data, at least v2.0 to extract
```

Heureusement Python3 est présent, on va pouvoir se débrouiller :)

Jetons un œil au script qui vérifie la solution :

```bash
#!/bin/bash

# MySQL credentials
MYSQL_USER="root"
DATABASES=("first" "second" "third")
TABLE="foo"

# Initialize a variable to track if the table is found in all databases
table_found=true

for DATABASE in "${DATABASES[@]}"; do
    # Check if the table exists
    if ! sudo mysql -u"$MYSQL_USER" -e "USE $DATABASE; DESCRIBE $TABLE;" &> /dev/null; then
        table_found=false
        break
    fi
done

if $table_found; then
    echo -n "OK"
else
    echo -n "NO"
fi
```

Rien de plus que ce que décrivait l'énoncé.

MariaDB est bien en écoute :

```console
admin@i-0d7f356c863ad6235:~$ ps aux | grep db
message+     607  0.0  0.9   7888  4212 ?        Ss   09:51   0:00 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
mysql        701  0.0 16.2 1543452 75980 ?       Ssl  09:51   0:00 /usr/sbin/mariadbd
admin       1238  0.0  0.1   5264   636 pts/0    S<+  09:56   0:00 grep db
admin@i-0d7f356c863ad6235:~$ sudo ss -lntp
State                Recv-Q                Send-Q                               Local Address:Port                               Peer Address:Port               Process                                           
LISTEN               0                     128                                        0.0.0.0:22                                      0.0.0.0:*                   users:(("sshd",pid=634,fd=3))                    
LISTEN               0                     80                                       127.0.0.1:3306                                    0.0.0.0:*                   users:(("mariadbd",pid=701,fd=19))               
LISTEN               0                     4096                                             *:6767                                          *:*                   users:(("sadagent",pid=602,fd=7))                
LISTEN               0                     4096                                             *:8080                                          *:*                   users:(("gotty",pid=601,fd=6))                   
LISTEN               0                     128                                           [::]:22                                         [::]:*                   users:(("sshd",pid=634,fd=4))
```

En revanche, on ne dispose pas du mot de passe utilisateur :

```console
admin@i-0d7f356c863ad6235:~$ mysql -u root
ERROR 1698 (28000): Access denied for user 'root'@'localhost'
```

On verra ça plus tard. Tentons déjà d'extraire les backups SQL. Il y a cette ligne de commande Python qui se substitue à `unzip` :

```console
admin@i-0d7f356c863ad6235:~$ python3 -m zipfile -e dbs_to_restore.zip backups
Traceback (most recent call last):
  File "/usr/lib/python3.9/runpy.py", line 197, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/lib/python3.9/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/usr/lib/python3.9/zipfile.py", line 2428, in <module>
    main()
  File "/usr/lib/python3.9/zipfile.py", line 2400, in main
    zf.extractall(curdir)
  File "/usr/lib/python3.9/zipfile.py", line 1633, in extractall
    self._extract_member(zipinfo, path, pwd)
  File "/usr/lib/python3.9/zipfile.py", line 1679, in _extract_member
    os.makedirs(upperdirs)
  File "/usr/lib/python3.9/os.py", line 225, in makedirs
    mkdir(name, mode)
OSError: [Errno 122] Disk quota exceeded: 'backups'
```

Allons bon ! Effectivement le disque est monté avec des options de quota.

```
/dev/nvme0n1p1 on / type ext4 (rw,relatime,discard,quota,usrquota,grpquota,errors=remount-ro)
```

Si je liste les quotas pour l'utilisateur `admin`, j'obtiens ceci :

```console
admin@i-0d7f356c863ad6235:~$ sudo quota -u admin
Disk quotas for user admin (uid 1000):
  Filesystem                   blocks       soft       hard     inodes     soft     hard
  /dev/nvme0n1p1              5242880          0    5242880         28  5242880        0
```

Pour `root` c'est différent :

```
Disk quotas for user root (uid 0):
  Filesystem                   blocks       soft       hard     inodes     soft     hard
  /dev/nvme0n1p1              1930652          0          0      40439        0        0
```

J'ai tenté de recopier la ligne de root pour admin. La commande `edquota` exécute l'éditeur par défaut et tente d'appliquer le changement quand on quitte :

```console
root@i-042c0722d08affd59:/home/admin# export EDITOR=vim
root@i-042c0722d08affd59:/home/admin# edquota -u admin
edquota: WARNING - /dev/nvme0n1p1: cannot change current block allocation
edquota: WARNING - /dev/nvme0n1p1: cannot change current inode allocation
```

Il a pu me prendre certains changements, mais pas tous...

Je me suis dit que ce sera plus efficace de remonter le disque sans les quotas :

```console
root@i-042c0722d08affd59:/home/admin# sudo mount -o remount,rw,relatime,discard,errors=remount-ro /dev/nvme0n1p1 /
root@i-042c0722d08affd59:/home/admin# 
exit
admin@i-042c0722d08affd59:~$ mkdir backups
mkdir: cannot create directory ‘backups’: No space left on device
admin@i-042c0722d08affd59:~$ df -h
Filesystem       Size  Used Avail Use% Mounted on
udev             218M     0  218M   0% /dev
tmpfs             46M  372K   46M   1% /run
/dev/nvme0n1p1   7.7G  7.3G     0 100% /
tmpfs            228M     0  228M   0% /dev/shm
tmpfs            5.0M     0  5.0M   0% /run/lock
/dev/nvme0n1p15  124M   11M  114M   9% /boot/efi
```

Cette fois, on manque de place sur le disque. J'ai trouvé rapidement le coupable :

```console
root@i-042c0722d08affd59:/home/admin# du -h --max-depth 1 /var/log  2> /dev/null 
4.0K    /var/log/mysql
4.0K    /var/log/private
36K     /var/log/apt
17M     /var/log/journal
8.0K    /var/log/runit
5.3G    /var/log/custom
4.0K    /var/log/chrony
12K     /var/log/unattended-upgrades
5.3G    /var/log
```

Il faut supprimer le dossier `/var/log/custom`. Si l'on supprime uniquement son contenu, j'ai l'impression que des données reviennent.

On peut désormais décompresser le zip, ce qui donne un fichier `.tar.gz` mais on est vite ramené sur des problèmes d'espace disque : 

```console
admin@i-042c0722d08affd59:~$ ls backups/ -alh
total 33M
drwxr-xr-x 2 admin admin 4.0K Mar 10 12:59 .
drwxr-xr-x 6 admin admin 4.0K Mar 10 12:59 ..
-rw-r--r-- 1 admin admin  33M Mar 10 12:59 dbs_to_restore.tar.gz
admin@i-042c0722d08affd59:~$ cd backups/
admin@i-042c0722d08affd59:~/backups$ tar zxvf dbs_to_restore.tar.gz 
first.sql
tar: first.sql: Cannot write: No space left on device
second.sql
tar: second.sql: Cannot write: No space left on device
third.sql
tar: third.sql: Cannot write: No space left on device
tar: Exiting with failure status due to previous errors
```

Il faut avancer au fur et à mesure : extraire le `.tar.gz`, supprimer le zip puis extraire les fichiers du `.tar.gz` un à un.

Avant ça on va réinitialiser le mot de passe du MariaDB, manipulation déjà décrite sur le challenge _Rosario_.

```console
root@i-0edcee8585bb735a1:/home/admin# /etc/init.d/mariadb stop
Stopping mariadb (via systemctl): mariadb.service.
root@i-0edcee8585bb735a1:/home/admin# df -h
Filesystem       Size  Used Avail Use% Mounted on
udev             218M     0  218M   0% /dev
tmpfs             46M  380K   46M   1% /run
/dev/nvme0n1p1   7.7G  2.0G  5.3G  28% /
tmpfs            228M     0  228M   0% /dev/shm
tmpfs            5.0M     0  5.0M   0% /run/lock
/dev/nvme0n1p15  124M   11M  114M   9% /boot/efi
tmpfs             46M     0   46M   0% /run/user/0
root@i-0edcee8585bb735a1:/home/admin# mysqld_safe --skip-grant-tables &
[1] 1048
root@i-0edcee8585bb735a1:/home/admin# 240310 13:08:21 mysqld_safe Logging to syslog.
240310 13:08:21 mysqld_safe Starting mariadbd daemon with databases from /var/lib/mysql

root@i-0edcee8585bb735a1:/home/admin# mysql -u root
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 3
Server version: 10.5.23-MariaDB-0+deb11u1 Debian 11

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> use mysql;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [mysql]> flush privileges;
Query OK, 0 rows affected (0.001 sec)

MariaDB [mysql]> ALTER USER 'root'@'localhost' IDENTIFIED BY '';
Query OK, 0 rows affected (0.001 sec)

MariaDB [mysql]> flush privileges;
Query OK, 0 rows affected (0.000 sec)

MariaDB [mysql]> exit
Bye
root@i-0edcee8585bb735a1:/home/admin# kill -9 %1
root@i-0edcee8585bb735a1:/home/admin# /etc/init.d/mariadb start
Starting mariadb (via systemctl): mariadb.service.
```

Les bases de données attendues n'existant pas, il faut les créer avant chaque importation :

```console
admin@i-0edcee8585bb735a1:~/backups$ tar -xvzf dbs_to_restore.tar.gz first.sql
first.sql
admin@i-0edcee8585bb735a1:~/backups$ mysql -u root -e "CREATE DATABASE first;"
admin@i-0edcee8585bb735a1:~/backups$ mysql -u root first < first.sql 
admin@i-0edcee8585bb735a1:~/backups$ rm first.sql 
admin@i-0edcee8585bb735a1:~/backups$ tar -xvzf dbs_to_restore.tar.gz second.sql
second.sql
admin@i-0edcee8585bb735a1:~/backups$ mysql -u root -e "CREATE DATABASE second;"
admin@i-0edcee8585bb735a1:~/backups$ mysql -u root second < second.sql 
admin@i-0edcee8585bb735a1:~/backups$ rm second.sql 
admin@i-0edcee8585bb735a1:~/backups$ mysql -u root -e "CREATE DATABASE third;"
admin@i-0edcee8585bb735a1:~/backups$ tar -xvzf dbs_to_restore.tar.gz third.sql
third.sql
admin@i-0edcee8585bb735a1:~/backups$ rm dbs_to_restore.tar.gz
admin@i-0edcee8585bb735a1:~/backups$ mysql -u root third < third.sql
```
