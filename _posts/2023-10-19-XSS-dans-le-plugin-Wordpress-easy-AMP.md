---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress easy AMP"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [easy AMP](https://wordpress.org/plugins/wp-amp-it-up) (slug: `wp-amp-it-up`) se présente de cette façon :

> The WordPress AMP Plugin for WP – easy AMP create a Google-compliant AMP version of your webpages for free and without any prior knowledge and enable AMP on your WordPress ite! – Just install the AMP plugin, activate it and you’re done!

La version testée est la 4.0 et date d'il y a 9 mois au moment de ces lignes.

## La vulnérabilité

Tout le code se concentre dans le fichier `wp-amp-it-up.php`.

Inutile donc d'aller plus loin.

À la fin du fichier, différentes actions sont enregistrées :

```php
    add_action( 'plugins_loaded', 'amp_cloud_plugin_preview', 0 );                                                     
    add_action( 'wp_head', 'amp_cloud_insert_linkreltag', 1 );                                                         
    add_action( 'wp_head', 'amp_cloud_insert_verifitag', 2 );                                                          
    add_action( 'wp_loaded', 'amp_cloud_check_adstxt', 9999 )
```

La fonction `amp_cloud_insert_linkreltag` est celle qui est vulnérable :

```php
function amp_cloud_insert_linkreltag()                                                                         
{                                                                                                              
    if (is_single())                                                                                            
    {                                                                                                          
        // AMP-Cloud AMP-HTML-Adresse -------------------------------------------                              
        $amp_url    = "".amp_cloud_add_query_amp(amp_cloud_get_urlaktuell())."";                           
        echo "<link rel=\"amphtml\" href=\"".$amp_url."\" />";                                             
    }                                                                                                          
}
```

Son objectif est juste de rajouter un entête HTML `link rel`. La valeur est déterminée depuis l'URL courante passée à
la moulinette de la fonction suivante :

```php
function amp_cloud_get_urlaktuell()
{
    if (!empty($_SERVER["QUERY_STRING"])) {
        $urlquery = "?".amp_cloud_sortQUERY_KD($_SERVER["QUERY_STRING"])."";
    } else {
        $urlquery = "".amp_cloud_sortQUERY_KD($_SERVER["QUERY_STRING"])."";
    }

    $urlaktuell = "".amp_cloud_get_urlaktuellos().$urlquery."";
    return  trim("".$urlaktuell."");
}
```

L'énigmatique fonction `amp_cloud_sortQUERY_KD` correspond au code suivant :

```php
function amp_cloud_sortQUERY_KD($queryIST)
{
    if (!empty($queryIST)) {
        // Query splitten
        parse_str($queryIST, $output_ist);

        // Leere Parameter entfernen
        $output_ist = array_filter($output_ist);
        $output_ist = array_merge($output_ist);

        // Doppelte Parameter entfernen
        array_unique($output_ist);

        // Query sortieren
        ksort($output_ist);

        // Query-Ausgabe setzen
        $queryNEU       = http_build_query($output_ist);
    } else {
        $queryNEU = "".$queryIST."";
    }

    // Rückgabe
    return "".$queryNEU."" ;
}
```

L'objectif semble être uniquement de réorganiser les paramètres dans la query string et d'éviter les doublons.

En aucun cas le contenu de cette query string n'est échappé, permettant alors une injection de code HTML/JS.

PoC :

`http://localhost:8000/?p=1&yolo=%22%3E%3CScRiPt%3Ealert%28%27XSS%27%29%3C%2FsCrIpT%3E`

Notez que ce plugin n'est qu'une copie du plugin [AMP+]({% link _posts/2023-09-11-XSS-dans-le-plugin-Wordpress-AMP-Plus.md %}) : même auteur, même fonctionnalités, même vulnérabilité.
