---
title: "Solution du challenge Cape Town de SadServers.com"
tags: [CTF,AdminSys,SadServers
---

**Scenario:** "Cape Town": Borked Nginx

**Level:** Medium

**Type:** Fix

**Tags:** [nginx](https://sadservers.com/tag/nginx)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There's an Nginx web server installed and managed by systemd. Running `curl -I 127.0.0.1:80` returns `curl: (7) Failed to connect to localhost port 80: Connection refused` , fix it so when you curl you get the default Nginx page.

**Test:** `curl -Is 127.0.0.1:80|head -1` returns `HTTP/1.1 200 OK`

**Time to Solve:** 15 minutes.

Déjà la base : est-ce que le port est en écoute (et donc le service lancé) ?

```console
admin@i-06cb61539b1effc2b:/$ ss -lntp
State                 Recv-Q                Send-Q                               Local Address:Port                               Peer Address:Port               Process                                          
LISTEN                0                     128                                        0.0.0.0:22                                      0.0.0.0:*                                                                   
LISTEN                0                     4096                                             *:6767                                          *:*                   users:(("sadagent",pid=567,fd=7))               
LISTEN                0                     4096                                             *:8080                                          *:*                   users:(("gotty",pid=566,fd=6))                  
LISTEN                0                     128                                           [::]:22                                         [::]:*  
```

Non, alors voyons son état systemctl :

```console
admin@i-06cb61539b1effc2b:/$ systemctl status nginx
● nginx.service - The NGINX HTTP and reverse proxy server
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: failed (Result: exit-code) since Sat 2024-03-02 09:52:55 UTC; 1min 16s ago
    Process: 574 ExecStartPre=/usr/sbin/nginx -t (code=exited, status=1/FAILURE)
        CPU: 29ms

Mar 02 09:52:55 i-06cb61539b1effc2b systemd[1]: Starting The NGINX HTTP and reverse proxy server...
Mar 02 09:52:55 i-06cb61539b1effc2b nginx[574]: nginx: [emerg] unexpected ";" in /etc/nginx/sites-enabled/default:1
Mar 02 09:52:55 i-06cb61539b1effc2b nginx[574]: nginx: configuration file /etc/nginx/nginx.conf test failed
Mar 02 09:52:55 i-06cb61539b1effc2b systemd[1]: nginx.service: Control process exited, code=exited, status=1/FAILURE
Mar 02 09:52:55 i-06cb61539b1effc2b systemd[1]: nginx.service: Failed with result 'exit-code'.
Mar 02 09:52:55 i-06cb61539b1effc2b systemd[1]: Failed to start The NGINX HTTP and reverse proxy server.
```

Erreur à la première ligne du fichier de configuration, voyons ça :

```console
admin@i-06cb61539b1effc2b:/etc/nginx/sites-enabled$ head default 
;
##
# You should look at the following URL's in order to grasp a solid understanding
# of Nginx configuration files in order to fully unleash the power of Nginx.
# https://www.nginx.com/resources/wiki/start/
# https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
# https://wiki.debian.org/Nginx/DirectoryStructure
#
# In most cases, administrators will remove this file from sites-enabled/ and
# leave it as reference inside of sites-available where it will continue to be
```

La correction est vite faite, mais sans trop de surprises, on tombe sur un problème plus gros :

```console
admin@i-06cb61539b1effc2b:/etc/nginx/sites-enabled$ sudo vi default 
admin@i-06cb61539b1effc2b:/etc/nginx/sites-enabled$ sudo systemctl start nginx
admin@i-06cb61539b1effc2b:/etc/nginx/sites-enabled$ systemctl status nginx
● nginx.service - The NGINX HTTP and reverse proxy server
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2024-03-02 09:56:14 UTC; 7s ago
    Process: 862 ExecStartPre=/usr/sbin/nginx -t (code=exited, status=0/SUCCESS)
    Process: 863 ExecStart=/usr/sbin/nginx (code=exited, status=0/SUCCESS)
   Main PID: 864 (nginx)
      Tasks: 2 (limit: 524)
     Memory: 2.4M
        CPU: 31ms
     CGroup: /system.slice/nginx.service
             ├─864 nginx: master process /usr/sbin/nginx
             └─865 nginx: worker process

Mar 02 09:56:14 i-06cb61539b1effc2b systemd[1]: Starting The NGINX HTTP and reverse proxy server...
Mar 02 09:56:14 i-06cb61539b1effc2b nginx[862]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
Mar 02 09:56:14 i-06cb61539b1effc2b nginx[862]: nginx: configuration file /etc/nginx/nginx.conf test is successful
Mar 02 09:56:14 i-06cb61539b1effc2b systemd[1]: Started The NGINX HTTP and reverse proxy server.
admin@i-06cb61539b1effc2b:/etc/nginx/sites-enabled$ curl -Is 127.0.0.1:80|head -1
HTTP/1.1 500 Internal Server Error
```

On va devoir regarder dans les logs du serveur.

```console
admin@i-06cb61539b1effc2b:/etc/nginx/sites-enabled$ tail /var/log/nginx/error.log 
2022/09/11 16:39:11 [emerg] 5875#5875: unexpected ";" in /etc/nginx/sites-enabled/default:1
2022/09/11 16:54:26 [emerg] 5931#5931: unexpected ";" in /etc/nginx/sites-enabled/default:1
2022/09/11 16:55:00 [emerg] 5961#5961: unexpected ";" in /etc/nginx/sites-enabled/default:1
2022/09/11 17:02:07 [emerg] 6066#6066: unexpected ";" in /etc/nginx/sites-enabled/default:1
2022/09/11 17:07:03 [emerg] 6146#6146: unexpected ";" in /etc/nginx/sites-enabled/default:1
2024/03/02 09:52:55 [emerg] 574#574: unexpected ";" in /etc/nginx/sites-enabled/default:1
2024/03/02 09:56:14 [alert] 864#864: socketpair() failed while spawning "worker process" (24: Too many open files)
2024/03/02 09:56:14 [emerg] 865#865: eventfd() failed (24: Too many open files)
2024/03/02 09:56:14 [alert] 865#865: socketpair() failed (24: Too many open files)
2024/03/02 09:56:40 [crit] 865#865: *1 open() "/var/www/html/index.nginx-debian.html" failed (24: Too many open files), client: 127.0.0.1, server: _, request: "HEAD / HTTP/1.1", host: "127.0.0.1"
```

Le serveur ne parvient pas à ouvrir le fichier d'index, car trop de fichiers sont ouverts sur le système.

Ma première réaction a été de voir du côté de `ulimit` :

```console
admin@i-05a9742de4b12737a:/$ ulimit -a
real-time non-blocking time  (microseconds, -R) unlimited
core file size              (blocks, -c) 0
data seg size               (kbytes, -d) unlimited
scheduling priority                 (-e) 0
file size                   (blocks, -f) unlimited
pending signals                     (-i) 1748
max locked memory           (kbytes, -l) 64
max memory size             (kbytes, -m) unlimited
open files                          (-n) 1024
pipe size                (512 bytes, -p) 8
POSIX message queues         (bytes, -q) 819200
real-time priority                  (-r) 0
stack size                  (kbytes, -s) 8192
cpu time                   (seconds, -t) unlimited
max user processes                  (-u) 1748
virtual memory              (kbytes, -v) unlimited
file locks                          (-x) unlimited
```

Tout semble standard ici...

Si la limite n'est pas globale au système, elle concerne alors probablement que le processus. Encore un hack de chez systemd ?

```console
root@i-05a9742de4b12737a:/etc/security# cat /etc/systemd/system/nginx.service
[Unit]
Description=The NGINX HTTP and reverse proxy server
After=syslog.target network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/usr/sbin/nginx -s reload
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true
LimitNOFILE=10

[Install]
WantedBy=multi-user.target
```

Bingo ! La directive `LimitNOFILE` limite le nombre de fichiers ouverts par le service.

Il suffit de retirer l'option et de redémarrer le service :

```console
root@i-05a9742de4b12737a:/etc/security# vi /etc/systemd/system/nginx.service
root@i-05a9742de4b12737a:/etc/security# systemctl restart nginx
Warning: The unit file, source configuration file or drop-ins of nginx.service changed on disk. Run 'systemctl daemon-reload' to reload units.
root@i-05a9742de4b12737a:/etc/security# systemctl daemon-reload
root@i-05a9742de4b12737a:/etc/security# curl -Is 127.0.0.1:80|head -1
HTTP/1.1 500 Internal Server Error
root@i-05a9742de4b12737a:/etc/security# systemctl restart nginx
root@i-05a9742de4b12737a:/etc/security# curl -Is 127.0.0.1:80|head -1
HTTP/1.1 200 OK
```
