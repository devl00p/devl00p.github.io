---
title: "Ext2 et les effacements sécurisés"
tags: [Computer forensics]
---

Dans [ma solution de l'épreuve forensics du challenge Securitech 2006]({% link _posts/2011-01-05-Solution-de-l-epreuve-forensics-du-challenge-Securitech-2006.md %}), vous avez peut-être été étonné de savoir à quel point il était aisé d'étudier une image d'un disque et d'en extraire des données, ce même si les fichiers ont été effacés.  

La question que l'on peut se poser est *"Pourquoi des mesures n'ont pas été prises au niveau des systèmes d'exploitation pour garantir une suppression efficace des données ?"*  

Personnellement je vois deux réponses. La première est tout simplement que si l'effacement sécurisé peut-être considéré comme une caractéristique utile (voire nécessaire), la possibilité de pouvoir récupérer des données malencontreusement effacées est toute aussi importante (et à surement sauvé un bon nombre de personnes).  

La seconde réponse pourrait être l'existence d'un lobby puissant qui a tout intérêt à ce que les particuliers n'aient pas de moyens d'effacer leurs données les plus sensibles (organisations gouvernementales etc).  

Vous avez peut-être entendu parler de cette rumeur de backdoor dans *Windows Vista* demandée par le gouvernement britannique et qui lui aurait permis de passer à travers les systèmes de cryptage inclus dans le prochain Windows. Cette rumeur lancée par [le site de la BBC](http://news.bbc.co.uk/1/hi/uk_politics/4713018.stm) a très vite [été](http://www.theregister.co.uk/2006/02/17/vista_back_door_panic/) [démentie](http://www.theregister.co.uk/2006/03/06/nada_vista_backdoor/), mais à tout de même eu le temps de faire parler d'elle et de faire réfléchir.  

L'hypothèse que des pressions soient exercées sur Microsoft pour empêcher l'effacement sécurisé ne me parait si extraordinaire que ça...  

Linux propose bien une méthode d'effacement sécurisée par le biais de l'attribut `s` que l'on peut fixer avec la commande `chattr` (voir la page de manuel).  

Afin de comprendre le fonctionnement du système de fichiers ext2, j'ai créé une petite partition sur un vieux disque et ai effectué mes tests en *"boîte noire"* à l'aide du live cd [grml](http://grml.org/) dont j'ai déjà parlé et qui contient différents outils d'analyse forensics ou de récupération de données.  

Après un `cfdisk` obligatoire, j'ai écrasé le contenu de la partition puis l'ai formaté en ext2 :  

```bash
dd if=/dev/zero of=/dev/hda1
mke2fs /dev/hda1
```

Cette opération me donne un système ext2 tout ce qu'il y a de plus standard (sans journalisation en plus).  

À l'aide de la commande strings qui extrait les chaines de caractères d'un fichier, on peut déjà connaître le contenu du disque :

```console
# strings /dev/hda1
lost+found
```

Créons maintenant un répertoire et un fichier. Ces données nous servirons de base pour la suite :

```console
# mount /dev/hda1 /mnt
# ls /mnt/
.  ..  lost+found
# mkdir /mnt/mondir
# umount /mnt
# strings /dev/hda1
lost+found
mondir

# echo "ceci est un test" > /mnt/mondir/fichier.txt
# strings /dev/hda1
lost+found
mondir
ceci est un test
fichier.txt
```

Lors de mes tests, j'ai passé beaucoup de temps à démonter puis remonter le système de fichier... pour gagner de la place, je ne marque pas les commandes mount et umount qui seraient trop nombreuses.  

Utilisons les commandes du [SleuthKit](http://www.sleuthkit.org/sleuthkit/) pou avoir un aperçu des informations présentes sur le disque :

```console
# fls -r /dev/hda1
d/d 11: lost+found
d/d 1673:       mondir
+ r/r 1674:     fichier.txt
# fls -rm / /dev/hda1
0|/lost+found|0|11|16832|d/drwx------|2|0|0|0|12288|1149019267|1149019267|1149019267|1024|0
0|/mondir|0|1673|16877|d/drwxr-xr-x|2|0|0|0|1024|1149019487|1149019583|1149019583|1024|0
0|/mondir/fichier.txt|0|1674|33188|-/-rw-r--r--|1|0|0|0|17|1149019583|1149019583|1149019583|1024|0
# icat /dev/hda1 1674
ceci est un test
```

Notre `fichier.txt` possède le numéro d'inode 1674 et sa taille est de 17 octets.  

**Note :** En analyse forensic on peut classer les données contenues sur le disque en plusieurs catégories.  

* Les données concernant le système de fichier lui-même : sa structure, son type, les caractéristiques qu'il propose
* Le contenu des fichiers, organisées sous forme de blocks de taille fixe. Un block possède un état qui permet de savoir si un fichier l'utilise (allocated) ou s'il est libre pour créer un éventuel fichier (free ou unallocated)
* Les métadonnées (metadata) : ce sont les données qui décrivent un fichier. Sous Linux on parle d'_inode_. On y trouve les permissions, les dates de modification, dernier accès et changement d'état ainsi que les pointeurs vers les blocks de données que l'on a vu précédemment.
* La catégorie des noms de fichiers. Il s'agit principalement de structures décrivant les répertoires. On peut décrire un répertoire comme un tableau dont chaque entrée contient un nom de fichier, sa longueur (la longueur du nom, pas du fichier lui-même) et le numéro d'inode correspondant au fichier
* La catégorie applicative qui est la plupart du temps un fichier de journalisation. Cette catégorie ne nous intéresse pas puisque par défaut ext2 n'offre pas de système de journalisation

Les trois catégories ne nous retiendrons ici sont les noms de fichiers, les contenus des fichiers et enfin les métadonnées qui font le lien entre ces deux catégories.  

Passons maintenant à l'action et effaçons notre `fichier.txt` :  

```console
# rm /mnt/mondir/fichier.txt
# strings /dev/hda1
lost+found
mondir
ceci est un test
fichier.txt
```

À première vue le résultat est plutôt navrant puisque l'on retrouve le nom du fichier effacé ainsi que son contenu.  

Voyons ça de plus près :

```console
# fls -rm / /dev/hda1
0|/lost+found|0|11|16832|d/drwx------|2|0|0|0|12288|1149019267|1149019267|1149019267|1024|0
0|/mondir|0|1673|16877|d/drwxr-xr-x|2|0|0|0|1024|1149019777|1149019780|1149019780|1024|0
0|/mondir/fichier.txt (deleted)|0|0|0|-/----------|0|0|0|0|0|0|0|0|1024|0
# ils /dev/hda1
class|host|device|start_time
ils|shirley||1149020073
st_ino|st_alloc|st_uid|st_gid|st_mtime|st_atime|st_ctime|st_mode|st_nlink|st_size|st_block0|st_block1
1|a|0|0|1149019267|1149019267|1149019267|0|0|0|0|0
1674|f|0|0|1149019583|1149019583|1149019780|100644|0|17|9217|0
# icat /dev/hda1 1674
ceci est un test
```

La commande `fls` s'intéresse aux noms de fichiers, elle explore les tableaux de répertoires et est en mesure de détecter les fichiers qui ont été effacés.  

Comme écrit dans [Forensic Discovery](http://www.porcupine.org/forensics/forensic-discovery/) de *Wietse Venema* et *Dan Farmer*, la suppression d'un fichier a les conséquences suivantes sur la catégorie noms de fichiers :

> When a file is deleted, the directory entry with the file name and inode number is marked as unused. Typically, the inode number is set to zero, so that the file name becomes disconnected from any file information. (...)  
> 
> Names of deleted files can still be found by reading the directory with the strings command.

Nous avons donc perdu le lien entre le nom de fichier et ses métadonnées... heureusement la commande `ils` nous permet de récupérer la liste des inodes correspondant à des fichiers effacés.  

La commande `icat` quand à elle nous affiche le contenu du fichier correspondant à l'inode qui lui passe en paramètre.  

Le livre de _Venema_ et `Farmer` nous informe aussi que :  

> With 2.2 Linux kernels, the Linux Ext2fs (second extended) file system marks the directory entry as unused, but preserves the connections between directory entry, file attributes and file data blocks.

Autant dire que l'analyse forensics doit être très facile avec les noyaux 2.2... Heureusement pour nos données la situation a changé.  

Si l'on est parvenu à récupérer le contenu de notre fichier effacé avec icat, c'est parce que la taille du fichier est resté stocké sur le disque...  

Voyons ce qu'il se passe si on tronque le fichier avant de l'effacer. Pour cela j'ai écrit quelques lignes de code (trunc.c) :

```c
#include 
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc,char *argv[])
{
 int fd;
 if(argc!=2)exit(1);
 fd=open(argv[1],O_WRONLY);
 ftruncate(fd,0);
 close(fd);
 unlink(argv[1]);
 return 0;
}
```

On compile et on lance :

```console
# gcc -o trunc trunc.c -Wall -W -pedantic
# ./trunc /mnt/mondir/fichier.txt
# ils /dev/hda1
class|host|device|start_time
ils|shirley||1149021092
st_ino|st_alloc|st_uid|st_gid|st_mtime|st_atime|st_ctime|st_mode|st_nlink|st_size|st_block0|st_block1
1|a|0|0|1149020576|1149020576|1149020576|0|0|0|0|0
1674|f|0|0|1149021076|1149020953|1149021076|100644|0|0|0|0
# icat /dev/hda1 1674
#
# strings /dev/hda1
lost+found
mondir
Ceci est un test
fichier.txt
```

Cette fois la commande `icat` n'a pas pu récupérer le contenu du fichier. Mais le contenu du fichier est toujours lisible sur le disque. Un outil comme [foremost](http://foremost.sourceforge.net/) est tout à fait capable d'extraire des fichiers en se fiant uniquement à leur entête.  

Intéressons-nous maintenant au nom du fichier effacé toujours présent sur le disque. En repartant de notre base et en renommant deux fois le fichier avec des noms de même taille on obtient un résultat satisfaisant :

```console
# mv /mnt/mondir /mnt/xxxxxx
# strings /dev/hda1
lost+found
mondir
xxxxxx
fichier.txt
Ceci est un test
# mv /mnt/xxxxxx /mnt/zzzzzz
# strings /dev/hda1
lost+found
zzzzzz
xxxxxx
Ceci est un test
fichier.txt
```

Nous sommes sur la bonne voie. On retrouve en effet ces principes dans le code source de la commande d'effacement sécurisée `shred` ([shred.c](http://www.koders.com/c/fid4EDBE3714530C2E975A02A9FED285E47BF49EA45.aspx)).  

Le `ftruncate` est présent dans la fonction principale `do_wipefd`
La technique utilisée pour les noms de fichiers est en revanche différente (faites un `shred -u -v fichier` pour comprendre vite fait le mécanisme) :

```c
/*
* Repeatedly rename a file with shorter and shorter names,
* to obliterate all traces of the file name on any system that
* adds a trailing delimiter to on-disk file names and reuses
* the same directory slot.
*/
```

Attaquons-nous maintenant au contenu du fichier... une seule solution : écraser les données par d'autres données.

```console
# echo blahblah > /mnt/zzzzzz/fichier.txt
# strings /dev/hda1
lost+found
zzzzzz
xxxxxx
blahblah
fichier.txt
# perl -e "print 'A'x400" > /mnt/zzzzzz/fichier.txt
# strings /dev/hda1
lost+found
zzzzzz
AAAAA[...]AAAAA
fichier.txt
# echo blahblah > /mnt/zzzzzz/fichier.txt
# strings /dev/hda1
lost+found
zzzzzz
xxxxxx
blahblah
fichier.txt
# perl -e "print 'B'x4100" > /mnt/zzzzzz/fichier.txt
# strings /dev/hda1
lost+found
zzzzzz
BBBB[...]BBBBBB
fichier.txt
# echo blahblah > /mnt/zzzzzz/fichier.txt
# strings /dev/hda1
lost+found
zzzzzz
blahblah
BBBB[...]BBBBBB
fichier.txt
```

Les résultats semblaient satisfaisants au début... mais on s'aperçoit à la fin qu'il faut plus de données pour écraser la [slack space](http://en.wikipedia.org/wiki/Slack_space) et par conséquent l'ancien contenu du fichier.  

Tout à l'heure, je vous ai dit que le système gérait les données par blocks. Il ne peut pas manipuler chaque fichier à l'octet près, ce serait une énorme perte de temps.  

A la création d'un fichier le système va allouer plusieurs blocks de données. D'après mes tests Linux en réserve au minimum deux. Le code suivant permet de connaître l'espace mémoire réservé pour un fichier (`getstat.c`) :

```c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>

int main(int argc,char *argv[])
{
  struct stat mystat;
  if(argc!=2)exit(1);
  if(stat(argv[1],&mystat) < 0)exit(1);
  printf("Taille totale en octets: %d\nTaille de bloc pour E/S: %d\nNombre de blocs alloués: %d\n",
        mystat.st_size, mystat.st_blksize, mystat.st_blocks);
  return 0;
}
```

Voyons ce que ça donne :

```console
# echo blahblah > /mnt/zzzzzz/fichier.txt
# ./getstat /mnt/zzzzzz/fichier.txt
Taille totale en octets: 9
Taille de bloc pour E/S: 4096
Nombre de blocs alloués: 2
```

Conclusion : pour un fichier de seulement 9 octets, le système en a réservé 8192 (2 x 4096). Il est possible de fixer cette taille lors de la création de la partition ext2. 4096 semble être un bon compromis entre vitesse d'accès et gaspillage de place.  

Pour effacer de façon sûre notre fichier, il faut donc écraser ces deux blocks de 4096 octets, le renommer plusieurs fois et ramener sa taille à zéro avant de l'effacer...  

J'ai écrit le code suivant pour réaliser cette opération (`secrm.c`) :

```c
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libgen.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main(int argc,char *argv[])
{
  int fd;
  char *buff;
  char *path1;
  char *path2;
  int i;
  struct stat mystat;
  if(argc!=2)exit(1);
  if(stat(argv[1],&mystat)<0)exit(1);
  if(!S_ISREG(mystat.st_mode))exit(1);
  printf("Taille totale en octets: %d\nTaille de bloc pour E/S: %d\nNombre de blocs alloués: %d\n",
        mystat.st_size, mystat.st_blksize, mystat.st_blocks);
  buff=(char*)malloc(strlen(basename(argv[1])));
  path1=strdup(argv[1]);
  path2=strdup(argv[1]);
  memset(buff,'x',strlen(basename(path1)));
  sprintf(path1,"%s/%s",dirname(path1),buff);
  printf("filename -> %s\n",path1);
  link(argv[1],path1);
  unlink(argv[1]);
  memset(buff,'z',strlen(basename(path2)));
  sprintf(path2,"%s/%s",dirname(path2),buff);
  link(path1,path2);
  unlink(path1);
  printf("filename -> %s\n",path2);
  free(path1);
  free(buff);
  buff=(char*)malloc(mystat.st_blksize);
  fd=open(path2,O_WRONLY);
  printf("Overwriting...\n");
  for(i=0;i<mystat.st_blocks;i++)
  {
    memset(buff,i,mystat.st_blksize);
    write(fd,buff,mystat.st_blksize);
  }
  free(buff);
  printf("Truncating...\n");
  fsync(fd);
  ftruncate(fd,0);
  close(fd);
  printf("Unlinking...\n");
  unlink(path2);
  free(path2);
  printf("Done !\n");
  return 0;
}
```

On reprend notre base et on teste :

```console
# strings /dev/hda1
lost+found
mondir
Ceci est un test
fichier.txt
# ./secrm /mnt/mondir/fichier.txt
Taille totale en octets: 17
Taille de bloc pour E/S: 4096
Nombre de blocs alloués: 2
filename -> /mnt/mondir/xxxxxxxxxxx
filename -> /mnt/mondir/zzzzzzzzzzz
Overwriting...
Truncating...
Unlinking...
Done !
# strings /dev/hda1
lost+found
mondir
zzzzzzzzzzz
xxxxxxxxxxx
# fls -r /dev/hda1
d/d 11: lost+found
d/d 1673:       mondir
+ r/- * 0:      zzzzzzzzzzz
+ r/- * 0:      xxxxxxxxxxx
# ils /dev/hda1
class|host|device|start_time
ils|shirley||1149027322
st_ino|st_alloc|st_uid|st_gid|st_mtime|st_atime|st_ctime|st_mode|st_nlink|st_size|st_block0|st_block1
1|a|0|0|1149027164|1149027164|1149027164|0|0|0|0|0
1674|f|0|0|1149027269|1149027250|1149027269|100644|0|0|0|0
# icat /dev/hda1 1674
#
```

Mission accomplie !  

Évidemment toute implémentation en kernel land serait bien plus efficace...  

Sur le sujet des anti-forensics et de l'effacement sécurisé, la référence reste les travaux d'un certain *The Grugq*.  

Je vous conseille vivement *The Defiler's Toolkit* de sa création qui contient un code pour effacer les noms des fichiers effacés sur votre disque (`klismafile`) ainsi qu'un code qui va s'occuper des métadonnées (`necrofile`).  

Bibliographie :  

[File System Forensic Analysis](http://www.digital-evidence.org/fsfa/) de *Brian Carrier*  

[Forensic Discovery](http://www.porcupine.org/forensics/forensic-discovery/) de *Wietse Venema* et *Dan Farmer*  

[shred.c](http://www.koders.com/c/fid4EDBE3714530C2E975A02A9FED285E47BF49EA45.aspx) par *Colin Plumb*  

Secure Data Deletion for Linux File Systems  

The Ext2 File System sur The Linux Tutorial  

[Secure Deletion of Data from Magnetic and Solid-State Memory](http://www.cs.auckland.ac.nz/~pgut001/pubs/secure_del.html) de *Peter Gutmann*  

[Can Intelligence Agencies Read Overwritten Data? A repsonse to Gutmann.](http://www.nber.org/sys-admin/overwritten-data-guttman.html) de *Daniel Feenberg*  

[the grugq - secure deletion patch, kernel 2.4.24](http://lkml.org/lkml/2004/1/28/107)  

[Defeating Forensic Analysis on Unix](http://www.phrack.org/phrack/59/p59-0x06.txt) par *the grugq*

*Published January 06 2011 at 09:21*
