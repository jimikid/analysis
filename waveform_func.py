
"""
@author: sbaek
    V00 06/01/2016
    - initial release
    - scripted for waveforms of .csv file
    - df should have a key 't' at the first column which means time

    V01 10/25/2016
    - overall changes
"""

import os
from os.path import abspath, dirname, exists
import csv, time
import pandas as pd
from scipy import integrate
import figure_functions as ff
import matplotlib.pyplot as plt
from collections import OrderedDict

class waveforms:
    def __init__(self, df, filename='waveforms', filepath=''):
        print '\n Start at %s ' % time.strftime("%d/%m/%Y %I:%M")

        self.filepath = filepath
        self.filename=filename
        self.df=df
        self.timestep= self.df['t'][len(self.df['t']) - 9] -self.df['t'][len(self.df['t']) - 10]
        self.return_str=str()
        self.sets = []
        self.labels = []
        self.rms=OrderedDict()

    def __str__(self):
        self.return_str += '\n filename : %s  ' %self.filename
        self.return_str += '\n filepath : %s  ' % self.filepath
        return self.return_str


    def plot_all(self, marker='-'):
        # build datasets and labels
        print '\n plot'
        for i in self.df.keys():
            if (i != 't') and not ('Unnamed' in i):
                #print ' build a set of %s with time ' % i
                self.sets.append((self.df['t'], self.df[i]))  # [(df['t'], df['i_pri']*1),(df['t'], df['i_sec']*1)]
                self.labels.append(('time', i))
        ff.plot(
            data=self.sets, label=self.labels,
            # limit=[((0,90),(0,50)), ((0,90),(0,400))],
            title=self.filename, marker=marker,
            fig_num=1
        )

    def get_labels(self):
        l=[]  #
        for i in self.df.keys():
            if (i != 't') and not ('Unnamed' in i):
                l.append(i)
        return l

    def get_rms(self, df=pd.DataFrame(), show=True):
        if not df.empty:
            df2=df
        else:df2=self.df

        data_dict = OrderedDict()
        for key in df2.keys():
            if (key != 't') and not ('Unnamed' in key):
                temp1 = [float(df2[key][j]) ** 2 for j in range(len(df2[key]))]
                temp2 = (integrate.cumtrapz(temp1, df2['t'], initial=0))
                a, b = df2['t'][len(df2['t']) - 1], df2['t'][0]
                c, d = temp2[len(temp2) - 1], temp2[0]
                rms = ((c - d) / (a - b)) ** 0.5
                if show:
                    # print ' RMS %s : %.2e '%(i, rms)
                    print ' RMS %s : %.2f ' % (key, rms)
                data_dict.update({key: rms})
        #print '\n'
        return data_dict


    def get_avg(self, df=pd.DataFrame(), show=True):
        if not df.empty:
            df2=df
        else:df2=self.df
        # use sum(), len() for avg calculatio with daraframes

        data_dict = OrderedDict()
        for key in df2.keys():
            if (key != 't') and not ('Unnamed' in key):
                avg = sum(df2[key])/len(df2[key])
                if show:
                    #print ' AVG %s : %.2e '%(i, avg)
                    print ' AVG %s : %.2f '%(key, avg)
                data_dict.update({key: avg})
        #print '\n'
        return data_dict


    def get_pkpk(self, df=pd.DataFrame(), show=True):
        if not df.empty:
            df2=df
        else:df2=self.df
        # use sum(), len() for avg calculatio with daraframes

        data_dict = OrderedDict()
        for key in df2.keys():
            if (key != 't') and not ('Unnamed' in key):
                pkpk = max(df2[key])-min(df2[key])
                if show:
                    #print ' pk-pk %s : %.2e '%(key, pkpk)
                    print ' pk-pk %s : %.2f ' % (key, pkpk)
                data_dict.update({key: pkpk})
        #print '\n'
        return data_dict

    def get_freq(self, key=None):
        if key:
            zeros = self.get_zero_crossing(key=key)
        else:
            zeros = self.get_zero_crossing(key=self.get_labels()[3])  # if there is no zeroes in, used channel 4 to get zeros

        try:
            freq = 1/(zeros[2][1] - zeros[0][1])  #pass zeros twice for one cycle
        except:
            freq = 1 / (zeros[1][1] - zeros[0][1])/2 # in case the number of zeroes detected is not enough

        return freq

    def get_zero_crossing_waveforms(self, key=None, cycle=1, replace=True):
        if key:
            zeros = self.get_zero_crossing(key=key)
        else:
            zeros = self.get_zero_crossing(key=self.get_labels()[3])  # if there is no zeroes in, used channel 4 to get zeros

        length=int(zeros[cycle*2][0] - zeros[0][0])
        data=OrderedDict({'t': [i * self.timestep for i in range(length)]})
        for i in self.df.keys():
            if (i != 't') and not ('Unnamed' in i):
                data.update({i: self.df[i][zeros[0][0]:zeros[cycle*2][0]]})

        df2=pd.DataFrame(data)
        df2=df2.set_index([range(len(df2))])
        self.df=df2
        return df2


    def get_zero_rise_crossing_waveforms(self, key=None, cycle=1, replace=True):
        if key:
            zeros = self.get_zero_rise_crossing(key=key)
        else:
            zeros = self.get_zero_crossing(key=self.get_labels()[3])  # if there is no zeroes in, used channel 4 to get zeros

        length=int(zeros[cycle][0] - zeros[0][0])
        data=OrderedDict({'t': [i * self.timestep for i in range(length)]})
        for i in self.df.keys():
            if (i != 't') and not ('Unnamed' in i):
                data.update({i: self.df[i][zeros[0][0]:zeros[cycle][0]]}) # the number of zeros are a half of get_zero_crossing()

        df2=pd.DataFrame(data)
        df2=df2.set_index([range(len(df2))])
        self.df=df2
        return df2

    def get_zero_crossing(self, key):
        # key of the data set in dataframe format is required
        # zeros : [(index, time, value), (index, time, value), ..]  06/22/2016
        print ' find zeros with %s' %key
        skip_pts = 10  #in case of noise
        zeros, j = [], 10
        while(j < len(self.df[key])):
            # This method returns -1 if x < y, returns 0 if x == y and 1 if x > y
            if cmp(self.df[key][j], 0) + cmp(self.df[key][j - 2], 0) == 0 or self.df[key][j] == 0:  # cmp(self.df[key][i], 0) + cmp(self.df[key][i - 1], 0) == 0 -> polarity change
                zeros.append((j, self.df['t'][j], self.df[key][j]))
                j += skip_pts
            else: j+=1
        return zeros


    def get_zero_rise_crossing(self, key):
        # key of the data set in dataframe format is required
        # zeros : [(index, time, value), (index, time, value), ..]  06/22/2016
        print ' find zeros with %s' % key
        skip_pts = 10  # in case of noise
        zeros, j = [], 5
        while (j < len(self.df[key])-5):
            if (self.df[key][j+4] > self.df[key][j - 4]) and (abs(self.df[key][j]) < 0.1):  # cmp(self.df[key][i], 0) + cmp(self.df[key][i - 1], 0) == 0 -> polarity change
                zeros.append((j, self.df['t'][j], self.df[key][j]))
                j += skip_pts
            else:
                j += 1
        return zeros
