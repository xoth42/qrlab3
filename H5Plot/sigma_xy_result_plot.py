# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 20:18:24 2020

@author: Wang_Lab
"""


import numpy as np
import glob
import re
import matplotlib.pyplot as pl


foldername = 'sigma_xy'

filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\01052021cooldown_circulator\\%s'%(foldername) 

filelist = glob.glob(r'%s\\*T_results.txt'%(filepath))
filelist_base = glob.glob(r'%s\\*T_base_results.txt'%(filepath))


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
            
proj_base = np.zeros((len(fields),npts))    

for filename in filelist_base:
# Read the array from file
#    if filename[95]!=filename[96]:
    print '\n'
    print filename
    num = [float(s) for s in re.findall(r'-?\d+\.?\d*', filename)]
    proj = np.loadtxt(filename,delimiter=",")
    ifield = np.argmin(np.abs(fields - num[-1]))
    proj_base[ifield] = proj
    x = proj[::2]
    y = proj[1::2]
    pl.figure()
    pl.title('%sT'%(num[-1]))
    pl.plot(delays,x)
    pl.plot(delays,y)
    pl.plot(delays,np.sqrt(x**2 + y**2))


sigma_x = proj_data[:,::2]
sigma_y = proj_data[:,1::2]

sigma_x_b = proj_base[:,::2]
sigma_y_b = proj_base[:,1::2]

env = np.sqrt(sigma_x**2 + sigma_y**2)

env_base = np.sqrt(sigma_x_b**2 + sigma_y_b**2)

env = env/env_base

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
        

angle_data = np.arctan((sigma_y)/sigma_x)
for j in range(len(angle_data)):
    for i in range(len(angle_data[0])-1):
        if angle_data[j][i+1] < (angle_data[j][i]-.75*np.pi/2):
            angle_data[j][i+1:] = angle_data[j][i+1:] + np.pi
            
angle_base = np.arctan((sigma_y_b)/sigma_x_b)
for j in range(len(angle_base)):
    for i in range(len(angle_base[0])-1):
        if angle_base[j][i+1] < (angle_base[j][i]-.75*np.pi/2):
            angle_base[j][i+1:] = angle_base[j][i+1:] + np.pi
            
angle_data = angle_base - angle_data


pl.figure()
pl.title('accumulated phase')
X, Y = np.meshgrid(delays,fieldplot-0.005)
pl.pcolormesh(X,Y,angle_data)
pl.colorbar()


angle = angle_data[:, delay] - angle_data[:,0]
freq = angle/(2*np.pi*0.140)
pl.figure()
pl.plot(fields,freq, label = '%s ns'%(delays[delay]*1000))
pl.ylabel('qubit shift freq')
pl.xlabel('field(T)')
pl.legend()


pl.figure()
pl.title('stark shift vs. dephasing')
pl.plot(-np.log(sigma),freq, label = '%s ns'%(delays[delay]*1000))
pl.ylabel('qubit shift freq')
pl.xlabel('dephasing decay rate')
pl.legend()




