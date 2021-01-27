# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 20:18:24 2020

@author: Wang_Lab
"""


import numpy as np
import glob
import re
import matplotlib.pyplot as pl


foldername = 'sigma_xy_redo'
#foldername = '0.25T in fridge\\330'
filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\1126cooldown_circulator\\%s'%(foldername) 
#filepath = 'C:\Users\Wang_Lab\Documents\\yingying\\FMR\\power sweep 220 mode' 
filelist = glob.glob(r'%s\\*.txt'%(filepath))
#pl.title('temperature dependence')

fields = np.linspace(-0.05, 0.05, 11)
fieldplot = np.linspace(-0.05,0.06,12)

npts = 242
delays = np.linspace(0,0.24,121)
proj_data = np.zeros((len(fields),npts))

#print filelist
for filename in filelist:
# Read the array from file
#    if filename[95]!=filename[96]:
    print '\n'
    print filename
    num = [float(s) for s in re.findall(r'-?\d+\.?\d*', filename)]
    proj = np.loadtxt(filename,delimiter=",")
    ifield = np.argmin(np.abs(fields - num[-1]))
    proj_data[ifield] = proj
    x = proj[::2]
    y = proj[1::2]
    pl.figure()
    pl.title('%sT'%(num[-1]))
    pl.plot(delays,x)
    pl.plot(delays,y)
    pl.plot(delays,np.sqrt(x**2 + y**2))
            



sigma_x = proj_data[:,::2]
sigma_y = proj_data[:,1::2]


env = np.sqrt(sigma_x**2 + sigma_y**2)

pl.figure()
X, Y = np.meshgrid(delays,fieldplot-0.005)
pl.pcolormesh(X,Y,env)
pl.colorbar()

delay = 70
sigma_raw = env[:, delay:delay + 10]

sigma = np.mean(sigma_raw, 1)
pl.figure()
#pl.plot(fields,sigma, label = '%s ns'%(delays[delay]*1000))
pl.plot(fields,-np.log(sigma), label = '%s ns'%(delays[delay]*1000))
pl.ylabel('qubit decay rate')
pl.xlabel('field(T)')
pl.legend()
        

