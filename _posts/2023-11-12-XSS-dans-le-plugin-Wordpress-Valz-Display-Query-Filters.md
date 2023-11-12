---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Valz Display Query Filters"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Valz Display Query Filters](https://wordpress.org/plugins/valz-display-query-filters/) se présente de cette façon :

> This plugin, once activated, spits out the information passed by each filter used in manipulating database queries, as a learning tool.
> 
> The code itself is heavily documented and demonstrates best practices for working with those filters and actions to view / manipulate the query.
> 
> It is very important to note that this plugin is not meant for a production environment as it will insert a lot of really ugly HTML throughout your page. You’ll get the most use out of this plugin by looking at its code, and maybe previewing one or two pages on a sandbox, vanilla WordPress site.

L'auteur est assez explicite sur le fait que ce plugin sert pour du debugging et ne devrait pas être utilisé en production. 

Nous allons tout de même voir de quoi il s'agit.

La version testée est la 0.1 et date d'il y a 11 ans au moment de ces lignes.

## La vulnérabilité

Il n'y a qu'un unique script, `valz_display_query_filters.php`, qui hooke de nombreuses fonctions de Wordpress :

```php
class Valz_Query_Filters {                                                                                             
    function __construct(){                                                                                            
        add_filter( 'request', array( $this, 'request_filter' ) );                                                     
        add_action( 'parse_request', array( $this, 'parse_request_action' ) );                                         
        add_filter( 'query_string', array( $this, 'query_string_filter' ) );                                           
        add_action( 'parse_query', array( $this, 'parse_query_action' ) );                                             
        add_filter( 'pre_get_posts', array( $this, 'pre_get_posts_action' ) );                                         
        add_filter( 'posts_search', array( $this, 'posts_search_filter' ), 10, 2 );                                    
        add_filter( 'posts_where', array( $this, 'posts_where_filter' ), 10, 2 );                                      
        add_filter( 'posts_join', array( $this, 'posts_join_filter' ), 10, 2 );                                        
        add_filter( 'posts_clauses', array( $this, 'posts_clauses_filter' ), 10, 2 );                                  
        add_filter( 'posts_request', array( $this, 'posts_request_filter' ), 10, 2 );                                  
        add_filter( 'posts_results', array( $this, 'posts_results_filter' ), 10, 2 );                                  
    }
```

Tous les hooks sont destinés à afficher les données reçues :

```php
function request_filter( $query_vars ){                                                                            
    echo '<h1>request</h1>';                                                                                       
    print_r( $query_vars );                                                                                        
                                                                                                                   
    return $query_vars;                                                                                            
}
```

La nature du plugin n'excuse en aucun cas que les données devraient être proprement échappées avant d'être affichées.

En raison du fonctionnement du plugin qui affiche tout, on peut obtenir un XSS avec un tas de paramètres différents.

PoC :

```
http://localhost:8000/?page_id=%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
```
