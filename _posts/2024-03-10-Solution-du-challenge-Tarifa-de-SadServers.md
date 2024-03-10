---
title: "Solution du challenge Tarifa de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Tarifa": Between Two Seas

**Level:** Medium

**Type:** Fix

**Tags:** [docker](https://sadservers.com/tag/docker)   [haproxy](https://sadservers.com/tag/haproxy)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There are three Docker containers defined in the *docker-compose.yml* file: an HAProxy accepting connections on port :5000 of the host, and two nginx containers, not exposed to the host.

The person who tried to set this up wanted to have HAProxy in front of the (backend or upstream) nginx containers load-balancing them but something is not working.

**Test:** Running curl localhost:5000 several times returns both hello there from nginx_0 and hello there from nginx_1

Check */home/admin/agent/check.sh* for the test that "Check My Solution" runs.

**Time to Solve:** 20 minutes.

On peut constater le problème nous même en demandant plusieurs fois la page HTML :

```console
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ curl localhost:5000
hello there from nginx_0
admin@i-064e74fec80bbfdae:~$ docker ps -a
CONTAINER ID   IMAGE           COMMAND                  CREATED        STATUS          PORTS                                       NAMES
c79c9eb25143   haproxy:2.8.4   "docker-entrypoint.s…"   3 months ago   Up 48 seconds   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   haproxy
4052b12402a3   nginx:1.25.3    "/docker-entrypoint.…"   3 months ago   Up 48 seconds   80/tcp                                      nginx_1
2624cd20f3c4   nginx:1.25.3    "/docker-entrypoint.…"   3 months ago   Up 49 seconds   80/tcp                                      nginx_0
```

Avec `docker inspect` on peut voir comment sont configurés les conteneurs qui tournent :

```
        "Mounts": [
            {
                "Type": "bind",
                "Source": "/home/admin/custom-nginx_0.conf",
                "Destination": "/etc/nginx/conf.d/default.conf",
                "Mode": "ro",
                "RW": false,
                "Propagation": "rprivate"
            },
            {
                "Type": "bind",
                "Source": "/home/admin/custom_index/nginx_0",
                "Destination": "/usr/share/nginx/html",
                "Mode": "rw",
                "RW": true,
                "Propagation": "rprivate"
            }
        ],
```

Pour ce qui est du contenu monté ça semble correct :

```console
admin@i-064e74fec80bbfdae:~$ cat custom_index/nginx_*/index.html
hello there from nginx_0
hello there from nginx_1
```

Jetons un œil au `docker-compose.yaml` :

```docker
version: '3'

services:
  nginx_0:
    image: nginx:1.25.3
    container_name: nginx_0
    restart: always
    volumes:
      - ./custom_index/nginx_0:/usr/share/nginx/html
      - ./custom-nginx_0.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - frontend_network

  nginx_1:
    image: nginx:1.25.3
    container_name: nginx_1
    restart: always
    volumes:
      - ./custom_index/nginx_1:/usr/share/nginx/html
      - ./custom-nginx_1.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - backend_network

  haproxy:
    image: haproxy:2.8.4
    container_name: haproxy
    restart: always
    ports:
      - "5000:5000"
    depends_on:
      - nginx_0
      - nginx_1
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    networks:
      - frontend_network

networks:
  frontend_network:
    driver: bridge
  backend_network:
    driver: bridge
```

On remarque déjà que `haproxy` n'a qu'un seul des réseaux dans ses dépendances `networks`. Il faut rajouter une ligne pour `backend_network`.

On peut relancer les conteneurs, mais le résultat n'est pas meilleur. Je me connecte à chaque conteneur pour voir s'ils répondent :

```console
admin@i-064e74fec80bbfdae:~$ docker exec -it 7f3733ea9925 /bin/sh
# curl http://127.0.0.1
hello there from nginx_0
# 
admin@i-064e74fec80bbfdae:~$ docker exec -it 0f59ba2de70d /bin/sh
# curl http://127.0.0.1
curl: (7) Failed to connect to 127.0.0.1 port 80 after 0 ms: Couldn't connect to server
```

La raison est que le second écoute sur un autre port :

```console
admin@i-064e74fec80bbfdae:~$ diff ./custom-nginx_0.conf  ./custom-nginx_1.conf
2c2
<     listen 80;
---
>     listen 81;
```

Il faut modifier la configuration du HAProxy comme ceci :

```
global
    daemon
    maxconn 256

defaults
    mode http
    default-server init-addr last,libc,none
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http-in
    bind *:5000
    default_backend nginx_backends

backend nginx_backends
    balance roundrobin
    server nginx_0 nginx_0:80 check
    server nginx_1 nginx_1:81 check
```

On peut alors tout relancer et ça fonctionne comme attendu :

```console
admin@i-064e74fec80bbfdae:~$ docker compose down
[+] Running 5/5
 ✔ Container haproxy               Removed                                                                                                                                                                    0.2s 
 ✔ Container nginx_0               Removed                                                                                                                                                                    0.3s 
 ✔ Container nginx_1               Removed                                                                                                                                                                    0.3s 
 ✔ Network admin_backend_network   Removed                                                                                                                                                                    0.1s 
 ✔ Network admin_frontend_network  Removed                                                                                                                                                                    0.2s 
admin@i-064e74fec80bbfdae:~$ docker compose up
[+] Running 5/5
 ✔ Network admin_frontend_network  Created                                                                                                                                                                    0.0s 
 ✔ Network admin_backend_network   Created                                                                                                                                                                    0.1s 
 ✔ Container nginx_0               Created                                                                                                                                                                    0.1s 
 ✔ Container nginx_1               Created                                                                                                                                                                    0.1s 
 ✔ Container haproxy               Created                                                                                                                                                                    0.0s 
Attaching to haproxy, nginx_0, nginx_1
nginx_1  | /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
nginx_1  | /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
nginx_1  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
nginx_1  | 10-listen-on-ipv6-by-default.sh: info: can not modify /etc/nginx/conf.d/default.conf (read-only file system?)
nginx_1  | /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
nginx_1  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
nginx_0  | /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
nginx_0  | /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
nginx_1  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
nginx_1  | /docker-entrypoint.sh: Configuration complete; ready for start up
nginx_0  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
nginx_0  | 10-listen-on-ipv6-by-default.sh: info: can not modify /etc/nginx/conf.d/default.conf (read-only file system?)
nginx_0  | /docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
nginx_0  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
nginx_0  | /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
nginx_0  | /docker-entrypoint.sh: Configuration complete; ready for start up
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: using the "epoll" event method
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: nginx/1.25.3
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14) 
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: OS: Linux 5.10.0-23-cloud-amd64
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: start worker processes
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: start worker process 21
nginx_1  | 2024/03/10 09:37:13 [notice] 1#1: start worker process 22
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: using the "epoll" event method
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: nginx/1.25.3
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14) 
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: OS: Linux 5.10.0-23-cloud-amd64
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: start worker processes
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: start worker process 21
nginx_0  | 2024/03/10 09:37:13 [notice] 1#1: start worker process 22
haproxy  | [NOTICE]   (1) : New worker (9) forked
haproxy  | [NOTICE]   (1) : Loading success.
```
