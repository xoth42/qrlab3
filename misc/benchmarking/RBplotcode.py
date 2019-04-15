# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 21:04:23 2017

@author: Wang Lab
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import lmfit

data= np.loadtxt('rawdata2.txt')


ave=np.mean(data, axis=0)

data_normalized=(data - 0.65) / 6.29
std = np.std(data_normalized, axis = 0)/np.sqrt(int(np.shape(data_normalized)[0]))


ave_oneless = np.delete(ave, 0)
std_oneless = np.delete(std, 0)
x_data = np.arange(6, 151, 3)
ave_normalized = (ave_oneless - 0.65)/6.29  

    
xs = x_data
ys=ave_normalized #- 0.5
err=std_oneless

def exp_decay(params, x, data,err):
    est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
    return (data-est)/err

def exp_decay2(params, x):
    est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
    return est

params=lmfit.Parameters()
params.add('amplitude', value=0.5)
params.add('ofs', value=0.5, vary=False)
params.add('tau', value=100)

ax = plt.gca()
result= lmfit.minimize(exp_decay, params, args=(xs,ys,err))
lmfit.report_fit(result.params)
plt.plot(np.linspace(0,151,51), exp_decay2(result.params,np.linspace(0,151,51)))
plt.errorbar(xs,ys,std_oneless, linestyle='None')
plt.plot(xs,ys, 'ro', markersize=4, color='r', linestyle='None')
#plt.yscale('log')
ax.set_ylabel('Average fidelity')
ax.set_xlabel('Number of computational gates')

pl.savefig("finalRBplot.png")
pl.show()

