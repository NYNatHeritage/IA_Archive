# IA_mod_nhdNAV.py
# Created on: Wed June 9, 2010
#   (created by John Schmid, GIS Specialist, NYNHP)
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy


# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True



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


NavT = "UPTRIB"
StartC = 6212800
StartM = 0
MaxD = 0
DataP = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02"
#AppP = "C:/Documents and Settings/All Users/Desktop/Install/VAACOMObjectNavigator"
AppP = "C:/_Schmid/_project/Important_Areas/geo_scripts/NHD_scripts/VAACOMObjectNavigator/"


##try:
##    def nhdNAV_module(NavT, StartC, StartM, MaxD, DataP, AppP):
##        
##        arcpy.AddMessage("MODULE:")
##        arcpy.AddMessage("NHD Navigator")
##        arcpy.AddMessage("")

arcpy.AddMessage("start")
#Initialize object
nhd = win32com.client.Dispatch("VAANavigatorCOM.clsVAANavigate")
#Set properties
nhd.Navtype = NavT
nhd.Startcomid = StartC
nhd.Startmeas = StartM
nhd.Maxdistance = MaxD
nhd.Datapath = DataP
nhd.Apppath = AppP
arcpy.AddMessage(nhd.Navtype)
arcpy.AddMessage(nhd.Startcomid)
arcpy.AddMessage(nhd.Maxdistance)
arcpy.AddMessage(nhd.Datapath)
arcpy.AddMessage(nhd.Apppath)
#Do the navigation
numReturn = nhd.VAANavigate()
arcpy.AddMessage(numReturn)
#Terminate the object
nhd = None
del win32com.client
arcpy.AddWarning("end")

##        arcpy.AddMessage("nhdNAV module: FINISHED")
##
##except:
##    #arcpy.AddMessage("Error")
##    #arcpy.AddMessage(arcpy.GetMessages(2))




