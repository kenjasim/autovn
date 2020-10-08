import socket
import sys
from threading import Thread

class PortForward(object):
    
    def server(self, host_addr='', host_port=2001, dest_addr="20.0.0.3", dest_port=22): 
        try:
            list_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            list_socket.bind((host_addr, host_port))
            list_socket.listen(5)
            while True:
                client_socket = list_socket.accept()[0]
                print("client socket connected")
                forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("forward socket created")
                forward_socket.connect((dest_addr, dest_port))
                print("forward socket connected")
                Thread(target=self.forward, args=(client_socket, forward_socket)).start()
                Thread(target=self.forward, args=(forward_socket, client_socket)).start()
        finally:
            Thread(target=self.server)
    
    def forward(self, source, destination):
        print("here") 
        while True:
            string = source.recv(1024)
            if string:
                print("forwarding") 
                destination.sendall(string)
            else:
                source.shutdown(socket.SHUT_RD)
                destination.shutdown(socket.SHUT_WR)

################################################################################
# Main
################################################################################

if __name__ == '__main__':
    pf = PortForward()
    pf.server()  


################################################################################
# Resources
################################################################################

