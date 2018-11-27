from unittest import mock
from unittest.mock import sentinel, patch
from server import Server

def testServerInitializer():
    sut = Server(1069)
    with patch("server.Server.database") as mock_store:
        sut.storeWord("Hello4")
    mock_store.assert_called_once_with("Hello1")
    
testServerInitializer()