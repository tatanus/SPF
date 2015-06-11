import re
import string
import ConfigParser
import os
import os.path
import socket
import fcntl
import struct
import base64
import zlib
import json
import time
import subprocess
import urllib
import urllib2

class Utils():

    @staticmethod
    def compressDict(d):
        return base64.b64encode(zlib.compress(json.dumps(d),9))

    @staticmethod
    def decompressDict(s):
        return json.loads(zlib.decompress(base64.b64decode(s)))

    @staticmethod
    def to_unicode_str(obj, encoding='utf-8'):
        # checks if obj is a string and converts if not
        if not isinstance(obj, basestring):
            obj = str(obj)
        obj = Utils.to_unicode(obj, encoding)
        return obj

    @staticmethod
    def to_unicode(obj, encoding='utf-8'):
        # checks if obj is a unicode string and converts if not
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)
        return obj

    @staticmethod
    def is_writeable(filename):
        try:
            fp = open(filename, 'a')
            fp.close()
            return True
        except IOError:
            return False

    @staticmethod
    def is_readable(filename):
        try:
            fp = open(filename, 'r')
            fp.close()
            return True
        except IOError:
            return False

    @staticmethod
    def file_exists(filename):
        return os.path.isfile(filename)

    @staticmethod
    def get_random_str(length):
        return ''.join(random.choice(string.lowercase) for i in range(length))

    @staticmethod
    def htmlClean(text):
        if (not text):
            return text
        text = re.sub('<em>', '', text)
        text = re.sub('<b>', '', text)
        text = re.sub('</b>', '', text)
        text = re.sub('</em>', '', text)
        text = re.sub('%2f', ' ', text)
        text = re.sub('%3a', ' ', text)
        text = re.sub('<strong>', '', text)
        text = re.sub('</strong>', '', text)
        for e in ('>', ':', '=', '<', '/', '\\', ';', '&', '%3A', '%3D', '%3C'):
            text = string.replace(text, e, ' ')
        return text

    @staticmethod
    def unique_list(old_list):
        new_list = []
        if old_list != []:
            for x in old_list:
                if x not in new_list:
                    new_list.append(x)
        return new_list

    @staticmethod
    def load_config(filename):
        config = {}
        if Utils.is_readable(filename):
            parser = ConfigParser.SafeConfigParser()
            parser.read(filename)
            for section_name in parser.sections():
                for name, value in parser.items(section_name):
                    config[name] = value
        return config

    @staticmethod
    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

    @staticmethod
    def getIP():
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127."):
            interfaces = [ "eth0", "eth1", "eth2", "wlan0", "wlan1", "wifi0", "ath0", "ath1", "ppp0", ]
            for ifname in interfaces:
                try:
                    ip = Utils.get_interface_ip(ifname)
                    break
                except IOError:
                    pass
        return ip

    @staticmethod
    def screenCaptureWebSite(url, outfile):
        cmd = 'phantomjs --ssl-protocol=any --ignore-ssl-errors=yes libs/screencap.js "%s" "%s"' % (url, outfile)
        subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
