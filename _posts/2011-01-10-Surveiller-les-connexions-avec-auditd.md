---
title: "Surveiller les connexions avec auditd"
tags: [BlueTeam]
---

`auditd` est un démon qui permet de surveiller ce qu'il se passe au niveau du noyau Linux 2.6.  

Une fois activé il se met en écoute de nouvelles règles de surveillance et enregistre dans un fichier de journalisation (`/var/log/audit/audit.log`) tous les événements correspondants aux règles définies.  

Le démon `auditd` et les programmes clients qui l'accompagnent (`auditctl`, `ausearch`, `aureport`) peuvent être utilisés à différentes fins, par exemple pour [surveiller les accès effectués sur des fichiers sensibles](http://www.cyberciti.biz/tips/linux-audit-files-to-see-who-made-changes-to-a-file.html).  

Dans cet exemple, nous allons voir comment surveiller les connexions réseaux. Avec `iptables` nous pourrions logger les connexions entrantes et sortantes, malheureusement nous n'aurions pas les informations concernant le programme qui participe à ces connexions.  

Pour savoir si vous disposez d'`auditd`, le plus simple est encore de regarder s'il est présent parmi les processus en cours (commande `ps aux`). Si c'est le cas, cela ne signifie pas pour autant qu'il soit actif. Pour cela il faut lancer la commande :  

```console
# auditctl -s
AUDIT_STATUS: enabled=0 flag=1 pid=3670 rate_limit=0 backlog_limit=256 lost=0 backlog=0
```

Ici le démon n'est pas actif (`enabled=0`). Pour l'activer il faut tapper `auditctl -e 1` (et `auditctl -e 0` quand vous souhaiterez le désactiver).  
Si on relance `auditctl -s`, nous obtiendrons `enabled=1`.  

Afin de voir les logs défiler, je vous recommande d'exécuter un `tail -f /var/log/audit/audit.log` dans une console.  

Informons maintenant `auditd` que nous souhaitons garder les connexions à l'œil. L'option `-S` permet d'activer la surveillance sur un appel système. À tout hazard on tente la commande :  

```console
# auditctl -a exit,always -S connect
Syscall name unknown: connect
```

