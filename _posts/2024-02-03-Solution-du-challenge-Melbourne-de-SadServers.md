---
title: "Solution du challenge Melbourne de SadServers.com"
tags: [CTF,AdminSys,SadServers
---

**Scenario:** "Melbourne": WSGI with Gunicorn

**Level:** Medium

**Type:** Fix

**Tags:** [gunicorn](https://sadservers.com/tag/gunicorn)   [nginx](https://sadservers.com/tag/nginx)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There is a Python [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) web application file at `/home/admin/wsgi.py` , the purpose of which is to serve the string "Hello, world!". This file is served by a [Gunicorn](https://docs.gunicorn.org/en/stable/) server which is fronted by an nginx server (both servers managed by systemd). So the flow of an HTTP request is: Web Client (curl) -> Nginx -> Gunicorn -> wsgi.py . The objective is to be able to curl the localhost (on default port :80) and get back "Hello, world!", using the current setup.

**Test:** `curl -s http://localhost` returns Hello, world! (serving the wsgi.py file via Gunicorn and Nginx)

**Time to Solve:** 20 minutes.

Voyons voir pourquoi ce serveur web ne fonctionne pas :)

```console
admin@i-0488d0c89dff19acb:/$ curl -v http://localhost 
*   Trying 127.0.0.1:80...
* connect to 127.0.0.1 port 80 failed: Connection refused
* Failed to connect to localhost port 80: Connection refused
* Closing connection 0
curl: (7) Failed to connect to localhost port 80: Connection refused
admin@i-0488d0c89dff19acb:/$ ps aux | grep -i "nginx|gunicorn"
admin        864  0.0  0.1   5276   704 pts/0    S<+  15:50   0:00 grep -i nginx|gunicorn
```

Pour le moment, rien n'est lancé !

Le fichier `wsgi.py` est le suivant :

```python
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', '0'), ])
    return [b'Hello, world!']
```

La directive `proxy_pass` définie dans `/etc/nginx/sites-enabled/default` m'a semblé étrange avec ses deux schemes mais elle est finalement légitime.

```nginx
server {
    listen 80;

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.socket;
    }
}
```

J'ai trouvé une documentation qui correspond parfaitement à notre situation :

[Deploying Gunicorn &mdash; Gunicorn 21.2.0 documentation](https://docs.gunicorn.org/en/stable/deploy.html#systemd)

Le fichier de configuration `proxy_params` n'apporte rien de bien intéressant :

```nginx
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

Allons voir du côté de systemd avec le fichier `/etc/systemd/system/gunicorn.service` :

```systemd
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=/home/admin
ExecStart=/usr/local/bin/gunicorn \
          --bind unix:/run/gunicorn.sock \
          wsgi
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Essayons de lancer la commande manuellement :

```console
admin@i-0488d0c89dff19acb:~$ /usr/local/bin/gunicorn --bind unix:/run/gunicorn.sock wsgi
[2024-03-02 15:59:08 +0000] [963] [INFO] Starting gunicorn 20.1.0
[2024-03-02 15:59:08 +0000] [963] [ERROR] Retrying in 1 second.
[2024-03-02 15:59:09 +0000] [963] [ERROR] Retrying in 1 second.
[2024-03-02 15:59:10 +0000] [963] [ERROR] Retrying in 1 second.
[2024-03-02 15:59:11 +0000] [963] [ERROR] Retrying in 1 second.
[2024-03-02 15:59:12 +0000] [963] [ERROR] Retrying in 1 second.
[2024-03-02 15:59:13 +0000] [963] [ERROR] Can't connect to /run/gunicorn.sock
```

L'entrée systemd repose sur une autre unité qui est `/etc/systemd/system/gunicorn.socket` :

```systemd
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
# SocketUser=nginx

[Install]
WantedBy=sockets.target
```

Comme `SocketUser` est commenté, systemctl va créer `/run/gunicorn.sock` avec le compte root :

```console
admin@i-0488d0c89dff19acb:~$ sudo systemctl enable --now gunicorn.socket
admin@i-0488d0c89dff19acb:~$ ls -al /run/gunicorn.sock
srw-rw-rw- 1 root root 0 Mar  2 15:48 /run/gunicorn.sock
admin@i-0488d0c89dff19acb:~$ /usr/local/bin/gunicorn --bind unix:/run/gunicorn.sock wsgi
[2024-03-02 16:01:23 +0000] [992] [INFO] Starting gunicorn 20.1.0
[2024-03-02 16:01:23 +0000] [992] [ERROR] Retrying in 1 second.
[2024-03-02 16:01:24 +0000] [992] [ERROR] Retrying in 1 second.
[2024-03-02 16:01:25 +0000] [992] [ERROR] Retrying in 1 second.
[2024-03-02 16:01:26 +0000] [992] [ERROR] Retrying in 1 second.
[2024-03-02 16:01:27 +0000] [992] [ERROR] Retrying in 1 second.
[2024-03-02 16:01:28 +0000] [992] [ERROR] Can't connect to /run/gunicorn.sock
```

Pour obtenir plus d'information, on relance la commande avec `--log-level DEBUG` :

```
[2024-03-02 16:23:51 +0000] [870] [DEBUG] connection to /run/gunicorn.sock failed: [Errno 13] Permission denied: '/run/gunicorn.sock'
[2024-03-02 16:23:51 +0000] [870] [ERROR] Retrying in 1 second.
[2024-03-02 16:23:52 +0000] [870] [ERROR] Can't connect to /run/gunicorn.sock
```

Je peux éditer `/etc/systemd/system/gunicorn.socket` pour mettre l'utilisateur `admin` comme `SocketUser` : 

```console
admin@i-097995a6b9078f235:/$ sudo systemctl disable --now gunicorn.socket
Removed /etc/systemd/system/sockets.target.wants/gunicorn.socket.
admin@i-097995a6b9078f235:/$ vi /etc/systemd/system/gunicorn.socket
admin@i-097995a6b9078f235:/$ sudo vi /etc/systemd/system/gunicorn.socket
admin@i-097995a6b9078f235:/$ sudo systemctl enable --now gunicorn.socket
Created symlink /etc/systemd/system/sockets.target.wants/gunicorn.socket → /etc/systemd/system/gunicorn.socket.
admin@i-097995a6b9078f235:/$ ls /run/gunicorn.sock  -al
srw-rw-rw- 1 admin admin 0 Mar  2 16:28 /run/gunicorn.sock
```

Ça marche en théorie ! Il faut aussi que le dossier `/run` soit disponible en écriture pour d'autres utilisateurs que `root` :

```console
admin@i-097995a6b9078f235:/$ sudo chmod o+w run/
admin@i-097995a6b9078f235:/$ /usr/local/bin/gunicorn --log-level DEBUG --bind unix:/run/gunicorn.sock wsgi
[2024-03-02 16:32:35 +0000] [10936] [DEBUG] Current configuration:
  config: ./gunicorn.conf.py
  wsgi_app: None
  bind: ['unix:/run/gunicorn.sock']
--- snip ---
[2024-03-02 16:36:55 +0000] [10958] [INFO] Starting gunicorn 20.1.0
[2024-03-02 16:36:55 +0000] [10958] [DEBUG] Arbiter booted
[2024-03-02 16:36:55 +0000] [10958] [INFO] Listening at: unix:/run/gunicorn.sock (10958)
[2024-03-02 16:36:55 +0000] [10958] [INFO] Using worker: sync
[2024-03-02 16:36:55 +0000] [10959] [INFO] Booting worker with pid: 10959
[2024-03-02 16:36:55 +0000] [10958] [DEBUG] 1 workers
```

Je peux maintenant lancer Nginx :

```console
admin@i-097995a6b9078f235:~$ sudo systemctl start nginx
admin@i-097995a6b9078f235:~$ curl -s http://localhost
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.18.0</center>
</body>
</html>
```

Si j'avais fait plus attention j'aurais vu dans sa configuration qu'il utilise un nom de socket un peu différent :

```console
admin@i-097995a6b9078f235:~$ sudo tail /var/log/nginx/error.log
2024/03/02 16:38:27 [crit] 10976#10976: *1 connect() to unix:/run/gunicorn.socket failed (2: No such file or directory) while connecting to upstream, client: 127.0.0.1, server: , request: "GET / HTTP/1.1", upstream: "http://unix:/run/gunicorn.socket:/", host: "localhost"
```

Je remplace `gunicorn.socket` par `gunicorn.sock` dans la configuration du Nginx et je relance :

```console
admin@i-00529e3f60fcd6fa9:/$ curl -D- http://127.0.0.1/
HTTP/1.1 200 OK
Server: nginx/1.18.0
Date: Sat, 02 Mar 2024 16:49:11 GMT
Content-Type: text/html
Content-Length: 0
Connection: keep-alive
```

Pas de contenu. C'est parce que le script `wsgi.py` met `Content-Length` à 0.

Une fois l'entête supprimé ça fonctionne :

```console
admin@i-00529e3f60fcd6fa9:/$ sudo systemctl restart gunicorn.service
admin@i-00529e3f60fcd6fa9:/$ sudo systemctl restart nginx.service
admin@i-00529e3f60fcd6fa9:/$ curl -D- http://127.0.0.1/
HTTP/1.1 200 OK
Server: nginx/1.18.0
Date: Sat, 02 Mar 2024 16:51:34 GMT
Content-Type: text/html
Transfer-Encoding: chunked
Connection: keep-alive

Hello, world!
```
