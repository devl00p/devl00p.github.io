---
title: "Pseudo-terminaux, portes dérobées, telnet et tunneling"
tags: [Coding, Réseau, Tunneling]
---

# Pseudo-terminaux, portes dérobées, telnet et tunneling

J'ai toujours trouvé aux réseaux un petit côté *magique*, l'idée de pouvoir éditer un fichier qui se trouve à des milliers de kilometres de chez moi ma toujours parue fabuleuse. C'est peut-être pour cela que j'ai toujours admiré les [TTYs](http://en.wikipedia.org/wiki/Data_terminal) (ouah, c'est beau un terminal, surtout avec du _ncurse_ !) et ils sont restés longtemps pour moi un grand mystère, au moins jusqu'à ces derniers jours, moment fatidique où j'ai décidé de me lancer dans l'épineuse aventure des TTY/PTY.  

## Un terminal, kezako ?  

Sous Linux, un terminal est avant tout un périphérique. On en trouve dans `/dev` (`pty*`, `tty*`) et dans `/dev/pts` (terminaux esclaves).  
Le terminal se charge de faire le lien entre le clavier et le programme qui recevra les commandes. Il transforme la frappe de certaines touches du clavier en un *code d'échappement* que le programme saura comment interpréter.  

Ces codes d'échappements sont définis dans des standards comme le [VT100](http://www.termsys.demon.co.uk/vtansi.htm).  

L'utilité d'un terminal par rappel à une ligne de commande *brute* est bien évidemment de pouvoir exécuter des programmes interactifs comme *Vim*, *Emacs*, *top*, *nethack* et bien d'autres... c'est pour dire à quel point ils sont devenus indispensables ;-)   

Même si la plupart des backdoors existantes n'offrent pas le support des ttys, quelques-unes le proposent avec plus ou moins de réussite.  

## Canonique or not canonique ?  

Dans la plupart des cas, elles sont inutilisables telles quelles car il n'y a pas de client associé. L'utilisation de netcat pour s'y connecter ne permet pas de profiter du terminal côté serveur, car netcat ne gère pas le tty. Notamment netcat lit les données tapées de façon canonique (attente d'une fin de ligne pour traiter les données) alors qu'un terminal les lit de façon non canonique : les données sont traitées à chaque frappe du clavier.  

Le mode non canonique est indispensable pour les programmes cités plus tôt (par exemple pouvoir taper simplement `q` pour quitter `top` sans avoir à appuyer sur `entrée`).  

## Toi comprendre ce que moi dire ?  

