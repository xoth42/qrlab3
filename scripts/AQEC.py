# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 14:03:37 2019

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 14:53:09 2018

@author: wanglab111
"""

import mclient
reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib.pyplot as plt
import os
os.chdir(r'C:/qrlab/scripts')

qubit_info = mclient.get_qubit_info('qubit1ge')
ef_info = mclient.get_qubit_info('qubit1ef')
cavity_infoA = mclient.get_qubit_info('cavityA')
cavity_infoAs = mclient.get_qubit_info('cavityAs')
#cavity_infoB = mclient.get_qubit_info('cavityB')
dig = mclient.instruments['dig']


fwm_info = mclient.get_qubit_info('FWM_info')
#fwm_info_a2 = mclient.get_qubit_info('FWM_info_a2')
#fwm_info_a4 = mclient.get_qubit_info('FWM_info_a4')    
#qubit_a0s = mclient.get_qubit_info('qubit_a0s')
#qubit_a2s = mclient.get_qubit_info('qubit_a2s')
#qubit_a4s = mclient.get_qubit_info('qubit_a4s')

#qubit_b1 = mclient.get_qubit_info('qubit_b1')
#qubit_b2 = mclient.get_qubit_info('qubit_b2')
#qubit_b3 = mclient.get_qubit_info('qubit_b3')
#qubit_b4 = mclient.get_qubit_info('qubit_b4')

qubit_a1 = mclient.get_qubit_info('qubit_a1')
qubit_a2 = mclient.get_qubit_info('qubit_a2')
qubit_a3 = mclient.get_qubit_info('qubit_a3')
qubit_a4 = mclient.get_qubit_info('qubit_a4')
qubit_a5 = mclient.get_qubit_info('qubit_a5')
qubit_a6 = mclient.get_qubit_info('qubit_a6')
qubit_a7 = mclient.get_qubit_info('qubit_a7')

cA = cavity_infoA.rotate
cAs = cavity_infoAs.rotate
ge = qubit_info.rotate
geqs = qubit_info.rotate_quasilective
ges = qubit_info.rotate_selective
ges_a1 = qubit_a1.rotate_selective
ges_a2 = qubit_a2.rotate_selective
ges_a3 = qubit_a3.rotate_selective


class comb(object):
    def __init__(self, info, detunings, amps, sigma = 100, vary = None,
                 stark_shift = 0, **kwargs):
        self.info = info
        self.num_tones = len(detunings)
        self.detunings = detunings
        self.amps = amps
        self.sigma = sigma
        if vary is None:
            vary = [1] * self.num_tones
        self.vary = vary
        self.stark_shift = stark_shift

    def get_poly_seq(self, width, df):
        g = pulselib.DetunedGaussSquare(width, self.sigma, chans=self.info.sideband_channels)
        for i, det in enumerate(self.detunings):
            freq = (self.vary[i] * df - det - self.stark_shift)
            if freq != 0:
                period = 1e9 / freq
            else:
                period = 1e50
            g.add(self.amps[i], period)
        return [g()]        


            

start_state = '0'
end_state = '04'
grape = sequencer.Join([sequencer.Trigger(250), 
                      sequencer.Combined([
                                          pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_' + start_state
                                                            + '_' + end_state + '_transmon_1000ns.csv', 
                                                            44, chan=qubit_info.sideband_channels[0]),
                                          pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_' + start_state
                                                            + '_' + end_state + '_cavity_1000ns.csv', 
                                                            144, chan=cavity_infoA.sideband_channels[0])
                                          ])
                    ])

grape2 = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_2_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_2_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0])
                                      ])
                ])
grape4 = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_4_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0])
                                      ])
                ])


grape6 = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_fock_0_to_6_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])
                                      
one_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])
                                      
zero_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddsqrt3_cavity_1000ns.csv', 
                                                        -144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])

plus_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])  
                                      
minus_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_plus_sqrt3_cavity_1000ns.csv', 
                                                        -144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])  
                      
plusi_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_cavity_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])   
                                      
                                      
minusi_cat = sequencer.Join([sequencer.Trigger(250), 
                  sequencer.Combined([
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_transmon_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_transmon_q_1000ns.csv', 
                                                        44, chan=qubit_info.sideband_channels[1]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_cavity_q_1000ns.csv', 
                                                        144, chan=cavity_infoA.sideband_channels[0]),
                                      pulselib.CSVPulse(r'C:\qrlab\pulseseq\CSVPulses\envelope_cat_oddisqrt3_cavity_1000ns.csv', 
                                                        -144, chan=cavity_infoA.sideband_channels[1])
                                      ])
                ])
                                      
cat_bloch = [zero_cat, one_cat, plus_cat, minus_cat, plusi_cat, minusi_cat]
                        
re_data = np.real(np.loadtxt(r'C:\qrlab\pulseseq\CSVPulses\Gaussian_envelope_coherent_c_400ns.csv', dtype = complex))
im_data = np.imag(np.loadtxt(r'C:\qrlab\pulseseq\CSVPulses\Gaussian_envelope_coherent_c_400ns.csv', dtype = complex))
                                      
grape_displacement = sequencer.Join([sequencer.Trigger(250), 
                                     sequencer.Combined([pulselib.DataPulse(re_data, 125, chan=cavity_infoA.sideband_channels[0]),
                                                         pulselib.DataPulse(im_data, 125, chan=cavity_infoA.sideband_channels[1])
                                   ])])


#ss = 1.065e6 
#ss = 2.05e6
chi2 = 2.655e6
# one tone
#fwm_comb = comb(fwm_info, [0-ss], [.2], [], vary = [1], stark_shift = ss)
#ge_comb = comb(qubit_info, [0+ss], [1.0e-3], [], vary = [-1], stark_shift = ss)

#two tone
#fwm_comb = comb(fwm_info, [0, chi2], [x * 0.2 for x in [1, 0.8]], 
#                [100], vary = [1, 1], stark_shift = ss)
#ge_comb = comb(qubit_info, [0, -chi2], [y * 1e-3 for y in [1, 1]], [110], vary = [-1, -1], stark_shift = -ss)

# four tone
#fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x * .2 for x in [-0.9, 0.7, 0.7, -0.9]],
#                [100, 101, 102], vary = [1] * 4, stark_shift = ss)
#ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [1.0e-3] * 4, [110, 111, 112], vary = [-1] * 4, stark_shift = -ss)

def get_poly_seq(dt):
    ss = 2.112e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.08, 0.90, 0.55, 0.57]], 
                    vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-0.90, 1.15, 1.0, 1.33]], 
                   vary = [-1]*4, stark_shift = -ss)
    poly_seq = []
    extra_infos = [c.info for c in [fwm_comb, ge_comb]]
    for c in [fwm_comb, ge_comb]:
        poly_seq += c.get_poly_seq(dt - c.sigma*4, 0)
        print(poly_seq)
        print(extra_infos)
    return poly_seq


if 0: # poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec
    ss = 2.112e6
#    fwm_comb = comb(fwm_info, [0, chi2], [x*0.2 for x in [-1.08, 0.90]], 
#                    [110, 111, 112], vary = [1]*2, stark_shift = ss)
#    ge_comb = comb(qubit_info, [0, -chi2], [y*1.0e-3 for y in [-0.90, 1.15]], 
#                   [110, 111, 112], vary = [-1]*2, stark_shift = -ss)
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.08, 0.90, 0.55, 0.57]], 
                     vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-0.90, 1.15, 1.0, 1.33]], 
                   vary = [-1]*4, stark_shift = -ss)
    freqs = np.linspace(-3e6, 3e6, 111)
    delay_times=[15e3]
    for delay_t in delay_times:
        ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a3, [fwm_comb, ge_comb],
                                                freqs, delay_t, post_delay = 1e3,
                                                seq = grape2, plot_seqs = False,
                                                bgcor = True,
                                                extra_info = [qubit_info, cavity_infoA]
                                                )
        ssb.measure_keysight()
    bla
    
    
if 0: # 2d poly ssbspec to find stark shift
    from FWM import poly_fwm_ssbspec2d
    
    fwm_freqs = np.linspace(-6e6, 3e6, 16)
    ge_freqs = np.linspace(-.08e6, .08e6, 5)
    delay_times=[15e3]
    for delay_t in delay_times:
        ssb2d = poly_fwm_ssbspec2d.poly_fwm_ssbspec2d(qubit_a5, fwm_comb, ge_comb,
                                                fwm_freqs, ge_freqs, delay_t,
                                                seq = grape, post_delay = 1e3, bgcor = True,
                                                extra_info = [qubit_info, cavity_infoA]
                                                )
        ssb2d.measure_keysight()
    bla

    
if 0: # time domain
    from FWM import poly_time_domain
    ss = 2.5173e6 #2.112e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)

    qubit_list = [
#                  qubit_info, 
                  qubit_a1, 
#                  qubit_a2, 
                  qubit_a3, 
#                  qubit_a4, 
                  qubit_a5,
#                  qubit_a6,
                  qubit_a7
                  ]
    delays = np.concatenate((np.linspace(0e3, 18e3, 10),
                             np.linspace(20e3, 350e3, 34),
                             ))

    td = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], qubit_list, delays,
                                       plot_seqs=False, bgcor=True, seq=plus_cat, 
                                       extra_info = [qubit_info, cavity_infoA]
                                       )
    td.measure_keysight()
    bla

    
if 0: # Sweeping FWM amps to get all three e-o rates
    from FWM import poly_fwm_ssbspec
    from FWM import poly_time_domain
    
    for r3 in np.linspace(0.55, 0.6, 1): 
        for r4 in np.linspace(0.6, 0.57, 1):
            ss = 2.5173e6
            fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
            ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)
            
#            freqs = np.linspace(-3.0e6, -1.0e6, 81)
#            ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_info, [fwm_comb, ge_comb], freqs, 10e3, post_delay = 1e3, seq = None,
#                                                    bgcor = False, extra_info = [qubit_info, cavity_infoA])
#            ss = -1 * ssb.measure_keysight()
#            fwm_comb.stark_shift = ss
#            ge_comb.stark_shift = -ss

            freqs = np.linspace(-0.2e6, 0.2e6, 31)
            dig.set_naverages(500)
            ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_info, [fwm_comb, ge_comb], freqs, 10e3, post_delay = 1e3, seq = None,
                                                    bgcor = True, extra_info = [qubit_info, cavity_infoA])
            ss += -1 * ssb.measure_keysight()
            fwm_comb.stark_shift = ss
            ge_comb.stark_shift = -ss

            fwm_comb.vary = [0, 0, 0, 1]
            ge_comb.vary = [0, 0, 0, -1]
            ssb = poly_fwm_ssbspec.poly_fwm_ssbspec(qubit_a6, [fwm_comb, ge_comb], freqs, 10e3, post_delay = 1e3, seq = grape6,
                                                    bgcor = True, extra_info = [qubit_info, cavity_infoA])
            dw67 = ssb.measure_keysight()
#
#            fwm_comb.detunings = [0, chi2, chi2*2, chi2*3-dw67]
#            ge_comb.detunings = [0, -chi2, -chi2*2, -chi2*3+dw67]
            
            dig.set_naverages(1000)
            delays = np.concatenate((np.linspace(0e3, 20e3, 21), np.linspace(21e3, 70e3, 15)))
            
            td0 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a1], delays, bgcor=True, seq=None, 
                                               extra_info = [qubit_info, cavity_infoA])
            td0.measure_keysight()
            
            td2 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a3], delays, bgcor=True, seq=grape2, 
                                               extra_info = [qubit_info, cavity_infoA])
            td2.measure_keysight()
            
            dig.set_trigger_period(3000)
            td4 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a5,], delays, bgcor=True, seq=grape4, 
                                               extra_info = [qubit_info, cavity_infoA])
            td4.measure_keysight()
            
            td6 = poly_time_domain.poly_time_domain([fwm_comb, ge_comb], [qubit_a7,], delays, bgcor=True, seq=grape6, 
                                               extra_info = [qubit_info, cavity_infoA])
            td6.measure_keysight()
            dig.set_trigger_period(2000)
            
    bla
    

if 0: # SSB after e-o dissipation
    from single_qubit import ssbspec

    dt = 200e3
    ss = 2.112e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.08, 0.90, 0.55, 0.57]], 
                    vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-0.90, 1.15, 1.0, 1.33]], 
                   vary = [-1]*4, stark_shift = -ss)
    infos = [fwm_comb.info, ge_comb.info]
    poly_seq = []
    for c in [fwm_comb, ge_comb]:
        poly_seq += c.get_poly_seq(dt - c.sigma*4, 0)
        
    seq = sequencer.Join([sequencer.Trigger(200), plus_cat, sequencer.Combined(poly_seq)])
        
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
                                        np.linspace(-11e6, 1e6, 121),
                                        )), 
                            seq=seq, plot_seqs=False, 
                            extra_info = infos + [cavity_infoA]
                            )
    spec.measure_keysight()
    bla    

if 0: # Q function w/ e-o dissipation on coherence state
    from scripts.single_cavity import Qfunction
    ss = 2.5173e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)
    
    infos = [fwm_comb.info, ge_comb.info]
    for dt in [130e3]:
        seq = sequencer.Join([sequencer.Trigger(200), zero_cat])
        if dt>0:
            seq.append(sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0)))
            
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoA, amax=2.1, N=15, amaxx=None, Nx=None, amaxy=None, Ny=None,
             seq=seq, postseq=None, delay=5, bgcor=False, 
             extra_info = infos+ [qubit_info, cavity_infoA]
             )
        Qfun.measure_keysight()
    bla


if 1: # W function after e-o dissipation on prepared state
    from scripts.single_cavity import WignerbyParity
    ss = 2.5173e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)
    
    infos = [fwm_comb.info, ge_comb.info]
    for cat in cat_bloch:
        for dt in [0e3, 70e3, 140e3]:
            seq = sequencer.Sequence()
            seq.append(cat)
            if dt>0:
                seq.append(sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0)))
#                seq.append(sequencer.Delay(dt))
                
            Wfun = WignerbyParity.WignerFunction(qubit_a2, ef_info, cavity_infoAs, 
    #                                 xs = np.linspace(-2,2,15), ys = np.linspace(-2,2,15),
                                     xs = np.linspace(-1.7,1.7,15), ys = np.linspace(-1.7,1.7,15),
                                     t_ge=356, t_gf=0,
                                     seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                     extra_info = infos+ [qubit_info, cavity_infoA]
                                     )
            Wfun.measure_keysight()
    #        for x_start in [-2.3, -1.1, 0.1, 1.1]:
    #            Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoB, 
    ##                                             xs = np.linspace(-2.1,2.1,15), ys = np.linspace(-1.5,1.5,11),
    #                                             xs = np.linspace(x_start,x_start+1.0, 6), ys = np.linspace(-2.2,2.2,23),
    ##                                             xs = np.linspace(-0.8,0.8,11), ys = np.linspace(-0.8,0.8,11),
    #                                             t_ge=320, t_gf=0,
    #                                             seq=seq, delay=5, bgcor=True, zmax=75, zmin=20, 
    #                                             extra_info = [qubit_b0s, fwm_info, qubit_b2s, qubit_b4s, fwm_info_b2, fwm_info_b4]
    #                                             )
    #            Wfun.measure_keysight()
        bla



if 0: # Vlastakis cat SSB or Wigner
    from single_qubit import ssbspec
    from scripts.single_cavity import WignerbyParity
#    dt = 50e3    
    seq = sequencer.Join([sequencer.Trigger(500), c(1.7,0), ge(np.pi/2, 0), sequencer.Delay(382), c(1.7, 0),  # this was written for c(1.7,0)
                          geqs(np.pi, 1.1), c(-1.7, 0.05*np.pi/2),
                          sequencer.Delay(500)
                        ])
#    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((np.linspace(-10e6, 1e6, 101),)), 
#                           seq=seq, plot_seqs=False, extra_info = [cavity_infoA])
#    spec.measure_keysight()
    Wfun = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA, 
#                                 xs = np.linspace(-2,2,15), ys = np.linspace(-2,2,15),
                                 xs = np.linspace(-2.8,2.8,15), ys = np.linspace(-2.8,2.8,15),
                                 t_ge=382, t_gf=0,
                                 seq=seq, delay=5, bgcor=True, zmax=100, zmin=-100, 
                                 extra_info = infos
                                 )
    Wfun.measure_keysight()    
    bla

if 0: # Kerr revival test
    from scripts.single_cavity import Qfunction
    for dt in [160e3, 180e3, 200e3, 220e3, 240e3]:
        seq = sequencer.Join([sequencer.Trigger(250), 
                              c(1.5, 0),
                              sequencer.Delay(dt)
                              ])    
        Qfun = Qfunction.QFunction(qubit_info, cavity_infoB, amax=2.1, N=11, amaxx=None, Nx=None, amaxy=None, Ny=None,
                     seq=seq, postseq=None, delay=5, bgcor=False, 
                     )
        Qfun.measure_keysight()
        Wfun.measure_keysight()

    
if 0: # SNAP gate
    from single_qubit import ssbspec
    
    c = cavity_infoA.rotate
#        seq = sequencer.Join([sequencer.Trigger(250), 
#                              c(1.55,0), 
#                              sequencer.Combined([ges(2*np.pi, 0), ges_a1(2*np.pi, phase)]), 
#                              c(-.44, 0),
#                              ])
    #    seq = sequencer.Join([sequencer.Trigger(250), 
    #                          c(.56,0), 
    #                          ges(2*np.pi, 0),
    #                          c(-.26, 0)
    #                          ])
    #    seq = sequencer.Join([sequencer.Trigger(250), 
    #                          c(1.14,0), 
    #                          ges(2 * np.pi, 0),
    #                          c(-.56, 0)
    #                          ])
    seq = sequencer.Join([sequencer.Trigger(250), 
                          c(2.1,0), 
                          sequencer.Combined([ges(2*np.pi, 0), ges_a1(2*np.pi, 0), ges_a2(2*np.pi, 0), ges_a3(2*np.pi, 0)]), 
                          c(-.32, 0),
                          ])
    spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                        np.linspace(-21e6, -19e6, 31),
#                                        np.linspace(-11e6, -9e6, 31),
                                        np.linspace(-6e6, -3e6, 111),
                                       )), 
                           seq=seq, plot_seqs=False, 
                           extra_info = [cavity_infoA, qubit_a1, qubit_a2, qubit_a3]#, qubit_b0s, qubit_b2s, qubit_b4s, fwm_info, fwm_info_b2, fwm_info_b4]
                           )
    spec.measure_keysight()
    bla
    
if 0: # Calibrate selective pi pulse at different photon numbers
    from single_qubit import rabi
    tr = rabi.Rabi(qubit_a6, 
#                   np.linspace(-0.7, 0.7, 51), selective=False,    
                  np.linspace(-0.025, 0.025, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, 
                   seq=grape6,
                   extra_info=[cavity_infoA, qubit_info])
    tr.measure_keysight()
    bla

if 0: # Ramsey measurement with selective pulses at different photon numbers
    from single_qubit import T2measurement
    t2 = T2measurement.T2Measurement(qubit_a2, np.linspace(0e3, 20e3, 101), detune=.4e6,
                                     double_freq=False, generate=True, seq=grape2, selective=True, extra_info=[cavity_infoA, qubit_info])
    t2.measure_keysight()
    bla
    
    
if 0: # Test qubit pop after fwm tone
    from single_qubit import rabi
    tr = rabi.Rabi(fwm_info, 
#                   np.linspace(-0.9, 0.9, 101), selective=False,
                  np.linspace(-0.4, 0.4, 51), selective=True,
#                   np.linspace(-0.1, 0.1, 41), selective=.5,
                   plot_seqs=False, generate=True, repeat_pulse=1, update=False, seq=None,
                   postseq = sequencer.Delay(2e3))
    tr.measure_keysight()
    bla


if 0: # wigner rotation test
    from AQEC import wigner_angle_test
    ss = 2.5173e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)

    infos = [fwm_comb.info, ge_comb.info]
        
#    times = np.array([0e3, 70e3, 140e3, 210e3, 280e3, 350e3, 420e3])
    times = np.linspace(0, 250e3, 100)
#    times = np.concatenate([np.linspace(120e3, 160e3, 5),
#                            np.linspace(260e3, 300e3, 5),
#                            np.linspace(400e3, 440e3, 5),
#                            ])
    phases = np.zeros_like(times)
    amps = np.zeros_like(times)
    sigmas = np.zeros_like(times)
    for i, dt in enumerate(times):
        seq = sequencer.Sequence()
        seq.append(zero_cat)
        
        poly_seq = []
        if dt>0:
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq.append(poly_seq)
#            seq.append(sequencer.Delay(dt))
            
        wa = wigner_angle_test.wigner_angle_test(qubit_a2, cavity_infoAs, 41, 
                                                 .6, t_ge  = 356, bgcor = True, fit = True,
                                                 seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)
        result = wa.measure_keysight()
        params = result.params
        phases[i] = params['phase']
        amps[i] = params['amp']
        sigmas[i] = params['sigma']
        
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(times/1e3, phases)
    plt.ylabel('phases')
    plt.subplot(3,1,2)
    plt.plot(times/1e3, amps)
    plt.ylabel('amps')
    plt.subplot(3,1,3)
    plt.plot(times/1e3, sigmas)
    plt.ylabel('sigmas')
    plt.xlabel('times [us]')
        
    bla

if 0: # Q rotation test
    from AQEC import husimiq_angle_test
    ss = 2.5173e6
    fwm_comb = comb(fwm_info, [0, chi2, chi2*2, chi2*3], [x*0.2 for x in [-1.20, 1.00, 0.62, 0.56]], vary = [1]*4, stark_shift = ss)
    ge_comb = comb(qubit_info, [0, -chi2, -chi2*2, -chi2*3], [y*1.0e-3 for y in [-1.03, 1.58, 1.35, 1.75]], vary = [-1]*4, stark_shift = -ss)

    infos = [fwm_comb.info, ge_comb.info]
        
    times = np.linspace(0e3, 10e3, 3)
#    times = np.concatenate([np.linspace(100e3, 160e3, 5),
#                            np.linspace(260e3, 300e3, 5),
#                            np.linspace(400e3, 440e3, 5),
#                            ])
    phases = np.zeros_like(times)
    amps = np.zeros_like(times)
    sigmas = np.zeros_like(times)
    for i, dt in enumerate(times):
        seq = sequencer.Sequence()
        seq.append(grape)
        
        poly_seq = []
        if dt>0:
            poly_seq = sequencer.Combined(fwm_comb.get_poly_seq(dt - fwm_comb.sigma*4, 0) + ge_comb.get_poly_seq(dt - ge_comb.sigma*4, 0))
            seq.append(poly_seq)
#            seq.append(sequencer.Delay(dt))
       
            
        qa = husimiq_angle_test.husimiq_angle_test(qubit_info, cavity_infoAs, 41, 
                                                 .7, bgcor = False, fit = True,
                                                 seq = seq, extra_info = [qubit_info, cavity_infoA] + infos)

        result = qa.measure_keysight()
        params = result.params
        phases[i] = params['phase']
        amps[i] = params['amp']
        sigmas[i] = params['sigma']
        
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(times/1e3, phases)
    plt.ylabel('phases')
    plt.subplot(3,1,2)
    plt.plot(times/1e3, amps)
    plt.ylabel('amps')
    plt.subplot(3,1,3)
    plt.plot(times/1e3, sigmas)
    plt.ylabel('sigmas')
    plt.xlabel('times [us]')
        
    bla            
            