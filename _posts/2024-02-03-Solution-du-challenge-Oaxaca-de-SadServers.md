---
title: "Solution du challenge Oaxaca de SadServers.com"
tags: [CTF,AdminSys,SadServers
---

**Scenario:** "Oaxaca": Close an Open File

**Level:** Medium

**Type:** Fix

**Tags:** [bash](https://sadservers.com/tag/bash)   [unusual-tricky](https://sadservers.com/tag/unusual-tricky)  

**Description:** The file `/home/admin/somefile` is open for writing by some process. Close this file without killing the process.

**Test:** `lsof /home/admin/somefile` returns nothing.

**Time to Solve:** 15 minutes.

Voyons le processus qui utilise le fichier :

```console
admin@i-05fd8a4af5206358f:/$ sudo lsof /home/admin/somefile 
COMMAND PID  USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME
bash    794 admin   77w   REG  259,1        0 272875 /home/admin/somefile
sudo    806  root   77w   REG  259,1        0 272875 /home/admin/somefile
admin@i-05fd8a4af5206358f:/$ ps aux | grep "screen|tmux"
admin        811  0.0  0.1   5208   652 pts/0    S<+  10:53   0:00 grep screen|tmux
```

Il s'agit de bash et je ne vois aucune session `screen` ni `tmux` présente...

Je fouille dans le dossier de l'administrateur :

```console
admin@i-05fd8a4af5206358f:/$ cd home/admin/
admin@i-05fd8a4af5206358f:~$ ls -a
.  ..  .bash_history  .bash_logout  .bashrc  .local  .profile  .selected_editor  .ssh  agent  openfile.sh  somefile
admin@i-05fd8a4af5206358f:~$ cat openfile.sh 
#!/bin/bash
exec 66> /home/admin/somefile
```

La commande `exec` de bash a été utilisée pour ouvrir un descripteur de fichier.

On peut normalement le fermer de cette façon :

```console
admin@i-05fd8a4af5206358f:~$ exec 66>&-
admin@i-05fd8a4af5206358f:~$ sudo lsof /home/admin/somefile 
COMMAND PID  USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME
bash    794 admin   77w   REG  259,1        0 272875 /home/admin/somefile
sudo    833  root   77w   REG  259,1        0 272875 /home/admin/somefile
```

Hmmm, ça n'a pas fonctionné. Pas le bon descripteur ?

Voyons voir les descripteurs du PID courant (bash) :

```console
admin@i-05fd8a4af5206358f:~$ echo $$
794
admin@i-05fd8a4af5206358f:~$ ls /proc/794/fd -al
total 0
dr-x------ 2 admin admin  0 Mar  2 10:52 .
dr-xr-xr-x 9 admin admin  0 Mar  2 10:52 ..
lrwx------ 1 admin admin 64 Mar  2 10:52 0 -> /dev/pts/0
lrwx------ 1 admin admin 64 Mar  2 10:52 1 -> /dev/pts/0
lrwx------ 1 admin admin 64 Mar  2 10:52 2 -> /dev/pts/0
lrwx------ 1 admin admin 64 Mar  2 10:52 255 -> /dev/pts/0
l-wx------ 1 admin admin 64 Mar  2 10:52 77 -> /home/admin/somefile
admin@i-05fd8a4af5206358f:~$ exec 77>&-
admin@i-05fd8a4af5206358f:~$ sudo lsof /home/admin/somefile 
admin@i-05fd8a4af5206358f:~$
```

Ici, il s'agissait du descripteur 77.
