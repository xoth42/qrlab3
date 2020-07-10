# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:17:08 2019

@author: WangLab
"""
#kappa_55dB = kappa_10mK[0]
#kappa_err_55dB = kerr_10mK[0]
#kappa_10mK = kappa_10mK[1:]
#kerr_10mK = kerr_10mK[1:]
#T = [10,15,20,30,40,50]
#LW = np.zeros([len(T),len(kappa_10mK)])
#LW_err = np.zeros([len(T),len(kappa_10mK)])
#LW[0] = kappa_10mK
#LW[1] = kappa_15mK
#LW[2] = kappa_20mK
#LW[3] = kappa_30mK
#LW[4] = kappa_40mK
#LW[5] = kappa_50mK
#LW_err[0] = kerr_10mK
#LW_err[1] = kerr_15mK
#LW_err[2] = kerr_20mK
#LW_err[3] = kerr_30mK
#LW_err[4] = kerr_40mK
#LW_err[5] = kerr_50mK
#powers = power_50mK
LW_err = np.transpose(LW_err)
pl.figure()
for i in range(len(powers)):
     pl.errorbar(T, LW[i]/1000000, yerr = LW_err[i]/1000000, fmt ='o', label='%sdB'%(powers[i]))



pl.xlabel('T(mK)', fontsize = 15)
pl.ylabel('linewidth(MHz)', fontsize = 15)
pl.legend()
pl.show()     
np.savetxt(r'C:\Users\WangLab\Documents\\yingying\\0808cooldown\\LW.txt' , LW , delimiter=",")
     
np.savetxt(r'C:\Users\WangLab\Documents\\yingying\\0808cooldown\\LW_err.txt' , LW_err , delimiter=",")    
np.savetxt(r'C:\Users\WangLab\Documents\\yingying\\0808cooldown\\T.txt' , T , delimiter=",")  