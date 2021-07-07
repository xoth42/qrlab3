from instrument import Instrument
import types
#import numpy as np
#import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
#from lib.math import fit
#from lmfit.models import LinearModel, LorentzianModel
#from measurement import Measurement1D

class Readout_Info(Instrument):

    def __init__(self, name, **kwargs):
        Instrument.__init__(self, name, tags=['virtual'])

        self.add_parameter('rotype', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=('High-power', 'Dispersive'),
                help='Read-out type to use')
        self.add_parameter('rfsource1', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='RF-source for read-out pulse')
        self.add_parameter('rfsource2', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='RF-source for demodulation')
        self.add_parameter('power', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
        self.add_parameter('frequency', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_GET)
        self.add_parameter('readout_chan', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('IQg', type=complex,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ point of g')
        self.add_parameter('IQe', type=complex,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ point of e')
        self.add_parameter('IQe_radius', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='IQ radius threshold for e state')
        self.add_parameter('threshold_pt', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='projected threshold for g/e discrimination')
        self.add_parameter('acq_chan', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True)
        self.add_parameter('pulse_len', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=500)
        self.add_parameter('acq_len', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='Acquisition length for FPGA',
                set_func=lambda x: True, value=3000)
        self.add_parameter('ref_len', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='Reference length for FPGA',
                set_func=lambda x: True, value=500)
        self.add_parameter('naverages', type=int,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                help='# averages for FPGA',
                set_func=lambda x: True, value=500)
        self.add_parameter('envelope', type=bytes,
                help='Envelope for FPGA',
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value='1')
#        self.add_parameter('ref_freq',  type=types.FloatType,
#                help='reference frequency is 50(MHz) or others',
#                flags=Instrument.FLAG_GETSET|Instrument.FLAG_SOFTGET,
#                set_func=lambda x: True, value = 50)#Yingying
        self.set(kwargs)

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
        #ins = self._get_ins()
        #if ins:
         #   return ins.get_frequency()
        #Josh did this on 3/20/18 since the get wasn't working and it wasn't
        #important to get working.
        return 1
    def do_set_frequency(self, val):
        ins = self._get_ins()
        if ins:
            return ins.set_frequency(val)
        
    def do_get_sequence(self):
        ro = Combined([
                    Constant(self.get_pulse_len(), 1, chan=self.get_readout_chan()),
                    Constant(self.get_pulse_len(), 1, chan=self.get_acq_chan())])
        return ro
    
#    def do_get_sequence(self):
#        p_l = self.pulse_len
#        r_c = self.
#        ro = 'Combined([Constant(%d, 1, chan=%s),Constant(%d, 1, %s)])' % (self.pulse_len,self.readout_chan,self.pulse_len,self.acq_chan)       
#        return ro
        
        
        
        
        
