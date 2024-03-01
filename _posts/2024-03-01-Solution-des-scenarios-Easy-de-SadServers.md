---
title: "Solution des scénarios Easy de SadServers.com"
tags: [CTF,AdminSys]
---

[SadServers](https://sadservers.com/) change des CTF de hacking classique : ici, vous avez à disposition un serveur cassé (avec une fonction qui ne marche pas comme il faut) et votre mission est de le réparer.

Il n'y a pas forcément de contexte sécurité informatique donc on ne peut même pas qualifier ces challenges de BlueTeam. Ils n'en restent pas moins intéressants.

C'est parti !

## "Saint John": what is writing to this log file?

**Level:** Easy

**Type:** Fix

**Description:** A developer created a testing program that is continuously writing to a log file `/var/log/bad.log` and filling up disk. You can check for example with `tail -f /var/log/bad.log`.  
This program is no longer needed. Find it and terminate it.

**Test:** The log file size doesn't change (within a time interval bigger than the rate of change of the log file).  

The "Check My Solution" button runs the script `/home/admin/agent/check.sh`, which you can see and execute.

**Time to Solve:** 10 minutes.

Comme c'est le premier challenge, on peut commencer par regarder un peu sur quoi on est connecté...

```console
admin@i-0b7815a3563d62e2c:~$ id
uid=1000(admin) gid=1000(admin) groups=1000(admin),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev)
admin@i-0b7815a3563d62e2c:~$ uname -a
Linux i-0b7815a3563d62e2c 5.10.0-25-cloud-amd64 #1 SMP Debian 5.10.191-1 (2023-08-16) x86_64 GNU/Linux
```

Ma première idée est d'utiliser `lsof` qui affiche tous les fichiers ouverts par chaque processus.

```console
admin@i-0b7815a3563d62e2c:~$ lsof | grep bad.log
badlog.py 591                    admin    3w      REG              259,1    10330 265802 /var/log/bad.log
```

On voit un process `badlog.py` de PID 591. On peut voir avec `ps` qu'il est lancé via Python3 :

```
admin        591  0.0  1.7  12508  8260 ?        S    13:03   0:00 /usr/bin/python3 /home/admin/badlog.py
```

Ici une simple recherche sur `badlog` dans la liste des process aurait donc suffit.

Par curiosité, le script est le suivant :

```python
#! /usr/bin/python3
# test logging

import random
import time
from datetime import datetime

with open('/var/log/bad.log', 'w') as f:
    while True:
        r = random.randrange(2147483647)
        print(str(datetime.now()) + ' token: ' + str(r), file=f)
        f.flush()
        time.sleep(0.3)
```

J'utilise `pstree` pour savoir comment il est appelé :

```console
systemd─┬─2*[agetty]
        ├─badlog.py
        ├─chronyd───chronyd
        ├─cron
        ├─dbus-daemon
        ├─2*[dhclient───3*[{dhclient}]]
        ├─gotty─┬─bash───asciinema─┬─asciinema
        │       │                  ├─sh───bash───pstree
        │       │                  └─{asciinema}
        │       └─8*[{gotty}]
        ├─rsyslogd───3*[{rsyslogd}]
        ├─sadagent───4*[{sadagent}]
        ├─sshd
        ├─systemd-journal
        ├─systemd-logind
        ├─systemd-udevd
        └─unattended-upgr
```

On voit que le processus hérite de `systemd`. Pour autant je ne vois pas d'entrées systemd pour le programme.

Il s'avère finalement qu'il s'agit d'une bête tâche crontab lancée au démarrage :

```console
dmin@i-0b7815a3563d62e2c:~$ crontab -l
#Ansible: reboot
@reboot /home/admin/badlog.py &
```

Le cron doit être géré via systemd ce qui expliquait l'affichage plus tôt.

Pour corriger le serveur, il suffit de tuer le process : `kill -15 591`


## "Saskatoon": counting IPs.

**Level:** Easy

**Type:** Do

**Tags:** [bash](https://sadservers.com/tag/bash)  

**Description:** There's a web server access log file at `/home/admin/access.log`. The file consists of one line per HTTP request, with the requester's IP address at the beginning of each line.  

Find what's the IP address that has the most requests in this file (there's no tie; the IP is unique). Write the solution into a file `/home/admin/highestip.txt`. For example, if your solution is "1.2.3.4", you can do `echo "1.2.3.4" > /home/admin/highestip.txt`

**Test:** The SHA1 checksum of the IP address `sha1sum /home/admin/highestip.txt` is 6ef426c40652babc0d081d438b9f353709008e93 (just a way to verify the solution without giving it away.)

**Time to Solve:** 15 minutes.

On va commencer par regarder à quoi correspond le fichier de log :

```console
admin@ip-172-31-27-155:/$ head -5 /home/admin/access.log
83.149.9.216 - - [17/May/2015:10:05:03 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-search.png HTTP/1.1" 200 203023 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
83.149.9.216 - - [17/May/2015:10:05:43 +0000] "GET /presentations/logstash-monitorama-2013/images/kibana-dashboard3.png HTTP/1.1" 200 171717 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
83.149.9.216 - - [17/May/2015:10:05:47 +0000] "GET /presentations/logstash-monitorama-2013/plugin/highlight/highlight.js HTTP/1.1" 200 26185 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
83.149.9.216 - - [17/May/2015:10:05:12 +0000] "GET /presentations/logstash-monitorama-2013/plugin/zoom-js/zoom.js HTTP/1.1" 200 7697 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
83.149.9.216 - - [17/May/2015:10:05:07 +0000] "GET /presentations/logstash-monitorama-2013/plugin/notes/notes.js HTTP/1.1" 200 2892 "http://semicomplete.com/presentations/logstash-monitorama-2013/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
```

On pourrait penser que la commande `cut` suffirait pour obtenir le champ des adresses IPs mais en réalité il y a des whitespaces au début des lignes qui ne se verront pas forcément dans cet article de blog.

Il faut donc utiliser `awk` pour afficher les adresses IP. On va ensuite trier l'output pour rassembler les adresses IPs par groupe puis compter les occurrences avec `uniq -c`.

On obtient alors des lignes avec deux entrées, d'abord un nombre d'apparitions suivi de l'adresse IP correspondante.

Dernière étape : utiliser `sort -nr` qui va classer les résultats par ordre de grandeur numérique (`-n`) mais inversé (`-r`) mettant ainsi l'adresse la plus fréquente en tête. 
```console
admin@ip-172-31-27-155:/$ cat /home/admin/access.log | awk '{ print $1 }' | sort | uniq -c | sort -nr | head
    482 66.249.73.135
    364 46.105.14.53
    357 130.237.218.86
    273 75.97.9.59
    113 50.16.19.13
    102 209.85.238.199
     99 68.180.224.225
     84 100.43.83.137
     83 208.115.111.72
     82 198.46.149.143
```

Ecriture de la solution :
```bash
echo "66.249.73.135" > /home/admin/highestip.txt
```


## "Santiago": Find the secret combination

**Level:** Easy

**Type:** Do

**Tags:** [bash](https://sadservers.com/tag/bash)  

**Description:** Alice the spy has hidden a secret number combination, find it using these instructions:  

1) Find the number of **lines** with occurrences of the string **Alice** (case sensitive) in the **.txt* files in the `/home/admin` directory  
2) There's a file where **Alice** appears exactly once. In that file, in the line after that "Alice" occurrence there's a number.  
   Write both numbers consecutively as one (no new line or spaces) to the solution file. For example if the first number from 1) is *11* and the second *22*, you can do `echo -n 11 > /home/admin/solution; echo 22 >> /home/admin/solution` or `echo "1122" > /home/admin/solution`.

