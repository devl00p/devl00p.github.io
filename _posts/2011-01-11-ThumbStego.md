---
title: "ThumbStego"
tags: [Stéganographie]
---

Je viens de tester [ThumbStego](https://sourceforge.net/projects/thumbstego/) (pour *"Thumbnail Steganography"*), un nouvel outil permettant de dissimuler des données dans des images.  

Jusque-là, rien de bien nouveau, il existe un tas d'outils qui permettent de cacher de l'information dans des images. Là où ce logiciel se démarque des autres c'est que contrairement à la majorité (et [pngstego dont j'avais parlé]({% link _posts/2011-01-07-Presentation-de-pngstego.md %}) en fait partie), *ThumbStego* ne se base pas sur la méthode [LSB](http://en.wikipedia.org/wiki/Least_significant_bit) qui consiste à utiliser le bit de poids faible de chaque octet.  

La description du logiciel, telle que trouvée sur *PacketStorm*, est la suivante :  

> Thumbnail steganography creates a thumbnail from a source image and stores data in it by altering the color channels.
> To decipher the data, a new thumbnail is made from the original image and the differences between the pixels are calculated.
> This is intended to increase complexity of automated deciphering of images containing extra (steganographied) data.
> It requires both the original and the thumbnail to decipher. The original works like a key to unlock the thumbnail.


Je ne saurais pas expliquer en détail le fonctionnement de cet outil, les courageux se pencheront vers les sources en Java. Ce qu'il faut retenir c'est principalement la génération d'une image miniature de l'originale, créée de façon à ce que l'originale ait un rôle de [masque](http://fr.wikipedia.org/wiki/Masque_jetable) pour extraire les données cachées.  

Pour utiliser le logiciel, vous aurez besoin d'une version récente de Java sans quoi un message d'erreur de version vous jette, ou alors vous devrez recompiler le programme. De mon côté, j'ai opté pour la première solution et ait installé la version 1.6 de Java (j'avais la 1.5).  

Armé d'une image et d'un fichier texte, le me suis placé dans le répertoire bin (une fois l'archive de *ThumbStego* décompressée) et j'ai tapé la commande suivante :  

```bash
java -cp . tstego/TStego E sdreams.jpg out.png 17941-8.txt S
```

Ceci m'a généré l'image miniature `out.png`... à la regarder avec un éditeur hexadécimal, rien ne se laisse deviner que ce fichier cache des données à sa façon.  

L'image et sa miniature :  

![Sweet Dreams](/assets/img/sweet_dreams.jpg)

![Sweet Dreams Thumbnail](/assets/img/sweet_dreams_mini.png)

Pour extraire les données :  

```bash
java -cp . tstego/TStego D sdreams.jpg out.png secret.txt
```

Et on découvre alors qu'[une vingtaine de fables de La Fontaine](http://www.gutenberg.org/etext/17941) y étaient dissimulées.  

Pour résumer *ThumbStego* utilise un concept très intéressant et comble du bonheur offre un ratio qui a l'air pas mauvais du tout.  

Certes je n'ai pas fait de calcul, mais l'option `S` permet de générer une miniature la plus petite possible en prenant en compte la quantité de données à cacher. Avec une miniature réduite de seulement 1%, il est évident que le ratio est bien plus intéressant qu'avec les outils standards.  

Rien que dans mon exemple, le texte fait environ 29% de la taille de la miniature en étant loin de forcer les capacités du soft... avec d'autres outils, on aurait eu un ratio de 12.5% (1/8 pour le LSB).  
On regrette juste que le logiciel soit un peu lent (de grosses boucles dans le code) et un peu casse-tête à lancer (sous la forme d'un `jar` ce serait parfait).  

Dans tous les cas, à garder sous la main.  

Mise à jour : les nouvelles versions sont maintenant sous la forme d'un jar avec une interface graphique.

*Published January 11 2011 at 08:50*
