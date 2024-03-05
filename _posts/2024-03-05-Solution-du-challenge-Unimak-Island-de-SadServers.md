---
title: "Solution du challenge Unimak Island de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

Scenario:** "Unimak Island": Fun with Mr Jason

**Level:** Medium

**Type:** Do

**Tags:** [json](https://sadservers.com/tag/json)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** Using the file `station_information.json` , find the `station_id` where `has_kiosk` is `false` and `capacity` is greater than 30.

Save the `station_id` of the solution in the `/home/admin/mysolution` file, for example: `echo "ec040a94-4de7-4fb3-aea0-ec5892034a69" > ~/mysolution`

You can use the installed utilities [jq](https://jqlang.github.io/jq/), [gron](https://github.com/tomnomnom/gron), [jid](https://github.com/simeji/jid) as well as [Python3](https://docs.python.org/3/library/json.html) and [Golang](https://gobyexample.com/json).

**Test:** `md5sum /home/admin/mysolution` returns `8d8414808b15d55dad857fd5aeb2aebc`

**Time to Solve:** 15 minutes.

Voyons voir à quoi ressemble ce fichier JSON :

```console
f9a69:~$ ls -alh
total 1.2M
drwxr-xr-x 6 admin admin 4.0K Sep 26 21:49 .
drwxr-xr-x 3 root  root  4.0K Sep 17 16:44 ..
drwx------ 3 admin admin 4.0K Sep 20 15:52 .ansible
-rw------- 1 admin admin  119 Mar  4 20:04 .bash_history
-rw-r--r-- 1 admin admin  220 Aug  4  2021 .bash_logout
-rw-r--r-- 1 admin admin 3.5K Aug  4  2021 .bashrc
drwxr-xr-x 3 admin admin 4.0K Sep 20 15:56 .config
-rw-r--r-- 1 admin admin  807 Aug  4  2021 .profile
drwx------ 2 admin admin 4.0K Sep 17 16:44 .ssh
drwxr-xr-x 2 admin root  4.0K Sep 26 21:49 agent
-rw-r--r-- 1 admin admin 1.1M Sep 26 21:49 station_information.json
admin@i-02bb40c710bff9a69:~$ cat station_information.json | python3 -m json.tool | head -20
{
    "data": {
        "stations": [
            {
                "eightd_has_key_dispenser": false,
                "rental_methods": [
                    "KEY",
                    "CREDITCARD"
                ],
                "external_id": "c00ef46d-fcde-48e2-afbd-0fb595fe3fa7",
                "station_id": "c00ef46d-fcde-48e2-afbd-0fb595fe3fa7",
                "rental_uris": {
                    "ios": "https://bkn.lft.to/lastmile_qr_scan",
                    "android": "https://bkn.lft.to/lastmile_qr_scan"
                },
                "region_id": "71",
                "capacity": 3,
                "short_name": "4920.13",
                "electric_bike_surcharge_waiver": false,
                "has_kiosk": true,
```

Il faut donc énumérer le contenu de `data > stations`, ce qui se fait très bien avec Python :

```console
admin@i-02bb40c710bff9a69:~$ cat read.py 
import json

with open("station_information.json") as fd:
    data = json.load(fd)
    for station in data["data"]["stations"]:
        if station["has_kiosk"] is False and station["capacity"] > 30:
            print(station["station_id"])
admin@i-02bb40c710bff9a69:~$ python3 read.py 
05c5e17c-7aa9-49b7-9da3-9db4858ec1fc
admin@i-02bb40c710bff9a69:~$ echo 05c5e17c-7aa9-49b7-9da3-9db4858ec1fc > mysolution
```
