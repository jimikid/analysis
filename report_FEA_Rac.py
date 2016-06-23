"""
Created on 05/16/2016, @author: sbaek
  V00
    - initial release

    V01 : 05/31/2016
     - read data from .csv files from Ansys report with frequencies

"""
import sys, time
from os.path import abspath, dirname

sys.path.append(dirname(dirname(__file__)))
sys.path.append('%s/analysis' % (dirname(dirname(__file__))))

from collections import OrderedDict
from math import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

para, init = OrderedDict(), OrderedDict()
para, init = OrderedDict(), OrderedDict()


def main(filename, it):
    print '\n Start at %s ' % time.strftime("%d/%m/%Y %I:%M")
    save_path = "C:/Users/sbaek/Documents/Ansoft/"
    df = pd.read_csv(save_path + filename + '.csv')

    '''
    e.g.

    len(df)=2

    df.loc[0]
    Freq [kHz]                            200
    GND_237_loss [] - Phase='0deg'        1.189990e-04

    df.loc[1]
    Freq [kHz]                            100
    GND_237_loss [] - Phase='0deg'          1
    '''

    plt.figure(it)
    for i in range(len(df)):  # iteration for frequencies , plots will be overlapped  with different colors
        labels = []
        values = []
        loss_via = 0
        for j in range(1, len(df.loc[i])):  # df.loc[0].index[0]='Freq [kHz]'
            try:
                type(float(
                    df.loc[i].values[j])) == float  # bar plot works with float only.  verify the value is float type
                if 'via' in df.loc[i].index[j]:  # losses in vias are aggregated shown as 'via' on the plot
                    # print df.loc[i].index[j], df.loc[i].values[j]
                    loss_via = loss_via + df.loc[i].values[j]
                else:
                    # print df.loc[i].index[j], df.loc[i].values[j]
                    labels.append(df.loc[i].index[j].split('_loss')[0])
                    values.append(df.loc[i].values[j])
            except:
                pass
        labels.append('via')
        values.append(loss_via)

        objects = labels
        y_pos = np.arange(len(objects))
        performance = values
        plt.barh(y_pos, performance, align='center', alpha=0.5)
        xticks = [i * 0.0005 for i in range(6)]  # xlimit can be set by ticks.
        plt.xticks(xticks)
        plt.yticks(y_pos, objects)
        plt.xlabel('Rac[Ohm]')
        plt.title(filename)
        plt.show()


if __name__ == '__main__':
    filename = "620_00504r03_v02_Q14"
    main(filename, 1)

    filename = "620_00504r03_v01_Q14"
    main(filename, 2)
