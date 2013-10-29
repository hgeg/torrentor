#!/usr/bin/env python
# -*- conding: utf-8 -*-
import sys,shelve

def remove_form_list(filename):
  downloads = shelve.open("downloads")
  lst = downloads['list']
  if filename in lst: lst.remove(filename)
  downloads.close()

def add_to_list(filename):
  downloads = shelve.open("downloads")
  lst = downloads['list']
  lst.append(filename)
  lst.reverse()
  while len(lst)>10: lst.pop()
  lst.reverse()
  downloads.close()

if __name__ == '__main__':
  if sys.argv[1] == '--add':
    add_to_list(sys.argv[2])
  elif sys.argv[2] == '--remove':
    remove_form_list(sys.argv[2])
  return 0
  
