---
title: "Bypass de firewall sur le port source"
tags: [firewall]
---

Un firewall n'est rien de plus qu'un ensemble de règles qui détermine ce qui passe sur un réseau et ce qui ne passe pas.  

Si les règles sont mal écrites, ou si le logiciel firewall est buggé ou peu évolué, il peut être possible de passer à travers ces règles pour accèder à des services normalement filtrés.  

Fixer un port source pour ses connexions est l'un des méthodes utilisées pour passer un firewall. Les pare-feux vérifient principalement les adresses IP ainsi que les ports source et destination de chaque paquet qui passe, ce qui permet d'écrire des règles assez facilement  

On distingue ensuite deux catégories de firewall : les [stateless](http://en.wikipedia.org/wiki/Stateless_firewall) et les [statefull](http://en.wikipedia.org/wiki/Stateful_firewall).  
Les firewalls *"statefull"* mémorisent l'état des connexions (demande de connexion, connexion établie...), ce que les *"stateless"* ne font pas.  

Mais certaines applications ou certains protocoles comme FTP sont de vrais casse-têtes pour le filtrage des paquets.  

Le protocole FTP indique en effet que le serveur renvoit les données depuis son port 20 vers un port du client. Par conséquent si un administrateur veut permettre aux personnes sur son réseau d'utiliser des clients FTP il va probablement autoriser tout paquet dont le port source est 20.  

Un attaquant pourra alors découvrir des services normalement cachés en effectuant un scan de port avec des paquets dont le port source est 20. L'option `-g` de Nmap permet de faire ça très facilement.  

Une fois que l'intrus aura trouvé un service accessible, il va devoir faire en sorte que ses connexions viennent du port source lui ouvrant l'accès à la machine.  
Pour cela j'ai relevé différentes solutions plus ou moins efficaces. Par la suite on considérera que l'attaquant possède l'adresse IP `192.168.0.2` et tente d'accèder au port 80 de la machine `192.168.0.3` en fixant son port source à 20.  

**Netcat 1.10**  
[Netcat](http://www.vulnwatch.org/netcat/) est le *"couteau suisse TCP/IP"*. Ce serait trop long de décrire toutes les opérations que l'on peut faire avec mais vous trouverez différents documents sur le sujet sur Internet.  
Notre visiteur l'utilisera de la façon suivante :  

```bash
netcat -v -p 20 192.168.0.3 80
```

Cela va ouvrir une connexion à destination du port 80 de la machine filtrée et avec le port source 20.  

Le premier souci c'est que netcat récupère ce qu'il doit envoyer sur l'entrée standard. Pour les protocoles utilisant des caractères ASCII ça va encore mais dans la majorité des cas il faut avoir recours à des redirections d'entrées/sorties.  
On pourrait alors chainer deux netcat, l'un écoutant sur un port en renvoyant ce qu'il reçoit vers l'entrée du second netcat (avec la commande précédente).  

Le second souci c'est que netcat ne fonctionne pas comme un serveur qui tournerait en fond pour réceptionner en continu les requêtes et convient mal à certains protocoles qui effectuent des connexions courtes et nombreuses (HTTP par exemple).  
La version Windows de netcat a bien une option `-L` pour l'écoute continue mais on croise à nouveau le problème des redirections.  

**KevProxy**  
[KevProxy](http://www.bournemouthbynight.co.uk/tools/kp.c) comble avec succès les lacunes que l'on avait avec netcat.  

Le programme a certes moins de fonctionnalités mais fait exactement ce dont on a besoin pour cet exercice. Il ouvre un port en local en créant un thread pour chaque connexion. Chaque connexion est renvoyée sur une ip et un port spécifié en prenant soin de modifier le port source.  

Pour l'utiliser dans notre cas on utilisera la commande suivante :  

```bash
kp 8080 192.168.0.3 80 20 v
```

Il n'y a plus qu'à lancer son navigateur sur localhost:8080 et on accèdera par notre tunnel au port 80 de la machine filtrée. Le *"v"* final est optionnel et ajoute de la verbosité.  
Un excellent outil qui mérite à être connu.  

**Fpipe 2.1**  
[Fpipe](http://www.foundstone.com/index.htm?subnav=resources/navigation.htm&subcontent=/resources/proddesc/fpipe.htm) est le célèbre outil de redirection de port de *Foundstone* et fonctionne sous Windows. Il fait tout ce que *KevProxy* peut faire et offre quelques options supplémentaires.  
La commande à lancer sera :  

```bash
fpipe -v -l 8080 -s 20 -r 80 192.168.0.3
```

Le principe est exactement le même que pour KP.  

**Netfilter / iptables**  
Quoi de mieux qu'un firewall pour passer un autre firewall ?  

Ici on va se servir des fonctionnalités de S[NAT](http://fr.wikipedia.org/wiki/Network_address_translation) de [Netfilter](http://www.netfilter.org/) pour réécrire au vol le port source des paquets à destination du port 80 de la machine `192.168.0.3` :  

```bash
iptables -t nat -A POSTROUTING -p TCP -m tcp -s 192.168.0.2 --dport 80 -j SNAT --to-source 192.168.0.2:20
```

Tout se fait de façon complétement transparente.  

Des documents sur le même sujet :  

[Ma solution du CTF Jangow avec du hole punching via FTP]({% link _posts/2022-01-09-VulnHub-Jangow-CTF-walkthrough.md %})

[Phrack : Breaking through a Firewall using a forged FTP command](http://www.phrack.org/archives/63/p63-0x13_Breaking_Through_a_Firewall.txt)  

[Nmap : Évitement de pare-feux/IDS et mystification](http://insecure.org/nmap/man/fr/man-bypass-firewalls-ids.html)  

[Pyramid BenHur Firewall Active FTP Portfilter Ruleset Results in a Firewall Leak](http://www.securiteam.com/securitynews/5WP0M0K7PS.html)

*Published January 09 2011 at 13:39*