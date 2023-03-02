---
title: "Faire un système de joker en Python"
tags: [Coding, Python]
---

Les expressions régulières, c'est bien... et c'est plutôt simple à intégrer dans un code. Mais quand il s'agit de faire une application qui propose son propre système d'expressions régulières ça fait mal.  

C'est un problème sur lequel je me suis penché sur [Wapiti](http://wapiti.sourceforge.net/) afin de permettre aux utilisateurs d'exclure les urls correspondant à certaines expressions.  

Mais gérer tous les caractères spéciaux des expressions régulières n'est pas vraiment ce que je cherche étant donné que l'exclusion d'une URL se fera probablement sur un pattern (masque de filtrage) simple et de plus je vois mal quelqu'un tapper des expressions régulières en ligne de commande (sans compter qu'il faudra échapper les caractères spéciaux de bash).  

Donc j'ai préféré écrire un système d'expression régulière se limitant au joker (l'astérisque ou wildcard en anglais), comme celui utilisé par Opera pour bloquer les pubs (`urlfilter.ini`).  

```python
#!/usr/bin/env python
import re

def starmatch(regexp,string):
  regexp = re.sub("\*+","*",regexp)
  match = True
  if not regexp.count("*"):
    if regexp == string:
      return True
    else:
      return False
  blocks = regexp.split("*")
  start = ""
  end = ""
  if not regexp.startswith("*"):
    start = blocks[0]
  if not regexp.endswith("*"):
    end = blocks[-1]
  if start != "":
    if string.startswith(start):
      blocks = blocks[1:]
    else:
      return False
  if end:
    if string.endswith(end):
      blocks = blocks[:-1]
    else:
      return False
  blocks = [block for block in blocks if block!=""]
  if not blocks:
    return match
  for block in blocks:
    i = string.find(block)
    if i == -1: return False
    string = string[i+len(block):]
  return match
```

Quelques tests que j'ai effectués :
```
regexp=*plop*, string=http://plop : True  
regexp=*plop*, string=plop : True  
regexp=*plop, string=plop8 : False  
regexp=*plop*truc, string=http://ploptruc : True  
regexp=*plop*truc, string=http://ploptruca : False  
regexp=*plop*truc*, string=http://ploptruca : True  
regexp=plop*a*c*truc, string=plopbabctruc : True  
regexp=plop*c*a*truc, string=plopbabctruc : False  
regexp=plop*a*c*, string=plop : False  
regexp=*plop*, string=ploplop : True  
regexp=*plop, string=ploplop : True  
regexp=plop*, string=ploplop : True  
```

Ca fonctionne :)

*Published January 07 2011 at 10:36*
