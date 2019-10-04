"""
performs Q function meausurement at every point with fixed amplitude alpha with varying angle from 0 to 2pi

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
    dx = np.min([np.abs(x - params['phase']), np.abs(x - params['phase'] - np.pi)], axis = 0)  #This has been corrected to -np.pi
    est = (params['background'] + params['amp'] * np.exp(-np.power(dx, 2.) / (2 * np.power(params['sigma'], 2.)))
                                + params['amp'] * np.exp(-np.power(np.pi - dx, 2.) / (2 * np.power(params['sigma'], 2.))))
    
    return data - est

def quadruple_gaussian(params, x, data):
    dx = np.min([np.abs(x - params['phase']), np.abs(x - params['phase'] - np.pi/2),
                 np.abs(x - params['phase'] - np.pi), np.abs(x - params['phase'] - np.pi * 3/2)], axis = 0)  #This has been corrected to -np.pi
    est = (params['background'] + params['amp'] * np.exp(-np.power(dx, 2.) / (2 * np.power(params['sigma'], 2.)))
                                + params['amp'] * np.exp(-np.power(np.pi/2 - dx, 2.) / (2 * np.power(params['sigma'], 2.)))
                                + params['amp'] * np.exp(-np.power(np.pi - dx, 2.) / (2 * np.power(params['sigma'], 2.)))
                                + params['amp'] * np.exp(-np.power(np.pi *3/2 - dx, 2.) / (2 * np.power(params['sigma'], 2.))))
    
    return data - est


def analysis(meas, data=None, fig=None):
    ys, fig = meas.get_ys_fig(data, fig)
    xs = meas.angles
    
    fig.axes[0].plot(xs, ys)
#    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Angle [radians]')
    if meas.fit:
        phase = xs[np.argmin(ys)]
        if phase > np.pi:
            phase -= np.pi
        
        params = lmfit.Parameters()
        params.add('background', value=max(ys))
        params.add('amp', value=np.min(ys)-np.max(ys), max = 0)
        params.add('sigma', value=np.pi/8, min=0)
        params.add('phase', value=phase, min=0, max=np.pi)
            
        result = lmfit.minimize(quadruple_gaussian, params, args=(xs, ys))
        lmfit.report_fit(result.params)
    
        fig.axes[0].plot(xs, -quadruple_gaussian(result.params, xs, 0))
        fig.canvas.draw()
        
        return result
    fig.canvas.draw()
    return None


class husimiq_angle_test(Measurement1D):

    def __init__(self, qubit_info, cav_info, npoints, alpha, delay = 1e3,
                 bgcor = False, fit = False, seq=None, postseq=None, **kwargs):
        self.qubit_info = qubit_info
        self.cav_info = cav_info
        self.npoints = npoints
        self.alpha= alpha
        self.delay = delay
        self.bgcor = bgcor
        self.fit = fit
        if seq is None:
            seq = Trigger(500)
        self.seq = seq
        self.postseq = postseq
    
        self.angles = np.linspace(0, 2 * np.pi, npoints)
        self.xs = self.angles
        if bgcor:
            npoints *= 2
                    
        super(husimiq_angle_test, self).__init__(npoints, infos=[qubit_info, cav_info], **kwargs)
        
        self.data.create_dataset('angles', data=self.angles)
        self.data.set_attrs(
                alpha = alpha,
        )

    def generate(self):
        s = Sequence()
        rs = self.qubit_info.rotate_selective
        c = self.cav_info.rotate
        for angle in self.angles:
            for i_bg in range(2):
                if i_bg == 1 and not self.bgcor:
                    continue

                s.append(self.seq)
                s.append(c(self.alpha, angle))

                if i_bg == 0:
                    s.append(rs(np.pi, X_AXIS))

                if self.delay:
                    s.append(Delay(self.delay))

                s.append(Combined([
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.readout_chan),
                    Constant(self.readout_info.pulse_len, 1, chan=self.readout_info.acq_chan),
                ]))
                s.append(Delay(800))

        s = self.get_sequencer(s)
        seqs = s.render(debug=False)
        return seqs


    def get_ys(self, data=None):
        ys = super(husimiq_angle_test, self).get_ys(data)
        if self.bgcor:
            return ys[::2] - ys[1::2]
        return ys

    def analyze(self, data=None, fig=None):
        return analysis(self, data, fig)

