# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 10:54:37 2019

@author: WangLab
"""
import matplotlib
matplotlib.interactive(True)
import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import lmfit
from lmfit import Parameters, Minimizer, report_fit

def S11(params, x, y): #model to use for S11 fitting to determine qubit frequency

    est = (-1 - params['kappa_1'] / (1j*(x-params['omega_c'])-params['kappa_a']/2))*params['A']
    return y - abs(est)
step_number = 400 #number of frequency points points - 1 used per sweep by the VNA (points value on sweep setup on VNA -1)
qubit_frequency1 = 8.6507625e9 #pre-defined qubit frequency to determine amount of shift due to stark drive
Data_freq = np.linspace(9e9,12e9,101) #array of different stark drive frequencies used over the run
filepath = r'C:\_Data\\'
hdf5_name = r'0625cooldown_circulator - Copy (5).hdf5'
date1 = '20190722'
date2 = '20190723' #date 2 is only necessary if data spans 2 days Comment line 24 out if only using one day
f = h5.File(filepath + hdf5_name, 'r')

background = '/20190722/124323_SingleTraceNoAsync' #data file of high power sweep for background to do background subtraction
background_freq = f[background]['freqs'].value
background_real = f[background]['real'].value
background_imag = f[background]['imaginary'].value
background_mag = (background_real**2 + background_imag**2)**.5
exp1 = f['/' + date1]
trials1 = []
for name in exp1: #creating a list of all files containing desired data
    trials1.append(name)
initial = (trials1.index('130554_SingleTrace'))
trials1 = trials1[initial:]
date1_add = [date1]*len(trials1)
trials1 = ['/' + date1_add[i] + '/' + trials1[i] for i in range(len(trials1))]
exp2 = f['/' + date2]#comment out line 40 - 47 if only using date1
trials2 = []
for name in exp2:
    trials2.append(name)
final = (trials2.index('002943_SingleTrace'))
trials2 = trials2[:final+1]
date2_add = [date2]*len(trials2)
trials2 = [('/' + date2_add[i] + '/' + trials2[i]) for i in range(len(trials2))]
trials = trials1 + trials2 #delete trials2 from line 48 if only using one day
Data_max = []
error_bounds1 = [[],[]]

for i in range(len(trials)): #determining frequency shift for each trial and appending it to Data_max
#    exp = f[u'/20190722/180531_SingleTrace']
    exp = f[str(trials[i])]
    freq = exp['freqs'].value
    real = exp['real'].value
    imag = exp['imaginary'].value
    mag = (real**2 + imag**2)**.5
#    pl.figure()    
#    pl.plot(freq[0],mag[0]) #put run2_run1 for y value if you want to plot the ratio of the two data sets, set to Data_max if only using one data set
#    pl.title('data')
#    pl.xlabel('freq')
#    pl.ylabel('data')
#    pl.show()
    mag = (real**2 + imag**2)**.5 - background_mag + background_mag[0][np.argmin(mag, axis = 1)[0]]
#    pl.figure()
#    pl.plot(freq[0],mag[0]) #put run2_run1 for y value if you want to plot the ratio of the two data sets, set to Data_max if only using one data set
#    pl.title('data - background')
#    pl.xlabel('freq')
#    pl.ylabel('data - background')
#    pl.show()
    min_index = np.argmin(mag, axis = 1)[0] #finding minimum point of data, this should be where the qubit is
    if (min_index-30) < 0:
        low_bound = 0
    else:
        low_bound = min_index - 30
    if (min_index + 30) > 400:
        up_bound = 400
    else:
        up_bound = min_index + 30 
    freq = freq[0][low_bound:up_bound] #isolating the curve to the 60 points around the minimum for a more accurate fit of qubit
    mag = mag[0][low_bound:up_bound]   
#    pl.figure()
#    pl.plot(freq,mag) #put run2_run1 for y value if you want to plot the ratio of the two data sets, set to Data_max if only using one data set
#    pl.title('data')
#    pl.xlabel('freq')
#    pl.ylabel('data')
    params = lmfit.Parameters()
    params.add('kappa_1', value=2.1305e+05)
    params.add('omega_c', value=freq[np.argmin((mag))]*1.0001)
    params.add('kappa_a', value=3.0022e+06)
    params.add('A', value=1)
    result = lmfit.minimize(S11, params, args=(freq,mag)) #fitting the data to the S11 model above to give a more accurate qubit frequency than just the minimum alone
    lmfit.report_fit(result.params)    
    fitdata = abs((-1 - result.params['kappa_1'].value / (-1j*(freq-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
#    pl.plot(freq,fitdata) #put run2_run1 for y value if you want to plot the ratio of the two data sets, set to Data_max if only using one data set
#    pl.show()
    qubit_shift_frequency = freq[np.argmin(fitdata)]
    print(qubit_shift_frequency)
    resids_sq = (mag - fitdata)**2
    st_dev = (sum(resids_sq)/len(mag))**.5
    #error_low = abs(freq[list(fitdata[0]).index(np.abs(fitdata[0:np.argmin(fitdata)]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #error_high = abs(freq[list(fitdata[0]).index(np.abs(fitdata[np.argmin(fitdata)+1:]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #fr = Symbol('fr')
    #error_bounds = solve(abs((-1 - result.params['kappa_1'].value / (-1j*(fr-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)-(fitdata[0].min()+2*st_dev),f)
    #print(error_bounds)
    freq_e= np.linspace(freq[0],freq[-1],501)
    fitdata_e = abs((-1 - result.params['kappa_1'].value / (-1j*(freq_e-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    error_low = fitdata_e.max()
    index_low = 0
    error_high = fitdata_e.max()
    index_high = 0
    test_range_low = fitdata_e[0:np.argmin(fitdata_e)]
    test_range_high = fitdata_e[np.argmin(fitdata_e)+1:]
    #pl.figure()
    #pl.plot(freq_e,fitdata_e)
    #pl.show()
    for l in range(len(test_range_low),0,-1):
        error_low_t = abs(fitdata_e[l]-(fitdata_e.min()+2*st_dev))
        if error_low_t <= error_low:
            error_low = error_low_t
            index_low = l
        if error_low_t > error_low:
            break
    for a in range(np.argmin(fitdata_e)+1,np.argmin(fitdata_e) + 1 + len(test_range_high)):
        error_high_t = abs(fitdata_e[a]-(fitdata_e.min()+2*st_dev))
        if error_high_t <= error_high:
            error_high = error_high_t
            index_high = a
        if error_high_t > error_high:
            break
    upper_error1 = ((freq_e[index_high] - freq_e[np.argmin(fitdata_e)]))
    lower_error1 = ((freq_e[np.argmin(fitdata_e)] - freq_e[index_low]))
    error_bounds1[0].append(lower_error1)
    error_bounds1[1].append(upper_error1)
    Data_max.append(qubit_frequency1 - qubit_shift_frequency) #appending the shifted frequency to Data_max


#manual entry of bad data points below
#Add a list of the graph dates and times with errors in the format '/yearmonthday/hourminutesecond_experiment' to graph_errors(line 83) if you just want
# to either insert a qubit value manually or want to tell the program to fit S11 around a different point on the original graph.
#If you want to use a different trace with a different frequency range put your entry as a list as[old trace date and time, new trace date and time] in same format
graph_errors = ['/20190722/152148_SingleTrace','/20190722/211714_SingleTrace','/20190722/212406_SingleTrace','/20190722/213058_SingleTrace','/20190722/213750_SingleTrace','/20190722/214442_SingleTrace','/20190722/215134_SingleTrace','/20190722/215826_SingleTrace','/20190722/220518_SingleTrace','/20190722/221210_SingleTrace','/20190722/221902_SingleTrace'] 
#make sure the index of shift_errors corresponds to the same index of the graph_errors file you want to change
#If you want to just input the desired qubit frequency manually make the entry ['man',desired frequency]
#if you want to get a fit for the curve whether it is original or a new file, just input the frequency around which you want the curve to be fit
#it will fit 30 points above and below the value you set
shift_errors = [['man',8.550e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9]]
frequency_errors = []
error_index = [trials.index(graph_errors[j]) for j in range(len(graph_errors))]
for i in range(len(graph_errors)): #converts indexes to actual frequencies of stark drives
    frequency_errors.append((Data_freq[error_index[i]]))
for k in range(len(frequency_errors)): 
    if type(graph_errors[k]) == list: #determining which file to use new or old one
        exp_error = f[graph_errors[k][1]]
    else:
        exp_error = f[graph_errors[k]]
    freq = exp_error['freqs'].value
    real = exp_error['real'].value
    imag = exp_error['imaginary'].value
    mag = (real**2 + imag**2)**.5
    if shift_errors[k][0] == 'man': #determining whether to fit or just use input frequency value
        Data_max[error_index[k]] = (qubit_frequency1 - shift_errors[k][1])
        continue
    min_index_error = shift_errors[k]
    if (min_index_error-30) < 0:
        low_bound = 0
    else:
        low_bound = min_index_error - 30
    if (min_index_error + 30) > step_number:
        up_bound = step_number
    else:
        up_bound = min_index_error + 30 
    freq = freq[0][low_bound:up_bound] #centering the data around desired point
    real = real[0][low_bound:up_bound]
    imag = imag[0][low_bound:up_bound]
    mag = (real**2 + imag**2)**.5
    params = lmfit.Parameters()
    params.add('kappa_1', value=2.1305e+05)
    params.add('omega_c', value=freq[np.argmin((mag))]*1.0001)
    params.add('kappa_a', value=3.0022e+06)
    params.add('A', value=1)
    result = lmfit.minimize(S11, params, args=(freq,mag)) #fitting the data to S11 model above
    fitdata = abs((-1 - result.params['kappa_1'].value / (-1j*(freq-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    qubit_shift_frequency = freq[np.argmin(fitdata)]
    resids_sq = (mag - fitdata)**2
    st_dev = (sum(resids_sq)/len(mag))**.5
    #error_low = abs(freq[list(fitdata[0]).index(np.abs(fitdata[0:np.argmin(fitdata)]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #error_high = abs(freq[list(fitdata[0]).index(np.abs(fitdata[np.argmin(fitdata)+1:]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #fr = Symbol('fr')
    #error_bounds = solve(abs((-1 - result.params['kappa_1'].value / (-1j*(fr-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)-(fitdata[0].min()+2*st_dev),f)
    #print(error_bounds)
    freq_e= np.linspace(freq[0],freq[-1],501)
    fitdata_e = abs((-1 - result.params['kappa_1'].value / (-1j*(freq_e-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    error_low = fitdata_e.max()
    index_low = 0
    error_high = fitdata_e.max()
    index_high = 0
    test_range_low = fitdata_e[0:np.argmin(fitdata_e)]
    test_range_high = fitdata_e[np.argmin(fitdata_e)+1:]
    #pl.figure()
    #pl.plot(freq_e,fitdata_e)
    #pl.show()
    for l in range(len(test_range_low),0,-1):
        error_low_t = abs(fitdata_e[l]-(fitdata_e.min()+2*st_dev))
        if error_low_t <= error_low:
            error_low = error_low_t
            index_low = l
        if error_low_t > error_low:
            break
    for a in range(np.argmin(fitdata_e)+1,np.argmin(fitdata_e) + 1 + len(test_range_high)):
        error_high_t = abs(fitdata_e[a]-(fitdata_e.min()+2*st_dev))
        if error_high_t <= error_high:
            error_high = error_high_t
            index_high = a
        if error_high_t > error_high:
            break
    upper_error1 = ((freq_e[index_high] - freq_e[np.argmin(fitdata_e)]))
    lower_error1 = [error_index[k]] = ((freq_e[np.argmin(fitdata_e)] - freq_e[index_low]))
    error_bounds1[0][k] = lower_error1
    error_bounds1[1][k] = upper_error1
    Data_max[error_index[k]] = (qubit_frequency1 - qubit_shift_frequency)
    
Data_max_1 = Data_max[:] #copying data to compare to Data_max_2 if a comparison plot is desired


# code below is the exact same as above, it is for comparing two sets of data together for things like circulator performance, if only one data set is required
# then comment out lines 133 - 245, all comments and directions are the same as above just do it for the second data set
qubit_frequency2 = 8.6507150e9 
Data_freq = np.linspace(9e9,12e9,101)
filepath = r'C:\_Data\\'
hdf5_name = r'0625cooldown_circulator - Copy (5).hdf5'
date1 = '20190721'
date2 = '20190722'
f = h5.File(filepath + hdf5_name, 'r')
background = '/20190719/184117_SingleTraceNoAsync'
background_freq = f[background]['freqs'].value
background_real = f[background]['real'].value
background_imag = f[background]['imaginary'].value
background_mag = (background_real**2 + background_imag**2)**.5
exp1 = f['/' + date1]
trials1 = []
for name in exp1:
    trials1.append(name)
initial = (trials1.index('143910_SingleTrace'))
trials1 = trials1[initial:]
date1_add = [date1]*len(trials1)
trials1 = ['/' + date1_add[i] + '/' + trials1[i] for i in range(len(trials1))]
exp2 = f['/' + date2]
trials2 = []
for name in exp2:
    trials2.append(name)
final = (trials2.index('020235_SingleTrace'))
trials2 = trials2[:final+1]
date2_add = [date2]*len(trials2)
trials2 = [('/' + date2_add[i] + '/' + trials2[i]) for i in range(len(trials2))]
trials = trials1 + trials2

Data_max = []
error_bounds2 = [[],[]]

for i in range(len(trials)):
    exp = f[str(trials[i])]
    freq = exp['freqs'].value
    real = exp['real'].value
    imag = exp['imaginary'].value
    mag = (real**2 + imag**2)**.5    
    mag = (real**2 + imag**2)**.5 - background_mag[0] + background_mag[0][np.argmin(mag, axis = 1)[0]]
    min_index = np.argmin(mag, axis = 1)[0]
    if (min_index-30) < 0:
        low_bound = 0
    else:
        low_bound = min_index - 30
    if (min_index + 30) > 400:
        up_bound = 400
    else:
        up_bound = min_index + 30 
    freq = freq[0][low_bound:up_bound]
    mag = mag[0][low_bound:up_bound]
    params = lmfit.Parameters()
    params.add('kappa_1', value=2.1305e+05)
    params.add('omega_c', value=freq[np.argmin((mag))]*1.0001)
    params.add('kappa_a', value=3.0022e+06)
    params.add('A', value=1)
    result = lmfit.minimize(S11, params, args=(freq,mag))
    fitdata = abs((-1 - result.params['kappa_1'].value / (-1j*(freq-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    qubit_shift_frequency = freq[np.argmin(fitdata)]
    resids_sq = (mag - fitdata)**2
    st_dev = (sum(resids_sq)/len(mag))**.5
    #error_low = abs(freq[list(fitdata[0]).index(np.abs(fitdata[0:np.argmin(fitdata)]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #error_high = abs(freq[list(fitdata[0]).index(np.abs(fitdata[np.argmin(fitdata)+1:]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #fr = Symbol('fr')
    #error_bounds = solve(abs((-1 - result.params['kappa_1'].value / (-1j*(fr-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)-(fitdata[0].min()+2*st_dev),f)
    #print(error_bounds)
    freq_e= np.linspace(freq[0],freq[-1],501)
    fitdata_e = abs((-1 - result.params['kappa_1'].value / (-1j*(freq_e-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    error_low = fitdata_e.max()
    index_low = 0
    error_high = fitdata_e.max()
    index_high = 0
    test_range_low = fitdata_e[0:np.argmin(fitdata_e)]
    test_range_high = fitdata_e[np.argmin(fitdata_e)+1:]
    #pl.figure()
    #pl.plot(freq_e,fitdata_e)
    #pl.show()
    for l in range(len(test_range_low),0,-1):
        error_low_t = abs(fitdata_e[l]-(fitdata_e.min()+2*st_dev))
        if error_low_t <= error_low:
            error_low = error_low_t
            index_low = l
        if error_low_t > error_low:
            break
    for a in range(np.argmin(fitdata_e)+1,np.argmin(fitdata_e) + 1 + len(test_range_high)):
        error_high_t = abs(fitdata_e[a]-(fitdata_e.min()+2*st_dev))
        if error_high_t <= error_high:
            error_high = error_high_t
            index_high = a
        if error_high_t > error_high:
            break
    upper_error2 = ((freq_e[index_high] - freq_e[np.argmin(fitdata_e)]))
    lower_error2 = ((freq_e[np.argmin(fitdata_e)] - freq_e[index_low]))
    error_bounds2[0].append(lower_error2)
    error_bounds2[1].append(upper_error2)
    Data_max.append(qubit_frequency2 - qubit_shift_frequency)
#mag_trial = ((f['/20190722/211023_SingleTrace']['real'].value)**2+(f['/20190722/211023_SingleTrace']['imaginary'].value)**2)**.5
#plotting_mag = mag_trial[0]
#plotting_freq = (f['/20190721/184417_SingleTrace']['freqs'].value)[0]
#pl.figure()
#pl.plot(plotting_freq,plotting_mag)
#pl.title('qubit freq vs stark shift freq')
#pl.xlabel('stark shift frequencies')
#pl.ylabel('qubit frequencies')
#pl.show()    

#manual entry of bad data points below
graph_errors = ['/20190721/165520_SingleTrace','/20190721/225020_SingleTrace','/20190721/225711_SingleTrace','/20190721/230403_SingleTrace','/20190721/231053_SingleTrace','/20190721/231745_SingleTrace','/20190721/232436_SingleTrace','/20190721/233128_SingleTrace','/20190721/233820_SingleTrace','/20190721/234511_SingleTrace','/20190721/235203_SingleTrace','/20190721/235203_SingleTrace'] #add a list of the graph dates and times with errors in the format '/yearmonthday/hourminutesecond_experiment'
shift_errors = [['man',8.550e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9],['man',8.55e9]] #for a shift that is off the range completely put a shift_errors value of the following list: ['man',shift frequency determined manually]

frequency_errors = []
error_index = [trials.index(graph_errors[j]) for j in range(len(graph_errors))]
for i in range(len(graph_errors)):
    frequency_errors.append((Data_freq[error_index[i]]))
for k in range(len(frequency_errors)): 
    if type(graph_errors[k]) == list:
        exp_error = f[graph_errors[k][1]]
    else:
        exp_error = f[graph_errors[k]]
    freq = exp_error['freqs'].value
    real = exp_error['real'].value
    imag = exp_error['imaginary'].value
    mag = (real**2 + imag**2)**.5
    if shift_errors[k][0] == 'man':
        Data_max[error_index[k]] = (qubit_frequency2 - shift_errors[k][1])
        continue
    min_index_error = shift_errors[k]
    if (min_index_error-30) < 0:
        low_bound = 0
    else:
        low_bound = min_index_error - 30
    if (min_index_error + 30) > step_number:
        up_bound = step_number
    else:
        up_bound = min_index_error + 30 
    freq = freq[0][low_bound:up_bound]
    real = real[0][low_bound:up_bound]
    imag = imag[0][low_bound:up_bound]
    mag = (real**2 + imag**2)**.5
    params = lmfit.Parameters()
    params.add('kappa_1', value=2.1305e+05)
    params.add('omega_c', value=freq[np.argmin((mag))]*1.0001)
    params.add('kappa_a', value=3.0022e+06)
    params.add('A', value=1)
    result = lmfit.minimize(S11, params, args=(freq,mag))
    fitdata = abs((-1 - result.params['kappa_1'].value / (-1j*(freq-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    qubit_shift_frequency = freq[np.argmin(fitdata)]
    resids_sq = (mag - fitdata)**2
    st_dev = (sum(resids_sq)/len(mag))**.5
    #error_low = abs(freq[list(fitdata[0]).index(np.abs(fitdata[0:np.argmin(fitdata)]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #error_high = abs(freq[list(fitdata[0]).index(np.abs(fitdata[np.argmin(fitdata)+1:]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
    #fr = Symbol('fr')
    #error_bounds = solve(abs((-1 - result.params['kappa_1'].value / (-1j*(fr-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)-(fitdata[0].min()+2*st_dev),f)
    #print(error_bounds)
    freq_e= np.linspace(freq[0],freq[-1],501)
    fitdata_e = abs((-1 - result.params['kappa_1'].value / (-1j*(freq_e-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
    error_low = fitdata_e.max()
    index_low = 0
    error_high = fitdata_e.max()
    index_high = 0
    test_range_low = fitdata_e[0:np.argmin(fitdata_e)]
    test_range_high = fitdata_e[np.argmin(fitdata_e)+1:]
    #pl.figure()
    #pl.plot(freq_e,fitdata_e)
    #pl.show()
    for l in range(len(test_range_low),0,-1):
        error_low_t = abs(fitdata_e[l]-(fitdata_e.min()+2*st_dev))
        if error_low_t <= error_low:
            error_low = error_low_t
            index_low = l
        if error_low_t > error_low:
            break
    for a in range(np.argmin(fitdata_e)+1,np.argmin(fitdata_e) + 1 + len(test_range_high)):
        error_high_t = abs(fitdata_e[a]-(fitdata_e.min()+2*st_dev))
        if error_high_t <= error_high:
            error_high = error_high_t
            index_high = a
        if error_high_t > error_high:
            break
    upper_error2 = ((freq_e[index_high] - freq_e[np.argmin(fitdata_e)]))
    lower_error2 = ((freq_e[np.argmin(fitdata_e)] - freq_e[index_low]))
    error_bounds2[0][k] = lower_error2
    error_bounds2[1][k] = upper_error2
    Data_max[error_index[k]] = (qubit_frequency2 - qubit_shift_frequency)
Data_max_2 = Data_max[:]
Data_max_1[44] = .03e6
run2_run1 = [Data_max_2[i]/Data_max_1[i] for i in range(len(Data_max_1))]
#pl.plot(Data_freq,Data_max_2) #put run2_run1 for y value if you want to plot the ratio of the two data sets, set to Data_max if only using one data set
error_bounds_combined = [run2_run1[i]*(((error_bounds2[0][i]+error_bounds2[1][i])/(Data_max_2[i]-qubit_frequency2))**2 + ((error_bounds1[0][i]+error_bounds1[1][i])/(Data_max_1[i]-qubit_frequency1))**2)**.5 for i in range(len(Data_max_1))]

pl.figure()

#pl.plot(Data_freq, run2_run1)
pl.errorbar(Data_freq/1e9, run2_run1,
            yerr=error_bounds_combined,
            fmt='')
#pl.errorbar(Data_freq, Data_max_1,
#            yerr=error_bounds1,
#            fmt='', label = '.024 T')
#pl.errorbar(Data_freq, Data_max_2,
#            yerr=error_bounds2,
#            fmt='', label = '-.024 T')
pl.xlabel('Stark Drive Frequency(GHz)',fontsize = 12)
pl.ylabel('Ratio of Qubit Frequency Shifts',fontsize = 12)
pl.yscale('log')
pl.legend()
pl.show()

#disregard below, just trial stuff
#exp = f[str(trials[50])]
#freq = exp['freqs'].value
#real = exp['real'].value
#imag = exp['imaginary'].value
#mag = (real**2 + imag**2)**.5
#mag = (real**2 + imag**2)**.5 - background_mag[0] + background_mag[0][np.argmin(mag, axis = 1)[0]]
#min_index = np.argmin(mag, axis = 1)[0]
#if (min_index-30) < 0:
#    low_bound = 0
#else:
#    low_bound = min_index - 30
#if (min_index + 30) > 400:
#    up_bound = 400
#else:
#    up_bound = min_index + 30 
#freq = freq[0][low_bound:up_bound]
#mag = mag[0][low_bound:up_bound]
#params = lmfit.Parameters()
#params.add('kappa_1', value=2.1305e+05)
#params.add('omega_c', value=freq[np.argmin((mag))]*1.0001)
#params.add('kappa_a', value=3.0022e+06)
#params.add('A', value=1)
#result = lmfit.minimize(S11, params, args=(freq,mag))
#fitdata = abs((-1 - result.params['kappa_1'].value / (-1j*(freq-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
##pl.figure()    
##pl.plot(freq,mag)
##pl.show() #put run2_run1 for y value if you want to plot the ratio of the two data sets, set to Data_max if only using one data set
#qubit_shift_frequency = freq[np.argmin(mag)]
##pl.plot(freq[0],fitdata[0])
##pl.show()
#resids_sq = (mag - fitdata)**2
#st_dev = (sum(resids_sq)/len(mag))**.5
#print(st_dev)
##error_low = abs(freq[list(fitdata[0]).index(np.abs(fitdata[0:np.argmin(fitdata)]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
##error_high = abs(freq[list(fitdata[0]).index(np.abs(fitdata[np.argmin(fitdata)+1:]-(qubit_shift_frequency+2*st_dev).min()))] - qubit_shift_frequency)
##fr = Symbol('fr')
##error_bounds = solve(abs((-1 - result.params['kappa_1'].value / (-1j*(fr-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)-(fitdata[0].min()+2*st_dev),f)
##print(error_bounds)
#freq_e= np.linspace(freq[0],freq[-1],101)
#fitdata_e = abs((-1 - result.params['kappa_1'].value / (-1j*(freq_e-result.params['omega_c'].value)-result.params['kappa_a'].value/2))*result.params['A'].value)
#error_low = fitdata_e.max()
#index_low = 0
#error_high = fitdata_e.max()
#index_high = 0
#test_range_low = fitdata_e[0:np.argmin(fitdata_e)]
#test_range_high = fitdata_e[np.argmin(fitdata_e)+1:]
##pl.figure()
##pl.plot(freq_e,fitdata_e)
##pl.show()
#for l in range(len(test_range_low),0,-1):
#    error_low_t = abs(fitdata_e[l]-(fitdata_e.min()+2*st_dev))
#    if error_low_t <= error_low:
#        error_low = error_low_t
#        print(error_low,l)
#        index_low = l
#    if error_low_t > error_low:
#        break
#for a in range(np.argmin(fitdata_e)+1,np.argmin(fitdata_e) + 1 + len(test_range_high)):
#    error_high_t = abs(fitdata_e[a]-(fitdata_e.min()+2*st_dev))
#    if error_high_t <= error_high:
#        error_high = error_high_t
#        print(error_high,a)
#        index_high = a
#    if error_high_t > error_high:
#        break
#upper_error = (freq_e[index_high] - freq_e[np.argmin(fitdata_e)])
#lower_error = (freq_e[np.argmin(fitdata_e)] - freq_e[index_low])
#print(freq_e[np.argmin(fitdata_e)],freq_e[index_low],freq_e[index_high])
#print(upper_error,lower_error)



