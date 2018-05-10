# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 13:01:31 2017

@author: WangLab
"""

import numpy as np
import matplotlib.pyplot as pl
import lmfit


x = np.linspace(0, 100, 101)
data = np.exp(-(x / 50) * np.sin(5 * x)
    
pl.plot(x , data)
pl.show()


def myfit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phase
    '''
    
    
    
    ofs = params['ofs']
    amp = params['amp']
    tau = params['tau']
    freq = params['freq']
    phase = params['phase']

    model = ofs + amp * np.exp(-(x / tau)) * np.sin(2 * np.pi * freq * x + phase)

    return data - model
    

    
params = lmfit.Parameters()
params.add('ofs', value=0)
params.add('amp', value=1)
params.add('tau', value=500)
params.add('freq', value=5)
params.add('phase', value=0)
  
result = lmfit.minimize(myfit, params, args=(x, data))
lmfit.report_fit(params)
pl.plot(x, myfit(params, x, data))