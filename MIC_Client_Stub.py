#James Richards 100966651
#Chibueze Franklin Ndudirim 100977934

# Source: https://pymotw.com/2/socket/udp.html

import socket, sys, time

host = sys.argv[1]
sendPort = int(sys.argv[2])
receivePort = int(sys.argv[3])
numberOfMessagesToSend = int(sys.argv[4])

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (host, sendPort)
receiver_address = ('localhost', receivePort)

s.bind(receiver_address)

message = "Message"
for x in range(numberOfMessagesToSend):
    print ("")
    print ("Sending Message" + str(x + 1) + " to " + str(server_address))
    s.sendto(("01" + message + str(x + 1)).encode('utf-8'), server_address)
    print ("Waiting to receive acknowledgement on port %d : press Ctrl-C or Ctrl-Break to stop " % receivePort)

    buf, address = s.recvfrom(2048)
    if not len(buf):
        break
    print ("Received acknowledgement of %s bytes from %s %s: " % (len(buf), address, buf ))

s.shutdown(1)

