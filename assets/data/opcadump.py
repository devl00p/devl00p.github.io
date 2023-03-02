#!/usr/bin/env python
# Opera Cache Python Dumper
# devloop.lyua.org - 04/2009
from struct import *
import sys
import time
import cgi
import shutil
import zlib
import os

fmt = "xBHIIxxxQ"

print "Opera Cookie Dumper"
if len(sys.argv) != 3:
  print "Usage python opcodump.py <dcache.url> <output_directory>"
  sys.exit()

file_path=""
if not sys.argv[1].endswith("dcache4.url"):
  print "Invalid name for an Opera Cache file !"
  sys.exit()
elif not os.path.isfile(sys.argv[1]):
  print "File not found !"
  sys.exit()
else:
  file_path=os.path.dirname(sys.argv[1])

if not os.path.isdir(sys.argv[2]):
  os.makedirs(sys.argv[2])
out_path=os.path.abspath(sys.argv[2])

fd = open(sys.argv[1], "r")
(file_version_number, app_version_number, idtag_length, length_length) = unpack(">IIHH", fd.read(12))

major_fv = file_version_number >> 12
minor_fv = file_version_number & 4095
print "File version: %d.%d" % (major_fv, minor_fv)

major_av = app_version_number >> 12
minor_av = app_version_number & 4095
print "Application version: %d.%d" % (major_av, minor_av)
if major_av == 2:
  print "Cookie file"
elif major_av == 32:
  print "Cache file"
print "Size of idtags:", idtag_length, "bytes"
print "Size of payload length fields:", length_length, "bytes"
MSB = 1 << (idtag_length * 8) - 1
print "MSB: %#x" % MSB
print "==================================="

current = {}
current_header_name = ""
anchor = ""

output_start="""<html>
  <head>
    <title>Opera Cache Dumper - devloop.lyua.org</title>
    <style>
      table { border: 1px solid black; width: 100%}
      img { border: 3px solid #6495ed; margin-left: auto; margin-right: auto; }
      td { border: thin solid #6495ed; width: 50%; }
      td.headers { border: thin solid #ed9564; width: 50%; }
      td.relatives { border: thin solid #9564ed; width: 50%; }
    </style>
  </head>
  <body>
"""

