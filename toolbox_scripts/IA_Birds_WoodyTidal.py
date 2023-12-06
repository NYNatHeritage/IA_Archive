# ---------------------------------------------------------------------------
# IA_Birds_WoodyTidal.py
# Created on: 2011 August
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Tim Howard, NYNHP)
# Usage: Important Area Model for NYNHP estuarine birds - woody tidal - communities
# Latest Edits: Update to arcpy module
#   Dependency: IA_mod_estuarine.py
# Shall not be distributed without written permission from the New York Natural Heritage Program
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


ModelType = "Birds_WoodyTidal"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)
Proj = arcpy.GetParameterAsText(3)

in_EOs = "in_estvar"
in_estvar = "in_estvar"
out_estvar = "out_estvar"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EEST_G02'"
    IAmodel = "01EEST_G02"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HEST_G02'"
    IAmodel = "01HEST_G02"

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

################### Run estuarine module
###################
arcpy.AddWarning("Running estuarine module...")
import IA_mod_estuarine
IA_mod_estuarine.EST_module(in_estvar, out_estvar, WSP, LULC)
arcpy.AddMessage("Estuarine model, complete.")

if EXorHIST == "Extant":

    ################### Pull out and clip EOID = 7557
    ###################
    # First, select the EO in question
    arcpy.AddMessage("Running the EOID=7557 Exception.")
    arcpy.MakeFeatureLayer_management(in_estvar, "LAYER_in_estvar")
    arcpy.SelectLayerByAttribute_management("LAYER_in_estvar", "NEW_SELECTION", "EO_ID = 7557")
    arcpy.Buffer_analysis("LAYER_in_estvar", "EO7557_buff", 2800, "FULL", "ROUND", "ALL")
    # Then select the new pre-IA's with this EO
    arcpy.MakeFeatureLayer_management(out_estvar, "LAYER_out_estvar")
    arcpy.SelectLayerByLocation_management("LAYER_out_estvar", "INTERSECT", "LAYER_in_estvar", "", "NEW_SELECTION")
    arcpy.Clip_analysis("LAYER_out_estvar", "EO7557_buff", "ToAppend")
    arcpy.SelectLayerByLocation_management("LAYER_out_estvar", "", "", "", "SWITCH_SELECTION")
    arcpy.Append_management("LAYER_out_estvar", "ToAppend")
    arcpy.AddMessage("DONE with the EOID=7557 Exception.")
    
else:
    arcpy.CopyFeatures_management (out_estvar, "ToAppend")
    

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("ToAppend", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("ToAppend", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("ToAppend", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

arcpy.MakeFeatureLayer_management("Elim", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_estvar, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous")

################### WRAP UP
###################
arcpy.CopyFeatures_management ("Contiguous", FinalFC)
arcpy.CopyFeatures_management ("Contiguous", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)
arcpy.AddMessage("IA model done: Woody Tidal Animals.")


