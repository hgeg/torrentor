# -*- coding: utf-8 -*-
from __future__ import with_statement
from downloader.models import *
from collections import OrderedDict
from pythonopensubtitles.opensubtitles import OpenSubtitles
from downloader import forms
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator
from django.utils.encoding import smart_text
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from StringIO import StringIO
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import time,bencode,urllib2,gzip,re,logging,zipfile,subprocess,string,httplib,json

from settings import DOWNLOADS_DIR, CONVERT_DIR

log = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3)'

tvshowRegex = re.compile('(?P<show>.*)S(?P<season>[0-9]{2})E(?P<episode>[0-9]{2}).(?P<teams>.*)', re.IGNORECASE)
tvshowRegex2 = re.compile('(?P<show>.*).(?P<season>[0-9]{1,2})x(?P<episode>[0-9]{1,2}).(?P<teams>.*)', re.IGNORECASE)
movieRegex = re.compile('(?P<movie>.*)[\.|\[|\(| ]{1}(?P<year>(?:(?:19|20)[0-9]{2}))(?P<teams>.*)', re.IGNORECASE)

def prs(st): return filter(lambda x: x in string.printable, st)

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def getFileName(filepath):
    if os.path.isfile(filepath):
        filename = os.path.basename(filepath)
    else:
        filename = filepath
    if filename.endswith(('.avi', '.wmv', '.mov', '.mp4', '.mpeg', '.mpg', '.mkv')):
        fname = filename.rsplit('.', 1)[0]
    else:
        fname = filename
    return fname
        
def guessFileData(filename):
    filename = unicode(getFileName(filename).lower())
    matches_tvshow = tvshowRegex.match(filename)
    if matches_tvshow: # It looks like a tv show
        (tvshow, season, episode, teams) = matches_tvshow.groups()
        tvshow = tvshow.replace(".", " ").strip()
        teams = teams.split('.')
        return {'type' : 'tvshow', 'name' : tvshow.strip(), 'season' : int(season), 'episode' : int(episode), 'teams' : teams}
    else:
        matches_tvshow = tvshowRegex2.match(filename)
        if matches_tvshow:
            (tvshow, season, episode, teams) = matches_tvshow.groups()
            tvshow = tvshow.replace(".", " ").strip()
            teams = teams.split('.')
            return {'type' : 'tvshow', 'name' : tvshow.strip(), 'season' : int(season), 'episode' : int(episode), 'teams' : teams}
        else:
            matches_movie = movieRegex.match(filename)
            if matches_movie:
                (movie, year, teams) = matches_movie.groups()
                teams = teams.split('.')
                part = None
                if "cd1" in teams :
                    teams.remove('cd1')
                    part = 1
                if "cd2" in teams :
                    teams.remove('cd2')
                    part = 2
                return {'type' : 'movie', 'name' : movie.strip(), 'year' : year, 'teams' : teams, 'part' : part}
            else:
                return {'type' : 'unknown', 'name' : filename, 'teams' : [] }

def downloadContent(url, timeout = None):
    ''' Downloads the given url and returns its contents.'''
    try:
        log.debug("Downloading %s" % url)
        req = urllib2.Request(url, headers={'Referer' : url, 'User-Agent' : USER_AGENT})
        if timeout:
            socket.setdefaulttimeout(timeout)
        f = urllib2.urlopen(req)
        content = f.read()
        f.close()
        return content
    except urllib2.HTTPError, e:
        log.warning("HTTP Error: %s - %s" % (e.code, url))
    except urllib2.URLError, e:
        log.warning("URL Error: %s - %s" % (e.reason, url))

def downloadFile(url, filename):
    ''' Downloads the given url to the given filename '''
    content = downloadContent(url)
    dump = open(filename, "wb")
    dump.write(content)
    dump.close()
    log.debug("Download finished to file %s. Size : %s"%(filename,os.path.getsize(filename)))
        
def createFile(videofilename,suburl):
    '''pass the URL of the sub and the file it matches, will unzip it
    and return the path to the created file'''
    srtbasefilename = videofilename.rsplit(".", 1)[0]
    zipfilename = srtbasefilename +".zip"
    downloadFile(suburl, zipfilename)
    
    if zipfile.is_zipfile(zipfilename):
        log.debug("Unzipping file " + zipfilename)
        zf = zipfile.ZipFile(zipfilename, "r")
        for el in zf.infolist():
            if el.orig_filename.rsplit(".", 1)[1] in ("srt", "sub", "txt"):
                outfile = open(DOWNLOADS_DIR+"subs/"+srtbasefilename + "." + el.orig_filename.rsplit(".", 1)[1], "wb")
                outfile.write(zf.read(el.orig_filename))
                outfile.flush()
                outfile.close()
            else:
                log.info("File %s does not seem to be valid " %el.orig_filename)
        # Deleting the zip file
        zf.close()
        os.remove(zipfilename)
        return srtbasefilename + ".srt"
    else:
        log.info("Unexpected file type (not zip)")
        os.remove(zipfilename)
        return None

