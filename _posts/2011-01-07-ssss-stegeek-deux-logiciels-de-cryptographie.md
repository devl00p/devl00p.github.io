---
title: "SSSS et Stegeek : Présentation de deux logiciels de cryptographie"
tags: [Cryptographie, Stéganographie]
---

Dans ce billet je vais vous parler de deux logiciels [cryptographiques](http://fr.wikipedia.org/wiki/Cryptographie) qui se basent sur des concepts ingénieux.  

## SSSS

[SSSS](http://point-at-infinity.org/ssss/) (pour *Shamir's Secret Sharing Scheme*) se base sur le principe du [secret partagé](http://en.wikipedia.org/wiki/Secret_sharing), plus précisément sur les travaux du célèbre [Adi Shamir](http://en.wikipedia.org/wiki/Adi_Shamir) sur le sujet.  

Le principe du secret partagé est entré depuis longtemps dans nos esprits. Qui n'a pas vu un film dans lequel un trésor est protégé par tout un tas de verrous et auquel on ne pourra accéder qu'une fois que les propriétaires des clés correspondantes seront réunis ?  

Mais dans une telle situation, on a tendance à voir les clés des différents protagonistes comme autant de mots de passe. Je dirais que du point de vue de _SSSS_, le mot de passe est le trésor et que les clés... sont simplement des clés cryptographiques. Certes ce ne sont pas des clés publiques puisque leur divulgation permettrait l'accès au trésor par n'importe qui, mais le vol d'une seule clé ne permettrait pas de briser la protection.  

Si je dis que le trésor est un mot de passe, c'est principalement parce que _SSSS_ ne permet que de cacher une chaine de 128 caractères ASCII maximum.  

La commande `ssss-split` va se charger de répartir le secret à dissimuler dans les différentes clés. Par exemple si je désire cacher le secret dans 8 clés différentes et que ce secret soit accessible par 4 possesseurs de ces clés (quelque ils soient), je tape :  

```bash
ssss-split -t 4 -n 8
```

Le programme me demande alors d'entrer le secret et 8 clés seront générés :  

```
1-57c86c3b18f3c490
2-208098db24047637
3-c600bba02b41008a
4-a76a68d66263efcc
5-556f77fc199c2934
6-0b2dfbbecc1efb19
7-48a9365210b2b699
8-239ab30fbb4d76e7
```

Je m'empresse de donner à chacun sa clé et si plus tard nous avons besoin de retrouver ce secret il suffira de réunir 4 membres du groupe et de faire appel à la commande `ssss-combine` :  

```console
$ ssss-combine -t 4
Enter 4 shares separated by newlines:
Share [1/4]: 3-c600bba02b41008a
Share [2/4]: 6-0b2dfbbecc1efb19
Share [3/4]: 8-239ab30fbb4d76e7
Share [4/4]: 1-57c86c3b18f3c490
Resulting secret: l33tp4ss
```

Dans ce cas-là ce sont les clés numérotées 3, 6, 8, 1 qui ont permis de retrouver le secret.  

C'est dommage que le logiciel soit limité à 128 caractères et ne permette pas de partager des fichiers...  

J'ai aussi trouvé un bug assez gênant :  

```console
$ ssss-combine -t 2
Enter 2 shares separated by newlines:
Share [1/2]: 4-a76a68d66263efcc
Share [2/2]: 7-48a9365210b2b699
Resulting secret: o..Q....
WARNING: binary data detected, use -x mode instead.
```

Dans le cas où seulement deux clés sont compromises sur les 4 (ou plus), on obtient un mauvais résultat, mais dont la longueur est celle du vrai mot de passe.  

Pour compiler le logiciel vous aurez besoin de la librairie _GMP_ sur les calculs de grands nombres (paquets `gmp` et `gmp-devel` sur SUSE)  

## Stegeek

[Stegeek](http://sourceforge.net/projects/stegeek) se base aussi sur le principe des clés multiples, mais de façon bien différente. Si je devais donner une référence, je dirais que c'est le principe de la *"salle sur demande"* dans *Harry Potter*.  

Pour ceux qui ne connaissent pas cela signifie qu'il y a un coffre magique dont le contenu change en fonction de la clé utilisée pour l'ouvrir.  

À quoi ce principe peut-il servir en informatique ? Tout simplement à induire en erreur un attaquant qui aurait intercepté le fichier crypté et aurait réussi à en extraire des données (sans intérêt) avec un certain mot de passe alors que les données sensibles seraient protégées avec un mot de passe plus fort.

Pour faire fonctionner _Stegeek_ vous devez au préalable créer un fichier qui contiendra les différents mots de passes (un par fichier à dissimuler et un mot de passe par ligne).  

Par exemple je crée un nouveau fichier nommé `passfile` dont le contenu est :  

> ceciestlepremierpass  
> thisisthesecondpass  
> herecomethethirdpassword


Ensuite j'utilise `stegeek` pour cacher 3 fichiers dans un fichier nommé *blah* :  

```console
$ stegeek -o blah -r 1.5 /etc/passwd /etc/issue /etc/SuSE-release < passfile
/etc/passwd
/etc/issue
/etc/SuSE-release
-----
Adding 3 files.
Enter encryption keys for files
(10-36 chars, first 4 chars must differ from other keys of files in archive)
key 0:key 1:key 2:
Creating archive...
Done.
```

Maintenant déchiffrons le fichier *blah* avec le troisième mot de passe, le résultat étant stocké dans le fichier `secret` :  

```console
$ stegeek -e -o secret blah
Enter extraction key: herecomethethirdpassword
Extracting...
Done.
Erreur de segmentation
$ cat secret
SUSE LINUX 10.1 (i586)
VERSION = 10.1
```

Et avec le second mot de passe :  

```console
$ stegeek -e -o secret blah
Enter extraction key: thisisthesecondpass
Extracting...
Done.
Erreur de segmentation
$ cat secret
Welcome to SUSE LINUX 10.1 (i586) - Kernel \r (\l).
```

Malgré quelques erreurs de segmentation tout fonctionne. Malheureusement le projet est mort :'(   

Deux logiciels forts intéressants... évidemment il faut trouver l'occasion de les utiliser.

*Published January 07 2011 at 08:05*
