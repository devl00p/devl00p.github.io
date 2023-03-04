#!/usr/bin/env python
# devloop.lyua.org 06/2009
import sys
from unicodedata import normalize
import os

conv = {}
conv['3'] = u'\u0417' # 3
conv['5'] = u"\u01BC" # 5
conv[';'] = u"\u037E" # ;
conv['a'] = u"\u0430" # a
conv['c'] = u"\u0441" # c
conv['e'] = u"\u0435" # e
conv['h'] = u"\u04BA" # h
conv['i'] = u"\u0456" # i
conv['j'] = u"\u0458" # j
conv['o'] = u"\u043E" # o
conv['p'] = u"\u0440" # p
conv['s'] = u"\u0455" # s
conv['u'] = u"\u03C5" # u
conv['v'] = u"\u03BD" # v
conv['x'] = u"\u0445" # x
conv['y'] = u"\u0443" # y
conv['A'] = u"\u0391" # A
conv['B'] = u"\u0412" # B
conv['C'] = u"\u0421" # C
conv['E'] = u"\u0415" # E
conv['F'] = u"\u03DC" # F
conv['G'] = u"\u13C0" # G
conv['H'] = u"\u041D" # H
conv['I'] = u"\u0406" # I
conv['J'] = u"\u0408" # J
conv['K'] = u"\u041A" # K
conv['L'] = u"\u216C" # L
conv['M'] = u"\u041C" # M
conv['N'] = u"\u039D" # N
conv['O'] = u"\u041E" # O
conv['P'] = u"\u0420" # P
conv['S'] = u"\u0405" # S
conv['T'] = u"\u03A4" # T
conv['X'] = u"\u0425" # X
conv['Y'] = u"\u04AE" # Y
conv['Z'] = u"\u0396" # Z

# chr(255).decode("ISO-8859-1") => unicode
# fd.write(chr(255).decode("ISO-8859-1").encode("UTF-8"))
# normalize("NFD",u) decompose
# normalize("NFC",u) canonique
# >=192 && <=255

def int2bin(n, count=8):
  return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

def hide_in_char(c,b,html,force=0):
  val=""

  if c in conv.keys():
    if b == 0:
      val = c.decode("ISO-8859-1")
    else:
      val = conv[c]
  elif ord(c)>= 192 and ord(c)<=255:
    if b == 0:
      val = c.decode("ISO-8859-1")
    else:
      val = normalize("NFD",c.decode("ISO-8859-1"))
  else:
    if force == 1:
      val = c.decode("ISO-8859-1")
    else:
      return False

  if html == 0:
    return val.encode("UTF-8")
  else:
    return val.encode('ascii', 'xmlcharrefreplace')

# print repr(hide_in_char(chr(80),1,1))
# print repr(hide_in_char(chr(235),1,1))

if len(sys.argv)<3:
  print "Usage: python hide.py file_to_hide ascii_text_file [html]"
  sys.exit()
try:
  fd=open(sys.argv[1])
except IOError:
  print "file not found"
  sys.exit()

data=[]
print "Input file size:", os.path.getsize(sys.argv[1])

ascii7=1
lowerc=0
upperc=0
numeric=0
basicc=0
specialc=0
basic=" \n.?!,:-/'\""

# 63 chars (6 bits) charset
charsets={}
charsets["alphanumspace"] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
charsets["alphabasic"]    = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \n.?!,:-/'\""
charsets["lowernumbasic"] = "abcdefghijklmnopqrstuvwxyz0123456789 \n.?!,;:-/'\"@&()+*=<>_#$%|\\"
charsets["uppernumbasic"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \n.?!,;:-/'\"@&()+*=<>_#$%|\\"
charsets["english"]       = "etaoinshrdlcumwfgypbETAOINSHRDLCUMWFGYPB \n.?!,;:-/'\"@&()+*_#$%\\"
charsets["french"]        = "esaitnrulodcpmvqfbghESAITNRULODCPMVQFBGH \n.?!,;:-/'\"@&()+*_#$%\\"

buff=fd.read()
fd.close()

for c in buff:
  if ord(c)>127:
    ascii7=0
  if ord(c)>60 and ord(c)<123:
    lowerc=1
  elif ord(c)>64 and ord(c)<91:
    upperc=1
  elif ord(c)>47 and ord(c)<58:
    numeric=1
  elif c in basic:
    basicc=1
  else:
    specialc=1

  if c not in data:
    data.append(c)

x=len(data)-1
charset=""

i=0
n=x
while True:
  n = n>>1
  i+=1
  if n == 0:
    break

if i==8:
  print "nbit: 8"
  print "charset: iso"
elif i==7:
  if ascii7==1:
    print "nbit: 7"
    print "charset: ascii"
  else:
    i=8
    print "nbit: 8"
    print "charset: iso"
elif i==6:
  print "nbit: 6"
  for k,v in charsets.items():
    ok=1
    for c in buff:
      if c not in v:
        ok=0
    if ok==1:
      print "charset:",k
      data=charsets[k]
      charset=data
      break
  if ok==0:
    data.sort()
    for x in data:
      charset+="%02x" % ord(x)
    print "charset:",charset
else:
  print "nbit:",i
  data.sort()
  for x in data:
    charset+="%02x" % ord(x)
  print "charset:",charset


fd=open(sys.argv[2])
text=fd.read()
fd.close()
if len(text)<len(buff)*i:
  print "Error: we need",len(buff)*i,"characters to hide the data"
  sys.exit()

n = 0
html = 0
if "html" in sys.argv:
  html = 1
output_char = ''
x = 0

fd=open("out.txt","w")
for c in buff:
  # Use a predefined charset or a custom charset
  if charset!="":
    s=int2bin( data.index(c), i)

    x = 0
    while x < len(s):
      b = s[x]

      # test if the character is exploitable
      output_char = hide_in_char(text[n], int(b), html)

      # not exploitable => simply convert to UTF-8
      # don't hide bit
      if output_char == False:
        fd.write( hide_in_char(text[n], 0, html, 1) )

      # exploitable => hide the bit
      # move to next bit
      if output_char != False:
        fd.write(output_char)
        sys.stdout.write(b)
        x += 1

      # move to next char
      n+=1

  # Simple ascii conversion (7 or 8 bits)
  else:
    s=int2bin( ord(c), i)
    x = 0

    while x < len(s):
      b = s[x]

      output_char = hide_in_char(text[n], int(b), html)

      if output_char == False:
        fd.write( hide_in_char(text[n], 0, html, 1) )

      if output_char != False:
        fd.write(output_char)
        sys.stdout.write(b)
        x += 1

      n+=1

while n<len(text):
  fd.write(text[n])
  n+=1
fd.close()
print
