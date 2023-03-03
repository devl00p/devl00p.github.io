---
title: "Cassage de captchas faibles"
tags: [captcha, Coding, Python]
---

J'utilise depuis un moment le service en ligne de [ADrive](http://www.adrive.com/) et je ne pouvais forcément que tiquer sur la page *"You're not a robot, right?"* qui apparait juste après la saisie des identifiants et demande de recopier un [captcha](http://fr.wikipedia.org/wiki/Captcha) numérique.  

Déjà je me suis dit que coder une API ou un outil pour ce site ne serait pas une mauvaise idée (on verra éventuellement ça) mais aussi, c'était une bonne occasion de se pencher sur la sécurité d'un système de captcha qui a première vue m'a semblé plutôt faible.  

Je ne m'étendrais pas sur ce qui fait le bon ou le mauvais captcha, le sujet a déjà été débattu ailleurs (surtout dans le *Bouchonnois*)  

Je dirais seulement que globalement un bon captcha trompe les OCR et a un alphabet (nombre de caractères utilisés différents) conséquent.  

Les captchas de ADrive sont assez limités, car l'alphabet est limité à 9 caractères (nombres entiers de 1 à 9 inclus), le captcha étant long de 5 caractères.  
Voici quelques exemples :  

![13125](/assets/img/13125.jpeg)

![25519](/assets/img/25519.jpeg)

![43588](/assets/img/43588.jpeg)

![55962](/assets/img/55962.jpeg)

![62136](/assets/img/62136.jpeg)

![77141](/assets/img/77141.jpeg)

![86154](/assets/img/86154.jpeg)

![91522](/assets/img/91522.jpeg)

On remarque que le fond de chaque nombre lui est propre et ne change pas. Les caractères sont toujours disposés à la même hauteur... il s'agit uniquement d'un recollage.  

Première idée qui me vient à l'esprit : on retire le cadre, on découpe en 5 images, on calcule des hashes MD5 sur chaque image extraite et on en déduit le nombre.  

Avec ImageMagick, les opérations de découpage sont simples :  

```bash
convert captcha.jpg -shave 2x2 out.jpg
convert out.jpg -crop 5x1@ montage_%d.jpg
```

Mais on s'aperçoit que cela ne fonctionne pas : pour deux nombres identiques on a un hash différent.  

On étudie en détail les images et on remarque que la division en 5 n'a pas donné des images de taille égale.  

Quelque chose cloche et il s'avère en réalité que l'espace pris par les différents caractères diffère.  

On sort un éditeur photo et on compte les pixels pour obtenir la largeur de quelques nombres. Ensuite les largeurs des autres caractères peuvent être déterminées par des équations à plusieurs inconnues (merci le bac S)  

Cette fois, on va faire autrement, mais toujours sans utiliser de technologie OCR : lire les pixels correspondant au premier caractère, déterminer duquel il s'agit en testant des points caractéristiques et procéder de même avec les suivants.  

Pour cela j'utilise la [Python Imaging Library](http://www.pythonware.com/library/pil/handbook/index.htm).  

La valeur de chaque pixel des captchas est représentée par 3 valeurs (R, V, B). Plus les valeurs sont faibles plus le pixel est sombre, plus elles sont élevées plus il est clair.  

Je choisis de modifier l'image pour mettre à 0 les pixels sombres au delà d'un certain seuil (40) et mettre blanc (soit 255) les autres :  

```python
from PIL import Image

im = Image.open("62136.jpeg")
(xlen, ylen) = im.size

# Conversion noir OU blanc
for x in range(0, xlen):
  for y in range(0, ylen):
    couleur = im.getpixel((x, y))
    if all(z < 40 for z in couleur):
      im.putpixel((x, y), (0, 0, 0))
    else:
      im.putpixel((x, y), (255, 255, 255))

im.save("62136_wb.jpeg")
```

Le résultat ressemble à ceci (avant et après) :  

![62136](/assets/img/62136.jpeg)

