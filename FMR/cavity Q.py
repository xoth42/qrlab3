# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 10:20:32 2018

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)

import lmfit
import re
import numpy as np
import matplotlib.pyplot as pl
import csv


#pl.figure()
def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
#    est = est + params['roff'] + 1j*params['ioff']
#    est = est * np.exp(1j*params['phi'])
    return np.abs(y)-np.abs(est)
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real - est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
#filepath = 'C:\Users\WangLab\Documents\yingying\\niobium cavity\\supercon two port simulation V3_1.csv'
filepath ='C:\Users\WangLab\Documents\\yingying\\transition results\\length of pins V2.csv'
#filepath_rad ='C:\Users\WangLab\Documents\\yingying\\transition results\\length of pins rad.csv'
print filepath[50:]
header = csv.reader(open(filepath, 'r')).next()

data = np.genfromtxt(filepath, delimiter=',', skip_header = 2)
data = np.transpose(data)
x=data[0]
f1 = 8.6
f2 = 9.4
n1 = int((f1-np.min(x))/(np.max(x)-np.min(x))*len(x))
n2 = int((f2-np.min(x))/(np.max(x)-np.min(x))*len(x))
x = x * 1e9
x = x[n1:n2]

#header = csv.reader(open(filepath_rad, 'r')).next()
#
#data_rad = np.genfromtxt(filepath_rad, delimiter=',', skip_header = 2)
#data_rad = np.transpose(data_rad)

line=np.empty(len(header)-1)
temp=np.empty(len(header)-1)
#line1=np.empty(len(header)-1))
#temp1=np.empty(len(header)-1)
err=np.empty(len(header)-1)
feq=np.empty(len(header)-1)
ferr=np.empty(len(header)-1)
linei=np.empty(len(header)-1)
linec=np.empty(len(header)-1)
Qtot=np.empty(len(header)-1)
Qi=np.empty(len(header)-1)
Qc=np.empty(len(header)-1)
i=0
#print filelist
pl.figure()

for j in range(len(header))[1:]:
# Read the array from file
#    if filename[95]!=filename[96]:
        print '\n'
        print header[j]

        y = data[j] 
        y = y[n1:n2]
        y = np.power(10,y/20.0)
#        phase = data_rad[j] 
#        phase = phase[n1:n2]
#        y = y*np.exp(1j*phase)
        

#        pl.figure()
#        pl.suptitle('fitting for %s'%(header[j]))
#        pl.subplot(211)
        pl.plot(x, np.abs(y))
        pl.ylabel('intensity')
       
         
        params = lmfit.Parameters()
        params.add('kappa_prod', value= 3e12, min = 0)
        params.add('omega_c', value=x[np.argmax(abs(y))]-1e6)
        params.add('kappa_a', value=22e6, min = 0)
#        params.add('roff',value = 0)
#        params.add('ioff',value = 0)  
#        params.add('phi',value = 0, max = np.pi, min = -np.pi)
        
        result = lmfit.minimize(S21, params, args=(x, y))
    
#        lmfit.report_fit(result.params)
        
        y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )
        
        
#        pl.figure()
        pl.plot(x, np.abs(y1),'--',label = header[j])
        pl.xlabel('frequency')
        pl.legend()
        pl.show() 
#        pl.figure()
#        pl.subplot(121)
#        pl.plot(x,np.abs(y))
#        pl.plot(x, np.abs(y1),'--')
#
#        pl.subplot(122)
#
#        pl.plot(np.real(y), np.imag(y))
#        pl.ylabel('Q')
#        pl.xlabel('I')
#
#        pl.plot(np.real(y1), np.imag(y1),'--,'r'')
##            pl.xlabel('I')
#        pl.legend()
#        pl.subplot(212)
#        pl.plot(x, - phase)
#        pl.plot(x, np.arctan(y1.imag/y1.real),'--')
#        #pl.plot(x, np.arctan(est.imag/est.real),'--')
#        pl.xlabel('frequency')
#        pl.ylabel('phase')
#        pl.legend()

        digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", header[j])
        print digit
        temp[i] = digit[-1]

        
        line[i] = result.params['kappa_a'].value
        err[i]=result.params['kappa_a'].stderr
        feq[i] = result.params['omega_c'].value
        ferr[i]=result.params['omega_c'].stderr
        linec[i] = np.sqrt(result.params['kappa_prod'].value)
        linei[i] = (result.params['kappa_a'].value-2*np.sqrt(result.params['kappa_prod'].value))
        Qtot[i] =  result.params['omega_c'].value/line[i]
        Qc[i] = result.params['omega_c'].value/linec[i]
        Qi[i] = result.params['omega_c'].value/linei[i]
        
        print 'total Q', result.params['omega_c'].value/line[i]
        print 'coupling Q', result.params['omega_c'].value/linec[i]
        print 'freq', result.params['omega_c'].value
        print 'internal Q', result.params['omega_c'].value/linei[i]


    #    pl.suptitle('fitting for %s'%(filename[41:]))
    #    pl.plot(x, np.abs(y))
    #    pl.ylabel('intensity')
    #    lmfit.report_fit(result.params)
    #    pl.plot(x, np.abs(y1),'--')
    #    pl.xlabel('frequency')
    #    pl.legend()
    #    pl.savefig('%s\%sMHz.png'%(filepath,temp[i]))
    #    errpercent[i1]=result.params['tau'].stderr/result.params['tau'].value
        i = i + 1
#print temp

pl.figure()
pl.scatter(temp,Qtot,label='Q total')
pl.scatter(temp,Qc,label='Q couple')
pl.xlabel('gap(mm)')
pl.yscale('log')
pl.legend()
pl.show()



#pl.figure()
#pl.errorbar(temp,line,yerr=err,fmt='o',label='kappa_a')
#pl.ylabel('Hz')
##pl.xscale('log')
##pl.scatter(temp,line,label='kappa_a')
##pl.scatter(temp,linei,label='kappa_internal')
##pl.scatter(temp,linec,label='kappa_coupling')
#pl.legend()

#pl.figure()
#pl.scatter(temp,feq/line*1000,label='Q tot')
##pl.xscale('log')
##pl.scatter(temp,line,label='kappa_a')
##pl.scatter(temp,linei,label='kappa_internal')
##pl.scatter(temp,linec,label='kappa_coupling')
#pl.legend()
#pl.show()
#result = [temp,line,err]
##np.savetxt('%s/result.txt'%(filepath), result , delimiter=",")
