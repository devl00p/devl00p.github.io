---
title: "Analyse forensique d'un système Windows : partie 2"
tags: [Computer forensics, Windows]
---

## A search for the name of *"Greg Schardt"* reveals multiple hits...

> One of these proves that Greg Schardt is Mr. Evil and is also the administrator of this computer. What file is it? What software program does this file relate to?  

On passe un grep bien placé : `grep -R -i schar *`  

Parmi les résultats obtenus, une page html dans le cache d'Internet Explorer :  
`Documents and Settings/Mr. Evil/Local Settings/Temporary Internet Files/Content.IE5/JIRVJY9X/id_check[1].htm`  

Ce fichier nous apprend que l'utilisateur a tenté d'enregistrer un compte *Yahoo! Mail* avec le login *mrevil2000*. Ce compte était déjà pris, *Yahoo!* propose différentes solutions basées sur les noms et prénoms qu'il a saisi. Ces informations sont d'ailleurs présentes dans le code source de la page :  

![Cookies extracted from IE](/assets/img/cache_ie_mr_evil.jpg)

On trouve aussi un fichier ini correspondant à l'application de monitoring réseau [Look@LAN](http://www.lookatlan.com/). Ce fichier est `Program Files/Look@LAN/irunin.ini` qui contient notamment les lignes suivantes :  

```ini
[Variables]
%LANHOST%=N-1A9ODN6ZXK4LQ
%LANDOMAIN%=N-1A9ODN6ZXK4LQ
%LANUSER%=Mr. Evil
%REGOWNER%=Greg Schardt
%MYDOCUMENTSDIR%=C:\Documents and Settings\Mr. Evil\My Documents
%SRCFILE%=C:\Documents and Settings\Mr. Evil\Desktop\lalsetup250.exe
%SRCDIR%=C:\Documents and Settings\Mr. Evil\Desktop
```

Non seulement on a la preuve que *Greg Schardt* se cache derrière *Mr. Evil* mais aussi que son compte windows a les droits nécessaires pour installer un logiciel.  

De plus les comptes *Administrator* et *Mr. Evil* ont des mots de passe vide (les hashs présents correspondent à une chaine vide) :  

```console
# cd /mnt/WINDOWS/system32/config
# bkhive system /tmp/hive
bkhive 1.1.0 by Objectif Securite
http://www.objectif-securite.ch
original author: ncuomo@studenti.unina.it

Root Key : $$$PROTO.HIV
Default ControlSet: 001
Bootkey: d6089864d286cb02e4d55c4968d130ab
# samdump2 SAM /tmp/hive
samdump2 1.1.0 by Objectif Securite
http://www.objectif-securite.ch
original author: ncuomo@studenti.unina.it

Root Key : SAM
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
No password for Guest
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
HelpAssistant:1000:21118292169779ec4027c45deeef399d:bd8c73557c81323923ce58a35a475b63:::
SUPPORT_388945a0:1002:aad3b435b51404eeaad3b435b51404ee:c23fadd57e66830c9575b070ad3a2026:::
Mr. Evil:1003:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

Cela s'ajoute à l'hypothèse qu'une seule personne utilise le portable.  

## List the network cards used by this computer  
Dans la ruche system, sous `\ControlSet001\Services\Tcpip\Parameters\Interfaces` on trouve les différentes interfaces réseau :  

```plain
{6E4090C2-FAEF-489A-8575-505D21FC1049}
{86FC0C96-3FF2-4D59-9ABA-C602F213B5D2}
{F9356994-E82B-49FC-BFE9-59568F68F497}
{417ECA57-8D1D-49AE-990C-18E6A627A059}
```

J'ai aussi remarqué par d'autres clés dans la BDR que les deux dernières interfaces semblent être des alias. Seules les deux premières sont à prendre en compte. Les clés sous `Software\Microsoft\Windows NT\CurrentVersion\NetworkCards` nous donnent plus d'informations sur ces interfaces.  

Ainsi `6E4090C2-FAEF-489A-8575-505D21FC1049` serait une *Xircom CardBus Ethernet 100 + Modem 56 (Ethernet Interface)* tandis que `86FC0C96-3FF2-4D59-9ABA-C602F213B5D2` serait une carte *Compaq WL110 Wireless LAN PC Card*.  

## This same file reports the IP address and MAC address of the computer. What are they?  

> An internet search for vendor name/model of NIC cards by MAC address can be used to find out which network interface was used. In the above answer, the first 3 hex characters of the MAC address report the vendor of the card. Which NIC card was used during the installation and set-up for LOOK@LAN?  

C'est de loin la partie qui m'a posée le plus de problèmes. Windows ne semble pas stocker les addresses MAC dans un fichier spécifique par conséquent il a fallu chercher ailleurs...  

La carte ethernet est visiblement configuré pour avoir une adresse IP attribuée par DHCP :  

```plain
\ControlSet001\Services\{6E4090C2-FAEF-489A-8575-505D21FC1049}\Parameters\Tcpip
LastWrite time: Fri Aug 27 15:30:17 2004
        --> EnableDHCP;REG_DWORD;1
        --> IPAddress;REG_MULTI_SZ;0.0.0.0^@^@
        --> SubnetMask;REG_MULTI_SZ;0.0.0.0^@^@
        --> DefaultGateway;REG_MULTI_SZ;
        --> DhcpIPAddress;REG_SZ;0.0.0.0^@
        --> DhcpSubnetMask;REG_SZ;255.0.0.0^@
        --> DhcpServer;REG_SZ;255.255.255.255^@
        --> Lease;REG_DWORD;3600
        --> LeaseObtainedTime;REG_DWORD;1093620617
        --> T1;REG_DWORD;1093622417
        --> T2;REG_DWORD;1093623767
        --> LeaseTerminatesTime;REG_DWORD;1093624217
