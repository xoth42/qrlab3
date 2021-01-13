# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 15:04:41 2020

@author: Wang_Lab
"""

import numpy as np
import matplotlib.pyplot as plt

ref = 110
delays = np.linspace(0.1e3,0.3e3,101) 
phase1 = []
phase2 = []
for delay in delays:
    t = np.linspace(delay,998+delay,500 )
    s = np.sin(2* np.pi*50*t * 0.001)
    r = np.sin(2* np.pi * ref *t * 0.001)
    
    
    phis = np.linspace(0, 2*np.pi *len(t)/10 * ref/50,len(t),endpoint = False)
    _exp_iphi = np.exp(1j * phis) 
    _exp_iphi = _exp_iphi.astype(np.complex64)
    IQ = np.zeros([len(t)/10], dtype=np.complex64)
    
    def demodulate(ar):
        ar2 = ar.reshape((len(ar) / len(t), len(t)))
        ar3 = np.dot(ar2,_exp_iphi)
        ar4 = np.repeat(ar3, len(t)/10)
        IQ[:len(ar4)] = ar4 * np.exp(1j * np.angle(ar4)*(50.0/np.abs(ref)-1))
        return(IQ)
        
    r_d = demodulate(r)
    
    
    
    phis_s = np.linspace(0, 2*np.pi, 10, endpoint=False)
    _exp_iphi_s = np.exp(1j * phis_s) 
    _exp_iphi_s = _exp_iphi_s.astype(np.complex64)
    IQ_s = np.zeros([len(t)/10,], dtype=np.complex64)
    
    def demodulate_s(ar):
        ar2 = ar.reshape((len(ar) / 10, 10))
    #    print ar2
    #    print _exp_iphi_s
        ar3 = np.dot(ar2, _exp_iphi_s)
        IQ_s[:len(ar2)] = ar3
        return(IQ_s)
        
    s_d = demodulate_s(s)
    
    phase1.append(np.angle(s_d)[0])
    phase2.append(np.angle(r_d)[0])

plt.figure()
plt.plot(delays, phase1)
plt.plot(delays,phase2)
phase = np.array(phase1) - np.array(phase2)
phase = phase%(2 *np.pi)
plt.plot(delays,phase,marker ='s' )
#plt.legend()

