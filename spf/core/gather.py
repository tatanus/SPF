import re
import urllib2

from core.parser import Parser
from core.display import Display, ProgressBar

class Gather():
    def __init__(self, domain, display=None):
        self.domain = domain
        self.display = display
        self.results = ""
        self.user_agent = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)"
        self.p = ProgressBar(display=self.display)
        self.gather()
        self.parser = Parser(self.results, self.domain)

    def hosts(self):
        return self.parser.hosts()

    def emails(self):
        return self.parser.emails()

    @staticmethod
    def get_sources():
        return "Currently searching [google, bing, ask, dogpile, yandex, baidu, yahoo, duckduckgo]"

    def search(self, url, offset=1, maxoffset=0, title=""):
        current_offset = 0
        data = ""
        self.p.reset(title=title)
        while current_offset <= maxoffset:
            self.p.rotate()
            temp_url = re.sub(r'\[\[OFFSET\]\]', str(current_offset), url)
            try:
                headers = { 'User-Agent' : self.user_agent }
                req = urllib2.Request(temp_url, None, headers)
                data += urllib2.urlopen(req).read()
            except urllib2.URLError as e:
                self.display.error("Could not access [%s]" % (title))
                return data
            except Exception as e:
                print e
            current_offset += offset
        self.p.done()
        return data
    
    def gather(self, maxoffset=500):
        self.results += self.search(title="Google",     url="http://www.google.com/search?num=100&start=[[OFFSET]]&hl=en&meta=&q=%40\"" + self.domain + "\"", offset=100, maxoffset=maxoffset)
        self.results += self.search(title="Bing",       url="http://www.bing.com/search?q=%40" + self.domain + "&count=50&first=[[OFFSET]]", offset=50, maxoffset=maxoffset)
        self.results += self.search(title="Ask",        url="http://www.ask.com/web?q=%40" + self.domain + "&pu=100&page=[[OFFSET]]", offset=100, maxoffset=maxoffset)
        self.results += self.search(title="Dogpile",    url="http://www.dogpile.com/search/web?qsi=[[OFFSET]]&q=\"%40" + self.domain + "\"", offset=10, maxoffset=maxoffset/10)
        self.results += self.search(title="Yandex",     url="http://www.yandex.com/search?text=%40" + self.domain + "&numdoc=50&lr=[[OFFSET]]", offset=50, maxoffset=maxoffset)
        self.results += self.search(title="Baidu",      url="http://www.baidu.com/s?wd=%40" + self.domain + "&pn=[[OFFSET]]", offset=10, maxoffset=maxoffset/10)
        self.results += self.search(title="Yahoo",      url="https://search.yahoo.com/search?p=\"%40" + self.domain + "\"&b=[[OFFSET]]&pz=10", offset=10, maxoffset=maxoffset/10)
        self.results += self.search(title="DuckDuckGo", url="https://duckduckgo.com/lite?q=\"%40" + self.domain + "\"" )
