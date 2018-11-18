from Database import Database
import socket, sys, time

class Server:
    def __init__(self, port):
        self.name = "Server"
        self.port = port
        self.database = Database()
        self.listen()
    
    def listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('localhost', self.port)
        s.bind(server_address)
        print("%s: Server operational.\nServer Address: %s" %(self.name, server_address))

        while True:
            print ("%s: Waiting to receive on port %d : press Ctrl-C or Ctrl-Break to stop " %(self.name, self.port))

            buffer, address = s.recvfrom(2048)
            if not len(buffer):
                break
            print ("%s: Received %s bytes from %s %s: " %(self.name, len(buffer), address, buffer.decode('utf8')))
            self.processMessage(buffer)
            acknowledgement = "09" + buffer.decode('utf8')
            print ("%s: Sending %s bytes acknowledgement to %s %s: " %(self.name, len(acknowledgement), address, acknowledgement ))
            s.sendto(acknowledgement.encode('utf-8'), address)
        
        s.shutdown(1)
        return
    
    def processMessage(self, buffer):
        opcode = (buffer[:2]).decode('utf8')
        message = (buffer[2:len(buffer)]).decode('utf8')
        print("%s: Opcode: %s. Message: %s" %(self.name, opcode, message))
        self.executeCommand(opcode, message)
    
    def executeCommand(self, opcode, message):
        if opcode == "01":
            print("%s: Storing Message in database. Message: %s" %(self.name, message))
            self.storeWord(message)
        else:
            print("%s: Invalid Message Received. Opcode: %s. Message: %s" %(self.name, opcode, message))
        return
        
    def storeWord(self, word):
        self.database.storeWord(word)
        return


server = Server(1069)