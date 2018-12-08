from Database import Database
from GCodeGenerator import GCodeGenerator
import socket, sys, time
import serial
import threading

class Server:
    def __init__(self): 
        self.name = "Server"
        serverIPAddress = input("Please Enter Server's IP address: ")
        serverPort = int(input("Please Enter Server's Port: "))
        MICClientIPAddress = input("Please Enter MICClient's IP address: ")
        MICClientPort = int(input("Please Enter MICClient's Port: "))
        AppIPAddress = input("Please Enter App's IP address: ")
        AppIPPort = int(input("Please Enter App's Port: "))
        self.MICClient_Address = (MICClientIPAddress, MICClientPort)
        self.App_Address = (AppIPAddress, AppIPPort)
        self.Server_Address = (serverIPAddress, serverPort)
        self.shouldStopWriting = False
        self.database = Database()
        self.GCodeGenerator = GCodeGenerator()
        self.arduinoSerialBus = serial.Serial('/dev/ttyACM1', 9600)
        self.listen()
    
    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.Server_Address)
        print("%s: Server operational.\nServer Address: %s" %(self.name, self.Server_Address))

        while True:
            print ("%s: Waiting to receive: press Ctrl-C or Ctrl-Break to stop " %(self.name))

            buffer, address = self.socket.recvfrom(2048)
            if not len(buffer):
                break
            print ("%s: Received %s bytes from %s %s: " %(self.name, len(buffer), address, buffer.decode('utf8')))
            processingThread = threading.Thread(target = self.processMessage, args = [buffer, address])
            processingThread.start()
        
        s.shutdown(1)
        return
    
    def processMessage(self, buffer, sender):
        opcode = (buffer[:2]).decode('utf8')
        message = (buffer[2:len(buffer)]).decode('utf8')
        print("%s: Opcode: %s. Message: %s" %(self.name, opcode, message))
        self.executeCommand(opcode, message, sender)
    
    def executeCommand(self, opcode, message, sender):
        if opcode == "01" or opcode == "02":
            print("%s: Received a Start Recording command. Message: %s" %(self.name, message))
            self.sendMessage((opcode + message), self.MICClient_Address)
        elif opcode == "03":
            print("Expected Address: %s Sender: %s Equal %s" %(self.App_Address, sender, (sender == self.App_Address)))
            print("%s: Storing Message in database. Message: %s" %(self.name, message))
            if sender == self.App_Address:
                print("Deleting All Words")
                self.database.deleteAllWords()
            self.storeText(message)
            self.sendAcknowledgement(opcode, sender)
            self.updateApp()
        elif opcode == "04":
            print("%s: Starting the writing process.")
            self.sendAcknowledgement(opcode, sender)
            self.shouldStopWriting = False
            self.writeNextWord()
        elif opcode == "05":
            print("%s: Stopping the writing process.")
            self.shouldStopWriting = True
            self.sendAcknowledgement(opcode, sender)
        elif opcode == "07":
            print("%s: Storing font %s in the database." %(self.name, message))
            self.database.deleteAllFonts()
            self.database.storeFont(message)
            self.sendAcknowledgement(opcode, sender)
        elif opcode == "09":
            self.nextStepForACK(opcode, message)
        else:
            print("%s: Invalid Message Received. Opcode: %s. Message: %s" %(self.name, opcode, message))
        return
    
    def nextStepForACK(self, ackOpcode, acknowledgedCommand):
        if self.isAppCommand(acknowledgedCommand):
            print("%s: Received an acknowledgement for command with opcode %s. Forwarding acknowledgement to the app" %(self.name, acknowledgedCommand))
            self.sendMessage((ackOpcode + acknowledgedCommand), self.App_Address)
        elif self.isWritingCommand(acknowledgedCommand):
            print("%s: Received an acknowledgement for writing command with opcode %s." %(self.name, acknowledgedCommand))
            self.writeNextWord();
        elif self.isServerCommand(acknowledgedCommand):
            print("%s: Received an acknowledgement for server command with opcode %s." %(self.name, acknowledgedCommand))
        else:
            print("%s: Invalid ACK Received. Opcode: %s. Message: %s" %(self.name, ackOpcode, acknowledgedCommand))
    
    def isAppCommand(self, commandOpcode):
        return commandOpcode == "01" or commandOpcode == "02" or commandOpcode == "03" or commandOpcode == "07" or commandOpcode == "08"
    
    def isWritingCommand(self, commandOpcode):
        return commandOpcode == "04" or commandOpcode == "05"
    
    def isServerCommand(self, commandOpcode):
        return self.isWritingCommand(commandOpcode) or commandOpcode == "07"
    
    def storeText(self, text):        
        for word in text.split():
            self.database.storeWord(word)
            
        return
    
    def writeNextWord(self):
        if self.shouldStopWriting:
            print("%s: Writing Has Stopped" %(self.name))
            return
        nextWord = self.database.dequeueNextWord()
        if nextWord is None: 
            print("%s: No more words to write" %(self.name))
        else:
            print("%s: Next word to be written is %s" %(self.name, nextWord))
            print(self.shouldStopWriting)
            font = self.database.getSelectedFont()
            gCode = self.GCodeGenerator.generateGCode(nextWord, font)
            print("\n".join(gCode))
            for line in gCode:
                self.sendMessageToArduino(line)
                self.getArduinoAcknowledgement()
            self.writeNextWord()
    
    def updateApp(self):
        words = self.database.getAllWords()
        message = '06' + ' '.join(words)
        self.sendMessage(message, self.App_Address)

    def sendAcknowledgement(self, messageOpcode, recipientAddress):
        acknowledgement = "09" + messageOpcode
        self.sendMessage(acknowledgement, recipientAddress)

    def sendMessage(self, message, recipientAddress):
        print("%s: Sending %s to %s" %(self.name, message, recipientAddress))
        self.socket.sendto(message.encode('utf-8'), recipientAddress)
    
    def sendMessageToArduino(self, message):
        print("%s: Sending message to Arduino: %s" %(self.name, message))
        self.arduinoSerialBus.write(message)
        self.arduinoSerialBus.flush()
    
    def getArduinoAcknowledgement(self):
        message = self.arduinoSerialBus.readline()
        if "09" in message:
            print("%s: Received acknowledgement from Arduino: %s" %(self.name, message))
        else:
            print(message)
            self.getArduinoAcknowledgement()


server = Server()
