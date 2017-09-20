#!/usr/bin/env python

import sys
import logging
import signal
import random
import string
from impacket import smbserver

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open('smb_cap.log', 'a+')

    def write(self, message):
        if message.startswith("Config file parsed") or message.startswith("Callback added for UUID") or message.startswith("Connecting Share") or message.startswith("SMB2_TREE_CONNECT") or message.startswith("Disconnecting Share") or message.startswith("Handle: ") or message.startswith("Closing down connection") or message.startswith("Incoming connection") or message.startswith("AUTHENTICATE_MESSAGE") or message.startswith("User ") or message.startswith("Remaining connections"):
            return

        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

class SmbCap():
    def __init__(self):
        # Setup logging
        handler = logging.StreamHandler(Logger())
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)

        # Create a new SMB server
        server = smbserver.SimpleSMBServer()
        
        # Support SMBv2
        server.setSMB2Support(True)
        
        # Set a random SMB challenge
        challenge = ''.join(random.choice(string.digits) for i in range(16))
        server.setSMBChallenge(challenge)
        
        # Log SMB traffic to console
        server.setLogFile('')
        
        # Start the server
        server.start()

def sigint_handler(signum, frame):
        print 'Stopping... Someone pressed CTRL+C!'
        sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    s = SmbCap()
