"""
Created on Thu Oct 17 14:04:39 2019

@author: Wang_Lab
"""
from .sequencer import Combined, Sequence, Sequencer, Delay, Pulse, Instruction, Constant, Join
from .pulselib import CSVPulse, DetunedGaussSquare, DataPulse
import mclient
import numpy as np



class octlib(object):
    
    def __init__(self, qt_amp, cav_amp, time_shift, qubit_info, cav_info,
                 filepath=r'C:\qrlab\pulseseq\CSVPulses', decode_info=None):
        self.qt_amp = qt_amp
        self.cav_amp = cav_amp
        self.time_shift = time_shift
        self.filepath = filepath
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        if decode_info is None:
            decode_info = cav_info
        self.decode_info = decode_info

    def fock_state(self, end_state, phase = 0):
        combined_path = self.filepath + '\state_transfer_' + end_state
        data = self.cav_amp * np.loadtxt(combined_path + '_cavity_1000ns.csv') - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_1000ns.csv')
        data *= np.exp(-1.0j*phase)
        cav_i = np.real(data)
        cav_q = np.imag(data)
        
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
                                         filename = combined_path + '_cavity_1000ns.csv')]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
                                         filename = combined_path + '_cavity_q_1000ns.csv')]),
                         ])

    def fock_state_two_file(self, end_state, start_state='0'):
        combined_path = self.filepath + '\envelope_fock_' + start_state + '_' + end_state
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               CSVPulse(combined_path + '_cavity_1000ns.csv', self.cav_amp, chan=self.cav_info.sideband_channels[0])]),
                         ])
    
    
    def mod4_prep(self, state, phase = 0):
        combined_path = self.filepath + '\state_transfer_' + state
        data = self.cav_amp * np.loadtxt(combined_path + '_cavity_1000ns.csv') - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_1000ns.csv')
        data *= np.exp(-1.0j*phase)
        cav_i = np.real(data)
        cav_q = np.imag(data)
        
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
                                         filename = combined_path + '_cavity_1000ns.csv')]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
                                         filename = combined_path + '_cavity_q_1000ns.csv')]),
                         ])

    def mod4_encode(self):
        combined_path = self.filepath + '\encoding_unitary'
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               CSVPulse(combined_path + '_cavity_1000ns.csv', self.cav_amp, chan=self.cav_info.sideband_channels[0])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               CSVPulse(combined_path + '_cavity_q_1000ns.csv', self.cav_amp, chan=self.cav_info.sideband_channels[1])]),
                         ])

    def mod4_decode(self, phase = 0, secondary = False): # 3000 is the new decoding, 1000 is the old, 2000 is bad
        dt_0 = '3000'
        dt_pi = '2000'
        
        
        combined_path = self.filepath + '\decoding_unitary'
        if secondary:
            data = (self.cav_amp * np.loadtxt(combined_path + '_cavity_' + dt_pi + 'ns_pi.csv') 
                    - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_' + dt_pi + 'ns_pi.csv'))
        else:
#            data = self.cav_amp * np.loadtxt(combined_path + '_cavity_1000ns.csv') - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_1000ns.csv')
            data = (self.cav_amp * np.loadtxt(combined_path + '_cavity_' + dt_0 + 'ns.csv') 
                    - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_' + dt_0 + 'ns.csv'))
#            phase += np.pi/2
        data *= np.exp(-1.0j*phase)
        cav_i = np.real(data)
        cav_q = np.imag(data)
        
        if secondary:
            return Combined([Join([CSVPulse(combined_path + '_transmon_' + dt_pi + 'ns_pi.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                             Join([CSVPulse(combined_path + '_transmon_q_' + dt_pi + 'ns_pi.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                                   DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
                                             filename = combined_path + '_cavity_' + dt_pi + 'ns_pi.csv')]),
                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                                   DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
                                             filename = combined_path + '_cavity_q_' + dt_pi + 'ns_pi.csv')]),
                             ])
        else:
#            return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
#                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
#                             Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
#                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
#                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
#                                   DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
#                                             filename = combined_path + '_cavity_1000ns.csv')]),
#                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
#                                   DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
#                                             filename = combined_path + '_cavity_q_1000ns.csv')]),
#                             ])
            return Combined([Join([CSVPulse(combined_path + '_transmon_' + dt_0 + 'ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                             Join([CSVPulse(combined_path + '_transmon_q_' + dt_0 + 'ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                                   DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
                                             filename = combined_path + '_cavity_' + dt_0 + 'ns.csv')]),
                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                                   DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
                                             filename = combined_path + '_cavity_q_' + dt_0 + 'ns.csv')]),
                             ])
    
    def mod4_decode2(self, phase = 0, secondary = False): # just the secondary decoding
        combined_path = self.filepath + '\decoding_unitary'
