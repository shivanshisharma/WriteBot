from Database import Database
import socket, sys, time
import speech_recognition as sr

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
            print("%s: Received a Start Recording command. Message: %s" %(self.name, message))
            self.startRecording() #TODO: Make this check for the current system state to make sure it isn't already recording
        elif opcode == "04":
            print("%s: Storing Message in database. Message: %s" %(self.name, message))
            self.storeWord(message)
        else:
            print("%s: Invalid Message Received. Opcode: %s. Message: %s" %(self.name, opcode, message))
        return
        
    def storeWord(self, word):
        self.database.storeWord(word)
        return

    #sendMessage('localhost' 1500 1501 'Hello')
    def sendMessage(host, sendPort, receivePort, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (host, sendPort)
        receiver_address = ('localhost', receivePort)
        s.bind(receiver_address)
        
        s.sendto(data.encode('utf-8'), server_address)
        
        buf, address = s.recvfrom(2048)
        print ("Received %s bytes from %s: %s" % (len(buf), address, buf))
        
        quit()

    def startRecording(self):
        queue = []
        r = sr.Recognizer()
        r.energy_threshhold = 4000
        with sr.Microphone() as source:
            print('Recording speech, say something!')
            try:
                audio = r.listen(source, timeout = 10) #Set timeout time
            except sr.WaitTimeoutError:
                return "Audio Timeout"
        try:
            queue = list(r.recognize_google(audio).lower())
            #print(queue)
            print(r.recognize_google(audio).lower()) #try commenting out this line to see if it still prints
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return "Could not request results from Google Speech Recognition service; {0}".format(e)
    
    def pauseRecording(self):
        print("Pausing..")


server = Server(1069)