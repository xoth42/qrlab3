# -*- coding: utf-8 -*-
"""
Created on Sun July 10 23:34:46 2019

@author: Wang_Lab
"""

'''
Reading data from ab time domain decay data from HDF5 file to perform analysis. 

fit lorentzian cruves to get cavity temperatures. Requires the path information to be filled out. Also requires
the min_x and max_x to be specified for the lorentaizn peak you want to fit.
Take amplitude values to calculate the temp.

Chen Wang
'''
#
#t1_result_c = []
#t1_err_c = []
#

import os
import time
import h5py as h5
import numpy as np
import matplotlib.pyplot as pl
import json
import time

from scripts.single_qubit import T1measurement


''' Path to the .hdf5 file '''

filepath = 'C:\Users\wanglab\Desktop\hdf5_copies'
hdf5_name = '\Fluxonium31october.hdf5'
#hdf5_name = '20190204 Cooldown.hdf5'
date = '20210118'
#

timetable = ['013503', '013722', '013940', '014158', '014416', '014634', '014854', '015114', '020130', '020352', '020615']
#timetable = ['185244','185353', '185502', '185611', '185720', '185828', '185937', '190046', '190155', '190303', '190412', '190521', '190629']
#timetable = ['002355', '002716', '003038', '003400', '003722', '004044', '004406', '004728', '005050', '005412', '005837', '010301',
#             '010623', '010944', '011306', '011628', '011949', '012311', '012955', '013317', '013638', '014000', '014321']
##



#timetable = ['195743', '200104', '200425', '200746', '201107', '201428', '201749', '202110', '202431', '202752', '203113', 
#             '203536', '203857', '204218', '204539', '204900', '205221','205543', '205904', '210225', '210545', '210906', '211227', '211548', '211909', '212230', '212552', '212913', 
#             '213234', '213555', '213917', '214238', '214600', '214921', '215242', '215603', '215924', '220348', '220709', '221031', '221352', '221713', '222034', '222355', '222717', '223038', '223400', 
#             '223721', '224042', '224404', '224725', '225047', '225408', '225730', '230051', '230412', '230733', '231054', '231416']
#
#timetable = ['022935','023150', '023620','023835', '024051','024306', '024521', '024737', '024952', '025208', 
#             '025423', '025638', '025854', '030109', '030324', '030539', '030753', '031008', '031223', '031438', '031652', '031907',
#             '032123', '032339', '032554', '032809', '033024', '033238', '033453', '033709', '033924', '034139', '034354', 
#             '034608', '034823', '035038', '035253','035509', '035724', '035939', '040154', '040410', '040625', '040840', 
#             '041056', '041311','041526','041741', '041956', '042212', '042427', '042643', '042858', '043114', '043329','043544',
#             '043759', '044014', '044229', '044444', '044659', '044915', '045130', '045345', '045600', '045816', '050031', '050247', 
#             '050247', '050502', '050717', '050932', '051148', '051404', '051619', '051834', '052049', '052305', '052520', '052735','052950',
#             '053205', '053421', '053636', '053851', '054106', '054322', '054538', '054754', '055009', '055226', '055441', '055656', '055911', '060127', '060342', '060557', 
#             '060813', '061028', '061244', '061500', '061716', '061931', '062146', '062402', '062617', '062833', 
#             '063049', '063305', '063521', '063737', '063952', '064208', '064424', '064639', '064855', '065110', '065325', '065541', '065757', '070012', '070228', 
#             '070444', '070659', '070915', '071131', '071347', '071603', '071819', '072035', '072250', '072506', '072722', '072938', '073153', '073409', '073625', '073841', '074057', 
#             '074312', '074528', '074743', '074959', '075215', '075431', '075647', '075904', '080120', '080336', '080552', '080808', '081024', '081240', '081456', '081713', '081928', 
#             '082144', '082400', '082616', '082832', '083049', '083304', '083521', '083737', '083953', '084210', '084426', 
#             '084642', '084858', '085114', '085330', '085546', '085844', '090100', '090316', '090532', '090748', '091004', 
#             '091221', '091437', '091653', '091909'
#             ]
#    
for i in range(11):
    timet = timetable[i]
#time = '143054'

    experiment = 'T1Measurement'
    
    ''' Primary x axis and secondary if 2d'''
    x_key = 'delays'
    #x2_key = 'powers'
    
    f = h5.File(filepath + hdf5_name, 'r')
    exp = f['/' + date + '/' + timet + '_' + experiment]
    
    
    
    
    
    
    qubit_info = mclient.get_qubit_info('qubit1ge')
    xs = exp['delays'].value
    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                         xs, 
                                         double_exp=False, plot_seqs=False, proj_func='phase', seq=None, keep_data=False) 
    
    
    
    data = exp['avg_pp'].value
    t1.avg_data = exp['avg_pp']
    t1.analyze(data = data)
    #pl.figure()
    #pl.plot(xs,ys,linestyle='-', marker='o', markersize=3, markerfacecolor='red' )
    fig = t1.fig
    #t1_result.append(t1.fit_params['tau'].value)
    #t1_err.append(t1.fit_params['tau'].stderr)
    #t1_ofs.append(t1.fit_params['ofs'].value)
    #t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    #t1_amp.append(t1.fit_params['amplitude'].value)
    #t1_amp_err.append(t1.fit_params['amplitude'].stderr)
    #t1_amp2.append(t1.fit_params['amplitude2'].value)
    #t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
    #t1_result2.append(t1.fit_params['tau2'].value)
    #t1_err2.append(t1.fit_params['tau2'].stderr)
    #T1_Ypoints.append(t1.get_ys())
    
    
#    pl.show()
    #plt.close()
    
    
    #t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
    #                                     np.concatenate((np.linspace(0,0,50), np.linspace(0.1e3, 1.9e3, 31), np.linspace(2e3, 20e3, 56), np.linspace(20.1e3, 450e3, 60))), 
    #                                     double_exp=True, generate=True, plot_seqs=False, proj_func='phase', seq=None) 
    #t1.measure_keysight()
    #
    #t1_ofs.append(t1.fit_params['ofs'].value)
    #t1_ofs_err.append(t1.fit_params['ofs'].stderr)
    #t1_amp.append(t1.fit_params['amplitude'].value)
    #t1_amp_err.append(t1.fit_params['amplitude'].stderr)
    #t1_amp2.append(t1.fit_params['amplitude2'].value)
    #t1_amp2_err.append(t1.fit_params['amplitude2'].stderr)
    #t1_result2.append(t1.fit_params['tau2'].value)
    #t1_err2.append(t1.fit_params['tau2'].stderr)
    T1_Ypoints.append(t1.get_ys())
    
    ys = data
    
    #pl.plot(xs,ys,linestyle='-', marker='o', markersize=3, markerfacecolor='red' )
    #print(ys)
    
    
    
    
#    pl.show()
    
    
    t1_result_c.append(t1.fit_params['tau'].value)
    t1_err_c.append(t1.fit_params['tau'].stderr)
    time.sleep(1)