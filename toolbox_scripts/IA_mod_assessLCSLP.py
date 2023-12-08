# ---------------------------------------------------------------------------
# IA_mod_assessLCSLP.py
# Created on: Wed May 26, 2010
#   (created by John Schmid, GIS Specialist, NYNHP)
# Usage: This script is a commonly used module that assesses land cover and slope in a buffer 
# REVISED: Just Riverine right now (no forest 50% thing, like palustrine)
#           Works as of October 5, 2011
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os,  arcpy

# Check out any necessary licenses
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
import arcpy.cartography as CA
arcpy.env.snapRaster = "W:/GIS_Data/SnapRasters/snapras30met"
#arcpy.env.snapRaster ="F:\\_Schmid\\_GIS_Data\\SnapRasters\\snapras30met" 

# Workspace
#arcpy.env.workspace  = "C:/_Schmid/_project/Important_Areas/GIS_Data/SCRATCH.gdb"
#arcpy.env.workspace = "D:\\Git_Repos\\scratch.gdb"  #2017 update path
arcpy.env.workspace ="H:/Please_Do_Not_Delete_me/Important_Areas/scratch2023.gdb"
WSP = arcpy.env.workspace
arcpy.env.overwriteOutput = True


def ALCSLP_RIVmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size):
    
    arcpy.AddMessage("MODULE:")
    arcpy.AddMessage("Assessing Land Cover Type and Slope")
    arcpy.AddMessage("")

    #   Erase the original input shape from the new buffer, to create a "ring".
    #   Then blast it into single parts, so that the frequency will work on separate
    #   wetlands
    arcpy.AddMessage("Create a buffer 'ring'...")
    arcpy.Erase_analysis(in_buff_ring, in_buff, "ringvar1", "")
    #arcpy.RepairGeometry_management ("ringvar1")
    #DON"T THINK THIS STEP NECESSARY?????arcpy.MultipartToSinglepart_management("ringvar1", "ringvar2")
    arcpy.CopyFeatures_management("ringvar1", "ringvar2")

    #   Convert the buffer ring to a raster, make it an integer raster (easier to run
    #   thru the CON statement), and run the Con to create a binary buffer.
    arcpy.AddMessage("Create a binary raster buffer 'ring'...")
    arcpy.FeatureToRaster_conversion("ringvar2", value_field, "ringvar2_rast", cell_size)
    rvar2_buff = "D:\\Git_Repos\\scratch.gdb\\rvar2_buff"
    arcpy.gp.Int_sa("ringvar2_rast", "ringvar2_int")
    rvar2_buff = "D:\\Git_Repos\\scratch.gdb\\rvar2_buff"
    arcpy.gp.Con_sa("ringvar2_int", "1", "rvar2_buff", "0", "\"Value\" > 0")
    
    ################### Assess LULC
    ###################
    
    #   Give the raster buffer LU values, and then export to vector
    arcpy.AddMessage("Give buffer 'ring' LU values, export to vector...")
    #arcpy.gp.Times_sa("rvar2_buff", "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/LULC_NE_CCAP06_15", "ccap_buff")

    arcpy.gp.Times_sa("rvar2_buff", "H:\Please_Do_Not_Delete_me\_Schmid\Important_Areas\GIS_Data/IA_Process.gdb/LULC_NE_CCAP06_15", "ccap_buff")
    #   Reclassify LU values: Forested equals 2 (tomultiply the 2.0 coefficient in the methodology,
    #   Non-forested (terrestrial) buffer equals 1, and all else equals NoData
    #   All others = NODATA
    arcpy.AddMessage("Reclassify LU values: Forested equals 2, Non-forested (terrestrial) buffer equals 1, and all else equals NoData")
    arcpy.gp.Reclassify_sa("ccap_buff", "VALUE", "2 1;3 1;4 1;5 1;6 1;7 1;8 1;9 2;10 2;11 2;12 1;20 1", "ccap_recl", "NODATA")

    ################### Assess Slope
    ###################
    
    arcpy.AddMessage("Now assessing slope...")
    arcpy.FeatureToRaster_conversion(in_buff,  value_field, "in_buff_rast", cell_size)
    #arcpy.gp.Watershed_sa("F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/state_fldir_15", "in_buff_rast", "buff_shed", "Value")
    arcpy.gp.Watershed_sa("H:\Please_Do_Not_Delete_me\_Schmid\Important_Areas\GIS_Data/IA_Process.gdb/state_fldir_15", "in_buff_rast", "buff_shed", "Value")
    # Calculate the slope of this watershed area, w/ conditional statement
    arcpy.AddMessage("Calculate the slope of this watershed...")
    
