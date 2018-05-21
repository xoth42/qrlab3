import sys
import numpy as np
import scipy as sc
import scipy.signal as signal
import copy
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
sys.path.append('Z:\\kchou\\_CodeRoutines\\Python\\General Tools')
from lmfit import minimize, Parameters, Parameter, fit_report, report_fit


'''
    Function fitting with lmfit Python package
        (http://cars9.uchicago.edu/software/python/lmfit/index.html)

        currently supported:
        - Polynomial
        - Lorentzian
        - Sine
'''

# TODO fit with error bounds

def generate_fit_ydata(x_data, fit_params, function):
    '''
        generate fit data with a more dense x-range (factor of 10)
    '''
    x_start = x_data[0]
    x_end = x_data[-1]
    x_num_pts = len(x_data)

    # create new x_scale assuming linearly spaced
    multiplier = 10
    new_x_data = np.linspace(x_start, x_end, x_num_pts * multiplier)

    # generate y data
    new_y_data = function(new_x_data)

    return new_x_data, new_y_data

def calc_norm_redchi(y_data, y_fit):
    '''
        calculated the Pearson's chi-squared value of a fit
    '''

    return np.sum((y_data - y_fit)**2 / y_fit)


def fit_plot(x_data, y_data, residuals, x_fit=None, y_fit=None, figure_no=None):
    final = y_data + residuals
    perc_err = residuals / y_data * 100.0

    if figure_no is not None:
        plt.figure(figure_no, figsize=(8,5), facecolor='w', edgecolor='w')

    gs = GridSpec(4, 1)
    ax_residual = plt.subplot(gs[0, :])
    ax_data = plt.subplot(gs[1:4, :])

    ax_data.plot(x_data, y_data, 'ro-')
    if x_fit is None and y_fit is None:
        ax_data.plot(x_data, final, 'k')
    else:
        ax_data.plot(x_fit, y_fit, 'k-')

    ax_residual.plot(x_data, perc_err, 'ko')
    ax_residual.set_ylabel('% error')
    ax_residual.xaxis.set_ticklabels([])

    plt.tight_layout()

def report_fit_params(params):
    report_fit(params)

def plot_2d(x_data, y_data, z_data, figure_no=1, replot=False,
            plot_type='pcolor', show=False, color='jet'):
    '''
        For 2D data (x, y, z), specify.
        x_data and y_data are 1D arrays that specify the axes range
    '''
    if replot:
        plt.close(figure_no)

    plt.figure(figure_no, figsize=(7, 5), facecolor='w', edgecolor='w')

    if plot_type=='pcolor':
        xx_pcolor, yy_pcolor = set_2Daxes_pcolor(x_data, y_data)
        plt.pcolor(xx_pcolor, yy_pcolor, np.transpose(z_data),
                   vmax=np.nanmax(z_data), vmin=np.nanmin(z_data),
                    cmap=color)
        plt.colorbar()
    elif plot_type=='contour':
        c_plot = plt.contour(x_data, y_data, z_data, colors='k', linewidths=2)
        plt.clabel(c_plot, inline=1, fontsize=12)
    plt.tight_layout()
    if show:
        plt.show()

def find_min_max(data):

    min_series = []
    max_series = []
    for series in data:
        min_series = series.min


def set_2Daxes_pcolor(x_data, y_data):
    '''
        x_data and y_data are 1D arrays specifying the mesh.
    '''
    # adjust the 1D range by adding another element and shifting by half a period
    dx = x_data[-1] - x_data[-2]
    x_range = np.concatenate((x_data, [x_data[-1] + dx]))
    x_range = x_range - dx/2.0

    dy = y_data[-1] - y_data[-2]
    y_range = np.concatenate((y_data, [y_data[-1] + dy]))
    y_range = y_range - dy/2.0

    # generate mesh
    return np.meshgrid(x_range, y_range)



#def set_2Daxes_pcolor(xx_ranges, yy_ranges):
#    # for x axis, first add another row and transpose
##    x_st = np.transpose(np.concatenate((xx_ranges, np.array([xx_ranges[0]]))))
##    delta = x_st[1] - x_st[0]
##    # subtract by half the difference and add an additional row of elements
##    x_pcolor = np.transpose(np.concatenate((x_st - delta / 2.0,
##                                           np.array([x_st[-1] + delta / 2.0]))))
#    # assume xx_ranges data are spaced evenly
#    xx_ranges = np.transpose(xx_ranges)
#    dx = xx_ranges[-1] - xx_ranges[-2]
#    x_st = np.concatenate((xx_ranges, np.array([xx_ranges[-1] + dx])))
#    print x_st
#    x_pcolor = x_st - dx/2.0
#    x_pcolor = np.transpose(x_pcolor)
#    print x_pcolor
#
#    # assume yy_ranges data are spaced evenly
#    dy = yy_ranges[-1] - yy_ranges[-2]
#    y_st = np.concatenate((yy_ranges, np.array([yy_ranges[-1] + dy])))
#    y_pcolor = y_st - dy/2.0
#    print y_pcolor
#
#    # for y axis, first add another row
##    yy_transpose = np.transpose(yy_ranges)
##    y_st = np.transpose(np.concatenate((yy_transpose, np.array([yy_transpose[0]]))))
##    delta = y_st[1] - y_st[0]
##    # subtract by half the difference and add an additional row of elements
##    y_pcolor = np.concatenate((y_st - delta / 2.0,
##                               np.array([y_st[-1] + delta / 2.0])))
#
#    return x_pcolor, y_pcolor

def find_peaks(y_data, plot=True, width_frac=4, min_length_frac=4):
    # TODO this is a general function, so place elsewhere
    # TODO figure out how to determine peak positions when
    # two are close together

    # define transform widths to be 1/4 of total length of array
    widths = np.arange(1, len(y_data)/width_frac)
    cwt_mat = sc.signal.cwt(y_data, signal.ricker, widths)
    if plot:
        plt.pcolor(cwt_mat)
        plt.show()

    # here we pick peaks to have ridge lengths at least 1/<min_len_frac>
    # of the length of our cwt widths
    peak_indices = signal.find_peaks_cwt(y_data, widths,
                                 min_length=len(widths)/min_length_frac)

    return peak_indices

#==============================================================================
# Functions
#==============================================================================

parameter_keys = ('name', 'value', 'vary', 'min', 'max', 'expr')

class Function(object):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        '''
        Specification for general functions. When defining a new function,
        implement the function() method.
        This class will serve two purposes: for defining ideal value

        Arguments:
         x_data
         y_data
         parmams_list: write in the form specified by the Parameters class

        '''
        self._xdata = np.array(x_data)
        self._ydata = np.array(y_data)
#        self.params_list = params_list # this is a temporary variable
        if x_data is None and y_data is not None:
            self._xdata = np.arange(len(y_data))
        try:
            # see if the child function has defined param_names,
            # if so, then do nothing
            self.param_names
        except:
            # if not defined, then set to None
            self.param_names = None # this should be specified in specific function
        self._params = Parameters()   # start with an empty Parameters object()

        # make a Parameters list object associated with function
        self.set_parameters(params_list)


    def set_parameters(self, params_list):
        '''
            Input parameters in the form of a tuple:
               ('name', value, vary, min, max, 'expr')

             Only 'name' and value are required, if the others are unspecified
             then the defaults are vary=True, min=None, max=None, 'expr'=None

             If they are specified, then all optional parameters must be specified
        '''

        # TODO: make a check that no new parameters are added?
        self._params = Parameters()
        if params_list is not None and not isinstance(params_list, Parameters):
            for param in params_list:
                if len(param) == 1:
                    # add only name - this should only be used by the initialization
                    self._params.add(param[0])
                elif len(param) == 2:
                    # name and value are specified
                    self._params.add(param[0], value=param[1])
                elif len(param) == 6:
                    self._params.add(param[0], value=param[1], vary=param[2],
                                     min=param[3], max=param[4], expr=param[5])
                else:
                    print 'error - set_parameters(): bad parameter list %s' % param
        elif isinstance(params_list, Parameters):
            self._params = copy.deepcopy(params_list)
        else:
