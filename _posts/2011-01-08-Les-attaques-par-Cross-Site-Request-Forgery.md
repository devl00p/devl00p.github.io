---
title: "Les attaques par Cross-Site Request Forgery"
tags: [vulnérabilité]
---

Dans le monde de la sécurité informatique, il y a parfois des vulnérabilités et des concepts tellement évidents que l'on n'en parle pas et on passe à côté. Jusqu'à ce qu'un petit malin trouve une formule qui en jette pour décrire ce concept (au hazard *"Compromis temps-mémoire"*) et alors ça devient la ruée vers l'or.  

C'est le cas des attaques par Cross-Site Request Forgery (_CSRF_ ou encore _XSRF_).  

Il est vrai que la formule est bien longue pour un principe pour le moins simple : inciter un internaute à cliquer ou se rendre sur une page donnée pour qu'une tâche spécifique soit effectuée par son intermédiaire sur un site Internet.  

L'exemple le plus simple est celui des scripts de déconnexion présents sur les forums, les webmails, et autre plateformes communautaires.  

Généralement ces scripts ne font rien pour vérifier que l'utilisateur a suivi une procédure dans les règles pour se déconnecter. Ainsi un membre d'un forum fictif pourrait poster un message de la forme :  

```
[url=http://exemple.com/forum/logout.php]La bande anonce du dernier James Bond[/url]
```

Provoquant la déconnexion des autres membres pensant cliquer sur un lien vers une bande-annonce.  

Si l'attaquant est encore plus sournois il peut par exemple donner l'URL du script de connexion comme adresse pour son avatar. Ainsi à chaque lecture d'une discussion à laquelle il a participé, les utilisateurs se voient déconnectés.  

Dans des cas particuliers, il doit même être possible de déconnecter les utilisateurs dès leur connexion, provoquant ainsi un [déni de service](http://fr.wikipedia.org/wiki/D%C3%A9ni_de_service).  

Un [cas réel](http://www.dlitz.net/stuff/xsrf/) a été trouvé il y a 2 mois sur Google. Techniquement il s'agit juste d'une page qui redirige le visiteur vers <http://www.google.com/setprefs?hl=ga> (à quelques paramètres près) changeant ainsi la langue dans laquelle Google s'affiche.  

Même si le résultat est plus une plaisanterie qu'une attaque malveillante, elle montre tout de même l'étendue des possibilités.  

On pourrait forcer les utilisateurs à effacer leurs messages sur un webmail, s'inscrire dans un groupe sur _last.fm_ (expérience vécue... mais je n'ai pas déterminé à quel moment et par quelle page ça a eu lieu) ou encore les forcer à acheter la discographie complète de *Richard Gotainer* sur eBay.  

Ce qui différencie un CSRF d'un simple lien, c'est le résultat obtenu : l'altération ou l'insertion de données sur le site Internet visé ou dans le navigateur de l'internaute.  
Dans le cas de Google, la victime n'a pas à posséder un compte Gmail pour que l'attaque fonctionne : les données altérées sont les préférences enregistrées dans un cookie.  

Une exploitation réussie sur un forum _IPB_ vulnérable pourrait [forcer l'administrateur du forum à augmenter les droits d'un membre](http://secunia.com/advisories/22272/).  

On peut faire en sorte qu'un internaute se rende sur une page... mais peut-on faire en sorte qu'il remplisse un formulaire et clique sur le bouton *"Envoyer"* ?  
En fait ce n'est pas beaucoup plus difficile : il faut créer une page avec un form et des champs cachés (`input type=hidden`) et des valeurs pré-renseignées. Avec les CSS on peut très facilement faire apparaître le bouton comme étant un lien ou encore une image cliquable.  

Si on ne souhaite pas attendre que l'utilisateur appuie sur le bouton, on peut automatiser l'envoi des données en utilisant la fonction `submit()` du langage Javascript.  

Que peut-on faire finalement pour se protéger de telles attaques ?  

Premièrement durcir les règles de session sur le site : empêcher par exemple la reconnexion automatique (redemander à chaque fois le login et le mot de passe). Les utilisateurs risquent de ne pas apprécier et en aucun cas ça ne bloque les attaques (ça peut éventuellement réduire le nombre d'attaques réussies).  

Faire des vérifications sur le référant (l'adresse de la page d'où ont été envoyées les données). La majorité des navigateurs envoient un référant. Une minorité ne l'envoie pas pour des raisons de vie privée. On peut par exemple accepter les données quand le référant est valide ou vide et refuser les données provenant d'un site extérieur.  

Malheureusement les redirections HTTP (comme utilisées pour l'exemple avec Google) ne transmettent pas ce référant.  

Compter sur le navigateur pour détecter de telles attaques serait illusoire (tous n'intégreront pas ces protections et ce serait le jeu du chat et de la souris avec les pirates).  

Utiliser un système de captcha pour valider chaque envoie de données...  

En fait la seule solution qui semble efficace est de passer dans les URLs générées par le site un nombre aléatoire, stocké dans une base de données ou enregistré dans un cookie. L'attaquant ne pouvant déterminer ce nombre aléatoire, il ne pourra pas générer des URLs valides.  

Bien sûr, il faut que ce nombre aléatoire soit pris dans un intervalle assez grand pour que les chances qu'il trouve un couple nombre/victime valide soit infime.  
Il faut aussi compter sur les utilisateurs pour ne pas divulguer ce nombre aléatoire. C'est pour ça que certaines personnes préfèrent passer cette valeur par POST (champ caché dans un formulaire) que par GET (url).  

Quoi qu'il en soit on n'est pas sorti de l'auberge.

*Published January 08 2011 at 10:59*
