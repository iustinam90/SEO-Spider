# -*- coding: utf-8 -*-
import requests,pickle,operator,datetime,threading,os,commands,logging,re,pdb,urllib,json
import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from seo_spider.inputs import publish_key,subscribe_key


#######################################################################################################
#
# This spider takes all external links from all pages (output from SEOSpider) and finds the broken ones  
#######################################################################################################

# callback for pubnub send/recv
def _callback(message):
    print(message)

# send to pubnub channel
def send_to_channel(ch,name,obj):
    from pubnub import Pubnub
    pubnub = Pubnub(publish_key, subscribe_key)
    s=json.dumps(obj)
    dl='-_-_'+str(len(s)+1000000)[1:]
    s=s+dl
    logging.warning(str(len(s)-10)+" "+ str(len(urllib.quote(s.encode("utf-8")))+97)) #pana a 16000…;la 18000 da err
    page_num=name
    for i in xrange(0, len(s), 12000):
        pubnub.publish(ch, name+page_num+str(i+1000000)[1:]+s[i:i+12000], callback= _callback, error= _callback)

############################################################################

class BrokenlinksSpider(scrapy.Spider):
    name = "BrokenLinks"
    blinks=[]
    start_urls=[]
    brokenLinksExternal={}
    
    ############################################################################
    # make sure we send data across pubnub clannel even when there were no broken links found 
    def my_close(self, spider):
        if not spider.brokenLinksExternal and spider.ch:
            send_to_channel(spider.ch,"ble", spider.brokenLinksExternal)
            logging.warning("finished no broken")

    ############################################################################
    def __init__(self, f=None,ch=None, *args, **kwargs):
        super(BrokenlinksSpider, self).__init__(*args, **kwargs)
        
        dispatcher.connect(self.my_close, signals.spider_closed)
        
        self.init_time=datetime.datetime.now()
        self.ch=ch
        
        # get the crawled pages from pickle file to retrieve external urls 
        if not f:
            #get file with last date
            last_file=commands.getstatusoutput("ls -lt |awk '{print $9;}' |grep '\d\d\d\d-\d\d-\d\d_'")[1].split('\n')[0]
            f=last_file[0:19]+"_pickled"
        self.f_outfile=f[0:19]+"_stats.txt"
        self.h_outfile=f[0:19]+"_stats.html"
        logging.warning(self.f_outfile)
        logging.warning(self.h_outfile)                
        data=pickle.load(open(f,'r'))
                
        self.picklefile=f
        self.data=data
        #l=set(reduce(operator.add,[it['LinksExternal'] for it in data['items']]))
        self.d={}
        for it in data['items']:
            for u in it['LinksExternal']:
                if u not in self.d.keys(): self.d[u]=[]
                self.d[u].append(it['Url'])
        self.start_urls = list(self.d.keys()) #add to the "to be crawled" list
    
        # bad anchors and links to files appended to file outputs
        BadAnchors=data['BadAnchors']
        LinksToFiles=data['LinksToFiles']
        ############################################################################################
        #                                                                                          #
        #                                    !!! CODE REMOVED !!!                                  #
        #                                                                                          #
        ############################################################################################
                
        fw=open(self.f_outfile,'a',1)
        fw1=open(self.h_outfile,'a',1)
        fw.write(stats_str_f.encode('ascii', 'ignore'))
        fw1.write('<html>'+stats_str_h.encode('ascii', 'ignore')+'</html>')
        fw.close(); fw1.close()


    
    ############################################################################
    # parse response for each external url 
    def parse(self, response):
        logging.warning(str(response.status)+" "+response.url)
        if(response.status!=200): 
            logging.warning("!!!!!!!!!")
            self.brokenLinksExternal[response.url]={'sts':str(response.status),'ref':'','redir':''}
            
            # look for referring pages
            if response.url in self.d.keys():
                yield {'line':"* "+str(response.status)+" "+response.url+"   On page(s):"+' '.join(self.d[response.url])}
                self.brokenLinksExternal[response.url]['ref']=' '.join(self.d[response.url])
            else:
                redir=''
                if 'redirect_urls' in response.request.meta.keys():
                    redir=response.request.meta['redirect_urls']
                ############################################################################################
                #                                                                                          #
                #                                    !!! CODE REMOVED !!!                                  #
                #                                                                                          #
                ############################################################################################
                    
                yield {'line':"* "+str(response.status)+" "+response.url+"   On page(s):"+pages} #+"   Redirect URLs: "+' '.join(redir)}
                self.brokenLinksExternal[response.url]['ref']=pages
                self.brokenLinksExternal[response.url]['redir']=' '.join(redir)
