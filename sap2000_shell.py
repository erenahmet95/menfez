import os

import sys

import comtypes.client

import  sap2000_excel

from    numpy import *


### İlk önce kabuk elemanları parçaları girilecek sonra koordinat dosyaları
c = sap2000_excel.excel2()
d = sap2000_excel.excel2()

shell_1 = []
for x in c[2]:
    for j in range(len(d[0])):
        if x == d[0][j]:


            shell_1.append([x,d[2][j],d[3][j],d[4][j]])
shell_2 = []
for x in c[3]:
    for j in range(len(d[0])):
        if x == d[0][j]:


            shell_2.append([x,d[2][j],d[3][j],d[4][j]])
shell_3 = []
for x in c[4]:
    for j in range(len(d[0])):
        if x == d[0][j]:


            shell_3.append([x,d[2][j],d[3][j],d[4][j]])
shell_4 = []
for x in c[5]:
    for j in range(len(d[0])):
        if x == d[0][j]:


            shell_4.append([x,d[2][j],d[3][j],d[4][j]])
shell_1=array(shell_1)
shell_2=array(shell_2)
shell_3=array(shell_3)
shell_4=array(shell_4)

area_koordinat = hstack((shell_1,shell_2,shell_3,shell_4))
area_koordinat = area_koordinat[1::]
area_koordinat = area_koordinat.astype(float)

#set the following flag to True to attach to an existing instance of the program

#otherwise a new instance of the program will be started

AttachToInstance = False



#set the following flag to True to manually specify the path to SAP2000.exe

#this allows for a connection to a version of SAP2000 other than the latest installation

#otherwise the latest installed version of SAP2000 will be launched

SpecifyPath = False



#if the above flag is set to True, specify the path to SAP2000 below

ProgramPath = 'C:\Program Files (x86)\Computers and Structures\SAP2000 21\SAP2000.exe'



#full path to the model

#set it to the desired path of your model

APIPath = 'C:\CSiAPIexample'

if not os.path.exists(APIPath):

        try:

            os.makedirs(APIPath)

        except OSError:

            pass

ModelPath = APIPath + os.sep + 'API_1-001.sdb'



if AttachToInstance:

    #attach to a running instance of SAP2000

    try:

        #get the active SapObject

        mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

    except (OSError, comtypes.COMError):

        print("No running instance of the program found or failed to attach.")

        sys.exit(-1)

else:

    #create API helper object

    helper = comtypes.client.CreateObject('SAP2000v20.Helper')

    helper = helper.QueryInterface(comtypes.gen.SAP2000v20.cHelper)

    if SpecifyPath:

        try:

            #'create an instance of the SAPObject from the specified path

            mySapObject = helper.CreateObject(ProgramPath)

        except (OSError, comtypes.COMError):

            print("Cannot start a new instance of the program from " + ProgramPath)

            sys.exit(-1)

    else:

        try:

            #create an instance of the SAPObject from the latest installed SAP2000

            mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

        except (OSError, comtypes.COMError):

            print("Cannot start a new instance of the program.")

            sys.exit(-1)



    #start SAP2000 application

    mySapObject.ApplicationStart()


SapModel = mySapObject.SapModel



#initialize model

SapModel.InitializeNewModel()



#create new blank model

ret = SapModel.File.NewBlank()



#define material property

MATERIAL_CONCRETE = 2

ret = SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)



#assign isotropic mechanical properties to material

ret = SapModel.PropMaterial.SetMPIsotropic('CONC', 3600, 0.2, 0.0000055)



#define rectangular frame section property

ret = SapModel.PropFrame.SetRectangle('R1', 'CONC', 12, 12)



#define frame section property modifiers

ModValue = [1000, 0, 0, 1, 1, 1, 1, 1]

ret = SapModel.PropFrame.SetModifiers('R1', ModValue)



#switch to k-ft units

kip_ft_F = 6

ret = SapModel.SetPresentUnits(kip_ft_F)

#x=[50,100,150,100,50,0]
#y=[0,0,40,80,80,40]
#z=[0,0,0,0,0,0]
point = ' '
#ret = SapModel.AreaObj.AddByCoord(6,x,y,z,eren,)

for i in range(len(area_koordinat)):
    x= []
    x.append([area_koordinat[i][1],area_koordinat[i][5],area_koordinat[i][9],area_koordinat[i][13]])
    y = []
    y.append([area_koordinat[i][2],area_koordinat[i][6],area_koordinat[i][10],area_koordinat[i][14]])
    z= []
    z.append([area_koordinat[i][3],area_koordinat[i][7],area_koordinat[i][11],area_koordinat[i][15]])

    ret = SapModel.AreaObj.AddByCoord(4,x[0],y[0],z[0],point)
    i = str(i)
    red = SapModel.AreaObj.GetPoints(i,)




ret = SapModel.View.RefreshView()
