# ---------------------------------------------------------------------------
# IA_mod_estuarine.py
# Created on: 2011 August
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Tim Howard, Program Scientist, NYNHP)
# Usage: Important Area Model that need the estuarine community IA methodology
# Latest Edits: Update to arcpy module
#   Dependency: IA_mod_wetland_select.py
# Shall not be distributed without permission from the New York Natural Heritage Program
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
#arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
arcpy.env.snapRaster ="H:\\Please_Do_Not_Delete_me\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met" 
# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace

# Load required toolboxes...
arcpy.env.overwriteOutput = True


def EST_module(in_estvar, out_estvar, WSP, LULC):

    est_comms = in_estvar
    CCAP_select = "CCAP_select"
    CCAP_Select_Query = "\"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 16 OR \"VALUE\" = 17 OR \"VALUE\" = 18 OR \"VALUE\" = 22 OR \"VALUE\" = 23"
    arcpy.AddMessage("Estuarine methodolody = ESTMOD")
    

    ################### Wetland adjacency
    ###################

    # Join the comm_v field from commcode table to the selected county estuarine EOs
    arcpy.AddMessage("ESTMOD: Join the comm_v field from commcode table to the selected county estuarine EOs...")
    arcpy.MakeTableView_management("H:\\Please_Do_Not_Delete_me\\_Schmid\\Important_Areas\\GIS_Data\\IA_Process.gdb\\_LUT_estuarine_comms", "VIEW_LUT_commcode")
    arcpy.MakeFeatureLayer_management(est_comms, "LAYER_est_comms")
    arcpy.AddJoin_management("LAYER_est_comms", "SCIEN_NAME", "VIEW_LUT_commcode", "SCIEN_NAME")
    arcpy.CopyFeatures_management("LAYER_est_comms", "est_comms_commcode")
    arcpy.AddMessage("ESTMOD: Commcode table, joined.")

    # Assign the un-buffered EOs to the in_EOs variable and run wetlands selection module: CCAP Wetlands 
    arcpy.AddMessage("ESTMOD: Run wetlands selection module: CCAP Wetlands...")
    in_features = est_comms
    import IA_mod_lulc_select
    IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
    arcpy.AddMessage("ESTMOD: Wetlands have been selected.")

    # Union the selected EOs w/commcode to the CCAP wetlands they touch.
    arcpy.AddMessage("ESTMOD: Union the selected EOs w/commcode to the CCAP wetlands they touch...")
    arcpy.Union_analysis("est_comms_commcode ; CCAP_select", "Step1Union", "", "")
    arcpy.Dissolve_management("Step1Union", "Step1Dissolve", "", "", "SINGLE_PART")

    #Run the Spatial Join tool, CCAP wetlands
    arcpy.AddMessage("ESTMOD: Do spatial join: CCAP wetlands with the EOs commocode...")
    arcpy.SpatialJoin_analysis("Step1Dissolve", "est_comms_commcode", "step1_spatjoin")
    arcpy.AddMessage("ESTMOD: CCAP selection, done.")

    ################### Temporary 100m buffer
    ###################
                  
    arcpy.AddMessage("ESTMOD: Creating temporary 100m buffer...")
    # Buffer the nibbled feaures 100 meters
    arcpy.Buffer_analysis("step1_spatjoin", "SpatJoin_buff", 100, "FULL", "ROUND", "NONE", "")
    # Dissolve the nibbled polys out of the buffered polys to make an analysis buffer
    arcpy.Dissolve_management("SpatJoin_buff", "SpatJoin_diss", "", "", "SINGLE_PART")
    arcpy.Erase_analysis("SpatJoin_diss", "step1_spatjoin", "SpatJoin_erase", "")
    arcpy.AddMessage("ESTMOD: Temp 100m buffer, ready.")
    
    ################### High Intensity land use
    ###################
                  
    arcpy.AddMessage("ESTMOD: Determining high intensity land use...")
    # Create layer of CCAP Hi intensity LU
    arcpy.Cellsize = 15
    arcpy.XYTolerance = "0.02"
    arcpy.MakeRasterLayer_management(LULC, "LAYER_CCAPHI", "\"VALUE\" = 2")
    # Add next step so that snapraster applies to CCAP
    arcpy.CopyRaster_management("LAYER_CCAPHI", "LAYER_CCAPHIpre")
    arcpy.RasterToPolygon_conversion("LAYER_CCAPHIpre", "polys_CCAPHI", "NO_SIMPLIFY", "VALUE")
    # Clip the hi intensity LU within the buffer from Part 2
    arcpy.Clip_analysis("polys_CCAPHI", "SpatJoin_erase", "CCAPHI_buff")
    # Buffer the nibbled feaures 100 meters
    arcpy.Buffer_analysis("CCAPHI_buff", "CCAPHI_buff2", 100, "FULL", "ROUND", "NONE", "")
    arcpy.AddMessage("ESTMOD: Hi-Intensity LC, analyzed.")

    ################### Identity with high intensity land use
    ###################
                  
    arcpy.AddMessage("ESTMOD: Clip the hi intensity LU within the buffer...")
    # Clip the hi intensity LU within the buffer
    arcpy.Identity_analysis("step1_spatjoin", "CCAPHI_buff2", "Step4Identity")
    arcpy.AddMessage("ESTMOD: Parts of the Step 1 polys that are in the 100m HILU 100m buffer, have been identified.")

    ################### Apply buffer to base polygon, based on land use and community type
    ###################
                  
    arcpy.AddMessage("ESTMOD: Apply buffer to base polygon, based on land use and community type...")
    arcpy.AddField_management("Step4Identity", "IA_Calculated_Buffer", "DOUBLE")
    rows = arcpy.UpdateCursor("Step4Identity")
    for row in rows:
        if row.BUFF_DIST == None:
            row.BUFF_DIST = 0
            rows.updateRow(row)
        if row.BUFF_DIST == 0 and row._LUT_estuarine_comms_IA_CATEGORY == "WT":
            row.IA_Calculated_Buffer = 15
            rows.updateRow(row)
        elif row.BUFF_DIST == 100 and row._LUT_estuarine_comms_IA_CATEGORY == "WT":
            row.IA_Calculated_Buffer = 30
            rows.updateRow(row)
        elif row.BUFF_DIST == 0 and row._LUT_estuarine_comms_IA_CATEGORY == "NWT":
            row.IA_Calculated_Buffer = 30
            rows.updateRow(row)
        elif row.BUFF_DIST == 100 and row._LUT_estuarine_comms_IA_CATEGORY == "NWT":
            row.IA_Calculated_Buffer = 46
            rows.updateRow(row)
        elif row.BUFF_DIST == 0 and row._LUT_estuarine_comms_IA_CATEGORY == "SM":
            row.IA_Calculated_Buffer = 15
            rows.updateRow(row)
        elif row.BUFF_DIST == 100 and row._LUT_estuarine_comms_IA_CATEGORY == "SM":
            row.IA_Calculated_Buffer = 30
            rows.updateRow(row)
        else:
            row.setValue("IA_Calculated_Buffer", "0")
            rows.updateRow(row)
    arcpy.AddMessage("ESTMOD: Buffer distances have been attributed.")
    
    # Estuarine polys buffer according to subclass: woody tidal, non-woody tidal, or salt marsh.
    arcpy.AddMessage("Buffering....")
    arcpy.Buffer_analysis("Step4Identity", "Step5interim", "IA_Calculated_Buffer", "FULL", "ROUND", "LIST", "OBJECTID")
    arcpy.MultipartToSinglepart_management("Step5interim","Step5Buffer")
    arcpy.AddMessage("ESTMOD: Buffers completed.")

    arcpy.CopyFeatures_management ("Step5Buffer", out_estvar)

    arcpy.AddMessage("ESTMOD: FINISHED")

