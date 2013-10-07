from __future__ import with_statement
import os,sys

content = ""
BASE_DIR = sys.argv[1]
SETUP_DIR = os.getcwd()
HOME_DIR = os.path.expanduser("~")
with open('runapps.sh','r') as f:
  content = f.read()
with open('runapps.sh','w+') as f:
  f.write(content.replace('<BASE_DIR>',BASE_DIR))

with open('settings.py','r') as f:
  content = f.read()
with open('settings.py','w+') as f:
  f.write(content.replace('<BASE_DIR>',BASE_DIR))

with open('%s/rtorrent.rc'%SETUP_DIR,'r') as f:
  content = f.read()
with open('%s/.rtorrent.rc'%HOME_DIR,'w+') as f:
  print f.abspath
  f.write(content.replace('<BASE_DIR>',BASE_DIR))



