# ---------------------------------------------------------------------------
# IA_AnimalsRepresentedByEO.py
# Created on: 2012 March 27
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
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
arcpy.env.workspace = arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "AnimalsEOsOnly"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_EOs"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EALL_NOB'"
    IAmodel = "01EALL_NOB"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#
#elif Proj == "All":
#    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"


print("Animals Represented by EO")


##################### Select EOs
#####################

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management(in_EOs, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(in_EOs, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management(in_EOs, "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)

arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous")

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("Contiguous", FinalFC)
arcpy.CopyFeatures_management ("Contiguous",FinalFC_gdb)

print("IA model done: EOs Only.")



