# -*- coding: utf-8 -*-
"""
Created on Fri Mar 05 16:48:49 2021

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 10:50:07 2021

@author: WangLab
"""

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
#import lmfit
matplotlib.interactive(True)


input_port = 0 #signifying what port we are driving on
output_port = 3 #signifying what port the signal is coming out of
delta = np.concatenate((np.linspace(-.05,0,26),np.linspace(0,.05,26))) #specifying field range

def Sij_resid(params,x,y):
    param = params.valuesdict()
    wa = param['wa']
    wb = param['wb']
    ka = param['ka']
    kb = param['kb']
    ga = param['ga']
    ga2 = param['ga2']
    gab_rat = param['gab_rat']
    gab2_rat = param['gab_rat']
    gb = ga*gab_rat
    gb2 = ga2*gab2_rat
    ga_an = param['ga_an']
    ga2_an = param['ga2_an']
    gb_an = ga_an*gab_rat
    gb2_an = ga2_an*gab2_rat
    wp = param['wp']
    k = param['k']
    spl = param['spl']
    wp = param['wp']
    wn = param['wn']
    wni_an = param['wni_an']
    gamma1 = param['gamma1']
    gamma2 = param['gamma2']
    # gamma3 = param['gamma3']
    gamma4 = param['gamma4']
    A = param['A']
    ani_diag = param['ani_diag']
    null_field = param['null_field']
    

    # phi = param['phi']
    gamma_list = [gamma1,gamma2,0,gamma4]
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,0,0],[0,0,0,gamma4]])
    lorentz_freqs = []
    kappa_tot = []
    kappa_prod = []

    eig_0 = []
    eig_1 = []
    eig_2 = []
    eig_3 = []
    
    
    
    for i in range(len(delta)): #getting model data for each field delta
        wpp = wp + ani_diag*((1/np.cosh(delta[i]/null_field)))
        wnn = wn - ani_diag*((1/np.cosh(delta[i]/null_field))) - 1j*(wni_an/2)*((1/np.cosh(delta[i]/null_field)))
        wpn = -1j*delta[i]*k+spl*((1/np.cosh(delta[i]/null_field)))
        wnp = 1j*delta[i]*k+spl*((1/np.cosh(delta[i]/null_field)))
        ga_tot = ga + ga_an*((1/np.cosh(delta[i]/null_field)))
        ga2_tot = ga2 + ga2_an*((1/np.cosh(delta[i]/null_field)))
        gb_tot = gb + gb_an*((1/np.cosh(delta[i]/null_field)))
        gb2_tot = gb2 + gb2_an*((1/np.cosh(delta[i]/null_field)))
        H = np.array([[wa-1j*ka/2,0,ga_tot,ga2_tot],
                      [0,wb-1j*kb/2,-gb_tot,gb2_tot],
                      [ga_tot,-gb_tot,wpp,wpn],
                      [ga2_tot,gb2_tot,wnp, wnn]])
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

    lorentz_freqs_2 = []
    kappa_tot_2 = []
    kappa_prod_2 = []
    lorentz_freqs_1 = []
    kappa_tot_1 = []
    kappa_prod_1 = []

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

    return ((model_vals-y))**2


kappa_tot_scale = 1
kappa_prod_scale = 1e2

#data_txt_neg = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210109_232841\\results.txt')
data_txt_neg = np.loadtxt('C:\Users\WangLab\Documents\circulator results\\2021-03-11 16-09-18\\0to-0.05results.txt')

data_txt = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210110_083300\\results.txt')
data_txt = np.transpose(data_txt)
data_txt_neg = np.transpose(data_txt_neg)
#data_txt = np.loadtxt('C:\Users\WangLab\Documents\circulator results\\20210310_234625\\three_mode_results.txt')
#data_txt = np.transpose(data_txt)
#data_txt_neg = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210310_234625\\three_mode_results_neg.txt')
#data_txt_neg = np.transpose(data_txt_neg)

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

