
"""
@author: sbaek
  V00 10/07/2016
    - initial release
    - ProjectName,, DesignName, file_path are necessary.
    - new(), open(), or activate(), at least one of them is required to start.

"""
import win32com.client
import os, sys, csv, time
from os.path import abspath, dirname, exists
import pandas as pd
import figure_functions as ff
import matplotlib.pyplot as plt
from collections import OrderedDict
from Ansys_Eddy import Ansys_Eddy

oAnsoftApp = win32com.client.Dispatch("Ansoft.ElectronicsDesktop")
oDesktop = oAnsoftApp.GetAppDesktop()

class PCB(Ansys_Eddy):
    '''
    subclass inherited from Ansys_Eddy
    '''
    def __init__(self, ProjectName='P1', DesignName='D1', file_path='C:/Users/sbaek/Documents/Ansoft/'):
        '''
        - default file_path has to be set for a existing folder
        :param ProjectName:
        :param DesignName:
        :param file_path:
        '''

        Ansys_Eddy.__init__(self, ProjectName, DesignName, file_path)
        self.z_crd=[]  #record z of each layer

    #the thickness of copper can be added or fixed by [oz] or [mm].
    def put_oz(self, oz=1):
        self.thick= oz*35*10**-6  #1oz copper 35um thick [m]
        return self.thick

    def put_mm(self, mm=35 * 10 ** -3):
        self.thick= mm
        return self.thick

    def put_height(self, mm=35 * 10 ** -3):
        '''
        - self.height can be manually set.
        '''
        self.height= mm
        return self.height

    def stack_pcb(self, dimension=(50e-3, 50e-3), name= 'layer', origin=(0,0,0), thick=35e-6, material= "copper"):
        '''
        :param dimension: (x,y) dimension in m
        :param name:  str
        :param origin: the center of the dimension
        :material

        - default thickness is 1oz, 35um, thickness can be added with 'thick' valuable or 'putOz()'

        '''
        if not self.thick:
            self.thick = thick  # in case thickness hasn't been set.
            prt = '\n copper thickness is set: %s mm ' % (self.thick * 1000)
            self.spec += prt
            print prt
        else:pass

        self.set_coort_z(name=name + '_cood', z=origin[2])

        oEditor = self.oD.SetActiveEditor("3D Modeler")
        oEditor.CreateBox(
            [
                "NAME:BoxParameters",
                "XPosition:="	, str(origin[0]*1000)+"mm",
                "YPosition:="		, str(origin[1]*1000)+"mm",
                #"ZPosition:="		, str(origin[2])+"m",
                "ZPosition:="	, "0mm",#0 from the relative coordinate
                "XSize:="		, str(dimension[0]*1000)+"mm",
                "YSize:="		, str(dimension[1]*1000)+"mm",
                "ZSize:="		, str(self.thick*1000)+"mm",

            ],
            [
                "NAME:Attributes",
                "Name:="		, name,
                "Flags:="		, "",
                "Color:="		, "(255 128 0)",
                "Transparency:="	, 0.8,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\""+material+"\"",
                "SolveInside:="		, True
            ])
        self.act_coort()  #back to global coordinate



    def layer_pcb(self, stacks, dimension=(50e-3, 50e-3),  origin=(0, 0, 0)):
        '''
         - calculate and set self.height (total thickness of the pcb).
        :param stacks: [(thickness in oz, 'material'),..] from the bottom layer
        :param dimension:
        :param origin:
        :return:
        '''
        z_origin=0
        layer=1
        die=1
        for i in range(len(stacks)):
            material= stacks[i][1]
            thick=stacks[i][0]
            self.put_oz(thick)
            origin=(-dimension[0] / 2, -dimension[1] / 2, z_origin)

            print '\n material : %s' % material
            print ' origin : %s, %s, %s' %origin
            print ' dimension : %s, %s' %dimension
            print ' thickness : %s [um] ' %(self.thick*1e6)

            if material=='copper':
                name='layer_' + str(layer)
                print ' %s\n' %name
                self.stack_pcb(name=name, dimension=dimension,
                              origin=origin,
                              material= material)  # thickness has been set by 'putOz()'
                layer +=1
                self.z_crd.append(z_origin)
                z_origin = z_origin + self.thick

            else:
                name='die_' + str(die)
                print ' %s\n' %name
                self.stack_pcb(name=name, dimension=dimension,
                              origin=origin,
                              material= material)  # thickness has been set by 'putOz()'
                die +=1
                z_origin = z_origin + self.thick
            self.height=z_origin


    def crt_via(self, name='via', loc=(0, 0), dia=0.5e-3, thick=35e-6):
        '''
        - self.height has to be set in advance
        :param loc:
        :param dia:
        :param thick:
        :return:
        '''
        self.act_coort()
        oEditor = self.oD.SetActiveEditor("3D Modeler")
        oEditor.CreateCylinder(
            [
                "NAME:CylinderParameters",
                "XCenter:="	, str(loc[0]*1000)+"mm",
                "YCenter:="		, str(loc[1]*1000)+"mm",
                "ZCenter:="		, "0mm",
                "Radius:="		, str(dia/2.0*1000)+"mm",
                "Height:="		, str(self.height*1000)+"mm",
                "WhichAxis:="		, "Z",
                "NumSides:="		, "0"
            ],
            [
                "NAME:Attributes",
                "Name:="		, name,
                "Flags:="		, "",
                "Color:="		, "(143 175 143)",
                "Transparency:="	, 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\"copper\"",
                "SolveInside:="		, True
            ])

        list_str=''
        names=self.get_objts('copper')
        names += self.get_objts('FR4_epoxy')
        for i in range(len(names)):
            if str(names[i]) != name:  #omit the tool part from the list
                if i==len(names)-1:list_str += str(names[i]) #omit period at the end
                else:list_str += str(names[i]+',')

        oEditor.Subtract(
            [
                "NAME:Selections",
                "Blank Parts:="		, list_str,
                "Tool Parts:="		, name
            ],
            [
                "NAME:SubtractParameters",
                "KeepOriginals:="	, True
            ])

        oEditor.CreateCylinder(
            [
                "NAME:CylinderParameters",
                "XCenter:=", str(loc[0] * 1000) + "mm",
                "YCenter:="	, str(loc[1 ] *1000 ) +"mm",
                "ZCenter:="		, "0mm",
                "Radius:="		, str( (dia / 2.0-thick) *1000  ) +"mm",
                "Height:="		, str(self. height *1000 ) +"mm",
                "WhichAxis:="		, "Z",
                "NumSides:="		, "0"
            ],
            [
                "NAME:Attributes",
                "Name:="		, name+"_p",
                "Flags:="		, "",
                "Color:="		, "(143 175 143)",
                "Transparency:="	, 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\"copper\"",
                "SolveInside:="		, True
            ])

        oEditor.Subtract(
            [
                "NAME:Selections",
                "Blank Parts:="		, name,
                "Tool Parts:="		, name+"_p"
            ],
            [
                "NAME:SubtractParameters",
                "KeepOriginals:="	, False
            ])


    def crt_vias(self, name='via_array', loc=((0, 0), (3e-3, 3e-3)), num=2, dia=0.5e-3, thick=35e-6):
        '''
        :param name:
        :param loc: ((x1,y1),(x2,y2))
        :param num: the number of vias
        :param dia:
        :param thick:
        :return:
        '''
        x1=loc[0][0]
        y1=loc[0][1]
        x2=loc[1][0]
        y2=loc[1][1]

        for i in range(num):
            self.crt_via(name=name + '_%s' % (i + 1), loc=(x1 + (x2 - x1) / (num - 1) * i, y1 + (y2 - y1) / (num - 1) * i), dia=dia, thick=thick)
