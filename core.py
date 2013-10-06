#!/usr/bin/env python
# -*- coding utf-8 -*-
from __future__ import with_statement
import web,requests,json,redis,re,time,urllib
import os,sys
import settings

urls = (
  '/torrentor',             'Main',
  '/torrentor/',            'Main',
  '/torrentor/q/',          'Query',
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
      return render.index()
    else:
      return render.list(query,[e for e in os.listdir(settings.MEDIA_DIR) if query in e.lower()])

class Media:
  def GET(self,movie):
    return render.media(movie)
  def POST(self):
    return render.index()

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
  #app.internalerror = web.debugerror
  web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
  app.run()
