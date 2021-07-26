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
    'DetunedGaussian',
)

class Pulse_Info(Instrument):

    def __init__(self, name, **kwargs):
        Instrument.__init__(self, name, tags=['virtual'])
        self.add_parameter('deltaf', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                units='Hz')
        self.add_parameter('sideband_period', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('sideband_phase', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('channels', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='The physical channel this qubit should be in'
                )
        # markers
        self.add_parameter('marker_channel', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value='',
                set_func=lambda x: True,
                doc='Marker channel for activity',
                gui_group='markers'
                )
        self.add_parameter('marker_ofs', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value=8,
                set_func=lambda x: True,
                doc='Marker offset with respect to activity, 0 = start simultaneously',
                gui_group='markers'
                )
        self.add_parameter('marker_bufwidth', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value=4,
                set_func=lambda x: True,
                doc='Marker buffer width, total buffer = activity + bufwidth',
                gui_group='markers'
                )

        # rotation parameters
        # self.add_rotation_parameters(suffix='')

        self.set(kwargs)

    def do_set_deltaf(self, val, calc=True):
        if not calc:
            return

        if val == 0:
            period = 1e50

        else:
            period = 1e9 / val
        self.set_sideband_period(period, calc=False)

    def do_set_sideband_period(self, val, calc=True):
        if not calc:
            return
        if val == 0:    # This shouldn't occur for period...
            deltaf = 1e50
        else:
            deltaf = 1e9 / val
        self.set_deltaf(deltaf, calc=False)

    def add_rotation_parameters(self, suffix='', rotations=ROTATIONS):
        self.add_parameter('sideband_channels'+suffix, type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='The sequencing channel for this qubit, sideband modulation will let it end up in the physical channels.',
                gui_group='rotation'+suffix
                )
        self.add_parameter('rotation'+suffix, type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=rotations,
                set_func=lambda x: True, value='Gaussian',
                gui_group='rotation'+suffix,
                )
        self.add_parameter('w'+suffix, type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=10,
                doc='For Gaussian rotations sigma, for others the pulse width',
                gui_group='rotation'+suffix,
                )
        self.add_parameter('pi_amp'+suffix, type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=1.0,
                doc='''The amplitude for a pi pulse. If pi/2 amp is specified
                as well a quadratic interpolation will be performed''',
                gui_group='rotation'+suffix,
                )
        self.add_parameter('pi2_amp'+suffix, type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='The amplitude for a pi/2 pulse',
                gui_group='rotation'+suffix,
                )
        self.add_parameter('drag'+suffix, type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='''The drag parameter, specifies which fraction of the
                derivative should be added to the other quadrature''',
                gui_group='rotation'+suffix,
                )
        self.add_parameter('oct_filepath'+suffix, type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='',
                gui_group='rotation'+suffix,
                )

