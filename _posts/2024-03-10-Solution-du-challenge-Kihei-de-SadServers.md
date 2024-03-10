---
title: "Solution du challenge Kihei de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Kihei": Surely Not Another Disk Space Scenario

**Level:** Medium

**Type:** Fix

**Tags:** [disk volumes](https://sadservers.com/tag/disk%20volumes)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There is a `/home/admin/kihei` program. Make the changes necessary, so it runs successfully, without deleting the `/home/admin/datafile` file.

**Test:** Running `/home/admin/kihei` returns `Done.`.

**Time to Solve:** 30 minutes.

On trouve deux fichiers dans le dossier de `admin` : le binaire ainsi qu'un fichier de plusieurs Go.

```console
admin@i-0d1a37bdfe942aeab:~$ file kihei datafile 
kihei:    ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, Go BuildID=DwolUanvRPB7DWhc7e4I/nM83nW4qxDvf9asNaf7E/5u1Qa6jnFvq2KL4kV5G1/6IwNz7tVbey9uC58oKsR, not stripped
datafile: data
```

Ni GDB ni ltrace ne sont présents sur le système. De toute façon le binaire est compilé statiquement.

Les challenges de _SadServers_ ne disposent pas d'accès Internet donc récupérer le binaire localement pour l'analyser relève du casse-tête.

On a toutefois `strace` :

```console
admin@i-0d1a37bdfe942aeab:~$ strace ./kihei 
execve("./kihei", ["./kihei"], 0x7ffc7fe95ab0 /* 13 vars */) = 0
arch_prctl(ARCH_SET_FS, 0x56b030)       = 0
sched_getaffinity(0, 8192, [0, 1])      = 8
openat(AT_FDCWD, "/sys/kernel/mm/transparent_hugepage/hpage_pmd_size", O_RDONLY) = 3
read(3, "2097152\n", 20)                = 8
close(3)                                = 0
mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fdaf11a6000
--- snip ---
fcntl(2, F_GETFL)                       = 0x2 (flags O_RDWR)
getuid()                                = 1000
openat(AT_FDCWD, "/etc/passwd", O_RDONLY|O_CLOEXEC) = 3
epoll_create1(EPOLL_CLOEXEC)            = 4
pipe2([5, 6], O_NONBLOCK|O_CLOEXEC)     = 0
epoll_ctl(4, EPOLL_CTL_ADD, 5, {EPOLLIN, {u32=5871088, u64=5871088}}) = 0
epoll_ctl(4, EPOLL_CTL_ADD, 3, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=3394346744, u64=140577673944824}}) = -1 EPERM (Operation not permitted)
read(3, "root:x:0:0:root:/root:/bin/bash\n"..., 4096) = 1540
close(3)                                = 0
newfstatat(AT_FDCWD, "/home/admin/data/newdatafile", 0xc0000129f8, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/local/sbin/fallocate", 0xc000012b98, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/local/bin/fallocate", 0xc000012c68, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/sbin/fallocate", 0xc000012d38, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/bin/fallocate", {st_mode=S_IFREG|0755, st_size=35048, ...}, 0) = 0
openat(AT_FDCWD, "/dev/null", O_RDONLY|O_CLOEXEC) = 3
epoll_ctl(4, EPOLL_CTL_ADD, 3, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=3394346744, u64=140577673944824}}) = -1 EPERM (Operation not permitted)
openat(AT_FDCWD, "/dev/null", O_WRONLY|O_CLOEXEC) = 7
epoll_ctl(4, EPOLL_CTL_ADD, 7, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=3394346744, u64=140577673944824}}) = -1 EPERM (Operation not permitted)
openat(AT_FDCWD, "/dev/null", O_WRONLY|O_CLOEXEC) = 8
epoll_ctl(4, EPOLL_CTL_ADD, 8, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=3394346744, u64=140577673944824}}) = -1 EPERM (Operation not permitted)
pipe2([9, 10], O_CLOEXEC)               = 0
getpid()                                = 760
rt_sigprocmask(SIG_SETMASK, NULL, [], 8) = 0
rt_sigprocmask(SIG_SETMASK, ~[], NULL, 8) = 0
clone(child_stack=NULL, flags=CLONE_VM|CLONE_VFORK|SIGCHLD) = 764
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=760, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=760, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
close(10)                               = 0
read(9, "", 8)                          = 0
close(9)                                = 0
close(3)                                = 0
close(7)                                = 0
close(8)                                = 0
waitid(P_PID, 764, {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=764, si_uid=1000, si_status=1, si_utime=0, si_stime=0}, WEXITED|WNOWAIT, NULL) = 0
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=764, si_uid=1000, si_status=1, si_utime=0, si_stime=0} ---
rt_sigreturn({mask=[]})                 = 0
wait4(764, [{WIFEXITED(s) && WEXITSTATUS(s) == 1}], 0, {ru_utime={tv_sec=0, tv_usec=1978}, ru_stime={tv_sec=0, tv_usec=0}, ...}) = 764
unlinkat(AT_FDCWD, "/home/admin/data/newdatafile", 0) = 0
nanosleep({tv_sec=0, tv_nsec=1000000}, NULL) = 0
nanosleep({tv_sec=0, tv_nsec=1000000}, NULL) = 0
write(2, "panic: ", 7panic: )                  = 7
write(2, "exit status 1", 13exit status 1)           = 13
write(2, "\n", 1
)                       = 1
write(2, "\n", 1
)                       = 1
write(2, "goroutine ", 10goroutine )              = 10
write(2, "1", 11)                        = 1
write(2, " [", 2 [)                       = 2
write(2, "running", 7running)                  = 7
write(2, "]:\n", 3]:
)                     = 3
write(2, "main.main", 9main.main)                = 9
write(2, "(", 1()                        = 1
write(2, ")\n", 2)
)                      = 2
write(2, "\t", 1        )                       = 1
write(2, "./main.go", 9./main.go)                = 9
write(2, ":", 1:)                        = 1
write(2, "64", 264)                       = 2
write(2, " +", 2 +)                       = 2
write(2, "0x47d", 50x47d)                    = 5
write(2, "\n", 1
)                       = 1
exit_group(2)                           = ?
+++ exited with 2 +++
```

On obtiendra une compréhension plus claire de ce qui est attendu en regardant le fichier `check.sh` :

```console
#!/usr/bin/bash
# 6GB datafile exists
res=$(ls -l /home/admin/datafile |cut -d' ' -f 5)
res=$(echo $res|tr -d '\r')

if [[ "$res" != "5368709120" ]]
then
  echo -n "NO"
  exit
fi

# kihei binary didn't change
res=$(md5sum /home/admin/kihei |cut -d' ' -f 1)
res=$(echo $res|tr -d '\r')

if [[ "$res" != "79387f23f56e732aa789ee22761f8b84" ]]
then
  echo -n "NO"
  exit
fi

# kihei runs succesfully
res=$(/home/admin/kihei)
res=$(echo $res|tr -d '\r')

if [[ "$res" = "Done." ]]
then
  echo -n "OK"
else
  echo -n "NO"
fi
```

Donc :

- il faut que `/home/admin/datafile` fasse 6Go de taille
- il ne faut pas altérer le binaire du challenge
- il faut que le binaire affiche `Done.` quand on l'exécute

Avec `strace` je parviens à comprendre que le programme tente de créer `data/newdatafile` et de le remplir avec 1.5Go :

```
616   openat(AT_FDCWD, "/home/admin/data/newdatafile", O_RDWR|O_CREAT, 0666) = 3
616   fallocate(3, 0, 0, 1500000000)    = -1 ENOSPC (No space left on device)
```

La difficulté est lié à l'espace disque disponible :

```console
admin@i-0b7f2da04a55bd886:~$ df -h
Filesystem       Size  Used Avail Use% Mounted on
udev             217M     0  217M   0% /dev
tmpfs             46M  368K   46M   1% /run
/dev/nvme0n1p1   7.7G  6.1G  1.2G  84% /
tmpfs            228M   12K  228M   1% /dev/shm
tmpfs            5.0M     0  5.0M   0% /run/lock
/dev/nvme0n1p15  124M  5.9M  118M   5% /boot/efi
```

Il nous manque au moins 0.3Go pour que le programme puisse écrire la quantité de données attendue.

On peut tenter de gagner de la place en supprimant `/var/cache` mais ce n'est pas suffisant.

J'ai tenté de jouer sur l'ordre des vérifications en utilisant un lien (symbolique ou non) de `datafile` vers `newdatafile` pour que le binaire réutilise l'espace du gros fichier, mais ça n'a rien donné.

Finalement, il faut se pencher sur les disques présents sur le système et remarquer que certains ne sont pas utilisés :

```console
admin@i-0dbd5dce9178f03c1:~$ lsblk -l
NAME       MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
nvme1n1    259:0    0    1G  0 disk 
nvme0n1    259:1    0    8G  0 disk 
nvme2n1    259:2    0    1G  0 disk 
nvme0n1p1  259:3    0  7.9G  0 part /
nvme0n1p14 259:4    0    3M  0 part 
nvme0n1p15 259:5    0  124M  0 part /boot/efi
admin@i-0dbd5dce9178f03c1:~$ mount
sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
udev on /dev type devtmpfs (rw,nosuid,relatime,size=221828k,nr_inodes=55457,mode=755)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)
tmpfs on /run type tmpfs (rw,nosuid,nodev,noexec,relatime,size=46636k,mode=755)
/dev/nvme0n1p1 on / type ext4 (rw,relatime,discard,errors=remount-ro)
securityfs on /sys/kernel/security type securityfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev)
tmpfs on /run/lock type tmpfs (rw,nosuid,nodev,noexec,relatime,size=5120k)
cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)
pstore on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
none on /sys/fs/bpf type bpf (rw,nosuid,nodev,noexec,relatime,mode=700)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=30,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=1575)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,pagesize=2M)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
debugfs on /sys/kernel/debug type debugfs (rw,nosuid,nodev,noexec,relatime)
tracefs on /sys/kernel/tracing type tracefs (rw,nosuid,nodev,noexec,relatime)
fusectl on /sys/fs/fuse/connections type fusectl (rw,nosuid,nodev,noexec,relatime)
configfs on /sys/kernel/config type configfs (rw,nosuid,nodev,noexec,relatime)
/dev/nvme0n1p15 on /boot/efi type vfat (rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro)
```

`nvme1n1` et `nvme2n1` ne sont pas utilisés et font chacun 1Go. Seuls, ils ne permettront pas de stocker le fichier `newdatafile` mais si on parvient à les combiner alors ce sera bon.

On ne peut pas juste formatter les disques avec `fdisk`, il va falloir utiliser les commandes LVM comme expliqué [dans cette vidéo](https://www.youtube.com/watch?v=Q6J18RkZ3VY).

Les étapes sont les suivantes :

- déclaration de chacun des disques comme volume physique avec `pvcreate`
- création d'un groupe de volume contenant les deux volumes physiques avec `vgcreate`
- création d'un volume logique utilisant la totalité du groupe de volume avec `lvcreate`
- formatage du volume logique en ext4

```console
admin@i-0dbd5dce9178f03c1:~$ sudo pvcreate /dev/nvme1n1 /dev/nvme2n1
WARNING: dos signature detected on /dev/nvme2n1 at offset 510. Wipe it? [y/n]: y
  Wiping dos signature on /dev/nvme2n1.
  Physical volume "/dev/nvme1n1" successfully created.
  Physical volume "/dev/nvme2n1" successfully created.
admin@i-0dbd5dce9178f03c1:~$ sudo vgcreate vg /dev/nvme1n1 /dev/nvme2n1
  Volume group "vg" successfully created
admin@i-0dbd5dce9178f03c1:~$ lvcreate -n lv -l 100%FREE vg
  WARNING: Running as a non-root user. Functionality may be unavailable.
  /dev/mapper/control: open failed: Permission denied
  Failure to communicate with kernel device-mapper driver.
  Incompatible libdevmapper 1.02.175 (2021-01-08) and kernel driver (unknown version).
  striped: Required device-mapper target(s) not detected in your kernel.
  Run `lvcreate --help' for more information.
admin@i-0dbd5dce9178f03c1:~$ sudo lvcreate -n lv -l 100%FREE vg
  Logical volume "lv" created.
admin@i-0dbd5dce9178f03c1:~$ sudo mkfs.ext4 /dev/vg/lv
mke2fs 1.46.2 (28-Feb-2021)
Creating filesystem with 522240 4k blocks and 130560 inodes
Filesystem UUID: e0eb8344-b6f5-464d-81be-ec633fef11f9
Superblock backups stored on blocks: 
        32768, 98304, 163840, 229376, 294912

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (8192 blocks): done
Writing superblocks and filesystem accounting information: done 
```

On peut alors monter le volume logique et changer les permissions pour le binaire :

```console
admin@i-0dbd5dce9178f03c1:~$ df -h
Filesystem         Size  Used Avail Use% Mounted on
udev               217M     0  217M   0% /dev
tmpfs               46M  372K   46M   1% /run
/dev/nvme0n1p1     7.7G  6.1G  1.2G  84% /
tmpfs              228M   12K  228M   1% /dev/shm
tmpfs              5.0M     0  5.0M   0% /run/lock
/dev/nvme0n1p15    124M  5.9M  118M   5% /boot/efi
/dev/mapper/vg-lv  2.0G   24K  1.9G   1% /home/admin/data
admin@i-0dbd5dce9178f03c1:~$ sudo chown -R admin: /home/admin/data
```

On dispose maintenant d'assez de place disponible.

Une solution alternative est d'utiliser `tune2fs` comme dans [cette solution](https://sigflag.at/blog/2023/writeup-sadservers-com-july-update/).

Par défaut, lors du formatage d'un disque, le système alloue une partie de l'espace pour de la maintenant (fragmentation, etc).

Avec `tune2fs` on peut modifier la quantité d'espace réservée par le système. L'auteur de cette solution alternative réduit l'espace réservé à 1% ce qui lui permet d'agrandir l'espace disque à 1.6Go ce qui est suffisant pour résoudre le challenge.
