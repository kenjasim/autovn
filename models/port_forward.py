import socket
import os
from threading import Thread
import multiprocessing
import logging

from sqlalchemy import Column, Integer, ForeignKey
from db import Base
from db import Session
from print_colours import Print

class PortForward(Base):
    """
    Server to handle port forwarding between host machine, and guest OS SSH clients.
    """
    # Define 'portforwards' SQL table for instances of Network
    __tablename__ = 'portforwards'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    deployment_id = Column(Integer, ForeignKey('deployments.id'))

    def __init__(self, deployment_id):
        self.pid = None
        self.deployment_id = deployment_id
        self.write_to_db()
    
    def start_forwarding_server(self, host_addr='', host_port=2001, dest_addr='', dest_port=22): 
        """
        Run SSH forwarding server as a sub-process. 
        """
        kwargs = {"host_addr": host_addr, "host_port": host_port, "dest_addr": dest_addr, "dest_port": dest_port}
        # required for Mac Catalina  
        try:
            multiprocessing.set_start_method("fork")
        except RuntimeError:
            pass
        # Create and start server as a process
        proc = multiprocessing.Process(target=self.forwarding_server, kwargs=kwargs)
        proc.daemon = True
        proc.start()

    def forwarding_server(self, host_addr='', host_port=2001, dest_addr='', dest_port=22): 
        """
        Initialise port forwarding server to bridge SSH connections between 
        host and virtual machine.
        """
        # Store ProcessID of current subprocess. ID avaliable for shutdown process
        self.pid = os.getpid()
        self.update_to_db()
        # Server process
        try:
            # Listen for new inbound connections
            list_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            list_socket.bind((host_addr, host_port))
            list_socket.listen(5)
            while True:
                # Accept new socket with client 
                client_socket = list_socket.accept()[0]
                # Setup onward socket with host's SSH client
                forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                forward_socket.connect((dest_addr, dest_port))
                # Forward data streams between client and forward socket 
                client_thread = Thread(target=self.forward, args=(client_socket, forward_socket))
                client_thread.daemon = True
                client_thread.start()
                forward_thread = Thread(target=self.forward, args=(forward_socket, client_socket))
                forward_thread.daemon = True
                forward_thread.start()
        finally:
            # If exception encountered, re-establish server 
            forward_server = Thread(target=self.forwarding_server)
            forward_server.daemon = True
            forward_server.start()
    
    def forward(self, source, destination):
        """
        Read from source socket stream and write to destination socket stream.
        """
        try:
            while True:
                string = source.recv(1024)
                if string:
                    destination.sendall(string)
                else:
                    source.shutdown(socket.SHUT_RD)
                    destination.shutdown(socket.SHUT_WR)
        except OSError:
            # Client forcefully closes ssh connection
            pass
    
    def port_in_use(self, port):
        """
        Check if port is in use. 
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def write_to_db(self):
        """
        Write the PortForward object to the database
        """
        Session.add(self)
        Session.commit()

    def update_to_db(self):
        """
        Update the host to the database
        """
        Session.commit()


################################################################################
# Resources
################################################################################