#        if secondary:
        data = self.cav_amp * np.loadtxt(combined_path + '_cavity_2000ns_pi.csv') - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_2000ns_pi.csv')
#        else:
#            data = self.cav_amp * np.loadtxt(combined_path + '_cavity_3000ns.csv') - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_3000ns.csv')
        data *= np.exp(-1.0j*phase)
        cav_i = np.real(data)
        cav_q = np.imag(data)
        
#        if secondary:
        return Combined([Join([CSVPulse(combined_path + '_transmon_2000ns_pi.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_2_2000ns_pi.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
                                         filename = combined_path + '_cavity_2000ns_pi.csv')]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
                                         filename = combined_path + '_cavity_q_2000ns_pi.csv')]),
                         ])
#        else:
#            return Combined([Join([CSVPulse(combined_path + '_transmon_3000ns.csv', -self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
#                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
#                             Join([CSVPulse(combined_path + '_transmon_q_3000ns.csv', -self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
#                                   Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
#                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
#                                   DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase)]),
#                             Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
#                                   DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase)]),
#                             ])
    
    def fock01_encode(self, phase = 0):
        combined_path = self.filepath + '\simple_unitary'
        data = self.cav_amp * np.loadtxt(combined_path + '_cavity_1000ns.csv') - 1.0j* self.cav_amp * np.loadtxt(combined_path + '_cavity_q_1000ns.csv')
        data *= np.exp(-1.0j*phase)
        cav_i = np.real(data)
        cav_q = np.imag(data)
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),

                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               DataPulse(cav_i, amp = self.cav_amp, chan=self.cav_info.sideband_channels[1], phase = phase,
                                         filename = combined_path + '_cavity_1000ns.csv')]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               DataPulse(cav_q, amp = self.cav_amp, chan=self.cav_info.sideband_channels[0], phase = phase,
                                         filename = combined_path + '_cavity_q_1000ns.csv')]),
                        ])

    def alpha2(self):
        combined_path = self.filepath + r'\state_transfer_coherent'
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               CSVPulse(combined_path + '_cavity_1000ns.csv', self.cav_amp, chan=self.cav_info.sideband_channels[0])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               CSVPulse(combined_path + '_cavity_q_1000ns.csv', self.cav_amp, chan=self.cav_info.sideband_channels[1])]),
                        ])
    
    def prekerr(self):
        combined_path = self.filepath + r'\state_transfer_prekerr'
        return Combined([Join([CSVPulse(combined_path + '_transmon_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[0]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[0])]),
                         Join([CSVPulse(combined_path + '_transmon_q_1000ns.csv', self.qt_amp, chan=self.qubit_info.sideband_channels[1]),
                               Constant(self.time_shift, 0, chan=self.qubit_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[1]),
                               CSVPulse(combined_path + '_cavity_1000ns.csv', self.cav_amp, chan=self.cav_info.sideband_channels[1])]),
                         Join([Constant(self.time_shift, 0, chan=self.cav_info.sideband_channels[0]),
                               CSVPulse(combined_path + '_cavity_q_1000ns.csv', -self.cav_amp, chan=self.cav_info.sideband_channels[0])]),
                        ])
    
    
class comb(object):
    def __init__(self, info, detunings, amps, sigma = 100, vary = None,
                 stark_shift = 0, phases = None, **kwargs):
        self.info = info
        self.num_tones = len(detunings)
        self.detunings = detunings
        self.amps = amps
        self.sigma = sigma
        if vary is None:
            vary = [1] * self.num_tones
        self.vary = vary
        self.stark_shift = stark_shift
        if phases is None:
            phases = [0] * self.num_tones
        self.phases = phases

    def get_poly_seq(self, width, df):
        g = DetunedGaussSquare(width, self.sigma, chans=self.info.sideband_channels)
        for i, det in enumerate(self.detunings):
            freq = (self.vary[i] * df - det - self.stark_shift)
            if freq != 0:
                period = 1e9 / freq
            else:
                period = 1e50
            g.add(self.amps[i], period, phases = (self.phases[i], self.phases[i]-np.pi/2))
        return [g()]
    
def cavity_cooling(cavity_info = None, reservoir_info = None, cavity_amp = .1, reservoir_amp = .1,
                   cavity_detuning = -55.9):
    if cavity_info is None:
        cavity_info = mclient.instruments['cavity_infoA']