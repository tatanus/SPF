import re
import os
import subprocess
import tempfile

from modules.dataCollector import dataCollector

class theHarvester(dataCollector):
    def __init__(self, domain, path, display):
        dataCollector.__init__(self, domain, path, "theHarvester", display)
        (garbage, self.outfile) = tempfile.mkstemp(suffix='.xml', prefix='theHarvester_', dir=None, text=True)

    def run_command(self):
        self.display.verbose("python " + self.path + " -d " + self.domain + " -b bing -l 500 -f")
        return subprocess.call(["python", self.path, "-d", self.domain, "-b", "bing", "-l", "500", "-f", self.outfile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def load_results(self):
        # open outfile
        a=open(self.outfile,'rb')
        data = a.read()
        return data
        # extract necessary data
        # grep -oh "[^>]*@[^<]*" self.outfile
#        emails = re.findall("<email>([^<]*)</email>", data)
#        return emails

    def cleanup(self):
        os.remove(self.outfile)
        return

if __name__ == "__main__":
    th = theHarvester("example.com", "/TOOLS/theHarvester/theHarvester.py")
    th.run()
    print th.emails()
    print th.hosts()
