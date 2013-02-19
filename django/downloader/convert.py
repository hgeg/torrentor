#!/usr/bin/python
import sys,subprocess
from datetime import datetime
DOWNLOADS_DIR = "/home/can/torrentor/downloads/" 
CONVERT_DIR = "/home/can/torrentor/convert/"
base, infile = sys.argv[1].rsplit('/',1)
outfile = infile.rsplit('.',1)[0]
if "-m" in sys.argv:
  subprocess.call(['mv','%s'%sys.argv[1],'%s%s'%(DOWNLOADS_DIR,infile.replace(' ',''))])
  subprocess.call(['touch','%s~'%sys.argv[1]])
elif "-c" in sys.argv:
  subprocess.call(['cp','%s'%sys.argv[1],'%s%s'%(CONVERT_DIR,infile.replace(' ',''))])
try:
  print "Starting operation on",datetime.now()
  print "converting",infile
  i=subprocess.call(['ffmpeg', '-i', '%s%s'%(CONVERT_DIR,infile.replace(' ','')), '-vcodec', 'libx264', '-preset', 'veryfast', '-threads', '0', '-strict', 'experimental', '-acodec', 'aac', '%s/%s.mp4'%(base,outfile.replace(' ',''))])
  assert(i==0)
  print "conversion process finished with code:",i
  #subprocess.call(['cp','%s%s.mp4'%(CONVERT_DIR,outfile.replace(' ','')),'"%s/%s.mp4"'%(base,outfile)])
  print "output is moved to location %s/%s"%(base,outfile)
except:
  print "Exception, operation aborted"
  subprocess.call(['cp','%s%s.mp4'%(CONVERT_DIR,infile.replace(' ','')),'"%s/%s.mp4"'%(base,infile)])
  print "input is moved to location %s/%s"%(base,infile)
finally:
  print "Executing clean-up..."
  subprocess.call(['rm','%s~'%sys.argv[1]])
  print "EXIT\n"
