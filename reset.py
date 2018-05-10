# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:04:09 2017

@author: Jeff 'do you have a better solution?' Gertler
Modified by Josh

Resets the instrument gui if it is frozen. This is the shittiest workaround.
"""
import time
while True:
    from mclient import instruments
    try:
        alz = instruments['alazar']
        alz.set_naverages(alz.get_naverages())
    except:
        pass
        #print('no alazar')

        try:
            awg = instruments['AWG1']
            awg.set_reffreq(awg.get_reffreq())
        except:
            #print('no awg')
            pass
    #Added by Josh
    try:
        reset_readout = instruments['readout']
        reset_readout.set('acq_chan', 'g')
    except:
        #print "no readout"
        #time.sleep(0.01)
        pass