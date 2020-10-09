from subprocess import Popen, PIPE
import subprocess
import pathlib
import sys
import socket
import os
from threading import Thread

class Shell(object):
    """
    Object for creating SSH terminal sessions with clients. 
    """

    def connect(self, hostname, hostaddr, password, hostport):
        """
        Open Apple Mac terminal and open interactive SSH session with host
        Options: 
            hostname (str): username of target host 
            hostaddr (str): IP address of the target host 
            password (str): password of the target host 
            hostport (str): SSH-client port to connect to on target host
        """
        # Identify path the SSH bash files 
        bsPath = str(pathlib.Path(__file__).parent.absolute())
        # Check the OS to see which shell to run
        # For Mac use AppleScript 
        # For Linux Gnome Terminal
        if sys.platform == "darwin":
            cmd = ("osascript -e '"
                "tell application \"Terminal\" "
                "to do script "
                "\"cd " + bsPath + " "
                + "&& ./ssh_connect.sh "
                + hostname + " "
                + hostaddr + " "
                + password + " "
                + str(hostport) 
                + "\"'")
        elif sys.platform == "linux":
            cmd = ("gnome-terminal --working-directory="
                "\"" + bsPath + "\""
                + " -- "
                + "zsh -c \"./ssh_connect.sh "
                + hostname + " "
                + hostaddr + " "
                + password + " "
                + str(hostport)
                + "; zsh \"")
        else:
            raise Exception("OS not supported, please open shell manually")
        # Execute as subprocess
        r = Popen([cmd], universal_newlines = True, shell=True, stdout=PIPE)

    def copy(self, hostname="dev", hostaddr="20.0.0.5", password="ved", keypath="~/.ssh/id_rsa.pub"):
        """
        Share SSH public key with host.
        Options:
            hostname (str): username of target host 
            hostaddr (str): IP address of the target host 
            password (str): password of the target host 
            keypath  (str): path to RSA key to be shared with target host. 
        """
        bsPath = str(pathlib.Path(__file__).parent.absolute())
        cmd = bsPath + "/ssh_copy.sh " + hostname + " " + hostaddr + " " + password + " " + keypath
        # Execute as subprocess
        r = subprocess.getoutput(cmd)
        return r


################################################################################
# Resources
################################################################################

# cmd = ['osascript -e "tell application \\"Terminal\\" to do script \\"cd ~/Documents/Code && ./ssh_connect.sh dev 20.0.0.5 ved \\""']
