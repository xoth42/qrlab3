# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 17:36:46 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 20:18:24 2020

@author: Wang_Lab
"""


import numpy as np
import glob
import re
import matplotlib.pyplot as pl


foldername = 'CW_ramsey'


filepath = 'C:\\Users\\Wang_Lab\\Documents\\circulator results\\01052021cooldown_circulator\\%s'%(foldername) 


filelist = glob.glob(r'%s\\*.txt'%(filepath))


fields = np.linspace(-0.05, 0.05, 11)



slope = np.zeros(len(fields))

#print filelist
pl.figure()
for filename in filelist:
# Read the array from file
#    if filename[95]!=filename[96]:
    print '\n'
    print filename
    num = [float(s) for s in re.findall(r'-?\d+\.?\d*', filename)]

    ifield = np.argmin(np.abs(fields - num[-1]))
    data = np.loadtxt(filename,delimiter=",")
    
    
    freq = data[:len(data)/2]
    tau = data[len(data)/2:len(data)]
    freq = freq * 1000 #MHz
    tau = tau/1000 #us
#    pl.figure()
    pl.title('%sT'%(num[-1]))
    pl.scatter(freq,1/tau, label = 'field = %s T'%(num[-1] ))
    p = np.polyfit(freq, 1/tau, 1)
    pl.plot(np.linspace(np.min(freq), np.max(freq), len(freq)), p[0] * np.linspace(np.min(freq), np.max(freq), len(freq)) + p[1])
    pl.xlabel('df(MHz)')
    pl.ylabel('1/tau')
    pl.legend()
    
    slope[ifield] = p[0]
pl.figure()
pl.plot(fields, -slope)


            







#pl.figure()
##pl.plot(fields,sigma, label = '%s ns'%(delays[delay]*1000))
#pl.plot(fields,-np.log(sigma), label = '%s ns'%(delays[delay]*1000))
#pl.ylabel('qubit decay rate')
#pl.xlabel('field(T)')
#pl.legend()
        

