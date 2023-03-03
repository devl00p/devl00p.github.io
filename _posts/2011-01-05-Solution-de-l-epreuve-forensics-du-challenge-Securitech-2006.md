---
title: "Solution de l'épreuve forensics du challenge Securitech 2006"
tags: [Computer forensics]
---

Dans le jargon informatique, les analyses post-mortem ou plus simplement *"analyses après intrusions"* (en anglais [Computer forensics](http://en.wikipedia.org/wiki/Computer_forensics)) sont l'ensemble des techniques visant à récolter les preuves d'une activité illégale sur un système informatique.  

Ce domaine est en pleine croissance et les sites dédiés à ce sujet commencent à fleurir sur la toile, preuve que l'efficacité des techniques de sécurisation reste très relative et que le nombre d'attaques va croissant.  

Le forensics n'est pas seulement utilisé pour étudier les intrusions indésirables, mais aussi pour les intrusions désirables ([honeypots](http://en.wikipedia.org/wiki/Honeypot_(computing))), afin de se tenir au courant des dernières techniques ou [exploits](http://en.wikipedia.org/wiki/Security_exploit) en vogue.  

C'est aussi un sujet épineux puisque techniquement délicat (essayez d'analyser l'intérieur d'un objet sans y mettre les doigts) et en rapport direct avec la connaissance des systèmes de fichiers (sujet à troll).  

Mais ce qui est sûr, c'est que c'est un sujet passionnant et que sa pratique nous apprend tout un tas de choses intéressantes.  

Pour cette épreuve du _Securitech_ de cette année, on nous donnait une image vmware d'un système linux récemment piraté.  

On nous donnait quelques axes de recherches par le biais des 3 questions suivantes :  

* Quel est le chemin absolu de l'exécutable ayant permis à l'intrus d'entrer sur le système ?
* Quel sont les coordonnées du pirate où sont envoyées des informations concernant le système ?
* Quelle est la commande détournée (backdoor) permettant au pirate de reprendre possession du système ?

L'analyse que je fais dans ce billet est une analyse "après-coup" dans le sens où il m'a fallu du temps avant de trouver quelque chose d'intéressant et que je ne vais pas énumérer tous les tests que j'ai effectué au début.  

L'une des étapes par lesquelles je suis passé consistait à installer des binaires propres sur le système afin d'analyser l'activité en cours. En effet, le pirate ayant probablement installé un [rootkit](http://fr.wikipedia.org/wiki/Rootkit), on ne peut pas accorder de confiance au système...  

Parmi les programmes installés dans cette étape, il y avait les commandes de bases (coreutis) et les commandes de recherche de fichiers (findutils) ainsi que [iproute2](http://linux-net.osdl.org/index.php/Iproute2) et [listps](http://csl.sublevel3.org/listps/).  

L'échec de cette étape nous indiquait que soit le pirate avait installé une rookit au niveau du noyau, soit qu'il était particulièrement rusé pour cacher sa présence (soit les deux).  

![](/assets/img/forensics_sec2006.jpg)

Quand on ouvre l'image vmware on tombe nez à nez avec une jolie ange/démone sur un système Debian avec WindowMaker.  

Deux xterm sont ouverts, montrant l'usage de [PeerCast](http://fr.wikipedia.org/wiki/PeerCast) et de `ogg123`.  

Ces informations ne sont sûrement pas là innocemment, mais pour le moment on ne peut pas en dire davantage.  

En revanche ce qu'il y a de plus choquant, c'est ce sudo qui n'en fait qu'à sa tête :  

![Securitech Sudo](/assets/img/securitech_sudo.jpg)

On pense tout de suite à l'utilisation d'un faux sudo destiné à capturer le mot de passe de l'utilisateur...  

J'ai étudié le path, lancé quelques strings sur sudo, bash et les librairies PAM mais je n'y ai rien vu de choquant (ça m'aura tout de même fait découvrir [les insultes intégrées à sudo](http://www.wlug.org.nz/FunnyApplicationErrorMessages))  

Pour vérifier l'hypothèse que ce problème était lié à bash j'ai lancé 'sh' et lancé un sudo qui s'est exécuté sans erreurs...  

J'ai analysé vite fait les `.bashrc` et `.bash_profile` sans rien y voir d'intéressant. Pourtant, si j'avais pris mon temps j'aurais sans aucun doute vu le nombre de lignes vides impressionnantes dans le `.bashrc`, mais j'y reviendrais tout à l'heure.  

C'est en tapant la commande 'alias' que j'ai eu l'apparition suivante :

```bash
alias sudo='~/\ '
```

Le pirate a créé un fichier dont le nom est composé d'un espace unique, l'objectif étant de le rendre plus ou moins invisible à un `ls`.  

L'analyse de ce binaire nous apprend beaucoup de choses :  

Différentes commandes sont exécutées afin d'obtenir des informations sur le système. Parmi ces commandes se trouvent whoami, netstat et uname. Les résultats de ces commandes sont mises dans un buffer et envoyées par HTTP à un script php (`recup_data.php`) avant d'être envoyées une nouvelle fois au pirate par le biais du protocole SMTP.  

L'adresse du destinataire n'était pas évidente à récupérer, car le nom d'utilisateur n'était pas explicite (bien qu'en clair dans le code) et le nom de domaine du serveur smtp était lui encrypté.  

La méthode simple pour récupérer ces informations consistait à exécuter le binaire dans un autre environnement et à sniffer la communication.  

Par la suite j'ai repris l'image vmware originale, installé un [netcat](http://www.vulnwatch.org/netcat/) compilé statiquement et copié le disque vers ma machine.  

Sous vmware :

```bash
dd if=/dev/sda1 | ./nc-static 192.168.0.3 8080
```

Sur ma machine :

```bash
netcat -l -p 8080 -v > disk.img
```

Le transfert m'a pris beaucoup de temps et à échoué la première fois  

Je suis passé aux choses sérieuses en installant [The Sleuth Kit](http://www.sleuthkit.org/sleuthkit/) sur ma machine.  

Ce kit est équipé d'un ensemble de commandes qui permettent d'analyser efficacement l'image d'un disque, sa création est clairement destinée aux analyses forensics.  

Les seuls [outils](http://www.sleuthkit.org/sleuthkit/tools.php) de TSK dont je me suis servi sont :  

* `fls` (liste les fichiers présents sur le disque, y compris les fichiers effacés)
* `icat` (extrait le contenu d'un fichier)
* `mactime` (permet de recréer un historique des fichiers ouverts/modifiés/créés)

`fls` génère une sortie où chaque ligne correspond à un fichier, par exemple :  

```
0|/etc/init.d/exim4|0|766622|33261|-/-rwxr-xr-x|1|0|0|0|3888|1146225760|1117180771|1145825532|4096|0
```

Ce n'est pas super agréable comme lecture (surtout avec un fichier de 28970 lignes) donc on filtre avec `grep` et on scrolle sur les endroits qui nous intéressent.  

`mactime` utilise l'output de fls pour générer sa chronologie, les résultats sont bien plus intéressants, par exemple le 28 avril 2006 à 14h26 :  

```
Fri Apr 28 2006 14:26:12   510089 ..c -/-rwxr-xr-x 1000     1000     896288   /home/jmerchat/
                           510089 ..c -/-rwxr-xr-x 1000     1000     896288   /home/jmerchat/sudo (deleted-realloc)
Fri Apr 28 2006 14:27:39       67 m.. -/-rw-r--r-- 1000     1000     896289   /home/jmerchat/WDI.pls
Fri Apr 28 2006 14:28:15    55340 .a. -/-rwxr-xr-x 0        0        456116   /bin/mv
```

On voit clairement que le pirate avait d'abord installé le passlogger sous le nom sudo et qu'il a ensuite tapé  

```bash
mv sudo ' '
```

On en déduit qu'à ce moment de la journée, il n'a encore que des droits limités... allons un peu plus loin :  

```
Fri Apr 28 2006 14:42:42    98156 .a. -/-rwxr-xr-x 0        0        456117   /bin/netstat
                            12536 .a. -/-rwxr-xr-x 0        0        51161    /usr/bin/whoami
Fri Apr 28 2006 14:42:51   510089 .a. -/-rwxr-xr-x 1000     1000     896288   /home/jmerchat/sudo (deleted-realloc)
                           510089 .a. -/-rwxr-xr-x 1000     1000     896288   /home/jmerchat/
```

À 14h42, l'utilisateur `jmerchat` est tombé dans le piège tendu par le pirate, le mot de passe lui est donc envoyé (au pirate) par les moyens que l'on connait.  

Maintenant que le pirate peut passer root, voyons quelles vont être ses futures actions :  

```
Fri Apr 28 2006 14:49:45       10 .a. l/lrwxrwxrwx 0        0        49503    /usr/bin/touch -> /bin/touch
                            15500 .a. -/-rwxr-xr-x 0        0        912145   /var/cache/apt/aptutils.cache
                             4096 m.c d/drwxr-xr-x 0        0        912132   /var/cache/apt
                              958 ..c -/-rwxr-xr-x 0        0        766638   /etc/init.d/modutils
                            30360 .a. -/-rwxr-xr-x 0        0        456133   /bin/touch
Fri Apr 28 2006 14:49:46    15500 m.c -/-rwxr-xr-x 0        0        912145   /var/cache/apt/aptutils.cache
Fri Apr 28 2006 14:49:47     8284 .a. -/-rwxr-xr-x 0        0        766480   /etc/cron.weekly/man-db (deleted-realloc)
                             8284 .a. -/-rwxr-xr-x 0        0        766480   /etc/nologin (deleted-realloc)
                            13680 .a. -/-rw-r--r-- 0        0        766469   /etc/modutils.cache
                             6192 .a. -/-rwxr-xr-x 0        0        325817   /sbin/insmod
                            13680 .a. -/-rw-r--r-- 0        0        766469   /etc/cron.daily/man-db (deleted-realloc)
                             8284 .a. -/-rwxr-xr-x 0        0        766480   /etc/fileutils.cache
```

De toute évidence, il fait appel à la commande `touch` pour modifier les dates de différents fichiers. On remarque que le nom de ces fichiers se termine par `utils.cache`.  

On voit quelque chose de TRES intéressant : l'utilisation de la commande insmod pour charger un module du noyau !  

```
Fri Apr 28 2006 14:49:48   340608 mac -/-rw-rw-r-- 0        43       913919   /var/log/.wtmp.EVOsc3 (deleted-realloc)
                           258811 .a. -/-rw-r----- 0        4        913890   /var/log/kern.log
                          1013800 m.c -/-rw-r--r-- 1000     1000     146606   /tmp/peercast.2598.log
                           270522 .a. -/-rw-r----- 0        4        913908   /var/log/syslog
                           340608 mac -/-rw-rw-r-- 0        43       913919   /var/log/wtmp
                           203780 .a. -/-rw-r----- 0        4        913904   /var/log/messages
                            11622 .a. -/-rw-r----- 0        4        913879   /var/log/auth.log
Fri Apr 28 2006 14:49:49        0 mac -/-rw-r--r-- 0        0        146611   /tmp/syslog.hm (deleted)
                                0 mac -/-rw-r--r-- 0        0        146612   /tmp/kern.log.hm (deleted)
                                0 mac -/-rw-r--r-- 0        0        146609   /tmp/messages.hm (deleted)
                            18828 .a. -/-rwxr-xr-x 0        0        51152    /usr/bin/wc
                                0 mac -/-rw-r--r-- 0        0        146610   /tmp/auth.log.hm (deleted)
                            23160 .a. -/-rwxr-xr-x 0        0        50809    /usr/bin/cut
```

Je ne sais pas vous, mais moi j'appelle ça effacer ses traces.  

Pour terminer il semble effacer quelques fichiers et rends très certainement le `.bash_history` immuable (avec la commande `chattr`) afin que bash n'ajoute pas de lignes à l'historique des commandes.  

```
Fri Apr 28 2006 14:52:29    30712 .a. -/-rwxr-xr-x 0        0        456123   /bin/rm
Fri Apr 28 2006 14:52:43    13680 ..c -/-rw-r--r-- 0        0        766469   /etc/modutils.cache
                            13680 ..c -/-rw-r--r-- 0        0        766469   /etc/cron.daily/man-db (deleted-realloc)
Fri Apr 28 2006 14:52:49     8284 ..c -/-rwxr-xr-x 0        0        766480   /etc/fileutils.cache
                             6116 .a. -/-rw-r--r-- 0        0        163189   /lib/libcom_err.so.2.1
                            19184 .a. -/-rw-r--r-- 0        0        163195   /lib/libe2p.so.2.3
                             8284 ..c -/-rwxr-xr-x 0        0        766480   /etc/cron.weekly/man-db (deleted-realloc)
                               13 .a. l/lrwxrwxrwx 0        0        162899   /lib/libe2p.so.2 -> libe2p.so.2.3
                               17 .a. l/lrwxrwxrwx 0        0        162892   /lib/libcom_err.so.2 -> libcom_err.so.2.1
                             8284 ..c -/-rwxr-xr-x 0        0        766480   /etc/nologin (deleted-realloc)
                             7636 .a. -/-rwxr-xr-x 0        0        50790    /usr/bin/chattr
Fri Apr 28 2006 14:53:34     8545 m.c -/-rw------- 1000     1000     896209   /home/jmerchat/.bash_history
```

Passons à l'analyse de ces fichiers `utils.cache`...  

Pour les extraire il nous faut utiliser la commande `icat` avec le numéro d'inode du fichier, par exemple :  

```bash
icat disk.img 912145 > /var/cache/apt/aptutils.cache
```

La commande file nous renseigne sur la nature de ces fichiers :  

```
aptutils.cache: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.0, dynamically linked (uses shared libs), for GNU/Linux 2.2.0, not stripped
modutils.cache: ELF 32-bit LSB relocatable, Intel 80386, version 1 (SYSV), not stripped
fileutils.cache: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.0, dynamically linked (uses shared libs), for GNU/Linux 2.2.0, stripped
```

En d'autres termes, on a deux exécutables et un module (.ko)  

Voici un extrait du `strings` sur `fileutils.cache` qui se passe de commentaires :

```
powered by click
        if you want to hide yourself and clean log files:
        usage %s <user> <host> <real_ip>
         if you want to change ip host user and clean logs:
        usage %s <user> <fake_user> <fake_host> <host> <real_ip>
/var/log/messages
/var/log/secure
/var/log/xferlog
/var/log/maillog
/var/log/proftpd.log
/var/log/auth.log
/var/log/syslog
/var/log/kern.log
messages.hm
secure.hm
xferlog.hm
maillog.hm
proftpd.log.hm
auth.log.hm
syslog.hm
kern.log.hm
```

La même opération sur `aptutils.cache` est plus intéressante :  

```
You need root level (to use raw sockets).
Utility to connect reverse shell from engelmickey:
%s ip_dest [port]
error creating socket.
* Launching reverse_shell:
Waiting shell on port %d (it may delay some seconds) ...
launching shell ...
ENGELKMICKEY
Sending ICMP ...
error sending data.
```

et enfin sur `modutils.cache` :

```
sk_del_node_init
license=GPL
vermagic=2.6.8 preempt 686 gcc-3.3
depends=
utils.cache
#<debconf_DSA_1297>
#</debconf_DSA_1297>
validnivo
include/linux/crypto.h
Cannot allocate crypto_tfm
/bin/bash
--noprofile
--norc
TERM=linux
HOME=/
HISTFILE=/dev/null
ENYELKMICMPKEY
/dev/ptmx
/dev/pts/%d
utils.cache
PATH=/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/local/sbin
usbkhd
```

Ce cher rootkit se cacherait sous le nom `usbkhb`... Si on retourne sous vmware elle n'apparait nulle part dans un `lsmod` ou dans `/proc/modules`... en revanche elle est présente dans `/sys/modules`  

On retrouve deux chaines quasi-similaires dans le reverse shell et le module (respectivement `ENGELKMICKEY` et `ENYELKMICMPKEY`), preuve qu'ils sont liés par leur fonctionnement.  

Il y a aussi la chaine `utils.cache` qui nous prouve bien que cette chaine est utilisée pour cacher un fichier et enfin un `validnivo` qui attire l'œil et deux balises étranges (`debconf_DSA_1297`).  

Revenons sur `ENYELKMICMPKEY`. On peut le décomposer en `ENYE LKM ICMP KEY`. Après une recherche sur Google on retrouve [la rootkit originale](http://www.enye-sec.org/index2.html) utilisée pour l'épreuve et ainsi son code source qui va nous être d'une grande utilité.  

Par exemple le reverse shell installé ne fonctionne pas ? On prend la source de la lkm, on compile (`make conectar`), on lance et paf ! Un shell root.  

C'est marrant, mais ce qui nous intéresse, c'est ce `validnivo` de tout à l'heure et aussi la possibilité de répondre aux questions...  

Dans la doc de `ENYELKM v1.1` on a l'info suivante :  

```
* Consiguiendo root local:

Haciendo: # kill -s 58 12345
se consigue id 0.
```

Notre pirate a dû modifier les paramètres par défaut avant compilation puisque cette commande ne donne pas l'UID 0.  

Une seule solution : désassembler le rootkit et étudier son code.
Après quelques recherches je trouve une commande qui semble appropriée :  

```bash
objdump -dr modutils.cache
```

La partie qui nous intéresse est :

```nasm
000002e0 :
 2e0: 83 ec 0c sub $0xc,%esp
 2e3: b8 00 e0 ff ff mov $0xffffe000,%eax
 2e8: 8b 4c 24 10 mov 0x10(%esp),%ecx
 2ec: 89 5c 24 08 mov %ebx,0x8(%esp)
 2f0: 8b 5c 24 14 mov 0x14(%esp),%ebx
 2f4: 21 e0 and %esp,%eax
 2f6: 81 f9 43 ba 00 00 cmp $0xba43,%ecx
 2fc: 8b 10 mov (%eax),%edx
 2fe: 74 15 je 315 <hacked_kill+0x35>
 300: 89 5c 24 04 mov %ebx,0x4(%esp)
 304: 89 0c 24 mov %ecx,(%esp)
 307: ff 15 00 00 00 00 call *0x0
 309: R_386_32 orig_kill
 30d: 8b 5c 24 08 mov 0x8(%esp),%ebx
 311: 83 c4 0c add $0xc,%esp
 314: c3 ret
 315: b8 24 00 00 00 mov $0x24,%eax
 31a: 39 d8 cmp %ebx,%eax
 31c: 75 e2 jne 300 <hacked_kill+0x20>
 31e: 31 c0 xor %eax,%eax
 320: 31 db xor %ebx,%ebx
 322: 31 c9 xor %ecx,%ecx
 324: 89 82 d0 01 00 00 mov %eax,0x1d0(%edx)
 32a: 31 c0 xor %eax,%eax
 32c: 89 82 e4 01 00 00 mov %eax,0x1e4(%edx)
 332: 31 c0 xor %eax,%eax
 334: 89 9a d4 01 00 00 mov %ebx,0x1d4(%edx)
 33a: 89 8a e0 01 00 00 mov %ecx,0x1e0(%edx)
 340: eb cb jmp 30d <hacked_kill+0x2d>
```

On retrouve deux `cmp` avec des valeurs fixes : `0xba43` et `0x36` soit 47683 et 36 en décimal.  

![Securitech Rootkit](/assets/img/securitech_rootkit.jpg)

On a maintenant la réponse à la question sur l'accès dérobé.  

L'étude de la rootkit nous révèle l'existence de deux fonctions nommées `analyse_challenge_vn` et `vn` qui sont à priori là pour nous donner un validateur.  

Le seul appel à `analyse_challenge_vn` se fait par la fonction `hide_marcas`.  

En analysant le rootkit original, on retrouve à quoi correspond cette fonction :  

```
* Ocultar partes de un fichero:

Se oculta en un fichero todo lo que este entre las marcas:
(marcas incluidas)

#<OCULTAR_8762>
texto a ocultar
#</OCULTAR_8762>
```

J'enregistre le fichier, je fais un `cat` en espérant trouver le validateur, mais le fichier est vide... c'est pas ça...  

J'analyse la fonction vn et j'y vois :

```nasm
     fd9:       e8 fc ff ff ff          call   fda <vn+0x28a>
                        fda: R_386_PC32 printchars
     fde:       8d 44 24 20             lea    0x20(%esp),%eax
     fe2:       89 04 24                mov    %eax,(%esp)
     fe5:       e8 fc ff ff ff          call   fe6 <vn+0x296>
                        fe6: R_386_PC32 printchars
     fea:       c7 04 24 81 00 00 00    movl   $0x81,(%esp)
                        fed: R_386_32   .rodata.str1.1
     ff1:       8b 84 24 0c 05 00 00    mov    0x50c(%esp),%eax
     ff8:       89 44 24 04             mov    %eax,0x4(%esp)
     ffc:       e8 fc ff ff ff          call   ffd <vn+0x2ad>
                        ffd: R_386_PC32 printk
```

Le résultat passe apparemment par `printk`. Un petit `dmesg` et je retrouve effectivement un lien et un code à entrer sur le site du challenge.  

Il ne nous reste plus qu'à trouver l'application faillible qui a permise au pirate d'accéder au système la première fois... Une étude des logs ne donne pas grand-chose d'intéressant du côté d'apache ou exim4... 

Le journal de `peercast` disponible par l'interface web (port 7144) ainsi qu'un fichier de stats xml montre quelques caractères étranges qui correspondent au message de fichier corrompu que l'on peut lire dans le xterm...  

Le problème, c'est qu'au niveau des dates récoltées par `mactime` on n'obtient pas de correspondances intéressantes... mais l'administrateur semble avoir changé la date du système à plusieurs reprises, ce qui pourrait éventuellement expliquer le décalage.  

J'ai essayé de retrouver la présence d'un shellcode dans la mémoire des processus `peercast` à l'aide de `memfetch` de [Michal Zalewski](http://lcamtuf.coredump.cx/) mais une nouvelle fois, je n'ai obtenu aucune preuve explicite.  

J'ai donc validé la dernière question sur des suppositions et ça a été accepté.  

Si quelqu'un a trouvé quelque chose de solide, je suis preneur.  

Au final, j'ai appris beaucoup de trucs, notamment en me servant de _Sleuth Kit_ et le désassemblage d'un module était aussi nouveau pour moi.  

Ce sera aussi l'épreuve qui m'aura couté le plus puisque j'ai du acheté une barrette de 512 Mo de RAM pour pouvoir faire fonctionner vmware... mais je ne le regrette pas.

*Published January 05 2011 at 15:45*
