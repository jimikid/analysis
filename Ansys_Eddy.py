
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

oAnsoftApp = win32com.client.Dispatch("Ansoft.ElectronicsDesktop")
oDesktop = oAnsoftApp.GetAppDesktop()

class Ansys_Eddy:
    """
           __INIT__     
           __STR__      
           
    inputs
    """

    def __init__(self, ProjectName='ProjectName', DesignName='DesignName', file_path=None):
        print '\n Start at %s ' % time.strftime("%d/%m/%Y %I:%M")

        self.p_name = ProjectName
        self.d_name=DesignName
        self.file_path=file_path

        self.spec = "\n ProjectName : %s " % (self.p_name)
        self.spec += '\n DesignName : %s ' % self.d_name
        self.spec += '\n file_path : %s ' % self.file_path
        self.z_crd=[]  #record z of each layer

    def __str__(self):
        return self.spec

    def get_prjt_name(self):
        return self.p_name

    def get_dj_name(self):
        return self.d_name

    def get_filepath(self):
        return self.file_path

    def get_edt(self):
        oE = self.oD.SetActiveEditor("3D Modeler")
        return oE

    def new_prjt(self):
        oProject = oDesktop.NewProject()
        oProject.InsertDesign("Maxwell 3D", self.d_name, "EddyCurrent", "")
        oDesign = oProject.SetActiveDesign(self.d_name)
        oProject.SaveAs(self.file_path + self.p_name + '.aedt', True)
        print ' ProjectName : %s, DesignName : %s' % (self.p_name, self.d_name)

        oDesktop.RestoreWindow()
        oProject = oDesktop.SetActiveProject(self.p_name)
        oDesign = oProject.SetActiveDesign(self.d_name)
        self.oP, self.oD = oProject, oDesign

    def open_prjt(self):
        oDesktop.OpenProject(self.file_path + self.p_name + '.aedt')
        oProject = oDesktop.SetActiveProject(self.p_name)
        oDesign = oProject.SetActiveDesign(self.d_name)
        self.oP, self.oD = oProject, oDesign

    def act_prjt(self):
        oProject = oDesktop.SetActiveProject(self.p_name)
        oDesign = oProject.SetActiveDesign(self.d_name)
        self.oP, self.oD = oProject, oDesign

    def save_prjt(self):
        print ' save : %s' % (self.file_path + self.p_name + '.aedt')
        self.oP.SaveAs(self.file_path + self.p_name + '.aedt', True)

    def close_prjt(self):
        oDesktop.CloseProject(self.p_name)

    def crt_region(self, pad=100, material='vacuum'):
        '''
        - if pad has one number, then put that into all direction
        - other wise pad has to be [] with 6 parameters
        :param pad: int or [int, int, ...]
        :param material:
        :return:
        '''
        self.act_coort()
        # if pad has one number, then put that into all direction
        padding=[]
        if type(pad)==int:
            for i in range(6):
                padding.append(pad)
        elif type(pad)==list:
            padding=pad

        oEditor = self.oD.SetActiveEditor("3D Modeler")
        oEditor.CreateRegion(
            [
                "NAME:RegionParameters",
                "+XPaddingType:=", "Percentage Offset",
                "+XPadding:="	, str(padding[0]),
                "-XPaddingType:="	, "Percentage Offset",
                "-XPadding:="		, str(padding[1]),
                "+YPaddingType:="	, "Percentage Offset",
                "+YPadding:="		, str(padding[2]),
                "-YPaddingType:="	, "Percentage Offset",
                "-YPadding:="		, str(padding[3]),
                "+ZPaddingType:="	, "Percentage Offset",
                "+ZPadding:="		, str(padding[4]),
                "-ZPaddingType:="	, "Percentage Offset",
                "-ZPadding:="		, str(padding[5])
            ],
            [
                "NAME:Attributes",
                "Name:="		, "Region",
                "Flags:="		, "Wireframe#",
                "Color:="		, "(255 0 0)",
                "Transparency:="	, 0.9,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\""+material+"\"",
                "SolveInside:="		, True
            ])


    def del_objt(self, name):
        oEditor = self.oD.SetActiveEditor("3D Modeler")
        oEditor.Delete(
            [
                "NAME:Selections",
                "Selections:="	, name
            ])

    def del_objts(self, material):
        '''
            - delete objects by material
        :param material:
        :return:
        '''
        list=self.get_objts(material)
        for i in list:
            self.del_objt(i)


    def get_objts(self, material):
        oEditor = self.oD.SetActiveEditor("3D Modeler")
        ObjectList = oEditor.GetObjectsByMaterial(material)  # SolidList is in list
        return ObjectList

    def act_coort(self, name='Global'):
        oEditor = self.oD.SetActiveEditor("3D Modeler")
        ''' activate global coordinate '''
        oEditor.SetWCS(
            [
                "NAME:SetWCS Parameter",
                #"Working Coordinate System:=", "Global",
                "Working Coordinate System:=", name,
                "RegionDepCSOk:=", False
            ])

    def set_section(self, name, plane):
        oEditor = self.oD.SetActiveEditor("3D Modeler")
        oEditor.Section(
            [
                "NAME:Selections",
                "Selections:="	, name,
                "NewPartsModelFlag:="	, "Model"
            ],
            [
                "NAME:SectionToParameters",
                "CreateNewObjects:="	, True,
                #"SectionPlane:="	, "YZ",
                "SectionPlane:=", plane,
                "SectionCrossObject:="	, False
            ])

        section_name=name+'_Section1'
        print ' make a %s from %s on %s' % (section_name, name, plane)
        return section_name

    def set_coort_z(self, name, z):
        oEditor = self.oD.SetActiveEditor("3D Modeler")
        self.act_coort()

        ''' ser relative coordinate at z distance from (0,0,0) '''
        oEditor.CreateRelativeCS(
            [
                "NAME:RelativeCSParameters",
                "Mode:="	, "Axis/Position",
                "OriginX:="		, "0mm",
                "OriginY:="		, "0mm",
                "OriginZ:="		, str(z*1000)+"mm",
                "XAxisXvec:="		, "1mm",
                "XAxisYvec:="		, "0mm",
                "XAxisZvec:="		, "0mm",
                "YAxisXvec:="		, "0mm",
                "YAxisYvec:="		, "1mm",
                "YAxisZvec:="		, "0mm"
            ],
            [
                "NAME:Attributes",
                "Name:="		, name
            ])

    def thicken(self, names_list, thick=None):
        '''
        :param names_list:['', '',..]
        :param thick:  float in m
        :return:
        '''
        if thick == None:
            thick=self.thick

        oEditor = self.oD.SetActiveEditor("3D Modeler")
        for name in names_list:
            oEditor.ThickenSheet(
                [
                    "NAME:Selections",
                    "Selections:="	, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:SheetThickenParameters",
                    "Thickness:="		, str(thick*1000)+"mm",
                    "BothSides:="		, False
                ])

