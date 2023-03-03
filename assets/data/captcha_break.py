# devloop 08/2010
# Adrive.com captcha breaker
from PIL import Image
import sys

def break_captcha(fichier):
#if len(sys.argv) != 2:
#  print "Usage: python captcha_break.py <file>"
#  sys.exit()

  largeurs = {1 : 19, 2 : 17, 3 : 18, 4 : 18,
      5 : 18, 6 : 18, 7 : 18, 8 : 21, 9 : 18}

  try:
    im = Image.open(fichier)
  except IOError:
    return "error"
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
  for n in range(0,5):
    if all((0,0,0) == im.getpixel((xdecal + x, 29)) for x in range(4,15)):
      captcha += "2"
      xdecal += largeurs[2]

    elif im.getpixel((xdecal + 3, 16)) == (0, 0, 0):
      captcha += "4"
      xdecal += largeurs[4]

  # fail : (2, 21) (2, 22)
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
      # affiche les caracteres deja trouves
      if len(captcha) > 0:
        print captcha
      for x in range(0, 17):
        for y in range(2, 31):
          if im.getpixel((xdecal + x, y)) == (0,0,0):
            print x, y
      break

  if len(captcha) == 5:
    print captcha
    return captcha
