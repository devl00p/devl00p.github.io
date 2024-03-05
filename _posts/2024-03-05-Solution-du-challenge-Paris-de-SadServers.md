---
title: "Solution du challenge Paris de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Paris": Where is my webserver?

**Level:** Medium

**Type:** Hack

**Tags:** [unusual-tricky](https://sadservers.com/tag/unusual-tricky)  

**Description:** A developer put an important password on his webserver localhost:5000 . However, he can't find a way to recover it. This scenario is easy to solve once you realize the one "trick".

Find the password and save it in `/home/admin/mysolution` , for example: `echo "somepassword" > ~/mysolution`

Scenario credit: PuppiestDoggo

**Test:** `md5sum ~/mysolution` returns d8bee9d7f830d5fb59b89e1e120cce8e

**Time to Solve:** 15 minutes.

Le fichier `webserver.py` est la propriété de root mais présent dans notre dossier, on peut donc le déplacer :

```console
admin@i-0914c01abdff80d82:~$ ls -al
total 44
drwxr-xr-x 6 admin admin 4096 Sep 24 23:20 .
drwxr-xr-x 3 root  root  4096 Sep 17 16:44 ..
drwx------ 3 admin admin 4096 Sep 20 15:52 .ansible
-rw------- 1 admin admin  121 Mar  4 20:40 .bash_history
-rw-r--r-- 1 admin admin  220 Aug  4  2021 .bash_logout
-rw-r--r-- 1 admin admin 3526 Aug  4  2021 .bashrc
drwxr-xr-x 3 admin admin 4096 Sep 20 15:56 .config
-rw-r--r-- 1 admin admin  807 Aug  4  2021 .profile
drwx------ 2 admin admin 4096 Sep 17 16:44 .ssh
drwxr-xr-x 2 admin root  4096 Sep 24 23:20 agent
-rwxrwx--- 1 root  root   360 Sep 24 23:20 webserver.py
admin@i-0914c01abdff80d82:~$ mv webserver.py yolo
admin@i-0914c01abdff80d82:~$ cat yolo
cat: yolo: Permission denied
admin@i-0914c01abdff80d82:~$ ls -al
total 44
drwxr-xr-x 6 admin admin 4096 Mar  4 20:40 .
drwxr-xr-x 3 root  root  4096 Sep 17 16:44 ..
drwx------ 3 admin admin 4096 Sep 20 15:52 .ansible
-rw------- 1 admin admin  194 Mar  4 20:40 .bash_history
-rw-r--r-- 1 admin admin  220 Aug  4  2021 .bash_logout
-rw-r--r-- 1 admin admin 3526 Aug  4  2021 .bashrc
drwxr-xr-x 3 admin admin 4096 Sep 20 15:56 .config
-rw-r--r-- 1 admin admin  807 Aug  4  2021 .profile
drwx------ 2 admin admin 4096 Sep 17 16:44 .ssh
drwxr-xr-x 2 admin root  4096 Sep 24 23:20 agent
-rwxrwx--- 1 root  root   360 Sep 24 23:20 yolo
```

En revanche, il n'est pas possible de modifier les permissions et je ne vois aucune astuce pour résoudre le problème.

En regardant l'indice ça devient plus clair :

> **1.** The user agent of the client you are using against the web server may play a role here.

Testons avec le User-Agent "admin" :

```console
admin@i-0914c01abdff80d82:~$ curl -D- -H "User-Agent: admin" http://127.0.0.1:5000/
HTTP/1.1 200 OK
Server: Werkzeug/2.3.7 Python/3.9.2
Date: Mon, 04 Mar 2024 20:51:32 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 35
Connection: close

Welcome! Password is FDZPmh5AX3oiJt
```
