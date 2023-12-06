# ---------------------------------------------------------------------------
# IA_WoodTurtle.py
# Created on: 2011 November
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

ModelType = "WoodTurtle_"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)


in_put_buff = "in_put_buff"
out_buff = "out_buff"
hydro = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/HRE_bat"
#NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
#NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
FBP_flowlines = "W:/Projects/Freshwater_Blueprint/Data/_MasterGDB/Freshwater_Blueprint_Spatial_Data.gdb/a_NHDplus_based_Flowlines/Blueprint_Systems_NEAHC_lines"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
CCAP_Select_Query = "\"VALUE\" = 2 OR \"VALUE\" = 5 OR \"VALUE\" = 20"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETRV_WDT'"
    IAmodel = "01ETRV_WDT"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HXXXXXXX'"
    IAmodel = "01HXXXXXXX"

# Buffer the EO 10, 300, and 500m for various steps.
arcpy.AddMessage("Buffer the EO 10, 300, and 500m for various steps...")
arcpy.Buffer_analysis(in_put, "in_put10", 10, "FULL", "ROUND", "ALL")
arcpy.Buffer_analysis(in_put, "in_put300", 300, "FULL", "ROUND", "ALL")
arcpy.Buffer_analysis(in_put, "in_put500", 500, "FULL", "ROUND", "ALL")
arcpy.MultipartToSinglepart_management("in_put500","in_put500sp")

# Process: Use the Identity function
arcpy.AddMessage("Use the Identity function to locate max distance 500m streams...")
arcpy.Identity_analysis (hydro, "in_put500sp", "HydroIDpre")
arcpy.Select_analysis("HydroIDpre", "HydroID", "FID_in_put500sp <> -1")
arcpy.Buffer_analysis("HydroID", "HydroIDbuff", 6.25, "FULL", "ROUND", "ALL")
arcpy.MultipartToSinglepart_management("HydroIDbuff","HydroIDbuffsp")

# Select out the contiguous streams within 300m of the points
arcpy.AddMessage("Select out the contiguous streams within 300m of the points...")    
arcpy.MakeFeatureLayer_management("HydroIDbuffsp", "LAYER_HydroIDbuffsp")
arcpy.SelectLayerByLocation_management("LAYER_HydroIDbuffsp", "INTERSECT", "in_put300", "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_HydroIDbuffsp", "HydroWood")

# Buffer the streams 300meter per methodology
arcpy.AddMessage("Buffer the streams 300meter per methodology...")
arcpy.Buffer_analysis("HydroWood", "HydroWoodBuff", 300, "FULL", "FLAT", "ALL")

#Run terrestrial community module
arcpy.AddMessage("Running Terrestrial Community model....")
arcpy.MultipartToSinglepart_management("HydroWoodBuff","HydroWoodBuffsp")
inputPar = "HydroWoodBuffsp"
outputPar = "outTerr"
import IA_mod_terrestrial
IA_mod_terrestrial.TerrestrialModule(inputPar, outputPar)

######## HOLLIE WANTS THIS OUT FOR NOW 12/05/2011 ############# Alis Roads (Class 1 only)
##################### I had to place the select by attribute before the select by location, because there is a software
##################### bug when you try to select by location on a very large SDE dataset. Sheesh.

##arcpy.AddMessage("Removing selected Roads....")
##arcpy.MakeFeatureLayer_management("Database Connections/bloodhound.sde/AIMS.alisroads", "LAYER_alisroads")
##arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2")
##arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", outputPar, "", "SUBSET_SELECTION")
##arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")
##arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")
##arcpy.Erase_analysis(outputPar, "Buff_alisroads", "Erase")

# Extracting the CCAP uplands and erase from buffer
arcpy.AddMessage("Removing CCAP developed/barren land LU/LC....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP", CCAP_Select_Query)
arcpy.RasterToPolygon_conversion("LAYER_CCAP", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Erase_analysis(outputPar, "polys_CCAP", "Erase2")

#####################################################
## The section in here caused crashing, till I manually "Repaired Geometry" and manually dissolved#######
### Union back in, the 10m buffer
##arcpy.Union_analysis(["in_put10", "Erase2"], "Unioned", "", "", "NO_GAPS")
##arcpy.Dissolve_management("Unioned", "Dissolve1", "", "", "SINGLE_PART")
#####################################################


# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#

arcpy.AddField_management("Repair_Geo8DISS", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Repair_Geo8DISS", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Repair_Geo8DISS", "Repair_Geo8_DISS2", "IA_MODEL_R", "", "SINGLE_PART")
#Since the SINGLE_PART function in previous step is mysteriously not working:
arcpy.MultipartToSinglepart_management("Repair_Geo8_DISS2","Repair_Geo8_DISS2sp")


# Select out only those polys contiguous with the EO
arcpy.MakeFeatureLayer_management("Repair_Geo8_DISS2sp", "LAYER_Repair_Geo8_DISS2sp")
arcpy.SelectLayerByLocation_management("LAYER_Repair_Geo8_DISS2sp", "INTERSECT", "in_put10", "", "NEW_SELECTION")

################### WRAP UP
################### 

arcpy.CopyFeatures_management ("LAYER_Repair_Geo8_DISS2sp", FinalFC)
arcpy.CopyFeatures_management ("LAYER_Repair_Geo8_DISS2sp", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Wood Turtle.")















