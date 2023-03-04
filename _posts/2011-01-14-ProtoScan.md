---
title: "ProtoScan"
tags: [Réseau]
---

Introduction
------------

`ProtoScan` est un logiciel en ligne de commande qui permet de déterminer quels sont les protocoles supportés par une machine distante. `ProtoScan` ne fonctionne que sous plateforme Linux et se base sur la librairie du C standard ([glibc](http://www.gnu.org/software/libc/libc.html)).

Partie Technique
----------------

### Rappels sur le protocole IP

Le Protocole Internet (IP) permet à plusieurs machines de communiquer entre elles. Toutefois, ce protocole ne permet pas d'échanger des données, il sert de support à des protocoles de plus haut niveau qui se chargent du transport des données.  

Le système de support entre protocoles est le suivant : le logiciel que vous utilisez va générer des données dans un protocole spécifique. Dans l'exemple d'un navigateur de page web, ce dernier va générer du HTTP. Celui-ci est un protocole de haut niveau et ne peux pas transiter pur sur le réseau. L'ordinateur va donc rajouter l'entête du protocole servant de support (TCP) puis rajoutera l'entête du protocole servant de support au TCP, à savoir IP.  

À l'opposé, le serveur dont vous désirez lire les pages web va devoir retirer les entêtes les un après les autres pour parvenir à ce qui l'intéresse, à savoir la requête HTTP générée par votre navigateur.  

Seulement comment le serveur fait-il le tri parmi toutes les données qu'il reçoit ? Une fois qu'il a retiré l'entête IP, il est tout à fait possible que ce qui suit ne soit pas du TCP mais de l'UDP, du GGP ou un autre protocole...  

En fait, c'est [l'entête IP](http://www.frameip.com/enteteip/) qui indique quel est le protocole qui suit. L'entête IP possède en effet un champ 'protocol' qui identifie le protocole supérieur par un chiffre bien définit ; ainsi si ce champ a pour valeur 6 alors le serveur saura qu'il s'agit du protocole TCP.  

`Protoscan` se base sur ce champ pour envoyer des données. Nous verrons tout à l'heure pourquoi.  

### Rappels sur le protocole ICMP

Le protocole IP n'est pas un protocole 'fiable' (voir [Etude IP sur SupInfo](http://www.supinfo-projects.com/fr/2003/protocole_ip/1/)). Il se fiche bien se savoir si les données arrive effectivement à destination et si elles arrivent en bon état. Pour combler cette lacune le protocole ICMP (Internet Control Message Protocol) a été créé. Comme son nom l'indique, il se charge d'informer des problèmes rencontrés par les paquets IP.  

Bien qu'IP et ICMP soient des protocoles à part entière, ils sont indissociables l'un de l'autre. Un constructeur informatique ne peut pas implémenter l'IP sans ICMP et vice-versa.  

Le protocole ICMP permet entre autres de savoir si la machine que l'on souhaite contacter est en marche (commande ping), ou de connaître les routeurs par lesquels passent nos données (commande traceroute). Quand on connait mieux le protocole ICMP on s'aperçoit qu'il permet d'obtenir des informations intéressantes sur une machine, comme les ports UDP fermés, si la machine se situe derrière un firewall, ou encore si un protocole est supporté ou non par la machine en question.  

C'est ce dernier cas qui nous intéresse.

Fonctionnement de ProtoScan
---------------------------

Le rôle de `ProtoScan` est de déterminer quels sont les protocoles supportés par une machine distante. Pour cela, il va délibérément provoquer des erreurs qui lui permettront de recevoir les messages ICMP concernant les protocoles supportés.  

`ProtoScan` va envoyer des paquets malformés. Ces paquets ne sont toutefois pas générés au hazard : ils s'arrêtent à l'entête IP (aucun protocole ne se trouve après).  

Pour observer le comportement d'une machine face à ces paquets malformés, nous allons faire des tests avec [Hping](http://www.hping.org/), un logiciel qui permet de générer ses propres paquets (il faut être root).

```console
# hping3 -c 1 --rawip --ipproto 6 127.0.0.1
HPING 127.0.0.1 (lo 127.0.0.1): raw IP mode set, 20 headers + 0 data bytes
[|tcp]
--- 127.0.0.1 hping statistic ---
1 packets tramitted, 0 packets received, 100% packet loss
round-trip min/avg/max = 0.0/0.0/0.0 ms
```

D'abord quelques éclaircissements sur la ligne de commande :  

`-c 1` permet de n'envoyer le paquet qu'une seule fois  

`--rawip` permet de générer soit même les entêtes IP  

`--ipproto 6` fixe le champ 'protocol' de l'entête IP à 6. Cela correspond à TCP
la ligne se termine bien évidemment avec l'adresse de la machine destinataire.  

Dans cet exemple les statistiques nous montrent clairement que la machine qui a reçu notre paquet n'a pas généré d'erreur. Il faut dire aussi que le protocole TCP est un protocole supporté par presque toutes les machines réseaux.  

Essayons maintenant avec un protocole moins connu, par exemple HMP (Host Monitoring Protocol) qui est désigné par la valeur 20.

```console
# hping3 -c 1 --rawip --ipproto 20 127.0.0.1
HPING 127.0.0.1 (lo 127.0.0.1): raw IP mode set, 20 headers + 0 data bytes
ICMP Protocol Unreachable from ip=127.0.0.1 name=localhost
--- 127.0.0.1 hping statistic ---
1 packets tramitted, 1 packets received, 0% packet loss
round-trip min/avg/max = 0.0/0.0/0.0 ms
```

Cette fois, la machine nous a renvoyé un paquet. Il s'agit d'un paquet ICMP dont le libellé est 'Protocol Unreachable' qui nous informe clairement que le protocole que nous avons demandé (HMP) n'est pas supporté par la machine.  

Pour connaître tous les protocoles supportés par une machine distante il suffirait donc de répéter la commande pour toutes les valeurs possibles du champ 'protocol' fixé par l'option ipproto de Hping.  

Théoriquement cela fait 256 possibilités. En pratique il n'y a que 136 protocoles reconnus pour l'instant (Les protocoles et leur numéro sont définis dans le fichier `/etc/protocols` sur un système Linux).  

`ProtoScan` se charge de tester toutes les possibilités et affiche les résultats dans un format compréhensible. Pour utiliser correctement `Protoscan` il suffit de passer l'adresse de la machine en argument :

```console
# ./protoscan 127.0.0.1
        Launching scan...
Protocol icmp [1] supporte
Protocol igmp [2] supporte
Protocol ipv4 [4] supporte
Protocol tcp [6] supporte
Protocol udp [17] supporte
        Scan done!
```

`Protoscan` a été programmé en C et repose sur les librairies standard, par conséquence, il ne nécessite pas l'installation d'un autre logiciel ou d'une librairie spéciale.  

Compilation : `gcc -o protoscan protoscan.c`  

[Télécharger le code source protoscan.c](/assets/data/protoscan.c)

*Published January 14 2011 at 17:06*
