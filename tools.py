import libtorrent as lt
import time,os,sys,requests,redis,thread,json

DOWNLOAD_PATH = '/media/30c9cdc2-52cd-4ca1-a65c-00d888ec25ff/downloads/'
MEDIA_PATH = '/media/30c9cdc2-52cd-4ca1-a65c-00d888ec25ff/media/'
STATES = ['queued', 'checking', 'downloading metadata','downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
TORRENT_URL = r'(http(?:s|)://[^"]*torrent[^"]*)'

ses = lt.session()
ses.listen_on(6881, 6891)

def filetype(path):
  ext = path.rsplit('.',1)[-1].lower()
  if ext in ('mp4','mkv','avi','webm','rmvb','wmv'): return 'mov'
  elif os.isdir(path): return 'dir'
  else: return 'file'

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
      meta = '["%s",%.2f,%.1f,"%s"]'%(filename,s.progress * 100, s.download_rate / 1024, STATES[s.state])
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