#    buff_shed_int = Int("buff_shed")
    arcpy.gp.Int_sa("buff_shed", "buff_shed_int")
#    buff_shed_int.save("buff_shed_int")
#    buff_shed_binary = Con("buff_shed_int", "1", "0", "VALUE > 0")
#    buff_shed_binary.save("buff_shed_binary")   
    arcpy.gp.Con_sa("buff_shed_int", "1", "buff_shed_binary", "0", "\"Value\" > 0")
#    slope_buff = Times("buff_shed_binary", "C:\_Schmid\_GIS_Data/slope/st30slp_pr")
#    slope_buff.save("slope_buff")
    #arcpy.gp.Times_sa("buff_shed_binary", "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/st30slp_pr_15", "slope_buff")
    #arcpy.gp.Times_sa("buff_shed_binary", "F:/_Schmid/_project/Important_Areas/GIS_Data/IA_Process.gdb/st30slp_pr_15", "slope_buff")
    arcpy.gp.Times_sa("buff_shed_binary", "H:/Please_Do_Not_Delete_me/_Schmid/Important_Areas/GIS_Data/IA_Process.gdb/st30slp_pr_15", "slope_buff")
    # Assess the cover type and slope
    arcpy.AddMessage("Assess Cover Type with Slope")
    #arcpy.gp.Con_sa("ccap_recl", "F:/_Schmid/_project/Important_Areas/GIS_Data/soils/ssurgo2_FinalKFact.gdb/NYS_s2_EroHzd_2012_June_15", "LC_raster", "ccap_recl", "\"Value\" > 0")
    
    arcpy.gp.Con_sa("ccap_recl", "H:/Please_Do_Not_Delete_me/_Schmid/_GIS_Data/soils/ssurgo2_FinalKFact.gdb/NYS_s2_EroHzd_2012_June_15", "LC_raster", "ccap_recl", "\"Value\" > 0")
#    LC_raster = Con("ccap_recl", "C:/_Schmid/_project/Important_Areas/GIS_Data/soils/ssurgo2_FinalKFact.gdb/NYS_s2_EroHzd_2012_June", "ccap_recl", "VALUE = 1")
#    LC_raster.save("LC_raster")

#    cover_slope = Times("LC_raster", "slope_buff")
#    cover_slope.save("cover_slope")
    arcpy.gp.Times_sa("LC_raster", "slope_buff", "cover_slope")

    # Convert the watershed to polys (must be a raster first)
    arcpy.AddMessage("Convert the watershed to polys...")

#    cover_slope_int = Int("cover_slope")
#    cover_slope_int.save("cover_slope_int")
    arcpy.gp.Int_sa("cover_slope", "cover_slope_int")
    arcpy.RasterToPolygon_conversion("cover_slope_int", "cover_slope_polys", "NO_SIMPLIFY", "VALUE")



    # Buffer
    arcpy.AddMessage("Buffering the cover/slope combo...")
    #####################################
    ##################################### Next step botches - next step, NEW 3/13/2013
    #####################################
    arcpy.Clip_analysis("cover_slope_polys", in_buff, "cover_slope_polys2")
    arcpy.Buffer_analysis("cover_slope_polys2", "Final_Buff", "gridcode", "FULL", "ROUND", "ALL", "")
    # Union the three parts: the input EOs, the baseline buffer, and the final extra buffer.
    arcpy.AddMessage("Union the three parts: the input EOs, the baseline buffer, and the final extra buffer...")
    arcpy.MultipartToSinglepart_management("Final_Buff","Final_Buffsp")# This step necessary or I get the Topoengine error.
    arcpy.AddMessage("multipart to singlepart complete...")
    #USED MERGE BELOW AND WASN"T GETTING BULLSHIT 9999 ESRI ERRORS LIKE W/UNION...WTF...arcpy.Union_analysis(["Final_Buffsp", in_buff_ring], "Final_Union")
    arcpy.AddMessage("WTF????")
    arcpy.Union_analysis(["Final_Buffsp", in_buff_ring], "Final_Union")
