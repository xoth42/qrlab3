# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:15:26 2017

@author: WangLab
"""
import numpy as np
import matplotlib.pyplot as pl
#from fitting_programs import *
#from lib.math import fit
from scipy.optimize import leastsq
from sympy.solvers import solve
from sympy import Symbol

data = np.loadtxt("0815_hanger_magshield_cold", unpack=True)
y = data

center_freq = 8.5901166e9
span = 1e5
half_span = span / 2.0
x = np.linspace(-half_span, half_span, 1601)

def lorentzian(x,p):
    numerator = (p[0]**2 )
    denominator = ( x - (p[1]) )**2 + p[0]**2
    y = p[2]*(numerator/denominator)
    return y
    
def residuals(p,y,x):
    err = y - lorentzian(x,p)
    return err
    

ind_bg_low = (x > min(x)) & (x < -30e3)
ind_bg_high = (x > 30e3) & (x < max(x))

x_bg = np.concatenate((x[ind_bg_low],x[ind_bg_high]))
y_bg = np.concatenate((y[ind_bg_low],y[ind_bg_high]))
    
m, c = np.polyfit(x_bg, y_bg, 1)

background = m*x + c
y_bg_corr = y - background
    
p = [3e3,2e3,5]

pbest = leastsq(residuals,p,args=(y_bg_corr,x),full_output=1)
best_parameters = pbest[0]

fit = lorentzian(x,best_parameters)

pl.plot(x,y_bg_corr,'wo')
pl.plot(x,fit,'r-',lw=2)
pl.xlabel(r'Detuning', fontsize=18)
pl.ylabel('Intensity (a.u.)', fontsize=18)


FWHM = 2*best_parameters[0]
Q = (center_freq+best_parameters[1])/FWHM

S21 = best_parameters[2]/10
power = 10**(S21)

a = Symbol('a')
Qi = Symbol('Qi')
ratio = max(solve((a**2/((1+a)**2)-power), a))
print(ratio)

Qi = solve(1/Q - 1/Qi - 1/(ratio*Qi), Qi)
print(Qi)

print(best_parameters)

print('FWHM:', FWHM)
print('Q:', Q)
print('Qi:', Qi)
print('Qc:', ratio*Qi[0])



# l = fit.Lorentzian(x,data)
# print 'Lorentzian'



# l.fit(y_data=data, plot=True)

#pl.plot(x,data)
#pl.title('title')
#pl.xlabel('Detuning')
#pl.ylabel('dB')
#pl.show()




# f = fit.Lorentzian(fs, amps)
# h0 = np.max(amps)
# w0 = 2e6
# pos = fs[np.argmax(amps)]
# p0 = [np.min(amps), w0*h0, pos, w0]
# p = f.fit(p0)

pl.show()