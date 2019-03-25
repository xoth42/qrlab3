# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 08:09:16 2018

@author: wanglab
"""

import numpy as np
import matplotlib.pyplot as plt
import lmfit

def double_exp_sin_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
#    est = params['ofs'].value + params['amplitude'].value * np.exp(-x / params['tau'].value) + params['amplitude2'].value * np.exp(-x / params['tau2'].value)
    exp1 = np.exp(-x / params['tau1'].value)
    exp2 = np.exp(-x / params['tau2'].value)
    est = params['ofs'].value + (params['amp1'].value * exp1 + params['amp2'].value * exp2) * sine
    return data - est

def double_exp_decay(params, x, data):
    est = params['ofs'].value + params['amplitude'].value * np.exp(-x / params['tau'].value) + params['amplitude2'].value * np.exp(-x / params['tau2'].value)
    return data - est


def analysis(xs, ys, fig):
#    xs = meas.delays
#    ys, fig = meas.get_ys_fig(data, fig)

#    fig.axes[0].plot(xs/1e3, ys, 'ks', ms=3)

    amp0 = (np.max(ys) - np.min(ys)) / 2
    off0 = (np.max(ys) + np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])
    print 'Delta f estimate: %.03f kHz' % (f0 * 1e6)

    params = lmfit.Parameters()
    params.add('ofs', value=off0)
    params.add('amp1', value=amp0/2, min=0)
    params.add('amp2', value=amp0/2, vary=False)
    params.add('amp2', value=0, vary=False)
    params.add('tau1', value=xs[-1]/100, min=10, max=4e6)
    params.add('tau2', value=xs[-1], min=10, max=4e6)
    params.add('freq', value=f0, min=0)
    params.add('phi0', value=0, min=-1.2*np.pi, max=1.2*np.pi)
    result = lmfit.minimize(double_exp_decay, params, args=(xs, ys))
    lmfit.report_fit(result.params)

    fig.axes[0].plot(xs/1e3, -double_exp_sin_fit(result.params, xs, 0), label='Fit, tau1=%.03f us, tau2=%.03f us, df=%.03f kHz'
            %(result.params['tau1'].value/1000, result.params['tau2'].value/1000))#, result.params['freq'].value*1e6))
    fig.axes[0].legend()
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Time [us]')
    fig.axes[1].plot(xs/1e3, double_exp_sin_fit(result.params, xs, ys), marker='s')
    fig.canvas.draw()


xs = np.concatenate((np.linspace(0e3, 50e3, 26), np.linspace(60e3, 1250e3, 55)))
ys = t1.get_ys()
#xs = np.linspace(0, 2*np.pi, 400)
#ys = np.sin(x**2)
fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(xs/1e3, ys, 'ks', ms=3)
analysis(xs, ys, fig)

