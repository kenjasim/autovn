from subprocess import Popen, PIPE
import subprocess
import pathlib

class Shell(object):

    def connect(self, hostname="dev", hostaddr="20.0.0.5", password="ved"):
        """Open Apple Mac terminal and open interactive SSH session with host"""
        # Use AppleScript to open a new terminal and run SSH bash script
        bsPath = str(pathlib.Path(__file__).parent.absolute())
        cmd = ("osascript -e '"
            "tell application \"Terminal\" "
            "to do script "
            "\"cd " + bsPath + " "
            + "&& ./ssh_connect.sh "
            + hostname + " "
            + hostaddr + " "
            + password
            + "\"'")
        # Execute as subprocess 
        r = Popen([cmd], universal_newlines = True, shell=True, stdout=PIPE)
    
    def copy(self, hostname="dev", hostaddr="20.0.0.5", password="ved", keypath="~/.ssh/id_rsa.pub"):
        """Share SSH public key with host."""
        bsPath = str(pathlib.Path(__file__).parent.absolute())
        cmd = bsPath + "/ssh_copy.sh " + hostname + " " + hostaddr + " " + password + " " + keypath
        # Execute as subprocess 
        r = subprocess.getoutput(cmd)
        return r
   

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    s = Shell()
    s.connect(hostname="dev", hostaddr="192.168.56.101", password="ved")


################################################################################
# Resources
################################################################################

# cmd = ['osascript -e "tell application \\"Terminal\\" to do script \\"cd ~/Documents/Code && ./ssh_connect.sh dev 20.0.0.5 ved \\""']