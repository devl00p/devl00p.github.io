---
title: "La vrai fausse backdoor dans le chiffrement des disques durs par PGP"
tags: [Cryptographie]
---

Il y a quelques jours, le blog *Securology* a publié [un article](http://securology.blogspot.com/2007/10/pgp-whole-disk-encryption-barely.html) traitant d'une fonctionnalité peu connue du logiciel de chiffrement de disque _PGP Whole Disk Encryption (WDE)_ qui a provoqué quelques réactions *"trollesques"*...  

Avant d'entrer dans le vif du sujet, il est bon de connaître à quoi sert _PGP WDE_ et un résumé simple de son fonctionnement.  

_PGP Whole Disk Encryption_ permet, comme son nom l'indique, de chiffrer la totalité d'un disque dûr, c'est-à-dire : les différentes partitions, le (ou les) système(s) d'exploitation et le secteur de boot (Master Boot Record).  

Quand un poste disposant de cette technologie est allumé, il boote d'abord sur du code de PGP qui va demander la saisie d'un mot de passe au clavier par l'utilisateur.  

Par une suite de différents calculs cryptographiques, ce mot de passe va permettre au final le déchiffrement des données.  

Dans les étapes utilisées pour arriver au lancement du système d'exploitation, la première est le déchiffrement d'une clé qui a été cryptée à l'aide du mot de passe de l'utilisateur.  

Cette méthode est très utilisée, notamment pour la cryptographie à clé publique : pour éviter que la clé secrète soit compromise en cas d'intrusion et/ou de vol de données, celle-ci n'est pas stockée en clair sur le disque, mais stockée chiffrée par un algorithme de chiffrement symétrique.  

Ce procédé est nommé S2K / K2S (string-to-key et vice-versa), il est par exemple documenté dans la [RFC 2440 : OpenPGP Message Format](http://www.ietf.org/rfc/rfc2440.txt) (chapitres `3.6.*`, c'est dans la même RFC que l'on trouve une explication sur le Radix-64).  

On pourrait penser que la clé déchiffrée est celle utilisée pour le déchiffrement, mais il n'en est rien. Il y a une seconde étape qui permet à partir de cette clé d'accéder à la clé maître (master key) avec laquelle le chiffrement a été utilisé.  

L'objectif de ce second procédé et de permettre à différents utilisateurs de déchiffrer le disque, chacun utilisant un mot de passe différent (si j'ai bien tout compris)  

Maintenant que vous connaissez (vaguement) le fonctionnement du système, il est temps de parler de la fonctionnalité baptisée *"Whole Disk Encryption (WDE) Bypass"*.  

Le nom est celui donné par PGP et est suffisamment explicite : il permet de passer outre la saisie d'un mot de passe pour déchiffrer les données.  

A quoi sert exactement cette fonctionnalité ? Elle permet aux administrateurs de faire redémarrer les machines dont le disque est chiffré par _WDE_.  

Partons du principe que vous êtes un administrateur d'un parc réseau avec des machines ultra-sécurisées et que vous avez besoin d'effectuer différentes taches qui seront validées lors du redémarrage de la machine.  

Vous lancez l'opération et vous attendez sagement que vos machines redémarrent pour continuer à travailler. Sauf que... les machines ne redémarrent pas !  

En effet, le système d'exploitation ne s'est pas lancé, car personne n'est devant le poste pour saisir le mot de passe de déchiffrement et par conséquent la couche réseau de l'OS n'est pas disponible. Vous voilà obligé de faire le tour des machines et de saisir chaque mot de passe de déchiffrement pour remettre votre réseau en marche.  

C'est là qu'intervient la fameuse fonctionnalité *"bypass"*. Quand elle est activée, elle va stocker sur le disque une nouvelle clé de chiffrement dérivée de la master key ainsi qu'un flag disant à _WDE_ d'utiliser cette clé automatiquement au prochain démarrage du poste. Cette clé est cryptée par le procédé S2K par un mot de passe fixe (valeur hexadécimale `0x01`).  

Donc :  

* l'administrateur lance ses taches sur les machines
* il active le WDE Bypass
* il redémarre les postes
* WDE utilise la clé de bypass pour démarrer les postes
* WDE supprime les données de bypass qui ont été placées sur le disque
* les postes sont démarrés et accessibles par le réseau

Sur le principe, c'est plutôt bien trouvé et c'est une fonctionnalité qui semble très appréciée dans les entreprises (on peut comprendre). Le problème, c'est que l'on baisse la sécurité du chiffrement à chaque utilisation du mode bypass : il suffit qu'un intrus subtilise une machine entre le moment de la mise hors tension et celui du redémarrage pour disposer d'un disque sur lequel sont présentes toutes les informations nécessaires pour déchiffer le disque.  

Le débat faire rage sur [Slashdot](http://it.slashdot.org/article.pl?sid=07/10/04/1639224) entre ceux qui considèrent qu'il s'agit d'une backdoor et ceux qui défendent qu'il s'agit d'une fonctionnalité tout à fait normale.  

En réalité quand j'essayais de comprendre le fonctionnement de tout ça, ça n'a pas été évident de trouver les commentaires de ceux qui se posaient les vraies questions sur Slashdot. Il faut dire que tous les articles sur le sujet sont en anglais et que ça ne facilite pas la tâche... heureusement, c'est de l'écrit (j'ai eu l'occasion de parler anglais cet après midi et c'était l'enfer, en plus c'était une discussion avec un chinois)  

Après avoir pesé le pour et le contre, mon opinion personnelle est que non, ce n'est pas une backdoor.  

D'abord, bien que peu expliquée, cette fonctionnalité était citée dans la documentation. De plus, PGP affiche une position claire sur cette fonctionnalité et a réagi en postant un commentaire sur le blog de l'auteur de l'article avant de [donner des explications publiques](http://www.pgp.com/wde_bypass_feature.html).  

Cependant, cette fonctionnalité baisse considérablement la sécurité générale du chiffrement. Comme toujours en cryptographie, le niveau de sécurité d'un système est équivalent à celui de son maillon le plus faible. Ici on peut imaginer un malware qui active le WDE Bypass en vue d'une prochaine attaque physique, ou encore un code qui modifiera le fonctionnement du WDE... mais là on s'écarte sans doute trop du sujet.  

Dans tous les cas pour activer cette fonctionnalité, il faut un *"cryptographic access"* aux données, c'est-à-dire avoir des droits d'utilisateur sur la machine, c'est-à-dire... avoir accès aux données en clair.  

En fin de compte ce qui gêne, c'est que le WDE Bypass pourrait tout aussi bien être utilisé en douce, et qu'une clé spéciale soit intégrée à l'installation du logiciel, chiffrée à l'aide d'une passphrase connue seulement par une certaine agence de sécurité nationale.  

Bref on en revient à la confiance que l'on donne aux développeurs des logiciels que l'on utilise. Mais c'est un procédé intéressant et je comptais bien vous faire profiter de ces articles.  

[Explication (simplifiée) de PGP WDE sur le site officiel (vidéo présente)](http://www.pgp.com/products/wholediskencryption/index.html)  
[Un second article de Securology en réponse aux informations apportées par un représentant de PGP](http://securology.blogspot.com/2007/10/response-to-jon-callas-pgp-encryption.html)  
[Le premier article](http://securology.blogspot.com/2007/10/pgp-whole-disk-encryption-barely.html)

*Published January 10 2011 at 09:10*
