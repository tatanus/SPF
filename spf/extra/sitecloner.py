import json
import sys
import urllib2
import re
import os
from HTMLParser import HTMLParser

class htmltagparser(HTMLParser):
    def __init__(self):
        self.reset()
        self.NEWATTRS = []
    def handle_starttag(self, tag, attrs):
        self.NEWATTRS = attrs
    def clean(self):
        self.NEWATTRS = []

class Cloner(object):
    def __init__(self, url, path, maxdepth=3):
        self.start_url = url
        self.path = os.getcwd() + "/" + path
        self.maxdepth = maxdepth
        self.seenurls = []
        self.user_agent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)"

    # ######################################3
    # Utility Functions
    # ######################################3
    
    # http get request
    def get_url(self, url):
        headers = { 'User-Agent' : self.user_agent }
        try:
            req = urllib2.Request(url, None, headers)
            return urllib2.urlopen(req).read()
        except urllib2.HTTPError, e:
            print 'We failed with error code - %s.' % e.code
            if e.code == 404:
                return ""
            else:
                return ""

    # download a binary file
    def download_binary(self, url):
        filename = ""
        if url.startswith(self.start_url):
            filename = url[len(self.start_url):]
        else:
            return
       
        data = self.get_url(url)
        if (data == ""):
            return
        self.write_outfile(data, filename)
        return

    # writeout a file
    def write_outfile(self, data, filename):
        if filename.startswith("/"):
            filename = filename[1:]
        
        fullfilename = self.path + "/" + filename
        if not os.path.exists(os.path.dirname(fullfilename)):
            os.makedirs(os.path.dirname(fullfilename))

        print "WRITING OUT FILE    [%s]" % (filename)

        f = open(fullfilename, 'a')
        f.write(data)
        f.close()        

    # unique a list
    def unique_list(self, old_list):
        new_list = []
        if old_list != []:
            for x in old_list:
                if x not in new_list:
                    new_list.append(x)
        return new_list

    # ######################################3
    # html and link processing functions
    # ######################################3

    def find_forms(self, html):
        form_regex = re.compile('<form[^>]+>')
        return self.unique_list(form_regex.findall(html))

    # convert all forms to contain hooks
    def process_forms(self, html, method="get", action="index"):
        # find all forms in page
        forms = self.find_forms(html)       

        parser = htmltagparser()
        # loop over each form
        for form in forms:

            print "FOUND A FORM        [%s]" % (form)
           
            # parse out parts of old form tag 
            parser.feed(form)
            attrs = parser.NEWATTRS
            parser.clean()
            
            # build new form
            new_form = "<form method=\"%s\" action=\"%s\"" % (method, action)
            for (name, value) in attrs:
                if ((name.lower() != "method") and (name.lower() != "action")):
                    new_form += " %s=\"%s\"" % (name, value)
            new_form += ">"

            print "REWROTE FORM TO BE  [%s]" % (new_form)

            # rewrite html with new form
            html = html.replace(form, new_form)
        return html

    # build new list of only the link types we are interested in
    def process_links(self, links):
        new_links = []
        for link in links:
            link = link.lower()
            if (link.endswith(".css")  or 
                link.endswith(".html") or
                link.endswith(".php")  or
                link.endswith(".asp")  or
                link.endswith(".aspx") or
                link.endswith(".js")   or
                link.endswith(".ico")  or
                link.endswith(".png")  or
                link.endswith(".jpg")  or
                link.endswith(".jpeg") or
                link.endswith(".bmp")  or
                link.endswith(".gif")
#                ("." not in os.path.basename(link))
               ):
                new_links.append(link)
        return new_links
    
    # primary recersive function used to clone and crawl the site
    def clone(self, depth=0, url="", base="", method="get", action="index"):
        # early out if max depth is reached
        if (depth > self.maxdepth):
            print "MAX URL DEPTH       [%s]" % (url)
            return

        # if no url is specified, then assume the starting url
        if (url == ""):
            url = self.start_url

        # if no base is specified, then assume the starting url
        if (base == ""):
            base = self.start_url

        # check to see if we have processed this url before
        if (url in self.seenurls):
            print "ALREADY SEEN URL    [%s]" % (url)
            return
        else:
            self.seenurls.append(url)

        # get the url and return if nothing was returned
        html = self.get_url(url)
        if (html == ""):
            return

        # determine the websites script/filename
        filename = ""
        # we are only interested in urls on the same site
        if url.startswith(base):
            filename = url[len(base):]

            # if filename is blank, assume index.html
            if (filename == ""):
                filename = "index.html"
        else:
            print "BAD URL             [%s]" % (url)
            return

        print "CLONING URL         [%s]" % (url)

        # find links
        links = re.findall(r"<link.*?\s*href=\"(.*?)\".*?>", html)
        links += re.findall(r"<script.*?\s*src=\"(.*?)\".*?>", html)
        links += re.findall(r"<img.*?\s*src=\"(.*?)\".*?>", html)
        links += re.findall(r"\"(.*?)\"", html)
        links += re.findall(r"url\(\"?(.*?)\"?\);", html)

        links = self.process_links(self.unique_list(links))

        # loop over the links
        for link in links:
            link = link.lower()
            new_link = link
            if link.startswith("http"):
                new_link = link
            elif link.startswith("//"):
                new_link = "http:" + link
            elif link.startswith("/"):
                new_link = base + link
            elif link.startswith("../"):
                new_link = base + "/" + link[3:]
            else:
                new_link = base + "/" + link

            good_link = new_link
            if (new_link.startswith(self.start_url)):
                good_link = new_link[len(self.start_url):]

            print "FOUND A NEW LINK    [%s]" % (new_link)
            print "FOUND A NEW LINK *  [%s]" % (good_link)
    
            # switch out new_link for link
            html = html.replace("\"" + link + "\"", "\"" + good_link + "\"")

            # determine is we need to call Clone recursively
            if (link.endswith(".css")  or
                link.endswith(".html") or
                link.endswith(".php")  or
                link.endswith(".asp")  or
                link.endswith(".aspx") or
                link.endswith(".js")
#                ("." not in os.path.basename(link))
               ):
                # recursively call process_html on each non-image link
                if base != self.start_url:
                    self.clone(url=new_link, base=os.path.dirname(url), depth=depth+1)
                else:
                    self.clone(url=new_link, depth=depth+1)
            else:
                # must be a binary file, so just download it
                self.download_binary(new_link)

        # update any forms within the page  
        html = self.process_forms(html, action=action)

        # write out the html for the page we have been processing
        self.write_outfile(html, filename)
        return

if __name__ == "__main__":
    def usage():
        print "%s <URL> <outdirectory> (optional <form action>)" % (sys.argv[0])

    if ((len(sys.argv) < 3) or (len(sys.argv) > 4)):
        usage()
        sys.exit(0)

    c = Cloner(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 4:
        c.clone(action=sys.argv[3])
    else:
        c.clone()
