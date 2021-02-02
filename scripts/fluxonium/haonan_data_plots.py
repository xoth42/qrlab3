# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 11:21:15 2020

@author: wanglab
"""
import mclient
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
import matplotlib.pyplot as plt
import os
import lmfit

#Interleaved RB, error per clifford: 0.0964 +- 0.0012
#Non interleaved RB, error per clifford: 0.0748 +- 0.0009
#Error per CZ (Interleaved - noninterleaved): 0.0216 +- 0.0015
#Error per Pauli CYCLE for XEB: 0.0436 +- 0.0013


def RB_fit(ys, xs, std, N, label='', F_final=0.5, F_init=1.0, fig=None):    
    err = std/np.sqrt(N)

    def exp_decay(params, x, data):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return (data-est)

    def exp_decay2(params, x):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return est

    params=lmfit.Parameters()
    params.add('amplitude', value=F_init-F_final, vary=True)
    params.add('ofs', value=F_final, vary=False)
    params.add('tau', value=len(xs))
    result= lmfit.minimize(exp_decay, params, args=(xs,ys))
    lmfit.report_fit(result.params)
    EPC = (1-F_final-(1-F_final)*np.exp(-1.0/result.params['tau']))
    print ("EPC: %f" %(EPC))
    label = label+"EPC: %.4f" %(EPC)
    if fig==None:
        fig, ax=plt.subplots(1)
    else:
        ax = fig.axes[0]
    ax.plot(xs, exp_decay2(result.params,xs), markersize =4)
    ax.errorbar(xs,ys,err, markersize=2, linestyle='None', capsize=2, color='black')
    ax.plot(xs,ys, 'o', markersize=3, linestyle='None', label=label)#color='magenta')
    ax.plot(xs,np.transpose(ys), '.', markersize=3, linestyle='None')

    ax.set_ylabel('Average fidelity')
    ax.set_xlabel('Number of Cliffords')
    fig.axes[0].legend(loc=0)
    
    return fig


def XEB_fit(ys, xs,  label='', F_final=0.5, F_init=1.0, fig=None):    

    def exp_decay(params, x, data):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return (data-est)

    def exp_decay2(params, x):
        est=params['ofs'] + params['amplitude'] * np.exp(-x/params['tau'].value)
        return est

    params=lmfit.Parameters()
    params.add('amplitude', value=F_init-F_final, vary=True)
    params.add('ofs', value=F_final, vary=True)
    params.add('tau', value=len(xs))
    result= lmfit.minimize(exp_decay, params, args=(xs,ys))
    lmfit.report_fit(result.params)
    Pauli_EPC = (15.0/16.0)*(1-F_final-(1-F_final)*np.exp(-1.0/result.params['tau']))
    print ("Pauli EPC: %f" %(Pauli_EPC))
    label = label+"Pauli EPC: %.4f" %(Pauli_EPC)

    if fig==None:
        fig, ax=plt.subplots(1)
    else:
        ax = fig.axes[0]
    ax.plot(xs, exp_decay2(result.params,xs), markersize =4)
    ax.plot(xs,ys, 'o', markersize=3, linestyle='None', label=label)#color='magenta')
    ax.plot(xs,np.transpose(ys), '.', markersize=3, linestyle='None')

    ax.set_ylabel('Average fidelity')
    ax.set_xlabel('Number of Cycles')
    fig.axes[0].legend(loc=0)
    
    return fig

#Non interleaved RB 
RB_xs = np.array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17,
       18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
       35])

non_interleaved_ys = np.array([0.76469352, 0.73100216, 0.69320081, 0.63846677, 0.59882404,
       0.56013413, 0.53559452, 0.49219972, 0.47285907, 0.443358  ,
       0.42808998, 0.42331725, 0.39080903, 0.37841788, 0.37070981,
       0.37414227, 0.35264708, 0.34560657, 0.32974552, 0.31453596,
       0.33048267, 0.30986946, 0.30900949, 0.29685231, 0.29159133,
       0.27882592, 0.28762804, 0.27664901, 0.27815495, 0.27540573,
       0.26910246, 0.26930512, 0.27134208, 0.26771394, 0.25852115])
    
non_interleaved_std=np.array([0.05482038, 0.05587171, 0.04370181, 0.05149624, 0.0501389 ,
       0.04909424, 0.04930237, 0.04918388, 0.05158702, 0.05165563,
       0.06019308, 0.04733957, 0.04371979, 0.04798974, 0.04414301,
       0.04784951, 0.04547843, 0.03510388, 0.04088223, 0.03681135,
       0.03494727, 0.04196368, 0.0292752 , 0.03753891, 0.03872271,
       0.03517076, 0.02951622, 0.03770507, 0.03606626, 0.03535069,
       0.03765565, 0.03722829, 0.03247045, 0.03738816, 0.03474668])    
    
    
RB_fit(non_interleaved_ys, RB_xs, non_interleaved_std, N=45,  F_final=0.25, F_init=1-0.1)
plt.title("Non-interleaved RB", fontsize=12)

#interleaved RB with CZ
interleaved_ys = np.array([0.75203281, 0.68247276, 0.63539446, 0.58154914, 0.54378081,
       0.51075212, 0.4767969 , 0.45557806, 0.41266091, 0.40507365,
       0.36952782, 0.35361331, 0.33433377, 0.33536193, 0.32509759,
       0.30685477, 0.31393955, 0.28785127, 0.29089179, 0.28077348,
       0.27577344, 0.27520508, 0.28041008, 0.26811962, 0.26859535,
       0.27217191, 0.26804241, 0.27100031, 0.25633297, 0.26577804,
       0.26845775, 0.25579683, 0.25090348, 0.25744625, 0.24920147])
    
    
interleaved_std= np.array([0.04857914, 0.04726303, 0.049784  , 0.047457  , 0.05178827,
       0.05451157, 0.03751931, 0.03724491, 0.0323818 , 0.04611098,
       0.03667586, 0.03332835, 0.03704725, 0.03985792, 0.03422019,
       0.03207928, 0.04258983, 0.03139766, 0.03914465, 0.03112892,
       0.03571677, 0.03312422, 0.0388999 , 0.03067032, 0.03553495,
       0.03194525, 0.0323623 , 0.03282971, 0.03483237, 0.03473505,
       0.03776862, 0.03267745, 0.02891176, 0.03575634, 0.03188529])


RB_fit(interleaved_ys, RB_xs, non_interleaved_std, N=45,  F_final=0.25, F_init=1-0.1)
plt.title("Interleaved RB with CZ", fontsize=12)


#XEB

XEB_xs = np.array([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11., 12., 13.,
       14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25., 26.,
       27., 28., 29., 30., 31., 32., 33., 34., 35., 36., 37., 38., 39.,
       40., 41., 42., 43., 44., 45., 46., 47., 48., 49., 50., 51., 52.,
       53., 54., 55., 56., 57., 58., 59., 60., 61., 62., 63., 64., 65.,
       66., 67., 68., 69., 70.])
    
    
XEB_ys= np.array([ 0.88052009,  0.84535856,  0.80298981,  0.83514279,  0.72098571,
        0.68435349,  0.66289694,  0.65214263,  0.59850222,  0.57500091,
        0.57539849,  0.54765865,  0.5610301 ,  0.47078658,  0.46455514,
        0.41889615,  0.43007179,  0.37574757,  0.35504479,  0.35025118,
        0.37565024,  0.34515767,  0.28834024,  0.30283816,  0.25241064,
        0.24618955,  0.23669563,  0.24439693,  0.23509035,  0.22090648,
        0.25461083,  0.20511267,  0.17331813,  0.14704416,  0.17081299,
        0.15151852,  0.15751836,  0.13172206,  0.15672289,  0.12663085,
        0.1194901 ,  0.08322782,  0.12411246,  0.12332939,  0.09924889,
        0.14570933,  0.11765639,  0.1059706 ,  0.09094827,  0.10500071,
        0.10039904,  0.07545753,  0.05352115,  0.06017406,  0.06945085,
        0.04813341,  0.06974827,  0.05944777,  0.07160355,  0.05798262,
        0.0260067 ,  0.04264266,  0.02421063,  0.04435247,  0.03723344,
       -0.00925328,  0.0238095 ,  0.02493709,  0.03552547,  0.05266509])   
    
XEB_fit(XEB_ys, XEB_xs,  F_final=0, F_init=1)
plt.title("XEB", fontsize=12)
