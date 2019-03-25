# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 11:02:09 2019

@author: Wang_Lab
"""

import matplotlib.pyplot as plt
import lmfit

#data= y


#ave=np.mean(y, axis=0)

#data_normalized=(data +25) / -6.5
std = np.std(wd, axis = 0)/np.sqrt(int(np.shape(wd)[0]))


#ave_oneless = np.delete(ave, 0)
#std_oneless = np.delete(std, 0)
x_data = np.linspace(1, 151, 51)
#ave_normalized = (ave +25)/ -6.5  

    
xs = x_data
ys=wd_ave
err=std

def exp_decay(params, x, data,err):
    est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
    return (data-est)/err

def exp_decay2(params, x):
    est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
    return est

params=lmfit.Parameters()
params.add('amplitude', value=0.5)
params.add('ofs', value=0.5, vary=False)
params.add('tau', value=100)

ax1 = plt.gca()
result= lmfit.minimize(exp_decay, params, args=(xs,ys,err))
lmfit.report_fit(result.params)
plt.plot(np.linspace(0,151,51), 1-exp_decay2(result.params,np.linspace(0,151,51)))
plt.errorbar(xs,1-ys,std, linestyle='None')
plt.plot(xs,1-ys, 'ro', markersize=4, color='r', linestyle='None')
#plt.plot(xs,1-np.transpose(y), '.', markersize=4, linestyle='None')
plt.title('With Drag Correction')
#plt.yscale('log')
ax1.set_ylabel('Average fidelity')
ax1.set_xlabel('Number of gates')


plt.figure()
ax2 = plt.gca()
plt.plot(xs,np.log(1-ys), 'ro', markersize=4, color='r', linestyle='None')
plt.title('Without Drag Correction')
ax2.set_ylabel('log(Average Fidelity)')
ax2.set_xlabel('Number of gates')
plt.show()
#
#
xs = np.linspace(1, 151, 51)
data =np.log(1-ys) 
err2 = np.std(data, axis = 0)/np.sqrt(int(np.shape(data)[0]))

def linear_fit(params, x, data, err):
    est = params['m']*x + params['n']
    return (data-est)/err

def linear_fit2(params, x):
    est = params['m']*x + params['n']
    return est

params = lmfit.Parameters()
params.add('m', value=0)
params.add('n', value=0, vary=False)


result = lmfit.minimize(linear_fit, params, args=(xs,data,err2))
lmfit.report_fit(result.params)
plt.plot(np.linspace(0,151,51), linear_fit2(result.params, np.linspace(0,151,51)))


    


#fit = np.polyfit(xs, np.log(1-ys), 1, w=1/std)
#fit_fn = np.poly1d(fit)





#import numpy as np
#import matplotlib.pyplot as pl
#import lmfit
#
#def fit_exp(params, x, data):
#    return data - (params['a'] + params['b'] * np.exp(-1 * x / params['c']))
#
#def exponential(params, x):
#    return params['a'] + params['b'] * np.exp(-1 * x / params['c'])
#
#data = np.loadtxt('raw_data.txt')
#ave = np.mean(data, axis = 0)
#std = np.std(data, axis = 0)/np.sqrt(int(np.shape(data)[0]))
#
#x_data = np.arange(1, 151, 3)
#
#params = lmfit.Parameters()
#params.add('a', value=np.min(ave))
#params.add('b', value=np.max(ave))
#params.add('c', value=x_data[-1])
#
#result = lmfit.minimize(fit_exp, params, args=(x_data, ave))
#
#print(result.params['a'].value)
#print(result.params['c'].value)
#a = result.params['a'].value
#
#ave -= a
#
#ave /= np.max(ave)
#
#fit = np.polyfit(x_data, np.log(ave), 1, w=1/std)
#fit_fn = np.poly1d(fit)
#print fit_fn
#print fit_fn[1]
## fit_fn is now a function which takes in x and returns an estimate for y
#
#text = 'Error per gate = %.03f '%(fit_fn[1]*(-1))
#
#
#
#pl.clf()
#ax = pl.gca()
##ax.set_yscale('log')
#ax.set_ylabel('ln(Fidelity)')
#ax.set_xlabel('Gate Pairs')
#pl.errorbar(x_data, np.log(ave), yerr = std)
#pl.plot(x_data, fit_fn(x_data), '--k', label=text)
#pl.legend(text)
#
#
#pl.savefig("plot.png")
#pl.show()
