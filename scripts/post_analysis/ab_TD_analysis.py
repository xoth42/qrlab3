# -*- coding: utf-8 -*-
"""
Created on Sun July 10 23:34:46 2019

@author: Wang_Lab
"""

'''
Reading data from ab time domain decay data from HDF5 file to perform analysis. 

Chen Wang
'''

#import os
#import time
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import lmfit
#import json
#import mclient

#from FWM import ab_time_domain

def exp_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-x / params['tau'].value)
    return data - est

def fit_exp_decay(axes, line_index=0, amp_init=None, tau_init=None, vary_offset=True, fit_start=0, fit_stop=0, label=''):
    line = axes.lines[line_index]
    xdata = line.get_xdata()
    ydata = line.get_ydata()
    xs = xdata[fit_start:len(xdata)-fit_stop]
    ys = ydata[fit_start:len(ydata)-fit_stop]
    if amp_init is None:
        amp_init = np.max(ys)
    if tau_init is None:
        tau_init = xs[-1]
    params = lmfit.Parameters()
    params.add('ofs', value=0, vary=vary_offset)
    params.add('amplitude', value=amp_init)
    params.add('tau', value=tau_init)
    result = lmfit.minimize(exp_decay, params, args=(xs, ys))
    lmfit.report_fit(result.params)
    fit_ydata = -exp_decay(result.params, xs, 0)
    if result.params['tau'].value < 1000 and result.params['tau'].value > 0:
        label = label+': tau = %.01f us +/- %.01f us'%(result.params['tau'].value, result.params['tau'].stderr)
    else:
        label = label+': tau is long'
    axes.plot(xs, fit_ydata, label=label, color=line.get_color())
    axes.legend(loc=0)
    axes.set_ylabel('Intensity [AU]')
    axes.set_xlabel('Time [us]')

    return fit_ydata

def Prob_est(data, bg, bg_good=37.0, e_good=10.0, floor=7.0):
    heating_ratio = (bg-floor)/(bg_good-floor)
    e_state = (e_good-floor)*heating_ratio + floor
    probability = (bg-data)/(bg-e_state)
    return probability
    

''' Path to the .hdf5 file '''
filepath = 'C:\_Data\Analysis'
hdf5_name = '\June19PumpCat-copy3.hdf5'
#hdf5_name = '20190204 Cooldown.hdf5'
#date = '20190709'
experiment = 'ab_time_domain'
bgcor = True   # This info should have been written as attributes


'''Coherent state initial states'''
#qubit_list = ['a0b0', 'a1b0', 'a1b1', 'a2b1']  # This info should have been written as attributes
#qubit_list = ['a0b0', 'a1b0', 'a0b1', 'a2b0', 'a1b1']  # This info should have been written as attributes
#datetime = '20190710/101740'   #2.0dBm
#datetime = '20190709/212641'   #6.0dBm
#datetime = '20190709/230932'   #8.0dBm
#datetime = '20190710/135044'   #8.0dBm
#datetime = '20190709/180058'   #9.5dBm  somewhat heated
#datetime = '20190710/084238'   #9.5dBm  not enough averaging
#datetime = '20190710/023515'   #10.7dBm
#datetime = '20190710/005224'   #11.6dBm
#datetime = '20190710/121235'   #11.6dBm

qubit_list = ['a0b0', 'a1b0', 'a0b1', 'a2b0', 'a1b1']  # This info should have been written as attributes
datetime = ['20190708/173859','20190709/075900']   # 11.6dBm low disp

'''pumped up initial states'''
#qubit_list = ['a0b0', 'a1b1', 'a2b2']  # This info should have been written as attributes
#datetime = '20190711/113154'    #2.0dBm 
#datetime = ['20190711/144247','20190711/153118']    #4.5dBm 
#datetime = '20190711/103237'    #6.0dBm 
#datetime = '20190711/120639'    #6.0dBm more pts near 0
#datetime = '20190710/161551'    #8.0dBm 
#datetime = '20190710/223447'    #9.5dBm
#datetime = '20190711/133111'    #10.7dBm
#datetime = '20190709/133637'    #11.6dBm no a2b2
#datetime = '20190709/114000'   #11.6dBm

f = h5.File(filepath + hdf5_name, 'r')
#exp = f['/' + date + '/' + time + '_' + experiment]

if type(datetime) == list:
    ys = 0
    for i in range(len(datetime)):
        exp = f['/' + datetime[i] + '_' + experiment]
        xs = exp['delays']
#        xs = exp['decaytimes']
        new_ys = exp['avg_pp']
        delays = xs.value/1000.0
        ys = (ys*i+new_ys.value)*1.0/(i+1)
    datetime = datetime[0]+'...'+datetime[-1]
else:
    exp = f['/' + datetime + '_' + experiment]
#    xs = exp['delays']
    xs = exp['decaytimes']
    ys = abs(exp['avg'].value)
    delays = xs.value/1000.0
num_delays = len(xs)
num_qlist = len(qubit_list)

ydata = {}
ydata['bg'] = ys[num_qlist*num_delays: (num_qlist+1)*num_delays]   
fig, ax = plt.subplots(2, 1)
fig.suptitle(hdf5_name+'/'+datetime+'_'+experiment, fontsize=12)
ax[0].plot(delays, ydata['bg'], 'ks', ms=3)
fit_bg = fit_exp_decay(ax[0])

fitdata = {}
pdata = {}
for i, info in enumerate(qubit_list):
    ydata[info] = ys[i*num_delays: (i+1)*num_delays]
    pdata[info] = Prob_est(ydata[info], fit_bg)
#    ax[1].plot(delays, fit_bg-ydata[info], marker='s', label=info)
    ax[1].plot(delays[1:len(delays)], pdata[info][1:len(delays)], marker='s', linestyle='', label=info)

for i in [0, 4]:
    fitdata[qubit_list[i]] = fit_exp_decay(ax[1], i, amp_init=-0.5, tau_init=10, fit_start=0, label=qubit_list[i])
#for i in [2]:
#    fitdata[qubit_list[i]] = fit_exp_decay(ax[1], i, amp_init=0.1, tau_init=5, fit_start=0, fit_stop=0, label=qubit_list[i])#, vary_offset=False)
    
ax[1].set_ylabel('Probability')#Intensity [AU]')
ax[1].set_xlabel('Time [us]')
