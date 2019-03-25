import matplotlib
matplotlib.interactive(True)

#
from mclient import instruments
VNA = instruments['VNA']
Yoko = instruments['Yoko']

import numpy as np
import datetime
import time
import matplotlib.pyplot as pl
import objectsharer as objsh


#date = datetime.datetime.now()
datasrv = objsh.helper.find_object('dataserver')
filename = 'c:/_data/YIG_Copper_Cavity_sweep_test.hdf5'
datafile = datasrv.get_file(filename)
ts = time.localtime()
tstr = time.strftime('%Y%m%d/%H%M%S', ts)
datafile._timestamp_str = tstr
datafile._groupname = '%s_%s'  % (tstr, 'test')
datagroup = datafile.create_group(datafile._groupname)
datagroup.set_attrs(
    title='test with VNA.set_format in main loop',
    comment='just test'
)





#Make sure to check that repeat is off for Yoko GS200
#To do manually, press 'Program' key and press repeat is the left most option on screen



#Vi = 4.0
#Vf = 5.7
#I_i = 0.0 #Current - switched to controlling current on 2/1/19
#I_f = 0.2
#
#
##step = 1e-3
#step = 0.0004
#sleeptime = 0.05
currents = np.linspace(0,0.98,981)
freqs = np.linspace(8e9,9e9,1601)
average_factor = 1
Sij = ['S11']#,'S21','S12','S22']

datagroup.create_dataset('currents', data=currents)
datagroup.create_dataset('freqs', data = freqs)
#        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.currents),len(freqs)])
#        self.phasedata = self.data.create_dataset('phases', shape=[len(self.currents),len(freqs)])
print datagroup.get_fullname()
realdata = [0,0,0,0]
imagdata = [0,0,0,0]
for i, sij in enumerate(Sij):
    
    realdata[i] = datagroup.create_dataset('real%s'%(sij), shape=[len(currents),len(freqs)])
    imagdata[i] = datagroup.create_dataset('imaginary%s'%(sij), shape=[len(currents),len(freqs)])

#foldername = 'C:\Users\WangLab\Documents\\yingying\\circulator\\20190109' 
#foldername = r"C:\Users\WangLab\Documents\TConnolly\calibrated_circulator\transition1-3"
#filename = '%s\\circulator_S11_4_14_%s_%s_%s_7.5mm_pins_port3_terminated_%s-%s-%s.txt'%(foldername,Vi,Vf,step,date.hour,date.minute,date.second)
#Check and change angle before running angular experiments
#filename = '%s\\s11_2_term%s-%s-%s_Date_%s-%s_%s-%s-%s.txt'%(foldername,I_i,I_f,step,date.month,date.day,date.hour,date.minute,date.second)

  #magnetic field step
#range = yoko.select_voltage_range(10)
#yoko.do_set_source_range(range)

#m = Mi  
#v = Vi
#VNA.set_s_param('S11')

Yoko.do_set_output_state(0)
VNA.set_start_freq(freqs[0])
VNA.set_stop_freq(freqs[-1])
VNA.set_points(len(freqs))
timelimit = 16 # breaks long time measurement to severals 300 seconds.
avelimit = int(timelimit/VNA.get_sweep_time())

if avelimit<1:
    avelimit = 1
if avelimit >999:
    avelimit = 999
    
if average_factor < avelimit:
    avelimit = average_factor
    
VNA.set_average_factor(avelimit)

for icurrent, current in enumerate(currents):
    Yoko.do_set_current(current)
#    time.sleep(0.5)
    ave = avelimit
    if average_factor > avelimit:
        VNA.set_average_factor(ave)
    count = 0

    while count < average_factor:
        ave = avelimit
        
        if (average_factor-count) < avelimit:
            ave = average_factor-count
            VNA.set_average_factor(ave)
        
        reals = []
        imags = []


#            VNA.set_trigger_source('internal')
#            VNA.set_average_factor(40)

        VNA.set_trigger_source('BUS')
