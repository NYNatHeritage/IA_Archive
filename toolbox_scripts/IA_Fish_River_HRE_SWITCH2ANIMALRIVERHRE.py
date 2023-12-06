# ---------------------------------------------------------------------------
# IA_Fish_River.py
# Created on: 2011 December
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (animal methodology by Hollie Shaw, NYNHP)
# This script shall not be distributed without permission from the New York Natural Heritage Program
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Animals_River_"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)

NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
in_flowline = "FlowAppend"
out_buff = "out_buff"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERIV_G01'"
    IAmodel = "01ERIV_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HRIV_G01'"
    IAmodel = "01HRIV_G01"


### Select out the contiguous streams within 300m of the points
##arcpy.AddMessage("Select out the contiguous streams within 300m of the points...")    
##
##arcpy.CreateFeatureclass_management(WSP, "FlowAppend", "POLYLINE", NHDplusHydro, "DISABLED", "DISABLED", NHDplusHydro)
##
##arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
##arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT", in_put, "", "NEW_SELECTION")
##
### Grab flowlines associated with selected catchments
##arcpy.AddMessage("Grab flowlines associated with selected catchments...")
##rows = arcpy.SearchCursor("LAYER_NHDplusCatch")
##for row in rows: 
##    HydroCatch = row.COMID
##    HydroCatch_ID = repr(HydroCatch)
##    # Take out one of the <61ha EOs at a time, to get buffered
##    arcpy.Select_analysis(NHDplusHydro, "GetHydro", "COMID = " + HydroCatch_ID)
##    arcpy.AddMessage("COMID = " + HydroCatch_ID)
##    arcpy.Append_management("GetHydro", "FlowAppend", "NO_TEST")
##
# Run riverine community module.
arcpy.AddMessage("Run riverine community module...")
import IA_mod_riverine
IA_mod_riverine.RiverineModuleHRE(in_flowline, out_buff)

### Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
### and came up with memory issues, so I just write to the final layer for now. 
###
##arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
##arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
##arcpy.Dissolve_management(out_buff, "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
##
##################### WRAP UP
##################### 
##
##arcpy.CopyFeatures_management ("Dissolve", FinalFC)
##arcpy.CopyFeatures_management ("Dissolve", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)
##
##arcpy.AddMessage("IA model done: Riverine Animals.")















