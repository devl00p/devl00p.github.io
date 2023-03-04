---
title: "Les Questions Cons du Hacking : Un reverse shell anonyme c'est possible ?"
tags: [Réseau, Tor, Vie privée et anonymat]
---

S01E03: Un reverse shell anonyme c'est possible ?
-------------------------------------------------

C'est une excellente question et je me remercie de me l'avoir posé !  

Un connect-back ou reverse shell anonyme, c'est un peu le Saint Graal, la Chimère, le fantasme, la salope sauvage de tout hacker. Tout le monde n'a pas goûté à son petit goût fumé, mais oui ça existe !  

Avant toute chose et dans le but d'éviter un hors sujet, rassemblons-nous les neurones pour définir la situation ainsi que ce que l'on souhaite entendre par *anonyme*.  

Ici on exclura toute analyse post-intrusion donc on laisse tomber le binaire qui demande l'adresse IP de connect-back sur l'entrée standard (pour éviter qu'elle ne soit hardcodée) et aussi le binaire chiffré / packé / anti-debug / timebomb qui fait tout pour rendre compliqué la récupération d'une IP pourtant hardcodée.  

On part donc du principe qu'un administrateur a lancé un `tcpdump` et qu'il voit tout ce qu'il se passe sur le réseau.  

On exclut aussi le tunneling de ninja par [DNS](https://github.com/sensepost/DNS-Shell), [ICMP](http://icmpshell.sourceforge.net/) et [compagnie]({% link _posts/2011-01-11-Pseudo-terminaux-portes-derobees-telnet-et-tunneling.md %}). On oublie aussi les protocoles que l'admin ne penserait pas à surveiller ([SCTP](https://en.wikipedia.org/wiki/Stream_Control_Transmission_Protocol) & co).  

Par anonyme on entendra ici que l'adresse IP du connect-back n'est pas celle de l'attaquant et qu'il est en mesure d'utiliser plusieurs relais pour dissimuler sa véritable adresse IP.  

Evidemment on suppose qu'il dissimule déjà son IP avec sa RCE, sinon ça n'a pas grand intérêt :D  

### Pourquoi vouloir un reverse shell ?

C'est vrai ça ! [A quoi bon grand-père](https://www.youtube.com/watch?v=qQHUfNPdaXY) ?  

Souvent, avant d'obtenir un shell, l'attaquant dispose d'une RCE (exécution de commandes à distance) de misère (souvent à travers un script PHP, comme celui décrit dans [Tales of PenTest #1]({% link _posts/2017-07-07-Tales-of-PenTest-1-Celui-qui-donnait-la-permission-FILE.md %})) qui ne conserve pas l'environnement d'une commande à l'autre (le plus triste, c'est le répertoire courant) et qui ne permet pas d'utiliser des programmes interactifs comme Vim, (h)top et compagnie.  

Avec IRC
--------

La technique est connue depuis la nuit des temps : l'attaquant lance sur la cible un bot IRC qui va rejoindre un channel (si possible caché et protégé par une clé).  
 L'attaquant n'a plus qu'à joindre la channel et via des messages spéciaux (préfixes) il fait passer des commandes au bot qui les exécute et retourne l'output via IRC.  

C'est couramment utilisé par les botnets car l'attaquant peut laisser des commandes sur le channel à l'intention de tous les bots qui sont présents simultanément.  

Avantages :  

* L'attaquant peut se connecter au serveur IRC via un système (Tor, VPN ou interface web comme [Mibbit](https://mibbit.com/)) qui renforce son anonymat.
* Le bot peut avoir un mécanisme de conservation de l'environnement
* On trouve plein de codes sources de ce style, du [plus ancien orienté DDoS en C](https://packetstormsecurity.com/irc/kaiten.c) à [celui en Python avec support du SSL](https://pastebin.com/peVD4td9)
* Il existe des serveurs IRC écoutant sur les ports 80 ou 443 (pour les règles de firewall)
* Le trafic peut sortir via un proxy HTTP (si il supporte *CONNECT*)

Inconvénients :  

* La technique est connue des IDS
* La technique est connue des AVs (le bot peut être détecté)
* En raison des protections anti-flood propres à IRC on imagine mal tunneler un htop ou un Vim donc l’interaction restera très basique

Avec HTTP
---------

À une époque les créateurs de malware ont délaissé les C&C IRC pour se retrancher vers le web.  

Le principe n'est pas très éloigné de l'IRC. Ici on aura un site internet sur lequel les bots signalent leur existence et vont chercher des commandes que le botmaster aurait laissé.  

Avantages :  

* L'attaquant peut se connecter sans problèmes via Tor et autres proxies quelconques
* On peut trouver du code existant, mais il est préférable de le relire à deux fois (entre vulnérabilités et backdoors)
* On peut laisser des commandes à un bot même s'il n'est pas là (la commande est stockée en base de données, le bot vient la chercher quand il se connecte)
* Pas de connexion permanente contrairement à IRC donc plus furtif
* Web donc généralement pas de problématiques de firewall ou de proxy

Inconvénients :
* Peut être long et laborieux de coder soit même le site
* Il faut enregistrer et créer le site tout en préservant son anonymat
* Le protocole HTTP complexifie la conservation de l'environnement, car les connexions sont ponctuelles
* A quoi bon troquer une RCE web contre un C&C web ?

Avec Ngrok
----------

[Ngrok](https://ngrok.com/) se présente comme un *"tunnel sécurisé vers localhost"*.  

Un peu comme les deux solutions que l'on a vues précédemment, Ngrok offre un point de rendez-vous entre la cible et son attaquant.  

On peut utiliser Ngrok pour rendre accessible un service derrière un NAT. Dans ce cas Ngrok va créer soit un sous domaine de ngrok.io (pour les tunnels HTTP et HTTPS) qui redirigera les requêtes vers votre service local, soit ouvrir un port sur `x.tcp.ngrok.io` (`x` étant un entier commençant à 0) qui redirigera les paquets vers votre service local.  

La création d'un tunnel se fait via une connexion sur le port 443 de `tunnel.us.ngrok.com` (le serveur dépend probablement de la région que vous sélectionnez).  

Quand quelqu'un se connecte au sous domaine ou au port sur `x.tcp.ngrok.io`, les données sont retransmises sur le tunnel qui a été préalablement établit.  

On peut donc utiliser Ngrok dans deux configurations :  

* Lancer ngrok sur la cible pour rendre accessible un service qui aurait été normalement injoignable (ssh, rdp, backdoor écoutant sur 127.0.0.1)
* Lancer ngrok sur la machine de l'attaquant afin que l'IP du connect-back soit celle du Ngrok et non celle de l'attaquant

Avantages de la première méthode (qui sort du sujet du connect-back) :  

* Ngrok est codé en Go donc les exécutables sont des binaires statiques facilement déployables (copier, exécuter)
* La cible ne voit qu'une connexion sur un port HTTPS vers un serveur AWS... seems legit
* l'attaquant peut utiliser un système d'anonymisation quelconque pour joindre le tunnel Ngrok, il n'a pas à s'embêter à lancer un service et NATer un port
* le binaire Ngrok est clean (c'est juste un outil d'administration) donc non détecté par les antivirus

Inconvénients :  

* L'éventuelle backdoor locale qui se retrouve dans la liste des processus de la cible et netstat
* Ngrok qui se retrouve aussi dans netstat (mais en connexion sortante) et dans la liste des processus

Ngrok et connect-back
---------------------

Pour la suite de l'article, on va se concentrer sur la seconde configuration, à savoir l'attaquant a lancé Ngrok sur sa machine et la cible fera un connect-back sur le tunnel Ngrok.  

On est donc proche des cas de figure HTTP et IRC vu précédemment et si on inclut Tor dans tout ça on peut représenter la communication de cette façon :  

![Meterpreter through Tor through Ngrok](/assets/img/ngrok/ngrok_tor_meterpreter.png)

Ngrok différencie les tunnels servant à relayer du HTTP(S) de ceux relayant directement du TCP.  

L'avantage des tunnels HTTP(S) est qu'il suffit de lancer l'exécutable Ngrok avec comme paramètre "http" suivi du port du service web local.  

Par exemple `./ngrok http 7777`  

On obtient en retour une interface de statut ncurses avec l'URL ngrok générée (sur la capture, c'est le port 8000 et non 7777, mais peu importe).  

![Ngrok http tunnel port 8000](/assets/img/ngrok/ngrok_http_8000.png)

Le sous domaine alloué par *Ngrok* accepte alors les connexions sur les ports 80 et 443. Le port 443 a un certificat valide. On profite donc d'un chiffrement de notre tunnel chez la cible :)  

![Ngrok tunnel valid certificate](/assets/img/ngrok/ngrok_https_certificate.png)

Est-ce que l'on peut abuser du tunnel HTTP pour relayer autre chose ?  

Essayons d'envoyer des données non conformes HTTP :  

```console
$ ncat 3b9ad5f5.ngrok.io 80 -v
Ncat: Version 6.01 ( http://nmap.org/ncat )
Ncat: Connected to 2600:1f16:59e:b200:dd1c:548d:63ef:7119:80.
plop
HTTP/1.0 400 Bad request
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<html><body><h1>400 Bad request</h1>
Your browser sent an invalid request.
</body></html>
Ncat: 5 bytes sent, 187 bytes received in 8.26 seconds.
```

Il semble que Ngrok fasse office de proxy web.  

Essayons d'envoyer une requête HTTP sans le Host :  

```console
$ ncat 3b9ad5f5.ngrok.io 80 -v
Ncat: Version 6.01 ( http://nmap.org/ncat )
Ncat: Connected to 2600:1f16:59e:b200:dd1c:548d:63ef:7119:80.
GET / HTTP/1.0

HTTP/1.1 404 Not Found
Content-Length: 17
Connection: close
Content-Type: text/plain

Tunnel  not found
Ncat: 16 bytes sent, 108 bytes received in 6.33 seconds.
```

Et si on émet une requête valide :  

```console
$ ncat 3b9ad5f5.ngrok.io 80 -v
Ncat: Version 6.01 ( http://nmap.org/ncat )
Ncat: Connected to 2600:1f16:59e:b200:dd1c:548d:63ef:7119:80.
GET / HTTP/1.1
Host: 3b9ad5f5.ngrok.io
```

On reçoit sur notre port 7777 :  

```
Ncat: Version 6.01 ( http://nmap.org/ncat )
Ncat: Listening on :::7777
Ncat: Listening on 0.0.0.0:7777
Ncat: Connection from ::1.
Ncat: Connection from ::1:50685.
GET / HTTP/1.1
Host: 3b9ad5f5.ngrok.io
X-Forwarded-For: dead:beef:cafe:babe:133t:a1cd:c001:3a69
```

Là ça passe. On remarque aussi qu'il relaye l'adresse IP du client qui s'est connecté au tunnel (soit l'IP de la cible dans cette configuration).  

On ne peut donc faire passer que du HTTP(S) via ce type de tunnel. Est-ce que l'on peut en tirer quelque chose avec Metasploit ?  

D'après mes tests si on tente de faire passer un Meterpreter http via le tunnel http :  

* Ça ne fonctionne qu'avec un Meterpreter HTTP non-stager
* On peut exploiter la fonctionnalité SSL du tunnel Ngrok mais il faut que le handler Meterpreter soit lui http (pas de https vers https)
* C'est vraiment très instable (ngrok a visiblement du mal avec les requêtes générées par Meterpreter, la session aura une durée de vie très limitée)

![MsfVenom https meterpreter generation](/assets/img/ngrok/msfvenom_reverse_https.png)

![Meterpreter http handler receiving reverse shell from Ngrok tunnel](/assets/img/ngrok/metasploit_handler.png)

Retranchons-nous maintenant vers les tunnels TCP.  

Il suffit de remplacer `http` par `tcp` dans la commande : `./ngrok tcp 7777`  

Cette fois il y a des étapes supplémentaires :  

```
Tunnel session failed: TCP tunnels are only available after you sign up.                                                                                                                                                                     
Sign up at: https://ngrok.com/signup                                                                                                                                                                                                         

If you have already signed up, make sure your authtoken is installed.                                                                                                                                                                        
Your authtoken is available on your dashboard: https://dashboard.ngrok.com                                                                                                                                                                   

ERR_NGROK_302
```

Il faut donc se rendre sur la page *https://ngrok.com/signup* et créer un compte pour récupérer un token d'activation.  

![Signup on Ngrok](/assets/img/ngrok/ngrok_tcp_signup.png)

Les bons points :  

* On peut accéder au site via Tor, VPN, etc
* On a une adresse email à saisir, mais aucune vérification n'est faite (l'adresse mail peut ne pas exister).
* Pas de captcha
* On peut avoir des informations de statut sur le tunnel via le site

![Ngropk tunnel status via web interface](/assets/img/ngrok/ngrok_tcp_status.png)

C'est donc entièrement automatisable.  

La seule restriction est finalement de donner un mot de passe plus long que 10 caractères.  

Une fois le compte créé on obtient le token qu'il faut valider de cette façon :  

```console
$ ./ngrok authtoken 6ZuSho4BXgfbRB7v7qcR2_3Wnxf7fCBc74zBDP1x1i6
```

On obtient une réponse de ce style :  

```
Authtoken saved to configuration file: /home/devloop/.ngrok2/ngrok.yml
```

Il suffit alors de relancer la première commande Ngrok pour créer le tunnel.  

![Ngrok tcp tunnel](/assets/img/ngrok/ngrok_tcp_conn.png)

Cette fois, on peut faire passer tout ce que l'on souhaite à travers le tunnel TCP, même un stager (`windows/meterpreter/reverse_tcp`).  

Attention tout de même, il y a des petits curieux qui scannent les ports de `0.tcp.ngrok.io` en espérant trouver des services croustillants, mais je ne suis pas sûr qu'ils tiltent en voyant un stager Meterpreter dans leur Nmap :D  

Avantage : on peut vraiment faire passer tout type de communication TCP.  

Inconvénient : on ne choisit par le numéro de port (quoi que l'on puisse réserver une adresse Ngrok d'après [la documentation](https://ngrok.com/docs#tcp))  

Mais ce serait vraiment [vicieux](https://www.youtube.com/watch?v=xdNDv6yygI0) de demander plus :P  

### Configuration Ngrok avancée

Ngrok a quelques pépites supplémentaires à offrir que l'on peut voir en lisant [la documentation](https://ngrok.com/docs#config).  

**Proxy socks**  

Un rajoutant une ligne au fichier de configuration *ngrok.yml* on peut spécifier un proxy SOCKS pour faire par exemple passer le tunnel à travers Tor avant qu'il atteigne le serveur de Ngrok (et ça semble plus fiable que d'essayer de socksifier Ngrok, peut-être une particularité de *Go*) :  

```yaml
socks5_proxy: "socks5://127.0.0.1:9050"
```

**Pas de logs**  

Ça peut être utile si c'est la cible qui fait tourner Ngrok  

```yaml
log: false
```

**Choisir la localisation du serveur Ngrok**  

Un serveur Amazon aux USA c'est pour le moins discret, mais si la cible est au Japon, on peut spécifier une autre région pour le tunnel.  

Les serveurs sont en Ohio (us), à Francfort (eu), Singapour (ap) et Sydney (au)  

```yaml
region: us
```

**Pas d'interface de contrôle**  

Par défaut Ngrok lance un service web avec une API REST sur le port 4040 (https://ngrok.com/docs#client-api)  

Cette API permet d'avoir un état des tunnels, des statistiques, etc. On peut désactiver l'écoute sur ce port de cette manière :  

```yaml
web_addr: false
```

*Published July 22 2017 at 15:16*
