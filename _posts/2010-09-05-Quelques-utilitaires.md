---
title: "Quelques utilitaires dont je suis l'auteur"
tags: [Coding]
---

J'ai quelques (très) vieux codes que j'ai fait par le passé que j'ai conservé et qui pourraient peut-être intéresser les curieux.

## lzcrack 1.0: Casseur d'archives ZIP protégées

Aka _Linux Zip Cracker_, un casseur de mots de passe d'archive ZIP.

Il effectue une attaque par force-brute sur le système de protection "historique" par mot de passe implémenté par PKZip (en opposition aux protections contemporaines comme AES).

Contrairement à ses concurrents de l'époque sous Linux, il ne fait pas appel à l'outil d'archivage externe `unzip` pour tester les mots de passe : j'avais écrit à l'époque l'algorithme directement en C ce qui le rendait plus rapide.

Aujourd'hui je ne peux que conseiller d'utiliser `zip2john` + `John The Ripper` mais j'étais fier d'avoir passé du temps à fouiller dans les spécifications du format ZIP.

[lzcrack-1.0.tar.gz](/assets/data/lzcrack-1.0.tar.gz)

## Spock : Détection de scan de ports

Un programme permettant de détecter les scans de ports TCP. Fonctionne sous Linux uniquement.

Il se base sur l'idée qu'une tentative de connexion sur un port fermé est suspecte.

Il ouvre l'interface réseau en mode RAW et pour chaque demande de connexion compare le port demandé à la liste des ports TCP fermés.

Le logiciel est susceptible de donner des faux-positifs.

[spock.c](/assets/data/spock.c)

## Python ascii85

L'ASCII-85 est un algorithme d'encodage au format texte qui utilise un alphabet plus large que le plus connu base64.

Par conséquent, on économise de la place par rapport au base64.
C'est une librairie 100% Python.

[ascii85.py](/assets/data/ascii85.py)

## VXcloud : Un antivirus sur le "cloud" pour Linux

Ce script Python utilise deux services de détection de malwares en ligne : _Malware Hash Registry_ de la _Team Cymru_ et _VirusTotal_.

Ces deux services fonctionnent grâce à de gigantesques bases de données de hashes MD5 des fichiers connus pour être des malwares.

_VXcloud_ se propose de scanner les fichiers que vous souhaitez sur votre machine et d'envoyer leur hash à ces services pour déterminer s'ils sont néfastes.

Bien que l'analyse par hash MD5 uniquement ne soit pas la plus efficace, ces services ont recours à une quarantaine d'antivirus différents ce qui loin d'être négligeable !

[vxcloud2.py](/assets/data/vxcloud2.py)

## py_cgi_srv : Serveur de CGI 100% Python

Voici un serveur HTTP minimaliste développé en Python capable de renvoyer des pages statiques, mais aussi des pages dynamiques... codées elles aussi en Python.

Le serveur fonctionne aussi bien sous Windows que Linux et peut facilement être adapté pour exécuter d'autres langages de scripts (Perl, Ruby etc)

[py_cgi_srv.py](/assets/data/py_cgi_srv.py)