def process_block(data):
  s="  <div>\n"

  pix=0
  out_file_name=""
  if data.has_key("mime"):
    if data["mime"].startswith("image/"):
      pix=1
      if data["mime"] in ["image/jpeg", "image/pjpeg", "image/jpg"]:
        out_file_name=data["filename"]+".jpg"

      elif data["mime"]=="image/x-icon":
        out_file_name=data["filename"]+".ico"

      elif data["mime"]=="image/png":
        out_file_name=data["filename"]+".png"

      elif data["mime"]=="image/bmp":
        out_file_name=data["filename"]+".bmp"

      elif data["mime"]=="image/gif":
        out_file_name=data["filename"]+".gif"

      if not data.has_key("encoding"):
        shutil.copy(file_path+"/"+data["filename"], out_path+"/"+out_file_name)
      elif data["encoding"]=="gzip":
        # decompress gzipped file
        fdc=open(file_path+"/"+data["filename"],"r")
        fdd=open(out_path+"/"+out_file_name,"w")
        try:
          buff=zlib.decompress(fdc.read())
          fdd.write(buff)
        except zlib.error:
          out_file_name+=".gz"
          pix=0
          shutil.copy(file_path+"/"+data["filename"], out_path+"/"+out_file_name)
        fdd.close()
        fdc.close()
      else:
        pix=0
        out_file_name+="."+data["encoding"]

    elif data["mime"] in ["application/xhtml+xml",
        "text/css",
        "application/x-javascript",
        "application/x-www-form-urlencoded",
        "text/html",
        "text/javascript",
        "text/xml",
        "application/xml",
        "application/javascript"]:
      out_file_name=data["filename"]+".txt"
      if not data.has_key("encoding"):
        # simple copy
        shutil.copy(file_path+"/"+data["filename"], out_path+"/"+out_file_name)
      elif data["encoding"]=="gzip":
        # decompress gzipped file
        fdc=open(file_path+"/"+data["filename"],"r")
        fdd=open(out_path+"/"+out_file_name,"w")
        try:
          buff=zlib.decompress(fdc.read())
          fdd.write(buff)
        except zlib.error:
          out_file_name+=".gz"
          shutil.copy(file_path+"/"+data["filename"], out_path+"/"+out_file_name)
        fdd.close()
        fdc.close()
    elif data["mime"]=="application/x-shockwave-flash":
      out_file_name=data["filename"]+".swf"
      shutil.copy(file_path+"/"+data["filename"], out_path+"/"+out_file_name)

    else:
      shutil.copy(file_path+"/"+data["filename"], out_path+"/"+data["filename"])
      out_file_name=data["filename"]

  s+="    <table>\n"
  s+="      <caption>"+cgi.escape(data["url"])+"</caption>\n"

  for x in data.keys():
    if x=="age":
      if data["age"]!=0:
        s+="      <tr><td>"+x.title()+"</td><td>"+cgi.escape(str(data[x]))+"</td></tr>\n"
    elif x in ["last-visited","last-lodified","date","localtime","expiry-date"]:
      if data[x]!="Thu Jan  1 01:00:00 1970":
        s+="      <tr><td>"+x.title()+"</td><td>"+cgi.escape(str(data[x]))+"</td></tr>\n"
    elif x not in ["url","headers","relatives", "user-agent", "user-agent-sub"]:
      s+="      <tr><td>"+x.title()+"</td><td>"+cgi.escape(str(data[x]))+"</td></tr>\n"

  if data["headers"]!={}:
    for k,v in data["headers"].items():
      s+="      <tr><td class=\"headers\">"+cgi.escape(k.title())+"</td><td class=\"headers\">"+cgi.escape(str(v))+"</td></tr>\n"

  if data["relatives"]!={}:
    for k,v in data["relatives"].items():
      s+="      <tr><td class=\"relatives\">"+cgi.escape(k.title())+"</td><td class=\"relatives\">"+cgi.escape(str(v))+"</td></tr>\n"

  s+="  </table>\n"
  if pix==1:
    s+="  <img src=\""+out_path+"/"+out_file_name+"\" /><br />\n"
  else:
    s+="<a href=\""+out_path+"/"+out_file_name+"\">"+out_file_name+"</a><br />\n"
  s+="</div><br /><br />\n"
  return s

fdi=open(out_path+"/"+"index.html","w")
fdi.write(output_start)

