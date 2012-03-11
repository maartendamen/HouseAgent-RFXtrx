#-*- coding: utf-8 -*-
from twisted.internet import protocol, defer
import ConfigParser
import os
from houseagent.plugins import pluginapi
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from houseagent.plugins.pluginapi import Logging
from houseagent import config_to_location

class RFXtrxGlobals():
    '''
    This class defines static constants used within the code.
    '''
    TRANSCEIVER_TYPES = {0x50: '310MHz', 0x51: '315MHz', 0x53: '433.92MHz', 0x55: '868.00MHz',
                         0x56: '868.00MHz FSK', 0x57: '868.30MHz', 0x58: '868.30MHz FSK', 
                         0x59: '868.35MHz', 0x5A: '868.35MHz FSK', 0x5B: '868.95MH'}
    
    LIGHTING_TYPES = {0x00: 'X10 lighting', 0x01: 'ARC', 0x02: 'ELRO AB400D', 0x03: 'Waveman',
                      0x04: 'Chacon EMW200', 0x05: 'IMPULS'}
    LIGHTING_COMMANDS = {0x00: 'Off', 0x01: 'On', 0x02: 'Dim', 0x03: 'Bright', 0x05: 'All/group Off',
                         0x06: 'All/group On', 0x07: 'Chime', 0xFF: 'Illegal command'}
    
    LIGHTING_HOUSECODE = {0x41: 'A', 0x42: 'B', 0x43: 'C', 0x44: 'D', 0x45: 'E', 0x46: 'F', 0x47: 'G',
                          0x48: 'H', 0x49: 'I', 0x4A: 'J', 0x4B: 'K', 0x4C: 'L', 0x4D: 'M', 0x4E: 'N',
                          0x4F: 'O', 0x50: 'P'}
    
    LIGHTING2_TYPES = {0x00: 'AC', 0x01: 'HomeEasy EU', 0x02: 'ANSLUT'}
    LIGHTING2_COMMANDS = {0x00: 'Off', 0x01: 'On', 0x02: 'Set level', 0x03: 'Group off', 0x04: 'Group on', 0x05: 'Set group level'}

    SECURITY1_TYPES = {0x00: 'X10 security door/window sensor', 0x01: 'X10 security motion sensor',
                       0x02: 'X10 security remote (no alive packets)', 0x03: 'KD101 (no alive packets)',
                       0x04: 'Visonic PowerCode door/window sensor � primary contact (with alive packets)',
                       0x05: 'Visonic PowerCode motion sensor (with alive packets)',
                       0x06: 'Visonic CodeSecure (no alive packets)',
                       0x07: 'Visonic PowerCode door/window sensor � auxiliary contact (no alive packets)'}
    
    SECURITY1_STATUS = {0x00: 'Normal', 0x01: 'Normal Delayed', 0x02: 'Alarm', 0x03: 'Alarm Delayed',
                        0x04: 'Motion', 0x05: 'No Motion', 0x06: 'Panic', 0x07: 'Panic End', 
                        0x08: 'Tamper', 0x09: 'Arm Away', 0x0A: 'Arm Away Delayed',
                        0x0B: 'Arm Home', 0x0C: 'Arm Home Delayed', 0x0D: 'Disarm', 0x10: 'Light Off',
                        0x11: 'Light On', 0x12: 'Light 2 Off', 0x13: 'Light 2 On', 0x14: 'Dark detected',
                        0x15: 'Light Detected', 0x16: 'Battery low MS10 or XX18 sensor', 0x17: 'air KD101'}
    
    TEMPERATURE_TYPES = {0x01: 'THR128/138, THC138', 0x02: 'THC238/268,THN132,THWR288,THRN122,THN122,AW129/131', 0x03: 'THWR800',
                         0x04: 'RTHN318', 0x05: 'La Crosse TX3, TX4, TX17'}
    
    TEMPHUMI_TYPES = {0x01: 'THGN122/123,/THGN132,THGR122/228/238/268', 0x02: 'THGR810', 0x03: 'RTGR328', 0x04: 'THGR328',
                       0x05: 'WTGR800', 0x06: 'THGR918,THGRN228,THGN500', 0x07: 'TFA TS34C'}
    
    HUMIDITY_STATUS = {0x00: 'Dry', 0x01: 'Comfortable', 0x02: 'Normal', 0x03: 'Wet'}
    BAROMETER_FORECAST = {0x00: 'No information available', 0x01: 'Sunny', 0x02: 'Partly Cloudy',
                          0x03: 'Cloudy', 0x04: 'Rain'}
    
    WEIGHT_TYPES = {0x01: 'BWR102', 0x02: 'GR101'}
    RFXMETER_TYPES = {0x00: 'RFXMeter counter'}
    WIND_TYPES = {0x01: 'WTGR800', 0x02: 'WGR800', 0x03: 'STR918, WGR918', 0x04: 'TFA'}
    TEMP_HUM_BARO_TYPES = {0x01: 'BTHR918', 0x02: 'BTHR918N, BTHR968'}
    
