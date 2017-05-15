
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

class DAB:
    """
    - converter models - DAB
    - run function current() which builds current waveforms and Irms 
    """

    def __init__(self, fs, Vi, Ls, d, ps, timestep=1E-7):
        """        
        :param fs: float, siwtcing frequency 
        :param Vi: float, input voltage
        :param Ls: float, filter inductance in henry
        :param d: float, conversion ratio
        :param ps: float, phase shift in radian
        :para timestep: float
        """
        self.step = timestep
        self.resolution = 1

        self.fs, self.Vi = fs, Vi
        self.Ls, self.d, self.ps = Ls, d, ps
        self.t_ps=self.ps/(2 * pi * self.fs)
        self.deg=self.ps/(2 * pi)*360.0

        self.T = 1.0 / self.fs;
        self.w = 2 * pi * self.fs

        #run functions to set self.current and self Po during initiation.
        self.current()
        self.Po()

    def __str__(self):
        ''
        #print ' Converter type : Dual active bridge \n'
        #print ' fs: %.1f [kHz], Vi: %.0f, Ls: %.3f [mH]' % (self.fs / 1000, self.Vi, self.Ls*1000)
        #print ' Ls: %.3f [mH], phase shift: %.1f [deg]' % (self.Ls * 1000, self.ps/2/pi*360)

    def i1(self, t):
        th = 2 * pi * self.fs * t
        y = (self.Vi * ((-1 + self.d) * pi + 2 * (th + self.d * th - self.d * self.ps))) / (2 * self.Ls * self.w)
        return y

    def i2(self, t):
        th = 2 * pi * self.fs * t
        y = (self.Vi * ((-1 + self.d) * pi + 2 * (th - self.d * th + self.d * self.ps))) / (2 * self.Ls * self.w)
        return y


    def current(self):
        ''' 
        - build lists of the current saveform with time for a period
        - set self.r, self.current, self.Irms
        - return time and current 
        '''
        current_t=[]
        t1 = [i * self.step for i in range(0, int(self.t_ps / self.step), self.resolution)]
        for i in t1:
            current_t.append(self.i1(t=i))

        t2 = [i * self.step for i in range(int(self.t_ps / self.step), int(self.T / self.step / 2), self.resolution)]
        for i in t2:
            current_t.append(self.i2(t=i))

        t3 = [i * self.step for i in range(int(self.T / self.step / 2), int(self.T / self.step / 2) + int(self.t_ps / self.step), self.resolution)]
        for i in t3:
            current_t.append(-self.i1(t=i - self.T / 2))
        t4 = [i * self.step for i in range(int(self.T / self.step / 2) + int(self.t_ps / self.step), int(self.T / self.step), self.resolution)]
        for i in t4:
            current_t.append(-self.i2(t=i - self.T / 2))

        self.t, self.current = t1+t2+t3+t4, current_t

        a=[(i) ** 2 for i in self.current]
        self.Irms = sqrt(sum(a) / len(a))
        return self.t, self.current


    def dab_Irms(self,Vi, Ls, d, ps):
        ''' calculate Irms'''
        a=Vi*sqrt((d-1)**2*pi**3+12.0*d*pi*ps**2-8*d*ps**3)
        b=2*self.w*Ls*sqrt(3*pi)
        y=a/b
        return y

    def Po(self):
        # calculate Po
        Po=(self.d*self.Vi**2*(pi -self.ps)*self.ps)/(self.w*self.Ls*pi)
        self.Po=Po
        return Po

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
        waves = wf.waveforms(filename=filename, filepath=filepath, df=df)
        waves.get_rms()
        waves.get_avg()
        waves.get_pkpk()
        zeros = waves.get_zero_crossing(waves.get_labels()[0])
        freq = waves.get_freq(waves.get_labels()[0], zeros)
        print ' %.1f kHz' % (freq / 1000)

        print waves
        waves.plot_all()
