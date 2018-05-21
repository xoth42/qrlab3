# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 12:04:09 2017

@author: Jeff 'do you have a better solution?' Gertler

Resets the instrument gui if it is frozen. This is the shittiest workaround.
"""

from mclient import instruments
try:
    alz = instruments['alazar']
    alz.set_naverages(alz.get_naverages())
except:
    print('no alazar')
    
    try:
        awg = instruments['AWG1']
        awg.set_reffreq(awg.get_reffreq())
    except:
        print('no awg')

