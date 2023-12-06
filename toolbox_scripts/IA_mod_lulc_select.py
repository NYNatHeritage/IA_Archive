# ---------------------------------------------------------------------------
# IA_common_functions.py
# Created on: 2011 August
#   (created by John Schmid, GIS Specialist, NYNHP)
# Usage: This script lists functions used commonly in most, if not all, IA models
#
# Revision: Update to arcpy module
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
#arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
arcpy.env.snapRaster ="F:\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met" 
# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
# Load required toolboxes...
arcpy.env.overwriteOutput = True

#
# NEW Process: CCAP (2005) EXTRACT FUNCTIONS *****************************

def CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query):

    #   Extracting the CCAP Wetlands, no water.
##    arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAPW", CCAP_Select_Query)
##    # Add next step so that snapraster applies to CCAP
##    arcpy.CopyRaster_management("LAYER_CCAPW", "CCAPW")
##    arcpy.RasterToPolygon_conversion("CCAPW", "CCAP_temp", "NO_SIMPLIFY", "VALUE")
    arcpy.gp.Con_sa(LULC, "1", "LAYER_CCAP", "0", CCAP_Select_Query)
    arcpy.gp.SetNull_sa("LAYER_CCAP", "1", "LAYER_CCAPnull", "\"Value\" = 0")
    arcpy.Buffer_analysis(in_features, "out_clipEO", 5000, "FULL", "ROUND", "NONE", "")
    arcpy.gp.ExtractByMask_sa("LAYER_CCAPnull", "out_clipEO", "extractedLU")
    arcpy.RasterToPolygon_conversion("extractedLU", "CCAP_LU_clean", "NO_SIMPLIFY", "VALUE")

    # Tried the above as a quicker alternative to the commented out older sections.
    
    
    # This part added by John: Create a 2km clip buffer of the in features, because if it is not used
    # The CCAP/LU selection includes Lake Ontario, the Hudson River, and LI Sound. Also, the later
    # Buffering of 1 meter is easier to process with only the relevant polys to contend with
##    arcpy.Buffer_analysis(in_features, "out_clipEO", 5000, "FULL", "ROUND", "NONE", "")
##    arcpy.Clip_analysis("CCAP_temp", "out_clipEO", "CCAP_LU_clean")
##    arcpy.AddMessage("CCAP Wetlands have been clipped to 2000meters.")
    # This buffer is insignificant in dimension, but allows for kitty-corner cells to be counted
    # as adjacent. The only way I can find to capture kitty-corner cells.
##    arcpy.Dissolve_management("CCAP_LU_clean", "CCAP_LU_clean2")
##    arcpy.Buffer_analysis("CCAP_LU_clean2", "polys_CCAPWtemp", "1", "FULL", "ROUND", "ALL")
##    arcpy.MultipartToSinglepart_management("polys_CCAPWtemp", "polys_CCAPW")
##    arcpy.MakeFeatureLayer_management("polys_CCAPW", "LAYER_polys_CCAPW", "", "", "")
##    arcpy.SelectLayerByLocation_management("LAYER_polys_CCAPW", "INTERSECT", in_features, "", "NEW_SELECTION")

    arcpy.Dissolve_management("CCAP_LU_clean", "CCAP_LU_clean2")
    arcpy.Buffer_analysis("CCAP_LU_clean2", "polys_CCAPWtemp", "1", "FULL", "ROUND", "ALL")
    arcpy.MultipartToSinglepart_management("polys_CCAPWtemp", "polys_CCAPW")
    arcpy.MakeFeatureLayer_management("polys_CCAPW", "LAYER_polys_CCAPW", "", "", "")
    arcpy.SelectLayerByLocation_management("LAYER_polys_CCAPW", "INTERSECT", in_features, "", "NEW_SELECTION")


    LUrows = arcpy.SearchCursor("LAYER_polys_CCAPW")
    for LUrow in LUrows: 

        if LUrow == None:
            arcpy.CreateFeatureClass_management(WSP, CCAP_select, "POLYGON")
            arcpy.AddMessage("No CCAP Wetlands....empty F.C. created.")
        else:
            arcpy.FeatureToPolygon_management("LAYER_polys_CCAPW", CCAP_select, "", "ATTRIBUTES", "")
            arcpy.AddMessage("CCAP Wetlands...found.")
        break
    
def NWI_polys(in_features, NWI_select, WSP):  
    
    # Selecting NWI Wetland polys
    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\SDEADMIN.nc_nwi_poly_2016", "LAYER_NWI_P")
    arcpy.SelectLayerByLocation_management("LAYER_NWI_P", "INTERSECT", in_features, "", "NEW_SELECTION")
    arcpy.CopyFeatures_management ("LAYER_NWI_P", NWI_select)

def NWI_lines(in_features, NWI_select_lines, WSP):  
    
    # Selecting NWI Wetland polys
    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\SDEADMIN.nc_nwi_line2008", "LAYER_NWI_L")
    arcpy.SelectLayerByLocation_management("LAYER_NWI_L", "INTERSECT", in_features, "", "NEW_SELECTION")
    arcpy.CopyFeatures_management ("LAYER_NWI_L", NWI_select_lines)


def DEC_wetlands(in_features, DEC_wetlands, WSP):  
    arcpy.AddMessage("DEC Wetlands in....")
    # Selecting DEC Wetlands
    arcpy.MakeFeatureLayer_management("M:\\gis_util\\connectfiles\\gisview@gisprod_default_10.0.sde\\ARCS.fwwetpol_reguwet", "LAYER_DECW", "", "", "")
    arcpy.SelectLayerByLocation_management("LAYER_DECW", "INTERSECT", in_features, "", "NEW_SELECTION")
    arcpy.FeatureToPolygon_management("LAYER_DECW", "DECWmp", "", "ATTRIBUTES", "")
    arcpy.MultipartToSinglepart_management("DECWmp", "DECWsp")
    arcpy.MakeFeatureLayer_management("DECWsp", "LAYER_DECWsp", "", "", "")
    arcpy.SelectLayerByLocation_management("LAYER_DECWsp", "INTERSECT", in_features, "", "NEW_SELECTION")

    DECrows = arcpy.SearchCursor("LAYER_DECWsp")
    for DECrow in DECrows: 

        if DECrow == None:
            arcpy.CreateFeatureClass_management(WSP, DEC_wetlands, "POLYGON")
            arcpy.AddMessage("No DEC Wetlands....empty F.C. created.")
        else:
            arcpy.FeatureToPolygon_management("LAYER_DECWsp", DEC_wetlands, "", "ATTRIBUTES", "")
            arcpy.AddMessage("DEC Wetlands...found.")   
        break

