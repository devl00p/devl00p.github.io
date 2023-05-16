---
title: "Solution du CTF FourAndSix #1 de VulnHub"
tags: [CTF, VulnHub]
---

[FourAndSix #1](https://vulnhub.com/entry/fourandsix-1,236/) était un CTF vraiment bizarre. On tombe sur un fichier qui laisse supposer un chemin à prendre qui s'annonce passionnant, mais finalement l'exploitation se fait sans péril et sans gloire.

J'aurais bien touché deux mots à l'auteur du CTF, [Fred Wemeijer](https://vulnhub.com/author/fred-wemeijer,595/), pour vérifier la solution attendue, mais je n'ai pas trouvé de façon de le contacter.

```
Nmap scan report for 192.168.56.204
Host is up (0.00027s latency).
Not shown: 48180 closed tcp ports (reset), 17351 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.7 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.7: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
|       EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    5.0     https://vulners.com/exploitpack/EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    *EXPLOIT*
|       EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    5.0     https://vulners.com/exploitpack/EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    *EXPLOIT*
|       EDB-ID:45939    5.0     https://vulners.com/exploitdb/EDB-ID:45939      *EXPLOIT*
|       EDB-ID:45233    5.0     https://vulners.com/exploitdb/EDB-ID:45233      *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2018-15473  5.0     https://vulners.com/cve/CVE-2018-15473
|       1337DAY-ID-31730        5.0     https://vulners.com/zdt/1337DAY-ID-31730        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS-        0.0     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS- *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
111/tcp  open  rpcbind 2 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2            111/tcp   rpcbind
|   100000  2            111/udp   rpcbind
|   100003  2,3         2049/tcp   nfs
|   100003  2,3         2049/udp   nfs
|   100005  1,3          729/udp   mountd
|_  100005  1,3          948/tcp   mountd
948/tcp  open  mountd  1-3 (RPC #100005)
2049/tcp open  nfs     2-3 (RPC #100003)
```

Donc on voit qu'il y a NFS qui est présent. Avec `showmount` on peut lister les exports :

```console
$ showmount -e 192.168.56.204
Export list for 192.168.56.204:
/shared (everyone)
$ sudo mount 192.168.56.204:/shared/ /mnt/
Created symlink /run/systemd/system/remote-fs.target.wants/rpc-statd.service → /usr/lib/systemd/system/rpc-statd.service.
$ sudo ls -al /mnt/
total 1042
drwxrwxrwx 2 root root     512 29 avril  2018 .
drwxr-xr-x 1 root root     176 27 févr.  2022 ..
-rw-r--r-- 1 root root 1048576 29 avril  2018 USB-stick.img
```

Je trouve une image de disque qui est formatée en FAT :

```console
$ file USB-stick.img
USB-stick.img: DOS/MBR boot sector, code offset 0x3c+2, OEM-ID "mkfs.fat", sectors/cluster 4, root entries 512, sectors 2048 (volumes <=32 MB), Media descriptor 0xf8, sectors/FAT 2, sectors/track 32, heads 64, reserved 0x1, serial number 0x286d9961, unlabeled, FAT (12 bit)
```

Si je monte l'image sur ma machine je ne trouve que quelques images d'*Hello Kitty*.

À l'aide d'un éditeur hexadécimal je peux regarder si d'autres données sont présentes dans l'image disque et il y a effectivement une clé privée SSH altérée :

```
-----BEGIN RSA PRIVATE KEY-----
HAHAHAHAiAAAAAAAAAAAAAAAAADAMAGED6LDKNWPuXsSdrjdUkNviYiUIZFZBm28
qcUNWoyUFBHQNHwxuRlak0ouh2o0xpKVyhB8/vf/lmUbUWqdCurd1M5H09zX+fU3
zeDgiiaLfi0IoaeTmZeWpM34+22RsDpKOiyWzsomud+LjdqRAyKEK0adJVVPPVoY
ylOnpahb1k1KfUB7Ucl/Gp0E59MUX95VhMVDrIF1GGV+yHF1cjj+PbRJ0lRDg4zI
60Xl+nvGq6sD/KpLREDMlOvkuCl3NrYZrMHH2lklVrtBC3EauFhA8QRjfymDFYPy
7GfpAJRWlLNeMZk0TiYqLzsBTrh5S51U11mpwQIDAQABAoIBADsNYIXm26ZslWOb
etj+zFSe60+FBJg6Aeo3fV6FdK3pDnxmd/fpPLmgs/N7M4J72FjS8jgQX6GKVsCM
o4TLmDueiICSevsZT8XYEczth58Yy0zgEnSU0zmd1no68XLyBuhJBLj62PukG5jY
VNEb270JiFF+se4RnOeJRnDRJ5A58ZvJDkO9GdB1xdugkddVdrha8B1dECO1qn9M
enpbz3wc/N6SWeFxQ7gAKXubw80KYSx3n1W3frWS5EzdmHFZBvYvpBLLh417VNoE
F6m3cy+CcVwsVjgdQ7AkVF8Pn4WOKN9Epv3YFwE4Y8FtR/xHi4aZc+e2luRoeX65
ezd6LeUCgYEA/oRmiG1RswByZHYjdI1PzVv3P57+6Dtw+K9thG/ZkrRb+PcDcwup
```

Il y a aussi la clé publique SSH au complet :

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD6gjSEWyoPnQl3CpifosMo1Y+5exJ2uN1SQ2+JiJQhkVkGbbypxQ1ajJQUEdA0fDG5GVqTSi6HajTGkpXKEHz+9/+WZRtRap0K6t3UzkfT3Nf59TfN4OCKJot+LQihp5OZl5akzfj7bZGwOko6LJbOyia534uN2pEDIoQrRp0lVU89WhjKU6elqFvWTUp9QHtRyX8anQTn0xRf3lWExUOsgXUYZX7IcXVyOP49tEnSVEODjMjrReX6e8arqwP8qktEQMyU6+S4KXc2thmswcfaWSVWu0ELcRq4WEDxBGN/KYMVg/LsZ+kAlFaUs14xmTROJiovOwFOuHlLnVTXWanB user@fourandsix
```

Est-il possible de reconstruire la partie manquante ? Oui ! En effet l'ASCII armor encodé en base64 contient différentes informations indiquant le cryptogramme utilisé.

Tout est décrit dans cette page [The OpenSSH Private Key Format](https://coolaj86.com/articles/the-openssh-private-key-format/).

Ça commence comme ceci :

```
"openssh-key-v1"0x00    # NULL-terminated "Auth Magic" string
32-bit length, "none"   # ciphername length and string
32-bit length, "none"   # kdfname length and string
32-bit length, nil      # kdf (0 length, no kdf)
32-bit 0x01             # number of keys, hard-coded to 1 (no length)
32-bit length, sshpub   # public key in ssh format
```

Par exemple si je décode le base64 de ma clé privée SSH ça commence comme ça :

```
openssh-key-v1\x00\x00\x00\x00\naes256-ctr\x00\x00\x00\x06bcrypt
```

Sur la clé SSH altérée on devrait avoir au plus court quelque chose comme ça :

```
openssh-key-v1\0\0\0\0\0none\0\0\0\0none\0
```

Soit la chaine suivante en base64 :

```
b3BlbnNzaC1rZXktdjFcMFwwXDBcMFwwbm9uZVwwXDBcMFwwbm9uZVww
```

On voit qu'elle est bien plus grande que les 33 caractères écrasés. De plus sur la clé altérée les caractères qui sont censés faire vraiment partie de la clé se décodent seulement en du charabia alors qu'on devrait trouver le `ciphername` et `kdfname`.

Ça semble donc être une fausse piste. Vraiment dommage, car il y aurait eu de quoi s'amuser.

Au lieu de ça on pouvait monter via NFS la racine du système bien qu'elle n'apparaissait pas dans les exports.

On pouvait alors lire le flag final :

```console
$ cat /mnt/root/proof.txt
904b4a46b21bbf13dbe53d21a3cd024f
```

Vraiment dommage.
