import matplotlib
matplotlib.interactive(True)


import lmfit
import numpy as np
import matplotlib.pyplot as pl

new_data = np.loadtxt(r'C:\qrlab\FMR\trace_S11_with_cal.txt',delimiter=",")
new_data = np.transpose(new_data)
x = new_data[0]
y = new_data[1]
#x = x * 1000000000 
#y = np.power(10,y/20.0)
#x = np.array(range(30))
#y= np.sin (10*x)+ 0.1*np.sin(100*x)
pl.figure(0)
pl.plot(x, y)
pl.show()
def fitsin(params, x, y):

    est =params['offset'] + params['amp']* np.sin(params['freq'] * x + params['phase'])
#    + params['amp2']* np.sin(params['freq2'] * x + params['phase2'])
    return y - est
    
params = lmfit.Parameters()
params.add('amp', value=0.3)
params.add('freq', value=220)
params.add('offset', value=-9.2)
params.add('phase', value=0)
#params.add('amp2', value=0.1, min = 0)
#params.add('freq2', value=20)
#params.add('phase2', value=0)


result = lmfit.minimize(fitsin, params, args=(x, y))
lmfit.report_fit(result.params)
ysin=y - fitsin(result.params, x, y)
pl.plot(x, ysin,'--')
pl.show()

newy= np.array( fitsin(result.params, x, y))
pl.figure(1)
pl.plot(x, newy,'--')
pl.show()
x= x[:,None].T
newy =newy[:,None].T
trace = np.concatenate([x,newy]).T
np.savetxt(r'trace_cal_sub.txt' , trace , delimiter=",")

#pl.figure(2)
#x = x * 1000000000 
#acty = np.power(10,newy/20.0)
#pl.plot(x, acty)
#pl.show()