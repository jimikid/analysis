
"""
Created on 08/28/2016, @author: sbaek
    - initial release
"""

import sys, time, os
from os.path import abspath, dirname
sys.path.append(dirname(dirname(__file__)))
from collections import OrderedDict

from math import *
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
#import data_aq_lib.analysis.figure_functions as ff
import analysis.figure_functions as ff
#import data_aq_lib.analysis.waveform_func as wf
import analysis.waveform_func as wf
mue = 4.0 * pi * 1E-7 ;

class DAB:
    def __init__(self, fs, ni, no, ri_oc, ro_oc, h_oc, n_oc, mue_ic, ri_ic, ro_ic, h_ic, n_ic):
        current, B_oc, B_ic = [], [], []
        step = 1E-7
        resolution = 1

        self.fs = fs
        self.T = 1.0 / self.fs;

        # Outer core #
        self.ni, self.no = ni, no;
        self.ri_oc = ri_oc
        self.ro_oc = ro_oc

        stack=0.8;

        self.l_oc = h_oc * n_oc;
        self.Ac_oc = stack*(self.ro_oc - self.ri_oc) * self.l_oc
        self.V_oc = pi * (self.ro_oc ** 2 - self.ri_oc ** 2) * self.l_oc;

        self.mue_ic = mue * mue_ic*65.4/68.3 #based on effective Ac, mue_r287;
        self.ri_ic = ri_ic
        self.ro_ic = ro_ic

        self.l_ic = h_ic * n_ic;
        self.Ac_ic = (self.ro_ic - self.ri_ic) * self.l_ic;
        self.V_ic = pi * (self.ro_ic ** 2 - self.ri_ic ** 2) * self.l_ic;

        self.k_oc = 0.3571;
        self.beta_oc = 2.0694;

        self.k_ic = 1.2681* 1E-5;
        self.beta_ic = 2.106;
        self.alpha_ic = 1.309;

        self.w = 2 * pi * self.fs

        self.Fi = (self.mue_ic * self.ni * log(self.ro_ic / self.ri_ic) / (2 * pi * (self.ro_ic - self.ri_ic)))

    def __str__(self):
        print '\n Outer cores specs'
        print ' Di_oc :%.2f, Do_oc : %.2f [mm]' % (self.ri_oc * 2 * 1E3, self.ro_oc * 2 * 1E3)
        print ' length :%.2f [m], Ac_oc : %.2f [cm^2], V_oc : %.2f [cm^2]' % (self.l_oc, self.Ac_oc * 1E4, self.V_oc * 1E6)
        print '\n Inner cores specs'
        print ' Di_ic :%.2f, Do_ic : %.2f [mm]' % (self.ri_ic * 2 * 1E3, self.ro_ic * 2 * 1E3)
        print ' length :%.2f [m], Ac_ic : %.2f [cm^2], V_ic : %.2f [cm^2] \n' % (self.l_oc, self.Ac_ic * 1E4, self.V_ic * 1E6)


    def i1(self, Vi, t, Ls, d, ps):
        th = 2 * pi * self.fs * t
        y=(Vi*((-1 + d)*pi + 2*(th + d*th - d * ps))) / (2 * Ls *  self.w )
        return y

    def i2(self,Vi, t, Ls, d, ps):
        th = 2 * pi * self.fs * t
        y=(Vi*((-1 + d)*pi + 2*(th - d*th + d * ps))) / (2 * Ls *  self.w )
        return y

    def Bi1(self,Vi, t, F, Ls, d, ps ):
        y=F*self.i1(Vi, t, Ls, d, ps)
        return y

    def Bi2(self,Vi, t, F, Ls, d, ps):
        y=F*self.i2(Vi, t, Ls, d, ps)
        return y

    def Irms(self,Vi, Ls, d, ps):
        a=Vi*sqrt((d-1)**2*pi**3+12.0*d*pi*ps**2-8*d*ps**3)
        b=2*self.w*Ls*sqrt(3*pi)
        y=a/b
        return y


    def Boc(self, Vop, t, t_ps, Ac_oc):
        y=Vop/self.ni*(t-t_ps-self.T/4)/self.Ac_oc/self.no
        return y

    def Bic_pk(self, Vi, Ls, F, d, ps):
        if d>1:
            #y = (Vi / 2 * mue * ni * ((-1 + d) * pi + 2 * ps)) / (4 * w * Ls * pi * ri_ic)
            t_ps=ps/2/pi*self.T;
            y= F*self.i1(Vi=Vi, t=t_ps, Ls=Ls, d=d, ps=ps)
        else:
            #y = (Vi/ 2 * mue * ni * ((1 - d) * pi + 2 * d * ps)) / (4 * w * Ls * pi * ri_ic)
            y = F*self.i2(Vi=Vi, t=self.T/2, Ls=Ls, d=d, ps=ps)

        return y

    def Boc_pk(self, Vop, Ac_oc):
        y = Vop/self.ni * self.T / 2.0 / 2.0/ Ac_oc
        return y

    def L(self, mue, n, ri, ro, l):
        y=n**2*mue/2/pi*log(ro/ri)*l
        return y

    def P(self, d, Vi, ps, Ls, fs):
        w = 2 * pi * fs
        y=(d*Vi**2*(pi -ps)*ps)/(self.w*Ls*pi)
        return y

    def Loss_oc(self, k_oc, B, beta_oc, V_oc):
        y=k_oc*1E6*B**beta_oc*V_oc
        return y

    def Loss_ic(self, k_ic, Bi, alpha_ic, beta_ic, V_ic, fs, ps):
        fs2=fs * pi / ps;
        y= k_ic *1E6 * (Bi) ** beta_ic * (fs2) ** (alpha_ic - 1) * fs * V_ic
        return y

    def bound_low(self, Vi, ps, Ls):
        Pb=Vi**2/(Ls*self.w)
        y=Pb*(pi-ps)*ps/(pi-2*ps)
        return y

    def bound_high(self, Vi, ps, Ls):
        Pb=Vi**2/(Ls*self.w)
        y=Pb*((pi-2* ps)*(pi-ps)*ps)/(pi**2)
        return y


    def read(self, filepath, filename):
        file = filepath + filename + '.csv'
        print ' read file %s' % file
        df = pd.read_csv(file)
        #df = convert_1st_key_t(df)  # change the first key(column) to 't' which is compatible with waveform_func.py

        waves = wf.waveforms(filename=filename, filepath=filepath, df=df)
        waves.get_rms()
        waves.get_avg()
        waves.get_pkpk()
        zeros = waves.get_zero_crossing(waves.get_labels()[0])
        freq = waves.get_freq(waves.get_labels()[0], zeros)
        print ' %.1f kHz' % (freq / 1000)

        print waves
        waves.plot_all()



