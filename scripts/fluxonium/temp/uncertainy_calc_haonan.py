# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:21:15 2020

@author: wanglab
"""

if 1:
    qubit1 = [0.010203, 0.009, 0.009, 0.011]
    qubit2 = [0.007269, 0.007, 0.009, 0.007]
    
    std1 = np.std(qubit1, axis=0)
    std2 = np.std(qubit2, axis=0)
    
    err1 = std1/np.sqrt(len(qubit1))
    err2 = std2/np.sqrt(len(qubit2))

    print((np.mean(qubit1)*(6.0/7.0)))
    print(err1)
    print((np.mean(qubit2)*(6.0/7.0)))
    print(err2)



if 1: #XEB uncertainty
    tau_cycle = 21.0001459
    delta_tau_cycle = 0.64348434
    
    
    tau_qubit1 = 48.5016237
    delta_tau_qubit1 = 0.27790585
    
    tau_qubit2 = 68.2798186
    delta_tau_qubit2=0.65431256
    
    
    
    import numpy as np
    
    def p(tau):
        return np.exp(-1.0/tau)
    
    
#    pauli_r_qubit1 = (3.0/2.0)*(6.0/7.0) * 0.5*(1-p(tau_qubit1))
#    pauli_r_qubit2 = (3.0/2.0)*(6.0/7.0) * 0.5*(1-p(tau_qubit2))
    pauli_r_cycle = (15.0/16.0) * (1-p(tau_cycle))
    
    
    pauli_r_qubit1 = (3.0/2.0)*(6.0/7.0) * np.mean(qubit1)
    pauli_r_qubit2 = (3.0/2.0)*(6.0/7.0) * np.mean(qubit2)
    
    
    
    
    
    delta_p_cycle = (p(tau_cycle) * delta_tau_cycle)/(tau_cycle*tau_cycle)  #p uncertainty is same as (1-p)
    print(delta_p_cycle)
    
    
#    delta_p_qubit1 = 0.5*(p(tau_qubit1) * delta_tau_qubit1)/(tau_qubit1*tau_qubit1) #0.5(1-p)
#    print(delta_p_qubit1)
#    
#    
#    delta_p_qubit2 = 0.5*(p(tau_qubit2) * delta_tau_qubit2)/(tau_qubit2*tau_qubit2) #0.5(1-p)
#    print(delta_p_qubit2)
    
 
    delta_p_qubit1 = err1
    delta_p_qubit2 = err2
    
    Pauli_delta_p_cycle = (15.0/16.0) * delta_p_cycle
    
    Pauli_delta_p_qubit1 = (3.0/2.0)*(6.0/7.0)* delta_p_qubit1
    
    Pauli_delta_p_qubit2 = (3.0/2.0)*(6.0/7.0)* delta_p_qubit2
    
    Z = (1-pauli_r_cycle) / ((1-pauli_r_qubit1)*(1-pauli_r_qubit2)) #Z is 1- pauli_cz
    
    
    delta_Z =   (np.sqrt((Pauli_delta_p_cycle/(1-pauli_r_cycle))**2 + (Pauli_delta_p_qubit1/(1-pauli_r_qubit1))**2 + (Pauli_delta_p_qubit2/(1-pauli_r_qubit2))**2))
    final_delta_Z = Z * delta_Z
    uncertainty = final_delta_Z*(4.0/5.0)
    print(uncertainty)



if 0: #RB uncertainty
    tau_nonint = 9.52111171
    delta_nonint = 0.11832800
    
  
    tau_int = 7.27021348
    delta_int = 0.09403640
    
    
    
    def p(tau):
        return np.exp(-1.0/tau)
    
    
 
    
    
    
    delta_r_nonint = (3.0/4.0)*(p(tau_nonint) * delta_nonint/(tau_nonint*tau_nonint))  #p uncertainty is same as (1-p)
    print(delta_r_nonint)
    delta_r_int = (3.0/4.0)*(p(tau_int) * delta_int/(tau_int*tau_int))  #p uncertainty is same as (1-p)
    print(delta_r_int)
    
    
    
    
    delta_Z =   (np.sqrt(delta_r_int**2 + delta_r_nonint**2))
    print(delta_Z)


    interleaved=(3.0/4.0)*(1-p(tau_int))
    noninterleaved=(3.0/4.0)*(1-p(tau_nonint))
    
    Z =  ((3.0/4.0)*(1-p(tau_int))) - ((3.0/4.0)*(1-p(tau_nonint)))