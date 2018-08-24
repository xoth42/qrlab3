from __future__ import division
import h5py
import numpy as np
import matplotlib.pyplot as plt
from pyfftw.interfaces.numpy_fft import fft
from pathos.multiprocessing import Pool, freeze_support

plt.close('all')


def right_half(array):
    a, b = np.array_split(array, 2)
    return b


def dot(a, b):
    return (a.imag * b.imag) + (a.real * b.real)


def mag(n):
    return np.absolute(n)


def unit_vector(v):
    return (1 / (mag(v))) * v


def coherence(a, b, c):
    return (np.absolute(a)) ** 2 / (b * c)


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


def fast_map(func, iterable):
    return np.asarray(map(func, iterable))


def project(c1, v, s):
    v = v - c1
    s = s - c1
    q = (dot(v, s) / (dot(v, v))) * v

    if phase(v) - phase(s) >= np.pi / 2:
        return -q + c1
    return q + c1


def project_test():
    a = complex(np.random.randint(100), np.random.randint(100))
    b = complex(np.random.randint(100), np.random.randint(100))
    c = complex(np.random.randint(100), np.random.randint(100))
    d = project(a, b, c)
    plt.figure()

    plt.grid()
    plt.plot([a.real, b.real], [a.imag, b.imag], color='r', linestyle='-')
    plt.plot([a.real, c.real], [a.imag, c.imag], color='b', linestyle='-')
    plt.plot(d.real, d.imag, 'k*')


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

    def other_function(self, func, *args, **kwargs):
        func(*args, **kwargs)


class CorrelationDay(object):
    def __init__(self, file, key):
        self.file = file
        self.key = key
        self.groups = self.file[self.key]
        self.flux_change = []
        self.I = []
        self.II = []
        self.constant_flux = []
        self.flux = []
        if len(self.groups) == 0:
            raise ValueError('No data groups')
        self.process_groups()
        self.create_data()

    def process_groups(self):
        for i in self.groups:
            if '_T1_FT1' in i:
                if 'T1_FT1_fluxmeasurement' in i:
                    if i[-2:] in ['II', 'tI']:
                        self.flux_change.append(i)
                    else:
                        self.flux.append(i)
                else:
                    self.constant_flux.append(i)

        for i in self.flux_change:
            if i[-2:] == 'II':
                self.II.append(i)
            else:
                self.I.append(i)

    def parallel_data_construction(self, name):
        g = []
        e = []
        equator = []
        t1 = []
        ft1 = []
        f = []

        if name == self.constant_flux:
            for i in self.constant_flux:
                pass
        if name == self.I:
            for i in self.I:
                group = self.groups[i]['avg']
                for i in group:
                    equator.append(i)
                    t1.append(i)
                    g.append(i)
        if name == self.II:
            for i in self.II:
                group = self.groups[i]['avg']
                for i in group:
                    g.append(i)
                    ft1.append(i)
                    f.append(i)
        if name == self.flux:
            pass
        results = dict()
        results = {'g': np.asarray(g),
                   'e': np.asarray(e),
                   'equator': np.asarray(equator),
                   't1': np.asarray(t1),
                   'ft1': np.asarray(ft1),
                   'f': np.asarray(f)}
        return results

    def create_data(self):
        pool = Pool(processes=2)
        #        a = pool.map(parallel_data_construction, [self.flux,
        # self.constant_flux, self.I, self.II])
        results = map(self.parallel_data_construction,
                      [self.flux, self.constant_flux, self.I, self.II])
        data = dict()
        data['flux'] = results[0]
        data['constant_flux'] = results[1]
        data['I'] = results[2]
        data['II'] = results[3]
        pool.close()
        return data


file_path = r'C:\Users\Wang_Lab\Desktop\TunableTransmonJuly18.hdf5'
day_codes = []
try:
    file = h5py.File(file_path, 'r')
except IOError:
    file_path = r'/media/jcarey/files/TunableTransmonJuly18.hdf5'
    file = h5py.File(file_path, 'r')
