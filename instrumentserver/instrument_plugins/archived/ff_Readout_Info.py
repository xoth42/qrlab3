from .instrument import Instrument
from instrumentserver.instrument_plugins import Readout_Info as ri
import types

class ff_Readout_Info(ri.Readout_Info):

    def __init__(self, name, **kwargs):
        ri.Readout_Info.__init__(self, name, tags=['virtual'])

        self.add_parameter('flux_chan', type=int, #Stringtype for marker chans..
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('pre_flux_len', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('post_flux_len', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('ro_flux_amp', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)

        self.set(kwargs)

