from .Pulse_Info import Pulse_Info
from .instrument import Instrument
import types

ROTATIONS = (
    'Marker',
    'Square',
    'Overdrive',
)

class ReadoutPulse_Info(Pulse_Info):

    def __init__(self, name, **kwargs):
        super(ReadoutPulse_Info, self).__init__(name, tags=['virtual'], **kwargs)

        self.add_parameter('sideband_channels', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='The sequencing channel for this qubit, sideband modulation will let it end up in the physical channels.',
                gui_group='readout',
                )
        self.add_parameter('rotation', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=ROTATIONS,
                set_func=lambda x: True, value='Square',
                gui_group='readout',
                )
        self.add_parameter('w', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=2000,
                doc='length of readout pulse in ns',
                gui_group='readout',
                )
        self.add_parameter('amp', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0.5,
                doc='amplitude of readout pulse',
                gui_group='readout',
                )
        self.add_parameter('tau', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=100,
                doc='The decay time for the overdrive pulse',
                gui_group='readout',
                )
        self.add_parameter('amp1', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0.5,
                doc='The amplitude for the emptying displacement for an OD pulse',
                gui_group='readout',
                )
        self.add_parameter('tau1', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=100,
                doc='The decay time for the emptying displacement for an OD pulse',
                gui_group='readout',
                )
        self.add_parameter('w1', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=1000,
                doc='The length for the emptying displacement for an OD pulse',
                gui_group='readout',
                )

        self.add_parameter('ofs', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0.25,
                doc='The length for the emptying displacement for an OD pulse',
                gui_group='readout',
                )

        self.set(kwargs)
