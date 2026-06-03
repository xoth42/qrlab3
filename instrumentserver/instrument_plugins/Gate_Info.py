from instrumentserver.instrument_plugins.Pulse_Info import Pulse_Info
from instrumentserver.instrument import Instrument

ROTATIONS = (
    'Gaussian',
    'GaussianSquare',
    'Square',
    'Triangle',
    'Sinc',
    'Hanning',
    'Kaiser',
    'FlatTop',
    'OCT',
)

class Gate_Info(Pulse_Info):

    def __init__(self, name, **kwargs):
        super(Gate_Info, self).__init__(name, tags=['virtual'], **kwargs)

        self.add_parameter('deltaf', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                units='Hz')
        self.add_parameter('sideband_period', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('sideband_phase', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('sideband_phase2', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('channels', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='One pair of physical channels'
                )
        self.add_parameter('channels2', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='Second pair of physical channels'
                )
        self.add_parameter('sideband_channels', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='One pair of virtual channels'
                )
        self.add_parameter('sideband_channels2', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='Second pair of virtual channels'
                )
        self.add_parameter('relative_amp', type=float,
			  flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
		       set_func=lambda x: True,
		       doc='Scaling amplitude played between the two drives'
			  )
        self.add_parameter('relative_phase', type=float,
			  flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
		       set_func=lambda x: True,
		       doc='Phase difference played between the two drives'
			  )
        self.add_parameter('rotation', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=ROTATIONS,
                set_func=lambda x: True, value='Gaussian')
        self.add_parameter('chop', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=4,
                doc='Gaussian truncation number')
        self.add_parameter('w', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=10,
                doc='For Gaussian rotations sigma'
                )
        self.add_parameter('sq_len', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='For GaussianSquare rotations the square length'
                )

        self.add_parameter('pi_amp', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=1.0,
                doc='''The amplitude for a pi pulse. If pi/2 amp is specified
                as well a quadratic interpolation will be performed''',
                )

        self.add_parameter('pi2_amp', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='The amplitude for a pi/2 pulse',
                )

        self.add_parameter('drag', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='''The drag parameter, specifies which fraction of the
                derivative should be added to the other quadrature''',
                )

        self.add_parameter('marker_channel', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value='',
                set_func=lambda x: True,
                doc='Marker channel for activity')
        self.add_parameter('marker_ofs', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value=0,
                set_func=lambda x: True,
                doc='Marker offset before activity',
                )
        self.add_parameter('marker_bufwidth', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value=10,
                set_func=lambda x: True,
                doc='Marker buffer width',
                )
        self.add_rotation_parameters(suffix='')
        self.set(kwargs)
