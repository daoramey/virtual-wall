from OSC import *
import string
import math
import msvcrt
import sys
import datetime
import openvr
import numpy as np
import random



# Default orientation values	
rollOffset=0
pitchOffset=0
yawOffset=0
roll=0
pitch=0
yaw=0
FiltersetIdx=0

angleOffset=0



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
positionVectorSubSampled=xrange(0,360,minAngleDifference)

# Create OSC client 
multiClient = OSCMultiClient()
multiClient.setOSCTarget((ip,port))


# Init file to record tracking data
trackingDataFile = open('trackingdata.txt', 'a')
now = datetime.datetime.now()
trackingDataFile.write(str('++++ Next scene started +++++++++++  ') + str(now.isoformat()) + str('\n'))


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
		#print('!!!Currently only Yaw is sent to pyBinSim!!!')
		
		yaw = 180+yaw
		
	
		
		#Filterset = (int(round(posZ/0.25))+1)*25	# 25cm resolution
		

		#if Filterset > 8*25:
		#	Filterset = 8*25
		#elif Filterset < 25:
		#	Filterset = 25
		
		
		if msvcrt.kbhit():
			char = msvcrt.getch()

			# Key '1' actives 1st filter set
			if ord(char) == 49:
				FiltersetIdx = 0
			# Key '2' actives 2nd filter set
			if ord(char) == 50:
				FiltersetIdx = 1
			# Key '3' actives 1st filter set
			if ord(char) == 51:
				FiltersetIdx = 2
			# Key '4' actives 2nd filter set
			if ord(char) == 52:
				FiltersetIdx = 3
			# Key '5' actives 1st filter set
			if ord(char) == 53:
				FiltersetIdx = 4
			# Key '6' actives 2nd filter set
			if ord(char) == 54:
				FiltersetIdx = 5
			# Key '7' actives 1st filter set
			if ord(char) == 55:
				FiltersetIdx = 6
			# Key '8' actives 2nd filter set
			if ord(char) == 56:
				FiltersetIdx = 7
				
			# Key '9' randomizes angle offset
			if ord(char) == 57:
				r = random.randint(0,3)
				print('r= ', r)
				
				angle = r*90
				angleOffset = round(angle/4)*4
				print('angleOffset = ', angleOffset)
				trackingDataFile.write('angleOffSet= '+str(angleOffset)+str('\n'))
				
			# Key '0' marks chosen orientation
			if ord(char) == 48:
				trackingDataFile.write('Chosen Orientation\n')
				trackingDataFile.write(str(now.isoformat()) + str('  Yaw = ')+str(yaw) + str(' ') + str('Filterset ')+str(Filterset)+ str(' ') + str('PosZ ')+str(posZ)+ str('PosX ')+str(posX) + str('\n'))
				print('Chosen Orientation \n')
				
		#posZ=(posZ*10)+10
		#print "posZ gewandelt:",(posZ)


		#for n in range(0,nSources):
		message = OSCMessage(oscIdentifier)
		#channel valueOne valueTwo ValueThree
		yaw=min(positionVectorSubSampled, key=lambda x: abs(x - yaw))
		yawSend = yaw+int(angleOffset)
		if yawSend >359:
			yawSend= yawSend - 360
		Filterset = FiltersetIdx * 25 + 30
		binSimParamters=[0,yawSend,Filterset,0]
		print(' Yaw: ', yaw, ' Filterset: ', Filterset, ' PosY ', posZ, 'offs', angleOffset)#print([' Yaw: ', yaw])
		trackingDataFile.write(str(now.isoformat()) + str('  Yaw = ')+str(yaw) + str(' ') + str('Filterset ')+str(Filterset)+ str(' ') + str('PosZ ')+str(posZ)+ str('PosX ')+str(posX)+ str('  AngleOffSet ')+str(angleOffset) + str('\n'))
		message.append(binSimParamters)
		multiClient.send(message)
        
        
		sys.stdout.flush()
            
		time.sleep(0.02)        


except KeyboardInterrupt:	# Break if ctrl+c is pressed
		
		# Close Textfile for TrackingData
		trackingDataFile.write(str('++++ Scene Stopped +++++++++++  ') + str(now.isoformat()) + str('\n'))
		trackingDataFile.close()
		
        # Last Message sets angles to zero
		message = OSCMessage(oscIdentifier)
		message.append([0, 0, 0])
		multiClient.send(message)

		# Console output
		print "Done"




"""


	# define current angles as "zero position"	when spacebar is hit
        if msvcrt.kbhit():
            if ord(msvcrt.getch()) == 32:
                rollOffset = roll
                pitchOffset = pitch
                yawOffset = yaw

	# calculate difference between current angles and "zero position"
        roll = roll - rollOffset
        pitch = pitch - pitchOffset
        yaw = yaw - yawOffset

        if(roll < -180):
                roll = 360+roll
                		
        if(pitch < -90):
                pitch = 360+pitch
		
        if(yaw < -180):
                yaw = 360+yaw

        if(roll > 180):
                roll = -1*(360-roll)

        if(pitch > 90):
                pitch = -1*(360-pitch)
	
        if(yaw > 180):
                yaw = -1*(360-yaw)		
		
 """    
        
