# IA_mod_nhdNAV.py
# Created on: Wed June 9, 2010
#   (created by John Schmid, GIS Specialist, NYNHP)
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting, win32com.client
# Create the Geoprocessor object
gp = arcgisscripting.create()
# Check out any necessary licenses
gp.CheckOutExtension("spatial")
# Load required toolboxes...
gp.AddToolbox("C:/Program Files/ArcGIS/ArcToolbox/Toolboxes/Analysis Tools.tbx")
gp.OverwriteOutput = 1


# Navtype – Type of navigation. (STRING) Valid values are
#     UPMAIN – Upstream Mainstem
#     UPTRIB – Upstream with tributaries
#     DNMAIN – Downstream mainstem
#     DNDIV – Downstream with divergences
# Startcomid – Starting NHDFlowline comid for the navigation. (NUMERIC) Must be greater than 0.
# Startmeas – Starting measure for the navigation. (NUMERIC) Must be between 0 and 100, inclusive.
#     Additionally, a startmeas of –1 is valid. It indicates that the navigator should perform
#     “whole NHDFlowline” navigation and begin at the from measure of the NHDFlowline for upstream
#     navigations and the to measure of the NHDFlowline for downstream navigations.
# Maxdistance – Maximum travel distance in kilometers. (NUMERIC) A value of 0 indicates there is
#     no maximum travel distance and to navigate each path until the path ends. 0 is the default value.
# Datapath – Path to the NHDPlus workspace, openme.txt should be in this location (STRING)
# Apppath – Path to the directory containing VAANavigationCom.dll. (STRING)
# There are several external files packaged along with the VAANavigation COM object that are needed
#     to perform navigation. The com object must be able to find them.
#     TNavWorkskel.mdb, TFromToSkel.mdb, ComputeFromTo.dll)


in_var = gp.GetParameterAsText(0)
# Should come from parent script.....NavT = gp.GetParameterAsText(1)
out_var = gp.GetParameterAsText(2)
AppP = "C:/Documents and Settings/All Users/Desktop/Install/VAACOMObjectNavigator"




# Starting loop that selects a record ("in_EOs" 100m buffer of EOs) at a time, and runs it through the procedure
cur = gp.SearchCursor(in_EOs)
row = cur.Next()
while row:
    EO_ID = row.EO_ID
    suffix = repr(EO_ID)
    # Create a layer of the EO
    LAYER_in_EOs = "LAYER_in_EOs"
    LAYER_in_EOs_Selected = "LAYER_in_EOs_Selected
    gp.MakeFeatureLayer_management(in_EOs, LAYER_in_EOs)
    gp.SelectLayerByAttribute(LAYER_in_EOs, "NEW_SELECTION", "\"EO_ID\" =" + suffix)
    gp.MakeFeatureLayer_management(LAYER_in_EOs, LAYER_in_EOs_Selected)        

    # Select the EPA Region with that EO
    LAYER_EPA = "LAYER_EPA"
    LAYER_Selected_EPA = "LAYER_Selected_EPA"
    gp.MakeFeatureLayer_management("C:/_Schmid/_GIS_Data/nhdplus/EPA_regions.shp", LAYER_EPA)
    gp.SelectLayerByLocation_management(LAYER_EPA, "HAVE_THEIR_CENTER_IN", LAYER_in_EOs_Selected, "", "NEW_SELECTION")
    gp.MakeFeatureLayer_management(LAYER_EPA, LAYER_Selected_EPA)

    # Determine the EPA region and then assign the region to the NHD folder
    cur2 = gp.SearchCursor(LAYER_Selected_EPA)
    row2 = cur2.Next()
    EPA_Reg = row2.HUC_2
    DataP = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus" + EPA_Reg

    # Select the stream segment
    LAYER_Flowline = "LAYER_Flowline"
    LAYER_Flowline_Selected = "LAYER_Flowline_Selected"
    gp.MakeFeatureLayer_management("C:/_Schmid/_GIS_Data/nhdplus/NHDPlus" + EPA_Reg + "/Hydrography/nhdflowline.shp", LAYER_Flowline)
    gp.SelectLayerByLocation_management(LAYER_Flowline, "INTERSECT", LAYER_in_EOs_Selected, "", "NEW_SELECTION")
    gp.MakeFeatureLayer_management(LAYER_Flowline, LAYER_Flowline_Selected)   


    # Assign the COM_ID value
    cur3 = gp.SearchCursor(LAYER_Flowline_Selected)
    row3 = cur3.Next()
    StartC = row3.COMID




    
    


    while row2:


    print "This script will now calculate Important Areas for " + row.COUNTY + " County."
    suffix = repr(Cnty)
    County_Name = row.COUNTY

    row = cur.Next()






import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_module(NavT, StartC, StartM, MaxD, DataP, AppP)





StartM = 0
MaxD = 0





##try:
##    def nhdNAV_module(NavT, StartC, StartM, MaxD, DataP, AppP):
##        
##        gp.AddMessage("MODULE:")
##        gp.AddMessage("NHD Navigator")
##        gp.AddMessage("")

print "start"
#Initialize object
nhd = win32com.client.Dispatch("VAANavigatorCOM.clsVAANavigate")
#Set properties
nhd.Navtype = NavT
nhd.Startcomid = StartC
nhd.Startmeas = StartM
nhd.Maxdistance = MaxD
nhd.Datapath = DataP
nhd.Apppath = AppP
print nhd.Navtype
print nhd.Startcomid
print nhd.Maxdistance
print nhd.Datapath
print nhd.Apppath
#Do the navigation
numReturn = nhd.VAANavigate()
print numReturn
#Terminate the object
nhd = None
del win32com.client
print "end"

##        gp.AddMessage("nhdNAV module: FINISHED")
##
##except:
##    #gp.AddMessage("Error")
##    #gp.AddMessage(gp.GetMessages(2))




