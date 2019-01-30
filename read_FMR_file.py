# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 19:09:23 2017

@author: WangLab
"""

import mclient
import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
new_data = np.loadtxt(r'C:\qrlab\FMR\text_parall1-400-1.txt')
print new_data.shape
# Note that this returned a 2D array!
# However, going back to 3D is easy if we know the 
# original shape of the array

size = new_data.shape[1]
new_data = new_data.reshape((4,1601,size))

X = new_data[0]
Y = new_data[1]
Z = new_data[2]
phase = new_data[3]

#if a 2D color graph is needed
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field')
pl.ylabel('Frequency (GHZ)')
pl.show()

#==============================================================================
# #if specific trace is needed
# 
# m = 289 #the magnetic field you want
# for i in range(size):
#     if X[0][i] < m:
#         i = i + 1
#     else:
#         break
# 
# Z = np.transpose(Z)
# Y = np.transpose(Y)
# phase = np.transpose(phase)
# z = Z[i]
# phase = phase[i]
# freq = Y[0]
# pl.plot(freq, z)
# pl.xlabel('frequency(GHZ)')
# pl.ylabel('dB')
# pl.show()
# z = z[:,None].T
# freq = freq[:,None].T
# trace = np.concatenate([freq, z, phase]).T
# np.savetxt(r'D:\%smT.txt' %(X[0][i]), trace , delimiter=",") 
# 
# 
#==============================================================================
#==============================================================================
# Z = np.transpose(Z)
# max2 = []
# 
# for i in range(size):
#     max2.append(np.argmax(Z[i]))
# 
# freq = []
# mag2 =[]
# for i in max2:
#     freq.append(i * 0.000125 + 8.4)
# mag2 = [j*0.02+280 for j in range(size)]
# pl.plot(mag2,freq)
#==============================================================================
