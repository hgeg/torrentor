from __future__ import with_statement
import os,sys

content = ""
SITE_DIR = sys.argv[1]
DATA_DIR = sys.argv[2]
DFT_USER = sys.argv[3]

with open('torrentor.conf','r') as f:
  content = f.read()
with open('torrentor.conf','w+') as f:
  f.write(content.replace('<SITE_DIR>',SITE_DIR).replace('<DATA_DIR>',DATA_DIR))

with open('torrentor-stack','r') as f:
  content = f.read()
with open('torrentor-stack','w+') as f:
  f.write(content.replace('<SITE_DIR>',SITE_DIR).replace('<DATA_DIR>',DATA_DIR).replace('<USER>',DFT_USER))

with open('runapps.sh','r') as f:
  content = f.read()
with open('runapps.sh','w+') as f:
  f.write(content.replace('<SITE_DIR>',SITE_DIR).replace('<DATA_DIR>',DATA_DIR))

with open('settings.py','r') as f:
  content = f.read()
with open('settings.py','w+') as f:
  f.write(content.replace('<SITE_DIR>',SITE_DIR).replace('<DATA_DIR>',DATA_DIR))

with open('%s/rtorrent.rc'%SITE_DIR,'r') as f:
  content = f.read()
with open('%s/.rtorrent.rc'%SITE_DIR,'w+') as f:
  f.write(content.replace('<SITE_DIR>',SITE_DIR).replace('<DATA_DIR>',DATA_DIR))
