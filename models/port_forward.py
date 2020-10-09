import socket
import sys, os
from threading import Thread
import multiprocessing

from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from db import Base
from db import Session

class PortForward(Base):

    __tablename__ = 'sshforwarder'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)

    def __init__(self):
        self.pid = None
        self.write_to_db()
    
    def start_forwarding_server(self, host_addr='', host_port=2001, dest_addr='', dest_port=22): 
        """
        Run SSH forwarding server threaded. 
        """
        # Create and start a process
        kwargs = {"host_addr": host_addr, "host_port": host_port, "dest_addr": dest_addr, "dest_port": dest_port}
        try:
            multiprocessing.set_start_method("fork")
        except:
            pass
        proc = multiprocessing.Process(target=self.forwarding_server, kwargs=kwargs)
        proc.daemon = True
        proc.start()

    def forwarding_server(self, host_addr='', host_port=2001, dest_addr='', dest_port=22): 
        """
        Initialise port forwarding server to bridge SSH connections between 
        host and virtual machine.
        """
        self.pid = os.getpid()

        self.update_to_db()
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
                client_thread = Thread(target=self.forward, args=(client_socket, forward_socket))
                client_thread.daemon = True
                client_thread.start()
                forward_thread = Thread(target=self.forward, args=(forward_socket, client_socket))
                forward_thread.daemon = True
                forward_thread.start()
        finally:
            forward_server = Thread(target=self.forwarding_server)
            forward_server.daemon = True
            forward_server.start()
    
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

    def write_to_db(self):
        """
        Write the host to the database
        """
        Session.add(self)
        Session.commit()

    def update_to_db(self):
        """
        Update the host to the database
        """
        Session.commit()

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    pf = PortForward()
    pf.server()  


################################################################################
# Resources
################################################################################