**Test:** Running md5sum /home/admin/solution returns d80e026d18a57b56bddf1d99a8a491f9(just a way to verify the solution without giving it away.)

**Time to Solve:** 15 minutes.

La commande `grep` n'a pas d'option pour chercher des occurrences dans plusieurs fichiers tout en gardant un compteur global des occurrences.

La solution la plus simple semble être de regrouper le contenu des fichiers texte dans un grand bloc (ici via `cat`) et de le passer à `grep`.

Pour la seconde partie (trouver le texte qui n'a qu'une occurrence de _Alice_), `grep` place d'abord le nom du fichier dans l'output avant le nombre d'occurrences.

Ici, on peut tricher en cherchant `:1` dans les résultats. Si cela avait été plus compliqué, on aurait sans doute pû s'en tirer avec `awk`.

```console
admin@i-026aee31b935dc6b3:/$ pwd
/
admin@i-026aee31b935dc6b3:/$ cd home/admin/
admin@i-026aee31b935dc6b3:~$ cat *.txt | grep -c Alice
411
admin@i-026aee31b935dc6b3:~$ grep -c Alice *.txt | sort -n | head
11-0.txt:398
84-0.txt:0
1342-0.txt:1
1661-0.txt:12
admin@i-026aee31b935dc6b3:~$ grep -c Alice *.txt | grep ":1"
1342-0.txt:1
1661-0.txt:12
admin@i-026aee31b935dc6b3:~$ grep Alice 1342-0.txt
                                Alice
admin@i-026aee31b935dc6b3:~$ grep -A1 Alice 1342-0.txt
                                Alice
                        156 CHARING CROSS ROAD
admin@i-026aee31b935dc6b3:~$ echo 411156 > solution
```


## "The Command Line Murders"

**Level:** Easy

**Type:** Do

