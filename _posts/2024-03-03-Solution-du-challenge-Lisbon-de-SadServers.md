---
title: "Solution du challenge Lisbon de SadServers.com"
tags: [CTF,AdminSys,SadServers]
---

**Scenario:** "Lisbon": etcd SSL cert troubles

**Level:** Medium

**Type:** Fix

**Tags:** [etcd](https://sadservers.com/tag/etcd)   [ssl](https://sadservers.com/tag/ssl)   [realistic-interviews](https://sadservers.com/tag/realistic-interviews)  

**Description:** There's an *etcd* server running on https://localhost:2379 , get the value for the key "foo", ie `etcdctl get foo` or `curl https://localhost:2379/v2/keys/foo`

**Test:** etcdctl get foo returns bar.

**Time to Solve:** 20 minutes.

Ce scénario a été un vrai casse-tête. J'en ai résolu une partie, mais j'ai dû jeter l'éponge à la fin et consulter la solution.

Voyons ce qu'il se passe avec la commande :

```console
admin@i-08f438fe20e16868c:/$ etcdctl get foo
Error:  client: etcd cluster is unavailable or misconfigured; error #0: x509: certificate has expired or is not yet valid: current time 2025-03-02T17:18:38Z is after 2023-01-30T00:02:48Z

error #0: x509: certificate has expired or is not yet valid: current time 2025-03-02T17:18:38Z is after 2023-01-30T00:02:48Z
```

Le certificat a expiré. En plus l'erreur nous indique que nous sommes en 2025 au lieu de 2024.

On peut aussi constater le problème de certificat avec `openssl` :

```console
admin@i-08f438fe20e16868c:/etc/default$ openssl s_client -connect 127.0.0.1:2379
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = localhost
verify error:num=10:certificate has expired
notAfter=Jan 30 00:02:48 2023 GMT
verify return:1
depth=0 C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = localhost
notAfter=Jan 30 00:02:48 2023 GMT
verify return:1
---
Certificate chain
 0 s:C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = localhost
   i:C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = localhost
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDkzCCAnugAwIBAgIUH9str4OD0GJuoYSEBWSMjLvDZyIwDQYJKoZIhvcNAQEL
BQAwWTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDESMBAGA1UEAwwJbG9jYWxob3N0MB4X
DTIyMTIzMTAwMDI0OFoXDTIzMDEzMDAwMDI0OFowWTELMAkGA1UEBhMCQVUxEzAR
BgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGEludGVybmV0IFdpZGdpdHMgUHR5
IEx0ZDESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEA4Q6WAutMU7NwZNVedwkkFu2vElGXt4UNhraRauCtD9XzP7RSm8UG
IXg5ddqFhOmi06LtSybimbA9K9763y5T5ncpluuYBN+Z9h8t83ZRV+QYW3gO5YRD
WfZjIRBhHXW4cfHOu2oOJd0rD95V87p1u1zxuqbDjh+4vWvgzzyuCRqlWyuKPmGk
XbmM4+qxlq62VhukhL1q46DKmSBE9zL1Oe23bermvp8XSPdfaWgNx4ChitJddvV4
eXOQw6VmA9Lf/WibMbYaubwsjhx+y2du20GcDqG8wk0IO2SyLgZrLsV/JiGqBnT2
49u33gDW+CP/2YUlPCURAkxt4sftu4sKeQIDAQABo1MwUTAdBgNVHQ4EFgQUiXpO
MNVRg1O+yM+Gvvw2TjN/zX0wHwYDVR0jBBgwFoAUiXpOMNVRg1O+yM+Gvvw2TjN/
zX0wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAJlr9IQXzWfZo
PVwYu1hZTWkCR3UUKy9mvy3t5JX+2evQXZOhDfycq6CNkxfg6EXEjhqPrmoSosMU
Z9miIvbQMyWn4o6ORQpE3wacJri6GhLBjpyNfoMQivJMhJ0BXUrGyvZPD+wQF2Jc
Iwhj45Xtn+wluh9AmqCGy6S/Zf1QNjdnpbFImwzviuY/lqHhnSsIPQTaX5wYxrER
UbryzP5/4HF9kHEQJXxeHS3/URIp8otpviq3H7UODHeIviZgLdBtJGlkBXmub30p
7xgnGw/YHOlJcxUes0u8kbiTUQvFPj2OS0oYpV/txHvdiC9lqmfxcE28smTdMoV9
1F4bJMqqSQ==
-----END CERTIFICATE-----
subject=C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = localhost

issuer=C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = localhost

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: X25519, 253 bits
---
SSL handshake has read 1475 bytes and written 363 bytes
Verification error: certificate has expired
--- snip ---
```

Le programme `etcd` est lancé avec des options permettant d'utiliser un certificat SSL :

```console
admin@i-08f438fe20e16868c:/etc/default$ ps aux | grep etcd
etcd         578  0.8  5.2 11729040 24668 ?      Ssl  17:17   0:04 /usr/bin/etcd --cert-file /etc/ssl/certs/localhost.crt --key-file /etc/ssl/certs/localhost.key --advertise-client-urls=https://localhost:2379 --listen-client-urls=https://localhost:2379
```

Tout est lancé depuis systemd :

```console
root@i-08f438fe20e16868c:/etc/default# cat ../systemd/system/etcd2.service 
[Unit]
Description=etcd - highly-available key value store
Documentation=https://etcd.io/docs
Documentation=man:etcd
After=network.target
Wants=network-online.target

[Service]
Environment=DAEMON_ARGS=
Environment=ETCD_NAME=%H
Environment=ETCD_DATA_DIR=/var/lib/etcd/default
EnvironmentFile=-/etc/default/%p
Type=notify
User=etcd
PermissionsStartOnly=true
#ExecStart=/bin/sh -c "GOMAXPROCS=$(nproc) /usr/bin/etcd $DAEMON_ARGS"
ExecStart=/usr/bin/etcd $DAEMON_ARGS \
        --cert-file /etc/ssl/certs/localhost.crt \
        --key-file /etc/ssl/certs/localhost.key \
        --advertise-client-urls=https://localhost:2379 \
        --listen-client-urls=https://localhost:2379
Restart=on-abnormal
#RestartSec=10s
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
Alias=etcd2.service
```

J'ai d'abord tenté de supprimer toutes les options données à etcd afin qu'il écoute en _clair_.

Malgré cela le client continuait de tomber sur un certificat... étrange.

J'ai donc plutôt choisi de mettre le certificat auto-signé à jour.

Déjà, il fallait corriger la date du système qui avance d'une année :

```bash
sudo date -s "last year"
```

Puis régénérer un certificat :

```console
admin@i-0b35d84e135f65ac8:/$ sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/certs/localhost.key -out /etc/ssl/certs/localhost.crt
Generating a RSA private key
............+++++
....+++++
writing new private key to '/etc/ssl/certs/localhost.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:localhost
Email Address []:
admin@i-0b35d84e135f65ac8:/$ sudo systemctl restart etcd2
admin@i-0b35d84e135f65ac8:/$ etcdctl get foo
Error:  client: etcd cluster is unavailable or misconfigured; error #0: x509: certificate has expired or is not yet valid: current time 2024-03-02T17:53:17Z is after 2023-01-30T00:02:48Z

error #0: x509: certificate has expired or is not yet valid: current time 2024-03-02T17:53:17Z is after 2023-01-30T00:02:48Z
```

C'est la grosse claque : le serveur continue d'utiliser l'ancien certificat alors qu'on a écrasé les fichiers... WTF !

La blague qui était en place sur ce challenge, c'est qu'une règle iptables redirige le port de `etcd` vers un Nginx qui utilise le vieux certificat :

```console
admin@i-02f3860338fe0d7a3:/$ sudo iptables -t nat -L OUTPUT --line-numbers
Chain OUTPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    REDIRECT   tcp  --  anywhere             anywhere             tcp dpt:2379 redir ports 443
2    DOCKER     all  --  anywhere            !ip-127-0-0-0.us-east-2.compute.internal/8  ADDRTYPE match dst-type LOCAL
```

Une fois la règle retirée :

```bash
sudo iptables -t nat -D OUTPUT 1
```

On pouvait finalement accéder aux données.

```console
admin@i-02f3860338fe0d7a3:/$ sudo systemctl restart etcd2
admin@i-02f3860338fe0d7a3:/$ etcdctl get foo
bar
```
