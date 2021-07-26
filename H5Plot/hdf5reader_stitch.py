import os
import time
if 0:
    os.system(r'C:\qrlab-3\start.bat')
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
filepath = 'C:/_Data/'
hdf5_name = 'AQEC-11-2019.hdf5'
date_list = ['20191107']*5 #+ ['20191107']*3
time_list = ['184744','193756','202807','211817','220827']


experiment = 'WignerFunction'

#num_exp = len(date_list)
num_exp = 5
N = 35
#expn = N/num_exp
expn = 7

''' Primary x axis and secondary if 2d'''
x_key = 'displacements'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')
xs = np.zeros((N, N))
ys = np.zeros((N, N))
data = np.zeros((N, N))

for i in range(num_exp):
    exp = f['/' + date_list[i] + '/' + time_list[i] + '_' + experiment]
    displacements = np.array(exp['displacements'].value)
    d = np.array(exp['avg_pp'].value[::2] - exp['avg_pp'].value[1::2]).reshape(displacements.shape)
    for j in range(N):
        xs[j, i*expn:(i+1)*expn] = (np.real(displacements))[j]
        ys[j, i*expn:(i+1)*expn] = (np.imag(displacements))[j]
        data[j, i*expn:(i+1)*expn] = d[j]
        
data /= -130


pl.figure()
pc = pl.pcolormesh(xs, ys, data, vmin=-1, vmax=1, cmap=pl.get_cmap('RdBu_r'))
pl.colorbar(pc)

pl.xlim(xs.min(), xs.max())
pl.ylim(ys.min(), ys.max())
#    if meas.zmin is not None and meas.zmax is not None:  (was trying to force set data range for color bar)
#        ax.set_zlim(meas.zmin, meas.zmax())
pl.xlabel(r'$Re \{\alpha \}$')
pl.ylabel(r'$Im \{\alpha \}$')


#y_keys.remove(x2_key)


    
#qubit_info = mclient.get_qubit_info('qubit1ge')
#ef_info = mclient.get_qubit_info('qubit1ef')

#cavity_infoR = mclient.get_qubit_info('cavity1R')
#cavity_infoA = mclient.get_qubit_info('cavityAlice')
#cavity_infoB = mclient.get_qubit_info('cavityBob')

#toload = ['qubit1ge', 'readout']
#mclient.load_settings_from_file(filepath + 'settings/' + date + '/' + time + '.set', toload)    # Last time-Rabi callibration

#qubits = mclient.get_qubits()
#qubit_info = mclient.get_qubit_info('qubit1ge')

#tr1 = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA, t_ge=300, t_gf=0,
#                                         amax=1.2, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                                         seq=None, delay=5, saveas=None, bgcor=False, keep_data=False)
#time.sleep(1)
#tr2 = WignerbyParity.WignerFunction(qubit_info, ef_info, cavity_infoA, t_ge=300, t_gf=0,
#                                         amax=1.2, N=13, amaxx=None, Nx=None, amaxy=None, Ny=None,
#                                         seq=None, delay=5, saveas=None, bgcor=False, keep_data=False)
#tr1.displacements = exp1[x_key].value + 1.3
#tr2.displacements = exp2[x_key].value - 1.3
#
#tr1.xs = np.real(tr1.displacements[0])
#tr2.xs = np.real(tr2.displacements[0])

#tr.ys = np.imag(tr.displacements[:1][0])
#data1 = exp1['avg_pp'].value[::2] - exp1['avg_pp'].value[1::2]
#data1 /= -90
#
#data2 = exp2['avg_pp'].value[::2] - exp2['avg_pp'].value[1::2]
#data2 /= -90
#tr.analyze(data = data)
#fig = tr.fig




if 0:
    zs, fig = tr1.get_ys_fig(data1)
    data1 = data1.reshape(len(tr1.xs), len(tr1.ys))
    data2 = data2.reshape(len(tr2.xs), len(tr2.ys))

    xs1, ys1 = tr1.get_plotxsys()
    xs2, ys2 = tr2.get_plotxsys()
    xs1 += 1.3
    xs2 -= 1.3
    xs = np.concatenate((xs1, xs2))
    ys = np.concatenate((ys1, ys2))
    zs = np.concatenate((data1, data2))
    ax = fig.axes[0]
#    pl.sca(ax)
    pc = ax.pcolormesh(xs1, ys1, data1, cmap=pl.get_cmap('RdBu'))
    pc = ax.pcolormesh(xs2, ys2, data2, cmap=pl.get_cmap('RdBu'))

    fig.colorbar(pc)

    ax.set_xlim(xs.min()), xs.max()
    ax.set_ylim(ys.min(), ys.max())
    ax.set_xlabel(r'$Re \{\alpha \}$')
    ax.set_ylabel(r'$Im \{\alpha \}$')
    fig.canvas.draw()
    
#pl.show()

