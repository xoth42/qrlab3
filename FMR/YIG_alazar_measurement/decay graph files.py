import numpy as np
import re

import lmfit

#from numpy import NaN, Inf, arange, isscalar, asarray, array

import matplotlib.pyplot as pl
import glob


def dem_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-(x - start_fitting) /( 2*params['tau'].value))
    return data - est
filepath = 'C:\qrlab-3\YIG_measurement\RT third mode'    
filelist = glob.glob(r'%s\decay*.txt'%(filepath))
#pl.title('temperature dependence')
taulist=np.empty(len(filelist))
temp=np.empty(len(filelist))
#line1=np.empty(len(filelist))
#temp1=np.empty(len(filelist))
err=np.empty(len(filelist))
errpercent=np.empty(len(filelist))
i1=0
for filename in filelist:
# Read the array from file
    print filename
    data_decay1 = np.loadtxt(r'%s'%(filename), delimiter=",")
    print data_decay1.shape
    
    digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", filename)
    #[float(s) for s in filename.split('_'or' ') if s.isdigit()]
    print digit
    print 'OK'
    temp[i1] = digit[2]
#    print i1
#    print temp[i1]
    start_fitting = 1140
    mag = float(digit[3])
    freq = float(digit[4])*1e9
    if int(digit[5])<=2000000:
        n=1
        data2 = data_decay1.reshape(2,data_decay1.shape[0]/2)
        data_real = data2[0]
        data_imag = data2[1]
        
        
        
        #buf = data_real[0]+1j*data_imag[0]
        buf = data_real+1j*data_imag
        buf = buf[:,None].T
        
        amp = np.abs(buf)
        amp = amp[0]
        amp = amp/float(n)
        I = np.real(buf)
        I = I[0]
        I = I / float(n)
        Q = np.imag(buf)
        Q = Q[0]
        Q = Q / float(n)
        #plt.figure()
        #plt.scatter(I,Q)
    if int(digit[5])>2000000:
        n=int(digit[5])/2000000# number of average traces

        data2 = data_decay1.reshape(2,n,data_decay1.shape[0]/2/n)
        data_real = data2[0]
        data_imag = data2[1]
        
        
        
        #buf = data_real[0]+1j*data_imag[0]
        buf = data_real+1j*data_imag
#        buf = buf[:,None].T
        
#        amp = np.abs(buf)
#        amp = amp[0]
#        amp = amp/float(n)
        I = np.real(buf)
        I = I[0]
        I = I / float(n)
        Q = np.imag(buf)
        Q = Q[0]
        Q = Q / float(n)
        #plt.figure()
        #plt.scatter(I,Q)
        for i in range(n-1):
        
        
            buf_new = data_real[i+1]+1j*data_imag[i+1]
    #        buf_new = buf_new[:,None].T
        
#            amp_new = np.abs(buf_new)
##            amp_new = amp_new[0]
#            
#            amp = amp + amp_new/float(n)
            
            
            I_new = np.real(buf_new)
#            I_new = I_new[0]
            
            I = I + I_new/float(n)
            Q_new = np.imag(buf_new)
#            Q_new = Q_new[0]
        #    plt.scatter(I_new,Q_new)
            
            Q = Q + Q_new/float(n)
        #            print i
        
        #plt.legend()
    
#    plt.figure()
#    plt.title('Demodulated data')
    timex = 20*np.array(range(len(I)))
    Ioff = np.average(I[0:7])
    Qoff = np.average(Q[0:7])
    I= I - Ioff
    Q= Q - Qoff
    #        timex = timex[:,None].T
    #        plt.subplot(211)
    #        plt.plot(timex[0], np.real(buf[0]), label='Iraw')
    #        plt.plot(timex[0], np.imag(buf[0]), label='Qraw ')
    #plt.plot(timex, amp,label='number of averages = %s \n magnetic field = %s mT \n frequency = %s GHz'%(n, mag, freq/1e9))
