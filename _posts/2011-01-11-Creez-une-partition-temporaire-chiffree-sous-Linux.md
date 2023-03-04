---
title: "Créez une partition temporaire chiffrée sous Linux"
tags: [Cryptographie, Vie privée et anonymat]
---

L'opération est assez simple et fonctionnera sur les distributions équipées de `dm-crypt` (vérifier que le programme `cryptsetup` est présent).  

Il vous faut une partition à sacrifier pour l'utilisation d'un `/tmp` qui sera recréé à chaque démarrage avec une clef de chiffrement aléatoire (les données dans `/tmp` seront perdues à chaque arrêt du système d'exploitation).  

Chez moi j'ai utilisé `/dev/sda5` (une vieille partition `vfat` dont je me servais plus) qui sera reformatée en `ext2` pour l'occasion.  

On commence par créer une entrée dans `/etc/crypttab` :  

```
temp    /dev/sda5       /dev/urandom    tmp,cipher=aes-cbc-essiv:sha256
```

Cela provoquera la création d'un périphérique de chiffrement `/dev/mapper/temp`. L'option `tmp` permet de spécifier qu'il faut exécuter `mkfs` sur le mapper pour créer le système de fichier. En l'absence d'une correspondance dans `/etc/fstab`, le système `ext2` est utilisé.  

L'option `cipher` est nécessaire afin que `cryptsetup` sache comment chiffrer les données.  
Le périphérique `/dev/urandom` est utilisé comme clef aléatoire pour le chiffrement des données.  

Il faut ensuite créer une entrée correspondante dans `/etc/fstab` (options à modifier selon vos préférences) :  

```
/dev/mapper/temp     /tmp                 ext2       noexec                0 0
```

On redémarre la machine et normalement tout fonctionne :)  

Article sur le même sujet :  

[Créez une partition cachée sous Linux]({% link _posts/2011-01-11-Creez-une-partition-cachee-sous-Linux.md %})

*Published January 11 2011 at 09:25*