freq2 = np.concatenate((data_txt_neg[3][::-1],data_txt[1]))
freq2_err = np.concatenate((data_txt_neg[4][::-1],data_txt[2]))
freq1 = np.concatenate((data_txt_neg[1][::-1],data_txt[3]))
freq1_err = np.concatenate((data_txt_neg[2][::-1],data_txt[4]))
kappa_tot2 = np.concatenate((data_txt_neg[7][::-1],data_txt[5]))
kappa_tot2_err = np.concatenate((data_txt_neg[8][::-1],data_txt[6]))
kappa_tot1 = np.concatenate((data_txt_neg[5][::-1],data_txt[7]))
kappa_tot1_err = np.concatenate((data_txt_neg[6][::-1],data_txt[8]))
kappa_prod2 = np.concatenate((data_txt_neg[11][::-1],data_txt[9]))
kappa_prod2_err = np.concatenate((data_txt_neg[12][::-1],data_txt[10]))
kappa_prod1 = np.concatenate((data_txt_neg[9][::-1],data_txt[11]))
kappa_prod1_err = np.concatenate((data_txt_neg[10][::-1],data_txt[12]))
phi21 = np.concatenate((data_txt_neg[13][::-1],data_txt[13]))
phi21_err = np.concatenate((data_txt_neg[14][::-1],data_txt[14]))

#freq2 = np.concatenate((data_txt_neg[5][::-1],data_txt[5]))
#freq2_err = np.concatenate((data_txt_neg[6][::-1],data_txt[6]))
#freq1 = np.concatenate((data_txt_neg[1][::-1],data_txt[1]))
#freq1_err = np.concatenate((data_txt_neg[2][::-1],data_txt[2]))
#kappa_tot2 = np.concatenate((data_txt_neg[11][::-1],data_txt[11]))
#kappa_tot2_err = np.concatenate((data_txt_neg[12][::-1],data_txt[12]))
#kappa_tot1 = np.concatenate((data_txt_neg[7][::-1],data_txt[7]))
#kappa_tot1_err = np.concatenate((data_txt_neg[8][::-1],data_txt[8]))
#kappa_prod2 = np.concatenate((data_txt_neg[17][::-1],data_txt[17]))
#kappa_prod2_err = np.concatenate((data_txt_neg[18][::-1],data_txt[18]))
#kappa_prod1 = np.concatenate((data_txt_neg[13][::-1],data_txt[13]))
#kappa_prod1_err = np.concatenate((data_txt_neg[14][::-1],data_txt[14]))
#phi21 = np.concatenate((data_txt_neg[19][::-1],data_txt[19]))
#phi21_err = np.concatenate((data_txt_neg[20][::-1],data_txt[20]))

replace_one_point = False
if replace_one_point:
    itime = 36
    kappa_tot1[itime] = result.params['kappa_a1'].value
    kappa_tot1_err[itime] = result.params['kappa_a1'].stderr
    freq1[itime] = result.params['omega_c'].value
    freq1_err[itime] = result.params['omega_c'].stderr

    kappa_prod1[itime] = result.params['kappa_prod1'].value
    kappa_prod1_err[itime] = result.params['kappa_prod1'].stderr
    kappa_prod2[itime] = result.params['kappa_prod2'].value
    kappa_prod2_err[itime] = result.params['kappa_prod2'].stderr
    kappa_tot2[itime] = result.params['kappa_a2'].value
    kappa_tot2_err[itime] = result.params['kappa_a2'].stderr
    freq2[itime] = result.params['omega_c2'].value
    freq2_err[itime] = result.params['omega_c2'].stderr
    phi21[itime] = result.params['phi21'].value
    phi21_err[itime] = result.params['phi21'].stderr
    
#    itime = 0
#    kappa_tot1[itime] = result_.params['kappa_a1'].value
#    kappa_tot1_err[itime] = result_.params['kappa_a1'].stderr
#    freq2[itime] = result_.params['omega_c'].value
#    freq2_err[itime] = result_.params['omega_c'].stderr
#
#    kappa_prod2[itime] = result_.params['kappa_prod1'].value
#    kappa_prod2_err[itime] = result_.params['kappa_prod1'].stderr
#    kappa_prod1[itime] = result_.params['kappa_prod2'].value
#    kappa_prod1_err[itime] = result_.params['kappa_prod2'].stderr
#    kappa_tot2[itime] = result_.params['kappa_a2'].value
#    kappa_tot2_err[itime] = result_.params['kappa_a2'].stderr
#    freq1[itime] = result_.params['omega_c2'].value
#    freq1_err[itime] = result_.params['omega_c2'].stderr
#    phi21[itime] = result_.params['phi21'].value
#    phi21_err[itime] = result_.params['phi21'].stderr

