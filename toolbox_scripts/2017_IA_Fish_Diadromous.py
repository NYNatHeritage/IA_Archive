# ---------------------------------------------------------------------------
# IA_Fish_Diadromous.py
# Created on: 2011 December
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Tim Howard, NYNHP)
#
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
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "Fish_Diadromous"
#in_put = arcpy.GetParameterAsText(0)
#in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
##EXorHIST = arcpy.GetParameterAsText(1)
#EXorHIST = "Extant"
##tyme = arcpy.GetParameterAsText(2)
#tyme="12_31_2017"


in_estvar = "in_estvar"
out_estvar = "out_estvar"
#LULC = "H:\\Please_Do_Not_Delete_me\\_Schmid\\Important_Areas\\GIS_Data\\IA_Process.gdb/LULC_HRE"
FinalFC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ERES_DIF'"
    IAmodel = "01ERES_DIF"
##elif EXorHIST == "Historical":
##    selectQuery = "IA_MODEL = '01ERES_XXX'"
##    IAmodel = "01ERES_XXX"

# Select out the proper EOs
arcpy.Select_analysis(in_put, in_estvar, selectQuery)
arcpy.AddWarning("In EOs selected. " + EXorHIST + " " + ModelType)


################### Run estuarine module
###################
arcpy.AddWarning("Running estuarine module...")
import IA_mod_estuarine
IA_mod_estuarine.EST_module(in_estvar, out_estvar, WSP, LULC)
arcpy.AddWarning("Estuarine model, complete.")

arcpy.CopyFeatures_management ("Step4Identity", out_estvar)

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management(out_estvar, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(out_estvar, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management(out_estvar, "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
#Since the SINGLE_PART function in previous step is mysteriously not working:
arcpy.MultipartToSinglepart_management("Dissolve","Dissolvesp")


# Select out only those polys contiguous with the EO
arcpy.MakeFeatureLayer_management("Dissolvesp", "LAYER_Dissolvesp")
arcpy.SelectLayerByLocation_management("LAYER_Dissolvesp", "INTERSECT", in_estvar, "", "NEW_SELECTION")

################### WRAP UP
################### 

FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("LAYER_Dissolvesp", FinalFC)
arcpy.CopyFeatures_management ("LAYER_Dissolvesp", FinalFC_gdb)

print("IA model done: Diadromous Fish.")



