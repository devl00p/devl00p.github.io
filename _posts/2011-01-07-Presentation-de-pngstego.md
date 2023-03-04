---
title: "Présentation de pngstego"
tags: [Stéganographie]
---

J'étais passé à côté de [pngstego](http://pngstego.sourceforge.net/) en me disant que ce logiciel de [stéganographie](http://fr.wikipedia.org/wiki/St%C3%A9ganographie) utilisant le format PNG n'en valait pas la peine, comme un certain nombre de programmes qui dissimulent des informations dans des fichiers image.  

Il faut dire que `pngstego` utilise la technique des bits de poids faible (voir [Wikipedia: LSB](http://en.wikipedia.org/wiki/Least_significant_bit)) qui est on ne peut plus classique. Le principe est simple : chaque pixel de l'image est encodé par un code couleur tenant sur un octet dans le fichier. Le dernier bit de cet octet est dit *"bit de poids faible"* car son état est quasi insignifiant sur le rendu final de l'image. En effet l'œil humain ne parviendra pas à distinguer des nuances aussi subtiles entre deux couleurs.  

L'avantage de la technique LSB est qu'elle donne un ratio d'un huitième (1/8) pour la dissimulation des données ce qui loin d'être négligeable comparé à un [isosteg](http://isosteg.sourceforge.net/) (moins de 1/700).  

Le gros inconvénient de cette technique est quelle est facilement détectable, par exemple avec des outils comme [stegdetect](http://www.outguess.org/detection.php) de [Niels Provos](http://www.citi.umich.edu/u/provos/) ou [Shade](http://shade.sourceforge.net/) (pour l'instant ne supporte que le format BMP).  

Afin de rendre plus difficile la récupération des données, `pngstego` utilise un [chiffrement par transposition](http://www.apprendre-en-ligne.net/crypto/transpo/index.html). Les données à insérer ne sont pas mises dans l'ordre dans l'image, mais aléatoirement en utilisant les fonctions C pseudo-aléatoires `random()` et `srandom()`.  

Afin que la personne à qui est destinée l'image générée puisse extraire le message secret, une clé privée doit être connue des deux participants. Cette clé est en fait la *"graine"* qui a servi à initialiser la fonction `srandom()`, c'est donc un nombre.  

Vous pouvez laisser `pngstego` le choisir aléatoirement pour vous ou le fixer vous-même. Utiliser sa date de naissance ou son numéro de téléphone n'est pas forcément une bonne idée. Je recommande par exemple que vous choisissiez un mot de passe et que vous utilisiez les valeurs décimales/hexadécimales/octales des caractères.  

Mais la transposition ne vous protégera pas forcément de l'attaque d'un bon [cryptanalyste](http://fr.wikipedia.org/wiki/Cryptanalyste) (en particulier si le message est un texte en clair, on peut se fier aux majuscules, ponctuation etc pour retrouver le message original)  

C'est pour cela que l'auteur de `pngstego` conseille d'utiliser une solution de cryptage puissante (_GPG_) avant de dissimuler les données.  

Le code source est très léger et compile facilement (tapper `make`, juste quelques warnings). Il nécessite les entêtes de la librairie `png` (`libpng-devel`)  

Pour l'exemple, nous allons utiliser une photo d'une œuvre de [Banksy](http://www.banksy.co.uk/). Banksy est un artiste engagé très réputé, principalement pour ses graffitis. Son dernier coup a été de [détourner le CD audio de Paris Hilton](http://www.fluctuat.net/blog/4562-Paris-Hilton-Punked) (vous pouvez trouver [des photos sur flickr](http://www.flickr.com/photos/n3wjack/238327248/in/set-351291/)).

L'image choisie ici est un graff bien connu :  

![image originale](/assets/img/banksy_original.png)

Et le texte à dissimuler sera [Jabberwocky](http://en.wikipedia.org/wiki/Jabberwocky), un poème délirant de *Lewis Carroll* tiré de *"Through The Looking Glass"* qui se base sur le principe des [mots-valises](http://fr.wikipedia.org/wiki/Mot-valise) ([portmanteau](http://en.wikipedia.org/wiki/Portmanteau) en anglais).

L'image pesant 68Ko et [le texte 961](http://www.nothings.org/writing/jab.txt) octets, on rentre largement dans le ratio.  

On n'a plus qu'à tapper la commande  

```bash
./pngstego -s -i bksmall_in.png -m jab.txt bksmall_out.png
```

Qui donne la sortie suivante :  

```
Image size 240 x 160 pixels, 8 bit per pixels
random seed: 917184151
libpng warning: Invalid sBIT depth specified
libpng warning: Invalid sBIT depth specified
```

Voici l'image résultante :  

![image obtenue](/assets/img/banksy_resultat.png)

Cette nouvelle image pèse 2Ko de plus (70Ko)... Je ne suis pas parvenu à déterminer la raison de cette augmentation, il se pourrait que ce soit la regénération par la librairie png qui soit en cause :/   

Pour retrouver le message, on utilise `pngstego` en mode extraction et en spécifiant la graine utilisée lors de la création de l'image :  

```bash
./pngstego -x -i bksmall_out.png -m message.txt -S 917184151
```

Rien de plus simple !  

PS : `pngstego` ne fonctionne pas avec toutes les images PNG, il accepte les images en niveau de gris 8 bits et les images couleur 8 bits RGB.  

Utilisez la commande `file` pour savoir si une image est utilisable :  

```console
$ file bksmall_in.png
bksmall_in.png: PNG image data, 240 x 160, 8-bit/color RGB, non-interlaced
```

Si on avait obtenu RGBA au lieu de RGB nous n'aurions pas pû utiliser l'image.

*Published January 07 2011 at 09:05*
