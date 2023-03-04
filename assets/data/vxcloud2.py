#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://devloop.users.sourceforge.net/
# v1: 25/06/2011
# v2: 17/05/2012
# [*] Fixed a bug in recursive directory scanning
# [*] Changed to new VirusTotal report API

# VXcloud : a small cloud-based antivirus using Team-Cymru and VirusTotal APIs
# Detection is based on MD5 hashes of files

# Copyright (C) 2012 Nicolas SURRIBAS
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sys, getopt, os
import threading
from multiprocessing import Pool
import socket
import simplejson
import httplib
import urllib
from hashlib import md5
import time

VIRUS_TOTAL_API_KEY = ""

def md5sum(filename, buf_size=8192):
  m = md5()
  f = open(filename)
  data = f.read(buf_size)
  while data:
    m.update(data)
    data = f.read(buf_size)
  return m.hexdigest()

def ScanFile(filename):
  return (filename, md5sum(filename))

def CymruHashCheck(hashlist):
  sock = socket.socket()
  sock.connect( ("hash.cymru.com", 43) )
  sock.send("begin\n")
  sock.send( "\n".join(hashlist) )
  sock.send("\nend\n")
  data = ""
  while True:
    buff = sock.recv(1024)
    if buff == "":
      break
    else:
      data += buff
  sock.close()
  data = data.strip()
  tab = []
  for line in data.split("\n"):
    if not line.startswith("#"):
      tab.append(line.split(" "))
  # [ (SHA1|MD5, TIME(unix_t), DETECTION_PERCENT), (a, b, c), ...]
  return tab

def VirusTotalCheck(md5_list):
  params = {"apikey": VIRUS_TOTAL_API_KEY}
  params["resource"] = md5_list
  cnx = httplib.HTTPConnection("www.virustotal.com")
  cnx.request("POST", "/vtapi/v2/file/report", urllib.urlencode(params))
  resp = cnx.getresponse()
  if resp.status != 200:
    data = [{'status': resp.status}]
  else:
    data = simplejson.loads(resp.read())
    if isinstance(data, dict):
      data = [data]
    data[0]["status"] = resp.status
  cnx.close()
  return data

def usage(cmd):
  print "Usage: %s file | [-r] directory | -h" % (cmd)

if __name__ == '__main__':
  print "\t-= vxcloud v2 - devloop.users.sf.net / 2011-2012 =-"
  if sys.stdin.encoding:
    convert = lambda x: unicode(x, sys.stdin.encoding)
    sys.argv = map(convert, sys.argv)

  if len(sys.argv) < 2:
    usage(sys.argv[0])
    sys.exit(0)

  try:
    opts, args = getopt.getopt(sys.argv[1:], "r:h", ["recurse=", "help"])
  except getopt.GetoptError, err:
    print str(err)
    usage(sys.argv[0])
    sys.exit(2)

  filelist = []

  for opt, arg in opts:
    if opt == "-r":
      if not os.path.isdir(arg):
        if os.path.isfile(arg):
          print "%s is not a directory, adding as a file..." % (arg)
          filelist.append(arg)
        else:
          print "Invalid directory '%s', skipping." % (arg)
      else:
        for root, dirs, files in os.walk(arg):
          for filename in files:
            filelist.append(os.path.join(root,filename))
    elif opt in ("-h", "--help"):
      usage(sys.argv[0])
      sys.exit()

  for arg in args:
    if os.path.isfile(arg):
      filelist.append(arg)
    elif os.path.isdir(arg):
      for filename in os.listdir(arg):
        if os.path.isfile( os.path.join(arg, filename) ):
          filelist.append( os.path.join(arg, filename) )
    else:
      print "Invalid file or directory '%s', skipping." % (arg)



  if filelist == []:
    print "Empty list of files. Nothing to scan."
  else:
    # Calculate md5 hashes
    print "Calculating MD5 hashes..."
    print
    pool = Pool(processes=4)
    d = dict(pool.map(ScanFile, filelist))
    hashes = d.values()

    # Submit to the Malware Hash Registry
    print "  == Team Cymru Hash check =="
    tab = CymruHashCheck(hashes)
    for h, t, p in tab:
      if p != "NO_DATA":
        for k, v in d.iteritems():
          if v == h:
            print "%s (%s): First seen %s, detection = %s%%" % (k, v, time.ctime(int(t)), p)

    print
    print "  == VirusTotal Hash check =="
    if not VIRUS_TOTAL_API_KEY:
        print "You must get a VirusTotal API key (free) to activate this scan method."
        print "Get one on http://www.virustotal.com/"
    else:
      # Submit to VirusTotal
      pool2 = Pool(processes=5)
      hashes_blocks = [", ".join(hashes[i:i+4]) for i in range(0, len(hashes), 4)]
      results = pool2.map(VirusTotalCheck, hashes_blocks)

      excess = False

      for response in results:
        if response[0]["status"] == 409:
          excess = True
        elif response[0]["status"] == 403:
          print "You don't have the authorization to use this API. Please check your API key."
          sys.exit()

        for scan in response:
          if scan["response_code"] == 0:
            # file isn't known as a malware
            pass
          elif scan["response_code"] == 1:
            for k, v in d.iteritems():
              if v == scan["resource"]:
                print "%s (%s): First seen %s" % (k, v, scan["scan_date"])
                for firm, report in scan["scans"].iteritems():
                  if report["detected"]:
                    print "%s: %s" % (firm.ljust(22), report["result"])
                print "Detection rate: %s/%s" % (scan["positives"], scan["total"])
                print "More info:", scan["permalink"]
                print
          elif scan["response_code"] == -2:
            print "One of the file you asked a report for is still queued for analysis. Please try later."
            print "Info message:", scan["verbose_msg"]
          elif scan["response_code"] == -1:
            # Is it still true with the new API ? Not documented
            print "Your VirusTotal API key is invalid. Get one on http://www.virustotal.com/"
            break

      if excess:
        print "You exceeded the public API request rate (20 requests in 5 minutes)"

