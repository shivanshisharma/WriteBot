# TO TEST: python server.py
import socket, sys, time
import speech_recognition as sr

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

def startRecording():
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

def pauseRecording():
    print("Pausing..")
    

#Continually polling for tasks
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = int(1500) #hardcoded port
    server_address = ('localhost', port)
    s.bind(server_address)

    while True:
        print ("Waiting to receive on port %d" % port)
        buf, address = s.recvfrom(2048)
        print ("Received %s bytes from %s: %s\n" % (len(buf), address, buf))
        break
    
    if(buf == b'Record'): #Message to start recording from android application
        startRecording()

    if(buf == b'Pause Recording'): #Message to pause recording from android application
        pauseRecording()

    #s.shutdown(1)

