# A script by Josh to process all the data for the correlation studies.
# TODO Look and see why some array values are zero.
# TODO Parallelize.
# TODO Add some nice comments.
# TODO Make the timestep right.

from __future__ import division

import h5py
import numpy as np
# Some of the arrays are so big that numpy's fft function is super slow. In
# that case you need the fft from fftw, the fastest Fourier transform in the
# West.
from pyfftw.interfaces.numpy_fft import fft
import scipy.fftpack
import datetime
import inspect


def display():
    '''
    A nice function to make debugging easier. Prints the line number and the
    time.
    :return:
    '''
    cf = inspect.currentframe()
    time = datetime.datetime.now()
    line_no = cf.f_back.f_lineno
    print
    print 'Time is: ' + str(time)
    print 'On line: ' + str(line_no)
    print


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


def return_timestep(trigger_rate, number_of_points, num_averages):
    return (
                   trigger_rate * num_averages * number_of_points) / 60
    # time step in min


#
# def spec(array):
#    time_step = return_timestep(100e-6, 3, 1000) #TODO diff time steps for I
#  and II
#    time = np.linspace(0, time_step * len(data_pipeline.g),
# len(data_pipeline.g))
#    N = len(time)
#    w = np.linspace(0.0, 1.0/(2.0*time_step), len(time)/2)
#    fourier = scipy.fftpack.fft(array[len(array)/2:])
#    spec = np.abs(fourier)
#    return w , 2.0/N*spec[0:N/2]
def phase(c):
    '''
    Return the phase of a complex number.
    :param c:
    :return:
    '''
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
    if (v == None) or (s == None):
        return 0 + 0j
    v = v - c1
    s = s - c1
    q = (dot(v, s) / (dot(v, v))) * v

    if phase(v) - phase(s) >= np.pi / 2:
        return -q + c1
    return q + c1


def project_test():
    import matplotlib.pyplot as plt
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
        plt.xlabel('time (sec)')

    def convert(self, name):
        '''Make the keys better for saving and printing. Shamelessly stolen
        from the internet. This uses a regex to replace some characters in
        the string so that the name of the plot is correct.'''
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        a = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        a = a.replace(' ', '_')
        return a

    def other_function(self, func, *args, **kwargs):
        '''
        I'm not sure why this works, but it does. Such is life.
        :param func:
        :param args:
        :param kwargs:
        :return:
        '''
        func(*args, **kwargs)


class CorrelationDay(object):
    def __init__(self, file, key, histogram=None, start=None, end=None, ):
        '''
        This is how the data should be organized. Feed this script a list of
        days that you want to process data from.
        :param file: An open HDF5 file.
        :param key: The key is the group name, which for qrlab is the date
        string for the day you want to process.
        :param histogram: Determines whether the input data was taken in
        histogram mode, and contains all of the shot by shot data,
        or in average mode, so that it only contains average data.
        '''
        if histogram is None:
            raise ValueError('The histogram parameter must be set.')
        self.histogram = histogram
        self.file = file
        self.key = key
        self.start = start
        self.end = end
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
        self.time_process_groups()
        self.process_groups()

    def time_process_groups(self):
        '''
        This function processes the groups in such a way that only data
        between the start and end points will be processed.
        :return:
        '''
        if (self.start == None) or (self.end == None):
            self.good_groups = self.groups
            return
        groups = list()
        for i in self.groups:
            groups.append(i)
        splits = [i.split('_') for i in groups]
        splits = [i[0] for i in splits]
        starting_index = splits.index(self.start)
        ending_index = splits.index(self.end)
        self.good_groups = groups[starting_index:ending_index]

    def process_groups(self):
        '''
        This function will take the gigantic list of groups in the file and
        organize them into a bunch of nice lists for easier processing.
        :return:
        '''
        for i in self.good_groups:
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
                if 'avg' in self.groups[i]:
                    group = self.groups[i]['avg']
                    equator.append(group[0])
                    t1.append(group[1])
                    g.append(group[2])
                    ft1.append(group[3])
                    f.append(group[4])
                if 'shots' in self.groups[i]:
                    group = self.groups[i]['shots']
                    # for k in group:
                    #    temp.append(k)
                    # stacked_array = np.row_stack(np.split(group[:],
                    #                                       (len(group[:]) /
                    #                                        5)))
                    # equator.append(stacked_array[:, 0])
                    # t1.append(stacked_array[:, 1])
                    # g.append(stacked_array[:, 2])
                    # ft1.append(stacked_array[:, 3])
                    # f.append(stacked_array[:, 4])
                    # print group[0::1]
                    equator.append(group[0::5])
                    t1.append(group[1::5])
                    g.append(group[2::5])
                    ft1.append(group[3::5])
                    f.append(group[4::5])

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
                    equator.append(group[0])
                    g.append(group[1])
                    ft1.append(group[2])
                    f.append(group[3])
                else:
                    print 'No data in measurement ' + str(i) + '. Skipping'
        if name == self.flux:
            pass
        results = dict()
        g = self.purge_non_arrays_and_flatten(g)
        e = self.purge_non_arrays_and_flatten(e)
        equator = self.purge_non_arrays_and_flatten(equator)
        t1 = self.purge_non_arrays_and_flatten(t1)
        ft1 = self.purge_non_arrays_and_flatten(ft1)
        f = self.purge_non_arrays_and_flatten(f)

        results = {'g': np.asarray(g),
                   'e': np.asarray(e),
                   'equator': np.asarray(equator),
                   't1': np.asarray(t1),
                   'ft1': np.asarray(ft1),
                   'f': np.asarray(f)}
        return results

    def purge_non_arrays_and_flatten(self, arr):
        if self.histogram == False:
            return arr
        '''
        There are measurements which contain the shot data and others that
        contain only the avg value. In that case the result list would
        contain a few scalars in between giant numpy arrays. This function
        purges the scalars.
        :param arr:
        :return:
        '''
        ndarrays = filter(lambda x: type(x) == np.ndarray, arr)
        return np.ndarray.flatten(np.asarray(ndarrays))

    def create_data(self):
        '''
        Call this function to actually produce the data for calculations.
        :return:
        '''

        results = map(self.parallel_data_construction,
                      [self.flux, self.constant_flux, self.I, self.II])
        data = dict()
        data['flux'] = results[0]
        data['constant_flux'] = results[1]
        data['I'] = results[2]
        data['II'] = results[3]
        return data

    def __add__(self, other):
        '''
        This functions implements the addition operator between two day
        objects. This particular operation DOES NOT COMMUTE, to preserve the
        idea of time progressing along the entries in an array.
        :param other:
        :return:
        '''
        if self.histogram != other.histogram:
            raise ValueError('Hist parameters must be the same for addition.')
        before_data = self.create_data()
        after_data = other.create_data()
        new_data = dict()
        temp_data = dict()
        for key in before_data:
            for item in before_data[key]:
                if (len(before_data[key][item]) == 0) and (len(after_data[key][
                                                                   item])
                                                           == 0):
                    temp_data[item] = []
                elif (len(before_data[key][item]) == 0):
                    temp_data[item] = after_data[key][item]
                elif len(after_data[key][item]) == 0:
                    temp_data[item] = before_data[key][item]
                else:
                    temp_data[item] = np.concatenate((before_data[key][item],
                                                      after_data[key][item]))
            new_data[key] = temp_data
            temp_data = dict()
        return new_data


