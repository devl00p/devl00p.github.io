---
title: "AACS de nouveau ridiculisé"
tags: [Cryptographie]
---

En février dernier, un certain *ATARI Vampire* du forum *Doom9* est parvenu à récupérer une (sub) Device Key du logiciel _WinDVD_.  

C'est aussi par ce logiciel que plusieurs bidouilleurs se sont fait les dents sur la protection *AACS* et [sont parvenus à la casser]({% link _posts/2011-01-08-AACS-casse.md %}) à plusieurs reprises.  

Comme on pouvait s'y attendre, le groupe *AACS Licensing Administrator* a finalement eu recours au système de révocation de *AACS* en obligeant l'éditeur de _WinDVD_ (_InterVideo_, filiale de _Corel_) à [mettre à jour son logiciel](http://www.01net.com/editorial/345818/piratage/une-rustine-pour-stopper-le-deverrouillage-des-dvd-haute-definition/) [qui incluera de nouvelles clés](http://www.referencement-internet-web.com/20070410-HD-DVD-Blu-ray-AACS-cles.php) [ainsi que de nouvelles protections anti](http://www.theregister.co.uk/2007/04/10/cracked_aacs_keys_revoked/) [rétro-ingénierie](http://fr.wikipedia.org/wiki/R%C3%A9tro-ing%C3%A9nierie).  

Le système de révocation est tel que les nouveaux disques HD-DVD ou BluRay seront illisibles sur l'ancienne version du logiciel _WinDVD_. Les utilisateurs se voient donc obligés d'effectuer une mise à jour de leurs logiciels s'ils souhaitent continuer à regarder des films.  

On se demande qui est le plus à plaindre dans cette histoire. Ce qui est sûr, c'est que malgré toutes les protections qui pourront être ajoutées, ce ne sera qu'une question de temps avant que les nouvelles clés soient trouvées.  

Ça n'a pas forcément d'utilité, mais si les clés sont divulguées puis mises à jour sans cesse, les consommateurs vont probablement aller voir ailleurs et la société perdra vite sa crédibilité. Les pirates ont par conséquent en bon moyen de pression sur les éditeurs de logiciels.  

Sans compter (et j'y reviens juste après) que les clés révoquées doivent être stockées sur les nouveaux disques et risqueraient de s'entasser, augmentant ainsi l'espace disque nécessaire pour placer un média protégé.  

Bref c'est le jeu du chat et de la souris, mais on se garde bien de la dire sur le site du [AACSLA](http://www.aacsla.com/home).  

Quelques petites 24 heures plus tard, c'est le système de révocation en question qui est mis à mal par *Geremia* et *arnezami* [sur le forum *Doom9*](http://forum.doom9.org/showthread.php?t=124294) et [*XBoxHacker BBS*](http://www.xboxhacker.net/index.php?topic=6866.20).  

*Geremia* a effectué ses tests sur le lecteur HD-DVD de la _Xbox_. Il a d'abord cherché à identifier le firmware utilisé en comparant le [chipset](http://fr.wikipedia.org/wiki/Chipset) avec ceux existant puis en le désassemblant.  

Après quelques heures d'analyse de code assembleur bizarre (`FR30`, kezako ?), il est parvenu à patcher le firmware pour retirer la procédure de vérification des clés révoquées.  

![AACS algorithm](/assets/img/host2.png)

Un peu plus tard, un certain *xt5* a mis à disposition [un programme](http://forum.doom9.org/showpost.php?p=987043&postcount=103) qui va modifier le code en mémoire pour bypasser la vérification, ce qui évite la désagréable tâche d'avoir à flasher le disque.  

Difficile de savoir qu'elle va être la réponse de l'_AACSLA_ et de _Microsoft_. S'il faut obliger les utilisateurs à mettre à jour leur firmware ça peut être problématique.  

[Clubic : Une nouvelle protection HD-DVD contournée](http://www.clubic.com/actualite-72260-protection-hd-dvd-contournee.html)  

[RegHardware : Hack exposes AACS 'hole'](http://www.reghardware.co.uk/2007/04/10/aacs_hold_exposed/)

*Published January 09 2011 at 14:36*
