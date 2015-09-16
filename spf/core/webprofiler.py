import sys
import os
import re
import string
import urllib2
import ssl
import socket

class indicator():
    def __init__(self):
        self.causes = []
        self.score = 0
        self.causesdict = {"body" : 1,
                           "title" : 2,
                           "url" : 4,
                           "cookies" : 8,
                           "headers" : 8}

    def addcause(self, cause):
        try:
            self.score += self.causesdict[cause]
            self.causes.append(cause)
        except KeyError:
            print "ERROR: Unknown cause [%s]" % (cause)

    def getscore(self):
        return self.score

    def getcauses(self):
        return self.causes

class profiler(urllib2.HTTPRedirectHandler):
    def __init__(self):
        self.indicatordict = dict()
        self.indicatormatchlist = dict()
        self.suffixes = list()

        self.load_indicators()
        self.loadSuffixes()

        self.indent_n = 0

        self.debug = False

    def indent(self):
        if (self.indent_n == 0):
            return ''
        return (' ' * ((self.indent_n * 2) - 2)) + "-> "

    def extractTitle(self, html):
        start = html.find("<title>")
        if start > -1:
            start = start + 7
            end = html.find("</title>")
            title = html[start:end]
            title = title.strip()
        else:
            title = ""
        return(title)

    def load_indicators(self):
        script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
        fn = script_dir + "indicators.txt"
        with open(fn,'r') as inf:
            for line in inf:
                t, f, m = line.strip().split('\t')

                l = None
                if (t in self.indicatormatchlist.keys()):
                    l = self.indicatormatchlist[t]
                else:
                    l = []
                l.append([f.strip(), m.strip()])
                self.indicatormatchlist[t] = l

    def loadSuffixes(self):
        self.suffixes.append("/owa")

    def http_error_302(self, req, fp, code, msg, headers):
        self.checkindicators(url=req.get_full_url(), headers=headers)
        if (self.debug):
            self.indent_n += 1
            print "%s[REDIRECT] = [../%s]" % (self.indent(), headers['Location'])
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

    def updateindicator(self, key, value):
        i = None
        if (key in self.indicatordict.keys()):
            i = self.indicatordict[key]
        else:
            i = indicator()
        i.addcause(value)
        self.indicatordict[key] = i
        
    def checkindicators(self, url="", headers="", body="", cookies=[]):
        self.indent_n += 1
        url = str(url).lower()
        headers = str(headers).lower()
        body = str(body).lower()
        cookies = str(cookies).lower()
        if (self.debug):
            print "%sBEGIN URL  = [%s]" % (self.indent(), url)
            print "----------------------------------"
            print "URL = [%s]" % (url)
            print "HEADERS = [%s]" % (headers)
            print "COOKIES = [%s]" % (cookies)
            print "----------------------------------"
  
        for k, v in self.indicatormatchlist.iteritems():
            for l in v:
                field = url
                if (l[0] == "headers"):
                    field = headers
                elif (l[0] == "cookies"):
                    field = cookies
                elif (l[0] == "body"):
                    field = body
                elif (l[0] == "title"):
                    field = self.extractTitle(body)

                if (re.search(l[1].lower(), field)):
                    if (self.debug):
                        self.indent_n += 1
                        print "%sFOUND    = [%s] in the [ %s ]" % (self.indent(), l[1].lower(), l[0])
                        self.indent_n -= 1
                    self.updateindicator(k.lower(), l[0])
        if (self.debug):
            print "%sEND URL    = [%s]" % (self.indent(), url)
            self.indent_n -= 1

    def run(self, url, debug=False):
        self.debug = debug

        if (self.debug):
            print self.indent()
            print "%sSTART URL  = [%s]" % (self.indent(), url)

        opener = urllib2.build_opener(self)
        urllib2.install_opener(opener)
        try:
            response = urllib2.urlopen(url)
            if (response):
                cookies = []
                if ('Set-Cookie' in response.info()):
                    cookies = response.info()['Set-Cookie']
                self.checkindicators(url=response.geturl(), headers=response.info(), body=response.read(), cookies=cookies)
                if (self.debug):
                    self.indent_n = 0
                    print "%sSTOP URL   = [%s]" % (self.indent(), response.geturl())

#        for suffix in self.suffixes:
#            temp_url = url + suffix
#            print "TRYING URL = [%s]" % (temp_url)
#            response = urllib2.urlopen(temp_url)
#            self.checkindicators(url=response.geturl(), headers=response.info(), body=response.read())
#            print "STOP URL   = [%s]" % (response.geturl())
        except urllib2.HTTPError as e:
            if (self.debug):
                print "%sHTTPError: %s" %(self.indent(), str(e))
        except urllib2.URLError as e:
            if (self.debug):
                print "%sURLERROR: %s" %(self.indent(), str(e))
        except ssl.SSLError as e:
            if (self.debug):
                print "%sSSLERROR: %s" %(self.indent(), str(e))
        except socket.timeout as e:
            if (self.debug):
                print "%sSocket.Timeout: %s" %(self.indent(), str(e))
        except socket.error as e:
            if (self.debug):
                print "%sSocket.Error: %s" %(self.indent(), str(e))
        except:
            print "%sUnexpectedError: %s" %(self.indent(), sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            pass

        # display results
        if (self.indicatordict):
            if (debug):
                print
            for key, value in self.indicatordict.iteritems():
                if (self.debug):
                    print "%sMATCHED    = [%s, %i, %s]" % (self.indent(), key, value.getscore(), value.getcauses())
        return self.indicatordict.items()

    def hasLogin(self, url, debug=False):
        self.debug = debug
        try:
            response = urllib2.urlopen(url)
            if (response):
                body = response.read()
                m = re.search("(<\s*form.*)", body, re.IGNORECASE|re.DOTALL)
                if m:
                    m2 = re.search("(pass|login|user)", m.group(1), re.IGNORECASE)
                    if (m2):
                        return True
        except urllib2.HTTPError as e:
            if (self.debug):
                print "%sHTTPError: %s" %(self.indent(), str(e))
        except urllib2.URLError as e:
            if (self.debug):
                print "%sURLERROR: %s" %(self.indent(), str(e))
        except ssl.SSLError as e:
            if (self.debug):
                print "%sSSLERROR: %s" %(self.indent(), str(e))
        except socket.timeout as e:
            if (self.debug):
                print "%sSocket.Timeout: %s" %(self.indent(), str(e))
        except socket.error as e:
            if (self.debug):
                print "%sSocket.Error: %s" %(self.indent(), str(e))
        except:
            print "%sUnexpectedError: %s" %(self.indent(), sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            pass

        return False

if __name__ == "__main__":
    p = profiler()
    p.run(sys.argv[1], debug=True)
