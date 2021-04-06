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
    delta = np.linspace(0,-.05,26)
    lorentz_freqs = []
    kappa_tot = []
    kappa_prod = []
    input_port = 1 #signifying that wer are inputting on the first port
    output_port = 3 #signifying we are reading out through the second port
    eig_0 = []
    eig_1 = []
    eig_2 = []
    eig_3 = []
    
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
        right_evals = la.eigvals(H)#I'm pretty sure this is right eigenvalues but not 100% sure
    
        lorentz_freqs.append([np.real(right_evals[0]),np.real(right_evals[1]),np.real(right_evals[2]),np.real(right_evals[3])])
        kappa_tot.append([-np.imag(right_evals[0])*2,-np.imag(right_evals[1])*2,-np.imag(right_evals[2])*2,-np.imag(right_evals[3])*2])
        kappa_prod.append((gamma_list[input_port]*gamma_list[output_port])*abs(np.asarray([right_evs[output_port][0]*np.conj(left_evs[input_port][0]),
                          right_evs[output_port][1]*np.conj(left_evs[input_port][1]),
                          right_evs[output_port][2]*np.conj(left_evs[input_port][2]),
                          right_evs[output_port][3]*np.conj(left_evs[input_port][3])]))**2)
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

    if max([eig_0_0[-1],eig_1_0[-1],eig_2_0[-1],eig_3_0[-1]]) > max([eig_0_1[-1],eig_1_1[-1],eig_2_1[-1],eig_3_1[-1]]):
        cav_1_max = True
    else:
        cav_1_max = False

    for i in range(len(delta)):
        eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
        eig1_part = [eig_0_0[i],eig_1_0[i],eig_2_0[i],eig_3_0[i]]
        eig2_part = [eig_0_1[i],eig_1_1[i],eig_2_1[i],eig_3_1[i]]
        if cav_1_max:
            eig1_ind_sort = np.argsort(eig1_part)
            index1 = eig1_ind_sort[-1]
            index2 = eig1_ind_sort[-2]
        else:
            eig2_ind_sort = np.argsort(eig2_part)
            index1 = eig2_ind_sort[-2]
            index2 = eig2_ind_sort[-1]
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
    
kappa_tot_scale = 1
kappa_prod_scale = 1e2

freq1 = [1.08081856e+10, 1.08081064e+10, 1.08081056e+10, 1.08080787e+10,
       1.08079829e+10, 1.08080038e+10, 1.08079915e+10, 1.08080676e+10,
       1.08080144e+10, 1.08076617e+10, 1.08069443e+10, 1.08065044e+10,
       1.08062791e+10, 1.08060650e+10, 1.08058279e+10, 1.08057616e+10,
       1.08058314e+10, 1.08057170e+10, 1.08056404e+10, 1.08054877e+10,
       1.08054497e+10, 1.08054538e+10, 1.08054972e+10, 1.08052549e+10,
       1.08053990e+10, 1.08051230e+10]
freq2 = [1.08241210e+10, 1.08236911e+10, 1.08228877e+10, 1.08208171e+10,
       1.08184651e+10, 1.08147895e+10, 1.08125241e+10, 1.08112090e+10,
       1.08106380e+10, 1.08104618e+10, 1.08103716e+10, 1.08105378e+10,
       1.08107078e+10, 1.08107819e+10, 1.08108998e+10, 1.08109229e+10,
       1.08109881e+10, 1.08109352e+10, 1.08109449e+10, 1.08109481e+10,
       1.08109334e+10, 1.08109154e+10, 1.08109047e+10, 1.08108497e+10,
       1.08109201e+10, 1.08108583e+10]
kappa_tot1 = [1119745.66120935, 1268610.32797188, 1291730.62246295,
       1444275.57155828, 1651193.71901025, 1914512.57139387,
       2307603.86755862, 2572518.11067425, 3013164.58756861,
       3789780.88427191, 4507201.27389526, 4632129.4223025 ,
       3911137.90366337, 3705487.82246245, 3250321.41105881,
       2997405.27915722, 2944189.58634288, 2632945.8818832 ,
       2576476.26594947, 2459850.91771862, 2388368.2351226 ,
       2462922.02139303, 2254056.48957693, 2228780.48201033,
       2222499.17950223, 2203722.49701684]
kappa_tot2 = [24595006.18268016, 24238942.47139579, 25734529.7357273 ,
       23468854.23394037, 21724071.71068322, 22387399.52871925,
       17055060.48075255, 15811284.7356298 , 12332497.54203614,
        8181610.60339105,  5571818.131129  ,  4551930.33449613,
        3584262.43906374,  3085276.72924327,  2594713.01638649,
        2308415.78474101,  2120392.460538  ,  1889751.7409438 ,
        1734900.13503547,  1557671.32816325,  1424920.01268665,
        1374927.04074583,  1308766.23809949,  1223127.60466848,
        1214264.04560343,  1113025.47005813]
