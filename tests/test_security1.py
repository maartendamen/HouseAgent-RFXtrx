import unittest
from rfxtrx import RFXtrxProtocol

response = ['\x08', ' ', '\x00', '\x9d', '\xd3', '\xdc', 'T', '\x00', 'i']

class Test(unittest.TestCase):

    def setUp(self):
        self.protocol = RFXtrxProtocol(None)
        self.protocol._handle_security1_response(response[2:])

    def testStatus(self):
        '''
        Test whether the correct status string is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].status, 'Normal', 'Unexpected status')
        
    def testSubtype(self):
        '''
        Test whether the correct subtype is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].subtype, 'X10 security door/window sensor', 'Unexpected subtype')

    def testBatteryLevel(self):
        '''
        Test whether the correct battery level is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].battery_level, 'OK', 'Unexpected battery level')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()