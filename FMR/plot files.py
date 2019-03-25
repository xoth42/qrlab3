# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 10:34:13 2018

@author: WangLab
"""



import matplotlib
matplotlib.interactive(True)

import lmfit
import re
import numpy as np
import matplotlib.pyplot as pl
import glob
foldername = 'S21 0.02T'
#filepath = 'C:\Users\WangLab\Documents\\FMR 11032018\\different modes\\%s'%(foldername) 
filepath = 'C:\Users\WangLab\Documents\\12042018 cooldown\\power sweep\\%s'%(foldername) 
filelist = glob.glob(r'%s\*.txt'%(filepath))
#pl.title('temperature dependence')
line=np.empty(len(filelist))
temp=np.empty(len(filelist))
#line1=np.empty(len(filelist))
#temp1=np.empty(len(filelist))
err=np.empty(len(filelist))
feq=np.empty(len(filelist))
ferr=np.empty(len(filelist))
ioff=np.empty(len(filelist))
roff=np.empty(len(filelist))
i=0
#print filelist
pl.figure()
for filename in filelist:
# Read the array from file
#    if filename[95]!=filename[96]:
            print '\n'
            print filename
            digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", filename)
        
            new_data = np.loadtxt(filename,delimiter=",")
            new_data = np.transpose(new_data)
#            print('\n')
#            print(filename)
            
            #new_data = np.loadtxt(filename,delimiter=",")
#            new_data = get_trace(m)
#            new_data = np.transpose(new_data)
            x = new_data[0] 
            y = new_data[1] 
            phase2 = new_data[2]
            pl.plot(x,y,label=filename[len(filepath):])
pl.legend()            
pl.show()