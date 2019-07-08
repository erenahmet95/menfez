import os

import sys

import comtypes.client

import sap2000_excel

from numpy import *

import menfez_koordinat

area_koordinat = menfez_koordinat.menfez()



# set the following flag to True to attach to an existing instance of the program

# otherwise a new instance of the program will be started

AttachToInstance = False

# set the following flag to True to manually specify the path to SAP2000.exe

# this allows for a connection to a version of SAP2000 other than the latest installation

# otherwise the latest installed version of SAP2000 will be launched

SpecifyPath = False

# if the above flag is set to True, specify the path to SAP2000 below

ProgramPath = 'C:\Program Files (x86)\Computers and Structures\SAP2000 21\SAP2000.exe'

# full path to the model

# set it to the desired path of your model

APIPath = 'C:\CSiAPIexample'

if not os.path.exists(APIPath):

    try:

        os.makedirs(APIPath)

    except OSError:

        pass

ModelPath = APIPath + os.sep + 'Menfez-Api.sdb'


if AttachToInstance:

    # attach to a running instance of SAP2000

    try:

        # get the active SapObject

        mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

    except (OSError, comtypes.COMError):

        print("No running instance of the program found or failed to attach.")

        sys.exit(-1)

else:

    # create API helper object

    helper = comtypes.client.CreateObject('SAP2000v20.Helper')

    helper = helper.QueryInterface(comtypes.gen.SAP2000v20.cHelper)

    if SpecifyPath:

        try:

            # 'create an instance of the SAPObject from the specified path

            mySapObject = helper.CreateObject(ProgramPath)

        except (OSError, comtypes.COMError):

            print("Cannot start a new instance of the program from " + ProgramPath)

            sys.exit(-1)

    else:

        try:

            # create an instance of the SAPObject from the latest installed SAP2000

            mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

        except (OSError, comtypes.COMError):

            print("Cannot start a new instance of the program.")

            sys.exit(-1)

    # start SAP2000 application

    mySapObject.ApplicationStart()

SapModel = mySapObject.SapModel

# initialize model

SapModel.InitializeNewModel()

# create new blank model

ret = SapModel.File.NewBlank()

# define material property

MATERIAL_CONCRETE = 2

ret = SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
ret = SapModel.PropMaterial.SetMaterial("Rebar",6)

# assign isotropic mechanical properties to material

ret = SapModel.PropMaterial.SetMPIsotropic('CONC', 3600, 0.2, 0.0000055)
ret = SapModel.PropMaterial.SetMPIsotropic("Rebar",420000,0.3,1.55*10**-5)
ret = SapModel.PropArea.SetShell_1("Duvar",1,True,"CONC",0,float(input("Thickness Değeri"))/0.025,float(input("Bending değerini giriniz"))/0.025)

# define rectangular frame section property

ret = SapModel.PropFrame.SetRectangle('R1', 'CONC', 12, 12)

# define frame section property modifiers

ModValue = [1000, 0, 0, 1, 1, 1, 1, 1]

ret = SapModel.PropFrame.SetModifiers('R1', ModValue)

# switch to k-ft units

birim = 6

ret = SapModel.SetPresentUnits(birim)

# x=[50,100,150,100,50,0]
# y=[0,0,40,80,80,40]
# z=[0,0,0,0,0,0]
eren = ' '
# ret = SapModel.AreaObj.AddByCoord(6,x,y,z,eren,)

for i in range(0,4):


    ret = SapModel.AreaObj.AddByCoord(4, area_koordinat[0][i],area_koordinat[1][i], area_koordinat[2][i],"")

ret = SapModel.LoadPatterns.Add("Q", 8)  ### 8 girişi Other olarak yükü atıyor
ret = SapModel.LoadPatterns.Add("SuBasinci", 8)
ret = SapModel.LoadPatterns.Add("ToprakBasinci", 8)

ret = SapModel.View.RefreshView()
NumberNames = int()
MyName = ''
MyLabel = list()
MyStory = list()
########Joint Patternları Tanımladık
ret = SapModel.PatternDef.SetPattern("Su_Basinci")
ret = SapModel.PatternDef.SetPattern("Toprak_Basinci")

