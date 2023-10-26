---
title: "Faille d'injection SQL dans le plugin Wordpress Loginplus"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Loginplus](https://wordpress.org/plugins/loginplus) se présente de cette façon :

> Login plus changes WordPress Login Logo and Logo Url without altering any core file. See Login Logs like Hacking attempt,Failed login, successfull login with tons of info.

La version testée est la 1.2 et date d'il y a 10 mois au moment de ces lignes.

## La vulnérabilité

Le script `loginplus.php` du plugin définit, parmi d'autres, un hook pour la fonction `wp_login_failed` :

```php
//failed login attemp                                                                                                  
add_action( 'wp_login_failed', 'login_plus_splogin_failed' );                                                          
function login_plus_splogin_failed($username) {                                                                        
    global $wpdb;                                                                                                      
                                                                                                                       
    if(wp_get_referer())                                                                                               
      $refUrl=wp_get_referer();                                                                                        
    else                                                                                                               
      $refUrl='NA';                                                                                                    
                                                                                                                       
    $allUser=get_users();                                                                                              
    $allu=array();                                                                                                     
        foreach($allUser  as $auser){                                                                                  
            $allu[]=$auser->user_login;                                                                                
                                                                                                                       
        }                                                                                                              
    if(in_array($username, $allu)){                                                                                    
        $visitType= 'Failed Login';                                                                                    
    }else{                                                                                                             
        $visitType= 'Hacking Attempt';                                                                                 
    }                                                                                                                  
                                                                                                                       
    $sys=new LoginPlusSystem();                                                                                        
    $uagent=$_SERVER ['HTTP_USER_AGENT'];                                                                              
    $ipaddr= $_SERVER['REMOTE_ADDR'];                                                                                  
                                                                                                                       
    $browser=$sys->getBrowser($uagent)." ".$sys->broV($uagent);                                                        
    $visitoros=$sys->getOS($uagent);                                                                                   
    $today=date("Y-m-d");                                                                                              
    $failedlog = "insert into " . $wpdb->prefix . "sp_login_details                                                    
    (username,uagent,ipaddr,browser,visitoros,visitdate,queryType,refUrl,visitType)                                    
    values('$username','$uagent','$ipaddr','$browser','$visitoros','$today','failedLogin','$refUrl','$visitType')";    
    $wpdb->query($failedlog);                                                                                          
                                                                                                                       
    //error_log("user $username: authentication failure for \"".admin_url()."\": Password Mismatch");                  
}
```

La fonction est vulnérable à une faille d'injection SQL, car le nom d'utilisateur (variable `$username`) est utilisé tel quel dans la requête SQL `INSERT`.

Il en va de même avec le User-Agent (variable `$uagent`). 

Wordpress n'affichant pas les erreurs par défaut il est tout de même possible de réaliser une exploitation de la vulnérabilité en mode time-based via l'emploi de la fonction `SLEEP` (dans le cas de MySQL).

Pour augmenter ses chances d'exploitation, il faut privilégier l'injection dans le nom d'utilisateur, car des opérations sont effectuées sur le User-Agent afin de récupérer le nom du navigateur et la version.

Il y a même un bug qui touche l'extraction de la version, il est donc préférable de spécifier un User-Agent court du genre `Mozilla`.

L'exploitation est possible avec `sqlmap`.

PoC :

```bash
python sqlmap.py -u http://localhost:8000/wp-login.php --data "log=yolo&pwd=ddd&wp-submit=Log+In&redirect_to=http%3A%2F%2Flocalhost%3A8000%2Fwp-admin%2F&testcookie=1" -A "Mozilla" --dbms mysql --risk 3 --level 5
```
