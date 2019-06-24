# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 19:09:32 2019

@author: WangLab
"""

import matplotlib
matplotlib.interactive(True)

#
import mclient
reload(mclient)
from mclient import instruments

VNA = instruments['VNA']
Yoko = instruments['Yoko']

import numpy as np
import datetime
import time
import matplotlib.pyplot as pl
import objectsharer as objsh


currents = np.linspace(0,0.1,1001)
freqs = np.linspace(8e9,9e9,201)
average_factor = 1
Sij = ['S11','S21','S12','S22','S00','S01','S02','S03']
timelimit = 16 # breaks long time measurement to severals 16 seconds.
main_loop_time = 100
IF_bandwidth = 10000


#VNA.set_if_bandwidth('%s'%(IF_bandwidth))
#VNA.set_timeout(40000)
#avelimit = int(timelimit/VNA.get_sweep_time())
avelimit = 1

    
if average_factor < avelimit:
    avelimit = average_factor
    


datasrv = objsh.helper.find_object('dataserver')
filename = 'c:/_data/YIG_Copper_Cavity_sweep_test.hdf5'
datafile = datasrv.get_file(filename)
ts = time.localtime()
tstr = time.strftime('%Y%m%d/%H%M%S', ts)
datafile._timestamp_str = tstr
datafile._groupname = '%s_%s'  % (tstr, 'test')
datagroup = datafile.create_group(datafile._groupname)
datagroup.set_attrs(
    title='test with no VNA',
    comment='no YOKO, creat random data',
    VNA_IF_bandwidth = VNA.get_if_bandwidth(),
    total_average_factor = average_factor,
    mainlooptime = main_loop_time,
    stop_at = '0/%s'%(len(currents)),
    VNA_average_factor = avelimit,   
)




datagroup.create_dataset('currents', data=currents)
datagroup.create_dataset('freqs', data = freqs)
#        self.ampdata = self.data.create_dataset('amplitudes', shape=[len(self.currents),len(freqs)])
#        self.phasedata = self.data.create_dataset('phases', shape=[len(self.currents),len(freqs)])
print datagroup.get_fullname()
realdata = [0,0,0,0,0,0,0,0]
imagdata = [0,0,0,0,0,0,0,0]
for i, sij in enumerate(Sij):
    
    realdata[i] = datagroup.create_dataset('real%s'%(sij), shape=[len(currents),len(freqs)])
    imagdata[i] = datagroup.create_dataset('imaginary%s'%(sij), shape=[len(currents),len(freqs)])


'''    
objsh.helper.backend.main_loop(1000)

for icurrent, current in enumerate(currents):
    datagroup.set_attrs(stop_at = '%s/%s'%(icurrent +1, len(currents)))
    ave = avelimit

    count = 0

    while count < average_factor:
        ave = avelimit
        

#            print 'ok8'
        for i, sij in enumerate(Sij):

            reals = np.random.random_sample(len(freqs))
            imags = np.random.random_sample(len(freqs))
        

            if count == 0:
                

                realdata[i][icurrent,:] = reals
#                print('real:',realdata[i][icurrent,:])
#                print datagroup.keys()
#                objsh.helper.backend.connect_to('tcp://127.0.0.1:55556')
                imagdata[i][icurrent,:] = imags
#                print('imag:',imagdata[i][icurrent,:])
    
    
            else:
                reals =( reals *ave + realdata[i][icurrent,:] * count)/float(ave+count)
                imags =( imags *ave + imagdata[i][icurrent,:] * count)/float(ave+count)
                realdata[i][icurrent,:] = reals
                imagdata[i][icurrent,:] = imags


#        VNA.set_trigger_source('internal')
        count = count + ave
#        print '%s averages done' %(count)
    
    print 'current = %.04fmA done ' % (current)
'''