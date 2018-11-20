from unittest import mock
from server import Server

def testServerInitializer():
    testServer = Server(1069)
    self.assertEqual(testServer.name, "Server")
    self.assertEqual(testServer.MICClient_Address, ("localhost", 1078))
    self.assertFalse(testServer.shouldStopWriting)
    self.assertEqual(testServer.App_Addressname, ("localhost", 1070))
    self.assertEqual(testServer.port, 1069)
    self.assertIsNotNone(testServer.database)
    testServer = None
    
testServerInitializer()