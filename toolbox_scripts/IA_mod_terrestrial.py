# ---------------------------------------------------------------------------
# IA_Terrestrial.py
# Created on: 2010 May 24
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


def TerrestrialModule(inputPar, outputPar):

    arcpy.AddMessage("Important Areas: TERRESTRIAL COMMUNTIES")

    ################# Separate out small patch vs. matrix
    ################# 
    arcpy.AddMessage("Separate out small patch vs. matrix...")

    arcpy.MakeFeatureLayer_management(inputPar, "LAYER_inputPar")
    arcpy.SelectLayerByAttribute_management("LAYER_inputPar", "NEW_SELECTION", "\"Shape_Area\" < 8093745")
    arcpy.CopyFeatures_management("LAYER_inputPar", "PaTch")
    arcpy.SelectLayerByAttribute_management("LAYER_inputPar", "SWITCH_SELECTION")
    arcpy.CopyFeatures_management("LAYER_inputPar", "MaTrix")

    ##################### 15 meter baseline buffer
    #####################   
    arcpy.AddMessage("Apply baseline buffer: 15m")
    arcpy.Buffer_analysis("PaTch", "PaTch_15", 15, "FULL", "ROUND", "ALL", "")


    ##################### Assess Land Cover Type and Slope
    #####################
    arcpy.AddMessage("Start the Assess Land Cover Type and Slope Module")
    value_field = "OBJECTID"
    cell_size = 5
    in_buff = "PaTch"
    in_buff_ring = "PaTch_15"
    out_buff = "out_buff"
        
    import IA_mod_assessLCSLP
    IA_mod_assessLCSLP.ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)


    # Combine the matrix and buffered patches
    arcpy.Union_analysis(["MaTrix", out_buff], "MaTrix_PaTch", "ONLY_FID", "", "NO_GAPS")
    arcpy.Dissolve_management("MaTrix_PaTch", outputPar, "", "", "MULTI_PART")

    arcpy.AddMessage("Terrestrial Community Important Areas Complete.")

