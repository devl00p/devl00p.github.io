---
title: "Utilisations alternatives du protocole BitTorrent"
tags: [Coding, Réseau]
---

## Introduction

Le protocole BitTorrent est un protocole de transfert de données Poste à poste (P2P) qui est devenu très populaire. Il supporte le multisourcing et permet de télécharger parallèlement plusieurs blocks d'un même fichier.  

Il est centralisé autour d'un *"tracker"* qui correspond à un annuaire de personnes qui partagent un fichier à un moment donné. Quand un client récupère cet annuaire, il peut se connecter à chaque client pour négocier le téléchargement d'un ou plusieurs morceaux de fichiers.  

La recherche de fichier est elle complétement décentralisée, on ne demande pas au tracker s'il possède le fichier que l'on recherche. Il faut pour télécharger une ressource, disposer d'un fichier métainfo `.torrent` qui décrit les fichiers et le tracker.  

Le protocole BitTorrent est aussi connu pour sa faculté à charger la bande passante des peers. Le protocole est fait de telle façon que le tracker n'a que peu d'informations à échanger avec les clients.  

Dans cet article je vous présenterais une partie du protocole BitTorrent qui correspond à la traduction du début de [la spécification](http://wiki.theory.org/BitTorrentSpecification) puis je parlerais des utilisations alternatives qui peuvent être faites de ce système.  

## Spécifications du Protocole Bittorrent v1.0  

### Présentation  

BitTorrent est un protocole d'échange de fichier peer-to-peer conçu par *Bram Cohen*. Visitez son site à <http://www.bittorrent.com>. BitTorrent est conçu pour faciliter les transferts de fichiers entre plusieurs peers sur des réseaux non fiables.  

### Objectif  

L'objectif de cette spécification est de documenter la version 1.0 du protocole BitTorrent dans les détails. La page de spécification du protocole faite par _Bram_ expose les grandes lignes du protocole dans des termes simples et manque de détails sur certains points. Notre souhait est que ce document devienne la spécification officielle, écrite à l'aide de termes clair et sans ubiquité, qui peut aussi bien être utilisée comme base pour des discussions que pour des implémentations futures.  

Ce document se veut être tenu à jour et utilisé par la communauté de développement BitTorrent. Tout le monde est invité à contribuer à ce document, en gardant à l'esprit que son contenu doit représenter le protocole actuel, déjà déployé dans un bon nombre d'implémentations clientes.  

### Conventions  

Dans ce document, différentes conventions sont utilisées afin de présenter les informations de façon concise et sans équivoque.  

* peer contre client : Dans ce document, un peer est n'importe quel client BitTorrent participant au téléchargement. Le client est aussi un peer, cependant il s'agit du client BitTorrent fonctionnant localement sur la machine.
* piece contre block : Dans ce document, un *"piece"* (morceau) correspond à une portion des données téléchargées, décrite dans le fichier métainfo, qui peut-être validé par un hash SHA1. Un block est une portion de données qu'un client peut demander à un peer. Un *"piece"* est constitué de deux blocks ou plus, qui peuvent ensuite être validés.

### bencodage  

Le bencodage est une méthode permettant de spécifier et d'organiser les informations dans un format court. Cette méthode supporte les types suivants : chaine de caractères, entiers, listes et dictionnaires.  

#### Chaines de caractères  

Les chaines de caractère sont codées de la façon : `<longueur de la chaine en base 10 ASCII>:<chaine de caractères>`
Notez qu'il n'y a aucun délimiteur de début et de fin.  

Exemple : `4:spam` représente la chaine spam  

#### Entiers

Les entiers sont encodés de la façon suivante : `i<entier en base 10 ASCII>e ` 

Le `i` initial et le `e` de fin sont les délimiteurs. Il est possible d'avoir des entiers négatifs comme `i-3e`. Il est interdit de préfixer le nombre avec un zéro comme dans `i04e`. Cependant, `i0e` est valide.  

Exemple : `i3e` représente l'entier 3  

Note : le nombre maximum de bits pour cet entier n'est pas spécifié, mais il s'agit généralement d'un entier signé de 64 bits qui permet de manipuler des gros fichiers (dépassant les 4Go).  

#### Listes

Les listes sont encodées selon le format : `l<valeurs bencodées>e`  

Le `l` et le `e` sont les délimiteurs de début et de fin. Une liste peut contenir n'importe quel type bencodé, y compris d'autres listes...  

Exemple : `l4:spam4:eggse` représente une liste composée de deux chaines : `["spam", "eggs"]`  

#### Dictionnaires

Les dictionnaires sont encodés selon le modèle suivant : `d<chaine bencodée><élément bencodé>e`

Le `d` et le `e` servent de délimiteurs. Notez que les clés doivent être des chaines bencodées. Les valeurs peuvent être de n'importe quel type bencodé, aussi bien les entiers, les chaines, les listes ou d'autres dictionnaires. Les clés doivent être des chaines et apparaître dans l'ordre alphabétique. Les chaines doivent pouvoir être comparées par une comparaison binaire, en opposition à une comparaison spécifique à une culture.  

Exemple : `d3:cow3:moo4:spam4eggse` représente le dictionnaire `{"cow"=>"moo","spam"=>"eggs"}`

Exemple : `d4:spaml1:a1:bee` représente le dictionnaire `{"spam"=>["a","b"]}`

Exemple : `d9:publisher3:bob18:publisher.location4:home17:publisher-webpage15:www.exemple.come`

### Structure de fichier métainfo  

Toutes les données dans le fichier métainfo sont bencodées. La spécification pour le bencodage est définie ci-dessus.  

Le contenu d'un fichier métainfo (un fichier avec une extension `.torrent`) est un dictionnaire bencodé, contenant les clés listées ci-dessous. Toutes les chaines de caractères sont encodées en UTF-8.  

* `info` : un dictionnaire qui décrit les fichiers du torrent. Il y a deux formes possibles : une dans le cas où le torrent correspond à un seul fichier sans structure de répertoire et le cas où l'on a affaire à un torrent *multi-fichiers* (voir détails plus loin).
* `announce` : l'URL d'annonce du tracker (chaine de caractères)
* `announce-list` : (optionnel) c'est une extension de la spécification officielle qui est aussi à compatibilité ascendante. Cette clé est utilisée pour implémenter une liste de trackers de secours. La spécification complète peut être lue [ici](http://home.elp.rr.com/tur/multitracker-spec.txt)
* `creation date` : (optionnel) la date de création du torrent, dans le format de date standard UNIX (nombre de secondes depuis le `1/1/1970 à 00:00:00 UTC`)
* `comment` : (optionnel) commentaires de l'auteur (chaine de caractères)
* `created by` : (optionnel) nom et version du programme utilisé pour créer le `.torrent` (chaine de caractères)

### Dictionnaire info  

Cette section contient les champs qui sont communs aux deux modes, *fichier seul* et *multi fichiers*.  

* `piece-length` : nombre d'octets dans chaque piece (entier)
* `pieces` : chaine qui consiste en la concaténation de tous les hashs SHA1 de 20 octets, un par piece (chaine d'octets)
* `private` : (optionnel) ce champ est un entier. S'il est à `1`, le client DOIT publier sa présence pour obtenir d'autres peers SEULEMENT via les trackers déclarés explicitement dans le fichier métainfo. Si ce champ est à `0` ou s'il n'est pas présent, le client peut obtenir des peers par d'autres moyens, par exemple l'[échange de peer PEX](http://en.wikipedia.org/wiki/Peer_exchange), [DHT](http://en.wikipedia.org/wiki/Distributed_hash_table). Ici `private` doit être compris comme _aucun peers d'origine extérieure_.

#### Info dans le mode *fichier seul*  

Dans le cas du mode *fichier seul*, le dictionnaire info contient la structure suivante :  

`name` : le nom du fichier. À titre purement consultatif. (chaine)  

`length` : longueur du fichier en octets (entier)  

`md5sum` : (optionnel) une chaine de 32 caractères hexadécimaux correspondant à la somme MD5 du fichier. Elle n'est pas du tout utilisée par BitTorrent, mais certains programmes l'utilisent pour une meilleure compatibilité.  

#### Info dans le mode *multi fichiers*  

Dans le cas du mode *multi fichiers*, le dictionnaire info contient la structure suivante :  

* `name` : le nom du répertoire dans lequel stocker tous les fichiers. À titre purement consultatif. (chaine)
* `files` : une liste de dictionnaires, un pour chaque fichier. Chaque dictionnaire contient les clés suivantes :
	+ `length` : longueur du fichier en octets (entier)
	+ `md5sum` : (optionnel) une chaine de 32 caractères hexadécimaux correspondant à la somme MD5 du fichier. Elle n'est pas du tout utilisée par BitTorrent, mais certains programmes l'utilisent pour une meilleure compatibilité.
	+ `path` : une liste contenant une ou plusieurs chaines qui regroupées représentent le chemin (path) et le nom du fichier. Chaque élément de cette liste correspond au nom d'un répertoire ou (dans le cas du dernier élément) au nom du fichier. Par exemple, un fichier `*`dir1/dir2/file.ext`*` consistera de trois chaines : `dir1`, `dir2`, et `file.ext`. Le tout est encodé comme une liste bencodée de chaines telle que `l4:dir14:dir28:file.exte`

### Tracker HTTP/HTTPS Protocol  

Le tracker est un service HTTP/HTTPS qui répond à des requêtes HTTP GET. Les requêtes incluent les paramètres des clients qui permettent au tracker de générer des statistiques générales. La réponse inclue une liste de peer qui aide le client à la diffusion du torrent. La base de l'URL se compose d'une URL d'annonce telle que définit dans le fichier métadonnée (.torrent). Les paramètres sont alors ajoutés à l'URL, en utilisant la méthode CGI standard (c'est-à-dire avec un `?` après l'URL d'annonce, suivie par des séquences `param=valeur` séparées par `&`).  

Notez que toutes les données binaires dans l'URL (particulièrement `info_hash` et `peer_id`) doit être proprement échappées. Cela signifie que toutes les valeurs ne se trouvant pas dans l'ensemble 0-9, a-z, A-Z, '.', '-', '_' et '˜', doivent être encodées sous le format `%nn`* où `nn` est la valeur hexadécimale de l'octet.  

Pour le hash de 20 octets suivant :  

`\x12\x34\x56\x78\x9a\xbc\xde\xf1\x23\x45\x67\x89\xab\xcd\xef\x12\x34\x56\x78\x9a  `

la forme encodée correcte sera `%124Vx%9A%BC%DE%F1%23-g%89%AB%CD%EF%12%34Vx%9A`.  

#### Paramètres de Requête Tracker  

Les paramètres utilisés dans les requêtes client vers tracker sont les suivants :  

* `info_hash` : hash SHA1 de 20 octets urlencodé de la valeur de la clé info du fichier métainfo. Notez que cette valeur sera un dictionnaire bencodé, comme dis dans la définition de la clé info ci-dessus.
* `peer_id` : chaine de 20 octets urlencodée et utilisée comme ID unique du client, générée par le client à son lancement. N'importe quelle valeur est acceptée et peut être des données binaires.
* `port` : le numéro de port sur lequel le client écoute. Les ports réservés pour BitTorrent sont typiquement 6881-6889. Les clients peuvent choisir d'abandonner s'ils ne parviennent pas à écouter sur un port dans cette plage.
* `uploaded` : la somme totale uploadée (depuis que le client a envoyé l'événement `started` au tracker) en base 10 ASCII. Bien que cela ne soit pas explicitement déclaré dans la spécification officielle, il s'agit du nombre total d'octets téléchargé.
* `left` : La somme des octets que le client doit encore télécharger, encodé en base 10 ASCII.
* `compact`: Indique que le client accepte une réponse compacte. La liste de peer est remplacée par une chaine de peers avec 6 octets par peers. Les 4 premiers octets représentent l'hôte (avec les octets dans l'ordre réseau), les deux derniers sont le port (là encore dans l'ordre réseau). Notez que certains trackers ne supportent que les réponses compactes (pour économiser de la bande passante) et refusent les requêtes normales.
* `no_peer_id` : Indique que le tracker peut omettre le champ peer id dans le dictionnaire de peers. Cette option est ignorée si compact est activé.
* `event` : si spécifié, il doit être l'un des états started, completed ou stopped (ou vide qui revient à non spécifié). Si non spécifié, alors cette requête est faite à intervalles réguliers.
	+ `started` : la première requête au tracker doit inclure la clé event avec cette valeur.
	+ `stopped` : Doit être envoyé au tracker si le client s'arrête proprement.
	+ `completed` : Doit être envoyé au tracker quand le téléchargement est complet. Cependant, ne dois pas être envoyé si le téléchargement était déjà à 100% au lancement du client. Vraisemblablement, cela permet au tracker de garder des statistiques des téléchargements complets.
* `ip` : Optionnel. La véritable adresse IP du client, dans le format standard (4 nombres décimaux de 0 à 255 séparés par des points). Ce paramètre est utile seulement si l'adresse IP qui envoie les requêtes n'est pas la même que celle du client.
* `numwant` : Optionnel. Nombre de peers que le client veut bien recevoir du tracker. Cette valeur peut être à zéro. Si omise, elle vaut généralement 50 peers.
* `key`: Optionnel. Une identification additionnelle qui n'est partagée avec aucun utilisateur. Cela permet à un client de s'identifier même si son adresse IP change.
* `trackerid` : Optionnel. Si l'annonce précédente contenait un tracker id, il doit être placé ici.

## Utilisations alternatives  

### Découvertes des ports NATés

Une application qui a besoin de communiquer avec des machines sur Internet est souvent bloquée par un routeur/firewall. Il faut alors que l'utilisateur de la machine configure lui-même son équipement afin de [NAT](http://en.wikipedia.org/wiki/Network_address_translation)er certains ports pour que l'application soit joignable. Mais ces applications préfèrent parfois trouver une *porte* elles-mêmes pour simplifier la vie de l'utilisateur ou parce qu'elles veulent rester *discrètes*.  

Pour les ports UDP, il existe le protocole [STUN](http://en.wikipedia.org/wiki/STUN) qui permet à une application, en effectuant une suite de communications pré-établies, de déterminer derrière quel type d'équipement elle se trouve.  

La première utilisation alternative de BitTorrent à laquelle j'ai pensée, c'est la détection de ports TCP NATés. Le principe est très simple : à partir d'un fichier torrent valide et partagé par un grand nombre de peer, on calcule les paramètres nécessaires pour envoyer une requête au tracker et pour chaque port que l'on veut tester on envoie cette requête, avec comme seule modification le paramètre port.  

Pour décoder les fichiers torrent, j'ai utilisé [une implémentation Python](http://wiki.theory.org/Decoding_bencoded_data_with_python) qui était citée dans la spécification.  

L'utilisation du langage Python est d'autant plus agréable que les différents types présents dans un fichier métainfo sont les mêmes que ceux proposés par Python (str, int, list et dict).  

Les paramètres nécessaires à l'envoi d'une requête valide sont `info_hash` (à calculer), `peer_id` (aléatoire, 20 octets), `compact` (que nous fixerons à 1), `port` (à fixer nous même) ainsi que `uploaded` (0), downloaded (0), `left` (taille totale du ou des fichiers) et `event` (`started`) qui nous déclarent comme nouveau peer et permettent notre entrée dans la liste du tracker.  

Le plus compliqué a été le calcul du hash SHA1 du dictionnaire info bencodé... Au départ, je pensais chercher un moyen de le lire directement en analysant le fichier torrent au fûr et à mesure, mais devant la difficulté, j'ai préféré trouver une autre solution en utilisant le code déjà implémenté.  

Pour cela j'ai rajouté des fonctions de bencodage à celles déjà présentes de bdécodage. Une fois la structure info re-bencodée, il suffisait de calculer la somme SHA1... en théorie.  

La spécification dit que les clés du dictionnaire `info` doivent être ordonnées alphabétiquement. Visiblement les logiciels qui génèrent les fichiers torrent ne l'on pas pris en compte. Mais quelque soit l'ordre des clés, le résultat dans le fichier fera toujours la même taille.  

J'ai donc ré-encodé le dictionnaire `info`, calculé sa taille, puis extrait le nombre d'octets correspondant du fichier torrent pour calculer le SHA1.  

Le calcul de la taille totale des données est assez simple. Dans le mode *fichier seul* il nous suffit de lire le champ `length`, sinon il faut boucler sur chaque dictionnaire *files* et faire des additions.  

Le résultat est un script [torrentscan.py](/assets/data/torrentscan.py) qui prend comme arguments le nom du fichier torrent à utiliser et la liste des ports sur lesquels écouter.  

Voici le résultat de deux essais, sachant que mes ports 21-25, 6666 et 6881 sont redirigés depuis mon routeur vers ma machine :  

```console
$ python torrentscan.py aaf.torrent 21,80,6666,6880-6884
Tracker: http://denis.stalker.h3q.com:6969/announce
Hash: %27%CD%C0%D5%D2%0A%F4%01%E3X%9C%A9%21a%EAn%F6%B7%E8%40
Total length: 368701440
Announced port 6884
Announced port 80
Error listening on port 80
(98, 'Address already in use')
Announced port 6666
Announced port 6880
Announced port 21
Announced port 6882
Announced port 6881
Announced port 6883
[6881, 6666, 21]
```

Ici le programme a été lancé en root. Apache occupait déjà le port 80, ce qui explique le message *"Address already in use"*. En simple utilisateur, on aurait eu un *"Permission denied"* pour les ports 21 et 80.  

Les ports accessibles de l'extérieur sont affichés à la fin.  

```console
$ python torrentscan.py aaf.torrent 21,24,4444-4446,6666
Tracker: http://denis.stalker.h3q.com:6969/announce
Hash: %27%CD%C0%D5%D2%0A%F4%01%E3X%9C%A9%21a%EAn%F6%B7%E8%40
Total length: 368701440
Announced port 4446
Announced port 24
Announced port 4445
Announced port 21
Announced port 4444
Announced port 6666
[21, 6666, 24]
```

Le programme est assez long à s'exécuter. La partie qui attend les connexions demande à être améliorée. Pour chaque port, un thread est lancé qui envoie une annonce au tracker puis se met en écoute. Les threads ont jusqu'à 10 secondes pour s'exécuter, mais la gestion des sockets fait dépasser ce temps (même si le programme s'arrête tout seul au bout d'un moment).  

Ensuite j'ai remarqué que les clients BitTorrent communiquent très peu avec le tracker. Pour un gros fichier, j'ai compté que Azureus a envoyé moins de 5 requêtes. Les clients ne cherchent pas vraiment à mettre leur liste de peers à jour. Il faut alors compter sur les peers arrivant après nous pour qu'ils nous contactent.  

C'est pour cela qu'il est très important d'utiliser un torrent très demandé (le torrent pour les ISOs d'une distribution Linux juste après sa sortie est l'idéal).

### Attaque par amplification  

Un envoyant des requêtes d'annonce sur un grand nombre de trackers pour un nombre tout aussi important de torrent très demandé et en spécifiant l'adresse IP d'une machine dans le paramètre `ip` de la requête, on peut effectuer une attaque DDoS ([déni de service](http://en.wikipedia.org/wiki/Denial-of-service_attack) distribué) par amplification (comme le célèbre [Smurf](http://en.wikipedia.org/wiki/Smurf_attack)).  

L'attaque est dite par amplification, car en effectuant une seule connexion à une seule machine (le serveur d'un tracker), on provoque la connexion de plusieurs peers sur la victime.  

L'efficacité de cette attaque est liée à tout un tas de paramètres à prendre en considération : nombre de fichiers torrent, demandes pour ces données, réaction du serveur (va-t-il fermer la connexion immédiatement en voyant arriver des données malformées ? Sinon combien de temps va-t-il attendre ?) et du client BitTorrent (va-t-il laisser au serveur le soin de fermer la communication ? Combien de nouvelles tentatives va-t-il faire après le premier échec), etc.  

### Utilisation par les Botnets  

Un bot pourrait très bien utiliser le tracker d'un torrent anodin pour se déclarer à son *bot herder*. La majorité des bots existants utilisent le protocole IRC et se connectent à un channel avec un pseudo ayant une forme caractéristique (par exemple `botXXXXXXXX` où les `X` sont plus ou moins aléatoires).  

Le paramètre `peer_id` est l'identifiant du peer et doit faire 20 octets. C'est largement suffisant pour y placer des informations qui permettront au bot herder de le reconnaitre des peers légitimes. Quant au port déclaré auprès du tracker il pourrait en fait s'agir du port d'une backdoor, port choisi par exemple parce qu'il a été découvert comme NATé en utilisant le protocole BitTorrent et la porte dérobée attendant des commandes, à tout hazard une attaque BitTorrent-plifiée.  

Je reviendrais surement un jour sur les protocoles décentralisés, parce qu'il y a tout un tas de choses passionnantes ([Distributed Hash Table](http://en.wikipedia.org/wiki/Distributed_hash_table) et compagnie).  

Mise à jour :  

Un cas de malware utilisant les données de trackers public a été révélé. [Il génère des noms de fichiers en se basant sur le "top" du site ThePirateBay](http://blog.trendmicro.com/pirate-worm-sails-the-p2p-bay/).  

Au 27ᵉ Chaos Communication Congress, [une technique de DDoS basée sur l'utilisation des DHT du protocole BitTorrent](http://torrentfreak.com/bottorrent-using-bittorrent-as-a-ddos-tool-101229/) a été présentée...

*Published January 10 2011 at 07:46*
