# -*- coding: utf-8 -*-
"""
Created on Wed Nov 06 12:56:58 2019

@author: Wang_Lab
"""


import numpy as np
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as pl
#from t1t2_plotting import smart_T1_delays
import os
import time
import math
import lmfit
import time
import datetime

filename2 = 'C:\\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191116\\213401_qubit2_StarkShift'
filename2_0 = 'C:\\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191116\\213401_qubit2_StarkShift_off'
#filename2 = 'C:\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191116\\090432_StarkShift'
#filename2_0 = 'C:\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191116\\090432_StarkShift_off'

#filename1 = 'C:\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191108\\154247_StarkShift'
#filename1_0 = 'C:\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191108\\154247_StarkShift_off'

#filename2 = 'C:\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191109\\054224_StarkShift'
#filename2_0 = 'C:\Users\Wang_Lab\Documents\yingying\\08272019cooldown\\20191109\\054224_StarkShift_off'

#new_data = np.loadtxt('%s.txt'%(filename1))
#new_data_0 = np.loadtxt('%s.txt'%(filename1_0))
#
#Z = new_data
#Z_0 =new_data_0 
##Z[4][5] = -9
##Z[5][3] = -8.3
##Z[5][5] = -12
#Z[1][1] = -0.027
#Z_0[3][11] = 0.016
#Z[4][5] = -0.049
#Z[5][2] = -0.02
#Z[6][2] = -0.042
#Z_0[11][2] = 0.039
#Z_0[12][0] = -0.006
#Z_0[14][1] = 0.044
#Z_0[14][2] = 0.047
#Z_0[14][6] = 0.043
#Z_0[14][8] = 0.043
#Z_0[14][11] = 0.041
#Z_0[14][12] = 0.044
#Z[14][17] = -0.978

new_data2 = np.loadtxt('%s.txt'%(filename2))
new_data2_0 = np.loadtxt('%s.txt'%(filename2_0))

Z2 = new_data2
Z2_0 = new_data2_0
#Z2[4][11] = -0.25
#Z2[6][17] = -1.841
#Z2[12][2] = -0.452
#Z2[13][6] = -0.218
#Z2[13][17] = -5
#Z2[14][4] = -0.4155
#Z2[14][17] = -6


#Z = Z[5: ]
#Z_0 = Z_0[5: ]

##Z = np.transpose(Z)
#Z2 = np.transpose(Z2)
##Z_0 = np.transpose(Z_0)
#Z2_0 = np.transpose(Z2_0)
#
#
##Z = Z - Z_0
Z2 = Z2 - Z2_0

Z2p = Z2[0::2]

Z2m=Z2[1::2]
#
##Z = Z[0:len(Z)-1]
#Z2 = Z2[0:len(Z2)-1]

#sub = Z/Z2

#sub = np.transpose(sub)


#fields = np.linspace(0.05,0.03,11)
fields = [-0.035,0.035,-0.04,0.04,-0.045,0.045,-0.05,0.05,-0.055,0.055]
#fields = [0.01,-0.01,0.015,-0.015,0.02,-0.02,0.025,-0.025,0.03,-0.03,0.04,-0.04]
fieldsm = fields[1::2]
fieldsp = fields[0::2]
#dfields = fields[3] - fields[1]
#fields = np.concatenate([fields, np.asarray([fields[-1] + fields[1] - fields[0]])])
#fields = fields - dfields
#freqs = np.linspace(10.65e9,10.83e9,19)
freqs = np.linspace(10.93e9,10.938e9,9)
#freqs = np.linspace(10.60e9,10.84e9,25)
X, Ym = np.meshgrid( freqs, fieldsm)
X, Yp = np.meshgrid( freqs, fieldsp)
#pl.figure()
#pl.pcolormesh(X,Y,sub,vmax = 0.5, vmin = 0)
#pl.colorbar()
#pl.show()

#X, Y = np.meshgrid(fields, freqs)
pl.figure()
pl.pcolormesh(X,Ym,Z2m,vmax = 0, vmin = -7)
pl.colorbar()
pl.show()
#X, Y = np.meshgrid(fields, freqs)
pl.figure()
pl.pcolormesh(X,Yp,Z2p,vmax = 0, vmin = -7)
pl.colorbar()
pl.show()

#X, Y = np.meshgrid(fields, freqs)
pl.figure()
pl.pcolormesh(X,Yp,Z2m[:,0:-1]/Z2p[:,0:-1],vmax = 0.5, vmin = 0)
pl.colorbar()
pl.show()
#X, Y = np.meshgrid(fields, freqs)
#pl.figure()
#pl.pcolormesh(X,Y,Z_0)
#pl.colorbar()
#pl.show()

pl.figure()
for i in range(len(fields)-2):
    pl.plot(freqs[0:-1], Z2[i][0:-1],label = 'field = %sT'%(fields[i]))
    pl.legend()
pl.ylim(-7,1)
#pl.figure()    
#fig , ( (ax1,ax2) , (ax3,ax4)) = pl.subplots(2, 2)
#
#plot1= ax1.pcolormesh(Xm,Y,Z2m)
#pl.colorbar(plot1,cax=ax1)
#plot2= ax2.pcolormesh(Xp,Y,Z2p,vmax = 0.1,vmin = -5)
#pl.colorbar(plot1,cax=ax2)
#plot3= ax3.pcolormesh(Xp,Y,Z2p[:][0:-1]/Z2m[:][0:-1])
#pl.colorbar(plot1,cax=ax3)
