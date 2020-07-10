# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 12:53:22 2019

@author: WangLab
"""
import matplotlib
matplotlib.interactive(True)
import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
#300kHz-14 GHz

filepath = 'C:\_Data\\'
hdf5_name = '0808cooldown_FMR - Copy.hdf5'
date_DC = '20190823'
time_DC = '125113'
experiment = 'SingleTraceNoAsync'
f = h5.File(filepath + hdf5_name, 'r')
exp_DC = f['/' + date_DC + '/' + time_DC + '_' + experiment]
freq_DC = exp_DC['freqs'].value[0]
real_DC = exp_DC['real'].value[0]
imag_DC = exp_DC['imaginary'].value[0]
mag_DC = (real_DC**2 + imag_DC**2)**.5
dB_DC = 20*np.log10(mag_DC)
f.close()

date_DCKL = '20190823'
time_DCKL = '154529'
experiment = 'SingleTraceNoAsync'
f = h5.File(filepath + hdf5_name, 'r')
exp_DCKL = f['/' + date_DCKL + '/' + time_DCKL + '_' + experiment]
freq_DCKL = exp_DCKL['freqs'].value[0]
real_DCKL = exp_DCKL['real'].value[0]
imag_DCKL = exp_DCKL['imaginary'].value[0]
mag_DCKL = (real_DCKL**2 + imag_DCKL**2)**.5
dB_DCKL = 20*np.log10(mag_DCKL)
f.close()


date_A = '20190823'
time_A = '124557'
f = h5.File(filepath + hdf5_name, 'r')
exp_A = f['/' + date_A + '/' + time_A + '_' + experiment]
freq_A = exp_A['freqs'].value[0]
real_A = exp_A['real'].value[0]
imag_A = exp_A['imaginary'].value[0]
mag_A = (real_A**2 + imag_A**2)**.5
dB_A = 20*np.log10(mag_A)
f.close()


date1 = '20190822'
time1 = '175717'
f = h5.File(filepath + hdf5_name, 'r')
#following code is if data is part of 2D plot
experiment_S = 'Power_Sweep_VNA'
index = -2

exp1 = f['/' + date1 + '/' + time1 + '_' + experiment_S]
freq12 = exp1['freqs'].value
real12 = exp1['realS21'].value[index]
imag12 = exp1['imaginaryS21'].value[index]
mag12 = (real12**2 + imag12**2)**.5
dB12 = 20*np.log10(mag12) - dB_DC
f.close()

date2 = '20190823'
time2 = '121637'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq21 = exp2['freqs'].value[0]
real21 = exp2['real'].value[0]
imag21 = exp2['imaginary'].value[0]
mag21 = (real21**2 + imag21**2)**.5
dB21 = 20*np.log10(mag21) - dB_DCKL
f.close()


date2 = '20190823'
time2 = '120855'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag13 = (real**2 + imag**2)**.5
dB13 = 20*np.log10(mag13) - dB_A
f.close()

date2 = '20190823'
time2 = '121248'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag11 = (real**2 + imag**2)**.5
dB11 = 20*np.log10(mag11) - dB_DCKL
f.close()


date2 = '20190823'
time2 = '122102'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag23 = (real**2 + imag**2)**.5
dB23 = 20*np.log10(mag23) - dB_A
f.close()

date2 = '20190823'
time2 = '122329'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag22 = (real**2 + imag**2)**.5
dB22 = 20*np.log10(mag22) - dB_DC
f.close()

#performance = mag2/mag1
#pl.figure()
#pl.title('Commercial Circulator Performancelow temp')
#pl.plot(freq1,performance)
#pl.ylabel('S21/S12')
#pl.xlabel('frequency GHz')
#pl.show()


pl.figure()
#pl.plot(freq/1e9,dB13, label = 'S13')
#pl.plot(freq/1e9,dB12, label = 'S12')
pl.title('S13/S12')
pl.plot(freq/1e9,(dB13-dB12))
pl.xlim(6,10)
pl.ylabel('dB')
pl.xlabel('frequency (GHz)')
pl.legend()
pl.show()

'''
#7-9
#port 3 as referance and other ports + attenuator and - directional coupler
filepath = 'C:\_Data\\'
hdf5_name = '0808cooldown_FMR - Copy (6).hdf5'
date_DC = '20190823'
time_DC = '125043'
experiment = 'SingleTraceNoAsync'
f = h5.File(filepath + hdf5_name, 'r')
exp_DC = f['/' + date_DC + '/' + time_DC + '_' + experiment]
freq_DC = exp_DC['freqs'].value[0]
real_DC = exp_DC['real'].value[0]
imag_DC = exp_DC['imaginary'].value[0]
mag_DC = (real_DC**2 + imag_DC**2)**.5
dB_DC = 20*np.log10(mag_DC)
f.close()

date_DCKL = '20190823'
time_DCKL = '154752'
experiment = 'SingleTraceNoAsync'
f = h5.File(filepath + hdf5_name, 'r')
exp_DCKL = f['/' + date_DCKL + '/' + time_DCKL + '_' + experiment]
freq_DCKL = exp_DCKL['freqs'].value[0]
real_DCKL = exp_DCKL['real'].value[0]
imag_DCKL = exp_DCKL['imaginary'].value[0]
mag_DCKL = (real_DCKL**2 + imag_DCKL**2)**.5
dB_DCKL = 20*np.log10(mag_DCKL)
f.close()


date_A = '20190823'
time_A = '124709'
f = h5.File(filepath + hdf5_name, 'r')
exp_A = f['/' + date_A + '/' + time_A + '_' + experiment]
freq_A = exp_A['freqs'].value[0]
real_A = exp_A['real'].value[0]
imag_A = exp_A['imaginary'].value[0]
mag_A = (real_A**2 + imag_A**2)**.5
dB_A = 20*np.log10(mag_A)
f.close()


date1 = '20190822'
time1 = '231222'
f = h5.File(filepath + hdf5_name, 'r')
#following code is if data is part of 2D plot
experiment_S = 'Power_Sweep_VNA'
index = -2

exp1 = f['/' + date1 + '/' + time1 + '_' + experiment_S]
freq12 = exp1['freqs'].value
real12 = exp1['realS21'].value[index]
imag12 = exp1['imaginaryS21'].value[index]
mag12 = (real12**2 + imag12**2)**.5
dB12 = 20*np.log10(mag12) - dB_DC
f.close()

date2 = '20190823'
time2 = '121720'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq21 = exp2['freqs'].value[0]
real21 = exp2['real'].value[0]
imag21 = exp2['imaginary'].value[0]
mag21 = (real21**2 + imag21**2)**.5
dB21 = 20*np.log10(mag21) - dB_DCKL
f.close()


date2 = '20190823'
time2 = '120932'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag13 = (real**2 + imag**2)**.5
dB13 = 20*np.log10(mag13) - dB_A
f.close()

date2 = '20190823'
time2 = '121207'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag11 = (real**2 + imag**2)**.5
dB11 = 20*np.log10(mag11) - dB_DCKL
f.close()


date2 = '20190823'
time2 = '121944'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag23 = (real**2 + imag**2)**.5
dB23 = 20*np.log10(mag23) - dB_A
f.close()

date2 = '20190823'
time2 = '122404'
f = h5.File(filepath + hdf5_name, 'r')
exp2 = f['/' + date2 + '/' + time2 + '_' + experiment]
freq = exp2['freqs'].value[0]
real = exp2['real'].value[0]
imag = exp2['imaginary'].value[0]
mag22 = (real**2 + imag**2)**.5
dB22 = 20*np.log10(mag22) - dB_DC
f.close()

#performance = mag2/mag1
#pl.figure()
#pl.title('Commercial Circulator Performancelow temp')
#pl.plot(freq1,performance)
#pl.ylabel('S21/S12')
#pl.xlabel('frequency GHz')
#pl.show()


pl.figure()
#pl.plot(freq/1e9,dB23, label = 'S23')
#pl.plot(freq/1e9,dB21, label = 'S21')
pl.title('S21/S23')
pl.plot(freq/1e9,(dB21-dB23))
pl.ylabel('dB')
pl.xlabel('frequency (GHz)')
pl.legend()
pl.show()
'''