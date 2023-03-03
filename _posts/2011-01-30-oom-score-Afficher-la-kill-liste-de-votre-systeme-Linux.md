---
title: "oom_score : Afficher la 'kill' liste de votre système Linux"
tags: [AdminSys, Coding]
---

Bien que les plantages soient peu fréquents sous Linux, ils existent comme sur tout autre système d'exploitation.  

Toutefois, on a plus souvent affaire à une montée en charge du système qu'à un Kernel Panic (l'équivalent des BSOD Windows).  

Au moment où le problème survient, il est souvent trop tard pour pouvoir agir sur le système : un processus _fou_ a englouti toute la RAM et seul le bruit du disque dur nous indique qu'il s'attaque à la SWAP.  

Pour prévenir ce genre de problème, il existe des *soupapes de sécurité* dont le rôle et de terminer les processus à l'origine de ces problèmes.  

L'environnement graphique KDE inclut un outil baptisé `kwin_killer_helper` pour cette tache. Malheureusement il s'avère très peu efficace et d'aucune façon configurable.  

Au niveau du kernel Linux lui-même on trouve un code baptisé [oom_kill](http://oomkill.net/) (oom = *Out of memory*) qui se charge effectivement de terminer un ou des processus... à condition d'attendre suffisamment longtemps.  

En effet, le code de `oom_kill` se montre peu efficace pour déterminer quel est le coupable et va souvent tuer le processus voisin qui n'avait rien demandé.  

À titre d'exemple, il va finir par fermer KDE (et donc la totalité des applications graphiques) alors qu'il aurait pu suffire de terminer le processus qui gère le plugin Flash dans le navigateur.  

L'algorithme utilisé pour la détection de mauvais processus a toutefois était corrigé [avec le noyau 2.3.36](http://linuxfr.org/2010/10/21/27463.html).  

Quand un système plante à répétition et que `oom_kill` fait des apparitions fréquentes dans les logs, la seule vraie solution consiste à rajouter de la RAM sur le PC.  

L'avantage de `oom_kill` (en dehors du fait qu'il agit au niveau du kernel) est qu'il est configurable : chaque processus dans `/proc/[pid]` a des fichiers `oom_adjl` et `oom_score` qui permettent de savoir si un processus est dans le collimateur du kernel ou de l'y placer volontairement.  

La page de manuel de *proc(5)* nous informe de différents points intéressants :  

* `oom_adjl` contient une valeur numérique située entre `-17` et `15`. Plus la valeur est grande (et positive) plus le processus a des chances d'être candidat à un "suicide" décidé par le kernel.
* On peut jouer sur cette valeur, par exemple en faisant un `echo -5 > /proc/[pid]/oom_adj`
* `oom_score` contient une valeur numérique bien plus grande qui est calculée à partir de différents éléments comme l'utilisation CPU du processus, sa priorité, s'il tourne avec des privilèges, etc. Le résultat est ensuite décalé à l'aide de la valeur `oom_adjl` (bit shift). Cette opération est définie par la fonction [badness](http://oomkill.net/)
* la valeur `-17` dans `oom_adjl` est particulière et permet de marquer le processus comme indestructible
* Tout ce mécanisme peut être activé ou désactivé par `/proc/sys/vm/panic_on_oom`. Si ce fichier contient "1" alors le système fait un kernel panic en cas de débordement de mémoire. S'il est à 0, `oom-killer` est appelé à la rescousse.

Pour afficher la liste des processus par ordre croissant de risque de se faire tuer, j'ai créé un script python : [oom_score.py](/assets/data/oom_score.py)  

Il donne un résultat de ce style :  

```
oom_score pid   process name                   oom_adj                              
        0  3593 /sbin/auditd -s disable            -17                              
        0   665 /sbin/udevd --daemon               -17                              
       13  2610 /sbin/acpid                          0                              
       15  3622 /usr/sbin/avahi-dnsconfd -D          0
...
    34560  5187 /usr/bin/krunner                     0
    83495  5108 kdeinit4: kdeinit4 Running...        0
    90882     1 init [5]                             0
   103294  5614 /bin/sh /usr/bin/firefox             0
```

Dans cet exemple, on peut voir que le navigateur Firefox sera le premier à éjecter en cas de manque de mémoire sur le système.

*Published January 30 2011 at 17:44*
