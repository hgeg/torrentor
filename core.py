#!/usr/bin/env python
# -*- coding utf-8 -*-
from __future__ import with_statement
import web,requests,json,redis,re,time,urllib
import os,sys,socket,fcntl,struct
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

urls = (
  '/torrentor',             'Main',
  '/torrentor/',            'Main',
  '/torrentor/q/',          'Query',
  '/torrentor/media:(.+)/', 'Media',
  '/torrentor/mediaserve/(.*)/' , 'MServer',
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
      return render.list(query,[e for e in os.listdir(settings.MEDIA_DIR) if query in e.lower()])

class Media:
  def GET(self,movie):
    return render.media(movie)
  def POST(self):
    return render.index()

class MServer:
   def GET(self, file):
     try:
       f = open('%s/%s'%(MEDIA_DIR,file), 'rb')
       return f.read()
     except:
      return web.redirect('/torrentor/')

class JSON:
  def GET(self,call): pass
  def POST(self,call):
    web.header('Content-Type', 'application/json')
    post = json.loads(web.data())
    if call=='match':
      query = post["query"];
      found = [e for e in os.listdir(settings.MEDIA_DIR) if query in e.lower()]
      if(found): return '[{"name":"%s","seeders":0,"leechers":0,"torrent":""}]'%found[0]
      else: return requests.get('http://fenopy.se/module/search/api.php?keyword=%s&format=json&limit=1'%query).text

if __name__ == '__main__':
  sys.argv.append("%s:8092"%get_lan_ip())
  #app.internalerror = web.debugerror
  #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
  app.run()
