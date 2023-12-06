# ---------------------------------------------------------------------------
# IA_Birds_GM_Raptors.py
# Created on: 2012 January
#   (script by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw and Jesse Jaycox, NYNHP)
# Usage: Grassland/Marsh Raptors
#   
# Shall not be distributed without permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#
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

ModelType = "Birds_GrassMarsh_Raptors"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)


in_EOs = "in_EOs"
CCAP_Select_Query = "\"VALUE\" = 5 OR \"VALUE\" = 7 OR \"VALUE\" = 8 OR \"VALUE\" = 20 OR \"VALUE\" = 18 OR \"VALUE\" = 15"
NWI_wetlands = "M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\SDEADMIN.nc_nwi_poly_2016"
HectExpression = "float(!SHAPE.AREA@HECTARES!)"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETPE_GMR'"
    IAmodel = "01ETPE_GMR"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HTPE_GMR'"
    IAmodel = "01HTPE_GMR"

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

print(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

################### Select Grasslands and Marsh from CCAP
###################
# Selecting Grassland and Marsh LULC
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP_select", CCAP_Select_Query)
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_CCAP_select", "LAYER_CCAP_selectpre")
arcpy.RasterToPolygon_conversion("LAYER_CCAP_selectpre", "CCAP_select", "NO_SIMPLIFY", "VALUE")

# Selecting out the estuarine and palustrine NWI wetlands
arcpy.MakeFeatureLayer_management(NWI_wetlands, "LAYER_NWI_select")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_select", "NEW_SELECTION", "\"ATTRIBUTE\" LIKE 'E%' OR \"ATTRIBUTE\" LIKE 'P%'")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_select", "SUBSET_SELECTION", "\"ATTRIBUTE\" NOT LIKE '%FO%'")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_select", "REMOVE_FROM_SELECTION", "\"ATTRIBUTE\" = 'E1UBL'")
arcpy.CopyFeatures_management ("LAYER_NWI_select", "NWI_wet_polys")
print("NWI Wetlands, selected.")

# DEC wetlands do not need to be sub-selected.
# Union and dissolve all relevant wetland types
arcpy.Union_analysis("CCAP_select #; F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/DECwetlands_HREP_polys #; NWI_wet_polys #", "GrassMarshUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("GrassMarshUnion", "GrassMarshDissolve", "", "", "SINGLE_PART")
print("Grasslands and Marsh unioned and dissolved.")

# Run the preliminary swipe to see if contiguous habitat is >500 acres
arcpy.MakeFeatureLayer_management("GrassMarshDissolve", "LAYER_grass_marsh")
arcpy.SelectLayerByLocation_management("LAYER_grass_marsh", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.Union_analysis(in_EOs + " #; LAYER_grass_marsh #", "GM_EO_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("GM_EO_Union", "in_gmBirds", "", "", "SINGLE_PART")
print("Raptor EOs and habitat, unioned and dissolved.")

arcpy.AddField_management("in_gmBirds", "Hectares", "DOUBLE", "20")
arcpy.CalculateField_management("in_gmBirds", "Hectares", HectExpression, "PYTHON")
print("Hectares calculated.")

# Add field to assign a static ID
arcpy.AddField_management("in_gmBirds", "gm_ID", "SHORT")
arcpy.CalculateField_management("in_gmBirds", "gm_ID", "int(!OBJECTID!)", "PYTHON")

arcpy.Select_analysis("in_gmBirds", "Append_in_gmBirds", "Hectares >= 202")
arcpy.Select_analysis("in_gmBirds", "Working_in_gmBirds", "Hectares < 202")
print("Grassland bird EOs >= 61ha differentiated.")


################### Two loops - go through each EO, and buffer as many times as necessary to reach thresholds
###################

# BIG LOOP: Go through each EO =< hectare threshold

rows = arcpy.SearchCursor("Working_in_gmBirds")

for row in rows: 
    gm_ID = row.gm_ID
    rgm_ID = repr(gm_ID)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis("Working_in_gmBirds", "GetBuffed", "gm_ID = " + rgm_ID)
    print("gm_ID = " + rgm_ID)

    Dist = 100
    TotalDist = 5100 # This includes "Dist" value for killing the loop
    ElimDist = 6070
    TotalDistm = 2020000
    checkOne = 1
    countDist = 0
    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "gmBirdsBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        print(repr(countDist) + " meters, buffering EO.")
        #Clip grass/marsh with bird buffer
        arcpy.Clip_analysis("GrassMarshDissolve", "gmBirdsBuff", "gmBirdsBuff_clip")
        #Dissolve them and prepare to test size - first as single part to eliminate 1.5 acre (0.6070309 ha) and smaller
        arcpy.Dissolve_management("gmBirdsBuff_clip", "gmDissolve1", "", "", "SINGLE_PART")
        arcpy.MakeFeatureLayer_management("gmDissolve1", "LAYER_gmDissolve1", "", "", "")
        # Select singlepart EO/buffer >=1.5 acres
        arcpy.SelectLayerByAttribute_management("LAYER_gmDissolve1", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(ElimDist))
        #Dissolve them and prepare to test size
        arcpy.Dissolve_management("LAYER_gmDissolve1", "gmDissolve2", "", "", "MULTI_PART")
        arcpy.MakeFeatureLayer_management("gmDissolve2", "LAYER_gmDissolve2", "", "", "")
        # Select multipart EO/buffer >=61ha
        arcpy.SelectLayerByAttribute_management("LAYER_gmDissolve2", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))

        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_gmDissolve2")
        SelectCount = int(results.getOutput(0))
        print(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            print repr(checkOne) + " buffer attempts."
            arcpy.Copy_management("gmBirdsBuff", "GetBuffed")
            print("Feature " + repr(row.gm_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("gmDissolve2", "Append_in_gmBirds", "NO_TEST")
            print("Feature " + repr(row.gm_ID) + " is big enough now, and appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_gmDissolve2", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("gmDissolve2", "Append_in_gmBirds", "NO_TEST")
            print("Feature " + repr(row.gm_ID) + " has reached 0.5km so now it is appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")

# Union back in the starting units of the 'too small, need buffer' polygons
arcpy.Union_analysis("in_EOs #; Append_in_gmBirds #; Working_in_gmBirds #", "gmUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("gmUnion", "Dissolve", "", "", "SINGLE_PART")


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Dissolve", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Dissolve", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management("Dissolve", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Grassland/Marsh Raptors.")



