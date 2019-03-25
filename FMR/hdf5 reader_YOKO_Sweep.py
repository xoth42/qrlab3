import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

#from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
#from scripts.single_cavity import WignerbyParity
    
#import mclient
#from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json


''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
date = '20190323'
time = '013603'
experiment = 'Current_Sweep_YOKO'

''' Primary x axis and secondary if 2d'''
#x_key = 'freqs'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()
#print(y_keys)

#y_keys.remove(x_key)
#y_keys.remove(x2_key)
freq = exp['freqs'].value
current = exp['currents'].value
real = exp['realS11'].value
imag = exp['imaginaryS11'].value

'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
if current.any() < 0.5:
    field = current*529.37 + 0.49
else:
    field = -268.93 * (current)**2 + 839.69*current - 88.67

'''Plot'''
pl.figure()
mag = 20*np.log10(real**2 + imag**2)
Z = np.transpose(mag)
X,Y = np.meshgrid(field, freq)
pl.pcolormesh(X,Y,Z)
pl.colorbar()
pl.title('YIG FMR Spectrum, S11 Measurement')
pl.xlabel('Magnetic Field(mT)')
pl.ylabel('Frequency(GHz)')