kappa_prod1 = [2.69501221e+08, 3.30155951e+08, 8.71232973e+08, 2.18422011e+09,
       4.00640457e+09, 8.01994167e+09, 1.38779367e+10, 2.16015622e+10,
       3.54112849e+10, 5.81173153e+10, 5.37399865e+10, 2.91021451e+10,
       1.33174424e+10, 7.67396355e+09, 3.96566846e+09, 2.66823016e+09,
       1.87717819e+09, 1.23481870e+09, 8.97248987e+08, 5.55066987e+08,
       3.77911806e+08, 3.13935915e+08, 2.62303899e+08, 1.83486166e+08,
       1.34320362e+08, 8.52443428e+07]
kappa_prod1 = list(np.sqrt(np.asarray(kappa_prod1)))
kappa_prod2 = [3.37534424e+11, 3.44272244e+11, 3.94691509e+11, 3.77334403e+11,
       3.72975807e+11, 4.23927244e+11, 3.39221684e+11, 3.41207915e+11,
       3.23920926e+11, 2.91084111e+11, 1.92007868e+11, 1.15566649e+11,
       7.08121476e+10, 5.27640297e+10, 3.93285604e+10, 3.26184275e+10,
       2.79270806e+10, 2.31912462e+10, 2.01417367e+10, 1.65005778e+10,
       1.39721726e+10, 1.26990730e+10, 1.17672357e+10, 1.01588495e+10,
       9.10869323e+09, 7.73732598e+09]
kappa_prod2 = list(np.sqrt(np.asarray(kappa_prod2)))
datas = list(np.asarray(freq2)/1e9) + list(np.asarray(freq1)/1e9) + list(np.asarray(kappa_tot2)*kappa_tot_scale/1e9) + list(np.asarray(kappa_tot1)*kappa_tot_scale/1e9) + list(np.asarray(kappa_prod2)*kappa_prod_scale/1e9) + list(np.asarray(kappa_prod1)*kappa_prod_scale/1e9)
datas = np.asarray(datas)

freq1_err = [10040.58708447, 10797.43093447,  6680.51124137,  5296.78505019,
        5271.00621261,  3687.48813341,  4577.00698619,  4106.82756027,
        5442.09442079, 22670.85115172, 11365.77139844, 12455.30850576,
        8600.51738744,  8974.42023373,  8954.25845939,  9196.09821532,
       10537.32303981, 10160.56690983, 10846.23622983, 13598.93701152,
       15664.44061561, 18709.56399975, 20305.5510503 , 30483.59166954,
       29155.6439816 , 46894.24119294]
freq2_err = [60181.2363658 , 59322.32608067, 62146.69061928, 55471.84144676,
       53854.88111139, 46378.68602476, 33314.16596772, 26550.29479357,
       22445.4341359 , 19868.8545943 ,  8972.06883799,  5207.84991609,
        3466.57455424,  2579.29043594,  1939.71509637,  1611.13971201,
        1557.25415303,  1346.37305583,  1128.10569412,  1117.41104349,
        1078.73628327,  1091.26996365,  1231.20738248,  1380.27586544,
        1453.80880606,  1957.44396601]
kappa_tot1_err = [60181.2363658 , 59322.32608067, 62146.69061928, 55471.84144676,
       53854.88111139, 46378.68602476, 33314.16596772, 26550.29479357,
       22445.4341359 , 19868.8545943 ,  8972.06883799,  5207.84991609,
        3466.57455424,  2579.29043594,  1939.71509637,  1611.13971201,
        1557.25415303,  1346.37305583,  1128.10569412,  1117.41104349,
        1078.73628327,  1091.26996365,  1231.20738248,  1380.27586544,
        1453.80880606,  1957.44396601]
kappa_tot2_err = [24595006.18268016, 24238942.47139579, 25734529.7357273 ,
       23468854.23394037, 21724071.71068322, 22387399.52871925,
       17055060.48075255, 15811284.7356298 , 12332497.54203614,
        8181610.60339105,  5571818.131129  ,  4551930.33449613,
        3584262.43906374,  3085276.72924327,  2594713.01638649,
        2308415.78474101,  2120392.460538  ,  1889751.7409438 ,
        1734900.13503547,  1557671.32816325,  1424920.01268665,
        1374927.04074583,  1308766.23809949,  1223127.60466848,
        1214264.04560343,  1113025.47005813]
kappa_prod1_err = [6.12100227e+06, 9.70148977e+06, 1.55046231e+07, 2.99002030e+07,
       4.70442301e+07, 6.16575869e+07, 1.23864960e+08, 1.74847951e+08,
       4.16647379e+08, 1.32491868e+09, 9.49338101e+08, 4.26599817e+08,
       1.61165147e+08, 8.97511587e+07, 4.48357867e+07, 3.27206407e+07,
       2.99470051e+07, 2.10071428e+07, 1.45305982e+07, 1.16371744e+07,
       8.80730427e+06, 8.95604806e+06, 9.11426076e+06, 1.02106621e+07,
       6.01251897e+06, 6.43369452e+06]

