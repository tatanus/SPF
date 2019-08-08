#!/usr/bin/env python3
"""
Standard Launcher for the spf (Speed Phishing Framework)
"""

import sys, traceback

from core.framework import Framework

if __name__ == "__main__":
    framework = Framework()
    try:
        framework.run(sys.argv[1:])
    except KeyboardInterrupt:
        framework.ctrlc()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print()
        print()
        print("*** print_exception:")
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
        print()
        print()
        print("*** print_exc:")
        traceback.print_exc()
        #print
        #print
        #print "*** format_exc, first and last line:"
        #formatted_lines = traceback.format_exc().splitlines()
        #print formatted_lines[0]
        #print formatted_lines[-1]
        #print
        #print
        #print "*** format_exception:"
        #print repr(traceback.format_exception(exc_type, exc_value,
        #                                  exc_traceback))
        #print
        #print
        #print "*** extract_tb:"
        #print repr(traceback.extract_tb(exc_traceback))
        #print
        #print
        #print "*** format_tb:"
        #print repr(traceback.format_tb(exc_traceback))
        #print
        #print
        #print "*** tb_lineno:", exc_traceback.tb_lineno
        #print sys.exc_info()[0]
        #framework.cleanup()
