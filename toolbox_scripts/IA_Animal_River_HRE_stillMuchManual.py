# ---------------------------------------------------------------------------
# IA_Animal_River.py
# Created on: 2011 December
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (animal methodology by Hollie Shaw, NYNHP)
# This script shall not be distributed without permission from the New York Natural Heritage Program
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting, arcpy, win32com.client

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
ModelType = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
in_features = "in_features"
ClipBuff = "ClipBuff"
in_flowline = "FlowAppend"
out_buff = "out_buff"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERIV_G01'"
    IAmodel = "01ERIV_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HRIV_G01'"
    IAmodel = "01HRIV_G01"


### Select out the proper EOs
##arcpy.Select_analysis(in_put, in_EOs, selectQuery)
##arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)    
##
### Create the clip buffer for riverine module
##arcpy.Buffer_analysis(in_EOs, in_features, 10, "FULL", "ROUND", "ALL")
##
### Create the clip buffer for riverine module
##arcpy.Buffer_analysis(in_EOs, ClipBuff, 3000, "FULL", "ROUND", "ALL")
##
##arcpy.CreateFeatureclass_management(WSP, "FlowAppend", "POLYLINE", NHDplusHydro, "DISABLED", "DISABLED", NHDplusHydro)
##
##arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
##arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT", in_EOs, "", "NEW_SELECTION")
##
##rows = arcpy.SearchCursor("LAYER_NHDplusCatch")
##for row in rows: 
##    HydroCatch = row.COMID
##    HydroCatch_ID = repr(HydroCatch)
##    # Take out one of the <61ha EOs at a time, to get buffered
##    arcpy.Select_analysis(NHDplusHydro, "GetHydro", "COMID = " + HydroCatch_ID)
##    arcpy.AddMessage("HydroCatch_ID = " + HydroCatch_ID)
##    arcpy.Append_management("GetHydro", "FlowAppend", "TEST")
##
##arcpy.AddMessage("Get this far, 1") 
### Run riverine community module.
##import IA_mod_riverine
##IA_mod_riverine.RiverineModuleHRE(in_features, ClipBuff, in_flowline, out_buff)

arcpy.MakeFeatureLayer_management(out_buff, "LAYER_out_buff")
arcpy.SelectLayerByLocation_management("LAYER_out_buff", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_out_buff", "out_buff2")

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("out_buff2", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("out_buff2", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("out_buff2", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")


################### WRAP UP
################### 

arcpy.CopyFeatures_management ("Dissolve", FinalFC)
arcpy.CopyFeatures_management ("Dissolve", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: " + ModelType)
##














