#-*- coding: UTF-8 -*-
import requests # pip install requests
import json
import datetime
import time
from google_search import GoogleCustomSearch
import duckduckgo
import uuid
import cyclone.escape
import os.path
from twisted.python import log
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import urllib2
import md5
import hashlib
import unfurl
from goose import Goose
from pyteaser import SummarizeUrl
import tldextract
from pymongo import MongoClient
from pyslideshare2 import pyslideshare
import xml.etree.ElementTree as ET
from random import shuffle
import sha
import feedfinder
import feedparser
import re
from urlunshort import resolve

##Mongo client
client = MongoClient('localhost', 27017)
db = client.Synapse

#####TWITTER KEYS#####
CONSUMER_KEY = 'ieZUZgZrSJJE0QLBBOsgXg'
CONSUMER_SECRET = 'PlIpSrh6unKYZISSDieBIFAB3D9f6aSh4p4Dmcn8Q'
OAUTH_TOKEN = '1015949947-0Akq5OBnEzTp7OwaIuvLNiKN6L52FNLVOW9yIyf'
OAUTH_TOKEN_SECRET = 'SJz3nXcyGt2lIKhmPiFg5VlTdHLbrRSPRRgUZ552xfe1e'
####Twitter auth handler####
auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(OAUTH_TOKEN,OAUTH_TOKEN_SECRET)
twittApi = tweepy.API(auth)
####Google custom search API####
SEARCH_ENGINE_ID = '009363772985848074726:jxffracj2_8' #os.environ['SEARCH_ENGINE_ID']                          
API_KEY = 'AIzaSyCE9D6fjIW86IN2uekwJbaS3TDfNbim-lE' #os.environ['GOOGLE_CLOUD_API_KEY']
googleApi = GoogleCustomSearch(SEARCH_ENGINE_ID, API_KEY)
####Slideshare API keys####
ssapi_key = 'lKp4aIF5' # Your api key
sssecret_key = 'x7fmnUa8' # Your secret key
##########################

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
    #Inicia la actividad de busqueda
    def start(self):
        self.running=1
        while self.running==1:
            self.getPages()
            self.updatePages(self.pages)
            #self.updatePosts(self.pages)
            self.running=0
            
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
        self.getGoogleSearch("query",links)
        """
        self.getInterestingUserTwitter("3dprinting")
        #DuckDuckgo
        #self.getDuckGo("query",links)
        #api.import.io       
        #self.getApiIO("query",links)
        ###Get slideshows && search slideshows
        #self.getSlideShow(query="3DPrinting",links=links)
        #self.getSlideShow(tag="3DPrinting",links=links)
        ###Take 10 links randomly
        #shuffle(links)
        #links=['http://t.co/oJj4lEcWJI']
        #self.pages=links[0:20]
        """ TABLA DE ENLACEs
        print "Tabla_______________________________________________"
        print "Url--------------Tweets que contienen la url-------------Delicious saved"
        for link in links:
          print link+" || "+str(get_tweets_for_url(link))+" || "+str(get_saves_for_url(link))
        """

    def getGoogleSearch(self,query="",links=[]):
        for result in googleApi.search('3D printing'):
          link=result['link']
          if link not in links:
              #print link
            links.insert(0,link)

    def getDuckGo(self,query="",links=[]):
        q=duckduckgo
        r=q.query('3D printing')
        for i in r.related:
            link=i.url
            if link not in links:
                links.insert(0,link)

    def getApiIO(self,query="",links=[]):
        url="https://api.import.io/store/data/97e350d1-d55c-4c66-bcc4-5c2bd2eb8765/_query?input/query="+"Linkin%20Park"+"&_user=7d0326db-696a-436d-8aba-f6c2e1c9e921&_apikey=89Gl8Ce2tiqX949GcKQTE9hCg6NW%2FkN36WpGKEA4knjhoTTRT72%2BitSWPicKFsZ4RmTwvyMbC%2BOrPtxAvy1EGw%3D%3D"
        response=urllib2.urlopen(url)
        res=response.read()
        res=json.loads(res)
        res=res['results']
        for li in res:
          link=li['url']
          if link not in links:
            links.insert(0,link) 


    def getInterestingUserTwitter(self,query):
        users = db.Users
        url="https://api.import.io/store/data/2297660e-b775-433d-a408-8fb6d7a808e7/_query?input/webpage/url=http%3A%2F%2Fwefollow.com%2Finterest%2F"+query+"%2F62-100&_user=7d0326db-696a-436d-8aba-f6c2e1c9e921&_apikey=89Gl8Ce2tiqX949GcKQTE9hCg6NW%2FkN36WpGKEA4knjhoTTRT72%2BitSWPicKFsZ4RmTwvyMbC%2BOrPtxAvy1EGw%3D%3D"
        response=urllib2.urlopen(url)
        res=response.read()
        res=json.loads(res)
        int_Users=res['results']
        for user in int_Users:
            username=str(user['username'])
            score=int(user['score'])
            social_network="Twitter"
            description=str(user['description'])
            doc={"username":username,"subject":query,"score":score,"social_network":social_network,"description":description,"last_updated":datetime.datetime.now()}
            users.insert(doc)
            print "insertado usuario"+username

    def getSlideShow(self,query="",tag="",links=[]):
        ts = int(time.time())
        time_hash=sha.new(sssecret_key + str(ts)).hexdigest()   
        if query!="":
            url="https://www.slideshare.net/api/2/search_slideshows?q="+query+"&api_key="+ssapi_key+"&hash="+time_hash+"&ts="+str(ts)
        elif tag!="":
            url="https://www.slideshare.net/api/2/get_slideshows_by_tag?tag="+tag+"&limit=10&api_key="+ssapi_key+"&hash="+time_hash+"&ts="+str(ts)
        else: 
            print "error"
        response=urllib2.urlopen(url)
        res=response.read()
        #print res
        root = ET.fromstring(res)
        for child in root:
            try:
                link=child[5].text
                if link not in links:
                    links.insert(0,link)
            except:
                pass

    #Se construye la tarjeta HTML y se envia a la cache
    def updatePosts(self,pages):
        for ht in pages:
            if self.running==1:
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
        resources = db.Resources
        for page in pages:      
            ###Mirar sis es url corta y convertirla
            #try:
             #   page=unfurl.expand_url(page)           
            #except (RuntimeError, TypeError, NameError):
             #   pass
            ###Mirar si ya esta en la BD
            if resources.find({'url':page}).count()==0:
                print "Trying to insert new URL: "+page
                try:
                    #self.getRss(page)    
                    Resource=self.createResource(page)
                except:
                    print "erroraco al crear el recurso"
                ##introducir a la BD
                try:
                    resources.insert(Resource)
                    print "Succesfully inserted"
                except:
                    print "Something went wrong you silly boy"

    def getRss(self,url):
        f=feedfinder.feed(url)
        if f!=None:
            print "ESTE ENLACE TIENE RSS: "+f
            #mirar base datos
            feeds=db.Feeds
            a=feeds.find({'rss_url':f,'lasthash':True},{'hash':1})
            count=a.count()
            feed=feedparser.parse(f)
            i=0
            j=0
            new_lasthash=""
            
            for fe in feed.entries:
                j+=1
                thishash = hashlib.md5(fe.link.encode("utf8") + fe.title.encode("utf8")).hexdigest()
                if count==0:##no hay ningun feed de esa pagina
                    doc=self.getAttrib(fe)
                    if i==0:
                        i+=1
                        doc["rss_url"]=f
                        doc["lasthash"]=True
                        doc["hash"]=thishash 
                    else:
                        doc["rss_url"]=f
                        doc["lasthash"]=False
                        doc["hash"]=thishash 
                    feeds.insert(doc)
                else:#hay algun feed de esa pagina
                    for lh in a:
                        lasthash=lh['hash']
                    #if lasthash!=thishash:
                    if feeds.find({'link ':fe.link}).count()==0:
                        #nuevo feed
                        #feeds.find({'rss_url':f}).count()
                        doc=self.getAttrib(fe)
                        if i==0:
                            new_lasthash=thishash 
                            feeds.update({'rss_url':f,'lasthash':True},{"$set":{'rss_url':f,'lasthash':False}})
                            doc["rss_url"]=f
                            doc["lasthash"]=True
                            doc["hash"]=thishash 
                            i+=1
                            feeds.insert(doc)
                        else:
                            doc["rss_url"]=f
                            doc["lasthash"]=False
                            doc["hash"]=thishash 
                            feeds.insert(doc)
                    else:
                        print "Terminado"
                        break
                        
        else:
            print "No tiene RSS"
            
    def getAttrib(self,feed):
        doc={}
        #doc={"lasthash":True,'hash':thishash,'rss_url':f,'url':fe.link,'summary':fe.summary,'title':fe.title,'title_detail':fe.title_detail,'author':{'name':fe.author,'detail':fe.author_detail},'published':fe.published,'e_id':fe.id}
        for atr in ['link','summary','title','title_detail','author','author_detail','published','id']:
            if hasattr(feed,atr):
                doc[atr]=feed[atr]
            else:
                doc[atr]=""
        return doc

    def createResource(self,url,related_to="",leaf=0):
        if resolve(url)!=None:
             url=resolve(url)
        g = Goose()
        a= g.extract(url=url)
        #faltan los de comentados
        raw_content=a.raw_doc
        #location_name
        #location_lon
        #location_lat
        url_hash=hashlib.md5(url).hexdigest()      
        authors,tags=self.get_authsAndTags(url,leaf)
        social_network=tldextract.extract(url)
        summaries=SummarizeUrl(url)
        interest=self.get_interest(url)
        resource={"related_to":related_to,"url":url,"url_hash":url_hash,"meta_description":a.meta_description,"meta_keywords":a.meta_keywords,"meta_lang":a.meta_lang,"title":a.title,"summaries":summaries,"authors":authors,"tags":tags,"interest":interest}
        return resource

    def get_authsAndTags(self,url,leaf):
        url_link=url
        a=resolve(url)
        url=hashlib.md5(url).hexdigest()
        response=urllib2.urlopen("http://feeds.delicious.com/v2/json/url/"+url)        
        delRes=json.loads(response.read())
        s=twittApi
        twitRes=s.search(url_link)
        authors=[]
        tags=[]
        for a in delRes:
            author=a["a"]
            if author not in authors:
                authors.insert(0,author)
            for t in a["t"]:
                if leaf==0:
                    self.relatedTo(author,url_link,t,"delicious")
                if t not in tags:
                    tags.insert(0,t)
        #se supone que Twitres es una lsita hacer cosas
        for r in twitRes:
            author=r.author.name
            if author not in authors:
                authors.insert(0,author)
            #s=el string del tweet
            hts=self.extract_hash_tags(r.text)
            for ht in hts:
                if leaf==0:
                    self.relatedTo(author,url_link,ht,"twitter",r.id)
                if ht not in tags:
                    tags.insert(0,ht)
        return authors,tags

    def relatedTo(self,user,url,tag,social_network,max_id=0):
        firsturl=url
        resources = db.Resources
        tagl=[]
        tagl.append(tag)
        relatedToTweet=[]
        relatedToDel=[]
        if social_network=="twitter":
            print "Entrado en reltated totwitter para: "+url
            response=twittApi.user_timeline(user=user,max_id=max_id-1,count=50)
            for tweet in response:
                ht=self.extract_hash_tags(tweet.text)
                intersect=list(set(tagl) & set(ht))
                if len(intersect)>0:
                    #relatedToTweet.append(tweet)
                    ##mirar si en el texto hay enlaces
                    ##para cada enlace dle texto
                    links= self.extract_urls(str(tweet.text))
                    print links
                    for link in links:
                        Resource=self.createResource(link,firsturl,1)
                        try:
                            resources.insert(Resource)
                            print "Succesfully inserted related resource twitter"
                        except:
                            print "Something went wrong you silly boy in related twitter"
        elif social_network=="delicious":    
            url="http://feeds.delicious.com/v2/json/"+str(user)+"/"+urllib2.quote(str(tag),'')
            print "accediendo a"+ url#para cambiar los espacios a %20 
            response=urllib2.urlopen(url)
            print "opene2"
            resp=json.loads(response.read())
            print "opene2"
            for res in resp:
                if firsturl!=str(res["u"]):
                    print "Link relacionado en delicious: "+str(res["u"])
                    Resource=self.createResource(str(res["u"]),firsturl,1)
                    try:
                        resources.insert(Resource)
                        print "Succesfully inserted resource delicious"
                    except:
                        print "Something went wrong you silly boy in  delicious"
                        pass
                else:
                    print "eran el mimso url"
        else:
            print "Este enlace no tiene nada de twitter ni deli"
        
    def extract_hash_tags(self,s):
        return set(part[1:] for part in s.split() if part.startswith('#'))            

    def extract_urls(self,s):
        a= re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', s)
        return a
    def get_tweets_for_url(self,url):
       response=urllib2.urlopen("http://urls.api.twitter.com/1/urls/count.json?url="+url)
       res=response.read()
       res=json.loads(res)
       return res['count']

    def get_saves_for_url(self,url):
       url=hashlib.md5(url).hexdigest()
       response=urllib2.urlopen("http://feeds.delicious.com/v2/json/url/"+url)        
       res=json.loads(response.read())
       count=len(res)
       return count 

    def get_interest(self,url):
        response=urllib2.urlopen('http://free.sharedcount.com/?url='+url+'&apikey=cabec5c5d636b063cbbcf8cbe966fd3c4c7d9152')
        res=json.loads(response.read())
        return res