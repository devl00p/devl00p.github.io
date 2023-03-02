# TorrentScan : detect NATed tcp ports using BitTorrent trackers
# devloop.lyua.org 08/2007
import re,sha,urllib2,threading,socket,sys
try:
    import psyco # Optional, 2.5x improvement in speed
    psyco.full()
except ImportError:
    pass

decimal_match = re.compile('\d')

# bdecode functions riped from
# http://wiki.theory.org/Decoding_bencoded_data_with_python
def bdecode(data):
    '''Main function to decode bencoded data'''
    chunks = list(data)
    chunks.reverse()
    root = _dechunk(chunks)
    return root

def _dechunk(chunks):
    item = chunks.pop()

    if (item == 'd'): 
        item = chunks.pop()
        hash = {}
        while (item != 'e'):
            chunks.append(item)
            key = _dechunk(chunks)
            hash[key] = _dechunk(chunks)
            item = chunks.pop()
        return hash
    elif (item == 'l'):
        item = chunks.pop()
        list = []
        while (item != 'e'):
            chunks.append(item)
            list.append(_dechunk(chunks))
            item = chunks.pop()
        return list
    elif (item == 'i'):
        item = chunks.pop()
        num = ''
        while (item != 'e'):
            num  += item
            item = chunks.pop()
        return int(num)
    elif (decimal_match.findall(item)):
        num = ''
        while decimal_match.findall(item):
            num += item
            item = chunks.pop()
        line = ''
        for i in range(1, int(num) + 1):
            line += chunks.pop()
        return line
    raise "Invalid input!"

# b(re)encoding functions added
def encode_str(data):
  return str(len(data))+":"+data

def encode_int(data):
  return "i"+str(data)+"e"

def encode_list(data):
  s="l"
  for e in data:
    if type(e)==str:
      s+=encode_str(e)
    if type(e)==int:
      s+=encode_int(e)
    if type(e)==list:
      s+=encode_list(e)
    if type(e)==dict:
      s+=encode_dict(e)
  s+="e"
  return s

def encode_dict(data):
  s="d"
  for k,v in data.items():
    s+=encode_str(k)

    if type(v)==str:
      s+=encode_str(v)
    if type(v)==int:
      s+=encode_int(v)
    if type(v)==list:
      s+=encode_list(v)
    if type(v)==dict:
      s+=encode_dict(v)
  s+="e"
  return s

# Communicate with the tracker
class Scan(threading.Thread):
  def __init__(self,port):
    threading.Thread.__init__(self)
    self.port=port

  def run(self):
    # Send an announce...
    track=tracker+"?"+"info_hash="+hash
    track+="&peer_id=cH3cKmYl33tp33rID101&uploaded=0&downloaded=0&event=started&compact=1&port="
    track+=str(self.port)+"&left="+str(total)
    urllib2.urlopen(track)
    print "Announced port",self.port
    # ... and waiting for someone to connect
    self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
      self.sock.bind(('',self.port))
    except socket.error,err:
      print "Error listening on port",self.port
      print err
    self.sock.listen(1)
    if self.sock.accept():
      nated.append(self.port)

  def close(self):
    self.sock.shutdown(1)
    self.sock.close()
    
# Execution starts here
if len(sys.argv)<3:
  print "Usage: python torrentscan.py <torrent file> <ports>"
  print "Example: python torrentscan.py debian_iso.torrent 80,110-113,4444,6891"
  sys.exit(1)

# Reading port list from command line
args=[a.replace(" ","") for a in sys.argv[2].split(",") if a.strip()!=""]
ports=[]
for a in args:
  if a.isdigit(): ports.append(int(a))
  else:
    l=a.split("-")
    if len(l)==2:
      if l[0].isdigit() and l[1].isdigit:
        if int(l[0])>=int(l[1]):
	  max=int(l[0])
	  min=int(l[1])
	else:
	  min=int(l[0])
	  max=int(l[1])
	for i in range(min,max+1):
	  ports.append(i)
lst=[]
for p in ports:
  if p not in lst:
    lst.append(p)

# Fetching torrent file
f=open(sys.argv[1],"r")
data=f.read()
plop=bdecode(data)
tracker=plop["announce"]
print "Tracker: "+tracker

# Calculating size of dictionnary info
l=len(encode_dict(plop["info"]))
start=data.find("4:info")+6
end=start+l

# Reading info from the file, calculate sha1sum
s=data[start:end]
hash=urllib2.quote(sha.sha(s).digest())
print "Hash: "+hash
total=0
if plop["info"].has_key("files"):
  for fi in plop["info"]["files"]:
    total=total+fi["length"]
else:
  total=plop["info"]["length"]
print "Total length:",total
f.close()

nated=[]
threadlist=[]
# Let's go!
for p in lst:
  scan=Scan(p)
  scan.setDaemon(True)
  scan.start()
  threadlist.append(scan)
# Lame timeout
for t in threadlist:
  t.join(10.0)
  t.close()

print nated

