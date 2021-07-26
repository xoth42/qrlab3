import lmfit
import numpy as np
import matplotlib
import matplotlib.pyplot as pl

m=0
prod = []
omega = []
a = []
while m<10:
# use kappa_prod and kappa_a instead of kappa 1, 2, int
    new_data = np.loadtxt(r'C:\qrlab-3\FMR\0mT_1mm_trace\%s.txt'%m,delimiter=",")
    new_data = np.transpose(new_data)
    x = new_data[0] 
    y = new_data[1] 
    phase = new_data[2]
    
    ##plotting s21^2 to get the linewidth of the cavity and YIG mode
    #y = np.power(10,y/10.0)
    #pl.plot(x, y)
    
    y = np.power(10,y/20.0)
    
    pl.plot(x, y)
    
    def S21(params, x, y):
        est = np.sqrt(params['kappa_prod'])
        est = est/(1j*(x-params['omega_c'])-(params['kappa_a'])/2.0 )
        return y - abs(est)
        
    params = lmfit.Parameters()
    params.add('kappa_prod', value= 3.007e8, min = 0)
    params.add('omega_c', value= 8.5040e+09)
    params.add('kappa_a', value=3.3771e+06)

    print m
    result = lmfit.minimize(S21, params, args=(x, y))
    lmfit.report_fit(result.params)
    y=y-S21(result.params, x, y)
    prod.append(result.params['kappa_prod'].value)
    omega.append(result.params['omega_c'].value)
    a.append(result.params['kappa_a'].value)
    pl.plot(x, y,'--')
    

    m = m + 1
    
print 'kappa_prod'    
print np.average(prod)
print 'omega_c'
print np.average(omega)
print 'kappa_a'
print np.average(a)