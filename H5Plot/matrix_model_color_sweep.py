# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 10:41:05 2020

@author: Wang_Lab
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

wa = 10.811
wb = 10.812
wp = 10.77757
wn = 10.811
ga = .025236
ga2 = -0.0046639
gb = ga
gb2 = ga2
spl = -.06098
A = 0.01
k = 8
gamma1 = 0.0002
gamma2 = 0.0012
gamma4 = .1977

chis = []
wbs = np.linspace(10.8,10.82, 201)
for wb in wbs:
    
    delta = np.linspace(0,.05,26)
    input_port = 1
    output_port = 3
    gamma_list = [gamma1,gamma2,0,gamma4]
    identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
    gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,0,0],[0,0,0,gamma4]])
    
    freqs = np.linspace(10.8,10.84,1601)
    model_data_abs = np.zeros([26,1601])
    model_data_phase = np.zeros([26,1601])
    input_vec = np.matmul((-1j*identity*np.sqrt(gamma)),(identity[input_port].reshape(4,1)))
    for i in range(len(delta)):
        H = np.array([[wa,0,ga,ga2],
                      [0,wb,-gb,gb2],
                      [ga,-gb,wp,1j*delta[i]*k+spl],
                      [ga2,gb2,-1j*delta[i]*k+spl, wn]])  
        H = H - 1j*gamma/2
        for j in range(len(freqs)):
            G = la.inv(freqs[j]*identity-H)
            cav_ops = np.matmul(G,input_vec)
            output = cav_ops[output_port][0]*gamma_list[output_port]
            model_data_abs[i][j] = abs(output)
            model_data_phase[i][j] = np.angle(output)
    model_data_abs = model_data_abs*A
    
#    plt.figure()
#    #plt.plot(freqs,model_data_abs[25])
#    fieldplot, freqplot = np.meshgrid(delta, freqs)
#    plt.pcolormesh(fieldplot, freqplot, 10*np.log10(np.transpose(model_data_abs)), vmax = -10, vmin = -50)
#    plt.colorbar()
 

    delta = np.linspace(0,-.05,101)       
    record = []
    for qubit in [0,-0.0007]:
        wb_1 = wb + qubit
        out_3 = []
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
                          [0,wb_1,-gb,gb2],
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
#        plt.figure()
#        plt.title('top mode')
#        plt.plot(delta,list(eig_cav1_0), label = 'cav 1 part')
#        plt.plot(delta,list(eig_cav1_1), label = 'cav 2 part')
#        plt.plot(delta,list(eig_cav1_2), label = 'mode 3 part')
#        plt.plot(delta,list(eig_cav1_3), label = 'mode 4 part')
#        plt.legend()
#        
#            
#        plt.figure()
#        plt.title('bottom mode')
#        plt.plot(delta,list(eig_cav2_0), label = 'cav 1 part')
#        plt.plot(delta,list(eig_cav2_1), label = 'cav 2 part')
#        plt.plot(delta,list(eig_cav2_2), label = 'mode 3 part')
#        plt.plot(delta,list(eig_cav2_3), label = 'mode 4 part')
#        plt.legend()
        
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
        
#        plt.figure()
#        
#        plt.title('freqs 2')
#        for i in range(len(lorentz_freqs_2[0])):
#            plt.plot(delta,[pt[i] for pt in lorentz_freqs_2],label = 'model index %s'%i)
#        
#        
#        plt.legend()
#        
#        plt.figure()
#        
#        plt.title('kappa_tot 2')
#        for i in range(len(kappa_tot_2[0])):
#            plt.plot(delta,[pt[i] for pt in kappa_tot_2],label = 'model index %s'%i)
#        
#        
#        plt.legend()  
        
        record.append(lorentz_freqs_2)
    
    record = np.asarray(record)
    chi = record[0] - record[1]
    
    plt.figure()
    plt.title('chi')
    for i in range(len(lorentz_freqs_2[0])):
        plt.plot(delta,[pt[i] for pt in chi],label = 'model index %s'%i)    
    print('chi min is %sMHz'%(np.min(chi)*1000))
    chis.append(np.min(chi)*1000)
    
plt.figure()
plt.plot(wbs, chis)
plt.xlabel('wb')
