# ---------------------------------------------------------------------------
# IA_WetlandBirds.py
# Created on: 2011 November 23
#   
#   (created by John Schmid, GIS Specialist, NYNHP)
#   (methodology by Hollie Shaw, Zoologist, NYNHP)
# Usage: Important Area Model for Tiger Salamander (Ambystoma tigrinum)
#   Dependency: IA_mod_palustrine.py
# Shall not be distributed without permission from the New York Natural Heritage Program
#   Edited: 
#   Edit: 
# ---------------------------------------------------------------------------
#
# Import system modules
import sys, string, os, arcgisscripting, win32com.client, arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
#arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
arcpy.env.snapRaster ="F:\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met"   #2017 update path
# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


ModelType = "Birds_Wetland_"
#in_put = arcpy.GetParameterAsText(0)
in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
#EXorHIST = arcpy.GetParameterAsText(1)
EXorHIST = "Extant"
#tyme = arcpy.GetParameterAsText(2)
tyme="12_01_2011"
Proj = arcpy.GetParameterAsText(3)
Proj = "HREP"


in_EOs = "in_EOs"
CCAP_select = "CCAP_select"
# LU Code 21 not included below because it includes estuarine.
CCAP_Select_Query = "\"VALUE\" = 13 OR \"VALUE\" = 14 OR \"VALUE\" = 15 OR \"VALUE\" = 22"

if Proj == "DOT":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_DOT"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_DOT"
    
elif Proj == "HRE Culverts":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HRE"
    StudyArea = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HRE"

elif Proj == "All":
    LULC = "F:/_Schmid/_GIS_Data/LULC/ccap_ne_2006"
    StudyArea = "M:/reg0/reg0data/base/borders/statemun/region.state"
    
elif Proj == "HREP":
    LULC = "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_HREP_CCAP06"
    
    #StudyArea = "C:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/StudyArea_HREP"
    StudyArea = "F:\\_Schmid\\_project\\Important_Areas\\GIS_Data\\IA_Process.gdb\\StudyArea_HREP"


DEC_wetlands = "DEC_wetlands"
NWI_select = "NWI_select"
in_buff_ring = "in_buff_ring"
#FinalFC = "W:/Projects/Important_Areas/GIS/GIS_Data/IA_results_CURRENT.gdb/" + ModelType + tyme + EXorHIST
FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"

if EXorHIST == "Extant":
    selectQuery = "IA_MODEL = '01EPES_WTB'"
    IAmodel = "01EPES_WTB"
#elif EXorHIST == "Historical":
#    selectQuery = "IA_MODEL = 'XXXXXXX'"
#    IAmodel = "XXXXXXX"

arcpy.AddMessage(ModelType + " model")

# Select out the proper EOs
arcpy.Select_analysis(in_put, "all_EOs", selectQuery)
arcpy.MakeFeatureLayer_management("all_EOs", "LAYER_all_EOs", "", "", "")
arcpy.SelectLayerByLocation_management("LAYER_all_EOs", "INTERSECT", StudyArea, "", "NEW_SELECTION")
arcpy.CopyFeatures_management("LAYER_all_EOs", in_EOs)

# First select the wetland type associated with the EO - palustrine or estuarine.
arcpy.MakeFeatureLayer_management(in_EOs, "LAYER_in_EOs")
in_features = "LAYER_in_EOs"

# Select out NWI wetlands
import IA_mod_lulc_select
IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)

# Select EOs that are in NWI estuarine wetland
arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"ATTRIBUTE\" LIKE 'E%'")
arcpy.SelectLayerByLocation_management("LAYER_in_EOs", "INTERSECT", "LAYER_NWI_polys", "", "NEW_SELECTION")
arcpy.CopyFeatures_management ("LAYER_in_EOs", "EstEOs")
arcpy.SelectLayerByLocation_management("LAYER_in_EOs", "", "", "", "SWITCH_SELECTION")
arcpy.CopyFeatures_management ("LAYER_in_EOs", "NoEstEOs")

