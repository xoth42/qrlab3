# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 10:05:05 2017

@author: Wang Lab
"""

import numpy as np
import matplotlib.pyplot as plt
from pulseseq.sequencer import *
from pulseseq.pulselib import *
from measurement import Measurement1D
import h5py
import lmfit

'''This will not work yet because it should run another RB measurement first and then have an array of saved data to fit to.'''

''' Replace every 'b' with 'data'. '''

def exp_decay(params, x, b):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return b - est

def double_exp_decay(params, x, b):
    est = params['ofs'].value + params['amplitude'].value * np.exp(-x / params['tau'].value) + params['amplitude2'].value * np.exp(-x / params['tau2'].value)
    return b - est


def analysis(meas, b=None, fig=None):
    plt.figure()

    plt.plot(xs, b, 'ks', ms=3)

    params = lmfit.Parameters()
    params.add('ofs', value=np.min(b))
    params.add('amplitude', value=np.max(b))
    params.add('tau', value=xs[-1]/2.0, min=50.0)
    result = lmfit.minimize(exp_decay, params, args=(xs, b))
#        lmfit.report_fit(params)
#        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -exp_decay(result.params, xs, 0), label='Fit, tau = %.03f us'%(result.params['tau'].value/1000.))
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs, exp_decay(result.params, xs, b), marker='s')

    fig.canvas.draw()
    return params

