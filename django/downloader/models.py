# -*- coding: utf-8 -*-
from __future__ import with_statement
from django.db import models
import os,xmlrpclib,subprocess,redis,pickle
from django.utils.encoding import smart_text
from django.db.models.signals import pre_init
from collections import namedtuple

grades = ["bytes","KB","MB","GB","TB","EB","YB"]
grad_t = ['month','day','hour','min','second']
grd_tt = [30*24*3600,24*3600,3600,60,1]
_ntuple_diskusage = namedtuple('usage', 'total used free')
conn = xmlrpclib.ServerProxy('http://localhost:5151/RPC2')
r = redis.StrictRedis(host='localhost',port=6379,db=0)

to_canonical = lambda path: ("/home/can/torrentor/downloads/%s/"%path).encode('utf-8')


def cache_hash(sender, args, **kwargs):
  return 0
  for e in conn.download_list():
    if args[1] == conn.d.get_base_filename(e):
      hlist = pickle.loads(r.get('hlist'))
      progs = pickle.loads(r.get('progs'))
      hlist += e
      progs[e] = 3
      r.set("hlist",pickle.dumps(hlist))
      r.set("progs",pickle.dumps(progs))
      return

def check_cached(thash):
    progs = pickle.loads(r.get('progs'))
    hlist = pickle.loads(r.get('hlist'))
    progress = progs[thash]
    rate = 1
    if progress>0:
      rate = down_rate(thash)
      current = disk_usage(thash)
      total = disk_total(thash)
    else:
      current = disk_total(thash)
      total = current
    if current>8 and progress==2:
        progs[thash] = 1
    elif total-current<=0 and progress==1:
        proc = Process.objects.get(category=thash)
        proc.progress = 0;
        proc.save()
        progress=0
        del hlist[hlist.index(thash)]
        del progs[thash]
    r.set("hlist",pickle.dumps(hlist))
    r.set("progs",pickle.dumps(progs))
    return ("%s of %s downloaded"%(Process.sizify(current),Process.sizify(total)), int((current*1.0)/total*100), Process.speedify(rate), 'Process.timify(int((self.length-current)/(rate+1)))',sp_rate(thash),conn.d.get_name(thash))

def linkTorrent(proc):
  if not proc.category == '..': return 
  for e in conn.download_list():
    if proc.name == conn.d.get_base_filename(e):
      proc.category = e
      proc.save()
      return

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

# Create your models here.
class Process(models.Model):
    #categorizing and storing options
    name     = models.CharField(max_length=100,null=False)
    category = models.CharField(max_length=100,default="..")
    subcat   = models.CharField(max_length=100,default="downloads")

    #sources of the torrent file
    tfile    = models.FileField(upload_to=".",null=True)
    tlink    = models.CharField(max_length=250,null=True)
    mlink    = models.CharField(max_length=250,null=True)
    ttype    = models.IntegerField(default=0)
    
    #process tracking variables
    progress = models.IntegerField(default=0)
    subp     = models.IntegerField(default=0)
    length   = models.IntegerField(default=0)

    @staticmethod
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

    @staticmethod
    def speedify(length,grade=0):
        if length>1024:
            return Process.speedify(length/1024.0,grade+1)
        else:
          if grade>0:
            return "%.2f %s/s"%(length,grades[grade])
          else:
            return "%d %s/s"%(length,grades[grade])

    @staticmethod
    def sizify(length,grade=0):
        if length>1024:
            return Process.sizify(length/1024.0,grade+1)
        else:
          if grade>0:
            return "%.2f %s"%(length,grades[grade])
          else:
            return "%d %s"%(length,grades[grade])

    def perform(self,action):
      if action=="pause":
        self.progress=7
        self.save()
        conn.d.pause(self.category)
      if action=="resume":
        conn.d.resume(self.category)
        self.progress=1
        self.save()
      if action=="cancel":
        try:
          conn.d.erase(self.category)
        except:pass
        self.delete()
      progs = pickle.loads(r.get('progs'))
      progs[self.category] = self.progress
      r.set("progs",pickle.dumps(progs))

    def check(self):
        linkTorrent(self)
        total = self.length
        rate = 1
        if self.progress>0:
          rate = down_rate(self.category)
          current = disk_usage(self.category)
        else:
          current = self.length
        if current>8 and self.progress==2:
            self.progress=1
            self.save()
        elif total-current<=0 and self.progress==1:
            self.progress=0
            self.save()
        return ("%s of %s downloaded"%(Process.sizify(current),Process.sizify(total)), int((current*1.0)/total*100), Process.speedify(rate), 'Process.timify(int((self.length-current)/(rate+1)))',sp_rate(self.category))

#pre_init.connect(cache_hash, sender = Process)
