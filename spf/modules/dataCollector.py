import os
import sys

from core.parser import Parser

class dataCollector(object):
    def __init__(self, domain, path, name, display):
        self.domain = domain
        self.path = path
        self.name = name
        self.display = display
        self.results = ""
        self.parser = None

    def load_results(self):
        # need to overload
        return None

    def run_command(self):
        # need to overload
        return None

    def cleanup(self):
        # need to overload
        return None

    def emails(self):
        if (not self.parser):
            return []
        return self.parser.emails()

    def hosts(self):
        if (not self.parser):
            return []
        return self.parser.hosts()

    def run(self):
        # verify that self.config["XXXXXXXXXX_path"] exists
        if (self.path):
            if (os.path.isfile(self.path)):
                # Start process
                process = self.run_command()
            else:
                return "ERROR: " + self.name + "_path does not point to a valid file"
        else:
            return "ERROR: " + self.name + "_path is not configured"
        self.results = self.load_results()
        self.parser = Parser(self.results, self.domain)
        self.cleanup()
        return None
