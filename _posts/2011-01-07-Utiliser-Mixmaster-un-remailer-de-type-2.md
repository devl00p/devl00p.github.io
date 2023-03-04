---
title: "Utiliser Mixmaster : un remailer de type 2"
tags: [Cryptographie]
---

Il existe différentes façons de protéger sa vie privée et/ou son anonymat sur Internet.  

La cryptographie, qu'elle soit à clé secrète ou publique, est couramment utilisée pour s'assurer que les communications interceptées ne puissent être exploitées par un attaquant. Des réseaux comme [Tor](http://tor.eff.org/) se chargent de faire passer vos paquets TCP dans un vrai labyrinthe informatique pour fausser votre adresse IP.  

Pour ce qui est des messages électroniques (emails et post sur Usenet), des serveurs se chargent de les relayer en prenant soit de retirer les informations vous identifiant. Ce sont les remailers.

Tout a commencé en 1993 grâce au remailer _Penet_ (rapport à son adresse, _anon.penet.fi_) tenu par un Finlandais.  

Ce remailer de type 0 (pseudonymous remailer) fonctionnait le plus simplement du monde en retirant certains entêtes du message (principalement le `From:`) avant de le renvoyer au destinataire final.  

Pour permettre à ses utilisateurs anonymes de recevoir des messages, le serveur proposait aussi des comptes mail de la forme `anXXXXX@anon.penet.fi`.  

Afin que ces comptes mails ne soit pas accessibles à tous et qu'une identité anonyme ne soit pas détournée par une autre, le serveur devait garder une liste de correspondance entre les vraies adresses emails et les fausses.  

Ajouté à cela, aucun chiffrage des données n'était effectué, rendant les utilisateurs vulnérables à de nombreuses attaques.  

L'architecture centralisée de ce système a fait retomber tous les problèmes sur le serveur. L'Eglise de Scientologie a porté plainte à plusieurs reprises, car des documents confidentiels avaient été postés sur le newsgroup _alt.religion.scientology_ avec l'aide du remailer.  

[Après plusieurs attaques](http://en.wikipedia.org/wiki/Penet_remailer), son propriétaire a finalement fermé le remailer en 1996.  

Pour corriger ces erreurs, une nouvelle génération de remailers est apparue : les Cypherpunks (remailer type I).  

Le principe utilisé n'est ni plus ni moins celui de Tor.  

Mais cette architecture en *oignon* a quelques défauts :  

* possibilités d'[attaques par rejeu](http://www.commentcamarche.net/attaques/rejeu.php3) (pas nécessairement utiles pour un attaquant, mais généralement nuisibles (flood))
* attaques statistiques : une personne qui a des soupçons sur une personne pourrait faire le rapprochement entre l'envoi de données chiffrées vers un remailer et l'apparition d'un nouveau message sur Usenet (comparaison des heures d'envoi et de publication)
* étude de la taille des messages chiffrés (dans le cas où ils ont une taille égale ou très proche du message en clair)

Ces faiblesses ont été comblées avec les remailers de type II, les Mixmasters.  

Cette fois les messages sont encryptés en triple-DES à l'aide d'une clé choisie aléatoirement pour chaque node. Les clés sont elles même encryptée en utilisant la clé publique RSA des nodes respectives. On a ensuite le traditionnel *"Je déchiffre puis je fais suivre"*.  

Les remailers ne renvoient pas immédiatement le message. Ils attendent que leur file d'attente soit pleine ou qu'un certain laps de temps, soit passé avant de faire suivre le message.  

Les paquets envoyés par Mixmaster font tous le même taille.  

L'implémentation officielle s'appelle [Mixmaster](http://mixmaster.sourceforge.net/) et est téléchargeable sur SourceForge.  

Pour compiler les sources, vous aurez besoin des librairies `OpenSSL`, `zlib`, `pcre` et `Ncurses` avec leurs fichiers include (packages `devel`).  

Il faut lancer l'installation en lançant `./Install` et en répondant par défaut à la quasi-totalité des questions.  

À la question demandant qu'elle est l'adresse email de votre remailer, donnez une adresse email avec un domaine acceptant les mails (par exemple `walt@disney.com` ou `gates@microsoft.com`). Le but est de pouvoir utiliser les remailers plus restrictifs qui vérifient la validité de l'adresse.  

Mixmaster se charge uniquement de vous faire choisir le parcours des messages et de les chiffrer en conséquence. L'envoi des messages s'effectue par un logiciel externe.  

Par défaut il s'agit de `Sendmail`, mais si vous voulez vous éviter un sérieux mal de crâne, je vous conseille plutôt d'installer `Exim`.  

`Exim` (tout comme `Sendmail` d'ailleurs) envoie automatiquement les messages avec une adresse du type `user@hostname.domain`. Par exemple si votre machine s'appelle `b0x` et que votre login est `toto`, l'adresse sera `toto@b0x`, ce qui a de grandes chances d'être considéré comme invalide par les remailers.  

Il faut alors ouvrir le fichier `/etc/exim/exim.conf` et faire quelques modifications.  

Dans la section `MAIN CONFIGURATION SETTINGS` :  

```ini
primary_hostname = disney.com
no_local_from_check
trusted_users = votre_nom_de_login
received_header_text = Received: by $primary_hostname
```

Dans la section `REWRITE CONFIGURATION` :  

```
*@disney.com    ${lookup{$1}lsearch{/etc/email-addresses}{$value}fail} frFs
```

Éditez ensuite le fichier de configuration de Mixmaster (`mix.cfg`) et remplacez `/usr/sbin/sendmail` par le path vers Exim (normalement `/usr/sbin/exim`)  
Dernière étape, créez un fichier `/etc/email-addresses` dont le contenu sera :  

```
votre_nom_de_login: mickey@disney.com
```

Vous avez alors un Exim qui enverra des emails venant de `mickey@disney.com` et un Mixmaster qui l'utilisera pour envoyer les mails.  

Mixmaster se lance en mode console. Lors du lancement vous avez un menu ainsi qu'un indicateur du nombre de messages dans la file d'attente :  

![Mixmaster start](/assets/img/mix1.jpg)  

La première chose à faire est de mettre à jour la liste des remailers en tapant la lettre `U` puis la touche `*`.  

*[Image perdue, était présente sur Image-Dream]*  

Choisissez ensuite l'un des serveurs à l'aide des lettres en préfixe (a...) pour obtenir les différentes clés publiques et les statistiques. Chaque serveur effectue des tests réguliers des autres remailers pour calculer un pourcentage d'efficacité.  

*[Image perdue, était présente sur Image-Dream]*  

Une fois revenu au menu principal, tapez `P` pour poster un message sur Usenet et entrez `alt.test` (ou `misc.test`) comme newsgroup. Ce sont des groupes réservés aux tests d'envois de message dont n'hésitez pas.  

Pour éditer le corps du message, tapez `E`. Mixmaster lance alors Vi. À vous de modifier le fichier et de l'enregistrer en quittant. Vous pouvez aussi sélectionner le chemin à faire emprunter à vos messages (touche `C`). Prenez de préférence ceux qui ont un bon pourcentage. Par défaut Mixmaster prend un chemin aléatoire, mais généralement de bonne qualité.  

![](/assets/img/mix4.jpg)  

![](/assets/img/mix5.jpg)

![](/assets/img/mix6.jpg)  

Validez votre message en appuyant sur M. Vous vous retrouvez au menu principal. Appuyez sur `S` pour envoyer les messages.  

J'ai remarqué que Mixmaster a des fois du mal pour l'envoi du message. Je vous conseille d'avoir Ethereal lancé en parallèle pour vérifier que les données sont effectivement envoyées (si ce n'est pas le cas, rappuyer sur `S`)  

En théorie votre message sera accessible sur Usenet dans quelque temps (passez par _Google Groups_ pour le retrouver).  

Je dis bien *"en théorie"* car Mixmaster est loin d'être performant. Sur plus de 25 messages que j'ai envoyés lors d'un test (en utilisant différentes nodes), seul les messages 3, 5, 8, 14, 18, 20 et 22 ont effectivement été postés soit environ 75% de pertes.  
Le message 3 a mis plus d'une heure à arriver à destination. Le premier arrivé est le 14 :  

![](/assets/img/mix7.jpg)

La source du message est la suivante :  

```
From: Anonymous <nobody@4096.net>
Organization: Anonymous Posting Service
Comments: This message did not originate from the Sender address above.
        It was remailed automatically by anonymizing remailer software.
        Please report problems or inappropriate use to the
        remailer administrator at <abuse@4096.net>.
Subject: 14ieme test
Message-ID: <f86e33bb9579458c5a3a6263520c0a5d@4096.net>
Newsgroups: alt.test
Date: Thu, 09 Nov 2006 23:07:01 -0000
Path: aioe.org!news.motzarella.org!news.germany.com!
      solnet.ch!solnet.ch!zen.net.uk!dedekind.zen.co.uk!4096.net!anon.4096.net
X-Abuse-Contact: abuse@4096.net
Xref: aioe.org alt.test:68450

si ce message est publie je joue au loto
```

Conclusion : il y a plus de chances d'arriver à poster un message par Mixmaster que de gagner au loto, mais je vous déconseille tout de même d'utiliser Mixmaster pour envoyer des messages urgents et/ou importants.  

Plus d'infos sur les remailers sur [FreeHaven](http://freehaven.net/related-comm.html#SMTP).

*Published January 07 2011 at 14:25*
