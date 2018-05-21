import matplotlib.pyplot as plt
import numpy as np
import re

import lmfit

from numpy import NaN, Inf, arange, isscalar, asarray, array

 # fitting the modulated data



def dem_decay(params, x, data):
    est = params['ofs'] + params['amplitude'] * np.exp(-(x - start_fitting) /( 2*params['tau'].value))
    return data - est

#freq_list = [8.454e9]
#for freq in freq_list:
#
#start_freq = 8.423e9
#stop_freq = 8.428e9
#num = 1          
#freq_list = np.linspace(start_freq, stop_freq, num)
#
#for freq in freq_list:
filename = 'C:\qrlab\YIG_measurement\RT FMR four\decay_graph_05012018_1.5mm_-22.0dB_281.6mT__8.0892 GHz_20000000_-22.0dB'
data_decay1 = np.loadtxt(r'%s.txt'%(filename), delimiter=",")
print data_decay1.shape

digit = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", filename)
#[float(s) for s in filename.split('_'or' ') if s.isdigit()]
print digit
print 'OK'
start_fitting = 1140
mag = float(digit[3])
freq = float(digit[4])*1e9

n=10# number of average traces

if int(digit[5])<=2000000:
        n=1
        data2 = data_decay1.reshape(2,data_decay1.shape[0]/2)
        data_real = data2[0]
        data_imag = data2[1]
        
        
        
        #buf = data_real[0]+1j*data_imag[0]
        buf = data_real+1j*data_imag
        buf = buf[:,None].T
        
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

#plt.legend()

plt.figure()
plt.title('Demodulated data')
timex = 20*np.array(range(96))
#        timex = timex[:,None].T
#        plt.subplot(211)
#        plt.plot(timex[0], np.real(buf[0]), label='Iraw')
#        plt.plot(timex[0], np.imag(buf[0]), label='Qraw ')
#plt.plot(timex, amp,label='number of averages = %s \n magnetic field = %s mT \n frequency = %s GHz'%(n, mag, freq/1e9))
#plt.plot(timex, amp,label='magnetic field = %s mT \n frequency = %s GHz'%(mag, freq/1e9))
plt.plot(timex, I, label = 'I')
plt.plot(timex, Q, label = 'Q')
A = np.sqrt(I**2 +Q**2)
plt.plot(timex, A, marker = 's',label = 'A from I and Q')            


plt.xlabel('time ns')
plt.legend()
params = lmfit.Parameters()
params.add('ofs', value=np.min(A))
params.add('amplitude', value=np.max(A))
params.add('tau', value=40, min=5.0)
xs = timex[start_fitting/20:240]
ys = A[start_fitting/20:240]
result = lmfit.minimize(dem_decay, params, args=(xs, ys))
#        lmfit.report_fit(params)
#        result2 = lmfit.minimize(exp_decay, result.params, args=(xs,ys))
lmfit.report_fit(result.params)
#plt.plot(xs,ys-dem_decay(result.params, xs,ys),'--', label='Fit, tau = %.03f +/- %.03f ns'%(result.params['tau'].value,result.params['tau'].stderr))
plt.legend()

#plt.figure()
#plt.plot(I,Q)
#plt.xlabel('I')
#plt.ylabel('Q')
#plt.legend()