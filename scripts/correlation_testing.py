from __future__ import division
# -*- coding: utf-8 -*-
#Script by Josh to investigate the correlation between both T1 and FT1
#6/18/18

import numpy as np
import csv
import matplotlib
matplotlib.rcParams['agg.path.chunksize'] = 10000
import matplotlib.pyplot as plt
from scipy.integrate import simps
from scipy.signal import fftconvolve
from pyfftw.interfaces.numpy_fft import fft
g = np.load('g.npy')
t1 = np.load('t1.npy')
ft1 = np.load('ft1.npy')
equator = np.load('equator.npy')
class VectorizedNumpyFunction(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        import numpy as np
        self.func = np.vectorize(self.func)
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
class PredefinedPlot(object):
    def __init__(self, x, y, title, *args, **kwargs):
        import matplotlib
        matplotlib.rcParams['agg.path.chunksize'] = 10000
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot()
    
#data_location = 'C:\\Users\\wanglab\\Desktop\\t1tf1'
#overnight_run = 'C:\\Users\\wanglab\\Desktop\\t1ft1\\0324-0325 overnight run\\processed_results\\100 shot data_IQ.txt'
#data = []
#def josh_correlate(a, b):
#    from scipy.signal import fftconvolve
#    cross_correlate = fftconvolve(a, b)
#    from pyfftw.interfaces.numpy_fft import fft
#    csd = fft(cross_correlate)
#    return csd
def magnitude(s):
    return np.math.sqrt((s.real)**2 + (s.imag)**2)
magnitude = np.vectorize(magnitude)
def square(s):
    return s**2
square = np.vectorize(square)
def angle(num):
    return np.math.atan(num.imag / num.real)
def argand_diagram(array, *args, **kwargs):
    mags = map(magnitude, array)
    angles = map(angle, array)
    plt.figure()
    plot = plt.polar(angles, mags, *args, **kwargs)
    return plot
def coherence(x, y):
    return (square((magnitude(cross_spectral_density(x, y))))) / (cross_spectral_density(x, x) * cross_spectral_density(y, y))
def cross_spectral_density(a, b, *args, **kwargs):
    return fft(np.correlate(a, b, mode = 'full'))
def noise_average(array):
    av = np.average(array)
    noise_array = array - av
    return np.average(square(magnitude(noise_array)))
def absolute(x):
    return abs(x)
absolute = np.vectorize(absolute)
#f = open(overnight_run, 'rb')
#reader = csv.reader(f)
#l_f = list(reader)
#data.append(l_f)
#f.close()
#
#data = np.asarray(data)
#data.flatten()
#data = data[0]




#results = np.core.defchararray.replace(data, '+ -' , '-')
#results = np.core.defchararray.replace(results, '+  -', '-')
#for _ in range(0, 10):
#    results = np.core.defchararray.replace(results, " ", '')
#complex = np.vectorize(complex)
#results = complex(results)
#
#g = results[:,0]
#equator = results[:,1]
#t1 = results[:,2]
#ft1 = results[:,3]

run = True
if run is True:
    gamma_1 = map(lambda x: 1/x, t1)
    
        
    csd = cross_spectral_density(t1, ft1)
    absolute_csd = absolute(csd)
    
    
    print noise_average(equator)
    print noise_average(t1)
    print noise_average(ft1)