```

Dans le fichier `Program Files/Look@LAN/irunin.ini` on a des informations nous aidant à résoudre la seconde question :  

```ini
%LANIP%=192.168.1.111
%LANNIC%=0010a4933e09
```

La configuration de Ethereal (`Documents and Settings/Mr. Evil/Application Data/Ethereal/preferences`) nous informe que l'interface Wireless est plus souvent utilisée pour les attaques :  

```plain
####### Capture ########
# Default capture device
capture.device: ORINOCO PC Card (Microsoft's Packet Scheduler) : \Device\NPF_{86FC0C96-3FF2-4D59-9ABA-C602F213B5D2}
```

tout comme celles de Cain (`\Software\Cain\Settings`) :  

```plain
Adapter;REG_SZ;\Device\NPF_{86FC0C96-3FF2-4D59-9ABA-C602F213B5D2}
```

Une information précieuse est présente dans les *event logs* du système (fichiers `Evt`) :  

```plain
Record nb : 11
Time Generated : Thu Aug 19 22:50:32 2004 GMT
Time Written : Thu Aug 19 22:52:02 2004 GMT
Evt ID : 1073746025 Evt type : 4 Evt category : 0
Program : Tcpip
Computer : N-1A9ODN6ZXK4LQ
String 0 :
String 1 : \DEVICE\TCPIP_{6E4090C2-FAEF-489A-8575-505D21FC1049}

Record nb : 12
Time Generated : Thu Aug 19 22:52:59 2004 GMT
Time Written : Thu Aug 19 22:52:59 2004 GMT
Evt ID : 1007 Evt type : 2 Evt category : 0
Program : Dhcp
Computer : N-1A9ODN6ZXK4LQ
String 0 : 0010A4933E09
String 1 : 169.254.242.213
```

Résumons : l'interface `6E4090C2-FAEF-489A-8575-505D21FC1049` correspond à la carte ethernet *Xircom*. L'ip `169.254.242.213` lui a été attribuée par DHCP. L'adresse MAC est `00:10:A4:93:3E:09`. C'est cette carte qui a permis d'installer *Look@LAN*.  

Pour lire les logs Windows j'ai utilisé `evtreader.pl` disponible sur [d-fence.be](http://www.d-fence.be/).  

## Find 6 installed programs that may be used for hacking.  

On trouve sans difficultés différents programmes installés : `Anonymiser`, `Cain`, `Ethereal`, `Look@LAN`, `Network Stumbler` et `AnalogX WhoIs`.  
Notons aussi la présence de tout un arsenal d'outils de piratage classés soigneusement par catégories (énumération, footprinting, exploitation...) dans `C:\My Documents\`.  
Dans les entrées `UserAssist` et `MRU` de la base de registre, qui correspondent à la mémorisation des documents récents et des commandes tapées dans *Démarrer > Exécuter*, on trouve de nombreuses références à un lecteur `D:` qui contient beaucoup de programmes du même type.  

## What is the SMTP email address for Mr. Evil?  

En fouillant dans les fichiers présents dans le cache d'Internet Explorer (certains sont compressés), j'ai pû trouver une page correspondant à la fin de la procédure de création du compte *Yahoo! Mail* de *Mr. Evil* :  

![Mr Evil email address](/assets/img/yahoo_mrevil.jpg)

## What are the NNTP (news server) settings for Mr. Evil?  

Ces informations se situent dans la ruche `NTUSER.DAT` :  

```plain
\$$$PROTO.HIV\Software\Microsoft\Windows\CurrentVersion\UnreadMail\whoknowsme@sbcglobal.net
LastWrite time: Fri Aug 20 21:18:30 2004
        --> MessageCount;REG_DWORD;0
        --> TimeStamp;REG_BINARY;90 0e dc 3d fb 86 c4 01
        --> Application;REG_SZ;msimn^@

\$$$PROTO.HIV\Software\Microsoft\Internet Account Manager\Accounts\00000002
LastWrite time: Fri Aug 20 21:16:43 2004
        --> Account Name;REG_SZ;news.dallas.sbcglobal.net^@
        --> Connection Type;REG_DWORD;3
        --> NNTP Server;REG_SZ;news.dallas.sbcglobal.net^@
        --> NNTP User Name;REG_SZ;whoknowsme@sbcglobal.net^@
        --> NNTP Use Sicily;REG_DWORD;0
        --> NNTP Display Name;REG_SZ;Mr Evil^@
        --> NNTP Email Address;REG_SZ;whoknowsme@sbcglobal.net^@
        --> NNTP Prompt for Password;REG_DWORD;0
        --> Last Updated;REG_BINARY;10 db d8 fd fa 86 c4 01

\$$$PROTO.HIV\Software\Microsoft\Internet Account Manager\Accounts\00000001
LastWrite time: Fri Aug 20 21:14:20 2004
        --> Account Name;REG_SZ;pop.sbcglobal.net^@
        --> Connection Type;REG_DWORD;3
        --> POP3 Server;REG_SZ;pop.sbcglobal.net^@
        --> POP3 User Name;REG_SZ;whoknowsme@sbcglobal.net^@
        --> POP3 Use Sicily;REG_DWORD;0
        --> POP3 Prompt for Password;REG_DWORD;0
        --> SMTP Server;REG_SZ;smtp.sbcglobal.net^@
        --> SMTP Display Name;REG_SZ;Mr Evil^@
        --> SMTP Email Address;REG_SZ;whoknowsme@sbcglobal.net^@
```

Ces informations se retrouvent aussi dans le fichier `Program Files/Agent/Data/AGENT.INI` :  

```ini
[Profile]
FullName="Mr Evil"
EMailAddress="whoknowsme@sbcglobal.net"
UserName="whoknowsme@sbcglobal.net"
Password="84106D94696F"
SMTPUserName="whoknowsme@sbcglobal.net"
SMTPPassword="84106D94696F"

[Servers]
NewsServer="news.dallas.sbcglobal.net"
MailServer="smtp.sbcglobal.net"
POPServer=""
NNTPPort=119
SMTPPort=25
POPPort=110
SMTPServerPort=25
```

## What two installed programs show this information?  

Les entrées dans la BDR correspondent à *Outlook Express*. Le fichier ini correspond au lecteur de news [Forte Agent](http://www.forteinc.com/).  

## List 5 newsgroups that Mr. Evil has subscribed to?  

La liste complète est stockée sous forme de fichiers *Outlook Express* dans le dossier `Documents and Settings/Mr. Evil/Local Settings/Application Data/Identities/{EF086998-1115-4ECD-9B13-9ADC067B4929}/Microsoft/Outlook Express/`. Je ne donnerais que quelques newsgroups :  

```
alt.hacking  
alt.2600  
alt.binaries.hacking.utilities  
alt.dss.hack  
free.binaries.hackers.malicious  
free.binaries.hacking.talentless.troll-haven
```

Fin de la seconde partie. Stay tuned.

*Published January 09 2011 at 17:53*
