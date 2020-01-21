"""
performs wigner parity at every point with fixed amplitude alpha with varying angle from 0 to 2pi
wigner is the bgcor version wigner

Jeff Gertler
"""


import numpy as np
from math import factorial
import matplotlib.pyplot as plt
#from lib.math import fit
import copy
import mclient
from measurement import Measurement1D
from pulseseq.sequencer import *
from pulseseq.pulselib import *
import lmfit
import math
import time
import objectsharer as objsh

def double_gaussian(params, x, data):
    dx = np.min([np.abs(x - params['phase']), np.abs(x - params['phase'] - np.pi)], axis = 0)  #This should be a minus sign
    est = (params['background'] + params['amp'] * np.exp(-np.power(dx, 2.) / (2 * np.power(params['sigma'], 2.)))
                                + params['amp'] * np.exp(-np.power(np.pi - dx, 2.) / (2 * np.power(params['sigma'], 2.))))
    
#    est = (params['background'] + params['amp'] * np.exp(-np.power(x, 2.) / (2 * np.power(params['sigma'], 2.)))
#                                + params['amp'] * np.exp(-np.power(x - np.pi, 2.) / (2 * np.power(params['sigma'], 2.)))
#                                + params['amp'] * np.exp(-np.power(x - 2 * np.pi, 2.) / (2 * np.power(params['sigma'], 2.))))
#    est = np.roll(est, int(params['phase'] / (2 * np.pi) * len(x)))
    return data - est
    

def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.xs
    
    fig.axes[0].plot(xs, ys)
    fig.axes[0].plot(xs, np.flip(ys,0))
#    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('displacement')
        
    if meas.fit:
        n = len(xs)
        fig.axes[1].plot(xs[n/2+1:], np.flip(ys[:n/2], 0) - ys[n/2+1:])
        return np.sum(np.power(np.flip(ys[:n/2], 0) - ys[n/2+1:], 2))
#        phase = xs[np.argmin(ys)]
#        if phase > np.pi:
#            phase -= np.pi
#        
#        params = lmfit.Parameters()
#        params.add('background', value=0, vary=False)
#        params.add('amp', value=np.min(ys), max = 0)
#        params.add('sigma', value=np.pi/8, min=0)
#        params.add('phase', value=phase, min=0, max=np.pi)
#            
#        result = lmfit.minimize(double_gaussian, params, args=(xs, ys))
#        lmfit.report_fit(result.params)
#    
#        fig.axes[0].plot(xs, -double_gaussian(result.params, xs, 0))
#        fig.canvas.draw()
#        
#        return result
    fig.canvas.draw()
    return None



class wigner_line_cut(Measurement1D):

    def __init__(self, qubit_info, cav_info, xs, y=0, rotation=0, t_ge=0, delay = 0,
                 bgcor = False, fit = False, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.xs = xs
        self.y= y
        self.rotation=rotation
        self.t_ge = t_ge
        self.delay = delay
        self.bgcor = bgcor
        self.fit = fit
        if seq is None:
            seq = [Trigger(200)]
        self.seq = seq
        self.postseq = postseq
    
        npoints = len(xs)
        if bgcor:
            npoints *= 2
        
        super(wigner_line_cut, self).__init__(npoints, infos=[qubit_info, cav_info], **kwargs)
        
        self.data.create_dataset('xs', data=self.xs)
        self.data.set_attrs(
                y = y,
                rotation = rotation,
                t_ge = t_ge
        )

    def generate(self):
        s = Sequence()
        ge = self.qubit_info.rotate
        c = self.cav_info.rotate
        for x in self.xs:
            alpha = 1j * self.y + (np.cos(self.rotation) + 1j * np.sin(self.rotation)) * x
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue
                
                temp_seq = self.seq[:]
                temp_seq += [c(np.abs(alpha), np.angle(alpha))]

                if i_bg == 0:
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    temp_seq += [Delay(self.t_ge)]

                    temp_seq += [ge(np.pi/2, X_AXIS)]
                else:
#                    s.append(ge(np.pi/2, Y_AXIS))
                    temp_seq += [ge(np.pi/2, X_AXIS)]
                    temp_seq += [Delay(self.t_ge)]
                    temp_seq += [ge(-np.pi/2, X_AXIS)]

                if self.delay:
                    temp_seq += [Delay(self.delay)]

                temp_seq += [Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ])]
                temp_seq += [Delay(2000)]
                s.append(Join(temp_seq))

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs


    def get_ys(self, data=None):
        ys = super(wigner_line_cut, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

