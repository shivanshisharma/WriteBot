import speech_recognition as sr
import socket

class MICClient:
    def __init__(self, serverIPAddress, serverPort, receivePort): #TODO: Reconsider global variables 
        self.name = "MICClient"
        self.serverAddress = (serverIPAddress, serverPort) #TODO: Consider letting the user input these
        self.listen(receivePort) #TODO: Consider letting the user input this
    
    def listen(self, receivePort):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receive_address = ('10.0.1.41', receivePort) #TODO: Consider letting the user input the address
        self.socket.bind(receive_address)
        print("%s: %s operational.\n%s Address: %s" %(self.name, self.name, self.name, receive_address))

        while True:
            print ("%s: Waiting to receive on port %d : press Ctrl-C or Ctrl-Break to stop " %(self.name, receivePort))

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
            try:
                print("Say something!")
                sendMessage(self, recognizer.recognize_google(audio), serverAddress)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                
        recognizer = sr.Recognizer()
        #recognizer.energy_threshhold = 4000 #for sensitive microphone or microphones in louder rooms
        microphone = sr.Microphone()
                
        self.stop_listening = recognizer.listen_in_background(microphone, callback)
        print("Just started callback")

    def pauseRecording(self):
        self.stop_listening()
        
    def sendAcknowledgement(self, messageOpcode, recipientAddress):
        acknowledgement = "09" + messageOpcode
        self.sendMessage(acknowledgement, recipientAddress)

    def sendMessage(self, message, recipientAddress):
        print ("Sending %s to %s" %(message, recipientAddress))
        self.socket.sendto(message.encode('utf-8'), recipientAddress)

MICClient('10.0.1.42', 1069, 1078)
