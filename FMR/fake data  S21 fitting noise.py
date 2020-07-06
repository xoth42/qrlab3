# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 15:10:29 2019

@author: WangLab
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 08 19:59:26 2018

@author: WangLab
"""
import numpy as np
import matplotlib.pyplot as pl
import lmfit
import cmath


kappa_1 = 1e5
kappa_2 = 1e5
omega_c = 8.5e9
kappa_a = 1.5e6



def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0)# + params['g']**2/(1j *(x-params['omega_fmr'])-params['kappa_fmr']/2))
    est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
#    np.abs(y)-np.abs(est)
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real - est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
#    np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
#x = np.arange(7.5e9, 8.5e9, 0.00001e9)

m_lst = np.random.normal(20)
span1 = 10e6

 
    
line=np.empty(len(m_lst))
temp=np.empty(len(m_lst))
err=np.empty(len(m_lst))
feq=np.empty(len(m_lst))
ferr=np.empty(len(m_lst))
linei=np.empty(len(m_lst))
linec=np.empty(len(m_lst))
totalQ = np.empty(len(m_lst))
#    As = np.empty(len(m_lst))
#    Aserr = np.empty(len(m_lst))
roff = np.empty(len(m_lst))
ioff = np.empty(len(m_lst))

y = np.empty([len(m_lst),1601],dtype = complex)

i=0
pl.figure()   
for i,omega_n in enumerate(m_lst):
    
    x = np.linspace(omega_c - span1/2, omega_c + span1/2, 1601)
    y[i] =np.sqrt(kappa_1 *kappa_2)/(1j*(x-(omega_c + (omega_n-0.5)*1e6))-kappa_a/2)
#    print omega_fmr
#    print x[np.argmin(abs(y))]
#    omega_fmr1 = x[np.argmax(abs(y))]
#    x = np.linspace(omega_fmr1 - span/2, omega_fmr1 + span/2, 101)
#    y = np.sqrt(kappa_1 *kappa_2)/(1j*(x-omega_c)-kappa_a/2 +g**2/(1j*(x-omega_fmr)-kappa_fmr/2))
#    y_bg = np.sqrt(kappa_1 *kappa_2)/(1j*(x-omega_c)-kappa_a/2)
#    y = y - y_bg

      
    #pl.suptitle('fitting for %s'%(foldername))
    
    
    #            y = y * np.exp(-1j*phase2)
    
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 1e11, min = 0)
    params.add('omega_c', value=x[np.argmax(y[i])]*1.0001)
    params.add('kappa_a', value=1.1e6, min = 0)
#    params.add('g', value= 30e6, min = 0)
#    params.add('omega_fmr', value=omega_fmr-4e6)
#    params.add('kappa_fmr', value=1.5e6, min = 0)
    params.add('roff',value = 0)
    params.add('ioff',value = 0)
    params.add('phi',value = 0, max = np.pi, min = -np.pi)

    
    result = lmfit.minimize(S21, params, args=(x, y[i]))
    
    lmfit.report_fit(result.params)
    
    y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0)# + result.params['g'].value**2/(1j *(x-result.params['omega_fmr'].value)-result.params['kappa_fmr'].value/2) )
    y1 = y1 + result.params['roff'].value + 1j*result.params['ioff'].value
#    y1 = y1 * np.exp(1j*result.params['phi'].value)
    #            *(1-result.params['Asym'].value*(x-result.params['omega_c'].value)/(result.params['kappa_a'].value/2.0))
    
#    pl.figure()
    pl.subplot(121)
    pl.plot(x,np.abs(y[i]))
    pl.plot(x, np.abs(y1),'--')
    
    
    pl.subplot(122)
    pl.plot(y[i].real,y[i].imag)
    pl.ylabel('Q')
    pl.xlabel('I')
    pl.plot(np.real(y1), np.imag(y1),'--')
    pl.legend()
#    
#    
#    
#    temp[i] = m_lst[i]
   # temp[i] = temp[i]*1000

    
    line[i] = result.params['kappa_a'].value/float(1000000)
    err[i]= (result.params['kappa_a'].stderr)/float(1000000)
    feq[i] = result.params['omega_c'].value/float(1000000000)
    ferr[i]=result.params['omega_c'].stderr/float(1000000000)
    roff[i] = result.params['roff'].value
    ioff[i] = result.params['ioff'].value
    totalQ[i] = (result.params['omega_c'].value/line[i]/float(1000000))

phase = np.empty(len(y[i]))
for j in range(len(y[i])):
    
    phase[j]= cmath.phase(y[i][j]) 
pl.figure()    
pl.plot(x,phase*180/np.pi, '.')
pl.show()
    

y_ave =y[i] *0.0
for j in range(len(y)):
    y_ave = y_ave + y[j]
y_ave = y_ave/len(y)


params = lmfit.Parameters()
params.add('kappa_prod', value= 1e11, min = 0)
params.add('omega_c', value=x[np.argmax(y_ave)])
params.add('kappa_a', value=1.1e6, min = 0)
#    params.add('g', value= 30e6, min = 0)
#    params.add('omega_fmr', value=omega_fmr-4e6)
#    params.add('kappa_fmr', value=1.5e6, min = 0)
params.add('roff',value = 0)
params.add('ioff',value = 0)
params.add('phi',value = 0, max = np.pi, min = -np.pi)


result = lmfit.minimize(S21, params, args=(x, y_ave))

lmfit.report_fit(result.params)

y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0)# + result.params['g'].value**2/(1j *(x-result.params['omega_fmr'].value)-result.params['kappa_fmr'].value/2) )
y1 = y1 + result.params['roff'].value + 1j*result.params['ioff'].value
y1 = y1 * np.exp(1j*result.params['phi'].value)
#            *(1-result.params['Asym'].value*(x-result.params['omega_c'].value)/(result.params['kappa_a'].value/2.0))

pl.figure()
pl.subplot(121)
pl.plot(x,np.abs(y_ave))
pl.plot(x, np.abs(y1),'--')


pl.subplot(122)
pl.plot(y_ave.real,y_ave.imag)
pl.ylabel('Q')
pl.xlabel('I')
pl.plot(np.real(y1), np.imag(y1),'--')
pl.legend()