---
title: "Un script de sauvegarde de vos fichiers de configuration sous Linux"
tags: [Coding, sysadmin]
---

Quoi de plus agréable quand on change de distribution d'avoir à disposition ses fichiers de configuration précieusement conservés ?  

Quand on passe du temps à peaufiner la configuration du serveur d'affichage ou de son éditeur de texte préféré, l'idée de perdre ces fameux fichiers donne des sueurs froides.  

Seulement lorsque l'on souhaite faire une sauvegarde de ces fichiers, on doit tout faire à la main et surtout on a toujours tendance à en oublier quelques-uns .  

Cette pour cette raison que j'ai bricolé un petit script Bash qui rassemble vos fichiers de conf et en fait une belle archive `tar.bz2` prête à être copiée à l'abri des crashs.  

Vous pouvez télécharger le script en question ici : [saveconfig.sh](/assets/data/saveconfig.sh)

Ce script est très facilement personnalisable. Il se divise en deux sections : la première contient les commandes (le script à proprement parler) et la seconde partie est une liste de fichiers à sauvegarder.  

Vous pouvez aussi bien ajouter des noms de fichiers que de répertoires. Dans tous les cas, il faut donner le chemin complet à partir de la racine (/).  

Si vous indiquez un répertoire, tout son contenu sera copié... donc réfléchissez bien à ce que vous rajoutez ! Il est peut-être préférable de donner des noms de fichiers appartenant à un même répertoire plutôt que de donner le répertoire entier (je pense en particulier aux répertoires cachés utilisés par les navigateurs et qui contiennent le cache de votre navigation).  

Lancé en utilisateur lambda, `saveconfig.sh` enregistre les fichiers de configuration du système (dans `/etc`, `/usr`...).  

Lancé en root, le script va en plus enregistrer la configuration de chaque utilisateur "humain" (dont l'UID est supérieur ou égal à 500)  

Les fichiers de configuration des utilisateurs doivent être indiqués à l'aide du mot clé `_USER_` qui sera remplacé lors de l'utilisation du script par le répertoire home de cet utilisateur (rien de bien compliqué, vous comprendrez facilement en regardant la liste des fichiers par défaut).  

Petite note : `saveconfig.sh` ne garde pas en mémoire les permissions des fichiers... mais c'est facilement modifiable en modifiant les arguments passés à tar et cp.  

Le script a besoin de `bash`, `awk`, `tar` et `bzip2` pour fonctionner.  

[Télécharger saveconfig.sh](/assets/data/saveconfig.sh)

*Published January 05 2011 at 12:28*
