#!/usr/bin/env python

import sys
import logging
import signal
from impacket import smbserver

# Logger to write to both console and file
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open('smb_cap.log', 'a+')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

class SmbCap():
    def __init__(self):
        # Init logging
        handler = logging.StreamHandler(Logger())
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
        # Create a new SMB server
        server = smbserver.SimpleSMBServer()
        # We want to support SMBv2
        server.setSMB2Support(True)
        # Set a custom SMB challenge
        server.setSMBChallenge('1122334455667788')
        # Log SMB traffic to console
        server.setLogFile('')
        # Start the server
        server.start()


def sigint_handler(signum, frame):
        print 'Stop pressing the CTRL+C!'
        sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
if __name__ == "__main__":
    s = SmbCap()