class RFXtrxDevice(object):
    '''
    Abstract class to represent a RFXtrxDevice
    '''
    def __init__(self, id, type, subtype, rssi):
        self.id = id
        self.type = type
        self.subtype = subtype
        self.rssi = rssi
    
class LightingDevice(RFXtrxDevice):
    '''
    Abstract class to represent a lighting device (switch, dimmer etc.)
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
        self.unit = None
        self.command = None
    
    def __repr__(self):
        return '[LightingDevice] id: %r, type: %r, subtype: %r, unit: %r, command: %r, rssi: %r' % (self.id, self.type, self.subtype, self.unit, 
                                                                                                    self.command, self.rssi)   

class TemperatureSensor(object):
    '''
    Abstract class to represent a temperature sensor.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
       
        self.temperature = None
        self.battery_level = None
    
    def __repr__(self):
        return '[TemperatureSensor] id: %r, type: %r, subtype: %r, temperature: %r, battery level: %r, rssi: %r' % (self.id, self.type, 
                                                                                                                    self.subtype, self.temperature, 
                                                                                                                    self.battery_level, self.rssi)

class WeightScale(RFXtrxDevice):
    '''
    This abstract class represents a weight scale.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(id, type, subtype, rssi)
        self.weight = None
        self.battery_level = None
    
    def __repr__(self):
        return '[WeightScale] id: %r, type: %r, subtype: %r, weight: %r, battery level: %r, rssi: %r' % (self.id, self.type, 
                                                                                                          self.subtype, self.weight, 
                                                                                                          self.battery_level, self.rssi)          

class RFXMeter(RFXtrxDevice):
    '''
    Anstract class to represent a RFXMeter device.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
        self.counter = None
        
    def __repr__(self):
        return '[RFXMeter] id: %r, type: %r, subtype: %r, counter: %r, rssi: %r' % (self.id, self.type, self.subtype, self.counter, self.rssi)

class SecurityDevice(RFXtrxDevice):
    '''
    Abstract class to represent a security device.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
        self.status = None
        self.battery_level = None
        
    def __repr__(self):
        return '[SecurityDevice] id: %r, type: %r, subtype: %r, status: %r, battery level: %r rssi: %r' % (self.id, self.type, self.subtype, self.status, self.battery_level, self.rssi)

class TemperatureHumiditySensor(RFXtrxDevice):
    '''
    This abstract class represents a temperature humidity sensor.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
        self.temperature = None
        self.humidity = None
        self.battery_level = None
        self.humidity_status = None
        
    def __repr__(self):
        return '[TemperatureHumiditySensor] id: %r, type: %r, subtype: %r, temperature: %r, humidity: %r, humidity_status: %r, battery_level: %r rssi: %r' % (self.id, self.type, self.subtype, self.temperature, self.humidity, self.humidity_status, self.battery_level, self.rssi)

