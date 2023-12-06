# ---------------------------------------------------------------------------
# IA_Terrestrial.py
# Created on: 2012 May 7
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Tim Howard, Program Scientist, NYNHP)
# Usage: Important Area Model for NYNHP terrestrial communities
#   Dependency: IA_mod_assessLCSLP.py
# Shall not be distributed without permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#

# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"

# Workspace
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True

ModelType = "Communities_Terrestrial"
#in_put = arcpy.GetParameterAsText(0)
#EXorHIST = arcpy.GetParameterAsText(1)
#tyme = arcpy.GetParameterAsText(2)
#Proj = arcpy.GetParameterAsText(3)


in_EOs = "in_EOs"
inputPar = "inputPar"
outputPar = "outputPar"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST


if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '03ETER_G01'"
    IAmodel = "03ETER_G01"
elif EXorHIST == "Historical":
    selectQuery = "IA_MODEL = 'XXXXXXXXXX'"
    IAmodel = "XXXXXXXXXX"
#
#if Proj == "DOT":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
#    Roadblocks = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_DOT_poly"
#    
#elif Proj == "HRE Culverts":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"
#    Roadblocks = "XXXXX"
#    
#elif Proj == "All":
#    LULC = "C:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
#    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
#    Roadblocks = "XXXXX"
#    
#elif Proj == "HREP":
#    LULC = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
#    StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
#    Roadblocks = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/ALIS_ACC1and2_HREP_poly"


# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)
arcpy.AddMessage("In EOs selected. " + EXorHIST + " " + ModelType)

# Dissolve together the terrestrial community EOs in question
arcpy.Dissolve_management(in_EOs, inputPar, "", "", "SINGLE_PART")

#test
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test1.shp"
arcpy.CopyFeatures_management(inputPar, test_step)

# Select CCAP wetlands
inputPar = "in_EOs"
import IA_mod_terrestrial

##################
test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test2.shp"
arcpy.CopyFeatures_management(in_buff_ring, test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test2b.shp"
arcpy.CopyFeatures_management(in_buff, test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test3.shp"
arcpy.CopyFeatures_management("ringvar1", test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test4.tif"
arcpy.CopyRaster_management("ccap_buff", test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test5.tif"
arcpy.CopyRaster_management("ccap_RECL", test_step)


test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test6.tif"
arcpy.CopyRaster_management("buff_shed", test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test7.tif"
arcpy.CopyRaster_management("slope_buff", test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test8.tif"
arcpy.CopyRaster_management("LC_raster", test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test8b.tif"
arcpy.CopyRaster_management("cover_slope", test_step)


test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test9.shp"
arcpy.CopyFeatures_management("cover_slope_polys", test_step)

test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test9b.shp"
arcpy.CopyFeatures_management("cover_slope_polys2", test_step)


test_step= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + "_test10.shp"
arcpy.CopyFeatures_management("Final_Buff", test_step)



######################
IA_mod_terrestrial.TerrestrialModule(inputPar, outputPar)
arcpy.AddMessage("Terrestrial Module complete")

################### Aggregate and Dissolve all
###################
# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 

arcpy.AddField_management(outputPar, "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management(outputPar, "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")

arcpy.Dissolve_management(outputPar, "Dissolve2", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.MakeFeatureLayer_management("Dissolve2", "LAYER_Elim")
arcpy.SelectLayerByLocation_management("LAYER_Elim", "INTERSECT", in_EOs, "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_Elim", "Contiguous")

##################### WRAP UP
##################### 
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST

arcpy.CopyFeatures_management ("Contiguous", FinalFC)
arcpy.CopyFeatures_management ("Contiguous", FinalFC_gdb)

