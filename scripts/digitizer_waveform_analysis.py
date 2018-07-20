# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from DaqBufferExample import digitizer_capture
import numpy as np

plt.close('all')


def numpy_array_map(func, iterable):
    return np.asarray(map(func, iterable))


def _range_(n):
    return range(0, len(n))

#object to make plotting easier.
class PlotObject(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        import matplotlib.pyplot as plt
        plt.figure()
        plt.grid()
        plt.plot(*args)
        if 'others' in kwargs:
            plt.plot(*kwargs['others'])
        if 'titles' in kwargs:
            self.titles = kwargs['titles']
            plt.title(self.titles[0])
            plt.xlabel(self.titles[1])
            plt.ylabel(self.titles[2])


points_per_cycle = 4000
captures = 10000
data = digitizer_capture([points_per_cycle, captures, 20])

ch1 = data[0]
ch2 = data[1]
ch3 = data[2]
ch4 = data[3]
from scipy.integrate import simps
#Split the big array of data into each capture. Ch2 gets split because that
# channel was actually plugged in.
capture_cycles = np.split(ch2, captures)

#Use the simpson method to integrate the resulting captures. The theory is
# that if there is a waveform out of place, the area under that Gaussian will
#  be different, and it should be obvious that the digitizer dropped a wave.
integrations = map(simps, capture_cycles)
integrations = np.asarray(integrations)
from scipy.optimize import curve_fit


def linear(x, a, b):
    return a * x + b
#Plotting the integrations, its clear that there are 'bands' where the
# integrations of the waves fall. How can it be shown that one of the waves
# jumped out of order? Fit a line to the sequence of integrations and look at
#  the fitted parameters. If a wave jumped out of place, it would be clear
# that a wave is out of place.

wave_regions = np.split(integrations, captures / 10)
# plt.plot(integrations, 'bo')
fits = map(lambda x: curve_fit(linear, _range_(x), x), wave_regions)

coefficents = numpy_array_map(lambda x: x[0], fits)
a_coefficent = coefficents[..., 0]
b_coefficent = coefficents[..., 1]
plt.grid()
plt.title('Coefficents for parameters for linear fits')
plt.plot(a_coefficent, 'r*')
plt.plot(b_coefficent, 'bo')











