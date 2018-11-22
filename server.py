from Database import Database
import socket, sys, time

class Server:
    def __init__(self, port):
        self.name = "Server"
        self.MICClient_Address = ('10.0.0.41', 1078)
        self.shouldStopWriting = False
        self.App_Address = ("localhost", 1070)
        self.port = port
        self.database = Database()
        self.listen()
    
    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('10.0.0.42', self.port)
        self.socket.bind(server_address)
        print("%s: Server operational.\nServer Address: %s" %(self.name, server_address))

        while True:
            print ("%s: Waiting to receive on port %d : press Ctrl-C or Ctrl-Break to stop " %(self.name, self.port))

            buffer, address = self.socket.recvfrom(2048)
            if not len(buffer):
                break
            print ("%s: Received %s bytes from %s %s: " %(self.name, len(buffer), address, buffer.decode('utf8')))
            self.processMessage(buffer)
        
        s.shutdown(1)
        return
    
    def processMessage(self, buffer):
        opcode = (buffer[:2]).decode('utf8')
        message = (buffer[2:len(buffer)]).decode('utf8')
        print("%s: Opcode: %s. Message: %s" %(self.name, opcode, message))
        self.executeCommand(opcode, message)
    
    def executeCommand(self, opcode, message):
        if opcode == "01" or opcode == "02":
            print("%s: Received a Start Recording command. Message: %s" %(self.name, message))
            self.sendMessage((opcode + message), self.MICClient_Address)
        elif opcode == "03":
            print("%s: Storing Message in database. Message: %s" %(self.name, message))
            self.storeWord(message)
            self.sendAcknowledgement(opcode, self.App_Address)
        elif opcode == "04":
            print("%s: Starting the writing process.")
            self.sendAcknowledgement(opcode, self.App_Address)
            self.shouldStopWriting = False
            self.writeNextWord()
        elif opcode == "05":
            print("%s: Stopping the writing process.")
            self.shouldStopWriting = True
            self.sendAcknowledgement(opcode, self.App_Address)
        elif opcode == "09":
            self.nextStepForACK(opcode, message)
        else:
            print("%s: Invalid Message Received. Opcode: %s. Message: %s" %(self.name, opcode, message))
        return
    
    def nextStepForACK(self, ackOpcode, acknowledgedCommand):
        if self.isAppCommand(acknowledgedCommand):
            print("%s: Received an acknowledgement for command with opcode %s. Forwarding acknowledgement to the app" %(self.name, acknowledgedCommand))
            self.sendMessage((ackOpcode + acknowledgedCommand), self.App_Address)
        elif self.isServerCommand(acknowledgedCommand):
            print("%s: Received an acknowledgement for command with opcode %s." %(self.name, acknowledgedCommand))
            self.writeNextWord();
        else:
            print("%s: Invalid ACK Received. Opcode: %s. Message: %s" %(self.name, opcode, acknowledgedCommand))
    
    def isAppCommand(self, commandOpcode):
        return commandOpcode == "01" or commandOpcode == "02" or commandOpcode == "03"
    
    def isServerCommand(self, commandOpcode):
        return commandOpcode == "04" or commandOpcode == "05"
    
    def storeWord(self, word):
        self.database.storeWord(word)
        return
    
    def writeNextWord(self):
        nextWord = self.database.dequeueNextWord()
        if self.shouldStopWriting or nextWord is None: #TODO: Send a message in the app once there are no words left to write.
            print("Writing Has Stopped")
        else: #TODO: Send the word/coordinates to the Arduino
            print("Next word to be written is %s" %(nextWord))
    
    def sendAcknowledgement(self, messageOpcode, recipientAddress):
        acknowledgement = "09" + messageOpcode
        self.sendMessage(acknowledgement, recipientAddress)

    def sendMessage(self, message, recipientAddress):
        print ("Sending %s to %s" %(message, recipientAddress))
        self.socket.sendto(message.encode('utf-8'), recipientAddress)


server = Server(1069)