Et là... c'est le drame. En réalité, il n'y a pas de syscall nommé `connect`. Les différents syscalls réseau passent par [socketcall](http://www.linux-kheops.com/doc/man/manfr/man-html-0.9/man2/socketcall.2.html).  

On utilisera alors la commande `auditctl -a exit,always -S socketcall` à la place.  

Aucun message de confirmation n'apparait à l'exécution de la commande, mais un message devrait apparaître dans le fichier de log et il nous est possible de lister les règles avec `auditctl` :  

```console
# auditctl -l
LIST_RULES: exit,always syscall=socketcall
```

Puisque tout est ok, on lance un [netcat](http://www.vulnwatch.org/netcat/) sur [www.perdu.com](http://www.perdu.com/) (port 80) et là... tout va très vite !  

Tout un tas de lignes ont fait leur apparition dans le fichier de log. Pour l'article, je n'ai gardé que celles qui m'intéressent à savoir :  

```plain
type=SYSCALL msg=audit(1198689227.553:67): arch=40000003 syscall=102 success=yes exit=3 a0=1 a1=bfeaf4f0 a2=0 a3=0 items=0 ppid=6356 pid=6608 auid=4294967295 uid=1000 gid=100 euid=1000 suid=1000 fsuid=1000 egid=100 sgid=100 fsgid=100 tty=pts4 comm="netcat" exe="/usr/bin/netcat" key=(null)
type=SOCKETCALL msg=audit(1198689227.553:67): nargs=3 a0=2 a1=1 a2=6
type=SYSCALL msg=audit(1198689227.553:68): arch=40000003 syscall=102 success=yes exit=0 a0=e a1=bfeaf4f0 a2=0 a3=0 items=0 ppid=6356 pid=6608 auid=4294967295 uid=1000 gid=100 euid=1000 suid=1000 fsuid=1000 egid=100 sgid=100 fsgid=100 tty=pts4 comm="netcat" exe="/usr/bin/netcat" key=(null)
type=SOCKETCALL msg=audit(1198689227.553:68): nargs=5 a0=3 a1=1 a2=2 a3=bfeaf528 a4=4
type=SYSCALL msg=audit(1198689227.553:69): arch=40000003 syscall=102 success=yes exit=0 a0=3 a1=bfeaf4f0 a2=0 a3=0 items=0 ppid=6356 pid=6608 auid=4294967295 uid=1000 gid=100 euid=1000 suid=1000 fsuid=1000 egid=100 sgid=100 fsgid=100 tty=pts4 comm="netcat" exe="/usr/bin/netcat" key=(null) type=SOCKADDR msg=audit(1198689227.553:69): saddr=0200005052A5B0910000000000000000
type=SOCKETCALL msg=audit(1198689227.553:69): nargs=3 a0=3 a1=804f020 a2=10
```

Je vous l'accorde, ce n'est par très parlant. On va décrypter ça ;-)   

Les lignes `SYSCALL`, comme leur nom l'indique, nous renseigne sur l'appel système qui a été détecté ainsi que le programme à son origine et les droits qu'il possède à ce moment.  
Comme expliqué [ici](http://racl.oltrelinux.com/tutorial/asmsocket.html) ou [là](http://diozaka.org/modules/bindshell.html), on apprend que `socketcall` est bien le syscall numéro 102 (ou 0x66 en hexadécimal).  

Il prend comme argument le nom de la fonction réseau à utiliser, chacune ayant une valeur prédéfinie :  

```c
#define SYS_SOCKET      1
#define SYS_BIND        2
#define SYS_CONNECT     3
#define SYS_LISTEN      4
#define SYS_ACCEPT      5
#define SYS_GETSOCKNAME 6
#define SYS_GETPEERNAME 7
#define SYS_SOCKETPAIR  8
#define SYS_SEND        9
#define SYS_RECV        10
#define SYS_SENDTO      11
#define SYS_RECVFROM    12
#define SYS_SHUTDOWN    13
#define SYS_SETSOCKOPT  14
#define SYS_GETSOCKOPT  15
#define SYS_SENDMSG     16
#define SYS_RECVMSG     17
```

De cette façon, si on reprend notre première ligne :  

> 
> type=SYSCALL msg=audit(1198689227.553:67): arch=40000003 **syscall=102** success=yes exit=3 **a0=1** a1=bfeaf4f0 a2=0 a3=0


On en déduit qu'il s'agit d'un appel à la fonction `socket()` car `a0=1=SYS_SOCKET`. En lançant un strace parallèlement, on voit que `socket()` a été utilisé de cette manière :  

```c
socket(PF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
```

Sachant que `PF_INET` = 2, `SOCK_STREAM` = 1 et que `IPPROTO_TCP` = 6, on est peu surpris de retrouver ces valeurs dans la ligne suivante :  

```plain
type=SOCKETCALL msg=audit(1198689227.553:67): nargs=3 a0=2 a1=1 a2=6
```

La fonction suivante est un `setsockopt()` : `syscall=102 a0=e` (14 en décimal) appelé de cette façon :  

```c
setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0
```

Là encore on retrouve les bonnes valeurs dans les messages d'`auditd`.  

Voilà enfin la dernière partie qui nous intéresse et qui correspond au connect suivant :  

```plain
connect(3, {sa_family=AF_INET, sin_port=htons(80), sin_addr=inet_addr("82.165.176.145")}, 16) = 0

type=SYSCALL msg=audit(1198689227.553:69): arch=40000003 syscall=102 success=yes exit=0 a0=3...
type=SOCKADDR msg=audit(1198689227.553:69): saddr=0200005052A5B0910000000000000000
type=SOCKETCALL msg=audit(1198689227.553:69): nargs=3 a0=3 a1=804f020 a2=10
```

La ligne `SOCKADDR` correspond à une structure `sockaddr` (le second argument du `connect()`) comme commenté [ici](http://www.promethos.org/lxr/http/source/include/linux/audit.h). Cette structure est la suivante :  

```nasm
 struc sockaddr_in
         sin_family:     resw    1       ; protocol family
         sin_port:       resw    1       ; port
         sin_addr:       resd    1       ; struct sin_addr.s_addr
         sin_zero:       resd    2       ; padding
 endstruc
```

Le `saddr` se décompose donc en :  

* `0x02` : `AF_INET`
* `0x50` : le port après un `htons()`, ici le port 80
* `52A5B091` : l'adresse IP en hexadécimal, soit `180.249.41.240` (www.perdu.com)

Nous sommes finalement parvenus à déchiffrer une connexion dans les logs d'`auditd`.

*Published January 10 2011 at 10:45*
