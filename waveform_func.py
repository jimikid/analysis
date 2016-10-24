
"""
@author: sbaek
  V00 06/01/2016
    - initial release
    - scripted for waveforms of .csv file
    - df should have a key 't' at the first column which means time
"""

import os
from os.path import abspath, dirname, exists
import csv, time
import pandas as pd
from scipy import integrate
import figure_functions as ff
import matplotlib.pyplot as plt

class waveforms:
    """
           __INIT__     
           __STR__      
           
    inputs
            dataset_path=''             - type:str with '\' at the end
            filename=''                 - type:str
            filepath=''                 - type:str
    """    
    
    def __init__(self, df, filename='waveforms', filepath=''):
        print '\n Start at %s ' % time.strftime("%d/%m/%Y %I:%M")

        self.filepath = filepath
        self.filename=filename
        self.df=df
        self.timestep= self.df['t'][len(self.df['t']) - 9] -self.df['t'][len(self.df['t']) - 10]
        self.return_str=str()
        self.sets = []
        self.labels = []
        self.rms=dict()

    def __str__(self):
        self.return_str += '\n filename : %s  ' %self.filename
        self.return_str += '\n filepath : %s  ' % self.filepath
        return self.return_str


    def plot_all(self):
        # build datasets and labels
        print '\n plot'
        for i in self.df.keys():
            if not (i == 't'):
                #print ' build a set of %s with time ' % i
                self.sets.append((self.df['t'], self.df[i]))  # [(df['t'], df['i_pri']*1),(df['t'], df['i_sec']*1)]
                self.labels.append(('time', i))
        ff.plot(
            data=self.sets, label=self.labels,
            # limit=[((0,90),(0,50)), ((0,90),(0,400))],
            title=self.filename,
            fig_num=1
        )

    def get_labels(self):
        l=[]  #
        for i in self.df.keys():
            if not (i == 't'):
                l.append(i)
        return l


    def get_rms(self):
        data=[]
        for i in self.df.keys():
            if not (i == 't'):
                temp1 = [float(self.df[i][j]) ** 2 for j in range(len(self.df[i]))]
                temp2 = (integrate.cumtrapz(temp1, self.df['t'], initial=0))
                a, b = self.df['t'][len(self.df['t']) - 1], self.df['t'][0]
                c, d = temp2[len(temp2) - 1], temp2[0]
                rms = ((c - d) / (a - b)) ** 0.5
                #print ' RMS %s : %.2e '%(i, rms)
                print ' RMS %s : %.2f '%(i, rms)
                data.append(rms)
        print '\n'
        return data

    def get_avg(self):
        # use sum(), len() for avg calculatio with daraframes
        data=[]
        for i in self.df.keys():
            if not (i == 't'):
                avg = sum(self.df[i])/len(self.df[i])
                #print ' AVG %s : %.2e '%(i, avg)
                print ' AVG %s : %.2f '%(i, avg)
                data.append(avg)
        print '\n'
        return data

    def get_pkpk(self):
        # use sum(), len() for avg calculatio with daraframes
        data=[]
        for i in self.df.keys():
            if not (i == 't'):
                pkpk = max(self.df[i])-min(self.df[i])
                print ' pk-pk %s : %.2e '%(i, pkpk)
                data.append(pkpk)
        print '\n'
        return data

    def get_freq(self, zeros):
        # zeros is required for calculation
        # give freq based on the start and end points if zeros are less than 3
        try:
            freq = 1/(zeros[3][1] - zeros[1][1])  #pass zeros twice for one cycle
        except: freq=0
        return freq

    def get_zero_crossing(self, key):
        # key of the data set in dataframe format is required
        # calculate timestep somewhere in the middle
        # zeros : [(index, time, value), (index, time, value), ..]  06/22/2016
        print ' find zeros with %s' %key
        skip_pts = 10  #in case of noise

        zeros = []
        for i in range(10,len(self.df[key]) - 10): # start from value at index 1 for comparison
            # This method returns -1 if x < y, returns 0 if x == y and 1 if x > y
            if cmp(self.df[key][i], -1e-6) + cmp(self.df[key][i - 2], 1e-6) == 0 or self.df[key][i] == 0: #cmp(self.df[key][i], 0) + cmp(self.df[key][i - 1], 0) == 0 -> polarity change
            #if self.df[key][i] == 0:
                zeros.append((i, i * self.timestep, self.df[key][i]))
                i + skip_pts
            else:pass
        return zeros
