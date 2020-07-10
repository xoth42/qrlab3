# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 22:28:37 2020

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import matplotlib.pyplot as plt
import copy
import mclient
import lmfit
import time

FIT_AMP         = 'AMP'         # Fit simple sine wave
FIT_AMPFUNC     = 'AMPFUNC'     # Try to fit amplitude curve based on pi/2 and pi amp
FIT_PARABOLA    = 'PARABOLA'    # Fit a parabola (to determine min/max pos)

def fit_timerabi(params, x, data):
    est = (params['ofs'].value - np.exp(-x / params['tau']) *params['amp'].value 
            * np.cos(2*np.pi*x / params['period'].value + params['phase'].value))
    return data  - est



def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.times

    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    amp0 = (np.min(ys) - np.max(ys)) / 2
#    if ys[0]>np.average(ys):
#        amp0 = -amp0
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    period0 = 1 / np.abs(fftfs[np.argmax(fftys)])

    params = lmfit.Parameters()
    params.add('ofs', value=np.average(ys))
    params.add('amp', value=amp0)
    params.add('phase', value=0, vary=False)#min=-np.pi, max=np.pi)
    params.add('tau', value=np.max(xs))
    params.add('period', value=period0, min=0)
    
    result = lmfit.minimize(fit_timerabi, params, args=(xs, ys))
    # stderr of 0 is none. replace with other line when using actual data
    #txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 0, result.params['period'].value, 0, result.params['period'].value/2 )
    txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 
                                                                             result.params['amp'].stderr, 
                                                                             result.params['period'].value, 
                                                                             result.params['period'].stderr, 
                                                                             result.params['period'].value/2 )
    fig.axes[0].plot(xs, -fit_timerabi(result.params, xs, 0), label=txt)
    fig.axes[0].plot(xs, -fit_timerabi(result.params, xs, 0))
    fig.axes[1].plot(xs, fit_timerabi(result.params, xs, ys), marker='s')

#    lmfit.report_fit(params)
    lmfit.report_fit(result.params)

    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Pulse time')
    fig.axes[0].legend(loc=0)

    fig.canvas.draw()
    return result.params

class CavTimeRabi(Measurement1D):

    def __init__(self, fwm_channal, fwm_amp, times, power,seq=None, r_axis=0, fix_phase=True,
                 fix_period=None, repeat_pulse=1, selective=False, fit_type=FIT_AMP, **kwargs):
        self.fwm_channal = fwm_channal
        self.fwm_amp = fwm_amp
        self.times = times
        self.xs = times
        self.power = power

        if seq is None:
            seq = Trigger(1000)
        self.seq = seq

        self.fix_phase = fix_phase
        self.fix_period = fix_period
        self.repeat_pulse = repeat_pulse
        self.r_axis = r_axis
        self.fit_type = fit_type
        self.selective = selective

        super(CavTimeRabi, self).__init__(len(times), infos=(), **kwargs)
        self.data.create_dataset('times', data=times)

    def generate(self):

        
#        s = Sequence()
#        self.readout_info.rfsource1.set_power(self.power)
#        time.sleep(0.1)
#        for plen in self.times:           
#            s.append(self.seq)
#
#            fwm_plen = int(10000 + plen + 200 + self.readout_info.pulse_len) 
#            delay_acq = int(10200 +plen)
#            delay_ro = int(200 + self.readout_info.pulse_len)
#            
#            
#            s.append(Combined([
#                    Constant(int(fwm_plen), self.fwm_amp, chan = self.fwm_channal),
#                    Join([Delay(10000),Constant(int(plen), 1, chan=self.readout_info.readout_chan),Delay(delay_ro)]),
#                    Join([Delay(delay_acq), Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]),
#                ])
#                )
#            s.append(Delay(2000))
#    
#        
#        s = self.get_sequencer(s)
#        seqs = s.render()
#        return seqs
        s = Sequence()
        self.readout_info.rfsource1.set_power(self.power)
        time.sleep(0.1)
        for plen in self.times:           
            s.append(self.seq)

            fwm_plen = int(10000 + plen) 
            delay_acq = int(10200 +plen)
            delay_ro = int(200 + self.readout_info.pulse_len)
            
            
            s.append(Combined([
                    Constant(int(fwm_plen), self.fwm_amp, chan = self.fwm_channal),
                    Join([Delay(10000),Constant(int(plen), 1, chan=self.readout_info.readout_chan)]),
                ])
                )
            s.append(Join([Delay(200),Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan)]))
            s.append(Delay(2000))
    
        
        s = self.get_sequencer(s)
        seqs = s.render()
        return seqs


    def analyze(self, data=None, fig=None):
        self.fit_params = analysis(self, data=data, fig=fig)