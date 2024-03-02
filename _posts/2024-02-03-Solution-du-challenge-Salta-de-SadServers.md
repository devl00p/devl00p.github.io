---
title: "Solution du challenge Salta de SadServers.com"
tags: [CTF,AdminSys,SadServers
---

**Scenario:** "Salta": Docker container won't start.

**Level:** Medium

**Type:** Fix

**Tags:** [docker](https://sadservers.com/tag/docker)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There's a "dockerized" Node.js web application in the `/home/admin/app` directory. Create a Docker container so you get a web app on port *:8888* and can *curl* to it. For the solution to be valid, there should be only one running Docker container.

**Test:** `curl localhost:8888` returns `Hello World!` from a running container.

**Time to Solve:** 15 minutes.

C'est parti pour du Docker !

```console
admin@i-0d07b2079856860d3:/$ cd home/admin/app/
admin@i-0d07b2079856860d3:~/app$ ls -a
.  ..  .dockerignore  Dockerfile  package-lock.json  package.json  server.js
admin@i-0d07b2079856860d3:~/app$ cat .dockerignore 
node_modules
npm-debug.log

admin@i-0d07b2079856860d3:~/app$ cat Dockerfile 
# documentation https://nodejs.org/en/docs/guides/nodejs-docker-webapp/

# most recent node (security patches) and alpine (minimal, adds to security, possible libc issues)
FROM node:15.7-alpine 

# Create app directory & copy app files
WORKDIR /usr/src/app

# we copy first package.json only, so we take advantage of cached Docker layers
COPY ./package*.json ./

# RUN npm ci --only=production
RUN npm install

# Copy app source
COPY ./* ./

# port used by this app
EXPOSE 8880

# command to run
CMD [ "node", "serve.js" ]
```

À première vua tout semble bon. Voyons voir s'il y a encore un conteneur présent :

```console
admin@i-0d07b2079856860d3:~/app$ sudo docker images -a
REPOSITORY   TAG           IMAGE ID       CREATED         SIZE
<none>       <none>        a6ee5c4d5a96   17 months ago   124MB
<none>       <none>        0b18357df7c9   17 months ago   124MB
app          latest        1d782b86d6f2   17 months ago   124MB
<none>       <none>        5cad5aa08c7a   17 months ago   124MB
<none>       <none>        acfb467c80ba   17 months ago   110MB
<none>       <none>        463b1571f18e   17 months ago   110MB
node         15.7-alpine   706d12284dd5   3 years ago     110MB
admin@i-0d07b2079856860d3:~/app$ sudo docker ps -a
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS                     PORTS     NAMES
124a4fb17a1c   app       "docker-entrypoint.s…"   17 months ago   Exited (1) 17 months ago             elated_taussig
admin@i-0d07b2079856860d3:~/app$ sudo docker logs 124a4fb17a1c
node:internal/modules/cjs/loader:928
  throw err;
  ^

Error: Cannot find module '/usr/src/app/serve.js'
    at Function.Module._resolveFilename (node:internal/modules/cjs/loader:925:15)
    at Function.Module._load (node:internal/modules/cjs/loader:769:27)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:76:12)
    at node:internal/main/run_main_module:17:47 {
  code: 'MODULE_NOT_FOUND',
  requireStack: []
```

Là, il fallait être attentif au détail : Node tente d'exécuter `serve.js` alors que le fichier s'appelle `server.js` (une lettre en plus). 

On corrige le Dockerfile, on recrée l'image et on relance :

```console
root@i-0817bf54eaf7b54d1:/home/admin/app# docker build -t app .
Sending build context to Docker daemon  101.9kB
Step 1/7 : FROM node:15.7-alpine
 ---> 706d12284dd5
Step 2/7 : WORKDIR /usr/src/app
 ---> Using cache
 ---> 463b1571f18e
Step 3/7 : COPY ./package*.json ./
 ---> Using cache
 ---> acfb467c80ba
Step 4/7 : RUN npm install
 ---> Using cache
 ---> 5cad5aa08c7a
Step 5/7 : COPY ./* ./
 ---> 853722d2e8fc
Step 6/7 : EXPOSE 8880
 ---> Running in ef29a0a042f6
Removing intermediate container ef29a0a042f6
 ---> 509af769a64d
Step 7/7 : CMD [ "node", "server.js" ]
 ---> Running in 6c71c9461ed1
Removing intermediate container 6c71c9461ed1
 ---> f171ac81321b
Successfully built f171ac81321b
Successfully tagged app:latest
root@i-0817bf54eaf7b54d1:/home/admin/app# docker run -d app
be3744800d849d25d5a801c5a32f7a271d99b9b7bf02cb04620972e3bca10939
root@i-0817bf54eaf7b54d1:/home/admin/app# curl localhost:8888
these are not the droids you're looking for
```

Cette fois, on n'obtient pas le contenu espéré...

Le script est pourtant tout simple :

```js
var express = require('express'),
  app = express(),
  port = process.env.PORT || 8888,
  bodyParser = require('body-parser');

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.get('/', function (req, res) {
    res.send('Hello World!')
  })

app.use(function(req, res) {
    res.status(404).send({url: req.originalUrl + ' not found'})
  });

app.listen(port);

console.log('Server Started on: ' + port);
```

Ah, mais oui ! J'ai oublié de rendre le port du conteneur accessible. Actuellement le port est utilisé par un autre service :

```console
root@i-0817bf54eaf7b54d1:/home/admin/app# ss -lntp
State           Recv-Q          Send-Q                    Local Address:Port                     Peer Address:Port          Process                                                                                
LISTEN          0               128                             0.0.0.0:22                            0.0.0.0:*              users:(("sshd",pid=588,fd=3))                                                         
LISTEN          0               511                             0.0.0.0:8888                          0.0.0.0:*              users:(("nginx",pid=608,fd=6),("nginx",pid=607,fd=6),("nginx",pid=606,fd=6))          
LISTEN          0               4096                                  *:6767                                *:*              users:(("sadagent",pid=561,fd=7))                                                     
LISTEN          0               4096                                  *:8080                                *:*              users:(("gotty",pid=560,fd=6))                                                        
LISTEN          0               128                                [::]:22                               [::]:*              users:(("sshd",pid=588,fd=4))                                                         
LISTEN          0               511                                [::]:8888                             [::]:*              users:(("nginx",pid=608,fd=7),("nginx",pid=607,fd=7),("nginx",pid=606,fd=7))
```

Actuellement, on tape sur Nginx :

```console
root@i-0817bf54eaf7b54d1:/home/admin/app# cat /var/www/html/index.nginx-debian.html 
these are not the droids you're looking for
```

Du coup, je stoppe Nginx et relance Docker comme il faut :

```console
root@i-0817bf54eaf7b54d1:/home/admin/app# systemctl stop nginx
root@i-0817bf54eaf7b54d1:/home/admin/app# docker stop be3744800d84
be3744800d84
root@i-0817bf54eaf7b54d1:/home/admin/app# docker run -p 8888:8888 -d app
77a84a67da3fd733c38b59c5e1ea366cbf6a1b190cceaca50050ee767438b6af
root@i-0817bf54eaf7b54d1:/home/admin/app# curl localhost:8888
Hello World!
```
