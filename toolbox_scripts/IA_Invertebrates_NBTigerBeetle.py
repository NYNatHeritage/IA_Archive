# ---------------------------------------------------------------------------
# IA_Invertebrates_NBTigerBeetle.py
# Created on: 2013 March
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Erin White, NYNHP)
# Usage: Important Area Model for NYNHP OakPine Foodplant Leps
#   
 # This script shall not be distributed without permission from the New York Natural Heritage Program
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

ModelType = "Invertebrates_NBTigerBeetle"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

arcpy.AddMessage(ModelType + " model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_PAT'"
    IAmodel = "01ETER_PAT"
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


##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

##################### Select out specific terretrial communities
#####################
arcpy.MakeFeatureLayer_management("W:/GIS_Data/EO_Mapping/_statewide_EOs/statewide_eos.shp", "LAYER_EOs")
arcpy.SelectLayerByAttribute_management("LAYER_EOs", "NEW_SELECTION", "\"SCIEN_NAME\" = 'Dwarf pine ridges'")
arcpy.SelectLayerByLocation_management("LAYER_EOs", "INTERSECT", in_EOs, "", "SUBSET_SELECTION")
arcpy.CopyFeatures_management("LAYER_EOs", "TerrComms")

##################### Run terrestrial module
#####################
inputPar = "TerrComms"
outputPar = "outputpar"
import IA_mod_terrestrial
IA_mod_terrestrial.TerrestrialModule(inputPar, outputPar)
arcpy.AddMessage("Terrestrial Module complete")

#Union them and prepare to test size
arcpy.Union_analysis([outputPar, in_EOs], "TerrUnion", "ONLY_FID", "", "NO_GAPS")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("TerrUnion", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("TerrUnion", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("TerrUnion", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)


################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Invertebrates_NBTigerBeetle")



