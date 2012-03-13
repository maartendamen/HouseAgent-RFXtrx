import unittest
from rfxtrx import RFXtrxProtocol

response = ['\x07', '\x10', '\x01', '\x88', 'M', '\x02', '\x01', '`']
# [LightingDevice] id: 'M2', type: 'LIGHTING', subtype: 'ARC', unit: None, command: 'On', rssi: 6

class Test(unittest.TestCase):

    def setUp(self):
        self.protocol = RFXtrxProtocol(None, None)
        self.protocol._handle_lighting_response(response[2:])
        
    def testSubtype(self):
        '''
        Test whether the correct subtype is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].subtype, 'ARC', 'Unexpected subtype')
    
    def testUnit(self):
        '''
        Test whether the correct unit code is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].unit, None, 'Unexpected unit')
        
    def testCommand(self):
        '''
        Test whether the correct command is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].command, 'On', 'Unexpected command')
        
    def testId(self):
        '''
        Test whether the correct id is parsed.
        '''        
        self.assertEqual(self.protocol._devices[0].id, 'M2', 'Unexpected ID')

if __name__ == "__main__":
    unittest.main()