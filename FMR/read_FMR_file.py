

import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
<<<<<<< HEAD
new_data = np.loadtxt('text_0.5mm_270.0_300.0_0.05.txt')
=======
new_data = np.loadtxt(r'C:\qrlab\FMR\text_1.5mm_fridge_0.24_0.285_0.0002.txt')
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
print new_data.shape
# Note that this returned a 2D array!
# However, going back to 3D is easy if we know the 
# original shape of the array

size = new_data.shape[1]
new_data = new_data.reshape((4,new_data.shape[0]/4,size))

X = new_data[0]
Y = new_data[1]
Z = new_data[2]
phase = new_data[3]

<<<<<<< HEAD
Ms = 178 * 0.8
#X = X *302.8/294.8
=======
#==============================================================================
Ms = 178 * 0.8
X = X *302.8/273 *1000
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
pl.figure()
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field')
pl.ylabel('Frequency (GHZ)')
#==============================================================================
<<<<<<< HEAD
# x= X[0]
# pl.plot(x,np.zeros_like(x)+8.484)
# pl.plot(x,np.zeros_like(x)+8.532)
# pl.plot(x,np.zeros_like(x)+8.562)
# pl.plot(x,np.zeros_like(x)+8.592)
#==============================================================================
#pl.plot(x,np.zeros_like(x)+8.624)
pl.show()
pl.legend()
#==============================================================================
# x = X[0]
# slope = 28.2
# offset = 0
# pl.plot(x, offset+ slope*x/1000)
# pl.plot(x, offset+ slope*(x+Ms*(0.4-0.333333))/1000)
# pl.plot(x, offset+ slope*(x+Ms*(0.428571-0.333333))/1000)
# pl.plot(x, offset+ slope*(x+Ms*(0.444444-0.333333))/1000)
# pl.plot(x, offset+ slope*(x+Ms*(0.454545-0.333333))/1000)
# pl.plot(x, offset+ slope*(x+Ms*(0.2-0.333333))/1000)
#==============================================================================
#==============================================================================
# #if specific trace is needed
# 
# 
# m = 275.2 #the magnetic field you want
=======
#x= X[0]
#y= Y[:,0]
#pl.plot(np.zeros_like(y)+0.262,y)
#pl.plot(x,np.zeros_like(x)+8.2)
#pl.plot(x,np.zeros_like(x)+8.532)
#pl.plot(x,np.zeros_like(x)+8.562)
#pl.plot(x,np.zeros_like(x)+8.592)
#pl.plot(x,np.zeros_like(x)+8.624)
#pl.show()
#pl.legend()
x = X[0]
slope = 28.2
offset = 0
pl.plot(x, offset+ slope*x/1000)
pl.plot(x, offset+ slope*(x+Ms*(0.4-0.333333))/1000)
pl.plot(x, offset+ slope*(x+Ms*(0.428571-0.333333))/1000)
pl.plot(x, offset+ slope*(x+Ms*(0.444444-0.333333))/1000)
pl.plot(x, offset+ slope*(x+Ms*(0.454545-0.333333))/1000)
pl.plot(x, offset+ slope*(x+Ms*(0.2-0.333333))/1000)
#if specific trace is needed

#==============================================================================
# m = 0.262 #the magnetic field you want
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
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
# pl.figure()
# pl.plot(freq, z)
# pl.xlabel('frequency(GHZ)')
# pl.ylabel('dB')
<<<<<<< HEAD
# pl.show()
=======
# #pl.show()
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
# pl.legend()
# pl.figure()
# y= np.exp(z/20)
# pl.plot(freq,y)
# z = z[:,None].T
# freq = freq[:,None].T
# phase = phase[:,None].T
# trace = np.concatenate([freq, z, phase]).T
<<<<<<< HEAD
# np.savetxt(r'C:\Users\Wang_Lab\Documents\yingying\FMR\%smT.txt' %(X[0][i]), trace , delimiter=",") 
#==============================================================================

=======
# #np.savetxt(r'C:\Users\Wang_Lab\Documents\yingying\FMR\%smT.txt' %(X[0][i]), trace , delimiter=",") 
# 
#==============================================================================
>>>>>>> f59135e796c90615515b0f2c4bf0933eb63ea6b7
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

