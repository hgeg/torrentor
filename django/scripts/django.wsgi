import os,sys

path = '/home/can/torrentor'
if path not in sys.path:
  sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi as app
application = app.WSGIHandler()
