# -*- coding: utf-8 -*-
"""
Created on Mon Nov 05 21:19:40 2018

@author: WangLab
"""
import matplotlib
matplotlib.interactive(True)

import lmfit
import re
import numpy as np
import matplotlib.pyplot as pl
import glob


#pl.figure()
def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    est = est + params['roff'] + 1j*params['ioff']
    est = est * np.exp(1j*params['phi'])
    
    return np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
#    np.abs(y)-np.abs(est)
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real - est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
#foldername = 'bandwidth2'    
foldername = 'mode1 0dB'
#foldername = '0.25T in fridge\\330'
filepath = 'C:\Users\Wang_Lab\Documents\\yingying\\11212018cooldown\\T sweep\\%s'%(foldername) 
#filepath = 'C:\Users\Wang_Lab\Documents\\yingying\\FMR\\power sweep 220 mode' 
filelist = glob.glob(r'%s\\*.txt'%(filepath))
#pl.title('temperature dependence')
line=np.empty(len(filelist))
temp=np.empty(len(filelist))
#line1=np.empty(len(filelist))
#temp1=np.empty(len(filelist))
err=np.empty(len(filelist))
feq=np.empty(len(filelist))
ferr=np.empty(len(filelist))
ioff=np.empty(len(filelist))
roff=np.empty(len(filelist))
i=0
#print filelist
for filename in filelist:
# Read the array from file
#    if filename[95]!=filename[96]:
            print '\n'
            print filename
        
            new_data = np.loadtxt(filename,delimiter=",")
            new_data = np.transpose(new_data)
#            print('\n')
#            print(filename)
            
            #new_data = np.loadtxt(filename,delimiter=",")
#            new_data = get_trace(m)
#            new_data = np.transpose(new_data)
            x = new_data[0]
            if x[-1]<20:
                x = x*1e9
            y = new_data[1] 
            phase2 = new_data[2]
    
#            x = x * 1000000000
            #x = x * 1000000
            
#            f1 = k*(m-m_h) + f_min
#            f2 = k*(m-m_l) + f_min
#            start = (f1-f_min)/(f_max-f_min)*(f_points-1)
#            if start < 0:
#                start = 0
#
#            stop = (f2-f_min)/(f_max-f_min)*(f_points-1)
#            if stop > f_points-1:
#                stop = f_points-1
#            x0=x[int(start):int(stop)]
#            y0=y[int(start):int(stop)]
#            phase0=phase2[int(start):int(stop)]
#                          
#            omega_c = x0[np.argmax(y0)]
#            f1 = omega_c - 0.01
#            f2 = omega_c + 0.01
#            start = (f1-f_min)/(f_max-f_min)*(f_points-1)
#            if start < 0:
#                start = 0
#
#            stop = (f2-f_min)/(f_max-f_min)*(f_points-1)
#            if stop > f_points-1:
#                stop = f_points-1
#            x=x[int(start):int(stop)]
#            y=y[int(start):int(stop)]
#            phase2=phase2[int(start):int(stop)]
            
#            x = x * 1000000000            
            
            y = np.power(10,y/20.0)
            y = y * np.exp(-1j*phase2*np.pi/180)

#            x = x[int(1600*0.3):int(1600*0.7)]   
#            y = y[int(1600*0.3):int(1600*0.7)]  
    

    
#            y = y * np.exp(-1j*phase2)
            
            params = lmfit.Parameters()
            params.add('kappa_prod', value= 2e4, min = 0)
            params.add('omega_c', value=x[np.argmax(y)]-1e5)
            params.add('kappa_a', value=2.5e6, min = 0)
            params.add('roff',value = -1e-5)
            params.add('ioff',value = -5e-5)
            params.add('phi',value = 2.84, max = np.pi, min = -np.pi)
            
        
            result = lmfit.minimize(S21, params, args=(x, y))
        
#            lmfit.report_fit(result.params)
    
            y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 ) + result.params['roff'].value + 1j*result.params['ioff'].value
            y1 = y1 * np.exp(1j*result.params['phi'].value)
            #            *(1-result.params['Asym'].value*(x-result.params['omega_c'].value)/(result.params['kappa_a'].value/2.0))
            digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", filename)
#            print digit
            temp[i] = digit[-1]
           # temp[i] = temp[i]*1000            
            pl.figure(temp[i])
            pl.subplot(121)
            pl.plot(x,np.abs(y))
            pl.plot(x, np.abs(y1),'--')
#            pl.suptitle('fitting for %s'%(foldername))
            pl.subplot(122)
#            pl.plot(x,phase2)

            pl.plot(np.real(y), np.imag(y))
            pl.ylabel('Q')
            pl.xlabel('I')
    
            pl.plot(np.real(y1), np.imag(y1),'--,'r'')
#            pl.xlabel('I')
#            pl.legend()

    
            
            line[i] = result.params['kappa_a'].value/float(1000000)
            err[i]= (result.params['kappa_a'].stderr)/float(1000000)
            feq[i] = result.params['omega_c'].value/float(1000000000)
            ferr[i]=result.params['omega_c'].stderr/float(1000000000)
#            totalQ[i] = (result.params['omega_c'].value/line[i]/float(1000000))
            roff[i] = result.params['roff'].value
            ioff[i] = result.params['ioff'].value    
            i = i + 1
    
    
    
pl.figure()
pl.errorbar(temp,line,yerr=err,fmt='o',label='kappa_a')
if foldername == 'mode1 0dB':
    pl.errorbar(300,1.70,yerr=1.70*0.0036,fmt='o',color = 'b')
if foldername == 'mode1 -35dB':
    pl.errorbar(300,1.71,yerr=1.71*0.0157,fmt='o',color = 'b')

#    pl.scatter(temp,line,label='kappa_a')
#    pl.scatter(temp,linei,label='kappa_internal')
#    pl.scatter(temp,linec,label='kappa_coupling')
pl.legend()
#pl.xlabel('span')
#pl.xlabel('T(mK)')
pl.xscale('log')
#pl.title('Mode %s'%M)
pl.ylabel('linewidth(MHz)')
#pl.xlabel('Magnetic Field')
pl.savefig('%s\linwidth.png'%(filepath))
result = [temp,line,err]
#np.savetxt('%s\linwidth'%(filepath), result , delimiter=",")
#line[13] = line[12]
#line[60] = line[59]
print np.average(line[0:10])
print np.average(line[10:20])



pl.figure()
pl.errorbar(temp,feq,yerr=ferr,fmt='o')
#pl.xlabel('span')
#pl.xlabel('T(mK)')
#pl.xscale('log')
pl.ylabel('frequency(GHz)')
pl.xlabel('Magnetic Field')
#pl.savefig('%s\\frequency.jpg'%(filepath))
#pl.title('Mode %s'%M)

#pl.figure()
#pl.scatter(temp,totalQ)
#pl.ylabel('Total Q')
#pl.xlabel('Magnetic Field')
##pl.title('Mode %s'%M)
#pl.savefig('%s\total Q.jpg'%(filepath))