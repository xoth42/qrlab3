import lmfit
import re
import numpy as np
import matplotlib.pyplot as pl
import matplotlib
import glob
import os
import datetime
matplotlib.interactive(True)

#filename = 'C:\Users\WangLab\Documents\FMR 11032018\\text_1.5mm_4.0_6.0_0.005_11-3-2018'
filename = 'C:\Users\Wang_Lab\Documents\\yingying\\11212018cooldown\\text_0.246_0.27_0.0002_ave_factor_10'
#filename = 'C:\Users\WangLab\Documents\FMR 11032018\\1.5mm old data\\text_1.5mm_250-340_ANALYZE'
#m_lst = [.64,.68,.72,.76]


'''******'''

m_lst = np.arange(0.25,0.269,0.0002)

#figpath = 'C:\Users\Wang_Lab\Documents\\yingying\\11212018cooldown\\text_0.246_0.27_0.0002_ave_factor_10'
date = datetime.datetime.now()

#figname = '110_0 %s_%s'%(date.hour,date.minute)



#print(m_lst)
#ranges = np.matrix([[8.5,8.65],[8.5,8.7],[8.5,8.7],[8.5,8.75]])



#------------------------------------------------------------------------------------------------------------------------------------------------


'''Display a single plot'''
if 1:
    # Read the array from file
