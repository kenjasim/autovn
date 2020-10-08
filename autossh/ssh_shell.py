from subprocess import Popen, PIPE
import subprocess
import pathlib
import sys
import socket
from threading import Thread

class Shell(object):

    def connect(self, hostname, hostaddr, password, hostport):
        """Open Apple Mac terminal and open interactive SSH session with host"""
        # Use AppleScript to open a new terminal and run SSH bash script
        bsPath = str(pathlib.Path(__file__).parent.absolute())
        # Check the OS to see which shell to run
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
        """Share SSH public key with host."""
        bsPath = str(pathlib.Path(__file__).parent.absolute())
        cmd = bsPath + "/ssh_copy.sh " + hostname + " " + hostaddr + " " + password + " " + keypath
        # Execute as subprocess
        r = subprocess.getoutput(cmd)
        return r

    def start_forwarding_server(self, host_addr='', host_port=2001, dest_addr='', dest_port=22): 
        """
        Run SSH forwarding server threaded. 
        """
        kwargs = {"host_addr": host_addr, "host_port": host_port, "dest_addr": dest_addr, "dest_port": dest_port}
        Thread(target=self.forwarding_server, kwargs=kwargs).start() 
    
    def forwarding_server(self, host_addr='', host_port=2001, dest_addr='', dest_port=22): 
        """
        Initialise port forwarding server to bridge SSH connections between 
        host and virtual machine.
        """
        try:
            list_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            list_socket.bind((host_addr, host_port))
            list_socket.listen(5)
            while True:
                client_socket = list_socket.accept()[0]
                # print("client socket connected")
                forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # print("forward socket created")
                forward_socket.connect((dest_addr, dest_port))
                # print("forward socket connected")
                Thread(target=self.forward, args=(client_socket, forward_socket)).start()
                Thread(target=self.forward, args=(forward_socket, client_socket)).start()
        finally:
            Thread(target=self.forwarding_server).start() 
    
    def forward(self, source, destination):
        """
        Helper script for forwarding_server for managing socket stream read/writes.
        """
        try:
            while True:
                string = source.recv(1024)
                if string:
                    # print("forwarding") 
                    destination.sendall(string)
                else:
                    source.shutdown(socket.SHUT_RD)
                    destination.shutdown(socket.SHUT_WR)
        except Exception as e: 
            pass 
    
    def port_in_use(self, port):
        """
        Check if port is in use. 
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0


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
