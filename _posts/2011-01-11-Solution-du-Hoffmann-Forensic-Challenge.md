---
title: "Solution du Hoffmann Forensic Challenge"
tags: [Computer forensics, CTF]
---

Le [Hoffmann Forensic Challenge](http://www.linuxmag.nl/nl/4137085f61440) est un challenge d'[inforensique](http://fr.wikipedia.org/wiki/Inforensique) organisé par le *Linux Magazine* néerlandais dont la date de récupération des *"copies"* était le 31 décembre dernier.  

J'en profite donc pour donner ma correction à moi, peut-être pas complète mais probablement la seule disponible en ligne à l'heure actuelle.  

**EDIT:** Suite à une demande, j'ai retrouvé sur mon disque le fichier originalement fourni pour le challenge. Ceux qui souhaitent s'exercer sur ce challenge pourront le télécharger [ici](https://mega.co.nz/#!7kIjkQRD!k_KCAIhshTJiVQ86zeP5daCFdU5xWAU28hvJt8bLR9I).  

## Énoncé  

Ceux qui, comme moi, ne parlent pas le néerlandais, pouvaient se concentrer sur [une traduction anglaise](http://www.forensicfocus.com/index.php?name=Forums&file=viewtopic&t=2062) de l'énoncé.  

L'histoire (fictive) c'est qu'un certain *Willem Z* a été arrêté. À son domicile ont été trouvés du matériel pour fabriquer des explosifs, 5 ordinateurs et tous un tas de trucs montrant son attirance pour le système d'exploitation libre *GNU/Linux*.  

Malheureusement, les disques durs des ordinateurs sont chiffrés et le suspect est muet comme une carpe. Malgré cela il est probable qu'une attaque terroriste soit planifiée.  

Dans l'appareil photo de _Z_ a été trouvé une carte mémoire sur laquelle aucune photo ne semble présente. Mais la police suspecte que cette carte mémoire recèle peut-être des informations importantes, c'est pour cela qu'elle fait appel à vous, *"the forensic expert"*.  

## Questions auxquelles répondre  

* Qui sont les terroristes et quand l'attaque est-elle prévue ?
* Quel est la cible de l'attaque ?
* Pour chaque fichier important, dire quelles protections ont été prises pour cacher les données.
* Expliquez comment vous, the forensic expert avez-vous obtenu ces informations

## Décortiquage de l'image  

Le seul élément auquel on a droit est un fichier nommé `472af4e029380mmc_challenge.E01` qui correspond à l'image disque d'une [carte MMC](http://fr.wikipedia.org/wiki/Carte_MMC) d'appareil photo.  

Ce fichier ne fait que 793 Ko, et quand on lance un `file` dessus on n'obtient rien de bien parlant (data).  

De plus un `strings` ne nous donnera rien de mieux. Seule piste, le header du fichier qui commence par les lettres *"EVF"*.  

Après quelques recherches et en lisant les pages correspondant aux 3 premières références données pour le challenge, on parvient à déterminer qu'il s'agit d'un format défini par le logiciel spécialisé [EnCase](http://www.guidancesoftware.com/products/ef_index.asp). *EVF* correspond à **E**nCase E**v**idence **F**ile, mais le format en lui-même est le *Expert Witness format (EWF)*.  

On en apprend un peu plus sur ce format par le biais d'une doc pour [PyFlag](http://pyflag.sourceforge.net/Documentation/manual/iosource.html) et [une lettre d'information SleuthKit](http://www.sleuthkit.org/informer/sleuthkit-informer-23.txt) :  

> Expert witness format is a proprietary format which is mainly used by Encase and FTK. This format also compresses data in 32kb chunks to achieve a seekable compressed file. This file format must also be split across files smaller than 2gb (generally 640mb is used).
> 
> 

Pour mon analyse, je me sers uniquement de logiciels libres. J'ai dû récupérer [la librairie EWF](https://www.uitwisselplatform.nl/projects/libewf/) qui est accompagnée de quelques outils très utiles ainsi que de l'indispensable [SleuthKit](http://www.sleuthkit.org/sleuthkit/index.php) que j'ai recompilé avec EWF.  

La commande `mmls` de *SleuthKit* nous permet de mettre en évidence la présence de partitions dans l'image :  

```console
$ mmls 472af4e029380mmc_challenge.E01
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

     Slot    Start        End          Length       Description
00:  -----   0000000000   0000000000   0000000001   Primary Table (#0)
01:  -----   0000000001   0000000015   0000000015   Unallocated
02:  00:00   0000000016   0000013247   0000013232   Linux (0x83)
03:  -----   0000013248   0000013279   0000000032   Unallocated
```

On remarque la présence d'une partition Ext2 à l'offset 16. Avec `fls`, on peut lister les fichiers présents à condition de spécifier le format de l'image (EWF) et l'offset (16) :  

```console
$ fls -r -i ewf -o 16 472af4e029380mmc_challenge.E01
d/d 11: lost+found
r/r 12: file1.jpg
r/r 13: file2.jpg
r/r 14: file4.jpg
r/r 15: file5.odt
```

## Extraction des fichiers  

On voit déjà quelques fichiers présents dans l'image. À l'aide de la commande `icat` on peut les extraire (dernier argument = numéro d'inode du fichier à extraire) :  

```bash
icat -i ewf -o 16 472af4e029380mmc\_challenge.E01 12 > file1.jpg
```  

Après avoir extrait les autres fichiers et lancé un `file`, on obtient des résultats correspondant bien aux extensions... du moins pour les images :  

```plain
file1.jpg: JPEG image data, JFIF standard 1.01
file2.jpg: JPEG image data, JFIF standard 1.01
file4.jpg: JPEG image data, JFIF standard 1.01
file5.odt: data
```

La première image est une photo de deux personnes (de vraies têtes de terroristes) :  

![selfie](/assets/img/file1eu8.jpg)  

La seconde image représente... heu je passe.  

![device](/assets/img/file2yd8.jpg)  

La troisième image est cassée (*"premature end of data segment"*) mais de toute évidence, il s'agit d'une copie d'écran d'une photo satellite pompée sur *Google Maps*.  

Quant à notre fichier *ODT* (format *OpenOffice.org*), si on le regarde de plus prêt (avec un héditeur hexadécimal) on remarque quelque chose d'assez particulier :  

```plain
4b 50 04 03 00 14 00 00  00 00 96 5b 37 44 c6 5e  |KP.........[7D.^|
0c 32 00 27 00 00 00 27  00 00 00 08 00 00 69 6d  |.2.'...'......im|
65 6d 79 74 65 70 70 61  6c 70 63 69 74 61 6f 69  |emyteppalpcitaoi|
```

Les plus attentifs auront compris que pour les octets du fichiers ont été inversés deux à deux. Un fichier OpenOffice n'est rien de plus qu'une archive ZIP avec des fichiers pour le style, la définition et le contenu du document. Or une archive ZIP commence par *"PK"* et non *"KP"*. De même au lieu de lire *"imemytep"* il faut lire *"mimetype"*.  

Un script Python vite-fait-mal-fait, permet de remettre les choses en ordre (output à rediriger vers un fichier) :  

```python
import sys
fd=open("file5.odt")
buff=fd.read()
count=len(buff)
reste=count%2
if reste==1: count-=1
for i in range(0,count,2):
  chars=buff[i+1]+buff[i]
  sys.stdout.write(chars)
if reste==1:
  sys.stdout.write(buff[len(buff)-1])
fd.close()
```

On ouvre le fichier ODT corrigé. Ce dernier est un document vantant les mérites d'Ubuntu, si ce n'est qu'une page a été ajoutée avec les lignes suivantes :  

> wachtwoord=slechtetijden  
> steghide gebruiken om te extracten
> 
> 

Sans être néerlandais pour autant, j'aurais tendance à dire qu'il faut se servir de *steghide* (un logiciel de stéganographie) pour extraire des données d'une des images et ce en utilisant le mot *"slechtetijden"* comme mot de passe.  

Malheureusement tous nos essais sont voués à l'échec. De toute évidence, les fichiers sont incomplets ou alors c'est l'image corrompue qui contient les données cachées.  

## Extraction des fichiers (seconde méthode)  

Cette fois-ci on va faire du [carving](http://www.forensicswiki.org/wiki/Carving) sur le système de fichier en brut. Pour cela il faut l'extraire de l'image EWF.  
Les outils fournis avec la libewf s'avèrent très efficaces (prendre les options par défaut pour `ewfexport`) :  

```console
$ ewfinfo 472af4e029380mmc_challenge.E01
ewfinfo 20071209 (libewf 20071209, zlib 1.2.3, libcrypto 0.9.8)

Acquiry information
        Case number:            1
        Description:            Hoffmann forensic challenge for Linux magazine
        Examiner name:          TGP
        Evidence number:        1
        Notes:                  MMC San disk found in digital camera
        Acquiry date:           Tue Oct  9 13:23:45 2007
        System date:            Tue Oct  9 13:23:45 2007
        Operating system used:  Linux
        Software version used:  20070512
        Password:               N/A

Media information
        Media type:             fixed disk
        Media is physical:      yes
        Amount of sectors:      13280
        Bytes per sector:       512
        Media size:             6799360
        Error granularity:      64
        Compression type:       best compression
        GUID:                   00000000-0000-0000-0000-000000000000
        MD5 hash in file:       ff810a83895039486e813c675ada6b39

$ ewfexport -t plop 472af4e029380mmc_challenge.E01
ewfexport 20071209 (libewf 20071209, zlib 1.2.3, libcrypto 0.9.8)

Information for export required, please provide the necessary input
Export to file format (raw, ewf, smart, ftk, encase1, encase2, encase3, encase4, encase5, encase6, linen5, linen6, ewfx) [raw]:
Start export at offset (0 >= value >= 6799360) [0]:
Amount of bytes to export (0 >= value >= 6799360) [6799360]:

Export started at: Thu Dec 20 17:50:26 2007

This could take a while.

Export completed at: Thu Dec 20 17:50:26 2007

Written: 6.4 MiB (6799360 bytes) in 0 second(s).
```

On peut maintenant travailler sur le fichier `plop` :  

```console
$ file plop
plop: x86 boot sector, extended partition table (last)\011
```

Pour le carving, j'ai eu recours à [Foremost](http://foremost.sourceforge.net/) (nécessite un fichier de conf bien fourni en entêtes) puis à [PhotoRec](http://www.cgsecurity.org/wiki/PhotoRec_FR) qui s'est montré bien plus efficace.  

```console
$ photorec /debug plop
```

Les fichiers obtenus et leur somme MD5 sont :  

```plain
270a0a913fa9603db8121fdf78d63aca  f10258.jpg
589032f2ec313816ef36772a08808db0  f10318.jpg
59bcfa18339749f1d25a6d30a2668a64  f10526.jpg
e92a8f1202253443274122572bbb00d3  f11616.jpg
```

Les deux premiers fichiers, nous les connaissons déjà.  
Le troisième est la copie d'écran de Google Maps... mais au complet :  

![](/assets/img/gmap.jpg)  

Enfin, le dernier est une autre version du fichier que l'on connait déjà (le composant électronique) car la somme MD5 ne correspond pas. En réalité il s'agit du fichier où on été dissimulé les données. On se sert alors de steghide pour les extraire :  

```console
$ steghide extract -sf f11616.jpg -xf hidden_data
Enter passphrase:
wrote extracted data to "hidden_data".
```

Le contenu du fichier texte obtenu est le suivant :  

```plain
Contact codenaam        e-mail  gsm
piet    de spier        despier@mail.com        06-11111111
karel   de gok  degok@mail.com  06-22222222
henk    de arm  dearm@email.com 06-33333333
johan   de teen deteen@postvak.nl       06-44444444
sondra  de oorbel       deoorbel@postbak.nl     06-55555555
jimmy   oerwoud oerwoude@jungle.nl      06-66666666
bertus  de melker       demelker@mail.com       06-77777777

        2 januari worden de bloemetjes buiten gezet
```

La liste correspondant très probablement à la liste des terroristes, il ne nous reste plus qu'à traduire la dernière ligne à l'aide de [Google Translate](http://www.google.com/translate_t) (*Dutch to English*).  

On en déduit que ces crétins-là veulent faire exploser des tulipes au [Keukenhof](http://fr.wikipedia.org/wiki/Keukenhof), un parc floral situé au nord-ouest de *Lisse*, en *Hollande*. L'attaque est planifiée pour le 2 janvier.  

[Site officiel du parc Keukenhof](http://www.exoti.com/rubriques/keukenhof/keukenhof.html).  

Pour revenir à la troisième question, les protections prises par le suspect pour protéger ses données étaient le *"cryptage"* du fichier ODT, l'utilisation de *steghide* et un système de fichier qui a été cassé (intentionnelement ou non, je ne saurais dire)

*Published January 11 2011 at 08:02*
