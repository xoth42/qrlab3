
import matplotlib.pyplot as plt
import numpy as np
import time
import lmfit
import re

from numpy import NaN, Inf, arange, isscalar, asarray, array



data1 = np.loadtxt(r'alazar_sweep_fridge_a_04042018_1.5mm_-10.0dB_0.262T_0.262T_8.54 GHz-8.545 GHz_51_5000ave.txt', delimiter=",")
data2 = data1.reshape((2,data1.shape[0]/2/96,96))
data_real = data2[0]
data_imag = data2[1]

# enter those values to creat graph label
sen = 40
mag =0
start_freq = 8.54e9
stop_freq = 8.545e9
num=51


Amp = []
I = []
Q = []
A = []
freq_range = np.linspace(start_freq, stop_freq, num)
i = 0            
    
for freq in freq_range:

    buf = data_real[i]+1j*data_imag[i]
    ave = np.average(np.abs(buf))
    Amp.append(ave)
    aveI = np.average(data_real[i])
    I.append(aveI)
    aveQ = np.average(data_imag[i])
    Q.append(aveQ)
    A.append(np.sqrt(aveI**2 + aveQ**2))
    i += 1
    
    
   
plt.figure()
plt.plot(freq_range, Amp,label=' magnetic field = %s mT \n Amp'%( mag))
plt.plot(freq_range, I, label = 'I')
plt.plot(freq_range, Q, label = 'Q')
plt.plot(freq_range, A, label = 'A from I and Q')




def peakdet(x,v, delta):
    maxtab = []        
    mintab = []        
#            if x is None:
#                x = arange(len(v))                
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
                mxpos = x[i]                
        if this < mn:                
            mn = this
            mnpos = x[i]                
        if lookformax:                
            if this < mx-delta:                
                maxtab.append((mxpos, mx))               
                mn = this
                mnpos = x[i]                
                lookformax = False                
        else:                
            if this > mn+delta:
                mintab.append((mnpos, mn))                
                mx = this                
                mxpos = x[i]                
                lookformax = True                
    return array(maxtab), array(mintab)
        
maxtab, mintab = peakdet(freq_range,A,sen)
if len(maxtab) == 0:
    print 'no peak!'
elif len(maxtab)!=1:               
    plt.scatter(array(maxtab)[:,0], array(maxtab)[:,1], color='blue')        
#            plt.scatter(array(mintab)[:,0], array(mintab)[:,1], color='red')
#            for freq in maxtab[:,0]:
#                i = 1
#                plt.scatter(freq, 0, lable = 'freq%s = %s GHz'%(i,freq/1e9))
#                i += 1

    plt.legend()
else:
    plt.scatter(array(maxtab)[0][0], array(maxtab)[0][1], color='blue', label='freq = %s GHz'%(maxtab[0][0]/1e9))        
#            plt.scatter(array(mintab)[0][0], array(mintab)[0][1], color='red')
    print maxtab[0][0]        
 
    plt.legend()

#np.savetxt(r'alazar_sweep_%s mT_%s GHz-%s GHz_%s.txt'%(mag,start_freq/float(1e9),stop_freq/float(1e9),num) , data , delimiter=",") # saves data