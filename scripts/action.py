#!/usr/bin/env python
# -*- conding: utf-8 -*-
import sys,shelve

def init_list():
  db = shelve.open("downloads")
  db['list'] = []
  db.close()
  return 0

def remove_form_list(filename):
  db = shelve.open("downloads")
  lst = downloads['list']
  if filename in lst: lst.remove(filename)
  db.close()
  return 0

def add_to_list(filename):
  db = shelve.open("downloads")
  lst = downloads['list']
  lst += [filename]
  if len(lst)>10:
    lst.reverse()
    while len(lst)>10: lst.pop()
    lst.reverse()
  db.close()
  return 0

if __name__ == '__main__':
  if sys.argv[1] == '--add':
    add_to_list(sys.argv[2])
  elif sys.argv[1] == '--remove':
    remove_form_list(sys.argv[2])
  elif sys.argv[1] == '--init':
    init_list()
  
