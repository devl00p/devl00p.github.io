---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress JP Theme Switcher Bar"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [JP Theme Switcher Bar](https://wordpress.org/plugins/jp-theme-bar/) (slug: `jp-theme-bar`) se présente de cette façon :

> Use this plugin to create a demo site for your themes, or use it to allow users to customize the presentation of your site.

> The JP Theme Bar Plugin adds a theme switching bar to the bottom of your site, perfect for theme preview sites. The settings page for the plugin lets the end user choose which themes to add, as well as set the colors for the theme bar. You can see it in action on this site.
 
La version testée est la 0.1.0 qui date d'il y a 9 ans.

## La vulnérabilité

Dans le script `jptb-frontend.php` le plugin hook la gestion des liens en faisant en sorte que Wordpress utilise la fonction `keep_query_var` :

```php
class jptb_frontend {
   function __construct() {
       add_action( 'wp_enqueue_scripts', array( $this, 'scriptsNstyles' ) );
       add_action( $this->where(), array( $this, 'html_bar') );
       add_action( 'wp_enqueue_scripts', array( $this, 'inline_style' ) );
       add_filter( 'query_vars', array( $this, 'add_theme_var' ) );
       if ( get_option( 'jptb_mod_switch' ) == 1 ) {
           add_action( 'after_theme_setup', array( $this, 'theme_settings' ) );
       }
       $filters = $this->link_filters();
       foreach ( $filters as $filter ) {
           add_filter( $filter, array( $this, 'keep_query_var' ) );
       }
   }
```

Cette fonction modifie les liens pour rajouter le paramètre `theme` :

```php
    /**    
     * Keep the query var for links
     *
     * @package jptb
     * @since 0.0.3
     */
    function keep_query_var( $link ) {
        //get the theme with the query var
        $theme = get_query_var( 'theme' );
        //set to current stylesheet if none is being previewed.
        if ( $theme === '' ) {
            $theme = get_stylesheet();
        }
        $link = add_query_arg( 'theme', $theme, $link );
        return $link;
    }
```

Pour cela le plugin emploie la fonction [add_query_arg](https://developer.wordpress.org/reference/functions/add_query_arg/) de Wordpress qui stipule :

> Important: The return value of add_query_arg() is not escaped by default. Output should be late-escaped with esc_url() or similar to help prevent vulnerability to cross-site scripting (XSS) attacks.

Ici, on voit qu'aucun filtrage n'est effectué ce qui rend le plugin vulnérable à une faille XSS par le paramètre `theme`.

PoC:

```
http://localhost:8000/?theme=%22%3E%3C%2Fa%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
```
