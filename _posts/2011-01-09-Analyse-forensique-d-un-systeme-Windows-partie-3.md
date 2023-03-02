---
title: "Analyse forensique d'un système Windows : partie 3"
tags: [Computer forensics, Windows]
---

## A popular IRC (Internet Relay Chat) program called MIRC was installed...

> What are the user settings that was shown when the user was online and in a chat channel?  

Les préférences sont sauvegardées dans le fichier `Program Files/mIRC/mirc.ini` :  

```ini
[ident]
active=yes
userid=Mrevil
system=UNIX
port=113
[mirc]
user=Mini Me
email=none@of.ya
nick=Mr
anick=mrevilrulez
host=Undernet: US, CA, LosAngelesSERVER:losangeles.ca.us.undernet.org:6660GROUP:Undernet
```

## This IRC program has the capability to log chat sessions...

> List 3 IRC channels that the user of this computer accessed.  

On trouve entre autres les fichiers suivants dans `Program Files/mIRC/logs` : `#Chataholics.UnderNet.log`, `#Elite.Hackers.UnderNet.log`, `#evilfork.EFnet.log`, `#thedarktower.AfterNET.log`, `#ushells.UnderNet.log`.  

## Ethereal, a popular "sniffing" program that can be used to intercept wired and wireless internet packets was also found to be installed...

> When TCP packets are collected and re-assembled, the default save directory is that users \My Documents directory. What is the name of the file that contains the intercepted data?  

Sans difficultés, on trouve un fichier pcap à `Documents and Settings/Mr. Evil/interception`  

## Viewing the file in a text format reveals much information about who and what was intercepted...

> What type of wireless computer was the victim (person who had his internet surfing recorded) using?  

Ce que *Mr. Evil* a pu intercepter, c'est du traffic HTTP.  

Une simple requête nous donne des informations sur la victime :  

```http
GET /hm/folder.aspx HTTP/1.1
Accept: */*
UA-OS: Windows CE (Pocket PC) - Version 4.20
UA-color: color16
UA-pixels: 240x320
UA-CPU: Intel(R) PXA255
UA-Voice: FALSE
Referer: http://mobile.msn.com/hm/folder.aspx?ts=1093601294&fts=1093566459&folder=ACTIVE&msg=0
UA-Language: JavaScript
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; PPC; 240x320)
Host: mobile.msn.com
Connection: Keep-Alive
```

On a donc affaire à un PDA équipe de *Windows CE* avec le navigateur Internet Explorer.  

## What websites was the victim accessing?  

```console
# strings interception|grep Host|sort|uniq
Host:239.255.255.250:1900
Host: login.passport.com
Host: login.passport.net
Host: mobile.msn.com
Host: www.passportimages.com
```

La victime accédait à son compte MSN depuis son PDA.  

