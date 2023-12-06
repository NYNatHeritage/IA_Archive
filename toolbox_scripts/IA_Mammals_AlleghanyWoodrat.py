# ---------------------------------------------------------------------------
# IA_Mammals_AlleghanyWoodrat.py
# Created on: 2013 March 6
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Erin White, Zoologist, NYNHP)
# Usage: Important Area Model for Alleghany Woodrat
#   Dependency: none
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 
#   Edit Reason:
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

ModelType = "Mammals_AlleghanyWoodrat"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
#CCAP_Select_Query = "VALUE = 21"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_RAT'"
    IAmodel = "01ETER_RAT"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    
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


arcpy.AddMessage(ModelType + " model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Buffer selected EOs 200 meters
###################
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 160, "FULL", "ROUND", "NONE", "")


################### Erase Hudson River
###################
arcpy.Erase_analysis("in_EOs_buff", "Database Connections/Bloodhound.sde/SDEADMIN.nc_major_waterbody", "Erase")


################### Aggregate and Dissolve all
###################

arcpy.Merge_management([in_EOs, "Erase"], "Union")
arcpy.Dissolve_management("Union", "Dissolve", "", "", "SINGLE_PART")

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Elim", "IA_MODEL_R", "", "SINGLE_PART")
####arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Contiguous", FinalFC)
arcpy.CopyFeatures_management ("Contiguous", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Alleghany Woodrat.")

