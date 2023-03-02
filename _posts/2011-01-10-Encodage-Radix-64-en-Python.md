---
title: "Encodage Radix-64 en Python"
tags: [Coding, Python]
---

Le [Radix-64](http://en.wikipedia.org/wiki/Radix-64), aussi connu sous le nom de *ASCII Armor*, est une méthode d'encodage utilisée par les logiciels de chiffrement de mails comme *OpenPGP* et *GnuPG* pour transformer des données chiffrées brutes en une version textuelle qui convient mieux au protocole SMTP.  

Comme l'explique le chapitre 6 de la [RFC 2440 : OpenPGP Message Format](http://tools.ietf.org/html/rfc2440), le Radix-64 n'est rien de plus que l'encodage [Base64](http://en.wikipedia.org/wiki/Base64) SAUF QUE :  

* les données encodées en base64 doivent être découpées en lignes de longueur égale. La taille de ces lignes ne doit pas dépasser les 76 caractères (la convention est de faire des lignes de 64 caractères).
* une ligne complémentaire correspondant à la somme de contrôle des données sur 24 bits (CRC24), encodée en base64 et précédée du caractère `=` doit suivre les données précédentes.

L'exemple présent dans la RFC est le suivant :  

```
-----BEGIN PGP MESSAGE-----  
Version: OpenPrivacy 0.99  

yDgBO22WxBHv7O8X7O/jygAEzol56iUKiXmV+XmpCtmpqQUKiQrFqclFqUDBovzS  
vBSFjNSiVHsuAA==  
=njUN  
-----END PGP MESSAGE-----
```  

J'ai écrit un code en Python qui se charge de l'encodage et du décodage de données en Radix-64 : [Télécharger radix64.py](/assets/data/radix64.py)

```python
#!/usr/bin/env python2
# devloop.lyua.org 9/2007
import base64

def _CRC24(data="",size=0):
  crc = 0xb704ce
  i = 0
  j = 0

  for temp in range(0, size):
    crc = crc ^ ord(data[j]) << 16
    for i in range(0,8):
      crc = crc << 1
      if crc & 0x1000000 != 0:
        crc = crc ^ 0x1864cfb
    j = j + 1
  return crc & 0xffffff

def signature(data=""):
  x = "%x" % _CRC24(data,len(data))
  x = x.rjust(6,'0')
  return "=" + base64.b64encode(x.decode("hex_codec"))

def _divide(seq, size):
  return [seq[i:i+size] for i in xrange(0,len(seq), size)]

def r64encode(data=""):
  output = _divide(base64.b64encode(data),64)
  output.append(signature(data))
  return output

def r64decode(data):
  if not data:
    return ""
  if data[-1].startswith("="):
    c = ""
    for x in data[0:-1]:
      c += x
    m = base64.b64decode(c)
    s = signature(m)
    if s == data[-1]:
      return m
    else: return "CRC Error"
```

La fonction d'encodage prend un string en entrée et retourne un tableau de lignes. La fonction de décodage fonctionne dans le sens inverse (logique).  

Exemple d'utilisation des fonctions Radix-64 :  

```python
#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import radix64
c = radix64.r64encode("La mode est une forme de laideur si intolérable qu'il faut en changer tous les six mois.\n\t-+- Oscar Wilde -+-")
for x in c:
  print x
print radix64.r64decode(c)
```

On obtient :  

```plain
TGEgbW9kZSBlc3QgdW5lIGZvcm1lIGRlIGxhaWRldXIgc2kgaW50b2zDqXJhYmxl
IHF1J2lsIGZhdXQgZW4gY2hhbmdlciB0b3VzIGxlcyBzaXggbW9pcy4KCS0rLSBP
c2NhciBXaWxkZSAtKy0=
=5lNi
La mode est une forme de laideur si intolérable qu'il faut en changer tous les six mois.
        -+- Oscar Wilde -+-
```

*Published January 10 2011 at 08:05*
