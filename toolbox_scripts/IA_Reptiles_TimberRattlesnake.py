# ---------------------------------------------------------------------------
# IA_Reptiles_TimberRattlesnake.py
# Created on: 2013 March 4
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Jesse Jaycox, former zoologist with NYNHP, and adapted by Erin
#       White, Zoologist, NYNHP)
# Usage: Important Area Model for Timber Rattlesnake
# Shall not be distributed without permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "Reptiles_TimberRattlesnake"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "\"VALUE\" in ( 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23)"
RoadBarrier = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/MajRoads_TimberRattlesnake_Barriers"
HudsonRiver = "Database Connections/Bloodhound.sde/SDEADMIN.dfw_hudson_river_shoreline"

FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETPL_TRS'"
    IAmodel = "01ETPL_TRS"
##elif EXorHIST == "Historical":
##    selectQuery = "IA_MODEL = 'XXXXXX'"
##    IAmodel = "XXXXXX"


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

    
arcpy.AddMessage("Timber Rattlesnake model")

################### Select EOs
###################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Capture Roadless Blocks
###################

# Select out the proper Roadless Blocks
arcpy.MakeFeatureLayer_management("C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HREP_TBLK", "LAYER_HREP_TBLK", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_HREP_TBLK", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_HREP_TBLK", "RoadlessBLK")

################### Buffer the EOs 3.5km and 4.5km
###################

arcpy.Buffer_analysis(in_EOs, "in_EOs3500", 3500, "FULL", "ROUND", "ALL")
arcpy.Buffer_analysis(in_EOs, "in_EOs4500", 4500, "FULL", "ROUND", "ALL")
arcpy.Buffer_analysis(in_EOs, "in_EOs800", 800, "FULL", "ROUND", "ALL")

################### Clip Roadless Blocks
###################

arcpy.Clip_analysis("RoadlessBLK", "in_EOs4500", "RdBlkClip4500")

################### Select Undeveloped Landcover and Clip to the 3.5km buffer
###################

in_features = "in_EOs3500"

# Select CCAP wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")
arcpy.Clip_analysis(CCAP_select, "in_EOs3500", "LUClip3500")

################### Union and Dissolve EOs back in
###################
arcpy.Union_analysis([in_EOs, "in_EOs800", "LUClip3500", "RdBlkClip4500"], "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Erase_analysis("EOUnion", RoadBarrier, "Erase_Road")
arcpy.Erase_analysis("Erase_Road", HudsonRiver, "Erase_HR")
arcpy.Dissolve_management("Erase_HR", "EODiss", "", "", "SINGLE_PART")
# Select out touching EO
arcpy.MakeFeatureLayer_management("EODiss", "LAYER_EODiss")
arcpy.SelectLayerByLocation_management("LAYER_EODiss", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_EODiss", "EODissolve")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("EODissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("EODissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("EODissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Timber Rattlesnake model")

