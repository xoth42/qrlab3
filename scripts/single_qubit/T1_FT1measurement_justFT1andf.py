# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 15:02:11 2018

@author: WangLab2
"""

import matplotlib.pyplot as plt
import numpy as np
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import h5py
import lmfit

def analysis(meas, data=None, fig=None, ofs=None, amplitude=None, f_ofs=None, f_amp=None):
#    ys, fig = meas.get_ys_fig(data, fig)
##    xs = range(5)
#    T1delay = meas.T1delay
#    FT1delay = meas.FT1delay
##    
##    fig.axes[0].plot(xs, ys, 'ks', ms=3)
##    
#    print data
#    print ys
##    print xs
#    print T1delay
#    print FT1delay
#    
#    eq = data[0]
#    g = data[2]
#    e = 2*data[0] - data[2]
#    f = data[4]
#    
#    T1 = -T1delay / np.log((data[1]-g)/(e-g))
#    FT1 = -FT1delay / np.log((data[3]-eq)/(f-eq))
#    
#    print T1, FT1
#    return T1, FT1
    return
    

#def T1exp_decay(T1params, T1delay, T1data):
#    T1est = T1params['ofs'] + T1params['amplitude'] * np.exp(-T1delay / T1params['tau'].value)
#    return T1data - T1est
#    
#def FT1exp_decay(FT1params, FT1delay, FT1data):
#    FT1est = FT1params['f_ofs'] + FT1params['f_amplitude'] * np.exp(-FT1delay / FT1params['f_tau'].value)
#    return FT1data - FT1est
    
#def analysis(meas, data=None, fig=None, ofs=None, amplitude=None, f_ofs=None, f_amp=None):
##    ys, fig = meas.get_ys_fig(data, fig)
##    xs = meas.T1delay
#
##    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)
#
#    T1params = lmfit.Parameters()
#    if ofs is not None:
#        T1params.add('ofs', value=ofs, vary=False)
#    else:
#        T1params.add('ofs', value=0)
#    if amplitude is not None:
#        T1params.add('amplitude', value=amplitude, vary=False)
#    else:
#        T1params.add('amplitude', value=0)
#    T1params.add('tau', value=meas.T1delay*2.0)
#    T1result = lmfit.minimize(T1exp_decay, T1params, args=(meas.T1delay, meas.T1data))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
#
#    lmfit.report_fit(T1result.params)
#
#    plt.figure()
#    plt.plot(meas.T1delay/1e3, -T1exp_decay(T1result.params, meas.T1delay, 0), label='Fit, tau = %.03f us'%(T1result.params['tau'].value/1000.))
#    plt.legend(loc=0)
#    plt.set_ylabel('Intensity [AU]')
#    plt.set_xlabel('Time [us]')
#    plt.plot(meas.T1delay, T1exp_decay(T1result.params, meas.T1delay, meas.T1data), marker='s')
#    
#    FT1params = lmfit.Parameters()
#    if f_ofs is not None:
#        FT1params.add('f_ofs', value=f_ofs, vary=False)
#    else:
#        FT1params.add('f_ofs', value=0)
#    if f_amp is not None:
#        FT1params.add('f_amplitude', value=f_amp, vary=False)
#    else:
#        FT1params.add('f_amplitude', value=0)
#    FT1params.add('f_tau', value=meas.FT1delay*2.0)
#    FT1result = lmfit.minimize(FT1exp_decay, FT1params, args=(meas.FT1delay, meas.FT1data))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
#
#    lmfit.report_fit(FT1result.params)
#
#    plt.figure()
#    plt.plot(meas.FT1delay/1e3, -FT1exp_decay(FT1result.params, meas.FT1delay, 0), label='Fit, tau = %.03f us'%(FT1result.params['tau'].value/1000.))
#    plt.legend(loc=0)
#    plt.set_ylabel('Intensity [AU]')
#    plt.set_xlabel('Time [us]')
#    plt.plot(meas.FT1delay, FT1exp_decay(T1result.params, meas.FT1delay, meas.FT1data), marker='s')  
#    
#    return T1result.params, FT1result.params
    
    
class T1_FT1_fluxmeasurementII(Measurement1D):

    def __init__(self, qubit_info, ef_info, T1delay, FT1delay, seq=None, postseq=None, ofs=None, amplitude=None, f_ofs=None,
                 f_amp=None, **kwargs):
        self.qubit_info = qubit_info
        self.ef_info = ef_info
        self.T1delay = T1delay
        self.FT1delay = FT1delay
        if seq is None:
            seq = Trigger(250)
        self.seq = seq
        self.postseq = postseq
        self.ofs = ofs
        self.amplitude = amplitude
        self.f_ofs = f_ofs
        self.f_amp = f_amp


        super(T1_FT1_fluxmeasurementII, self).__init__(4, infos=(qubit_info, ef_info), **kwargs)
        self.T1data = self.data.create_dataset('T1delay', data=T1delay)
        self.FT1data = self.data.create_dataset('FT1delay', data=FT1delay)
        
        
    def generate(self):
        '''Optional pre-sequence'''
        s = Sequence() 
        r_ge = self.qubit_info.rotate
        r_ef = self.ef_info.rotate
        
#        
#        '''This measures voltage of |e>'''
#        s.append(self.seq)
#        s.append(r_ge(np.pi, 0))
#        
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#        ]))
        
        '''This measures voltage of |g> + |e>'''
        s.append(self.seq)
        s.append(r_ge(np.pi/2, 0))
        
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))
        s.append(Delay(1000))
# 
#        '''This does the T1 measurement'''
#        s.append(self.seq)
#        s.append(r_ge(np.pi, 0))
#        s.append(Delay(self.T1delay))
#        
#        s.append(Combined([
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
#            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
#        ]))
#        s.append(Delay(1000))
        
        '''This measures voltage of |g>'''
        s.append(self.seq)
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))
        s.append(Delay(1000))
        
        '''This does the FT1 measurement'''
        s.append(self.seq)
        s.append(r_ge(np.pi, 0))
        s.append(r_ef(np.pi, 0))
        s.append(Delay(self.FT1delay))
        s.append(r_ge(np.pi/2, 0))
#        s.append(r_ef(np.pi, 0))
#        s.append(r_ge(np.pi, 0))

        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))
        s.append(Delay(1000))
        
        '''This measures |f> excited state voltage'''
        s.append(self.seq)
        s.append(r_ge(np.pi, 0))
        s.append(r_ef(np.pi, 0))
        
        if self.postseq is not None: #Optional post-sequence
                s.append(self.postseq) 
                
        s.append(Combined([
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
            Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
        ]))
        s.append(Delay(1000))
        
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs

    def analyze(self, data=None, fig=None):
        self.result_params = analysis(self, data, fig, ofs=self.ofs, amplitude=self.amplitude, f_ofs=self.f_ofs, f_amp=self.f_amp)
#        return self.result_params['tau'].value