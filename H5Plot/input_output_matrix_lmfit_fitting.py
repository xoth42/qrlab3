# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:27:51 2021

@author: WangLab
"""

        

import os
import time
import lmfit 


import matplotlib
matplotlib.interactive(True)
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt
import json
from matplotlib import gridspec
import scipy.linalg as la

if 0: # anisotropy model
#    fields = np.linspace(0,0,1)
    limit_for_off = 1
    
    fields = [-.048,.048]
    
    def S31_resid(params,x,y):
    
        wa = params['wa']
        wb = params['wb']
        ga = params['ga']
        ga2 = params['ga2']
        gab_scl = params['gab_scl']
        gb = ga*gab_scl
        gb2 = ga2*gab_scl
        wp = params['wp']
        k = params['k']
        spl = params['spl']
        wn = params['wn']
        gamma1 = params['gamma1']
        gamma2 = params['gamma2']
        gamma3 = 0
        gamma4 = params['gamma4']
        A = params['A']
        phi = params['phi']
        i_off = params['i_off']
        r_off = params['r_off']
        ani_diag = params['ani_diag']
        null_field = params['null_field']
    
        identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
        tot_resid = np.zeros([2,1601])
        for j in range(len(fields)):
            
            out_3 = []
    #        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*fields[i]*k+spl],[ga2,gb2,-1j*fields[i]*k+spl, wn]])  
            # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
            b_in = np.array([1,0,0,0]).reshape(4,1)
            x = x/1e9
            for i in range(len(x)):
                wpp = wp + ani_diag*(1/np.cosh(fields[j]/null_field))
                wnn = wn - ani_diag*(1/np.cosh(fields[j]/null_field))
                wpn = -1j*fields[j]*k+spl*(1/np.cosh(fields[j]/null_field))
                wnp = 1j*fields[j]*k+spl*(1/np.cosh(fields[j]/null_field))
                H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])
                
                big_matrix = (x[i]*identity - H + 1j*gamma/2)
                
                a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
                
                out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
            out_3_ = np.conj(np.asarray(out_3))
        #    if np.max(np.abs(datas)) < limit_for_off:
        #        r_off = (y[0].real+ y[-1].real)/2
        #        i_off = (y[0].imag+ y[-1].imag)/2#, vary = False)
            out_3_ = out_3_ + r_off + 1j*i_off
        
        #    S31_mag = abs(np.array(out_3_))
        #    S31_phase = np.angle(np.array(out_3_))
        #    return np.abs(out_3_ - y)
            tot_resid[j] = np.sqrt((np.real(out_3_)-np.real(y[j]))**2+(np.imag(out_3_)-np.imag(y[j]))**2)
        return tot_resid
            
            
    ''' Path to the .hdf5 file '''
    #filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
    filepath = 'C:\_Data\\'
    #hdf5_name = 'VNAtestJan30.hdf5'
    #hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
    hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'
    
    date = ['20210109','20210110']
    times = ['090240','072113']
    #times = ['225028']
    #fields = [0]
    #time_ = '192458'
    #experiment = 'Power_Sweep_VNA'
    
    #fields = np.linspace(-.05,-.05,1)
    
    #fields = np.linspace(0.05, 0.002,13)
    
    ''' Primary x axis and secondary if 2d'''
    #x_key = 'freqs'
    #x2_key = 'powers'
    data_len = 1601
    
    datas = np.zeros((len(times),data_len),dtype = complex)
    freqs_all = []
    j = 0 #index of the power from the color plot used 0 = lowest power
    
    for i in range(len(times)):
        f = h5.File(filepath + hdf5_name, 'r')
        
        limit_for_off = 1
        k = 0
        #freq1 = np.zeros([nrows,len(fields)])
        #freq2 = np.zeros([nrows,len(fields)])
        #freq1_err = np.zeros([nrows,len(fields)])
        #freq2_err = np.zeros([nrows,len(fields)])  
        r_off = np.zeros(1)
        i_off = np.zeros(1)
        
        title = str(times[i]) + '_Power_Sweep_VNA'
        x_key = 'freqs'
        #x2_key = 'powers'
        exp = f[date[i]][title]
        #    exp = f['/' + date1 + '/' + time + '_' + experiment]
        y_keys = exp.keys()
        #print(y_keys)
        
        #y_keys.remove(x_key)
        #y_keys.remove(x2_key)
        freq = exp['freqs'].value
        freqs_all.append(list(freq))
        #current = exp['currents'].value
        #        powers = exp['powers'].value
        real = exp['realS21'].value
        imag = exp['imaginaryS21'].value
        datas[i] = real[j] + 1j*imag[j] 
    
    
    if np.max(np.abs(datas[0])) < limit_for_off:
        r_off = (datas[0].real+ datas[-1].real)/2
        i_off = (datas[0].imag+ datas[-1].imag)/2#, vary = False)
    
    freqs_all = np.array(freqs_all, dtype = object)
    wa = 10.8104
    wb = 10.804
    ga = .019
    ga2 = .008
    gb = ga
    gb2 = ga2
    wp = 10.72
    k = 9
    spl = .105
    wn = 10.82
    gamma1 = .00015
    gamma2 = .001
    gamma3 = .002
    gamma4 = .6
    A = .23
    phi = -1.4
    i_off = .00061
    r_off = -.00017
    ani_diag = .07
    null_field = .025
    params = lmfit.Parameters()
    fix_vary = False
    params.add('wa', value=10.8104,vary = False)
    params.add('wb', value=10.804, vary = False)
    params.add('ga', value=.019,min = -.04, max = .04, vary = fix_vary)
    params.add('ga2', value=.008, min = -.03, max = .03, vary = fix_vary)
    params.add('wp', value=10.72, min = 10.2, max = 11.0, vary = fix_vary)
    params.add('wn', value=10.82, min = 10.2, max = 11.0, vary = fix_vary)
    params.add('k', value=9.0, min = 7.0, max = 10.0, vary = fix_vary)
    params.add('spl', value=.105, min = .05,max = .15, vary = fix_vary)
    params.add('gamma1', value=.00015, min = .00005,max = .003, vary = fix_vary)
    params.add('gamma2', value=.001, min = .00005,max = .003, vary = fix_vary)
#    params.add('gamma3', value=0, vary = False)
    params.add('gamma4', value=.6, min = .1,max = 1.5, vary = fix_vary)
    params.add('A', value=.23, min = .01, max = 1.0, vary = fix_vary)
    params.add('phi', value=-1.4, min = -3.5,max = 3.5, vary = fix_vary)
    params.add('i_off', value=.00016, min = -.001, max = .001, vary = fix_vary)
    params.add('r_off', value=-.00017, min = -.001, max = .001, vary = fix_vary)
    params.add('ani_diag', value=.07, min = 0.0, max = .15, vary = fix_vary)
    params.add('null_field', value=.025, min = 0.0, max = .2, vary = fix_vary)#,vary = False)
    params.add('gab_scl', value = 1.0, min = .5, max = 2, vary = fix_vary)
    #if np.max(np.abs(datas)) < limit_for_off:
    #    params.add('roff',value =(datas[itime][0].real+ datas[itime][-1].real)/2)#,vary = False)
    #    params.add('ioff',value = (datas[itime][0].imag+ datas[itime][-1].imag)/2)#, vary = False)
    
    
    result = lmfit.minimize(S31_resid, params, args=(freq,datas), method='differential_evolution')
    lmfit.report_fit(result.params)
                                                                        
    param = [result.params['wa'].value,result.params['wb'].value,result.params['ga'].value,result.params['ga2'].value,result.params['wp'].value,result.params['k'].value,result.params['spl'].value,result.params['wn'].value,result.params['gamma1'].value,result.params['gamma2'].value,result.params['gamma4'].value,result.params['A'].value,result.params['phi'].value,result.params['i_off'].value,result.params['r_off'].value,result.params['ani_diag'].value,result.params['null_field'].value,result.params['gab_scl']]                                                                    
    
    def S31_model(param,delta,freq_):
        wa = param[0]
        wb = param[1]
        ga = param[2]
        ga2 = param[3]
        gab_scl = param[17]
        gb = ga*gab_scl
        gb2 = ga2*gab_scl
        wp = param[4]
        k = param[5]
        spl = param[6]
        wn = param[7]
        gamma1 = param[8]
        gamma2 = param[9]
        gamma3 = 0
        gamma4 = param[10]
        A = param[11]
        phi = param[12]
        i_off = param[13]
        r_off = param[14]
        ani_diag = param[15]
        null_field = param[16]
        
        w = freq_/1e9
        identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
        out_3 = []
    #    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
        # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
        b_in = np.array([1,0,0,0]).reshape(4,1)
        for i in range(len(w)):
            wpp = wp + ani_diag*(1/np.cosh(delta/null_field))
            wnn = wn - ani_diag*(1/np.cosh(delta/null_field))
            wpn = -1j*delta*k+spl*(1/np.cosh(delta/null_field))
            wnp = 1j*delta*k+spl*(1/np.cosh(delta/null_field))
            H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])
            
            big_matrix = (w[i]*identity - H + 1j*gamma/2)
            
            a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
            
            out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
        out_3_ = np.conj(out_3)
        out_3_ = out_3_ + r_off + 1j*i_off
        S31_mag = abs(np.array(out_3_))
        S31_phase = np.angle(np.array(out_3_))
        print(out_3[0])
        print(out_3_[0])
        return [out_3_,S31_mag,S31_phase]
    
    
    
    for i in range(len(fields)):
    
        model_data = S31_model(param,fields[i],freqs_all[i])[0]
        
        plt.figure()
        plt.title('Magnitude at field = %s'%(fields[i]))
        
        plt.plot(freqs_all[i],np.abs(datas[i]), label = 'data')
        plt.plot(freqs_all[i],np.abs(model_data),label = 'model')
        plt.legend()
        
        plt.figure()
        plt.title('Phase at field = %s'%(fields[i]))
        
        plt.plot(freqs_all[i],np.angle(datas[i]), label = 'data')
        plt.plot(freqs_all[i],np.angle(model_data),label = 'model')
        plt.legend()
        
        plt.figure()
        plt.title('IQ at field = %s'%(fields[i]))
        plt.plot(np.real(datas[i]),np.imag(datas[i]), label = 'data')
        plt.plot(np.real(model_data),np.imag(model_data),label = 'model')
        plt.legend()
            
        
    str_params = 'wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off,ani_diag,null_field,gab_scl'
    str_params = str_params.split(',')
    for i in range(len(param)):
        print(str_params[i] + ' = ' + str(param[i]))
    
if 1: #isotropic YIG model
    
#    fields = np.linspace(0,0,1)
    limit_for_off = 1
    
    fields = [-.048,.048]
    
    def S31_resid(params,x,y):
    
        wa = params['wa']
        wb = params['wb']
        ga = params['ga']
        ga2 = params['ga2']
        gab_scl = params['gab_scl']
        gb = ga*gab_scl
        gb2 = ga2*gab_scl
        wp = params['wp']
        k = params['k']
        spl = params['spl']
        wn = params['wn']
        gamma1 = params['gamma1']
        gamma2 = params['gamma2']
        gamma3 = 0
        gamma4 = params['gamma4']
        A = params['A']
        phi = params['phi']
        i_off = params['i_off']
        r_off = params['r_off']

    
        identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
        tot_resid = np.zeros([2,1601])
        for j in range(len(fields)):
            
            out_3 = []
    #        H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*fields[i]*k+spl],[ga2,gb2,-1j*fields[i]*k+spl, wn]])  
            # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
            b_in = np.array([1,0,0,0]).reshape(4,1)
            x = x/1e9
            for i in range(len(x)):
                wpp = wp
                wnn = wn
                wpn = 1j*fields[j]*k+spl
                wnp = -1j*fields[j]*k+spl
                H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])
                
                big_matrix = (x[i]*identity - H + 1j*gamma/2)
                
                a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
                
                out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
            out_3_ = np.conj(np.asarray(out_3))
        #    if np.max(np.abs(datas)) < limit_for_off:
        #        r_off = (y[0].real+ y[-1].real)/2
        #        i_off = (y[0].imag+ y[-1].imag)/2#, vary = False)
            out_3_ = out_3_ + r_off + 1j*i_off
        
        #    S31_mag = abs(np.array(out_3_))
        #    S31_phase = np.angle(np.array(out_3_))
        #    return np.abs(out_3_ - y)
            tot_resid[j] = np.sqrt((np.real(out_3_)-np.real(y[j]))**2+(np.imag(out_3_)-np.imag(y[j]))**2)
        return tot_resid
            
            
    ''' Path to the .hdf5 file '''
    #filepath = 'C:\\Users\\WangLab\\Documents\\yingying\\'
    filepath = 'C:\_Data\\'
    #hdf5_name = 'VNAtestJan30.hdf5'
    #hdf5_name = 'YIG_Copper_Cavity_sweep_test.hdf5'
    hdf5_name = '20210105cooldown_circulator_VNA - Copy.hdf5'
    
    date = ['20210109','20210110']
    times = ['090240','072113']
    #times = ['225028']
    #fields = [0]
    #time_ = '192458'
    #experiment = 'Power_Sweep_VNA'
    
    #fields = np.linspace(-.05,-.05,1)
    
    #fields = np.linspace(0.05, 0.002,13)
    
    ''' Primary x axis and secondary if 2d'''
    #x_key = 'freqs'
    #x2_key = 'powers'
    data_len = 1601
    
    datas = np.zeros((len(times),data_len),dtype = complex)
    freqs_all = []
    j = 0 #index of the power from the color plot used 0 = lowest power
    
    for i in range(len(times)):
        f = h5.File(filepath + hdf5_name, 'r')
        
        limit_for_off = 1
        k = 0
        #freq1 = np.zeros([nrows,len(fields)])
        #freq2 = np.zeros([nrows,len(fields)])
        #freq1_err = np.zeros([nrows,len(fields)])
        #freq2_err = np.zeros([nrows,len(fields)])  
        r_off = np.zeros(1)
        i_off = np.zeros(1)
        
        title = str(times[i]) + '_Power_Sweep_VNA'
        x_key = 'freqs'
        #x2_key = 'powers'
        exp = f[date[i]][title]
        #    exp = f['/' + date1 + '/' + time + '_' + experiment]
        y_keys = exp.keys()
        #print(y_keys)
        
        #y_keys.remove(x_key)
        #y_keys.remove(x2_key)
        freq = exp['freqs'].value
        freqs_all.append(list(freq))
        #current = exp['currents'].value
        #        powers = exp['powers'].value
        real = exp['realS21'].value
        imag = exp['imaginaryS21'].value
        datas[i] = real[j] + 1j*imag[j] 
    
    
    if np.max(np.abs(datas[0])) < limit_for_off:
        r_off = (datas[0].real+ datas[-1].real)/2
        i_off = (datas[0].imag+ datas[-1].imag)/2#, vary = False)
    
    freqs_all = np.array(freqs_all, dtype = object)
    wa = 10.8104
    wb = 10.804
    ga = .019
    ga2 = .008
    gb = ga
    gb2 = ga2
    wp = 10.72
    k = 9
    spl = .105
    wn = 10.82
    gamma1 = .00015
    gamma2 = .001
    gamma3 = .002
    gamma4 = .6
    A = .23
    phi = -1.4
    i_off = .00061
    r_off = -.00017
    ani_diag = .07
    null_field = .025
    params = lmfit.Parameters()
    fix_vary = False
    params.add('wa', value=10.8104, min = 10, max = 11, vary = False)
    params.add('wb', value=10.804, min = 10, max = 11, vary = False)
    params.add('ga', value=.019,min = -.04, max = .04, vary = fix_vary)
    params.add('ga2', value=.008, min = -.03, max = .03, vary = fix_vary)
    params.add('wp', value=10.72, min = 10.2, max = 11, vary = fix_vary)
    params.add('wn', value=10.82, min = 10.2, max = 11, vary = fix_vary)
    params.add('k', value=9, min = 7, max = 10, vary = fix_vary)
    params.add('spl', value=.105, min = .05,max = .15, vary = fix_vary)
    params.add('gamma1', value=.00015, min = .00005,max = .003, vary = fix_vary)
    params.add('gamma2', value=.001, min = .00005,max = .003, vary = fix_vary)
    params.add('gamma3', value=0,min = -1, max = 1, vary = fix_vary)
    params.add('gamma4', value=.6, min = .1,max = 1.5, vary = fix_vary)
    params.add('A', value=.23, min = .01, max = 1.5, vary = fix_vary)
    params.add('phi', value=-1.4, min = -3.5,max = 3.5, vary = fix_vary)
    params.add('i_off', value=.00016, min = -.01, max = .01, vary = fix_vary)
    params.add('r_off', value=-.00017, min = -.01, max = .01, vary = fix_vary)
    params.add('gab_scl', value=1, min = .5, max = 2, vary = fix_vary)

    
    
    result = lmfit.minimize(S31_resid, params, args=(freq,datas), method = 'differential_evolution')
    lmfit.report_fit(result.params)
                                                                        
    param = [result.params['wa'].value,result.params['wb'].value,result.params['ga'].value,result.params['ga2'].value,result.params['wp'].value,result.params['k'].value,result.params['spl'].value,result.params['wn'].value,result.params['gamma1'].value,result.params['gamma2'].value,result.params['gamma4'].value,result.params['A'].value,result.params['phi'].value,result.params['i_off'].value,result.params['r_off'].value,result.params['gab_scl']]                                                                    
    
    def S31_model(param,delta,freq_):
        wa = param[0]
        wb = param[1]
        ga = param[2]
        ga2 = param[3]
        gab_scl = param[15]        
        gb = ga*gab_scl
        gb2 = ga2*gab_scl
        wp = param[4]
        k = param[5]
        spl = param[6]
        wn = param[7]
        gamma1 = param[8]
        gamma2 = param[9]
        gamma3 = 0
        gamma4 = param[10]
        A = param[11]
        phi = param[12]
        i_off = param[13]
        r_off = param[14]

        
        w = freq_/1e9
        identity = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
        gamma = np.array([[gamma1,0,0,0],[0,gamma2,0,0],[0,0,gamma3,0],[0,0,0,gamma4]])
        out_3 = []
    #    H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wp,1j*delta*k+spl],[ga2,gb2,-1j*delta*k+spl, wn]])  
        # a vector = [a_a,a_b,a_p,a_n]  ,  b vector = [b_left(1), b_right(2) , 0 , b_upper(3)]
        b_in = np.array([1,0,0,0]).reshape(4,1)
        for i in range(len(w)):
            wpp = wp
            wnn = wn
            wpn = 1j*delta*k+spl
            wnp = -1j*delta*k+spl
            H = np.array([[wa,0,ga,ga2],[0,wb,-gb,gb2],[ga,-gb,wpp,wpn],[ga2,gb2,wnp, wnn]])
            
            big_matrix = (w[i]*identity - H + 1j*gamma/2)
            
            a = -1j*np.matmul(np.matmul(la.inv(big_matrix),np.sqrt(gamma)),b_in)
            
            out_3.append(A*np.exp(-1j*phi)*(np.sqrt(gamma4)*a[3][0]))
        out_3_ = np.conj(out_3)
        out_3_ = out_3_ + r_off + 1j*i_off
        S31_mag = abs(np.array(out_3_))
        S31_phase = np.angle(np.array(out_3_))
        print(out_3[0])
        print(out_3_[0])
        return [out_3_,S31_mag,S31_phase]
    
    
    
    for i in range(len(fields)):
    
        model_data = S31_model(param,fields[i],freqs_all[i])[0]
        
        plt.figure()
        plt.title('Magnitude at field = %s'%(fields[i]))
        
        plt.plot(freqs_all[i],np.abs(datas[i]), label = 'data')
        plt.plot(freqs_all[i],np.abs(model_data),label = 'model')
        plt.legend()
        
        plt.figure()
        plt.title('Phase at field = %s'%(fields[i]))
        
        plt.plot(freqs_all[i],np.angle(datas[i]), label = 'data')
        plt.plot(freqs_all[i],np.angle(model_data),label = 'model')
        plt.legend()
        
        plt.figure()
        plt.title('IQ at field = %s'%(fields[i]))
        plt.plot(np.real(datas[i]),np.imag(datas[i]), label = 'data')
        plt.plot(np.real(model_data),np.imag(model_data),label = 'model')
        plt.legend()
            
        
    str_params = 'wa,wb,ga,ga2,wp,k,spl,wn,gamma1,gamma2,gamma4,A,phi,i_off,r_off,gab_scl'
    str_params = str_params.split(',')
    for i in range(len(param)):
        print(str_params[i] + ' = ' + str(param[i]))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
