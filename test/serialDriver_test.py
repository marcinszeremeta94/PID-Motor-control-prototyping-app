from SerialDriver import SerialConnectionState
from SerialDriver import SerialDriver
import mock
import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSerialMethods(unittest.TestCase):

    @mock.patch('SerialDriver.serial')
    def testSucceedConnection(self, mock_serial):
        sutSerial = SerialDriver()
        sutSerial.establishConnection()
        sutSerial.connect()
        self.assertEqual(SerialConnectionState.Connected, sutSerial.getState())


if __name__ == '__main__':
    unittest.main()