#    plt.plot(timex, amp,label='magnetic field = %s mT \n frequency = %s GHz'%(mag, freq/1e9))
#    plt.plot(timex, I, label = 'I')
#    plt.plot(timex, Q, label = 'Q')
    A = np.sqrt(I**2 +Q**2)
#    plt.plot(timex, A, marker = 's',label = 'A from I and Q')            
    
    
#    plt.xlabel('time ns')
#    plt.legend()

    slope, icp=np.polyfit(I[start_fitting/20:96], Q[start_fitting/20:96], 1)
    #the projection to the fitting line
    pj = I[start_fitting/20:96] + Q[start_fitting/20:96] * slope
    pj = pj/np.sqrt(1+slope**2)

    params = lmfit.Parameters()
    params.add('ofs', value=0)
    params.add('amplitude', value=-1)
    params.add('tau', value=40, min=5.0)
    xs = timex[start_fitting/20:96]
    ys =A[start_fitting/20:96]
    result = lmfit.minimize(dem_decay, params, args=(xs, ys))
    #        lmfit.report_fit(params)
    #        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
#    lmfit.report_fit(result.params)
#    plt.plot(xs,ys-dem_decay(result.params, xs,ys),'--', label='Fit, tau = %.03f +/- %.03f ns'%(result.params['tau'].value,result.params['tau'].stderr))
#    plt.legend()
    
#    lmfit.report_fit(result.params)
    taulist[i1] = result.params['tau'].value
    
    
    
    if temp[i1] == 100:
        pl.figure()
        pl.suptitle('fitting for %s'%(filename))
        pl.plot(timex, I,label='I')
        pl.plot(timex, Q,label='Q')
        
        pl.plot(timex, A,label='A')
        pl.plot(xs, pj, marker='s',label='projection')
        pl.ylabel('intensity')
        lmfit.report_fit(result.params)
        y1= result.params['ofs'].value + result.params['amplitude'].value * np.exp(-(xs - start_fitting) /( 2*result.params['tau'].value))
        pl.plot(xs, y1,'--',label='Fit, tau = %.03f +/- %.03f ns'%(result.params['tau'].value,result.params['tau'].stderr))
        pl.xlabel('time')
        pl.legend()
        pl.figure()
        pl.plot(I,Q)
        pl.xlabel('I')
        pl.ylabel('Q')
#        slope = Q[start_fitting/20]/I[start_fitting/20]
        pl.plot(I[start_fitting/20:96],slope*I[start_fitting/20:96]+icp)
        pl.legend()
        

    #fitting with log scale
#    taulist[i1],icp=slope, icp=np.polyfit(timex[start_fitting/20:96], np.log(A[start_fitting/20:96]), 1)
#    taulist[i1] = -0.5/taulist[i1]
    
    pl.figure()
#    pl.plot(timex,np.log(A),marker='s')
#    pl.plot(timex[start_fitting/20:96],(-0.5/taulist[i1])*timex[start_fitting/20:96]+icp,'--',label='fitting tau: %.03f'%(taulist[i1]))
    pl.plot(I,Q)
    pl.plot(I[start_fitting/20:96],Q[start_fitting/20:96])
    pl.xlabel('I')
    pl.ylabel('Q')
    pl.legend()
    pl.savefig('%s\IQ %sdB.jpg'%(filepath,temp[i1]))
    err[i1]=result.params['tau'].stderr
#    errpercent[i1]=result.params['tau'].stderr/result.params['tau'].value
    i1=i1+1
#print temp
pl.figure()
pl.errorbar(temp,taulist,yerr=err,fmt='o')#,label=digit[0])
#pl.scatter(temp, taulist)
pl.xlabel('power')
#pl.xlabel('T(mK)')
#pl.xscale('log')
pl.ylabel('tau')
pl.legend()
pl.savefig(r'%s\tau vs power.jpg'%(filepath))
#pl.figure()
#pl.scatter(temp,errpercent)



        




