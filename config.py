from __future__ import with_statement
import os,sys

content = ""
DATA_DIR = sys.argv[1]
SITE_DIR = sys.argv[2]

with open('runapps.sh','r') as f:
  content = f.read()
with open('runapps.sh','w+') as f:
  f.write(content.replace('<SITE_DIR>'SITE_DIR).replace('<DATA_DIR>',DATA_DIR))

with open('settings.py','r') as f:
  content = f.read()
with open('settings.py','w+') as f:
  f.write(content.replace('<SITE_DIR>'SITE_DIR).replace('<DATA_DIR>',DATA_DIR))

with open('%s/rtorrent.rc'%SETUP_DIR,'r') as f:
  content = f.read()
with open('%s/.rtorrent.rc'%HOME_DIR,'w+') as f:
  f.write(content.replace('<SITE_DIR>'SITE_DIR).replace('<DATA_DIR>',DATA_DIR))
