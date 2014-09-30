from dnowglobals import *
import os
import signal
import sys    

def pp(o):
   return json.dumps(o, indent=4)
#Detiene el servidor
def kill():
    log.msg('You pressed Ctrl+C!')
    pid=os.getpid()
    os.kill(pid,signal.SIGKILL)

class RealTimeSocketHandler(cyclone.websocket.WebSocketHandler):

    def initialize(self,cache):
        self.cache=cache
    #Llega una conexion websocket
    def connectionMade(self):
        log.msg("Connection made through websocket")
        self.cache.waiters.add(self)
        #log.msg("Total ",len(self.cache.waiters))
    #Se cierra una conexion websocket
    def connectionLost(self, reason):
        log.msg("Connection lost through websocket")
        self.cache.waiters.remove(self)
    #Se recibe un mensaje mediante websocket
    def messageReceived(self, message):
        #message=unicode(message,'utf-8')
        keywords=False
        message=message
        log.msg("Some user has changed the keywords to %s" % message)
        parsed = cyclone.escape.json_decode(message)
        print parsed
        selNets={}
        cParser=parser()
        soNet=cParser.parseConfig()
        for sN in soNet:
            try:
                if parsed[sN]=="on" and parsed["keywords"+sN]!="":
                    newTag = parsed["keywords"+sN]
                    newTag=newTag.encode('utf-8')
                    if newTag=="kill_server":
                        log.msg("Killing the server")
                        kill()
                    kw=[]
                    kw.append(str(newTag))
                    inner={}
                    inner['name']=sN
                    for op in soNet[sN]:
                        if self.get_argument(sN+op, ''):
                            inner[sN+op]=self.get_argument(sN+op, '')
                    inner['kw']=kw
                    selNets[sN]=inner
                    keywords=True
                else:
                    continue
            except:
                log.msg("That key doesnt exists!")
                pass
        if keywords==True:        
            self.cache.stopListeners()
            self.cache.runListeners(selNets)

class MainHandler(cyclone.web.RequestHandler):
    
    def initialize(self,cache):
        self.cache=cache
        self.soNet=[]
        signal.signal(signal.SIGINT, self.signal_handler)
    #Recibida peticion GET
    def get(self):
        cParser=parser()
        soNet=cParser.parseConfig()
        self.soNet=soNet
        if self.cache.tracking==None:
            self.render("keywordsForm.html",networks=soNet)
        else:  
            self.render("index.html",nodes=self.cache.cache,networks=soNet)
    #Recibida peticion POST
    def post(self):
        keywords=False
        selNets={}
        cParser=parser()
        soNet=cParser.parseConfig()
        for sN in soNet:
            if not self.get_argument(sN, ''):
                continue
            else:
                if not self.get_argument('keywords'+sN, ''):
                    continue                
                else:
                    keywords=self.get_argument('keywords'+sN, '')
                    kw=[]
                    kw.append(str(keywords.encode('utf-8')))
                    cParser=parser()
                    soNet=cParser.parseConfig()
                    inner={}
                    inner['name']=sN
                    for op in soNet[sN]:
                        if self.get_argument(sN+op, ''):
                            inner[sN+op]=self.get_argument(sN+op, '')
                    inner['kw']=kw
                    selNets[sN]=inner
                    keywords=True
        if keywords==True:
            self.cache.sn=selNets
            self.cache.runListeners(selNets)            
            self.render("index.html",nodes=self.cache.cache,networks=soNet)
        else:
            self.render("keywordsForm.html",networks=soNet)
    #Peticion de cerrar servidor    
    def signal_handler(self,signal, frame):
        print('You pressed Ctrl+C!')
        kill()
class ShutDown(cyclone.web.RequestHandler):
    
    def initialize(self,cache):
        self.cache=cache
    #Reiniciar el sistema completamente
    def get(self):
        print "QUIERE TERMINAR TODO"
        self.cache.clear()
        self.redirect("/")
        
if __name__ == "__main__":
    cache=embedCache()
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        autoescape=None
        )
    #Asociacion de rutas
    application = cyclone.web.Application([
        (r"/", MainHandler,dict(cache=cache)),
        (r"/realtime", RealTimeSocketHandler,dict(cache=cache)),
        (r"/shutdown", ShutDown,dict(cache=cache))
    ],**settings)
    log.startLogging(sys.stdout)
    reactor.listenTCP(8888, application, interface="127.0.0.1")
    reactor.run()