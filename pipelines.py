# -*- coding: utf-8 -*-
import csv,datetime,os,logging,pprint,pickle,re,pdb,sys,json,urllib
from spiders.SEO import SiteStats
from seo_spider.inputs import publish_key,subscribe_key
sys.path.append("/Volumes/hdd1/x/_py/python-master")

#in settings.py: ITEM_PIPELINES = {   'myproject.pipelines.PricePipeline': 300,...}


def _callback(message):
    print(message)


class WriteCsvFastPipeline(object):
	def __init__(self):
		self.fw=''; self.fw1=''
		self.first=1
		self.ind=0
		self.js={'pages':[]}
    
    def init_pubnub():
        from pubnub import Pubnub
        self.pubnub = Pubnub(publish_key, subscribe_key)

	#########################################################################
	def init_BrokenLinks(self,spider):
		if spider.ch:
            self.init_pubnub()

	#########################################################################
	def init_SEO(self,spider):
		self.now=datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d_%H-%M-%S")
		self.pickle_fname=os.path.join(spider.dir,self.now+"_pickled")
		fname=os.path.join(spider.dir,self.now+"_"+spider.dom+"_pages.csv")
		self.csvfile=open(fname,'wb',1) # flush per line
		self.fw=csv.writer(self.csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		self.SiteStats=SiteStats()
		if spider.ch:
            self.init_pubnub()


	#########################################################################
	def stringify(self, obj,objname):
		ret=''
		if objname=='LinksAndTitleAttr':
			ret='\n'.join([u'; '.join([l['title']+' (title)', l['href']+' (href)']).encode('utf-8') for l in obj])

		elif objname=='Imgs' or objname=='ImgsWithAltOrTitle' or objname=='ImgsWithoutAltOrTitle':
			ret='\n'.join([u'; '.join([img['alt']+' (alt)', img['title']+' (title)', img['src']+' (src)']).encode('utf-8') for img in obj])
		elif type(obj) == list:
			ret=u''
			for x in obj:
				if isinstance(x,str): ret+=unicode(x,'UTF-8')+u"\n"
				if isinstance(x,unicode): ret+=x+u"\n"
			ret=ret.encode('utf-8')
		elif type(obj) == float or type(obj)==int:
			ret=str(obj)
		else:
            		if isinstance(obj, unicode):
               			ret=obj.encode('utf-8')
            		else:
              		 	ret=obj # like 'insights on what\xe2\x80\x99s the most suitable'
		return ret
			

	#########################################################################
	def process_item(self, item, spider):
		if(spider.name=='SEO'):
			self.process_item_SEO(item,spider)
		if(spider.name=='BrokenLinks'):
			self.process_item_BrokenLinks(item,spider)

	#########################################################################
	def process_item_BrokenLinks(self, item, spider):
		if self.first==1: 
			self.init_BrokenLinks(spider)
			self.fw=open(spider.f_outfile,'a',1)
			self.fw1=open(spider.h_outfile,'a',1)
			self.first=0
			self.fw1.write('<html>') #+spider.stats_str_h)
			self.fw.write("\n\n***** Broken External Links:\n\n")
			self.fw1.write("<br/><br/><H3>Broken External Links</H3><br/>"+'<a href="javascript:Toggle('+str(999)+');">[View]</a><div class="ToggleTarget" id="ToggleTarget'+str(999)+'">')
		self.fw.write(item['line']+"\n")
		l=re.sub('(http[s]*://[^\s<>]*)',r'<a href="\1" target="_blank" rel="nofollow">\1</a>',item['line'])
		self.fw1.write(l+"<br/>")

	#########################################################################
	def process_item_SEO(self, item, spider):
		if self.first==1: 
			self.init_SEO(spider)
			self.hdr=spider.fields
			self.fw.writerow(self.hdr)
			self.first=0
		self.fw.writerow([self.stringify(item[x],x) for x in self.hdr])

		with open(self.pickle_fname,'w',1) as f:
			pickle.dump({'items':spider.items,'brokenLinksInternal':spider.brokenLinksInternal,'BadAnchors':spider. BadAnchors,'LinksToFiles':spider.LinksToFiles,'kwds':spider.kwds,'SiteData':spider.SiteData},f)
			f.close()
		if spider.ch:
			self.send_to_channel(spider.ch,"pgs",item.__dict__['_values'])
			self.js['pages'].append(item.__dict__['_values'])
		self.ind+=1
		return item

	#########################################################################
	def send_to_channel(self,ch,name,obj):
        ############################################################################################
        #                                                                                          #
        #                                    !!! CODE REMOVED !!!                                  #
        #                                                                                          #
        ############################################################################################

	#########################################################################
	def close_spider(self, spider):
		if(spider.name=='SEO'):
			self.close_spider_SEO(spider)
		if(spider.name=='BrokenLinks'):
			self.close_spider_BrokenLinks(spider)

	#########################################################################
	def close_spider_BrokenLinks(self, spider):
		if self.fw: 
			self.fw.close()
		if self.fw1: 
			self.fw1.write("Total: "+str(len(spider.brokenLinksExternal))+"<br/></div></html>")
			self.fw1.close()
		with open(spider.picklefile,'w') as f:
			pickle.dump({'items':spider.data['items'],'brokenLinksInternal':spider.data['brokenLinksInternal'],'BadAnchors':spider.data['BadAnchors'],'LinksToFiles':spider.data['LinksToFiles'],'kwds':spider.data['kwds'],'SiteData':spider.data['SiteData'],'brokenLinksExternal':spider.brokenLinksExternal},f)
			f.close()
		if spider.ch and not self.first:
			self.send_to_channel(spider.ch,"ble", spider.brokenLinksExternal)
			logging.warning("finished")


	#########################################################################
	def close_spider_SEO(self, spider):
		f_stats=os.path.join(spider.dir,self.now+"_stats.txt")
		h_stats=os.path.join(spider.dir,self.now+"_stats.html")
		logging.warning("closingg: \n"+"scrapy crawl BrokenLinks -L WARNING -a f="+self.now+'_pickled\nsay -v Bells "dong dong dong"\n')
		spider.SiteData['fin_time']=datetime.datetime.now()
                t=str(spider.SiteData['fin_time']-spider.SiteData['init_time']).split('.')[0].split(':')
		spider.SiteData['ElapsedTime']=t[0]+"h "+t[1]+"m "+t[2]+"s "
		# one more dump (with end and elapsed time time)
		with open(self.pickle_fname,'w',1) as f:
			pickle.dump({'items':spider.items,'brokenLinksInternal':spider.brokenLinksInternal,'BadAnchors':spider. BadAnchors,'LinksToFiles':spider.LinksToFiles,'kwds':spider.kwds,'SiteData':spider.SiteData},f)
			f.close()

		sts= self.SiteStats.getSiteStats(spider.items)
		str_stats,html_stats=self.SiteStats.getPrettyStats(sts,spider.brokenLinksInternal,spider.BadAnchors,spider.LinksToFiles,spider.kwds,spider.SiteData)
		
		if spider.ch:
			self.send_to_channel(spider.ch,"bli", spider.brokenLinksInternal)
			self.send_to_channel(spider.ch,"ban", spider.BadAnchors)
			self.send_to_channel(spider.ch,"ltf", spider.LinksToFiles)
			self.send_to_channel(spider.ch,"kwd", spider.kwds)
			self.send_to_channel(spider.ch,"sts", sts)

			spider.SiteData['init_time']=datetime.datetime.strftime(spider.SiteData['init_time'],"%Y/%m/%d %H:%M:%S")
			spider.SiteData['fin_time']=datetime.datetime.strftime(spider.SiteData['fin_time'],"%Y/%m/%d %H:%M:%S")
			self.send_to_channel(spider.ch,"sda", spider.SiteData)

			self.js['bli']= spider.brokenLinksInternal
			self.js['ban']= spider.BadAnchors
			self.js['ltf']= spider.LinksToFiles
			self.js['kwd']= spider.kwds
			self.js['sts']= sts
			self.js['sda']= spider.SiteData
			with open(self.pickle_fname+"_json",'w',1) as f:	
				pickle.dump(self.js,f)
				f.close()

		with open(f_stats,'w',1) as f:
			f.write(str_stats) 
			f.close()
		with open(h_stats,'w',1) as f:
			f.write(html_stats) 
			f.close()
		self.csvfile.close()

