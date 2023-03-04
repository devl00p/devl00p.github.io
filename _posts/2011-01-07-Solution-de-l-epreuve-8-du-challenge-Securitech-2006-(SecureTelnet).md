---
title: "Solution de l'épreuve 8 du challenge Securitech 2006 (SecureTelnet)"
tags: [CTF, Cryptographie]
---

**NB : L'article traitant d'un cas spécifique de cryptanalyse, il risque d'être difficile à comprendre pour des non-initiés.**

C'est avec un décalage non négligeable que je rédige cette solution, mais comme les solutions officielles ne sont pas disponibles sur [le site du challenge](http://www.challenge-securitech.com/), mieux vaut tard que jamais.  
Il faut dire qu'un bon nombre de solutions ont été faites sur le net par les participants (voir [ma solution de la partie inforensique]({% link _posts/2011-01-05-Solution-de-l-epreuve-forensics-du-challenge-Securitech-2006.md %}).)  

Comme toutes les épreuves de l'édition 2006 de ce concours de sécurité informatique, on ne disposait pas d'un énoncé, mais uniquement d'[un fichier au format pcap](/assets/data/ch08_trace.zip) (tcpdump, ethereal...) avec quelques trames réseau. Le participant devait alors trouver où était la vulnérabilité et comment l'exploiter.  

La page de ressources mettait aussi à disposition un exécutable Linux (ELF) nommé `SecureTelnet`. [Le binaire](/assets/data/securetelnet.zip) n'étant pas [strippé](http://unixhelp.ed.ac.uk/CGI/man-cgi?strip) son analyse ne devrait pas être trop difficile.  

Les trames réseau correspondent à une communication entre deux machines, le client (`192.168.1.14`) et le serveur (`193.168.50.86`) qui écoute sur le port 2323.  

