---
title: "Solution du challenge Manhattan de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Manhattan": can't write data into database.

**Level:** Medium

**Type:** Fix

**Tags:** [disk volumes](https://sadservers.com/tag/disk%20volumes)   [postgres](https://sadservers.com/tag/postgres)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** Your objective is to be able to insert a row in an existing Postgres database. The issue is not specific to Postgres and you don't need to know details about it (although it may help).

Helpful Postgres information: it's a service that listens to a port (:5432) and writes to disk in a data directory, the location of which is defined in the *data_directory* parameter of the configuration file `/etc/postgresql/14/main/postgresql.conf`. In our case Postgres is managed by *systemd* as a unit with name *postgresql*.

**Test:** (from default admin user) `sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt `

Should return: `INSERT 0 1`

**Time to Solve:** 20 minutes.

On entre ici dans les scénarios de niveau intermédiaire proposés sur [sadservers.com](https://sadservers.com/).

On a une commande qui doit fonctionner pour résoudre le challenge, on va donc la lancer pour voir pourquoi ça ne passe pas.

```console
root@i-0b8ce19730a071b11:/# sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
        Is the server running locally and accepting connections on that socket?
```

Le client ne parvient pas à se connecter au socket serveur qui est de type Unix.

Je regarde le fichier de configuration de Postgresql. Ce dernier est plein de lignes commentées, mais avec l'aide de `grep` je peux faire le tri.

```console
root@i-0b8ce19730a071b11:/# cat /etc/postgresql/14/main/postgresql.conf | grep -v "^\s*#" | grep -v "^$"
data_directory = '/opt/pgdata/main'             # use data in another directory
hba_file = '/etc/postgresql/14/main/pg_hba.conf'        # host-based authentication file
ident_file = '/etc/postgresql/14/main/pg_ident.conf'    # ident configuration file
external_pid_file = '/var/run/postgresql/14-main.pid'                   # write an extra PID file
port = 5432                             # (change requires restart)
max_connections = 100                   # (change requires restart)
unix_socket_directories = '/var/run/postgresql' # comma-separated list of directories
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
shared_buffers = 128MB                  # min 128kB
dynamic_shared_memory_type = posix      # the default is the first option
max_wal_size = 1GB
min_wal_size = 80MB
log_line_prefix = '%m [%p] %q%u@%d '            # special values:
log_timezone = 'Etc/UTC'
cluster_name = '14/main'                        # added to process titles if nonempty
stats_temp_directory = '/var/run/postgresql/14-main.pg_stat_tmp'
datestyle = 'iso, mdy'
timezone = 'Etc/UTC'
lc_messages = 'C.UTF-8'                 # locale for system error message
lc_monetary = 'C.UTF-8'                 # locale for monetary formatting
lc_numeric = 'C.UTF-8'                  # locale for number formatting
lc_time = 'C.UTF-8'                             # locale for time formatting
default_text_search_config = 'pg_catalog.english'
include_dir = 'conf.d'                  # include files ending in '.conf' from
```

On voit un numéro de port et une mention des sockets Unix. Ça semble raccord avec le nom de fichier auquel tente d'accéder le client.

A tout hasard on peut vérifier les ports TCP :

```console
root@i-0b8ce19730a071b11:/# ss -lntp
State        Recv-Q        Send-Q               Local Address:Port               Peer Address:Port                                                
LISTEN       0             128                        0.0.0.0:22                      0.0.0.0:*           users:(("sshd",pid=616,fd=3))           
LISTEN       0             128                              *:6767                          *:*           users:(("sadagent",pid=590,fd=7))       
LISTEN       0             128                              *:8080                          *:*           users:(("gotty",pid=582,fd=6))          
LISTEN       0             128                           [::]:22                         [::]:*           users:(("sshd",pid=616,fd=4))
```

Rien du tout ici. Et comme on s'y attend, rien de plus pour le socket Unix :

```console
root@i-0b8ce19730a071b11:/# ls /var/run/postgresql/
14-main.pg_stat_tmp
```

En fin de compte, est-ce que PostgreSQL tourne ?

```console
root@i-0b8ce19730a071b11:/# ps aux | grep -i postgr
root       890  0.0  0.1   4964   820 pts/0    S+   09:09   0:00 grep -i postgr
```

Non. Voyons voir la liste des unités systemd avec la commande `systemctl list-units` :

```
  postgresql.service                                                       loaded active exited    PostgreSQL RDBMS                              
● postgresql@14-main.service                                               loaded failed failed    PostgreSQL Cluster 14-main
```

Il y a deux services dont l'un qui est en échec. On va se renseigner sur le status de chacun.

```console
root@i-0b8ce19730a071b11:/# systemctl status postgresql.service
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: active (exited) since Sat 2024-03-02 09:02:30 UTC; 9min ago
  Process: 670 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
 Main PID: 670 (code=exited, status=0/SUCCESS)

Mar 02 09:02:30 i-0b8ce19730a071b11 systemd[1]: Starting PostgreSQL RDBMS...
Mar 02 09:02:30 i-0b8ce19730a071b11 systemd[1]: Started PostgreSQL RDBMS.
```

On voit sur le second service que la création d'un fichier échoue en raison d'un disque plein :

```console
root@i-0b8ce19730a071b11:/# systemctl status postgresql@14-main.service 
● postgresql@14-main.service - PostgreSQL Cluster 14-main
   Loaded: loaded (/lib/systemd/system/postgresql@.service; enabled-runtime; vendor preset: enabled)
   Active: failed (Result: protocol) since Sat 2024-03-02 09:12:49 UTC; 1min 45s ago
  Process: 901 ExecStart=/usr/bin/pg_ctlcluster --skip-systemctl-redirect 14-main start (code=exited, status=1/FAILURE)

Mar 02 09:12:49 i-0b8ce19730a071b11 systemd[1]: Starting PostgreSQL Cluster 14-main...
Mar 02 09:12:49 i-0b8ce19730a071b11 postgresql@14-main[901]: Error: /usr/lib/postgresql/14/bin/pg_ctl /usr/lib/postgresql/14/bin/pg_ctl start -D /opt/pgdata/main -l /var/log/postgresql/postgresql-14-main.log -s 
Mar 02 09:12:49 i-0b8ce19730a071b11 postgresql@14-main[901]: 2024-03-02 09:12:49.122 UTC [906] FATAL:  could not create lock file "postmaster.pid": No space left on device
Mar 02 09:12:49 i-0b8ce19730a071b11 postgresql@14-main[901]: pg_ctl: could not start server
Mar 02 09:12:49 i-0b8ce19730a071b11 postgresql@14-main[901]: Examine the log output.
Mar 02 09:12:49 i-0b8ce19730a071b11 systemd[1]: postgresql@14-main.service: Can't open PID file /run/postgresql/14-main.pid (yet?) after start: No such file or directory
Mar 02 09:12:49 i-0b8ce19730a071b11 systemd[1]: postgresql@14-main.service: Failed with result 'protocol'.
Mar 02 09:12:49 i-0b8ce19730a071b11 systemd[1]: Failed to start PostgreSQL Cluster 14-main.
```

J'ai pu récupérer la commande exacte que le service tente de lancer :

```bash
/usr/lib/postgresql/14/bin/pg_ctl start -D /opt/pgdata/main \
  -l /var/log/postgresql/postgresql-14-main.log -s -o \
  -c 'config_file="/etc/postgresql/14/main/postgresql.conf"'
```

Voici l'aide pour l'explication des options :

```console
postgres@i-0b8ce19730a071b11:/$ /usr/lib/postgresql/14/bin/pg_ctl --help
pg_ctl is a utility to initialize, start, stop, or control a PostgreSQL server.

Usage:
  pg_ctl init[db]   [-D DATADIR] [-s] [-o OPTIONS]
  pg_ctl start      [-D DATADIR] [-l FILENAME] [-W] [-t SECS] [-s]
                    [-o OPTIONS] [-p PATH] [-c]
  pg_ctl stop       [-D DATADIR] [-m SHUTDOWN-MODE] [-W] [-t SECS] [-s]
  pg_ctl restart    [-D DATADIR] [-m SHUTDOWN-MODE] [-W] [-t SECS] [-s]
                    [-o OPTIONS] [-c]
  pg_ctl reload     [-D DATADIR] [-s]
  pg_ctl status     [-D DATADIR]
  pg_ctl promote    [-D DATADIR] [-W] [-t SECS] [-s]
  pg_ctl logrotate  [-D DATADIR] [-s]
  pg_ctl kill       SIGNALNAME PID

Common options:
  -D, --pgdata=DATADIR   location of the database storage area
  -s, --silent           only print errors, no informational messages
  -t, --timeout=SECS     seconds to wait when using -w option
  -V, --version          output version information, then exit
  -w, --wait             wait until operation completes (default)
  -W, --no-wait          do not wait until operation completes
  -?, --help             show this help, then exit
If the -D option is omitted, the environment variable PGDATA is used.

Options for start or restart:
  -c, --core-files       allow postgres to produce core files
  -l, --log=FILENAME     write (or append) server log to FILENAME
  -o, --options=OPTIONS  command line options to pass to postgres
                         (PostgreSQL server executable) or initdb
  -p PATH-TO-POSTGRES    normally not necessary

Options for stop or restart:
  -m, --mode=MODE        MODE can be "smart", "fast", or "immediate"

Shutdown modes are:
  smart       quit after all clients have disconnected
  fast        quit directly, with proper shutdown (default)
  immediate   quit without complete shutdown; will lead to recovery on restart

Allowed signal names for kill:
  ABRT HUP INT KILL QUIT TERM USR1 USR2

Report bugs to <pgsql-bugs@lists.postgresql.org>.
PostgreSQL home page: <https://www.postgresql.org/>
```

Lançons la commande directement pour voir si on reproduit puis jetons un œil aux disques :

```console
postgres@i-0ae5a99cc5d8a1de9:/$ /usr/lib/postgresql/14/bin/pg_ctl start -D /opt/pgdata/main -l /var/log/postgresql/postgresql-14-main.log -s -o '-c config_file="/etc/postgresql/14/main/postgresql.conf"'
pg_ctl: could not start server
Examine the log output.
postgres@i-0ae5a99cc5d8a1de9:/$ tail /var/log/postgresql/postgresql-14-main.log
2024-03-02 09:34:19.689 UTC [904] FATAL:  could not create lock file "postmaster.pid": No space left on device
postgres@i-0ae5a99cc5d8a1de9:/$ df -h
Filesystem       Size  Used Avail Use% Mounted on
udev             224M     0  224M   0% /dev
tmpfs             47M  1.5M   46M   4% /run
/dev/nvme1n1p1   7.7G  1.2G  6.1G  17% /
tmpfs            233M     0  233M   0% /dev/shm
tmpfs            5.0M     0  5.0M   0% /run/lock
tmpfs            233M     0  233M   0% /sys/fs/cgroup
/dev/nvme1n1p15  124M  278K  124M   1% /boot/efi
/dev/nvme0n1     8.0G  8.0G   28K 100% /opt/pgdata
tmpfs             47M     0   47M   0% /run/user/108
```

Où se trouve normalement ce fichier `postmaster.pid` ? D'après [cette documentation](https://docs.postgresql.fr/current/server-start.html) :

> Tant que le serveur est lancé, son pid est stocké dans le fichier `postmaster.pid` du répertoire de données. C'est utilisé pour empêcher plusieurs instances du serveur d'être exécutées dans le même répertoire de données et peut aussi être utilisé pour arrêter le processus le serveur.

Par conséquent, ça correspond bien au dossier `/opt/pgdata` qui est plein.

```console
postgres@i-0ae5a99cc5d8a1de9:/$ cd /opt/pgdata
postgres@i-0ae5a99cc5d8a1de9:/opt/pgdata$ du -h --max-depth 1
50M     ./main
8.0G    .
postgres@i-0ae5a99cc5d8a1de9:/opt/pgdata$ ls -alh
total 8.0G
drwxr-xr-x  3 postgres postgres   82 May 21  2022 .
drwxr-xr-x  3 root     root     4.0K May 21  2022 ..
-rw-r--r--  1 root     root       69 May 21  2022 deleteme
-rw-r--r--  1 root     root     7.0G May 21  2022 file1.bk
-rw-r--r--  1 root     root     923M May 21  2022 file2.bk
-rw-r--r--  1 root     root     488K May 21  2022 file3.bk
drwx------ 19 postgres postgres 4.0K May 21  2022 main
```

Il y a trois fichiers `.bk` qui prennent de la place. Il suffit de les supprimer. Après ça le service fonctionne normalement :

```console
root@i-0ae5a99cc5d8a1de9:/# systemctl restart postgresql.service
root@i-0ae5a99cc5d8a1de9:/# sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt
INSERT 0 1
```
