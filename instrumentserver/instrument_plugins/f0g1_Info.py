from instrument import Instrument
import types

class f0g1_Info(Instrument):

    def __init__(self, name, **kwargs):
        Instrument.__init__(self, name, tags=['virtual'])
        
        

#        self.add_parameter('pump_frequency', type=types.FloatType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_GET)
#        self.add_parameter('pump_power', type=types.FloatType,
#               flags=Instrument.FLAG_SET|Instrument.FLAG_GET)
        self.add_parameter('sideband_amp', type=types.FloatType,
               flags=Instrument.FLAG_GETSET)
        self.add_parameter('pump_time', type=types.FloatType,
               flags=Instrument.FLAG_GETSET)
        self.add_parameter('pump_chan', type=types.StringType,
               flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
               set_func=lambda x: True)
#        self.add_parameter('ef_info_name', type=types.StringType,
#               flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#               set_func=lambda x: True)
#        self.add_parameter('pump_name', type=types.StringType,
#               flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#               set_func=lambda x: True)


        self.set(kwargs)

    def do_get_sideband_amp(self):
        return self.sideband_amp
    
    def do_get_pump_time(self):
        return self.pump_time
    
    def do_set_sideband_amp(self, value):
        self.sideband_amp = value
    
    def do_set_pump_time(self, value):
        self.pump_time = value