file_path = r'C:\Users\Wang_Lab\Desktop\TunableTransmonJuly18.hdf5'
try:
    file = h5py.File(file_path, 'r')
except IOError:
    # This is so that Josh can work on his personal computer.
    file_path = r'/media/jcarey/files/TunableTransmonJuly18.hdf5'
    file = h5py.File(file_path, 'r')
if len(file.keys()) == 0:
    raise ValueError('No keys')
# correlation_day = file['20180731']
# The old data (AKA the 24 hr run from before the move) is organized into a
# series of numpy files in the same directory as this script. Its an easier
# format to work with but qrlab produces info in the HDF5 so thats what needs
#  to be worked with.
first_day = CorrelationDay(file, '20180815', histogram=False, start=
'133503', end='195709')
second_day = CorrelationDay(file, '20180816', histogram=True, start = None,
                            end = None)

old_data = [np.load('g.npy'), np.load('equator.npy'), np.load('t1.npy'),
            np.load('ft1.npy')]

preliminary_option_dict = {'plot': True,
                           'mean': False,
                           'run': True,
                           'average': False,
                           'old': False,
                           'I_and_II': False,
                           'constant': True,
                           'projections': False,
                           'mean_point_number': 100}


class DataPipeLineCallableClass(object):
    def __init__(self, data_processing_mode, option_dictionary):
        self.data_processing_mode = data_processing_mode
        self.option_dictionary = option_dictionary
        self.dictionary_error_check()

    def dictionary_error_check(self):
        if self.option_dictionary['old'] == self.option_dictionary[
            'I_and_II'] == self.option_dictionary['constant']:
            raise ValueError('One option must be selected.')
        if type(self.option_dictionary['mean_point_number']) is not int:
            raise ValueError('Mean point number must be an integer.')

    def __call__(self, DayObject):
        if self.data_processing_mode is 'I_and_II':
            self.flux_toggle_data_pipeline(DayObject)
        if self.data_processing_mode is 'constant':
            self.constant_flux_data_pipeline(DayObject)

    def constant_flux_data_pipeline(self, DayObject):
        # Creating the day objects takes very little time. Running the
        # create_data function is what produces the data and takes so long.
        CreatedData = DayObject.create_data()
        label = DayObject.key
        g = CreatedData['constant_flux']['g']
        equator = CreatedData['constant_flux']['equator']
        t1 = CreatedData['constant_flux']['t1']
        ft1 = CreatedData['constant_flux']['ft1']
        f = CreatedData['constant_flux']['f']
        projections = self.option_dictionary['projections']
        true_t1 = t1
        true_ft1 = ft1
        if projections is True:
            true_t1 = map(lambda x: project(*x), zip(equator, g, t1))
            true_ft1 = np.asarray(
                map(lambda x: project(*x), zip(f, g, ft1)))
            true_t1 = np.asarray(true_t1)

        data = filter(lambda x: type(x) == np.ndarray, [g, equator, true_t1,
                                                        true_ft1])
        len_min = min(map(len, data))
        data = [i[0:len_min] for i in data]
        len_max = max(map(len, data))
        if len_max is 0:
            print "There is no data. Returning"
            return
        if self.option_dictionary['mean'] is True:
            mean_point_number = self.option_dictionary['mean_point_number']
            temporary_data = []
            for index, entry in enumerate(data):
                splits = np.array_split(entry,
                                        (len(entry) / mean_point_number))
                means = np.asarray(map(np.average, splits))
                temporary_data.append(means)
            data = temporary_data
        display()

        ##########################################
        # Data is now properly prepared for calculations.
        ##########################################

        directions = g - equator
        angles = np.angle(directions, deg=True)
        amplitudes = map(np.absolute, data)
        averages = map(lambda x: x - np.average(x), amplitudes)
        if self.option_dictionary['average'] is True:
            autocorrelations = map(
                lambda x: np.correlate(x, x, mode='full') / np.sum(x ** 2),
                averages)
        else:
            autocorrelations = map(
                lambda x: np.correlate(x, x, mode='full'),
                averages)

        right_halves = fast_map(right_half, autocorrelations)

        #        cc = np.correlate(averages[2], averages[3], mode='full')

        spectrums = fast_map(fft, right_halves)

        cc_yz = np.correlate(averages[2], averages[3], mode='full')  # cross
        # -correlation of T1 and FT1
        cc_yz = cc_yz[len(cc_yz) // 2:]
        cc_xy = np.correlate(averages[1], averages[2], mode='full')  #
        # cross-correlation of equator and T1
        cc_xy = cc_xy[len(cc_xy) // 2:]
        cc_xz = np.correlate(averages[1], averages[3], mode='full')  #
        # cross-correlation of equator and FT1
        cc_xz = cc_xz[len(cc_xz) // 2:]

        cc_ft1eq2 = np.correlate(averages[3], averages[5], mode='full')
        cc_ft1eq2 = cc_ft1eq2[len(cc_ft1eq2) // 2:]

        cc_xx2 = np.correlate(averages[1], averages[5], mode='full')
        cc_xx2 = cc_xx2[len(cc_xx2) // 2:]

        time_step = 12.0  # in seconds

        time = np.linspace(0, time_step * len(right_halves[0]),
                           len(right_halves[0]))
        time_raw = np.linspace(0, time_step * len(averages[0]),
                               len(averages[0]))
        N = len(time)

        w = np.linspace(0.0, 1.0 / (2.0 * time_step), len(time) / 2)

        cc_spectrum_yz = np.abs(fft(cc_yz))
        cc_spectrum_xy = np.abs(fft(cc_xy))
        cc_spectrum_xz = np.abs(fft(cc_xz))

        cc_spectrum_ft1eq2 = np.abs(fft(cc_ft1eq2))
        cc_spectrum_xx2 = np.abs(fft(cc_xx2))

        #        fft_yz = scipy.fftpack.fft(right_halves_cc[0])
        #        fft_xy = scipy.fftpack.fft(cc_xy[len(cc_xy)/2:])
        #        fft_xz = scipy.fftpack.fft(cc_xz[len(cc_xz)/2:])
        #
        #        fourier = scipy.fftpack.fft(autocorr_T1[len(
        # autocorr_T1)/2:])

        def nice_label(title):
            if old is True:
                return 'Old data ' + str(title)
            else:
                return 'Dataset_' + str(label) + str(' ') + str(title)

        if self.option_dictionary['plot'] == True:
            import matplotlib.pyplot as plt
            plt.close('all')
            #            plt.figure()
            #            plt.loglog(cc_spectrum, 'r')
            #            plt.grid()
            #            plt.title(
            #                nice_label(
            #                    'Power spectral density for T1 and FT1
            # correlations'))
            #            plt.figure()
            #            plt.plot(coherence_, 'k')
            #            plt.title(nice_label('Coherence'))
            subtracted_autoc = right_halves[2] - right_halves[1]
            R_t1t1_spec = np.abs(fft(subtracted_autoc))
            subtracted_autocII = right_halves[3] - right_halves[5]
            R_ft1ft1_spec = np.abs(fft(subtracted_autocII))
            noise_equiv = cc_xy[:-1] - right_halves[1]
            R_t1ft1 = cc_yz - cc_xx2
            R_t1ft1_spec = np.abs(fft(R_t1ft1))

            #            phases_p = PredefinedPlot([angles, 'k'],
            # nice_label('phases'))
            #    phases_p.other_function(plt.ylim, ((-2*np.pi, 2*np.pi)))
            autoc_p = PredefinedPlot([time, subtracted_autoc, 'm'],
                                     nice_label(
                                         "autocorr of T1 minus autocorr "
                                         "of eq"))
            t1c_p = PredefinedPlot([time, right_halves[2], 'k'],
                                   nice_label(r'$T_{1}$ autocorrelation'))
            #            gc_p = PredefinedPlot([time, right_halves[0], 'b'],
            #                                  nice_label(r'g
            # autocorrelation'))
            eqc_p = PredefinedPlot([time, right_halves[1], 'g'],
                                   nice_label(r'Equator autocorrelation'))
            ft1c_p = PredefinedPlot([time, right_halves[3], 'k'],
                                    nice_label(r'$FT_{1}$ autocorrelation'))
            eqIIc_p = PredefinedPlot([time, right_halves[5], 'g'],
                                     nice_label(
                                         r'Equator(II) autocorrelation'))
            autocII_p = PredefinedPlot([time, subtracted_autocII, 'm'],
                                       nice_label(
                                           "autocorr of FT1 minus "
                                           "autocorr of eqII"))
            #            g_p = PredefinedPlot([time_raw, averages[0], 'm'],
            #                                 nice_label(r'Raw g_1
            # voltages'))
            eq_p = PredefinedPlot([time_raw, averages[1], 'g'],
                                  nice_label(r'Raw Equator voltages'))
            print('variance of equator:',
                  np.sum(averages[1] ** 2) / len(averages[1]))
            t1_p = PredefinedPlot([time_raw, averages[2], 'k'],
                                  nice_label(r'Raw T1 voltages'))
            print(
                'variance of T1:',
                np.sum(averages[2] ** 2) / len(averages[2]))
            ft1_p = PredefinedPlot([time_raw, averages[3], 'b'],
                                   nice_label(r'Raw FT1 voltages'))
            print(
                'variance of FT1:',
                np.sum(averages[3] ** 2) / len(averages[3]))
            #            ft1_p = PredefinedPlot([time_raw, averages[4],
            # 'b'],
            #                                   nice_label(r'Raw g_2
            # voltages'))
            ft1_p = PredefinedPlot([time_raw, averages[5], 'b'],
                                   nice_label(r'Raw eq_2 voltages'))
            print('variance of equatorII:',
                  np.sum(averages[5] ** 2) / len(averages[5]))
            cc_eqt1_p = PredefinedPlot([time_raw, cc_xy, 'b'],
                                       nice_label(
                                           r'Cross-correlation of equator '
                                           r'and '
                                           r'T1'))
            cc_eqft1_p = PredefinedPlot([time_raw, cc_xz, 'b'],
                                        nice_label(
                                            r'Cross-correlation of equator '
                                            r'and FT1'))
            cc_t1ft1_p = PredefinedPlot([time_raw, cc_yz, 'b'],
                                        nice_label(
                                            r'Cross-correlation of T1 and '
                                            r'FT1'))
            cc_ft1eq2_p = PredefinedPlot([time_raw, cc_ft1eq2, 'b'],
                                         nice_label(
                                             r'Cross-correlation of FT1 '
                                             r'and '
                                             r'equatorII'))
            cc_eqeq2_p = PredefinedPlot([time_raw, cc_xx2, 'b'],
                                        nice_label(
                                            r'Cross-correlation of '
                                            r'equator and '
                                            r'equatorII'))
            noise_equiv_p = PredefinedPlot([time, noise_equiv, 'b'],
                                           nice_label(
                                               r'Cross-corr equator T1 '
                                               r'minus autocorr equator'))
            spec_t1t1_p = PredefinedPlot(
                [w, 2.0 / N * R_t1t1_spec[0:N // 2], 'o'],
                nice_label(r'Spectral density of T1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_ft1ft1_p = PredefinedPlot(
                [w, 2.0 / N * R_ft1ft1_spec[0:N // 2], 'o'],
                nice_label(r'Spectral density of FT1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_eqt1_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_xy[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of equator and T1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_eqft1_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_xz[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of equator and FT1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_t1ft1_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_yz[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of T1 and FT1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_ft1eq2_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_ft1eq2[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of FT1 and equatorII'))
            plt.yscale('log')
            plt.xscale('log')
            spec_eqeq2_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_xx2[0:N // 2], 'o'],
                nice_label(
                    r'Cross-spectral density of equator and equatorII'))
            plt.yscale('log')
            plt.xscale('log')
            spec_t1ft1_subtr_p = PredefinedPlot(
                [w, 2.0 / N * R_t1ft1_spec[0:N // 2], 'o'],
                nice_label(
                    r'Cross-spectral density of T1 and FT1 (with '
                    r'background subtracted)'))
            plt.yscale('log')
            plt.xscale('log')

    def flux_toggle_data_pipeline(self, DayObject):
        # Creating the day objects takes very little time. Running the
        # create_data function is what produces the data and takes so long.
        CreatedData = DayObject.create_data()
        label = DayObject.key
        g = CreatedData['I']['g']
        g_2 = CreatedData['II']['g']
        equator = CreatedData['I']['equator']
        equator_2 = CreatedData['II']['equator']
        t1 = CreatedData['I']['t1']
        ft1 = CreatedData['II']['ft1']
        f = CreatedData['II']['f']

        projections = self.option_dictionary['projections']
        if projections is True:
            true_t1 = map(lambda x: project(*x), zip(equator, g, t1))
            true_ft1 = np.asarray(
                map(lambda x: project(*x), zip(f, g_2, ft1)))
            true_t1 = np.asarray(true_t1)
        if projections is False:
            true_t1 = t1
            true_ft1 = ft1
        data = filter(lambda x: type(x) is np.ndarray,
                      [g, equator, true_t1, true_ft1, g_2, equator_2])
        len_min = min(map(len, data))
        len_max = max(map(len, data))
        if len_max is 0:
            print "There is no data. Returning"
            return
        data = [i[0:len_min] for i in data]
        mean = self.option_dictionary['mean']
        if mean is True:
            mean_point_number = self.option_dictionary['mean_point_number']
            empty_data = []
            for index, entry in enumerate(data):
                splits = np.array_split(entry,
                                        (len(entry) / mean_point_number))
                means = np.asarray(map(np.average, splits))
                empty_data.append(means)
            data = empty_data

        ##########################################
        # Data is now properly prepared for calculations.
        ##########################################

        directions = g - equator
        angles = np.angle(directions, deg=True)
        amplitudes = map(np.absolute, data)
        averages = map(lambda x: x - np.average(x), amplitudes)
        average = self.option_dictionary['average']
        if average is True:
            autocorrelations = map(
                lambda x: np.correlate(x, x, mode='full') / np.sum(x ** 2),
                averages)
        else:
            autocorrelations = map(
                lambda x: np.correlate(x, x, mode='full'),
                averages)

        display()
        right_halves = fast_map(right_half, autocorrelations)

        #        cc = np.correlate(averages[2], averages[3], mode='full')

        spectrums = fast_map(fft, right_halves)
        spectrums = fast_map(np.absolute, spectrums)
        #        cc_spectrum = fft(cc)
        #        cc_spectrum = np.absolute(cc_spectrum)
        #
        #        coherence_ = coherence(cc_spectrum[0:len(spectrums[2])],
        # spectrums[2],
        #                               spectrums[3])

        cc_yz = np.correlate(averages[2], averages[3], mode='full')  # cross
        # -correlation of T1 and FT1
        cc_yz = cc_yz[len(cc_yz) // 2:]
        cc_xy = np.correlate(averages[1], averages[2], mode='full')  #
        # cross-correlation of equator and T1
        cc_xy = cc_xy[len(cc_xy) // 2:]
        cc_xz = np.correlate(averages[1], averages[3], mode='full')  #
        # cross-correlation of equator and FT1
        cc_xz = cc_xz[len(cc_xz) // 2:]

        cc_ft1eq2 = np.correlate(averages[3], averages[5], mode='full')
        cc_ft1eq2 = cc_ft1eq2[len(cc_ft1eq2) // 2:]

        cc_xx2 = np.correlate(averages[1], averages[5], mode='full')
        cc_xx2 = cc_xx2[len(cc_xx2) // 2:]

        crosscorrelations = [[cc_yz], [cc_xy], [cc_xz]]

        time_step = 12.0  # in seconds

        time = np.linspace(0, time_step * len(right_halves[0]),
                           len(right_halves[0]))
        time_raw = np.linspace(0, time_step * len(averages[0]),
                               len(averages[0]))
        N = len(time)

        w = np.linspace(0.0, 1.0 / (2.0 * time_step), len(time) / 2)

        cc_spectrum_yz = np.abs(fft(cc_yz))
        cc_spectrum_xy = np.abs(fft(cc_xy))
        cc_spectrum_xz = np.abs(fft(cc_xz))

        cc_spectrum_ft1eq2 = np.abs(fft(cc_ft1eq2))
        cc_spectrum_xx2 = np.abs(fft(cc_xx2))

        #        fft_yz = scipy.fftpack.fft(right_halves_cc[0])
        #        fft_xy = scipy.fftpack.fft(cc_xy[len(cc_xy)/2:])
        #        fft_xz = scipy.fftpack.fft(cc_xz[len(cc_xz)/2:])
        #
        #        fourier = scipy.fftpack.fft(autocorr_T1[len(
        # autocorr_T1)/2:])

        def nice_label(title):
            if self.option_dictionary['old'] is True:
                return 'Old data ' + str(title)
            else:
                return 'Dataset_' + str(label) + str(' ') + str(title)

        if self.option_dictionary['plot'] == True:
            import matplotlib.pyplot as plt
            plt.close('all')
            #            plt.figure()
            #            plt.loglog(cc_spectrum, 'r')
            #            plt.grid()
            #            plt.title(
            #                nice_label(
            #                    'Power spectral density for T1 and FT1
            # correlations'))
            #            plt.figure()
            #            plt.plot(coherence_, 'k')
            #            plt.title(nice_label('Coherence'))
            subtracted_autoc = right_halves[2] - right_halves[1]
            R_t1t1_spec = np.abs(fft(subtracted_autoc))
            subtracted_autocII = right_halves[3] - right_halves[5]
            R_ft1ft1_spec = np.abs(fft(subtracted_autocII))
            noise_equiv = cc_xy[:-1] - right_halves[1]
            R_t1ft1 = cc_yz - cc_xx2
            R_t1ft1_spec = np.abs(fft(R_t1ft1))

            #            phases_p = PredefinedPlot([angles, 'k'],
            # nice_label(
            # 'phases'))
            #    phases_p.other_function(plt.ylim, ((-2*np.pi, 2*np.pi)))
            autoc_p = PredefinedPlot([time, subtracted_autoc, 'm'],
                                     nice_label(
                                         "autocorr of T1 minus autocorr "
                                         "of eq"))
            t1c_p = PredefinedPlot([time, right_halves[2], 'k'],
                                   nice_label(r'$T_{1}$ autocorrelation'))
            #            gc_p = PredefinedPlot([time, right_halves[0], 'b'],
            #                                  nice_label(r'g
            # autocorrelation'))
            eqc_p = PredefinedPlot([time, right_halves[1], 'g'],
                                   nice_label(r'Equator autocorrelation'))
            ft1c_p = PredefinedPlot([time, right_halves[3], 'k'],
                                    nice_label(r'$FT_{1}$ autocorrelation'))
            eqIIc_p = PredefinedPlot([time, right_halves[5], 'g'],
                                     nice_label(
                                         r'Equator(II) autocorrelation'))
            autocII_p = PredefinedPlot([time, subtracted_autocII, 'm'],
                                       nice_label(
                                           "autocorr of FT1 minus "
                                           "autocorr of "
                                           "eqII"))
            #            g_p = PredefinedPlot([time_raw, averages[0], 'm'],
            #                                 nice_label(r'Raw g_1
            # voltages'))
            eq_p = PredefinedPlot([time_raw, averages[1], 'g'],
                                  nice_label(r'Raw Equator voltages'))
            print(
                'variance of equator:',
                np.sum(averages[1] ** 2) / len(averages[1]))
            t1_p = PredefinedPlot([time_raw, averages[2], 'k'],
                                  nice_label(r'Raw T1 voltages'))
            print(
                'variance of T1:',
                np.sum(averages[2] ** 2) / len(averages[2]))
            ft1_p = PredefinedPlot([time_raw, averages[3], 'b'],
                                   nice_label(r'Raw FT1 voltages'))
            print(
                'variance of FT1:',
                np.sum(averages[3] ** 2) / len(averages[3]))
            #            ft1_p = PredefinedPlot([time_raw, averages[4],
            # 'b'],
            #                                   nice_label(r'Raw g_2
            # voltages'))
            ft1_p = PredefinedPlot([time_raw, averages[5], 'b'],
                                   nice_label(r'Raw eq_2 voltages'))
            print('variance of equatorII:',
                  np.sum(averages[5] ** 2) / len(averages[5]))
            cc_eqt1_p = PredefinedPlot([time_raw, cc_xy, 'b'],
                                       nice_label(
                                           r'Cross-correlation of equator '
                                           r'and '
                                           r'T1'))
            cc_eqft1_p = PredefinedPlot([time_raw, cc_xz, 'b'],
                                        nice_label(
                                            r'Cross-correlation of equator '
                                            r'and FT1'))
            cc_t1ft1_p = PredefinedPlot([time_raw, cc_yz, 'b'],
                                        nice_label(
                                            r'Cross-correlation of T1 and '
                                            r'FT1'))
            cc_ft1eq2_p = PredefinedPlot([time_raw, cc_ft1eq2, 'b'],
                                         nice_label(
                                             r'Cross-correlation of FT1 '
                                             r'and '
                                             r'equatorII'))
            cc_eqeq2_p = PredefinedPlot([time_raw, cc_xx2, 'b'],
                                        nice_label(
                                            r'Cross-correlation of '
                                            r'equator and '
                                            r'equatorII'))
            noise_equiv_p = PredefinedPlot([time, noise_equiv, 'b'],
                                           nice_label(
                                               r'Cross-corr equator T1 '
                                               r'minus '
                                               r'autocorr equator'))
            spec_t1t1_p = PredefinedPlot(
                [w, 2.0 / N * R_t1t1_spec[0:N // 2], 'o'],
                nice_label(r'Spectral density of T1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_ft1ft1_p = PredefinedPlot(
                [w, 2.0 / N * R_ft1ft1_spec[0:N // 2], 'o'],
                nice_label(r'Spectral density of FT1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_eqt1_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_xy[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of equator and T1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_eqft1_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_xz[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of equator and FT1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_t1ft1_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_yz[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of T1 and FT1'))
            plt.yscale('log')
            plt.xscale('log')
            spec_ft1eq2_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_ft1eq2[0:N // 2], 'o'],
                nice_label(r'Cross-spectral density of FT1 and equatorII'))
            plt.yscale('log')
            plt.xscale('log')
            spec_eqeq2_p = PredefinedPlot(
                [w, 2.0 / N * cc_spectrum_xx2[0:N // 2], 'o'],
                nice_label(
                    r'Cross-spectral density of equator and equatorII'))
            plt.yscale('log')
            plt.xscale('log')
            spec_t1ft1_subtr_p = PredefinedPlot(
                [w, 2.0 / N * R_t1ft1_spec[0:N // 2], 'o'],
                nice_label(
                    r'Cross-spectral density of T1 and FT1 (with background '
                    r'subtracted)'))
            plt.yscale('log')
            plt.xscale('log')


# def data_pipeline(DayObject):
#     # The four variables below are 'switches.' plot turns on the plotting
#     # routine. Run runs the routine. averages normalizes some of the cross
#     # correlations. This might not be good depending on how we want to
#     # process this data. Old loads the old data into the proper variables.
#     # I_and_II means the data will be taken from the measurements that end
#     # with I and II. constant means take the data from the constant data; the
#     #  one with no flux in the name. Projections determine whether the data
#     # will be projected on the right axis, AKA T1 onto the line spanned by
#     # |equator> and |g>, and FT1 onto the line spanned by |g_2> and |f>. Mean
#     #  determines whether the data will be averaged, and mean_point_number
#     # determines how many points get averaged together.
#     display()
#     plot = False
#     mean = False
#     run = True
#     average = False
#     old = False
#     I_and_II = True
#     constant = False
#     projections = True
#     mean_point_number = 100
#     if type(mean_point_number) is not int:
#         raise ValueError('Must be an integer.')
#     if constant == I_and_II == old:
#         raise ValueError('Cannot be set at the same time.')
#     if old is False:
#         # Creating the day objects takes very little time. Running the
#         # create_data function is what produces the data and takes so long.
#         CreatedData = DayObject.create_data()
#     label = DayObject.key
#     if run is True:
#         if old is False:
#             if I_and_II is True:
#                 g = CreatedData['I']['g']
#                 g_2 = CreatedData['II']['g']
#                 equator = CreatedData['I']['equator']
#                 equator_2 = CreatedData['II']['equator']
#                 t1 = CreatedData['I']['t1']
#                 ft1 = CreatedData['II']['ft1']
#                 f = CreatedData['II']['f']
#             if constant is True:
#                 g = CreatedData['constant_flux']['g']
#                 g_2 = g
#                 equator = CreatedData['constant_flux']['equator']
#                 equator_2 = equator
#                 t1 = CreatedData['constant_flux']['t1']
#                 ft1 = CreatedData['constant_flux']['ft1']
#                 f = CreatedData['constant_flux']['f']
#
#             if projections is True:
#                 true_t1 = map(lambda x: project(*x), zip(equator, g, t1))
#                 true_ft1 = np.asarray(
#                     map(lambda x: project(*x), zip(f, g_2, ft1)))
#                 true_t1 = np.asarray(true_t1)
#             if projections is False:
#                 true_t1 = t1
#                 true_ft1 = ft1
#             data = list()
#             for i in [g, equator, true_t1, true_ft1, g_2, equator_2]:
#                 if (type(i) == np.ndarray) or (i != None):
#                     i = np.nan_to_num(i)
#                     data.append(i)
#             len_min = min(map(len, data))
#             data = [i[0:len_min] for i in data]
#         else:
#             data = old_data
#             g = data[0]
#             g_2 = g
#             equator = data[1]
#             t1 = data[2]
#             ft1 = data[3]
#         if mean is True:
#             empty_data = []
#             for index, entry in enumerate(data):
#                 splits = np.array_split(entry, (len(entry) /
# mean_point_number))
#                 means = np.asarray(map(np.average, splits))
#                 empty_data.append(means)
#             data = empty_data
#         display()
#
#         ##########################################
#         # Data is now properly prepared for calculations.
#         ##########################################
#
#         directions = g - equator
#         angles = np.angle(directions, deg=True)
#         amplitudes = map(np.absolute, data)
#         averages = map(lambda x: x - np.average(x), amplitudes)
#         if average is True:
#             autocorrelations = map(
#                 lambda x: np.correlate(x, x, mode='full') / np.sum(x ** 2),
#                 averages)
#         else:
#             autocorrelations = map(
#                 lambda x: np.correlate(x, x, mode='full'),
#                 averages)
#
#         display()
#         right_halves = fast_map(right_half, autocorrelations)
#
#         #        cc = np.correlate(averages[2], averages[3], mode='full')
#
#         spectrums = fast_map(fft, right_halves)
#         spectrums = fast_map(np.absolute, spectrums)
#         #        cc_spectrum = fft(cc)
#         #        cc_spectrum = np.absolute(cc_spectrum)
#         #
#         #        coherence_ = coherence(cc_spectrum[0:len(spectrums[2])],
#         # spectrums[2],
#         #                               spectrums[3])
#
#         cc_yz = np.correlate(averages[2], averages[3], mode='full')  # cross
#         # -correlation of T1 and FT1
#         cc_yz = cc_yz[len(cc_yz) // 2:]
#         cc_xy = np.correlate(averages[1], averages[2], mode='full')  #
#         # cross-correlation of equator and T1
#         cc_xy = cc_xy[len(cc_xy) // 2:]
#         cc_xz = np.correlate(averages[1], averages[3], mode='full')  #
#         # cross-correlation of equator and FT1
#         cc_xz = cc_xz[len(cc_xz) // 2:]
#
#         cc_ft1eq2 = np.correlate(averages[3], averages[5], mode='full')
#         cc_ft1eq2 = cc_ft1eq2[len(cc_ft1eq2) // 2:]
#
#         cc_xx2 = np.correlate(averages[1], averages[5], mode='full')
#         cc_xx2 = cc_xx2[len(cc_xx2) // 2:]
#
#         crosscorrelations = [[cc_yz], [cc_xy], [cc_xz]]
#
#         time_step = 12.0  # in seconds
#
#         time = np.linspace(0, time_step * len(right_halves[0]),
#                            len(right_halves[0]))
#         time_raw = np.linspace(0, time_step * len(averages[0]),
#                                len(averages[0]))
#         N = len(time)
#
#         w = np.linspace(0.0, 1.0 / (2.0 * time_step), len(time) / 2)
#
#         cc_spectrum_yz = np.abs(fft(cc_yz))
#         cc_spectrum_xy = np.abs(fft(cc_xy))
#         cc_spectrum_xz = np.abs(fft(cc_xz))
#
#         cc_spectrum_ft1eq2 = np.abs(fft(cc_ft1eq2))
#         cc_spectrum_xx2 = np.abs(fft(cc_xx2))
#
#         #        fft_yz = scipy.fftpack.fft(right_halves_cc[0])
#         #        fft_xy = scipy.fftpack.fft(cc_xy[len(cc_xy)/2:])
#         #        fft_xz = scipy.fftpack.fft(cc_xz[len(cc_xz)/2:])
#         #
#         #        fourier = scipy.fftpack.fft(autocorr_T1[len(autocorr_T1)/2:])
#
#         def nice_label(title):
#             if old is True:
#                 return 'Old data ' + str(title)
#             else:
#                 return 'Dataset_' + str(label) + str(' ') + str(title)
#
#         if plot == True:
#             import matplotlib.pyplot as plt
#             plt.close('all')
#             #            plt.figure()
#             #            plt.loglog(cc_spectrum, 'r')
#             #            plt.grid()
#             #            plt.title(
#             #                nice_label(
#             #                    'Power spectral density for T1 and FT1
#             # correlations'))
#             #            plt.figure()
#             #            plt.plot(coherence_, 'k')
#             #            plt.title(nice_label('Coherence'))
#             subtracted_autoc = right_halves[2] - right_halves[1]
#             R_t1t1_spec = np.abs(fft(subtracted_autoc))
#             subtracted_autocII = right_halves[3] - right_halves[5]
#             R_ft1ft1_spec = np.abs(fft(subtracted_autocII))
#             noise_equiv = cc_xy[:-1] - right_halves[1]
#             R_t1ft1 = cc_yz - cc_xx2
#             R_t1ft1_spec = np.abs(fft(R_t1ft1))
#
#             #            phases_p = PredefinedPlot([angles, 'k'], nice_label(
#             # 'phases'))
#             #    phases_p.other_function(plt.ylim, ((-2*np.pi, 2*np.pi)))
#             autoc_p = PredefinedPlot([time, subtracted_autoc, 'm'],
# nice_label(
#                 "autocorr of T1 minus autocorr of eq"))
#             t1c_p = PredefinedPlot([time, right_halves[2], 'k'],
#                                    nice_label(r'$T_{1}$ autocorrelation'))
#             #            gc_p = PredefinedPlot([time, right_halves[0], 'b'],
#             #                                  nice_label(r'g
# autocorrelation'))
#             eqc_p = PredefinedPlot([time, right_halves[1], 'g'],
#                                    nice_label(r'Equator autocorrelation'))
#             ft1c_p = PredefinedPlot([time, right_halves[3], 'k'],
#                                     nice_label(r'$FT_{1}$ autocorrelation'))
#             eqIIc_p = PredefinedPlot([time, right_halves[5], 'g'],
#                                      nice_label(r'Equator(II)
# autocorrelation'))
#             autocII_p = PredefinedPlot([time, subtracted_autocII, 'm'],
#                                        nice_label(
#                                            "autocorr of FT1 minus autocorr
# of "
#                                            "eqII"))
#             #            g_p = PredefinedPlot([time_raw, averages[0], 'm'],
#             #                                 nice_label(r'Raw g_1 voltages'))
#             eq_p = PredefinedPlot([time_raw, averages[1], 'g'],
#                                   nice_label(r'Raw Equator voltages'))
#             print(
#             'variance of equator:', np.sum(averages[1] ** 2) / len(
# averages[1]))
#             t1_p = PredefinedPlot([time_raw, averages[2], 'k'],
#                                   nice_label(r'Raw T1 voltages'))
#             print(
#             'variance of T1:', np.sum(averages[2] ** 2) / len(averages[2]))
#             ft1_p = PredefinedPlot([time_raw, averages[3], 'b'],
#                                    nice_label(r'Raw FT1 voltages'))
#             print(
#             'variance of FT1:', np.sum(averages[3] ** 2) / len(averages[3]))
#             #            ft1_p = PredefinedPlot([time_raw, averages[4], 'b'],
#             #                                   nice_label(r'Raw g_2
# voltages'))
#             ft1_p = PredefinedPlot([time_raw, averages[5], 'b'],
#                                    nice_label(r'Raw eq_2 voltages'))
#             print('variance of equatorII:',
#                   np.sum(averages[5] ** 2) / len(averages[5]))
#             cc_eqt1_p = PredefinedPlot([time_raw, cc_xy, 'b'],
#                                        nice_label(
#                                            r'Cross-correlation of equator
# and '
#                                            r'T1'))
#             cc_eqft1_p = PredefinedPlot([time_raw, cc_xz, 'b'],
#                                         nice_label(
#                                             r'Cross-correlation of equator '
#                                             r'and FT1'))
#             cc_t1ft1_p = PredefinedPlot([time_raw, cc_yz, 'b'],
#                                         nice_label(
#                                             r'Cross-correlation of T1 and
# FT1'))
#             cc_ft1eq2_p = PredefinedPlot([time_raw, cc_ft1eq2, 'b'],
#                                          nice_label(
#                                              r'Cross-correlation of FT1 and '
#                                              r'equatorII'))
#             cc_eqeq2_p = PredefinedPlot([time_raw, cc_xx2, 'b'],
#                                         nice_label(
#                                             r'Cross-correlation of equator
# and '
#                                             r'equatorII'))
#             noise_equiv_p = PredefinedPlot([time, noise_equiv, 'b'],
#                                            nice_label(
#                                                r'Cross-corr equator T1 minus '
#                                                r'autocorr equator'))
#             spec_t1t1_p = PredefinedPlot(
#                 [w, 2.0 / N * R_t1t1_spec[0:N // 2], 'o'],
#                 nice_label(r'Spectral density of T1'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_ft1ft1_p = PredefinedPlot(
#                 [w, 2.0 / N * R_ft1ft1_spec[0:N // 2], 'o'],
#                 nice_label(r'Spectral density of FT1'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_eqt1_p = PredefinedPlot(
#                 [w, 2.0 / N * cc_spectrum_xy[0:N // 2], 'o'],
#                 nice_label(r'Cross-spectral density of equator and T1'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_eqft1_p = PredefinedPlot(
#                 [w, 2.0 / N * cc_spectrum_xz[0:N // 2], 'o'],
#                 nice_label(r'Cross-spectral density of equator and FT1'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_t1ft1_p = PredefinedPlot(
#                 [w, 2.0 / N * cc_spectrum_yz[0:N // 2], 'o'],
#                 nice_label(r'Cross-spectral density of T1 and FT1'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_ft1eq2_p = PredefinedPlot(
#                 [w, 2.0 / N * cc_spectrum_ft1eq2[0:N // 2], 'o'],
#                 nice_label(r'Cross-spectral density of FT1 and equatorII'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_eqeq2_p = PredefinedPlot(
#                 [w, 2.0 / N * cc_spectrum_xx2[0:N // 2], 'o'],
#                 nice_label(r'Cross-spectral density of equator and
# equatorII'))
#             plt.yscale('log')
#             plt.xscale('log')
#             spec_t1ft1_subtr_p = PredefinedPlot(
#                 [w, 2.0 / N * R_t1ft1_spec[0:N // 2], 'o'],
#                 nice_label(
#                     r'Cross-spectral density of T1 and FT1 (with background
#  subtracted)'))
#             plt.yscale('log')
#             plt.xscale('log')
#
#
# data_pipeline(first_day)
test = DataPipeLineCallableClass('I_and_II', preliminary_option_dict)
test(first_day)