![62136_wb](/assets/img/62136_wb.jpeg)

Il faut ensuite trouver des points caractéristiques pour chaque caractère. Par exemple le '2' comporte une suite horizontale de pixels noirs qu'aucun autre caractère ne possède.  

On se charge de lire sur 17 pixels de largeur (largeur minimale d'un caractère), tester la présence de certains pixels puis avancer notre pointeur de la largeur du caractère trouvé.  

Pour certains caractères (le '6' notamment) c'est plus compliqué car on rencontre pas mal de collisions (pixels communs à d'autres caractères) mais je suis finalement parvenu à écrire le programme suivant qui décode avec succès les captchas du site (testé toutefois seulement sur 33 captchas différents) :  

```python
# devloop 08/2010
# Adrive.com captcha breaker
from PIL import Image
import sys

if len(sys.argv) != 2:
  print "Usage: python captcha_break.py <file>"
  sys.exit()

largeurs = {1 : 19, 2 : 17, 3 : 18, 4 : 18,
    5 : 18, 6 : 18, 7 : 18, 8 : 21, 9 : 18}

im = Image.open(sys.argv[1])
(xlen, ylen) = im.size

# Conversion noir OU blanc
for x in range(0, xlen):
  for y in range(0, ylen):
    couleur = im.getpixel((x, y))
    if all(z < 40 for z in couleur):
      im.putpixel((x, y), (0, 0, 0))
    else:
      im.putpixel((x, y), (255, 255, 255))

captcha = ""

# On retire la bordure du captcha, on avance dans la largeur
xdecal = 2

# 5 nombres
for n in range(0,5):
  if all((0,0,0) == im.getpixel((xdecal + x, 29)) for x in range(4,15)):
    captcha += "2"
    xdecal += largeurs[2]

  elif im.getpixel((xdecal + 3, 16)) == (0, 0, 0):
    captcha += "4"
    xdecal += largeurs[4]

# fail (pixels provoquant des collisions) : (2, 21) (2, 22)
  elif im.getpixel((xdecal + 3, 17)) == (0, 0, 0):
    captcha += "8"
    xdecal += largeurs[8]

# fail : (4, 15) (15, 4) (8, 8) (13, 19) (13, 20)
# fail : (13, 21) (13, 23) (13, 24) (13, 25)
# fail : (3, 18) (3, 19) (3, 20) (3, 21)
  elif im.getpixel((xdecal + 3, 22)) == (0, 0, 0):
    captcha += "6"
    xdecal += largeurs[6]

  elif im.getpixel((xdecal + 3, 2)) == (0, 0, 0):
    captcha += "9"
    xdecal += largeurs[9]

  elif im.getpixel((xdecal + 3, 30)) == (0, 0, 0):
    captcha += "1"
    xdecal += largeurs[1]

  elif im.getpixel((xdecal + 14, 3)) == (0, 0, 0):
    captcha += "5"
    xdecal += largeurs[5]

# fail : (9, 16) (3, 18) (3, 19) (3, 20)
  elif im.getpixel((xdecal + 2, 25)) == (0, 0, 0):
    captcha += "3"
    xdecal += largeurs[3]

  elif im.getpixel((xdecal + 2, 12)) == (0, 0, 0):
    captcha += "7"
    xdecal += largeurs[7]

  else:
    # Nombre non trouve. Affiche l'image et donne le
    # tableau des pixels noirs.
    im.show()
    # affiche les caractères deja trouves
    if len(captcha) > 0:
      print captcha
    for x in range(0, 17):
      for y in range(2, 31):
        if im.getpixel((xdecal + x, y)) == (0,0,0):
          print x, y
    break

if len(captcha) == 5:
  print captcha
```

Le code est aussi téléchargeable ici : [captcha_break.py](/assets/data/captcha_break.py)  
Comme quoi si l'alphabet utilisé est limité on arrive à casser en peu de temps un captcha quelques soit les caractères ou les symboles présents.

*Published January 11 2011 at 17:24*
