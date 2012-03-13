import unittest
from rfxtrx import RFXtrxProtocol

# This is a WTGR800 sensor
response = ['\x10','\x56','\x01','\x03','\x2F', '\x00', '\x00', '\xF7', '\x00', '\x20', '\x00', '\x24', '\x01', '\x60', '\x00', '\x00', '\x59']

class Test(unittest.TestCase):

    def setUp(self):
        self.protocol = RFXtrxProtocol(None, None)
        self.protocol._handle_wind_response(response[2:])

    def testID(self):
        '''
        Test whether the correct ID is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].id, 12032, 'Unexpected ID')

    def testSubtype(self):
        '''
        Test whether the correct subtype is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].subtype, 'WTGR800', 'Unexpected subtype')
        
    def testDirection(self):
        '''
        Test whether the correct direction is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].direction, 247 , 'Unexpected direction')
        
    def testAverageSpeed(self):
        '''
        Test whether the correct average speed is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].average_speed, 3.2 , 'Unexpected average speed')
        
    def testWindGust(self):
        '''
        Test whether the correct wind gust is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].gust, 3.6 , 'Unexpected wind gust')
        
    def testBattery(self):
        '''
        Test whether the correct battery level is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].battery, 'OK' , 'Unexpected battery level')                

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()