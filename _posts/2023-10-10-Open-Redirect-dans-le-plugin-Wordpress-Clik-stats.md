---
title: "Open Redirect dans le plugin Wordpress Clik stats"
tags: [vulnérabilité]
---

## Présentation du plugin

Voici la description officielle :

> clikStats is a plugin that automatically detects the current links within each post.

> ClikStats is retrofitable, and requires no special provision from any classes or code.

> Once activated, clikStats will compile who, when, what data which can be viewed through the back office.

> The beauty of this plugin is in its portability, it can be used straight out of the box, and provide usefull visitor information, without the need to reverse engineer your posts.

>The latest version now supports, multiple quotation types, invalid markup, uppercase/lowercase markup and hash tags

Ce plugin a été testé en version 0.8. Il date d'il y a 9 ans.

## La vulnérabilité

La vulnérabilité est tout bête : le script `clikstats/ck.php` récupère une URL via le paramètre `Ck_lnk`, fait quelques opérations dessus et à la fin effectue une redirection vers l'URL sans avertir l'utilisateur :

```php
// reassemble the url (reserved querys must be removed from the url assembly)                                          
$urlA = $_GET['Ck_lnk'];                                                                                               
foreach ($_GET as $key=>$val) $urlA.= !in_array($key, $reserved, true)  ? '&'.$key.'='.$val : '';

--- snip ---

// send them to where they originally requested                                                                        
header('Location: '.$urlA);
```

PoC :

```
http://localhost:8000/wp-content/plugins/clikstats/ck.php?Ck_id=2&Ck_lnk=https%3A%2F%2Fopenbugbounty.org%2F
```
