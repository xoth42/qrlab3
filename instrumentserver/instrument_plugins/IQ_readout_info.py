# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:41:47 2020

@author: Wang_Lab
"""

from instrumentserver.instrument import Instrument
from instrumentserver.instrument_plugins.Pulse_Info import Pulse_Info
from pulseseq.sequencer import *
from pulseseq.pulselib import *

#class IQ_Readout_Info(Qubit_Info,Readout_info):
#    def __init__(self, name, **kwargs):
#        super(IQ_Readout_Info, self).__init__(name, tags=['virtual'], **kwargs)

class IQ_Readout_Info(Pulse_Info):

    def __init__(self, name, **kwargs):
        super(IQ_Readout_Info, self).__init__(name, tags=['virtual'], **kwargs)

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
#Qubit_info parameters:
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
        self.add_parameter('sideband_channels', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True,
                doc='The sequencing channel for this qubit, sideband modulation will let it end up in the physical channels.'
                )
        self.add_parameter('rotation', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=ROTATIONS,
                set_func=lambda x: True, value='Gaussian')

        self.add_parameter('rotation_selective', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=ROTATIONS,
                set_func=lambda x: True, value='Gaussian')

        self.add_parameter('rotation_quasilective', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                option_list=ROTATIONS,
                set_func=lambda x: True, value='Gaussian')

        self.add_parameter('w', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=10,
                doc='For Gaussian rotations sigma, for others the pulse width'
                )

        self.add_parameter('w_selective', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=10,
                doc='For Gaussian rotations sigma, for others the pulse width'
                )

        self.add_parameter('w_quasilective', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=10,
                doc='For Gaussian rotations sigma, for others the pulse width'
                )

        self.add_parameter('pi_amp', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=1.0,
                doc='''The amplitude for a pi pulse. If pi/2 amp is specified
                as well a quadratic interpolation will be performed''',
                )

        self.add_parameter('pi_amp_quasilective', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=1.0,
                doc='''The amplitude for a pi pulse. If pi/2 amp is specified
                as well a quadratic interpolation will be performed''',
                )

        self.add_parameter('pi_amp_selective', type=float,
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

        self.add_parameter('pi2_amp_selective', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='The amplitude for a pi/2 pulse',
                )

        self.add_parameter('pi2_amp_quasilective', type=float,
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

        self.add_parameter('drag_selective', type=float,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                set_func=lambda x: True, value=0,
                doc='''The drag parameter, specifies which fraction of the
                derivative should be added to the other quadrature''',
                )

        self.add_parameter('marker_channel', type=bytes,
                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
                value='',
                set_func=lambda x: True,
                doc='Marker channel for activity',
                )
#        self.add_parameter('marker_pre', type=types.IntType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                value=8,
#                set_func=lambda x: True,
#                doc='Marker buffer before activity',
#                )
#        self.add_parameter('marker_post', type=types.IntType,
#                flags=Instrument.FLAG_SET|Instrument.FLAG_SOFTGET,
#                value=4,
#                set_func=lambda x: True,
#                doc='Marker buffer after activity',
#                )
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
        self.add_rotation_parameters(suffix='_selective')
        self.add_rotation_parameters(suffix='_oct', rotations=ROTATIONS)
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

#    def do_get_sequence(self):
#        if self.mixer_info.deltaf == 0:
#            
#            ro = (Combined([
#                Join([Delay(300),Constant(self.pulse_len, 1, chan=self.acq_chan)]),
#                Join([Constant(self.pulse_len + 100, 1, chan=self.readout_chan),Delay(200)]),
#                Join([Delay(100),Constant(self.pulse_len, self.pi_amp, chan=self.channels[0]),Delay(200)]),
#            ]))
#        else:
#            ro = (Combined([
#                Join([Delay(300),Constant(self.pulse_len, 1, chan=self.acq_chan)]),
#                Join([Constant(self.pulse_len + 100, 1, chan=self.readout_chan),Delay(200)]),
#                Join([Delay(100),self.rotate(np.pi, 0),Delay(200)]),
#
#            ]))
#        return ro
        
        
        
        
        
        
        
        
        
        
        
