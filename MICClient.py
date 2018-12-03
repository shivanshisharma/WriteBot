import speech_recognition as sr
import socket

class MICClient:
    def __init__(self):
        self.name = "MICClient"
        serverIPAddress = input("Enter server IP address: ")
        serverPort = int(input("Enter server port: "))
        self.serverAddress = (serverIPAddress, serverPort)
        receiveIPAddress = input("Enter receiver IP address: ")
        receivePort = int(input("Enter receiver port: "))
        self.receiveAddress = (receiveIPAddress, receivePort)
        self.listen()
    
    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.receiveAddress)
        print("%s: %s operational.\n%s Address: %s" %(self.name, self.name, self.name, self.receiveAddress))

        while True:
            print ("%s: Waiting to receive on %s : press Ctrl-C or Ctrl-Break to stop " %(self.name, self.receiveAddress))

            buffer, address = self.socket.recvfrom(2048)
            if not len(buffer):
                break
            print ("%s: Received %s bytes from %s %s: " %(self.name, len(buffer), address, buffer.decode('utf8')))
            self.processMessage(buffer)
            self.sendAcknowledgement((buffer[:2]).decode('utf8'), address)
        
        self.socket.shutdown(1)
        return
    
    def processMessage(self, buffer):
        opcode = (buffer[:2]).decode('utf8')
        message = (buffer[2:len(buffer)]).decode('utf8')
        print("%s: Opcode: %s. Message: %s" %(self.name, opcode, message))
        self.executeCommand(opcode, message)
    
    def executeCommand(self, opcode, message):
        if opcode == "01":
            print("%s: Received a Start Recording command. Message: %s" %(self.name, message))
            self.startRecording() #TODO: Make this check for the current system state to make sure it isn't already recording
        elif opcode == "02":
            print("%s: Received a Pause Recording command. Message: %s" %(self.name, message))
            self.pauseRecording() #TODO: Make this check for the current system state to make sure it is already recording
        else:
            print("%s: Invalid Message Received. Opcode: %s. Message: %s" %(self.name, opcode, message))
        return

    def startRecording(self):        
        def callback(recognizer, audio):
            print("Just started callback")
            try:
                print("Entered Try")
                self.sendMessage(("03" + recognizer.recognize_google(audio)), self.serverAddress)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                
        recognizer = sr.Recognizer()
        recognizer.energy_threshhold = 4000 #for sensitive microphone or microphones in louder rooms
        microphone = sr.Microphone()
                
        self.stop_listening = recognizer.listen_in_background(microphone, callback)
        print("Say Something!")

    def pauseRecording(self):
        self.stop_listening()
        
    def sendAcknowledgement(self, messageOpcode, recipientAddress):
        acknowledgement = "09" + messageOpcode
        self.sendMessage(acknowledgement, recipientAddress)

    def sendMessage(self, message, recipientAddress):
        print ("Sending %s to %s" %(message, recipientAddress))
        self.socket.sendto(message.encode('utf-8'), recipientAddress)

MICClient()
