# This file is part of the pyBinSim project.
#
# Copyright (c) 2017 A. Neidhardt, F. Klein, N. Knoop, T. Köllmer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pythonosc import osc_message_builder
from pythonosc import udp_client
import string
import math
import sys
import time
import openvr
import argparse
import numpy as np


def start_tracker():
	
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
			## to get yaw from 0 to 360 degree, axis 0 and 1 have been switched
			
			yawRad=np.arctan2(v[0][2],v[2][2])
			yaw =int(round(np.degrees(yawRad)))           
			
			pitchRad=np.arctan2(-v[1][2],np.sqrt(np.square(v[0][2])+np.square(v[2][2])))
			pitch=int(round(np.degrees(pitchRad)))
			
			rollRad=np.arctan2(v[1][0],v[1][1])
			roll  =int(round(np.degrees(rollRad)))
			
			posX=v[0][3]
			posY=v[1][3]
			posZ=v[2][3]
	
			
			#print(['YAW: ',yaw,' PITCH: ',pitch,'ROLL: ',roll])
			#print(['X: ',round(posX,2),' Y: ',round(posY,2),'Z: ',round(posZ,2)])
	
	
			# adjustment to desired global origin
			posZ= posZ  + 0.8
			if yaw < 0:
				yaw = 360+yaw
				
			yaw = 360 -yaw
			
			
			# select filterset according to Z-value of listener
			Filterset = int(round(posZ/0.25))		# 25cm resolution
			
			if Filterset > 8:
				Filterset = 8
			elif Filterset < 0:
				Filterset = 0
			
			
			# Build and send OSC message
			#channel valueOne valueTwo ValueThree valueFour valueFive ValueSix
			yaw=min(positionVectorSubSampled, key=lambda x: abs(x - yaw))
			binSimParameters=[0,yaw,Filterset,0,0,0,0]
			print(' Yaw: ', yaw, ' Filterset: ', Filterset, ' PosY ', posZ)
			client.send_message(oscIdentifier, binSimParameters) 
			
			
			sys.stdout.flush()
		
			time.sleep(0.02)        
	
	
	except KeyboardInterrupt:	# Break if ctrl+c is pressed
		
			# Console output
			print("Done")
	

if __name__ == "__main__":
	start_tracker()
	
