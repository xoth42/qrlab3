# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 11:33:40 2020

@author: Wang_Lab, SVG
"""

import types

#from instrument import Instrument
#from Pulse_Info import Pulse_Info
#from mclient import instruments
from Readout_Info import Readout_Info
from Qubit_Info import Qubit_Info


#IQe=(30.69-48.9j), 
#IQg=(31.27-48.64j), 
#IQe_radius=1 ,
#rfsource1='RObrick',
#rfsource2='SC_ref',
#pulse_len=300,
#readout_chan='1m1',
#acq_chan='2m1',
#deltaf=-100e6,
#pi_amp=0.7,
#pi_amp_selective=0.01,
#rotation='Square',
#channels='7,7',
#sideband_channels='I5,Q5',
#sideband_phase=0,
#w=300,
#w_selective=200

class I_Q_readout_info(Qubit_Info,Readout_Info):
    def __init__(self, name, **IQ_args):
        pass

#        self.add_parameter('rotype', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                option_list=('High-power', 'Dispersive'),
#                help='Read-out type to use')
#        self.add_parameter('rfsource1', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='RF-source for read-out pulse')
#        self.add_parameter('rfsource2', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='RF-source for demodulation')
#        self.add_parameter('power', type=types.FloatType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET)
#        self.add_parameter('frequency', type=types.FloatType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_GET)
#        self.add_parameter('readout_chan_I', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                set_func=lambda x: True)
#        self.add_parameter('readout_chan_Q', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                set_func=lambda x: True)
#        self.add_parameter('IQg', type=types.ComplexType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='IQ point of g')
#        self.add_parameter('IQe', type=types.ComplexType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='IQ point of e')
#        self.add_parameter('IQe_radius', type=types.FloatType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='IQ radius threshold for e state')
#        self.add_parameter('threshold_pt', type=types.FloatType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='projected threshold for g/e discrimination')
#        self.add_parameter('acq_chan', type=types.StringType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                set_func=lambda x: True)
#        self.add_parameter('pulse_len', type=types.IntType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                set_func=lambda x: True, value=500)
#        self.add_parameter('acq_len', type=types.IntType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='Acquisition length for FPGA',
#                set_func=lambda x: True, value=3000)
#        self.add_parameter('ref_len', type=types.IntType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='Reference length for FPGA',
#                set_func=lambda x: True, value=500)
#        self.add_parameter('naverages', type=types.IntType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                help='# averages for FPGA',
#                set_func=lambda x: True, value=500)
#        self.add_parameter('envelope', type=types.StringType,
#                help='Envelope for FPGA',
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                set_func=lambda x: True, value='1')
#
#        self.set(IQ_args)
        
#    mixer_info = instruments.create('mixer_info', 'Qubit_Info',
#                        deltaf=-100e6,
#                        pi_amp=0.7,
#                        pi_amp_selective=0.01,
#                        rotation='Square',
#                        channels='7,7',
#                        sideband_channels='I5,Q5',
#                        sideband_phase=0,
#                        w=300,
#                        w_selective=200)
#    
#    readout = instruments.create('readout', 'Readout_Info', IQe=(30.69-48.9j), IQg=(31.27-48.64j),
#                             IQe_radius=1 , rfsource1='RObrick', rfsource2='SC_ref',
#                             pulse_len=300, readout_chan='1m1', acq_chan='2m1')

































