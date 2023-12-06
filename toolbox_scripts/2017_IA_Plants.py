
# ---------------------------------------------------------------------------
# IA_Plants.py
# Created on: 2012 August
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (community methodology by Troy Weldy, NYNHP)
# This script shall not be distributed without permission from the New York Natural Heritage Program
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcpy, arcgisscripting, win32com.client

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
#arcpy.env.workspace  = "G:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Plants"
#in_put = arcpy.GetParameterAsText(0)
#in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
#EXorHIST = arcpy.GetParameterAsText(1)
#EXorHIST = "Extant"
#tyme = arcpy.GetParameterAsText(2)
#tyme="12_01_2011"
#Proj = arcpy.GetParameterAsText(3)
#Proj = "HREP"

CCAP_Select_Query = "VALUE = 13 OR VALUE = 14 OR VALUE = 15 OR VALUE = 16 OR VALUE = 17 OR VALUE = 18"
in_features = "in_plants"
CCAP_select = "CCAP_select"
DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
FinalFC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '02EALL_G01'"
    IAmodel = "02EALL_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = '01HXXXXXXX'"
    IAmodel = "01HXXXXXXX"

#if Proj == "DOT":
#    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    Roadblocks = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_DOT_poly"
#    
#elif Proj == "HRE Culverts":
#    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#    Roadblocks = "XXXXX"
#    
#elif Proj == "All":
#    LULC = "F:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    Roadblocks = "XXXXX"
#    
#elif Proj == "HREP":
#    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
#    Roadblocks = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", "in_plants")
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

# Select out the EOs > or < 250,000 sq meters
arcpy.Select_analysis("in_plants", "pBig", "Shape_Area >= 250000")
arcpy.Select_analysis("in_plants", "pSmall", "Shape_Area < 250000")
arcpy.AddMessage("Plant EOs < 250,000 square meters differentiated.")

# First, explode EO reps into multipart, EO polys
arcpy.MultipartToSinglepart_management("pSmall","pSmallmp")
# Second, assign an ID to the small plant polygons
arcpy.AddField_management("pSmallmp", "pSmallmp_ID", "SHORT")
arcpy.CalculateField_management("pSmallmp", "pSmallmp_ID", "int(!OBJECTID!)", "PYTHON")

####### WETLANDS #######
# Selecting out wetlands from CCAP LU/LC
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.") 

# Selecting out contiguous NWI wetland polys
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)

arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"ATTRIBUTE\" LIKE 'P%'")
arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")
arcpy.AddMessage("NWI Wetland polys have been selected...")

# Selecting out contiguous DEC wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
arcpy.AddMessage("LU/LC SELECT: DEC Wetlands have been selected...")

# Union and Dissolve all wetland components
arcpy.Union_analysis([CCAP_select, "NWI_wet_polys", DEC_wetlands], "WetUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetUnion", "WetDiss", "", "", "SINGLE_PART")
arcpy.AddMessage("Unioned and Dissolved all wetland components...")


####### WETLANDS PER EO POLY #######
# Run IDENTITY on the wetlands and plant EOs
arcpy.Identity_analysis ("pSmallmp", "WetDiss", "outEOwet")

