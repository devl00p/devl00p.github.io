---
title: "Stéganographie et Unicode (UTF-8)"
tags: [Stéganographie]
---

## Mise en bouche  

Jetez un œil à ce texte, [extrait d'une page Wikipedia](http://en.wikipedia.org/wiki/Letter_frequencies) :   

> The frequency of letters in text has often been studied for use in cryptography, and frequency analysis in particular. No exact letter frequency distribution underlies a given language, since all writers write slightly differently. Linotype machines sorted the letters' frequencies as etaoin shrdlu cmfwyp vbgkqj xz based on the experience and custom of manual compositors.  

Et maintenant jetez un autre œil au texte suivant :   

> Thе frequеncy of lettеrѕ in tеxt Һas oftеn beеn studіed for uѕe in сryptogrарhу, and freqυеncy analуѕis in pаrticular. Νо eхасt lettеr frequеncy dіstribution underlies a given language, since all writers write slightly differently. Linotype machines sorted the letters' frequencies as etaoin shrdlu cmfwyp vbgkqj xz based on the experience and custom of manual compositors.  

Vous semblent-ils différents ? Peut-être avez-vous remarqué une particularité dans l'un des textes... car l'un d'entre eux contient un message secret.  

Jeter un coup d'œil au code HTML de cette page vous donnera certainement un indice, pourtant j'aurais très bien pu vous montrer deux textes bruts (plain text) et vous n'aurez pas forcément remarqué plus de particularités.  

## L'unicode : qu'est-ce que c'est et pourquoi on nous emmerde avec  

L'[unicode](http://fr.wikipedia.org/wiki/Unicode) est une norme de codage des caractères destinée à être utilisée massivement pour rassembler et remplacer les normes existantes de différents pays.  

On pourrait représenter l'unicode comme une énorme table de correspondance entre les caractères et leurs valeurs informatique comme on peut en trouver pour l'[ASCII](http://www.asciitable.com/).  

Pendant longtemps, chacun y allait de sa norme de codage des caractères : ASCII et ISO 8859-1 pour les occidentaux, le Big5 pour les Chinois, le KOI8-U pour les Russes, le Shift-JIS ou encore le ISO 2022 pour les Japonais.  

On peut imaginer que cette diversité de normes n'arrange pas les développeurs qui souhaitent rendre leurs logiciels accessibles au plus de personnes possibles, quelque soit leur langue.  

Unicode se *"décline"* en plusieurs formats : [UTF-8](http://fr.wikipedia.org/wiki/UTF-8), UTF-16 et UTF-32.  

Il y a aussi l'[UTF-7](http://en.wikipedia.org/wiki/UTF-7) utilisé par des protocoles d'envoi de courrier et on parle de UTF-5 ou d'UTF-6, chacun ayant pour spécificité d'être compatible avec un *"alphabet"* prédéfini comme ceux (limités) utilisés pour composer une adresse email ou un nom de domaine.  

Le nombre situé derrière les caractères *UTF* correspond au nombre de bits minimum nécessaire pour l'encodage d'un caractère.  

Le format dont cet article parlera sera l'UTF-8 qui est principalement utilisé par nous autres européens ou américains.  

Ce format-là a en effet le grand avantage d'être rétro-compatible avec l'ASCII, c'est-à-dire que la plupart des caractères que l'on utilise sont encodés sur un octet, exactement comme ils l'étaient auparavant.  

Ce *"miracle"* tient sur le fait que l'UTF-8 utilise les premiers bits de chaque octet pour déterminer s'il a affaire à nos bons vieux caractères où s'il doit chercher dans des tables plus exotiques.  

Ainsi notre petit `a` sera codé `0x61` en hexa comme c'était le cas en ASCII, mais le `à` avec accent tiendra sur deux caractères et se codera `0xC3A0`.  

[La page Wikipedia sur l'UTF-8](http://fr.wikipedia.org/wiki/UTF-8) montre quels bits sont utilisés sur chaque octet.  

L'UTF-8 est donc, comme d'autres formats d'unicode, extensible. Comme dit [sur cette page](http://www.tbray.org/ongoing/When/200x/2003/04/26/UTF), on pourrait qualifier le format UTF-8 de raciste : quand nos caractères sont encodés sur un ou deux octets, les Thaïlandais ou les coréens ont droit à 3 octets par caractère !  

Pas de quoi les motiver à utiliser UTF-8, heureusement l'UTF-16 et l'UTF-32 mettent tout le monde à un niveau d'égalité (toutefois l'UTF-32 prend comme son nom l'indique 4 octets par caractère).

## UTF-8 : représentation, encodage et décodage en Python...  

Quand on veut nommer un caractère en unicode, on utilise généralement la forme `U+XXXX` où `XXXX` est un nombre hexadécimal dont la taille peut varier.  

Pour *"fouiller"* dans l'unicode, il y a trois sites quasi-indispensables :  

[decodeunicode.org](http://www.decodeunicode.org/en/) : une mine d'or à l'interface soignée.  

[FileFormat.Info](http://www.fileformat.info/info/unicode/) : très pratique, le site offrent aussi des ressources en dehors d'unicode  

[Unicode.org](http://www.unicode.org/fr/charts/) : le site officiel avec les tables de caractères au format PDF.  

[Unimap (unipad.org)](http://www.unipad.org/unimap/) : assez simple mais efficace.  

Si vous programmez, vous vous êtes peut-être déjà arraché les cheveux devant des problèmes de mauvais encodages. Mon expérience m'a montré que le mieux est encore d'aller à la source et de corriger directement le mauvais caractère (par exemple dans une page html) au lieu de tenter de le convertir/corriger.  

Je vous donne tout de même quelques commandes pratiques en Python pour jouer avec les caractères unicode.  

Définissons un caractère `s` dont la valeur est `é` et observons son type :   

```python
>>> s='é'
>>> type(s), repr(s)
(<type 'str'>, "'\\xc3\\xa9'")
```

`s` est un caractère `brut` : c'est un type `str` et non unicode. On voit toutefois qu'il est codé sur deux octets, il est donc bien au format UTF-8, mais n'offre pas les avantages de la classe unicode.  

Transformons ce caractère au type unicode :   

```python
>>> u=unicode(s,"UTF-8")
>>> type(u), repr(u)
(<type 'unicode'>, "u'\\xe9'")
```

Le caractère unicode auquel on a à faire est donc le [U+00E9](http://www.decodeunicode.org/de/u+00e9).  

Renseignons-nous sur ce caractère :   

```python
>>> import unicodedata
>>> unicodedata.name(u)
'LATIN SMALL LETTER E WITH ACUTE'
>>> unicodedata.lookup('LATIN SMALL LETTER E WITH ACUTE')
u'\xe9'
```

Le type python unicode ne permet pas de tout faire, on pourrait le qualifier de *"virtuel"*. On est obligé de le mettre en *"dur"* (l'encoder) pour effectuer certaines opérations comme écrire dans un fichier.  

```python
>>> u.encode("UTF-8")
'\xc3\xa9'
```

D'autres commandes pratiques :   

```python
>>> ord(u)
233
>>> unichr(233)
u'\xe9'
>>> u.encode('ascii', 'xmlcharrefreplace')
'é'
```

## UTF-8 et stéganographie  

L'idée d'utiliser l'unicode pour dissimuler des données m'est venue en me demandant s'il n'y avait pas plusieurs façons d'encoder le même caractère. Après tout, chaque format (ASCII, UTF-8, UTF-16...) offre différents encodages pour un même caractère alors pourquoi pas le même caractère dans un même format ? Avec deux encodages possibles on peut donc glisser un bit (valeur 0 pour un encodage, valeur 1 pour le second).  

Mes recherches sur Internet m'ont montré que non seulement je n'étais pas le seul à y avoir pensé, mais en plus certains l'avaient déjà implémenté. Je n'invente donc rien, mais je vous fournis les techniques utilisées.  

**La première technique** est proposée [par MockingEye](http://www.mockingeye.com/index.php/2008/12/29/unistegpy-hiding-text-in-text-using-unicode/) et son implémentation [unisteg.py](http://www.mockingeye.com/wp-content/uploads/2008/12/unisteg.py).  

Elle se base sur les [diacritiques](http://fr.wikipedia.org/wiki/Diacritique). Typiquement ce sont les accents et cédilles qui peuvent être attachés à un caractère.  

Si vous vous rendez sur [le bloc des diacritiques sur decodeunicode.org](http://www.decodeunicode.org/en/combining_diacritical_marks), vous verrez tout de suite de quoi je veux parler.  

Unicode permet donc d'encoder de deux façons différentes nos lettres à accent. Soit sous leur forme fixe (le `é`) soit sous une forme combinée (la lettre `e` combinée avec [le diacritique de l'accent aigue](http://www.decodeunicode.org/en/u+0301)).  

Le passage de la forme composée à la forme décomposée (et vice-versa) peut se faire par la fonction normalize de la librairie [unicodedata](http://docs.python.org/library/unicodedata.html) en python :   

```python
>>> unicodedata.normalize("NFD", u)
u'e\u0301'
>>> unicodedata.normalize("NFC", u'e\u0301')
u'\xe9'
>>> unicodedata.normalize("NFD", u).encode("UTF-8")
'e\xcc\x81'
```

On remarque que le diacritique ne précède pas le caractère, mais le suit. Pour faire simple :  

![e combining diacritical](https://raw.githubusercontent.com/devl00p/blog/master/images/concat.png)

**La seconde méthode** est [proposée par Antonio Alcorn](http://www.cs.trincoll.edu/~aalcorn/steganography/). Elle est implémentée en PHP, mais le code source n'est pas disponible. Toutefois en analysant le résultat, on se rend compte que la technique se base sur l'utilisation de caractères différents, mais visuellement très proche.  

Par exemple, notre `e` est très proche [du petit IE cyrillique](http://www.decodeunicode.org/en/u+0435).  

[Les caractères cyrilliques](http://www.decodeunicode.org/en/cyrillic) sont plus bruts que nos caractères et sont généralement représentés sans serif (voir [empattement](http://fr.wikipedia.org/wiki/Empattement_(typographie))). En fonction de la police utilisée pour afficher les caractères, on ne verra donc pas la différence. On se servira pour ce faire d'une police sans-serif comme Arial.  

Dans le second texte au début de cet article, vous avez peut-être remarqué que le `h` de `has` était plus large. C'est tout simplement parce qu'il s'agit du [caractère cyrillique SHHA (U+04BA)](http://www.decodeunicode.org/en/u+04ba/properties).  

Ayant créé moi-même mes outils de stéganographie UTF-8 (voir çi-dessous), la recherche des caractères similaires m'a pris un bon moment. J'ai rassemblé ça dans [ce fichier](/assets/data/unicode_similar.txt).  

Les caractères où la différence n'est pas visible (avec la bonne police) sont placés directement. Ceux où l'on peut se laisser prendre sont entre parenthèses avec le signe + accolé. Ceux entre parenthèses ressemblent d'assez loin.  

## utf8hide et utf8reveal  

[utf8hide.py](/assets/data/utf8hide.py) permet comme son nom l'indique de cacher des données dans un texte.  

Il demande deux arguments : le fichier dont il faut cacher le contenu et un fichier texte **au format ISO-8859-1 ou ASCII**. Un troisième argument (*"html"*) peut être passé si on souhaite ensuite injecter le résultat dans une page web.  

J'ai repris l'idée de l'implémentation PHP qui propose d'utiliser seulement 5 bits pour coder un caractère à cacher en la poussant plus loin et sans les limitations.  

Le programme fait une analyse du fichier à dissimuler et détermine le plus petit nombre de bits nécessaire pour coder un octet. Si le message secret est court, il définit un charset (alphabet) lui permettant ainsi de *"comprimer"* un octet sur seulement quelques bits (3, 4, 5, 6). Au-delà, le charset serait trop gros et le programme préfère utiliser les codes habituels des caractères.  

Le résultat obtenu est placé dans le fichier `out.txt`. L'affichage donne le nombre de bits pour un octet (nbit), le charset utilisé et la taille du fichier secret. Il faut conserver ces paramètres pour l'opération inverse.  

Un peu à l'instar de [ThumbStego]({% link _posts/2011-01-11-ThumbStego.md %}) qui nécessitait une image et sa signature, [utf8reveal.py](/assets/data/utf8reveal.py) a besoin du texte ascii/iso8859 qui a servi à dissimuler le fichier et la version UTF-8 dans laquelle sont cachées les données.  

On lui passe aussi en argument les variables vues plus tôt et le programme recréé le fichier secret dans `secret.xxx`.  

Les deux programmes affichent les bits à l'écran (0 ou 1) ce qui peut-être ennuyeux pour les gros fichiers... mais une telle utilisation est à éviter.  

En effet, le programme a beau compresser comme il peut les données en entrées et utiliser la méthode des diacritiques ainsi que celle des ressemblances entre caractères, tous les caractères ne sont malheureusement pas exploitables. Le programme passe alors aux caractères suivant jusqu'à tomber sur un caractère exploitable. Le ratio est donc bien plus faible que 1/8ème mais c'est suffisant pour y passer quelques mots.  

## Arghhh  

J'ai eu la peur de ma vie (c'est quelque peu exagéré) en développant le code. En voulant recopier mes scripts vers un répertoire de sauvegarde, j'ai bêtement tapé `rm -r` au lieu de `cp`, supprimant ainsi les codes et le répertoire de sauvegarde.  

À défaut de faire n'importe quoi, je me suis félicité d'avoir quelques connaissances en inforensique, ce qui m'a permis d'extraire le code de la partition. Pourtant, comme le code fait plus de 4096 octets, il était sur deux blocs mémoire et sur du `ext3`... merci à `grep`, `dd` et `hexdump`.

*Published January 16 2011 at 10:24*
