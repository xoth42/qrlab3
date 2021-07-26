import matplotlib
matplotlib.interactive(True)


import lmfit
import numpy as np
import matplotlib.pyplot as pl
# matplotlib.use('WXAgg')


#new_data = np.loadtxt(r'C:\qrlab-3\FMR\trace_S11_without_cal.txt',delimiter=",")
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

new_data = np.loadtxt(r'C:\qrlab-3\FMR\trace_cal_sub.txt' , delimiter=",")
new_data = np.transpose(new_data)
x = new_data[0]
y = new_data[1]
x = x * 1000000000 
y = np.power(10,y/20.0)
pl.plot(x, y)
pl.show()



def S11(params, x, y):

    est = -1 - params['kappa_a1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2)
    return y - abs(est)
    
params = lmfit.Parameters()
params.add('kappa_a1', value=2.1305e+05)
params.add('omega_c', value=8.504e9)
params.add('kappa_a', value=3.0022e+06)


result = lmfit.minimize(S11, params, args=(x, y))
lmfit.report_fit(result.params)
y=y-S11(result.params, x, y)
pl.plot(x, y,'--')
pl.show()




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

