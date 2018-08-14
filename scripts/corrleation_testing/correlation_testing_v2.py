from __future__ import division
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve
from pyfftw.interfaces.numpy_fft import fft



def vectorize_dec(function):
    def wrapper():
        return np.vectorize(function)
    return wrapper
def phase(c):
    import numpy as np
    try:
        return np.arctan(c.imag / c.real)
    except ZeroDivisionError:
        return 0
def mag(n):
    return np.absolute(n)

def fast_map(func, iterable):
    return np.asarray(map(func, iterable))
def project(c1, v, s):
    v = v - c1
    s = s - c1
    q = ((v.imag*s.imag + v.real*v.imag)/(s.imag**2 + s.real**2))*s
    return q + c1

def project_test():
    a = complex(np.random.randint(100), np.random.randint(100))    
    b = complex(np.random.randint(100), np.random.randint(100))    
    c = complex(np.random.randint(100), np.random.randint(100))
    d = project(a, b, c)
    plt.plot(a.real, a.imag, 'bo')
    plt.plot(b.real, b.imag, 'r*')
    plt.plot(c.real, c.imag, 'g^')
    plt.plot(d.real, d.imag, 'kx')
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
    
file_path = r'C:\Users\Wang_Lab\Desktop\TunableTransmonJuly18.hdf5'
try:
    file = h5py.File(file_path, 'r')
except IOError:
    file_path = r'/media/jcarey/files/TunableTransmonJuly18.hdf5'
    file = h5py.File(file_path, 'r')
if len(file.keys()) == 0:
    raise ValueError('No keys')
correlation_day = file['20180731']
good_keys = correlation_day.keys()
data_I = np.asarray([0, 0, 0])

data_II = np.asarray([0, 0, 0])
for key in good_keys:
    if 'avg' not in correlation_day[key]:
        continue
    if key[-2:] not in ['II', 'tI']:
        continue
    if key[-2:] == 'tI':
        data_I = np.vstack((data_I, correlation_day[key]['avg']))
    if key[-2:] == 'II':
        data_II = np.vstack((data_II, correlation_day[key]['avg']))

data_I = data_I[1:]
data_II = data_II[1:]
equator = data_I[:, 0]
t1 = data_I[:, 1]
g = data_I[:, 2]
true_t1 = map(lambda x: project(*x), zip(equator, g, t1))
true_t1 = np.asarray(true_t1)


g_2 = data_II[:, 0]
ft1 = data_II[:, 1]
f = data_II[:, 2]
true_ft1 = np.asarray(map(lambda x: project(*x), zip(g_2, f, ft1)))

run = True
if run is True:
    time_step = 500e-6 * 4 * 100 / 60
    time = np.linspace(0, time_step * len(t1), len(t1))
    data = [g, equator, true_t1, true_ft1]
    amplitudes = fast_map(np.absolute, data)
    averages = fast_map(lambda x: x - np.average(x), amplitudes)

    autocorrelations = fast_map(lambda x: np.correlate(x, x, mode = 'full') / np.sum(x**2), averages)
    
    right_halves = fast_map(lambda x: x[int(len(x)/2) + 1:], autocorrelations)
    t1c_p = PredefinedPlot([right_halves[2], 'k'], r'$T_{1}$ autocorrelation')
    gc_p = PredefinedPlot([right_halves[0], 'b'], r'g autocorrelation')
    eqc_p = PredefinedPlot([right_halves[1], 'g'], r'Equator autocorrelation')
    ft1c_p = PredefinedPlot([right_halves[3], 'm'], r'$FT_{1}$ autocorrelation')
    cross_correlate = lambda x: np.correlate(x[0], x[1], mode = 'full')

    cc = np.correlate(averages[2], averages[3], mode = 'full')
    spectrums = fast_map(fft, right_halves)
    cc_spectrum = fft(cc)
    plt.figure()
    plt.loglog(cc_spectrum, 'r*')
    plt.grid()
    plt.title('Power spectral density for T1 and FT1 correlations')
    coherence = (np.absolute(cc_spectrum[:len(spectrums[2])]))**2 / (spectrums[2]*spectrums[3])
    
    









