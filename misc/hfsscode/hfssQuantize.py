import numpy as np
import matplotlib.pyplot as pl

# Inputs from simulation
imfile = 'test1_imY.txt'
refile = 'test1_reY.txt'
Cj = 3e-15 # fF
Lj = 8e-9 # nH

e = 1.6e-19 # coulombs
h_bar = 6.63e-34 
Ec = e*e / (2 * Cj)

# Read in data
w = np.loadtxt(imfile, skiprows=7)[:,0]   # GHz
imY = np.loadtxt(imfile, skiprows=7)[:,1] # ???
reY = np.loadtxt(refile, skiprows=7)[:,1] # ???
N = len(w)

# find the roots to locate frequencies
imY_roots = np.array([], dtype = int)
for i in range(N-1):
	if(imY[i] * imY[i+1] < 0):
		imY_roots = np.append(imY_roots, [i])


# assuming evenly spaced frequencies
dw = w[1]-w[0]
# Take derivative with gradient function
dimY = np.gradient(imY) / dw
dreY = np.gradient(reY) / dw

# Calculate qubit properties
qubit = imY_roots[0]
Cq = .5 * dimY[qubit]
Lq = 1./(w[qubit]*w[qubit] * Cq)

# Calculate cavity properties
cavity = imY_roots[2]
Cc = .5 * dimY[cavity]
Lc = 1./(w[cavity]*w[cavity] * Cc)

# Calculate anharmonicities and frequency shifts
Xqq = -(Lq * Cj * Ec)/(Lj * Cq)
Xcc = -(Lc * Cj * Ec)/(Lj * Cc)
Xqc = -2 * np.sqrt(Xqq * Xcc)

# Converting from energy to frequency
Xqq /= h_bar * 1e6
Xcc /= h_bar * 1e6
Xqc /= h_bar * 1e6

print('w_q = ' + str(w[qubit]) + 'GHz, w_c = ' + str(w[cavity]) + 'GHz')
print('X_qq = ' + str(Xqq) + 'MHz, X_qc = ' + str(Xqc) + 'MHz')




'''
pl.plot(w, dimY)
pl.show()

pl.plot(w, imY)
pl.show()
'''