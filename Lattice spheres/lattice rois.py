'''
TITLE: lattice '
AUTHOR: Ian Gleeson
DATE: August 2023
PURPOSE: to make lattice vmat spheres for high dose and low dose sabr plans similar to paper by Duriseti et al doi: https://doi.org/10.1101/2020.03.09.20033332
REQUIREMENTS: CPython 3.8 64-bit interpreter
TPS VERSION: 12A
HISTORY: v1.0.0 
VERSION: 1.0.0

*** Radiotherapy Python Script Disclaimer ***

This radiotherapy Python script is provided for informational and educational purposes only. It is important to understand that the Script is open-source and comes with absolutely no warranties or guarantees of any kind. By using the Script, you acknowledge and agree to the following:

1. No Warranty: The Script is provided "as is" and without any warranty, express or implied, including but not limited to the implied warranties of merchantability, fitness for a particular purpose, or non-infringement.

2. User Responsibility: The user ("the User") acknowledges that they are solely responsible for evaluating the Script's suitability for their specific purposes and ensuring its safe and accurate use.

3. No Medical Advice: The Script is not a substitute for professional medical advice, diagnosis, or treatment. It should not be used for making medical decisions. Always consult with a qualified healthcare professional regarding any medical condition or treatment.

4. Accuracy and Reliability: While efforts have been made to ensure the accuracy and reliability of the Script, it may contain errors or inaccuracies. The User should exercise caution and due diligence when using the Script.

5. Compliance: The User must ensure that their use of the Script complies with all applicable laws, regulations, and industry standards. The User is solely responsible for any legal or regulatory issues arising from the use of the Script.

6. No Liability: Under no circumstances shall the creators, contributors, or distributors of the Script be liable for any direct, indirect, incidental, special, or consequential damages resulting from the use of the Script. This includes, but is not limited to, loss of data, business interruption, or personal injury.

7. Open Source: The Script is open-source software, which means it can be freely modified, distributed, and used by others. However, the User must adhere to the terms and conditions specified in the Script's open-source license.

By using the Script, the User acknowledges and accepts the terms of this disclaimer. If the User does not agree with these terms, they should not use the Script. The User should always seek professional guidance and validation when using the Script for any medical or clinical applications.

*** End of Disclaimer ***

'''


from connect import *
import math
from math import sqrt
import numpy as np
from tkinter import *
from tkinter import messagebox


### gui ###
root = Tk()
script_version = '1.0.0'
script_name = 'lattice rois'
root.title(f"{script_name} v{script_version}")
mycolour = '#%02x%02x%02x' % (50, 50, 50)
myorange = '#%02x%02x%02x' % (255, 140, 0)
root.configure(background=mycolour)
root.geometry("400x300")  # Set wxh

# Add label with wraplength attribute for line wrapping
lbl1 = Label(root, text='This script will make two sets (red and blue) of 1.5cm diameter lattice spheres inside the target rois', wraplength=380)
lbl1.pack()
lbl1.configure(background=mycolour, fg="white")

#####################################################################################
try:
    patient = get_current("Patient")
    case = get_current("Case")
except:
    root = Tk()
    root.withdraw()
    messagebox.showerror("Error - " + str(script_name) + "v" + str(script_version), "No patients case loaded. Please open a patients case")
    exit()
    
##get target roi list for tkinter
#roi_names = System.Collections.Generic.List[str]()
rois = case.PatientModel.RegionsOfInterest

roi_list = []
external_list = []    
for roi in rois:
    if roi.OrganData.OrganType == "Target":
        roi_list.append(roi.Name)
    if roi.Type == "External":
        external_list.append(roi.Name)

##get planning ct scans list to pick which one to use
RCTS_list = []
for RCT in case.Examinations:
    RCTS_list.append(RCT.Name)

