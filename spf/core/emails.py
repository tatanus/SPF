#!/usr/bin/env python

import re
import urllib2
import smtplib
import dns.resolver
import dns.reversename
import socket

from core.utils import Utils

MX_RECORD_CACHE = {}

# Attempt to validate that the system can actually communicate with the target MX server
def validate_mx(server, domain):
    try:
        if server in MX_RECORD_CACHE:
            return MX_RECORD_CACHE[server]
        smtp = smtplib.SMTP(timeout=10)
        smtp.connect(server)
        status, _ = smtp.helo()
        if status != 250:
            smtp.quit()
            print "%s answer: %s - %s" % (server, status, _)
        smtp.mail('')
        status, _ = smtp.rcpt("invalid@"+domain)
        if status == 250:
            smtp.quit()
            MX_RECORD_CACHE[server] = True
            return True
        print "%s answer: %s - %s" % (server, status, _)
        smtp.quit()
    except smtplib.SMTPServerDisconnected as e:  # Server not permits verify user
        print "%s disconnected. [%s]" % (server, e)
    except smtplib.SMTPConnectError as e:
        print "Unable to connect to %s. [%s]" % (server, e)
    except socket.timeout as e:
        print "Timedout connecting to %s. [%s]" % (server, e)
    MX_RECORD_CACHE[server] = False
    return False        

# Lookup a domain and get its mailserver
def get_mx_records(domain):
    records = dns.resolver.query(domain, 'MX')
    hosts = []
    for rdata in records:
        if (validate_mx((str(rdata.exchange))[:-1], domain)):
            hosts.append((str(rdata.exchange))[:-1])
    return hosts
    
# Lookup a domain and get its mailserver
def get_mx_record(domain):
    hosts = get_mx_records(domain)
    if (hosts):
        return hosts[0]
    else:
        return None

# attempt to validate an address by connecting to the remote SMTP
def validate_email_address(email_to, email_from, debug=False):
    # find the appropiate mail server
    domain = email_to.split('@')[1]
    remote_server = get_mx_record(domain)

    if (remote_server == None):
        print "No valid email server could be found for [%s]!" % (email_to)
        return False

    # Login into the mail exchange server
    try:
        smtp = smtplib.SMTP()
        smtp.connect(remote_server)
        if debug:
            smtp.set_debuglevel(True)
    except smtplib.SMTPConnectError, e:
        print e
        return False
 
    try:
        smtp.ehlo_or_helo_if_needed()
    except Exception, e:
        print e
        return False
 
    # First Try to verify with VRFY
    # 250 is success code. 400 or greater is error.
    v_code, v_message = smtp.verify(email_to)
    if v_code and v_code != 250:
        f_code, f_message = smtp.mail(email_from)
        # Then use RCPT to verify
        if f_code and f_code == 250:
            r_code, r_message = smtp.rcpt(email_to)
            if r_code and r_code == 250:
                return True, r_message
            if r_code and r_code == 550:
                return False, r_message
        else:
            return False
    else:
        return True, v_message

    smtp.quit()
    return False

def send_email_direct(email_to, email_from, subject, body, debug=False):
    # find the appropiate mail server
    domain = email_to.split('@')[1]
    remote_server = get_mx_record(domain)
    if (remote_server == None):
        print "No valid email server could be found for [%s]!" % (email_to)
        return

    # connect to remote mail server and forward message on 
    server = smtplib.SMTP(remote_server, 25)
    message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (email_from, email_to, subject, body)

    smtp_sendmail_return = ""
    if debug:
        server.set_debuglevel(True)
    try:
        smtp_sendmail_return = server.sendmail(email_from, email_to, message)
    except Exception, e:
        exception = 'SMTP Exception:\n' + str( e) + '\n' + str( smtp_sendmail_return)
    finally:
        server.quit()

def send_email_account(remote_server, remote_port, username, password, email_to, email_from, subject, body, debug=False):
    if (remote_server == "smtp.gmail.com"):
        send_email_gmail(username, password, email_to, email_from, subject, body, debug)
    else:
        # connect to remote mail server and forward message on 
        server = smtplib.SMTP(remote_server, remote_port)
        message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (email_from, email_to, subject, body)

        smtp_sendmail_return = ""
        if debug:
            server.set_debuglevel(True)
        try:
            server.login(username, password)
            smtp_sendmail_return = server.sendmail(email_from, email_to, message)
        except Exception, e:
            exception = 'SMTP Exception:\n' + str( e) + '\n' + str( smtp_sendmail_return)
        finally:
            server.quit()

def send_email_gmail(username, password, email_to, email_from, subject, body, debug=False):
    # connect to remote mail server and forward message on 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (email_from, email_to, subject, body)

    smtp_sendmail_return = ""
    if debug:
        server.set_debuglevel(True)
    try:
        server.ehlo()
        server.starttls()
        server.login(username,password)
        smtp_sendmail_return = server.sendmail(email_from, email_to, message)
    except Exception, e:
        exception = 'SMTP Exception:\n' + str( e) + '\n' + str( smtp_sendmail_return)
    finally:
        server.quit()

class EmailTemplate():
    def __init__(self, TYPE, SUBJECT, BODY):
        self.TYPE = TYPE
        self.SUBJECT = SUBJECT
        self.BODY = BODY

    def getTYPE(self):
        return self.TYPE

    def getSUBJECT(self):
        return self.SUBJECT

    def getBODY(self):
        return self.BODY

    def __str__(self):
        return "TYPE = [%s]\nSUBJECT = [%s]\nBODY = \n%s" % (self.TYPE, self.SUBJECT, self.BODY)

if __name__ == "__main__":
    #print get_mx_record("knowledgecg.com")
    #print get_mx_record("rapid7.com")
    #print get_mx_record("gmail.com")
    #print get_mx_record("knowledgecg.com")
    #print get_mx_record("rapid7.com")
    #print get_mx_record("gmail.com")
    #print validate_email_address("adam.compton@knowledgecg.com", "adam.compton@gmail.com", debug=False)
    #print validate_email_address("adam.compt@knowledgecg.com", "adam.compton@gmail.com", debug=False)
    print "hi"
