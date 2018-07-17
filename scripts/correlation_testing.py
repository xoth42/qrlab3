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
    def __init__(self, param_list, title, **kwargs):
        import matplotlib
        matplotlib.rcParams['agg.path.chunksize'] = 10000
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(*param_list, **kwargs)
        plt.grid()
        plt.title(str(title))
        plt.show()
    
#data_location = 'C:\\Users\\wanglab\\Desktop\\t1tf1'
#overnight_run = 'C:\\Users\\wanglab\\Desktop\\t1ft1\\0324-0325 overnight run\\processed_results\\100 shot data_IQ.txt'
#data = []
def beep():
    print '\a'
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

def angular_freq_to_freq(w):
    return w / (2*np.pi)
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
    time_step = 500e-6 * 4 * 100 / 60
    time = np.linspace(0, time_step * len(t1), len(t1))
    data = [g, equator, t1, ft1]
    amplitudes = map(np.absolute, data)
    averages = map(lambda x: x - np.average(x), amplitudes)

    autocorrelations = map(lambda x: np.correlate(x, x, mode = 'full') / np.sum(x**2), averages)
    right_halves = map(lambda x: x[int(len(x)/2) + 1:], autocorrelations)
    t1c_p = PredefinedPlot([right_halves[2], 'k'], r'$T_{1}$ autocorrelation')
    gc_p = PredefinedPlot([right_halves[0], 'b'], r'g autocorrelation')
    eqc_p = PredefinedPlot([right_halves[1], 'g'], r'Equator autocorrelation')
    ft1c_p = PredefinedPlot([right_halves[3], 'm'], r'$FT_{1}$ autocorrelation')
    cross_correlate = lambda x: np.correlate(x[0], x[1], mode = 'full')
    cc = np.correlate(averages[2], averages[3], mode = 'full')
    print noise_average(equator)
    print noise_average(t1)
    print noise_average(ft1)
    beep()

