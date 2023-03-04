---
title: "La prochaine mise à jour de AACS déjà dans les choux"
tags: [Cryptographie]
---

L'[AACSLA](http://www.aacsla.com/) continue d'utiliser son système de révocation des clés pour impeacher la lecture de nouveaux disques haute définition sur des lecteurs dont les clés ont été rendues publiques.  

La mise à jour vers ce que l'on appelle l'*"AACS version 3"* devrait être déployée dans ce but d'ici quelques jours, le 22 mai 2007, et être mise en place sur tous les supports HD-DVD et BluRay qui seront disponibles à la vente.  

Mais c'était sans compter sur les développeurs du logiciel de déchiffrement [AnyDVD](http://en.wikipedia.org/wiki/AnyDVD) qui proposent une version mise à jour de leur logiciel permettant d'effectuer une copie des médias protégés par _AACS v3_.  

La nouvelle [publiée sur Ars Technica](http://arstechnica.com/news.ars/post/20070517-latest-aacs-revision-defeated-a-week-before-release.html) nous informe que l'exploit est déjà *"visible"* [par le biais des HD-DVD de Matrix 2 et 3](http://forum.slysoft.com/showthread.php?t=4214&page=3) sortis en avance dans les rayons.  

L'article d'*Ars Technica* parle d'une nouvelle clé de volume trouvée par *SlySoft*, l'éditeur de *AnyDVD*, mais techniquement ça ne colle pas avec [ce que l'on a vu jusqu'à présent]({% link _posts/2011-01-08-AACS-casse.md %}).  

Pour que *SlySoft* dévoile sa mise à jour à un tel moment, il fallait, [comme le fait remarquer Freedom to Tinker](http://www.freedom-to-tinker.com/?p=1158), que l'éditeur ait gardé secrètement cette clé sous la main depuis un bon moment.  

Je pense ([et je ne suis pas le seul](http://episteme.arstechnica.com/eve/forums/a/tpc/f/174096756/m/929006105831?r=897003305831#897003305831)) que la clé en question doit plus correspondre à une *Device Key*, une clé qui est spécifique à (par exemple) une version d'un logiciel de lecture donnée. Les anciennes versions de *AnyDVD* se basaient apparemment sur des clés de *PowerDVD*. Évidemment, *AnyDVD* ne peut pas explicitement utiliser les clés d'un logiciel tiers. C'est pour cela que les clés qu'il utilise doivent être le résultat d'une opération combinant plusieurs clés à l'un des moment de l'algorithme _AACS_ (l'_AACS_ ce n'est pas seulement le jeu du chat et de la souris, c'est aussi jouer avec le feu sans jamais se bruler).  

Le fonctionnement de *AnyDVD* est encore un mystère à l'heure actuelle, mais déjà [discuté sur Doom9](http://forum.doom9.org/showthread.php?t=125945). On en saura peut-être plus d'ici peu.  

Quoi qu'il en soit, les pirates sont tellement en avance sur l'_AACSLA_ qu'ils en sont à attendre les révocations pour pouvoir publier aussitôt les clés toujours fonctionnelles.  

L'_AACSLA_ quant à lui continue inlassablement de révoquer ses clés et à menacer de poursuites judiciaires puisqu'il n'a plus que ce moyen pour essayer de garder la *"machine"* en fonctionnement (et ses clients par la même occasion).  

Autres articles relatifs à l'_AACS_ :  

[devloop :: AACS cassé]({% link _posts/2011-01-08-AACS-casse.md %})  

[devloop :: AACS de nouveau ridiculisé]({% link _posts/2011-01-09-AACS-de-nouveau-ridiculise.md %})  

[devloop :: 09F911029D74E35BD84156C5635688C0](https://web.archive.org/web/20140219070337/http://my.opera.com/devloop/blog/2007/05/02/09f911029d74e35bd84156c5635688c0)  

Certains ont trouvé une façon de représenter graphiquement la Processing Key en RGB :  

<http://en.wikipedia.org/wiki/Image:Free-speech-flag.svg>  

[09 f9: A Legal Primer (EFF)](http://www.eff.org/deeplinks/archives/005229.php)  

[AnyDVD method of operation](http://forum.doom9.org/showthread.php?t=122272) (date un peu)

*Published January 10 2011 at 07:04*