@csrf_exempt
def login(request):
  if request.user.is_authenticated(): return HttpResponseRedirect('/')
  if request.method=="GET":
    try: n = request.GET['next']
    except: n = ''
    return render_to_response('login.html',{'n':n})
  usr = request.POST["username"]
  pas = request.POST["password"]
  nxt = request.POST["next"]
  try: u = User.objects.get(username=usr)
  except: return render_to_response("login.html",{'message':'Invalid username or password'})
  user = auth.authenticate(username=u.username, password=pas)
  if user is not None:
    if user.is_active:
      auth.login(request, user)
      return HttpResponseRedirect("%s"%nxt)
    else:
      return render_to_response("login.html",{'message':'This user is not activated'})
  else:
      return render_to_response("login.html",{'message':'Invalid username or password'})

@login_required
def logout(request):
  auth.logout(request)
  return HttpResponseRedirect('/')

@login_required
def newslog(request):
  return render_to_response('newslog.html',{'user':request.user})

@login_required
def pre_upload(request):
    form = forms.torrentForm()
    return render_to_response('index.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def upload(request):
    form = forms.torrentForm(request.POST,request.FILES)
    if request.user.username=="guest":
      return render_to_response('index.html', {'form': form, "message": "Guest's are not allowed to start download processes."}, context_instance=RequestContext(request))
    if form.is_valid():
            try:
              f = request.FILES['torfile']
            except:
              f = ""
            if not f == "":
              raw = f.read()
              try:
                name = bencode.bdecode(raw)['info']['name']
                length = bencode.bdecode(raw)['info']['length']
              except KeyError:
                length = 0
                for file in bencode.bdecode(raw)['info']['files']:
                    length += file['length']
                proc = Process.objects.create(tfile=f,name=name,length=length,ttype=0,progress=2)
                proc.save()
                if(os.path.isdir(to_canonical(name))):
                  if not os.path.exists(to_canonical(name)):
                    os.makedirs(to_canonical(name))
              except: pass
            else:
              u = int(time.time())
              l = request.POST['torlink']
              try:
                data = urllib2.urlopen(l)
                buf = StringIO(data.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
              except:
                data = urllib2.urlopen(l)
                data = data.read()
              with open("/home/can/torrentor/torrents/%d.torrent"%u,"wb") as f:
                  f.write(data)
              with open("/home/can/torrentor/torrents/%d.torrent"%u) as f:
                  raw = f.read()
              name = bencode.bdecode(raw)['info']['name']
              try:
                  length = bencode.bdecode(raw)['info']['length']
              except:
                  length = 0
                  for file in bencode.bdecode(raw)['info']['files']:
                      length += file['length']
              proc = Process.objects.create(tlink=l,name=name,length=length,ttype=1,progress=2)
              proc.save()
              print to_canonical(name)
              if(os.path.isdir(to_canonical(name))):
                if not os.path.exists(to_canonical(name)):
                  os.makedirs(to_canonical(name))
    else: pass
    return HttpResponseRedirect("/") 

@login_required
def perform(request,action,pid):
    Process.objects.filter(category=pid)[0].perform(action)
    return HttpResponse('OK')

def check(request,type,query): 
    data=''
    if(type=="limit"):
      lookup = Process.objects.filter(progress__gt=0)
    if len(lookup)>0:
      for e in lookup:
          if request.user.username != "guest":
            stats = (
             '''<td><p class="text-success">Seeding <button class="btn btn-inverse btn-mini" href="#"><i class="icon-white icon-pause"></i></button> <button class="btn btn-inverse btn-mini" href="#"><i class="icon-white icon-remove"></i></button></p></td>''',
             '''<td><p class="text-info">Downloading <button class="btn btn-inverse btn-mini" onclick="perform('pause','%s');"><i class="icon-white icon-pause"></i></button> <button class="btn btn-inverse btn-mini" onclick="perform('cancel','%s');" href="#"><i class="icon-white icon-remove"></i></button></p></td>'''%(e.category,e.category),
             '''<td><p class="text-mute">Queued <button class="btn btn-inverse btn-mini" onclick="perform('pause','%s');" href=""><i class="icon-white icon-pause"></i></button> <button class="btn btn-inverse btn-mini" onclick="perform('cancel','%s');" href="#"><i class="icon-white icon-remove"></i></button></p></td>'''%(e.category,e.category),"","","","",
             '''<td><p class="text-warning">Paused <button class="btn btn-inverse btn-mini" onclick="perform('resume','%s');"><i class="icon-white icon-play"></i></button> <button class="btn btn-inverse btn-mini" onclick="perform('cancel','%s');" href="#"><i class="icon-white icon-remove"></i></button></p></td>'''%(e.category,e.category),
            )
          else:
            stats = (
             '''<td><p class="text-success">Seeding</p></td>''',
             '''<td><p class="text-info">Downloading</p></td>''',
             '''<td><p class="text-mute">Queued</p></td>''',"","","","",
             '''<td><p class="text-warning">Paused</p></td>''',
            )
          try:
              status = stats[e.progress]
          except:
              status = '<td><p class="text-error">Error %d<i class="icon-exclamation-sign"></i></p></td>'%e.progress
          check = e.check()
          name = e.name if len(e.name)<50 else "%s..."%e.name[:47]
          data += '''<tr>
                       <td><p>%s</p></td>
                       %s
                       <td>
                           <div class="progress" style="margin-bottom:-20px;">
                              <div class="bar bar-inverse" style="width:%d%%;">
                              </div>
                           </div>
                           <small>&nbsp;&nbsp;%s</small> 
                           <small class="pull-right">%s&nbsp;&nbsp;</small>
                           <br/>
                           <!--<small>Estimated time left: %s</small>-->
                       </td>
                       <td><p>%s</p></td>
                   </tr>'''%(name,status,check[1],check[0],check[2],check[3],check[4])
    else:
            data = '<tr><td><p class="text-info">No processes...</p></td><td></td><td></td><td></td></tr>'
    return HttpResponse(data)


def subtitles(request,path):
  try:
    proc = Process.objects.filter(name=path.split('/')[0])[0]
  except:
    return '/archive/notFound.vtt'
  if proc.subp ==1:
    return proc.mlink
  try:
    opsub = OpenSubtitles()
    opsub.login('hgeg','sokoban')
  except:
    return '/archive/error.vtt'
    
  subsFile = "/archive/internal.vtt"
  try:
    data = guessFileData(path)
    if(data['type']=='tvshow'):
      sub = opsub.search_subtitles([{'sublanguageid':'eng','query':data['name'],'season':data['season'],'episode':data['episode']}])[0]
    else:
      sub = opsub.search_subtitles([{'sublanguageid':'eng','query':data['name']}])[0]
    subsFile = createFile(path,sub['ZipDownloadLink'])
    proc.subp = 1
    proc.mlink = subsFile
    proc.save()
    return proc.mlink
  except: pass

  if request != None:
    return HttpResponse(str(subsFile))
  else: return subsFile
  
@login_required
def convert(request,key): 
  arg = "%s%s"%(DOWNLOADS_DIR,key)
  base, infile = arg.rsplit('/',1)
  outfile = infile.rsplit('.',1)[0]
  subprocess.call(['mv',arg,'%s%s'%(CONVERT_DIR,infile)])
  subprocess.call(['touch','%s~'%arg])
  subprocess.Popen(['screen','python','/home/can/torrentor/downloader/convert.py',arg])
  return HttpResponseRedirect("/browse/%s"%key.rsplit('/',1)[0])

@login_required
@csrf_exempt
def search(request,path="home"):
    query= request.POST['query']
    if path == "home":
      path = "" 
      back = {}
    else:
      back = OrderedDict()
      plist = path.split("/")[1:] if len(path)==0 else path.split("/")
      conpath = ""
      for e in plist:
        conpath += "/%s"%e
        back[e] = "/browse%s"%conpath
    inside = OrderedDict()
    p = re.compile(r'(%s)'%query,re.IGNORECASE)
    canonical = to_canonical(path)
    if os.path.isdir(canonical):
      for item in os.listdir(canonical):
        if query.lower() in removeNonAscii(item).lower():
          name = re.sub(p,r'<span style="background-color:yellow;">\1</span>',item)
          if path=="":
            inside[name] = "%s"%item
          else:
            inside[name] = "%s/%s"%(path,item)
      inside = OrderedDict(sorted(inside.iteritems()))
    return render_to_response('files.html', {'from': back, 'to':inside, 'current':path, 'q':query})
  
@login_required
def searchtorrents(request,query):
  h = httplib.HTTPConnection('fenopy.se')
  h.request('GET','/module/search/api.php?keyword='+query+'&format=json&limit=5')
  data = h.getresponse().read()
  return HttpResponse(data,mimetype="application/json")


@login_required
def browse(request,path='home',page=1):
    if page<1: page = 1
    if path == "home":
      path = "" 
      back = {}
    else:
      back = OrderedDict()
      plist = path.split("/")[1:] if len(path)==0 else path.split("/")
      conpath = ""
      for e in plist:
        conpath += "/%s"%e
        back[e] = "/browse%s"%conpath
    inside = OrderedDict()
    path = smart_text(path)
    canonical = to_canonical(path)
    if os.path.isdir(canonical):
      if path == "":
        prc = Process.objects.filter(progress=0).order_by("-id")
        p = Paginator(prc,10)
        for item in p.page(page):
            inside[item.name] = "%s"%item.name
      else:
        p = Paginator(sorted(os.listdir(canonical)),10)
        for item in p.page(page):
            inside[prs(item)] = "%s/%s"%(path,unicode(item.decode('utf-8')))
        inside = OrderedDict(sorted(inside.iteritems()))
      #if page<p.num_pages: page = p.num_pages
      if path == '': path = 'home'
      return render_to_response('files.html', {'from': back,'user':request.user, 'to':inside, 'current':path,'page':int(page),'pages':p.page_range,"pmax":p.num_pages})
    elif plist[-1].lower().split(".")[-1] in ("mp4","m4v",'ogg'):
      return render_to_response('video.html', {'from': back,'user':request.user, 'media':path, 'title':path.split("/")[-1],'subtitle':subtitles(None,path)})
    elif plist[-1].lower().split(".")[-1]=="mp3":
      return render_to_response('audio.html', {'from': back,'user':request.user, 'media':path, 'title':path.split("/")[-1]})
    else: return HttpResponseRedirect("//torrentor.zapto.org:942/%s"%path)


def check_json(request): 
      lookup = Process.objects.filter(progress__gt=0).order_by("id").reverse()
      dump = [{'name':e.name,'progress':e.progress,'status':e.check()[1]} for e in lookup]
      return HttpResponse(json.dumps(dump),mimetype="application/json")

def browse_json(request,path='home',page=1):
    if page<1: page = 1
    if path == "home":
      path = "" 
      back = {}
    else:
      back = OrderedDict()
      plist = path.split("/")[1:] if len(path)==0 else path.split("/")
      conpath = ""
      for e in plist:
        conpath += "/%s"%e
        back[e] = "/browse%s"%conpath
    inside = OrderedDict()
    keyst  = []
    path = smart_text(path)
    canonical = to_canonical(path)
    if os.path.isdir(canonical):
      if path == "":
        prc = Process.objects.filter(progress=0).order_by("-id")
        p = Paginator(prc,10)
        for item in p.page(page):
            inside[item.name] = "%s"%item.name
            keyst += [item.name]
      else:
        p = Paginator(sorted(os.listdir(canonical)),10)
        for item in p.page(page):
            inside[prs(item)] = "%s/%s"%(path,unicode(item.decode('utf-8')))
            keyst += [prs(item)]
        inside = OrderedDict(sorted(inside.iteritems()))
      #if page<p.num_pages: page = p.num_pages
      #if path == '': path = 'home'
      return HttpResponse(json.dumps({'from': back, 'to':inside, 'keysto': keyst, 'current':path,'page':int(page),'pmax':p.num_pages}), mimetype="application/json")
    #elif plist[-1].lower().split(".")[-1] in ("mp4","m4v",'ogg'):
    #  return render_to_response('video.html', {'from': back,'user':request.user, 'media':path, 'title':path.split("/")[-1],'subtitle':subtitles(None,path)})
    #elif plist[-1].lower().split(".")[-1]=="mp3":
    #  return render_to_response('audio.html', {'from': back,'user':request.user, 'media':path, 'title':path.split("/")[-1]})
    #else: return HttpResponseRedirect("//torrentor.zapto.org:942/%s"%path)

@csrf_exempt
def upload_json(request):
    u = int(time.time())
    l = request.POST['torlink']
    try:
      data = urllib2.urlopen(l)
      buf = StringIO(data.read())
      f = gzip.GzipFile(fileobj=buf)
      data = f.read()
    except:
      data = urllib2.urlopen(l)
      data = data.read()
    with open("/home/can/torrentor/torrents/%d.torrent"%u,"wb") as f:
        f.write(data)
    with open("/home/can/torrentor/torrents/%d.torrent"%u) as f:
        raw = f.read()
    name = bencode.bdecode(raw)['info']['name']
    try:
        length = bencode.bdecode(raw)['info']['length']
    except:
        length = 0
        for file in bencode.bdecode(raw)['info']['files']:
            length += file['length']
    proc = Process.objects.create(tlink=l,name=name,length=length,ttype=1,progress=2)
    proc.save()
    print to_canonical(name)
    if(os.path.isdir(to_canonical(name))):
      if not os.path.exists(to_canonical(name)):
        os.makedirs(to_canonical(name))
    return HttpResponse('{"msg":true}',mimetype="application/json") 

