# -*- coding: utf-8 -*-
import scrapy,logging,re,pdb,itertools,operator,datetime,bs4,commands,requests,os #,whois
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from seo_spider.items import SeoSpiderItem
from seo_spider.siteStats import SiteStats
from seo_spider.inputs import *

# scrapy crawl SEO -L WARNING -a site=http://backlinko.com dir=/working/dir ch=pubnub_channel



#######################################################################################
#
# Main spider
#######################################################################################

class SeoSpider(scrapy.Spider):
    name = "SEO"
    start_urls = ['http://searchengineland.com']
    dir=os.getcwd()
    linksJoined={}
    bad_links=[]
    first_page=1
    
    items=[]
    brokenLinksInternal={} # url:[list of referrers]
    BadAnchors={}
    LinksToFiles={}
    SiteData={'Emails':{},'Sitemaps':[],'Technologies':{},'Warnings':[],'Theme':'','AlexaRank':'','UrlsWithUnderscores':[],'UrlsWithQueryStrings':[],'ItemsNum':0,'init_time':0,'StartUrl':'','DomainRedirection':{},'Whois':'','CloakedLinks':{},'Feeds':[],'ElapsedTime':''}

    def __init__(self, site=None,dir=None,ch=None, *args, **kwargs):
        super(SeoSpider, self).__init__(*args, **kwargs)
        self.init_time=datetime.datetime.now()
        if site:
            if not re.search(url_rex,site):
                raise CloseSpider('Invalid URL')
            self.start_urls = [site]
        if dir:
            self.dir=dir
        self.ch=ch
        self.dom='.'.join(self.start_urls[0].strip().split("/")[2].split('.')[-2:])
        if(self.start_urls[0].strip().split("/")[2].endswith(".co.uk") or self.start_urls[0].strip().split("/")[2].endswith(".com.au")):
            self.dom='.'.join(self.start_urls[0].strip().split("/")[2].split('.')[-3:])

        self.kwds={}
        if self.dom in kwds.keys():
            self.kwds=kwds[self.dom]
    

    ##########################################################

    # populate fields of a Scrapy Item (webpage) by parsing html with spath and regular expressions
    def fillSeoSpiderItem(self,response,item):

        for k in SeoSpiderItem.fields.keys(): item[k]=''
        item['Url']=response.url
        if "_" in response.url:
            self.SiteData['UrlsWithUnderscores'].append(response.url)
        if re.search("\?.*=",response.url):
            self.SiteData['UrlsWithQueryStrings'].append(response.url)
        item['ResponseTime']=response.meta['download_latency']
        m=re.search('<title>([^<>]*)</title>',response.body,re.I)
        if m:
            item['Title']=unicode(m.group(1),'utf-8') #28.12
            item['TitleLen']=len(item['Title'])
            
        m=re.search('<meta[^>]*[\'"]description[\'"][^>]*/>',response.body,re.I)
        if(m):
            m1=re.search('content=[\'"]([^\'"]*)[\'"]',m.group(0),re.I)
            if(m1):
                item['MetaDesc']=m1.group(1)
                item['MetaDescLen']=len(item['MetaDesc'])

        ############################################################################################
        #                                                                                          #
        #                                    !!! CODE REMOVED !!!                                  #
        #                                                                                          #
        ############################################################################################


        for l in response.xpath('//*[@id="comments"]//img'):
            alt=l.xpath("@alt").extract()
            title=l.xpath("@title").extract()
            src=l.xpath("@src").extract()
            it=[alt,title,src]
            if it in item['Imgs']:
                item['Imgs'].remove(it)
        item['Imgs']= [dict(zip(['alt','title','src'],it)) for it in item['Imgs']]
        item['Imgs']=[{'alt':''.join(it['alt']),'title':''.join(it['title']),'src':''.join(it['src'])} for it in item['Imgs']]

        item['ImgsNum']=len(item['Imgs'])
        item['ImgsWithAltOrTitle']=[it for it in item['Imgs'] if (it['alt'] or it['title'])]
        item['ImgsWithAltOrTitleNum']=len(item['ImgsWithAltOrTitle'])
        item['ImgsWithoutAltOrTitle']=[it for it in item['Imgs'] if not (it['alt'] and it['title'])]
        item['ImgsWithoutAltOrTitleNum']=len(item['ImgsWithoutAltOrTitle'])
                    
        paragraphs=[len(x.strip()) for x in response.xpath("//p/text()").extract()]
        if(len(paragraphs)>0):
            item['PLenMax']=max(paragraphs) 
        item['PNum']=len(re.findall("<p ", response.body,re.I)) # num of paragraphs
        
        #
        url=item['Url']
        if url not in self.kwds.keys():
            if url.endswith('/'): url=url[:-1]
            else: url=url+'/'
                
        if url in self.kwds.keys():
            tags=['Url','Title','MetaDesc','MetaKwds']
            for kwd in self.kwds[url].keys():
                for t in tags:
                    if item[t]:
                        self.kwds[url][kwd][t]={'pos':[],'num':0}
                        for m in re.finditer(kwd.replace(' ','\W'),item[t],re.I):
                            self.kwds[url][kwd][t]['pos'].append(m.start(0))
                            self.kwds[url][kwd][t]['num']+=1
                for i in range(1,7):
                    t='H'+str(i)
                    if item[t]:
                        self.kwds[url][kwd][t]={'pos':[],'num':0,'tagnum':[]}
                        for j in range(0,len(item[t])):
                            for m in re.finditer(kwd.replace(' ','\W'),item[t][j],re.I):
                                self.kwds[url][kwd][t]['pos'].append(m.start(0))
                                self.kwds[url][kwd][t]['num']+=1
                                self.kwds[url][kwd][t]['tagnum'].append(j+1)
                
                ############################################################################################
                #                                                                                          #
                #                                    !!! CODE REMOVED !!!                                  #
                #                                                                                          #
                ############################################################################################
            
                # whole body
                self.kwds[url][kwd]['body']={'pos':[],'num':0}
                for m in re.finditer(kwd.replace(' ','\W'),body_text_only,re.I):
                    self.kwds[url][kwd]['body']['pos'].append(m.start(0))
                    self.kwds[url][kwd]['body']['num']+=1
                
                            
        for m in re.finditer(mail_rex,response.body,re.I):
            if m.group(1) not in self.SiteData['Emails'].keys():
                self.SiteData['Emails'][m.group(1)]=[]
            if response.url not in self.SiteData['Emails'][m.group(1)]:
                self.SiteData['Emails'][m.group(1)].append(response.url)
    
        for patt in tech.keys():
            if re.search(patt,response.body):
                if tech[patt] not in self.SiteData['Technologies'].keys():
                    self.SiteData['Technologies'][tech[patt]]=[]
                self.SiteData['Technologies'][tech[patt]].append(response.url)

        comml=[len(response.xpath('//ol[re:test(@class,"comment[-]*list")]/li')),
               len(response.xpath('//ol[@itemtype="http://schema.org/UserComments"]/li')),
               len(response.xpath('//section[re:test(@class,"commentlist")]/div')),
               ]
        item['PostCommentsNum']=max(comml)

        item['Pdfs']=[]
        item['LinksExternal']=[]
        item['LinksInternal']=[]
        item['LinksInComments']=[]
        item['LinksAndTitleAttr']=[]
        item['LinksNoFollowNotInComm']=[]
        item['BadAnchors']=[]
        item['LinksToFiles']=[]
    
        return item
    
    ##########################################################
    
    def parseSitemapRobots(self,response):
        if(response.status!=200):
            logging.error(response.url+" error getting robots")
            return
        m=re.search("sitemap:(.*?)\n",response.body,re.I)
        if m:
            self.SiteData['Sitemaps'].append(m.group(1).strip())


    ##########################################################
    
    def parseSitemap(self,response):
        if(response.status!=200):
            logging.error(response.url+" error getting sitemap")
            return
        self.SiteData['Sitemaps'].append(response.url)
        for wd in ['Yoast SEO','google-sitemap-pro']:
            if wd in response.body:
                if wd not in self.SiteData['Technologies'].keys():
                    self.SiteData['Technologies'][wd]=[]
                self.SiteData['Technologies'][wd].append(response.url)
    
    
    ##########################################################
    
    def parseAlexaRank(self,response):
        if(response.status!=200):
            logging.error(response.url+" error getting Alexa Rank")
            return
        bsobj=bs4.BeautifulSoup(response.body, "xml")
        if bsobj.find("POPULARITY"):
            self.SiteData['AlexaRank']+="Global Rank: "+bsobj.find("POPULARITY")['TEXT']+"; "
        if bsobj.find("REACH"):        
            self.SiteData['AlexaRank']+="Reach: "+bsobj.find("REACH")['RANK']+"; "
        if bsobj.find("COUNTRY"): # and ('RANK' in bsobj.find("COUNTRY").keys()):
            self.SiteData['AlexaRank']+="Rank in "+bsobj.find("COUNTRY")['NAME']+": "+bsobj.find("COUNTRY")['RANK']

    ##########################################################

    def parsePlugin(self,response):
        if(response.status!=200):
            logging.error(response.url+" error plugin")
            return
        if response.request.url in plugin_urls.keys():
            url_part='/'.join(response.request.url.split('/')[3:])
            wd=plugin_urls[url_part]
            if wd not in self.SiteData['Technologies'].keys():
                self.SiteData['Technologies'][wd]=[]
            self.SiteData['Technologies'][wd].append(response.request.url)

    ##########################################################

    def parseTheme(self,response):
        if(response.status!=200):
            logging.error(response.url+" error getting theme css")
            return
        for attr in ["Theme Name","Theme URI","Description","Author","Author URI","Version","Template"]:
            m=re.search(attr+":(.*?)\n",response.body,re.I)
            if m:
                self.SiteData['Theme']+=m.group(0)

    ##########################################################
    
    #does not work because of duplicate filter
    def parseDomainRedir(self,response):
        if(response.status!=200):
            logging.error(response.url+" error parseDomainRedir")
        self.SiteData['DomainRedirection'][response.request.url]=[response.url,response.status]

    ##########################################################

    def parseFacebookStats(self,response):
        if(response.status!=200):
            logging.error(response.url+" error parseFacebookStats")
        else:
            bsobj=bs4.BeautifulSoup(response.body, "xml")
            item=self.items[response.meta['itemNum']]
            for x in "share_count like_count comment_count click_count commentsbox_count".split(' '):
                if bsobj.find(x):
                    item["FacebookStats"]+=x+": "+bsobj.find(x).contents[0]+"; "
            item["FacebookTotalCount"]+=bsobj.find('total_count').contents[0]
        
        yield self.items[response.meta['itemNum']]
    
    ##########################################################

    def parse(self, response):
        logging.warning(response.url)
        
        referrer=response.request.headers.get('Referer', None)

        # eg "http://b.backlinko.com" -> backlinko.com
        p_domain='.'.join(response.url.strip().split("/")[2].split('.')[-2:])
        if(response.url.strip().split("/")[2].endswith(".co.uk") or response.url.strip().split("/")[2].endswith(".com.au")):
            p_domain='.'.join(response.url.strip().split("/")[2].split('.')[-3:])

        # cloaked links ..
        if self.dom!=p_domain:
            logging.warning("__ referrer: "+response.request.headers.get('Referer', None))
            if response.url in self.SiteData['CloakedLinks'].keys():
                if referrer not in self.SiteData['CloakedLinks'][response.url]['onpage']:
                    self.SiteData['CloakedLinks'][response.url]['onpage'].append(referrer)
            else:
                self.SiteData['CloakedLinks'][response.url]={'onpage':[referrer]}
            return
                    
        # broken link?
        if(response.status!=200):
            if response.url in self.linksJoined.keys():
                self.bad_links.append(self.linksJoined[response.url])
            if response.url in self.brokenLinksInternal.keys():
                if referrer not in self.brokenLinksInternal[response.url]['ref'] and referrer!=None:
                    self.brokenLinksInternal[response.url]['ref'].append(referrer)
            else:
                self.brokenLinksInternal[response.url]={'ref':[referrer],'sts':response.status}
            return

        # other types of documents 
        if 'pdf' in response.headers['Content-Type']:
            if response.url in self.LinksToFiles.keys():
                if referrer not in self.LinksToFiles[response.url]['onpage']:
                    self.LinksToFiles[response.url]['onpage'].append(referrer)
            else:
                self.LinksToFiles[response.url]={'onpage':[referrer]}
            # nu-l mai adaug la itemul respectiv..
            logging.warning("__ Content-Type pdf")
            return
                
        if 'text/xml' in response.headers['Content-Type']:
            if 'X-Type' in response.headers.keys():
                if response.headers['X-Type']=='feed':
                    self.SiteData['Feeds'].append(response.url)
            logging.warning("__ Content-Type xml")
            return


        if self.first_page:
            self.first_page=0
            self.SiteData['StartUrl']=self.start_urls[0]
            self.SiteData['init_time']=self.init_time
            # find plugins in src
            ############################################################################################
            #                                                                                          #
            #                                    !!! CODE REMOVED !!!                                  #
            #                                                                                          #
            ############################################################################################
    
            # whois
            self.SiteData['Whois']=commands.getstatusoutput(whois_cmds[0]+p_domain+whois_cmds[1])[1]
            # make sure to crawl pages from keywords
            for url in self.kwds.keys():
                yield scrapy.Request(url)
            # plugins 
            for url_part in plugin_urls.keys():
                yield scrapy.Request("http://"+p_domain+"/"+url_part, callback=self.parsePlugin,priority=-1)
        
        item=SeoSpiderItem()
        self.fillSeoSpiderItem(response,item)


                    
        ############################################################################################
        #                                                                                          #
        #                                    !!! CODE REMOVED !!!                                  #
        #                                                                                          #
        ############################################################################################

        item['LinksAndTitleAttr']= [dict(zip(['href','title'],it)) for it in item['LinksAndTitleAttr']]
        item['LinksAndTitleAttr']=[{'href':''.join(it['href']),'title':''.join(it['title'])} for it in item['LinksAndTitleAttr'] if it['href']]
        links=[it['href'] for it in item['LinksAndTitleAttr']] # all links...we need to filter these later
        item['LinksWithTitleNum']=len([1 for it in item['LinksAndTitleAttr'] if it['title']])
        item['LinksWithoutTitleNum']=len(item['LinksAndTitleAttr'])-item['LinksWithTitleNum']
        
                
        # no follow links
        links_nof=response.xpath("//a[contains(@rel,'nofollow')]/@href").extract()
        comm_links_nof=response.xpath('//*[@id="comments"]//a[contains(@rel,"nofollow")]/@href').extract()
        for l in comm_links_nof:
            if l in links_nof: links_nof.remove(l)
        
        item['LinksNoFollowNotInComm']=links_nof
        item['LinksNoFollowNum']=len(links_nof)+len(comm_links_nof)
                
        for href in links:
            # find malformed
            ############################################################################################
            #                                                                                          #
            #                                    !!! CODE REMOVED !!!                                  #
            #                                                                                          #
            ############################################################################################
            
            # not http
            if not url.startswith('http'):
                # file:
                item['BadAnchors'].append(href)
                if href in self.BadAnchors.keys():
                    if response.url not in self.BadAnchors[href]['onpage']:
                        self.BadAnchors[href]['onpage'].append(response.url)
                else:
                    self.BadAnchors[href]={'onpage':[response.url]}
                continue
            
            skip=0
    
            # files
            for ext in file_ext:
                if url.lower().endswith(ext.lower()) or ext.lower()+"?" in url.lower().split('/')[-1]:
                    item['LinksToFiles'].append(url)
                    if url in self.LinksToFiles.keys():
                        if response.url not in self.LinksToFiles[url]['onpage']:
                            self.LinksToFiles[url]['onpage'].append(response.url)
                    else:
                        self.LinksToFiles[url]={'onpage':[response.url]}
                    skip=1
                    
            if skip: continue

            # start parsing the 'real' urls and follow them
            
            u_domain='.'.join(url.strip().split("/")[2].split('.')[-2:])
            if(url.strip().split("/")[2].endswith(".co.uk") or url.strip().split("/")[2].endswith(".com.au")):
                u_domain='.'.join(url.strip().split("/")[2].split('.')[-3:])
            
            # if this url domain eq parent domain -> internal; else ->external

            ############################################################################################
            #                                                                                          #
            #                                    !!! CODE REMOVED !!!                                  #
            #                                                                                          #
            ############################################################################################

        
        item['LinksExternalNum']=len(item['LinksExternal'])
        item['LinksInternalNum']=len(item['LinksInternal'])
                
        self.items.append(item)

        req=scrapy.Request(fb_stats_url_part+item['Url'],callback=self.parseFacebookStats)
        req.meta['itemNum']=self.SiteData['ItemsNum']
        yield req

        self.SiteData['ItemsNum']+=1


