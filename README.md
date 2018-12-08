# WriteBot

## Instructions on how to start the system 

1. Clone this repo:  
`$ git clone https://github.com/BuzyFranklin/WriteBot.git`  

2. On the Raspberry Pi 3, start the server:  
`$ python server.py`  

It will ask for 6 arguments, the address of the Raspberry Pi 3 (server) and port, the address of the Raspberry Pi 2 (mic client) and port, and the address of the android app and port.  

3. On the Raspberry Pi 2, start the mic client:  
`$ python MICClient.py`  

It will ask for 6 arguments, the address of the Raspberry Pi 3 (server) and port, and the address of the Raspberry Pi 2 (mic client) and port.  

Get the correct modules with pip:  
* pip install speechrecognition
* pip install pyaudio
* pip install pyalsaaudio

4. Under `My Application` build and run the android application on a simulator or real device.  
