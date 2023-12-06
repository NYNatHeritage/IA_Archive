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
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "Birds_Wading"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)

in_EOs = "in_EOs"
#LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
CCAP_Select_Query = "\"VALUE\" = 18 OR \"VALUE\" = 8"
NWI_wetlands = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\SDEADMIN.nc_nwi_poly_2016"

FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/_latest_results/" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EEST_G02'"
    IAmodel = "01EEST_G02Wade"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HEST_G02'"
    IAmodel = "01HEST_G02Wade"

print(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, in_EOs, selectQuery)
print("In EOs selected. " + EXorHIST + " " + ModelType)

# Buffer EOs
arcpy.Buffer_analysis(in_EOs, "in_EOs_buff", 5000, "FULL", "ROUND", "ALL")
print("EOs buffered 5 km.")

# Select emergent wetlands and grassland from CCAP
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_select", CCAP_Select_Query)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_select", "CCAP_selectPre")
arcpy.RasterToPolygon_conversion("CCAP_selectPre", "CCAP_select", "NO_SIMPLIFY", "VALUE")
print("CCAP land use selected.")

# Selecting out the NWI open water
arcpy.MakeFeatureLayer_management(NWI_wetlands, "LAYER_NWI_select")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_select", "NEW_SELECTION", "\"ATTRIBUTE\" LIE 'L%' OR \"ATTRIBUTE\" LIKE 'R%'")
arcpy.CopyFeatures_management ("LAYER_NWI_select", "NWI_openwater")
print("NWI Wetlands, selected.")

# Union and dissolve all relevant wetland types
arcpy.Union_analysis(["CCAP_select", "NWI_openwater", in_EOs], "WetUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetUnion", "WetDissolve", "", "", "SINGLE_PART")
print("Wetlands/Open Water, unioned and dissolved.")

# Clip the wetland/open water with the 5km EO buffer
arcpy.Clip_analysis("WetDissolve", "in_EOs_buff", "WetBuff")
print("Wetlands/Open Water, clipped.")

# Aggregate and Dissolve all and add the IA_MODEL_R field
arcpy.AddField_management("WetBuff", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("WetBuff", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("WetBuff", "WetBuff2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("WetBuff2", "Elim", "AREA", 3000)
print("Poly's aggregated.")

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Wading Foraging Birds.")


