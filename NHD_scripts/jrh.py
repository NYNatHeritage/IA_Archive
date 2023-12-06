# IA_mod_nhdNAV.py
# Created on: Wed June 9, 2010
#   (created by John Schmid, GIS Specialist, NYNHP)
# 
# ---------------------------------------------------------------------------

# Import system modules
import sys, string, os, arcgisscripting, win32com.client
# Create the Geoprocessor object
gp = arcgisscripting.create()

# Navtype – Type of navigation. (STRING) Valid values are
#     UPMAIN – Upstream Mainstem
#     UPTRIB – Upstream with tributaries
#     DNMAIN – Downstream mainstem
#     DNDIV – Downstream with divergences
# Startcomid – Starting NHDFlowline comid for the navigation. (NUMERIC) Must be greater than 0.
# Startmeas – Starting measure for the navigation. (NUMERIC) Must be between 0 and 100, inclusive.
#     Additionally, a startmeas of –1 is valid. It indicates that the navigator should perform
#     “whole NHDFlowline” navigation and begin at the from measure of the NHDFlowline for upstream
#     navigations and the to measure of the NHDFlowline for downstream navigations.
# Maxdistance – Maximum travel distance in kilometers. (NUMERIC) A value of 0 indicates there is
#     no maximum travel distance and to navigate each path until the path ends. 0 is the default value.
# Datapath – Path to the NHDPlus workspace, openme.txt should be in this location (STRING)
# Apppath – Path to the directory containing VAANavigationCom.dll. (STRING)
# There are several external files packaged along with the VAANavigation COM object that are needed
#     to perform navigation. The com object must be able to find them.
#     TNavWorkskel.mdb, TFromToSkel.mdb, ComputeFromTo.dll)


NavT = "UPMAIN"
StartC = 66972510
StartM = 0
MaxD = 0
DataP = "D:\HSC\NHDPlusData\NHD02080103"
AppP = "D:\NHDPlusTools\VAACOMObjectNavigator"

##try:
##    def nhdNAV_module(NavT, StartC, StartM, MaxD, DataP, AppP):
##        
##        gp.AddMessage("MODULE:")
##        gp.AddMessage("NHD Navigator")
##        gp.AddMessage("")

print "start"
#Initialize object
nhd = win32com.client.Dispatch("VAANavigatorCOM.clsVAANavigate")

nhd.Navtype = NavT
nhd.Startcomid = StartC
nhd.Startmeas = StartM
nhd.Maxdistance = MaxD
nhd.Datapath = DataP
nhd.Apppath = AppP
print nhd.Navtype
gp.AddMessage(nhd.navtype)
print nhd.Startcomid
gp.AddMessage(nhd.startcomid)
print nhd.Maxdistance
gp.AddMessage(nhd.maxdistance)
print nhd.Datapath
gp.AddMessage(nhd.datapath)
print nhd.Apppath
gp.AddMessage(nhd.apppath)
#Do the navigation
numReturn = nhd.VAANavigate()
print numReturn
gp.AddMessage(numReturn)
#Terminate the object
nhd = None
del win32com.client
print "end"
gp.AddMessage("end" )

#except:
#    #gp.AddMessage("Error")
#    #gp.AddMessage(gp.GetMessages(2))




