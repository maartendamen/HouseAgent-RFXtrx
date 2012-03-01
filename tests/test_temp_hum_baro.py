import unittest
from rfxtrx import RFXtrxProtocol

# This is a WTGR800 sensor
response = ['\x0D', '\x54', '\x02', '\x01', '\x94', '\x00', '\x00', '\xD0', '\x20', '\x20', '\x03', '\xF4', '\x01', '\x60']

class Test(unittest.TestCase):

    def setUp(self):
        self.protocol = RFXtrxProtocol(None)
        self.protocol._handle_temp_hum_baro(response[2:])
        
    def testSubtype(self):
        '''
        Test whether the correct subtype is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].subtype, 'BTHR918N, BTHR968', 'Invalid subtype')
        
    def testTemperature(self):
        '''
        Test whether the correct temperature is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].temperature, '20.8', 'Invalid temperature')
        
    def testHumidity(self):
        '''
        Test whether the correct humidity is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].humidity, 32, 'Invalid humidity')
    
    def testBarometer(self):
        '''
        Test whether the correct barometer value is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].barometer, 1012, 'Invalid barometer')
        
    def testForecast(self):
        '''
        Test whether the correct forecast value is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].forecast, 'Sunny', 'Invalid forecast')
        
    def testBattery(self):
        '''
        Test whether the correct battery value is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].battery, 'Low', 'Invalid battery')
        
    def testRSSI(self):
        '''
        Test whether the correct RSSI value is parsed.
        '''
        self.assertEqual(self.protocol._devices[0].rssi, 6, 'Invalid RSSI')  

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()