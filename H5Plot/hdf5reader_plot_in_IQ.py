# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:40:50 2019

@author: Wang_Lab
"""

import os
import time
if 0:
    os.system(r'C:\qrlab\start.bat')
    time.sleep(1)

from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
from scripts.single_cavity import WignerbyParity
    
import mclient
from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from lib.math import fit

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = '1122cooldown_Circulator_cavity - Copy.hdf5'
date = '20191204'
time = '123442'
experiment = 'Rabi'

''' Primary x axis and secondary if 2d'''
x_key = 'amps'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()

    
xs = exp[x_key].value
data = exp['avg_pp'].value
data_c = exp['avg'].value


    
ys = data
fig = pl.figure()
fig.add_subplot(121)
fig.axes[0].plot(xs/1e6,ys)
fig.axes[0].set_xlabel('amps')
fig.axes[0].set_ylabel('Intensity (AU)')
fig.axes[0].legend()
fig.add_subplot(122)
fig.axes[1].plot(data_c.real, data_c.imag)
fig.axes[1].plot(0, 0)
fig.axes[1].set_xlabel('I')
fig.axes[1].set_ylabel('Q')
fig.axes[1].set_aspect('equal', 'box')
fig.axes[1].legend()

#    
#    fig.axes[0].plot(-xs/1e6, ys)

fig.canvas.draw()
f.close()