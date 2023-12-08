# ---------------------------------------------------------------------------
# IA_palustrine.py
# Created on: 2010 April 27
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Tim Howard, Program Scientist, NYNHP)
# Usage: Important Area Model for NYNHP palustrine communities
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   *******SPECIAL REVISION NOTE: SSURGO 2 SOILS HAVE BEEN INCORPORATED*******
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

sys.path.insert(1, 'H:/Please_Do_Not_Delete_me/Important_Areas/IA_Archive/toolbox_scripts')

# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "H:/Please_Do_Not_Delete_me/Important_Areas/scratch2023.gdb"  #2023 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Communities_Palustrine"
#in_put = arcpy.GetParameterAsText(0)
#in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
in_put="H:\\_Conley_Backup\\D_Git\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts"
##EXorHIST = arcpy.GetParameterAsText(1)
EXorHIST = "Extant"
##tyme = arcpy.GetParameterAsText(2)
tyme="12_07_2023"
##Proj = arcpy.GetParameterAsText(3)
Proj = "HREP"

#in_EOs = "in_EOs"
in_EOs= "in_EOs" ##Test with old input for new paths
CCAP_select = "CCAP_select"
CCAP_Select_Query = "VALUE = 13 OR VALUE = 14 OR VALUE = 15 OR VALUE = 22"

#FinalFC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EALL_NOB'" ##Changed the code for 2023 testing to the RAPWINCA code since no Pal Comm in old sample
    #IAmodel = "03EPAL_G01"
    IAmodel ="01EALL_NOB"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXX'"
    IAmodel = "XXXXX"

if Proj == "DOT":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    Roadblocks = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_DOT_poly"
    
elif Proj == "HRE Culverts":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
    Roadblocks = "XXXXX"
    
elif Proj == "All":
    LULC = "F:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    Roadblocks = "XXXXX"
    
elif Proj == "HREP":
    #LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    LULC ="H:/Please_Do_Not_Delete_me/Important_Areas/HRE_2016_ccap_corrected.tif" ##Updated 2016 CCAP clipped to HRE extent 10 counties plus
    #StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
    StudyArea = "H:/Please_Do_Not_Delete_me/_Schmid/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"  #Updated path to stored J. Schmidt Files no new data
    #Roadblocks = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"
    Roadblocks = "H:/Please_Do_Not_Delete_me/_Schmid/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"#Updated path to stored J. Schmidt Files no new data





print("Palustrine Communities model")


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
print("In EOs selected. " + EXorHIST + " " + ModelType)

################### Determine contiguous CCAP palustrine wetlands
###################
in_features = in_EOs
import IA_mod_lulc_select
IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
print("LU/LC SELECT: CCAP Wetlands have been selected...")
 
# Union the input EOs and wetlands.
arcpy.Union_analysis([in_EOs, CCAP_select], "WetUnion", "ONLY_FID", "", "NO_GAPS")
arcpy.Dissolve_management("WetUnion", "WetDiss", "", "", "SINGLE_PART")

################### Run palustrine community module ###################
###################
value_field = "ORIG_ID"
cell_size = 15
in_buff = "WetDiss"
in_buff_ring = "in_buff_ring"
out_buff = "out_buff"

# Apply baseline buffer: 163m
arcpy.AddField_management("WetDiss", "ORIG_ID", "SHORT")
arcpy.CalculateField_management("WetDiss", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
arcpy.Buffer_analysis("WetDiss", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")

import IA_mod_assessLCSLP
IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)


################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management(out_buff, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(out_buff, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management(out_buff, "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve2", "Elim", "AREA", 3000)

################### WRAP UP
################### 
FinalFC= "H:\\Please_Do_Not_Delete_me\\\Important_Areas" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="H:\\Please_Do_Not_Delete_me\\\Important_Areas\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST


arcpy.CopyFeatures_management ("Elim", FinalFC)
arcpy.CopyFeatures_management ("Elim", FinalFC_gdb)

print("IA model done: Palustrine Communities.")






