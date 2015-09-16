#!/usr/bin/env python

import sys
import time
import os
import re
import glob

from core.utils import Utils

class ReportGenException(Exception):
    pass

class ReportGen():
    def __init__(self, directory):
        self.directory = directory
        self.config = {}
        self.load_config()
        self.filename = "report-%s.html" % (time.strftime("%Y_%m_%d_%H_%M_%S"))

        self.WEBLOGS_FILENAME = self.directory + "logs/*.log"

        self.campaigns = {}

    def load_config(self):
        filename = self.directory + "logs/INFO.txt"
        if not Utils.is_readable(filename):
            raise ReportGenException("Filename: [%s] is NOT readable." % (filename))

        a=open(filename,'rb')
        lines = a.readlines()
        for line in lines:
            parts = line.split("=")
            if (parts[0] == "STARTTIME"):
                self.config["start_ts"] = parts[1]
            if (parts[0] == "ENDTIME"):
                self.config["end_ts"] = parts[1]
            if (parts[0] == "TARGETDOMAIN"):
                self.config["domain"] = parts[1]
            if (parts[0] == "PHISHINGDOMAIN"):
                self.config["phishing_domain"] = parts[1]

    def start(self):
        self.print_file("<html>")
        self.print_file("<style>")
        self.print_file("html, body {")
        self.print_file("    margin-left: auto;")
        self.print_file("    margin-right: auto;")
        self.print_file("    width: 75%;")
        self.print_file("    padding: 0;")
        self.print_file("    background-color: white;")
        self.print_file("}")
        self.print_file("#images{")
        self.print_file("    text-align:center;")
        self.print_file("    margin:50px auto;")
        self.print_file("}")
        self.print_file("#images img{")
        self.print_file("    margin:0px 20px;")
        self.print_file("    border:3px solid;")
        self.print_file("    display:inline-block;")
        self.print_file("    text-decoration:none;")
        self.print_file("    color:black;")
        self.print_file("}")
        self.print_file("#textblock{")
        self.print_file("    border:3px solid;")
        self.print_file("    background-color: grey;")
        self.print_file("    word-wrap: break-word;")
        self.print_file("    -ms-word-break: break-all;")
        self.print_file("    word-break: break-all;")
        self.print_file("    -webkit-hyphens: auto;")
        self.print_file("    -moz-hyphens: auto;")
        self.print_file("    hyphens: auto;")
        self.print_file("}")
        self.print_file("</style>")

        self.print_file("<body>")
        self.print_file("     <h1>Report for Phishing Exercise against [%s]</h1>" % (self.config["domain"]))
        self.print_file("     <br>")
        self.print_file("     <br>")
        self.print_file("     The phishing engagement was started on [%s] and ran through [%s]." % (self.config["start_ts"], self.config["end_ts"]))
        self.print_file("     <br>")
        self.print_file("     <br>")
        if (self.config["phishing_domain"] != ""):
            self.print_file("     For this exercise, the domain [%s] was registered and used for the phishing attacks." % (self.config["phishing_domain"]))
        self.print_file("     <br>")
        self.print_file("     <br>")
        self.process_campaigns()
        self.print_file("</body>")
        self.print_file("</html>")
        return self.filename

    def process_campaigns(self):
        # identify all campaigns
        weblogs = self.find_files(self.WEBLOGS_FILENAME)
        # loop over each campaign, calling self.process_campaign(campaign) on each
        for log in weblogs:
            campaign = log[:-4]
            campaign = re.sub('^' + self.directory + "logs/" , '', campaign)
            self.process_campaign(campaign)

            self.print_campaign(campaign)
        return

    def process_campaign(self, campaign):
        self.campaigns[campaign] = {}
        # load screenshot
        self.campaigns[campaign]["screenshots"] = []
        self.campaigns[campaign]["screenshots"].append(self.directory + "screenshots/" + campaign + "." + self.config["phishing_domain"] + ".png")
        files = self.find_files(self.directory + "screenshots/" + Utils.getIP() + ":*_" + campaign + ".png")
        if (files):
            self.campaigns[campaign]["screenshots"].append(files[0])

        # load email template and email targets
        self.process_email_template(campaign)

        # load phishing statistics
        self.process_statistics(campaign)
        return

    def process_email_template(self, campaign):
        if (Utils.is_readable(self.directory + "email_template_" + campaign  +".txt")):
            data = ""
            with open (self.directory + "email_template_" + campaign  +".txt" , "r") as myfile:
                data = myfile.read()
            parts = data.split("----------------------------------------------")
            self.campaigns[campaign]["email_template"] = parts[1].strip()
            parts = parts[2].split("--------")
            emails = parts[1].strip().splitlines()
            self.campaigns[campaign]["email_targets"] = emails
        return

    def process_statistics(self, campaign):
        self.campaigns[campaign]["stats"] = {}
        if ("email_targets" in self.campaigns[campaign]):
            self.campaigns[campaign]["stats"]["emails_sent"] = len(self.campaigns[campaign]["email_targets"])
        else:
            self.campaigns[campaign]["stats"]["emails_sent"] = 0
        self.campaigns[campaign]["stats"]["website_access"] = self.grep_file(self.directory + "logs/" + campaign + ".log", "[ACCESS]")
        self.campaigns[campaign]["stats"]["credentials"] = self.grep_file(self.directory + "logs/" + campaign + ".log", "[CREDENTIALS]")

        return

    def print_campaign(self, campaign):
        self.print_file("<hr>")
        self.print_file("<br>")
        self.print_file("<h2> Phishing Campaign : %s </h2>" % (campaign))
        self.print_file("<br>")
        self.print_file("<h3>")
        self.print_file("SAMPLE EMAIL:")
        self.print_file("</h3>")
        self.print_file("<div id=\"textblock\">")
        self.print_file("<pre>")
        if ("email_template" not in self.campaigns[campaign]):
            self.print_file("No emails were sent using this email template.")
            self.print_file("</pre>")
            self.print_file("</div>")
        else:
            self.print_file(self.campaigns[campaign]["email_template"])
            self.print_file("</pre>")
            self.print_file("</div>")
            self.print_file("<br>")
            self.print_file("<h3>")
            self.print_file("TARGET EMAIL ADDRESS(es):")
            self.print_file("</h3>")
            self.print_file("<div id=\"textblock\">")
            self.print_file("<pre>")
            for e in self.campaigns[campaign]["email_targets"]:
                self.print_file(e + "<br>")
            self.print_file("</pre>")
            self.print_file("</div>")
        self.print_file("<br>")
        self.print_file("<h3>")
        self.print_file("PHISHING WEBSITE(s)")
        self.print_file("</h3>")
        self.print_file("<div id=\"images\">")
        for s in self.campaigns[campaign]["screenshots"]:
            s = re.sub('^' + self.directory + "screenshots/", '', s)
            self.print_file("<img src=\"%s\" width=\"500px\" height=\"500px\" />" % (s))
            caption = s[:-4]
            caption = re.sub("_" + campaign + "$", '', caption)
            caption = re.sub("_", ':', caption)
            self.print_file("<div class=\"caption\">http://%s</div>" % (caption))
            self.print_file("<br>")
        self.print_file("</div>")
        self.print_file("<br>")
        self.print_file("<h3>")
        self.print_file("CAPTURED CREDENTIALS:")
        self.print_file("</h3>")
        self.print_file("<div id=\"textblock\">")
        self.print_file("<pre>")
        for c in self.campaigns[campaign]["stats"]["credentials"]:
            self.print_file(c)
        self.print_file("</pre>")
        self.print_file("</div>")
        self.print_file("<br>")
        self.print_file("<h3>")
        self.print_file("PHISHING STATISTICS")
        self.print_file("</h3>")
        self.print_file("<table>")
        self.print_file("<tr><td># of emails sent</td><td>%s</td></tr>" % (self.campaigns[campaign]["stats"]["emails_sent"]))
        self.print_file("<tr><td># of access to web site</td><td>%s</td></tr>" % (len(self.campaigns[campaign]["stats"]["website_access"])-2))
        self.print_file("<tr><td># of credentials collected</td><td>%s</td></tr>" % (len(self.campaigns[campaign]["stats"]["credentials"])))
        self.print_file("</table>")

    def grep_file(self, filename, match):
        matches = []
        for line in open(filename):
            if match in line:
                matches.append(line.strip())
        return matches

    def find_files(self, filemask):
        return glob.glob(filemask)

    def print_file(self, line):
        fullfilename = self.directory + "reports/" + self.filename
        
        if not os.path.exists(os.path.dirname(fullfilename)):
            os.makedirs(os.path.dirname(fullfilename))

        if not Utils.is_writeable(fullfilename):
            raise ReportGenException("Filename: [%s] is NOT writeable." % (fullfilename))

        fp = open(fullfilename, "a")
        fp.write(line)
        fp.close()

        return

if __name__ == "__main__":
    def usage():
        print "report.py <report directory>"

    if len(sys.argv) != 2:
        usage()
        exit(0)

    if Utils.is_readable(sys.argv[1] + "logs/INFO.txt"):
        try:
            print ReportGen(sys.argv[1]).start()
        except ReportGenException as e:
            print e
    else:
        print "[" + sys.argv[1] + "] does not appear to be a valid report directory."
