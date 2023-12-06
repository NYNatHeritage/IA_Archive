# ---------------------------------------------------------------------------
# IA_NorthernCricketFrog.py
# Created on: 2013 March
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Northern Cricket Frog
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited:
#   Edit:
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


ModelType = "Amphibians_NorthernCricketFrog"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
in_features = "in_EOs"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
CCAP_select = "CCAP_select"
CCAP_Select_Query = "\"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 21 OR \"VALUE\" = 22"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPAL_NCF'"
    IAmodel = "01EPAL_NCF"
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

    
arcpy.AddMessage("Northern Cricket Frog model")

##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer the EOs 340 meters and then 450 meters
###################

arcpy.Buffer_analysis(in_EOs, "in_EOs450", 450, "FULL", "ROUND", "ALL")

################### Select wetlands, union them, and then buffer them 340m
###################
# Select DEC wetlands
arcpy.AddMessage("Going into DEC Wetlands...")
import IA_mod_lulc_select
IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
arcpy.AddMessage("LU/LC SELECT: DEC Wetlands have been selected.")

# Select out NWI wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)
# Selecting out the lacustrine and palustrine NWI wetlands
arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"SYSTEM\" = 'P'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")

# Select CCAP wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")

# Union and Dissolve
arcpy.Union_analysis([in_EOs, CCAP_select, "NWI_wet_polys", DEC_wetlands], "WetUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetUnion", "WetDissolve", "", "", "SINGLE_PART")
arcpy.Buffer_analysis("WetDissolve", "WetDissolve340", 340, "FULL", "ROUND", "ALL")

################### Select Undeveloped Landcover, clip to 450m
###################

in_features = "in_EOs450"
CCAP_select = "CCAP_selectUndev"
CCAP_Select_Query = "\"VALUE\" = 6  OR \"VALUE\" = 7 OR \"VALUE\" = 8 OR \"VALUE\" = 9 OR \"VALUE\" = 10 OR \"VALUE\" = 11 OR \"VALUE\" = 12 OR \"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 17 OR \"VALUE\" = 18 OR \"VALUE\" = 19 OR \"VALUE\" = 20 OR \"VALUE\" = 21 OR \"VALUE\" = 22 OR \"VALUE\" = 23"

# Select CCAP wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")

arcpy.Clip_analysis("CCAP_selectUndev", "in_EOs450", "Undev450")


################### Union and Dissolve EOs back in
###################
arcpy.Union_analysis([in_EOs, "WetDissolve340", "Undev450"], "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "EODissolve", "", "", "SINGLE_PART")


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

arcpy.AddMessage("IA model done: Northern Cricket Frog.")

