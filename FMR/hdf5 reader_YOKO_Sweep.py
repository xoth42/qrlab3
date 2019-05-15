import matplotlib
matplotlib.interactive(True)
#from pulseseq import sequencer, pulselib
#from scripts.single_qubit import rabi
#from scripts.single_cavity import WignerbyParity
    
#import mclient
#from mclient import instruments

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
from matplotlib import gridspec

''' Path to the .hdf5 file '''
#filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
filepath = 'C:\_Data\\'
#hdf5_name = 'VNAtestJan30.hdf5'
hdf5_name = 'test.hdf5'
date = '20190331'
time = '230028'
experiment = 'test'

''' Primary x axis and secondary if 2d'''
x_key = 'freqs'
x2_key = 'currents'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]

#exp = f['C:\_Data\\YIG_Copper_Cavity_sweep_test.hdf5/20190328/124139_test']
y_keys = exp.keys()
print(y_keys)

y_keys.remove(x_key)
y_keys.remove(x2_key)
freqs = exp[x_key].value
currents = exp[x2_key].value
#Sij = exp.attrs['Sij_list']
Sij = ['S11','S21','S12','S22']
fig_name = exp.attrs['title']
print Sij
realdata = [0,0,0,0]
imagdata = [0,0,0,0]
for i in range(len(Sij)):
    realdata[i] = exp['real%s'%(Sij[i])].value
    imagdata[i] = exp['imaginary%s'%(Sij[i])].value

'''Conversion factor from Yoko current in mA to actual magnetic field in mT'''
if currents.any() < 0.5:
    field = currents*529.37 + 0.49
else:
    field = -268.93 * (currents)**2 + 839.69*currents - 88.67

'''Plot'''
#for i in range(len(Sij)):
#    pl.figure()
#    mag = 20*np.log10(real[i]**2 + imag[i]**2)
#    Z = np.transpose(mag)
#    X,Y = np.meshgrid(field, freq)
#    pl.pcolormesh(X,Y,Z)
#    pl.colorbar()
#    pl.title('YIG FMR Spectrum, %s Measurement'%(Sij[i]))
#    pl.xlabel('Magnetic Field(mT)')
#    pl.ylabel('Frequency(GHz)')
#    
#    pl.show()

fig = pl.figure()
fig.suptitle(filepath + hdf5_name +'/' + date + '/' + time + '_' + experiment)
a=[0,0,0,0]

if len(Sij) == 1:
#    gs=[0]
    gs= gridspec.GridSpec(1 , 1)
#            fig.axes[0].title = Sij[0]
else:
    gs = gridspec.GridSpec((len(Sij)-1)/2 + 1, 2)
    gs.update(wspace=0.5, hspace=0.4)
    
field = np.zeros(len(currents))     
for i in range(len(currents)):
    #Current-field relationship input below, for driving Yoko in current mode - BS, 3/20/19
    if currents[i] < 0.5:
        field[i] = currents[i]*529.37 + 0.49
    else:
        field[i] = -268.93 * (currents[i])**2 + 839.69*currents[i]-88.67

ampdata = np.zeros((len(Sij),len(currents), len(freqs)))
ampdata_a = np.zeros((len(Sij),len(freqs), len(currents)))
xs,ys = np.meshgrid(field, freqs/float(1e9))
gss=[0,0,0,0]
for k in range(len(Sij)):
#    if not len(Sij) == 1:
    gss[k] = gridspec.GridSpecFromSubplotSpec(1,2, subplot_spec=gs[k],width_ratios = (19,1))        
    fig.add_subplot(gss[k][0])
    fig.axes[k].set_title('%s%s'%(fig_name,Sij[k]))
    fig.axes[k].set_xlim(xs.min(), xs.max()+currents[1] - currents[0])
    fig.axes[k].set_ylim(ys.min(), ys.max())
    
#        ampdata = np.zeros((len(realdata),len(currentdata[0,:]), len(freqdata[0,:])))
#    imag = np.zeros((len(self.currents),len(self.freqs)))
    for i in range(len(currents)):
        ampdata[k][i] = 20*np.log10(np.sqrt(realdata[k][i,:]**2 + imagdata[k][i,:]**2))
#        ampdata[k][i] = imagdata[k][i,:]
#    print Z
#    field_a, freqdata = np.meshgrid(field, freqs)
    ampdata_a[k] = np.transpose(ampdata[k])
#    print ampdata_a[k]
#    phase = np.transpose(phase)
    a[k]=fig.axes[k].pcolormesh(xs, ys, ampdata_a[k])
#    Colorbar(ax = fig.axes[k], mappable = a, orientation = 'horizontal', ticklocation = 'top')
#    pl.colorbar( a[k] )#, ax = gs[k/2, k%2] )
    fig.axes[k].set_xlabel('Magnetic Field(mT)')
    fig.axes[k].set_ylabel('Frequency(GHz)')


for k in range(len(Sij)):
    fig.add_subplot(gss[k][1])
    pl.colorbar( a[k],fig.axes[len(Sij)+k])




