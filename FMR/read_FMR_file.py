

import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
new_data = np.loadtxt('text_1.5mm_240-320.txt')
print new_data.shape
# Note that this returned a 2D array!
# However, going back to 3D is easy if we know the 
# original shape of the array

size = new_data.shape[1]
new_data = new_data.reshape((4,new_data.shape[0]/4,size))

Ms = 178 * 0.8

X = new_data[0]
Y = new_data[1]
Z = new_data[2]
phase = new_data[3]

X = X *302.8/296.1
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field')
pl.ylabel('Frequency (GHZ)')
pl.show()
x = X[0]
pl.plot(x, 28.025*x/1000, color = 'r')
pl.plot(x, 28.025*(x+Ms*(0.4-0.333333))/1000, color = 'r')
pl.plot(x, 28.025*(x+Ms*(0.428571-0.333333))/1000, color = 'r')
pl.plot(x, 28.025*(x+Ms*(0.444444-0.333333))/1000, color = 'r')
pl.plot(x, 28.025*(x+Ms*(0.454545-0.333333))/1000, color = 'r')
pl.plot(x, 28.025*(x+Ms*(0.285714-0.333333))/1000, color = 'r')
pl.plot(x, 28.025*(x+Ms*(0.2-0.333333))/1000, color = 'r')
#if specific trace is needed

#==============================================================================
# 
# m = 290 #the magnetic field you want
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
# phase = phase[:,None].T
# trace = np.concatenate([freq, z, phase]).T
# np.savetxt(r'C:\qrlab\FMR\traces_1.5mm_240-320\%smT.txt' %(X[0][i]), trace , delimiter=",") 
#==============================================================================

#==============================================================================
# freq = 8.4862 
# for i in range(900):
#     if Y[i][0] < freq:
#         i = i + 1
#     else:
#         break
# 
# 
# Y = np.transpose(Y)
# 
# z = Z[i]
# 
# mag = X[0]
# mag = mag * 302.8/296.5
# pl.plot(mag, z)
# pl.xlabel('mag')
# pl.ylabel('dB')
# pl.show()
# z = z[:,None].T
# mag = mag[:,None].T
#==============================================================================

