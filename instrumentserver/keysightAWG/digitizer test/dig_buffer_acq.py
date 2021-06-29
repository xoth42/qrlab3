""" This file is used to test the capabilites of the digitizer and the buffer pool.
This file loads data onto the awg, runs the hvi and captures with the digitizer"""



import numpy as np
import matplotlib.pyplot as pl
import keysightSD1 as key
from CompiledHVI import CompiledHVI
import time
import gc
import mclient




nsamples = 150 #number of data points taken ever acquisition

npoints = 1 # number of different experimental points, each will be averaged
naverages = 100 # total number of averages per point
ntransfers = 1  # number of blocks it takes the dig data to transfer to the pc

data_channel = 1
ref_channel = 2

dig = mclient.instruments['dig']
#hvi.stop()


data, ref = dig.test_dig(nsamples, npoints, naverages, ntransfers)

#hvi.stop()

#means /= np.max(means)

fig = pl.figure()
for i in range(npoints):
    ax1 = fig.add_subplot(2, npoints, i+1)
    ax1.plot(data[i])
#    for j in range(naverages):
#        ax1.plot(data[data_channel, j, i])
    if i>0:ax1.set_yticks([])
    
    ax2 = fig.add_subplot(2, npoints, i+1+npoints)
    ax2.plot(ref[i])
    
    ax1.set_xlim(75, 100)
    ax2.set_xlim(75, 100)


    
    
    