#    arcpy.Union_analysis("Final_Buffsp #; " + in_buff_ring + " #", "Final_Union")
#    arcpy.Merge_management(["Final_Buffsp", in_buff_ring], "Final_Union")
    arcpy.AddMessage("Final union complete...")
    # Dissolve
    arcpy.Dissolve_management("Final_Union", out_buff, "", "", "SINGLE_PART")
    
                  
    arcpy.AddMessage("ALCSLP module: FINISHED")


def ALCSLP_PALmodule(in_buff, in_buff_ring, out_buff, WSP, value_field, cell_size):


    arcpy.AddMessage("MODULE:")
    arcpy.AddMessage("Assessing Land Cover Type and Slope")
    arcpy.AddMessage("")

    #   Erase the original input shape from the new buffer, to create a "ring".
    #   Then blast it into single parts, so that the frequency will work on separate
    #   wetlands
    arcpy.AddMessage("Create a buffer 'ring'...")
    arcpy.Erase_analysis(in_buff_ring, in_buff, "ringvar1", "")
    #arcpy.RepairGeometry_management ("ringvar1")
    #DON"T THINK THIS STEP NECESSARY?????arcpy.MultipartToSinglepart_management("ringvar1", "ringvar2")
    arcpy.CopyFeatures_management("ringvar1", "ringvar2")

    #   Convert the buffer ring to a raster, make it an integer raster (easier to run
    #   thru the CON statement), and run the Con to create a binary buffer.
    arcpy.AddMessage("Create a binary raster buffer 'ring'...")
    arcpy.FeatureToRaster_conversion("ringvar2", value_field, "ringvar2_rast", cell_size)
    arcpy.gp.Int_sa("ringvar2_rast", "rvar2_int")
    #rvar2_buff = Con("rvar2_int", "1", "0", "VALUE > 0")
    rvar2_buff = Con(Raster("rvar2_int") > 0, 1, 0)
    rvar2_buff.save("rvar2_buff")   

    
    ################### Assess LULC
    ###################
    
    #   Give the raster buffer LU values, and then export to vector
    arcpy.AddMessage("Give buffer 'ring' LU values, export to vector...")

    arcpy.env.cellSize = cell_size
    ccap_buff = Times("rvar2_buff", "H:/Please_Do_Not_Delete_me/Important_Areas/HRE_2016_ccap_corrected.tif") ##2023 changed from ne_2006
    ccap_buff.save("ccap_buff")
    
    #   Reclassify LU values: Forested equals 2 (tomultiply the 2.0 coefficient in the methodology,
    #   Non-forested (terrestrial) buffer equals 1, and all else equals NoData
    #   All others = NODATA
    arcpy.AddMessage("Reclassify LU values: Forested equals 2, Non-forested (terrestrial) buffer equals 1, and all else equals NoData")

    ccap_recl = Reclassify("ccap_buff", "VALUE", "2 8 1; 9 11 2; 12 12 1; 20 20 1", "NODATA")
    ccap_recl.save ("ccap_recl")
    ###
    ### FOREST PART (River version does not use this) - START
    ###
    arcpy.RasterToPolygon_conversion("ccap_recl", "ccap_buff_polys", "NO_SIMPLIFY", "VALUE")
    arcpy.Intersect_analysis("ccap_buff_polys ; ringvar2", "ccap_buff_FID")
        
    #   Create frequency tables of the area calculations, based on GRIDCODE and the buffer ID.
    arcpy.AddMessage("Create frequency tables...")

    arcpy.Frequency_analysis("ccap_buff_FID", "freq_Ring_Total_Table", "FID_ringvar2", "Shape_Area") #total buff area
    arcpy.Frequency_analysis("ccap_buff_FID", "freq_LU_Table", "FID_ringvar2 ; gridcode", "Shape_Area") #Grid code area per buff ID
    arcpy.MakeTableView_management("freq_LU_Table", "freq_LU_View")
    arcpy.AddJoin_management("freq_LU_View", "FID_ringvar2", "freq_Ring_Total_Table", "FID_ringvar2")
    arcpy.CopyRows_management("freq_LU_View", "LU_Table") # Combo of two prev. frequency tables
        
    #   Separate out what is forested, and what is not forested (yet still terrestrial)
    arcpy.AddMessage("Separate out what is forested/non-forested terrestrial...")

    Forest_Query = "freq_LU_Table_gridcode = 2"
    arcpy.MakeTableView_management("LU_Table", "LU_View", Forest_Query)
    arcpy.CopyRows_management("LU_View", "ForestLU_Table") #This table is just forested lu in buff
    arcpy.AddField_management("ForestLU_Table", "Perc_Forest_LU", "DOUBLE")
        
    #   Determine what percentage of the buffer contains forested LU
    arcpy.AddMessage("Determine what percentage of the buffer contains forested LU...")
    arcpy.CalculateField_management("ForestLU_Table", "Perc_Forest_LU", "(!freq_LU_Table_Shape_Area! / !freq_Ring_Total_Table_Shape_Area!) * 100", "PYTHON")
        
    #   Determine which buffer areas get an extra 50m, and populate the field
    arcpy.AddMessage("Determine which buffer areas get an extra 50m, and populate the field...")
        
    arcpy.AddField_management("ccap_buff_FID", "LT50_Forest", "LONG")
    arcpy.MakeFeatureLayer_management("ccap_buff_FID", "LAYER_ccap_buff_FID2")
    arcpy.AddJoin_management("LAYER_ccap_buff_FID2", "FID_ringvar2", "ForestLU_Table", "freq_Ring_Total_Table_FID_ringvar2")
    arcpy.CopyFeatures_management("LAYER_ccap_buff_FID2", "ForBuf")
    # I tried doing the following steps before the previous CopyFeatures but
    # the mystical syntax rules prohibit logic.....arghhh
    arcpy.MakeFeatureLayer_management("ForBuf", "LAYER_ForBuf")
    arcpy.SelectLayerByAttribute_management("LAYER_ForBuf", "NEW_SELECTION", "\"ForestLU_Table_Perc_Forest_LU\" < 50")
    arcpy.SelectLayerByAttribute_management("LAYER_ForBuf", "SUBSET_SELECTION", "\"ccap_buff_FID_gridcode\" = 2")
    arcpy.CopyFeatures_management("LAYER_ForBuf", "Forest_Buffer")
    arcpy.CalculateField_management("Forest_Buffer", "ccap_buff_FID_LT50_Forest", 50, "PYTHON")

    arcpy.AddMessage("ALCSLP module: Assess Land Cover Type is done.")
    ###
    ### FOREST PART (River version does not use this) - END
    ###

    ################### Assess Slope
    ###################
    
    arcpy.AddMessage("Now assessing slope...")

    arcpy.env.cellSize = cell_size
    arcpy.FeatureToRaster_conversion(in_buff,  value_field, "in_buff_rast", cell_size)
    #buff_shed = Watershed("F:/_Schmid/_GIS_Data/flow_dir/state_fldir", "in_buff_rast")
    buff_shed = Watershed("H:/Please_Do_Not_Delete_me/_Schmid/_GIS_Data/flow_dir/state_fldir", "in_buff_rast") #Update path to Schmidt archive for 2023
    buff_shed.save("buff_shed")

    # Calculate the slope of this watershed area, w/ conditional statement
    arcpy.AddMessage("Calculate the slope of this watershed...")
    
    buff_shed_int = Int("buff_shed")
    buff_shed_int.save("buff_shed_int")
    buff_shed_binary = Con("buff_shed_int", "1", "0", "VALUE > 0")
    buff_shed_binary.save("buff_shed_binary")   
    #slope_buff = Times("buff_shed_binary", "F:\_Schmid\_GIS_Data/slope/st30slp_pr")
    slope_buff = Times("buff_shed_binary", "H:/Please_Do_Not_Delete_me/_Schmid/_GIS_Data/slope/st30slp_pr")
    
    slope_buff.save("slope_buff")


