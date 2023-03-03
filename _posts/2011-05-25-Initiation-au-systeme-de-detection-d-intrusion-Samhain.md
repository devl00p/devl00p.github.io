---
title: "Initiation au système de détection d'intrusion Samhain"
tags: [BlueTeam]
---

## Présentation de Samhain

[Samhain](http://www.la-samhna.de/samhain/index.html) est un [HIDS](http://fr.wikipedia.org/wiki/Système_de_détection_d'intrusion#HIDS_.28IDS_machine.29) multiplateforme pour les systèmes UNIX, Linux et Windows (à travers l'utilisation de [Cygwin](http://www.cygwin.com/)). Il est sous licence libre *GNU GPL*.  

Il fonctionne essentiellement comme un logiciel de vérification d'intégrité du système en surveillant en permanence les fichiers et en reportant toute modification qui a eu lieu.  

Il possède toutefois d'autres fonctionnalités qui en font un outil de détection d'intrusion puissant.  

## Pourquoi utiliser Samhain plutôt que X ou Y ?

L'un des avantages de *Samhain* est que son développement est toujours actif comparé à ses concurrents dont les dernières versions datent un peu : [AIDE](http://aide.sourceforge.net/) (février 2011), [Tripwire](http://sourceforge.net/projects/tripwire/) (mars 2010), [Osiris](http://osiris.shmoo.com/index.html) (janvier 2007) et [Integrit](http://integrit.sourceforge.net/texinfo/integrit.html) (juin 2007).  

De plus en termes de fonctionnalités, il se place largement au-dessus des logiciels précédemment cités (voir plus loin).  

Son seul vrai rival semble alors être [OSSEC](http://en.wikipedia.org/wiki/OSSEC) que je n'ai pas eu l'occasion de tester.  

## Pourquoi cet article ?

Tout d'abord les ressources en français sur ce logiciel manquent cruellement et n'entrent pas dans les détails.  

Ensuite, malgré la documentation, un utilisateur novice se retrouve face à des questions auxquelles j'ai tenté de répondre dans le présent article.  

Enfin, c'est l'occasion de partager un point de vue sur un logiciel gratuit et open-source.  

## L'installation

La compilation du code source est simple et tout ce qu'il y a de plus classique sous Linux : un fichier `configure` et un `Makefile`.  

Toutefois, avant de se lancer dans cette opération, je vous conseille vivement de lire [la documentation](http://www.la-samhna.de/samhain/s_documentation.html) (manuel, FAQ etc) et de faire le tour des fonctionnalités proposées, car de nombreuses options du script `configure` permettent d'inclure des modules intéressants qui ne sont pas présents par défaut.  

Pour voir les options de configuration disponibles, vous pouvez vous rendre [sur cette page,](http://www.la-samhna.de/samhain/manual/installation-configure.html) mais le mieux est probablement de lancer un `./configure --help` pour lister la totalité des options disponibles dans la version que vous avez récupéré.  

Parmi les options supplémentaires dédiées à la sécurité, on notera entre autres la surveillance des programmes [SetUID](http://fr.wikipedia.org/wiki/Setuid), la possibilité de surveiller les modules kernel (présence de [rootkit](http://fr.wikipedia.org/wiki/Rootkit)), l'analyse des fichiers journaux, les vérifications sur les systèmes de fichiers montés, la surveillance des ports ouverts et la détection des processus cachés.  

Sous Windows (avec *Cygwin*) un module permet de surveiller les clés de la base de registre.  

Une autre des *"killer features"* pour les utilisateurs avancés est la possibilité de [rendre Samhain furtif](http://www.la-samhna.de/samhain/manual/stealthmode.html).
On peut offusquer les données de log, dissimuler le fichier de configuration par stéganographie, renommer facilement les exécutables à la compilation ou utiliser un module kernel pour le cacher complètement au système.  

Les administrateurs systèmes ne sont pas en reste avec certaines fonctionnalités comme la possibilité de tout loguer vers une base de données (à la place du fichier journal) ou vers un serveur de journalisation central.  

Pour des mesures de sécurité ou parce que vous souhaitez monitorer plusieurs machines, vous pourrez en effet mettre en place le serveur de journalisation *Yule* qui fait partie du projet *Samhain*.  

Pour aller encore plus loin, on citera également le logiciel [Beltane](http://www.la-samhna.de/beltane/index.html) qui est une console de gestion web (en PHP) permettant de surveiller efficacement des machines avec Samhain installé.  

Samhain offre aussi un support de l'[IDS Prelude](http://www.prelude-technologies.com/), activable là aussi par une option de compilation.  

Une fois le logiciel configuré puis installé (`make`) j'ai mis en place le script d'init par la commande *[make install-boot](http://www.la-samhna.de/samhain/manual/installation-install.html)*.

## Configuration utilisée pour cet article

Dans mon cas, j'ai utilisé une configuration très basique : la base de Samhain (surveillance des fichiers) ainsi que la surveillance des ports et des processus.  

J'ai tenté la première fois d'activer la surveillance des modules kernel mais j'ai obtenu une erreur de compilation. Comme j'avais des doutes sur mon utilisation de cette option (que se passe-t-il quand on met à jour le kernel ou le module *nVidia* ?), je n'ai pas insisté et l'ai désactivé.  

J'ai compilé aussi le support de vérification des fichiers SUID mais d'après la documentation ce module est assez gourmand en ressources. Il est toutefois possible de régler son utilisation du disque par des directives spéciales dans le fichier de configuration.  

Je n'ai pas non plus utilisé le serveur de log *Yule* : la journalisation se fait ici en local dans un fichier de log (par défaut `/var/log/samhain_log`).

## Fonctionnement général de Samhain

En tant que vérificateur d'intégrité du système, Samhain surveille tous les fichiers et dossiers présents sur votre système pour vous alerter des modifications. Pour cela il lui faut bien sûr une base initiale qui lui sert de référence et qui contient les noms des fichiers du système avec leurs informations associées (taille, [timestamps](http://fr.wikipedia.org/wiki/Horodatage), propriétaires, permissions, attributs étendus...)  

Cette base sous format binaire se situe dans le fichier `/var/lib/samhain/samhain_file` et est nommée *"baseline database"* ou encore *"on-disk database"* dans la documentation de Samhain.  

Note : le fichier de configuration et cette base de données peuvent être signées cryptographiquement pour ajouter un niveau de sécurité.
Voir l'annexe [A3](http://www.la-samhna.de/samhain/manual/openpgp-signatures.html) ainsi que [le chapitre 8](http://www.la-samhna.de/samhain/manual/signed-files.html) de la documentation.  

Dès que Samhain détectera une modification par rapport à ce qui est enregistré dans la base, il l'indiquera à travers une ligne dans le journal de log.  

Cela peut être l'ajout ou la disparition d'un fichier, un changement de taille, de permissions, une date de modification ou de dernier accès, etc.

## Première utilisation

Une fois Samhain installé sur la machine, il faut créer la base initiale.  

On remplie cette base avec la commande suivante qui va scanner vos disques et mémoriser les caractéristiques de chaque fichier et dossier :

```bash
samhain -t init -p info
```

L'option `-t` permet de spécifier l'action à entreprendre (ici une initialisation) et l'option `-p` indique le niveau de verbosité à employer sur la sortie console (*stdout*).  

Nous reviendrons plus tard sur cette notion de verbosité.  

## Le fichier de configuration

Tous les réglages pour fixer quels fichiers et répertoires surveiller et comment les surveiller ainsi que les réactions à produire en fonction des changements détectés sur le système sont définis dans un fichier de configuration unique : `/etc/samhainrc`.  

Ce fichier de configuration en texte seul a une syntaxe très simple :  

Ça se résume à des noms de sections dans lesquels se trouvent des couples clé/valeur séparées par le caractère égal (`=`).  

Une section peut apparaître plusieurs fois. Le fichier de configuration fourni par défaut utilise d'ailleurs cette caractéristique pour regrouper les règles (couples clé/valeur) d'après l'emplacement des fichiers sur le disque.  

Les commentaires (qui commencent par le caractère dièse) peuvent être utilisés pour mieux s'y retrouver.  

Par exemple on écrira :

```ini
# --- règles pour /etc ---
[ReadOnly]
file=/etc/passwd

[Attributes]
file=/etc/mtab

# --- règles pour /var ---
[ReadOnly]
dir=/var/lib
[Attributes]
file=/var/tmp
[LogFiles]
file=/var/run/utmp
```

Qui est plus lisible que :

```ini
[ReadOnly]
file=/etc/passwd
dir=/var/lib

[Attributes]
file=/etc/mtab
file = /var/tmp

[LogFiles]
file=/var/run/utmp
```

Ce sera plus efficace pour retrouver une règle ou trouver où en placer une supplémentaire.  

Comme vous avez pu le remarquer, les clés les plus fréquentes sont `file` (quand il s'agit d'un fichier) et `dir` (pour un dossier). Quant à la valeur, il s'agit du chemin vers la ressource concernée.  

Les dossiers sont des cas particuliers, car ils peuvent être traitées aussi comme des fichiers (sous Linux, tout est fichier).  

Ainsi on peut activer une règle pour le contenu d'un dossier avec une clé `dir`, et une autre règle pour le dossier en lui-même avec la clé `file`. Ça peut éviter des doublons dans le fichier de log, car pour toute modification d'un fichier dans le dossier, le dossier en lui-même est aussi modifié (date de dernière modification)...  

Il faut tout de même faire très attention aux règles qu'on emploie : si on ne surveille que le contenu du dossier et pas le dossier lui-même, Samhain risque par exemple de passer outre la détection d'une opération de création aussitôt suivie de suppression d'un même fichier : le contenu du dossier n'aura pas eu l'air de changer, mais les propriétés du répertoire ont gardé une trace de cette activité, il peut être utile de le signaler.  

Concernant l'ordre dans lequel les règles sont prises en compte, c'est toujours la règle avec le chemin le plus spécifique (le plus proche du fichier concerné) qui l'emporte. L'ordre des sections n'a aucune importance. Les règles indiquées sous une section sont considérées comme en faisant partie.  

Un exemple concret et applicable est présent dans le fichier de configuration par défaut :

```ini
[ReadOnly]
## for these files, only access time is ignored
dir = 99/etc

[Attributes]
## check permission and ownership
file = /etc/mtab
```

Il indique à Samhain de surveiller toute modification (sans les dates de dernier accès, section `[ReadOnly]`) sur les fichiers se trouvant dans `/etc`, sauf pour le fichier `/etc/mtab` dont il faut uniquement surveiller les permissions (section `[Attributes]`) car ce fichier est généré dynamiquement par le système, inutile de reporter les modifications sur son contenu.  

On aurait très bien pu inverser les sections avec leurs clés associées, Samhain aurait appliqué les règles de la même façon.  

Un autre point à connaître est le fait que si un dossier est à la fois dans une clé `dir` et une clé `file`, c'est la clé `file` qui prédomine.  

S'il y a réellement une incohérence (le même couple clé/valeur dans deux sections différentes par exemple), Samhain générera un message d'erreur et refusera probablement de se lancer.  

Les clés `file` et `dir` ne sont pas les seules clés disponibles, mais sont celles auxquelles vous aurez le plus recourt.  

[Une page de documentation](http://www.la-samhna.de/samhain/manual/filedef.html) rassemble tout ce qu'il faut connaître sur la gestion des fichiers par Samhain.  

Un chemin de fichier indiqué dans une clé `file` ou `dir` sera toujours complet, c'est-à-dire qu'il débutera par le caractère `/` indiquant la racine.  

Les caractères spéciaux du shell Unix (`*`, `?`, `[...]`) ainsi que d'autres éléments sont acceptés et permettent par exemple d'appliquer des règles à un groupe de fichier correspondant au même pattern.  

Pour les clés *dir*, le chemin peut être précédé d'un *indice de récursion* (ou de profondeur) indiquant jusqu'à quel niveau de sous-dossier s'applique la règle.  

Cet indice est un entier qui peut aller jusqu'à 99. Par défaut, en l'absence de cet indice, il est à 0, c'est-à-dire que la règle s'applique à tous les éléments directement dans le dossier mais pas aux sous-dossiers.  

Un indice de -1 est un cas particulier qui permet de ne pas surveiller le contenu du dossier, quel que soit le niveau de profondeur.  

La documentation de Samhain donne 3 exemples concrets pour illustrer cela :  

*Exemple 1 :* Si vous voulez uniquement surveiller les fichiers dans un dossier, mais pas l'inode du dossier lui-même, utilisez :

```ini
[ReadOnly]
dir = /u01/oracle/archive00
[IgnoreAll]
file = /u01/oracle/archive00
```

*Exemple 2 :* Si vous voulez surveiller un dossier, mais pas son contenu qui change fréquemment :

```ini
[Attributes]
file = /var/spool/mqueue
file = /tmp
[IgnoreAll]
dir=-1/var/spool/mqueue
dir=-1/tmp
```

*Exemple 3 :* Si vous souhaitez surveiller un dossier (en tant que fichier), tout en vous assurant qu'aucun fichier à l'intérieur ne soit supprimé, mais pas les attributs actuels de ces fichiers :

```ini
[Attributes]
file = /root
[IgnoreAll]
dir=0/root
```

## Les sections pour gérer les fichiers et dossiers

Maintenant que nous avons vu les clés `dir` et `file`, regardons de plus près les sections disponibles.  

L'utilisation de ces règles requiert une bonne connaissance des systèmes de fichiers que vous utilisez.  

Je vous invite à ce sujet à consulter [la page Wikipedia sur les MAC times](http://en.wikipedia.org/wiki/MAC_times) (modification/access/change).  

La section `[ReadOnly]` permet comme son nom l'indique de surveiller les fichiers qui ne sont pas censés changer, si ce n'est leur date de dernier accès.  

Sont surveillés : le propriétaire, le groupe, les permissions, le type de fichier, le numéro de périphérique, les hard-links (ou [lien matériel](http://fr.wikipedia.org/wiki/Lien_matériel)), les liens symboliques (soft-links), le numéro d'inode, la somme de contrôle, la taille, la date de dernière modification et la date de changement (ctime).  

C'est probablement le paramétrage de surveillance le plus complet que vous utiliserez. C'est très pratique pour les fichiers statiques que l'on trouve dans `/etc`, `/bin`, `/usr`...  

La section `[IgnoreNone]` est encore plus radicale, car elle surveille le dernier accès (`atime`). En revanche elle ne prend pas le compte le temps de changement (ctime).  

La documentation propose d'utiliser ce paramètre comme un pot de miel pour pirates : placer sur votre système un fichier au nom alléchant (ex: `bank_accounts.xls`) et indiquer son chemin dans la section `[IgnoreNone]` pour remonter toute lecture du fichier leurre.  

La section `[Attributes]` permet comme son nom l'indique de surveiller les changements sur les droits (propriétaire, groupe, permissions), le type de fichier et le numéro de périphérique.  

Elle ferme les yeux sur les changements de taille et de date.  

On peut par exemple utiliser cette section pour surveiller un fichier de base de données : son contenu va changer en permanence, inutile donc de surveiller les modifications. En revanche un changement de propriétaire ou de droit d'accès (passage en exécutable) est suspicieux.  

La section `[LogFiles]` vérifie les fichiers journaux dont la taille peut varier en grandissant ou en diminuant. Tout est surveillé sauf les dates, la taille du fichier et la signature.  

La section `[GrowingLogFiles]` est identique à la précédente sauf que Samhain s'assure que la taille du fichier ne va pas diminuant.  

La section `[IgnoreAll]` ignore toutes les métadonnées concernant un fichier. Elle ne permet que de s'assurer de la présence du fichier.  

La section `[PreLink]` est utilisée pour les librairies préchargées (voir [Prelink sur Wikipedia](http://en.wikipedia.org/wiki/Prelink)). Je n'en ai pas personnellement l'utilité.  

Les sections `[UserX]` (X allant de 0 à 4 inclus) sont des sections supplémentaires qui par défaut reportent toute modification.  

## Les sections spécifiques

Les autres sections permettent de fixer des options sur le fonctionnement de Samhain et de ses modules.  

La section `[EventSeverity]` permet de définir le niveau d'alerte renvoyé pour chaque manquement à une règle donnée.
Dans cette section, on pourra par exemple placer les lignes suivantes :

```ini
SeverityReadOnly=crit
SeverityGrowingLogs=warn
SeverityIgnoreAll=info
```

Les niveaux d'alerte sont décris au [chapitre 4.1.1 de la documentation](http://www.la-samhna.de/samhain/manual/basic-configuration.html).  

La section `[Log]` est en lien direct avec la précédente. Elle permet de définir des seuils pour chaque méthode de journalisation.  

Si une alerte est levée, elle sera journalisée sur tous les systèmes de log dont le seuil est inférieur ou égal au niveau de l'alerte.  

Ainsi si le seuil est défini à `warn`, les alertes de niveau `info` ne seront pas logués tandis que les alertes de niveau `warn` et `crit` seront historisées.  

Dans cette section, on utilisera par exemple des clés/valeurs de cette façon :

```ini
MailSeverity=crit
LogSeverity=warn
PrintSeverity=info
```

Ici les alertes de niveau `info` ou supérieures sont envoyées à la console.  

Les alertes de niveau `warn` ou supérieures sont conservées dans un fichier.  

Les alertes `crit` ou supérieures feront l'objet d'un email envoyé à l'administrateur.  

Dans mon cas, j'ai défini `PrintSeverity` à `none`. J'utilise généralement X, mais en cas de plantage, je veux pouvoir utiliser la console (`Ctrl+Alt+F1`) sans être ennuyé.  

La section `[PortCheck]` permet de vérifier les ports ouverts sur la machine. Il faut l'activer avec `PortCheckActive=yes`.  

Par défaut les ports TCP 0 à 65535 sont scannés à un intervalle de secondes défini par la clé `PortCheckInterval`.  

On peut spécifier les ports qui doivent normalement être ouvert avec la clé `PortCheckRequired`. Celle-ci prend comme valeur une interface (IP) suivi d'un port (ou d'un service) séparé par un slash avec le protocole. On peut spécifier une liste de port/protocole en les séparant par des virgules.  

Exemple (présent dans la documentation) :

```ini
PortCheckRequired = 192.168.1.128:22/tcp,25/tcp,80/tcp,portmapper/tcp,portmapper/udp
```

Le même formatage sera utilisé avec les clés `PortCheckOptional`, `PortCheckIgnore` et `PortCheckSkip`.

La clé `PortCheckIgnore` spécifie les ports ouverts pour lesquels aucune alerte ne sera relevée. Toutefois, le scan sur ces ports à tout de même lieu.  

Si vous souhaitez que Samhain ne scanne pas du tout un port donné, il faut avoir recours à `PortCheckSkip`.  

Brièvement :

- La section `[SuidCheck]` permet de configurer le module de surveillances des fichiers SetUID. Des clés/valeurs spécifiques sont décrites dans la documentation comme la clé `SuidCheckFps` qui spécifie le nombre de fichiers à surveiller par secondes.

- La section `[Kernel]` permet de gérer le module de détection de rootkits.

- La section `[Utmp]` surveille les activités des comptes utilisateurs (connexion/déconnexion).

- La section `[Database]` permet de configurer l'utilisation d'une base de données.

- La section `[External]` permet d'appeler des scripts et programmes externes.

- La section `[ProcessCheck]` cherche des processus cachés.

- La section `[Mounts]` vérifie les disques montés.

- La section `[Logmon]` est dédiée à la surveillance de fichiers journaux. On peut par exemple lever une alerte si une ligne correspondant à une expression régulière est trouvée dans un journal.

- Enfin la section `[Registry]` permet de mettre en place une surveillance du registre Windows.

Les clés et valeurs possibles pour ces modules sont indiquées dans la documentation ou à décommenter dans le fichier `samhainrc` fournit avec le logiciel.

La section [Misc]
-----------------

Cette section offre des options de configuration très utiles. La plus importante étant sans doute la clé `Daemon` indiquant à Samhain s'il doit se lancer ou nom en tant que démon.  

Personnellement je l'ai laissé à `yes` ce qui est probablement plus sûr, mais vous pouvez très bien préférer de lancer Samhain en tache crontab avec cette option à `no`.  

La clé `SetFileCheckTime` définie l'intervalle de temps (en secondes) entre deux vérifications complètes du système.  

Les clés `SetMailAddress`, `SetMailRelay` et `MailSubject` sont comme vous le devinez dédiées à l'envoi d'alertes par email.  

Les clés `IgnoreAdded` et `IgnoreMissing` parlent d'elles même. On peut les utiliser pour les fichiers au nom prédéterminés qui apparaissent temporairement (fichier cache d'une application par exemple)  

Les clés `Redef*` permettent de réécrire le fonctionnement d'une section pour ajouter ou retirer des vérifications par rapport à ce qui est fait par défaut.  

La valeur doit être un ensemble de mots clés précédé d'un signe `+` (ajout) ou d'un `-` (retrait).  

Les mots clés sont :

```
CHK (checksum)
TXT (stocker le contenu du fichier dans la base)
LNK (lien symbolique)
HLN (hardlink)
INO (inode)
USR (utilisateur propriétaire)
GRP (groupe)
MTM (mtime)
ATM (atime)
CTM (ctime)
SIZ (taille du fichier)
RDEV (numéro de périphérique)
MOD (file mode)
PRE (Linux; prelinked binary)
SGROW (file size is allowed to grow)
AUDIT (Linux; report who changed the file)
```

On écrira par exemple :

```ini
RedefReadOnly = -INO,-USR,-GRP
```

Ces réécritures doivent apparaître avant les sections concernées. Il est alors préférable de mettre la section `[Misc]` en tête de fichier.  

La clé `FileNamesAreUTF8` permet d'indiquer à Samhain s'il risque de croiser des noms de fichiers Unicode. En 2011, je vous conseille de le mettre à `yes`. On trouve souvent sur le système des noms de fichiers certificats avec des accents... Sans cette option, vous risquez d'obtenir des messages *"Weird Filename"* dans vos logs.  

Le fichier `samhainrc` fournit par défaut offre une configuration quasi prête à l'emploi, mais il faut par exemple changer les noms de fichiers pour l'adapter aux choix propres à la distribution.  

Par exemple le fichier `/var/lib/logrotate/status` du `samhainrc` peu être `/var/lib/logrotate.status` sur votre système.

## Le fichier de log

Le fichier journal est par défaut `/var/log/samhain_log`. Au format texte uniquement, il contient un message par ligne.  

Au début vous passerez beaucoup de temps à analyser vos logs, car cela vous permettra de peaufiner votre `samhainrc` pour définir ce qui est une activité normale et ce qu'il faut surveiller.  

Le format des alertes présentes dans le fichier de log est relativement simple à comprendre. Voici à titre d'exemple une alerte que j'ai relevée dans mon log (coupée pour plus de lisibilité) :

```
CRIT   :  [2011-04-29T18:41:19+0200] msg=<POLICY [ReadOnly] ---I-M--T->,
path=</etc/init.d/postfix>,
mode_old=<-rw-r--r-->, mode_new=<-rwxr-xr-x>,
attr_old=<------------>, attr_new=<------------>,
inode_old=<1290353>, inode_new=<1291538>,
ctime_old=<[2011-03-18T18:20:09]>, ctime_new=<[2011-04-21T14:28:53]>,
mtime_old=<[2011-02-23T01:13:10]>, mtime_new=<[2011-03-30T22:52:47]>,
```

Ici nous avons une alerte de niveau critique (CRIT) qui a été remontée le 24 avril 2011 à 18h41.  

Le fichier `/etc/init.d/postfix` qui était marqué `ReadOnly` a été modifié.  

L'inode a été changé ainsi que les dates et les permissions.  

Derrière la section à laquelle se reporte l'alerte se trouve une suite de caractère avec des tirets.  

Ces caractères indiquent rapidement les points qui font l'objet d'une modification.  

Les caractères sont 'C' pour 'checksum', 'L' pour (soft) 'link', 'D' pour 'device number', 'I' pour 'inode', 'H' pour (le nombre de) 'hardlinks', 'M' pour 'mode', 'U' pour 'user' (propriétaire), 'G' pour 'group', 'T' pour 'time' (tous confondus) et 'S' pour 'size'.  

Voici un récapitulatif sous forme de tableau que j'ai récupéré sur le forum de Samhain :

```
|==================================
|Pos|Ltr| Meaning
| 0 | C | checksum
| 1 | L | link (soft)
| 2 | D | rdev (device number)
| 3 | I | inode
| 4 | H | hardlinks (number of)
| 5 | M | mode
| 6 | U | user (owner)
| 7 | G | group (owner)
| 8 | T | atime, ctime, mtime (any)
| 9 | S | size
|==================================
```

Dans l'alerte, Samhain nous indique aussi les anciennes valeurs qu'il avait en mémoire pour chaque nouvelle valeur.  

Dans mon cas, cette modification fait suite à une mise à jour de *Postfix*.  

En dehors du changement évident des dates et de l'inode (le fichier a été écrasé), je l'avais désactivé avant la mise à jour avec `chmod -x /etc/init.d/postfix`, ce qui n'est pas très propre (j'aurais dû utiliser `chkconfig` à la place).  

La mise à jour a donc remis le flag d'exécution sur le fichier.

## Recharger la configuration

Si vous avez modifié votre fichier *samhainrc*, il faut dire au programme qu'il doit recharger le fichier de configuration. Vous pouvez bien sûr le stopper et le relancer, mais ce n'est pas très propre (voir plus loin).  

Il est possible de recharger la configuration alors que Samhain est en train de tourner (en démon par exemple). Pour cela il faut lui envoyer le signal `SIGHUP`.  

Récupérer le PID du programme et lancez la commande `kill -s SIGHUP <pid de samhain>`.  

En ce qui me concerne cette commande ne fonctionne pas correctement puisque le processus arrête de loguer... mais il semble qu'il s'agisse d'[un bogue qui a été depuis corrigé](http://packetstormsecurity.org/files/101345/Samhain-File-Integrity-Checker-2.8.4a.html).

## Mettre à jour la base de données (baseline database)

Lorsque Samhain se lance, il charge le fichier de configuration en mémoire ainsi que le base de référence (`/var/lib/samhain/samhain_file`).  

Quand ensuite il rencontre une modification, il la reporte dans les logs... mais la base n'est pas mise à jour. C'est à l'administrateur d'effectuer cette mise à jour.  

Cette opération de mise à jour fonctionne de manière très basique : il ne s'agit pas d'un *"dump"* des modifications reportées par Samhain vers la base, mais d'un nouveau scan complet du système pour la mettre à jour.  

Du coup, si vous stoppez puis relancez Samhain sans avoir mis la base à jour, vous aurez une incidence au niveau des logs puisque Samhain va reprendre la base de référence non mise à jour et reporter dans les logs les modifications qu'il avait déjà reportées par le passé. Pour peu que Samhain ait fonctionné longtemps, cela va vous générer des logs considérables.  

Il est donc important d'effectuer une mise à jour de la base avant de relancer le démon ou d'éteindre votre machine ou encore de temps en temps en cas de plantage du système.  

L'opération de mise à jour de la base s'effectue en théorie par la commande `samhain -t update`.  

Seulement, il y a des éléments à prendre en considération :

* Samhain est très protecteur avec son fichier de log. La commande d'update n'aboutira pas, car le démon Samhain a posé un verrou dessus. On peut stopper Samhain, mettre à jour la base puis relancer Samhain mais ce n'est pas la bonne méthode. Il est préférable d'effectuer l'update avec les options `-l none -p warn`. Ainsi l'update n'écrira pas sur le fichier de log (`-l none`) mais à la place affichera les messages dans la console (`-p warn`).
* en l'absence d'options passées en ligne de commande, Samhain prend pour références les options du fichier de configuration. Si vous lancez l'update et que samhainrc indique qu'il doit se lancer en démon, l'update se lancera aussi en démon. On utilisera alors l'option `--foreground` pour éviter cela.

Finalement, on peut lancer une mise à jour de la base malgré que Samhain soit en train de tourner en démon avec cette commande :

```bash
samhain -t update -l none -p warn --foreground
```

## Faire la rotation des logs (logrotate)

Comme Samhain verrouille le fichier de log, l'opération de rotation ne se fera pas simplement.  

Il faut signaler à Samhain de retirer temporairement son verrou en lui envoyant un signal `SIGTTIN`.  

Il rend alors l'accès au fichier journal possible pendant un laps de temps de 3 secondes.  

Un script pour réaliser cette opération est [fourni dans la documentation](http://www.la-samhna.de/samhain/manual/log-file-rotation.html).

## La sécurité de Samhain

L'ensemble du [chapitre 11 de la documentation](http://www.la-samhna.de/samhain/manual/security-design.html) couvre la sécurité de Samhain lui-même, c'est-à-dire les difficultés qu'aurait un pirate à passer inaperçu et effacer ses traces sur un système sur lequel Samhain est installé.  

Cette sécurité semble vraiment excellente. La seule vraie possibilité pour un pirate serait à mon avis d'exploiter une configuration laxiste de Samhain (par exemple une arborescence de fichier non surveillée dans laquelle le pirate pourrait placer ses binaires).  

Le chapitre 11 donne aussi quelques astuces pour renforcer la sécurité de base.

## Trouver de l'aide

La documentation officielle, les pages de manuel, les exemples dans le fichier `samhainrc` sont autant de secours pour votre utilisation de Samhain.  

Si malgré ça vous ne trouvez pas de réponses à vos questions, vous pouvez être aidé [sur le forum officiel](http://www.la-samhna.de/forum/cgi-bin/wolfbbs_index.cgi).

## Mon fichier samhainrc pour openSUSE

À titre d'annexe, vous trouverez [mon fichier samhainrc](/assets/data/samhainrc) que j'utilise sur ma distribution GNU/Linux openSUSE.  

Sur ce, bonne sécurisation à tous !  

[Site officiel du projet Samhain](http://www.la-samhna.de/samhain/index.html)

*Published May 25 2011 at 09:30*
