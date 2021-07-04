
'''
plot time rabi results

Yingying
'''



import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
from scripts.single_qubit import timerabi
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
import lmfit


def fit_timerabi(params, x, data):
    est = (params['ofs'].value - np.exp(-x / params['tau']) *params['amp'].value 
            * np.cos(2*np.pi*x / params['period'].value + params['phase'].value))
    return data  - est




''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '20190204 Cooldown.hdf5'
date = '20190410'
time = '112906'
#time = '143054'

experiment = 'TimeRabi'

''' Primary x axis and secondary if 2d'''
x_key = 'times'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = list(exp.keys())
print(y_keys)

y_keys.remove(x_key)
#y_keys.remove(x2_key)


    
qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')
#qubit2_info = mclient.get_qubit_info('qubit2tone')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#cavity_infoB = mclient.get_qubit_info('cavityBob')

#toload = ['qubit1ge', 'readout']
#mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration

#qubits = mclient.get_qubits()
#qubit_info = mclient.get_qubit_info('qubit1ge')
#tr = timerabi.TimeRabi(qubit_info, np.linspace(1, 400, 180), amp=0.4)

    
#spec = ssbspec.SSBSpec(qubit_info, np.concatenate((
#                                   np.linspace(-5.0e6, -3.4e6, 51), 
#                                   np.linspace(-1.8e6, -0.9e6, 50), 
#                                   np.linspace(-.5e6, .5e6, 50),
#                                   )), 
#                       seq=None, plot_seqs=False)
xs = exp[x_key].value
data = exp['avg_pp'].value
#spec.avg_data = exp['avg_pp']
#spec.analyze(data = data)
#fig = spec.fig

#xs = -1*spec.detunings /1e6
ys = data

fig = pl.figure()
pl.rcParams.update({'font.size':11})
#title = self.title
#fig.suptitle(title)
fig.add_subplot(111)

#gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])

#fig.add_subplot(gs[0])
#fig.add_subplot(gs[1])

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
##txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 0, result.params['period'].value, 0, result.params['period'].value/2 )
#txt = 'Amp = %.03f +- %.03e\nPeriod = %.03f +- %.03e\nPi amp = %.06f' % (result.params['amp'].value, 
#                                                                         result.params['amp'].stderr, 
#                                                                         result.params['period'].value, 
#                                                                         result.params['period'].stderr, 
#                                                                         result.params['period'].value/2 )
ys = (ys-result.params['ofs'].value)/result.params['amp'].value/2 +0.5
fig.axes[0].plot(xs, ys, 'ks', ms=3)
fig.axes[0].plot(np.linspace(0,xs[-1],10*len(xs)), (-fit_timerabi(result.params, np.linspace(0,xs[-1],10*len(xs)), 0)-result.params['ofs'].value)/result.params['amp'].value/2 +0.5)#, label=txt)
#fig.axes[0].plot(xs, -fit_timerabi(result.params, xs, 0))
#fig.axes[1].plot(xs, fit_timerabi(result.params, xs, ys), marker='s')

#    lmfit.report_fit(params)
lmfit.report_fit(result.params)

fig.axes[0].set_ylabel('Excitatiom probability ', fontsize = 15)
fig.axes[0].set_xlabel('Pulse time (ns)', fontsize = 15)
fig.axes[0].spines['left'].set_linewidth(2)
fig.axes[0].spines['right'].set_linewidth(2)
fig.axes[0].spines['top'].set_linewidth(2)
fig.axes[0].spines['bottom'].set_linewidth(2)
fig.axes[0].tick_params(direction = 'in')
#fig.axes[0].legend(loc=0)
pl.xlim(0,xs[-1]*1.05)
pl.ylim(0,1)
fig.canvas.draw()


