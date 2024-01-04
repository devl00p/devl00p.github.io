---
title: "How I Automated Wapiti to Find Vulnerable WordPress Plugins"
tags: [vulnérabilité, Wapiti]
---

## Introduction

This is not the first time I have automated [Wapiti](https://github.com/wapiti-scanner/wapiti) in order to find vulnerabilities : In September 2019, I conducted some mass vulnerability scanning on the Internet to figure out how effective the XSS capabilities of Wapiti were and to discover bugs in my code.

With 18650 websites scanned each day over a period of one month, I found numerous vulnerabilities. I submitted my discoveries to the OpenBugBounty website which quickly made me reach the 1st place on the website.

[During this research]({% link _posts/2020-02-03-One-crazy-month-of-web-vulnerability-scanning.md %}) I found several kinds of vulnerabilities :

- unknown vulnerabilities in custom web applications
- known vulnerabilities in popular applications
- unknown vulnerabilities in (not so) popular applications

As it was obvious that Wapiti was capable enough to find vulnerabilities in closed or OSS software, I asked myself

> What if I scanned all WordPress plugins to find vulnerabilities ?

## Here we go again

Ok, let's do it. But where to start ?

First, the list of WordPress plugins: fortunately WordPress keeps an SVN with all existing plugins, almost 100k last time I checked :

https://plugins.svn.wordpress.org/

Second, I need the stack to operate the WordPress. It means Apache / PHP / MySQL. A bonus point if I can automate the plugin installation in an easy way.

It turns out there is a CLI tool called [WP-CLI](https://wp-cli.org/) that does what I need.

It is also easy to find a Docker Compose file that will set up containers with the CLI tool and the required stack.

And finally... How will I scan each plugin ?

## Life is about making choices

Let's be honest : most WordPress plugins are only designed with the administrator in mind.

Stuff like _rich editors_ or _user management_ expose URLs that only the administrator can access, not visitors.

Do I really want to connect as administrator to the WordPress using an automated scanner and taking the risks to accidentally delete stuff, break the database or more ? No.

Also, some plugins require human interaction. A plugin to include a poll within a post doesn't have any effect before you actually fill the poll in the administrator dashboard.

Can I create a script that will guess what to write in the database to fill such data ? No.

So I decided to scan only the _visible_ part of the WordPress. I will of course miss some vulnerabilities, but it would make things a lot easier.

## Problems

With my initial setup I quickly noticed several issues.

The most annoying issue was that some WordPress plugins will actually break your WordPress installation :

- broken database structure that cause a PHP error and prevent WordPress from running
- script trying to fetch some data on some server that doesn't exist anymore
- htaccess designed to block access to the WordPress in different ways
- script that eats all your RAM before eating your swap and kill your computer

Therefore, I could not rely on WP-CLI for uninstalling plugins. I had to do the cleanup in a more basic way : restoring files and database.

Docker doesn't provide a snapshot mechanism meaning I had to write a script to do that for me, working on a mounted volume.

One secondary problem was tied to permissions. With the volume mounted on my disk, files inside the volume were tied to non-existent UID/GID (because for example, Apache used UID 33 in the container).

It was annoying because if I wanted to read/edit some files I had to use the `sudo` command for that. The less I use `sudo` / `sudoers` the safer I feel, so I had to edit the Dockerfiles of containers to change the default UID.


## Docker

Here is the docker-compose file that specifies how containers work together :

```docker
version: '3'
services:
  wordpress:
    build:
      dockerfile: Dockerfile.wordpress
      context: .
    depends_on:
      - mysql
    links:
      - mysql
    ports:
      - 8000:80
    restart: always
    environment:
      WORDPRESS_DB_HOST: mysql:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wp-app
      WORDPRESS_DEBUG: 1
      WORDPRESS_TABLE_PREFIX: wp_
      WORDPRESS_CONFIG_EXTRA: |
        define('FS_METHOD', 'direct');
        define('SCRIPT_DEBUG', true);
    volumes:
      - ./.srv/wordpress/:/var/www/html
      - ./.srv/log/:/var/log
      - ./custom.ini:/usr/local/etc/php/conf.d/custom.ini

  wpcli:
    depends_on:
      - mysql
      - wordpress
    build:
      dockerfile: Dockerfile.wpcli
      context: .
    links:
      - mysql:mysql
    entrypoint: wp
    command: "--info"
    environment:
      WORDPRESS_DB_HOST: mysql:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wp-app
      WORDPRESS_DEBUG: 1
      WORDPRESS_TABLE_PREFIX: wp_
      WORDPRESS_CONFIG_EXTRA: |
        define('FS_METHOD', 'direct');
    volumes:
      - ./.srv/wordpress/:/var/www/html
      - ./.srv/log/:/var/log
      - ./custom.ini:/usr/local/etc/php/conf.d/custom.ini

  mysql:
    build:
      dockerfile: Dockerfile.mysql
      context: .
    restart: always
    ports:
      - 3306:3306
    volumes:
      - "./.srv/database:/var/lib/mysql"
    environment:
      MYSQL_ROOT_PASSWORD: wordpress
      MYSQL_DATABASE: wp-app
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
```

The `wordpress` container needs a `custom.ini` file which is the PHP configuration file.

Here it is :

```ini
file_uploads = On
memory_limit = 3072M
upload_max_filesize = 3072M
post_max_size = 3072M
max_execution_time = 1200
max_input_vars = 2000
default_socket_timeout = 7
```

I fixed the problem of scripts fetching external resources by setting a socket timeout.

Note also that the `docker-compose` sets `WORDPRESS_DEBUG` to `true` meaning that PHP warnings are displayed, which makes it handy for error-based SQL injections.

Still, this is not the default behavior so once the vulnerability is found you must set it to `false` and check if the vulnerability is exploitable with blind techniques.

Here is the Dockerfile for WordPress :

```docker
# Use the official WordPress image as the base image
FROM wordpress:latest

# Set the desired UID and GID for the www-data user
ARG WWW_DATA_UID=1000
ARG WWW_DATA_GID=1000

# Create a new user with the specified UID and GID
RUN usermod -u $WWW_DATA_UID www-data && groupmod -g $WWW_DATA_GID www-data
```

The one for WP-CLI :

```docker
# Use the official WordPress image as the base image
FROM wordpress:cli

# Set the desired UID and GID for the www-data user
# ARG WWW_DATA_UID=1000
# ARG WWW_DATA_GID=1000

# Set the desired UID and GID for the custom user
ARG CUSTOM_UID=1000
ARG CUSTOM_GID=1000

USER root
# Create the custom user
RUN addgroup -g $CUSTOM_GID custom-group && \
    adduser -D -u $CUSTOM_UID -G custom-group -s /bin/sh -h /var/www custom-user

    # Change ownership of the application directory to the existing www-data user and group
RUN chown -R custom-user:custom-group /var/www/html
USER custom-user
```

And finally, the one for MySQL :

```docker
FROM mysql:5.7

# Set the desired UID and GID for the www-data user
ARG MYSQL_UID=1000
ARG MYSQL_GID=1000

# Create a new user with the specified UID and GID
RUN usermod -u $MYSQL_UID mysql && groupmod -g $MYSQL_GID mysql
```

A problem that I didn't fix is the logs : they are written by the root user so cleaning them requires `sudo`.

They also grow quickly, so I had to regularly empty them.

One improvement would be to clean them after uninstalling each plugin. We could also rely on logs to spot vulnerabilities.

## Setting up the full thing

Here is the Bash script which was launching the containers, configuring the WordPress and creating a backup of the initial state.

```bash
docker compose up -d
sleep 20
docker-compose run --rm wpcli core install --title="My Site" --admin_user=admin --admin_password=changeme --admin_email=me@example.com --url=http://localhost:8000/ --allow-root
docker-compose run --rm wpcli term create category fun --description="This is gonna be fun"
docker-compose run --rm wpcli user create bob bob@example.com --role=author
docker-compose run --rm wpcli post create --post_title='Bob post' --post_content='Hello world' --meta_input='{"key1":"hi","key2":"there"}' --post_status=publish --post_category=fun --post_author=2 --tags_input=hello,world
docker-compose run --rm wpcli plugin delete akismet
docker-compose run --rm wpcli plugin delete hello
docker compose run --rm wpcli option update comment_previously_approved 0
mysqldump -u root -pwordpress -h 127.0.0.1 wp-app > dump.sql
find .srv/wordpress -type d -exec chmod 777 {} \;
rm -rf wordpress_backup 2> /dev/null
cp -r .srv/wordpress wordpress_backup
```

## Wapiti

Here is the script responsible for installing plugins, launching Wapiti and restoring the initial state :

```python
import os
from os.path import isfile
import subprocess

with open("plugins.txt") as fd:
    for plugin in fd:
        plugin = plugin.strip()

        if isfile(f"scans/{plugin}.json"):
            continue

        try:
            subprocess.check_output(
                    [
                        "docker-compose", "run", "--rm", "wpcli", "plugin", "install", plugin, "--activate", "--allow-root"
                    ],
                    stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as exception:
            if "plugin could not be found" in exception.output.decode(encoding="utf-8", errors="ignore"):
                # Allows to skip non-existent plugins if the script crash
                with open(f"scans/{plugin}.json", "w") as fd_out:
                    fd_out.write("{}")
                continue

        print(f"Installing {plugin}")
        subprocess.run(
                [
                    "wapiti",
                    "-u", "http://localhost:8000/",
                    "--color",
                    "--flush-session",
                    "-m", "exec,file,permanentxss,redirect,sql,ssrf,upload,xss,xxe",
                    "-f", "json",
                    "-o", f"scans/{plugin}.json",
                ]
        )

        os.system("/usr/bin/bash ./reinit.sh")
```

## Restore state

Here is the script that restored the initial state :

```bash
#!/usr/bin/bash
# remove content of wordpress directory
find .srv/wordpress/ -type f -name '.*' -exec rm -f {} \;
find .srv/wordpress/ -type d -name '.*' -exec rm -rf {} \;
rm -rf .srv/wordpress/*

# restore original files
cp -r wordpress_backup/* .srv/wordpress/

# get rid of permission issues
find .srv/wordpress/ -type d -exec chmod 777 {} \;

# drop the db
mysqladmin -u wordpress -pwordpress -f -h 127.0.0.1 drop wp-app
# recreate it
mysqladmin -u wordpress -pwordpress -f -h 127.0.0.1 create wp-app
# restore original data
mysql -u wordpress -pwordpress -h 127.0.0.1 wp-app < dump.sql
```

I had to remove everything under the web root but not the web root itself as Apache seems to keep the inode to that folder.

Removing the web root directly made Apache go crazy.

## Waiting

I started the scans in August 2023. If WordPress plugins weren't causing any troubles I could have installed them in bulks of 10 before scanning the WordPress with Wapiti.

Unfortunately if a single plugin breaks the WordPress it would have hidden potential vulnerabilities for other plugins.

I finally split the list of plugins over 3 computers and I let the scans run till January 2024.

## Vulnerabilities

I found a total of 36 vulnerabilities. No crazy stuff like a vulnerability that would impact 50% of existing Wordpress websites : most plugins here are old and not popular enough.

None of those vulnerabilities were previously found.

Note that while I may be the first to use a vulnerability scanner to scan WordPress plugins, some people are using code analysis tools to find vulnerabilities. That method may have missed vulnerabilities that Wapiti was able to find.

Still it shows that Wapiti is effective when it comes to vulnerability scanning.

Here is the list of vulnerabilities, each one has been documented on my website :

[SQL injection in ActivityTime]({% link _posts/2023-09-11-Injection-SQL-dans-le-plugin-Wordpress-ActivityTime.md %})

[SQL injection in Article Analytics]({% link _posts/2023-09-11-Injection-SQL-dans-le-plugin-Wordpress-Article-Analytics.md %})

[Cross-Site Scripting in AMP Plus]({% link _posts/2023-09-11-XSS-dans-le-plugin-Wordpress-AMP-Plus.md %})

[Cross-Site Scripting in Bee Classifieds]({% link _posts/2023-09-16-XSS-dans-le-plugin-Wordpress-Bee-Classifieds.md %})

[Cross-Site Scripting in Charjing For Subscription Billing]({% link _posts/2023-10-07-XSS-dans-le-plugin-Wordpress-Charjing-For-Subscription-Billing.md %})

[Open-Redirect in Clik Stats]({% link _posts/2023-10-10-Open-Redirect-dans-le-plugin-Wordpress-Clik-stats.md %})

[Cross-Site Scripting in Clickbank WordPress Storefront]({% link _posts/2023-10-10-XSS-dans-le-plugin-Clickbank-WordPress-Storefront.md %})

[Cross-Site Scripting in Comments Link Optimization]({% link _posts/2023-10-17-XSS-dans-le-plugin-Wordpress-Comments-Link-Optimization.md %})

[Cross-Site Scripting in easy AMP]({% link _posts/2023-10-19-XSS-dans-le-plugin-Wordpress-easy-AMP.md %})

[Cross-Site Scripting in EchBay Admin Security]({% link _posts/2023-11-22-XSS-dans-le-plugin-Wordpress-EchBay-Admin-Security.md %})

[SQL injection in FS Product Inquiry]({% link _posts/2023-12-18-Injection-SQL-dans-le-plugin-Wordpress-FS-Product-Inquiry.md %})

[Cross-Site Scripting in FS Product Inquiry]({% link _posts/2023-12-18-XSS-dans-le-plugin-Wordpress-FS-Product-Inquiry.md %})

[Cross-Site Scripting in JP Theme Switcher Bar]({% link _posts/2023-10-10-XSS-dans-le-plugin-Wordpress-JP-Theme-Switcher-Bar.md %})

[File inclusion in JS Job Manager]({% link _posts/2023-10-18-Faille-include-dans-le-plugin-Wordpress-JS-Job-Manager.md %})

[SQL injection in LeaderBoard Lite]({% link _posts/2023-10-18-Injection-SQL-dans-le-plugin-Wordpress-LeaderBoard-Lite.md %})

[Cross-Site Scripting in LH Login Page]({% link _posts/2023-10-20-XSS-dans-le-plugin-Wordpress-LH-Login-Page.md %})

[Cross-Site Scripting in Like DisLike Voting]({% link _posts/2023-10-21-XSS-dans-le-plugin-Wordpress-Like-DisLike-Voting.md %})

[SQL injection in LogDash Activity Log]({% link _posts/2023-10-26-Injection-SQL-dans-le-plugin-Wordpress-LogDash-Activity-Log.md %})

[SQL injection in Loginplus]({% link _posts/2023-10-26-Injection-SQL-dans-le-plugin-Wordpress-Loginplus.md %})

[Open-Redirect in Multipurpose CSS3 Animated Buttons]({% link _posts/2023-11-12-Open-Redirect-dans-le-plugin-Wordpress-Multipurpose-CSS3-Animated-Buttons.md %})

[Cross-Site Scripting in NanoSupport Support Ticketing Knowledgebase for WordPress]({% link _posts/2023-11-12-XSS-dans-le-plugin-Wordpress-NanoSupport-Support-Ticketing-Knowledgebase-for-WordPress.md %})

[Cross-Site Scripting in NS Simple Intro Loader]({% link _posts/2023-11-19-XSS-dans-le-plugin-Wordpress-NS-Simple-Intro-Loader.md %})

[SSRF in OpenID]({% link _posts/2023-11-23-SSRF-dans-le-plugin-Wordpress-OpenID.md %})

[Cross-Site Scripting in Peters Custom Anti-Spam Image]({% link _posts/2023-11-30-XSS-dans-le-plugin-Wordpress-Peters-Custom-Anti-Spam-Image.md %})

[Cross-Site Scripting in Post Like Dislike]({% link _posts/2023-12-06-XSS-dans-le-plugin-Wordpress-Post-Like-Dislike.md %})

[SQL injection in Posts Logs And Tracking]({% link _posts/2023-12-07-Injection-SQL-dans-le-plugin-Wordpress-Posts-Logs-And-Tracking.md %})

[File inclusion in PS PHPCaptcha WP]({% link _posts/2023-12-16-Faille-include-dans-le-plugin-Wordpress-PS-PHPCaptcha-WP.md %})

[Cross-Site Scripting in qrLogin]({% link _posts/2023-12-19-XSS-dans-le-plugin-Wordpress-qrLogin.md %})

[Cross-Site Scripting in Real Simple Contact Form]({% link _posts/2023-12-24-XSS-dans-le-plugin-Wordpress-Real-Simple-Contact-Form.md %})

[Cross-Site Scripting in Reservation]({% link _posts/2023-12-31-XSS-dans-le-plugin-Wordpress-Reservation.md %})

[Cross-Site Scripting in TM Wordpress Redirection]({% link _posts/2023-11-22-XSS-dans-le-plugin-Wordpress-TM-Wordpress-Redirection.md %})

[Cross-Site Scripting in Valz Display Query Filters]({% link _posts/2023-11-12-XSS-dans-le-plugin-Wordpress-Valz-Display-Query-Filters.md %})

[Cross-Site Scripting in Verifyne]({% link _posts/2023-11-12-XSS-dans-le-plugin-Wordpress-Verifyne.md %})

[SSRF in Webmention]({% link _posts/2023-11-03-SSRF-dans-le-plugin-Wordpress-Webmention.md %})

[File inclusion in WP-Game]({% link _posts/2023-10-18-Faille-include-dans-le-plugin-Wordpress-WP-Game.md %})

[Cross-Site Scripting in XYZZY Basic SEO and-Analytics]({% link _posts/2023-09-16-XSS-dans-le-plugin-Wordpress-XYZZY-Basic-SEO-and-Analytics.md %})
