---
title: "Revue du honeypot mwcollect"
tags: [honeypot, malware]
---

**Note : Cet article a été initialement écrit en décembre 2005.**  

[mwcollect](http://mwcollect.org/) est un [honeypot](http://fr.wikipedia.org/wiki/Honeypot) destiné à la surveillance des malwares circulant sur le réseau Internet.  

Commençons par décrypter un peu ce charabia...  

Un malware est un programme (logiciel) donc les objectifs sont néfastes. Évidemment les malwares ne sont pas tous aussi néfastes les uns que les autres. On les divise en plusieurs catégories : virus, vers, spyware, adware, backdoors/rootkits, dialers... mais bien souvent ces programmes sont des mélanges de plusieurs catégories ou du moins collaborent les uns avec un autres (ex: un ver qui infecte des machines et y installe spyware/dialer ainsi qu'une rootkit pour cacher sa présence).  

Un honeypot est un leurre destiné à attirer les pirates. Comment peut-on attirer un pirate ? Et bien il suffit de mettre à disposition un service/programme qui semble exploitable et d'attendre son passage.  

Quel est l'utilité d'un tel leurre ? Principalement se tenir au courant des techniques, vulnérabilités, logiciels utilisés par les attaquants pour mieux se défendre.  

En règle générale quand on entend "honeypot" on pense à des systèmes complets, sacrifiés pour ces chers pirates ou encore des systèmes émulés avec une architecture réseau soigneusement étudié pour récupérer les informations... bref un arsenal qui demande du matos assez costaud.  

Heureusement on trouve quelques solutions légères qui simulent un ou plusieurs services en particulier... _mwcollect_ est l'une de ces solutions.  

Il simule différents services exploités massivement par les vers, donne de fausses réponses afin de faire croire que l'attaque a réussi et stocke les données qui ont une signature inconnue (donc à priori une nouvelle variante d'un ver voire pourquoi pas... une toute nouvelle attaque) sur le disque.  

Les données recueillies sont soit des fichiers qu'un ver/attaquant a voulu transférer sur sa victime, soit des shellcodes utilisés pour abuser d'une vulnérabilité (une suite d'instructions que le ver veut faire exécuter à sa victime).  

Les failles que j'ai simulé à l'aide de _mwcollect_ sont (des failles Windows) MS04-11 (service lsass, exploité notamment par Sasser), MS05-39 (service PnP, exploité notamment par Zotob) ainsi que MS03-26 (RPC-DCOM exploité en particulier par le célèbre Blaster).  

Je n'ai pas calculé combien de temps au total j'ai fait tourner _mwcollect_ mais j'ai pu en tirer certaines conclusions et certains chiffres :  

* Sur un total de 382 exploitations réussies, 249 reviennent au service RCP-DCOM, 131 sont à attribuer à lsass et seulement 2 au service Plug and Play.
* Il faut moins d'une minute une fois les services lancés pour être scanné.
* Une faille est exploitée dans LES 5 PREMIERES MINUTES.
* Même si la faille a été exploitée, l'attaque complète échoue dans la plupart des cas. Les vers ont en effet tendance à utiliser le protocole TFTP pour se propager, ce qui implique le lancement d'un mini-serveur TFTP sur la machine attaquante. La plupart du temps le port 69 est explicitement fermé sur la machine par conséquent soit le mécanisme de propagation du ver est imparfait soit la machine attaquante a récupéré le malware d'une façon particulière (site internet, P2P etc)... mais dans tous les cas, on peut considérer que le créateur du malware n'a pas pensé à tout.
* Très rarement le port TFTP de l'attaquant est protégé par un firewall. Dans ces cas soit un vrai attaquant se trouve sur la machine, soit le ver était présent avant l'apparition du firewall (passage à SP2 ?), ou encore le ver est venu d'ailleurs.
* Il y a parfois des cas où la commande exécutée est du type `tftp.exe -i 0.0.0.0 get malware.exe` ce qui montre que le malware attaquant n'a pas été capable de déterminer l'adresse IP sur laquelle il se trouve.
* Sur tous les cas d'exploitation AUCUN n'a réussi à transférer un fichier par TFTP... j'ai seulement eu 3 cas où le serveur TFTP était effectivement lancé mais le fichier à télécharger était... manquant.
* Les noms de fichiers utilisés par les malwares sont généralement des noms qui pourraient être ceux d'un exécutable système windows... ou des utilitaires (ex: PopupBlocker.exe).
* Malgré les stats effrayantes que je viens de donner, j'ai remarqué que seules des IPs du même fournisseur d'accès que moi apparaissent dans les logs. Bref le traffic est filtré par le F.A.I. Si ce n'était pas le cas une exploitation surviendrait probablement dès le lancement de Windows (sympa non ?).
* Une bonne partie des shellcodes sont encodés à l'aide d'un XOR

Le résultat d'un hexdump sur un des shellcodes récupéré :  

![Hexdump du shellcode](/assets/img/hexdump.jpg)

Le shellcode n'étant pas crypté on devine tout de suite à l'aide des chaines de caractères qu'il ouvre un port et y associe une instance de l'invite de commande...  

Quelques critiques sur _mwcollect_ :  

Quand un shellcode demande l'ouverture d'un port, _mwcollect_ se charge évidemment de l'ouvrir... malheureusement quand le ver/l'attaquant se connecte à ce port on a un beau segfault.

Le programme ne garde pas en mémoire les shellcodes qu'il a déjà reçu... on se retrouve vite fait avec 25 fois le shellcode le plus fréquent. À cause de tout ça on s'en lasse assez vite.

Bon point : on est deux fois plus heureux d'être sous Linux après cette expérience.  

Aller sur le site de [mwcollect](http://mwcollect.org/)

*Published January 05 2011 at 13:36*
