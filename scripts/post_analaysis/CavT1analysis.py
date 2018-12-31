# -*- coding: utf-8 -*-
"""
Created on Fri Jan 02 08:35:23 2015

@author: RSL
"""

import numpy as np
import h5py
import lmfit
import matplotlib.pyplot as plt
import math

def poisson_decay_fit_func(params, xs, ys, n):
    '''
    Poissonian distribution given photon projection:
    alpha = alpha0 * exp(-xs / tau)

    params:
        ofs = offset
        amp = amplitude
        alpha0 = initial displacement
        tau = decay constant for energy, i.e. <n>
    '''

    alphas = params['alpha0'].value * np.exp(-xs / 2.0 / params['tau'].value)
#    nbars = params['alpha0'].value**2 * np.exp(-xs / params['tau'].value)
    nbars = alphas**2 + params['nth'].value
    vals = params['ofs'].value + params['amp'].value * nbars**n / math.factorial(n) * np.exp(-nbars)
    return ys - vals

def analysis(xdata, ydata):

    xs = xdata[0:]/1e3
    ys = ydata[0:]
    fig = plt.figure()
    fig.add_subplot(211)
    fig.axes[0].plot(xs, ys, 'ks', ms=3)

    params = lmfit.Parameters()
    params.add('amp', value=(np.max(ys)-np.min(ys)), min=0)
    params.add('alpha0', value=2.0, min=0.5, max=10)
    params.add('nth', value=0, vary=False)#min=0, max=0.4)
    params.add('tau', value=xs[-1]/5.0, min=0, max=20e3)
    params.add('ofs', value=np.max(ys))
    result = lmfit.minimize(poisson_decay_fit_func, params, args=(xs, ys, 0))
    lmfit.fit_report(params)

    txt = 'Fit, Amp=%.03f\nT1=%.02f +- %.02f us\na0 = %.03f +- %.03f\nnth = %.03f +- %.03f' % (params['amp'].value, params['tau'].value, params['tau'].stderr, params['alpha0'].value, params['alpha0'].stderr, params['nth'].value, params['nth'].stderr)
    ys_model = -poisson_decay_fit_func(params, xs, 0, 0)
    fig.axes[0].plot(xs, ys_model, label=txt)
    fig.axes[0].legend(loc=0)
    fig.axes[0].set_ylabel('Intensity [AU]')
    fig.axes[0].set_xlabel('Delay [us]')

    fig.add_subplot(212)
    fig.axes[1].plot(xs, ys - ys_model)
    fig.canvas.draw()
    return params


qubit = h5py.File('C:\\_data\\150507 Cooldown\\DblCoax2.hdf5','r')
exp = qubit['20150509']['202412_CavT1']
xdata = np.array(exp['delays'])
ydata = np.array(exp['avg'])
if 0:
    ydata2D = np.reshape(ydata, (-1, 2)).transpose()
    ydata = ydata2D[0]-ydata2D[1]
result = analysis(xdata, ydata)