Les requêtes étranges correspondant à l'adresse IP `239.255.255.250` et à destination du port 1900 sont en fait des requêtes [UPnP](http://www.microsoft.com/technet/network/plan/insidenet/sohonet/upnpsup.mspx). L'adresse IP `239.255.255.250` est une [adresse multicast](http://www.iana.org/assignments/multicast-addresses) et n'est pas routable sur Internet.  

![SSDP UPnP](/assets/img/ssdp_upnp.jpg)  

En regardant les paquets, on voit aussi que *Mr. Evil* laisse échapper une requête SMB :  

![SMB request](/assets/img/interception.jpg)  

## Search for the main users web based email address. What is it?  

Un grep sur le caractère arobase nous donne deux résultats.  

Le premier correspond à des données envoyées par POST pour l'envoi d'un email :  
`__EVENTTARGET=&__EVENTARGUMENT=&ToTextBox=rudy@hotmail.com&CcTextBox=&BccTextBox=& SubjectTextBox=Hey%2C+This+is+Mr+Evil&BodyTextBox=Hi.+Call+me&SendCommand=Send`  

Et celle qui nous intéressera plus et la requête de déconnexion à MSN :  

```http
GET /logout.srf?lc=1033&id=961&... HTTP/1.1
Accept: */*
UA-OS: Windows CE (Pocket PC) - Version 4.20
UA-color: color16
UA-pixels: 240x320
UA-CPU: Intel(R) PXA255
UA-Voice: FALSE
Referer: http://mobile.msn.com/hm/folder.aspx?ts=1093601294&fts=1093566459&folder=ACTIVE&msg=0
UA-Language: JavaScript
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; PPC; 240x320)
Host: login.passport.com
Connection: Keep-Alive
Cookie: MSPPre=findme69@hotmail.com; BrowserTest=Success?; MSPPost=1; MSPAuth=6jjJk8xxgD...
```

## Yahoo mail, a popular web based email service, saves copies of the email under what file name?  

Après avoir fait un essai, j'aurais été tenté de dire `file.html`. En réalité IE met en cache les mails de chez _Yahoo!_ dans des fichiers du type `wbkXX.tmp` où `XX` représente une valeur hexadécimale.  

La plupart des mails étaient du spam, des discussions sur des newsgroup _Yahoo!_ ou des informations sans intérêts.  

## How many executable files are in the recycle bin? Are these files really deleted?  

Les fichiers envoyés à la corbeille ne sont pas réellement supprimés. Ils sont placés dans un répertoire nommé `RECYCLER` et sont renommés sous la forme `DcN.ext` où `N` est un chiffre décimal et ext correspond à l'extension originale du fichier.  
Les correspondances permettant de remettre le fichier en place en cas de restauration sont stockés dans un fichier INFO2 que l'on peut analyser à l'aide de `rifiuti`, l'un des très pratiques outils de la suite [ODESSA](http://odessa.sourceforge.net/).  

```console
# file RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/*
RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/Dc1.exe:     MS-DOS executable PE  for MS Windows (GUI) Intel 80386 32-bit
RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/Dc2.exe:     MS-DOS executable PE  for MS Windows (GUI) Intel 80386 32-bit, Nullsoft Installer self-extracting archive
RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/Dc3.exe:     MS-DOS executable PE  for MS Windows (GUI) Intel 80386 32-bit, UPX compressed
RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/Dc4.exe:     MS-DOS executable PE  for MS Windows (GUI) Intel 80386 32-bit, Nullsoft Installer self-extracting archive
RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/desktop.ini: ASCII text, with CRLF line terminators
RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/INFO2:       Hitachi SH big-endian COFF object, not stripped

# rifiuti RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/INFO2
INFO2 File: RECYCLER/S-1-5-21-2000478354-688789844-1708537768-1003/INFO2

INDEX   DELETED TIME    DRIVE NUMBER    PATH    SIZE
1       08/25/2004 18:18:25     2       C:\Documents and Settings\Mr. Evil\Desktop\lalsetup250.exe      2160128
2       08/27/2004 17:12:30     2       C:\Documents and Settings\Mr. Evil\Desktop\netstumblerinstaller_0_4_0.exe       1325056
3       08/27/2004 17:15:26     2       C:\Documents and Settings\Mr. Evil\Desktop\WinPcap_3_01_a.exe   442880
4       08/27/2004 17:29:58     2       C:\Documents and Settings\Mr. Evil\Desktop\ethereal-setup-0.10.6.exe    8460800
```

On a donc 4 exécutables qui correspondent à des programmes d'installation.  

## How many files are actually reported to be deleted by the file system?  

Il y a énormément de fichiers effacés par le système. J'ai obtenu une liste par [Autopsy](http://www.sleuthkit.org/autopsy/) mais je n'ai pas noté le nombre exact. Aucun fichier ne m'a semblé être d'intérêt dans notre cas.  

## Perform an Anti-Virus check. Are there any viruses on the computer?  

```console
# avgscan .
AVG7 Anti-Virus command line scanner
Copyright (c) 2006 GRISOFT, s.r.o.
Version du programme 7.5.45, engine 442
Base de Virus: Version 269.4.0/762  2007-04-15
Le type de licence est GRATUIT
./My Documents/COMMANDS/enum.exe  Programme potentiellement nuisible HackTool.VT
./My Documents/COMMANDS/nc.exe  Programme potentiellement nuisible RemoteAdmin.T
./My Documents/COMMANDS/pwdump2.exe  Programme potentiellement nuisible HackTool.AH
./My Documents/ENUMERATION/NT/enum/files/enum.exe  Programme potentiellement nuisible HackTool.VT
./My Documents/EXPLOITATION/NT/Get Admin/GASYS.DLL  Programme potentiellement nuisible Exploit.AHE
./My Documents/EXPLOITATION/NT/Get Admin/GetAdmin.exe  Programme potentiellement nuisible Exploit.AHC
./My Documents/EXPLOITATION/NT/sechole/ADMINDLL.DLL  Cheval de Troie Generic3.CPH
./My Documents/EXPLOITATION/NT/sechole/SECHOLE.EXE  Cheval de Troie Generic.GRY
./My Documents/EXPLOITATION/NT/sechole/SECHOLED.EXE  Cheval de Troie Generic.ACE
./WINDOWS/system32/advert.dll  Adware Generic.GPV
Analysés: 7420 fichiers, 0 secteurs
Infections: 10
Erreurs: 0
```

Comme on s'en doute il y a quelques outils détectés comme *HackTool*, *Cheval de Troie* et *Exploit*.  

Le poste semble être infecté par un adware. Les caches d'IE m'ont aussi permis de constater le manque de filtrage contre les ADS (IE olbige).  

## Quelques trucs pour finir  

*Pasco* de [ODESSA](http://odessa.sourceforge.net/) permet de lire les fichiers `.dat` d'IE.  

En dehors des sites de _Yahoo!_, _Ethereal_, _NetStumbler_, _Hackoo_, _2600_ etc j'ai relevé les urls suivantes :  

```plain
file://4.12.220.254/Temp/yng13.bmp
http://edit.yahoo.com/config/id_check?.fn=Greg&.ln=Schardt&.id=mrevil2000&.u=b568cfp0ic6g0
```

Je ne saurais dire à quoi correspond la première. La seconde est la tentative de création du compte *mrevil2000*.  

Le pirate a aussi accédé à _WhatIsMyIP_ à plusieurs reprises qui lui a répondu `216.62.23.121` d'après une page en cache.  

Le compte email de *Mr. Evil* ne contenait que le message de bienvenue après création de la boite :  

![Mr Evil Inbox](/assets/img/yahoo_evil_greg.jpg)

Look@LAN a mémorisé deux adresses :  

```plain
\$$$PROTO.HIV\Look@LAN\MRUHosts
LastWrite time: Thu Aug 26 15:05:02 2004
        --> MRU1;REG_SZ;4.12.220.254^@
        --> MRU2;REG_SZ;169.254.50.81^@
```

Mais qui est 4.12.220.254 ?  

Mémoire de *"Exécuter"* :  

```plain
\$$$PROTO.HIV\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU
LastWrite time: Thu Aug 26 15:05:15 2004
        --> a;REG_SZ;www.cnn.com\1^@
        --> MRUList;REG_SZ;dcba^@
        --> b;REG_SZ;cmd\1^@
        --> c;REG_SZ;www.google.com\1^@
        --> d;REG_SZ;telnet\1^@
```

Un répertoire partagé était visiblement sur notre IP mystère :  

```console
# grep -r 4.12.220.254 *
Fichier binaire Documents and Settings/Mr. Evil/Local Settings/History/History.IE5/index.dat concorde
Fichier binaire Documents and Settings/Mr. Evil/Local Settings/History/History.IE5/MSHist012004082620040827/index.dat concorde
Fichier binaire Documents and Settings/Mr. Evil/NetHood/Temp on m1200 (4.12.220.254)/target.lnk concorde
Fichier binaire Documents and Settings/Mr. Evil/NTUSER.DAT concorde
Fichier binaire Documents and Settings/Mr. Evil/Recent/Temp on m1200 (4.12.220.254).lnk concorde
Fichier binaire Documents and Settings/Mr. Evil/Recent/yng13.lnk concorde
```

J'ai aussi vu des mails visiblement encodés parmi les caches pour _Yahoo!_ Bien que le codage semble simple, je ne s'aurais pas dire ce qu'il en est.  

## Conclusion  

Si vous avez des choses à cacher, n'utilisez pas Windows (à mon avis KDE c'est à peu près le même constat)  

Tout ça, c'était très intéressant à analyser et j'ai appris quelques nouveaux trucs sur Windows.  

Deux autres docs à lire :  
[Recycler Bin Record Reconstruction](http://www.e-fense.com/helix/Docs/Recycler_Bin_Record_Reconstruction.pdf)  

[Un document sur les fichiers LNK](http://mediasrv.ns.ac.yu/extra/fileformat/windows/lnk/shortcut.pdf)

*Published January 09 2011 at 18:10*
