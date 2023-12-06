# ---------------------------------------------------------------------------
# IA_Birds__BW_Colonial.py
# Created on: 2011 August
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Tim Howard, NYNHP)
# Usage: Important Area Model for NYNHP estuarine birds - woody tidal - communities
# Latest Edits: New to arcpy module
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


ModelType = "Birds_BW_Colonial"
in_put = arcpy.GetParameterAsText(0)
EXorHIST = arcpy.GetParameterAsText(1)
tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
CCAP_Select_Query = "VALUE = 18 OR VALUE = 19 OR VALUE = 20"
CCAP_Select_Query2 = "VALUE = 19 OR VALUE = 20"
CCAP_Select_Query3 = "VALUE = 18"

out_estvar = "out_estvar"
in_estvar = "in_estvar"
value_field = "ORIG_FID"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETES_CWB' OR IA_MODEL = '01ETES_COT' OR IA_MODEL = '01ETES_GBT'"
    IAmodel = "Multiple_BWbirdsE"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HTES_CWB' OR IA_MODEL = '01HTES_COT' OR IA_MODEL = '01HTES_GBT'"
    IAmodel = "Multiple_BWbirdsH"

arcpy.AddMessage(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

################### Select estuarine emergent marsh and unconsolidated shore from CCAP
###################
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_select", CCAP_Select_Query)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_select", "LAYER_CCAP_selectpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_selectpre", "CCAP_select", "NO_SIMPLIFY", "VALUE")
# This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
# as adjacent. The only way I can find to capture kitty-corner cells.
arcpy.Buffer_analysis("CCAP_select", "CCAP_selecttemp", "1 Meters", "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("CCAP_selecttemp", "polys_CCAPW")

arcpy.MakeFeatureLayer_management("polys_CCAPW", "LAYER_polys_CCAPW")
arcpy.SelectLayerByLocation_management("LAYER_polys_CCAPW", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_polys_CCAPW", "CCAP_both_selected_by_EOs")
arcpy.AddMessage("CCAP land use selected.")

################### Convert EO polygons to line features
###################

arcpy.PolygonToLine_management(in_EOs, "in_EOs_lines")
arcpy.AddMessage("EO lines created.")

################### Apply 200 meter buffer to portion of EO that intersects with unconsolidated
###################

arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_Ushore", CCAP_Select_Query2)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_Ushore", "LAYER_CCAP_Ushorepre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_Ushorepre", "CCAP_Ushore", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("CCAP_Ushore", "UshoreDissolve", "", "", "SINGLE_PART")
arcpy.Clip_analysis("in_EOs_lines", "UshoreDissolve", "EOlines_within_Ushore")
arcpy.Buffer_analysis("EOlines_within_Ushore", "Ushore_linebuff", 200, "FULL", "ROUND", "ALL")
arcpy.AddMessage("Beach/Wetland Colonial Waterbirds CCAP Unconsolidated shore and EO intersection, buffered 200m.")

################### Apply 6.25 meter buffer to portion of EO that intersects with emergent estuarine
###################

arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_EmergEst", CCAP_Select_Query3)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_EmergEst", "LAYER_CCAP_EmergEstpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_EmergEstpre", "CCAP_EmergEst", "NO_SIMPLIFY", "VALUE")
arcpy.Dissolve_management("CCAP_EmergEst", "EmergEstDissolve", "", "", "SINGLE_PART")
arcpy.Clip_analysis("in_EOs_lines", "EmergEstDissolve", "EOlines_within_EmergEst")
arcpy.Buffer_analysis("EOlines_within_EmergEst", "EmergEst_linebuff", 6.25, "FULL", "ROUND", "ALL")
arcpy.AddMessage("Beach/Wetland Colonial Waterbirds CCAP estuarine emergent and EO intersection, buffered 6.25m.")


################# Run estuarine module
#################

# First, need a surrogate 'species' to assure it will run the salt marsh components of the estuarine module
arcpy.AddField_management("EmergEst_linebuff", "SCIEN_NAME", "TEXT")
arcpy.CalculateField_management("EmergEst_linebuff", "SCIEN_NAME", "'Rynchops niger'", "PYTHON")
arcpy.CopyFeatures_management ("EmergEst_linebuff", in_estvar)
arcpy.AddMessage("Field populated, dude.")

arcpy.AddMessage("Running estuarine module...")
import IA_mod_estuarine
IA_mod_estuarine.EST_module(in_estvar, out_estvar, WSP, LULC)
arcpy.AddMessage("Estuarine model, complete.")

arcpy.Union_analysis(in_EOs + " #; " +  out_estvar + " #; Ushore_linebuff #; CCAP_both_selected_by_EOs #", "BW_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("BW_Union", "Dissolve", "", "", "SINGLE_PART")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)
arcpy.AddMessage("IA's aggregated.")

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Beach/Wetland Colonial Birds.")


