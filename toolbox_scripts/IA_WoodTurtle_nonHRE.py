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
NHDplusHydro = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/Hydrography/nhdflowline.shp"
NHDplusCatch = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/drainage/catchment.shp"
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

# First buffer the EO for locational uncertainty and to make it a polygon.
arcpy.Buffer_analysis(in_put, "in_put10", 10, "FULL", "ROUND", "ALL")

# Buffer the EO to catch the segments.
arcpy.Buffer_analysis(in_put, in_put_buff, 300, "FULL", "ROUND", "ALL")

# Select the stream segments associated with the buffered EO.
arcpy.AddMessage("Prepping for upstream/downstream analysis....")
arcpy.MakeFeatureLayer_management(NHDplusHydro, "LAYER_NHDplusHydro")
arcpy.SelectLayerByLocation_management("LAYER_NHDplusHydro", "INTERSECT", "in_put_buff", "", "NEW_SELECTION")
arcpy.CreateTable_management(WSP, "COMID_table", "C:\_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults")

#####
# "DNDIV" NatT function not working properly in NHD script (it is only capturing downstream mainstem - no divergences)
# So I will capture all downstream mainsteam (500 meters), and then UPTRIB and capture the whole watershed for that lowest
# segment. This will accomplish the same thing (although not as efficiently as if DNDIV worked.
#####

# Run the NHD Navigation script
arcpy.AddMessage("Running DOWNSTREAM mainstem....")
HydroRows = arcpy.SearchCursor("LAYER_NHDplusHydro")
for HydroRow in HydroRows:
    # Upstream Trib variables
    NavT = "DNMAIN"
    StartC = HydroRow.COMID
    comidPrint = repr(StartC)
    arcpy.AddMessage(comidPrint)
    StartM = 0
    MaxD = 0.50
    DataP = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02"
    AppP = "C:/_Schmid/_project/Important_Areas/geo_scripts/NHD_scripts/VAACOMObjectNavigator/"

    import IA_mod_nhdNAV
    IA_mod_nhdNAV.NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP)
     
    arcpy.Append_management("C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults", "COMID_table", "TEST")
    arcpy.CopyRows_management("COMID_table", "COMID_table_DNMAIN")

# Run the NHD Navigation script
arcpy.AddMessage("Running UPSTREAM, including tribs....")
HydroRows = arcpy.SearchCursor("COMID_table_DNMAIN")
for HydroRow in HydroRows:
    # Upstream Trib variables
    NavT = "UPTRIB"
    StartC = HydroRow.COMID
    comidPrint = repr(StartC)
    arcpy.AddMessage(comidPrint)
    StartM = 0
    MaxD = 0
    DataP = "C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02"
    AppP = "C:/_Schmid/_project/Important_Areas/geo_scripts/NHD_scripts/VAACOMObjectNavigator/"

    import IA_mod_nhdNAV
    IA_mod_nhdNAV.NHDNav_module(WSP, NavT, StartC, StartM, MaxD, DataP, AppP)
     
    arcpy.Append_management("C:/_Schmid/_GIS_Data/nhdplus/NHDPlus02/TNavWork.mdb/tblNavResults", "COMID_table", "TEST")

# Select out the segments
arcpy.AddMessage("Selecting river segments from COMID table....")
arcpy.MakeFeatureLayer_management(FBP_flowlines, "LAYER_FBP_flowlines")
arcpy.AddJoin_management("LAYER_FBP_flowlines", "COMID", "COMID_table", "Comid", "KEEP_COMMON")
arcpy.CopyFeatures_management("LAYER_FBP_flowlines", "flowlines")

# Buffer the EO 10m buffer with 500m to clip the stream segments.
arcpy.AddMessage("Buffering EOs 500 meters....")
arcpy.Buffer_analysis("in_put10", "in_put500", 500, "FULL", "ROUND", "ALL")

#Clip the flowlines
arcpy.AddMessage("Clipping river segments to 500 meters....")
arcpy.Clip_analysis("flowlines", "in_put500", "clipped_flowlines")

# Buffer the clipped flowlines 300m.
arcpy.AddMessage("Buffering selected river segments 300 meters....")
arcpy.Buffer_analysis("clipped_flowlines", "clipflow300", 300, "FULL", "ROUND", "ALL")

#Run terrestrial community module
arcpy.AddMessage("Running Terrestrial Community model....")
arcpy.MultipartToSinglepart_management("clipflow300","clipflow300sp")
inputPar = "clipflow300sp"
outputPar = "outTerr"
import IA_mod_terrestrial
IA_mod_terrestrial.TerrestrialModule(inputPar, outputPar)

################### Alis Roads (Class 1 only)
################### I had to place the select by attribute before the select by location, because there is a software
################### bug when you try to select by location on a very large SDE dataset. Sheesh.

arcpy.AddMessage("Removing selected Roads....")
arcpy.MakeFeatureLayer_management("Database Connections/bloodhound.sde/AIMS.alisroads", "LAYER_alisroads")
arcpy.SelectLayerByAttribute_management("LAYER_alisroads", "NEW_SELECTION", "\"ACC\" = 1 OR \"ACC\" = 2 OR \"ACC\" = 3")
arcpy.SelectLayerByLocation_management("LAYER_alisroads", "INTERSECT", outputPar, "", "SUBSET_SELECTION")
arcpy.MakeFeatureLayer_management("LAYER_alisroads", "LAYER_selected_alisroads")
arcpy.Buffer_analysis("LAYER_selected_alisroads", "Buff_alisroads", 6.25, "FULL", "ROUND", "ALL", "")
arcpy.Erase_analysis(outputPar, "Buff_alisroads", "Erase")

################### Extracting the CCAP uplands and erase from buffer
###################
arcpy.AddMessage("Removing CCAP developed/barren land LU/LC....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAP", CCAP_Select_Query)
arcpy.RasterToPolygon_conversion("LAYER_CCAP", "polys_CCAP", "NO_SIMPLIFY", "VALUE")
arcpy.Erase_analysis("Erase", "polys_CCAP", "Erase2")

# Add the IA_MODEL_R field - I tried dissolving (which may be extraneous anyway)
# and came up with memory issues, so I just write to the final layer for now. 
#
arcpy.AddField_management("Erase2", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("Erase2", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("Erase2", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
#Since the SINGLE_PART function in previous step is mysteriously not working:
arcpy.MultipartToSinglepart_management("Dissolve","Dissolvesp")


# Select out only those polys contiguous with the EO
arcpy.MakeFeatureLayer_management("Dissolvesp", "LAYER_Dissolvesp")
arcpy.SelectLayerByLocation_management("LAYER_Dissolvesp", "INTERSECT", "in_put10", "", "NEW_SELECTION")

################### WRAP UP
################### 

arcpy.CopyFeatures_management ("LAYER_Dissolvesp", FinalFC)
arcpy.CopyFeatures_management ("LAYER_Dissolvesp", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Wood Turtle.")















