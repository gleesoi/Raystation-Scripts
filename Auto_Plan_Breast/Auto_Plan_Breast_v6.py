'''
TITLE: 'Auto Plan Breast'
AUTHOR: Ian Gleeson
PURPOSE: Auto plan breasts 26/5 tangents, 48/15 sibs, vmat nodes 40/15
REQUIREMENTS: CPython 3.8 64-bit interpreter
TPS VERSION: 12A
HISTORY: v6.0.0 - logging plan stats to text files, reversed laterality names rois
VERSION: 6.0.0

'''
import math
from connect import *
import connect, ctypes, sys
from tkinter import *
from tkinter import messagebox
import os
import numpy as np
import datetime
import clr
from os import listdir, mkdir, chdir, path

##filepath=r'\\Client\U$\Ian Gleeson\RAYSTATION\SCRIPTING\SCRIPTS\IG TESTS SCRIPTS RADNET\AUTO 2FIELD BREAST 26Gy 5#\IG AUTO PLAN\partial breast\SIB BITS\PLUS VMAT NODES\SISO BITS\final\WB_PB_FOR_SUBMISSION\v5\v6'
filepath=r'\\GBCBGPPHFS001.net.addenbrookes.nhs.uk\ProjectData\Project Data\RayStation\Scripting\In house scripts\12A Scripts\Testing\Auto Plan Breast v6.0.0'

os.chdir(filepath)
sys.path.append(filepath)

try:
    import Whole_Breast_v6
except:
    filepath=r'\\GBCBGPPHFS001.net.addenbrookes.nhs.uk\ProjectData\Project Data\RayStation\Scripting\In house scripts\12A Scripts\Auto Plan Breast'
    os.chdir(filepath)
    sys.path.append(filepath)
    
script_version = '6.0.0'
script_name = 'Auto Plan Breast'

###########next buttons to select course and then autoplan
root = Tk()
root.title("Auto Plan Breast v" + str(script_version))
mycolour = '#%02x%02x%02x' % (50, 50, 50)
myorange = '#%02x%02x%02x' % (255, 140, 0)
root.configure(background = mycolour)
root.geometry("760x240")
######add label#######################
lbl1 = Label(root, text='This script will auto plan a Breast/Chest wall - Click on the Site/Technique you want to use')
lbl1.place(x=65, y =5)
lbl1.configure(background = mycolour, fg = "white", justify=CENTER)


def autoplanWB():
    try:
        import Whole_Breast_v6
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local script Whole_Breast_v6" + str(sys.path))
        exit()
        
    try:
        from Whole_Breast_v6 import autoplan
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local function in Whole_Breast_v6 script" + str(sys.path))
        exit()
        
    try:
        Whole_Breast_v6.autoplan()
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot execute function in Whole_Breast_v6 script" + str(sys.path))
        exit()        
    

def autoplanVMAT2():
    try:
        import VMAT_Breast_v6
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local script VMAT_Breast_v6" + str(sys.path))
        exit()
        
    try:
        from VMAT_Breast_v6 import autoplanVMAT
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local function in VMAT_Breast_v6 script" + str(sys.path))
        exit()
        
    try:
        VMAT_Breast_v6.autoplanVMAT()
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot execute function in VMAT_Breast_v5 script" + str(sys.path))
        exit()
    
def autoplanPB():
    try:
        import Partial_Breast_v6
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local script Partial_Breast_v6" + str(sys.path))
        exit()
        
    try:
        from Partial_Breast_v6 import autoplanPBB
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local function in Partial_Breast_v6 script" + str(sys.path))
        exit()
        
    try:
        Partial_Breast_v6.autoplanPBB()
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot execute function in Partial_Breast_v6 script" + str(sys.path))
        exit()


def autoplanSIBA():
    try:
        import SIB_Breast_v6
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local script SIB_Breast_v5" + str(sys.path))
        exit()
        
    try:
        from SIB_Breast_v6 import autoplanSIB
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot import local function in SIB_Breast_v5 script" + str(sys.path))
        exit()
        
    try:
        SIB_Breast_v6.autoplanSIB()
    except:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Error - Auto Plan Breast v" + str(script_version), "Cannot execute function in SIB_Breast_v5 script" + str(sys.path))
        exit()


def Button_pressed2():
	root.destroy()

##button for plan whole breast
myButton = Button(root, text="WHOLE BREAST Plan 26Gy/5F", command=autoplanWB)
##button for partial breast 
myButton2 = Button(root, text="PARTIAL BREAST Plan 26Gy/5F", command=autoplanPB)
##button for SIB
myButton3 = Button(root, text="SIB BREAST Plan 48Gy/15F", command=autoplanSIBA)
##button for VMAT nodes
myButton4 = Button(root, text="VMAT BREAST + NODES 40Gy/15F +/- SIB 48Gy/15F", command=autoplanVMAT2)
##button for SISO
#myButton5 = Button(root, text="Start SISO BREAST NODES 40Gy/15F", command=autoplanSISO)
##cancel button
butt2 = Button(root, text = 'Cancel', command = Button_pressed2)

myButton.place(x=10, y=100)
myButton2.place(x=10, y=140)
myButton3.place(x=260, y=100)
myButton4.place(x=260, y=140)
#myButton5.place(x=10, y=180)
butt2.place(x=200, y=50)

root.mainloop()