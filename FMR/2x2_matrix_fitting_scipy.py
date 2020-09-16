# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 15:29:26 2020

@author: Wang_Lab
"""

from scipy.optimize import minimize
import os
import time 



import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib import gridspec
from scipy import linalg
filepath = 'C:\\Users\\Wang_Lab\\Downloads\\'
#hdf5_name = 'VNAtestJan30.hdf5'
#hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
hdf5_name = '0626cooldown_circualtor_VNA - Copy.hdf5'

date = '20200628'
time = '214324'
experiment = 'Power_Sweep_VNA'

f = h5.File(filepath + hdf5_name, 'r')
exp = f['/' + date + '/' + time + '_' + experiment]
y_keys = exp.keys()

freq = exp['freqs'][()]
powers = exp['powers'][()]
real = exp['realS21'][()][0]
imag = exp['imaginaryS21'][()][0]
x = freq
magnitude = abs(real+1j*imag)
data_mag = magnitude
phase = np.angle(real-1j*imag)
data_phase = phase
data = real-1j*imag

def S31_resid(params,x,real,imag):
    wa,wb,ga,ga2,spl,wn,wp,gamma4,k_in,A,phi,i_off,r_off = params[0],params[1],params[2],params[3],params[4],params[5],params[6],params[7],params[8],params[9],params[10],params[11],params[12]
    delta = 0
    k = 0
    gamma1 = 0
    gamma2 = 0
    identity = np.array([[1,0],[0,1]])
    gamma = np.array([[np.sqrt(k_in),0],[0,np.sqrt(gamma4)]])
    out_3 = []
    Matrix_1 = np.array([[wa-1j*gamma1/2,ga2],[ga2,wn-1j*gamma4/2]])
    Matrix_2 = np.array([[0,ga],[ga2,spl + 1j*k*delta]])
#    Matrix_3 = np.array([[-wb+1j*gamma2/2+x[i],ga],[ga,x[i]-wp]])
    Matrix_4 = np.array([[0,ga2],[ga,spl-1j*k*delta]])
    # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    b_in = np.array([1,0]).T
    for i in range(len(x)):
        Matrix_3 = np.array([[-wb+1j*gamma2/2+x[i],ga],[ga,x[i]-wp]])
        a = linalg.inv(x[i]*identity-(Matrix_1 + (Matrix_2.dot(linalg.inv(Matrix_3))).dot(Matrix_4))).dot(gamma.dot(b_in))
        
        out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[1])+1j*i_off+r_off)
#    S31_mag = abs(np.array(out_3))
#    S31_phase = np.angle(np.array(out_3))
#    S31 = np.concatenate((S31_mag,S31_phase))
    S31 = np.asarray(out_3)
    return np.sum(np.sqrt((S31.real-real)**2+(S31.imag-imag)**2))

initial_guess = [10.8056,10.81103,.0304,.009,-.074,10.8,10.723,.2,.0001,.06,1,.001186,-.02]
result = minimize(S31_resid, initial_guess, args = (x,real,imag))

params = result.x

wa,wb,ga,ga2,spl,wn,wp,gamma4,k_in,A,phi,i_off,r_off = params[0],params[1],params[2],params[3],params[4],params[5],params[6],params[7],params[8],params[9],params[10],params[11],params[12]
delta = 0
k = 0
gamma1 = 0
gamma2 = 0
freqs = freq/1e9
w = freq/1e9
#identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
#gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
#out_3 = []
#H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
## a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
#b_in = np.array([1,0,0,0]).reshape(4,1)
#for i in range(len(w)):
#    
#    big_matrix = (w[i]*identity - H + 1j*gamma/2)
#    
#    a = -1j*la.inv(big_matrix)@np.sqrt(gamma)@b_in
#    
#    out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[3][0]))
identity = np.array([[1,0],[0,1]])
gamma = np.array([[np.sqrt(k_in),0],[0,np.sqrt(gamma4)]])
out_3 = []
Matrix_1 = np.array([[wa-1j*gamma1/2,ga2],[ga2,wn-1j*gamma4/2]])
Matrix_2 = np.array([[0,ga],[ga2,spl + 1j*k*delta]])
#    Matrix_3 = np.array([[-wb+1j*gamma2/2+x[i],ga],[ga,x[i]-wp]])
Matrix_4 = np.array([[0,ga2],[ga,spl-1j*k*delta]])
# a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
b_in = np.array([1,0]).T
for i in range(len(w)):
    Matrix_3 = np.array([[-wb+1j*gamma2/2+w[i],ga],[ga,w[i]-wp]])
    a = linalg.inv(w[i]*identity-(Matrix_1 + (Matrix_2.dot(linalg.inv(Matrix_3))).dot(Matrix_4))).dot(gamma.dot(b_in))
    
    out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[1])+1j*i_off+r_off)
S31_mag = abs(np.array(out_3))
S31_phase = np.angle(np.array(out_3))
S31 = np.concatenate((S31_mag,S31_phase))
S31_mag = abs(np.array(out_3))
S31_phase = np.angle(np.array(out_3))
plt.figure()
plt.title('Magnitude')
plt.plot(freqs,S31_mag,label = 'model')
plt.plot(freqs,data_mag, label = 'data')
plt.legend()

plt.figure()
plt.title('Phase')
plt.plot(freqs,S31_phase,label = 'model')
plt.plot(freqs,data_phase, label = 'data')
plt.legend()

plt.figure()
plt.title('IQ')
plt.plot(S31_mag*np.cos(S31_phase),S31_mag*np.sin(S31_phase),label = 'model')
plt.plot(real,-imag,label = 'data')
plt.legend()



















