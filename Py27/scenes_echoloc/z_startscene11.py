import sys
import time
import datetime
import math
import os

	
SettingsFile = open('../pyBinSimSettings.txt','w')
SettingsFile.write(	'soundfile signals\SherlockHolmesCUT_mono.wav\nblockSize 256\nfilterSize 16384\nfilterList brirs\MeasOBRIR_44100_anechoic1wall_4deg\Filterlist_Meas_OBRIRs44100_anechoic1Wall_row.txt\nenableCrossfading True\nuseHeadphoneFilter False 999 999 999\nloudnessFactor 1')
SettingsFile.close()

startBinSimcommand=('start cmd.exe /c python %homepath%/Desktop/pyBinSim_version061216/pyBinSim2.py')
os.system(startBinSimcommand)
time.sleep(1)
startBinSimcommand=('start cmd.exe /c python %homepath%/Desktop/pyBinSim_version061216/TranslationWithVive2pyBinSim_25cm_1Wall.py')
os.system(startBinSimcommand)



