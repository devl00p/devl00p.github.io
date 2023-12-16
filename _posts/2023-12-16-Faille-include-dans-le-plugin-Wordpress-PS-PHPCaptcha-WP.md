---
title: "Faille d'inclusion dans le plugin Wordpress PS PHPCaptcha WP"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [PS PHPCaptcha WP](https://wordpress.org/plugins/ps-phpcaptcha/) se présente de cette façon :

> If you are keen to provide your users kind of a tracking free environment, you would have to remove
Google Recaptcha and other cloud based Captcha solutions from your WordPress installation.
>
> PS PHPCaptcha WP does not use any remote resources. This makes it fully GDPR compliant without any need to mention it
in your privacy policy.
>
> To generate the image this plugin does not need to use the WordPress database and therefore IO of the database is very low.
> This very important if you run a site with high traffic.

La version testée est la 1.2.0 qui date d'il y a 5 mois au moment de ces lignes.

## La vulnérabilité

Dans le script `public/renderimage.php` on trouve une classe nommée `renderimage` pour laquelle une instance est créée à la fin du script :

```php
$image = new renderimage();
```

Le constructeur de cette classe récupère un paramètre via GET :

```php
public function __construct() {
    session_start();                                                                                               
    $blogId = '';
    
    if(isset($_GET['blogid']) && !empty($_GET['blogid'])) {
        $blogId = $_GET['blogid'];
    }

    $preset = Psphpcaptchawp_Public::getConfig($blogId);
    $phrase = $this->getRandomString($preset);
    $this->setSession($phrase);
    $this->renderImage($preset, $phrase);
}
```

On peut voir que la variable `$blogId` est passée à la fonction `getConfig` de la classe `Psphpcaptchawp_Public` définie dans `public/class-psphpcaptchawp-public.php` :

```php
public static function getConfig($blogId = '') {
    $preset = Psphpcaptchawp_Admin::getPresets();                                                                  
    $preset['strictlowercase'] = ($preset['strictlowercase'] == 1) ? true:false;

    if(file_exists(__DIR__ . "/../config".$blogId.".php")) {
        require_once __DIR__ . "/../config".$blogId.".php";
```

On voit clairement ici qu'il y a une faille d'inclusion via l'utilisation de `require_once`.

L'exploitation est rendue difficile par le fait que le script définit à la fois un préfixe et un suffixe, ce qui est la pire des conditions.

Toutefois, dans certaines situations (hébergement mutualisé) on peut imaginer des scénarios d'exploitation.
