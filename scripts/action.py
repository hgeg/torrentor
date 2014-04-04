#!/usr/bin/env python
# -*- conding: utf-8 -*-
from __future__ import with_statement
import os,sys,redis,json,xmlrpclib,requests,hashlib,struct,xmlrpclib,zlib
from subprocess import call as runCommand

db = redis.StrictRedis(host='localhost', port=6379, db=0)

def init_list():
  db.set('now_playing','')
  db.set('convProcess',None)
  db.set('convQueue','[]')
  db.set('dCount',0)
  return 0

def play(filename):
  db.set('now_playing',filename)

def stop():
  db.set('now_playing','')

def remove_form_list(filename):
  lst = json.loads(db.get('list'))
  if filename in lst: lst.remove(filename)
  db.set('list',json.dumps(lst))
  return 0

def add_to_list(filename):
  lst = json.loads(db.get('list'))
  lst += [filename]
  if len(lst)>10:
    lst.reverse()
    while len(lst)>10: lst.pop()
    lst.reverse()
  db.set('list',json.dumps(lst))
  return 0

def convert(path='tConvNone'):
  cp = db.get('convProcess')
  try:
    cq = list(json.loads(db.get('convQueue')))
  except:
    cq = []
  if path != 'tConvNone':
    if isinstance(path,tuple):
      cq.append(path[0])
    else:
      cq.append(path)
    db.set('convQueue',json.dumps(cq))
  if cp=='None':
    cp = cq.pop(0)
    db.set('convProcess',cp)
    db.set('convQueue',cq)
    cin = cp[:-3]+'cnv'
    cout = cp[:-3]+'mp4'
    print "cin:",cin
    print "cout:",cout
    runCommand(['mv',cp,cin])
    runCommand(['/home/pi/torrentor/scripts/omxtx',cin,cout])
    runCommand(['mv',cin,cp])
    db.set('convProcess',None)
    convert()
  print "cp:",cp
  print "cq:",cq

def convData():
  cp = db.get('convProcess')
  try:
    cq = list(json.loads(db.get('convQueue')))
  except: cq = []
  print "cp:",cp
  print "cq:",cq

def show_list():
  conn = xmlrpclib.ServerProxy('http://localhost/scgi')
  trs = [dl for dl in conn.d.multicall('default','d.get_base_filename=','d.get_down_rate=','d.get_bytes_done=','d.get_size_bytes=','d.is_active=','d.get_hash=','d.is_open=') if dl[2]<dl[3] and dl[2]>0]
  dcount = int(db.get('dCount'))
  ncount = len(trs)
  if ncount!=dcount: db.delete('/')
  db.set('dCount',ncount)
  retval = json.dumps({'list':trs,'now_playing':db.get('now_playing')[:36]})
  return retval

def toggle(hash):
  conn = xmlrpclib.ServerProxy('http://localhost/scgi')
  is_active = conn.d.is_active(hash)
  if(is_active==1):
      conn.d.pause(hash)
      return "paused"
  else: 
      conn.d.resume(hash)
      return "playing"

def OSHash(name): 
  longlongformat = 'q'  # long long 
  bytesize = struct.calcsize(longlongformat) 

  f = open(name, "rb") 

  filesize = os.path.getsize(name) 
  hash = filesize 

  if filesize < 65536 * 2: return "SizeError" 

  for x in range(65536/bytesize): 
    buffer = f.read(bytesize) 
    (l_value,)= struct.unpack(longlongformat, buffer)  
    hash += l_value 
    hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  


  f.seek(max(0,filesize-65536),0) 
  for x in range(65536/bytesize): 
    buffer = f.read(bytesize) 
    (l_value,)= struct.unpack(longlongformat, buffer)  
    hash += l_value 
    hash = hash & 0xFFFFFFFFFFFFFFFF 

  f.close() 
  returnedhash =  "%016x" % hash 
  return returnedhash 

def get_hash(name):
  readsize = 64 * 1024
  with open(name, 'rb') as f:
    size = os.path.getsize(name)
    data = f.read(readsize)
    f.seek(-readsize, os.SEEK_END)
    data += f.read(readsize)
  return hashlib.md5(data).hexdigest()

def get_subtitle(path):
  try:
      filehash = OSHash(path)
      filesize = int(os.path.getsize(path))
      proxy = xmlrpclib.ServerProxy("http://api.opensubtitles.org/xml-rpc")
      login = proxy.LogIn('hgeg','sokoban','en','torrentor')
      if(login['status']=='200 OK'):
        token = login['token']
        data = proxy.SearchSubtitles(token,[{'moviehash':filehash,'moviebytesize':filesize,'sublanguageid':'eng,en,tr'}])
        content = zlib.decompress(requests.get(data['data'][0]['SubDownloadLink']).content,16+zlib.MAX_WBITS)
        with open(path[:-3]+'srt','wb') as f:
          f.write(content)
        print path[:-3]+'srt'
      else: print "Connection Error: %s"%login['status']
  except: print "DBError: no subtitle found"
 


if __name__ == '__main__':
  if sys.argv[1] == '--add':
    add_to_list(sys.argv[2])
  elif sys.argv[1] == '--remove':
    remove_form_list(sys.argv[2])
  elif sys.argv[1] == '--list':
    print show_list()
  elif sys.argv[1] == '--play':
    play(sys.argv[2])
  elif sys.argv[1] == '--stop':
    stop()
  elif sys.argv[1] == '--init':
    init_list()
  elif sys.argv[1] == '--conv':
    convert(sys.argv[2])
  elif sys.argv[1] == '--cdat':
    convData()
  elif sys.argv[1] == '--getsub':
    get_subtitle(sys.argv[2])
