# -*- coding: utf-8 -*-
"""
Created on Mon Apr 02 19:33:47 2018

@author: Wang_Lab
"""
import time
import os
import glob
f = open(r'C:\qrlab\FMR\CH6 T 18-04-02.log')
tdata = f.readlines()
for filename in glob.glob('*.txt'):
#filelist = ('C:\qrlab\FMR')
#for filename in filelist:
    t= time.ctime(os.path.getctime(r'C:\qrlab\FMR\%s'%(filename)))
    t1 = t[11:16]
    print t,t1
    timelist = []
    timelist.append(t)

    for t in tdata:
    #    print t[10:15]
        if t1==t[10:15]:
            print t
            print t[19:]