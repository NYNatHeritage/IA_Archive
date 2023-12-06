# -*- coding: utf-8 -*-
import os, arcpy
arcpy.env.workspace='D:\\Git_Repos\\IA_geoprocessing_scripts\\geo_scripts\\toolbox_scripts'

#os.chdir('D:\\Git_Repos\\IA_geoprocessing_scripts\\geo_scripts\\toolbox_scripts')

tyme="_3_5_"
('2017_IA_EasternBoxTurtle.py')

execfile('D:/Git_Repos/IA_geoprocessing_scripts/geo_scripts/toolbox_scripts/2017_IA_EasternBoxTurtle.py')


##Get list of the python scripts
##run chosen scripts

import arcpy

arcpy.env.workspace='D:\\Git_Repos\\IA_geoprocessing_scripts\\geo_scripts\\toolbox_scripts'
script_list=[]
for f in arcpy.ListFiles("2017_*"): script_list.append(f)

full_list=script_list
script_list[16:18]


in_put="W:\Projects\HREP\Impt_Areas_updates_2018\GIS\diadromous_fishes_Culverts.shp"# (this is a point shapefile)
arcpy.Buffer_analysis(in_put, "W:\Projects\HREP\Impt_Areas_updates_2018\GIS\diadromous_fishes_Culverts_buf.shp", 100, "FULL", "ROUND", "ALL")


#in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts_sample"
script_loc='D:\\Git_Repos\\IA_geoprocessing_scripts\\geo_scripts\\toolbox_scripts'
#in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts"
EXorHIST="Extant"
LULC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\LULC_HRE_10"
StudyArea="D:\\Git_Repos\\IA_geoprocessing_scripts\\HREP_Project_Area_merge.shp"


FinalFC= "D:\\Git_Repos\\IA_geoprocessing_scripts\\" + ModelType + tyme + EXorHIST + ".shp"
FinalFC_gdb="D:\\Git_Repos\\IA_geoprocessing_scripts\\OUTPUT.gdb\\" + ModelType + tyme + EXorHIST
################ Run on loop
completed_scripts=[]

for i in range (41,42):
    tyme="_9_7_"
#    in_put= "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\EOs_test_for_scripts"
    #in_put="W:\\Projects\\HREP\\Impt_Areas_updates_2018\\GIS\EOs_IA_model_input.shp"
    in_put= "W:\Projects\HREP\Impt_Areas_updates_2018\GIS\diadromous_fishes_Culverts_polygons.shp"# (this is a point shapefile)
#    in_put="W:\\Projects\\HREP\\Impt_Areas_updates_2018\\GIS\HREP_IA_WatchList_Herps.shp"
    EXorHIST="Extant"
    LULC = "D:\\Git_Repos\\IA_geoprocessing_scripts\\EOs_test_for_scripts.gdb\\LULC_HRE_10"
    StudyArea="D:\\Git_Repos\\IA_geoprocessing_scripts\\HREP_Project_Area_merge.shp"
    Roadblocks = "H:\\Please_Do_Not_Delete_me\\_Schmid\\Important_Areas\\GIS_Data\\IA_Process.gdb/ALIS_ACC1and2_HREP_poly"
    print script_list[i]
    script=script_loc+"\\"+str(script_list[i])
    execfile(script)
    completed_scripts.append(script_list[i])