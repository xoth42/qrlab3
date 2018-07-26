import os
import sys
import time
import ctypes
from ctypes import wintypes
import random
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('C:\Program Files (x86)\Keysight\SD1\Libraries\Python')
import keysightSD1 as key
from timeit import default_timer as timer


pointsPerCycle = 8185      
captureCycles = 1

chassis = 0

digName = "M3102A"
digSlot = 3
digChannels = [1]
digChannel = 1
digScale = 1
captureDelay = 0
readTimeout = 1
digTriggerMode = key.SD_TriggerModes.SWHVITRIG



dig = key.SD_AIN()
error = dig.openWithSlotCompatibility(digName, chassis, digSlot, key.SD_Compatibility.KEYSIGHT)
if error < 0:
    print("Digitizer open error: {}".format(error))
    dig.close()
    exit()


error = dig.DAQflush(digChannel)
if error < 0:
    print('Error DAQflush {}'.format(error))

error = dig.channelInputConfig(digChannel, digScale, key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
if error < 0:
    print('Error channelInputConfig {}'.format(error))

error = dig.DAQconfig(digChannel, pointsPerCycle, captureCycles, captureDelay, digTriggerMode)
if error < 0:
    print('Error DAQconfig {}'.format(error))

error = dig.DAQbufferPoolConfig(digChannel, pointsPerCycle * captureCycles)
if error < 0:
    print('Error DAQbufferPoolConfig {}'.format(error))


#Start all DAQs at the same time
error = dig.DAQstart(digChannel)
if error < 0:
    print('Error DAQstartMultiple {}'.format(error))   
   

#trigger DAQs
for cycles in range(captureCycles):
    dig.DAQtrigger(digChannel)
    time.sleep(0.001)



# #Debug with DAQread --- This works well if you remove DAQbufferPoolConfig()
# dataRead = dig.DAQread(digChannel, pointsPerCycle  * captureCycles, 1)
# plt.plot(dataRead)
# plt.show()
# exit()

#make sure it's done capturing
time.sleep(2)



dataRead = dig.DAQbufferGet(digChannel)



#print(dataRead[0][100000000])   #this crashes Python - instead of the normal Python wrapping or throwing an exception


#Transfer the read data to a Python list
myData = []
for i in range(pointsPerCycle * captureCycles):
#    print(dataRead[0][i])
#    print(np.shape(dataRead))
    myData.append(dataRead[0][i])


plt.plot(myData)
plt.show()




error = dig.DAQbufferPoolRelease(digChannel)
if error < 0:
    print('Error DAQbufferPoolRelease {}'.format(error))


dig.close()

print("Done.")