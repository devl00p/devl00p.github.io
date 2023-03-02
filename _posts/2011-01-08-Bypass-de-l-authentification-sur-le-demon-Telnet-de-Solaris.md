---
title: "Bypass de l'authentification sur le démon Telnet de Solaris"
tags: [vulnérabilité]
---

**NB : L'article a été initialement rédigé en février 2007.**

Une vulnérabilité pour le moins importante a été découverte dans le système d'authentification de *SunOs 5.10/5.11*.  

Même si [la faille](http://www.com-winner.com/0day_was_the_case_that_they_gave_me.pdf) est recensée comme étant imputable au service `in.telnetd`, le programme `login` a son importance dans l'exploitation de la vulnérabilité.  

Pour cette vulnérabilité, aucune injection de code ou technique d'exploitation avancée n'est nécessaire. Il suffit juste d'avoir recours à une astuce.  

Le serveur telnet ne gère pas l'authentification, il exécute le programme `login` avec plus ou moins d'arguments.  

`login` a une option `-f` [apparemment non documentée (pas dans la manpage)](http://docs.sun.com/app/docs/doc/817-0674/6mgf6fkej?q=login&a=view) qui permet de se logger sur le système sans avoir à saisir de mot de passe. Typiquement cette option peut-être utilisée quand l'utilisateur est déjà connecté sur le système.  

Une restriction supplémentaire a été mise en place telle qu'expliquée dans le code source : *"Must be root to bypass authentification."*  

Le service telnet fonctionne avec les droits root par conséquent il a la possibilité de bypasser cette authentification, seulement l'option `-f` n'est pas utilisée par défaut. MAIS telnet appelle le binaire `login` à l'aide de la fonction `execl` avec comme 8ᵉ argument un beau `getenv("USER")`.  

Reste alors à trouver comment fixer le contenu de la variable d'environnement USER à `-f`. Et là inutile de chercher bien loin, tout est dans la page de manuel de telnet :   

> -l user   
>   
> 
>  When connecting to a remote system that understands the ENVIRON option,  
> 
>  then user will be sent to the remote system as the value for the ENVIRON variable USER.


Par conséquent, il ne reste qu'à se connecter sur une machine Solaris de la façon suivante :  

```bash
telnet -l "-froot" <ip>
```

pour se connecter en tant que root sans avoir à saisir de mot de passe... ce qui est assez gênant ou très hospitalier (tout dépend de quel côté on se place).  

En attendant que Solaris propose un patch qui ajoutera des vérifications supplémentaires sur le contenu de la variable d'environnement `USER`, la solution temporaire consiste à stopper le service Telnet ou à le remplacer par quelque chose de mieux (ssh)  

Solaris 10 s'en tire pas trop mal sur le coup puisqu'il semble qu'une règle supplémentaire empêche root de se connecter depuis autre chose que la console (voir [ici](http://erratasec.blogspot.com/2007/02/trivial-remote-solaris-0day-disable.html))... seulement ce n'est pas difficile de trouver des comptes existants sur le système (bin, daemon, sys...)  

Le login de Mac OS X a une option `-f` [qui suit les même règles](http://www.hmug.org/man/1/login.php) (manquerait plus qu'ils aient aussi pompé le code du `telnetd`, ça pourrait être drôle) alors que sous Linux cette option [n'est pas bien claire](http://www.die.net/doc/linux/man/man1/login.1.html).  

Comme quoi même après des années de développement, une bonne dose de documents sur la programmation sécurisée et du code source vu et revu, on n'est pas à l'abri de laisser passer une faille de sécurité stupide... l'erreur est humaine. On en a vu [de bonnes chez Apple](http://projects.info-pull.com/moab/) récemment.  

Une faille similaire avait déjà été découverte [en 1994](http://osvdb.org/displayvuln.php?osvdb_id=1007) dans `rlogin` !!

*Published January 08 2011 at 14:17*
