---
title: "Le système de fichiers Ext3"
tags: [Computer forensics]
---

Après [m'être attaqué à Ext2]({% link _posts/2011-01-06-Ext2-et-les-effacements-securises.md %}), je continue mes études des systèmes de fichiers en vous parlant cette fois de [Ext3](http://en.wikipedia.org/wiki/Ext3), un système de fichiers dont l'objectif était de combler les lacunes de la version précédente.  

On dit souvent qu'Ext3 n'est rien de plus qu'un Ext2 avec un système de [journalisation](http://en.wikipedia.org/wiki/Journaling_file_system).  

Pourtant, Ext3 apporte des améliorations en termes de vitesse d'accès aux données et permet le redimensionnement du système de fichier. Quelques changements sur la gestion des métadonnées ont aussi leur importance comme nous allons le voir.  

Mais avant de continuer il est important de comprendre ce qu'est un journal pour un système de fichiers.  

Quand on édite un fichier sur notre disque dur, le système d'exploitation effectue tout un tas d'opérations pour mettre à jour le système de fichiers. Par exemple si on ajoute des données à un fichier, le système va devoir allouer des blocks (rechercher des blocks libres disponibles), les marquer comme utilisés, y inscrire les données puis enfin mettre à jour les métadonnées (taille du fichier, pointeurs sur les blocks utilisés, dates de modification, accès etc).  

Imaginons qu'une panne d'électricité arrive en plein milieu de ces opérations : on pourrait très bien se retrouver avec des blocks marqués comme utilisés dans le système de fichiers, mais qui ne sont en réalité utilisés par aucuns fichiers... c'est donc de l'espace perdu.  

Heureusement le programme `fsck` se charge de chercher ce type d'erreurs pour nous... seulement vérifier l'intégralité du système de fichiers, c'est long ! C'est pour cela que l'on a créé la journalisation : à chaque modification du système de fichiers les opérations à effectuer sont enregistrées avant d'être effectuées.  

Après une panne d'électricité le système n'a qu'à regarder dans le journal quelles opérations il doit reprendre (ou annuler) pour s'assurer que tout fonctionne.  

Comme pour la dernière fois, j'ai effectué des tests en boîte noire, à l'aide du [SleuthKit](http://www.sleuthkit.org/sleuthkit/).  

Au lieu de créer une partition sur un disque dur, j'ai opté pour la création d'un fichier conteneur :  

```bash
dd if=/dev/zero of=ext3.img count=50000
mkfs.ext3 ext3.img
```

On obtient ainsi un système de fichier ext3 d'environ 25Mo. Regardons ce que le formatage nous a donné :  

```console
# ils -a ext3.img
class|host|device|start_time
ils|shirley||1151770485
st_ino|st_alloc|st_uid|st_gid|st_mtime|st_atime|st_ctime|st_mode|st_nlink|st_size|st_block0|st_block1
1|a|0|0|1151770448|1151770448|1151770448|0|0|0|0|0
2|a|0|0|1151770448|1151770448|1151770448|40755|3|1024|201|0
3|a|0|0|0|0|0|0|0|0|0|0
4|a|0|0|0|0|0|0|0|0|0|0
5|a|0|0|0|0|0|0|0|0|0|0
6|a|0|0|0|0|0|0|0|0|0|0
7|a|0|0|0|0|0|0|0|0|0|0
8|a|0|0|1151770448|0|1151770448|100600|1|1048576|214|215
9|a|0|0|0|0|0|0|0|0|0|0
10|a|0|0|0|0|0|0|0|0|0|0
11|a|0|0|1151770448|1151770448|1151770448|40700|2|12288|202|203
```

Cette commande nous permet d'afficher les inodes actuellement allouées (utilisées). Comment expliquer que 11 inodes soient déjà utilisées avant que l'on a créé aucun fichier ?  

La réponse est trouvable dans le fichier `/usr/include/linux/ext3_fs.h` :  

```c
/*
 * Special inodes numbers
 */
#define EXT3_BAD_INO             1      /* Bad blocks inode (blocks inutilisables) */
#define EXT3_ROOT_INO            2      /* Root inode (la racine / ) */
#define EXT3_BOOT_LOADER_INO     5      /* Boot loader inode */
#define EXT3_UNDEL_DIR_INO       6      /* Undelete directory inode */
#define EXT3_RESIZE_INO          7      /* Reserved group descriptors inode */
#define EXT3_JOURNAL_INO         8      /* Journal inode (le fameux journal de ext3) */
```

Les inodes 6, 7, 9 et 10 sont réservées pour un usage ultérieur (en prévision pour une prochaine version). Les inodes 3 et 4 sont utilisées pour stocker les [ACL](http://www.suse.de/~agruen/acl/linux-acls/online/) (un système de permissions plus évolué que le traditionnel user-group-others)  

L'inode 11 est utilisé par le répertoire `lost+found` caractéristique des systèmes Ext :  

```console
# fls -rm / ext3.img
0|/lost+found|0|11|16832|d/drwx------|2|0|0|0|12288|1151770448|1151770448|1151770448|1024|0
```

Montons maintenant le système de fichier et créons un fichier :  

```bash
mount -o loop ext3.img /mnt/
echo test > /mnt/fichier
umount /mnt
```

Observons le résultat avec `fls` (travaille au niveau des noms de fichiers) :  

```console
# fls -rm / ext3.img
0|/lost+found|0|11|16832|d/drwx------|2|0|0|0|12288|1151770448|1151770448|1151770448|1024|0
0|/fichier|0|12|33188|-/-rw-r--r--|1|0|0|0|5|1151770676|1151770676|1151770676|1024|0
```

`ils` nous renseigne sur les inodes :  

```console
# ils -a ext3.img
class|host|device|start_time
ils|shirley||1151770757
st_ino|st_alloc|st_uid|st_gid|st_mtime|st_atime|st_ctime|st_mode|st_nlink|st_size|st_block0|st_block1
1|a|0|0|1151770448|1151770448|1151770448|0|0|0|0|0
2|a|0|0|1151770676|1151770673|1151770676|40755|3|1024|201|0
3|a|0|0|0|0|0|0|0|0|0|0
4|a|0|0|0|0|0|0|0|0|0|0
5|a|0|0|0|0|0|0|0|0|0|0
6|a|0|0|0|0|0|0|0|0|0|0
7|a|0|0|0|0|0|0|0|0|0|0
8|a|0|0|1151770448|0|1151770448|100600|1|1048576|214|215
9|a|0|0|0|0|0|0|0|0|0|0
10|a|0|0|0|0|0|0|0|0|0|0
11|a|0|0|1151770448|1151770448|1151770448|40700|2|12288|202|203
12|a|0|0|1151770676|1151770676|1151770676|100644|1|5|5121|0
```

La dernière ligne concerne notre nouveau fichier :  

* son inode est 12
* l'inode est allouée (a)
* l'utilisateur propriétaire est root (uid 0)
* le groupe propriétaire est root (gid 0)
* les dates de modification, dernier accès, changement des métadonnées ont la même valeur
* l'inode est pointée par un seul lien (*"fichier"*)
* le fichier fait 5 octets
* Les deux dernières entrées permettent au système de retrouver les blocks où ont été enregistré le contenu du fichier.

Effaçons le fichier et observons le résultat :  

```console
# rm /mnt/fichier
# fls -rm / ext3.img
0|/lost+found|0|11|16832|d/drwx------|2|0|0|0|12288|1151770448|1151770448|1151770448|1024|0
0|/fichier (deleted)|0|12|33188|-/-rw-r--r--|0|0|0|0|0|1151770676|1151770861|1151770861|1024|0
```

Par rapport au fls précédent, on a perdu... la taille du fichier !  

```console
# ils ext3.img 12
class|host|device|start_time
ils|shirley||1151770996
st_ino|st_alloc|st_uid|st_gid|st_mtime|st_atime|st_ctime|st_mode|st_nlink|st_size|st_block0|st_block1
12|f|0|0|1151770861|1151770676|1151770861|100644|0|0|0|0
```

Au niveau de l'inode les changements sont radicaux : les adresses des blocks sont maintenant à 0.  

Contrairement à Ext2, nous ne pouvons pas récupérer le contenu du fichier à l'aide de la commande `icat`.  

Nos observations peuvent se retrouver sur [la page Wikipédia consacrée à Ext3](http://en.wikipedia.org/wiki/Ext3) :  

> Unlike ext2, ext3 zeroes out the block pointers in the inodes of deleted files. Because this removes all metadata for the affected files, the files cannot be recovered directly. The user's only recourse is to grep the hard drive for data known to signal the start and end of the file. This provides slightly more secure deletion than ext2, which can be either an advantage or a disadvantage.

Tout est dit ! Les données sont plus difficiles à extraire toutefois elles sont toujours présentes sur le disque. Différents outils existent comme [foremost](http://foremost.sourceforge.net/) qui se charge d'extraire les fichiers d'une partition en se fiant à leurs entête.  

Mais tout n'est pas finis !! Après tout Ext3 journalise les changements alors voyons ce qu'il y a dans ce fameux journal :  

```bash
icat ext3.img 8 > journal
hexdump journal
```

Malheureusement, c'est loin d'être la gloire... on retrouve tout de même quelques octets correspondants aux métadonnées du fichier :  

```plain
0001580 81a4 0000 0000 0000 a034 44a6 a0ed 44a6
0001590 a0ed 44a6 a0ed 44a6 0000 0000 0000 0000
00015a0 0000 0000 0000 0000 0000 0000 0000 0000
```

`0x44A6A034` est la valeur hexadécimale de `1151770676` (la date de dernière modification) et `0x81A4` devient `100644` en octal (les permissions sur le fichier). Seulement... ces informations concernent le fichier effacé et non le fichier avant sa suppression.

Impossible donc de récupérer l'ancienne inode.  

L'explication est lisible [ici](http://archives.free.net.ph/message/20060621.043510.faad11ed.en.html) : Ext3 utilise une journalisation dite physique et ne conserve que les modifications sur les blocks, contrairement à une journalisation logique qui enregistre les modifications sur les fichiers.  

Ne baissons pas les bras : nous allons récupérer le groupe de blocks sur lequel se trouve notre fichier afin de réduire le champ d'action pour la récupération des données.  
Nous utilisons la commande `imap` de `debugfs` qui nous renseigne sur l'inode qui nous intéresse (12) :  

```console
# debugfs ext3.img
debugfs 1.38 (30-Jun-2005)
debugfs:  imap <12>
Inode 12 is part of block group 0
        located at block 6, offset 0x0180
```

Avec `fsstat` du _SleuthKit_ récupérons les informations sur le groupe de block 0 :  

```console
# fsstat ext3.img
Group: 0:
  Inode Range: 1 - 1568
  Block Range: 1 - 8192
  Layout:
    Super Block: 1 - 1
    Group Descriptor Table: 2 - 2
    Data bitmap: 3 - 3
    Inode bitmap: 4 - 4
    Inode Table: 5 - 200
    Data Blocks: 201 - 8192
  Free Inodes: 1557 (99%)
  Free Blocks: 6949 (84%)
  Total Directories: 2
...
```

On extrait l'ensemble de ces 8192 blocks dans un fichier :  

```console
# dls ext3.img 1-8192 < out
# ls -hl out
-rw-r--r--  1 root root 6,8M 2006-07-01 18:49 out
# strings out
test
```

On obtient un fichier de 6,8Mo mais le contenu est dedans.   

La journalisation fait de Ext3 un système de fichiers plus stable en cas d'arrêt brutal de l'ordinateur mais, contrairement à ce que l'on pourrait croire, le journal (au niveau physique) rends la récupération de données effacées bien plus difficile.  

Le noyau Linux permet de choisir le niveau de journalisation lors du montage du système de fichier :  

>  "mount -o data=journal"  
>  Journals all data and metadata, so data is written twice. This  
>  is the mode which all prior versions of ext3 used.  
>   
>  "mount -o data=ordered"  
>  Only journals metadata changes, but data updates are flushed to  
>  disk before any transactions commit. Data writes are not atomic  
>  but this mode still guarantees that after a crash, files will  
>  never contain stale data blocks from old files.  
>   
>  "mount -o data=writeback"  
>  Only journals metadata changes, and data updates are entirely  
>  left to the normal "sync" process. After a crash, files will  
>  may contain stale data blocks from old files: this mode is  
>  exactly equivalent to running ext2 with a very fast fsck on reboot.

Le mode utilisé par défaut est *ordered*. En conclusion l'effacement sécurisé sur un système Ext3 consiste simplement à réécrire par dessus les blocks alloués au fichier. Par défaut, il n'y a pas de risques de retrouver le contenu d'un fichier dans le journal.  

Références :  

[Ext3 - Wikipedia](http://en.wikipedia.org/wiki/Ext3)  

[Journaling File System - Wikipedia](http://en.wikipedia.org/wiki/Journaling_file_system)  

[Brian Carrier - Why Recovering a Deleted Ext3 File Is Difficult](http://linux.sys-con.com/read/117909_1.htm)  

[Linux Ext3 FAQ](http://batleth.sapienti-sat.org/projects/FAQs/ext3-faq.html)  

[Récupération de photos numériques sur une partition Ext3](http://sid.rstack.org/index.php/R%E9cup%E9ration_de_photos_num%E9riques)

*Published January 06 2011 at 12:48*
