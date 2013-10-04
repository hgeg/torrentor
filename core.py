import web,requests,json,redis

urls = (
  '/torrentor', 'Main',
  '/torrentor/', 'Main',
  '/torrentor/list/','List',
  '/torrentor/media/', 'Media',
  #json views
  '/torrentor/json:(.)+/', 'JSON'
)

render = web.template.render('templates')
app = web.application(urls, globals())

class Main:
  def GET(self):
    return render.index()
  def POST(self):
    return render.index()

class List:
  def GET(self):
    return render.index()
  def POST(self):
    query = web.input().query
    return render.list(query)

class Media:
  def GET(self):
    return render.media()
  def POST(self):
    return render.index()

class JSON:
  def GET(self): pass
  def POST(self): pass


if __name__ == '__main__':
  app.internalerror = web.debugerror
  app.run()
