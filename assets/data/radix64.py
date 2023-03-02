#!/usr/bin/env python
# devloop.lyua.org 9/2007
import base64

def _CRC24(data="",size=0):
  crc=0xb704ce
  i=0
  j=0

  for temp in range(0,size):
    crc=crc^ord(data[j])<<16
    for i in range(0,8):
      crc=crc<<1
      if crc&0x1000000!=0:
        crc=crc^0x1864cfb
    j=j+1
  return crc&0xffffff

def signature(data=""):
  x="%x" % _CRC24(data,len(data))
  x=x.rjust(6,'0')
  return "="+base64.b64encode(x.decode("hex_codec"))
  

def _divide(seq, size): 
  return [seq[i:i+size] for i in xrange(0,len(seq),size)]

def r64encode(data=""):
  output=_divide(base64.b64encode(data),64)
  output.append(signature(data))
  return output

def r64decode(data=[]):
  if data==[]:
    return ""
  if data[-1].startswith("="):
    c=""
    for x in data[0:-1]:
      c+=x
    m=base64.b64decode(c)
    s=signature(m)
    if s==data[-1]:
      return m
    else: return "CRC Error"
