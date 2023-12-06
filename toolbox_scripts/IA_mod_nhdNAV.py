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
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
#arcpy.env.snapRaster ="F:\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met" 
arcpy.env.overwriteOutput = True


def NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP):
    print("MODULE:")
    print("NHD Navigator")
    print("")

    print("start")
    #Initialize object
    nhd = win32com.client.Dispatch("VAANavigatorCOM.clsVAANavigate")
    #Set properties
    print("initialized")
    nhd.Navtype = NavT
    nhd.Startcomid = StartC
    nhd.Startmeas = StartM
    nhd.Maxdistance = MaxD
    nhd.Datapath = DataP
    nhd.Apppath = AppP
    print(nhd.Navtype)
    print(nhd.Startcomid)
    print(nhd.Maxdistance)
    print(nhd.Datapath)
    print(nhd.Apppath)
    #Do the navigation
    numReturn = nhd.VAANavigate()
    print(numReturn)
    #Terminate the object
    nhd = None
    #del win32com.client
    arcpy.AddWarning("end")

    print("nhdNAV module: FINISHED")





