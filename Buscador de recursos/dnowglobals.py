import cyclone.web
import sys
import uuid
import cyclone.escape
import os.path
import cyclone.websocket
from twisted.internet import reactor
from twisted.python import log
from twisted.internet import threads
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web import server, resource
import json
import threading
from configParser import parser
from duckListener import *
import datetime
import time

class embedCache(object):

   def __init__(self):
      self.waiters = set()
      self.cache = []
      self.numLis=0
      self.listeners={}
      self.listenersInstances={}
      self.cache_size = 20
      self.tracking = None
      self.lock = threading.RLock()
   #Metodo que actualiza la cache
   def update_cache(self, htmlCard):
      with self.lock:
         if len(self.cache) > self.cache_size:
            self.cache = self.cache[0:self.cache_size-1]
         self.cache.insert(0,htmlCard['html'])
         log.msg("Cache updated")
   #Metodo que envia las actualizaciones a los clientes activos.
   def send_updates(self, htmlCard):
      log.msg("Sending message to %d waiters" % len(self.waiters))
      for waiter in self.waiters:
         try:
            waiter.sendMessage(htmlCard)
         except Exception, e:
            log.err("Error sending message. %s" % str(e))
   #Metodo que inicia los escuchadores con los parametros que le envia MainHandler o RealTimeSocketHandler.
   def runListeners(self,nets):
      self.tracking=True
      listeners={}
      #result=configParser.parseConfig()
      for i in nets:
         kw=nets[i]['kw']
         #log.msg(i+" tiene opciones: "+str(i['name']))
         if i=="Twitter":
            twitter=twitterListener(kw,True,self)
            listeners["Twitter"]=twitter
            log.msg("Twitter listener starting...")
         if i=="Facebook":
            facebook=facebookListener(kw,self)
            listeners["Facebook"]=facebook
            log.msg("Facebook listener starting...")
         if i=="DuckDuckGo":
            duck=duckListener(kw,self)
            listeners["DuckDuckGo"]=duck
            log.msg("DuckDuckGo listener starting...")
         if i=="Youtube":
            try:   
               option=nets[i]['Youtubeoption']
            except:
               option=""
               log.msg("Youtube doesn't have options")
            youtube=youtubeListener(kw,self)
            listeners["Youtube"]=youtube
            log.msg("Youtube listener starting...")
         if i=="Flickr":
            try:               
               fecha_min=nets[i]['FlickrFechaMinimaCaptura']
               fecha_max=nets[i]['FlickrFechaMaximaCaptura']
            except:
               y = datetime.date.today() - datetime.timedelta(1)
               t = datetime.date.today() + datetime.timedelta(1)
               fecha_min=str(y)
               fecha_max=str(t)
            flickr=flickrListener(kw,self,fecha_min,fecha_max) 
            listeners["Flickr"]=flickr
            log.msg("Flickr listener starting...")
      list_of_listeners={}
      for d in listeners:
         if d=="Twitter":
            listhread = listeners[d].start() 
         else:
            listhread = threads.deferToThread(listeners[d].start)
         list_of_listeners[d]=listhread 
         self.numLis=self.numLis+1      
      self.listeners=list_of_listeners
      self.listenersInstances=listeners  
   #Metodo que para los escuchadores
   def stopListeners(self):
      log.msg("First, we have to stop the active listeners")
      for activeLis in self.listeners:
         log.msg("Stopping : "+activeLis)
         try:
            self.listeners[activeLis].disconnect()
         except:
            self.listenersInstances[activeLis].stop()
      self.numLis=0
   #Metodo que inicializa los parametros de la cache.
   def clear(self):
      self.stopListeners()
      self.cache = []
      self.numLis=0
      self.listeners={}
      self.listenersInstances={}
      self.tracking = None
      self.lock = threading.RLock()