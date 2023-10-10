---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress 'Clickbank WordPress Plugin (Storefront)'"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [Clickbank WordPress Plugin (Storefront)](https://wordpress.org/plugins/clickbank-storefront/) (slug: `clickbank-storefront`) se présente de cette façon :

> Clickbank® is the World’s Largest Digital Info Product Store. As a Clickbank affiliate, one can make tons of CASH by promoting these products.

> Using this plugin, you can host more than 10,000 clickbank products on your website as a wordpress plugin with just few clicks.
 
Il semble qu'à défaut d'obtenir une tonne de cash, vous allez surtout avoir droit à une tonne de XSS.

La version testée est la 1.7 qui date d'il y a 3 mois.

## La vulnérabilité

Le script principal `clickbank-storefronts.php` exécute une fonction à l'initialisation :

```php
add_action("init", 'cs_sql_inject_check');
```

Cette fonction est déclarée dans `functions.inc.php` :

```php
function cs_sql_inject_check()
{
   //$cs_error_info = cs_sql_inject_check_detail($_GET['page'],"int",3,'page');
   $cs_error_info = cs_sql_inject_check_detail($_GET['user_id'],"int",10,'user_id');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_mcat'],"int",5,'cs_mcat');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_scat'],"int",5,'cs_scat');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_category'],"int",3,'cs_category');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_temp_main_category'],"int",3,'cs_temp_main_category');        
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_main_category'],"int",3,'cs_main_category');                  
   $cs_error_info = cs_sql_inject_check_detail($_GET['memnumber'],"int",10,'memnumber');

   $cs_error_info = cs_sql_inject_check_detail($_GET['switch_view'],"text",4,'switch_view');
   $cs_error_info = cs_sql_inject_check_detail($_GET['sortby'],"text",30,'sortby');

   //$cs_error_info = cs_sql_inject_check_detail($_GET['niche'],"text",1,'niche');

   $cs_error_info = cs_sql_inject_check_detail($_GET['tar'],"text",100,'tar');
   //$cs_error_info = cs_sql_inject_check_detail($_GET['section'],"text",15,'section');

   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_main_category_name'],"text",100    ,'cs_main_category_name');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_mcat_name'],"text",100,'cs_mcat_name');
   $cs_error_info = cs_sql_inject_check_detail($_GET['mem'],"text",150,'mem');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_review_id'],"text",100,'cs_review_id');
   $cs_error_info = cs_sql_inject_check_detail($_GET['criteria'],"text",30,'criteria');
   $cs_error_info = cs_sql_inject_check_detail($_GET['cs_keywords'],"text",30,'cs_keywords');
}
```

La fonction `cs_sql_inject_check_detail` est utilisée pour vérifier qu'un paramètre suit bien certaines règles de type et de longueur.

Le problème, c'est que quand ce n'est pas le cas, le paramètre est affiché sans vérification dans la page : 


```php
function cs_sql_inject_check_detail($cs_input,$cs_input_type,$cs_max_length,$cs_query_string)
{
     if (   ($cs_input_type==="int")  && (strlen($cs_input)>0)  )  {
        if (    (is_numeric($cs_input)) && ( strlen($cs_input) <= $cs_max_length )     ){}
        else { echo 'Error_code: ['.$cs_query_string.']['.$cs_input."][numeric_mx$cs_max_length]<br \>\n"; wp_die(); }
     }

     if (   ($cs_input_type==="text") && (strlen($cs_input)>0)  ){

        if (    ( strlen($cs_input) <= $cs_max_length )        ){}
        else { echo 'Error_code: ['.$cs_query_string.']['.$cs_input."][text_mx$cs_max_length] <br \>\n"; wp_die(); }
     }
}
```

Le plugin est donc vulnérable à des Cross-Site Scripting sur de nombreux paramètres.

PoC:

```
http://localhost:8000/?memnumber=%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E
```
