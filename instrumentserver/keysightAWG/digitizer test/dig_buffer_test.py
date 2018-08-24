""" This file is used to test the capabilites of the digitizer and the buffer pool.
This file loads data onto the awg, runs the hvi and captures with the digitizer"""



import numpy as np
import matplotlib.pyplot as pl
import keysightSD1 as key
from CompiledHVI import CompiledHVI
import time
import gc


def digitizer_setup(dig, nsamples, npoints, naverages, ntransfers, captureDelay = 0, digScale = 2):
    digChannels = [1, 2, 3, 4] 
    errors = []
    errors += [dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)]

    for i in range(len(digChannels)):   
       errors += [dig.DAQtriggerExternalConfig(digChannels[i], key.SD_TriggerExternalSources.TRIGGER_EXTERN, 
                                            key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)]
       errors += [dig.DAQflush(digChannels[i])]
       errors += [dig.channelInputConfig(digChannels[i], digScale, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)]
       errors += [dig.DAQconfig(digChannels[i], nsamples, npoints * naverages, captureDelay, key.SD_TriggerModes.EXTTRIG)]
       errors += [dig.DAQbufferPoolConfig(digChannels[i], nsamples * npoints * naverages / ntransfers, 100)]
    print(errors)

def digitizer_acquire(dig, hvi, awg, nsamples, npoints, naverages, ntransfers, data_channel):
    assert(naverages % ntransfers == 0)

    digChannels = [1, 2, 3, 4]
    awg.AWGstartMultiple(15)
    dig.DAQstartMultiple(3)
    hvi.start()
    
    # Add code to either trigger digitizer or wait for first few cycles
    sums = np.zeros((npoints, nsamples), dtype = np.float64)
    sums_squared = np.zeros_like(sums, dtype = np.float64)
       
#    return data
    averages_per_transfer = naverages / ntransfers
    temp = np.zeros(nsamples*npoints * averages_per_transfer, dtype = np.float64)
    for transfer in range(ntransfers):
        try:
            if transfer % (ntransfers/10) == 0: 
                print(str(transfer) + r'/' + str(ntransfers) + ' transfers done')

                gc.collect()
        except:
            pass# modulo shit ain't workin. its ok
        temp = dig.DAQbufferGet(data_channel) / 35000.
        if type(temp) is float and temp < 0:
            print('error thrown with code ', temp)
#        temp = np.array(temp, dtype = float)
        
#        temp /= np.max(temp)
        
#        means[transfer * points_per_transfer : (transfer+1) * points_per_transfer] = temp
#        stds[transfer * points_per_transfer : (transfer+1) * points_per_transfer] = temp**2
        
        ''' this only works if ntransfers == naverages '''
        samples_per_average = nsamples * npoints
        for i in range(averages_per_transfer):
            for j in range(npoints):
                sums[j] += temp[i * samples_per_average + j * nsamples : i * samples_per_average + (j+1) * nsamples]
                sums_squared[j] += temp[i * samples_per_average + j * nsamples : i * samples_per_average + (j+1) * nsamples]**2

            
    
    for i in range(len(digChannels)):
        dig.DAQbufferPoolRelease(digChannels[i])
    

    means = sums / naverages
#    for i in range(npoints):
#        pl.plot((sums_squared[i] / npoints) - (means[i] * means[i])) 
    stds = np.sqrt((sums_squared / naverages) - (means * means)) 
    
   
    return means, stds

def Gaussian(x, sigma, mu):
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(
        -((x - mu) ** 2) / (2 * sigma) ** 2)

def load_awg(awg, npoints):
    awgChannels = [1, 2, 3, 4]
    gaussian = np.asarray([Gaussian(x, 10, 10) for x in np.linspace(-100, 100, 4000)])
    gaussian = gaussian * (1 / max(gaussian))
    
    pulse_length = len(gaussian)
    
    # Make a whole series of Gaussian waves, each bigger than the last.
    gaussian_waves = [gaussian * i for i in np.linspace(0.4, 1, npoints)]
    
    wait_time = 0
    
    full_length = pulse_length + wait_time
    
    awg.waveformFlush()
    
    trigger_data = np.concatenate((np.ones(10), np.zeros(full_length - 10)))    
    trigger = key.SD_Wave()
    trigger.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, trigger_data)
    awg.waveformLoad(trigger, 0)
    
    for i in range(npoints):
        data_wave = key.SD_Wave()
        data_wave.newFromArrayDouble(key.SD_WaveformTypes.WAVE_ANALOG, gaussian_waves[i])
        awg.waveformLoad(data_wave, i+1)
    
    # Setup Channels
    for i in awgChannels:
        awg.AWGflush(i)
        awg.channelWaveShape(i, key.SD_Waveshapes.AOU_AWG)
        awg.channelAmplitude(i, 1)
        awg.AWGqueueConfig(i, 1) # Setup the queue in cyclic mode
        
    # load data onto channels 1 and 2
    for i in [1, 2]: 
        for k in range(npoints):
            awg.AWGqueueWaveform(i, k+1, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
    
    # load triggers onto channels 3 and 4
    for i in [3, 4]:
        for k in range(npoints):
            awg.AWGqueueWaveform(i, 0, key.SD_TriggerModes.SWHVITRIG, 0, 1, 0)
    


def fetch_keysight_shit(trigger_period):
#    testing_HVI_location = r'C:\qrlab\instrumentserver\keysightAWG\digitizer test\2nd_trigger.HVI'
    testing_HVI_location = r'C:\qrlab\instrumentserver\keysightAWG\\' + str(trigger_period) + 'usTrigger.HVI'
    hvi = CompiledHVI(testing_HVI_location)
    
    chassis = 0
    digSlot = 3
    digName = "M3102A"
    dig = key.SD_AIN()
    dig.openWithSlotCompatibility(digName, chassis, digSlot, key.SD_Compatibility.KEYSIGHT)
    
    AWG_PRODUCT = "M3202A"
    CHASSIS = 0
    AWG_SLOT = 7
    awg = key.SD_AOU()
    awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)
    
    return hvi, dig, awg






trigger_period = 100 #us
nsamples = 4000 #number of data points taken ever acquisition

npoints = 20 # number of different experimental points, each will be averaged
naverages = 10000 # total number of averages per point
ntransfers = naverages / 10  # number of blocks it takes the dig data to transfer to the pc

data_channel = 1

hvi, dig, awg = fetch_keysight_shit(trigger_period)
hvi.stop()

print('data rate (samp/us):', nsamples / trigger_period)
print('measurment time (s):', naverages * npoints * trigger_period * 1e-6)
print('on ratio:', nsamples * 2 / (trigger_period * 1e3))


load_awg(awg, npoints)
digitizer_setup(dig, nsamples, npoints, naverages, ntransfers)
start_time = time.time()
print('starting acquisition')
means, stds = digitizer_acquire(dig, hvi, awg, nsamples, npoints, naverages, ntransfers, data_channel)

hvi.stop()
dig.close()
awg.close()


print('acquisition finished', time.time()-start_time)

#means /= np.max(means)

pl.close('all')
fig = pl.figure()
for i in range(npoints):
    ax1 = fig.add_subplot(2, npoints, i+1)
    ax1.set_ylim((0, np.max(means)))
    ax1.plot(means[i])
#    for j in range(naverages):
#        ax1.plot(data[data_channel, j, i])
    if i>0:ax1.set_yticks([])
    
    ax2 = fig.add_subplot(2, npoints, i+1+npoints)
    ax2.plot(stds[i])


    
    
    


