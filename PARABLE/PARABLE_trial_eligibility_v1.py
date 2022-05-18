import math
from connect import *
import connect, ctypes, sys
from tkinter import *
from tkinter import messagebox
import os
#import numpy as np

#written by Ian Gleeson
#runs in CPython 3.6 64bit
#Raystattion 10A
script_version = 1.00
script_name = 'PARABLE Trial Eligibility'
    
###########next buttons to select course and then autoplan
root = Tk()
root.title("PARABLE Trial Eligibility v" + str(script_version))
mycolour = '#%02x%02x%02x' % (50, 50, 50)
myorange = '#%02x%02x%02x' % (255, 140, 0)
root.configure(background = mycolour)
root.geometry("860x200")
######add label#######################
lbl1 = Label(root, text='This script will determine PARABLE trial eligibility based on cardiac risk, plan mean heart dose and patient age as per Table A1 in PARABLE RTQA pack')
lbl1.place(x=65, y =5)
lbl1.configure(background = mycolour, fg = "white", justify=CENTER)
######
lbl12 = Label(root, text='* Risk factors include: pre existing cardiac or circulatory disease, diabetes, COPD, BMI >30 kg/m2, smoking (long term continuous within previous year)')
lbl12.place(x=10, y =140)
lbl12.configure(background = mycolour, fg = "white", justify=CENTER)


def run():
    #get current case, patient and examination
    try:
        db = get_current("PatientDB")
        case = get_current("Case")
        patient = get_current("Patient")
        plan = get_current("Plan")
        examination = get_current("Examination")
        #beam_set = get_current("BeamSet")
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - PARABLE Trial Eligibility v" + str(script_version), "Please open a patient and plan first")
        exit()


    #check we have a heart contoured    
    rois = case.PatientModel.RegionsOfInterest 
    roi_structures = case.PatientModel.StructureSets[examination.Name].RoiGeometries
    
    roi_list = []
        
    for roi in rois:
        roi_list.append(roi.Name)
        
    if 'Heart' not in roi_list:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - PARABLE Trial Eligibility v" + str(script_version), "No ROI Heart Present")
        exit()

            
    if 'Heart' in roi_list:
        if roi_structures["Heart"].HasContours() is False:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error - PARABLE Trial Eligibility v" + str(script_version), "ROI 'Heart' needs outlining first!")
            exit()
                 
    ###############GET DATE OF BITH AND CALC AGE OF PATIENT##############
    import datetime
    date = str(patient.DateOfBirth)  #eg 24/09/1961 00:00:00

    datem = datetime.datetime.strptime(date, "%d/%m/%Y %H:%M:%S")  #locates day month year

    born_day = datem.day

    born_month = datem.month

    born_year = datem.year

    from datetime import date

    def age(birthdate):
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    #    
    age_years = age(date(born_year, born_month, born_day))   #eg 60

    #############get the MHD # cGy to Gy so divide by 100########################
    MHD = round(plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='Heart', DoseType='Average') / 100, 2)

    #####################cardiac risk factor define########################

    if clicked.get() == "Does current patient have any cardiac risk factors?":
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - PARABLE Trial Eligibility v" + str(script_version), "Please select if patient has any cardiac risk factors")
        exit()
        
    if clicked.get() == "Yes":
        cardiac_risk = "True"
    if clicked.get() == "No":
        cardiac_risk = "False"
     
    ##############calculate eligibility based on Table A PARABLE RTTQA DOC#####################

    if age_years <= 44:
        if cardiac_risk == 'False':
            if MHD >= 4:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'
        if cardiac_risk == 'True':
            if MHD >= 2.5:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'
                

    if 45 <= age_years <= 54:
        if cardiac_risk == 'False':
            if MHD >= 6:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'
        if cardiac_risk == 'True':
            if MHD >= 4:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'

    if 55 <= age_years <= 64:
        if cardiac_risk == 'False':
            if MHD >= 6:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'
        if cardiac_risk == 'True':
            if MHD >= 4.5:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'
                
    if age_years >=65:
        if cardiac_risk == 'False':
            if MHD >= 6:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'
        if cardiac_risk == 'True':
            if MHD >= 5.5:
                eligibility = 'Eligible for PARABLE - please ensure PARABLE trials team are aware'
            else:
                eligibility = 'NOT Eligible for PARABLE'


    ##window at end to show results
    window = Tk()
    window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
    window.withdraw()

    messagebox.showinfo('PARABLE Trial Eligibility v' + str(script_version), 'Script complete' + "\n" + "\n" + "Cardiac Risk/s" + ": " + str(cardiac_risk) + "\n" + "\n" + "Age (years)" + ": " + str(age_years) + "  (" + str(born_day) + "/" + str(born_month) + "/" + str(born_year) + ")" + "\n" + "\n" + "MHD(Gy)" + ": " + str(MHD) + "\n" + "\n" + "Result" + ": " + str(eligibility))

    window.deiconify()
    window.destroy()
    window.quit()

    #############################################################################################
def Button_pressed2():
	root.destroy()
    
#drop down box to pick cardiac risks
clicked = StringVar()
clicked.set("Does current patient have any cardiac risk factors?")
drop = OptionMenu(root, clicked, "Yes", "No")
#drop.pack()
drop.place(x=10, y=50)

##button for start script
myButton = Button(root, text="Determine PARABLE Eligiblity", command=run)

##cancel button
butt2 = Button(root, text = 'Cancel', command = Button_pressed2)

myButton.place(x=400, y=50)
butt2.place(x=650, y=50)

root.mainloop()
