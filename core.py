#!/usr/bin/env python
# -*- coding utf-8 -*-
from __future__ import with_statement
from subprocess import call as runCommand
#from twatch import *
import web,requests,json,redis,re,time,urllib
import os,sys,socket,fcntl,struct,shelve
import settings

#Methods to get interface data
def get_interface_ip(ifname):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

def get_lan_ip():
  ip = socket.gethostbyname(socket.gethostname())
  if ip.startswith("127.") and os.name != "nt":
    interfaces = ["eth0", "eth1", "eth2", "wlan0", "wlan1", "wifi0", "ath0", "ath1", "ppp0",]
    for ifname in interfaces:
      try:
        ip = get_interface_ip(ifname)
        break
      except IOError: pass
  return ip

def checktype(f):
  typ = "file"
  if os.path.isdir(f): typ = "dir"
  elif reduce(lambda x,y:x|y, map(lambda x: x in f, ('mp4','ogv','webm','avi','mkv'))):
    typ = 'mov'
  elif reduce(lambda x,y:x|y, map(lambda x: x in f, ('jpg','png','gif','jpeg'))):
    typ = 'pic'
  return typ

urls = (
  '/torrentor',             'Main',
  '/torrentor/',            'Main',
  '/torrentor/q/',          'Query',
  '/torrentor/l/(.*)',      'List',
  '/torrentor/media:(.+)/', 'Media',
  #json views
  '/torrentor/json:(.+)/',  'JSON'
)

r = redis.StrictRedis(host='localhost', port=6379, db=0)
render = web.template.render(settings.TEMPLATES_DIR)
app = web.application(urls, globals())

class Main:
  def GET(self):
    return render.index()
  def POST(self):
    return render.index()

class Query:
  def GET(self):
    return render.index()
  def POST(self):
    query = web.input().query
    if re.match('(magnet:\?.*|http://.*/.*\.(torrent\?title=.*|torrent))',query):
      timestamp = int(time.time())
      with open('%s/tfile_%d.torrent'%(settings.TORRENTS_DIR,timestamp),'wb') as f:  
        f.write(requests.get(query,stream=True).content)
      return web.redirect('/torrentor/')
    else:
      if query == '': return web.redirect('/torrentor/l/')
      path = settings.MEDIA_DIR
      files = sorted([(e,checktype("%s/%s"%(path,e))) for e in os.listdir(path) if query.lower() in e.lower()], key=lambda e:os.path.getctime(abs_path+'/'+e[0]), reverse=True)
      return render.list(query,files,False)

class List:
  def GET(self,path):
    abs_path = "%s/%s"%(settings.MEDIA_DIR,path)
    if path == '': path = '/'
    if not path[-1] == '/': path = "%s/"%path 
    if(os.path.isdir(abs_path)):
      files = sorted([(e, checktype("%s/%s"%(abs_path,e))) for e in os.listdir(abs_path)], key=lambda e:os.path.getctime(abs_path+'/'+e[0]), reverse=True)
      return render.list(path,files,True)
    else:
      return render.media(path.split('/')[-1],path)
  def POST(self):
    return render.index()

class JSON:
  def GET(self,call): pass
  def POST(self,call):
    web.header('Content-Type', 'application/json')
    post = json.loads(web.data())
    if call == 'match':
      query = post["query"];
      found = [e for e in os.listdir(settings.MEDIA_DIR) if query in e.lower()]
      if(found): return '[{"name":"%s","seeders":0,"leechers":0,"torrent":""}]'%found[0]
      else: return requests.get('http://fenopy.se/module/search/api.php?keyword=%s&format=json&limit=1'%query).text
    if call == 'playHDMI':
      runCommand(["screen", "-S", "omx", "-X", "quit"])
      runCommand(["screen", "-dmS", "omx", "omxplayer", "-o", "hdmi", "%s/%s"%(settings.MEDIA_DIR,post['path'])])
      return('Playing...')
    if call == 'status':
      db = shelve.open('/scripts/downloads.db')
      retval = json.dumps({'list': data[list]})
      db.close()
      return retval


if __name__ == '__main__':
  sys.argv.append("%s:8092"%get_lan_ip())
  #app.internalerror = web.debugerror
  #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
  app.run()
