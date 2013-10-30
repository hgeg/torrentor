#!/usr/bin/env python
# -*- conding: utf-8 -*-
import sys,shelve,json

def init_list():
  db = shelve.open("downloads")
  db['list'] = []
  db.close()
  return 0

def remove_form_list(filename):
  db = shelve.open("downloads")
  lst = db['list']
  if filename in lst: lst.remove(filename)
  db['list'] = lst
  db.close()
  return 0

def add_to_list(filename):
  db = shelve.open("downloads")
  try:
    lst = db['list']
  except:
    db['list'] = []
    lst = db['list']
  lst += [filename]
  if len(lst)>10:
    lst.reverse()
    while len(lst)>10: lst.pop()
    lst.reverse()
  db['list'] = lst
  db.close()
  return 0

def show_list():
  db = shelve.open("downloads")
  retval = json.dumps({'list':db['list']})
  db.close()
  return retval


if __name__ == '__main__':
  if sys.argv[1] == '--add':
    add_to_list(sys.argv[2])
  elif sys.argv[1] == '--remove':
    remove_form_list(sys.argv[2])
  elif sys.argv[1] == '--list':
    print show_list()
  elif sys.argv[1] == '--init':
    init_list()
  