#    filename = 'C:\Users\WangLab\Documents\FMR 11032018\\text_1.5mm_4.0_6.0_0.005_11-3-2018'
    new_data = np.loadtxt('%s.txt'%(filename))
    print(new_data.shape)

    size = new_data.shape[1]
    new_data = new_data.reshape((4,new_data.shape[0]//4,size))
    
    X = new_data[0]
    Y = new_data[1]
    Z = new_data[2]
    phase = new_data[3] 
    
    x=X[0]
    y=Y[:,0] 
#    z0 = Z[:,0]   
    X, Y = np.meshgrid(x,y)
#    X, Z0 = np.meshgrid(x,z0)
    f_min = Y[0][0]
    f_max = Y[-1][0]
    

    pl.figure()
    #pl.suptitle(filename[0:21])
    pl.pcolormesh(X, Y, Z)#,vmin=-90, vmax=-25)
    pl.colorbar()
    pl.xlabel('Magnetic Field')
    pl.ylabel('Frequency (GHZ)')
    
#    f1 = (3.05)+0.01905*x
#    f2 = (3.11)+0.01905*x
#    k = 0.0215
    k = 27
    m_h = 0.245
    m_l = 0.25
    f1 = k*(x-m_h) + f_min 
    f2 = k*(x-m_l) + f_min
    #pl.plot(x,2.99+0.019*x,'r')
    pl.plot(x,f1,'r')
    pl.plot(x,f2,'r')
    pl.ylim(f_min,f_max)
#    pl.xlim(4.9,5.7)
#    pl.xlim(270,290)

    pl.show()
#    pl.savefig('%s\%s_indentify.jpg'%(figpath,figname))
    if m_h<m_l:
        m_t = m_h
        m_h=m_l
        m_l=m_t
    
#------------------------------------------------------------------------------------------------------------------------------------------------
new_data = np.loadtxt('%s.txt'%(filename))
size = new_data.shape[1]
f_points = new_data.shape[0]//4
new_data = new_data.reshape((4,f_points,size))
X = new_data[0]
Y = new_data[1]
Z = new_data[2]
phase = new_data[3] 
#
Z = np.transpose(Z)
Y = np.transpose(Y)
phase = np.transpose(phase)

def get_trace(m):
    i=0
    for i in range(size):
        if X[0][i] < m:
            i = i + 1
        else:
            break

    z = Z[i]
#    z = Z[i] / Z[0]
    phase1 = phase[i]
    freq = Y[0]
    z = z[:,None].T
    freq = freq[:,None].T
    phase1 = phase1[:,None].T
    trace = np.concatenate([freq, z, phase1]).T
    return trace
    
#def fitsin(params, x, y):
#
#    est =params['offset'] + params['amp']* np.sin(params['freq'] * x + params['phase']) +params['slope'] * x
##    + params['amp2']* np.sin(params['freq2'] * x + params['phase2'])
#    return y - est
#    
#params = lmfit.Parameters()
#params.add('amp', value=0.1)
#params.add('freq', value=220)
#params.add('offset', value=-0.6)
#params.add('phase', value=0)
#params.add('slope',value=0.05)

f_min = Y[0][0]
f_max = Y[0][-1]
    
if 1:
    pl.figure()
    def S21(params, x, y):
            est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
            est = est + params['roff'] + 1j*params['ioff']
            est = est * np.exp(1j*params['phi'])
#            est = est*(1-params['Asym']*(x-params['omega_c'])/(params['kappa_a']/2.0) )
            
#            return np.abs(y)-np.abs(est)
            return np.sqrt((y.real-est.real)**2 +(y.imag-est.imag)**2)
            
    line=np.empty(len(m_lst))
    temp=np.empty(len(m_lst))
    #line1=np.empty(len(filelist))
    #temp1=np.empty(len(filelist))
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
    #print filelist
    for m in m_lst:
    
#            print('\n')
#            print(filename)
            
            #new_data = np.loadtxt(filename,delimiter=",")
            new_data = get_trace(m)
            new_data = np.transpose(new_data)
            x = new_data[0] 
            y = new_data[1] 
            phase2 = new_data[2]
    
#            x = x * 1000000000
            #x = x * 1000000
            
            f1 = k*(m-m_h) + f_min
            f2 = k*(m-m_l) + f_min
            start = (f1-f_min)/(f_max-f_min)*(f_points-1)
            if start < 0:
                start = 0

            stop = (f2-f_min)/(f_max-f_min)*(f_points-1)
            if stop > f_points-1:
                stop = f_points-1
            x0=x[int(start):int(stop)]
            y0=y[int(start):int(stop)]
            phase0=phase2[int(start):int(stop)]
                          
            omega_c = x0[np.argmax(y0)]
            f1 = omega_c - 0.003
            f2 = omega_c + 0.003
            start = (f1-f_min)/(f_max-f_min)*(f_points-1)
            if start < 0:
                start = 0

            stop = (f2-f_min)/(f_max-f_min)*(f_points-1)
            if stop > f_points-1:
                stop = f_points-1
            x=x[int(start):int(stop)]
            y=y[int(start):int(stop)]
            phase2=phase2[int(start):int(stop)]
            
            x = x * 1000000000            
            
            y = np.power(10,y/20.0)
            y = y * np.exp(-1j*phase2*np.pi/180)
    

            
            params = lmfit.Parameters()
            params.add('kappa_prod', value= 3e4, min = 0)
            params.add('omega_c', value=omega_c * 1e9)
            params.add('kappa_a', value=2.5e6, min = 0)
            params.add('roff',value = -1e-5)
            params.add('ioff',value = -5e-5)
            params.add('phi',value = 2.88, max = np.pi, min = -np.pi)
            
#            params.add('Asym', value = 0.2)
            
#            if f1 < 10.0:
#                params = lmfit.Parameters()
#                params.add('kappa_prod', value= 3e7, min = 0)
#                params.add('omega_c', value=8.65e9)
#                params.add('kappa_a', value=2e4, min = 0)
#            else:
#                if f1 <11.0:
#                    params = lmfit.Parameters()
#                    params.add('kappa_prod', value= 3e7, min = 0)
#                    params.add('omega_c', value=10.0e9)
#                    params.add('kappa_a', value=2e4, min = 0)
#                else:
#                    params = lmfit.Parameters()
#                    params.add('kappa_prod', value= 3e7, min = 0)
#                    params.add('omega_c', value=11.1e9)
#                    params.add('kappa_a', value=2e4, min = 0)
            
        
            result = lmfit.minimize(S21, params, args=(x, y))
#        
            lmfit.report_fit(result.params)
#    
            y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 ) + result.params['roff'].value + 1j*result.params['ioff'].value
            y1 = y1 * np.exp(1j*result.params['phi'].value)
##            *(1-result.params['Asym'].value*(x-result.params['omega_c'].value)/(result.params['kappa_a'].value/2.0))
#            
#            pl.figure()
#            pl.suptitle('fitting for %s'%(figname))
            pl.subplot(211)
            pl.plot(x, np.abs(y))
            pl.plot(x, np.abs(y1),'--')
            pl.ylabel('intensity')
            
    

            pl.subplot(212)
            pl.plot(np.real(y), np.imag(y))
            pl.ylabel('Q')
            pl.xlabel('I')            
#    #        pl.figure()
            pl.plot(np.real(y1), np.imag(y1),'--')
#
##            pl.xlabel('frequency')
#            pl.legend()
#            
            temp[i] = m_lst[i]
#           # temp[i] = temp[i]*1000
#    
#            
            line[i] = result.params['kappa_a'].value/float(1000000)
            err[i]= (result.params['kappa_a'].stderr)/float(1000000)
            feq[i] = result.params['omega_c'].value/float(1000000000)
#            ferr[i]=result.params['omega_c'].stderr/float(1000000000)
##            linec[i] = np.sqrt(result.params['kappa_prod'].value)/float(1000000)
##            linei[i] = (result.params['kappa_a'].value-2*np.sqrt(result.params['kappa_prod'].value))/float(1000000)
##            print(temp[i],'mT')
##            print('total Q', result.params['omega_c'].value/line[i]/float(1000000))
##            print('coupling Q', result.params['omega_c'].value/linec[i]/float(1000000))
##            print('internal Q', result.params['omega_c'].value/linei[i]/float(1000000))
##            As[i] = result.params['Asym'].value
##            Aserr[i]=result.params['Asym'].stderr
#            roff[i] = result.params['roff'].value
#            ioff[i] = result.params['ioff'].value
#            totalQ[i] = (result.params['omega_c'].value/line[i]/float(1000000))
    
            i = i + 1
    
    
#    pl.savefig('%s\%s_fitting.jpg'%(figpath,figname))
    pl.figure()
    pl.errorbar(temp,line,yerr=err,fmt='o',label='kappa_a')
#    pl.scatter(temp,line,label='kappa_a')
#    pl.scatter(temp,linei,label='kappa_internal')
#    pl.scatter(temp,linec,label='kappa_coupling')
    pl.legend()
    pl.ylim(1,5)
#    #pl.xlabel('span')
#    #pl.xlabel('T(mK)')
#    #pl.xscale('log')
#    #pl.title('Mode %s'%M)
#    pl.ylabel('linewidth(MHz)')
#    pl.xlabel('Magnetic Field')
#    pl.savefig('%s\%s_linwidth.jpg'%(figpath,figname))
#    result = [temp,line,err]
#    np.savetxt('%s\%s_linwidth.txt'%(figpath,figname), result , delimiter=",")
    
#    pl.figure()
#    pl.errorbar(temp, As, yerr = Aserr, fmt ='o', label = 'Antisymmetric factor')
#    pl.savefig('%s\%s_Antisymmetric factor.jpg'%(figpath,figname))
#    pl.legend()

#    feq = feq *1e9
#    pl.figure()
#    pl.scatter(feq, roff, label = 'roff')
#    pl.scatter(feq, ioff, label = 'ioff')
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
#    mi,bi=np.polyfit(feq,ioff,1)
#    pl.plot(feq,mi*feq+bi)    
#    print 'ioff = %s*x + %s'%(mi,bi)
#    pl.figure()
#    pl.errorbar(temp,feq,yerr=ferr,fmt='o')
#    #pl.xlabel('span')
#    #pl.xlabel('T(mK)')
#    #pl.xscale('log')
#    pl.ylabel('frequency(GHz)')
#    pl.xlabel('Magnetic Field')
##    pl.savefig('%s\%s_frequency.jpg'%(figpath,figname))
#    #pl.title('Mode %s'%M)
    
#    pl.figure()
#    pl.scatter(temp,totalQ)
#    pl.ylabel('Total Q')
#    pl.xlabel('Magnetic Field')
#    #pl.title('Mode %s'%M)
#    pl.savefig('%s\%s_total Q.jpg'%(figpath,figname))
    
