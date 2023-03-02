---
title: "Python Opera Cookie Dumper"
tags: [Coding, Computer forensics]
---

Je me suis intéressé au [format de fichier utilisé par le navigateur Opera](http://www.opera.com/docs/fileformats/).  

Bien que les spécifications soient disponibles, on trouve peu d'outils pour gérer les historiques, caches et cookies du navigateur.  

Finalement je suis parvenu à écrire un script *Python* qui extrait les données du fichier `cookies4.dat` et les affiche dans un format texte plus compréhensible que le format binaire d'*Opera*.  

La sortie générée ressemble à ça :  

```plain
Opera Cookie Dumper
File version: 1.0
Application version: 2.1
Cookie file
Size of idtags: 1 bytes
Size of payload length fields: 2 bytes
MSB: 0x80
===================================
dsource.org
        dsource-auth_data  = a%3A11%3A%22autologinid%22%3Bs%3A6%3A%22userid%22%3Bi%3A-1%7D
        path = /projects
        path = /dsss
        trac_session  = e7f77d380bc7290b2347490c
        path = /tutorials
        trac_session  = 49ca56cec7f142d58d2201ea
userfriendly.org
        __qca  = 1239814048-45958653-24014683
...
```

Toutes les informations n'apparaissent pas. Actuellement il n'est affiché que le domaine, le path sur le serveur et les noms et valeurs des cookies.  

Durant mes recherches, j'ai découvert un tag non documenté (tag id `0x26`) qui correspond en réalité au champ *"Delete new cookies when exiting Opera is checked"* dans les préférences de site. Si la valeur est à 2 cela signifie que la suppression est activée. Si la valeur est à 1 ou si le tag est omis cela signifie que la suppression n'a pas lieu.  

Il y a aussi un flag `0x27|MSB` que j'ai rencontré, mais je n'ai pas pû découvrir sa signification.  

Dans tous les cas ça peut être utile pour faire du [Web Browser Forensics](http://www.securityfocus.com/infocus/1827) et le code est disponible ici :  

[opcodump.py](/assets/data/opcodump.py)

*Published January 11 2011 at 11:44*