**Tags:** [bash](https://sadservers.com/tag/bash)  

**Description:** This is the [Command Line Murders](https://github.com/veltman/clmystery) with a small twist as in the solution is different  

Enter the name of the murderer in the file `/home/admin/mysolution`, for example `echo "John Smith" > ~/mysolution`

Hints are at the base of the `/home/admin/clmystery` directory. Enjoy the investigation!

**Test:** `md5sum ~/mysolution` returns 9bba101c7369f49ca890ea96aa242dd5  

(You can always see `/home/admin/agent/check.sh` to see how the solution is evaluated).

**Time to Solve:** 20 minutes.

J'ai mis un peu de temps à résoudre celui-ci, car je ne comprenais pas forcément ce qui était attendu.

Le projet est sur Github et nous conseille de lire le fichier `instructions` :

```console
admin@i-0f0b9a4170ac2cd32:~$ pwd
/home/admin
admin@i-0f0b9a4170ac2cd32:~$ cd clmystery/
admin@i-0f0b9a4170ac2cd32:~/clmystery$ ls
LICENSE.md  cheatsheet.md   hint1  hint3  hint5  hint7  instructions
README.md   cheatsheet.pdf  hint2  hint4  hint6  hint8  mystery
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat instructions 
.OOOOOOOOOOOOOOO @@                                   @@ OOOOOOOOOOOOOOOO.
OOOOOOOOOOOOOOOO @@                                    @@ OOOOOOOOOOOOOOOO
OOOOOOOOOO'''''' @@                                    @@ ```````OOOOOOOOO
OOOOO'' aaa@@@@@@@@@@@@@@@@@@@@"""                   """""""""@@aaaa `OOOO
OOOOO,""""@@@@@@@@@@@@@@""""                                     a@"" OOOA
OOOOOOOOOoooooo,                                            |OOoooooOOOOOS
OOOOOOOOOOOOOOOOo,                                          |OOOOOOOOOOOOC
OOOOOOOOOOOOOOOOOO                                         ,|OOOOOOOOOOOOI
OOOOOOOOOOOOOOOOOO @          THE                          |OOOOOOOOOOOOOI
OOOOOOOOOOOOOOOOO'@           COMMAND                      OOOOOOOOOOOOOOb
OOOOOOOOOOOOOOO'a'            LINE                         |OOOOOOOOOOOOOy
OOOOOOOOOOOOOO''              MURDERS                      aa`OOOOOOOOOOOP
OOOOOOOOOOOOOOb,..                                          `@aa``OOOOOOOh
OOOOOOOOOOOOOOOOOOo                                           `@@@aa OOOOo
OOOOOOOOOOOOOOOOOOO|                                             @@@ OOOOe
OOOOOOOOOOOOOOOOOOO@                               aaaaaaa       @@',OOOOn
OOOOOOOOOOOOOOOOOOO@                        aaa@@@@@@@@""        @@ OOOOOi
OOOOOOOOOO~~ aaaaaa"a                 aaa@@@@@@@@@@""            @@ OOOOOx
OOOOOO aaaa@"""""""" ""            @@@@@@@@@@@@""               @@@|`OOOO'
OOOOOOOo`@@a                  aa@@  @@@@@@@""         a@        @@@@ OOOO9
OOOOOOO'  `@@a               @@a@@   @@""           a@@   a     |@@@ OOOO3
`OOOO'       `@    aa@@       aaa"""          @a        a@     a@@@',OOOO'


There's been a murder in Terminal City, and TCPD needs your help.

To figure out whodunit, go to the 'mystery' subdirectory and start working from there.

You'll want to start by collecting all the clues at the crime scene (the 'crimescene' file).

The officers on the scene are pretty meticulous, so they've written down EVERYTHING in their officer reports.

Fortunately the sergeant went through and marked the real clues with the word "CLUE" in all caps.

If you get stuck, open one of the hint files (from the CL, type 'cat hint1', 'cat hint2', etc.).

To check your answer or find out the solution, open the file 'solution' (from the CL, type 'cat solution').

To get started on how to use the command line, open cheatsheet.md or cheatsheet.pdf (from the command line, you can type 'nano cheatsheet.md').

Don't use a text editor to view any files except these instructions, the cheatsheet, and hints.
```

Le fichier `crimescene` contient vraiment beaucoup d'enregistrement... Il faudra faire le tri.

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ grep -c "Crime Scene Report" mystery/crimescene 
1000
```

Je jette un œil à un premier indice :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat hint1 
Try poking around what's in a file by using the 'head' command:

  head -n 20 people

This will show you the first 20 lines of the 'people' file.
admin@i-0f0b9a4170ac2cd32:~/clmystery$ ls mystery/
crimescene  interviews  memberships  people  streets  vehicles
admin@i-0f0b9a4170ac2cd32:~/clmystery$ head -n 20 mystery/people 
***************
To go to the street someone lives on, use the file
for that street name in the 'streets' subdirectory.
To knock on their door and investigate, read the line number
they live on from the file.  If a line looks like gibberish, you're at the wrong house.
***************

NAME    GENDER  AGE     ADDRESS
Alicia Fuentes  F       48      Walton Street, line 433
Jo-Ting Losev   F       46      Hemenway Street, line 390
Elena Edmonds   F       58      Elmwood Avenue, line 123
Naydene Cabral  F       46      Winthrop Street, line 454
Dato Rosengren  M       22      Mystic Street, line 477
Fernanda Serrano        F       37      Redlands Road, line 392
Emiliano Wenk   M       90      Paulding Street, line 490
Larry Lapin     M       71      Atwill Road, line 298
Jakub Gondos    M       61      Mitchell Street, line 187
Derek Kazanin   M       55      Tennis Road, line 440
Jens Tuimalealiifano    M       83      Rockwood Street, line 205
Nikola Kadhi    M       75      Glenville Avenue, line 226
```

Il y a ce fichier `people` qui nous sera peut-être utile pour la suite.

On a ensuite un fichier pour certaines rues :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ ls mystery/streets/ | head
Abbot_Street
Acton_Street
Addington_Road
Alaric_Street
Albany_Street
Aldworth_Street
Alpine_Street
Andover_Road
Ansonia_Road
Appleton_Road
```

Le contenu de ces fichiers est surprenant :

```
admin@i-0f0b9a4170ac2cd32:~/clmystery$ head mystery/streets/Mystic_Street 
flutist uneasily boatman hollows instituted raindrops 
spits gladiolas institutional legitimately 
exes swearer hesitating eggnog lowers ventilates 
euphoria everglade fussed troopships 
allied gored reemerged thimblefuls ohms loose bothering 
frilly broth minimally illnesses forefathers 
appoint debilitate relate diaries workmanship ploys 
residue quirky nameless transliterating hazings 
spies tumbled finnier snarled tirelessness 
naturalness loiters absorbing suspenders warred
```

Passons à un second indice :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat hint2
Try using grep to search for the clues in the crimescene file:

        grep "CLUE" crimescene
```

Ça y est, on réduit considérablement les pistes :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ grep CLUE mystery/crimescene 
CLUE: Footage from an ATM security camera is blurry but shows that the perpetrator is a tall male, at least 6'.
CLUE: Found a wallet believed to belong to the killer: no ID, just loose change, and membership cards for Rotary_Club, Delta SkyMiles, the local library, and the Museum of Bash History. The cards are totally untraceable and have no name, for some reason.
CLUE: Questioned the barista at the local coffee shop. He said a woman left right before they heard the shots. The name on her latte was Annabel, she had blond spiky hair and a New Zealand accent
```

Dois-je considérer ces "clues" comme véridiques ? Je suppose que oui.

J'ai décidé d'aller fouiller dans les interviews pour voir s'il y avait des données en rapport avec les indices :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ grep -r -l -i zealand mystery/interviews/
mystery/interviews/interview-94126412
mystery/interviews/interview-47246024
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat mystery/interviews/interview-94126412
is, you know. Please, Ma'am, is this New Zealand or Australia?' (and
she tried to curtsey as she spoke--fancy CURTSEYING as you're falling
through the air! Do you think you could manage it?) 'And what an
ignorant little girl she'll think me for asking! No, it'll never do to
ask: perhaps I shall see it written up somewhere.'

Down, down, down. There was nothing else to do, so Alice soon began
talking again. 'Dinah'll miss me very much to-night, I should think!'
(Dinah was the cat.) 'I hope they'll remember her saucer of milk at
tea-time. Dinah my dear! I wish you were down here with me! There are no
mice in the air, I'm afraid, but you might catch a bat, and that's very
like a mouse, you know. But do cats eat bats, I wonder?' And here Alice
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat mystery/interviews/interview-47246024
Ms. Sun has brown hair and is not from New Zealand.  Not the witness from the cafe
```

Le premier fichier semble être du charabia et le second ne nous aide pas puisque le suspect serait un homme et non une femme.

Cherchons des références à _Delta SkyMiles_ :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ grep -i -r -l skymiles mystery/interviews/
mystery/interviews/interview-30259493
mystery/interviews/interview-290346
mystery/interviews/interview-174898
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat mystery/interviews/interview-30259493
Shaw knew the victim, but has never been a SkyMiles member and has a solid alibi for the morning in question.  Not considered a suspect.
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat mystery/interviews/interview-290346
Drives a similar car to the description.

Is a SkyMiles, TCPL, Museum of Bash History, and AAA member.

Bostock is 6' 4", easily tall enough to match the camera footage.

However, upon questioning, Bostock can prove that he was out of town on the morning of the murder, multiple witnesses and credit card transactions confirm.
admin@i-0f0b9a4170ac2cd32:~/clmystery$ cat mystery/interviews/interview-174898
The license plate of Keefe's Mazda matches the witness's description, but the make is wrong, and Keefe has never been a SkyMiles member.  Shouldn't be considered a suspect.
```

OK, donc les deux premiers disculpent des individus sans vraiment nous donner d'infos utiles.

La dernière interview est plus intéressante, car la plaque d'immatriculation de _Keefe_ correspondrait plus ou moins à ce qu'un suspect a vu.

De plus, on apprend que la voiture du suspect n'est pas une `Mazda`.

J'ai décidé de m'orienter vers l'indice des cartes de club :

```console
admin@i-0f0b9a4170ac2cd32:~/clmystery$ ls mystery/memberships/
AAA         Delta_SkyMiles          REI                      Terminal_City_Library
AAdvantage  Fitness_Galaxy          Rotary_Club              United_MileagePlus
Costco      Museum_of_Bash_History  TCSU_Alumni_Association
```

J'affiche les personnes faisant partie des mêmes clubs que le suspect (qui a perdu ses cartes) et je regroupe pour connaître celles qui font partie des 4 clubs à la fois :

```console
admin@i-0a475b23b9de132d8:~/clmystery/mystery/memberships$ cat Delta_SkyMiles Museum_of_Bash_History Rotary_Club Terminal_City_Library | sort | uniq -c | sort -nr | grep 4
      4 Yunwen Crous
      4 Xiaodong Dulko
      4 Sonata Raif
      4 Sofiane Satch
      4 Ravil Ismail
      4 Nenad Blerk
      4 Mclain Rakoczy
      4 Mateusz Yi
      4 Mary Tomashova
      4 Marlene Nicholson
      4 Lisa Edgar
      4 Joshua Fenclova
      4 Joe Germuska
      4 James McNeill
      4 Ibrahima Csima
      4 Gia Mogawane
      4 Georgina Issanova
      4 Erik Plouffe
      4 Emmanuel Hornsey
      4 Elena Costa
      4 Dalibor Vidal
      4 Andrei Masna
      4 Alexander Jiang
      4 Aldo Nicolas
      4 Adrian Lidberg
```

Notre liste de suspects a fortement diminué ! Pour retirer le 4 en début de ligne, on peut utiliser `awk` : `awk '{ print $2,$3 }'`

Maintenant, il faudrait joindre cette liste avec celle du fichier `people`. L'idée est que pour chacun de ces suspects, on veut obtenir l'information du sexe stocké dans le fichier `people`.

L'option `-f` de `grep` permet de recherche des motifs depuis un autre fichier. L'option `-F` permet d'interpréter les motifs comme de simples chaines et non des expressions rationnelles.

```console
admin@i-0a475b23b9de132d8:~/clmystery/mystery$ grep -F -f suspects.txt people | awk '$3 == "M"'
Gia Mogawane    M       37      Trident Street, line 330
Joe Germuska    M       65      Plainfield Street, line 275
Adrian Lidberg  M       26      Fairfax Street, line 107
Joshua Fenclova M       89      Shepard Court, line 214
Sofiane Satch   M       20      Selkirk Road, line 232
Ravil Ismail    M       25      Avila Road, line 210
Ibrahima Csima  M       34      Whitcomb Avenue, line 120
James McNeill   M       34      Farmington Road, line 417
Mclain Rakoczy  M       86      Webber Street, line 329
Dalibor Vidal   M       88      Maple Avenue, line 354
Erik Plouffe    M       87      Yeoman Street, line 177
Mateusz Yi      M       46      President Road, line 294
Alexander Jiang M       88      Blanche Street, line 78
Aldo Nicolas    M       40      Corbet Street, line 400
Emmanuel Hornsey        M       19      Gorham Street, line 295
Andrei Masna    M       58      Stoughton Street, line 301
Nenad Blerk     M       43      Scottfield Road, line 62
```

La commande `awk` a ici servi à ne garder que les hommes.

Maintenant jetons un œil au registre des véhicules. Le fichier contient des blocs de lignes qui ressemble à ceci :

```console
License Plate L337GX9
Make: Mazda
Color: Orange
Owner: John Keefe
Height: 6'4"
Weight: 185 lbs
```

On sait que le suspect a une plaque d'immatriculation qui ressemble à celle de _John Keefe_. On peut supposer que le début est `L337`.

Je fais une recherche sur ce motif et à chaque fois, j'affiche les 5 lignes suivantes (l'enregistrement complet) puis je `grep` sur _Owner_ pour obtenir un nom.

```console
admin@i-0be0b593538501576:~/clmystery/mystery$ grep -A5 L337 vehicles | grep Owner | awk ' { print $2, $3 }'
Katie Park
Mike Bostock
John Keefe
Erika Owens
Matt Waite
Brian Boyer
Al Shaw
Aron Pilhofer
Miranda Mulligan
Heather Billings
Joe Germuska
Jeremy Bowers
Jacqui Maher
```

Je ne suis plus très loin...

Je sais que la voiture n'est pas une Mazda, or les propriétaires sont nombreux (aide de ChatGPT pour ça) :

```console
admin@i-0be0b593538501576:~/clmystery/mystery$ awk '/License Plate/{p=$NF}/Make: Mazda/{lp=p}/Owner:/{if(lp)print $(NF-1), $NF}'  vehicles > mazda_owners.txt
admin@i-0be0b593538501576:~/clmystery/mystery$ wc -l mazda_owners.txt 
5019 mazda_owners.txt
```

Une fois que j'ai fait le tri, il ne reste plus qu'une personne. C'est gagné !

```console
admin@i-0be0b593538501576:~/clmystery/mystery$ grep -F -f males.txt car_owners.txt 
Joe Germuska
```

## "Taipei": Come a-knocking

**Level:** Easy

**Type:** Hack

**Tags:**

**Description:** There is a web server on port :80 protected with [Port Knocking](https://en.wikipedia.org/wiki/Port_knocking). Find the one "knock" needed (sending a SYN to a single port, not a sequence) so you can curl localhost.

**Test:** Executing curl localhost returns a message with md5sum *fe474f8e1c29e9f412ed3b726369ab65*. (Note: the resulting md5sum includes the new line terminator: `echo $(curl localhost)`)

**Time to Solve:** 15 minutes.

Il y a un démon port-knocker sur la machine :

```console
admin@i-0b4255b88a167a9c5:~$ ps aux | grep -i knock
root         620  0.0  0.2   8504  1212 ?        Ss   20:55   0:00 /usr/sbin/knockd -i lo
admin        765  0.0  0.1   5132   700 pts/1    S<+  20:56   0:00 grep -i knock
admin@i-0b4255b88a167a9c5:~$ cat /etc/knockd.conf 
cat: /etc/knockd.conf: Permission denied
admin@i-0b4255b88a167a9c5:~$ ls -al /etc/knockd.conf 
-r--r----- 1 root root 169 Sep 19 00:23 /etc/knockd.conf
admin@i-0b4255b88a167a9c5:~$ sudo -l
Matching Defaults entries for admin on i-0b4255b88a167a9c5:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User admin may run the following commands on i-0b4255b88a167a9c5:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: /sbin/shutdown
```

Bon... On ne peut pas accéder au fichier de configuration et l'autorisation sudo `ALL` ne peut pas se faire sans le mot de passe (qu'on ne connait pas).

J'ai fouillé un peu dans le dossier `agent` (qui sert à l'infra du challenge) mais ça ne m'a pas donné plus d'idées.
```console
admin@i-0b4255b88a167a9c5:~$ cd agent/
admin@i-0b4255b88a167a9c5:~/agent$ ls
check.sh  sadagent  sadagent.txt
admin@i-0b4255b88a167a9c5:~/agent$ file *
check.sh:     Bourne-Again shell script, ASCII text executable
sadagent:     ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, Go BuildID=H6A8cVluPFUvaNojVwMi/C5t-5rNiA5GJLWeSm5Qz/KXfivG_lDFnrqPGrWEJo/K_OQEFevUZEPr4lPEnoe, not stripped
sadagent.txt: empty
admin@i-0b4255b88a167a9c5:~/agent$ cat check.sh 
#!/bin/bash
res=$(curl -s localhost)
res=$(echo $res|tr -d '\r')
checksum=$(echo $res| md5sum| awk '{print $1}')

if [[ "$checksum" = "fe474f8e1c29e9f412ed3b726369ab65" ]]
then
  echo -n "OK"
else
  echo -n "NO"
fi
```

Connaissant déjà les port-knockers via les CTF de hacking j'ai lancé un bête scan de port à deux reprises :

```console
admin@i-0b4255b88a167a9c5:~/agent$ nmap -p- -T5 localhost
Starting Nmap 7.80 ( https://nmap.org ) at 2024-02-27 20:57 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000076s latency).
Not shown: 65532 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
6767/tcp open  bmc-perf-agent
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 1.09 seconds
admin@i-0b4255b88a167a9c5:~/agent$ nmap -p- -T5 localhost
Starting Nmap 7.80 ( https://nmap.org ) at 2024-02-27 20:57 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000055s latency).
Not shown: 65531 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
6767/tcp open  bmc-perf-agent
8080/tcp open  http-proxy

Nmap done: 1 IP address (1 host up) scanned in 2.00 seconds
admin@i-0b4255b88a167a9c5:~/agent$ ./check.sh 
OK
```

On voit qu'avec un peu de chances Nmap trouve la bonne séquence des ports à taper.


## "Lhasa": Easy Math

**Level:** Easy

**Type:** Do

**Tags:** [bash](https://sadservers.com/tag/bash)  

**Description:** There's a file `/home/admin/scores.txt` with two columns (imagine the first number is a counter and the second one is a test score for example).  

Find the average (more precisely; the arithmetic mean: sum of numbers divided by how many numbers are there) of the numbers in the second column (find the average score).  

Use exaclty two digits to the right of the decimal point. i. e., **use exaclty two "decimal digits" without any rounding**. Eg: if average = 21.349 , the solution is 21.34. If average = 33.1 , the solution is 33.10.  

Save the solution in the `/home/admin/solution` file, for example: `echo "123.45" > ~/solution`  

Tip: There's bc, Python3, Golang and sqlite3 installed in this VM.

**Test:** `md5sum /home/admin/solution` returns 6d4832eb963012f6d8a71a60fac77168 solution

**Time to Solve:** 15 minutes.

À quoi ressemble de fichier des scores avec ses lignes numérotées ?

```console
admin@i-048d0cb2e8575821d:~$ head scores.txt 
1 7.4
2 0.4
3 1.6
4 6.2
5 7.6
6 7.7
7 5.6
8 4.4
9 8.0
10 7.0
```

Avec mon expérience en Python ça n'a pas duré longtemps :

```python
admin@i-048d0cb2e8575821d:~$ cat calc.py 
with open("scores.txt") as fd:
    total = 0
    count = 0 
    for line in fd:
        _, value = line.strip().split()
        value = float(value)
        total += value
        count += 1

    print(f"{total/count:.02f}")
admin@i-048d0cb2e8575821d:~$ python3 calc.py 
5.20
```


## "Bucharest": Connecting to Postgres

**Level:** Easy

**Type:** Fix

**Tags:** [postgres](https://sadservers.com/tag/postgres)  

**Description:** A web application relies on the PostgreSQL 13 database present on this server. However, the connection to the database is not working. Your task is to identify and resolve the issue causing this connection failure. The application connects to a database named *app1* with the user *app1user* and the password *app1user*.  

Credit [PykPyky](https://twitter.com/PykPyky)

**Test:** Running `PGPASSWORD=app1user psql -h 127.0.0.1 -d app1 -U app1user -c '\q'` succeeds (does not return an error).

**Time to Solve:** 10 minutes.

Commençons par reproduire l'erreur :

```console
admin@i-0c9c6a4d86d5f67b1:~$ PGPASSWORD=app1user psql -h 127.0.0.1 -d app1 -U app1user -c '\q'
psql: error: FATAL:  pg_hba.conf rejects connection for host "127.0.0.1", user "app1user", database "app1", SSL on
FATAL:  pg_hba.conf rejects connection for host "127.0.0.1", user "app1user", database "app1", SSL off
```

C'est déjà plus explicite : un fichier de configuration est à l'origine du problème.

```console
admin@i-0c9c6a4d86d5f67b1:~$ find /etc/ -name pg_hba.conf 2> /dev/null 
/etc/postgresql/13/main/pg_hba.conf
admin@i-0c9c6a4d86d5f67b1:~$ cat /etc/postgresql/13/main/pg_hba.conf
cat: /etc/postgresql/13/main/pg_hba.conf: Permission denied
admin@i-0c9c6a4d86d5f67b1:~$ ls -al /etc/postgresql/13/main/pg_hba.conf
-rw-r----- 1 postgres postgres 5075 Nov 25 18:05 /etc/postgresql/13/main/pg_hba.conf
admin@i-0c9c6a4d86d5f67b1:~$ sudo -l
Matching Defaults entries for admin on i-0c9c6a4d86d5f67b1:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User admin may run the following commands on i-0c9c6a4d86d5f67b1:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
    (ALL) NOPASSWD: ALL
    (ALL) NOPASSWD: ALL
    (ALL) NOPASSWD: /sbin/shutdown
```

Ici, on a suffisamment de droits pour être qui l'on souhaite.

```console
admin@i-0c9c6a4d86d5f67b1:~$ sudo -u postgres bash
postgres@i-0c9c6a4d86d5f67b1:/home/admin$ cat /etc/postgresql/13/main/pg_hba.conf
# PostgreSQL Client Authentication Configuration File
# ===================================================
#
# Refer to the "Client Authentication" section in the PostgreSQL
# documentation for a complete description of this file.  A short
# synopsis follows.
#
# This file controls: which hosts are allowed to connect, how clients
# are authenticated, which PostgreSQL user names they can use, which
# databases they can access.  Records take one of these forms:
#
# local         DATABASE  USER  METHOD  [OPTIONS]
# host          DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
# hostssl       DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
# hostnossl     DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
# hostgssenc    DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
# hostnogssenc  DATABASE  USER  ADDRESS  METHOD  [OPTIONS]
#
# (The uppercase items must be replaced by actual values.)
#
# The first field is the connection type: "local" is a Unix-domain
# socket, "host" is either a plain or SSL-encrypted TCP/IP socket,
# "hostssl" is an SSL-encrypted TCP/IP socket, and "hostnossl" is a
# non-SSL TCP/IP socket.  Similarly, "hostgssenc" uses a
# GSSAPI-encrypted TCP/IP socket, while "hostnogssenc" uses a
# non-GSSAPI socket.
#
# DATABASE can be "all", "sameuser", "samerole", "replication", a
# database name, or a comma-separated list thereof. The "all"
# keyword does not match "replication". Access to replication
# must be enabled in a separate record (see example below).
#
# USER can be "all", a user name, a group name prefixed with "+", or a
# comma-separated list thereof.  In both the DATABASE and USER fields
# you can also write a file name prefixed with "@" to include names
# from a separate file.
#
# ADDRESS specifies the set of hosts the record matches.  It can be a
# host name, or it is made up of an IP address and a CIDR mask that is
# an integer (between 0 and 32 (IPv4) or 128 (IPv6) inclusive) that
# specifies the number of significant bits in the mask.  A host name
# that starts with a dot (.) matches a suffix of the actual host name.
# Alternatively, you can write an IP address and netmask in separate
# columns to specify the set of hosts.  Instead of a CIDR-address, you
# can write "samehost" to match any of the server's own IP addresses,
# or "samenet" to match any address in any subnet that the server is
# directly connected to.
#
# METHOD can be "trust", "reject", "md5", "password", "scram-sha-256",
# "gss", "sspi", "ident", "peer", "pam", "ldap", "radius" or "cert".
# Note that "password" sends passwords in clear text; "md5" or
# "scram-sha-256" are preferred since they send encrypted passwords.
#
# OPTIONS are a set of options for the authentication in the format
# NAME=VALUE.  The available options depend on the different
# authentication methods -- refer to the "Client Authentication"
# section in the documentation for a list of which options are
# available for which authentication methods.
#
# Database and user names containing spaces, commas, quotes and other
# special characters must be quoted.  Quoting one of the keywords
# "all", "sameuser", "samerole" or "replication" makes the name lose
# its special character, and just match a database or username with
# that name.
#
# This file is read on server startup and when the server receives a
# SIGHUP signal.  If you edit the file on a running system, you have to
# SIGHUP the server for the changes to take effect, run "pg_ctl reload",
# or execute "SELECT pg_reload_conf()".
#
# Put your actual configuration here
# ----------------------------------
#
# If you want to allow non-local connections, you need to add more
# "host" records.  In that case you will also need to make PostgreSQL
# listen on a non-local interface via the listen_addresses
# configuration parameter, or via the -i or -h command line switches.

# DO NOT DISABLE!
# If you change this first entry you will need to make sure that the
# database superuser can access the database using some other method.
# Noninteractive access to all databases is required during automatic
# maintenance (custom daily cronjobs, replication, and similar tasks).
#
# Database administrative login by Unix domain socket
local   all             postgres                                peer
host    all             all             all                     reject
host    all             all             all                     reject

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
```

Il faut ajouter une entrée pour autoriser l'utilisateur `app1user`. Les règles sont ordonnées donc on placera la ligne suivante avant les autres :

```
host    app1    app1user    127.0.0.1/32     md5
```

Je redémarre `postgresql` et c'est gagné :

```console
admin@i-0348bdb7476455470:~$ sudo vi /etc/postgresql/13/main/pg_hba.conf
admin@i-0348bdb7476455470:~$ sudo systemctl restart postgresql
admin@i-0348bdb7476455470:~$ PGPASSWORD=app1user psql -h 127.0.0.1 -d app1 -U app1user -c '\q'
```


## "Bilbao": Basic Kubernetes Problems

**Level:** Easy

**Type:** Fix

**Tags:** [kubernetes](https://sadservers.com/tag/kubernetes)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There's a Kubernetes Deployment with an Nginx pod and a Load Balancer declared in the manifest.yml file. The pod is not coming up. Fix it so that you can access the Nginx container through the Load Balancer.  

There's no "sudo" (root) access.

**Test:** Running `curl 10.43.216.196` returns the default Nginx Welcome page.  

See `/home/admin/agent/check.sh` for the test that "Check My Solution" runs.

**Time to Solve:** 10 minutes.

Mon utilisation habituelle de Kubernetes se résume aux commandes `kubectl get`, `describe` et `logs` mais regardons.

Ici, on a le yaml qui décrit le job à déployer :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: localhost:5000/nginx
        ports:
        - containerPort: 80
        resources:
          limits:
            memory: 2000Mi
            cpu: 100m
          requests:
            cpu: 100m
            memory: 2000Mi
      nodeSelector:
        disk: ssd

---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  clusterIP: 10.43.216.196
  type: LoadBalancer
```

Utilisons `get` pour obtenir le nom du pod et `describe` pour voir ce qui ne va pas.

```console
admin@i-099ad03c5c74d5c45:~$ kubectl get pods
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-67699598cc-zrj6f   0/1     Pending   0          40d
admin@i-099ad03c5c74d5c45:~$ kubectl describe pod nginx-deployment-67699598cc-zrj6f
Name:             nginx-deployment-67699598cc-zrj6f
Namespace:        default
Priority:         0
Service Account:  default
Node:             <none>
Labels:           app=nginx
                  pod-template-hash=67699598cc
Annotations:      <none>
Status:           Pending
IP:               
IPs:              <none>
Controlled By:    ReplicaSet/nginx-deployment-67699598cc
Containers:
  nginx:
    Image:      localhost:5000/nginx
    Port:       80/TCP
    Host Port:  0/TCP
    Limits:
      cpu:     100m
      memory:  2000Mi
    Requests:
      cpu:        100m
      memory:     2000Mi
    Environment:  <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-mslhc (ro)
Conditions:
  Type           Status
  PodScheduled   False 
Volumes:
  kube-api-access-mslhc:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   Guaranteed
Node-Selectors:              disk=ssd
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  40d   default-scheduler  0/2 nodes are available: 1 node(s) didn't match Pod's node affinity/selector, 1 node(s) had untolerated taint {node.kubernetes.io/unreachable: }. preemption: 0/2 nodes are available: 2 Preemption is not helpful for scheduling..
  Warning  FailedScheduling  63s   default-scheduler  0/2 nodes are available: 1 node(s) didn't match Pod's node affinity/selector, 1 node(s) had untolerated taint {node.kubernetes.io/unreachable: }. preemption: 0/2 nodes are available: 2 Preemption is not helpful for scheduling..
```

Ok donc il y a un problème de sélection de node ainsi qu'un problème de _taint_.

De la même façon, je peux lister les nodes. L'une est en carafe.

```console
admin@i-099ad03c5c74d5c45:~$ kubectl get nodes
NAME                  STATUS     ROLES                  AGE   VERSION
node1                 Ready      control-plane,master   40d   v1.28.5+k3s1
i-02f8e6680f7d5e616   NotReady   control-plane,master   40d   v1.28.5+k3s1
```

La voici :

```console
admin@i-099ad03c5c74d5c45:~$ kubectl describe node i-02f8e6680f7d5e616
Name:               i-02f8e6680f7d5e616
Roles:              control-plane,master
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/instance-type=k3s
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=i-02f8e6680f7d5e616
                    kubernetes.io/os=linux
                    node-role.kubernetes.io/control-plane=true
                    node-role.kubernetes.io/master=true
                    node.kubernetes.io/instance-type=k3s
Annotations:        alpha.kubernetes.io/provided-node-ip: 10.0.0.196
                    k3s.io/hostname: i-02f8e6680f7d5e616
                    k3s.io/internal-ip: 10.0.0.196
                    k3s.io/node-args: ["server","--write-kubeconfig-mode","644"]
                    k3s.io/node-config-hash: ABCLQJAJLOKCGAA6UI3NDL4N4IX35T27GK2KPBZOOOHX3TJTLKEA====
                    k3s.io/node-env: {"K3S_DATA_DIR":"/var/lib/rancher/k3s/data/28f7e87eba734b7f7731dc900e2c84e0e98ce869f3dcf57f65dc7bbb80e12e56"}
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 17 Jan 2024 23:50:25 +0000
Taints:             node.kubernetes.io/unreachable:NoExecute
                    node.kubernetes.io/unreachable:NoSchedule
Unschedulable:      false
Lease:
  HolderIdentity:  i-02f8e6680f7d5e616
  AcquireTime:     <unset>
  RenewTime:       Wed, 17 Jan 2024 23:50:25 +0000
Conditions:
  Type             Status    LastHeartbeatTime                 LastTransitionTime                Reason              Message
  ----             ------    -----------------                 ------------------                ------              -------
  MemoryPressure   Unknown   Wed, 17 Jan 2024 23:50:26 +0000   Wed, 17 Jan 2024 23:51:30 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
  DiskPressure     Unknown   Wed, 17 Jan 2024 23:50:26 +0000   Wed, 17 Jan 2024 23:51:30 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
  PIDPressure      Unknown   Wed, 17 Jan 2024 23:50:26 +0000   Wed, 17 Jan 2024 23:51:30 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
  Ready            Unknown   Wed, 17 Jan 2024 23:50:26 +0000   Wed, 17 Jan 2024 23:51:30 +0000   NodeStatusUnknown   Kubelet stopped posting node status.
Addresses:
  InternalIP:  10.0.0.196
  Hostname:    i-02f8e6680f7d5e616
Capacity:
  cpu:                2
  ephemeral-storage:  8026128Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             2000036Ki
  pods:               110
Allocatable:
  cpu:                2
  ephemeral-storage:  7807817313
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             2000036Ki
  pods:               110
System Info:
  Machine ID:                 ec26942be8219bc22967aa0256120fca
  System UUID:                ec2e4d56-bd40-5b59-d79b-0f65d3a03d96
  Boot ID:                    52d12eb0-e5c5-41df-a59e-2be237dac240
  Kernel Version:             5.10.0-8-cloud-amd64
  OS Image:                   Debian GNU/Linux 11 (bullseye)
  Operating System:           linux
  Architecture:               amd64
  Container Runtime Version:  containerd://1.7.11-k3s2
  Kubelet Version:            v1.28.5+k3s1
  Kube-Proxy Version:         v1.28.5+k3s1
PodCIDR:                      10.42.0.0/24
PodCIDRs:                     10.42.0.0/24
ProviderID:                   k3s://i-02f8e6680f7d5e616
Non-terminated Pods:          (2 in total)
  Namespace                   Name                                       CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                                       ------------  ----------  ---------------  -------------  ---
  kube-system                 local-path-provisioner-84db5d44d9-qrwpv    0 (0%)        0 (0%)      0 (0%)           0 (0%)         40d
  kube-system                 helm-install-traefik-crd-fdqdr             0 (0%)        0 (0%)      0 (0%)           0 (0%)         40d
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests  Limits
  --------           --------  ------
  cpu                0 (0%)    0 (0%)
  memory             0 (0%)    0 (0%)
  ephemeral-storage  0 (0%)    0 (0%)
  hugepages-1Gi      0 (0%)    0 (0%)
  hugepages-2Mi      0 (0%)    0 (0%)
Events:
  Type     Reason                          Age                From                   Message
  ----     ------                          ----               ----                   -------
  Normal   Starting                        40d                kubelet                Starting kubelet.
  Warning  InvalidDiskCapacity             40d                kubelet                invalid capacity 0 on image filesystem
  Normal   NodeHasSufficientMemory         40d (x2 over 40d)  kubelet                Node i-02f8e6680f7d5e616 status is now: NodeHasSufficientMemory
  Normal   NodeHasNoDiskPressure           40d (x2 over 40d)  kubelet                Node i-02f8e6680f7d5e616 status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientPID            40d (x2 over 40d)  kubelet                Node i-02f8e6680f7d5e616 status is now: NodeHasSufficientPID
  Normal   NodeReady                       40d                kubelet                Node i-02f8e6680f7d5e616 status is now: NodeReady
  Normal   NodeAllocatableEnforced         40d                kubelet                Updated Node Allocatable limit across pods
  Normal   NodePasswordValidationComplete  40d                k3s-supervisor         Deferred node password secret validation complete
  Normal   Synced                          40d                cloud-node-controller  Node synced successfully
  Normal   RegisteredNode                  40d                node-controller        Node i-02f8e6680f7d5e616 event: Registered Node i-02f8e6680f7d5e616 in Controller
  Normal   NodeNotReady                    40d                node-controller        Node i-02f8e6680f7d5e616 status is now: NodeNotReady
  Normal   RegisteredNode                  5m26s              node-controller        Node i-02f8e6680f7d5e616 event: Registered Node i-02f8e6680f7d5e616 in Controller
```

Voici celle qui est ready :

```console
admin@i-02e80a7efdd67d33b:~$ kubectl describe node node1
Name:               node1
Roles:              control-plane,master
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/instance-type=k3s
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=node1
                    kubernetes.io/os=linux
                    node-role.kubernetes.io/control-plane=true
                    node-role.kubernetes.io/master=true
                    node.kubernetes.io/instance-type=k3s
Annotations:        alpha.kubernetes.io/provided-node-ip: 172.31.39.41
                    flannel.alpha.coreos.com/backend-data: {"VNI":1,"VtepMAC":"72:34:28:03:a9:d4"}
                    flannel.alpha.coreos.com/backend-type: vxlan
                    flannel.alpha.coreos.com/kube-subnet-manager: true
                    flannel.alpha.coreos.com/public-ip: 172.31.39.41
                    k3s.io/hostname: node1
                    k3s.io/internal-ip: 172.31.39.41
                    k3s.io/node-args: ["server","--write-kubeconfig-mode","644"]
                    k3s.io/node-config-hash: PJ5JHSN6NTUVCSNRPYERYVG3GEF66BBA5GLBEFMTX2XODC44JGOA====
                    k3s.io/node-env:
                      {"K3S_DATA_DIR":"/var/lib/rancher/k3s/data/28f7e87eba734b7f7731dc900e2c84e0e98ce869f3dcf57f65dc7bbb80e12e56","K3S_NODE_NAME":"node1"}
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 17 Jan 2024 23:50:35 +0000
Taints:             <none>
Unschedulable:      false
Lease:
  HolderIdentity:  node1
  AcquireTime:     <unset>
  RenewTime:       Tue, 27 Feb 2024 21:45:12 +0000
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Tue, 27 Feb 2024 21:44:53 +0000   Wed, 17 Jan 2024 23:50:35 +0000   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Tue, 27 Feb 2024 21:44:53 +0000   Wed, 17 Jan 2024 23:50:35 +0000   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Tue, 27 Feb 2024 21:44:53 +0000   Wed, 17 Jan 2024 23:50:35 +0000   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Tue, 27 Feb 2024 21:44:53 +0000   Tue, 27 Feb 2024 21:44:53 +0000   KubeletReady                 kubelet is posting ready status. AppArmor enabled
Addresses:
  InternalIP:  172.31.39.41
  Hostname:    node1
Capacity:
  cpu:                2
  ephemeral-storage:  8026128Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             2000036Ki
  pods:               110
Allocatable:
  cpu:                2
  ephemeral-storage:  7807817313
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             2000036Ki
  pods:               110
System Info:
  Machine ID:                 ec26942be8219bc22967aa0256120fca
  System UUID:                ec228431-e34e-eb22-1e9e-ff7028b1b085
  Boot ID:                    267eeb9d-1c01-4f0b-89ed-898cf68fd6d4
  Kernel Version:             5.10.0-8-cloud-amd64
  OS Image:                   Debian GNU/Linux 11 (bullseye)
  Operating System:           linux
  Architecture:               amd64
  Container Runtime Version:  containerd://1.7.11-k3s2
  Kubelet Version:            v1.28.5+k3s1
  Kube-Proxy Version:         v1.28.5+k3s1
PodCIDR:                      10.42.1.0/24
PodCIDRs:                     10.42.1.0/24
ProviderID:                   k3s://node1
Non-terminated Pods:          (5 in total)
  Namespace                   Name                                       CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                                       ------------  ----------  ---------------  -------------  ---
  kube-system                 svclb-nginx-service-97900f05-kk2hx         0 (0%)        0 (0%)      0 (0%)           0 (0%)         40d
  kube-system                 local-path-provisioner-84db5d44d9-mg5tr    0 (0%)        0 (0%)      0 (0%)           0 (0%)         40d
  kube-system                 metrics-server-67c658944b-pxdx7            100m (5%)     0 (0%)      70Mi (3%)        0 (0%)         40d
  kube-system                 traefik-f4564c4f4-mrj46                    0 (0%)        0 (0%)      0 (0%)           0 (0%)         40d
  kube-system                 coredns-6799fbcd5-84cwc                    100m (5%)     0 (0%)      70Mi (3%)        170Mi (8%)     40d
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                200m (10%)  0 (0%)
  memory             140Mi (7%)  170Mi (8%)
  ephemeral-storage  0 (0%)      0 (0%)
  hugepages-1Gi      0 (0%)      0 (0%)
  hugepages-2Mi      0 (0%)      0 (0%)
Events:
  Type     Reason                          Age                From                   Message
  ----     ------                          ----               ----                   -------
  Normal   Starting                        40d                kube-proxy             
  Normal   Starting                        28s                kube-proxy             
  Normal   NodeHasSufficientMemory         40d (x2 over 40d)  kubelet                Node node1 status is now: NodeHasSufficientMemory
  Normal   Starting                        40d                kubelet                Starting kubelet.
  Warning  InvalidDiskCapacity             40d                kubelet                invalid capacity 0 on image filesystem
  Normal   NodeHasNoDiskPressure           40d (x2 over 40d)  kubelet                Node node1 status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientPID            40d (x2 over 40d)  kubelet                Node node1 status is now: NodeHasSufficientPID
  Normal   NodeAllocatableEnforced         40d                kubelet                Updated Node Allocatable limit across pods
  Normal   NodeReady                       40d                kubelet                Node node1 status is now: NodeReady
  Normal   Synced                          40d                cloud-node-controller  Node synced successfully
  Normal   NodePasswordValidationComplete  40d                k3s-supervisor         Deferred node password secret validation complete
  Normal   RegisteredNode                  40d                node-controller        Node node1 event: Registered Node node1 in Controller
  Normal   Starting                        36s                kubelet                Starting kubelet.
  Warning  InvalidDiskCapacity             35s                kubelet                invalid capacity 0 on image filesystem
  Normal   NodeHasSufficientMemory         35s                kubelet                Node node1 status is now: NodeHasSufficientMemory
  Normal   NodeHasNoDiskPressure           35s                kubelet                Node node1 status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientPID            35s                kubelet                Node node1 status is now: NodeHasSufficientPID
  Warning  Rebooted                        35s                kubelet                Node node1 has been rebooted, boot id: 267eeb9d-1c01-4f0b-89ed-898cf68fd6d4
  Normal   NodeNotReady                    35s                kubelet                Node node1 status is now: NodeNotReady
  Normal   NodeAllocatableEnforced         34s                kubelet                Updated Node Allocatable limit across pods
  Normal   NodePasswordValidationComplete  28s                k3s-supervisor         Deferred node password secret validation complete
  Normal   NodeReady                       24s                kubelet                Node node1 status is now: NodeReady
  Normal   RegisteredNode                  19s                node-controller        Node node1 event: Registered Node node1 in Controller
```

De toute façon, aucune des deux n'est utilisée par le pod. J'ai d'abord retiré le _taint_, je ne sais pas si ça a eu un effet quelconque.

```console
admin@i-02e80a7efdd67d33b:~$ kubectl taint nodes i-02f8e6680f7d5e616 node.kubernetes.io/unreachable-
node/i-02f8e6680f7d5e616 untainted
```

Ensuite le pod avait la règle suivante pour la sélection des nodes :

```yaml
Node-Selectors:              disk=ssd
```

Il y a incompatibilité avec les nodes donc soit on change la règle du pod, soit on change les nodes. C'est ce que j'ai fait :

```console
kubectl label nodes i-02f8e6680f7d5e616 disk=ssd
```

Il faut ensuite supprimer le pod qui ne parviendra pas à se déployer dans l'état.

```console
admin@i-0d7e9ff48700a48e5:~$ kubectl delete pod nginx-deployment-67699598cc-zrj6f
pod "nginx-deployment-67699598cc-zrj6f" deleted
admin@i-0d7e9ff48700a48e5:~$ kubectl get pods
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-67699598cc-ldcf2   0/1     Pending   0          4s
```

Un nouveau pod a été automatiquement créé, il est en état _pending_.

```console
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  42s   default-scheduler  0/2 nodes are available: 1 Insufficient memory, 1 node(s) had untolerated taint {node.kubernetes.io/unreachable: }. preemption: 0/2 nodes are available: 1 No preemption victims found for incoming pod, 1 Preemption is not helpful for scheduling..
```

Maintenant il rale car il n'obtient pas la quantité de mémoire demandée. On va corriger ses exigences à la baisse en éditant le _yaml_ puis en l'appliquant.  

```console
admin@i-0d7e9ff48700a48e5:~$ vi manifest.yml 
admin@i-0d7e9ff48700a48e5:~$ kubectl apply -f manifest.yml
deployment.apps/nginx-deployment configured
service/nginx-service unchanged
admin@i-0d7e9ff48700a48e5:~$ kubectl get pods
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-7449df8bfc-5dn94   1/1     Running   0          6s
```

C'est finit pour les challenges _Easy_.
