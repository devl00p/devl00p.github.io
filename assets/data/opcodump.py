#!/usr/bin/env python
# devloop.lyua.org - 04/2009
from struct import *
import sys

fmt="xBHII"

print "Opera Cookie Dumper"
if len(sys.argv)!=2:
  print "Usage python opcodump.py <opera_file>"
  sys.exit()

fd=open(sys.argv[1],"r")
(file_version_number,app_version_number,idtag_length,length_length)=unpack(">IIHH",fd.read(12))

major_fv=file_version_number>>12
minor_fv=file_version_number&4095
print "File version: %d.%d" % (major_fv, minor_fv)

major_av=app_version_number>>12
minor_av=app_version_number&4095
print "Application version: %d.%d" % (major_av, minor_av)
if major_av==2:
  print "Cookie file"
elif major_av==32:
  print "Cache file"
print "Size of idtags:",idtag_length,"bytes"
print "Size of payload length fields:",length_length,"bytes"
MSB=1<<(idtag_length*8)-1
print "MSB: %#x" % MSB
print "==================================="

domain=[]
tags=[]
printed=0

while True:
  # lecture du tag
  data=fd.read(idtag_length)
  if data=="":
    break
  tag=unpack(">"+fmt[idtag_length],data)[0]

  # !! TAGS TERMINATORS !!
  # Path component terminator
  if tag==5|MSB:
    if tags!=[]: tags.pop()
    continue
  # Domain component terminator
  elif tag==4|MSB:
    if domain!=[]: domain.pop(0)
    if tags!=[]: tags.pop()
    printed=0
    continue

  # !! FLAGS !!
  # flag: The cookie will only be sent to HTTPS servers.
  elif tag==0x19|MSB:
    continue
  # flag: This cookie will only be sent to the server that sent it.
  elif tag==0x1B|MSB:
    continue
  # flag: Reserved for delete protection: Not yet implemented
  elif tag==0x1C|MSB:
    continue
  # flag: This cookie will not be sent if the path is only a prefix of the URL.
  # If the path is /foo, /foo/bar will match but not /foobar.
  elif tag==0x20|MSB:
    continue
  # flag:
  # If true, this cookie was set as the result of a password login form,
  # or by a URL that was retrieved using a cookie that can be tracked
  # back to such a cookie.
  elif tag==0x22|MSB:
    continue
  # flag:
  # If true, this cookie was set as the result of a HTTP authentication login,
  # or by a URL that was retrieved using a cookie that can be tracked back
  # to such a cookie.
  elif tag==0x23|MSB:
    continue
  # flag:
  # In "Display Third party cookies" mode this flag will be set if the cookie
  # was set by a third party server, and only these cookies will be sent if
  # the URL is a third party. Cookies that were received when loading a URL
  # from the server directly will not be sent to third party URLs in this mode.
  # The reverse is NOT true.
  elif tag==0x24|MSB:
    continue
  # It's probably a flag but undocumented
  elif tag==0x27|MSB:
    continue


  # If where are here it means the tag is followed by a length indicator
  data=fd.read(length_length)
  if data=="":
    break
  length=unpack(">"+fmt[length_length],data)[0]


  # !! START TAGS !!
  # domain record
  if tag==1:
    tags.append(tag)
  # path record
  elif tag==2:
    tags.append(tag)
    if printed==0:
      print ".".join(domain)
      printed=1

  # Following tags (till end of the file) don't have a tag terminator
  # cookie record
  elif tag==3:
    if printed==0:
      print ".".join(domain)
      printed=1
    pass

  # The name of the domain part
  elif tag==0x1e:
    s=fd.read(length)
    domain.insert(0,s)
  
  # The name of the cookie
  elif tag==0x10:
    sys.stdout.write("\t"+fd.read(length)+"  = ")
  # The value of the cookie
  elif tag==0x11:
    print fd.read(length)

  # Comment/Description of use (RFC 2965)
  elif tag==0x14:
    sys.stdout.write("\t# "+fd.read(length)+" : ")
  # URL for Comment/Description of use (RFC 2965)
  elif tag==0x15:
    print fd.read(length)

  # The name of the path part
  elif tag==0x1d:
    print "\tpath = /"+fd.read(length)

  # Informations on Version=1 cookies
  elif tag in [0x16,0x17,0x18]:
    if length>0:
      print fd.read(length)

  # Some time and int8 values
  elif tag in [0x12,0x13,0x1f,0x21,0x25]:
    time=fd.read(length)

  elif tag==0x26:
    data=fd.read(length)
    x=unpack(">"+fmt[length],data)[0]
    # if x==2 then it means "Delete new cookies when exiting Opera is checked".
    # else it's not checked or set to 1
  else:
    # Unknown tag ^_^
    print "tag: %#x" % tag
    print "\tbody length: %d" % length
    fd.read(length)
fd.close()
