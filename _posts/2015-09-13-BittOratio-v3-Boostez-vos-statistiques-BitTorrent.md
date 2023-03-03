---
title: "BittOratio v3 : Boostez vos statistiques BitTorrent"
tags: [Coding, Réseau]
---

### Mise à jour du 13 septembre 2015  

La version 3 de *BittOratio* est disponible.  

Elle supporte désormais les réponses HTTP en mode *chunked* qui l’empêchait de recevoir correctement les réponses de certains trackers.  

Téléchargez cette nouvelle version ici : [bittoratio3.py](/assets/data/bittoratio3.py)  

### Mise à jour du 25 avril 2014  

Une nouvelle version de *BittOratio* est disponible.  

Elle corrige des problèmes d'affichage et surtout un bug dans le renvoi des headers HTTP qui provoquait la transmission de réponses HTTP invalides vers le client BitTorrent.  

*BittOratio* devrait donc maintenant fonctionner avec tous les trackers.  

Nouvelle version à télécharger ici : [bittoratio2.py](/assets/data/bittoratio2.py)  

## Article original (11 janvier 2011)  

Dans la même optique que pour le code [statsliar](http://my.opera.com/devloop/blog/2006/10/11/booster-les-statistiques-d-un-site) qui permet de booster les statistiques d'un site en envoyant des requêtes multiples à travers des proxys, je me suis mis à écrire un programme capable de booster ses statistiques d'upload sur les communautés BitTorrent qui s'appuient sur le principe du ratio.  

Le principe de ces sites est simple : on peut continuer à télécharger tant que l'on veut du moment que l'on partage dans une certaine proportion. Le ratio est une variable dont la règle est "quantité de données downloadées" divisée par "quantité de données uploadées".  

Le ratio exigé est lié au règlement du site, son minimum autorisé est généralement de 0.5.  

C'est plus l'envie que le besoin qui m'a amené à développer cet outil. C'était l'occasion de reprendre les spécifications BitTorrent étudiées pour mon article [Utilisations alternatives du protocole BitTorrent]({% link _posts/2011-01-10-Utilisations-alternatives-du-protocole-BitTorrent.md %}) et de voir ce qu'il était possible de faire.  

La première partie du document est la suite de la traduction de la spécification. La seconde partie explique le fonctionnement de l'outil.  

Je vous invite à vous pencher d'abord sur l'article cité précédemment et à consulter la partie concernant les requêtes envoyées par le client sur le tracker sans quoi la compréhension peut s'avérer difficile.  

## Première partie : Réponses émises par le tracker  

Le tracker répond avec un document *text/plain* correspondant à un dictionnaire bencodé contenant les clés suivantes :  

* `failure reason` : Si présent, alors il est possible qu'aucune autre clé ne soit présente. Sa valeur est un message d'erreur expliquant pourquoi la requête a échoué (chaîne).
* `warning message` : (nouveau, optionnel) Similaire à failure reason, mais la réponse est toujours traitée normalement. L'avertissement est affiché au même titre qu'une erreur.
* `interval` : Intervalle en secondes que le client devrait attendre entre l'envoi de requêtes régulières au tracker.
* `min interval` : (optionnel) Intervalle minimum d'annonce. Si présent, les clients ne doivent pas annoncer plus fréquemment qu'à cet intervalle.
* `tracker id` : Une chaîne que le client devrait renvoyer sur chaque prochaine annonce. S'il est absent et si une précédente annonce a envoyé un tracker id, ne pas rejeter cette ancienne valeur, mais la conserver.
* `complete` : nombre de peers qui disposent du fichier entier, c'est-à-dire les *seeders* (entier).
* `incomplete` : nombre de peers qui ne seedent pas, c'est-à-dire les *leechers* (entier).
* `peers` : (modèle dictionnaire) La valeur correspondante est une liste de dictionnaires, chacun avec les clés suivantes :
	+ `peer id` : Un identifiant que le peer a choisi lui-même, comme décrit plus tôt pour la requête au tracker (chaîne).
	+ `ip` : l'adresse ip du peer, soit en Ipv6 (forme hexadécimale), soit en ipv4 (séparation par des points) ou un nom DNS (chaîne).
	+ `port` : le numéro de port du peer (entier).
* `peers` : (modèle binaire) Au lieu d'utiliser le modèle de dictionnaire décrit précédemment, la valeur peut être une chaîne constituée de multiples de 6 octets. Les 4 premiers octets correspondent à l'adresse IP et les deux suivants au numéro de port. Le tout en notation réseau (big endian)

Comme mentionné plus tôt, la liste des peers est de 50 peers par défaut. S'il y a moins de peers sur le torrent, alors la liste sera plus petite. Dans le cas contraire, le tracker renvoi une liste de peers choisis aléatoirement.  

Le tracker a le droit d'implémenter un mécanisme plus intelligent de sélection des peers à retourner comme réponse. Il pourrait par exemple éviter de retourner la liste des seeders à un seeder.  

Les clients peuvent envoyer une requête plus tôt qu'au bout de l'intervalle spécifié si un événement se produit (par exemple *stopped* ou *completed*) ou si le client a besoin de découvrir plus de peers. Toutefois, il est mal vu de *marteler* un tracker pour obtenir davantage de peers. Si un client souhaite une plus large liste de peers dans la réponse, alors il devrait spécifier le paramètre `numwant`.  

Note pour l'implémentation :

Même 30 peers est suffisant, la version 3 du client officiel n'établit en réalité de nouvelles connexions que s'il y a moins de 30 peers et va refuser les connexions s'il y en a 55.
Ces valeurs sont importantes pour des raisons de performance. Quand un morceau (piece) a terminé de télécharger, des messages _HAVE_ (obtenu) devront être envoyés aux peers les plus actifs. La conséquence est que l'utilisation de la bande passante augmente proportionnellement au nombre de peers. Au-delà de 25, les nouveaux peers n'auront que très peu d'influence sur l'augmentation de la vitesse de téléchargement.

Les créateurs d'interfaces graphiques sont fortement conseillés de dissimuler cela et d'empêcher de telles configurations qui de toute façon se montrerait très rarement utiles.  

## Convention "scrape" des trackers  

Par convention la plupart des trackers supportent un autre type de requête, permettant de connaître l'état d'un torrent donné (ou de tous les torrents) que le tracker gère. On y fait référence en tant que *"page de scrape"* car elle automatise le traitement laborieux d'extraction des statistiques du tracker.  

L'URL de scrape se base aussi sur la méthode GET, similaire à ce qui a déjà été décris. Cependant l'URL de base est différente. La génération de cette URL de scrape se fait selon les étapes suivantes :

Commencer avec l'URL d'annonce. Trouver le dernier `/` dans cette chaîne. Si le texte suivant immédiatement ce `/` n'est pas `announce` alors on considère que le tracker ne supporte pas la convention de scrape. Si c'est le cas, on substitue `announce` par `scrape` pour obtenir l'URL de scrape.  

Exemples : (URL d'annonce ? URL de scrape)  

```
  ~http://example.com/announce          ? ~http://example.com/scrape
  ~http://example.com/x/announce        ? ~http://example.com/x/scrape
  ~http://example.com/announce.php      ? ~http://example.com/scrape.php
  ~http://example.com/a                 ? (scrape non supporté)
  ~http://example.com/announce?x2%0644 ? ~http://example.com/scrape?x2%0644
  ~http://example.com/announce?x=2/4    ? (scrape non supporté)
  ~http://example.com/x%064announce     ? (scrape non supporté)
```

L'URL peut être complétée par le paramètre optionnel `info_hash`, une variable de 20 octets décrite plus tôt. Cela restreint le rapport du tracker à un torrent particulier. Dans le cas contraire les statistiques de tous les torrents gérés par le tracker sont retournés. Les développeurs de logiciels sont fortement encouragés à utiliser le paramètre `info_hash` dès que c'est possible, afin de réduire la charge et bande passante du tracker.  

Vous avez aussi la possibilité de spécifier plusieurs paramètres `info_hash` aux trackers qui les supportent. Bien que cela ne soit pas indiqué dans les spécifications officielles, c'est devenu un standard dans la pratique – par exemple :  

`http://example.com/scrape.php?info_hash=aaaaaaaaaaaaaaaaaaaa&info_hash=bbbbbbbbbbbbbbbbbbbb&info_hash=cccccccccccccccccccc`  

La réponse de cette requête HTTP GET est un document *"text/plain"* ou encore une version compressée par gzip qui correspond à un dictionnaire bencodé contenant les clés suivantes :  

* `files` : un dictionnaire comportant des paires clés / valeurs pour chaque torrent pour lequel il existe des statistiques. Si `info_hash` est spécifié et valide, le dictionnaire contiendra une seule paire clé / valeur. Chaque clé correspond au `info_hash`, une suite de 20 octets. La valeur de chaque entrée du dictionnaire est composé des éléments suivants :
	+ `complete` : nombre de peers qui disposent du fichier entier, c'est-à-dire les seeders (entier)
	+ `downloaded` : nombre total de fois où le tracker a enregistré une terminaison (complétion) (`event=complete`, c'est-à-dire quand un client termine de télécharger un torrent)
	+ `incomplete` : nombre de peers non-seeders, c'est à dire les *leechers* (entier)
	+ `name` : (optionnel) le nom interne du torrent, tel que défini dans la section d'info du fichier torrent (*name*)

Notez que cette réponse a 3 niveaux de profondeur de dictionnaire (sur le même principe que les poupées russes). Voici un exemple :  

```
d5:filesd20:....................d8:completei5e10:downloadedi50e10:incompletei10eeee
```

Où *....................* est le `info_hash` de 20 octets avec 5 seeders, 10 leechers, et 50 téléchargements complets.  

## Extensions non-officielles au scrape  

Ci-dessous sont les clés de réponse qui sont utilisés non officiellement. Comme elles sont non-officielles, elles sont aussi optionnelles.  

* `Failure reason` : Un message d'erreur expliquant pourquoi la requête a échoué (chaîne). Clients connus pour utiliser cette clé : *Azureus*.
* `Flags` : un dictionnaire constitué de drapeaux divers. La valeur des clés de drapeau est un autre dictionnaire à niveaux, pouvant contenir l'information suivante :
	+ `min_request_interval` : La valeur de cette clé est un entier correspondant au nombre de secondes que le client doit attendre avant de scraper à nouveau le tracker. Trackers connus pour utiliser cette clé : *BNBT*. Clients utilisant cette clé : *Azureus*.

## BittOratio : Comment tricher sur ses statistiques d'upload  

À bien regarder la façon dont sont formées les requêtes et réponses du tracker on remarque que tricher est simple : il suffit d'exagérer la valeur passée au paramètre *uploaded* sur les requêtes *announce*.  

Pour le tracker il est beaucoup plus compliqué de savoir si le client triche ou non. Toutefois, certaines vérifications peuvent être faites :  

* Vérifier que le client a envoyé une requête annonce de démarrage du torrent (`event=started`) avant de prétendre avoir partagé des données.
* Surveiller s'il n'y a pas des incohérences (quantité d'upload qui diminue au lieu d'augmenter). Mais ces incohérences peuvent être non intentionnelles (utilisateur qui efface par mégarde un fichier que le client torrent va re-télécharger etc).
* Vérifier que le client n'est pas seul sur le torrent : pour uploader il lui faut forcément un autre client.
* Vérifier que le client a bien ses ports de partage ouvert. Il ne peut pas partager s'il refuse toute connexion. Mais cette vérification serait difficile à mettre en place pour le tracker).
* Calculer la vitesse d'émission du client en se basant sur la quantité d'upload qu'il prétend envoyer entre deux moments successifs et vérifier si cette vitesse est informatiquement réaliste.

Des outils existent déjà pour simuler l'upload de données : [RatioMaster](http://www.moofdev.net/ratiomaster) et [RatioMaster-NG](http://ratiomaster.nrpg.info/).  

Le second se veut être une correction du premier. Ils ne téléchargent pas réellement les fichiers, mais envoient des suites de requêtes au tracker pour faire croire qu'ils participent aux transferts.  

Je n'ai pas cherché à étudier leur fonctionnement précis, mais certains trackers tentent de détecter ce type de fraude par les vérifications citées plus haut.  

Mon logiciel BittOratio fonctionne autrement. C'est un proxy HTTP qui modifie au vol les requêtes d'annonce à destination du tracker, multipliant la quantité de données envoyée par un facteur (nombre entier) modifiable dans le code source.  

Pour qu'il fonctionne, il faut donc que les fichiers soient réellement téléchargés et mis à disposition, mais vous n'aurez pas à uploader autant que vous ne téléchargez pour obtenir un bon ratio.  

L'avantage de cet outil est que ce système de triche est indécelable.  

Il suffit de lancer le proxy qui écoute sur le port tcp 8080 et de configurer votre client BitTorrent pour passer par le proxy.
Par exemple avec *Transmission* sous *Linux*, il faut modifier le fichier `.config/transmission/settings.json` pour placer les réglages suivants :  

```json
"proxy": "localhost",
"proxy-auth-enabled": false,
"proxy-auth-password": "",
"proxy-auth-username": "",
"proxy-enabled": true,
"proxy-port": 8080,
"proxy-type": 0,
```

Les requêtes interceptées sont affichées de façon succincte à l'écran (identité du tracker, hash du torrent, quantité d'upload).  

La difficulté principale lors de l'écriture du programme a été de gérer les erreurs de connexion. Comme la bande-passante est bouffée par le client BitTorrent, le proxy rencontre pas mal d'erreurs de timeout (connexion au tracker indispo ou résolution dns qui prend trop de temps).  

On pourrait penser que les requêtes du tracker importe peu, mais elles ont un effet important sur le client BitTorrent.
La première technique que j'ai employée pour gérer ces erreurs était de renvoyer au client un message HTTP 504 (*Gateway Timeout*) correspondant parfaitement aux problèmes de ce type, mais le client avait une mauvaise tendance à abandonner au bout d'un moment.  

Finalement j'ai mis en place un système de cache qui renvoi au client le résultat de la requête précédente (pour le même `info_hash`) et qui améliore largement la stabilité de l'ensemble.  

Quand on stoppe le proxy (Ctrl+C), celui-ci *flushe* le cache et envoie les annonces d'upload qui n'auraient pas été envoyées sur le tracker faute de capacité réseau.  

Parmi les modifications apportées durant l'écriture du code, j'ai dû abandonner _urllib2_ (vraiment à la masse en termes de performances) au profit de _httplib_.  

Pour terminer (et puisque certains se posent la question) il semble d'après mes observations qu'il est préférable de stopper (mettre en pause) les torrents avant de fermer complètement le client BitTorrent au lieu de le fermer directement : en effet le client n'envoie pas forcément les requêtes d'annonce à la fermeture pour synchroniser ses statistiques avec le tracker alors que la mise en pause envoie ces informations avec l'event `stopped`.  

Le code se trouve ici : [bittoratio.py](/assets/data/bittoratio.py)  

J'avais d'abord cherché une analogie à *Bit Torrent* pour le nom du programme, je suis arrivé à *Dick Rivers*... je me suis abstenu.  

Je reprendrais peut-être un jour la suite de la traduction de la spécification.

*Published September 13 2015 at 08:44*