#            print 'error - set_parameters(): params_list is NoneType'
#             use the defined determine_initial_params()
            self._params = self.determine_initial_params()



    def update_parameters(self, param_name, **kwargs):
        '''
            name the parameter and add on a keyword list of settings
            according to the Parameter class construction

            TODO this needs to make sure not too add any new parameters
        '''
        try:
            # check if the parameter name exists
            self._params.keys().index(param_name)

            # move through keyword argument list and add parameters
            for key, value in kwargs.iteritems():
                try:
                    self._params.add(param_name, key=value)
                except TypeError:
                    print 'Function.update_parameter(): bad keyword argument'
        except ValueError:
            print 'Function.update_parameter(): parameter does not exist'

    def get_parameter_names(self):
        return self.param_names

    def get_parameters_obj(self):
        return self._params

    def get_xdata(self):
        return self._xdata

    def get_ydata(self):
        return self._ydata

    def print_parameters(self):

        msg = ''
        for name in self.param_names:
            msg += str(name) +  ': \t'
            msg += 'value = ' + str(self._params[name].value) + '\t'
            msg += 'vary = ' + str(self._params[name].vary) + '\t'
            msg += 'min = ' + str(self._params[name].min) + '\t'
            msg += 'max = ' + str(self._params[name].max) + '\t'
            msg += 'expr = ' + str(self._params[name].expr) + '\t'
            msg += '\n'
        print msg

    def func(self, x_data):
        '''
            Define in specific Function classes
        '''
        pass

    def function(self, x_data, set_ydata=False):
        '''
            returns an array of y_data with the option of setting the object's
            _ydata
        '''

        if self._params is None:
            print 'Function.get_value(): parameters are not specified'
            return

        temp = self.func(x_data)
        if set_ydata:
            self._ydata = temp
        return temp


    def determine_initial_params(self):
        '''
            Define in specific classes. Specify initial conditions
        '''
        return None

    def residual(self, params, x_data, y_data):
        '''
            Define objective function: function to be minimized
        '''

        return self.function(x_data) - y_data

    def fit(self, y_data=None, plot=True, method='leastsq'):
        '''
            Fitting function - uses the lmfit package to perform the fit.
            Fit outcome is not applied to the object after the minimization.

            optional arguments:
              y_data: set temporary y_data to use for fit. This will also
                  update the stored y_data parameter for the object--i.e. this
                  is not temporary.
              fit_alg: pass the method argument of a particular fitting method
                   to the minimize() function.
                   Options: Levenberg_Marquardt (leastsq), Nelder-Mead (nelder)
                      L-BFGS-B (lbfgsb), Simulated Annealing (anneal),
                      Powell (powell), conjugate Gradient (cg),
                      Newtown-CG (newton), COBYLA (cobyla),
                      Sequential Linear Square Programming (slsqp)
        '''
        temp_params = self._params

        # allow for user defined data sets
        if y_data is not None:
            self._ydata = y_data
        result = minimize(self.residual, temp_params,
                          args=(self.get_xdata(),  self.get_ydata()),
                          method=method)

        x_fit, y_fit = generate_fit_ydata(self.get_xdata(), temp_params, self.function)

        y_final = self._ydata + result.residual
#        self._params = temp_params # this might be a problem,
        # as calling function() will update self._ydata

        if plot:
            fit_plot(self._xdata, self._ydata, result.residual,
                     x_fit=x_fit, y_fit=y_fit)

        return result, temp_params, y_final




#TODO write a check function for proper parameters
#==============================================================================
#  Specific functions
#==============================================================================

class Polynomial(Function):

    def __init__(self, x_data=None, y_data=None, order=None, params_list=None):
        '''
            Polynomial fit up to 9th order:

            a + b * x + c * x**2 + d * x**3 + e * x**4 + ... + h * x*9
        '''

        tmp_max_order = 9
        if order is None or order > 9:
            self._order = tmp_max_order
        else:
            self._order = order


        self.param_names = ['zero', 'one', 'two', 'three', 'four', 'five',
                            'six', 'seven', 'eight', 'nine']

        Function.__init__(self, x_data=x_data, y_data=y_data, params_list=params_list)
        # TODO: robust method for specifying subset
        # extend and overwrite the parent class


        # let's keep all orders available for quick fit changing
#        if order is None:
#            # max order
#            self._order = len(self.param_names) - 1
#        else:
#
#        print self._params

    def func(self, x_data):
        if self._params is not None:
#                a = self._params['zero'].value
#                b = self._params['one'].value
#                c = self._params['two'].value
#                d = self._params['three'].value
#                e = self._params['four'].value
#                f = self._params['five'].value
#                g = self._params['six'].value
#                h = self._params['seven'].value
#                i = self._params['eight'].value
#                j = self._params['nine'].value

                # only define function up to specified order
            tmp_param_names = self.param_names[0:(self._order + 1)]

            val = 0
            for n, name in enumerate(tmp_param_names):
                val += self._params[name].value * x_data**n
            return val
    #                return a + b * x_data + c * x_data**2 + d * x_data**3 + \
    #                        e * x_data**4 + f * x_data**5 + g * x_data**6 + \
    #                        h * x_data**7 + i * x_data**8 + j * x_data**9

    def determine_initial_params(self):
        '''
            Specifies parameters up to the order n
        '''

        #TODO determine a smart way to determine initial parameters
        #  take repeated derivatives
        params = Parameters()
        tmp_param_names = self.param_names[0:self._order + 1]
        tmp_fixed_param_names = self.param_names[self._order+1:len(self.param_names)]

        # set non-fixed values
        for n, name in enumerate(tmp_param_names):
            params.add(name, 1.0, vary=True)

        for n, name in enumerate(tmp_fixed_param_names):
            params.add(name, 0.0, vary=False)

        return params



class Lorentzian(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        # initialize parameter list to contain the names
        # I think this is unnecessary, since the __init__ calculates an initial
        # set of parameters, so self._params is defined there.
#        if params_list is None:
#            params_list = (('amplitude',), ('position',), ('width',), ('offset',))

        Function.__init__(self, x_data=x_data, y_data=y_data, params_list=params_list)

        # overwrite the parent class
        self.param_names = ['amplitude', 'position', 'offset', 'width']

    def func(self, x_data):

        if self._params is not None:
            offset      = self._params['offset'].value
            a           = self._params['amplitude'].value
            x0          = self._params['position'].value
            b           = self._params['width'].value
#
            return offset + a / ((x_data - x0)**2 + b**2)
        else:
            return None

    def determine_initial_params(self):
        '''
            for fitting lorentzians
        '''
        # setup initial parameters
        if self._ydata is None:
            # TODO is this the right construction?
            # if no y data specified, then set default parameters
            params = Parameters()
            params.add('amplitude',     value=1.0)
            params.add('position',      value=1.0)
            params.add('width',         value=1.0, min=0) # 1 period
            params.add('offset',        value=1.0)

            return params

        ave = sc.mean(self._ydata)
        if abs(max(self._ydata) - ave) > abs(min(self._ydata) - ave):
            # we expect a peak
#            peak_indices = find_peaks(self._ydata, width_frac=3, min_length_frac=2)
#            print peak_indices
            initial_position = self._xdata[(np.abs(self._ydata - max(self._ydata))).argmin()]
            initial_position = self._xdata[np.where(self._ydata==np.max(self._ydata))[0][0]]
            initial_offset = min(self._ydata)

            # estimate FWHM
            temp_amp = max(self._ydata) - initial_offset
            half_max = initial_offset + temp_amp / 2.0
            above_half_max = np.where(self._ydata - half_max >= 0.0)[0]
            initial_width = np.abs(self._xdata[above_half_max[-1]] -
                                   self._xdata[above_half_max[0]])/2.0

            # estimate amplitude: (ymax - offset) * B^2
            initial_amp = (max(self._ydata) - initial_offset) * initial_width**2

#            print initial_amp, initial_position, initial_width, initial_offset
        else:
            # we expect a dip
            initial_position = self._xdata[(np.abs(self._ydata - min(self._ydata))).argmin()]
            initial_offset = max(self._ydata)

            # estimate FWHM
            half_max = initial_offset / 2.0 + min(self._ydata) / 2.0
            
            above_half_max = np.where(self._ydata - half_max <= 0.0)[0]
            initial_width = np.abs(self._xdata[above_half_max[-1]] -
                                   self._xdata[above_half_max[0]])/2.0
            # estimate amplitude: (ymin - offset) * B^2\
            initial_amp = (min(self._ydata) - initial_offset) # * initial_width**2

        params = Parameters()
        params.add('amplitude',     value=initial_amp)
        params.add('position',      value=initial_position)
        params.add('width',         value=initial_width, min=0)
        params.add('offset',        value=initial_offset)

        return params

class Sine(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None,
                 constrain_pos_amp = False):
        '''
            Simple Sine fit function: y = offset + amp * sin(2 * pi * (f * x _ phi))
        '''

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)
        # overwrite the parent class  param_names
        self.param_names = ['amplitude', 'frequency', 'phase', 'offset']

    def func(self, x_data):

        if self._params is not None:
            a           = self._params['amplitude'].value
            f           = self._params['frequency'].value
            p           = self._params['phase'].value
            offset      = self._params['offset'].value

            return offset + a * np.sin(2 * np.pi * (f * x_data + p))
        else:
            return None

    def determine_initial_params(self):
        '''
            for fitting sines
        '''
        initial_amp = (max(self._ydata) -  min(self._ydata)) / 2.0
        initial_offset = (max(self._ydata) + min(self._ydata)) / 2.0
        initial_phase = 0.5  # how do I do this intelligently?

        # determine initial freq from fft
        dt = self._xdata[1] - self._xdata[0]
        temp_ydata = self._ydata - initial_offset # remove offset for fft
        fft_freqs = np.fft.fftfreq(len(self._ydata), d=dt)
        fft_amp = list(np.abs(np.fft.fft(temp_ydata))) # want to use index() function in list

