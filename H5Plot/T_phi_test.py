import os
import time

import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import lmfit

''' Path to the .hdf5 file '''
filepath = 'C:/_Data/'
hdf5_name = 'AQEC-11-2019.hdf5'
start_date = 20191209
end_date = 20191211
start_time = 184704
end_time = 211252




def t202_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    exp = np.exp(-(x / params['tau'].value))
    est = params['ofs'].value + params['amp'].value * exp * sine + params['slope'] * x
    return data - est


def t2_fit(params, x, data):
    '''
    Exponentially decaying sine fit function: a + b * exp(-c * x) * sin(d * x + e)

    parameters:
       ofs
       amp
       tau
       freq
       phi0
    '''

    sine = np.sin(2 * np.pi * x * params['freq'].value + params['phi0'].value)
    exp = np.exp(-(x / params['tau'].value))
    est = params['ofs'].value + params['amp'].value * exp * sine
    return data - est


def t2_analysis(xs, ys): 
    amp0 = (np.max(ys) - np.min(ys)) / 2
    off0 = (np.max(ys) + np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])

    params = lmfit.Parameters()
    params.add('ofs', value=off0)
    params.add('amp', value=amp0, min=0)
    params.add('tau', value=xs[-1], min=10, max=4e6)
    params.add('freq', value=f0, min=0)
    params.add('phi0', value=np.pi*0, min=-1.2*np.pi, max=1.2*np.pi)
    result = lmfit.minimize(t2_fit, params, args=(xs, ys))

    return result.params



def t202_analysis(xs, ys): 
    amp0 = (np.max(ys) - np.min(ys)) / 2
    off0 = (np.max(ys) + np.min(ys)) / 2
    fftys = np.abs(np.fft.fft(ys - np.average(ys)))
    fftfs = np.fft.fftfreq(len(ys), xs[1]-xs[0])
    f0 = np.abs(fftfs[np.argmax(fftys)])

    params = lmfit.Parameters()
    params.add('ofs', value=off0)
    params.add('amp', value=amp0, min=0)
    params.add('tau', value=xs[-1], min=10, max=4e6)
    params.add('freq', value=f0, min=0)
    params.add('phi0', value=0, min=-1.2*np.pi, max=1.2*np.pi)
    params.add('slope', value = 0)
    result = lmfit.minimize(t202_fit, params, args=(xs, ys))

    return result.params




''' Primary x axis and secondary if 2d'''
x_key = 'delays'
#x2_key = 'powers'

f = h5.File(filepath + hdf5_name, 'r')

#find all experiments in the right range of dates and times
t2_list = []
t202_list = []
for date in f:
    if int(date) >= start_date and int(date) <= end_date:
        date_folder = f[date]
        for exp in date_folder:
            
            if((int(date) > start_date or int(exp[:6]) >= start_time) and
               (int(date) < end_date or int(exp[:6]) <= end_time)):
                if exp[7:] == 'CavT2':
                    t2_list += [str(date) + '/' + str(exp)]
                elif exp[7:] == 'CavT2_02':
                    t202_list += [str(date) + '/' + str(exp)]

n_t2 = len(t2_list)
n_t202 = len(t202_list)
times_t2 = np.zeros(n_t2)
times_t202 = np.zeros(n_t202)
values_t2 = np.zeros(n_t2)
values_t202 = np.zeros(n_t202)
std_t2 = np.zeros(n_t2)
std_t202 = np.zeros(n_t202)



for i, name in enumerate(t2_list):
    try:
        exp = f[name]
        delays = exp['delays'].value
        data = exp['avg_pp'].value
    except KeyError:
        print('bad name or key', name)
        values_t2[i] = 0
        continue
        
    date = int(name[6:8])
    hour = int(name[-12:-10])
    minute = int(name[-10:-8])
    second = int(name[-8:-6])
    times_t2[i] = 86400 * date + 3600 * hour + 60 * minute + second

    fit = t2_analysis(delays, data)
    values_t2[i] = fit['tau'].value
    std_t2[i] = fit['tau'].stderr

for i, name in enumerate(t202_list):
    try:
        exp = f[name]
        delays = exp['delays'].value
        data = exp['avg_pp'].value
    except KeyError:
        print('bad name or key', name)
        values_t202[i] = 0
        continue
        
    date = int(name[6:8])
    hour = int(name[-15:-13])
    minute = int(name[-13:-11])
    second = int(name[-11:-9])
    times_t202[i] = 86400 * date + 3600 * hour + 60 * minute + second

    fit = t202_analysis(delays, data)
    values_t202[i] = fit['tau'].value
    std_t202[i] = fit['tau'].stderr
    
threshold = 1000

times_t2 = times_t2[values_t2 > threshold]
std_t2 = std_t2[values_t2 > threshold]
values_t2 = values_t2[values_t2 > threshold]

times_t202 = times_t202[values_t202 > threshold]
std_t202 = std_t202[values_t202 > threshold]
values_t202 = values_t202[values_t202 > threshold]

pl.figure()
pl.errorbar(times_t2/3600, values_t2, yerr = std_t2, label = 't2', fmt = '.')
pl.errorbar(times_t202/3600, values_t202, yerr = std_t202, label = 't2_02', fmt = '.')
pl.xlabel('hours')
pl.legend()
#pl.xlim(np.min(times_t2), np.max(times_t2))