while True:
  # lecture du tag
  data = fd.read(idtag_length)
  if data == "":
    break
  tag = unpack(">"+fmt[idtag_length], data)[0]

  # !! TAGS TERMINATORS !!
  # Path component terminator
  if tag == 5|MSB:
    continue
  # Domain component terminator
  elif tag == 4|MSB:
    continue


  # !! FLAGS !!
  # flag: The URL is a result of a form query
  elif tag == 0x0b|MSB:
    continue
  # flag: File is downloaded and stored locally on user's disk,
  # and is not part of the disk cache directory
  elif tag == 0x0c|MSB:
    continue
  # flag: Always check if modified
  elif tag == 0x0f|MSB:
    continue
  # flag: Reserved for future use
  elif tag == 0x30|MSB:
    continue
  elif tag == 0x31|MSB:
    continue

  # If where are here it means the tag is followed by a length indicator
  data = fd.read(length_length)
  if data == "":
    break
  length = unpack(">"+fmt[length_length], data)[0]


  # Following tags (till end of the file) don't have a tag terminator

  # !! START TAGS !!
  if tag == 0x00:
    data = fd.read(length)
    print "unknown:", unpack(">"+fmt[length], data)[0]

  elif tag == 0x01:
    if current != {}:
      #print current
      fdi.write(process_block(current))
    current = {}
    # cache record
    pass
  # path record
  elif tag == 0x02:
    pass


  # The name of the URL, fully qualified
  elif tag == 0x03:
    current["url"]=fd.read(length)
    current["headers"] = {}
    current["relatives"]= {}

  # Last visited
  elif tag == 0x04:
    data = fd.read(length)
    x = unpack(">"+fmt[length], data)[0]
    current["last-visited"] = time.ctime(x)

  # Localtime, when the file was last loaded, not GMT
  elif tag == 0x05:
    data = fd.read(length)
    x = unpack(">"+fmt[length], data)[0]
    current["localtime"] = time.ctime(x)

  # Status of load
  elif tag == 0x07:
    data = fd.read(length)
    status = unpack(">"+fmt[length], data)[0]
    if status == 2:
      current["status"] = "Loaded"
    elif status == 4:
      current["status"] = "Loading aborted"
    elif status == 5:
      current["status"] = "Loading failed"
    
  # Content size
  elif tag == 0x08:
    data = fd.read(length)
    fsize = unpack(">"+fmt[length], data)[0]
    current["size"] = fsize

  # MIME type of content
  elif tag == 0x09:
    current["mime"] = fd.read(length)

  # Character set of content
  elif tag == 0x0a:
    current["charset"] = fd.read(length)

  # Name of file (cache files: only local to cache directory)
  elif tag == 0x0d:
    current["filename"] = fd.read(length)
  
  # Contains the HTTP protocol specific information
  elif tag == 0x10:
    # just pass and let the magic happen
    pass

  # HTTP date header
  elif tag == 0x15:
    current["date"] = fd.read(length)

  # Expiry date
  elif tag == 0x16:
    data = fd.read(length)
    x = unpack(">"+fmt[length], data)[0]
    current["expiry-date"] = time.ctime(x)

  # Last-Modified
  elif tag == 0x17:
    current["last-modified"] = fd.read(length)

  # Entity tag
  elif tag == 0x19:
    current["entity"] = fd.read(length)

  # Response line text
  elif tag == 0x1b:
    data = fd.read(length)
    current["response"] = data

  # Response code
  elif tag == 0x1c:
    data = fd.read(length)
    current["code"] = unpack(">"+fmt[length], data)[0]
 
  # Suggested file name
  elif tag == 0x1f:
    data = fd.read(length)
    current["suggested-filename"] = data

  # Content Encodings
  elif tag == 0x20:
    current["encoding"] = fd.read(length)
  
  # Content Location
  elif tag == 0x21:
    current["location"] = fd.read(length)
  
  # Relative link record
  elif tag == 0x22:
    pass

  # The name of the relative link
  elif tag == 0x23:
    data = fd.read(length)
    anchor = data

  # Expiry date
  elif tag == 0x24:
    data = fd.read(length)
    x = unpack(">"+fmt[length],data)[0]
    current["relatives"][anchor] = time.ctime(x)

  # This value identifies the User Agent string.
  elif tag == 0x25:
    data = fd.read(length)
    current["user-agent"] = unpack(">"+fmt[length], data)[0]

  # This value identifies the User Agent sub version.
  elif tag == 0x26:
    data = fd.read(length)
    current["user-agent-sub"] = unpack(">"+fmt[length], data)[0]

  # Language used. For exemple fr_FR
  elif tag == 0x2e:
    data = fd.read(length)
    current["lang"] = data

  # Undocumented but it looks like it's connectec to the "Age" header
  elif tag == 0x3a:
    data = fd.read(length)
    current["age"] = unpack(">"+fmt[length], data)[0]

  # Some kind of HTTP header record tag
  elif tag == 0x3b:
    pass

  # Sub record tag
  elif tag == 0x3c:
    pass

  # HTTP Header name
  elif tag == 0x3d:
    current_header_name = fd.read(length)

  # HTTP Header value
  elif tag == 0x3e:
    data = fd.read(length)
    current["headers"][current_header_name] = data

  # Next free cache file number
  elif tag == 0x40:
    data = fd.read(length)
    print "Next free cache file number: opr"+data

  else:
    # Unknown tag ^_^
    print "unknown tag: %#x" % tag
    print "\tbody length: %d" % length
    data = fd.read(length)
    print data.encode("hex_codec")

fd.close()

fdi.write("</body></html>")
fdi.close()