##################################################
########### set up
##################################################

    def set_analysis(self, freq=1e5):
        print ' set analysis at %.1f kHz' %(freq/1000)
        oModule = self.oD.GetModule("AnalysisSetup")
        oModule.InsertSetup("EddyCurrent",
                            [
                                "NAME:Setup1",
                                "Enabled:="	, True,
                                "MaximumPasses:="	, 10,
                                "MinimumPasses:="	, 2,
                                "MinimumConvergedPasses:=", 1,
                                "PercentRefinement:="	, 30,
                                "SolveFieldOnly:="	, False,
                                "PercentError:="	, 1,
                                "SolveMatrixAtLast:="	, True,
                                "PercentError:="	, 1,
                                "UseCacheFor:="		, ["Pass"],
                                "UseIterativeSolver:="	, False,
                                "RelativeResidual:="	, 0.0001,
                                #"Frequency:="		, "100kHz",
                                "Frequency:="	, str(freq/1000.0)+"kHz",
                                "NonLinearResidual:="	, 0.0001,
                                "HasSweepSetup:="	, False,
                                "UseHighOrderShapeFunc:=", False
                            ])

    def analyze(self):
        print ' analyze'
        self.oD.AnalyzeAll()


    def set_1Arms(self, name):
        '''
        - name is a object in str
        :param name: str
        :return:
        '''

        print ' set 1Arms'
        oModule = self.oD.GetModule("BoundarySetup")
        oModule.AssignCurrent(
            [
                "NAME:Current1",
                #"Objects:="		, ["layer_1_Section1"],
                "Objects:="	, [name],
                "Phase:="		, "0deg",
                "Current:="		, "1.414A",
                "IsSolid:="		, True,
                "Point out of terminal:=", False
            ])

    def set_skin_mesh(self, names, depth, layer, length):
        '''
        - not sure that how to calculate SurfTriMaxLength. manually check and put that in.
        - better to use this function for script, not interactive process

        :param names: ["layer_1","layer_2",...]
        :param depth:
        :param layer:
        :param length:
        :return:
        '''
        print ' set mesh '
        oModule = self.oD.GetModule("MeshSetup")
        oModule.AssignSkinDepthOp(
            [
                #"NAME:SkinDepth1",
                "NAME:"+names[0],
                "Enabled:="	, True,
                "Objects:="		, names,
                "RestrictElem:="	, False,
                "NumMaxElem:="		, "1000",
                "SkinDepth:="		, str(depth * 1000.0) + "mm",
                #"SurfTriMaxLength:="	, "0.1mm",
                "SurfTriMaxLength:=", str(length * 1000.0) + "mm",
                "NumLayers:="		, str(layer)
            ])

    def del_cal(self):
        ''' Delete previous calculator expressions '''
        try:
            oModule = self.oD.GetModule("FieldsReporter")
            oModule.CalcStack("clear")
            oModule.ClearAllNamedExpr()
            print '\n delete expressions in a calculator'
        except:
            pass

    def del_rpt(self):
        ''' Delete previous reports '''
        try:
            oModule = self.oD.GetModule("ReportSetup")
            oModule.DeleteAllReports()
            print ' delete plots'
        except:
            pass

    def crt_rpt(self, names, format="Data Table"):  # form :"Rectangular Plot", "Data Table"

        if (format == 'Pot') or (format == 'Rectangular Plot'):  # 'Table' is fine
            form="Rectangular Plot"
        else:
            form="Data Table"  #default is table
        '''
        - plot calculator expression with frequency

        :param names: ["Rac","Lac",..]
        :param form:
        :return:
        '''
        print '\n %s ' % time.strftime("%d/%m/%Y %I:%M")
        oModule = self.oD.GetModule("ReportSetup")
        oModule.CreateReport("XY Plot 1", "Fields", form, "Setup1 : LastAdaptive",
                             [
                                 "Domain:="	, "Sweep"
                             ],
                             [
                                 "Freq:="		, ["All"],
                                 "Phase:="		, ["0deg"],
                             ],
                             [
                                 "X Component:="		, "Freq",
                                 # "Y Component:="		, ["Rac","Lac"]
                                 "Y Component:="		, names
                             ], [])


