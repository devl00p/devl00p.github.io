---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Tm – WordPress Redirection"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Tm – WordPress Redirection](https://wordpress.org/plugins/tm-wordpress-redirection/) se présente de cette façon :

> Redirect link from another web with rel = nofollow like vBulletin or normal redirect.
>
> Just activate and settings…..

La version testée est la 1.2 et date d'il y a 13 ans au moment de ces lignes.

## La vulnérabilité

La vulnérabilité est toute simple. On a le script `l.php` suivant :

```php
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">          
<html xmlns="http://www.w3.org/1999/xhtml">                                                                            
    <head>                                                                                                             
        <?php                                                                                                                                                                                                                                                                                  
            $rootdirectory = dirname ( dirname (dirname (dirname (__FILE__))));                                        
            require_once( $rootdirectory . "/wp-config.php" );                                                         
            require_once( $rootdirectory . "/wp-includes/wp-db.php" );                                                 
                                                                                                                       
            $url=$_SERVER['QUERY_STRING'];                                                                             
            if($url)                                                                                                   
            {                                                                                                          
                $url = urldecode($url);                                                                                
            }                                                                                                          
        ?>
--- snip ---
    <body>                                                                                                             
                                                                                                                       
        <div id="warning">                                                                                             
            <p>Bạn đã nhấn vào một liên kết không thuộc <?php echo get_option("blogname"); ?></p>                      
            <p>Liên kết sẽ được chuyển tới:<br />                                                                      
                <b><?php echo $url; ?></b></p>                                                                         
            <p><a rel="nofollow" href="<?php echo $url; ?>">[Tôi đồng ý chuyển tới liên kết đã nhấn]</a>&nbsp;&nbsp;<a id="comeback" href=''>[Tôi không đồng ý, hãy đóng cửa sổ này lại]</a></p>
        </div>                                                                                                         
    </body>                                                                                                            
</html>
```

On peut voir que la query string (ce qui suit le caractère `?` dans l'URL) est url-décodé pour remplir la variable `$url`.

Cette variable est plus loin affichée directement sans échappement préalable.

Le PoC consiste à simplement passer le code HTML dans la query string :

```
http://localhost:8000/wp-content/plugins/tm-wordpress-redirection/l.php?%3Cscript%3Ealert(%27XSS%27)%3C/script%3E
```
