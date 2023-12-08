---
title: "Solution du crackme Weird de crackmes.one"
tags: [crackme]
---

[crackmes.one](https://crackmes.one/) est le site qui succès à _crackmes.de_ et met à disposition des crackmes pour toutes plateformes et architectures avec des binaires créés à partir de nombreux langages.

Ici, il s'agit du dernier crackme posté, voici les métadonnées.

> Author: exzettabyte
> 
> Language: C/C++
>
> Platform: Unix/linux etc.
> 
> Difficulty: 2.0
>
> Quality: 4.0
>
> Arch: x86-64
> 
> Description: Find The Flag

L'utilisation de la commande `file` sur le binaire indique qu'il s'agit d'un exécutable statique :

`weird: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, no section header`

En regardant les chaines de caractères dans ce fichier, je remarque des références à un packer bien connu :

```
$Info: This file is packed with the UPX executable packer http://upx.sf.net $
$Id: UPX 3.95 Copyright (C) 1996-2018 the UPX Team. All Rights Reserved. $
UPX!
```

On unpacke le binaire avec `upx` :

```console
$ upx -d weird 
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2023
UPX 4.2.1       Markus Oberhumer, Laszlo Molnar & John Reiser    Nov 1st 2023

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
    878719 <-    335696   38.20%   linux/amd64   weird

Unpacked 1 file
```

On a toujours un binaire statique :

```console
$ file weird 
weird: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, BuildID[sha1]=01505e0b7627458ae8c25f85686edc38358fba68, for GNU/Linux 3.2.0, not stripped
```

J'ouvre le fichier dans `Cutter` et là, je remarque que la fonction `main()` ne fait pas grand-chose :

```nasm
int main(int argc, char **argv, char **envp);
0x00401ddb      endbr64
0x00401ddf      push    rbp
0x00401de0      mov     rbp, rsp
0x00401de3      lea     rdi, str.Something_weird ; 0x49500f ; const char *s
0x00401dea      call    sym.puts   ; sym.puts ; int puts(const char *s)
0x00401def      mov     eax, 0
0x00401df4      pop     rbp
0x00401df5      ret
```

Vous avez dit weird ?

Comme le binaire n'est pas strippé, j'ai les noms des fonctions présentes et j'en remarque une nommée `secret`.

![crackmes.one weird secret](/assets/img/crackmes/weird_secret.png)

Cette fonction ne semble pas accepter d'argument. Elle fait son taff dans son coin puis semble afficher le flag.

J'édite l'instruction `call` dans le `main()` afin qu'il appelle cette fonction :

```nasm
int main(int argc, char **argv, char **envp);
0x00401ddb      endbr64
0x00401ddf      push    rbp
0x00401de0      mov     rbp, rsp
0x00401de3      lea     rdi, str.Something_weird ; 0x49500f ; const char *s
0x00401dea      call    secret     ; sym.secret
0x00401def      mov     eax, 0
0x00401df4      pop     rbp
0x00401df5      ret
```

Et désormais, on peut obtenir le flag :

```console
$ ./weird 
Flag : flag{9aec9b0277379453e49889427efe7e7b}
```