def make_lattice_rois():
    #user input lattice arrangment like lattice of spheres inside the GTV volume as per Duriseti et al
    lattice_spacing = 3.0  # 3 cm center-to-center spacing for all spheres = 6cm for high dose to high dose or low dose to low dose sphere...
    sphere_diameter = 1.5  # 1.5 cm diameter
    separation_z = 3.0     # 3 cm separation between spheres in z direction
    diagonal_separation = 4.2426 #  Pythagorean theorem: c^2 = a^2 + b^2

    #connect current patient case and exam
    patient = get_current("Patient")
    case = get_current("Case")
    examination = get_current("Examination")
    
    #get exam name and gtv and ptv from user selection
    RCT_exam = clicked3.get()
    gtv_name = clicked1.get()
    print(str(gtv_name))
    ptv_name = clicked2.get()
    print(str(ptv_name))

    # Need to get center coordinates of ROI GTV
    roi_geometries = case.PatientModel.StructureSets[examination.Name].RoiGeometries
    roi_name = 'PTV_2000'
    roi_center = roi_geometries[roi_name].GetCenterOfRoi()
    center_ROI_coordinates = {'x': roi_center.x, 'y': roi_center.y, 'z': roi_center.z}

    # GTV bounding box limits
    ss = case.PatientModel.StructureSets[examination.Name]
    external_box = ss.RoiGeometries[roi_name].GetBoundingBox()
    z_max = external_box[1].z   # Most sup is positive 19.049
    z_min = external_box[0].z   # Most inf neg -17.549 
    y_max = external_box[0].y   # Most ANT -13.18
    y_min = external_box[1].y   # Most POST  +10.05
    x_max = external_box[0].x   # Most RIGHT?  -18.37
    x_min = external_box[1].x   # Most LEFT?   +19.91

    # Create two lists to store the coordinates of the spheres
    list1_sphere_coordinates = []
    list2_sphere_coordinates = []


    # Loop through the z-axis
    z = z_min
    while z <= z_max:
        y_index = 1  # Initialize y_index for alternating colors along y-axis
        y = y_min
        while y >= y_max:
            x = x_min
            x_index = 1  # Initialize x_index for alternating colors along x-axis
            while x >= x_max:
                # Determine the color based on the sum of the coordinates
                color_index = (x_index + y_index + int(z / separation_z)) % 2
                if color_index == 0:
                    list1_sphere_coordinates.append({'x': x, 'y': y, 'z': z})
                else:
                    list2_sphere_coordinates.append({'x': x, 'y': y, 'z': z})

                # Toggle x_index for alternating colors along x-axis
                x_index = 3 - x_index

                # Move along the x-axis with the lattice spacing in x and y directions
                x -= lattice_spacing

            # Toggle y_index for alternating colors along y-axis
            y_index = 3 - y_index

            # Move along the y-axis with the lattice spacing in x and y directions
            y -= lattice_spacing

        # Move along the z-axis with the separation between axial planes
        z += separation_z


    # Create spheres with diagonal separation in the axial plane
    list1_sphere_names = []
    list2_sphere_names = []


    # Create spheres with diagonal separation in the axial plane
    for coords in list1_sphere_coordinates:
        x = coords['x']
        y = coords['y']
        z = coords['z']

        # Create the sphere ROI and geometry
        sphere_name = f"Sphere_x{int(x)}_y{int(y)}_z{int(z)}"
        list1_sphere_names.append(sphere_name)  # Store the sphere name in list1
        sphere_center = {'x': x, 'y': y, 'z': z}

        sphere_roi = case.PatientModel.CreateRoi(Name=sphere_name, Color="Red", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        sphere_roi.CreateSphereGeometry(Radius=sphere_diameter * 0.5, Examination=examination, Center=sphere_center, Representation="TriangleMesh", VoxelSize=None)

    for coords in list2_sphere_coordinates:
        x = coords['x']
        y = coords['y']
        z = coords['z']

        # Create the sphere ROI and geometry
        sphere_name = f"Sphere_x{int(x)}_y{int(y)}_z{int(z)}"
        list2_sphere_names.append(sphere_name)  # Store the sphere name in list2
        sphere_center = {'x': x, 'y': y, 'z': z}

        sphere_roi = case.PatientModel.CreateRoi(Name=sphere_name, Color="Blue", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        sphere_roi.CreateSphereGeometry(Radius=sphere_diameter * 0.5, Examination=examination, Center=sphere_center, Representation="TriangleMesh", VoxelSize=None)


    ##################################################################################################################################################################################

    ##################################################################################################################################################################################

    print(list1_sphere_names)
    print(list2_sphere_names)
                          
    ##################################################################################################################################################################################

    ##################################################################################################################################################################################                  
                          
     


    ##pauze for planner to review - do at end now instead
    ##await_user_input("Please review spheres and adjust/delete any if needed\n\nOnce happy please click resume at the bottom left of the Scripting Menu which will make the PTVs etc.")
    
    #get new list names in case some were deleted?
    

    ##MAKE PTV_6670 COMBINED HIGH DOSE SPHERES ONLY AND CROP IT TO GTV_2000 MINUS 5MM
    with CompositeAction('ROI algebra (PTV_6670)'):

      retval_0 = case.PatientModel.CreateRoi(Name="PTV_6670", Color="Red", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

      retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': list1_sphere_names, 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["GTV_2000"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")



    ##SIMPLIFY PTV_6670 TO REMOVE ANY SMALL ISOLATED slice AREAS <0.2cm2 THAT ARE TOO SMALL
    case.PatientModel.StructureSets[examination.Name].SimplifyContours(RoiNames=["PTV_6670"], RemoveHoles3D=False, RemoveSmallContours=True, AreaThreshold=0.2, ReduceMaxNumberOfPointsInContours=False, MaxNumberOfPoints=None, CreateCopyOfRoi=False, ResolveOverlappingContours=False)


    ##MAKE 'PTV_AVOID' COMBINED COLD SPHERES ONLY AND CROP IT TO PTV_2000 

    with CompositeAction('ROI algebra (PTV_Avoid)'):

      retval_0 = case.PatientModel.CreateRoi(Name="PTV_Avoid", Color="Aqua", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

      retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': list2_sphere_names, 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV_2000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


    #MAKE PTV CONTROL STRUVTURE WHICH IS cropping PTV_6670 + 8 mm from PTV_2000
    with CompositeAction('ROI algebra (PTV_Control)'):

      retval_0 = case.PatientModel.CreateRoi(Name="PTV_Control", Color="Lime", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

      retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV_2000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV_6670"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.8, 'Inferior': 0.8, 'Anterior': 0.8, 'Posterior': 0.8, 'Right': 0.8, 'Left': 0.8 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


    ##ENSURE PTV_6670 DOES NOT OVERLAP WITH ANY OARS



    ##delete all individual sphere rois
    for roi_name in list1_sphere_names:
        case.PatientModel.RegionsOfInterest[roi_name].DeleteRoi()

    for roi_name in list2_sphere_names:
        case.PatientModel.RegionsOfInterest[roi_name].DeleteRoi()


    ##MAKE 2 OPTIMISATION RINGS AND RVR AROUND THE PTV_2000
    with CompositeAction('ROI algebra (Ring1)'):

      retval_0 = case.PatientModel.CreateRoi(Name="Ring1", Color="255, 0, 128", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

      retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV_2000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.1, 'Inferior': 1.1, 'Anterior': 1.1, 'Posterior': 1.1, 'Right': 1.1, 'Left': 1.1 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV_2000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

      # CompositeAction ends 


    with CompositeAction('ROI algebra (Ring2)'):

      retval_1 = case.PatientModel.CreateRoi(Name="Ring2", Color="255, 128, 0", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

      retval_1.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [str(external_list[0])], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV_2000"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.1, 'Inferior': 1.1, 'Anterior': 1.1, 'Posterior': 1.1, 'Right': 1.1, 'Left': 1.1 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

      retval_1.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

      # CompositeAction ends 


    #update geometry PTV_Contol
    case.PatientModel.RegionsOfInterest['PTV_Control'].UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

    ##make VMAT LATTICE plan NOW ~4 ARCS ELEKTA 6MV USE A PROTOCOL TO LOAD AS NEEDED ETC
    
    #messege box                
    window = Tk()
    window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
    window.withdraw()

    messagebox.showinfo(str(script_name) + ' v' + str(script_version), 'Script complete' + "\n" + "\n" +

    "Please review created rois to ensure satisfactory. Remove any high dose sphere components if needed" + "\n" + "\n")

    window.deiconify()
    window.destroy()
    window.quit()


# gui root ##

def Button_pressed2():
    root.destroy()
#GTV#
#label plan name
lbl11 = Label(root, text='Select GTV roi')
lbl11.place(x=20,y=50)

#drop down box for roi select target of interest
clicked1 = StringVar()
clicked1.set(roi_list[0])
drop1 = OptionMenu(root, clicked1, *roi_list)
drop1.place(x=150, y=50)

#PTV#
#label plan name
lbl11 = Label(root, text='Select PTV roi')
lbl11.place(x=20,y=100)

#drop down box for roi select target of interest
clicked2 = StringVar()
clicked2.set(roi_list[0])
drop2 = OptionMenu(root, clicked2, *roi_list)
drop2.place(x=150, y=100)

#CT#
#label RCT name
lbl12 = Label(root, text='Select Planning CT')
lbl12.place(x=20,y=150)

#drop down box for RCT
clicked3 = StringVar()
clicked3.set(RCTS_list[0])
drop3 = OptionMenu(root, clicked3, *RCTS_list)
drop3.place(x=150, y=150)

##button to function
myButton = Button(root, text="Make lattice spheres", command=make_lattice_rois)
myButton.place(x=20, y=200)

##cancel button
butt2 = Button(root, text = 'Quit', command = Button_pressed2)
butt2.place(x=150, y=200)

root.mainloop()