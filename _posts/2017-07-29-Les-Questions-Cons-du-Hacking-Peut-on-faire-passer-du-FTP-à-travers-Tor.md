---
title: "Les Questions Cons du Hacking : Peut-on faire passer du FTP à travers Tor ?"
tags: [Réseau, Tor]
---

S01E04 : Peut-on faire passer du FTP à travers Tor ?
----------------------------------------------------

Oui ? Non ? Peut-être ? Qui prend les paris ?  

Les partisans du oui affirmeront probablement que Tor permet de relayer du TCP or comme FTP utilise TCP il n'y a aucune raison que ce soit impossible.  

Sauf que :  

```console
$ torify ftp opensuse.mirrors.ovh.net
Connected to 91.121.189.201.
220 ProFTPD 1.3.5 Server (OVH.com mirror system) [::ffff:91.121.189.201]
Name (opensuse.mirrors.ovh.net:devloop): anonymous
331 Anonymous login ok, send your complete email address as your password
Password:
230 Anonymous access granted, restrictions apply
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
500 Illegal PORT command
ftp: bind: Address already in use
```

Oups. Certains insisteront alors pour passer en mode passif :  

```console
$ torify ftp opensuse.mirrors.ovh.net
Connected to 91.121.189.201.
220 ProFTPD 1.3.5 Server (OVH.com mirror system) [::ffff:91.121.189.201]
Name (opensuse.mirrors.ovh.net:devloop): anonymous
331 Anonymous login ok, send your complete email address as your password
Password:
230 Anonymous access granted, restrictions apply
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> passive
Passive mode on.
ftp> ls
227 Entering Passive Mode (91,121,189,201,139,50).
150 Opening ASCII mode data connection for file list
drwxr-xr-x  16 ftp      ftp          4096 Jul 28 05:26 archlinux
-rw-r--r--   1 ftp      ftp            29 Jul 28 07:30 archlinux.timestamp
-rw-r--r--   1 ftp      ftp          1150 Dec 11  2014 favicon.ico
drwxrwxr-x  44 ftp      ftp          4096 Apr  5 12:42 ftp.centos.org
-rw-r--r--   1 ftp      ftp            29 Jul 28 09:42 ftp.freebsd.org.timestamp
drwxr-xr-x   3 ftp      ftp          4096 Jul 28 06:48 ftp.mysql.com
-rw-r--r--   1 ftp      ftp            29 Jul 28 10:30 ftp.mysql.com.timestamp
drwxr-xr-x  43 ftp      ftp          4096 Jul  1  2016 ftp.slackware.com
-rw-r--r--   1 ftp      ftp            29 Jul 28 12:31 ftp.slackware.com.timestamp
drwxr-xr-x   6 ftp      ftp          4096 Mar 28  2011 gentoo-distfiles
drwxr-xr-x 171 ftp      ftp          4096 Feb  1  2016 gentoo-portage
drwxr-xr-x   5 ftp      ftp          4096 Jul 28 06:52 opensuse
-rw-r--r--   1 ftp      ftp            29 Jul 28 06:52 opensuse.timestamp
drwxrwsr-x 248 ftp      ftp         20480 Jul 17 07:08 parallels
-rw-r--r--   1 ftp      ftp            29 Jul 28 08:32 parallels.timestamp
drwxr-xr-x   3 ftp      ftp          4096 Jun 16  2015 pub
-rw-r--r--   1 ftp      ftp            29 Jul 28 09:06 www.freebsd.org.timestamp
226 Transfer complete
ftp> 221 Goodbye.
```

Et la magie s'opère !  

Première question à régler : quelle est la différence entre le mode actif et le mode passif FTP ?  

Relançons le transfert FTP en actif, mais cette fois sans passer sous Tor.  

![Active FTP transfert](/assets/img/ftp/ftp_actif.png)

On voit ici que l'on envoie au serveur FTP une adresse IP (`192.168.1.6`) ainsi qu'un port (`44468` car `((173<<8) | 180) = 44468`) via la commande FTP `PORT`. Cette commande permet de définir le canal qui sera utilisé pour le transfert des données (`FTP-DATA`), c'est-à-dire l'adresse à laquelle le serveur FTP doit envoyer les listings de fichiers et leur contenus.  

Ce mode est dit actif, car c'est le client qui prend en charge le fait d'ouvrir un port dédié aux transferts de données.  

Dans la capture, une fois que l'on envoie la commande `LIST` au serveur, ce dernier initie une connexion sur notre port `44468` pour envoyer les 1239 octets correspondants au listing du dossier. Ici l'adresse IP spécifiée via `PORT` est celle du réseau local donc inutilisable par le serveur qui se retranche sur l'IP qui s'est réellement connectée.  

La raison pour laquelle ça ne marche pas avec Tor c'est tout simplement qu'un circuit Tor ne permet que d'établir une connexion sortante, on ne peut pas indiquer à une node de sortie d'ouvrir un port et de nous relayer les informations en sens inverse.  

En mode passif, c'est bien sûr l'inverse.  

![Passive FTP transfert](/assets/img/ftp/ftp_passif.png)

