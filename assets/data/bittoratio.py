import socket
import threading
import urllib
import cgi
import urlparse
import sys
import urllib2
import time
import httplib

FACTOR = 10
PORT = 8080

spool = {}
scrape_cache = {}
announce_cache = {}

class ClientThread(threading.Thread):
  def __init__(self, channel, details):
    self.channel = channel
    self.details = details
    threading.Thread.__init__(self)
	
  def run(self):
    #print "Connexion de %s:%s" % (self.details[0], self.details[1])
    req = ""
    while True:
      t = self.channel.recv(4096)
      req += t
      if len(t)<4096:
        break
        
    lines = req.splitlines()
    if lines[0].find(" ") == -1:
      self.channel.close()
      return
    first_line = lines[0].split(" ")
    if len(first_line) < 2:
      self.channel.close()
      return
    method = first_line[0]
    uri = first_line[1]
    uri_frag = urlparse.urlsplit(uri)
    host = uri_frag.netloc
    query = uri_frag.query
    params = urlparse.parse_qs(query)
    uploaded = 0
    for k, v in params.items():
      if k == "uploaded":
        uploaded = int(v[0]) * FACTOR
        params[k] = str(uploaded)
      elif k == "info_hash":
        current_info_hash = v[0]
        params[k] = v[0]
      else:
        params[k] = v[0]

    current_url = (uri_frag.scheme, uri_frag.netloc, uri_frag.path, urllib.urlencode(params), uri_frag.fragment)

    res = urlparse.urlunsplit((uri_frag.scheme, uri_frag.netloc, uri_frag.path, urllib.urlencode(params), uri_frag.fragment))
    #print time.strftime("[%H:%M:%S]"), res
    current_action = uri_frag.path.split("/")[-1]
    print time.strftime("[%H:%M:%S]"), uri_frag.netloc, current_action, urllib.quote(current_info_hash), uploaded or ""

    current_headers = lines[1:]
    header_dict = {}

    for header in lines[1:]:
      if header.find(":") > 0:
        k, v = header.split(":", 1)
        k = k.strip()
        v = v.strip()
        header_dict[k] = v

    data = ""
    try:
      conn = httplib.HTTPConnection(uri_frag.netloc)
      conn.request("GET", uri_frag.path + '?' + urllib.urlencode(params), headers = header_dict)
      resp = conn.getresponse()
      data  = "HTTP/1.0 %s %s\r\n" % (resp.status, resp.reason)
      data += "\r\n".join([k + ": " + v for k, v in resp.getheaders()])
      data += "\r\n"
      data += resp.read()
      conn.close()
    # prendre aussi : error: [Errno 104] Connection reset by peer et gaierror: [Errno -3] Temporary failure in name resolution
    except socket.error:
      if current_action == "announce" and current_info_hash in announce_cache.keys():
          self.channel.send(announce_cache[current_info_hash])
          if uploaded > 0:
            spool[current_info_hash] = (current_url, header_dict)
      elif current_action == "scrape" and current_info_hash in scrape_cache.keys():
          self.channel.send(scrape_cache[current_info_hash])
      else:
        data  = "HTTP/1.1 504 Gateway Timeout\r\n"
        data += "Content-Length: 15\r\n"
        data += "Content-Type: text/html\r\n\r\n"
        data += "Gateway Timeout"
        self.channel.send(data)
        print "[!] Connection eror"

      self.channel.close()
      return

    if data !="":
      self.channel.send(data)
    self.channel.close()

    if current_action == "announce":
      announce_cache[current_info_hash] = data 
    elif current_action == "scrape":
      scrape_cache[current_info_hash] = data

    if current_info_hash in spool.keys():
      spool.pop(current_info_hash)

server = socket.socket()
server.bind(('', PORT))
server.listen(20)
print "Listening on port", PORT, "- Factor =", FACTOR
try:
  while True:
    channel, details = server.accept()
    ClientThread(channel, details).start()
except KeyboardInterrupt:
  print "Exiting"
  for k, v in spool.items():
    print "Flushing", v[0][1], urllib.quote(k), urlparse.parse_qs(v[0][3])['uploaded'][0]

    try:
      conn = httplib.HTTPConnection(v[0][1])
      conn.request("GET", v[0][2] + '?' + v[0][3], headers = v[1])
      resp = conn.getresponse()
      conn.close()
    except socket.error:
      print "Oups"
  sys.exit()
