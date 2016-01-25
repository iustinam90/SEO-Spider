# SEO-Spider
Scraper that evaluates tens of SEO factors for any website

! Important:  The code here is for presentation purposes only. I removed ~ 1600 lines of code and files too 

<h2>Detailed list of features and analyzed data</h2>
<h4>HTML elements:</h4>
<ul>
<li>Page size &#8211; recommended to be less than 300KB</li>
<li><span style="line-height: 1.5;">Page text percentage and text/html ratio &#8211; checks if page text size is between 20-50% and text/html ratio 25-70%</span></li>
<li><em>Title</em> tag &#8211; check if defined for each page and its length; per page and site statistics
<ul>
<li><span style="line-height: 1.5;">all pages should have a title tag and </span><span style="line-height: 1.5;">the length should be between 10 and 70 characters</span></li>
</ul>
</li>
<li><em>H1-&gt;H6</em> tags &#8211; number, length and list &#8211; per page and site statistics
<ul>
<li><span style="line-height: 1.5;">there shouldn&#8217;t be more than one <em>H1</em>tag per page</span></li>
<li><span style="line-height: 1.5;">shows how much you use subheadings to break text into smaller blocks</span></li>
</ul>
</li>
<li><span style="line-height: 1.5;">Tables &#8211; number and nesting level &#8211; it is advisable not to use tables, unless absolutely necessary</span></li>
<li><span style="line-height: 1.5;">Paragraphs number and their length &#8211; per page and site statistics</span>
<ul>
<li><span style="line-height: 1.5;">large blocks of text should be broken in paragraphs for easy reading</span></li>
</ul>
</li>
<li>Html header tags:
<ul>
<li><span style="line-height: 1.5;"><em>meta description</em> &#8211; check if defined for each page and its length; per page and site statistics</span></li>
<li><span style="line-height: 1.5;"><em>meta keywords, meta robots, meta charset, language, doctype, canonical link</em> &#8211; check if defined for each page</span></li>
<li><span style="line-height: 1.5;">favicon, Google authorship, Google publisher</span></li>
</ul>
</li>
<li>Excess spaces length &#8211; these are spaces in the html code that can be removed to decrease page size</li>
<li><span style="line-height: 1.5;">Html comments length &#8211; these can also be removed to decrease page size</span></li>
<li>CSS and JS files, inline styles &#8211; number per page and site statistics : the fewer, the better</li>
</ul>
<h4>Links :</h4>
<ul>
<li>Pages that have the most internal backlinks &#8211; internal SEO: your most important pages are the ones which have the most links pointing to them</li>
<li>Site maximum depth &#8211; how far away your pages are from the home page; the fewer levels, the better; a flat structure is desirable</li>
<li>Internal and external links list &#8211; per page ; checks if number of links exceeds 100</li>
<li>Links that have title attribute defined &#8211; number per page and website statistics ; they do make a difference for SEO</li>
<li>Broken internal and external links &#8211; these should be fixed;<br />
includes bad anchors &#8211; a common issue found during analysis of multiple websites is to find links like &#8220;http:/..&#8221; (there should be 2 slashes)</li>
<li><em>No follow</em> links &#8211; too many do-follow external links can affect page rank</li>
<li>Urls with underscores &#8211; underscore is not considered a separator so it&#8217;s better to replace them with hyphens</li>
<li>Urls with query strings &#8211; better use URL rewriting to improve usability and search friendliness of your site<br />
eg<em> &#8216;http://www.mysite.com/myproductdetails.php?id=7&#8217; -&gt; &#8216;http://www.mysite.com/products/7/&#8217;</em></li>
<li>Cloaked links</li>
<li>Links from comments &#8211; If you&#8217;re curious what websites your most active fans own</li>
<li>Feeds</li>
<li>Links to files &#8211; PDFs, Excel and Word docs, images, etc &#8211; you might want to remove links pointing to images</li>
</ul>
<h4>Images:</h4>
<p>Checks if <em>alt </em>and <em>title</em> attributes are defined and their number; per page and website statistics. Image alt attribute should be less than 150 characters.</p>
<h4>Social engagement:</h4>
<ul>
<li>Facebook shares, likes and comments + total</li>
<li><span style="line-height: 1.5;">Blog comments &#8211; per page and website total</span></li>
</ul>
<h4>Website information:</h4>
<ul>
<li>Response time &#8211; defines the overall site speed and identifies slow pages</li>
<li><span style="line-height: 1.5;">Whois data &#8211; creation, update and expiration dates, registrant name and contact info, registrar, name servers. Domain registration length and domain privacy are ranking factors.</span></li>
<li><span style="line-height: 1.5;">Domain redirection &#8211; google sees <em>&#8216;http://www.[domain]&#8217;</em> and <em>&#8216;http://[domain]&#8217;</em> as 2 separate sites; you should configure redirection from non-preferred domain to the preferred one (most commonly &#8216;<em>http://[domain]&#8217;</em>)</span></li>
<li><span style="line-height: 1.5;">Alexa ranks</span></li>
<li><span style="line-height: 1.5;">Theme &#8211; identifies website theme</span></li>
<li><span style="line-height: 1.5;">Sitemaps</span></li>
<li><span style="line-height: 1.5;">Emails</span></li>
<li>Plugins, services and technologies your (competitor) website is using</li>
</ul>
<h4>Keyword usage:</h4>
<p><span style="line-height: 1.5;">Identifies whether the keyword is present, in which position (better at the beginning) and how many times in each of the html elements:<em> </em></span><em><span style="line-height: 1.5;">url, title, meta description, H1-&gt;H6 tags, body, image filename, title and alt attributes.</span></em></p>

