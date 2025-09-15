---
title: "Tutoriel : Faire une électrolyse"
tags: [Mécanique]
---

## La théorie

Dernièrement, j'ai remplacé sur ma voiture des étriers de freins qui étaient bien attaqués par la rouille (j'ai dû sortir l'un des pistons avec une pompe à graisse). Je les ai remplacés par des nouveaux, mais j'ai conservé les anciens afin de faire une reféction et d'apprendre deux trois trucs.

Grosso modo les étapes de la réfection (après dépose) :

- nettoyage
- dérouillage
- [peinture époxy](https://www.amazon.fr/dp/B0BZJPQQ4H?th=1)
- [peinture spéciale étrier de frein](https://www.amazon.fr/dp/B0CDM14YWQ)
- remontage de pistons neufs et des caoutchoucs et joints neufs
 
D'après Wikipedia, une électrolyse c'est :

> L'électrolyse est une méthode qui permet de réaliser des réactions chimiques grâce à une activation électrique. C'est un processus de conversion d'énergie électrique en énergie chimique

Il y a différentes applications à l'électrolyse, mais pour un particulier l'utilisation la plus courante consiste à enlever la rouille d'un objet.

Sur le plan théorique, que se passe-t'il ?

La rouille est réduite en fer : La pièce rouillée est connectée au pôle négatif (la cathode). Sous l'effet du courant électrique, la rouille, qui est de l'oxyde de fer, est chimiquement réduite.

Des électrons sont ajoutés aux ions d'oxygène et de fer de la rouille, la convertissant en hydrogène gazeux et en fer pur. La rouille ne voyage pas, elle est transformée sur place et se détache de la surface de la pièce sous forme d'une poudre noire qui tombe au fond de l'eau.

Le métal sacrificiel s'oxyde : Le morceau de métal (anode) que vous avez mis dans l'eau est connecté au pôle positif. Sous l'effet du courant, il s'oxyde et se corrode très rapidement. Il rouille à la place de votre pièce. C'est pour cette raison qu'on l'appelle "métal sacrificiel".

## La pratique

On voit déjà mieux comment s'y prendre. Pour commencer, il faut déjà être équipé. Voici le matériel dont il faut disposer :

- un grand bac en plastique qui servira pour le bain d'électrolyse (suffisamment grand pour que les deux pièces n'entrent pas en contact)
- du bicarbonate de soude ou des cristaux de soude (genre seau de 1Kg, à adapter selon le volume du bain)
- un chargeur de batterie de voiture
- une batterie de voiture, même très fatiguée ça marche (explications plus loin)
- un morceau de métal sacrificiel (boîte de conserve)
- deux fils électriques (genre fil en cuivre solide pour la maison)
- une brosse métallique
- un sceau d'eau propre

Et pas obligatoire, mais tout de même bien pratique pour faire bien les choses :

- une pince à dénuder / sertir
- un multimètre
- un contenant plastique refermable (bidon de 5L ou simple bouteille)

### Le mélange

La première étape consiste à préparer le mélange eau + bicarbonate de soude. C'est mieux de disposer d'un contenant qu'on puisse fermer comme ça on peut mettre l'eau et le bicarbonate puis secouer franchement sans crainte. Avec une simple touillette ça ne va pas bien se mélanger et le succès de l'électrolyse dépend beaucoup du mélange.

Dans quelles proportions mélanger l'eau avec le bicarbonate de soude ? Pas de science exacte là-dessus mais il faut que l'eau soit suffisamment trouble. Dans mon cas j'ai dû mettre 500g de bicarbonate pour 8 litres d'eau.

L'avantage de commencer par le mélange, c'est que ça laisse le temps au bicarbonate de bien se diluer dans l'eau.

### Les pièces métalliques

On a donc la pièce à récupérer ainsi que la pièce sacrificielle.

Pour cette dernière, à vous de voir ce que vous avez sous la main. Plus c'est gros (ou grand) et lourd (pour éviter de bouger dans le bac) mieux c'est.

J'ai utilisé une grosse boîte de conserve et j'ai fait différents trous, déjà pour qu'elle ne flotte pas et ensuite pour faire passer le fil électrique dénudé (à son extrémité).

Évitez les canettes avec un imprimé du type coca/fanta : la peinture rend le métal difficilement conducteur. Pour s'assurer que tout est OK, on peut se servir d'un multimètre en fonction ohmmètre.

Assurez-vous que les fils sont bien en contact avec les objets. Comme expliqué dans la partie théorique, on doit avoir un fil relié à la pièce à récupérer. L'autre extrémité de ce fil ira à la borne négative de la batterie.

Pour la pièce sacrificielle, le fil sera bien sûr reliée à la borne positive.

![Pièces métalliques dans leur bain d'électrolyse](/assets/img/mecanique/electrolyse_bain.jpg)


### Les précautions

Avant de tout relier électriquement il y a plusieurs précautions à prendre :

- faire ça dans un lieu ventilé : l'opération dégage des gaz toxiques
- protéger si besoin le bac avec une grille surtout si vous avez des enfants ou des animaux de compagnie :)
- toujours commencer par débrancher les fils électriques avant de sortir une des pièces en métal
- porter des gants quand vous sortez les pièces sinon vos mains seront recouvertes d'une couche de rouille noire

### Le branchement

On en vient à la raison pour laquelle il faut une batterie pour réaliser l'opération : les chargeurs de batterie modernes sont dit "intelligents" car ils sont capables de voir s'ils sont connectés à un objet qui supporte la charge. Ils peuvent adapter le courant en fonction, afin que la batterie charge de façon douce et sûre.

Par conséquent, si vous allumez le chargeur de batterie et que vous mesurez la tension à ses bornes à l'aide de voltmètre, ce n'est pas anormal de mesure approximativement 1 volt alors que le chargeur est censé délivrer 14 volts (comme un alternateur).

Pour tromper le chargeur, on le branchera à une batterie de voiture et les fils menant à chaque pièce en métal seront branchés en parallèle. C'est-à-dire que sur la cosse positive de la batterie, vous aurez à la fois le cable positif (rouge) du chargeur de batterie et le fil menant à la pièce sacrificielle. Inversement sur la borne négative de la batterie, vous aurez à la fois le cable négatif (noir) du chargeur et le fil menant à la pièce à récupérer.

Comme les chargeurs ont généralement des pinces crocos, c'est facilement de serrer le fil dénudé sur la cosse de la batterie, ça évite d'avoir à faire des soudures supplémentaires.

Rappelez-vous que dès que vous reliez les fils à la batterie la réaction devrait se déclencher, même si le chargeur n'est pas encore en marche. Dès branchement, vous devriez voir des petites bulles remonter à la surface. C'est bon signe.

![Mon setup d'electrolyse](/assets/img/mecanique/electrolyse_setup.jpg)

### Attendre

Maintenant, vous êtes bon pour patienter quelques heures en fonction de la taille de l'objet et de son état. Pour mon étrier, j'ai bien attendu six bonnes heures.

Après ça, la pièce sacrificielle avait bien morflé alors qu'elle était en état neuf :

![Déplacement de la rouille par electrolyse](/assets/img/mecanique/electrolyse_conserve.jpg)


### Mettre au sec

Pour sécher les pièces, différentes options s'offrent à vous comme un compresseur, sèche-cheveux, décapeur thermique, etc.

Moi, j'ai préféré mettre la pièce au four, préchauffé à 100°. Avantage : ça sèche vite et la pièce est chaude, ce qui est pratique pour appliquer l'époxy (il sèche immédiatement).

![Peinture expoxy](/assets/img/mecanique/electrolyse_epoxy.jpg)

Au moment de sortir les pièces du bac, pensez bien à porter des gants. Passez-les dans un seau d'eau propre pour enlever le noir et frottez avec une brosse métallique.

Mettez ensuite la pièce à sécher au four. N'oubliez pas d'avoir un gant de cuisson pour la sortir du four (Il vaut mieux prévenir que guérir). Si vous avez moyen de l'accrocher en hauteur (avec un fil ou un crochet en métal) pour peindre toute sa surface avec de l'époxy, c'est parfait.

Avant / après :

![Résultat après preinture](/assets/img/mecanique/electrolyse_avant_apres.jpg)