Vient alors un autre problème : le terminal client et le terminal serveur doivent parler la même langue. Une bonne partie des normes existantes sont compatibles, car basées sur les [codes d'échappement ANSI](http://www.termsys.demon.co.uk/vtansi.htm) mais ce n'est pas toujours le cas.  

Le standard utilisé est habituellement défini par la variable d'environnement `TERM` sous le shell.  

Deux solutions sont possibles pour faire dialoguer correctement le client et le serveur :  

* Utiliser un client et un serveur utilisant le même langage
* Utiliser un protocole permettant au client et au serveur de se mettre d'accord sur le type de terminal à utiliser

## Implémentations  

La première solution est celle utilisée dans [sorshell.c](http://www.darkircop.org/security/sorshell.c). Le client et le serveur se voient fixer la variable d'environnement `TERM` à `vt100`. Le client est configuré en mode non canonique est sans échos (voir plus loin).  

L'autre solution a fait son apparition il y a maintenant longtemps avec [le protocole telnet](http://www.commentcamarche.net/internet/telnet.php3). Par ce protocole, le client et le serveur négocient le type de terminal ainsi que d'autres règles de transmission.  

L'implémentation de telnet dans un logiciel ne facilitant pas les choses, certains ont préféré ruser comme pour [Tiny Shell](http://tsh.thecostaricacondo.com/) qui se contente de l'envoi du type de terminal utilisé.  

Il existe tout de même [un code en perl](http://rawlab.mindcreations.com/codes/perl-backdoor.pl) où toute la couche telnet est utilisée.

## Terminal client  

Un dehors du mode canonique (ou non), le client ne doit pas interpréter certains signaux comme un `Ctrl+C` afin de les traduire pour les transmettre au serveur.  

Les deux parties doivent aussi se mettre d'accord sur qui renvoie les données. Quand on frappe sur une touche depuis le client, on s'attend à ce qu'elle apparaisse à l'écran. Soit elle s'affiche au moment où on appuie sur la touche, soit quand le serveur nous la renvoie (il a fait un *écho*), soit les deux en même temps (dans ce cas-là, le caractère s'affiche en double).  

Le serveur renvoyant généralement plus de données que le client n'en envoi, le client est habituellement passé en non-écho et les caractères s'affichent alors lorsque le serveur les renvoie au client (le client ne renvoie pas les données du serveur).  

Dans une session telnet, la taille de la fenêtre de terminal sera aussi négociée (généralement `80x25` par défaut).  

Le rôle du terminal client consiste à lire les touches tapées sur l'entrée standard pour les retransmettre vers le serveur, le tout avec les caractéristiques citées précédemment.  

Sa programmation est simple. Il faut d'abord récupérer une structure `termios` définissant le modèle du terminal actuel à l'aide de la fonction `tcgetattr()`, modifier cette structure selon nos souhaits pour enfin mettre à jour le terminal avec les nouveaux paramètres (fonction `tcsetattr()`).  

Le code utilisé en C dans `sorshell` est le suivant :  

```c
struct termios deftt,tt;

/* terminal init */
tcgetattr(0, &deftt); /* récupére les préférences du terminal */
tt = deftt; /* copie */
tt.c_oflag &= ~(OPOST);
tt.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG); /* pas d'écho, ne recoit pas les signaux, mode non-canonique... */
tt.c_iflag &= ~(ICRNL); /* transforme les CR en NL */
tt.c_cc[VMIN] = 1; /* lit caractère après caractère */
tt.c_cc[VTIME] = 0; /* pas de délai de lecture */
tcsetattr(0, TCSADRAIN, &tt); /* mettre à jour le terminal */
...
tcsetattr(0, TCSADRAIN, &deftt); /* restauration */
```

## stty  

Sous Linux, la commande `stty` permet de modifier les paramètres d'un terminal. On peut alors utiliser un client *brut* en modifiant le terminal courant, ce qui donnerait un script dans ce style :  

```bash
stty -icanon -echo -isig
netcat serveur 9999 -v
stty icanon echo isig
clear
```

## Un shell avec terminal pour pas un rond  

Petite astuce trouvée [sur pentestmonkey](http://pentestmonkey.net/blog/post-exploitation-without-a-tty/) : on peut utiliser la richesse des API Python pour associer facilement un shell avec un pseudo-terminal.  

La commande pour lancer un serveur fonctionnant avec le script client précédent sera la suivante :  

```bash
netcat -e "python -c 'import pty; pty.spawn(\"/bin/sh\")'" -v -l -p 9999
```

## Terminal serveur  

Du côté du serveur, le terminal doit fonctionner en sens inverse : lire les codes d'échappement reçus et les transformer en signaux, déplacement de curseur; etc.  

La programmation du serveur est plus compliquée et se base sur l'utilisation d'un [pseudo-terminal](http://en.wikipedia.org/wiki/Pseudo_terminal) dont le fonctionnement est proche des [pipe](http://en.wikipedia.org/wiki/Pipeline_(Unix)).  

On a alors un pseudo-terminal (*pty*) maître sur lequel on écrit les données reçues par le réseau et un pty esclave (*pts*) qui reçoit les données et les filtre avant de les renvoyer au shell.  

La programmation suivra la procédure suivante :  

1. Ouverture du périphérique `/dev/ptmx` qui va chercher un pty maître disponible et retourner son descripteur de fichier
2. Appel à la fonction [grantpt()](http://linux.die.net/man/3/grantpt) pour modifier les droits d'accès au terminal esclave (le pts)
3. Utilisation de la fonction [unlockpt()](http://linux.die.net/man/3/unlockpt) pour déverrouiller le pts
4. [ptsname()](http://linux.die.net/man/3/ptsname) permettra ensuite de récupérer le nom du pts
5. Ouverture du pseudo-terminal esclave

Pour terminer, le programme fait un `fork()`, le processus fils redirige ses entrées/sorties vers le pts avant de lancer un shell et le processus père gère les entrées réseau.  

C'est ce que fait [sorshell.c](http://www.darkircop.org/security/sorshell.c) (mis à part qu'il le fait en bas niveau).  

## Tunneling à travers Jabber (GTalk)  

En Python, le nombre d'étapes a été fortement réduites et côté serveur, il suffit d'appeler les fonctions `openpty()` et `fork()` du [module pty](http://docs.python.org/lib/module-pty.html).  

Pour illustrer tout cela j'ai développé un petit programme permettant de faire passer un shell/tty à travers une session *XMPP*. Le code se base sur l'utilisation des serveurs *GoogleTalk* mais peu être facilement modifié. Il utilise la librairie [xmpppy](http://xmpppy.sourceforge.net/)  

Le protocole *XMPP* ne permettant pas de faire facilement transiter des données brutes, celles-ci sont envoyées sous leur forme hexadécimale (encodage pour le caractère 'A' sera '61'). Quelques temporisations ont dû être rajoutées, car le serveur *GTalk* n'hésite pas à couper la communication si les envois successifs sont trop rapprochés.  

Ça fonctionne plutôt bien, si ce n'est que c'est assez lent. J'ai réussi à éditer avec *VIM*, naviguer dans une page de manuel, etc. Par contre, il faut faire attention avec les commandes qui envoient continuellement des données à l'écran (c'est le cas de `top`) qui risquent de faire bloquer le programme dans une boucle (avec un `top -n <nombre d'affichages>` ça passe).  

[Télécharger jabbertunnel.tar.bz2](/assets/data/jabbertunnel.tar.bz2)  

Références :  

[www.iakovlev.org](http://www.iakovlev.org/index.html?p=1169&m=1&l1=5)  

[sorshell.c](http://www.darkircop.org/security/sorshell.c)  

[emse.fr : Saisies de données au clavier](http://kiwi.emse.fr/POLE/SDA/tty.html)  

[win.py (Terminal Emulator)](http://sam.holden.id.au/software/pywily/win.py)  

[Python Library Reference : termios](http://docs.python.org/lib/module-termios.html)  

[Python Library Reference : pty](http://docs.python.org/lib/module-pty.html)

*Published January 11 2011 at 09:11*
