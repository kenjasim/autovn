#!/usr/bin/python3

import optparse

################################################################################
# Main module to be called on start-up. Alias for cli.py
################################################################################

def parseargs():
    p = optparse.OptionParser()
    p.add_option("-r", dest="restapi" ,action="store_true", help="Start avn's REST Api only")
    return p.parse_args()
    
from cli import Console
from restapi.server import RESTServer

if __name__ == '__main__':
    (opts, args) = parseargs()
    
    if opts.restapi == True:
        RESTServer().start()
    else:
        console = Console().cmdloop()