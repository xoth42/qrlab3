from Pulse_Info import Pulse_Info
from instrument import Instrument
import types

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

        self.add_parameter('deltaf', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                units='Hz')
        self.add_parameter('sideband_period', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('sideband_phase', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('sideband_phase2', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('channels', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='One pair of physical channels'
                )
        self.add_parameter('channels2', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='Second pair of physical channels'
                )
        self.add_parameter('sideband_channels', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='One pair of virtual channels'
                )
        self.add_parameter('sideband_channels2', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='Second pair of virtual channels'
                )
        self.add_parameter('relative_amp', type=types.FloatType,
			  flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
		       set_func=lambda x: True,
		       doc='Scaling amplitude played between the two drives'
			  )
        self.add_parameter('relative_phase', type=types.FloatType,
			  flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
		       set_func=lambda x: True,
		       doc='Phase difference played between the two drives'
			  )
        self.add_parameter('rotation', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=ROTATIONS,
                set_func=lambda x: True, value='Gaussian')

        self.add_parameter('w', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=10,
                doc='For Gaussian rotations sigma'
                )
        self.add_parameter('sq_len', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='For GaussianSquare rotations the square length'
                )

        self.add_parameter('pi_amp', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=1.0,
                doc='''The amplitude for a pi pulse. If pi/2 amp is specified
                as well a quadratic interpolation will be performed''',
                )

        self.add_parameter('pi2_amp', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='The amplitude for a pi/2 pulse',
                )

        self.add_parameter('drag', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='''The drag parameter, specifies which fraction of the
                derivative should be added to the other quadrature''',
                )

        self.add_parameter('marker_channel', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value='',
                set_func=lambda x: True,
                doc='Marker channel for activity')
        self.add_parameter('marker_ofs', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value=0,
                set_func=lambda x: True,
                doc='Marker offset before activity',
                )
        self.add_parameter('marker_bufwidth', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value=10,
                set_func=lambda x: True,
                doc='Marker buffer width',
                )
        self.add_rotation_parameters(suffix='')
        self.set(kwargs)
