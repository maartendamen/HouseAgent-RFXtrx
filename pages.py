from twisted.web.static import File
import os
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
import json
from mako.lookup import TemplateLookup
from mako.template import Template
from twisted.web import http
from twisted.internet.defer import inlineCallbacks
import sys

def init_pages(web, coordinator, db):
    
    if hasattr(sys, 'frozen'):
        web.putChild("rfxtrx_images", File(os.path.join(os.path.dirname(sys.executable), 'plugins/rfxtrx/templates/images')))
    else:
        web.putChild("rfxtrx_images", File(os.path.join('houseagent/plugins/rfxtrx/templates/images')))
    web.putChild('rfxtrx_devices', RFXtrxDevices(coordinator, db))
    web.putChild('rfxtrx_devices_view', RFXtrxDevicesView(db, coordinator))


class RFXtrxDevicesView(Resource):
    def __init__(self, db, coordinator):
        self.db = db
        self.coordinator = coordinator
        Resource.__init__(self)

    def finished(self, locations):
        
        if hasattr(sys, 'frozen'):
            # Special case when we are frozen.
            lookup = TemplateLookup(directories=[os.path.join(os.path.dirname(sys.executable), 'templates/')])
            template = Template(filename=os.path.join(os.path.dirname(sys.executable), 'plugins/rfxtrx/templates/devices.html'), lookup=lookup)
        else:    
            lookup = TemplateLookup(directories=['houseagent/templates/'])
            template = Template(filename='houseagent/plugins/rfxtrx/templates/devices.html', lookup=lookup)
            
        self.request.write(str(template.render(locations=locations, pluginid=self.pluginid)))
        self.request.finish()
    
    def render_GET(self, request):
        self.request = request
        self.db.query_locations().addCallback(self.finished)
        
        # Uglyness alert!
        plugins = self.coordinator.get_plugins_by_type("RFXtrx")
        if len(plugins) == 0:
            self.request.write(str("No online RFXtrx plugins found..."))
            self.request.finish()
        elif len(plugins) == 1:
            self.pluginguid = plugins[0].guid
            self.pluginid = plugins[0].id
        
        return NOT_DONE_YET    
    
class RFXtrxDevices(Resource):
    def __init__(self, coordinator, db):
        self.coordinator = coordinator
        self.db = db
    
    @inlineCallbacks    
    def result(self, result):
        db_devices = yield self.db.query_devices()
        
        output = []
        for id, data in result.iteritems():
            in_db = False
            
            for db_device in db_devices:
                if db_device[2] == id:
                    in_db = True
            
            dev = {'id': id,
                   'type': data[0],
                   'subtype': data[1],
                   'rssi': data[2], 
                   'database': in_db}
            output.append(dev)
            
        self.request.write(json.dumps(output))
        self.request.finish()
    
    @inlineCallbacks
    def _add(self, parameters):
        address = parameters['address'][0]
        name = parameters['name'][0]
        plugin_id = parameters['plugin_id'][0]
        location_id = parameters['location_id'][0]
        
        done = yield self.db.save_device(name, address, plugin_id, location_id)
        self.request.finish(done)
       
    def render_PUT(self, request):
        self.request = request
        self._add(http.parse_qs(request.content.read(), 1)) # http://twistedmatrix.com/pipermail/twisted-web/2007-March/003338.html
        return NOT_DONE_YET    
    
    def render_GET(self, request):
        self.request = request
        plugins = self.coordinator.get_plugins_by_type("RFXtrx")
        
        if len(plugins) == 0:
            self.request.write(str("No online RFXtrx plugins found..."))
            self.request.finish()
        elif len(plugins) == 1:
            self.pluginguid = plugins[0].guid
            self.pluginid = plugins[0].id
            self.coordinator.send_custom(plugins[0].guid, "get_devices", '').addCallback(self.result)   
                
        return NOT_DONE_YET