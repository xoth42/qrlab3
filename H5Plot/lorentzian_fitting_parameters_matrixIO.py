# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 15:26:50 2020

@author: Wang_Lab
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 15:33:18 2020

@author: Jack
"""

import os
import time
import lmfit 

import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib import gridspec
import scipy.linalg as la
import matplotlib
matplotlib.interactive(True)


# def S31(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
#     A=gam1/2-1j*(w-w1)
#     B=gam2/2-1j*(w-w2)
#     C=gam3/2-1j*(w-w3)
#     D=-1j*(w-w4)
#     s31= gam3*gam1*abs((B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2)))**2
#     return s31
# def S31_phase(gam1,gam2,gam3,w1,w2,w3,w4,j1,j2,delta,w):
#     A=gam1/2-1j*(w-w1)
#     B=gam2/2-1j*(w-w2)
#     C=gam3/2-1j*(w-w3)
#     D=-1j*(w-w4)
#     s31_raw = 1j*(B*D*j1-B*delta*j2+2*j1*j2**2)/(B*D*j1**2+B*C*j2**2+4*j1**2*j2**2+A*(B*(C*D+delta**2)+D*j1**2+C*j2**2))
#     s31_phase = []
#     for i in range(len(w)):
#         s31_phase.append(cmath.phase(s31_raw[i]))
#     return s31_phase
input_port = 0 #signifying what port we are driving on
output_port = 3 #signifying what port the signal is coming out of
#delta = np.concatenate((np.linspace(-.05,0,26),np.linspace(0,.05,26)))

def Sij_resid(params,x,y):
    param = params.valuesdict()
    wa = param['wa']
    wb = param['wb']
    ga = param['ga']
    ga2 = param['ga2']
    gb = ga
    gb2 = ga2
    wp = param['wp']
    k = param['k']
    spl = param['spl']
    wp = param['wp']
    wn = param['wn']
    gamma1 = param['gamma1']
    gamma2 = param['gamma2']
    # gamma3 = param['gamma3']
    gamma4 = param['gamma4']
    A = param['A']
    # A = param['A']
    # phi = param['phi']
    gamma_list = [gamma1,gamma2,0,gamma4]
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,0,0],[0,0,0,gamma4]])
    out_3 = []
#    delta = np.linspace(0,-.05,26)
    delta = np.concatenate((np.linspace(-.05,0,26),np.linspace(0,.05,26)))
    lorentz_freqs = []
    kappa_tot = []
    kappa_prod = []

    eig_0 = []
    eig_1 = []
    eig_2 = []
    eig_3 = []
    
    for i in range(len(delta)): #getting model data for each field delta
        H = np.array([[wa,0,ga,ga2],
                      [0,wb,-gb,gb2],
                      [ga,-gb,wp,1j*delta[i]*k+spl],
                      [ga2,gb2,-1j*delta[i]*k+spl, wn]])  
        H = H - 1j*gamma/2
        left_evs = la.eig(H, left = True, right = False)[1]
        right_evs = la.eig(H, left = False, right = True)[1]
        eig_0.append(right_evs[:,0])
        eig_1.append(right_evs[:,1])
        eig_2.append(right_evs[:,2])
        eig_3.append(right_evs[:,3])
        right_evals = la.eigvals(H)#I'm pretty sure this is right eigenvalues but not 100% sure
    
        lorentz_freqs.append([np.real(right_evals[0]),np.real(right_evals[1]),np.real(right_evals[2]),np.real(right_evals[3])])# all of these are from spectral decomposition
        kappa_tot.append([-np.imag(right_evals[0])*2,-np.imag(right_evals[1])*2,-np.imag(right_evals[2])*2,-np.imag(right_evals[3])*2])
        kappa_prod.append((gamma_list[input_port]*gamma_list[output_port])*abs(np.asarray([right_evs[output_port][0]*np.conj(left_evs[input_port][0]),
                          right_evs[output_port][1]*np.conj(left_evs[input_port][1]),
                          right_evs[output_port][2]*np.conj(left_evs[input_port][2]),
                          right_evs[output_port][3]*np.conj(left_evs[input_port][3])]))**2)
    #getting mode participation values for each mode for wa (0) and wb (1):
    eig_0_0 = np.zeros(len(delta))
    eig_0_1 = np.zeros(len(delta))
    for i in range(len(delta)):
        eig_0_0[i] = abs(eig_0[i][0])**2
        eig_0_1[i] = abs(eig_0[i][1])**2

    eig_1_0 = np.zeros(len(delta))
    eig_1_1 = np.zeros(len(delta))
    for i in range(len(delta)):
        eig_1_0[i] = abs(eig_1[i][0])**2
        eig_1_1[i] = abs(eig_1[i][1])**2

    eig_2_0 = np.zeros(len(delta))
    eig_2_1 = np.zeros(len(delta))
    for i in range(len(delta)):
        eig_2_0[i] = abs(eig_2[i][0])**2
        eig_2_1[i] = abs(eig_2[i][1])**2

    eig_3_0 = np.zeros(len(delta))
    eig_3_1 = np.zeros(len(delta))
    for i in range(len(delta)):
        eig_3_0[i] = abs(eig_3[i][0])**2
        eig_3_1[i] = abs(eig_3[i][1])**2
    
    eig_cav1 = []
    eig_cav2 = []
    index_cav1 = []
    index_cav2 = []

#    if max([eig_0_0[-1],eig_1_0[-1],eig_2_0[-1],eig_3_0[-1]]) > max([eig_0_1[-1],eig_1_1[-1],eig_2_1[-1],eig_3_1[-1]]): #seeing which has higher max participation wa or wb
#        cav_1_max = True
#    else:
#        cav_1_max = False
#
#    for i in range(len(delta)):
#        eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
#        eig1_part = [eig_0_0[i],eig_1_0[i],eig_2_0[i],eig_3_0[i]]
#        eig2_part = [eig_0_1[i],eig_1_1[i],eig_2_1[i],eig_3_1[i]]
#        if cav_1_max:
#            eig1_ind_sort = np.argsort(eig1_part)
#            index1 = eig1_ind_sort[-1]
#            index2 = eig1_ind_sort[-2]
#        else:
#            eig2_ind_sort = np.argsort(eig2_part)
#            index1 = eig2_ind_sort[-2]
#            index2 = eig2_ind_sort[-1]

    for i in range(len(delta)):
        eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
        eigsum = [eig_0_0[i] +eig_0_1[i] ,eig_1_0[i] + eig_1_1[i],eig_2_0[i] + eig_2_1[i],eig_3_0[i]+eig_3_1[i]]
        eig_ind_sort = np.argsort(eigsum)
        index1 = eig_ind_sort[-1]
        index2 = eig_ind_sort[-2]
        index_cav1.append(int(index1))
        index_cav2.append(int(index2))
        eig_cav1.append(list(eigs[index1]))
        eig_cav2.append(list(eigs[index2]))
    top_index = []
    bottom_index = []
        
    for i in range(len(delta)):
        if lorentz_freqs[i][index_cav1[i]]>lorentz_freqs[i][index_cav2[i]]:
            top_index.append(index_cav1[i])
            bottom_index.append(index_cav2[i])
        else:
            top_index.append(index_cav2[i])
            bottom_index.append(index_cav1[i])
        eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
        eig_cav1.append(list(eigs[top_index[-1]]))
        eig_cav2.append(list(eigs[bottom_index[-1]]))
        
    eig_cav1_0 = np.zeros(len(delta))
    eig_cav1_1 = np.zeros(len(delta))
    for i in range(len(delta)):
        eig_cav1_0[i] = abs(eig_cav1[i][0])**2
        eig_cav1_1[i] = abs(eig_cav1[i][1])**2
        
    eig_cav2_0 = np.zeros(len(delta))
    eig_cav2_1 = np.zeros(len(delta))
    for i in range(len(delta)):
        eig_cav2_0[i] = abs(eig_cav2[i][0])**2
        eig_cav2_1[i] = abs(eig_cav2[i][1])**2
#    
#    eig_cav1_0 = np.zeros(len(delta))
#    eig_cav1_1 = np.zeros(len(delta))
#    for i in range(len(delta)):
#        eig_cav1_0[i] = abs(eig_cav1[i][0])**2
#        eig_cav1_1[i] = abs(eig_cav1[i][1])**2
#        
#    eig_cav2_0 = np.zeros(len(delta))
#    eig_cav2_1 = np.zeros(len(delta))
#    for i in range(len(delta)):
#        eig_cav2_0[i] = abs(eig_cav2[i][0])**2
#        eig_cav2_1[i] = abs(eig_cav2[i][1])**2
#    for i in range(len(delta)):
#        eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
#        freqs_sort = np.argsort(lorentz_freqs[i][2:4])
#        index1 = 2 + freqs_sort[-1]
#        index2 = 2 + freqs_sort[-2]
#        index_cav1.append(int(index1))
#        index_cav2.append(int(index2))
#        eig_cav1.append(list(eigs[index1]))
#        eig_cav2.append(list(eigs[index2]))

#    top_index = index_cav1
#    bottom_index = index_cav2
    lorentz_freqs_2 = []
    kappa_tot_2 = []
    kappa_prod_2 = []
    lorentz_freqs_1 = []
    kappa_tot_1 = []
    kappa_prod_1 = []
#    for i in range(len(top_index)):
#        lorentz_freqs_2.append([lorentz_freqs[i][top_index[i]],lorentz_freqs[i][bottom_index[i]]])
#        kappa_tot_2.append([kappa_tot[i][top_index[i]],kappa_tot[i][bottom_index[i]]])
#        kappa_prod_2.append([kappa_prod[i][top_index[i]],kappa_prod[i][bottom_index[i]]])
    for i in range(len(top_index)):
        lorentz_freqs_1.append(lorentz_freqs[i][top_index[i]])
        lorentz_freqs_2.append(lorentz_freqs[i][bottom_index[i]])
        kappa_tot_1.append(kappa_tot[i][top_index[i]])
        kappa_tot_2.append(kappa_tot[i][bottom_index[i]])
        kappa_prod_1.append(A*kappa_prod[i][top_index[i]])
        kappa_prod_2.append(A*kappa_prod[i][bottom_index[i]])
    
    kappa_tot_scale = 1
    kappa_prod_scale = 5e4
    model_vals = list(lorentz_freqs_1) + list(lorentz_freqs_2) + list(np.asarray(kappa_tot_1)*kappa_tot_scale) + list(np.asarray(kappa_tot_2)*kappa_tot_scale) + list(np.asarray(kappa_prod_1)*kappa_prod_scale) + list(np.asarray(kappa_prod_2)*kappa_prod_scale)
    model_vals = np.asarray(model_vals)
#    print len(model_vals)
    return ((model_vals-y))**2

#signifying we are reading out through the second port
#     for i in range(len(delta)):
#         H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta[i]*k+spl],[ga2,gb2,-1j*delta[i]*k+spl, wn]])  
#         H = H - 1j*gamma/2
#         left_evs = la.eig(H, left = True, right = False)[1]
#         right_evs = la.eig(H, left = False, right = True)[1]
#         right_evals = la.eigvals(H)#I'm pretty sure this is right eigenvalues but not 100% sure
#    
#         lorentz_freqs.append([np.real(right_evals[2]),np.real(right_evals[3])])
#         kappa_tot.append([-np.imag(right_evals[2])*2,-np.imag(right_evals[3])*2])
#         kappa_prod.append(abs(np.asarray([right_evs[output_port][0]*np.conj(left_evs[input_port][0]),
#                           right_evs[output_port][1]*np.conj(left_evs[input_port][1])])))

        
    # # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
    # b_in = np.array([1,0,0,0]).reshape(4,1)
    
    # for i in range(len(x)):
        
    #     big_matrix = (x[i]*identity - H + 1j*gamma/2)
        
    #     a = -1j*la.inv(big_matrix)@np.sqrt(gamma)@b_in
        
    #     out_3.append(A*np.exp(1j*phi)*(np.sqrt(gamma4)*a[3][0]))
    # S31_mag = abs(np.array(out_3))
    # S31_phase = np.angle(np.array(out_3))
    # S31 = np.concatenate((S31_mag,S31_phase))
    # return S31


#''' Path to the .hdf5 file '''
##filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
#filepath = 'C:\_Data\\'
##hdf5_name = 'VNAtestJan30.hdf5'
##hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
#hdf5_name = '0827cooldown_circualtor_VNA.hdf5'
#
#date = '20191125'
#time = '171742'
#experiment = 'Power_Sweep_VNA'
#
#f = h5.File(filepath + hdf5_name, 'r')
#exp = f['/' + date + '/' + time + '_' + experiment]
#y_keys = exp.keys()
##print(y_keys)
#
##y_keys.remove(x_key)
##y_keys.remove(x2_key)
#freq = exp['freqs'][()]
##current = exp['currents'].value
#powers = exp['powers'][()]
#real = exp['realS31'][()]
#imag = exp['imaginaryS31'][()]
#
#magnitude = abs(real+1j*imag)**2
#data_mag = magnitude[0]
#phase = np.angle(real+1j*imag)
#data_phase = phase[0]
#data = np.concatenate((data_mag,data_phase))
    
#kappa_tot_scale = 1
#kappa_prod_scale = 1e2
kappa_tot_scale = 1
kappa_prod_scale = 1e2


data_txt = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210109_232841\\results.txt')
data_txt = np.transpose(data_txt)
data_txt_neg = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210110_083300\\results.txt')
data_txt_neg = np.transpose(data_txt_neg)

#if only fitting one set either positive or negative, use the following:
#freq1 = data_txt[1]
#freq1_err = data_txt[2]
#freq2 = data_txt[3]
#freq2_err = data_txt[4]
#kappa_tot1 = data_txt[5]
#kappa_tot1_err = data_txt[6]
#kappa_tot2 = data_txt[7]
#kappa_tot2_err = data_txt[8]
#kappa_prod1 = data_txt[9]
#kappa_prod1_err = data_txt[10]
#kappa_prod2 = data_txt[11]
#kappa_prod2_err = data_txt[12]
#phi21 = data_txt[13]
#phi21_err = data_txt[14]

freq1 = np.concatenate((data_txt_neg[1][::-1],data_txt[1]))
freq1_err = np.concatenate((data_txt_neg[2][::-1],data_txt[2]))
freq2 = np.concatenate((data_txt_neg[3][::-1],data_txt[3]))
freq2_err = np.concatenate((data_txt_neg[4][::-1],data_txt[4]))
kappa_tot1 = np.concatenate((data_txt_neg[5][::-1],data_txt[5]))
kappa_tot1_err = np.concatenate((data_txt_neg[6][::-1],data_txt[6]))
kappa_tot2 = np.concatenate((data_txt_neg[7][::-1],data_txt[7]))
kappa_tot2_err = np.concatenate((data_txt_neg[8][::-1],data_txt[8]))
kappa_prod1 = np.concatenate((data_txt_neg[9][::-1],data_txt[9]))
kappa_prod1_err = np.concatenate((data_txt_neg[10][::-1],data_txt[10]))
kappa_prod2 = np.concatenate((data_txt_neg[11][::-1],data_txt[11]))
kappa_prod2_err = np.concatenate((data_txt_neg[12][::-1],data_txt[12]))
phi21 = np.concatenate((data_txt_neg[13][::-1],data_txt[13]))
phi21_err = np.concatenate((data_txt_neg[14][::-1],data_txt[14]))

##freq1 is lower one
#freq1 = [  1.08213400e+10,   1.08213228e+10,   1.08213204e+10,
#         1.08213424e+10,   1.08213244e+10,   1.08213152e+10,
#         1.08212977e+10,   1.08213203e+10,   1.08212744e+10,
#         1.08211902e+10,   1.08212461e+10,   1.08210254e+10,
#         1.08210127e+10,   1.08208809e+10,   1.08208553e+10,
#         1.08207967e+10,   1.08206884e+10,   1.08204502e+10,
#         1.08204213e+10,   1.08202687e+10,   1.08204546e+10,
#         1.08204937e+10,   1.08204563e+10,   1.08203063e+10,
#         1.08203653e+10,   1.08203222e+10]
##freq2 is higher one
#freq2 = [  1.08326871e+10,   1.08321902e+10,   1.08313858e+10,
#         1.08303315e+10,   1.08288701e+10,   1.08260851e+10,
#         1.08247387e+10,   1.08239434e+10,   1.08233400e+10,
#         1.08228303e+10,   1.08226110e+10,   1.08224053e+10,
#         1.08225867e+10,   1.08224791e+10,   1.08226279e+10,
#         1.08227419e+10,   1.08227158e+10,   1.08227258e+10,
#         1.08227045e+10,   1.08227345e+10,   1.08227574e+10,
#         1.08227112e+10,   1.08227002e+10,   1.08226144e+10,
#         1.08226991e+10,   1.08226349e+10]
#kappa_tot1 = [ 1458931.38068345,  1417151.91290721,  1464146.38897895,
#        1448174.2420111 ,  1446124.01114107,  1620210.82017222,
#        1497158.24266218,  1523689.00325872,  1706809.1368574 ,
#        1863583.03074044,  1946934.52878779,  2224523.44618431,
#        2320922.26645961,  2630823.8888596 ,  2340434.02824848,
#        2223926.47905887,  2191302.1084671 ,  2158214.72805673,
#        2119393.59393927,  2511465.57639075,  2100461.02129551,
#        2021938.24432331,  2209451.63261707,  2141203.52925324,
#        2102950.08040082,  2066309.65337634]
#kappa_tot2 = [ 16237118.48820736,  15734264.45376964,  15400778.00482422,
#        15347589.57640317,  18759044.10897866,  18263446.88906244,
#        15043756.60812051,  12813059.1773751 ,   9667094.19208429,
#         7866676.50242091,   7080877.21469553,   5114332.93260616,
#         4463596.3683429 ,   3488848.73808856,   2895776.47389079,
#         2456390.94420235,   2282227.52905419,   1952417.30891136,
#         1741168.60800747,   1604475.06712124,   1487399.23923451,
#         1451286.992947  ,   1368393.61873668,   1426057.46131627,
#         1278082.54466204,   1195854.31291325]
#kappa_prod1 = [  2.48321707e+10,   2.62417604e+10,   2.92108002e+10,
#         3.17963619e+10,   3.32663848e+10,   3.79283952e+10,
#         4.10102246e+10,   4.56671567e+10,   6.37354572e+10,
#         9.59548768e+10,   1.23216245e+11,   2.20297557e+11,
#         2.32653745e+11,   2.99205249e+11,   1.82098717e+11,
#         1.33211174e+11,   1.12293075e+11,   8.69888848e+10,
#         7.18456271e+10,   6.59083712e+10,   5.41404828e+10,
#         4.79786199e+10,   4.42688330e+10,   3.82960901e+10,
#         3.46137119e+10,   2.98947580e+10]
#
#kappa_prod2 = [  5.34920439e+11,   5.42563082e+11,   5.73047225e+11,
#         6.21117575e+11,   9.04211248e+11,   9.50160971e+11,
#         8.27663147e+11,   7.34900720e+11,   6.34321515e+11,
#         6.13303693e+11,   6.36509486e+11,   5.83574651e+11,
#         4.60094090e+11,   3.28861482e+11,   1.63794056e+11,
#         8.78054777e+10,   6.12218358e+10,   3.04147799e+10,
#         2.01992534e+10,   1.23057792e+10,   1.07424269e+10,
#         9.00124437e+09,   6.79697834e+09,   4.99147785e+09,
#         3.76718646e+09,   2.66728763e+09]

'''
freq1 = [  1.08232256e+10,   1.08227676e+10,   1.08233233e+10,
         1.08233315e+10,   1.08233112e+10,   1.08220266e+10,
         1.08231729e+10,   1.08230432e+10,   1.08224833e+10,
         1.08224182e+10,   1.08222626e+10,   1.08221935e+10,
         1.08220308e+10,   1.08217635e+10,   1.08220850e+10,
         1.08219437e+10,   1.08218316e+10,   1.08221809e+10,
         1.08221906e+10,   1.08221422e+10,   1.08222179e+10,
         1.08219686e+10,   1.08222320e+10,   1.08220852e+10,
         1.08220874e+10,   1.08219967e+10]
freq1_err = [  11237.54382184,   14151.9042245 ,   16706.71552768,
         17948.48400733,   17526.5940949 ,   31620.6779091 ,
         37249.36384478,   38706.35815301,   63341.0282222 ,
         80064.88943496,   90678.60340137,   80072.6684175 ,
         83569.4727529 ,  152017.8087648 ,   58976.95418172,
        624119.43875059,   53418.16366888,   45734.16327371,
         32944.20634046,   32622.60109376,   32045.47839094,
         25422.7409344 ,   15805.21589599,   23718.54329675,
         15402.50717949,   17815.70837896]
freq2 = [  1.08380672e+10,   1.08382929e+10,   1.08361969e+10,
         1.08320508e+10,   1.08306844e+10,   1.08265004e+10,
         1.08258501e+10,   1.08255625e+10,   1.08255150e+10,
         1.08255865e+10,   1.08259101e+10,   1.08258701e+10,
         1.08261041e+10,   1.08253371e+10,   1.08251042e+10,
         1.08260501e+10,   1.08256674e+10,   1.08257538e+10,
         1.08258563e+10,   1.08257188e+10,   1.08262001e+10,
         1.08253042e+10,   1.08253876e+10,   1.08257761e+10,
         1.08255137e+10,   1.08244698e+10]
freq2_err = [  730221.09353929,   816111.90831597,   820821.90027871,
         914660.66834952,  1151368.77418078,  2502347.62772622,
         478817.38657245,   370800.81812261,   381002.03057519,
         271718.5902637 ,   240451.36482305,   242642.12683233,
         226305.30335364,   270496.63686678,   171684.40111595,
          93526.71730333,   104552.03102754,    78859.51123994,
          58834.99728954,    53843.27818528,   419777.77282283,
          75065.44487235,    45468.95477279,    36826.71993591,
          47664.81740531,    86368.19508046]
kappa_tot1 = [ 3249741.45275982,  3522508.81127384,  3759914.30509465,
        3634052.7438327 ,  3485611.6807688 ,  4416342.05290904,
        4121604.69881414,  3963577.17808161,  4223711.50221644,
        4266894.52376202,  4126779.68947812,  3554610.04021169,
        3317999.66642101,  3889640.64066234,  2465316.99126623,
        2562199.65084075,  2324271.04394132,  2005771.16533975,
        1748640.91822473,  1850403.98729472,  1578572.29255239,
        1624460.59116327,  1354554.0454342 ,  1647926.18942948,
        1314832.3586408 ,  1274807.99237019]
kappa_tot1_err = [   23949.11295087,    25336.4710633 ,    32578.40110963,
          36808.59127713,    33906.18564251,    65788.98115923,
          75107.98120623,    77028.90179353,   123224.6561282 ,
         149220.85655335,   174585.73865456,   172751.98444718,
         177117.92484543,   302419.15260965,   126303.41340531,
        1119757.32906624,   113337.9203554 ,    64152.75496754,
          51123.12868095,    53172.48324234,    57157.53465093,
          44162.85215113,    37802.14841753,    53342.02280128,
          38676.98527697,    43052.98042709]
kappa_tot2 = [ 34550439.61629315,  35079327.97912265,  34600795.3589175 ,
        31982668.96394195,  37578135.81312631,  51810976.36149279,
        18801125.37335953,  15232310.47257293,  12976032.95367382,
         9950239.21920146,   8162669.65126421,   7392155.12771485,
         6429431.20484296,   5550339.35976333,   4512446.15379918,
         8405896.89580457,   3538295.36886741,   3001165.42987704,
         2706072.87706521,   2830075.56166766,   7862125.20237018,
         3158543.88801041,   2368637.20004536,   2108639.03602951,
         2236362.93963065,   3447244.27116374]
kappa_tot2_err = [ 1326074.80661689,  1376186.28512879,  1356139.75672952,
        1428832.40813556,  1852751.89777158,  4705865.87204735,
        1029163.38080961,   796522.84273826,   912422.75115273,
         671337.45450494,   593809.87667194,   572360.5800777 ,
         486965.49573122,   464502.35373149,   315492.80881306,
         195593.45718968,   206354.81377785,   126290.28995579,
         115530.61314885,   122053.62748734,   648405.77465381,
         116673.25317765,    75630.94942367,    67615.3658634 ,
          74278.39007971,   176577.47803711]
kappa_prod1 = [  4.31339426e+08,   3.87314143e+08,   3.94809676e+08,
         3.65647147e+08,   3.24096732e+08,   1.71350988e+08,
         3.18402315e+08,   2.78668920e+08,   1.86119421e+08,
         1.53479273e+08,   8.16916213e+07,   3.80484063e+07,
         2.02783786e+07,   1.64428014e+07,   1.51008442e+07,
         5.38337705e+06,   1.06139768e+07,   1.32645375e+07,
         1.29628998e+07,   1.39273387e+07,   8.43714543e+06,
         1.58131008e+07,   1.62918010e+07,   1.25604252e+07,
         1.30129452e+07,   1.49155883e+07]
kappa_prod1_err = [  5180065.33979943,   5054190.63682262,   6320283.72047254,
         7447253.83325707,   6761713.50624789,   5318320.42001591,
        17800942.04195022,  18494499.36590403,  19612138.25223901,
        20931292.90258212,  13282745.60640017,   6016891.82005019,
         2947685.12924815,   3865435.88128814,   1924625.61107578,
         2272831.77112051,    975184.26273562,    897688.90152885,
          816575.42518771,    863644.06216682,    678708.39465015,
          901588.2804836 ,    809346.1958209 ,    755594.40034073,
          611486.86792336,   1000459.48461733]
kappa_prod2 = [  1.15095621e+09,   1.02199811e+09,   1.04719058e+09,
         6.91443256e+08,   8.78297782e+08,   8.55503018e+08,
         3.76745842e+08,   3.01734251e+08,   1.98109940e+08,
         1.69687908e+08,   9.09920268e+07,   4.24711870e+07,
         2.23417637e+07,   1.89516388e+07,   1.47874849e+07,
         7.23894789e+06,   1.16601616e+07,   1.31228770e+07,
         1.22323873e+07,   1.42152298e+07,   1.01114765e+07,
         1.60345803e+07,   1.65807503e+07,   1.32643538e+07,
         1.40897660e+07,   1.35892183e+07]
kappa_prod2_err = [  1.09849184e+08,   9.85019655e+07,   9.90264776e+07,
         6.73150866e+07,   1.00331401e+08,   1.97020490e+08,
         2.69653225e+07,   2.45979575e+07,   2.54085533e+07,
         2.80308900e+07,   1.79623775e+07,   8.59812721e+06,
         4.37824280e+06,   5.06199424e+06,   2.44922732e+06,
         1.02416444e+06,   1.28331758e+06,   1.07972178e+06,
         1.01065546e+06,   1.16564673e+06,   1.62303136e+06,
         1.27878394e+06,   1.04579626e+06,   8.24397124e+05,
         9.44628872e+05,   1.37933265e+06]
'''

kappa_prod1 = list(np.sqrt(np.asarray(kappa_prod1)))
kappa_prod2 = list(np.sqrt(np.asarray(kappa_prod2)))
datas = list(np.asarray(freq2)/1e9) + list(np.asarray(freq1)/1e9) + list(np.asarray(kappa_tot2)*kappa_tot_scale/1e9) + list(np.asarray(kappa_tot1)*kappa_tot_scale/1e9) + list(np.asarray(kappa_prod2)*kappa_prod_scale/1e9) + list(np.asarray(kappa_prod1)*kappa_prod_scale/1e9)
datas = np.asarray(datas)

#freq1_err = [  4998.73712533,   5003.59254441,   5848.71213094,   6606.97926355,
#         7917.07812048,   9997.18161147,   9231.98402504,   7585.26591575,
#         7429.08875079,   7870.85295771,   9494.66445403,  10947.18828694,
#         8259.13847302,  10393.99791036,   6766.66040542,   4669.59872636,
#         3978.33391318,   2880.1067499 ,   2550.22379177,   3165.41821725,
#         2650.79741579,   2302.03129959,   2609.76794747,   2492.44653935,
#         2327.30401116,   2144.78825258]
#freq2_err = [ 45483.13894759,  44170.28554926,  44549.65534069,  47540.8578504 ,
#        69028.12084147,  78100.93475856,  61036.43589408,  48820.74602213,
#        36687.61036882,  27560.03303935,  25589.71431166,  20749.81359015,
#        17173.55062122,  11534.65619891,   8149.76499886,   5773.37476321,
#         4917.18742001,   3933.53107744,   3848.25231132,   3373.46225917,
#         3181.45141737,   3234.32115659,   3025.46710698,   3707.4315302 ,
#         2997.82497697,   3133.61795765]
#kappa_tot1_err = [  7922.01724714,   8805.88281656,  11377.45180035,  12103.84482837,
#        16773.05634773,  21599.79561162,  15032.99712957,  13633.49824897,
#        15949.4181694 ,  16225.18263822,  17632.01523347,  18810.95439787,
#        14227.98972304,  18773.13948659,  11987.78131905,   9753.19341142,
#         6850.90047523,   5588.56301375,   5010.67484025,   6868.46335003,
#         4861.35655532,   4621.08344204,   5203.71627422,   5130.87451876,
#         4612.33286548,   4379.78263808]
#kappa_tot2_err = [  95055.41020872,   93238.85541471,   96907.32306823,
#        103523.69048072,  153320.90157706,  162435.07792694,
#        133777.04413757,  114869.1296031 ,  102125.78132929,
#         81766.75252994,   68893.83438595,   45864.30654634,
#         32905.12524626,   36063.19229485,   21026.61402366,
#         14897.82967342,   11964.95922889,    8457.59214701,
#          6637.63040096,    7303.81978968,    6248.03846923,
#          6200.65718202,    6221.7858858 ,    6872.19600694,
#          6417.11179827,    6178.1679531 ]
#kappa_prod1_err = [  2.09636605e+08,   2.15690212e+08,   2.43993813e+08,
#         2.86924241e+08,   3.67944077e+08,   6.19405312e+08,
#         6.92089230e+08,   8.59694602e+08,   1.68006141e+09,
#         2.68224043e+09,   3.74089760e+09,   7.23912190e+09,
#         6.03149936e+09,   6.71609759e+09,   2.66054148e+09,
#         1.27114963e+09,   8.32157880e+08,   4.80288675e+08,
#         3.77888294e+08,   3.51139492e+08,   2.72080967e+08,
#         2.22033310e+08,   2.10358241e+08,   1.75481826e+08,
#         1.53677812e+08,   1.25523655e+08]
#
#kappa_prod2_err = [  6.94558205e+09,   7.01789539e+09,   7.85651466e+09,
#         8.98562348e+09,   1.55152495e+10,   1.46028242e+10,
#         1.09661735e+10,   8.42215051e+09,   6.98229766e+09,
#         7.14680299e+09,   8.57409723e+09,   1.34361345e+10,
#         1.07479130e+10,   9.41718113e+09,   3.18854236e+09,
#         1.25540040e+09,   7.84443446e+08,   2.97089352e+08,
#         1.85915093e+08,   1.21400154e+08,   9.90787000e+07,
#         8.35856518e+07,   6.63307574e+07,   5.01540981e+07,
#         3.63953160e+07,   2.77070723e+07]

kappa_prod1_err = list(np.sqrt(np.asarray(kappa_prod1_err)))
kappa_prod2_err = list(np.sqrt(np.asarray(kappa_prod2_err)))
datas_errs = list(np.asarray(freq2_err)/1e9) + list(np.asarray(freq1_err)/1e9) + list(np.asarray(kappa_tot2_err)*kappa_tot_scale/1e9) + list(np.asarray(kappa_tot1_err)*kappa_tot_scale/1e9) + list(np.asarray(kappa_prod2_err)*kappa_prod_scale/1e9) + list(np.asarray(kappa_prod1_err)*kappa_prod_scale/1e9)

fields = np.concatenate((np.linspace(-.05,0,26),np.linspace(0,.05,26)))

fix_vary = False
params = lmfit.Parameters()

#params.add('gamma1',value = .0001, min = 0, max = .001, vary = False)
#params.add('gamma2',value = .0005, min = 0, max = .005, vary = False)
## params.add('gamma3',value = 0.002, vary = fix_vary)
#params.add('gamma4',value = .28, min = 0, vary = False)
#params.add('wb',value = 10.804, vary = False)
#params.add('wa',value = 10.8104, vary = False)
#params.add('wp',value = 10.78, vary = False, max = 10.8)
#params.add('wn',value = 10.75, vary = False)
#params.add('ga',value = .025, vary = False)
#params.add('ga2',value = .008, vary = False)
#params.add('spl',value = -.09, vary = False)
#params.add('A',value = .157, vary = False)

params.add('gamma1',value = .00001, vary = False)
params.add('gamma2',value = .00001, vary = False)
# params.add('gamma3',value = 0, vary = fix_vary)
params.add('gamma4',value = .00972*2, vary = fix_vary)
params.add('wb',value = 10.8110259, vary = False)
params.add('wa',value = 10.8055980, vary = False)
params.add('wp',value = 10.7226776, vary = fix_vary)
params.add('wn',value = 10.8003602, vary = fix_vary)
params.add('ga',value = .03038315, vary = fix_vary)
params.add('ga2',value = .00890035, vary = fix_vary)
params.add('spl',value = -.07407939, vary = fix_vary)
params.add('A',value = 3, vary = True)

# params.add('A',value = .01, min = .001, max = .1, vary = fix_vary )
# params.add('delta',value = 0, vary = False, vary = fix_vary)
params.add('k',value = 8, vary = False)
# params.add('phi',value = 0, vary = fix_vary)
#freqs = freq/1e9
print('data seze %s'%(len(datas)))
result = lmfit.minimize(Sij_resid, params, args=(fields, datas))
lmfit.report_fit(result.params)

gamma1 = result.params['gamma1'].value
gamma2 = result.params['gamma2'].value
# gamma3 = result.params['gamma3'].value
gamma4 = result.params['gamma4'].value
wa = result.params['wa'].value
wb = result.params['wb'].value
wp = result.params['wp'].value
wn = result.params['wn'].value
ga = result.params['ga'].value
ga2 = result.params['ga2'].value
gb = 1*ga
gb2 = 1*ga2
spl = result.params['spl'].value
# delta = result.params['delta'].value
A=result.params['A'].value
k = result.params['k'].value
# phi = result.params['phi']
#w = freqs
identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,0,0],[0,0,0,gamma4]])
gamma_list = [gamma1,gamma2,0,gamma4]
out_3 = []
delta = np.linspace(-.05,-.05,201)
lorentz_freqs = []
kappa_tot = []
kappa_prod = []
phase = []
relative_phase = []
eig_0 = []
eig_1 = []
eig_2 = []
eig_3 = []
kappa_prod_comp = []

for i in range(len(delta)):
    H = np.array([[wa,0,ga,ga2],
                  [0,wb,-gb,gb2],
                  [ga,-gb,wp,1j*delta[i]*k+spl],
                  [ga2,gb2,-1j*delta[i]*k+spl, wn]])  
    H = H - 1j*gamma/2
    left_evs = la.eig(H, left = True, right = False)[1]
    right_evs = la.eig(H, left = False, right = True)[1]
    eig_0.append(right_evs[:,0])
    eig_1.append(right_evs[:,1])
    eig_2.append(right_evs[:,2])
    eig_3.append(right_evs[:,3])
#    right_evals = la.eigvals(H)#I'm pretty sure this is right eigenvalues but not 100% sure
    e,v =la.eig(H)
    right_evals = e
    lorentz_freqs.append([np.real(right_evals[0]),np.real(right_evals[1]),np.real(right_evals[2]),np.real(right_evals[3])])
    kappa_tot.append([-np.imag(right_evals[0])*2,-np.imag(right_evals[1])*2,-np.imag(right_evals[2])*2,-np.imag(right_evals[3])*2])
    kappa_prod.append(np.sqrt(gamma_list[input_port]*gamma_list[output_port])*
                      abs(np.asarray([eig_0[-1][output_port]*np.conj(left_evs[:,0][input_port]),
                      eig_1[-1][output_port]*np.conj(left_evs[:,1][input_port]),
                      eig_2[-1][output_port]*np.conj(left_evs[:,2][input_port]),
                      eig_3[-1][output_port]*np.conj(left_evs[:,3][input_port])])))
    phase.append(np.angle(np.asarray([eig_0[-1][output_port]*np.conj(left_evs[:,0][input_port]),
                      eig_1[-1][output_port]*np.conj(left_evs[:,1][input_port]),
                      eig_2[-1][output_port]*np.conj(left_evs[:,2][input_port]),
                      eig_3[-1][output_port]*np.conj(left_evs[:,3][input_port])])))
    kappa_prod_comp.append(np.sqrt(gamma_list[input_port]*gamma_list[output_port])*
                      (np.asarray([eig_0[-1][output_port]*np.conj(left_evs[:,0][input_port]),
                      eig_1[-1][output_port]*np.conj(left_evs[:,1][input_port]),
                      eig_2[-1][output_port]*np.conj(left_evs[:,2][input_port]),
                      eig_3[-1][output_port]*np.conj(left_evs[:,3][input_port])])))
#print(lorentz_freqs)
#print(kappa_prod)
#print(kappa_tot)
eig_0_0 = np.zeros(len(delta))
eig_0_1 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_0_0[i] = abs(eig_0[i][0])**2
    eig_0_1[i] = abs(eig_0[i][1])**2
#    
#plt.figure()
#plt.title('eig_0')
#plt.plot(delta,eig_0_0, label = 'cav 1 part')
#plt.plot(delta,eig_0_1, label = 'cav 2 part')
#plt.legend()
#
eig_1_0 = np.zeros(len(delta))
eig_1_1 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_1_0[i] = abs(eig_1[i][0])**2
    eig_1_1[i] = abs(eig_1[i][1])**2
#    
#plt.figure()
#plt.title('eig_1')
#plt.plot(delta,eig_1_0, label = 'cav 1 part')
#plt.plot(delta,eig_1_1, label = 'cav 2 part')
#plt.legend()
#
eig_2_0 = np.zeros(len(delta))
eig_2_1 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_2_0[i] = abs(eig_2[i][0])**2
    eig_2_1[i] = abs(eig_2[i][1])**2
#    
#plt.figure()
#plt.title('eig_2')
#plt.plot(delta,eig_2_0, label = 'cav 1 part')
#plt.plot(delta,eig_2_1, label = 'cav 2 part')
#plt.legend()
#
eig_3_0 = np.zeros(len(delta))
eig_3_1 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_3_0[i] = abs(eig_3[i][0])**2
    eig_3_1[i] = abs(eig_3[i][1])**2
#    
#plt.figure()
#plt.title('eig_3')
#plt.plot(delta,eig_3_0, label = 'cav 1 part')
#plt.plot(delta,eig_3_1, label = 'cav 2 part')
#plt.legend()

eig_cav1 = []
eig_cav2 = []
index_cav1 = []
index_cav2 = []

#if max([eig_0_0[-1],eig_1_0[-1],eig_2_0[-1],eig_3_0[-1]]) > max([eig_0_1[-1],eig_1_1[-1],eig_2_1[-1],eig_3_1[-1]]):
#    cav_1_max = True
#else:
#    cav_1_max = False

#for i in range(len(delta)):
#    eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
#    eig1_part = [eig_0_0[i],eig_1_0[i],eig_2_0[i],eig_3_0[i]]
#    eig2_part = [eig_0_1[i],eig_1_1[i],eig_2_1[i],eig_3_1[i]]
#    if cav_1_max:
#        eig1_ind_sort = np.argsort(eig1_part)
#        index1 = eig1_ind_sort[-1]
#        index2 = eig1_ind_sort[-2]
#    else:
#        eig2_ind_sort = np.argsort(eig2_part)
#        index1 = eig2_ind_sort[-2]
#        index2 = eig2_ind_sort[-1]
#    index_cav1.append(int(index1))
#    index_cav2.append(int(index2))
#    eig_cav1.append(list(eigs[index1]))
#    eig_cav2.append(list(eigs[index2]))
for i in range(len(delta)):
    eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
    eigsum = [eig_0_0[i] +eig_0_1[i] ,eig_1_0[i] + eig_1_1[i],eig_2_0[i] + eig_2_1[i],eig_3_0[i]+eig_3_1[i]]
    eig_ind_sort = np.argsort(eigsum)
    index1 = eig_ind_sort[-1]
    index2 = eig_ind_sort[-2]
    index_cav1.append(int(index1))
    index_cav2.append(int(index2))
    eig_cav1.append(list(eigs[index1]))
    eig_cav2.append(list(eigs[index2]))    
eig_cav1_0 = np.zeros(len(delta))
eig_cav1_1 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_cav1_0[i] = abs(eig_cav1[i][0])**2
    eig_cav1_1[i] = abs(eig_cav1[i][1])**2
    
eig_cav2_0 = np.zeros(len(delta))
eig_cav2_1 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_cav2_0[i] = abs(eig_cav2[i][0])**2
    eig_cav2_1[i] = abs(eig_cav2[i][1])**2
    
top_index = []
bottom_index = []

for i in range(len(delta)):
    if lorentz_freqs[i][index_cav1[i]]>lorentz_freqs[i][index_cav2[i]]:
        top_index.append(index_cav1[i])
        bottom_index.append(index_cav2[i])
    else:
        top_index.append(index_cav2[i])
        bottom_index.append(index_cav1[i])
    eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
    eig_cav1.append(list(eigs[top_index[-1]]))
    eig_cav2.append(list(eigs[bottom_index[-1]]))
    
eig_cav1_0 = np.zeros(len(delta))
eig_cav1_1 = np.zeros(len(delta))
eig_cav1_2 = np.zeros(len(delta))
eig_cav1_3 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_cav1_0[i] = abs(eig_cav1[i][0])**2
    eig_cav1_1[i] = abs(eig_cav1[i][1])**2
    eig_cav1_2[i] = abs(eig_cav1[i][2])**2
    eig_cav1_3[i] = abs(eig_cav1[i][3])**2
    
eig_cav2_0 = np.zeros(len(delta))
eig_cav2_1 = np.zeros(len(delta))
eig_cav2_2 = np.zeros(len(delta))
eig_cav2_3 = np.zeros(len(delta))
for i in range(len(delta)):
    eig_cav2_0[i] = abs(eig_cav2[i][0])**2
    eig_cav2_1[i] = abs(eig_cav2[i][1])**2
    eig_cav2_2[i] = abs(eig_cav2[i][2])**2
    eig_cav2_3[i] = abs(eig_cav2[i][3])**2
    
#top_index = index_cav1[:8]+index_cav2[8:]
#bottom_index = index_cav2[:8]+index_cav1[8:]
#top_index = index_cav1
#bottom_index = index_cav2
#top_index = [1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3]
#bottom_index =[2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2]
#plt.figure()
#plt.title('top mode')
#plt.plot(delta,list(eig_cav1_0), label = 'cav 1 part')
#plt.plot(delta,list(eig_cav1_1), label = 'cav 2 part')
#plt.plot(delta,list(eig_cav1_2), label = 'mode 3 part')
#plt.plot(delta,list(eig_cav1_3), label = 'mode 4 part')
#plt.legend()
#
#    
#plt.figure()
#plt.title('bottom mode')
#plt.plot(delta,list(eig_cav2_0), label = 'cav 1 part')
#plt.plot(delta,list(eig_cav2_1), label = 'cav 2 part')
#plt.plot(delta,list(eig_cav2_2), label = 'mode 3 part')
#plt.plot(delta,list(eig_cav2_3), label = 'mode 4 part')
#plt.legend()

lorentz_freqs_2 = []
kappa_tot_2 = []
kappa_prod_2 = []
phi21 = []
kp_phase_top = []
kp_phase_bottom = []
kappa_prod_comp_plot = []
kappa_prod_comp_plot_o = []
relative_phase = []
for i in range(len(top_index)):
    lorentz_freqs_2.append([lorentz_freqs[i][top_index[i]],lorentz_freqs[i][bottom_index[i]]])
    kappa_tot_2.append([kappa_tot[i][top_index[i]],kappa_tot[i][bottom_index[i]]])
    kappa_prod_2.append([A*kappa_prod[i][top_index[i]],A*kappa_prod[i][bottom_index[i]]])
    phi21.append(-phase[i][top_index[i]]+phase[i][bottom_index[i]])
    kp_phase_top.append(phase[i][top_index[i]])
    kp_phase_bottom.append(phase[i][bottom_index[i]])
    kappa_prod_comp_plot.append([A*kappa_prod_comp[i][top_index[i]],A*kappa_prod_comp[i][bottom_index[i]]])
    kappa_prod_comp_plot_o.append([A*kappa_prod_comp[i][3-top_index[i]],A*kappa_prod_comp[i][3-bottom_index[i]]])
    
kappa_prod_comp_plot_r = list(np.real(np.asarray(kappa_prod_comp_plot)))
kappa_prod_comp_plot_c = list(np.imag(np.asarray(kappa_prod_comp_plot)))

fitting_data = [10.78,10.829,10.806]
fitting_ktot = [2.31e7,2.118e7,9.906e5]
fitting_kprod = [3.65e10,8.6e10,1.3447e9]

plt.figure()

plt.title('freqs 2')
for i in range(len(lorentz_freqs_2[0])):
    plt.plot(delta,[pt[i] for pt in lorentz_freqs_2],label = 'model index %s'%i)
for j in range(len(lorentz_freqs[0])):
    plt.plot(delta,np.transpose(lorentz_freqs)[j],label = 'all modes index %s'%j )
plt.scatter(fields,np.asarray(freq2)/1e9, label = 'data index 0')
plt.scatter(fields,np.asarray(freq1)/1e9, label = 'data index 1')
for i in range(len(fitting_data)):
    plt.scatter([0],fitting_data[i], marker = 'o')
plt.ylim(10.7,10.9)
plt.legend()

plt.figure()

plt.title('kappa_tot 2')
for i in range(len(kappa_tot_2[0])):
    plt.plot(delta,[pt[i] for pt in kappa_tot_2],label = 'model index %s'%i)
plt.scatter(fields,np.asarray(kappa_tot2)/1e9,label = 'data index 0')
plt.scatter(fields,np.asarray(kappa_tot1)/1e9,label = 'data index 1')
for i in range(len(fitting_data)):
    plt.scatter([0],fitting_ktot[i]/1e9, marker = 'o')
plt.legend()

plt.figure()

plt.title('kappa_prod 2')
for i in range(len(kappa_prod_2[0])):
    plt.plot(delta,[pt[i] for pt in kappa_prod_2],label = 'model index %s'%i)
plt.scatter(fields,np.asarray(kappa_prod2)/1e9,label = 'data index 0')
plt.scatter(fields,np.asarray(kappa_prod1)/1e9,label = 'data index 1')
for i in range(len(fitting_data)):
    plt.scatter([0],fitting_kprod[i]**.5/1e9, marker = 'o')
plt.legend()


#fitting_data = [10.78,10.829,10.806]
#fitting_ktot = []
#
#plt.figure()
#for i in range(len(lorentz_freqs[0])):
#    plt.scatter(fields,lorentz_freqs[0][i], marker = 'o')
#for j in range(len(fitting_data)):
#    plt.scatter(fields,fitting_data[j], marker = '^')
#plt.legend()
    



#
#plt.figure()
#
#plt.title('kappa_prod comp')
#for i in range(len(kappa_prod_2[0])):
#    plt.scatter([pt[i] for pt in kappa_prod_comp_plot_r],[pt[i] for pt in kappa_prod_comp_plot_c],label = 'model index %s'%i)
#
#plt.legend()

#
#plt.figure()
#plt.title('phi21')
#plt.plot(delta,phi21, label = 'phi21')
#plt.plot(delta, kp_phase_top, label = 'top' )
#plt.plot(delta, kp_phase_bottom, label = 'bottom' )
#plt.legend()



#
#plt.figure()
#
#plt.title('phase 2')
#plt.plot(delta,phase_2)
#plt.legend()
#
#plt.figure()
#
#plt.title('freqs')
#for i in range(len(lorentz_freqs[0])):
#    plt.plot(delta,[pt[i] for pt in lorentz_freqs],label = 'index %s'%i)
#plt.legend()
#
#plt.figure()
#
#plt.title('kappa_tot')
#for i in range(len(kappa_tot[0])):
#    plt.plot(delta,[pt[i] for pt in kappa_tot],label = 'index %s'%i)
#plt.legend()
#
#plt.figure()
#
#plt.title('kappa_prod')
#for i in range(len(kappa_prod[0])):
#    plt.plot(delta,[pt[i] for pt in kappa_prod],label = 'index %s'%i)
#plt.legend()
#
#plt.figure()
#
#plt.title('phase')
#for i in range(len(phase[0])):
#    plt.plot(delta,[pt[i] for pt in phase],label = 'index %s'%i)
#plt.legend()




