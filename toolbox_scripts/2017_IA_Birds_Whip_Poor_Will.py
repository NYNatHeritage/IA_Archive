# ---------------------------------------------------------------------------
# IA_Birds_WhipPoorWill.py
# Created on: 2018 May
#   (script by Amy Conley, Spatial Ecologist, NYNHP,)
#   (methodology by Hollie Shaw, NYNHP)
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
arcpy.env.workspace = arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Birds_Whip_Poor_Will"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)


in_EOs = "in_EOs"
CCAP_Select_Query = "VALUE = 7 OR VALUE = 8 OR VALUE = 9 OR VALUE = 10 OR VALUE = 11"
HectExpression = "float(!SHAPE.AREA@HECTARES!)"
FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST

print(ModelType + " model")

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01ETER_WPW'"
    IAmodel = "01ETER_FLD"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"
    
    
    
print(ModelType + " model")    
    
# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
                              
######testing
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test1.shp"
arcpy.CopyFeatures_management("LAYER_all_EOs", test_step)
#result- ok
##################### Select Woodlands from CCAP
#####################
# Selecting CCAP Wetlands, palustrine and estuarine, but not including water
attExtract = ExtractByAttributes(LULC, CCAP_Select_Query) 
attExtract.save("CCAP_WoodL")
arcpy.RasterToPolygon_conversion("CCAP_WoodL", "polys_WoodL", "NO_SIMPLIFY", "VALUE")
print("LU/LC selected...")


#testing
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test2.shp"
arcpy.CopyFeatures_management("polys_WoodL", test_step)

#Result- This worked

#######
################### Calc Hectares and determine < or > 15 ha
###################

arcpy.AddField_management(in_EOs, "Hectares", "DOUBLE", "20")
arcpy.MultipartToSinglepart_management(in_EOs,"in_EOsMP")
arcpy.CalculateField_management("in_EOsMP", "Hectares", HectExpression, "PYTHON")
print("Hectares calculated...")

# Add field to assign a static ID
arcpy.AddField_management("in_EOsMP", "WBIRD_ID", "SHORT")
arcpy.CalculateField_management("in_EOsMP", "WBIRD_ID", "int(!OBJECTID!)", "PYTHON")

arcpy.Select_analysis("in_EOsMP", "Append_in_WPW", "Hectares >= 15")
arcpy.Select_analysis("in_EOsMP", "Working_in_WPW", "Hectares < 15")
print("Whippoorwill EOs >= 15 ha differentiated...")



#####Testing
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test3.shp"
arcpy.CopyFeatures_management("Append_in_WPW", test_step)


test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test3b.shp"
arcpy.CopyFeatures_management("Working_in_WPW", test_step)



################### Two loops - go through each EO, and buffer as many times as necessary to reach thresholds
###################

# BIG LOOP: Go through each EO =< hectare threshold

rows = arcpy.SearchCursor("Working_in_WPW")

