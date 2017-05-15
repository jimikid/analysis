
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
import analysis.figure_functions as ff
import analysis.waveform_func as wf
mue = 4.0 * pi * 1E-7 ;

class CWT:
    def __init__(self, fs, ni, no, ri_oc, ro_oc, h_oc, n_oc, mue_ic, ri_ic, ro_ic, h_ic, n_ic, stack=0.8, timestep=1E-7):
        #current, B_oc, B_ic = [], [], []
        self.step = timestep
        self.resolution = 1

        self.fs = fs
        self.T = 1.0 / self.fs;

        # Outer core #
        self.ni, self.no = ni, no;
        self.ri_oc, self.ro_oc = ri_oc, ro_oc

        self.stack=stack;
        self.l_oc = h_oc * n_oc;
        self.Ac_oc = stack*(self.ro_oc - self.ri_oc) * self.l_oc
        self.V_oc = pi * (self.ro_oc ** 2 - self.ri_oc ** 2) * self.l_oc;

        self.mue_ic = mue_ic * 65.4 / 68.3  # based on effective Ac, mue_r287;
        self.ri_ic, self.ro_ic = ri_ic, ro_ic

        self.l_ic = h_ic * n_ic;
        self.Ac_ic = (self.ro_ic - self.ri_ic) * self.l_ic;
        self.V_ic = pi * (self.ro_ic ** 2 - self.ri_ic ** 2) * self.l_ic;

        self.w = 2 * pi * self.fs

        #factor to calculate Bic saveform from current waveform
        self.Fi = (self.mue_ic * self.ni * log(self.ro_ic / self.ri_ic) / (2 * pi * (self.ro_ic - self.ri_ic)))

    def __str__(self):
        ''
        #print '\n Outer cores specs'
        #print ' Di_oc :%.2f, Do_oc : %.2f [mm]' % (self.ri_oc * 2 * 1E3, self.ro_oc * 2 * 1E3)
        #print ' length :%.2f [m], Ac_oc : %.2f [cm^2], V_oc : %.2f [cm^2]' % (self.l_oc, self.Ac_oc * 1E4, self.V_oc * 1E6)

        #print '\n Inner cores specs'
        #print ' Di_ic :%.2f, Do_ic : %.2f [mm]' % (self.ri_ic * 2 * 1E3, self.ro_ic * 2 * 1E3)
        #print ' length :%.2f [m], Ac_ic : %.2f [cm^2], V_ic : %.2f [cm^2] \n' % (self.l_oc, self.Ac_ic * 1E4, self.V_ic * 1E6)


    def i1(self, Vi, t, Ls, d, ps):
        th = 2 * pi * self.fs * t
        y=(Vi*((-1 + d)*pi + 2*(th + d*th - d * ps))) / (2 * Ls *  self.w )
        return y

    def i2(self,Vi, t, Ls, d, ps):
        th = 2 * pi * self.fs * t
        y=(Vi*((-1 + d)*pi + 2*(th - d*th + d * ps))) / (2 * Ls *  self.w )
        return y

    def Bic(self, current_t):
        Bic_t=[i*self.Fi for i in current_t]
        self.Bic_t=Bic_t
        return Bic_t

    def Boc(self, t_ps, Vop):
        ''' Boc '''
        Boc_t=[]
        t1 = [i * self.step for i in range(0, int(t_ps / self.step), self.resolution)]
        for i in t1:
            Boc_t.append(-Vop/self.ni*((i+self.T/2)-t_ps-self.T/4)/self.Ac_oc/self.no)

        t2 = [i * self.step for i in range(int(t_ps / self.step), int((t_ps + self.T / 2) / self.step), self.resolution)]
        for i in t2:
            Boc_t.append(Vop / self.ni * ((i) - t_ps - self.T / 4) / self.Ac_oc / self.no)
        t3 = [i * self.step for i in range(int((t_ps + self.T / 2) / self.step), int(self.T / self.step), self.resolution)]
        for i in t3:
            Boc_t.append(-Vop / self.ni * ((i - self.T / 2) - t_ps - self.T / 4) / self.Ac_oc / self.no)

        self.Boc_t=Boc_t
        return Boc_t

    def Bic_pk(self, Vi, Ls, d, ps):
        if d>1:
            t_ps=ps/2/pi*self.T;
            y= self.Fi*self.i1(Vi=Vi, t=t_ps, Ls=Ls, d=d, ps=ps)
        else:
            y = self.Fi*self.i2(Vi=Vi, t=self.T/2, Ls=Ls, d=d, ps=ps)
        return y

    def Boc_pk(self, Vop, Ac_oc):
        y = Vop/self.ni * self.T / 2.0 / 2.0/ Ac_oc
        return y

    def L(self, mue, n, ri, ro, l):
        y=n**2*mue/2/pi*log(ro/ri)*l
        return y

    def Loss_oc(self, k_oc, Bpk, beta_oc):
        y=k_oc*1E6*Bpk**beta_oc*self.V_oc
        return y

    def Loss_ic(self, k_ic, Bpk, alpha_ic, beta_ic, ps):
        if ps==0:
            y=0
        else:
            fs2=self.fs * pi / ps;
            y= k_ic *1E6 * (Bpk) ** beta_ic * (fs2) ** (alpha_ic - 1) * self.fs * self.V_ic
        return y
