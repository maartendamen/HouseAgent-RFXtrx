import unittest
from rfxtrx import RFXtrxProtocol

response = ['\x0b', '\x11', '\x01', '\x00', '\x00', '\x08', '\x15', '\xe2', '\x0b', '\x01', '\x0f', 'P']
response2 = ['\x0b', '\x11', '\x00', '|', '\x00', '\x16', '\xae', '*', '\x0c', '\x01', '\x0f', '`']

class Test(unittest.TestCase):

    def setUp(self):
        self.protocol = RFXtrxProtocol(None)
        self.protocol._handle_lighting2_response(response[2:])
        self.protocol._handle_lighting2_response(response2[2:])
        
    def testSubtype(self):
        '''
        Test whether the correct subtype is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].subtype, 'HomeEasy EU', 'Unexpected subtype')
        self.assertEqual(self.protocol._devices[1].subtype, 'AC', 'Unexpected subtype')
    
    def testUnit(self):
        '''
        Test whether the correct unit code is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].unit, 11, 'Unexpected unit')
        self.assertEqual(self.protocol._devices[1].unit, 12, 'Unexpected unit')
        
    def testCommand(self):
        '''
        Test whether the correct command is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].command, 'On', 'Unexpected command')
        self.assertEqual(self.protocol._devices[1].command, 'On', 'Unexpected command')
        
    def testId(self):
        '''
        Test whether the correct id is parsed.
        '''        
        self.assertEqual(self.protocol._devices[0].id, '00815E2', 'Unexpected ID')
        self.assertEqual(self.protocol._devices[1].id, '016AE2A', 'Unexpected ID')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()