kappa_prod2_err = [4.74854209e+09, 4.75023348e+09, 5.35810789e+09, 4.73771606e+09,
       4.38946808e+09, 3.82499094e+09, 2.60443553e+09, 2.00518616e+09,
       2.14981874e+09, 3.80676625e+09, 1.80198986e+09, 8.42055411e+08,
       3.21535356e+08, 1.95761552e+08, 1.13309573e+08, 8.96571197e+07,
       7.65741699e+07, 5.95717750e+07, 4.63802353e+07, 3.94698023e+07,
       3.31454589e+07, 3.18026248e+07, 3.10384129e+07, 2.95507886e+07,
       2.65279083e+07, 2.85849078e+07]

datas_errs = list(np.asarray(freq2_err)/1e9) + list(np.asarray(freq1_err)/1e9) + list(np.asarray(kappa_tot2_err)*kappa_tot_scale/1e9) + list(np.asarray(kappa_tot1_err)*kappa_tot_scale/1e9) + list(np.asarray(kappa_prod2_err)*kappa_prod_scale/1e9) + list(np.asarray(kappa_prod1_err)*kappa_prod_scale/1e9)

fields = np.linspace(0,-.05,26)

fix_vary = False
params = lmfit.Parameters()
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
print 'data seze %s'%(len(datas))
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
gb = ga
gb2 = ga2
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
delta = np.linspace(0,-.05,101)
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

input_port = 1 #signifying that wer are inputting on the first port
output_port = 3 #signifying we are reading out through either the second cavity or the copper waveguide port
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

if max([eig_0_0[-1],eig_1_0[-1],eig_2_0[-1],eig_3_0[-1]]) > max([eig_0_1[-1],eig_1_1[-1],eig_2_1[-1],eig_3_1[-1]]):
    cav_1_max = True
else:
    cav_1_max = False

for i in range(len(delta)):
    eigs = [eig_0[i],eig_1[i],eig_2[i],eig_3[i]]
    eig1_part = [eig_0_0[i],eig_1_0[i],eig_2_0[i],eig_3_0[i]]
    eig2_part = [eig_0_1[i],eig_1_1[i],eig_2_1[i],eig_3_1[i]]
    if cav_1_max:
        eig1_ind_sort = np.argsort(eig1_part)
        index1 = eig1_ind_sort[-1]
        index2 = eig1_ind_sort[-2]
    else:
        eig2_ind_sort = np.argsort(eig2_part)
        index1 = eig2_ind_sort[-2]
        index2 = eig2_ind_sort[-1]
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
plt.figure()
plt.title('top mode')
plt.plot(delta,list(eig_cav1_0), label = 'cav 1 part')
plt.plot(delta,list(eig_cav1_1), label = 'cav 2 part')
plt.plot(delta,list(eig_cav1_2), label = 'mode 3 part')
plt.plot(delta,list(eig_cav1_3), label = 'mode 4 part')
plt.legend()

    
plt.figure()
plt.title('bottom mode')
plt.plot(delta,list(eig_cav2_0), label = 'cav 1 part')
plt.plot(delta,list(eig_cav2_1), label = 'cav 2 part')
plt.plot(delta,list(eig_cav2_2), label = 'mode 3 part')
plt.plot(delta,list(eig_cav2_3), label = 'mode 4 part')
plt.legend()

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

plt.figure()

plt.title('freqs 2')
for i in range(len(lorentz_freqs_2[0])):
    plt.plot(delta,[pt[i] for pt in lorentz_freqs_2],label = 'model index %s'%i)
plt.scatter(fields,np.asarray(freq2)/1e9, label = 'data index 0')
plt.scatter(fields,np.asarray(freq1)/1e9, label = 'data index 1')

plt.legend()

plt.figure()

plt.title('kappa_tot 2')
for i in range(len(kappa_tot_2[0])):
    plt.plot(delta,[pt[i] for pt in kappa_tot_2],label = 'model index %s'%i)
plt.scatter(fields,np.asarray(kappa_tot2)/1e9,label = 'data index 0')
plt.scatter(fields,np.asarray(kappa_tot1)/1e9,label = 'data index 1')

plt.legend()

plt.figure()

plt.title('kappa_prod 2')
for i in range(len(kappa_prod_2[0])):
    plt.plot(delta,[pt[i] for pt in kappa_prod_2],label = 'model index %s'%i)
plt.scatter(fields,np.asarray(kappa_prod2)/1e9,label = 'data index 0')
plt.scatter(fields,np.asarray(kappa_prod1)/1e9,label = 'data index 1')

plt.figure()

plt.title('kappa_prod comp')
for i in range(len(kappa_prod_2[0])):
    plt.scatter([pt[i] for pt in kappa_prod_comp_plot_r],[pt[i] for pt in kappa_prod_comp_plot_c],label = 'model index %s'%i)

plt.legend()


plt.figure()
plt.title('phi21')
plt.plot(delta,phi21, label = 'phi21')
plt.plot(delta, kp_phase_top, label = 'top' )
plt.plot(delta, kp_phase_bottom, label = 'bottom' )
plt.legend()



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