###########
########### Need to update the erosion hazard soil feature class for HREP Culverts
    
    # Assess the cover type and slope
    arcpy.AddMessage("Assess Cover Type with Slope")
    
    #LC_raster = Con("ccap_recl", "F:/_Schmid/_project/Important_Areas/GIS_Data/soils/ssurgo2_FinalKFact.gdb/NYS_s2_EroHzd_2012_June", "ccap_recl", "VALUE = 1")
    LC_raster = Con("ccap_recl", "H:/Please_Do_Not_Delete_me/_Schmid/Important_Areas/GIS_Data/soils/ssurgo2_FinalKFact.gdb/NYS_s2_EroHzd_2012_June", "ccap_recl", "VALUE = 1") #Update path to Schmidt archive for 2023
    LC_raster.save("LC_raster")

    cover_slope = Times("LC_raster", "slope_buff")
    cover_slope.save("cover_slope")

    # Convert the watershed to polys (must be a raster first)
    arcpy.AddMessage("Convert the watershed to polys...")

    cover_slope_int = Int("cover_slope")
    cover_slope_int.save("cover_slope_int")
    arcpy.RasterToPolygon_conversion("cover_slope_int", "cover_slope_polys", "NO_SIMPLIFY", "VALUE")

    # Run through the forest buffer
    arcpy.AddMessage("Run through the forest buffer...")
    arcpy.RepairGeometry_management ("Forest_Buffer")
    arcpy.Identity_analysis("Forest_Buffer", "cover_slope_polys", "buff_shed_all")

    # Add together the extra buffer components, and then run the buffer
    arcpy.AddMessage("Add together the extra buffer components, and then run the buffer...")

    arcpy.AddField_management("buff_shed_all", "total_extra_buff", "LONG")
    arcpy.CalculateField_management("buff_shed_all", "total_extra_buff", "!ccap_buff_FID_LT50_Forest! + !gridcode!", "PYTHON")
    # Dissolve based on unique buffer distances, and then buffer
    arcpy.AddMessage("Dissolve based on unique buffer distances, and then buffer...")

    arcpy.Dissolve_management("buff_shed_all", "Buff_shed_diss", "total_extra_buff", "", "SINGLE_PART")
    arcpy.Buffer_analysis("Buff_shed_diss", "Final_Buff", "total_extra_buff", "FULL", "ROUND", "ALL", "")
        
    # Union the three parts: the input EOs, the baseline buffer, and the final extra buffer.
    arcpy.AddMessage("Union the parts: the input EOs with the baseline buffer and the final extra buffer...")
    arcpy.MultipartToSinglepart_management("Final_Buff","Final_Buffsp")# This step necessary or I get the Topoengine error.
    arcpy.AddMessage("multipart to singlepart complete...")
    #USED MERGE BELOW AND WASN"T GETTING BULLSHIT 9999 ESRI ERRORS LIKE W/UNION...WTF...arcpy.Union_analysis(["Final_Buffsp", in_buff_ring], "Final_Union")
    arcpy.Merge_management(["Final_Buffsp", in_buff_ring], "Final_Union")
    # Dissolve
    arcpy.Dissolve_management("Final_Union", "pre_out_buff")
    arcpy.MultipartToSinglepart_management("pre_out_buff", out_buff)
    
    arcpy.AddMessage("ALCSLP PAL module: FINISHED")