alan = ''
val1 = int()
val2 = int()
ret = SapModel.AreaObj.SetLoadUniform("3", "DEAD", int(input("Sabit Yük Miktarı ")), 10)
ret = SapModel.AreaObj.SetLoadUniform("3", "Q", int(input("Hareketli Yük Miktarını Giriniz ")), 10)
for i in range(1,5):
    area_label = str(i)
    ret = SapModel.EditArea.Divide(area_label, 2, 4, alan, val1, val2, 20,20)  ### Edit yaparken 0.025 * n oranında bölüyor. NumberArea değişşsede fark etmiyort
# ret = SapModel.SelectObj.PlaneXY("3") ### Tüm XY düzlemini Seçiyor
Value = [True, True, False, False, False, True]  # Mafsal Şartları

Value2 = [False, True, False, False, False, False]  # DOFS

for i in range(2):
    i = str(i)
    #ret = SapModel.SelectObj.CoordinateRange(0, 0, 0, 480, 0, 160, False, "Global", True)
    ret = SapModel.SelectObj.PlaneYZ("2")

    ret = SapModel.PointObj.SetRestraint(i, Value2, 2)

ret = SapModel.AreaObj.SetSpring("ALL", 1, 14000, 1, " ", -2, 1, 3, True, list(), 0, False, "Local",2)  ## Orjinal fonksiyona göre farklı kullanım ile çalıştı.
###################### Joint Pattern Yüklerinin Atanması

'''
Joint Pattern Kullanırken Value Değeri Direk Tanımlanmış Joint Pattern lar ile çarpılıp uygulanıyor.
'''

'''
----Joint Pattern Değerlerini Hesaplama----

Tek Boyutta Yük Değiştiği İçin A=0 B = 0  C ve D Değerlerini Buluruz.

Burada Menfez Üst ve Alt  Kısımlarına Denk Gelen Toplam Kuvvet Değerlerini Bulduktan Sonra İşleme
Devam Ederiz. 

*** Sürsarj Etkileri+ Yanal Toprak Basıncları Hesaplanıp etki ettirilir.

Araçlardan Meydana Gelen Sursarj Etkisi = P3 = H30-S24/MenfezAlan = 300/(4*12) (Culmann Yöntemi)

Yanal Toprak Basınçları (Zeminin Aktif ve Pasif Etkileri Dikkate Alınarak Hesaplanmalıdır) 
***Rankine Ve Coulomb Yöntemi
P1 = K0*Gamazemin*H1(Menfez Üzeri Zemin yüksekliği)

P2 = K0*Gamazemin*H2(Menfez Yüksekliği Boyunca) + P1

Bütün değerler hesaplanıp örnek olacaak şekilde ; Menfez üst noktasında toplam 16.25 KN/m2 Alt noktasında 56.25Kn/M2
olarak hesaplanmıştır.

Pattern Denklemi Şu Şekilde olur. 
Pattern Value = A*x + B*y +C*z + D 
A*0 + B*0 +C*4 + 56.25 = 16.25 Buradan C = -10 olarak bulunur D = 56.25 olur


***** 






'''


ret = SapModel.PointObj.SetPatternByXYZ("ALL","Toprak_Basinci",0,0,-10,56.25,2,0,False)
ret = SapModel.PointObj.SetPatternByXYZ("ALL","Su_Basinci",0,0,-10,40,2,0,False)
ret = SapModel.SelectObj.ClearSelection()
ret = SapModel.SelectObj.PlaneYZ("2")
ret = SapModel.AreaObj.SetLoadSurfacePressure("ALL","ToprakBasinci",-2,1,"Toprak_Basinci",True,2)
ret = SapModel.AreaObj.SetLoadSurfacePressure("ALL","SuBasinci",-1,1,"Su_Basinci",True,2)
ret = SapModel.SelectObj.ClearSelection()

