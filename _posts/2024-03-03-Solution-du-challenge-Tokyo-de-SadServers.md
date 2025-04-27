---
title: "Solution du challenge Tokyo de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Tokyo": can't serve web file

**Level:** Medium

**Type:** Fix

**Tags:** [apache](https://sadservers.com/tag/apache)    [realistic-interviews](https://sadservers.com/tag/realistic-interviews)    

**Description:**  There's a web server serving a file  `/var/www/html/index.html`  with content "hello sadserver" but when we try to check it locally with an HTTP client like  `curl 127.0.0.1:80`, nothing is returned. This scenario is not about the particular web server configuration and you only need to have general knowledge about how web servers work.

**Test:**  `curl 127.0.0.1:80`  should return:  `hello sadserver`

**Time to Solve:**  15 minutes.

Voyons ce qu'il se passe avec ce serveur web...

Un `curl` montre que le serveur ne répond pas (timeout). Deux possibilités, soit le serveur fait tourner un script qui prend une éternité, soit le pare-feu bloque notre requête.

```console
root@ip-172-31-21-14:/# curl -v 127.0.0.1:80
*   Trying 127.0.0.1:80...
^C
root@ip-172-31-21-14:/# iptables -L
Chain INPUT (policy ACCEPT)
target     prot opt source               destination         
DROP       tcp  --  anywhere             anywhere             tcp dpt:http

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination    
```

C'était donc la seconde hypothèse. On va supprimer les règles du pare-feu et retenter :

```console
root@ip-172-31-21-14:/# iptables -F
root@ip-172-31-21-14:/# curl -v 127.0.0.1:80
*   Trying 127.0.0.1:80...
* Connected to 127.0.0.1 (127.0.0.1) port 80 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1
> User-Agent: curl/7.81.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 403 Forbidden
< Date: Sat, 02 Mar 2024 09:43:44 GMT
< Server: Apache/2.4.52 (Ubuntu)
< Content-Length: 274
< Content-Type: text/html; charset=iso-8859-1
< 
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.52 (Ubuntu) Server at 127.0.0.1 Port 80</address>
</body></html>
* Connection #0 to host 127.0.0.1 left intact
```

Cette fois, j'ai un problème d'accès. On doit avoir des pistes dans `/etc/apache2/apache2.conf`.

```apache
<Directory />
        Options FollowSymLinks
        AllowOverride None
        Require all denied
</Directory>
```

Ce `denied` ne me dit rien de bon, je le change par `granted`.

Je vois aussi que le fichier d'index est lisible uniquement par root, on va corriger ça :

```console
root@ip-172-31-21-14:/etc/apache2# ls -al /var/www/html/
total 12
drwxr-xr-x 2 root root 4096 Aug  1  2022 .
drwxr-xr-x 3 root root 4096 Aug  1  2022 ..
-rw------- 1 root root   16 Aug  1  2022 index.html
root@ip-172-31-21-14:/etc/apache2# chmod o+r /var/www/html/index.html 
root@ip-172-31-21-14:/etc/apache2# curl 127.0.0.1:80
hello sadserver
```