# Make a Frequency Table of the ID'd EOS with Wetlands = total area
arcpy.MakeTableView_management ("outEOwet", "VIEW_outEOwet")
arcpy.Frequency_analysis("VIEW_outEOwet", "outEOwet_freq",["pSmallmp_ID"], ["Shape_Area"])
# Make a Frequency Table of the ID'd EOS with Wetlands = wetland area
arcpy.MakeTableView_management ("outEOwet", "VIEW_outEOwet", "FID_WetDiss > 0")
arcpy.Frequency_analysis("VIEW_outEOwet", "outEOwetONLYwet_freq",["pSmallmp_ID"], ["Shape_Area"])
# Add fields to run calculations on the percentage of wetland in each EO
arcpy.AddField_management("outEOwet_freq", "WetArea", "DOUBLE")
arcpy.AddField_management("outEOwet_freq", "TotalArea", "DOUBLE")
arcpy.AddField_management("outEOwet_freq", "WetAreaPer", "SHORT")
# Calculate total area
arcpy.CalculateField_management("outEOwet_freq", "TotalArea", "!Shape_Area!", "PYTHON")
# Calculate wetland area and then precentage of each EO that is wetland
arcpy.MakeTableView_management ("outEOwet_freq", "VIEW_outEOwetfreq")
arcpy.DeleteField_management("VIEW_outEOwetfreq", ["Shape_Area"])
arcpy.AddJoin_management("VIEW_outEOwetfreq", "pSmallmp_ID", "outEOwetONLYwet_freq", "pSmallmp_ID")
arcpy.CalculateField_management("VIEW_outEOwetfreq", "WetArea", "!Shape_Area!", "PYTHON")
arcpy.SelectLayerByAttribute_management("VIEW_outEOwetfreq", "NEW_SELECTION", "WetArea IS NULL")
arcpy.CalculateField_management("VIEW_outEOwetfreq", "WetArea", "0", "PYTHON")
arcpy.SelectLayerByAttribute_management("VIEW_outEOwetfreq", "CLEAR_SELECTION")
arcpy.CalculateField_management("VIEW_outEOwetfreq", "WetAreaPer", "(!WetArea!/!TotalArea!)*100", "PYTHON")
arcpy.RemoveJoin_management("VIEW_outEOwetfreq", "outEOwetONLYwet_freq")
# Now JOIN the frequency table to the small EO polys, and split the features into two parts:
# >= 50% wetlands and <50% wetlands
arcpy.MakeFeatureLayer_management("pSmallmp", "LAYER_pSmallmp")
arcpy.AddJoin_management("LAYER_pSmallmp", "pSmallmp_ID", "VIEW_outEOwetfreq", "pSmallmp_ID")
arcpy.SelectLayerByAttribute_management("LAYER_pSmallmp", "NEW_SELECTION", "outEOwet_freq.WetAreaPer < 50")
arcpy.CopyFeatures_management ("LAYER_pSmallmp", "B2_lt50")
arcpy.SelectLayerByAttribute_management("LAYER_pSmallmp", "SWITCH_SELECTION")
arcpy.CopyFeatures_management ("LAYER_pSmallmp", "B1_gt50")
arcpy.AddMessage("WETLANDS PER EO POLY...DONE")
    
####### WETLANDS EO POLY PER SMALL GT 50 WETLANDS #######
# 4A. Frequency Tables, Percent of Wetland that is EO poly
# Select the wetlands touching the gt50 wetlands, then assign ID to a joinable field, and then
# run IDENTITY to find how much EO is in the wetland
arcpy.MakeFeatureLayer_management("WetDiss", "LAYER_WetDiss")
arcpy.SelectLayerByLocation_management("LAYER_WetDiss", "INTERSECT", "B1_gt50", "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_WetDiss", "WetDiss_gt50_EOs")
arcpy.AddField_management("WetDiss_gt50_EOs", "wIDeos_ID", "SHORT")
arcpy.CalculateField_management("WetDiss_gt50_EOs", "wIDeos_ID", "int(!OBJECTID!)", "PYTHON")

arcpy.Identity_analysis ("WetDiss_gt50_EOs", "B1_gt50", "WetDiss_ID_EOs")

