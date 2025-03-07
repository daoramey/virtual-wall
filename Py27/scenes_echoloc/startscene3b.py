import sys
import time
import datetime
import math
import os

	
SettingsFile = open('../pyBinSimSettings.txt','w')
SettingsFile.write(	'soundfile signals\SherlockHolmesCUT_mono.wav\nblockSize 512\nfilterSize 65536\nfilterList brirs\MeasOBRIR_44100_Room1_alongtheWall_4deg\Filterlist_Meas_OBRIRs44100_Room1wall_row.txt\nenableCrossfading True\nuseHeadphoneFilter False 999 999 999\nloudnessFactor 1')
SettingsFile.close()

# Init file to record tracking data
trackingDataFile = open('trackingdata.txt', 'a')
now = datetime.datetime.now()
trackingDataFile.write(str('++++ scene3_echoloc_Room1wall_separat +++++++++++  ') + str(now.isoformat()) + str('\n'))
trackingDataFile.close()

startBinSimcommand=('start cmd.exe /c python %homepath%/Desktop/pyBinSim_version061216/pyBinSim.py')
os.system(startBinSimcommand)
time.sleep(1)
startBinSimcommand=('start cmd.exe /c python %homepath%/Desktop/pyBinSim_version061216/TranslationWithVive2pyBinSim_25cm_Room1and2_sep.py')
os.system(startBinSimcommand)



