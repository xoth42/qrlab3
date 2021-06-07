# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:20:37 2019

@author: Wang_Lab
"""

#This spectroscopy is intended to follow one specific transition over the full flux period and not to get the full spectrum of the device. It makes use of SSB spec rather than the regular spectroscopy
#with the hope that we can avoid the current crashing problem. -Ebru

#%%
import scipy.interpolate as sciint



c_low = np.array([[-3.19418233e+07, -3.19418233e+07, -6.12994684e+07,
        -8.47657287e+07, -1.12760241e+08, -1.43657278e+08,
        -1.79340851e+08, -2.21160448e+08, -2.71187684e+08,
        -3.32126453e+08, -4.07695399e+08, -5.03053290e+08,
        -6.25473603e+08, -7.85363448e+08, -9.97855912e+08,
        -1.28533354e+09, -1.68142651e+09, -2.23722435e+09,
        -3.03055140e+09, -4.17865401e+09, -5.85147714e+09,
        -8.27055202e+09, -1.16416834e+10, -1.58828796e+10,
        -1.99138072e+10, -2.06260581e+10, -1.36133309e+10,
         1.11657132e+09,  1.53177135e+10,  2.13859278e+10,
         2.00971564e+10,  1.58914711e+10,  1.16553761e+10,
         8.33756890e+09,  5.97787421e+09,  4.36585657e+09,
         3.28690897e+09,  2.58222580e+09,  2.15101427e+09,
         1.94005868e+09,  1.94852170e+09,  2.21432991e+09,
         2.96081999e+09,  4.35614061e+09,  8.29651372e+09,
         1.44923666e+10,  4.47276127e+10,  9.13368944e+10,
         4.58955076e+11,  2.81307983e+11, -5.93577353e+11,
        -2.03910832e+11, -6.32864950e+10, -2.41722825e+10,
        -1.08827217e+10, -5.77914013e+09, -3.52803482e+09,
        -2.49472011e+09, -2.03945712e+09, -1.91497836e+09,
        -2.02340117e+09, -2.34444655e+09, -2.90796629e+09,
        -3.79057679e+09, -5.12235627e+09, -7.09341629e+09,
        -9.93165954e+09, -1.37696132e+10, -1.82131322e+10,
        -2.14231258e+10, -1.93996672e+10, -8.64537828e+09,
         7.16813612e+09,  1.84462220e+10,  2.09583192e+10,
         1.79719929e+10,  1.35893597e+10,  9.75341359e+09,
         6.89848351e+09,  4.89975384e+09,  3.52645128e+09,
         2.58163880e+09,  1.92434125e+09,  1.45974124e+09,
         1.12541413e+09,  8.80373793e+08,  6.97504817e+08,
         5.58615783e+08,  4.51295172e+08,  3.66932079e+08,
         2.99460867e+08,  2.44540162e+08,  1.99034389e+08,
         1.60568827e+08,  1.27584835e+08,  9.80360578e+07,
         7.34921984e+07,  4.32840816e+07,  4.32840816e+07],
       [-4.65676300e+05, -4.68823750e+05, -4.71971200e+05,
        -4.78011463e+05, -4.86364020e+05, -4.97475070e+05,
        -5.11630621e+05, -5.29302322e+05, -5.51094799e+05,
        -5.77816808e+05, -6.10543537e+05, -6.50716600e+05,
        -7.00285939e+05, -7.61918203e+05, -8.39305525e+05,
        -9.37631208e+05, -1.06428406e+06, -1.22996671e+06,
        -1.45041598e+06, -1.74903729e+06, -2.16078913e+06,
        -2.73737586e+06, -3.55233087e+06, -4.69946690e+06,
        -6.26451748e+06, -8.22676339e+06, -1.02591923e+07,
        -1.16006085e+07, -1.14905850e+07, -9.98122413e+06,
        -7.87391994e+06, -5.89360736e+06, -4.32771020e+06,
        -3.17922493e+06, -2.35766629e+06, -1.76862477e+06,
        -1.33842656e+06, -1.01454456e+06, -7.60099891e+05,
        -5.48145496e+05, -3.56978022e+05, -1.64976627e+05,
         5.32166984e+04,  3.44966883e+05,  7.74207712e+05,
         1.59172091e+06,  3.01975458e+06,  7.42707732e+06,
         1.64271367e+07,  6.16511722e+07,  8.93704041e+07,
         3.08810995e+07,  1.07883472e+07,  4.55228870e+06,
         2.17042559e+06,  1.09807534e+06,  5.28616475e+05,
         1.80974669e+05, -6.48474528e+04, -2.65809346e+05,
        -4.54505481e+05, -6.53885271e+05, -8.84899894e+05,
        -1.17144204e+06, -1.54495393e+06, -2.04969531e+06,
        -2.74865895e+06, -3.72729444e+06, -5.08411019e+06,
        -6.87877676e+06, -8.98974634e+06, -1.09013305e+07,
        -1.17532197e+07, -1.10468934e+07, -9.22925887e+06,
        -7.16408993e+06, -5.39318449e+06, -4.05413037e+06,
        -3.09305870e+06, -2.41330314e+06, -1.93049632e+06,
        -1.58301055e+06, -1.32862373e+06, -1.13900500e+06,
        -9.95166545e+05, -8.84271663e+05, -7.97522311e+05,
        -7.28792310e+05, -6.73748012e+05, -6.29278761e+05,
        -5.93122391e+05, -5.63614429e+05, -5.39518186e+05,
        -5.19905944e+05, -5.04083981e+05, -4.91512160e+05,
        -4.81851985e+05, -4.74610288e+05, -4.70345206e+05],
       [-4.68072057e+00, -3.53749835e+01, -6.62760066e+01,
        -9.74788060e+01, -1.29154347e+02, -1.61469183e+02,
        -1.94613917e+02, -2.28804037e+02, -2.64290385e+02,
        -3.01370222e+02, -3.40402692e+02, -3.81829603e+02,
        -4.26204161e+02, -4.74231209e+02, -5.26824445e+02,
        -5.85189090e+02, -6.50943301e+02, -7.26299462e+02,
        -8.14338378e+02, -9.19426505e+02, -1.04784730e+03,
        -1.20873072e+03, -1.41532024e+03, -1.68635591e+03,
        -2.04647512e+03, -2.52245068e+03, -3.12963394e+03,
        -3.84763334e+03, -4.60607863e+03, -5.31133419e+03,
        -5.89779803e+03, -6.35000144e+03, -6.68572727e+03,
        -6.93229744e+03, -7.11416024e+03, -7.24969096e+03,
        -7.35174409e+03, -7.42902896e+03, -7.48731831e+03,
        -7.53028848e+03, -7.56001785e+03, -7.57716179e+03,
        -7.58083262e+03, -7.56775402e+03, -7.53099400e+03,
        -7.45328354e+03, -7.30181662e+03, -6.95868362e+03,
        -6.17517642e+03, -3.61064350e+03,  1.34975856e+03,
         5.29949754e+03,  6.66815767e+03,  7.17203085e+03,
         7.39284278e+03,  7.50019882e+03,  7.55362857e+03,
         7.57693556e+03,  7.58074983e+03,  7.56988919e+03,
         7.54622998e+03,  7.50982417e+03,  7.45928177e+03,
         7.39173988e+03,  7.30251808e+03,  7.18444948e+03,
         7.02684441e+03,  6.81413750e+03,  6.52472118e+03,
         6.13179236e+03,  5.61058038e+03,  4.95724501e+03,
         4.21314155e+03,  3.46425698e+03,  2.79827355e+03,
         2.25982333e+03,  1.84737147e+03,  1.53706826e+03,
         1.30231417e+03,  1.12145413e+03,  9.78779210e+02,
         8.63375788e+02,  7.67741263e+02,  6.86690390e+02,
         6.16592135e+02,  5.54860762e+02,  4.99621144e+02,
         4.49488346e+02,  4.03420995e+02,  3.60622232e+02,
         3.20471669e+02,  2.82477895e+02,  2.46244786e+02,
         2.11447310e+02,  1.77813694e+02,  1.45112690e+02,
         1.13141910e+02,  8.17262839e+01,  5.06886051e+01],
       [ 6.04636447e+00,  6.04570721e+00,  6.04403838e+00,
         6.04135015e+00,  6.03762969e+00,  6.03285883e+00,
         6.02701348e+00,  6.02006294e+00,  6.01196886e+00,
         6.00268392e+00,  5.99215008e+00,  5.98029620e+00,
         5.96703492e+00,  5.95225831e+00,  5.93583206e+00,
         5.91758733e+00,  5.89730932e+00,  5.87472089e+00,
         5.84945891e+00,  5.82103928e+00,  5.78880512e+00,
         5.75184941e+00,  5.70890161e+00,  5.65816958e+00,
         5.59714736e+00,  5.52246551e+00,  5.43000775e+00,
         5.31566250e+00,  5.17680888e+00,  5.01366554e+00,
         4.82920101e+00,  4.62770146e+00,  4.41333641e+00,
         4.18948345e+00,  3.95865321e+00,  3.72265227e+00,
         3.48277809e+00,  3.23997780e+00,  2.99496347e+00,
         2.74829382e+00,  2.50043398e+00,  2.25180419e+00,
         2.00282786e+00,  1.75399280e+00,  1.50595151e+00,
         1.25972034e+00,  1.01714313e+00,  7.82152959e-01,
         5.64839598e-01,  3.95997224e-01,  3.53883016e-01,
         4.73599327e-01,  6.73754843e-01,  9.02171129e-01,
         1.14179578e+00,  1.38657443e+00,  1.63390320e+00,
         1.88245233e+00,  2.13142855e+00,  2.38028099e+00,
         2.62856431e+00,  2.87586312e+00,  3.12173967e+00,
         3.36568694e+00,  3.60707533e+00,  3.84508303e+00,
         4.07859831e+00,  4.30608231e+00,  4.52538803e+00,
         4.73356644e+00,  4.92678894e+00,  5.10068621e+00,
         5.25144305e+00,  5.37740063e+00,  5.47992225e+00,
         5.56261916e+00,  5.62975249e+00,  5.68509378e+00,
         5.73155166e+00,  5.77123456e+00,  5.80563951e+00,
         5.83583042e+00,  5.86257224e+00,  5.88642402e+00,
         5.90780174e+00,  5.92702036e+00,  5.94432234e+00,
         5.95989704e+00,  5.97389432e+00,  5.98643408e+00,
         5.99761306e+00,  6.00750989e+00,  6.01618868e+00,
         6.02370175e+00,  6.03009167e+00,  6.03539278e+00,
         6.03963231e+00,  6.04283129e+00,  6.04500515e+00]])
x_low = np.array([-1.63571344e-03, -1.60286779e-03, -1.57002214e-03, -1.53717649e-03,
       -1.50433084e-03, -1.47148519e-03, -1.43863954e-03, -1.40579388e-03,
       -1.37294823e-03, -1.34010258e-03, -1.30725693e-03, -1.27441128e-03,
       -1.24156563e-03, -1.20871997e-03, -1.17587432e-03, -1.14302867e-03,
       -1.11018302e-03, -1.07733737e-03, -1.04449172e-03, -1.01164607e-03,
       -9.78800414e-04, -9.45954763e-04, -9.13109111e-04, -8.80263460e-04,
       -8.47417808e-04, -8.14572157e-04, -7.81726505e-04, -7.48880854e-04,
       -7.16035202e-04, -6.83189551e-04, -6.50343899e-04, -6.17498248e-04,
       -5.84652596e-04, -5.51806945e-04, -5.18961293e-04, -4.86115642e-04,
       -4.53269991e-04, -4.20424339e-04, -3.87578688e-04, -3.54733036e-04,
       -3.21887385e-04, -2.89041733e-04, -2.56196082e-04, -2.23350430e-04,
       -1.90504779e-04, -1.57659127e-04, -1.24813476e-04, -9.19678242e-05,
       -5.91221727e-05, -2.62765212e-05,  6.56913030e-06,  3.94147818e-05,
        7.22604333e-05,  1.05106085e-04,  1.37951736e-04,  1.70797388e-04,
        2.03643039e-04,  2.36488691e-04,  2.69334342e-04,  3.02179994e-04,
        3.35025645e-04,  3.67871297e-04,  4.00716948e-04,  4.33562600e-04,
        4.66408251e-04,  4.99253903e-04,  5.32099554e-04,  5.64945206e-04,
        5.97790857e-04,  6.30636509e-04,  6.63482160e-04,  6.96327812e-04,
        7.29173463e-04,  7.62019114e-04,  7.94864766e-04,  8.27710417e-04,
        8.60556069e-04,  8.93401720e-04,  9.26247372e-04,  9.59093023e-04,
        9.91938675e-04,  1.02478433e-03,  1.05762998e-03,  1.09047563e-03,
        1.12332128e-03,  1.15616693e-03,  1.18901258e-03,  1.22185824e-03,
        1.25470389e-03,  1.28754954e-03,  1.32039519e-03,  1.35324084e-03,
        1.38608649e-03,  1.41893214e-03,  1.45177780e-03,  1.48462345e-03,
        1.51746910e-03,  1.55031475e-03,  1.58316040e-03,  1.61600605e-03])

f_low = sciint.PPoly(c_low, x_low)



c_high = np.array([[-2.81369106e+07, -2.81369106e+07, -5.61039730e+07,
        -7.77453609e+07, -1.02835726e+08, -1.29424910e+08,
        -1.58810051e+08, -1.91554021e+08, -2.28604335e+08,
        -2.71081381e+08, -3.20466591e+08, -3.78730960e+08,
        -4.48542213e+08, -5.33551518e+08, -6.38824863e+08,
        -7.71501114e+08, -9.41809767e+08, -1.16465331e+09,
        -1.46201983e+09, -1.86639598e+09, -2.42451767e+09,
        -3.19724264e+09, -4.23801614e+09, -5.49300491e+09,
        -6.48444412e+09, -5.75516831e+09, -1.58072319e+09,
         2.05663400e+09, -4.30469838e+09, -1.80764441e+10,
        -2.67134392e+10, -2.48968826e+10, -1.50454755e+10,
        -1.59167430e+09,  1.07754653e+10,  1.83335496e+10,
         2.04171828e+10,  1.89065440e+10,  1.60336245e+10,
         1.32211602e+10,  1.11251532e+10,  1.00272093e+10,
         1.02301592e+10,  1.23113264e+10,  1.82009387e+10,
         3.13842813e+10,  6.80909367e+10,  1.50861462e+11,
         3.95534428e+11,  2.95415173e+11, -4.04715989e+11,
        -3.31704273e+11, -1.25005084e+11, -5.71283763e+10,
        -2.74407992e+10, -1.64665988e+10, -1.16394470e+10,
        -1.00526515e+10, -1.01648894e+10, -1.14944431e+10,
        -1.37702063e+10, -1.66600610e+10, -1.93676434e+10,
        -2.02597665e+10, -1.70115832e+10, -8.10856554e+09,
         4.97431333e+09,  1.78508518e+10,  2.55308364e+10,
         2.39428277e+10,  1.31128504e+10,  1.92949539e+09,
         1.91551886e+08,  4.25983524e+09,  6.50763027e+09,
         6.19529230e+09,  5.00317996e+09,  3.82691928e+09,
         2.90139270e+09,  2.21981695e+09,  1.72464518e+09,
         1.36222075e+09,  1.09281272e+09,  8.88868231e+08,
         7.31583115e+08,  6.08062182e+08,  5.09347686e+08,
         4.29120410e+08,  3.62853079e+08,  3.07254689e+08,
         2.59904272e+08,  2.18995985e+08,  1.83182036e+08,
         1.51359973e+08,  1.22866089e+08,  9.63153735e+07,
         7.36445586e+07,  4.48577061e+07,  4.48577061e+07],
       [-6.34114259e+05, -6.36886785e+05, -6.39659310e+05,
        -6.45187625e+05, -6.52848416e+05, -6.62981535e+05,
        -6.75734672e+05, -6.91383331e+05, -7.10258481e+05,
        -7.32784455e+05, -7.59495989e+05, -7.91073791e+05,
        -8.28392786e+05, -8.72590770e+05, -9.25165312e+05,
        -9.88113168e+05, -1.06413454e+06, -1.15693760e+06,
        -1.27169899e+06, -1.41576198e+06, -1.59967095e+06,
        -1.83857554e+06, -2.15362209e+06, -2.57122329e+06,
        -3.11248727e+06, -3.75144464e+06, -4.31854140e+06,
        -4.47430105e+06, -4.27164660e+06, -4.69581847e+06,
        -6.47701622e+06, -9.10927716e+06, -1.15625401e+07,
        -1.30450755e+07, -1.32019142e+07, -1.21401327e+07,
        -1.03336005e+07, -8.32175353e+06, -6.45876026e+06,
        -4.87885574e+06, -3.57608287e+06, -2.47984416e+06,
        -1.49179350e+06, -4.83744762e+05,  7.29375851e+05,
         2.52284092e+06,  5.61535241e+06,  1.23248259e+07,
         2.71902550e+07,  6.61650129e+07,  9.52743243e+07,
         5.53948433e+07,  2.27097145e+07,  1.03920943e+07,
         4.76283805e+06,  2.05890527e+06,  4.36336772e+05,
        -7.10578891e+05, -1.70113656e+06, -2.70275380e+06,
        -3.83538122e+06, -5.19225541e+06, -6.83388708e+06,
        -8.74231568e+06, -1.07386514e+07, -1.24149210e+07,
        -1.32139143e+07, -1.27237606e+07, -1.09647921e+07,
        -8.44906121e+06, -6.08980788e+06, -4.79770754e+06,
        -4.60758094e+06, -4.58870600e+06, -4.16895481e+06,
        -3.52771274e+06, -2.91724751e+06, -2.42424939e+06,
        -2.04715642e+06, -1.76126202e+06, -1.54252802e+06,
        -1.37258673e+06, -1.23835765e+06, -1.13067521e+06,
        -1.04308884e+06, -9.71000873e+05, -9.11084277e+05,
        -8.60894708e+05, -8.18610489e+05, -7.82856052e+05,
        -7.52580111e+05, -7.26969935e+05, -7.05390738e+05,
        -6.87340538e+05, -6.72425987e+05, -6.60319137e+05,
        -6.50828514e+05, -6.43571803e+05, -6.39151661e+05],
       [-5.60804773e-01, -4.23076621e+01, -8.42366503e+01,
        -1.26438285e+02, -1.69073124e+02, -2.12292416e+02,
        -2.56263422e+02, -3.01167304e+02, -3.47205142e+02,
        -3.94602828e+02, -4.43617751e+02, -4.94547226e+02,
        -5.47739660e+02, -6.03609573e+02, -6.62658043e+02,
        -7.25500921e+02, -7.92908334e+02, -8.65860896e+02,
        -9.45631047e+02, -1.03390245e+03, -1.13294631e+03,
        -1.24587776e+03, -1.37700409e+03, -1.53219472e+03,
        -1.71887989e+03, -1.94433021e+03, -2.20939416e+03,
        -2.49820079e+03, -2.78546714e+03, -3.08000938e+03,
        -3.44698841e+03, -3.95893037e+03, -4.63790968e+03,
        -5.44616284e+03, -6.30826232e+03, -7.14063836e+03,
        -7.87880277e+03, -8.49155003e+03, -8.97702563e+03,
        -9.34941702e+03, -9.62712498e+03, -9.82603585e+03,
        -9.95648688e+03, -1.00213747e+04, -1.00133068e+04,
        -9.90648563e+03, -9.63918137e+03, -9.04992452e+03,
        -7.75202594e+03, -4.68571135e+03,  6.16868852e+02,
         5.56569582e+03,  8.13109091e+03,  9.21834138e+03,
         9.71611501e+03,  9.94017961e+03,  1.00221375e+04,
         1.00131298e+04,  9.93391543e+03,  9.78926679e+03,
         9.57451748e+03,  9.27799888e+03,  8.88299239e+03,
         8.37138186e+03,  7.73151681e+03,  6.97102264e+03,
         6.12922685e+03,  5.27728702e+03,  4.49922107e+03,
         3.86156041e+03,  3.38402178e+03,  3.02641425e+03,
         2.71749142e+03,  2.41543338e+03,  2.12778231e+03,
         1.87498025e+03,  1.66329133e+03,  1.48784639e+03,
         1.34098015e+03,  1.21589016e+03,  1.10737503e+03,
         1.01162618e+03,  9.25868016e+02,  8.48055588e+02,
         7.76656891e+02,  7.10502802e+02,  6.48684489e+02,
         5.90482685e+02,  5.35318243e+02,  4.82717031e+02,
         4.32284630e+02,  3.83687845e+02,  3.36641025e+02,
         2.90895859e+02,  2.46233442e+02,  2.02458560e+02,
         1.59393061e+02,  1.16877639e+02,  7.47457513e+01],
       [ 6.71435682e+00,  6.71365329e+00,  6.71157558e+00,
         6.70811669e+00,  6.70326494e+00,  6.69700366e+00,
         6.68931094e+00,  6.68015917e+00,  6.66951446e+00,
         6.65733592e+00,  6.64357477e+00,  6.62817313e+00,
         6.61106255e+00,  6.59216209e+00,  6.57137585e+00,
         6.54858967e+00,  6.52366677e+00,  6.49644178e+00,
         6.46671260e+00,  6.43422897e+00,  6.39867626e+00,
         6.35965220e+00,  6.31663372e+00,  6.26893154e+00,
         6.21563703e+00,  6.15559166e+00,  6.08747773e+00,
         6.01019373e+00,  5.92338453e+00,  5.82713310e+00,
         5.72026162e+00,  5.59910881e+00,  5.45836551e+00,
         5.29302312e+00,  5.10001044e+00,  4.87895057e+00,
         4.63196408e+00,  4.36275489e+00,  4.07553654e+00,
         3.77428049e+00,  3.46239780e+00,  3.14272482e+00,
         2.81766223e+00,  2.48938804e+00,  2.16014383e+00,
         1.83268208e+00,  1.51113094e+00,  1.20299661e+00,
         9.24388206e-01,  7.13117513e-01,  6.41061589e-01,
         7.49767347e-01,  9.80584275e-01,  1.26772576e+00,
         1.57969521e+00,  1.90299330e+00,  2.23112270e+00,
         2.56036463e+00,  2.88812958e+00,  3.21222007e+00,
         3.53043177e+00,  3.84028734e+00,  4.13883731e+00,
         4.42254604e+00,  4.68736009e+00,  4.92911874e+00,
         5.14440552e+00,  5.33164457e+00,  5.49188619e+00,
         5.62874150e+00,  5.74731023e+00,  5.85235537e+00,
         5.94665235e+00,  6.03094608e+00,  6.10548305e+00,
         6.17110442e+00,  6.22910308e+00,  6.28076502e+00,
         6.32715454e+00,  6.36909417e+00,  6.40720942e+00,
         6.44197885e+00,  6.47377384e+00,  6.50288732e+00,
         6.52955394e+00,  6.55396434e+00,  6.57627527e+00,
         6.59661687e+00,  6.61509810e+00,  6.63181069e+00,
         6.64683215e+00,  6.66022812e+00,  6.67205408e+00,
         6.68235676e+00,  6.69117526e+00,  6.69854188e+00,
         6.70448279e+00,  6.70901864e+00,  6.71216484e+00]])

x_high = np.array([-1.63571344e-03, -1.60286779e-03, -1.57002214e-03, -1.53717649e-03,
       -1.50433084e-03, -1.47148519e-03, -1.43863954e-03, -1.40579388e-03,
       -1.37294823e-03, -1.34010258e-03, -1.30725693e-03, -1.27441128e-03,
       -1.24156563e-03, -1.20871997e-03, -1.17587432e-03, -1.14302867e-03,
       -1.11018302e-03, -1.07733737e-03, -1.04449172e-03, -1.01164607e-03,
       -9.78800414e-04, -9.45954763e-04, -9.13109111e-04, -8.80263460e-04,
       -8.47417808e-04, -8.14572157e-04, -7.81726505e-04, -7.48880854e-04,
       -7.16035202e-04, -6.83189551e-04, -6.50343899e-04, -6.17498248e-04,
       -5.84652596e-04, -5.51806945e-04, -5.18961293e-04, -4.86115642e-04,
       -4.53269991e-04, -4.20424339e-04, -3.87578688e-04, -3.54733036e-04,
       -3.21887385e-04, -2.89041733e-04, -2.56196082e-04, -2.23350430e-04,
       -1.90504779e-04, -1.57659127e-04, -1.24813476e-04, -9.19678242e-05,
       -5.91221727e-05, -2.62765212e-05,  6.56913030e-06,  3.94147818e-05,
        7.22604333e-05,  1.05106085e-04,  1.37951736e-04,  1.70797388e-04,
        2.03643039e-04,  2.36488691e-04,  2.69334342e-04,  3.02179994e-04,
        3.35025645e-04,  3.67871297e-04,  4.00716948e-04,  4.33562600e-04,
        4.66408251e-04,  4.99253903e-04,  5.32099554e-04,  5.64945206e-04,
        5.97790857e-04,  6.30636509e-04,  6.63482160e-04,  6.96327812e-04,
        7.29173463e-04,  7.62019114e-04,  7.94864766e-04,  8.27710417e-04,
        8.60556069e-04,  8.93401720e-04,  9.26247372e-04,  9.59093023e-04,
        9.91938675e-04,  1.02478433e-03,  1.05762998e-03,  1.09047563e-03,
        1.12332128e-03,  1.15616693e-03,  1.18901258e-03,  1.22185824e-03,
        1.25470389e-03,  1.28754954e-03,  1.32039519e-03,  1.35324084e-03,
        1.38608649e-03,  1.41893214e-03,  1.45177780e-03,  1.48462345e-03,
        1.51746910e-03,  1.55031475e-03,  1.58316040e-03,  1.61600605e-03])

f_high = sciint.PPoly(c_high, x_high)


## f_high ( current detuning from sweet spot) = upper qubit frequency
## f_low ( current detuning from sweeet spot) = lower qubit frequency
#%%


import mclient
#reload(mclient)
import numpy as np
from pulseseq import sequencer, pulselib
import matplotlib
#matplotlib.rcParams['backend'] = 'Qt4Agg'
#matplotlib.rcParams['backend.qt4'] = 'PyQt4'
import matplotlib.pyplot as plt
#from t1t2_plotting import smart_T1_delays
from pulseseq import sequencer, pulselib
import os
import time
import math
import datetime
import pandas as pd


from scripts.single_qubit import ssbspec_lorentzianfit
from scripts.single_qubit import contrast_check
from scripts.single_qubit import rabi
from scripts.single_qubit import T1measurement
from scripts.single_qubit import T2measurement
from scripts.single_qubit import ssbspec
from scripts.single_qubit import spectroscopy


qubits = mclient.get_qubits()
qubit_info = mclient.get_qubit_info('qubit1ge')
yoko = mclient.instruments['yoko']
qbrick = mclient.instruments['ZZ']
qubit_info = mclient.get_qubit_info('qubit1ge')
ge = mclient.instruments['qubit1ge']
dig = mclient.instruments['dig']
os.chdir(r'C:/qrlab/scripts')



start_freq = 1096.70e6
start_current = -3.4
stop_current = -0
current_step= 0.2
current_list = np.arange(start_current, stop_current, current_step)

#Npts = 70
#Icenter = -2.0080625
#Istep = 0.0025
#Ispan = 0.1
#current_list = np.linspace(Icenter-Ispan/2, Icenter+Ispan/2, Npts+1)
#ii = np.argsort(np.abs(current_list-Icenter))
#current_list = current_list[ii]

do_erase_data = False
do_start_from_last = True
do_start_from_first = False

do_CW = True
NavgCW = 1000


NavgSSBcoarse = 3000
SSB_Xpoints_coarse = np.linspace(-100e6, 100e6, 201)


do_SSBfine = False
NavgSSBfine = 6000
SSB_Xpoints = np.linspace(-40e6, 40e6, 151)

NavgRabi = 10000
Rabi_Xpoints = np.linspace(-1, 1, 51)/1


NavgT1 = 10000
T1_Xpoints = np.linspace(0,40e3,41)

do_T2 = True
NavgT2 = 10000
T2_Xpoints = np.linspace(0, 3e3,61)

do_T2e1 = True
NavgT2e1 = 10000
T2e1_Xpoints = np.linspace(0, 7e3, 61)


do_T2e21 = False
T2e21_Xpoints = np.linspace(0, 5e3, 81)


detuning = -100e6


if do_start_from_last:
    ii = data.last_valid_index()
    start_freq = data['freq'][ii]
    current = data['current'][ii]
    current_list = current_list[ current_list > current if current_step > 0 else current_list < current ]
    
    

if do_start_from_first:
    ii = 0
    start_freq = data['freq'][ii]
    current = data['current'][ii]
    current_list = current_list[ current_list < current if current_step < 0 else current_list > current ]
    
    pi_amp = data['Rabi_piamp'][ii]
    ge.set('pi_amp', pi_amp)
    ge.set('pi2_amp', pi_amp/2)
    ge.set('pi_amp_selective', pi_amp*qubit1ge.get_w()/qubit1ge.get_w_selective())
    ge.set('pi2_amp_selective', pi_amp/2*qubit1ge.get_w()/qubit1ge.get_w_selective())


if do_erase_data:
    data = pd.DataFrame()

    fig, axes = plt.subplots(nrows=2, ncols=2,
                             gridspec_kw={'height_ratios':[0.3,0.6],
                                          'width_ratios':[0.6,0.3]})
    axes[0,1].set_visible(False)
    axes[0,0].set_ylabel('T')
    axes[1,1].set_xlabel('T')
    
    axes[1,0].set_ylabel('frequency')
    axes[1,0].set_xlabel('current')
    
    fig2, axes2 = plt.subplots(nrows=2, ncols=1, sharex=True)
    axes2[-1].set_xlabel('Current')
    axes2[-1].set_ylabel('T')
    axes2[0].set_ylabel('frequency')


freq = start_freq # LO frequency
for current in current_list:
    temp = {'current': current}
    yoko.do_ramp_current(current)
   # freq=f_low((current+1.98)*1e-3)*1e9
   # freq=freq+detuning
    #freq=qbrick.get_frequency()
    qbrick.set_frequency(freq)

    if do_CW:
    ## Hit qubit with CW around predicted freq
        alz.set_naverages(NavgCW)
        qubit_freq = freq+detuning
        freq_range = 1000e6#e6
        IQ_mod.set_frequency(qubit_freq + freq_range+450e6)
        spec = spectroscopy.Spectroscopy(qbrick, qubit_info,
                                             np.linspace(max(qubit_freq-freq_range, 0),
                                                         qubit_freq+freq_range, 151) + 950e6,
                                                 [5],
                                            plen=8000, amp=0.00000005, seq=None,  postseq=None, plot_seqs=False) #1=1ns for plen
        spec.measure()
        XS = spec.q_freqs
        amp = spec.ampdata[0,:]
        phase = spec.phasedata[0,:]
        
        ys = np.abs(amp*phase)
        
        ii = np.argmax(ys)
        freq = XS[ii]-detuning
        
        
        temp.update({'CW_center': XS[ii]})

        #Need to update freq here
        qbrick.set_frequency(freq)

    
    
    
    
    
    ## Coarse SSB qubit spec 
    alz.set_naverages(NavgSSBcoarse)
    spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, SSB_Xpoints_coarse, seq=None, plot_seqs=False, proj_func='phase')
    spec.measure()
    plt.close(spec.fig)
    XS = spec.xs
    YS = spec.get_ys()
    width = spec.width()
    height = spec.height
    center = spec.center
    
    temp.update({'SSB_width': width, 'SSB_height': height, 'SSB_center': center})
    

    freq += spec.center * 1e6
    temp['freq'] = freq
    temp['qubit_freq'] = freq + detuning
    
    qbrick.set_frequency(freq)
    qubit_info = mclient.get_qubit_info('qubit1ge')
    
    
    if False:
        ## Fine SSB spec
        old_w = qubit1ge.get_w_selective()
        old_piamp = qubit1ge.get_pi_amp_selective()
        
        qubit1ge.set_w_selective(200)
        qubit1ge.set_pi_amp_selective(old_piamp*old_w/200)
        
        alz.set_naverages(NavgSSBfine)
        seq = sequencer.Trigger(600)
        spec = ssbspec_lorentzianfit.SSBSpec_lorentzianfit(qubit_info, SSB_Xpoints, seq=None, plot_seqs=False, proj_func='phase')
        spec.measure()
        plt.close(spec.fig)    
        
    
        qubit1ge.set_w_selective(old_w)
        qubit1ge.set_pi_amp_selective(old_piamp)

        XS = spec.xs
        YS = spec.get_ys()
        width = spec.width()
        height = spec.height
        center = spec.center
        
        temp.update({'SSB_width': width, 'SSB_height': height, 'SSB_center': center})
        
    
        freq += spec.center * 1e6
        temp['freq'] = freq
        
        qbrick.set_frequency(freq)
        qubit_info = mclient.get_qubit_info('qubit1ge')
    
    
    ## Power Rabi
    alz.set_naverages(NavgRabi)
    tr = rabi.Rabi(qubit_info, Rabi_Xpoints, plot_seqs=False, generate=True, selective=False, repeat_pulse=1, seq=None,
                       update=False, proj_func='phase')
    dataR=tr.measure()    
    plt.close(tr.fig)

    ge.set('pi_amp', tr.pi_amp)
    ge.set('pi2_amp', tr.pi_amp/2)
    ge.set('pi_amp_selective', tr.pi_amp*qubit1ge.get_w()/qubit1ge.get_w_selective())
    ge.set('pi2_amp_selective', tr.pi_amp/2*qubit1ge.get_w()/qubit1ge.get_w_selective())

    temp.update({'Rabi_piamp': tr.pi_amp, 'Rabi_contrast': tr.fit_params['amp'].value})
    
    ## T1 measurement
    alz.set_naverages(NavgT1)
    t1 = T1measurement.T1Measurement(qubit_info, #np.linspace(0, 0.8e3, 100),
                                        T1_Xpoints,
                                         double_exp=False, generate=True, plot_seqs=False, proj_func='phase', seq=None)
    t1.measure()
    plt.close(t1.fig)
    
    names = ['tau', 'ofs', 'amplitude']
    temp.update({'T1_' + name: t1.fit_params[name].value for name in names})
    temp.update({'T1_' + name + '_err': t1.fit_params[name].stderr for name in names})


    if do_T2:
        ## T2 Measurement
        alz.set_naverages(NavgT2)
        t2 = T2measurement.T2Measurement(qubit_info, T2_Xpoints, detune=2e6, double_freq=True, 
                                                 generate=True, postseq=None, 
                                                     proj_func='phase', seq=None)
        t2.measure()
        plt.close(t2.fig)          
    
        names = t2.fit_params.keys()
        temp.update({'T2_' + name: t2.fit_params[name].value for name in names})
        temp.update({'T2_' + name + '_err': t2.fit_params[name].stderr for name in names})
    
    if do_T2e1:
        ## T2 Echo measurement
        alz.set_naverages(NavgT2e1)

        t2e = T2measurement.T2Measurement(qubit_info, T2e1_Xpoints, detune=1e6, double_freq=False, echotype = T2measurement.ECHO_HAHN, necho=1, plot_seqs = False, generate=True,
                                         seq=None, postseq=None, proj_func='phase')
        t2e.measure()
        plt.close(t2e.fig)          
    
        names = t2e.fit_params.keys()
        temp.update({'T2e1_' + name: t2e.fit_params[name].value for name in names})
        temp.update({'T2e1_' + name + '_err': t2e.fit_params[name].stderr for name in names})

    if do_T2e21:
        ## T2 multiple echoes measurement
#        t2e = T2measurement.T2Measurement(qubit_info, T2e_Xpoints, detune=0.2e6, double_freq=False, echotype = T2measurement.ECHO_HAHN, necho=11, plot_seqs = False, generate=True,
#                                         seq=None, postseq=None, proj_func='phase')
#        t2e.measure()
#        plt.close(t2e.fig)          
#    
#        names = t2e.fit_params.keys()
#        temp.update({'T2e11_' + name: t2e.fit_params[name].value for name in names})
#        temp.update({'T2e11_' + name + '_err': t2e.fit_params[name].stderr for name in names})
    
     
        t2e = T2measurement.T2Measurement(qubit_info, T2e_Xpoints, detune=1e6, double_freq=False, echotype = T2measurement.ECHO_HAHN, necho=21, plot_seqs = False, generate=True,
                                         seq=None, postseq=None, proj_func='phase')
        t2e.measure()
        plt.close(t2e.fig)          
        names = t2e.fit_params.keys()
        temp.update({'T2e21_' + name: t2e.fit_params[name].value for name in names})
        temp.update({'T2e21_' + name + '_err': t2e.fit_params[name].stderr for name in names})
        


    
    data = data.append(temp, ignore_index=True)


    
    axes[1,0].plot(current, freq, marker='o', fillstyle='none', color='k')
    axes[0,0].errorbar(current, temp['T1_tau'], yerr=temp['T1_tau_err'], 
        marker='o', fillstyle='none', color='k', capsize=2)
    axes[1,1].errorbar(temp['T1_tau'], freq, xerr=temp['T1_tau_err'], 
        marker='o', fillstyle='none', color='k', capsize=2)
    
    xlim = [data['current'].min(), data['current'].max()]
    ylim = [data['freq'].min(), data['freq'].max()]
  #  xlim = [-2.027, -1.999]
  #  ylim = [750e6, 790e6]
    axes[0,0].set_xlim(xlim)
    axes[0,0].set_ylim(bottom=0)
    axes[1,0].set_xlim(xlim)
    axes[1,0].set_ylim(ylim)
    axes[1,1].set_ylim(ylim)
    axes[1,1].set_xlim(left=0)
    
    fig.tight_layout()
    fig.canvas.draw()
    
    
    axes[1,0].plot(current, freq, marker='o', fillstyle='none', color='k')

    if do_T2e21:
        axes2[1].errorbar(current, temp['T2e21_tau'], yerr=temp['T2e21_tau_err'],
             marker='p', fillstyle='none', color='m', capsize=2)
      #  axes2[1].errorbar(current, 2*temp['T2e21_tau'], yerr=temp['T2e21_tau_err'],
      #       marker='p', fillstyle='none', color='m', capsize=2)
    
#        axes2[1].errorbar(current, temp['T2e11_tau'], yerr=temp['T2e11_tau_err'],
#             marker='p', fillstyle='none', color='b', capsize=2)

      #  axes2[1].errorbar(current, 2*temp['T2e11_tau'], yerr=temp['T2e11_tau_err'],
       #      marker='p', fillstyle='none', color='b', capsize=2)
       
    if do_T2e1:
        axes2[1].errorbar(current, temp['T2e1_tau'], yerr=temp['T2e1_tau_err'],
             marker='p', fillstyle='none', color='g', capsize=2)
       # axes2[1].errorbar(current, 2*temp['T2e1_tau'], yerr=temp['T2e1_tau_err'],
       #      marker='p', fillstyle='none', color='g', capsize=2)
        
    axes2[0].plot(current, freq,  marker='o', fillstyle='none', color='k')
    axes2[1].errorbar(current, temp['T1_tau'], yerr=temp['T1_tau_err'],
         marker='o', fillstyle='none', color='k', capsize=2)
    
    if do_T2:
        axes2[1].errorbar(current, temp['T2_tau'], yerr=temp['T2_tau_err'],
             marker='p', fillstyle='none', color='r', capsize=2)
      #  axes2[1].errorbar(current, 2*temp['T2_tau'], yerr=temp['T2_tau_err'],
      #       marker='p', fillstyle='none', color='r', capsize=2)
        
    axes2[0].set_xlim(xlim)
    axes2[0].set_ylim(ylim)
    for ax in axes2[1:]:
        ax.set_ylim(bottom=0)
        ax.set_xlim(xlim)

    fig2.tight_layout()
    fig2.canvas.draw()
   # plt.close('all')


    
    
    
    
    
#%%
   
#if True:
#    loadPath = 'C:/_data/'
#    fnames = ['20210525_coherencevsflux_deviceD_BF.csv', '20210525_coherencevsflux_deviceD_BF_2.csv']
#    for i,fname in enumerate(fnames):
#        if i==0:
#            data = pd.read_csv(loadPath + fname)   
#        else:
#            data = pd.concat([data,pd.read_csv(loadPath + fname)  ])
#    
#
#fig, ax = plt.subplots(nrows=1, ncols=1)
#T1data = data[['current', 'freq', 'T1_tau', 'T1_tau_err']].sort_values('current')
#ax.errorbar(T1data['current'], T1data['T1_tau'], yerr=T1data['T1_tau_err'], 
#            marker='o', fillstyle='none', lw=0.3)
#ax.set_xlabel('Current (mA)')    
#ax.set_ylabel('T1 (ns))')    
#ax.set_ylim([1e-1, 50000])
#
#fig, ax = plt.subplots(nrows=1, ncols=1)
#T2data = data[['current', 'freq', 'T2_tau', 'T2_tau_err']].sort_values('current')
#ax.errorbar(T2data['current'], T2data['T2_tau'], yerr=T2data['T2_tau_err'], 
#            marker='o', fillstyle='none', lw=0.3)
#ax.set_xlabel('Current (mA)')     
#ax.set_ylabel('T2 (ns))')
#ax.set_ylim([1e-1, 50000])
#
#    
#fig, ax = plt.subplots(nrows=1, ncols=1)
#T2e1data = data[['current', 'freq', 'T2e1_tau', 'T2e1_tau_err']].sort_values('current')
#ax.errorbar(T2e1data['current'], T2e1data['T2e1_tau'], yerr=T2e1data['T2e1_tau_err'], 
#            marker='o', fillstyle='none', lw=0.3)
#ax.set_xlabel('Current (mA)')       
#ax.set_ylabel('T2e echo=1 (ns))')    
#ax.set_ylim([1e-1, 50000]) 
#    
#
#fig, ax = plt.subplots(nrows=1, ncols=1)
#T2e11data = data[['current', 'freq', 'T2e11_tau', 'T2e11_tau_err']].sort_values('current')
#ax.errorbar(T2e11data['current'], T2e11data['T2e11_tau'], yerr=T2e11data['T2e11_tau_err'], 
#            marker='o', fillstyle='none', lw=0.3)
#ax.set_xlabel('Current (mA)')    
#ax.set_ylabel('T2e echo=11 (ns))')   
#ax.set_ylim([1e-1, 200000])  
#
#fig, ax = plt.subplots(nrows=1, ncols=1)
#T2e21data = data[['current', 'freq', 'T2e21_tau', 'T2e21_tau_err']].sort_values('current')
#ax.errorbar(T2e21data['current'], T2e21data['T2e21_tau'], yerr=T2e21data['T2e21_tau_err'], 
#            marker='o', fillstyle='none', lw=0.3)
#ax.set_xlabel('Current (mA)')   
#ax.set_ylabel('T2e echo=21 (ns))')   
#ax.set_ylim([1e-1, 50000])   
#    
#    
#        
#    
#Tdata = data[['current', 'freq', 'T1_tau', 'T1_tau_err',
#              'T2_tau', 'T2_tau_err', 'T2e1_tau', 'T2e1_tau_err',
#              'T2e11_tau', 'T2e11_tau_err', 'T2e21_tau', 'T2e21_tau_err']].sort_values('current')
#
#tauKeys = ['T2_tau', 'T2e1_tau', 'T2e11_tau',  'T2e21_tau']
#
#Tdata[tauKeys] = 1/(1/Tdata[tauKeys].values-1/(2*Tdata[['T1_tau']].values))
#fig, ax = plt.subplots(nrows=1, ncols=1)
#
#for tau in tauKeys:
#    ax.plot(Tdata['current'], Tdata[tau], marker='o', fillstyle='none', ls='')
#
#data = data.sort_values(by='current')
#freq, current = data['freq'], data['current']
#
#
   
#%% Polynomial fit of qubit feq
fig, ax = plt.subplots(nrows=1, ncols=1)
current = data['current'].reshape(-1)
freq = data['qubit_freq'].reshape(-1)


ax.plot(current, freq, marker='o', fillstyle='none', ls='')
a,b,c = np.polyfit(current.reshape(-1), freq.reshape(-1), 2)
ax.plot(current, a*current**2+b*current+c, ls='--', color='k', label='Poly2nd order fit')
ax.legend(frameon=False)
res = 'Current at sweet-spot: {} mA\nFreq at sweet spot: {} MHz'.format(-b/(2*a), (c-b**2/(4*a))*1e-6)
res += '\npolyfit ax**2+bx+c: a={}, b={}, c={}'.format(a,b,c)
ax.annotate(res, xy=(0.5, 1), xycoords='axes fraction',
            xytext=(0,-3), textcoords='offset points', ha='center', va='top')
ax.set_xlabel('Current (mA)')
ax.set_ylabel('Qubit Frequency (Hz)')

#%%
#
#
#
#
#
#fig, ax = plt.subplots(nrows=1, ncols=1)
#ax.plot(data['current'], data['Rabi_piamp'], marker='o', fillstyle='none', ls='') 
#ax.set_xlabel('current (mA)')
#ax.set_ylabel('Pi amp')
#    
#
#
#
#fig, ax = plt.subplots(nrows=1, ncols=1)
#ax.plot(data['current'], data['Rabi_contrast'], marker='o', fillstyle='none', ls='') 
#ax.set_xlabel('current (mA)')
#ax.set_ylabel('Rabi contrast')
#    
   
   
   
   
   
   
   
data = pd.DataFrame()
temp.update({'Rabi_piamp': tr.pi_amp, 'Rabi_contrast': tr.fit_params['amp'].value})

names = ['tau', 'ofs', 'amplitude']
temp.update({'T1_' + name: t1.fit_params[name].value for name in names})
temp.update({'T1_' + name + '_err': t1.fit_params[name].stderr for name in names})

temp['current'] = yoko.get_current()
temp['freq'] = qbrick.get_frequency()

data = data.append(temp, ignore_index=True)
