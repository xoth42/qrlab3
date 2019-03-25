

import sys
from numpy import NaN, Inf, arange, isscalar, asarray, array
import matplotlib.pyplot as pl
matplotlib.interactive(True)



def peakdet(v,freq,a, delta, x = None):
    maxtab = []
    mintab = []
    if x is None:
        x = arange(len(v))
        
        v = asarray(v)
        
        if len(v) != len(x):
        
            sys.exit('Input vectors v and x must have same length')
        
        if not isscalar(delta):
        
            sys.exit('Input argument delta must be a scalar')
        if delta <= 0:
        
            sys.exit('Input argument delta must be positive')
        
        mn, mx = Inf, -Inf
        
        mnpos, mxpos = NaN, NaN
        
        lookformax = True
        
        for i in arange(len(v)):
        
            this = v[i]
        
            if this > mx:
        
                    mx = this
        
                    mxpos = freq[i]
        
            if this < mn:
        
                mn = this
        
                mnpos = freq[i]
        
            if lookformax:
        
                if this < mx-delta:
        
                    maxtab.append((mxpos, a))
        
                    mn = this
        
                    mnpos = freq[i]
        
                    lookformax = False
        
            else:
        
                if this > mn+delta:
        
                    mintab.append((mnpos, a))
        
                    mx = this
        
                    mxpos = freq[i]
        
                    lookformax = True
        
    return array(maxtab), array(mintab)



#series = [0,0,0,2,0,0,0,-2,0,0,0,2,0,0,0,-2,0]
#new_data = np.loadtxt(r'0mT_0.75mm_trace\1.txt',delimiter=",")
#new_data = np.transpose(new_data)
#freq = new_data[0] 
#series = new_data[1] 
#phase = new_data[2]
#print(min(x), max(x))
#x = x.astype(float)
#print(min(x), max(x))
#x = x * 1000000000

new_data = np.loadtxt('text_1.5mm_240-320.txt')
size = new_data.shape[1]
num = new_data.shape[0] 
new_data = new_data.reshape((4,num/4,size))


X = new_data[0]
Y = new_data[1]
Z = new_data[2]
phase = new_data[3]
pl.pcolormesh(X, Y, Z)
pl.colorbar()
pl.xlabel('Magnetic Field')
pl.ylabel('Frequency (GHZ)')
pl.show()

Z = np.transpose(Z)
Y = np.transpose(Y)

for i in range (size):
    print i
    maxtab, mintab = peakdet(Z[i],Y[i],X[0][i],5)
    
    
    pl.scatter(array(maxtab)[:,1], array(maxtab)[:,0], color='blue')
#==============================================================================
#     if array(mintab):
#         
#         pl.scatter(array(mintab)[:,1], array(mintab)[:,0], color='red')
#     
#==============================================================================
