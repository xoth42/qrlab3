# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 17:34:58 2020

@author: Wang_Lab
"""

import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as pl
from matplotlib import gridspec
import lmfit
import os
#fields = lin_power
#j = 0
#fields = np.linspace(0, 0.05,26)
 
#H = np.array([[wa,0,ga,ga2],
#              [0,wb,-gb,gb2],
#              [ga,-gb,wp,1j*delta[i]*k+spl],
#              [ga2,gb2,-1j*delta[i]*k+spl, wn]]) 

def TwoModesFitting(params, fields, ws):
    wa_p = []
    wb_p = []
    wp_p = []
    for i, field in enumerate(fields):
        wpp = params['wp'] + params['ani_diag']* (1-np.abs(field/params['ani_null_field'])) -1j* params['wpi']/2
        wnn = params['wn'] - params['ani_diag']* (1-np.abs(field/params['ani_null_field'])) -1j* params['wni']/2
        wpn = 1j*field *params['k'] + params['ani_g'] * (1-np.abs(field/params['ani_null_field']))
        wnp = -1j*field *params['k'] + params['ani_g'] * (1-np.abs(field/params['ani_null_field']))
        H = np.array([[params['wa']-1j*params['wai']/2, 0,   params['ga'], params['ga2']], 
                      [0,  params['wb']-1j*params['wbi']/2, -params['ga'], params['ga2']],
                      [params['ga'],-params['ga'],  wpp, wpn],
                      [params['ga2'],params['ga2'], wnp, wnn]])
    
    
    
        e,v =LA.eig(H)
        m = np.argsort(abs(v[0]))
        n = np.argsort(abs(v[1]))
        ind_lst = [0,1,2,3]
        if m[3] == n[3]:
            if abs(e[n[2]] - ws[i]) < abs(e[m[3]] - ws[i]):
                wa_p.append(e[n[2]])
                wb_p.append(e[m[3]])
            else:
                wa_p.append(e[m[3]])
                wb_p.append(e[n[2]])
            ind_lst.remove(m[3])
            ind_lst.remove(n[2])
        else:
            if abs(e[n[3]] - ws[i]) < abs(e[m[3]] - ws[i]):
                wa_p.append(e[n[3]])
                wb_p.append(e[m[3]])
            else:
                wa_p.append(e[m[3]])
                wb_p.append(e[n[3]])
            ind_lst.remove(m[3])
            ind_lst.remove(n[3])
#        wp_p.append(e[np.argmax(abs(v[2]))])
        if e[ind_lst[0]]>e[ind_lst[1]]:
            wp_p.append(e[ind_lst[0]])
        else:
            wp_p.append(e[ind_lst[1]])
        
#        n = np.argmax(v[1])
#        wa_p = 
#        if e[2] > 10.85 or e[3] > 10.85:
#            wb_p.append(min(e[2],e[3]))
#            wa_p.append(max(e[0],e[1]))
#        elif e[2] <10.8 or e[3] <10.8:
#            wb_p.append(min(e[1],e[0]))
#            wa_p.append(max(e[2],e[3]))
#        else:
#            if e[2] < e[3]:
#                wa_p.append(e[2])
#                wb_p.append(e[3])
#            else:
#                wa_p.append(e[3])
#                wb_p.append(e[2])
            
    est1= np.concatenate((np.asarray(wa_p),np.asarray(wb_p),np.asarray(wp_p)[0:6]))
    est = np.concatenate((np.real(est1),-np.imag(est1)))
#    est = np.real(est1)
    off = np.abs(ws - est)
#    print off
#    off[len(off)/2:] = off[len(off)/2:]
#    off[:len(off)/2] = off[:len(off)/2]
    off[52:58] = off[52:58]*.05
    off[110:] = off[110:]*.05
    
    return off



params = lmfit.Parameters()
vary_params = False
params.add('wa', value=10.8104, vary = False, min = 10.809, max = 10.815)
params.add('wb', value=10.804, vary = False, min = 10.80, max = 10.809)
params.add('wai', value=0.00015, vary = False)
params.add('wbi', value=0.00100, vary = False)
params.add('wp', value=10.72, vary = False, min = 10, max= 10.8 )#,vary = False)
params.add('wn', value=10.85, vary = False ,min = 10.2, max = 10.9)#,max= 11.5,min = 10.9)
params.add('wni', value=0.36, min = 0, vary = False)
params.add('ga', value=0.02, max = .03, vary = False)
#params.add('gb', value=0.02)
params.add('ga2', value=0.008, max = .02, vary = False)
#params.add('gb2', value=0.008)

params.add('ani_diag', value=0.07, vary= False)
params.add('ani_g', value=0.08, vary=False)
params.add('ani_null_field', value=0.07, vary=False)

#params.add('g',value = 0.030, vary = vary_params)

params.add('k', value = 8, vary = False)
params.add('wpi', value=0.002, vary = False)#,vary = False)
params.add('slp',value = 0, vary = False)


#omega_c = freq1[0]
#omega_c2 = freq2[0]
#omega_c_err =  freq1_err[0]
#omega_c2_err =  freq2_err[0]

#data = np.concatenate((omega_c/1e9, omega_c2/1e9,kappa_a/1e9,kappa_a2/1e9))
#data = np.concatenate((freq1[0], freq2[0]))

#data = np.loadtxt('C:\Users\Wang_Lab\Documents\yingying\cavity freqs and kappas.txt')
#data = np.loadtxt('C:\Users\WangLab\Documents\yingying\\0317cooldown_cavity freqs and kappas.txt')
#data = np.loadtxt('C:\Users\WangLab\Documents\yingying\\0317cooldown_S21 cavity freqs and kappas.txt')

#data = np.loadtxt('C:\Users\Wang_Lab\Documents\yingying\\0626_cooldown_circulator_data\\cavity freqs and kappas.txt')
#
#data = data*1e9
#
#bad_data_i = 0
#bad_data_f = 0
#fields = np.linspace(0, -0.05,26)
#omega_c = data[bad_data_i:len(data)/4 - bad_data_f]
#omega_c2 = data[len(data)/4 +bad_data_i:len(data)/2-bad_data_f]
#kappa_a = data[len(data)/2 +bad_data_i:len(data)*3/4-bad_data_f]
#kappa_a2 = data[len(data)*3/4 +bad_data_i:len(data)-bad_data_f]
data_txt = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210109_232841\\results.txt')
data_txt = np.transpose(data_txt)


omega_c = data_txt[1]
freq1_err = data_txt[2]
omega_c2 = data_txt[3]
freq2_err = data_txt[4]
kappa_a = data_txt[5]
kappa_tot1_err = data_txt[6]
kappa_a2 = data_txt[7]
kappa_tot2_err = data_txt[8]
kappa_prod1 = data_txt[9]
kappa_prod1_err = data_txt[10]
kappa_prod2 = data_txt[11]
kappa_prod2_err = data_txt[12]
phi21 = data_txt[13]
phi21_err = data_txt[14]
fields = np.linspace(0, -0.05,26)  

data_txt3 = np.loadtxt('C:\\Users\\WangLab\\Documents\\circulator results\\20210111_163703\\three_mode_results.txt')
data_txt3 = np.transpose(data_txt3)
omega_c3 = data_txt3[1]
freq1_err3 = data_txt3[2]
omega_c23 = data_txt3[3]
freq2_err3 = data_txt3[4]
omega_c33 = data_txt3[5]
freq3_err3 = data_txt3[6]
kappa_a3 = data_txt3[7]
kappa_tot1_err3 = data_txt3[8]
kappa_a23 = data_txt3[9]
kappa_tot2_err3 = data_txt3[10]
kappa_a33 = data_txt3[11]
kappa_tot3_err3 = data_txt3[12]
kappa_prod13 = data_txt3[13]
kappa_prod1_err3 = data_txt3[14]
kappa_prod23 = data_txt3[15]
kappa_prod2_err3 = data_txt3[16]
kappa_prod33 = data_txt3[17]
kappa_prod3_err3 = data_txt3[18]
phi213 = data_txt3[19]
phi21_err3 = data_txt3[20]
phi313 = data_txt3[21]
phi31_err3 = data_txt3[22]
fields3 = np.linspace(0, -0.05,26)     
         
data = np.concatenate([omega_c,omega_c2,omega_c23[0:6],kappa_a/2,kappa_a2/2,kappa_a23[0:6]/2])
result = lmfit.minimize(TwoModesFitting, params, args=(fields, data/1e9))
lmfit.report_fit(result.params)

#data = np.concatenate([omega_c,omega_c2])
#result = lmfit.minimize(TwoModesFitting, params, args=(fields, data/1e9))
#lmfit.report_fit(result.params)

#pl.figure()
#pl.errorbar(fields, omega_c/1e9, yerr =omega_c_err/1e9, fmt ='o', label='data')
#pl.errorbar(fields, omega_c2/1e9, yerr =omega_c2_err/1e9, fmt ='o', label='data')
#pl.plot(fields, -TwoModesFitting(result.params, fields, np.zeros(len(data)))[0:len(fields)],label = 'fitting')
#pl.plot(fields, -TwoModesFitting(result.params, fields, np.zeros(len(data)))[len(fields):2*len(fields)],label = 'fitting')
#pl.ylabel('frequency(GHz)')
#pl.legend(loc='upper right')




#pl.figure()
#pl.errorbar(fields, kappa_a/1e9, yerr = kappa_a_err/1e9, fmt ='o', label='kappa_tot data')
#pl.errorbar(fields, kappa_a2/1e9, yerr = kappa_a2_err/1e9, fmt ='o')
#pl.plot(fields, -TwoModesFitting(result.params, fields, np.zeros(len(data)))[2*len(fields):3*len(fields)]/5,label = 'fitting')
#pl.plot(fields, -TwoModesFitting(result.params, fields, np.zeros(len(data)))[3*len(fields):4*len(fields)]/5,label = 'fitting')
#pl.ylabel('linewidth(MHz)')
#pl.legend(loc='upper right')


#
w1 = []
w2 = []
w3 = []
w4 = []

wa_p = []
wb_p = []
wp_p = []

for i,field in enumerate(fields):
    wpp = result.params['wp'].value + result.params['ani_diag'].value* (1-np.abs(field/result.params['ani_null_field'].value)) -1j* result.params['wpi'].value/2
    wnn = result.params['wn'].value - result.params['ani_diag'].value* (1-np.abs(field/result.params['ani_null_field'].value)) -1j* result.params['wni'].value/2
    wpn = 1j*field *result.params['k'].value + result.params['ani_g'].value * (1-np.abs(field/result.params['ani_null_field'].value))
    wnp = -1j*field *result.params['k'].value + result.params['ani_g'].value * (1-np.abs(field/result.params['ani_null_field'].value))
    H = np.array([[result.params['wa'].value-1j*result.params['wai'].value/2, 0,   result.params['ga'].value, result.params['ga2'].value], 
                  [0,  result.params['wb'].value-1j*result.params['wbi'].value/2, -result.params['ga'].value, result.params['ga2'].value],
                  [result.params['ga'].value,-result.params['ga'].value,  wpp, wpn],
                  [result.params['ga2'].value,result.params['ga2'].value, wnp, wnn]])



    e,v =LA.eig(H)
    
    m = np.argsort(abs(v[0]))
    n = np.argsort(abs(v[1]))
    ind_lst = [0,1,2,3]
    if m[3] == n[3]:
        if abs(e[n[2]] - data[i]) < abs(e[m[3]] - data[i]):
            wa_p.append(e[n[2]])
            wb_p.append(e[m[3]])
        else:
            wa_p.append(e[m[3]])
            wb_p.append(e[n[2]])
        ind_lst.remove(m[3])
        ind_lst.remove(n[2])
    else:
        if abs(e[n[3]] - data[i]) < abs(e[m[3]] - data[i]):
            wa_p.append(e[n[3]])
            wb_p.append(e[m[3]])
        else:
            wa_p.append(e[m[3]])
            wb_p.append(e[n[3]])
        ind_lst.remove(m[3])
        ind_lst.remove(n[3])
#    wp_p.append(e[np.argmax(abs(v[2]))])
    if e[ind_lst[0]]>e[ind_lst[1]]:
        wp_p.append(e[ind_lst[0]])
    else:
        wp_p.append(e[ind_lst[1]])
    
    w1.append(e[0])
    w2.append(e[1])
    w3.append(e[2])
    w4.append(e[3])

est1= np.concatenate((np.asarray(wa_p),np.asarray(wb_p),np.asarray(wp_p)[0:6]))
est = np.concatenate((np.real(est1),-np.imag(est1)))

resid = (est - data/1e9)

pl.figure()
pl.title('residual')
pl.plot(fields,resid[0:26], label = 'wa')
pl.plot(fields,resid[26:52], label = 'wb')
pl.plot(fields[0:6],resid[52:58], label = 'wp')
pl.plot(fields,resid[58:84], label = 'ka')
pl.plot(fields,resid[84:110], label = 'kb')
pl.plot(fields[0:6],resid[110:], label = 'kp')

pl.legend()





pl.figure()
#pl.errorbar(fields, omega_c/1e9, yerr =omega_c_err/1e9, fmt ='o', label='data')
#pl.errorbar(fields, omega_c2/1e9, yerr =omega_c2_err/1e9, fmt ='o', label='data')
pl.scatter(fields, data[0:26]/1e9, label='2 mode freq 1')
pl.scatter(fields, data[26:52]/1e9, label = '2 mode freq 2' )
pl.scatter(fields, omega_c3/1e9, label='3 mode freq 1')
pl.scatter(fields, omega_c23/1e9, label = '3 mode freq 2' )
pl.scatter(fields, omega_c33/1e9, label = '3 mode freq 2' )
pl.plot(fields, np.real(w1), label = 'fitting eigenvalue_real')
pl.plot(fields, np.real(w2))
pl.plot(fields, np.real(w3))
pl.plot(fields, np.real(w4))
pl.plot(fields, wa_p, label = 'wa')
pl.plot(fields, wb_p, label = 'wb')
pl.plot(fields, wp_p, label = 'wp')
pl.ylim(10.7,10.9)
#pl.plot(fields, np.real(wa_p), label = 'wa_p')
#pl.plot(fields, np.real(wb_p), label = 'wb_p')

pl.xlabel('fields (T)')
pl.ylabel('GHz')
pl.legend()

pl.figure()
#pl.errorbar(fields, kappa_a/1e9, yerr = kappa_a_err/1e9, fmt ='o', label='kappa_tot data')
#pl.errorbar(fields, kappa_a2/1e9, yerr = kappa_a2_err/1e9, fmt ='o')
pl.scatter(fields, kappa_a/2e9,  label='data_kappa_tot/2')
pl.scatter(fields, kappa_a2/2e9,)
pl.scatter(fields, kappa_a3/2e9, label='3 mode kappa 1')
pl.scatter(fields, kappa_a23/2e9, label = '3 mode kappa 2' )
pl.scatter(fields, kappa_a33/2e9, label = '3 mode kappa 2' )
pl.plot(fields, -np.imag(w1), label = 'fitting eigenvalue_-imag')
pl.plot(fields, -np.imag(w2))
pl.plot(fields,- np.imag(w3))
pl.plot(fields,- np.imag(w4))
pl.xlabel('fields (T)')
pl.ylabel('GHz')
pl.legend()


#x = np.linspace(0,.07)
#pl.figure()
#pl.plot(x,(1-(x/.07)))
#pl.plot(x,np.exp(-x/.05))



'''
k = 12    
wa = 10.7115
wb = 10.711# + 0.0001j

ga = 0.0195
ga2 = ga*0.4
gb = ga
gb2 = ga2



wp =10.619 
wn = 10.9- 1j*0.3
delta = 1

deltalist = np.linspace(-0,0.05,26)


off = []

for war in np.linspace(10.7117,10.7116,1):
    for wbr in np.linspace(10.7108,10.7116,1):
        for wnr in np.linspace(10.88,10.92,1):
            for wni in np.linspace(0.2853,0.26,1):
                for ga in np.linspace(0.01954,0.02,1):
                    for ga2 in np.linspace(0.01253,0.01,1):
                        for k in np.linspace(12,12,1):
                            wa = war - 0.0005051j
                            wb = wbr - 0.002261j
                            gb = ga
                            gb2 = ga2
                            wn = wnr - 1j*wni
                            wa_p =[]
                            wb_p = []
                            wp_p = []
                            wn_p = []
                            va_p =[]
                            vb_p = []
                            vp_p =[]
                            vn_p = []
                            pl.figure()
                            
                            pl.scatter(fields, omega_c/1e9)
                            pl.scatter(fields, omega_c2/1e9)
                            
                            for i, delta in enumerate(deltalist):
                            
                                H = np.array([[wa, 0,   ga, ga2], 
                                              [0,  wb, -gb, gb2],
                                              [ga,-gb,  wp, 1j*delta*k],
                                              [ga2,gb2, -1j*delta*k, wn]])
                                
                                
                                
                                e,v =LA.eig(H)
                            
                            
                            
                                wa_p.append(e[2])
                                wb_p.append(e[3])
                                wp_p.append(e[0])
                                wn_p.append(e[1])
                                va_p.append(v[:,2])
                                vb_p.append(v[:,3])   
                                vp_p.append(v[:,0])
                                vn_p.append(v[:,1])
                                if wa_p[i] - wa_p[0] < wb_p[i] - wa_p[0]:
                                    a = wa_p[i]
                                    wa_p[i] = wb_p[i]
                                    wb_p[i] = a
                                
                    #        print e
                    #        print v
                            off.append(np.sum((np.real(wa_p) - omega_c2/1e9)**2 + (np.real(wb_p) - omega_c/1e9)**2+(-np.imag(wa_p) - kappa_a2/1e9)**2 +(-np.imag(wb_p) - kappa_a/1e9)**2))
                            #pl.figure()
                            #pl.subplot(211)   
                            pl.plot(deltalist,np.real(wa_p))
                            pl.plot(deltalist,np.real(wb_p),label = ' wa = %s, wb = %s,\n wp = %s, wn = %s - %si, \n ga = %s, ga2 = %s,\n k = %s off = %s'%(wa,wb,wp,wn.real,-wn.imag,ga,ga2,k, off[j]))
                            #pl.scatter(deltalist,np.real(wp_p),label = ' mode c')
                            #pl.scatter(deltalist,np.real(wn_p),label = ' mode d')
                            pl.ylim(10.71,10.719)
                            pl.legend()
                            
                            
                            
                            fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\11222019cooldown', 'freq_fitting\%s_%s.png'%(j, off[j]))
                            print j, off[j]
                            fdir = os.path.split(fn)[0]
                            if not os.path.isdir(fdir):
                                os.makedirs(fdir)
                            kwargs = dict()
                            pl.savefig(fn, **kwargs)
                            pl.close()
                            pl.figure()
                            pl.errorbar(lin_power, kappa_a/1e9, yerr = kappa_a_err/1e9, fmt ='o', label='kappa_tot')
                            pl.errorbar(lin_power, kappa_a2/1e9, yerr = kappa_a2_err/1e9, fmt ='o')
                            
                            pl.plot(deltalist,-np.imag(wb_p),label = 'imag\n mode a')
                            pl.plot(deltalist,-np.imag(wa_p),label = ' mode b') 
                            pl.legend()
                            fn = os.path.join(r'C:\Users\Wang_Lab\Documents\yingying\11222019cooldown', 'freq_fitting\%s_kappa_%s.png'%(j, off[j]))
                            fdir = os.path.split(fn)[0]
                            if not os.path.isdir(fdir):
                                os.makedirs(fdir)
                            kwargs = dict()
                            pl.savefig(fn, **kwargs)
                            pl.close()
                            j = j + 1
        
        
print 'min', np.argmin(off), np.min(off)

pl.figure()
pl.plot(off)
#pl.legend()
#pl.subplot(212) 
#pl.scatter(deltalist,np.imag(wa_p),label = 'imag\n mode a')
#pl.scatter(deltalist,np.imag(wb_p),label = ' mode b')
#pl.scatter(deltalist,np.imag(w3),label = ' mode c')
#pl.scatter(deltalist,np.imag(w4),label = ' mode d')
##pl.ylim(-0.008,0.008)
#pl.legend() 
#
#va_p = np.asarray(va_p)
#vb_p = np.asarray(vb_p)
#vc_p = np.asarray(vc_p)
#vd_p = np.asarray(vd_p)


#pl.figure()
#pl.errorbar(lin_power, kappa_a/1e9, yerr = kappa_a_err/1e9, fmt ='o', label='kappa_tot')
#pl.errorbar(lin_power, kappa_a2/1e9, yerr = kappa_a2_err/1e9, fmt ='o')
#
#pl.plot(deltalist,-np.imag(wb_p),label = 'imag\n mode a')
#pl.plot(deltalist,-np.imag(wa_p),label = ' mode b') 
#pl.plot(deltalist,-np.imag(wb_p)+0.0012,label = 'imag\n mode a')
#pl.plot(deltalist,-np.imag(wa_p)+0.0012,label = ' mode b') 
'''