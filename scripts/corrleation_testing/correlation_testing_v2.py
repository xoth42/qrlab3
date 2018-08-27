# A script by Josh to process all the data for the correlation studies.


from __future__ import division

import h5py
import matplotlib.pyplot as plt
import numpy as np
import warnings
# Some of the arrays are so big that numpy's fft function is super slow. In
# that case you need the fft from fftw, the fastest Fourier transform in the
# West.
from pyfftw.interfaces.numpy_fft import fft


# So many plots. So many.
plt.close('all')


def right_half(array):
    '''
    Take the right half of an array, since the correlations are all symmetric
    around zero.
    :param array:
    :return:
    '''
    a, b = np.array_split(array, 2)
    return b


def dot(a, b):
    '''
    Take the dot product by pretending complex numbers are vectors.
    :param a:
    :param b:
    :return:
    '''
    return (a.imag * b.imag) + (a.real * b.real)


def mag(n):
    '''
    The magnitude.
    :param n:
    :return:
    '''
    return np.absolute(n)


def unit_vector(v):
    '''
    Make a unit vector.
    :param v:
    :return:
    '''
    return (1 / (mag(v))) * v


def coherence(a, b, c):
    '''
    The coherence. Refer to the wikipedia page for the formula.
    :param a:
    :param b:
    :param c:
    :return:
    '''
    return ((np.absolute(a)) ** 2) / (b * c)


def phase(c):
    '''
    Return the phase of a complex number.
    :param c:
    :return:
    '''
    import numpy as np
    try:
        return np.arctan(c.imag / c.real)
    except ZeroDivisionError:
        return 0


def fast_map(func, iterable):
    '''
    map usually returns a list. Thats fine but returning a nice numpy array
    would be nice. Kind of inefficent but I don't know another way to do
    this. Maybe produce some generators?
    :param func:
    :param iterable:
    :return:
    '''
    return np.asarray(map(func, iterable))


def project(c1, v, s):
    '''
    Do a projection onto the line spanned by v and s. The formula is from the
    wiki page.
    :param c1: The offset. Subtracted to move everything to the origin.
    :param v:
    :param s:
    :return:
    '''
    v = v - c1
    s = s - c1
    q = (dot(v, s) / (dot(v, v))) * v

    if phase(v) - phase(s) >= np.pi / 2:
        return -q + c1
    return q + c1


def project_test():
    '''
    Test the projection routine from above.
    :return:
    '''
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
    '''A nice object for making plotting easier.'''

    def __init__(self, param_list, title, **kwargs):
        import matplotlib
        matplotlib.rcParams['agg.path.chunksize'] = 10000
        # This setting isn't really necessary. You need this if you want to
        # plot a truly gigantic array. Matplotlib will complain that the
        # array is too big to plot.
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(*param_list, **kwargs)
        plt.grid()
        plt.title(str(title))
        print self.convert(title)
        plt.savefig(self.convert(title) + '.png')
        plt.show()

    def convert(self, name):
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        a = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        a = a.replace(' ', '_')
        return a

    def other_function(self, func, *args, **kwargs):
        '''
        I'm not sure why this works, but it does.
        :param func:
        :param args:
        :param kwargs:
        :return:
        '''
        func(*args, **kwargs)


class CorrelationDay(object):
    def __init__(self, file, key):
        '''
        This is how the data should be organized. Feed this script a list of
        days that you want to process data from.
        :param file: An open HDF5 file.
        :param key: The key is the group name, which for qrlab is the date
        string for the day you want to process.
        '''
        self.file = file
        self.key = key
        self.groups = self.file[self.key]
        self.flux_change = []
        # flux_change in the measurement with flux in the name, but no I or
        # II at the end.
        self.I = []
        self.II = []
        self.constant_flux = []
        # constant_flux is the measurement with no flux in the name. Refer to
        #  the onenote for more info.
        self.flux = []
        if len(self.groups) == 0:
            raise ValueError('No data groups')
        self.process_groups()
        self.create_data()

    def process_groups(self):
        '''
        This function will take the gigantic list of groups in the file and
        organize them into a bunch of nice lists for easier processing.
        :return:
        '''
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
        '''This function takes a bunch of lists of group names,
        and constructs a bunch of dictionaries that organize the data for
        further processing. It has parallel in the name since I want to run
        this in parallel at some point. Thats not yet working obviously.'''
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
                if 'avg' in self.groups[i]:
                    group = self.groups[i]['avg']
                    equator.append(group[0])
                    t1.append(group[1])
                    g.append(group[2])
                else:
                    print 'No data in measurement ' + str(i) + '. Skipping'
        if name == self.II:
            for i in self.II:

                if 'avg' in self.groups[i]:
                    group = self.groups[i]['avg']
                    g.append(group[0])
                    ft1.append(group[1])
                    f.append(group[2])
                else:
                    print 'No data in measurement ' + str(i) + '. Skipping'
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
        '''
        Call this function to actually produce the data for calculations.
        :return:
        '''
        #        a = pool.map(parallel_data_construction, [self.flux,
        # self.constant_flux, self.I, self.II])
        results = map(self.parallel_data_construction,
                      [self.flux, self.constant_flux, self.I, self.II])
        data = dict()
        data['flux'] = results[0]
        data['constant_flux'] = results[1]
        data['I'] = results[2]
        data['II'] = results[3]
        return data


file_path = r'C:\Users\Wang_Lab\Desktop\TunableTransmonJuly18.hdf5'
day_codes = []
try:
    file = h5py.File(file_path, 'r')
except IOError:
    # This is so that Josh can work on this personal computer.
    file_path = r'/media/jcarey/files/TunableTransmonJuly18.hdf5'
    file = h5py.File(file_path, 'r')
if len(file.keys()) == 0:
    raise ValueError('No keys')
# correlation_day = file['20180731']
# The old data (AKA the 24 hr run from before the move) is organized into a
# series of numpy files in the same directory as this script. Its an easier
# format to work with but qrlab produces info in the HDF5 so thats what needs
#  to be worked with.
first_day = CorrelationDay(file, '20180731')
second_day = CorrelationDay(file, '20180809')
old_data = [np.load('g.npy'), np.load('equator.npy'), np.load('t1.npy'),
            np.load('ft1.npy')]


def data_pipeline(DayObject):
    # The four variables below are 'switches.' plot turns on the plotting
    # routine. Run runs the routine. averages normalizes some of the cross
    # correlations. This might not be good depending on how we want to
    # process this data. Old loads the old data into the proper variables.
    plot = True
    run = True
    average = False
    old = False
    CreatedData = DayObject.create_data()
    label = DayObject.key
    if run is True:
        g = CreatedData['I']['g']
        g_2 = CreatedData['II']['g']
        equator = CreatedData['I']['equator']
        t1 = CreatedData['I']['t1']
        ft1 = CreatedData['II']['ft1']
        f = CreatedData['II']['f']
        time_step = 500e-6 * 4 * 100 / 60
        time = np.linspace(0, time_step * len(t1), len(t1))
        true_t1 = map(lambda x: project(*x), zip(equator, g, t1))
        true_ft1 = np.asarray(map(lambda x: project(*x), zip(g_2, f, ft1)))
        true_t1 = np.asarray(true_t1)
        data = list()
        for i in [g, equator, true_t1, true_ft1]:
            if len(i) > 0:
                i = np.nan_to_num(i)
                data.append(i)
        len_min = min(map(len, data))
        data = [i[0:len_min] for i in data]

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
                return 'Dataset_' + str(label) + str(' ') + str(title)

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


data_pipeline(second_day)
