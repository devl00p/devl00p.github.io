---
title: "Live CD et stéganographie"
tags: [Stéganographie]
---

Les distributions Linux *"live"* (que l'on peut démarrer sans installation en bootant à partir d'un CD ou d'un DVD) offrent un support intéressant pour dissimuler des données.  

En effet, qui penserait à étudier en détail un CD-ROM qui à première vue ne contient que l'un de ces systèmes d'exploitation ?  

De plus le système de fichier virtuel obtenu une fois que l'on a démarré le système est stocké compressé sur le CD, ce qui rend encore plus difficile l'analyse du cd.  

De plus en plus de systèmes utilisent _SquashFS_ pour stocker les fichiers compressés. [SquashFS](http://en.wikipedia.org/wiki/SquashFS) est un système de fichier compressé accessible en lecture seule. Il offre un très bon taux de compression et est simple d'utilisation.  

Dans cet article, on va modifier l'iso de [grml 0.8](http://grml.org/) (la version 0.9 devrait sortir sous peu, la [release candidate 1](http://grml.org/files/README-0.9-rc1.php) étant déjà disponible).  

Au départ je comptais modifier l'iso d'Ubuntu live, mais je me suis rendu compte que je n'avais plus le fichier. Ubuntu utilisant aussi _SquashFS_, l'opération ne devrait pas être bien différente (vous pouvez utiliser [cet article](http://doc.ubuntu-fr.org/applications/personnalisation/customisationcd) sur la personnalisation du CD)  

Avant d'aller plus loin il faut nous assurer d'avoir :  

* Un système assez performant (générer l'image _SquashFS_ demande beaucoup de ressources)
* Quelques Go de libre
* Un logiciel pour modifier des fichiers isos comme [ISO Master](http://littlesvr.ca/isomaster/) ou [Kiso](http://kiso.sourceforge.net/). On pourrait très bien faire cette opération avec mount et mkisofs... mais pourquoi s'embêter ?
* Le module noyau pour _SquashFS_ ainsi que les outils utilisateur

Depuis ma SUSE 10.1 j'ai opté pour `isomaster` dont d[es packages sont disponibles](http://packman.links2linux.de/package/isomaster/).  

J'ai aussi dû installer _SquashFS_ puisqu'il n'est pas présent par défaut sur SUSE 10.1. J'ai récupéré `squashfs-3.1-1.i586.rpm` et `squashfs-kmp-default-3.1_2.6.16.21_0.25-1.i586.rpm` disponibles ici  

Un `rpm -ivh *.rpm` et les packages sont installés. Ensuite on charge le module `SquashFS` avec modprobe : `modprobe squashfs`  

On ouvre `grml_0.8.iso` avec ISO Master :  

![ISO master en action](/assets/img/isomaster.jpg)  

Le logiciel est très simple d'utilisation. La fenêtre du haut représente l'arborescence locale et la fenêtre du bas le contenu du cdrom.  

On extrait l'image _SquashFS_ du cdrom. Pour _grml_, il s'agit du fichier `GRML/GRML` :  

![GRML squashfs file](/assets/img/grml_iso.jpg)  

Le fichier est facilement reconnaissable : il prend la quasi-totalité de l'espace.  

On monte le système de fichier (en root) :  

```bash
mount -t squashfs GRML /mnt/ -o loop
```

Comme SquashFS est en lecture seule on ne va pas pouvoir travailler directement sur le système de fichier. On va faire une copie d'archive :  

```bash
cp -a /mnt/. /tmp/fs_grml/
sync
umount /mnt/
```

On peut libérer de la place en supprimant l'ancienne image _SquashFS_ (fichier GRML) dont on n'a plus besoin.

À vous de dissimuler vos données dans le système de fichier présent dans `/tmp/fs_grml`. J'ai opté pour *"un petit plus"* en utilisant _mansteg_ et [dissimuler les données dans les manpages]({% link _posts/2011-01-06-mansteg-steganographie-dans-les-manpages.md %}).  

```bash
python hide.py ~root/.gnupg/secring.gpg /tmp/fs_grml/usr/share/man/man1/gpg.1.gz
```

Une fois les fichiers ajoutés on génère une nouvelle image _SquashFS_ (c'est assez long) :  

```bash
mksquashfs /tmp/fs_grml/ /tmp/GRML
```

Avec ISO Master on rouvre l'ISO, on supprime l'ancien fichier `GRML` présent dans le dossier du même nom et on y place le nouveau. On enregistre ensuite l'ISO sous un autre nom (les modifications directes ne sont pas supportées).  

On grave l'ISO et c'est bon !  

**NB: ISOLINUX peut retourner une erreur de checksum au démarrage du live CD. Il est préférable de se référer à la documentation de la distribution et d'utiliser la commande `mkisofs` présentée.**

*Published January 08 2011 at 13:23*
