---
title: "Les Questions Cons du Hacking : Peut-on spoofer son adresse IP sur Internet ?"
tags: [Réseau, Vie privée et anonymat]
---

S01E02: Peut-on spoofer son adresse IP sur Internet ?
-----------------------------------------------------

Et la réponse est OUI. C'est tout :)  

Il est évident que c'est possible puisque l'on sait que cela est déjà utilisé depuis longtemps par des attaques DDoS comme celles qui ont exploité (plus récemment) la fameuse commande [NTP MONLIST](https://blog.cloudflare.com/understanding-and-mitigating-ntp-based-ddos-attacks/).  

Il y a deux critères majeurs pour qu'une attaque de ce type réussisse :  

* un fort vecteur d'amplification, c'est-à-dire envoyer peu et recevoir beaucoup en retour
* une [réflection](https://en.wikipedia.org/wiki/Denial-of-service_attack#Reflected_.2F_spoofed_attack), c'est le terme utilisé pour signifier que si on envoie un paquet avec une IP spoofée alors le destinataire va répondre à l'IP indiquée par le paquet falsifié (qui pour le coup sera la cible de l'attaque)

Dans cet article quand je parle de spoofing je parle bien de forger les paquets pour changer l'adresse IP et non d'utiliser un proxy ou un VPN quelconque (le mot spoofing est fréquemment galvaudé).  

### Comment spoofer son IP sur Internet ?

Pour forger de tels paquets (pour TCP) ou datagrammes (pour UDP) on peut avoir recours à des outils comme [hping3](https://github.com/antirez/hping), [Nemesis](http://nemesis.sourceforge.net/) ou écrire ses propres outils avec [Scapy](http://secdev.org/projects/scapy/) (en Python) ou en C avec les sockets RAW.  

Toutefois, si vous faites le test chez vous en envoyant un paquet avec une IP falsifiée chez un ami qui a lancé *Wireshark* (après avoir créé une redirection NAT of course) vous risquez d'être déçu : il ne recevra probablement pas ce paquet.  

La raison la plus simple, c'est qu'à notre époque tous les particuliers disposent d'une box faisant office de routeur vers l'Internet et que ce routeur est capable de filtrer les paquets à l'arrivée ([ingress filtering](https://en.wikipedia.org/wiki/Ingress_filtering)) comme à la sortie ([egress filtering](https://en.wikipedia.org/wiki/Egress_filtering)). Et il n'a pas de raison valable de laisser filer un paquet avec une fausse adresse IP (pour pouvoir réellement tester il faudrait passer le routeur en mode bridge... à vos propre risques puisque vous exposez alors votre machine aux scans en tout genre).  

Si par chance ce paquet forgé parvient tout de même à passer votre routeur, il faut encore qu'il passe d'autres routeurs probablement filtrants de votre ISP puis ceux sur le chemin ([NSP](https://en.wikipedia.org/wiki/Network_service_provider), [AS](https://fr.wikipedia.org/wiki/Autonomous_System)) avant de toquer à la porte de l'ISP de votre ami puis son propre routeur. Mais [admettons](https://www.youtube.com/watch?v=wexVwQG95Ws) :)  

Plus vraisemblablement vous aurez à fouiller sur le web crado (dark-web ou assimilés) pour trouver une personne offrant (moyennant finance) un serveur permettant l'envoi de ces paquets spoofés, généralement vendu explicitement pour des attaques réseau.  

![Someone selling spoofed VPS services on a hacker forum](/assets/img/ip_spoofing/spoofed_vps.png)

Ainsi avec l'accès à un tel serveur (aucun serveur n'a été maltraité durant le montage) j'avais pu il y a quelque temps de ça tester l'envoi de 4 datagrammes dont les IPs sources étaient respectivement celles de *bing.com*, *facebook.com*, *google.com* et un serveur OVH.  

![Wireshark capture showing spoofed paquets for facebook and bing](/assets/img/ip_spoofing/spoofed.png)

Sur ces 4 datagrammes, seul celui dont l'adresse IP source était celle de Google ne m'est pas parvenu. Preuve que cela fonctionne, mais qu'il y a bien du filtrage sur le chemin.  

Mais ce serveur qui autorisait aveuglément l'envoi de paquets forgés où se situait-il ? Dans un pays de l'ex-union soviétique ? Dans un pays de l'Amérique Centrale ou du Sud [où il n'y a pas que les cyber-criminels qui y trouvent refuge ?](https://www.youtube.com/watch?v=ylgOY5YF1HE)  

En l'occurence ce serveur était hébergé chez nos voisins allemands (vive l'Europe) par [Contabo](https://contabo.com/).  

Surprenant ? En fait non.  

Si on se base sur [les résultats](https://spoofer.caida.org/recent_tests.php?as_include=&country_include=&no_nat=1&no_block=1) du projet [Spoofer](https://www.caida.org/projects/spoofer/) du *CAIDA* (*Center for Applied Internet Data Analysis*) on peut voir qu'il y a des réseaux partout à travers le monde permettant d'envoyer des paquets avec adresse IP falsifiée.  

Cela est très certainement la conséquence d'un laxisme de la part de ces entreprises. Il y a peut-être parfois des raisons techniques et économiques.  

Pour les réseaux qui eux filtrent les paquets on peut se demander jusqu'où va le filtrage. Depuis (par exemple) un serveur OVH pourrait-on spoofer l'IP d'un autre serveur OVH ? Si on incrémente juste l'adresse IP est-ce que cela passe ?  

### Que peut faire un attaquant avec de l'IP spoofing ?

Sur Internet pas grand-chose : les attaques de détournement de session avec des outils comme *Hunt* ou *Ettercap* requièrent de pouvoir se mettre en situation d'homme du milieu avant de surveiller les numéros de séquence TCP. Des scénarios sur Internet semblent plutôt capilotracté.  

Dès lors cette possibilité sera majoritairement exploitée dans des attaques DDoS. En TCP ont peu en profiter pour faire du [SYN flood](https://en.wikipedia.org/wiki/SYN_flood) et en UDP on exploitera un protocole quelconque avec un fort taux d'amplification.  

Même si ces types d'attaques sont toujours utilisés à notre époque, un botnet comme [Mirai](https://fr.wikipedia.org/wiki/Mirai_(logiciel_malveillant)) a montré que c'était plus simple et plus efficace de simplement pénétrer des objets connectés à la sécurité inexistante pour en faire des zombies...  

Pour plus d'informations sur le sujet, vous pouvez lire [cette présentation](https://idea.popcount.org/2016-09-20-strange-loop---ip-spoofing/) de *CloudFlare*.  

### Conclusion

C'est tout à fait possible de spoofer son IP sur Internet, mais pas depuis n'importe quel réseau. Cela se fera obligatoirement depuis un ISP qui ferme les yeux (volontairement ou non) sur le spoofing IP.  

Même avec cette possibilité certains paquets spoofés risquent de ne pas toucher leur cible en raison de routeurs qui appliquent des règles de filtrage en chemin.  

Si vous avez des questions cons (mais pas trop) que vous vous posez et qui ne nécessitent pas trop d'investigation pour y répondre, n'hésitez pas à me contacter par email.  


*Published July 01 2017 at 11:20*