#        VNA.write('INIT:CONT ON')

#        VNA.set_averaging_trigger(1)
        
        VNA.trigger()
        
        wait = VNA.opc(async=True) # wait for completion

#            print 'ok7'
#                a=0
        try:
            while not wait.is_valid():
#                        if a % 10 == 0:
#                            print 'async', a 
#                        a= a + 1
                
#                    time.sleep(0.1)
                objsh.helper.backend.main_loop(100)
                VNA.set_format('REAL')
        except:
            print 'error with async'
#                VNA.set_interrupt(True)
#        '''

#            print 'ok8'
        for i, sij in enumerate(Sij):
            VNA.set_s_param(sij)
            prev_fmt = VNA.get_format()
            freqs = VNA.do_get_xaxis()
            VNA.set_format('REAL')
            ret = VNA.do_get_yaxes()
            reals = ret[0]
            VNA.set_format('IMAG')
            ret = VNA.do_get_yaxes()
            imags = ret[0]
            VNA.set_format(prev_fmt)
        

            if count == 0:
                
#                    self.freqdata[0,:] = freqs
        #        print freqs
        #        print self.freqdata
                realdata[i][icurrent,:] = reals
                imagdata[i][icurrent,:] = imags
    
    
            else:
                reals =( reals *ave + realdata[i][icurrent,:] * count)/float(ave+count)
                imags =( imags *ave + imagdata[i][icurrent,:] * count)/float(ave+count)
                realdata[i][icurrent,:] = reals
                imagdata[i][icurrent,:] = imags


            VNA.set_trigger_source('internal')
        count = count + ave
        print '%s averages done' %(count)
    
    print 'current = %.04fmA done ' % (current)
    
    


    
#    Yoko.do_set_source_range('10E+0') # fixes range problem
#    Yoko.set_voltage_ramp(level, slew = 10) # slew is rate of change of voltage
#    Yoko.do_set_current(I)
#    time.sleep(sleeptime)
#    
#    
#    #mag.do_set_field(N) #commmand for using arduino power supply  
#    Mag.append(I)
#    
#    datanew = VNA.do_get_data()
#    valuenew = datanew[0]
#    phasenew = datanew[1]
#    valuenew = valuenew[:,None].T
#    phasenew = phasenew[:,None].T
#
#    value = np.concatenate([value,valuenew])
#    phase = np.concatenate([phase,phasenew])
#    
#    I = I+step
##    s_params = ['S11','S21','S12','S22']
#
##    for sij in s_params:
##        VNA.set_s_param(sij)
##        print('done')
#    
#    
##print Mag
##Yoko.do_set_voltage(0)
##Yoko.set_voltage_ramp(0,slew=1) #Only for YOKO GS200
#
#
##axis = axis / float(1000000000)
#X, Y = np.meshgrid(Mag, axis)
#Z = np.transpose(value)
#phase = np.transpose(phase)

#save the data as a file
#to_save = [X, Y, Z, phase]
#with file(filename,'w') as outfile:
#    outfile.write('# new slice\n')
#
#    # Iterating through a ndimensional array produces slices along
#    # the last axis. This is equivalent to data[i,:,:] in this case
#    for data_slice in to_save:
#
#        # The formatting string indicates that I'm writing out
#        # the values in left-justified columns 7 characters in width
#        # with 2 decimal places.  
#        np.savetxt(outfile, data_slice, fmt='%-7.7f')
#
#        # Writing out a break to indicate different slices...
#        outfile.write('# New slice\n')
#
#pl.figure()
#pl.pcolormesh(X, Y, Z)
#pl.colorbar()
#pl.xlabel('Magnetic Field Current (mA)')
#pl.ylabel('Frequency')
#pl.show()   
#
#vlist = np.arange(I,I_i,-step) 
#for i in vlist[1:]:
#    print i
#    Yoko.do_set_current(i)
#    time.sleep(0.1)

    