for i in range(2):
    i = str(i)
    #ret = SapModel.SelectObj.CoordinateRange(140, 161, 0, 480, 0, 160, False, "Global", True) ## İyi çalışmadığı için değiştirdim
    ret = SapModel.SelectObj.PlaneYZ("4") ### YZ ekseninde olan bir noktanın adını giriyoruz

    ret = SapModel.PointObj.SetRestraint(i, Value2, 2)

ret = SapModel.AreaObj.SetSpring("ALL", 1, 14000, 1, " ", -2, 1, 3, True, list(), 0, False, "Local",2)  ## Orjinal fonksiyona göre farklı kullanım ile çalıştı.
ret = SapModel.PointObj.SetPatternByXYZ("ALL","Toprak_Basinci",0,0,-10,56.25,2,0,False)
ret = SapModel.PointObj.SetPatternByXYZ("ALL","Su_Basinci",0,0,-10,40,2,0,False)
ret = SapModel.SelectObj.ClearSelection()
ret = SapModel.SelectObj.PlaneYZ("4")
ret = SapModel.AreaObj.SetLoadSurfacePressure("ALL","ToprakBasinci",-2,1,"Toprak_Basinci",True,2)
ret = SapModel.AreaObj.SetLoadSurfacePressure("ALL","SuBasinci",-1,1,"Su_Basinci",True,2)
ret = SapModel.SelectObj.ClearSelection()

for i in range(2):
    i = str(i)
    #ret = SapModel.SelectObj.CoordinateRange(0, 160, 0, 480, -20,-0.1, False, "Global",True)  ### Xmaksı Menfezin Değerlerini 0.025 e bölrek girmemiz lazım
    ret = SapModel.SelectObj.PlaneXY("1")
    ret = SapModel.PointObj.SetRestraint(i, Value,2)  ##  2 değeri, bir birinci görüştür olarak gelişigüzel bir noktası adını gösterir
##fonksiyon yok sayar.
ret = SapModel.AreaObj.SetSpring("ALL", 1, 40000, 1, " ", -2, 1, 3, True, list(), 0, False, "Local",2)  ## Orjinal fonksiyona göre farklı kullanım ile çalıştı.
#### 1 ALL adındaki bütün gruplara Etki ediyor - 2 Seçili Elemanlara Etki Ediyor

ret = SapModel.SelectObj.ClearSelection()

# ret = SapModel.SelectObj.All() ### Tekli fonksiyonları () ile kullan VB den farklı




#ret = SapModel.AreaObj.SetLoadSurfacePressure("ALL", "SuBasinci", -2, 10, "Su_Basinci", True, 2)
ret = SapModel.SetPresentUnits(birim)
ret = SapModel.File.Save(ModelPath)

ret = SapModel.Analyze.RunAnalysis()
ret = SapModel.SelectObj.PlaneXY("3")
'''
SAP API fonksiyonlarında Double olan değişkenleri PYTHON ' da liste olarak tanımlayabiliriz. 

NumberR


'''

NumberResults = 0
Object = []
Element = []
Point_element = []

Acase = []
StepType = []
StepNum = []
F11 =[]
F22=[]
F12 = []
FMax= []
FMin= []
FAngle =[]
FVM = []
M11 = []
M22 = []
M12 = []
MMax = []
Mmin=[]
MAngle = []
V13= []
V23= []
VMax = []
VAngle = []
ObjectElm = 0
ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

[NumberResults,Object,Element,Point_element,Acase,StepType,StepNum,F11,F22,F12,FMax,FMin,FAngle,FVM,M11,M22,M12,MMax,Mmin,MAngle,V13,V23,VMax,VAngle,ret]= SapModel.Results.AreaForceShell("ALL",3,NumberResults,Object,Element,Point_element,Acase,StepType,StepNum,F11,F22,F12,FMax,FMin,FAngle,FVM,M11,M22,M12,MMax,Mmin,MAngle,V13,V23,VMax,VAngle)


print(Acase)
print(StepType)
print(StepNum)
print(Element)
print(Object)
print("F11 Doğrultusu Kuvvet",F11)
print("F12 Doğrultusu Kuvvetler",F12)
print("M11 Doğrultusu Moment",M11)
print("M12 doğrultusu",M12)
print("M22 Doğrultusu ",M22)



