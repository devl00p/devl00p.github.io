#!/usr/bin/env python
# Tarhison - devloop.lyua.org 2007
import tarfile, tempfile, sys, os

if len(sys.argv)<2:
  print "Usage: python "+sys.argv[0]+" archive.tar[.gz|.bz2]"
  exit(1)
ext=sys.argv[1].split(".")[-1]
if ext=="tar":
  comp=""
elif ext in ["gz","bz2"]:
  comp=ext
else:
  print "Unknown extension"
  exit(1)
try:
  tarin=tarfile.open(sys.argv[1],"r:"+ext)
except IOError:
  print sys.argv[1]+": File not found"
  exit(1)
except tarfile.ReadError:
  print sys.argv[1]+": Not an archive file"
  exit(1)
tmpdir=tempfile.mkdtemp()
print "Creating temporary directory",tmpdir
tmpf=tempfile.mkstemp(".tar")[1]
if ext in ["gz","bz2"]:
  tmpf=tmpf+"."+ext
print "Creating temporary file",tmpf
tarout=tarfile.open(tmpf,"w:"+ext)
print "Extracting archive"
tarin.extractall(tmpdir)
print "Generating anonymous copy"
for tarinfo in tarin:
  print tmpdir+"/"+tarinfo.name
  tarinfo.uname="anon"
  tarinfo.gname="anon"
  tarinfo.mtime=0
  tarinfo.uid=1000
  tarinfo.gid=1000
  if tarinfo.isdir():
    tarout.addfile(tarinfo)
  else:
    tarout.addfile(tarinfo,file(tmpdir+"/"+tarinfo.name))
tarout.close()
tarin.close()

print "Overwritting original"
fin=open(tmpf,"r")
fout=open(sys.argv[1],"w")
while 1:
  buffer=fin.read(500)
  if buffer=="": break
  fout.write(buffer)
fout.close()
fin.close()
print "Deleting temporary file"
os.unlink(tmpf)
print "Deleting temporary extracted files"
for root,dirs,files in os.walk(tmpdir,topdown=False):
  for name in files:
    os.remove(root+"/"+name)
  for name in dirs:
    os.rmdir(root+"/"+name)
print "Anonymisation done !"