# Make a Frequency Table of the ID'd wetlands with EOs = total area
arcpy.MakeTableView_management ("WetDiss_ID_EOs", "VIEW_wIDeos")
arcpy.Frequency_analysis("VIEW_wIDeos", "wIDeos_freq",["wIDeos_ID"], ["Shape_Area"])
# Make a Frequency Table of the ID'd wetlands with EOs = EO area
arcpy.MakeTableView_management ("WetDiss_ID_EOs", "VIEW_wIDeos", "FID_B1_gt50 >0")
arcpy.Frequency_analysis("VIEW_wIDeos", "wIDeos_onlyEO_freq",["wIDeos_ID"], ["Shape_Area"])
# Add fields to run calculations on the percentage of EO in each wetland
arcpy.AddField_management("wIDeos_freq", "EOArea", "DOUBLE")
arcpy.AddField_management("wIDeos_freq", "TotalArea", "DOUBLE")
arcpy.AddField_management("wIDeos_freq", "EOAreaPer", "SHORT")
# Calculate total area
arcpy.CalculateField_management("wIDeos_freq", "TotalArea", "!Shape_Area!", "PYTHON")
# Calculate EO area and then precentage of each wetland that is EO
arcpy.MakeTableView_management ("wIDeos_freq", "VIEW_wIDeosfreq")
arcpy.DeleteField_management("VIEW_wIDeosfreq", ["Shape_Area"])
arcpy.AddJoin_management("VIEW_wIDeosfreq", "wIDeos_ID", "wIDeos_onlyEO_freq", "wIDeos_ID")
arcpy.CalculateField_management("VIEW_wIDeosfreq", "EOArea", "!Shape_Area!", "PYTHON")
arcpy.SelectLayerByAttribute_management("VIEW_wIDeosfreq", "NEW_SELECTION", "EOArea IS NULL")
arcpy.CalculateField_management("VIEW_wIDeosfreq", "EOArea", "0", "PYTHON")
arcpy.SelectLayerByAttribute_management("VIEW_wIDeosfreq", "CLEAR_SELECTION")
arcpy.CalculateField_management("VIEW_wIDeosfreq", "EOAreaPer", "(!EOArea!/!TotalArea!)*100", "PYTHON")
arcpy.RemoveJoin_management("VIEW_wIDeosfreq", "wIDeos_onlyEO_freq")
# Now JOIN the frequency table to the wetland polys, and split the features into two parts:
# >= 10% EO and <10% EO
arcpy.MakeFeatureLayer_management("WetDiss_gt50_EOs", "LAYER_Wet10")
arcpy.AddJoin_management("LAYER_Wet10", "wIDeos_ID", "VIEW_wIDeosfreq", "wIDeos_ID")
arcpy.SelectLayerByAttribute_management("LAYER_Wet10", "NEW_SELECTION", "wIDeos_freq.EOAreaPer < 10")
arcpy.CopyFeatures_management ("LAYER_Wet10", "B1b_Wetlands_LT10")
arcpy.SelectLayerByAttribute_management("LAYER_Wet10", "SWITCH_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Wet10", "B1a_Wetlands_GT10")
arcpy.AddMessage("WETLANDS EO POLY PER SMALL GT 50 WETLANDS...DONE")

# Locate the EO polys that are >50% wetland, and yet make up >10% of the wetland they are in, and then the EOs that
# make up <10% of the wetlands they are in
arcpy.MakeFeatureLayer_management("B1_gt50", "LAYER_pSmall_gt50")
arcpy.SelectLayerByLocation_management("LAYER_pSmall_gt50", "INTERSECT", "B1a_Wetlands_GT10", "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_pSmall_gt50", "B1a_GT10")
arcpy.SelectLayerByAttribute_management("LAYER_pSmall_gt50", "SWITCH_SELECTION")
arcpy.CopyFeatures_management ("LAYER_pSmall_gt50", "B1b_LT10")
arcpy.AddMessage("GT50 EOs pulled out and split into LT10 and GT10 of wetland...")

# Buffer the "B1a_Wetlands_GT10" wetlands for later use
arcpy.Buffer_analysis("B1a_Wetlands_GT10", "B1a_GT10_BUFFWET", 90, "FULL", "ROUND", "ALL", "")

# Buffer B1b_LT10 EOs and then 'merge' them with unbuffered B1a_GT10
arcpy.Buffer_analysis("B1b_LT10", "B1b_LT10_BUFF", 90, "FULL", "ROUND", "ALL", "")

# Buffer B2_LT50
arcpy.Buffer_analysis("B2_lt50", "B2_lt50_BUFF", 90, "FULL", "ROUND", "ALL", "")

