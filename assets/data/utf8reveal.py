#!/usr/bin/env python
# devloop.lyua.org 06/2009
import sys
from unicodedata import normalize
from htmlentitydefs import name2codepoint as n2cp
import re
import codecs


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

def substitute_entity(match):
  ent = match.group(3)
  
  if match.group(1) == "#":
    if match.group(2) == '':
      return unichr(int(ent))
    elif match.group(2) == 'x':
      return unichr(int('0x'+ent, 16))
  else:
    cp = n2cp.get(ent)

    if cp:
      return unichr(cp)
    else:
      return match.group()

def decode_htmlentities(string):
  entity_re = re.compile(r'&(#?)(x?)(\d{1,5}|\w{1,8});')
  return entity_re.subn(substitute_entity, string)[0]

def is_exploitable(c):
  ok = 0

  if c in conv.keys():
    ok = 1
  elif ord(c)>= 192 and ord(c)<=255:
    ok = 1

  return ok

# print repr(hide_in_char(chr(80),1,1))
# print repr(hide_in_char(chr(235),1,1))

if len(sys.argv)!=6:
  print "Usage: python reveal.py ascii_text_file utf8_text_file nbits charset filesize"
  sys.exit()
try:
  fd=open(sys.argv[1])
except IOError:
  print "file not found"
  sys.exit()

data=[]
nbit = int(sys.argv[3])
fsize = long(sys.argv[5])

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
charsets["iso"]   = ""
charsets["ascii"] = ""

charset = sys.argv[4]
char_index = ""
if charset in charsets.keys():
  char_index = charsets[charset]
else:
  char_index = charset.decode("hex_codec")



ascii_text = fd.read()
fd.close()

fd = codecs.open(sys.argv[2], "r", "UTF-8")
utf8_text = fd.read()
fd.close()
utf8_text = decode_htmlentities(utf8_text)

n = 0
html = 0
output_char = ''
x = 0
char_tab = []

while x<len(utf8_text):
  if x<len(utf8_text)-1 and ord(utf8_text[x+1])>=768 and ord(utf8_text[x+1])<=879:
    char_tab.append(utf8_text[x:x+2])
    x += 1
  else:
    char_tab.append(utf8_text[x])
  x += 1

bit_string = ""

fd=open("secret.xxx","w")
total = 0

def add_bit(b):
  global charset
  global char_index
  global bit_string
  global fd
  global total

  # add the bit to the current byte
  bit_string += b

  # if we have enough bit for a char
  if len(bit_string) == nbit:
    # conversion to a byte
    n = int(bit_string, 2)
    if charset == "ascii" or charset == "iso":
      fd.write(chr(n))
    # use custom charset
    else:
      fd.write(char_index[n])
    # empty
    bit_string = ""
    total += 1
    if total == fsize:
      return False
  return True

x = 0
i = 0

for c in ascii_text:
  if is_exploitable(c):
    if c in conv.keys():
      if conv[c] == char_tab[x]:
        if add_bit('1') == False:
          break
      else:
        if add_bit('0') == False:
          break
    else:
      if normalize("NFD",unicode(c,"ISO-8859-1")) == char_tab[x]:
        if add_bit('1') == False:
          break
      else:
        if add_bit('0') == False:
          break
  x += 1

fd.close()
