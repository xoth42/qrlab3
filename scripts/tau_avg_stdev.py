# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:01:00 2021

@author: Wang_Lab
"""

#0 firld
import numpy as np

tau_g = [.33,.318,.394,.335,.299,.352,.322,.403,.349,.321]
tau_e = [.301,.313,.368,.275,.299,.295,.275,.353,.262,.336]
tau_g = np.asarray(tau_g)
tau_e = np.asarray(tau_e)
print('ave_tau_g 0T= %s +/- %s us'%(np.average(tau_g), np.std(tau_g)/(np.sqrt(len(tau_g)-1))))
print('ave_tau_e 0T= %s +/- %s us'%(np.average(tau_e), np.std(tau_e)/(np.sqrt(len(tau_e)-1))))


tau_g_ = [.665,.614,.835,.737,.542,.618,.552,.659,.558,.526]
tau_e_ = [.868,.477,.783,.541,.514,.561,.737,.584,.542,.501]
tau_g_ = np.asarray(tau_g_)
tau_e_ = np.asarray(tau_e_)
print('ave_tau_g .05T= %s +/- %s us'%(np.average(tau_g_), np.std(tau_g_)/(np.sqrt(len(tau_g_)-1))))
print('ave_tau_e .05T= %s +/- %s us'%(np.average(tau_e_), np.std(tau_e_)/(np.sqrt(len(tau_e_)-1))))