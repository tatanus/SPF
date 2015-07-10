import subprocess
import os
import re
import sys
import urlparse

class SiteCloner():
    def __init__(self, clone_dir="web_clones/"):
        self.clone_dir = clone_dir

    def fixForms(self, html, method="POST", action="index"):
        html = re.sub("<\s*form[^>]+>", "<form method=\"%s\" action=\"%s\">" % (method, action), html)
        return html
    
    def writeConfig(self, tdir, url):
        of = open("%sCONFIG" % tdir, "w")
        url = urlparse.urlparse(url)
        vhost = url.hostname.split('.')[0]
        of.write("VHOST=%s\n" % vhost)
        of.write("LOGFILE=%s.log\n" % vhost)
        of.write("REDIRECTURL=error\n")
        of.close()
    
    def cloneUrl(self, url):
        # break URL apart into component parts 
        url_details = urlparse.urlparse(url)
        path = os.path.split(url_details.path)[0]
        hostname = url_details.hostname
    
        ## make dir if needed
        if not os.path.isdir(self.clone_dir):
            os.makedirs(self.clone_dir)
    
        try:
            # check if we have wget
            if os.path.isfile("/usr/local/bin/wget") or os.path.isfile("/usr/bin/wget") or os.path.isfile("/usr/local/wget"):
                #use WGET to clone the index and supporting files
                subprocess.Popen('cd %s;timeout -s KILL 60 wget --no-check-certificate -e robots=off -O INDEX -c "%s";' % (self.clone_dir, url), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).wait()
                subprocess.Popen('cd %s;timeout -s KILL 60 wget --no-check-certificate -e robots=off -c -p -k "%s";' % (self.clone_dir, url), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).wait()
    
                # fix the <form> tag in INDEX to work with SPF
                html = ""
                with open ("%sINDEX" % self.clone_dir, "r") as myfile:
                    html=myfile.read()
                myfile.close()
                # correct/fix any forms 
                html = self.fixForms(html)
                # write the file back out
                of = open("%sINDEX" % self.clone_dir, "w")
                of.write(html)
                of.close()
    
                # move INDEX to proper directory
                os.rename("%sINDEX" % self.clone_dir, "%s%s/%s/INDEX" % (self.clone_dir, hostname, path))
    
                # create a proper CONFIG file
                self.writeConfig("%s%s%s/" % (self.clone_dir, hostname, path), url)
    
                return "%s%s%s/" % (self.clone_dir, hostname, path)
    
            else:
                print "WGET WAS NOT FOUND"
        except TypeError as e:
           print e
        except NameError as e:
           print e
        except:
           print sys.exc_info()[0] 
    
        return None

if __name__ == "__main__":
    s = SiteCloner()
    print s.cloneUrl("http://www.safelogin.co")
    #print s.cloneUrl("https://204.131.222.4/+CSCOE+/logon.html?fcadbadd=1")

