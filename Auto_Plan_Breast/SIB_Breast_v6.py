'''
TITLE: 'Auto Plan Breast'
AUTHOR: Ian Gleeson
PURPOSE: Auto plan breasts 26/5 tangents, 48/15 sibs, vmat nodes 40/15
REQUIREMENTS: CPython 3.8 64-bit interpreter
TPS VERSION: 12A
HISTORY: v6.0.0 - logging plan stats to text files, reversed laterality names rois
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

def autoplanSIB():
    startTime = datetime.datetime.now()
    script_version = '6.0.0'
    script_name = 'Auto Plan Breast'
    #written by Ian Gleeson
    #runs in CPython 3.6 64bit ## now use 3.6 cPython for use tkinter
    #Raystattion 10A
    #Summer 2021
    ###########next buttons to select course and then autoplan
    top = Toplevel()
    top.title("Auto Plan Breast v" + str(script_version))
    mycolour = '#%02x%02x%02x' % (50, 50, 50)
    myorange = '#%02x%02x%02x' % (255, 140, 0)
    top.configure(background = mycolour)
    top.geometry("760x240")
    ######add label#######################
    lbl1 = Label(top, text='Ensure you have loaded the checkers approved medial field plan. Select the course, machine and clinical goals and then click Start')
    lbl1.place(x=65, y =5)
    lbl1.configure(background = mycolour, fg = "white", justify=CENTER)


    def autoplanSIB1():
        #get current case, patient and examination
        db = get_current("PatientDB")

        try:
            patient = get_current("Patient")
        except:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No patient loaded. Please open a patient")
            exit()

        try:
            case = get_current("Case")
        except:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No case loaded. Please open a case")
            exit()
        try:
            examination = get_current("Examination")
            print (examination.Name)
        except:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No examination loaded. Please open an examination")
            exit()

        try:
            plan = get_current("Plan")
        except:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No plan loaded. Please open a plan")
            exit()    

        try:
            beam_set = get_current("BeamSet")
        except:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No Beamset loaded. Please open a Beamset")
            exit()
        
         ##flag if dont select course, machine or breathing
        if clicked.get() == 'Select MOSAIQ Course':
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Please Select MOSAIQ Course")
            exit()
            
        if clicked2.get() == 'Select Machine':
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Please Select Machine")
            exit() 
        
        
        ##flags those wanting to plan on Varian and y jaws >11cm for whole breast
        if clicked2.get() == 'TrueBeamSTx':
            if len(beam_set.Beams[0].Segments) == 1:
                if beam_set.Beams[0].Segments[0].JawPositions[2] < -11:  #y1 always minus number
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Y1 Jaw > 11cm so plan on Elekta")
                    exit()
                if beam_set.Beams[0].Segments[0].JawPositions[3] > 11:  #y2 positive number
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Y2 Jaw > 11cm so plan on Elekta")
                    exit()
            if len(beam_set.Beams[0].Segments) == 0:
                if beam_set.Beams[0].InitialJawPositions[2] < -11:  #y1 always minus number
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Y1 Jaw > 11cm so plan on Elekta")
                    exit()
                if beam_set.Beams[0].InitialJawPositions[3] > 11:  #y2 always positive number
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Y2 Jaw > 11cm so plan on Elekta")
                    exit()
         
         
         
        ###error if more than one field at start########
        if len(beam_set.Beams) >1:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Only one Medial field should exist when starting")
            exit()
            
        ####error if tech if NOT 3dcrt at start#########
        if beam_set.PlanGenerationTechnique != 'Conformal':
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Technique must be 3DCRT when starting")
            exit()
            
        ##error if more than one beamset at start#########
        if len(plan.BeamSets) >1:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Only one Beamset should exist when starting")
            exit()
        


        #gives error if not HFS and then exits when user hits ok. runs with C python but text errors with iron python cant see all letters
        if examination.PatientPosition != 'HFS':
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Script only for HFS!")
            exit() 


        #any plan in case cannot be called 'Left Breast' or 'Right Breast' as thats what the copy plan can be called later

        if beam_set.Beams[0].Isocenter.Position.x > 0:
            for p in case.TreatmentPlans:
                if p.Name in ['Left Breast']:
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No Plan Name in Case can be called 'Left Breast'")
                    exit()
                    
        if beam_set.Beams[0].Isocenter.Position.x < 0:
            for p in case.TreatmentPlans:
                if p.Name in ['Right Breast']:
                    root = Tk()
                    root.withdraw()
                    messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No Plan Name in Case can be called 'Right Breast'")
                    exit()


        #checks if roi Skin exits. if not, gives a error messege
        rois = case.PatientModel.RegionsOfInterest 

        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
            
        if 'Skin' not in roi_list:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No ROI called 'Skin' found!")
            exit()
        
        if 'CTVp_4800' not in roi_list:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No ROI called 'CTVp_4800' found!")
            exit()
            
        if 'Heart' not in roi_list:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No ROI called 'Heart' found!")
            exit()
            
        #access roi structures    
        roi_structures = case.PatientModel.StructureSets[examination.Name].RoiGeometries
        
        if 'CTVp_4800' in roi_list:
            if roi_structures["CTVp_4800"].HasContours() is False:
                root = Tk()
                root.withdraw()
                messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "ROI 'CTVp_4800' needs outlining first!")
                exit()
                
        if 'Heart' in roi_list:
            if roi_structures["Heart"].HasContours() is False:
                root = Tk()
                root.withdraw()
                messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "ROI 'Heart' needs outlining first!")
                exit()
           
            
        #get beams isocenter position for laterality labelling

        if beam_set.Beams[0].Isocenter.Position.x > 0:
            NewPlan_Name = 'Left Breast'
        elif beam_set.Beams[0].Isocenter.Position.x < 0:
            NewPlan_Name = 'Right Breast'

        plan = case.TreatmentPlans[plan.Name]        
        #copy plan and rename it to new plan name and beamset and set as current
        case.CopyPlan(PlanName=plan.Name, NewPlanName=NewPlan_Name, KeepBeamSetNames=False)

        patient.Save()

        plan = case.TreatmentPlans[NewPlan_Name]
        plan.SetCurrent()
        
        ##if elekta and med beam has MLC, then check virtual x jaw post border and check post border mlcs are not >1mm from each other - if they are, then move virtual post x jaw to match most post mlc
        #tested 09/11/22 IG on right and left case. to be put at start of WB/SIB/PB script once plan named and approved field copied prior to machine change functions
        #ensures virtual jaws align with mlc where needed so later if we "conform mlc" to field that it will conform correctly to new virtual jaw and not an original one (whih may not be aligned with mlc)
        def checkElektaVirtualJaw():
            beam_set = get_current("BeamSet")
            if beam_set.MachineReference.MachineName == 'Agility':
                if len(beam_set.Beams[0].Segments) == 1:
                    mlc_list = []
                    
                    for beam in beam_set.Beams:
                        for segment in beam.Segments:
                            if plan.Name == 'Left Breast':
                                leaf_positions = segment.LeafPositions[0]
                                post_jaw = beam_set.Beams[0].Segments[0].JawPositions[0]
                                
                            if plan.Name == 'Right Breast':
                                leaf_positions = segment.LeafPositions[1]
                                post_jaw = beam_set.Beams[0].Segments[0].JawPositions[1]
                                
                            for i in range(30, 46):
                                mlc_list.append(leaf_positions[i]) 
                                
                    #get difference between most post mlc and virtual jaw   #left vjaw is -4.0, min left mlc is -3.21 so dif is asbsolute 0.788
                    diff_jawmlc = abs(min(mlc_list) - post_jaw)

                    if diff_jawmlc > 0.1:
                        for beam in beam_set.Beams:
                            if plan.Name == 'Left Breast':
                                segments = beam.Segments[0]
                                jaw = segments.JawPositions
                                #moves post virtual jaw x1 to smallest post mlc
                                jaw[0] = min(mlc_list)  
                                segments.JawPositions = jaw
                                
                            if plan.Name == 'Right Breast':
                                segments = beam.Segments[0]
                                jaw = segments.JawPositions
                                #moves post virtual jaw x2 to smallest post mlc
                                jaw[1] = min(mlc_list)  
                                segments.JawPositions = jaw

        checkElektaVirtualJaw()                                
                                 
        #################################################MACHINE CHANGE BITS########################
        #####################################machine CHANGE WITH NO MLC AT START##############################
            
        def changeMachine_NoMLC():
            #conforms mlc to field in no mlc
            ##set leaf positioning outside and conform mlc
            beam_set = get_current("BeamSet")
            if len(beam_set.Beams[0].Segments) == 0:
                beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0) #sets treat protect outside so no mlc comes inside edge at top and bottom
                beam_set.TreatAndProtect()


            #Beamseto old parameters
            beam = plan.BeamSets[0].Beams
            beamset = plan.BeamSets[0]
            for beam in beamset.Beams:
                segments = beam.Segments[0]
                old_jaw = segments.JawPositions

                old_x1 = old_jaw[0]
                old_x2 = old_jaw[1]
                old_y1 = old_jaw[2]
                old_y2 = old_jaw[3]

                old_gantry = beam.GantryAngle
                old_collimator = beam.InitialCollimatorAngle
                old_beamName = beam.Name
                old_beamDescription = beam.Description
                old_isoName = beam.Isocenter.Annotation.Name
                iso_x = beam.Isocenter.Position.x
                iso_y = beam.Isocenter.Position.y
                iso_z = beam.Isocenter.Position.z
                iso_colour = beam.Isocenter.Annotation.DisplayColor
                old_rotation = beam.CouchRotationAngle
                old_pitch = beam.CouchPitchAngle
                old_roll = beam.CouchRollAngle

            #create a copy new beamset 3DCRT and 5#s and NEW machine
            if beamset.MachineReference.MachineName == 'Agility':
                plan.AddNewBeamSet(Name='copy1', ExaminationName=examination.Name, MachineName='TrueBeamSTx', Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=5, CreateSetupBeams=False, Comment="")
            if beamset.MachineReference.MachineName == 'TrueBeamSTx':
                plan.AddNewBeamSet(Name='copy1', ExaminationName=examination.Name, MachineName='Agility', Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=5, CreateSetupBeams=False, Comment="")
                
            #need to set new beamset as current. need to save before change
            patient.Save()
            beam_set = plan.BeamSets[1]
            beam_set.SetCurrent()


            ##create new beam
            beam_set.CreatePhotonBeam(BeamQualityId=r"6", IsocenterData={ 'Position': { 'x': iso_x, 'y': iso_y, 'z': iso_z }, 'NameOfIsocenterToRef': plan.Name, 'Name': plan.Name, 'Color': iso_colour }, Name=old_beamName, Description=old_beamDescription, GantryAngle=round(old_gantry), CouchRotationAngle=old_rotation, CouchPitchAngle=old_pitch, CouchRollAngle=old_roll, CollimatorAngle=round(old_collimator))

            ##need to conform mlc to 5 x 5 field first so i can change the jaws
            beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0) #sets treat protect outside so no mlc comes inside edge at top and bottom
            beam_set.TreatAndProtect()

            ##change jaws to old jaws
            for beam in beam_set.Beams:
                segments = beam.Segments[0]
                jaw = segments.JawPositions
                jaw[0] = old_x1   
                jaw[1] = old_x2
                jaw[2] = old_y1
                jaw[3] = old_y2
                segments.JawPositions = jaw

            ##re conform mlc to new jaws now
            beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0)
            beam_set.TreatAndProtect()

            ##delete old beamset
            patient.Save()
            beam_set = plan.BeamSets[0]
            beam_set.SetCurrent()
            beam_set.DeleteBeamSet()
            patient.Save()
            beam_set = get_current("BeamSet")
        
        ########################CHANGE MACHINE THAT HAS MLC AT START - WORKS BOTH ELEKTA AND VARIAN########

        def changeMachine_MLC():
            #Beamseto old parameters
            beam = plan.BeamSets[0].Beams
            beamset = plan.BeamSets[0]
            for beam in beamset.Beams:
                segments = beam.Segments[0]
                old_jaw = segments.JawPositions

                old_x1 = old_jaw[0]
                old_x2 = old_jaw[1]
                old_y1 = old_jaw[2]
                old_y2 = old_jaw[3]

                old_gantry = beam.GantryAngle
                old_collimator = beam.InitialCollimatorAngle
                old_beamName = beam.Name
                old_beamDescription = beam.Description
                old_isoName = beam.Isocenter.Annotation.Name
                iso_x = beam.Isocenter.Position.x
                iso_y = beam.Isocenter.Position.y
                iso_z = beam.Isocenter.Position.z
                iso_colour = beam.Isocenter.Annotation.DisplayColor
                old_rotation = beam.CouchRotationAngle
                old_pitch = beam.CouchPitchAngle
                
                old_roll = beam.CouchRollAngle
                
            #add 242 to beam MU
            beamset.Beams[0].BeamMU = 242
            ##calc dose
            beamset.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
            beamset.FractionDose.UpdateDoseGridStructures()
            beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)  

            ##create a d50
            #get max dose to skin roi in Gy
            nr_fractions  = beamset.FractionationPattern.NumberOfFractions
            Skin_max = beamset.FractionDose.GetDoseAtRelativeVolumes(RoiName='Skin', RelativeVolumes=[0])
            Skin_max_final = round(Skin_max[0] * nr_fractions)    #cGy max per plan dose

            #get 50% max dose in Gy
            Skin_max_50 = Skin_max_final * 0.5  ##cGy    

            #################################################################################################
            #roi from dose the 50% max Skin dose
            plan_dose = plan.TreatmentCourse.TotalDose
            threshold_level = Skin_max_50
            roi_name = 'zzd50'
            roi = case.PatientModel.CreateRoi(Name = roi_name, Color = 'Blue', Type = 'Ptv')
            roi.CreateRoiGeometryFromDose(DoseDistribution = plan_dose, ThresholdLevel = threshold_level)

            #create a copy new beamset 3DCRT and 5#s and NEW machine
            if beamset.MachineReference.MachineName == 'Agility':
                plan.AddNewBeamSet(Name='copy1', ExaminationName=examination.Name, MachineName='TrueBeamSTx', Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=5, CreateSetupBeams=False, Comment="")
            if beamset.MachineReference.MachineName == 'TrueBeamSTx':
                plan.AddNewBeamSet(Name='copy1', ExaminationName=examination.Name, MachineName='Agility', Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=5, CreateSetupBeams=False, Comment="")
                
            #need to set new beamset as current need to save before change
            patient.Save()
            beam_set = plan.BeamSets[1]
            beam_set.SetCurrent()


            ##create new beam match gantry coll iso
            beam_set.CreatePhotonBeam(BeamQualityId=r"6", IsocenterData={ 'Position': { 'x': iso_x, 'y': iso_y, 'z': iso_z }, 'NameOfIsocenterToRef': plan.Name, 'Name': plan.Name, 'Color': iso_colour }, Name=old_beamName, Description=old_beamDescription, GantryAngle=round(old_gantry), CouchRotationAngle=old_rotation, CouchPitchAngle=old_pitch, CouchRollAngle=old_roll, CollimatorAngle=round(old_collimator))

            ##set d50 treat roi
            beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName = 'zzd50')

            ##set leaf positi threshold 0 and conform to zzd50
            beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0)
            beam_set.TreatAndProtect()


            ##move jaws back to original size? errors on ant x2(left breast) jaw saying violates machine ?move all except ant jaw
            if plan.Name == 'Left Breast':  
                for beam in beam_set.Beams:
                    segments = beam.Segments[0]
                    jaw = segments.JawPositions
                    jaw[0] = old_x1   
                    #jaw[1] = old_x2  ant jaw left breast dont move yet as errors
                    jaw[2] = old_y1
                    jaw[3] = old_y2
                    segments.JawPositions = jaw
            if plan.Name == 'Right Breast':  
                for beam in beam_set.Beams:
                    segments = beam.Segments[0]
                    jaw = segments.JawPositions
                    #jaw[0] = old_x1  ant jaw right breast dont move yet as errors  
                    jaw[1] = old_x2  
                    jaw[2] = old_y1
                    jaw[3] = old_y2
                    segments.JawPositions = jaw

            ##now move ant mlc bank to original ant jaw position
            beam_set = get_current("BeamSet")
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                with CompositeAction('Shift ant MLCs to ant jaw'):
                    for beam in beam_set.Beams:
                        for segment in beam.Segments:
                            leafPositions = segment.LeafPositions
                            for leafNumber in range(60):  ##varian range
                                if plan.Name == 'Left Breast':    
                                    leafPositions[1][leafNumber] = old_x2  ##x2 bank ant
                                if plan.Name == 'Right Breast':        
                                    leafPositions[0][leafNumber] = old_x1  ##x1 bank ant
                            segment.LeafPositions = leafPositions
                            
            if beam_set.MachineReference.MachineName == 'Agility':
                with CompositeAction('Shift ant MLCs to ant jaw'):
                    for beam in beam_set.Beams:
                        for segment in beam.Segments:
                            leafPositions = segment.LeafPositions
                            for leafNumber in range(80):  ##elekta range
                                if plan.Name == 'Left Breast':
                                    leafPositions[1][leafNumber] = old_x2  ##x2 bank ant
                                if plan.Name == 'Right Breast':
                                    leafPositions[0][leafNumber] = old_x1  ##x1 bank ant
                        
                            segment.LeafPositions = leafPositions

            ##now move ant jaw to original
            for beam in beam_set.Beams:
                if plan.Name == 'Left Breast':
                    segments = beam.Segments[0]
                    jaw = segments.JawPositions
                    jaw[1] = old_x2  #moves ant jaw now
                    segments.JawPositions = jaw
                if plan.Name == 'Right Breast':
                    segments = beam.Segments[0]
                    jaw = segments.JawPositions
                    jaw[0] = old_x1   #moves ant jaw now
                    segments.JawPositions = jaw
                
            #close leaves behind jaws if needed?CAN DO IF PEOPLE WANT
            #close leaves behind jaws if needed. need to check if liekky has heart mlc first and then if not can conform mlc to field edges to tidy
            #varian left sided PB where bank X1 is post border MLC
            #loop thorugh mlc in ranges 0,10 to 0,46 and add values to a list
            #find the max and min of those values
            #find the difference of that mmax min values
            #if the differercne is amll ,0.1cm then we assume theres no heart mlc being displaced anterior
            #then we can confoirm the mlc to field edges
            def conform_mlc_if_no_heart_mlc():
                mlc_list = []

                for beam in beam_set.Beams:
                    for segment in beam.Segments:
                        if plan.Name == 'Left Breast':
                            leaf_positions = segment.LeafPositions[0]
                        if plan.Name == 'Right Breast':
                            leaf_positions = segment.LeafPositions[1]
                        
                        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':        
                            for i in range(10, 46):
                                mlc_list.append(leaf_positions[i])
                        if beam_set.MachineReference.MachineName == 'Agility':        
                            for i in range(30, 46):
                                mlc_list.append(leaf_positions[i])        
                                
                            
                max_mlcdiff = abs(max(mlc_list)-min(mlc_list)) 

                if max_mlcdiff < 0.1:  #if mlc differences along back border <0.1cm then likely no heart mlc in field so we can conform mlc to field edges to tidy up
                    no_heartMLC = "True"
                    beam_set.Beams[0].RemoveTreatOrProtectRoi(RoiName = 'zzd50') ##remove ccurrent treat margins set on zzd50 roi
                    beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0)
                    beam_set.TreatAndProtect()

            conform_mlc_if_no_heart_mlc()



            # save and delete beamset0
            patient.Save()
            beam_set = plan.BeamSets[0]
            beam_set.SetCurrent()
            beam_set.DeleteBeamSet()
            patient.Save()

            ##delete roi zzd50
            #case.PatientModel.RegionsOfInterest['zzd50'].DeleteRoi()

            #pt save
            patient.Save()
            beam_set = get_current("BeamSet")

        ######DECIDE WHAT TO DO BASED ON WHAT MACHINE SELECTED######
        if clicked2.get() == 'TrueBeamSTx':
            if beam_set.MachineReference.MachineName == 'Agility':
                if len(beam_set.Beams[0].Segments) == 0: 
                    changeMachine_NoMLC()
                if len(beam_set.Beams[0].Segments) == 1: 
                    changeMachine_MLC()
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                pass
            
            
        if clicked2.get() == 'Agility':
            if beam_set.MachineReference.MachineName == 'Agility':
                pass
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                if len(beam_set.Beams[0].Segments) == 0: 
                    changeMachine_NoMLC()
                if len(beam_set.Beams[0].Segments) == 1: 
                    changeMachine_MLC()


        ################################################END MACHINE CHANGE BITS#####################
        #EDIT BEAMSET name to match plan name
        plan.BeamSets[0].DicomPlanLabel = plan.Name

        ##if no MLC on medial field at start then MLC is conformed to jaws
        beam_set = get_current("BeamSet")
        if len(beam_set.Beams[0].Segments) == 0:
            beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0) #sets treat protect outside so no mlc comes inside edge at top and bottom
            beam_set.TreatAndProtect()


        #CHANGE med beam DEFAULT TO 6MV if its 10MV
        plan.BeamSets[0].Beams[0].BeamQualityId = r"6"

        #rounds gentry angle only if needed but state tree doesnt allow setting of a coll angle
        beam_set = get_current("BeamSet")
        beam_set.Beams[0].GantryAngle = round(beam_set.Beams[0].GantryAngle)


        #CONFORM MLC BEAM IF NOT DONE AS WONT RUN - may not be scripable yet

        #access pois for a list
        pois = case.PatientModel.PointsOfInterest
                   
        poi_list = []

        for poi in pois:
            if poi.Type == 'LocalizationPoint':
                poi_list.append(poi.Name)
                
        ##if the list above is empty then theres no localization point present
        if len(poi_list) == 0:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "No POI with Type 'LocalizationPoint' defined!")
            exit()

        # Get POI geometries 
        poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries

        #for item in poi_list. uses the localisation point type as point here which is the index 0 point in list if present     
        center_x = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.x
        center_y = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.y
        center_z = case.PatientModel.StructureSets[examination.Name].PoiGeometries[poi_list[0]].Point.z

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

        #makes rlat tattoo point
        retval_5 = case.PatientModel.CreatePoi(Examination=examination, Point=center_right_tattoo_ROI_coordinates, Name=r"Right lat tattoo", Color="Yellow", VisualizationDiameter=1, Type="Undefined")

        #thresholding to place lat poi marker for better accuracy of placement
        def thresholdlat_pois():
            try:
                #mark threshold ribs roi
                with CompositeAction('Gray level threshold (Ribs)'):
                    # Threshold action
                    r = case.PatientModel.CreateRoi(Name=r"Ribs", Color="SaddleBrown", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
                    r.GrayLevelThreshold(Examination=examination, LowThreshold=100, HighThreshold=2000, PetUnit=r"", CbctUnit=None, BoundingBox=None)
                    # Expand and contract
                    r.CreateMarginGeometry(Examination=examination, SourceRoiName=r"Ribs", MarginSettings={ 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 })
                    r.CreateMarginGeometry(Examination=examination, SourceRoiName=r"Ribs", MarginSettings={ 'Type': "Contract", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 })
                    # Simplify contours
                    case.PatientModel.StructureSets[examination.Name].SimplifyContours(RoiNames=[r"Ribs"], RemoveHoles3D=True, RemoveSmallContours=True, AreaThreshold=0.1, ReduceMaxNumberOfPointsInContours=False, MaxNumberOfPoints=None, CreateCopyOfRoi=False, ResolveOverlappingContours=True)
                
                if plan.Name == 'Right Breast':
                    #intersect right tattoo roi with threshold ribs roi to make marker roi final
                    with CompositeAction('ROI algebra (right lat marker roi)'):

                      retval_0 = case.PatientModel.CreateRoi(Name="right lat marker roi", Color="Lime", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

                      retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Ribs"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["right tattoo ROI"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

                      retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

                    #need to get center coordinates of ROI right tattoo ROI to use below to make poi tattoo in center
                    try:
                        roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
                        roi_name = 'right lat marker roi'
                        roi_center = roi_geometries[roi_name].GetCenterOfRoi()
                        center_right_tattoo_ROI_coordinates = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}

                        #makes rlat tattoo point
                        retval_5 = case.PatientModel.CreatePoi(Examination=examination, Point=center_right_tattoo_ROI_coordinates, Name=r"right lat marker tatt", Color="Yellow", VisualizationDiameter=1, Type="Undefined")

                        #delete old one # tidy up
                        case.PatientModel.PointsOfInterest['Right lat tattoo'].DeleteRoi()
                        case.PatientModel.RegionsOfInterest['right lat marker roi'].DeleteRoi()
                        case.PatientModel.RegionsOfInterest['Ribs'].DeleteRoi()
                        case.PatientModel.PointsOfInterest['right lat marker tatt'].Name = "Right lat tattoo"
                    except:
                        case.PatientModel.RegionsOfInterest['Ribs'].DeleteRoi()
                        case.PatientModel.RegionsOfInterest['right lat marker roi'].DeleteRoi()
                    
                if plan.Name == 'Left Breast':
                    #intersect lefttattoo roi with threshold ribs roi to make marker roi final
                    with CompositeAction('ROI algebra (left lat marker roi)'):

                      retval_0 = case.PatientModel.CreateRoi(Name="left lat marker roi", Color="Lime", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

                      retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Ribs"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["left tattoo ROI"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

                      retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

                    #need to get center coordinates of ROI right tattoo ROI to use below to make poi tattoo in center
                    try:
                        roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
                        roi_name = 'left lat marker roi'
                        roi_center = roi_geometries[roi_name].GetCenterOfRoi()
                        center_right_tattoo_ROI_coordinates = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}

                        #makes llat tattoo point
                        retval_5 = case.PatientModel.CreatePoi(Examination=examination, Point=center_right_tattoo_ROI_coordinates, Name=r"left lat marker tatt", Color="Yellow", VisualizationDiameter=1, Type="Undefined")

                        #delete old one
                        case.PatientModel.PointsOfInterest['Left lat tattoo'].DeleteRoi()
                        case.PatientModel.RegionsOfInterest['left lat marker roi'].DeleteRoi()
                        case.PatientModel.RegionsOfInterest['Ribs'].DeleteRoi()
                        case.PatientModel.PointsOfInterest['left lat marker tatt'].Name = "Left lat tattoo"
                    except:
                        case.PatientModel.RegionsOfInterest['Ribs'].DeleteRoi()
                        case.PatientModel.RegionsOfInterest['left lat marker roi'].DeleteRoi()
            except:
                pass

        #run lat poi thresholding    
        thresholdlat_pois()

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
        if plan.Name == 'Left Breast':
            case.PatientModel.PointsOfInterest['Right lat tattoo'].DeleteRoi()
        elif plan.Name == 'Right Breast':
            case.PatientModel.PointsOfInterest['Left lat tattoo'].DeleteRoi()
            
        #load MABS Heart ROI?could load heart and skin and lungs from here MABS OAR Breast in clinical db?
            
            
        #load roi template for Breast 26Gy/5F. doesnt load skin or heart as both done before (skin by defer and heart MABS)
        #not working despite recorded likely due to source saved location? or edits to source file? ask marian/josh
        #case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.TemplatePatientModels['Breast_Table1(26Gy)'], SourceExaminationName=r"CT 1", SourceRoiNames=[r"PTVp_2600", r"Skin-PTV", r"Lung_Ipsi", r"xxBreast_T1(26Gy)"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")

        #add ROIs manually via record script as loading template not working above

        retval_1 = case.PatientModel.CreateRoi(Name=r"Lung_Ipsi", Color="Teal", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        
        retval_1 = case.PatientModel.CreateRoi(Name=r"Lung_Contra", Color="Teal", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        
        case.PatientModel.CreateRoi(Name=r"Breast_Contra", Color="Aqua", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

        retval_3 = case.PatientModel.CreateRoi(Name=r"xxBreast_T3(48Gy no Nodes)", Color="Black", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)


        #run MBS for BOTH lung ROIs
        case.PatientModel.MBSAutoInitializer(MbsRois=[{ 'CaseType': "Thorax", 'ModelName': r"Lung (Left)", 'RoiName': r"Lung (Left)", 'RoiColor': "255, 51, 204" }], CreateNewRois=True, Examination=examination, UseAtlasBasedInitialization=True)
        case.PatientModel.AdaptMbsMeshes(Examination=examination, RoiNames=[r"Lung (Left)"], CustomStatistics=None, CustomSettings=None)
        
        case.PatientModel.MBSAutoInitializer(MbsRois=[{ 'CaseType': "Thorax", 'ModelName': r"Lung (Right)", 'RoiName': r"Lung (Right)", 'RoiColor': "0, 255, 0" }], CreateNewRois=True, Examination=examination, UseAtlasBasedInitialization=True)
        case.PatientModel.AdaptMbsMeshes(Examination=examination, RoiNames=[r"Lung (Right)"], CustomStatistics=None, CustomSettings=None)

        #copy lung rois into correctly named ROis if left or right sided plan
        if plan.Name == 'Left Breast':
            with CompositeAction('ROI algebra (Lung_Ipsi)'):

                retval_0 = case.PatientModel.RegionsOfInterest['Lung_Ipsi'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Left)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

                retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
                
            with CompositeAction('ROI algebra (Lung_Contra)'):

                retval_0 = case.PatientModel.RegionsOfInterest['Lung_Contra'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Right)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

                retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

                # CompositeAction ends
        elif plan.Name == 'Right Breast':
            with CompositeAction('ROI algebra (Lung_Ipsi)'):

                retval_0 = case.PatientModel.RegionsOfInterest['Lung_Ipsi'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Right)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

                retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
                
            with CompositeAction('ROI algebra (Lung_Contra)'):

                retval_0 = case.PatientModel.RegionsOfInterest['Lung_Contra'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Lung (Left)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

                retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

                # CompositeAction ends
                
        #delete MBS named lung ROIs
        case.PatientModel.RegionsOfInterest['Lung (Left)'].DeleteRoi()

        case.PatientModel.RegionsOfInterest['Lung (Right)'].DeleteRoi()
                   
       
        '''         
        #DLS CONTRA BREAST AND LUNGS. if already there then they are renamed anyways
        patient_db = get_current("PatientDB")
        if plan.Name == 'Left Breast':
                tpm = patient_db.LoadTemplatePatientModel(templateName = 'Dr_Breast_Nodal_DLS_Left_TestIG2', lockMode = 'Read')
                case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName=r"CT 1", SourceRoiNames=['Breast_Contra', 'Lung_Ipsi', 'Lung_Contra'], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")
        elif plan.Name == 'Right Breast':
            tpm = patient_db.LoadTemplatePatientModel(templateName = 'Dr_Breast_Nodal_DLS_Right_TestIG2', lockMode = 'Read')
            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName=r"CT 1", SourceRoiNames=['Breast_Contra', 'Lung_Ipsi', 'Lung_Contra'], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")
        '''

        ################Bring planner to modelling window. access tabs of interest###########################################################################################################
        ui = get_current('ui')
        ui.TitleBar.Navigation.MenuItem['Patient modeling'].Button_Patient_modeling.Click()
        ui.TabControl_Modules.TabItem['Structure definition'].Button_Structure_definition.Click()
        ui.ToolPanel.TabItem['ROIs'].Select() # go to ROI side tools

        ###turns off all rois and pois except ipsi lung and skin
        rois = case.PatientModel.RegionsOfInterest 

        for roi in rois:
            patient.SetRoiVisibility(RoiName=roi.Name, IsVisible=False)

        patient.SetRoiVisibility(RoiName='Lung_Ipsi', IsVisible=True)
        patient.SetRoiVisibility(RoiName='Lung_Contra', IsVisible=True)
        patient.SetRoiVisibility(RoiName='Breast_Contra', IsVisible=True)
        patient.SetRoiVisibility(RoiName='Skin', IsVisible=True)


        #in response to rare error  in creating ptv due to overlapping ipsi lung contours
        case.PatientModel.StructureSets[examination.Name].SimplifyContours(RoiNames=[r"Lung_Ipsi"], RemoveHoles3D=False, RemoveSmallContours=False, AreaThreshold=None, ReduceMaxNumberOfPointsInContours=False, MaxNumberOfPoints=None, CreateCopyOfRoi=False, ResolveOverlappingContours=True)
        
        patient.Save()
        ##prompts use to check rois. the user can then continue script from left lower panel when happy or stop it
        await_user_input("Please review/edit the created ROIs (Lung_Ipsi / Lung_Contra) and manually roi Breast_Contra\n\nOnce happy please click resume at the bottom left of the Scripting Menu")
        ###################################################################################################################################################################################

        ##double check contra breast roi present and has contours - if not pause again for user to sort
        rois = case.PatientModel.RegionsOfInterest 

        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
            
        if 'Breast_Contra' not in roi_list:
            await_user_input("Please outline a 'Breast_Contra' ROI\n\nOnce happy please click resume at the bottom left of the Scripting Menu")
            
        if 'Breast_Contra' in roi_list:
            if roi_structures["Breast_Contra"].HasContours() is False:
                await_user_input("Please outline a 'Breast_Contra' ROI\n\nOnce happy please click resume at the bottom left of the Scripting Menu")
            
        ###BRING BACK TO PLAN DESIGN TAB#######
        ui.TitleBar.Navigation.MenuItem['Plan design'].Button_Plan_design.Click() #go to plan design
        ui.TabControl_Modules.TabItem['Plan setup'].Button_Plan_setup.Click()  ##plansetup tab
        ui.Workspace.TabControl['Plan'].TabItem['Beams'].Select()   ##beams tab

        #set grid size default
        with CompositeAction('Set default grid'):

          retval_0 = beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })

          beam_set.FractionDose.UpdateDoseGridStructures()

        beam_set = get_current("BeamSet")

        #Names beams med depending on machine name
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            if plan.Name == 'Left Breast':
                beam_set.Beams[0].Name = r"VA01"
                beam_set.Beams['VA01'].Description = r"VA01 LMED"
            elif plan.Name == 'Right Breast':
                beam_set.Beams[0].Name = r"VA01"
                beam_set.Beams['VA01'].Description = r"VA01 RMED"
        elif beam_set.MachineReference.MachineName == 'Agility':
            if plan.Name == 'Left Breast':
                beam_set.Beams[0].Name = r"EA01"
                beam_set.Beams['EA01'].Description = r"EA01 LMED"
            elif plan.Name == 'Right Breast':
                beam_set.Beams[0].Name = r"EA01"
                beam_set.Beams['EA01'].Description = r"EA01 RMED"
                

        #define machine as beamset 1 machine
        machine_name = plan.BeamSets[0].MachineReference.MachineName

        #opposes the 3DCRT beam
        beam_set = get_current("BeamSet") ##added new test
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            beam_set.AddOpposedBeam(BeamName=r"VA01")
        elif beam_set.MachineReference.MachineName == 'Agility':
            beam_set.AddOpposedBeam(BeamName=r"EA01")

        #rename lat beam
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            if plan.Name == 'Left Breast':
                beam_set.Beams[1].Name = r"VA03"
                beam_set.Beams['VA03'].Description = r"VA03 LLAT"
            elif plan.Name == 'Right Breast':
                beam_set.Beams[1].Name = r"VA03"
                beam_set.Beams['VA03'].Description = r"VA03 RLAT"
        elif beam_set.MachineReference.MachineName == 'Agility':
            if plan.Name == 'Left Breast':
                beam_set.Beams[1].Name = r"EA03"
                beam_set.Beams['EA03'].Description = r"EA03 LLAT"
            elif plan.Name == 'Right Breast':
                beam_set.Beams[1].Name = r"EA03"
                beam_set.Beams['EA03'].Description = r"EA03 RLAT"
            
        #################################FORMULA TO ALIGN LATERAL GANTRY ANGLE#####################################################################################
        #divergence = tan-1(0.5 * (post x jaw size x 2 / 100))
        #new lateral angle(right breast) = oppossed gantry angle - 2 * divergence
        #new lateral angle(left breast) = oppossed gantry angle + 2 * divergence

        #if its right breast we want x2 jaw varian or mlc for elekta (its a positive value eg 3.4)
        #if its left breast we want x1 jaw varian or mlc elekta (its  negative value eg - 5.7)
        ##we are assuming collimators are off 0 at def stage!!##
        #divergence = math.degrees(math.atan(x))

        if plan.Name == 'Left Breast':
            x = 0.5 * abs(beam_set.Beams[0].Segments[0].JawPositions[0]) * 2 / 100 ##x1 as a positive value eg -5.7 to 5.7
            divergence = math.degrees(math.atan(x))
            beam_set.Beams[1].GantryAngle = round(beam_set.Beams[1].GantryAngle + 2 * divergence)  ##pt 4355684 expect to go from 133(opposed) to 139.5246588 on lat
            
        if plan.Name == 'Right Breast':
            x = 0.5 * abs(beam_set.Beams[0].Segments[0].JawPositions[1]) * 2 / 100   ##x2 is post jaw positive on right breast
            divergence = math.degrees(math.atan(x))
            beam_set.Beams[1].GantryAngle = round(beam_set.Beams[1].GantryAngle - 2 * divergence)

        ##########################################################################################################################################################
        
        ##make bolus now if needed before any calcs
        with CompositeAction('Expand (PTVp_4800)'):

            retval_0 = case.PatientModel.CreateRoi(Name=r"PTVp_4800", Color="Red", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_0.SetMarginExpression(SourceRoiName=r"CTVp_4800", MarginSettings={ 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 })

            retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

        # CompositeAction ends
        with CompositeAction('ROI algebra (zzPlanning Bolus)'):

            retval_1 = case.PatientModel.CreateRoi(Name=r"zzPlanning Bolus", Color="Aqua", Type="Bolus", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_1.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Skin"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            
        ##IF BOLUS NO CONTOURS THEN DELETE, otherwise assign material water - scripting bug in 10A with setting material - julien uzan 2020 community post - workaround below loading template roi i made
        roi_structures = case.PatientModel.StructureSets[examination.Name].RoiGeometries

        if roi_structures["zzPlanning Bolus"].HasContours() is False:
            case.PatientModel.RegionsOfInterest['zzPlanning Bolus'].DeleteRoi()
        else:
            ##need to load a template that has an roi with water density first so system knows what material we can then assign to bolus
            tpm = db.LoadTemplatePatientModel(templateName = 'zzWater density', lockMode = 'Read')
            case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=tpm, SourceExaminationName='CT 1', SourceRoiNames=["zzWater density"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="EmptyGeometries")

            case.PatientModel.RegionsOfInterest['zzPlanning Bolus'].SetRoiMaterial(Material=case.PatientModel.Materials[0])

        #add bolus beams if required
        rois = case.PatientModel.RegionsOfInterest 

        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
            
            
        if 'zzPlanning Bolus' in roi_list:
            for Beams in beam_set.Beams:
                Beams.SetBolus(BolusName=r"zzPlanning Bolus")


        ##delete the water density roi - as not needed anymore as we got the desnity info assigned above 
        if 'zzWater density' in roi_list:
            case.PatientModel.RegionsOfInterest['zzWater density'].DeleteRoi()
        
        
        
        #enter 129MU on each open beam_set calc dose
        beam_set.Beams[0].BeamMU = 129
        beam_set.Beams[1].BeamMU = 129
        beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
        plan.TreatmentCourse.TotalDose.UpdateDoseGridStructures()
        beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False) 

        #get max dose to skin roi in Gy
        nr_fractions  = beam_set.FractionationPattern.NumberOfFractions
        Skin_max = beam_set.FractionDose.GetDoseAtRelativeVolumes(RoiName='Skin', RelativeVolumes=[0])
        Skin_max_final = round(Skin_max[0] * nr_fractions)    #cGy max per plan dose

        #get 50% max dose in Gy
        Skin_max_50 = Skin_max_final * 0.5  ##cGy    


        #################################################################################################
        #roi from dose the 50% max Skin dose
        plan_dose = plan.TreatmentCourse.TotalDose
        threshold_level = Skin_max_50
        roi_name = 'd50'
        roi = case.PatientModel.CreateRoi(Name = roi_name, Color = 'Blue', Type = 'Control')
        roi.CreateRoiGeometryFromDose(DoseDistribution = plan_dose, ThresholdLevel = threshold_level)

        #make it a contour as can access primary.shape.contour
        case.PatientModel.StructureSets[examination.Name].RoiGeometries['d50'].SetRepresentation(Representation='Contours')
        
        #sort roi algebra to make PTV from zzD50 and update skin-ptv, then delete zzD50 roi
        
        #make empty PTVp_4000
        retval_0 = case.PatientModel.CreateRoi(Name=r"PTVp_4000", Color="Red", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        
        #make d50 for ptv_4000
        with CompositeAction('ROI algebra (1)'):

          retval_0 = case.PatientModel.CreateRoi(Name=r"1", Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"d50"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Skin"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('ROI algebra (2)'):

          retval_1 = case.PatientModel.CreateRoi(Name=r"2", Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

          retval_1.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"1"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Lung_Ipsi"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('ROI algebra (PTVp_4000)'):

          retval_2 = case.PatientModel.RegionsOfInterest['PTVp_4000'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"2"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

          retval_2.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

          # CompositeAction ends 


        with CompositeAction('Delete ROI (1, 2)'):

          retval_0.DeleteRoi()

          retval_1.DeleteRoi()

          # CompositeAction ends 
        #grow and sort remainder rois


        with CompositeAction('ROI algebra (PTVp_4800_DVH)'):

            retval_0 = case.PatientModel.CreateRoi(Name=r"PTVp_4800_DVH", Color="255, 0, 128", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"CTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"Skin"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends 
          
        with CompositeAction('Expand (PTVp_4800_DVH+1cm)'):

            retval_0 = case.PatientModel.CreateRoi(Name=r"PTVp_4800_DVH+1cm", Color="Yellow", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_0.SetMarginExpression(SourceRoiName=r"PTVp_4800_DVH", MarginSettings={ 'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 1, 'Posterior': 1, 'Right': 1, 'Left': 1 })

            retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends 
            
        with CompositeAction('ROI algebra (PTVp_4000-PTVp_4800_DVH)'):

            retval_0 = case.PatientModel.CreateRoi(Name=r"PTVp_4000-PTVp_4800_DVH", Color="Lime", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800_DVH"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends 


        with CompositeAction('ROI algebra (PTVp_4000-PTVp_4800_DVH+1cm)'):

            retval_1 = case.PatientModel.CreateRoi(Name=r"PTVp_4000-PTVp_4800_DVH+1cm", Color="Lime", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_1.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800_DVH+1cm"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends
            
        with CompositeAction('ROI algebra (Skin-PTVAndAx)'):

            retval_0 = case.PatientModel.CreateRoi(Name=r"Skin-PTVAndAx", Color="Lime", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"Skin"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800_DVH+1cm", r"PTVp_4000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

        # CompositeAction ends 


        with CompositeAction('ROI algebra (zzRing1_SIB)'):

            retval_2 = case.PatientModel.CreateRoi(Name=r"zzRing1_SIB", Color="255, 0, 128", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_2.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_2.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends 


        with CompositeAction('ROI algebra (zzRing2_SIB)'):

            retval_3 = case.PatientModel.CreateRoi(Name=r"zzRing2_SIB", Color="Green", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_3.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_3.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends 


        with CompositeAction('ROI algebra (zzRing3_SIB)'):

            retval_4 = case.PatientModel.CreateRoi(Name=r"zzRing3_SIB", Color="255, 128, 0", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

            retval_4.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [r"PTVp_4800"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

            retval_4.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

            # CompositeAction ends
            
                
                
        ####GET FIELD BORDERS TO TATTOOS MEASURMEWNTS AND SEPARATIONS DISTANCES BASED ON ADDING POINTS TO ROI d50
        ######################MED BORDER FOR LEFT BREAST##################################

        if plan.Name == 'Left Breast':
            #Get POI geometries 
            poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries
             
            #LIST TO ADD THE NEW X COORDINATE FOR d50 on slice where z is 0
            z_value = center_z
            z_coord = []
            x_coords = []

            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    array = coordinate.z
                    idx = (np.abs(array - z_value)).argmin()
                    z_coord.append(idx)
                    if coordinate.z == z_coord[0]:   #on slice 0 gets list of all x values 
                        x_coords.append(coordinate.x)
                      
            new_x = min(x_coords)  ##(for left breast we then want smallest x which is closest to contra side in contour)

            y_coords = []  ##empty list to add our new y value

            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    while coordinate.z == z_coord[0] and coordinate.x == new_x:   ##loops thorugh to find y value when z=0 and x=min value
                        y_coords.append(coordinate.y)  ##adds the y value to list to be called on below and breaks loop
                        break
                                        
            #create the point
            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': new_x, 'y': y_coords[0], 'z': center_z }, Name=r"Med border left breast", Color="Yellow", VisualizationDiameter=1, Type="Undefined")
            ######################################################################################

            ######################LAT BORDER FOR LEFT BREAST##################################

            #get the x point for d50 on slice where z is 0
            y1_coords = []

            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    if coordinate.z == z_coord[0]:   #on slice 0 gets list of all y values 
                        y1_coords.append(coordinate.y)
                      
            new_y = max(y1_coords)  ##(for left breast we then want LARGEST y which is most posterior contour point)

            x1_coords = []  ##empty list to add our new x value

            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    while coordinate.z == z_coord[0] and coordinate.y == new_y:   ##loops thorugh to find y value when z=0 and x=min value
                        x1_coords.append(coordinate.x)  ##adds the y value to list to be called on below and breaks loop
                        break
                                        
            #create the point
            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': x1_coords[0], 'y': new_y, 'z': center_z }, Name=r"Lat border left breast", Color="Yellow", VisualizationDiameter=1, Type="Undefined")
            
            ##################################################################################################################
            #MOVE FIELD BORDERS BY SMALL OFFSET TO BETTER ALIGN WITH FIELD EDGES AS USES D50% ISODOSE SO NEEDS SMALL ADJUSTMENT
            ##################################################################################################################
            #access MEDIAL BORDER pois geometries
            center_xMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point.x
            center_yMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point.y 
            center_zMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point.z

            #get Lat border left breast coordinates
            center_xLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point.x
            center_yLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point.y
            center_zLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point.z
            
            ##shift medial 0.2cm to contra side and lateral border poi 0.3cm post
            case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point = { 'x': center_xMB - 0.2, 'y': center_yMB, 'z': center_zMB } # moves poi right
            case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point = { 'x': center_xLB, 'y': center_yLB + 0.3, 'z': center_zLB } # moves poi post
            ###################################################################################################################
            

            ######DISTANCE BORDERS FOR LEFT BREAST################################################################################

            #get medial tattoo coordinates 
            center_xMT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.x  
            center_yMT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.y       
            center_zMT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.z  


            #get Med border left breast coordinates
            center_xMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point.x
            center_yMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point.y 
            center_zMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border left breast'].Point.z 

            #calc distance between med tat and med border points
            d1 = ((center_xMB - center_xMT)**2 + (center_yMB - center_yMT)**2 + (center_zMB - center_zMT)**2)**0.5
            Med_tattoo_to_field_edge = round(d1, 1)

            #get lat tattoo coordinates
            center_xLT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Left lat tattoo'].Point.x  
            center_yLT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Left lat tattoo'].Point.y       
            center_zLT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Left lat tattoo'].Point.z 

            #get Lat border left breast coordinates
            center_xLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point.x
            center_yLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point.y
            center_zLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border left breast'].Point.z

            #calc distance between lat tat and lat border points
            d2 = ((center_xLB - center_xLT)**2 + (center_yLB - center_yLT)**2 + (center_zLB - center_zLT)**2)**0.5
            Lat_tattoo_to_field_edge = round(d2, 1)
        
            ############################SEPARATION DISTANCE LEFT BREAST#####################################################################
            Sep_LB = ((center_xMB - center_xLB)**2 + (center_yMB - center_yLB)**2 + (center_zMB - center_zLB)**2)**0.5
            Separation_LB = round(Sep_LB, 1)
        
        
        
        
        if plan.Name == 'Right Breast':
            ######################MED BORDER FOR RIGHT BREAST##################################
            z_value = center_z
            z_coord = []
            x2_coords = []  #LIST TO ADD THE NEW X COORDINATE FOR d50 on slice where z is 0

            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    array = coordinate.z
                    idx = (np.abs(array - z_value)).argmin()
                    z_coord.append(idx)
                    if coordinate.z == z_coord[0]:   #on slice 0 gets list of all x values 
                        x2_coords.append(coordinate.x)
                      
            new_x1 = max(x2_coords)  ##(for left breast we then want smallest x which is cloest to contra side in contour)

            y2_coords = []  ##empty list to add our new y value

            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    while coordinate.z == z_coord[0] and coordinate.x == new_x1:   ##loops thorugh to find y value when z=0 and x=min value
                        y2_coords.append(coordinate.y)  ##adds the y value to list to be called on below and breaks loop
                        break
                                        
            #create the point
            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': new_x1, 'y': y2_coords[0], 'z': center_z }, Name=r"Med border right breast", Color="Yellow", VisualizationDiameter=1, Type="Undefined")

            ######################LAT BORDER FOR RIGHT BREAST##################################

            #get the x point for d50 on slice where z is 0
            y3_coords = []

            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    if coordinate.z == z_coord[0]:   #on slice 0 gets list of all y values 
                        y3_coords.append(coordinate.y)
                      
            new_y1 = max(y3_coords)  ##(for left breast we then want LARGEST y which is most posterior contour point)

            x3_coords = []  ##empty list to add our new x value

            for [contour_index, contour] in enumerate(ss.RoiGeometries['d50'].PrimaryShape.Contours):
                for coordinate in contour:
                    while coordinate.z == z_coord[0] and coordinate.y == new_y1:   ##loops thorugh to find y value when z=0 and x=min value
                        x3_coords.append(coordinate.x)  ##adds the y value to list to be called on below and breaks loop
                        break
                                        
            #create the point
            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': x3_coords[0], 'y': new_y1, 'z': center_z }, Name=r"Lat border right breast", Color="Yellow", VisualizationDiameter=1, Type="Undefined")
            
            ##################################################################################################################
            #MOVE FIELD BORDERS BY SMALL OFFSET TO BETTER ALIGN WITH FIELD EDGES AS USES D50% ISODOSE SO NEEDS SMALL ADJUSTMENT
            ##################################################################################################################
            #get Med border RIGHT breast coordinates
            center_xMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point.x
            center_yMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point.y 
            center_zMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point.z

            #get Lat border RIGHT breast coordinates
            center_xLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point.x
            center_yLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point.y
            center_zLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point.z
            ##shift medial 0.2cm to contra side and lateral border poi 0.3cm post 
            case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point = { 'x': center_xMB + 0.2, 'y': center_yMB, 'z': center_zMB } # moves poi left
            case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point = { 'x': center_xLB, 'y': center_yLB + 0.3, 'z': center_zLB } # moves poi post
            ###################################################################################################################################################################################
            
            
            ######DISTANCE BORDERS FOR RIGHT BREAST################################################################################
            center_xMT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.x  
            center_yMT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.y       
            center_zMT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med tattoo'].Point.z

            #get Med border left breast coordinates
            center_xMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point.x
            center_yMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point.y 
            center_zMB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Med border right breast'].Point.z

            #calc distance between med tat and med border points
            d1 = ((center_xMB - center_xMT)**2 + (center_yMB - center_yMT)**2 + (center_zMB - center_zMT)**2)**0.5
            Med_tattoo_to_field_edge = round(d1, 1)

            #get lat tattoo coordinates
            center_xLT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Right lat tattoo'].Point.x  
            center_yLT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Right lat tattoo'].Point.y       
            center_zLT = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Right lat tattoo'].Point.z 

            #get Lat border left breast coordinates
            center_xLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point.x
            center_yLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point.y
            center_zLB = case.PatientModel.StructureSets[examination.Name].PoiGeometries['Lat border right breast'].Point.z

            #calc distance between lat tat and lat border points
            d2 = ((center_xLB - center_xLT)**2 + (center_yLB - center_yLT)**2 + (center_zLB - center_zLT)**2)**0.5
            Lat_tattoo_to_field_edge = round(d2, 1)
            
            ###SEP RIGHT BREAST##################################
            Sep_LB = ((center_xMB - center_xLB)**2 + (center_yMB - center_yLB)**2 + (center_zMB - center_zLB)**2)**0.5
            Separation_LB = round(Sep_LB, 1)
            
        
        ##################################################################### LATERAL BEAM FLASH PART#######################################################################################################

        ####################################################################################################################################################################################################
        ##GROW THE D50 ant 2cm and right or left 2cm only
        if plan.Name == 'Left Breast':
            with CompositeAction('ROI algebra (FLASH)'):

              retval_0 = case.PatientModel.CreateRoi(Name=r"FLASH", Color="255, 0, 128", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

              retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"d50"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 2, 'Posterior': 0, 'Right': 0, 'Left': 2 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

              retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

              # CompositeAction ends 
              
        if plan.Name == 'Right Breast':
            with CompositeAction('ROI algebra (FLASH)'):

              retval_0 = case.PatientModel.CreateRoi(Name=r"FLASH", Color="255, 0, 128", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

              retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [r"d50"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 2, 'Posterior': 0, 'Right': 2, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

              retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

              # CompositeAction ends 


        ##make another beamset
        machine_name = plan.BeamSets[0].MachineReference.MachineName

        plan.AddNewBeamSet(Name='FLASH', ExaminationName=examination.Name, MachineName=machine_name, Modality="Photons", TreatmentTechnique="Conformal", PatientPosition="HeadFirstSupine", NumberOfFractions=15, CreateSetupBeams=False, Comment="")

        ##copy in the lat beam_set
        patient.Save()
        beam_set = plan.BeamSets[1]
        beam_set.SetCurrent()

        ##now copy over LAT from beamset 0 into beamset 1
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets[0], BeamsToCopy=[r"VA03"])
        if beam_set.MachineReference.MachineName == 'Agility':
            beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets[0], BeamsToCopy=[r"EA03"])


        ##set roi treat roi d50
        beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName = 'FLASH')

        #beam_set.Beams[2].SetTreatAndProtectMarginsForBeam(TopMargin=0.0, BottomMargin=0.0 LeftMargin=0.0, RightMargin=0.0, Roi='d50')

        ##conform mlc outside jaw
        beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0) #sets treat protect outside so no mlc comes inside edge at top and bottom
        beam_set.TreatAndProtect()

        ##note ant jaw size depending if left or right
        if plan.Name == 'Left Breast':
            FlashAnt_jaw = beam_set.Beams[0].Segments[0].JawPositions[0]  #minus number x1
        if plan.Name == 'Right Breast':
            FlashAnt_jaw = beam_set.Beams[0].Segments[0].JawPositions[1]  ##plus number x2


        ##delete roi treat roi setting
        beam_set.Beams[0].RemoveTreatOrProtectRoi(RoiName = 'FLASH')

        #delete roi
        case.PatientModel.RegionsOfInterest['FLASH'].DeleteRoi()

        ##delete beamset and beam_set
        beam_set.DeleteBeamSet()
        patient.Save()

        beam_set = plan.BeamSets[0]
        beam_set.SetCurrent()
        beam_set = get_current("BeamSet")


        def SortFlashLat():       
            ##move x ant jaw to 2cm flash only if it is less than 2cm
            for beam in beam_set.Beams:
                segments = beam.Segments[0]
                jaw = segments.JawPositions
                if beam.Name in ['EA03', 'VA03']:
                    if plan.Name == 'Left Breast':
                        if jaw[0] > FlashAnt_jaw:
                            jaw[0] = FlashAnt_jaw
                    if plan.Name == 'Right Breast':
                        if jaw[1] < FlashAnt_jaw:
                            jaw[1] = FlashAnt_jaw
                segments.JawPositions = jaw


                    
            #move ant bank of mlc out to jaw position also now dep if left or right and machine - full ant row or just aross beam? cant conform mlc in case heart or siso mlc already on post x side
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                with CompositeAction('Shift ant MLCs to ant jaw'):
                    for beam in beam_set.Beams:
                        if beam.Name in ['VA03']: 
                            for segment in beam.Segments:
                                leafPositions = segment.LeafPositions
                                for leafNumber in range(59):  ##varian range - SHOULD BE 60 but leave top one closed so next bit close leafs behinds jaws using this as reference leaf to match to
                                    if plan.Name == 'Left Breast':    
                                        leafPositions[0][leafNumber] = FlashAnt_jaw  ##x1 bank ant
                                    if plan.Name == 'Right Breast':        
                                        leafPositions[1][leafNumber] = FlashAnt_jaw  ##x2 bank ant
                                segment.LeafPositions = leafPositions
                            
            if beam_set.MachineReference.MachineName == 'Agility':
                with CompositeAction('Shift ant MLCs to ant jaw'):
                    for beam in beam_set.Beams:
                        if beam.Name in ['EA03']:
                            for segment in beam.Segments:
                                leafPositions = segment.LeafPositions
                                for leafNumber in range(79):  ##elekta range should be 80 but leave top one closed so next bit close leafs behinds jaws using this as reference leaf to match to
                                    if plan.Name == 'Left Breast':
                                        leafPositions[0][leafNumber] = FlashAnt_jaw  ##x1 bank ant
                                    if plan.Name == 'Right Breast':
                                        leafPositions[1][leafNumber] = FlashAnt_jaw  ##x2 bank ant               
                                segment.LeafPositions = leafPositions




            ##close leafs outside jaws
            def close_leaves_behind_jaw_for_breast_Elekta():
              for beam in beam_set.Beams:   
                segments = beam.Segments[0]
                leaf_positions = segments.LeafPositions
                jaw = segments.JawPositions
                y1 = jaw[2]
                y2 = jaw[3]
                first_x1 = leaf_positions[0][1]
                last_x1 = leaf_positions[0][79]
                first_x2 = leaf_positions[1][1]
                last_x2 = leaf_positions[1][79]
                # get the last corresponding MLC that is in the field
                mlcY1 = math.floor((y1 + 20) * 2) + 1.0
                mlcY2 = math.ceil ((y2 + 20) * 2)

                # don't forget that mlc 50 is in spot leafPositions[0][49]
                for i in range(0, int(mlcY1 -2)):
                    leaf_positions[0][i] = first_x1
                    leaf_positions[1][i] = first_x2

                for j in range(int(mlcY2 +1), 80):
                    leaf_positions[0][j] = last_x1
                    leaf_positions[1][j] = last_x2
                            
                segments.LeafPositions = leaf_positions


            # FUNCTION CLOSE LEAFS OUTSIDE FIELD for VARIAN machine only### not perfect but shouldnt close leaves inside field
            def close_leaves_behind_jaw_for_breast_Varian():
              for beam in beam_set.Beams:   
                  
                segments = beam.Segments[0]
                leaf_positions = segments.LeafPositions
                jaw = segments.JawPositions
                y1 = jaw[2]
                y2 = jaw[3]
                first_x1 = leaf_positions[0][1]
                last_x1 = leaf_positions[0][59]
                first_x2 = leaf_positions[1][1]
                last_x2 = leaf_positions[1][59]
                # get the last corresponding MLC that is in the field
                mlcY1 = math.floor((y1 + 11) * 2) + 2   ###ig edited. looks ok ## e.g jaw is for example 4 so 11-4 is outer 7cm of leaves to close(if 0.5cm leaves = 14 leaves to close)
                mlcY2 = math.ceil ((y2 + 11) * 3) ### ig edited to 3. looks ok safe.

                # don't forget that mlc 50 is in spot leafPositions[0][49]
                for i in range(0, int(mlcY1 -2)):
                    leaf_positions[0][i] = first_x1
                    leaf_positions[1][i] = first_x2

                for j in range(int(mlcY2 +1), 60):
                    leaf_positions[0][j] = last_x1
                    leaf_positions[1][j] = last_x2
                            
                segments.LeafPositions = leaf_positions

            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                close_leaves_behind_jaw_for_breast_Varian()
            if beam_set.MachineReference.MachineName == 'Agility':
                close_leaves_behind_jaw_for_breast_Elekta()
            
            
            
            ##FOR VARIAN IF TOP MLC LEFT IN FIELD DUE TO FIELD BEING >10.5CM THEN PULL IT OUT TO ANT JAW
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                if beam_set.Beams['VA03'].Segments[0].JawPositions[3] > 10.5:
                    with CompositeAction('Shift top MLCs to ant jaw'):
                        for beam in beam_set.Beams:
                            if beam.Name in ['VA03']: 
                                for segment in beam.Segments:
                                    leafPositions = segment.LeafPositions
                                    for leafNumber in [59]:  ##varian range - TOP MLC IN VARIAN FIELD WILL BE MOVED TO ANT JAW IF NEEDED
                                        if plan.Name == 'Left Breast':    
                                            leafPositions[0][leafNumber] = FlashAnt_jaw  ##x1 bank ant
                                        if plan.Name == 'Right Breast':        
                                            leafPositions[1][leafNumber] = FlashAnt_jaw  ##x2 bank ant
                                    segment.LeafPositions = leafPositions


            ##to ensure min leaf gap of 0.5cm for varian (VA03) lat beam as after flash it may become invalid on mlcs outside field and not compute if min gap violated. i dont think issue with agility process?
            #does both right or left sided varian va03 beams if gap <0.5cm
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                for beam in beam_set.Beams:
                    if beam.Name in ['EA03', 'VA03']:
                        for segment in beam.Segments:
                            leafPositions = segment.LeafPositions
                            for leafNumber in range(59):
                                if plan.Name == 'Right Breast':
                                    #current_gap = abs(leafPositions[1][leafNumber] - leafPositions[0][leafNumber])
                                    current_gap = leafPositions[1][leafNumber] - leafPositions[0][leafNumber]  #ant mlc x2 - postx1 = -0.41
                                    if current_gap < 0:  #negative which means anterior x2 bank is overlapping into bank x1 so need to retract bank x2 by this amount plus 0.5 . eg -0.41
                                        leafPositions[1][leafNumber] = leafPositions[1][leafNumber] + 0.5 + abs(current_gap) # addition 0.5+absolute value gap - eg 0.5+0.41 = 0.91cm increase                                    
                                    if current_gap > 0:
                                        if current_gap < 0.5:
                                            leafPositions[1][leafNumber] = leafPositions[1][leafNumber] + 0.5 - current_gap


                                if plan.Name == 'Left Breast':
                                    current_gap = leafPositions[0][leafNumber] - leafPositions[1][leafNumber]  # eg. -5.57 + -5.9 = 0.33
                                    if current_gap > 0:
                                        if current_gap < 0.5:
                                            leafPositions[0][leafNumber] = leafPositions[0][leafNumber] - 0.5 - current_gap  #so -5.57-0.5-0.33=-6.4
                                    
                                    if current_gap < 0:
                                        if current_gap > -0.5:
                                            leafPositions[0][leafNumber] = leafPositions[0][leafNumber] - 0.5 - current_gap
                            segment.LeafPositions = leafPositions
            #
            #########################################################################################################################################################################################################
            #########################################################################################################################################################################################################
            ##only look at lat beam mlcs as after flash the mlcs outside field may remain open due to end lasf pairs open so we assess of theres no heart mlc in field and if so then conform beamset both med and lat
            
            def conform_mlc_if_no_heart_mlc_Lat():
                mlc_list = []

                for beam in beam_set.Beams:
                    if beam.Name in ['EA03', 'VA03']:
                        for segment in beam.Segments:
                            if plan.Name == 'Left Breast':
                                leaf_positions = segment.LeafPositions[1]
                            if plan.Name == 'Right Breast':
                                leaf_positions = segment.LeafPositions[0]
                            
                            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':        
                                for i in range(10, 46):
                                    mlc_list.append(leaf_positions[i])
                            if beam_set.MachineReference.MachineName == 'Agility':        
                                for i in range(30, 46):
                                    mlc_list.append(leaf_positions[i])        
                                
                            
                max_mlcdiff = abs(max(mlc_list)-min(mlc_list)) 

                if max_mlcdiff < 0.1:  #if mlc differences along back border <0.1cm then likely no heart mlc in field so we can conform mlc to field edges to tidy up
                    no_heartMLC = "True"
                    beam_set.SetLeafPositioningThreshold(LeafPositioningThreshold=0)
                    beam_set.TreatAndProtect()
                    
            conform_mlc_if_no_heart_mlc_Lat()
            ##save
            patient.Save()

        ##move x ant jaw to 2cm flash only if it is less than 2cm
        for beam in beam_set.Beams:
            segments = beam.Segments[0]
            jaw = segments.JawPositions
            if beam.Name in ['EA03', 'VA03']:
                if plan.Name == 'Left Breast':
                    if jaw[0] > FlashAnt_jaw:
                        SortFlashLat()
                if plan.Name == 'Right Breast':
                    if jaw[1] < FlashAnt_jaw:
                        SortFlashLat()
        ######################################################################################################################################################################################################

        #######################################################################################################################################################################################################
        
        ####################################
        #change tec to SMLC
        plan_opt = plan.PlanOptimizations[0]
        opt_parameters = plan_opt.OptimizationParameters
        #beam_set = get_current('BeamSet')
        beam_set.SetTreatmentTechnique(Technique = 'SMLC')
        opt_parameters.TreatmentSetupSettings[0].SegmentConversion.UseConformalSequencing = True


        #create a copy new beamset SMLC and 5#s and same machine
        plan.AddNewBeamSet(Name='copy', ExaminationName=examination.Name, MachineName=machine_name, Modality="Photons", TreatmentTechnique="SMLC", PatientPosition="HeadFirstSupine", NumberOfFractions=15, CreateSetupBeams=False, Comment="")

        #need to set COPIED beamset as current before copying in MED AND LAT beam. need to save before change
        patient.Save()
        beam_set = plan.BeamSets[1]
        beam_set.SetCurrent()

        #now copy over 2 beams(med and lat opens) from beamset 0 into beamset 1
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets[0], BeamsToCopy=[r"VA01"])
            beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets[0], BeamsToCopy=[r"VA03"])
        elif beam_set.MachineReference.MachineName == 'Agility':
            beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets[0], BeamsToCopy=[r"EA01"])
            beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets[0], BeamsToCopy=[r"EA03"])

        #save, make orig active and delete it
        patient.Save()
        beam_set = plan.BeamSets[0]
        beam_set.SetCurrent()
        beam_set.DeleteBeamSet()
        patient.Save()

        #adds the prescription bit to new copied beamset
        plan.BeamSets[0].AddRoiPrescriptionDoseReference(RoiName="PTVp_4000", PrescriptionType="MedianDose", DoseValue=4000, RelativePrescriptionLevel=1.0)
            
        #rename new beamset name to plan name
        plan.BeamSets[0].DicomPlanLabel = plan.Name

        #EDIT ISO NAME IS BE SAME AS PLAN NAME
        plan.BeamSets[0].Beams[0].Isocenter.Annotation.Name = plan.Name

        #################################################

        #copy med and lat beams to create med SMLC and lat SMLC named beams and reorder them correctly
        beam_set = get_current("BeamSet")
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            beam_set.CopyBeam(BeamName=r"VA01")
            beam_set.CopyBeam(BeamName=r"VA03")
        elif beam_set.MachineReference.MachineName == 'Agility':
            beam_set.CopyBeam(BeamName=r"EA01")
            beam_set.CopyBeam(BeamName=r"EA03") 

        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            if plan.Name == 'Left Breast':
                beam_set.Beams['VA2'].Name = r"VA02"
                beam_set.Beams['VA02'].Description = r"VA02 LMED SMLC"
                beam_set.Beams['VA4'].Name = r"VA04"
                beam_set.Beams['VA04'].Description = r"VA04 LLAT SMLC"
            elif plan.Name == 'Right Breast':
                beam_set.Beams['VA2'].Name = r"VA02"
                beam_set.Beams['VA02'].Description = r"VA02 RMED SMLC"
                beam_set.Beams['VA4'].Name = r"VA04"
                beam_set.Beams['VA04'].Description = r"VA04 RLAT SMLC"
            
        if beam_set.MachineReference.MachineName == 'Agility':
            if plan.Name == 'Left Breast':
                beam_set.Beams['EA2'].Name = r"EA02"
                beam_set.Beams['EA02'].Description = r"EA02 LMED SMLC"
                beam_set.Beams['EA4'].Name = r"EA04"
                beam_set.Beams['EA04'].Description = r"EA04 LLAT SMLC" 
            elif plan.Name == 'Right Breast':
                beam_set.Beams['EA2'].Name = r"EA02"
                beam_set.Beams['EA02'].Description = r"EA02 RMED SMLC"
                beam_set.Beams['EA4'].Name = r"EA04"
                beam_set.Beams['EA04'].Description = r"EA04 RLAT SMLC"
            
        #renumber beams and reorder them
        if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
            beam_set.Beams['VA03'].Number = 22
            beam_set.Beams['VA02'].Number = 2
            beam_set.Beams['VA03'].Number = 3
        elif beam_set.MachineReference.MachineName == 'Agility':
            beam_set.Beams['EA03'].Number = 22
            beam_set.Beams['EA02'].Number = 2
            beam_set.Beams['EA03'].Number = 3

        #if sep >27cm then use 10MV on opens only beams[0] and [1]
        if Separation_LB > 25:
            beam_set.Beams[0].BeamQualityId = r"10"
            beam_set.Beams[1].BeamQualityId = r"10"

        #enter 1 MU into SMLC fields now and calc dose
        beam_set.Beams[2].BeamMU = 1
        beam_set.Beams[3].BeamMU = 1

        beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)

        #exclude open beams from opt
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=r"Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=r"Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

        #reset beams to allow opt settings input
        plan.PlanOptimizations[0].ResetOptimization()

        #select Treat margins for the SMLC beams
        beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName = 'PTVp_4000')

        ###need to covert PTV to contour type to enable it to have contours as an object in primary shape
        case.PatientModel.StructureSets[examination.Name].RoiGeometries['PTVp_4000'].SetRepresentation(Representation='Contours')
        
        ######NOW MEASURE CHEST WALL THICKNESS TO DETERMINE IF TREAT MARGIN 2.0 OR 0.4cm USED antererioly on SMLC fields#######
        #######################################RIGHT SIDE CHEST WALL THICKNESS#############################################

        ##need x y z coordinates of most lateral and most medial location of ptvp on slize when z =0. we need center y value of ptvp
        if plan.Name == 'Right Breast':
            #Get POI geometries 
            poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries
            roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
            
            ##add point center of PTVp_2600
            roi_center = roi_geometries['PTVp_4000'].GetCenterOfRoi()
            center_PTVp2600 = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}    ##we use this center of ptvp for height y value roi_center.y
            
            #####now we get the most lateral point x value of ptvp when z = 0
            cwallx_coords = []

            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['PTVp_4000'].PrimaryShape.Contours):
                for coordinate in contour:
                    if coordinate.z == 0 and coordinate.y <= roi_center.y + 0.6 and coordinate.y >= roi_center.y - 0.3:   #on slice 0 gets list of all x values within the center ptv y value +-0.3cm. made 0.6 as error on pt 695449             
                        cwallx_coords.append(coordinate.x)
        #
            cwallLatnew_x = min(cwallx_coords)  ##(for RIGHT breast we then want smallest x which is cloest to lateral side)

            cwallMednew_x = max(cwallx_coords)  ##(for RIGHT breast we then want smallest x which is cloest to medial side)

            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': cwallLatnew_x, 'y': roi_center.y, 'z': 0 }, Name=r"lat cwall", Color="Green", VisualizationDiameter=1, Type="Undefined")  ##lat poi right breast
            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': cwallMednew_x, 'y': roi_center.y, 'z': 0 }, Name=r"med cwall", Color="Green", VisualizationDiameter=1, Type="Undefined")  ##med poi right breast
            
            #measure distance (cm) between two points for rough estimate of thickness of PTV in straight line not tangent
            thickness_PTVp2600 = abs(cwallLatnew_x - cwallMednew_x)
            
            
            #select Treat margins for the SMLC beams
            beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName = 'PTVp_4000')
            
            if thickness_PTVp2600 <= 4.0:
                beam_set.Beams[2].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=2.0, RightMargin=0.4, Roi='PTVp_4000')
                beam_set.Beams[3].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=0.4, RightMargin=2.0, Roi='PTVp_4000')
            elif thickness_PTVp2600 > 4.0:
                beam_set.Beams[2].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=0.4, RightMargin=0.4, Roi='PTVp_4000')
                beam_set.Beams[3].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=0.4, RightMargin=0.4, Roi='PTVp_4000')

        #######################################LEFT SIDE CHEST WALL THICKNESS#############################################

        ##need x y z coordinates of most lateral and most medial location of ptvp on slize when z =0. we need center y value of ptvp
        if plan.Name == 'Left Breast':
            #Get POI geometries 
            poi_geometries = case.PatientModel.StructureSets[examination.Name].PoiGeometries
            roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
            
            ##add point center of PTVp_2600
            roi_center = roi_geometries['PTVp_4000'].GetCenterOfRoi()
            center_PTVp2600 = {'x':roi_center.x, 'y':roi_center.y, 'z':roi_center.z}    ##we use this center of ptvp for height y value roi_center.y
            
            #####now we get the most lateral point x value of ptvp when z = 0
            cwallx_coords = []

            ss = case.PatientModel.StructureSets[examination.Name]
            for [contour_index, contour] in enumerate(ss.RoiGeometries['PTVp_4000'].PrimaryShape.Contours):
                for coordinate in contour:
                    if coordinate.z == 0 and coordinate.y <= roi_center.y + 0.6 and coordinate.y >= roi_center.y - 0.3:   #on slice 0 gets list of all x values within the center ptv y value +-0.3cm             
                        cwallx_coords.append(coordinate.x)
        #
            cwallLatnew_x = max(cwallx_coords)  ##(for LEFT breast we then want biggest x which is cloest to lateral side)

            cwallMednew_x = min(cwallx_coords)  ##(for LEFT breast we then want smallest x which is cloest to medial side)

            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': cwallLatnew_x, 'y': roi_center.y, 'z': 0 }, Name=r"lat cwall", Color="Green", VisualizationDiameter=1, Type="Undefined")  ##lat poi right breast
            case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': cwallMednew_x, 'y': roi_center.y, 'z': 0 }, Name=r"med cwall", Color="Green", VisualizationDiameter=1, Type="Undefined")  ##med poi right breast
            
            #measure distance (cm) between two points for rough estimate of thickness of PTV in straight line not tangent
            thickness_PTVp2600 = abs(cwallLatnew_x - cwallMednew_x)
            
            #select Treat margins for the SMLC beams
            beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName = 'PTVp_4000')
            
            if thickness_PTVp2600 <= 4.0:
                beam_set.Beams[2].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=0.4, RightMargin=2.0, Roi='PTVp_4000')
                beam_set.Beams[3].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=2.0, RightMargin=0.4, Roi='PTVp_4000')
            elif thickness_PTVp2600 > 4.0:
                beam_set.Beams[2].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=0.4, RightMargin=0.4, Roi='PTVp_4000')
                beam_set.Beams[3].SetTreatAndProtectMarginsForBeam(TopMargin=0.4, BottomMargin=0.4, LeftMargin=0.4, RightMargin=0.4, Roi='PTVp_4000')


        ########delete the points once not needed#########
        case.PatientModel.PointsOfInterest['lat cwall'].DeleteRoi()

        case.PatientModel.PointsOfInterest['med cwall'].DeleteRoi()

        #ensure split is removed from the med SMLC beam as default causes the original med beam to be split and we cant change this until after a reset with smlc type. lat and orig med beams are fine.
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[2].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=r"Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

        ################BRING PLANNER TO PLAN OPT TAB##############
        ui.TitleBar.Navigation.MenuItem['Plan optimization'].Button_Plan_optimization.Click() #go to plan opt
        ui.Workspace.TabControl['2D | Image'].TabItem['2D | Image'].Select()
        ui.Workspace.TabControl['DVH'].TabItem['Clinical goals'].Select()
        ui.Workspace.TabControl['Objectives/constraints'].TabItem['Objectives/constraints'].Select()
        
        #optimisation settings
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 1e-7
        plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 40
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 5
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeIntermediateDose = True
        plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True

        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MaxNumberOfSegments = 6
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinSegmentArea = 9
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinSegmentMUPerFraction = 5
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MaxNumberOfSegments = 6
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinNumberOfOpenLeafPairs = 4
        plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinLeafEndSeparation = 2


        ##clinical goals - load template based on what planner selected at start in drop down option
        tpmCG = db.LoadTemplateClinicalGoals(templateName = clicked4.get(),lockMode = 'Read')
        plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=tpmCG)
        
        ##MUST DELETE zzd50 ROI after margins set but before opt, and this ROI is present if change machine MLC is run. not deleting it will result in opt failure as previously we selected all treat margins to it for all beams.
        if 'zzd50' in roi_list:
            case.PatientModel.RegionsOfInterest['zzd50'].DeleteRoi()
            
        #add manual opt functions as issues with loading templates source/root
        with CompositeAction('Add optimization function'):

          retval_0 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVp_4000", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = 3900

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 1

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_1 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVp_4000", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[1].DoseFunctionParameters.DoseLevel = 4100

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_2 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVp_4000", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[2].DoseFunctionParameters.DoseLevel = 4000
          
          plan.PlanOptimizations[0].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight = 1

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_3 = plan.PlanOptimizations[0].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName=r"Skin", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[3].DoseFunctionParameters.HighDoseLevel = 4000

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[3].DoseFunctionParameters.LowDoseLevel = 3500

          plan.PlanOptimizations[0].Objective.ConstituentFunctions[3].DoseFunctionParameters.LowDoseDistance = 0.1

          # CompositeAction ends


        ##set color map and 4000 ref in Gy
        import clr
        clr.AddReference('System.Drawing')
        import System.Drawing

        #define coloir table
        dose_color_table = case.CaseSettings.DoseColorMap.ColorTable

        # Create a color from ARGB-values.
        color_0percent = System.Drawing.Color.FromArgb(0,0,0,0)
        color_25percent = System.Drawing.Color.FromArgb(255,128,128,192)
        color_50percent = System.Drawing.Color.FromArgb(255,128,255,255)
        color_60percent = System.Drawing.Color.FromArgb(255,255,0,128)
        color_70percent = System.Drawing.Color.FromArgb(255,255,255,0)
        color_80percent = System.Drawing.Color.FromArgb(255,0,128,128)
        color_90percent = System.Drawing.Color.FromArgb(255,255,128,0)
        color_95percent = System.Drawing.Color.FromArgb(255,0,0,255)
        color_100percent = System.Drawing.Color.FromArgb(255,0,255,0)
        color_105percent = System.Drawing.Color.FromArgb(255,255,0,0)
        color_107percent = System.Drawing.Color.FromArgb(255,0,255,255)
        color_110percent = System.Drawing.Color.FromArgb(255,128,0,0)

        # Add this color at 10 percent level in the dose color table.
        dose_color_table[0] = color_0percent
        dose_color_table[25] = color_25percent
        dose_color_table[50] = color_50percent
        dose_color_table[60] = color_60percent
        dose_color_table[70] = color_70percent
        dose_color_table[80] = color_80percent
        dose_color_table[90] = color_90percent
        dose_color_table[95] = color_95percent
        dose_color_table[100] = color_100percent
        dose_color_table[105] = color_105percent
        dose_color_table[107] = color_107percent
        dose_color_table[110] = color_110percent

        # Set the new color table.
        case.CaseSettings.DoseColorMap.ColorTable = dose_color_table

        case.CaseSettings.DoseColorMap.ColorMapReferenceType = 'ReferenceValue'
        case.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
        case.CaseSettings.DoseColorMap.ReferenceValue = 4000
        ########################################################################################

        #save before opt in case of crash during opt - have a messge if crashes 
        patient.Save()

        #should i make opens 240MU each at start or not? does it make a dif?

        #run opt x 1
        try:
            plan.PlanOptimizations[0].RunOptimization()
        except:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot optimise - please continue manually and check if min leaf gap parameter needs lowering" + str(sys.path))
            exit()

        ##scale then
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)

        #sort weights and clamp # cant find if this is scriptable to set or clamp so instead get total plan MU and give weights of 37.5% to each opens and 12.5% to each smlc beam. this will round beams also auto to 2 dp
        plan = get_current("Plan")
        beam_set = get_current("BeamSet")
        Plan_MU = beam_set.Beams[0].BeamMU + beam_set.Beams[1].BeamMU + beam_set.Beams[2].BeamMU + beam_set.Beams[3].BeamMU
        beam_set.Beams[0].BeamMU = Plan_MU * 0.3875  ##MED OPEN
        beam_set.Beams[2].BeamMU = Plan_MU * 0.1125  ##MED SMLC
        beam_set.Beams[1].BeamMU = Plan_MU * 0.3875  ##LAT OPEN
        beam_set.Beams[3].BeamMU = Plan_MU * 0.1125  ##LAT SMLC

        ##scale off then
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=False)

        #reopt again
        patient.Save()
        plan.PlanOptimizations[0].RunOptimization()

        ##scale on then
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)

        #now get stats for ptv - v90, v95, v105, v107, d0.5cc    #get stats for skin-ptv - v27.8, d0.5cc
        nr_fractions  = beam_set.FractionationPattern.NumberOfFractions
        dose_value_v95 = beam_set.Prescription.PrimaryPrescriptionDoseReference.DoseValue/nr_fractions*0.95
        dose_value_v105 = beam_set.Prescription.PrimaryPrescriptionDoseReference.DoseValue/nr_fractions*1.05
        dose_value_v107 = beam_set.Prescription.PrimaryPrescriptionDoseReference.DoseValue/nr_fractions*1.07
        dose_value_v110 = beam_set.Prescription.PrimaryPrescriptionDoseReference.DoseValue/nr_fractions*1.10

        PTV_v95 = beam_set.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='PTVp_4000', DoseValues=[dose_value_v95])*100  ##this gets v24.7 in 5# = 494 * 100 = 95.22 (as was given as 0.9522) # tested in console
        PTV_v105 = beam_set.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='PTVp_4000', DoseValues=[dose_value_v105])*100
        PTV_v107 = beam_set.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='PTVp_4000', DoseValues=[dose_value_v107])*100

        #get total volume first of PTVp_2600 in cc, then get relative v28.6 in %, then multiply by volume cc to get absolute cc #tested console
        PTV_volume = plan.TreatmentCourse.TotalDose.GetDoseGridRoi(RoiName = 'PTVp_4000').RoiVolumeDistribution.TotalVolume
        PTV_v110_rel = beam_set.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='PTVp_4000', DoseValues=[dose_value_v110])
        PTV_v110_abs = PTV_v110_rel[0]*PTV_volume

        #Skin-PTV_v107cc # tested console gives absolute volume result
        SkinPTV_volume = plan.TreatmentCourse.TotalDose.GetDoseGridRoi(RoiName = 'Skin-PTVAndAx').RoiVolumeDistribution.TotalVolume
        SkinPTV_v107_rel = beam_set.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='Skin-PTVAndAx', DoseValues=[dose_value_v107])
        SkinPTV_v107_abs = SkinPTV_v107_rel[0]*SkinPTV_volume

        #Skin-PTV_v110cc #tested console gives absolute volume result
        SkinPTV_volume = plan.TreatmentCourse.TotalDose.GetDoseGridRoi(RoiName = 'Skin-PTVAndAx').RoiVolumeDistribution.TotalVolume
        SkinPTV_v110_rel = beam_set.FractionDose.GetRelativeVolumeAtDoseValues(RoiName='Skin-PTVAndAx', DoseValues=[dose_value_v110])
        SkinPTV_v110_abs = SkinPTV_v110_rel[0]*SkinPTV_volume

        ###############################################LOOPING THORUGH ALL CFS AND CHANGING MAYBE CHANGE########################
        #check plan pass or fail and change optimisation function weights as needed 
        if PTV_v95[0] < 90:
            plan.PlanOptimizations[0].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight += 5
        if 90 <= PTV_v95[0] <= 95:
            plan.PlanOptimizations[0].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight += 3
        if PTV_v105[0] > 50 or PTV_v107[0] > 2 or PTV_v110_abs > 0.5:
            plan.PlanOptimizations[0].Objective.ConstituentFunctions[1].DoseFunctionParameters.Weight += 2
        if SkinPTV_v107_abs > 2.0 or SkinPTV_v110_abs > 0.5:
            plan.PlanOptimizations[0].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight += 1
            
        ##scale off then
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=False)

        #reopt
        patient.Save()
        plan.PlanOptimizations[0].RunOptimization()

        #autoscale on only when likely that plan is met as may not scale if too cold or hot
        patient.Save()
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)
        patient.Save()

        #LIMITS SMLC Y JAWS TO BE NO LARGER THAN THE MEDIAL OPEN Y JAWS. could not get segment loop working so instead i address each segment in SMLC beams 
        #max y jaws for medial open beam
        max_y1 = beam_set.Beams[0].Segments[0].JawPositions[2]  #y1 = -10 on open med
        max_y2 = beam_set.Beams[0].Segments[0].JawPositions[3]  #y2 = 10 on open med

        for beam in beam_set.Beams:
            segments = beam.Segments[0]
            jaw = segments.JawPositions
            if beam.Name in ['EA02', 'EB02', 'EC02', 'ED02', 'EE02', 'EA04', 'EB04', 'EC04', 'ED04', 'EE04', 'VA02', 'VB02', 'VC02', 'VD02', 'VE02', 'VA04', 'VB04', 'VC04', 'VD04', 'VE04']: 
                if jaw[2] < max_y1:
                    jaw[2] = max_y1
                if jaw[3] > max_y2: 
                    jaw[3] = max_y2
            segments.JawPositions = jaw
            
        #
        for beam in beam_set.Beams:
            try:
                segments = beam.Segments[1]
                jaw = segments.JawPositions
                if beam.Name in ['EA02', 'EB02', 'EC02', 'ED02', 'EE02', 'EA04', 'EB04', 'EC04', 'ED04', 'EE04', 'VA02', 'VB02', 'VC02', 'VD02', 'VE02', 'VA04', 'VB04', 'VC04', 'VD04', 'VE04']: 
                    if jaw[2] < max_y1:
                        jaw[2] = max_y1
                    if jaw[3] > max_y2: 
                        jaw[3] = max_y2
                segments.JawPositions = jaw
            except:
                pass
                
                
                
        for beam in beam_set.Beams:
            try:
                segments = beam.Segments[2]
                jaw = segments.JawPositions
                if beam.Name in ['EA02', 'EB02', 'EC02', 'ED02', 'EE02', 'EA04', 'EB04', 'EC04', 'ED04', 'EE04', 'VA02', 'VB02', 'VC02', 'VD02', 'VE02', 'VA04', 'VB04', 'VC04', 'VD04', 'VE04']: 
                    if jaw[2] < max_y1:
                        jaw[2] = max_y1
                    if jaw[3] > max_y2: 
                        jaw[3] = max_y2
                segments.JawPositions = jaw
            except:
                pass
                
        for beam in beam_set.Beams:
            try:
                segments = beam.Segments[3]
                jaw = segments.JawPositions
                if beam.Name in ['EA02', 'EB02', 'EC02', 'ED02', 'EE02', 'EA04', 'EB04', 'EC04', 'ED04', 'EE04', 'VA02', 'VB02', 'VC02', 'VD02', 'VE02', 'VA04', 'VB04', 'VC04', 'VD04', 'VE04']: 
                    if jaw[2] < max_y1:
                        jaw[2] = max_y1
                    if jaw[3] > max_y2: 
                        jaw[3] = max_y2
                segments.JawPositions = jaw
            except:
                pass
                
        for beam in beam_set.Beams:
            try:
                segments = beam.Segments[4]
                jaw = segments.JawPositions
                if beam.Name in ['EA02', 'EB02', 'EC02', 'ED02', 'EE02', 'EA04', 'EB04', 'EC04', 'ED04', 'EE04', 'VA02', 'VB02', 'VC02', 'VD02', 'VE02', 'VA04', 'VB04', 'VC04', 'VD04', 'VE04']: 
                    if jaw[2] < max_y1:
                        jaw[2] = max_y1
                    if jaw[3] > max_y2: 
                        jaw[3] = max_y2
                segments.JawPositions = jaw
            except:
                pass
                
        for beam in beam_set.Beams:
            try:
                segments = beam.Segments[5]
                jaw = segments.JawPositions
                if beam.Name in ['EA02', 'EB02', 'EC02', 'ED02', 'EE02', 'EA04', 'EB04', 'EC04', 'ED04', 'EE04', 'VA02', 'VB02', 'VC02', 'VD02', 'VE02', 'VA04', 'VB04', 'VC04', 'VD04', 'VE04']: 
                    if jaw[2] < max_y1:
                        jaw[2] = max_y1
                    if jaw[3] > max_y2: 
                        jaw[3] = max_y2
                segments.JawPositions = jaw
            except:
                pass

        #NOW CALC FINAL DOSE AGAIN IF JAWS CHANGED. IF NO JAWS CHANGED IT WILL STILL BE FINE
        beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)
        patient.Save()

        ##TURN OFF ROIS APART FROM PTV
        for roi in rois:
            patient.SetRoiVisibility(RoiName=roi.Name, IsVisible=False)
        
        patient.SetRoiVisibility(RoiName='PTVp_4000', IsVisible=True)

        if plan.Name == 'Right Breast':
            patient.SetPoiVisibility(PoiName='Med border right breast', IsVisible=False)
            patient.SetPoiVisibility(PoiName='Lat border right breast', IsVisible=False)
        if plan.Name == 'Left Breast':
            patient.SetPoiVisibility(PoiName='Med border left breast', IsVisible=False)
            patient.SetPoiVisibility(PoiName='Lat border left breast', IsVisible=False)
            
            
        ##################sorts final beam labels as per course number###############################
        if clicked.get() == "Course 1":
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                if plan.Name == 'Left Breast':
                    beam_set.Beams[0].Name = r"VA01"
                    beam_set.Beams['VA01'].Description = r"VA01 LMED"
                    beam_set.Beams[1].Name = r"VA03"
                    beam_set.Beams['VA03'].Description = r"VA03 LLAT"
                    beam_set.Beams[2].Name = r"VA02"
                    beam_set.Beams['VA02'].Description = r"VA02 LMED SMLC"
                    beam_set.Beams[3].Name = r"VA04"
                    beam_set.Beams['VA04'].Description = r"VA04 LLAT SMLC"
                if plan.Name == 'Right Breast':
                    beam_set.Beams[0].Name = r"VA01"
                    beam_set.Beams['VA01'].Description = r"VA01 RMED"
                    beam_set.Beams[1].Name = r"VA03"
                    beam_set.Beams['VA03'].Description = r"VA03 RLAT"
                    beam_set.Beams[2].Name = r"VA02"
                    beam_set.Beams['VA02'].Description = r"VA02 RMED SMLC"
                    beam_set.Beams[3].Name = r"VA04"
                    beam_set.Beams['VA04'].Description = r"VA04 RLAT SMLC"
            if beam_set.MachineReference.MachineName == 'Agility':
                if plan.Name == 'Left Breast':
                    beam_set.Beams[0].Name = r"EA01"
                    beam_set.Beams['EA01'].Description = r"EA01 LMED"
                    beam_set.Beams[1].Name = r"EA03"
                    beam_set.Beams['EA03'].Description = r"EA03 LLAT"
                    beam_set.Beams[2].Name = r"EA02"
                    beam_set.Beams['EA02'].Description = r"EA02 LMED SMLC"
                    beam_set.Beams[3].Name = r"EA04"
                    beam_set.Beams['EA04'].Description = r"EA04 LLAT SMLC"
                if plan.Name == 'Right Breast':
                    beam_set.Beams[0].Name = r"EA01"
                    beam_set.Beams['EA01'].Description = r"EA01 RMED"
                    beam_set.Beams[1].Name = r"EA03"
                    beam_set.Beams['EA03'].Description = r"EA03 RLAT"
                    beam_set.Beams[2].Name = r"EA02"
                    beam_set.Beams['EA02'].Description = r"EA02 RMED SMLC"
                    beam_set.Beams[3].Name = r"EA04"
                    beam_set.Beams['EA04'].Description = r"EA04 RLAT SMLC"
        if clicked.get() == "Course 2":
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                if plan.Name == 'Left Breast':
                    beam_set.Beams[0].Name = r"VB01"
                    beam_set.Beams['VB01'].Description = r"VB01 LMED"
                    beam_set.Beams[1].Name = r"VB03"
                    beam_set.Beams['VB03'].Description = r"VB03 LLAT"
                    beam_set.Beams[2].Name = r"VB02"
                    beam_set.Beams['VB02'].Description = r"VB02 LMED SMLC"
                    beam_set.Beams[3].Name = r"VB04"
                    beam_set.Beams['VB04'].Description = r"VB04 LLAT SMLC"
                if plan.Name == 'Right Breast':
                    beam_set.Beams[0].Name = r"VB01"
                    beam_set.Beams['VB01'].Description = r"VB01 RMED"
                    beam_set.Beams[1].Name = r"VB03"
                    beam_set.Beams['VB03'].Description = r"VB03 RLAT"
                    beam_set.Beams[2].Name = r"VB02"
                    beam_set.Beams['VB02'].Description = r"VB02 RMED SMLC"
                    beam_set.Beams[3].Name = r"VB04"
                    beam_set.Beams['VB04'].Description = r"VB04 RLAT SMLC"
            if beam_set.MachineReference.MachineName == 'Agility':
                if plan.Name == 'Left Breast':
                    beam_set.Beams[0].Name = r"EB01"
                    beam_set.Beams['EB01'].Description = r"EB01 LMED"
                    beam_set.Beams[1].Name = r"EB03"
                    beam_set.Beams['EB03'].Description = r"EB03 LLAT"
                    beam_set.Beams[2].Name = r"EB02"
                    beam_set.Beams['EB02'].Description = r"EB02 LMED SMLC"
                    beam_set.Beams[3].Name = r"EB04"
                    beam_set.Beams['EB04'].Description = r"EB04 LLAT SMLC"
                if plan.Name == 'Right Breast':
                    beam_set.Beams[0].Name = r"EB01"
                    beam_set.Beams['EB01'].Description = r"EB01 RMED"
                    beam_set.Beams[1].Name = r"EB03"
                    beam_set.Beams['EB03'].Description = r"EB03 RLAT"
                    beam_set.Beams[2].Name = r"EB02"
                    beam_set.Beams['EB02'].Description = r"EB02 RMED SMLC"
                    beam_set.Beams[3].Name = r"EB04"
                    beam_set.Beams['EB04'].Description = r"EB04 RLAT SMLC"
        if clicked.get() == "Course 3":
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                if plan.Name == 'Left Breast':
                    beam_set.Beams[0].Name = r"VC01"
                    beam_set.Beams['VC01'].Description = r"VC01 LMED"
                    beam_set.Beams[1].Name = r"VC03"
                    beam_set.Beams['VC03'].Description = r"VC03 LLAT"
                    beam_set.Beams[2].Name = r"VC02"
                    beam_set.Beams['VC02'].Description = r"VC02 LMED SMLC"
                    beam_set.Beams[3].Name = r"VC04"
                    beam_set.Beams['VC04'].Description = r"VC04 LLAT SMLC"
                if plan.Name == 'Right Breast':
                    beam_set.Beams[0].Name = r"VC01"
                    beam_set.Beams['VC01'].Description = r"VC01 RMED"
                    beam_set.Beams[1].Name = r"VC03"
                    beam_set.Beams['VC03'].Description = r"VC03 RLAT"
                    beam_set.Beams[2].Name = r"VC02"
                    beam_set.Beams['VC02'].Description = r"VC02 RMED SMLC"
                    beam_set.Beams[3].Name = r"VC04"
                    beam_set.Beams['VC04'].Description = r"VC04 RLAT SMLC"
            if beam_set.MachineReference.MachineName == 'Agility':
                if plan.Name == 'Left Breast':
                    beam_set.Beams[0].Name = r"EC01"
                    beam_set.Beams['EC01'].Description = r"EC01 LMED"
                    beam_set.Beams[1].Name = r"EC03"
                    beam_set.Beams['EC03'].Description = r"EC03 LLAT"
                    beam_set.Beams[2].Name = r"EC02"
                    beam_set.Beams['EC02'].Description = r"EC02 LMED SMLC"
                    beam_set.Beams[3].Name = r"EC04"
                    beam_set.Beams['EC04'].Description = r"EC04 LLAT SMLC"
                if plan.Name == 'Right Breast':
                    beam_set.Beams[0].Name = r"EC01"
                    beam_set.Beams['EC01'].Description = r"EC01 RMED"
                    beam_set.Beams[1].Name = r"EC03"
                    beam_set.Beams['EC03'].Description = r"EC03 RLAT"
                    beam_set.Beams[2].Name = r"EC02"
                    beam_set.Beams['EC02'].Description = r"EC02 RMED SMLC"
                    beam_set.Beams[3].Name = r"EC04"
                    beam_set.Beams['EC04'].Description = r"EC04 RLAT SMLC"   

        patient.Save()
        
        #################################################################################################################################
        #pause script for review of tangent plan to 40Gy. once happy then resume script.
        
        ##prompts use to check rois. the user can then continue script from left lower panel when happy or stop it
        await_user_input("Please review the 40Gy tangent plan now and make any adjustments.\n\nOnce happy please click resume script at the bottom left of the Scripting Menu")
        
        ###################################################################################################################################################
        ###BRING BACK TO PLAN DESIGN TAB#######
        ui.TitleBar.Navigation.MenuItem['Plan design'].Button_Plan_design.Click() #go to plan design
        ui.TabControl_Modules.TabItem['Plan setup'].Button_Plan_setup.Click()  ##plansetup tab
        ui.Workspace.TabControl['Plan'].TabItem['Beams'].Select()   ##beams tab
        
        #tangents gantry med, lat, coll angles etc
        Med_gantry = beam_set.Beams[0].GantryAngle
        Lat_gantry = beam_set.Beams[1].GantryAngle
        iso_x = beam_set.Beams[0].Isocenter.Position.x
        iso_y = beam_set.Beams[0].Isocenter.Position.y
        iso_z = beam_set.Beams[0].Isocenter.Position.z
        iso_colour = beam_set.Beams[0].Isocenter.Annotation.DisplayColor
     
        ####add new VMAT beam set
        plan.AddNewBeamSet(Name='VMAT', ExaminationName=examination.Name, MachineName=machine_name, Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=15, CreateSetupBeams=False, Comment="")
        
        #SET BEASMET VMAT AS PRIMARY
        patient.Save()
        beam_set = plan.BeamSets[1]
        beam_set.SetCurrent()
        
        #add beamset background dependancy
        
        plan.UpdateDependency(DependentBeamSetName='VMAT', BackgroundBeamSetName=plan.Name, DependencyUpdate='CreateDependency')
        
        #add px
        beam_set.AddRoiPrescriptionDoseReference(RoiName="PTVp_4800", PrescriptionType="MedianDose", DoseValue=800, RelativePrescriptionLevel=1.0)
        
        
        #add beam
        if plan.Name =='Left Breast':
            beam_set.CreateArcBeam(ArcStopGantryAngle=Lat_gantry, ArcRotationDirection="Clockwise", BeamQualityId=r"6", IsocenterData={ 'Position': { 'x': iso_x, 'y': iso_y, 'z': iso_z }, 'NameOfIsocenterToRef': plan.Name, 'Name': 'Left BreastV', 'Color': iso_colour }, Name=r"EA05", Description=r"EA05 VMAT", GantryAngle=Med_gantry, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=10)
        if plan.Name =='Right Breast':
            beam_set.CreateArcBeam(ArcStopGantryAngle=Lat_gantry, ArcRotationDirection="CounterClockwise", BeamQualityId=r"6", IsocenterData={ 'Position': { 'x': iso_x, 'y': iso_y, 'z': iso_z }, 'NameOfIsocenterToRef': plan.Name, 'Name': 'Right BreastV', 'Color': iso_colour }, Name=r"EA05", Description=r"EA05 VMAT", GantryAngle=Med_gantry, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=10)

        ##number beam as 5
        beam_set.Beams[0].Number = 5
        
        ##add bolus to beam if needed - if in list as previously deleted it if was empty
        if 'zzPlanning Bolus' in roi_list:
            for Beams in beam_set.Beams:
                Beams.SetBolus(BolusName=r"zzPlanning Bolus")
        
        
        ##set roi treat margin 5mm
        #select Treat margins for the VMAT beams
        beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName = 'PTVp_4800')
        beam_set.Beams[0].SetTreatAndProtectMarginsForBeam(TopMargin=0.5, BottomMargin=0.5, LeftMargin=0.5, RightMargin=0.5, Roi='PTVp_4800')
        
        
        ###BRING PLANNER TO PLAN OPT TAB and 2d view on to see slice############

        ui.TitleBar.Navigation.MenuItem['Plan optimization'].Button_Plan_optimization.Click() #go to plan opt
        ui.Workspace.TabControl['2D | Image'].TabItem['2D | Image'].Select()
        ui.Workspace.TabControl['DVH'].TabItem['Clinical goals'].Select()
        ui.Workspace.TabControl['Objectives/constraints'].TabItem['Objectives/constraints'].Select()
        ############################################
        
        
        ##set opt settings
        #optimisation settings
        plan.PlanOptimizations[1].OptimizationParameters.Algorithm.OptimalityTolerance = 1e-7
        plan.PlanOptimizations[1].OptimizationParameters.Algorithm.MaxNumberOfIterations = 50
        plan.PlanOptimizations[1].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 7
        plan.PlanOptimizations[1].OptimizationParameters.DoseCalculation.ComputeIntermediateDose = False
        plan.PlanOptimizations[1].OptimizationParameters.DoseCalculation.ComputeFinalDose = True
        
        #add optimisation functions
        with CompositeAction('Add optimization function'):

          retval_0 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MinDose", RoiName=r"PTVp_4800", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = 4790

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 10

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_1 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"PTVp_4800", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.DoseLevel = 4810

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[1].DoseFunctionParameters.Weight = 10

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_2 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="UniformDose", RoiName=r"PTVp_4800", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.DoseLevel = 4800

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[2].DoseFunctionParameters.Weight = 10

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_3 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="DoseFallOff", RoiName=r"Skin-PTVAndAx", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.HighDoseLevel = 4800

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.LowDoseLevel = 2400

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.LowDoseDistance = 0.8

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[3].DoseFunctionParameters.Weight = 5

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_4 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxEud", RoiName=r"Heart", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[4].DoseFunctionParameters.DoseLevel = 1300

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_5 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRing1_SIB", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.DoseLevel = 4560

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[5].DoseFunctionParameters.Weight = 15

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_6 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRing2_SIB", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.DoseLevel = 4400

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[6].DoseFunctionParameters.Weight = 100

          # CompositeAction ends 


        with CompositeAction('Add optimization function'):

          retval_7 = plan.PlanOptimizations[1].AddOptimizationFunction(FunctionType="MaxDose", RoiName=r"zzRing3_SIB", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeams=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[7].DoseFunctionParameters.DoseLevel = 4280

          plan.PlanOptimizations[1].Objective.ConstituentFunctions[7].DoseFunctionParameters.Weight = 500

          # CompositeAction ends 
        
        
        ##set color map and 2600 ref in Gy
        import clr
        clr.AddReference('System.Drawing')
        import System.Drawing

        #define coloir table
        dose_color_table = case.CaseSettings.DoseColorMap.ColorTable

        # Create a color from ARGB-values.
        color_0percent = System.Drawing.Color.FromArgb(0,0,0,0)
        color_25percent = System.Drawing.Color.FromArgb(255,128,128,192)
        color_50percent = System.Drawing.Color.FromArgb(255,128,255,255)
        color_60percent = System.Drawing.Color.FromArgb(255,255,0,128)
        color_70percent = System.Drawing.Color.FromArgb(255,255,255,0)
        color_79166percent = System.Drawing.Color.FromArgb(255,0,0,255)  #v38Gy blue
        color_8916percent = System.Drawing.Color.FromArgb(255,0,255,255) #v42.8Gy sky blue
        color_90percent = System.Drawing.Color.FromArgb(255,255,128,0)
        color_9166percent = System.Drawing.Color.FromArgb(255,128,0,0)  #v44Gy maroon
        color_95percent = System.Drawing.Color.FromArgb(255,165,0)  #V45.6 orange
        color_100percent = System.Drawing.Color.FromArgb(255,0,255,0)  #V48Gy green
        color_105percent = System.Drawing.Color.FromArgb(255,255,0,0)
        color_107percent = System.Drawing.Color.FromArgb(255,0,255,255)
        color_110percent = System.Drawing.Color.FromArgb(255,128,0,0)

        # Add this color at 10 percent level in the dose color table.
        dose_color_table[0] = color_0percent
        dose_color_table[25] = color_25percent
        dose_color_table[50] = color_50percent
        dose_color_table[60] = color_60percent
        dose_color_table[70] = color_70percent
        dose_color_table[79.166] = color_79166percent
        dose_color_table[89.16] = color_8916percent
        dose_color_table[90] = color_90percent
        dose_color_table[91.66] = color_9166percent
        dose_color_table[95] = color_95percent
        dose_color_table[100] = color_100percent
        dose_color_table[105] = color_105percent
        dose_color_table[107] = color_107percent
        dose_color_table[110] = color_110percent

        # Set the new color table.
        case.CaseSettings.DoseColorMap.ColorTable = dose_color_table

        case.CaseSettings.DoseColorMap.ColorMapReferenceType = 'ReferenceValue'
        case.CaseSettings.DoseColorMap.PresentationType = 'Absolute'
        case.CaseSettings.DoseColorMap.ReferenceValue = 4800
        ########################################################################################
        
        
        #start opt
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=False)      
        plan.PlanOptimizations[1].RunOptimization()
        patient.Save()
        
        ##opt again
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=False)
        
        plan.PlanOptimizations[1].RunOptimization()
        beam_set.SetAutoScaleToPrimaryPrescription(AutoScale=True)
                
            
        #sort vmat beam name
        if clicked.get() == "Course 1":
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                beam_set.Beams[0].Name = r"VA05"
                beam_set.Beams['VA05'].Description = r"VA05 VMAT"
            if beam_set.MachineReference.MachineName == 'Agility':
                beam_set.Beams[0].Name = r"EA05"
                beam_set.Beams['EA05'].Description = r"EA05 VMAT"
        if clicked.get() == "Course 2":
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                beam_set.Beams[0].Name = r"VB05"
                beam_set.Beams['VB05'].Description = r"VB05 VMAT"
            if beam_set.MachineReference.MachineName == 'Agility':
                beam_set.Beams[0].Name = r"EB05"
                beam_set.Beams['EB05'].Description = r"EB05 VMAT"
        if clicked.get() == "Course 3":
            if beam_set.MachineReference.MachineName == 'TrueBeamSTx':
                beam_set.Beams[0].Name = r"VC05"
                beam_set.Beams['VC05'].Description = r"VC05 VMAT"
            if beam_set.MachineReference.MachineName == 'Agility':
                beam_set.Beams[0].Name = r"EC05"
                beam_set.Beams['EC05'].Description = r"EC05 VMAT"           
                    
        ##sort plan name
        if plan.Name == 'Left Breast':
            plan.Name = 'L_Breast SIB'
            plan.BeamSets[0].DicomPlanLabel = plan.Name
            
        if plan.Name == 'Right Breast':
            plan.Name = 'R_Breast SIB'
            plan.BeamSets[0].DicomPlanLabel = plan.Name           
        #turn on ptv48 visible
        patient.SetRoiVisibility(RoiName='PTVp_4800', IsVisible=True)
        
        ###############################################################################
        ##some reason need to update some geo for below ROIs although this doesnt change their geoemetry.
        case.PatientModel.RegionsOfInterest['PTVp_4000-PTVp_4800_DVH'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

        case.PatientModel.RegionsOfInterest['PTVp_4000-PTVp_4800_DVH+1cm'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto") 

        case.PatientModel.RegionsOfInterest['Skin-PTVAndAx'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

        case.PatientModel.RegionsOfInterest['zzRing3_SIB'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
        
        ##update dose stats also for dvh
        plan.TreatmentCourse.TotalDose.UpdateDoseGridStructures()
        #pt save
        patient.Save()
        
        ##function to do if planning bolus on beams - tidy up
        def Bolus_Tidy():
            #set beamsset 0 as current 
            patient.Save()
            beam_set = plan.BeamSets[0]
            beam_set.SetCurrent()
                    
            ##remove bolus from the beamsset
            for Beams in beam_set.Beams:
                Beams.SetBolus(BolusName=r"")
                
            ##recalc the beamsset with no bolus
            beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)

            #change to beamset1
            patient.Save()
            beam_set = plan.BeamSets[1]
            beam_set.SetCurrent()

            ##remove the bolus
            for Beams in beam_set.Beams:
                Beams.SetBolus(BolusName=r"")
                
            ##recalc the vMat beam_set with no bolus
            beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False)

            ##change px roi to ptv48 dvh # in12a this adds another one on top so need to edit or delete original first
            beam_set.DeletePrimaryPrescription()
            beam_set.AddRoiPrescriptionDoseReference(RoiName="PTVp_4800_DVH", PrescriptionType="MedianDose", DoseValue=800, RelativePrescriptionLevel=1.0)
            

        #if bolus here then will pauze for planner to review/adjust and then can resume to sort bolus and prescription
        rois = case.PatientModel.RegionsOfInterest 
        roi_list = []
            
        for roi in rois:
            roi_list.append(roi.Name)
            
        if 'zzPlanning Bolus' in roi_list:
            await_user_input("Please review the plan and optimise more if needed\n\nOnce happy please click resume at the bottom left of the Scripting Menu and this will re compute without planning bolus and scale to PTVp_4800_DVH")
            Bolus_Tidy()
        else:
            pass
        
        #get planner initials and add to plan
        patient.Save()
        
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
            MyFileName = patient.PatientID + '_SIB_' + str(staff_id) + '.txt'
            file = open(MyFileName, "w") # write mode over writes
            file.write("SIB Script ran - start time: " + str(startTime)
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

        messagebox.showinfo('Auto Plan Breast v' + str(script_version), 'Script complete. I hope it helped!' + "\n" + "\n" + "ANT FSD AT TATTOOS" + ": " + str(ANT_FSDATTATTOOS1) + "cm" + "\n" + "\n" + "SET ANT FSD" + ": " + str(SET_ANTFSD1) + "cm" + "\n" + "\n" + "Med tattoo to field edge" + ": " + str(Med_tattoo_to_field_edge) + "cm" + "\n" + "\n" + "Lat tattoo to field edge" + ": " + str(Lat_tattoo_to_field_edge) + "cm")

        window.deiconify()
        window.destroy()
        window.quit()
        
        top.destroy()
        ######################################################################################################################################
        
        
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
    drop2 = OptionMenu(top, clicked2, "Agility", "TrueBeamSTx" )
    #drop2.pack()
    drop2.place(x=310, y=50)

    #drop down box to pick clinical goal template
    db = get_current("PatientDB")
    CGs_list = []
    #only see those with Breast in Name and is approved
    for CGs in db.GetClinicalGoalTemplateInfo():
        if "Breast" in (CGs["Name"]) or "breast" in (CGs["Name"]):
            if "48" in (CGs["Name"]):
                if (CGs["IsApproved"] == True):
                    CGs_list.append(CGs["Name"])
                
    clicked4 = StringVar()
    clicked4.set("Select Clinical Goal Template")

    drop4 = OptionMenu(top, clicked4, *CGs_list)
    drop4.place(x=550, y=50)

    ##button for sib breast 
    myButton2 = Button(top, text="Start SIB BREAST Plan 48Gy/15F", command=autoplanSIB1)

    ##cancel button
    butt2 = Button(top, text = 'Cancel', command = Button_pressed2)

    myButton2.place(x=150, y=150)

    butt2.place(x=500, y=150)

    top.mainloop()
