---
title: "Solution du crackme grainne"
tags: [reverse engineering, CTF]
---

Il s'agit d'un crackme linux de [stefanie](http://gnurbs.blogsome.com/) qui a été proposé sur [crackmes.de](http://crackmes.de/) ainsi que sur son blog.  

Une fois que l'on a téléchargé le binaire et fait quelques tests, on se dit que ça ne va pas être de la tarte.  

```console
$ file grainne
grainne: ELF 32-bit LSB executable, Intel 80386, version 1, statically linked, corrupted section header size
```

L'exécutable ne fait que 595 octets. Autant dire qu'il a été cuisiné maison et n'est pas passé par gcc. D'autres mesures ont aussi dû être prises pour réduire la taille du fichier.  

Si on essaye d'étudier le programme avec des programmes habituels, tous se cassent les dents. Objdump renvoi *"File format not recognized"*, HT Editor nous donne *"unexpected end of file"* et pour gdb... le fichier n'est pas un exécutable !  

`readelf` nous donne quelques infos avant de jeter l'éponge :  

```console
$ readelf -a grainne
readelf: Error: Unable to read in 0xe800 bytes of section headers
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 73 74 65 66 75 21 75 7c
  Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       115
  Type:                              EXEC (Executable file)
  Machine:                           Intel 80386
  Version:                           0x1
  Entry point address:               0x804800c
  Start of program headers:          76 (bytes into file)
  Start of section headers:          76 (bytes into file)
  Flags:                             0x0
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         2
  Size of section headers:           59392 (bytes)
  Number of section headers:         65498
  Section header string table index: 65535 <corrupt: out of range>
readelf: Error: Out of memory allocating 0xe7dd9000 bytes for section headers
readelf: Error: Section headers are not available!
Abandon
```

[ELFsh](http://eresi.asgardlabs.org/) sera plus bavard :  

```console
$ elfsh -f grainne -p

 [*] Object grainne has been loaded (O_RDONLY)

 [Program Header Table .::. PHT]
 [Object grainne]

 [00] 0x08048000 -> 0x08048253 r-x memsz(00000595) foffset(00000000) filesz(00000595) align(00004096) => Loadable segment
 [01] 0x080480FB -> 0x0804834E rw- memsz(00000595) foffset(00000251) filesz(00000074) align(00004096) => Loadable segment
```

Le point d'entrée du programme (début des instructions) est à `0x804800c`. Or `0x08048000` correspond au début du fichier (offset 0). Donc on peut désassembler le programme à partir de l'octet 12 (0xC) à l'aide de `ndisasm` :  

```nasm
0804800C  7521              jnz 0x804802f
0804800E  757C              jnz 0x804808c
08048010  0200              add al,[eax]
08048012  0300              add eax,[eax]
08048014  0100              add [eax],eax
08048016  0000              add [eax],al
08048018  0C80              or al,0x80
```

Seules les deux premières instructions ont l'air correctes. Il faut dire aussi quelles se trouvent en plein milieu de l'entête du fichier ^_^  

Si on désassemble à l'adresse `0x804802f` (`ndisasm -o 0x804802f -b 32 -e 47 grainne`), on obtient un call `0x804800e` qui nous ramène au second saut conditionnel que l'on a vu tout à l'heure.  

On arrive enfin à des instructions lisibles en suivant le nouveau saut :  

```nasm
$ ndisasm -o 0x804808c -b 32 -e 140 grainne
0804808C  BFFFFFFFFF        mov edi,0xffffffff
08048091  5A                pop edx
08048092  8915FB800408      mov [0x80480fb],edx
08048098  BEFFFFFFFF        mov esi,0xffffffff
0804809D  8B15FB800408      mov edx,[0x80480fb]
080480A3  FF12              call near [edx]
080480A5  8B15FB800408      mov edx,[0x80480fb]
080480AB  81C208000000      add edx,0x8
080480B1  FF12              call near [edx]
...
```

Pour être franc, je n'ai rien compris à cette portion de code lors de mon étude, et sans un débugger capable de fonctionner sur le binaire, difficile de savoir ce qu'il se passe réellement.  

J'ai donc décidé de chercher ailleurs une partie de code qui serait intéressante. Je l'ai finalement trouvée à tâtons à l'offset 325.  

C'est la partie du binaire qui se trouve après la seconde *"section"* donnée par ELFsh : 251 (foffset) + 74 (filesz) = 325 (145 en hexa)  

Reste à trouver à quelle adresse virtuelle cette section correspond.  

`0x8048000 + 0x145 = 0x8048145`  

La commande à taper sera alors `ndisasm -o 0x8048145 -b 32 -e 325 grainne`  

On se retrouve face à quelques routines anti-débogage qui empêchent par exemple `strace` de faire tourner correctement le programme :  

```nasm
08048145  B830000000        mov eax,0x30
0804814A  BB05000000        mov ebx,0x5
0804814F  B91B820408        mov ecx,0x804821b
08048154  CD80              int 0x80           <- signal(SIGTRAP,0x804821b)
08048156  CC                int3
```

Le code utilise l'appel système `signal` pour que la fonction se trouvant à l'adresse `0x804821b` soit appelée si le signal `SIGTRAP` est levé. Juste après, ce signal est levé avec `int3` pour exécuter la fonction.  
Dans le cas où le programme est tracé avec `strace`, l'instruction `int3` n'aura pas d'effet et notre fonction ne sera pas appelée.  

On trouve aussi à plusieurs reprises dans le code la suite d'instruction suivante :  

```nasm
push dword 0xbadc0de
ret
```

En fait ces instructions n'ont pas d'intérêt sinon de compliquer la compréhension et fausser le désassemblage.  

Dans une condition normale d'utilisation, le programme appellera la fonction déclarée par `signal()`, soit les instructions suivantes :  

```console
0804821B  B804000000        mov eax,0x4
08048220  BB01000000        mov ebx,0x1
08048225  B9FF800408        mov ecx,0x80480ff
0804822A  BA23000000        mov edx,0x23
0804822F  CD80              int 0x80            <- write(1,"shut up and crack me already...\n-> ",35)
08048231  C3                ret
```

Sur le moment je n'ai pas compris le sens du `ret` puisqu'à première vue on ne vient pas d'un call. Mais je me trompais car le code est bien appelé depuis un call dans la section du programme que j'ai laissé tomber. Je n'ai compris cela que bien après, en lisant [le billet de stefanie sur le crackme](https://web.archive.org/web/20071016104607/http://gnurbs.blogsome.com/2007/05/27/the-grainne-crackme/).  

Plus tard le programme lit 12 octets sur l'entrée standard et effectue un XOR sur chaque octet à l'aide d'une variable incrémentée à chaque fois (variable initialisée à 0x1a) :  

```console
080481D4  B90A000000        mov ecx,0xa         <- i=12
080481D9  BA1A000000        mov edx,0x1a
080481DE  BF22810408        mov edi,0x8048122    <- buffer lu
080481E3  3117              xor [edi],edx
080481E5  42                inc edx
080481E6  47                inc edi
080481E7  E2FA              loop 0x80481e3     <- ecx--;
```

Le résultat est ensuite comparé à une chaine hardcodée (`Jsysy?pIGMg`). Il suffisait de suivre l'algorithme de cryptage sur cette chaine pour trouver la bonne clé.  

Un crackme très intéressant mais que j'aurais préféré résoudre en comprenant tous les procédés utilisés.  

Je vous renvoie [aux explications que l'auteur donne sur le sujet](https://web.archive.org/web/20071016104607/http://gnurbs.blogsome.com/2007/05/27/the-grainne-crackme/).

*Published January 10 2011 at 07:20*
