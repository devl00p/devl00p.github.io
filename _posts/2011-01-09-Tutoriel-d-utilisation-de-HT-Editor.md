---
title: "Tutoriel d'utilisation de HT Editor"
tags: [reverse engineering, tutoriel]
---

Edit 2023: Ceci ets un vieil article, je vous conseillerais plutôt [Cutter](https://cutter.re/) comme solution open-source pour faire du reverse-engineering sous Linux. 

[HT Editor](http://hte.sourceforge.net/) est un [désassembleur](http://fr.wikipedia.org/wiki/D%C3%A9sassembleur) et éditeur d'exécutables. Il est sous licence GNU GPL et est disponible pour Linux, \*BSD et Windows.  

Il y a peu d'attrait pour les désassembleurs sous Linux et la plupart ne sont pas simple d'utilisation (tout en ligne de commande par exemple). Cela peut s'expliquer par le fait que les programmes sous Linux sont généralement open-source et gratuits.  

HT offre une interface en ncurse permettant de naviguer facilement dans le code, ce qui le rend bien plus agréable à utiliser que le vieux [objdump](http://www.gnu.org/software/binutils/manual/html_chapter/binutils_4.html). De plus il est capable de lire [différents formats d'exécutables](http://hte.sourceforge.net/readme.html#General%20features) et permet de *"switcher"* entre différentes vues (hexa, assembleur, entêtes du fichier...)  

Dans ce billet, on va seulement se concentrer sur l'utilisation du logiciel (touches à connaître) pour naviguer facilement.  

Pour lancer HT (après compilation, le nom du programme doit être `ht`), le plus simple est de lui passer le fichier à analyser en paramètre. Mais vous pouvez aussi le lancer sans arguments et utiliser la touche `F3` ou faire un `Alt+F` > `Open` puis donner le chemin du fichier.  

Une fois le fichier ouvert vous vous retrouvez face à la vue par défaut qui est un éditeur hexadécimal tout ce qu'il y a de plus banal :  

![HT Editor start](/assets/img/ht_start.jpg)  

Quelle que soit la vue dans laquelle vous vous trouvez, vous pouvez toujours vous déplacer avec les touches de direction ainsi qu'avec les touches `PageUp` et `PageDown`.  
En haut de la fenêtre se trouve les menus accessibles avec la touche `Alt` + lettre en rouge.  
En bas de la fenêtre sont marquées les commandes accessibles par les touches `F` (`F1`, `F2`... jusqu'à `F10`) qui sont en haut de votre clavier.  

La touche `F6` fait apparaître un menu qui vous permet de changer le mode d'affichage. À chaque fois que vous vous retrouvez sur un menu ou une boîte de dialogue, sachez que vous pouvez en sortir avec la touche `Echap`.  

![HT Editor Menu](/assets/img/ht_menu.jpg)

Le mode auquel nous allons nous intéresser est le mode *elf/image* qui est le plus évolué pour analyser le code assembleur. Déplacez-vous avec les touches et tapez sur `Entrée` pour valider.  
L'étape suivante consiste à trouver le point d'entrée du programme (`_start`). C'est lui qui va faire appel à la fonction `main` du programme. Pour cela scrollez vers le bas et vous devriez le trouver sans difficultés.  

![HT Editor entry point](/assets/img/ht_entrypoint.jpg)  

Les adresses vers lesquelles on peut *naviguer* sont en blanc dans le code. Il suffit de tapper sur la touche `Entrée` pour s'y rendre. Pour faire marche arrière vous pouvez utiliser la touche `Backspace`.  

Faites `Entrée` pour vous rendre dans le `main`.  

HT ne résout pas tout seul les noms des fonctions (libc et autres librairies) quand le programme a été compilé dynamiquement. À la place, on trouve des noms de fonction du type `wrapper_XXXXXXX_XXXXXXX` qui ne sont pas très parlantes.  

Pour trouver le nom des fonctions correspondantes, on peut parfois le faire au feeling (par exemple une chaine de formatage en premier argument est bon signe pour un `printf`) mais il est plus efficace d'utiliser `objdump`.  

```console
$ objdump -R /tmp/locale/s
/tmp/locale/s:     file format elf32-i386

DYNAMIC RELOCATION RECORDS
OFFSET   TYPE              VALUE
08049e48 R_386_GLOB_DAT    __gmon_start__
08049e10 R_386_JUMP_SLOT   mkdir
08049e14 R_386_JUMP_SLOT   setenv
08049e18 R_386_JUMP_SLOT   chmod
08049e1c R_386_JUMP_SLOT   execv
08049e20 R_386_JUMP_SLOT   chdir
08049e24 R_386_JUMP_SLOT   __libc_start_main
08049e28 R_386_JUMP_SLOT   strcat
08049e2c R_386_JUMP_SLOT   printf
08049e30 R_386_JUMP_SLOT   fclose
08049e34 R_386_JUMP_SLOT   exit
08049e38 R_386_JUMP_SLOT   getcwd
08049e3c R_386_JUMP_SLOT   memset
08049e40 R_386_JUMP_SLOT   fopen
08049e44 R_386_JUMP_SLOT   fwrite
```

En faisant le regroupement entre une adresse obtenue par objdump et la première adresse figurant après `wrapper`_ dans HT on peut en déduire le nom de la fonction. Par exemple `wrapper_8049e10_80484a0` correspond à la fonction `mkdir`.  

![HT Editor wrapper](/assets/img/ht_wrapper.jpg)

On peut alors changer facilement le label de la fonction. Il suffit de se rendre à l'entrée de la fonction sur le label (qui est toujours de la forme `nom_du_label:` et de tapper sur la touche n pour le changer. On peut aussi insérer de nouveaux labels dans le code.  

![HT Editor labelling](/assets/img/ht_label.jpg)  

Remarquez aussi sur l'image précédente que l'on voit les adresses ayant amenées à la fonction (`xref`). Ça peut être utile dans certains cas.  

Tout comme pour les labels, on peut insérer des commentaires avec la touche `#`.  

![HT Editor code comments](/assets/img/ht_comments.jpg)  

Une fois que vous avez terminé, enregistrez votre travail avec `F2` puis utilisez `F10` pour quitter.  

J'ai fait une petite [vidéo d'une session d'analyse de code](http://video.google.fr/videoplay?docid=6431140821932154867) (Google Vidéo) sur un binaire récupéré sur le honeypot. La qualité est pas top après traitement par Google et l'analyse en elle-même a été faite rapidement (j'ai quelques erreurs par rapport au [code original de l'exploit](http://www.digitalmunition.com/ex_perl2b.c)) mais ce sera probablement suffisant pour montrer la navigation à travers HT.  

[HT Editor](http://hte.sourceforge.net/)

*Published January 09 2011 at 10:38*
