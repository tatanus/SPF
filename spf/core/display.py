import re
import string
import ConfigParser
import os
import sys
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

from core.utils import Utils

class Colors(object):
    N = '\033[m' # native
    R = '\033[31m' # red
    G = '\033[32m' # green
    O = '\033[33m' # orange
    B = '\033[34m' # blue

class ProgressBar():
    def __init__(self, end=100, width=10, title="", display=None):
        self.end = end
        self.width = width
        self.title = title
        self.display = display
        self.progress = float(0)
        self.bar_format = '[%(fill)s>%(blank)s] %(progress)s%% - %(title)s'
        self.rotate_format = '[Processing: %(mark)s] %(title)s'
        self.markers='|/-\\'
        self.curmark = -1
        self.completed = False
        self.reset()

    def reset(self, end=None, width=None, title=""):
        self.progress = float(0)
        self.completed = False
        if( end):
            self.end = end
        if (width):
            self.width = width
        self.curmark = -1
        self.title = title

    def inc(self, num=1):
        if (not self.completed):
            self.progress += num

            cur_width = (self.progress / self.end) * self.width
            fill = int(cur_width) * "-"
            blank = (self.width - int(cur_width)) * " "
            percentage = int((self.progress / self.end) * 100)

            if (self.display):
                self.display.verbose(self.bar_format % {'title': self.title, 'fill': fill, 'blank': blank, 'progress': percentage}, rewrite=True, end="", flush=True)
            else:
                sys.stdout.write('\r' + self.bar_format % {'title': self.title, 'fill': fill, 'blank': blank, 'progress': percentage})
                sys.stdout.flush()

            if (self.progress == self.end):
                self.done()
        return self.completed

    def done(self):
        print
        self.completed = True

    def rotate(self):
        if (not self.completed):
            self.curmark = (self.curmark + 1) % len(self.markers)
            if (self.display):
                self.display.verbose(self.rotate_format % {'title': self.title, 'mark': self.markers[self.curmark]}, rewrite=True, end="", flush=True)
            else:
                sys.stdout.write('\r' + self.rotate_format % {'title': self.title, 'mark': self.markers[self.curmark]})
                sys.stdout.flush()
        return self.completed

class Display():
    def __init__(self, verbose=False, debug=False, logpath=None):
        self.VERBOSE = verbose
        self.DEBUG = debug
        self.logpath = logpath
        self.ruler = '-'

    def setLogPath(self, logpath):
        self.logpath = logpath

    def enableVerbose(self):
        self.VERBOSE = True

    def enableDebug(self):
        self.DEBUG = True

    def log(self, s, filename="processlog.txt"):
        if (self.logpath is not None):
            fullfilename = self.logpath + filename
            if not os.path.exists(os.path.dirname(fullfilename)):
                os.makedirs(os.path.dirname(fullfilename))
            fp = open(fullfilename, "a")
            if (filename == "processlog.txt"):
                fp.write(time.strftime("%Y.%m.%d-%H.%M.%S") + " - " + s + "\n")
            else:
                fp.write(s)
            fp.close()

    def _display(self, line, end="\n", flush=True, rewrite=False):
        if (rewrite):
            line = '\r' + line
        sys.stdout.write(line + end)
        if (flush):
            sys.stdout.flush()
        self.log(line)

    def error(self, line, end="\n", flush=True, rewrite=False):
        '''Formats and presents errors.'''
        line = line[:1].upper() + line[1:]
        s = '%s[!] %s%s' % (Colors.R, Utils.to_unicode(line), Colors.N)
        self._display(s, end=end, flush=flush, rewrite=rewrite)

    def output(self, line, end="\n", flush=True, rewrite=False):
        '''Formats and presents normal output.'''
        s = '%s[*]%s %s' % (Colors.B, Colors.N, Utils.to_unicode(line))
        self._display(s, end=end, flush=flush, rewrite=rewrite)

    def alert(self, line, end="\n", flush=True, rewrite=False):
        '''Formats and presents important output.'''
        s = '%s[*]%s %s' % (Colors.G, Colors.N, Utils.to_unicode(line))
        self._display(s, end=end, flush=flush, rewrite=rewrite)

    def verbose(self, line, end="\n", flush=True, rewrite=False):
        '''Formats and presents output if in verbose mode.'''
        if self.VERBOSE:
            self.output("[VERBOSE] " + line, end=end, flush=True, rewrite=rewrite)

    def debug(self, line, end="\n", flush=True, rewrite=False):
        '''Formats and presents output if in debug mode (very verbose).'''
        if self.DEBUG:
            self.output("[DEBUG]   " + line, end=end, flush=True, rewrite=rewrite)

    def yn(self, line, default=None):
        valid = {"yes": True, "y": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif (default.lower() == "yes") or (default.lower() == "y"):
            prompt = " [Y/n] "
        elif (default.lower() == "no") or (default.lower() == "n"):
            prompt = " [y/N] "
        else:
            print "ERROR: Please provide a valid default value: no, n, yes, y, or None"

        while True:
            choice = self.input(line + prompt)
            if default is not None and choice == '':
                return valid[default.lower()]
            elif choice.lower() in valid:
                return valid[choice.lower()]
            else:
                self.alert("Please respond with 'yes/no' or 'y/n'.")

    def selectlist(self, line, input_list):
        answers = []
        
        # loop over and display the list
        if input_list != []:
            i = 1
            for item in input_list:
                self.output(str(i) + ": " + str(item))
                i = i + 1
        else:
            return answers

        # prompt the user
        choice = self.input(line)

        # seperate choice into an array
        answers = (choice.replace(' ', '')).split(',')

        # return the results
        return answers

    def input(self, line):
        '''Formats and presents an input request to the user'''
        s = '%s[?]%s %s' % (Colors.O, Colors.N, Utils.to_unicode(line))
        answer = raw_input(s)
	return answer

    def heading(self, line):
        '''Formats and presents styled header text'''
        line = Utils.to_unicode(line)
        self.output(self.ruler*len(line))
        self.output(line.upper())
        self.output(self.ruler*len(line))

    def print_list(self, title, _list):
        self.heading(title)
        if _list != []:
            for item in _list:
                self.output(item)
        else:
            self.output("None")
