---
title: "Lecture de lignes depuis un flux en C"
tags: [Coding]
---

Quand on a besoin de lire des données depuis un fichier ou un socket, on sait parfois sur quoi on va tomber si les données suivent une structure prédéfinie mais dans d'autres cas on ne sait pas quelles données vont être lues.  

Ce cas est assez simple à gérer avec des langages dits *"haut niveau"* mais c'est plus difficile en C.  

Quand j'étudie des codes sources en C je vois généralement deux cas qui sont :  

* l'utilisation d'un énorme buffer pour récupérer les données suivi des opérations effectuées sur ce buffer
* la lecture octet par octet du flux pour éviter de faire des opérations complexes sur le buffer

La première solution fonctionne correctement si le buffer est toujours plus grand que les données reçues, mais dans la plupart des cas que j'ai observé, cette éventualité n'a pas été prise en compte ce qui peut provoquer de nombreux bugs.  

La seconde solution est plus robuste, mais peu performante.  

Comme j'ai dû faire face à cette problématique récemment je vous donne que j'ai écrit pour lire des lignes depuis un fichier. Le programme lit des données depuis un fichier par blocs de 16 octets et affiche chaque ligne de texte.  

On a les variables suivantes :  

* `buffer` : un buffer de 16 octets utilisé uniquement pour la lecture des données
* `current` : un pointeur sur le caractère en cours de lecture dans le buffer
* `str` : un pointeur vers une chaine de caractères allouée dynamiquement qui contiendra la ligne en cours de traitement
* `i` : un index sur le caractère en cours sur la ligne en cours
* `j` : un index sur le caractère en cours sur le buffer

Si vous avez tout suivi, voici le code :  

```c
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char * argv[]) {
    char * current;
    int fd;
    char * str;
    char buff[17];
    int i, j;
    int size;
    int len;

    fd = open("fic.txt", O_RDONLY);
    i = 0;
    size = 16;
    str = malloc(size);
    while (1) {
        len = read(fd, buff, 16);
        if (len < 1) {
            close(fd);
            return 1;
        }
        current = buff;
        j = 0;
        while (j < len) {
            if ( * current == '\n') {
                str[i] = '\0';
                printf("%s.\n", str);
                i = 0;
                free(str);
                size = 16;
                str = malloc(size);
                current++;
            } else {
                str[i++] = * current++;
            }
            j++;
        }
        if (i > 0) {
            size += 16;
            str = realloc(str, size);
        }
    }
    free(str);
    close(fd);
    return 0;
}
```

Il doit y avoir quelques modifications à faire pour adapter la boucle à vos besoins. Je n'ai pas observé de bugs durant mes tests. N'hésitez pas à faire des remarques.

*Published January 10 2011 at 07:28*
