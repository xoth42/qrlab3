# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 15:47:32 2018

@author: Wang_Lab
"""

X=[0,1,2,3,4,5,6,7,8,9,10,10.3,10.4,10.5]

Y=[0,58,120,181,242,300,354,407,454,494,527,536.9,539.9,543]
import lmfit
import numpy as np
from scipy.optimize import curve_fit

X= np.asarray(X)
import matplotlib.pyplot as pl

#def fitting(params, x, data):
#    est = params['c'] + params['b'] * x + params['a'] * x **2
#    return data - est
#
#pl.figure()
#pl.scatter(X,Y,marker = 's')
#pl.plot(X[0:6],60*X[0:6],'--')
#
#params = lmfit.Parameters()
#params.add('a', value=-4)
#params.add('b', value=40)
#params.add('c', value=0)
xs = X[5:]
ys = Y[5:]
#result = lmfit.minimize(fitting, params,  args=(xs, ys))
#lmfit.report_fit(result.params)
##pl.plot(xs,ys-fitting(result.params, xs,ys),'--')
##pl.plot(X[5:],-2*X[5:]**2+ 40*X[5:],'--')
#pl.xlabel('voltage(V)')
#pl.ylabel('magnetic field(mT)')
#pl.legend()

def model_func(x, a, b, c):    
    return a*x**2 + b*x + c 
sigma = np.ones(len(xs))
sigma[[0]] = 0.01
popt, pcov = curve_fit(model_func, xs, ys, p0=(-4 ,40, 0), sigma=sigma)
pl.plot(xs, model_func(xs, popt[0], popt[1], popt[2]))
text = "$f(x)=a*x^2 + b*x+c$ | a=%.3f, b=%.3f, c=%.3f" % (popt[0],popt[1],popt[2])
pl.annotate(text, xy=(0.03, 0.93), xycoords='axes fraction', fontsize=12)
pl.xlim([0,11])
pl.ylim([0,600])
pl.grid()
