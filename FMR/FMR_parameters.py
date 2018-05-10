import matplotlib
matplotlib.interactive(True)


import lmfit
import numpy as np
import matplotlib
import matplotlib.pyplot as pl
# matplotlib.use('WXAgg')

'''
import matplotlib.pyplot as pl

x = np.array((range(10)))

y = np.array(3.0*np.exp(-x/2))

pl.plot(x, y)

def exp_decay(params, x, data):
    est = params['ofs'] + np.sqrt(params['amplitude'] * np.exp(-x / params['tau'].value) )/1j
    return data - abs(est)
  

params = lmfit.Parameters()
params.add('ofs', value=np.min(y))
params.add('amplitude', value=np.max(y))
params.add('tau', value=x[-1]/2.0)

result = lmfit.minimize(exp_decay, params, args=(x, y))
lmfit.report_fit(result.params)

pl.plot(x, y-exp_decay(result.params, x, y), marker='s')

'''


#new_data = np.loadtxt(r'C:\qrlab\FMR\289.0mT.txt',delimiter=",")
#new_data = np.transpose(new_data)
#x = new_data[0]
#y = new_data[1]
#x = x * 1000000000* 2 * np.pi
#y = np.power(10,y/20.0)
#pl.plot(x, y)
##y = np.power(10,y/10.0)
#print abs(1+1j)
#def S21(params, x, y):
#    est = np.sqrt(params['kappa1']*params['kappa2'])
#    est = est/(1j*(x-params['omega_c'])-(params['kappa1']+params['kappa2']+params['kappa_int'])/2.0 + params['g'] **2 /(1j*(x-params['omega_FMR'])-params['gamma_m']/2.0))
#    return y - abs(est)
#    
#params = lmfit.Parameters()
#params.add('kappa1', value= 1.8967e+06, min = 0)
#params.add('kappa2', value=6258.0129, min = 0)
#params.add('omega_c', value= 2* np.pi*8.504e9)
#params.add('kappa_int', value=1.9316e+07, min = 0)
#params.add('g',value= 295*10**6)
#params.add('omega_FMR',value = 2*np.pi*8.44e9)
#params.add('gamma_m', value = 2e7, min=0)
#
#result = lmfit.minimize(S21, params, args=(x, y))
#lmfit.report_fit(result.params)
#y=y-S21(result.params, x, y)

#pl.plot(x, y,'--')



#with x the frequency

#==============================================================================
# new_data = np.loadtxt(r'C:\qrlab\FMR\290.0mT.txt',delimiter=",")
# new_data = np.transpose(new_data)
# x = new_data[0]
# y = new_data[1]
# x = x * 1000000000
# 
# ##plotting s21^2 to get the linewidth of the cavity and YIG mode
# #y = np.power(10,y/10.0)
# #pl.plot(x, y)
# 
# y = np.power(10,y/20.0)
# pl.plot(x, y)
# 
# print abs(1+1j)
# def S21(params, x, y):
#     est = np.sqrt(params['kappa1']*params['kappa2'])
#     est = est/(1j*(x-params['omega_c'])-(params['kappa1']+params['kappa2']+params['kappa_int'])/2.0 + params['g'] **2 /(1j*(x-params['omega_FMR'])-params['gamma_m']/2.0))
#     return y - abs(est)
#     
# params = lmfit.Parameters()
# params.add('kappa1', value= 2.1305e+05, min = 0)
# params.add('kappa2', value=1664.58721, min = 0)
# params.add('omega_c', value= 8.5040e+09)
# params.add('kappa_int', value=3.0022e+06, min = 0)
# params.add('g',value= 24.75e6)
# params.add('omega_FMR',value = 8.48e9)
# params.add('gamma_m', value = 3e6, min=0)
# 
# result = lmfit.minimize(S21, params, args=(x, y))
# lmfit.report_fit(result.params)
# y=y-S21(result.params, x, y)
# 
# pl.plot(x, y,'--')
# 
# kappa_a = result.params['kappa_int'].value + result.params['kappa1'].value + result.params['kappa2'].value
# print kappa_a
#==============================================================================



# use kappa_prod and kappa_a instead of kappa 1, 2, int

#new_data = np.loadtxt(r'C:\qrlab\FMR\290.0mT.txt',delimiter=",")
#new_data = np.transpose(new_data)
#x = new_data[0]
#y = new_data[1]
#x = x * 1000000000

##plotting s21^2 to get the linewidth of the cavity and YIG mode
#y = np.power(10,y/10.0)
#pl.plot(x, y)

