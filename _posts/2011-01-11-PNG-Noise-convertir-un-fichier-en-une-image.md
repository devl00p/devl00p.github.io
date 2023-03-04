---
title: "PNG Noise : convertir un fichier en une image"
tags: [Stéganographie]
---

Voici deux petits programmes que j'ai faits en me servant de la librairie d'écriture/lecture d'images PNG [PNGwriter](http://pngwriter.sourceforge.net/).  

Cette librairie est très simple et permet de générer des images très basiques particulièrement adaptés aux graphes et autres représentations mathématiques (voir [les exemples](http://pngwriter.sourceforge.net/) sur le site). Des fonctions très pratiques sont disponibles comme placer un simple pixel, un trait, une forme géométrique, du texte...  

Mon objectif premier en utilisant cette librairie était de faire un programme capable de prendre des données brutes d'un fichier quelconque et d'en faire une image PNG valide (affichable sans erreurs dans différents logiciels). Le résultat n'est forcément pas très beau (c'est du *"bruit"*) mais on peut procéder en sens inverse et extraire les données présentes dans l'image pour recréer le fichier original.  

L'utilité du programme est questionnable. Une des applications pourrait être de passer certains filtres sur les formats de fichiers comme ceux présents sur les services de stockage d'image en ligne. On pourrait alors y stocker tout type de données.  
Du point de vue stéganographique le programme offre un excellent ratio, mais un œil humain se douterait que l'image renferme un secret ;-)   

Enfin l'idée m'est entrée dans la tête donc il fallait que je le fasse. Je vous laisse à votre imagination pour d'autres applications.  

Le principe est le suivant :  

* PNG est un format d'[image matricielle](http://fr.wikipedia.org/wiki/Image_matricielle), c'est-à-dire que les images sont définies par un ensemble de pixel
* Chaque pixel de l'image est défini par une couleur codée sur 3 valeurs : R, V, B (rouge, vert et bleu)
* Chacune de ces [couleurs primaires](http://fr.wikipedia.org/wiki/Couleur_primaire) est codée de 0 à 65535, correspondant à autant de nuances différentes

Une nuance de couleur (0 à 65535) tient sur 2 octets. On a donc 6 octets (car 3 couleurs primaires) par pixel. Il suffit alors de lire le fichier à *"transformer"* par morceaux de 6 bits et de les intégrer comme pixel dans une image.  

Le programme s'arrange pour que les dimensions de l'image finale soient le plus proche possible du carré. Les derniers pixels sont donc des pixels de bourrage.  

Le tout premier pixel de l'image sert à stocker la taille du fichier d'origine pour déterminer le nombre d'octets effectifs lors de l'opération inverse.  

En utilisant le programme `transform` sur [ce fichier pdf](http://www.mulix.org/lectures/tau_linux_workshop/kernel_modules.pdf) vous expliquant comment implémenter la suite de *Fibonacci* en kernel-land (hmmm), on obtient l'image suivante :  

![Kernel Module as PNG](/assets/img/kern_module.png)

Le programme `extract` sera capable de retrouver le fichier original à partir de cette image.  

C'est aussi intéressant, car ça permet de voir tout de suite les répétitions présentes dans un fichier : les zones unies de l'image représentent les zones du fichier qui gagneraient à être compressées.  

Ainsi si on régénère une image à partir du fichier PDF une fois compressé avec bzip2 on obtient :  

![Kernel Module compressed as PNG](/assets/img/kern_mod_bz2.png)

Vous trouverez les sources dans l'archive [png_noise.zip](/assets/data/png_noise.zip)  

La librairie _PNGwriter_ n'est pas incluse. Les commandes pour la compilation sont indiquées dans la source.

*Published January 11 2011 at 11:33*
