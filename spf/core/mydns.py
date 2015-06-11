import sys

import dns.resolver
import dns.reversename
import dns.zone
import os
from core.gather import Gather
from core.display import Display, ProgressBar

class Dns():
    @staticmethod    
    def lookup(name):
        hosts = []
        try:
            records = dns.resolver.query(name)
            for rdata in records:
                hosts.append(rdata.address)
            return hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
            return hosts

    @staticmethod    
    def reverse(ip):
        hosts = []
        try:
            records = dns.resolver.query(dns.reversename.from_address(ip), 'PTR')
            for rdata in records:
                hosts.append(rdata.to_text().rstrip('.'))
            return hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
            return hosts

    @staticmethod    
    def mx(domain):
        hosts = []
        try:
            records = dns.resolver.query(domain, "MX")
            for rdata in records:
                hosts.append(str(rdata.exchange).rstrip('.'))
            return hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
            return hosts
    
    @staticmethod    
    def ns(domain):
        hosts = []
        try:
            records = dns.resolver.query(domain, "NS")
            for rdata in records:
                hosts.append(rdata.to_text().rstrip('.'))
            return hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
            return hosts

    @staticmethod    
    def a(host):
        hosts = []
        try:
            records = dns.resolver.query(host, "A")
            for rdata in records:
                hosts.append(rdata.to_text().rstrip('.'))
            return hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
            return hosts

    @staticmethod    
    def txt(domain):
        hosts = []
        try:
            records = dns.resolver.query(domain, "TXT")
            for rdata in records:
                hosts.append(rdata.to_text())
            return hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
            return hosts

    @staticmethod    
    def axfr(domain):
        hosts = Dns.ns(domain)
        for host in hosts:
            z = dns.zone.from_xfr(dns.query.xfr(host, domain))
            print dns.query.xfr(host, domain)
            if (z):
                names = z.nodes.keys()
                names.sort()
                for n in names:
                    print z[n].to_text(n)
                print ""

    @staticmethod    
    def brute(domain, display):
        hosts = []
        script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
        fn = script_dir + "namelist.txt"
        if os.path.isfile(fn):
            num_lines = sum(1 for line in open(fn, 'r+'))
            progress = ProgressBar(end=num_lines, width=50, display=display)
            f = open(fn, 'r+')

            for line in f:
                progress.inc()
                target = line.strip() + '.' + domain.strip()

                temp_hosts = Dns.a(target)
                if(Dns.a(target)):
                    hosts.append(target.lower())
            return hosts
        else:
            print "ERROR: " + script_dir + "namelist.txt could not be found!"
            return hosts



if __name__ == "__main__":
    print "hi"

