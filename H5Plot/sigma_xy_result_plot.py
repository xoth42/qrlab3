# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 20:18:24 2020

@author: Wang_Lab
"""


import numpy as np
import glob
import re
import matplotlib.pyplot as pl


foldername = 'sigma_xy_qubit2'

filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\06062021cooldown_circulator\\%s'%(foldername) 

filelist = glob.glob(r'%s\\*T_results.txt'%(filepath))
filelist_base = glob.glob(r'%s\\*T_base_results.txt'%(filepath))


#fields_fin = np.asarray([0,0.0001])#np.linspace(-.05,.05,21)
fields_fin = np.linspace(0,.05,2)
#fieldplot = np.asarray([-0.05, -0.04, -0.03, -0.02, -0.01,  0.  ,0.005,  0.01, 0.015, 0.02,  0.03, 0.04,  0.05,0.06])
#fieldplot = np.asarray([0,0.0001])
#fields = np.asarray([0,.005,.01,.015,.02,-.05,-.04,-.03,-.02,-.01,.03,0,.04,.05,.02,.025,.035,.045,0,
#                     -.005,-.01,-.015,-.02,-.025,-.03,-.035,-.04,-.045,-.05,-.005,-.015,-.015,-.025,
#                     -.035,-.045,0,.005,.01,.015,.02,.025,.03])
#fieldplot = fields
trials = 2
fields = np.zeros(trials)
npts = 242
delays = np.linspace(0,0.24,121)
proj_data = np.zeros((trials,npts))

#print filelist
for i,filename in enumerate(filelist):
# Read the array from file
#    if filename[95]!=filename[96]:
    print('\n')
    print(filename)
    num = [float(s) for s in re.findall(r'-?\d+\.?\d*', filename)]
    proj = np.loadtxt(filename,delimiter=",")
#    ifield = np.argmin(np.abs(fields - num[-1]))
    proj_data[i] = proj
    fields[i] = num[-1]
    x = proj[::2]
    y = proj[1::2]
    pl.figure()
    pl.title('%sT'%(num[-1]))
    pl.plot(delays,x)
    pl.plot(delays,y)
    pl.plot(delays,np.sqrt(x**2 + y**2))
    pl.close()
            
proj_base = np.zeros((trials,npts))    

for i,filename in enumerate(filelist_base):
# Read the array from file
#    if filename[95]!=filename[96]:
    print('\n')
    print(filename)
    num = [float(s) for s in re.findall(r'-?\d+\.?\d*', filename)]
    proj = np.loadtxt(filename,delimiter=",")
#    ifield = np.argmin(np.abs(fields - num[-1]))
    proj_base[i] = proj
    x = proj[::2]
    y = proj[1::2]
    pl.figure()
    pl.title('%sT'%(num[-1]))
    pl.plot(delays,x)
    pl.plot(delays,y)
    pl.plot(delays,np.sqrt(x**2 + y**2))
    pl.close()


sigma_x = proj_data[:,::2]
sigma_y = proj_data[:,1::2]

sigma_x_b = proj_base[:,::2]
sigma_y_b = proj_base[:,1::2]

env = np.sqrt(sigma_x**2 + sigma_y**2)

env_base = np.sqrt(sigma_x_b**2 + sigma_y_b**2)
#env_base[9] = 1
#
#env = env/env_base

pl.figure()
fieldplot = np.concatenate([fields_fin, np.asarray([fields_fin[-1] * 2 - fields_fin[-2]])])
X, Y = np.meshgrid(delays,fieldplot)
pl.pcolormesh(X,Y,env)
pl.colorbar()

delay = 100
sigma_raw = env[:, delay:delay + 10]

sigma = np.mean(sigma_raw, 1)
sigma_stdv = np.std(sigma_raw, 1)/3

        

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
angle = np.zeros((len(fields),10))
for i in range(len(fields)):
    angle[i] = angle_data[i, delay-5:delay+5] - angle_data[i,0]
angle_plot = np.mean(angle,1)
angle_stdv = np.std(angle,1)/(3*2*np.pi*delays[delay])
freq = angle_plot/(2*np.pi*delays[delay])

freq_fin = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
freq_err_fin = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
sigma_fin = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
sigma_err_fin = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
env_fin =[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
angle_data_fin = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

#freq_fin = [[],[]]
#freq_err_fin = [[],[]]
#sigma_fin = [[],[]]
#sigma_err_fin = [[],[]]
#env_fin =[[],[]]
#angle_data_fin = [[],[]]
for i in range(len(fields)):
    ifield = np.argmin(np.abs(fields[i] - fields_fin))
    freq_fin[ifield].append(freq[i])
    freq_err_fin[ifield].append(angle[i][:])
    sigma_fin[ifield].append(sigma[i])
    sigma_err_fin[ifield].append(sigma_raw[i][:])
    env_fin[ifield].append(env[i])
    angle_data_fin[ifield].append(angle_data[i]-angle_data[i][0])
    
    
freq_plot = np.zeros(len(fields_fin))
freq_err_plot = np.zeros(len(fields_fin))
sigma_plot = np.zeros(len(fields_fin))
sigma_err_plot = np.zeros(len(fields_fin))
env_plot =[]
angle_data_plot = []
for i in range(len(fields_fin)):
    freq_plot[i]=np.mean(freq_fin[i])
    sigma_plot[i]=np.mean(sigma_fin[i])
    freq_err_plot[i]=np.std(freq_err_fin[i])/np.sqrt(10*len(freq_err_fin[i]))
    sigma_err_plot[i]=np.std(sigma_err_fin[i])/np.sqrt(10*len(freq_err_fin[i]))
    env_plot.append(np.mean(env_fin[i],0))
    angle_data_plot.append(np.mean(angle_data_fin[i],0))

    
    
    
    
pl.figure()
#pl.plot(fields,sigma, label = '%s ns'%(delays[delay]*1000))
pl.errorbar(fields_fin,-np.log(sigma_plot)/(delays[delay]),sigma_err_plot/sigma_plot/(delays[delay]), fmt = 'o', label = '%s ns'%(delays[delay]*1000))
pl.ylabel('qubit decay rate')
pl.xlabel('field(T)')
pl.legend()

#pl.figure()
#pl.title('Accumulated Phase')
#pl.xlabel('Time(ns)')
#pl.ylabel('Field(T)')
#X, Y = np.meshgrid(delays*1e3,fields_fin-0.005)
#pl.pcolormesh(X,Y,angle_data_plot,vmin = 0)
#pl.colorbar()
#
#pl.figure()
#pl.title('Envelope Function')
#pl.ylabel('Field(T)')
#pl.xlabel('Time(ns)')
#X, Y = np.meshgrid(delays*1e3,fields_fin-0.005)
#pl.pcolormesh(X,Y,env_plot)
#pl.colorbar()




pl.figure()
pl.errorbar(fields_fin,freq_plot,freq_err_plot/(2*np.pi**delays[delay]),fmt ='o', label = '%s ns'%(delays[delay]*1000))
pl.ylabel('qubit shift freq')
pl.xlabel('field(T)')
pl.legend()


pl.figure()
pl.title('stark shift vs. dephasing')
pl.scatter(-np.log(sigma),freq, label = '%s ns'%(delays[delay]*1000))
pl.ylabel('qubit shift freq')
pl.xlabel('dephasing decay rate')
pl.legend()




