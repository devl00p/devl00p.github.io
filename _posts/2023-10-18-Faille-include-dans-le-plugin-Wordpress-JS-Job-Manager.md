---
title: "Faille d'inclusion PHP dans le plugin Wordpress JS Job Manager"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [JS Job Manager](https://wordpress.org/plugins/js-jobs/) (slug: `js-jobs`) se présente de cette façon :

> JS Jobs allows you to run your own, unique jobs classifieds service where you or employer can advertise their jobs, job seekers can upload their resume and apply to any jobs.
>
> No need to setup anything, just click and install it.
> It comes with 250+ configurations and 45 shortcode with full power.
> JS Jobs also have its own login/register pages.
  
La version testée est la 2.0.1 qui date d'il y a 5 mois.

## La vulnérabilité

Dans le script `jsjobs.php` on trouve la classe principale qui se va charger le code des différents modules via une fonction nommée `includes()` :

```php
class jsjobs {                                                                                                         
                                                                                                                       
    public static $_path;                                                                                              
    public static $_pluginpath;                                                                                        
    public static $_data; /* data[0] for list , data[1] for total paginition ,data[2] fieldsorderring , data[3] userfield for form , data[4] for reply , data[5] for ticket history  , data[6] for internal notes  , data[7] for ban email  , data['ticket_attachment'] for attachment */
    public static $_pageid;                                                                                            
    public static $_db;                                                                                                
    public static $_configuration;                                                                                     
    public static $_sorton;                                                                                            
    public static $_sortorder;                                                                                         
    public static $_ordering;                                                                                          
    public static $_sortlinks;                                                                                         
    public static $_msg;                                                                                               
    public static $_error_flag;                                                                                        
    public static $_error_flag_message;                                                                                
    public static $_currentversion;                                                                                    
    public static $_error_flag_message_for;                                                                            
    public static $_error_flag_message_for_link;                                                                       
    public static $_error_flag_message_for_link_text;                                                                  
    public static $_error_flag_message_register_for;                                                                   
    public static $theme_chk;                                                                                          
    public static $_search;                                                                                            
    public static $_captcha;                                                                                           
    public static $_jsjobsession;                                                                                      
                                                                                                                       
    function __construct() {                                                                                           
        self::includes();                                                                                              
        //  self::registeractions();                                                                                   
        self::$_path = plugin_dir_path(__FILE__);                                                                      
        self::$_pluginpath = plugins_url('/', __FILE__);
        --- snip ---
```

L'un des scripts chargés est `includes/shortcodes.php` qui contient une classe `JSJOBSshortcodes` dont les méthodes correspondent à différents panels comme le `Job Seeker` :

```php
function show_jobseeker_controlpanel($raw_args, $content = null) {                                                 
    //default set of parameters for the front end shortcodes                                                       
    ob_start();                                                                                                    
    $defaults = array(                                                                                             
        'jsjobsme' => 'jobseeker',                                                                                 
        'jsjobslt' => 'controlpanel',                                                                              
    );                                                                                                             
    $sanitized_args = shortcode_atts($defaults, $raw_args);                                                        
    if(isset(jsjobs::$_data['sanitized_args']) && !empty(jsjobs::$_data['sanitized_args'])){                       
        jsjobs::$_data['sanitized_args'] += $sanitized_args;                                                       
    }else{                                                                                                         
        jsjobs::$_data['sanitized_args'] = $sanitized_args;                                                        
    }                                                                                                              
    $pageid = get_the_ID();                                                                                        
    jsjobs::setPageID($pageid);                                                                                    
    jsjobs::addStyleSheets();                                                                                      
    $offline = JSJOBSincluder::getJSModel('configuration')->getConfigurationByConfigName('offline');               
    if ($offline == 1) {                                                                                           
        JSJOBSlayout::getSystemOffline();                                                                          
    } elseif (JSJOBSincluder::getObjectClass('user')->isdisabled()) { // handling for the user disabled            
        JSJOBSlayout::getUserDisabledMsg();                                                                        
    } else {                                                                                                       
        $module = JSJOBSrequest::getVar('jsjobsme', null, 'jobseeker');                                            
        $layout = JSJOBSrequest::getLayout('jsjobslt', null, 'controlpanel');                                      
        $jobseekerarray = array('addcoverletter', 'mycoverletters', 'myresumes','myappliedjobs');                  
        $isouruser = JSJOBSincluder::getObjectClass('user')->isJSJobsUser();                                       
        $isguest = JSJOBSincluder::getObjectClass('user')->isguest();                                              
        if (in_array($layout, $jobseekerarray) && $isouruser == false && $isguest == false) {                      
            JSJOBSincluder::include_file('newinjsjobs', 'common');                                                 
        } else {                                                                                                   
        echo "hi there<br />\n";                                                                                   
            JSJOBSincluder::include_file($module);                                                                 
        }                                                                                                          
    }                                                                                                              
    unset(jsjobs::$_data['sanitized_args']);                                                                       
    $content .= ob_get_clean();                                                                                    
    return $content;                                                                                               
}
```

La fonction `JSJOBSrequest::getVar` permet de récupérer une variable passée dans l'URL.

Ici la valeur du paramètre `jsjobsme` est utilisée pour remplir la variable `$module`. On a ensuite une inclusion déclenchée via l'instruction suivante :

```php
JSJOBSincluder::include_file($module);
```

La fonction include_file est déclarée dans `includes/includer.php` :

```php
public static function include_file($filename, $module_name = null) {                                              
    if ($module_name != null) {                                                                                    
        if (file_exists(JSJOBS_PLUGIN_PATH . 'modules/' . $module_name . '/tmpl/' . $filename . '.inc.php')) {     
            require_once(JSJOBS_PLUGIN_PATH . 'modules/' . $module_name . '/tmpl/' . $filename . '.inc.php');      
        }                                                                                                          
        if (locate_template('js-jobs/' . $module_name . '-' . $filename . '.php', 1, 1)) {                         
            return;                                                                                                
        // } elseif (locate_template($module_name . '-' . $filename . '.php', 1, 1)) { // to add layout in root template directory
        //     return;                                                                                             
        } else {                                                                                                   
            include_once JSJOBS_PLUGIN_PATH . 'modules/' . $module_name . '/tmpl/' . $filename . '.php';           
        }                                                                                                          
    } else {                                                                                                       
        include_once JSJOBS_PLUGIN_PATH . 'modules/' . $filename . '/controller.php';                              
    }                                                                                                              
    return;                                                                                                        
}
```

Dans notre cas `$module_name` n'est pas défini et prend la valeur par défaut (`null`).

Nous nous retrouvons donc dans le dernier cas d'inclusion.

En raison des contraintes de préfixe et de suffixe, il faut pour exploiter la vulnérabilité être en mesure de placer un script `controller.php` à un endroit que le serveur web est capable d'inclure.

PoC si on est en mesure de créer le fichier dans `/tmp` :

```
http://localhost:8000/?page_id=10&jsjobsme=../../../../../../../../../../tmp
```

L'ID de la page vulnérable doit être celle correspondant à _JS Jobs_ (un lien `Jobseeker` doit être présent dans la page).
