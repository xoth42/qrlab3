import matplotlib
matplotlib.interactive(True)


import lmfit
import numpy as np
import matplotlib.pyplot as pl
# matplotlib.use('WXAgg')


#new_data = np.loadtxt(r'C:\qrlab\FMR\trace_S11_without_cal.txt',delimiter=",")
#new_data = np.transpose(new_data)
#x = new_data[0]
#y = new_data[1]
#x = x * 1000000000 * 2 * np.pi
#y = np.power(10,y/20.0)
#pl.plot(x, y)
#pl.show()
#
##print abs(1+1j)
#def S11(params, x, y):
#
#    est = -1 - 2 * params['kappa_a1'] / (1j*(x-params['omega_c'])-params['kappa_a'] + params['g'] **2 /(1j*(x-params['omega_FMR'])-params['gamma_m']/2.0))
#    return y - abs(est)
#    
#params = lmfit.Parameters()
#params.add('kappa_a1', value=100000)
#params.add('omega_c', value=2 * np.pi*8.504e9)
#params.add('kappa_a', value=13.35*10**6)
#params.add('g',value= 197*10**6)
#params.add('omega_FMR',value = 0)
#params.add('gamma_m', value = 2*10**6 )
#
#result = lmfit.minimize(S11, params, args=(x, y))
#lmfit.report_fit(result.params)
#y=y-S11(result.params, x, y)
##y=10*np.log10(y)
#pl.plot(x, y,'--')
#pl.show()



#with x to be frequency, and fit the trace 
filename = 'S11_V5'
print filename

newpath2 = r'C:\Users\Wang_Lab\Documents\yingying\FMR\copper_cavity_input_coupling_test\%s_cal_sub.txt'%(filename)

new_data = np.loadtxt(newpath2 , delimiter=",")
new_data = np.transpose(new_data)
x = new_data[0]
y = new_data[1]
phase = new_data[2]
x = x * 1000000000 
y = np.power(10,y/20.0)
pl.figure()
pl.suptitle('fitting for %s'%(filename))
pl.subplot(211)
pl.plot(x, y)
pl.ylabel('intensity')
y = y * np.exp(-1j*phase)



def S11(params, x, y):

#    est = -1 - params['kappa_a1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2)
    est = 1 + params['kappa_a1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2)

#    est = est * np.exp(1j*params['phase'])
#    resid = calculate_complex_residual(y-est)
    
    return np.concatenate([y.real - est.real, y.imag - est.imag])
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real + est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)
    
params = lmfit.Parameters()
params.add('kappa_a1', value=1e+06, min = 0)
params.add('omega_c', value=8.49e9)
params.add('kappa_a', value=4e6, min = 0)
#params.add('phase', value=0)

result = lmfit.minimize(S11, params, args=(x, y))
lmfit.report_fit(result.params)
est = 1 + params['kappa_a1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2)
print params['kappa_a1']
y1=1 + result.params['kappa_a1'].value / (1j*(x-result.params['omega_c'].value)-result.params['kappa_a'].value/2)
pl.plot(x, np.abs(y1),'--')
#pl.plot(x, est,'--')
pl.legend()


pl.subplot(212)
pl.plot(x, - phase)
pl.plot(x, np.arctan(y1.imag/y1.real),'--')
#pl.plot(x, np.arctan(est.imag/est.real),'--')
pl.xlabel('frequency')
pl.ylabel('phase')
pl.legend()



#
#print "ok"
#a = np.array(range(1601))
#a=8.4 +  a*0.2/1600
#a = a *10**9
#print "ok"
#est = -1 - 2 * 1.8938e+05 / (1j*(a-8.2221e+09)-1.6390e+08 + 1.7837e+09**2 /(1j*(a)--9.6584e+09/2.0))
#    
#pl.plot(a, abs(est),'--')
#pl.show()

