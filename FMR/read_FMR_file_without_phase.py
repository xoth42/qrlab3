import mclient
import numpy as np
import matplotlib.pyplot as pl

# Read the array from file
new_data = np.loadtxt('text_parall1-400-1.txt')
print new_data.shape
# Note that this returned a 2D array!
# However, going back to 3D is easy if we know the 
# original shape of the array

size = new_data.shape[1]
new_data = new_data.reshape((3,1601,size))

X = new_data[0]
Y = new_data[1]
Z = new_data[2]

#Z = np.power(10, Z/20)
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field')
pl.ylabel('Frequency (GHZ)')
pl.show()

#==============================================================================
# 
# #if specific trace is needed
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
# 
# z = Z[i]
# 
# freq = Y[0]
# pl.plot(freq, z)
# pl.xlabel('frequency(GHZ)')
# pl.ylabel('dB')
# pl.show()
# z = z[:,None].T
# freq = freq[:,None].T
# trace = np.concatenate([freq, z]).T
# np.savetxt(r'C:\qrlab\FMR\%smT.txt' %(X[0][i]), trace , delimiter=",") 
#==============================================================================





#==============================================================================
# max = []
# 
# for i in range(1601):
#     max.append(np.argmax(Z[i]))
# 
# mag = []
# for i in max:
#     mag.append(i * 0.02 + 280)
# 
# pl.plot(mag,x/(10**9))
#==============================================================================
#==============================================================================
# 
# Z = np.transpose(Z)
# max2 = []
# 
# for i in range(1251):
#     max2.append(np.argmax(Z[i]))
# 
# freq = []
# mag2 =[]
# for i in max2:
#     freq.append(i * 0.000125 + 8.4)
# mag2 = [j*0.02+280 for j in range(1251)]
# pl.plot(mag2,freq)
# 
#==============================================================================
