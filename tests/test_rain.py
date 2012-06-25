import unittest
from rfxtrx import RFXtrxProtocol

# This is a WTGR800 sensor
response = ['\x0b', 'U', '\x01', '\x14', 'r', '\x00', '\x00', '\x00', '\x00', '*', 'b', 'h']

class Test(unittest.TestCase):

    def setUp(self):
        self.protocol = RFXtrxProtocol(None, None)
        self.protocol._handle_rain(response[2:])

    def testID(self):
        '''
        Test whether the correct ID is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].id, 29184, 'Unexpected ID')
        
    def testSubtype(self):
        '''
        Test whether the correct subtype is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].subtype, 'RGR126/682/918', 'Unexpected subtype')
        
    def testRainrate(self):
        '''
        Test whether the correct rain rate is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].rain_rate, 0, 'Incorrect rain rate')
        
    def testTotalrain(self):
        '''
        Test whether the correct amount of total rain is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].total_rain, 10850, 'Incorrect total rain')
        
    def testBattery(self):
        '''
        Test whether the correct battery status is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].battery, 'Ok', 'Incorrect battery status')
        
    def testRSSI(self):
        '''
        Test whether the correct RSSI is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].rssi, 6, 'Incorrect RSSI')
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()