##################################################
########### calculator
##################################################
    def cal_loss(self, name='AllObjects'):
        '''
        - name has to be a object, default is AllObjects (calculate total ohmic loss)
        :param name:
        :return:
        '''

        # add volume first
        self.cal_vol(name)
        oModule = self.oD.GetModule("FieldsReporter")
        oModule.EnterQty("OhmicLoss")
        oModule.EnterVol(name)
        oModule.CalcOp("Integrate")

        name = name + '_loss'
        oModule.AddNamedExpression(name, "Fields")
        print ' calculator : %s' % name
        return name

    def cal_vol(self, name):
        '''
        name has to be a object
        name_list : list of the names in calculator in Maxwell
        '''
        oModule = self.oD.GetModule("FieldsReporter")
        oModule.EnterScalar(1)
        oModule.EnterVol(name)
        oModule.CalcOp("Integrate")

        name = name + '_vol'
        oModule.AddNamedExpression(name, "Fields")
        print ' calculator : %s' % name
        return name

    def cal_J_real(self, name):
        '''
        - name has to be a sheet
        :param name:
        :return:
        '''
        oModule = self.oD.GetModule("FieldsReporter")
        oModule.EnterQty("J")
        oModule.CalcOp("Real")
        oModule.EnterSurf(name)
        oModule.CalcOp("NormalComponent")
        oModule.CalcOp("Integrate")

        name=name+'_J_real'
        oModule.AddNamedExpression(name, "Fields")
        print ' calculator : %s'%name

    def cal_energy(self):
        '''
        - can be used for inductance calculation when excitation is 1Arms
        :return:
        '''

        oModule = oDesign.GetModule("FieldsReporter")
        oModule.EnterQty("energy")
        oModule.EnterVol("AllObjects")
        oModule.CalcOp("Integrate")
        oModule.AddNamedExpression("Energy", "Fields")

    def cal_sub(self, names):
        '''
        - names[0]= names[1]-names[2]-names[3]...
        :param names:  ['','','','']
        :return:
        '''
        oModule = self.oD.GetModule("FieldsReporter")
        oModule.CopyNamedExprToStack(names[0])
        for i in range(1, len(names)):
            oModule.CopyNamedExprToStack(names[i])
            oModule.CalcOp("-")
        oModule.AddNamedExpression(names[0], "Fields")

    def cal_add(self, names):
        '''
        - names[0]= names[1]-names[2]-names[3]...
        :param names:  ['','','','']
        :return:
        '''
        oModule = self.oD.GetModule("FieldsReporter")
        oModule.CopyNamedExprToStack(names[0])
        for i in range(1, len(names)):
            oModule.CopyNamedExprToStack(names[i])
            oModule.CalcOp("+")
        oModule.AddNamedExpression(names[0], "Fields")