kappa_prod1 = list(np.sqrt(np.asarray(kappa_prod1)))
kappa_prod2 = list(np.sqrt(np.asarray(kappa_prod2)))
datas = list(np.asarray(freq2)/1e9) + list(np.asarray(freq1)/1e9) + list(np.asarray(kappa_tot2)*kappa_tot_scale/1e9) + list(np.asarray(kappa_tot1)*kappa_tot_scale/1e9) + list(np.asarray(kappa_prod2)*kappa_prod_scale/1e9) + list(np.asarray(kappa_prod1)*kappa_prod_scale/1e9)
datas = np.asarray(datas)

kappa_prod1_err = list((np.asarray(kappa_prod1_err)/np.asarray(kappa_prod1)**2 * 0.5)* kappa_prod1)
kappa_prod2_err = list((np.asarray(kappa_prod2_err)/np.asarray(kappa_prod2)**2 * 0.5)* kappa_prod2)
datas_errs = list(np.asarray(freq2_err)/1e9) + list(np.asarray(freq1_err)/1e9) + list(np.asarray(kappa_tot2_err)*kappa_tot_scale/1e9) + list(np.asarray(kappa_tot1_err)*kappa_tot_scale/1e9) + list(np.asarray(kappa_prod2_err)*kappa_prod_scale/1e9) + list(np.asarray(kappa_prod1_err)*kappa_prod_scale/1e9)

fields = np.concatenate((np.linspace(-.05,0,26),np.linspace(0,.05,26)))

fix_vary = False
params = lmfit.Parameters()
ani_diag = 0.07
params.add('gamma1',value = .00015, min = 0, max = .001, vary = False)
params.add('gamma2',value = .001, min = 0, max = .005, vary = False)
params.add('gamma3',value = 0.002, vary = False)
params.add('gamma4',value = .6, min = 0, vary = False)
params.add('wa',value = 10.8104, vary = False)
params.add('wb',value = 10.804, vary = False)
params.add('ka', value = .0005, vary = False)
params.add('kb', value = .001, vary = False)
params.add('wp',value = 10.72, vary = False, max = 10.8)
params.add('wn',value = 10.82, vary = False)
params.add('wni_an',value = 0, vary = False)
params.add('ga',value = 0.01, vary = False)
params.add('ga2',value = .005, vary = False)
params.add('ga_an',value = 0.0095, vary = False)
params.add('ga2_an',value = .003, vary = False)
params.add('gab_rat',value = 1, vary = False)
params.add('gab2_rat',value = 1, vary = False)
params.add('spl',value = 0.105, vary = False, min=-0.05, max=0.12)
params.add('A',value = .45, vary = False)
params.add('k',value =9, vary = False)
params.add('ani_diag',value = 0.07, vary = False)
params.add('null_field' ,value = 0.0185, vary = False)


# params.add('phi',value = 0, vary = fix_vary)
#freqs = freq/1e9
print 'data seze %s'%(len(datas))
result = lmfit.minimize(Sij_resid, params, args=(fields, datas))
lmfit.report_fit(result.params)

gamma1 = result.params['gamma1'].value
gamma2 = result.params['gamma2'].value
gamma3 = result.params['gamma3'].value
gamma4 = result.params['gamma4'].value
wa = result.params['wa'].value
wb = result.params['wb'].value
ka = result.params['ka'].value
kb = result.params['kb'].value
wp = result.params['wp'].value
wn = result.params['wn'].value
wni_an = result.params['wni_an'].value
ga = result.params['ga'].value
ga2 = result.params['ga2'].value
ga_an = result.params['ga_an'].value
ga2_an = result.params['ga2_an'].value
gab_rat = result.params['gab_rat'].value
gab2_rat = result.params['gab2_rat'].value
gb =ga
gb2 = ga2
gb_an = gab_rat*ga_an
gb2_an = gab2_rat*ga2_an
spl = result.params['spl'].value
# delta = result.params['delta'].value
A=result.params['A'].value
k = result.params['k'].value
ani_diag = result.params['ani_diag'].value
null_field = result.params['null_field'].value