# 'Merge' B1a_GT10 EOs with B1a_Wetlands_GT10 wetlands
arcpy.Union_analysis(["B1b_LT10_BUFF", "B1b_Wetlands_LT10"], "B1b_LT10_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("B1b_LT10_Union", "B1b_LT10_Merge", "", "", "SINGLE_PART")

# 'Merge' EOs and EO based buffers (all GT50 EOs)
arcpy.Union_analysis(["B1a_GT10", "B1b_LT10_BUFF", "B2_lt50_BUFF"], "B3_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("B3_Union", "B3_Merge", "", "", "SINGLE_PART")
arcpy.AddMessage("Unioned and Dissolved B3...")

# Run the land cover-slope (PAL) module, but first establish an ID field
arcpy.AddField_management("B3_Merge", "ORIG_ID", "SHORT")
arcpy.CalculateField_management("B3_Merge", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")

arcpy.AddMessage("Wetland buffering and merging done, ready for LCSLP module...")

# Run the Land Cover Type and Slope Module
value_field = "ORIG_ID"
cell_size = 15
in_buff = "B3_Merge"
in_buff_ring = "B3_Merge_ring"
out_buff = "B3_LCSLP"

# Create a small buffer to calc flow-in/flow-out
arcpy.Buffer_analysis("B3_Merge", in_buff_ring, 30, "FULL", "ROUND",  "LIST", "ORIG_ID")
import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)
arcpy.AddMessage("Land Cover Type and Slope Module Complete...")

# 'Merge' LCSLP based buffers with previous merge and wetland buff
arcpy.Union_analysis([out_buff, "B1b_LT10_Merge", "B1a_GT10_BUFFWET"], "B4_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("B4_Union", "B4_Merge", "", "", "SINGLE_PART")
arcpy.AddMessage("Unioned and Dissolved B4...")

# Road part 50m from Wet Buffer
# Buffer The new buffered polys 50m to see what roads they catch:
arcpy.Buffer_analysis("B4_Merge", "B4_Merge_BUFF", 50, "FULL", "ROUND", "ALL", "")
arcpy.Clip_analysis("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "B4_Merge_BUFF", "roads_within_wet_buff")
arcpy.Buffer_analysis("roads_within_wet_buff", "Road50_BUFF", 50, "FULL", "FLAT", "ALL", "")
arcpy.Union_analysis(["B4_Merge", "Road50_BUFF"], "Road50_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("Road50_Union", "Road50_Merge", "", "", "SINGLE_PART")
arcpy.AddMessage("Road 50m analysis done...")

# Road part 200m from EO
# Buffer The new buffered polys 200m to see what roads they catch:
arcpy.Buffer_analysis("pSmallmp", "pSmallmp_BUFF", 200, "FULL", "ROUND", "ALL", "")
arcpy.Clip_analysis("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "pSmallmp_BUFF", "roads_200m_fromEO")
arcpy.Buffer_analysis("roads_200m_fromEO", "Road200_BUFF", 200, "FULL", "FLAT", "ALL", "")
arcpy.Union_analysis(["Road50_Merge", "Road200_BUFF"], "Road200_Union", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("Road200_Union", "Road200_Merge", "", "", "SINGLE_PART")
arcpy.AddMessage("Road 200m analysis done...")

# Eliminate the road features
arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\AIMS.alisroads", "LAYER_alisroads")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", "Road200_Merge", "", "NEW_SELECTION")
arcpy.Buffer_analysis("LAYER_alisroads", "Road200_CLIPBUFF", 6.25, "FULL", "ROUND", "ALL", "")
arcpy.Erase_analysis("Road200_Merge","Road200_CLIPBUFF","Road200_Erase")
# There must be some sort of bug, because when I tri the multipart command below, ArcMap vaporizes.
# So I fooled it with a dissolve, which does the same thing
# IT BLOWS UP WITH THIS: arcpy.MultipartToSinglepart_management("Road200_Erase","Road200_Erasemp")
arcpy.Dissolve_management("Road200_Erase", "Road200_Erasemp", "", "", "SINGLE_PART")

arcpy.MakeFeatureLayer_management("Road200_Erasemp", "LAYER_Road200_Erase")
#arcpy.SelectLayerByLocation_management("LAYER_Road200_Erase", "INTERSECT", "pSmallmp", "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Road200_Erase", "RoadlessBuffs")
arcpy.AddMessage("Roads eliminated...")

# Merge the buffers with the small EOs, and dissolve
# The buffer all of it 10m
arcpy.Union_analysis(["pSmallmp", "RoadlessBuffs"], "EndUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("EndUnion", "EndMerge", "", "", "SINGLE_PART")
arcpy.Buffer_analysis("EndMerge", "EndMergeBUFF", 10, "FULL", "ROUND", "ALL", "")
arcpy.AddMessage("Buffers merged to small EO polys, and everything got a 10m buffer...")

# Merge the small EO buffers back to the non-buffered large EOs
arcpy.Union_analysis(["pBig", "EndMergeBUFF"], "finalUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.AddMessage("Large, unbuffered plant EOs and smaller, buffer EOs merged...")

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
###########arcpy.AggregatePolygons_cartography ("finalUnion", "Elim", 1, 0, 100000)
arcpy.AddField_management("finalUnion", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("finalUnion", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("finalUnion", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST
arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)
#arcpy.CopyFeatures_management ("Elim", "G:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Plants.")















