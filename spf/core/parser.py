import re
import urllib

from core.utils import Utils

class Parser():
    def __init__(self, text, domain):
        self.text = text
        self.domain = domain

    def hosts(self):
        if (not self.text):
            return []
        reg_hosts = re.compile('[a-zA-Z0-9\.\-]*\.' + self.domain)
        return Utils.unique_list(reg_hosts.findall(urllib.unquote_plus(self.text)))
 
    def emails(self):
        if (not self.text):
            return []
        reg_emails = re.compile('[a-zA-Z0-9\.\-_]+@[a-zA-Z0-9\.\-]*' + self.domain)
        return Utils.unique_list(reg_emails.findall(Utils.htmlClean(self.text)))
