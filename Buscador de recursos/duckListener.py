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

##NUEVO
import unfurl
from goose import Goose
from pyteaser import SummarizeUrl
import tldextract
from pymongo import MongoClient
#client = MongoClient('localhost', 27017)

#####TWITTER KEYS#####
CONSUMER_KEY = 'ieZUZgZrSJJE0QLBBOsgXg'
CONSUMER_SECRET = 'PlIpSrh6unKYZISSDieBIFAB3D9f6aSh4p4Dmcn8Q'
OAUTH_TOKEN = '1015949947-0Akq5OBnEzTp7OwaIuvLNiKN6L52FNLVOW9yIyf'
OAUTH_TOKEN_SECRET = 'SJz3nXcyGt2lIKhmPiFg5VlTdHLbrRSPRRgUZ552xfe1e'
####Twitter auth handler####
auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(OAUTH_TOKEN,OAUTH_TOKEN_SECRET)
twittApi = tweepy.API(auth)

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
        self.running=1
        self.getPages()
        self.updatePages(self.pages)
        #while self.running==1:
        
            #self.updatePosts(self.pages)
            
    #Para el escuchador        
    def stop(self):
        self.running=0
        return False
    #Busca en duckduck con los parametros que se pasen
    def getPages(self):
        links=[]
        #r=twittApi.search(q='www.google.com')
        #for i in r:
         #  print i.text
        """
        #Google 
        # https://www.google.com/cse/all
        # https://www.google.com/cse/setup/basic?cx=009363772985848074726:jxffracj2_8
        SEARCH_ENGINE_ID = '009363772985848074726:jxffracj2_8' #os.environ['SEARCH_ENGINE_ID']   

        # https://console.developers.google.com/project/hontza-edu/apiui/credential                        
        API_KEY = 'AIzaSyCE9D6fjIW86IN2uekwJbaS3TDfNbim-lE' #os.environ['GOOGLE_CLOUD_API_KEY']

        api = GoogleCustomSearch(SEARCH_ENGINE_ID, API_KEY)
        
        for result in api.search('3D printing'):
          link=result['link']
          if link not in links:
              #print link
            links.insert(0,link)
        #EndGoogle"""
        print "Bien1"

        #DuckDuckgo
        q=duckduckgo
        r=q.query('3D printing')

        for i in r.related:
            link=i.url
            if link not in links:
                links.insert(0,link)

        #api.import.io       
        url="https://api.import.io/store/data/97e350d1-d55c-4c66-bcc4-5c2bd2eb8765/_query?input/query="+"LinkinPark"+"&_user=7d0326db-696a-436d-8aba-f6c2e1c9e921&_apikey=89Gl8Ce2tiqX949GcKQTE9hCg6NW%2FkN36WpGKEA4knjhoTTRT72%2BitSWPicKFsZ4RmTwvyMbC%2BOrPtxAvy1EGw%3D%3D"
        response=urllib2.urlopen(url)
        res=response.read()
        res=json.loads(res)
        res=res['results']
        for li in res:
          link=li['url']
          if link not in links:
            links.insert(0,link)
        print "Bien3"    
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
                #log.msg("============================>")
                #log.msg("got message from facebook")
                nodeId=str(uuid.uuid4())
                htmlcard="<a class=\"embedly-card\" href=\""+ht+"\">Prueba</a>\n"+html_script
                htmlcard="<div class=\"node\" id=\"m"+nodeId+"\">"+htmlcard+"</div>"
                #twitter sample url
                htmlcard=htmlcard+html_script
                node = {
                    "id": nodeId,
                    "html":htmlcard
                    }
                #log.msg("Attemptim to update cache facebook")
                self.cache.update_cache(node)
                self.cache.send_updates(node)
                time.sleep(5)
    

    def updatePages(self,pages):
        ##para cada url:
        for page in pages:      
            ###Mirar sis es url corta y convertirla

            #try:
                #page=unfurl.expand_url(page)           
            #except (RuntimeError, TypeError, NameError):
               # pass
            print page
            ###Mirar si ya esta en la BD
            
            ##Crear el recursos
                ##pyteaser
                ##goose
                ##quien habla en twiter delicious
                ##hashtags twitter y etiquetas delicous
                ##related to
            try:    
                Resource=self.createResource(page)
            except:
                pass
            print "  "
            print "  "
            print Resource
            print "  "
            print "  "
            #db = client.Synapse
            #resources = db.Resources
            ##introducir a la BD
            #resources.insert(Resource)
    
    
    def createResource(self,url):
        g = Goose()
        a= g.extract(url=url)
        #faltan los de comentados
        #crearid
        #externalid
        raw_content=a.raw_doc
        #location_name
        #location_lon
        #location_lat 
        url_hash=hashlib.md5(url).hexdigest()      
        authors,tags=self.get_authsAndTags(url)
        social_network=tldextract.extract(url)
        summaries=SummarizeUrl(url)
        resource={"url":url,"url_hash":url_hash,"meta_description":a.meta_description,"meta_keywords":a.meta_keywords,"meta_lang":a.meta_lang,"title":a.title,"social_network":social_network,"raw_content":a.raw_doc,"summaries":summaries,"authors":authors,"tags":tags}
        return resource

    def get_authsAndTags(self,url):
        url=hashlib.md5(url).hexdigest()
        response=urllib2.urlopen("http://feeds.delicious.com/v2/json/url/"+url)        
        delRes=json.loads(response.read())
        s=twittApi
        twitRes=s.search(url)
        authors=[]
        tags=[]
        for a in delRes:
            author=a["a"]
            if author not in authors:
                authors.insert(0,author)
            for t in a["t"]:
                if t not in tags:
                    tags.insert(0,t)
        #se supone que Twitres es una lsita hacer cosas
        for r in twitRes:
            author=r.author.name
            if author not in authors:
                authors.insert(0,author)
            #s=el string del tweet
            hts=self.extract_hash_tags(s)
            for ht in hts:
                if ht not in tags:
                    tags.insert(0,ht)
        return authors,tags
        
    def extract_hash_tags(self,s):
        return set(part[1:] for part in s.split() if part.startswith('#'))            



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
















