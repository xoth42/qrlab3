import matplotlib
matplotlib.interactive(True)

import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
new_data = np.loadtxt('C:\\Users\WangLab\Documents\FMR(2019)\\YIG_3_1.5mm_DCC_ZoomForModes_S12_0.5-0.55-5e-05_Date_3-24_16-1-35_XandY.txt')
new_data2 = np.loadtxt('C:\\Users\WangLab\Documents\FMR(2019)\\YIG_3_1.5mm_DCC_ZoomForModes_S12_0.5-0.55-5e-05_Date_3-24_16-1-35_ZandPhase.txt')
print(new_data.shape)
# Note that this returned a 2D array!
# However, going back to 3D is easy if we know the 
# original shape of the array

size = new_data.shape[1]
size2 = new_data2.shape[1]
new_data = new_data.reshape((2,new_data.shape[0]/2,size))
new_data2 = new_data2.reshape((2,new_data2.shape[0]/2,size2))

Ms = 178 * 1

X = new_data[0]
Y = new_data[1]
Z = new_data2[0]
phase = new_data2[1]

#X = X *50
pl.figure()
pl.pcolormesh(X, Y / float(10**9), Z)
pl.colorbar()
pl.title('1.5mm YIG (Sample 3) FMR Measurement of S12')
pl.xlabel('Magnetic Field (mT)')
pl.ylabel('Frequency (GHZ)')

x = X[0]
#pl.plot(x, 28.025*x/1000, color = 'b') #110
#pl.plot(x, 28.025*(x+Ms*(0.4-0.333333))/1000, color = 'r') #220
#pl.plot(x, 28.025*(x+Ms*(0.428571-0.333333))/1000, color = 'r') #330
#pl.plot(x, 28.025*(x+Ms*(0.444444-0.333333))/1000, color = 'r') #440
#pl.plot(x, 28.025*(x+Ms*(0.454545-0.333333))/1000, color = 'r') #550
#pl.plot(x, 28.025*(x+Ms*(0.285714-0.333333))/1000, color = 'r') #320
#pl.plot(x, 28.025*(x+Ms*(0.2-0.333333))/1000, color = 'r') #210
pl.plot(x, 28.025*x/1000, color = 'b') #110
pl.plot(x, 28.025*(x+Ms*(0.4-0.333333))/1000, color = 'r') #220
pl.plot(x, 28.025*(x+Ms*(0.428571-0.333333))/1000, color = 'r') #330
pl.plot(x, 28.025*(x+Ms*(0.444444-0.333333))/1000, color = 'r') #440
pl.plot(x, 28.025*(x+Ms*(0.454545-0.333333))/1000, color = 'r') #550
pl.plot(x, 28.025*(x+Ms*(0.285714-0.333333))/1000, color = 'r') #320
pl.plot(x, 28.025*(x+Ms*(0.2-0.333333))/1000, color = 'r') #210
pl.show()
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

