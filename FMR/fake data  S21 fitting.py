# -*- coding: utf-8 -*-
"""
Created on Thu Nov 08 19:59:26 2018

@author: WangLab
"""
import numpy as np
import matplotlib.pyplot as pl
import lmfit

kappa_1 = 1e6
kappa_2 = 1e6
omega_c = 8.5e9
kappa_a = 1.5e6
g = 20e6
omega_fmr = 7.5e9
kappa_fmr = 1e6


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


m_lst = np.arange(8.5e9,8.6e9,0.2e9)
span1 = 2e8
span = 30e6

 
    
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
i=0
pl.figure()   
for omega_fmr in m_lst:
    
    x = np.linspace(omega_fmr - span1/2, omega_fmr + span1/2, 101)
    y =np.sqrt(kappa_1 *kappa_2)/(1j*(x-(omega_c))-kappa_a/2 +g**2/(1j*(x-omega_fmr)-kappa_fmr/2))
    print omega_fmr
    print x[np.argmax(abs(y))]
    omega_fmr1 = x[np.argmax(abs(y))]

    x = np.linspace(omega_fmr1 - span/2, omega_fmr1 + span/2,401)
    y = np.sqrt(kappa_1 *kappa_2)/(1j*(x-omega_c)-kappa_a/2 +g**2/(1j*(x-omega_fmr)-kappa_fmr/2))
#    y_bg = np.sqrt(kappa_1 *kappa_2)/(1j*(x-omega_c)-kappa_a/2)
#    y = y - y_bg

      
    #pl.suptitle('fitting for %s'%(foldername))
    
    
    #            y = y * np.exp(-1j*phase2)
    
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 1e11, min = 0)
    params.add('omega_c', value=omega_fmr)
    params.add('kappa_a', value=1.1e6, min = 0)
#    params.add('g', value= 30e6, min = 0)
#    params.add('omega_fmr', value=omega_fmr-4e6)
#    params.add('kappa_fmr', value=1.5e6, min = 0)
    params.add('roff',value = 0)
    params.add('ioff',value = 0)
    params.add('phi',value = 0, max = np.pi, min = -np.pi)

    
    result = lmfit.minimize(S21, params, args=(x, y))
    
    lmfit.report_fit(result.params)
    
    y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0)# + result.params['g'].value**2/(1j *(x-result.params['omega_fmr'].value)-result.params['kappa_fmr'].value/2) )
    y1 = y1 + result.params['roff'].value + 1j*result.params['ioff'].value
#    y1 = y1 * np.exp(1j*result.params['phi'].value)
    #            *(1-result.params['Asym'].value*(x-result.params['omega_c'].value)/(result.params['kappa_a'].value/2.0))
    
#    pl.figure()

    pl.subplot(121)
    pl.plot(x,np.abs(y))
#    pl.plot(x, np.abs(y1),'--')
    
    
    pl.subplot(122)
    pl.plot(y.real,y.imag)
    pl.ylabel('Q')
    pl.xlabel('I')
#    pl.plot(np.real(y1), np.imag(y1),'--')
    pl.legend()
    
    
    

    temp[i] = m_lst[i]
   # temp[i] = temp[i]*1000

    
    line[i] = result.params['kappa_a'].value/float(1000000)
    err[i]= (result.params['kappa_a'].stderr)/float(1000000)
    feq[i] = result.params['omega_c'].value/float(1000000000)
    ferr[i]=result.params['omega_c'].stderr/float(1000000000)
    roff[i] = result.params['roff'].value
    ioff[i] = result.params['ioff'].value
    totalQ[i] = (result.params['omega_c'].value/line[i]/float(1000000))

    i = i + 1
    
    
#pl.figure()
#pl.errorbar(temp,line,yerr=err,fmt='o',label='kappa_a')
#
#pl.legend()
#
#pl.ylabel('linewidth(MHz)')
#pl.xlabel('Magnetic Field')
#print np.average(line)


#
#feq = feq *1e9
#pl.figure()
#pl.scatter(feq, roff, label = 'roff')
#pl.scatter(feq, ioff, label = 'ioff')
##    pl.savefig('%s\%s_roff.jpg'%(figpath,figname))
#    pl.legend()
#    for i in range(len(roff)-1):
#        if np.abs(roff[i+1]-roff[i])>0.0001 or np.abs(ioff[i+1]-ioff[i])>0.0001:
#            roff[i+1] = roff[i]
#            ioff[i+1] = ioff[i]
#    mr,br=np.polyfit(feq,roff,1)
#    pl.plot(feq,mr*feq+br)
#    print 'roff = %s*x + %s'%(mr,br)

#    
    
#pl.figure()
#pl.errorbar(temp,line,yerr=err,fmt='o',label='kappa_a')
#
#pl.legend()
#
#pl.ylabel('linewidth(MHz)')
#pl.xlabel('Magnetic Field')
#print np.average(line)
#
#
#
#feq = feq *1e9
#pl.figure()
#pl.scatter(feq, roff, label = 'roff')
#pl.scatter(feq, ioff, label = 'ioff')
###    pl.savefig('%s\%s_roff.jpg'%(figpath,figname))
##    pl.legend()
##    for i in range(len(roff)-1):
##        if np.abs(roff[i+1]-roff[i])>0.0001 or np.abs(ioff[i+1]-ioff[i])>0.0001:
##            roff[i+1] = roff[i]
##            ioff[i+1] = ioff[i]
##    mr,br=np.polyfit(feq,roff,1)
##    pl.plot(feq,mr*feq+br)
##    print 'roff = %s*x + %s'%(mr,br)
##    
##    mi,bi=np.polyfit(feq,ioff,1)
##    pl.plot(feq,mi*feq+bi)    
##    print 'ioff = %s*x + %s'%(mi,bi)
##pl.figure()
##pl.errorbar(temp,feq,yerr=ferr,fmt='o')
##
##pl.ylabel('frequency(GHz)')
##pl.xlabel('Magnetic Field')
#
#
#pl.figure()
#pl.scatter(temp,totalQ)
#pl.ylabel('Total Q')
#pl.xlabel('Magnetic Field')



#pl.figure()
#pl.scatter(temp,totalQ)
#pl.ylabel('Total Q')
#pl.xlabel('Magnetic Field')

