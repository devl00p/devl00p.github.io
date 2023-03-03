#!/usr/bin/env python
import os
width = 60
pid_width = len("pid")
oom_score_width = len("oom_score")
oom_adj_width = len("oom_adj")

pidlist = [pid for pid in os.listdir("/proc") if pid.isdigit()]
oom_pids = {}

for pid in pidlist:
  if len(pid)>pid_width:
    pid_width=len(pid)
  try:
    fd = open("/proc/"+pid+"/oom_score")
    oom_score = int(fd.read().strip())
    if len(str(oom_score))>oom_score_width:
      oom_score_width = len(str(oom_score))
    fd.close()
  except IOError:
    continue
  try:
    fd = open("/proc/"+pid+"/oom_adj")
    oom_adj = int(fd.read().strip())
    if len(str(oom_adj))>oom_adj_width:
      oom_adj_width = len(str(oom_adj))
    fd.close()
  except IOError:
    continue
  try:
    fd = open("/proc/"+pid+"/cmdline")
    cmdline = fd.read().strip()
    fd.close()
  except IOError:
    continue
  if cmdline == "":
    continue
  cmdline = " ".join(cmdline.split("\0")).strip()
  if len(cmdline)>width:
    cmdline=cmdline[:width-3]+"..."
  oom_pids[int(pid)]={'oom_score':oom_score, 'oom_adj': oom_adj, 'cmdline': cmdline}

oom_score_list = list(set([oom_pids[pid]['oom_score'] for pid in oom_pids.keys()]))
oom_score_list.sort()
print "oom_score".ljust(oom_score_width), "pid".ljust(pid_width), "process name".ljust(width), "oom_adj".ljust(oom_adj_width)
for oom_score in oom_score_list:
  for pid in oom_pids.keys():
    if oom_pids[pid]['oom_score'] == oom_score:
      print str(oom_score).rjust(oom_score_width), str(pid).rjust(pid_width), oom_pids[pid]['cmdline'].ljust(width), str(oom_pids[pid]['oom_adj']).rjust(oom_adj_width)
