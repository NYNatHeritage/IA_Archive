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

ModelType = "Invertebrates_RiparianTigerBeetle"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
in_put_buff = "in_put_buff"
NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
#in_features = "in_features"
ClipBuff = "ClipBuff"
in_flowline = "FlowAppend"
out_buff = "out_buff"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERIV_TGB'"
    IAmodel = "01ERIV_TGB"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HRIV_G01'"
    IAmodel = "01HRIV_G01"

if Proj == "DOT":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

elif Proj == "All":
    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    
elif Proj == "HREP":
    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

# Create the clip buffer for riverine module
arcpy.Buffer_analysis(in_EOs, in_put_buff, 25, "FULL", "ROUND", "ALL")

# Create the clip buffer for riverine module
arcpy.Buffer_analysis(in_EOs, ClipBuff, 3000, "FULL", "ROUND", "ALL")

arcpy.CreateFeatureclass_management(WSP, "FlowAppend", "POLYLINE", NHDplusHydro, "DISABLED", "DISABLED", NHDplusHydro)

arcpy.MakeFeatureLayer_management(NHDplusCatch, "LAYER_NHDplusCatch")
arcpy.SelectLayerByLocation_management("LAYER_NHDplusCatch", "INTERSECT", in_EOs, "", "NEW_SELECTION")

rows = arcpy.SearchCursor("LAYER_NHDplusCatch")
for row in rows: 
    HydroCatch = row.COMID
    HydroCatch_ID = repr(HydroCatch)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis(NHDplusHydro, "GetHydro", "COMID = " + HydroCatch_ID)
    arcpy.AddMessage("HydroCatch_ID = " + HydroCatch_ID)
    arcpy.Append_management("GetHydro", "FlowAppend", "TEST")


arcpy.AddMessage("Get this far, 1") 
# Run riverine community module.
import IA_mod_riverine
IA_mod_riverine.RiverineModuleNOTRIBS(in_put_buff, StudyArea, out_buff)

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management(out_buff, "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve", "Elim", "AREA", 1000000)

# Select out only those polys contiguous with the EO
arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")


################### WRAP UP
################### 

arcpy.CopyFeatures_management ("LAYER_Elim", FinalFC)
arcpy.CopyFeatures_management ("LAYER_Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: " + ModelType)















