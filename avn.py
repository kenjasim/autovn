#!/usr/bin/python3

import optparse

################################################################################
# Main module to be called on start-up. Alias for cli.py
################################################################################

def parseargs():
    p = optparse.OptionParser()
    p.add_option("-v", dest="noDB", action="store_true", help="Start without the database.")
    return p.parse_args()
    
from cli import Console

if __name__ == '__main__':
    (opts, args) = parseargs()
    console = Console().cmdloop()