for row in rows: 
    WBIRD_ID = row.WBIRD_ID  #Use these because they refer to the exploded parts
    rw_ID = repr(WBIRD_ID)
    #EO_ID = row.EO_ID
    #rEO_ID = repr(EO_ID)
    # Take out one of the <61ha EOs at a time, to get buffered
    arcpy.Select_analysis("Working_in_WPW", "GetBuffed", "WBIRD_ID = " + rw_ID)

    Dist = 50    #Step Distance meters
    TotalDist = 550 # This includes "Dist" value for killing the loop- maximum search distance
    TotalDistm = 150000    #Area threshold for skipping
    checkOne = 1
    countDist = 0

    # Create a 'roadblock' to clip the features with (we do not want buffer rings to go past ACC = 1 or 2 roads
    # Originally written for grassland birds, but no roadblock called for w/rh woodpecker so substitute the study area
    # for roadblocks
    # arcpy.MakeFeatureLayer_management(Roadblocks, "LAYER_Roadblocks")
    arcpy.MakeFeatureLayer_management(StudyArea, "LAYER_Roadblocks")
    arcpy.SelectLayerByLocation_management("LAYER_Roadblocks", "INTERSECT", "GetBuffed", "", "NEW_SELECTION")

    # Smaller loop, buffer concentric rings
    while checkOne > 0:
        arcpy.Buffer_analysis("GetBuffed", "WPWBuff", Dist, "FULL", "ROUND", "ALL", "")
        countDist = countDist + Dist
        print(repr(countDist) + " meters, buffering EO.")
        #Clip grasslands with bird EO buffer
        arcpy.Clip_analysis("polys_WoodL", "WPWBuff", "WPWBuff_clip")
        #Clip previous clip with roadless block
        arcpy.Clip_analysis("WPWBuff_clip", "LAYER_Roadblocks", "WPW_clip")
        #Union them and prepare to test size
        arcpy.Union_analysis("GetBuffed #; WPW_clip #", "WPWUnion", "ONLY_FID", "", "NO_GAPS")
        arcpy.Dissolve_management("WPWUnion", "WPWDissolve", "", "", "MULTI_PART")
        arcpy.MakeFeatureLayer_management("WPWDissolve", "LAYER_WPWDissolve", "", "", "")
        # Select multipart EO/buffer >=8.5ha
        arcpy.SelectLayerByAttribute_management("LAYER_WPWDissolve", "NEW_SELECTION", "\"Shape_Area\" >= " + repr(TotalDistm))

        # Check for empty selection and, if so, buffer EO again, or hits the hectare or distance thresholds
        # and moves on to the next EO.
        results = arcpy.GetCount_management("LAYER_WPWDissolve")
        SelectCount = int(results.getOutput(0))
        print(repr(SelectCount) + " selected features.")
        if SelectCount == 0:
            checkOne = checkOne + 1
            print(repr(checkOne) + " buffer attempts.")
            arcpy.Copy_management("WPWDissolve", "GetBuffed")
            print("Feature " + repr(row.WBIRD_ID) + " still not big enough.")
        else:
            checkOne = 0
            arcpy.Append_management("WPWDissolve", "Append_in_WPW", "NO_TEST")
            print("Feature " + repr(row.WBIRD_ID) + " is big enough now, and appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")
            arcpy.SelectLayerByAttribute_management("LAYER_WPWDissolve", "CLEAR_SELECTION")
        if countDist >= TotalDist:
            checkOne = 0
            arcpy.Append_management("WPWDissolve", "Append_in_WPW", "NO_TEST")
            print("Feature " + repr(row.WBIRD_ID) + " has reached 0.5km so now it is appended.")
            print("checkOne = " + repr(checkOne) + " buffer attempts.")


#Testing
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test4.shp"
arcpy.CopyFeatures_management("Append_in_WPW", test_step)
#

# This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
# as adjacent. The only way I can find to capture kitty-corner cells.
arcpy.Buffer_analysis("Append_in_WPW", "polys_Elim", "1 Meters", "FULL", "ROUND", "ALL", "")
arcpy.MultipartToSinglepart_management("polys_Elim", "polys_ElimSP")
arcpy.MakeFeatureLayer_management("polys_ElimSP", "LAYER_polys_ElimSP", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_polys_ElimSP", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_polys_ElimSP", "Contiguous")

#test
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test5.shp"
arcpy.CopyFeatures_management("Contiguous", test_step)


########Buffer by 30meters
arcpy.Buffer_analysis("Contiguous", "buff_features_30", 30, "FULL", "ROUND", "ALL", "")


# Select CCAP wetlands
in_features = "buff_features_30"
CCAP_select2 = "CCAP_select2"
CCAP_Select_Query_2 = "VALUE = 6 OR VALUE = 7 OR VALUE = 8 "
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select2, LULC, WSP, CCAP_Select_Query_2)
arcpy.AddMessage("LU/LC SELECT: CCAP cultivated lands, pasture/hay, and grasslands within 30 meters selected.")
arcpy.Clip_analysis(CCAP_select2, "buff_features_30", "LUClip30")

#test
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test6.shp"
arcpy.CopyFeatures_management("LUClip30", test_step)

##Union
# Union and Dissolve EOs back in
arcpy.Union_analysis(["LUClip30","Contiguous"], "EOUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EOUnion", "Dissolve", "", "", "SINGLE_PART")

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test7.shp"
arcpy.CopyFeatures_management("Dissolve", test_step)

#Run Ecology Terrestrial Model
inputPar = "Dissolve"
outputPar = "outputpar"
import IA_mod_terrestrial
IA_mod_terrestrial.TerrestrialModule(inputPar, outputPar)
print("Terrestrial Module complete")

#test

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test8.shp"
arcpy.CopyFeatures_management("outputpar", test_step)


#Union them and prepare to test size
arcpy.Union_analysis([outputPar, in_EOs], "TerrUnion", "ONLY_FID", "", "NO_GAPS")

################### Aggregate and Dissolve all


###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management( "TerrUnion", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management( "TerrUnion", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management( "TerrUnion", "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 1000000)

############

FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Whippoorwill.")