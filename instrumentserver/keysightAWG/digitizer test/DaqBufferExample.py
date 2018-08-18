import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
import keysightSD1 as key



pointsPerCycle = 10000
captureCycles = 1


# This variable defines how many total transactions will happen
# (pointsPerCycle * captureCycles / transfers) must be an even integer 
transfers = 1


chassis = 0
digSlot = 3

digName = "M3102A"


digChannels = [1, 2, 3, 4]
digScale = 2
captureDelay = 0


dig = key.SD_AIN()
error = dig.openWithSlotCompatibility(digName, chassis, digSlot, key.SD_Compatibility.KEYSIGHT)
if error < 0:
   print("Digitizer open error: {}".format(error))
   dig.close()
   exit()

error = dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
if error < 0:
      print('Error triggerIOconfig {}'.format(key.SD_Error.getErrorMessage(error)))

for i in range(len(digChannels)):   

   error = dig.DAQtriggerExternalConfig(digChannels[i], key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_RISE, key.SD_SyncModes.SYNC_NONE)
   if error < 0:
      print('Error DAQtriggerExternalConfig - {}'.format( key.SD_Error.getErrorMessage(error)))

   error = dig.DAQflush(digChannels[i])
   if error < 0:
      print('Error DAQflush {}'.format(error))

   error = dig.channelInputConfig(digChannels[i], digScale, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
   if error < 0:
      print('Error channelInputConfig {}'.format(error))

   error = dig.DAQconfig(digChannels[i], pointsPerCycle, captureCycles, captureDelay, key.SD_TriggerModes.EXTTRIG)
   if error < 0:
      print('Error DAQconfig {}'.format(error))

   error = dig.DAQbufferPoolConfig(digChannels[i], int(pointsPerCycle * captureCycles / transfers))
   if error < 0:
      print('Error DAQbufferPoolConfig {}'.format(error))

   error = dig.DAQstart(digChannels[i])
   if error < 0:
         print('Error DAQstart {}'.format(error))   


# Add code to either trigger digitizer or wait for first few cycles
#time.sleep(1)


data = []

for i in range(len(digChannels)):
   data.append(dig.DAQbufferGet(digChannels[i]))

for j in range(1, transfers):
   for i in range(len(digChannels)):
      temp = dig.DAQbufferGet(digChannels[i])      
      data[i] = np.concatenate((data[i], temp), axis=0)     #only here for data plotting purposes, this concatenation can be done afterwards for efficiency


for i in range(len(digChannels)):
   plt.plot(data[i], label=str(i+1))
plt.legend()
plt.show()


for i in range(len(digChannels)):
   error = dig.DAQbufferPoolRelease(digChannels[i])
   if error < 0:
      print('Error DAQbufferPoolRelease {}'.format(error))


dig.close()

print("Done.")