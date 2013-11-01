#!/usr/bin/env python
# -*- conding: utf-8 -*-
import sys,redis,json,xmlrpclib

db = redis.StrictRedis(host='localhost', port=6379, db=0)

def init_list():
  db.set('now_playing','')
  return 0

def play(filename):
  db.set('now_playing',filename)

def stop(filename):
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

def show_list():
  conn = xmlrpclib.ServerProxy('http://localhost/scgi')
  trs = [{'name':conn.d.get_base_filename(t),'drate':conn.d.get_down_rate(t),'done':conn.d.get_bytes_done(t),'total':conn.d.get_size_bytes(t)} for t in conn.download_list()]
  retval = json.dumps({'list':trs,'now_playing':db.get('now_playing')})
  return retval

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
  
