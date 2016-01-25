# -*- coding: utf-8 -*-

import re
#######################################################################################
#
# inputs used by spider and items such as regular expressions, constant values, etc
#######################################################################################

# pubnub auth
publish_key="<your publish_key here>"
subscribe_key="<your subscribe_key here>"

url_rex = re.compile(r'^https?://' # http:// or https://
                     r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))' #domain...
                     r'(?:/?|[/?]\S+)$', re.IGNORECASE)

mail_rex="[^A-Z0-9]([A-Z0-9][A-Z0-9._%+-]{0,63}(@|\s*[\ ##### removed code ####### *dot\s*[\]}\(]\s*)){1,8}[A-Z]{2,63})[^A-Z0-9]"

alexa_site="http://data.alexa.com/data?cli=10&dat=s&url="

fields=['Url','ResponseTime','Title','TitleLen','MetaDesc','MetaDescLen','MetaKwds','MetaCharset','Canonical','Lang','Doctype','PageSize','PageTextToHtmlRatio','PageTextPercentage','ExcessSpacesLen','HtmlCommentsLen','HtmlComments','TablesNum','TablesNestingLevel','H1','H1Num','H2','H2Num','H3','H3Num','H4','H4Num','H5','H5Num','H6','H6Num','CSSFilesNum','JsFilesNum','InlineStylesNum','PNum','PLenMax','Pdfs','LinksExternal','LinksExternalNum','LinksInternal','LinksInternalNum','LinksAndTitleAttr','LinksWithoutTitleNum','LinksNoFollowNotInComm','LinksNoFollowNum','LinksInComments','ImgsWithoutAltOrTitle','Imgs','ImgsWithoutAltOrTitleNum','ImgsNum','BadAnchors','LinksToFiles','FacebookStats','FacebookTotalCount','PostCommentsNum'] #'WordCount',

optim={'TitleLen':[10,55],'MetaDescLen':[70,160],'PageTextToHtmlRatio':[25,70],'PageSize':[0,300000],'LinksNum':[0,100],'PageCodeToTextRatio':[25,70],'PageTextPercentage':[20,50],'ResponseTime':[0,2],'TablesNum':[0,0],'TablesNestingLevel':[0,0],'ExcessSpacesLen':[0,50],'H1Num':[0,1],'CSSFilesNum':[0,7],'JsFilesNum':[0,7],'InlineStylesNum':[0,7],'ImgAltOrTitle':[0,0],'ImgAltLen':[0,150],'LinksTitle':[0,0]}

file_ext=[".jpg",".jpeg",".png",".bmp",".gif",".xls",".zip",".ods",".docx",".doc",".pptx",".ppt",".xlsx",".mp4",".avi",".flv",".mp3",".txt",".psd",".svg","m4a",".php"]


fb_stats_url_part="http://api.facebook.com/restserver.php?method=links.getStats&urls="

whois_cmds=['whois ',' |grep -i "^Update Date:\|^Creation Date:\|^Registrar Registration Expiration Date:\|^Registrar:\|^Registrant Name:\|^Registrant Organization:\|^Registrant Country:\|^Registrant Email:\|^Name Server:"']


bad_urls="""
mailto:
?replytocom=
#
.jpg
.png
.pdf
"""


tech={
'Performance optimized by WP Rocket':'WP Rocket (wp-rocket.me)',
'contact-form-7-css': 'Contact Form 7', 'contact-form-7': 'Contact Form 7',
'This site is optimized with the Yoast SEO': 'Yoast SEO',
'This site uses the Google Analytics by Yoast plugin': 'Google Analytics by Yoast',
'google-analytics.com/analytics.js': 'Google Analytics',
'google-analytics.com/ga.js': 'Google Analytics',
"<script [^>]* src=['\"][^'\"]*cdn\.optimizely\.com":'Optimizely',
'This site converts visitors into subscribers and customers with the OptinMonster WordPress plugin':'Optin Monster','optin-monster':'Optin Monster',
'<!-- AWeber Web Form Generator':'Aweber',
'\*\*\* COPY PROTECTED BY http://chetangole.com/blog/wp-copyprotect/':'WP Copy Protect',
"<link [^>]*? href=['\"][^'\"]*?fonts\.googleapis\.com/css":'Google Font API'
}

plugin_urls={
'wp-content/plugins/platinum-seo-pack/readme.txt':'Platinum SEO',
'wp-content/plugins/plugin-central/readme.txt':'Plugin Central',
'wp-content/plugins/contact-form-7/languages/readme.txt':'Contact Form 7',
'wp-content/plugins/jetpack/readme.txt':'JetPack',
'wp-content/plugins/tablepress/readme.txt':'TablePress',
'wp-content/plugins/tinymce-advanced/readme.txt':'TinyMCE Advanced',
'wp-content/plugins/wordfence/readme.txt':'Wordfence',
'wp-content/plugins/wp-copyprotect/readme.txt':'WP Copy Protect',
'wp-content/plugins/wp-mobile-detect/readme.txt':'WP Mobile Detect',
'wp-content/plugins/wp-mobile-edition/readme.txt':'WP Mobile Edition',
'wp-content/plugins/wp-super-cache/readme.txt':'WP Super Cache',
'wp-content/plugins/wordpress-seo/readme.txt':'Yoast SEO',
'wp-content/plugins/mainwp-child/readme.txt':'Mainwp Child',
'wp-content/plugins/mainwp/readme.txt':'Mainwp Dashboard',
'wp-content/plugins/gravity-forms-placeholders/readme.txt':'Gravity Forms Placeholders',
'wp-content/plugins/sitelinks-search-box/readme.txt':'Sitelinks Search Box',
}

kwds={
}

html_header="""
<html>
<head>
<title>Statistics</title>

<style type="text/css">
.ToggleTarget {
display: none;
}
a:link, a:visited{
color: #0B7D79;
text-decoration: none;
}
a:hover, a:active{
color: #0EB3AE
}
</style>

<script type="text/javascript">
function Toggle(id) {
var el = document.getElementById("ToggleTarget"+id);
if (el.style.display == "block") {
el.style.display = "none";
}
else {
el.style.display = "block";
}
}
</script>
</head>

<body>
"""

html_footer="""
</body>
</html>
"""
