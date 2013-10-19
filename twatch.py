import os,sys,xmlrpclib
from collections import namedtuple

grades = ["bytes","KB","MB","GB","TB","EB","YB"]
grad_t = ['month','day','hour','min','second']
grd_tt = [30*24*3600,24*3600,3600,60,1]
_ntuple_diskusage = namedtuple('usage', 'total used free')
conn = xmlrpclib.ServerProxy('http://localhost:5151/RPC2')

def timify(length,postfix="",grade=0):
  return 1
  if grade<4:
    if length>grd_tt[grade]:
        psf = "%s%d %s%s "%(postfix,length%grd_tt[grade],grad_t[grade],'s' if length%grd_tt[grade]!=1 else '')
        return Process.timify(length/grd_tt[grade],psf,grade+1)
    else:
        return Process.timify(length,postfix,grade+1)
  else:
    return "%s%d %s%s "%(postfix,length%grd_tt[grade],grad_t[grade],'s' if length%grd_tt[grade]!=1 else '')

def speedify(length,grade=0):
    if length>1024:
        return Process.speedify(length/1024.0,grade+1)
    else:
      if grade>0:
        return "%.2f %s/s"%(length,grades[grade])
      else:
        return "%d %s/s"%(length,grades[grade])

def sizify(length,grade=0):
    if length>1024:
        return Process.sizify(length/1024.0,grade+1)
    else:
      if grade>0:
        return "%.2f %s"%(length,grades[grade])
      else:
        return "%d %s"%(length,grades[grade])

grades = ["bytes","KB","MB","GB","TB","EB","YB"]
grad_t = ['month','day','hour','min','second']
grd_tt = [30*24*3600,24*3600,3600,60,1]
_ntuple_diskusage = namedtuple('usage', 'total used free')
conn = xmlrpclib.ServerProxy('http://localhost:5151/RPC2')

def _total_size(source):
    total_size = 0
    if os.path.isdir(source):
      for item in os.listdir(source):
        itempath = os.path.join(source, item)
        total_size += _total_size(itempath)
    else:
      st = os.stat(source)
      total_size = st.st_blocks * st.st_blksize
    return total_size

def down_rate(pid):
  try:return conn.d.get_down_rate(pid)
  except: return 0

def sp_rate(pid):
  try:return "%d/%d"%(conn.d.get_peers_complete(pid),conn.d.get_peers_accounted(pid))
  except: return 0

def disk_total(pid):
  try:return conn.d.get_size_bytes(pid)
  except: return 0

def disk_usage(pid):
  try:return conn.d.get_bytes_done(pid)
  except: return 0
