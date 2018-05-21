# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 17:54:07 2018

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as pl
import lmfit
import scipy as sy
import scipy.fftpack as syfp

freq0 = 50
noise = 0

w0 = 2*np.pi/1000*50
w = 2*np.pi/1000*freq0
N = np.array(range(801))
sindata = np.sin(N*w0)
cosdata = np.cos(N*w0)
taulist=[]
err=[]
errpercent=[]
start_fitting=20
#forlist=freq0+(np.random.rand(1)-0.5)*10
forlist=0.1*np.array(range(11)) + freq0
for freq0 in forlist:
    w = 2*np.pi/1000*freq0
    meas  = np.sin(N*w)*np.exp(-N/float(2*40))+(np.random.rand(801)-0.5)*2*noise
#    sp = np.fft.fft(meas)
#    freq = np.fft.fftfreq(meas.shape[-1])
#    pl.plot(freq, sp.real)#, freq, sp.imag)
#==============================================================================
#     sp = sy.fft(meas)
# #    print sp
#     freqs = syfp.fftfreq(len(meas))
# #    pl.figure()
# #    pl.plot(freqs, abs(sp), '.')
#     
# #    print freq0, 'MHz', 'calculated:', freqs[np.argmax(abs(sp))]
#==============================================================================
#==============================================================================
# #do n averages
#     if noise>=0.1:
#         n=100 
#         meas = meas/float(n) 
#         for i in range(n-1):
#             meas = meas + (np.sin(N*w)*np.exp(-N/float(2*40))+(np.random.rand(801)-0.5)*2*noise)/float(n)
#==============================================================================
    Idata = []
    Qdata = []
    for i in N:
        Idata.append(sindata[i] * meas[i])
        Qdata.append(cosdata[i] * meas[i])
    
    period = range(40)
    I = []
    Q = []
    A = []
    
    for j in period:
        Ivalue = 0
        Qvalue = 0
        for i in range(20):
            Ivalue += Idata[20*j+i]
            Qvalue += Qdata[20*j+i]
        I.append(Ivalue)
        Q.append(Qvalue)
        A.append(np.sqrt(Ivalue**2+Qvalue**2))
#    pl.figure()  
    #pl.plot(period, I)
    #pl.plot(period, Q)
    #pl.plot(period, A) 
    period = np.asarray(period) 
#    pl.plot(N,meas*10)
#    pl.plot(period*20, I, label = 'I')
#    pl.plot(period*20, Q, label = 'Q')
##    pl.plot(period*20, A,marker = 's', label = 'A   freq = %s Hz'%(freq0))
#    pl.plot(period*20, A,marker = 's', label = 'A   noise = %s'%(noise))
    
    def dem_decay(params, x, data):
        est = params['ofs'] + params['amplitude'] * np.exp(-(x) /( 2*params['tau'].value))# + params['A2']*np.sin(2*2*np.pi/1000*(freq0-50))
        return data - est
        
    params = lmfit.Parameters()
    params.add('ofs', value=np.min(A))
    params.add('amplitude', value=np.max(A))
    params.add('tau', value=40, min=5.0)
#    params.add('A2', value=1, max=np.max(A), min = -np.max(A))
    xs = period * 20
    ys = A
    result = lmfit.minimize(dem_decay, params, args=(xs[start_fitting/20:], ys[start_fitting/20:]))
    #        lmfit.report_fit(params)
    #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
    lmfit.report_fit(result.params)
#    pl.plot(xs[1:], ys[1:]-dem_decay(result.params, xs[1:], ys[1:]), label='Fit, tau = %.03f +/- %.03f ns'%(result.params['tau'].value,result.params['tau'].stderr))
#    pl.legend()
    taulist.append(result.params['tau'].value)
    err.append(result.params['tau'].stderr)
    errpercent.append(result.params['tau'].stderr/result.params['tau'].value)
#    pl.figure(freq0)
    pl.plot(I,Q)
    pl.xlabel('I')
    pl.ylabel('Q')
    pl.legend()
#    pl.scatter(noise,result.params['tau'].value)
pl.figure()   
#pl.errorbar(range(len(taulist)),taulist,yerr=err,fmt='o')
pl.errorbar(forlist,taulist,yerr=err,fmt='o')#, label= 'noise = %s'%(noise)) 
pl.legend() 
pl.figure()      
#pl.plot(range(len(errpercent)),errpercent)    
pl.scatter(forlist,errpercent)
pl.figure()
pl.scatter(taulist,errpercent)