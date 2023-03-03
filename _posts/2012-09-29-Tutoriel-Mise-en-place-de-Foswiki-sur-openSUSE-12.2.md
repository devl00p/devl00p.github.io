---
title: "Tutoriel : Mise en place de Foswiki sur openSUSE 12.2"
tags: [tutoriel]
---

## Introduction

Dans le présent article, nous allons voir comment mettre en place le logiciel de wiki [Foswiki](http://foswiki.org/) sur un système Linux [openSUSE](http://www.opensuse.org/fr/) 12.2.  

La version de *Foswiki* utilisée pour ce tutoriel est la 1.1.5. Les éditeurs de *Foswiki* comptent apporter différentes modifications à leur système pour la prochaine version, par conséquence si vous installez une version supérieure à la 1.1.5, référez-vous d'abord aux release notes de la version concernée afin de vous lancer dans ce tutoriel.  

La version d'*openSUSE* utilisée dans cet article est la 12.2 sur un système 32 bits. Le serveur web utilisé est un *Apache 2*.  

## Présentation de Foswiki

*Foswiki* est, comme son nom l'indique, un logiciel collaboratif d'édition d'articles (wiki) qui est libre et open-source (**F**ree and **O**pen **S**ource).  

Il est né d'un fork du système de wiki [TWiki](https://fr.wikipedia.org/wiki/TWiki) avec lequel il est resté compatible.  

Plusieurs particularités de *Foswiki* en font un système intéressant à utiliser : il est gratuit, développé en Perl et Javascript et n'utilise pas de base de données par défaut (même si cela est semble-t-il possible).  

Il dispose d'un système de gestion de versions des articles qui se base sur [GNU RCS](https://fr.wikipedia.org/wiki/GNU_RCS), un système largement éprouvé dont la première version remonte à 1982.  

Il inclut de base différents mécanismes de sécurité dont un wiki peut avoir besoin : gestion de droits avancés par ACL (notion de droits, de groupes et d'utilisateurs), systèmes anti-spam dont les captchas ou l'obfuscation des adresses emails, gestion de blacklist ou notion d'IPs autorisées, protection contre [les attaques CSRF]({% link _posts/2011-01-08-Les-attaques-par-Cross-Site-Request-Forgery.md %})...  

Il permet aussi de régler facilement la visibilité du wiki sur Internet pour empêcher par exemple l'indexation par les moteurs de recherche.  

Il est extensible via de nombreux plugins, dispose d'un outil de recherche performant, un système de compression et de mise en cache des articles, la génération de statistiques et enfin il est multi-langue.  

## Installation des prérequis

Dans le présent article, nous allons procéder à l'installation de *Foswiki 1.1.5* ainsi qu'à l'installation de tous [les logiciels nécessaires à son fonctionnement](http://foswiki.org/System/InstallationGuide#SystemRequirements). Cela inclut l'installation d'*Apache 2*, de *RCS* ainsi que différents modules Perl.  

En fonction du système d'exploitation que vous utilisez, des logiciels déjà présents, etc, vous aurez sans doute à adapter quelque peu les étapes décrites ici.  

Dans le cas d'une installation dite *"minimale serveur"* d'*openSUSE* (sans interface graphique), le [MTA Exim](https://fr.wikipedia.org/wiki/Exim) nécessaire à l'envoi de mails est présent par défaut ce qui n'est peut-être pas le cas sur un système *Debian*.  

Maintenant que vous êtes prêt, ouvrez un shell en tant qu'utilisateur root sur le système et installez les paquets suivants (21Mo au total) avec zypper :

```bash
zypper in apache2 apache2-mod_perl rcs perl-CGI-Session perl-HTML-Parser perl-HTML-Tree perl-URI perl-Digest-SHA1 perl-Authen-SASL gcc make
```

Les paquets gcc et make nous permettent de compiler les modules Perl supplémentaires via CPAN. Lancez ces deux commandes :

```bash
cpan -i Crypt::Eksblowfish::Bcrypt
```

Si vous lancez CPAN pour la première fois, plusieurs questions vous seront posées. Vous pouvez répondre *yes* à toutes les questions.

```bash
cpan -i Crypt::PasswdMD5
```

## Activation d'Apache 2

Maintenant que le serveur web *Apache* est installé, nous allons faire en sorte qu'il soit prêt à accueillir *Foswiki* :

```bash
a2enmod status
a2enmod perl
a2enmod rewrite
systemctl enable apache2.service
systemctl start apache2.service
```

Notez que le module `status` n'est pas nécessaire, mais très pratique pour s'assurer du bon fonctionnement du serveur.  

Ouvrez votre navigateur préféré (ou *w3m* en ligne de commande) à l'adresse <http://127.0.0.1/server-status/> afin de vérifier que le serveur est bien lancé.  

## Déploiement de Foswiki

Placez-vous dans le dossier où vous souhaitez mettre *Foswiki* et téléchargez-y l'archive de *Foswiki* [depuis le site officiel](http://foswiki.org/Download/FoswikiRelease01x01x05).  

Ici nous allons faire en sorte que le répertoire de base de *Foswiki* soit `/srv/www/htdocs/wiki` et qu'il soit accessible par l'url `/wiki`.  

Une fois l'archive téléchargée, décompressez là :

```bash
tar zxvf Foswiki-1.1.5.tgz
mv Foswiki-1.1.5 wiki
cd wiki
```

On récupère ensuite l'extension permettant de faire tourner *Foswiki* avec `mod_perl` (plus performant qu'en CGI).

```bash
wget http://foswiki.org/pub/Extensions/ModPerlEngineContrib/ModPerlEngineContrib.tgz
tar zxvf ModPerlEngineContrib.tgz
```

On rectifie finalement les droits sur *Foswiki* afin que le serveur *Apache* puisse y accéder.

```bash
cd ..
chown -R wwwrun.www wiki
```

## Configuration d'Apache 2

Maintenant nous devons indiquer à *Apache* comment il doit traiter les scripts présents dans *Foswiki*.  

Cela comprend leur exécution par `mod_perl` ainsi que la redirection des URLs via `mod_rewrite`.  

Heureusement pour nous, *Foswiki* a mis en place sur son site [un générateur de configuration d'Apache](http://foswiki.org/Support/ApacheConfigGenerator).  

Rendez-vous sur la page et remplissez le formulaire selon vos besoins.  

**Attention !** Si vous faites une erreur (même petite) dans la configuration, elle peut potentiellement s'avérer difficile à comprendre par la suite donc vérifiez à deux fois et si vous avez un doute référez-vous à la documentation de *Foswiki* ou basez-vous sur ma configuration qui est la suivante :

* Hostname : `opensuse.net`
* URL Path : `/wiki`
* Short URLs enable
* Runtime engine : `mod_perl`
* user names that are allowed to access configure : `admin`
* Login Manager : `TemplateLogin`
* Location of `.htpasswd` file : `/srv/www/htdocs/wiki/data/.htpasswd`
* Page to return when authentication fails : `UserRegistration`

Cochez aussi les deux recommandations anti-spam et cliquez sur *Update config file* pour obtenir votre fichier de configuration.  

Enregistrez-le par exemple sous le nom `foswiki_apache.conf` et placez-le dans `/etc/apache2/vhosts.d` (`a2ensite` n'est plus présent dans *openSUSE 12.2*).

Si vous ne disposez pas de PHP sur votre système, retirez la ligne faisant référence à `php_admin_flag` sous peine d'avoir une erreur au lancement d'*Apache*.

Protéger le script configure
----------------------------

La page */wiki/bin/configure* est le centre vital de *Foswiki* qui sera géré par l'administrateur. Il est important que l'on protège cette page par mot de passe comme on l'a sélectionné dans lors de la génération de la configuration d'Apache.  

Définissez un mot de passe pour le compte *admin* avec cette commande (remplacez *s3cr3t* par le mot de passe de votre choix, choisissez le fort) :

```bash
htpasswd2 -cbm /srv/www/htdocs/wiki/data/.htpasswd admin s3cr3t
```

## Configuration de base de Foswiki

Rendez-vous maintenant à l'adresse <http://127.0.0.1:8080/wiki/>.  

![Foswiki index](/assets/img/foswiki_index.png)

Cliquez sur *Configure Foswiki* et saisissez les identifiants pour notre compte *admin*.  

![Foswiki configure script](/assets/img/foswiki_configure.png)

Vous devrez valider les chemins d'accès aux fichiers que *Foswiki* a devinés pour vous. N'hésitez pas à afficher les options expert ou à vous servir des infos-bulles.  

![Fowiki validate path](/assets/img/foswiki_conf_block.png)

Quand vous avez bien tout vérifié, cochez la case *Change password* (normalement ça se déclenche même décoché la première fois) et cliquez sur *Save changes*.  

Cette étape est primordiale, car elle va permettre de générer le fichier `lib/LocalSite.cfg` qui contient votre configuration *Foswiki* et aussi de créer l'utilisateur *AdminUser* qui correspond au root dans les ACL de *Foswiki*.  

À ce sujet, *Foswiki* dispose d'une fonctionnalité similaire à *sudo* qui permet de s'identifier temporairement comme `AdminUser` si vous êtes connecté avec un autre utilisateur, le temps de réaliser une opération privilégiée.  

La validation de ces paramètres vous amènera à encore d'autres paramètres de configuration avec probablement des erreurs et des avertissements à corriger.  

**Rien de grave !** C'est normal à cette étape de la configuration. Prenez juste soin à remplir les champs demandés par *Foswiki*.  

![Menu de configuration Foswiki](/assets/img/foswiki_conf_etendu.png)

Dans la section *Security and Authentication*, choisissez l'encodage `bcrypt` pour les mots de passe (on a installé le module via CPAN, autant en profiter) et cochez `NeedVerification` sous *Registration*.  

Cela implique que nous configurions l'envoi de mails qui est demandé par *Foswiki*.  

Entrez une adresse email qui servira d'expéditeur pour les mails de vérifications envoyés aux nouveaux inscrits.  

Saisissez aussi les paramètres SMTP (serveur, username, password) correspondant à cette adresse email.  

Sauvez les paramètres. Vous pouvez ensuite retourner dans cette section si vous voulez faire un test d'envoi de mail (un bouton est prévu à cet effet)  

Mettez de côté pour le moment les paramètres de *Tuning* et d'*Internationalisation* : on a plus important à faire pour le moment.

## Patcher Foswiki

La version 1.1.5 de *Foswiki* a [un bug connu](http://www.foswiki.org/Tasks/Item11798) qui nous concerne malheureusement du moment où l'on souhaite utiliser une langue autre que l'anglais.  

Si l'on ne patche pas ce bug, il sera impossible de sauvegarder les articles une fois passé *Foswiki* en français.  

Ouvrez le fichier `lib/Foswiki/UI/Manage.pm`, allez à la ligne 508 et remplacez

```
eq 'Cancel'
```

par

```
ne ''
```

Et idem à la ligne 518, remplacez

```
eq 'Save'
```

par

```
ne ''
```

Sauvegardez le script. Attention le fichier est en lecture seule par défaut.  

On va ensuite rectifier [un autre bug](http://foswiki.org/Tasks/Item12080) qui est dû à un changement dans le langage de programmation Perl.  

Ouvrez le fichier `lib/Foswiki/Search/InfoCache.pm` et faites une recherche sur le mot `length` qui devrait vous amenez vers la ligne 249 qui correspond à cette instruction :

```perl
$this->{count} = length @{ $this->{list} };
```

Remplacez simplement `length` par `scalar` et sauvez le fichier.  

## Bravo

Redémarrez le serveur *Apache* :

```bash
systemctl restart apache2.service
```

Rendez vous sur [/wiki](http://127.0.0.1/wiki/) : Ça y est votre Foswiki est actif :)  

Vous pouvez si vous le souhaiter retourner sur `configure`, section `Internationalisation` et remplacer `en_US.ISO-8859-1` par `fr_FR.ISO-8859-1`.  

En cas d'erreur, vous trouverez des logs dans le dossier `working/logs` de *Foswiki* mais les plus intéressants seront peut-être les logs d'*Apache*.  

Pensez aussi à surveiller les logs d'*Exim*.

*Published September 29 2012 at 11:13*
