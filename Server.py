from Database import Database
import socket, sys, time

class Server:
    def __init__(self, port):
        self.port = port
        self.database = Database()
        self.listen()
    
    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', self.port)
        s.bind(server_address)
        print("Server operational.\nServer Address: %s", server_address)

        while True:

            print ("Waiting to receive on port %d : press Ctrl-C or Ctrl-Break to stop " % self.port)

            buf, address = s.recvfrom(2048)
            if not len(buf):
                break
            print ("Received %s bytes from %s %s: " % (len(buf), address, buf.decode('utf8')))
            self.storeWord(buf.decode('utf8'))
            acknowledgement = "ACK: " + buf.decode('utf8')
            print ("Sending %s bytes acknowledgement to %s %s: " % (len(acknowledgement), address, acknowledgement ))
            s.sendto(acknowledgement.encode('utf-8'), address)
        
        s.shutdown(1)
        return
        
    def storeWord(self, word):
        self.database.storeWord(word)
        return


server = Server(1069)