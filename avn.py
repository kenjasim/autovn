#!/usr/bin/python3

import argparse

################################################################################
# Main module to be called on start-up. 
################################################################################

def parseargs():
    p = argparse.ArgumentParser(description='Launch a custon virtual network')
    p.add_argument("-r", dest="restapi" ,action="store_true", help="Start avn's REST Api only")
    p.add_argument("-c", metavar='<url/to/api>', nargs='?', dest="cliconsole", type=str, const="default", help="Start avn's Rest Client Console (no argument defaults")
    return vars(p.parse_args())


from cli import Console
from restapi.server import RESTServer

if __name__ == '__main__':
    arguments = parseargs()
    
    if arguments["restapi"]:
        RESTServer().start()
    elif arguments["cliconsole"]:
        if arguments["cliconsole"] != "default":
            console = Console(remote=True, url=arguments["cliconsole"]).cmdloop() 
        else:
            console = Console(remote=True).cmdloop() 
    else:
        console = Console().cmdloop()
        