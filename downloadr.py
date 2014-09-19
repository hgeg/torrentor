#!/usr/bin/env python
# -*- coding: utf-8 -*-
import libtorrent as lt
import time,sys,requests,redis,thread,osub,os,json
from flask import Flask,request,render_template,send_from_directory
from flup.server.fcgi import WSGIServer
app = Flask(__name__)

def filetype(f):
  if os.path.isdir(f): return 'dir'
  elif f.rsplit('.',1)[-1] in ('mp4','mkv','avi','webm','rmvb','wmv'): return 'mov'
  else: return 'file'

DOWNLOAD_PATH = '/media/30c9cdc2-52cd-4ca1-a65c-00d888ec25ff/downloads/'
MEDIA_PATH = '/media/30c9cdc2-52cd-4ca1-a65c-00d888ec25ff/media/'
CONTROL_DIRECTIVES = ('files','downloads','pause','resume')
STATES = ['queued', 'checking', 'downloading metadata','downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
TORRENT_URL = r'(http(?:s|)://[^"]*torrent[^"]*)'
ses = lt.session()
ses.listen_on(6881, 6891)

class Datastore:
   
  def __init__(self):
    self.valid = True
    self.rdb = redis.StrictRedis(host='localhost',port=6379,db=3)

  @property
  def files(self):
    return self.rdb.hgetall('downloadr.files')

  @property
  def downloads(self): 
    return self.rdb.hgetall('downloadr.downloads')
  
  def set_file(self,name,path):
    self.rdb.hset('downloadr.files',name,path)
    self.rdb.hdel('downloadr.downloads',name)

  def set_download(self,name,status): 
    self.rdb.hset('downloadr.downloads',name,status)

  def clear(self): self.rdb.flushdb()

  def validate(self): self.valid = True;

  def invalidate(self): self.valid = False;

def download_torrent(url):
  global ses
  d = Datastore()
  try:
    info = lt.torrent_info(requests.get(url).content)
  except:
    e = lt.bdecode(requests.get(url).content)
    info = lt.torrent_info(e)

  h = ses.add_torrent({'ti':info,'save_path':DOWNLOAD_PATH,'storage_mode':lt.storage_mode_t.storage_mode_sparse})
  filename = h.name()

  try:
    while not h.is_seed():
      s = h.status()
      meta = '%.2f%% | ↓%.1f KB/s | %s '%(s.progress * 100, s.download_rate / 1024, STATES[s.state])
      d.set_download(filename,meta)
      time.sleep(1+len(d.downloads)*2)
    d.set_file(filename,json.dumps([filetype(DOWNLOAD_PATH+filename),int(time.time())]))
    os.rename('%s/%s'%(DOWNLOAD_PATH,filename),'%s/%s'%(MEDIA_PATH,filename))
    try:
      osub.get_subtitle('%s/%s'%(MEDIA_PATH,filename))
    except: pass
  except:
    d.set_download(filename,'')
    d.set_file(filename,'')

def control(op):
  global ses
  d = Datastore()
  if op == 'files':
    return 'files:'+json.dumps([(k,json.loads(v)[0]) for k,v in sorted(d.files.items(),key=lambda e:json.loads(e[1])[1],reverse=True) if '.srt' not in k])
  elif op == 'downloads':
    downloads = d.downloads
    try:
      return 'control:'+' '.join([("%s | %s"%(e,downloads[e])) for e in downloads.keys()]) if downloads else 'control:No downloads'
    except Exception as e: return e.message
  elif op == 'pause': 
    ses.pause()
    return 'control:Paused'
  elif op == 'resume': 
    ses.resume()
    return 'control:Resuming'
  else: return 'control:Error: No such command "%s"'%op

@app.route("/downloadr/",methods=['GET','POST'])
def download():
  if request.method == 'POST':
    cmd = request.form['url']
    if cmd in CONTROL_DIRECTIVES: return control(cmd) 
    else: 
      thread.start_new_thread(download_torrent,(cmd,))
      return "url"
  else:
    return render_template('downloadr.html')

@app.route("/downloadr/files/",methods=['POST'])
def files():
  #try:
    assert(request.method=='POST')
    path = request.form['path']
    return json.dumps(sorted([(e,filetype(MEDIA_PATH+path+'/'+e)) for e in map(lambda c: c,os.listdir(MEDIA_PATH+path)) if e[-3:]!='srt']))
  #except: return '["error"]'

#@app.route('/downloadr/static/<path:filename>')
#def get_static(filename):
#  return send_from_directory('/home/pi/downloadr/static/', filename)

if __name__ == "__main__":
  d = Datastore()
  d.clear()
  files = sorted(os.listdir(MEDIA_PATH), key=lambda f:os.path.getctime(MEDIA_PATH+f),reverse=True)
  for f in files:
    d.set_file(f,json.dumps([filetype(MEDIA_PATH+f),int(os.path.getctime(MEDIA_PATH+f))]))
  WSGIServer(app).run()
  #app.run(host='0.0.0.0',port=8912,debug=True)