Avec la fonctionnalité *"Follow TCP Stream"* d'Ethereal on se rend compte très vite que la communication se fait uniquement à l'aide de caractères imprimables (j'ai rajouté les signes inférieur et supérieur pour marquer le sens de la communication, la première ligne émanant du serveur) :  

```
< Secure Telnet 1.0
> VVNFUiBhbGljZQo=
< VVNFUiBhbGljZQo=
> QUxFQQo=
< QUxFQSD4A7SPYPK/qZVDzskNohowqhLukG6ZyBfIx5/1FZf+DpqynvulXaQ7oHIFrhU=
> Q0hBTExFTkdFII/JtptN9pii+JcTxjNk/jU=
< TUVTU0FHRSBCcmF2bywgcG91ciB2YWxpZGVyIGVudHJleiA6IFZBTElETklWTyBbdm90cmUgcHNldWRvXSBbdm90cmUgZW1haWxdCg==
```

En dehors de l'invite du serveur qui est en clair, on reconnait facilement l'encodage base64 par le jeu de caractères utilisé et l'utilisation du caractère `=` en fin de ligne.  

Une fois décodé la conversation devient :

```
> USER alice\n
< USER alice\n
> ALEA\n
< ALEA \xf8\x03\xb4\x8f`\xf2\xbf\xa9\x95C\xce\xc9\r\xa2\x1a0\xaa\x12\xee\x90n\x99\xc8\x17\xc8\xc7\x9f\xf5\x15\x97\xfe\x0e\x9a\xb2 \x9e\xfb\xa5]\xa4;\xa0r\x05\xae\x15
> CHALLENGE \x8f\xc9\xb6\x9bM\xf6\x98\xa2\xf8\x97\x13\xc63d\xfe5
< MESSAGE Bravo, pour valider entrez : VALIDNIVO [votre pseudo] [votre email]\n
```

J'ai utilisé une notation type C pour les caractères non-imprimables (`\xNN`).  

Le principe est le suivant : le client envoie le nom d'utilisateur au serveur. Ce dernier confirme en renvoyant la commande. Le client demande alors au serveur de lui envoyer une suite d'octets aléatoire. À partir de cet aléa le client crypte son mot de passe (avec d'éventuelles informations supplémentaires) et le renvoie au serveur (commande `CHALLENGE`). Le dernier renvoi un message de félicitation si l'utilisateur s'est authentifié ou un message d'erreur.  
Les différents messages d'erreurs existants sont :  

* `MESSAGE Mot de passe invalide\n` (TUVTU0FHRSBNb3QgZGUgcGFzc2UgaW52YWxpZGUK)
* `MESSAGE Commande non reconnue\n` (TUVTU0FHRSBDb21tYW5kZSBub24gcmVjb25udWUK)
* `MESSAGE Utilisateur inconnu\n` (TUVTU0FHRSBVdGlsaXNhdGV1ciBpbmNvbm51Cg==)

A ce stade on se dit qu'il va y avoir de la crypto !  

Après avoir récupéré quelques correspondances aléa/challenge et s'être brainstormé sur les suites d'octets, on se dit qu'il va y avoir ausi de l'analyse de binaire :p  

J'utilise [HT Editor](http://hte.sourceforge.net/) pour travailler sur le fichier. Un coup de `F6` pour passer en mode *elf/image* puis direction la fonction `main()`. Ce désassembleur est très pratique et permet de placer des commentaires (touche dièse). En revanche il ne résout pas les noms des fonctions de la libc mais affiche des noms comme `wrapper_804b79c_8048868`.  

J'utilise *gdb* en parallèle pour comprendre le fonctionnement des fonctions (les commandes `b`, `c`, `si`, `n`, `x`, `i` sont vos amies).  

Je ne détaillerais pas la vérification du nombre d'arguments passés au programme, l'ouverture d'un socket ou l'affichage d'infos sur la sortie standard.  
Les fonctions propres à l'exécutable (`recvData`, `extraitCommande`, `extraitArgument`, `sendBin`...) redirigent l'exécution du programme en fonction des commandes tapées par l'utilisateur et des réponses du serveur.  

Arrivé à un `call challenge` il est clair que toute la difficulté est concentrée dans cette fonction. Cette dernière aurait la déclaration suivante en C :  

```c
char * challenge(char *user, char *alea, char *pass);  
```

![securitech challenge 8 asm](/assets/img/securitech8_1call.jpg)

Une fois entré dans la fonction, les paramètres sont aux adresses suivantes :  

```
user : ebp+8  
alea : ebp+12 (ebp+0ch)  
pass : ebp+16 (ebp+10h)
```  

76 octets sont réservés sur la pile pour les variables locales (`sub esp, 4ch`)  

Un espace mémoire de taille = `strlen("CHALLENGE ") + 16` = 26 est alloué qui correspondra forcément à la commande `CHALLENGE` et son argument.  

Un second espace est alloué de taille = `strlen(pass) + 50`.  

Différentes opérations sont effectuées sur une variable locale située en `ebp-68` (ebp-44h). Nommons là `str` pour simplifier.  
Le nom d'utilisateur est recopié en deux coups (deux dword) dans `str`. Si la chaine fait plus de 8 caractères elle sera donc tronquée. Le nom d'utilisateur est recopié avec le caractère de fin de ligne (évidemment si le nom fait 7 caractères minimum).  

![securitech alice str](/assets/img/securitech8_alice.jpg)

Un pointeur est posé à `str+6` (7ᵉ caractère de `str`, les index commençant à 0), les 45 premiers caractères de l'aléa (de `aléa[0]` à `aléa[44]`) y sont recopiés. Dans notre cas, le nom d'utilisateur étant `alice\n`, les 45 caractères arrivent juste après.  

L'algorithme n'est pas très évolué puisque dans le cas d'un petit username, des données aléatoires seraient présentes entre le LF (fin de ligne) et l'aléa. Ensuite le nombre 6 n'est pas calculé à partir du user mais en dur dans le code...  

De même on retrouve la chaine `USER alice\n` hardcodée dans le binaire... autrement dit on doit faire nos calculs seulement avec ce nom.  

Le mot de passe qui a été demandé par le programme est ensuite concaténé à `str` (copie en `str+51`).  

On a alors str=`alice\nalea[0..44]password`.  

`str` passe ensuite dans une boucle où elle est recopiée à l'envers en `ebp-68` (ebp-44h).  

![boucle asm](/assets/img/securitech8_boucle.jpg)

L'ancienne chaîne de caractère ne nous servira plus, disons que ce résultat prend le nom `str`.  

Le pointeur est alors à la fin de la chaine.  

On a ensuite une opération perdue au milieu de différentes instructions apparemment inutiles :  

```nasm
movzx edx, byte ptr [ebx-1] ; transforme un octet en dword
...
mov eax, [ebp-30h] ; $eax = strlen(pass)+50
cdq
shr edx, 1ch ; décalage de 28 crans à droite... donc forcément zéro (edx ne peut pas dépasser 0xFF)
lea eax, [edx+eax]
mov esi, eax
and eax, 0fh ; $eax = (strlen(pass)+50) XOR 0x0F
sar esi, 4
sub eax, edx ; $eax = $eax - 0
mov edx, eax ; $edx = $eax
```

Ce qu'il faut retenir c'est que l'on obtient une valeur `X` = `XOR entre <la longueur du pass + 50> et 0x0F`.  

Le pointeur est ensuite diminué de `X`.  

Cette position marque le début d'une chaine que l'on appellera `buff`.  
`buff` vaut alors quelque chose comme `XX..X\necila` (la fin de `str` inversé)  

Deux appels à `memcpy` sont alors effectués.  

Le premier pour y attacher les` 16 - X` premiers caractères d'une chaine hardcodé :

```
zae('_]f4`#c84g
```  

Le second pour y attacher la chaine `CHALLENGE `  

Ça commence à être compliqué... En Python on peut résumer ça à :  

```python
user = "alice\n" # valeur fixe
alea_44 = alea[:45] # on utilise les 45 premiers octets de l'aléa
str = user + alea_44 + mypass # concaténation
str = str[::-1] # inversion
buff = str[len(str) - x - 1:] + "zae('_]f4`#c84g"[:16 - x] + "CHALLENGE "
```

Les dernières opérations de l'algorithme se font sur des blocks de 16 octets.  

`str` est découpée en 3 morceaux de 16 octets, respectivement `str1`, `str2` et `str3`.  

Si `X` n'est pas nul une opération supplémentaire est effectuée :  

`str1` est XORé avec les 16 premiers octets de `buff`.

Pour que `X` soit nul il faut que `(strlen(pass)+50) XOR 0x0F = 00` donc que `strlen(pass)+50 = 0x3F = 63` ce qui correspondrait à un mot de passe de 13 caractères.  

Dans tous les cas `str1` est XORé avec `str2` puis `str3`.  

Le challenge correspond au `str1` final.  

Si on analyse la situation, elle n'est pas désespérée :  

* Aucun procédé cryptographique avancé n'est utilisé, **juste des XOR**.
* `str` est initialement composé de **3 éléments différents dont deux sont connus** (aléa et username)

`str` est retournée ce qui fait que **les éléments que l'on connaît se retrouvent en fin de chaine, éléments utilisés pour le cryptage**.  

**X ne dépend que de la longueur du password et non de ses caractères.**  

La faille est là : les fins de chaines ! En prenant un password fictif et en ajustant sa taille (brute force sur la taille du pass), on pourra toujours calculer `str2`, `str3` ainsi que la fin de `str1`.  

Comme XOR est utilisé on peut espérer *"remonter"* uniquement à partir du challenge et de l'aléa présent dans la capture réseau.  

Pour rappel : Si `A XOR B = C` alors `A XOR C = B` et `B XOR C = A`.  

Le seul problème est l'opération effectuée avec les 16 premiers octets de `buff` où le password (la seule vraie inconnue) est utilisé.  
Ça laisse supposer que le mot de passe pourrait faire 13 caractères ;-)  

Voilà le code que j'ai écrit en Python :  

```python
#!/usr/bin/env python
import sys,operator
alea="\xf8\x03\xb4\x8f`\xf2\xbf\xa9\x95C\xce\xc9\r\xa2\x1a0\xaa\x12\xee\x90n\x99\xc8\x17\xc8\xc7\x9f\xf5\x15\x97\xfe\x0e\x9a\xb2\x9e\xfb\xa5]\xa4;\xa0r\x05\xae\x15"
cypher="\x8f\xc9\xb6\x9bM\xf6\x98\xa2\xf8\x97\x13\xc63d\xfe5"

for longueur in range(17):
  mypass = "X" * longueur
  x = (longueur+50) & 15
  print "longueur =", longueur, ",x =", x
  user = "alice\n"
  alea_44 = alea[:45]
  str = user + alea_44 + mypass
  str = str[::-1]
  magic = str[len(str)-x-1:] + "zae('_]f4`#c84g"[:16-x] + "CHALLENGE "
  for i in range(16):
    c = ord(cypher[i])
    if x != 0:
      c = operator.xor(c, ord(magic[i]))
    c = operator.xor(c, ord(str[i+16]))
    c = operator.xor(c, ord(str[i+32]))
    sys.stdout.write("\\x" + chr(c).encode("hex_codec"))
  print
  for i in range(len(str)):
    sys.stdout.write("\\x" + str[i].encode("hex_codec"))
  print
  print "-----------------------"
```

`str1` sera forcément composée soit du pass seulement, soit du pass et d'un bout de l'aléa.  

On prend par exemple un pass `XXX`. On effectue l'algorithme dans le bon sens avec l'aléa du challenge.  

`str1` se terminera obligatoirement par une partie de l'aléa.  

En effectuant les opérations en sens inverse sur le challenge (cypher dans mon code) de l'épreuve, on arrivera à une autre version de `str1`.  

**Si ces deux versions ont une fin commune (partie de l'aléa) alors on est en mesure de déterminer le bon mot de passe.**  

Dans la sortie de mon code on trouve :  

longueur = 13, x = 15  
```
\x79\x34\x33\x48\x7b\x5d\x7c\x66\x5b\x5f\x27\x47\x65**\x15\xae\x05**
\x58\x58\x58\x58
\x58\x58\x58\x58\x58\x58\x58\x58\x58**\x15\xae\x05**\x72\xa0\x3b\xa4\x5d\xa5\xfb\x9e\xb2\x9a\x0e\xfe\x97\x15\xf5\x9f\xc7\xc8\x17\xc8\x99\x6e\x90\xee\x12\xaa\x30\x1a\xa2\x0d\xc9\xce\x43\x95\xa9\xbf\xf2\x60\x8f
\xb4\x03\xf8\x0a\x65\x63\x69\x6c\x61
```  

Soit une correspondance de trois caractères pour un pass de longueur 13.  

Les 13 premiers caractères de `\x79\x34\x33\x48\x7b\x5d\x7c\x66\x5b\x5f\x27\x47\x65\x15\xae\x05` sont :  

```
y43H{]|f[_'Ge
```  

Qu'il faut penser à retourner :  

```
eG'_[f|]{H34y
```

Plus qu'à relancer SecureTelnet, donner le password et utiliser la commande `VALIDNIVO`.  

En espérant que c'était clair.

*Published January 07 2011 at 09:27*