#==============================================================================
# mag = 292.5 #set the magnetic field you want
# new_data = np.loadtxt(r'text_0.5mm_270.0_300.0_0.05.txt')
# size = new_data.shape[1]
# new_data = new_data.reshape((4,1601,size))
# X = new_data[0]
# Y = new_data[1]
# Z = new_data[2]
# 
# Z = np.transpose(Z)
# Y = np.transpose(Y)
# size = new_data.shape[1]
# for i in range(size):
#     if X[0][i] < mag:
#          i = i + 1
#     else:
#         break
#  
#  
# y = Z[i]
#  
# x = Y[0]
# x = x * float(1000000000)
# y = np.power(10,y/20.0)
# pl.figure()
# pl.plot(x, y,label = '%s mT'%(mag))
# 
# 
# def S21(params, x, y):
#     est = np.sqrt(params['kappa_prod'])
#     est = est/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 + params['g'] **2 /(1j*(x-params['omega_FMR'])-params['gamma_m']/2.0))
#     return y - abs(est)
#     
# params = lmfit.Parameters()
# params.add('kappa_prod', value= 3e10, min = 0)
# params.add('omega_c', value= 8.5e9)
# params.add('kappa_a', value=3e6)
# params.add('g',value= 24.75e6, min = 0)
# params.add('omega_FMR',value = 8.48e9)
# params.add('gamma_m', value = 3e6, min=0)
# 
# result = lmfit.minimize(S21, params, args=(x, y))
# lmfit.report_fit(result.params)
# y=y-S21(result.params, x, y)
# 
# pl.plot(x, y,'--')
# pl.legend()
#==============================================================================





def S21(params, x, y):
    est = np.sqrt(params['kappa_prod'])/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
    est = -est
    
    return np.concatenate([y.real - est.real, y.imag - est.imag])
    #np.concatenate([y.real - est.real, y.imag - est.imag])
    #y.real - est.real
    #np.abs(y)-np.abs(est)
    #resid.view(np.float)
    #np.sqrt((y.real - est.real)**2 + (y.imag - est.imag)**2)

#the fitting of 0 magnetic field, with x the frequency


filename = 'S12_fridge_-60dB_V2'
print filename

new_data = np.loadtxt(r'C:\qrlab\FMR\%s.txt'%(filename),delimiter=",")# while using this fitting, make sure that your peak is exactly at the center
new_data = np.transpose(new_data)
x = new_data[0] 
y = new_data[1] 
phase = new_data[2]
#print(min(x), max(x))
#x = x.astype(float)
#print(min(x), max(x))
x = x * 1000000000


##plotting s21^2 to get the linewidth of the cavity
#y = np.power(10,y/10.0)
#pl.plot(x, y)

y = np.power(10,y/20.0)
pl.figure()
pl.suptitle('fitting for %s'%(filename))
pl.subplot(211)
pl.plot(x, y)
pl.ylabel('intensity')

if 1: #if the phase reaches -180
    index_min = np.argmin(phase)
    phase[index_min + 1 : ] = phase[index_min + 1 : ] - 360

phase_ave = np.average(phase)
phase = phase - phase_ave
phase = phase * 2 * np.pi /float(360)   
y = y * np.exp(-1j*phase)

#print abs(1+1j)

 
params = lmfit.Parameters()
params.add('kappa_prod', value= 3.7e10, min = 0)
params.add('omega_c', value=8.512e9)
params.add('kappa_a', value=3e6, min = 0)


result = lmfit.minimize(S21, params, args=(x, y))

lmfit.report_fit(result.params)
y1 = np.sqrt(result.params['kappa_prod'].value)/(1j*(x-result.params['omega_c'].value)-(result.params['kappa_a'].value)/2.0 )


pl.plot(x, np.abs(y1),'--')
pl.xlabel('frequency')
pl.legend()

pl.subplot(212)
pl.plot(x, - phase)
pl.plot(x, np.arctan(y1.imag/y1.real),'--')
#pl.plot(x, np.arctan(est.imag/est.real),'--')
pl.xlabel('frequency')
pl.ylabel('phase')
pl.legend()
#print np.average(phase)
##the fitting of 0 magnetic field
#
#new_data = np.loadtxt(r'C:\qrlab\FMR\trace_S21_per.txt',delimiter=",")
#new_data = np.transpose(new_data)
#x = new_data[0]
#y = new_data[1]
#phase = new_data[2]
#x = x * 1000000000 * 2 * np.pi
#y = np.power(10,y/20.0)
#
#pl.plot(x, y)
##y = np.power(10,y/10.0)
##print abs(1+1j)
#def S21(params, x, y):
#    est = np.sqrt(params['kappa1']*params['kappa2'])
#    est = est/(1j*(x-params['omega_c'])-(params['kappa1']+params['kappa2']+params['kappa_int'])/2.0 )
#    return y - abs(est)
#    
#params = lmfit.Parameters()
#params.add('kappa1', value= 1.8967e+06, vary=False, min = 0)
#params.add('kappa2', value=1e4, min = 0)
#params.add('omega_c', value= 2* np.pi*8.504e9)
#params.add('kappa_int', value=13.35*10**6, min = 0)
#
#
#result = lmfit.minimize(S21, params, args=(x, y))
#lmfit.report_fit(result.params)
#y=y-S21(result.params, x, y)

#pl.plot(x, y,'--')
