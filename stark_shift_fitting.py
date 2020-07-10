# -*- coding: utf-8 -*-
"""
Created on Mon Jul 08 14:11:55 2019

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)
from scipy.optimize import curve_fit
from scripts.single_cavity import VNA_single_trace_V2
import numpy as np
import lmfit
from lmfit import Parameters, minimize, fit_report
import matplotlib.pyplot as pl

params = Parameters()
params.add('slope',value = -.03) #GHz/mW
params.add('const',value = 8.6) #Hz

freq1 = np.array([8.5421,8.5369,8.5293,8.5237,8.5010,8.4938,8.4834,8.4750])
power_dbm1 = np.array([2.5,3,3.5,4,4.5,5,5.5,6])
#freq1 = np.array([8.4874,8.503,8.529,8.5451,8.5596,8.5847,8.5954,8.6043,8.6188])
#power_dbm1 = np.array([2.75,2,1,0,-1,-3,-4,-5,-7])
freq = np.array([8.6507,8.4287])
power_dbm = np.array([-100,5.0])
power_mw = 10**(power_dbm/10)
power_mw1 = 10**(power_dbm1/10)
power_mw2 = np.array([0,4])
def stark_shift(params,w,data):
    a = params['slope']
    b = params['const']
    model = a*w + b
    return (model-data)

result = minimize(stark_shift,params,args = (power_mw1,),kws = {'data':freq1})
print(fit_report(result))
y = result.params['slope']*power_mw2 + result.params['const']
pl.figure()
pl.title('Comparison of Stark Shifts between qubits')
pl.plot(power_mw1,freq1, label = 'qubit 2')
pl.plot(power_mw2,y,'--')
pl.plot(power_mw,freq, label = 'qubit 1')
pl.legend()
pl.show()
#def expect(power_dbm, slope, const):
#    power = 10**(power_dbm/10)
#    return (slope*power + const)
#    
#print(expect(-10, result.params['slope'], result.params['const']))