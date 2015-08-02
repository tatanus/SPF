#!/usr/bin/env python
"""
Standard Launcher for the spf (Speed Phishing Framework)
"""

import sys

from core.framework import Framework

if __name__ == "__main__":
    framework = Framework()
    try:
        framework.run(sys.argv[1:])
    except KeyboardInterrupt:
        framework.ctrlc()
    except Exception as e:
        framework.cleanup()
