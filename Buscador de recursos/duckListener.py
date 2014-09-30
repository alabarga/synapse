import requests # pip install requests
import json
import urllib
import datetime
import time
from google_search import GoogleCustomSearch
import duckduckgo
import uuid
import cyclone.escape
import os.path
from twisted.python import log
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import tweepy
import urllib2
import md5
import hashlib

def pp(o):
   return json.dumps(o, indent=4)
html_script = "<script src=\"//cdn.embedly.com/widgets/platform.js\"></script>"
class duckListener():

    def __init__(self,track,cache,limit=10):
        self.track = track[:][0]
        self.cache = cache
        self.limit = str(limit)
        self.running = 0
        self.last_id = 0
        self.pages=[]
        self.crawler=duckduckgo
    #Inicia la actividad de busqueda
    def start(self):
        print "hola duckduckgo"
        self.running=1
        while self.running==1:
            self.getPages()
            self.updatePosts(self.pages)
    #Para el escuchador        
    def stop(self):
        self.running=0
        return False
    #Busca en duckduck con los parametros que se pasen
    def getPages(self):
        #####TWITTER KEYS#####
        CONSUMER_KEY = 'ieZUZgZrSJJE0QLBBOsgXg'
        CONSUMER_SECRET = 'PlIpSrh6unKYZISSDieBIFAB3D9f6aSh4p4Dmcn8Q'
        OAUTH_TOKEN = '1015949947-0Akq5OBnEzTp7OwaIuvLNiKN6L52FNLVOW9yIyf'
        OAUTH_TOKEN_SECRET = 'SJz3nXcyGt2lIKhmPiFg5VlTdHLbrRSPRRgUZ552xfe1e'
        ####Twitter auth handler####
        auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
        auth.set_access_token(OAUTH_TOKEN,OAUTH_TOKEN_SECRET)
        #api = tweepy.API(auth)
        #r=api.search(q='www.google.com')
        #for i in r:
         #  print i.text

        #Google 
        # https://www.google.com/cse/all
        # https://www.google.com/cse/setup/basic?cx=009363772985848074726:jxffracj2_8
        SEARCH_ENGINE_ID = '009363772985848074726:jxffracj2_8' #os.environ['SEARCH_ENGINE_ID']   

        # https://console.developers.google.com/project/hontza-edu/apiui/credential                        
        API_KEY = 'AIzaSyCE9D6fjIW86IN2uekwJbaS3TDfNbim-lE' #os.environ['GOOGLE_CLOUD_API_KEY']

        api = GoogleCustomSearch(SEARCH_ENGINE_ID, API_KEY)
        links=[]
        for result in api.search('3D printing'):
          link=result['link']
          if link not in links:
              #print link
            links.insert(0,link)
        #EndGoogle

        #DuckDuckgo
        q=duckduckgo
        r=q.query('3D printing')

        for i in r.related:
            link=i.url
            if link not in links:
                links.insert(0,link)
        #api.import.io       
        url="https://api.import.io/store/data/97e350d1-d55c-4c66-bcc4-5c2bd2eb8765/_query?input/query="+"3D%20printing"+"&_user=7d0326db-696a-436d-8aba-f6c2e1c9e921&_apikey=89Gl8Ce2tiqX949GcKQTE9hCg6NW%2FkN36WpGKEA4knjhoTTRT72%2BitSWPicKFsZ4RmTwvyMbC%2BOrPtxAvy1EGw%3D%3D"
        response=urllib2.urlopen(url)
        res=response.read()
        res=json.loads(res)
        res=res['results']
        for li in res:
          link=li['url']
          if link not in links:
            links.insert(0,link)

        """ TABLA DE ENLACEs
        print "Tabla_______________________________________________"
        print "Url--------------Tweets que contienen la url-------------Delicious saved"
        for link in links:
          print link+" || "+str(get_tweets_for_url(link))+" || "+str(get_saves_for_url(link))
        """

        self.pages=links[0:10]


    #Se construye la tarjeta HTML y se envia a la cache
    def updatePosts(self,pages):
        for ht in pages:
            if self.running==1:
                log.msg("============================>")
                log.msg("got message from facebook")
                nodeId=str(uuid.uuid4())
                htmlcard="<a class=\"embedly-card\" href=\""+ht+"\">Prueba</a>\n"+html_script
                htmlcard="<div class=\"node\" id=\"m"+nodeId+"\">"+htmlcard+"</div>"
                #twitter sample url
                htmlcard=htmlcard+html_script
                node = {
                    "id": nodeId,
                    "html":htmlcard
                    }
                log.msg("Attemptim to update cache facebook")
                self.cache.update_cache(node)
                self.cache.send_updates(node)
                time.sleep(5)
    def get_tweets_for_url(self,url):
       response=urllib2.urlopen("http://urls.api.twitter.com/1/urls/count.json?url="+url)
       res=response.read()
       res=json.loads(res)
       return res['count']

    def get_saves_for_url(self,url):
       url=hashlib.md5(url).hexdigest()
       response=urllib2.urlopen("http://feeds.delicious.com/v2/json/url/"+url)        
       res=json.loads(response.read())
       count=0
       for item in res:
          count+=1
       return count 
















