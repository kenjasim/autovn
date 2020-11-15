#!/usr/bin/python3

import argparse, os, pathlib, shutil, logging, sys
from pathlib import Path

from db import create_tables

homedir = pathlib.Path().home()

################################################################################
# Main module to be called on start-up. 
################################################################################

def parseargs():
    p = argparse.ArgumentParser(description='Launch a custom virtual network')
    p.add_argument("-r", dest="restapi" ,action="store_true", help="Start avn's REST Api only")
    p.add_argument("-c", metavar='<url/to/api>', nargs='?', dest="cliconsole", type=str, const="default", help="Start avn's Rest Client Console (no argument defaults)")
    return vars(p.parse_args())

def config_folder():
    """Check if the .avn config folder is made, if not make it and add the required files to it"""

    # Check if the directories have been created
    if not os.path.isdir(str(homedir / ".avn")):
        os.mkdir(str(homedir / ".avn"))
        os.mkdir(str(homedir / ".avn" / "keys"))
        os.mkdir(str(homedir / ".avn" / "templates"))
        os.mkdir(str(homedir / ".avn" / "images"))
        os.mkdir(str(homedir / ".avn" / "logs"))
        os.mkdir(str(homedir / ".avn" / "certs"))
        os.mkdir(str(homedir / ".avn" / "proxy"))

    # Makes the keys directory
    elif not os.path.isdir(str(homedir / ".avn" / "keys")):
        os.mkdir(str(homedir / ".avn" / "keys"))

    # Makes the templates directory
    elif not os.path.isdir(str(homedir / ".avn" / "templates")):
        os.mkdir(str(homedir / ".avn" / "templates"))
    
    # Makes the images directory
    elif not os.path.isdir(str(homedir / ".avn" / "images")):
        os.mkdir(str(homedir / ".avn" / "images"))
    
    # Makes the logs directory
    elif not os.path.isdir(str(homedir / ".avn" / "logs")):
        os.mkdir(str(homedir / ".avn" / "logs"))
    
    # Makes the certs directory
    elif not os.path.isdir(str(homedir / ".avn" / "certs")):
        os.mkdir(str(homedir / ".avn" / "certs"))
    
    # Makes the restapi proxy config directory
    elif not os.path.isdir(str(homedir / ".avn" / "proxy")):
        os.mkdir(str(homedir / ".avn" / "proxy"))
            

from cli import Console
from restapi.server import RESTServer

if __name__ == '__main__':

    # Check and make the config folder
    config_folder()

    # Initialise logging handling 
    logging.basicConfig(level=logging.DEBUG,
                                filename = str(homedir / ".avn" / "logs" / "avn.log"),
                                format='%(asctime)s, %(levelname)s, %(name)s, %(message)s')

    arguments = parseargs()

    create_tables()
    
    if arguments["restapi"]:
        RESTServer(remote=True).start()
    elif arguments["cliconsole"]:
        if arguments["cliconsole"] != "default":
            console = Console(remote=True, url=arguments["cliconsole"]).cmdloop() 
        else:
            console = Console(remote=True).cmdloop() 
    else:
        console = Console().cmdloop()
        
