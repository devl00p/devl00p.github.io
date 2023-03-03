---
title: "Analyse forensique d'un système Windows : partie 1"
tags: [Computer forensics, Windows]
---

## Avant-propos  

L'*inforensique* (version francisée du terme [computer forensics](http://en.wikipedia.org/wiki/Computer_forensics)) est l'ensemble des techniques visant à analyser un système informatique dans le but de collecter des informations et de recréer une image de l'activité ayant eu lieu sur ce système informatique.  

Principalement utilisée dans le cas d'investigations liées à la cybercriminalité, on l'appelle parfois *"analyse post-intrusion"* ou *"analyse post-mortem"* dans le cas de l'analyse d'un système informatique ayant rendu l'âme.  

L'inforensique est souvent liée à la récupération de données ([data recovery](http://en.wikipedia.org/wiki/Data_recovery)) effacées ou non. Dans le cas de la récupération de données effaçées on peut distinguer deux méthodes : la récupération basé sur les métadonnées ou sur les entêtes du fichier ([file carving](http://www.forensicswiki.org/wiki/Carving))  

Ces définitions ne sont pas officielles et sujettes à améliorations.  

## Informations et scénario  

Le système que nous allons étudier a été mis à disposition par le [NIST](http://www.nist.gov/) ([National Institute of Standards and Technology](http://en.wikipedia.org/wiki/National_Institute_of_Standards_and_Technology)) et fait partie de son projet *Computer Forensic Reference Data Sets* (*CFReDS*)  

Les données auxquelles nous avons accès sont l'image d'un disque dûr réalisée à l'aide de la commande de copie bas niveau `dd`. L'image a une taille de 4.4Go, aussi elle a été découpée en 7 morceaux de 636Mo.  

Les fichiers et les informations nécessaires sont disponibles sur la page [Hacking Case](http://www.cfreds.nist.gov/Hacking_Case.html).  

Le scénario est le suivant : Un portable Dell CPi, numéro de série VLQLW, a été trouvé abandonné avec une carte wireless PCMCIA et une antenne externe 802.11b fait maison.  

Ce portable est suspecté d'avoir été utilisé pour réaliser des attaques informatiques, bien qu'à l'heure actuelle on ne peut pas faire le lien avec un suspect nommé *Greg Schardt*, connu aussi pour ses activitées de hacking sous le pseudonyme *"Mr. Evil"*.  

*M. Schardt* aurait apparemment l'habitude de faire du wardriving pour tenter de récupérer des informations confidentielles telles que login et passwords, numéros de cartes de crédit...  

L'objectif est de prouver que l'ordinateur a servi à des fins de piratage et de faire le lien entre *Greg Schardt* et l'ordinateur.  

## Quelques notes avant de commencer  

Comme nous le verrons, le disque analysé contient le système d'exploitation Windows XP. C'est une sacrée chance d'avoir l'occasion d'analyser un système Windows puisque pour des raisons légales on ne trouve généralement que des images de systèmes GNU/Linux ou des images ne contenant pas un système d'exploitation (pour des tests de carving par exemple).  

En effet, les exécutables Windows sont sous licence propriétaire Microsoft par conséquent la mise à disposition de ces fichiers, Quelle que soit la forme sous laquelle ils se trouvent, n'est pas très légale. Mais comme le NIST dépend du Département US du Commerce je suppose qu'on a affaire à une exception (puis on ne va pas s'en plaindre).  

Au total, il nous faut répondre à 31 questions sur le système étudié. Cela nous facilite la tâche puisque nous saurons plus ou moins où chercher les informations.  
J'ai réalisé l'analyse sans tricher (je regarderais les solutions une fois toutes les parties de l'article mises en ligne) et en utilisant de préférences des logiciels libres et/ou gratuit.  

## Vérification des fichiers et génération d'une image unique  

Après avoir téléchargé les 7 morceaux de l'image et avoir vérifié que leurs hashs md5 correspondaient à ceux [présents dans les notes](http://www.cfreds.nist.gov/images%5Chacking-dd%5CSCHARDT.LOG), on peut passer à la concaténation des fichiers en un fichier unique :  

```bash
cat images\\hacking-dd\\SCHARDT.002 >> images\\hacking-dd\\SCHARDT.001
cat images\\hacking-dd\\SCHARDT.003 >> images\\hacking-dd\\SCHARDT.001
cat images\\hacking-dd\\SCHARDT.004 >> images\\hacking-dd\\SCHARDT.001
cat images\\hacking-dd\\SCHARDT.005 >> images\\hacking-dd\\SCHARDT.001
cat images\\hacking-dd\\SCHARDT.006 >> images\\hacking-dd\\SCHARDT.001
cat images\\hacking-dd\\SCHARDT.007 >> images\\hacking-dd\\SCHARDT.001
```

Comme vous pouvez vous en douter il faut avoir quelques giga octets de libres sur son disque pour récupérer les images.  

Je m'assure ensuite que l'image ne sera pas modifiée par mégarde et je la renomme en quelque chose de plus maniable :  

```console
# chmod -w images\\hacking-dd\\SCHARDT.001
# mv images\\hacking-dd\\SCHARDT.001 nist.img
# ls -lh nist.img
-r-------- 1 root root 4,4G avr 15 21:11 nist.img
# md5sum nist.img
f2e794489133b98c7106fd97cdf5a27f  nist.img
```

## What is the image hash? Does the acquisition and verification hash match?  

Le hash de l'image entière est `f2e794489133b98c7106fd97cdf5a27f`. Les hahs des fichiers téléchargés correspondant bien à ceux présents dans les notes, de plus la vérification du hash global après l'analyse est bien le même que le hash obtenu après concaténation, preuve que l'analyse s'est faite sans altération.  

## What operating system was used on the computer?  

Le résultat de la commande file sur l'image *nist.img* nous donne le résultat suivant :  

> x86 boot sector, Microsoft Windows XP MBR, Serial 0xec5dec5d; partition 1: ID=0x7, active, starthead 1, startsector 63, 9510417 sectors

Montons maintenant l'image en lecture seule et promenons-nous sur ce disque dûr :  

```console
# mount -o loop,ro,offset=32256 nist.img /mnt/
# cd /mnt/
# ls
AUTOEXEC.BAT  BOOTSECT.DOS  Documents and Settings  MSDOS.---     ntdetect.com   RECYCLER      System Volume Information  WINDOWS
boot.ini      COMMAND.COM   FRUNLOG.TXT             MSDOS.SYS     ntldr          SETUPLOG.TXT  Temp
BOOTLOG.PRV   CONFIG.SYS    hiberfil.sys            My Documents  pagefile.sys   SUHDLOG.DAT   VIDEOROM.BIN
BOOTLOG.TXT   DETLOG.TXT    IO.SYS                  NETLOG.TXT    Program Files  SYSTEM.1ST    WIN98
# cat boot.ini
[boot loader]
timeout=30
default=multi(0)disk(0)rdisk(0)partition(1)\WINDOWS
[operating systems]
multi(0)disk(0)rdisk(0)partition(1)\WINDOWS="Microsoft Windows XP Professional" /fastdetect
```

A priori le système est un Windows XP. Faisons une vérification supplémentaire en regardant le numéro de version inscrit dans la base de registre.  

Pour cela j'ai utilisé un petit programme perl nommé *"Offline Registry Parser"* et développé par *Harlan Carvey* (*keydet89*), l'auteur du blog [*Windows Incident Response*](http://windowsir.blogspot.com/) et du livre *"Windows Forensic Analysis"*.  

Ça aurait peut-être été plus facile d'utiliser les fonctionnalités d'éditeur de registre de [*chntpw*](http://home.eunet.no/pnordahl/ntpasswd/) mais le `regp.pl` est le premier outil que j'ai essayé et j'ai continué avec.  

La base de registre Windows est stockée dans différents fichiers que l'on appelle des *"ruches"* (*hives*). La plupart se trouvent dans le répertoire `WINDOWS/system32/config/`.  

Les ruches spécifiques aux utilisateurs sont les fichiers `NTUSER.DAT` se trouvant dans `Documents and Settings/<username>/`.  

La correspondance entre les ruches et l'arborescence du registre est la suivante :  

```
Default : HKEY_USERS\.Default
SAM : HKEY_LOCAL_MACHINE\SAM
Security : HKEY_LOCAL_MACHINE\Security
Software : HKEY_LOCAL_MACHINE\Software
System : HKEY_LOCAL_MACHINE\System
NTUSER.DAT : KKEY_CURRENT_USER
```

Avec la commande `perl regp.pl WINDOWS/system32/config/software` on affiche le contenu de `HKEY_LOCAL_MACHINE\Software` dans lequel on trouve :  

```
\$$$PROTO.HIV\Microsoft\Windows NT\CurrentVersion
LastWrite time: Fri Aug 27 15:08:22 2004
        --> CurrentBuild;REG_SZ;1.511.1 () (Obsolete data - do not use)^@
        --> InstallDate;REG_DWORD;1092955707
        --> ProductName;REG_SZ;Microsoft Windows XP^@
        --> RegDone;REG_SZ;^@
        --> RegisteredOrganization;REG_SZ;N/A^@
        --> RegisteredOwner;REG_SZ;Greg Schardt^@
        --> SoftwareType;REG_SZ;SYSTEM^@
        --> CurrentVersion;REG_SZ;5.1^@
        --> CurrentBuildNumber;REG_SZ;2600^@
        --> BuildLab;REG_SZ;2600.xpclient.010817-1148^@
```

On est bien sur un système Windows XP.  

## When was the install date?  

Dans le listing précédent, on trouve la clé `InstallDate`. Elle correspond au nombre de secondes écoulées depuis le 1er janvier 1970 (un format récurrent sur les systèmes UNIX). Pour traduire ça j'ai fait un petit programme en C :  

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(void)
{
  time_t t=1092955707;
  printf("%s",ctime(&t));
  return 0;
}
```

On compile et on lance, on obtient *"Fri Aug 20 00:48:27 2004"*. Les dates des fichiers sur le disque (que l'on peut avoir avec un simple `ls -l` une fois le système monté) correspondent aussi au mois d'août.  

Pour savoir où fouiller dans la base de registres j'ai trouvé deux documents PDF sympathiques :  

[Forensic Analysis of the Windows Registry](http://www.forensicfocus.com/downloads/forensic-analysis-windows-registry.pdf)  

[Access Data : Registry Quick Find Chart](http://www.accessdata.com/media/en_US/print/papers/wp.Registry_Quick_Find_Chart.en_us.pdf)  

## What is the timezone settings?  

On trouve l'information dans la ruche `system` :  

```
\$$$PROTO.HIV\ControlSet001\Control\TimeZoneInformation
LastWrite time: Thu Aug 19 17:20:02 2004
        --> Bias;REG_DWORD;360
        --> StandardName;REG_SZ;Central Standard Time^@
        --> StandardBias;REG_DWORD;0
        --> StandardStart;REG_BINARY;00 00 0a 00 05 00 02 00 00 00 00 00 00 00 00 00
        --> DaylightName;REG_SZ;Central Daylight Time^@
        --> DaylightBias;REG_DWORD;4294967236
        --> DaylightStart;REG_BINARY;00 00 04 00 01 00 02 00 00 00 00 00 00 00 00 00
        --> ActiveTimeBias;REG_DWORD;300
```

Un [article de WindowsITPro](http://www.windowsitpro.com/Articles/ArticleID/14966/14966.html?Ad=1) nous donne plus d'information sur le sens des différentes clés.  

Le système est en décalage de 6 heures par rapport à l'heure de Greenwich (6 \* 60 = 360). Cela fait pointer la zone horaire de notre pirate vers l'Amérique du Nord (Canada, Etats-Unis) ou le Mexique. La description de la timezone, [Central Time](http://wwp.greenwichmeantime.com/time-zone/usa/central-time/) correspond à nos calculs.  

## Who is the registered owner?  

Comme nous l'avons vu précédemment, dans `Software\Microsoft\Windows NT\CurrentVersion`, on trouve une clé nommée *RegisteredOwner* dont la valeur est *"Greg Schardt"*... pwn3d !  

## What is the computer account name?  

Réponse dans la ruche `system` :  

```
\$$$PROTO.HIV\ControlSet001\Control\ComputerName\ComputerName
LastWrite time: Thu Aug 19 22:20:03 2004
        --> ComputerName;REG_SZ;N-1A9ODN6ZXK4LQ^@
```

## What is the primary domain name?  

Le domaine Windows utilisé par défaut est mémorisé par `WinLogon` (ruche software) :  

```
\$$$PROTO.HIV\Microsoft\Windows NT\CurrentVersion\Winlogon
LastWrite time: Fri Aug 27 15:08:20 2004
        --> DefaultDomainName;REG_SZ;N-1A9ODN6ZXK4LQ^@
        --> DefaultUserName;REG_SZ;Mr. Evil^@
```

## When was the last recorded computer shutdown date/time?  

Toujours dans la base de registre Windows qui est une véritable mine d'information (ruche `system`):   

```
\$$$PROTO.HIV\ControlSet001\Control\Windows
LastWrite time: Fri Aug 27 15:46:33 2004
        --> Directory;REG_EXPAND_SZ;%SystemRoot%^@
        --> ErrorMode;REG_DWORD;0
        --> NoInteractiveServices;REG_DWORD;0
        --> SystemDirectory;REG_EXPAND_SZ;%SystemRoot%\system32^@
        --> ShellErrorMode;REG_DWORD;1
        --> ShutdownTime;REG_BINARY;c4 fc 00 07 4d 8c c4 01
```

Cette fois, j'ai fait appel à un outil non libre, mais gratuit : [Decode - Forensic Date/Time Decoder](http://www.digital-detective.co.uk/freetools/decode.asp)  
C'est un petit utilitaire qui tourne sous Windows (ou wine avec les bonnes dlls).  

![Forensic Time Decoder](/assets/img/dcode.jpg)

J'avoue ne pas mettre soucié beaucoup de cette histoire de timestamp... Il faut normalement retirer 6 heures pour obtenir la bonne heure.  

## How many accounts are recorded (total number)?  

La réponse se trouve bien sûr dans la ruche `SAM`. On trouve les noms d'utilisateurs suivants : `SUPPORT_388945a0`, `Guest`, `Mr. Evil`, `HelpAssistant` et `Administrator`.  

En dehors de *Mr. Evil*, tous correspondent à des comptes classiques pour un Windows XP. Dans une telle configuration, il est fort à parier que *Mr. Evil* est l'un des administrateurs du poste.  

## What is the account name of the user who mostly uses the computer?  
## Who was the last user to logon to the computer?  

Avec ce que l'on a vu précédemment, la présence de *Mr. Evil* dans la mémoire de `WinLogon` et le nombre de fichiers dans les répertoires personnels de cet utilisateur, je réponds *Mr. Evil*.  

Fin de la première partie. See you soon

*Published January 09 2011 at 17:30*
