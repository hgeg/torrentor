# -*- coding: utf-8 -*-
from django import template 
import os,string

def s(st): return filter(lambda x: x in string.printable, st)

register = template.Library()

@register.filter(name='noext')
def noext(value): return value.rsplit('.',1)[0]

@register.filter(name='ext')
def ext(value): return value.rsplit('.',1)[1]

@register.filter(name='isconv')
def isconv(value): return value.find('~')>0

@register.filter(name='isdone')
def isdone(value): return value.find('~')<0

@register.filter(name='isdir')
def isdir(value): return os.path.isdir('/home/can/torrentor/downloads/%s'%s(value))

@register.filter(name='path')
def path(value): 
  return '/home/can/torrentor/downloads/%s'%s(value)

