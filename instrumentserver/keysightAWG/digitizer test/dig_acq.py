import keysightSD1 as key
import numpy as np
import matplotlib.pyplot as plt




DIG_PRODUCT = "M3102A"
CHASSIS = 0
DIG_SLOT = 3


dig = key.SD_AIN()
ainID = dig.openWithSlot(DIG_PRODUCT, CHASSIS, DIG_SLOT)

DIGPart = dig.getProductNameBySlot(CHASSIS, DIG_SLOT)
DIGNumber = dig.getSerialNumberBySlot(CHASSIS,DIG_SLOT)
DIGNumModules = dig.moduleCount()
print("Part =", DIGPart)
print("S/N =", DIGNumber)
print("Number of Modules = ", DIGNumModules)






AWG_PRODUCT = "M3202A"
CHASSIS = 0
AWG_SLOT = 7

awg = key.SD_AOU()
aouID = awg.openWithSlot(AWG_PRODUCT, CHASSIS, AWG_SLOT)

# Gather Information about AWG S/N, Slot and S/N
AWGPart = awg.getProductNameBySlot(CHASSIS, AWG_SLOT)
AWGNumber = awg.getSerialNumberBySlot(CHASSIS, AWG_SLOT)
AWGNumModules = awg.moduleCount()
print("Part =", AWGPart)
print("S/N =", AWGNumber)
print("Number of Modules = ", AWGNumModules)






#set up full scale, input impedance and AC/DC coupling for Digitizer channels
Voltage_Scale = 2.8 # Scale > 3 saturates the Digitizer input and folds the waveform causing unwanted wave shape
dig.channelInputConfig(1 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
dig.channelInputConfig(2 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
dig.channelInputConfig(3 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)
dig.channelInputConfig(4 , Voltage_Scale,key.AIN_Impedance.AIN_IMPEDANCE_50, key.AIN_Coupling.AIN_COUPLING_DC)

# Check DIG Connection
if ainID < 0:
    print("ERROR")
    print("ainID:", ainID)
    print()
    print("AIN closed")

data_filepath = "C:\\qrlab\instrumentserver\keysightAWG\data\\"
print(data_filepath)

#intitialize Digitizer
dig.DAQflushMultiple(15)


##SET UP EXTERNAL DIGITAL TRIGGER
#PROGRAM Trig IN/Out as INPUT PORT - def triggerIOconfig(self, direction
dig.triggerIOconfig(key.SD_TriggerDirections.AOU_TRG_IN)
#EXTERNAL DIGITAL TRIGGER BEHAVIOR - def DAQdigitalTriggerConfig(self, channel, triggerSource, triggerBehavior)
dig.DAQdigitalTriggerConfig(1, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH)
dig.DAQdigitalTriggerConfig(2, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 
dig.DAQdigitalTriggerConfig(3, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 
dig.DAQdigitalTriggerConfig(4, key.SD_TriggerExternalSources.TRIGGER_EXTERN, key.SD_TriggerBehaviors.TRIGGER_HIGH) 


#CONFIGURE DAQ3 FOR CAPTURING RABI SWEEP - DAQconfig(self, nDAQ, nDAQpointsPerCycle, nCycles, prescaler, triggerMode)


num_ave = 1
num_aq = 500
ave_per_buf = 1
num_points = 1
#num_aq = 100
timeout = 2000
delay = 0

samp_array = np.zeros((4, num_ave, num_aq * num_points))
for ave in range(0, num_ave, ave_per_buf):
    dig.DAQconfig(1, num_aq, ave_per_buf * num_points, delay, key.SD_TriggerModes.EXTTRIG)
    dig.DAQconfig(2, num_aq, ave_per_buf * num_points, delay, key.SD_TriggerModes.EXTTRIG)
#    dig.DAQconfig(3, num_aq, num_ave, delay, key.SD_TriggerModes.EXTTRIG)
#    dig.DAQconfig(4, num_aq, num_ave, delay, key.SD_TriggerModes.EXTTRIG)
    
    
    #dig.DAQstart(1)
    awg.AWGstopMultiple(15)
    dig.DAQstartMultiple(15)
    awg.AWGstartMultiple(15)
    
    #READ DAQ BUFFER FOR ACQUIRED DATA
    for i in range(0, ave_per_buf):
        for n in range(2):
            temp = dig.DAQread(n+1, num_aq * num_points, timeout)
            if(len(temp) == num_aq * num_points):
                samp_array[n][ave + i] = temp
            else:
                print('return from DAQread is not num_aq')
                print('i', i, 'n', n, 'len(ret)', len(temp), 'num_aq', num_aq * num_points)

    dig.DAQstopMultiple(15)


#samp_array /= num_ave
plt.clf()
for i in range(num_ave):
    plt.plot(samp_array[0][i], label = 'sig ' + str(i+1))
    plt.plot(samp_array[1][i][:], label = 'ref ' + str(i+1), markersize = 1)

for i in range(num_points):
    plt.axvline(i * num_aq)


#plt.plot(samp_array[0][9000:12000], label = 'channel 1')
#plt.plot(samp_array[1][8500:13000], label = 'channel 2')
#plt.plot(samp_array[2], label = 'channel 3')
#plt.plot(samp_array[3], label = 'channel 4')

plt.legend()
plt.show()
#plt.clf()

#STOP DIG
#awg.AWGstopMultiple(15)

#    





