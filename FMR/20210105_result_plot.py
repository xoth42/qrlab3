# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 23:02:53 2021

@author: Wang_Lab
"""
import matplotlib.pyplot as pl
import numpy as np

#fields = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0, -.01, -.02, -.03, -.04, -.05]
#
#chi_qc = [0.47, 0.476 , -0.609, 0.022, 0.015, .001, 0.389, .370, -0.991, -0.006, 0.012, .008]
#
#chi_qc_err = [0.016, 0.022, 0.094, 0.017, 0.007, .017, .077, .032, 0.157,.012, 0.006, .008]
#
#fields_reorder = fields[-1:-7:-1] + fields[0:6]
#chi_qc_reorder = chi_qc[-1:-7:-1] + chi_qc[0:6]
#chi_qc_err_reorder = chi_qc_err[-1:-7:-1] + chi_qc_err[0:6]
#pl.figure()
#pl.errorbar(fields_reorder, chi_qc_reorder, yerr = chi_qc_err_reorder, label = 'qubit to cavity')
#pl.errorbar([-0.019,-0.02,-0.021], [0.258 ,-0.069 ,-0.892], yerr = [0.159, 0.109, 0.07], marker = 'o', label = 'qubit to cavity')
#
#stark_shift = [2.379,2.533,7.222,12.966,14.749,3.824,3.805,2.363,5.016,8.444,10.350]
#stark_shift_reorder = stark_shift[-1:-7:-1] + stark_shift[0:5]
#stark_shift_reorder = np.asarray(stark_shift_reorder)
#
#fields1 = np.linspace(-0.05,0.05,11)
#SS_freq = [0.03068945, 0.19863421, 0.25514084, 0.63475428, 1.17383627,
#       0.84346661, 0.45126846, 0.05289743, 0.02049829, 0.05316276,
#       0.02924217]
#
#photon = stark_shift_reorder/1.668
#pl.title('Chi_qc vs. Chi_cq')
#pl.xlabel('Fields (T)')
#pl.ylabel('Shift Frequency(MHz)')
#pl.plot(fields1, np.asarray(SS_freq)/photon, label = 'cavity to qubit')
#pl.legend()

fields = [0,0.005, 0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0, -.01, -.02, -.03, -.04, -.05]

chi_qc = [0.402, 0.395 , 0.348, 0.541, -0.161, .014, 0.019, -0.002, 0.408, 0.435, -1.103, 0.086,0.012,0.003]

chi_qc_err = [0.025, 0.069, 0.017, 0.032, 0.08, .008, .013, .015, 0.014,.051, 0.096, .018,0.009,0.014]

fields_reorder = fields[-1:-7:-1] + fields[0:8]
chi_qc_reorder = chi_qc[-1:-7:-1] + chi_qc[0:8]
chi_qc_err_reorder = chi_qc_err[-1:-7:-1] + chi_qc_err[0:8]
pl.figure()
pl.errorbar(fields_reorder, chi_qc_reorder, yerr = chi_qc_err_reorder, label = 'qubit to cavity')
#pl.errorbar([-0.019,-0.02,-0.021], [0.258 ,-0.069 ,-0.892], yerr = [0.159, 0.109, 0.07], marker = 'o', label = 'qubit to cavity')

stark_shift = [ 2.188,1.009,2.374,1.7611,2.065,5.944,10.44,11.788,3.302,2.218,2.065,6.578,10.363,13.486]
stark_shift_reorder = stark_shift[-1:-7:-1] + stark_shift[1:8]
stark_shift_reorder = np.asarray(stark_shift_reorder)

fields1 = fields[-1:-6:-1] + fields[0:8]
SS_freq = [ 0.05354174,  0.18679778,  0.32535741,  0.51031509,  1.05245357,
        1.28593525,  0.25120889,  0.51827799,  0.1841299 ,  0.0308364 ,
       -0.0090656 ,  0.01136863,  0.08280696]

photon = stark_shift_reorder/1.668
pl.title('Qubit to Cavity Chi')
pl.xlabel('Fields (T)')
pl.ylabel('Shift Frequency(MHz)')
#pl.plot(fields1, np.asarray(SS_freq)/photon, label = 'cavity to qubit')
pl.legend()