# phi = result.params['phi']
#w = freqs
identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
gamma_list = [gamma1,gamma2,gamma3,gamma4]
out_3 = []
delta = np.linspace(-.05,.05,201)
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
    wpp = wp + ani_diag*((1/np.cosh(delta[i]/null_field)))
    wnn = wn - ani_diag*((1/np.cosh(delta[i]/null_field))) - 1j*(wni_an/2)*((1/np.cosh(delta[i]/null_field)))
    wpn = -1j*delta[i]*k+spl*((1/np.cosh(delta[i]/null_field)))
    wnp = 1j*delta[i]*k+spl*((1/np.cosh(delta[i]/null_field)))
    ga_tot = ga + ga_an*((1/np.cosh(delta[i]/null_field)))
    ga2_tot = ga2 + ga2_an*((1/np.cosh(delta[i]/null_field)))
    gb_tot = gb + gb_an*((1/np.cosh(delta[i]/null_field)))
    gb2_tot = gb2 + gb2_an*((1/np.cosh(delta[i]/null_field)))
    H = np.array([[wa-1j*ka/2,0,ga_tot,ga2_tot],
                  [0,wb-1j*kb/2,-gb_tot,gb2_tot],
                  [ga_tot,-gb_tot,wpp,wpn],
                  [ga2_tot,gb2_tot,wnp, wnn]])
    H = H - 1j*gamma/2
    left_evs = la.eig(H, left = True, right = False)[1]
    right_evs = la.eig(H, left = False, right = True)[1]
#    eig_0.append(left_evs[:,0])
#    eig_1.append(left_evs[:,1])
#    eig_2.append(left_evs[:,2])
#    eig_3.append(left_evs[:,3])
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
#
#
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

fields = fields
delta = delta
plt.figure()

plt.title('Frequencies (  )')
plt.xlabel('Fields(T)')
plt.ylabel('Frequency(GHz)')
for i in range(len(lorentz_freqs_2[0])):
    plt.plot(delta,[pt[i] for pt in lorentz_freqs_2],label = 'model mode %s'%(i+1))
#for j in range(len(lorentz_freqs[0])):
#    plt.plot(delta,np.transpose(lorentz_freqs)[j],label = 'all modes index %s'%j )
plt.errorbar(fields,np.asarray(freq2)/1e9,yerr = np.asarray(freq2_err)/1e9,fmt ='o', color = 'tab:orange',label = 'data mode 1')
plt.errorbar(fields,np.asarray(freq1)/1e9,yerr = np.asarray(freq1_err)/1e9,fmt ='o',color = 'tab:blue',label = 'data mode 2')
#for i in range(len(fitting_data)):
#    plt.scatter([0],fitting_data[i], marker = 'o')
plt.ylim(10.7,10.9)
plt.legend()

plt.figure()

plt.title('Linewidth (  )')
plt.xlabel('Fields(T)')
plt.ylabel('Linewidth(MHz)')
for i in range(len(kappa_tot_2[0])):
    plt.plot(delta,[pt[i]*1e3 for pt in kappa_tot_2],label = 'model mode %s'%(i+1))
#for j in range(len(lorentz_freqs[0])):
#    plt.plot(delta,np.transpose(lorentz_freqs)[j],label = 'all modes index %s'%j 
plt.errorbar(fields,np.asarray(kappa_tot2)/1e6,yerr = np.asarray(kappa_tot2_err)/1e6,fmt ='o', color = 'tab:orange',label = 'data mode 1')
plt.errorbar(fields,np.asarray(kappa_tot1)/1e6,yerr = np.asarray(kappa_tot1_err)/1e6,fmt ='o',color = 'tab:blue',label = 'data mode 2')

#for i in range(len(fitting_data)):
#    plt.scatter([0],fitting_ktot[i]/1e9, marker = 'o')
plt.legend()

plt.figure()

plt.title('Amplitude (A)')
plt.xlabel('Fields(T)')
plt.ylabel('Amplitude(MHz)')
for i in range(len(kappa_prod_2[0])):
    if i == 1:
        plt.plot(delta,[(pt[i]) for pt in (3*np.asarray(kappa_prod_2)*1e3)],label = '3*model mode %s'%(i+1))
    else:
        plt.plot(delta,[(pt[i]) for pt in (np.asarray(kappa_prod_2)*1e3)],label = 'model mode %s'%(i+1))
plt.errorbar(fields,3*(np.asarray(kappa_prod2)/1e6),yerr = (np.asarray(kappa_prod2_err)/1e6),fmt ='o', color = 'tab:orange',label = '3*data mode 1')
plt.errorbar(fields,(np.asarray(kappa_prod1)/1e6),yerr = (np.asarray(kappa_prod1_err)/1e6),fmt ='o',color = 'tab:blue',label = 'data mode 2')
#plt.ylim((0,.8))
#for i in range(len(fitting_data)):
#    plt.scatter([0],fitting_kprod[i]**.5/1e9, marker = 'o')
plt.legend()







