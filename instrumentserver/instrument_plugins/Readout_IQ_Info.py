from instrument import Instrument
import types
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from Qubit_Info import Qubit_Info
import numpy as np

class Readout_IQ_Info(Qubit_Info):

    def __init__(self, name, **kwargs):
        super(Readout_IQ_Info, self).__init__(name, **kwargs)

        self.add_parameter('rotype', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=('High-power', 'Dispersive'),
                help='Read-out type to use')
        self.add_parameter('rfsource', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='RF-source for read-out pulse')
        self.add_parameter('power', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('frequency', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_GET)
        self.add_parameter('IQg', type=types.ComplexType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ point of g')
        self.add_parameter('IQe', type=types.ComplexType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ point of e')
        self.add_parameter('IQe_radius', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ radius threshold for e state')
        self.add_parameter('threshold_pt', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='projected threshold for g/e discrimination')
        self.add_parameter('acq_chan', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('acq_len', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='Acquisition length for FPGA',
                set_func=lambda x: True, value=3000)
        self.add_parameter('ref_len', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='Reference length for FPGA',
                set_func=lambda x: True, value=500)
        self.add_parameter('naverages', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='# averages for FPGA',
                set_func=lambda x: True, value=500)
        self.add_parameter('envelope', type=types.StringType,
                help='Envelope for FPGA',
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value='1')
        self.add_parameter('pulse_width', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='width of Gaussian Square wave',
                set_func=lambda x: True, value=3000)
        self.add_parameter('fixed_phase', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='lab phase of readout signal',
                set_func=lambda x: True, value=0)

        self.set(kwargs)
        
#        bad_parameters = ['w_quasilective',
#                          'power',
#                          'sideband_channels_selective',
#                          'rotation_quasilective',
#                          'ref_len',
#                          'pi_amp_quasilective',
#                          'pi2_amp_quasilective',
#                          'acq_len',
#                          ]
#        for p in bad_parameters:
#            self.remove_parameter(p)

    def do_set_rfsource(self, val):
        srv = self.get_instruments()
        if srv:
            self._ins = srv.get(val)
        else:
            self._ins = None

    def _get_ins(self):
        if self._ins:
            return self._ins
        srv = self.get_instruments()
        if srv:
            self._ins = srv.get(self.get_rfsource())

    def do_get_power(self):
        ins = self._get_ins()
        if ins:
            return ins.get_power()

    def do_set_power(self, val):
        ins = self._get_ins()
        if ins:
            return ins.set_power(val)

    def do_get_frequency(self):
        return 1
    
    def do_set_frequency(self, val):
        ins = self._get_ins()
        if ins:
            return ins.set_frequency(val)

    def do_get_sequence(self, readout_qubit_info, df = 0, phase = 0, amp = None):
        if amp is None: amp = self.get_pi_amp()
        pulse_width = int(self.get_pulse_width())
        w = int(self.get_w())
        g = DetunedGaussSquare(pulse_width, w, chans=readout_qubit_info.sideband_channels)
        if df != 0:
            period = 1e9 / df
        else:
            period = 1e50
        g.add(amp, period, phases = (phase, phase-np.pi/2))
        ro = Combined([
            g(),
            Constant(w * 4 + pulse_width, 1, chan=self.get_acq_chan())])
#        ro = readout_qubit_info.rotate(1, 0)
        return ro