class TemperatureHumidityBarometerSensor(RFXtrxDevice):
    '''
    This abstract class represents a temperature humidity and barometer sensor.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
        self.temperature = None
        self.humidity = None
        self.battery = None
        self.humidity_status = None
        self.barometer = None
        self.forecast = None
        
    def __repr__(self):
        return '[TemperatureHumidityBarometerSensor] id: %r, type: %r, subtype: %r, temperature: %r, humidity: %r, humidity_status: %r, barometer: %r, forecast: %r, battery: %r, rssi: %r' % (self.id, self.type, self.subtype, self.temperature, self.humidity, self.humidity_status, self.barometer, self.forecast, self.battery, self.rssi)


class WindSensor(RFXtrxDevice):
    '''
    This abstract class represents a wind sensor.
    '''
    def __init__(self, id, type, subtype, rssi):
        RFXtrxDevice.__init__(self, id, type, subtype, rssi)
        self.direction = None
        self.average_speed = None
        self.gust = None
        self.battery = None
    
    def __repr__(self):
        return '[WindSensor] id: %r, type: %r, subtype: %r, direction: %r, average speed: %r, wind gust: %r, battery: %r, rssi: %r' % (self.id, self.type, self.subtype, 
                                                                                                                                       self.direction, self.average_speed, self.gust,
                                                                                                                                       self.battery, self.rssi)    

class RFXTranceiver(object):
    '''
    Abstract class to represent the RFX transceiver
    '''
    def __init__(self, type, firmware):
        
        self.type = type
        self.firmware = firmware
        
        self.undecoded = False
        self.proguard = False
        self.fs20 = False
        self.lacrosse = False
        self.hideki = False
        self.lightwaverf = False
        self.mertik = False
        
        self.visonic = False
        self.ati = False
        self.oregon = False
        self.ikeakoppla = False
        self.home_easy = False
        self.ac = False
        self.arc = False
        self.x10 = False     
        
    def __repr__(self):
        return '[RFXtrxTransceiver] Display undecoded packets: %r, Proguard: %r, FS20: %r, La Crosse: %r, Hideki: %r, LightwaveRF: %r, Mertik: %r '  \
               'Visonic: %r, ATI: %r, Oregon Scientific: %r, Ikea-Koppla: %r, HomeEasy EU: %r, AC: %r, ARC: %r, X10: %r' % \
                (self.undecoded, self.proguard, self.fs20, self.lacrosse, self.hideki, self.lightwaverf, self.mertik, self.visonic,
                 self.ati, self.oregon, self.ikeakoppla, self.home_easy, self.ac, self.arc, self.x10)

class RFXtrxProtocol(protocol.Protocol):
    '''
    The class that handles the RFXtrx protocol.
    '''
    def __init__(self, wrapper, log):
        self.packet_length = 0
        self.payload = []
        self._lighting_devices = []
        self._devices = []
        self._wrapper = wrapper
        self._log = log
           
    def dataReceived(self, data):
        '''
        Function to handle incoming serial data.
        @param data: the data to handle.
        '''
        
        self.payload += data        
        if len(self.payload) == ord(self.payload[0]) + 1:
            self._log.debug('Received full packet response:%r' % (self.payload))
            self._handle_response(self.payload[1:])
            self.payload = []
    
    def connectionMade(self):
        '''
        This function is called when a serial connection has been made.
        '''
        self._log.debug('Serial connection made, sending reset sequence to RFXtrx...')
        self._reset()
        
    def _handle_response(self, response):
        '''
        Function called when a response has to be handled.
        @param response: the response to handle.
        '''
        
        response_type = ord(response[0])
        
        # Interface response
        if response_type == 0x01:
            self._handle_interface_status_response(response[1:])
        
        # LIGHTING
        elif response_type == 0x10:
            self._handle_lighting_response(response[1:])
        
        # LIGHTING2
        elif response_type == 0x11:
            self._handle_lighting2_response(response[1:])
        
        # SECURITY1
        elif response_type == 0x20:
            self._handle_security1_response(response[1:])
        
        # TEMPERATURE
        elif response_type == 0x50:
            self._handle_temperature_response(response[1:])
        
        # TEMP_HUMI
        elif response_type == 0x52:
            self._handle_temphumi_response(response[1:])
        
        # TEMP_HUM_BARO
        elif response_type == 0x54:
            self._handle_temp_hum_baro(response[1:])
        
        # WIND
        elif response_type == 0x56:
            self._handle_wind_response(response[1:])
        
        # WEIGHT
        elif response_type == 0x5D:
            self._handle_weight_response(response[1:])
        
        # RFXMETER
        elif response_type == 0x71:
            self._handle_rfxmeter_response(response[1:])
        else:
            self._log.debug('Unsupported response received: %r, please report to the HouseAgent team!' % (response_type))

    def _handle_temp_hum_baro(self, response):
        '''
        Handle temperature humidity and barometric response (0x54)
        @param response: the receiver response
        '''
        type = 'TEMP_HUM_BARO'
        subtype = RFXtrxGlobals.TEMP_HUM_BARO_TYPES[ord(response[0])]
        id = ord(response[2]) * 256 + ord(response[3])

        if ord(response[4]) & 0x80 == 0:
            temperature = "%2.1f" % (ord(response[4]) * 256.0 + ord(response[5]) / 10.0)
        else:
            temperature = "-%2.1f" % (ord(response[4]) & 0x7F * 256.0 + ord(response[5]) / 10.0)
            
        humidity = ord(response[6])
        #humidity_status = RFXtrxGlobals.HUMIDITY_STATUS[ord(response[7])]
        
        barometer = ord(response[8]) * 256 + ord(response[9])
        forecast = RFXtrxGlobals.BAROMETER_FORECAST[ord(response[10])]
        
        rssi = ord(response[11]) >> 4
        
        if ord(response[11]) & 0xF == 0:
            battery = 'Low'
        else:
            battery = 'Ok'
            
        device = self._device_exists(id, type)
        
        if not device:
            device = TemperatureHumidityBarometerSensor(id, type, subtype, rssi)
            self._devices.append(device)
            
        device.temperature = temperature
        device.humidity = humidity
        #device.humidity_status = humidity_status
        device.barometer = barometer
        device.forecast = forecast
        device.rssi = rssi
        device.battery = battery

        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Temperature': str(temperature), 'Humidity': str(humidity), 'Barometer': str(barometer),
                  'Forecast': str(forecast), 'Battery': str(battery)}
        self._report(id, values)

    def _handle_wind_response(self, response):
        '''
        Handle wind response type (0x56)
        @param response: the receiver response
        '''
        
        type = 'WIND'
        subtype = RFXtrxGlobals.WIND_TYPES[ord(response[0])]
        id = ord(response[2]) * 256 + ord(response[3])
        direction = ord(response[4]) * 256 + ord(response[5])
        average_speed = ord(response[6]) * 256.0 + ord(response[7]) / 10.0
        gust = ord(response[8]) * 256.0 + ord(response[9]) / 10.0
        
        if ord(response[0]) == 0x03:
            battery_level = ord(response[14]) + 1 * 10   
        else:
            if ord(response[14]) & 0xF == 0:
                battery_level = 'Low'
            else:
                battery_level = 'OK'
        
        rssi = ord(response[14]) >> 4
                
        device = self._device_exists(id, type)
        
        if not device:
            device = WindSensor(id, type, subtype, rssi)
            self._devices.append(device)
            
        device.direction = direction
        device.average_speed = average_speed
        device.gust = gust
        device.battery = battery_level

        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Direction': str(direction), 'Average speed': str(average_speed), 'Gust': str(gust),
                  'Battery': str(battery_level)}
        self._report(id, values)

    def _handle_security1_response(self, response):
        '''
        This function handles a security device response.
        @param response: the response to handle.
        '''
        
        type = 'SECURITY1'
        subtype = RFXtrxGlobals.SECURITY1_TYPES[ord(response[0])]
        id = "%01d%02X%02X" % (ord(response[2]), ord(response[3]), ord(response[4]))
        status = RFXtrxGlobals.SECURITY1_STATUS[ord(response[5])]
        
        if (ord(response[6]) & 0xF == 0):
            battery_level = 'Low'
        else:
            battery_level = 'OK'
        
        rssi = ord(response[6]) >> 4
        
        device = self._device_exists(id, type)
        
        if not device:
            device = SecurityDevice(id, type, subtype, rssi)
            self._devices.append(device)
        
        device.status = status
        device.battery_level = battery_level
        
        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Status': str(status), 'Battery level': str(battery_level)}
        self._report(id, values)
            
    def _handle_rfxmeter_response(self, response):
        '''
        This function handles a rfxmeter response.
        @param response: the response to handle.
        '''
        
        type = 'RFXMETER'
        subtype = RFXtrxGlobals.RFXMETER_TYPES[ord(response[0])]
        id = ord(response[2]) * 256 + ord(response[3])
        counter = (ord(response[4]) << 24) + (ord(response[5]) << 16) + (ord(response[6]) << 8) + ord(response[7])
        rssi = ord(response[8]) >> 4        
        
        device = self._device_exists(id, type)
        
        if not device:
            device = RFXMeter(id, type, subtype, rssi)
            self._devices.append(device)
        
        device.rssi = rssi
        device.counter = counter
        
        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Counter': str(counter)}
        self._report(id, values)        
            
    def _handle_temphumi_response(self, response):
        '''
        This function handles a temperature/humidity sensor response.
        @param response: the response to handle.
        '''
        
        type = 'TEMP_HUM'
        subtype = RFXtrxGlobals.TEMPHUMI_TYPES[ord(response[0])]
        id = ord(response[2]) * 256 + ord(response[3])
        
        if ord(response[4]) & 0x80 == 0:
            temperature = "%2.2f" % (ord(response[4]) * 256.0 + ord(response[5]) / 10.0)
        else:
            temperature = "-%2.2f" % (ord(response[4]) & 0x7F * 256.0 + ord(response[5]) / 10.0)
            
        humidity = ord(response[6])
        humidity_status = RFXtrxGlobals.HUMIDITY_STATUS[ord(response[7])]
        rssi = ord(response[8]) >> 4
        
        if subtype == RFXtrxGlobals.TEMPHUMI_TYPES[0x06]:
            battery_level = ord(response[8]) + 1 * 10
        else:
            if ord(response[8]) & 0xF == 0:
                battery_level = 'Low'
            else:
                battery_level = 'Ok'
                
        device = self._device_exists(id, type)
        
        if not device:
            device = TemperatureHumiditySensor(id, type, subtype, rssi)
            self._devices.append(device)
        
        device.temperature = temperature
        device.humidity = humidity
        device.rssi = rssi
        device.battery_level = battery_level
        device.humidity_status = humidity_status
        
        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Temperature': str(temperature), 'Humidity': str(humidity), 'Humidity status': humidity_status,
                  'Battery': battery_level}
        self._report(id, values)          
            
    def _handle_weight_response(self, response):
        '''
        This function handles a weight scale response.
        @param response: the response the handle
        '''        
        type = 'WEIGHT'
        subtype = RFXtrxGlobals.WEIGHT_TYPES[ord(response[0])]
        id = ord(response[2]) * 256 + ord(response[3])
        weight = response[4] * 25.6 + response[5] / 10
        rssi = ord(response[6]) >> 4
        battery_level = response[6] & 0xF
        
        device = self._device_exists(id, type)
        
        if not device:
            device = WeightScale(id, type, subtype, rssi)
            self._devices.append(device)
        
        device.weight = weight
        device.battery_level = battery_level
        device.rssi = rssi
        
    def _handle_lighting_response(self, response):
        '''
        Handle lighting1 response type
        @param response: the receiver response
        '''
        
        type = 'LIGHTING'
        subtype = RFXtrxGlobals.LIGHTING_TYPES[ord(response[0])]
        housecode = RFXtrxGlobals.LIGHTING_HOUSECODE[ord(response[2])]
        unitcode = ord(response[3])
        command = RFXtrxGlobals.LIGHTING_COMMANDS[ord(response[4])]
        rssi = ord(response[5]) >> 4
        
        id = '%s%d' % (housecode, unitcode)
        
        device = self._device_exists(id, type)
        
        if not device:
            device = LightingDevice(id, type, subtype)
            self._devices.append(device)
            
        device.command = command
        device.rssi = rssi
        
        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Status': str(command)}
        self._report(id, values)            
            
    def _handle_lighting2_response(self, response):
        '''
        Handle lighting2 response type (0x11)
        Protocols supported: AC, HomeEasy EU, ANSLUT
        @param response: the receiver response
        '''

        type = 'LIGHTING2'
        subtype = RFXtrxGlobals.LIGHTING2_TYPES[ord(response[0])]
        id = "%01d%02X%02X%02X" % (ord(response[2]), ord(response[3]), ord(response[4]), ord(response[5]))
        unit = ord(response[6])
        command = RFXtrxGlobals.LIGHTING2_COMMANDS[ord(response[7])]
        rssi = ord(response[9]) >> 4

        device = self._device_exists(id, type)
        
        if not device:
            device = LightingDevice(id, type, subtype, rssi)
            self._devices.append(device)

        device.unit = unit
        device.command = command
        device.rssi = rssi
        
        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Status': str(command)}
        self._report(id, values)
            
    def _handle_temperature_response(self, response):
        '''
        Handle temperature sensor response type (0x50)
        @param response: the receiver response
        '''
        
        type = 'TEMPERATURE'
        subtype = RFXtrxGlobals.TEMPERATURE_TYPES[ord(response[0])]
        id = ord(response[2]) * 256 + ord(response[3])
        
        if ord(response[4]) & 0x80 == 0:
            temperature = "%2.2f" % (ord(response[4]) * 256.0 + ord(response[5]) / 10.0)
        else:
            temperature = "-%2.2f" % (ord(response[4]) & 0x7F * 256.0 + ord(response[5]) / 10.0)
            
        rssi = ord(response[6]) >> 4
        battery_level = ord(response[6]) & 0xF
        
        device = self._device_exists(id, type)
        
        if not device:
            device = TemperatureSensor(id, type, subtype)
            self._devices.append(device)
        
        device.temperature = temperature
        device.rssi = rssi
        device.battery_level = battery_level
        
        self._log.debug('Handled response: %r' % device)
        
        # Report to master broker
        values = {'Temperature': str(temperature), 'Battery': battery_level}
        self._report(id, values)           
        
    def _device_exists(self, id, type):
        '''
        Helper function to check whether a device exists in the device list.
        @param id: the id of the device
        @param type: the type of the device
        '''
        for device in self._devices:
            if device.id == id and device.type == type:
                return device
            
        return False
        
    def _handle_interface_status_response(self, response):
        '''
        Function to handle interface status response.
        @param response: the response to handle
        '''
        transceiver_type = RFXtrxGlobals.TRANSCEIVER_TYPES[ord(response[3])]
        firmware_version = ord(response[4])
        
        transceiver = RFXTranceiver(transceiver_type, firmware_version)
        
        # Determine enabled protocols
        transceiver.undecoded = bool(ord(response[5]) & 0x80)
        transceiver.proguard = bool(ord(response[6]) & 0x20)
        transceiver.fs20 = bool(ord(response[6]) & 0x10)
        transceiver.lacrosse = bool(ord(response[6]) & 0x08)
        transceiver.hideki = bool(ord(response[6]) & 0x04)
        transceiver.lightwaverf = bool(ord(response[6]) & 0x02)
        transceiver.mertik = bool(ord(response[6]) & 0x01)

        transceiver.visonic = bool(ord(response[7]) & 0x80)
        transceiver.ati = bool(ord(response[7]) & 0x40)
        transceiver.oregon = bool(ord(response[7]) & 0x20)
        transceiver.ikeakoppla = bool(ord(response[7]) & 0x10)
        transceiver.home_easy = bool(ord(response[7]) & 0x08)
        transceiver.ac = bool(ord(response[7]) & 0x04)
        transceiver.arc = bool(ord(response[7]) & 0x02)
        transceiver.x10 = bool(ord(response[7]) & 0x01)
        
        self._log.debug('Transceiver status response received: %r' % (transceiver))
        
        # Set plugin as ready
        self._wrapper.pluginapi.ready()
        
    def _reset(self):
        '''
        Send a reset command to RFXtrx.
        '''
        self.transport.write('\x0D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        reactor.callLater(0.06, self._get_status) # get status at least 50ms later, 60ms in this case
    
    def _get_status(self):
        '''
        Send's a command to get the current RFXtrx status.
        '''
        self.transport.write('\x0D\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    def _report(self, id, values):
        '''
        Helper function that reports the supplied values to the master broker.
        
        @param id: the address/id of the device
        @param values: values to be reported.
        '''
        if self._wrapper:
            self._wrapper.pluginapi.value_update(id, values)

class RFXtrxWrapper(object):

    def __init__(self):
        '''
        Load initial RFXtrx configuration from rfxtrx.conf
        '''   
        config_file = config_to_location('rfxtrx.conf')
        
        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(config_file))
        self.port = config.get("serial", "port")

        # Get broker information (ZeroMQ)
        self.coordinator_host = config.get("coordinator", "host")
        self.coordinator_port = config.getint("coordinator", "port")
        
        self.loglevel = config.get('general', 'loglevel')
        self.id = config.get('general', 'id')

        callbacks = {'custom': self.cb_custom}
        self.pluginapi = pluginapi.PluginAPI(self.id, 'RFXtrx', 
                                             broker_host=self.coordinator_host, 
                                             broker_port=self.coordinator_port, **callbacks)
        
        log = Logging("RFXtrx", console=True)
        log.set_level(self.loglevel)
        
        self.protocol = RFXtrxProtocol(self, log) 
        myserial = SerialPort (self.protocol, self.port, reactor)
        myserial.setBaudRate(38400)
        reactor.run(installSignalHandlers=0)
        return True
    
    def cb_custom(self, action, parameters):
        '''
        This function is a callback handler for custom commands
        received from the coordinator.
        @param action: the custom action to handle
        @param parameters: the parameters passed with the custom action
        '''    
        if action == 'get_devices':
            devices = {}
            for dev in self.protocol._devices:
                devices[dev.id] = [dev.type, dev.subtype, dev.rssi]
            d = defer.Deferred()
            d.callback(devices)
            return d
    
if os.name == 'nt':        
    class RFXtrxService(pluginapi.WindowsService):
        '''
        This class provides a Windows Service interface for the RFXtrx plugin.
        '''
        _svc_name_ = "harfxtrx"
        _svc_display_name_ = "HouseAgent - RFXtrx Service"
        
        def start(self):
            '''
            Start the Zwave interface.
            '''
            RFXtrxWrapper()
        
if __name__ == '__main__':
    if os.name == 'nt':
        pluginapi.handle_windowsservice(RFXtrxService) # We want to start as a Windows service on Windows.
    else:
        RFXtrxWrapper()