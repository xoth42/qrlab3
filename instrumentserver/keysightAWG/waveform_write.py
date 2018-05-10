""" Python code for readout pulse. Should be the same as example from Andy """



# All current Python Driver calls
import keysightSD1 as key
import time
import numpy as np


def gaussian_dist(x, mu, sigma):
    return 1/(sigma * np.sqrt(2* np.pi)) * np.exp(-.5 * (x-mu)**2 / sigma**2)
    
def sinusoid(x, phi, w, a):
    return a * np.sin(2*np.pi * x * w + phi)

# Load waveforms to AWG
waveform_filepath = "C:\\qrlab\instrumentserver\keysightAWG\waveforms\\"
print(waveform_filepath)
gaussian = key.SD_Wave()
gaussian.newFromFile(waveform_filepath + 'Gaussian.csv')

fh_gaussian = key.SD_Wave()
fh_gaussian.newFromFile(waveform_filepath + 'First Half Gaussian.csv')

sh_gaussian = key.SD_Wave()
sh_gaussian.newFromFile(waveform_filepath + 'Second Half Gaussian.csv')

n = 100

if 1:
    name = 'Readout'
    fh = np.loadtxt(waveform_filepath + 'First Half Gaussian.csv', skiprows = 3)
    sh = np.loadtxt(waveform_filepath + 'Second Half Gaussian.csv', skiprows = 3)
    
    data = gaussian_dist(np.arange(-n/2, n/2), 0, n/7)
    data /= np.max(data)
    modulator = sinusoid(np.arange(n), 0, .1, 1)
    
    data = data * modulator
    
    #    data = np.concatenate((fh, np.ones(1000000), sh))
    np.savetxt(waveform_filepath + name + '.csv', data, delimiter = '\n\t',
               header = 'waveformName,' + name + '\nwaveformPoints,' + str(len(data)) 
               + '\nwaveformType,WAVE_ANALOG_16', fmt = '%1.15f', comments = '')

if 0:
    name = '100nsPause'
    data = np.ones(100)
    np.savetxt(waveform_filepath + name + '.csv', data, delimiter = '\n\t',
               header = 'waveformName,' + name + '\nwaveformPoints,' + str(len(data)) 
               + '\nwaveformType,WAVE_ANALOG_16', fmt = '%1.15f', comments = '')

if 1:
    name = 'Trigger'
    data = np.concatenate((np.ones(10)*.3, np.zeros(n-10)))
    np.savetxt(waveform_filepath + name + '.csv', data, delimiter = '\n\t',
               header = 'waveformName,' + name + '\nwaveformPoints,' + str(len(data)) 
               + '\nwaveformType,WAVE_ANALOG_16', fmt = '%1.15f', comments = '')