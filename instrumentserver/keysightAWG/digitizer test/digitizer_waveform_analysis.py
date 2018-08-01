# -*- coding: utf-8 -*-
#import matplotlib.pyplot as plt
#from DaqBufferExample import digitizer_capture
import numpy as np

#plt.close('all')


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


def digitizer_capture(args):
#    import os
    import sys
#    import time
    import numpy as np
#    sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
    import keysightSD1 as key
    def error_check(err):
        if err < 0:
            raise ValueError('Err is ' + str(err))
    pointsPerCycle = args[0] # was 100
    captureCycles = args[1] # was 20
    
    
    # This variable defines how many total transactions will happen
    # (pointsPerCycle * captureCycles / transfers) must be an even integer 
    transfers = args[2] # was 4
    
    chassis = 0
    digSlot = 3
    
    digName = "M3102A"
    
    
    digChannels = [1, 2, 3, 4]
    digScale = 2
    captureDelay = 0
    
    
    dig = key.SD_AIN()
    error = dig.openWithSlotCompatibility(digName, chassis, digSlot, key.SD_Compatibility.KEYSIGHT)
    if error < 0:
        error_check(error)
        print("Digitizer open error: {}".format(error))
        dig.close()
        exit()
    
    error = dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
    if error < 0:
        error_check(error)
        print('Error triggerIOconfig {}'.format(key.SD_Error.getErrorMessage(error)))
    
    for i in range(len(digChannels)):   
    
       error = dig.DAQtriggerExternalConfig(digChannels[i], key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
                                            key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)
       error_check(error)
       if error < 0:
          print('Error DAQtriggerExternalConfig - {}'.format( key.SD_Error.getErrorMessage(error)))
    
       error = dig.DAQflush(digChannels[i])
       error_check(error)
       if error < 0:
          error_check(error)
          print('Error DAQflush {}'.format(error))
    
       error = dig.channelInputConfig(digChannels[i], digScale, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
       error_check(error)

       if error < 0:
          print('Error channelInputConfig {}'.format(error))
    
       error = dig.DAQconfig(digChannels[i], pointsPerCycle, captureCycles, captureDelay, key.SD_TriggerModes.EXTTRIG)
       error_check(error)

       if error < 0:
          error_check(error)
          print('Error DAQconfig {}'.format(error))
    
       error = dig.DAQbufferPoolConfig(digChannels[i], int(pointsPerCycle * captureCycles / transfers))
       error_check(error)

       if error < 0:
          error_check(error)
          print('Error DAQbufferPoolConfig {}'.format(error))
    
       error = dig.DAQstart(digChannels[i])
       error_check(error)

       if error < 0:
           error_check(error)
           print('Error DAQstart {}'.format(error))   
    
    
    # Add code to either trigger digitizer or wait for first few cycles
    #time.sleep(1)
    
    
    data = []
    
    for i in range(len(digChannels)):
       data.append(dig.DAQbufferGet(digChannels[i]))
#    return data
    for j in range(1, transfers):
       for i in range(len(digChannels)):
          temp = dig.DAQbufferGet(digChannels[i])
          data[i] = np.concatenate((data[i], temp), axis=0)     #only here for data plotting purposes, this concatenation can be done afterwards for efficiency
    
    
#    for i in range(len(digChannels)):
#       plt.plot(data[i])
#       plt.show()
#       pass
        
    
    
    for i in range(len(digChannels)):
        error = dig.DAQbufferPoolRelease(digChannels[i])
        error_check(error)
        if error < 0:
            print('Error DAQbufferPoolRelease {}'.format(error))
    dig.close()
    return data
    
#See digitizer_waveform_analysis in the scripts folder for the analysis of
# the resulting data.
    









#from scipy.integrate import simps
#Split the big array of data into each capture. Ch2 gets split because that
# channel was actually plugged in.
#capture_cycles = np.split(ch2, captures)
#
##Use the simpson method to integrate the resulting captures. The theory is
## that if there is a waveform out of place, the area under that Gaussian will
##  be different, and it should be obvious that the digitizer dropped a wave.
#integrations = map(simps, capture_cycles)
#integrations = np.asarray(integrations)
#from scipy.optimize import curve_fit
#
#
#def linear(x, a, b):
#    return a * x + b
##Plotting the integrations, its clear that there are 'bands' where the
## integrations of the waves fall. How can it be shown that one of the waves
## jumped out of order? Fit a line to the sequence of integrations and look at
##  the fitted parameters. If a wave jumped out of place, it would be clear
## that a wave is out of place.
#
#wave_regions = np.split(integrations, captures / 10)
## plt.plot(integrations, 'bo')
#fits = map(lambda x: curve_fit(linear, _range_(x), x), wave_regions)
#
#coefficents = numpy_array_map(lambda x: x[0], fits)
#a_coefficent = coefficents[..., 0]
#b_coefficent = coefficents[..., 1]
#plt.grid()
#plt.title('Coefficents for parameters for linear fits')
#plt.plot(a_coefficent, 'r*')
#plt.plot(b_coefficent, 'bo')

########################################################

#NEW ANALYSIS

########################################################


import matplotlib.pyplot as plt
plt.close('all')

nsamples = 400 #number of data points taken ever acquisition
npoints = 4 # number of different experimental points, each will be averaged
naverages = 1 # total number of averages per point
captures = npoints * naverages # total number of acquistions for dig to take

num_transfers = 1 # number of blocks it takes the dig data to transfer to the pc

data = digitizer_capture([nsamples, captures, num_transfers])

ch1 = data[0]
ch2 = data[1]
ch3 = data[2]
ch4 = data[3]

big_array = ch2
print(np.shape(big_array))
#wave_sequences = np.asarray(np.split(big_array, captures / 10))
#print(np.shape(wave_sequences))


plt.plot(ch2)
plt.show()

#standard_dev = np.std(wave_sequences, axis = 0)
#plt.plot(standard_dev, 'r*')
#plt.title('Elementwise standard deviation for sequences of all n waves stitched together')
#plt.xlabel('Standard deviations')
#plt.plot((ch2 * 1/max(standard_dev)), 'bo')
#plt.grid()
#plt.show()