# Run through the big loop, first with estuarine-based EOs and then with non-estuarine
loop = 1
while loop < 3:
    if loop == 1:
        LoopEO = "NoEstEOs"
    if loop == 2:
        LoopEO = "EstEOs"

    # Buffer the EOs 100 meters
    arcpy.Buffer_analysis(LoopEO, "LoopEO_buff", 100, "FULL", "ROUND", "ALL", "")

    
    in_features = "LoopEO_buff"
    
    # Select CCAP wetlands
    import IA_mod_lulc_select
    IA_mod_lulc_select.CCAP_select(in_features, CCAP_select, LULC, WSP, CCAP_Select_Query)
    arcpy.AddMessage("LU/LC SELECT: CCAP Wetlands have been selected.")
    
    arcpy.AddMessage("Going into DEC Wetlands...")
    # Select DEC wetlands
    import IA_mod_lulc_select
    IA_mod_lulc_select.DEC_wetlands(in_features, DEC_wetlands, WSP)
    arcpy.AddMessage("LU/LC SELECT: DEC Wetlands have been selected.")

    # Select out NWI wetlands
    import IA_mod_lulc_select
    IA_mod_lulc_select.NWI_polys(in_features, NWI_select, WSP)
    # Selecting out the lacustrine and palustrine NWI wetlands
    arcpy.MakeFeatureLayer_management(NWI_select, "LAYER_NWI_polys")
    arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "NEW_SELECTION", "\"ATTRIBUTE\" LIKE 'E%' OR \"ATTRIBUTE\" LIKE 'P%'")
    arcpy.SelectLayerByAttribute_management("LAYER_NWI_polys", "REMOVE_FROM_SELECTION", "\"ATTRIBUTE\" = 'E1UBL'")
    arcpy.CopyFeatures_management ("LAYER_NWI_polys", "NWI_wet_polys")

    #Union all estuarine wetlands and EOs
    arcpy.Union_analysis([LoopEO, CCAP_select, DEC_wetlands, "NWI_wet_polys"], "Unioned", "", "", "NO_GAPS")
    # Dissolve all wetlands from previous Union
    arcpy.Dissolve_management("Unioned", "Dissolved", "", "", "SINGLE_PART")

    if loop == 1:
        # Apply baseline buffer: 163m
        arcpy.AddMessage("Apply baseline buffer: 163m")
        arcpy.AddField_management("Dissolved", "ORIG_ID", "SHORT")
        arcpy.CalculateField_management("Dissolved", "ORIG_ID", "int(!OBJECTID!)", "PYTHON")
        arcpy.Buffer_analysis("Dissolved", in_buff_ring, 163, "FULL", "ROUND", "LIST", "ORIG_ID")

        # Run the Land Cover Type and Slope Module
        arcpy.AddMessage("Start the Assess Land Cover Type and Slope Module")
        value_field = "ORIG_ID"
        cell_size = 15
        in_buff = "Dissolved"
        out_buff = "out_buff"
        import IA_mod_assessLCSLP
        IA_mod_assessLCSLP.ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size)

        out_buff_Est = out_buff

    if loop == 2:
        # Apply estuarine module
        arcpy.AddMessage("Running estuarine module...")
        in_estvar = LoopEO
        out_estvar = "out_estvar"
        value_field = "ORIG_FID"
        import IA_mod_estuarine
        IA_mod_estuarine.EST_module(in_estvar, out_estvar, WSP, LULC)
        arcpy.AddMessage("Estuarine model, complete.")

    loop = loop + 1
##    loop = 3
    
out_buff = "out_buff"
out_estvar = "out_estvar"

arcpy.Merge_management([out_buff, out_estvar], "out_merge")

#   Extracting the CCAP Bare Land, erasing latest layer with it.
arcpy.AddMessage("Eliminate Bare Land (code = 20)....")
arcpy.MakeRasterLayer_management(LULC, "LAYER_BareLand", "\"VALUE\" = 20")
# Add next step so that snapraster applies to CCAP
arcpy.CopyRaster_management("LAYER_BareLand", "LAYER_BareLandpre")
arcpy.RasterToPolygon_conversion("LAYER_BareLandpre", "polys_BareLand", "NO_SIMPLIFY", "VALUE")
arcpy.Erase_analysis("out_merge", "polys_BareLand", "BareLand_erase", "")

# Add the IA_MODEL_R field
arcpy.AddMessage("wrap up....")
arcpy.AddField_management("BareLand_erase", "IA_MODEL_R", "TEXT", "", "20")
arcpy.CalculateField_management("BareLand_erase", "IA_MODEL_R", "'" + IAmodel + "'", "PYTHON")
arcpy.Dissolve_management("BareLand_erase", "Dissolve", "IA_MODEL_R", "", "SINGLE_PART")
arcpy.EliminatePolygonPart_management("Dissolve", "Elim", "AREA", 1000000)

################### WRAP UP
################### 
arcpy.CopyFeatures_management ("Elim", FinalFC)
#arcpy.CopyFeatures_management ("Elim", "C:/_Schmid/_project/Important_Areas/GIS_Data/OUTPUT.gdb/" + ModelType + tyme + EXorHIST)

arcpy.AddMessage("IA model done: Wetland Birds.")





