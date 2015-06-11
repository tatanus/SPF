#!/usr/bin/env python

# Original code borrowed from http://code.activestate.com/recipes/286240-python-portscanners/
# Modified as needed by Adam Compton

import socket
import sys
import threading, Queue

MAX_THREADS = 10
TIMEOUT = 0.5

# Threaded Scanner class
class Scanner(threading.Thread):
    def __init__(self, inq, outq):
        threading.Thread.__init__(self)
        self.setDaemon(1)  # do not enter into daemon mode
        self.inq = inq
        self.outq = outq

    def run(self):
        # loop over the "in" queue and get a new port and scan it
        socket.setdefaulttimeout(TIMEOUT)
        while 1:
            host, port = self.inq.get()
            sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
            try:
                # connect to the given host:port
                sd.connect((host, port))
            except socket.error:
                # set the CLOSED flag
                self.outq.put((host, port, 'CLOSED'))
            else:
                # set the OPEN flag
                self.outq.put((host, port, 'OPEN'))
                sd.close()

def scan(host, ports, nthreads=MAX_THREADS):
    # set up in and out queues
    toscan = Queue.Queue()
    scanned = Queue.Queue()

    # set up scanner threads
    scanners = [Scanner(toscan, scanned) for i in range(nthreads)]
    for scanner in scanners:
        scanner.start()

    # add ports to the scan queue
    hostports = [(host, port) for port in ports]
    for hostport in hostports:
        toscan.put(hostport)

    # loop over scanned queue and id any open ports
    results = {}
    openports = []
    for host, port in hostports:
        while (host, port) not in results:
            nhost, nport, nstatus = scanned.get()
            results[(nhost, nport)] = nstatus
            if nstatus <> 'CLOSED':
                openports.append(nport)

    # return list of open ports
    return openports

if __name__ == '__main__':
    openports = scan('localhost', xrange(1, 1024))
    for port in openports:
        print port
