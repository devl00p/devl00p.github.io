---
title: "Les Questions Cons du Hacking : Peut-on prendre la main à distance avec RDP sans se faire remarquer ?"
tags: [Windows]
---

S01E01 : Peut-on prendre la main à distance avec RDP sans se faire remarquer ?
------------------------------------------------------------------------------

### Introduction

Cet article est l'occasion de commencer un nouveau concept de format d'articles, plus court, mais pas moins intéressant sur les questions (pas si connes) que l'on peut se poser autour du thème de la sécurité informatique.  

Ce format est bien sûr inspiré des [Questions Cons](https://www.youtube.com/playlist?list=PLgCwST0qDUDQ_wxI8fzfFBIumGa3t_S3U) par *Le Tatou* sur *Youtube*.  

On entame ici avec le [Remote Desktop Protocol](https://fr.wikipedia.org/wiki/Remote_Desktop_Protocol) de *Windows* avec pour objectif savoir si on peut se connecter sans se faire remarquer.  

Déjà, pourquoi vouloir prendre la main à distance ?  

Haha [Jean-Pierre](https://www.youtube.com/channel/UC9pVaOtZ8vdLBrlHu5xaaOA), I'm glad you fucking ask !  

You have to use RDP for three reasons :  

* Première raison, la présence du service Bureau à distance sur une bonne partie des versions de Windows fait que le choix s'impose presque.
* Deuxième raison, Windows est un système qui exploite très largement son interface graphique, délaissant même pour des opérations d'administration la possibilité d'effectuer une opération en ligne de commande (même si *PowerShell* apporte désormais de nombreuses possibilités).
* Troisième raison, pour certains programmes tiers l'accès à l'interface graphique sera la solution la plus rapide et la plus efficace pour obtenir des informations. L'accès à l'interface est aussi parfois la seule et unique façon de désactiver un mécanisme de sécurité (certains antivirus empêchent la désactivation de leur service par ligne de commande et le processus est protégé même si vous tenter de le tuer avec les droits SYSTEM alors que quelques clics dans l'interface permettent de s'en débarrasser).

Qu'est-ce que ça veut dire *"sans se faire remarquer"* ?  

Par *"sans se faire remarquer"* je veux dire que l'utilisateur courant (qui dispose d'un accès physique ou distant) de la machine ciblée ne verra pas apparaître une fenêtre, un message ou une notification quelconque lors de votre connexion.  

Je ne traiterai pas dans cet article des événements ajoutés aux logs de Windows et des logiciels de sécurité qui pourrait remonter l'information de connexion à un administrateur.  

### Environnement de test

Mon environnement de test se compose ici de :  

* Un _Windows 7 Entreprise_ disposant de deux comptes administrateurs (`IEUser` et `hax0r`). Il s'agit d'une image virtuelle fournit par Microsoft pour tester ses navigateurs (ce qui explique le nom de l'utilisateur `IEUser`)
* Un _Windows Server 2012 R2_ disposant de deux comptes administrateurs (`Administrateur` et `hax0r`).

Commençons d'abord par tester le comportement de Windows 7 face à différents cas.  

### Windows 7

**Premier cas :** l'utilisateur `IEUser` est connecté physiquement, une connexion distante est établie avec le même utilisateur.  

**Réaction :** L'utilisateur `IEUser` logué physiquement se retrouve déconnecté (il retourne à la mire de session et voit *"Logged on"* indiqué sous son image de profil).  

![Windows 7 RDP user already connected](/assets/img/rdp/win7_cas1.png)

De son côté, l'utilisateur en RDP reprend le contexte de la session de l'utilisateur (fenêtres qui étaient ouvertes, documents en cours...)  

Si l'utilisateur physique reprend la session, il reprend le contexte et l'utilisateur RDP est quant à lui déconnecté.  

**Second cas :** L'utilisateur `IEUser` est connecté physiquement, `hax0r` établie une connexion RDP.  

**Réaction :** L'utilisateur distant (`hax0r`) se voit demander s'il veut déconnecter l'utilisateur courant, nécessaire pour qu'il puisse prendre la main.  

![RDP asking for logged user session termination](/assets/img/rdp/win7_cas2_1.png)

L'utilisateur courant (`IEUser`) peut décliner la connexion de l'utilisateur (au passage, il voit le nom d'utilisateur à l'origine de la demande).  

![RDP ask confirmation for another user session termination](/assets/img/rdp/win7_cas2_2.png)

**Troisième cas :** Aucun utilisateur n'est préalablement connecté au système, `hax0r` ouvre alors une session distance puis `IEUser` se connecte physiquement.  

**Réaction :** c'est la même situation que le cas 2 en inverse.  

![RDP asking for session termination](/assets/img/rdp/win7_cas3.png)

**Quatrième cas :** `IEUser` est connecté en RDP. `hax0r` se connecte alors en RDP.  

**Réaction :** idem cas 2  

**Cinquième cas :** `IEUser` est connecté en RDP. Une autre personne se connecte avec `IEUser` en rdp.
**Réaction :** Idem au cas 1 avec fermeture de la première session RDP.  

**Conclusion :** c'est impossible de prendre la main sans risquer de se faire remarquer.  

[La raison est toute simple](https://social.technet.microsoft.com/Forums/windows/en-US/655ed2a6-e9fc-486c-bcbe-02fe3f59c206/multiple-rdp-sessions-for-windows-7) : la fonctionnalité de sessions concurrentes est mise en avant par les versions Server de Windows (_Windows 7_, c'est [pas assez cher mon fils](https://www.youtube.com/watch?v=MDo9BY72AU4) :D).  

Il existe toutefois des patchs (des cracks) comme *Concurrent Session Enabler* ou *Universal TermSrv Patch* qui permettent de débloquer le nombre d'utilisateurs différents pouvant se connecter en même temps via RDP.  

En dehors du fait que ces solutions ne sont certainement pas légales, il faut être conscient que leur développement n'est pas forcément suivi, que le patch n'est pas forcément stable et qu'il ne couvre pas forcément toutes les versions de Windows (en l’occurrence avec _Windows 7 Enterprise_ ça n'a pas l'air de fonctionner).  

Casser le service RDP d'une machine ce n'est pas ce que l'on peut faire de mieux quand on veut passer inaperçu :D  

**Une solution alternative** pour les Windows 9x (lol), XP, 7 et autres versions ne disposant pas de la fonctionnalité, c'est d'installer un *TightVNC* "furtif".  

*TightVNC* propose un installeur MSI avec [différentes options de déploiement [lien pdf]](http://www.tightvnc.com/doc/win/TightVNC_2.7_for_Windows_Installing_from_MSI_Packages.pdf) permettant d'avoir un bon niveau de discrétion.  

Je donne ci-dessous la ligne de commande pour l'installation du MSI (sur plusieurs lignes pour une meilleure lisibilité).  

Les noms de la plupart des options parlent d'eux-mêmes : On installe en silencieux le service VNC sans le client, on ne redémarre pas le système après l'installation, on ajoute l'exception au firewall Windows, on désactive les logs de l'application, on désactive la présence de l'icône de systray, on empêche la suppression du wallpaper lors des connexions et enfin on définit les différents mots de passe de connexion :)   

```
msiexec /i tightvnc-2.8.8-gpl-setup-32bit.msi
/quiet /norestart
ADDLOCAL=Server
SERVER_REGISTER_AS_SERVICE=1
SERVER_ADD_FIREWALL_EXCEPTION=1
SERVER_ALLOW_SAS=1 

SET_LOGLEVEL=1
VALUE_OF_LOGLEVEL=0

SET_RUNCONTROLINTERFACE=1
VALUE_OF_RUNCONTROLINTERFACE=0

SET_REMOVEWALLPAPER=1
VALUE_OF_REMOVEWALLPAPER=0

SET_USEVNCAUTHENTICATION=1
VALUE_OF_USEVNCAUTHENTICATION=1
SET_PASSWORD=1
VALUE_OF_PASSWORD=mainpass
SET_VIEWONLYPASSWORD=1
VALUE_OF_VIEWONLYPASSWORD=viewpass
SET_USECONTROLAUTHENTICATION=1
VALUE_OF_USECONTROLAUTHENTICATION=1
SET_CONTROLPASSWORD=1
VALUE_OF_CONTROLPASSWORD=admpass
```

Après cette étape, il restera toutefois à supprimer les entrées correspondantes dans le(s) menu Démarrer de l'utilisateur(s).  

### Windows Server

Maintenant voyons comment se comporte **Windows Server 2012 R02** en configuration par défaut. Je rappelle que pour cet exemple les utilisateurs sont `Administrateur` et `hax0r`.  

**Cas 1 :** idem à _Windows 7_  

**Cas 2 :** les sessions de `Administrateur` et `hax0r` cohabitent  

**Cas 3 :** idem au cas précédent  

**Cas 4 :** les deux sessions cohabitent  

**Cas 5 :** comportement similaire à _Windows 7_  

On voit ici qu'un même utilisateur ne peut pas être connecté physiquement ET en RDP. En revanche des utilisateurs différents peuvent avoir des sessions en même temps !  

C'est bien le fonctionnement de _Windows Server_ par défaut qui rentre en jeu.  

On en apprend plus sur les limitations en se rendant dans `gpedit.msc` sous *Configuration ordinateur > Modèles d'administration > Composants Windows > Services Bureau à distance > Hôte de la session Bureau à distance > Connexions*.  

![gpedit rdp host management](/assets/img/rdp/gpedit.png)

Le paramètre *"Limiter le nombre de connexions"* dispose du commentaire suivant :  

> Spécifie si les services Bureau à distance limitent le nombre de connexions simultanées au serveur.  
>
> Vous pouvez utiliser ce paramètre pour limiter le nombre de sessions des services Bureau à distance qui peuvent être actives sur un serveur. Si ce nombre est dépassé, les utilisateurs supplémentaires qui tentent de se connecter reçoivent un message d'erreur leur indiquant que le serveur est occupé et de réessayer plus tard. La limitation du nombre de sessions améliore les performances, car un nombre moins élevé de sessions nécessite moins de ressources système. Par défaut, les serveurs Hôte de la session Bureau à distance autorisent un nombre illimité de sessions de services Bureau à distance, et le Bureau à distance pour administration autorise deux sessions de services Bureau à distance.  
> 
> Pour utiliser ce paramètre, entrez le nombre maximal de connexions que vous souhaitez spécifier pour le serveur. Pour spécifier un nombre illimité de connexions, tapez 999999.  
> 
> Si vous activez ce paramètre, le nombre maximal de connexions est limité au nombre spécifié cohérent avec la version de Windows et le mode des services Bureau à distance qui s'exécutent sur le serveur.  
> 
> Si vous désactivez ce paramètre ou ne le configurez pas, les limites du nombre de connexions ne sont pas appliquées au niveau de la stratégie de groupe.

Comment **permettre à un utilisateur d'ouvrir plusieurs sessions simultanées** sur la même machine ? Il y a une clé de registre pour ça !  

Il faut aller dans `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\TerminalServer` et passer la valeur DWORD `fSingleSessionPerUser` à 0.  

La réaction du **cas 1** est alors modifiée : `Administrateur` physique reste connecté, `Administrateur` distant obtient sa propre session, les deux sessions cohabitent.  

En cas d'une session RDP supplémentaire de `Administrateur` (donc une troisième session) on peut observer la limitation décrite plus tôt avec une demande de choisir la fermeture d'une des deux sessions existantes.  
![Windows Server two RDP sessions max for administration](/assets/img/rdp/win2012_two_admin_limit.png)

### Conclusion

Il est tout à fait possible de prendre la main avec RDP sous _Windows Server_ sans se faire remarquer par l'utilisateur courant.  

Il faudra préalablement soit créer un nouvel utilisateur, soit utiliser un utilisateur qui a peu de chances d'être utilisé, soit utiliser un compte administrateur en ayant modifié la valeur en registre.  

Pour les éditions non Server on préférera installer un *TightVNC* silencieusement.  

Pour toutes les versions de Windows on peut aussi se tourner vers les modules/payloads VNC de *Metasploit*.  

On privilégiera l'utilisation du module de post-exploitation `post/windows/manage/payload_inject` avec un payload comme `windows/vncinject/reverse_tcp` (par exemple) ce qui permettra de ne pas déposer un exécutable sur le disque (le code est injecté dans un processus existant) et donc d'éviter de se faire détecter par un antivirus.  

Le payload dispose d'une option `ViewOnly` qui permet de choisir si on veut interagir ave l'interface ou seulement regarder ce qui se passe.

*Published June 23 2017 at 20:19*