if len(file.keys()) == 0:
    raise ValueError('No keys')
# correlation_day = file['20180731']
first_day = CorrelationDay(file, '20180731')
old_data = [np.load('g.npy'), np.load('equator.npy'), np.load('t1.npy'),
            np.load('ft1.npy')]


def data_pipeline(DataDictionary, label):
    plot = True
    run = True
    average = False
    old = True
    if run is True:
        g = DataDictionary['g']
        equator = DataDictionary['equator']
        t1 = DataDictionary['t1']
        ft1 = DataDictionary['ft1']
        time_step = 500e-6 * 4 * 100 / 60
        time = np.linspace(0, time_step * len(t1), len(t1))
        true_t1 = map(lambda x: project(*x), zip(equator, g, t1))
        true_ft1 = np.asarray(map(lambda x: project(*x), zip(g_2, f, ft1)))
        true_t1 = np.asarray(true_t1)
        data = [g, equator, true_t1, true_ft1]

        if old is True:
            data = old_data
        directions = g - equator
        angles = np.angle(directions, deg=True)
        amplitudes = fast_map(np.absolute, data)
        averages = fast_map(lambda x: x - np.average(x), amplitudes)
        if averages is True:
            autocorrelations = fast_map(
                lambda x: np.correlate(x, x, mode='full') / np.sum(x ** 2),
                averages)
        else:
            autocorrelations = fast_map(
                lambda x: np.correlate(x, x, mode='full'),
                averages)

        right_halves = fast_map(right_half, autocorrelations)

        cross_correlate = lambda x: np.correlate(x[0], x[1], mode='full')

        cc = np.correlate(averages[2], averages[3], mode='full')
        spectrums = fast_map(fft, right_halves)
        spectrums = fast_map(np.absolute, spectrums)
        cc_spectrum = fft(cc)
        cc_spectrum = np.absolute(cc_spectrum)

        coherence_ = coherence(cc_spectrum[0:len(spectrums[2])], spectrums[2],
                               spectrums[3])

        def nice_label(title):
            if old is True:
                return 'Old data ' + str(title)
            else:
                return 'New data ' + str(label) + str(' ') + str(title)

        if plot == True:
            plt.figure()
            plt.loglog(cc_spectrum, 'r')
            plt.grid()
            plt.title(
                nice_label(
                    'Power spectral density for T1 and FT1 correlations'))
            plt.figure()
            plt.plot(coherence_, 'k')
            plt.title(nice_label('Coherence'))
            subtracted_autoc = right_halves[2] - right_halves[1]

            phases_p = PredefinedPlot([angles, 'k'], nice_label('phases'))
            #    phases_p.other_function(plt.ylim, ((-2*np.pi, 2*np.pi)))
            autoc_p = PredefinedPlot([subtracted_autoc, 'm'], nice_label(
                "autocorr of T1 minus autocorr of eq"))
            t1c_p = PredefinedPlot([right_halves[2], 'k'],
                                   nice_label(r'$T_{1}$ autocorrelation'))
            gc_p = PredefinedPlot([right_halves[0], 'b'],
                                  nice_label(r'g autocorrelation'))
            eqc_p = PredefinedPlot([right_halves[1], 'g'],
                                   nice_label(r'Equator autocorrelation'))
            ft1c_p = PredefinedPlot([right_halves[3], 'm'],
                                    nice_label(r'$FT_{1}$ autocorrelation'))
            g_p = PredefinedPlot([averages[0], 'm'],
                                 nice_label(r'Raw g_1 voltages'))
            t1_p = PredefinedPlot([averages[2], 'k'],
                                  nice_label(r'Raw T1 voltages'))
            ft1_p = PredefinedPlot([averages[3], 'b'],
                                   nice_label(r'Raw FT1 voltages'))


if __name__ == '__main__':
    pool = Pool(processes=4)
    information = first_day.create_data()
    processing_list = [(information[label], label) for label in
                       information.keys()]
    a = pool.map(data_pipeline, processing_list)
    pool.close()
