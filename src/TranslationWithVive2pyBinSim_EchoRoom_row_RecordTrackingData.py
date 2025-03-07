from pythonosc import osc_message_builder
from pythonosc import udp_client
import string
import math
import msvcrt
import time
import sys
import openvr
import numpy as np
import os
import datetime
import argparse



# Default orientation values	
rollOffset=0
pitchOffset=0
yawOffset=0
roll=0
pitch=0
yaw=0
Filterset=0



oscIdentifier = '/pyBinSim'
ip = '127.0.0.1'
port = 10000
nSources = 0
minAngleDifference=4  

run=True


if (len(sys.argv))>1:
	for i in range(len(sys.argv)):

		if( sys.argv[i] == '-port' ):
			port = int(sys.argv[i+1])
			
		if( sys.argv[i] == '-ip' ):
			ip = sys.argv[i+1]
			
		if( sys.argv[i] == '-nSources' ):
			nSources = int(sys.argv[i+1])
			
		if( sys.argv[i] == '-angleStep' ):
			minAngleDifference = int(sys.argv[i+1])


# Internal settings:
positionVector=np.arange(360)
positionVectorSubSampled=range(0,360,minAngleDifference)

# Create OSC client 
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default=ip,help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=port,help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

# Init file to record tracking data
script_dir = os.path.dirname(__file__)
trackingDataFileName='trackingdata.txt'
trackingDataFile = open(os.path.join(script_dir, trackingDataFileName), 'a')
now = datetime.datetime.now()
trackingDataFile.write(str('++++ Tracking EchoRoom_row started +++++++++++  ') + str(now.isoformat()) + str('\n'))


# init openvr for HTC Vive
help(openvr.VRSystem)

openvr.init(openvr.VRApplication_Scene)

poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
poses = poses_t()



try:
	while 1:
		openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)
		hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
		v = hmd_pose.mDeviceToAbsoluteTracking
		
		
		## extraction of angles from rotation matrix
		## to get yaw from -180 to + 180 degree, axis 0 and 1 have been switched
		
		yawRad=np.arctan2(v[0][2],v[2][2])
		#angleX=np.arctan2(v[1][2],v[2][2])
		yaw =int(round(np.degrees(yawRad)))           
		
		pitchRad=np.arctan2(-v[1][2],np.sqrt(np.square(v[0][2])+np.square(v[2][2])))
		#yawRad=np.arctan2(-v[0][2],np.sqrt(np.square(v[1][2])+np.square(v[2][2])))
		pitch=int(round(np.degrees(pitchRad)))
		
		rollRad=np.arctan2(v[1][0],v[1][1])
		#angleZ=np.arctan2(v[0][1],v[0][0])
		roll  =int(round(np.degrees(rollRad)))
		
		posX=v[0][3]
		posY=v[1][3]
		posZ=v[2][3]

		
		#print(['YAW: ',yaw,' PITCH: ',pitch,'ROLL: ',roll])
		#print(['X: ',round(posX,2),' Y: ',round(posY,2),'Z: ',round(posZ,2)])

		
		
		yaw = 360+yaw
		if yaw >359:
			yaw=yaw-360
			
		yaw = 360 - yaw
		
		posZ = 1 - posZ
		
		
		Filterset = (int(round(posZ/0.25)))*25+30	# 25cm resolution
		

		if Filterset > 8*25+30:
			Filterset = 8*25+30
		elif Filterset < 30:
			Filterset = 30
		
		
		if msvcrt.kbhit():
			char = msvcrt.getch()
				
			# Key '0' marks chosen orientation
			if ord(char) == 48:
				trackingDataFile.write('Chosen Orientation\n')
				now = datetime.datetime.now()
				trackingDataFile.write(str(now.isoformat()) + str('  Yaw = ')+str(yaw) + str(' ') + str('Filterset ')+str(Filterset)+ str(' ') + str('PosZ ')+str(posZ)+ str(' PosX ')+str(posX) + str('\n'))
				print('Chosen Orientation \n')
		
		#channel valueOne valueTwo ValueThree
		yaw=min(positionVectorSubSampled, key=lambda x: abs(x - yaw))
		binSimParameters=[0,yaw,Filterset,0,0,0,0]
		print(' Yaw: ', yaw, ' Filterset: ', Filterset, ' PosY ', posZ)#print([' Yaw: ', yaw])
		now = datetime.datetime.now()
		trackingDataFile.write(str(now.isoformat()) + str('  Yaw = ')+str(yaw) + str(' ') + str('Filterset ')+str(Filterset)+ str(' ') + str('PosZ ')+str(posZ) + str('\n'))
		client.send_message(oscIdentifier, binSimParameters) 


		sys.stdout.flush()
    
		time.sleep(0.005)        


except KeyboardInterrupt:	# Break if ctrl+c is pressed
		
		# Close Textfile for TrackingData
		now = datetime.datetime.now()
		trackingDataFile.write(str('++++ Scene Stopped +++++++++++  ') + str(now.isoformat()) + str('\n'))
		trackingDataFile.close()
		
	
		# Console output
		print("Done")



