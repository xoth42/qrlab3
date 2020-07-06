import matplotlib
matplotlib.interactive(True)
import os
import time
import lmfit 
import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec


filepath = 'C:\_Data\\'
hdf5_name = '0625cooldown_circulator - Copy (2).hdf5'
date = '20190716'
time_1 = '130920'
time_2 = '123511'
experiment = 'Magnet_Sweep_VNA'
max_field = .05
min_field = 0
f = h5.File(filepath + hdf5_name, 'r')
exp1 = f['/' + date + '/' + time_1 + '_' + experiment]
exp2 = f['/' + date + '/' + time_2 + '_' + experiment]
#y_keys = exp.keys()

mag = np.linspace(0,.05,101)
freq1 = exp1['freqs'].value
real1 = exp1['realS21'].value
imag1 = exp1['imaginaryS21'].value

freq2 = exp2['freqs'].value
real2 = exp2['realS21'].value
imag2 = exp2['imaginaryS21'].value
max_phase = 0
ind_freq = 0
ind_field = 0
phase_diff_array = np.zeros((len(real1),len(real1[0])))
for i in range(len(freq1)):
    count = 0
    for j in range(len(real1)):
        phase1 = np.arctan(imag1[j][i]/real1[j][i]) + np.pi 
        phase2 = np.arctan(imag2[j][i]/real2[j][i]) + np.pi 
        phase_diff = phase2-phase1 
#        if phase_diff < .5 and j > 0 and phase_diff_array[j-1,i] > 2.5:
#            phase_diff = phase_diff + 2*np.pi
#        if phase_diff > 2.5 and j > 0 and phase_diff_array[j-1,i] > .5:
#            phase_diff = phase_diff - 2*np.pi
#            count = count - 1
        phase_diff_array[j][i] = phase_diff
        if phase_diff > max_phase:
            max_phase = phase_diff
            ind_freq = i
            ind_field = j
        else:
            continue
print(max_phase,freq1[ind_freq],(ind_field*(max_field-min_field)/len(real1)+min_field))
pl.figure()
pl.pcolormesh(np.linspace(0,0.05,101),np.linspace(8,12,1601),np.transpose(phase_diff_array),cmap = 'RdBu')
pl.colorbar()
pl.show()
#pl.pcolor(mag,freq1,phase_diff_array)
#pl.show()
if subtract:
    f_s = h5.File(filepath + hdf5_name_s, 'r')
    exp_s = f_s['/' + date_s + '/' + time_s + '_' + experiment_s]
    y_keys_s = exp_s.keys()
    #print(y_keys)
    
    #y_keys.remove(x_key)
    #y_keys.remove(x2_key)
    freq_s = exp_s['freqs'].value

    real_s = exp_s['real'].value
    imag_s = exp_s['imaginary'].value
    real = real - real_s
    imag = imag - imag_s
    
    
    mag = 10*np.log10(real**2 + imag**2)

fig = pl.figure()
gs = gridspec.GridSpec(1, 2)
fig.add_subplot(gs[0])
fig.add_subplot(gs[1])



fig.axes[1].plot(real[0],imag[0])
fig.axes[0].plot(freq[0]/1e9,mag[0])






freqs = freq[0]
datas = real + 1j*imag