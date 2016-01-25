# -*- coding: utf-8 -*-
#######################################################################################
#
# Analyzes data for all pages to generate statistics and format the report
#######################################################################################

import scrapy,logging,re,pdb,itertools,operator,datetime,bs4,commands,requests,os #,whois
from seo_spider.inputs import *

class SiteStats(object):
    def __init__(self):pass
    
    # average, min, max for a list 
    def getStatsForList(self,l):
        if len(l)==0:
            return ['0','0','0']
        avg_float=sum(l)/float(len(l))
        return [str(int(avg_float*1000)/1000.0),
                str(min(l)),
                str(max(l))]
    
    def getFreqMapForlist(self,l):
        freq={}
        for i in l:
            if i not in freq.keys():
                freq[i]=0
            freq[i]=freq[i]+1
        return sorted([(v,k) for (k,v) in freq.items()],reverse=True)
    
    # returns output for html
    def getHtml(self,stats_str):
        res=""
        i=0;wait=0
        for l in stats_str.split("\n"):
            l=re.sub("_____ ([^_]*) _____",r'<H2>\1</H2>',l)
            l=re.sub("\*\*\*\*\* ([^:]*):",r'<H3>\1</H3>',l)
            l=re.sub("<exp>",'<a href="javascript:Toggle('+str(i)+');">[View]</a><div class="ToggleTarget" id="ToggleTarget'+str(i)+'">',l)
            if re.search("</exp>",l):
                l=re.sub("</exp>","</div>",l)
                i+=1
            l=re.sub('(http[s]*://[^\s<>]*)',r'<a href="\1" target="_blank" rel="nofollow">\1</a>',l)
            res+=l+"<br/>"
        return res
    
    def linktree_rec(self,remaining,tree1,q,maxdepth):
        if not q:
            return maxdepth
        tree,lk,depth=q[0]
        q=q[1:]
        if lk not in tree1.keys(): lk=lk+'/'
        for l in tree1[lk]['LinksInternal']:
            if l.endswith('/'): l=l[:-1]
            if l in remaining:
                remaining.remove(l);
                tree[l]={}
                q.append((tree[l],l,depth+1))
        maxdepth=self.linktree_rec(remaining,tree1,q,depth)
        return max(depth,maxdepth)
    
    # returns a tree of links and maximum depth also
    def sitetree_str(self,tree,i,s):
        for k in tree.keys():
            s1="--"*i+str(i)+"-"+k
            s2=self.sitetree_str(tree[k],i+1,'')
            s+=s1+'\n'+s2
        return s
    
    ##########################################################
    
    # returns formatted text and html output for the statistics 
    def getPrettyStats(self,stats,brokenLinksInternal,BadAnchors,LinksToFiles,kwds,SiteData):
        stats_str="\n\n_____ Statistics for "+SiteData['StartUrl']+" _____\n"+str(SiteData['ItemsNum'])+" pages analyzed, elapsed time: "+(SiteData['ElapsedTime'] if 'ElapsedTime' in SiteData.keys() else '')+"\n\n"
        
        stats_str+="\n\n***** Warnings (more details for each page in the CSV report):\n"
        attrs={'Title':'Title','MetaDesc':'Meta Description','MetaCharset':'Meta Charset','Canonical':'Link rel="canonical"','Lang':'Language','Doctype':'Doctype'} #'MetaKwds':'Meta Keywords'
        for attr in attrs.keys():
            num=len(stats[attr+"NotDefined"])
            if num==0:
                stats_str+="\nGood. All pages have html "+attrs[attr]+" defined\n"
            else:
                if num>0 :
                    pagehas="page has"
                    if num>1: pagehas="pages have"
                    stats_str+="\n"+str(num)+" "+pagehas+" no html "+attrs[attr]+" defined\n"
                    stats_str+="<exp>"+u"\n".join(stats[attr+"NotDefined"]).encode('utf-8')+"</exp>"+"\n"
        
        attrs={'ResponseTime':'Response Time (seconds)','TitleLen':'Title Length','MetaDescLen':'Meta Description Length','PageSize':'Page Size (bytes)','PageTextPercentage':'Page Text Percentage','TablesNum':'Tables','TablesNestingLevel':'Nested Tables','H1Num':'Number of H1 tags','ExcessSpacesLen':'Excess Spaces Length','CSSFilesNum':'Number of CSS Files','JsFilesNum':'Number of JS Files','InlineStylesNum':'Number of Inline Styles','LinksNum':'Number of Links','ImgAltOrTitle':'Images without Alt or Title Attribute','ImgAltLen':'Images with Alt Attribute length','LinksTitle':'Links without Title Attribute'}
        for attr in attrs.keys():
            num=len(stats[attr+"NotGood"])
            if(optim[attr][0]==0 and optim[attr][1]==0):
                issue=attrs[attr]
            elif(optim[attr][0]==0):
                issue=attrs[attr]+" > "+str(optim[attr][1])
            elif(optim[attr][1]==9999):
                issue=attrs[attr]+" < "+str(optim[attr][0])
            else:
                issue=attrs[attr]+" not in range "+str(optim[attr])
            if num==0 :
                stats_str+="\nGood. No page has "+issue+"\n"
            if num>0 :
                page="page"
                if num>1: page+="s"
                stats_str+="\n"+str(num)+" "+page+" have "+issue+"\n"
                stats_str+="<exp>"+u"\n".join(stats[attr+"NotGood"]).encode('utf-8')+"</exp>"+"\n"
        
        stats_str+="\n<b>Facebook total shares + likes + comments:</b> "+str(stats['fb_total'])+"\n"
        stats_str+="\n<b>Total number of post comments:</b> "+str(stats['comments_total'])+"\n"
        
        a=['Favicon','GPublisher','GAuthor'] #'MetaRobots',
        for x in a:
            stats_str+="\n<b>"+x+":</b>\n"+u"\n".join([str(v)+" "+k for (v,k) in stats[x+"ByFreq"]]).encode('utf-8')+"\n"
        
        keys="AlexaRank Whois Sitemaps Theme Technologies DomainRedirection Emails UrlsWithQueryStrings UrlsWithUnderscores"
        for x in keys.split(" "): #SiteData.keys():
            if x in ['init_time','ItemsNum','StartUrl']: continue
            if type(SiteData[x])==list:
                stats_str+="\n<b>"+x+" - "+str(len(SiteData[x]))+":</b>\n"
                if not SiteData[x]:
                    stats_str+=" not found\n"
                else:
                    if len(SiteData[x])>10: stats_str+="<exp>"
                    for y in SiteData[x]:
                        stats_str+=str(y)+"\n"
                    if len(SiteData[x])>10: stats_str+="</exp>"
            elif type(SiteData[x])==dict:
                stats_str+="\n<b>"+x+" - "+str(len(SiteData[x]))+":</b>\n"
                if not SiteData[x]:
                    stats_str+=" not found\n"
                for y in SiteData[x].keys():
                    where=SiteData[x][y]
                    if type(where)==list and len(where)>3: #Emails..what pages
                        where=where[:3]+['...']
                    if x=="Technologies":
                        stats_str+=str(y)+"\n"
                    else:
                        stats_str+=str(y)+" -> "+str(where)+"\n"
            else:
                stats_str+="\n<b>"+x+":</b>\n"+(str(SiteData[x]) or "not found\n")+"\n"
        
        stats_str+="\n<b>Cloaked Links - "+str(len(SiteData["CloakedLinks"]))+":</b>\n"
        if not SiteData["CloakedLinks"]:
            stats_str+=" not found\n"
        else:
            stats_str+="<exp>"
            for b in SiteData["CloakedLinks"].keys():
                stats_str+="* "+b+"   On page(s): "+" ".join(SiteData["CloakedLinks"][b]['onpage'])+"\n"
            stats_str+="</exp>\n"
        
        stats_str+="\n<b>Feeds - "+str(len(SiteData["Feeds"]))+":</b>\n"
        if not SiteData["Feeds"]:
            stats_str+=" not found\n"
        else:
            stats_str+="<exp>"+"\n".join(SiteData["Feeds"])+"</exp>"+"\n"
        
        
        stats_str+="\n\n"
        a=['ResponseTime','PageSize','PageTextToHtmlRatio','PageTextPercentage','TitleLen','MetaDescLen','TablesNum','CSSFilesNum','JsFilesNum','InlineStylesNum']
        for x in a:
            stats_str+=x+": "+stats[x][0]+" (average), "+stats[x][1]+" (min), "+stats[x][2]+" (max)\n"
        
        for i in range(1,7):
            stats_str+="Number of H"+str(i)+" tags per page: "+stats['HNum'][i][0]+" (average), "+stats['HNum'][i][1]+" (min), "+stats['HNum'][i][2]+" (max)\n"
        for i in range(1,7):
            stats_str+="H"+str(i)+" length: "+stats['HLen'][i][0]+" (average), "+stats['HLen'][i][1]+" (min), "+stats['HLen'][i][2]+" (max)\n"
        
        stats_str+="\n\n***** Links statistics:\n"
        stats_str+="\nNumber of internal links per page: "+stats['LinksInternalNum'][0]+" (average), "+stats['LinksInternalNum'][1]+" (min), "+stats['LinksInternalNum'][2]+" (max)\n"
        stats_str+="\nNumber of external links per page: "+stats['LinksExternalNum'][0]+" (average), "+stats['LinksExternalNum'][1]+" (min), "+stats['LinksExternalNum'][2]+" (max)\n"
        stats_str+="\nNumber of links without 'title' attribute per page: "+stats['LinksWithoutTitleNum'][0]+" (average), "+stats['LinksWithoutTitleNum'][1]+" (min), "+stats['LinksWithoutTitleNum'][2]+" (max)\n"
        stats_str+="\nInternal link length: "+stats['LinksInternalLen'][0]+" (average), "+stats['LinksInternalLen'][1]+" (min), "+stats['LinksInternalLen'][2]+" (max)\n"
        stats_str+="\n\n***** Internal links by frequency - "+str(len(stats['LinksInternalByFreq']))+":\n"+"<exp>"+u"\n".join([str(v)+" "+k for (v,k) in stats['LinksInternalByFreq']]).encode('utf-8')+"</exp>"
        stats_str+="\n\n***** External links by frequency - "+str(len(stats['LinksExternalByFreq']))+":\n"+"<exp>"+u"\n".join([str(v)+" "+k for (v,k) in stats['LinksExternalByFreq']]).encode('utf-8')+"</exp>"
        stats_str+="\n\n***** Links in comments by frequency (most active commenters) - "+str(len(stats['LinksInCommentsByFreq']))+":\n"+"<exp>"+u"\n".join([str(v)+" "+k for (v,k) in stats['LinksInCommentsByFreq']]).encode('utf-8')+"</exp>"
        
        stats_str+="\n\n***** Broken internal links - "+str(len(brokenLinksInternal))+":\n"
        stats_str+="<exp>"
        for blink in brokenLinksInternal.keys():
            stats_str+="* "+blink+"\t Status: "+str(brokenLinksInternal[blink]['sts'])+"\t Referrers: "+u" ".join(brokenLinksInternal[blink]['ref']).encode('utf-8')+"\n"
        stats_str+="</exp>"
        
        # moved malformed anchors and links to files
        
        stats_str+="\n\n\n***** Images:\n"
        stats_str+="\nNumber of images per page: "+stats['ImgsNum'][0]+" (average), "+stats['ImgsNum'][1]+" (min), "+stats['ImgsNum'][2]+" (max)\n"
        stats_str+="\nNumber of images with 'alt' attribute per page: "+stats['ImgsAltNum'][0]+" (average), "+stats['ImgsAltNum'][1]+" (min), "+stats['ImgsAltNum'][2]+" (max)\n"
        stats_str+="\nNumber of images with 'title' attribute per page: "+stats['ImgsTitleNum'][0]+" (average), "+stats['ImgsTitleNum'][1]+" (min), "+stats['ImgsTitleNum'][2]+" (max)\n"
        stats_str+="\nImage 'alt' attribute length: "+stats['ImgsAltLen'][0]+" (average), "+stats['ImgsAltLen'][1]+" (min), "+stats['ImgsAltLen'][2]+" (max)\n"
        stats_str+="\nImage 'title' attribute length: "+stats['ImgsTitleLen'][0]+" (average), "+stats['ImgsTitleLen'][1]+" (min), "+stats['ImgsTitleLen'][2]+" (max)\n"
        
        stats_str+="\n\n***** PDFs found:\n<exp>"+u"\n".join(stats['PdfsAll']).encode('utf-8')+"</exp>\n"
        
        
        attrs=['Url','Title','MetaDesc','MetaKwds','H1','H2','H3','H4','H5','H6','ImgAlt','ImgTitle','ImgSrc','body']
        for url in kwds.keys():
            stats_str+="\n\n***** Keywords for url: "+url+"\n\n"
            for k in kwds[url].keys():
                stats_str+="\n\n***  "+k+"\n\n"
                for a in attrs:
                    if a in kwds[url][k].keys():
                        times=' times'
                        if kwds[url][k][a]['num']==1: times=' time'
                        stats_str+=a+": "+str(kwds[url][k][a]['num'])+times
                        if kwds[url][k][a]['pos']:
                            stats_str+=", in positions "+str(kwds[url][k][a]['pos'])
                        if 'tagnum' in kwds[url][k][a].keys() and kwds[url][k][a]['tagnum']:
                            stats_str+=", for "+a+" numbers "+str(kwds[url][k][a]['tagnum'])
                        stats_str+='\n'
        
        stats_str+="\n\n***** Site max depth - "+str(stats['maxdepth'])+":\n"
        stats_str+="<exp>"+str(stats['sitetree_str'])+"</exp>"
        
        stats_str+="\n\n***** Html Comments :\n"+"<exp>"+u"\n".join([str(v)+" "+k for (v,k) in stats['HtmlCommentsByFreq']]).encode('utf-8')+"</exp>"
        
        html_str=html_header+self.getHtml(stats_str)+html_footer
        stats_str=stats_str.replace("<exp>","").replace("</exp>","").replace("<b>","").replace("</b>","")
        return (stats_str,html_str)
    
    ##########################################################
    
    # calculates statistics for all pages (items)
    def getSiteStats(self,items):
        stats={} #SiteStats()
        stats['PdfsAll']=reduce(operator.add, [it['Pdfs'] for it in items] or [])
        
        for attr in ['ResponseTime','TitleLen','MetaDescLen','PageSize','PageTextToHtmlRatio','PageTextPercentage','TablesNum','CSSFilesNum','JsFilesNum','InlineStylesNum']:
            stats[attr]=self.getStatsForList([it[attr] for it in items if it[attr]])
        
        stats['HLen']={}
        stats['HNum']={}
        for i in range(1,7):
            mlist=[list(len(x) for x in it['H'+str(i)]) for it in items if it['H'+str(i)]] or [[]]
            stats['HLen'][i]=self.getStatsForList(reduce(operator.add,mlist))
            stats['HNum'][i]=self.getStatsForList([len(it['H'+str(i)]) for it in items if it['H'+str(i)]])
        
        
        mlist=[list(len(x) for x in it['LinksInternal']) for it in items if it['LinksInternal']] or [[]]
        stats['LinksInternalLen']=self.getStatsForList(reduce(operator.add,mlist))
        
        stats['LinksInternalNum']=self.getStatsForList([len(it['LinksInternal']) for it in items if it['LinksInternal']])
        stats['LinksExternalNum']=self.getStatsForList([len(it['LinksExternal']) for it in items if it['LinksExternal']])
        # cate linkuri au titlu pe pagina
        stats['LinksWithTitleNum']=self.getStatsForList([it['LinksWithTitleNum'] for it in items if it['LinksWithTitleNum']])
        stats['LinksWithoutTitleNum']=self.getStatsForList([it['LinksWithoutTitleNum'] for it in items if it['LinksWithoutTitleNum']])
        
        stats['ImgsNum']=self.getStatsForList([len(it['Imgs']) for it in items if it['Imgs']])
        # cate imagini au alt pentru fiecare pagina
        stats['ImgsAltNum']=self.getStatsForList([len([img['alt'] for img in it['Imgs'] if img['alt']]) for it in items if it['Imgs']])
        # ce lungimi au textele alt pt fiecare pagina
        mlist=[[len(img['alt']) for img in it['Imgs'] if img['alt']] for it in items if it['Imgs']] or [[]]
        stats['ImgsAltLen']=self.getStatsForList(reduce(operator.add,mlist))
        # cate titluri la imagini pt fiecare pag
        stats['ImgsTitleNum']=self.getStatsForList([len([img['title'] for img in it['Imgs'] if img['title']]) for it in items if it['Imgs']])
        # lungime titluri la imagini
        mlist=[[len(img['title']) for img in it['Imgs'] if img['title']] for it in items if it['Imgs']] or [[]]
        stats['ImgsTitleLen']=self.getStatsForList(reduce(operator.add,mlist))
        
        mlist=[it['LinksInternal'] for it in items if it['LinksInternal']] or [[]]
        stats['LinksInternalByFreq']=self.getFreqMapForlist(reduce(operator.add,mlist))
        mlist=[it['LinksExternal'] for it in items if it['LinksExternal']] or [[]]
        stats['LinksExternalByFreq']=self.getFreqMapForlist(reduce(operator.add,mlist))
        mlist=[it['LinksInComments'] for it in items if ('LinksInComments'in it.keys() and it['LinksInComments'])] or [[]]
        stats['LinksInCommentsByFreq']=self.getFreqMapForlist(reduce(operator.add,mlist))
        
        mlist=[it['HtmlComments'] for it in items if it['HtmlComments']] or [[]]
        stats['HtmlCommentsByFreq']=self.getFreqMapForlist(reduce(operator.add,mlist))
        mlist=[it['Favicon'] for it in items if it['Favicon']] or [[]]
        stats['FaviconByFreq']=self.getFreqMapForlist(reduce(operator.add,mlist))
        for attr in ['MetaRobots','GPublisher','GAuthor']:
            stats[attr+'ByFreq']=self.getFreqMapForlist([it[attr] for it in items if it[attr]])
        
        for attr in ['Title','MetaDesc','MetaKwds','MetaCharset','Canonical','Lang','Doctype']:
            stats[attr+"NotDefined"]=[it['Url'] for it in items if not it[attr]]
        for attr in ['ResponseTime','TitleLen','MetaDescLen','PageSize','PageTextPercentage','TablesNum','TablesNestingLevel','H1Num','ExcessSpacesLen','CSSFilesNum','JsFilesNum','InlineStylesNum']:
            stats[attr+"NotGood"]=[it['Url'] for it in items if (it[attr] and (it[attr]<optim[attr][0] or it[attr]>optim[attr][1]))]
        stats["LinksNumNotGood"]=[it['Url'] for it in items if (it['LinksExternalNum']+it['LinksInternalNum'] not in range(optim['LinksNum'][0],optim['LinksNum'][1]+1))]
        stats["ImgAltOrTitleNotGood"]=[it['Url'] for it in items if (it['ImgsWithoutAltOrTitleNum']>0)]
        stats["ImgAltLenNotGood"]=[it['Url'] for it in items if (len(['1' for img in it['Imgs'] if (len(img['alt'])<optim['ImgAltLen'][0] or len(img['alt'])>optim['ImgAltLen'][1])])>0)]
        stats["LinksTitleNotGood"]=[it['Url'] for it in items if (it['LinksWithoutTitleNum']>0)]
        
        # site tree +depth
        urls=[it['Url'] for it in items]
        remaining=[]
        for u in urls:
            if u.endswith('/'):
                remaining.append(u[:-1])
            else:
                remaining.append(u)
        lk=remaining[0]
        remaining=list(set(remaining))
        tree1={}
        for it in items: tree1[it['Url']]=it
        tree={lk:{}}
        remaining.remove(lk)
        stats['maxdepth']=self.linktree_rec(remaining,tree1,[(tree[lk],lk,0)],0)
        stats['sitetree_str']=self.sitetree_str(tree,0,'')
        
        stats['fb_total']=sum(int(it['FacebookTotalCount']) for it in items if it['FacebookTotalCount'])
        stats['comments_total']=sum(int(it['PostCommentsNum']) for it in items if it['PostCommentsNum'])
        #todo imgs with alt len not in range..
        
        return stats
