import matplotlib
matplotlib.interactive(True)


import lmfit
import numpy as np
import matplotlib.pyplot as pl
import os
filename = 'S11_V5'
print filename

newpath = r'C:\Users\Wang_Lab\Documents\yingying\FMR\copper_cavity_input_coupling_test\%s.txt'%(filename)
newpath2 = r'C:\Users\Wang_Lab\Documents\yingying\FMR\copper_cavity_input_coupling_test\%s_cal_sub.txt'%(filename)
if not os.path.exists(os.path.dirname(newpath)):

    os.makedirs(os.path.dirname(newpath))
new_data = np.loadtxt (newpath,delimiter=",")
new_data = np.transpose(new_data)
x = new_data[0]
y = new_data[1]
phase = new_data[2]
#x = x * 1000000000 
#y = np.power(10,y/20.0)
#x = np.array(range(30))
#y= np.sin (10*x)+ 0.1*np.sin(100*x)
fig, axs = pl.subplots(nrows=2, ncols=2, sharex=True)
fig.subplots_adjust()
fig.suptitle('subtract sin wave for %s'%(filename))
ax = axs[0,0]
ax.set_ylabel('dB')
ax.plot(x,y)
#pl.figure()
#pl.plot(x, y)
#pl.xlabel('frequency(GHZ)')
#pl.ylabel('dB')
#pl.show()
if 1:#if there are some jumps between -180 to 180
    for i in range(len(phase)):
        if phase[i] >100:
            phase[i] = phase[i] - 360
    
def fitsin(params, x, y):

    est =params['offset'] + params['amp']* np.sin(params['freq'] * x + params['phase']) +params['slope'] * x
#    + params['amp2']* np.sin(params['freq2'] * x + params['phase2'])
    return y - est
    
params = lmfit.Parameters()
params.add('amp', value=0.1)
params.add('freq', value=220)
params.add('offset', value=-0.6)
params.add('phase', value=0)
params.add('slope',value=0.05)
#params.add('amp2', value=0.1, min = 0)
#params.add('freq2', value=20)
#params.add('phase2', value=0)
x1 = x[0:600]
x1= np.concatenate([x1,x[1000:1600]])
y1 = y[0:600]
y1= np.concatenate([y1,y[1000:1600]])

result = lmfit.minimize(fitsin, params, args=(x1, y1))
lmfit.report_fit(result.params)
ysin=y - fitsin(result.params, x, y)
ax.plot(x, ysin,'--')
#pl.xlabel('frequency(GHZ)')
#pl.ylabel('dB')
#pl.show()
#pl.legend()

newy= np.array( fitsin(result.params, x, y))
ax = axs[0,1]
ax.plot(x, newy)
#pl.show()
#pl.legend()


params['amp'].value = 1  
params['freq'].value = 220 
params['offset'].value = 1 
params['phase'].value = 0 
params['slope'].value = -100   

x2 = x[0:600]
x2= np.concatenate([x2,x[1000:1600]])
y2 = phase[0:600]
y2= np.concatenate([y2,phase[1000:1600]])

result = lmfit.minimize(fitsin, params, args=(x2, y2))
lmfit.report_fit(result.params)
phase1=phase - fitsin(result.params, x, phase)

ax = axs[1,0]
ax.set_xlabel('frequency(GHZ)')
ax.set_ylabel('deg.')
ax.plot(x,phase)
ax.plot(x, phase1,'--')
#pl.xlabel('frequency(GHZ)')
#pl.ylabel('phase')
#pl.show()
#pl.legend()

ax = axs[1,1]
ax.set_xlabel('frequency(GHZ)')
phase2 = fitsin(result.params, x, phase)
ax.plot(x, phase2)



phase_rad = phase2 * 2 * np.pi /float(360)
x= x[:,None].T
newy =newy[:,None].T
phase_rad = phase_rad[:,None].T
trace = np.concatenate([x,newy,phase_rad]).T
np.savetxt(newpath2 , trace , delimiter=",")

#pl.figure(2)
#x = x * 1000000000 
#acty = np.power(10,newy/20.0)
#pl.plot(x, acty)
#pl.show()