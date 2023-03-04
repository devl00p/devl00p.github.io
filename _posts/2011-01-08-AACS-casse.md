---
title: "AACS cassé"
tags: [Cryptographie]
---

Il y a quelques jours, un certain *Arnezami* a [cassé la protection *AACS*](http://www.theregister.co.uk/2007/02/14/aacs_hack/) qui protège le contenu des disques HD-DVD et Blu-Ray en rendant publique la *"Processing Key"* utilisée dans le procédé de déchiffrement de tous les disques commercialisés jusqu'à présent.  

Ce qu'il faut comprendre dans cette histoire, c'est que tôt ou tard cette protection aurait été cassé comme l'ont été de nombreux systèmes de DRM.  

La protection *AACS* se base sur un ensemble de clés qui permet de rendre impossible (en réalité l'objectif est seulement de rendre plus difficile) l'exportation du contenu vers des supports jugés indésirables par les grandes sociétés de distribution (derrière *AACS* se cache *Disney*, *Intel*, *Microsoft*, *Matsushita* (*Panasonic*), *Warner Brothers*, *IBM*, *Toshiba*, et *Sony*) ou d'empêcher la lecture sur des lecteurs considérés comme pirates.  

Mais *AACS* ne demande pas à l'utilisateur d'effectuer une connexion à un serveur sur Internet pour effectuer une validation comme le fait Windows... Par conséquent, où sont situées les clés permettant de déchiffrer le contenu protégé ? Tout simplement sur le même disque !  

Ça peut sembler stupide, mais c'est la technique généralement utilisée par les systèmes de DRM. Bien sûr, ce n'est pas (censé être) aussi simple : la protection se base sur tout un tas d'algorithmes cryptographiques pour que les curieux ne tombent pas trop rapidement sur ces fameuses clés.  

Ajouté à ça les constructeurs de lecteurs (qui je le rappelle sont derrière *AACS*) ne vont pas hésiter à rajouter des protections supplémentaires sur leur matériel ou sur les logiciels de lecture de média qu'ils développent.  

Mais les développeurs savent bien qu'ils ne peuvent pas dissimuler continuellement des données dans le flux d'exécution de leur programme. Il y aura forcément un moment où ces données seront en clair. Bien sûr, ils s'arrangent pour que ces données soient aussitôt effacées de la mémoire, mais le mal est fait.  

Sur le célèbre forum du site [Doom9](http://www.doom9.org/), *Arnezami* a posté un schéma très pratique représentant l'algorithme de chiffrement utilisé par *AACS* :  

![AACS algorithm](/assets/img/aacs.png)

La partie gauche représente les données présentes sur le disque acheté dans le commerce. La partie de droite représente les données présentes sur le lecteur ainsi que les calculs effectués pour traiter les données.  
Notez bien le code graphique utilisé : les données sont représentées dans des rectangles blancs aux bords arrondis. Les fonctions sont représentées par des rectangles gris qui reçoivent des arguments symbolisés par les flèches.  

Les premières attaques réalisées se sont concentrées sur la dernière partie de l'algorithme, à savoir le déchiffrement du contenu. Pour cela il fallait seulement récupérer la *"Title Key"* (Kt).  

*Muslix64* a ouvert la danse [en annonçant sur le forum Doom9](http://forum.doom9.org/showthread.php?t=119871) la disponibilité de son logiciel *BackupHDDVD* qui permet de déchiffrer le contenu. Additionnellement, il expliquait dans [une interview](http://www.slyck.com/story1390.html) être parvenu à retrouver les _Title Key_ de plusieurs HD-DVD en analysant la mémoire de logiciels de lecture de disques HD-DVD durant leur utilisation. D'après bon nombre de posts, il s'agirait de *PowerDVD* ou *InterVideo WinDVD 8*.  

*BackupHDDVD* ne fait rien d'illégal. Il ne déchiffre pas les HD-DVD en un seul click. Pour déchiffrer un disque, il faut lui fournir la Title Key. Or cette clé est spécifique au support et non au film !! Il faut donc avoir quelques compétences en débogage, voire en reverse engineering pour retrouver la fameuse clé.  

Cela a tout de même permis de voir débarquer [le premier HD-DVD pirate disponible sur BitTorrent](http://www.theregister.co.uk/2007/01/18/hd-dvd_crack/)... D'autres ont suivi.  

La solution pour permettre à tout le monde de déchiffrer les données consiste à remonter un peu dans l'algorithme. La _Title Key_ est générée à partir de clés chiffrées stockées sur le disque et à partir d'une clé de volume (_Kvu_).  

Bingo ! Cette clé de volume est spécifique au film, car créée à partir d'un identifiant unique (_Volume ID_).  

À partir de là *AACS* est fortement chamboulé. Différents sites comme [HDKeys](http://www.hdkeys.com/) et [AACS Keys](http://www.aacskeys.com/) donnent des listes de clés de volume.  

*Muslix64* sort une nouvelle version de son logiciel qui se base non plus sur les _Title Keys_ mais sur ces clés de volume. [L'annonce](http://forum.doom9.org/showpost.php?p=924731&postcount=245) est une fois de plus faite sur *Doom9*.  

Ce n'est que quelque temps plus tard que [*Muslix64* réitérera son exploit avec Blu-Ray](http://www.theregister.co.uk/2007/01/23/blu-ray_drm_cracked/) et un nouveau logiciel (*BackupBluRay*).  

Vous vous demandez peut-être en regardant le schéma pourquoi les bidouilleurs ne sont pas montés directement à la source et n'ont pas publié les clés de périphériques (*Device Keys*) et les clés de séquences (*Sequence Keys*) pour les mettre dans une base de donnée.  

La raison, c'est que le standard *AACS* intègre un procédé de révocation permettant de rendre inutilisable un lecteur...  

Si quelqu'un publiait des clés correspondant à un lecteur, les ingénieurs chez *AACS* modifieraient les clés présentes sur les prochains disques commercialisées de façon à ce que le lecteur piraté ne puisse plus rien lire de nouveau. Vous trouverez plus d'explications chez *Freedom to Tinker* [ici](http://www.freedom-to-tinker.com/?p=1107) et [ici](http://www.freedom-to-tinker.com/?p=1110).  

La dernière étape a été achevée par *Arnezami*. Il a débuté [une magnifique discussion](http://forum.doom9.org/showthread.php?t=121866) sur *Doom9* en annonçant avoir trouvé le *Volume ID* du film *KingKong*.  

Ce *Volume ID* est une structure de données qui pourrait être définie de la façon suivante en C :  

```c
struct VolumeID {
  uchar MediaType; // 0x40
  uchar Reserved;
  uchar UniqueNumber[12];
  uchar Reserved[2];
};
```

Dans cette structure, le premier octet est toujours **fixé** à `0x40`. Les octets réservés sont par convention fixés à un octet nul.  

Il reste alors l'ID (*UniqueNumber*) qui après plusieurs observations semble être **prévisible**.  

Par exemple pour *KingKong*, cet ID a pour valeur :  

`09 18 20 06 08 41 00 20 20 20 20 20 ` 

Les premiers octets correspondent à la date de production : le `09/18/2006 à 8h41`. Vient ensuite un octet nul et des espaces pour remplir l'espace restant.  

Cela a été validé à l'aide d'autres disques pris comme exemple.  

Mais tous les disques ne se basent pas sur le principe de la date. Ainsi l'ID utilisé pour le film *Serenity* commence par `53 45 52 45 4e 49 54 59`, ce qui se révèle être le code héxadécimal de... *"SERENITY"*.  

Mais l'objectif d'*Arnezami* est de remonter jusqu'à la *Media Key* (_Km_). Avec la _Km_ et le *Volume ID* on pourra facilement générer les clés de volume.  

Pourquoi c'est si important ? J'avoue que j'ai eu beaucoup de mal à comprendre au début...  

Dans la discussion un certain *noclip* prétendait que le même *Media Key Block* (_MKB_) était utilisé pour tous les disques utilisés jusqu'à présent... information vite réfutée par *evdberg* qui possède des disques avec des MKB différents.  

C'est à ce moment qu'*Arnezami* a évoqué la *"Processing Key"*. Lui qui a beaucoup fouillé dans les spécifications d'*AACS* a relevé l'information suivante :  

> Once the device has the correct Device Key D, it calculates a Processing Key K using AES-G3 as described above.  
> Using that Processing Key K and the appropriate 16 bytes of encrypted key data C, the device calculates the 128-bit Media Key Km as follows:  
> Km = AES-128D(K, C) XOR (00000000000000000000000016 || uv)  
> The appropriate encrypted key data C is found in the Media Key Data Record in the Media Key Block.
>

Effectivement on peut remonter à ce niveau puisque le fameux `C` est lisible sur le disque dans le *Media Key Block*. Seul problème : comment est généré la *Processing Key* ?  

Tout le monde (même *Arnezami*) s'accordent sur l'hypothèse que cette clé soit générée à partir des *Device Keys*.  

Quelque temps après il nous faisait part de ses avancés en publiant la *Media Key* (Km) de *KingKong*.  

Il est ensuite revenu en révélant la fameuse *Processing Key* qui à la surprise générale semble être indépendante de tous calculs et peut être utilisée pour déchiffrer **tous** les disques commercialisés jusqu'à présent.  

Le plus drôle dans tout ça, c'est qu'à aucun moment il n'a utilisé d'outils de reverse-engineering... juste des logiciels d'analyse de la mémoire.  

Le changement de cette clé par les personnes derrière l'*AACS* n'aurait pas d'effet : la nouvelle clé serait aussitôt trouvée et publiée sur Internet.

*Published January 08 2011 at 15:17*
