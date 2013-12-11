#!/usr/bin/env python
# -*- coding utf-8 -*-
from __future__ import with_statement
from subprocess import call as runCommand
from subprocess import check_output as cout
from subprocess import Popen as popen
#from twatch import *
import web,requests,json,redis,re,time,urllib
from web.background import background, backgrounder
import os,sys,socket,fcntl,struct,shelve
import settings
from scripts import action

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

#Helper methods

@background
def downloadTorrent(url):
  timestamp = int(time.time())
  req = requests.get(url,stream=True)
  with open('%s/tfile_%d.torrent'%(settings.TORRENTS_DIR,timestamp),'wb') as f:  
      for chunk in req.iter_content(256):
        f.write(chunk)

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
    if re.match('(magnet:\?.*|http(s|)://.*/.*\.(torrent\?title=.*|torrent))',query):
      timestamp = int(time.time())
      req = requests.get(query,stream=True)
      with open('%s/tfile_%d.torrent'%(settings.TORRENTS_DIR,timestamp),'wb') as f:  
          for chunk in req.iter_content(256):
            f.write(chunk)
      return web.redirect('/torrentor/')
    else:
      if query == '': return web.redirect('/torrentor/l/')
      path = settings.MEDIA_DIR
      files = sorted([(e,checktype("%s/%s"%(path,e))) for e in os.listdir(path) if query.lower() in e.decode('utf-8').lower() and e[-3:]!='srt'], key=lambda e:os.path.getctime(path+'/'+e[0]), reverse=True)
      return render.list(query,files,False)

class List:
  def GET(self,path):
    abs_path = "%s/%s"%(settings.MEDIA_DIR,path)
    if path == '': path = '/'
    if not path[-1] == '/': path = "%s/"%path 
    if(os.path.isdir(abs_path)):
      if path=='/':
        files = sorted([(e, checktype("%s/%s"%(abs_path,e))) for e in os.listdir(abs_path) if e[-3:]!='srt'], key=lambda e:os.path.getctime(abs_path+'/'+e[0]), reverse=True)
        path = ''
      else:
        files = [(e, checktype("%s/%s"%(abs_path,e))) for e in os.listdir(abs_path) if e[-3:]!='srt']
      return render.list(path,files,True)
    else:
      return render.media(path.split('/')[-1],path)
  def POST(self):
    return render.index()

class JSON:
  def GET(self,call): 
    if call == 'status':
      try:
        omxcount = int(cout(["pgrep","-f","omxplayer","-c"]))
      except: omxcount = 0
      if omxcount==0: 
          action.stop()
      retval = action.show_list()
      return retval

  @backgrounder
  def POST(self,call):
    web.header('Content-Type', 'application/json')
    post = json.loads(web.data())
    if call == 'match':
      query = post["query"];
      if re.match('(magnet:\?.*|http(s|)://.*/.*\.(torrent\?title=.*|torrent))',query):
        downloadTorrent(query)
        return '{"status":"downloading"}'
      else:
          found = [e for e in os.listdir(settings.MEDIA_DIR) if query in e.lower()]
          if(found): return '[{"status":"found"}]'%found[0]
          else: return json.dumps(requests.get('http://fenopy.se/module/search/api.php?keyword=%s&format=json&limit=1'%query).json()[0].update(status="search"))
    if call == 'playHDMI':
      runCommand('echo "on 0" | cec-client -s',shell=True)
      runCommand(["screen", "-S", "omx", "-X", "quit"])
      popen(["screen", "-S", "omx", "omxplayer", "-o", "hdmi", "%s/%s"%(settings.MEDIA_DIR,post['path'])])
      action.play(post['path'].split('/')[-1])
      return('{"error":false,"status":"playing"}')
    if call == 'control':
      keymap = {'back':'\c[[B', 'play':'p', 'stop':'q', 'next':'\c[[A'}
      runCommand(["screen", "-S", "omx", "-X", "stuff", keymap[post['directive']]])
    if call == 'subtitle':
      try:
        f = open(("%s/%s"%(settings.MEDIA_DIR,post['path']))[:-3]+'srt')
        result = "true"
        f.close()
      except IOError:
        runCommand(['periscope','%s/%s'%(settings.MEDIA_DIR,post['path']),'-l','en','--quiet'])
        try:
          f = open(("%s/%s"%(settings.MEDIA_DIR,post['path']))[:-3]+'srt')
          result = "true"
          f.close()
        except IOError:
          result = "false"
      return '{"result":%s}'%result


if __name__ == '__main__':
  sys.argv.append("%s:8092"%get_lan_ip())
  #app.internalerror = web.debugerror
  #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
  app.run()