#        plt.plot(fft_freqs, fft_amp)
#        plt.show()

        initial_freq = np.abs(fft_freqs[fft_amp.index(max(fft_amp))])

        params = Parameters()

        params.add('amplitude',    value=initial_amp)
        #params.add('amplitude',    value=initial_amp)
        params.add('frequency',    value=initial_freq)
        params.add('phase',        value=initial_phase, min=0, max=1) # 1 period
        params.add('offset',       value=initial_offset)

        return params

class Exp(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        '''
            Simple decay fit function: y = offset + amp * exp(-t/tau)
        '''

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

        # overwrite the parent class  param_names
        self.param_names = ['amplitude', 'time_constant', 'offset']

    def func(self, x_data):
        if self._params is not None:
            a           = self._params['amplitude'].value
            tau           = self._params['time_constant'].value
            offset      = self._params['offset'].value

            return offset + a * np.exp(-x_data / tau)
        else:
            return None

    def determine_initial_params(self):
        '''
            for fitting decaying exp
        '''

        initial_amp = np.max(self._ydata) - np.min(self._ydata)
        initial_offset = np.average(self._ydata)


        # TODO fix polynomial estimation code.
        # fit to a line
#        log_offset_ydata = np.log(np.abs(self._ydata - initial_offset))
#        p = Polynomial(x_data=self._xdata, y_data=log_offset_ydata, order=1, params_list=None)
#        result, params, y_final = p.fit(plot=True)
#        print ' ------'
#        report_fit(params)
#        print ' -----'
#        initial_tau = np.abs(params['one'].value)


        initial_tau = 3.0

        params = Parameters()
        params.add('amplitude',         value=initial_amp)
        params.add('time_constant',     value=initial_tau)
        params.add('offset',            value=initial_offset)

        return params

class SinExp(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        '''
            Exponential modulated sine:
            y = offset + amp * (exp(-t/tau) * sine(2 * pi * f * (x + phi)))
        '''

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

        # overwrite the parent class  param_names
        self.param_names = ['amplitude', 'frequency', 'phase', 'time_constant', 'offset']

    def func(self, x_data):
        if self._params is not None:
            a           = self._params['amplitude'].value
            freq        = self._params['frequency'].value
            phase       = self._params['phase'].value
            tau         = self._params['time_constant'].value
            offset      = self._params['offset'].value

            return offset + a * (np.exp(-x_data / tau) * \
                            np.sin(2 * np.pi * (freq * x_data + phase)))
        else:
            return None

    def determine_initial_params(self):
        '''
            for fitting decaying exp
        '''

                # TODO fix polynomial estimation code.
        initial_amp = np.max(self._ydata) - np.min(self._ydata)
        initial_offset = np.average(self._ydata)
        initial_tau = 2.0
        initial_phase  = 0.5

        # determine initial freq from fft
        dt = self._xdata[1] - self._xdata[0]
        temp_ydata = self._ydata - initial_offset # remove offset for fft
        fft_freqs = np.fft.fftfreq(len(self._ydata), d=dt)
        fft_amp = list(np.abs(np.fft.fft(temp_ydata))) # want to use index() function in list

#        plt.plot(fft_freqs, fft_amp)
#        plt.show()

        initial_freq = np.abs(fft_freqs[fft_amp.index(max(fft_amp))])

        params = Parameters()
        params.add('amplitude',         value=initial_amp)
        params.add('frequency',         value=initial_freq)
        params.add('phase',             value=initial_phase)
        params.add('time_constant',     value=initial_tau)
        params.add('offset',            value=initial_offset)

        return params

class CoherentState_Decay(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        '''
            coherent state decay (n = 0):
            y = offset + amp * exp(-n0 * exp(-t/tau))
        '''

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

        # overwrite the parent class  param_names
        self.param_names = ['amplitude',
                            'nbar',
                            'time_constant',
                            'offset']

    def func(self, x_data):
        if self._params is not None:
            a           = self._params['amplitude'].value
            nbar        = self._params['nbar'].value
            tau         = self._params['time_constant'].value
            offset      = self._params['offset'].value

            return offset + a * np.exp(-nbar * np.exp(-x_data / tau))
        else:
            return None

    def determine_initial_params(self):

        initial_amp = np.max(self._ydata) - np.min(self._ydata)
        initial_offset = np.average(self._ydata)
        initial_nbar = 10.0
        initial_tau  = 10.0

        params = Parameters()
        params.add('amplitude',         value=initial_amp)
        params.add('nbar',              value=initial_nbar)
        params.add('time_constant',     value=initial_tau)
        params.add('offset',            value=initial_offset)

        return params

class Gaussian(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        '''
            Simple decay fit function:
            y = offset + amp / (sigma * sqrt(2 * pi)) * exp(-(x-x0)^2/(2 * sigma**2))
        '''

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

        # overwrite the parent class  param_names
        self.param_names = ['amplitude', 'position', 'sigma', 'offset']

    def func(self, x_data):
        if self._params is not None:
            a               = self._params['amplitude'].value
            x0              = self._params['position'].value
            sigma           = self._params['sigma'].value
            offset          = self._params['offset'].value

            return offset + a / (sigma * np.sqrt(2 * np.pi)) * \
                        np.exp(- (x_data - x0)**2 / (2.0 * sigma**2))
        else:
            return None

    def determine_initial_params(self):
        # setup initial parameters
        if self._ydata is None:
            # TODO is this the right construction?
            # if no y data specified, then set default parameters
            params = Parameters()
            params.add('amplitude',     value=1.0)
            params.add('position',      value=1.0)
            params.add('offset',        value=1.0)
            params.add('sigma',         value=1.0, min=0)

            return params

        ave = sc.mean(self._ydata)
        if abs(max(self._ydata) - ave) > abs(min(self._ydata) - ave):
            # we expect a peak
#            peak_indices = find_peaks(self._ydata, width_frac=3, min_length_frac=2)
#            print peak_indices
            initial_position = self._xdata[(np.abs(self._ydata - max(self._ydata))).argmin()]
            initial_offset = min(self._ydata)

            # estimate FWHM
            temp_amp = max(self._ydata) - initial_offset
            half_max = initial_offset + temp_amp / 2.0
            above_half_max = np.where(self._ydata - half_max >= 0.0)[0]
            initial_width = np.abs(self._xdata[above_half_max[-1]] -
                                   self._xdata[above_half_max[0]])/2.0

            # estimate amplitude: (ymax - offset) * B^2
            initial_amp = (max(self._ydata) - initial_offset) * initial_width**2

#            print initial_amp, initial_position, initial_width, initial_offset
        else:
            # we expect a dip
            initial_position = self._xdata[(np.abs(self._ydata - min(self._ydata))).argmin()]
            initial_offset = max(self._ydata)

            # estimate FWHM
            half_max = initial_offset + min(self._ydata) / 2.0
            above_half_max = np.where(self._ydata - half_max <= 0.0)[0]
            initial_width = np.abs(self._xdata[above_half_max[-1]] -
                                   self._xdata[above_half_max[0]])/2.0
            # estimate amplitude: (ymin - offset) * B^2
            initial_amp = (min(self._ydata) - initial_offset) * initial_width**2

        params = Parameters()
        params.add('amplitude',     value=initial_amp)
        params.add('position',      value=initial_position)
        params.add('offset',        value=initial_offset)
        params.add('sigma',         value=initial_width, min=0)
        return params

class ErrorFunction(Function):

    def __init__(self, x_data=None, y_data=None, params_list=None):
        '''
            Error function fitting function
            sc.special.erf: 2/sqrt(pi)*integral(exp(-t**2), t=0..z).

            y = o + a * erf(b(x-x0))
        '''

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

        # overwrite the parent class  param_names
        self.param_names = ['amplitude', 'x_scale', 'position', 'offset']

    def func(self, x_data):
        if self._params is not None:
            a                   = self._params['amplitude'].value
            b                   = self._params['x_scale'].value
            x0                  = self._params['position'].value
            offset              = self._params['offset'].value

            return offset + a * sc.special.erf(b * (x_data - x0))
        else:
            return None

    def determine_initial_params(self):

        initial_offset = np.average(self._ydata)
        initial_amp = max(self._ydata) - min(self._ydata)
        initial_position = -25.0
        initial_xscale = .001

        params = Parameters()
        params.add('amplitude',         value=initial_amp)
        params.add('position',          value=initial_position)
        params.add('x_scale',           value=initial_xscale)
        params.add('offset',            value=initial_offset)

        return params


class Poisson(Function):

    def __init__(self, x_data=None, y_data=None, fix_n=None, params_list=None):
        '''
            Poisson fitting function
            P(n|n_bar) = amp * exp(-alpha) * (alpha)**(-2n)/sqrt(n!) + offset
        '''
        self.fix_n = fix_n

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

        # overwrite the parent class  param_names
        self.param_names = ['amplitude', 'n', 'alpha_scale', 'offset']

    def func(self, x_data):
        if self._params is not None:
            a                   = self._params['amplitude'].value
            n                   = self._params['n'].value
            alpha_scale         = self._params['alpha_scale'].value
            offset              = self._params['offset'].value

            return offset + a * np.exp(-(x_data/alpha_scale)**2) * \
                        (x_data/alpha_scale)**(2*n) / sc.misc.factorial(n)
        else:
            return None

    def determine_initial_params(self):
        '''
            for fitting decaying exp
        '''

        # TODO corner case: n = 0, this is not true
        initial_offset = self._ydata[-1] # alpha = 0, only get offset (ideally)
        initial_amp = max(self._ydata) - min(self._ydata)
        # TODO initial amp is bad
        initial_n = 1.0
        vary_n = True
        if self.fix_n is not None:
            initial_n = self.fix_n
            vary_n = False

        initial_alpha_scale = 0.01

        params = Parameters()
        params.add('amplitude',         value=initial_amp)
        params.add('n',                 value=initial_n, vary=vary_n)
        params.add('alpha_scale',       value=initial_alpha_scale, min=0.0)
        params.add('offset',            value=initial_offset)

        return params








def unravel_parameters(parameters, make_copy=False):
    params_list = []
    for name in parameters:
        p = parameters[name]
        if make_copy:
            p = copy.deepcopy(parameters[name])
        params_list.append(p)

    return params_list

def rename_param(p, new_name):
    p_temp = copy.deepcopy(p)
    p_temp.name = new_name
    return p_temp

def merge_parameters(parameter_list, freeze_offset=True):
    ''' takes n Parameter objects and combines them into a new Parameter class'''

    merged = Parameters()
    for i, pn in enumerate(parameter_list):
        p_list = unravel_parameters(pn, make_copy=True)
        for p in p_list:
            p_rename = rename_param(p, 'm%s_%s' %(i, p.name))
            merged[p_rename.name] = p_rename
    return merged
#
class MultipleLorentzians(Function):

    def __init__(self, num_peaks=None, x_data=None, y_data=None, params_list=None):
        if num_peaks is None:
            self.num_peaks = len(find_peaks(y_data))
        else:
            self.num_peaks = num_peaks

        Function.__init__(self, x_data=x_data, y_data=y_data,
                          params_list=params_list)

#        if self._ydata is not None and params_list is None:
#            self._params = self.determine_initial_params()

        # overwrite the parent class  param_names
        self.param_names = [p for p in self._params]

    def define_parameters(self):
        '''
            defines the appropriate number of parameters given the
            number of peaks
        '''
        parameters_list = []
        l = Lorentzian()
        params = l.get_parameters_obj()
        for i in np.arange(self.num_peaks):
            tmp = copy.deepcopy(params)
            parameters_list.append(tmp)

        self._params = merge_parameters(parameters_list)

    def determine_initial_params(self):

        # TODO better initial parameter algorithm
        # here I only specify the positions of all peaks, not sure
        # how best to specify other parameters
        if self._ydata is None:
            print 'error - determine_initial_params() - no _ydata!'
            return

        # define all parameters
        self.define_parameters()

        peaks = find_peaks(self._ydata)
        peak_positions = [self._xdata[peaks[i]] for i in np.arange(len(peaks))]
        print 'peak_positions at %s' % (peak_positions)

        for i in np.arange(len(peaks)):
            self._params['position' + str(i)].value = peak_positions[i]

        # TODO actually we only need 1 offset!
        # now perform a single lorentzian fit with initial seed to have position
        # at all of the found peaks
        for i, peak in enumerate(peak_positions):
            print 'peak position: %f' % (peak)
            p_temp = self.copy_params_subset(self._params, i)
            print p_temp
            l = Lorentzian(x_data=self._xdata, y_data=self._ydata, params_list=p_temp)
            result, params, y_data = l.fit()
            print params

            # add these parameters to the multi-peak parameters
            self.update_params_subset(params, i)

        # TODO be consistent with returning vs. assigning
        return self._params

    def copy_params_subset(self, parameters, index):
        '''
            helper function to copy a subset of the total parameters,
            specified by index
        '''
        # lorentzians, so use these
        ps = ['amplitude', 'position', 'width', 'offset']

        p_temp = Parameters()
        for p_name in ps:
            param = copy.deepcopy(parameters[p_name + str(index)])
            p_temp[p_name] = param
        return p_temp

    def update_params_subset(self, params, index):
        '''

        '''
        # lorentzians, so use these
        ps = ['amplitude', 'position', 'width', 'offset']

        for p_name in ps:
            param = copy.deepcopy(params[p_name])
            self._params[p_name + str(index)] = param

    def func(self, x_data):
        num_peaks = self.num_peaks

        func_val = 0.0

        if self._params is not None:
            for i in np.arange(num_peaks):
                # define a new Parameter object for each lor peak
                p_temp = Parameters()
                ps = ['amplitude', 'position', 'width', 'offset']
                p_temp = self.copy_params_subset(self._params, i)

                l = Lorentzian(x_data=x_data, y_data=None, params_list=p_temp)
                func_val += l.func(x_data)

            return func_val
        else:
            return None


#
#class CompositeFunctions(Function): pass
#
#    def __init__(self, x_data=None, y_data=None, params_list=None):
#        pass



# TODO BIG ASSUMPTION FOR THIS FIT: time has a constant dt

if __name__ == "__main__":

#==============================================================================
#  test Polynomial
#==============================================================================

    test_poly = False
    if test_poly:
        print '--- Testing Polynomial fit ---'

        # generate x data
        xs = np.linspace(-10, 10, 101)

        # generate data set from parameters
        #               (Name,       Value,  Vary,   Min,  Max,  Expr)
        params_list = (('zero',     2.0,    True,   None, None, None),
                       ('one',      0.5,   True,   None, None, None),
                       ('two',      -4.2,   True,   None, None, None),
                       ('three',    10.3,   True,   None, None, None),
                        ('four',    .3,   True,   None, None, None),
                        ('five',    0.0,   False,   None, None, None),
                        ('six',     0.0,   False,  None, None, None),
                        ('seven',     0.0,   False,   None, None, None),
                        ('eight',    0.0,   False,  None, None, None),
                        ('nine',     0.0,   False,  None, None, None))
        p = Polynomial(x_data=xs, y_data=None, params_list=params_list)
        ys = p.function(xs, set_ydata=True)
#        plt.plot(xs, ys)

        # estimator for parameter list from data
#        p = Polynomial(x_data=xs, y_data=ys, order=4, params_list=None)
#        p.print_parameters()
#        result, params, y_final = p.fit()
#        plt.show()
#        report_fit(params)

         # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0.00 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * 1000 for _ in np.arange(len(ys))]
        p = Polynomial(x_data=xs, y_data=noisy_y, order=4, params_list=None)
        p.print_parameters()

        # now fit old params list to noisy data
        result, params, y_final = p.fit(plot=True)
        plt.title('Polynomial fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test lorentzian
#==============================================================================
    test_lor = False
    if test_lor:

        print ' ---- Testing Lorentzian fit ----'
        # generate Lorentzian data
        xs = np.linspace(0, 100, 51)

        # generate data set from parameters
        #               (Name,       Value,  Vary,   Min,  Max,  Expr)j
        params_list = (('amplitude', 2.0,    True,   None, None, None),
                       ('position',  40.3,   True,   None, None, None),
                       ('width',     5.2,   True,   None, None, None),
                       ('offset',    12.3,   True,   None, None, None))
        l = Lorentzian(x_data=xs, y_data=None, params_list=params_list)
        l.function(xs, set_ydata=True)
        ys = l.function(xs)

    #    # first make a new Lorentzian with different initial conditions and let's
    #    #  make sure the fit algorithm will converge to the original parameters
    #    params_list_2 = (('amplitude', 3,      True,   None, None, None),
    #                     ('position',  50.0,   True,   None, None, None),
    #                     ('width',     19.2,   True,   None, None, None),
    #                     ('offset',    -1.3,   True,   None, None, None))
    #    l = Lorentzian(x_data=xs, y_data=ys, params_list=params_list_2)
    #    result, params, y_final = l.fit()
    #    report_fit(params)

        # let's rely on the automated initial parameter list software for noisy data
        print '----'

        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0.00 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * 0.01 for _ in np.arange(len(ys))]
        plt.figure()
        l = Lorentzian(x_data=xs, y_data=noisy_y, params_list=None)
        l.print_parameters()

        # now fit old params list to noisy data
        result, params, y_final = l.fit(plot=True)
        plt.title('Lorentzian fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test sine
#==============================================================================
    test_sine = False
    if test_sine:

        # in seconds
        xs = np.linspace(-1, 1, 101)
        params_list = (('amplitude',  2.0,    True,   None, None, None),
                       ('frequency',  2.0,   True,   None, None, None),
                       ('phase',      0.2,   True,   None, None, None),
                       ('offset',     1,   True,   None, None, None))

        s = Sine(x_data=xs, y_data=None, params_list=params_list)
        s.function(xs, set_ydata=True)
        ys = s.get_ydata()

#        s = Sine(x_data=xs, y_data=ys, params_list=None)
#        s.print_parameters()
#        result, params, y_final = s.fit(plot=True)
#        plt.show()
#        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * 1. for _ in np.arange(len(ys))]

        s = Sine(x_data=noisy_x, y_data=noisy_y, params_list=None)
        result, params, y_final = s.fit(plot=True)
        plt.title('Sine fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test exponential
#==============================================================================
    test_exp = False
    if test_exp:

        # in seconds
        xs = np.linspace(0, 8, 101)
        params_list = (('amplitude',      2.0,    True,   None, None, None),
                       ('time_constant',  2.0,   True,   None, None, None),
                       ('offset',         1,   True,   None, None, None))

        exp = Exp(x_data=xs, y_data=None, params_list=params_list)
        exp.function(xs, set_ydata=True)
        ys = exp.get_ydata()

        # check initial parameters can be determined accurately
#        exp = Exp(x_data=xs, y_data=ys, params_list=None)
#        exp.print_parameters()
#        result, params, y_final = exp.fit(plot=True)
#        plt.show()
#        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * .1 for _ in np.arange(len(ys))]

        exp = Exp(x_data=noisy_x, y_data=noisy_y, params_list=None)
        result, params, y_final = exp.fit(plot=True)
        plt.title('Exp fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test exponential modulated with sine
#==============================================================================
    test_sinexp = False
    if test_sinexp:

        # in seconds
        xs = np.linspace(0, 8, 101)
        params_list = (('amplitude',       2.0,     True,   None, None, None),
                       ('frequency',       0.5,     True,   None, None, None),
                       ('phase',           2.0,     True,   None, None, None),
                       ('time_constant',   2.0,     True,   None, None, None),
                       ('offset',          1,       True,   None, None, None))

        params_list = (('amplitude',       .059,     True,   None, None, None),
                       ('frequency',       2,     True,   None, None, None),
                       ('phase',           .25,     True,   None, None, None),
                       ('time_constant',   1.255,     True,   None, None, None),
                       ('offset',          3.588,       True,   None, None, None))

        se = SinExp(x_data=xs, y_data=None, params_list=params_list)
        se.function(xs, set_ydata=True)
        ys = se.get_ydata()

        # check initial parameters can be determined accurately
        exp = SinExp(x_data=xs, y_data=ys, params_list=None)
        exp.print_parameters()
        result, params, y_final = exp.fit(plot=True)
        plt.show()
        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * .01 for _ in np.arange(len(ys))]

        exp = SinExp(x_data=noisy_x, y_data=noisy_y, params_list=None)
        result, params, y_final = exp.fit(plot=True)
        plt.title('Exp fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test coherent state decay
#==============================================================================
    test_csdecay = False
    if test_csdecay:

        # in seconds
        xs = np.linspace(0, 200, 101)
        params_list = (('amplitude',       2.0,     True,   None, None, None),
                       ('nbar',            12.0,     True,   None, None, None),
                       ('time_constant',   10.0,     True,   None, None, None),
                       ('offset',          6.5,       True,   None, None, None))

        csd = CoherentState_Decay(x_data=xs, y_data=None, params_list=params_list)
        csd.function(xs, set_ydata=True)
        ys = csd.get_ydata()

        # check initial parameters can be determined accurately
        csd = CoherentState_Decay(x_data=xs, y_data=ys, params_list=None)
        csd.print_parameters()
        result, params, y_final = csd.fit(plot=True)
        plt.show()
        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * .2 for _ in np.arange(len(ys))]

        csd = CoherentState_Decay(x_data=noisy_x, y_data=noisy_y, params_list=None)
        result, params, y_final = csd.fit(plot=True)
        plt.title('Exp fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test gaussian
#==============================================================================
    test_gaussian = False
    if test_gaussian:

        # in seconds
        xs = np.linspace(0, 100, 101)
        params_list = (('amplitude',    2.0,     True,   None, None, None),
                       ('position',     35.0,     True,   None, None, None),
                       ('offset',       6.5,       True,   None, None, None),
                       ('sigma',        8.0,     True,   None, None, None))

        f = Gaussian(x_data=xs, y_data=None, params_list=params_list)
        f.function(xs, set_ydata=True)
        ys = f.get_ydata()

        # check initial parameters can be determined accurately
        f = Gaussian(x_data=xs, y_data=ys, params_list=None)
        f.print_parameters()
        result, params, y_final = f.fit(plot=True)
        plt.show()
        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * .01 for _ in np.arange(len(ys))]

        f = Gaussian(x_data=noisy_x, y_data=noisy_y, params_list=None)
        result, params, y_final = f.fit(plot=True)
        plt.suptitle('Gaussian fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test Poisson
#==============================================================================
    test_poisson = False
    if test_poisson:

        # in seconds
        xs = np.linspace(0, 5, 101)
        params_list = (('amplitude',    1.0,     True,   None, None, None),
                       ('n',            0.0,     True,   None, None, None),
                       ('alpha_scale',  1.0,     True,   None, None, None),
                       ('offset',       0.0,       True,   None, None, None))

        p = Poisson(x_data=xs, y_data=None, params_list=params_list)
        p.function(xs, set_ydata=True)
        ys = p.get_ydata()

        # check initial parameters can be determined accurately
#        p = Poisson(x_data=xs, y_data=ys, fix_n=None, params_list=None)
#        p.print_parameters()
#        result, params, y_final = p.fit(plot=True)
#        plt.show()
#        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * .2 for _ in np.arange(len(ys))]

        f = Poisson(x_data=noisy_x, y_data=noisy_y,
                                  params_list=None, fix_n = 0.0)
        result, params, y_final = f.fit(plot=True)
        plt.title('Poisson fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  test Error function
#==============================================================================
    test_erf = False
    if test_erf:

        # in seconds
        xs = np.linspace(0, 5, 101)
        params_list = (('amplitude',    1.0,     True,   None, None, None),
                       ('position',     1.0,     True,   None, None, None),
                       ('x_scale',      1.0,     True,   None, None, None),
                       ('offset',       0.0,       True,   None, None, None))

        f = ErrorFunction(x_data=xs, y_data=None, params_list=params_list)
        f.function(xs, set_ydata=True)
        ys = f.get_ydata()

        # check initial parameters can be determined accurately
        f = ErrorFunction(x_data=xs, y_data=ys, params_list=None)
        f.print_parameters()
        result, params, y_final = f.fit(plot=True)
        plt.show()
        report_fit(params)

        # now fit to noisy data
        # now add noise to the data set
        noisy_x = xs + [np.random.uniform() * 0 for _ in np.arange(len(xs))]
        noisy_y = ys + [np.random.uniform() * .2 for _ in np.arange(len(ys))]

        f = ErrorFunction(x_data=noisy_x, y_data=noisy_y, params_list=None)
        result, params, y_final = f.fit(plot=True)
        plt.title('Exp fit with noise')
        plt.show()
        report_fit(params)

#==============================================================================
#  Test MultipleLorentzians
#==============================================================================

    test_ml = False
    if test_ml:
        xs = np.linspace(0, 100, 101)

        # generate some lorentzians
        ml_data = np.zeros_like(xs, dtype=np.float)

        #               (Name,       Value,  Vary,   Min,  Max,  Expr)
        params_list = (('amplitude', 0.5,    True,   None, None, None),
                       ('position',  40.3,   True,   None, None, None),
                       ('width',     1.2,   True,   None, None, None),
                       ('offset',    0,   True,   None, None, None))
        l = Lorentzian(x_data=xs, y_data=None, params_list=params_list)
        l.function(xs, set_ydata=True)
        ml_data += l.function(xs)

        params_list = (('amplitude', 5,    True,   None, None, None),
                       ('position',  10.3,   True,   None, None, None),
                       ('width',     4.2,   True,   None, None, None),
                       ('offset',    0.,   True,   None, None, None))
        l = Lorentzian(x_data=xs, y_data=None, params_list=params_list)
        l.function(xs, set_ydata=True)
        ml_data += l.function(xs)

        params_list = (('amplitude', 1,    True,   None, None, None),
                       ('position',  80,   True,   None, None, None),
                       ('width',     3,   True,   None, None, None),
                       ('offset',    0.,   True,   None, None, None))
        l = Lorentzian(x_data=xs, y_data=None, params_list=params_list)
        l.function(xs, set_ydata=True)
        ml_data += l.function(xs)

        plt.plot(xs, ml_data, 'bo-')
        plt.title('test data')
        plt.show()

        noisy_y = ml_data + [np.random.uniform() * 0.0 for _ in np.arange(len(ml_data))]
        ml = MultipleLorentzians(num_peaks=3, x_data=xs, y_data=noisy_y)
        ml.func(xs)
        result, params, y_values = ml.fit()

        report_fit(params)
        ml_data

        #TODO need to better fit peaks that are close together!
        # number of peaks
        # NOTE continuous wavelet transform (cwt) has a lot of trouble
        # with offsets!
#        widths = np.arange(1, len(ml_data)/4)
#        cwt_mat = sc.signal.cwt(ml_data, signal.ricker, widths)
#        plt.pcolor(cwt_mat)
#        plt.show()
#        blah = signal.find_peaks_cwt(ml_data, widths, min_length=len(widths)/2)
#        print blah



#def residual_lor(params, x_data, y_data):
#    # extract parameter values
#    a = params['amp'].value
#    x0 = params['position'].value
#    b = params['width'].value
#    offset = params['offset'].value
#
#    model = offset + a / ((x_data - x0)**2 + b**2)
#    return model - y_data
#
#def fit_lor(y_data, x_data=None, x_scale=1.0, y_scale=1.0, num_periods=2.0,
#            plot=True, verbose=True, figure_no=1):
#    # generate corresponding x data
#    # here we are inclusive
#    y_data = np.array(y_data) * y_scale
#    if x_data is None:
#        x_data = np.linspace(0, len(y_data)-1, len(y_data)) * x_scale
#    else:
#        x_data = x_data
#
#    # setup initial parameters
#    ave = sc.mean(y_data)
#    if abs(max(y_data) - ave) > abs(min(y_data) - ave):
#        # we expect a peak
#        initial_amp = (max(y_data) - min(y_data))
#        initial_position = x_data[(np.abs(y_data - max(y_data))).argmin()]
#        initial_offset = min(y_data)
#    else:
#        # we expect a dip
#        initial_amp = (min(y_data) - max(y_data))
#        initial_position = x_data[(np.abs(y_data - min(y_data))).argmin()]
#        initial_offset = max(y_data)
#
#    initial_width = 0.0001
#
#    params = Parameters()
#    params.add('amp',    value=initial_amp)
#    params.add('position',   value=initial_position)
#    params.add('width',    value=initial_width, min=0) # 1 period
#    params.add('offset', value=initial_offset)
#
#    result = minimize(residual_lor, params, args=(x_data, y_data))
#    final = y_data + result.residual
#
#    if plot:
#        plt.figure(figure_no)
#        gs = GridSpec(4, 1)
#        ax_data = plt.subplot(gs[1:4, :])
#        ax_residual = plt.subplot(gs[0, :], sharex=ax_data)
#        ax_data.plot(x_data, y_data, 'ro')
#        ax_data.plot(x_data, final, 'k')
#        ax_residual.plot(x_data, result.residual, 'ko')
#        plt.setp(ax_residual.get_xticklabels(), visible=False)
#        plt.show()
#
#    if verbose:
#        report_fit(params)
#
#    return result, params
#
#
#
#
##==============================================================================
## Simple sine fit
##==============================================================================
#
#def residual_sin(params, x_data, y_data):
#    # extract initial parameter values
#    amp = params['amp'].value
#    freq = params['freq'].value
#    phi = params['phi'].value
#    offset = params['offset'].value
#
#    model = amp * np.sin( 2 * np.pi * (freq * x_data + phi)) + offset
#    return model - y_data
#
#def fit_sin(y_data, x_scale=1.0, y_scale=1.0, num_periods=2.0,
#            plot=True, verbose=True, figure_no=1):
#    # generate corresponding x data
#    # here we are inclusive
#    y_data = np.array(y_data) * y_scale
#    x_data = np.linspace(0, len(y_data)-1, len(y_data)) * x_scale
#
#    # setup initial parameters
#    initial_amp = (max(y_data) - min(y_data)) * 0.5
#    initial_freq = float(num_periods) / float(len(y_data))
#    initial_phi = 0.5
#    initial_offset = (max(y_data) + min(y_data)) * 0.5
#
#    params = Parameters()
#    params.add('amp',    value=initial_amp)
#    params.add('freq',   value=initial_freq,  min=0)
#    params.add('phi',    value=initial_phi,   min=-2.0, max=2.0) # 1 period
#    params.add('offset', value=initial_offset)
#
#    result = minimize(residual_sin, params, args=(x_data, y_data))
#    final = y_data + result.residual
#
#    if plot:
#        plt.figure(figure_no)
#        gs = GridSpec(4, 1)
#        ax_data = plt.subplot(gs[1:4, :])
#        ax_residual = plt.subplot(gs[0, :])
#        ax_data.plot(x_data, y_data, 'ro')
#        ax_data.plot(x_data, final, 'k')
#        ax_residual.plot(x_data, result.residual, 'ko')
#        plt.show()
#
#    if verbose:
#        report_fit(params)
#
#    return result, params
#
## call fit results: params['amp'].value and params['amp'].stderr
#
#def load_fit_sin(file_name):
#    y_data = fileIO.ImportGeneralFile(file_name)
#    y_data_nopi = y_data[0:80]
#    y_data_pi   = y_data[81:-1]
#
#    result_nopi, params_nopi = fit_sin(y_data_nopi)
#    result_pi, params_pi     = fit_sin(y_data_pi)
#
#    return params_nopi, params_pi
#
#def load_fit_sin_zeta(file_name, verbose=True):
#    y_data = fileIO.ImportGeneralFile(file_name)
#
#    num_pts =len(y_data)
#    y_data_nopi = y_data[0:num_pts/2]
#    y_data_pi   = y_data[num_pts/2:num_pts]
#
#    result_nopi, params_nopi = fit_sin(y_data_nopi, num_periods=3,
#                                       y_scale=1000.0, x_scale=1,
#                                       figure_no=1)
#    result_pi, params_pi     = fit_sin(y_data_pi, num_periods=3,
#                                       y_scale=1000.0, x_scale=1,
#                                       figure_no=2)
#
#    # print out the results
#    detuning_nopi = params_nopi['phi'].value
#    detuning_pi   = params_pi['phi'].value
#    detuning_stderr_nopi = params_nopi['phi'].stderr
#    detuning_stderr_pi   = params_pi['phi'].stderr
#
#    if verbose:
#        print 'no pi phase: ' + str(detuning_nopi) + \
#                ' +/- ' + str(detuning_stderr_nopi)
#        print 'pi phase: ' + str(detuning_pi) + \
#                ' +/- ' + str(detuning_stderr_pi)
#        print 'zeta (kHz): ' + str(detuning_nopi - detuning_pi) + \
#                    ' +/- ' + str(detuning_stderr_nopi + detuning_stderr_pi)
#
#    return params_nopi, params_pi
#
#
#def load_fit_sine_zeta_compare(file_name_1, file_name_2, delay_1, delay_2):
#    params_nopi1, params_pi1 = load_fit_sin_zeta(file_name_1)
#    params_nopi2, params_pi2 = load_fit_sin_zeta(file_name_2)
#
#    phase_nopi1 = params_nopi1['phi'].value
#    phase_pi1   = params_pi1['phi'].value
#    phase_nopi2 = params_nopi2['phi'].value
#    phase_pi2   = params_pi2['phi'].value
#
#    stderr_nopi1 = params_nopi1['phi'].stderr
#    stderr_pi1   = params_pi1['phi'].stderr
#    stderr_nopi2 = params_nopi2['phi'].stderr
#    stderr_pi2   = params_pi2['phi'].stderr
#
#    zeta = np.abs(float((phase_nopi1 - phase_pi1) - (phase_nopi2 - phase_pi2))  \
#            / float(delay_1 - delay_2)) * 10**6
#
#    print 'expt 1 phase no pi: ' + str(phase_nopi1) + ' +/- ' + str(stderr_nopi1)
#    print 'expt 1 phase wi pi: ' + str(phase_pi1)   + ' +/- ' + str(stderr_pi1)
#    print 'expt 1 phase no pi: ' + str(phase_nopi2) + ' +/- ' + str(stderr_nopi2)
#    print 'expt 2 phase wi pi: ' + str(phase_pi2)   + ' +/- ' + str(stderr_pi2)
#
#    print 'zeta (kHz): ' + str(zeta)
#
#
##==============================================================================
## Simple decaying exponential
##==============================================================================
#
#def residual_exp(params, x_data, y_data):
#    # extract initial parameter values
#    amp     = params['amp'].value
#    decay   = params['decay'].value
#    offset  = params['offset'].value
#
#    model = amp *  np.exp( -1 * x_data / decay) + offset
#    return model - y_data
#
#def fit_exp(y_data, y_scale=1.0, x_scale=1.0, decay_constants=2.0,
#            plot=True, verbose=True, figure_no=13):
#    # generate corresponding x data
#    # here we are inclusive
#    x_data = np.linspace(0, len(y_data)-1, len(y_data)) * x_scale
#    y_data = np.array(y_data) * y_scale
#
#    # setup initial parameters
#    initial_amp     = (max(y_data) - min(y_data)) * 0.5
#    initial_decay   = float(len(y_data)) / float(decay_constants) * x_scale
#    initial_offset  = (max(y_data) + min(y_data)) * 0.5
#
#    params = Parameters()
#    params.add('amp',       value=initial_amp)
#    params.add('decay',     value=initial_decay)
#    params.add('offset',    value=initial_offset)
#
#    result = minimize(residual_exp, params, args=(x_data, y_data))
#    final = y_data + result.residual
#
#    if plot:
#        plt.figure(figure_no, figsize=(7, 5), facecolor='w', edgecolor='w')
#        gs = GridSpec(4, 1)
#        ax_data = plt.subplot(gs[1:4, :])
#        ax_residual = plt.subplot(gs[0, :])
#        ax_data.plot(x_data, y_data, 'ro')
#        ax_data.plot(x_data, final, 'k')
#        ax_data.set_xlabel('Delay time ($\mu s$)')
#        ax_data.set_ylabel('Readout voltage (mV)')
#        ax_residual.plot(x_data, result.residual, 'ko')
#        plt.text(0.2, 0.8, fit_report(params), ha='left', va='top',
#                 transform=ax_data.transAxes, fontsize=8)
#        plt.show()
#
#    if verbose:
#        report_fit(params)
#
#    return result, params
#
## call fit results: params['amp'].value and params['amp'].stderr
#
#def load_fit_exp(file_name, step_size, freq=-1.0):
#    y_data = fileIO.ImportGeneralFile(file_name)
#
#    result, params = fit_exp(y_data, y_scale=1000.0, x_scale=step_size, decay_constants=3.0)
#
#    T1_time = params['decay'].value
#    T1_stderr = params['decay'].stderr
#    print 'T1 (us) = ' + str(T1_time) + ' +\- ' + str(T1_stderr)
#
#    if freq > 0:
#        Q_value = 2 * np.pi * freq * 1e9 * T1_time * 1e-6
#        Q_stderr = 2 * np.pi * freq * 1e9 * T1_stderr * 1e-6
#        print 'Q (' + str(freq) + ') = ' + str(Q_value) + ' +\- ' + str(Q_stderr)
#
#
##==============================================================================
## Decaying exponential with sin
##==============================================================================
#
#def residual_exp_sin(params, x_data, y_data):
#    # extract initial parameter values
#    amp     = params['amp'].value
#    freq    = params['freq'].value
#    phi     = params['phi'].value
#    offset  = params['offset'].value
#    decay   = params['decay'].value
#
#    model = amp * np.sin( 2 * np.pi * (freq * x_data + phi))  \
#            * np.exp( -1 * x_data / decay) + offset
#    return model - y_data
#
#def fit_exp_sin(y_data, y_scale=1.0, x_scale=1.0, decay_constants = 2.0,
#                num_periods=3.0, plot=True, verbose=True, figure_no=1):
#    # generate corresponding x data
#    # here we are inclusive
#    y_data = np.array(y_data) * y_scale
#    x_data = np.linspace(0, len(y_data)-1, len(y_data)) * x_scale
#
#    # setup initial parameters
#    initial_amp = (max(y_data) - min(y_data)) * 0.5
#    initial_freq = float(num_periods) / float(len(y_data))
#    initial_phi = 0.5
#    initial_offset = (max(y_data) + min(y_data)) * 0.5
#    initial_decay = len(x_data) / decay_constants
#
#    params = Parameters()
#    params.add('amp',    value=initial_amp)
#    params.add('freq',   value=initial_freq,  min=0.0)
#    params.add('phi',    value=initial_phi,   min=-2.0, max=2.0) # 1 period
#    params.add('offset', value=initial_offset)
#    params.add('decay',  value=initial_decay, min=0.0)
#
#    result = minimize(residual_exp_sin, params, args=(x_data, y_data))
#    final = y_data + result.residual
#
#    if plot:
#        plt.figure(figure_no, figsize=(7, 5), facecolor='w', edgecolor='w')
#        gs = GridSpec(4, 1)
#        ax_data = plt.subplot(gs[1:4, :])
#        ax_residual = plt.subplot(gs[0, :])
#        ax_data.plot(x_data, y_data, 'ro')
#        ax_data.plot(x_data, final, 'k')
#        ax_residual.plot(x_data, result.residual, 'ko')
#        plt.show()
#
#    if verbose:
#        report_fit(params)
#
#    return result, params
#
#def load_fit_exp_sin(file_name):
#    y_data = fileIO.ImportGeneralFile(file_name)
#    num_pts =len(y_data)
#
#    y_data_nopi = y_data[0:num_pts/2]
#    y_data_pi   = y_data[num_pts/2:num_pts]
#
#    result_nopi, params_nopi = fit_exp_sin(y_data_nopi)
#    result_pi, params_pi     = fit_exp_sin(y_data_pi)
#
#    return params_nopi, params_pi
#
#def fit_exp_sin_zeta(file_name, step_size):
#    y_data = fileIO.ImportGeneralFile(file_name)
#
#    num_pts =len(y_data)
#    y_data_nopi = y_data[0:num_pts/2]
#    y_data_pi   = y_data[num_pts/2:num_pts]
#
#    result_nopi, params_nopi = fit_exp_sin(y_data_nopi,
#                                           y_scale=1000.0, x_scale=step_size,
#                                           figure_no=1)
#    result_pi, params_pi     = fit_exp_sin(y_data_pi,
#                                           y_scale=1000.0, x_scale=step_size,
#                                           figure_no=2)
#
#    # print out the results
#    detuning_nopi = params_nopi['freq'].value * 10**6
#    detuning_pi   = params_pi['freq'].value * 10**6
#    detuning_stderr_nopi = params_nopi['freq'].stderr * 10**6
#    detuning_stderr_pi   = params_pi['freq'].stderr * 10**6
#
#    print 'no pi detuning (kHz): ' + str(detuning_nopi) + \
#            ' +/- ' + str(detuning_stderr_nopi)
#    print 'pi detuning (kHz): ' + str(detuning_pi) + \
#            ' +/- ' + str(detuning_stderr_pi)
#    print 'zeta (kHz): ' + str(detuning_nopi - detuning_pi) + \
#                ' +/- ' + str(detuning_stderr_nopi + detuning_stderr_pi)
#
##==============================================================================
## Poisson distribution
##==============================================================================
#
## TODO handle x_data = 0 = n case correctly.
#def residual_poisson(params, x_data, y_data):
#    # extract initial parameter values
#    amp             = params['amp'].value
#    alpha_ratio     = params['alpha_ratio'].value     # displacement
#    n               = params['n'].value            # photon number
#    offset          = params['offset'].value
#
#    model = amp * np.exp( -1 * alpha_ratio*alpha_ratio * x_data*x_data) * \
#                  (alpha_ratio * x_data)**(2 * n) / sc.misc.factorial(n) + offset
#
#
#    return model - y_data
#
#def fit_poisson(y_data, y_scale=1.0, x_scale=1.0, n_guess=0.0, vary_n=True,
#                alpha_ratio_guess=1.0, plot=True, verbose=True, figure_no=1):
#    # generate corresponding x data
#    # here we are inclusive
#    y_data = np.array(y_data) * y_scale
#    x_data = np.linspace(0, len(y_data)-1, len(y_data)) * x_scale
#
#    # setup initial parameters
#    initial_amp             = (max(y_data) - min(y_data))
#    initial_alpha_ratio     = alpha_ratio_guess
#    initial_n               = n_guess
#    initial_offset          = min(y_data)
#
#    params = Parameters()
#    params.add('amp',           value=initial_amp)
#    params.add('alpha_ratio',   value=initial_alpha_ratio)
#    params.add('n',             value=initial_n,   min=0.0, vary=vary_n)
#    params.add('offset',        value=initial_offset)
#
#    result = minimize(residual_poisson, params, args=(x_data, y_data))
#    final = y_data + result.residual
#
#    if plot:
#        plt.figure(figure_no, figsize=(7, 5), facecolor='w', edgecolor='w')
#        gs = GridSpec(4, 1)
#        ax_data = plt.subplot(gs[1:4, :])
#        ax_residual = plt.subplot(gs[0, :])
#        ax_data.plot(x_data, y_data, 'ro')
#        ax_data.plot(x_data, final, 'k')
#        ax_residual.plot(x_data, result.residual, 'ko')
#        plt.text(0.2, 0.95, fit_report(params), ha='left', va='top',
#                 transform=ax_data.transAxes, fontsize=8)
#        plt.show()
#
#    if verbose:
#        report_fit(params)
#
#    return result, params
#
#def load_fit_poisson(file_name, n_guess=0.0, vary_n=True, alpha_ratio_guess=0.0, figure_no=25):
#    y_data = fileIO.ImportGeneralFile(file_name)
#    num_pts =len(y_data)
#
#    y_data_pi       = np.array(y_data[1:num_pts/2])
#    y_data_nopi     = np.array(y_data[num_pts/2+1:num_pts])
#
#    y_data_calibrate =  y_data_nopi - y_data_pi
#
#    plt.close(figure_no)
#    result_nopi, params_nopi = fit_poisson(y_data_calibrate, y_scale=1000.0,
#               n_guess=n_guess, vary_n=vary_n, alpha_ratio_guess=alpha_ratio_guess,
#               figure_no=figure_no)
#    plt.figure(figure_no)
#    plt.title(file_name.split('\\')[-1], fontsize=12)
#
#    return params_nopi
#
##==============================================================================
## 2D Gaussian fit
##==============================================================================
#
#def residual_2dgaussian(params, x, y, z):
#    # extract initial parameter values
#    amp         = params['amp'].value
#    x0          = params['x0'].value
#    y0          = params['y0'].value
#    sigma_x     = params['sigma_x'].value
#    sigma_y     = params['sigma_y'].value
#    corr        = params['corr'].value
#    offset      = params['offset'].value
#
#    model = amp * np.exp(-1 / (2 * (1 - corr**2)) *
#            (((x - x0) / sigma_x)**2 + ((y - y0) / sigma_y)**2  -
#            (2 * corr * (x - x0) * (y - y0)) / (sigma_x * sigma_y))) + offset
#    return model - z
#
## this function performs the 2D gaussian fit, generating proper input fit params
##  you will need to input x and y data arrays for this fit
## REQUIRED: all data is in the form of a 2D array
#def fit_2dgaussian(x_data, y_data, z_data, x_scale=1.0, y_scale=1.0,
#                        x0_guess=0.0, y0_guess=0.0, vary_no_corr=True,
#                        z_scale=1.0, plot=True, verbose=True, figure_no=1):
#    # generate corresponding x and y data
#    x_data = np.array(x_data) * x_scale
#    y_data = np.array(y_data) * y_scale
#    z_data = np.array(z_data) * z_scale
#
#    # setup initial parameters
#    initial_amp             = (np.max(z_data) - np.min(z_data))
#    initial_x0              = x0_guess
#    initial_y0              = y0_guess
#    initial_sigma_x         = 1.0
#    initial_sigma_y         = 1.0
#    initial_corr             = 0.0
#    initial_offset          = np.min(z_data)
#
#    params = Parameters()
#    params.add('amp',       value=initial_amp)
#    params.add('x0',        value=initial_x0)
#    params.add('y0',        value=initial_y0)
#    params.add('sigma_x',   value=initial_sigma_x)
#    params.add('sigma_y',   value=initial_sigma_y)
#    params.add('corr',      value=initial_corr, vary=vary_no_corr)
#    params.add('offset',    value=initial_offset)
#
#    # flatten data for fitting
#    x_flatten = np.ndarray.flatten(x_data)
#    y_flatten = np.ndarray.flatten(y_data)
#    z_flatten = np.ndarray.flatten(z_data)
#    result = minimize(residual_2dgaussian, params, args=(x_flatten, y_flatten, z_flatten))
#
#    # reshape the fitted data (for plotting)
#    final_flatten = z_flatten + result.residual
#    final = np.reshape(final_flatten, z_data.shape)
#
#    if plot:
#       plot_2d(x_data, y_data, z_data, figure_no=51, plot_type='pcolor')
#       plot_2d(x_data, y_data, final, figure_no=51, plot_type='contour')
#
#    if verbose:
#        report_fit(params)
#
#    return result, params
#
#def plot_2d(x_data, y_data, z_data, figure_no=1, replot=False, plot_type='pcolor'):
#
#    if replot:
#        plt.close(figure_no)
#
#    plt.figure(figure_no, figsize=(7, 5), facecolor='w', edgecolor='w')
#
#    if plot_type=='pcolor':
#        x_pcolor, ypcolor = set_2Daxes_pcolor(x_data, y_data)
#        plt.pcolor(x_pcolor, ypcolor, z_data,
#                   vmax=z_data.max()*0.75, vmin=z_data.min()*1.1)
#        plt.colorbar()
#    elif plot_type=='contour':
#        c_plot = plt.contour(x_data, y_data, z_data, colors='k', linewidths=2)
#        plt.clabel(c_plot, inline=1, fontsize=12)
#
#    plt.show()
#
## returns a line cut of two dimensional data
## TODO,: arbitrary axis
##def cut_2d(x_data, y_data, z_data, axis='v', value=0):
#
#disp_0_j0 = -0.009797 + 1j * 0.195319
#disp_0p2_j0 = 1.24038 + 1j * 0.079915
#disp_0p2_j0_100ns = 1.088761 + 1j * 0.173827
#
#angles = [np.angle(disp_0_j0), np.angle(disp_0p2_j0), np.angle(disp_0p2_j0_100ns)]
#disp   = [np.abs(disp_0_j0),    np.abs(disp_0p2_j0), np.abs(disp_0p2_j0_100ns)]
#
#i_window_default = [-0.25, 0.25, 21]
#q_window_default = [-0.25, 0.25, 21]
#
#i_window_default = [-0.5, 0.5, 21]
#q_window_default = [-0.5, 0.5, 21]
##i_window_default = [-0.25, 0.75, 21]
##q_window_default = [-0.25, 0.75, 21]
#def load_fit_qfunction(file_name, i_window=i_window_default,
#                       q_window=q_window_default, alpha_scale=1.0,
#                       z_scale=1000.0, vary_no_corr=True):
#
#    i_ranges = np.linspace(i_window[0], i_window[1], i_window[2]) * alpha_scale
#    q_ranges = np.linspace(q_window[0], q_window[1], q_window[2]) * alpha_scale
#
#    # import data and subtract off calibration expt
#    raw_data = fileIO.ImportGeneralFile(file_name)
#    raw_len = len(raw_data)
#    qfunction_pi    = -1 * np.array(raw_data[0:raw_len/2])
#    qfunction_nopi  = -1 * np.array(raw_data[raw_len/2:raw_len])
#    qfunction = (qfunction_pi - qfunction_nopi) * z_scale
#
#    # convert 1D arrays to 2D
#    ii_ranges, qq_ranges    = np.meshgrid(i_ranges, q_ranges)
#    qfunction_2d            = np.reshape(qfunction, ii_ranges.shape)
#    qfunction_pi_2d         = np.reshape(qfunction_pi, ii_ranges.shape)
#    qfunction_nopi_2d       = np.reshape(qfunction_nopi, ii_ranges.shape)
#
#    plot_2d(ii_ranges, qq_ranges, qfunction_pi_2d, figure_no=52, replot=True)
#    plot_2d(ii_ranges, qq_ranges, qfunction_nopi_2d, figure_no=53, replot=True)
##    plot_2d(ii_ranges, qq_ranges, qfunction_2d, figure_no=54)
#
#    result, params = fit_2dgaussian(ii_ranges, qq_ranges, qfunction_2d, figure_no=50, vary_no_corr=vary_no_corr)
#    plt.title(file_name.split('\\')[-1], fontsize=12)
#
#    x0 = params['x0'].value
#    y0 = params['y0'].value
#
#    disp = x0 + 1j * y0
#    disp_amp = np.abs(disp)
#    disp_angle = np.rad2deg(np.angle(disp))
#
#    print 'diplacement amplitude: ' + str(disp_amp)
#    print 'displacement angle: ' + str(disp_angle)
#
## adjust xy axis for plotting with pcolor()
##  shifts x and y axes by 0.5 a step size since pcolor
##   plots squares in the center of adjacent coordinates
#def set_2Daxes_pcolor(xx_ranges, yy_ranges):
#    # for x axis, first add another row and transpose
#    x_st = np.transpose(np.concatenate((xx_ranges, np.array([xx_ranges[0]]))))
#    delta = x_st[1] - x_st[0]
#    # subtract by half the difference and add an additional row of elements
#    x_pcolor = np.transpose(np.concatenate((x_st - delta / 2.0,
#                                           np.array([x_st[-1] + delta / 2.0]))))
#
#    # for y axis, first add another row
#    yy_transpose = np.transpose(yy_ranges)
#    y_st = np.transpose(np.concatenate((yy_transpose, np.array([yy_transpose[0]]))))
#    delta = y_st[1] - y_st[0]
#    # subtract by half the difference and add an additional row of elements
#    y_pcolor = np.concatenate((y_st - delta / 2.0,
#                               np.array([y_st[-1] + delta / 2.0])))
#
#    return x_pcolor, y_pcolor