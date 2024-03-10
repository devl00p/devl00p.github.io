---
title: "Solution du challenge Rosario de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Rosario": Restore a MySQL database

**Level:** Medium

**Type:** Fix

**Tags:** [mysql](https://sadservers.com/tag/mysql)  

**Description:** A developer created a database named 'main' but now some data is missing in the database. You need to restore the database using the the dump "/home/admin/backup.sql".  
The issue is that the developer forgot the root password for the MariaDB server.  
If you encounter an issue while restoring the database, fix it.

Credit: [Sebastian Segovia](https://www.linkedin.com/in/sebastian-segovia-a7518a228/)

**Test:** The database, once restored, has a table named "solution".

The "Check My Solution" button runs the script /home/admin/agent/check.sh, which you can see and execute.

**Time to Solve:** 15 minutes.

J'ai fouillé un peu pour trouver la bonne solution pour réinitialiser le mot de passe de l'utilisateur `root` de MariaDB.

Il est important d'avoir consulté le fichier `agent/check.sh` du challenge d'abord, car on voit que la vérification s'effectue sans mots de passe pour `root`.

Voici les étapes à suivre. D'abord l'arrêt de MariaDB est son lancement en mode `skip-grant-tables` :

```console
admin@i-07a44688ee65bf125:~$ sudo su
root@i-07a44688ee65bf125:/home/admin# /etc/init.d/mariadb stop
Stopping mariadb (via systemctl): mariadb.service.
root@i-07a44688ee65bf125:/home/admin# mysqld_safe --skip-grant-tables &
[1] 984
root@i-07a44688ee65bf125:/home/admin# 240305 15:56:04 mysqld_safe Logging to syslog.
240305 15:56:04 mysqld_safe Starting mariadbd daemon with databases from /var/lib/mysql
```

On peut alors se connecter en root sans mots de passe et définir un mot de passe vide :

```console
root@i-07a44688ee65bf125:/home/admin# mysql -u root
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 3
Server version: 10.5.23-MariaDB-0+deb11u1 Debian 11

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> use mysql;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [mysql]> ALTER USER 'root'@'localhost' IDENTIFIED BY '';
ERROR 1290 (HY000): The MariaDB server is running with the --skip-grant-tables option so it cannot execute this statement
MariaDB [mysql]> flush privileges;
Query OK, 0 rows affected (0.001 sec)

MariaDB [mysql]> ALTER USER 'root'@'localhost' IDENTIFIED BY '';
Query OK, 0 rows affected (0.001 sec)

MariaDB [mysql]> flush privileges;
Query OK, 0 rows affected (0.001 sec)
MariaDB [mysql]> exit
Bye
```

Ensuite, on relance MariaDB normalement :

```console
root@i-07a44688ee65bf125:/home/admin# jobs
[1]+  Running                 mysqld_safe --skip-grant-tables &
root@i-07a44688ee65bf125:/home/admin# kill -9 %1
root@i-07a44688ee65bf125:/home/admin# /etc/init.d/mariadb start
Starting mariadb (via systemctl): mariadb.service.
```

Finalement le dernier problème que l'on a, c'est que le caractère `?` est utilisé comme délimiter de ligne (à la place de `,`) :

```console
admin@i-0f83c4cf82c450cc7:~$ cat backup.sql 
-- MariaDB dump 10.19  Distrib 10.5.21-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: main
-- ------------------------------------------------------
-- Server version       10.5.21-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */?
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */?
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */?
/*!40101 SET NAMES utf8mb4 */?
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */?
/*!40103 SET TIME_ZONE='+00:00' */?
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */?
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */?
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */?
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */?

--
-- Table structure for table `solution`
--

DROP TABLE IF EXISTS `solution`?
--- snip ---
```

Il faut ajouter une ligne au début du fichier qui indique `DELIMITER ?`.

On peut alors importer la script de backup avec `mysql -u root main < backup.sql`.
