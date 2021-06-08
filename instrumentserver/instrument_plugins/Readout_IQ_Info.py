from instrument import Instrument
import types
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from Pulse_Info import Pulse_Info
import numpy as np

class Readout_IQ_Info(Pulse_Info):

    def __init__(self, name, **kwargs):
        super(Readout_IQ_Info, self).__init__(name, **kwargs)

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
        self.add_parameter('pulse_width', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='width of Gaussian Square wave',
                set_func=lambda x: True, value=3000)                
        self.add_parameter('sigma', type=types.IntType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='sigma of Gaussian Square wave rise and fall',
                set_func=lambda x: True, value=10)        
        self.add_parameter('amp', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='amplitude of readout pulse',
                set_func=lambda x: True, value=0)
        self.add_parameter('fixed_phase', type=types.FloatType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='lab phase of readout signal',
                set_func=lambda x: True, value=0)
        self.add_parameter('rfsource', type=types.StringType,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='RF-source for read-out pulse')
        
        
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

    def do_get_sequence(self, phase = np.pi/4, amp = None, chop=4):
        if amp is None: amp = self.get_amp()
        width = int(self.get_pulse_width())
        sigma = int(self.get_sigma())
        
        # calculate a gauss square by hand
        blockwidth = np.ceil(width+chop*sigma)
        ts = np.linspace(-blockwidth/2, blockwidth/2, blockwidth, endpoint=True)
        ys = np.zeros_like(ts, dtype=complex)
        ys[(ts>-width/2)&(ts<width/2)] = 1
        mask = (ts<=-width/2)
        ys[mask] = np.exp(-((ts[mask]+width/2)/sigma)**2)
        mask = (ts>=width/2)
        ys[mask] = np.exp(-((ts[mask]-width/2)/sigma)**2)

        # send it to the different channels based on the phase
        
        ys *= np.exp(-1.0j*phase)
        data_i = np.real(ys)
        data_q = np.imag(ys)
        
        # now we need to modulate it 
        phis = 2 * np.pi * np.arange(0, len(ys)) / self.get_sideband_period()
        data_i *= amp * np.cos(phis)
        data_q *= amp * np.sin(phis)

        # load it up
        channels = self.get_channels().split(',')
        return Combined([DataPulse(data_i, amp = amp, chan=int(channels[0]), 
                                         filename = 'RO_I_pulse'),
                         DataPulse(data_q, amp = amp, chan=int(channels[1]), 
                                         filename = 'RO_Q_pulse'),
                         Constant(sigma * 4 + width, 1, chan=self.get_acq_chan())])
        

    def do_get_sequence_old(self, readout_qubit_info, df = 0, phase = 0, amp = None):
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