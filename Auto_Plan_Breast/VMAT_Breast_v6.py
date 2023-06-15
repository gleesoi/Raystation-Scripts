'''
TITLE: 'Auto Plan Breast'
AUTHOR: Ian Gleeson
PURPOSE: Auto plan breasts 26/5 tangents, 48/15 sibs, vmat nodes 40/15
REQUIREMENTS: CPython 3.8 64-bit interpreter
TPS VERSION: 12A
HISTORY: v6.0.0 - logging plan stats to text files, reversed laterality names rois, OPT AND PRESCRIBE TO PTVP_4800_DVH NOW NOT PTVp_4800, opt function weights improved
VERSION: 6.0.0

'''

from connect import *
import math
import connect, ctypes, sys
import os
import numpy as np
import datetime
from tkinter import *
from tkinter import messagebox

def autoplanVMAT():
    startTime = datetime.datetime.now()
    script_version = '6.0.0'
    script_name = 'Auto Plan Breast'
    #written by Ian Gleeson
    #runs in CPython 3.6 64bit ## now use 3.6 cPython for use tkinter
    #Raystattion 12A
    #Summer 2021

    ###########next buttons to select course and then autoplan
    top = Toplevel()
    top.title("Auto Plan Breast v" + str(script_version))
    mycolour = '#%02x%02x%02x' % (50, 50, 50)
    myorange = '#%02x%02x%02x' % (255, 140, 0)
    top.configure(background = mycolour)
    top.geometry("780x240")
    ######add label#######################
    lbl1 = Label(top, text='Load the approved case (no plan should be open) with Drs contours. Select the course, machine and clinical goals and then click Start')
    lbl1.place(x=65, y =5)
    lbl1.configure(background = mycolour, fg = "white", justify=CENTER)
    
    def autoVMAT():
        #get current case, patient and examination
        db = get_current("PatientDB")

        try:
            patient = get_current("Patient")
        except:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No patient loaded. Please open a patient")
            exit()

        try:
            case = get_current("Case")
        except:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No case loaded. Please open a case")
            exit()
        try:
            examination = get_current("Examination")
            print (examination.Name)
        except:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No examination loaded. Please open an examination")
            exit()

        try:
            plan = get_current("Plan")
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Close current plan before running script")
            exit()
        except:
            pass    
        
        ##flag if dont select course, machine or breathing
        if clicked.get() == 'Select MOSAIQ Course':
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Please Select MOSAIQ Course")
            exit()
            
        if clicked2.get() == 'Select Machine':
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Please Select Machine")
            exit()
        
        #gives error if not HFS and then exits when user hits ok. runs with C python but text errors with iron python cant see all letters
        if examination.PatientPosition != 'HFS':
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Script only for HFS!")
            exit() 


        #checks if roi Skin exits. if not, gives a error messege
        rois = case.PatientModel.RegionsOfInterest 

        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
            
        if 'Skin' not in roi_list:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No ROI called 'Skin' found!")
            exit()
        
        if 'CTVp_4000' not in roi_list:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No ROI called 'CTVp_4800' found!")
            exit()
            
        if 'Heart' not in roi_list:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No ROI called 'Heart' found!")
            exit()
            
        #access roi structures    
        roi_structures = case.PatientModel.StructureSets[examination.Name].RoiGeometries
        
        if 'CTVp_4000' in roi_list:
            if roi_structures["CTVp_4000"].HasContours() is False:
                top = Tk()
                top.withdraw()
                messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "ROI 'CTVp_4000' needs outlining first!")
                exit()
                
        if 'CTVp_4800' in roi_list:
            if roi_structures["CTVp_4800"].HasContours() is True:
                SIB_plan = 'Yes'
            if roi_structures["CTVp_4800"].HasContours() is False:
                SIB_plan = 'No'
                
                
        if 'CTVp_4800' not in roi_list:
            SIB_plan = 'No'
            
        print(SIB_plan)
            
            
                
        if 'Heart' in roi_list:
            if roi_structures["Heart"].HasContours() is False:
                top = Tk()
                top.withdraw()
                messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "ROI 'Heart' needs outlining first!")
                exit()
           
        
        #any plan in case exist then it cannot be called 'L Breast Inital' or 'R Breast Inital' as thats what plan can be called later - only will apply if case has some plans
        if len(case.TreatmentPlans) != 0:
            for p in case.TreatmentPlans:
                if p.Name in ['R_Breast_Initial', 'L_Breast_Initial']:
                    top = Tk()
                    top.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No Plan Name in Case can be called 'L_Breast_Initial' or 'R_Breast_Initial'")
                    exit()
                    
        ##determine laterality of CTVp_4000 if left or right sided breast
        roi_centerCTVp4000 = roi_structures['CTVp_4000'].GetCenterOfRoi()
        CTVp4000_coordinates = {'x':roi_centerCTVp4000.x, 'y':roi_centerCTVp4000.y, 'z':roi_centerCTVp4000.z}
        
        if roi_centerCTVp4000.x > 0:
            plan_name = 'L_Breast_Initial'
        else:
            plan_name = 'R_Breast_Initial'        

        #access pois for a list
        pois = case.PatientModel.PointsOfInterest
                   
        poi_list = []

        for poi in pois:
            if poi.Type == 'LocalizationPoint':
                poi_list.append(poi.Name)
                
        ##if the list above is empty then theres no localization point present
        if len(poi_list) == 0:
            top = Tk()
            top.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No POI with Type 'LocalizationPoint' defined!")
            exit()

        # Get POI geometries 
        poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries

        #for item in poi_list. uses the localisation point type as point here which is the index 0 point in list if present     
        center_x = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.x
        center_y = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.y
        center_z = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.z

        #Sets window to Patient modelling and side menu to ROIs
        ui = get_current('ui')
        ui.TitleBar.Navigation.MenuItem['Patient modeling'].Button_Patient_modeling.Click()
        ui.TabControl_Modules.TabItem['Structure definition'].Button_Structure_definition.Click()
        ui.ToolPanel.TabItem['ROIs'].Select() # go to ROI side tools
        
        #makes roi box at ant tattoo

        with CompositeAction('Create box ROI (set up point ROI)'):

          retval_0 = case.PatientModel.CreateRoi(Name=r"set up point ROI", Color="Blue", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_0.CreateBoxGeometry(Size={ 'x': 1.5, 'y': 1.5, 'z': 1.0 }, Examination=examination, Center={ 'x': center_x, 'y': center_y, 'z': center_z }, Representation="TriangleMesh", VoxelSize=None)

          # CompositeAction ends
          
        with CompositeAction('Expand (ant box1)'):

          retval_1 = case.PatientModel.CreateRoi(Name=r"ant box1", Color="Yellow", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_1.SetMarginExpression(SourceRoiName=r"set up point ROI", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 15, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('Expand (ant box2)'):

          retval_2 = case.PatientModel.CreateRoi(Name=r"ant box2", Color="255, 128, 0", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_2.SetMarginExpression(SourceRoiName=r"ant box1", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 15, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_2.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('Create wall (Skin wall)'):

          retval_3 = case.PatientModel.CreateRoi(Name=r"Skin wall", Color="Aqua", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_3.SetWallExpression(SourceRoiName=r"Skin", OutwardDistance=0.3, InwardDistance=0.3)

          retval_3.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('ROI algebra (ant tattoo ROI)'):

          retval_4 = case.PatientModel.CreateRoi(Name=r"ant tattoo ROI", Color="255, 0, 128", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_4.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"ant box2"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Skin wall"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_4.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 

        #need to get center coordinates of ROI ant tattoo ROI to use below to make poi tattoo in center
        roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
        roi_name = 'ant tattoo ROI'
        roi_center = roi_geometries[roi_name].GetCenterOfRoi()
        center_ant_tattoo_ROI_coordinates = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}

        #makes ant tattoo point
        retval_5 = case.PatientModel.CreatePoi(Examination=examination, Point=center_ant_tattoo_ROI_coordinates, Name=r"Med tattoo", Color="Yellow", VisualizationDiameter=1, Type="Undefined")


        #makes left side tattoo ROI box
        with CompositeAction('Expand (left box1)'):

          retval_0 = case.PatientModel.CreateRoi(Name=r"left box1", Color="SaddleBrown", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_0.SetMarginExpression(SourceRoiName=r"set up point ROI", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 15 })

          retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('Expand (left box2)'):

          retval_1 = case.PatientModel.CreateRoi(Name=r"left box2", Color="Lime", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_1.SetMarginExpression(SourceRoiName=r"left box1", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 15 })

          retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('ROI algebra (left tattoo ROI)'):

          retval_2 = case.PatientModel.CreateRoi(Name=r"left tattoo ROI", Color="Green", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_2.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"left box2"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Skin wall"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_2.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        #need to get center coordinates of ROI left tattoo ROI to use below to make poi tattoo in center
        roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
        roi_name = 'left tattoo ROI'
        roi_center = roi_geometries[roi_name].GetCenterOfRoi()
        center_left_tattoo_ROI_coordinates = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}

        #makes ant tattoo point
        retval_5 = case.PatientModel.CreatePoi(Examination=examination, Point=center_left_tattoo_ROI_coordinates, Name=r"Left lat tattoo", Color="Yellow", VisualizationDiameter=1, Type="Undefined")


        #makes right side tattoo ROI box
        with CompositeAction('Expand (right box1)'):

          retval_4 = case.PatientModel.CreateRoi(Name=r"right box1", Color="Magenta", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_4.SetMarginExpression(SourceRoiName=r"set up point ROI", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 15, 'Left': 0 })

          retval_4.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('Expand (right box2)'):

          retval_5 = case.PatientModel.CreateRoi(Name=r"right box2", Color="255, 128, 0", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_5.SetMarginExpression(SourceRoiName=r"right box1", MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 15, 'Left': 0 })

          retval_5.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('ROI algebra (right tattoo ROI)'):

          retval_6 = case.PatientModel.CreateRoi(Name=r"right tattoo ROI", Color="255, 0, 128", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_6.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"right box2"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Skin wall"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_6.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 

        #need to get center coordinates of ROI right tattoo ROI to use below to make poi tattoo in center
        roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
        roi_name = 'right tattoo ROI'
        roi_center = roi_geometries[roi_name].GetCenterOfRoi()
        center_right_tattoo_ROI_coordinates = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}

        #makes lat tattoo point
        retval_5 = case.PatientModel.CreatePoi(Examination=examination, Point=center_right_tattoo_ROI_coordinates, Name=r"Right lat tattoo", Color="Yellow", VisualizationDiameter=1, Type="Undefined")


        #deletes the tattoo rois and skin ring ROIs
        with CompositeAction('Delete ROI (set up point ROI, ant box1, ant box2, Skin wall, ant tattoo ROI, left box1, left box2, left tattoo ROI, right box1, right box2, right tattoo ROI)'):

          case.PatientModel.RegionsOfInterest['set up point ROI'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['ant box1'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['ant box2'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['Skin wall'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['ant tattoo ROI'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['left box1'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['left box2'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['left tattoo ROI'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['right box1'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['right box2'].DeleteRoi()

          case.PatientModel.RegionsOfInterest['right tattoo ROI'].DeleteRoi()

          # CompositeAction ends
          
        #delete contralateral poi created
        if plan_name == 'L_Breast_Initial':
            case.PatientModel.PointsOfInterest['Right lat tattoo'].DeleteRoi()
        elif plan_name == 'R_Breast_Initial':
            case.PatientModel.PointsOfInterest['Left lat tattoo'].DeleteRoi()


        ###############################################################  COUCH ###################################################################
        def sort_couch():
            tpm = db.LoadTemplatePatientModel(templateName = 'AA_Couch top (no densities)', lockMode = 'Read')

            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName='CT 1', SourceRoiNames=["Couch Top"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="AlignImageCenters")


            #Get POI geometries 
            poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries
             
            #LIST TO ADD THE most post Skin y COORDINATE on slice where z is 0
            z_value = center_z  #ref slice coordinate
            z_coord = []
            y_coords = []

            ##need to get closest contour point to ref slice coordinate
            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['Skin'].PrimaryShape.Contours):
                for coordinate in contour:
                    array = coordinate.z ##need to find closest z value to ref point z value
                    idx = (np.abs(array - z_value)).argmin()
                    z_coord.append(idx)
                    if coordinate.z == z_coord[0]:   #on slice 0 gets list of all x values 
                        y_coords.append(coordinate.y)


            new_ySkin = max(y_coords)  # most post skin y value on ref slice


            ##move couch to align with Skin contour on ref slice and then 9.5cm post. htis based on standard distance bweteen board and couch at ref. some patients may differ depednning on board angle.
            ss = case.PatientModel.StructureSets[examination.Name]
               
            couch_thickness = 7.54
            Skin_box = ss.RoiGeometries['Skin'].GetBoundingBox()
            couch_box = ss.RoiGeometries["Couch Top"].GetBoundingBox()

            y_translation = -(abs(couch_box[1].y - new_ySkin)-couch_thickness) + 9.5

            transMat = {
            'M11':1.0,'M12':0.0,'M13':0.0,'M14':0,  ##x move
            'M21':0.0,'M22':1.0,'M23':0.0,'M24':y_translation,  ##y move AP
            'M31':0.0,'M32':0.0,'M33':1.0,'M34':0.0,    ##z move sup inf
            'M41':0.0,'M42':0.0,'M43':0.0,'M44':1.0}
            case.PatientModel.RegionsOfInterest["Couch Top"].TransformROI3D(Examination=examination, TransformationMatrix=transMat)
            
            ##now we can assign the density and structure type to the couch ROI##add a material to couch by loading an emprty roi template with cork93 material which will become index [0]
            tpm = db.LoadTemplatePatientModel(templateName = 'zzCork93', lockMode = 'Read')
            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName='CT 1', SourceRoiNames=["zzCork93"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")
            case.PatientModel.RegionsOfInterest['Couch Top'].SetRoiMaterial(Material=case.PatientModel.Materials[0])

            ##make couch top a support roi now
            with CompositeAction('Apply ROI changes (Couch Top)'):

              case.PatientModel.RegionsOfInterest['Couch Top'].Type = "Support"

              case.PatientModel.RegionsOfInterest['Couch Top'].OrganData.OrganType = "Other"

            ##delete the zzcork roi
            case.PatientModel.RegionsOfInterest['zzCork93'].DeleteRoi()
        
        if 'Couch Top' not in roi_list:       
            sort_couch()
        ###############################################################  END COUCH ###################################################################
        
        ###############################################################  SORT LUNGS ###################################################################
        def sort_lungs():
            rois = case.PatientModel.RegionsOfInterest 
            roi_list = []  

            for roi in rois:
                roi_list.append(roi.Name)
                
            if 'Lung_Contra' not in roi_list:
                clung_present = 'False'
                case.PatientModel.CreateRoi(Name=r"Lung_Contra", Color="Teal", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            else:
                clung_present = 'True'

            if 'Lung_Ipsi' not in roi_list:
                ipsil_present = 'False'
                case.PatientModel.CreateRoi(Name=r"Lung_Ipsi", Color="Teal", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            else:
                ipsil_present = 'True'
                

            #try run MBS for BOTH lung ROIs - if error then likely exists already
            try:
                case.PatientModel.MBSAutoInitializer(MbsRois=[{ 'CaseType': "Thorax", 'ModelName': r"Lung (Left)", 'RoiName': r"Lung (Left)", 'RoiColor': "255, 51, 204" }], CreateNewRois=True, Examination=examination, UseAtlasBasedInitialization=True)
                case.PatientModel.AdaptMbsMeshes(Examination=examination, RoiNames=[r"Lung (Left)"], CustomStatistics=None, CustomSettings=None)

                case.PatientModel.MBSAutoInitializer(MbsRois=[{ 'CaseType': "Thorax", 'ModelName': r"Lung (Right)", 'RoiName': r"Lung (Right)", 'RoiColor': "0, 255, 0" }], CreateNewRois=True, Examination=examination, UseAtlasBasedInitialization=True)
                case.PatientModel.AdaptMbsMeshes(Examination=examination, RoiNames=[r"Lung (Right)"], CustomStatistics=None, CustomSettings=None)
            except:
                pass


            #copy lung rois into correctly named ROis if left or right sided plan
            if plan_name == 'L_Breast_Initial':
                if ipsil_present == 'False':
                    with CompositeAction('ROI algebra (Lung_Ipsi)'):
                        retval_0 = case.PatientModel.RegionsOfInterest['Lung_Ipsi'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Left)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                        retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

                if clung_present == 'False':    
                    with CompositeAction('ROI algebra (Lung_Contra)'):
                        retval_0 = case.PatientModel.RegionsOfInterest['Lung_Contra'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Right)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                        retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            if plan_name == 'R_Breast_Initial':
                if ipsil_present == 'False':
                    with CompositeAction('ROI algebra (Lung_Ipsi)'):
                        retval_0 = case.PatientModel.RegionsOfInterest['Lung_Ipsi'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Right)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                        retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
                if clung_present == 'False':      
                    with CompositeAction('ROI algebra (Lung_Contra)'):
                        retval_0 = case.PatientModel.RegionsOfInterest['Lung_Contra'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Left)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                        retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            #delete MBS named lung ROIs
            try:
                case.PatientModel.RegionsOfInterest['Lung (Left)'].DeleteRoi()
                case.PatientModel.RegionsOfInterest['Lung (Right)'].DeleteRoi()
            except:
                pass
                
        sort_lungs()
        ###############################################################  END LUNGS ###################################################################
        
        ###############################################################  LOAD empties CB, ARM ###################################################################
        def load_empties():
            #load template with contra breast and arm block. it wont load any roi thats already present such as contra breast
            tpm = db.LoadTemplatePatientModel(templateName = 'Breast_T4&5(IMC)', lockMode = 'Read')
            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName='CT 1', SourceRoiNames=["zzArm", "Breast_Contra"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")
            #############################################################################################################
            ###turns off all rois and pois except ipsi lung and skin
            rois = case.PatientModel.RegionsOfInterest 

            for roi in rois:
                patient.SetRoiVisibility(RoiName=roi.Name, IsVisible=False)

            patient.SetRoiVisibility(RoiName='Lung_Ipsi', IsVisible=True)
            patient.SetRoiVisibility(RoiName='Lung_Contra', IsVisible=True)
            patient.SetRoiVisibility(RoiName='Breast_Contra', IsVisible=True)
            patient.SetRoiVisibility(RoiName='Skin', IsVisible=True)
            patient.SetRoiVisibility(RoiName='zzArm', IsVisible=True)
            patient.SetRoiVisibility(RoiName='Couch Top', IsVisible=True)
            
            ##pauze for planner to sort couch, arm block and cb and review lungs
            await_user_input("Please review the created auto seg ROIs (Lung_Ipsi and Lung_Contra), outline Breast_Contra manually, zzArm and position Couch Top if needed\n\nOnce happy please click resume at the bottom left of the Scripting Menu")
            
        load_empties()
        ###############################################################  END load empties ###################################################################
        
        ##check contra breast outlined and flag if empty. arm may not always be applicable?
        rois = case.PatientModel.RegionsOfInterest 
        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
            
        if 'Breast_Contra' not in roi_list:
            await_user_input("Please outline a 'Breast_Contra' ROI\n\nOnce happy please click resume at the bottom left of the Scripting Menu")
            
        if 'Breast_Contra' in roi_list:
            if roi_structures["Breast_Contra"].HasContours() is False:
                await_user_input("Please outline a 'Breast_Contra' ROI\n\nOnce happy please click resume at the bottom left of the Scripting Menu")
        ############################################################################################################

        ###test load teample all rois that are not in list yet. will include sib ptvs also 
        Template = db.LoadTemplatePatientModel(templateName='Breast_T4&5(IMC)', lockMode="Read")
                
        #Loop through list of ROI's, and then import missing ones from chosen template	
        roi_geometries = case.PatientModel.RegionsOfInterest
        roi_Names = [roi.Name for roi in roi_geometries]
        
        newROI = []
        for roi in Template.PatientModel.RegionsOfInterest:
            Match_roi = 0
            for j in roi_Names:
                if roi.Name == j:
                    Match_roi = Match_roi + 1
            if Match_roi == 0:
                newROI.append(roi.Name)
        #print('newROI', newROI)
        case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.LoadTemplatePatientModel(templateName = 'Breast_T4&5(IMC)'),
        SourceExaminationName=r"CT 1", SourceRoiNames=newROI, SourcePoiNames=[], AssociateStructuresByName=True,
        TargetExamination=examination, InitializationOption="EmptyGeometries")
        
        ###############################################################  UPDATE ROIS ###################################################################
        ##update rois that are derived and unapproved
        def update_rois():
            ##update rois that are derived and unapproved
            Exam_Name = examination.Name

            #list ALL rois set 0
            list = []
            rois = case.PatientModel.StructureSets[Exam_Name].SubStructureSets[0].RoiStructures
            for roi in rois:
                list.append(roi.OfRoi.Name)
                
            #list ONLY approved rois set 1
            list2 = []
            rois2 = case.PatientModel.StructureSets[Exam_Name].SubStructureSets[1].RoiStructures
            for roi in rois2:
                if roi.OfRoi.Name in list:
                    list.remove(roi.OfRoi.Name)

            #now list of only unapproved ones
            list

            roi_geometries = case.PatientModel.RegionsOfInterest
            for roi in roi_geometries:
                if roi.DerivedRoiExpression is not None:
                    if roi.Name in list:
                        case.PatientModel.RegionsOfInterest[roi.Name].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")  
                        
                
        update_rois()
        
        ###############################################################  END MAKE ROIS NOT LOADED ###################################################################
        ###############################################################  DELETE EMPTY UNAPPROVED ROIS ROIS ###################################################################
        def delete_empties():
            approved_empty_rois = [] 

            sub_structure_set_list = case.PatientModel.StructureSets[examination.Name].SubStructureSets

            for structure_set in sub_structure_set_list:
                rois = structure_set.RoiStructures
                uncontoured = [roi for roi in rois if not roi.HasContours()]
                for roi in uncontoured:
                    try:
                        roi.OfRoi.DeleteRoi()
                    except:
                        approved_empty_rois.append(roi.OfRoi.Name)

            if approved_empty_rois:
                aprv_empties = []
                [aprv_empties.append(x) for x in approved_empty_rois if x not in aprv_empties]            
                #messagebox.showinfo('Auto Plan Breast v' + str(script_version), 'Structure set contains these approved empty ROIs:' + str(aprv_empties))
                   
        delete_empties()
        ###############################################################  END DELETE EMPTY UNAPPROVED ROIS ROIS ###################################################################

        ########################################################################################
        #sort these as not done as rely on others
        try:
            #case.PatientModel.RegionsOfInterest['PTVn_LN_Combined'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            case.PatientModel.RegionsOfInterest['zzRing_AllPTV'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            case.PatientModel.RegionsOfInterest['zzRVR'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            case.PatientModel.RegionsOfInterest['Skin-PTVAndAx'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            case.PatientModel.RegionsOfInterest['zzPlanning Bolus Full VMAT'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
        except:
            pass
        

        
        ##go to beamset tab ui
        ui.TitleBar.Navigation.MenuItem['Plan design'].Button_Plan_design.Click() #go to plan design
        ui.TabControl_Modules.TabItem['Plan setup'].Button_Plan_setup.Click()  ##plansetup tab
        #ui.Workspace.TabControl['Plan'].TabItem['Beams'].Select()   ##beams tab


        #########################################################################################
        
        #identify machine
        
        ##add new beamset0 dep on what selected machine - default elekta regardless of what clicked
        if clicked2.get() == 'TrueBeamSTx':
            machine_name = 'Agility'
        if clicked2.get() == 'Agility':
            machine_name = 'Agility'
           
        #add plan and beamset    
        with CompositeAction('Add Treatment plan'):

            retval_0 = case.AddNewPlan(PlanName=plan_name, PlannedBy=r"", Comment=r"", ExaminationName=examination.Name, IsMedicalOncologyPlan=False, AllowDuplicateNames=False)
            retval_1 = retval_0.AddNewBeamSet(Name=plan_name, ExaminationName=examination.Name, MachineName="Agility", Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=15, CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined" }, Custom=None, ToleranceTableLabel=None)

        patient.Save()
        
        plan = case.TreatmentPlans[plan_name]
        plan.SetCurrent()
    
        plan = get_current("Plan")
        beam_set = get_current("BeamSet")
        
        if SIB_plan == 'No':
            beam_set.AddRoiPrescriptionDoseReference(RoiName="PTVp_4000", PrescriptionType="MedianDose", DoseValue=4000, RelativePrescriptionLevel=1.0)
        if SIB_plan == 'Yes':
            beam_set.AddRoiPrescriptionDoseReference(RoiName="PTVp_4800_DVH", PrescriptionType="MedianDose", DoseValue=4800, RelativePrescriptionLevel=1.0)
            
        
        beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })

        #get iso center ptv combined
        roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
        roi_name = 'PTV_Combined'
        roi_center = roi_geometries[roi_name].GetCenterOfRoi()
        PTV_coordinates = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}


        ##add new beams dual arcs - iso is at ref slice but center AP and RL of PTV combined
        if plan.Name =='L_Breast_Initial':
            beam_set.CreateArcBeam(ArcStopGantryAngle=179, ArcRotationDirection="Clockwise", BeamQualityId=r"6", IsocenterData={ 'Position': { 'x':roi_center.x, 'y':roi_center.y, 'z':center_z }, 'NameOfIsocenterToRef': plan.Name, 'Name': plan.Name, 'Color': "255, 255, 128" }, Name=r"EA01", Description=r"EA01 VMAT", GantryAngle=310, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=10)
            beam_set.CreateArcBeam(ArcStopGantryAngle=310, ArcRotationDirection="CounterClockwise", BeamQualityId=r"6", IsocenterData=beam_set.GetIsocenterData(Name=plan.Name), Name=r"EA02", Description=r"EA02 VMAT", GantryAngle=179, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=350)

        if plan.Name =='R_Breast_Initial':
            beam_set.CreateArcBeam(ArcStopGantryAngle=181, ArcRotationDirection="CounterClockwise", BeamQualityId=r"6", IsocenterData={ 'Position': { 'x':roi_center.x, 'y':roi_center.y, 'z':center_z }, 'NameOfIsocenterToRef': plan.Name, 'Name': plan.Name, 'Color': "255, 255, 128" }, Name=r"EA01", Description=r"EA01 VMAT", GantryAngle=50, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=10)
            beam_set.CreateArcBeam(ArcStopGantryAngle=50, ArcRotationDirection="Clockwise", BeamQualityId=r"6", IsocenterData=beam_set.GetIsocenterData(Name=plan.Name), Name=r"EA02", Description=r"EA02 VMAT", GantryAngle=181, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=350)


        ##check sup inf ok 13cm? move if not
        #ISO POINT
        iso_z = beam_set.Beams[0].Isocenter.Position.z   ## iso z level value  2.22

        ss = case.PatientModel.StructureSets[examination.Name]

        PTVCombined_roi_box = ss.RoiGeometries['PTV_Combined'].GetBoundingBox()

        z_max = PTVCombined_roi_box[1].z   ##most sup is positive value  4.05

        distance_imaging = z_max - iso_z  #11.12
        
        iso_name = beam_set.Beams[0].Isocenter.Annotation.Name

        #moves iso sup inf if distance >13cm iso to most sup PTV_Combined
        if distance_imaging > 13.5:
            new_isoZ = iso_z + distance_imaging - 13.5
            beam_set.Beams[0].Isocenter.EditIsocenter(Name=iso_name, Position={'x':roi_center.x, 'y':roi_center.y, 'z':new_isoZ})
            beam_set.Beams[1].Isocenter.EditIsocenter(Name=iso_name, Position={'x':roi_center.x, 'y':roi_center.y, 'z':new_isoZ})
            
            
        def move_iso_if_couch_corner_47():
            ##check iso to most contra lat side distance is <=47cm and move AP RL until ok
            #ISO POINT define coordinates
            iso_z = beam_set.Beams[0].Isocenter.Position.z  
            iso_x = beam_set.Beams[0].Isocenter.Position.x   
            iso_y = beam_set.Beams[0].Isocenter.Position.y  


            ##couch bounding box and coordinate most lateral
            ##need to add poi at most lateral part of couch on isocenter slice
            ss = case.PatientModel.StructureSets[examination.Name]

            Couch_roi_box = ss.RoiGeometries['Couch Top'].GetBoundingBox()

            if plan.Name =='L_Breast_Initial':
                x_max = Couch_roi_box[0].x   ##most contralat position for left breast
            elif plan.Name =='R_Breast_Initial':
                x_max = Couch_roi_box[1].x   ##most contralat position for left breast

            y_max = Couch_roi_box[0].y   ##most ant of couch, we then plus 1cm to get it to corner

            #create the couch corner point using sup inf iso value, most lat x value couch and then get most ant couch value
            #case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': x_max, 'y': y_max + 1, 'z': iso_z }, Name=r"Couch corner", Color="Yellow", VisualizationDiameter=1, Type="Undefined")


            ##calc distance between couch corner and iso to ensure <47cm
            couch_dist = ((iso_x - x_max)**2 + (iso_y - y_max - 1)**2 + (iso_z - iso_z)**2)**0.5
            couch_distf = round(couch_dist, 1)  #e.g 48.5cm

            #loop to move iso AP RL 1cm until <47cm
            while couch_distf > 47:
                if plan.Name =='L_Breast_Initial':
                    beam_set.Beams[0].Isocenter.EditIsocenter(Name=iso_name, Position={'x':iso_x - 1, 'y':iso_y + 1, 'z':iso_z}) # move contralat and post for left breast
                    beam_set.Beams[1].Isocenter.EditIsocenter(Name=iso_name, Position={'x':iso_x - 1, 'y':iso_y + 1, 'z':iso_z}) # move contralat and post for left breast
                    
                if plan.Name =='R_Breast_Initial':
                    beam_set.Beams[0].Isocenter.EditIsocenter(Name=iso_name, Position={'x':iso_x + 1, 'y':iso_y + 1, 'z':iso_z}) # move contralat and post for left breast
                    beam_set.Beams[1].Isocenter.EditIsocenter(Name=iso_name, Position={'x':iso_x + 1, 'y':iso_y + 1, 'z':iso_z}) # move contralat and post for left breast
                
                iso_z = beam_set.Beams[0].Isocenter.Position.z  #this refreshes iso position each loop so knows current one
                iso_x = beam_set.Beams[0].Isocenter.Position.x   
                iso_y = beam_set.Beams[0].Isocenter.Position.y 
                
                couch_dist = ((iso_x - x_max)**2 + (iso_y - y_max - 1)**2 + (iso_z - iso_z)**2)**0.5  #refresh distance 
                couch_distf = round(couch_dist, 1)  #refresh this new value after any iso moves
                if 0 <= couch_distf <= 47:
                    break    
                    
        move_iso_if_couch_corner_47()
        
        ##if zzPlanning Bolus Full VMAT in list then add material water to it and assign to beam
        #add bolus beams if required
        rois = case.PatientModel.RegionsOfInterest 

        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
                
        if 'zzPlanning Bolus Full VMAT' in roi_list:
            tpm = db.LoadTemplatePatientModel(templateName = 'zzWater density', lockMode = 'Read')
            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName='CT 1', SourceRoiNames=["zzWater density"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")
            case.PatientModel.RegionsOfInterest['zzPlanning Bolus Full VMAT'].SetRoiMaterial(Material=case.PatientModel.Materials[1])  ##index now 1 as couch cork is [0]
            for Beams in beam_set.Beams:  ##add to beams
                Beams.SetBolus(BolusName=r"zzPlanning Bolus Full VMAT")
                
        ##delete the water density roi now as not needed - will be there only if bolus still here
        if 'zzPlanning Bolus Full VMAT' in roi_list:
            case.PatientModel.RegionsOfInterest['zzWater density'].DeleteRoi()

        #default dose grid set
        beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
        beam_set.FractionDose.UpdateDoseGridStructures()
        
        ###BRING PLANNER TO PLAN OPT TAB and 2d view on to see slice############

        ui.TitleBar.Navigation.MenuItem['Plan optimization'].Button_Plan_optimization.Click() #go to plan opt
        ui.Workspace.TabControl['2D | Image'].TabItem['2D | Image'].Select()
        ui.Workspace.TabControl['DVH'].TabItem['Clinical goals'].Select()
        ui.Workspace.TabControl['Objectives/constraints'].TabItem['Objectives/constraints'].Select()
        ############################################

        #opt settings
        #optimisation settings
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1e-7
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 50
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 7
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeIntermediateDose = False
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True
        
        ##clinical goals - load template based on what planner selected at start in drop down option
        tpmCG = db.LoadTemplateClinicalGoals(templateName = clicked4.get(),lockMode = 'Read')
        plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=tpmCG)

        #opt functions add   

        with CompositeAction('Add optimization function'):

            retval_0 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"Breast_Contra", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

            plan.PlanOptimizations[0].Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = 250

            # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_1 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"Lung_Contra", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[1].DoseFunctionParameters.DoseLevel = 90

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_2 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDvh", RoiName=r"Lung_Contra", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[2].DoseFunctionParameters.DoseLevel = 250

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[2].DoseFunctionParameters.PercentVolume = 1
          
          plan.PlanOptimizations[0].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight = 1.5

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_3 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"Heart", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[3].DoseFunctionParameters.DoseLevel = 300

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_4 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDvh", RoiName=r"Heart", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[4].DoseFunctionParameters.DoseLevel = 1300

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[4].DoseFunctionParameters.PercentVolume = 1

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_5 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDvh", RoiName=r"Lung_Ipsi", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[5].DoseFunctionParameters.DoseLevel = 1700

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[5].DoseFunctionParameters.PercentVolume = 25

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[5].DoseFunctionParameters.Weight = 7

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_6 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"Lung_Ipsi", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[6].DoseFunctionParameters.DoseLevel = 1150
          
          plan.PlanOptimizations[0].Objective.ConstituentFunctions[6].DoseFunctionParameters.Weight = 1.5

          # CompositeAction ends 
          


        
        if SIB_plan == 'No':
            with CompositeAction('Add optimization function'):

                retval_0 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVp_4000", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[7].DoseFunctionParameters.DoseLevel = 3990

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[7].DoseFunctionParameters.Weight = 55

                # CompositeAction ends 


            with CompositeAction('Add optimization function'):

                  retval_1 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVp_4000", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[8].DoseFunctionParameters.DoseLevel = 4010

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[8].DoseFunctionParameters.Weight = 10

                  # CompositeAction ends 


            with CompositeAction('Add optimization function'):

                  retval_2 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVp_4000", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[9].DoseFunctionParameters.DoseLevel = 4000

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[9].DoseFunctionParameters.Weight = 40

                  # CompositeAction ends 
        
        
        if SIB_plan == 'Yes':
            with CompositeAction('Add optimization function'):

                retval_0 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVp_4000-PTVp_4800_DVH", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[7].DoseFunctionParameters.DoseLevel = 3990

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[7].DoseFunctionParameters.Weight = 65

                # CompositeAction ends 


            with CompositeAction('Add optimization function'):

                  retval_1 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVp_4000-PTVp_4800_DVH", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[8].DoseFunctionParameters.DoseLevel = 4400

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[8].DoseFunctionParameters.Weight = 10

                  # CompositeAction ends 


            with CompositeAction('Add optimization function'):

                  retval_2 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVp_4000-PTVp_4800_DVH", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[9].DoseFunctionParameters.DoseLevel = 4000

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[9].DoseFunctionParameters.Weight = 0.1

                  # CompositeAction ends 
        
        
        
        

        with CompositeAction('Add optimization function'):

          retval_10 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName=r"Skin", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[10].DoseFunctionParameters.HighDoseLevel = 4000

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[10].DoseFunctionParameters.LowDoseLevel = 3800

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[10].DoseFunctionParameters.LowDoseDistance = 0.5

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[10].DoseFunctionParameters.Weight = 5

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_11 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName=r"Skin", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[11].DoseFunctionParameters.HighDoseLevel = 4000

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[11].DoseFunctionParameters.LowDoseLevel = 2000

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[11].DoseFunctionParameters.Weight = 5

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_12 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName=r"Skin", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[12].DoseFunctionParameters.HighDoseLevel = 2400

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[12].DoseFunctionParameters.LowDoseLevel = 500

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[12].DoseFunctionParameters.LowDoseDistance = 5

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[12].DoseFunctionParameters.Weight = 5

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_13 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"Skin-PTVAndAx", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[13].DoseFunctionParameters.DoseLevel = 3800

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[13].DoseFunctionParameters.PercentVolume = 25
          
          plan.PlanOptimizations[0].Objective.ConstituentFunctions[13].DoseFunctionParameters.Weight = 8

          # CompositeAction ends 

        
        with CompositeAction('Add optimization function'):

          retval_15 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRing_AllPTV", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[14].DoseFunctionParameters.DoseLevel = 3800

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[14].DoseFunctionParameters.PercentVolume = 25

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[14].DoseFunctionParameters.Weight = 12

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_16 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"zzRing_AllPTV", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[15].DoseFunctionParameters.DoseLevel = 3000

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_17 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRVR", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[16].DoseFunctionParameters.DoseLevel = 3000

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[16].DoseFunctionParameters.PercentVolume = 25
          
          plan.PlanOptimizations[0].Objective.ConstituentFunctions[16].DoseFunctionParameters.Weight = 80    #newly added 21/2/2023 based on testing few plans and splash laterally 

          # CompositeAction ends 
          
        ##need to get next index value to add opt function as some may be added and some wont be so wont know exact index.
        new_index = len(plan.PlanOptimizations[0].Objective.ConstituentFunctions)

        if 'zzArm_BLOCK' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_14 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzArm_BLOCK", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 1000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L1' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_7 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVn_LN_Ax_L1", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 3990

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 30

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L1' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_8 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVn_LN_Ax_L1", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4010

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L1' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVn_LN_Ax_L1", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 
              

        if 'PTVn_LN_Ax_L2' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_7 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVn_LN_Ax_L2", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 3990

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 30

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L2' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_8 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVn_LN_Ax_L2", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4010

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L2' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVn_LN_Ax_L2", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 
              
              
              

        if 'PTVn_LN_Ax_L3' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_7 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVn_LN_Ax_L3", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 3990

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 30

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L3' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_8 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVn_LN_Ax_L3", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4010

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L3' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVn_LN_Ax_L3", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends
              
              
           
        if 'PTVn_LN_Ax_L4' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_7 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVn_LN_Ax_L4", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 3990

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 30

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L4' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_8 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVn_LN_Ax_L4", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4010

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 

        if 'PTVn_LN_Ax_L4' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVn_LN_Ax_L4", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends
              
              
              
              
        if 'PTVn_LN_Interpect' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_7 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVn_LN_Interpect", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 3990

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 30

              # CompositeAction ends 

        if 'PTVn_LN_Interpect' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_8 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVn_LN_Interpect", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4010

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 

        if 'PTVn_LN_Interpect' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVn_LN_Interpect", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends
              
      
        if 'PTVn_LN_IMN' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_7 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVn_LN_IMN", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 3990

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 30

              # CompositeAction ends 

        if 'PTVn_LN_IMN' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_8 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVn_LN_IMN", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4010

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends 

        if 'PTVn_LN_IMN' in roi_list:
            with CompositeAction('Add optimization function'):

              retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVn_LN_IMN", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

              plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10

              # CompositeAction ends
              
        if 'Oesophagus' in roi_list:
            if roi_structures["Oesophagus"].HasContours() is True:
                with CompositeAction('Add optimization function'):
                    retval_0 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"Oesophagus", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)
                    plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 1090
                    # CompositeAction ends
                    
        if 'Oesophagus' in roi_list:
            if roi_structures["Oesophagus"].HasContours() is True:
                with CompositeAction('Add optimization function'):
                    retval_1 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDvh", RoiName=r"Oesophagus", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)
                    plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 1700
                    plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 14
                    # CompositeAction ends
                
        
        if SIB_plan == 'Yes':
            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVp_4800_DVH", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4800

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 5

            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVp_4800_DVH", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4800

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10
                
            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVp_4800_DVH", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4800

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10
                
            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRing1_SIB", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4560

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10
                
            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRing2_SIB", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4200

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 10
                
            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVp_4000-PTVp_4800_DVH+1cm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4200

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 20
                
            with CompositeAction('Add optimization function'):

                  retval_2 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDvh", RoiName=r"PTVp_4000-PTVp_4800_DVH+1cm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4100

                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 1
                  
                  plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 20
                  
            with CompositeAction('Add optimization function'):

                retval_9 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVp_4000-PTVp_4800_DVH+1cm", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.DoseLevel = 4000

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.PercentVolume = 25

                plan.PlanOptimizations[0].Objective.ConstituentFunctions[new_index].DoseFunctionParameters.Weight = 20
            



        ###LOOPS THROUGH TO ADD THE WEIGHTS AND DOSE VALUES TO THOSE OPT FUNCTIONS ADDED WITH new_index as above doesnt load these values for some reason?
        
        constituent_functions = [cf for cf in plan.PlanOptimizations[0].Objective.ConstituentFunctions ]
        for index,cf in enumerate(constituent_functions):
            
            func_type = ""
            roi_Name = cf.ForRegionOfInterest.Name
            roi_list = ['PTVn_LN_IMN','PTVn_LN_Ax_L1','PTVn_LN_Ax_L2','PTVn_LN_Ax_L3','PTVn_LN_Ax_L4','PTVn_LN_Interpect']
            roilist_sib = ['PTVp_4800_DVH']
            roi_sibring1 = ['zzRing1_SIB']
            roi_sibring2 = ['zzRing2_SIB']
            roiptvwb_sib = ['PTVp_4000-PTVp_4800_DVH+1cm']
            
            roi_list2 = ['zzArm_BLOCK']
            roi_list3 = ['Oesophagus']
            
            func_type1 = ['MinDose']
            func_type2 = ['MaxDose']
            func_type3 = ['UniformDose']
            func_type4 = ['MaxEud']
            func_type5 = ['MaxDvh']
            if hasattr( cf.DoseFunctionParameters, 'FunctionType' ):
                func_type = cf.DoseFunctionParameters.FunctionType  
            if func_type in func_type1 and roi_Name in roi_list:  ##sort min dose ptvnodes
                cf.DoseFunctionParameters.Weight = 30
                cf.DoseFunctionParameters.DoseLevel = 3990
            if func_type in func_type2 and roi_Name in roi_list:  ##sort max dose ptvnodes
                cf.DoseFunctionParameters.Weight = 15
                cf.DoseFunctionParameters.DoseLevel = 4010
            if func_type in func_type3 and roi_Name in roi_list:  ##sort uniform dose ptv nodes
                cf.DoseFunctionParameters.Weight = 10
                cf.DoseFunctionParameters.DoseLevel = 4000
                
                
            if func_type in func_type2 and roi_Name in roi_list2:  ##sort max dose arm
                cf.DoseFunctionParameters.Weight = 1
                cf.DoseFunctionParameters.DoseLevel = 1000
            if func_type in func_type4 and roi_Name in roi_list3:  ##sort oesoph eud
                cf.DoseFunctionParameters.Weight = 1
                cf.DoseFunctionParameters.DoseLevel = 1090
            if func_type in func_type5 and roi_Name in roi_list3:  ##sort oesoph max dvh
                cf.DoseFunctionParameters.Weight = 1
                cf.DoseFunctionParameters.DoseLevel = 1700
                cf.DoseFunctionParameters.PercentVolume = 14
               
            #sib rois opt functions    
            if func_type in func_type1 and roi_Name in roilist_sib:  ##sort sib ptv min dose
                cf.DoseFunctionParameters.Weight = 10
                cf.DoseFunctionParameters.DoseLevel = 4790
            if func_type in func_type2 and roi_Name in roilist_sib:  ##sort sib ptv max dose
                cf.DoseFunctionParameters.Weight = 10
                cf.DoseFunctionParameters.DoseLevel = 4810
            if func_type in func_type3 and roi_Name in roilist_sib:  ##sort sib ptv max dose
                cf.DoseFunctionParameters.Weight = 5
                cf.DoseFunctionParameters.DoseLevel = 4800   #sib uniform
                
            if func_type in func_type2 and roi_Name in roi_sibring1:  ##sort sib ptv ring1 max dose
                cf.DoseFunctionParameters.Weight = 10
                cf.DoseFunctionParameters.DoseLevel = 4560
            if func_type in func_type2 and roi_Name in roi_sibring2:  ##sort sib ptv ring1 max dose
                cf.DoseFunctionParameters.Weight = 10
                cf.DoseFunctionParameters.DoseLevel = 4200
                
                
            if func_type in func_type2 and roi_Name in roiptvwb_sib:  ##sort sib ptvwb40-tb+1cm max
                cf.DoseFunctionParameters.Weight = 20
                cf.DoseFunctionParameters.DoseLevel = 4200             
            if func_type in func_type5 and roi_Name in roiptvwb_sib:  ##sort sib ptvwb40-tb+1cm max dvh
                cf.DoseFunctionParameters.Weight = 20
                cf.DoseFunctionParameters.DoseLevel = 4100
                cf.DoseFunctionParameters.PercentVolume = 1
            if func_type in func_type3 and roi_Name in roiptvwb_sib:  ##sort sib ptvwb40-tb+1cm uniform
                cf.DoseFunctionParameters.Weight = 20
                cf.DoseFunctionParameters.DoseLevel = 4000
                
               

        #set the isodose colour template # Load the isodose-template with the name "template_name" and prescribed dose "dose" as 100%
        if SIB_plan == 'No':
            tpm = "Lung 55/20#"
            dose = 4000
        if SIB_plan == 'Yes':
            tpm = "Breast_SIB"
            dose = 4800
            
        template_colormap = db.LoadTemplateColorMap(templateName = str(tpm))

        case.CaseSettings.DoseColorMap.AuxiliaryUnit = template_colormap.ColorMap.AuxiliaryUnit

        case.CaseSettings.DoseColorMap.ColorMapReferenceType = template_colormap.ColorMap.ColorMapReferenceType

        case.CaseSettings.DoseColorMap.ColorTable = template_colormap.ColorMap.ColorTable

        case.CaseSettings.DoseColorMap.IsDiscrete = template_colormap.ColorMap.IsDiscrete

        case.CaseSettings.DoseColorMap.IsHighValuesClipped = template_colormap.ColorMap.IsHighValuesClipped

        case.CaseSettings.DoseColorMap.IsLowValuesClipped = template_colormap.ColorMap.IsLowValuesClipped

        case.CaseSettings.DoseColorMap.PresentationType = template_colormap.ColorMap.PresentationType        

        case.CaseSettings.DoseColorMap.ReferenceValue = dose


        # All names of isodose-templates can be found by the following command:

        colormap_templates_all = db.GetColorMapTemplateInfo()
            
        #start opt round1
        plan.PlanOptimizations[0].RunOptimization()
        patient.Save()

        ##opt again round 2 -try incase crashes when tries to auto scale?
        try:
            beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)
        except:
            pass
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=False)
        plan.PlanOptimizations[0].RunOptimization()
        try:
            beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)
        except:
            pass

        ##########################################################################################################################################################

        ##TURN OFF ROIS APART FROM PTV
        for roi in rois:
            patient.SetRoiVisibility(RoiName=roi.Name, IsVisible=False)
        
        patient.SetRoiVisibility(RoiName='PTVp_4000', IsVisible=True)
        patient.SetRoiVisibility(RoiName='PTVn_LN_Combined', IsVisible=True)
        
        if SIB_plan == 'Yes':
            patient.SetRoiVisibility(RoiName='PTVp_4800_DVH', IsVisible=True)
        #sort vmat beam name
        if clicked.get() == "Course 1":
            beam_set.Beams[0].Name = r"EA01"
            beam_set.Beams['EA01'].Description = r"EA01 VMAT"
            beam_set.Beams[1].Name = r"EA02"
            beam_set.Beams['EA02'].Description = r"EA02 VMAT"
        if clicked.get() == "Course 2":
            beam_set.Beams[0].Name = r"EB01"
            beam_set.Beams['EB01'].Description = r"EB01 VMAT"
            beam_set.Beams[1].Name = r"EB02"
            beam_set.Beams['EB02'].Description = r"EB02 VMAT"
        if clicked.get() == "Course 3":
            beam_set.Beams[0].Name = r"EC01"
            beam_set.Beams['EC01'].Description = r"EC01 VMAT"
            beam_set.Beams[1].Name = r"EC02"
            beam_set.Beams['EC02'].Description = r"EC02 VMAT"
                                   
        
        #get planner initials and add to plan
        patient.Save()  ##this now populates the user name below
        planner = patient.ModificationInfo.UserName  
        case.TreatmentPlans[plan.Name].PlannedBy = str(planner)
        
        ###################print on screen FSDs #########################################################################################

        #access set up point coordinates 
        pois = case.PatientModel.PointsOfInterest
        # Get POI geometries 
        poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries

        #for item in poi_list:       
        center_y = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.y    #6.9 this is AP point
           
        #access med tattoo coordinates
        MTcenter_y = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.y #-13.23  this is AP point

        #ANT FSD AT TATTOOS
        DIFF = MTcenter_y - center_y
        ANT_FSDATTATTOOS = 100 - abs(DIFF)  
        ANT_FSDATTATTOOS1 = round(ANT_FSDATTATTOOS,1)  #tested in console works ANT FSD AT TATTOOS ROUNDED 1DP

        #ANT FSD AT ISO. Get iso height location coordinates
        iso_y = beam_set.Beams[0].Isocenter.Position.y

        DIFF2 = MTcenter_y - iso_y

        SET_ANTFSD = 100 - abs(DIFF2)  
        SET_ANTFSD1 = round(SET_ANTFSD,1)  #tested console works SET ANT FSD. ROUNDED TO 1DP

        ##SHOW R/L AND SUP/INF SHIFTS. shifts = ref point coordinate minus iso coordinate
        iso_x = beam_set.Beams[0].Isocenter.Position.x
        iso_y = beam_set.Beams[0].Isocenter.Position.y
        iso_z = beam_set.Beams[0].Isocenter.Position.z
        
        RL_shift = round(center_x - iso_x, 1)
        SI_shift = round(center_z - iso_z, 1)
        AP_shift = round(center_y - iso_y, 1)

        if RL_shift <= 0:
            RL_direction = 'Left'
        if RL_shift > 0:
            RL_direction = 'Right'
            
        if SI_shift <= 0:
            SI_direction = 'Superior'
        if SI_shift > 0:
            SI_direction = 'Inferior'
            
        if AP_shift <= 0:
            AP_direction = 'Posterior'
        if AP_shift > 0:
            AP_direction = 'Anterior'

        ##absolute shifts without plus minus signs eg 0.3 sup or 14.5 left not -14.5 left
        absRL_SHIFT = abs(RL_shift)
        absSI_SHIFT = abs(SI_shift)

        #####log info text log###
        try:
            import datetime
            filepath = r'\\Client\J$\PLANNING\Auto Breast log'
            ##filepath = r'\\Client\U$\Ian Gleeson\RAYSTATION\SCRIPTING\SCRIPTS\IG TESTS SCRIPTS RADNET\AUTO 2FIELD BREAST 26Gy 5#\IG AUTO PLAN\partial breast\SIB BITS\PLUS VMAT NODES\SISO BITS\final\WB_PB_FOR_SUBMISSION\v5\v6\log'
            os.chdir(filepath)
            #cg lists total
            total_CGs = len(plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions)
            CGs_stats = []
            #add cgs to list
            for i in range(0,total_CGs):
                CGs_stats.append(plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[i].GetClinicalGoalValue())
                
                #add roi names and goals and types etc to lists
            roi_namestats = []
            roi_goaltype = []
            roi_goals = []

            for i in range(0,total_CGs):
                roi_namestats.append(plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[i].ForRegionOfInterest.Name)
                roi_goaltype.append(plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[i].PlanningGoal.Type)
                roi_goals.append(plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[i].PlanningGoal.ParameterValue)
                
            #time,plan,case
            endTime = datetime.datetime.now()
            caseName =case.CaseName
            planName = plan.Name
            
            #username
            from System import Environment
            staff_id = Environment.UserName
            
            ##write to file to record patient number that script ran to end ok
            MyFileName = patient.PatientID + '_VMAT_' + staff_id + '.txt'
            file = open(MyFileName, "w") # write mode over writes
            file.write("VMAT Script ran - start time: " + str(startTime)
            + "\n" + "END TIME: " + str(endTime)
            + "\n" + "MRN: " + patient.PatientID
            + "\n" + "Case: " + str(caseName) 
            + "\n" + "Plan: " + str(planName)
            + "\n" + "Staff: " + str(staff_id)
            + "\n" + "Roi Names: " + str(roi_namestats)
            + "\n" + "Goal Type: " + str(roi_goaltype)
            + "\n" + "Roi Goal: " + str(roi_goals)
            + "\n" + "CGs: " + str(CGs_stats))
                    
            #write things to py file
            file.close
            file.flush()  ##flushes write to file quicker as may be problems later on if variables not there when we need them
            os.fsync(file.fileno())   ##speeds up writing to file.
        except:
            messagebox.showinfo('Auto Plan Breast v' + str(script_version), 'log file not created - inform scripting of this instance')
            
            
        ##window at end to show the FSDs?
        window = Tk()
        window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
        window.withdraw()

        messagebox.showinfo('Auto Plan Breast v' + str(script_version), 'Script complete. Please review the plan and optimise more if needed' + "\n" + "\n" + "ANT FSD AT TATTOOS" + ": " + str(ANT_FSDATTATTOOS1) + "cm" + "\n" + "\n" + "SET ANT FSD" + ": " + str(SET_ANTFSD1) + "cm" + "\n" + "\n" + "Move iso" + ": " + str(absSI_SHIFT) + "cm" + ": " + str(SI_direction) + "\n" + "\n" + "Move iso" + ": " + str(absRL_SHIFT) + "cm" + ": " + str(RL_direction))

        window.deiconify()
        window.destroy()
        window.quit()
        
        top.destroy()
       
    ###########################################################
    def Button_pressed2():
        top.destroy()

    #drop down box to pick mosaiq course
    clicked = StringVar()
    clicked.set("Select MOSAIQ Course")
    drop = OptionMenu(top, clicked, "Course 1", "Course 2", "Course 3" )
    #drop.pack()
    drop.place(x=10, y=50)

    #drop down box to pick machine
    clicked2 = StringVar()
    clicked2.set("Select Machine")
    drop2 = OptionMenu(top, clicked2, "Agility")
    #drop2.pack()
    drop2.place(x=310, y=50)

    #drop down box to pick clinical goal template
    db = get_current("PatientDB")
    CGs_list = []
    #only see those with Breast in Name and is approved
    for CGs in db.GetClinicalGoalTemplateInfo():
        if "Breast" in (CGs["Name"]) or "breast" in (CGs["Name"]) or "PARABLE" in (CGs["Name"]) :
            if "40" in (CGs["Name"]) or "48" in (CGs["Name"]):
                if (CGs["IsApproved"] == True):
                    CGs_list.append(CGs["Name"])
                
    clicked4 = StringVar()
    clicked4.set("Select Clinical Goal Template")

    drop4 = OptionMenu(top, clicked4, *CGs_list)
    drop4.place(x=550, y=50)

    ##button for VMAT nodes
    myButton4 = Button(top, text="Start VMAT BREAST NODES 40Gy or 48Gy /15F", command=autoVMAT)

    ##cancel button
    butt2 = Button(top, text = 'Cancel', command = Button_pressed2)

    myButton4.place(x=150, y=150)

    butt2.place(x=500, y=150)

    top.mainloop()