Une fois connecté on envoie la commande `PASV` pour demander au serveur le mode passif (qu'il acceptera ou non selon sa configuration).  

S'il l'accepte il retourne une adresse IP et un numéro de port sous le même format que la commande `PORT` sur lequel on se connecte et sur lequel le serveur transmet les données (comme les 1239 octets de listing).  

Si le mode passif fonctionne avec Tor c'est parce que le client ne fait qu'établir des connexions sortantes, il n'a aucun port à ouvrir.  

Au pire une connexion sur le port de données mettra un peu de temps à se faire, car il faudra trouver une node de sortie qui autorise l'accès à ce numéro de port, mais c'est une autre histoire :)  

Maintenant peut-on faire passer une connexion FTP active à travers Tor ? On a vu en [S01E03]({% link _posts/2017-07-22-Les-Questions-Cons-du-Hacking-Un-reverse-shell-anonyme-c-est-possible.md %}) qu'on pouvait avoir un connect-back anonyme en exploitant `Ngrok`.  

Pour le cadre de cet article le tunnel Ngrok ne passera pas à travers Tor mais comme indiqué dans le précédent article ce n'est pas plus compliqué à faire que de rajouter une ligne dans un fichier de configuration :)   

Donc il suffit en théorie de se connecter via Tor sur le port 21 du serveur FTP, d'envoyer une commande `PORT` avec l'adresse IP et le port d'un tunnel Ngrok précédemment créé et de recevoir les résultats de `LIST` via ce tunnel.  

![Active FTP transfert with ftp-data going through a Ngrok tunnel](/assets/img/ftp/ftp_tor_actif.png)

Seulement dans la pratique, c'est loin d'être aussi simple. Les clients FTP existants rendent difficile la manipulation, car ils gèrent mal la possibilité de spécifier l'adresse de la commande `PORT` ou la façon de la gérer. D'autres points peuvent bloquer comme *FileZilla* qui passe obligatoirement en mode passif si on spécifie un proxy `SOCKS`.  

Le mieux est encore d'écrire son propre client FTP. Pour réussir la manipulation, j'ai réécrit certaines méthodes de la classe FTP de la librairie `ftplib` de Python.  

Quand on regarde [son code source](https://github.com/python/cpython/blob/3.6/Lib/ftplib.py) on voit qu'il faut changer la méthode `makeport()` pour qu'elle envoie l'adresse du tunnel Ngrok et non notre adresse, mettre en écoute un socket sur le loopback et fixer le numéro de port associé qui serait normalement aléatoire.  

La méthode `connect()` doit aussi être modifiée, tout simplement pour s'assurer que la connexion passe par Tor.  

Ce qui nous donne :  

```python
from ftplib import FTP
import socket
import socks  # pip install PySocks

FTP_SRV_IP = "100.100.100.100"
NGROK_IP = "52.15.194.28"
NGROK_PORT = 18967
DATA_PORT = 31337
TIMEOUT = 10

class NgrokFTP(FTP):
    port = 2121  # Mon serveur FTP écoute en local sur 21 mais est NATé en 2121 sur la box
    timeout = TIMEOUT

    def makeport(self):
        err = None
        sock = socket.socket(socket.AF_INET)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', DATA_PORT))
        sock.listen(1)
        resp = self.sendport(NGROK_IP, NGROK_PORT)
        sock.settimeout(TIMEOUT)
        return sock

    def connect(self, host='', port=2121, timeout=TIMEOUT, source_address=None):
        self.host = host
        self.port = port
        self.sock = socks.socksocket()
        self.sock.settimeout(timeout)
        self.sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        self.sock.connect((self.host, self.port))
        self.af = self.sock.family
        self.file = self.sock.makefile('r', encoding=self.encoding)
        self.welcome = self.getresp()
        return self.welcome

my_ftp = NgrokFTP(FTP_SRV_IP)
my_ftp.set_pasv(False)
my_ftp.login()
my_ftp.retrlines('LIST')
my_ftp.quit()
```

Et le résultat avec le ProFTPd mis en place pour l'occasion :  

```console
$ python ftp_tor.py
-rw-r--r--   1 ftp      ftp           170 Apr  5  2016 welcome.msg
```

Victory !  

Enfin pas tout à fait : pour parvenir à mes fins il aura fallu activer l'option [AllowForeignAddress](http://www.proftpd.org/docs/directives/linked/config_ref_AllowForeignAddress.html) de *ProFTPd* qui permet d'accepter les adresses IP différentes de l'adresse IP qui a initié la connexion pour la commande `PORT`.  

Une option similaire pour *vsFTPd* se nomme [port_promiscuous](https://security.appspot.com/vsftpd/vsftpd_conf.htm) et est aussi désactivée par défaut.  

La raison de ces opt-in est toute simple : l'activer rend le serveur FTP vulnérable à une [attaque bounce](https://en.wikipedia.org/wiki/FTP_bounce_attack) (comme le script Nmap du même nom).  

Pour conclure, le FTP sous Tor ça se fait sans aucun problème si le serveur autorise le mode passif.  

Si ce n'est pas le cas il faut sacrifier un poulet pour qu'il permette le bounce et coder son propre client FTP utilisant un tunnel Ngrok... Pas gagné.  

Et dans tous les cas (actif comme passif) on peut bruteforcer allègrement les comptes :D  


*Published July 29 2017 at 08:30*
