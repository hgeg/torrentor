#import libtorrent as lt
import time, os, sys, requests, redis, thread, json
from flask import Flask, Response, request, render_template, url_for, session

app = Flask(__name__)
app.secret_key = "testSecretKey"

#DOWNLOAD_PATH = '/media/30c9cdc2-52cd-4ca1-a65c-00d888ec25ff/downloads/'
#MEDIA_PATH = '/media/30c9cdc2-52cd-4ca1-a65c-00d888ec25ff/media/'
DOWNLOAD_PATH = '/Users/hgeg/Documents/'
MEDIA_PATH = '/Users/hgeg/Documents/'
STATES = ['queued', 'checking', 'downloading metadata','downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
TORRENT_URL = r'(http(?:s|)://[^"]*torrent[^"]*)'

'''
ses = lt.session()
ses.listen_on(6881, 6891)
'''

def filetype(path):
  ext = os.path.splitext(path)[1].lower()
  if ext in ('mp4','mkv','avi','webm','rmvb','wmv'): return 'mov'
  elif os.path.isdir(path): return 'dir'
  else: return 'file'

class Datastore:
   
  def __init__(self):
    self.valid = True
    self.rdb = redis.StrictRedis(host='localhost',port=6379,db=3)

  @property
  def items(self): return self.rdb.hgetall('downloadr.items')
  def set(self,name,data): self.rdb.hset('downloadr.items',name,data)
  def clear(self): self.rdb.flushdb()
  def validate(self): self.valid = True;
  def invalidate(self): self.valid = False;

def download_torrent(url):
  return 0
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
      meta = '[%.2f,%.1f,"%s"]'%(s.progress * 100, s.download_rate / 1024, STATES[s.state])
      d.set(filename,meta)
      time.sleep(1+len(d.downloads)*2)
    d.set(filename,json.dumps([filetype(DOWNLOAD_PATH+filename),int(time.time())]))
    os.rename('%s/%s'%(DOWNLOAD_PATH,filename),'%s/%s'%(MEDIA_PATH,filename))
  except:
    d.set(filename,'')

@app.route('/torrentor',methods=['GET'])
def home():
  return render_template('index.html')

@app.route('/torrentor/download/',methods=['POST'])
def download():
  time.sleep(1)
  return "control:%s"%(url)

@app.route('/torrentor/items/',methods=['POST'])
def items():
  return json.dumps({'error':False,'items':Datastore().items})

@app.route('/torrentor/files/',methods=['POST'])
def files():
  #try:                                                                                                                                                   
    assert(request.method=='POST')
    path = request.form['path']
    return json.dumps(sorted([(e,filetype(MEDIA_PATH+path+'/'+e)) for e in map(lambda c: c,os.listdir(MEDIA_PATH+path)) if e[-3:]!='srt']))
  #except: return '["error"]' 


@app.route('/torrentor/static/<path:path>')
def get_static(path):
  mimetypes = {
    ".css": "text/css",
    ".html": "text/html",
    ".js": "application/javascript",
    ".png": "image/png",
  }
  complete_path = os.path.join(os.getcwd(),'static', path)
  ext = os.path.splitext(path)[1]
  mimetype = mimetypes.get(ext, "text/html")
  with open(complete_path,'rb') as f:
    content = f.read()
  return Response(content, mimetype=mimetype)

if __name__ == '__main__': 
  d = Datastore()
  d.clear()
  files = sorted(os.listdir(MEDIA_PATH), key=lambda f:os.path.getctime(MEDIA_PATH+f),reverse=True)
  for f in files:
    d.set(f,json.dumps([filetype(MEDIA_PATH+f),int(os.path.getctime(MEDIA_PATH+f))]))
  app.run(host='localhost',port=8092,debug=True)
