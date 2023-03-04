---
title: "Créez une partition cachée sous Linux"
tags: [Cryptographie, Vie privée et anonymat]
---

## Introduction

![Smiling lock](/assets/img/devloop_lock.jpg)

Les systèmes d'exploitation les plus utilisés proposent tous à l'heure actuelle des solutions pour chiffrer les partitions ou l'ensemble d'un disque.  

L'inconvénient de ces systèmes est que la présence des données chiffrées est généralement bien visible, par exemple par le biais d'un fichier de montage (`/etc/crypttab` ou `/etc/cryptotab` sous openSUSE) et de la table des partitions permettant au système de savoir avec quel algorithme il doit déchiffrer les partitions chiffrées et sur quelle partie du disque.  

Dans cet article je vais vous expliquer comment mettre en place une partition cachée qui ne sera visible ni dans la table des partitions ni décrite dans un fichier de configuration.  

À l'heure actuelle, [TrueCrypt propose un système de ce type](http://www.truecrypt.org/docs/?s=hidden-volume), mais nous utiliserons ici une méthode plus basique en nous servant de la commande `losetup` pour la gestion des périphériques de boucle (`/dev/loop*`) et de `cryptsetup` qui permet de créer des volumes `dm-crypt`.  

Le principe est le suivant : sur un disque dur nous allons créer une partition visible qui prendra la moitié de l'espace. Ensuite sur le reste de l'espace (tout l'espace libre restant) nous placerons notre partition chiffrée.  

## Créer une partition cachée sur un disque dur  

Dans l'exemple qui suit le disque fait une taille de 50Mo. La partition visible fera 20Mo, le reste sera pris par notre partition secrète. À vous d'adapter les commandes en fonction de votre disque et des systèmes de fichiers que vous désirez.  

On partitionne le disque à l'aide de `cfdisk` pour créer notre partition de 20Mo. Il est important que cette partition soit placée au début du disque :  

```bash
cfdisk /dev/hda1
```

On récupère l'adresse de la fin de cette partition (en octets) à l'aide de la commande `parted` :  

```bash
parted /dev/hda unit B print
```

Dans mon cas, la fin de la partition est à l'offset `16450559`. Nous fixerons alors le début de notre partition cachée à `16450600` (arrondir au supérieur).  

On formate la partition visible en `ext2`, on la monte et on crée un fichier pour tester :  

```bash
mkfs.ext2 /dev/hda1
mount -t ext2 /dev/hda1 /mnt/hda1
echo abcd > /mnt/hda1/truc
```

Passons maintenant à notre partition chiffrée. Pour ne pas faire de bêtises, il faut trouver le nom d'un périphérique loop non utilisé. Ceux en cours d'utilisation peuvent être obtenus par la commande suivante :  

```bash
losetup -a
```

Dans mon cas, loop0 est déjà utilisé donc je me rabats sur loop1 :  

```bash
losetup -o 16450600 /dev/loop1 /dev/hda
```

On crée ensuite le *"mapper"* qui se chargera du chiffrement. Dans mon cas, il s'appelle *"toto"* et utilise l'algorithme par défaut (AES128). Pour plus d'infos, lisez la page de manuel de `cryptsetup`. Le programme vous demandera de saisir le mot de passe pour le chiffrement.  

```bash
cryptsetup create toto /dev/loop1
```

On vérifie que notre mapper a bien été créé à l'aide de `dmsetup ls` puis on peut créer et jouer avec notre partition :  

```bash
mkfs.ext2 /dev/mapper/toto
mount /dev/mapper/toto /mnt/test
echo test > /mnt/test/truc
umount /mnt/test
```

Quand on a fini on démonte le mapper et le périphérique de boucle :  

```bash
cryptsetup remove toto
losetup -d /dev/loop1
```

Si on effectue une recherche sur le disque dur, on trouve une occurrence pour `abcd`, 0 pour `test` et une seule pour `truc`. Notre partition est bien chiffrée et invisible.  

Seul problème, pour ne pas à avoir à mémoriser les commandes et l'offset de la partition, il est préférable de créer un script de montage et un autre du démontage. À vous de faire marcher votre imagination pour dissimuler ces scripts.

*Published January 11 2011 at 07:09*
